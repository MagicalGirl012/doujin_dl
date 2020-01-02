doujin_dl.py

1/2/2020

Author: MagicalGirl012
        https://github.com/MagicalGirl012

python doujin_dl.py [mode] [number]

Modes:
  1 - numcsv
    numcsv: download doujins from a csv file w/ doujin id numbers in it
            looks for csv file in the csv folder called "numbers.csv"
    stop_num: refers to the number of doujins to download before the program stops

    Ex:
      python doujin_dl.py numcsv 20
        downloads up to 20 doujins
      python3 doujin_dl.py numcsv 100
        downloads up to 100 doujins

  2 - tagcsv
    tagcsv: download doujins from a csv file w/ doujin tags in it
            will perform a search to find doujins that meet tag requirements
            looks for csv file in the csv folder called "tags.csv"
    stop_num: refers to the number of doujins to download before the program stops

    Ex:
      python doujin_dl.py tagcsv 20
        downloads up to 20 doujins
      python3 doujin_dl.py tagcsv 100
        downloads up to 100 doujins

  3 - single
    single: download a single doujin based upon a number
    number: refers to the doujin id to download

    Ex:
      python doujin_dl.py single 177013
        downloads doujin from nhentai.net w/ id of 177013
