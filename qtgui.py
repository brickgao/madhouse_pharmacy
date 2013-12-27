# -*- coding: utf-8 -*-

import sys
from PyQt4 import QtGui, QtWebKit, QtCore
import os

class mainWindow(QtGui.QMainWindow):

    def __init__(self):

        super(mainWindow, self).__init__()
        self.initLayout()

    def initLayout(self):

        self.webView = QtWebKit.QWebView()
        self.urlString = 'http://localhost:5000'
        self.url = QtCore.QUrl()
        self.url.setUrl(self.urlString)
        self.webView.setContextMenuPolicy(QtCore.Qt.NoContextMenu)
        self.webView.load(self.url)
        self.setCentralWidget(self.webView)
        self.setGeometry(100, 100, 600, 500)
        self.setMinimumSize(600, 500)
        self.setMaximumSize(600, 500)
        self.setWindowTitle(u'Madhouse Card System')
        self.show()

def run():

    app = QtGui.QApplication(sys.argv)
    ex = mainWindow()
    sys.exit(app.exec_())


        
