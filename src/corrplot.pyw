#!/usr/bin/env python

# for debugging, requires: python configure.py --trace ...
if 0:
    import sip
    sip.settracemask(0x3f)

import sys
from PyQt4 import Qt, QtCore, QtGui
import PyQt4.Qwt5 as Qwt
from PyQt4.Qwt5.anynumpy import *

import qrc_resources
import numpy as np
import time
import hla

from cothread.catools import caget, caput

class Spy(Qt.QObject):
    
    def __init__(self, parent):
        Qt.QObject.__init__(self, parent)
        parent.setMouseTracking(True)
        parent.installEventFilter(self)

    # __init__()

    def eventFilter(self, _, event):
        if event.type() == Qt.QEvent.MouseMove:
            self.emit(Qt.SIGNAL("MouseMove"), event.pos())
        return False

    # eventFilter()

# class Spy

class CorrCurve(Qwt.QwtPlotCurve):

    def __init__(self, pvx, pvy):
        """A curve of x versus y data with error bars in dx and dy.

        Horizontal error bars are plotted if dx is not None.
        Vertical error bars are plotted if dy is not None.

        - curvePen is the pen used to plot the curve
        - curveStyle is the style used to plot the curve
        - curveSymbol is the symbol used to plot the symbols
        - errorPen is the pen used to plot the error bars
        - errorCap is the size of the error bar caps
        - errorOnTop is a boolean:

            - if True, plot the error bars on top of the curve,
            - if False, plot the curve on top of the error bars.
        """

        super(CorrCurve, self).__init__()
        self.setPen(Qt.QPen(Qt.Qt.black, 2))
        self.setStyle(Qwt.QwtPlotCurve.Lines)
        self.setSymbol(Qwt.QwtSymbol(Qwt.QwtSymbol.Ellipse,
                                        Qt.QBrush(Qt.Qt.red),
                                        Qt.QPen(Qt.Qt.black, 2),
                                        Qt.QSize(9, 9)))
        self.errorPen = Qt.QPen(Qt.Qt.blue, 2)

        self.x  = []
        self.y  = []
        self.dx = []
        self.dy = []

        self.pv = [pvx, pvy]

        self.__errorbar = False

    def update(self):
        #if not self.live: return None
        if self.pv[0]:
            self.x.append(caget(self.pv[0]))
        if self.pv[1]:
            self.y.append(caget(self.pv[1]))

        Qwt.QwtPlotCurve.setData(self, self.x, self.y)

    # setData()
        
    def boundingRect(self):
        """Return the bounding rectangle of the data, error bars included.
        """

        if len(self.x) == 0 or len(self.y) == 0:
            return Qt.QRectF(-1, 1, 2, 2)

        xmin = min(self.x)
        xmax = max(self.x)
        ymin = min(self.y)
        ymax = max(self.y)

        return Qt.QRectF(xmin, ymin, xmax-xmin, ymax-ymin)
        
    # boundingRect()

# class OrbitPlotCurve

class CorrPlot(Qwt.QwtPlot):
    def __init__(self, parent = None, data = None, plane = 'H'):
        super(CorrPlot, self).__init__(parent)
        #Qwt.QwtPlot.__init__(self, *args)
        
        self.setCanvasBackground(Qt.Qt.white)
        self.plotLayout().setAlignCanvasToScales(True)

        self.xpv = []
        self.ypv = []
        self.curve = []

        #.resize(400, 300)
        grid1 = Qwt.QwtPlotGrid()
        grid1.attach(self)
        grid1.setPen(Qt.QPen(Qt.Qt.black, 0, Qt.Qt.DotLine))

        picker1 = Qwt.QwtPlotPicker(Qwt.QwtPlot.xBottom,
                                   Qwt.QwtPlot.yLeft,
                                   Qwt.QwtPicker.NoSelection,
                                   Qwt.QwtPlotPicker.CrossRubberBand,
                                   Qwt.QwtPicker.AlwaysOn,
                                   self.canvas())
        picker1.setTrackerPen(Qt.QPen(Qt.Qt.red))
        self.setAxisAutoScale(Qwt.QwtPlot.xBottom)
        self.setAxisAutoScale(Qwt.QwtPlot.yLeft)
        
    def appendVariables(self, argx, argy):
        self.xpv.append(argx)
        self.ypv.append(argy)
        self.curve.append(CorrCurve(argx, argy))
        #self.curve[-1].update()
        self.curve[-1].attach(self)

    def alignScales(self):
        self.canvas().setFrameStyle(Qt.QFrame.Box | Qt.QFrame.Plain)
        self.canvas().setLineWidth(1)
        for i in range(Qwt.QwtPlot.axisCnt):
            scaleWidget = self.axisWidget(i)
            if scaleWidget:
                scaleWidget.setMargin(0)
            scaleDraw = self.axisScaleDraw(i)
            if scaleDraw:
                scaleDraw.enableComponent(
                    Qwt.QwtAbstractScaleDraw.Backbone, False)
    def update(self):
        for c in self.curve:
            c.update()
        self.replot()

    # alignScales()

    def scaleVertical(self, factor):
        scalediv = self.axisScaleDiv(Qwt.QwtPlot.yLeft)
        sr, sl = scalediv.upperBound(), scalediv.lowerBound()
        dy = (sr - sl)*(factor - 1)/2.0
        #print "bound:",scalediv.lowerBound(), scalediv.upperBound()
        self.setAxisScale(Qwt.QwtPlot.yLeft, sl - dy, sr + dy)

    def zoomAuto(self):
        bound = self.curve1.boundingRect()
        w = bound.width()
        h = bound.height()
        xmin = bound.left() - w*.05
        xmax = bound.right() + w*.05
        ymin = bound.top() - h*.08
        ymax = bound.bottom() + h*.08
        #print "Width:", w, "   Height:", h
        if w > 0.0: self.setAxisScale(Qwt.QwtPlot.xBottom, xmin, xmax)
        else: self.setAxisAutoScale(Qwt.Qwt.Plot.xBottom)

        if h > 0.0: self.setAxisScale(Qwt.QwtPlot.yLeft, ymin, ymax)
        else: self.setAxisAutoScale(Qwt.QwtPlot.yLeft)

class CorrPlotMainWindow(Qt.QMainWindow):

    def __init__(self, parent = None):
        Qt.QMainWindow.__init__(self, parent)

        # initialize a QwtPlot central widget

        self.plot1 = CorrPlot(self)

        self.plot1.plotLayout().setCanvasMargin(4)
        self.plot1.plotLayout().setAlignCanvasToScales(True)
        self.plot1.setTitle("Horizontal Orbit")


        wid = QtGui.QWidget()
        vbox = QtGui.QHBoxLayout()
        vbox.addWidget(self.plot1)
        wid.setLayout(vbox)
        self.setCentralWidget(wid)

        self.statusBar().showMessage('Hello;')

        #
        # file menu
        #
        self.fileMenu = self.menuBar().addMenu("&File")
        filetest = Qt.QAction("test", self)
        self.connect(filetest, Qt.SIGNAL("triggered()"), self.test)

        fileQuitAction = Qt.QAction(Qt.QIcon(":/filequit.png"), "&Quit", self)
        fileQuitAction.setShortcut("Ctrl+Q")
        fileQuitAction.setToolTip("Quit the application")
        fileQuitAction.setStatusTip("Quit the application")
        #fileQuitAction.setIcon(Qt.QIcon(":/filequit.png"))
        self.connect(fileQuitAction, Qt.SIGNAL("triggered()"),
                     self.close)
        
        #
        self.fileMenu.addAction(filetest)
        self.fileMenu.addAction(fileQuitAction)

        # view
        self.viewMenu = self.menuBar().addMenu("&View")
        # live data
        viewLiveAction = Qt.QAction(Qt.QIcon(":/viewlive.png"),
                                    "Live", self)
        viewLiveAction.setCheckable(True)
        viewLiveAction.setChecked(True)
        self.connect(viewLiveAction, Qt.SIGNAL("toggled(bool)"),
                     self.liveData)
        # errorbar
        viewErrorBarAction = Qt.QAction(Qt.QIcon(":/viewerrorbar.png"),
                                    "Live", self)
        viewErrorBarAction.setCheckable(True)
        viewErrorBarAction.setChecked(True)
        self.connect(viewErrorBarAction, Qt.SIGNAL("toggled(bool)"),
                     self.errorBar)

        # scale
        viewZoomOut15Action = Qt.QAction(Qt.QIcon(":/viewzoomout.png"),
                                         "Zoom out x1.5", self)
        self.connect(viewZoomOut15Action, Qt.SIGNAL("triggered()"),
                     self.zoomOut15)
        viewZoomIn15Action = Qt.QAction(Qt.QIcon(":/viewzoomin.png"),
                                        "Zoom in x1.5", self)
        self.connect(viewZoomIn15Action, Qt.SIGNAL("triggered()"),
                     self.zoomIn15)
        viewZoomAutoAction = Qt.QAction(Qt.QIcon(":/viewzoomauto.png"),
                                        "Auto Fit", self)
        self.connect(viewZoomAutoAction, Qt.SIGNAL("triggered()"),
                     self.zoomAuto)

        self.viewMenu.addAction(viewZoomOut15Action)
        self.viewMenu.addAction(viewZoomIn15Action)
        self.viewMenu.addAction(viewZoomAutoAction)
        self.viewMenu.addSeparator()
        self.viewMenu.addAction(viewLiveAction)
        self.viewMenu.addAction(viewErrorBarAction)

        # help
        self.helpMenu = self.menuBar().addMenu("&Help")

        #toolbar
        #toolbar = Qt.QToolBar(self)
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
        viewToolBar.addAction(viewErrorBarAction)

    def liveData(self, on):
        """Switch on/off live data taking"""
        self.plot1.liveData(on)
        self.plot2.liveData(on)
    
    def errorBar(self, on):
        self.plot1.setErrorBar(on)
        self.plot2.setErrorBar(on)

    def zoomOut15(self):
        self.plot1.scaleVertical(1.5)
        self.plot2.scaleVertical(1.5)

    def zoomIn15(self):
        self.plot1.scaleVertical(1.0/1.5)
        self.plot2.scaleVertical(1.0/1.5)

    def zoomAuto(self):
        self.plot1.zoomAuto()
        self.plot2.zoomAuto()

    def test(self):
        self.plot1.appendVariables("SR:C01-MG:G06B<HCM:H2>Fld-RB",
                                   "SR:C29-BI:G04A<BPM:M1>Pos-X")
        
        t = caget("SR:C01-MG:G06B<HCM:H2>Fld-RB")
        for i in [-4, -2, 0, 2, 4]:
            caput("SR:C01-MG:G06B<HCM:H2>Fld-SP", t + i *.0002)
            print i, caget("SR:C01-MG:G06B<HCM:H2>Fld-RB"),  
            #print caget("SR:C29-BI:G04A<BPM:M1>Pos-X")
            time.sleep(5)
            print i, caget("SR:C01-MG:G06B<HCM:H2>Fld-RB"),  
            print caget("SR:C29-BI:G04A<BPM:M1>Pos-X")
            self.plot1.update()
        time.sleep(2)
        caput("SR:C01-MG:G06B<HCM:H2>Fld-SP", t)
        print caget("SR:C29-BI:G04A<BPM:M1>Pos-X")

def main(args):
    app = Qt.QApplication(args)

    demo = CorrPlotMainWindow()
    demo.resize(800,600)
    demo.show()

    sys.exit(app.exec_())

# main()


# Admire!
if __name__ == '__main__':
    main(sys.argv)

# Local Variables: ***
# mode: python ***
# End: ***
