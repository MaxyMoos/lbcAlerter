# -*- coding: utf-8 -*-

import sqlite3

from lbc_utils import *
from lbc_item import lbc_item


DATABASE_NAME = "file:tmp.db?mode=memory&cache=shared"
TABLE_NAME = "curTable"
IMG_TABLE_NAME = "curImgTable"
DB_CONNECTION = None
DEFAULT_MAX_RESULTS = 5


def openDatabase():
    global DB_CONNECTION
    DB_CONNECTION = sqlite3.connect(DATABASE_NAME, uri=True)
    createDatabaseIfNeeded()


def closeDatabase():
    global DB_CONNECTION
    DB_CONNECTION.close()


def createDatabaseIfNeeded():
    cursor = DB_CONNECTION.cursor()

    try:
        cursor.execute("SELECT count(1) FROM " + TABLE_NAME)
    except sqlite3.OperationalError:
        cursor.execute("CREATE TABLE " + TABLE_NAME +
                       " (id INTEGER PRIMARY KEY, title TEXT, price INTEGER)")
    # Now for images DB
    try:
        cursor.execute("SELECT count(1) FROM " + IMG_TABLE_NAME)
    except sqlite3.OperationalError:
        cursor.execute("CREATE TABLE " + IMG_TABLE_NAME +
                       " (id INTEGER PRIMARY KEY, image BLOB)")

    DB_CONNECTION.commit()
    cursor.close()


def buildItemsFromDBResult(*dbResults):
    items = []
    for dbResult in dbResults:
        curItem = lbc_item(dbResult[0], dbResult[1], dbResult[2])
        getImagesForItem(curItem)
        items += [curItem]
    return items


def getImagesForItem(lbcItem):
    cursor = DB_CONNECTION.cursor()

    try:
        cursor.execute("SELECT image FROM " + IMG_TABLE_NAME
                       + " WHERE id = " + str(lbcItem.id))
        images = cursor.fetchall()
        lbcItem.images = images
    except sqlite3.OperationalError as e:
        log(1, e.args)

    cursor.close()


def insertItemsIntoDatabases(*args):
    import time
    start_time = time.time()
    cursor = DB_CONNECTION.cursor()

    for lbcItem in args:
        try:
            cursor.execute("SELECT * FROM " + TABLE_NAME
                           + " WHERE id = " + str(lbcItem.id))
            # Else we are creating a duplicate item
            if (len(cursor.fetchall()) == 0):
                cursor.execute("INSERT INTO "
                               + TABLE_NAME
                               + " VALUES (?, ?, ?)",
                               (lbcItem.id, lbcItem.title, lbcItem.price,)
                               )
        except sqlite3.OperationalError:
            log(1, "Error while trying to insert instance " +
                str(lbcItem) + " into " + TABLE_NAME)

    DB_CONNECTION.commit()
    cursor.close()
    elapsed_time = time.time() - start_time
    log(2, "insertItemsIntoDatabase elapsed time : {}s".format(elapsed_time))


def insertImagesIntoDatabase(dbConn, *lbcItems):
    cursor = dbConn.cursor()

    for lbcItem in lbcItems:
        try:
            cursor.execute("SELECT COUNT(*) FROM "
                           + IMG_TABLE_NAME
                           + " WHERE id = " + str(lbcItem.id))
            # Assumption: if at least one image exists, all images have already
            # been processed
            if (cursor.fetchone() is None):
                for img_b16_data in lbcItem.images:
                    c.execute("INSERT INTO "
                              + IMG_TABLE_NAME
                              + " VALUES (?, ?)",
                              (lbcItem.id, img_b16_data))
        except sqlite3.OperationalError as e:
            log(0, "Error during image insertion into database : " + e.args)

    dbConn.commit()
    cursor.close()


def getItemFromDatabase(title="", price=-1, itemId=-1):
    cursor = DB_CONNECTION.cursor()
    request = "SELECT * FROM " + TABLE_NAME + " WHERE "
    try:
        if (itemId != -1):
            request += "id = " + str(itemId)
        elif (title != ""):
            request += "title = " + title
        elif (price != -1):
            request += "price = " + str(price)
        else:
            raise ValueError("getItemFromDatabase - at least one parameter \
                             is required to complete request")

        cursor.execute(request)
        dbResults = cursor.fetchall()
        return buildItemsFromDBResult(*dbResults)

    except sqlite3.OperationalError as e:
        log(1, e.args)
        return []


def getItemsFromIds(itemsIds=[]):
    cursor = DB_CONNECTION.cursor()
    try:
        request = "SELECT * FROM " + TABLE_NAME + " WHERE id in ("
        for itemId in itemsIds:
            request += str(itemId)
            if (itemId != itemsIds[-1]):
                request += ", "
            else:
                request += ")"
        cursor.execute(request)
        return buildItemsFromDBResult(*cursor.fetchall())
    except sqlite3.OperationalError as e:
        log(1, e.args)
