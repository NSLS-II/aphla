
from PyQt4.Qt import Qt, SIGNAL
from PyQt4.QtGui import (QDialog, QTableWidget, QTableWidgetItem,
                         QDoubleSpinBox, QGridLayout, QVBoxLayout,
                         QHBoxLayout, QSizePolicy, QHeaderView,
                         QDialogButtonBox, QPushButton, QApplication)

class DoubleSpinBoxCell(QDoubleSpinBox):
    def __init__(self, row = -1, col = -1, parent = None):
        super(QDoubleSpinBox, self).__init__(parent)
        self.row = row
        self.col = col

class OrbitCorrDlg(QDialog):
    def __init__(self, bpm, s, x, y, stepsize = (None, None), orbit_plots = None,
                 correct_orbit = None, parent = None):

        super(OrbitCorrDlg, self).__init__(parent)
        self.table = QTableWidget(len(bpm), 4)
        self.table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        hdview = QHeaderView(Qt.Horizontal)
        self.table.setHorizontalHeaderLabels(['BPM', 's', 'x', 'y'])
        for i in range(len(bpm)):
            it = QTableWidgetItem(bpm[i])
            it.setFlags(it.flags() & (~Qt.ItemIsEditable))
            self.table.setItem(i, 0, it)

            it = QTableWidgetItem(str(s[i]))
            it.setFlags(it.flags() & (~Qt.ItemIsEditable))
            #it.setMinimumWidth(80)
            self.table.setItem(i, 1, it)

            it = DoubleSpinBoxCell(i, 2)
            it.setRange(-100000, 100000)
            if stepsize[0] is not None: it.setSingleStep(stepsize[0])
            it.setMinimumWidth(88)
            self.connect(it, SIGNAL("valueChanged(double)"), self.call_update)
            #self.connect(it, SIGNAL("
            self.table.setCellWidget(it.row, it.col, it)

            it = DoubleSpinBoxCell(i, 3)
            it.setRange(-100000, 100000)
            if stepsize[1] is not None: it.setSingleStep(stepsize[1])
            it.setMinimumWidth(88)
            self.connect(it, SIGNAL("valueChanged(double)"), self.call_update)
            self.table.setCellWidget(it.row, it.col, it)

        #self.connect(self.table, SIGNAL("cellClicked(int, int)"),
        #             self._cell_clicked)
        self.table.resizeColumnsToContents()
        #self.table.horizontalHeader().setStretchLastSection(True)
        for i in range(4):
            print "width", i, self.table.columnWidth(i)
        #self.table.setColumnWidth(0, 300)
        self.table.setColumnWidth(1, 80)

        btn = QPushButton("Apply")
        self.connect(btn, SIGNAL("clicked()"), self.call_apply)
        hbox = QHBoxLayout()
        hbox.addStretch(1)
        hbox.addWidget(btn)
        layout = QVBoxLayout()
        layout.addWidget(self.table)
        layout.addLayout(hbox) 
        self.setLayout(layout)
        #self.update_orbit = update_orbit
        self.orbit_plots = orbit_plots
        self.correct_orbit = correct_orbit
        self.val = [s, x, y]

    #def _cell_clicked(self, row, col):
    #    print row, col

    def call_update(self, val):
        sender = self.sender()
        print "row/col", sender.row, sender.col, sender.value()
        print "  value was", self.val[sender.col-2][sender.row]
        self.table.setCurrentCell(sender.row, sender.col)
        self.val[sender.col-1][sender.row] = sender.value()
        #for p in self.orbit_plots:
        #    #self.update_orbit(self.val[0], self.val[1])
        self.orbit_plots[0].plotDesiredOrbit(self.val[1], self.val[0])
        self.orbit_plots[1].plotDesiredOrbit(self.val[2], self.val[0])


    def call_apply(self):
        #print "apply the orbit"
        self.correct_orbit(self.val[0], self.val[1])

    def done(self, r):
        for p in self.orbit_plots:
            p.plotDesiredOrbit(None, None)

        QDialog.done(self, r)
