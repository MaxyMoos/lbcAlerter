# -*- coding: utf-8 -*-

from PyQt4.QtGui import *
from PyQt4.QtCore import *
from lbc_utils import *


class QImageWindow(QDialog):
    def __init__(self, lbcItem):
        super(QImageWindow, self).__init__()
        self._item      =   lbcItem
        self._layout    =   QHBoxLayout()
        self._imageZone =   QLabel()
        self.pixmapImg  =   QPixmap()
        self.pixmapImg.loadFromData( self._item.getImages()[0] )
        self.pixmapImg  =   self.pixmapImg.scaled(self._imageZone.size(), Qt.KeepAspectRatio)
        self._imageZone.setPixmap(self.pixmapImg)

        self.resize(500,500)
        self._layout.addWidget(self._imageZone, Qt.AlignHCenter | Qt.AlignVCenter)
        self.setLayout(self._layout)
