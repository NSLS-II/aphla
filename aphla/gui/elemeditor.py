"""
Element Property Editor
=======================

:author: Lingyun Yang <lyyang@bnl.gov>

list all properties of element, provide editing.

A table view for HLA element, with delegates user can modify value online
"""

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

import traceback
import collections
import numpy as np
import sys, time
from functools import partial

import qrangeslider

C_FIELD, C_VAL_RAW = 0, 1
_DBG_VERBOSE = 1

import logging
_logger = logging.getLogger(__name__)

class SimpleListDlg(QDialog):
    def __init__(self, parent = None, datalist = None, mode='r'):
        super(SimpleListDlg, self).__init__(parent)
        self.tbl = QTableWidget()
        self.mode = mode # read only or write 'r'/'w'
        self.values = []
        if datalist is not None:
            data = datalist.toList()
            self.tbl.setRowCount(len(data))
            self.tbl.setColumnCount(1)
            for i,val in enumerate(data):
                #print i, val.toFloat()
                self.values.append(val.toFloat()[0])
                it = QTableWidgetItem("%g" % val.toFloat()[0])
                if self.mode == 'r': 
                    it.setFlags(it.flags() & ~Qt.ItemIsEditable)
                self.tbl.setItem(i,0,it)
        
        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok|
                                     QDialogButtonBox.Cancel)
        layout = QVBoxLayout()
        layout.addWidget(self.tbl)
        layout.addWidget(buttonBox)
        self.setLayout(layout)

        self.connect(buttonBox, SIGNAL("accepted()"), self.accept)
        self.connect(buttonBox, SIGNAL("rejected()"), self.reject)


    def accept(self):
        self.values = []
        for i in range(self.tbl.rowCount()):
            v = self.tbl.item(i,0).data(Qt.EditRole).toFloat()
            if self.mode == 'w': self.values.append(v[0])
        self.done(0)

    def reject(self):
        self.values = []
        self.done(0)


class ElementPropertyTableModel(QAbstractTableModel):
    def __init__(self, elems):
        super(ElementPropertyTableModel, self).__init__()
        self._allelems = elems
        # elem obj, name/fld, handle
        self._elemrec = []
        self._desc  = []
        self._unitsys = [None, 'phy']
        self._value, self._unit = [], []
        self._inactive = set()

        t0 = time.time()
        self._load_rows(elems)
        t1 = time.time()  
        #for i in range(len(self._elemrec)): self._update_data(i)
        t2 = time.time()
        _logger.info("full update takes {0} ({1}+{2})".format(
                t2-t0, t1-t0, t2-t1))

    def _load_rows(self, allelems):
        ik = 0
        for elem in allelems:
            self._elemrec.append((elem, "%s" % elem.name, None))
            self._value.append(None)
            self._desc.append("family = %s\nsb = %.4g\nlength= %.4g\n" \
                              % (elem.family,elem.sb, elem.length))
            self._unit.append(None)
            for var in sorted(elem.fields()):
                # postfix for field name, field__r and field__w
                for hdl in ('readback', 'setpoint'):
                    #if not self._has_field_handle(elem, var, hdl): continue
                    if hdl == 'setpoint' and not elem.settable(var): continue
                    self._elemrec.append((elem, var, hdl))
                    self._value.append([None for v in self._unitsys])
                    self._unit.append([None for v in self._unitsys])
                    self._desc.append(None)
            ik += 1
        self._NF = len(self._elemrec)
        self._inactive = set()
        #print self._value

    def _element_block(self, irow):
        ret = []
        if irow < 0 or irow >= len(self._value): return ret
        # 
        for i0 in range(irow, -1, -1):
            if self._value[i0] is not None: continue
            ret.append(i0)
            for i in range(i0+1, len(self._value)):
                if self._value[i] is None: break
                ret.append(i)
            return ret
        return []

    def _has_field_handle(self, elem, fld, hdl):
        try:
            elem.get(fld, handle=hdl, unitsys=None)
        except:
            return False
        return True

    def _get_quiet(self, elem, var, src, u):
        try:
            v = elem.get(var, handle=src, unitsys=u)
        except:
            v = None
        # check the unit
        try:
            usymb = elem.getUnit(var, unitsys=u)
        except:
            usymb = ""

        try:
            v = float(v)
        finally:
            return v, usymb

    def _update_data(self, i):
        if self._value[i] is None: return
        elem, fld, hdl = self._elemrec[i]
        #print "updating", elem.name
        for k,u in enumerate(self._unitsys):
            #self._field[i] = "<b>%s</b>" % elem.name
            v, usymb = self._get_quiet(elem, fld, hdl, u)
            #print "  updated:", elem.name, fld, src, u, v
            self._value[i][k] = v
            self._unit[i][k] = usymb
        #print self._value
        
    def isHeadIndex(self, i):
        if self._value[i] is None: return True
        else: return False

    def subHeadIndex(self):
        return [i for i,v in enumerate(self._value) if v is None]

    def _format_value(self, val, unit = ""):
        """format as QVariant"""
        if val is None: return QVariant()
        if len(unit) > 0: usymb = "[{0}]".format(unit)
        else: usymb = ""
        if isinstance(val, (str, unicode)):
            if len(val) < 8: return QVariant(str(val) + usymb)
            return QVariant(str(val)[:8]+"... "+usymb)
        elif isinstance(val, collections.Iterable):
            return QVariant(str(val)[:8]+"... "+usymb)
        else:
            return QVariant("{0:.4g} {1}".format(val, usymb))

    def data(self, index, role=Qt.DisplayRole):
        """return data as a QVariant"""
        #print "data model=",role
        if not index.isValid() or index.row() >= self._NF:
            return QVariant()

        r, col  = index.row(), index.column()
        
        elem, fld, hdl = self._elemrec[r]
        vals, units = self._value[r], self._unit[r]

        if role == Qt.DisplayRole:
            if col == C_FIELD and vals is None:
                return QVariant(fld)
            elif col == C_FIELD:
                if hdl == None: return QVariant()
                elif hdl == 'readback': return QVariant(fld+'_r')
                elif hdl == 'setpoint': return QVariant(fld+'_w')
                else: raise RuntimeError("unknow handle '%s'" % hdl)
            #print r, col, self._field[r], self._value[r]
            elif vals is None: 
                return QVariant()
            # all for display
            elif isinstance(vals[col-1], (tuple, list)):
                #return QVariant.fromList([QVariant(v) for v in vals[col-1]])
                return QVariant("[...]")
            else:
                #print "converting", val, unit
                return self._format_value(vals[col-1], units[col-1])
        elif role == Qt.EditRole:
            if col == C_FIELD: 
                raise RuntimeError("what is this ?")
                return QVariant(self._field[r]+self._fieldpfx[r])
            #print r, col, self._field[r], self._value[r]
            if vals is None: return QVariant()
            if isinstance(vals[col-1], (tuple, list)):
                return QVariant.fromList([QVariant(v) for v in vals[col-1]])
            elif vals[col-1] is not None:
                return QVariant(vals[col-1])
        elif role == Qt.TextAlignmentRole:
            if col == C_FIELD: return QVariant(Qt.AlignLeft | Qt.AlignVCenter)
            else: return QVariant(Qt.AlignRight | Qt.AlignBottom)
        elif role == Qt.ToolTipRole:
            if col == C_FIELD and self._desc[r]:
                return QVariant(self._desc[r])
        elif role == Qt.ForegroundRole:
            if r in self._inactive and self.isHeadIndex(r):
                return QColor(Qt.darkGray)
            elif r in self._inactive:
                return QColor(Qt.lightGray)
            #else: return QColor(Qt.black)
        elif role == Qt.BackgroundRole:
            if self.isHeadIndex(r): return QColor(Qt.lightGray)            
        elif role == Qt.CheckStateRole:
            if vals is not None: return QVariant()
            elif r in self._inactive: return Qt.Unchecked
            else: return Qt.Checked 
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
            if section == C_FIELD: return QVariant("Field")
            elif section == C_VAL_RAW: return QVariant("None(Raw)")
            else: return QVariant(self._unitsys[section-1])
        elif orientation == Qt.Vertical:
            if self._value[section] is not None: return QVariant()
            idx = [k for k in range(section+1) if self._value[k] is None]
            return QVariant(len(idx))

        return QVariant(int(section+1))

    def flags(self, index):
        #print "flags:", 
        if not index.isValid():
            return Qt.ItemIsEnabled
        row, col = index.row(), index.column()
        elem, fld, hdl = self._elemrec[row]
        vals = self._value[row]
        if vals is None:
            return Qt.ItemIsEnabled | Qt.ItemIsEditable | Qt.ItemIsUserCheckable | Qt.ItemIsSelectable
        elif vals[col-1] is None:
            return Qt.ItemIsEnabled
        elif hdl == 'setpoint' and row not in self._inactive:
            return Qt.ItemFlags(QAbstractTableModel.flags(self, index) |
                Qt.ItemIsEditable)
        else:
            return Qt.ItemIsEnabled
        
    def rowCount(self, index=QModelIndex()):
        return len(self._elemrec)
    
    def columnCount(self, index=QModelIndex()):
        return 3

    def isList(self, index):
        r, c = index.row(), index.column()
        if c == 0: return False
        return isinstance(self._value[r][c-1], (list, tuple))

    def setData(self, index, value, role=Qt.EditRole):
        #print "setting data", index.row(), index.column(), value.toInt()
        if not index.isValid(): return False
        
        #if index.isValid() and 0 <= index.row() < self._NF:
        row, col = index.row(), index.column()
        elem, fld, hdl = self._elemrec[row]
        if col == C_FIELD:
            #print "Editting property, ignore"
            checkstate, err = value.toInt()
            if checkstate == Qt.Unchecked:
                #print "disable row ", row
                self.setElementActive(row, False)
                self.emit(SIGNAL("toggleElementState(PyQt_PyObject, bool)"), 
                          elem, False)
            elif checkstate == Qt.Checked:
                #print "enable row", row
                self.setElementActive(row, True)
                self.emit(SIGNAL("toggleElementState(PyQt_PyObject, bool)"),
                          elem, True)
            else:
                raise RuntimeError("unknown check state for cell (%d,%d)" % (row, col))
        elif value.canConvert(QVariant.List):
            val = [v.toFloat()[0] for v in value.toList()]
            self._value[row][col-1] = val
            _logger.info("Did not set {0}.{1} for real machine".format(
                elem.name, fld))
        else:
            #print "Editting pv col=", col, value, value.toDouble()
            # put the value to machine
            vd = value.toDouble()[0]
            unit = self._unitsys[col-1]

            _logger.info("Putting {0} to {1}.{2} in role {3}".format(
                vd, elem.name, fld, role))
            # need to update model data, otherwise, setEditorData will
            # call model for un-updated value
            elem.put(fld, vd, unitsys=unit)
            #for i in range(len(self._elemrec)): self._update_data(i)
            self._value[row][col-1] = vd
        # update the whole table ?
        #idx0 = self.index(0, 0)
        #idx1 = self.index(len(self._elemrec) - 1, self.columnCount()-1)
        #self.emit(SIGNAL("dataChanged(QModelIndex,QModelIndex)"),
        #          idx0, idx1)
        return True

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

    def clear(self):
        self._allelems = []
        self._elemrec = []
        self._desc  = []
        self._value = []
        self._unit = []

    
class ElementPropertyDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super(ElementPropertyDelegate, self).__init__(parent)
        self._modified = False

    def paint(self, painter, option, index):
        #if index.column() == SETPOINT:
        #print index.row(), index.column()
        model = index.model()
        row, col = index.row(), index.column()
        if index.column() == 0 and model.isHeadIndex(index.row()):
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
        if col == 0 and model._value[row] is None:
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

        elem, fld, hdl = model._elemrec[row]
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
        if event.type() == QEvent.MouseButtonDblClick and model.isList(index):
            # read-only ?
            if model.flags(index) & Qt.ItemIsEditable: mode = 'w'
            else: mode = 'r'
            #print mode
            data = model.data(index, role=Qt.EditRole)
            fm = SimpleListDlg(datalist=data, mode = mode)
            fm.setModal(True)
            fm.exec_()
            if fm.values:
                #print fm.values
                vals = QVariant.fromList([QVariant(d) for d in fm.values])
                model.setData(index, vals)
            return True

        return QStyledItemDelegate.editorEvent(self, event, model, option, index)

    def updateEditorGeometry(self, editor, opt, index):
        #print "geometry:", opt.rect
        #opt.rect.adjust(0, 30, 100, 60)
        QStyledItemDelegate.updateEditorGeometry(self, editor, opt, index)

        
class ElementPropertyView(QTableView):
    def __init__(self, parent = None):
        QTableView.__init__(self, parent)
        self.timerId = self.startTimer(3000)


    def disableElement(self, checked=True, irow=-1):
        if irow < 0: return
        print "Disable element:", irow
        self.model().setElementActive(irow, not checked)

    def timerEvent(self, e):
        mdl = self.model()
        if not mdl: return

        row1 = self.rowAt(0)
        if row1 == -1: row1 = 0
        row2 = self.rowAt(self.height())
        if row2 == -1: row2 = mdl.rowCount()
        for i in range(row1, row2):
            mdl._update_data(i)
            idx = self.currentIndex()
            if idx.row() == i:continue
            idx0 = mdl.index(i, 0)
            idx1 = mdl.index(i, mdl.columnCount()-1)
            mdl.emit(SIGNAL("dataChanged(QModelIndex,QModelIndex)"),
                     idx0, idx1)

    def contextMenuEvent(self, e):
        mdl = self.model()
        irow = self.rowAt(e.y())
        #print "Row:", self.rowAt(e.y())
        cmenu = QMenu()
        m_dis = QAction("disabled", self)
        m_dis.setCheckable(True)
        act = mdl.isActive(irow)
        if not act:
            m_dis.setChecked(True)

        self.connect(m_dis, SIGNAL("toggled(bool)"),
                     partial(self.disableElement, irow=irow))
        cmenu.addAction(m_dis)
        cmenu.exec_(e.globalPos())

class ElementEditorDock(QDockWidget):
    def __init__(self, parent, elems=[], sb = None, se = None):
        QDockWidget.__init__(self, parent)
        self.model = None
        #self.connect(self, SIGNAL('tabCloseRequested(int)'), self.closeTab)
        #gb = QGroupBox("select")
        fmbox = QGridLayout()

        #fmbox.addRow("S-Range", self.lblRange)

        self.elemBox = QLineEdit()
        self.elemBox.setToolTip(
            "list elements within the range of the active plot.<br>"
            "Examples are '*', 'HCOR', 'BPM', 'QUAD', 'c*c20a', 'q*g2*'"
            )
        self.elems = elems
        self.elemCompleter = QCompleter(elems)
        self.elemBox.setCompleter(self.elemCompleter)

        #self.rangeSlider = qrangeslider.QRangeSlider()
        #self.rangeSlider.setMin(0)
        #self.rangeSlider.setMax(100)
        #self.rangeSlider.setRange(10, 70)
        #self.elemBox.insertSeparator(len(self.elems))
        #fmbox.addRow("Range", self.rangeSlider)
        fmbox.addWidget(QLabel("Filter"), 0, 0)
        fmbox.addWidget(self.elemBox, 0, 1)
        #self.refreshBtn = QPushButton("refresh")
        #fmbox.addRow(self.elemBox)

        self.lblInfo = QLabel()

        #self.fldGroup = QGroupBox()
        fmbox2 = QFormLayout()
        self.lblNameField  = QLabel()
        self.lblStep  = QLabel()
        self.lblRange = QLabel()
        self.valMeter = Qwt.QwtThermo()
        self.valMeter.setOrientation(Qt.Horizontal, Qwt.QwtThermo.BottomScale)
        self.valMeter.setSizePolicy(QSizePolicy.MinimumExpanding, 
                                    QSizePolicy.Fixed)
        self.valMeter.setEnabled(False)
        fmbox2.addRow("Name", self.lblNameField)
        #fmbox2.addRow("Field", self.lblField)
        fmbox2.addRow("Step", self.lblStep)
        #fmbox2.addRow("Range", self.valMeter)
        fmbox2.addRow("Range", self.lblRange)
        fmbox2.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)
        fmbox2.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        #self.fldGroup.setLayout(fmbox2)


        self.model = None
        self.delegate = None
        self.tableview = ElementPropertyView()
        #self.tableview.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.tableview.setWhatsThis("double click cell to enter editing mode")
        #fmbox.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)
        vbox = QVBoxLayout()
        vbox.addLayout(fmbox)
        vbox.addWidget(self.tableview)
        #vbox.addWidget(self.lblInfo)
        vbox.addLayout(fmbox2)
        #vbox.addWidget(self.fldGroup)
        cw = QWidget(self)
        cw.setLayout(vbox)
        self.setWidget(cw)

        #self.connect(self.elemBox, SIGNAL("editingFinished()"), 
        #             self.refreshTable)
        self.connect(self.elemBox, SIGNAL("returnPressed()"), 
                     self.refreshTable)
        #self.connect(self.elemBox, SIGNAL("currentIndexChanged(QString)"),
        #             self.refreshTable)

        self.setWindowTitle("Element Editor")
        self.noTableUpdate = True

    def refreshTable(self, txt = None):
        elemname = str(self.elemBox.text()) if txt is None else txt
        self.elemBox.selectAll()
        t0 = time.time()
        #elems = [e for e in self.parent().getVisibleElements(elemname)
        #          if e.family in ['BPM', 'COR', 'HCOR']][:40]
        self.sb, self.se = self.parent().getVisibleRange()
        elems = self.parent().getVisibleElements(elemname, self.sb, self.se)
        deadelems = self.parent().getDeadElements()
        _logger.info("Found elems: {0}".format(len(elems)))
        QApplication.processEvents()
        t1 = time.time()
        if self.model and self.model.rowCount() > 0:
            del self.model
            del self.delegate
            #self.model.clear()
        self.model = ElementPropertyTableModel(elems)
        self.connect(self.model, 
                     SIGNAL("toggleElementState(PyQt_PyObject, bool)"),
                     self.elementStateChanged)

        t2 = time.time()
        self.delegate = ElementPropertyDelegate()
        self.connect(self.delegate, SIGNAL("editingElement(PyQt_PyObject)"),
                     self.updateCellInfo)

        #t2 = time.time()
        self.tableview.reset()
        self.tableview.setModel(self.model)
        self.tableview.setItemDelegate(self.delegate)
        #self.model.load(elems)
        #print "model size:", self.model.rowCount(), self.model.columnCount()
        for i in range(self.model.rowCount()):
            elem, fld, hdl = self.model._elemrec[i]
            #print i, elem.name, fld, self.model._value[i]
            if self.model.isHeadIndex(i):
                self.tableview.setSpan(i, 0, 1, self.model.columnCount())
            elif self.tableview.columnSpan(i, 0) > 1:
                self.tableview.setSpan(i, 0, 1, 1)
        #idx0 = self.model.index(0, 0)
        #idx1 = self.model.index(self.model.rowCount() - 1,
        #                        self.model.columnCount()-1)
        #self.model.emit(SIGNAL("dataChanged(QModelIndex,QModelIndex)"),
        #                idx0, idx1)
        #for i in range(self.model.columnCount()):
        #rz = self.tableview.geometry()
        #fullwidth = sum([self.tableview.columnWidth(i) for i in range(ncol)])
        #self.tableview.setMinimumWidth(fullwidth+20)
        #self.tableview.setMaximumWidth(fullwidth+60)
        #self.tableview.adjustSize()
        #self.connect(self.tableview, SIGNAL("clicked(QModelIndex)"), 
        #             self.processCell)
        t3 = time.time()
        #self._addElements(elems)
        #print "DT:", t1 - t0, t2 - t1, t3 - t2
        self.elemBox.deselect()
        self.tableview.setFocus()
        self.tableview.resizeColumnToContents(0)
        for i in range(self.model.columnCount()):
            w = self.tableview.columnWidth(i)
            self.tableview.setColumnWidth(i, w + 5)

    def updateCellInfo(self, elemrec):
        elem, fld, hdl = elemrec
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
            print elem.get(fld, unitsys=None)
            print self.valMeter.value()
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
        self.elemBox.setEnabled(v)
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

class MTestForm(QDialog):
    def __init__(self, parent=None):
        super(MTestForm, self).__init__(parent)
        elems = ap.getElements("C10")
        #elems = []
        print elems
        self.model = ElementPropertyTableModel(elems)
        self.tablev = QTableView()
        self.tablev.setModel(self.model)
        self.tablev.setItemDelegate(ElementPropertyDelegate(self))
        for i in self.model.subHeadIndex():
            self.tablev.setSpan(i, 0, 1, self.model.columnCount()) 
        #for i in range(self.model.columnCount()):
        self.tablev.resizeColumnsToContents()
        
        vbox = QVBoxLayout()
        vbox.addWidget(self.tablev)
        self.setLayout(vbox)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    import aphla as ap
    ap.machines.init("nsls2v2")
    form = MTestForm()
    form.resize(400, 300)
    form.show()
    app.exec_()
