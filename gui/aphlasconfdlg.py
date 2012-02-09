#!/usr/bin/env python

import sys

from PyQt4.QtCore import QSize, SIGNAL, Qt
from PyQt4.QtGui import (QDialog, QAction, QActionGroup, QVBoxLayout, 
    QWidget, QTabWidget, QLabel, QIcon, QApplication, QImage, QPixmap,
    QSizePolicy, QFileDialog, QTableWidget, QHBoxLayout, QTableWidgetItem,
    QHeaderView)

class ApHlasConfDlg(QDialog):
    def __init__(self, width, height, parent = None):
        super(ApHlasConfDlg, self).__init__(parent)
        
        table1 = QTableWidget(5, 5)
        table1.connect(table1, SIGNAL("cellActivated(int, int)"), self.showTags)
        table1.connect(table1, SIGNAL("cellClicked(int, int)"), self.showTags)
        it1 = QTableWidgetItem("Hello")
        table1.setItem(0, 0, it1)

        hdview = QHeaderView(Qt.Horizontal)
        hdview.setStretchLastSection(True)
        self.tagsTable = QTableWidget(5,1)
        self.tagsTable.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        self.tagsTable.setHorizontalHeader(hdview)
        self.tagsTable.setHorizontalHeaderLabels(['tags'])
        l = QHBoxLayout(self)
        l.addWidget(table1)
        l.addWidget(self.tagsTable)

    def showTags(self, row, col):
        for i in range(3):
            print i
            it = self.tagsTable.item(i, 0)
            if it is None: 
                print "New an item at ", i, 0
                it = QTableWidgetItem("tags: %d (%d,%d)" % (i, row, col))
                self.tagsTable.setItem(i, 0, it)
            else:
                print "Existing item", i, 0
                it.setText("this is a very long tags: %d (%d,%d)" % (i, row, col))
        #self.tagsTable.resizeColumnsToContents()


    
if __name__ == "__main__":
    app = QApplication(sys.argv)
    dlg = ApHlasConfDlg(640, 480)
    dlg.show()
    app.exec_()


