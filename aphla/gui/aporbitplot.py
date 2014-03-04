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
from functools import partial

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


class ApCaPlot(Qwt.QwtPlot):
    def __init__(self, parent = None):
        super(Qwt.QwtPlot, self).__init__(parent)
        self.drift = False
        self.live = True
        self.curves = []
        self._hold = False
        self._cadata = None

        grid = Qwt.QwtPlotGrid()
        grid.attach(self)
        grid.setPen(QPen(Qt.black, 0, Qt.DotLine))
        #grid1 = Qwt.QwtPlotGrid()
        #grid1.attach(self)
        #pen = grid1.majPen()
        #pen.setStyle(Qt.DotLine)
        #pen.setWidthF(1.2)
        #grid1.setMajPen(pen)


        legend = Qwt.QwtLegend()
        legend.setItemMode(Qwt.QwtLegend.CheckableItem)
        self.insertLegend(legend, self.RightLegend)

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

        self.markers = [] # Qwt.QwtPlotMarker()
        #self.mark1.setLabelAlignment(Qt.AlignLeft | Qt.AlignTop)
        #self.mark1.setPen(QPen(QColor(0, 255, 0)))
        #self.mark1.attach(self)
        #self.markers = []
        #self.addMarkers(None)
        #self.marker = Qwt.QwtPlotMarker()
        #self.marker.attach(self)
        #self.marker.setLabelAlignment(Qt.AlignLeft)
        #self.marker.setLabelAlignment(Qt.AlignBottom)
        #self.marker.setValue(100, 0)
        #self.marker.setLabel(Qwt.QwtText("Hello"))

        self.connect(self, SIGNAL("legendChecked(QwtPlotItem*, bool)"),
                     self.showCurve)


    def setMarkers(self, mks, on = True):
        self.clearMarkers()
        if not mks: return
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
                        #Qwt.QwtSymbol.Diamond,
                        Qwt.QwtSymbol.Star1,
                        QBrush(Qt.blue),
                        QPen(Qt.red, 1),
                        QSize(10, 10)))
                mk1.setValue(r[1], 0)
                mk1.setLabel(Qwt.QwtText(r[0]))
                mk1.setLabelAlignment(Qt.AlignTop)
                #mk1.setLabelAlignment(Qt.AlignBottom)
                mk1.setAxis(Qwt.QwtPlot.xBottom, Qwt.QwtPlot.yRight)
                mk1.attach(self)
                self.markers.append([r[0], mk1])

    def clearMarkers(self):
        for name, mk in self.markers:
            mk.detach()
        self.markers = []

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
        self.showCurve(self.curvemag, True)

    def elementDoubleClicked(self, elems):
        pass

    def addMagnetProfile(self, sb, se, name, minlen = 0.2):
        self.picker1.addMagnetProfile(sb, se, name, minlen)

    def showCurve(self, c, on):
        c.setVisible(on)
        w = self.legend().find(c)
        if w and w.inherits("QwtLegendItem"):
            w.setChecked(on)

        #if any([c.isVisible() for c in self.curves])
        self.replot()

    def curvesBound(self, yax = Qwt.QwtPlot.yLeft):
        bd = QtCore.QRectF()
        #for c in self.curves:
        #    if not c.isVisible(): continue
        #    if c.yAxis() != yax: continue
        #    bd = bd.united(c.boundingRect())
        for c in self.itemList():
            if not c.isVisible(): continue
            if c.yAxis() != yax: continue
            if isinstance(c, Qwt.QwtPlotGrid): continue
            bd = bd.united(c.boundingRect())
        return bd

    def resetPlot(self, ax = Qwt.QwtPlot.yLeft):
        bd = self.curvesBound()
        if not bd.isValid(): return
        self.setAxisScale(ax, bd.bottom(), bd.top())
        self.setAxisScale(Qwt.QwtPlot.xBottom, bd.left(), bd.right())


    def contextMenuEvent(self, e):
        cmenu = QMenu()

        cmenu.addAction("Update", self.pullCaData)

        cmenu.addSeparator()

        m_reset = QAction("Reset Plot", self)
        self.connect(m_reset, SIGNAL("triggered(bool)"), self.resetPlot)
        cmenu.addAction(m_reset)

        cmenu.addSeparator()

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

        cmenu.addSeparator()
        cmenu.addAction("Zoom in X", partial(self.scaleX, factor=0.7),
                        QtGui.QKeySequence.ZoomIn)
        cmenu.addAction("Zoom out X", partial(self.scaleX, factor=1.4),
                        QtGui.QKeySequence.ZoomOut)
        cmenu.addAction("Auto fit X", self.scaleX)

        cmenu.addSeparator()
        cmenu.addAction("Zoom in Y", partial(self.scaleY, factor=0.7))
        cmenu.addAction("Zoom out Y", partial(self.scaleY, factor=1.4))
        cmenu.addAction("Auto fit Y", self.scaleY)

        cmenu.addSeparator()
        subm = QtGui.QMenu("Line Style", cmenu)
        for cmd in ["Increase Line Width", "Decrease Line Width"]:
            subm.addAction(cmd, partial(self.setPlotStyle, cmd=cmd))
        subm.addSeparator()
        for k,v in CURVE_STYLES:
            subm.addAction(k, partial(self.setPlotStyle, cmd=k))
        subm.addSeparator()
        for cmd in ["Increase Point Size", "Decrease Point Size"]:
            subm.addAction(cmd, partial(self.setPlotStyle, cmd=cmd))
        subm.addSeparator()
        for k,v in SYMBOLS:
            subm.addAction(k, partial(self.setPlotStyle, cmd=k))
        subm.addSeparator()
        for k,v in COLORS:
            subm.addAction(k, partial(self.setPlotStyle, color=v))

        cmenu.addMenu(subm)

        subm = QtGui.QMenu("Marker Style", cmenu)
        for k,v in SYMBOLS:
            subm.addAction(k, partial(self.setMarkerStyle, cmd=k))
        cmenu.addMenu(subm)

        cmenu.exec_(e.globalPos())

    def setDrift(self, on):
        if on:
            self.saveAsReference()
            self.drift = True
        else:
            self.drift = False
        self.replot()

    def _setAutoScale(self, on):
        if on:
            print "Enable autoscale"
            self.zoomer1.reset()
            self.zoomer1.setEnabled(False)
            self.setAxisAutoScale(Qwt.QwtPlot.yLeft)
        else:
            self._hold = True
            self.zoomer1.setEnabled(True)
            asd = self.axisScaleDiv(Qwt.QwtPlot.yLeft)
            #print asd.lowerBound(), asd.upperBound()
            print "Disable autoscale"
            self.setAxisScale(Qwt.QwtPlot.yLeft, asd.lowerBound(),
                              asd.upperBound())
            # has to replot before base
            self.zoomer1.setZoomBase(True)
            self._hold = False

    def scaleX(self, factor = None, axis = Qwt.QwtPlot.xBottom):
        if self.axisAutoScale(axis):
            self._setAutoScale(False)

        scalediv = self.axisScaleDiv(axis)
        sr, sl = scalediv.upperBound(), scalediv.lowerBound()
        if factor is not None:
            dx = (sr - sl)*(factor-1.0)/2
            self.setAxisScale(axis, sl - dx, sr + dx)
        else:
            bound = self.curvesBound()
            w = bound.width()
            h = bound.height()
            #bound.adjust(0.0, -h*.1, 0.0, h*.1)
            xmin = bound.left()
            xmax = bound.right()
            if w > 0.0: self.setAxisScale(axis, xmin, xmax)
            #if h > 0.0: self.setAxisScale(Qwt.QwtPlot.yLeft, ymin, ymax)

        # leave replot to the caller
        self.replot()
        
    def scaleY(self, factor = None, axis = Qwt.QwtPlot.yLeft):
        if self.axisAutoScale(axis):
            self._setAutoScale(False)

        scalediv = self.axisScaleDiv(axis)
        sr, sl = scalediv.upperBound(), scalediv.lowerBound()
        if factor is not None:
            dy = (sr - sl)*(factor-1.0)/2
            #print "bound:",scalediv.lowerBound(), scalediv.upperBound()
            self.setAxisScale(axis, sl - dy, sr + dy)
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
        self.replot()

    def zoomed(self, r):
        print "L/R:", r.left(), r.right()
        print "T/B:", r.top(), r.bottom()
        pass

    def pullCaData(self):
        pass

    def closeEvent(self, e):
        if self._cadata is not None: self._cadata.close()
        e.accept()

    def _set_symbol(self, c, s = None, dsize = None, color = None):
        symb = c.symbol()
        if s is not None:
            symb.setStyle(s)
        if dsize is not None:
            sz = symb.size() + QtCore.QSize(dsize, dsize)
            symb.setSize(sz)
        c.setSymbol(symb)

    def _set_line(self, c, ls = None, dwidth = None, color = None):
        pen, symb = c.pen(), c.symbol()
        if ls in [v[1] for v in CURVE_STYLES]:
            c.setStyle(ls)
        elif ls in [v[1] for v in PEN_STYLES]:
            pen.setStyle(ls)
            c.setPen(pen)
        if dwidth is not None:
            pen.setWidth(pen.width() + dwidth)
            c.setPen(pen)
        if color is not None:
            pen.setColor(color)
            c.setPen(pen)

    def setPlotStyle(self, **kwargs):
        for c in self.itemList():
            if not c.isVisible(): continue
            #if isinstance(c, Qwt.QwtPlotGrid): continue
            if not isinstance(c, (Qwt.QwtPlotCurve,)):
                continue
            st = kwargs.get("cmd", None)
            if st == "Increase Point Size":
                self._set_symbol(c, None, 1)
            elif st == "Decrease Point Size":
                self._set_symbol(c, None, -1)
            elif st in [v[0] for v in CURVE_STYLES]:
                for name,val in CURVE_STYLES:
                    if name == st: self._set_line(c, val)
            elif st in [v[0] for v in PEN_STYLES]:
                for name,val in PEN_STYLES:
                    if name == st: self._set_line(c, val)
            elif st in [v[0] for v in SYMBOLS]:
                for name,val in SYMBOLS:
                    if name == st: self._set_symbol(c, val)            
            elif st == "Increase Line Width":
                self._set_line(c, None, 1)
            elif st == "Decrease Line Width":
                self._set_line(c, None, -1)
            color = kwargs.get("color", None)
            if color in [v[1] for v in COLORS]:
                self._set_symbol(c, color=color)
                self._set_line(c, color=color)
        self.replot()

    def setMarkerStyle(self, **kwargs):
        for name,c in self.markers:
            if not c.isVisible(): continue
            st = kwargs.get("cmd", None)
            if st == "Increase Size":
                self._set_symbol(c, None, 1)
            elif st == "Decrease Size":
                self._set_symbol(c, None, -1)
            elif st in [v[0] for v in SYMBOLS]:
                for name,val in SYMBOLS:
                    if name == st: self._set_symbol(c, val)            
            color = kwargs.get("color", None)
            if color in [v[1] for v in COLORS]:
                self._set_symbol(c, color=color)
                self._set_line(c, color=color)
        self.replot()

class ApCaTimeSeriesPlot(ApCaPlot):
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

        self._t, self._vals, self._refs = [], {}, {}
        self._pvs = pvs
        self.curves = [ Qwt.QwtPlotCurve(pv) for pv in pvs ]
        for i,c in enumerate(self.curves):
            self._vals.setdefault(self._pvs[i], [])
            self._refs[pv] = -1
            name, color = COLORS[i % len(COLORS)]
            c.setPen(QPen(color))
            c.attach(self)

        self._timerId = self.startTimer(1500)
        
    def timerEvent(self, e):
        if not self.live: return
        if self._hold: return

        self._hold = True
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
        self._hold = False

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


class ApCaWaveformPlot(ApCaPlot):
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

        self.setCanvasBackground(Qt.white)
        self.setAutoReplot(False)

        self.plotLayout().setAlignCanvasToScales(True)

        self._pvs, self.curves, self._ref = pvs, [], []
        for i,pv in enumerate(pvs):
            name, color = COLORS[i % len(COLORS)]
            c = Qwt.QwtPlotCurve()
            c.setPen(QPen(color, 1.5))
            c.attach(self)
            self.curves.append(c)
            self._ref.append(None)

        # one more plot with second y axis
        #self.curve2 = Qwt.QwtPlotCurve()

        #self.setMinimumSize(300, 100)

        #self.connect(self, SIGNAL("doubleClicked
        self.count = 0
        self._cadata = CaDataMonitor()
        for pv in pvs:
            self._cadata.addHook(pv, self._ca_update)
        self._cadata.addPv(pvs)
        ymin, ymax = self._cadata.getRange()
        self.setAxisScale(Qwt.QwtPlot.yLeft, ymin, ymax)
        self.zoomer1.setZoomBase(True)
        self._cadata.start()

    def _ca_update(self, val, idx = None):
        if self._hold: return
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
        self._hold = True
        for i,c in enumerate(self.curves):
            d = c.data()
            self._ref[i] = [d.y(j) for j in range(d.size())]
            #print i, np.average(self._ref[i])
        self._hold = False

    def setDrift(self, on):
        if on:
            self.saveAsReference()
            self.drift = True
        else:
            self.drift = False


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

    def setErrorBar(self, on):
        self.curves1[0].errorOnTop = on

    def moveCurves(self, ax, fraction = 0.80):
        scalediv = self.axisScaleDiv(ax)
        sr, sl = scalediv.upperBound(), scalediv.lowerBound()
        sl1, sr1 = sl + (sr-sl)*fraction, sr + (sr-sl)*fraction
        self.setAxisScale(ax, sl1, sr1)


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



class ApCaArrayPlot(ApCaPlot):
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
        self.labels = kwargs.get("labels", None)

        self.setCanvasBackground(Qt.white)
        #self.setAxisAutoScale(Qwt.QwtPlot.yLeft, False)
        self.setAutoReplot(False)

        self.plotLayout().setAlignCanvasToScales(True)
        self.setMinimumSize(600, 100)

        self._count = []
        self.curves, self._y = [], []
        self._pvs = {} # (pv, (i_curve, j_point))
        self._golden, self._ref = [], []
        self._x = kwargs.get("x", [])
        for i,pvl in enumerate(pvs):
            name, color = COLORS[i%len(COLORS)]
            #c = Qwt.QwtPlotCurve()
            c = ApErrBarCurve(color)
            if self.labels is None or not self.labels[i]:
                c.setTitle("[%s ...]" % pvl[0])
            else:
                c.setTitle(self.labels[i])
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
            self._y.append([0.0] * len(pvl))
        # one more plot with second y axis
        self.curve2 = Qwt.QwtPlotCurve()
        
        for c in self.curves:
            self.showCurve(c, True)

        self.showCurve(self.curve2, True)

        self._cadata = CaDataMonitor(wait=0.6)
        for pv in self._pvs.keys():
            #self._cadata.addHook(pv, self._ca_update)
            self._cadata.addHook(pv, self._ca_update_all)
        self._cadata.addPv(self._pvs.keys())
        ymin, ymax = self._cadata.getRange()
        self.setAxisScale(Qwt.QwtPlot.yLeft, ymin, ymax)
        self.zoomer1.setZoomBase(True)
        self._cadata.start()

    def _ca_update(self, val, idx = None):
        if self._hold: return
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
        #QtGui.qApp.processEvents()

    def _ca_update_all(self, val, idx = None):
        if self._hold: return
        if not self.live: return
        for pv in self._pvs.keys():
            v1 = self._cadata.get(pv)
            #print "Updating %s: " % pv, v1
            for i,j in self._pvs.get(pv, []):
                self._count[i][j] += 1
                self._y[i][j] = v1

        for i, c in enumerate(self.curves):
            x, y, e1 = c.data()
            if self._ref[i] is not None and self.drift:
                y = [self._y[i][k] - self._ref[i][k]
                     for k in range(len(self._y[i]))]
            else:
                y = self._y[i]
            c.setData(y, x, e1)

        if any([c.isVisible() for c in self.curves]):
            self.replot()
        #QtGui.qApp.processEvents()

    def pullCaData(self):
        if not self._cadata: return
        self._cadata.pull()
        self._ca_update_all(None, None)

    def saveAsReference(self):
        self._hold = True
        for i,c in enumerate(self.curves):
            xi, yi, ei = c.data()
            self._ref[i] = yi
        self._hold = False

    def elementDoubleClicked(self, elem):
        #print "element selected:", elem
        self.emit(SIGNAL("elementSelected(PyQt_PyObject)"), elem)
    
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

    def closeEvent(self, e):
        self._cadata.close()
        e.accept()


class ApMdiSubPlot(QMdiSubWindow):
    def __init__(self, parent = None, **kw):
        super(ApMdiSubPlot, self).__init__(parent)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.err_only  = False
        self.live = True
        pvs = kw.pop("pvs", [])
        #self.aplot = ApCaWaveformPlot(pvs)
        self.aplot = ApCaArrayPlot(pvs, **kw)
        #self.connect(self.aplot, SIGNAL("elementSelected(PyQt_PyObject)"),
        #             self.elementSelected)
        self.setWidget(self.aplot)
        self.setMinimumSize(400, 100)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

    def elementSelected(self, elem):
        #eleminfo = [self.data.machine, self.data.lattice, elem]
        #self.emit(SIGNAL("elementSelected(PyQt_PyObject)"), eleminfo)
        pass

    def editElements(self):
        self.emit(SIGNAL("editVisibleElements()"))

    def currentXlim(self):
        """a tuple of (xmin, xmax)"""
        ax = self.aplot.axisScaleDiv(Qwt.QwtPlot.xBottom)
        return (ax.lowerBound(), ax.upperBound())

    def setMarkers(self, mks, on):
        self.aplot.setMarkers(mks, on)

    #def disableElement(self, name):
    #    if name in self.data.names():
    #        self.data.disable(name)

    #def setReferenceData(self, dat = None):
    #    if isinstance(dat, float):
    #        self.data.yref = np.ones(len(self.data.yref), 'd') * dat
    #    elif dat:
    #        self.data.yref = np.array(dat, 'd')
    #    else:
    #        s, y, yerr = self.data.data()
    #        self.data.yref = y

    #def lattice(self):
    #    return self.data.lattice

    #def machine(self):
    #    return self.data.machine

    #def fullname(self):
    #    return (self.data.machine, self.data.lattice, 
    #            self.data.name, self.data.yfield)

    #def plotCurve2(self, y, x = None):
    #    self.aplot.plotCurve2(y, x)


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
    pvs = [("SR:C19-BI{BPM:1}Pos:X-I", "SR:C19-BI{BPM:2}Pos:X-I",
            "SR:C19-BI{BPM:3}Pos:X-I", "SR:C19-BI{BPM:4}Pos:X-I",
            "SR:C19-BI{BPM:5}Pos:X-I","SR:C19-BI{BPM:6}Pos:X-I",
            "SR:C18-BI{BPM:1}Pos:X-I","SR:C18-BI{BPM:2}Pos:X-I",
            "SR:C18-BI{BPM:3}Pos:X-I","SR:C18-BI{BPM:4}Pos:X-I",
            "SR:C18-BI{BPM:5}Pos:X-I","SR:C18-BI{BPM:6}Pos:X-I",
            "SR:C13-BI{BPM:1}Pos:X-I","SR:C13-BI{BPM:2}Pos:X-I",
            "SR:C13-BI{BPM:3}Pos:X-I","SR:C13-BI{BPM:4}Pos:X-I",
            "SR:C13-BI{BPM:5}Pos:X-I","SR:C13-BI{BPM:6}Pos:X-I",
            "SR:C12-BI{BPM:1}Pos:X-I","SR:C12-BI{BPM:2}Pos:X-I",
            "SR:C12-BI{BPM:3}Pos:X-I","SR:C12-BI{BPM:4}Pos:X-I",
            "SR:C12-BI{BPM:5}Pos:X-I","SR:C12-BI{BPM:6}Pos:X-I",
            "SR:C11-BI{BPM:1}Pos:X-I","SR:C11-BI{BPM:2}Pos:X-I",
            "SR:C11-BI{BPM:3}Pos:X-I","SR:C11-BI{BPM:4}Pos:X-I",
            "SR:C11-BI{BPM:5}Pos:X-I","SR:C11-BI{BPM:6}Pos:X-I",
            "SR:C10-BI{BPM:1}Pos:X-I","SR:C10-BI{BPM:2}Pos:X-I",
            "SR:C10-BI{BPM:3}Pos:X-I","SR:C10-BI{BPM:4}Pos:X-I",
            "SR:C10-BI{BPM:5}Pos:X-I","SR:C10-BI{BPM:6}Pos:X-I",
            "SR:C17-BI{BPM:1}Pos:X-I","SR:C17-BI{BPM:2}Pos:X-I",
            "SR:C17-BI{BPM:3}Pos:X-I","SR:C17-BI{BPM:4}Pos:X-I",
            "SR:C17-BI{BPM:5}Pos:X-I","SR:C17-BI{BPM:6}Pos:X-I",
            "SR:C16-BI{BPM:1}Pos:X-I","SR:C16-BI{BPM:2}Pos:X-I",
            "SR:C16-BI{BPM:3}Pos:X-I","SR:C16-BI{BPM:4}Pos:X-I",
            "SR:C16-BI{BPM:5}Pos:X-I","SR:C16-BI{BPM:6}Pos:X-I",
            "SR:C15-BI{BPM:1}Pos:X-I","SR:C15-BI{BPM:2}Pos:X-I",
            "SR:C15-BI{BPM:3}Pos:X-I","SR:C15-BI{BPM:4}Pos:X-I",
            "SR:C15-BI{BPM:5}Pos:X-I","SR:C15-BI{BPM:6}Pos:X-I",
            "SR:C14-BI{BPM:1}Pos:X-I","SR:C14-BI{BPM:2}Pos:X-I",
            "SR:C14-BI{BPM:3}Pos:X-I","SR:C14-BI{BPM:4}Pos:X-I",
            "SR:C14-BI{BPM:5}Pos:X-I","SR:C14-BI{BPM:6}Pos:X-I",
            "SR:C30-BI{BPM:1}Pos:X-I","SR:C30-BI{BPM:2}Pos:X-I",
            "SR:C30-BI{BPM:3}Pos:X-I","SR:C30-BI{BPM:4}Pos:X-I",
            "SR:C30-BI{BPM:5}Pos:X-I","SR:C30-BI{BPM:6}Pos:X-I",
            "SR:C09-BI{BPM:1}Pos:X-I","SR:C09-BI{BPM:2}Pos:X-I",
            "SR:C09-BI{BPM:3}Pos:X-I","SR:C09-BI{BPM:4}Pos:X-I",
            "SR:C09-BI{BPM:5}Pos:X-I","SR:C09-BI{BPM:6}Pos:X-I",
            "SR:C08-BI{BPM:1}Pos:X-I","SR:C08-BI{BPM:2}Pos:X-I",
            "SR:C08-BI{BPM:3}Pos:X-I","SR:C08-BI{BPM:4}Pos:X-I",
            "SR:C08-BI{BPM:5}Pos:X-I","SR:C08-BI{BPM:6}Pos:X-I",
            "SR:C03-BI{BPM:1}Pos:X-I","SR:C03-BI{BPM:2}Pos:X-I",
            "SR:C03-BI{BPM:3}Pos:X-I","SR:C03-BI{BPM:4}Pos:X-I",
            "SR:C03-BI{BPM:5}Pos:X-I","SR:C03-BI{BPM:6}Pos:X-I",
            "SR:C02-BI{BPM:1}Pos:X-I","SR:C02-BI{BPM:2}Pos:X-I",
            "SR:C02-BI{BPM:3}Pos:X-I","SR:C02-BI{BPM:4}Pos:X-I",
            "SR:C02-BI{BPM:5}Pos:X-I","SR:C02-BI{BPM:6}Pos:X-I",
            "SR:C01-BI{BPM:1}Pos:X-I","SR:C01-BI{BPM:2}Pos:X-I",
            "SR:C01-BI{BPM:3}Pos:X-I","SR:C01-BI{BPM:4}Pos:X-I",
            "SR:C01-BI{BPM:5}Pos:X-I","SR:C01-BI{BPM:6}Pos:X-I",
            "SR:C07-BI{BPM:1}Pos:X-I","SR:C07-BI{BPM:2}Pos:X-I",
            "SR:C07-BI{BPM:3}Pos:X-I","SR:C07-BI{BPM:4}Pos:X-I",
            "SR:C07-BI{BPM:5}Pos:X-I","SR:C07-BI{BPM:6}Pos:X-I",
            "SR:C06-BI{BPM:1}Pos:X-I","SR:C06-BI{BPM:2}Pos:X-I",
            "SR:C06-BI{BPM:3}Pos:X-I","SR:C06-BI{BPM:4}Pos:X-I",
            "SR:C06-BI{BPM:5}Pos:X-I","SR:C06-BI{BPM:6}Pos:X-I",
            "SR:C05-BI{BPM:1}Pos:X-I","SR:C05-BI{BPM:2}Pos:X-I",
            "SR:C05-BI{BPM:3}Pos:X-I","SR:C05-BI{BPM:4}Pos:X-I",
            "SR:C05-BI{BPM:5}Pos:X-I","SR:C05-BI{BPM:6}Pos:X-I",
            "SR:C04-BI{BPM:1}Pos:X-I","SR:C04-BI{BPM:2}Pos:X-I",
            "SR:C04-BI{BPM:3}Pos:X-I","SR:C04-BI{BPM:4}Pos:X-I",
            "SR:C04-BI{BPM:5}Pos:X-I","SR:C04-BI{BPM:6}Pos:X-I",
            "SR:C22-BI{BPM:1}Pos:X-I","SR:C22-BI{BPM:2}Pos:X-I",
            "SR:C22-BI{BPM:3}Pos:X-I","SR:C22-BI{BPM:4}Pos:X-I",
            "SR:C22-BI{BPM:5}Pos:X-I","SR:C22-BI{BPM:6}Pos:X-I",
            "SR:C23-BI{BPM:1}Pos:X-I","SR:C23-BI{BPM:2}Pos:X-I",
            "SR:C23-BI{BPM:3}Pos:X-I","SR:C23-BI{BPM:4}Pos:X-I",
            "SR:C23-BI{BPM:5}Pos:X-I","SR:C23-BI{BPM:6}Pos:X-I",
            "SR:C20-BI{BPM:1}Pos:X-I","SR:C20-BI{BPM:2}Pos:X-I",
            "SR:C20-BI{BPM:3}Pos:X-I","SR:C20-BI{BPM:4}Pos:X-I",
            "SR:C20-BI{BPM:5}Pos:X-I","SR:C20-BI{BPM:6}Pos:X-I",
            "SR:C21-BI{BPM:1}Pos:X-I","SR:C21-BI{BPM:2}Pos:X-I",
            "SR:C21-BI{BPM:3}Pos:X-I","SR:C21-BI{BPM:4}Pos:X-I",
            "SR:C21-BI{BPM:5}Pos:X-I","SR:C21-BI{BPM:6}Pos:X-I",
            "SR:C26-BI{BPM:1}Pos:X-I","SR:C26-BI{BPM:2}Pos:X-I",
            "SR:C26-BI{BPM:3}Pos:X-I","SR:C26-BI{BPM:4}Pos:X-I",
            "SR:C26-BI{BPM:5}Pos:X-I","SR:C26-BI{BPM:6}Pos:X-I",
            "SR:C27-BI{BPM:1}Pos:X-I","SR:C27-BI{BPM:2}Pos:X-I",
            "SR:C27-BI{BPM:3}Pos:X-I","SR:C27-BI{BPM:4}Pos:X-I",
            "SR:C27-BI{BPM:5}Pos:X-I","SR:C27-BI{BPM:6}Pos:X-I",
            "SR:C24-BI{BPM:1}Pos:X-I","SR:C24-BI{BPM:2}Pos:X-I",
            "SR:C24-BI{BPM:3}Pos:X-I","SR:C24-BI{BPM:4}Pos:X-I",
            "SR:C24-BI{BPM:5}Pos:X-I","SR:C24-BI{BPM:6}Pos:X-I",
            "SR:C25-BI{BPM:1}Pos:X-I","SR:C25-BI{BPM:2}Pos:X-I",
            "SR:C25-BI{BPM:3}Pos:X-I","SR:C25-BI{BPM:4}Pos:X-I",
            "SR:C25-BI{BPM:5}Pos:X-I","SR:C25-BI{BPM:6}Pos:X-I",
            "SR:C28-BI{BPM:1}Pos:X-I","SR:C28-BI{BPM:2}Pos:X-I",
            "SR:C28-BI{BPM:3}Pos:X-I","SR:C28-BI{BPM:4}Pos:X-I",
            "SR:C28-BI{BPM:5}Pos:X-I","SR:C28-BI{BPM:6}Pos:X-I",
            "SR:C29-BI{BPM:1}Pos:X-I","SR:C29-BI{BPM:2}Pos:X-I",
            "SR:C29-BI{BPM:3}Pos:X-I","SR:C29-BI{BPM:4}Pos:X-I",
            "SR:C29-BI{BPM:5}Pos:X-I","SR:C29-BI{BPM:6}Pos:X-I"),
           ("SR:C19-BI{BPM:1}Pos:Y-I", "SR:C19-BI{BPM:2}Pos:Y-I",
            "SR:C19-BI{BPM:3}Pos:Y-I", "SR:C19-BI{BPM:4}Pos:Y-I",
            "SR:C19-BI{BPM:5}Pos:Y-I","SR:C19-BI{BPM:6}Pos:Y-I",
            "SR:C18-BI{BPM:1}Pos:Y-I","SR:C18-BI{BPM:2}Pos:Y-I",
            "SR:C18-BI{BPM:3}Pos:Y-I","SR:C18-BI{BPM:4}Pos:Y-I",
            "SR:C18-BI{BPM:5}Pos:Y-I","SR:C18-BI{BPM:6}Pos:Y-I",
            "SR:C13-BI{BPM:1}Pos:Y-I","SR:C13-BI{BPM:2}Pos:Y-I",
            "SR:C13-BI{BPM:3}Pos:Y-I","SR:C13-BI{BPM:4}Pos:Y-I",
            "SR:C13-BI{BPM:5}Pos:Y-I","SR:C13-BI{BPM:6}Pos:Y-I",
            "SR:C12-BI{BPM:1}Pos:Y-I","SR:C12-BI{BPM:2}Pos:Y-I",
            "SR:C12-BI{BPM:3}Pos:Y-I","SR:C12-BI{BPM:4}Pos:Y-I",
            "SR:C12-BI{BPM:5}Pos:Y-I","SR:C12-BI{BPM:6}Pos:Y-I",
            "SR:C11-BI{BPM:1}Pos:Y-I","SR:C11-BI{BPM:2}Pos:Y-I",
            "SR:C11-BI{BPM:3}Pos:Y-I","SR:C11-BI{BPM:4}Pos:Y-I",
            "SR:C11-BI{BPM:5}Pos:Y-I","SR:C11-BI{BPM:6}Pos:Y-I",
            "SR:C10-BI{BPM:1}Pos:Y-I","SR:C10-BI{BPM:2}Pos:Y-I",
            "SR:C10-BI{BPM:3}Pos:Y-I","SR:C10-BI{BPM:4}Pos:Y-I",
            "SR:C10-BI{BPM:5}Pos:Y-I","SR:C10-BI{BPM:6}Pos:Y-I",
            "SR:C17-BI{BPM:1}Pos:Y-I","SR:C17-BI{BPM:2}Pos:Y-I",
            "SR:C17-BI{BPM:3}Pos:Y-I","SR:C17-BI{BPM:4}Pos:Y-I",
            "SR:C17-BI{BPM:5}Pos:Y-I","SR:C17-BI{BPM:6}Pos:Y-I",
            "SR:C16-BI{BPM:1}Pos:Y-I","SR:C16-BI{BPM:2}Pos:Y-I",
            "SR:C16-BI{BPM:3}Pos:Y-I","SR:C16-BI{BPM:4}Pos:Y-I",
            "SR:C16-BI{BPM:5}Pos:Y-I","SR:C16-BI{BPM:6}Pos:Y-I",
            "SR:C15-BI{BPM:1}Pos:Y-I","SR:C15-BI{BPM:2}Pos:Y-I",
            "SR:C15-BI{BPM:3}Pos:Y-I","SR:C15-BI{BPM:4}Pos:Y-I",
            "SR:C15-BI{BPM:5}Pos:Y-I","SR:C15-BI{BPM:6}Pos:Y-I",
            "SR:C14-BI{BPM:1}Pos:Y-I","SR:C14-BI{BPM:2}Pos:Y-I",
            "SR:C14-BI{BPM:3}Pos:Y-I","SR:C14-BI{BPM:4}Pos:Y-I",
            "SR:C14-BI{BPM:5}Pos:Y-I","SR:C14-BI{BPM:6}Pos:Y-I",
            "SR:C30-BI{BPM:1}Pos:Y-I","SR:C30-BI{BPM:2}Pos:Y-I",
            "SR:C30-BI{BPM:3}Pos:Y-I","SR:C30-BI{BPM:4}Pos:Y-I",
            "SR:C30-BI{BPM:5}Pos:Y-I","SR:C30-BI{BPM:6}Pos:Y-I",
            "SR:C09-BI{BPM:1}Pos:Y-I","SR:C09-BI{BPM:2}Pos:Y-I",
            "SR:C09-BI{BPM:3}Pos:Y-I","SR:C09-BI{BPM:4}Pos:Y-I",
            "SR:C09-BI{BPM:5}Pos:Y-I","SR:C09-BI{BPM:6}Pos:Y-I",
            "SR:C08-BI{BPM:1}Pos:Y-I","SR:C08-BI{BPM:2}Pos:Y-I",
            "SR:C08-BI{BPM:3}Pos:Y-I","SR:C08-BI{BPM:4}Pos:Y-I",
            "SR:C08-BI{BPM:5}Pos:Y-I","SR:C08-BI{BPM:6}Pos:Y-I",
            "SR:C03-BI{BPM:1}Pos:Y-I","SR:C03-BI{BPM:2}Pos:Y-I",
            "SR:C03-BI{BPM:3}Pos:Y-I","SR:C03-BI{BPM:4}Pos:Y-I",
            "SR:C03-BI{BPM:5}Pos:Y-I","SR:C03-BI{BPM:6}Pos:Y-I",
            "SR:C02-BI{BPM:1}Pos:Y-I","SR:C02-BI{BPM:2}Pos:Y-I",
            "SR:C02-BI{BPM:3}Pos:Y-I","SR:C02-BI{BPM:4}Pos:Y-I",
            "SR:C02-BI{BPM:5}Pos:Y-I","SR:C02-BI{BPM:6}Pos:Y-I",
            "SR:C01-BI{BPM:1}Pos:Y-I","SR:C01-BI{BPM:2}Pos:Y-I",
            "SR:C01-BI{BPM:3}Pos:Y-I","SR:C01-BI{BPM:4}Pos:Y-I",
            "SR:C01-BI{BPM:5}Pos:Y-I","SR:C01-BI{BPM:6}Pos:Y-I",
            "SR:C07-BI{BPM:1}Pos:Y-I","SR:C07-BI{BPM:2}Pos:Y-I",
            "SR:C07-BI{BPM:3}Pos:Y-I","SR:C07-BI{BPM:4}Pos:Y-I",
            "SR:C07-BI{BPM:5}Pos:Y-I","SR:C07-BI{BPM:6}Pos:Y-I",
            "SR:C06-BI{BPM:1}Pos:Y-I","SR:C06-BI{BPM:2}Pos:Y-I",
            "SR:C06-BI{BPM:3}Pos:Y-I","SR:C06-BI{BPM:4}Pos:Y-I",
            "SR:C06-BI{BPM:5}Pos:Y-I","SR:C06-BI{BPM:6}Pos:Y-I",
            "SR:C05-BI{BPM:1}Pos:Y-I","SR:C05-BI{BPM:2}Pos:Y-I",
            "SR:C05-BI{BPM:3}Pos:Y-I","SR:C05-BI{BPM:4}Pos:Y-I",
            "SR:C05-BI{BPM:5}Pos:Y-I","SR:C05-BI{BPM:6}Pos:Y-I",
            "SR:C04-BI{BPM:1}Pos:Y-I","SR:C04-BI{BPM:2}Pos:Y-I",
            "SR:C04-BI{BPM:3}Pos:Y-I","SR:C04-BI{BPM:4}Pos:Y-I",
            "SR:C04-BI{BPM:5}Pos:Y-I","SR:C04-BI{BPM:6}Pos:Y-I",
            "SR:C22-BI{BPM:1}Pos:Y-I","SR:C22-BI{BPM:2}Pos:Y-I",
            "SR:C22-BI{BPM:3}Pos:Y-I","SR:C22-BI{BPM:4}Pos:Y-I",
            "SR:C22-BI{BPM:5}Pos:Y-I","SR:C22-BI{BPM:6}Pos:Y-I",
            "SR:C23-BI{BPM:1}Pos:Y-I","SR:C23-BI{BPM:2}Pos:Y-I",
            "SR:C23-BI{BPM:3}Pos:Y-I","SR:C23-BI{BPM:4}Pos:Y-I",
            "SR:C23-BI{BPM:5}Pos:Y-I","SR:C23-BI{BPM:6}Pos:Y-I",
            "SR:C20-BI{BPM:1}Pos:Y-I","SR:C20-BI{BPM:2}Pos:Y-I",
            "SR:C20-BI{BPM:3}Pos:Y-I","SR:C20-BI{BPM:4}Pos:Y-I",
            "SR:C20-BI{BPM:5}Pos:Y-I","SR:C20-BI{BPM:6}Pos:Y-I",
            "SR:C21-BI{BPM:1}Pos:Y-I","SR:C21-BI{BPM:2}Pos:Y-I",
            "SR:C21-BI{BPM:3}Pos:Y-I","SR:C21-BI{BPM:4}Pos:Y-I",
            "SR:C21-BI{BPM:5}Pos:Y-I","SR:C21-BI{BPM:6}Pos:Y-I",
            "SR:C26-BI{BPM:1}Pos:Y-I","SR:C26-BI{BPM:2}Pos:Y-I",
            "SR:C26-BI{BPM:3}Pos:Y-I","SR:C26-BI{BPM:4}Pos:Y-I",
            "SR:C26-BI{BPM:5}Pos:Y-I","SR:C26-BI{BPM:6}Pos:Y-I",
            "SR:C27-BI{BPM:1}Pos:Y-I","SR:C27-BI{BPM:2}Pos:Y-I",
            "SR:C27-BI{BPM:3}Pos:Y-I","SR:C27-BI{BPM:4}Pos:Y-I",
            "SR:C27-BI{BPM:5}Pos:Y-I","SR:C27-BI{BPM:6}Pos:Y-I",
            "SR:C24-BI{BPM:1}Pos:Y-I","SR:C24-BI{BPM:2}Pos:Y-I",
            "SR:C24-BI{BPM:3}Pos:Y-I","SR:C24-BI{BPM:4}Pos:Y-I",
            "SR:C24-BI{BPM:5}Pos:Y-I","SR:C24-BI{BPM:6}Pos:Y-I",
            "SR:C25-BI{BPM:1}Pos:Y-I","SR:C25-BI{BPM:2}Pos:Y-I",
            "SR:C25-BI{BPM:3}Pos:Y-I","SR:C25-BI{BPM:4}Pos:Y-I",
            "SR:C25-BI{BPM:5}Pos:Y-I","SR:C25-BI{BPM:6}Pos:Y-I",
            "SR:C28-BI{BPM:1}Pos:Y-I","SR:C28-BI{BPM:2}Pos:Y-I",
            "SR:C28-BI{BPM:3}Pos:Y-I","SR:C28-BI{BPM:4}Pos:Y-I",
            "SR:C28-BI{BPM:5}Pos:Y-I","SR:C28-BI{BPM:6}Pos:Y-I",
            "SR:C29-BI{BPM:1}Pos:Y-I","SR:C29-BI{BPM:2}Pos:Y-I",
            "SR:C29-BI{BPM:3}Pos:Y-I","SR:C29-BI{BPM:4}Pos:Y-I",
            "SR:C29-BI{BPM:5}Pos:Y-I","SR:C29-BI{BPM:6}Pos:Y-I"),
           ]

    #p = ApCaWaveformPlot(['V:2-SR-BI{BETA}Y-I', 'V:2-SR-BI{BETA}Y-I'])
    #p = ApCaWaveformPlot(['V:2-SR-BI{ORBIT}Y-I', 'V:2-SR-BI{ORBIT}Y-I'])
    #p = ApCaWaveformPlot(['BR-BI{DCCT:1}I-Wf'])
    #p = ApCaArrayPlot([('V:2-SR:C29-BI:G2{PL1:3551}SA:X',
    #                    'V:2-SR:C29-BI:G2{PL2:3571}SA:X',
    #                    'V:2-SR:C29-BI:G4{PM1:3596}SA:X',
    #                    'V:2-SR:C29-BI:G4{PM1:3606}SA:X',
    #                    'V:2-SR:C29-BI:G6{PH2:3630}SA:X',
    #                    'V:2-SR:C29-BI:G6{PH1:3645}SA:X',)])
    p = ApCaArrayPlot(pvs)
    import time
    #pvs = ['V:2-SR:C29-BI:G2{PL1:3551}SA:X',
    #       'V:2-SR:C29-BI:G2{PL2:3571}SA:X',
    #       'V:2-SR:C29-BI:G4{PM1:3596}SA:X',]
    #pvs = ['BR:A3-BI{BPM:6}Cnt:Trig-I', 'BR:A3-BI{BPM:7}Cnt:Trig-I']
    #pvs = ['LTB-MG{Bend:1}Energy-I-cal']
    #p = ApCaTimeSeriesPlot(pvs)
    p.show()
    cothread.WaitForQuit()

