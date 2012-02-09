#! /usr/bin/env python

"""

GUI application for Current Monitoring

:author: Yoshiteru Hidaka
:license:

This application can start monitoring the beam current. It plots the beam current
history since the monitor start, and automatically updates the plot as new data
come in.

"""

import sys
import time
import numpy as np

import cothread
from cothread.catools import camonitor, FORMAT_TIME

from PyQt4 import Qt
import PyQt4.Qwt5 as qwt

from hlaGui import InteractivePlotWindow, PlotZoomer, PlotPanner, PlotDataCursor, PlotEditor
from Qt4Designer_files.ui_current_monitor import Ui_MainWindow


########################################################################
class CurrentMonitorData(Qt.QObject):
    """
    Inheriting from QObject so that this object can emit signals
    """

    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        
        Qt.QObject.__init__(self)
        
        self.nSamples = 1e3
        self.current_array_index = 0
        self.current_array = np.empty((self.nSamples,1))
        self.current_array[:] = np.NaN
        self.time_array = self.current_array.copy()
        
        #if not hla.machines._lat :
        #    hla.initNSLS2VSR()

        self.current_pv_name = 'SR:C00-BI:G00{DCCT:00}CUR-RB'
        #self.current_pv_name = hla.getElements('DCCT').pv()
        
        self.camonitor_subscription = None
        
        
    #----------------------------------------------------------------------
    def initialize_data_array(self):
        """ """
        
        self.current_array[:] = np.NaN
        self.current_array_index = 0
        self.time_array[:] = np.NaN
        
    #----------------------------------------------------------------------
    def start_subscription(self):
        """ """
        
        self.camonitor_subscription = camonitor(self.current_pv_name,
                                                self.camonitor_callback,
                                                format = FORMAT_TIME,
                                                all_updates = False)
        
    #----------------------------------------------------------------------
    def stop_subscription(self):
        """ """
        
        self.camonitor_subscription.close()
        
        
    #----------------------------------------------------------------------
    def camonitor_callback(self, new_value):
        """ """
        
        print new_value
        
        if self.current_array_index < len(self.current_array) :
            self.current_array[self.current_array_index] = new_value
            self.time_array[self.current_array_index] = new_value.timestamp
            self.current_array_index += 1
        else :
            self.current_array[:-1] = self.current_array[1:]
            self.current_array[-1] = new_value
            self.time_array[:-1] = self.time_array[1:]
            self.time_array[-1] = new_value.timestamp
            
        self.emit(Qt.SIGNAL("sigDataUpdated"),())
        
    #----------------------------------------------------------------------
    def process_raw_data_for_display(self):
        """ """
        
        t = self.time_array - self.time_array[0]
        y = self.current_array
        nan_ind = np.isnan(y)
        t = t[~nan_ind]
        y = y[~nan_ind]
        # Without removing NaN's from data, the plot line will turn back
        # to somewhere near the initial data point at the end of the line.
        # So, it is critical to remove NaN's here.
        
        self.emit(Qt.SIGNAL("sigDataProcessedReadyForDisplay"),
                  t, y)
        
        
    
########################################################################
class CurrentMonitorView(InteractivePlotWindow, Ui_MainWindow):
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
        self._initDataCursors()
        self._initPlotEditors()
        
                
    #----------------------------------------------------------------------
    def closeEvent(self, qCloseEvent):
        """ """
        
        # Need to notify CurrentMonitorApp that the view is close so that
        # CurrentMonitorApp can delete the camonitor subscription object,
        # which will ensure that the subscription is stopped, if running.
        # Without this, if this GUI is opened by another parent GUI, the
        # camonitor will keep running as long as the parent GUI is alive
        # even after this GUI window is closed.
        self.emit(Qt.SIGNAL("sigViewClosed"),())
        
    
    #----------------------------------------------------------------------
    def parent(self):
        """ """
        
        return self._parent
    
    #----------------------------------------------------------------------
    def _initPlots(self):
        """ """

        # Initialize the plot canvas
        p = self.qwtPlot # for short-hand notation
        p.setCanvasBackground(Qt.Qt.white)
        p.setAxisTitle(qwt.QwtPlot.xBottom, 'Time [s]')
        p.setAxisTitle(qwt.QwtPlot.yLeft, 'Current [mA]')
        p.setAxisAutoScale(qwt.QwtPlot.xBottom)
        p.setAxisAutoScale(qwt.QwtPlot.yLeft)
        p.setAutoReplot()
        
        # Initialize the curve representing the current history
        p.curve = qwt.QwtPlotCurve('Current [mA]')
        p.curve.setPen( Qt.QPen(Qt.Qt.red,
                                5,
                                Qt.Qt.SolidLine) )
        p.curve.setStyle(qwt.QwtPlotCurve.Lines)
        p.curve.setSymbol(qwt.QwtSymbol(qwt.QwtSymbol.Ellipse,
                                       Qt.QBrush(Qt.Qt.green),
                                       Qt.QPen(Qt.Qt.black, 6),
                                       Qt.QSize(5,5)))
        p.curve.setData(np.linspace(1,self.data.current_array_index+1,1),
                        self.data.current_array)
        p.curve.attach(self.qwtPlot)
        
        
        p.replot()
        
        
        self.plots = self.findChildren(qwt.QwtPlot)
        
    #----------------------------------------------------------------------
    def _initZoomers(self):
        """ """
        
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
        """ """
        
        self.panners = {}
                
        for p in self.plots :
            panner = PlotPanner(p.canvas())
            
            panner.setEnabled(False)
            
            self.panners[str(p.objectName())] = panner
    
            
    #----------------------------------------------------------------------
    def _initDataCursors(self):
        """ """
        
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
        """ """
        
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
        """ """
        
        new_value = self.data.current_array[self.data.current_array_index - 1]
        new_value = new_value.tolist()[0] # converting from NumPy array to a Python float
        
        self.label_current.setText('{:.3f}'.format(new_value))
        
    #----------------------------------------------------------------------
    def slotUpdatePlot(self, time_seconds, current_mA):
        """ """
        
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
        """ """

        self.statusBar().showMessage(message_text)
        
    

    

########################################################################
class CurrentMonitorApp(Qt.QObject):
    """
    Inheriting from QObject so that this object can connect signals to slots
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
        """ """
        
        self.data = CurrentMonitorData()
        
    
    #----------------------------------------------------------------------
    def _initView(self):
        """ """
        
        self.view = CurrentMonitorView(self.data, parent = self)
        
        self.connect(self.data, Qt.SIGNAL("sigDataUpdated"),
                     self.view.slotDataUpdated)
        self.connect(self.data, Qt.SIGNAL("sigDataUpdated"),
                     self.data.process_raw_data_for_display)
        
        self.connect(self.data, Qt.SIGNAL("sigDataProcessedReadyForDisplay"),
                     self.view.slotUpdatePlot)
        
        self.connect(self.view.pushButton_start, Qt.SIGNAL("clicked()"),
                     self.slot_start_monitor)
        
        self.connect(self.view.pushButton_stop, Qt.SIGNAL("clicked()"),
                     self.slot_stop_monitor)
        
        self.connect(self.view, Qt.SIGNAL("sigViewClosed"),
                     self.slotViewClosed)
        
        
    #----------------------------------------------------------------------
    def slot_start_monitor(self):
        """ """
        
        self.data.initialize_data_array()
        
        self.data.start_subscription()
        
        message = "Monitoring started @ " + time.asctime()
        self.view.updateStatusBar(message)
        
        # Reset all zoom stacks
        for key, zoomer in self.view.zoomers.items() :
            zoomer.resetZoomStack()
    
    #----------------------------------------------------------------------
    def slot_stop_monitor(self):
        """
        """
        
        if self.data.camonitor_subscription != None :
            if self.data.camonitor_subscription._Subscription__state == \
               self.data.camonitor_subscription._Subscription__OPEN :
                
                message = "Monitoring stopped @ " + time.asctime()
                self.view.updateStatusBar(message)
                
                self.data.stop_subscription() # Stop camonitor
            else:
                message = "Monitoring has been already stopped."
                self.view.updateStatusBar(message)
        else:
            message = "No camonitor subscription exists."
            self.view.updateStatusBar(message)
            
    #----------------------------------------------------------------------
    def slotViewClosed(self):
        """ """
        
        self.slot_stop_monitor()
        
        # print 'camonitor subscription closed and deleted.'
                
        
        
#----------------------------------------------------------------------        
def make():
    app = CurrentMonitorApp()
    window = app.view
    window.show()
    return app

#----------------------------------------------------------------------
def main(args = None):
    
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
    
