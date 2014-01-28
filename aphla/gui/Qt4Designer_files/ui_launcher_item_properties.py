# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_launcher_item_properties.ui'
#
# Created: Tue Jan 28 17:15:01 2014
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
        Dialog.resize(413, 429)
        self.gridLayout = QtGui.QGridLayout(Dialog)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.label_7 = QtGui.QLabel(Dialog)
        self.label_7.setObjectName(_fromUtf8("label_7"))
        self.gridLayout.addWidget(self.label_7, 0, 0, 1, 1)
        self.lineEdit_parentPath = QtGui.QLineEdit(Dialog)
        self.lineEdit_parentPath.setEnabled(True)
        self.lineEdit_parentPath.setReadOnly(True)
        self.lineEdit_parentPath.setObjectName(_fromUtf8("lineEdit_parentPath"))
        self.gridLayout.addWidget(self.lineEdit_parentPath, 0, 1, 1, 1)
        self.label = QtGui.QLabel(Dialog)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 1, 0, 1, 1)
        self.lineEdit_dispName = QtGui.QLineEdit(Dialog)
        self.lineEdit_dispName.setObjectName(_fromUtf8("lineEdit_dispName"))
        self.gridLayout.addWidget(self.lineEdit_dispName, 1, 1, 1, 1)
        self.label_6 = QtGui.QLabel(Dialog)
        self.label_6.setObjectName(_fromUtf8("label_6"))
        self.gridLayout.addWidget(self.label_6, 2, 0, 1, 1)
        self.comboBox_itemType = QtGui.QComboBox(Dialog)
        self.comboBox_itemType.setObjectName(_fromUtf8("comboBox_itemType"))
        self.comboBox_itemType.addItem(_fromUtf8(""))
        self.comboBox_itemType.addItem(_fromUtf8(""))
        self.comboBox_itemType.addItem(_fromUtf8(""))
        self.gridLayout.addWidget(self.comboBox_itemType, 2, 1, 1, 1)
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.label_2 = QtGui.QLabel(Dialog)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.verticalLayout.addWidget(self.label_2)
        self.label_5 = QtGui.QLabel(Dialog)
        self.label_5.setObjectName(_fromUtf8("label_5"))
        self.verticalLayout.addWidget(self.label_5)
        self.gridLayout.addLayout(self.verticalLayout, 3, 0, 1, 1)
        self.comboBox_command = QtGui.QComboBox(Dialog)
        self.comboBox_command.setEnabled(False)
        self.comboBox_command.setEditable(True)
        self.comboBox_command.setObjectName(_fromUtf8("comboBox_command"))
        self.gridLayout.addWidget(self.comboBox_command, 3, 1, 1, 1)
        self.label_4 = QtGui.QLabel(Dialog)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.gridLayout.addWidget(self.label_4, 4, 0, 1, 1)
        self.comboBox_useImport = QtGui.QComboBox(Dialog)
        self.comboBox_useImport.setEnabled(False)
        self.comboBox_useImport.setObjectName(_fromUtf8("comboBox_useImport"))
        self.comboBox_useImport.addItem(_fromUtf8(""))
        self.comboBox_useImport.addItem(_fromUtf8(""))
        self.gridLayout.addWidget(self.comboBox_useImport, 4, 1, 1, 1)
        self.label_3 = QtGui.QLabel(Dialog)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.gridLayout.addWidget(self.label_3, 5, 0, 1, 1)
        self.lineEdit_importArgs = QtGui.QLineEdit(Dialog)
        self.lineEdit_importArgs.setEnabled(False)
        self.lineEdit_importArgs.setObjectName(_fromUtf8("lineEdit_importArgs"))
        self.gridLayout.addWidget(self.lineEdit_importArgs, 5, 1, 1, 1)
        self.label_8 = QtGui.QLabel(Dialog)
        self.label_8.setObjectName(_fromUtf8("label_8"))
        self.gridLayout.addWidget(self.label_8, 6, 0, 1, 1)
        self.plainTextEdit_description = QtGui.QPlainTextEdit(Dialog)
        self.plainTextEdit_description.setMinimumSize(QtCore.QSize(0, 71))
        self.plainTextEdit_description.setObjectName(_fromUtf8("plainTextEdit_description"))
        self.gridLayout.addWidget(self.plainTextEdit_description, 6, 1, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(Dialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 7, 0, 1, 2)

        self.retranslateUi(Dialog)
        self.comboBox_useImport.setCurrentIndex(1)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), Dialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QtGui.QApplication.translate("Dialog", "Properties", None, QtGui.QApplication.UnicodeUTF8))
        self.label_7.setText(QtGui.QApplication.translate("Dialog", "Parent Path", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("Dialog", "Name", None, QtGui.QApplication.UnicodeUTF8))
        self.label_6.setText(QtGui.QApplication.translate("Dialog", "Item Type", None, QtGui.QApplication.UnicodeUTF8))
        self.comboBox_itemType.setItemText(0, QtGui.QApplication.translate("Dialog", "Page", None, QtGui.QApplication.UnicodeUTF8))
        self.comboBox_itemType.setItemText(1, QtGui.QApplication.translate("Dialog", "App", None, QtGui.QApplication.UnicodeUTF8))
        self.comboBox_itemType.setItemText(2, QtGui.QApplication.translate("Dialog", "Library", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("Dialog", "Command /", None, QtGui.QApplication.UnicodeUTF8))
        self.label_5.setText(QtGui.QApplication.translate("Dialog", "Py Module Name", None, QtGui.QApplication.UnicodeUTF8))
        self.label_4.setText(QtGui.QApplication.translate("Dialog", "Use Import", None, QtGui.QApplication.UnicodeUTF8))
        self.comboBox_useImport.setItemText(0, QtGui.QApplication.translate("Dialog", "True", None, QtGui.QApplication.UnicodeUTF8))
        self.comboBox_useImport.setItemText(1, QtGui.QApplication.translate("Dialog", "False", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("Dialog", "Import Arguments", None, QtGui.QApplication.UnicodeUTF8))
        self.label_8.setText(QtGui.QApplication.translate("Dialog", "Description", None, QtGui.QApplication.UnicodeUTF8))

