import cothread
from cothread.catools import caget, caput
#from aphlas.epicsdatamonitor import CaDataMonitor

from PyQt4.QtCore import (PYQT_VERSION_STR, QFile, QFileInfo, QSettings,
        QObject, QString, QT_VERSION_STR, QTimer, QVariant, Qt, SIGNAL,
        QSize, QRectF, QLine)
from PyQt4.QtGui import (QApplication, QWidget,
        QDockWidget, QFileDialog, QFrame, QImage, QImageReader,
        QImageWriter, QInputDialog, QKeySequence, QListWidget,
        QMessageBox, QPainter, QPixmap, QPrintDialog,
        QPrinter, QSpinBox, QPen, QBrush,
        QTableWidget)

import PyQt4.Qwt5 as Qwt
from PyQt4.Qwt5.anynumpy import *

import numpy as np

class MagnetPicker(Qwt.QwtPlotPicker):
    """
    show the magnet name when moving cursor in the plot.
    """
    def __init__(self, canvas, profile = None, minlen = 0.2):
        """
        initialize with cavas and magnet profile::

        - profile = [(s_begin, s_end, name), ...]
        - minlen the minimum length of "active magnet region"
        """
        Qwt.QwtPlotPicker.__init__(self, Qwt.QwtPlot.xBottom,
                          Qwt.QwtPlot.yLeft,
                          Qwt.QwtPicker.NoSelection,
                          Qwt.QwtPlotPicker.CrossRubberBand,
                          Qwt.QwtPicker.AlwaysOn,
                          canvas)
        if profile is None:
            self.profile = []
        else:
            self.profile = profile

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
        return Qwt.QwtText("%.3f, %.3f\n%s" % (pos.x(), pos.y()*1e6, '\n'.join(s)))


class OrbitPlotCurve(Qwt.QwtPlotCurve):
    """Orbit curve
    """
    def __init__(self, x, pvs, **kw):
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


        self.setPen(kw.get('curvePen', QPen(Qt.NoPen)))
        self.setStyle(kw.get('curveStyle', Qwt.QwtPlotCurve.Lines))
        self.setSymbol(kw.get('curveSymbol', Qwt.QwtSymbol())
        self.errorPen = kw.get('errorPen', QPen(Qt.NoPen)
        self.errorCap = kw.get('errorCap', 0)
        self.errorOnTop = kw.get('errorOnTop', False)
        self.samples = kw.get('samples', 10)
        self.yfactor = kw.get('factor', 1e6)
        
        if len(pvs) != len(x):
            raise ValueError("pv and x are not same size")
        self.pvs = pvs
        self.icount = 0
        # how many samples are kept for statistics
        n = len(x)
        self.x      = np.array(x)
        self.y      = np.zeros((samples, n), 'd')
        self.yref   = np.zeros(n, 'd')
        self.errbar = np.zeros(n, 'd')
        #self.camonitor = CaDataMonitor(pvs, samples=self.SAMPLES)
        #self.camonitor = CaDataMonitor(pvs, simulation=True)
        self.mask = np.zeros(n, 'i')
        self.__live = False
        self.showDifference = False
        self.update()

    def update(self):
        """update the Qwt data"""
        # y and errbar sync with plot, not changing data.
        c, i = divmod(self.icount, self.samples)
        self.y[i,:] = caget(self.pvs)
        self.y[i, :] *= self.yfactor
        self.icount += 1
        if self.icount < self.samples:
            self.errbar[:] = np.std(self.y[:self.icount,:])
        else:
            self.errbar[:] = np.std(self.y, axis=0)
            
        kept = 1-self.mask
        x1 = np.compress(kept, self.x, axis=0)
        y1 = np.compress(kept, self.y[i,:] - self.yref, axis = 0)
        
        Qwt.QwtPlotCurve.setData(self, x1, y1)

    def boundingRect(self):
        """
        Return the bounding rectangle of the data, error bars included.
        """
        c, i = divmod(self.icount, self.samples)
        kept = 1 - self.mask
        x  = np.compress(kept, self.x, axis=0)
        y = np.compress(kept, self.y[i,:] - self.yref, axis = 0)

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

        c, i = divmod(self.icount, self.samples)

        if last < 0:
            last = self.dataSize() - 1

        if self.errorOnTop:
            Qwt.QwtPlotCurve.drawFromTo(self, painter, xMap, yMap, first, last)

        # draw the error bars
        painter.save()
        painter.setPen(self.errorPen)

        #painter.drawText(10, 10, 20, 30, Qt.AlignBottom and Qt.AlignRight, "HHH")

        # draw the error bars with caps in the y direction
        if self.errorOnTop and self.icount > self.samples:
            # draw the bars
            kept = 1 - self.mask
            x1  = np.compress(kept, self.x, axis=0)
            y1 = np.compress(kept, self.y[i,:] - self.yref, axis = 0)
            yer1 = np.compress(kept, self.errbar, axis=0)
        
            if len(self.errbar.shape) in [0, 1]:
                ymin = (y1 - yer1)
                ymax = (y1 + yer1)
            else:
                # both x and y direction
                ymin = (y1 - yer1[0])
                ymax = (y1 + yer1[1])
            n, i = len(x1), 0
            lines = []
            while i < n:
                xi = xMap.transform(x1[i])
                lines.append(
                    QLine(xi, yMap.transform(ymin[i]),
                                 xi, yMap.transform(ymax[i])))
                i += 1
            painter.drawLines(lines)

            # draw the caps
            if self.errorCap > 0:
                cap = self.errorCap/2
                i, j = 0, 0
                lines = []
                while i < n:
                    xi = xMap.transform(x1[i])
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
        self.icount = 0
        self.y.fill(0.0)


class OrbitPlot(Qwt.QwtPlot):
    def __init__(self, parent = None, x = None, pvs = None, 
                 plane = 'H', pvs_golden = None,
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

        if pvs_golden is None: self.golden = None
        else:
            #for pv in pvs_golden: print pv, caget(pv.encode("ascii"))
            self.golden = OrbitPlotCurve(
                x,
                pvs_golden,
                curvePen = QPen(Qt.black, 2),
                errorOnTop = False
            )
            self.golden.attach(self)
            #print "Golden orbit is attached"
        self.bound = self.curve1.boundingRect()
        if not self.golden is None:
            self.bound = self.bound.united(self.golden.boundingRect())
        
        self.curvemag = Qwt.QwtPlotCurve("Magnet Profile")
        # get x, y, color
        magx, magy, magc = self.getMagnetProfile()
        self.curvemag.setData(magx, magy)
        self.curvemag.setYAxis(Qwt.QwtPlot.yRight)
        self.setAxisScale(Qwt.QwtPlot.yRight, -2, 20)
        self.enableAxis(Qwt.QwtPlot.yRight, False)

        self.curvemag.attach(self)
        
        #print "size hint:", self.sizeHint()
        #print "min sizehint:", self.minimumSizeHint(), self.minimumWidth()
        self.setMinimumSize(400, 200)
        #self.resize(300, 200)
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

        self.marker = Qwt.QwtPlotMarker()
        self.marker.attach(self)
        #self.marker.setLabelAlignment(Qt.AlignLeft)
        self.marker.setLabelAlignment(Qt.AlignBottom)
        #self.marker.setValue(100, 0)
        self.marker.setLabel(Qwt.QwtText("Hello"))

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
        #prof = hla.getBeamlineProfile()
        prof = []
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
        x = self.invTransform(Qwt.QwtPlot.xBottom, 20)
        y = self.invTransform(Qwt.QwtPlot.yLeft, 10)
        #print "(20,10)", x, y
        #print "x=0 is", self.transform(Qwt.QwtPlot.xBottom, 27.0)
        self.marker.setValue(x, y)

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
        self.curve1.errorOnTop = on
        self.replot()

    def _scaleVertical(self, factor = 1.0/1.5):
        scalediv = self.axisScaleDiv(Qwt.QwtPlot.yLeft)
        sr, sl = scalediv.upperBound(), scalediv.lowerBound()
        dy = (sr - sl)*(factor - 1)/2.0
        
        #print "bound:",scalediv.lowerBound(), scalediv.upperBound()
        self.setAxisScale(Qwt.QwtPlot.yLeft, sl - dy, sr + dy)
        self.replot()

    def zoomIn(self):
        self._scaleVertical(1.0/1.5)

    def zoomOut(self):
        self._scaleVertical(1.5/1.0)

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
        self.curve1.mask[i] = v

    def getMask(self):
        return self.curve1.getMask()

    def datainfo(self):
        return "avg: %.4e std: %.4e" % \
            (self.curve1.average(), self.curve1.std())
    
    def resetPvData(self):
        self.curve1.resetPvData()
