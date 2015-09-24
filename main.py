#!/usr/bin/python3
# -*- coding: utf-8 -*-

import html_parser as parser
import database as db
import settingsManager as settings
from qtInterface.qt_interface import *
from qtInterface.qt_utilclasses import *
from lbc_utils import *

import sys
import requests
import base64
from threading import Thread


mainApp         = None


# @Brief : MainApplication is the class used to setup & manage the application main loop
#          Why a class? will you ask. Well we need to stay within the Qt framework
#          so we have to have a class that inherits from QObject. That's why.
class MainApplication(QObject):

    def __init__(self):
        super(MainApplication, self).__init__()
        self._curSearchQuery        =   ""
        self._curSearchRegion       =   ""
        self._displayedItems        =   []
        self._pushbulletInstances   =   []
        self._settingsManager       =   settings.settingsManager()
        # Load Pushbullet settings on startup if available
        self.setPushbulletInstances( self._settingsManager.getPushbulletAccounts() )

    def onStart(self):
        db.openDatabase()

    def onClose(self):
        db.closeDatabase()


    # ******************************************
    # Thread class to manage async item updates
    # ******************************************
    class t_UpdateItems(Thread):
        def __init__(self):
            super(MainApplication.t_UpdateItems, self).__init__()
            self.timer = QTimer()
            self.timer.setSingleShot(True)
            self.timer.timeout.connect(self.run)

        def restart(self):
            self.timer.stop()
            self.run()

        def run(self):
            try:
                mainApp.refreshMainWindow()
            except Exception as e:
                log(0, e.args)
            finally:
                getImagesThread = MainApplication.t_getImages()
                getImagesThread.start()
                self.timer.start(60000)

    # ***************************************
    # Thread class to manage images retrieval
    # ***************************************
    class t_getImages(Thread):
        def __init__(self):
            super(MainApplication.t_getImages, self).__init__()
            self.writeToDBThreads = []

        def run(self):
            for itemWidget in mainApp.mainWin.itemPanelWidgets:
                curItem = itemWidget.getItem()
                if curItem and len(curItem.images) == 0:
                    imgURLs = parser.getAndParseItemPage(curItem.url)
                    for url in imgURLs:
                        imgFile = requests.get(url)
                        curItem.images += [base64.b16encode(imgFile.content)]
                    self.writeToDBThreads += [MainApplication.t_saveImagesToDB(itemWidget)]
                    self.writeToDBThreads[-1].start()


    # *****************************************************
    # Thread class to manage images recording into database
    # *****************************************************
    class t_saveImagesToDB(Thread):
        def __init__(self, itemWidget):
            super(MainApplication.t_saveImagesToDB, self).__init__()
            self.itemWidget = itemWidget
            self.lbcItem = itemWidget.getItem()

        def run(self):
            import os

            self.dbConn = db.sqlite3.connect(db.DATABASE_NAME, uri=True) # Needed as the sqlite rule is 1 db connection per Thread
            db.insertImagesIntoDatabase(self.dbConn, self.lbcItem)
            self.dbConn.close()
            # Update the widget to display/enable image button
            self.itemWidget.setImageButtonVisibility(True)

    def setPushbulletInstances(self, pbInstances):
        self._pushbulletInstances   =   pbInstances

    def getPushbulletInstances(self):
        return self._pushbulletInstances

    def sendPushbulletNotifications(self, items):
        counter = 0
        for item in items:
            for pbInstance in self._pushbulletInstances:
                log(3, "mainApp.pushbulletInstance number {} = ".format(counter) + str(pbInstance))
                counter += 1
                pbInstance.sendLinkToDevicesInSendlist(lbcItem=item)

    def getSettingsManager(self):
        return self._settingsManager

    def onSubmitNewSearchString(self):
        self._curSearchQuery = self.mainWin.queryInput.text()
        log( 2, "New search string = {}".format(self._curSearchQuery) )
        self.updateItemsThread.restart()

    def onChangingRegion(self, newRegionValueIndex):
        self._curSearchRegion = sorted(parser.REGIONS.keys())[newRegionValueIndex]
        log( 2, "New region value : {}".format(self._curSearchRegion) )

    def onClosingSettingsWindow(self, listOfPushbulletAccounts):
        # Callback - We set the active PB accounts and save current state in settings file
        self.setPushbulletInstances(listOfPushbulletAccounts)
        self._settingsManager.saveSettings(self.mainWin.queryInput.text(), self.mainWin.getRegionValueFromCombobox(), listOfPushbulletAccounts )

    def refreshMainWindow(self):
        newItems = parser.getItemsFromWebpage( self._curSearchQuery, self._curSearchRegion )
        db.insertItemsIntoDatabases(*newItems)      # This method handles duplicates
        self._displayedItems = newItems[0:NB_SHOWN_ITEMS]

        curItems    =   mainApp.mainWin.getItems()
        itemsToNotify = [item for item in self._displayedItems if item not in curItems]
        log( 3, "itemsToNotify = \n{}".format([str(item) + "\n" for item in itemsToNotify]) )
        mainApp.sendPushbulletNotifications(itemsToNotify)
        mainApp.mainWin.updateItems( *(self._displayedItems) )
        mainApp.mainWin.updateStatusBar( "Last updated at " + getCurTimeString() + " - " + str(len(itemsToNotify)) + " new items added!")


    # Application main loop. Everything starts and ends here
    def main(self):
        app = QApplication(sys.argv)

        # Initialization of database
        self.onStart()

        # Let's get some handles
        self.mainWin = MainWindow(self)
        self.updateItemsThread = self.t_UpdateItems()

        # Initialize "Region" combobox with values
        for region in sorted( parser.REGIONS.keys() ):
            self.mainWin.addItemToRegionCombobox(region)

        # Init search from UserSettings config file if available
        searchQuery, searchRegion = self._settingsManager.getSearchSettings()
        if searchQuery != "" and searchRegion != "":
            self._curSearchQuery = searchQuery
            self._curSearchRegion = searchRegion
            self.mainWin.queryInput.setText(searchQuery)
            timer = QTimer()
            timer.setSingleShot(True)
            timer.timeout.connect( self.onSubmitNewSearchString )
            timer.start(1000)

        # Connect signals & slots
        self.mainWin.startSearchButton.clicked.connect( self.onSubmitNewSearchString )
        self.mainWin.queryInput.keyEnterPressed.connect( self.onSubmitNewSearchString )

        self.mainWin.setWindowTitle("LeBonCoin alerter")
        self.mainWin.show()

        self.mainWin.updateStatusBar("sqlite3 version " + db.sqlite3.sqlite_version)

        app.exec_()

        self.onClose()
        sys.exit()



if __name__ == "__main__":
    mainApp = MainApplication()
    mainApp.main()
