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
from aphla import catools, getElements, setLocalBump, getBeta, getEta, getPhase, getTunes

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
        jx0, jy0 = 2, 3
        for i in range(self.table.rowCount()):
            self.table.item(i, jx0).setData(Qt.DisplayRole, str(0.0))
            self.table.item(i, jy0).setData(Qt.DisplayRole, str(0.0))
        #self.updateTargetOrbit(self.base_orbit_box.currentText())

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

    def getTargetOrbit(self):
        x = [self.table.item(i,4).data(Qt.DisplayRole).toFloat()[0]
             for i in range(self.table.rowCount())]
        y = [self.table.item(i,5).data(Qt.DisplayRole).toFloat()[0]
             for i in range(self.table.rowCount())]
        return (self.sb, x), (self.sb, y)

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
        #self._update_orbit_plot()
        x, y = self.getTargetOrbit()
        self.emit(SIGNAL("targetOrbitChanged(PyQt_PyObject, PyQt_PyObject)"),
                  x, y)

    def updateBump(self, row, col):
        #print "updating ", row, col
        if col == 2 or col == 3:
            self.updateTargetOrbit(self.base_orbit_box.currentText())


class OrbitCorrNBumps(QtGui.QWidget):
    def __init__(self, bpms, cors, plots = [], parent = None):
        self.bpm_all, self.cor_all = bpms, cors
        self.cors = []
        self._plots = plots
        super(OrbitCorrNBumps, self).__init__(parent)
        self.table4 = QTableWidget(4, 12)
        self.table4.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        hdview = QHeaderView(Qt.Horizontal)
        self.table4.setHorizontalHeaderLabels(
            ['Corrector', 's', 'Beta X', 'Beta Y', 'Phi X', 'Phi Y',
             "dPhiX", "dPhiY", "dX", "dY", "X", "Y"])
        for i in range(4):
            for j in range(12):
                it = QTableWidgetItem()
                self.table4.setItem(i, j, it)
        self.table4.resizeColumnsToContents()
        #self.table.horizontalHeader().setStretchLastSection(True)
        #for i in range(4):
        #    print "width", i, self.table.columnWidth(i)
        #self.table.setColumnWidth(0, 300)
        #self.table4.setColumnWidth(1, 80)
        hrow = self.table4.rowHeight(0)
        htbl = (hrow * 4) + self.table4.horizontalHeader().height() +\
            2*self.table4.frameWidth()
        self.table4.setMinimumHeight(htbl + 10)
        #self.table4.setMaximumHeight(htbl + 10)

        grp = QtGui.QGroupBox("Correctors")
        gbox = QtGui.QGridLayout()
        self.cbox = [QtGui.QComboBox(), QtGui.QComboBox(),
                     QtGui.QComboBox(), QtGui.QComboBox()]
        for i,c in enumerate(self.cbox):
            c.addItem("")
            for cobj in self.cor_all: c.addItem(cobj.name)
            c.setCurrentIndex(i + 10)
            gbox.addWidget(c, 0, i+1)
            gbox.setColumnStretch(i+1, 1)
            self.connect(c, SIGNAL("currentIndexChanged(QString)"),
                         self.updateCorrectors)
            
        gbox.addWidget(QtGui.QLabel("Correctors:"), 0, 0)
        grp.setLayout(gbox)

        vbox1 = QtGui.QVBoxLayout()
        vbox1.addWidget(self.table4)
        vbox1.addWidget(grp)
        vbox1.addStretch()

        hbox1 = QtGui.QHBoxLayout()
        hbox1.addStretch()
        btnClear = QtGui.QPushButton("Clear")
        hbox1.addWidget(btnClear)
        btnZoomin = QtGui.QPushButton("Zoom In")
        hbox1.addWidget(btnZoomin)
        btnApply = QtGui.QPushButton("Apply")
        hbox1.addWidget(btnApply)

        vbox1.addLayout(hbox1, 0)
        #vbox1.addStretch()
        self.setLayout(vbox1)

        self.connect(self.table4, SIGNAL("cellChanged(int,int)"),
                     self.updateTable)
        self.connect(btnZoomin, SIGNAL("clicked()"),
                     self._zoom_in_plots)

    def updateCorrectors(self, name):
        corls = [str(c.currentText()) for c in self.cbox]
        for i,c1 in enumerate(corls[:-1]):
            if not c1: continue
            for j,c2 in enumerate(corls[i+1:]):
                if not c2: continue
                if c1 == c2:
                    QtGui.QMessageBox.critical(
                        self, "Local Orbit Bump", 
                        "ERROR: Can not have duplicate correctors",
                        QtGui.QMessageBox.Ok)
                    return
                #self.progress.setValue(0)
        self.cors = [c for c in self.cor_all if c.name in corls]
        if len(self.cors) < 3: return
        nux, nuy = getTunes(source="database")
        beta = getBeta([c.name for c in self.cors])
        phse = getPhase([c.name for c in self.cors])
        
        #print beta, type(beta)
        #print phse, type(phse)
        tb = self.table4
        for i,c in enumerate(self.cors):
            tb.item(i,0).setData(Qt.DisplayRole, c.name)
            tb.item(i,1).setData(Qt.DisplayRole, c.sb)
            tb.item(i,2).setData(Qt.DisplayRole, "%.4f" % (beta[i,0],))
            tb.item(i,3).setData(Qt.DisplayRole, "%.4f" % (beta[i,1],))
            tb.item(i,4).setData(Qt.DisplayRole, "%.4f" % (phse[i,0],))
            tb.item(i,5).setData(Qt.DisplayRole, "%.4f" % (phse[i,1],))
            # 
            dphx = phse[i,0] - phse[0,0]
            if dphx < 0: dphx += nux * 2 * 3.14159
            tb.item(i,6).setData(Qt.DisplayRole, "%.4f" % (dphx,))
            
            dphy = phse[i,1] - phse[0,1]
            if dphy < 0: dphy += nuy * 2 * 3.14159
            tb.item(i,7).setData(Qt.DisplayRole, "%.4f" % (dphy,))

            tb.item(i,8).setData(Qt.DisplayRole, "0.0")
            tb.item(i,9).setData(Qt.DisplayRole, "0.0")

            if c.pv(field="x", handle="setpoint"):
                tb.item(i,10).setData(Qt.DisplayRole, "%.5f" % (c.x,))
            if c.pv(field="y", handle="setpoint"):
                tb.item(i,11).setData(Qt.DisplayRole, "%.5f" % (c.y,))            
            
        tb.resizeColumnsToContents()
        tb.setColumnWidth(8, 80)
        tb.setColumnWidth(9, 80)

        self.emit(SIGNAL("correctorChanged(PyQt_PyObject)"), self.cors)

    def _zoom_in_plots(self):
        s = []
        for i in range(self.table4.rowCount()):
            val, err = self.table4.item(i,1).data(Qt.DisplayRole).toFloat()
            s.append(val)

        s0, s1 = min(s), max(s)
        ds = (s1 - s0)/ 10.0
        for p in self._plots:
            p.setAxisScale(Qwt.QwtPlot.xBottom, s0 - ds, s1 + ds)
            p.replot()
        
    def updateTable(self, row, col):
        #print self.table4.currentRow(), self.table4.currentColumn()
        if col != 5 or col != 6: return
        
        
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

        # top tabs for plotting
        tabs = QtGui.QTabWidget()
        tabs.addTab(self.bpm_plot, "Orbit")
        tabs.addTab(self.cor_plot, "Correctors")
        tabs.addTab(self.tw_plot, "Twiss")
        tabs.setMinimumHeight(200)
        tabs.setMaximumHeight(280)

        layout = QVBoxLayout()
        layout.addWidget(tabs)

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
        layout.addWidget(tabs)

        hln = QtGui.QFrame()
        hln.setLineWidth(3)
        hln.setFrameStyle(QtGui.QFrame.Sunken)
        hln.setFrameShape(QtGui.QFrame.HLine)
        layout.addWidget(hln)

        hbox = QHBoxLayout()

        hbox.addStretch()
        btn = QPushButton("Close")
        self.connect(btn, SIGNAL("clicked()"), self.accept)
        hbox.addWidget(btn)
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
        self.bpm_plot.setAxisScale(Qwt.QwtPlot.xBottom, s0-ds, s1+ds)
        self.bpm_plot.replot()
        self.cor_plot.setMarkers(mks)
        self.tw_plot.setMarkers(mks)
    
    def _help(self):
        print "HELP"

    def done(self, r):
        #for p in self.bpm_plots:
        #    p.plotCurve2(None, None)

        QDialog.done(self, r)

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
    form.resize(600, 500)
    form.setWindowTitle("Create Local Bump")
    form.show()
    #form.reloadElements("*")
    #app.exec_()
    cothread.WaitForQuit()
