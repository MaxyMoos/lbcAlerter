# -*- coding: utf-8 -*-
from PyQt4.QtGui import *
from PyQt4.QtCore import *


# QT utilities
class SearchLineEdit(QLineEdit):
    keyEnterPressed = pyqtSignal()

    def keyPressEvent(self, event):
        super(SearchLineEdit, self).keyPressEvent(event)
        if ( event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter):
            self.keyEnterPressed.emit()
