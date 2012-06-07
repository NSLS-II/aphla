"""
A table view for HLA element, with delegates user can modify value online
"""

from PyQt4.QtCore import (QAbstractTableModel, QDataStream, QFile,
        QIODevice, QModelIndex, QRegExp, QSize, QString, QVariant, Qt,
        SIGNAL)
from PyQt4.QtGui import (QColor, QComboBox, QLineEdit, QDoubleSpinBox,
        QSpinBox, QStyle, QStyledItemDelegate, QTextDocument, QTextEdit)

import numpy as np

FIELD, VALUE = 0, 1


class ElementPropertyTableModel(QAbstractTableModel):
    def __init__(self, elem):
        super(ElementPropertyTableModel, self).__init__()
        self._elem = elem
        self._field, self._value = [], []
        for var in dir(elem):
            try:
                callable(getattr(elem, var))
            except:
                continue
            if callable(getattr(elem, var)): continue
            if var.startswith('_'): continue
            if var in elem.fields() and elem.settable(var):
                self._field.append((var+".SP", 'setpoint'))
                #self._value.append(elem.get(var, 'setpoint'))
                self._value.append(1e6)

                self._field.append((var+".RB", 'setpoint'))
                #self._value.append(elem.get(var, 'readback'))
                self._value.append(1e6)
            else:
                self._field.append((var, None))
                self._value.append(getattr(elem, var))
                #self._value.append(1e6)
                
            print "field record:", self._field[-1], self._value[-1]
        self._NF = len(self._field)

    def data(self, index, role=Qt.DisplayRole):
        if (not index.isValid() or
            not (0 <= index.row() < self._NF)):
            return QVariant()
        r, col  = index.row(), index.column()
        if role == Qt.DisplayRole:
            if col == FIELD: return QVariant(self._field[r][0])
            elif col == VALUE: return QVariant(self._value[r])
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
            elif section == VALUE: return QVariant("Value")
        return QVariant(int(section+1))

    def flags(self, index):
        if not index.isValid():
            return Qt.ItemIsEnabled
        row, col = index.row(), index.column()
        field = self._field[row][0]
        if field[:-3] in self._elem.fields():
            if field[-3:] == '.SP':
                if index.column() == VALUE:
                    return Qt.ItemFlags(
                        QAbstractTableModel.flags(self, index)|
                        Qt.ItemIsEditable)
            else:
                return Qt.ItemIsEnabled

        else:
            return Qt.ItemIsEnabled

    def rowCount(self, index=QModelIndex()):
        return len(self._field)
    
    def columnCount(self, index=QModelIndex()):
        return 2

    def setData(self, index, value, role=Qt.EditRole):
        print "setting data"
        if index.isValid() and 0 <= index.row() < self._NF:
            row, col = index.row(), index.column()
            if col == FIELD:
                print "Editting property"
            elif col == VALUE:
                print "Editting pv"
                self._value[row] = value
            self.emit(SIGNAL("dataChanged(QModelIndex,QModelIndex)"),
                      index, index)
            return True
        return False

    
class ElementPropertyDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super(ElementPropertyDelegate, self).__init__(parent)

    def paint(self, painter, option, index):
        #if index.column() == SETPOINT:
        QStyledItemDelegate.paint(self, painter, option, index)

    def sizeHint(self, option, index):
        fm = option.fontMetrics
        return QStyledItemDelegate.sizeHint(self, option, index)

    def createEditor(self, parent, option, index):
        if index.column() == VALUE:
            spinbox = QDoubleSpinBox(parent)
            spinbox.setRange(-100, 100)
            spinbox.setSingleStep(2)
            spinbox.setAlignment(Qt.AlignRight|Qt.AlignVCenter)
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
        if text.contains("http://") >= 0:
            editor.setValue(text)
        elif index.column() == VALUE:
            value = text.toDouble()[0]
            editor.setValue(value)
        else:
            QStyledItemDelegate.setEditorData(self, editor, index)

    def setModelData(self, editor, model, index):
        if index.column() == VALUE:
            model.setData(index, QVariant(editor.value()))
        else:
            QStyledItemDelegate.setModelData(self, editor, model, index)
