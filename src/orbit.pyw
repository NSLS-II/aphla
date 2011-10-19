#!/usr/bin/env python

# for debugging, requires: python configure.py --trace ...
if 0:
    import sip
    sip.settracemask(0x3f)

import sys
import cothread, hla
from epicsdatamonitor import CaDataMonitor

app = cothread.iqt(use_timer=True)


from PyQt4.QtCore import (PYQT_VERSION_STR, QFile, QFileInfo, QSettings,
        QObject, QString, QT_VERSION_STR, QTimer, QVariant, Qt, SIGNAL,
        QSize, QRectF, QLine)
from PyQt4.QtGui import (QAction, QActionGroup, QApplication, QWidget,
        QDockWidget, QFileDialog, QFrame, QIcon, QImage, QImageReader,
        QImageWriter, QInputDialog, QKeySequence, QLabel, QListWidget,
        QMainWindow, QMessageBox, QPainter, QPixmap, QPrintDialog,
        QPrinter, QSpinBox, QPen, QBrush, QVBoxLayout, QTabWidget,
        QTableWidget)

hla.machines.initNSLS2VSRTxt()

import PyQt4.Qwt5 as Qwt
from PyQt4.Qwt5.anynumpy import *

import qrc_resources
import numpy as np

#import bpmtabledlg
from elementpickdlg import ElementPickDlg

class MagnetPicker(Qwt.QwtPlotPicker):
    def __init__(self, canvas):
        Qwt.QwtPlotPicker.__init__(self, Qwt.QwtPlot.xBottom,
                          Qwt.QwtPlot.yLeft,
                          Qwt.QwtPicker.NoSelection,
                          Qwt.QwtPlotPicker.CrossRubberBand,
                          Qwt.QwtPicker.AlwaysOn,
                          canvas)
        
        self.profile = []

    def addMagnetProfile(self, sb, se, name, minlen = 0.2):
        if se < sb: 
            raise ValueError("s range of %s is wrong, must be se > sb" % name)

        c = (sb + se)/2.0
        if se - sb < minlen:
            w = minlen
        else:
            w = se - c

        if not self.profile:
            self.profile.append((c-w, c+w, name))
            return
        elif self.profile[-1][0] < c - w:
            self.profile.append((c-w, c+w, name))
            return

        for i,m in enumerate(self.profile):
            if m[0] < c - w: continue
            self.profile.insert(i, (c-w, c+w, name))
            return

    def trackerTextF(self, pos):
        s = []
        x, y = pos.x(), pos.y()
        for m in self.profile:
            if x > m[0] and x < m[1]:
                s.append(m[2])
        return Qwt.QwtText("%.3f, %.3f\n%s" % (pos.x(), pos.y(), '\n'.join(s)))


class OrbitPlotCurve(Qwt.QwtPlotCurve):
    """Orbit"""
    SAMPLES = 10
    def __init__(self, x, pvs,
                 curvePen = QPen(Qt.NoPen),
                 curveStyle = Qwt.QwtPlotCurve.Lines,
                 curveSymbol = Qwt.QwtSymbol(),
                 errorPen = QPen(Qt.NoPen),
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
        
        if len(pvs) != len(x):
            raise ValueError("pv and x are not same size")

        n = len(x)
        self.x      = np.array(x)
        self.y      = np.zeros(n, 'd')
        self.yref   = np.zeros(n, 'd')
        self.errbar = np.zeros(n, 'd')
        self.camonitor = CaDataMonitor(pvs, samples=self.SAMPLES)
        self.mask = np.zeros(n, 'i')
        self.__live = False
        self.showDifference = False
        self.update()

    def update(self):
        """update the Qwt data"""
        # y and errbar sync with plot, not changing data.
        self.y[:] = self.camonitor.recent[:]
        self.errbar[:] = self.camonitor.std[:]

        kept = 1-self.mask
        x = np.compress(kept, self.x, axis=0)

        if self.showDifference:
            y = np.compress(kept, self.y, axis=0)
        else:
            y = np.compress(kept, self.y - self.yref, axis = 0)
        
        Qwt.QwtPlotCurve.setData(self, x, y)

    def boundingRect(self):
        """
        Return the bounding rectangle of the data, error bars included.
        """
        kept = 1 - self.mask
        x  = np.compress(kept, self.x, axis=0)
        if self.showDifference:
            y = np.compress(kept, self.y, axis=0)
        else:
            y = np.compress(kept, self.y - self.yref, axis = 0)

        y2 = np.compress(kept, self.errbar, axis=0)
        xmin = min(x)
        xmax = max(x)
        ymin = min(y - y2)
        ymax = max(y + y2)
        w = xmax - xmin
        h = ymax - ymin
        return QRectF(xmin, ymin, w, h)
        

    def drawFromTo(self, painter, xMap, yMap, first, last = -1):
        """
        Draw an interval of the curve, including the error bars.

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
        if self.errorOnTop:
            # draw the bars
            kept = 1 - self.mask
            x  = np.compress(kept, self.x, axis=0)
            if self.showDifference:
                y = np.compress(kept, self.y, axis=0)
            else:
                y = np.compress(kept, self.y - self.yref, axis = 0)
            y2 = np.compress(kept, self.errbar, axis=0)
        
            if len(self.errbar.shape) in [0, 1]:
                ymin = (y - y2)
                ymax = (y + y2)
            else:
                # both x and y direction
                ymin = (y - y2[0])
                ymax = (y + y2[1])
            n, i = len(x), 0
            lines = []
            while i < n:
                xi = xMap.transform(x[i])
                lines.append(
                    QLine(xi, yMap.transform(ymin[i]),
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
                        QLine(xi - cap, yMap.transform(ymin[i]),
                                     xi + cap, yMap.transform(ymin[i])))
                    lines.append(
                        QLine(xi - cap, yMap.transform(ymax[i]),
                                     xi + cap, yMap.transform(ymax[i])))
                    i += 1
            painter.drawLines(lines)

        painter.restore()

        Qwt.QwtPlotCurve.drawFromTo(self, painter, xMap, yMap, first, last)


    def average(self):
        """average of the whole curve"""
        return np.average(self.y)

    def std(self):
        """std of the curve"""
        return np.std(self.y)

    def resetPvData(self):
        """
        clear the history data, start with clean observation
        """
        self.camonitor.resetData()

    def saveAsReference(self):
        """
        save the current orbit as reference
        """
        self.yref = self.y[:]

    def getReference(self):
        return self.yref[:]
    

class OrbitPlot(Qwt.QwtPlot):
    def __init__(self, parent = None, x = None, pvs = None, plane = 'H',
                 live=True, errorbar=True):
        super(OrbitPlot, self).__init__(parent)
        
        self.setCanvasBackground(Qt.white)
        #self.alignScales()

        # Initialize data
        # uncomment to draw the curve on top of the error bars
        #errorOnTop = False 
        self.errorOnTop = errorbar
        self.__live = live
        
        #self.setTitle("An Orbit Plot")
        #self.insertLegend(Qwt.QwtLegend(), Qwt.QwtPlot.BottomLegend);

        self.setAxisAutoScale(Qwt.QwtPlot.xBottom)
        self.setAxisAutoScale(Qwt.QwtPlot.yLeft)

        self.plotLayout().setAlignCanvasToScales(True)

        self.curve1 = OrbitPlotCurve(
            x,
            pvs,
            curvePen = QPen(Qt.black, 2),
            curveSymbol = Qwt.QwtSymbol(
                Qwt.QwtSymbol.Ellipse,
                QBrush(Qt.red),
                QPen(Qt.black, 2),
                QSize(9, 9)),
            errorPen = QPen(Qt.blue, 1),
            errorCap = 10,
            errorOnTop = self.errorOnTop,
            )

        self.curve1.attach(self)
        self.bound = self.curve1.boundingRect()

        self.curvemag = Qwt.QwtPlotCurve("Magnet Profile")
        # get x, y, color
        magx, magy, magc = self.getMagnetProfile()
        self.curvemag.setData(magx, magy)
        self.curvemag.setYAxis(Qwt.QwtPlot.yRight)
        self.setAxisScale(Qwt.QwtPlot.yRight, -2, 20)
        self.enableAxis(Qwt.QwtPlot.yRight, False)

        self.curvemag.attach(self)
        
        #print "BD",self.bound
        #.resize(400, 300)
        grid1 = Qwt.QwtPlotGrid()
        grid1.attach(self)
        grid1.setPen(QPen(Qt.black, 0, Qt.DotLine))

        #picker1 = Qwt.QwtPlotPicker(Qwt.QwtPlot.xBottom,
        #                           Qwt.QwtPlot.yLeft,
        #                           Qwt.QwtPicker.NoSelection,
        #                           Qwt.QwtPlotPicker.CrossRubberBand,
        #                           Qwt.QwtPicker.AlwaysOn,
        #                           self.canvas())
        self.picker1 = MagnetPicker(self.canvas())
        self.picker1.setTrackerPen(QPen(Qt.red, 4))
        

        self.zoomer1 = Qwt.QwtPlotZoomer(Qwt.QwtPlot.xBottom,
                                        Qwt.QwtPlot.yLeft,
                                        Qwt.QwtPicker.DragSelection,
                                        Qwt.QwtPicker.AlwaysOff,
                                        self.canvas())
        self.zoomer1.setRubberBandPen(QPen(Qt.black))

        self.connect(self.zoomer1, SIGNAL("zoomed(QRectF)"),
                     self.zoomed1)
        self.timerId = self.startTimer(500)


    def zoomed1(self, rect):
        print "Zoomed"
        
    def setPlot(self, mode):
        if mode == self.PLOT_SINGLESHOT:
            self.update()
        elif mode == self.PLOT_LIVE:
            pass
        else:
            pass

    def alignScales(self):
        self.canvas().setFrameStyle(QFrame.Box | QFrame.Plain)
        self.canvas().setLineWidth(1)
        for i in range(Qwt.QwtPlot.axisCnt):
            scaleWidget = self.axisWidget(i)
            if scaleWidget:
                scaleWidget.setMargin(0)
            scaleDraw = self.axisScaleDraw(i)
            if scaleDraw:
                scaleDraw.enableComponent(
                    Qwt.QwtAbstractScaleDraw.Backbone, False)

    def addMagnetProfile(self, sb, se, name, minlen = 0.2):
        self.picker1.addMagnetProfile(sb, se, name, minlen)

    def getMagnetProfile(self):
        prof = hla.getBeamlineProfile()
        x, y, c = [], [], []
        for box in prof:
            for i in range(len(box[0])):
                x.append(box[0][i])
                y.append(box[1][i])
                c.append(box[2])
        return x, y, c
        
    def timerEvent(self, e):
        if not self.__live: return
        self.curve1.update()
        self.replot()

    def singleShot(self):
        #print "Plot :: singleShot"
        self.zoomer1.setZoomBase(self.curve1.boundingRect())
        self.curve1.update()
        self.replot()

    def liveData(self, on):
        self.__live = on
        self.zoomer1.setZoomBase(self.curve1.boundingRect())
        return None

    def setErrorBar(self, on):
        self.curve1.setErrorBar(on)
        self.replot()

    def scaleVertical(self, factor):
        scalediv = self.axisScaleDiv(Qwt.QwtPlot.yLeft)
        sr, sl = scalediv.upperBound(), scalediv.lowerBound()
        dy = (sr - sl)*(factor - 1)/2.0
        
        #print "bound:",scalediv.lowerBound(), scalediv.upperBound()
        self.setAxisScale(Qwt.QwtPlot.yLeft, sl - dy, sr + dy)
        self.replot()

    def zoomAuto(self):
        bound = self.curve1.boundingRect()
        w = bound.width()
        h = bound.height()
        #xmin = bound.left() - w*.03
        #xmax = bound.right() + w*.03
        ymin = bound.top() - h*.05
        ymax = bound.bottom() + h*.03
        xmin = bound.left()
        xmax = bound.right()
        #ymin = bound.top()
        #ymax = bound.bottom()
        if w > 0.0: self.setAxisScale(Qwt.QwtPlot.xBottom, xmin, xmax)
        else: self.setAxisAutoScale(Qwt.Qwt.Plot.xBottom)

        if h > 0.0: self.setAxisScale(Qwt.QwtPlot.yLeft, ymin, ymax)
        else: self.setAxisAutoScale(Qwt.QwtPlot.yLeft)


    def setMask(self, i, v):
        self.curve1.setMask(i, v)

    def getMask(self):
        return self.curve1.getMask()

    def datainfo(self):
        return "avg: %.4e std: %.4e" % \
            (self.curve1.average(), self.curve1.std())
    
    def resetPvData(self):
        self.curve1.resetPvData()

class OrbitPlotMainWindow(QMainWindow):
    """
    the main window
    """
    def __init__(self, parent = None):
        QMainWindow.__init__(self, parent)

        self.setIconSize(QSize(48, 48))
        # initialize a QwtPlot central widget
        bpm = hla.getElements('BPM')
        pvx = [e.pv(tags=[hla.machines.HLA_TAG_EGET, hla.machines.HLA_TAG_X])[0]
               for e in bpm]
        #print pvx
        pvy = [e.pv(tags=[hla.machines.HLA_TAG_EGET, hla.machines.HLA_TAG_Y])[0]
               for e in bpm]
        pvsx = [e.sb for e in bpm]
        pvsy = [e.sb for e in bpm]
        self.bpm = [e.name for e in bpm]
        
        self.plot1 = OrbitPlot(self, pvsx, [p.encode('ascii') for p in pvx])
        self.plot2 = OrbitPlot(self, pvsy, [p.encode('ascii') for p in pvy])

        for e in hla.getGroupMembers(['QUAD', 'BPM', 'HCOR', 'VCOR', 'SEXT'],
                                     op='union'):
            self.plot1.addMagnetProfile(e.sb, e.sb+e.length, e.name)
            
        #for i in range(10):
        #    self.plot1.maskIndex(i)
        
        self.plot1.plotLayout().setCanvasMargin(4)
        self.plot1.plotLayout().setAlignCanvasToScales(True)
        self.plot1.setTitle("Horizontal Orbit")
        self.plot1.singleShot()
        #print self.plot1.curve1.y

        self.plot2.plotLayout().setCanvasMargin(4)
        self.plot2.plotLayout().setAlignCanvasToScales(True)
        self.plot2.setTitle("Vertical Orbit")

        wid1 = QWidget()
        vbox = QVBoxLayout()
        vbox.addWidget(self.plot1)
        vbox.addWidget(self.plot2)
        wid1.setLayout(vbox)
        wid = QTabWidget()
        wid.addTab(wid1, "Orbit Plot")

        wid2 = QTableWidget()
        
        wid.addTab(wid2, "test2")
        wid.addTab(QLabel("H3"), "test3")
        self.setCentralWidget(wid)

        #self.setCentralWidget(OrbitPlot())

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

        self.timerId = self.startTimer(500)

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

    def chooseBpm(self):
        #print self.bpm
        bpm = []
        bpmmask = self.plot1.mask[:]
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
        
    def timerEvent(self, e):
        #self.statusBar().showMessage("%s; %s"  % (
        #        self.plot1.datainfo(), self.plot2.datainfo()))
        self.updateStatus()

    def updateStatus(self):
        self.statusBar().showMessage("%s; %s"  % (
                self.plot1.datainfo(), self.plot2.datainfo()))        

    def singleShot(self):
        #print "Main: Singleshot"
        self.plot1.singleShot()
        self.plot2.singleShot()
        self.updateStatus()

    def resetPvData(self):
        self.plot1.resetPvData()
        self.plot2.resetPvData()
        #hla.hlalib._reset_trims()


def main(args):
    #app = QApplication(args)
    demo = OrbitPlotMainWindow()
    demo.resize(1000,600)
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
