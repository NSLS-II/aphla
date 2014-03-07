# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_tinkerConfigSetupPref.ui'
#
# Created: Fri Feb 28 22:48:12 2014
#      by: PyQt4 UI code generator 4.9.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName(_fromUtf8("Dialog"))
        Dialog.resize(344, 291)
        self.gridLayout = QtGui.QGridLayout(Dialog)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.label_2 = QtGui.QLabel(Dialog)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout.addWidget(self.label_2, 0, 0, 1, 1)
        self.listWidget_visible_columns = QtGui.QListWidget(Dialog)
        self.listWidget_visible_columns.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.listWidget_visible_columns.setAlternatingRowColors(True)
        self.listWidget_visible_columns.setSelectionMode(QtGui.QAbstractItemView.NoSelection)
        self.listWidget_visible_columns.setResizeMode(QtGui.QListView.Adjust)
        self.listWidget_visible_columns.setObjectName(_fromUtf8("listWidget_visible_columns"))
        self.gridLayout.addWidget(self.listWidget_visible_columns, 0, 1, 3, 2)
        self.pushButton_edit_visible_columns = QtGui.QPushButton(Dialog)
        self.pushButton_edit_visible_columns.setMaximumSize(QtCore.QSize(61, 16777215))
        self.pushButton_edit_visible_columns.setObjectName(_fromUtf8("pushButton_edit_visible_columns"))
        self.gridLayout.addWidget(self.pushButton_edit_visible_columns, 0, 3, 2, 1)
        spacerItem = QtGui.QSpacerItem(20, 192, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 1, 0, 2, 1)
        spacerItem1 = QtGui.QSpacerItem(20, 177, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem1, 2, 3, 1, 1)
        self.horizontalLayout_6 = QtGui.QHBoxLayout()
        self.horizontalLayout_6.setObjectName(_fromUtf8("horizontalLayout_6"))
        self.pushButton_restore_default = QtGui.QPushButton(Dialog)
        self.pushButton_restore_default.setObjectName(_fromUtf8("pushButton_restore_default"))
        self.horizontalLayout_6.addWidget(self.pushButton_restore_default)
        spacerItem2 = QtGui.QSpacerItem(92, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_6.addItem(spacerItem2)
        self.buttonBox = QtGui.QDialogButtonBox(Dialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.horizontalLayout_6.addWidget(self.buttonBox)
        self.gridLayout.addLayout(self.horizontalLayout_6, 3, 0, 1, 4)

        self.retranslateUi(Dialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), Dialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QtGui.QApplication.translate("Dialog", "Startup Preferences", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("Dialog", "Visible Columns", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_edit_visible_columns.setText(QtGui.QApplication.translate("Dialog", "Edit", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_restore_default.setText(QtGui.QApplication.translate("Dialog", "Restore Default", None, QtGui.QApplication.UnicodeUTF8))

