# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'launcher.ui'
#
# Created: Wed Oct  5 19:57:52 2011
#      by: PyQt4 UI code generator 4.8.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName(_fromUtf8("MainWindow"))
        MainWindow.resize(523, 266)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.pushButton_01 = QtGui.QPushButton(self.centralwidget)
        self.pushButton_01.setGeometry(QtCore.QRect(80, 90, 121, 27))
        self.pushButton_01.setObjectName(_fromUtf8("pushButton_01"))
        self.pushButton_02 = QtGui.QPushButton(self.centralwidget)
        self.pushButton_02.setGeometry(QtCore.QRect(280, 90, 121, 27))
        self.pushButton_02.setObjectName(_fromUtf8("pushButton_02"))
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtGui.QStatusBar(MainWindow)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QtGui.QApplication.translate("MainWindow", "MainWindow", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_01.setText(QtGui.QApplication.translate("MainWindow", "Current Monitor 1", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_02.setText(QtGui.QApplication.translate("MainWindow", "Current Monitor 2", None, QtGui.QApplication.UnicodeUTF8))

