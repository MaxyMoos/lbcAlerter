# -*- coding: utf-8 -*-
from datetime import date, timedelta
import base64


class lbc_item():
    def __init__(self, itemId=-1, title="", price=None, date=-1, url="", images=[]):
        self.id = itemId
        self.title = title
        if price is None:
            self.price = "Pas de prix indiqué"
        else:
            self.price = price
        self.date = date
        self.url = url
        self.images = images

    def __str__(self):
        return self.title + " / " + str(self.id)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.url == other.url
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def get_date_string(self):
        itemDate = date(self.date.year, self.date.month, self.date.day)
        if ( itemDate == date.today() ):
            return "Aujourd'hui, " + self.date.strftime("%H:%M")
        elif ( itemDate == date.today() - timedelta(days=1) ):
            return "Hier, " + self.date.strftime("%H:%M")
        else:
            return self.date.strftime("%A %d %B %Y, %H:%M")

    def getId(self):
        return self.id

    def getTitle(self):
        return self.title

    def getPrice(self):
        return self.price

    def getDate(self):
        return self.date

    def getURL(self):
        return self.url

    def getImagesAsJPEG(self):
        return [base64.b16decode(x) for x in self.images]
