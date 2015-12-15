# -*- coding: utf-8 -*-

from PyQt4.QtGui import *
from PyQt4.QtCore import *
from lbc_utils import *
from qtInterface.qt_utilclasses import *
from pushbullet_max import Pushbullet


class QPushbulletDevice(QWidget):

    def __init__(self, pbDevice, parent=None):
        super(QPushbulletDevice, self).__init__(parent)
        self._layout = QHBoxLayout()
        self._pbDevice = pbDevice
        self._nameLabel = QLabel(pbDevice._nickname)
        self._typeLabel = QLabel(pbDevice._type)
        self._selectedCheckbox = QCheckBox("Send notifications", self)

        self._selectedCheckbox.setCheckState(
            Qt.Checked if pbDevice.isInSendlist() else Qt.Unchecked)

        # Connect signals <-> slots
        self._selectedCheckbox.toggled.connect(lambda: self.parentWidget().toggleNotificationsForDevice(self._selectedCheckbox.isChecked(), self._pbDevice))

        # Add widgets to layout
        self._layout.addWidget(self._nameLabel)
        self._layout.addWidget(self._typeLabel)
        self._layout.addWidget(self._selectedCheckbox)

        self.setLayout(self._layout)

    def getCheckbox(self):
        return self._selectedCheckbox


class QPushbulletAccount(QWidget):

    class QPbAccountHeadline(QWidget):
        def __init__(self, token, parent):
            super().__init__(parent)
            self.accountLabel = QLabel(
                "Pushbullet account + " + token)
            self.accountLabel.setStyleSheet("QLabel { \
                                                    background-color : green; \
                                                    color: white \
                                                 }")
            self.removeAccountButton = QPushButton("Remove")
            self.removeAccountButton.clicked.connect(lambda: self.parentWidget().parentWidget().removeAccount(token))

            self.layout = QHBoxLayout()
            self.layout.addWidget(self.accountLabel)
            self.layout.addWidget(self.removeAccountButton)
            self.setLayout(self.layout)
 


    def __init__(self, pbInstance, parent=None):
        super(QPushbulletAccount, self).__init__(parent)
        self._pbInstance = pbInstance
        self._devices = []

        self._layout = QGridLayout()
        self.headlineWidget = self.QPbAccountHeadline(self._pbInstance.getToken(), self)
        self._layout.addWidget(self.headlineWidget)

        self._pbInstance.getDevices()
        for device in self._pbInstance.devices:
            newDev = QPushbulletDevice(device, parent=self)
            self._layout.addWidget(newDev)
            self._devices += [newDev]

        self.setLayout(self._layout)

    def delete(self):
        self._pbInstance = None
        self._devices = []
        while self._layout.takeAt(0) != None:
            item = self._layout.takeAt(0)
            item.widget = None
            item = None
        self.headlineWidget.delete()
        self.headlineWidget = None


    def toggleNotificationsForDevice(self, mustAdd, device):
        if mustAdd:
            self._pbInstance.addDeviceToSendlist(device.getIden())
            log(1, "Device " + str(device) + " added to Pushbullet sendlist")
        else:
            self._pbInstance.removeDeviceFromSendlist(device.getIden())
            log(1, "Device " + str(device) +
                " removed from Pushbullet sendlist")


class QPushbulletSettings_Window(QDialog):

    # Signal used to transmit the latest Pushbullet instances to the MainApp
    # handle when closing Settings window
    closeWin = pyqtSignal()


    def __init__(self, mainAppHandle):
        super(QPushbulletSettings_Window, self).__init__()
        self._pbInstancesWidgets = []  # Handles to the widgets
        self._pbInstances = []

        self._mainAppHandle = mainAppHandle
        self._layout = QGridLayout()
        self.pbInputTextLabel = QLabel(
            "Copy/paste a Pushbullet account token then press Enter:")
        self.pbTokensInputText = SearchLineEdit()

        # Connect slots<->signals
        self.pbTokensInputText.keyEnterPressed.connect(
            self.refreshPushbulletTokens)
        # Setup layout
        self._layout.addWidget(self.pbInputTextLabel)
        self._layout.addWidget(self.pbTokensInputText)
        self.setLayout(self._layout)

        # Load current Pushbullet instances from main App handle
        self.setPushbulletInstances(
            self._mainAppHandle.getPushbulletInstances())
        self.refreshQPushbulletAccountsShown()
        self.setWindowTitle("Pushbullet settings")


    def setPushbulletInstances(self, listOfPushbulletAccounts):
        self._pbInstances = listOfPushbulletAccounts


    def getPushbulletInstances(self):
        return self._pbInstances


    def removeAccount(self, accountToken):
        for pbInstance in self._pbInstances:
            if pbInstance.getToken() == accountToken:
                self._pbInstances.remove(pbInstance)
                for pbAccountWidget in self._pbInstancesWidgets:
                    if pbAccountWidget._pbInstance.getToken() == accountToken:
                        self._pbInstancesWidgets.remove(pbAccountWidget)
                        pbAccountWidget.setParent(None)
                        break
        self.refreshQPushbulletAccountsShown()


    def refreshQPushbulletAccountsShown(self):
        # Create a widget per Pushbullet instance available & show it
        for curPbInstance in self._pbInstances:
            tmpAccount = QPushbulletAccount(curPbInstance, parent=self)
            self._pbInstancesWidgets += [tmpAccount]
            self._layout.addWidget(tmpAccount)
            self.setLayout(self._layout)
        # Hack: next line necessary if resize call is to work
        QCoreApplication.processEvents()
        self.resize(self.minimumSizeHint())


    def refreshPushbulletTokens(self):
        new_tokens = self.pbTokensInputText.text().split(';')
        for token in new_tokens:
            if token not in [instance.getToken() for instance in self._pbInstances]:
                try:
                    self._pbInstances += [Pushbullet(token)]
                except ValueError as e:
                    print(e)
        self.refreshQPushbulletAccountsShown()


    def closeEvent(self, event):
        self.closeWin.emit()
        event.accept()
