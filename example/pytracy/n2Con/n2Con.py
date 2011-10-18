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
import hla
# import pytracy as pt
import numpy as np
import elements
import orbitView
import twissView
import latticeView

__version__="0.0.1"

class MainForm(QDialog):

    def __init__(self, parent=None):         
	super(MainForm, self).__init__(parent)          
  	self.setGeometry(0,0,1000,600)
        self.oldsize = QSize(1000,600)
        self.oldflags = 0
        self.pos = 0
        self.fullSize = False
          # self.HorizontalScrollbarPolicy = 1
          # self.VerticalScrollbarPolicy = 1
        self.model = elements.ElementsModel("SR-txt")
#       self.centralwidget = QWidget(self)
        self.VLayout = QVBoxLayout(self)
        self.upper=QWidget(self)
        self.upperL = QWidget(self)
        self.hLayout = QHBoxLayout(self.upper)
        self.stackedlayout = QStackedLayout(self.upperL)
        self.stack1 = QWidget(self)
        self.stack2 = QWidget(self)
        self.stack3 = QWidget(self)
        self.vlaystack1 = QVBoxLayout(self.stack1)
        self.orbitView1= orbitView.OrbitView(0,self.stack1)
        self.orbitView2= orbitView.OrbitView(1,self.stack1)
        self.vlaystack1.addWidget(self.orbitView1)
        self.vlaystack1.addWidget(self.orbitView2)
#       self.stack1.setLayout(self.vlaystack1)
        self.stackedlayout.addWidget(self.stack1)
        vlaystack2 = QVBoxLayout(self.stack2)
        self.twissView1 = twissView.TwissView(0,self.stack2)
        self.twissView2 = twissView.TwissView(1,self.stack2)
        vlaystack2.addWidget(self.twissView1)
        vlaystack2.addWidget(self.twissView2)
        self.stackedlayout.addWidget(self.stack2)
# Stack 2: Lattice View
        self.stack3Grid = QGridLayout(self.stack3)
        self.latticeView = latticeView.LatticeView(self.upper)
        self.stack3Grid.addWidget(self.latticeView,0,0)
        self.stackedlayout.addWidget(self.stack3)
        self.tableView = QTableView()
        self.tableView.setModel(self.model)
#       self.hLayout.addLayout(self.stackedlayout,100)
        self.hLayout.addWidget(self.upperL)
        self.hLayout.addWidget(self.tableView)
        self.buttonLayout = QHBoxLayout()
        self.orbitButton = QPushButton("&Orbit")
        self.twissButton = QPushButton("&Twiss")
        self.latticeButton = QPushButton("&Lattice")
        self.correctorButton = QPushButton("&Corrector")
        self.detailButton = QPushButton("&Detail")
        self.quitButton = QPushButton("&Quit")
        self.buttonLayout.addWidget(self.orbitButton)
        self.buttonLayout.addWidget(self.twissButton)
        self.buttonLayout.addWidget(self.latticeButton)
        self.buttonLayout.addWidget(self.correctorButton)
        self.buttonLayout.addWidget(self.detailButton)
        self.buttonLayout.addWidget(self.quitButton)
        self.VLayout.addWidget(self.upper)
        self.VLayout.addLayout(self.buttonLayout)
#       self.centralwidget(self.VLayout)
        self.tableView.verticalHeader().hide()
        self.tableView.horizontalHeader().setBackgroundRole(QPalette.NoRole)
        self.tableView.resizeRowsToContents(); # Adjust the row height.     
        self.tableView.resizeColumnsToContents(); # Adjust the row height.     
        rowheight = self.tableView.rowHeight(0)
        for n, ele in enumerate(self.model.selectedElements):
           if ele.family == "SQUADnCOR":
               self.tableView.setRowHeight(n,3*rowheight)
           if ele.family == "FCOR" or ele.family == "COR02" or ele.family == "COR03":
               self.tableView.setRowHeight(n,2*rowheight)
        # tableView->setColumnWidth( 0, 45 );     
#       self.tableView.setColumnWidth( 1, 20 ); 
        # tableView->setFixedHeight(int)
#       self.tableView.setFixedWidth(300)




        self.orbitView1.setModel(self.model)
        self.orbitView2.setModel(self.model)
        self.twissView1.setModel(self.model)
        self.twissView2.setModel(self.model)
        self.latticeView.setModel(self.model)
        self.delegate = elements.ElementsDelegate(self)
        self.tableView.setItemDelegate(self.delegate)
        self.tableView.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tableView.setSelectionMode(QAbstractItemView.SingleSelection)
        self.orbitView1.setSelectionModel(self.tableView.selectionModel())
        self.orbitView2.setSelectionModel(self.tableView.selectionModel())
        self.twissView1.setSelectionModel(self.tableView.selectionModel())
        self.twissView2.setSelectionModel(self.tableView.selectionModel())
        self.latticeView.setSelectionModel(self.tableView.selectionModel())
#       self.setCentralWidget(self.centralwidget)
        self.orbitView1.drawOrbit()
        self.orbitView2.drawOrbit()
        self.orbitView1.draw_lattice()
        self.orbitView2.draw_lattice()
        self.twissView1.drawTwiss()
        self.twissView2.drawTwiss()
        self.twissView1.draw_lattice()
        self.twissView2.draw_lattice()
        self.latticeView.drawLattice()
#       print self.tableView.viewport().width()
        self.connect(self.quitButton, SIGNAL("clicked()"), self, SLOT("close()"))

        self.connect(self.orbitButton, SIGNAL("clicked()"), self.showOrbit)
        self.connect(self.twissButton, SIGNAL("clicked()"), self.showTwiss)
        self.connect(self.latticeButton, SIGNAL("clicked()"), self.showLattice)

        self.connect(self.tableView.verticalScrollBar(), SIGNAL("valueChanged(int)"), self.printChanged)
        self.connect(self.delegate,SIGNAL("needsUpdate"),self.tableView,SLOT("update"))

#       self.tableView.verticalScrollBar().emit(SIGNAL("valueChanged(int)"),self.pos)

#       fileNewAction = QAction(QIcon("images/filenew.png"), "&New", self)
#       modeChangeAction = QAction(QIcon(""), "&SizeMode", self)
#       modeChangeAction.setShortcut(QKeySequence.New)
#       modeChangeAction.setShortcut("Ctrl+m")
#       helpText = "Create a new image"
#       fileNewAction.setToolTip(helpText)
#       fileNewAction.setStatusTip(helpText)
#       self.connect(modeChangeAction, SIGNAL("triggered()"), self.modeChange)

#   def modeChange(self):
#       if self.fullSize:
#           self.show()
#           print self.fullSize
#           self.fullSize = False
#       else:
#           self.showFullScreen()
#           print self.fullSize
#           self.fullSize = True

    def showOrbit(self):
        self.stackedlayout.setCurrentWidget(self.stack1)

    def showTwiss(self):
        self.stackedlayout.setCurrentWidget(self.stack2)

    def showLattice(self):
        self.stackedlayout.setCurrentWidget(self.stack3)

    def resizeEvent(self,event):
        QDialog.resizeEvent(self,event)
        self.tableView.verticalScrollBar().emit(SIGNAL("valueChanged(int)"),self.pos)

# http://lists.trolltech.com/qt-interest/1999-11/msg00022.html
    def keyPressEvent(self,event):
        if event.key() == Qt.Key_F:
            if self.fullSize:
#               self.reparent( 0, 0,        QPoint(0,0), True );
                self.setWindowFlags( self.oldflags)
                self.resize(self.oldsize)
                self.show()
                self.tableView.verticalScrollBar().emit(SIGNAL("valueChanged(int)"),self.pos)
                self.fullSize = False
            else:
                self.oldsize = self.size()
                self.oldflags = self.windowFlags()
                self.setWindowFlags( Qt.FramelessWindowHint)
#               self.reparent( 0, WStyle_Customize | WStyle_NoBorder | WType_Popup, QPoint( 0, 0 ), False ) 
                self.resize(QApplication.desktop().size())
                self.tableView.verticalScrollBar().emit(SIGNAL("valueChanged(int)"),self.pos)
                self.show()
                self.fullSize = True
        QDialog.keyPressEvent(self,event)

        
# rapidGUI page 482
    def printChanged(self,inn):
        self.pos = inn
        fm = QFontMetrics(self.tableView.font())
        vv=self.tableView.viewport()
        offset=self.tableView.horizontalHeader().size().height()
        rowheight = self.tableView.rowHeight(0)
#       print "scrol",inn, "viewPort",vv.height(),"headerheight",offset,"rowheight",rowheight, vv.height()//rowheight
        self.orbitView1.changeRange(inn, inn+self.tableView.viewport().height()//self.tableView.rowHeight(0))
        self.orbitView2.changeRange(inn, inn+self.tableView.viewport().height()//self.tableView.rowHeight(0))
        self.twissView1.changeRange(inn, inn+self.tableView.viewport().height()//self.tableView.rowHeight(0))
        self.twissView2.changeRange(inn, inn+self.tableView.viewport().height()//self.tableView.rowHeight(0))

#  File "/home/jchoi/injector/orbitView.py", line 62, in changeRange
#    xmax = self.model().selectedElements[i2].se + 1
#IndexError: list index out of range
#NotImplementedError: QAbstractItemView.visualRegionForSelection() is abstract and must be overridden



def main():     
    app = QApplication(sys.argv)     
    # hla.machines.initNSLS2VSRTxt()
    # hla.initNSLS2VSRTwiss()
    # pt.Read_Lattice('CD3-June20-tracy')
    # pt.Ring_GetTwiss(True,0)
#   form.setAttribute(Qt.WStyle_NoBorder ) # Qt.WStyle_Customize | Qt.WStyle_NoBorder )



#   form.setAttribute(Qt.WA_DeleteOnClose)
#   form.tableView.setColumnWidth( 4, 30 ); 
#   print form.tableView.viewport().width()
# http://stackoverflow.com/questions/1524474/qt-hide-the-title-bar-of-a-dialog-window
# QApplication app(argc, argv);      QPixmap pixmap(":/splash.png");      QSplashScreen splash(pixmap);      splash.show();      app.processEvents();      ...      QMainWindow window;      window.show();      splash.finish(&window); 
# http://doc.trolltech.com/4.5/qwidget.html#windowFlags-prop
    pixmap = QPixmap("n2Splash.png")
    splash = QSplashScreen(pixmap)
    splash.show()
    form = MainForm()     
    form.tableView.setHorizontalScrollBarPolicy(1)
    form.tableView.resizeColumnsToContents(); # Adjust the column width.      
    form.tableView.setFixedWidth(330)
    form.show()     
    splash.finish(form)
#   form.showFullScreen()     
    app.setStyleSheet("QWidget {background:black; border-width: 1px; border-color:navy}"
                      "QTableView {border: 2px; border-radius 2px; color:white; gridline-color:purple}"
                      "QwtPlotCanvas {border: 2px; border-radius 2px; background:darkgreen}"
#                     "QPushButton {border: 2px solid #8f8f91; border-radius: 6px; "
#                     "             background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #f6f7fa, stop: 1 #dadbde); min-width: 80px;}"
                      "QPushButton {color: white;"
                      " background-color: QLinearGradient( x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #88d, stop: 0.1 #99e, stop: 0.49 #77c, stop: 0.5 #66b, stop: 1 #77c);"
                                   "border-width: 1px; border-color: #339; border-style: solid; border-radius: 7; padding: 3px; font-size: 10px; padding-left: 5px;"
                                   "padding-right: 5px; min-width: 50px; max-width: 50px; min-height: 13px; max-height: 13px; }"
                      "QPushButton:pressed {background-color: red}"
                      # "QPushButton:pressed {background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #dadbde, stop: 1 #f6f7fa);}"
                      "QPushButton:flat {border: none;}" # /* no border for a flat push button */
                      "QPushButton:default { border-color: navy;}" # /* make the default button prominent */
                      "QPushButton:checked { color: red; background-color: red;}" # /* make the default button prominent */
                      "QHeader:section { spacing: 10px; background-color:lightblue; color: blue; border: 1px solid red; margin: 1px; text-align: right;"
                                 "font-family: arial; font-size:12px;}"
                      "QDoubleSpinBox { background-color: white; padding:0px;padding-right: 0px; border-width: 0px;padding-left:0px;padding-top:0px;margin: 0px;border-width:0px}") # make room for the arrows */
#    border-image: url(:/images/frame.png) 4;
#                     ":section:first { spacing: 10px; background-color:lightblue; color: blue; border: 1px solid red; margin: 1px; text-align: right;"

    app.exec_()  

if __name__ == '__main__':     
    main() 


# try with a QItemSelectionModel:


# fileSelectionModel = QtGui.QItemSelectionModel(itemModel, tableView)

# tableView.setSelectionModel(fileSelectionModel)

# self.connect(fileSelectionModel, SIGNAL(

# "currentChanged(const QModelIndex &, const QModelIndex &)"),

# self.cellSelected)

# self.connect(fileSelectionModel, SIGNAL(

# "selectionChanged(const QItemSelection &, const QItemSelection &)"),

# self.updateSelection)

