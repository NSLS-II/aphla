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


class LatticeView(QAbstractItemView):

    def __init__(self, parent=None):
        QAbstractItemView.__init__(self)
#       QScrollArea.__init__(self)
        layout = QGridLayout(self.viewport())
#       xmax = self.model.elements[-1].se - self.model.elements[0].sb
        self.view = LatticeCanvas(self)
#       self.view.setMinimumSize(600,600)
        self.scene = QGraphicsScene() #-60, -60, 0, 120)
#       self.scene = QGraphicsScene(-320, -20, 640, 640)
#       backColor = QColor()
#       backColor.setRed(255)
#       back = QBrush(backColor)
#       back = QBrush(backColor)
        self.scene.setBackgroundBrush(Qt.black)
        self.view.setScene(self.scene)
        self.view.setContextMenuPolicy(Qt.ActionsContextMenu)

        layout.addWidget(self.view,0,0)
#       self.plot.setCanvasBackground(Qt.black)
        
#   def dataChanged(self,topLeft, bottomRight):
#       self.redraw()

#   def selectionChanged(self,selected, deselected):
#       self.draw_lattice()

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

    def drawLattice(self):
       
        elements = self.model().selectedElements

	ActualWidth = 600
	ActualHeight = 600
        startangle = 0
        totalAngle = 0

#testRect = QGraphicsRectItem(-100,-100,200,200)
#	testRect.setRect(QtCore.QRectF(0, -hght/2.0, wdth, hght))

#       testRect.setBrush(Qt.red)

#	self.scene.addItem(testRect)          
#       return
        for i,elem in enumerate(elements):
            if elem.family=="DIPOLE":
                  totalAngle = totalAngle + 6.0*np.pi/180.
                             
        angle = 0 
	bendangle = 0 

        x=0
        y=0
        prese=0

        for i, elem in enumerate(elements): 
            x += (elem.sb - prese)*np.cos(angle)
            y += (elem.sb - prese)*np.sin(angle)

            if elem.family == "DIPOLE":
		bendangle = 3.0*np.pi/180.0
                angle += bendangle
                bendangle = 3.0*np.pi/180.0
	    else:
		angle += bendangle
		bendangle = 0

	    if elem.length > 0.0001:
#               print "RectElem",elem.name
#               sys.exit()
		rect = RectElem(i,elem) # elem['Length'],mt, 
		self.scene.addItem(rect)          
		rect.setRotation(angle*180./np.pi)
		rect.translate(x, y)
	    x += elem.length*np.cos(angle)
	    y += elem.length*np.sin(angle)
            prese = elem.se

	rect = self.scene.sceneRect()
     	self.view.fitInView(rect.x()-25,rect.y()-25,rect.width()+50,rect.height()+50,1) #AspectRatioMode.KeepAspectRatio:1) #0,0,300,300,Qt.KeepAspectRatio)

# I could even attach it to the mouse scroll event :) 

class RectElem(QGraphicsRectItem):

    def __init__(self,i, elem, parent=None):
        QGraphicsPixmapItem.__init__(self, parent)
        self.id = i
        s=elem.se
#       self.name="%d %s"%(i,info['Name'])
        wdth = elem.length
        hght = 1.0
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)          # set move restriction rect for the item
        self.setRect(QRectF(0, -hght/2.0, wdth, hght))
        if elem.family=="DIPOLE":
            self.setBrush(Qt.blue)
        elif elem.family=="QUAD":
            self.setBrush(Qt.yellow)
        elif elem.family=="SEXT":
            self.setBrush(Qt.red)
        else:
                self.setBrush(Qt.white)
#       self.setToolTip(QString("Hi! My name is %s\nI'm at %f m"%(info['Name'].upper(),s)))
        if isinstance(elem.name,list):
            self.setToolTip(QString(' '.join(elem.name)))
        else:
            self.setToolTip(QString(elem.name))

# class HeaderViewFilter(QObject):
#     def __init__(self, parent, header, *args):
#         super(HeaderViewFilter, self).__init__(parent, *args)
#         self.header = header
#     def eventFilter(self, object, event):
#         if event.type() == QEvent.MouseMove:
#             logicalIndex = self.header.logicalIndexAt(event.pos())
#             # you could emit a signal here if you wanted

# class HeaderViewFilter(QObject):
# 
#     def __init__(self, parent=None): #, header, *args):
#         super(HeaderViewFilter, self).__init__(parent) #, *args)
   #     self.header = header
   # def eventFilter(self, object, event):
   #     if event.type() == QEvent.MouseMove:
   #         logicalIndex = self.header.logicalIndexAt(event.pos())

#     def eventFilter(self, object, event):
#         if event.type() == QEvent.HoverEvent:
#             print "Hover!" # do something useful



class LatticeCanvas(QGraphicsView):

    def __init__(self,mainWidget,parent=None):
        super(LatticeCanvas, self).__init__(parent)
        self.setDragMode(2)
        self.rubberBand = None
#       self.connect(self,SIGNAL("itemSelected"),mainWidget.itemSelected)
#       self.filter=HeaderViewFilter()
#       self.setMouseTracking(1)
#       self.installEventFilter(self.filter)


    def mousePressEvent(self,event):
	self.origin = event.pos()
	if self.rubberBand is None:
            self.rubberBand = QRubberBand(QRubberBand.Rectangle, self)
        self.rubberBand.setGeometry(QRect(self.origin, QSize()))
        self.rubberBand.show()


    def mouseMoveEvent(self,event):
 	self.rubberBand.setGeometry(QRect(self.origin, event.pos()).normalized())

    def mouseReleaseEvent(self, event):
	if event.pos() != self.origin:
	    self.rubberBand.setGeometry(QRect(self.origin, event.pos()).normalized())
	    self.rubberBand.hide()
	    qp1=self.mapToScene(self.origin)
	    qp2=self.mapToScene(event.pos())
      	    self.fitInView(min(qp1.x(),qp2.x()),min(qp1.y(),qp2.y()),abs(qp2.x()-qp1.x()),abs(qp2.y()-qp1.y()),1)
	else:
	    p = self.mapToScene(event.pos().x(), event.pos().y())
	    item= self.scene().itemAt(p);
	    if item is not None:
 	        self.emit(SIGNAL("itemSelected"),item.id)

    def mouseDoubleClickEvent(self, event):
	rect = self.scene().sceneRect()
     	self.fitInView(rect.x()-25,rect.y()-25,rect.width()+50,rect.height()+50,1) #AspectRatioMode.KeepAspectRatio:1) #0,0,300,300,Qt.KeepAspectRatio)


if __name__ == "__main__":
    constructModel()
