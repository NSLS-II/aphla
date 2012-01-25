from PyQt4.QtCore import (PYQT_VERSION_STR, QFile, QFileInfo, QSettings,
        QObject, QString, QT_VERSION_STR, QTimer, QVariant, Qt, SIGNAL,
        QSize, QRectF)
from PyQt4.QtGui import (QAction, QActionGroup, QApplication, QWidget,
        QDockWidget, QFileDialog, QFrame, QIcon, QImage, QImageReader,
        QImageWriter, QInputDialog, QKeySequence, QLabel, QListWidget,
        QMainWindow, QMessageBox, QPainter, QPixmap, QPrintDialog,
        QPrinter, QSpinBox, QPen, QBrush, QVBoxLayout, QTabWidget,
        QTableWidget, QDialog, QHBoxLayout, QDialogButtonBox, QGridLayout,
        QPushButton)

import qwtfig

class MainDlg(QMainWindow):
    def __init__(self, parent=None):  
        super(MainDlg, self).__init__(parent)

        self.bt1 = QPushButton("Push 1")
        self.bt2 = QPushButton("Push 2")
      
        box = QGridLayout()
        box.addWidget(self.bt1, 0, 0)
        box.addWidget(self.bt2, 1, 0)
        
        wid = QWidget()
        wid.setLayout(box)
        self.setCentralWidget(wid)

        self.forms = []

        self.connect(self.bt1, SIGNAL("clicked()"), self.plot)

    def plot(self):
        self.forms.append(qwtfig.QwtDlg())
        self.forms[-1].show()


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    form = MainDlg()
    form.show()
    app.exec_()

    print "selected: ", form.result()

