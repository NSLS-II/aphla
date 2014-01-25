"""
aporbit Plot
============

:author: Lingyun Yang <lyyang@bnl.gov>

The viewer module for `aporbit` GUI. This defines a plot and container widget.
"""

import cothread

if __name__ == "__main__":
    app = cothread.iqt()
    import aphla

from collections import deque
from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import (
    PYQT_VERSION_STR, QFile, QFileInfo, QSettings,
    QObject, QString, QT_VERSION_STR, QTimer, QVariant, Qt, SIGNAL,
    QSize, QRectF, QLine, pyqtSignal)

from PyQt4.QtGui import (
    QAction, QApplication, QWidget, QColor, QDialog,
    QDockWidget, QFileDialog, QFrame, QGridLayout, QIcon,
    QImage, QImageReader, QMenu, QComboBox,
    QImageWriter, QInputDialog, QKeySequence, QLabel, QListWidget,
    QMessageBox, QPainter, QPixmap, QPrintDialog, QPushButton,
    QPrinter, QSpinBox, QPen, QBrush, QFontMetrics, QSizePolicy,
    QMdiSubWindow, QTableWidget, QHBoxLayout, QVBoxLayout)

import PyQt4.Qwt5 as Qwt
from PyQt4.Qwt5.anynumpy import *
import cothread
from cothread.catools import caget, camonitor, FORMAT_TIME
from pvmanager import CaDataMonitor, CaDataGetter
import aphla as ap

import time
import numpy as np
from collections import deque
from datetime import datetime

import sip

import mleapresources

# sip has a bug affecting PyQwt
# http://blog.gmane.org/gmane.comp.graphics.qwt.python/month=20101001
if sip.SIP_VERSION_STR > '4.10.2':
    from scales import DateTimeScaleEngine


COLORS = [("Blue", Qt.blue),
          ("Green", Qt.green),
          ("Red", Qt.red), 
          ("Cyan", Qt.cyan),
          ("Magenta", Qt.magenta),
          ("Yellow", Qt.yellow),
          ("Black", Qt.black)]
SYMBOLS = [("NoSymbol", Qwt.QwtSymbol.NoSymbol),
           ("Ellipse", Qwt.QwtSymbol.Ellipse),
           ("Rect", Qwt.QwtSymbol.Rect),
           ("Diamond", Qwt.QwtSymbol.Diamond),
           ("Triangle", Qwt.QwtSymbol.Triangle),
           ("Cross", Qwt.QwtSymbol.Cross),
           ("XCross", Qwt.QwtSymbol.XCross),
           ("HLine", Qwt.QwtSymbol.HLine),
           ("VLine", Qwt.QwtSymbol.VLine),
           ("Star1", Qwt.QwtSymbol.Star1),
           ("Star2", Qwt.QwtSymbol.Star2),
           ("Hexagon", Qwt.QwtSymbol.Hexagon)]
CURVE_STYLES = [("No Curve", Qwt.QwtPlotCurve.NoCurve),
          ("Lines", Qwt.QwtPlotCurve.Lines),
          ("Sticks", Qwt.QwtPlotCurve.Sticks)]
# Qt.PenStyle
PEN_STYLES = [("Solid Line", Qt.SolidLine),
              ("Dashed Line", Qt.DashLine),
              ("Dotted Line", Qt.DotLine),
              ("Dash-Dotted Line", Qt.DashDotLine),
              ("Dash-Dot-Dotted Line", Qt.DashDotDotLine)]


class MagnetPicker(Qwt.QwtPlotPicker):
    """
    show the magnet name when moving cursor in the plot.
    """
    def __init__(self, canvas, profile = [], minlen = 0.2):
        """
        initialize with cavas and magnet profile::

        - profile = [(s_begin, s_end, name, color = None), ...]
        - minlen the minimum length of "active magnet region"
        """
        Qwt.QwtPlotPicker.__init__(self, Qwt.QwtPlot.xBottom,
                          Qwt.QwtPlot.yLeft,
                          Qwt.QwtPicker.NoSelection,
                          Qwt.QwtPlotPicker.CrossRubberBand,
                          Qwt.QwtPicker.AlwaysOn,
                          canvas)
        self.profile = []
        self.minlen = minlen
        for rec in profile:
            self.addMagnetProfile(rec[0], rec[1], rec[2], self.minlen)

        self.connect(self, SIGNAL("selected(QPointF&)"),
                     self.activate_element)
        # instead of list, use PyQt_PyObject
        #self.elementSelected = pyqtSignal(PyQt_PyObject)
        #self.elementSelected = pyqtSignal(list)

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
        """
        """
        # There is a bug in sip-4.10.2 and pyqwt5 in Debian-6.0
        s = self.element_names(pos.x(), pos.y())
        lab = Qwt.QwtText("%.3f, %.3f\n%s" % (pos.x(), pos.y(), '\n'.join(s)))
        return lab

    def widgetMouseDoubleClickEvent(self, evt):
        #print "Double Clicked", evt.x(), evt.y(), evt.pos(), evt.posF()
        pos = self.invTransform(evt.pos())
        elements = self.element_names(pos.x(), pos.y())

        #print "emitting:", elements
        elemlst = ap.getElements(elements)
        msgbox, msg = QMessageBox(), ""
        for elem in elemlst:
            msg += "<strong>%s:</strong><br>" % elem.name
            for v in elem.fields():
                msg += "  %s: %s<br>" % (v, str(elem.get(v, unitsys=None)))

        msgbox.setText(msg)
        msgbox.exec_()

        # emit with a list of element names
        self.emit(SIGNAL("elementDoubleClicked(PyQt_PyObject)"), elements)


class ApCaTimeSeriesPlot(Qwt.QwtPlot):
    def __init__(self, pvs, parent = None, **kw):
        super(ApCaTimeSeriesPlot, self).__init__(parent)

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
        if sip.SIP_VERSION_STR > '4.10.2':
            DateTimeScaleEngine.enableInAxis(self, Qwt.QwtPlot.xBottom)
        sd = self.axisScaleDraw(Qwt.QwtPlot.xBottom)
        #fmh = QFontMetrics(scaleWidget.font()).height()
        #scaleWidget.setMinBorderDist(0, fmh/2)
        #print "Scale Draw Extent:", sd.minimumExtent()
        sd.setMinimumExtent(fmh*2)
        #print "Scale Draw Extent:", sd.minimumExtent()

        self.drift = False

        self._t, self._vals, self._refs = [], {}, {}
        self._pvs = pvs
        self.curves = [ Qwt.QwtPlotCurve(pv) for pv in pvs ]
        for i,c in enumerate(self.curves):
            self._vals.setdefault(self._pvs[i], [])
            self._refs[pv] = -1
            name, color = COLORS[i % len(COLORS)]
            c.setPen(QPen(color))
            c.attach(self)

        grid1 = Qwt.QwtPlotGrid()
        grid1.attach(self)
        grid1.setPen(QPen(Qt.black, 0, Qt.DotLine))

        legend = Qwt.QwtLegend()
        legend.setItemMode(Qwt.QwtLegend.CheckableItem)
        self.insertLegend(legend, self.RightLegend)

        self.mark1 = Qwt.QwtPlotMarker()
        self.mark1.setLabelAlignment(Qt.AlignLeft | Qt.AlignTop)
        #self.mark1.setPen(QPen(QColor(0, 255, 0)))
        self.mark1.attach(self)
        self.live = True
        self.__hold = False
        self._timerId = self.startTimer(1500)
        
    def timerEvent(self, e):
        if not self.live: return
        if self.__hold: return

        self.__hold = True
        self.updateData()
        if self.drift:
            for i,pv in enumerate(self._pvs):
                y0 = self._vals[pv][self._refs[pv]]
                self.curves[i].setData(
                    self._t, [d - y0 for d in self._vals[pv]])
                #self.mark1.setValue(self._t[self._refs[pv]], 0.0)
        else:
            for i,pv in enumerate(self._pvs):
                self.curves[i].setData(self._t, self._vals[pv])
            
        self.setAxisScale(Qwt.QwtPlot.xBottom, self._t[0], self._t[-1])
        #self.zoomer.setZoomBase(False)
        self.replot()
        self.__hold = False

    def saveAsReference(self, pv = None):
        for i,pv in enumerate(self._pvs):
            self._refs[pv] = len(self._vals[pv]) - 1

    def updateData(self):
        self._t.append(float(datetime.now().strftime("%s")))
        for i,v in enumerate(caget(self._pvs, timeout=0.8)):
            self._vals[v.name].append(v if v.ok else np.nan)
        
    def closeEvent(self, e):
        print "Close"
        e.accept()

class ApErrBarCurve(Qwt.QwtPlotCurve):
    """
    Orbit curve
    """
    __REF_NONE   = 0
    __REF_GOLDEN = 1
    __REF_SAVED  = 2

    def __init__(self, color, **kw):
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
        self.e1 = None

        self.setPen(kw.get('curvePen', QPen(color)))
        self.setStyle(kw.get('curveStyle', Qwt.QwtPlotCurve.Lines))
        #self.setStyle(kw.get('curveStyle', Qwt.QwtPlotCurve.Sticks))
        #self.setStyle(kw.get('curveStyle', Qwt.QwtPlotCurve.Steps))
        self.setSymbol(kw.get('curveSymbol', Qwt.QwtSymbol()))
        self.errorPen = kw.get('errorPen', QPen(color))
        self.errorCap = kw.get('errorCap', 0)
        self.errorOnTop = kw.get('errorOnTop', False)
        self.setTitle(kw.get("title", ""))
        
    def data(self):
        d = Qwt.QwtPlotCurve.data(self)
        x = [d.x(i) for i in range(d.size())]
        y = [d.y(i) for i in range(d.size())]
        return x, y, self.e1

    def setData(self, y, x = None, e = None):
        if e is not None: self.e1 = e
        if x is None:
            Qwt.QwtPlotCurve.setData(self, y, range(len(y)))
        else:
            Qwt.QwtPlotCurve.setData(self, x, y)

    def boundingRect(self):
        """
        Return the bounding rectangle of the data, error bars included.
        """
        data = Qwt.QwtPlotCurve.data(self)
        if data.size() == 0:
            return Qwt.QwtPlotCurve.boundingRect(self)
        
        if self.e1 is None:
            return data.boundingRect()

        x = [data.x(i) for i in range(data.size())]
        y1 = [data.y(i) - 0.5*self.e1[i] for i in range(data.size())]
        y2 = [data.y(i) + 0.5*self.e1[i] for i in range(data.size())]
        xmin, xmax = min(x), max(x)
        ymin, ymax = min(y1), max(y2)
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
        #if not all([self.x1, self.y1, self.e1]): return

        if last < 0:
            last = self.dataSize() - 1

        if self.errorOnTop:
            Qwt.QwtPlotCurve.drawFromTo(self, painter, xMap, yMap, first, last)

        # draw the error bars
        painter.save()
        painter.setPen(self.errorPen)

        #painter.drawText(10, 10, 20, 30, Qt.AlignBottom and Qt.AlignRight, "HHH")

        # draw the error bars with caps in the y direction
        if self.e1 is not None and self.errorOnTop:
            # draw the bars
            data = Qwt.QwtPlotCurve.data(self)
            lines = []
            for i in range(data.size()):
                xi = xMap.transform(data.x(i))
                y1 = data.y(i) - self.e1[i]/2.0
                y2 = data.y(i) + self.e1[i]/2.0
                lines.append(
                    QLine(xi, yMap.transform(y1),
                          xi, yMap.transform(y2)))
            painter.drawLines(lines)

            # draw the caps
            if self.errorCap > 0:
                cap = self.errorCap/2
                lines = []
                for i in range(data.size()):
                    xi = xMap.transform(x1[i])
                    y1 = data.y(i) - self.e1[i]/2.0
                    y2 = data.y(i) + self.e1[i]/2.0
                    lines.append(
                        QLine(xi - cap, yMap.transform(y1),
                              xi + cap, yMap.transform(y1)))
                    lines.append(
                        QLine(xi - cap, yMap.transform(y2),
                              xi + cap, yMap.transform(y2)))
                painter.drawLines(lines)

        painter.restore()

        Qwt.QwtPlotCurve.drawFromTo(self, painter, xMap, yMap, first, last)


class ApCaWaveformPlot(Qwt.QwtPlot):
    def __init__(self, pvs, **kwargs):
        """initialization
        
        Parameters
        -----------
        pvs: waveform PV list
        parent : None
        title : 
        """
        parent = kwargs.pop("parent", None)
        super(ApCaWaveformPlot, self).__init__(parent)
        self.live = kwargs.get("live", True)
        self.__hold = False

        self.setCanvasBackground(Qt.white)
        self.setAutoReplot(False)

        self.plotLayout().setAlignCanvasToScales(True)

        self.drift = False
        self._pvs, self.curves, self._ref = pvs, [], []
        for i,pv in enumerate(pvs):
            name, color = COLORS[i % len(COLORS)]
            c = Qwt.QwtPlotCurve()
            c.setPen(QPen(color, 1.5))
            c.attach(self)
            self.curves.append(c)
            self._ref.append(None)

        # one more plot with second y axis
        self.curve2 = Qwt.QwtPlotCurve()

        #self.setMinimumSize(300, 100)
        grid1 = Qwt.QwtPlotGrid()
        grid1.attach(self)
        pen = grid1.majPen()
        pen.setStyle(Qt.DotLine)
        pen.setWidthF(1.2)
        grid1.setMajPen(pen)

        self.picker1 = None
        #self.zoomer1 = None
        self.zoomer1 = Qwt.QwtPlotZoomer(Qwt.QwtPlot.xBottom,
                                         Qwt.QwtPlot.yLeft,
                                         Qwt.QwtPicker.DragSelection,
                                         Qwt.QwtPicker.AlwaysOff,
                                         self.canvas())
        self.zoomer1.setRubberBandPen(QPen(Qt.black))
        # zoom in and out and Home
        self.zoomer1.setKeyPattern(Qwt.QwtEventPattern.KeyRedo, Qt.Key_I)
        self.zoomer1.setKeyPattern(Qwt.QwtEventPattern.KeyUndo, Qt.Key_O)
        self.zoomer1.setKeyPattern(Qwt.QwtEventPattern.KeyHome, Qt.Key_Home)
        #self.zoomer1.setMousePattern(Qwt.QwtEventPattern.MouseSelect3, Qt.NoButton)
        #self.zoomer1.setMousePattern(Qwt.QwtEventPattern.MouseSelect6, Qt.NoButton)
        # right click will not zoom to home
        self.zoomer1.setMousePattern(Qwt.QwtEventPattern.MouseSelect2, Qt.NoButton)

        self.markers = []
        #self.addMarkers(None)
        #self.marker = Qwt.QwtPlotMarker()
        #self.marker.attach(self)
        #self.marker.setLabelAlignment(Qt.AlignLeft)
        #self.marker.setLabelAlignment(Qt.AlignBottom)
        #self.marker.setValue(100, 0)
        #self.marker.setLabel(Qwt.QwtText("Hello"))
        #self.connect(self, SIGNAL("doubleClicked
        self.count = 0
        self._cadata = CaDataMonitor()
        for pv in pvs:
            self._cadata.addHook(pv, self._ca_update)
        self._cadata.addPv(pvs)

    def _ca_update(self, val, idx = None):
        if self.__hold: return
        if not self.live: return

        self.count += 1
        c = self.curves[idx]

        if self._ref[idx] is not None and self.drift:
            vref = self._ref[idx]
            y = [val[i] - yi for i,yi in enumerate(vref)]
            c.setData(range(len(val)), y)
        else:
            c.setData(range(len(val)), val)
        self.replot()
        if self.count == 1: self.zoomer1.setZoomBase(False)

    def saveAsReference(self):
        self.__hold = True
        for i,c in enumerate(self.curves):
            d = c.data()
            self._ref[i] = [d.y(j) for j in range(d.size())]
            print i, np.average(self._ref[i])
        self.__hold = False

    def setDrift(self, on):
        if on:
            self.saveAsReference()
            self.drift = True
        else:
            self.drift = False

    def setMarkers(self, mks, on = True):
        names, locs = zip(*mks)
        if not on:
            for r in self.markers:
                if r[0] in names: r[1].detach()
        else:
            known_names, mklst = [], []
            if self.markers: known_names, mklst = zip(*self.markers)
            for r in mks:
                if r[0] in known_names:
                    i = known_names.index(r[0])
                    mklst[i].attach(self)
                    continue
                mk1 = Qwt.QwtPlotMarker()
                mk1.setSymbol(Qwt.QwtSymbol(
                        Qwt.QwtSymbol.Diamond,
                        QBrush(Qt.blue),
                        QPen(Qt.red, 1),
                        QSize(12, 12)))
                mk1.setValue(r[1], 0)
                mk1.setAxis(Qwt.QwtPlot.xBottom, Qwt.QwtPlot.yRight)
                mk1.attach(self)
                self.markers.append([r[0], mk1])

    #def elementDoubleClicked(self, elem):
    #    print "element selected:", elem
    #    self.emit(SIGNAL("elementSelected(PyQt_PyObject)"), elem)
    
    def contextMenuEvent(self, e):
        cmenu = QMenu()
        m_drift = QAction("Drift", self)
        m_drift.setCheckable(True)
        #c = QApplication.clipboard()
        m_drift.setChecked(self.drift)
        self.connect(m_drift, SIGNAL("toggled(bool)"), self.setDrift)
        cmenu.addAction(m_drift)
        cmenu.exec_(e.globalPos())

    def setMagnetProfile(self, mprof):
        self.curvemag = Qwt.QwtPlotCurve("Magnet Profile")
        # get x, y, color(optional)
        # x, y and profile(left, right, name)
        mags, magv, magp = [], [], []
        for rec in mprof:
            mags.extend(rec[0])
            magv.extend(rec[1])
            if rec[3]:
                magp.append((min(rec[0]), max(rec[0]), 
                             rec[3].encode('ascii')))
        self.curvemag.setData(mags, magv)
        self.curvemag.setYAxis(Qwt.QwtPlot.yRight)
        # fixed scale
        self.setAxisScale(Qwt.QwtPlot.yRight, -2, 20)
        self.enableAxis(Qwt.QwtPlot.yRight, False)

        self.curvemag.attach(self)

        if magp and sip.SIP_VERSION_STR > '4.10.2':
            self.picker1 = MagnetPicker(self.canvas(), profile=magp)
            #sb = [v[0] for v in magp]
            #se = [v[1] for v in magp]
            #names = [v[2] for v in magp]
            #self.picker1.addMagnetProfile(sb, se, names)
            self.picker1.setTrackerPen(QPen(Qt.red, 4))
            self.connect(self.picker1, 
                         SIGNAL("elementDoubleClicked(PyQt_PyObject)"),
                         self.elementDoubleClicked)
        
        #self.connect(self.zoomer1, SIGNAL("zoomed(QRectF)"),
        #             self.zoomed1)
        #self.timerId = self.startTimer(1000)

    def alignScales(self):
        # raise RuntimeError("ERROR")
        return
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

    def setErrorBar(self, on):
        self.curves1[0].errorOnTop = on

    def moveCurves(self, ax, fraction = 0.80):
        scalediv = self.axisScaleDiv(ax)
        sr, sl = scalediv.upperBound(), scalediv.lowerBound()
        sl1, sr1 = sl + (sr-sl)*fraction, sr + (sr-sl)*fraction
        self.setAxisScale(ax, sl1, sr1)

    def scaleXBottom(self, factor = None):
        scalediv = self.axisScaleDiv(Qwt.QwtPlot.xBottom)
        sr, sl = scalediv.upperBound(), scalediv.lowerBound()
        if factor is not None:
            dx = (sr - sl)*(factor-1.0)/2
            #print "bound:",scalediv.lowerBound(), scalediv.upperBound()
            self.setAxisScale(Qwt.QwtPlot.xBottom, sl - dx, sr + dx)
        else:
            bound = self.curvesBound()
            w = bound.width()
            h = bound.height()
            #bound.adjust(0.0, -h*.1, 0.0, h*.1)
            xmin = bound.left()
            xmax = bound.right()
            if w > 0.0: self.setAxisScale(Qwt.QwtPlot.xBottom, xmin, xmax)
            #if h > 0.0: self.setAxisScale(Qwt.QwtPlot.yLeft, ymin, ymax)

        # leave replot to the caller
        #self.replot()
        
    def scaleYLeft(self, factor = None):
        scalediv = self.axisScaleDiv(Qwt.QwtPlot.yLeft)
        sr, sl = scalediv.upperBound(), scalediv.lowerBound()
        if factor is not None:
            dy = (sr - sl)*(factor-1.0)/2
            #print "bound:",scalediv.lowerBound(), scalediv.upperBound()
            self.setAxisScale(Qwt.QwtPlot.yLeft, sl - dy, sr + dy)
        else:
            bound = self.curvesBound()
            w = bound.width()
            h = bound.height()
        
            #bound.adjust(0.0, -h*.1, 0.0, h*.1)
            ymin = bound.top() - h*.05
            ymax = bound.bottom() + h*.03
            xmin = bound.left()
            xmax = bound.right()
            #if w > 0.0: self.setAxisScale(Qwt.QwtPlot.xBottom, xmin, xmax)
            if h > 0.0: self.setAxisScale(Qwt.QwtPlot.yLeft, ymin, ymax)

        # leave replot to the caller
        #self.replot()

    def setColor(self, c):
        symb = self.curve1.symbol()
        pen = symb.pen()
        pen.setColor(c)
        symb.setPen(pen)
        br = symb.brush()
        br.setColor(c)
        symb.setBrush(br)
        self.curves1[0].setSymbol(symb)

        pen = self.curves1[0].pen()
        pen.setColor(c)
        self.curves1[0].setPen(pen)

    def curvesBound(self):
        bd = self.curves1[0].boundingRect()
        if self.curves1[1].isVisible():
            bd = bd.united(self.curves1[1].boundingRect())
        if self.curves1[2].isVisible():
            bd = bd.united(self.curves1[2].boundingRect())
        if self.curve2.isVisible():
            bd = bd.united(self.curve2.boundingRect())
        return bd

    def closeEvent(self, e):
        self._cadata.close()
        e.accept()

class ApCaArrayPlot(Qwt.QwtPlot):
    def __init__(self, pvs, **kwargs):
        """initialization
        
        Parameters
        -----------
        pvs: waveform PV list
        parent : None
        title : 
        """
        parent = kwargs.pop("parent", None)
        super(ApCaArrayPlot, self).__init__(parent)
        self.live = kwargs.get("live", True)
        self.__hold = False

        self.setCanvasBackground(Qt.white)
        #self.setAxisAutoScale(Qwt.QwtPlot.yLeft, False)
        self.setAutoReplot(False)

        self.plotLayout().setAlignCanvasToScales(True)

        self.drift = False
        self._count = []
        self._pvs, self.curves, self._y = {}, [], []
        self._golden, self._ref = [], []
        self._x = kwargs.get("x", [])
        for i,pvl in enumerate(pvs):
            name, color = COLORS[i%len(COLORS)]
            #c = Qwt.QwtPlotCurve()
            c = ApErrBarCurve(color)
            #c.setBrush(QBrush(COLORS[i % len(COLORS)]))
            #c.setPen(QPen(colors))
            #c.setPen(QPen(Qt.red, 4))
            if i <= len(self._x):
                self._x.append(range(len(pvl)))
            c.setData([np.nan for j in range(len(pvl))], self._x[i])
            c.attach(self)
            self.curves.append(c)
            self._golden.append(None)
            self._ref.append(None)
            for j,pv in enumerate(pvl):
                self._pvs.setdefault(pv, [])
                self._pvs[pv].append((i,j))
            self._count.append([0] * len(pvl))
            self._y = [[0.0] * len(pvl)]
        # one more plot with second y axis
        self.curve2 = Qwt.QwtPlotCurve()

        #self.setMinimumSize(300, 100)
        grid1 = Qwt.QwtPlotGrid()
        grid1.attach(self)
        pen = grid1.majPen()
        pen.setStyle(Qt.DotLine)
        pen.setWidthF(1.2)
        grid1.setMajPen(pen)

        self.picker1 = None
        #self.zoomer1 = None
        self.zoomer1 = Qwt.QwtPlotZoomer(Qwt.QwtPlot.xBottom,
                                         Qwt.QwtPlot.yLeft,
                                         Qwt.QwtPicker.DragSelection,
                                         Qwt.QwtPicker.AlwaysOff,
                                         self.canvas())
        self.zoomer1.setRubberBandPen(QPen(Qt.black))
        # zoom in and out and Home
        self.zoomer1.setKeyPattern(Qwt.QwtEventPattern.KeyRedo, Qt.Key_I)
        self.zoomer1.setKeyPattern(Qwt.QwtEventPattern.KeyUndo, Qt.Key_O)
        self.zoomer1.setKeyPattern(Qwt.QwtEventPattern.KeyHome, Qt.Key_Home)
        #self.zoomer1.setMousePattern(Qwt.QwtEventPattern.MouseSelect3, Qt.NoButton)
        #self.zoomer1.setMousePattern(Qwt.QwtEventPattern.MouseSelect6, Qt.NoButton)
        # right click will not zoom to home
        self.zoomer1.setMousePattern(Qwt.QwtEventPattern.MouseSelect2, Qt.NoButton)
        self.connect(self.zoomer1, SIGNAL("zoomed(const QwtDoubleRect&)"),
                     self.zoomed)

        self.markers = []
        #self.addMarkers(None)
        #self.marker = Qwt.QwtPlotMarker()
        #self.marker.attach(self)
        #self.marker.setLabelAlignment(Qt.AlignLeft)
        #self.marker.setLabelAlignment(Qt.AlignBottom)
        #self.marker.setValue(100, 0)
        #self.marker.setLabel(Qwt.QwtText("Hello"))
        #self.connect(self, SIGNAL("doubleClicked
        self._cadata = CaDataMonitor()
        for pv in self._pvs.keys():
            self._cadata.addHook(pv, self._ca_update)
        self._cadata.addPv(self._pvs.keys())

    def zoomed(self, r):
        #if self.zoomer1.zoomRectIndex() == 0:
        #    self.setAxisAutoScale(self.zoomer1.xAxis())
        #    self.setAxisAutoScale(self.zoomer1.yAxis())
        #    self.replot()
        #print "zoomed"
        pass

    def _ca_update(self, val, idx = None):
        if self.__hold: return
        if not self.live: return
        #print "Updating %s: " % val.name, self._pvs[val.name], val
        for i,j in self._pvs.get(val.name, []):
            self._count[i][j] += 1
            self._y[i][j] = val
            c = self.curves[i]
            x, y, e1 = c.data()
            if self._ref[i] is not None and self.drift:
                y = [self._y[i][k] - self._ref[i][k]
                     for k in range(len(self._y[i]))]
            else:
                y = self._y[i]
            c.setData(y, x, e1)

        self.replot()

    def saveAsReference(self):
        self.__hold = True
        for i,c in enumerate(self.curves):
            xi, yi, ei = c.data()
            self._ref[i] = yi
        self.__hold = False

    def setDrift(self, on):
        if on:
            self.saveAsReference()
            self.drift = True
        else:
            self.drift = False
        self.replot()

    def _setAutoScale(self, on):
        if on:
            self.zoomer1.reset()
            self.zoomer1.setEnabled(False)
            self.setAxisAutoScale(Qwt.QwtPlot.yLeft)
        else:
            self.__hold = True
            self.zoomer1.setEnabled(True)
            asd = self.axisScaleDiv(Qwt.QwtPlot.yLeft)
            print asd.lowerBound(), asd.upperBound()
            self.setAxisScale(Qwt.QwtPlot.yLeft, asd.lowerBound(),
                              asd.upperBound())
            # has to replot before base
            self.zoomer1.setZoomBase(True)
            self.__hold = False

    def contextMenuEvent(self, e):
        cmenu = QMenu()
        m_drift = QAction("Drift", self)
        m_drift.setCheckable(True)
        #c = QApplication.clipboard()
        m_drift.setChecked(self.drift)
        self.connect(m_drift, SIGNAL("toggled(bool)"), self.setDrift)
        cmenu.addAction(m_drift)

        m_autoscale = QAction("Auto Scale", self)
        m_autoscale.setCheckable(True)
        m_autoscale.setChecked(self.axisAutoScale(Qwt.QwtPlot.yLeft))
        self.connect(m_autoscale, SIGNAL("toggled(bool)"), self._setAutoScale)
        cmenu.addAction(m_autoscale)

        cmenu.exec_(e.globalPos())

    def setMarkers(self, mks, on = True):
        names, locs = zip(*mks)
        if not on:
            for r in self.markers:
                if r[0] in names: r[1].detach()
        else:
            known_names, mklst = [], []
            if self.markers: known_names, mklst = zip(*self.markers)
            for r in mks:
                if r[0] in known_names:
                    i = known_names.index(r[0])
                    mklst[i].attach(self)
                    continue
                mk1 = Qwt.QwtPlotMarker()
                mk1.setSymbol(Qwt.QwtSymbol(
                        Qwt.QwtSymbol.Diamond,
                        QBrush(Qt.blue),
                        QPen(Qt.red, 1),
                        QSize(12, 12)))
                mk1.setValue(r[1], 0)
                mk1.setAxis(Qwt.QwtPlot.xBottom, Qwt.QwtPlot.yRight)
                mk1.attach(self)
                self.markers.append([r[0], mk1])

    #def elementDoubleClicked(self, elem):
    #    print "element selected:", elem
    #    self.emit(SIGNAL("elementSelected(PyQt_PyObject)"), elem)
    
    def setMagnetProfile(self, mprof):
        self.curvemag = Qwt.QwtPlotCurve("Magnet Profile")
        # get x, y, color(optional)
        # x, y and profile(left, right, name)
        mags, magv, magp = [], [], []
        for rec in mprof:
            mags.extend(rec[0])
            magv.extend(rec[1])
            if rec[3]:
                magp.append((min(rec[0]), max(rec[0]), 
                             rec[3].encode('ascii')))
        self.curvemag.setData(mags, magv)
        self.curvemag.setYAxis(Qwt.QwtPlot.yRight)
        # fixed scale
        self.setAxisScale(Qwt.QwtPlot.yRight, -2, 20)
        self.enableAxis(Qwt.QwtPlot.yRight, False)

        self.curvemag.attach(self)

        if magp and sip.SIP_VERSION_STR > '4.10.2':
            self.picker1 = MagnetPicker(self.canvas(), profile=magp)
            #sb = [v[0] for v in magp]
            #se = [v[1] for v in magp]
            #names = [v[2] for v in magp]
            #self.picker1.addMagnetProfile(sb, se, names)
            self.picker1.setTrackerPen(QPen(Qt.red, 4))
            self.connect(self.picker1, 
                         SIGNAL("elementDoubleClicked(PyQt_PyObject)"),
                         self.elementDoubleClicked)
        
        #self.connect(self.zoomer1, SIGNAL("zoomed(QRectF)"),
        #             self.zoomed1)
        #self.timerId = self.startTimer(1000)

    def alignScales(self):
        # raise RuntimeError("ERROR")
        return
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

    def setErrorBar(self, on):
        self.curves1[0].errorOnTop = on

    def moveCurves(self, ax, fraction = 0.80):
        scalediv = self.axisScaleDiv(ax)
        sr, sl = scalediv.upperBound(), scalediv.lowerBound()
        sl1, sr1 = sl + (sr-sl)*fraction, sr + (sr-sl)*fraction
        self.setAxisScale(ax, sl1, sr1)

    def scaleXBottom(self, factor = None):
        scalediv = self.axisScaleDiv(Qwt.QwtPlot.xBottom)
        sr, sl = scalediv.upperBound(), scalediv.lowerBound()
        if factor is not None:
            dx = (sr - sl)*(factor-1.0)/2
            #print "bound:",scalediv.lowerBound(), scalediv.upperBound()
            self.setAxisScale(Qwt.QwtPlot.xBottom, sl - dx, sr + dx)
        else:
            bound = self.curvesBound()
            w = bound.width()
            h = bound.height()
            #bound.adjust(0.0, -h*.1, 0.0, h*.1)
            xmin = bound.left()
            xmax = bound.right()
            if w > 0.0: self.setAxisScale(Qwt.QwtPlot.xBottom, xmin, xmax)
            #if h > 0.0: self.setAxisScale(Qwt.QwtPlot.yLeft, ymin, ymax)

        # leave replot to the caller
        #self.replot()
        
    def scaleYLeft(self, factor = None):
        scalediv = self.axisScaleDiv(Qwt.QwtPlot.yLeft)
        sr, sl = scalediv.upperBound(), scalediv.lowerBound()
        if factor is not None:
            dy = (sr - sl)*(factor-1.0)/2
            #print "bound:",scalediv.lowerBound(), scalediv.upperBound()
            self.setAxisScale(Qwt.QwtPlot.yLeft, sl - dy, sr + dy)
        else:
            bound = self.curvesBound()
            w = bound.width()
            h = bound.height()
        
            #bound.adjust(0.0, -h*.1, 0.0, h*.1)
            ymin = bound.top() - h*.05
            ymax = bound.bottom() + h*.03
            xmin = bound.left()
            xmax = bound.right()
            #if w > 0.0: self.setAxisScale(Qwt.QwtPlot.xBottom, xmin, xmax)
            if h > 0.0: self.setAxisScale(Qwt.QwtPlot.yLeft, ymin, ymax)

        # leave replot to the caller
        #self.replot()

    def setColor(self, c):
        symb = self.curve1.symbol()
        pen = symb.pen()
        pen.setColor(c)
        symb.setPen(pen)
        br = symb.brush()
        br.setColor(c)
        symb.setBrush(br)
        self.curves1[0].setSymbol(symb)

        pen = self.curves1[0].pen()
        pen.setColor(c)
        self.curves1[0].setPen(pen)

    def curvesBound(self):
        bd = self.curves1[0].boundingRect()
        if self.curves1[1].isVisible():
            bd = bd.united(self.curves1[1].boundingRect())
        if self.curves1[2].isVisible():
            bd = bd.united(self.curves1[2].boundingRect())
        if self.curve2.isVisible():
            bd = bd.united(self.curve2.boundingRect())
        return bd

    def closeEvent(self, e):
        self._cadata.close()
        e.accept()


class ApLivePlotPvList(Qwt.QwtPlot):
    def __init__(self, pvs, **kwargs): 
        """initialization
        
        Parameters
        -----------
        parent : None
        lat : 
        """
        parent   = kwargs.pop("parent", None)
        errorbar = kwargs.get("errorbar", False)
        title    = kwargs.get("title", None)
        pvm      = kwargs.get("pvm", None)
        samples  = kwargs.get("samples", 10)

        super(ApLivePlotPvList, self).__init__(parent)

        self._hold = True
        self._pvs = tuple([pv for pv in pvs])
        self._val_golden = kwargs.get("golden", [0.0] * len(pvs))
        self._val_ref    = kwargs.get("reference", [0.0] * len(pvs))

        if pvm is None:
            self._data = dict([(pv, deque([ap.catools.caget(pv)], samples))
                               for pv in pvs])
        else:
            self._data = dict([(pv, deque([pvm.get(pv)], samples))
                               for pv in pvs])
        self._x = kwargs.pop("x", range(len(pvs)))
            
        self.connect(pvm, QtCore.SIGNAL("dataChanged(PyQt_PyObject)"),
                     self.updatePvData)

        self.setCanvasBackground(Qt.white)
        self.errorOnTop = errorbar
        # disable implicit replotting, use manual replot() instead.
        self.setAutoReplot(False)

        self.plotLayout().setAlignCanvasToScales(True)

        self._curve0 = ApPlotCurve(curvePen = QPen(Qt.black, 2),
                                   errorOnTop = False
                                   )
        self._curve0.attach(self)

        self._curve1 = ApPlotCurve(
            curvePen = QPen(Qt.red, 3.0),
            curveSymbol = Qwt.QwtSymbol(
                Qwt.QwtSymbol.Ellipse,
                QBrush(Qt.red),
                QPen(Qt.black, 1.0),
                QSize(8, 8)),
            errorPen = QPen(Qt.black, 1.0),
            errorCap = 6,
            errorOnTop = self.errorOnTop,
            )

        self._curve1.attach(self)

        self._curve2 = Qwt.QwtPlotCurve()
        self._curve2.setPen(QPen(Qt.green, 3, Qt.DashLine))
        self._curve2.attach(self)
        self._curve2.setZ(self._curve1.z() + 2.0)
        self._curve2.setVisible(False)

        self.curves = [self._curve0, self._curve1, self._curve2]

        #print "Golden orbit is attached"
        #self.bound = self.curve1.boundingRect()
        #if self.golden is not None:
        #    self.bound = self.bound.united(self.golden.boundingRect())

        self.curvemag = None

        #self.setMinimumSize(300, 100)
        grid1 = Qwt.QwtPlotGrid()
        grid1.attach(self)
        pen = grid1.majPen()
        pen.setStyle(Qt.DotLine)
        pen.setWidthF(1.2)
        grid1.setMajPen(pen)
        #print "Width", grid1.majPen().widthF(), grid1.majPen().color()

        self.picker1 = None
        #self.zoomer1 = None
        self.zoomer1 = Qwt.QwtPlotZoomer(Qwt.QwtPlot.xBottom,
                                         Qwt.QwtPlot.yLeft,
                                         Qwt.QwtPicker.DragSelection,
                                         Qwt.QwtPicker.AlwaysOff,
                                         self.canvas())
        self.zoomer1.setRubberBandPen(QPen(Qt.black))

        self.markers = []

        #self.addMarkers(None)
        #self.marker = Qwt.QwtPlotMarker()
        #self.marker.attach(self)
        #self.marker.setLabelAlignment(Qt.AlignLeft)
        #self.marker.setLabelAlignment(Qt.AlignBottom)
        #self.marker.setValue(100, 0)
        #self.marker.setLabel(Qwt.QwtText("Hello"))
        #self.connect(self, SIGNAL("doubleClicked
        self.scaleXBottom()
        self.scaleYLeft()
        self.replot()
        self._hold = False

    def updatePvData(self, val):
        if self._hold: return
        self._hold = True
        pv = val.name
        try:
            i = self._pvs.index(val.name)
        except:
            return
        if pv not in self._pvs: return
        self._data[pv].append(val)
        y = [self._data[pv][-1] for pv in self._pvs]
        e = [np.std(self._data[pv]) for pv in self._pvs]
        self._curve1.setData(self._x, y, e)
        self.replot()
        print pv, val
        self._hold = False

    def setMarkers(self, mks, on = True):
        names, locs = zip(*mks)
        if not on:
            for r in self.markers:
                if r[0] in names: r[1].detach()
        else:
            known_names, mklst = [], []
            if self.markers: known_names, mklst = zip(*self.markers)
            for r in mks:
                if r[0] in known_names:
                    i = known_names.index(r[0])
                    mklst[i].attach(self)
                    continue
                mk1 = Qwt.QwtPlotMarker()
                mk1.setSymbol(Qwt.QwtSymbol(
                Qwt.QwtSymbol.Diamond,
                QBrush(Qt.blue),
                QPen(Qt.red, 1),
                QSize(12, 12)))
                mk1.setValue(r[1], 0)
                mk1.setAxis(Qwt.QwtPlot.xBottom, Qwt.QwtPlot.yRight)
                mk1.attach(self)
                self.markers.append([r[0], mk1])

    def elementDoubleClicked(self, elem):
        print "element selected:", elem
        self.emit(SIGNAL("elementSelected(PyQt_PyObject)"), elem)

    
    def setMagnetProfile(self, mprof):
        self.curvemag = Qwt.QwtPlotCurve("Magnet Profile")
        # get x, y, color(optional)
        # x, y and profile(left, right, name)
        mags, magv, magp = [], [], []
        for rec in mprof:
            mags.extend(rec[0])
            magv.extend(rec[1])
            if rec[3]:
                magp.append((min(rec[0]), max(rec[0]), 
                             rec[3].encode('ascii')))
        self.curvemag.setData(mags, magv)
        self.curvemag.setYAxis(Qwt.QwtPlot.yRight)
        # fixed scale
        self.setAxisScale(Qwt.QwtPlot.yRight, -2, 20)
        self.enableAxis(Qwt.QwtPlot.yRight, False)

        self.curvemag.attach(self)

        if magp and sip.SIP_VERSION_STR > '4.10.2':
            self.picker1 = MagnetPicker(self.canvas(), profile=magp)
            #sb = [v[0] for v in magp]
            #se = [v[1] for v in magp]
            #names = [v[2] for v in magp]
            #self.picker1.addMagnetProfile(sb, se, names)
            self.picker1.setTrackerPen(QPen(Qt.red, 4))
            self.connect(self.picker1, 
                         SIGNAL("elementDoubleClicked(PyQt_PyObject)"),
                         self.elementDoubleClicked)
        
        #self.connect(self.zoomer1, SIGNAL("zoomed(QRectF)"),
        #             self.zoomed1)
        #self.timerId = self.startTimer(1000)

    def alignScales(self):
        # raise RuntimeError("ERROR")
        return
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

    def __updatePlot(self):
        self._curve1.setData()
        if self.golden is not None: self.golden.update()

    def setErrorBar(self, on):
        self._curve1.errorOnTop = on

    def moveCurves(self, ax, fraction = 0.80):
        scalediv = self.axisScaleDiv(ax)
        sr, sl = scalediv.upperBound(), scalediv.lowerBound()
        sl1, sr1 = sl + (sr-sl)*fraction, sr + (sr-sl)*fraction
        self.setAxisScale(ax, sl1, sr1)

    def scaleXBottom(self, factor = None):
        scalediv = self.axisScaleDiv(Qwt.QwtPlot.xBottom)
        sr, sl = scalediv.upperBound(), scalediv.lowerBound()
        if factor is not None:
            dx = (sr - sl)*(factor-1.0)/2
            #print "bound:",scalediv.lowerBound(), scalediv.upperBound()
            self.setAxisScale(Qwt.QwtPlot.xBottom, sl - dx, sr + dx)
        else:
            bound = self.curvesBound()
            w = bound.width()
            h = bound.height()
            #bound.adjust(0.0, -h*.1, 0.0, h*.1)
            xmin = bound.left()
            xmax = bound.right()
            if w > 0.0: self.setAxisScale(Qwt.QwtPlot.xBottom, xmin, xmax)
            #if h > 0.0: self.setAxisScale(Qwt.QwtPlot.yLeft, ymin, ymax)

        # leave replot to the caller
        #self.replot()
        
    def scaleYLeft(self, factor = None):
        scalediv = self.axisScaleDiv(Qwt.QwtPlot.yLeft)
        sr, sl = scalediv.upperBound(), scalediv.lowerBound()
        if factor is not None:
            dy = (sr - sl)*(factor-1.0)/2
            #print "bound:",scalediv.lowerBound(), scalediv.upperBound()
            self.setAxisScale(Qwt.QwtPlot.yLeft, sl - dy, sr + dy)
        else:
            bound = self.curvesBound()
            w = bound.width()
            h = bound.height()
        
            #bound.adjust(0.0, -h*.1, 0.0, h*.1)
            ymin = bound.top() - h*.05
            ymax = bound.bottom() + h*.03
            xmin = bound.left()
            xmax = bound.right()
            #if w > 0.0: self.setAxisScale(Qwt.QwtPlot.xBottom, xmin, xmax)
            if h > 0.0: self.setAxisScale(Qwt.QwtPlot.yLeft, ymin, ymax)

        # leave replot to the caller
        #self.replot()

    def plotCurve2(self, y, x = None):
        """
        hide curve if x,y are both None
        """
        if y is None and x is None:
            self.curve2.detach()
            self.curve2.setVisible(False)
            #print "disabling desired orbit and quit"
            return

        self.curve2.attach(self)
        self.curve2.setVisible(True)
        if x is not None:
            self.curve2.setData(x, y)
            return
        data = self.curve2.data()
        vx = [data.x(i) for i in range(data.size())]
        self.curve2.setData(vx, y)
        
    def setColor(self, c):
        symb = self._curve1.symbol()
        pen = symb.pen()
        pen.setColor(c)
        symb.setPen(pen)
        br = symb.brush()
        br.setColor(c)
        symb.setBrush(br)
        self._curve1.setSymbol(symb)

        pen = self._curve1.pen()
        pen.setColor(c)
        self._curve1.setPen(pen)

    def addCurve(self, **kwargs):
        x = kwargs.get('x', None)
        y = kwargs.get('y', None)
        yerr = kwargs.get('yerr', None)
        curv = ApPlotCurve(
            curvePen = kwargs.get("curvePen", QPen(Qt.black, 2.0)),
            curveStyle = kwargs.get("curveStyle", Qwt.QwtPlotCurve.Lines),
            #curveSymbol = kwargs.get("curveSymbol", Qwt.QwtSymbol(
            #        Qwt.QwtSymbol.Ellipse,
            #        QBrush(Qt.red),
            #        QPen(Qt.black, 1.0),
            #        QSize(8, 8))),
            curveSymbol = kwargs.get("curveSymbol", Qwt.QwtSymbol()),
            errorPen = kwargs.get("errorPen", QPen(Qt.black, 1.0)),
            errorCap = kwargs.get("errorCap", 6),
            errorOnTop = kwargs.get("errorOnTop", False),
            title = kwargs.get("title", "")
            )

        if x is not None and y is not None: curv.setData(x, y, yerr)
        curv.attach(self)
        self.excurv.append(curv)
        return curv

    def curvesBound(self):
        bd = self._curve1.boundingRect()
        if self._curve2.isVisible():
            bd = bd.united(self._curve2.boundingRect())
        for curv in self.curves:
            if not curv.isVisible(): continue
            bd = bd.united(curv.boundingRect())
        return bd


class ApMdiSubPlot(QMdiSubWindow):
    def __init__(self, parent = None, data = None, live = True,
                 element_fields = []):
        super(ApMdiSubPlot, self).__init__(parent)
        self.aplot = ApPlot()
        self.setWidget(self.aplot)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.data = data # ApVirtualElement
        self._eflist = element_fields
        self.live = live
        self.err_only  = False
        self.connect(self.aplot, SIGNAL("elementSelected(PyQt_PyObject)"),
                     self.elementSelected)
        self.setMinimumSize(400, 100)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

    def updatePlot(self, s = None, y = None, yerr = None):
        #print "updating the data"
        if (s, y, yerr) == (None, None, None) and self.data:
            self.data.update()
            s, y, yerr = self.data.data()

        #return
        #print "set data", type(s), type(y), type(yerr)
        if self.err_only: self.aplot.curve1.setData(s, yerr)
        else: self.aplot.curve1.setData(s, y, yerr)
        # set unit
        self.aplot.setAxisTitle(Qwt.QwtPlot.yLeft, self.data.label())
        #print "replot"
        #print s, y, yerr
        #print "done replot"
        self.aplot.replot()

    def elementSelected(self, elem):
        eleminfo = [self.data.machine, self.data.lattice, elem]
        self.emit(SIGNAL("elementSelected(PyQt_PyObject)"), eleminfo)

    def editElements(self):
        self.emit(SIGNAL("editVisibleElements()"))


    def currentXlim(self):
        """a tuple of (xmin, xmax)"""
        ax = self.aplot.axisScaleDiv(Qwt.QwtPlot.xBottom)
        return (ax.lowerBound(), ax.upperBound())

    def setMarkers(self, mks, on):
        self.aplot.setMarkers(mks, on)

    def disableElement(self, name):
        if name in self.data.names():
            self.data.disable(name)

    def setReferenceData(self, dat = None):
        if isinstance(dat, float):
            self.data.yref = np.ones(len(self.data.yref), 'd') * dat
        elif dat:
            self.data.yref = np.array(dat, 'd')
        else:
            s, y, yerr = self.data.data()
            self.data.yref = y

    def lattice(self):
        return self.data.lattice

    def machine(self):
        return self.data.machine

    def fullname(self):
        return (self.data.machine, self.data.lattice, 
                self.data.name, self.data.yfield)

    def plotCurve2(self, y, x = None):
        self.aplot.plotCurve2(y, x)


class ApSvdPlot(QDialog):
    def __init__(self, s):
        super(QDialog, self).__init__()

        self.s = s[:]

        self.p = Qwt.QwtPlot()

        self.c1 = Qwt.QwtPlotCurve("S-values")
        self.c1.setData(range(len(s)), s)
        self.c1.attach(self.p)
        #self.c1.setYAxis(Qwt.QwtPlot.yLeft)
        self.c1.setPen(QPen(Qt.blue, 2))
        #self.p.enableAxis(Qwt.QwtPlot.yLeft)
        self.p.setAxisTitle(Qwt.QwtPlot.yLeft, "Singular Values")

        self.c2 = Qwt.QwtPlotCurve("S/max(S) (log scale)")
        self.c2.setData(range(len(s)), s/np.max(s))
        self.c2.setPen(QPen(Qt.red, 3))
        self.c2.attach(self.p)
        self.c2.setYAxis(Qwt.QwtPlot.yRight)
        self.p.enableAxis(Qwt.QwtPlot.yRight)
        self.p.setAxisTitle(Qwt.QwtPlot.yRight, "Singular Values (logscale)")

        eg = Qwt.QwtLog10ScaleEngine()
        self.p.setAxisScaleEngine(Qwt.QwtPlot.yRight, eg)
        self.p.insertLegend(Qwt.QwtLegend(), Qwt.QwtPlot.BottomLegend)

        grid1 = Qwt.QwtPlotGrid()
        grid1.attach(self.p)
        grid1.setPen(QPen(Qt.black, 0.2, Qt.DotLine))

        hb = QHBoxLayout()
        hb.addWidget(QLabel("Show top"))
        self.ns = QComboBox()
        for i in [5,10,25,40,60,80,100,120,160] + range(200,len(s)+1,50): 
            self.ns.addItem("%d" % i)
        self.ns.addItem("%d" % len(s))

        hb.addWidget(self.ns)
        hb.addStretch()

        vb = QVBoxLayout()
        vb.addLayout(hb)
        vb.addWidget(self.p)
        self.setLayout(vb)
        self.resize(400, 300)

        self.picker1 = None
        #self.zoomer1 = None
        self.zoomer1 = Qwt.QwtPlotZoomer(Qwt.QwtPlot.xBottom,
                                         Qwt.QwtPlot.yLeft,
                                         Qwt.QwtPicker.DragSelection,
                                         Qwt.QwtPicker.AlwaysOff,
                                         self.p.canvas())
        self.zoomer1.setRubberBandPen(QPen(Qt.black))
        self.connect(self.ns, SIGNAL("currentIndexChanged(QString)"),
                     self.updatePlot)

    def updatePlot(self, txt):
        n, err = txt.toInt()
        self.c1.setData(range(1, n+1), self.s[:n])
        self.c2.setData(range(1, n+1), self.s[:n]/np.max(self.s))
        self.p.replot()

if __name__ == "__main__":
    #p = ApCaWaveformPlot(['V:2-SR-BI{BETA}X-I', 'V:2-SR-BI{BETA}Y-I'])
    #p = ApCaWaveformPlot(['V:2-SR-BI{ORBIT}X-I', 'V:2-SR-BI{ORBIT}Y-I'])
    #p = ApCaWaveformPlot(['BR-BI{DCCT:1}I-Wf'])
    p = ApCaArrayPlot([('V:2-SR:C29-BI:G2{PL1:3551}SA:X',
                        'V:2-SR:C29-BI:G2{PL2:3571}SA:X',
                        'V:2-SR:C29-BI:G4{PM1:3596}SA:X',
                        'V:2-SR:C29-BI:G4{PM1:3606}SA:X',
                        'V:2-SR:C29-BI:G6{PH2:3630}SA:X',
                        'V:2-SR:C29-BI:G6{PH1:3645}SA:X',)])
    import time
    #pvs = ['V:2-SR:C29-BI:G2{PL1:3551}SA:X',
    #       'V:2-SR:C29-BI:G2{PL2:3571}SA:X',
    #       'V:2-SR:C29-BI:G4{PM1:3596}SA:X',]
    #pvs = ['BR:A3-BI{BPM:6}Cnt:Trig-I', 'BR:A3-BI{BPM:7}Cnt:Trig-I']
    #pvs = ['LTB-MG{Bend:1}Energy-I-cal']
    #p = ApCaTimeSeriesPlot(pvs)
    p.show()
    cothread.WaitForQuit()

