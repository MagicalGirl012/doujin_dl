#doujin_dl.py

#1/2/2020

#Author: MagicalGirl012
#        https://github.com/MagicalGirl012

#Description:
#   downloads doujins from nhentai.net
#   can download a single doujin
#   or multiple doujins from a search query / csv

    
#Packages
import sys
import os
import shutil
import requests
from bs4 import BeautifulSoup
import csv

print("All packages initialized")
print()

#Get the directory which the file runs from
file_directory, filename = os.path.split(os.path.abspath(__file__))

#Get the folder where files are downloaded to
download_folder = os.path.join(file_directory, "downloads")

#Change working directory
os.chdir(file_directory)

#download_image_from_url():
#   file_name - String representing what to call the downloaded file
#   web_url - String representing URL to image to download
#   download_dir - directory to download the image to
#Method name is self-explanatory
def download_image_from_url(file_name, web_url, download_dir):

    response = requests.get(web_url, stream=True)
    with open( os.path.join(download_dir, file_name), 'wb' ) as out_file:
        shutil.copyfileobj(response.raw, out_file)

    #cleanup
    del response

#download_single_doujin():
#   six_digit_number - int representing where one can find the art of their liking
#Purpose of method is to download a single doujin from a six_digit_number
#Calls the download_image_from_url method to accomplish this task
def download_single_doujin(number, download_folder = download_folder):

    #Check to see if number is in the download list
    with open("download_archive.txt", "r") as download_archive:
        if( str(number) in download_archive.read() ):
            print("{0} is already in the download archive, canceling".format(number))

            return
        else:
            print("{0} is not in download archive, proceeding with download".format(number))

    url_base = "https://nhentai.net/g/"
    url = url_base + str(number)

    print("Proceeding to download: {0}".format(number))
    print()

    response = requests.get(url)

    html_soup = BeautifulSoup(response.text, "html.parser")

    try:

        #Find thumbnail container
        thumbnail_container = html_soup.find("div", id="thumbnail-container")

        #Find divs within thumbnail container
        #tags = thumbnail_container.find_all("div", {"class", "thumb-container"})

        #Find links w/in those divs
        link_tags = thumbnail_container.find_all("a", {"class", "gallerythumb"})

        #Find images_urls w/in those links
        urls_to_keep = []
        for tag in link_tags:
            img_tag = tag.find("img")
            url = img_tag["data-src"]
            urls_to_keep.append(url)

        #Modify url to get non thumbnail image.
        modified_urls = []
        for url in urls_to_keep:
            modified_url = url.replace("//t.", "//i.")
            modified_url = modified_url.replace("t.jpg", ".jpg")
            modified_urls.append(modified_url)

    except AttributeError as e:
        print("Nothing found under number")
        return

    #Checks to see if any images were found
    if( not ( len(modified_urls) == 0 ) ):

        #Create directory for images to be downloaded
        new_directory = os.path.join(download_folder, str(number))
        if( not os.path.exists( new_directory ) ):
            os.makedirs( new_directory )
        else:
            print("Directory exists already")

    else:
        print("Nothing found")
        return

    #Start to download the images
    download_dir = os.path.join(download_folder, str(number))

    for index, url in enumerate(modified_urls):

        download_image_from_url(str(index) + ".jpg", url, download_dir)

        print("{0} images downloaded".format(index + 1))

    print("All images downloaded")
    print()

    #When the entire process finishes without fail, then adds it to the download_list
    with open("download_archive.txt", "a") as download_archive:
        download_archive.write(str(number) + "\n")
        print("Recorded {0} in download archive".format(number))

#get_search_url():
#   tags_csv - csv file containing tags to exclude and include
#Purpose of this method is to create a search_url which can be used to scrap for numbers
def get_search_url(tags_csv):

    search_url = "https://nhentai.net/search/?q="

    with open(tags_csv, "r") as tags_csv_file:

        csv_reader = csv.reader(tags_csv_file, delimiter=",")

        #First row of csv file refers to tags to include
        #Second row of csv file refers to tags to exclude

        for row_index, row in enumerate(csv_reader):
            #Line w/ Notes and shit
            if( row_index==0 ):
                continue
            #Tags to include
            elif( row_index==1 ):
                for tag_index, tag in enumerate(row):
                    search_url = search_url + "+\"{0}\"".format(tag)
            #Tags to exclude
            elif( row_index==2 ):
                for tag_index, tag in enumerate(row):
                    search_url = search_url + "+-\"{0}\"".format(tag)

    search_url = search_url.replace(" ", "+")
    search_url = search_url + "&sort=popular"

    print("Final generated search url is: \n{0}".format(search_url))
    print()

    return search_url

#get_numbers_from_search():
#   search_url - url generated from search.
#   stop_num - the number of doujin numbers to record
#This will likely take the search_url from the get_search_url method, and find all of the results
#that show up on the resulting pages
def get_numbers_from_search(search_url, stop_num):

    #Refers to page results shown
    page_num = 0

    #Refers to the number of numbers recorded thusfar
    counter = 0

    #List of numbers that shall be returned
    numbers = []

    while(counter < stop_num):

        #If it reaches this point, it should look to the next page
        page_num += 1

        response = requests.get(search_url + "&page={0}".format(page_num), stream=True)
        html_soup = BeautifulSoup(response.text, "html.parser")

        #Shouldn't need response after this point
        del response

        print("Analyzing results from page {0}".format(page_num))
        print()

        doujin_links = html_soup.find_all("a", {"class", "cover"})

        for doujin_link in doujin_links:

            #Check to see if the count of doujins to be downloaded have been exceeded
            if(counter < stop_num):
                href = doujin_link["href"]
                number = href.replace("/", "").replace("g", "")

                numbers.append(number)

                #At this point a number has been added, so the counter should increase by one
                counter += 1

            #If the count has been exceeded, will break out of checking more numbers
            #If the count has been exceeded, should also break out of while loop above
            else:
                break

    print("List of numbers are: \n{0}".format(numbers))
    print("Total of {0}".format(len(numbers)))
    print()

    return numbers

#get_numbers_from_csv_file():
#   csv_file_path - csv file w/ the id numbers
#If a buddy gives you his/her list of sacred numbers, you can download em all
def get_numbers_from_csv_file(numbers_csv, stop_num):

    numbers = []

    with open(numbers_csv, "r") as csv_file:

        csv_reader = csv.reader(csv_file, delimiter=",")

        for index, row in enumerate(csv_reader):

            if(index < stop_num):
                numbers.append(row[0])
            else:
                break

    return numbers

#download_from_number_list():
#   numbers - list of ints representing nhentai id's
#   stop_num - when to stop adding more downloads
#Downloads from a list of numbers
def download_from_number_list(numbers, stop_num):

    for num_index, number in enumerate(numbers):

        #Since you want to download stop_num number of doujins,
        #and num_index starts @ 0, you use less than
        if(num_index < stop_num):
            download_single_doujin(number)
        else:
            break

#numbers_csv_file_path = os.path.join(file_directory, "csv/numbers.csv")
#

#stop_num = 2

#Method#1 - CSV File w/ Numbers
#numbers = get_numbers_from_csv_file(numbers_csv_file_path, stop_num)

#Method#2 - CSV File w/ Tags
#search_url = get_search_url(tags_csv_file_path)
#numbers = get_numbers_from_search(search_url, stop_num)

#download_from_number_list(numbers, stop_num)

if( sys.argv[1:][0] == "numcsv" ):
    print("Downloading doujins from number csv")
    print()

    numbers_csv_file_path = os.path.join(file_directory, "csv/numbers.csv")

    stop_num = int(sys.argv[1:][1])
    numbers = get_numbers_from_csv_file(numbers_csv_file_path, stop_num)

    download_from_number_list(numbers, stop_num)

elif( sys.argv[1:][0] == "tagcsv" ):
    print("Downloading douins from tags csv")
    print()

    stop_num = int(sys.argv[1:][1])
    tags_csv_file_path = os.path.join(file_directory, "csv/numbers.csv")
    search_url = get_search_url(tags_csv_file_path)
    numbers = get_numbers_from_search(search_url, stop_num)

    download_from_number_list(numbers, stop_num)

elif( sys.argv[1:][0] == "single"):
    print("Downloading a single doujin")
    print()

    download_single_doujin(sys.argv[1:][1])

else:
    print("Unrecognized Mode")
