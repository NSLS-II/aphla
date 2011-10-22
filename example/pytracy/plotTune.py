#! /etc/bin/env python

import sys

from PyQt4 import Qt
import PyQt4.Qwt5 as Qwt
from PyQt4.Qwt5.anynumpy import *

from PyQt4 import QtCore
from PyQt4 import QtGui

import math


class TunePlot(Qwt.QwtPlot):

    def __init__(self,hrange,vrange,order,period, *args):
        Qwt.QwtPlot.__init__(self, *args)
        # set plot title
        self.setTitle('TunePlot')
        # set plot layout
        self.plotLayout().setMargin(0)
        self.plotLayout().setCanvasMargin(0)
        self.plotLayout().setAlignCanvasToScales(True)
        # set legend
      #  legend = Qwt.QwtLegend()
      #  legend.setItemMode(Qwt.QwtLegend.ClickableItem)
      #  self.insertLegend(legend, Qwt.QwtPlot.RightLegend)
      # set axis titles
        self.setAxisTitle(Qwt.QwtPlot.xBottom, u'\u03BD<sub>x</sub>')
        self.setAxisTitle(Qwt.QwtPlot.yLeft, u'\u03BD<sub>y</sub>')
	lines = self.getLines(hrange, vrange, order, period)
      # attach a curve
 	for line in lines:
            curve = Qwt.QwtPlotCurve('')
            curve.attach(self)
            curve.setPen(Qt.QPen(Qt.Qt.green, 2))
            curve.setData(line[0], line[1] )

	self.replot()




    def getLines(self,hrange, vrange, orders, period):

	alllines=[]
	for r in orders:
	   for m in range(r+1):
	
		n=r-m;

	        p1=int(math.ceil(m*hrange[0]+n*vrange[0]))
		p2=int(math.floor(m*hrange[1]+n*vrange[0]))
		for p in range(p1, p2+1):
		    if m!=0:
			alllines.append([math.fabs(m)+math.fabs(n),m,n,p,(p-n*vrange[0])/double(m),vrange[0]])

		p1=int(math.ceil(m*hrange[0] +n*vrange[0]))
		p2=int(math.floor(m*hrange[0] +n*vrange[1]))
		for p in range(p1, p2+1):
		    if n!=0:
			alllines.append([math.fabs(m)+math.fabs(n),m,n,p,hrange[0] ,(p-m*hrange[0] )/double(n)])

		p1=int(math.ceil(m*hrange[0] +n*vrange[1]))
		p2=int(math.floor(m*hrange[1] +n*vrange[1]))
		for p in range(p1, p2+1):
		    if m!=0:
			alllines.append([math.fabs(m)+math.fabs(n),m,n,p,(p-n*vrange[1] )/double(m),vrange[1]])

		p1=int(math.ceil(m*hrange[1] +n*vrange[0]))
		p2=int(math.floor(m*hrange[1] +n*vrange[1]))
		for p in range(p1, p2+1):
		    if n!=0:
			alllines.append([math.fabs(m)+math.fabs(n),m,n,p,hrange[1] ,(p-m*hrange[1] )/double(n)])
	
		n=-r+m;

		p1=int(math.ceil(m*hrange[0] +n*vrange[0]))
		p2=int(math.floor(m*hrange[1] +n*vrange[0]))
		for p in range(p1, p2+1):
		    if m!=0:
			alllines.append([math.fabs(m)+math.fabs(n),m,n,p,(p-n*vrange[0] )/double(m),vrange[0]])

		p1=int(math.ceil(m*hrange[0] +n*vrange[0]))
		p2=int(math.floor(m*hrange[0] +n*vrange[1]))
		for p in range(p2, p1+1):
		    if n!=0:
			alllines.append([math.fabs(m)+math.fabs(n),m,n,p,hrange[0] ,(p-m*hrange[0] )/double(n)])

		p1=int(math.ceil(m*hrange[0] +n*vrange[1]))
		p2=int(math.floor(m*hrange[1] +n*vrange[1]))
		for p in range(p1, p2+1):
		    if m!=0:
			alllines.append([math.fabs(m)+math.fabs(n),m,n,p,(p-n*vrange[1] )/double(m),vrange[1]])

		p1=int(math.ceil(m*hrange[1] +n*vrange[0]))
		p2=int(math.floor(m*hrange[1] +n*vrange[1]))
		for p in range(p2, p1+1):
		    if n!=0:
			alllines.append([math.fabs(m)+math.fabs(n),m,n,p,hrange[1],(p-m*hrange[1])/double(n)])

#	if alllines:
	alllines.sort()
        last = alllines[-1]
        for i in range(len(alllines)-2, -1, -1):
            if last == alllines[i]:
                del alllines[i]
            else:
                last = alllines[i]

#	unique = set(alllines)  # (*find unique elements and numbers*)

	temp=[line[:4] for line in alllines]
#	temp=alllines[:,:4] # extract the resonance properties:sameline*)
#	tallied2=set(temp) #(*extract only same lines*)
	ret=[] 

	done = False

	for t4 in temp:
	    if temp.count(t4) == 2:
		if done:
		    done=False
	        else:
                    done=True
	            X1=alllines[temp.index(t4)][4]
	            X2=alllines[temp.index(t4)+1][4]
	            Y1=alllines[temp.index(t4)][5]
	            Y2=alllines[temp.index(t4)+1][5]
#		    if ((X1==X2) and (X1==hrange[0] or X1==hrange[1])) or \
#		       ((Y1==Y2) and (Y1==hrange[0] or Y1==hrange[1])):
#	               pass
#		    else:
		    ret.append([[X1,X2],[Y1,Y2]])
	return(ret)



class Loco(QtGui.QDialog):
    def __init__(self, parent=None):
        super(Loco,self).__init__(parent)
	tuneplot = TunePlot([14,15],[8,9],[3],1)
        layout = QtGui.QVBoxLayout()
        Button1 = QtGui.QPushButton("&Quit")
        layout.addWidget(tuneplot)
        layout.addWidget(Button1)
        self.setLayout(layout)

        self.connect(Button1, QtCore.SIGNAL("clicked()"), self.close)

if __name__ == "__main__":
    import sys

    app = Qt.QApplication(sys.argv)
    form = Loco()
    form.resize(300,300)
#   form.connect(form, SIGNAL("find"), find)
#   form.connect(form, SIGNAL("replace"), replace)
    form.show()
    app.exec_()
