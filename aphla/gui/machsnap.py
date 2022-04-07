from __future__ import print_function, division, absolute_import

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
from PyQt4.QtGui import (QCheckBox,
        QColor, QComboBox, QLineEdit, QDoubleSpinBox,
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

from aporbitplot import ApPlotWidget

C_ELEMVAR, C_PVSTR = 0, 1
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


class SnapshotTableModel(QAbstractTableModel):
    def __init__(self):
        super(SnapshotTableModel, self).__init__()
        # elem obj, name/fld, handle
        self._elemvar = []
        self._pvstr = []
        # the data
        self._snaplist = []
        self._livedata = []

    def addSnapshot(self, fname):
        import h5py
        f = h5py.File(fname, 'r')
        grp = f['V2SR']
        self._snaplist.append([None] * len(self._elemvar))
        for k,v in grp.items():
            try:
                i = self._elemvar.index(k)
            except:
                self._elemvar.append(k)
                self._pvstr.append(v.attrs['pv'])
                for s in self._snaplist: s.append(None)
                self._snaplist[-1][-1] = v

    def _update_data(self, i):
        pass

    def isHeadIndex(self, i):
        pass

    def subHeadIndex(self):
        pass

    def _format_value(self, val, unit = ""):
        """format as QVariant"""
        if val is None: return QVariant()
        if isinstance(val, (str, unicode)):
            if len(val) < 8: return QVariant(str(val) + unit)
            return QVariant(str(val)[:8]+"... "+unit)
        elif isinstance(val, collections.abc.Iterable):
            return QVariant(str(val)[:8]+"... "+unit)
        else:
            return QVariant("{0:.4g} {1}".format(val, unit))

    def data(self, index, role=Qt.DisplayRole):
        """return data as a QVariant"""
        r, col  = index.row(), index.column()
        isnap = col - (C_PVSTR + 1)
        #print "data model=",role, r, col, isnap, len(self._snaplist)
        if role == Qt.DisplayRole:
            if col == C_ELEMVAR:
                return QVariant(self._elemvar[r])
            elif col == C_PVSTR:
                return QVariant(str(self._pvstr[r]))
            elif isnap < len(self._snaplist):
                return QVariant(str(self._snaplist[isnap][r][0,0]))

        return QVariant()

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.TextAlignmentRole:
            if orientation == Qt.Horizontal:
                return QVariant(int(Qt.AlignLeft|Qt.AlignVCenter))
            return QVariant(int(Qt.AlignRight|Qt.AlignVCenter))
        if role != Qt.DisplayRole:
            return QVariant()
        if orientation == Qt.Horizontal:
            if section == C_ELEMVAR:
                return QVariant("Element & Field")
            if section == C_PVSTR:
                return QVariant("EPICS PV")

        return QVariant(int(section+1))

    def flags(self, index):
        return Qt.ItemIsEnabled

    def rowCount(self, index=QModelIndex()):
        return len(self._elemvar)

    def columnCount(self, index=QModelIndex()):
        return 3 + len(self._snaplist) + 1

    def clear(self):
        self._allelems = []
        self._elemrec = []
        self._desc  = []
        self._value = []
        self._unit = []


class SnapshotItemDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super(SnapshotItemDelegate, self).__init__(parent)
        self._modified = False

    def paint(self, painter, option, index):
        model = index.model()
        row, col = index.row(), index.column()
        QStyledItemDelegate.paint(self, painter, option, index)

    def sizeHint(self, option, index):
        return QStyledItemDelegate.sizeHint(self, option, index)

    def createEditor(self, parent, option, index):
        return QStyledItemDelegate.createEditor(self, parent, option,
                                                index)

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


class SnapshotTableView(QTableView):
    def __init__(self, parent = None):
        QTableView.__init__(self, parent)
        self.timerId = self.startTimer(3000)


    def disableElement(self, checked=True, irow=-1):
        if irow < 0: return
        print("Disable element:", irow)
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
    def __init__(self, parent, elems=[]):
        QDockWidget.__init__(self, parent)
        self.model = None
        #self.connect(self, SIGNAL('tabCloseRequested(int)'), self.closeTab)
        #gb = QGroupBox("select")
        fmbox = QFormLayout()

        #fmbox.addRow("S-Range", self.lblRange)

        self.elemBox = QLineEdit()
        self.elemBox.setToolTip(
            "list elements within the range of the active plot.<br>"
            "Examples are '*', 'HCOR', 'BPM', 'QUAD', 'c*c20a', 'q*g2*'"
            )
        self.elems = elems
        self.elemCompleter = QCompleter(elems)
        self.elemBox.setCompleter(self.elemCompleter)
        #self.elemBox.insertSeparator(len(self.elems))
        fmbox.addRow("Filter", self.elemBox)
        #self.refreshBtn = QPushButton("refresh")
        #fmbox.addRow(self.elemBox)

        self.fldGroup = QGroupBox()
        fmbox2 = QFormLayout()
        self.lblName  = QLabel()
        self.lblField = QLabel()
        self.lblStep  = QLabel()
        self.lblRange = QLabel()
        self.valMeter = Qwt.QwtThermo()
        self.valMeter.setOrientation(Qt.Horizontal, Qwt.QwtThermo.BottomScale)
        self.valMeter.setSizePolicy(QSizePolicy.MinimumExpanding,
                                    QSizePolicy.Fixed)
        self.valMeter.setEnabled(False)
        #fmbox2.addRow("Name", self.lblName)
        #fmbox2.addRow("Field", self.lblField)
        fmbox2.addRow("Step", self.lblStep)
        #fmbox2.addRow("Range", self.valMeter)
        fmbox2.addRow("Range", self.lblRange)
        #fmbox2.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)
        fmbox2.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        self.fldGroup.setLayout(fmbox2)


        self.model = None
        self.delegate = None
        self.tableview = ElementPropertyView()
        #self.tableview.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.tableview.setWhatsThis("double click cell to enter editing mode")
        fmbox.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)
        vbox = QVBoxLayout()
        vbox.addLayout(fmbox)
        vbox.addWidget(self.tableview)
        vbox.addWidget(self.fldGroup)
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
        elemname = str(self.elemBox.text())
        if txt is not None: elemname = txt
        self.elemBox.selectAll()
        t0 = time.time()
        #elems = [e for e in self.parent().getVisibleElements(elemname)
        #          if e.family in ['BPM', 'COR', 'HCOR']][:40]
        elems = self.parent().getVisibleElements(elemname)
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
        print("DT:", t1 - t0, t2 - t1, t3 - t2)
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
        if True:
            self.lblRange.setText(str(bd))
        elif bd is None or bd[0] is None or bd[1] is None:
            self.valMeter.setEnabled(False)
        else:
            rg = Qwt.QwtDoubleInterval(bd[0], bd[1])
            self.valMeter.setScale(rg, (bd[1]-bd[0])/2.01)
            self.valMeter.setValue(elem.get(fld, unitsys = None))
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

class MTestForm(QDialog):
    def __init__(self, parent=None):
        super(MTestForm, self).__init__(parent)
        self.model = SnapshotTableModel()
        self.model.addSnapshot('test.h5')
        self.tablev = QTableView()
        self.tablev.setModel(self.model)
        self.tablev.setItemDelegate(SnapshotItemDelegate(self))
        #for i in range(self.model.columnCount()):
        self.tablev.resizeColumnsToContents()
        self.tablev.setColumnHidden(1, True)

        hb1 = QHBoxLayout()
        vb2 = QVBoxLayout()
        vb2.addWidget(ApPlotWidget(), 1.0)

        vb3a = QVBoxLayout()
        cb = QCheckBox("show PV")
        self.connect(cb, SIGNAL("stateChanged(int)"), self._set_pv_view)
        vb3a.addWidget(cb)
        vb3a.addStretch()

        vb3b = QVBoxLayout()
        vb3b.addWidget(QPushButton("Refresh"))
        vb3b.addWidget(QPushButton("Plot"))
        vb3b.addWidget(QPushButton("Ramp"))
        vb3b.addStretch()

        hb2 = QHBoxLayout()
        hb2.addLayout(vb3a, 1.0)
        hb2.addLayout(vb3b)

        vb2.addLayout(hb2)
        hb1.addWidget(self.tablev, .6)
        hb1.addLayout(vb2, 0.4)
        self.setLayout(hb1)

    def _set_pv_view(self, st):
        if st == Qt.Checked: self.tablev.setColumnHidden(1, False)
        elif st == Qt.Unchecked: self.tablev.setColumnHidden(1, True)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    import aphla as ap
    form = MTestForm()
    form.resize(400, 300)
    form.show()
    app.exec_()
