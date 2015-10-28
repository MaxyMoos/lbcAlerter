from datetime import datetime


def getCurDateTimeString():
    return datetime.now().strftime("%A, %d. %B %Y %I:%M%p")
