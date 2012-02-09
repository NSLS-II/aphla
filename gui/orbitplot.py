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
        return Qwt.QwtText("%.3f, %.3f\n%s" % (pos.x(), pos.y(), '\n'.join(s)))


class OrbitPlotCurve(Qwt.QwtPlotCurve):
    """Orbit curve
    """
    def __init__(self, data, **kw):
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

        self.data = data
        self.x1, self.y1, self.e1 = None, None, None
        self.yref = None # no mask applied
        self.data_field = kw.get('data_field', 'orbit')
        self.setPen(kw.get('curvePen', QPen(Qt.NoPen)))
        self.setStyle(kw.get('curveStyle', Qwt.QwtPlotCurve.Lines))
        self.setSymbol(kw.get('curveSymbol', Qwt.QwtSymbol()))
        self.errorPen = kw.get('errorPen', QPen(Qt.NoPen))
        self.errorCap = kw.get('errorCap', 0)
        self.errorOnTop = kw.get('errorOnTop', True)
        self.__live = False
        self.showDifference = False
        self.update()

    def setDrift(self, mode):
        if mode == 'no':
            self.yref = None
        elif mode == 'now':
            x1, y1, e1 = self.data.data(field=self.data_field, nomask=True)
            self.yref = y1
        elif mode == 'golden':
            self.yref = self.data.golden(nomask = True)

    def update(self):
        self.x1, self.y1, self.e1 = self.data.data(field=self.data_field)
        if self.yref is not None:
            self.y1 = self.y1 - np.compress(self.data.keep, self.yref)
        Qwt.QwtPlotCurve.setData(self, self.x1, self.y1)

    def boundingRect(self):
        """
        Return the bounding rectangle of the data, error bars included.
        """
        #x, y, y2 = self.data.data(field=self.data_field)
        x, y, y2 = self.x1, self.y1, self.e1
        xmin, xmax = min(x), max(x)
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

        #painter.drawText(10, 10, 20, 30, Qt.AlignBottom and Qt.AlignRight, "HHH")

        # draw the error bars with caps in the y direction
        if self.errorOnTop:
            # draw the bars
            #x1, y1, yer1 = self.data.data(field=self.data_field)
            x1, y1, yer1 = self.x1, self.y1, self.e1

            ymin = (y1 - yer1)
            ymax = (y1 + yer1)

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


class OrbitPlot(Qwt.QwtPlot):
    def __init__(self, parent = None, data = None, data_field = 'orbit',
                 pvs_golden = None, live = True, errorbar = True, 
                 picker_profile = None, magnet_profile = None):
        
        #data = kw.get('data', None)
        #data_field = kw.get('data_field', 'orbit')
        #pvs_golden = kw.get('pvs_golden', None)
        #live = kw.get('live', True)
        #errorbar= kw.get('errorbar', True)
        #picker_profile = kw.get('picker_profile', None)

        super(OrbitPlot, self).__init__(parent)
        
        self.setCanvasBackground(Qt.white)
        self.errorOnTop = errorbar
        self.live = live
        
        #self.setTitle("An Orbit Plot")
        #self.insertLegend(Qwt.QwtLegend(), Qwt.QwtPlot.BottomLegend);

        self.setAxisAutoScale(Qwt.QwtPlot.xBottom)
        self.setAxisAutoScale(Qwt.QwtPlot.yLeft)

        self.plotLayout().setAlignCanvasToScales(True)

        self.curve1 = OrbitPlotCurve(
            data = data, data_field = data_field,
            curvePen = QPen(Qt.black, 2),
            curveSymbol = Qwt.QwtSymbol(
                Qwt.QwtSymbol.Ellipse,
                QBrush(Qt.red),
                QPen(Qt.black, 2),
                QSize(8, 8)),
            errorPen = QPen(Qt.blue, 1),
            errorCap = 10,
            errorOnTop = self.errorOnTop,
            )

        self.curve1.attach(self)

        self.curve2 = Qwt.QwtPlotCurve()
        self.curve2.setPen(QPen(Qt.red, 4))
        self.curve2.attach(self)
        #self.curve2.setVisible(False)

        print "PV golden:", pvs_golden
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
        if self.golden is not None:
            self.bound = self.bound.united(self.golden.boundingRect())
        
        if magnet_profile is not None:
            self.curvemag = Qwt.QwtPlotCurve("Magnet Profile")
            # get x, y, color(optional)
            magx, magy = [], []
            if len(magnet_profile) == 2:
                magx, magy = magnet_profile
                magc = ['k'] * len(magx)
            elif len(magnet_profile) == 3:
                magx, magy, magc = magnet_profile
            self.curvemag.setData(magx, magy)
            self.curvemag.setYAxis(Qwt.QwtPlot.yRight)
            self.setAxisScale(Qwt.QwtPlot.yRight, -2, 20)
            self.enableAxis(Qwt.QwtPlot.yRight, False)

            self.curvemag.attach(self)
        
        self.setMinimumSize(400, 200)
        grid1 = Qwt.QwtPlotGrid()
        grid1.attach(self)
        grid1.setPen(QPen(Qt.black, 0, Qt.DotLine))

        self.picker1 = MagnetPicker(self.canvas(), profile = picker_profile)
        self.picker1.setTrackerPen(QPen(Qt.red, 4))
        
        self.zoomer1 = Qwt.QwtPlotZoomer(Qwt.QwtPlot.xBottom,
                                        Qwt.QwtPlot.yLeft,
                                        Qwt.QwtPicker.DragSelection,
                                        Qwt.QwtPicker.AlwaysOff,
                                        self.canvas())
        self.zoomer1.setRubberBandPen(QPen(Qt.black))

        self.connect(self.zoomer1, SIGNAL("zoomed(QRectF)"),
                     self.zoomed1)
        #self.timerId = self.startTimer(1000)

        self.marker = Qwt.QwtPlotMarker()
        self.marker.attach(self)
        #self.marker.setLabelAlignment(Qt.AlignLeft)
        self.marker.setLabelAlignment(Qt.AlignBottom)
        #self.marker.setValue(100, 0)
        #self.marker.setLabel(Qwt.QwtText("Hello"))

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

    def updatePlot(self):
        self.curve1.update()
        if self.golden is not None: self.golden.update()
        self.replot()
        if self.live:
            self.zoomer1.setZoomBase(self.curve1.boundingRect())
            
        #x = self.invTransform(Qwt.QwtPlot.xBottom, 20)
        #y = self.invTransform(Qwt.QwtPlot.yLeft, 10)
        #self.marker.setValue(x, y)

    def setDrift(self, mode = 'no'):
        self.curve1.setDrift(mode)

    def singleShot(self):
        #print "Plot :: singleShot"
        self.zoomer1.setZoomBase(self.curve1.boundingRect())
        self.curve1.update()
        if self.golden is not None: self.golden.update()
        self.replot()

    def liveData(self, on):
        self.live = on
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


