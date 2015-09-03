# -*- coding: utf-8 -*-
# HTML parsing code

from urllib.request import urlopen
from urllib.parse import quote
from bs4 import BeautifulSoup
from socket import timeout

import database
from lbc_utils import *
from lbc_item import *

import re
from datetime import datetime, timedelta, date



BASE_URL        =   "http://www.leboncoin.fr"
STANDARD_SUFFIX =   "/annonces/offres"

# TODO - Add remaining region choices in this dict
REGIONS    =   {
                    'France'            :   '/occasions/',
                    'Paris'             :   '/ile_de_france/paris/',
                    'Île-de-France'     :   '/ile_de_france/'
                }

SEARCH_PARAMS   =   "?f=a&th=0&q=" # th=0 disables thumbnails so the html response is as small as possible

SEARCH_TERM     =   ""
CUR_REGION      =   ""
FULL_URL        =   ""


def setSearchTerm(newSearchString):
    global SEARCH_TERM
    SEARCH_TERM = newSearchString.replace(' ', '+')
    log(1, "setSearchTerm triggered with new search : " + newSearchString)

def setRegion(newRegion):
    global CUR_REGION
    if newRegion in REGIONS.keys():
        CUR_REGION = newRegion

def getSoup(url):
    try:
        f = urlopen( url )
    except Exception as e:
        log(1, getCurDateTimeString() + " - CONNECTION ERROR, check your Internet connectivity" )
        return []
    return BeautifulSoup(f)

def build_full_url(region):
    global FULL_URL

    if region in REGIONS.keys():
        FULL_URL = BASE_URL + STANDARD_SUFFIX + REGIONS[region] + SEARCH_PARAMS + SEARCH_TERM
        log(1, "FULL_URL = {}".format(FULL_URL))
    else:
        raise ValueError("region value (\"" + region + "\") is not good or supported")

# @Brief: Extracts date from an item HTML block
# @Return_Format: datetime instance
def getDate(dateElement):
    monthsInfo = {
                    'janvier'   :   1,
                    'février'   :   2,
                    'mars'      :   3,
                    'avril'     :   4,
                    'mai'       :   5,
                    'juin'      :   6,
                    'juillet'   :   7,
                    'août'      :   8,
                    'sept'      :   9,
                    'octobre'   :   10,
                    'novembre'  :   11,
                    'décembre'  :   12
                }

    if dateElement:
        # Input string is filled with extra spaces => strip + split string to ease processing
        str_elements = [i.strip() for i in dateElement.text.split("\n") if i.strip() != ""]

        if (str_elements[0] == "Aujourd'hui"):
            day = datetime.now().day
            month = datetime.now().month
        elif (str_elements[0] == "Hier"):
            yday = datetime.now() - timedelta(days=1)
            day = yday.day
            month = yday.month
        else:
            day = int(re.search("[0-9]+", str_elements[0]).group())
            month = monthsInfo[re.search("(\w+)$", str_elements[0]).group()]

        hour    =   int(str_elements[1][0:2])
        minutes =   int(str_elements[1][3:5])

        return datetime(datetime.today().year, month, day, hour=hour, minute=minutes)

def getAndParseResultsPage():
    import time
    start_time = time.time()
    soup = getSoup(FULL_URL)
    log(1, "Updated search results from URL : " + FULL_URL)

    results = []

    if soup:
        x = soup.body.find_all('div', attrs={'class': 'lbc'})

        for elem in x:
            try:
                title   =   elem.find("div", attrs={'class':'detail'}).h2.string.strip()
                price   =   elem.find("div", attrs={'class':'price'})
                if price:   price = price.string.strip()
                date    =   getDate(elem.find("div", attrs={'class':'date'}))
                url     =   elem.parent['href']
                images  =   [] # getAndParseItemPage(url)

                id_regex = re.search("[0-9]+(?=\.htm)", url)
                if id_regex: itemId = str(id_regex.group())
                else: itemId = -1   # TODO - Throw error instead of this

                results += [lbc_item(itemId=itemId, title=title, price=price, date=date, url=url, images=images)]

                log(3, "ID = {}".format(itemId))
                log(3, "title = {}".format(title) )
                log(3, "date = {}".format(date))
                log(3, "price = {}".format(price) )
                log(3, "{}".format(images) )
                log(3, "************************" )
                log(3, "\n")

            except Exception as e:
                log( 1, "Error while parsing the following object:\n{}\nError: {}".format(title, e.args) )

    elapsed_time = time.time() - start_time
    log(2, "getAndParseResultsPage - elapsed_time = {}s".format(elapsed_time))
    return results

def getAndParseItemPage(itemURL):
    images = []

    soup = getSoup(itemURL)

    if soup:
        x = soup.body.find_all("meta", attrs={'itemprop':'image'})
        for elem in x:
            try:
                images += [elem['content']]
            except Exception as e:
                log(1,"Error while parsing the following object:\n{}".format(elem))
        return images
