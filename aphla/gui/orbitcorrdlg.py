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

from aporbitplot import ApCaArrayPlot

class DoubleSpinBoxCell(QDoubleSpinBox):
    def __init__(self, row = -1, col = -1, val = 0.0, parent = None):
        super(QDoubleSpinBox, self).__init__(parent)
        self.row = row
        self.col = col
        self.setValue(val)
        self.setDecimals(10)

class OrbitCorrDlg(QDialog):
    def __init__(self, bpms = None,
                 stepsize = 0.001, orbit_plots = None,
                 correct_orbit = None, parent = None):
        self.bpms = bpms
        if bpms is None:
            self.bpms = ap.getElements("BPM")
        self.bpms = [bpm for bpm in self.bpms if bpm.flag == 0]
        pvx = [bpm.pv(field="x", handle="readback")[0] for bpm in self.bpms]
        pvy = [bpm.pv(field="y", handle="readback")[0] for bpm in self.bpms]
        self.x0, self.y0 = None, None
        self._update_current_orbit()

        s = [bpm.sb for bpm in self.bpms]
        self.plot = ApCaArrayPlot([pvx, pvy], x = [s, s])
        magprof = aphla.getBeamlineProfile()
        self.plot.setMagnetProfile(magprof)
        self.plot.setMinimumHeight(120)
        self.plot.setMaximumHeight(200)

        self.xc = Qwt.QwtPlotCurve()
        self.xc.setTitle("Target X")
        self.xc.attach(self.plot)
        self.xc.setData(s, self.x0)
        self.plot.showCurve(self.xc, True)

        self.yc = Qwt.QwtPlotCurve()
        self.yc.setTitle("Target Y")
        self.yc.attach(self.plot)
        self.yc.setData(s, self.y0)
        self.plot.showCurve(self.yc, True)
        
        self._stepsize0 = stepsize
        super(OrbitCorrDlg, self).__init__(parent)
        self.table = QTableWidget(len(self.bpms), 6)
        self.table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        hdview = QHeaderView(Qt.Horizontal)
        self.table.setHorizontalHeaderLabels(
            ['BPM Name', 's', 'X Bump', 'Y Bump', "Target X", "Target Y"])
        
        for i,bpm in enumerate(self.bpms):
            it = QTableWidgetItem(bpm.name)
            it.setFlags(it.flags() & (~Qt.ItemIsEditable))
            self.table.setItem(i, 0, it)

            it = QTableWidgetItem(str(bpm.sb))
            it.setFlags(it.flags() & (~Qt.ItemIsEditable))
            #it.setMinimumWidth(80)
            self.table.setItem(i, 1, it)

            for j in range(2, 6):
                it = QTableWidgetItem(str(0.0))
                it.setData(Qt.DisplayRole, str(0.0))
                it.setFlags(it.flags() | Qt.ItemIsEditable)
                self.table.setItem(i, j, it) 
            # use the current orbit 
            self.table.item(i,4).setData(Qt.DisplayRole, str(self.x0[i]))
            self.table.item(i,5).setData(Qt.DisplayRole, str(self.y0[i]))

        #self.connect(self.table, SIGNAL("cellClicked(int, int)"),
        #             self._cell_clicked)
        self.table.resizeColumnsToContents()
        #self.table.horizontalHeader().setStretchLastSection(True)
        #for i in range(4):
        #    print "width", i, self.table.columnWidth(i)
        #self.table.setColumnWidth(0, 300)
        self.table.setColumnWidth(1, 80)

        frmbox = QFormLayout()
        self.base_orbit_box = QtGui.QComboBox()
        self.base_orbit_box.addItems([
                "Current Orbit", "All Zeros"])
        frmbox.addRow("Orbit Base", self.base_orbit_box)

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

        self.rcondbox = QLineEdit(str(stepsize), parent=self)
        self.rcondbox.setValidator(QDoubleValidator(0, 1, 0, self))
        self.rcondbox.setText("1e-2")
        frmbox.addRow("r&cond for SVD", self.rcondbox)

        self.scalebox = QDoubleSpinBox()
        self.scalebox.setRange(0.01, 5.00)
        self.scalebox.setSingleStep(0.01)
        self.scalebox.setValue(0.68)
        frmbox.addRow("&Scale correctors", self.scalebox)

        hln2 = QtGui.QFrame()
        hln2.setLineWidth(3)
        hln2.setFrameStyle(QtGui.QFrame.Sunken)
        hln2.setFrameShape(QtGui.QFrame.HLine)
        frmbox.addRow(hln2)

        #vbox.addStretch(1.0)
        #self.qdb = QDialogButtonBox(self)
        #self.qdb.addButton("APP", QDialogButtonBox.ApplyRole)
        #self.qdb.addButton("R", QDialogButtonBox.ResetRole)
        #btn.setDefault(True)
        #self.qdb.addButton(QDialogButtonBox.Cancel)
        #self.qdb.addButton(QDialogButtonBox.Help)

        self.progress = QProgressBar()
        self.progress.setMaximum(self.repeatbox.value())

        hbox = QHBoxLayout()

        btn = QPushButton("Reset")
        self.connect(btn, SIGNAL("clicked()"), self.resetBumps)
        hbox.addWidget(btn)

        hbox.addStretch()
        btn = QPushButton("Close")
        self.connect(btn, SIGNAL("clicked()"), self.accept)
        hbox.addWidget(btn)
        self.correctOrbitBtn = QPushButton("Apply")
        #self.correctOrbitBtn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.correctOrbitBtn.setStyleSheet("QPushButton:disabled { color: gray }");
        self.connect(self.correctOrbitBtn, SIGNAL("clicked()"), self.call_apply)
        self.correctOrbitBtn.setDefault(True)
        hbox.addWidget(self.correctOrbitBtn)

        layout = QVBoxLayout()
        layout.addWidget(self.plot)

        hb1 = QHBoxLayout()
        hb1.addWidget(self.table, 1)
        hb1.addLayout(frmbox) 

        layout.addLayout(hb1, 1)

        layout.addWidget(self.progress)
        #layout.addWidget(self.qdb)
        layout.addLayout(hbox)
        self.setLayout(layout)
        #self.update_orbit = update_orbit
        #self._x0 = tuple(x)  # save for reset
        #self._y0 = tuple(y)  # save for reset
        #self.val = [s, x, y]
        self.setMinimumWidth(1000)
        # draw the target orbit
        #self.orbit_plots[0].plotCurve2(self.val[1], self.val[0])
        #self.orbit_plots[1].plotCurve2(self.val[2], self.val[0])

        self.connect(self.base_orbit_box,
                     SIGNAL("currentIndexChanged(QString)"), 
                     self.updateTargetOrbit)
        self.connect(self.repeatbox, SIGNAL("valueChanged(int)"),
                     self.progress.setMaximum)
        self.connect(self.table, SIGNAL("cellChanged (int, int)"),
                     self.updateBump)

        #self.connect(self.qdb, SIGNAL("clicked(QAbstractButton)"), self._action)
        #self.connect(self.qdb, SIGNAL("helpRequested()"), self._help)

    #def _cell_clicked(self, row, col):
    #    print row, col

    def _update_current_orbit(self):
        pvx = [bpm.pv(field="x", handle="readback")[0] for bpm in self.bpms]
        pvy = [bpm.pv(field="y", handle="readback")[0] for bpm in self.bpms]
        self.x0 = [float(v) for v in aphla.catools.caget(pvx)]
        self.y0 = [float(v) for v in aphla.catools.caget(pvy)]

    def _update_orbit_plot(self):
        s = [bpm.sb for bpm in self.bpms]
        vx1 = [ 0.0 ] * len(self.bpms)
        vy1 = [ 0.0 ] * len(self.bpms)
        jx, jy = 4, 5
        for i in range(self.table.rowCount()):
            vx1[i],err = self.table.item(i, jx).data(Qt.DisplayRole).toFloat()
            vy1[i],err = self.table.item(i, jy).data(Qt.DisplayRole).toFloat()
        self.xc.setData(s, vx1)
        self.yc.setData(s, vy1)
        self.plot.replot()

    def updateTargetOrbit(self, baseobt):
        if baseobt == "All Zeros":
            jx0, jx1 = 2, 4
            jy0, jy1 = 3, 5
            for i in range(self.table.rowCount()):
                it0 = self.table.item(i, jx0)
                it1 = self.table.item(i, jx1)
                it1.setData(Qt.DisplayRole, it0.data(Qt.DisplayRole))
                it0 = self.table.item(i, jy0)
                it1 = self.table.item(i, jy1)
                it1.setData(Qt.DisplayRole, it0.data(Qt.DisplayRole))
        elif baseobt == "Current Orbit":
            self._update_current_orbit()
            jx0, jx1 = 2, 4
            jy0, jy1 = 3, 5
            for i in range(self.table.rowCount()):
                dx0,err = self.table.item(i, jx0).data(Qt.DisplayRole).toFloat()
                it = self.table.item(i, jx1)
                it.setData(Qt.DisplayRole, self.x0[i] + dx0)

                dy0,err = self.table.item(i, jy0).data(Qt.DisplayRole).toFloat()
                it = self.table.item(i, jy1)
                it.setData(Qt.DisplayRole, self.y0[i] + dy0)
        self._update_orbit_plot()

    def updateBump(self, row, col):
        #print "updating ", row, col
        if col == 2 or col == 3:
            self.updateTargetOrbit(self.base_orbit_box.currentText())

    def update_cell_stepsize(self, text):
        for i in range(self.table.rowCount()):
            for j in [2, 3]:
                it = self.table.cellWidget(i, j)
                if it is None: continue
                it.setSingleStep(float(self.stepsizebox.text()))

    def call_apply(self):
        #print "apply the orbit"
        trims = [c for c in aphla.getElements("HCOR") + aphla.getElements("VCOR")
                 if c.flag == 0]
        obt = []
        jx, jy = 4, 5
        for i in range(self.table.rowCount()):
            x1,err = self.table.item(i, jx).data(Qt.DisplayRole).toFloat()
            y1,err = self.table.item(i, jy).data(Qt.DisplayRole).toFloat()
            obt.append([x1, y1])

        self.correctOrbitBtn.setEnabled(False)
        nrepeat = self.repeatbox.value()
        scale   = float(self.scalebox.text())
        rcond   = float(self.rcondbox.text())
        self.progress.setValue(0)
        QApplication.processEvents()
        for i in range(nrepeat):
            aphla.setLocalBump(self.bpms, trims, obt)
            self.progress.setValue(i+1)
            QApplication.processEvents()
        self.correctOrbitBtn.setEnabled(True)

    def _help(self):
        print "HELP"

    def done(self, r):
        #for p in self.orbit_plots:
        #    p.plotCurve2(None, None)

        QDialog.done(self, r)

    def resetBumps(self):
        jx0, jy0 = 2, 3
        for i in range(self.table.rowCount()):
            self.table.item(i, jx0).setData(Qt.DisplayRole, str(0.0))
            self.table.item(i, jy0).setData(Qt.DisplayRole, str(0.0))
        self.updateTargetOrbit(self.base_orbit_box.currentText())

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
    form = OrbitCorrDlg(bpms) 
    form.resize(600, 500)
    form.setWindowTitle("Create Local Bump")
    form.show()
    #form.reloadElements("*")
    #app.exec_()
    cothread.WaitForQuit()
