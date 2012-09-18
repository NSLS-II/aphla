import cothread
from cothread.catools import caget, caput

from PyQt4.QtCore import (PYQT_VERSION_STR, QFile, QFileInfo, QSettings,
        QObject, QString, QT_VERSION_STR, QTimer, QVariant, Qt, SIGNAL,
        QSize, QRectF, QLine, pyqtSignal)
#from PyQt4 import (PyQt_PyObject,)
from PyQt4.QtGui import (QApplication, QWidget, QColor,
        QDockWidget, QFileDialog, QFrame, QImage, QImageReader,
        QImageWriter, QInputDialog, QKeySequence, QListWidget,
        QMessageBox, QPainter, QPixmap, QPrintDialog,
        QPrinter, QSpinBox, QPen, QBrush, QFontMetrics,
        QTableWidget)

import PyQt4.Qwt5 as Qwt
from PyQt4.Qwt5.anynumpy import *

import time
import numpy as np
import sip

# sip has a bug affecting PyQwt
# http://blog.gmane.org/gmane.comp.graphics.qwt.python/month=20101001
if sip.SIP_VERSION_STR > '4.10.2':
    from scales import DateTimeScaleEngine


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

        self.connect(self, SIGNAL("selected(QPointF&)"),
                     self.activate_element)
        # instead of list, use PyQt_PyObject
        #self.elementSelected = pyqtSignal(PyQt_PyObject)
        self.elementSelected = pyqtSignal(list)

    def activate_element(self, p):
        print p

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

    def element_names(self, x, y):
        s = []
        for m in self.profile:
            if x > m[0] and x < m[1]:
                s.append(m[2])
        return s

    def trackerTextF(self, pos):
        s = self.element_names(pos.x(), pos.y())
        return Qwt.QwtText("%.3f, %.3f\n%s" % (pos.x(), pos.y(), '\n'.join(s)))

    def widgetMouseDoubleClickEvent(self, evt):
        #print "Double Clicked", evt.x(), evt.y(), evt.pos(), evt.posF()
        pos = self.invTransform(evt.pos())
        elements = self.element_names(pos.x(), pos.y())
        
        #self.emit(SIGNAL("elementSelected(list)"), elements)
        self.emit(SIGNAL("elementDoubleClicked(PyQt_PyObject)"), elements)


class DcctCurrentCurve(Qwt.QwtPlotCurve):
    def __init__(self, **kw):
        super(DcctCurrentCurve, self).__init__()
        self.t = []
        self.v = []

    def setColor(self, color):
        c = QColor(color)
        c.setAlpha(150)
        self.setPen(c)
        self.setBrush(c)

    def updateCurve(self):
        self.setData(self.t, self.v)


class DcctCurrentPlot(Qwt.QwtPlot):
    def __init__(self, parent = None, **kw):
        super(DcctCurrentPlot, self).__init__(parent)

        #self.setAutoReplot(False)
        self.plotLayout().setAlignCanvasToScales(True)
        #self.setAxisTitle(Qwt.QwtPlot.xBottom, "Time")
        #self.setAxisScaleDraw(Qwt.QwtPlot.xBottom, TimeScaleDraw())
        self.setAxisScale(Qwt.QwtPlot.xBottom, 0, 240)
        #self.setAxisLabelRotation(Qwt.QwtPlot.xBottom, -10.0)
        self.setAxisLabelAlignment(Qwt.QwtPlot.xBottom, Qt.AlignLeft)
        scaleWidget = self.axisWidget(Qwt.QwtPlot.xBottom)
        fmh = QFontMetrics(scaleWidget.font()).height()
        #scaleWidget.setMinBorderDist(0, fmh/2)
        
        #self.setAxisTitle(Qwt.QwtPlot.yLeft, "I")
        #self.setAxisScale(Qwt.QwtPlot.yLeft, 0, 550)
        import sip
        if sip.SIP_VERSION_STR > '4.10.2':
            DateTimeScaleEngine.enableInAxis(self, Qwt.QwtPlot.xBottom)
        sd = self.axisScaleDraw(Qwt.QwtPlot.xBottom)
        #fmh = QFontMetrics(scaleWidget.font()).height()
        #scaleWidget.setMinBorderDist(0, fmh/2)
        #print "Scale Draw Extent:", sd.minimumExtent()
        sd.setMinimumExtent(fmh*2)
        #print "Scale Draw Extent:", sd.minimumExtent()

        self.curve = DcctCurrentCurve()
        self.curve.setColor(Qt.green)

        grid1 = Qwt.QwtPlotGrid()
        grid1.attach(self)
        grid1.setPen(QPen(Qt.black, 0, Qt.DotLine))

        self.curve.attach(self)

        self.mark1 = Qwt.QwtPlotMarker()
        self.mark1.setLabelAlignment(Qt.AlignLeft | Qt.AlignTop)
        #self.mark1.setPen(QPen(QColor(0, 255, 0)))
        self.mark1.attach(self)

    def updateDcct(self, curr):
        self.curve.v.append(curr)
        self.curve.t.append(curr.timestamp)
        #print self.curve.t, self.curve.v
        lb = Qwt.QwtText("%.2f mA" % curr.real)
        lb.setColor(Qt.blue)
        self.mark1.setValue(curr.timestamp, 0)
        self.mark1.setLabel(lb)

    def updatePlot(self):
        self.curve.updateCurve()
        self.setAxisScale(Qwt.QwtPlot.xBottom, self.curve.t[0], self.curve.t[-1])
        self.replot()

    def _loadFakeData(self, t0, v, lt, maxv, span, minv = 300.0):
        self.curve.t = np.linspace(t0 - span*3600.0, t0, 200).tolist()
        self.curve.v = [500.0] * 200
        return

        # dt from max current(last injection)
        dts0 = np.log(v/maxv)*lt
        tlst = np.linspace(0, span*3600.0, 1000)
        vlst = [0] * 1000
        ts0 = 0.0
        for i,t in enumerate(tlst):
            self.curve.t.append(t - span*3600.0 + t0)
            val = maxv*exp((ts0-t)/lt/3600.0)
            if val < 300.0:
                ts0 = t
                val = maxv
            vlst[i] = val
            
            self.curve.v.append(val)
        print self.curve.t[-1], t0, self.curve.v[-1]

    def _loadFakeDataFile(self, fname, shift = None):
        if shift is None: t0 = time.time()
        else: t0 = shift
        t, v = [], []
        for s in open(fname, 'r').readlines():
            rec = s.strip().split()
            stmp = ' '.join([rec[1], rec[2][:-7]])
            tstruct = time.strptime(stmp, "%Y-%m-%d %H:%M:%S")
            t.append(time.mktime(tstruct))
            v.append(float(rec[3]))
            #print time.mktime(t[-1]), rec[3]
        dt = t[-1] - t0
        self.curve.t = [ti - dt for ti in t]
        self.curve.v = v


class OrbitData(object):
    """
    the orbit related data. Raw orbit reading and statistics.

    - *samples* data points kept to calculate the statistics.
    - *scale* factor for *y*
    - *x* list of s-coordinate, never updated.
    - *pvs* list of channel names
    - *mode* 'EPICS' | 'sim', default is 'EPICS'
    - *keep* mask for ignore(0) or keep(1) that data point.
    """
    def __init__(self, **kw):
        self.samples = kw.get('samples', 10)
        self.scale = kw.get('scale', 1e6)
        self.pvs = kw.get('pvs', None)
        self.elems = kw.get('elements', None)
        self.field = kw.get('field', None)
        self.picker_profile = kw.get('picker_profile', None)
        self.magnet_profile = kw.get('magnet_profile', None)

        if self.pvs is not None:
            n = len(pvs)
            self.x = kw.get('x', np.arange(n))
            self.y = np.zeros((self.samples, n), 'd')
            self.y[0,:] = caget(self.pvs)
        elif self.elems is not None:
            n = len(self.elems)
            self.x = kw.get('x', np.arange(n))
            self.y = np.zeros((self.samples, n), 'd')
            # only take the first sample
            for j in range(n):
                self.y[0,j] = self.elems[j].get(self.field)
        else:
            n = 0
            self.x = None

        #if self.x is not None and len(self.x) != n:
        #    raise ValueError("pv and x are not same size %d != %d" % (n, len(self.x)))

        self.icur, self.icount = 0, 1
        # how many samples are kept for statistics
        self.errbar = np.ones(n, 'd') * 1e-15
        self.keep   = np.ones(n, 'i')
        #print self.x, self.y

    def _update_pvs_data(self):
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
        
    def _update_elems_data(self):
        """
        update the orbit data. It retrieve the data with channel access and
        calculate the updated standard deviation. If the current mode is
        'sim', instead of channel access it uses random data.
        """
        # y and errbar sync with plot, not changing data.
        i = self.icur + 1
        if i >= self.samples: i = 0
        self.y[i,:] = [e.get(self.field) for j,e in enumerate(self.elems)]
        self.y[i,:] *= self.scale
        self.errbar[:] = np.std(self.y, axis=0)
        self.icount += 1
        self.icur = i
        
    def update(self):
        if self.pvs is not None:
            self._update_pvs_data()
        elif self.elems is not None:
            self._update_elems_data()

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



class OrbitPlotCurve(Qwt.QwtPlotCurve):
    """
    Orbit curve
    """
    def __init__(self, **kw):
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

        self.x1, self.y1, self.e1 = None, None, None
        self.yref = None # no mask applied
        self.setPen(kw.get('curvePen', QPen(Qt.NoPen)))
        self.setStyle(kw.get('curveStyle', Qwt.QwtPlotCurve.Lines))
        self.setSymbol(kw.get('curveSymbol', Qwt.QwtSymbol()))
        self.errorPen = kw.get('errorPen', QPen(Qt.NoPen))
        self.errorCap = kw.get('errorCap', 0)
        self.errorOnTop = kw.get('errorOnTop', True)
        self.__live = False
        self.showDifference = False

    def update(self, x, y, e):
        self.x1, self.y1, self.e1 = x, y, e
        Qwt.QwtPlotCurve.setData(self, self.x1, self.y1)

    def boundingRect(self):
        """
        Return the bounding rectangle of the data, error bars included.
        """
        if not all([self.x1, self.y1, self.e1]):
            return Qwt.QwtPlotCurve.boundingRect(self)

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
        if not all([self.x1, self.y1, self.e1]): return

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
            x1, y1, yer1 = self.x1, self.y1, self.e1
            #print x1, y1, yer1 

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
    def __init__(self, parent = None, lat = None,
                 live = True, errorbar = True, title=None): 
        
        super(OrbitPlot, self).__init__(parent)
        
        self.setCanvasBackground(Qt.white)
        self.errorOnTop = errorbar
        self.live = live
        
        self.setAxisAutoScale(Qwt.QwtPlot.xBottom)
        self.setAxisAutoScale(Qwt.QwtPlot.yLeft)

        self.plotLayout().setAlignCanvasToScales(True)
        if title is not None: self.setTitle(title)

        self.curve1 = OrbitPlotCurve(
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

        #print "PV golden:", pvs_golden
        pvs_golden = None
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
        #self.bound = self.curve1.boundingRect()
        if self.golden is not None:
            self.bound = self.bound.united(self.golden.boundingRect())

        self.curvemag = None

        self.setMinimumSize(400, 200)
        grid1 = Qwt.QwtPlotGrid()
        grid1.attach(self)
        grid1.setPen(QPen(Qt.black, 0, Qt.DotLine))

        self.picker1 = None
        self.zoomer1 = None

        self.marker = Qwt.QwtPlotMarker()
        self.marker.attach(self)
        #self.marker.setLabelAlignment(Qt.AlignLeft)
        self.marker.setLabelAlignment(Qt.AlignBottom)
        #self.marker.setValue(100, 0)
        #self.marker.setLabel(Qwt.QwtText("Hello"))
        #self.connect(self, SIGNAL("doubleClicked

    def elementDoubleClicked(self, elem):
        print "element selected:", elem
        self.emit(SIGNAL("elementSelected(PyQt_PyObject)"), elem)

    def zoomed1(self, rect):
        print "Zoomed"
        
    def setPlot(self, picker_profile = None, magnet_profile = None):
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
        
        self.picker1 = None
        #self.picker1 = MagnetPicker(self.canvas(), profile = picker_profile)
        #self.picker1.setTrackerPen(QPen(Qt.red, 4))
        #self.connect(self.picker1, SIGNAL("elementDoubleClicked(PyQt_PyObject)"),
        #             self.elementDoubleClicked)
        
        self.zoomer1 = Qwt.QwtPlotZoomer(Qwt.QwtPlot.xBottom,
                                        Qwt.QwtPlot.yLeft,
                                        Qwt.QwtPicker.DragSelection,
                                        Qwt.QwtPicker.AlwaysOff,
                                        self.canvas())
        self.zoomer1.setRubberBandPen(QPen(Qt.black))

        self.connect(self.zoomer1, SIGNAL("zoomed(QRectF)"),
                     self.zoomed1)
        #self.timerId = self.startTimer(1000)

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

    def updateOrbit(self, data):
        x, y, e = data.data()
        self.curve1.update(x, y, e)
        print "orbit updated"
        self.replot()
        if self.live and self.zoomer1:
            self.zoomer1.setZoomBase(self.curve1.boundingRect())

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

    def plotDesiredOrbit(self, y, x = None):
        """
        hide curve if x,y are both None
        """
        if y is None and x is None:
            self.curve2.setVisible(False)
            print "disabling desired orbit and quit"
            return

        if x is not None:
            self.curve2.setData(x, y)
            return
        data = self.curve2.data()
        vx = [data.x(i) for i in range(data.size())]
        self.curve2.setData(vx, y)


