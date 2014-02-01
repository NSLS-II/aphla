# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_launcher_restore_hierarchy.ui'
#
# Created: Wed Jan 29 18:48:13 2014
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
        Dialog.resize(400, 220)
        self.formLayout = QtGui.QFormLayout(Dialog)
        self.formLayout.setObjectName(_fromUtf8("formLayout"))
        self.label = QtGui.QLabel(Dialog)
        self.label.setWordWrap(True)
        self.label.setObjectName(_fromUtf8("label"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.SpanningRole, self.label)
        spacerItem = QtGui.QSpacerItem(373, 6, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.formLayout.setItem(1, QtGui.QFormLayout.FieldRole, spacerItem)
        self.label_2 = QtGui.QLabel(Dialog)
        self.label_2.setWordWrap(True)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.formLayout.setWidget(2, QtGui.QFormLayout.SpanningRole, self.label_2)
        spacerItem1 = QtGui.QSpacerItem(373, 6, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.formLayout.setItem(3, QtGui.QFormLayout.FieldRole, spacerItem1)
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.checkBox_backup = QtGui.QCheckBox(Dialog)
        self.checkBox_backup.setObjectName(_fromUtf8("checkBox_backup"))
        self.verticalLayout.addWidget(self.checkBox_backup)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.lineEdit_backup_filepath = QtGui.QLineEdit(Dialog)
        self.lineEdit_backup_filepath.setObjectName(_fromUtf8("lineEdit_backup_filepath"))
        self.horizontalLayout.addWidget(self.lineEdit_backup_filepath)
        self.pushButton_browse = QtGui.QPushButton(Dialog)
        self.pushButton_browse.setObjectName(_fromUtf8("pushButton_browse"))
        self.horizontalLayout.addWidget(self.pushButton_browse)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.formLayout.setLayout(4, QtGui.QFormLayout.SpanningRole, self.verticalLayout)
        self.buttonBox = QtGui.QDialogButtonBox(Dialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.No|QtGui.QDialogButtonBox.Yes)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.formLayout.setWidget(5, QtGui.QFormLayout.SpanningRole, self.buttonBox)

        self.retranslateUi(Dialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), Dialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QtGui.QApplication.translate("Dialog", "Dialog", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("Dialog", "Launcher has found a user hierarchy file temporarily saved in a previous session that was not gracefully terminated.", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("Dialog", "Would you like to restore this hierarchy?", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBox_backup.setText(QtGui.QApplication.translate("Dialog", "Backup current user hierarchy to:", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_browse.setText(QtGui.QApplication.translate("Dialog", "Browse...", None, QtGui.QApplication.UnicodeUTF8))

