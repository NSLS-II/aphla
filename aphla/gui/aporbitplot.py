"""
aporbit Plot
============

:author: Lingyun Yang <lyyang@bnl.gov>

The viewer module for `aporbit` GUI. This defines a plot and container widget.
"""

from PyQt4.QtCore import (
    PYQT_VERSION_STR, QFile, QFileInfo, QSettings,
    QObject, QString, QT_VERSION_STR, QTimer, QVariant, Qt, SIGNAL,
    QSize, QRectF, QLine, pyqtSignal)

from PyQt4.QtGui import (
    QAction, QApplication, QWidget, QColor,
    QDockWidget, QFileDialog, QFrame, QGridLayout, QIcon,
    QImage, QImageReader, QMenu,
    QImageWriter, QInputDialog, QKeySequence, QLabel, QListWidget,
    QMessageBox, QPainter, QPixmap, QPrintDialog, QPushButton,
    QPrinter, QSpinBox, QPen, QBrush, QFontMetrics, QSizePolicy,
    QMdiSubWindow, QTableWidget)

import PyQt4.Qwt5 as Qwt
from PyQt4.Qwt5.anynumpy import *

import aphla as ap

import time
import numpy as np
import sip

import applotresources

# sip has a bug affecting PyQwt
# http://blog.gmane.org/gmane.comp.graphics.qwt.python/month=20101001
if sip.SIP_VERSION_STR > '4.10.2':
    from scales import DateTimeScaleEngine


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
                msg += "  %s: %s<br>" % (v, str(elem.get(v, unit=None)))

        msgbox.setText(msg)
        msgbox.exec_()

        # emit with a list of element names
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



class ApPlotCurve(Qwt.QwtPlotCurve):
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
        #self.setStyle(kw.get('curveStyle', Qwt.QwtPlotCurve.Lines))
        self.setStyle(kw.get('curveStyle', Qwt.QwtPlotCurve.Sticks))
        self.setSymbol(kw.get('curveSymbol', Qwt.QwtSymbol()))
        self.errorPen = kw.get('errorPen', QPen(Qt.NoPen))
        self.errorCap = kw.get('errorCap', 0)
        self.errorOnTop = kw.get('errorOnTop', True)
        self.__live = False
        self.showDifference = False

    def setData(self, x, y, e):
        self.x1, self.y1, self.e1 = x, y, e
        Qwt.QwtPlotCurve.setData(self, list(self.x1), list(self.y1))
            
    def boundingRect(self):
        """
        Return the bounding rectangle of the data, error bars included.
        """
        if self.x1 is None or self.y1 is None:
            return Qwt.QwtPlotCurve.boundingRect(self)
        
        x, y, y2 = self.x1, self.y1, self.e1
        xmin, xmax = min(x), max(x)
        if y2 is None:
            ymin, ymax = min(y), max(y)
        else:
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


class ApPlot(Qwt.QwtPlot):
    def __init__(self, parent = None, lat = None,
                 live = True, errorbar = True, title=None): 
        
        super(ApPlot, self).__init__(parent)
        
        self.setCanvasBackground(Qt.white)
        self.errorOnTop = errorbar
        self.live = live
        self.setAutoReplot(False)

        self.plotLayout().setAlignCanvasToScales(True)

        self.curve1 = ApPlotCurve(
            curvePen = QPen(Qt.red, 3),
            curveSymbol = Qwt.QwtSymbol(
                Qwt.QwtSymbol.Ellipse,
                QBrush(Qt.red),
                QPen(Qt.black, 1),
                QSize(8, 8)),
            errorPen = QPen(Qt.black, 1),
            errorCap = 6,
            errorOnTop = self.errorOnTop,
            )

        self.curve1.attach(self)

        self.curve2 = Qwt.QwtPlotCurve()
        self.curve2.setPen(QPen(Qt.green, 5))
        self.curve2.attach(self)
        self.curve1.setZ(self.curve2.z() + 1.0)
        #self.curve2.setVisible(False)

        #print "PV golden:", pvs_golden
        pvs_golden = None
        if pvs_golden is None: self.golden = None
        else:
            #for pv in pvs_golden: print pv, caget(pv.encode("ascii"))
            self.golden = ApPlotCurve(
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

        self.setMinimumSize(500, 200)
        grid1 = Qwt.QwtPlotGrid()
        grid1.attach(self)
        grid1.setPen(QPen(Qt.black, 0, Qt.DotLine))

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
        #raise RuntimeError("what is this")
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

    def updatePlot(self):
        self.curve1.setData()
        if self.golden is not None: self.golden.update()
        #self.replot()

    def setErrorBar(self, on):
        self.curve1.errorOnTop = on
        #self.replot()

    def _scaleVertical(self, factor = 1.0/1.5):
        scalediv = self.axisScaleDiv(Qwt.QwtPlot.yLeft)
        sr, sl = scalediv.upperBound(), scalediv.lowerBound()
        dy = (sr - sl)*(factor - 1)/2.0
        
        #print "bound:",scalediv.lowerBound(), scalediv.upperBound()
        self.setAxisScale(Qwt.QwtPlot.yLeft, sl - dy, sr + dy)
        self.replot()

    def plotCurve2(self, y, x = None):
        """
        hide curve if x,y are both None
        """
        if y is None and x is None:
            self.curve2.detach()
            self.curve2.setVisible(False)
            #print "disabling desired orbit and quit"
            return

        if x is not None:
            self.curve2.setData(x, y)
            return
        data = self.curve2.data()
        vx = [data.x(i) for i in range(data.size())]
        self.curve2.setData(vx, y)

    def setColor(self, c):
        symb = self.curve1.symbol()
        pen = symb.pen()
        pen.setColor(c)
        symb.setPen(pen)
        br = symb.brush()
        br.setColor(c)
        symb.setBrush(br)
        self.curve1.setSymbol(symb)

        pen = self.curve1.pen()
        pen.setColor(c)
        self.curve1.setPen(pen)


class ApPlotControlButton(QPushButton):
    def __init__(self, parent = None, iconres = None, iconsize = 24,
                 action = None):
        super(ApPlotControlButton, self).__init__("")
        self.maxiconsize = 64
        #bt1 = QPushButton("")
        if iconres: self.setIcon(QIcon(iconres))
        self.setIconSize(QSize(iconsize, iconsize))
        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.setMinimumSize(16, 16)
        self.setMaximumSize(self.maxiconsize, self.maxiconsize)
        if action: self.connect(self, SIGNAL("clicked()"), action)
        self.setFixedSize(iconsize,iconsize)
        self.adjustSize()

class ApPlotWidget(QWidget):
    def __init__(self, parent = None, iconsize = 24, title=None):
        super(ApPlotWidget, self).__init__(parent)

        majbox = QGridLayout()

        icol = 0
        for icon,act in [(":/view_zoom_xy.png", self.zoomAuto),
                         (":/view_zoomin_y.png", self.zoomIn),
                         (":/view_zoomout_y.png", self.zoomOut),
                         (":/view_zoomin_x.png", self.zoom),
                         (":/view_zoomout_x.png", self.zoom),
                         (":/view_zoomin_y.png", self.zoom)]:
            bt = ApPlotControlButton(iconres=icon, iconsize=24, action = act)
            majbox.addWidget(bt, 0, icol)
            majbox.setColumnStretch(icol, 0)
            icol = icol + 1

        self.moreopt = QMenu("")
        a1 = QAction(QIcon(":/file_quit.png"), "&Quit", self)
        a1.setToolTip("Quit the application")
        a1.setStatusTip("Quit the application")
        a1.setCheckable(True)
        #fileQuitAction.setIcon(Qt.QIcon(":/filequit.png"))
        self.connect(a1, SIGNAL("toggled(bool)"), self.a1toggle)
        self.moreopt.addAction(a1)

        bt = QPushButton("More")
        bt.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        bt.setMenu(self.moreopt)
        majbox.addWidget(bt, 0, icol)
        majbox.setColumnStretch(icol, 0)
        icol += 1

        self.live = True
        self.aplot = ApPlot(self, live= self.live)
        self.aplot.plotLayout().setCanvasMargin(4)
        self.aplot.plotLayout().setAlignCanvasToScales(True)

        majbox.addWidget(self.aplot, 1, 0, 1, 10)

        self.title = QLabel()
        ncol = majbox.columnCount()
        majbox.addWidget(self.title, 0, ncol-1)
        if title: self.title.setText(title)
        #majbox.setColumnStretch(3, 1)
        self.setLayout(majbox)

    def setMagnetProfile(self, magnet_profile):
        self.aplot.setMagnetProfile(magnet_profile)

    def setMarkers(self, mks, on = True):
        self.aplot.setMarkers(mks, on)

    def setAxisTitle(self, axis, title):
        self.aplot.setAxisTitle(axis, title)

    def setAxisScale(self, axis, minv, maxv):
        self.aplot.setAxisScale(axis, minv, maxv)

    def detachCurves(self):
        self.aplot.curve1.attach(None)
        self.aplot.curve2.attach(None)
        if self.aplot.curvemag: self.aplot.curvemag.attach(None)
        
    def attachCurves(self):
        self.aplot.curve1.attach(self.aplot)
        self.aplot.curve2.attach(self.aplot)
        if self.aplot.curvemag: self.aplot.curvemag.attach(self.aplot)

    def zoomIn(self):
        self.aplot._scaleVertical(1.0/1.5)

    def zoomOut(self):
        self.aplot._scaleVertical(1.5/1.0)

    def zoomAuto(self):
        #self.aplot.replot()
        #print "Auto Zoom", self.title, self.aplot.zoomer1.zoomStack()
        bound = self.aplot.curve1.boundingRect()
        w = bound.width()
        h = bound.height()
        
        bound.adjust(0.0, -h*.1, 0.0, h*.1)
        #xmin = bound.left() - w*.03
        #xmax = bound.right() + w*.03
        ymin = bound.top() - h*.05
        ymax = bound.bottom() + h*.03
        xmin = bound.left()
        xmax = bound.right()
        #ymin = bound.top()
        #ymax = bound.bottom()
        #print "bound:", bound, w, h
        #print "x, y= ", xmin, xmax, ymin, ymax
        if w > 0.0: self.setAxisScale(Qwt.QwtPlot.xBottom, xmin, xmax)
        #else: self.setAxisAutoScale(Qwt.Qwt.Plot.xBottom)

        if h > 0.0: self.setAxisScale(Qwt.QwtPlot.yLeft, ymin, ymax)
        #else: self.setAxisAutoScale(Qwt.QwtPlot.yLeft)
        self.aplot.zoomer1.setZoomStack([bound])
        self.aplot.replot()
        #print "Auto Zoom", self.title
        #print "   base:", self.aplot.zoomer1.zoomBase()
        #print "   rect:", self.aplot.zoomer1.zoomRect()
        #print "   index:", self.aplot.zoomer1.zoomRectIndex()
        #print "   stack:", self.aplot.zoomer1.zoomStack()
        #print ""

    def a1toggle(self, v):
        print v

    def zoom(self):
        print "zoom"


class ApOrbitPlot(ApPlotWidget):
    def __init__(self, parent = None, title = None):
        super(ApOrbitPlot, self).__init__(parent, iconsize=24, title=title)
        

    def updatePlot(self, x, y, err = None):
        self.aplot.curve1.setData(x, y, err)
        #print "orbit updated"
        self.aplot.replot()
        #if self.aplot.live and self.zoomer1:
        #    self.zoomer1.setZoomBase(self.curve1.boundingRect())
        #print self.aplot.zoomer1.zoomStack()


class ApMdiSubPlot(QMdiSubWindow):
    def __init__(self, parent = None, data = None):
        super(ApMdiSubPlot, self).__init__(parent)
        self.wid = ApPlotWidget(parent)
        self.aplot = self.wid.aplot
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setWidget(self.wid)
        self.data = data
        self.err_only  = False
        self.connect(self.aplot, SIGNAL("elementSelected(PyQt_PyObject)"),
                     self.elementSelected)

    def updatePlot(self):
        #print "updating the data"
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
        try:
            #self.aplot.replot()
            pass
        except:
            print "ERROR"
        #print "done replot"

    def elementSelected(self, elem):
        eleminfo = [self.data.machine, self.data.lattice, elem]
        self.emit(SIGNAL("elementSelected(PyQt_PyObject)"), eleminfo)

    def currentXlim(self):
        """a tuple of (xmin, xmax)"""
        ax = self.aplot.axisScaleDiv(Qwt.QwtPlot.xBottom)
        return (ax.lowerBound(), ax.upperBound())

    def setMarkers(self, mks, on):
        self.aplot.setMarkers(mks, on)

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

    def plotCurve2(self, y, x = None):
        self.aplot.plotCurve2(y, x)
