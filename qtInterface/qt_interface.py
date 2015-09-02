# -*- coding: utf-8 -*-

from PyQt4.QtGui import *
from PyQt4.QtCore import *
from lbc_utils import *
from qtInterface.qt_pushbullet import *
from qtInterface.qt_utilclasses import *
from datetime import time


NB_SHOWN_ITEMS  =   6


# ****************************

class ItemPanel(QWidget):

    def __init__(self, lbcItem=None):
        super(ItemPanel, self).__init__()
        self._item  =   lbcItem
        self.layout =   QGridLayout()

        titleStr    =   ""
        dateStr     =   ""
        priceStr    =   ""

        if lbcItem is not None:
            titleStr    =   lbcItem.title
            dateStr     =   lbcItem.get_date_string()
            priceStr    =   lbcItem.price

        # Widgets
        self.itemTitle  =   QLabel(titleStr)
        self.itemDate   =   QLabel(dateStr)
        self.itemPrice  =   QLabel(priceStr)

        # Widgets setup
        self.itemTitle.setTextFormat(Qt.RichText)
        self.itemTitle.setOpenExternalLinks(True)

        # Add to layout
        self.layout.addWidget(self.itemTitle)
        self.layout.addWidget(self.itemDate)
        self.layout.addWidget(self.itemPrice)

        self.setLayout(self.layout)

    def getItem(self):
        return self._item

    def updateFromItem(self, lbcItem):
        self._item = lbcItem
        self.itemTitle.setText("<a href=\"" + lbcItem.url + "\">" + lbcItem.title + "</a>")
        self.itemDate.setText(lbcItem.get_date_string())
        self.itemPrice.setText(lbcItem.price)


class SearchButton(QPushButton):
    def __init__(self, string):
        super(SearchButton, self).__init__(string)


class MainWindow(QWidget):


    def __init__(self, mainApp):
        super(MainWindow, self).__init__()
        self.mainAppHandle  =   mainApp
        self.layout = QGridLayout()
        self.itemPanelWidgets = []

        for i in range(0, NB_SHOWN_ITEMS):
            self.itemPanelWidgets += [ItemPanel()]

        # Widgets
        self.queryInput = SearchLineEdit("Recherche:")
        self._regionCombobox    =   QComboBox()
        self.startSearchButton  =   SearchButton("Rechercher")
        self._settingsButton    =   QPushButton("Settings", self)
        # Status bar
        self.statusBar  =   QStatusBar()
        self.statusBar.setSizeGripEnabled(False)
        self.statusBar.setFixedHeight( self.statusBar.minimumHeight() )

        self._settingsButton.clicked.connect( self.showSettingsWindow )


        # Add widgets to layout
        self.layout.addWidget(self.queryInput)
        self.layout.addWidget(self._regionCombobox)
        self.layout.addWidget(self.startSearchButton)
        self.layout.addWidget(self._settingsButton)
        for widget in self.itemPanelWidgets:
            self.layout.addWidget(widget)
            HLine = QFrame()
            HLine.setFrameStyle(QFrame.HLine)
            self.layout.addWidget(HLine)
        self.layout.addWidget(self.statusBar)

        self.setLayout(self.layout)

    def showSettingsWindow(self):
        self.settingsWin = QPushbulletSettings_Window(self.mainAppHandle)
        self.settingsWin.closeWin.connect( lambda: self.mainAppHandle.onClosingSettingsWindow( self.settingsWin.getPushbulletInstances() ) )
        self.settingsWin.show()

    def addItemToRegionCombobox(self, stringItemToAdd):
        self._regionCombobox.addItem(stringItemToAdd)

    def removeItemFromCombobox(self, stringItemToRemove):
        indexToRemove = self._regionCombobox.findText(stringItemToRemove)
        if indexToRemove != -1:
            self._regionCombobox.removeItem( indexToRemove )

    def removeAllItemsFromCombobox(self):
        while self._regionCombobox.count > 0:
            self._regionCombobox.removeItem(0)

    def getRegionValueFromCombobox(self):
        return self._regionCombobox.currentText()

    def updateStatusBar(self, message):
        self.statusBar.showMessage(message)

    def getItems(self):
        result = []
        for panel in self.itemPanelWidgets:
            result += [ panel.getItem() ]
        return result

    def updateItems(self, *newItems):
        for (item, panel) in zip(newItems, self.itemPanelWidgets):
            log(2, "updateItems - item = {}".format(item))
            panel.updateFromItem(item)
        self.updateStatusBar("Last updated at " + datetime.now().strftime("%H:%M") )
