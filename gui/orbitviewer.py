#! /usr/bin/env python

"""

GUI application for orbit display

:author: Yoshiteru Hidaka
:license:

This application can ...

"""

import sys

USE_DEV_SRC = False
if USE_DEV_SRC:
    # Force Python to use your development modules,
    # instead of the modules already installed on the system.
    import os
    if os.environ.has_key('HLA_DEV_SRC'):
        dev_src_dir_path = os.environ['HLA_DEV_SRC']

        if dev_src_dir_path in sys.path:
            sys.path.remove(dev_src_dir_path)
        
        sys.path.insert(0, dev_src_dir_path)
            
    else:
        print 'Environment variable named "HLA_DEV_SRC" is not defined. Using default HLA.'

import operator
#import time
#import numpy as np

import cothread
from cothread.catools import caget

from PyQt4 import Qt
import PyQt4.Qwt5 as qwt

import hla
from hla.hlaGui import InteractivePlotWindow, PlotZoomer, PlotPanner, PlotDataCursor, PlotEditor
from Qt4Designer_files.ui_orbit_viewer import Ui_MainWindow

if not hla.machines._lat :
    hla.initNSLS2VSR()


########################################################################
class OrbitData(Qt.QObject):
    """
    Inheriting from QObject so that this object can emit signals
    """

    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        
        Qt.QObject.__init__(self)
        
        self.bpm = hla.getElements('BPM')
        self.s = [b.sb for b in self.bpm]
        
        pvrb_list_of_list = [b._field['x'].pvrb for b in self.bpm]
        self.pvrb_list_x = reduce(operator.add, pvrb_list_of_list)
        
        pvrb_list_of_list = [b._field['y'].pvrb for b in self.bpm]
        self.pvrb_list_y = reduce(operator.add, pvrb_list_of_list)
        
        self.updateBPMReading()
        
    #----------------------------------------------------------------------
    def updateBPMxReading(self):
        """"""
        
        self.bpmX = caget(self.pvrb_list_x)
    
    #----------------------------------------------------------------------
    def updateBPMyReading(self):
        """"""
        
        self.bpmY = caget(self.pvrb_list_y)

    #----------------------------------------------------------------------
    def updateBPMReading(self):
        """"""
        
        self.updateBPMxReading()
        self.updateBPMyReading()
        
        self.emit(Qt.SIGNAL('updatedBPMReading'))
        
        
    
########################################################################
class OrbitView(InteractivePlotWindow, Ui_MainWindow):
    """
    
    """

    #----------------------------------------------------------------------
    def __init__(self, data, parent = None):
        """Constructor"""
        
        InteractivePlotWindow.__init__(self)
        
        self.data = data
        self._parent = parent
        
        # Set up the user interface from Designer
        self.setupUi(self)
        
        self.statusBar().showMessage("test")
        
        self._initPlots()
        
        self._initZoomers()
        self._initPanners() # This function must be called after self._initZoomers().
        # Otherwise, the "panned" signal will not be connected to the zoomer's slot.
        #self._initDataCursors()
        #self._initPlotEditors()
        
                
    #----------------------------------------------------------------------
    def closeEvent(self, qCloseEvent):
        """"""
        
        pass
        
    
    #----------------------------------------------------------------------
    def parent(self):
        """"""
        
        return self._parent
    
    #----------------------------------------------------------------------
    def _initPlots(self):
        """"""

        # Initialize the plot canvas for horizontal orbit
        p = self.qwtPlot_x # for short-hand notation
        p.setCanvasBackground(Qt.Qt.white)
        p.setAxisTitle(qwt.QwtPlot.xBottom, 's [m]')
        p.setAxisTitle(qwt.QwtPlot.yLeft, 'Horizontal BPM [m]')
        p.setAxisAutoScale(qwt.QwtPlot.xBottom)
        p.setAxisAutoScale(qwt.QwtPlot.yLeft)
        p.setAutoReplot()
        #
        # Initialize the curve representing the horizontal orbit
        p.curve = qwt.QwtPlotCurve('Horizontal Orbit')
        p.curve.setPen( Qt.QPen(Qt.Qt.red,
                                5,
                                Qt.Qt.SolidLine) )
        p.curve.setStyle(qwt.QwtPlotCurve.Lines)
        p.curve.setSymbol(qwt.QwtSymbol(qwt.QwtSymbol.Ellipse,
                                       Qt.QBrush(Qt.Qt.green),
                                       Qt.QPen(Qt.Qt.black, 6),
                                       Qt.QSize(5,5)))
        p.curve.setData(self.data.s,
                        self.data.bpmX)
        p.curve.attach(p)
        #
        p.replot()
        
        
        # Initialize the plot canvas for vertical orbit
        p = self.qwtPlot_y # for short-hand notation
        p.setCanvasBackground(Qt.Qt.white)
        p.setAxisTitle(qwt.QwtPlot.xBottom, 's [m]')
        p.setAxisTitle(qwt.QwtPlot.yLeft, 'Vertical BPM [m]')
        p.setAxisAutoScale(qwt.QwtPlot.xBottom)
        p.setAxisAutoScale(qwt.QwtPlot.yLeft)
        p.setAutoReplot()
        #
        # Initialize the curve representing the vertical orbit
        p.curve = qwt.QwtPlotCurve('Vertical Orbit')
        p.curve.setPen( Qt.QPen(Qt.Qt.red,
                                5,
                                Qt.Qt.SolidLine) )
        p.curve.setStyle(qwt.QwtPlotCurve.Lines)
        p.curve.setSymbol(qwt.QwtSymbol(qwt.QwtSymbol.Ellipse,
                                       Qt.QBrush(Qt.Qt.green),
                                       Qt.QPen(Qt.Qt.black, 6),
                                       Qt.QSize(5,5)))
        p.curve.setData(self.data.s,
                        self.data.bpmY)
        p.curve.attach(p)
        #
        p.replot()


        
        self.plots = self.findChildren(qwt.QwtPlot)
        
    #----------------------------------------------------------------------
    def _initZoomers(self):
        """"""
        
        self.zoomers = {}
        
        
        for p in self.plots :
            zoomer = PlotZoomer(qwt.QwtPlot.xBottom,
                                qwt.QwtPlot.yLeft,
                                qwt.QwtPicker.DragSelection,
                                qwt.QwtPicker.AlwaysOff,
                                p.canvas())
            zoomer.setRubberBandPen(Qt.QPen(Qt.Qt.black))
            # MouseSelect1 = Zoom in to a user specified rectangle
            # --- No change necessary
            # MouseSelect2 = Zoom back to zoomBase
            # --- Change form the default "RightClick" action to "Ctrl+RightClick"
            zoomer.setMousePattern(qwt.QwtEventPattern.MouseSelect2,
                                   Qt.Qt.RightButton, Qt.Qt.ControlModifier)
            # MouseSelect3 = Zoom back to one previous zoom state
            # --- Change to "RightClick"
            zoomer.setMousePattern(qwt.QwtEventPattern.MouseSelect3,
                                   Qt.Qt.RightButton, Qt.Qt.NoButton)
        
            zoomer.resetZoomStack()
            zoomer.setEnabled(False)
            
            self.zoomers[str(p.objectName())] = zoomer
            
        
    
    #----------------------------------------------------------------------
    def _initPanners(self):
        """"""
        
        self.panners = {}
                
        for p in self.plots :
            panner = PlotPanner(p.canvas())
            
            panner.setEnabled(False)
            
            self.panners[str(p.objectName())] = panner
    
            
    #----------------------------------------------------------------------
    def _initDataCursors(self):
        """"""
        
        current_font = self.fontInfo().family()
        
        self.data_cursors = {}
        
        marker = qwt.QwtPlotMarker()
        marker.setValue(1,200)
        text = qwt.QwtText('test')
        text.setFont(Qt.QFont(current_font, 12, Qt.QFont.Bold))
        text.setColor(Qt.Qt.blue)
        text.setBackgroundBrush(Qt.QBrush(Qt.Qt.yellow))
        text.setBackgroundPen(Qt.QPen(Qt.Qt.red,2))
        marker.setLabel(text)
        marker.setSymbol(qwt.QwtSymbol(qwt.QwtSymbol.Ellipse, # Marker Type (None, Ellipse, Rect, Diamond)
                                       Qt.QBrush(Qt.Qt.green), # Fill Color (Use "Qt.QBrush()" if you want transparent)
                                       Qt.QPen(Qt.Qt.black, 6), # Edge Color & Edge Thickness (Use "Qt.QPen()" if you want transparent
                                       Qt.QSize(5,5))) # Marker Size (Horizontal Size, Vertical Size)
        marker.setVisible(False)
        marker.attach(self.qwtPlot)
        data_cursor = PlotDataCursor(marker,
                                     qwt.QwtPlot.xBottom,
                                     qwt.QwtPlot.yLeft,
                                     qwt.QwtPicker.PointSelection,
                                     qwt.QwtPlotPicker.NoRubberBand,
                                     qwt.QwtPicker.AlwaysOff,
                                     self.qwtPlot.canvas())
        data_cursor.setEnabled(False)
        
        self.data_cursors['qwtPlot'] = data_cursor
    
    #----------------------------------------------------------------------
    def _initPlotEditors(self):
        """"""
        
        self.plot_editors = {}
        
        selection_highlighter_curve = qwt.QwtPlotCurve('selection highlight')
        selection_highlighter_curve.setStyle(qwt.QwtPlotCurve.NoCurve) # Line Connection Type (Lines, NoCurve, Sticks, Steps)
        selection_highlighter_curve.setSymbol(qwt.QwtSymbol(qwt.QwtSymbol.Rect, # Marker Type (None, Ellipse, Rect, Diamond)
                                                            Qt.QBrush(Qt.Qt.white), # Fill Color (Use "Qt.QBrush()" if you want transparent)
                                                            Qt.QPen(Qt.Qt.black, 1), # Edge Color & Edge Thickness (Use "Qt.QPen()" if you want transparent
                                                            Qt.QSize(5,5))) # Marker Size (Horizontal Size, Vertical Size)
        selection_highlighter_curve.setVisible(False)
        selection_highlighter_curve.attach(self.qwtPlot)
        
        plot_editor = PlotEditor(selection_highlighter_curve,
                                 qwt.QwtPlot.xBottom,
                                 qwt.QwtPlot.yLeft,
                                 qwt.QwtPicker.PointSelection,
                                 qwt.QwtPlotPicker.NoRubberBand,
                                 qwt.QwtPicker.AlwaysOff,
                                 self.qwtPlot.canvas())
        
        plot_editor.setEnabled(False)

        self.plot_editors['qwtPlot'] = plot_editor
        
        
    #----------------------------------------------------------------------
    def slotDataUpdated(self):
        """"""
        
        new_value = self.data.current_array[self.data.current_array_index - 1]
        new_value = new_value.tolist()[0] # converting from NumPy array to a Python float
        
        self.label_current.setText('{:.3f}'.format(new_value))
        
    #----------------------------------------------------------------------
    def slotUpdatePlot(self, time_seconds, current_mA):
        """"""
        
        self.qwtPlot.curve.setData(time_seconds, current_mA)
        
        # Purpose of this section of code:
        #   As new data come in, the plot region increases naturally.
        #   However, if the zoomer is enabled while new data come in,
        #   the associated zoom base does not grow on its own. Since
        #   the zoomer does not allow expand larger than the zoom base,
        #   in order for a user to see the new data, the zoom base must
        #   be also re-adjusted. Since the user most likely will not
        #   appreciate the view to change while s/he is using a zoomer,
        #   if the zoomer is not at the zoom base, the zoom stack will
        #   not be reset when new data come in. However, if the zoom
        #   stack is at the base, then the zoom base will be reset to
        #   the current axis range automatically calculated by the
        #   plot widget.
        zoomer = self.zoomers["qwtPlot"]
        zoomStackIndex = zoomer.zoomRectIndex()
        if zoomStackIndex == 0 :
            zoomer.resetZoomStack()
        
        
        
    #----------------------------------------------------------------------
    def updateStatusBar(self, message_text):
        """"""

        self.statusBar().showMessage(message_text)
        
    
    #----------------------------------------------------------------------
    def updateOrbitView(self):
        """"""
        
        self.qwtPlot_x.curve.setData(self.data.s, self.data.bpmX)
        self.qwtPlot_y.curve.setData(self.data.s, self.data.bpmY)
        

    

########################################################################
class OrbitApp(Qt.QObject):
    """
    """

    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        
        Qt.QObject.__init__(self)
        
        # _initActions() (Other than standard actions, specify acitons very specific for this GUI)
        # _initToolBar()
        # _initMenuBar()
        # _initStatusBar()
        
        self._initData()
        self._initView()
        
        
    
    #----------------------------------------------------------------------
    def _initData(self):
        """"""
        
        self.data = OrbitData()
        
    
    #----------------------------------------------------------------------
    def _initView(self):
        """"""
        
        self.view = OrbitView(self.data, parent = self)
        
        self.connect(self.view.pushButton_update,
                     Qt.SIGNAL('clicked()'),
                     self.data.updateBPMReading)
        self.connect(self.data, Qt.SIGNAL('updatedBPMReading'),
                     self.view.updateOrbitView)        
        
        
#----------------------------------------------------------------------        
def make():
    
    app = OrbitApp()
    window = app.view
    window.show()
    return app

#----------------------------------------------------------------------
def main(args):
    
    # If Qt is to be used (for any GUI) then the cothread library needs to be informed,
    # before any work is done with Qt. Without this line below, the GUI window will not
    # show up and freeze the program.
    qtapp = cothread.iqt()
    
    '''
    app = CurrentMonitorApp()
    window = app.view
    window.show()
    '''
    app = make()
    
    cothread.WaitForQuit()
    
    
if __name__ == "__main__":
    
    main(sys.argv)
    