#DOUJIN_DL.py

#2/20/2020

#Figured out reason behind situational 403 forbidden response
#Was b/c I assumed all images were of type .jpg
#Although rarer, there were files of .png

#Author: MagicalGirl012
#        https://github.com/MagicalGirl012

#Description:
#   downloads doujins from nhentai.net
#   can download a single doujin
#   or multiple doujins from a search query / csv


#Packages
import sys
import os
import requests
from bs4 import BeautifulSoup
import csv

from fake_useragent import UserAgent

print("All packages initialized")
print()

#Get the directory which the file runs from
file_directory_absolute_path, filename = os.path.split(os.path.abspath(__file__))

#Get the folder where files are downloaded to
downloads_folder_absolute_path = os.path.join(file_directory_absolute_path, "downloads")

#Gets the absolute path of the folder with download archives
#Avoids Duplicates
archives_folder_absolute_path = os.path.join(file_directory_absolute_path, "archives")

#Change working directory
os.chdir(file_directory_absolute_path)

#Useragent to avoid error 403
ua = UserAgent()

#create_headers()
#   Not necessary in the case of downloading from nhentai.net
#   However, it is still decent practice since some other sites may require this

def create_headers(ua = ua):
    random_user_agent = ua.random
    headers = {"User-Agent": random_user_agent}

    print("Generated Header: \n{0}".format(headers))

    return headers

#download_image_from_url():
#   file_name - String representing what to call the downloaded file
#   web_url - String representing URL to image to download
#   download_dir - directory to download the image to
#Method name is self-explanatory
def download_image_from_url(file_name, web_url, download_dir):

    #This line seems to work individually in terminal, but is inconsistent when downloading in the program
    #Don't quite understand why exactly this happens.
    response = requests.get(web_url, headers=create_headers(), stream=True)
    if( response.status_code == 200 ):
        with open( os.path.join(download_dir, file_name), 'wb' ) as out_file:
            out_file.write(response.content)
    else:
        print("Error in downloading image {0}".format(file_name))
        print("Exit Status: {0}".format(response.status_code))

    #cleanup
    del response

#download_single_doujin():
#   six_digit_number - int representing where one can find the art of their liking
#Purpose of method is to download a single doujin from a six_digit_number
#Calls the download_image_from_url method to accomplish this task
def download_single_doujin(id_number, archives_folder_absolute_path = archives_folder_absolute_path, downloads_folder_absolute_path = downloads_folder_absolute_path):

    #Check to see if the id number is in the download list
    with open( os.path.join(archives_folder_absolute_path, "id_number_download_archive.txt") , "r") as id_number_download_archive_file:
        if( str(id_number) in id_number_download_archive_file.read() ):
            print("{0} is already in the id number download archive, canceling".format(id_number))
            print()

            return
        else:
            print("{0} is not in the id number download archive, proceeding".format(id_number))
            print()

    url_base = "https://nhentai.net/g/"
    url = url_base + str(id_number)

    response = requests.get(url, headers=create_headers(), stream=True)

    html_soup = BeautifulSoup(response.text, "html.parser")

    #Debugging - See if request got an error
    #print(html_soup)

    #Check to see if the title of the doujin is the the title download archive (Avoids majority of duplicates from multiple translators)
    doujin_title = html_soup.find("h1").getText()

    print("Title of the doujin is: {0}".format(doujin_title))
    print()

    with open( os.path.join(archives_folder_absolute_path, "title_download_archive.txt"), "r" ) as title_download_archive_file:
        if( str(doujin_title) in title_download_archive_file.read() ):
            print("{0} is already in the title download archive, canceling".format(doujin_title))
            print()

            return
        else:
            print("{0} is not in the title download archive, proceeding".format(doujin_title))
            print()

    print("Proceeding to download: {0}".format(id_number))
    print()

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
            modified_url = modified_url.replace("t.png", ".png") #ALSO CHECK FOR .PNG

            modified_urls.append(modified_url)

    except AttributeError as e:
        print("Nothing found under number")
        return
    except Exception as e: #For all other errors
        print(e)
        return

    #Checks to see if any images were found
    if( not ( len(modified_urls) == 0 ) ):

        #Create directory for images to be downloaded
        new_directory = os.path.join(downloads_folder_absolute_path, str(doujin_title))
        if( not os.path.exists( new_directory ) ):
            os.makedirs( new_directory )
        else:
            print("Directory exists already")
            print()

    else:
        print("Nothing found")
        print()
        return

    #Start to download the images
    download_dir = os.path.join(downloads_folder_absolute_path, str(doujin_title))

    #print(modified_urls)

    #If there is a 't' in the number component before the jpg, will ruin the entire process
    #This was the cause for the error 403 response
    #The problems lies w/ the way the program analyzes the html, but I am too lazy to find an elegant solution


    for index, url in enumerate(modified_urls):

        download_image_from_url(str(index) + ".jpg", url, download_dir)

        print("{0} images processed".format(index + 1))
        print()

    print("All images downloaded")
    print()

    #When the entire process finishes without fail, then adds it to the download_list
    with open( os.path.join(archives_folder_absolute_path, "id_number_download_archive.txt") , "a") as id_number_download_archive_file:
        id_number_download_archive_file.write( str(id_number) + "\n" )
        print("Recorded {0} in id number download archive".format(id_number))
        print()

    #Also add the doujin title to the title_download_archive
    with open( os.path.join(archives_folder_absolute_path, "title_download_archive.txt"), "a" ) as title_download_archive_file:
        title_download_archive_file.write( str(doujin_title) + "\n" )
        print("Recorded {0} in the title download archive".format(doujin_title))
        print()

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

        response = requests.get(search_url + "&page={0}".format(page_num), headers=create_headers, stream=True)
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

    numbers_csv_file_path = os.path.join(file_directory_absolute_path, "csv/numbers.csv")

    stop_num = int(sys.argv[1:][1])
    numbers = get_numbers_from_csv_file(numbers_csv_file_path, stop_num)

    download_from_number_list(numbers, stop_num)

elif( sys.argv[1:][0] == "tagcsv" ):
    print("Downloading douins from tags csv")
    print()

    stop_num = int(sys.argv[1:][1])
    tags_csv_file_path = os.path.join(file_directory_absolute_path, "csv/tags.csv")
    search_url = get_search_url(tags_csv_file_path)
    numbers = get_numbers_from_search(search_url, stop_num)

    download_from_number_list(numbers, stop_num)

elif( sys.argv[1:][0] == "single"):
    print("Downloading a single doujin")
    print()

    download_single_doujin(sys.argv[1:][1])

else:
    print("Unrecognized Mode")
