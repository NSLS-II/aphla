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
from aphla import (catools, getElements, setLocalBump,
                   getTwiss, getTunes, getTwissAt)

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
            self.table.setItem(i, 2, QTableWidgetItem("%.4f" % self._twiss[i,1]))
            self.table.setItem(i, 3, QTableWidgetItem("%.4f" % self._twiss[i,2]))
            self.table.setItem(i, 4, QTableWidgetItem("%.4f" % self._twiss[i,3]))

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


# Bump from corrector strength
class Bump3XCor(QtGui.QWidget):
    def __init__(self, parent = None):
        super(Bump3XCor, self).__init__(parent)
        self._twiss = None
        self.xcor = QtGui.QComboBox()
        self.dxi = QtGui.QLineEdit("0.0")
        fmbox = QtGui.QFormLayout()
        fmbox.addRow("Indep. Cor", self.xcor)
        fmbox.addRow("dKick", self.dxi)
        self.setLayout(fmbox)

        self.connect(self.xcor, SIGNAL("currentIndexChanged(int)"),
                     self._update_dx)
        self.connect(self.dxi, SIGNAL("editingFinished()"),
                     self._update_dx)

    def setElements(self, names):
        self.xcor.clear()
        self.xcor.addItems(names)

    def setTwiss(self, tw):
        self._twiss = tw

    def dx(self):
        if self._twiss is None: return [0.0, 0.0, 0.0]
        x0 = float(self.dxi.text())
        if x0 == 0.0: return [0.0, 0.0, 0.0]

        i0 = self.xcor.currentIndex()        
        if i0 == -1: return [0.0, 0.0, 0.0]

        bta = self._twiss['beta']
        dph = self._twiss["dphi"]
        #print bta, dph
        cx21 = -np.sqrt(bta[0]/bta[1])*(np.sin(dph[2] - dph[0]) / 
                                        np.sin(dph[2] - dph[1]))
        cx31 = -np.sqrt(bta[0]/bta[2])*(np.sin(dph[1] - dph[0]) / 
                                        np.sin(dph[1] - dph[2]))

        fc = [1.0, cx21, cx31]
        return [v/fc[i0]*x0 for v in fc]

    def _update_dx(self):
        if self.isEnabled():
            vals = self.dx()
            self.emit(SIGNAL("dKickUpdated(PyQt_PyObject)"), vals)
        else:
            print "New dkick: disabled"

# Bump from a location
class Bump3XSrc(QtGui.QWidget):
    def __init__(self, parent = None):
        super(Bump3XSrc, self).__init__(parent)
        self._twiss = None
        self.loc = QtGui.QLineEdit()
        self.dxi = QtGui.QLineEdit("0.0")
        fmbox = QtGui.QFormLayout()
        fmbox.addRow("Location", self.loc)
        fmbox.addRow("dX (dY)", self.dxi)
        self.setLayout(fmbox)

        self.connect(self.loc, SIGNAL("editingFinished()"),
                     self._update_dx)
        self.connect(self.dxi, SIGNAL("editingFinished()"),
                     self._update_dx)

    def setTwiss(self, tw):
        self._twiss = tw

    def dx(self):
        if self._twiss is None or not self.loc.text():
            return [0.0, 0.0, 0.0]
        si = float(self.loc.text())
        xi = float(self.dxi.text())
        s1, s2, s3 = self._twiss["s"]
        b1, b2, b3 = self._twiss["beta"]
        a1, a2, a3 = self._twiss["alpha"]
        ph1, ph2, ph3 = self._twiss["phi"]
        dph1, dph2, dph3 = self._twiss["dphi"]
        if si < s1 or si > s3: return [0.0, 0.0, 0.0]

        cx21 = -np.sqrt(b1/b2)*(np.sin(dph3 - dph1) / 
                                np.sin(dph3 - dph2))
        cx31 = -np.sqrt(b1/b3)*(np.sin(dph2 - dph1) / 
                                np.sin(dph2 - dph3))

        fc = [1.0, cx21, cx31]
        if self._twiss['plane'] in ["y", "Y"]:
            col = ["alphay", "betay", "phiy"]
        else:
            col = ["alphax", "betax", "phix"]
        aft, bt, pht = ap.getTwissAt(si, col)

        print bt, aft, pht, self._twiss
        if si < s2:
            th1 = xi/(np.sqrt(b1*bt)*np.sin(pht - ph1))
            return [th1, th1*fc[1], th1*fc[2]]
        elif si < s3:
            th3 = xi/(np.sqrt(b3*bt)*np.sin(ph3 - pht))
            return [th3/cx31, th3/cx31*cx21, th3]
        else:
            return [0.0, 0.0, 0.0]

    def _update_dx(self):
        vals = self.dx()
        print "New dkick:", vals, self._twiss
        self.emit(SIGNAL("dKickUpdated(PyQt_PyObject)"), vals)


class Bump4XCor(QtGui.QWidget):
    def __init__(self, parent = None):
        super(Bump4XCor, self).__init__(parent)
        self.dxi1 = QtGui.QLineEdit("0.0")
        self.dxi2 = QtGui.QLineEdit("0.0")
        fmbox = QtGui.QFormLayout()
        fmbox.addRow("dX (dY) 1", self.dxi1)
        fmbox.addRow("dX (dY) 2", self.dxi2)
        self.setLayout(fmbox)

    def dx(self):
        return [0.0, 0.0, 0.0, 0.0]


class Bump4XSrc(QtGui.QWidget):
    def __init__(self, parent = None):
        super(Bump4XSrc, self).__init__(parent)
        self.loc = QtGui.QLineEdit("")
        self.ang = QtGui.QLineEdit("0.0")
        fmbox = QtGui.QFormLayout()
        fmbox.addRow("Location", self.loc)
        fmbox.addRow("Angle",    self.ang)
        self.setLayout(fmbox)

    def dx(self):
        return [0.0, 0.0, 0.0, 0.0]


class OrbitCorrNBumps(QtGui.QWidget):
    def __init__(self, bpms, cors, plots = [], parent = None):
        super(OrbitCorrNBumps, self).__init__(parent)
        self.bpm_all, self.cor_all = bpms, cors
        self.cors = []
        self.__updating = False
        self._plots = plots
        self._corlst1 = QtGui.QTreeWidget()
        self._header = dict([("Element", 0), ("Family", 1), ("s [m]", 2),
                             ("Alpha X", 3), ("Alpha Y", 4), ("Beta X", 5),
                             ("Beta Y", 6), ("Phi X", 7), ("Phi Y", 8),
                             ("Eta X", 9)])
        self._twiss = np.zeros((len(self.cor_all), 8), 'd')
        self._tunes = getTunes(source="database")
        self._corlst1.setColumnCount(len(self._header))
        self._corlst1.setHeaderLabels(
            sorted(self._header, key=self._header.get))
        prevcell = None
        for i,c in enumerate(self.cor_all):
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
        #self._corlst1.resizeColumnToContents(1)
        #self._corlst1.resizeColumnToContents(2)
        self._corlst1.setColumnWidth(0, 150)
        self._corlst1.expandAll()

        vbox1 = QtGui.QVBoxLayout()
        vbox1.addWidget(self._corlst1, 1)

        #self.elemlst.setSelectionMode(QAbstractItemView.MultiSelection)
        columns = ['Corrector', 's', 'Alpha', 'Beta',
                   'Phi', "dPhi", "Initial Kick", "dKick",
                   "Final Kick (set)", "Final Kick (read)"]
        self.table4 = QTableWidget(4, len(columns))
        #self.table4.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        hdview = QHeaderView(Qt.Horizontal)
        self.table4.setHorizontalHeaderLabels(columns)
        for i in range(4):
            for j in range(len(columns)):
                it = QTableWidgetItem()
                if j > 0: it.setTextAlignment(
                    Qt.AlignRight | Qt.AlignVCenter)
                if columns[j] != "dKick":
                    it.setFlags(it.flags() & (~Qt.ItemIsEditable))
                self.table4.setItem(i, j, it)
        #self.table4.resizeColumnsToContents()
        self.table4.horizontalHeader().setStretchLastSection(True)
        hrow = self.table4.rowHeight(0)
        htbl = (hrow * 4) + self.table4.horizontalHeader().height() +\
            2*self.table4.frameWidth()
        self.table4.setMinimumHeight(htbl + 10)
        self.table4.setMaximumHeight(htbl + 15)
        self.table4.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        vbox1.addWidget(self.table4, 0)

        hbox1 = QtGui.QHBoxLayout()
        hbox1.addLayout(vbox1, 2)

        hbox3 = QtGui.QHBoxLayout()
        self.rdbxbump = QtGui.QRadioButton("X Bump")
        self.rdbybump = QtGui.QRadioButton("Y BUmp")
        self.rdbxbump.setChecked(True)
        hbox3.addWidget(self.rdbxbump)
        hbox3.addWidget(self.rdbybump)
        grp1 = QtGui.QGroupBox("Plane")
        grp1.setLayout(hbox3)

        # 3 bumps
        self.bump_tabs = QtGui.QTabWidget()
        b3xcor = Bump3XCor()
        self.bump_tabs.addTab(b3xcor, "3Cor")
        self.connect(b3xcor, SIGNAL("dKickUpdated(PyQt_PyObject)"),
                     self._set_cor)
        b3xsrc = Bump3XSrc()
        self.bump_tabs.addTab(b3xsrc, "3Cor Src")
        self.connect(b3xsrc, SIGNAL("dKickUpdated(PyQt_PyObject)"),
                     self._set_cor)
        b4xcor = Bump4XCor()
        self.bump_tabs.addTab(b4xcor, "4Cor")
        b4xsrc = Bump4XSrc()
        self.bump_tabs.addTab(b4xsrc, "4Cor Src")

        fmbox = QtGui.QFormLayout()
        self.src = QtGui.QLineEdit()
        self.src.setValidator(QtGui.QDoubleValidator())
        self.src_x = QtGui.QLineEdit()
        self.src_xp = QtGui.QLineEdit()
        fmbox.addRow("Location", self.src)
        fmbox.addRow("Displacement", self.src_x)
        fmbox.addRow("Angle", self.src_xp)

        grp2 = QtGui.QGroupBox("Source Point")
        grp2.setLayout(fmbox)

        vbox2 = QtGui.QVBoxLayout()
        vbox2.addWidget(grp1)
        vbox2.addWidget(self.bump_tabs)
        vbox2.addStretch()
        gbox4 = QtGui.QGridLayout()
        btnClear = QtGui.QPushButton("Clear")
        btnZoomin = QtGui.QPushButton("Zoom In")
        btnApply  = QtGui.QPushButton("Apply")
        btnCheat = QtGui.QPushButton("_CHEAT_")
        gbox4.addWidget(btnClear, 0, 1)
        gbox4.addWidget(btnZoomin, 1, 1)
        gbox4.addWidget(btnApply, 2, 1)
        gbox4.addWidget(btnCheat, 3, 1)
        gbox4.setColumnStretch(1, 0)
        gbox4.setColumnStretch(0, 1)
        vbox2.addLayout(gbox4)
        hbox1.addLayout(vbox2)
        self.setLayout(hbox1)

        self.connect(btnClear, SIGNAL("clicked()"), self._clear_correctors)
        self.connect(btnZoomin, SIGNAL("clicked()"), self._zoom_in_plots)
        self.connect(btnApply, SIGNAL("clicked()"), self._apply_bump)
        self.connect(btnCheat, SIGNAL("clicked()"), self._cheat)
        self.connect(self._corlst1, SIGNAL("doubleClicked(QModelIndex)"),
                     self.addCorrector)
        #self.connect(self.src, SIGNAL("returnPressed()"),
        #             self._calc_source)
        #self.connect(self.table4, SIGNAL("cellChanged(int, int)"),
        #             self.updateTable)

        #self.connect(self.table4, SIGNAL("doubleClicked(QModelIndex)"),
        #             self.delCorrector)

    def _set_cor(self, vals):
        print "Received:", vals
        if vals is None: return
        for i,v in enumerate(vals):
            self.table4.item(i,7).setData(Qt.DisplayRole, "%.5f" % v)
        self.table4.resizeColumnsToContents()

    def _clear_correctors(self):
        self.cors = []
        for i in range(self.table4.rowCount()):
            for j in range(self.table4.columnCount()):
                self.table4.item(i,j).setData(Qt.DisplayRole, "")
        self.emit(SIGNAL("correctorChanged(PyQt_PyObject)"), self.cors)

    def _calc_source(self):
        st = float(self.src.text())
        self.src_x.setText(self.src_x.text() + QtCore.QString(" ??"))
        self.src_xp.setText(self.src_xp.text() + QtCore.QString(" ??"))
        if len(self.cors) == 3:
            s = [self.table4.item(i, 1).data(Qt.DisplayRole).toFloat()[0]
                  for i in range(3)]
            a = [self.table4.item(i, 2).data(Qt.DisplayRole).toFloat()[0]
                 for i in range(3)]
            b = [self.table4.item(i, 3).data(Qt.DisplayRole).toFloat()[0]
                 for i in range(3)]
            ph = [self.table4.item(i, 4).data(Qt.DisplayRole).toFloat()[0]
                  for i in range(3)]
            dth = [self.table4.item(i, 8).data(Qt.DisplayRole).toFloat()[0]
                   for i in range(3)]
            if self.rdbxbump.isChecked():
                bt, at, pht = getTwissAt(st, ["betax", "alphax", "phix"])
            elif self.rdbybump.isChecked():
                bt, at, pht = getTwissAt(st, ["betay", "alphay", "phiy"])
            #print pht, ph, dth
            if st > s[0] and st < s[1]:
                dx = dth[0]*np.sqrt(b[0]*bt)*np.sin(pht - ph[0])
                self.src_x.setText("%.5f" % dx)
                dxp = dth[0]*np.sqrt(b[0]/bt)*(np.cos(pht - ph[0]) -
                                               at*np.sin(pht-ph[0]))
                self.src_xp.setText("%.5f" % dxp)

    def _cheat(self):
        s = aphla.catools.caget('V:2-SR-BI{POS}-I')
        x = aphla.catools.caget('V:2-SR-BI{ORBIT}X-I')
        y = aphla.catools.caget('V:2-SR-BI{ORBIT}Y-I')
        p = self._plots[0]
        p._cheat[0].setData(s, x)
        p._cheat[1].setData(s, y)
        p.showCurve(p._cheat[0], True)
        p.showCurve(p._cheat[1], True)
        p.replot()

    def addCorrector(self, idx):
        #['Corrector', 's', 'Beta X', 'Beta Y', 'Phi X', 'Phi Y',
        #     "dPhiX", "dPhiY", "dX", "dY", "X", "Y"])
        if not self._corlst1.selectedItems(): return
        if len(self.cors) == 4: return
        it0 = self._corlst1.selectedItems()[-1]
        #it0.setForeground(0, Qt.blue)
        icor, ok = it0.data(0, Qt.UserRole).toInt()
        newc = self.cor_all[icor]
        i = len(self.cors)
        self.table4.item(i,0).setData(Qt.UserRole, icor)
        for j,h in [(0, "Element"), (1, "s [m]")]:
            self.table4.item(i,j).setData(Qt.DisplayRole,
                                          it0.text(self._header[h]))
        if self.rdbxbump.isChecked():
            jl = [self._header[h] for h in ["Alpha X", "Beta X", "Phi X"]]
            nu = self._tunes[0]
            kick = newc.x
        elif self.rdbybump.isChecked():
            jl = [self._header[h] for h in ["Alpha Y", "Beta Y", "Phi Y"]]
            nu = self._tunes[1]
            kick = newc.y
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
            print i, dph
            self.table4.item(i,5).setData(Qt.UserRole, dph)
            self.table4.item(i,5).setText("%.5g" % dph)
        self.table4.item(i,6).setData(Qt.UserRole, kick)
        self.table4.item(i,6).setText("%.5g" % kick)

        self.table4.resizeColumnsToContents()
        self.cors.append(newc)
        tw = {'s': [], 'beta': [], 'phi': [], 'alpha': [], 'dphi': [],
              'plane': "X"}
        for i in range(len(self.cors)):
            j, ok = self.table4.item(i,0).data(Qt.UserRole).toInt()
            tw['s'].append(self._twiss[j,0])
            if self.rdbxbump.isChecked():
                tw['alpha'].append(self._twiss[j,1])
                tw['beta'].append( self._twiss[j,3])
                tw['phi'].append(  self._twiss[j,5])
                tw["plane"] = "X"
            elif self.rdbybump.isChecked():
                tw['alpha'].append(self._twiss[j,2])
                tw['beta'].append( self._twiss[j,4])
                tw['phi'].append(  self._twiss[j,6])
                tw["plane"] = "Y"
            d, ok = self.table4.item(i,5).data(Qt.UserRole).toFloat()
            tw['dphi'].append(d)
        #print tw
        for i in range(self.bump_tabs.count()):
            wi = self.bump_tabs.widget(i)
            if isinstance(wi, Bump3XCor) and len(self.cors) == 3:
                wi.setDisabled(True)
                wi.setTwiss(tw)
                wi.setElements([c.name for c in self.cors])
                wi.setDisabled(False)
            if isinstance(wi, Bump3XSrc) and len(self.cors) == 3:
                wi.setDisabled(True)
                wi.setTwiss(tw)
                #wi.setElements([c.name for c in self.cors])
                wi.setDisabled(False)

        self.emit(SIGNAL("correctorChanged(PyQt_PyObject)"), self.cors)

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


    def _update_bump_4(self, ibase, jdx = 7):
        st = float(self.src.text())
        dx = float(self.src_x.text())
        dxp = float(self.src_xp.text())
        
        a = [self.table4.item(i, 2).data(Qt.DisplayRole).toFloat()[0]
             for i in range(4)]
        b = [self.table4.item(i, 3).data(Qt.DisplayRole).toFloat()[0]
             for i in range(4)]
        ph = [self.table4.item(i, 4).data(Qt.DisplayRole).toFloat()[0]
              for i in range(4)]

        if self.rdbxbump.isChecked():
            bt, at, pht = getTwissAt(st, ["betax", "alphax", "phix"])
        elif self.rdbybump.isChecked():
            bt, at, pht = getTwissAt(st, ["betay", "alphay", "phiy"])
        #dth = [self.table4.item(i, 8).data(Qt.DisplayRole).toFloat()[0]
        #       for i in range(4)]
        dt1 = dx*(np.cos(pht-ph[1]) - at*np.sin(pht-ph[1]))/\
            np.sqrt(bt*b[0])*np.sin(ph[1]-ph[0]) - \
            dxp*np.sqrt(bt/b[0])*np.sin(pht-ph[1])/np.sin(ph[1]-ph[0])
        dt2 = -dx*(np.cos(pht-ph[0]) - at*np.sin(pht-ph[0]))/\
            np.sqrt(bt*b[1])*np.sin(ph[1]-ph[0]) + \
            dxp*np.sqrt(bt/b[1])*np.sin(pht-ph[0])/np.sin(ph[1]-ph[0])
        dt3 = -dx*(np.cos(ph[3]-pht) - at*np.sin(pht-ph[3]))/\
            np.sqrt(bt*b[2])*np.sin(ph[3]-ph[2]) + \
            dxp*np.sqrt(bt/b[2])*np.sin(pht-ph[3])/np.sin(ph[3]-ph[2])
        dt4 = dx*(np.cos(ph[2]-pht) - at*np.sin(pht-ph[2]))/\
            np.sqrt(bt*b[3])*np.sin(ph[3]-ph[2]) - \
            dxp*np.sqrt(bt/b[3])*np.sin(pht-ph[1])/np.sin(ph[3]-ph[2])

        # same kick for theta2
        dth1, ok = self.table4.item(0,jdx).data(Qt.DisplayRole).toFloat()
        dth2 = -dth1
        dth3 = -(np.sqrt(b[0])*dth1*np.sin(ph[3]-ph[0]) +
                 np.sqrt(b[1])*dth2*np.sin(ph[3]-ph[1]))/\
                 np.sin(ph[3]-ph[2])/np.sqrt(b[2])
        dth4 = (np.sqrt(b[0])*dth1*np.sin(ph[2]-ph[0]) +
                 np.sqrt(b[1])*dth2*np.sin(ph[2]-ph[1]))/\
                 np.sin(ph[3]-ph[2])/np.sqrt(b[3])
        self.table4.item(1,jdx).setData(Qt.DisplayRole, str(dth2))
        self.table4.item(2,jdx).setData(Qt.DisplayRole, str(dth3))
        self.table4.item(3,jdx).setData(Qt.DisplayRole, str(dth4))
        print dt1, dt2, dt3, dt4

    def updateTable(self, row, col):
        #print self.table4.currentRow(), self.table4.currentColumn()
        if len(self.cors) < 3: return
        if col == 7:
            if self.__updating: return
            self.__updating = True
            if len(self.cors) == 3:
                self._update_bump_3(row, jdx = col)
            elif len(self.cors) == 4:
                self._update_bump_4(row, jdx = col)
            self.__updating = False

    def _apply_bump(self):
        jdx = 7
        dxl = [self.table4.item(i,jdx).data(Qt.DisplayRole).toFloat()[0]
               for i in range(len(self.cors))]

        if self.rdbxbump.isChecked():
            c0 = [c.x for c in self.cors]
            for i,c in enumerate(self.cors):
                c.x = c0[i] + dxl[i]
                #print dx, c.x, c.pv(field="x", handle="setpoint")
                self.table4.item(i,jdx+1).setData(Qt.DisplayRole,
                                                  "%.5f" % (c0[i] + dxl[i]))
                self.table4.item(i,jdx+2).setData(Qt.DisplayRole,
                                                  "%.5f" % (c.x))
        elif self.rdbybump.isChecked():
            c0 = [c.y for c in self.cors]
            for i,c in enumerate(self.cors):
                c.y = c0[i] + dxl[i]
                #print dx, c.x, c.pv(field="x", handle="setpoint")
                self.table4.item(i,jdx+1).setData(Qt.DisplayRole,
                                                  "%.5f" % (c0[i] + dxl[i]))
                self.table4.item(i,jdx+2).setData(Qt.DisplayRole,
                                                  "%.5f" % c.y)
        self.table4.resizeColumnsToContents()


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
        self._twiss = getTwiss("[pqs]*", ["s", "betax", "betay", "etax"])
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
