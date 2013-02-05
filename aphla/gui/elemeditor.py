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
        QTableWidget, QDialogButtonBox, QTableWidgetItem)

import collections
import numpy as np
import sys
import re
C_FIELD, C_VAL_RAW = 0, 1

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
        self._unitsys = [None, 'phy']
        self._allelems = elems

    def _init_data(self):
        self._elem, self._field, self._src = [], [], []
        for i,elem in enumerate(elems):
            # the head
            self._field.append(None)
            self._elem.append(elem)
            self._rdonly.append(True)
            # every fields, readback and setpoint
            for fld in elem.fields():
                self._field.append(fld) 
                self._elem.append(elem)
                self._src.append('readback')
                if elem.settable(fld):
                    self._field.append(fld)
                    self._elem.append(elem)
                    self._src.append('setpoint')

        nrow = len(self._elem)

        self._desc  = [None] * nrow   # description
        self._value = [[None, None] for i in range(nrow)]
        self._unit = ['' for i in range(nrow)]

        self._update_data(0, nrow, allmeta = True)

    def _get_quiet(self, elem, fld, src, u):
        """get but ignore exceptions"""
        # the value
        try:
            v = elem.get(fld, source=src, unitsys=u)
        except:
            v = None
        # check the unit
        try:
            usymb = elem.getUnit(var, unitsys=u)
        except:
            usymb = ""

        return v, usymb

    def _get_data(self, ielem, iunit):
        """get (readback, setpoint) for element field. None if error"""
        #if ielem >= len(self._elems): return None
        #if self._value[ielem] is None: return None
        #if iunit >=

        elem, fld = self._elem[ielem], self._field[ielem]
        v1, u1 = self._get_quiet(elem, fld, 'readback', self._unitsys[iunit])
        v2, u2 = self._get_quiet(elem, fld, 'setpoint', self._unitsys[iunit])
        
        return v1, v2

    def _update_data_row(self, i):
        elem, fld, src = self._elem[i], self._field[i], self._src[i]

        for icol,u in enumerate(self._unitsys):
            v1, u1 = self._get_quiet(elem, fld, src, u)
            self._value[i][icol] = v1
            self._unit[i][icol]  = u1

        
    def _update_data(self, i0, i1, allmeta = False):
        i0 = max(i0, 0)
        i1 = min(i1, len(self._elem))

        for i in range(i0, i1):
            self._update_data_row(i)
            if allmeta:
                self._desc.append("family = %s\nsb = %.4g\nlength= %.4g\n" \
                                      % (elem.family,elem.sb, elem.length))


    def isHeadIndex(self, i):
        if self._value[i] is None: return True
        else: return False

    def subHeadIndex(self):
        return [i for i,v in enumerate(self._value) if v is None]

    def _format_value(self, val, unit = ""):
        """format as QVariant"""
        if val is None: return QVariant()
        if isinstance(val, (str, unicode)):
            if len(val) < 8: return QVariant(str(val) + unit)
            return QVariant(str(val)[:8]+"... "+unit)
        elif isinstance(val, collections.Iterable):
            return QVariant(str(val)[:8]+"... "+unit)
        else:
            return QVariant("{0:.4g} {1}".format(val, unit))

    def data(self, index, role=Qt.DisplayRole):
        """return data as a QVariant"""
        #print "data model=",role
        if not index.isValid() or index.row() >= self._NF:
            return QVariant()

        row, col  = index.row(), index.column()
        fld, vals = self._field[row], self._value[row]
        unit = self._unit[row][col-1]
        # for each of the role
        if role == Qt.DisplayRole:
            if col == C_FIELD: return QVariant(fld)
            #print r, col, self._field[r], self._value[r]
            if self._value[row] is None: return QVariant()
            # all for display
            if isinstance(self._value[row][col-1], (tuple, list)):
                #return QVariant.fromList([QVariant(v) for v in vals[col-1]])
                return QVariant("[...]")
            elif vals[col-1] is not None:
                #print "converting", val, unit
                #vr, vw = self._get_data(row, col-1)
                #self._value[row] = [vr, vw]
                # readback and unit
                return self._format_value(vals[0], u)
        elif role == Qt.EditRole:
            if col == C_FIELD: return QVariant(fld)
            #print r, col, self._field[r], self._value[r]
            if vals is None: return QVariant()
            if isinstance(vals[col-1], (tuple, list)):
                return QVariant.fromList([QVariant(v) for v in vals[col-1]])
            elif vals[col-1] is not None:
                return QVariant(vals[col-1])
        elif role == Qt.TextAlignmentRole:
            if col == C_FIELD: return QVariant(Qt.AlignLeft|Qt.AlignBottom)
            else: return QVariant(Qt.AlignRight|Qt.AlignBottom)
        elif role == Qt.ToolTipRole:
            if self._value[row] is None:
                return QVariant(self._desc[row])
            else:
                col > C_FIELD and 
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
            if self._elemidx[section] is not None:
                return QVariant(self._elemidx[section] + 1)
            else:
                return QVariant()
        return QVariant(int(section+1))

    def flags(self, index):
        if not index.isValid():
            return Qt.ItemIsEnabled
        row, col = index.row(), index.column()
        field = self._field[row]
        if self._value[row] is None: return Qt.ItemIsEnabled
        elif re.match(self._editablefld, self._field[row]):
            #print "found editable", self._field[row], 
            if self._value[row][col-1] is not None:
                #print "Y"
                return Qt.ItemFlags(
                    QAbstractTableModel.flags(self, index)|
                    Qt.ItemIsEditable)
            else:
                pass
                #print "N"
        else:
            return Qt.ItemIsEnabled
        
        return Qt.ItemIsEnabled

    def rowCount(self, index=QModelIndex()):
        return len(self._field)
    
    def columnCount(self, index=QModelIndex()):
        return len(self._unitsys) + 1

    def isList(self, index):
        r, c = index.row(), index.column()
        if c == 0: return False
        return isinstance(self._value[r][c-1], (list, tuple))

    def setData(self, index, value, role=Qt.EditRole):
        #print "setting data", index.row(), index.column()
        if index.isValid() and 0 <= index.row() < self._NF:
            row, col = index.row(), index.column()
            if col == C_FIELD:
                #print "Editting property, ignore"
                pass
            elif value.canConvert(QVariant.List):
                val = [v.toFloat()[0] for v in value.toList()]
                self._value[row][col-1] = val
            else:
                #print "Editting pv col=", col, value, value.toDouble()
                # put the value to machine
                fld = self._field[row][:-3]
                vd = value.toDouble()[0]
                unit = self._unitsys[col-1]
                k = self._elemidx[row]
                elem = self._allelems[k].put(fld, vd, unitsys=unit)
                self._value[row][col-1] = vd
            self.emit(SIGNAL("dataChanged(QModelIndex,QModelIndex)"),
                      index, index)
            return True
        return False

    def updateData(self):
        for i in range(self.rowCount()):
            self._update_element(i)


class ElementPropertyDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super(ElementPropertyDelegate, self).__init__(parent)

    def paint(self, painter, option, index):
        #if index.column() == SETPOINT:
        #print index.row(), index.column()
        model = index.model()
        row, col = index.row(), index.column()
        if index.column() == 0 and model.isHeadIndex(index.row()):
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
            return QSize(5, fm.height())
        elif col == 0:
            text = index.model().data(index).toString()
            document = QTextDocument()
            document.setDefaultFont(option.font)
            document.setHtml(text)
            return QSize(document.idealWidth() + 5, fm.height())
            
        return QStyledItemDelegate.sizeHint(self, option, index)

    def createEditor(self, parent, option, index):
        row, col = index.row(), index.column()
        model = index.model()
        print "Creating editor", row, col, model._value[row]
        if model._value[row] is not None and model._field[row].endswith('_w'):
            #spinbox = QDoubleSpinBox(parent)
            #spinbox.setRange(-100, 100)
            #spinbox.setSingleStep(2)
            #spinbox.setAlignment(Qt.AlignRight|Qt.AlignVCenter)
            #spinbox.setValue(self._value[row][1])
            #return spinbox
            led = QLineEdit(parent)
            led.setText("")
            led.setAlignment(Qt.AlignRight|Qt.AlignVCenter)
            self.connect(led, SIGNAL("returnPressed()"),
                         self.commitAndCloseEditor)
            return led
        elif isinstance(model._value[row][col-1], collections.Iterable):
            print "Ignore list type values"
            pass
        else:
            print "Can not create editor"
            return QStyledItemDelegate.createEditor(self, parent, option,
                                                    index)

    def commitAndCloseEditor(self):
        editor = self.sender()
        if isinstance(editor, (QTextEdit, QLineEdit)):
            self.emit(SIGNAL("commitData(QWidget*)"), editor)
            self.emit(SIGNAL("closeEditor(QWidget*)"), editor)

    def setEditorData(self, editor, index):
        text = index.model().data(index, Qt.DisplayRole).toString()
        print "Setting editor to", text
        if index.column() == C_VAL_RAW or index.column() == VALUE_SP:
            value = text.toDouble()[0]
            #print text, value
            #value = index.model().data(index, Qt.DisplayRole)
            #editor.setValue(value)
            editor.setText(text)
        else:
            QStyledItemDelegate.setEditorData(self, editor, index)

    def setModelData(self, editor, model, index):
        print "Setting model", editor.text()
        if index.column() >= C_VAL_RAW:
            model.setData(index, QVariant(editor.text()))
        else:
            QStyledItemDelegate.setModelData(self, editor, model, index)

    def editorEvent(self, event, model, option, index):
        # MouseButtonDblClick 4
        # MouseButtonPress 2
        # MouseButtonRelease 3
        print "received an editor event:", event.type()
        if event.type() == QEvent.MouseButtonDblClick and model.isList(index):
            print "Popup list editor"
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


class ElementEditorDock(QDockWidget):
    def __init__(self, parent, elems=[]):
        QDockWidget.__init__(self, parent)
        self.model = None
        #self.connect(self, SIGNAL('tabCloseRequested(int)'), self.closeTab)
        gb = QGroupBox("select")
        hbox = QHBoxLayout()
        self.elemBox = QComboBox()
        self.elems = elems
        for e in self.elems: self.elemBox.addItem(e)
        self.elemBox.insertSeparator(len(self.elems))
        self.refreshBtn = QPushButton("refresh")
        hbox.addWidget(self.elemBox)
        hbox.addWidget(self.refreshBtn)
        hbox.setStretch(0, 1.0)
        hbox.setStretch(1, 0.0)
        gb.setLayout(hbox)
        
        vbox = QVBoxLayout()
        vbox.addWidget(gb)
        self.tableview = QTableView()
        vbox.addWidget(self.tableview)

        cw = QWidget()
        cw.setLayout(vbox)
        self.setWidget(cw)

        self.connect(self.refreshBtn, SIGNAL("clicked()"), self.refreshTable)
        #self.connect(self.elemBox, SIGNAL("currentIndexChanged(QString)"),
        #             self.refreshTable)

        self.setWindowTitle("Element Editor")
        self.noTableUpdate = True

    def refreshTable(self):
        elemname = str(self.elemBox.currentText())
        elems = self.parent().getVisibleElements(elemname)
        self._addElements(elems)

    def refreshBox(self):
        self.noTableUpdate = True
        self.elemBox.clear()
        self.noTableUpdate = False

    def processCell(self, index):
        print "Process cell", index.row(), index.column()

    def _addElements(self, elems):
        #self.setVisible(True)
        #print "new element:", elemnames
        #if elems is None:
        #    QMessageBox.warning(self, "Element Not Found",
        #                        "element " + str(elemnames) + " not found")
        #    return
            #print elem.name, elem.sb, elem.fields()
        self.model = ElementPropertyTableModel(elems=elems)
        self.tableview.setModel(self.model)
        self.tableview.setItemDelegate(ElementPropertyDelegate(self))
        for i in self.model.subHeadIndex():
            self.tableview.setSpan(i, 0, 1, self.model.columnCount()) 
        #for i in range(self.model.columnCount()):
        self.tableview.resizeColumnsToContents()
        #rz = self.tableview.geometry()
        ncol = self.tableview.model().columnCount()
        #fullwidth = sum([self.tableview.columnWidth(i) for i in range(ncol)])
        #self.tableview.setMinimumWidth(fullwidth+20)
        #self.tableview.setMaximumWidth(fullwidth+60)
        #self.tableview.adjustSize()
        self.connect(self.tableview, SIGNAL("clicked(QModelIndex)"), 
                     self.processCell)
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

    def closeTab(self, index):
        self.removeTab(index)
        if self.count() <= 0: self.setVisible(False)

    def setEnabled(self, v):
        self.elemBox.setEnabled(v)
        self.refreshBtn.setEnabled(v)

    def updateModelData(self):
        if self.model: self.model.updateData()

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
