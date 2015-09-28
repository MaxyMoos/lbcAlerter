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


def getSoup(url):
    try:
        f = urlopen( url )
    except Exception as e:
        log(1, getCurDateTimeString() + " - CONNECTION ERROR, check your Internet connectivity" )
        return []
    return BeautifulSoup(f)


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


def parseDivElement(elem):
    title   =   elem.find( "div", attrs={'class':'detail'} ).h2.string.strip()
    price   =   elem.find( "div", attrs={'class':'price'} )
    if price:
        price = price.string.strip()
    date    =   getDate( elem.find("div", attrs={'class':'date'}) )
    url     =   elem.parent['href']
    images  =   []

    itemID_regex = re.search("[0-9]+(?=\.htm)", url)
    if itemID_regex:
        itemID = str( itemID_regex.group() )
    else:
        # TODO - Raise an error instead of this
        itemID = -1
    return lbc_item( itemId=itemID, title=title, price=price, date=date, url=url, images=images )

def convertSpecialCharToHTML(text):
    from html.entities import codepoint2name
    resultStr = text
    for key, value in codepoint2name.items():
        if chr(key) in text:
            resultStr = text.replace(chr(key), "&" + value + ";")
    return resultStr

def removeAccentuatedCharacters(text):
    import unicodedata
    return unicodedata.normalize('NFD', text).encode('ascii', 'ignore').decode('utf-8')

def formatSearchQueryForRequest(searchQuery):
    # Unaccented letters lead to same search results, and sending accents in URLs is painful
    # so we remove them. LBC also replaces whitespaces with '+' characters in URLs
    resultStr = removeAccentuatedCharacters(searchQuery)
    resultStr = resultStr.replace(' ', '+')
    return resultStr

def getItemsFromWebpage( searchQuery="", searchRegion="" ):
    results     =   []
    url         =   BASE_URL + STANDARD_SUFFIX + REGIONS[searchRegion] + SEARCH_PARAMS + formatSearchQueryForRequest(searchQuery) #searchQuery.replace(' ', '+')
    parsedPage  =   getSoup(url)
    if parsedPage:
        divElements     =   parsedPage.body.find_all( 'div', attrs={'class':'lbc'} )
        for divElem in divElements:
            try:
                item = parseDivElement(divElem)
                if item:
                    results += [item]
            except Exception as e:
                log( 1, "Error while parsing the following object:\n{}\nError: {}".format(title, e.args) )
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
