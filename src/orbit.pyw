#!/usr/bin/env python

# for debugging, requires: python configure.py --trace ...
if 0:
    import sip
    sip.settracemask(0x3f)

import sys
import cothread, hla
from cothread.catools import camonitor
app = cothread.iqt()

from PyQt4 import Qt, QtCore, QtGui
import PyQt4.Qwt5 as Qwt
from PyQt4.Qwt5.anynumpy import *

import qrc_resources
import numpy as np


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

class OrbitPlotCurve(Qwt.QwtPlotCurve):

    SAMPLES = 10
    def __init__(self, pvs,
                 curvePen = Qt.QPen(Qt.Qt.NoPen),
                 curveStyle = Qwt.QwtPlotCurve.Lines,
                 curveSymbol = Qwt.QwtSymbol(),
                 errorPen = Qt.QPen(Qt.Qt.NoPen),
                 errorCap = 0,
                 errorOnTop = False,
                 ):
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

        Qwt.QwtPlotCurve.__init__(self)
        self.setPen(curvePen)
        self.setStyle(curveStyle)
        self.setSymbol(curveSymbol)
        self.errorPen = errorPen
        self.errorCap = errorCap
        self.errorOnTop = errorOnTop
        
        n = len(pvs)
        self.pvs = pvs
        #self.x = np.zeros(n, 'd')
        self.x = np.array(range(n))
        self.y = np.zeros((n, self.SAMPLES), 'd')
        self.y2 = np.zeros(n, 'd')
        self.__live = False

        self.moni = camonitor(pvs, self.updatePvs)

        self.__errorbar = True

        self.update()

    def updatePvs(self, val, idx):
        self.y[idx, 1:] = self.y[idx,:-1]
        self.y[idx, 0] = val
        self.y2[idx] = np.std(self.y[idx,:])

    def update(self):
        Qwt.QwtPlotCurve.setData(self, self.x, self.y[:,0])

    # setData()
        
    def boundingRect(self):
        """Return the bounding rectangle of the data, error bars included.
        """
        xmin = min(self.x)
        xmax = max(self.x)
        ymin = min(self.y[:,0] - self.y2)
        ymax = max(self.y[:,0] + self.y2)
        return Qt.QRectF(xmin, ymin, xmax-xmin, ymax-ymin)
        
    # boundingRect()

    def drawFromTo(self, painter, xMap, yMap, first, last = -1):
        """Draw an interval of the curve, including the error bars

        painter is the QPainter used to draw the curve

        xMap is the Qwt.QwtDiMap used to map x-values to pixels

        yMap is the Qwt.QwtDiMap used to map y-values to pixels
        
        first is the index of the first data point to draw

        last is the index of the last data point to draw. If last < 0, last
        is transformed to index the last data point
        """

        if last < 0:
            last = self.dataSize() - 1

        if self.errorOnTop:
            Qwt.QwtPlotCurve.drawFromTo(self, painter, xMap, yMap, first, last)

        # draw the error bars
        painter.save()
        painter.setPen(self.errorPen)

        # draw the error bars with caps in the y direction
        if self.y2 is not None:
            # draw the bars
            if len(self.y2.shape) in [0, 1]:
                ymin = (self.y[:,0] - self.y2)
                ymax = (self.y[:,0] + self.y2)
            else:
                ymin = (self.y[:,0] - self.y2[0])
                ymax = (self.y[:,0] + self.y2[1])
            x = self.x
            n, i, = len(x), 0
            lines = []
            while i < n:
                xi = xMap.transform(x[i])
                lines.append(
                    Qt.QLine(xi, yMap.transform(ymin[i]),
                                 xi, yMap.transform(ymax[i])))
                i += 1
            painter.drawLines(lines)
            # draw the caps
            if self.errorCap > 0:
                cap = self.errorCap/2
                n, i, j = len(x), 0, 0
                lines = []
                while i < n:
                    xi = xMap.transform(x[i])
                    lines.append(
                        Qt.QLine(xi - cap, yMap.transform(ymin[i]),
                                     xi + cap, yMap.transform(ymin[i])))
                    lines.append(
                        Qt.QLine(xi - cap, yMap.transform(ymax[i]),
                                     xi + cap, yMap.transform(ymax[i])))
                    i += 1
            painter.drawLines(lines)

        painter.restore()

        if not self.errorOnTop:
            Qwt.QwtPlotCurve.drawFromTo(self, painter, xMap, yMap, first, last)

    # drawFromTo()
    def liveData(self, on):
        pass

    def setErrorBar(self, on):
        self.__errorbar = on

    def singleShot(self):
        #print "Curve single shot"
        self.update()
        
class OrbitPlot(Qwt.QwtPlot):
    def __init__(self, parent = None, pvs = None, plane = 'H'):
        super(OrbitPlot, self).__init__(parent)
        #Qwt.QwtPlot.__init__(self, *args)
        
        self.setCanvasBackground(Qt.Qt.white)
        #self.alignScales()

        # Initialize data
        errorOnTop = False # uncomment to draw the curve on top of the error bars
        # errorOnTop = True # uncomment to draw the error bars on top of the curve
        
        #self.setTitle("An Orbit Plot")
        #self.insertLegend(Qwt.QwtLegend(), Qwt.QwtPlot.BottomLegend);

        self.setAxisAutoScale(Qwt.QwtPlot.xBottom)
        self.setAxisAutoScale(Qwt.QwtPlot.yLeft)

        self.plotLayout().setAlignCanvasToScales(True)

        self.curve1 = OrbitPlotCurve(
            pvs,
            curvePen = Qt.QPen(Qt.Qt.black, 2),
            curveSymbol = Qwt.QwtSymbol(
                Qwt.QwtSymbol.Ellipse,
                Qt.QBrush(Qt.Qt.red),
                Qt.QPen(Qt.Qt.black, 2),
                Qt.QSize(9, 9)),
            errorPen = Qt.QPen(Qt.Qt.blue, 1),
            errorCap = 10,
            errorOnTop = errorOnTop,
            )

        self.curve1.attach(self)
        self.bound = self.curve1.boundingRect()
        #print "BD",self.bound
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
        
        
        self.__live = False
        self.timerId = self.startTimer(500)

        #self.phase = 0.0

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

    # alignScales()

    def timerEvent(self, e):
        # y moves from left to right:
        # shift y array right and assign new value y[0]
        #self.y = concatenate((self.y[:1], self.y[:-1]), 1)
        if not self.__live: return

        self.curve1.update()

        #self.setAxisScale(Qwt.QwtPlot.xBottom, min(self.x), max(self.x))
        #self.setAxisScale(Qwt.QwtPlot.yLeft, 0, 2)

        #self.setAxisAutoScale(Qwt.QwtPlot.xBottom)
        #self.setAxisAutoScale(Qwt.QwtPlot.yLeft)
        #print self.curve1.boundingRect()
        #print self.bound

        #self.bound.united(self.curve1.boundingRect())
        #bd = self.curve1.boundingRect()
        #print "returned", bd.left(), bd.right(), bd.top(), bd.bottom()
        #self.bound = self.bound.united(self.curve1.boundingRect())
        #print self.bound.left(), self.bound.right()
        #print "B-T",self.bound.bottom(), self.bound.top()

        #self.setAxisScale(Qwt.QwtPlot.xBottom,
        #                  self.bound.left(), self.bound.right())
        #self.setAxisScale(Qwt.QwtPlot.yLeft,
        #                  self.bound.top(), self.bound.bottom())
        
        #self.setAxisScale(Qwt.QwtPlot.yLeft, 0, 2)

        self.replot()
        #self.zoomer1.setZoomBase()


    def singleShot(self):
        #print "Plot :: singleShot"
        self.curve1.singleShot()
        self.replot()


    def liveData(self, on):
        self.__live = on
        self.curve1.liveData(on)
        return None

        #print "Working on timer:", self.timerId, 
        if on:
            self.data.start()
            self.timerId = self.startTimer(500)
            #print "Enable timer:", self.timerId
        else:
            self.data.stop()
            self.killTimer(self.timerId)
            #print "Disabled timer:", self.timerId
            self.timerId = -1
            
    def setErrorBar(self, on):
        self.curve1.setErrorBar(on)
        #d = self.curve1.data()
        #x = [d.x(i) for i in range(d.size())]
        #y = [d.y(i) for i in range(d.size())]
        #self.curve1.setData(x, y, self.curve1.dx(), self.curve1.dy())
        self.replot()

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

class OrbitPlotMainWindow(Qt.QMainWindow):

    def __init__(self, parent = None):
        Qt.QMainWindow.__init__(self, parent)

        # initialize a QwtPlot central widget
        pvx = [p[0] for p in hla._orbit.pvrb]
        pvy = [p[1] for p in hla._orbit.pvrb]

        self.plot1 = OrbitPlot(self, pvx)
        self.plot2 = OrbitPlot(self, pvy)

        self.plot1.plotLayout().setCanvasMargin(4)
        self.plot1.plotLayout().setAlignCanvasToScales(True)
        self.plot1.setTitle("Horizontal Orbit")
        self.plot2.plotLayout().setCanvasMargin(4)
        self.plot2.plotLayout().setAlignCanvasToScales(True)
        self.plot2.setTitle("Vertical Orbit")

        wid1 = QtGui.QWidget()
        vbox = QtGui.QVBoxLayout()
        vbox.addWidget(self.plot1)
        vbox.addWidget(self.plot2)
        wid1.setLayout(vbox)
        wid = QtGui.QTabWidget()
        wid.addTab(wid1, "test1")
        wid.addTab(Qt.QLabel("Hello"), "test2")
        wid.addTab(QtGui.QLabel("H3"), "test3")
        self.setCentralWidget(wid)

        self.zoomer1 = Qwt.QwtPlotZoomer(Qwt.QwtPlot.xBottom,
                                        Qwt.QwtPlot.yLeft,
                                        Qwt.QwtPicker.DragSelection,
                                        Qwt.QwtPicker.AlwaysOff,
                                        self.plot1.canvas())
        self.zoomer1.setRubberBandPen(Qt.QPen(Qt.Qt.black))

        self.zoomer2 = Qwt.QwtPlotZoomer(Qwt.QwtPlot.xBottom,
                                        Qwt.QwtPlot.yLeft,
                                        Qwt.QwtPicker.DragSelection,
                                        Qwt.QwtPicker.AlwaysOff,
                                        self.plot2.canvas())
        self.zoomer2.setRubberBandPen(Qt.QPen(Qt.Qt.black))

        #self.setCentralWidget(OrbitPlot())

        self.statusBar().showMessage('Hello;')

        #
        # file menu
        #
        self.fileMenu = self.menuBar().addMenu("&File")
        fileQuitAction = Qt.QAction(Qt.QIcon(":/filequit.png"), "&Quit", self)
        fileQuitAction.setShortcut("Ctrl+Q")
        fileQuitAction.setToolTip("Quit the application")
        fileQuitAction.setStatusTip("Quit the application")
        #fileQuitAction.setIcon(Qt.QIcon(":/filequit.png"))
        self.connect(fileQuitAction, Qt.SIGNAL("triggered()"),
                     self.close)
        
        #
        self.fileMenu.addAction(fileQuitAction)

        # view
        self.viewMenu = self.menuBar().addMenu("&View")
        # live data
        viewLiveAction = Qt.QAction(Qt.QIcon(":/viewlive.png"),
                                    "Live", self)
        viewLiveAction.setCheckable(True)
        viewLiveAction.setChecked(False)
        self.connect(viewLiveAction, Qt.SIGNAL("toggled(bool)"),
                     self.liveData)

        viewSingleShotAction = Qt.QAction(Qt.QIcon(":/viewsingleshot.png"),
                                       "Single Shot", self)
        self.connect(viewSingleShotAction, Qt.SIGNAL("triggered()"),
                     self.singleShot)

        # errorbar
        viewErrorBarAction = Qt.QAction(Qt.QIcon(":/viewerrorbar.png"),
                                    "Errorbar", self)
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
        self.viewMenu.addAction(viewSingleShotAction)
        self.viewMenu.addSeparator()
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
        viewToolBar.addAction(viewSingleShotAction)
        viewToolBar.addAction(viewErrorBarAction)
        
    def liveData(self, on):
        """Switch on/off live data taking"""
        #print "MainWindow: liveData", on
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

    def singleShot(self):
        #print "Main: Singleshot"
        self.plot1.singleShot()
        self.plot2.singleShot()

def main(args):
    #app = Qt.QApplication(args)
    demo = OrbitPlotMainWindow()
    demo.resize(800,600)
    demo.show()

    #sys.exit(app.exec_())
    cothread.WaitForQuit()

# main()


# Admire!
if __name__ == '__main__':
    #hla.clean_init()
    main(sys.argv)

# Local Variables: ***
# mode: python ***
# End: ***
