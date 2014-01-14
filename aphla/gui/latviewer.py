"""
Lattice Viewer
=======================

:author: Lingyun Yang <lyyang@bnl.gov>

list all properties of lattice.
"""

import cothread
if __name__ == "__main__":
    app = cothread.iqt()

import aphla
import pvmanager

from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import (QAbstractTableModel, QDataStream, QFile,
        QIODevice, QModelIndex, QRegExp, QSize, QString, QVariant, Qt,
        SIGNAL, QEvent)
from PyQt4.QtGui import (QColor, QComboBox, QLineEdit, QDoubleSpinBox,
        QSpinBox, QStyle, QStyledItemDelegate, QTextDocument, QTextEdit, 
        QDialog, QDockWidget, QGroupBox, QPushButton, QHBoxLayout, 
        QGridLayout, QVBoxLayout, QTableView, QWidget, QApplication,
        QTableWidget, QDialogButtonBox, QStatusBar, QTableWidgetItem,
        QFormLayout, QLabel, QSizePolicy, QCompleter, QMenu, QAction,
        QTabWidget, QCheckBox, QMessageBox)
import PyQt4.Qwt5 as Qwt
from aporbitplot import ApPlot
from pvmanager import CaDataMonitor
#import traceback
import collections
import numpy as np
import os
import sys, time
from functools import partial
from fnmatch import fnmatch
import qrangeslider
import h5py
from datetime import datetime, date, time

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
        # mach data + a list of values from each dataset
        self.values = [None] + [v for v in values]
        self.hlvalues = {}
        self.ts = 0.0
        self.numerical = True
        self.diffs = [None for i in range(len(self.values))]
        self.dead  = [False for i in range(len(self.values))]

    def __str__(self):
        v = "{0}".format(self.values)
        return "{0}, {1}, {2}, {3}".format(self.pv, self.element,
                                           self.field, v)
    def __repr__(self):
        v = "{0}".format(self.values)
        return "{0}, {1}, {2}, {3}".format(self.pv, self.element,
                                           self.field, v)

    def _update_abs_diff(self, iref):
        for i,v in enumerate(self.values):
            if self.dead[i]:
                self.diffs[i] = None
            elif v is None:
                self.diffs[i] = None
            elif self.values[iref] is None:
                self.diffs[i] = None
            elif self.wf == 0:
                self.diffs[i] = v - self.values[iref]
            elif self.wf >= 1:
                #for j,vj in enumerate(v):
                #    try:
                #        self.diffs[i][j] = vj - self.values[iref][j]
                #    except:
                #        self.diffs[i][j] = None
                self.diffs[i] = None
            else:
                raise RuntimeError(
                    "unknown data for diff {0} {1} {2} {3}\n wf={4}".format(
                        self.element, self.field, self.pv, self.values,
                        self.wf))

    def _update_rel_diff(self, iref):
        for i,v in enumerate(self.diffs):
            if v is None or self.values[iref] is None:
                self.diffs[i] = None
            elif self.wf == 0 and self.values[iref] == 0.0:
                #self.diffs[i] = np.inf
                self.diffs[i] = None
            elif self.wf == 0:
                self.diffs[i] = v / self.values[iref]
            elif self.wf == 1:
                for j,vj in enumerate(v):
                    vr = self.values[iref][j]
                    if vr == 0.0:
                        #self.diffs[i][j] = np.inf
                        self.diffs[i][j] = None
                    else:
                        self.diffs[i][j] = vj / vr

    def updateDiff(self, iref, mode):
        """calculate the difference, relative or absolute, returns None if 
        the data does not make sense"""
        n = len(self.values)
        try:
            if self.dead[iref]:
                for i in range(n): self.diffs[i] = None
                return
        except:
            print self.pv, n, len(self.dead), self.values, self.diffs, self.dead
            raise

        self._update_abs_diff(iref)
        if mode == 1:
            self._update_rel_diff(iref)

class LatSnapshotSortFilterProxyModel(QtGui.QSortFilterProxyModel):
    def __init__(self, parent = None):
        super(LatSnapshotSortFilterProxyModel, self).__init__(parent)
        self.fltFld = ""
        self.fltPv  = ""

    def filterAcceptsRow(self, srcRow, srcParent):
        i0 = self.sourceModel().index(srcRow, 0, srcParent)
        i1 = self.sourceModel().index(srcRow, 1, srcParent)
        i2 = self.sourceModel().index(srcRow, 2, srcParent)
        name = self.sourceModel().data(i0).toString()
        fld  = self.sourceModel().data(i1).toString()
        pv   = self.sourceModel().data(i2).toString()

        return name.contains(self.filterRegExp()) and \
            fld.contains(self.fltFld) and \
            pv.contains(self.fltPv)

class LatSnapshotTableModel(QAbstractTableModel):
    def __init__(self):
        super(LatSnapshotTableModel, self).__init__()
        #self._cadata = pvmanager.CaDataMonitor([])
        self._cadata = pvmanager.CaDataGetter([])
        self._rows = []
        self._mask   = []
        self.dstitle = ["Last Shot"]
        self.dstimestamp = [0.0]
        self.dsref = [0, 0] # last shot data as reference, abs diff


    def updateCells(self, **kwargs):
        i0 = kwargs.get("i0", 0)
        i1 = kwargs.get("i1", len(self._rows))
        
        for i in range(i0, i1):
            r = self._rows[i]
            # ignore dead PV.
            if r.dead[0]: continue
            if self._cadata.dead(r.pv):
                r.dead[0] = True
                continue
            self._rows[i].values[0] = self._cadata.get(r.pv, None)
            self._rows[i].updateDiff(*self.dsref)
        idx0 = self.index(i0, self.columnCount() - 1)
        idx1 = self.index(i1, self.columnCount() - 1)

        self.emit(SIGNAL("dataChanged(QModelIndex,QModelIndex)"),
                  idx0, idx1)

    def _choose_common_lattice(self, fileNames):
        grps = {}
        for fname in fileNames: 
            f = h5py.File(str(fname), 'r')
            for k,v in f.items():
                if not isinstance(v, h5py.Group): continue
                grps.setdefault(k, 0)
                grps[k] += 1
        print grps
        comm_lat = [k for k,v in grps.items() if v == len(fileNames)]
        if len(comm_lat) == 1: return comm_lat[0]

        # need to choose one common lattice
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

    def loadSnapshotH5(self, fnames):
        if fnames is None:
            dpath = os.environ.get("HLA_DATA_DIR", "")
            fileNames = QtGui.QFileDialog.getOpenFileNames(
                None,
                "Open Data",
                dpath, "Data Files (*.h5 *.hdf5)")
        else:
            fileNames = fnames

        print "Checking files:", fileNames
        latname = self._choose_common_lattice(fileNames)
        if not latname: return
        
        print "Accepted the choice:", latname
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
            # read waveforms
            for k,v in f[latname].items():
                if not k.startswith("wf_"): continue
                pvs.append(v.attrs["pv"])
                elems.append(v.attrs["element"])
                flds.append(v.attrs["field"])
                rws.append(v.attrs["rw"])
                vals.append(list(v))
                ts.append(v.attrs["timestamp"])
                wf.append(len(v))
            self.addDataSet(pvs, elems, flds, rws, vals, ts, wf=wf,
                                  title=str(fname))
            f.close()

        self.updateCells()
        self.emit(SIGNAL("layoutChanged()"))

        return [str(fname) for fname in fileNames]


    def addDataSet(self, pvs, elements, fields, rw, values, ts, **kwarg):
        wf = kwarg.get("wf", [0] * len(pvs))
        # assume no duplicate PV in pvs
        mpv = {}
        for i,r in enumerate(self._rows):
            mpv.setdefault(r.pv, [])
            mpv[r.pv].append(i)

        # expand one column for each row
        nset = len(self.dstitle) - 1
        for i,pv in enumerate(pvs):
            idx = mpv.get(pv, [])
            for j in idx:
                # if find existing record by (name,field)
                if elements[i] == self._rows[j].element and \
                   fields[i] == self._rows[j].field:
                    self._rows[j].values.append(values[i])
                    self._rows[j].diffs.append(None)
                    self._rows[j].dead.append(False)
                    break
            else:
                # pv could be duplicate
                # a new record
                vals = [None] * nset + [values[i]]
                r = SnapshotRow(pv, elements[i], fields[i], rw[i], vals,
                                ts[i], wf[i])
                self._rows.append(r)
                self._mask.append(0)

        self._cadata.addPv(pvs)
        self.dstitle.append(kwarg.get("title", ""))
        self.dstimestamp.append(max(ts))
        print "ds:", len(self.dstitle), self.dstitle, len(self._rows[0].values)

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
        validrows =  [ r for i,r in enumerate(self._rows) 
                      if self._mask[i] == 0 ]
        #self.removeRows(0, len(validrows))
        n0 = len(validrows)
        for i,r in enumerate(self._rows):
            if fnmatch(r.element, "*%s*" % name) and \
               fnmatch(r.field, "*%s*" % field) and \
               fnmatch(r.pv, "*%s*" % pv) and self._mask[i] < 2:
                self._mask[i] = 0
                continue
            elif self._mask[i] == 0:
                self._mask[i] = 1
        #print "Sum of mask:", np.sum(self._mask)
        idx0 = self.index(0, self.columnCount() - 1)
        idx1 = self.index(len(self._rows), self.columnCount() - 1)

        validrows =  [ r for i,r in enumerate(self._rows) 
                      if self._mask[i] == 0 ]
        n1 = len(validrows)
        self.insertRows(0, len(validrows))

        self.emit(SIGNAL("dataChanged(QModelIndex,QModelIndex)"),
                  idx0, idx1)
        #self.emit(SIGNAL("layoutChanged()"))
        #print "mask updated"
        #print idx0, idx1


    def getSnapshotRecord(self, idx):
        n = 0
        for i,r in enumerate(self._rows):
            if self._mask[i]: continue
            n += 1
            if n == idx: return r
        return None

    def getSnapshotData(self):
        return [r for i,r in enumerate(self._rows) if self._mask[i] == 0]

    def getDiffs(self):
        idx, diffs = [], []
        for i,r in enumerate(self._rows):
            if self._mask[i]: continue
            idx.append(i)
            diffs.append(r.diffs)
        return idx, diffs

    def _ca_to_qvariant(self, val, **kwargs):
        """convert ca_* to qvariant data"""
        if val is None: return QVariant()
        elif isinstance(val, cothread.dbr.ca_float): return QVariant(float(val))
        elif isinstance(val, cothread.dbr.ca_int): return QVariant(int(val))
        else:
            pv = kwargs.get("pv", "")
            raise RuntimeError("invalid data type {0} "
                               "(pv={1}, pvmanager={2},{3})".format(
                                   type(val), kwargs.get("pv", ""),
                                   type(self._cadata.get(pv, None)),
                                   type(self._cadata.data.get(pv, None))))


    def data(self, index, role=Qt.DisplayRole):
        """return data as a QVariant"""
        #print "data model=",role
        if not index.isValid() or index.row() >= len(self._rows):
            return QVariant()

        ri, cj  = index.row(), index.column()
        ids, idsj = divmod(cj - C_VALUES, 2)

        r = self._rows[ri]
        if role == Qt.DisplayRole:
            if cj == C_PV:
                return QVariant(QString(r.pv))
            elif cj == C_ELEMENT: return QVariant(QString(r.element))
            elif cj == C_FIELD: return QVariant(QString(r.field))
            elif cj == C_RW: return QVariant(r.rw)

            # the values columns
            if r.wf: return QVariant("[...]")
            # the live data is not available
            # the data sections
            # fmt = "%.6g"
            #print r.element, r.field, cothread.catools.caget(r.pv), r.values, r.diffs

            if r.dead[ids] and idsj == 0:
                return QVariant(QString("Disconnected"))
            elif cj == C_VALUES: return self._ca_to_qvariant(r.values[0])

            if idsj == 0: val = r.values[ids]
            elif idsj == 1: val = r.diffs[ids]

            if val is None: return QVariant()
            elif isinstance(val, float): return QVariant(float(val))
            elif isinstance(val, int): return QVariant(int(val))
            else: return QVariant(QString(str(val)))

            # all for display
        #elif role == Qt.TextAlignmentRole:
        #    if cj == C_FIELD: return QVariant(Qt.AlignLeft | Qt.AlignVCenter)
        #    else: return QVariant(Qt.AlignRight | Qt.AlignBottom)
        #elif role == Qt.ToolTipRole:
        #    if col == C_FIELD and self._desc[r]:
        #        return QVariant(self._desc[r])
        elif role == Qt.ForegroundRole:
            if ids >= 0 and r.dead[ids] and idsj == 0:
                return QColor(Qt.white)
        elif role == Qt.BackgroundRole:
            if ids >= 0 and r.dead[ids] and idsj == 0:
                return QColor(Qt.red)
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
            ids, idsj = divmod(section-C_VALUES, 2)
            if ids < len(self.dstitle) and idsj == 1: return QVariant("diff")
            elif ids < len(self.dstitle) and idsj == 0:
                #print "ds:", len(self.dstimestamp), len(self.dstitle), ids
                ts = self.dstimestamp[ids]
                return QVariant("%s\n%s" % (
                    os.path.basename(self.dstitle[ids]), 
                    datetime.fromtimestamp(ts)))
            return QVariant()
        elif orientation == Qt.Vertical:
            validrows = [r for i,r in enumerate(self._rows) if self._mask[i] == 0]
            if section >= len(validrows): return QVariant()
            return QVariant(section)

        return QVariant()

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
        #validrows = [i for i in range(len(self._rows)) if self._mask[i] == 0]
        #return len(validrows)
        return len(self._rows)

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
        #self.update_count = 0
        #self.timerId = self.startTimer(2000)
        self.headers = self.horizontalHeader()
        self.headers.setContextMenuPolicy(Qt.CustomContextMenu)
        self.headers.customContextMenuRequested.connect(self.show_header)
        self.headers.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)

    def show_header(self, position):
        print "Position", position, self.headers.logicalIndexAt(position)
        for i in range(self.headers.count()):
            print self.headers.headerData(i, Qt.Horizontal)
        cmenu = QMenu()
        #c = QApplication.clipboard()
        #    cmenu.addAction("&Copy", 
        #                    partial(c.setText, d.toString()), "CTRL+C")
        #    cmenu.addAction("Copy Column", partial(self.copy_pvs, c.setText))
        #cmenu.exec_(e.globalPos())


    def contextMenuEvent(self, e):
        mdl = self.model()
        idx = self.indexAt(e.pos())
        d = mdl.data(idx, role=Qt.DisplayRole)
        irow = self.rowAt(e.y())
        icol = self.columnAt(e.x())
        #print "Row:", self.rowAt(e.y())
        cmenu = QMenu()
        c = QApplication.clipboard()
        if icol == C_PV:
            cmenu.addAction("&Copy", 
                            partial(c.setText, d.toString()), "CTRL+C")
            cmenu.addAction("Copy Column", partial(self.copy_pvs, c.setText))
        cmenu.exec_(e.globalPos())


    def copy_pvs(self, f, full=False):
        mdl = self.model()
        if full:
            s = "\n".join([r.pv for r in mdl._rows])
        else:
            valid = mdl.getSnapshotData()
            s = "\n".join([r.pv for r in valid])
        f(s)

    def setColumnHiddenState(self, state, icol = 0):
        #print icol, state
        if state == Qt.Unchecked:
            self.setColumnHidden(icol, False)
            #self.showColumn(icol)
        else:
            self.setColumnHidden(icol, True)
            #self.hideColumn(icol)

    def setDiffColumnHiddenState(self, state):
        mdl = self.model()
        if not mdl: return

        if state == Qt.Unchecked: s = False
        else: s = True

        for i in range(C_VALUES + 1, mdl.columnCount(), 2):
            self.setColumnHidden(i, s)

class SnapshotViewerWidget(QWidget):
    def __init__(self, parent, latdict, mach, logger):
        super(SnapshotViewerWidget, self).__init__(parent)

        self._lat_dict = latdict
        self._cur_mach = mach
        self._logger = logger
        #self.model = None
        #self.connect(self, SIGNAL('tabCloseRequested(int)'), self.closeTab)
        #gb = QGroupBox("select")
        fmbox = QGridLayout()
        #fmbox.addRow("S-Range", self.lblRange)

        self.pvBox = QLineEdit()
        self.elemNameBox = QLineEdit()
        self.elemNameBox.setToolTip(
            "list element name filter, xamples are 'c*c20a', 'q*g2*'"
            )
        self.elemFldBox = QLineEdit("")

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
        self.cmbRefDs.addItem("Last Shot")
        self.cmbRefTp = QtGui.QComboBox()
        self.cmbRefTp.addItem("Absolute diff")
        self.cmbRefTp.addItem("Relative diff [%]")

        fmbox2.addRow("Reference", self.cmbRefDs)
        fmbox2.addRow("Difference", self.cmbRefTp)
        fmbox2.addRow("Element", self.elemNameBox)
        fmbox2.addRow("Field", self.elemFldBox)
        fmbox2.addRow("PV", self.pvBox)
        #fmbox2.addRow("Name", self.lblNameField)
        #fmbox2.addRow("Step", self.lblStep)
        #fmbox2.addRow("Range", self.lblRange)
        fmbox2.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)
        fmbox2.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        #self.fldGroup.setLayout(fmbox2)
        tblFltBox = QtGui.QGroupBox("Filter")
        tblFltBox.setLayout(fmbox2)

        tblGrpBox = QtGui.QGroupBox("Lattice Data")
        #self.cbxLive = QCheckBox("Live")
        #self.cbxLive.setChecked(True)
        self.cbxHidePv        = QCheckBox("Hide PV")
        self.cbxHideReadback  = QCheckBox("Hide Readback")
        self.cbxHideDiff      = QCheckBox("Hide Difference")
        self.cbxHideTimeStamp = QCheckBox("Hide timestamp")
        vbox1 = QVBoxLayout()
        #vbox1.addWidget(self.cbxLive)
        vbox1.addWidget(self.cbxHidePv)
        vbox1.addWidget(self.cbxHideReadback)
        vbox1.addWidget(self.cbxHideDiff)
        vbox1.addWidget(self.cbxHideTimeStamp)
        vbox1.addStretch()
        tblGrpBox.setLayout(vbox1)

        gbox1 = QGridLayout()
        self.btnLoad    = QPushButton("Load...")
        self.btnSave    = QPushButton("Save")
        self.btnOneshot = QPushButton("One Shot")
        self.btnPut     = QPushButton("Put")
        self.btnRamp    = QPushButton("Ramp")
        gbox1.addWidget(self.btnLoad, 0, 0)
        gbox1.addWidget(self.btnSave, 0, 1)
        gbox1.addWidget(self.btnOneshot, 0, 2)
        gbox1.addWidget(self.btnPut, 0, 3)
        gbox1.addWidget(self.btnRamp, 1, 0)
        #btnFrm = QtGui.QFrame()
        #btnFrm.setFrameStyle(QtGui.QFrame.VLine | QtGui.QFrame.Sunken)
        #hbox1.addWidget(btnFrm)
        #hbox1.addLayout(vbox2, 0.0)

        self.extraPlot = QtGui.QFrame()
        self.extraPlot.setFrameStyle(QtGui.QFrame.HLine | QtGui.QFrame.Sunken)
        self.wfplt = ApPlot()
        rhsLayout = QtGui.QVBoxLayout()
        rhsLayout.addWidget(self.wfplt)
        self.extraPlot.setLayout(rhsLayout)
        self.extraPlot.hide()

        vbox = QVBoxLayout()

        vbox.addWidget(tblFltBox, 0.0)
        vbox.addWidget(self.extraPlot, 10.0)
        vbox.addWidget(tblGrpBox, 0.0)
        vbox.addStretch()
        vbox.addLayout(gbox1, 0.0)

        self.model = LatSnapshotTableModel()
        self.proxymodel = LatSnapshotSortFilterProxyModel()
        self.proxymodel.setSourceModel(self.model)
        self.proxymodel.setDynamicSortFilter(True)

        self.tableview = LatSnapshotView()
        #self.tableview.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        #self.tableview.setModel(self.model)
        self.tableview.setModel(self.proxymodel)
        #self.tableview.setItemDelegate(LatSnapshotDelegate(self))
        self.tableview.setSortingEnabled(True)
        self.tableview.setWhatsThis("double click cell to enter editing mode")
        #fmbox.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)
        self.tableview.resizeColumnsToContents()
        #self.tableview.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        #self.tableview.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)

        sm = self.tableview.selectionModel()
        self.connect(
            sm, SIGNAL("selectionChanged(QItemSelection,QItemSelection)"),
            self.selRow)

        self.plt = ApPlot()
        #self.plt = ApPlot()
        self.plt.insertLegend(Qwt.QwtLegend(), Qwt.QwtPlot.BottomLegend)
        self.plt.curve1.detach()
        self.plt.curve2.detach()
        self.plt.hide()

        hbox = QHBoxLayout()
        hbox.addWidget(self.tableview, 2)
        hbox.addLayout(vbox, 0)
        #vbox.addWidget(self.fldGroup)
        #cw = QWidget(self)
        #cw.setLayout(hbox)
        #self.setWidget(cw)
        vbox2 = QVBoxLayout()
        vbox2.addWidget(self.plt, 0.0)
        vbox2.addLayout(hbox, 1.0)

        self.setLayout(vbox2)

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
                     self.filterChanged)
        self.connect(self.elemFldBox, SIGNAL("textChanged(QString)"),
                     self.filterChanged)
        self.connect(self.pvBox, SIGNAL("textChanged(QString)"),
                     self.filterChanged)
        #
        self.connect(self.btnLoad, SIGNAL("pressed()"), self.loadSnapshotH5)
        self.connect(self.btnOneshot, SIGNAL("pressed()"), self._dead_button)
        self.connect(self.btnPut, SIGNAL("pressed()"), self._dead_button)
        self.connect(self.btnRamp, SIGNAL("pressed()"), self._dead_button)

        self.setWindowTitle("Snapshot Tool")
        self.noTableUpdate = True
        #self.cbxHidePv.setChecked(True)

        #self.timerId = self.startTimer(1500)

    def filterChanged(self, txt):
        self.proxymodel.fltFld  = self.elemFldBox.text()
        self.proxymodel.fltPv = self.pvBox.text()
        rx = QtCore.QRegExp(self.elemNameBox.text(),
                            Qt.CaseInsensitive,
                            QtCore.QRegExp.Wildcard)
        self.proxymodel.setFilterRegExp(rx)

    def selRow(self, i1, i2):
        rows = [i.top() for i in i1]
        if not rows: return

        if len(rows) != 1: 
            self.extraPlot.hide()
            raise RuntimeError("Invalid selections: {0}".format(rows))
        #print rows
        row = rows[0]
        r = self.model.getSnapshotRecord(row)
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
        #print len(dat), len(dat[0]), min([len(d) for d in dat]), max([len(d) for d in dat])
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
        if e.timerId() != self.timerId: return
        #if self.cbxLive.checkState() == Qt.Unchecked: return
            #self.tabs.currentIndex() =?= 0

        self.model.updateCells()

        #    self.model.updateLiveData()
        #    #self.model.updateVisibleData()
        if True:
            p = self.plt
            idx, diffs = self.model.getDiffs()
            if not idx or not diffs:
                for c in p.excurv: c.setData([], [], None)
                return
            #p = self.plt
            pens = [QtGui.QPen(Qt.red, 1.0),  QtGui.QPen(Qt.green, 1.0), 
                    QtGui.QPen(Qt.blue, 1.0),
                    QtGui.QPen(Qt.black, 1.0)]
            symbs = [
                Qwt.QwtSymbol(Qwt.QwtSymbol.Ellipse,
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
            #print len(dat), len(dat[0]), min([len(d) for d in dat]), max([len(d) for d in dat])
            for i in range(len(self.model.dstitle)):
                x, y = [], []
                if i >= len(p.excurv):
                    print "Add a new line:", i
                    p.addCurve(x=x, y=y, curveStyle=Qwt.QwtPlotCurve.Lines,
                               curvePen=pens[i % len(pens)],
                               curveSymbol=symbs[i % len(symbs)],
                               title=str(self.model.dstitle[i]))
                #if i == self.model.dsref[0]: continue
                #p.excurv[i].detach()
                for j,v in enumerate(diffs):
                    if i >= len(v): continue
                    if v[i] is None: continue
                    x.append(idx[j])
                    y.append(v[i])
                    if not isinstance(v[i], (float, int)):
                        raise RuntimeError("invalid data i={0}, {1}".format(
                            i, v[i]))
                #print "Size:", len(x), len(y), y[:5]
                p.excurv[i].setData(x, y, None)
                #p.excurv[i].attach(p)
            p.replot()
            #print "reploted"


    def filterTableRows(self):
        name, fld = self.elemNameBox.text(), self.elemFldBox.text()
        pv = self.pvBox.text()
        #n0 = self.model.rowCount()
        self.model.filterRows(name, fld, pv)
        #n1 = self.model.rowCount()
        #for i in range(n1, n0):
        #    self.tableview.hideRow(i)

    #def saveLatSnapshotH5(self):
    #    snapdlg.exec_()

    def _dead_button(self):
        QtGui.QMessageBox.warning(self, "Not Implemented",
                            "This is not implemented yet")

    def loadSnapshotH5(self, fnames = None):
        #st = self.cbxLive.checkState()
        #self.cbxLive.setCheckState(Qt.Unchecked)
        fnames = ['/Users/lyyang/devel/nsls2-hla/nsls2v2/2013_12/Untitled.h5']
        for fname in self.model.loadSnapshotH5(fnames):
            self.cmbRefDs.addItem(str(fname))

        self.tableview.resizeColumnsToContents()
        #self.tableview.setVisible(False)
        #self.tableview.resizeColumnToContents(C_ELEMENT)
        #self.tableview.resizeColumnToContents(C_FIELD)
        #self.tableview.resizeColumnToContents(C_RW)
        #self.tableview.setVisible(True)
        #self.cbxLive.setCheckState(st)

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

class SaveSnapshotWidget(QWidget):
    def __init__(self, parent, machs, mach, logger):
        super(SaveSnapshotWidget, self).__init__(parent)
        self._lat_dict = machs
        self._cur_mach = mach
        self._logger = logger
        self._pvlst = {}
        #self.fldGroup = QGroupBox()
        self.lblNameField  = QLabel()
        self.lblStep  = QLabel()
        self.lblRange = QLabel()
        self.valMeter = Qwt.QwtThermo()
        self.valMeter.setOrientation(Qt.Horizontal, Qwt.QwtThermo.BottomScale)
        self.valMeter.setSizePolicy(QSizePolicy.MinimumExpanding, 
                                    QSizePolicy.Fixed)
        self.valMeter.setEnabled(False)
        self.cmbMach = QtGui.QComboBox()
        for k in self._lat_dict.keys():
            self.cmbMach.addItem(k)
        if self._cur_mach:
            i = self.cmbMach.findText(self._cur_mach)
            self.cmbMach.setCurrentIndex(i)

        self.cmbLat = QtGui.QComboBox()
        self.cmbLat.addItem("*")
        for k in self._lat_dict.get(str(self.cmbMach.currentText()), {}).keys():
            self.cmbLat.addItem(k)
        self.cmbLat.setCurrentIndex(0)

        self.btnBrowsePv = QtGui.QPushButton("Browse...")
        gdbox = QtGui.QGridLayout()
        for i,(lbl,wid) in enumerate([("Machine:", self.cmbMach),
                                      ("Lattice:", self.cmbLat),
                                      ("Extra PVs:", self.btnBrowsePv)]):
            hbox = QtGui.QHBoxLayout()
            hbox.addWidget(QLabel(lbl))
            hbox.addWidget(wid)
            hbox.addStretch()
            gdbox.addLayout(hbox, 0, i)

        self.tblPvs = QtGui.QTableWidget()

        vbox2 = QtGui.QVBoxLayout()
        vbox2.addLayout(gdbox)
        vbox2.addWidget(self.tblPvs)

        hbox2 = QtGui.QHBoxLayout()
        self.btnSave = QtGui.QPushButton("Save...")
        hbox2.addStretch()
        hbox2.addWidget(self.btnSave)
        vbox2.addLayout(hbox2)

        self.setLayout(vbox2)

        self.connect(self.cmbMach, SIGNAL("currentIndexChanged(QString)"),
                     self.update_latlist)
        self.connect(self.cmbLat, SIGNAL("currentIndexChanged(QString)"),
                     self.update_pvlist)
        self.connect(self.btnSave, SIGNAL("clicked()"), self.saveSnapshot)

        self.update_pvlist()
        self.setMinimumWidth(600)

    def _prepare_parent_dirs(self, mach=""):
        dt = datetime.now()
        dpath = os.path.join(os.environ.get("HLA_DATA_DIR", ""),
                             mach, dt.strftime("%Y_%m"))
        if os.path.exists(dpath): return dpath

        r = QtGui.QMessageBox.question(
            self, "Create directories",
            "The default directories do not exist<br>"
            "%s<br>"
            "Create them ?" % dpath,
            QtGui.QMessageBox.Yes | QMessageBox.No)
        if r == QMessageBox.Yes: 
            qd = QtCore.QDir()
            qd.mkpath(dpath)
            self._logger.info("created '%s'" % dpath)
            return dpath
        return False

    def update_latlist(self, mach):
        self.cmbLat.clear()
        self.cmbLat.addItem("*")
        for latname in self._lat_dict.get(mach, {}).keys():
            self.cmbLat.addItem(latname)
        self.update_pvlist()

    def update_pvtable(self):
        self.tblPvs.clear()
        self.tblPvs.setColumnCount(8)
        npvs = sum([len(pvs) for k,pvs in self._pvlst.items()])
        self.tblPvs.setRowCount(npvs)
        stat = {}
        for lat,pvlst in self._pvlst.items():
            for i,pvr in enumerate(pvlst):
                pv, name, fam, fld, rw = pvr
                self.tblPvs.setItem(i,0, QtGui.QTableWidgetItem(pv))
                self.tblPvs.setItem(i,2, QtGui.QTableWidgetItem(name))
                self.tblPvs.setItem(i,3, QtGui.QTableWidgetItem(fam))
                self.tblPvs.setItem(i,4, QtGui.QTableWidgetItem(fld))
                self.tblPvs.setItem(i,5, QtGui.QTableWidgetItem(lat))
                self.tblPvs.setItem(i,6, QtGui.QTableWidgetItem(rw))
                stat.setdefault(fam, 0)
                stat[fam] += 1
        self.tblPvs.resizeColumnToContents(0)
        s = ", ".join(["%s: %d" % (k,v) for k,v in stat.items()])
        if self._logger: self._logger.info("archived: %s" % s)

    def update_pvlist(self):
        machname = str(self.cmbMach.currentText())
        self._pvlst = {}
        for latname,lat in self._lat_dict[machname].items():
            if str(self.cmbLat.currentText()) not in ["*", latname]:
                continue
            pvs = aphla.lattice.saveArchivePvs(lat)
            self._pvlst[latname] = pvs
        self.update_pvtable()

    def saveSnapshot(self):
        mach = str(self.cmbMach.currentText())
        dpath = self._prepare_parent_dirs(mach)
        if not dpath:
            QMessageBox.warning(self, "Abort", "Aborted")
            return
        dt = datetime.now()
        fname_pref = os.path.join(dpath, dt.strftime("snapshot_%d_%H%M%S_"))
        fname = fname_pref + mach + ".hdf5"
        if self.cmbLat.currentText() != "*":
            fname = fname_pref + str(self.cmbLat.currentText()) + ".hdf5"
        print fname

        fileName = QtGui.QFileDialog.getSaveFileName(
            self, "Save Lattice Snapshot Data",
            QString(fname),
            "Data Files (*.h5 *.hdf5);;All Files(*)")
        fileName = str(fileName)
        if not fileName: return
        idx0 = 0
        for latname,allpvr in self._pvlst.items():
            pvs = [pvr[0] for pvr in allpvr]
            dat = aphla.catools.readPvs(pvs)
            for j,d in enumerate(dat):
                i = j + idx0
                if d is None:
                    val, dt = "", ""
                    self.tblPvs.setItem(i,1, QtGui.QTableWidgetItem(val))
                    self.tblPvs.setItem(i,7, QtGui.QTableWidgetItem(dt))
                    self.tblPvs.item(i,0).setBackground(Qt.red)
                    self.tblPvs.item(i,1).setBackground(Qt.red)
                else:
                    val, dt = "{0}".format(d[0]), datetime.fromtimestamp(d[2])
                    if d[1] is not None and d[1] > 2:
                        val = "[{0} ...]".format(d[0][0])
                    self.tblPvs.setItem(i,1, QtGui.QTableWidgetItem(val))
                    self.tblPvs.setItem(i,7, QtGui.QTableWidgetItem(str(dt)))
                    #self.tblPvs.item(i,1).setBackground(Qt.green)
                    #self.tblPvs.item(i,1).setBackground(Qt.green)
            vals = [d[0] if d is not None else None for d in dat]
            size = [d[1] if d is not None else None for d in dat]
            tmstamp = [d[2] if d is not None else None for d in dat]
            elemnames, fams, flds, rbsp = zip(*allpvr)[1:]
            aphla.lattice.saveSnapshot(fileName, latname, 
                                       pvs, vals, size, tmstamp, rbsp,
                                       elemnames, flds, mode='w')
            self._logger.info("snapshot '%s' created: '%s'" % (
                    latname, fileName))
            idx0 += len(pvs)

        self.tblPvs.setVisible(False)
        self.tblPvs.resizeColumnsToContents()
        self.tblPvs.setVisible(True)


class LatSnapshotMain(QDialog):
    def __init__(self, parent, latdict, mach, logger):
        QDialog.__init__(self, parent)
        self.setWindowFlags(Qt.WindowCloseButtonHint|Qt.WindowMinMaxButtonsHint)
        snapview = SnapshotViewerWidget(self, latdict, mach, logger)
        snapsave = SaveSnapshotWidget(self, latdict, mach, logger)
        
        tabs = QTabWidget()
        tabs.addTab(snapview, "View")
        tabs.addTab(snapsave, "Save")
        vbox = QVBoxLayout()
        vbox.addWidget(tabs)
        self.setLayout(vbox)

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
    lat0, latdict = aphla.machines.load("nsls2v2", return_lattices=True)
    form = LatSnapshotMain(None, {"nsls2v2": latdict}, "nsls2v2", None)
    form.resize(1024, 700)
    #fname = "/epics/data/aphla/data/2013_11/snapshot_08_102731_SR.hdf5"
    #form.loadLatSnapshotH5([fname])
    form.show()
    #app.exec_()
    cothread.WaitForQuit()
