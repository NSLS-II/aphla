from __future__ import print_function, division, absolute_import

"""
AP Beam Based Alignment
------------------------

"""
# :author: Lingyun Yang <lyyang@bnl.gov>

#import cothread
#app = cothread.iqt()

import sys, time
import gui_resources
#import bpmtabledlg
from elempickdlg import ElementPickDlg
#from apbbaconfdlg import BbaConfig
#from orbitplot import OrbitPlot
#from aphla import conf, bba

import aphla as ap

from PyQt4.QtCore import QSize, SIGNAL, QThread, Qt
from PyQt4.QtGui import (QMainWindow, QAction, QActionGroup, QVBoxLayout,
    QWidget, QTabWidget, QLabel, QIcon, QApplication, QImage, QPixmap,
    QSizePolicy, QFileDialog, QDialog, QTableWidget, QHeaderView, QHBoxLayout,
    QProgressBar, QTableWidgetItem, QFormLayout)
#
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

import PyQt4.Qwt5 as Qwt
import numpy as np
from PIL import Image, ImageQt

#lyyang@virtac:/home/shengb/nsls2$ cat T2_NSLS2/tracy_align_error_one.txt
##index name      cell girder  dX    dY    dS    dRoll   dPitch   dYaw
#444    QH1G2C04A  2   4    1.0e-06 0.0e+00 0.00e+00 0.0e+00 0.00e+00 0.00e+00
#660    QH1G2C06A  2   6    1.0e-06 0.0e+00 0.00e+00 0.0e+00 0.00e+00 0.00e+00
#lyyang@virtac:/home/shengb/nsls2$


class BbaMplCanvas(FigureCanvas):
    """Ultimately, this is a QWidget (as well as a FigureCanvasAgg, etc.)."""
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        fig.subplots_adjust(bottom=0.2)
        self.axes = fig.add_subplot(111)
        # We want the axes cleared every time plot() is called
        self.axes.hold(True)
        #self.axes.set_xlabel("")
        #self.compute_initial_figure()
        #
        FigureCanvas.__init__(self, fig)
        self.setParent(parent)
        # to avoid the cut off of xlabel
        self.setMinimumSize(250, 200)
        FigureCanvas.setSizePolicy(self,
                                   QSizePolicy.Expanding,
                                   QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)


class BbaMainWindow(QMainWindow):
    """
    the main window
    """
    def __init__(self, parent = None):
        QMainWindow.__init__(self, parent)

        self.setIconSize(QSize(48, 48))

        self.widtab = QTabWidget()
        #widtab.addTab(QLabel("Tab1"), "Tab 1")
        self._bba = {}
        #self._bba_plot_data = []
        self._canvas_wid = []
        #
        self.setCentralWidget(self.widtab)

        #
        # file menu
        #
        self.fileMenu = self.menuBar().addMenu("&File")
        fileQuitAction = QAction(QIcon(":/file_quit.png"), "&Quit", self)
        fileQuitAction.setShortcut("Ctrl+Q")
        fileQuitAction.setToolTip("Quit the application")
        fileQuitAction.setStatusTip("Quit the application")
        self.connect(fileQuitAction, SIGNAL("triggered()"),
                     self.close)
        fileConfigAction = QAction("&Config", self)
        #
        fileOpenAction = QAction(QIcon(":file_quit.png"), "&Open...", self)
        fileOpenAction.setToolTip("Open an existing data file")
        self.connect(fileOpenAction, SIGNAL("triggered()"), self.fileOpen)

        self.fileMenu.addAction(fileOpenAction)
        self.fileMenu.addAction(fileQuitAction)
        self.fileMenu.addAction(fileConfigAction)

        self.controlMenu = self.menuBar().addMenu("&Control")

        controlGoAction =  QAction(QIcon(":/control_play.png"), "&Go", self)
        controlGoAction.setShortcut("Ctrl+G")
        #fileQuitAction.setToolTip("Quit the application")
        #fileQuitAction.setStatusTip("Quit the application")
        #fileQuitAction.setIcon(Qt.QIcon(":/filequit.png"))
        self.controlMenu.addAction(controlGoAction)
        self.connect(controlGoAction, SIGNAL("triggered()"), self.align)

        # help
        self.helpMenu = self.menuBar().addMenu("&Help")

        #toolbar = QToolBar(self)
        #self.addToolBar(toolbar)
        fileToolBar = self.addToolBar("File")
        fileToolBar.setObjectName("FileToolBar")
        fileToolBar.addAction(fileQuitAction)
        fileToolBar.addAction(controlGoAction)
        #

    def chooseBpm(self):
        #print self.bpm
        bpm = []
        bpmmask = self.plot1.curve1.mask[:]
        for i in range(len(self.bpm)):
            if bpmmask[i]:
                bpm.append((self.bpm[i], Qt.Unchecked))
            else:
                bpm.append((self.bpm[i], Qt.Checked))

        form = ElementPickDlg(bpm, 'BPM', self)

        if form.exec_():
            choice = form.result()
            for i in range(len(self.bpm)):
                if self.bpm[i] in choice:
                    self.plot1.setMask(i, 0)
                    self.plot2.setMask(i, 0)
                else:
                    self.plot1.setMask(i, 1)
                    self.plot2.setMask(i, 1)

    def fileOpen(self):
        """
        open a HDF5 file, show pictures as tabs
        """
        fname = QFileDialog.getOpenFileName(self,
                "Open data file", '.', "HDF5 files (*.h5, *.hdf5)")
        if not fname: return

        import h5py
        f = h5py.File(str(fname), 'r')
        for grp in f.keys():
            for img in f[grp].keys():
                ds1 = f[grp][img]
                #if ds1.get('attr', None) is None: continue
                if ds1.attrs.get('CLASS', None) != 'IMAGE': continue
                # the fourth alpha, needs be 255.
                d1 = np.ones(ds1.shape[:2] + (4,), dtype=np.uint8) * 255
                d1[:,:,:3] = np.asarray(ds1)

                wid = QWidget()
                l = QVBoxLayout(wid)
                imageLabel = QLabel(self)
                imageLabel.setText("Text")
                #imageLabel
                im1 = Image.fromarray(d1)
                pxm = QPixmap.fromImage(ImageQt.ImageQt(im1))
                #pxm.save("j.png")
                imageLabel.setPixmap(pxm)
                imageLabel.adjustSize()
                l.addWidget(imageLabel)
                self.widtab.addTab(wid, "%s:%s" % (grp, img))
        f.close()

    def _load_conf_h5(self, h5file, grp = "bba"):
        pass

    def align_quad(self, **kwargs):
        """
        """
        for quadname in confdat['bowtie_align']:
            bbconf = confdat['bowtie_align'][quadname]
            print("Quadrupole:", bbconf['Q'], caget(bbconf['Q'][2].encode('ascii')))
            for i in range(0, len(bbconf['COR_BPM']), 2):
                ac = bba.BbaBowtie()
                ac.quad, s, ac.quad_pvsp, ac.dqk1 = bbconf['Q'][:4]
                ac.bpm, s, ac.bpm_pvrb = bbconf['COR_BPM'][i][:3]
                ac.trim, s, ac.trim_pvsp, kickrg, obtpv = bbconf['COR_BPM'][i+1][:5]
                ac.quad_pvrb = ac.quad_pvsp
                ac.trim_pvrb = ac.trim_pvsp
                ac.kick = np.linspace(kickrg[0], kickrg[1], 4)
                ac.orbit_pvrb = confdat[obtpv]
                #ca.bpm = conf['
                # fix the utf-8
                ac.align()
                aclist = self._bba.setdefault(quadname, [])
                aclist.append(ac)

                print("Plotting ...")
                wid = QWidget(self)
                l = QVBoxLayout(wid)
                cv1 = BbaMplCanvas(wid)
                cv2 = BbaMplCanvas(wid)
                #x = np.linspace(0, 2*np.pi, 100)
                #cv1.axes.plot(x, np.sin(x) + np.random.rand(len(x))*.2, 'ro-')
                #cv2.axes.plot(x, np.tan(x) + np.random.rand(len(x))*.2, 'go-')
                ac.plot(cv1.axes, cv2.axes, factor=(1e6, 1e6))
                l.addWidget(cv1)
                l.addWidget(cv2)
                cv1.draw()
                cv2.draw()
                data1 = np.fromstring(cv1.tostring_rgb(), dtype=np.uint8, sep='')
                w, h = cv1.get_width_height()
                data1 = data1.reshape(h, w, 3)
                data2 = np.fromstring(cv2.tostring_rgb(), dtype=np.uint8, sep='')
                w, h = cv2.get_width_height()
                data2 = data2.reshape(h, w, 3)
                aclist.append([data1, data2])
                self.widtab.addTab(wid, "%s:%d" % (quadname, self.widtab.count()+1))
                #wid.setFocus()
                self.widtab.setCurrentIndex(self.widtab.count() - 1)
            # moving to the next quadname
        self.write()


    def write(self):
        import h5py
        print("FIXME: using hard coded file name: apbba.hdf5")
        f = h5py.File('apbba.hdf5', 'w')
        for quadname, rec in self._bba.items():
            for i in range(0, len(rec), 2):
                ac = rec[i]
                # name the group as quad:index
                grp = f.create_group("%s:%d" %(ac.quad, i/2))
                k, m, n = np.shape(ac.orbit)
                dset = grp.create_dataset("orbit", (k, m, n), 'd')
                dset[:, :, :] = ac.orbit
                grp['keep'] = ac.mask
                grp['trim_fitted'] = ac.trim_fitted
                grp['trim_pvsp'] = ac.trim_pvsp

                for j in range(len(rec[i+1])):
                    data = rec[i+1][j]
                    h, w, d = np.shape(data)
                    dset = grp.create_dataset("image_%02d"%j, (h, w, d), dtype=np.uint8)
                    dset[:,:,:] = data[:,:,:]
                    dset.attrs['CLASS'] = 'IMAGE'
                    dset.attrs['IMAGE_VERSION'] = '1.2'
                    dset.attrs['IMAGE_SUBCLASS'] = 'IMAGE_TRUECOLOR'

        f.close()


class ApBbaThread(QThread):
    def __init__(self):
        super(ApBbaThread, self).__init__()

    def run(self):
        #
        # Note: logging is not recommended: Cross Thread signal.
        #
        #print "initializing ", self.mach, self.latname
        #_logger.info("background initializing {0}.{1}".format(
        #    self.mach, self.latname))
        print("Measurement finished")


class ApBbaDlg(QDialog):
    def __init__(self, parent = None, **kwargs):
        super(ApBbaDlg, self).__init__(parent)

        self.bpms  = []
        self.quads = []
        self.corrs  = []
        self.quad_dkicks = []
        self.cor_dkicks = []

        self.bba = ap.bba.BbaBowtie()

        self.table = QTableWidget(0, 5)
        self.table.setMinimumHeight(120)
        self.table.setMinimumWidth(500)
        self.table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        hdview = QHeaderView(Qt.Horizontal)
        self.table.setHorizontalHeaderLabels(
            ['QUAD', 'BPM.field', 'BPM center', "Corr", "Kick"])

        fmbox = QFormLayout()
        self.subprogress = QProgressBar()
        self.subprogress.setTextVisible(True)
        self.subprogress.setSizePolicy(QSizePolicy.MinimumExpanding,
                                       QSizePolicy.Fixed)
        self.progress    = QProgressBar()
        self.progress.setTextVisible(True)
        self.progress.setSizePolicy(QSizePolicy.MinimumExpanding,
                                    QSizePolicy.Fixed)
        fmbox.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)
        fmbox.addRow("Current BPM", self.subprogress)
        fmbox.addRow("All Alignment", self.progress)
        #self.progress.setMaximum(self.repeatbox.value())
        vbox = QVBoxLayout()
        vbox.addWidget(self.table)
        vbox.addLayout(fmbox)

        #hbox.addStretch()
        self.widtab = QTabWidget()

        vbox.addWidget(self.widtab)

        self.setLayout(vbox)

        self.connect(self.widtab, SIGNAL("currentChanged(int)"),
                     self.activateResult)
        self.connect(self.table, SIGNAL("cellClicked(int, int)"),
                     self.activateResult)
        #self.bbathread = ApBbaThread()
        #self.connect(self.bbathread,
        #             SIGNAL("aligned(QString, QString, float, float)"),
        #             self.setResult)
        #self.connect(self.bbathread,
        #             SIGNAL("startAlign(QString, QString, QString)"),
        #             self.appendRecord)

        #self.connect(self.bbathread,
        #             SIGNAL("aligned(QString, QString, float, float)"),
        #             self.bbadlg.appendResult)

    def setInput(self, **kwargs):
        self.bpms = kwargs.get('bpms', [])
        self.quads = kwargs.get('quads', [])
        self.cors  = kwargs.get('cors', [])
        self.quad_dkicks = kwargs.get('quad_dkicks', [])
        self.cor_dkicks = kwargs.get('cor_dkicks', [])

    def runAlignment(self, **kwargs):
        self.setInput(**kwargs)
        #self.bbathread.start()
        print("Starting %d measurements" % len(self.bpms))
        self.progress.setMaximum(len(self.bpms))
        self.subprogress.setMaximum(100)
        from cothread.catools import caget, caput
        print(__file__, "BBA align", caget('V:2-SR:C30-BI:G2{PH1:11}SA:X'))
        self.table.setRowCount(len(self.bpms))
        for i,bpmrec in enumerate(self.bpms):
            print(i, bpmrec[0].name, self.quads[i][0].name)
            self.bba.setInput(bpmrec, self.quads[i], self.cors[i],
                              self.quad_dkicks[i], self.cor_dkicks[i])
            #self.emit(SIGNAL("startAlign(QString, QString, QString)"),
            #          self.quads[i][0].name, bpmrec[0].name, bpmrec[1])
            self.setNames(i, self.quads[i][0].name, bpmrec[0].name,
                          bpmrec[1], self.cors[i][0].name)
            self.bba.align(verbose=2, guihook = QApplication.processEvents,
                           logger = None, progress = self.subprogress)

            cv1 = BbaMplCanvas()
            cv2 = BbaMplCanvas()
            self.bba.plot(cv1.axes, cv2.axes, factor=(1e6, 1e6))
            cv1.draw()
            cv2.draw()

            wid = QWidget(self)
            hbox = QHBoxLayout()
            hbox.addWidget(cv1)
            hbox.addWidget(cv2)
            wid.setLayout(hbox)
            self.widtab.addTab(wid, "%s.%s" % (bpmrec[0].name, bpmrec[1]))
            self.widtab.setCurrentIndex(i)

            #time.sleep(.1)

            #self.emit(SIGNAL("aligned(QString, QString, float, float)"),
            #          bpmrec[0].name, bpmrec[1], 0.0, 0.0)
            self.setResult(i, bpmrec[0].name, bpmrec[1],
                           self.bba.bpm_fitted, self.bba.cor_fitted)
            self.progress.setValue(i + 1)

    def activateResult(self, i = 0, j = 0):
        if i < self.widtab.count() and i != self.widtab.currentIndex():
            self.widtab.setCurrentIndex(i)
        if i < self.table.rowCount() and i != self.table.currentRow():
            self.table.setCurrentCell(i, 1)

    def setNames(self, i, quadname, bpmname, fld, corname):
        self.table.setItem(i, 0, QTableWidgetItem(quadname))
        self.table.setItem(i, 1,
                           QTableWidgetItem("{0}.{1}".format(bpmname, fld)))
        self.table.setItem(i, 3, QTableWidgetItem(corname))

    def setResult(self, i, bpmname, fld, bpmval, corval):
        #self.table.setItem(n, 1, QTableWidgetItem(bpmname))
        #self.table.setItem(n, 2, QTableWidgetItem(fld))
        self.table.setItem(i, 2, QTableWidgetItem("%g" % bpmval))
        self.table.setItem(i, 4, QTableWidgetItem("%g" % corval))
        self.table.setCurrentCell(i, 1)

def main(args = None):
    #app = QApplication(args)
    demo = BbaMainWindow()
    demo.resize(600,500)
    demo.show()

    #sys.exit(app.exec_())
    cothread.WaitForQuit()


# Admire!
if __name__ == '__main__':
    #hla.clean_init()
    main(sys.argv)

# Local Variables: ***
# mode: python ***
# End: ***
