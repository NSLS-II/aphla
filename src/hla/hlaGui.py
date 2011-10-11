#! /usr/bin/env python

"""

Custom GUI Widgets Libraries

:author: Yoshiteru Hidaka
:license:

Defines base classes that can be used as templates for quickly creating
an interactive plotting GUI application.

"""

import sys
import copy
import numpy as np
from PyQt4.QtGui import QMainWindow, QMenu
from PyQt4 import Qt, QtCore
import PyQt4.Qwt5 as Qwt

import toolbar_icons

########################################################################
class InteractivePlotWindow(QMainWindow):
    """
    A custom window class inheritted from QMainWindow with frequently
    used plot interaction capabilities embedded in the toolbar and the
    menumbar by default.
    """

    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        
        QMainWindow.__init__(self)
        
        self._createActions()
        self._initToolBar()
        self._initMenuBar()
        
        
    #----------------------------------------------------------------------
    def _createActions(self):
        """"""
        
        self.actionGroup = ActionObjectsGroup()
        
        self.actions_dict = {}
        
        # Action for Zoom Box
        zoomBoxAction = Qt.QAction(Qt.QIcon(":/zoom_in.png"),
                                   "Zoom &Box", self)
        zoomBoxAction.setCheckable(True)
        zoomBoxAction.setToolTip("Zoom into a region of interest")
        zoomBoxAction.setStatusTip("Zoom into a region of interest")
        zoomBoxAction.setObjectName("action_zoom_box")
        self.actionGroup.addAction(zoomBoxAction)
        self.actions_dict["action_zoom_box"] = zoomBoxAction
        self.connect(zoomBoxAction, Qt.SIGNAL("toggled(bool)"),
                     self._enableZoomers)
        
        # Action for Pan XY
        panXYAction = Qt.QAction(Qt.QIcon(":/hand.png"), 
                                 "&Pan XY", self)
        panXYAction.setCheckable(True)
        panXYAction.setObjectName("action_pan_xy")
        self.actionGroup.addAction(panXYAction)
        self.actions_dict["action_pan_xy"] = panXYAction
        self.connect(panXYAction, Qt.SIGNAL("toggled(bool)"),
                     self._enablePanners)
        
        # Action for Edit Plot
        editPlotAction = Qt.QAction(Qt.QIcon(":/pointer.png"), 
                                    "&Edit Plot", self)
        editPlotAction.setCheckable(True)
        editPlotAction.setObjectName("action_edit_plot")
        self.actionGroup.addAction(editPlotAction)
        self.actions_dict["action_edit_plot"] = editPlotAction
        self.connect(editPlotAction, Qt.SIGNAL("toggled(bool)"),
                     self._enablePlotEditors)
        
        # Action for Data Cursor
        dataCursorAction = Qt.QAction(Qt.QIcon(":/data_cursor.png"),
                                      "Data &Cursor", self)
        dataCursorAction.setCheckable(True)
        dataCursorAction.setObjectName("action_data_cursor")
        self.actionGroup.addAction(dataCursorAction)
        self.actions_dict["action_data_cursor"] = dataCursorAction
        self.connect(dataCursorAction, Qt.SIGNAL("toggled(bool)"),
                     self._enableDataCursors)
        

        # TODO:
        # expandToFillAction (just enable auto scale) setCheckable = False
        # verticalZoomInAction
        # horizontalZoomInAction
        # backwardAction
        # forwardAction
        # screenshotAction

        
        # Connect these actions to the slot ensuring that the selection
        # of actions is mutually exclusive, or no action is selected.
        self.connect(zoomBoxAction, Qt.SIGNAL("triggered()"),
                     self._enforceMutualExclusiveness)
        self.connect(panXYAction, Qt.SIGNAL("triggered()"),
                     self._enforceMutualExclusiveness)
        self.connect(editPlotAction, Qt.SIGNAL("triggered()"),
                     self._enforceMutualExclusiveness)
        self.connect(dataCursorAction, Qt.SIGNAL("triggered()"),
                     self._enforceMutualExclusiveness)
        
        self.actionGroup.update_check_states()
        
    #----------------------------------------------------------------------
    def _enforceMutualExclusiveness(self):
        """
        This slot ensures that the selection of actions is mutually exclusive.
        In other words, this slot makes sure that, at any one moment,
        only one or zero action is being selected. If two actions are
        selected, then this slot will automatically de-select the previously
        selected action, and keep the newly selected action as selected.
        """
        
        previous_actions_check_states = copy.copy(self.actionGroup.checked)
        current_actions_check_states = self.actionGroup.update_check_states()
        
        if sum(current_actions_check_states) == 2 : # 2 toolbar or menu bar items are toggled on
            index_to_be_toggled_off = self.find(previous_actions_check_states) # list output
            index_to_be_toggled_off = index_to_be_toggled_off[0] # Convert list to int
            
            # Toggle off the previously turned-on item
            self.actionGroup.actions[index_to_be_toggled_off].setChecked(False)
    
            # Update the checked states in the actionGroup
            self.actionGroup.update_check_states()
        
    #----------------------------------------------------------------------
    def find(self, a):
        """
        Find and return the indices where the input argument array "a"
        is True or non-zero values. This function emulates the MATLAB
        function "find.m".
        """
        
        return [index for (index, value) in enumerate(a) if value]
    
    #----------------------------------------------------------------------
    def _enableZoomers(self, TF):
        """"""
        
        for key, zoomer in self.zoomers.items() :
            zoomer.setEnabled(TF)
        
    #----------------------------------------------------------------------
    def _enablePanners(self, TF):
        """"""
        
        for key, panner in self.panners.items() :
            panner.setEnabled(TF)
            
    #----------------------------------------------------------------------
    def _enableDataCursors(self, TF):
        """"""
                    
        for key, data_cursor in self.data_cursors.items() :
            data_cursor.setEnabled(TF)
            data_cursor.linked_marker.setVisible(False)
            # The reason why visibility is set to False always
            # is that without this it will show the previously
            # selected data cursor before a user has a chance
            # to select a new point.
            
    #----------------------------------------------------------------------
    def _enablePlotEditors(self, TF):
        
        for key, plot_editor in self.plot_editors.items() :
            plot_editor.setEnabled(TF)
            plot_editor.selection_highlighter_curve.setVisible(False)
        
            QwtPlot_obj = plot_editor.plot()
            if TF :
                self.connect(QwtPlot_obj,
                             QtCore.SIGNAL('customContextMenuRequested(const QPoint &)'),
                             plot_editor._slotContexMenuRequested)
            else :
                self.disconnect(QwtPlot_obj,
                                QtCore.SIGNAL('customContextMenuRequested(const QPoint &)'),
                                plot_editor._slotContexMenuRequested)
             
    #----------------------------------------------------------------------
    def _initToolBar(self):
        """"""
               
        # Zoom Box
        zoomBoxToolbar = self.addToolBar("Zoom Box")
        zoomBoxToolbar.setObjectName("toolbar_zoom_box")
        # zoomBoxAction = self.findChild(Qt.QAction,"action_zoom_box")
        zoomBoxAction = self.actions_dict["action_zoom_box"]
        zoomBoxToolbar.addAction(zoomBoxAction)
        
        # Pan XY
        panXYToolbar = self.addToolBar("Pan XY")
        panXYToolbar.setObjectName("toolbar_pan_xy")
        # panXYAction = self.findChild(Qt.QAction,"action_pan_xy")
        panXYAction = self.actions_dict["action_pan_xy"]
        panXYToolbar.addAction(panXYAction)
       
        # Data Cursor
        dataCursorToolbar = self.addToolBar("Data Cursor")
        dataCursorToolbar.setObjectName("toolbar_data_cursor")
        # dataCursorAction = self.findChild(Qt.QAction,"action_data_cursor")
        dataCursorAction = self.actions_dict["action_data_cursor"]
        dataCursorToolbar.addAction(dataCursorAction)
        
        # Add Separator
        dataCursorToolbar.addSeparator()
        
        # Edit Plot
        editPlotToolbar = self.addToolBar("Edit Plot")
        editPlotToolbar.setObjectName("toolbar_edit_plot")
        # editPlotAction = self.findChild(Qt.QAction,"action_edit_plot")
        editPlotAction = self.actions_dict["action_edit_plot"]
        editPlotToolbar.addAction(editPlotAction)
        
        
    #----------------------------------------------------------------------
    def _initMenuBar(self):
        """"""
                
        # Tools Menu
        toolsMenu = self.menuBar().addMenu("&Tools")

        # Add Zoom Box Menu
        # zoomBoxAction = self.findChild(Qt.QAction,"action_zoom_box")
        zoomBoxAction = self.actions_dict["action_zoom_box"]
        toolsMenu.addAction(zoomBoxAction)

        # Add Pan XY Menu
        # panXYAction = self.findChild(Qt.QAction,"action_pan_xy")
        panXYAction = self.actions_dict["action_pan_xy"]
        toolsMenu.addAction(panXYAction)

        # Add Data Cursor Menu
        # dataCursorAction = self.findChild(Qt.QAction,"action_data_cursor")
        dataCursorAction = self.actions_dict["action_data_cursor"]
        toolsMenu.addAction(dataCursorAction)

        # Add Separator
        toolsMenu.addSeparator()
        
        # Add Edit Plot Menu
        # editPlotAction = self.findChild(Qt.QAction,"action_edit_plot")
        editPlotAction = self.actions_dict["action_edit_plot"]
        toolsMenu.addAction(editPlotAction)
        
        

 
        
########################################################################
class ActionObjectsGroup:
    """"""

    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        
        self.actions = [] # list of QAction objects
        self.checked = [] # list of bool
        
        
    #----------------------------------------------------------------------
    def addAction(self, QAction):
        """"""
        
        self.actions.append(QAction)
        self.checked.append(QAction.isChecked())
        
    #----------------------------------------------------------------------
    def update_check_states(self):
        """"""
        
        for ii in range(len(self.actions)) :
            self.checked[ii] = self.actions[ii].isChecked()
            
        return self.checked
    
        
    
########################################################################
class PlotZoomer(Qwt.QwtPlotZoomer):
    """"""

    #----------------------------------------------------------------------
    def __init__(self, *args):
        """Constructor"""
        Qwt.QwtPlotZoomer.__init__(self, *args)
        
        self.connect(self, Qt.SIGNAL("zoomed(const QwtDoubleRect &)"),
                     self._slotZoomed)
        
    #----------------------------------------------------------------------
    def _slotZoomed(self):
        """"""
        
        if self.zoomRectIndex() == 0 : # If the zoomer is at the base
            self.resetZoomStack()
        
    
    #----------------------------------------------------------------------
    def zoom(self, *args):
        """
        Change the functionality of zoomer here, if you want
        """
        
        Qwt.QwtPlotZoomer.zoom(self, *args)
    
    #----------------------------------------------------------------------
    def resetZoomStack(self):
        """"""
        
        QwtPlot = self.plot()
        
        QwtPlot.setAxisAutoScale(self.xAxis())
        QwtPlot.setAxisAutoScale(self.yAxis())
        QwtPlot.replot()
        
        self.setZoomBase()
       
        
    #----------------------------------------------------------------------
    def _slotPanned(self):
        """
        When the plot is panned, the plot can extend outside the base zoom
        stack. In this case, when you re-activate the zoom box, the plot
        display region will snap back to the base zoom stack. In order to
        avoid this problem, every time the plot is panned, the plot's base
        zoom stack is reset to the current panned region.
        """
        
        self.setZoomBase()
        

########################################################################
class PlotPanner(Qwt.QwtPlotPanner):
    """"""

    #----------------------------------------------------------------------
    def __init__(self, *args):
        """Constructor"""
        Qwt.QwtPlotPanner.__init__(self, *args)
        
        QwtPlotCanvas = self.parent()
        linked_zoomer = QwtPlotCanvas.findChild(PlotZoomer)
        
        if linked_zoomer != None :
            self.connect(self, Qt.SIGNAL("panned(int,int)"),
                         linked_zoomer._slotPanned)
        
    
########################################################################
class PlotDataCursor(Qwt.QwtPlotPicker):
    """"""

    #----------------------------------------------------------------------
    def __init__(self, linked_QwtPlotMarker, *args):
        """Constructor"""
        
        Qwt.QwtPlotPicker.__init__(self, *args)
        
        self.connect(self,
                     Qt.SIGNAL("selected(const QwtDoublePoint&)"),
                     self.show_selected_point)
        
        self.linked_marker = linked_QwtPlotMarker
    
    #----------------------------------------------------------------------
    def show_selected_point(self, point):
        """"""
        
        x_raw = np.double(point.x())
        y_raw = np.double(point.y())
        
        #print window.qwtPlot.curve.closestPoint(point.toPoint())
        #print point.toPoint()
        
        
        QwtPlot_obj = self.plot()
        curves = QwtPlot_obj.itemList()
        curves = [c for c in curves 
                  if isinstance(c, Qwt.QwtPlotCurve)]
        # Remove the selection highlighter curve for a plot editor 
        # from the curve list, if it exists. The highlighter curve
        # exists solely for highlighting a selected curve, and it
        # is not a read data curve.
        QwtPlotCanvas_obj = self.parent()
        plot_editor = QwtPlotCanvas_obj.findChild(PlotEditor)
        if plot_editor != None :
            for (index, c) in enumerate(curves) :
                if c.title() == plot_editor.selection_highlighter_curve.title() :
                    highlighter_index = index
            curves.pop(highlighter_index)
        
        
        x_all = []
        y_all = []
        for c in curves :
            d = c.data()
            if isinstance(d, Qwt.QwtArrayData) :
                x = np.double(d.xData())
                y = np.double(d.yData())
            
                if len(x) == len(y) :
                    x_all = np.append(x_all, x)
                    y_all = np.append(y_all, y)
        
        if (x_all == []) | (y_all == []) :
            # No valid data points for the data cursor to lock onto.
            # Do nothing.
            comment = 'do nothing'

        else :
            distance = np.sqrt((x_all-x_raw)**2+(y_all-y_raw)**2)
            min_index = np.nanargmin(distance)
            closestPoints = [x_all[min_index], y_all[min_index]]
            
            # TODO:
            # Add distance threshold so that a click really far
            # from any of the data points will be ignored.
        
            # TODO:
            # If the selection point sits on a connecting line,
            # even if the selection point is far from the 
            # neighboring points on the line, lock onto the closest
            # of those points.

            self.linked_marker.setValue(closestPoints[0], 
                                        closestPoints[1])
        
            text = self.linked_marker.label();
            text.setText(
                Qt.QString("x: %1").arg(closestPoints[0],fieldWidth=-3,precision=6) + \
                '\r\n' + \
                Qt.QString("y: %1").arg(closestPoints[1],fieldWidth=-3,precision=6) )
            self.linked_marker.setLabel(text)
            self.linked_marker.setLabelAlignment(
                Qt.Qt.AlignRight | Qt.Qt.AlignTop)
        
            if ~self.linked_marker.isVisible() :
                self.linked_marker.setVisible(True)
         
        
    
########################################################################
class PlotEditor(Qwt.QwtPlotPicker):
    """"""

    #----------------------------------------------------------------------
    def __init__(self, selection_highlighter_QwtPlotCurve, *args):
        """Constructor"""
        
        Qwt.QwtPlotPicker.__init__(self, *args)
        
        self.connect(self,
                     Qt.SIGNAL("selected(const QwtDoublePoint&)"),
                     self.highlight_selected_curve)
        
        self.selection_highlighter_curve = \
            selection_highlighter_QwtPlotCurve;
        
        self.selected_curve = []
        
        QwtPlot_obj = self.plot()
        QwtPlot_obj.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        
        # Actions
        self.actionLineWidth = Qt.QAction(Qt.QIcon(),
                                          "Line Width",
                                          QwtPlot_obj)
        self.connect(self.actionLineWidth, Qt.SIGNAL("triggered()"),
                     self._slotActionLineWidthTriggered)
        self.actionLineColor = Qt.QAction(Qt.QIcon(),
                                          "Line Color",
                                          QwtPlot_obj)
        self.connect(self.actionLineColor, Qt.SIGNAL("triggered()"),
                     self._slotActionLineColorTriggered)
        
        # Popup Menu
        self.popMenu = QMenu(QwtPlot_obj)
        self.popMenu.addAction(self.actionLineWidth)
        self.popMenu.addSeparator()
        self.popMenu.addAction(self.actionLineColor)
        
    #----------------------------------------------------------------------
    def _slotActionLineWidthTriggered(self):
        """"""
        
    #----------------------------------------------------------------------
    def _slotActionLineColorTriggered(self):
        """"""
        
        c = self.selected_curve
        c.setPen(Qt.QPen(Qt.Qt.green,
                         5,
                         Qt.Qt.SolidLine))
        c.plot().replot()
        
        
    #----------------------------------------------------------------------
    def _slotContexMenuRequested(self, point):
        """"""
        
        if self.selected_curve != [] :
            self.popMenu.exec_(self.plot().mapToGlobal(point))
        
    
    #----------------------------------------------------------------------
    def highlight_selected_curve(self, point):
        """"""
        
        # Get selected point coordinate
        x_raw = np.double(point.x())
        y_raw = np.double(point.y())
        print 'Coordinate (x,y): ', x_raw, y_raw
        

        QwtPlot_obj = self.plot()

        # Transform these coordinate values to pixel values
        map_x = QwtPlot_obj.canvasMap(Qwt.QwtPlot.xBottom)
        x_pix = map_x.transform(x_raw)
        map_y = QwtPlot_obj.canvasMap(Qwt.QwtPlot.yLeft)
        y_pix = map_y.transform(y_raw)
        print 'Pixel (x,y): ', x_pix, y_pix
        
        # Find if there is any nearby curve on the plot. First,
        # find all piecewise lines that cross a certain-sized
        # box around the selected point.
        box_half_width_pixel = 5
        distance_threshold = 2
        x_min = x_pix - box_half_width_pixel
        x_max = x_pix + box_half_width_pixel
        y_min = y_pix - box_half_width_pixel
        y_max = y_pix + box_half_width_pixel
        
        
        curves = QwtPlot_obj.itemList()
        curves = [c for c in curves 
                  if isinstance(c, Qwt.QwtPlotCurve)]
        # Remove the selection highlighter curve from the curve list,
        # because the highlighter curve exists solely for highlighting
        # a selected curve, and it is not a read data curve.
        for (index, c) in enumerate(curves) :
            if c.title() == self.selection_highlighter_curve.title() :
                highlighter_index = index
        curves.pop(highlighter_index)
        
        
        min_distance = np.array([])
        selected_curve_candidates = []
        for c in curves :
            d = c.data()
            if isinstance(d, Qwt.QwtArrayData) :
                x = d.xData()
                y = d.yData()
            
                X = [map_x.transform(x_i) for x_i in x]
                Y = [map_y.transform(y_i) for y_i in y]
                
                smaller_than_x_min = [X_i < x_min for X_i in X]
                smaller_than_x_max = [X_i < x_max for X_i in X]
                smaller_than_y_min = [Y_i < y_min for Y_i in Y]
                smaller_than_y_max = [Y_i < y_max for Y_i in Y]
                
                diff_smaller_than_x_min = list(np.diff(smaller_than_x_min))
                diff_smaller_than_x_max = list(np.diff(smaller_than_x_max))
                
                inside_or_crossing_x_boundaries = [
                      (diff_smaller_than_x_min[i] != 0) # crossing x_min
                      | # or
                      (diff_smaller_than_x_max[i] != 0) # crossing x_max
                      | # or
                      ( (diff_smaller_than_x_min[i] == 0) # When the line piece is between x_min and x_max
                        &
                        (diff_smaller_than_x_max[i] == 0)
                        &
                        (smaller_than_x_min[i] != 
                         smaller_than_x_max[i]) )
                      for i in range(0,len(diff_smaller_than_x_min)) ]
        
                diff_smaller_than_y_min = list(np.diff(smaller_than_y_min))
                diff_smaller_than_y_max = list(np.diff(smaller_than_y_max))
                
                inside_or_crossing_y_boundaries = [
                      (diff_smaller_than_y_min[i] != 0) # crossing y_min
                      | # or
                      (diff_smaller_than_y_max[i] != 0) # crossing y_max
                      | # or
                      ( (diff_smaller_than_y_min[i] == 0) # When the line piece is between y_min and y_max
                        &
                        (diff_smaller_than_y_max[i] == 0)
                        &
                        (smaller_than_y_min[i] !=
                         smaller_than_y_max[i]) )
                      for i in range(0,len(diff_smaller_than_y_min)) ]
        
                inside_or_crossing_box = list(
                    np.array(inside_or_crossing_x_boundaries)
                    &
                    np.array(inside_or_crossing_y_boundaries)
                    )
                
                # Find the distance
                # from the selected point to
                # all these lines, and find the minimum distance.
                nLines = np.sum(inside_or_crossing_box)
                ind = [ i for i in range(0,len(inside_or_crossing_box)) \
                        if inside_or_crossing_box[i] ]
                distance = np.zeros(nLines)
                for i in range(0,nLines) :
                    x1 = X[ind[i]]
                    y1 = Y[ind[i]]
                    x2 = X[ind[i]+1]
                    y2 = Y[ind[i]+1]
                    distance[i] = self.point_line_distance(
                        x_pix, y_pix, x1, y1, x2, y2)
                
                if len(distance) != 0 :
                    
                    print distance.min()
                
                    if distance.min() < distance_threshold :
                        min_distance = np.append(min_distance, 
                                                 distance.min());
                        selected_curve_candidates.append(c)
                
        # Select the curve among the candidates that is closest to 
        # the selected point
        if len(selected_curve_candidates) != 0 :
            '''
            If this minimum distance is less than with your threshold
            distance, then choose the corresponding line to be the
            selected curve. If the minimum distance is more than
            the threshold, then no curve is selected.
            '''
            if min_distance.min() < distance_threshold :
                min_ind = min_distance.argmin()
                self.selected_curve = \
                    selected_curve_candidates[min_ind]
            else :
                self.selected_curve = []
        else :
            self.selected_curve = []
        
        # If such a curve is found, create a data series partially
        # sampled from the selected curve.
        if self.selected_curve != [] :
            
            xlim = QwtPlot_obj.axisScaleDiv(self.selected_curve.xAxis())
            xmin_axis = xlim.lowerBound()
            xmax_axis = xlim.upperBound()
            
            ylim = QwtPlot_obj.axisScaleDiv(self.selected_curve.yAxis())
            ymin_axis = ylim.lowerBound()
            ymax_axis = ylim.upperBound()
            
            xmin_curve = self.selected_curve.minXValue()
            xmax_curve = self.selected_curve.maxXValue()
            
            xmin = max(xmin_axis, xmin_curve)
            xmax = min(xmax_axis, xmax_curve)
            
            x = np.array(self.selected_curve.data().xData())
            y = np.array(self.selected_curve.data().yData())
            
            nSamples = 10
            x_highlight = np.linspace(xmin,xmax,nSamples)
            y_highlight = np.interp(x_highlight, x, y)
            
        
            # Show this new data series as a highlighter curve to
            # indicate this curve is being selected.
            h = self.selection_highlighter_curve
            h.setData(x_highlight, y_highlight)
            h.setVisible(True)
            
            
        
        
    def point_line_distance(self, x0,y0,x1,y1,x2,y2):
        '''
        Return the distance between the point (x0,y0) and
        a line connected by the points (x1,y1) and (x2,y2)
        '''
            
        a = np.double(y2-y1)
        b = np.double(-(x2-x1))
        c = np.double(y1*(x2-x1)-x1*(y2-y1))
            
        x0 = np.double(x0)
        y0 = np.double(y0)
            
        d = np.abs(a*x0+b*y0+c)/np.sqrt(a**2+b**2)
            
        return d
            
        
    
    