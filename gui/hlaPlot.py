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
import PyQt4.Qt as Qt
import PyQt4.Qwt5 as Qwt

import gui_icons

#----------------------------------------------------------------------
def getQtColor(colorString):
    """"""
    
    if colorString == 'blue':
        return Qt.Qt.blue
    elif colorString == 'red':
        return Qt.Qt.red
    elif colorString == 'black':
        return Qt.Qt.black
    elif colorString == 'white':
        return Qt.Qt.white
    else:
        raise ValueError('Unexpected color string: ' + colorString)

#----------------------------------------------------------------------
def getQtLineStyle(lineStyleString):
    """"""
    
    if lineStyleString == '-':
        return Qt.Qt.SolidLine
    else:
        raise ValueError('Unexpected line style string: ' + lineStyleString)
    
#----------------------------------------------------------------------
def getQwtMarker(markerString):
    """"""
    
    if markerString == 'None':
        return Qwt.QwtSymbol.NoSymbol
    elif markerString == '+':
        return Qwt.QwtSymbol.Cross
    elif markerString == 'x':
        return Qwt.QwtSymbol.XCross
    elif markerString == 'rect':
        return Qwt.QwtSymbol.Rect
    elif markerString == 'triangle':
        return Qwt.QwtSymbol.Triangle
    elif markerString == 'diamond':
        return Qwt.QwtSymbol.Diamond
    elif markerString == 'hline':
        return Qwt.QwtSymbol.HLine
    elif markerString == 'vline':
        return Qwt.QwtSymbol.VLine
    elif markerString == 'star1':
        return Qwt.QwtSymbol.Star1
    elif markerString == 'star2':
        return Qwt.QwtSymbol.Star2
    elif markerString == 'hexagon':
        return Qwt.QwtSymbol.Hexagon
    elif markerString == 'o':
        return Qwt.QwtSymbol.Ellipse
    else:
        raise ValueError('Unknown marker type string: ' + markerString)
    


########################################################################
class InteractivePlotWindow(Qt.QMainWindow):
    """
    A custom window class inheritted from QMainWindow with frequently
    used plot interaction capabilities embedded in the toolbar and the
    menubar by default.
    """

    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        
        Qt.QMainWindow.__init__(self)
        
        self._initInteractiveTools()
        
        self._createActions()
        self._initToolBar()
        self._initMenuBar()
        
    #----------------------------------------------------------------------
    def _initInteractiveTools(self):
        """"""
        
        self.zoomers = []
        self.panners = []
        self.dataCursors = []
        self.plotEditors = []
        
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
        
        for zoomer in self.zoomers:
            zoomer.setEnabled(TF)
            
        
        
    #----------------------------------------------------------------------
    def _enablePanners(self, TF):
        """"""
        
        for panner in self.panners:
            panner.setEnabled(TF)
            
    #----------------------------------------------------------------------
    def _enableDataCursors(self, TF):
        """"""
                    
        for data_cursor in self.dataCursors:
            data_cursor.setEnabled(TF)
            data_cursor.linked_marker.setVisible(False)
            # The reason why visibility is set to False always
            # is that without this it will show the previously
            # selected data cursor before a user has a chance
            # to select a new point.
            
    #----------------------------------------------------------------------
    def _enablePlotEditors(self, TF):
        
        for plot_editor in self.plotEditors:
            plot_editor.setEnabled(TF)
            plot_editor.selection_highlighter_curve.setVisible(False)
        
            QwtPlot_obj = plot_editor.plot()
            if TF :
                self.connect(QwtPlot_obj,
                             Qt.SIGNAL('customContextMenuRequested(const QPoint &)'),
                             plot_editor._slotContexMenuRequested)
            else :
                self.disconnect(QwtPlot_obj,
                                Qt.SIGNAL('customContextMenuRequested(const QPoint &)'),
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
        self.hlaPlotToolsMenu = Qt.QMenu('&Tools', self.menuBar())

        # Add Zoom Box Menu
        # zoomBoxAction = self.findChild(Qt.QAction,"action_zoom_box")
        zoomBoxAction = self.actions_dict["action_zoom_box"]
        self.hlaPlotToolsMenu.addAction(zoomBoxAction)

        # Add Pan XY Menu
        # panXYAction = self.findChild(Qt.QAction,"action_pan_xy")
        panXYAction = self.actions_dict["action_pan_xy"]
        self.hlaPlotToolsMenu.addAction(panXYAction)

        # Add Data Cursor Menu
        # dataCursorAction = self.findChild(Qt.QAction,"action_data_cursor")
        dataCursorAction = self.actions_dict["action_data_cursor"]
        self.hlaPlotToolsMenu.addAction(dataCursorAction)

        # Add Separator
        self.hlaPlotToolsMenu.addSeparator()
        
        # Add Edit Plot Menu
        # editPlotAction = self.findChild(Qt.QAction,"action_edit_plot")
        editPlotAction = self.actions_dict["action_edit_plot"]
        self.hlaPlotToolsMenu.addAction(editPlotAction)
        
    #----------------------------------------------------------------------
    def updateToolbarEnableStates(self):
        """"""

        checkedToolAction = None
        
        if self.zoomers:
            if self.zoomers[0].isEnabled():
                checkedToolAction = self.actions_dict['action_zoom_box']
            elif self.panners[0].isEnabled():
                checkedToolAction = self.actions_dict['action_pan_xy']
            elif self.dataCursors[0].isEnabled():
                checkedToolAction = self.actions_dict['action_data_cursor']
            elif self.plotEditors[0].isEnabled():
                checkedToolAction = self.actions_dict['action_edit_plot']
        
        actions = self.actionGroup.actions
        for a in actions:
            a.setChecked(False)
        
        if checkedToolAction:
            checkedToolAction.setChecked(True)
        
 
        
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
class PlotCurve(Qwt.QwtPlotCurve):
    """"""

    #----------------------------------------------------------------------
    def __init__(self, *args):
        """Constructor"""
        
        Qwt.QwtPlotCurve.__init__(self, *args)
        
        # Placer holders for NumPy array data.
        # These properties are added because if QwtPlotCurve contains
        # a large array, then it takes non-negligible amount of time
        # for just converting QwtArrayDouble, which is the type of data
        # returned by QwtPlotCurve.data().xData(), into NumPy double array.
        # So, when a curve is created, it is best to save the NumPy array
        # to these properties as well as QwtPlotCurve.setData(x,y) for
        # faster data processing later.
        self.numpyXData = np.array([])
        self.numpyYData = np.array([])
    
    
        
    
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
            pass

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
            #text.setText(
                #Qt.QString("x: %1").arg(closestPoints[0],fieldWidth=-3,precision=6) + \
                #'\r\n' + \
                #Qt.QString("y: %1").arg(closestPoints[1],fieldWidth=-3,precision=6) )
            text.setText( ('x: %-3.6g\r\n' + 'y: %-3.6g')
                          % (closestPoints[0], closestPoints[1]) )
            self.linked_marker.setLabel(text)
            self.linked_marker.setLabelAlignment(
                Qt.Qt.AlignRight | Qt.Qt.AlignTop)
        
            if not self.linked_marker.isVisible():
                print 'make it visible'
                self.linked_marker.setVisible(True)
            
            QwtPlot_obj.replot() # This line is essential. Without this new marker will now be drawn.
         
        
    
########################################################################
class PlotEditor(Qwt.QwtPlotPicker):
    """"""

    #----------------------------------------------------------------------
    def __init__(self, selection_highlighter_QwtPlotCurve, *args):
        """Constructor"""
        
        Qwt.QwtPlotPicker.__init__(self, *args)
        
        self.connect(self,
                     Qt.SIGNAL("selected(const QwtDoublePoint&)"),
                     self.highlightSelectedCurve)
        #self.connect(self,
                     #Qt.SIGNAL("selected(const QwtDoublePoint&)"),
                     #self.profile)
        
        self.selection_highlighter_curve = \
            selection_highlighter_QwtPlotCurve;
        
        self.selected_curve = []
        
        QwtPlot_obj = self.plot()
        QwtPlot_obj.setContextMenuPolicy(Qt.Qt.CustomContextMenu)


        self.popMenu = Qt.QMenu(QwtPlot_obj)
        menuLineWidth       = self.popMenu.addMenu('Line Width')
        menuLineColor       = self.popMenu.addMenu('Line Color')
        menuLineStyle       = self.popMenu.addMenu('Line Style')
        menuMarker          = self.popMenu.addMenu('Marker')
        menuMarkerSize      = self.popMenu.addMenu('Marker Size')
        menuMarkerFaceColor = self.popMenu.addMenu('Marker Face Color')
        menuMarkerEdgeColor = self.popMenu.addMenu('Marker Edge Color')
        menuMarkerEdgeWidth = self.popMenu.addMenu('Marker Edge Width')
        #
        for i in range(11):
            action = menuLineWidth.addAction(Qt.QIcon(), str(i))
            self.connect(action, Qt.SIGNAL('triggered()'),
                         self.onLineWidthActionTriggered)
            #
            action = menuMarkerSize.addAction(Qt.QIcon(),str(i))
            self.connect(action, Qt.SIGNAL('triggered()'),
                         self.onMarkerSizeActionTriggered)            
            #
            action = menuMarkerEdgeWidth.addAction(Qt.QIcon(),str(i))
            self.connect(action, Qt.SIGNAL('triggered()'),
                         self.onMarkerEdgeWidthActionTriggered)            
        #    
        colorStr = ['blue','red','black','green']
        for c in colorStr:
            action = menuLineColor.addAction(Qt.QIcon(),c)
            self.connect(action, Qt.SIGNAL('triggered()'),
                         self.onLineColorActionTriggered)
            #
            action = menuMarkerFaceColor.addAction(Qt.QIcon(),c)
            self.connect(action, Qt.SIGNAL('triggered()'),
                         self.onMarkerFaceColorActionTriggered)
            #
            action = menuMarkerEdgeColor.addAction(Qt.QIcon(),c)
            self.connect(action, Qt.SIGNAL('triggered()'),
                         self.onMarkerEdgeColorActionTriggered)            
        #
        markerStr = ['None','rect','triangle','o']
        for m in markerStr:
            action = menuMarker.addAction(Qt.QIcon(),m)
            self.connect(action, Qt.SIGNAL('triggered()'),
                         self.onMarkerActionTriggered)
        #
        lineStyleStr = ['None','-','DotLine',
                        'DashLine','DashDotLine','DashDotDotLine']
        for s in lineStyleStr:
            action = menuLineStyle.addAction(Qt.QIcon(),s)
            self.connect(action, Qt.SIGNAL('triggered()'),
                         self.onLineStyleActionTriggered)
      
    #----------------------------------------------------------------------
    def profile(self, point):
        """"""
        
        import hotshot
        import hotshot.stats
        
        prof = hotshot.Profile('plotter.prof')
        
        prof.runcall(self.highlightSelectedCurve, point)
        
        prof.close()        
        
            
    #----------------------------------------------------------------------
    def onLineWidthActionTriggered(self):
        """"""

        sender = self.sender()
        lineWidth = int(str(sender.text()))
        
        c = self.selected_curve
        currentPen = c.pen()
        c.setPen(Qt.QPen(currentPen.color(),
                         lineWidth,
                         currentPen.style()))
        c.plot().replot()
         
    #----------------------------------------------------------------------
    def onLineColorActionTriggered(self):
        """"""
        
        sender = self.sender()
        colorString = str(sender.text())
        
        c = self.selected_curve
        currentPen = c.pen()
        c.setPen(Qt.QPen(getattr(Qt.Qt, colorString),
                         currentPen.width(),
                         currentPen.style()))
        c.plot().replot()
        
    #----------------------------------------------------------------------
    def onLineStyleActionTriggered(self):
        """"""
        
        sender = self.sender()
        lineStyleStr = str(sender.text())
        
        c = self.selected_curve
        
        if lineStyleStr == 'None':
            c.setStyle(Qwt.QwtPlotCurve.NoCurve)
        else:
            c.setStyle(Qwt.QwtPlotCurve.Lines)
            
            if lineStyleStr == '-':
                QtLineStyle = Qt.Qt.SolidLine
            elif lineStyleStr == 'DotLine':
                QtLineStyle = Qt.Qt.DotLine
            elif lineStyleStr == 'DashLine':
                QtLineStyle = Qt.Qt.DashLine
            elif lineStyleStr == 'DashDotLine':
                QtLineStyle = Qt.Qt.DashDotLine
            elif lineStyleStr == 'DashDotDotLine':
                QtLineStyle = Qt.Qt.DashDotDotLine
            else:
                raise ValueError('Unexpected line style string.')
            
            currentPen = c.pen()

            c.setPen(Qt.QPen(currentPen.color(),
                             currentPen.width(),
                             QtLineStyle))
        
        c.plot().replot()
        
    #----------------------------------------------------------------------
    def onMarkerActionTriggered(self):
        """"""
        
        sender = self.sender()
        markerStr = str(sender.text())
        
        c = self.selected_curve
        
        currentSymbol = c.symbol()
        
        if markerStr == 'None':
            QwtSymbol = Qwt.QwtSymbol.NoSymbol
        elif markerStr == 'rect':
            QwtSymbol = Qwt.QwtSymbol.Rect
        elif markerStr == 'triangle':
            QwtSymbol = Qwt.QwtSymbol.Triangle
        elif markerStr == 'o':
            QwtSymbol = Qwt.QwtSymbol.Ellipse
        else:
            raise ValueError('Unexpected marker string.')
        
        c.setSymbol( Qwt.QwtSymbol(QwtSymbol,
                                   currentSymbol.brush(),
                                   currentSymbol.pen(),
                                   currentSymbol.size()) )
        
        c.plot().replot()
        
        
    #----------------------------------------------------------------------
    def onMarkerSizeActionTriggered(self):
        """"""

        sender = self.sender()
        markerSize = int(str(sender.text()))
        
        c = self.selected_curve
        
        currentSymbol = c.symbol()
        
        c.setSymbol( Qwt.QwtSymbol(currentSymbol.style(),
                                   currentSymbol.brush(),
                                   currentSymbol.pen(),
                                   Qt.QSize(markerSize,markerSize)) )
        
        c.plot().replot()
        
    #----------------------------------------------------------------------
    def onMarkerFaceColorActionTriggered(self):
        """"""
        
        sender = self.sender()
        colorString = str(sender.text())
        
        c = self.selected_curve
        
        currentSymbol = c.symbol()
        currentFaceBrush = currentSymbol.brush()

        c.setSymbol( Qwt.QwtSymbol(currentSymbol.style(),
                                   Qt.QBrush(getattr(Qt.Qt,colorString)),
                                   currentSymbol.pen(),
                                   currentSymbol.size()) )
 
        c.plot().replot()
           
    #----------------------------------------------------------------------
    def onMarkerEdgeColorActionTriggered(self):
        """"""
        
        sender = self.sender()
        colorString = str(sender.text())
        
        c = self.selected_curve
        
        currentSymbol = c.symbol()
        currentEdgePen = currentSymbol.pen()

        c.setSymbol( Qwt.QwtSymbol(currentSymbol.style(),
                                   currentSymbol.brush(),
                                   Qt.QPen(getattr(Qt.Qt,colorString),
                                           currentEdgePen.width()),
                                   currentSymbol.size()) )
 
        c.plot().replot()

        
    #----------------------------------------------------------------------
    def onMarkerEdgeWidthActionTriggered(self):
        """"""

        sender = self.sender()
        edgeWidth = int(str(sender.text()))
        
        c = self.selected_curve
        
        currentSymbol = c.symbol()
        currentEdgePen = currentSymbol.pen()

        c.setSymbol( Qwt.QwtSymbol(currentSymbol.style(),
                                   currentSymbol.brush(),
                                   Qt.QPen(currentEdgePen.color(),
                                           edgeWidth),
                                   currentSymbol.size()) )
 
        c.plot().replot()

        
    #----------------------------------------------------------------------
    def _slotContexMenuRequested(self, point):
        """"""
        
        if self.selected_curve != [] :
            self.popMenu.exec_(self.plot().mapToGlobal(point))
        
    

    #----------------------------------------------------------------------
    def highlightSelectedCurve(self, point):
        """"""
        
        #import tictoc
        
        #tStart = tictoc.tic()
        
        # Get selected point coordinate
        x_raw = np.double(point.x())
        y_raw = np.double(point.y())
        #print 'Coordinate (x,y): ', x_raw, y_raw
        

        QwtPlot_obj = self.plot()

        # Transform these coordinate values to pixel values
        map_x = QwtPlot_obj.canvasMap(Qwt.QwtPlot.xBottom)
        x_pix = map_x.transform(x_raw)
        map_y = QwtPlot_obj.canvasMap(Qwt.QwtPlot.yLeft)
        y_pix = map_y.transform(y_raw)
        #print 'Pixel (x,y): ', x_pix, y_pix
        
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
        
        #print 'start'
        #print tictoc.toc(tStart)
        
        min_distance = np.array([])
        selected_curve_candidates = []
        for c in curves :
            if hasattr(c, 'numpyXData'):
                xAll = c.numpyXData
            else:
                xAll = c.data().xData()
            if hasattr(c, 'numpyYData'):
                yAll = c.numpyYData
            else:
                yAll = c.data().yData()

            xpixAll = qwtScaleArrayTransform(xAll, map_x)
            ypixAll = qwtScaleArrayTransform(yAll, map_y)
            #
            #print 'xpixAll'
            #print tictoc.toc(tStart)

            smaller_than_x_min = xpixAll < x_min
            smaller_than_x_max = xpixAll < x_max
            smaller_than_y_min = ypixAll < y_min
            smaller_than_y_max = ypixAll < y_max    
            #
            #print 'smaller_than_x_min'
            #print tictoc.toc(tStart)

            diff_smaller_than_x_min = np.diff(smaller_than_x_min)
            diff_smaller_than_x_max = np.diff(smaller_than_x_max)
            #
            size_diff_smaller_than = diff_smaller_than_x_max.size
            #
            inside_or_crossing_x_boundaries = (
                diff_smaller_than_x_min | # crossing x_min
                diff_smaller_than_x_max | # crossing x_max
                (~diff_smaller_than_x_min & ~diff_smaller_than_x_max # When the line piece is between x_min and x_max
                 & (smaller_than_x_min[:size_diff_smaller_than] !=
                    smaller_than_x_max[:size_diff_smaller_than]) )
            )
            #
            #print 'inside_or_crossing_x_boundaries'
            #print tictoc.toc(tStart)

            diff_smaller_than_y_min = np.diff(smaller_than_y_min)
            diff_smaller_than_y_max = np.diff(smaller_than_y_max)
            #
            size_diff_smaller_than = diff_smaller_than_y_max.size
            #
            inside_or_crossing_y_boundaries = (
                diff_smaller_than_y_min | # crossing y_min
                diff_smaller_than_y_max | # crossing y_max
                (~diff_smaller_than_y_min & ~diff_smaller_than_y_max # When the line piece is between y_min and y_max
                 & (smaller_than_y_min[:size_diff_smaller_than] !=
                    smaller_than_y_max[:size_diff_smaller_than]) )
            )
            #
            #print 'inside_or_crossing_y_boundaries'
            #print tictoc.toc(tStart)

            inside_or_crossing_box = (
                inside_or_crossing_x_boundaries &
                inside_or_crossing_y_boundaries)
            #
            #print 'inside_or_crossing_box'
            #print tictoc.toc(tStart)

            # Find the distance
            # from the selected point to
            # all these lines, and find the minimum distance.
            nLines = np.sum(inside_or_crossing_box)
            ind = [ i for i in range(0,len(inside_or_crossing_box)) \
                    if inside_or_crossing_box[i] ]
            distance = np.zeros(nLines)
            for i in range(0,nLines) :
                x1 = xpixAll[ind[i]]
                y1 = ypixAll[ind[i]]
                x2 = xpixAll[ind[i]+1]
                y2 = ypixAll[ind[i]+1]
                distance[i] = self.point_line_distance(
                    x_pix, y_pix, x1, y1, x2, y2)
            #
            # 0.2 seconds
            #print 'point_line_distance'
            #print tictoc.toc(tStart)

            if len(distance) != 0 :
                
                #print distance.min()
            
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
        if self.selected_curve:
            
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
            
            # If the curve object has properties called "numpyXData'
            # and "numpyYData", it is much faster to directly get NumPy
            # array data from those properties, rather than to get the
            # data through xData() & yData() and then convert them to
            # NumPy data.
            if hasattr(self.selected_curve, 'numpyXData'):
                x = self.selected_curve.numpyXData
            else:
                x = np.array(self.selected_curve.data().xData())
            if hasattr(self.selected_curve, 'numpyYData'):
                y = self.selected_curve.numpyYData
            else:
                y = np.array(self.selected_curve.data().yData())
            
            nSamples = 10
            x_highlight = np.linspace(xmin,xmax,nSamples)
            y_highlight = np.interp(x_highlight, x, y)
            
            # Show this new data series as a highlighter curve to
            # indicate this curve is being selected.
            h = self.selection_highlighter_curve
            h.setData(x_highlight, y_highlight)
            h.setVisible(True)
            QwtPlot_obj.replot() # This line is essential. Without this, the new highlighter curve will not be drawn.
        
        #print 'last'
        #print tictoc.toc(tStart)
        
        
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
        
        if (a==0) and (b==0): # When the line is actually a point
            d = np.sqrt((x0-x1)**2+(y0-y1)**2)
        else:
            d = np.abs(a*x0+b*y0+c)/np.sqrt(a**2+b**2)
        
        if np.isnan(d):
            raise ValueError('NaN detected for point-line distance calculation.')
        
        return d
            
#----------------------------------------------------------------------
def qwtScaleArrayTransform(doubleArray, qwtScaleMapObj):
    """"""
    
    m = qwtScaleMapObj # for short-hand notation
    t = m.transformation() # for short-hand notation
    
    if isinstance(doubleArray, np.ndarray):
        npArray = doubleArray
    else: # Most likely, the double array is of type QwtArrayDouble.
        # Try to conver the array to NumPy array.
        try:
            npArray = np.array(doubleArray)
        except:
            raise('Passed double array object could not be converted to type NumPy array.')
    
    p1 = m.p1()
    p2 = m.p2()
    s1 = m.s1()
    s2 = m.s2()
    
    if t.type() == Qwt.QwtScaleTransformation.Linear:
        return p1 + (p2-p1) / (s2-s1) * (npArray-s1)
    elif t.type() == Qwt.QwtScaleTransformation.Log10:
        return p1 + (p2-p1) / np.log10(s2/s1) * \
               np.log10(npArray/s1)
    else:
        raise TypeError('QwtScaleTransformation type must be either Linear or Log10.')
    
    