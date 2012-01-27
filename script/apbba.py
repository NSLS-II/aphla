#!/usr/bin/env python

import cothread
app = cothread.iqt(use_timer=True)

from cothread.catools import caget, caput

import sys
import gui_resources
#import bpmtabledlg
from elementpickdlg import ElementPickDlg
from apbbaconfdlg import BbaConfig
#from orbitplot import OrbitPlot

from PyQt4.QtCore import QSize, SIGNAL, Qt
from PyQt4.QtGui import (QMainWindow, QAction, QActionGroup, QVBoxLayout, 
    QWidget, QTabWidget, QLabel, QIcon, QApplication, QImage, QPixmap,
    QSizePolicy, QFileDialog)
# 
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

import PyQt4.Qwt5 as Qwt
import numpy as np
from aphlas.bba import BbaBowtie
from PIL import Image, ImageQt

config_dir = "~/.hla"

#lyyang@virtac:/home/shengb/nsls2$ cat T2_NSLS2/tracy_align_error_one.txt 
##index name      cell girder  dX    dY    dS    dRoll   dPitch   dYaw
#444    QH1G2C04A  2   4    1.0e-06 0.0e+00 0.00e+00 0.0e+00 0.00e+00 0.00e+00
#660    QH1G2C06A  2   6    1.0e-06 0.0e+00 0.00e+00 0.0e+00 0.00e+00 0.00e+00
#lyyang@virtac:/home/shengb/nsls2$ 


class BbaMplCanvas(FigureCanvas):
    """Ultimately, this is a QWidget (as well as a FigureCanvasAgg, etc.)."""
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        fig.subplots_adjust(bottom=0.15)
        self.axes = fig.add_subplot(111)
        # We want the axes cleared every time plot() is called
        self.axes.hold(True)
        #self.axes.set_xlabel("")
        #self.compute_initial_figure()
        #
        FigureCanvas.__init__(self, fig)
        self.setParent(parent)
        # to avoid the cut off of xlabel
        self.setMinimumSize(400, 300)
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
        self.config = BbaConfig(config_dir, "nsls2_sr_bba.json")

        self.widtab = QTabWidget()
        #widtab.addTab(QLabel("Tab1"), "Tab 1")
        self._bba = []
        self._bba_plot_data = []
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
        #if not self.okToContinue():
        #    return
        #dir = (os.path.dirname(self.filename)
        #       if self.filename is not None else ".")
        #formats = (["*.{0}".format(unicode(format).lower())
        #        for format in QImageReader.supportedImageFormats()])
        fname = QFileDialog.getOpenFileName(self,
                "Open data file", '.', "HDF5 files (*.h5, *.hdf5)")
        import h5py
        f = h5py.File(str(fname), 'r')
        ds1 = f['MyDataset00']
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
        self.widtab.addTab(wid, "Tab %d" % (self.widtab.count()+1))
        f.close()

    def align(self):
        """
        """
        import json
        print "FIXME: using hard coded config file: nsls2_sr_bba.json"
        f = open("/home/lyyang/devel/nsls2-hla/script/data/nsls2_sr_bba.json")
        conf = json.load(f)
        bpmx = conf['orbit_pvx']
        bpmy = conf['orbit_pvy']
        #vx, vy = np.array(caget(bpmx)), np.array(caget(bpmy))
        #import matplotlib.pylab as plt
        #plt.plot(vx)
        #plt.plot(vy)
        #
        #import matplotlib.pylab as plt
        ac = BbaBowtie()
        #ac._analyze()

        #fig = plt.figure()
        #ax1 = fig.add_subplot(211)
        #ax2 = fig.add_subplot(212)
        #ac.plot(ax1, ax2)
        #fig.savefig("align.png")

        # if we need the config data
        for bbconf in conf['bowtie_align']:
            print "Quadrupole:", bbconf['Q'], caget(bbconf['Q'][2].encode('ascii'))
            ac.quad, s, ac.quad_pvsp, ac.dqk1 = bbconf['Q'][:4]
            for i in range(0, len(bbconf['COR_BPM']), 2):
                ac.bpm, s, ac.bpm_pvrb = bbconf['COR_BPM'][i][:3]
                ac.trim, s, ac.trim_pvsp, kickrg, obtpv = bbconf['COR_BPM'][i+1][:5]
                ac.quad_pvrb = ac.quad_pvsp
                ac.trim_pvrb = ac.trim_pvsp
                ac.kick = np.linspace(kickrg[0], kickrg[1], 8)
                ac.orbit_pvrb = conf[obtpv]
                #ca.bpm = conf['
                # fix the utf-8
                ac.align()
        self._bba.append(ac)

        print "Plotting ..."
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
        self._bba_plot_data.append((data1, data2))
        self.widtab.addTab(wid, "Tab %d" % (self.widtab.count()+1))
        #wid.setFocus()
        self.widtab.setCurrentIndex(self.widtab.count() - 1)
        self.write()

        pass
    
    def write(self):
        import h5py
        print "FIXME: using hard coded file name: myfile.hdf5"
        f = h5py.File('myfile.hdf5', 'w')
        for i in range(2):
            print "FIXME: output fixed dataset"
            data = self._bba_plot_data[-1][i]
            h, w, d = np.shape(data)
            dset = f.create_dataset("MyDataset%02d"%i, (h, w, d), dtype=np.uint8)
            dset[:,:,:] = data[:,:,:]
            dset.attrs['CLASS'] = 'IMAGE'
            dset.attrs['IMAGE_VERSION'] = '1.2'
            dset.attrs['IMAGE_SUBCLASS'] = 'IMAGE_TRUECOLOR'
        for i in range(len(self._bba)):
            k, m, n = np.shape(self._bba[i].orbit)
            dset = f.create_dataset("orbit%02d"%i, (k, m, n), 'd')
            dset[:, :, :] = self._bba[i].orbit

        f.close()


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
