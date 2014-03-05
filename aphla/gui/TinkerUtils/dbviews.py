import numpy as np

from PyQt4.QtCore import (
    Qt, SIGNAL, QSize, QSettings
)
from PyQt4.QtGui import (
    QWidget, QGridLayout, QSplitter, QTreeView, QTableView,
    QVBoxLayout, QHBoxLayout, QPushButton, QSpacerItem, QCheckBox, QLineEdit,
    QSizePolicy, QComboBox, QLabel, QTextEdit, QStackedWidget, QMessageBox,
    QMenu, QItemSelectionModel, QInputDialog, QAction, QIcon, QAbstractItemView,
)

import config
from aphla.gui.utils.orderselector import ColumnsDialog

########################################################################
class CustomTableView(QTableView):
    """"""

    #----------------------------------------------------------------------
    def __init__(self, *args):
        """Constructor"""

        QTableView.__init__(self, *args)

    #----------------------------------------------------------------------
    def closeEditor(self, editor, hint):
        """
        overwriting QAbstractItemView virtual protected slot
        """

        super(QTableView, self).closeEditor(editor, hint)

    #----------------------------------------------------------------------
    def edit(self, modelIndex, trigger, event):
        """"""

        return super(QTableView, self).edit(modelIndex, trigger, event)


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

        (column_ids, self.all_col_keys, self.all_col_names, user_editable,
         self.str_format) = \
            map(list,
                config.COL_DEF.getColumnDataFromTable(
                    'column_table',
                    column_name_list=['column_id', 'column_key',
                                      'short_descrip_name',
                                      'user_editable_in_conf_setup',
                                      'str_format'],
                    condition_str='only_for_snapshot=0')
                )
        self.vis_col_name_list = self.all_col_names[:]

        self.user_editable_col_ids = [c-1 for c, u in
                                      zip(column_ids, user_editable)
                                      if u == 1]

        self.tableView.setContextMenuPolicy(Qt.CustomContextMenu)

        self.contextMenu = QMenu()

        self.connect(self.comboBox_view, SIGNAL('currentIndexChanged(int)'),
                     self.on_view_base_change)
        self.connect(self.checkBox_sortable, SIGNAL('stateChanged(int)'),
                     self.on_sortable_state_changed)
        self.connect(self.pushButton_columns, SIGNAL('clicked()'),
                     self.launchColumnsDialog)

        self.actionModifyTableValues = QAction(QIcon(), 'Modify values...',
                                               self.tableView)
        self.addAction(self.actionModifyTableValues)
        self.connect(self.actionModifyTableValues, SIGNAL('triggered()'),
                     self.modify_values)

        self.connect(self.tableView,
                     SIGNAL('customContextMenuRequested(const QPoint &)'),
                     self.openContextMenu)

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
        self.tableView = CustomTableView(self.page_table)
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
    def openContextMenu(self, qpoint):
        """"""

        self.updateMenuItems()

        if self.contextMenu.actions() != []:
            sender = self.sender()

            globalClickPos = sender.mapToGlobal(qpoint)

            self.contextMenu.exec_(globalClickPos)

    #----------------------------------------------------------------------
    def updateMenuItems(self):
        """"""

        sender = self.sender()

        if sender == self.tableView:

            sm = self.tableView.selectionModel()
            proxy_index_list = sm.selectedIndexes()

            self.contextMenu.clear()

            cols = [i.column() for i in proxy_index_list]
            if len(set(cols)) != 1:
                return
            else:
                proxy_ind = proxy_index_list[0]
                proxy_model = self.tableView.model()
                source_model = proxy_model.sourceModel()
                source_ind = proxy_model.mapToSource(proxy_ind)
                source_col_ind = source_ind.column()

            if source_col_ind not in self.user_editable_col_ids:
                return

            if (self.all_col_keys[source_col_ind] == 'step_size') and \
               ((source_model.abstract.ref_step_size == 0.0) or
                np.isnan(source_model.abstract.ref_step_size)):
                msg = QMessageBox()
                msg.setText(('To change step size values directly, you must '
                             'have non-zero or non-nan reference step size.'))
                msg.exec_()
                return

            self.contextMenu.addAction(self.actionModifyTableValues)

        else:
            raise NotImplementedError('')

    #----------------------------------------------------------------------
    def modify_values(self):
        """"""

        sender = self.sender()

        if sender.parent() == self.tableView:

            sm = self.tableView.selectionModel()
            proxy_index_list = sm.selectedIndexes()
            proxy_model = self.tableView.model()
            source_model = proxy_model.sourceModel()

            source_index_list = [proxy_model.mapToSource(pi)
                                 for pi in proxy_index_list]
            source_cols = [i.column() for i in source_index_list]
            if len(set(source_cols)) != 1:
                return
            else:
                col_ind = source_cols[0]

            if col_ind in self.user_editable_col_ids:
                current_vals = [source_model.data(i) for i in source_index_list]

                if len(set(current_vals)) == 1:
                    current_val = current_vals[0]
                else:
                    current_val = None

                str_format = self.str_format[
                    self.user_editable_col_ids.index(col_ind)]
                if str_format is None:
                    data_type = 'string'
                elif str_format.endswith(('g', 'e')):
                    data_type = 'float'
                    if current_val is not None:
                        current_val = float(current_val)
                else:
                    raise ValueError('Unexpected str_format: {0:s}'.
                                     format(str_format))

                new_val = self.get_new_value(self.tableView, data_type,
                                             current_val)

                if new_val is not None:
                    row_inds = [i.row() for i in source_index_list]
                    source_model.modifyAbstractModel(new_val, col_ind, row_inds)

        else:
            raise NotImplementedError()

    #----------------------------------------------------------------------
    def get_new_value(self, parent, data_type, current_data):
        """"""

        if data_type == 'string':
            if current_data is None:
                current_data = ''

            prompt_text = ('Enter a new string')
            result = QInputDialog.getText(parent, 'New String', prompt_text,
                                          text=current_data)

            if result[1]: # If OK was pressed
                return str(result[0]).strip(' \t\n\r')
            else: # If Cancel was pressed
                return None

        elif data_type == 'float':
            if current_data is None:
                current_data = 0.0

            prompt_text = ('Enter a new float value:')
            result = QInputDialog.getDouble(
                parent, 'New Float', prompt_text, value=current_data,
                decimals=8)

            if result[1]: # If OK was pressed
                return result[0]
            else: # If Cancel was pressed
                return None
        else:
            raise ValueError('Unexpected current_data type: {0:s}'.format(
                type(current_data)))


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

########################################################################
class SnapshotDBViewWidget(QStackedWidget):
    """"""

    #----------------------------------------------------------------------
    def __init__(self, parentWidget):
        """Constructor"""

        QStackedWidget.__init__(self, parentWidget)

        self.page_tree = QWidget()
        gridLayout = QGridLayout(self.page_tree)
        self.treeView = QTreeView(self.page_tree)
        gridLayout.addWidget(self.treeView, 0, 0, 1, 1)
        self.addWidget(self.page_tree)
        #
        self.page_table = QWidget()
        gridLayout = QGridLayout(self.page_table)
        self.tableView = QTableView(self.page_table)
        gridLayout.addWidget(self.tableView, 0, 0, 1, 1)
        self.addWidget(self.page_table)

