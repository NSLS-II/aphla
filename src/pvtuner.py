#!/usr/bin/env

from cothread.catools import caput, caget

from PyQt4.QtCore import (PYQT_VERSION_STR, QFile, QFileInfo, QSettings,
        QObject, QString, QT_VERSION_STR, QTimer, QVariant, Qt, SIGNAL,
        QSize, QRectF)
from PyQt4.QtGui import (QAction, QActionGroup, QApplication, QWidget,
        QDockWidget, QFileDialog, QFrame, QIcon, QImage, QImageReader,
        QImageWriter, QInputDialog, QKeySequence, QLabel, QListWidget,
        QMainWindow, QMessageBox, QPainter, QPixmap, QPrintDialog,
        QPrinter, QSpinBox, QPen, QBrush, QVBoxLayout, QTabWidget,
        QTableWidget, QDialog, QHBoxLayout, QDialogButtonBox, QGridLayout,
        QPushButton, QLineEdit)

class PvTunerDlg(QDialog):
    def __init__(self, parent=None):  
        super(PvTunerDlg, self).__init__(parent)

        self.inputBox = QLineEdit()
        addPvBtn = QPushButton("add")

        self.table = QTableWidget()
        
        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok)

        box = QGridLayout()
        box.addWidget(self.inputBox, 0, 0)
        box.addWidget(addPvBtn, 0, 1)
        box.addWidget(self.table, 1, 0, 1, 2)
        box.addWidget(buttonBox, 2, 0)

        self.setLayout(box)

        self.connect(addPvBtn, SIGNAL("clicked()"), self.addPv)
        self.connect(buttonBox, SIGNAL("accepted()"), self.accept)

    def addPv(self):
        pass


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    form = PvTunerDlg()
    form.show()
    app.exec_()

    print "selected: ", form.result()

