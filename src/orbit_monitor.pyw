#!/usr/bin/env python

# orbit_monitor.py --- Simple Qt4 application embedding matplotlib canvases
#
# Copyright (C) 2005 Florent Rougon
#               2006 Darren Dale
#
# This file is an example program for matplotlib. It may be used and
# modified with no restriction; raw copies as well as modified versions
# may be distributed without limitation.

import sys, os, random, time
from PyQt4 import QtGui, QtCore

from numpy import arange, sin, pi
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

import cothread
import cothread.catools as catools
import latman

progname = os.path.basename(sys.argv[0])
progversion = "0.1"


class MyMplCanvas(FigureCanvas):
    """Ultimately, this is a QWidget (as well as a FigureCanvasAgg, etc.)."""
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        # We want the axes cleared every time plot() is called
        self.axes.hold(False)

        self.compute_initial_figure()

        #
        FigureCanvas.__init__(self, fig)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self,
                                   QtGui.QSizePolicy.Expanding,
                                   QtGui.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

    def compute_initial_figure(self):
        pass


class MyStaticMplCanvas(MyMplCanvas):
    """Simple canvas with a sine plot."""
    def compute_initial_figure(self):
        t = arange(0.0, 3.0, 0.01)
        s = sin(2*pi*t)
        self.axes.plot(t, s)


class MyDynamicMplCanvas(MyMplCanvas):
    """A canvas that updates itself every second with a new plot."""
    def __init__(self, *args, **kwargs):
        cur = catools.caget("SR:C00-BI:G00<DCCT:00>CUR:RB")
        self.MAX_LEN = 20000
        if os.path.exists("beam.txt"):
            dat = open("beam.txt", 'r').readlines()
            self.t, self.current = [], []
            for line in dat:
                self.t.append(float(line.split()[0]))
                self.current.append(float(line.split()[1]))
        else:
            self.t = [(time.time() - 1276896402.0)/3600.0]
            self.current = [float(cur)]
        MyMplCanvas.__init__(self, *args, **kwargs)
        timer = QtCore.QTimer(self)
        QtCore.QObject.connect(timer, QtCore.SIGNAL("timeout()"), self.update_figure)
        timer.start(4321)
        #print self.t, self.current

    def compute_initial_figure(self):
        #self.axes.plot([0, 1, 2, 3], [1, 2, 0, 4], 'r')
        pass

    def update_figure(self):
        # Build a list of 4 random integers between 0 and 10 (both inclusive)
        #l = [ random.randint(0, 10) for i in xrange(4) ]
        cur = catools.caget("SR:C00-BI:G00<DCCT:00>CUR:RB")
        #print self.t, self.current
        if len(self.t) % 100 == 0:
            f = open("beam.txt", 'w')
            for i in range(len(self.t)):
                f.write("%f %f\n" %(self.t[i], self.current[i]))
            f.close()
            print self.t[-1], self.current[-1]
        self.t.append((time.time() - 1276896402.0)/3600.0)
        self.current.append(float(cur))
        if len(self.t) > self.MAX_LEN:
            self.t.pop(0)
            self.current.pop(0)
        self.axes.plot(self.t, self.current, 'r-')
        self.draw()


class OrbitPlotCanvas(MyMplCanvas):
    """A canvas that updates itself every second with a new plot."""
    def __init__(self, *args, **kwargs):        
        self.BPM_ONLY = True
        MyMplCanvas.__init__(self, *args, **kwargs)
        timer = QtCore.QTimer(self)
        QtCore.QObject.connect(timer, QtCore.SIGNAL("timeout()"), self.update_figure)
        timer.start(3000)
        self.axes.hold(True)
        self.lat = latman.LatticeManager("../nsls2/conf/lattice_channels.txt")
        #print self.t, self.current

    def get_orbit(self, lat, delay=2):
        time.sleep(delay)
        vs = [v for v in catools.caget("SR:C00-Glb:G00<POS:00>RB:S")]
        vx = [v for v in catools.caget("SR:C00-Glb:G00<ORBIT:00>RB:X")]
        vy = [v for v in catools.caget("SR:C00-Glb:G00<ORBIT:00>RB:Y")]
        if not self.BPM_ONLY:
            return vs, vx, vy
        #print len(vs), len(vx), len(vy)
        bpm = lat.group_index("@BpmX")
        #print bpm
        s = [vs[i] for i in bpm]
        x = [vx[i] for i in bpm]
        y = [vy[i] for i in bpm]
        return s, x, y

    def compute_initial_figure(self):
        #self.axes.plot([0, 1, 2, 3], [1, 2, 0, 4], 'r')
        pass

    def update_figure(self):
        # Build a list of 4 random integers between 0 and 10 (both inclusive)
        #l = [ random.randint(0, 10) for i in xrange(4) ]
        s, x, y = self.get_orbit(self.lat)
        self.axes.cla()
        self.axes.plot(s, x, 'rx-')
        self.axes.plot(s, y, 'go-')
        #self.axes.ylabel("Orbit [mm]")
        self.draw()

class ApplicationWindow(QtGui.QMainWindow):
    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setWindowTitle("application main window")

        self.file_menu = QtGui.QMenu('&File', self)
        self.file_menu.addAction('&Quit', self.fileQuit,
                                 QtCore.Qt.CTRL + QtCore.Qt.Key_Q)
        self.menuBar().addMenu(self.file_menu)

        self.help_menu = QtGui.QMenu('&Help', self)
        self.menuBar().addSeparator()
        self.menuBar().addMenu(self.help_menu)

        self.help_menu.addAction('&About', self.about)

        self.main_widget = QtGui.QWidget(self)

        l = QtGui.QVBoxLayout(self.main_widget)
        #sc = MyStaticMplCanvas(self.main_widget, width=8, height=4, dpi=100)
        sc = OrbitPlotCanvas(self.main_widget, width=8, height=4, dpi=100)
        dc = MyDynamicMplCanvas(self.main_widget, width=8, height=4, dpi=100)
        l.addWidget(sc)
        l.addWidget(dc)

        self.main_widget.setFocus()
        self.setCentralWidget(self.main_widget)

        self.statusBar().showMessage("All hail matplotlib!", 2000)
        self.file_menu.addAction('&Refresh', sc.update_figure) 

    def fileQuit(self):
        self.close()

    def closeEvent(self, ce):
        self.fileQuit()

    def about(self):
        QtGui.QMessageBox.about(self, "About %s" % progname,
u"""%(prog)s version %(version)s
Copyright \N{COPYRIGHT SIGN} 2005 Florent Rougon, 2006 Darren Dale

This program is a simple example of a Qt4 application embedding matplotlib
canvases.

It may be used and modified with no restriction; raw copies as well as
modified versions may be distributed without limitation."""
% {"prog": progname, "version": progversion})


qApp = QtGui.QApplication(sys.argv)

aw = ApplicationWindow()
aw.setWindowTitle("%s" % progname)
aw.show()
sys.exit(qApp.exec_())
#qApp.exec_()
