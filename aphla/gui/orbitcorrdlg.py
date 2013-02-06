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
                         QLabel, QGroupBox, QLineEdit, QDoubleValidator)

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

        self.correctOrbitBtn = QPushButton("Apply")
        self.correctOrbitBtn.setStyleSheet("QPushButton:disabled { color: gray }");
        self.connect(self.correctOrbitBtn, SIGNAL("clicked()"), self.call_apply)

        vbox1 = QVBoxLayout()
        #hbox.addStretch(1)
        gb = QGroupBox("settings")
        lbl = QLabel("step size:")
        self.stepsizebox = QLineEdit(str(stepsize), parent=self)
        self.stepsizebox.setValidator(QDoubleValidator(self))
        self.connect(self.stepsizebox, SIGNAL("textChanged(QString)"), self.update_cell_stepsize)
        vbox1.addWidget(lbl)
        vbox1.addWidget(self.stepsizebox)
        lbl.setBuddy(self.stepsizebox)
        vbox1.setStretch(0, 0)
        vbox1.setStretch(1, 0)

        gb.setLayout(vbox1)

        vbox = QVBoxLayout()
        vbox.addWidget(gb)
        vbox.addStretch(1.0)
        vbox.addWidget(self.correctOrbitBtn)
        layout = QHBoxLayout()
        layout.addWidget(self.table)
        layout.addLayout(vbox) 
        layout.setStretch(0, 1)
        layout.setStretch(1, 0)
        self.setLayout(layout)
        #self.update_orbit = update_orbit
        self.orbit_plots = orbit_plots
        self.correct_orbit = correct_orbit
        self.val = [s, x, y]

        # draw the target orbit
        self.orbit_plots[0].plotCurve2(self.val[1], self.val[0])
        self.orbit_plots[1].plotCurve2(self.val[2], self.val[0])

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
        self.orbit_plots[1].plotCurve2(self.val[2], self.val[0])


    def call_apply(self):
        #print "apply the orbit"
        self.correctOrbitBtn.setEnabled(False)
        self.correct_orbit(self.bpm, zip(self.val[1], self.val[2]))
        self.correctOrbitBtn.setEnabled(True)

    def done(self, r):
        for p in self.orbit_plots:
            p.plotCurve2(None, None)

        QDialog.done(self, r)
