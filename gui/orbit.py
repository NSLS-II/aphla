#!/usr/bin/env python

#__all__ = [ 'main' ]

# for debugging, requires: python configure.py --trace ...
if 1:
    import sip
    sip.settracemask(0x3f)

from pkg_resources import require
require('cothread>=2.6')

import cothread
app = cothread.iqt()

import aphla
from aphla.catools import caget, caput, camonitor, FORMAT_TIME

import sys

import gui_resources

#import bpmtabledlg
from elementpickdlg import ElementPickDlg
from orbitconfdlg import OrbitPlotConfig
from orbitplot import OrbitPlot, DcctCurrentPlot
from orbitcorrdlg import OrbitCorrDlg
from elemproperty import *


import time
from PyQt4.QtCore import QSize, SIGNAL, Qt
from PyQt4.QtGui import (QMainWindow, QAction, QActionGroup, QTableView,
    QVBoxLayout, QPen, QSizePolicy, QMessageBox, QSplitter, QPushButton,
    QHBoxLayout, QGridLayout, QWidget, QTabWidget, QLabel, QIcon, QActionGroup)

import numpy as np

class OrbitData(object):
    """
    the orbit related data. Raw orbit reading and statistics.

    - *samples* data points kept to calculate the statistics.
    - *yfactor* factor for *y*
    - *x* list of s-coordinate, never updated.
    - *pvs* list of channel names
    - *mode* 'EPICS' | 'sim', default is 'EPICS'
    - *keep* mask for ignore(0) or keep(1) that data point.
    """
    def __init__(self, pvs, **kw):
        n = len(pvs)
        self.samples = kw.get('samples', 10)
        self.yfactor = kw.get('factor', 1e6)
        self.x = kw.get('x', np.array(range(n), 'd'))
        if len(self.x) != n:
            raise ValueError("pv and x are not same size %d != %d" % (n, len(self.x)))
        self.pvs = pvs
        self.pvs_golden = kw.get('pvs_golden', None)

        self.icur, self.icount = -1, 0
        # how many samples are kept for statistics
        self.y      = np.zeros((self.samples, n), 'd')
        for i in range(self.samples):
            self.y[i,:] = caget(self.pvs)
        #self.yref   = np.zeros(n, 'd')
        self.errbar = np.ones(n, 'd') * 1e-15
        self.keep   = np.ones(n, 'i')
        #print self.x, self.y

    def update(self):
        """
        update the orbit data. It retrieve the data with channel access and
        calculate the updated standard deviation. If the current mode is
        'sim', instead of channel access it uses random data.
        """
        # y and errbar sync with plot, not changing data.
        i = self.icur + 1
        if i >= self.samples: i = 0
        self.y[i,:] = caget(self.pvs)
        self.y[i, :] *= self.yfactor
        self.errbar[:] = np.std(self.y, axis=0)
        self.icount += 1
        self.icur = i
        
    def reset(self):
        """
        clear the history data points and statistics.
        """
        self.icur, self.icount = -1, 0
        self.y.fill(0.0)
        self.errbar.fill(0.0)
        #self.update()

    def min(self, axis='s'):
        c, i = divmod(self.icount - 1, self.samples)
        data = np.compress(self.keep, self.y, axis=1)
        return np.min(data)

    def max(self, axis='s'):
        c, i = divmod(self.icount - 1, self.samples)
        data = np.compress(self.keep, self.y, axis=1)
        return np.max(data)
        
    def average(self, axis='s'):
        """average of the whole curve"""
        c, i = divmod(self.icount - 1, self.samples)
        data = np.compress(self.keep, self.y, axis=1)
        return np.average(data)

    def std(self, axis='s'):
        """
        std of the curve
        - axis='t' std over time axis for each PV
        - axis='s' std over all PV for the latest dataset
        """
        if axis == 't': ax = 1
        elif axis == 's': ax = 0
        y = np.compress(self.keep, self.y, axis=1)
        return np.std(y, axis = ax)

    def data(self, field="orbit", nomask=False):
        """
        field = [ 'orbit' | 'std' ]
        """
        if self.icur < 0:
            n = len(self.x)
            x1, y1, e1 = self.x, np.zeros(n, 'd'), np.zeros(n, 'd')

        i = self.icur
        if field == 'orbit':
            x1 = self.x
            y1 = self.y[i,:]
            e1 = self.errbar
        elif field == 'std':
            x1 = self.x
            y1 = np.std(self.y, axis=0)
            e1 = np.zeros(len(x1), 'd')
        if nomask: return x1, y1, e1
        else:
            return np.compress(self.keep, [x1, y1, e1], axis=1)

    def golden(self, nomask=False):
        if self.pvs_golden is None:
            d = np.zeros(len(self.pvs), 'd')
        else:
            d = np.array(caget(self.pvs_golden)) * self.yfactor

        if nomask: return d
        else: return np.compress(self.keep, d)

    def unmasked(self, d):
        """
        
        """
        n = len(self.keep)
        ret = np.zeros(n, 'd')
        dc = [x for x in d]
        for i in range(n):
            if not self.keep[i]: continue
            ret[i] = dc.pop(0)
        return ret


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
    def __init__(self, parent = None, accname='us_nsls2_sr'):
        QMainWindow.__init__(self, parent)
        self.setIconSize(QSize(48, 48))
        orbit_conf_file = accname + "_orbit.json"
        if aphla.conf.inHome(orbit_conf_file):
            aphla.logger.info("Using config file '%s' from $HOME" % 
                              orbit_conf_file)
        self.config = OrbitPlotConfig(None, 
                                      aphla.conf.filename(orbit_conf_file))

        self.dcct = DcctCurrentPlot()
        self.dcct.curve.setData(np.linspace(0, 50, 50), np.linspace(0, 50, 50))
        self.dcct.setMinimumHeight(100)
        self.dcct.setMaximumHeight(150)

        print __name__, ":"
        print "  WARNING: Using hardcoded PV: 'SR:C00-BI:G00{DCCT:00}CUR-RB'"
        try:
            # load fake current
            print "loading fake current"
            t = caget('SR:C00-BI:G00{DCCT:00}CUR-RB', format=FORMAT_TIME)
            #self.dcct._loadFakeData(t.timestamp, t.real, 4.0, 500.0, 24.0)
            print "current: ", t
            camonitor('SR:C00-BI:G00{DCCT:00}CUR-RB', self.dcct.updateDcct, 
                      format=FORMAT_TIME)
        except:
            print "WARNING: timedout ?"
            t0 = time.time()
            t = np.linspace(t0 - 8*3600*24, t0, 100)
            self.dcct.curve.t = t
            v = 500*np.exp((t[0] - t[:50])/(4*3600*24))
            self.dcct.curve.v = v.tolist()+v.tolist()
            
            self.dcct.updatePlot()

        # initialize a QwtPlot central widget
        #bpm = hla.getElements('BPM')
        self.pvx = [b[1]['rb'].encode('ascii') for b in self.config.data['bpmx']]
        #print pvx
        self.pvy = [b[1]['rb'].encode('ascii') for b in self.config.data['bpmy']]
        self.pvsx = [b[1]['s'] for b in self.config.data['bpmx']]
        self.pvsy = [b[1]['s'] for b in self.config.data['bpmy']]
        self.bpm = [b[0] for b in self.config.data['bpmx']]
        pvsx_golden = [b[1]['golden'].encode("ascii") 
                       for b in self.config.data['bpmx']]
        pvsy_golden = [b[1]['golden'].encode("ascii") 
                       for b in self.config.data['bpmy']]
        self.orbitx_data = OrbitData(pvs = self.pvx, x = self.pvsx, 
                                     pvs_golden = pvsx_golden)
        self.orbity_data = OrbitData(pvs = self.pvy, x = self.pvsy,
                                     pvs_golden = pvsy_golden)
        self.orbitx_data.update()
        self.orbity_data.update()

        picker = [(v[1], v[2], v[0]) for v in self.config.data['magnetpicker']]
        self.plot1 = OrbitPlot(self, self.orbitx_data, picker_profile = picker,
                               magnet_profile = self.config.data['magnetprofile'])
        #self.plot1.curve1.setPen(QPen(Qt.blue, 2))
        self.plot2 = OrbitPlot(self, self.orbity_data, picker_profile = picker,
                               magnet_profile = self.config.data['magnetprofile'])
        self.plot3 = OrbitPlot(self, self.orbitx_data, data_field='std',
            errorbar=False, picker_profile = picker,
                               magnet_profile = self.config.data['magnetprofile'])
        self.plot4 = OrbitPlot(self, self.orbity_data, data_field='std',
            errorbar=False, picker_profile = picker,
                               magnet_profile = self.config.data['magnetprofile'])

        #print pvsx_golden, pvsy_golden
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

        self.elems = ElementPropertyTabs()
        self.elems.setVisible(False)
        self.elems.setTabsClosable(True)
        self.connect(self.plot1, SIGNAL("elementSelected(PyQt_PyObject)"),
                     self.elems.addElement)
        self.connect(self.plot2, SIGNAL("elementSelected(PyQt_PyObject)"),
                     self.elems.addElement)

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
        self.orbitSplitter.addWidget(self.elems)
        #majbox.addWidget(self.tabs, 1, 0)
        #majbox.addWidget(self.elems, 1, 1)
        majbox.addWidget(self.orbitSplitter) #, 1, 0, 1, 2)
        cwid.setLayout(majbox)

        wid1 = QWidget()
        gbox = QGridLayout()
        #self.plot1.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        #self.plot2.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        gbox.addWidget(self.plot1, 0, 1)
        gbox.addWidget(self.plot2, 1, 1)
        gbox.setRowStretch(0, 0.5)
        gbox.setRowStretch(1, 0.5)
        wid1.setLayout(gbox)        
        self.tabs.addTab(wid1, "Orbit Plot")

        wid1 = QWidget()
        vbox1 = QVBoxLayout()
        vbox1.addWidget(self.plot3)
        vbox1.addWidget(self.plot4)
        wid1.setLayout(vbox1)
        self.tabs.addTab(wid1, "Std")

        #wid1 = QWidget()
        #vbox = QGridLayout()
        #vbox.addWidget(self.plot5, 0, 1)
        ##vbox.addWidget(self.lbplt2info, 1, 0)
        ##vbox.addWidget(self.plot2, 1, 1)
        #wid1.setLayout(vbox)
        #self.tabs = QTabWidget()
        #self.tabs.addTab(wid1, "Orbit Steer")

        self.setCentralWidget(cwid)

        #self.setCentralWidget(OrbitPlot())
        #print self.plot1.sizeHint()
        #print self.plot1.minimumSizeHint()

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
        viewLiveAction.setChecked(True)
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
        self.viewMenu.addAction(viewDcct)

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
        dt = 800
        self.timerId = self.startTimer(dt)
        self.corbitdlg = None # orbit correction dlg

    def viewDcctPlot(self, on):
        self.dcct.setVisible(on)

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
        i = self.tabs.currentIndex()
        if i == 0:
            if self.plot1.live: self.plot1.updatePlot()
            if self.plot2.live: self.plot2.updatePlot()
        elif i == 1:
            if self.plot3.live: self.plot3.updatePlot()
            if self.plot4.live: self.plot4.updatePlot()
        self.dcct.updatePlot()

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

    def plotDesiredOrbit(self, x, y):
        #print "plot: ", x, y
        self.plot1.curve2.setData(self.pvsx, x)
        self.plot2.curve2.setData(self.pvsy, y)

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
                self.orbity_data.golden(), 
                self.plotDesiredOrbit, self.correctOrbit, self)
            self.corbitdlg.resize(600, 300)
            self.corbitdlg.setWindowTitle("Create Local Bump")
        self.corbitdlg.show()
        self.corbitdlg.raise_()
        self.corbitdlg.activateWindow()


def main():
    aphla.initNSLS2V1()
    #app = QApplication(args)
    #app.setStyle(st)
    if '--sim' in sys.argv:
        print "CA offline:", aphla.catools.CA_OFFLINE
        aphla.catools.CA_OFFLINE = True
    demo = OrbitPlotMainWindow(accname = 'us_nsls2_vsr')
    demo.setWindowTitle("NSLS-II SR")
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
