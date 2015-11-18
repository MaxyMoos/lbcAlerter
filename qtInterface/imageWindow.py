# -*- coding: utf-8 -*-

from PyQt4.QtGui import *
from PyQt4.QtCore import *
from lbc_utils import *


class QImageNavButtons(QWidget):

    def __init__(self):
        super(QImageNavButtons, self).__init__()
        self._layout = QHBoxLayout()
        self._prevButton = QPushButton("Previous", self)
        self._nextButton = QPushButton("Next", self)
        self._layout.addWidget(self._prevButton)
        self._layout.addWidget(self._nextButton)
        self.setLayout(self._layout)


class QImageWindow(QDialog):
    closeWinEvent = pyqtSignal()

    def __init__(self, lbcItem, parent=None):
        super(QImageWindow, self).__init__(parent)
        self.displayedImgIndex = 0
        self._item = lbcItem

        # Set up widgets
        self._layout = QVBoxLayout()
        self._imageZone = QLabel()
        self.pixmapImg = QPixmap()
        self.imgIndexText = QLabel()
        self._navButtons = QImageNavButtons()
        self._prevBtn = self._navButtons._prevButton
        self._nextBtn = self._navButtons._nextButton

        # Connect signals/slots
        self._prevBtn.clicked.connect(lambda: self.showNextOrPrevImage(-1))
        self._nextBtn.clicked.connect(lambda: self.showNextOrPrevImage(1))
        self.closeWinEvent.connect(self.parentWidget().onImageDialogClosed)

        # Set up the pixmap by loading first available image
        images = self._item.getImagesAsJPEG()
        if len(images) > 0:
            self.pixmapImg.loadFromData(images[0])
            self.pixmapImg = self.pixmapImg.scaled(
                self._imageZone.size(), Qt.KeepAspectRatio)
            self._imageZone.setPixmap(self.pixmapImg)
        if len(images) == 1:
            # Disable next/previous buttons
            self._prevBtn.setEnabled(False)
            self._nextBtn.setEnabled(False)

        self.imgIndexText.setText(str(self.displayedImgIndex + 1) \
                                  + " / " \
                                  + str(len(self._item.images)))
        self.imgIndexText.setAlignment(Qt.AlignHCenter)
        self.resize(500, 500)
        self.setWindowTitle(self._item.title + " - Images")
        self._layout.addWidget(
            self._imageZone)
        self._layout.addWidget(self.imgIndexText)
        self._layout.addWidget(self._navButtons, Qt.AlignHCenter)
        self._layout.setAlignment(Qt.AlignHCenter)
        self.setLayout(self._layout)

    def setAndRefreshPixmapWithImage(self, imageData):
        self.pixmapImg.loadFromData(imageData)
        self._imageZone.setPixmap(self.pixmapImg)

    def showNextOrPrevImage(self, nextOrPrev):
        # nextOrPrev value is -1 or 1
        self.displayedImgIndex = (
            self.displayedImgIndex + nextOrPrev) % len(self._item.images)
        self.imgIndexText.setText(str(self.displayedImgIndex + 1) \
                                  + " / " \
                                  + str(len(self._item.images)))
        self.setAndRefreshPixmapWithImage(
            self._item.getImagesAsJPEG()[self.displayedImgIndex])

    def keyPressEvent(self, event):
        # WORKAROUND: [Win10] Esc closes the imageWindow *without*
        # calling closeEvent
        if event.key() != Qt.Key_Escape:
            super().keyPressEvent(event)


    def closeEvent(self, event):
        self.closeWinEvent.emit()
        event.accept()
