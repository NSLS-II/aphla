import sys 
import os
# from PyQt4 import Qt
# from PyQt4 import QtGui, QtCore  
# import PyQt4.Qt as Qt
import PyQt4.Qwt5 as Qwt
# from PyQt4.Qt import *
# from PyQt4.Qwt5 import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import numpy as np

__version__="0.0.1"

NAME, LENGTH, START, END, ONOFF = range(5) #SETVAL, GETVAL, ONOFF, STATUS, MSSGE = range(8)
# Normal, Hovered, Pressed = range(3)
Normal, Pressed = range(2)

Qt.aqua = QColor(qRgb(0,255,255))

class TwissView(QAbstractItemView):

    def __init__(self, plane=0, parent=None):
        QAbstractItemView.__init__(self)
        layout = QGridLayout(self.viewport())
#       xmax = self.model.elements[-1].se - self.model.elements[0].sb
        self.plane = plane
        self.ymax = 40.0
        self.ymin = 0.0
        self.plot = Hplot(self)
        layout.addWidget(self.plot,0,0)
#       self.plot.setCanvasBackground(Qt.black)

        
    def dataChanged(self,topLeft, bottomRight):
        self.y = [self.model().cell[i].Beta[self.plane] for i in range(self.model().globval.Cell_nLoc)] # arange(0.0, 100.1, 0.5)
        self.betaxLine.setData(self.x, self.y)

    def selectionChanged(self,selected, deselected):
        # QwtPlotCurve.setPen, setBrush do not work because we customized the class
        if len(deselected.indexes()) > 0:
              self.rects[deselected.indexes()[0].row()].setPen(QPen(Qt.aqua,2))
              self.rects[deselected.indexes()[0].row()].setBrush(QBrush(Qt.aqua))
        self.rects[selected.indexes()[0].row()].setPen(QPen(Qt.red,2))
        self.rects[selected.indexes()[0].row()].setBrush(QBrush(Qt.red))
        self.plot.replot()

    def horizontalOffset(self):
        return 0

    def verticalOffset(self):
        return 0

    def moveCursor(self, cursorAction, modifiers):
        return self.currentIndex()

    def visualRect(self, index):
        return self.rect()

    def indexAt(self, point):
        return QModelIndex()

    def scrollTo(self,index,hint=QAbstractItemView.EnsureVisible):
        return

    def changeRange(self,i1, i2):
        xmin = self.model().selectedElements[i1].sb - 1
        xmax = self.model().selectedElements[i2].se + 1
        self.plot.setAxisScale(Qwt.QwtPlot.xBottom, xmin, xmax )
        self.plot.replot()
        
    def draw_lattice(self):

        # axes

        selected = self.currentIndex().row()
#       try:
#           rowNum = len(self.rects)
#           for row in range(rowNum):
#               if row == selected:
#                   color = Qt.red
#               else:
#                   color=QColor(qRgb(0,0,255))
##              b = QBrush(color)
##              b.setStyle(Qt.SolidPattern)
#               self.rects[row].penColor=color
#               self.rects[row].brushColor=color
#               self.rects[row].setPen(QPen(color))
#       except:
        rowNum = self.model().rowCount()

        eles = self.model().selectedElements
        self.rects=rowNum*[None]
        for row,ele in enumerate(eles):
#           length = self.model().data(self.model().index(row,elements.LENGTH))
#           family = self.model().data(self.model().index(row,elements.FAMILY)) #Qt.userRole
#           if family == elements.pytracy.globval.vcorr:
#                   continue
            if ele.length>0:
                self.rects[row] = LatticeElems(self)
            else:
                self.rects[row] = Qwt.QwtPlotCurve()
                self.rects[row].setPen(QPen(Qt.aqua))
            self.rects[row].attach(self.plot)
            try:
                self.rects[row].setData([ele.sb, ele.se],[self.ymin,self.ymin+(self.ymax-self.ymin)/10])
            except:
                print rowNum,ele.sb,ele.se

        self.clearZoomStack()

    def drawTwiss(self):
        elemenets = self.model().selectedElements
        cell = self.model().cell
        globval = self.model().globval
#       print globval.Cell_nLoc
        self.x = [cell[i].S for i in range(globval.Cell_nLoc)] # arange(0.0, 100.1, 0.5)
        self.y = [cell[i].Beta[self.plane] for i in range(globval.Cell_nLoc)] # arange(0.0, 100.1, 0.5)
#       self.y = len(self.x)*[0] # zeros(len(self.x), Float)
#       self.z = zeros(len(self.x), Float)

#       self.setTitle("A Moving QwtPlot Demonstration")
#       self.insertLegend(Qwt.QwtLegend(), Qwt.QwtPlot.BottomLegend);

        self.betaxLine = Qwt.QwtPlotCurve("Beta")
        self.betaxLine.setPen(QPen(Qt.white))
        self.betaxLine.attach(self.plot)
#       self.curveL = Qwt.QwtPlotCurve("Data Moving Left")
#       self.curveL.attach(self)
        self.betaxLine.setData(self.x, self.y)
#       self.curveL.setData(self.x, self.z)

#       self.replot()


#       bpms = hla.getGroupMembers('BPM')
#       pvs = bpms[0].pv()
#       try:
#           pv1 = hla.catools.caget(pvs[0])
#           pv2 = hla.catools.caget(pvs[1])
#       except hla.catools.Timedout, message:
#           pv1 = 0
#           pv2 = 0 
                
                    
    def clearZoomStack(self):
        """Auto scale and clear the zoom stack
        """
            
#       self.plot.setAxisAutoScale(Qwt.QwtPlot.xBotto
#       self.plot.setAxisAutoScale(Qwt.QwtPlot.yLeft)
        self.plot.replot()
#       self.zoomer.setZoomBase()

class LatticeElems(Qwt.QwtPlotCurve):

    def __init__(self, penColor=Qt.black, brushColor=Qt.white):
        Qwt.QwtPlotCurve.__init__(self)
        self.setPen(QPen(Qt.aqua,2))
        self.setBrush(QBrush(Qt.aqua))

    def drawFromTo(self, painter, xMap, yMap, start, stop):
        """Draws rectangles with the corners taken from the x-arrays.
        """

        painter.setPen(self.pen())
        painter.setBrush(self.brush())
        if stop == -1:
            stop = self.dataSize()
        if start & 1:
            start -= 1
        if stop & 1:
            stop -= 1
        start = max(start, 0)
        for i in range(start, stop, 2):
            px1 = xMap.transform(self.x(i))
            py1 = yMap.transform(self.y(i))
            px2 = xMap.transform(self.x(i+1))
            py2 = yMap.transform(self.y(i+1))
            painter.drawRect(px1, py1, (px2 - px1), (py2-py1))

class Hplot(Qwt.QwtPlot):

    def __init__(self, parent=None):
        Qwt.QwtPlot.__init__(self, parent)
        self.setMargin(10)
        self.plane = parent.plane
#plot->plotLayout()->setAlignCanvasToScales( true );
#plot->canvas()->setLineWidth( 0 );
#for ( int axis = 0; axis < QwtPlot::axisCnt; axis++ )
#{    plot->axisWidget( axis )->setMargin( 0 );    
#plot->axisScaleDraw( axis )->enableComponent(        QwtAbstractScaleDraw::Backbone, false );}

#   def __init__(self, model, parent=None):
#       Qwt.QwtPlot.__init__(self, parent)
        self.setCanvasBackground(Qt.black)
#       p = self.canvas().palette();

#       for i in range(QPalette.NColorGroups):
#   {
#if QT_VERSION < 0x040000
#       p.setColor((QPalette::ColorGroup)i, QColorGroup::Background, c);
#else
#           p.setColor(i, QPalette.Background, Qt.black);
#endif
#   }


        xmax = 700
        self.ymax = parent.ymax
        self.ymin = parent.ymin
        title = self.title()
        title.setColor(QColor(qRgb(200,200,200)))
        if self.plane == 0:
            title.setText('Horizontal Beta Function')
        else:
            title.setText('Vertical Beta Function')
        self.setTitle(title)

        # legend
#       legend = Qwt.QwtLegend()
#       legend.setFrameStyle(QFrame.Box | QFrame.Sunken)
#       legend.setItemMode(Qwt.QwtLegend.ClickableItem)
#       self.insertLegend(legend, Qwt.QwtPlot.BottomLegend)

        # grid
        self.grid = Qwt.QwtPlotGrid()
        self.grid.enableXMin(True)
        self.grid.setMajPen(QPen(Qt.white, 0, Qt.DotLine))
        self.grid.setMinPen(QPen(Qt.gray, 0 , Qt.DotLine))
        self.grid.attach(self)


        self.setAxisMaxMajor(Qwt.QwtPlot.xBottom, 6)
        self.setAxisMaxMinor(Qwt.QwtPlot.xBottom, 10)
        # self.setAxisScaleEngine(Qwt.QwtPlot.xBottom, QwtLog10ScaleEngine())

        qwtsw = self.axisWidget(Qwt.QwtPlot.xBottom)
        palette = qwtsw.palette()
        palette.setColor(QPalette.Text,  QColor(qRgb(210,210,210)))
        qwtsw.setPalette(palette)
        self.axisWidget(Qwt.QwtPlot.yLeft).setPalette(palette)

        # self.enableAxis(Qwt.QwtPlot.yRight)
        titlex = self.axisTitle(Qwt.QwtPlot.xBottom)
        titley = self.axisTitle(Qwt.QwtPlot.yLeft)
        titlex.setColor( QColor(qRgb(200,200,200)))
        titley.setColor( QColor(qRgb(200,200,200)))
        titlex.setText("Position (m)")
        self.setAxisScale(Qwt.QwtPlot.xBottom, 0, xmax )
        if self.plane == 0:
            titley.setText(u'\u03b2<sub>x</sub> (m)')
#           self.setAxisTitle(Qwt.QwtPlot.yLeft, 'x (mm)')    # mu: u'\u03bc
        else:
            titley.setText(u'\u03b2<sub>y</sub> (m)')
#           self.setAxisTitle(Qwt.QwtPlot.yLeft, 'y (mm)')    # mu: u'\u03bc
        self.setAxisTitle(Qwt.QwtPlot.yLeft,titley)
        self.setAxisTitle(Qwt.QwtPlot.xBottom,titlex)
        self.setAxisScale(Qwt.QwtPlot.yLeft, self.ymin, self.ymax)
#       self.setAxisTitle(Qwt.QwtPlot.yRight, u' ') # Phase [\u00b0]')

        # self.enableAxis(Qwt.QwtPlot.yRight)
#       self.setAxisTitle(Qwt.QwtPlot.xBottom, u'\u03c9/\u03c9<sub>0</sub>')
#       self.setAxisScale(Qwt.QwtPlot.xBottom, 0, xmax )
#       self.setAxisTitle(Qwt.QwtPlot.yLeft, 'Position ['+u'\u03c9'+'m]')
#       self.setAxisScale(Qwt.QwtPlot.yLeft, 0, 20)
#       self.setAxisTitle(Qwt.QwtPlot.yRight, u' ') # Phase [\u00b0]')



        # alias

#   def setDamp(self, d):
#       self.damping = d
#       # Numerical Python: f, g, a and p are NumPy arrays!
#       # g=hla.getGroups()
#       hcors = hla.getGroupMembers('HCOR')
#       hcordics = []
#       for e in hcors:
#           hcor = dict()
#           hcor.name = e.name
#           hcor.getval= hla.catools.caget(e.pv()[0])
#           hcor.getset= hla.catools.caget(e.pv()[1])
#           hcor.putset = hcor.getset
#       #   hcor.onoff = hla.catools.caget()
#           hcor.onoff = False
#           hcor.status = True
#           hcor.mssge = ""
#           hcordics.append(hcor)




if __name__ == "__main__":
    constructModel()
