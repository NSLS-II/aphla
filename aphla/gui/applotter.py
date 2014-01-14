"""

GUI application for data plotting

:author: Yoshiteru Hidaka
:license:


"""

import sys, os, math
import numpy as np
import scipy.interpolate as spint
import h5py
import cothread

# This API settings are necessary if IPython is to be embedded,
# and these settings must be performed before importing PyQt4.
# By using v.2 API, there will be no class Qstring and QVariant
# available.
import sip
sip.setapi('QString', 2)
sip.setapi('QVariant', 2)

import PyQt4.Qt as Qt
import PyQt4.Qwt5 as Qwt

from PlotterUtils.ui_plotter import Ui_MainWindow
import PlotterUtils.ui_addNewCurveForCurvesDockWidget as ui_addNewCurveForCurvesDockWidget
#import ui_addNewCurveForDatasetsDockWidget
import PlotterUtils.embedIPython as embedIPython

import aphla
import hlaPlot

DEF_LINE_COLOR = 'blue'
DEF_LINE_STYLE = '-'
DEF_LINE_WIDTH = 3
DEF_MARKER = 'None'
DEF_MARKER_SIZE = 3
DEF_MARKER_FACE_COLOR = 'red'
DEF_MARKER_EDGE_COLOR = 'blue'
DEF_MARKER_EDGE_WIDTH = 1
DEF_XAXIS = 'xBottom'
DEF_YAXIS = 'yLeft'


## TODO
# *) If indepVar selection is changed, the curves related
# to the variable should be also updated.
# *) Plot config file to automatically load data & plot
# *) Implement expression editor




########################################################################
class NewCurveDialogForCurvesDock(Qt.QDialog, ui_addNewCurveForCurvesDockWidget.Ui_Dialog):
    """"""

    #----------------------------------------------------------------------
    def __init__(self, existingFigNameList, varNameList):
        """Constructor"""

        Qt.QDialog.__init__(self)

        self.setupUi(self)

        self.data = {}

        colorCodingStrList = ['blue','red']
        varNameListWithIndexes = varNameList[:]
        varNameListWithIndexes.extend(['Index of "' + varName + '"'
                                       for varName in varNameList])

        self.lineEdit_dispName.setText('')
        self.checkBox_visible.setChecked(True)
        figTabTitleList = ['']
        figTabTitleList.extend(existingFigNameList)
        self.comboBox_figName.addItems(figTabTitleList)
        rowCount = 1
        colCount = 1
        self.spinBox_canvasRowCount.setValue(rowCount)
        self.spinBox_canvasColCount.setValue(colCount)
        rowIndexStrList = [str(i) for i in range(rowCount)]
        colIndexStrList = [str(i) for i in range(colCount)]
        self.listWidget_canvasRowPos.addItems(rowIndexStrList)
        self.listWidget_canvasRowPos.setCurrentRow(0)
        self.listWidget_canvasColPos.addItems(colIndexStrList)
        self.listWidget_canvasColPos.setCurrentRow(0)
        self.comboBox_xVarName.addItems(varNameListWithIndexes)
        self.comboBox_xAxis.addItems(['xBottom','xTop'])
        self.comboBox_yVarName.addItems(varNameListWithIndexes)
        self.comboBox_yAxis.addItems(['yLeft','yRight'])
        self.comboBox_lineColor.addItems(colorCodingStrList)
        self.comboBox_lineStyle.addItems(['None','-'])
        self.comboBox_lineStyle.setCurrentIndex(1)
        self.comboBox_lineWidth.addItems(['1','2','3','4','5'])
        self.comboBox_marker.addItems(['None','.','o','x'])
        self.comboBox_marker.setCurrentIndex(0)
        self.comboBox_markerSize.addItems(['1','2','3','4'])
        self.comboBox_markerEdgeColor.addItems(colorCodingStrList)
        self.comboBox_markerFaceColor.addItems(colorCodingStrList)

        self.splitter.setSizes([int(self.width()*(1./2)),
                                int(self.width()*(1./2))])

        self.connect(self.spinBox_canvasRowCount,
                     Qt.SIGNAL('valueChanged(int)'),
                     self.updateRowIndexListWidget)
        self.connect(self.spinBox_canvasColCount,
                     Qt.SIGNAL('valueChanged(int)'),
                     self.updateColIndexListWidget)

    #----------------------------------------------------------------------
    def updateRowIndexListWidget(self, rowCount):
        """"""

        rowIndexStrList = [str(i) for i in range(rowCount)]

        self.listWidget_canvasRowPos.clear()
        self.listWidget_canvasRowPos.addItems(rowIndexStrList)

    #----------------------------------------------------------------------
    def updateColIndexListWidget(self, colCount):
        """"""

        colIndexStrList = [str(i) for i in range(colCount)]

        self.listWidget_canvasColPos.clear()
        self.listWidget_canvasColPos.addItems(colIndexStrList)

    #----------------------------------------------------------------------
    def accept(self):
        """"""

        self.data['dispName'] = str(self.lineEdit_dispName.text())
        self.data['isVisible'] = self.checkBox_visible.isChecked()
        figName = str(self.comboBox_figName.currentText())
        self.data['figName'] = figName
        self.data['canvasRowCount'] = self.spinBox_canvasRowCount.value()
        self.data['canvasColCount'] = self.spinBox_canvasColCount.value()
        canvasRowPosItems = self.listWidget_canvasRowPos.selectedItems()
        if canvasRowPosItems:
            canvasRowPos = [int(item.text()) for item in canvasRowPosItems]
            canvasRowPos.sort()
            self.data['canvasRowPos'] = canvasRowPos
        else:
            msgBox = Qt.QMessageBox()
            msgBox.setText( (
                'A row index or a range of row indexes must be selected.') )
            msgBox.setInformativeText('')
            msgBox.setIcon(Qt.QMessageBox.Critical)
            msgBox.exec_()
            return
        canvasColPosItems = self.listWidget_canvasColPos.selectedItems()
        if canvasColPosItems:
            canvasColPos = [int(item.text()) for item in canvasColPosItems]
            canvasColPos.sort()
            self.data['canvasColPos'] = canvasColPos
        else:
            msgBox = Qt.QMessageBox()
            msgBox.setText( (
                'A column index or a range of column indexes must be selected.') )
            msgBox.setInformativeText('')
            msgBox.setIcon(Qt.QMessageBox.Critical)
            msgBox.exec_()
            return
        self.data['xVarName'] = str(self.comboBox_xVarName.currentText())
        self.data['xAxis'] = str(self.comboBox_xAxis.currentText())
        self.data['yVarName'] = str(self.comboBox_yVarName.currentText())
        self.data['yAxis'] = str(self.comboBox_yAxis.currentText())
        self.data['lineColor'] = str(self.comboBox_lineColor.currentText())
        self.data['lineStyle'] =  str(self.comboBox_lineStyle.currentText())
        self.data['lineWidth'] = int(self.comboBox_lineWidth.currentText())
        self.data['marker'] = str(self.comboBox_marker.currentText())
        self.data['markerSize'] = int(self.comboBox_markerSize.currentText())
        self.data['markerEdgeColor'] = str(self.comboBox_markerEdgeColor.currentText())
        self.data['markerFaceColor'] = str(self.comboBox_markerFaceColor.currentText())


        super(NewCurveDialogForCurvesDock, self).accept() # will hide the dialog

    #----------------------------------------------------------------------
    def reject(self):
        """"""

        super(NewCurveDialogForCurvesDock, self).reject() # will hide the dialog

#########################################################################
#class NewCurveDialogForDatasetsDock(Qt.QDialog, ui_addNewCurveForDatasetsDockWidget.Ui_Dialog):
    #""""""

    ##----------------------------------------------------------------------
    #def __init__(self, existingFigNameList, varNameList):
        #"""Constructor"""

        #Qt.QDialog.__init__(self)

        #self.setupUi(self)

        #self.data = {}

        #colorCodingStrList = ['blue','red']
        #varNameListWithIndexes = varNameList[:]
        #varNameListWithIndexes.extend(['Index of "' + varName + '"'
                                       #for varName in varNameList])

        #self.lineEdit_dispName.setText('')
        #self.checkBox_visible.setChecked(True)
        #figTabTitleList = ['']
        #figTabTitleList.extend(existingFigNameList)
        #self.comboBox_figName.addItems(figTabTitleList)
        #rowCount = 1
        #colCount = 1
        #self.spinBox_canvasRowCount.setValue(rowCount)
        #self.spinBox_canvasColCount.setValue(colCount)
        #rowIndexStrList = [str(i) for i in range(rowCount)]
        #colIndexStrList = [str(i) for i in range(colCount)]
        #self.listWidget_canvasRowPos.addItems(rowIndexStrList)
        #self.listWidget_canvasRowPos.setCurrentRow(0)
        #self.listWidget_canvasColPos.addItems(colIndexStrList)
        #self.listWidget_canvasColPos.setCurrentRow(0)
        #self.comboBox_xVarName.addItems(varNameListWithIndexes)
        #self.comboBox_xAxis.addItems(['xBottom','xTop'])
        #self.comboBox_yVarName.addItems(varNameListWithIndexes)
        #self.comboBox_yAxis.addItems(['yLeft','yRight'])
        #self.comboBox_lineColor.addItems(colorCodingStrList)
        #self.comboBox_lineStyle.addItems(['None','-'])
        #self.comboBox_lineStyle.setCurrentIndex(1)
        #self.comboBox_lineWidth.addItems(['1','2','3','4','5'])
        #self.comboBox_marker.addItems(['None','.','o','x'])
        #self.comboBox_marker.setCurrentIndex(0)
        #self.comboBox_markerSize.addItems(['1','2','3','4'])
        #self.comboBox_markerEdgeColor.addItems(colorCodingStrList)
        #self.comboBox_markerFaceColor.addItems(colorCodingStrList)

        #self.splitter.setSizes([int(self.width()*(1./2)),
                                #int(self.width()*(1./2))])

        #self.connect(self.spinBox_canvasRowCount,
                     #Qt.SIGNAL('valueChanged(int)'),
                     #self.updateRowIndexListWidget)
        #self.connect(self.spinBox_canvasColCount,
                     #Qt.SIGNAL('valueChanged(int)'),
                     #self.updateColIndexListWidget)

    ##----------------------------------------------------------------------
    #def updateRowIndexListWidget(self, rowCount):
        #""""""

        #rowIndexStrList = [str(i) for i in range(rowCount)]

        #self.listWidget_canvasRowPos.clear()
        #self.listWidget_canvasRowPos.addItems(rowIndexStrList)

    ##----------------------------------------------------------------------
    #def updateColIndexListWidget(self, colCount):
        #""""""

        #colIndexStrList = [str(i) for i in range(colCount)]

        #self.listWidget_canvasColPos.clear()
        #self.listWidget_canvasColPos.addItems(colIndexStrList)

    ##----------------------------------------------------------------------
    #def accept(self):
        #""""""

        #self.data['dispName'] = str(self.lineEdit_dispName.text())
        #self.data['isVisible'] = self.checkBox_visible.isChecked()
        #figName = str(self.comboBox_figName.currentText())
        #self.data['figName'] = figName
        #self.data['canvasRowCount'] = self.spinBox_canvasRowCount.value()
        #self.data['canvasColCount'] = self.spinBox_canvasColCount.value()
        #canvasRowPosItems = self.listWidget_canvasRowPos.selectedItems()
        #if canvasRowPosItems:
            #canvasRowPos = [int(item.text()) for item in canvasRowPosItems]
            #canvasRowPos.sort()
            #self.data['canvasRowPos'] = canvasRowPos
        #else:
            #msgBox = Qt.QMessageBox()
            #msgBox.setText( (
                #'A row index or a range of row indexes must be selected.') )
            #msgBox.setInformativeText('')
            #msgBox.setIcon(Qt.QMessageBox.Critical)
            #msgBox.exec_()
            #return
        #canvasColPosItems = self.listWidget_canvasColPos.selectedItems()
        #if canvasColPosItems:
            #canvasColPos = [int(item.text()) for item in canvasColPosItems]
            #canvasColPos.sort()
            #self.data['canvasColPos'] = canvasColPos
        #else:
            #msgBox = Qt.QMessageBox()
            #msgBox.setText( (
                #'A column index or a range of column indexes must be selected.') )
            #msgBox.setInformativeText('')
            #msgBox.setIcon(Qt.QMessageBox.Critical)
            #msgBox.exec_()
            #return
        #self.data['xVarName'] = str(self.comboBox_xVarName.currentText())
        #self.data['xAxis'] = str(self.comboBox_xAxis.currentText())
        #self.data['yVarName'] = str(self.comboBox_yVarName.currentText())
        #self.data['yAxis'] = str(self.comboBox_yAxis.currentText())
        #self.data['lineColor'] = str(self.comboBox_lineColor.currentText())
        #self.data['lineStyle'] =  str(self.comboBox_lineStyle.currentText())
        #self.data['lineWidth'] = int(self.comboBox_lineWidth.currentText())
        #self.data['marker'] = str(self.comboBox_marker.currentText())
        #self.data['markerSize'] = int(self.comboBox_markerSize.currentText())
        #self.data['markerEdgeColor'] = str(self.comboBox_markerEdgeColor.currentText())
        #self.data['markerFaceColor'] = str(self.comboBox_markerFaceColor.currentText())


        #super(NewCurveDialogForCurvesDock, self).accept() # will hide the dialog

    ##----------------------------------------------------------------------
    #def reject(self):
        #""""""

        #super(NewCurveDialogForCurvesDock, self).reject() # will hide the dialog


########################################################################
class CurvesDockModel(Qt.QStandardItemModel):
    """"""

    #----------------------------------------------------------------------
    def __init__(self, mainView, datasetsModel, *args):
        """Constructor"""

        Qt.QStandardItemModel.__init__(self, *args)

        self.mainView = mainView
        self.datasetsModel = datasetsModel

        self.colHeaderLabels = []

        self.rowHeaderLabels = ['Display Name', 'Show', 'Figure Name',
                                'Canvas Row Count', 'Canvas Column Count',
                                'Canvas Row Position', 'Canvas Column Position',
                                'X Variable', 'X-Axis', 'Y Variable', 'Y-Axis',
                                'Line Color', 'Line Style', 'Line Width',
                                'Marker', 'Marker Size', 'Marker Edge Color',
                                'Marker Face Color']
        r = self.rowHeaderLabels # for short-hand notation
        self.setVerticalHeaderLabels(self.rowHeaderLabels)
        self.setRowCount(len(self.rowHeaderLabels))


        self.curveList = []

    #----------------------------------------------------------------------
    def getIndexArray(self, vector):
        """"""

        if vector.ndim == 1:
            indexArray = np.arange(1,vector.size+1)
        else:
            raise ValueError('Dimension of the passed variable must be 1.')

        return indexArray

    #----------------------------------------------------------------------
    def getIndepVar(self, depVarName):
        """"""

        varNameList = self.datasetsModel.varNameList
        depVarRowInd = varNameList.index(depVarName)
        indepVarColInd = self.datasetsModel.propNameList.index('indepVar')

        indepVarName = str(
            self.datasetsModel.item(depVarRowInd,indepVarColInd).text())

        if indepVarName == 'index':
            depVar = self.datasetsModel.ds[depVarName]
            shape = depVar.shape
            if len(shape) != 1:
                depVar = depVar.squeeze()
                self.datasetsModel.ds[depVarName] = depVar
            if len(depVar.shape) != 1:
                msgBox = Qt.QMessageBox()
                msgBox.setText( 'Variable must be a 1-D vector.' )
                msgBox.setInformativeText( '' )
                msgBox.setIcon(Qt.QMessageBox.Critical)
                msgBox.exec_()
                return None
            indepVar = np.linspace(1,len(depVar),len(depVar))
        else:
            indepVar = self.datasetsModel.ds[indepVarName]

        return indepVar


    #----------------------------------------------------------------------
    def addNewCurve(self, newCurveData):
        """"""

        d = newCurveData # for short-hand notation

        y = self.datasetsModel.ds[d['yVarName']]
        if type(y) != np.ndarray:
            errorMsg = 'Y Variable must be of type numpy.ndarray.'
            print errorMsg
            self.mainView.statusbar.showMessage(errorMsg)
            return
        if d['xVarName'] == 'index':
            x = self.getIndexArray(y)
            #if y.ndim == 1:
                #x = np.arange(1,y.size+1)
            #else:
                #raise ValueError('Dimension of Y variable must be 1.')
            xIndepVar = x
            yIndepVar = x
        else:
            x = self.datasetsModel.ds[d['xVarName']]
            if type(x) != np.ndarray:
                errorMsg = 'X Variable must be of type numpy.ndarray.'
                print errorMsg
                self.mainView.statusbar.showMessage(errorMsg)
                return
            #
            xIndepVar = self.getIndepVar(d['xVarName'])
            yIndepVar = self.getIndepVar(d['yVarName'])

        if (xIndepVar == None) or (yIndepVar == None):
            return
        #
        if np.all(xIndepVar == yIndepVar):
            nanInd = np.isnan(x) | np.isnan(y)
            xData = x[~nanInd]
            yData = y[~nanInd]
        else: # Need to interpolate
            # Check monotonically increasing
            if np.all(np.diff(xIndepVar)<=0):
                msgBox = Qt.QMessageBox()
                msgBox.setText( ('Indep. var. associated w/ Y variable must be monotonically increasing for interpolation.') )
                msgBox.setInformativeText( '' )
                msgBox.setIcon(Qt.QMessageBox.Critical)
                msgBox.exec_()
                return
            else:
                f = spint.interp1d(yIndepVar,y,kind='linear',
                                   bounds_error=False,fill_value=np.nan)
                yinterp = f(xIndepVar)
                nanInd = np.isnan(x) | np.isnan(yinterp)
                xData = x[~nanInd]
                yData = yinterp[~nanInd]


        counter = 1
        newColHeader = 'Curve ' + str(counter)
        while newColHeader in self.colHeaderLabels:
            counter += 1
            newColHeader = 'Curve ' + str(counter)
        self.colHeaderLabels.append(newColHeader)
        self.setHorizontalHeaderLabels(self.colHeaderLabels)

        col = counter - 1

        r = self.rowHeaderLabels # for short-hand notation
        self.setItem(r.index('Display Name'),col,Qt.QStandardItem(d['dispName']))
        item = Qt.QStandardItem('')
        item.setCheckable(True)
        if d['isVisible']:
            item.setCheckState(Qt.Qt.Checked)
        else:
            item.setCheckState(Qt.Qt.Unchecked)
        self.setItem(r.index('Show'),col,item)
        self.setItem(r.index('Figure Name'),col,Qt.QStandardItem(d['figName']))
        self.setItem(r.index('Canvas Row Count'),col,Qt.QStandardItem(str(d['canvasRowCount'])))
        self.setItem(r.index('Canvas Column Count'),col,Qt.QStandardItem(str(d['canvasColCount'])))
        self.setItem(r.index('Canvas Row Position'),col,Qt.QStandardItem(str(d['canvasRowPos'])))
        self.setItem(r.index('Canvas Column Position'),col,Qt.QStandardItem(str(d['canvasColPos'])))
        self.setItem(r.index('X Variable'),col,Qt.QStandardItem(d['xVarName']))
        self.setItem(r.index('X-Axis'),col,Qt.QStandardItem(d['xAxis']))
        self.setItem(r.index('Y Variable'),col,Qt.QStandardItem(d['yVarName']))
        self.setItem(r.index('Y-Axis'),col,Qt.QStandardItem(d['yAxis']))
        self.setItem(r.index('Line Color'),col,Qt.QStandardItem(d['lineColor']))
        self.setItem(r.index('Line Style'),col,Qt.QStandardItem(d['lineStyle']))
        self.setItem(r.index('Line Width'),col,Qt.QStandardItem(str(d['lineWidth'])))
        self.setItem(r.index('Marker'),col,Qt.QStandardItem(d['marker']))
        self.setItem(r.index('Marker Size'),col,Qt.QStandardItem(str(d['markerSize'])))
        self.setItem(r.index('Marker Edge Color'),col,Qt.QStandardItem(d['markerEdgeColor']))
        self.setItem(r.index('Marker Face Color'),col,Qt.QStandardItem(d['markerFaceColor']))

        newCurve = hlaPlot.PlotCurve(d['dispName'])
        if d['lineStyle'] == '-':
            lineStyle = Qt.Qt.SolidLine
        newCurve.setPen(Qt.QPen(hlaPlot.getQtColor(d['lineColor']),
                                d['lineWidth'],
                                lineStyle))
        newCurve.setStyle(Qwt.QwtPlotCurve.Lines)
        newCurve.setSymbol(Qwt.QwtSymbol(
            hlaPlot.getQwtMarker(d['marker']),
            Qt.QBrush(hlaPlot.getQtColor(d['markerFaceColor'])),
            Qt.QPen(hlaPlot.getQtColor(d['markerEdgeColor']),2),
            Qt.QSize(d['markerSize'],d['markerSize'])))


        newCurve.setData(xData,yData)
        newCurve.numpyXData = xData
        newCurve.numpyYData = yData

        xAxis = getattr(Qwt.QwtPlot,d['xAxis'])
        yAxis = getattr(Qwt.QwtPlot,d['yAxis'])

        newCurve.setXAxis(xAxis)
        newCurve.setYAxis(yAxis)

        qwtPlot = self.mainView.getQwtPlot(d['figName'],
                                           d['canvasRowCount'], d['canvasColCount'],
                                           d['canvasRowPos'], d['canvasColPos'])
        # Need to update "Figure Name" since calling "getQwtPlot" function may
        # have changed "Figure Name" automatically, if the "Figure Name" string was
        # empty or there was a naming conflict.
        self.setItem(r.index('Figure Name'),col,
                     Qt.QStandardItem(qwtPlot.parent().title))
        qwtPlot.setAxisTitle(xAxis, d['xVarName'])
        qwtPlot.setAxisTitle(yAxis, d['yVarName'])
        qwtPlot.enableAxis(xAxis, True)
        qwtPlot.enableAxis(yAxis, True)
        qwtPlot.setAxisAutoScale(xAxis)
        qwtPlot.setAxisAutoScale(yAxis)

        newCurve.attach(qwtPlot)
        qwtPlot.replot()

        self.emit(Qt.SIGNAL('newCurveAdded'), qwtPlot, xAxis, yAxis)

        self.curveList.append(newCurve)

        self.mainView.raiseCanvas(qwtPlot)

    #----------------------------------------------------------------------
    def updateVarName(self, oldVarName, newVarName):
        """"""

        xVarNameInd = self.rowHeaderLabels.index('X Variable')
        yVarNameInd = self.rowHeaderLabels.index('Y Variable')
        for col in range(self.columnCount()):
            if self.item(xVarNameInd,col).text() == oldVarName:
                self.item(xVarNameInd,col).setText(newVarName)
            if self.item(yVarNameInd,col).text() == oldVarName:
                self.item(yVarNameInd,col).setText(newVarName)



########################################################################
class CurvesDockView(Qt.QWidget):
    """"""

    #----------------------------------------------------------------------
    def __init__(self, mainView):
        """Constructor"""

        Qt.QWidget.__init__(self)

        self.mainView = mainView

        self.setObjectName('curvesDockView')

        gridLayout = Qt.QGridLayout(self)
        gridLayout.setObjectName('curvesDock_gridLayout')
        horizLayout = Qt.QHBoxLayout()
        horizLayout.setObjectName('curvesDock_horizLayout')
        self.radioButton_simple = Qt.QRadioButton(self)
        self.radioButton_simple.setText('Simple')
        self.radioButton_simple.setChecked(True)
        self.radioButton_simple.setObjectName('curvesDock_radButton_simple')
        horizLayout.addWidget(self.radioButton_simple)
        self.radioButton_advanced = Qt.QRadioButton(self)
        self.radioButton_advanced.setText('Advanced')
        self.radioButton_advanced.setObjectName('curvesDock_radButton_advanced')
        horizLayout.addWidget(self.radioButton_advanced)
        spacerItem = Qt.QSpacerItem(40, 20, Qt.QSizePolicy.Expanding,
                                    Qt.QSizePolicy.Minimum)
        horizLayout.addItem(spacerItem)
        gridLayout.addLayout(horizLayout, 0, 0, 1, 1)
        self.tableView = Qt.QTableView(self)
        self.tableView.setObjectName('curvesDock_tableView')
        gridLayout.addWidget(self.tableView, 1, 0, 1, 1)


        self.model = CurvesDockModel(self.mainView,
                                     self.mainView.dockView_datasets.model)
        self.proxyModel = Qt.QSortFilterProxyModel()
        self.proxyModel.setSourceModel(self.model)

        self.tableView.setModel(self.proxyModel)
        #self.tableView.setSortingEnabled(True)
        self.tableView.resizeColumnsToContents()

        self.selectedVarNames = []

        self.connect(self.tableView.selectionModel(),
                     Qt.SIGNAL('selectionChanged(const QItemSelection &, const QItemSelection &)'),
                     self.onSelectionChange)
        self.tableView.setContextMenuPolicy(Qt.Qt.CustomContextMenu)
        self.tableView.contextMenu = Qt.QMenu()
        self.connect(self.tableView,
                     Qt.SIGNAL('customContextMenuRequested(const QPoint &)',),
                     self.openContextMenu)


        self.connect(self, Qt.SIGNAL('addNewCurve'), self.model.addNewCurve)

    #----------------------------------------------------------------------
    def onSelectionChange(self, selected, deselected):
        """"""

        itemSelectionModel = self.sender()

        proxyModel = itemSelectionModel.model()
        model = proxyModel.sourceModel()

        #print 'Old Selection Empty? ', deselected.isEmpty()
        #print 'Deselected = ', deselected
        #print 'New Selection Empty? ', selected.isEmpty()
        #print 'Selected = ', selected
        #selectedProxyIndexes = itemSelectionModel.selectedIndexes()
        #selectedIndexes = [proxyModel.mapToSource(proxyIndex)
                           #for proxyIndex in selectedProxyIndexes]
        #selectedItems = [model.itemFromIndex(index) for index in selectedIndexes]
        #selectedRows = [item.row() for item in selectedItems]
        #selectedItemTexts = [str(item.text()) for item in selectedItems]

        selectedProxyRowIndexes = itemSelectionModel.selectedRows()
        selectedRowIndexes = [proxyModel.mapToSource(proxyIndex)
                           for proxyIndex in selectedProxyRowIndexes]
        selectedRowItems = [model.itemFromIndex(index) for index in selectedRowIndexes]
        selectedRows = [item.row() for item in selectedRowItems]
        #self.selectedVarNames = [self.getVariableName(r) for r in selectedRows]
        #print selectedRows
        #print self.selectedVarNames

    #----------------------------------------------------------------------
    def openContextMenu(self, qpoint):
        """"""

        sender = self.sender()

        globalClickPos = sender.mapToGlobal(qpoint)

        sender.contextMenu.clear()
        if not self.selectedVarNames:
            menuStr = 'Add a new curve'
            action = sender.contextMenu.addAction(Qt.QIcon(), menuStr)
            self.connect(action, Qt.SIGNAL('triggered()'),
                         self.addNewCurve)


        else:
            pass


        sender.contextMenu.exec_(globalClickPos)

    #----------------------------------------------------------------------
    def addNewCurve(self):
        """"""

        if not self.mainView.varNameList:
            msgBox = Qt.QMessageBox()
            msgBox.setText( ('To add a new curve, you must first create at least one variable in "Datasets".') )
            msgBox.setInformativeText( '' )
            msgBox.setIcon(Qt.QMessageBox.Critical)
            msgBox.exec_()
            return

        dialog = NewCurveDialogForCurvesDock(self.mainView.figTabTitleList,
                                             self.mainView.varNameList)
        dialog.exec_()

        if dialog.result() == Qt.QDialog.Accepted:
            #print dialog.data

            self.emit(Qt.SIGNAL('addNewCurve'), dialog.data)




########################################################################
class FigureTab(Qt.QWidget):
    """"""

    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""

        Qt.QWidget.__init__(self)

        self.gridLayout = Qt.QGridLayout(self)
        self.title = 'Fig 1'
        self.subplotRowCount = 1

        self._initInteractiveTools()



    #----------------------------------------------------------------------
    def _initInteractiveTools(self):
        """"""

        self.zoomers = []
        self.panners = []
        self.dataCursors = []
        self.plotEditors = []







########################################################################
class DatasetsDockModel(Qt.QStandardItemModel):
    """"""

    #----------------------------------------------------------------------
    def __init__(self, mainView):
        """Constructor"""

        Qt.QStandardItemModel.__init__(self)

        self.mainView = mainView

        self.propNameColNameDict = {'name':'Name', 'origName':'Orig. Name',
                                    'description':'Description', 'indepVar':'Indep. Var.',
                                    'srcType':'Src. Type', 'srcAddr':'Src. Address',
                                    'srcTimeRange':'Src. Time Range', 'derivation':'Derivation'}
        self.propNameList = ['name', 'origName', 'description', 'indepVar',
                             'srcType', 'srcAddr', 'srcTimeRange', 'derivation']
        self.headerLabels = [self.propNameColNameDict[pName]
                             for pName in self.propNameList]
        if set(self.headerLabels) != set(self.propNameColNameDict.values()):
            raise ValueError('Values of prop. name vs. col. name dict must match w/ header labels.')
        self.setHorizontalHeaderLabels(self.headerLabels)
        self.setColumnCount(len(self.headerLabels))

        self.varNameList = []
        self.derivedVarNameList = []
        self.ds = {} # Will contain all the loaded data

        self.connect(self,
                     Qt.SIGNAL('dataChanged(const QModelIndex &, const QModelIndex &)'),
                     self.onDataChange)


    #----------------------------------------------------------------------
    def onDataChange(self, topLeftModelIndex, bottomRightModelIndex):
        """"""

        if topLeftModelIndex != bottomRightModelIndex:
            raise ValueError('There should be only 1 item data changed.')

        self.emit(Qt.SIGNAL('datasetsChanged'), topLeftModelIndex)

        item = self.itemFromIndex(topLeftModelIndex)
        if item.column() == self.col('derivation'):

            varNameItem = self.item(item.row(),self.col('name'))
            varName = str(varNameItem.text())

            # Do not perform derivation on variables whose source type
            # are NOT "variables".
            if varNameItem.srcType != 'variables':
                # Force reset uncommitted expression string to empty string
                varNameItem.uncommittedDerivationExpression = ''
                # Force reset committed expression string to empty string
                item.setText('')
                return

            # Perform derivation on variables whose source type is "variables"
            codeSource = str(item.text()).strip()
            if codeSource:
                derivedArray = self.runDerivation(codeSource,self.ds)
                if derivedArray != None: # Derivation evaluation succeeded
                    self.ds[varName] = derivedArray
                    varNameItem.uncommittedDerivationExpression = codeSource
                    self.emit(Qt.SIGNAL('derivationExpChangedOnDatasets'), varName)
                else: # Derivation evaluation failed
                    item.setText(varNameItem.uncommittedDerivationExpression)
            else:
                varNameItem.uncommittedDerivationExpression = ''
                self.ds[varName] = None

    #----------------------------------------------------------------------
    def commitDerivationExpChange(self, varName, newExpression):
        """"""

        rowIndex = self.varNameList.index(varName)

        derivationItem = self.item(rowIndex,self.col('derivation'))

        derivationItem.setText(newExpression)

    #----------------------------------------------------------------------
    def changeUncommittedExpression(self, varName, newUncommittedExpression):
        """"""

        rowIndex = self.varNameList.index(varName)

        varNameItem = self.item(rowIndex,self.col('name'))

        varNameItem.uncommittedDerivationExpression = newUncommittedExpression




    #----------------------------------------------------------------------
    def col(self, propName_or_colName, nameType='propName'):
        """"""

        if nameType == 'propName':
            propName = propName_or_colName
            return self.propNameList.index(propName)
        elif nameType == 'colName':
            colName = propName_or_colName
            return self.headerLabels.index(colName)
        else:
            raise TypeError('Unexpected nameType: ' + nameType)


    #----------------------------------------------------------------------
    def load_hdf5(self, filepath):
        """"""

        f = h5py.File(filepath, 'r')
        newDsNameList = self.getAllHDF5DatasetNameList(f)

        for n in newDsNameList:
            # If the new name conflicts w/ the variable names already loaded,
            # then automatically change the new name.
            newVarName = n
            dup_counter = 1
            while newVarName in self.varNameList:
                newVarName = n + '_dup' + str(dup_counter)
                dup_counter += 1
            self.varNameList.append(newVarName)
            self.ds[newVarName] = f[n].value.squeeze()
            newRow = self.rowCount()
            varNameItem = Qt.QStandardItem(newVarName)
            varNameItem.uncommittedDerivationExpression = ''
            varNameItem.srcType = 'file'
            self.setItem(newRow,0,varNameItem)

            for propName in self.propNameList[1:]:
                if propName == 'origName':
                    itemText = n
                    editable = False
                elif propName == 'description':
                    itemText = ''
                    editable = True
                elif propName == 'indepVar':
                    itemText = 'index'
                    editable = True
                elif propName == 'srcType':
                    itemText = varNameItem.srcType
                    editable = False
                elif propName == 'srcAddr':
                    itemText = filepath
                    editable = False
                elif propName == 'srcTimeRange':
                    itemText = 'N/A'
                    editable = False
                elif propName == 'derivation':
                    itemText = ''
                    editable = False
                else:
                    raise ValueError('Unexpected property name: ' + propName)
                item = Qt.QStandardItem(itemText)
                if not editable:
                    item.setEditable(editable)
                self.setItem(newRow, self.col(propName), item)


        f.close()


    #----------------------------------------------------------------------
    def getAllHDF5DatasetNameList(self, openedHDF5FileObj):
        """"""

        datasetNameList = []

        def appendDatasetName(name, obj):
            if isinstance(obj, h5py.Dataset):
                datasetNameList.append(name)

        openedHDF5FileObj.visititems(appendDatasetName)

        return datasetNameList


    #----------------------------------------------------------------------
    def updateVarNameList(self, modelIndex):
        """"""

        item = self.itemFromIndex(modelIndex)

        if item.column() == self.col('name'):
            changedRow = item.row()
            oldVarName = self.varNameList[changedRow]
            newVarName = str(item.text())

            self.varNameList[changedRow] = newVarName

            if item.srcType == 'variables':
                dInd = self.derivedVarNameList.index(oldVarName)
                self.derivedVarNameList[dInd] = newVarName

            var = self.ds.pop(oldVarName)
            self.ds[newVarName] = var

            indepVarColInd = self.propNameList.index('indepVar')
            for r in range(self.rowCount()):
                indepVarItem = self.item(r,indepVarColInd)
                if indepVarItem and \
                   (str(indepVarItem.text()) == oldVarName):
                    indepVarItem.setText(newVarName)

            return (oldVarName, newVarName)
        else:
            return ('', '')

    #----------------------------------------------------------------------
    def runDerivation(self, codeSource, args):
        """"""

        try:
            codeObj = compile(codeSource, '<string>', 'eval')
        except SyntaxError:
            try:
                codeObj = compile(codeSource, '<string>', 'exec')
            except:
                erroMsg = str(sys.exc_info())
                print erroMsg
                self.mainView.statusbar.showMessage(erroMsg)
                print 'Expression compilation failed.'
                return None

        #make a list of safe functions
        from math import acos, asin, atan, atan2, ceil, cos, cosh, \
             degrees, e, exp, fabs, floor, fmod, frexp, hypot, ldexp, \
             log, log10, modf, pi, pow, radians, sin, sinh, sqrt, tan, tanh
        import numpy as np
        import scipy as sp
        safe_list = ['math','acos', 'asin', 'atan', 'atan2', 'ceil',
                     'cos', 'cosh', 'degrees', 'e', 'exp', 'fabs',
                     'floor', 'fmod', 'frexp', 'hypot', 'ldexp', 'log',
                     'log10', 'modf', 'pi', 'pow', 'radians', 'sin',
                     'sinh', 'sqrt', 'tan', 'tanh',
                     'np', 'sp']
        #use the list to filter the local namespace
        safe_dict = dict([ (k, locals().get(k, None)) for k in safe_list ])
        #add any needed builtins back in.
        safe_dict['abs'] = abs
        for (k,v) in args.iteritems():
            safe_dict[k] = v
        custom_builtins = {'True':True, 'False':False, '__import__':__import__}
        try:
            #output = eval(codeObj, {"__builtins__":None}, safe_dict)
            #output = eval(codeObj, {"__builtins__":custom_builtins}, safe_dict)
            output = eval(codeObj, {}, safe_dict) # Allow __builtins__ in eval
        except:
            erroMsg = str(sys.exc_info())
            print erroMsg
            self.mainView.statusbar.showMessage(erroMsg)
            return None

        if output != None: # When code string was a single expression (using 'eval')
            return output
        else: # When code string was a sequence of statements (using 'exec')
            if safe_dict.has_key('output'):
                return safe_dict['output']
            else:
                errorMsg = 'You must assign a value to the variable "output".'
                print errorMsg
                self.mainView.statusbar.showMessage(errorMsg)
                return None




########################################################################
class DatasetsDockViewDelegate(Qt.QStyledItemDelegate):
    """"""

    #----------------------------------------------------------------------
    def __init__(self, varNameList, parent=None):
        """Constructor"""

        Qt.QStyledItemDelegate.__init__(self, parent)

        self.indepVarColIndex = 3

        self.varNameList = varNameList

    #----------------------------------------------------------------------
    def getItemFromProxyModelIndex(self, proxyModelIndex):
        """"""

        proxyModel = proxyModelIndex.model()
        model = proxyModel.sourceModel()
        sourceIndex = proxyModel.mapToSource(proxyModelIndex)
        item = model.itemFromIndex(sourceIndex)

        return item

    #----------------------------------------------------------------------
    def createEditor(self, parent, option, modelIndex):
        """
        implementation of virtual function
        """

        item = self.getItemFromProxyModelIndex(modelIndex)
        colInd = item.column()

        if colInd == self.indepVarColIndex:
            editor = Qt.QComboBox(parent)
            editor.setEditable(False)
            indepVarNameList = ['index']
            indepVarNameList.extend(self.varNameList)
            editor.addItems(indepVarNameList)
        else:
            editor = Qt.QStyledItemDelegate.createEditor(self, parent, option, modelIndex)

        return editor

    #----------------------------------------------------------------------
    def setEditorData(self, editor, modelIndex):
        """
        implementation of virtual function
        """

        item = self.getItemFromProxyModelIndex(modelIndex)
        colInd = item.column()

        if colInd == self.indepVarColIndex:
            matchedIndex = editor.findText(item.text(),
                                           (Qt.Qt.MatchCaseSensitive |
                                            Qt.Qt.MatchExactly))
            if matchedIndex == -1:
                matchedIndex = 0

            editor.setCurrentIndex(matchedIndex)
            #editor.showPopup()

        else:
            Qt.QStyledItemDelegate.setEditorData(self, editor, modelIndex)



    #----------------------------------------------------------------------
    def setModelData(self, editor, model, modelIndex):
        """
        implementation of virtual function
        """

        item = self.getItemFromProxyModelIndex(modelIndex)
        colInd = item.column()

        if colInd == self.indepVarColIndex:
            item.setText(editor.currentText())
        else:
            Qt.QStyledItemDelegate.setModelData(self, editor, model, modelIndex)


    #----------------------------------------------------------------------
    def updateEditorGeometry(self, editor, option, modelIndex):
        """
        implementation of virtual function
        """

        rect = option.rect
        #rect.adjust(0, -2, 0, +2)
        editor.setGeometry(rect)


########################################################################
class DatasetsDockView(Qt.QWidget):
    """"""

    #----------------------------------------------------------------------
    def __init__(self, mainView):
        """Constructor"""

        Qt.QWidget.__init__(self)

        self.setObjectName('datasetsDockView')

        gridLayout = Qt.QGridLayout(self)
        gridLayout.setObjectName('datasetsDock_gridLayout')
        horizLayout = Qt.QHBoxLayout()
        horizLayout.setObjectName('datasetsDock_horizLayout')
        self.radioButton_simple = Qt.QRadioButton(self)
        self.radioButton_simple.setText('Simple')
        self.radioButton_simple.setChecked(True)
        self.radioButton_simple.setObjectName('datasetsDock_radButton_simple')
        horizLayout.addWidget(self.radioButton_simple)
        self.radioButton_advanced = Qt.QRadioButton(self)
        self.radioButton_advanced.setText('Advanced')
        self.radioButton_advanced.setObjectName('datasetsDock_radButton_advanced')
        horizLayout.addWidget(self.radioButton_advanced)
        spacerItem = Qt.QSpacerItem(40, 20, Qt.QSizePolicy.Expanding,
                                    Qt.QSizePolicy.Minimum)
        horizLayout.addItem(spacerItem)
        gridLayout.addLayout(horizLayout, 0, 0, 1, 1)
        self.tableView = Qt.QTableView(self)
        self.tableView.setObjectName('datasetsDock_tableView')
        gridLayout.addWidget(self.tableView, 1, 0, 1, 1)



        self.model = DatasetsDockModel(mainView)
        self.proxyModel = Qt.QSortFilterProxyModel()
        self.proxyModel.setSourceModel(self.model)

        self.tableView.setModel(self.proxyModel)
        self.tableView.setSelectionMode(Qt.QAbstractItemView.ExtendedSelection)
        self.tableView.setSelectionBehavior(Qt.QAbstractItemView.SelectRows)
        self.tableView.setSortingEnabled(True)
        self.tableView.resizeColumnsToContents()

        self.delegate = DatasetsDockViewDelegate(self.model.varNameList)
        self.tableView.setItemDelegate(self.delegate)

        self.selectedVarNames = []

        self.connect(self.tableView.selectionModel(),
                     Qt.SIGNAL('selectionChanged(const QItemSelection &, const QItemSelection &)'),
                     self.onSelectionChange)
        self.tableView.setContextMenuPolicy(Qt.Qt.CustomContextMenu)
        self.tableView.contextMenu = Qt.QMenu()
        self.connect(self.tableView,
                     Qt.SIGNAL('customContextMenuRequested(const QPoint &)',),
                     self.openContextMenu)


        self.startDirPath = os.getcwd()



    #----------------------------------------------------------------------
    def getVariableName(self, rowIndex_or_modelIndex_or_item):
        """"""

        if type(rowIndex_or_modelIndex_or_item) is int:
            selectedRow = rowIndex_or_modelIndex_or_item
        elif type(rowIndex_or_modelIndex_or_item) is Qt.QModelIndex:
            selectedItem = self.model.itemFromIndex(
                rowIndex_or_modelIndex_or_item)
            selectedRow  = selectedItem.row()
        elif type(rowIndex_or_modelIndex_or_item) is Qt.QStandardItem:
            selectedRow = rowIndex_or_modelIndex_or_item.row()
        else:
            raise TypeError('Unexpected type: ' + type(rowIndex_or_modelIndex_or_item))

        return str(self.model.item(selectedRow,0).text())

    #----------------------------------------------------------------------
    def onSelectionChange(self, selected, deselected):
        """"""

        itemSelectionModel = self.sender()

        proxyModel = itemSelectionModel.model()
        model = proxyModel.sourceModel()

        #print 'Old Selection Empty? ', deselected.isEmpty()
        #print 'Deselected = ', deselected
        #print 'New Selection Empty? ', selected.isEmpty()
        #print 'Selected = ', selected
        #selectedProxyIndexes = itemSelectionModel.selectedIndexes()
        #selectedIndexes = [proxyModel.mapToSource(proxyIndex)
                           #for proxyIndex in selectedProxyIndexes]
        #selectedItems = [model.itemFromIndex(index) for index in selectedIndexes]
        #selectedRows = [item.row() for item in selectedItems]
        #selectedItemTexts = [str(item.text()) for item in selectedItems]

        selectedProxyRowIndexes = itemSelectionModel.selectedRows()
        selectedRowIndexes = [proxyModel.mapToSource(proxyIndex)
                           for proxyIndex in selectedProxyRowIndexes]
        selectedRowItems = [model.itemFromIndex(index) for index in selectedRowIndexes]
        selectedRows = [item.row() for item in selectedRowItems]
        self.selectedVarNames = [self.getVariableName(r) for r in selectedRows]
        #print selectedRows
        #print self.selectedVarNames


    #----------------------------------------------------------------------
    def openContextMenu(self, qpoint):
        """"""

        sender = self.sender()

        globalClickPos = sender.mapToGlobal(qpoint)

        sender.contextMenu.clear()
        if not self.selectedVarNames:

            pass

        elif len(self.selectedVarNames) == 1:

            menuStr = self.selectedVarNames[0] + ' vs. index'

            action = sender.contextMenu.addAction(Qt.QIcon(), menuStr)
            self.connect(action, Qt.SIGNAL('triggered()'),
                         self.onPlotActionTriggered)

        else:

            firstVarName = self.selectedVarNames[0]

            menuStr = '"All except ' + firstVarName + '" vs. ' + firstVarName
            action = sender.contextMenu.addAction(Qt.QIcon(), menuStr)
            action.setProperty('yVarNameList', self.selectedVarNames[1:])
            self.connect(action, Qt.SIGNAL('triggered()'),
                         self.onPlotActionTriggered)

            menuStr = '"All" vs. index'
            action = sender.contextMenu.addAction(Qt.QIcon(), menuStr)
            self.connect(action, Qt.SIGNAL('triggered()'),
                         self.onPlotActionTriggered)

            for n in self.selectedVarNames[1:]:
                menuStr = n + ' vs. ' + firstVarName
                #
                action = sender.contextMenu.addAction(Qt.QIcon(), menuStr)
                self.connect(action, Qt.SIGNAL('triggered()'),
                             self.onPlotActionTriggered)


        if sender.contextMenu.actions != []:
            sender.contextMenu.addSeparator()


        menuStr = 'Add variables from a file'
        action = sender.contextMenu.addAction(Qt.QIcon(), menuStr)
        self.connect(action, Qt.SIGNAL('triggered()'),
                     self.addVarsFromFile)
        #
        menuStr = 'Add PV (history)'
        action = sender.contextMenu.addAction(Qt.QIcon(), menuStr)
        self.connect(action, Qt.SIGNAL('triggered()'),
                     self.addPVHistory)
        #
        menuStr = 'Add PV (real-time)'
        action = sender.contextMenu.addAction(Qt.QIcon(), menuStr)
        self.connect(action, Qt.SIGNAL('triggered()'),
                     self.addPVMonitor)
        #
        menuStr = 'Add PV (history + real-time)'
        action = sender.contextMenu.addAction(Qt.QIcon(), menuStr)
        self.connect(action, Qt.SIGNAL('triggered()'),
                     self.addPVHistAndMon)
        #
        menuStr = 'Create new variable'
        action = sender.contextMenu.addAction(Qt.QIcon(), menuStr)
        self.connect(action, Qt.SIGNAL('triggered()'),
                     self.addVarsFromVars)


        sender.contextMenu.exec_(globalClickPos)

    #----------------------------------------------------------------------
    def addVarsFromFile(self):
        """"""

        caption = 'Load Data from a File'
        selectedFilterStr = ('HDF5 files (*.hdf5 *.h5)')
        filterStr = (selectedFilterStr + ';;' +
                      'All files (*)')
        qFilename = Qt.QFileDialog.getOpenFileName(
            None, caption, self.startDirPath, filterStr)
        # If you include 5th argument selectedFilter with v.2
        # PyQt API, getOpenFileName will fail. If you use v.1 API,
        # you can pass selectedFilter w/o a problem.
        filename = str(qFilename)

        self.startDirPath = filename

        try:
            self.model.load_hdf5(filename)
        except: # catch all exceptions
            msgBox = Qt.QMessageBox()
            msgBox.setText( (
                'Failed to load the HDF5 file "' + filename + '".') )
            msgBox.setInformativeText( str(sys.exc_info()) )
            msgBox.setIcon(Qt.QMessageBox.Critical)
            msgBox.exec_()
            return

    #----------------------------------------------------------------------
    def addPVHistory(self):
        """"""

        pass

    #----------------------------------------------------------------------
    def addPVMonitor(self):
        """"""

        pass

    #----------------------------------------------------------------------
    def addPVHistAndMon(self):
        """"""

        pass

    #----------------------------------------------------------------------
    def addVarsFromVars(self):
        """"""

        defaultVarNamePrefix = 'var'

        newVarName = defaultVarNamePrefix
        counter = 1
        newVarName = defaultVarNamePrefix + str(counter)
        while newVarName in self.model.varNameList:
            newVarName = defaultVarNamePrefix + str(counter)
            counter += 1
        self.model.varNameList.append(newVarName)
        self.model.derivedVarNameList.append(newVarName)
        self.model.ds[newVarName] = []
        newRow = self.model.rowCount()
        newVarNameItem = Qt.QStandardItem(newVarName)
        newVarNameItem.uncommittedDerivationExpression = ''
        newVarNameItem.srcType = 'variables'
        self.model.setItem(newRow,0,newVarNameItem)

        for propName in self.model.propNameList[1:]:
            if propName == 'origName':
                itemText = 'N/A'
                editable = False
            elif propName == 'description':
                itemText = ''
                editable = True
            elif propName == 'indepVar':
                itemText = 'index'
                editable = True
            elif propName == 'srcType':
                itemText = newVarNameItem.srcType
                editable = False
            elif propName == 'srcAddr':
                itemText = '[]'
                editable = False
            elif propName == 'srcTimeRange':
                itemText = 'N/A'
                editable = False
            elif propName == 'derivation':
                itemText = ''
                editable = True
            else:
                raise ValueError('Unexpected property name: ' + propName)
            item = Qt.QStandardItem(itemText)
            if not editable:
                item.setEditable(editable)
            self.model.setItem(newRow, self.model.col(propName), item)





    #----------------------------------------------------------------------
    def onPlotActionTriggered(self):
        """"""

        action = self.sender()
        actionText = str(action.text())
        yVarName, xVarName = actionText.split(' vs. ')

        if yVarName == ('"All except ' + xVarName + '"'):
            newFigName = self.parent().parent().getAutoGenNewFigName('')
            #yVarNameListQVariant = action.property('yVarNameList')
            #yVarNameList = [str(n.toString()) for n
                            #in yVarNameListQVariant.toList()]
            yVarNameList = action.property('yVarNameList')
            for yName in yVarNameList:
                newCurveData = {}
                d = newCurveData # for short-hand notation
                d['dispName'] = ''
                d['isVisible'] = True
                d['figName'] = newFigName
                d['canvasRowCount'] = 1
                d['canvasColCount'] = 1
                d['canvasRowPos'] = [0]
                d['canvasColPos'] = [0]
                d['xVarName'] = xVarName
                d['xAxis'] = DEF_XAXIS
                d['yVarName'] = yName
                d['yAxis'] = DEF_YAXIS
                d['lineColor'] = DEF_LINE_COLOR
                d['lineStyle'] = DEF_LINE_STYLE
                d['lineWidth'] = DEF_LINE_WIDTH
                d['marker'] = DEF_MARKER
                d['markerSize'] = DEF_MARKER_SIZE
                d['markerFaceColor'] = DEF_MARKER_FACE_COLOR
                d['markerEdgeColor'] = DEF_MARKER_EDGE_COLOR
                #d['markerEdgeWidth'] = DEF_MARKER_EDGE_WIDTH

                self.emit(Qt.SIGNAL('addNewCurve'), newCurveData)

        elif yVarName == '"All"':
            pass
        else:

            newCurveData = {}
            d = newCurveData # for short-hand notation
            d['dispName'] = ''
            d['isVisible'] = True
            d['figName'] = ''
            d['canvasRowCount'] = 1
            d['canvasColCount'] = 1
            d['canvasRowPos'] = [0]
            d['canvasColPos'] = [0]
            d['xVarName'] = xVarName
            d['xAxis'] = DEF_XAXIS
            d['yVarName'] = yVarName
            d['yAxis'] = DEF_YAXIS
            d['lineColor'] = DEF_LINE_COLOR
            d['lineStyle'] = DEF_LINE_STYLE
            d['lineWidth'] = DEF_LINE_WIDTH
            d['marker'] = DEF_MARKER
            d['markerSize'] = DEF_MARKER_SIZE
            d['markerFaceColor'] = DEF_MARKER_FACE_COLOR
            d['markerEdgeColor'] = DEF_MARKER_EDGE_COLOR
            #d['markerEdgeWidth'] = DEF_MARKER_EDGE_WIDTH

            self.emit(Qt.SIGNAL('addNewCurve'), newCurveData)


########################################################################
class ExpressionEditorDockModel(Qt.QObject):
    """"""

    #----------------------------------------------------------------------
    def __init__(self, mainView, datasetsModel):
        """Constructor"""

        Qt.QObject.__init__(self)

        self.sortedDerivedVarNameList = []

        self.mainView = mainView
        self.datasetsModel = datasetsModel



    #----------------------------------------------------------------------
    def updateSortedDerivedVarNameList(self, newDerivedVarNameList):
        """"""

        self.sortedDerivedVarNameList = newDerivedVarNameList[:]

        self.sortedDerivedVarNameList.sort() # alphabetically sorted

        self.emit(Qt.SIGNAL('varNameListChanged'))

    #----------------------------------------------------------------------
    def getUncommittedExpression(self, varName):
        """"""

        rowIndex = self.datasetsModel.varNameList.index(varName)

        varNameItem = self.datasetsModel.item(
            rowIndex, self.datasetsModel.col('name'))

        return varNameItem.uncommittedDerivationExpression


    #----------------------------------------------------------------------
    def getCommittedExpression(self, varName):
        """"""

        rowIndex = self.datasetsModel.varNameList.index(varName)

        derivationItem = self.datasetsModel.item(
            rowIndex, self.datasetsModel.col('derivation'))

        return str(derivationItem.text())



########################################################################
class ExpressionEditorDockView(Qt.QWidget):
    """"""

    #----------------------------------------------------------------------
    def __init__(self, mainView, datasetsModel):
        """Constructor"""

        Qt.QWidget.__init__(self)

        self.setObjectName('expressionEditorDockView')

        verticalLayout = Qt.QVBoxLayout(self)
        #
        self.splitter = Qt.QSplitter(self)
        sizePolicy = Qt.QSizePolicy(Qt.QSizePolicy.Expanding,
                                    Qt.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.splitter.sizePolicy().hasHeightForWidth())
        self.splitter.setSizePolicy(sizePolicy)
        self.splitter.setOrientation(Qt.Qt.Vertical)
        #
        verticalLayout.addWidget(self.splitter)
        #
        widget = Qt.QWidget(self.splitter)
        gridLayout = Qt.QGridLayout(widget)
        gridLayout.setObjectName('expressionEditorDock_gridLayout')
        horizLayout = Qt.QHBoxLayout()
        horizLayout.setObjectName('expressionEditorDock_horizLayout')
        label1 = Qt.QLabel(self)
        label1.setText('Variable Name:')
        horizLayout.addWidget(label1)
        self.comboBox_varName = Qt.QComboBox(self)
        self.comboBox_varName.setObjectName('expressionEditorDock_varName')
        self.comboBox_varName.setSizeAdjustPolicy(Qt.QComboBox.AdjustToContents)
        horizLayout.addWidget(self.comboBox_varName)
        spacerItem = Qt.QSpacerItem(25, 22, Qt.QSizePolicy.Expanding,Qt.QSizePolicy.Minimum)
        horizLayout.addItem(spacerItem)
        self.pushButton_applyChange = Qt.QPushButton(self)
        self.pushButton_applyChange.setObjectName('expressionEditorDock_applyChange')
        self.pushButton_applyChange.setText('Save && Apply Change')
        horizLayout.addWidget(self.pushButton_applyChange)
        self.pushButton_cancelChange = Qt.QPushButton(self)
        self.pushButton_cancelChange.setObjectName('expressionEditorDock_cancelChange')
        self.pushButton_cancelChange.setText('Cancel Change')
        horizLayout.addWidget(self.pushButton_cancelChange)
        gridLayout.addLayout(horizLayout, 0, 0, 1, 1)
        self.textEdit = Qt.QTextEdit(self)
        self.textEdit.setObjectName('expressionEditorDock_textEdit')
        self.textEdit.setEnabled(False)
        gridLayout.addWidget(self.textEdit, 1, 0, 1, 1)
        #
        kernelApp = embedIPython.IPythonLocalKernelApp.instance()
        kernelApp.start()
        ipythonNamespace = kernelApp.get_user_namespace()
        ipythonWidget = embedIPython.IPythonConsoleQtWidget()
        ipythonWidget.set_default_style(colors='linux')
        ipythonWidget.connect_kernel(connection_file=kernelApp.get_connection_file())
        ipythonWidget.setParent(self.splitter)
        #
        ipythonNamespace['whatever'] = [1,2,3]

        self.model = ExpressionEditorDockModel(mainView, datasetsModel)

        self.connect(self.model, Qt.SIGNAL('varNameListChanged'),
                     self.updateVarNameComboBoxItems)

        self.connect(self.comboBox_varName,
                     Qt.SIGNAL('currentIndexChanged(const QString &)'),
                     self.loadUncommittedExpression)
        self.connect(datasetsModel, Qt.SIGNAL('derivationExpChangedOnDatasets'),
                     self.loadUncommittedExpression)

        self.connect(self.textEdit,
                     Qt.SIGNAL('textChanged()'),
                     self.updateUncommittedExpressionOnDatasets)

        self.connect(self.pushButton_applyChange,
                     Qt.SIGNAL('clicked(bool)'),
                     self.commitExpressionChange)
        self.connect(self.pushButton_cancelChange,
                     Qt.SIGNAL('clicked(bool)'),
                     self.loadCommittedExpression)

    #----------------------------------------------------------------------
    def updateUncommittedExpressionOnDatasets(self):
        """"""

        varName = str(self.comboBox_varName.currentText())

        newUncommittedExpression = str(self.textEdit.toPlainText())

        self.emit(Qt.SIGNAL('uncommittedDerivationExpChanged'),
                  varName, newUncommittedExpression)



    #----------------------------------------------------------------------
    def updateVarNameComboBoxItems(self):
        """"""

        sortedDerivedVarNameList = self.model.sortedDerivedVarNameList

        selectedIndex = self.comboBox_varName.currentIndex()
        selectedText = str(self.comboBox_varName.currentText())

        self.comboBox_varName.clear()

        for n in sortedDerivedVarNameList:
            self.comboBox_varName.addItem(Qt.QIcon(), n)

        # If a new variable has been added, or a variable that is currently
        # not selected has been deleted, the selected variable name still exists
        # in sortedDerivedVarNameList. So, use the text to find the new, if changed, index.
        if selectedText in sortedDerivedVarNameList:
            newSelectedIndex = sortedDerivedVarNameList.index(selectedText)
        else:
            # If the currently selected variable has been deleted, and if the
            # selected index happens to go out of index bound of changed varNameList,
            # then set the index to -1, i.e., not selected. If the index does not
            # go out of bound, then use the currently selected index.
            # Also, use the currently selected index, in the case the selected
            # variable name has been changed.
            if selectedIndex >= len(sortedDerivedVarNameList):
                newSelectedIndex = -1
            else:
                newSelectedIndex = selectedIndex

        self.comboBox_varName.setCurrentIndex(newSelectedIndex)

    #----------------------------------------------------------------------
    def loadUncommittedExpression(self, varNameQString):
        """"""

        if varNameQString != self.comboBox_varName.currentText():
            return

        varName = str(varNameQString)

        if varName:
            uncomExpression = self.model.getUncommittedExpression(varName)
            self.textEdit.setText(uncomExpression)
            if not self.textEdit.isEnabled():
                self.textEdit.setEnabled(True)
        else:
            self.textEdit.setEnabled(False)

    #----------------------------------------------------------------------
    def loadCommittedExpression(self):
        """"""

        varNameQString = self.comboBox_varName.currentText()

        varName = str(varNameQString)

        if varName:
            committedExpression = self.model.getCommittedExpression(varName)
            self.textEdit.setText(committedExpression)

    #----------------------------------------------------------------------
    def commitExpressionChange(self):
        """"""

        varNameQString = self.comboBox_varName.currentText()

        varName = str(varNameQString)

        if varName:
            newMultilineExpression = str(self.textEdit.toPlainText())
            #newSemicolonedExpression = \
                #newMultilineExpression.replace('\n',';')

            self.emit(Qt.SIGNAL('derivationExpChangeCommittedOnEditor'),
                      varName, newMultilineExpression)





########################################################################
class PlotterModel(Qt.QObject):
    """"""

    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""

        Qt.QObject.__init__(self)



########################################################################
class PlotterView(hlaPlot.InteractivePlotWindow, Ui_MainWindow):
    """"""

    #----------------------------------------------------------------------
    def __init__(self, model):
        """Constructor"""

        hlaPlot.InteractivePlotWindow.__init__(self)

        self.model = model

        self.setupUi(self)


        self.figTabTitleList = []
        self.varNameList = []

        self.centralGridLayout = Qt.QGridLayout(self.centralwidget)
        self.tabWidget = Qt.QTabWidget(self.centralwidget)
        self.tabWidget.setObjectName('tabWidget')
        self.tabWidget.setTabsClosable(True)
        self.tabWidget.setMovable(True)
        self.tabWidget.setMinimumSize(Qt.QSize(0,0))
        self.connect(self.tabWidget,
                     Qt.SIGNAL('tabCloseRequested(int)'),
                     self.closeTab)
        self.centralGridLayout.addWidget(self.tabWidget, 0, 0, 1, 1)

        self.dockWidget_datasets.widget().deleteLater()
        self.dockView_datasets = DatasetsDockView(self)
        self.dockWidget_datasets.setWidget(self.dockView_datasets)
        #self.connect(self.dockView_datasets, Qt.SIGNAL('plotYvsX'),
                     #self.plotYvsX)
        self.varNameList = self.dockView_datasets.model.varNameList

        self.dockWidget_curves.widget().deleteLater()
        self.dockView_curves = CurvesDockView(self)
        self.dockWidget_curves.setWidget(self.dockView_curves)

        self.dockWidget_expression_editor.widget().deleteLater()
        self.dockView_expressionEditor = ExpressionEditorDockView(
            self, self.dockView_datasets.model)
        self.dockWidget_expression_editor.setWidget(self.dockView_expressionEditor)


        self.tabifyDockWidget(self.dockWidget_datasets,
                              self.dockWidget_expression_editor)
        self.tabifyDockWidget(self.dockWidget_datasets,
                              self.dockWidget_curves)
        self.tabifyDockWidget(self.dockWidget_datasets,
                              self.dockWidget_canvas_settings)
        self.tabifyDockWidget(self.dockWidget_datasets,
                              self.dockWidget_line_cursors)

        self.setTabPosition(Qt.Qt.TopDockWidgetArea,
                            Qt.QTabWidget.South)
        self.setTabPosition(Qt.Qt.BottomDockWidgetArea,
                            Qt.QTabWidget.South)
        self.setTabPosition(Qt.Qt.RightDockWidgetArea,
                            Qt.QTabWidget.South)
        self.setTabPosition(Qt.Qt.LeftDockWidgetArea,
                            Qt.QTabWidget.South)

        self.dockWidget_datasets.raise_()

        self.connect(self.dockWidget_datasets, Qt.SIGNAL('visibilityChanged(bool)'),
                     self.updateDockWidgetActionCheckState)
        self.connect(self.dockWidget_expression_editor, Qt.SIGNAL('visibilityChanged(bool)'),
                     self.updateDockWidgetActionCheckState)
        self.connect(self.dockWidget_curves, Qt.SIGNAL('visibilityChanged(bool)'),
                     self.updateDockWidgetActionCheckState)
        self.connect(self.dockWidget_canvas_settings, Qt.SIGNAL('visibilityChanged(bool)'),
                     self.updateDockWidgetActionCheckState)
        self.connect(self.dockWidget_line_cursors, Qt.SIGNAL('visibilityChanged(bool)'),
                     self.updateDockWidgetActionCheckState)

        self.actionGroupDockWidgets = Qt.QActionGroup(self)
        self.actionGroupDockWidgets.setExclusive(False)
        #
        self.actionDockWidget_datasets = Qt.QAction(Qt.QIcon(), 'Datasets',
                                                  self.actionGroupDockWidgets)
        self.actionDockWidget_datasets.setCheckable(True)
        self.actionDockWidget_datasets.setChecked(True)
        self.menuView.addAction(self.actionDockWidget_datasets)
        #
        self.actionDockWidget_expressionEditor = Qt.QAction(
            Qt.QIcon(), 'Expression Editor', self.actionGroupDockWidgets)
        self.actionDockWidget_expressionEditor.setCheckable(True)
        self.actionDockWidget_expressionEditor.setChecked(True)
        self.menuView.addAction(self.actionDockWidget_expressionEditor)
        #
        self.actionDockWidget_curves = Qt.QAction(Qt.QIcon(), 'Curves',
                                                  self.actionGroupDockWidgets)
        self.actionDockWidget_curves.setCheckable(True)
        self.actionDockWidget_curves.setChecked(True)
        self.menuView.addAction(self.actionDockWidget_curves)
        #
        self.actionDockWidget_canvasSettings = Qt.QAction(
            Qt.QIcon(), 'Canvas Settings', self.actionGroupDockWidgets)
        self.actionDockWidget_canvasSettings.setCheckable(True)
        self.actionDockWidget_canvasSettings.setChecked(True)
        self.menuView.addAction(self.actionDockWidget_canvasSettings)
        #
        self.actionDockWidget_cursors = Qt.QAction(
            Qt.QIcon(), 'Cursors', self.actionGroupDockWidgets)
        self.actionDockWidget_cursors.setCheckable(True)
        self.actionDockWidget_cursors.setChecked(True)
        self.menuView.addAction(self.actionDockWidget_cursors)
        #
        self.connect(self.actionGroupDockWidgets, Qt.SIGNAL('triggered(QAction *)'),
                     self.onDockWidgetActionGroupTriggered)

        self.menuTools.addActions(self.hlaPlotToolsMenu.actions())

        self.connect(self.dockView_curves.model, Qt.SIGNAL('newCurveAdded'),
                     self.addInteractiveTools)

        self.connect(self.tabWidget, Qt.SIGNAL('currentChanged(int)'),
                     self.onTabWidgetCurrentChanged)

        self.connect(self.dockView_datasets.model,
                     Qt.SIGNAL('datasetsChanged'),
                     self.propagateDatasetsChange)

        self.connect(self.dockView_datasets,
                     Qt.SIGNAL('addNewCurve'),
                     self.dockView_curves.model.addNewCurve)

        self.connect(self.dockView_expressionEditor,
                     Qt.SIGNAL('derivationExpChangeCommittedOnEditor'),
                     self.dockView_datasets.model.commitDerivationExpChange)
        self.connect(self.dockView_expressionEditor,
                     Qt.SIGNAL('uncommittedDerivationExpChanged'),
                     self.dockView_datasets.model.changeUncommittedExpression)

    #----------------------------------------------------------------------
    def propagateDatasetsChange(self, datasetsModelIndex):
        """"""

        oldVarName, newVarName = \
            self.dockView_datasets.model.updateVarNameList(datasetsModelIndex)

        if oldVarName:
            self.dockView_curves.model.updateVarName(oldVarName, newVarName)
            self.dockView_expressionEditor.model.updateSortedDerivedVarNameList(
                self.dockView_datasets.model.derivedVarNameList)

    #----------------------------------------------------------------------
    def addInteractiveTools(self, qwtPlot, xAxis, yAxis):
        """"""

        figTab = qwtPlot.parent()

        existingZoomers = qwtPlot.findChildren(hlaPlot.PlotZoomer)
        alreadyZoomerExists = [(z.xAxis() == xAxis) and (z.yAxis() == yAxis)
                              for z in existingZoomers]
        if not any(alreadyZoomerExists):
            zoomer = hlaPlot.PlotZoomer(xAxis, yAxis,
                                        Qwt.QwtPicker.DragSelection,
                                        Qwt.QwtPicker.AlwaysOff,
                                        qwtPlot.canvas())
            zoomer.setRubberBandPen(Qt.QPen(Qt.Qt.black))
            # MouseSelect1 = Zoom in to a user specified rectangle
            # --- No change necessary
            # MouseSelect2 = Zoom back to zoomBase
            # --- Change form the default "RightClick" action to "Ctrl+RightClick"
            zoomer.setMousePattern(Qwt.QwtEventPattern.MouseSelect2,
                                   Qt.Qt.RightButton, Qt.Qt.ControlModifier)
            # MouseSelect3 = Zoom back to one previous zoom state
            # --- Change to "RightClick"
            zoomer.setMousePattern(Qwt.QwtEventPattern.MouseSelect3,
                                   Qt.Qt.RightButton, Qt.Qt.NoButton)
            zoomer.resetZoomStack()
            zoomer.setEnabled(False)
            #
            figTab.zoomers.append(zoomer)

            currentFont = self.fontInfo().family()
            linkedDataCursorMarker = Qwt.QwtPlotMarker()
            linkedDataCursorMarker.setValue(7.17,0.53)
            text = Qwt.QwtText('test')
            text.setFont(Qt.QFont(currentFont, 12, Qt.QFont.Bold))
            text.setColor(Qt.Qt.blue)
            text.setBackgroundBrush(Qt.QBrush(Qt.Qt.yellow))
            text.setBackgroundPen(Qt.QPen(Qt.Qt.red,2))
            linkedDataCursorMarker.setLabel(text)
            linkedDataCursorMarker.setSymbol(
                Qwt.QwtSymbol(Qwt.QwtSymbol.Ellipse, # Marker Type (None, Ellipse, Rect, Diamond)
                              Qt.QBrush(Qt.Qt.green), # Fill Color (Use "Qt.QBrush()" if you want transparent)
                              Qt.QPen(Qt.Qt.black, 6), # Edge Color & Edge Thickness (Use "Qt.QPen()" if you want transparent
                              Qt.QSize(5,5))) # Marker Size (Horizontal Size, Vertical Size)
            linkedDataCursorMarker.setVisible(False)
            linkedDataCursorMarker.attach(qwtPlot)
            dataCursor = hlaPlot.PlotDataCursor(
                linkedDataCursorMarker, xAxis, yAxis,
                Qwt.QwtPicker.PointSelection, Qwt.QwtPlotPicker.NoRubberBand,
                Qwt.QwtPicker.AlwaysOff,
                qwtPlot.canvas())
            dataCursor.setEnabled(False)
            #
            figTab.dataCursors.append(dataCursor)

            selectionHighlighterCurve = hlaPlot.PlotCurve('Selection Highlighter')
            selectionHighlighterCurve.setStyle(Qwt.QwtPlotCurve.NoCurve) # Line Connection Type (Lines, NoCurve, Sticks, Steps)
            #selectionHighlighterCurve.setStyle(Qwt.QwtPlotCurve.Lines) # Line Connection Type (Lines, NoCurve, Sticks, Steps)
            #selectionHighlighterCurve.setPen(Qt.QPen(hlaPlot.getQtColor('white'),
                                                     #0.5,
                                                     #Qt.Qt.SolidLine))
            selectionHighlighterCurve.setSymbol(Qwt.QwtSymbol(Qwt.QwtSymbol.Rect, # Marker Type (None, Ellipse, Rect, Diamond)
                                                              Qt.QBrush(Qt.Qt.white), # Fill Color (Use "Qt.QBrush()" if you want transparent)
                                                              Qt.QPen(Qt.Qt.black, 1), # Edge Color & Edge Thickness (Use "Qt.QPen()" if you want transparent
                                                              Qt.QSize(5,5))) # Marker Size (Horizontal Size, Vertical Size)
            selectionHighlighterCurve.setVisible(False)
            selectionHighlighterCurve.attach(qwtPlot)
            #
            plotEditor = hlaPlot.PlotEditor(selectionHighlighterCurve,
                                            xAxis, yAxis,
                                            Qwt.QwtPicker.PointSelection,
                                            Qwt.QwtPlotPicker.NoRubberBand,
                                            Qwt.QwtPicker.AlwaysOff,
                                            qwtPlot.canvas())
            plotEditor.setEnabled(False)
            #
            figTab.plotEditors.append(plotEditor)

        existingPanner = qwtPlot.findChildren(hlaPlot.PlotPanner)
        if not existingPanner:
            panner = hlaPlot.PlotPanner(qwtPlot.canvas())
            panner.setEnabled(False)
            #
            figTab.panners.append(panner)




    #----------------------------------------------------------------------
    def onTabWidgetCurrentChanged(self, currentTabIndex):
        """"""

        figTab = self.tabWidget.widget(currentTabIndex)

        if figTab:
            self.zoomers     = figTab.zoomers
            self.panners     = figTab.panners
            self.dataCursors = figTab.dataCursors
            self.plotEditors = figTab.plotEditors

            self.updateToolbarEnableStates()
        else: # All tabs have been closed
            for a in self.actionGroup.actions:
                a.setChecked(False)


    #----------------------------------------------------------------------
    def updateDockWidgetActionCheckState(self, visibleUnblocked_NotUsed):
        """
        visibleUnblocked_NotUsed will be False, even if the sender dock widget
        is visible but the view is blocked by other dock widgets, like when
        the dock widgets are tabified. So, for the check state update, we need
        to actually use "isVisible()" function.
        """

        sender = self.sender()
        visible = sender.isVisible()

        if sender == self.dockWidget_datasets:
            self.actionDockWidget_datasets.setChecked(visible)
        elif sender == self.dockWidget_expression_editor:
            self.actionDockWidget_expressionEditor.setChecked(visible)
        elif sender == self.dockWidget_curves:
            self.actionDockWidget_curves.setChecked(visible)
        elif sender == self.dockWidget_canvas_settings:
            self.actionDockWidget_canvasSettings.setChecked(visible)
        elif sender == self.dockWidget_line_cursors:
            self.actionDockWidget_cursors.setChecked(visible)
        else:
            raise ValueError('Unexpected dock widget as sender')

    #----------------------------------------------------------------------
    def onDockWidgetActionGroupTriggered(self, action):
        """"""

        if action == self.actionDockWidget_datasets:
            dockWidget = self.dockWidget_datasets
        elif action == self.actionDockWidget_expressionEditor:
            dockWidget = self.dockWidget_expression_editor
        elif action == self.actionDockWidget_curves:
            dockWidget = self.dockWidget_curves
        elif action == self.actionDockWidget_canvasSettings:
            dockWidget = self.dockWidget_canvas_settings
        elif action == self.actionDockWidget_cursors:
            dockWidget = self.dockWidget_line_cursors
        else:
            raise ValueError('Unexpected dock view action.')

        if action.isChecked():
            dockWidget.show()
            dockWidget.raise_()
        else:
            dockWidget.hide()


    #----------------------------------------------------------------------
    def gcc(self):
        """
        (G)et (C)urrent (C)anvas

        """

        return None


    ##----------------------------------------------------------------------
    #def plotYvsX(self, yVarName, xVarName, qwtPlot):
        #""""""

        #newCurve = halPlot.PlotCurve(yVarName)

        #if not qwtPlot:
            #newTab = self.addNewFigTab()
            #qwtPlot = newTab.qwtPlots[0][0]
            #qwtPlot.setCanvasBackground(Qt.Qt.white)
            #qwtPlot.setAxisTitle(Qwt.QwtPlot.xBottom, xVarName)
            #qwtPlot.setAxisTitle(Qwt.QwtPlot.yLeft, yVarName)
            #qwtPlot.setAxisAutoScale(Qwt.QwtPlot.xBottom)
            #qwtPlot.setAxisAutoScale(Qwt.QwtPlot.yLeft)
            #qwtPlot.setAutoReplot()
            ##
            #qwtPlot.curves = [newCurve]
        #else:
            #qwtPlot.curves.append(newCurve)

        #newCurve.setPen(Qt.QPen(Qt.Qt.blue,
                                #0.5,
                                #Qt.Qt.SolidLine))
        #newCurve.setStyle(Qwt.QwtPlotCurve.Lines)
        #newCurve.setSymbol(Qwt.QwtSymbol(Qwt.QwtSymbol.Ellipse,
                                         #Qt.QBrush(Qt.Qt.blue),
                                         #Qt.QPen(Qt.Qt.black, 1),
                                         #Qt.QSize(2,2)))
        #newCurve.attach(qwtPlot)

        #newCurve.setData(self.dockView_datasets.model.ds[xVarName],
                         #self.dockView_datasets.model.ds[yVarName])

        ## Set the figure tab that contains the canvas as the current tab
        #self.raiseCanvas(qwtPlot)

    #----------------------------------------------------------------------
    def raiseCanvas(self, qwtPlot):
        """
        Set the figure tab that contains the canvas as the current tab
        """

        self.tabWidget.setCurrentWidget(qwtPlot.parent())

    #----------------------------------------------------------------------
    def getAutoGenNewFigName(self, userSuggestedFigName):
        """"""

        if userSuggestedFigName:
            counter = 1
            newFigName = userSuggestedFigName + '(dup ' + str(counter) + ')'
            while newFigName in self.figTabTitleList:
                counter += 1
                newFigName = userSuggestedFigName + '(dup ' + str(counter) + ')'
        else:
            counter = 1
            newFigName = 'Fig. ' + str(counter)
            while newFigName in self.figTabTitleList:
                counter += 1
                newFigName = 'Fig ' + str(counter)

        return newFigName


    #----------------------------------------------------------------------
    def addNewFigTab(self, figName = ''):
        """"""

        figureTab = FigureTab()

        if figName:

            if figName in self.figTabTitleList: # If specified figure name has a conflict
                # with the existing figure names, then modify the given name so that there
                # will be no conflict.
                self.getAutoGenNewFigName(figName)
            else:
                figureTab.title = figName

        else: # Auto-generate figure name, since no name was specified for the new figure tab.
            figureTab.title = self.getAutoGenNewFigName(figName)



        self.figTabTitleList.append(figureTab.title)
        self.tabWidget.addTab(figureTab, figureTab.title)

        self.tabWidget.setCurrentIndex(self.tabWidget.count())

        return figureTab

    #----------------------------------------------------------------------
    def closeTab(self, tabIndex):
        """"""

        w = self.tabWidget.widget(tabIndex)

        self.figTabTitleList.remove(w.title)

        w.deleteLater()

        self.tabWidget.removeTab(tabIndex)



    #----------------------------------------------------------------------
    def getQwtPlot(self, figName, rowCount, colCount,
                  rowPos, colPos):
        """"""

        if not figName:
            tab = self.addNewFigTab()
        else:
            if figName in self.figTabTitleList:
                tabIndex = self.figTabTitleList.index(figName)
                tab = self.tabWidget.widget(tabIndex)
            else:
                tab = self.addNewFigTab(figName)

        newCanvasRCIndex = []
        for r in range(rowPos[0], rowPos[-1]+1):
            for c in range(colPos[0], colPos[-1]+1):
                newCanvasRCIndex.append([r,c])

        layoutItem = tab.gridLayout.itemAtPosition(
            rowPos[0], colPos[0])
        if layoutItem:
            qwtPlot = layoutItem.widget()
        else: # When the specified cell is empty, create a new canvas (QwtPlot object) there
            for r in range(rowCount):
                for c in range(colCount):
                    if [r,c] in newCanvasRCIndex:
                        continue # Since this cell will be occupied by the new
                        # canvas, this space will be left empty.
                    layoutItem = tab.gridLayout.itemAtPosition(r, c)
                    if not layoutItem:
                        qwtPlot = Qwt.QwtPlot(tab)
                        qwtPlot.setSizePolicy(Qt.QSizePolicy.Ignored,
                                              Qt.QSizePolicy.Ignored)
                        qwtPlot.setCanvasBackground(Qt.Qt.white)
                        tab.gridLayout.addWidget(qwtPlot, r, c, 1, 1)

            qwtPlot = Qwt.QwtPlot(tab)
            qwtPlot.setSizePolicy(Qt.QSizePolicy.Ignored,
                                  Qt.QSizePolicy.Ignored)
            qwtPlot.setCanvasBackground(Qt.Qt.white)
            tab.gridLayout.addWidget(qwtPlot,rowPos[0],colPos[0],
                                     len(rowPos),len(colPos))

        return qwtPlot



########################################################################
class PlotterApp(Qt.QObject):
    """"""

    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""

        Qt.QObject.__init__(self)

        self._initModel()
        self._initView(self.model)


    #----------------------------------------------------------------------
    def _initModel(self):
        """"""

        self.model = PlotterModel()

    #----------------------------------------------------------------------
    def _initView(self, model):
        """"""

        self.view = PlotterView(model)

#----------------------------------------------------------------------
def make():
    """"""

    app = PlotterApp()
    app.view.show()

    return app


#----------------------------------------------------------------------
def main(args = None):
    """ """

    if 'cothread' in globals().keys():
        using_cothread = True
    else:
        using_cothread = False

    if using_cothread:
        # If Qt is to be used (for any GUI) then the cothread library needs to be informed,
        # before any work is done with Qt. Without this line below, the GUI window will not
        # show up and freeze the program.
        # Note that for a dialog box to be modal, i.e., blocking the application
        # execution until user input is given, you need to set the input
        # argument "user_timer" to be True.
        cothread.iqt()
    else:
        qapp = Qt.QApplication(args)


    app = PlotterApp()
    app.view.show()

    if using_cothread:
        cothread.WaitForQuit()
    else:
        exit_status = qapp.exec_()
        sys.exit(exit_status)


#----------------------------------------------------------------------
if __name__ == "__main__" :
    main(sys.argv)
