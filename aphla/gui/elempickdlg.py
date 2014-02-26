#!/usr/bin/env python

"""
:author: Lingyun Yang <lyyang@bnl.gov>

A dialog for picking elements.
"""
# Copyright (c) 2011 Lingyun Yang @ BNL.

from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import (Qt, SIGNAL)


class ElementPickDlg(QtGui.QDialog):

    def __init__(self, allelems, parent=None, **kwargs):
        """elemobj"""
        super(ElementPickDlg, self).__init__(parent)
        title  = kwargs.get("title", 'Choose Elements:')
        extra_cols = kwargs.get("extra_cols", [])
        self.setWindowTitle(title)
        self.elemlst = QtGui.QTreeWidget()
        # enable multi-selection
        self.elemlst.setHeaderLabels(["Name"] + [v[0] for v in extra_cols])
        for i,row in enumerate(allelems):
            name, status = row
            w = QtGui.QTreeWidgetItem()
            w.setFlags(w.flags() | Qt.ItemIsUserCheckable)
            w.setText(0, name)
            for j,c in enumerate(extra_cols):
                w.setText(j+1, str(c[1][i]))
            w.setCheckState(0, status)
            self.elemlst.addTopLevelItem(w)
        #self.elemlst.setSortingEnabled(True)
        
        elemLabel = QtGui.QLabel(title)

        buttonBox = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Ok|
                                           QtGui.QDialogButtonBox.Cancel)

        btnAll  = QtGui.QPushButton("Select All")
        btnNone = QtGui.QPushButton("Select None")
        btnInv  = QtGui.QPushButton("Invert Selection")
        hbox = QtGui.QHBoxLayout()
        hbox.addWidget(btnAll)
        hbox.addWidget(btnNone)
        hbox.addWidget(btnInv)
        hbox.addStretch()

        layout = QtGui.QGridLayout()
        layout.addWidget(elemLabel, 0, 0)
        layout.addWidget(self.elemlst, 1, 0)
        layout.addLayout(hbox, 2, 0)
        layout.addWidget(buttonBox, 3, 0)
        self.setLayout(layout)

        self.connect(btnAll, SIGNAL("clicked()"), self._sel_all)
        self.connect(btnNone, SIGNAL("clicked()"), self._sel_none)
        self.connect(btnInv, SIGNAL("clicked()"), self._sel_inv)

        self.connect(buttonBox, SIGNAL("accepted()"), self.accept)
        self.connect(buttonBox, SIGNAL("rejected()"), self.reject)

    def _sel_all(self):
        for i in range(self.elemlst.topLevelItemCount()):
            it = self.elemlst.topLevelItem(i)
            it.setCheckState(0, Qt.Checked)

    def _sel_none(self):
        for i in range(self.elemlst.topLevelItemCount()):
            it = self.elemlst.topLevelItem(i)
            it.setCheckState(0, Qt.Unchecked)

    def _sel_inv(self):
        for i in range(self.elemlst.topLevelItemCount()):
            it = self.elemlst.topLevelItem(i)
            if it.checkState(0) == Qt.Checked:
                it.setCheckState(0, Qt.Unchecked)
            elif it.checkState(0) == Qt.Unchecked:
                it.setCheckState(0, Qt.Checked)

    def checkStates(self):
        #print self.elemlst.selectedItems()
        ret = []
        for i in range(self.elemlst.topLevelItemCount()):
            it = self.elemlst.topLevelItem(i)
            ret.append(it.checkState(0))
        return ret

    def checkedNames(self):
        ret = []
        for i in range(self.elemlst.topLevelItemCount()):
            it = self.elemlst.topLevelItem(i)
            if it.checkState(0) != Qt.Checked: continue
            ret.append(str(it.data(0, Qt.DisplayRole).toString()))
        return ret
    
    def checkedIndices(self):
        return [ i for i in range(self.elemlst.topLevelItemCount())
                 if self.elemlst.topLevelItem(i).checkState(0) == Qt.Checked]
        

if __name__ == "__main__":
    import sys

    app = QtGui.QApplication(sys.argv)
    form = ElementPickDlg([('elem 1', Qt.Unchecked), ('elem 2', Qt.Checked)],
                          extra_cols=[("s", [0, 1])])
    form.show()
    app.exec_()

    print "selected: ", form.checkedNames()
    print "selected: ", form.checkedIndices()
