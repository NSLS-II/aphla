#!/usr/bin/env python

#__all__ = [ 'main' ]

# for debugging, requires: python configure.py --trace ...
#if 0:
#    import sip
#    sip.settracemask(0x3f)

import cothread
from cothread.catools import caget, caput
from aphlas.epicsdatamonitor import CaDataMonitor

app = cothread.iqt(use_timer=True)

import sys

import gui_resources

#import bpmtabledlg
from elementpickdlg import ElementPickDlg
from orbitconfdlg import OrbitPlotConfig
from orbitplot import OrbitPlot

from PyQt4.QtCore import QSize, SIGNAL, Qt
from PyQt4.QtGui import (QMainWindow, QAction, QActionGroup, QVBoxLayout, 
    QHBoxLayout, QGridLayout, QWidget, QTabWidget, QLabel, QIcon)

import numpy as np

config_dir = "~/.hla"

class OrbitData(object):
    """
    the orbit data
    """
    def __init__(self, pvs, **kw):
        n = len(pvs)
        self.samples = kw.get('samples', 10)
        self.yfactor = kw.get('factor', 1e6)
        self.x = kw.get('x', np.array(range(n), 'd'))
        if len(self.x) != n:
            raise ValueError("pv and x are not same size %d != %d" % (n, len(self.x)))
        self.pvs = pvs
        self.icur, self.icount = -1, 0
        # how many samples are kept for statistics
        self.y      = np.zeros((self.samples, n), 'd')
        for i in range(self.samples):
            self.y[i,:] = caget(self.pvs)
        self.yref   = np.zeros(n, 'd')
        self.errbar = np.ones(n, 'd') * 1e-15
        self.keep   = np.ones(n, 'i')
        #print self.x, self.y

    def update(self):
        """update the orbit data"""
        # y and errbar sync with plot, not changing data.
        i = self.icur + 1
        if i >= self.samples: i = 0
        self.y[i,:] = caget(self.pvs)
        self.y[i, :] *= self.yfactor
        self.errbar[:] = np.std(self.y, axis=0)
        self.icount += 1
        self.icur = i
        
    def reset(self):
        self.icur, self.icount = -1, 0
        self.y.fill(0.0)
        self.errbar.fill(0.0)
        #self.update()

    def min(self):
        c, i = divmod(self.icount - 1, self.samples)
        return np.min(self.y[i,:])

    def max(self):
        c, i = divmod(self.icount - 1, self.samples)
        return np.max(self.y[i,:])
        
    def average(self):
        """average of the whole curve"""
        c, i = divmod(self.icount - 1, self.samples)
        return np.average(self.y[i,:])

    def std(self):
        """std of the curve"""
        y = np.compress(self.keep, self.y, axis=1)
        return np.std(y, axis = 0)

    def data(self, field="orbit"):
        """
        field = [ 'orbit' | 'std' ]
        """
        if self.icur < 0:
            n = len(self.x)
            return self.x, np.zeros(n, 'd'), np.zeros(n, 'd')

        i = self.icur
        if field == 'orbit':
            x1 = np.compress(self.keep, self.x, axis=0)
            y1 = np.compress(self.keep, self.y[i,:] - self.yref, axis=0)
            e1 = np.compress(self.keep, self.errbar, axis=0)
            return x1, y1, e1
        elif field == 'std':
            x1 = np.compress(self.keep, self.x, axis=0)
            y1 = self.std()
            return x1, y1, np.zeros(len(x1), 'd')

class OrbitPlotMainWindow(QMainWindow):
    """
    the main window
    """
    def __init__(self, parent = None):
        QMainWindow.__init__(self, parent)

        self.setIconSize(QSize(48, 48))
        self.config = OrbitPlotConfig(config_dir, "nsls2_sr_orbit.json")

        # initialize a QwtPlot central widget
        #bpm = hla.getElements('BPM')
        pvx = [b[1]['rb'].encode('ascii') for b in self.config.data['bpmx']]
        #print pvx
        pvy = [b[1]['rb'].encode('ascii') for b in self.config.data['bpmy']]
        pvsx = [b[1]['s'] for b in self.config.data['bpmx']]
        pvsy = [b[1]['s'] for b in self.config.data['bpmy']]
        self.bpm = [b[0] for b in self.config.data['bpmx']]
        pvsx_golden = [b[1]['golden'].encode("ascii") 
                       for b in self.config.data['bpmx']]
        self.orbitx_data = OrbitData(pvs = pvx, x = pvsx)
        self.orbity_data = OrbitData(pvs = pvy, x = pvsy)
        self.orbitx_data.update()
        self.orbity_data.update()

        self.plot1 = OrbitPlot(self, self.orbitx_data)
        self.plot2 = OrbitPlot(self, self.orbity_data)
        self.plot3 = OrbitPlot(self, self.orbitx_data, data_field='std',
            errorbar=False)
        self.plot4 = OrbitPlot(self, self.orbity_data, data_field='std',
            errorbar=False)

        #for e in hla.getGroupMembers(['QUAD', 'BPM', 'HCOR', 'VCOR', 'SEXT'],
        #                             op='union'):
        #    self.plot1.addMagnetProfile(e.sb, e.sb+e.length, e.name)
            
        #for i in range(10):
        #    self.plot1.maskIndex(i)
        
        self.plot1.plotLayout().setCanvasMargin(4)
        self.plot1.plotLayout().setAlignCanvasToScales(True)
        self.plot1.setTitle("Horizontal Orbit")
        self.plot3.setTitle("Horizontal")
        #self.lbplt1info = QLabel("Min\nMax\nAverage\nStd")

        #self.plot1.singleShot()
        #print self.plot1.curve1.y

        self.plot2.plotLayout().setCanvasMargin(4)
        self.plot2.plotLayout().setAlignCanvasToScales(True)
        self.plot2.setTitle("Vertical Orbit")
        self.plot4.setTitle("Vertical")
        #self.lbplt2info = QLabel("Min\nMax\nAverage\nStd")

        wid1 = QWidget()
        vbox = QGridLayout()
        #vbox.addWidget(self.lbplt1info, 0, 0)
        vbox.addWidget(self.plot1, 0, 1)
        #vbox.addWidget(self.lbplt2info, 1, 0)
        vbox.addWidget(self.plot2, 1, 1)
        
        wid1.setLayout(vbox)
        self.wid = QTabWidget()
        self.wid.addTab(wid1, "Orbit Plot")

        #wid2 = QTableWidget()
        #wid.addTab(wid2, "test2")
        wid1 = QWidget()
        vbox = QVBoxLayout()
        vbox.addWidget(self.plot3)
        vbox.addWidget(self.plot4)
        wid1.setLayout(vbox)
        self.wid.addTab(wid1, "Std")
        self.setCentralWidget(self.wid)

        #self.setCentralWidget(OrbitPlot())
        #print self.plot1.sizeHint()
        #print self.plot1.minimumSizeHint()

        #
        # file menu
        #
        self.fileMenu = self.menuBar().addMenu("&File")
        fileQuitAction = QAction(QIcon(":/file_quit.png"), "&Quit", self)
        fileQuitAction.setShortcut("Ctrl+Q")
        fileQuitAction.setToolTip("Quit the application")
        fileQuitAction.setStatusTip("Quit the application")
        #fileQuitAction.setIcon(Qt.QIcon(":/filequit.png"))
        self.connect(fileQuitAction, SIGNAL("triggered()"),
                     self.close)
        
        #
        self.fileMenu.addAction(fileQuitAction)

        # view
        self.viewMenu = self.menuBar().addMenu("&View")
        # live data
        viewLiveAction = QAction(QIcon(":/view_livedata.png"),
                                    "Live", self)
        viewLiveAction.setCheckable(True)
        viewLiveAction.setChecked(True)
        self.connect(viewLiveAction, SIGNAL("toggled(bool)"),
                     self.liveData)

        viewSingleShotAction = QAction(QIcon(":/view_singleshot.png"),
                                       "Single Shot", self)
        self.connect(viewSingleShotAction, SIGNAL("triggered()"),
                     self.singleShot)

        # errorbar
        viewErrorBarAction = QAction(QIcon(":/view_errorbar.png"),
                                    "Errorbar", self)
        viewErrorBarAction.setCheckable(True)
        viewErrorBarAction.setChecked(False)
        self.connect(viewErrorBarAction, SIGNAL("toggled(bool)"),
                     self.errorBar)

        # scale
        viewZoomOut15Action = QAction(QIcon(":/view_zoomout.png"),
                                         "Zoom out x1.5", self)
        self.connect(viewZoomOut15Action, SIGNAL("triggered()"),
                     self.zoomOut15)
        viewZoomIn15Action = QAction(QIcon(":/view_zoomin.png"),
                                        "Zoom in x1.5", self)
        self.connect(viewZoomIn15Action, SIGNAL("triggered()"),
                     self.zoomIn15)
        viewZoomAutoAction = QAction(QIcon(":/view_zoom.png"),
                                        "Auto Fit", self)
        self.connect(viewZoomAutoAction, SIGNAL("triggered()"),
                     self.zoomAuto)

        controlChooseBpmAction = QAction(QIcon(":/control_choosebpm.png"),
                                         "Choose BPM", self)
        self.connect(controlChooseBpmAction, SIGNAL("triggered()"),
                     self.chooseBpm)

        controlResetPvDataAction = QAction(QIcon(":/control_reset.png"),
                                           "Reset PV Data", self)
        self.connect(controlResetPvDataAction, SIGNAL("triggered()"),
                     self.resetPvData)

        # zoom in the horizontal orbit
        controlZoomInPlot1Action = QAction("zoomin H", self)
        self.connect(controlZoomInPlot1Action, SIGNAL("triggered()"),
                     self.plot1.zoomIn)
        controlZoomOutPlot1Action = QAction("zoomout H", self)
        self.connect(controlZoomOutPlot1Action, SIGNAL("triggered()"),
                     self.plot1.zoomOut)
        controlZoomInPlot2Action = QAction("zoomin V", self)
        self.connect(controlZoomInPlot2Action, SIGNAL("triggered()"),
                     self.plot2.zoomIn)
        controlZoomOutPlot2Action = QAction("zoomout V", self)
        self.connect(controlZoomOutPlot2Action, SIGNAL("triggered()"),
                     self.plot2.zoomOut)

        self.viewMenu.addAction(viewZoomOut15Action)
        self.viewMenu.addAction(viewZoomIn15Action)
        self.viewMenu.addAction(viewZoomAutoAction)
        self.viewMenu.addSeparator()
        self.viewMenu.addAction(viewLiveAction)
        self.viewMenu.addAction(viewSingleShotAction)
        self.viewMenu.addSeparator()
        self.viewMenu.addAction(viewErrorBarAction)

        self.controlMenu = self.menuBar().addMenu("&Control")
        #self.viewMenu.addSeparator()
        self.controlMenu.addAction(controlChooseBpmAction)
        self.controlMenu.addAction(controlResetPvDataAction)
        self.controlMenu.addSeparator()
        self.controlMenu.addAction(controlZoomInPlot1Action)
        self.controlMenu.addAction(controlZoomOutPlot1Action)
        self.controlMenu.addAction(controlZoomInPlot2Action)
        self.controlMenu.addAction(controlZoomOutPlot2Action)

        # help
        self.helpMenu = self.menuBar().addMenu("&Help")

        #toolbar
        #toolbar = QToolBar(self)
        #self.addToolBar(toolbar)
        fileToolBar = self.addToolBar("File")
        fileToolBar.setObjectName("FileToolBar")
        fileToolBar.addAction(fileQuitAction)
        #
        viewToolBar = self.addToolBar("View")
        viewToolBar.setObjectName("ViewToolBar")
        viewToolBar.addAction(viewZoomOut15Action)
        viewToolBar.addAction(viewZoomIn15Action)
        viewToolBar.addAction(viewZoomAutoAction)
        viewToolBar.addAction(viewLiveAction)
        viewToolBar.addAction(viewSingleShotAction)
        #viewToolBar.addAction(viewErrorBarAction)

        controlToolBar = self.addToolBar("Control")
        controlToolBar.addAction(controlChooseBpmAction)
        controlToolBar.addAction(controlResetPvDataAction)

        # update at 2Hz
        self.timerId = self.startTimer(1000)

    def liveData(self, on):
        """Switch on/off live data taking"""
        #print "MainWindow: liveData", on
        self.plot1.liveData(on)
        self.plot2.liveData(on)
        self.plot3.liveData(on)
        self.plot4.liveData(on)
        
    def errorBar(self, on):
        self.plot1.setErrorBar(on)
        self.plot2.setErrorBar(on)

    def zoomOut15(self):
        """
        """
        i = self.wid.currentIndex()
        if i == 0:
            self.plot1._scaleVertical(1.5)
            self.plot2._scaleVertical(1.5)
        elif i == 1:
            self.plot3._scaleVertical(1.5)
            self.plot4._scaleVertical(1.5)
            
    def zoomIn15(self):
        """
        """
        i = self.wid.currentIndex()
        if i == 0:
            self.plot1._scaleVertical(1.0/1.5)
            self.plot2._scaleVertical(1.0/1.5)
        elif i == 1:
            self.plot3._scaleVertical(1.0/1.5)
            self.plot4._scaleVertical(1.0/1.5)

    def zoomAuto(self):
        i = self.wid.currentIndex()
        if i == 0:
            self.plot1.zoomAuto()
            self.plot2.zoomAuto()
        elif i == 1:
            self.plot3.zoomAuto()
            self.plot4.zoomAuto()
            
    def chooseBpm(self):
        #print self.bpm
        bpm = []
        livebpm = self.orbitx_data.keep
        for i in range(len(self.bpm)):
            if livebpm[i]:
                bpm.append((self.bpm[i], Qt.Checked))
            else:
                bpm.append((self.bpm[i], Qt.Unchecked))

        form = ElementPickDlg(bpm, 'BPM', self)

        if form.exec_(): 
            choice = form.result()
            for i in range(len(self.bpm)):
                if self.bpm[i] in choice:
                    self.orbitx_data.keep[i] = 1
                    self.orbity_data.keep[i] = 1
                else:
                    self.orbitx_data.keep[i] = 0
                    self.orbity_data.keep[i] = 0
        
    def timerEvent(self, e):
        #self.statusBar().showMessage("%s; %s"  % (
        #        self.plot1.datainfo(), self.plot2.datainfo()))
        #print "updating", __file__
        self.orbitx_data.update()
        self.orbity_data.update()
        self.updateStatus()
        i = self.wid.currentIndex()
        if i == 0:
            if self.plot1.live: self.plot1.updatePlot()
            if self.plot2.live: self.plot2.updatePlot()
        elif i == 1:
            if self.plot3.live: self.plot3.updatePlot()
            if self.plot4.live: self.plot4.updatePlot()

    def updateStatus(self):
        #self.statusBar().showMessage("%s; %s"  % (
        #        self.plot1.datainfo(), self.plot2.datainfo()))      
        pass

    def singleShot(self):
        #print "Main: Singleshot"
        self.plot1.singleShot()
        self.plot2.singleShot()
        self.plot3.singleShot()
        self.plot4.singleShot()
        self.updateStatus()

    def resetPvData(self):
        self.orbitx_data.reset()
        self.orbity_data.reset()
        #hla.hlalib._reset_trims()


def main(args = None):
    #app = QApplication(args)
    demo = OrbitPlotMainWindow()
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
