# -*- coding: utf-8 -*-
from datetime import datetime


DEBUG_LEVEL = 1
LOG_TO_FILE = False
LOG_FILEPATH = ""


def getCurDateTimeString():
    return datetime.now().strftime("%d/%m/%y %H:%M:%S")


def getCurTimeString():
    return datetime.now().strftime("%H:%M")


def log(dbgLevel, logMsg):
    if dbgLevel <= DEBUG_LEVEL:
        if LOG_TO_FILE:
            pass
        else:
            print(getCurDateTimeString() + "\t" +
                  str(dbgLevel) + "\t" + "{}".format(logMsg))


def debugLog(logMsg):
    print(logMsg)


def func_monitor(func):
    def call():
        print("Entering function {}".format(func.__name__))
        func()
        print("Finished calling function")
    call.__name__ = func.__name__
    return call
