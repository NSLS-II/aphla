# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'current_monitor.ui'
#
# Created: Tue Oct  4 11:10:11 2011
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
        MainWindow.resize(800, 600)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.gridLayout = QtGui.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.qwtPlot = QwtPlot(self.centralwidget)
        self.qwtPlot.setObjectName(_fromUtf8("qwtPlot"))
        self.gridLayout.addWidget(self.qwtPlot, 0, 0, 1, 5)
        self.label = QtGui.QLabel(self.centralwidget)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 1, 0, 1, 1)
        self.label_current = QtGui.QLabel(self.centralwidget)
        self.label_current.setObjectName(_fromUtf8("label_current"))
        self.gridLayout.addWidget(self.label_current, 1, 1, 1, 1)
        spacerItem = QtGui.QSpacerItem(491, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 1, 2, 1, 1)
        self.pushButton_start = QtGui.QPushButton(self.centralwidget)
        self.pushButton_start.setObjectName(_fromUtf8("pushButton_start"))
        self.gridLayout.addWidget(self.pushButton_start, 1, 3, 1, 1)
        self.pushButton_stop = QtGui.QPushButton(self.centralwidget)
        self.pushButton_stop.setObjectName(_fromUtf8("pushButton_stop"))
        self.gridLayout.addWidget(self.pushButton_stop, 1, 4, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtGui.QStatusBar(MainWindow)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QtGui.QApplication.translate("MainWindow", "MainWindow", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("MainWindow", "Current [mA]: ", None, QtGui.QApplication.UnicodeUTF8))
        self.label_current.setText(QtGui.QApplication.translate("MainWindow", "N/A", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_start.setText(QtGui.QApplication.translate("MainWindow", "Start", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_stop.setText(QtGui.QApplication.translate("MainWindow", "Stop", None, QtGui.QApplication.UnicodeUTF8))

from PyQt4.Qwt5 import *
