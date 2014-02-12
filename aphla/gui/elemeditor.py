"""
Element Property Editor
=======================

:author: Lingyun Yang <lyyang@bnl.gov>

list all properties of element, provide editing.

A table view for HLA element, with delegates user can modify value online
"""

import cothread

if __name__ == "__main__":
    app = cothread.iqt()
    import aphla

from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import (QAbstractTableModel, QDataStream, QFile,
        QIODevice, QModelIndex, QRegExp, QSize, QString, QVariant, Qt,
        SIGNAL, QEvent)
from PyQt4.QtGui import (QColor, QComboBox, QLineEdit, QDoubleSpinBox,
        QSpinBox, QStyle, QStyledItemDelegate, QTextDocument, QTextEdit, 
        QDialog, QDockWidget, QGroupBox, QPushButton, QHBoxLayout, 
        QGridLayout, QVBoxLayout, QTableView, QWidget, QApplication,
        QTableWidget, QDialogButtonBox, QStatusBar, QTableWidgetItem,
        QFormLayout, QLabel, QSizePolicy, QCompleter, QMenu, QAction)
import PyQt4.Qwt5 as Qwt
from fnmatch import fnmatch
from pvmanager import CaDataMonitor
#from aporbitplot import ApPlot
import traceback
import collections
import numpy as np
import sys, time
from functools import partial
import qrangeslider

import aphla

C_ELEM, C_FIELD, C_VAL_SP, C_VAL_RB = range(4)
_DBG_VERBOSE = 1

import logging
_logger = logging.getLogger(__name__)

#
#
class ElementPropertyTableModel(QAbstractTableModel):
    def __init__(self, **kwargs):
        super(ElementPropertyTableModel, self).__init__()
        # elem obj, idx, name/fld
        self._unitsys  = ['phy']
        self._unitsymb = []
        self._data     = []
        self._block    = [] # block of fields for one element
        self._inactive = []
        self._pvidx = {} # map pv to row,column,idx
        self._pvlst = [] # map row to pv list
        self._deadpvs = set()

    def clear(self):
        idx0 = self.index(0, 0)
        idx1 = self.index(len(self._data) - 1, self.columnCount()-1)
        self._data   = []
        self._pvidx  = {}
        self._pvlst  = []
        self.emit(SIGNAL("dataChanged(QModelIndex,QModelIndex)"),
                  idx0, idx1)

    def loadElements(self, rows):
        """
        elemplist - a list of (elem obj, field). *field=None* means separator.
        """
        self.beginResetModel()
        self.clear()
        for i, (elem, fld) in enumerate(rows):
            pvsp = elem.pv(field=fld, handle="setpoint")
            for j,pv in enumerate(pvsp):
                self._pvidx.setdefault(pv, [])
                self._pvidx[pv].append((i,C_VAL_SP,j))
            pvrb = elem.pv(field=fld, handle="readback")
            for j,pv in enumerate(pvrb):
                self._pvidx.setdefault(pv, [])
                self._pvidx[pv].append((i,C_VAL_RB,j))

            rec = [elem, fld, [None] * len(pvsp), [None] * len(pvrb)]
            for j,s in enumerate(self._unitsys):
                rec.append([None] * len(pvrb))
            self._data.append(rec)
            self._pvlst.append(pvsp + pvrb)

        if len(rows) > 0:
            self._block = [0]
            k = 0
            for i in range(1, len(rows)):
                elem, fld = rows[i]
                if elem != rows[i-1][0]:
                    k += 1
                self._block.append(k)
        self.updateData(0, len(self._data))
        self.endResetModel()

    def getElementField(self, row):
        return self._data[row][:2]

    def checkDeadPvs(self):
        if len(self._deadpvs) == 0: return
        pvs = list(self._deadpvs)
        vals = aphla.catools.caget(pvs, timeout=2)
        for i,val in enumerate(vals):
            if val.ok: self._deadpvs.remove(pvs[i])

    def updateData(self, row0, row1):
        pvs = reduce(lambda a,b: a + b,
                     [self._pvlst[i] for i in range(row0, row1)])
        pvs = [pv for pv in pvs if pv not in self._deadpvs]
        vals = aphla.catools.caget(pvs)
        for ipv,pv in enumerate(pvs):
            if not vals[ipv].ok:
                self._deadpvs.add(pv)
                continue
            for i,j,k in self._pvidx[pv]:
                self._data[i][j][k] = vals[ipv]
                if j == C_VAL_RB:
                    elem, fld = self._data[i][:2]
                    for isys, usys in enumerate(self._unitsys):
                        if usys not in elem.getUnitSystems(field=fld):
                            self._data[i][j+isys+1][k] = ''
                            continue
                        self._data[i][j+isys+1][k] = \
                            elem.convertUnit(fld, val, None, usys)
        idx0 = self.index(row0, C_VAL_SP)
        idx1 = self.index(row1-1, self.columnCount()-1)
        self.emit(SIGNAL("dataChanged(QModelIndex,QModelIndex)"),
                  idx0, idx1)
        #QtGui.qApp.processEvents()

    def _cell_to_qv(self, i, j):
        # assume it is a cadata
        if len(self._data[i][j]) == 0:
            return QVariant()
        elif len(self._data[i][j]) > 1:
            return QVariant("...")

        # size 1
        val = self._data[i][j][0]
        if val is None:
            return QVariant(QString("Disconnected"))
        elif isinstance(val, (float, np.float32)):
            return QVariant(float(val))
        elif isinstance(val, str):
            return QVariant(QString(val))
        elif isinstance(val, int):
            return QVariant(int(val))
        elif isinstance(val, (list, tuple)):
            return [self._cadata_to_qvariant(v) for v in val]
        elif isinstance(val, cothread.dbr.ca_array):
            return [self._cadata_to_qvariant(v) for v in val]
        elif not val.ok:
            return QVariant(QString("Disconnected"))
        else:
            raise RuntimeError("Unknow data type: {0} ({1})".format(
                    type(val), val))


    def isSubHeader(self, i):
        return self._data[i][1] is None

        
    def data(self, index, role=Qt.DisplayRole):
        """return data as a QVariant"""
        #print "data model=",role
        if not index.isValid() or index.row() >= len(self._data):
            return QVariant()

        r, col  = index.row(), index.column()
        elem, fld = self._data[r][:2]
        if role == Qt.DisplayRole:
            #print r, col, self._data[r]
            if col == C_ELEM:
                return QVariant(QString(elem.name))
            elif col == C_FIELD:
                return QVariant(QString(fld))
            return self._cell_to_qv(r, col)
        #elif role == Qt.EditRole:
        #    if col == C_FIELD: 
        #        raise RuntimeError("what is this ?")
        #        return QVariant(self._field[r]+self._fieldpfx[r])
        #    #print r, col, self._field[r], self._value[r]
        #    if vals is None: return QVariant()
        #    if isinstance(vals[col-1], (tuple, list)):
        #        return QVariant.fromList([QVariant(v) for v in vals[col-1]])
        #    elif vals[col-1] is not None:
        #        return QVariant(vals[col-1])
        elif role == Qt.TextAlignmentRole:
            if col == C_FIELD: return QVariant(Qt.AlignLeft | Qt.AlignVCenter)
            else: return QVariant(Qt.AlignRight | Qt.AlignBottom)
        elif role == Qt.ToolTipRole:
            if col == C_ELEM or col == C_FIELD:
                return QVariant("{0}, sb={1}, L={2}".format(
                    elem.family, elem.sb, elem.length))
            elif col == C_VAL_SP:
                pv = elem.pv(field=fld, handle="setpoint")
                return QVariant(", ".join(pv))
            elif col == C_VAL_RB:
                pv = elem.pv(field=fld, handle="readback")
                return QVariant(", ".join(pv))
            #elif col > C_VAL_RB:
            #    return QVariant(self._unitsymb[col-C_VAL_RB][r])
        elif role == Qt.ForegroundRole:
            #if idx == 0: return QColor(Qt.darkGray)
            #if r in self._inactive and self.isHeadIndex(r):
            #    return QColor(Qt.darkGray)
            #elif r in self._inactive:
            #    return QColor(Qt.lightGray)
            #else: return QColor(Qt.black)
            return QVariant()
        elif role == Qt.BackgroundRole:
            if self._block[r] % 2 == 0: return QVariant()
            else: return QColor(0xE0, 0xE0, 0xE0)
        elif role == Qt.CheckStateRole:
            #if vals is not None: return QVariant()
            #elif r in self._inactive: return Qt.Unchecked
            #else: return Qt.Checked 
            #if idx == 0 and col == C_FIELD: return Qt.Checked
            return QVariant()
        else:
            return QVariant()
        #print "Asking data role=", role
        return QVariant()

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.TextAlignmentRole:
            if orientation == Qt.Horizontal:
                return QVariant(int(Qt.AlignLeft|Qt.AlignVCenter))
            return QVariant(int(Qt.AlignRight|Qt.AlignVCenter))
        if role != Qt.DisplayRole:
            return QVariant()
        if orientation == Qt.Horizontal:
            #print "Section:", section, C_VAL_RB
            if section == C_FIELD: return QVariant("Field")
            elif section == C_VAL_SP: return QVariant("Setpoint")
            elif section == C_VAL_RB: return QVariant("Readback")
            elif section > C_VAL_RB and section < C_VAL_RB + len(self._unitsys):
                return QVariant(self._unitsys[section-1-C_VAL_RB])
            else:
                return QVariant()
        elif orientation == Qt.Vertical:
            #if self._value[section] is not None: return QVariant()
            #idx = [k for k in range(section+1) if self._value[k] is None]
            #return QVariant(len(idx))
            return QVariant(section)

        #return QVariant(int(section+1))
        return QVariant()

    def flags(self, index):
        #print "flags:", 
        if not index.isValid():
            return Qt.ItemIsEnabled
        row, col = index.row(), index.column()
        elem, fld = self._data[row][:2]

        if col == C_VAL_SP and fld is not None:
            return Qt.ItemFlags(QAbstractTableModel.flags(self, index) |
                                Qt.ItemIsSelectable)
            #return Qt.ItemFlags(QAbstractTableModel.flags(self, index) |
            #    Qt.ItemIsEditable)
        return Qt.ItemIsEnabled
        
    def rowCount(self, index=QModelIndex()):
        return len(self._data)
    
    def columnCount(self, index=QModelIndex()):
        return C_VAL_RB + len(self._unitsys) + 1


    def setElementActive(self, irow, active = True):
        rows = self._element_block(irow)
        if active:
            for i in rows:
                if i not in self._inactive: continue
                self._inactive.remove(i)
        else:
            for i in rows:
                if i in self._inactive: continue
                self._inactive.add(i)

    def isActive(self, irow):
        return irow not in self._inactive

    
class ElementPropertyDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super(ElementPropertyDelegate, self).__init__(parent)
        self._modified = False

    def paint(self, painter, option, index):
        #if index.column() == SETPOINT:
        #print index.row(), index.column()
        model = index.model()
        row, col = index.row(), index.column()
        if index.column() == 0 and model.isSubHeader(index.row()):
            QStyledItemDelegate.paint(self, painter, option, index)
            return
            text = model.data(index).toString()
            palette = QApplication.palette()
            document = QTextDocument()
            document.setDefaultFont(option.font)
            document.setHtml(text)
            color = Qt.lightGray #palette.highlight().color()
            
            painter.save()
            painter.fillRect(option.rect, color)
            painter.translate(option.rect.x(), option.rect.y())
            document.drawContents(painter)
            painter.restore()
        # elif index.column() > 0 and \
        #         isinstance(model._value[row][col-1], collections.Iterable):
        #     palette = QApplication.palette()
        #     document = QTextDocument()
        #     document.setDefaultFont(option.font)
        #     document.setHtml("<font><b>...</b></font>")
        #     #color = Qt.lightGray #palette.highlight().color()
            
        #     painter.save()
        #     #painter.fillRect(option.rect, color)
        #     painter.translate(option.rect.x(), option.rect.y())
        #     document.drawContents(painter)
        #     painter.restore()            
        else:
            QStyledItemDelegate.paint(self, painter, option, index)
        
    def sizeHint(self, option, index):
        fm = option.fontMetrics
        row, col = index.row(), index.column()
        model = index.model()
        if not model:
            return QStyledItemDelegate.sizeHint(self, option, index)

        if col == 0 and model.isSubHeader(row):
            # the element name
            return QSize(1, fm.height())
        else:
            text = index.model().data(index).toString()
            document = QTextDocument()
            document.setDefaultFont(option.font)
            document.setHtml(text)
            sz = max(document.idealWidth(), 15)
            if col == 0:
                return QSize(document.idealWidth(), fm.height())
            else:
                return QSize(sz, fm.height())
            
        return QStyledItemDelegate.sizeHint(self, option, index)

    def createEditor(self, parent, option, index):

        # bypass for now
        return QStyledItemDelegate.createEditor(self, parent, option, index)

        row, col = index.row(), index.column()
        model = index.model()
        #print "Creating editor", row, col, \
        #    [(type(v),v) for v in model._value[row]]

        self._modified = False

        if not (model.flags(index) & Qt.ItemIsEditable):
            return QStyledItemDelegate.createEditor(self, parent, option,
                                                    index)
        
        # ignore if no value stored
        if model._value[row] is None:
            return QStyledItemDelegate.createEditor(self, parent, option,
                                                    index)
        # a list value (waveform)
        if isinstance(model._value[row][col-1], collections.Iterable):
            _logger.warn("Ignore list type values for (%d,%d)" % (row, col))
            return QStyledItemDelegate.createEditor(self, parent, option,
                                                    index)

        if not isinstance(model._value[row][col-1], (int, float)):
            print "Can not create editor"
            return QStyledItemDelegate.createEditor(self, parent, option,
                                                    index)

        elem, fld = model._data[row][:2]
        elem.updateBoundary()
        bd = elem.boundary(fld)
        ss = elem.stepSize(fld)

        #if any([v is None for v in (bd[0], bd[1], ss)]):
        if True:
            led = QLineEdit(parent)
            led.setText("")
            led.setAlignment(Qt.AlignRight|Qt.AlignVCenter)
            self.connect(led, SIGNAL("returnPressed()"),
                         self.commitAndCloseEditor)
            #self.lblRange.setText("[ {0}, {1} ] / {2}".format(
            #        bd[0], bd[1], elem.stepSize(fld)))
            #self.lblStep.setText("{0}".format(elem.stepSize(fld)))
            return led
        else:
            slider = Qwt.QwtSlider(parent)
            ss = min(ss, (bd[1]-bd[0])/100)
            slider.setRange(bd[0], bd[1], ss)
            slider.setValue(model._value[row][col-1])
            #slider.setBorderWidth(1)
            #slider.setThumbWidth(20)
            slider.setScaleMaxMinor(10)
            return slider


    def commitAndCloseEditor(self):
        editor = self.sender()
        self._modified = True
        #print "commit and close:", editor.text()
        #if isinstance(editor, (QTextEdit, QLineEdit)):
        #    self.emit(SIGNAL("commitData(QWidget*)"), editor)
        #    self.emit(SIGNAL("closeEditor(QWidget*)"), editor)

    def setEditorData(self, editor, index):
        row, col = index.row(), index.column()
        if row == C_FIELD:
            return QStyledItemDelegate.setEditorData(self, editor, index)

        val = index.model().data(index, Qt.EditRole)

        #elem, fld, hdl = index.model()._elemrec[row]
        #elem.updateBoundary()
        #bd = elem.boundary(fld)
        #if self.valmeter and bd:
        #    vdbl, ok = val.toFloat()
        #    if ok and bd[0] and bd[1]:
        #        self.valmeter.setRange(bd[0], bd[1])
        #        self.valmeter.setValue(vdbl)
        #        self.valmeter.setVisible(True)
        #print "Setting editor to", text, index.model()._value[r]
        if isinstance(editor, QLineEdit):
            text = val.toString()
            #print "    set editor ", editor, "to", text
            editor.setText(text)
        elif isinstance(editor, Qwt.QwtSlider):
            value, err = val.toFloat()
            #print "slider value:", value
            #value = index.model().data(index, Qt.DisplayRole)
            editor.setValue(value)
        else:
            _logger.error("unknown editor, can not set its data")

        self.emit(SIGNAL("editingElement(PyQt_PyObject)"), 
                  index.model()._elemrec[row])

    def setModelData(self, editor, model, index):
        """copy data from editor to model"""
        #if _DBG_VERBOSE: print "updating model data", editor.text(),
        #print "  sender", self.sender()
        #traceback.print_stack(file=sys.stdout)
        row, col = index.row(), index.column()
        if row == C_FIELD:
            #if _DBG_VERBOSE: print "skip"
            return QStyledItemDelegate.setModelData(self, editor, model, index)

        if not self._modified: return
        if isinstance(editor, QLineEdit):
            model.setData(index, QVariant(editor.text()))
            #if _DBG_VERBOSE: print "done"
        elif isinstance(editor, Qwt.QwtSlider):
            model.setData(index, QVariant(editor.value()))
            #if _DBG_VERBOSE: print "done"
        else:
            #if _DBG_VERBOSE: print "skip"
            pass

    def editorEvent(self, event, model, option, index):
        #print "editor event"
        #if event.type() == QEvent.MouseButtonDblClick:
        #    # read-only ?
        #    if model.flags(index) & Qt.ItemIsEditable: mode = 'w'
        #    else: mode = 'r'
        #    #print mode
        #    data = model.data(index, role=Qt.EditRole)
        #    fm = SimpleListDlg(datalist=data, mode = mode)
        #    fm.setModal(True)
        #    fm.exec_()
        #    if fm.values:
        #        #print fm.values
        #        vals = QVariant.fromList([QVariant(d) for d in fm.values])
        #        model.setData(index, vals)
        #    return True

        return QStyledItemDelegate.editorEvent(
            self, event, model, option, index)

    def updateEditorGeometry(self, editor, opt, index):
        #print "geometry:", opt.rect
        #opt.rect.adjust(0, 30, 100, 60)
        QStyledItemDelegate.updateEditorGeometry(self, editor, opt, index)

        
class ElementPropertyView(QTableView):
    def __init__(self, parent = None):
        QTableView.__init__(self, parent)

    def disableElement(self, checked=True, irow=-1):
        if irow < 0: return
        print "Disable element:", irow
        self.model().setElementActive(irow, not checked)


    def contextMenuEvent(self, e):
        mdl = self.model()
        irow = self.rowAt(e.y())
        icol = self.columnAt(e.x())
        #print "Row:", self.rowAt(e.y())
        cmenu = QMenu()
        m_dis = QAction("disabled", self)
        m_dis.setCheckable(True)
        act = mdl.isActive(irow)
        c = QApplication.clipboard()
        if not act:
            m_dis.setChecked(True)

        self.connect(m_dis, SIGNAL("toggled(bool)"),
                     partial(self.disableElement, irow=irow))
        if icol in [C_VAL_SP, C_VAL_RB]:
            pvs = mdl.data(self.indexAt(e.pos()), Qt.ToolTipRole).toString()
            cmenu.addAction(
                "&Copy PV",
                partial(c.setText, pvs), "CTRL+C")
                            
        cmenu.addAction(m_dis)
        cmenu.exec_(e.globalPos())

class ElementEditor(QtGui.QDialog):
    def __init__(self, parent = None):
        super(ElementEditor, self).__init__(parent)
        #self.cadata = cadata
        #self.model = None
        fmbox = QFormLayout()

        self.elemName = QLineEdit()
        self.elemName.setToolTip(
            "list elements within the range of the active plot.<br>"
            "Examples are '*', 'HCOR', 'BPM', 'QUAD', 'c*c20a', 'q*g2*'"
            )
        self.elemName.setCompleter(QCompleter([
            "*", "BPM", "COR", "HCOR", "VCOR", "QUAD"]))

        self.elemField = QLineEdit()
        self.elemField.setToolTip(
            "Element fields separated by comma, space or both."
            "e.g. 'x, y'"
            )

        #self.rangeSlider = qrangeslider.QRangeSlider()
        #self.rangeSlider.setMin(0)
        #self.rangeSlider.setMax(100)
        #self.rangeSlider.setRange(10, 70)
        #self.elemName.insertSeparator(len(self.elems))
        #fmbox.addRow("Range", self.rangeSlider)
        fmbox.addRow("Elements:", self.elemName)
        fmbox.addRow("Fields:", self.elemField)
        fmbox.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)
        fmbox.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        #self.refreshBtn = QPushButton("refresh")
        #fmbox.addRow(self.elemName)

        self._active_elem = None
        self._active_idx  = None

        self.lblInfo = QLabel()

        self.gpCellEditor = QtGui.QGroupBox()
        fmbox2 = QFormLayout()
        self.lblNameField  = QLabel()
        self.ledStep  = QLineEdit(".1")
        self.ledStep.setValidator(QtGui.QDoubleValidator())
        self.connect(self.ledStep, SIGNAL("editingFinished()"),
                     self.setSpStepsize)
        self.spb1 = QtGui.QDoubleSpinBox()
        self.spb2 = QtGui.QDoubleSpinBox()
        self.spb5 = QtGui.QDoubleSpinBox()
        self.connect(self.spb5, SIGNAL("valueChanged(double)"),
                     self.spb2.setValue)
        self.connect(self.spb2, SIGNAL("valueChanged(double)"),
                     self.spb1.setValue)
        self.connect(self.spb1, SIGNAL("valueChanged(double)"),
                     self.spb5.setValue)
        self.connect(self.spb1, SIGNAL("valueChanged(double)"),
                     self.setActiveCell)

        self.lblPv = QLabel("")
        self.lblRange = QLabel("")
        self.valMeter = Qwt.QwtThermo()
        self.valMeter.setOrientation(Qt.Horizontal, Qwt.QwtThermo.BottomScale)
        self.valMeter.setSizePolicy(QSizePolicy.MinimumExpanding, 
                                    QSizePolicy.Fixed)
        self.valMeter.setEnabled(False)
        self.ledSet = QLineEdit("")
        self.ledSet.setValidator(QtGui.QDoubleValidator())
        self.connect(self.ledSet, SIGNAL("editingFinished()"),
                     self.setDirectValue)
        fmbox2.addRow("Name:", self.lblNameField)
        #fmbox2.addRow("Range", self.valMeter)
        fmbox2.addRow("Range:", self.lblRange)
        fmbox2.addRow("PV:", self.lblPv)
        fmbox2.addRow("Set:", self.ledSet)
        fmbox2.addRow("Stepsize:", self.ledStep)
        fmbox2.addRow("Step x1:", self.spb1)
        fmbox2.addRow("Step x2:", self.spb2)
        fmbox2.addRow("Step x5:", self.spb5)
        fmbox2.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)
        fmbox2.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        self.gpCellEditor.setLayout(fmbox2)
        self.gpCellEditor.setVisible(False)

        self.model = ElementPropertyTableModel()
        self.connect(self.model, 
                     SIGNAL("toggleElementState(PyQt_PyObject, bool)"),
                     self.elementStateChanged)
        self.tableview = ElementPropertyView()
        self.connect(self.tableview, SIGNAL("clicked(QModelIndex)"),
                     self.editingCell)
        self.delegate = ElementPropertyDelegate()
        self.connect(self.delegate, SIGNAL("editingElement(PyQt_PyObject)"),
                     self.updateCellInfo)

        #t2 = time.time()
        self.tableview.setModel(self.model)
        #self.tableview.setItemDelegate(self.delegate)
        #self.tableview.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.tableview.setWhatsThis("double click cell to enter editing mode")
        #fmbox.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)
        #self.model.loadElements(aphla.getElements("*")[:10])

        vbox = QVBoxLayout()
        vbox.addLayout(fmbox)
        vbox.addWidget(self.tableview)
        #vbox.addWidget(self.lblInfo)
        #vbox.addLayout(fmbox2)
        vbox.addWidget(self.gpCellEditor)
        self.setLayout(vbox)

        #self.connect(self.elemName, SIGNAL("editingFinished()"), 
        #             self.refreshTable)
        self.connect(self.elemName, SIGNAL("returnPressed()"), 
                     self._reload_elements)
        self.connect(self.elemField, SIGNAL("returnPressed()"), 
                     self._reload_elements)
        #self.connect(self.elemName, SIGNAL("currentIndexChanged(QString)"),
        #             self.refreshTable)

        self.setWindowTitle("Element Editor")
        self.noTableUpdate = True
        self.resize(800, 600)
        self.timerId = self.startTimer(1000)


    def setDirectValue(self):
        val = float(self.ledSet.text())
        self.spb1.setValue(val)

    def timerEvent(self, e):
        if self.model.rowCount() < 1: return

        #row1 = self.tableview.rowAt(0)
        #if row1 == -1: row1 = 0
        #row2 = self.tableview.rowAt(self.height())
        #if row2 == -1: row2 = self.model.rowCount()
        row1, row2 = 0, self.model.rowCount()
        self.model.updateData(row1, row2)
        #QApplication.processEvent()

    def _reload_elements(self):
        fam = str(self.elemName.text())
        fld = str(self.elemField.text())
        elems = []
        for e in aphla.getElements(fam):
            for f in e.fields():
                if not fnmatch(f, fld): continue
                elems.append((e, f))
        self.reloadElements(elems)

    def reloadElements(self, elems):
        self.model.loadElements(elems)
        print "model size:", self.model.rowCount(), self.model.columnCount()
        #for i in range(self.model.rowCount()):
        #    #print i, elem.name, fld, self.model._value[i]
        #    if self.model.isSubHeader(i):
        #        self.tableview.setSpan(i, 0, 1, self.model.columnCount())
        #    elif self.tableview.columnSpan(i, 0) > 1:
        #        self.tableview.setSpan(i, 0, 1, 1)
        #self.elemName.deselect()
        self.tableview.setFocus()
        self.tableview.resizeColumnToContents(0)
        #for i in range(self.model.columnCount()):
        #    w = self.tableview.columnWidth(i)
        #    self.tableview.setColumnWidth(i, w + 5)

    def setActiveCell(self, val):
        if self._active_elem is None:
            __logger.warn("no active element selected")
            return
        self.ledSet.setText("{0}".format(val))
        elem, fld = self._active_elem
        #print elem, fld, elem.get(fld, handle="setpoint", unitsys=None)
        elem.put(fld, val, unitsys=None)
        #print elem, fld, elem.get(fld, handle="setpoint", unitsys=None), " setted"
        idx0 = self.model.index(self._active_idx.row(), 0)
        idx1 = self.model.index(self._active_idx.row(), self.model.columnCount()-1)

        self.model.emit(SIGNAL("dataChanged(QModelIndex,QModelIndex)"),
                        idx0, idx1)

    def setSpStepsize(self):
        stp = float(self.ledStep.text())
        self.spb1.setSingleStep(stp)
        self.spb2.setSingleStep(2.0*stp)
        self.spb5.setSingleStep(5.0*stp)

    def editingCell(self, idx):
        r,c = idx.row(), idx.column()
        elem, fld = self.model.getElementField(r)
        s = self.model.data(idx).toString()
        if c != C_VAL_SP or len(s) == 0:
            self._active_elem, self._active_idx = None, None
            self.gpCellEditor.setVisible(False)
            return

        self.gpCellEditor.setVisible(True)

        self._active_elem = self.model.getElementField(r)
        self._active_idx = idx
        val, succ = self.model.data(idx).toDouble()
        if not succ:
            print "can not convert value {0} for {1}.{2}".format(
                self.model.data(idx), elem, fld)
        #print "{0}, {1}".format(elem, fld), val
        if elem.boundary(fld) is None:
            elem.updateBoundary(field=fld)
        try:
            bdl, bdr = elem.boundary(fld)
            ss = elem.stepSize(fld)
            self.lblRange.setText("[{0}, {1}]".format(bdl, bdr))
            self.ledStep.setText("{0}".format(ss))
            stp = float(self.ledStep.text())
            self.spb1.setSingleStep(stp)
            self.spb2.setSingleStep(2.0*stp)
            self.spb5.setSingleStep(5.0*stp)

            for spb in [self.spb1, self.spb2, self.spb5]:
                spb.setMinimum(bdl)
                spb.setMaximum(bdr)
                spb.setDecimals(10) # no scientific notation
                spb.setValue(val)
        except:
            self.lblRange.setText("")
            self.ledStep.setText("")
            for spb in [self.spb1, self.spb2, self.spb5]:
                spb.setMinimum(0)
                spb.setMaximum(0)
                spb.setDecimals(10) # no scientific notation
                spb.setValue(0)

        #self.lblInfo.setText("{0}.{1} in {2} ss={3}".format(
        #    elem.name, fld, bd, elem.stepSize(fld)))
        self.lblNameField.setText("{0}.{1}".format(elem.name, fld))
        pvl = elem.pv(field=fld, handle="setpoint")
        self.lblPv.setText("{0}".format(pvl))
        #v = aphla.catools.caget(pvl[0], format=aphla.catools.FORMAT_CTRL)
        #print "DRVH", v.upper_ctrl_limit
        #print "DRVL", v.lower_ctrl_limit

    def updateCellInfo(self, elemrec):
        elem, ik, fld = elemrec
        self.lblStep.setText(str(elem.stepSize(fld)))
        elem.updateBoundary()
        bd = elem.boundary(fld)
        #self.lblInfo.setText("{0}.{1} in {2} ss={3}".format(
        #    elem.name, fld, bd, elem.stepSize(fld)))
        self.lblNameField.setText("{0}.{1}".format(elem.name, fld))
        if True:
            self.lblRange.setText(str(bd))
        elif bd is None or bd[0] is None or bd[1] is None: 
            self.valMeter.setEnabled(False)
        else:
            rg = Qwt.QwtDoubleInterval(bd[0], bd[1])
            self.valMeter.setScale(rg, (bd[1]-bd[0])/2.01)
            self.valMeter.setValue(elem.get(fld, unitsys = None))
            #print elem.get(fld, unitsys=None)
            #print self.valMeter.value()
            self.valMeter.setEnabled(True)

    def elementStateChanged(self, elem, stat):
        #print "State changed:", elem, stat
        self.emit(SIGNAL("elementChecked(PyQt_PyObject, bool)"), elem, stat)

    def processCell(self, index):
        #print "Process cell", index.row(), index.column()
        #print "   val:", self.model._value[index.row()][index.column()]
        pass

    def _addElements(self, elems):
        #self.setVisible(True)
        #print "new element:", elemnames
        #if elems is None:
        #    QMessageBox.warning(self, "Element Not Found",
        #                        "element " + str(elemnames) + " not found")
        #    return
            #print elem.name, elem.sb, elem.fields()
        #self.tableview.reset()
        # wid = QWidget()
        # vbox = QVBoxLayout()
        # vbox.addWidget(QLabel("Name:   %s" % elem.name))
        # vbox.addWidget(QLabel("Device: %s" % elem.devname))
        # vbox.addWidget(QLabel("Cell:   %s" % elem.cell))
        # vbox.addWidget(QLabel("Girder: %s" % elem.girder))
        # vbox.addWidget(QLabel("sBegin: %.3f" % elem.sb))
        # vbox.addWidget(QLabel("Length: %.3f" % elem.length))

        # #vbox.addWidget(lb_name)
        # vbox.addWidget(self.tableview)
        # wid.setLayout(vbox)
        # self.addTab(wid, elem.name)
        #self.adjustSize()
        pass

    def closeTab(self, index):
        self.removeTab(index)
        if self.count() <= 0: self.setVisible(False)

    def setEnabled(self, v):
        self.elemName.setEnabled(v)
        #self.refreshBtn.setEnabled(v)

    def updateModelData(self):
        pass

    def setRange(self, vmin, vmax):
        #self.rangeSlider.setMin(int(vmin))
        #self.rangeSlider.setMax(int(vmax))
        #if self.rangeSlider.end() > vmax: self.rangeSlider.setEnd(vmax)
        #if self.rangeSlider.start() < vmin: self.rangeSlider.setStart(vmin)
        self.sb = vmin
        self.se = vmax
        #self.refreshTable()


# test purpose
if __name__ == "__main__":
    import aphla as ap
    ap.machines.load("nsls2")
    elems = []
    for bpm in ap.getElements("COR")[:3]:
        elems.append((bpm, 'x'))
        elems.append((bpm, 'y'))
    form = ElementEditor(None)
    form.reloadElements(elems)
    form.resize(800, 600)
    print "Elements reloaded"
    #form.reloadElements("*")
    #app.exec_()
    cothread.WaitForQuit()
