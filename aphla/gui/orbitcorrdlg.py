"""
Dialog for Orbit Correction and Local Bump
------------------------------------------

"""

# :author: Lingyun Yang <lyyang@bnl.gov>

from PyQt4.Qt import Qt, SIGNAL
from PyQt4.QtGui import (QDialog, QTableWidget, QTableWidgetItem,
                         QDoubleSpinBox, QGridLayout, QVBoxLayout,
                         QHBoxLayout, QSizePolicy, QHeaderView,
                         QDialogButtonBox, QPushButton, QApplication,
                         QLabel, QGroupBox, QLineEdit, QDoubleValidator,
                         QIntValidator, QSizePolicy, QDialogButtonBox, 
                         QFormLayout, QSpinBox, QProgressBar, QAbstractButton)

class DoubleSpinBoxCell(QDoubleSpinBox):
    def __init__(self, row = -1, col = -1, val = 0.0, parent = None):
        super(QDoubleSpinBox, self).__init__(parent)
        self.row = row
        self.col = col
        self.setValue(val)
        self.setDecimals(10)

class OrbitCorrDlg(QDialog):
    def __init__(self, bpm, s, x, y, xunit = '', yunit = '',
                 stepsize = 0.001, orbit_plots = None,
                 correct_orbit = None, parent = None):
        self.bpm = bpm
        self._stepsize0 = stepsize
        super(OrbitCorrDlg, self).__init__(parent)
        self.table = QTableWidget(len(bpm), 4)
        self.table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        hdview = QHeaderView(Qt.Horizontal)
        self.table.setHorizontalHeaderLabels(['BPM', 's', 'x', 'y'])
        for i in range(len(self.bpm)):
            it = QTableWidgetItem(self.bpm[i].name)
            it.setFlags(it.flags() & (~Qt.ItemIsEditable))
            self.table.setItem(i, 0, it)

            it = QTableWidgetItem(str(s[i]))
            it.setFlags(it.flags() & (~Qt.ItemIsEditable))
            #it.setMinimumWidth(80)
            self.table.setItem(i, 1, it)

            it = DoubleSpinBoxCell(i, 2, x[i])
            it.setRange(-100000, 100000)
            it.setSuffix(" " + xunit)
            it.setSingleStep(stepsize)
            #if xref is not None: it.setValue(xref[i])
            it.setMinimumWidth(88)
            self.connect(it, SIGNAL("valueChanged(double)"), self.call_update)
            self.table.setCellWidget(it.row, it.col, it)

            it = DoubleSpinBoxCell(i, 3, y[i])
            it.setRange(-100000, 100000)
            it.setSuffix(" " + yunit)
            it.setSingleStep(stepsize)
            #if yref is not None: it.setValue(yref[i])
            it.setMinimumWidth(88)
            self.connect(it, SIGNAL("valueChanged(double)"), self.call_update)
            self.table.setCellWidget(it.row, it.col, it)

        #self.connect(self.table, SIGNAL("cellClicked(int, int)"),
        #             self._cell_clicked)
        self.table.resizeColumnsToContents()
        #self.table.horizontalHeader().setStretchLastSection(True)
        #for i in range(4):
        #    print "width", i, self.table.columnWidth(i)
        #self.table.setColumnWidth(0, 300)
        self.table.setColumnWidth(1, 80)


        frmbox = QFormLayout()
        self.stepsizebox = QLineEdit(str(stepsize), parent=self)
        self.stepsizebox.setValidator(QDoubleValidator(self))
        # or connect the returnPressed() signal
        self.connect(self.stepsizebox, SIGNAL("textEdited(QString)"), 
                     self.update_cell_stepsize)
        frmbox.addRow("&Cell step size", self.stepsizebox)
        self.repeatbox = QSpinBox()
        self.repeatbox.setRange(1, 20)
        self.repeatbox.setValue(3)
        # or connect the returnPressed() signal
        frmbox.addRow("&Repeat correction", self.repeatbox)

        self.rcondbox = QLineEdit(str(stepsize), parent=self)
        self.rcondbox.setValidator(QDoubleValidator(0, 1, 0, self))
        self.rcondbox.setText("1e-4")
        frmbox.addRow("r&cond for SVD", self.rcondbox)

        self.scalebox = QDoubleSpinBox()
        self.scalebox.setRange(0.01, 5.00)
        self.scalebox.setSingleStep(0.01)
        self.scalebox.setValue(0.68)
        frmbox.addRow("&Scale correctors", self.scalebox)

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
        hbox.addStretch()

        btn = QPushButton("Reset")
        self.connect(btn, SIGNAL("clicked()"), self._reset)
        hbox.addWidget(btn)
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
        layout.addLayout(frmbox) 
        layout.addWidget(self.table)
        layout.addWidget(self.progress)
        #layout.addWidget(self.qdb)
        layout.addLayout(hbox)
        self.setLayout(layout)
        #self.update_orbit = update_orbit
        self.orbit_plots = orbit_plots
        self.correct_orbit = correct_orbit
        self._x0 = tuple(x)  # save for reset
        self._y0 = tuple(y)  # save for reset
        self.val = [s, x, y]

        # draw the target orbit
        self.orbit_plots[0].plotCurve2(self.val[1], self.val[0])
        self.orbit_plots[1].plotCurve2(self.val[2], self.val[0])

        self.connect(self.repeatbox, SIGNAL("valueChanged(int)"),
                     self.progress.setMaximum)

        #self.connect(self.qdb, SIGNAL("clicked(QAbstractButton)"), self._action)
        #self.connect(self.qdb, SIGNAL("helpRequested()"), self._help)

    #def _cell_clicked(self, row, col):
    #    print row, col

    def update_cell_stepsize(self, text):
        for i in range(self.table.rowCount()):
            for j in [2, 3]:
                it = self.table.cellWidget(i, j)
                if it is None: continue
                it.setSingleStep(float(self.stepsizebox.text()))

    def call_update(self, val):
        sender = self.sender()
        #print "row/col", sender.row, sender.col, sender.value()
        #print "  value was", self.val[sender.col-2][sender.row]
        self.table.setCurrentCell(sender.row, sender.col)
        self.val[sender.col-1][sender.row] = sender.value()
        #for p in self.orbit_plots:
        #    #self.update_orbit(self.val[0], self.val[1])
        self.orbit_plots[0].plotCurve2(self.val[1], self.val[0])
        self.orbit_plots[0].aplot.scaleYLeft()
        self.orbit_plots[1].plotCurve2(self.val[2], self.val[0])
        self.orbit_plots[1].aplot.scaleYLeft()


    def call_apply(self):
        #print "apply the orbit"
        self.correctOrbitBtn.setEnabled(False)
        nrepeat = self.repeatbox.value()
        scale   = float(self.scalebox.text())
        rcond   = float(self.rcondbox.text())
        self.progress.setValue(0)
        QApplication.processEvents()
        for i in range(nrepeat):
            self.correct_orbit(bpms = self.bpm, trims = None,
                               obt = zip(self.val[1], self.val[2]),
                               scale = scale, rcond = rcond)
            self.progress.setValue(i+1)
            QApplication.processEvents()
        self.correctOrbitBtn.setEnabled(True)

    def _help(self):
        print "HELP"

    def done(self, r):
        for p in self.orbit_plots:
            p.plotCurve2(None, None)

        QDialog.done(self, r)

    def _reset(self):
        for i in range(len(self.bpm)):
            it = self.table.cellWidget(i, 2)
            it.setValue(self._x0[i])
            it = self.table.cellWidget(i, 3)
            it.setValue(self._y0[i])

        self.repeatbox.setValue(3)
        self.scalebox.setValue(0.68)
        self.stepsizebox.setText(str(self._stepsize0))
        self.progress.setMaximum(3)
        self.progress.setValue(0)
        
    def _action(self, btn):
        #role = self.qdb.buttonRole(btn)
        #print "Role:", role
        #if role == QDialogButtonBox.ApplyRole:
        #    self.call_apply()
        #elif role == QDialogButtonBox.RejectRole:
        #    self.reject()
        pass

