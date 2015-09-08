# -*- coding: utf-8 -*-
import os.path
import json
from lbc_utils import *
from pushbulletJsonEncoder import *


SETTINGS_FILE_PATH                      =   "./UserSettings.json"
SETTINGS_FILE_PUSHBULLET_DEVICES_TAG    =   "Pushbullet Devices"


class settingsManager():

    def __init__(self):
        self._data  =   {}    #   Holds the contents of the settings file when opened on app launch

        try:
            with open(SETTINGS_FILE_PATH) as settingsFile:
                self._data = json.load( settingsFile )
        except FileNotFoundError as err:
            pass # self._data is already initialized

    def savePushbulletSettings(self, listOfPushbulletAccounts):
        if len(listOfPushbulletAccounts) > 0:
            with open(SETTINGS_FILE_PATH, mode="w") as settingsFile:
                settingsFile.write( json.dumps( {"Pushbullet accounts":listOfPushbulletAccounts}, cls=PushbulletJSONEncoder, indent=4, sort_keys=True ) )

    def getPushbulletAccounts(self):
        accounts = []

        try:
            for element in self._data["Pushbullet accounts"]:
                log(0, "Loading account from settings : {}".format(element) )
                accounts += [ Pushbullet(JSON=element) ]
        except KeyError:
            pass # No accounts available in settings file
        return accounts
