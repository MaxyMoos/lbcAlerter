# -*- coding: utf-8 -*-

import json
from lbc_utils import *
from pushbulletJsonEncoder import *

SETTINGS_FILE_PATH = "./UserSettings.json"

TAG_SEARCH_GLOBAL = "Search"
TAG_SEARCH_QUERY = "Query"
TAG_SEARCH_REGION = "Region"
TAG_PUSHBULLET_ACCOUNTS = "Pushbullet accounts"


class settingsManager():

    def __init__(self):
        # Holds the contents of the settings file when opened on app launch
        self._data = {}
        try:
            with open(SETTINGS_FILE_PATH) as settingsFile:
                self._data = json.load(settingsFile)
        except FileNotFoundError:
            pass  # self._data is already initialized

    def saveSettings(self, searchTerm, searchRegion, listOfPushbulletAccounts):
        globalSettings = {
            TAG_SEARCH_GLOBAL: {
                TAG_SEARCH_QUERY: searchTerm,
                TAG_SEARCH_REGION: searchRegion
            },

            TAG_PUSHBULLET_ACCOUNTS: listOfPushbulletAccounts
        }
        with open(SETTINGS_FILE_PATH, mode="w") as settingsFile:
            settingsFile.write(
                json.dumps(globalSettings, cls=PushbulletJSONEncoder, indent=4, sort_keys=True))

    def getSearchSettings(self):
        try:
            searchSettings = self._data[TAG_SEARCH_GLOBAL]
            return searchSettings[TAG_SEARCH_QUERY], searchSettings[TAG_SEARCH_REGION]
        except KeyError:
            return "", ""  # Settings file does not exist yet. Doesn't matter

    def getPushbulletAccounts(self):
        accounts = []

        try:
            for element in self._data[TAG_PUSHBULLET_ACCOUNTS]:
                accounts += [Pushbullet(JSON=element)]
        except KeyError:
            print("No accounts found in settings file")
            pass  # No accounts available in settings file
        return accounts
