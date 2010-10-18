#!/usr/bin/env python

# orbit_monitor.pyw --- Simple Qt4 application embedding matplotlib canvases
#
# Lingyun Yang (lyyang@bnl.gov)
#

import sys, os, random, time
from PyQt4 import QtGui, QtCore

from numpy import arange, sin, pi
import matplotlib.pylab as plt
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.dates import date2num, DateFormatter
from datetime import datetime

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
        try:
            cur = catools.caget("SR:C00-BI:G00<DCCT:00>CUR-RB")
        except cothread.cothread.Timedout:
            print "Time out"
            cur = 0
        self.MAX_LEN = 20000
        if os.path.exists("beam.txt"):
            dat = open("beam.txt", 'r').readlines()
            self.t, self.current = [], []
            for line in dat:
                self.t.append(float(line.split()[0]))
                self.current.append(float(line.split()[1]))
        else:
            self.t = [date2num(datetime.now())]
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
        try:
            cur = catools.caget("SR:C00-BI:G00<DCCT:00>CUR-RB")
        except cothread.cothread.Timedout:
            print "Time out"
            cur = 0.0
        #print self.t, self.current
        if len(self.t) % 100 == 0:
            f = open("beam.txt", 'w')
            for i in range(len(self.t)):
                f.write("%f %f\n" %(self.t[i], self.current[i]))
            f.close()
            #print self.t[-1], self.current[-1]
        self.t.append(date2num(datetime.now()))
        self.current.append(float(cur))
        if len(self.t) > self.MAX_LEN:
            self.t.pop(0)
            self.current.pop(0)
        #self.axes.fill(self.t, self.current, 'r.')
        self.axes.plot_date(self.t, self.current, 'b-')
        self.axes.xaxis.set_major_formatter(DateFormatter('%m-%d-%H-%M'))
        labels = self.axes.get_xticklabels()
        plt.setp(labels, rotation=30, fontsize = 10)
        self.axes.grid(True)
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
        self.lat = latman.LatticeManager("../machine/nsls2/conf/lat_conf_table.txt")
        #print self.t, self.current

    def get_orbit(self, lat, delay=2):
        time.sleep(delay)
        bpm = lat.group_index("BPMX")
        try:
            d = catools.caget("SR:C00-Glb:G00<POS:00>RB-S")
            vs = [v for v in d]
            d = catools.caget("SR:C00-Glb:G00<ORBIT:00>RB-X")
            vx = [v for v in d]
            d = catools.caget("SR:C00-Glb:G00<ORBIT:00>RB-Y")
            vy = [v for v in d]
        except cothread.cothread.Timedout:
            print "Time out when retrieve orbit"
            n = max(bpm) + 1
            #n = 1
            vs = arange(n)
            vx = [0.0] * n
            vy = [0.0] * n

        if not self.BPM_ONLY:
            return vs, vx, vy
        #print len(vs), len(vx), len(vy)
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
