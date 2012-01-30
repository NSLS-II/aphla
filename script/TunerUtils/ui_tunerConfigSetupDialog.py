# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_tunerConfigSetupDialog.ui'
#
# Created: Mon Nov  7 14:09:07 2011
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
        Dialog.resize(904, 762)
        self.buttonBox = QtGui.QDialogButtonBox(Dialog)
        self.buttonBox.setGeometry(QtCore.QRect(720, 730, 181, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.groupBox_switch_view = QtGui.QGroupBox(Dialog)
        self.groupBox_switch_view.setGeometry(QtCore.QRect(10, 640, 161, 41))
        self.groupBox_switch_view.setObjectName(_fromUtf8("groupBox_switch_view"))
        self.radioButton_knob_groups = QtGui.QRadioButton(self.groupBox_switch_view)
        self.radioButton_knob_groups.setGeometry(QtCore.QRect(0, 20, 101, 21))
        self.radioButton_knob_groups.setChecked(True)
        self.radioButton_knob_groups.setObjectName(_fromUtf8("radioButton_knob_groups"))
        self.buttonGroup = QtGui.QButtonGroup(Dialog)
        self.buttonGroup.setObjectName(_fromUtf8("buttonGroup"))
        self.buttonGroup.addButton(self.radioButton_knob_groups)
        self.radioButton_knobs = QtGui.QRadioButton(self.groupBox_switch_view)
        self.radioButton_knobs.setGeometry(QtCore.QRect(100, 20, 61, 21))
        self.radioButton_knobs.setObjectName(_fromUtf8("radioButton_knobs"))
        self.buttonGroup.addButton(self.radioButton_knobs)
        self.treeView = QtGui.QTreeView(Dialog)
        self.treeView.setGeometry(QtCore.QRect(10, 10, 881, 621))
        self.treeView.setAlternatingRowColors(True)
        self.treeView.setObjectName(_fromUtf8("treeView"))
        self.pushButton_add_from_file = QtGui.QPushButton(Dialog)
        self.pushButton_add_from_file.setGeometry(QtCore.QRect(12, 686, 101, 27))
        self.pushButton_add_from_file.setObjectName(_fromUtf8("pushButton_add_from_file"))
        self.pushButton_add_from_selector_GUI = QtGui.QPushButton(Dialog)
        self.pushButton_add_from_selector_GUI.setGeometry(QtCore.QRect(120, 686, 141, 27))
        self.pushButton_add_from_selector_GUI.setObjectName(_fromUtf8("pushButton_add_from_selector_GUI"))
        self.label = QtGui.QLabel(Dialog)
        self.label.setGeometry(QtCore.QRect(720, 660, 121, 16))
        self.label.setObjectName(_fromUtf8("label"))
        self.lineEdit_config_name = QtGui.QLineEdit(Dialog)
        self.lineEdit_config_name.setGeometry(QtCore.QRect(720, 680, 181, 25))
        self.lineEdit_config_name.setObjectName(_fromUtf8("lineEdit_config_name"))
        self.label_2 = QtGui.QLabel(Dialog)
        self.label_2.setGeometry(QtCore.QRect(280, 660, 151, 16))
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.textEdit_config_description = QtGui.QTextEdit(Dialog)
        self.textEdit_config_description.setGeometry(QtCore.QRect(280, 680, 431, 81))
        self.textEdit_config_description.setObjectName(_fromUtf8("textEdit_config_description"))
        self.checkBox_save_to_file = QtGui.QCheckBox(Dialog)
        self.checkBox_save_to_file.setGeometry(QtCore.QRect(720, 709, 121, 21))
        self.checkBox_save_to_file.setObjectName(_fromUtf8("checkBox_save_to_file"))
        self.pushButton_remove_duplicates = QtGui.QPushButton(Dialog)
        self.pushButton_remove_duplicates.setGeometry(QtCore.QRect(12, 725, 121, 27))
        self.pushButton_remove_duplicates.setObjectName(_fromUtf8("pushButton_remove_duplicates"))
        self.pushButton_preferences = QtGui.QPushButton(Dialog)
        self.pushButton_preferences.setGeometry(QtCore.QRect(173, 725, 91, 27))
        self.pushButton_preferences.setObjectName(_fromUtf8("pushButton_preferences"))

        self.retranslateUi(Dialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), Dialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QtGui.QApplication.translate("Dialog", "Dialog", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_switch_view.setTitle(QtGui.QApplication.translate("Dialog", "View based on", None, QtGui.QApplication.UnicodeUTF8))
        self.radioButton_knob_groups.setText(QtGui.QApplication.translate("Dialog", "Knob Groups", None, QtGui.QApplication.UnicodeUTF8))
        self.radioButton_knobs.setText(QtGui.QApplication.translate("Dialog", "Knobs", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_add_from_file.setText(QtGui.QApplication.translate("Dialog", "Add from file...", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_add_from_selector_GUI.setText(QtGui.QApplication.translate("Dialog", "Add from Selector GUI", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("Dialog", "Configuration Name:", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("Dialog", "Configuration Description:", None, QtGui.QApplication.UnicodeUTF8))
        self.textEdit_config_description.setHtml(QtGui.QApplication.translate("Dialog", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Ubuntu\'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"></p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBox_save_to_file.setText(QtGui.QApplication.translate("Dialog", "Save also to file", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_remove_duplicates.setText(QtGui.QApplication.translate("Dialog", "Remove Duplicates", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_preferences.setText(QtGui.QApplication.translate("Dialog", "Preferences", None, QtGui.QApplication.UnicodeUTF8))

