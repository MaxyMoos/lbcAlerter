# -*- coding: utf-8 -*-
import os.path
import json
from pushbulletJsonEncoder import *


SETTINGS_FILE_PATH                      =   "./UserSettings.json"
SETTINGS_FILE_PUSHBULLET_DEVICES_TAG    =   "Pushbullet Devices"


class settingsManager():

    def savePushbulletSettings(self, listOfPushbulletAccounts):
        with open(SETTINGS_FILE_PATH, mode="w") as settingsFile:
            settingsFile.write( json.dumps( {"Pushbullet accounts":listOfPushbulletAccounts}, cls=PushbulletJSONEncoder, indent=4, sort_keys=True ) )

    def parseSettingsFile(self):
        with open(SETTINGS_FILE_PATH, mode="r") as settingsFile:
            accounts = []

            data = json.load( settingsFile )
            for element in data["Pushbullet accounts"]:
                accounts += [ Pushbullet(JSON=element) ]
            return { 'Pushbullet':accounts }

    def getPushbulletAccounts(self):
        accounts = []

        with open(SETTINGS_FILE_PATH, mode="r") as settingsFile:
            data = json.load( settingsFile )
            for element in data["Pushbullet accounts"]:
                accounts += [ Pushbullet(JSON=element) ]
        return accounts
