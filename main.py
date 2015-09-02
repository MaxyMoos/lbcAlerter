#!/usr/bin/python3
# -*- coding: utf-8 -*-

import html_parser as parser
import database as db
import settingsManager as settings
from qtInterface.qt_interface import *
from qtInterface.qt_utilclasses import *
from lbc_utils import *

import sys
from threading import Thread


mainApp         = None
displayedItems  = None


def onStart():
    db.openDatabase()

def onClose():
    db.closeDatabase()

def cleanState():
    global displayedItems
    displayedItems = None

def refreshMain():
    global displayedItems

    parser.setRegion( mainApp.mainWin.getRegionValueFromCombobox() )
    newItems = parser.getAndParseResultsPage()
    db.insertItemsIntoDatabases(*newItems)      # This method handles duplicates
    displayedItems = newItems[0:NB_SHOWN_ITEMS]

    curItems    =   mainApp.mainWin.getItems()
    itemsToNotify = [item for item in displayedItems if item not in curItems]
    log( 3, "itemsToNotify = \n{}".format([str(item) + "\n" for item in itemsToNotify]) )
    mainApp.sendPushbulletNotifications(itemsToNotify)
    mainApp.mainWin.updateItems( *(displayedItems) )
    mainApp.mainWin.updateStatusBar( "Last updated at " + getCurTimeString() + " - " + str(len(itemsToNotify)) + " new items added!")



# @Brief : MainApplication is the class used to setup & manage the application main loop
#          Why a class? will you ask. Well we need to stay within the Qt framework
#          so we have to have a class that inherits from QObject. That's why.
class MainApplication(QObject):

    def __init__(self):
        super(MainApplication, self).__init__()
        self._pushbulletInstances = []
        self._settingsManager   =   settings.settingsManager()

        # Load settings on startup if available
        self.setPushbulletInstances( self._settingsManager.getPushbulletAccounts() )


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
                refreshMain()
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
            for lbcItem in displayedItems:
                if len(lbcItem.images) == 0:
                    lbcItem.images = parser.getAndParseItemPage(lbcItem.url)
                    self.writeToDBThreads += [MainApplication.t_saveImagesToDB(lbcItem)]
                    self.writeToDBThreads[-1].start()


    # *****************************************************
    # Thread class to manage images recording into database
    # *****************************************************
    class t_saveImagesToDB(Thread):
        def __init__(self, lbcItem):
            super(MainApplication.t_saveImagesToDB, self).__init__()
            self.lbcItem = lbcItem

        def run(self):
            import os

            self.dbConn = db.sqlite3.connect(db.DATABASE_NAME) # Needed as the sqlite rule is 1 db connection per Thread
            db.insertImagesIntoDatabase(self.dbConn, self.lbcItem)
            self.dbConn.close()


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
        searchString = self.mainWin.queryInput.text()
        log(2, "New search string = {}".format(searchString))
        parser.setSearchTerm(searchString)
        parser.build_full_url( self.mainWin.getRegionValueFromCombobox() ) # Hardcoded for now
        self.updateItemsThread.restart()

    def onClosingSettingsWindow(self, listOfPushbulletAccounts):
        # Callback - We set the active PB accounts and save them in settings file
        self.setPushbulletInstances(listOfPushbulletAccounts)
        self._settingsManager.savePushbulletSettings(listOfPushbulletAccounts)


    # Application main loop. Everything starts and ends here
    def main(self):
        app = QApplication(sys.argv)

        # Initialization of database
        onStart()

        # Let's get some handles
        self.mainWin = MainWindow(self)
        self.updateItemsThread = self.t_UpdateItems()

        # Initialize "Region" combobox with values
        for region in sorted( parser.REGIONS.keys() ):
            self.mainWin.addItemToRegionCombobox(region)

        # Connect signals & slots
        self.mainWin.startSearchButton.clicked.connect( self.onSubmitNewSearchString )
        self.mainWin.queryInput.keyEnterPressed.connect( self.onSubmitNewSearchString )

        self.mainWin.setWindowTitle("LeBonCoin alerter")
        self.mainWin.show()

        self.mainWin.updateStatusBar("sqlite3 version " + db.sqlite3.sqlite_version)

        app.exec_()

        onClose()
        sys.exit()



if __name__ == "__main__":
    mainApp = MainApplication()
    mainApp.main()
