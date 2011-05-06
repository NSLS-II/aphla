#!/usr/bin/env python

#from __future__ import division
#from __future__ import print_function
#from __future__ import unicode_literals
#from future_builtins import *

from PyQt4.QtCore import (Qt, SIGNAL, SLOT)
from PyQt4.QtGui import (QCheckBox, QDialog, QDialogButtonBox,
        QTableWidget, QTableWidgetItem,
        QGridLayout, QLabel, QLineEdit, QMessageBox, QSpinBox)

from fnmatch import fnmatch

class BpmTableDlg(QDialog):

    def __init__(self, bpm, parent=None):
        super(BpmTableDlg, self).__init__(parent)
        self.setAttribute(Qt.WA_DeleteOnClose)
        
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setRowCount(len(bpm))
        self.mask = [0]*len(bpm)
        self.bpm = bpm[:]
        
        self.bpmInputLabel = QLabel("BPM:")
        self.bpmInputEdit = QLineEdit("")

        buttonBox = QDialogButtonBox(QDialogButtonBox.Apply|
                                     QDialogButtonBox.Close)
        layout = QGridLayout()
        layout.addWidget(self.bpmInputLabel, 0, 0)
        layout.addWidget(self.bpmInputEdit, 0, 1)
        layout.addWidget(self.table, 1, 0, 1, 2)
        layout.addWidget(buttonBox, 2, 0, 1,2)
        self.setLayout(layout)

        self.live = []
        self.dead = []
        self.refresh()
        
        self.connect(buttonBox.button(QDialogButtonBox.Apply),
                     SIGNAL("clicked()"), self.apply)
        self.connect(buttonBox.button(QDialogButtonBox.Close),
                     SIGNAL("clicked()"), self.close)
        
        self.connect(self.bpmInputEdit, SIGNAL("textEdited(QString)"),
                     self.filter)
        self.connect(self.table, SIGNAL("cellClicked(int,int)"), self.savebpm)

    def savebpm(self, row, col):
        b = str(self.table.item(row, col).text())
        if not b in self.dead:
            print "Click",b
            self.dead.append(b)

        print self.dead
        
    def apply(self):
        for i in range(self.table.rowCount()):
            if self.table.item(i,0).isSelected():
                self.dead.append(str(self.table.item(i,0).text()))
                
        print "Applied"
        
    def refresh(self):
        self.table.clear()
        self.table.setRowCount(len(self.mask) - sum(self.mask))
        k = 0
        for i,b in enumerate(self.bpm):
            if self.mask[i]: continue
            item = QTableWidgetItem(b[0])
            self.table.setItem(k, 0, item)
            item = QTableWidgetItem("%.3f" % b[1])
            self.table.setItem(k, 1, item)
            k = k + 1
        
    def filter(self):
        s = str(self.bpmInputEdit.text()) + '*'
        print "Changed", s, 
        for i,b in enumerate(self.bpm):
            if b[0].startswith(s) or fnmatch(b[0], s):
                self.mask[i] = 0
            else:
                self.mask[i] = 1
            print self.mask[i],
        print ""
        self.refresh()
        
