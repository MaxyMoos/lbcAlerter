import json
import requests
from lbc_utils import log


# @brief:   This class represents a Pushbullet account (i.e : one PB token), with all its attached devices
#           Hence the inner class PushbulletDevice
#           It's this object that handles all the Pushbullet API requests, including sending pushes
class Pushbullet():

    # Inner class for PB devices
    # --------------------------
    class PushbulletDevice():

        def __init__(self, JSON=None, Account=None):
            if json is not None:
                self._nickname      =   JSON['nickname']
                self._iden          =   JSON['iden']
                self._type          =   JSON['type']
                self._active        =   JSON['active']
                self._parentAccount =   Account
            else:
                raise ValueError("Cannot init PushbulletDevice without json data")


        def __str__(self):
            if ( self._nickname is not None and self._iden is not None and self._type is not None ):
                return str(self._nickname) + " / iden: " + str(self._iden) + " / " + str(self._type)
            else:
                return "None"

        def getAccount(self):
            return self._parentAccount

        def isInSendlist(self):
            return self._iden in self._parentAccount.sendlist

        def getIden(self):
            return self._iden


    # Constants
    # ---------
    JSON_HEADER     =   {"Content-Type":"application/json"}

    PB_URL_ME       =   "https://api.pushbullet.com/v2/users/me"
    PB_URL_DEVICES  =   "https://api.pushbullet.com/v2/devices"
    PB_URL_PUSH     =   "https://api.pushbullet.com/v2/pushes"



    # Methods & functions
    # -------------------
    def __init__(self, pb_token=None, JSON=None):
        self.devices            =   []
        self.sendlist           =   []

        if JSON is not None:
            self._pushbulletToken   =   JSON["_pushbulletToken"]
            for deviceJSON in JSON["devices"]:
                self.devices += [ Pushbullet.PushbulletDevice(JSON=deviceJSON, Account=self) ]
                log(1, "Added device to new instance: " + str(self.devices[-1]) )
            self.sendlist   =   JSON["sendlist"]
        elif pb_token is not None:
            self._pushbulletToken   =   pb_token
        else:
            raise ValueError("Cannot initialize a Pushbullet object with no Token or no JSON data")

        # Session object must always be initialized
        self.curSession         =   requests.session()
        self.curSession.headers.update(self.JSON_HEADER)
        authParam = "Bearer " + self._pushbulletToken
        self.curSession.headers.update({"Authorization":authParam})

    def __eq__(self, other):
        return self._pushbulletToken == other._pushbulletToken and self.getDevices() == other.getDevices()

    def __str__(self):
        result = "Token = " + self._pushbulletToken + "\n"
        self.getDevices()
        result += "\n".join( [str(device) + "\n" for device in self.devices] )
        return result

    def getToken(self):
        return self._pushbulletToken

    def getDevices(self, forceRefresh=False):
        if len(self.devices) == 0 or forceRefresh:
            try:
                response    =   self.curSession.get(self.PB_URL_DEVICES)
                if ( response.status_code != 200 ):
                    log(1, "Error during getDevices request - HTTP " + str(response.status_code) )
                    return None
                else:
                    for device in response.json()['devices']:
                        self.devices += [self.PushbulletDevice(device, Account=self)]
                    return response.json()['devices']
            except Exception as e:
                log(0, e.args)
                return None

    def addDeviceToSendlist(self, deviceIden):
        if not deviceIden in self.sendlist:
            self.sendlist += [deviceIden]

    def sendLinkToDevicesInSendlist(self, title="", body="", url="", lbcItem=None):
        if lbcItem is not None:
            _title  =   lbcItem.getTitle()
            _body   =   lbcItem.get_date_string() + " - " + lbcItem.getPrice()
            _url    =   lbcItem.getURL()
        else:
            _title  =   title
            _body   =   body
            _url    =   url

        for deviceIden in self.sendlist:
            data    =   {
                            "type"  :   "link",
                            "title" :   _title,
                            "body"  :   _body,
                            "url"   :   _url,
                        }

            return self.curSession.post(self.PB_URL_PUSH, data=json.dumps(data))

    def getJSONCompatibleDict(self):
        # Request objects are not JSON-serializable & are not useful to save, so we need to omit them when exporting
        return { key:value for key, value in self.__dict__.items() if key is not "curSession" }
