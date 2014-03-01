from PyQt4.QtCore import (
    Qt, SIGNAL, QSize, QSettings
)
from PyQt4.QtGui import (
    QWidget, QGridLayout, QSplitter, QTreeView, QTableView,
    QVBoxLayout, QHBoxLayout, QPushButton, QSpacerItem, QCheckBox, QLineEdit,
    QSizePolicy, QComboBox, QLabel, QTextEdit, QStackedWidget, QMessageBox
)

import config
from aphla.gui.utils.orderselector import ColumnsDialog

########################################################################
class ConfigDBViewWidget(QWidget):
    """"""

    #----------------------------------------------------------------------
    def __init__(self, parentLayoutWidget, parentGridLayout):
        """Constructor"""

        QWidget.__init__(self, parentLayoutWidget)

        self._initUI(parentGridLayout)

        self.comboBox_view.setEditable(False)
        self.group_based_view_index = \
            self.comboBox_view.findText('Group-based View')
        self.channel_based_view_index = \
            self.comboBox_view.findText('Channel-based View')
        self.comboBox_view.setCurrentIndex(self.channel_based_view_index)
        self.on_view_base_change(self.channel_based_view_index)

        (self.all_col_keys, self.all_col_names) = map(list,
            config.COL_DEF.getColumnDataFromTable(
                'column_table', column_name_list=['column_key',
                                                  'short_descrip_name'],
                condition_str='only_for_snapshot=0')
            )
        self.vis_col_name_list = self.all_col_names[:]

        self.connect(self.comboBox_view, SIGNAL('currentIndexChanged(int)'),
                     self.on_view_base_change)
        self.connect(self.checkBox_sortable, SIGNAL('stateChanged(int)'),
                     self.on_sortable_state_changed)
        self.connect(self.pushButton_columns, SIGNAL('clicked()'),
                     self.launchColumnsDialog)

    #----------------------------------------------------------------------
    def _initUI(self, parentGridLayout):
        """"""

        self.gridLayout_5 = QGridLayout(self)
        self.gridLayout_5.setMargin(0)
        self.verticalLayout_2 = QVBoxLayout()
        self.stackedWidget = QStackedWidget(self)
        self.page_tree = QWidget()
        self.gridLayout_2 = QGridLayout(self.page_tree)
        self.treeView = QTreeView(self.page_tree)
        self.gridLayout_2.addWidget(self.treeView, 0, 0, 1, 1)
        self.stackedWidget.addWidget(self.page_tree)
        self.page_table = QWidget()
        self.gridLayout = QGridLayout(self.page_table)
        self.tableView = QTableView(self.page_table)
        self.gridLayout.addWidget(self.tableView, 0, 0, 1, 1)
        self.stackedWidget.addWidget(self.page_table)
        self.verticalLayout_2.addWidget(self.stackedWidget)
        self.horizontalLayout = QHBoxLayout()
        spacerItem = QSpacerItem(40, 20,
                                 QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.comboBox_view = QComboBox(self)
        self.comboBox_view.addItem('Group-based View')
        self.comboBox_view.addItem('Channel-based View')
        self.horizontalLayout.addWidget(self.comboBox_view)
        self.pushButton_columns = QPushButton(self)
        self.pushButton_columns.setText('Columns')
        self.horizontalLayout.addWidget(self.pushButton_columns)
        self.checkBox_sortable = QCheckBox(self)
        self.checkBox_sortable.setText('Sortable')
        self.checkBox_sortable.setChecked(False)
        self.horizontalLayout.addWidget(self.checkBox_sortable)
        self.verticalLayout_2.addLayout(self.horizontalLayout)
        self.gridLayout_5.addLayout(self.verticalLayout_2, 0, 0, 1, 1)

        parentGridLayout.addWidget(self, 0, 0, 2, 1)

    #----------------------------------------------------------------------
    def on_view_base_change(self, current_comboBox_index):
        """"""

        if current_comboBox_index == self.group_based_view_index:
            page_obj = self.page_tree
        elif current_comboBox_index == self.channel_based_view_index:
            page_obj = self.page_table
        else:
            raise ValueError('Unexpected current ComboBox index: {0:d}'.
                             format(current_comboBox_index))

        self.stackedWidget.setCurrentWidget(page_obj)

    #----------------------------------------------------------------------
    def on_sortable_state_changed(self, state):
        """"""

        if state == Qt.Checked:
            checked = True
        else:
            checked = False

        self.tableView.setSortingEnabled(checked)

    #----------------------------------------------------------------------
    def on_column_selection_change(self, new_vis_col_names,
                                   force_visibility_update=False):
        """"""

        if (not force_visibility_update) and \
           (new_vis_col_names == self.vis_col_name_list):
            return

        new_vis_col_logical_indexes = [
            self.all_col_names.index(name)
            for name in new_vis_col_names]

        header = self.tableView.horizontalHeader()
        #header = self.treeView.header()

        for (i, col_logical_ind) in enumerate(new_vis_col_logical_indexes):
            new_visual_ind = i
            current_visual_ind = header.visualIndex(col_logical_ind)
            header.moveSection(current_visual_ind, new_visual_ind)

        for i in range(len(self.all_col_names)):
            if i not in new_vis_col_logical_indexes:
                header.hideSection(i)
            else:
                header.showSection(i)

        self.vis_col_name_list = new_vis_col_names[:]

    #----------------------------------------------------------------------
    def launchColumnsDialog(self):
        """"""

        all_column_name_list = self.all_col_names[:]
        visible_column_name_list = self.vis_col_name_list[:]
        permanently_visible_column_name_list = \
            [self.all_col_names[self.all_col_keys.index('group_name')]]

        dialog = ColumnsDialog(all_column_name_list,
                               visible_column_name_list,
                               permanently_visible_column_name_list,
                               parentWindow=self)
        dialog.exec_()

        if dialog.output is not None:
            self.on_column_selection_change(dialog.output[:],
                                            force_visibility_update=False)
