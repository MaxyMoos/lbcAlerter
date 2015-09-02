# -*- coding: utf-8 -*-
import json
from pushbullet_max import Pushbullet


class PushbulletJSONEncoder(json.JSONEncoder):

    def default(self, object):

        if isinstance(object, Pushbullet.PushbulletDevice):
            tmpDict = dict(object.__dict__) # Make a hardcopy. Else we modify the original dict...
            for key in object.__dict__.keys():
                if key == "_parentAccount": # Don't save this backref in the JSON settings file -> circular dependency problem
                    tmpDict.pop(key)
                elif key[0] == "_":
                    tmpDict[ key[1:] ] = tmpDict.pop(key)
            return tmpDict

        if isinstance(object, Pushbullet):
            return object.getJSONCompatibleDict()
        return json.JSONEncoder.default(self, object)
