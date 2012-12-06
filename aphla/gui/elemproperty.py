"""
A table view for HLA element, with delegates user can modify value online
"""

from PyQt4.QtCore import (QAbstractTableModel, QDataStream, QFile,
        QIODevice, QModelIndex, QRegExp, QSize, QString, QVariant, Qt,
        SIGNAL)
from PyQt4.QtGui import (QColor, QComboBox, QLineEdit, QDoubleSpinBox,
        QSpinBox, QStyle, QStyledItemDelegate, QTextDocument, QTextEdit)

import numpy as np

FIELD, VALUE_RB, VALUE_SP = 0, 1, 2


class ElementPropertyTableModel(QAbstractTableModel):
    def __init__(self, elem):
        super(ElementPropertyTableModel, self).__init__()
        self._elem = elem
        self._field, self._value = [], []
        for var in elem.fields():
            self._field.append(var)
            self._value.append([elem.get(var, 'readback'),
                                elem.get(var, 'setpoint')])
        self._NF = len(self._field)

    def data(self, index, role=Qt.DisplayRole):
        if (not index.isValid() or
            not (0 <= index.row() < self._NF)):
            return QVariant()
        r, col  = index.row(), index.column()
        if role == Qt.DisplayRole:
            if col == FIELD: return QVariant(self._field[r])
            elif col == VALUE_RB: return QVariant(self._value[r][0])
            elif col == VALUE_SP: return QVariant(self._value[r][1])
            
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
            elif section == VALUE_RB: return QVariant("Readback")
            elif section == VALUE_SP: return QVariant("Setpoint")
        return QVariant(int(section+1))

    def flags(self, index):
        if not index.isValid():
            return Qt.ItemIsEnabled
        row, col = index.row(), index.column()
        field = self._field[row]
        if col == VALUE_SP:
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
        QStyledItemDelegate.paint(self, painter, option, index)

    def sizeHint(self, option, index):
        fm = option.fontMetrics
        return QStyledItemDelegate.sizeHint(self, option, index)

    def createEditor(self, parent, option, index):
        row, col = index.row(), index.column()
        if index.column() == VALUE_SP:
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
