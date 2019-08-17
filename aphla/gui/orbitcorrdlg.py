from __future__ import print_function, division, absolute_import

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
from aphla import (catools, getElements, setLocalBump, fget,
                   getTwiss, getTunes, getTwissAt, getBeamlineProfile)
from functools import partial

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
    """
    A general orbit correction or local bump panel.
    """
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
        self._twiss = getTwiss([b.name for b in self.bpms],
                               ["s", "betax", "betay", "etax"])
        for i,bpm in enumerate(self.bpms):
            it = QTableWidgetItem(bpm.name)
            it.setFlags(it.flags() & (~Qt.ItemIsEditable))
            self.table.setItem(i, 0, it)

            it = QTableWidgetItem(str(bpm.sb))
            it.setFlags(it.flags() & (~Qt.ItemIsEditable))
            #it.setMinimumWidth(80)
            self.table.setItem(i, 1, it)
            self.table.setItem(i, 2,
                               QTableWidgetItem("%.4f" % self._twiss[i,1]))
            self.table.setItem(i, 3,
                               QTableWidgetItem("%.4f" % self._twiss[i,2]))
            self.table.setItem(i, 4,
                               QTableWidgetItem("%.4f" % self._twiss[i,3]))

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
        btn = QPushButton("Clear")
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
        self.x0 = [float(v) if v.ok else np.nan for v in catools.caget(pvx)]
        self.y0 = [float(v) if v.ok else np.nan for v in catools.caget(pvy)]

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


class CorrectorViewer(QtGui.QWidget):
    """
    List all corrector and select part to lower table
    """
    def __init__(self, cors, field, parent=None, nmax=4):
        super(CorrectorViewer, self).__init__(parent)
        self._nmax  = nmax
        self._field = field
        self._cors  = cors
        self._corlst1 = QtGui.QTreeWidget()
        self._header = dict([("Element", 0), ("Family", 1), ("s [m]", 2),
                             ("Alpha X", 3), ("Alpha Y", 4), ("Beta X", 5),
                             ("Beta Y", 6), ("Phi X", 7), ("Phi Y", 8),
                             ("Eta X", 9)])
        self._twiss = np.zeros((len(self._cors), 8), 'd')
        self._tunes = getTunes(source="database")
        self._corlst1.setColumnCount(len(self._header))
        self._corlst1.setHeaderLabels(
            sorted(self._header, key=self._header.get))
        self._corlst1.header().setStretchLastSection(False)
        prevcell = None
        for i,c in enumerate(self._cors):
            if c.cell and (prevcell is None or c.cell != prevcell.text(0)):
                # a new parent
                prevcell = QtGui.QTreeWidgetItem()
                prevcell.setText(0, c.cell)
                self._corlst1.addTopLevelItem(prevcell)
            it = QtGui.QTreeWidgetItem()
            it.setData(0, Qt.UserRole, i)
            it.setText(self._header["Element"], c.name)
            it.setText(self._header["Family"], c.family)
            it.setText(self._header["s [m]"], "%.3f" % c.sb)
            try:
                tw = getTwiss(c.name,
                              ["s", "alphax", "alphay", "betax", "betay",
                               "phix", "phiy", "etax"])
                self._twiss[i,:] = tw[0,:]
                it.setText(self._header["Alpha X"], "%.4f" % self._twiss[i,1])
                it.setText(self._header["Alpha Y"], "%.4f" % self._twiss[i,2])
                it.setText(self._header["Beta X"],  "%.4f" % self._twiss[i,3])
                it.setText(self._header["Beta Y"],  "%.4f" % self._twiss[i,4])
                it.setText(self._header["Phi X"],   "%.4f" % self._twiss[i,5])
                it.setText(self._header["Phi Y"],   "%.4f" % self._twiss[i,6])
                it.setText(self._header["Eta X"],   "%.4f" % self._twiss[i,7])
            except:
                it.setDisabled(True)
                pass

            if c.cell:
                prevcell.addChild(it)
            else:
                self._corlst1.addTopLevelItem(it)
                prevcell = it
            for j in range(2, len(self._header)):
                it.setTextAlignment(j, Qt.AlignRight)
        self._corlst1.expandAll()
        for i in range(len(self._header)):
            self._corlst1.resizeColumnToContents(i)
        #self._corlst1.setColumnWidth(0, 150)

        #self.elemlst.setSelectionMode(QAbstractItemView.MultiSelection)
        columns = ['Corrector', 's', 'Alpha', 'Beta',
                   'Phi', "dPhi", "Initial Bump", "Cur. Sp", "dBump",
                   "Final Rb"]
        self.table4 = QTableWidget(0, len(columns))
        #self.table4.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        hdview = QHeaderView(Qt.Horizontal)
        self.table4.setHorizontalHeaderLabels(columns)
        #for i in range(4):
        #    for j in range(len(columns)):
        #        it = QTableWidgetItem()
        #        if j > 0: it.setTextAlignment(
        #            Qt.AlignRight | Qt.AlignVCenter)
        #        if columns[j] != "dKick":
        #            it.setFlags(it.flags() & (~Qt.ItemIsEditable))
        #        self.table4.setItem(i, j, it)
        #self.table4.resizeColumnsToContents()
        #self.table4.horizontalHeader().setStretchLastSection(True)
        #hrow = self.table4.rowHeight(0)
        #htbl = (hrow * 4) + self.table4.horizontalHeader().height() +\
        #    2*self.table4.frameWidth()
        #self.table4.setMinimumHeight(htbl + 10)
        #self.table4.setMaximumHeight(htbl + 15)
        #self.table4.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        #print "Size:", htbl + 10
        self.table4.resize(self.table4.width(), 150)

        splitter = QtGui.QSplitter(Qt.Vertical)
        splitter.addWidget(self._corlst1)
        splitter.addWidget(self.table4)
        vbox1 = QtGui.QVBoxLayout()
        vbox1.addWidget(splitter)
        self.setLayout(vbox1)

        self.connect(self._corlst1, SIGNAL("doubleClicked(QModelIndex)"),
                     self.addCorrector)
        #self.connect(self.src, SIGNAL("returnPressed()"),
        #             self._calc_source)
        #self.connect(self.table4, SIGNAL("cellChanged(int, int)"),
        #             self.updateTable)

        #self.connect(self.table4, SIGNAL("doubleClicked(QModelIndex)"),
        #             self.delCorrector)
        self._x0 = fget(self._cors, "x", handle="setpoint", unitsys=None)
        self._y0 = fget(self._cors, "y", handle="setpoint", unitsys=None)


    def addCorrector(self, idx):
        if not self._corlst1.selectedItems(): return
        #print self._corlst1.itemFromIndex(idx).text(0)
        nrow = self.table4.rowCount()
        if nrow >= self._nmax:
            QtGui.QMessageBox.critical(
                self, "Local Orbit Bump",
                "ERROR: We need only {0} correctors.".format(self._nmax),
                QtGui.QMessageBox.Ok)
                #self.progress.setValue(0)
            return
        self.table4.setRowCount(nrow+1)
        it0 = self._corlst1.selectedItems()[-1]
        icor, ok = it0.data(0, Qt.UserRole).toInt()
        if icor < 0: return
        newc = self._cors[icor]
        for j in range(self.table4.columnCount()):
            it = QTableWidgetItem()
            if j > 0: it.setTextAlignment(
                Qt.AlignRight | Qt.AlignVCenter)
            header = self.table4.horizontalHeaderItem(j)
            if header.text() != "dBump":
                it.setFlags(it.flags() & (~Qt.ItemIsEditable))
            else:
                it.setData(Qt.DisplayRole, "0")
                it.setData(Qt.UserRole, 0.0)
            self.table4.setItem(nrow, j, it)
        self.table4.item(nrow,0).setData(Qt.UserRole, icor)
        for j,h in [(0, "Element"), (1, "s [m]")]:
            self.table4.item(nrow,j).setData(Qt.DisplayRole,
                                          it0.text(self._header[h]))
        for j in range(self._corlst1.columnCount()):
            it0.setForeground(j, Qt.red)
        it0.setDisabled(True)
        self.emit(SIGNAL("correctorAdded(PyQt_PyObject)"), newc)
        # use initial values

        self.updateTwiss()
        self.updateCorReadings()
        self.table4.resizeColumnsToContents()
        if self.table4.rowCount() == self._nmax:
            #print "All correctors are ready"
            self.emit(SIGNAL("correctorsComplete()"))

    def updateTwiss(self):
        if self._field == "x":
            jl = [self._header[h] for h in ["Alpha X", "Beta X", "Phi X"]]
            nu = self._tunes[0]
        elif self._field == "y":
            jl = [self._header[h] for h in ["Alpha Y", "Beta Y", "Phi Y"]]
            nu = self._tunes[1]
        else:
            raise RuntimeError("unknown cor field {0}".format(self._field))
        #print "index:", jl
        # if rows provided use it, otherwise use all
        for i in range(self.table4.rowCount()):
            elemname = self.table4.item(i,0).data(Qt.DisplayRole).toString()
            it0 = self._corlst1.findItems(
                elemname, Qt.MatchExactly | Qt.MatchRecursive)[0]

            self.table4.item(i,2).setText(it0.text(jl[0]))
            self.table4.item(i,3).setText(it0.text(jl[1]))
            self.table4.item(i,4).setText(it0.text(jl[2]))
            self.table4.item(i,4).setData(Qt.UserRole, float(it0.text(jl[2])))

            if i == 0:
                self.table4.item(i,5).setText("0.0")
                self.table4.item(i,5).setData(Qt.UserRole, 0.0)
            else:
                dph, ok = self.table4.item(i-1,5).data(Qt.UserRole).toFloat()
                ph0, ok = self.table4.item(i-1,4).data(Qt.UserRole).toFloat()
                ph1, ok = self.table4.item(i,4).data(Qt.UserRole).toFloat()
                dph = dph + ph1 - ph0
                if ph1 < ph0:
                    dph = dph + 2.0*np.pi*nu
                #print "Updating twiss:", i, dph
                self.table4.item(i,5).setData(Qt.UserRole, dph)
                self.table4.item(i,5).setText("%.5g" % dph)
            icor, ok = self.table4.item(i,0).data(Qt.UserRole).toInt()
            #c = self._cors[icor]
            #kick = self._cors[icor].get(self._field, unitsys=None)
            #self.table4.item(i,6).setData(Qt.UserRole, kick)
            #self.table4.item(i,6).setText("%.5g" % kick)
        #self.updateKickReadings(col=0)

    def clear(self):
        for i in range(self.table4.rowCount()):
            elemname = self.table4.item(i,0).data(Qt.DisplayRole).toString()
            it0 = self._corlst1.findItems(
                elemname, Qt.MatchExactly | Qt.MatchRecursive)[0]
            it0.setDisabled(False)
            for j in range(self._corlst1.columnCount()):
                it0.setForeground(j, Qt.black)
        self.table4.setRowCount(0)

    def updateCorReadings(self):
        for i in range(self.table4.rowCount()):
            icor, ok = self.table4.item(i,0).data(Qt.UserRole).toInt()
            cor = self._cors[icor]
            if self._field == "x":
                self.table4.item(i,6).setData(Qt.UserRole, self._x0[icor])
                self.table4.item(i,6).setText("%.5g" % self._x0[icor])
            elif self._field == "y":
                self.table4.item(i,6).setData(Qt.UserRole, self._y0[icor])
                self.table4.item(i,6).setText("%.5g" % self._y0[icor])
            kicksp = cor.get(self._field, handle="setpoint", unitsys=None)
            self.table4.item(i,7).setData(Qt.UserRole, float(kicksp))
            self.table4.item(i,7).setText("%.5g" % kicksp)
            kickrb = cor.get(self._field, handle="readback", unitsys=None)
            self.table4.item(i,9).setData(Qt.UserRole, float(kickrb))
            self.table4.item(i,9).setText("%.5g" % kickrb)


    def updateDbump(self, dkick):
        nrow = min(self.table4.rowCount(), len(dkick))
        for i in range(nrow):
            # dbump column is 8
            it = self.table4.item(i, 8)
            if dkick[i] is None:
                it.setData(Qt.DisplayRole, "")
                it.setData(Qt.UserRole, 0.0)
            else:
                it.setData(Qt.UserRole, float(dkick[i]))
                it.setData(Qt.DisplayRole, "{0}".format(dkick[i]))
        self.updateCorReadings()
        self.table4.resizeColumnsToContents()
        #print "(0,7)", self.table4.item(0, 7).data(Qt.UserRole).toFloat()
        #print "(0,7)", self.table4.item(0, 7).data(Qt.DisplayRole).toFloat()

    def applyKick(self):
        nrow = self.table4.rowCount()
        for i in range(nrow):
            icor, ok = self.table4.item(i,0).data(Qt.UserRole).toInt()
            cor = self._cors[icor]
            # Current SP: 7, dBump 8
            k0, ok = self.table4.item(i, 7).data(Qt.UserRole).toFloat()
            dk, ok = self.table4.item(i, 8).data(Qt.UserRole).toFloat()
            #print "Setting {0} {1}+{2} [A]".format(cor.name, k0, dk)
            cor.put(self._field, k0+dk, unitsys=None)

        # update the final readings
        self.updateCorReadings()

    def getTwiss(self):
        tw = {"s": [], "Alpha": [], "Beta": [],
              "Phi": [], "dPhi": []}
        nrow = self.table4.rowCount()
        for j in range(self.table4.columnCount()):
            header = self.table4.horizontalHeaderItem(j)
            if header.text() not in tw.keys():
                continue
            k = str(header.text())
            for i in range(nrow):
                it = self.table4.item(i, j)
                v0, ok0 = it.data(Qt.UserRole).toFloat()
                v1, ok1 = it.data(Qt.DisplayRole).toFloat()
                if ok0:
                    tw[k].append(v0)
                elif ok1:
                    tw[k].append(v1)
                else:
                    tw[k].append(np.nan)
        return tw

    def selectedCorrectors(self):
        ret = []
        for i in range(self.table4.rowCount()):
            icor, ok = self.table4.item(i,0).data(Qt.UserRole).toInt()
            ret.append(self._cors[icor])
        return ret

    def resetCorrectors(self):
        for i in range(self.table4.rowCount()):
            icor, ok = self.table4.item(i,0).data(Qt.UserRole).toInt()
            cor = self._cors[icor]
            if self._field == "x":
                kick = self._x0[icor]
            elif self._field == "y":
                kick = self._y0[icor]
            cor.put(self._field, kick, unitsys=None)


class BumpNCor(QtGui.QWidget):
    def __init__(self, cors, nmax, field, parent = None):
        super(BumpNCor, self).__init__(parent)
        self.corview = CorrectorViewer(cors, field, nmax=nmax)

        hbox3 = QtGui.QHBoxLayout()
        self.rdbxbump = QtGui.QRadioButton("X Bump")
        self.rdbybump = QtGui.QRadioButton("Y BUmp")
        self.rdbxbump.setChecked(True)
        hbox3.addWidget(self.rdbxbump)
        hbox3.addWidget(self.rdbybump)
        self.grpPlane = QtGui.QGroupBox("Plane")
        self.grpPlane.setLayout(hbox3)

        self.gboxBtn = QtGui.QGridLayout()
        btnClear  = QtGui.QPushButton("Clear")
        btnReset  = QtGui.QPushButton("Reset")
        btnZoomin = QtGui.QPushButton("Zoom In")
        btnApply  = QtGui.QPushButton("Apply")
        self.gboxBtn.addWidget(btnClear, 0, 1)
        self.gboxBtn.addWidget(btnReset, 1, 1)
        self.gboxBtn.addWidget(btnZoomin, 2, 1)
        self.gboxBtn.addWidget(btnApply, 3, 1)
        self.gboxBtn.setColumnStretch(1, 0)
        self.gboxBtn.setColumnStretch(0, 1)

        self.connect(self.rdbxbump, SIGNAL("clicked()"),
                     partial(self.changeField, "x"))
        self.connect(self.rdbybump, SIGNAL("clicked()"),
                     partial(self.changeField, "y"))
        self.connect(btnClear, SIGNAL("clicked()"), self.clear)
        self.connect(btnReset, SIGNAL("clicked()"),
                     self.corview.resetCorrectors)
        self.connect(btnApply, SIGNAL("clicked()"),
                     self.corview.applyKick)
        self.connect(btnZoomin, SIGNAL("clicked()"),
                     self._zoom_in)
        self._x0 = fget(cors, "x", handle="setpoint", unitsys=None)
        self._y0 = fget(cors, "y", handle="setpoint", unitsys=None)

    def clear(self):
        self.corview.clear()

    def changeField(self, field):
        if field not in ['x', 'y']:
            QtGui.QMessageBox.critical(
                self, "Local Orbit Bump",
                "ERROR: The field should be one of ['x', 'y']",
                QtGui.QMessageBox.Ok)
            return
        self.corview._field = field
        print("Change field to {0}".format(self.corview._field))
        self.corview.updateTwiss()
        self.corview.updateCorReadings()

    def _zoom_in(self):
        self.emit(SIGNAL("zoomInCorrectors(PyQt_PyObject)"),
                  self.corview.selectedCorrectors())

# Bump from corrector strength
class Bump3XCor(BumpNCor):
    def __init__(self, cors, parent = None):
        super(Bump3XCor, self).__init__(cors, 3, parent)
        self.xcor = QtGui.QComboBox()
        self.dxi = QtGui.QLineEdit("0.0")
        #self.loc = QtGui.QLineEdit()
        #self.lbl

        fmbox = QtGui.QFormLayout()
        fmbox.addRow("Indep. Cor", self.xcor)
        fmbox.addRow("dCor (raw)", self.dxi)
        #fmbox.addRow("location", self.loc)

        vbox1 = QtGui.QVBoxLayout()
        vbox1.addWidget(self.grpPlane)
        vbox1.addLayout(fmbox)

        vbox1.addStretch()
        vbox1.addLayout(self.gboxBtn)

        hbox1 = QtGui.QHBoxLayout()
        hbox1.addWidget(self.corview, 1)
        hbox1.addLayout(vbox1)
        self.setLayout(hbox1)

        self.connect(self.xcor, SIGNAL("currentIndexChanged(int)"),
                     partial(self.corview.updateDbump, [0.0, 0.0, 0.0]))
        self.connect(self.dxi, SIGNAL("returnPressed()"),
                     self._update_dbump)
        self.connect(self.corview, SIGNAL("correctorAdded(PyQt_PyObject)"),
                     self._add_corrector)

    def _add_corrector(self, cor):
        self.xcor.setDisabled(True)
        self.xcor.addItem(cor.name)
        self.xcor.setDisabled(False)

    def clear(self):
        self.xcor.setDisabled(True)
        self.xcor.clear()
        self.xcor.setDisabled(False)
        self.dxi.setText("0")
        BumpNCor.clear(self)

    def dx(self, tw, dxi, ibase = 0):
        if tw is None: return [0.0, 0.0, 0.0]
        if dxi == 0.0: return [0.0, 0.0, 0.0]

        if ibase < 0: return [0.0, 0.0, 0.0]

        bta, dph = tw['Beta'], tw["dPhi"]
        #print bta, dph
        cx21 = -np.sqrt(bta[0]/bta[1])*(np.sin(dph[2] - dph[0]) /
                                        np.sin(dph[2] - dph[1]))
        cx31 = -np.sqrt(bta[0]/bta[2])*(np.sin(dph[1] - dph[0]) /
                                        np.sin(dph[1] - dph[2]))

        fc = [1.0, cx21, cx31]
        return [v/fc[ibase]*dxi for v in fc]

    def _update_dbump(self):
        if len(self.corview.selectedCorrectors()) < 3:
            QtGui.QMessageBox.critical(
                self, "Local Orbit Bump",
                "ERROR: please select 3 correctors.",
                QtGui.QMessageBox.Ok)
            return
        tw = self.corview.getTwiss()
        if not self.dxi.text():
            QtGui.QMessageBox.critical(
                self, "3 Cor Orbit Bump",
                "ERROR: Set reference corrector current first",
                QtGui.QMessageBox.Ok)
            return
        dkick = self.dx(tw, float(self.dxi.text()),
                        ibase = self.xcor.currentIndex())
        self.corview.updateDbump(dkick)

    def changeField(self, field):
        super(Bump3XCor, self).changeField(field)
        self.corview.updateDbump([0.0, 0.0, 0.0])
        self.clear()

# Bump from a location
class Bump3XSrc(BumpNCor):
    def __init__(self, cors, parent = None):
        super(Bump3XSrc, self).__init__(cors, 3, parent)
        self.loc = QtGui.QLineEdit()
        self.dxi = QtGui.QLineEdit("0.0")

        self.lblBeta = QtGui.QLabel()
        self.lblAlfa = QtGui.QLabel()
        self.lblPhi  = QtGui.QLabel()
        fmbox = QtGui.QFormLayout()
        fmbox.addRow("Location", self.loc)
        fmbox.addRow("dX (dY)", self.dxi)
        fmbox.addRow("Beta", self.lblBeta)
        fmbox.addRow("Alpha", self.lblAlfa)
        fmbox.addRow("Phi", self.lblPhi)
        vbox1 = QtGui.QVBoxLayout()
        vbox1.addWidget(self.grpPlane)
        vbox1.addLayout(fmbox)
        lbl = QtGui.QLabel(
            """<font color="red">WARNING:</font>The unit of dX(dY) is not """
            """calibrated, please take a look at the calculated current """
            """change before applying them""")
        lbl.setFixedWidth(300)
        lbl.setWordWrap(True)
        vbox1.addWidget(lbl)

        vbox1.addLayout(self.gboxBtn)

        hbox1 = QtGui.QHBoxLayout()
        hbox1.addWidget(self.corview, 1)
        hbox1.addLayout(vbox1)
        self.setLayout(hbox1)

        self.connect(self.loc, SIGNAL("returnPressed()"),
                     self._update_dx)
        self.connect(self.dxi, SIGNAL("returnPressed()"),
                     self._update_dx)
        self.connect(self.loc, SIGNAL("textEdited(QString)"),
                     self._clear_dkick)
        self.connect(self.dxi, SIGNAL("textEdited(QString)"),
                     self._clear_dkick)

    def clear(self):
        BumpNCor.clear(self)
        self.lblBeta.setText("")
        self.lblAlfa.setText("")
        self.lblPhi.setText("")

    def _clear_dkick(self):
        self.lblBeta.setText("")
        self.lblAlfa.setText("")
        self.lblPhi.setText("")
        self.corview.updateDbump([None] * 3)

    def changeField(self, field):
        super(Bump3XSrc, self).changeField(field)
        self.corview.updateDbump([0.0, 0.0, 0.0])
        self.clear()

    def dx(self, tw, xt = 0.0):
        #print tw, self.sender()
        if not tw: return [0.0, 0.0, 0.0]
        s1, s2, s3, st = tw["s"][:4]

        if st < s1 or st > s3:
            QtGui.QMessageBox.critical(
                self, "Local Orbit Bump",
                "ERROR: The position should be lcally within 3 correctors: ["
                "{0}, {1}].".format(s1, s2),
                QtGui.QMessageBox.Ok)
            return [0.0, 0.0, 0.0]

        bt1, bt2, bt3, bt  = tw["Beta"][:4]
        af1, af2, af3, at  = tw["Alpha"][:4]
        ph1, ph2, ph3, pht = tw["Phi"][:4]
        dph1, dph2, dph3 = tw["dPhi"][:3]

        cx21 = -np.sqrt(bt1/bt2)*(np.sin(dph3 - dph1) /
                                np.sin(dph3 - dph2))
        cx31 = -np.sqrt(bt1/bt3)*(np.sin(dph2 - dph1) /
                                  np.sin(dph2 - dph3))

        fc = [1.0, cx21, cx31]

        if st < s2:
            th1 = xt/(np.sqrt(bt1*bt)*np.sin(pht - ph1))
            return [th1, th1*fc[1], th1*fc[2]]
        elif st < s3:
            th3 = xt/(np.sqrt(bt3*bt)*np.sin(ph3 - pht))
            return [th3/cx31, th3/cx31*cx21, th3]
        else:
            return [0.0, 0.0, 0.0]

    def _update_dx(self):
        if len(self.corview.selectedCorrectors()) < 3:
            QtGui.QMessageBox.critical(
                self, "Local Orbit Bump",
                "ERROR: please select 3 correctors.",
                QtGui.QMessageBox.Ok)
            return
        tw = self.corview.getTwiss()
        if not self.loc.text() or not self.dxi.text():
            return
        st = float(self.loc.text())
        xt = float(self.dxi.text())
        if self.rdbxbump.isChecked():
            bt, at, pht = getTwissAt(st, ["betax", "alphax", "phix"])
        elif self.rdbybump.isChecked():
            bt, at, pht = getTwissAt(st, ["betay", "alphay", "phiy"])
        tw["s"].append(st)
        tw["Beta"].append(bt)
        tw["Alpha"].append(at)
        tw["Phi"].append(pht)
        if pht > tw["Phi"][1]:
            tw["dPhi"].append(pht - tw["Phi"][1] + tw["dPhi"][1])
        else:
            tw["dPhi"].append(tw["Phi"][2] - (tw["Phi"][2] - pht))
        self.lblBeta.setText("{0}".format(bt))
        self.lblAlfa.setText("{0}".format(at))
        self.lblPhi.setText("{0}".format(pht))
        vals = self.dx(tw, xt)
        #print "New dkick:", vals
        self.corview.updateDbump(vals)
        #self.emit(SIGNAL("dKickUpdated(PyQt_PyObject)"), vals)


class Bump4XCor(BumpNCor):
    def __init__(self, cors, parent = None):
        super(Bump4XCor, self).__init__(cors, 4, parent)
        self.dxi1 = QtGui.QLineEdit("0.0")
        self.dxi2 = QtGui.QLineEdit("0.0")
        fmbox = QtGui.QFormLayout()
        fmbox.addRow("dX (dY) 1", self.dxi1)
        fmbox.addRow("dX (dY) 2", self.dxi2)

        vbox1 = QtGui.QVBoxLayout()
        vbox1.addWidget(self.grpPlane)
        vbox1.addLayout(fmbox)

        vbox1.addStretch()
        vbox1.addLayout(self.gboxBtn)

        hbox1 = QtGui.QHBoxLayout()
        hbox1.addWidget(self.corview, 1)
        hbox1.addLayout(vbox1)
        self.setLayout(hbox1)

        self.connect(self.dxi1, SIGNAL("returnPressed()"),
                     self._update_dx)
        self.connect(self.dxi2, SIGNAL("returnPressed()"),
                     self._update_dx)

    def clear(self):
        BumpNCor.clear(self)
        self.dxi1.setText("")
        self.dxi2.setText("")

    def changeField(self, field):
        super(Bump4XCor, self).changeField(field)
        self.corview.updateDbump([0.0, 0.0, 0.0, 0.0])
        self.dxi1.setText("")
        self.dxi2.setText("")

    def dx(self, tw, dxi1, dxi2):
        bta = tw["Beta"]
        dph = tw["dPhi"]
        c1 = np.sqrt(bta[0])*dxi1
        c2 = np.sqrt(bta[1])*dxi2
        dp41, dp42 = np.sin(dph[3] - dph[0]), np.sin(dph[3] - dph[1])
        dp31, dp32 = np.sin(dph[2] - dph[0]), np.sin(dph[2] - dph[1])
        dp43 = np.sin(dph[3] - dph[2])
        dxi3 = -(c1*dp41 + c2*dp42)/dp43/np.sqrt(bta[2])
        dxi4 = (c1*dp31 + c2*dp32)/dp43/np.sqrt(bta[3])
        return [dxi1, dxi2, dxi3, dxi4]

    def _update_dx(self):
        if len(self.corview.selectedCorrectors()) < 4:
            QtGui.QMessageBox.critical(
                self, "Local Orbit Bump",
                "ERROR: please select 4 correctors.",
                QtGui.QMessageBox.Ok)
            return
        tw = self.corview.getTwiss()
        if not self.dxi1.text() or not self.dxi2.text():
            return
        dkick = self.dx(tw, float(self.dxi1.text()), float(self.dxi2.text()))
        self.corview.updateDbump(dkick)


class Bump4XSrc(BumpNCor):
    def __init__(self, cors, parent = None):
        super(Bump4XSrc, self).__init__(cors, 4, parent)
        self.loc = QtGui.QLineEdit("")
        self.dxi = QtGui.QLineEdit("0.0")
        self.ang = QtGui.QLineEdit("0.0")
        fmbox = QtGui.QFormLayout()
        fmbox.addRow("Location", self.loc)
        fmbox.addRow("dX (dY)",  self.dxi)
        fmbox.addRow("Angle",    self.ang)

        vbox1 = QtGui.QVBoxLayout()
        vbox1.addWidget(self.grpPlane)
        vbox1.addLayout(fmbox)
        lbl = QtGui.QLabel(
            """<font color="red">WARNING:</font>The unit of dX and dTheta """
            """are not calibrated, please take a look at the calculated """
            """current change before applying them""")
        lbl.setFixedWidth(300)
        lbl.setWordWrap(True)
        vbox1.addWidget(lbl)

        vbox1.addStretch()
        vbox1.addLayout(self.gboxBtn)

        hbox1 = QtGui.QHBoxLayout()
        hbox1.addWidget(self.corview, 1)
        hbox1.addLayout(vbox1)
        self.setLayout(hbox1)

        self.connect(self.loc, SIGNAL("returnPressed()"),
                     self._update_dx)
        self.connect(self.dxi, SIGNAL("returnPressed()"),
                     self._update_dx)
        self.connect(self.ang, SIGNAL("returnPressed()"),
                     self._update_dx)

    def dx(self, tw, dx, dxp):
        a0,  a1,  a2,  a3,  at  = tw["Alpha"]
        b0,  b1,  b2,  b3,  bt  = tw["Beta"]
        ph0, ph1, ph2, ph3, pht = tw["dPhi"]

        dt1 = dx*(np.cos(pht-ph1) - at*np.sin(pht-ph1))/\
            np.sqrt(bt*b0)*np.sin(ph1-ph0) - \
            dxp*np.sqrt(bt/b0)*np.sin(pht-ph1)/np.sin(ph1-ph0)
        dt2 = -dx*(np.cos(pht-ph0) - at*np.sin(pht-ph0))/\
            np.sqrt(bt*b1)*np.sin(ph1-ph0) + \
            dxp*np.sqrt(bt/b1)*np.sin(pht-ph0)/np.sin(ph1-ph0)
        dt3 = -dx*(np.cos(ph3-pht) - at*np.sin(pht-ph3))/\
            np.sqrt(bt*b2)*np.sin(ph3-ph2) + \
            dxp*np.sqrt(bt/b2)*np.sin(pht-ph3)/np.sin(ph3-ph2)
        dt4 = dx*(np.cos(ph2-pht) - at*np.sin(pht-ph2))/\
            np.sqrt(bt*b3)*np.sin(ph3-ph2) - \
            dxp*np.sqrt(bt/b3)*np.sin(pht-ph1)/np.sin(ph3-ph2)

        # same kick for theta2
        return [dt1, dt2, dt3, dt4]

    def changeField(self, field):
        super(Bump4XSrc, self).changeField(field)
        self.corview.updateDbump([0.0, 0.0, 0.0, 0.0])

    def _update_dx(self):
        if len(self.corview.selectedCorrectors()) < 4:
            QtGui.QMessageBox.critical(
                self, "Local Orbit Bump",
                "ERROR: please select 4 correctors.",
                QtGui.QMessageBox.Ok)
            return
        tw = self.corview.getTwiss()
        try:
            st  = float(self.loc.text())
            dxt = float(self.dxi.text())
            ang = float(self.ang.text())
        except:
            return
        if self.rdbxbump.isChecked():
            bt, at, pht = getTwissAt(st, ["betax", "alphax", "phix"])
        elif self.rdbybump.isChecked():
            bt, at, pht = getTwissAt(st, ["betay", "alphay", "phiy"])
        tw["s"].append(st)
        tw["Beta"].append(bt)
        tw["Alpha"].append(at)
        tw["Phi"].append(pht)
        if pht > tw["Phi"][1]:
            tw["dPhi"].append(pht - tw["Phi"][1] + tw["dPhi"][1])
        else:
            tw["dPhi"].append(tw["Phi"][2] - (tw["Phi"][2] - pht))
        dkick = self.dx(tw, dxt, ang)
        self.corview.updateDbump(dkick)


class OrbitCorrDlg(QDialog):
    def __init__(self, bpms = None, cors = None, parent = None):
        super(OrbitCorrDlg, self).__init__(parent)
        # add bpms
        bpmls = bpms
        if bpms is None:
            bpmls = getElements("BPM")
        bpmls = [bpm for bpm in bpmls if bpm.isEnabled()]
        pvx = [bpm.pv(field="x", handle="readback")[0] for bpm in bpmls]
        pvy = [bpm.pv(field="y", handle="readback")[0] for bpm in bpmls]
        #
        #self._update_current_orbit()

        s = [bpm.sb for bpm in bpmls]
        self.bpm_plot = ApCaArrayPlot([pvx, pvy], x = [s, s])
        magprof = getBeamlineProfile()
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

        #self.bpm_plot._cheat = [Qwt.QwtPlotCurve(), Qwt.QwtPlotCurve()]
        #self.bpm_plot._cheat[0].setTitle("_CHEAT_ X")
        #self.bpm_plot._cheat[1].setTitle("_CHEAT_ Y")
        #self.bpm_plot._cheat[0].attach(self.bpm_plot)
        #self.bpm_plot._cheat[1].attach(self.bpm_plot)
        #self.bpm_plot._set_symbol(self.bpm_plot._cheat[0],
        #                          Qwt.QwtSymbol.Triangle, dsize=2)
        #self.bpm_plot._set_symbol(self.bpm_plot._cheat[1],
        #                          Qwt.QwtSymbol.Diamond, dsize=2)
        #self.bpm_plot.showCurve(self.bpm_plot._cheat[0], False)
        #self.bpm_plot.showCurve(self.bpm_plot._cheat[1], False)
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
                                      labels=["HCOR Sp", "VCOR Sp"])
        #magprof = aphla.getBeamlineProfile()
        self.cor_plot.setMagnetProfile(magprof)
        self.cor_plot.setContentsMargins(12, 10, 10, 10)
        #self.cor_plot.setMinimumHeight(200)
        #self.cor_plot.setMaximumHeight(250)
        #print s, pvx

        # add twiss plots
        self._twiss = getTwiss("*", ["s", "betax", "betay", "etax"])
        #for i in range(len(self._twiss)):
        #    print i, self._twiss[i,0], self._twiss[i,1]

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
        cbetax.setData(self._twiss[:,0], self._twiss[:,1])
        cbetay.setData(self._twiss[:,0], self._twiss[:,2])
        cetax.setData(self._twiss[:,0], 10.0*self._twiss[:,3])
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
        tabs.addTab(self.tw_plot, "Twiss (Design)")
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

        tab_bump3xcor = Bump3XCor(corls, "x")
        tab_bump3xsrc = Bump3XSrc(corls, "x")
        tab_bump4xcor = Bump4XCor(corls, "x")
        tab_bump4xsrc = Bump4XSrc(corls, "x")
        #plots=[self.bpm_plot, self.cor_plot, self.tw_plot])
        #self.connect(tab_nbump_cor,
        #             SIGNAL("correctorChanged(PyQt_PyObject)"),
        #             self._update_corr_plot)
        tabs.addTab(tab_bump3xcor, "3 Cors. dI")
        tabs.addTab(tab_bump3xsrc, "3 Cors. dX")
        tabs.addTab(tab_bump4xcor, "4 Cors. dI")
        tabs.addTab(tab_bump4xsrc, "4 Cors. dX dTheta")
        layout.addWidget(tabs, 3)

        self.connect(tab_bump3xcor, SIGNAL("zoomInCorrectors(PyQt_PyObject)"),
                     self._zoom_in_cors)
        self.connect(tab_bump3xsrc, SIGNAL("zoomInCorrectors(PyQt_PyObject)"),
                     self._zoom_in_cors)
        self.connect(tab_bump4xcor, SIGNAL("zoomInCorrectors(PyQt_PyObject)"),
                     self._zoom_in_cors)
        self.connect(tab_bump4xsrc, SIGNAL("zoomInCorrectors(PyQt_PyObject)"),
                     self._zoom_in_cors)

        self.connect(tab_bump3xcor, SIGNAL("clearCorrectors(PyQt_PyObject)"),
                     self._clear_cors)
        self.connect(tab_bump3xsrc, SIGNAL("clearCorrectors(PyQt_PyObject)"),
                     self._clear_cors)
        self.connect(tab_bump4xcor, SIGNAL("clearCorrectors(PyQt_PyObject)"),
                     self._clear_cors)
        self.connect(tab_bump4xsrc, SIGNAL("clearCorrectors(PyQt_PyObject)"),
                     self._clear_cors)

        #hln = QtGui.QFrame()
        #hln.setLineWidth(3)
        #hln.setFrameStyle(QtGui.QFrame.Sunken)
        #hln.setFrameShape(QtGui.QFrame.HLine)
        #layout.addWidget(hln)

        # the cheat button
        #hbox = QHBoxLayout()
        #hbox.addStretch()
        #btn = QPushButton("__CHEAT__")
        #self.connect(btn, SIGNAL("clicked()"), self._cheat)
        #hbox.addWidget(btn)
        #layout.addLayout(hbox)

        self.setLayout(layout)
        #self.update_orbit = update_orbit
        #self._x0 = tuple(x)  # save for reset
        #self._y0 = tuple(y)  # save for reset
        #self.val = [s, x, y]
        self.setMinimumWidth(1000)
        self.setWindowFlags(Qt.Window)
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

    def _cheat(self):
        s = catools.caget('V:2-SR-BI{POS}-I')
        x = catools.caget('V:2-SR-BI{ORBIT}X-I')
        y = catools.caget('V:2-SR-BI{ORBIT}Y-I')
        p = self.bpm_plot
        p._cheat[0].setData(s, x)
        p._cheat[1].setData(s, y)
        p.showCurve(p._cheat[0], True)
        p.showCurve(p._cheat[1], True)
        p.replot()

    def _zoom_in_cors(self, corls):
        mks = [(c.name, c.sb) for c in corls]
        s0 = min([c.sb for c in corls])
        s1 = max([c.se for c in corls])
        ds = (s1 - s0) / 10.0
        self.bpm_plot.setMarkers(mks)
        self.bpm_plot.setAxisScale(Qwt.QwtPlot.xBottom, s0-ds, s1+ds)
        self.bpm_plot.replot()
        self.cor_plot.setMarkers(mks)
        self.cor_plot.replot()
        self.tw_plot.setMarkers(mks)
        self.tw_plot.replot()

    def _clear_cors(self, corls):
        self.bpm_plot.setMarkers([])
        self.bpm_plot.replot()
        self.cor_plot.setMarkers([])
        self.cor_plot.replot()
        self.tw_plot.setMarkers([])
        self.tw_plot.replot()


    def _help(self):
        print("HELP")

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

    def closeEvent(self, e):
        self.bpm_plot.close()
        self.cor_plot.close()
        self.tw_plot.close()
        e.accept()


if __name__ == "__main__":
    import aphla as ap
    #ap.machines.load("nsls2v2")
    ap.machines.load("nsls2")
    bpms = ap.getElements("BPM")
    cors = ap.getElements("COR")
    bpms[1].setEnabled(False)
    cors[1].setEnabled(False)

    form = OrbitCorrDlg(bpms)
    #form = OrbitCorrGeneral(bpms, cors)
    #form = OrbitCorrNBumps(bpms, cors)
    #form = CorrectorViewer(cors)
    #form = Bump3XCor(cors)
    #form = Bump3XSrc(cors)
    form.resize(1000, 400)
    form.setWindowTitle("Create Local Bump")
    form.setWindowFlags(Qt.Window)
    form.show()
    #form.reloadElements("*")
    #app.exec_()
    cothread.WaitForQuit()
