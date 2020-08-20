#!/usr/bin/env
from __future__ import print_function, division, absolute_import

import cothread
from cothread.catools import caput, caget, camonitor
app = cothread.iqt()

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
        QPushButton, QLineEdit, QTableView, QAbstractItemView)


class PvTunerDlg(QDialog):
    COL = 6
    COL_ELEMENT  = 0
    COL_FIELD    = 1
    COL_PV       = 2
    COL_STEPSIZE = 3
    COL_READBACK = 4
    COL_SETPOINT = 5
    FMT_READBACK = "%.4e"
    def __init__(self, parent=None):
        super(PvTunerDlg, self).__init__(parent)

        self.setAttribute(Qt.WA_DeleteOnClose)

        #self.inputBox = QLineEdit("PL2G2C01A.x")
        #self.inputBox = QLineEdit("CXH2G6C01B.x")
        self.inputBox = QLineEdit("PL2G2C01A")

        addPvBtn = QPushButton("add")

        self.table = QTableWidget(0, PvTunerDlg.COL)
        self.table.setHorizontalHeaderLabels(["Element", "Field", "PV",
                 "Stepsize", "Readback", "setpoint"])
        #self.table.horizontalHeader().setStretchLastSection(True)
        #self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)

        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok)

        box = QGridLayout()
        box.addWidget(self.inputBox, 0, 0)
        box.addWidget(addPvBtn, 0, 1)
        box.addWidget(self.table, 1, 0, 1, 2)
        box.addWidget(buttonBox, 2, 0)

        self.setLayout(box)

        self.pvs_rb = []
        self.pvs_rb_val_flat = []
        self.pvs_sp = []
        self.pvmoni = []
        self.spinbox = []
        self.connect(addPvBtn, SIGNAL("clicked()"), self.addPv)
        self.connect(buttonBox, SIGNAL("accepted()"), self.accept)
        #self.connect(self.table, SIGNAL("cellChanged"), self.updatePv)
        self.connect(buttonBox.button(QDialogButtonBox.Ok),
                     SIGNAL("clicked()"), self.close)
        self.connect(self.table, SIGNAL("cellClicked(int, int)"),
                     self._cell_clicked)


    def _cell_clicked(self, row, column):
        #print row, column
        if column in [self.COL_PV, self.COL_STEPSIZE]:
            item = self.table.item(row, column)
            if not item: return
            item.setFlags(item.flags() | Qt.ItemIsEditable)

    def _appendRecord(self, name):
        vec = name.split('.')
        if len(vec) > 2:
            QMessageBox.critical(None, "ERROR", "format is wrong")
            return

        if len(vec) == 1:
            elem, field = vec[0], 'value'
        elif len(vec) == 2:
            elem, field = vec

        elemobj = hla.getElements(elem)
        if elemobj:
            # pvsrb is a list
            pvsrb = elemobj.pv(field=field, handle='readback')
            self.pvs_rb.append(pvsrb)
            pvssp = elemobj.pv(field=field, handle='setpoint')
            self.pvs_sp.append(pvssp)
        else:
            QMessageBox.critical(None, "ERROR", "element %s not found" % elem)
            return

        # expand one row
        m, n = self.table.rowCount(), self.table.columnCount()
        self.table.insertRow(m)

        # add cells
        item = QTableWidgetItem(elem)
        item.setFlags(item.flags() & (~Qt.ItemIsEditable))
        self.table.setItem(m, self.COL_ELEMENT, item)

        item = QTableWidgetItem(field)
        item.setFlags(item.flags() & (~Qt.ItemIsEditable))
        self.table.setItem(m, self.COL_FIELD, item)


        item = QTableWidgetItem(', '.join(pvsrb))
        #item.setFlags(Qt.ItemIsSelectable|Qt.ItemIsEnabled)
        self.table.setItem(m, self.COL_PV, item)

        readval = ['%.4e' % v for v in caget(pvsrb)]
        item = QTableWidgetItem(', '.join(readval))
        item.setFlags(item.flags() & (~Qt.ItemIsEditable))
        self.table.setItem(m, self.COL_READBACK, item)

        # set the stepsize of PV
        stepsize = 0.00001
        if pvssp:
            item = QTableWidgetItem('%f' % stepsize)
            item.setFlags(item.flags() & (~Qt.ItemIsEditable))
            self.table.setItem(m, self.COL_STEPSIZE, item)

            self.spinbox.append(QDoubleSpinBox(self.table))
            self.spinbox[-1].setRange(-100, 100)
            #self.spinbox[-1].setValue(float(10.0))
            self.spinbox[-1].setSingleStep(stepsize)
            self.spinbox[-1].setDecimals(10)

            self.spinbox[-1].valueChanged.connect(self._writePv)

            self.table.setCellWidget(m, self.COL_SETPOINT, self.spinbox[-1])

            sp = float(caget(pvssp)[0])
            #print "setpoint:", pvssp, sp, type(sp)
            self.spinbox[-1].setValue(-1e-5)
            #print "connected", self.spinbox[-1].value()
        else:
            item = self.table.item(m, self.COL_STEPSIZE)
            if item: item.setFlags(item.flags() & (~Qt.ItemIsEditable))
            item = self.table.item(m, self.COL_SETPOINT)
            if item: item.setFlags(item.flags() & (~Qt.ItemIsEditable))
            self.spinbox.append(None)

        self.table.resizeColumnsToContents()


    def addPv(self):
        self._appendRecord(str(self.inputBox.text()))
        self._updateMonitors()

    def minimalSizeHint(self):
        return QSize(800, 600)


    def _writePv(self, v):
        """
        """
        c = QObject.sender(self)
        i = self.spinbox.index(c)
        #print i, c.text(), "changed"

        #print self.pvs_sp[i], v
        caput(self.pvs_sp[i], v)

    def _updateMonitors(self):
        """
        prepare the PV list for camonitor
        """
        #print "Updating monitors"
        pvs = []
        self.pvs_rb_val = []
        for i in range(self.table.rowCount()):
            for j in range(len(self.pvs_rb[i])):
                self.pvs_rb_val.append([i, 0.0])
            pvs.extend(self.pvs_rb[i])

        for p in self.pvmoni: p.close()
        self.pvmoni = camonitor(pvs, self._updatePvValues)
        #print self.pvmoni
        #print pvs
        #print self.pvs_rb_val


    def _updatePvValues(self, val, idx):
        #print idx, val
        s = []
        for i, v in enumerate(self.pvs_rb_val):
            if v[0] == self.pvs_rb_val[idx][0]:
                s.append(self.FMT_READBACK % val)
        #print s
        item = self.table.item(self.pvs_rb_val[idx][0], self.COL_READBACK)
        item.setText(','.join(s))

    def closePvMonitors(self):
        #print "Closing PV Monitors"
        for p in self.pvmoni: p.close()

        pass

    def closeEvent(self, event):
        self.closePvMonitors()
        event.accept()

    def close(self):
        self.closePvMonitors()
        return True

if __name__ == "__main__":
    import sys
    hla.machines.initNSLS2VSRTxt()
    print("Good !")

    #app = QApplication(sys.argv)
    form = PvTunerDlg()
    form.resize(800, 600)

    #form._appendRecord("PL2G2C01A")
    form._appendRecord("PL2G2C01A.x")
    form._appendRecord("PL2G2C01A.y")
    form._appendRecord("CXH2G6C01B.x")
    form._updateMonitors()

    form.show()
    #app.exec_()

    cothread.WaitForQuit()

    #print "selected: ", form.result()

