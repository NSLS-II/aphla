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

from aporbitplot import ApCaPlot, ApCaArrayPlot
from aphla import catools, getElements, setLocalBump, getBeta, getEta

class DoubleSpinBoxCell(QDoubleSpinBox):
    def __init__(self, row = -1, col = -1, val = 0.0, parent = None):
        super(QDoubleSpinBox, self).__init__(parent)
        self.row = row
        self.col = col
        self.setValue(val)
        self.setDecimals(10)

class OrbitCorrGeneral(QtGui.QWidget):
    def __init__(self, parent = None):
        super(OrbitCorrGeneral, self).__init__(parent)

class OrbitCorrNBumps(QtGui.QWidget):
    def __init__(self, parent = None):
        super(OrbitCorrNBumps, self).__init__(parent)

class OrbitCorrDlg(QDialog):
    def __init__(self, bpms = None, cors = None, parent = None):
        super(OrbitCorrDlg, self).__init__(parent)
        # add bpms
        self.bpms = bpms
        if bpms is None:
            self.bpms = getElements("BPM")
        self.bpms = [bpm for bpm in self.bpms if bpm.flag == 0]
        pvx = [bpm.pv(field="x", handle="readback")[0] for bpm in self.bpms]
        pvy = [bpm.pv(field="y", handle="readback")[0] for bpm in self.bpms]
        self.x0, self.y0 = None, None
        self._update_current_orbit()

        s = [bpm.sb for bpm in self.bpms]
        self.bpm_plot = ApCaArrayPlot([pvx, pvy], x = [s, s])
        magprof = aphla.getBeamlineProfile()
        self.bpm_plot.setMagnetProfile(magprof)

        self.xc = Qwt.QwtPlotCurve()
        self.xc.setTitle("Target X")
        self.xc.attach(self.bpm_plot)
        self.xc.setData(s, self.x0)
        self.bpm_plot.showCurve(self.xc, True)

        self.yc = Qwt.QwtPlotCurve()
        self.yc.setTitle("Target Y")
        self.yc.attach(self.bpm_plot)
        self.yc.setData(s, self.y0)
        self.bpm_plot.showCurve(self.yc, True)
        self.bpm_plot.setContentsMargins(12, 10, 10, 10)

        self.cors = cors
        if cors is None:
            self.cors = []
            for c in getElements("HCOR") + getElements("VCOR"):
                if c not in self.cors:
                    self.cors.append(c)
        pvx = [c.pv(field="x", handle="setpoint")[0]
               for c in getElements("HCOR") if c in self.cors]
        pvy = [c.pv(field="y", handle="setpoint")[0]
               for c in getElements("VCOR") if c in self.cors]
        s = [c.sb for c in self.cors]
        self.cor_plot = ApCaArrayPlot([pvx, pvy], x = [s, s],
                                      labels=["HCOR", "VCOR"])
        #magprof = aphla.getBeamlineProfile()
        self.cor_plot.setMagnetProfile(magprof)
        self.cor_plot.setContentsMargins(12, 10, 10, 10)
        #self.cor_plot.setMinimumHeight(200)
        #self.cor_plot.setMaximumHeight(250)

        self.tw_plot = ApCaPlot()
        cbetax = Qwt.QwtPlotCurve()
        cbetay = Qwt.QwtPlotCurve()
        cetax  = Qwt.QwtPlotCurve()
        beta = getBeta("[pqs]*", spos=True)
        eta = getEta("[pqs]*", spos = True)
        cbetax.setData(beta[:,-1], beta[:,0])
        cbetay.setData(beta[:,-1], beta[:,1])
        cetax.setData(  eta[:,-1],  eta[:,0])
        cbetax.attach(self.tw_plot)
        cbetax.setTitle("Beta X")
        cbetay.attach(self.tw_plot)
        cbetay.setTitle("Beta Y")
        cetax.attach( self.tw_plot)
        cetax.setTitle("Eta X")
        self.tw_plot.setMagnetProfile(magprof)
        self.tw_plot.setContentsMargins(12, 10, 10, 10)
        self.tw_plot.showCurve(cbetax, True)
        self.tw_plot.showCurve(cbetay, True)
        self.tw_plot.showCurve(cetax, True)

        tabs = QtGui.QTabWidget()
        tabs.addTab(self.bpm_plot, "Orbit")
        tabs.addTab(self.cor_plot, "Correctors")
        tabs.addTab(self.tw_plot, "Twiss")
        tabs.setMinimumHeight(200)
        tabs.setMaximumHeight(280)

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

        self.table4 = QTableWidget(4, 8)
        self.table4.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        hdview = QHeaderView(Qt.Horizontal)
        self.table4.setHorizontalHeaderLabels(
            ['Corrector', 's', 'X', 'Y', 'Beta X', 'Beta Y', 'Phi X', 'Phi Y'])
        self.table4.resizeColumnsToContents()
        #self.table.horizontalHeader().setStretchLastSection(True)
        #for i in range(4):
        #    print "width", i, self.table.columnWidth(i)
        #self.table.setColumnWidth(0, 300)
        self.table4.setColumnWidth(1, 80)

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

        self.rcondbox = QLineEdit()
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

        self.progress = QProgressBar()
        self.progress.setMaximum(self.repeatbox.value())
        self.progress.setMaximumHeight(15)
        frmbox.addRow(self.progress)

        grp = QtGui.QGroupBox("Local Bump")
        grp.setLayout(frmbox)
        #vbox.addStretch(1.0)
        #self.qdb = QDialogButtonBox(self)
        #self.qdb.addButton("APP", QDialogButtonBox.ApplyRole)
        #self.qdb.addButton("R", QDialogButtonBox.ResetRole)
        #btn.setDefault(True)
        #self.qdb.addButton(QDialogButtonBox.Cancel)
        #self.qdb.addButton(QDialogButtonBox.Help)

        layout = QVBoxLayout()
        layout.addWidget(tabs)

        hb1 = QHBoxLayout()
        hb1.addWidget(self.table, 1)
        hb1.addWidget(grp) 

        layout.addLayout(hb1, 1)

        hln = QtGui.QFrame()
        hln.setLineWidth(3)
        hln.setFrameStyle(QtGui.QFrame.Sunken)
        hln.setFrameShape(QtGui.QFrame.HLine)
        layout.addWidget(hln)

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

        #layout.addWidget(self.progress)
        #layout.addWidget(self.qdb)
        layout.addLayout(hbox)
        self.setLayout(layout)
        #self.update_orbit = update_orbit
        #self._x0 = tuple(x)  # save for reset
        #self._y0 = tuple(y)  # save for reset
        #self.val = [s, x, y]
        self.setMinimumWidth(1000)
        # draw the target orbit
        #self.bpm_plots[0].plotCurve2(self.val[1], self.val[0])
        #self.bpm_plots[1].plotCurve2(self.val[2], self.val[0])

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
        self.x0 = [float(v) for v in catools.caget(pvx)]
        self.y0 = [float(v) for v in catools.caget(pvy)]

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
        self.bpm_plot.replot()

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
        obt = []
        jx, jy = 4, 5
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

    def _help(self):
        print "HELP"

    def done(self, r):
        #for p in self.bpm_plots:
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
