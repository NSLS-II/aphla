"""
Element Property Editor
=======================

:author: Lingyun Yang <lyyang@bnl.gov>

list all properties of element, provide editing.

A table view for HLA element, with delegates user can modify value online
"""

from PyQt4.QtCore import (QAbstractTableModel, QDataStream, QFile,
        QIODevice, QModelIndex, QRegExp, QSize, QString, QVariant, Qt,
                          SIGNAL)
from PyQt4.QtGui import (QColor, QComboBox, QLineEdit, QDoubleSpinBox,
                         QSpinBox, QStyle, QStyledItemDelegate, QTextDocument, QTextEdit, QDialog,
                         QDockWidget, QGroupBox, QPushButton, QHBoxLayout, QGridLayout, QVBoxLayout, QTableView, QWidget, QApplication)

import collections
import numpy as np
import sys
FIELD, VALUE_RB, VALUE_SP = 0, 1, 2


class ElementPropertyTableModel(QAbstractTableModel):
    def __init__(self, elems):
        super(ElementPropertyTableModel, self).__init__()
        self._elems = elems
        self._field, self._value = [], []
        self._units = [None, 'phy']
        self._phyunit = []
        self._idx = []

        self._load()

    def _load(self):
        ik = 0
        for elem in self._elems:
            self._field.append("<b>%s</b>" % elem.name)
            self._value.append(None)
            self._idx.append(ik)
            self._phyunit.append(None)
            for var in sorted(elem.fields()):
                for src,s in [('readback', '.r'), ('setpoint', '.w')]:
                    vlst = []
                    for u in self._units:
                        try:
                            v = elem.get(var, source=src, unit=u)
                            usymb = elem.getUnit(var, unitsys=u)
                        except:
                            v = None
                            usymb = ""

                        vlst.append([v, usymb])
                    if not any([v[0] for v in vlst]): continue
                    self._field.append(var + s)
                    self._value.append(vlst)
                    self._idx.append(None)
            ik += 1
        self._NF = len(self._field)
        #print self._value

    def isHeadIndex(self, i):
        if self._value[i] is None: return True
        else: return False

    def subHeadIndex(self):
        return [i for i,v in enumerate(self._value) if v is None]

    def _format_value(self, *v):
        """format as QVariant"""
        if v[0] is None: return QVariant()
        unit = ""
        if len(v) > 1 and v[1]: unit = " [%s]" % v[1]
        if isinstance(v[0], (str, unicode)):
            if len(v[0]) < 8: return QVariant(str(v[0]) + unit)
            return QVariant(str(v[0])[:8]+"..."+unit)
        elif isinstance(v[0], collections.Iterable):
            return QVariant(str(v[0])[:8]+"..."+unit)
        else:
            return QVariant("{0:.7g}{1}".format(v[0], unit))

    def data(self, index, role=Qt.DisplayRole):
        if (not index.isValid() or
            not (0 <= index.row() < self._NF)):
            #print "Asking for data", index.row(), index.column(), "--"
            return QVariant()
        r, col  = index.row(), index.column()
        if role == Qt.DisplayRole:
            #print "Asking for data", index.row(), index.column(), \
            #    self._field[r], self._value[r]
            if col == FIELD: return QVariant(self._field[r])
            if self._value[r] is None: return QVariant()

            if col == VALUE_RB: return self._format_value(*(self._value[r][0]))
            elif col == VALUE_SP and self._value[r]:
                if self._value[r][1]:
                    return self._format_value(*(self._value[r][1]))
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
            if section == FIELD: return QVariant("Field")
            elif section == VALUE_RB: return QVariant("None(Raw)")
            elif section == VALUE_SP: return QVariant("phy")
        elif orientation == Qt.Vertical:
            if self._idx[section] is not None:
                return QVariant(self._idx[section] + 1)
            else:
                return QVariant()
        return QVariant(int(section+1))

    def flags(self, index):
        if not index.isValid():
            return Qt.ItemIsEnabled
        row, col = index.row(), index.column()
        field = self._field[row]
        if self._value[row] is None: return Qt.ItemIsEnabled
        elif self._field[row].endswith('.w'):
            return Qt.ItemFlags(
                QAbstractTableModel.flags(self, index)|
                Qt.ItemIsEditable)
        else:
            return Qt.ItemIsEnabled

    def rowCount(self, index=QModelIndex()):
        return len(self._field)
    
    def columnCount(self, index=QModelIndex()):
        return 3

    def setData(self, index, value, role=Qt.EditRole):
        print "setting data"
        if index.isValid() and 0 <= index.row() < self._NF:
            row, col = index.row(), index.column()
            if col == FIELD:
                print "Editting property"
            elif col == VALUE_SP:
                print "Editting pv"
                self._value[row][1] = value
            self.emit(SIGNAL("dataChanged(QModelIndex,QModelIndex)"),
                      index, index)
            return True
        return False

    
class ElementPropertyDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super(ElementPropertyDelegate, self).__init__(parent)

    def paint(self, painter, option, index):
        #if index.column() == SETPOINT:
        #print index.row(), index.column()
        model = index.model()
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
        if model._value[row] is not None and model._field[row].endswith('.w'):
            spinbox = QDoubleSpinBox(parent)
            spinbox.setRange(-100, 100)
            spinbox.setSingleStep(2)
            spinbox.setAlignment(Qt.AlignRight|Qt.AlignVCenter)
            #spinbox.setValue(self._value[row][1])
            return spinbox
        else:
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
        if index.column() == VALUE_SP:
            value = text.toDouble()[0]
            editor.setValue(value)
        else:
            QStyledItemDelegate.setEditorData(self, editor, index)

    def setModelData(self, editor, model, index):
        if index.column() == VALUE_SP:
            model.setData(index, QVariant(editor.value()))
        else:
            QStyledItemDelegate.setModelData(self, editor, model, index)


class ElementEditorDock(QDockWidget):
    def __init__(self, parent, elems=[]):
        QDockWidget.__init__(self, parent)
        #self.connect(self, SIGNAL('tabCloseRequested(int)'), self.closeTab)
        gb = QGroupBox("range")
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

    def _addElements(self, elems):
        #self.setVisible(True)
        #print "new element:", elemnames
        #if elems is None:
        #    QMessageBox.warning(self, "Element Not Found",
        #                        "element " + str(elemnames) + " not found")
        #    return
            #print elem.name, elem.sb, elem.fields()
        self.tableview.setModel(ElementPropertyTableModel(elems=elems))
        self.tableview.setItemDelegate(ElementPropertyDelegate(self))
        self.tableview.resizeColumnsToContents()
        #rz = self.tableview.geometry()
        ncol = self.tableview.model().columnCount()
        fullwidth = sum([self.tableview.columnWidth(i) for i in range(ncol)])
        self.tableview.setMinimumWidth(fullwidth+20)
        #self.tableview.setMaximumWidth(fullwidth+60)
        self.tableview.adjustSize()

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


class MTestForm(QDialog):
    def __init__(self, parent=None):
        super(MTestForm, self).__init__(parent)
        elems = ap.getElements("C10")
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
    form.show()
    app.exec_()
