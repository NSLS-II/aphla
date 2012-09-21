#!/usr/bin/env python

#__all__ = [ 'main' ]

# for debugging, requires: python configure.py --trace ...
if 1:
    import sip
    sip.settracemask(0x3f)

from pkg_resources import require
require('cothread>=2.2')

import cothread
app = cothread.iqt()

import aphla
from aphla.catools import caget, caput, camonitor, FORMAT_TIME

import sys

import gui_resources

from elementpickdlg import ElementPickDlg
from orbitconfdlg import OrbitPlotConfig
from orbitplot import OrbitPlot, DcctCurrentPlot
from orbitdata import OrbitData, OrbitDataVirtualBpm
from orbitcorrdlg import OrbitCorrDlg
from elemproperty import *


import time
from PyQt4.QtCore import QSize, SIGNAL, Qt
from PyQt4.QtGui import (QMainWindow, QAction, QActionGroup, QTableView,
    QVBoxLayout, QPen, QSizePolicy, QMessageBox, QSplitter, QPushButton,
    QHBoxLayout, QGridLayout, QWidget, QTabWidget, QLabel, QIcon, QActionGroup)

import numpy as np

class ElementPropertyTabs(QTabWidget):
    def __init__(self, parent = None):
        QTabWidget.__init__(self, parent)
        self.connect(self, SIGNAL('tabCloseRequested(int)'), self.closeTab)

    def addElement(self, elemnames):
        self.setVisible(True)
        print "new element:", elemnames
        elems = aphla.getElements(elemnames)
        if elems is None:
            QMessageBox.warning(self, "Element Not Found",
                                "element " + str(elemnames) + " not found")
        else:
            for elem in elems:
                #print elem.name, elem.sb, elem.fields()
                tableview = QTableView()
                tableview.setModel(ElementPropertyTableModel(elem=elem))
                tableview.setItemDelegate(ElementPropertyDelegate(self))
                tableview.resizeColumnsToContents()
                #rz = tableview.geometry()
                ncol = tableview.model().columnCount()
                fullwidth = sum([tableview.columnWidth(i) for i in range(ncol)])
                tableview.setMinimumWidth(fullwidth+20)
                #tableview.setMaximumWidth(fullwidth+60)
                print "Full width", fullwidth
                tableview.adjustSize()

                wid = QWidget()
                vbox = QVBoxLayout()
                vbox.addWidget(QLabel("Name:   %s" % elem.name))
                vbox.addWidget(QLabel("Device: %s" % elem.devname))
                vbox.addWidget(QLabel("Cell:   %s" % elem.cell))
                vbox.addWidget(QLabel("Girder: %s" % elem.girder))
                vbox.addWidget(QLabel("sBegin: %.3f" % elem.sb))
                vbox.addWidget(QLabel("Length: %.3f" % elem.length))

                #vbox.addWidget(lb_name)
                vbox.addWidget(tableview)
                wid.setLayout(vbox)
                self.addTab(wid, elem.name)
        self.adjustSize()

    def closeTab(self, index):
        self.removeTab(index)
        if self.count() <= 0: self.setVisible(False)


class OrbitPlotMainWindow(QMainWindow):
    """
    the main window has three major widgets: current, orbit tabs and element
    editor.
    """
    def __init__(self, parent = None, lat = None):
        QMainWindow.__init__(self, parent)
        self.setIconSize(QSize(48, 48))

        if lat is not None:
            self.set_lattice(lat)

        self.dcct = DcctCurrentPlot()
        #self.dcct.curve.setData(np.linspace(0, 50, 50), np.linspace(0, 50, 50))
        self.dcct.setMinimumHeight(100)
        self.dcct.setMaximumHeight(150)

        t0 = time.time()
        t = np.linspace(t0 - 8*3600*24, t0, 100)
        self.dcct.curve.t = t
        v = 500*np.exp((t[0] - t[:50])/(4*3600*24))
        self.dcct.curve.v = v.tolist()+v.tolist()
        
        self.dcct.updatePlot()

        cwid = QWidget()
        #majbox = QGridLayout()
        #majbox.addWidget(self.dcct, 0, 0, 1, 2)
        majbox = QVBoxLayout()
        #majbox.setSpacing(30)
        #majbox.setMargin(10)
        majbox.addWidget(self.dcct)
        # 
        self.orbitSplitter = QSplitter(Qt.Horizontal)
        self.tabs = QTabWidget()
        self.orbitSplitter.addWidget(self.tabs)
        #self.orbitSplitter.addWidget(self.elems)

        ##majbox.addWidget(self.tabs, 1, 0)
        ##majbox.addWidget(self.elems, 1, 1)
        majbox.addWidget(self.orbitSplitter) #, 1, 0, 1, 2)
        cwid.setLayout(majbox)

        self.data1 = None
        self.live_orbit = True

        picker = None #[(v[1], v[2], v[0]) for v in self.config.data['magnetpicker']]

        # all orbit plots: [plot, data, index]
        self.obtdata = None
        self.obtplots = [
            OrbitPlot(self, live=self.live_orbit, title="Horizontal Orbit"),
            OrbitPlot(self, live=self.live_orbit, title="Vertical Orbit"),
            OrbitPlot(self, live=self.live_orbit, title="Horizontal"),
            OrbitPlot(self, live=self.live_orbit, title="Vertical")
            ]
        self.obtxplot, self.obtyplot       = self.obtplots[0], self.obtplots[1]
        self.obtxerrplot, self.obtyerrplot = self.obtplots[2], self.obtplots[3]

        for p in self.obtplots:
            p.plotLayout().setCanvasMargin(4)
            p.plotLayout().setAlignCanvasToScales(True)
        #self.lbplt1info = QLabel("Min\nMax\nAverage\nStd")

        wid1 = QWidget()
        gbox = QGridLayout()
        #self.plot1.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        #self.plot2.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        gbox.addWidget(self.obtplots[0], 0, 1)
        gbox.addWidget(self.obtplots[1], 1, 1)
        gbox.setRowStretch(0, 0.5)
        gbox.setRowStretch(1, 0.5)
        wid1.setLayout(gbox)        
        self.tabs.addTab(wid1, "Orbit Plot")

        wid1 = QWidget()
        vbox1 = QVBoxLayout()
        vbox1.addWidget(self.obtplots[2])
        vbox1.addWidget(self.obtplots[3])
        wid1.setLayout(vbox1)
        self.tabs.addTab(wid1, "Std")

        self.setCentralWidget(cwid)

        #self.plot5 = OrbitCorrPlot(self, self.orbitx_data, picker_profile = picker,
        #    magnet_profile = self.config.data['magnetprofile'])
        #wid1 = QWidget()
        #vbox = QVBoxLayout()
        #vbox.addWidget(self.plot5)
        #wid1.setLayout(vbox)
        #self.tabs.addTab(wid1, "OrbitSt")

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
        viewLiveAction.setChecked(self.live_orbit)
        self.connect(viewLiveAction, SIGNAL("toggled(bool)"),
                     self.liveData)

        viewSingleShotAction = QAction(QIcon(":/view_singleshot.png"),
                                       "Single Shot", self)
        self.connect(viewSingleShotAction, SIGNAL("triggered()"),
                     self.singleShot)
        viewDcct = QAction("Current", self)
        viewDcct.setCheckable(True)
        viewDcct.setChecked(True)
        self.connect(viewDcct, SIGNAL("toggled(bool)"), self.viewDcctPlot)

        # errorbar
        viewErrorBarAction = QAction(QIcon(":/view_errorbar.png"),
                                    "Errorbar", self)
        viewErrorBarAction.setCheckable(True)
        viewErrorBarAction.setChecked(True)
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
                                           "Reset BPM statistics", self)
        self.connect(controlResetPvDataAction, SIGNAL("triggered()"),
                     self.resetPvData)

        # zoom in the horizontal orbit
        controlZoomInPlot1Action = QAction("zoomin H", self)
        self.connect(controlZoomInPlot1Action, SIGNAL("triggered()"),
                     self.obtplots[0].zoomIn)
        controlZoomOutPlot1Action = QAction("zoomout H", self)
        self.connect(controlZoomOutPlot1Action, SIGNAL("triggered()"),
                     self.obtplots[1].zoomOut)
        controlZoomInPlot2Action = QAction("zoomin V", self)
        self.connect(controlZoomInPlot2Action, SIGNAL("triggered()"),
                     self.obtplots[2].zoomIn)
        controlZoomOutPlot2Action = QAction("zoomout V", self)
        self.connect(controlZoomOutPlot2Action, SIGNAL("triggered()"),
                     self.obtplots[3].zoomOut)

        drift_from_now = QAction("Drift from Now", self)
        drift_from_now.setCheckable(True)
        drift_from_now.setShortcut("Ctrl+N")
        drift_from_golden = QAction("Drift from Golden", self)
        drift_from_golden.setCheckable(True)
        drift_from_none = QAction("None", self)
        drift_from_none.setCheckable(True)

        steer_orbit = QAction("Steer Orbit ...", self)
        self.connect(steer_orbit, SIGNAL("triggered()"), self.createLocalBump)
        
        self.viewMenu.addAction(drift_from_now)
        self.viewMenu.addAction(drift_from_golden)
        self.viewMenu.addAction(drift_from_none)

        self.viewMenu.addSeparator()
        self.viewMenu.addAction(viewLiveAction)
        self.viewMenu.addAction(viewSingleShotAction)

        self.viewMenu.addSeparator()
        self.viewMenu.addAction(viewErrorBarAction)
        
        drift_group = QActionGroup(self)
        drift_group.addAction(drift_from_none)
        drift_group.addAction(drift_from_now)
        drift_group.addAction(drift_from_golden)
        drift_from_none.setChecked(True)

        sep = self.viewMenu.addSeparator()
        #sep.setText("Drift")
        self.connect(drift_from_now, SIGNAL("triggered()"), self.setDriftNow)
        self.connect(drift_from_none, SIGNAL("triggered()"), self.setDriftNone)
        self.connect(drift_from_golden, SIGNAL("triggered()"), 
                     self.setDriftGolden)

        self.viewMenu.addSeparator()
        self.viewMenu.addAction(viewZoomOut15Action)
        self.viewMenu.addAction(viewZoomIn15Action)
        self.viewMenu.addAction(viewZoomAutoAction)
        self.viewMenu.addSeparator()
        # a bug in PyQwt5 for datetime x-axis, waiting for Debian 7
        #self.viewMenu.addAction(viewDcct)

        self.controlMenu = self.menuBar().addMenu("&Control")
        self.controlMenu.addAction(controlChooseBpmAction)
        self.controlMenu.addAction(controlResetPvDataAction)
        self.controlMenu.addSeparator()
        self.controlMenu.addAction(controlZoomInPlot1Action)
        self.controlMenu.addAction(controlZoomOutPlot1Action)
        self.controlMenu.addAction(controlZoomInPlot2Action)
        self.controlMenu.addAction(controlZoomOutPlot2Action)
        self.controlMenu.addSeparator()
        self.controlMenu.addAction(steer_orbit)

        # debug
        self.debugMenu = self.menuBar().addMenu("&Debug")
        reset_cor = QAction("_Reset Correctors_", self)
        self.connect(reset_cor, SIGNAL("triggered()"), self._reset_correctors)
        reset_quad = QAction("_Reset Quadrupoles_", self)
        self.connect(reset_quad, SIGNAL("triggered()"), self._reset_quadrupoles)
        random_vkick = QAction("_Random V Kick_", self)
        self.connect(random_vkick, SIGNAL("triggered()"), self._random_vkick)
        random_hkick = QAction("_Random H Kick_", self)
        self.connect(random_hkick, SIGNAL("triggered()"), self._random_hkick)
        #
        self.debugMenu.addAction(reset_cor)
        self.debugMenu.addAction(reset_quad)
        self.debugMenu.addAction(random_hkick)
        self.debugMenu.addAction(random_vkick)

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

        # update at 1/2Hz
        dt = 3000
        self.timerId = self.startTimer(dt)
        self.corbitdlg = None # orbit correction dlg


    def setLattice(self, lat):
        vbpm = lat._find_exact_element(aphla.machines.HLA_VBPM)
        if vbpm is not None:
            self.obtdata = OrbitDataVirtualBpm(velement=vbpm)
            self.obtdata.update()
            #print self.obtdata.xorbit()
            #print self.obtdata.yorbit()
        else:
            elems = lat.getElementList('BPM')
            x = [(e.se+e.sb)/2.0 for e in elems]
            se = [e.se for e in elems]
            sb = [e.sb for e in elems]
            picker = [(e.sb, e.se, e.name) for e in elems]
            # data for plot1,2
            self.obtdata = OrbitData(elements=elems, x=x, sb=sb, se=se)

        magprof = lat.getBeamlineProfile()
        for p in self.obtplots:
            p.setPlot(magnet_profile=magprof)

        return

        self.connect(self.plot1, SIGNAL("elementSelected(PyQt_PyObject)"),
                     self.elems.addElement)
        self.connect(self.plot2, SIGNAL("elementSelected(PyQt_PyObject)"),
                     self.elems.addElement)


    def _reset_correctors(self):
        aphla.hlalib._reset_trims()

    def _reset_quadrupoles(self):
        aphla.hlalib._reset_quad()

    def _random_hkick(self):
        hcors = aphla.getElements('HCOR')
        i = np.random.randint(len(hcors))
        hcors[i].x += 1e-7

    def _random_vkick(self):
        cors = aphla.getElements('VCOR')
        i = np.random.randint(len(cors))
        cors[i].y += 1e-7

    def viewDcctPlot(self, on):
        self.dcct.setVisible(on)

    def liveData(self, on):
        """Switch on/off live data taking"""
        #print "MainWindow: liveData", on
        self.live_orbit = on
        for p in self.obtplots: p.liveData(on)
        
    def errorBar(self, on):
        self.plot1.setErrorBar(on)
        self.plot2.setErrorBar(on)

    def setDriftNone(self):
        self.plot1.setDrift('no')
        self.plot2.setDrift('no')

    def setDriftNow(self):
        self.plot1.setDrift('now')
        self.plot2.setDrift('now')

    def setDriftGolden(self):
        self.plot1.setDrift('golden')
        self.plot2.setDrift('golden')

    def zoomOut15(self):
        """
        """
        i = self.tabs.currentIndex()
        if i == 0:
            self.plot1._scaleVertical(1.5)
            self.plot2._scaleVertical(1.5)
        elif i == 1:
            self.plot3._scaleVertical(1.5)
            self.plot4._scaleVertical(1.5)
            
    def zoomIn15(self):
        """
        """
        i = self.tabs.currentIndex()
        if i == 0:
            self.plot1._scaleVertical(1.0/1.5)
            self.plot2._scaleVertical(1.0/1.5)
        elif i == 1:
            self.plot3._scaleVertical(1.0/1.5)
            self.plot4._scaleVertical(1.0/1.5)

    def zoomAuto(self):
        i = self.tabs.currentIndex()
        if i == 0:
            self.plot1.zoomAuto()
            #self.plot2.zoomAuto()
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
        #print "updating", self.data1 
        if self.obtdata is not None:
            self.obtdata.update()
            sx, x, xerr = self.obtdata.xorbit()
            sy, y, yerr = self.obtdata.yorbit()
            #icur = self.tabs.currentIndex()
            self.obtxplot.updateOrbit(sx, x, xerr)
            self.obtxerrplot.updateOrbit(sx, xerr)
            self.obtyplot.updateOrbit(sy, y, yerr)
            self.obtyerrplot.updateOrbit(sy, yerr)
            

    def updateStatus(self):
        #self.statusBar().showMessage("%s; %s"  % (
        #        self.plot1.datainfo(), self.plot2.datainfo()))      
        pass

    def singleShot(self):
        #print "Main: Singleshot"
        for p in self.obtplots: p.singleShot()
        self.updateStatus()

    def resetPvData(self):
        self.orbitx_data.reset()
        self.orbity_data.reset()
        #hla.hlalib._reset_trims()

    #def plotDesiredOrbit(self, x, y):
    #    #print "plot: ", x, y
    #    self.plot1.curve2.setData(self.pvsx, x)
    #    self.plot2.curve2.setData(self.pvsy, y)

    def correctOrbit(self, x, y):
        #print "correct to :", x, y
        trimx = aphla.getElements('HCOR')
        trimy = aphla.getElements('VCOR')
        trimpvx = [t.pv(field='x', handle='setpoint')[0] for t in trimx]
        trimpvy = [t.pv(field='y', handle='setpoint')[0] for t in trimy]
        #print trimpvx
        xref = [v*1e-6 for v in x]
        aphla.correctOrbitPv(self.pvx, trimpvx, ormdata = None, scale = 0.5, 
                              ref = xref)
        yref = [v*1e-6 for v in y]
        aphla.correctOrbitPv(self.pvy, trimpvy, ormdata = None, scale = 0.5, 
                              ref = yref)
        pass

    def createLocalBump(self):
        if self.corbitdlg is None:
            self.corbitdlg = OrbitCorrDlg(
                self.pvx, self.orbitx_data.x, self.orbitx_data.golden(),
                self.orbity_data.golden(), (self.plot1, self.plot2),
                self.correctOrbit, self)
            self.corbitdlg.resize(600, 300)
            self.corbitdlg.setWindowTitle("Create Local Bump")
            #self.connect(self.corbitdlg, SIGNAL("finished(int)"),
            #             self.plot1.curve2.setVisible)
            self.plot1.plotDesiredOrbit(self.orbitx_data.golden(), 
                                        self.orbitx_data.x)
            self.plot2.plotDesiredOrbit(self.orbity_data.golden(), 
                                        self.orbity_data.x)

        self.corbitdlg.show()
        self.corbitdlg.raise_()
        self.corbitdlg.activateWindow()


def main(par=None):
    aphla.initNSLS2V1()
    #app = QApplication(args)
    #app.setStyle(st)
    if '--sim' in sys.argv:
        print "CA offline:", aphla.catools.CA_OFFLINE
        aphla.catools.CA_OFFLINE = True
    demo = OrbitPlotMainWindow()
    demo.setLattice(aphla.machines.getLattice('V1SR'))
    #demo.setWindowTitle("NSLS-II")
    demo.resize(800,500)
    demo.show()
    # print app.style() # QCommonStyle
    #sys.exit(app.exec_())
    cothread.WaitForQuit()


# Admire!
if __name__ == '__main__':
    #hla.clean_init()
    main(sys.argv)

# Local Variables: ***
# mode: python ***
# End: ***
