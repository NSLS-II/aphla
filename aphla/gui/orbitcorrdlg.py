"""
Dialog for Orbit Correction and Local Bump
------------------------------------------

"""

# :author: Lingyun Yang <lyyang@bnl.gov>

if __name__ == "__main__":
    import cothread
    app = cothread.iqt()
    import aphla


from PyQt4 import QtGui, QtCore
from PyQt4.Qt import Qt, SIGNAL
from PyQt4.QtGui import (QDialog, QTableWidget, QTableWidgetItem,
                         QDoubleSpinBox, QGridLayout, QVBoxLayout,
                         QHBoxLayout, QSizePolicy, QHeaderView,
                         QDialogButtonBox, QPushButton, QApplication,
                         QLabel, QGroupBox, QLineEdit, QDoubleValidator,
                         QIntValidator, QSizePolicy, QDialogButtonBox, 
                         QFormLayout, QSpinBox, QProgressBar, QAbstractButton)
import PyQt4.Qwt5 as Qwt

import numpy as np
from aporbitplot import ApCaPlot, ApCaArrayPlot
from aphla import catools, getElements, setLocalBump, getBeta, getEta, getPhase, getTunes, getAlpha

class DoubleSpinBoxCell(QDoubleSpinBox):
    def __init__(self, row = -1, col = -1, val = 0.0, parent = None):
        super(QDoubleSpinBox, self).__init__(parent)
        self.row = row
        self.col = col
        self.setValue(val)
        self.setDecimals(10)

class ElementSelectDlg(QDialog):
    def __init__(self, allelems, parent=None,
                 title='Choose Elements:'):
        """elemobj"""
        super(ElementSelectDlg, self).__init__(parent)
        self.setWindowTitle(title)
        self.elemlst = QtGui.QListWidget()
        self.result = []
        # enable multi-selection
        self.elemlst.setSelectionMode(QtGui.QAbstractItemView.MultiSelection)
        for e,st in allelems:
            w = QtGui.QListWidgetItem(e)
            w.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
            if st: w.setSelected(True)
            self.elemlst.addItem(w)
        #self.elemlst.setSortingEnabled(True)

        elemLabel = QLabel(title)

        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok|
                                     QDialogButtonBox.Cancel)

        layout = QGridLayout()
        layout.addWidget(elemLabel, 0, 0)
        layout.addWidget(self.elemlst, 1, 0)
        layout.addWidget(buttonBox, 2, 0)
        self.setLayout(layout)

        self.connect(buttonBox, SIGNAL("accepted()"), self.accept)
        self.connect(buttonBox, SIGNAL("rejected()"), self.reject)
        self.connect(self.elemlst, SIGNAL("itemSelectionChanged()"),
                     self.updateSelections)

    def updateSelections(self):
        #print self.elemlst.selectedItems()
        for i in range(self.elemlst.count()):
            it = self.elemlst.item(i)
            name = str(it.text())
            if it.isSelected() and name not in self.result:
                self.result.append(name)
            elif not it.isSelected() and name in self.result:
                self.result.pop(name)

class OrbitCorrGeneral(QtGui.QWidget):
    def __init__(self, bpms, cors, parent = None):
        super(OrbitCorrGeneral, self).__init__(parent)

        self.bpms, self.cors = bpms, cors
        self.sb = [bpm.sb for bpm in self.bpms]
        self.x0, self.y0 = None, None
        self._update_current_orbit()

        self.table = QTableWidget(len(self.bpms), 9)
        self.table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        hdview = QHeaderView(Qt.Horizontal)
        self.table.setHorizontalHeaderLabels(
            ['BPM Name', 's', "Beta X", "Beta Y",
             "Eta X", 'X Bump', 'Y Bump', "Target X", "Target Y"])
        beta = ap.getBeta([b.name for b in self.bpms])
        eta = ap.getEta([b.name for b in self.bpms])
        for i,bpm in enumerate(self.bpms):
            it = QTableWidgetItem(bpm.name)
            it.setFlags(it.flags() & (~Qt.ItemIsEditable))
            self.table.setItem(i, 0, it)

            it = QTableWidgetItem(str(bpm.sb))
            it.setFlags(it.flags() & (~Qt.ItemIsEditable))
            #it.setMinimumWidth(80)
            self.table.setItem(i, 1, it)
            self.table.setItem(i, 2, QTableWidgetItem("%.4f" % beta[i,0]))
            self.table.setItem(i, 3, QTableWidgetItem("%.4f" % beta[i,1]))
            self.table.setItem(i, 4, QTableWidgetItem("%.4f" % eta[i,0]))

            for j in range(5, 9):
                it = QTableWidgetItem(str(0.0))
                it.setData(Qt.DisplayRole, str(0.0))
                it.setFlags(it.flags() | Qt.ItemIsEditable)
                self.table.setItem(i, j, it) 
            # use the current orbit 
            #self.table.item(i,4).setData(Qt.DisplayRole, str(self.x0[i]))
            #self.table.item(i,5).setData(Qt.DisplayRole, str(self.y0[i]))

        #self.connect(self.table, SIGNAL("cellClicked(int, int)"),
        #             self._cell_clicked)
        self.table.resizeColumnsToContents()
        #self.table.horizontalHeader().setStretchLastSection(True)
        #for i in range(4):
        #    print "width", i, self.table.columnWidth(i)
        #self.table.setColumnWidth(0, 300)
        self.table.setColumnWidth(1, 80)

        vbox1 = QtGui.QVBoxLayout()
        frmbox = QFormLayout()
        self.base_orbit_box = QtGui.QComboBox()
        #self.base_orbit_box.addItems([
        #        "Current Orbit", "All Zeros"])
        self.base_orbit_box.addItems(["All Zeros", "Current Orbit"])
        frmbox.addRow("Orbit Base", self.base_orbit_box)
        grp = QtGui.QGroupBox("Local Bump")
        grp.setLayout(frmbox)
        vbox1.addWidget(grp)

        frmbox = QFormLayout()
        hln1 = QtGui.QFrame()
        hln1.setLineWidth(3)
        hln1.setFrameStyle(QtGui.QFrame.Sunken)
        hln1.setFrameShape(QtGui.QFrame.HLine)
        frmbox.addRow(hln1)
        self.repeatbox = QSpinBox()
        self.repeatbox.setRange(1, 20)
        self.repeatbox.setValue(3)
        # or connect the returnPressed() signal
        frmbox.addRow("&Repeat correction", self.repeatbox)

        self.rcondbox = QLineEdit()
        self.rcondbox.setValidator(QDoubleValidator(0, 1, 0, self))
        self.rcondbox.setText("1e-2")
        frmbox.addRow("r&cond for SVD", self.rcondbox)

        self.scalebox = QDoubleSpinBox()
        self.scalebox.setRange(0.01, 5.00)
        self.scalebox.setSingleStep(0.01)
        self.scalebox.setValue(0.68)
        frmbox.addRow("&Scale correctors", self.scalebox)

        #hln2 = QtGui.QFrame()
        #hln2.setLineWidth(3)
        #hln2.setFrameStyle(QtGui.QFrame.Sunken)
        #hln2.setFrameShape(QtGui.QFrame.HLine)
        #frmbox.addRow(hln2)

        self.progress = QProgressBar()
        self.progress.setMaximum(self.repeatbox.value())
        self.progress.setMaximumHeight(15)
        frmbox.addRow("Progress", self.progress)
        grp = QtGui.QGroupBox("Correction")
        grp.setLayout(frmbox)
        vbox1.addWidget(grp)

        #vbox.addStretch(1.0)
        #self.qdb = QDialogButtonBox(self)
        #self.qdb.addButton("APP", QDialogButtonBox.ApplyRole)
        #self.qdb.addButton("R", QDialogButtonBox.ResetRole)
        #btn.setDefault(True)
        #self.qdb.addButton(QDialogButtonBox.Cancel)
        #self.qdb.addButton(QDialogButtonBox.Help)

        gbox = QtGui.QGridLayout()
        btn = QPushButton("Reset")
        self.connect(btn, SIGNAL("clicked()"), self.resetBumps)
        gbox.addWidget(btn, 0, 1)

        self.correctOrbitBtn = QPushButton("Apply")
        #self.correctOrbitBtn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.correctOrbitBtn.setStyleSheet("QPushButton:disabled { color: gray }");
        self.connect(self.correctOrbitBtn, SIGNAL("clicked()"), self.call_apply)
        self.correctOrbitBtn.setDefault(True)
        gbox.addWidget(self.correctOrbitBtn, 1, 1)
        gbox.setColumnStretch(0, 1)

        vbox1.addStretch()
        vbox1.addLayout(gbox)
        
        hbox1 = QtGui.QHBoxLayout()
        hbox1.addWidget(self.table, 2)
        hbox1.addLayout(vbox1, 0)
        self.setLayout(hbox1)

        self.connect(self.base_orbit_box,
                     SIGNAL("currentIndexChanged(QString)"), 
                     self.updateTargetOrbit)
        self.connect(self.repeatbox, SIGNAL("valueChanged(int)"),
                     self.progress.setMaximum)
        self.connect(self.table, SIGNAL("cellChanged (int, int)"),
                     self.updateBump)

        #self.updateTargetOrbit(self.base_orbit_box.currentText())

    def _update_current_orbit(self):
        pvx = [bpm.pv(field="x", handle="readback")[0] for bpm in self.bpms]
        pvy = [bpm.pv(field="y", handle="readback")[0] for bpm in self.bpms]
        self.x0 = [float(v) for v in catools.caget(pvx)]
        self.y0 = [float(v) for v in catools.caget(pvy)]

    def resetBumps(self):
        jx0, jy0 = 5, 6
        for i in range(self.table.rowCount()):
            self.table.item(i, jx0).setData(Qt.DisplayRole, str(0.0))
            self.table.item(i, jy0).setData(Qt.DisplayRole, str(0.0))
        #self.updateTargetOrbit(self.base_orbit_box.currentText())

    def call_apply(self):
        #print "apply the orbit"
        obt = []
        jx, jy = 7, 8
        for i in range(self.table.rowCount()):
            x1,err = self.table.item(i, jx).data(Qt.DisplayRole).toFloat()
            y1,err = self.table.item(i, jy).data(Qt.DisplayRole).toFloat()
            obt.append([x1, y1])

        self.correctOrbitBtn.setEnabled(False)
        nrepeat = self.repeatbox.value()
        kw = { "scale": float(self.scalebox.text()),
               "rcond": float(self.rcondbox.text()) }
        self.progress.setValue(0)
        QApplication.processEvents()
        for i in range(nrepeat):
            err, msg = setLocalBump(self.bpms, self.cors, obt, **kw)
            self.progress.setValue(i+1)
            QApplication.processEvents()
            if err != 0:
                QtGui.QMessageBox.critical(
                    self, "Local Orbit Bump", 
                    "ERROR: {0}\nAbort.".format(msg),
                    QtGui.QMessageBox.Ok)
                #self.progress.setValue(0)
                break
       
        self.correctOrbitBtn.setEnabled(True)

    def getTargetOrbit(self):
        x = [self.table.item(i,7).data(Qt.DisplayRole).toFloat()[0]
             for i in range(self.table.rowCount())]
        y = [self.table.item(i,8).data(Qt.DisplayRole).toFloat()[0]
             for i in range(self.table.rowCount())]
        return (self.sb, x), (self.sb, y)

    def updateTargetOrbit(self, baseobt):
        if baseobt == "All Zeros":
            jx0, jx1 = 5, 7
            jy0, jy1 = 6, 8
            for i in range(self.table.rowCount()):
                it0 = self.table.item(i, jx0)
                it1 = self.table.item(i, jx1)
                it1.setData(Qt.DisplayRole, it0.data(Qt.DisplayRole))
                it0 = self.table.item(i, jy0)
                it1 = self.table.item(i, jy1)
                it1.setData(Qt.DisplayRole, it0.data(Qt.DisplayRole))
        elif baseobt == "Current Orbit":
            self._update_current_orbit()
            jx0, jx1 = 5, 7
            jy0, jy1 = 6, 8
            for i in range(self.table.rowCount()):
                dx0,err = self.table.item(i, jx0).data(Qt.DisplayRole).toFloat()
                it = self.table.item(i, jx1)
                it.setData(Qt.DisplayRole, self.x0[i] + dx0)

                dy0,err = self.table.item(i, jy0).data(Qt.DisplayRole).toFloat()
                it = self.table.item(i, jy1)
                it.setData(Qt.DisplayRole, self.y0[i] + dy0)
        #self._update_orbit_plot()
        x, y = self.getTargetOrbit()
        self.emit(SIGNAL("targetOrbitChanged(PyQt_PyObject, PyQt_PyObject)"),
                  x, y)

    def updateBump(self, row, col):
        #print "updating ", row, col
        if col == 5 or col == 6:
            self.updateTargetOrbit(self.base_orbit_box.currentText())


class OrbitCorrNBumps(QtGui.QWidget):
    def __init__(self, bpms, cors, plots = [], parent = None):
        super(OrbitCorrNBumps, self).__init__(parent)
        self.bpm_all, self.cor_all = bpms, cors
        self.cors = []
        self._plots = plots
        self._corlst1 = QtGui.QTreeWidget()
        header = ["Element", "Family", "s [m]", "Alpha X", "Alpha Y",
                  "Beta X", "Beta Y", "Phi X", "Phi Y"]
        self._corlst1.setColumnCount(len(header))
        self._corlst1.setHeaderLabels(header)
        prevcell = None
        for i,c in enumerate(self.cor_all):
            if c.cell and (prevcell is None or c.cell != prevcell.text(0)):
                # a new parent
                prevcell = QtGui.QTreeWidgetItem()
                prevcell.setText(0, c.cell)
                self._corlst1.addTopLevelItem(prevcell)
            it = QtGui.QTreeWidgetItem()
            it.setText(0, c.name)
            it.setText(1, c.family)
            it.setText(2, "%.3f" % c.sb)
            try:
                alfa = getAlpha(c.name)
                it.setText(3, "%.4f" % alfa[0,0])
                it.setText(4, "%.4f" % alfa[0,1])
                beta = getBeta(c.name)
                it.setText(5, "%.4f" % beta[0,0])
                it.setText(6, "%.4f" % beta[0,1])
                phse = getPhase(c.name)
                it.setText(7, "%.4f" % phse[0,0])
                it.setText(8, "%.4f" % phse[0,1])
            except:
                pass

            if c.cell:
                prevcell.addChild(it)
            else:
                self._corlst1.addTopLevelItem(it)
                prevcell = it
        #self._corlst1.resizeColumnToContents(0)
        self._corlst1.setColumnWidth(0, 150)
        self._corlst1.expandAll()


        vbox1 = QtGui.QVBoxLayout()
        vbox1.addWidget(self._corlst1, 1)

        #self.elemlst.setSelectionMode(QAbstractItemView.MultiSelection)
        columns = ['Corrector', 's', 'Alpha X', 'Alpha Y', 'Beta X', 'Beta Y',
                   'Phi X', 'Phi Y', "dPhiX", "dPhiY", "dX", "dY", "X", "Y"]
        self.table4 = QTableWidget(4, len(columns))
        self.table4.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        hdview = QHeaderView(Qt.Horizontal)
        self.table4.setHorizontalHeaderLabels(columns)
        for i in range(4):
            for j in range(len(columns)):
                it = QTableWidgetItem()
                self.table4.setItem(i, j, it)
        self.table4.resizeColumnsToContents()
        self.table4.horizontalHeader().setStretchLastSection(True)
        hrow = self.table4.rowHeight(0)
        htbl = (hrow * 4) + self.table4.horizontalHeader().height() +\
            2*self.table4.frameWidth()
        self.table4.setMinimumHeight(htbl + 10)
        self.table4.setMaximumHeight(htbl + 10)
        vbox1.addWidget(self.table4, 0)

        hbox1 = QtGui.QHBoxLayout()
        hbox1.addLayout(vbox1, 2)

        fmbox = QtGui.QFormLayout()
        self.src = QtGui.QLineEdit()
        self.src_x = QtGui.QLabel("???")
        self.src_xp = QtGui.QLabel("???")
        fmbox.addRow("Location", self.src)
        fmbox.addRow("Displacement", self.src_x)
        fmbox.addRow("Angle", self.src_xp)
        grp = QtGui.QGroupBox("Source Point")
        grp.setLayout(fmbox)

        vbox2 = QtGui.QVBoxLayout()
        vbox2.addWidget(grp)
        vbox2.addStretch()
        btnClear = QtGui.QPushButton("Clear")
        btnZoomin = QtGui.QPushButton("Zoom In")
        btnApply  = QtGui.QPushButton("Apply")
        btnCheat = QtGui.QPushButton("_CHEAT_")
        vbox2.addWidget(btnClear)
        vbox2.addWidget(btnZoomin)
        vbox2.addWidget(btnApply)
        vbox2.addWidget(btnCheat)
        hbox1.addLayout(vbox2)
        self.setLayout(hbox1)

        self.connect(btnClear, SIGNAL("clicked()"), self._clear_correctors)
        self.connect(btnZoomin, SIGNAL("clicked()"), self._zoom_in_plots)
        self.connect(btnApply, SIGNAL("clicked()"), self._apply_bump)
        self.connect(btnCheat, SIGNAL("clicked()"), self._cheat)
        self.connect(self._corlst1, SIGNAL("doubleClicked(QModelIndex)"),
                     self.addCorrector)
        self.connect(self.src, SIGNAL("returnPressed()"),
                     self._calc_source)
        self.connect(self.table4, SIGNAL("cellChanged(int, int)"),
                     self.updateTable)

        #self.connect(self.table4, SIGNAL("doubleClicked(QModelIndex)"),
        #             self.delCorrector)

    def _clear_correctors(self):
        self.cors = []
        for i in range(self.table4.rowCount()):
            for j in range(self.table4.columnCount()):
                self.table4.item(i,j).setData(Qt.DisplayRole, "")
        self.updateCorrectors(None)

    def _calc_source(self):
        self.src_x.setText(self.src_x.text() + QtCore.QString(" ??"))
        self.src_xp.setText(self.src_xp.text() + QtCore.QString(" ??"))

    def _cheat(self):
        s = aphla.catools.caget('V:2-SR-BI{POS}-I')
        x = aphla.catools.caget('V:2-SR-BI{ORBIT}X-I')
        y = aphla.catools.caget('V:2-SR-BI{ORBIT}Y-I')
        p = self._plots[0]
        p._cheat[0].setData(s, x)
        p._cheat[1].setData(s, y)
        p.replot()

    def addCorrector(self, idx):
        #['Corrector', 's', 'Beta X', 'Beta Y', 'Phi X', 'Phi Y',
        #     "dPhiX", "dPhiY", "dX", "dY", "X", "Y"])
        it0 = self._corlst1.selectedItems()[-1]
        i = len(self.cors)
        # name, s
        print self.cors
        self.table4.item(i,0).setData(Qt.DisplayRole, it0.text(0))
        self.table4.item(i,1).setData(Qt.DisplayRole, it0.text(2))
        self.table4.item(i,2).setData(Qt.DisplayRole, it0.text(3))
        self.table4.item(i,3).setData(Qt.DisplayRole, it0.text(4))
        self.table4.item(i,4).setData(Qt.DisplayRole, it0.text(5))
        self.table4.item(i,5).setData(Qt.DisplayRole, it0.text(6))
        self.table4.item(i,6).setData(Qt.DisplayRole, it0.text(7))
        self.table4.item(i,7).setData(Qt.DisplayRole, it0.text(8))
        self.table4.resizeColumnsToContents()
        self.updateCorrectors(None)

    def delCorrector(self, idx):
        #self.table4.removeRow(idx.row())
        n = self.table4.rowCount()
        for i in range(idx.row(), n - 1):
            for j in range(self.table4.columnCount()):
                dat = self.table4.item(i+1,j).data(Qt.DisplayRole)
                self.table4.item(i,j).setData(Qt.DisplayRole, dat)

        for j in range(self.table4.columnCount()):
            self.table4.item(n-1,j).setData(Qt.DisplayRole, "")
        
        self.updateCorrectors(None)

    def updateCorrectors(self, name):
        corls = [self.table4.item(i,0).data(Qt.DisplayRole).toString()
                 for i in range(self.table4.rowCount())]
        _cors = [c for c in self.cor_all if c.name in corls]
        #print corls, self.cors

        if len(_cors) < 3:
            self.cors = _cors
            return

        nux, nuy = getTunes(source="database")
        beta = getBeta([c.name for c in _cors])
        phse = getPhase([c.name for c in _cors])
        
        #print beta, type(beta)
        #print phse, type(phse)
        tb = self.table4
        jx, jy = 8, 9
        for i,c in enumerate(_cors):
            #tb.item(i,0).setData(Qt.DisplayRole, c.name)
            #tb.item(i,1).setData(Qt.DisplayRole, c.sb)
            #tb.item(i,2).setData(Qt.DisplayRole, "%.4f" % (beta[i,0],))
            #tb.item(i,3).setData(Qt.DisplayRole, "%.4f" % (beta[i,1],))
            #tb.item(i,4).setData(Qt.DisplayRole, "%.4f" % (phse[i,0],))
            #tb.item(i,5).setData(Qt.DisplayRole, "%.4f" % (phse[i,1],))

            # I do not like the way, phase has no 2pi
            dphx = (phse[i,0] - phse[0,0]) * 2.0 * np.pi
            if dphx < 0: dphx += nux * 2 * 3.14159
            tb.item(i,jx).setData(Qt.DisplayRole, "%.4f" % (dphx,))
            
            dphy = (phse[i,1] - phse[0,1]) * 2.0 * np.pi
            if dphy < 0: dphy += nuy * 2 * 3.14159
            tb.item(i,jy).setData(Qt.DisplayRole, "%.4f" % (dphy,))

            tb.item(i,jx+2).setData(Qt.DisplayRole, "0.0")
            tb.item(i,jy+2).setData(Qt.DisplayRole, "0.0")

            if c.pv(field="x", handle="setpoint"):
                tb.item(i,jx+4).setData(Qt.DisplayRole, "%.5f" % (c.x,))
            if c.pv(field="y", handle="setpoint"):
                tb.item(i,jy+4).setData(Qt.DisplayRole, "%.5f" % (c.y,))            
            
        tb.resizeColumnsToContents()
        tb.setColumnWidth(jx+2, 80)
        tb.setColumnWidth(jy+2, 80)
        self.cors = _cors

        self.emit(SIGNAL("correctorChanged(PyQt_PyObject)"), self.cors)

    def _zoom_in_plots(self):
        s = []
        for i in range(self.table4.rowCount()):
            val, ok = self.table4.item(i,1).data(Qt.DisplayRole).toFloat()
            if not ok: continue
            s.append(val)

        s0, s1 = min(s), max(s)
        ds = (s1 - s0)/ 10.0
        for p in self._plots:
            p.setAxisScale(Qwt.QwtPlot.xBottom, s0 - ds, s1 + ds)
            p.replot()
        
    def updateTable(self, row, col):
        #print self.table4.currentRow(), self.table4.currentColumn()
        if col != 8 and col != 9: return
        if len(self.cors) < 3: return
        jbx, jby = 4, 5
        jdphx, jdphy = 8, 9
        bx = [self.table4.item(i,jbx).data(Qt.DisplayRole).toFloat()[0]
              for i in range(len(self.cors))]
        by = [self.table4.item(i,jby).data(Qt.DisplayRole).toFloat()[0]
              for i in range(len(self.cors))]
        dphx = [self.table4.item(i,jdphx).data(Qt.DisplayRole).toFloat()[0]
              for i in range(len(self.cors))]
        dphy = [self.table4.item(i,jdphy).data(Qt.DisplayRole).toFloat()[0]
              for i in range(len(self.cors))]
        print bx, by, dphx, dphy
        cx21 = -np.sqrt(bx[0]/bx[1])*(np.sin(dphx[2] - dphx[0]) / 
                                      np.sin(dphx[2] - dphx[1]))
        cx31 = -np.sqrt(bx[0]/bx[2])*(np.sin(dphx[1] - dphx[0]) / 
                                      np.sin(dphx[1] - dphx[2]))
        jdx, jdy = 10, 11
        if row == 0:
            dx, err = self.table4.item(0,jdx).data(Qt.DisplayRole).toFloat()
            self.table4.item(1,jdx).setData(Qt.DisplayRole, str(dx*cx21))
            self.table4.item(2,jdx).setData(Qt.DisplayRole, str(dx*cx31))
    
    def _apply_bump(self):
        jdx, jdy = 10, 11
        for i,c in enumerate(self.cors):
            dx, err = self.table4.item(i,jdx).data(Qt.DisplayRole).toFloat()
            print c.name, c.x,
            c.x = c.x + dx
            print dx, c.x, c.pv(field="x", handle="setpoint")
            self.table4.item(i,jdx+2).setData(Qt.DisplayRole, str(c.x))
            
class OrbitCorrDlg(QDialog):
    def __init__(self, bpms = None, cors = None, parent = None):
        super(OrbitCorrDlg, self).__init__(parent)
        # add bpms
        bpmls = bpms
        if bpms is None:
            bpmls = getElements("BPM")
        bpmls = [bpm for bpm in bpmls if bpm.flag == 0]
        pvx = [bpm.pv(field="x", handle="readback")[0] for bpm in bpmls]
        pvy = [bpm.pv(field="y", handle="readback")[0] for bpm in bpmls]
        #
        #self._update_current_orbit()

        s = [bpm.sb for bpm in bpmls]
        self.bpm_plot = ApCaArrayPlot([pvx, pvy], x = [s, s])
        magprof = aphla.getBeamlineProfile()
        self.bpm_plot.setMagnetProfile(magprof)

        self.xc = Qwt.QwtPlotCurve()
        self.xc.setTitle("Target X")
        self.xc.attach(self.bpm_plot)
        #self.xc.setData(s, self.x0)
        self.bpm_plot.showCurve(self.xc, True)

        self.yc = Qwt.QwtPlotCurve()
        self.yc.setTitle("Target Y")
        self.yc.attach(self.bpm_plot)
        #self.yc.setData(s, self.y0)
        self.bpm_plot.showCurve(self.yc, True)

        self.bpm_plot._cheat = [Qwt.QwtPlotCurve(), Qwt.QwtPlotCurve()]
        self.bpm_plot._cheat[0].setTitle("_CHEAT_ X")
        self.bpm_plot._cheat[1].setTitle("_CHEAT_ Y")
        self.bpm_plot._cheat[0].attach(self.bpm_plot)
        self.bpm_plot._cheat[1].attach(self.bpm_plot)
        self.bpm_plot._set_symbol(self.bpm_plot._cheat[0],
                                  Qwt.QwtSymbol.Triangle, dsize=2)
        self.bpm_plot._set_symbol(self.bpm_plot._cheat[1], Qwt.QwtSymbol.Diamond, dsize=2)
        self.bpm_plot.showCurve(self.bpm_plot._cheat[0], False)
        self.bpm_plot.showCurve(self.bpm_plot._cheat[1], False)

        self.bpm_plot.setContentsMargins(12, 10, 10, 10)

        # add corrector plots
        corls = cors
        if cors is None:
            corls = []
            for c in getElements("HCOR") + getElements("VCOR"):
                if c not in corls:
                    corls.append(c)
        pvx = [c.pv(field="x", handle="setpoint")[0]
               for c in getElements("HCOR") if c in corls]
        pvy = [c.pv(field="y", handle="setpoint")[0]
               for c in getElements("VCOR") if c in corls]
        s = [c.sb for c in corls]
        self.cor_plot = ApCaArrayPlot([pvx, pvy], x = [s, s],
                                      labels=["HCOR", "VCOR"])
        #magprof = aphla.getBeamlineProfile()
        self.cor_plot.setMagnetProfile(magprof)
        self.cor_plot.setContentsMargins(12, 10, 10, 10)
        #self.cor_plot.setMinimumHeight(200)
        #self.cor_plot.setMaximumHeight(250)

        # add twiss plots
        self.tw_plot = ApCaPlot()
        cbetax = Qwt.QwtPlotCurve()
        pen = cbetax.pen()
        pen.setColor(Qt.red)
        cbetax.setPen(pen)
        cbetay = Qwt.QwtPlotCurve()
        pen.setColor(Qt.green)
        cbetay.setPen(pen)
        cetax  = Qwt.QwtPlotCurve()
        pen.setColor(Qt.blue)
        cetax.setPen(pen)
        beta = getBeta("[pqs]*", spos=True)
        eta = getEta("[pqs]*", spos = True)
        cbetax.setData(beta[:,-1], beta[:,0])
        cbetay.setData(beta[:,-1], beta[:,1])
        cetax.setData(  eta[:,-1],  10.0*eta[:,0])
        cbetax.attach(self.tw_plot)
        cbetax.setTitle("Beta X")
        cbetay.attach(self.tw_plot)
        cbetay.setTitle("Beta Y")
        cetax.attach( self.tw_plot)
        cetax.setTitle("10*Eta X")
        self.tw_plot.setMagnetProfile(magprof)
        self.tw_plot.setContentsMargins(12, 10, 10, 10)
        self.tw_plot.showCurve(cbetax, True)
        self.tw_plot.showCurve(cbetay, True)
        self.tw_plot.showCurve(cetax, True)

        # top tabs for plotting
        tabs = QtGui.QTabWidget()
        tabs.addTab(self.bpm_plot, "Orbit")
        tabs.addTab(self.cor_plot, "Correctors")
        tabs.addTab(self.tw_plot, "Twiss")
        tabs.setMinimumHeight(200)
        tabs.setMaximumHeight(280)

        layout = QVBoxLayout()
        layout.addWidget(tabs, 1)

        tabs = QtGui.QTabWidget()
        tab_general_cor = OrbitCorrGeneral(bpmls, corls)
        self.connect(tab_general_cor, 
                     SIGNAL("targetOrbitChanged(PyQt_PyObject, PyQt_PyObject)"),
                     self._update_orbit_plot)
        xobt, yobt = tab_general_cor.getTargetOrbit()
        self._update_orbit_plot(xobt, yobt)
        tabs.addTab(tab_general_cor, "General Bump")

        tab_nbump_cor = OrbitCorrNBumps(bpmls, corls, plots=[
                self.bpm_plot, self.cor_plot, self.tw_plot])
        self.connect(tab_nbump_cor, 
                     SIGNAL("correctorChanged(PyQt_PyObject)"),
                     self._update_corr_plot)
        tabs.addTab(tab_nbump_cor, "3/4 Bumps")
        layout.addWidget(tabs, 3)

        #hln = QtGui.QFrame()
        #hln.setLineWidth(3)
        #hln.setFrameStyle(QtGui.QFrame.Sunken)
        #hln.setFrameShape(QtGui.QFrame.HLine)
        #layout.addWidget(hln)

        #hbox = QHBoxLayout()

        #hbox.addStretch()
        #btn = QPushButton("Close")
        #self.connect(btn, SIGNAL("clicked()"), self.accept)
        #hbox.addWidget(btn)
        #layout.addLayout(hbox)

        self.setLayout(layout)
        #self.update_orbit = update_orbit
        #self._x0 = tuple(x)  # save for reset
        #self._y0 = tuple(y)  # save for reset
        #self.val = [s, x, y]
        self.setMinimumWidth(1000)
        # draw the target orbit
        #self.bpm_plots[0].plotCurve2(self.val[1], self.val[0])
        #self.bpm_plots[1].plotCurve2(self.val[2], self.val[0])

        #self.connect(self.qdb, SIGNAL("clicked(QAbstractButton)"), self._action)
        #self.connect(self.qdb, SIGNAL("helpRequested()"), self._help)

    #def _cell_clicked(self, row, col):
    #    print row, col

    def _update_orbit_plot(self, xobt, yobt):
        sx, vx = xobt
        sy, vy = yobt
        self.xc.setData(sx, vx)
        self.yc.setData(sy, vy)
        self.bpm_plot.replot()

    def _update_corr_plot(self, corls):
        mks = [(c.name, c.sb) for c in corls]
        s0 = min([c.sb for c in corls])
        s1 = max([c.se for c in corls])
        ds = (s1 - s0) / 10.0
        self.bpm_plot.setMarkers(mks)
        #self.bpm_plot.setAxisScale(Qwt.QwtPlot.xBottom, s0-ds, s1+ds)
        self.bpm_plot.replot()
        self.cor_plot.setMarkers(mks)
        self.cor_plot.replot()
        self.tw_plot.setMarkers(mks)
        self.tw_plot.replot()

    def _help(self):
        print "HELP"

    #def done(self, r):
    #    #for p in self.bpm_plots:
    #    #    p.plotCurve2(None, None)#
    #    
    #    QDialog.done(self, r)

    def _action(self, btn):
        #role = self.qdb.buttonRole(btn)
        #print "Role:", role
        #if role == QDialogButtonBox.ApplyRole:
        #    self.call_apply()
        #elif role == QDialogButtonBox.RejectRole:
        #    self.reject()
        pass

if __name__ == "__main__":
    import aphla as ap
    ap.machines.load("nsls2v2")
    bpms = ap.getElements("BPM")
    cors = ap.getElements("COR")
    form = OrbitCorrDlg(bpms) 
    #form = OrbitCorrGeneral(bpms, cors)
    #form = OrbitCorrNBumps(bpms, cors)
    form.resize(1000, 400)
    form.setWindowTitle("Create Local Bump")
    form.show()
    #form.reloadElements("*")
    #app.exec_()
    cothread.WaitForQuit()
