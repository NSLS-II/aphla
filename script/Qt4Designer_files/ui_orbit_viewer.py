# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_orbit_viewer.ui'
#
# Created: Tue Nov  8 11:14:15 2011
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
        self.qwtPlot_x = QwtPlot(self.centralwidget)
        self.qwtPlot_x.setObjectName(_fromUtf8("qwtPlot_x"))
        self.gridLayout.addWidget(self.qwtPlot_x, 0, 0, 1, 2)
        self.qwtPlot_y = QwtPlot(self.centralwidget)
        self.qwtPlot_y.setObjectName(_fromUtf8("qwtPlot_y"))
        self.gridLayout.addWidget(self.qwtPlot_y, 1, 0, 1, 2)
        spacerItem = QtGui.QSpacerItem(491, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 2, 0, 1, 1)
        self.pushButton_update = QtGui.QPushButton(self.centralwidget)
        self.pushButton_update.setObjectName(_fromUtf8("pushButton_update"))
        self.gridLayout.addWidget(self.pushButton_update, 2, 1, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtGui.QStatusBar(MainWindow)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QtGui.QApplication.translate("MainWindow", "Orbit Viewer", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_update.setText(QtGui.QApplication.translate("MainWindow", "Update", None, QtGui.QApplication.UnicodeUTF8))

from PyQt4.Qwt5 import *
