"""
Lattice Viewer
=======================

:author: Lingyun Yang <lyyang@bnl.gov>

list all properties of lattice.
"""

import cothread
app = cothread.iqt()

import pvmanager

from PyQt4 import QtGui
from PyQt4.QtCore import (QAbstractTableModel, QDataStream, QFile,
        QIODevice, QModelIndex, QRegExp, QSize, QString, QVariant, Qt,
        SIGNAL, QEvent)
from PyQt4.QtGui import (QColor, QComboBox, QLineEdit, QDoubleSpinBox,
        QSpinBox, QStyle, QStyledItemDelegate, QTextDocument, QTextEdit, 
        QDialog, QDockWidget, QGroupBox, QPushButton, QHBoxLayout, 
        QGridLayout, QVBoxLayout, QTableView, QWidget, QApplication,
        QTableWidget, QDialogButtonBox, QStatusBar, QTableWidgetItem,
        QFormLayout, QLabel, QSizePolicy, QCompleter, QMenu, QAction,
        QTabWidget, QCheckBox)
import PyQt4.Qwt5 as Qwt
from aporbitplot import ApPlot
#import traceback
import collections
import numpy as np
import os
import sys, time
from functools import partial
from fnmatch import fnmatch
import qrangeslider
import h5py
import datetime

C_ELEMENT, C_FIELD, C_PV, C_RW, C_VALUES = 0, 1, 2, 3, 4
_DBG_VERBOSE = 1

#import logging
#_logger = logging.getLogger(__name__)

class SnapshotRow(object):
    def __init__(self, pv, element, field, rw, values, ts, wf = 0):
        self.pv = pv
        self.element = element
        self.field = field
        self.rw = int(rw)
        self.ts = float(ts)
        self.wf = wf    # waveform: 0 - scalar
        # live data + a list of values from each dataset
        self.values = [None] + [v for v in values]
        self.hlvalues = {}
        self.ts = 0.0

    def __str__(self):
        v = "{0}".format(self.values)
        return "{0}, {1}, {2}, {3}".format(self.pv, self.element,
                                           self.field, v)
    def __repr__(self):
        v = "{0}".format(self.values)
        return "{0}, {1}, {2}, {3}".format(self.pv, self.element,
                                           self.field, v)
        

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


class LatSnapshotTableModel(QAbstractTableModel):
    def __init__(self):
        super(LatSnapshotTableModel, self).__init__()
        self._cadata = pvmanager.CaDataMonitor([])
        self._rows = []
        self._mask = []
        self.dstitle = ["Live Data"]
        self.dstimestamp = [0.0]
        self.dsref = [0, 0] # live data as reference, abs diff


    def updateLiveData(self):
        for i,r in enumerate(self._rows):
            self._rows[i].values[0] = self._cadata.get(r.pv, None)
        idx0 = self.index(0, C_VALUES - 1)
        idx1 = self.index(self.rowCount()-1, self.columnCount() - 1)
        self.emit(SIGNAL("dataChanged(QModelIndex,QModelIndex)"),
                  idx0, idx1)


    def addDataSet(self, pvs, elements, fields, rw, values, ts, **kwarg):
        wf = kwarg.get("wf", [0] * len(pvs))
        self.dstitle.append(kwarg.get("title", ""))
        # assume no duplicate PV in pvs
        if not self._rows:
            n = max([len(pvs), len(elements), len(fields), len(rw), 
                     len(values), len(ts), len(wf)])
            self._rows = [
                SnapshotRow(pvs[i], elements[i], fields[i], rw[i],
                            [values[i]], ts[i], wf[i])
                for i in range(n)]

            self._mask = [0] * n
            self.dstimestamp.append(max(ts))
            #print "initial import %d records" % n
        else:
            #print "Add extra"
            mpv = dict([(r.pv,i) for i,r in enumerate(self._rows)])
            nset = len(self._rows[0].values)
            for i,pv in enumerate(pvs):
                j = mpv.get(pv, -1)
                if j == -1:
                    # a new record
                    vals = [None] * nset + [values[i]]
                    r = SnapshotRow(pv, elements[i], fields[i], rw[i], vals,
                                    ts[i], wf[i])
                    self._rows.append(r)
                    self._mask.append(0)
                    continue
                elif elements[i] == self._rows[j].element and \
                        fields[i] == self._rows[j].field:
                    self._rows[j].values.append(values[i])
                else:
                    raise RuntimeError("pv meaning does not agree")
            self.dstimestamp.append(max(ts))
        self._cadata.addPvList(pvs)

        idx0 = self.index(0, C_VALUES - 1)
        idx1 = self.index(self.rowCount()-1, self.columnCount() - 1)
        self.emit(SIGNAL("dataChanged(QModelIndex,QModelIndex)"),
                  idx0, idx1)
        #print self._cadata.data
        
    def sort(self, col, order):
        #print self._rows
        if col == C_PV:
            self._rows = sorted(self._rows, key=lambda r: r.pv)
        elif col == C_ELEMENT:
            self._rows = sorted(self._rows, key=lambda r: r.element)
        elif col == C_FIELD:
            self._rows = sorted(self._rows, key=lambda r: r.field)
        elif col == C_RW:
            self._rows = sorted(self._rows, key=lambda r: r.rw)
        else:
            return

        if order == Qt.DescendingOrder: self._rows.reverse()


    def filterRows(self, name, field, pv):
        self.emit(SIGNAL("layoutAboutToBeChanged()"))
        for i,r in enumerate(self._rows):
            if fnmatch(r.element, "*%s*" % name) and \
               fnmatch(r.field, "*%s*" % field) and \
               fnmatch(r.pv, "*%s*" % pv) and self._mask[i] < 2:
                self._mask[i] = 0
                continue
            elif self._mask[i] == 0:
                self._mask[i] = 1
        #print "Sum of mask:", np.sum(self._mask)
        self.emit(SIGNAL("layoutChanged()"))
        idx0 = self.index(0, C_VALUES - 1)
        idx1 = self.index(self.rowCount()-1, self.columnCount() - 1)
        self.emit(SIGNAL("dataChanged(QModelIndex,QModelIndex)"),
                  idx0, idx1)


    def _calc_diff(self, vals, iref, mode):
        """calculate the difference, relative or absolute, returns None if 
        the data does not make sense"""
        dd = []
        try:
            vf = [float(v) for v in vals]
            dd = [v - vf[iref] for i,v in enumerate(vf)]
            if mode == 1:
                dd = [ v*100.0/vf[iref] for i,v in enumerate(dd)]
            return dd, 0
        except TypeError:
            pass
        except ZeroDivisionError:
            print "Divided by zero"
            return None, None

        dd = []
        try:
            for i,vf1 in enumerate(vals):
                vf2a = [float(v) for v in vf1]
                vf2r = [float(v) for v in vals[iref]]
                vdf = [v - vf2r[j] for j,v in enumerate(vf2a)]
                dd.append(vdf)
            if mode == 0: return dd, range(len(vals[0]))
        except ValueError:
            # can not convert string to float
            #raise
            return None, None
        except TypeError:
            #raise
            return None, None
        except:
            #print vals, iref, mode
            raise

        if mode == 1:
            idx, ret = [], []
            for i,vj in enumerate(vals[iref]):
                if np.abs(vj) == 0.0: continue
                idx.append(i)
                ret.append([v[i]/vj for v in dd])
            return zip(*ret), idx 
        return None, 0

    def getSnapshotRecord(self, idx):
        validrows = [r for i,r in enumerate(self._rows) if self._mask[i] == 0]
        #print idx, len(validrows)
        try:
            r = validrows[idx]
            print r, self.dsref
            dd, idx = self._calc_diff(r.values, self.dsref[0], self.dsref[1])
            return idx, r.values + dd
        except IndexError:
            print "index error: len(validrows)= {0}, i={1}".format(
                len(validrows), idx)
            raise
        except:
            print idx, r.values, dd

    def getSnapshotData(self):
        idx, ret = [], []
        validrows = [r for i,r in enumerate(self._rows) if self._mask[i] == 0]
        for i,r in enumerate(validrows):
            ri = [v for v in r.values]
            dd, iddx = self._calc_diff(ri, self.dsref[0], self.dsref[1])
            if not dd: continue
            ri.extend(dd)
            idx.append(i)
            ret.append(ri)
        return idx, ret


    def data(self, index, role=Qt.DisplayRole):
        """return data as a QVariant"""
        #print "data model=",role
        if not index.isValid() or index.row() >= len(self._rows):
            return QVariant()

        ri, cj  = index.row(), index.column()
        validrows = [r for i,r in enumerate(self._rows) if self._mask[i] == 0]
        if ri >= len(validrows): return QVariant()

        r = validrows[ri]
        if role == Qt.DisplayRole:
            if cj == C_PV:
                return QVariant(QString(r.pv))
            elif cj == C_ELEMENT: return QVariant(QString(r.element))
            elif cj == C_FIELD: return QVariant(QString(r.field))
            elif cj == C_RW: return QVariant(r.rw)

            if r.wf > 0: return QVariant("[...]")
            # the data sections
            fmt = "%.6g"
            ids, j = divmod(cj - C_VALUES, 2)

            dd = self._calc_diff(r.values, self.dsref[0], self.dsref[1])
            if dd is None: dlst = zip(r.values, [None] * len(r.values))
            else: dlst = zip(r.values, dd)
            v = dlst[ids][j]
            if v is None: return QVariant()
            try: return QVariant(fmt % v)
            except: return QVariant()
            # all for display
        #elif role == Qt.TextAlignmentRole:
        #    if cj == C_FIELD: return QVariant(Qt.AlignLeft | Qt.AlignVCenter)
        #    else: return QVariant(Qt.AlignRight | Qt.AlignBottom)
        #elif role == Qt.ToolTipRole:
        #    if col == C_FIELD and self._desc[r]:
        #        return QVariant(self._desc[r])
        #elif role == Qt.ForegroundRole:
        #    if r in self._inactive and self.isHeadIndex(r):
        #        return QColor(Qt.darkGray)
        #    elif r in self._inactive:
        #        return QColor(Qt.lightGray)
        #    #else: return QColor(Qt.black)
        #elif role == Qt.BackgroundRole:
        #    if self.isHeadIndex(r): return QColor(Qt.lightGray)            
        #elif role == Qt.CheckStateRole:
        #    if vals is not None: return QVariant()
        #    elif r in self._inactive: return Qt.Unchecked
        #    else: return Qt.Checked 
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
            if section == C_PV: return QVariant("PV")
            elif section == C_ELEMENT: return QVariant("Element")
            elif section == C_FIELD: return QVariant("Field")
            elif section == C_RW: return QVariant("R/W")
            ids, j = divmod(section-C_VALUES, 2)
            if j == 1: return QVariant("diff")
            else: 
                ts = self.dstimestamp[ids]
                return QVariant("%s\n%s" % (
                    self.dstitle[ids], datetime.datetime.fromtimestamp(ts)))
        elif orientation == Qt.Vertical:
            validrows = [r for i,r in enumerate(self._rows) if self._mask[i] == 0]
            if section >= len(validrows): return QVariant()
            return QVariant(section)

        return QVariant(int(section+1))

    def flags(self, index):
        validrows = [r for i,r in enumerate(self._rows) if self._mask[i] == 0]
        if not index.isValid():
            return Qt.ItemIsEnabled
        row, col = index.row(), index.column()
        idx, j = divmod(col - C_VALUES, 2)
        if validrows[row].rw == 1 and col == C_VALUES:
            return  Qt.ItemFlags(QAbstractTableModel.flags(self, index) |
                                 Qt.ItemIsEditable)
        elif col >= C_VALUES and j == 0:
            return  Qt.ItemFlags(QAbstractTableModel.flags(self, index) |
                                 Qt.ItemIsSelectable)
        return Qt.ItemIsEnabled
        
    def rowCount(self, index=QModelIndex()):
        validrows = [r for i,r in enumerate(self._rows) if self._mask[i] == 0]
        return len(validrows)
    
    def columnCount(self, index=QModelIndex()):
        if not self._rows: return 0
        return C_VALUES + len(self._rows[0].values)*2

    def setData(self, index, value, role=Qt.EditRole):
        #print "setting data", index.row(), index.column(), value.toInt()
        if not index.isValid(): return False
        
        #if index.isValid() and 0 <= index.row() < self._NF:
        ri, cj = index.row(), index.column()
        if cj == C_FIELD:
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
            #_logger.info("Did not set {0}.{1} for real machine".format(
            #    elem.name, fld))
        else:
            #print "Editting pv col=", col, value, value.toDouble()
            # put the value to machine
            vd = value.toDouble()[0]
            #unit = self._unitsys[col-1]

            #_logger.info("Putting {0} to {1}.{2} in role {3}".format(
            #    vd, elem.name, fld, role))
            # need to update model data, otherwise, setEditorData will
            # call model for un-updated value
            #elem.put(fld, vd, unitsys=unit)
            elem.put(fld, vd, unitsys=None)
            #for i in range(len(self._elemrec)): self._update_data(i)
            self._value[row][col-1] = vd
        # update the whole table ?
        #idx0 = self.index(0, 0)
        #idx1 = self.index(len(self._elemrec) - 1, self.columnCount()-1)
        #self.emit(SIGNAL("dataChanged(QModelIndex,QModelIndex)"),
        #          idx0, idx1)
        return True

    def clear(self):
        self._allelems = []
        self._elemrec = []
        self._desc  = []
        self._value = []
        self._unit = []

    
class LatSnapshotDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super(LatSnapshotDelegate, self).__init__(parent)
        self._modified = False

    def paint(self, painter, option, index):
        #if index.column() == SETPOINT:
        #print index.row(), index.column()
        model = index.model()
        row, col = index.row(), index.column()
        QStyledItemDelegate.paint(self, painter, option, index)
        
    def sizeHint(self, option, index):
        fm = option.fontMetrics
        row, col = index.row(), index.column()
        model = index.model()
        if False:
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
            #_logger.warn("Ignore list type values for (%d,%d)" % (row, col))
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
            #_logger.error("unknown editor, can not set its data")
            pass

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

        
class LatSnapshotView(QTableView):
    def __init__(self, parent = None):
        QTableView.__init__(self, parent)
        #self.timerId = self.startTimer(1000)


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

    def setColumnHiddenState(self, state, icol = 0):
        #print icol, state
        if state == Qt.Unchecked:
            self.setColumnHidden(icol, False)
        else:
            self.setColumnHidden(icol, True)

    def setDiffColumnHiddenState(self, state):
        mdl = self.model()
        if not mdl: return

        if state == Qt.Unchecked: s = False
        else: s = True

        for i in range(C_VALUES + 1, mdl.columnCount(), 2):
            self.setColumnHidden(i, s)


class LatSnapshotMain(QDialog):
    def __init__(self, parent = None):
        QDialog.__init__(self, parent)
        #self.model = None
        #self.connect(self, SIGNAL('tabCloseRequested(int)'), self.closeTab)
        #gb = QGroupBox("select")
        fmbox = QGridLayout()
        #fmbox.addRow("S-Range", self.lblRange)

        self.pvBox = QLineEdit()
        self.elemNameBox = QLineEdit()
        self.elemNameBox.setToolTip(
            "list element name and field pattern"
            "Examples are '*', 'HCOR', 'BPM', 'QUAD', 'c*c20a', 'q*g2*'"
            )
        self.elemFldBox = QLineEdit("*")
        #self.elems = elems
        #self.elemCompleter = QCompleter(elems)
        #self.elemBox.setCompleter(self.elemCompleter)

        #self.rangeSlider = qrangeslider.QRangeSlider()
        #self.rangeSlider.setMin(0)
        #self.rangeSlider.setMax(100)
        #self.rangeSlider.setRange(10, 70)
        #self.elemBox.insertSeparator(len(self.elems))
        #fmbox.addRow("Range", self.rangeSlider)
        #fmbox.addWidget(QLabel("Filter"), 0, 0)
        #fmbox.addWidget(self.elemBox, 0, 1)
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
        self.cmbRefDs = QtGui.QComboBox()
        self.cmbRefDs.addItem("Live Data")
        self.cmbRefTp = QtGui.QComboBox()
        self.cmbRefTp.addItem("absolute diff")
        self.cmbRefTp.addItem("relative diff [%]")

        hbelem = QHBoxLayout()
        hbelem.addWidget(self.elemNameBox, 2.0)
        hbelem.addWidget(self.elemFldBox, 1.0)
        hbdiff = QHBoxLayout()
        hbdiff.addWidget(self.cmbRefDs, 2.0)
        hbdiff.addWidget(self.cmbRefTp, 1.0)
        fmbox2.addRow("Reference", hbdiff)
        fmbox2.addRow("Element", hbelem)
        fmbox2.addRow("PV", self.pvBox)
        fmbox2.addRow("Name", self.lblNameField)
        #fmbox2.addRow("Field", self.lblField)
        fmbox2.addRow("Step", self.lblStep)
        #fmbox2.addRow("Range", self.valMeter)
        fmbox2.addRow("Range", self.lblRange)
        fmbox2.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)
        fmbox2.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        #self.fldGroup.setLayout(fmbox2)
        self.btnLoad = QPushButton("Load")
        self.cbxLive = QCheckBox("Live")
        self.cbxLive.setChecked(True)
        self.cbxHidePv = QCheckBox("Hide PV")
        self.cbxHideDiff = QCheckBox("Hide Difference")
        self.cbxHideTimeStamp = QCheckBox("Hide timestamp")
        vbox = QVBoxLayout()
        vbox.addWidget(self.btnLoad)
        vbox.addWidget(self.cbxLive)
        vbox.addWidget(self.cbxHidePv)
        vbox.addWidget(self.cbxHideDiff)
        vbox.addWidget(self.cbxHideTimeStamp)
        vbox.addStretch()
        vbox.addLayout(fmbox2)

        self.extraPlot = QtGui.QFrame()
        self.extraPlot.setFrameStyle(QtGui.QFrame.HLine | QtGui.QFrame.Sunken)
        self.wfplt = ApPlot()
        rhsLayout = QtGui.QVBoxLayout()
        rhsLayout.addWidget(self.wfplt)
        self.extraPlot.setLayout(rhsLayout)
        vbox.addWidget(self.extraPlot)
        self.extraPlot.hide()
        self.model = LatSnapshotTableModel()

        self.tableview = LatSnapshotView()
        #self.tableview.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.tableview.setModel(self.model)
        #self.tableview.setItemDelegate(LatSnapshotDelegate(self))
        self.tableview.setSortingEnabled(True)
        self.tableview.setWhatsThis("double click cell to enter editing mode")
        #fmbox.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)
        self.tableview.resizeColumnsToContents()
        #self.tableview.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        #self.tableview.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)

        sm = self.tableview.selectionModel()
        self.connect(sm, SIGNAL("selectionChanged(QItemSelection,QItemSelection)"),
                     self.selRow)

        self.tabs = QTabWidget()
        self.tabs.addTab(self.tableview, "Table")
        self.plt = ApPlot()
        #self.plt = ApPlot()
        self.plt.insertLegend(Qwt.QwtLegend(), Qwt.QwtPlot.BottomLegend)


        self.tabs.addTab(self.plt, "Plot")
        hbox = QHBoxLayout()
        hbox.addWidget(self.tabs, 1)
        hbox.addLayout(vbox, 0.1)
        #vbox.addWidget(self.fldGroup)
        #cw = QWidget(self)
        #cw.setLayout(hbox)
        #self.setWidget(cw)
        self.setLayout(hbox)

        #self.connect(self.elemBox, SIGNAL("editingFinished()"), 
        #             self.refreshTable)
        #self.connect(self.elemNameBox, SIGNAL("returnPressed()"), 
        #             self.refreshTable)
        #self.connect(self.elemBox, SIGNAL("currentIndexChanged(QString)"),
        #             self.refreshTable)

        self.connect(self.cbxHidePv, SIGNAL("stateChanged(int)"),
                     partial(self.tableview.setColumnHiddenState, icol=C_PV))
        self.connect(self.cbxHideDiff, SIGNAL("stateChanged(int)"),
                     self.tableview.setDiffColumnHiddenState)
        self.connect(self.cmbRefDs, SIGNAL("currentIndexChanged(int)"),
                     self.setModelReferenceData)
        self.connect(self.cmbRefTp, SIGNAL("currentIndexChanged(int)"),
                     self.setModelReferenceData)

        #
        self.connect(self.elemNameBox, SIGNAL("textChanged(QString)"),
                     self.filterTableRows)
        self.connect(self.elemFldBox, SIGNAL("textChanged(QString)"),
                     self.filterTableRows)
        self.connect(self.pvBox, SIGNAL("textChanged(QString)"),
                     self.filterTableRows)
        #
        self.connect(self.btnLoad, SIGNAL("pressed()"), self.loadLatSnapshotH5)

        self.setWindowTitle("Element Editor")
        self.noTableUpdate = True
        #self.cbxHidePv.setChecked(True)

        self.timerId = self.startTimer(1500)

    def selRow(self, i1, i2):
        rows = [i.top() for i in i1]
        if len(rows) != 1: 
            self.extraPlot.hide()
            raise RuntimeError("Invalid selections: {0}".format(rows))
        row = rows[0]
        x, dat = self.model.getSnapshotRecord(row)
        if not x or not dat:
            print "Data is invalid", rows, x, dat
            self.extraPlot.hide()
            return

        p = self.wfplt
        p.curve1.detach()
        p.curve2.detach()
        n = len(dat[0]) // 2
        #p = self.plt
        pens = [QtGui.QPen(Qt.red, 1.0),  QtGui.QPen(Qt.green, 1.0), 
                QtGui.QPen(Qt.blue, 1.0),
                QtGui.QPen(Qt.black, 1.0)]
        symbs = [Qwt.QwtSymbol(Qwt.QwtSymbol.Ellipse,
                               QtGui.QBrush(Qt.red), QtGui.QPen(Qt.black, 1.0),
                               QSize(8, 8)),
                 Qwt.QwtSymbol(Qwt.QwtSymbol.Diamond,
                               QtGui.QBrush(Qt.green), QtGui.QPen(Qt.black, 1.0),
                               QSize(8, 8)),
                 Qwt.QwtSymbol(Qwt.QwtSymbol.Triangle,
                               QtGui.QBrush(Qt.blue), QtGui.QPen(Qt.black, 1.0),
                               QSize(8, 8)),
                 Qwt.QwtSymbol(Qwt.QwtSymbol.Star1,
                               QtGui.QBrush(Qt.black), QtGui.QPen(Qt.black, 1.0),
                               QSize(8, 8))]
        print len(dat), len(dat[0]), min([len(d) for d in dat]), max([len(d) for d in dat])
        n = len(dat) // 2
        if n != len(self.model.dstitle):
            print n, self.model.dstitle, "does not agree"
            for c in p.excurv: c.setData([], [], None)
            self.extraPlot.hide()
            return

        for i in range(n):
            #print "data:", d[i]
            if i >= len(p.excurv):
                p.addCurve(x=x, y=dat[n+i],
                           curveStyle=Qwt.QwtPlotCurve.Lines,
                           curvePen=pens[i % len(pens)],
                           #curveSymbol=symbs[i % len(symbs)],
                           title="%s" % self.model.dstitle[i])
            else:
                p.excurv[i].setData(x, dat[n+i], None)
        p.replot()
        self.extraPlot.show()

        

    def setModelReferenceData(self):
        self.model.dsref[0] = self.cmbRefDs.currentIndex()
        self.model.dsref[1] = self.cmbRefTp.currentIndex()

    def timerEvent(self, e):
        if self.cbxLive.checkState() == Qt.Checked:
            self.model.updateLiveData()
        if self.tabs.currentIndex() == 1:
            p = self.plt
            x, dat = self.model.getSnapshotData()
            if not x or not dat:
                for c in p.excurv: c.setData([], [], None)
                return
            n = len(dat[0]) // 2
            #p = self.plt
            p.curve1.detach()
            p.curve2.detach()
            pens = [QtGui.QPen(Qt.red, 1.0),  QtGui.QPen(Qt.green, 1.0), 
                    QtGui.QPen(Qt.blue, 1.0),
                    QtGui.QPen(Qt.black, 1.0)]
            symbs = [Qwt.QwtSymbol(Qwt.QwtSymbol.Ellipse,
                                   QtGui.QBrush(Qt.red), QtGui.QPen(Qt.black, 1.0),
                                  QSize(8, 8)),
                    Qwt.QwtSymbol(Qwt.QwtSymbol.Diamond,
                                  QtGui.QBrush(Qt.green), QtGui.QPen(Qt.black, 1.0),
                                  QSize(8, 8)),
                    Qwt.QwtSymbol(Qwt.QwtSymbol.Triangle,
                                  QtGui.QBrush(Qt.blue), QtGui.QPen(Qt.black, 1.0),
                                  QSize(8, 8)),
                    Qwt.QwtSymbol(Qwt.QwtSymbol.Star1,
                                  QtGui.QBrush(Qt.black), QtGui.QPen(Qt.black, 1.0),
                                  QSize(8, 8))]
            print len(dat), len(dat[0]), min([len(d) for d in dat]), max([len(d) for d in dat])
            for i in range(n):
                y0 = [d[n+i] for d in dat]
                if i >= len(p.excurv):
                    p.addCurve(x=x, y=y0, curveStyle=Qwt.QwtPlotCurve.Lines,
                               curvePen=pens[i % len(pens)],
                               curveSymbol=symbs[i % len(symbs)],
                               title="DS %d" % i)
                else:
                    p.excurv[i].setData(x, y0, None)
            p.replot()

    def filterTableRows(self):
        name, fld = self.elemNameBox.text(), self.elemFldBox.text()
        pv = self.pvBox.text()
        self.model.filterRows(name, fld, pv)


    def saveLatSnapshotH5(self, fname):
        pass

    def _choose_common_lattice(self, fileNames):
        grps = {}
        for fname in fileNames: 
            f = h5py.File(str(fname), 'r')
            for k,v in f.items():
                if not isinstance(v, h5py.Group): continue
                grps.setdefault(k, 0)
                grps[k] += 1
        dlg = QDialog()
        gp = QGroupBox("Choose Lattice")
        vbox = QVBoxLayout()
        rbt = []
        for k,v in grps.items():
            if v < len(fileNames): continue
            rbt.append(QtGui.QRadioButton(k))
            vbox.addWidget(rbt[-1])
        vbox.addStretch(1)
        if not rbt: return None
        rbt[0].setChecked(True)
        gp.setLayout(vbox)
        vbox2 = QVBoxLayout()
        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok|
                                     QDialogButtonBox.Cancel)
        dlg.connect(buttonBox, SIGNAL("accepted()"), dlg.accept)
        dlg.connect(buttonBox, SIGNAL("rejected()"), dlg.reject)
        vbox2.addWidget(gp)
        vbox2.addWidget(buttonBox)
        dlg.setLayout(vbox2)
        if dlg.exec_() == QDialog.Rejected: return
        latname = ""
        for bt in rbt:
            if bt.isChecked(): 
                return str(bt.text())

        return None
        
    def loadLatSnapshotH5(self, fnames = None):
        if fnames is None:
            dpath = os.environ.get("HLA_DATA_DIR", "")
            fileNames = QtGui.QFileDialog.getOpenFileNames(
                self,
                "Open Data",
                dpath, "Data Files (*.h5 *.hdf5)")
        else:
            fileNames = fnames

        latname = self._choose_common_lattice(fileNames)
        if not latname: return
        
        #print "Accepted the choice:", latname
        for fname in fileNames:
            f = h5py.File(str(fname), 'r')
            ds = f[latname]["__scalars__"]
            pvs   = list(ds[:, "pv"])
            elems = list(ds[:, "element"])
            flds  = list(ds[:, "field"])
            rws   = list(ds[:, "rw"])
            vals  = list(ds[:, "value"])
            ts    = list(ds[:, "timestamp"] )
            wf    = [0] * len(pvs)
            #print ds[:,"element"]
            for k,v in f[latname].items():
                if not k.startswith("wf_"): continue
                pvs.append(v.attrs["pv"])
                elems.append(v.attrs["element"])
                flds.append(v.attrs["field"])
                rws.append(v.attrs["rw"])
                vals.append(list(v))
                ts.append(v.attrs["timestamp"])
                wf.append(len(v))
            self.model.addDataSet(pvs, elems, flds, rws, vals, ts, wf=wf,
                                  title=str(fname))
            self.cmbRefDs.addItem(str(fname))
            f.close()

        self.model.updateLiveData()
        self.model.emit(SIGNAL("layoutChanged()"))
        #print "Model rows:", self.model._rows
        self.tableview.resizeColumnsToContents()

    def refreshTable(self, txt = None):
        return
        elemname = str(self.elemBox.text()) if txt is None else txt
        self.elemBox.selectAll()
        t0 = time.time()
        #elems = [e for e in self.parent().getVisibleElements(elemname)
        #          if e.family in ['BPM', 'COR', 'HCOR']][:40]
        self.sb, self.se = self.parent().getVisibleRange()
        elems = self.parent().getVisibleElements(elemname, self.sb, self.se)
        deadelems = self.parent().getDeadElements()
        #_logger.info("Found elems: {0}".format(len(elems)))
        #QApplication.processEvents()
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
        self.model = LatSnapshotTableModel()
        pvs = ["V:2-SR:C30-BI:G2{PH1:11}SA:X",
               "V:2-SR:C30-BI:G2{PH1:11}SA:Y",
               "V:2-SR:C30-BI:G2{PH2:26}SA:X",
               "V:2-SR:C30-BI:G2{PH2:26}SA:Y",
               "V:2-SR:C30-BI:G4{PM1:55}SA:X",
               "V:2-SR:C30-BI:G4{PM1:55}SA:Y",
               "V:2-SR:C30-BI:G4{PM1:65}SA:X",
               "V:2-SR:C30-BI:G4{PM1:65}SA:Y",
               "V:2-SR:C30-BI:G6{PL1:105}SA:X",
               "V:2-SR:C30-BI:G6{PL1:105}SA:Y"]
    
        e = ["e1", "e1", "e2", "e2"]
        f = ["f4", "f3", "f2", "f1"]
        self.model.addDataSet(pvs[:4], e, f, [1.0, 2.0, 3.0, 4.0],
                              title="DS 1")
        self.model.addDataSet(pvs[:4], e, f,
                              [11.0, 12.0, 13, 14],
                              title="DS 2")
        self.tablev = LatSnapshotView()
        self.tablev.setModel(self.model)
        self.tablev.setItemDelegate(LatSnapshotDelegate(self))
        self.tablev.setSortingEnabled(True)
                                   
        #for i in self.model.subHeadIndex():
        #    self.tablev.setSpan(i, 0, 1, self.model.columnCount()) 
        #for i in range(self.model.columnCount()):
        self.tablev.resizeColumnsToContents()
        
        vbox = QVBoxLayout()
        vbox.addWidget(self.tablev)
        self.setLayout(vbox)

if __name__ == "__main__":
    #app = QApplication(sys.argv)
    #ap.machines.init("nsls2v2")
    #form = MTestForm()
    form = LatSnapshotMain()
    form.resize(900, 500)
    form.show()
    #app.exec_()
    cothread.WaitForQuit()
