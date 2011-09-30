#!/usr/bin/env

from cothread.catools import caput, caget

from PyQt4.QtCore import (PYQT_VERSION_STR, QFile, QFileInfo, QSettings,
        QObject, QString, QT_VERSION_STR, QTimer, QVariant, Qt, SIGNAL,
        QSize, QRectF)
from PyQt4.QtGui import (QAction, QActionGroup, QApplication, QWidget,
        QDockWidget, QFileDialog, QFrame, QIcon, QImage, QImageReader,
        QImageWriter, QInputDialog, QKeySequence, QLabel, QListWidget,
        QMainWindow, QMessageBox, QPainter, QPixmap, QPrintDialog,
        QPrinter, QDoubleSpinBox, QPen, QBrush, QVBoxLayout, QTabWidget,
        QTableWidget, QTableWidgetItem, QDialog, QHBoxLayout, 
        QDialogButtonBox, QGridLayout, QItemDelegate, QStandardItemModel, 
        QPushButton, QLineEdit, QTableView)

import hla


class PvTunerDlg(QDialog):
    def __init__(self, parent=None):  
        super(PvTunerDlg, self).__init__(parent)

        #self.inputBox = QLineEdit("PL2G2C01A.x")
        self.inputBox = QLineEdit("CXH2G6C01B.x")

        addPvBtn = QPushButton("add")

        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(["Element", "Field", "PV",
                 "Stepsize", "Readback", "setpoint"])
        #self.table.horizontalHeader().setStretchLastSection(True)
        
        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok)

        box = QGridLayout()
        box.addWidget(self.inputBox, 0, 0)
        box.addWidget(addPvBtn, 0, 1)
        box.addWidget(self.table, 1, 0, 1, 2)
        box.addWidget(buttonBox, 2, 0)

        self.setLayout(box)

        self.pvs_rb = []
        self.pvs_sp = []
        self.spinbox = []
        self.connect(addPvBtn, SIGNAL("clicked()"), self.addPv)
        self.connect(buttonBox, SIGNAL("accepted()"), self.accept)
        self.connect(self.table, SIGNAL("cellChanged"), self.updatePv)

    def updatePv(self, row, column):
        print row, column

    def addPv(self):
        vec = str(self.inputBox.text()).split('.')
        if len(vec) > 2:
            QMessageBox.critical(None, "ERROR", "format is wrong")
            return

        if len(vec) == 1:
            elem, field = vec[0], 'value'
        elif len(vec) == 2:
            elem, field = vec

        elemobj = hla.getElements(elem)
        if elemobj:
            pvsrb = elemobj.pv(field=field, handle='readback')
            self.pvs_rb.append(pvsrb)
            pvssp = elemobj.pv(field=field, handle='setpoint')
            self.pvs_sp.append(pvssp)
        else:
            QMessageBox.critical(None, "ERROR", "element %s not found" % elem)
            return

        item = QTableWidgetItem(elem)
        m, n = self.table.rowCount(), self.table.columnCount()
        self.table.insertRow(m)
        self.table.setItem(m, 0, item)
        
        item = QTableWidgetItem(field)
        self.table.setItem(m, 1, item)

        
        item = QTableWidgetItem(', '.join(pvsrb))
        self.table.setItem(m, 2, item)

        readval = ['%.4e' % v for v in caget(pvsrb)]
        item = QTableWidgetItem(', '.join(readval))
        self.table.setItem(m, 4, item)

        # set the stepsize of PV
        stepsize = 0.0001
        if pvssp:
            item = QTableWidgetItem('%f' % stepsize)
            self.table.setItem(m, 3, item)

            self.spinbox.append(QDoubleSpinBox(self.table))
            self.spinbox[-1].setValue(caget(pvssp[0]))
            self.spinbox[-1].setRange(-100, 100)
            self.spinbox[-1].setSingleStep(stepsize)
            self.spinbox[-1].setDecimals(10)
            self.table.setCellWidget(m, 5, self.spinbox[-1])
            #self.connect(self.spinbox[-1], SIGNAL("valueChanged(double)"),
            #             self.writePv)
            print "connected"
        else:
            self.spinbox.append(None)

        self.table.resizeColumnsToContents()
        pass

    def minimalSizeHint(self):
        return QSize(800, 600)


    def writePv(self, v):
        c = self.table.currentItem()
        #print c.text()
        print "changed"

if __name__ == "__main__":
    import sys
    hla.machines.initNSLS2VSRTxt()
    print "Good !"

    app = QApplication(sys.argv)
    form = PvTunerDlg()
    form.resize(800, 600)
    form.show()
    app.exec_()

    print "selected: ", form.result()

