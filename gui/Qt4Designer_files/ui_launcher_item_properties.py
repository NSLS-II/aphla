# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_launcher_item_properties.ui'
#
# Created: Tue Mar  6 14:10:47 2012
#      by: PyQt4 UI code generator 4.8.3
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
        Dialog.resize(400, 300)
        self.gridLayout = QtGui.QGridLayout(Dialog)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.label = QtGui.QLabel(Dialog)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.lineEdit_dispName = QtGui.QLineEdit(Dialog)
        self.lineEdit_dispName.setObjectName(_fromUtf8("lineEdit_dispName"))
        self.gridLayout.addWidget(self.lineEdit_dispName, 0, 1, 1, 1)
        self.label_6 = QtGui.QLabel(Dialog)
        self.label_6.setObjectName(_fromUtf8("label_6"))
        self.gridLayout.addWidget(self.label_6, 1, 0, 1, 1)
        self.comboBox_itemType = QtGui.QComboBox(Dialog)
        self.comboBox_itemType.setObjectName(_fromUtf8("comboBox_itemType"))
        self.comboBox_itemType.addItem(_fromUtf8(""))
        self.comboBox_itemType.addItem(_fromUtf8(""))
        self.gridLayout.addWidget(self.comboBox_itemType, 1, 1, 1, 1)
        self.label_2 = QtGui.QLabel(Dialog)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout.addWidget(self.label_2, 2, 0, 1, 1)
        self.comboBox_linkedFile = QtGui.QComboBox(Dialog)
        self.comboBox_linkedFile.setEditable(True)
        self.comboBox_linkedFile.setObjectName(_fromUtf8("comboBox_linkedFile"))
        self.gridLayout.addWidget(self.comboBox_linkedFile, 2, 1, 1, 1)
        self.label_3 = QtGui.QLabel(Dialog)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.gridLayout.addWidget(self.label_3, 3, 0, 1, 1)
        self.lineEdit_args = QtGui.QLineEdit(Dialog)
        self.lineEdit_args.setObjectName(_fromUtf8("lineEdit_args"))
        self.gridLayout.addWidget(self.lineEdit_args, 3, 1, 1, 1)
        self.label_4 = QtGui.QLabel(Dialog)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.gridLayout.addWidget(self.label_4, 4, 0, 1, 1)
        self.comboBox_useImport = QtGui.QComboBox(Dialog)
        self.comboBox_useImport.setObjectName(_fromUtf8("comboBox_useImport"))
        self.comboBox_useImport.addItem(_fromUtf8(""))
        self.comboBox_useImport.addItem(_fromUtf8(""))
        self.gridLayout.addWidget(self.comboBox_useImport, 4, 1, 1, 1)
        self.label_5 = QtGui.QLabel(Dialog)
        self.label_5.setObjectName(_fromUtf8("label_5"))
        self.gridLayout.addWidget(self.label_5, 5, 0, 1, 1)
        self.comboBox_singleton = QtGui.QComboBox(Dialog)
        self.comboBox_singleton.setObjectName(_fromUtf8("comboBox_singleton"))
        self.comboBox_singleton.addItem(_fromUtf8(""))
        self.comboBox_singleton.addItem(_fromUtf8(""))
        self.gridLayout.addWidget(self.comboBox_singleton, 5, 1, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(Dialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 6, 0, 1, 2)

        self.retranslateUi(Dialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), Dialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QtGui.QApplication.translate("Dialog", "Properties", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("Dialog", "Name", None, QtGui.QApplication.UnicodeUTF8))
        self.label_6.setText(QtGui.QApplication.translate("Dialog", "Item Type", None, QtGui.QApplication.UnicodeUTF8))
        self.comboBox_itemType.setItemText(0, QtGui.QApplication.translate("Dialog", "Page", None, QtGui.QApplication.UnicodeUTF8))
        self.comboBox_itemType.setItemText(1, QtGui.QApplication.translate("Dialog", "App", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("Dialog", "Linked File Name", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("Dialog", "Arguments", None, QtGui.QApplication.UnicodeUTF8))
        self.label_4.setText(QtGui.QApplication.translate("Dialog", "Use Import", None, QtGui.QApplication.UnicodeUTF8))
        self.comboBox_useImport.setItemText(0, QtGui.QApplication.translate("Dialog", "True", None, QtGui.QApplication.UnicodeUTF8))
        self.comboBox_useImport.setItemText(1, QtGui.QApplication.translate("Dialog", "False", None, QtGui.QApplication.UnicodeUTF8))
        self.label_5.setText(QtGui.QApplication.translate("Dialog", "Singleton", None, QtGui.QApplication.UnicodeUTF8))
        self.comboBox_singleton.setItemText(0, QtGui.QApplication.translate("Dialog", "True", None, QtGui.QApplication.UnicodeUTF8))
        self.comboBox_singleton.setItemText(1, QtGui.QApplication.translate("Dialog", "False", None, QtGui.QApplication.UnicodeUTF8))

