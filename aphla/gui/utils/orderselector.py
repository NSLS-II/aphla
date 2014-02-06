import sip
sip.setapi('QString', 2)
sip.setapi('QVariant', 2)

import sys

from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import (SIGNAL, QSize, QObject)
from PyQt4.QtGui import (QGridLayout, QVBoxLayout, QSplitter, QSpacerItem,
                         QLabel, QListView, QStandardItem, QStandardItemModel,
                         QSizePolicy, QPushButton, QIcon, QAbstractItemView,
                         QItemSelectionModel, QDialog, QWidget,
                         QDialogButtonBox)

import gui_icons

########################################################################
class OrderSelector(QObject):
    """"""

    #----------------------------------------------------------------------
    def __init__(self, parentWidget, full_string_list,
                 init_selected_string_list = None,
                 permanently_selected_string_list = None,
                 label_text_NotSelected = 'NOT Visible Column Names:',
                 label_text_Selected = 'Visible Column Names:'):
        """Constructor"""

        QObject.__init__(self)

        self.parentWidget = parentWidget
        self.label_text_NotSelected = label_text_NotSelected
        self.label_text_Selected = label_text_Selected

        self.model = OrderSelectorModel(full_string_list,
            init_selected_string_list=init_selected_string_list,
            permanently_selected_string_list=permanently_selected_string_list)
        self.view = OrderSelectorView(parentWidget,
                                      label_text_NotSelected,
                                      label_text_Selected,
                                      self.model)

        self.connect(self.view.pushButton_right_arrow, SIGNAL('clicked()'),
                     self.view.on_right_arrow_press)
        self.connect(self.view.pushButton_left_arrow, SIGNAL('clicked()'),
                     self.view.on_left_arrow_press)
        self.connect(self.view.pushButton_up_arrow, SIGNAL('clicked()'),
                     self.view.on_up_arrow_press)
        self.connect(self.view.pushButton_down_arrow, SIGNAL('clicked()'),
                     self.view.on_down_arrow_press)




########################################################################
class OrderSelectorModel(QObject):
    """"""

    #----------------------------------------------------------------------
    def __init__(self, full_string_list, init_selected_string_list=None,
                 permanently_selected_string_list=None):
        """Constructor"""

        QObject.__init__(self)

        self.output = []

        if not self.hasNoDuplicateStrings(full_string_list):
            raise ValueError('Duplicate strings detected in full string list.')
        else:
            self.full_string_list = full_string_list[:]

        if init_selected_string_list is not None:
            if not self.allStringsInList1FoundInList2(
                init_selected_string_list, self.full_string_list):
                raise ValueError('Some of the strings in initially selected string list are not in full string list.')
        else:
            init_selected_string_list = []

        if permanently_selected_string_list is not None:
            if not self.allStringsInList1FoundInList2(
                permanently_selected_string_list, init_selected_string_list):
                raise ValueError('Some of the strings in permanently selected string list are not in initially selected string list.')
        else:
            permanently_selected_string_list = []

        self.permanently_selected_string_list = permanently_selected_string_list[:]

        self.model_Selected = QStandardItemModel()
        self.model_NotSelected = QStandardItemModel()

        Selected_item_list = [None for s in init_selected_string_list]
        NotSelected_item_list = []
        for s in self.full_string_list:
            item = QStandardItem(s)
            try:
                Selected_item_list[init_selected_string_list.index(s)] = item
            except:
                NotSelected_item_list.append(item)

        for item in NotSelected_item_list: self.model_NotSelected.appendRow(item)
        for item in Selected_item_list: self.model_Selected.appendRow(item)

    #----------------------------------------------------------------------
    def getSelectedList(self):
        """"""

        selectedList = []
        for i in range(self.model_Selected.rowCount()):
            selectedList.append(self.model_Selected.item(i,0).text())

        return selectedList


    #----------------------------------------------------------------------
    def hasNoDuplicateStrings(self, full_string_list):
        """"""

        str_list = full_string_list
        str_set = set(full_string_list)

        if len(str_list) == len(str_set):
            return True
        else:
            return False

    #----------------------------------------------------------------------
    def allStringsInList1FoundInList2(self, str_list_1, str_list_2):
        """"""

        stringsNotFound = [ s for s in str_list_1
                            if s not in str_list_2 ]

        if stringsNotFound != []:
            return False
        else:
            return True


########################################################################
class OrderSelectorView(QObject):
    """"""

    #----------------------------------------------------------------------
    def __init__(self, parentWidget,
                 label_text_NotSelected, label_text_Selected,
                 model):
        """Constructor"""

        QObject.__init__(self)

        self.model = model

        self.gridLayout = QGridLayout(parentWidget)

        self.verticalLayout_left_list = QVBoxLayout()
        self.label_NotSelected = QLabel(parentWidget)
        self.label_NotSelected.setText(label_text_NotSelected)
        self.verticalLayout_left_list.addWidget(self.label_NotSelected)
        self.listView_NotSelected = QListView(parentWidget)
        self.verticalLayout_left_list.addWidget(self.listView_NotSelected)
        self.gridLayout.addLayout(self.verticalLayout_left_list, 0, 0, 1, 2)

        self.verticalLayout_right_left = QVBoxLayout()
        spacerItem = QSpacerItem(20,178,QSizePolicy.Minimum,QSizePolicy.Expanding)
        self.verticalLayout_right_left.addItem(spacerItem)
        self.pushButton_right_arrow = QPushButton(parentWidget)
        sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalPolicy(0)
        sizePolicy.setHeightForWidth(
            self.pushButton_right_arrow.sizePolicy().hasHeightForWidth())
        self.pushButton_right_arrow.setSizePolicy(sizePolicy)
        self.pushButton_right_arrow.setMinimumSize(QSize(50,50))
        self.pushButton_right_arrow.setMaximumSize(QSize(50,50))
        self.pushButton_right_arrow.setIcon(QIcon(':/right_arrow.png'))
        self.pushButton_right_arrow.setIconSize(QSize(50,50))
        self.pushButton_right_arrow.setText('')
        self.verticalLayout_right_left.addWidget(self.pushButton_right_arrow)
        self.pushButton_left_arrow = QPushButton(parentWidget)
        sizePolicy.setHeightForWidth(
            self.pushButton_left_arrow.sizePolicy().hasHeightForWidth())
        self.pushButton_left_arrow.setSizePolicy(sizePolicy)
        self.pushButton_left_arrow.setMinimumSize(QSize(50,50))
        self.pushButton_left_arrow.setMaximumSize(QSize(50,50))
        self.pushButton_left_arrow.setIcon(QIcon(':/left_arrow.png'))
        self.pushButton_left_arrow.setIconSize(QSize(50,50))
        self.pushButton_left_arrow.setText('')
        self.verticalLayout_right_left.addWidget(self.pushButton_left_arrow)
        spacerItem = QSpacerItem(20,178,QSizePolicy.Minimum,QSizePolicy.Expanding)
        self.verticalLayout_right_left.addItem(spacerItem)
        self.gridLayout.addLayout(self.verticalLayout_right_left, 0, 2, 1, 1)

        self.verticalLayout_right_list = QVBoxLayout()
        self.label_Selected = QLabel(parentWidget)
        self.label_Selected.setText(label_text_Selected)
        self.verticalLayout_right_list.addWidget(self.label_Selected)
        self.listView_Selected = QListView(parentWidget)
        self.verticalLayout_right_list.addWidget(self.listView_Selected)
        self.gridLayout.addLayout(self.verticalLayout_right_list, 0, 3, 1, 2)

        self.verticalLayout_up_down = QVBoxLayout()
        spacerItem = QSpacerItem(20,178,QSizePolicy.Minimum,QSizePolicy.Expanding)
        self.verticalLayout_up_down.addItem(spacerItem)
        self.pushButton_up_arrow = QPushButton(parentWidget)
        sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalPolicy(0)
        sizePolicy.setHeightForWidth(
            self.pushButton_up_arrow.sizePolicy().hasHeightForWidth())
        self.pushButton_up_arrow.setSizePolicy(sizePolicy)
        self.pushButton_up_arrow.setMinimumSize(QSize(50,50))
        self.pushButton_up_arrow.setMaximumSize(QSize(50,50))
        self.pushButton_up_arrow.setIcon(QIcon(':/up_arrow.png'))
        self.pushButton_up_arrow.setIconSize(QSize(50,50))
        self.pushButton_up_arrow.setText('')
        self.verticalLayout_up_down.addWidget(self.pushButton_up_arrow)
        self.pushButton_down_arrow = QPushButton(parentWidget)
        sizePolicy.setHeightForWidth(
            self.pushButton_down_arrow.sizePolicy().hasHeightForWidth())
        self.pushButton_down_arrow.setSizePolicy(sizePolicy)
        self.pushButton_down_arrow.setMinimumSize(QSize(50,50))
        self.pushButton_down_arrow.setMaximumSize(QSize(50,50))
        self.pushButton_down_arrow.setIcon(QIcon(':/down_arrow.png'))
        self.pushButton_down_arrow.setIconSize(QSize(50,50))
        self.pushButton_down_arrow.setText('')
        self.verticalLayout_up_down.addWidget(self.pushButton_down_arrow)
        spacerItem = QSpacerItem(20,178,QSizePolicy.Minimum,QSizePolicy.Expanding)
        self.verticalLayout_up_down.addItem(spacerItem)
        self.gridLayout.addLayout(self.verticalLayout_up_down, 0, 5, 1, 1)

        self.listView_NotSelected.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.listView_Selected.setSelectionMode(QAbstractItemView.ExtendedSelection)

        self.listView_NotSelected.setModel(self.model.model_NotSelected)
        self.listView_Selected.setModel(self.model.model_Selected)



    #----------------------------------------------------------------------
    def on_right_arrow_press(self):
        """"""

        NSMod = self.listView_NotSelected.model()
        NSSelMod = self.listView_NotSelected.selectionModel()

        SMod = self.listView_Selected.model()
        SSelMod = self.listView_Selected.selectionModel()

        mod_ind_list = NSSelMod.selectedRows(0)
        if mod_ind_list == []:
            return
        else:
            SSelMod.clearSelection()
        while mod_ind_list != []:
            mod_ind = mod_ind_list[0]

            item = NSMod.itemFromIndex(mod_ind)
            new_item = item.clone()
            SMod.appendRow(new_item)
            SSelMod.select(SMod.indexFromItem(new_item),
                           QItemSelectionModel.Select)
            NSMod.removeRow(mod_ind.row())

            mod_ind_list = NSSelMod.selectedRows(0)

    #----------------------------------------------------------------------
    def on_left_arrow_press(self):
        """"""

        SMod = self.listView_Selected.model()
        SSelMod = self.listView_Selected.selectionModel()

        NSMod = self.listView_NotSelected.model()
        NSSelMod = self.listView_NotSelected.selectionModel()

        mod_ind_list = SSelMod.selectedRows(0)
        if mod_ind_list == []:
            return
        else:
            NSSelMod.clearSelection()
        while mod_ind_list != []:
            mod_ind = mod_ind_list[0]

            item = SMod.itemFromIndex(mod_ind)
            text = item.text()
            if text in self.model.permanently_selected_string_list:
                print '"' + text + '"' + ' cannot be unselected.'
                return
            else:
                new_item = item.clone()
                NSMod.appendRow(new_item)
                NSSelMod.select(NSMod.indexFromItem(new_item),
                                QItemSelectionModel.Select)
                SMod.removeRow(mod_ind.row())

            mod_ind_list = SSelMod.selectedRows(0)


    #----------------------------------------------------------------------
    def on_up_arrow_press(self):
        """"""

        SMod = self.listView_Selected.model()
        SSelMod = self.listView_Selected.selectionModel()

        mod_ind_list = SSelMod.selectedRows(0)
        if mod_ind_list == []:
            return
        else:
            sorted_row_ind_list = sorted([mod_ind.row() for mod_ind in mod_ind_list])

        for row_ind in sorted_row_ind_list:
            try:
                upper_item = SMod.item(row_ind-1).clone()
                lower_item = SMod.item(row_ind).clone()
                SMod.removeRow(row_ind-1)
                SMod.insertRow(row_ind-1,lower_item)
                SMod.removeRow(row_ind)
                SMod.insertRow(row_ind,upper_item)
                SSelMod.select(SMod.indexFromItem(lower_item),
                               QItemSelectionModel.Select)
            except:
                break

    #----------------------------------------------------------------------
    def on_down_arrow_press(self):
        """"""

        SMod = self.listView_Selected.model()
        SSelMod = self.listView_Selected.selectionModel()

        mod_ind_list = SSelMod.selectedRows(0)
        if mod_ind_list == []:
            return
        else:
            sorted_row_ind_list = sorted([mod_ind.row() for mod_ind in mod_ind_list],
                                         reverse=True)

        for row_ind in sorted_row_ind_list:
            try:
                upper_item = SMod.item(row_ind).clone()
                lower_item = SMod.item(row_ind+1).clone()
                SMod.removeRow(row_ind)
                SMod.insertRow(row_ind,lower_item)
                SMod.removeRow(row_ind+1)
                SMod.insertRow(row_ind+1,upper_item)
                SSelMod.select(SMod.indexFromItem(upper_item),
                               QItemSelectionModel.Select)
            except:
                break

########################################################################
class ColumnsDialog(QDialog):
    """"""

    #----------------------------------------------------------------------
    def __init__(self, full_column_name_list, init_selected_colum_name_list,
                 permanently_selected_column_name_list, parentWindow = None):
        """Constructor"""

        QDialog.__init__(self, parent=parentWindow)

        self.setWindowFlags(QtCore.Qt.Window) # To add Maximize & Minimize buttons

        self.setWindowTitle('Column Visibility/Order')

        self.verticalLayout = QVBoxLayout(self)

        widget = QWidget(self)
        self.visible_column_order_selector = OrderSelector(
            parentWidget=widget,
            full_string_list=full_column_name_list,
            init_selected_string_list=init_selected_colum_name_list,
            permanently_selected_string_list=permanently_selected_column_name_list,
            label_text_NotSelected='NOT Visible Column Names:',
            label_text_Selected='Visible Column Names:')
        self.verticalLayout.addWidget(widget)

        self.buttonBox = QDialogButtonBox(self)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)
        self.verticalLayout.addWidget(self.buttonBox)

        self.output = None

        self.connect(self.buttonBox, SIGNAL('accepted()'), self.accept)
        self.connect(self.buttonBox, SIGNAL('rejected()'), self.reject)

    #----------------------------------------------------------------------
    def closeEvent(self, event):
        """"""

        self.output = None

        event.accept()

    #----------------------------------------------------------------------
    def accept(self):
        """"""

        selected_listView = self.visible_column_order_selector.view.listView_Selected
        SMod = selected_listView.model()
        self.output = [SMod.item(row_ind,0).text() for row_ind in range(SMod.rowCount())]

        super(ColumnsDialog, self).accept()

    #----------------------------------------------------------------------
    def reject(self):
        """"""

        self.output = None

        super(ColumnsDialog, self).reject()
