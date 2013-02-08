#!/usr/bin/env python
"""
:author: Lingyun Yang lyyang@bnl.gov

This is the main file for GUI app `aporbit`. A high level viewer and editor.
pp"""

# for debugging, requires: python configure.py --trace ...
if 1:
    import sip
    sip.settracemask(0x3f)

from pkg_resources import require
require('cothread>=2.2')

import cothread
app = cothread.iqt()

import traceback
import aphla
from aphla.catools import camonitor, FORMAT_TIME

import logging
import os, sys

import applotresources

from elempickdlg import ElementPickDlg
#from orbitconfdlg import OrbitPlotConfig
from aporbitplot import ApOrbitPlot, ApPlot, DcctCurrentPlot, ApPlotWidget, ApMdiSubPlot
from aporbitdata import ApVirtualElemData
from orbitcorrdlg import OrbitCorrDlg
from elemeditor import *


import time
from PyQt4.QtCore import QSize, SIGNAL, Qt, QObject
from PyQt4.QtGui import (QMainWindow, QAction, QActionGroup, QMenu, QTableView,
    QVBoxLayout, QPen, QSizePolicy, QMessageBox, QSplitter, QPushButton,
    QHBoxLayout, QGridLayout, QWidget, QTabWidget, QLabel, QIcon, QActionGroup,
    QPlainTextEdit, QMdiArea, QMdiSubWindow, QDockWidget
)
import PyQt4.Qwt5 as Qwt

import numpy as np

class QTextEditLoggingHandler(logging.Handler):
    def __init__(self, textedit):
        logging.Handler.__init__(self)
        self.textedit = textedit
        _lgfmt = logging.Formatter("%(asctime)s - %(name)s [%(levelname)s]: "
                                   "%(message)s")
        self.setFormatter(_lgfmt)

    def emit(self, record):
        self.textedit.appendPlainText(self.format(record))



class OrbitPlotMainWindow(QMainWindow):
    """
    the main window has three major widgets: current, orbit tabs and element
    editor.
    """
    def __init__(self, parent = None, machines=[]):
        QMainWindow.__init__(self, parent)
        self.setIconSize(QSize(32, 32))
        self.error_bar = True
        # aphla only stores lattice name, overwrite happens.
        # here stores machine as first level, lattice name as second
        self._machlat = {} # dict of dict
        for m in machines: 
            self._machlat[m] = {}

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

        self.mdiarea = QMdiArea()

        self.live_orbit = True

        self.setCentralWidget(self.mdiarea)

        #self._elemed = ElementPropertyTabs()
        self.elemeditor = ElementEditorDock(
            parent=self,
            elems=["BPM", "HCOR", "VCOR", "QUAD", "SEXT", "*"])
        self.elemeditor.setAllowedAreas(Qt.RightDockWidgetArea)
        self.elemeditor.setFeatures(QDockWidget.DockWidgetMovable|
                                    QDockWidget.DockWidgetClosable)
        self.elemeditor.setFloating(False)
        self.elemeditor.setEnabled(False)
        #self.elemeditor.setWidget(self._elemed)
        #self.elemeditor.show()
        #self.elemeditor.hide()
        self.addDockWidget(Qt.RightDockWidgetArea, self.elemeditor)

        self._vbpm = None
        self._dead_bpm = [] # dead BPM
        self._dead_cor = [] # dead corrector

        # logging
        self.logdock = QDockWidget("Log")
        textedit = QPlainTextEdit()
        self.logger = logging.getLogger(__name__)
        handler = QTextEditLoggingHandler(textedit)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)
        self.logdock.setWidget(textedit)
        self.logdock.setAllowedAreas(Qt.BottomDockWidgetArea)
        self.logdock.setFeatures(QDockWidget.DockWidgetMovable|
                                 QDockWidget.DockWidgetClosable)
        self.logdock.setFloating(False)
        self.logdock.setMinimumHeight(50)
        self.logdock.setMaximumHeight(200)
        self.logdock.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
        self.logdock.resize(200, 80)
        #print self.logdock.sizeHint()
        self.addDockWidget(Qt.BottomDockWidgetArea, self.logdock)

        #self.logger.info("INFO")

        self.createMenuToolBar()

        # update at 1/2Hz
        self.dt, self.itimer = 1500, 0
        self.timerId = None
        #self.timerId = self.startTimer(self.dt)
        self.corbitdlg = None # orbit correction dlg

        self.vbpm = None
        self.statusBar().showMessage("Welcome")

        #self.initMachine("nsls2v2")
        #self._newVelemPlot("V2SR", aphla.machines.HLA_VBPM, 'x', 
        #                   "H Orbit", c = None)

    def createMenuToolBar(self):
        #
        # file menu
        #
        self.machMenu = self.menuBar().addMenu("&Machines")
        self.connect(self.machMenu, SIGNAL("aboutToShow()"),
                     self.updateMachMenu)

        # view
        self.viewMenu = self.menuBar().addMenu("&View")

        mkmenu = QMenu("&Mark", self.viewMenu)
        for fam in ["BPM", "COR", "QUAD", "SEXT", "INSERTION"]:
            famAct = QAction(fam, self)
            famAct.setCheckable(True)
            self.connect(famAct, SIGNAL("toggled(bool)"), self.click_markfam)
            mkmenu.addAction(famAct)
        self.viewMenu.addMenu(mkmenu)

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
        
        # errorbar
        viewErrorBarAction = QAction(QIcon(":/view_errorbar.png"),
                                    "Errorbar", self)
        viewErrorBarAction.setCheckable(True)
        viewErrorBarAction.setChecked(True)
        self.connect(viewErrorBarAction, SIGNAL("toggled(bool)"),
                     self.errorBar)

        # scale
        viewZoomOut15Action = QAction(QIcon(":/view_zoomout.png"),
                                         "Zoom out x1.5 (All)", self)
        self.connect(viewZoomOut15Action, SIGNAL("triggered()"),
                     self.zoomOut15)
        viewZoomIn15Action = QAction(QIcon(":/view_zoomin.png"),
                                        "Zoom in x1.5 (All)", self)
        self.connect(viewZoomIn15Action, SIGNAL("triggered()"),
                     self.zoomIn15)
        viewZoomAutoAction = QAction(QIcon(":/view_zoom.png"),
                                        "Auto Fit (All)", self)
        self.connect(viewZoomAutoAction, SIGNAL("triggered()"),
                     self.zoomAuto)
        #viewAutoScale = QAction("Auto Scale", self)
        #viewAutoScale.setCheckable(True)
        #viewAutoScale.setChecked(False)
        #self.connect(viewAutoScale, SIGNAL("toggled(bool)"), self.zoomAutoScale)

        controlChooseBpmAction = QAction(QIcon(":/control_choosebpm.png"),
                                         "Choose BPM", self)
        self.connect(controlChooseBpmAction, SIGNAL("triggered()"),
                     self.chooseBpm)
        
        #controlResetPvDataAction = QAction(QIcon(":/control_reset.png"),
        #                                   "Reset BPM statistics", self)
        #self.connect(controlResetPvDataAction, SIGNAL("triggered()"),
        #             self.resetPvData)

        drift_from_now = QAction("Drift from Now", self)
        drift_from_now.setCheckable(True)
        drift_from_now.setShortcut("Ctrl+N")
        drift_from_golden = QAction("Drift from Golden", self)
        drift_from_golden.setCheckable(True)
        drift_from_none = QAction("None", self)
        drift_from_none.setCheckable(True)

        steer_orbit = QAction("Steer Orbit ...", self)
        #steer_orbit.setDisabled(True)
        self.connect(steer_orbit, SIGNAL("triggered()"), self.createLocalBump)
        
        self.viewMenu.addAction(drift_from_now)
        self.viewMenu.addAction(drift_from_golden)
        self.viewMenu.addAction(drift_from_none)

        self.viewMenu.addSeparator()
        self.viewMenu.addAction(viewLiveAction)
        self.viewMenu.addAction(viewSingleShotAction)

        self.viewMenu.addSeparator()
        #self.viewMenu.addAction(viewAutoScale)
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
        #for ac in self.viewMenu.actions(): ac.setDisabled(True)

        #
        self.controlMenu = self.menuBar().addMenu("&Control")
        self.controlMenu.addAction(controlChooseBpmAction)
        self.controlMenu.addAction("Choose COR", self.chooseCorrector)
        #self.controlMenu.addAction(controlResetPvDataAction)
        self.controlMenu.addSeparator()
        #self.controlMenu.addAction(controlZoomInPlot1Action)
        #self.controlMenu.addAction(controlZoomOutPlot1Action)
        #self.controlMenu.addAction(controlZoomInPlot2Action)
        #self.controlMenu.addAction(controlZoomOutPlot2Action)
        self.controlMenu.addSeparator()
        self.controlMenu.addAction(steer_orbit)
        #for ac in self.controlMenu.actions(): ac.setDisabled(True)

        # Window
        self.windowMenu = self.menuBar().addMenu("&Windows")
        self.windowMenu.addAction("Cascade", self.mdiarea.cascadeSubWindows)
        self.windowMenu.addAction("Tile", self.mdiarea.tileSubWindows)
        self.windowMenu.addAction("Previous", self.mdiarea.activatePreviousSubWindow)
        self.windowMenu.addAction("Next", self.mdiarea.activateNextSubWindow)
        self.windowMenu.addSeparator()
        viewDcct = QAction("Beam Current", self)
        viewDcct.setCheckable(True)
        viewDcct.setChecked(True)
        self.connect(viewDcct, SIGNAL("toggled(bool)"), self.dcct.setVisible)
        self.windowMenu.addAction(viewDcct)
        self.windowMenu.addAction(self.elemeditor.toggleViewAction())
        self.windowMenu.addAction(self.logdock.toggleViewAction())

        # debug
        self.debugMenu = self.menuBar().addMenu("&Debug")
        self.debugMenu.addAction("_Reset Correctors_", self._reset_correctors)
        self.debugMenu.addAction("_Reset Quadrupoles_", self._reset_quadrupoles)
        self.debugMenu.addAction("_Random V Kick_", self._random_vkick)
        self.debugMenu.addAction("_Random H Kick_", self._random_hkick)
        #for ac in self.debugMenu.actions(): ac.setDisabled(True)

        # help
        self.helpMenu = self.menuBar().addMenu("&Help")

        #toolbar
        #toolbar = QToolBar(self)
        #self.addToolBar(toolbar)
        #fileToolBar = self.addToolBar("File")
        #fileToolBar.setObjectName("FileToolBar")
        #fileToolBar.addAction(fileQuitAction)
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
        #controlToolBar.addAction(controlChooseBpmAction)
        #controlToolBar.addAction(controlResetPvDataAction)

        machToolBar = self.addToolBar("Machines")
        self.machBox = QComboBox()
        self.machBox.addItem("(None)")
        self.machBox.addItems(self._machlat.keys())
        self.connect(self.machBox, SIGNAL("currentIndexChanged(QString)"),
                     self.initMachine)
        self.latBox = QComboBox()
        self.connect(self.latBox, SIGNAL("currentIndexChanged(QString)"), 
                     self.__setLattice)
        machToolBar.addWidget(self.machBox)
        machToolBar.addWidget(self.latBox)
        machToolBar.addAction(QIcon(":/new_bpm.png"), "Orbits", self.newOrbitPlots)
        machToolBar.addAction(QIcon(":/new_cor.png"), "Correctors", self.newCorrectorPlots)

    def initMachine(self, v):
        vm = str(v)
        if vm == "(None)": 
            self.latBox.clear()
            return
        try:
            if vm not in self._machlat or not self._machlat[vm]:
                self.logger.info("initializing machine '%s'" % vm)
                aphla.machines.init(vm)
                # did not make sure user lattice has the same name
                mrec = {'_HLA_DEFAULT_': aphla.machines.getLattice()}
                for latname in aphla.machines.lattices():
                    lat = aphla.machines.getLattice(latname)
                    if lat.machine != vm: continue
                    mrec[latname] = lat
                    print lat.name, latname
                print "default is:", mrec['_HLA_DEFAULT_'].name
                self._machlat[vm] = mrec
            else:
                self.logger.warn("using previous initialized machine '%s'" % vm)
        except:
            QMessageBox.critical(self, "aphla", 
                                 "machine '%s' can not be initialized" % vm,
                                 QMessageBox.Ok)
            self.machBox.setCurrentIndex(self.machBox.findText("(None)"))
            return

        self.latBox.clear()
        if '_HLA_DEFAULT_' in self._machlat[vm]:
            self.latBox.addItem(self._machlat[vm]['_HLA_DEFAULT_'].name)
        for k in self._machlat[vm].keys():
            if k == '_HLA_DEFAULT_': continue
            if k == str(self.latBox.currentText()): continue
            self.latBox.addItem(k)

    def _current_mach_lat(self):
        """return the current machine name and lattice object"""
        mach = str(self.machBox.currentText())
        if not mach or mach not in self._machlat:
            self.logger.warn("machine '{0}' is not available: {1}".format(
                mach, self._machlat.keys()))
            return None, None
        lat  = str(self.latBox.currentText())
        if not lat or lat not in self._machlat[mach]:
            self.logger.warn("lattice '{0}' is not available for '{1}':{2}".format(
                lat, mach, self._machlat[mach].keys()))
            return mach, None
        _lat = self._machlat[mach][lat]
        if not _lat: 
            self.logger.warn("lattice '%s' is not available" % lat)
            return mach, None
        return mach, _lat

    def click_machine(self, act):
        self.machBox.setCurrentIndex(self.machBox.findText(act.text()))

    def click_lattice(self):
        #print self.sender()
        #print aphla.machines.lattices()
        latname = str(self.sender().text())
        if latname: self.__setLattice(latname)

    def _newVelemPlots(self, velem, field, title, **kw):
        """plot the field(s) for element"""
        c = kw.get('c', None)
        lat = kw.get('lat', None)
        if lat is not None:
            
        # magprof = lat.getBeamlineProfile()
        fields = [field]
        if field is None: fields = velem.fields()

        plots = []
        for fld in fields:
            print "Processing", velem.name, fld
            p = ApMdiSubPlot()
            #QObject.installEventFilter(p.aplot)
            p.data = ApVirtualElemData(velem, fld, machine=mach, lattice=lat.name)
            if c is not None: p.aplot.setColor(c)
            p.setAttribute(Qt.WA_DeleteOnClose)
            p.setWindowTitle("[%s.%s] %s %s" % (machname, latname, title, fld))
            #p.wid.setMagnetProfile(magprof)
            self.connect(p, SIGNAL("elementSelected(PyQt_PyObject)"), 
                         self.elementSelected)
            self.connect(p, SIGNAL("destroyed()"), self.subPlotDestroyed)
            #print "update the plot"
            p.updatePlot()
            # set the zoom stack
            #print "autozoom"
            p.aplot.setErrorBar(self.error_bar)
            p.wid.autoScaleXY()
            p.aplot.replot()
            self.mdiarea.addSubWindow(p)
            #print "Show"
            p.show()
            plots.append(p)

        print "Enable the buttons"
        if len(self.mdiarea.subWindowList()) > 0:
            self.elemeditor.setEnabled(True)

        return plots


    def subPlotDestroyed(self):
        if len(self.mdiarea.subWindowList()) == 0:
            self.elemeditor.setEnabled(False)
        

    def newOrbitPlots(self):
        mach, lat = self._current_mach_lat()
        bpms = lat.getElementList('BPM')
        vbpmx = aphla.element.merge(bpms, field='x')
        p1s = self._newVelemPlots(vbpmx, 'x', "Hori. Orbit", c=Qt.red)
        vbpmx = aphla.element.merge(bpms, field='y')        
        p2s = self._newVelemPlots(vbpmy, 'y', "Vert. Orbit", Qt.blue)

        if self.timerId is None: self.timerId = self.startTimer(self.dt)
        #print "fullname", p.fullname()

    def newCorrectorPlots(self):
        lat = str(self.latBox.currentText())
        if not lat or lat not in aphla.machines.lattices():
            print "No lattice available"
            return

        p1s = self._newVelemPlots(aphla.machines.HLA_VHCOR, 'x',
                               "Hori. Corr", Qt.red)
        p2s = self._newVelemPlot(lat, aphla.machines.HLA_VVCOR, 'y',
                                "Vert. Corr", Qt.blue)
        if self.timerId is None: self.timerId = self.startTimer(self.dt)
        
    def newPlot(self):
        lat = str(self.latBox.currentText())
        famname = self.sender().text()
        if not lat or lat not in aphla.machines.lattices():
            print "New plot:", famname, "are not available"
            return

        if famname == "H Orbit":
            self._newVelemPlot(lat, aphla.machines.HLA_VBPM, 'x',
                               "Hori. Orbit")
        elif famname == "V Orbit": 
            self._newVelemPlot(lat, aphla.machines.HLA_VBPM, 'y',
                               "Vert. Orbit", Qt.blue)
        elif famname == "H Corrector":
            self._newVelemPlot(lat, aphla.machines.HLA_VHCOR, 'x', "Hori. Corr")
        elif famname == "V Corrector":
            self._newVelemPlot(lat, aphla.machines.HLA_VVCOR, 'y', "Vert. Corr",
                               Qt.blue)
        elif famname == "Quad":
            # plot all fields
            self._newVelemPlot(lat, aphla.machines.HLA_VQUAD, None,
                               "Quadrupole", Qt.black)
        elif famname == "Sext":
            # plot all fields
            self._newVelemPlot(lat, aphla.machines.HLA_VSEXT, None,
                               "Sextupole", Qt.black)
            
        #self.mdiarea.cascadeSubWindows()
        #print self.mdiarea.subWindowList()
        if self.timerId is None: self.timerId = self.startTimer(self.dt)

    def click_markfam(self, on):
        w = self.mdiarea.currentSubWindow()
        if not w: return

        famname = self.sender().text()
        mks = []
        # need to convert to python str
        for elem in self._lat.getElementList(str(famname)):
            if elem.family != famname: continue
            if elem.virtual: continue
            mks.append([elem.name, 0.5*(elem.sb+elem.se)])

        w.setMarkers(mks, on)

    def __setLattice(self, latname):
        if not latname: return
        self._lat = aphla.machines.getLattice(unicode(latname, 'utf-8'))
        aphla.machines.use(str(latname))
        self.logger.info("using lattice '%s'" % latname)
        #self.setLattice(lat)

    def updateMachMenu(self):
        self.machMenu.clear()
        newPlotMenu = QMenu("New", self.machMenu)
        newPlotMenu.addAction("H Orbit", self.newPlot)
        newPlotMenu.addAction("V Orbit", self.newPlot)
        newPlotMenu.addAction("H Corrector", self.newPlot)
        newPlotMenu.addAction("V Corrector", self.newPlot)
        newPlotMenu.addAction("Quad", self.newPlot)
        newPlotMenu.addAction("Sext", self.newPlot)
        self.machMenu.addMenu(newPlotMenu)
        self.machMenu.addSeparator()

        mach_group = QActionGroup(self)
        for mach in self._machlat.keys():
            ac = QAction(mach, self)
            ac.setCheckable(True)
            mach_group.addAction(ac)
            if mach == self.machBox.currentText(): ac.setChecked(True)
            self.machMenu.addAction(ac)
        self.connect(mach_group, SIGNAL("triggered(QAction*)"), self.click_machine)
        self.machMenu.addSeparator()

        fileQuitAction = QAction(QIcon(":/file_quit.png"), "&Quit", self)
        fileQuitAction.setShortcut("Ctrl+Q")
        fileQuitAction.setToolTip("Quit the application")
        fileQuitAction.setStatusTip("Quit the application")
        #fileQuitAction.setIcon(Qt.QIcon(":/filequit.png"))
        self.connect(fileQuitAction, SIGNAL("triggered()"),
                     self.close)
        self.machMenu.addAction(fileQuitAction)
        #print self._machlat.keys()

    def _reset_correctors(self):
        aphla.hlalib._reset_trims()

    def _reset_quadrupoles(self):
        aphla.hlalib._reset_quad()


    def _random_hkick(self):
        hcors = self._lat.getElementList('HCOR')
        i = np.random.randint(len(hcors))
        print "Setting {0}/{1} HCOR".format(i, len(hcors))
        hcors[i].x += 1e-7


    def _random_vkick(self):
        cors = self._lat.getElementList('VCOR')
        i = np.random.randint(len(cors))
        print "kick {0} by 1e-7".format(cors[i].name),
        cors[i].y += 1e-7
        print " kick=",cors[i].y

    def viewDcctPlot(self, on):
        self.dcct.setVisible(on)

    def _active_plots(self):
        i = self.tabs.currentIndex()
        itab = self.tabs.currentWidget()
        return [v for v in itab.findChildren(ApPlot)]
        #return self.tabs.findChildren()

    def liveData(self, on):
        """Switch on/off live data taking"""
        self.live_orbit = on
        
    def errorBar(self, on):
        self.error_bar = on
        for w in self.mdiarea.subWindowList():
            w.aplot.setErrorBar(on)
            w.aplot.replot()

    def setDriftNone(self):
        w = self.mdiarea.currentSubWindow()
        if not w: return
        w.setReferenceData(0.0)

    def setDriftNow(self):
        w = self.mdiarea.currentSubWindow()
        if not w: return
        # use the current data as reference
        w.setReferenceData()

    def setDriftGolden(self):
        #self.plot1.setDrift('golden')
        #self.plot2.setDrift('golden')
        raise RuntimeError("No golden orbit defined yet")

    def zoomOut15(self):
        """zoom out Y"""
        for w in self.mdiarea.subWindowList():
            w.wid.zoomOutY()
            
    def zoomIn15(self):
        """ zoom in Y"""
        for w in self.mdiarea.subWindowList():
            w.wid.zoomInY()

    def zoomAuto(self):
        """auto scale X and Y"""
        for w in self.mdiarea.subWindowList():
            w.wid.autoScaleXY()
            
                    
    def chooseBpm(self):
        bpms = [e.name for e in aphla.getElements('BPM')]
        form = ElementPickDlg(bpms, self._dead_bpm, 'BPM', self)

        if form.exec_(): 
            choice = form.result()
            dead_bpm = []
            for i in range(len(bpms)):
                if bpms[i] in choice: continue
                dead_bpm.append(bpms[i])
            self._dead_bpm = dead_bpm
        self.logger.info("{0} bpms {1} are disabled".format(
                len(self._dead_bpm), self._dead_bpm))

    def chooseCorrector(self):
        cors = [e.name for e in aphla.getElements('COR')]
        form = ElementPickDlg(cors, self._dead_cor, 'COR', self)

        if form.exec_(): 
            choice = form.result()
            dead_elem = []
            for i in range(len(cors)):
                if cors[i] in choice: continue
                dead_elem.append(cors[i])
            self._dead_cor = dead_elem
        self.logger.info("{0} bpms {1} are disabled".format(
                len(self._dead_cor), self._dead_cor))

    def getVisibleElements(self, elemname):

        w = self.mdiarea.currentSubWindow()
        if not w: 
            self.logger.warn("no active plot")
            return []
        elems = _lat.getElementList(elemname)
        xl, xr = w.currentXlim()
        self.logger.info("searching for '{0}' in range [{1}, {2}]".format(
            elemname, xl, xr))
        return [e for e in elems if e.se > xl and e.sb < xr]


    def timerEvent(self, e):
        if not self.elemeditor.isHidden():
            self.elemeditor.updateModelData()

        if self.live_orbit:
            self.itimer += 1
            #self.updatePlots()
            #self.updateStatus()
            for w in self.mdiarea.subWindowList():
                if not isinstance(w, ApMdiSubPlot): continue
                w.updatePlot()
                w.aplot.replot()
            self.statusBar().showMessage("plot updated: {0}".format(
                time.strftime("%F %T")))
        else:
            self.statusBar().showMessage("live update disabled")
            
            
    def singleShot(self):
        for w in self.mdiarea.subWindowList():
            if not isinstance(w, ApMdiSubPlot):  continue
            w.updatePlot()
            w.aplot.replot()

        self.statusBar().showMessage("plot updated: {0}".format(
            time.strftime("%F %T")))

    #def resetPvData(self):
    #    self.obtdata.reset()
    #    #hla.hlalib._reset_trims()

    def elementSelected(self, elems):
        """this action is ignored"""
        mach, lat, elemnames = elems
        _lat = self._machlat[mach][lat]
        
        #elemobjs = _lat.getElementList(elemnames)
        #self._elemed.addElements(elemobjs)

    def activeOrbitPlot(self, field):
        mach = str(self.machBox.currentText())
        lat = str(self.latBox.currentText())
        for w in self.mdiarea.subWindowList():
            #print w.machine(), w.lattice(), w.data.yfield
            if not isinstance(w, ApMdiSubPlot):  continue
            if w.machine() != mach: continue
            if w.lattice() != lat: continue
            if w.data.yfield != field: continue
            return w

        return None


    def _correctOrbit(self, bpms, obt, **kwargs):
        trims = self._lat.getElementList('HCOR')+ self._lat.getElementList('VCOR')
        #print len(bpms), bpms
        #print len(trims), trims
        #print len(obt), obt
        #sp0 = []
        #for tr in trims:
        #    vx, vy = None, None
        #    if 'x' in tr.fields(): vx = tr.get('x', unitsys=None)
        #    if 'y' in tr.fields(): vy = tr.get('y', unitsys=None)
        #    sp0.append((vx, vy))

        repeat = kwargs.pop("repeat", 1)
        kwargs['verbose'] = 0
        for i in range(repeat):
            self.logger.info("setting a local bump")
            QApplication.processEvents()
            aphla.setLocalBump(bpms, trims, obt, **kwargs)
        #return sp0

        #try:
        #    aphla.setLocalBump(bpms, trims, obt)
        #except Exception as e:
        #    QMessageBox.warning(self, "Error:", " {0}".format(e))

    def createLocalBump(self):
        wx = self.activeOrbitPlot('x')
        wy = self.activeOrbitPlot('y')

        if self.corbitdlg is None:
            #print self.obtdata.elem_names
            # assuming BPM has both x and y, the following s are same
            s, x, xe = wx.data.data(nomask=True)
            s, y, ye = wy.data.data(nomask=True)
            x, y = [0.0]*len(s), [0.0] * len(s)
            xunit = wx.data.yunit
            yunit = wy.data.yunit
            #print np.shape(x), np.shape(y)
            self.corbitdlg = OrbitCorrDlg(
                self._lat.getElementList(wx.data.names()), 
                s, x, y, xunit = xunit, yunit=yunit,
                stepsize = 200e-6, 
                orbit_plots=(wx, wy),
                correct_orbit = self._correctOrbit)
            self.corbitdlg.resize(600, 500)
            self.corbitdlg.setWindowTitle("Create Local Bump")
            #self.connect(self.corbitdlg, SIGNAL("finished(int)"),
            #             self.plot1.curve2.setVisible)
            #self.obtxplot.plotDesiredOrbit(self.orbitx_data.golden(), 
            #                            self.orbitx_data.x)
            #self.obtyplot.plotDesiredOrbit(self.orbity_data.golden(), 
            #                            self.orbity_data.x)

        self.corbitdlg.show()
        self.corbitdlg.raise_()
        self.corbitdlg.activateWindow()


def main(par=None):
    #app.setStyle(st)
    mlist = os.environ.get('HLA_MACHINE_LIST', '').split()
    if not mlist: mlist = aphla.machines.machines()
    demo = OrbitPlotMainWindow(machines=mlist)
    #demo.setLattice(aphla.machines.getLattice('V2SR'))
    #demo.setWindowTitle("NSLS-II")
    demo.resize(1000,600)
    #print aphla.machines.lattices()
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
