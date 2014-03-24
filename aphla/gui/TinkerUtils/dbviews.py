import numpy as np

from PyQt4.QtCore import (
    Qt, SIGNAL, QSize, QSettings, QPoint, QEvent, QRect
)
from PyQt4.QtGui import (
    QWidget, QGridLayout, QSplitter, QTreeView, QTableView,
    QVBoxLayout, QHBoxLayout, QPushButton, QSpacerItem, QCheckBox, QLineEdit,
    QSizePolicy, QComboBox, QLabel, QTextEdit, QStackedWidget, QMessageBox,
    QMenu, QItemSelectionModel, QInputDialog, QAction, QIcon, QAbstractItemView,
    QStyledItemDelegate, QStyleOptionButton, QStyle
)

import config
from aphla.gui.utils.orderselector import ColumnsDialog
from aphla.gui.TinkerUtils.tinkerdb import TinkerMainDatabase

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
class ConfigMetaDBViewWidget(QWidget):
    """"""

    #----------------------------------------------------------------------
    def __init__(self, parentWidget):
        """Constructor"""

        QWidget.__init__(self, parentWidget)

        self._initUI(parentWidget)

        self.db = TinkerMainDatabase()
        self.db.create_temp_config_meta_table_text_view()
        self.all_col_keys = \
            self.db.getColumnNames('[config_meta_table text view]')
        self.col_keys_wo_desc = self.all_col_keys[:]
        self.col_keys_wo_desc.remove('config_description')

        self.col_names_wo_desc = [
            'Config.ID', 'Config.Name', 'Username', 'MASAR ID', 'Ref.StepSize',
            'Synced.GroupWeight', 'Time Created']

        self.vis_col_name_list = self.col_names_wo_desc[:]

        self.connect(self.checkBox_sortable, SIGNAL('stateChanged(int)'),
                     self.on_sortable_state_changed)
        self.connect(self.pushButton_columns, SIGNAL('clicked()'),
                     self.launchColumnsDialog)
        self.connect(self.pushButton_export, SIGNAL('clicked()'),
                     self.exportConfigToFile)
        self.connect(self.pushButton_edit_config_name_desc, SIGNAL('clicked()'),
                     self.editConfigNameOrDescription)

    #----------------------------------------------------------------------
    def _initUI(self, parentWidget):
        """"""

        verticalLayout_2 = QVBoxLayout(parentWidget)
        verticalLayout_2.setContentsMargins(0, 0, 0, 0) # zero margin

        self.splitter = QSplitter(parentWidget)
        self.splitter.setContentsMargins(0, 0, 0, 0) # zero margin
        self.splitter.setOrientation(Qt.Vertical)
        self.splitter.setHandleWidth(9)

        verticalLayout_2.addWidget(self.splitter)

        self.layoutWidget_2 = QWidget(self.splitter)
        verticalLayout = QVBoxLayout(self.layoutWidget_2)
        verticalLayout.setContentsMargins(-1, 0, -1, 0)
        self.tableView = QTableView(self)
        verticalLayout.addWidget(self.tableView)

        self.layoutWidget_3 = QWidget(self.layoutWidget_2)
        verticalLayout.addWidget(self.layoutWidget_3)
        horizontalLayout = QHBoxLayout(self.layoutWidget_3)
        horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.pushButton_export = QPushButton(self)
        self.pushButton_export.setText('Export...')
        self.pushButton_export.setMaximumWidth(200)
        horizontalLayout.addWidget(self.pushButton_export)
        spacerItem = QSpacerItem(20, 40, QSizePolicy.Expanding,
                                 QSizePolicy.Minimum)
        horizontalLayout.addItem(spacerItem)
        self.pushButton_columns = QPushButton(self)
        self.pushButton_columns.setText('Columns')
        self.pushButton_columns.setMaximumWidth(200)
        horizontalLayout.addWidget(self.pushButton_columns)
        self.checkBox_sortable = QCheckBox(self)
        self.checkBox_sortable.setText('Sortable')
        self.checkBox_sortable.setChecked(False)
        horizontalLayout.addWidget(self.checkBox_sortable)

        self.layoutWidget = QWidget(self.splitter)
        gridLayout = QGridLayout(self.layoutWidget)
        self.label_2 = QLabel(self)
        self.label_2.setText('Description')
        gridLayout.addWidget(self.label_2, 0, 0, 1, 1)
        spacerItem2 = QSpacerItem(20, 40, QSizePolicy.Minimum,
                                  QSizePolicy.Expanding)
        gridLayout.addItem(spacerItem2, 1, 0, 1, 1)
        self.pushButton_edit_config_name_desc = QPushButton(self)
        self.pushButton_edit_config_name_desc.setText('Edit...')
        gridLayout.addWidget(self.pushButton_edit_config_name_desc,
                             2, 0, 1, 1)
        self.textEdit_description = QTextEdit(self)
        self.textEdit_description.setReadOnly(True)
        gridLayout.addWidget(self.textEdit_description, 0, 1, 3, 1)

        tbV = self.tableView
        tbV.setSelectionMode(QAbstractItemView.SingleSelection)
        tbV.setSelectionBehavior(QAbstractItemView.SelectRows)
        tbV.setCornerButtonEnabled(True)
        tbV.setShowGrid(True)
        tbV.setAlternatingRowColors(True)
        tbV.setSortingEnabled(False)
        horizHeader = tbV.horizontalHeader()
        horizHeader.setSortIndicatorShown(False)
        horizHeader.setStretchLastSection(False)
        horizHeader.setMovable(False)

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
            self.col_names_wo_desc.index(name)
            for name in new_vis_col_names]

        header = self.tableView.horizontalHeader()
        #header = self.treeView.header()

        for (i, col_logical_ind) in enumerate(new_vis_col_logical_indexes):
            new_visual_ind = i
            current_visual_ind = header.visualIndex(col_logical_ind)
            header.moveSection(current_visual_ind, new_visual_ind)

        for i in range(len(self.col_names_wo_desc)):
            if i not in new_vis_col_logical_indexes:
                header.hideSection(i)
            else:
                header.showSection(i)

        self.vis_col_name_list = new_vis_col_names[:]

    #----------------------------------------------------------------------
    def launchColumnsDialog(self):
        """"""

        all_column_name_list = self.col_names_wo_desc[:]
        visible_column_name_list = self.vis_col_name_list[:]
        permanently_visible_column_name_list = []

        dialog = ColumnsDialog(all_column_name_list,
                               visible_column_name_list,
                               permanently_visible_column_name_list,
                               parentWindow=self)
        dialog.exec_()

        if dialog.output is not None:
            self.on_column_selection_change(dialog.output[:],
                                            force_visibility_update=False)

    #----------------------------------------------------------------------
    def exportConfigToFile(self):
        """"""

        self.emit(SIGNAL('exportConfigToFile'))

    #----------------------------------------------------------------------
    def editConfigNameOrDescription(self):
        """"""

        self.emit(SIGNAL('editConfigNameOrDescription'))

########################################################################
class ConfigDBViewWidget(QWidget):
    """"""

    #----------------------------------------------------------------------
    def __init__(self, parentWidget, parentGridLayout=None):
        """Constructor"""

        QWidget.__init__(self, parentWidget)

        if parentGridLayout is None:
            parentGridLayout = QGridLayout(parentWidget)
            parentGridLayout.addWidget(self)
        parentGridLayout.setContentsMargins(0, 0, 0, -1)
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
                    condition_str='only_for_ss=0')
                )
        self.vis_col_name_list = self.all_col_names[:]

        self.user_editable_col_ids = [c-1 for c, u in
                                      zip(column_ids, user_editable)
                                      if u == 1]

        t = self.tableView
        t.setCornerButtonEnabled(True)
        t.setShowGrid(True)
        t.setContextMenuPolicy(Qt.CustomContextMenu)
        t.setAlternatingRowColors(True)
        t.setSortingEnabled(False)
        horizHeader = t.horizontalHeader()
        horizHeader.setSortIndicatorShown(False)
        horizHeader.setStretchLastSection(False)
        horizHeader.setMovable(False)

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
                str_format = self.str_format[col_ind]

                if str_format != 'checkbox':
                    current_vals = [source_model.data(i, Qt.DisplayRole)
                                    for i in source_index_list]
                else:
                    current_vals = [source_model.data(i, Qt.UserRole)
                                    for i in source_index_list]

                if len(set(current_vals)) == 1:
                    current_val = current_vals[0]
                else:
                    current_val = None

                if str_format is None:
                    data_type = 'string'
                elif str_format.endswith(('g', 'e')):
                    data_type = 'float'
                    if current_val is not None:
                        current_val = float(current_val)
                elif str_format == 'checkbox':
                    data_type = 'bool'
                else:
                    raise ValueError('Unexpected str_format: {0:s}'.
                                     format(str_format))

                col_key = source_model.abstract.all_col_keys[col_ind]
                row_inds = [i.row() for i in source_index_list]

                msg = QMessageBox()
                msg.setIcon(QMessageBox.Critical)

                if col_key in ['channel_name', 'pvsp', 'pvrb']:
                    for row in row_inds:
                        if (source_model.d['elem_name'][row] is not None):
                            msg.setText(
                                'This property cannot be changed as it is defined by '
                                'the linked aphla element object.')
                            msg.exec_()
                            return

                if col_key == 'pvsp':
                    if len(row_inds) != 1:
                        msg.setText('It is not allowed to set multiple '
                                    'setpoint PVs to the same value.')
                        msg.exec_()
                        return

                new_val = self.get_new_value(self.tableView, data_type,
                                             current_val)

                if col_key == 'group_name':
                    if new_val == '':
                        msg.setText('Group name cannot be empty.')
                        msg.exec_()
                        return

                if new_val is not None:
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

        elif data_type == 'bool':

            prompt_text = ('Select a new bool value:')
            result = QInputDialog.getItem(
                parent, 'New Bool', prompt_text, ['True', 'False'],
                editable=False)

            if result[1]: # If OK was pressed
                if result[0] == 'True':
                    return True
                else:
                    return False
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
class SnapshotDBViewWidget(QWidget):
    """"""

    #----------------------------------------------------------------------
    def __init__(self, parentWidget):
        """Constructor"""

        QWidget.__init__(self, parentWidget)

        self._initUI()

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
                                      'user_editable_in_ss',
                                      'str_format'])
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

    #----------------------------------------------------------------------
    def _initUI(self):
        """"""

        self.stackedWidget = QStackedWidget(self)
        self.stackedWidget.setContentsMargins(0, 0, 0, 0)

        self.page_tree = QWidget()
        self.page_tree.setContentsMargins(0, 0, 0, 0)
        vLayout = QVBoxLayout(self.page_tree)
        vLayout.setContentsMargins(0, 0, 0, 0)
        self.treeView = QTreeView(self.page_tree)
        self.treeView.setContentsMargins(0, 0, 0, 0)
        vLayout.addWidget(self.treeView)
        self.stackedWidget.addWidget(self.page_tree)
        #
        self.page_table = QWidget()
        self.page_table.setContentsMargins(0, 0, 0, 0)
        vLayout = QVBoxLayout(self.page_table)
        vLayout.setContentsMargins(0, 0, 0, 0)
        self.tableView = QTableView(self.page_table)
        self.tableView.setContentsMargins(0, 0, 0, 0)
        vLayout.addWidget(self.tableView)
        self.stackedWidget.addWidget(self.page_table)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        spacerItem = QSpacerItem(40, 20,
                                 QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)

        self.comboBox_view = QComboBox(self)
        self.comboBox_view.addItem('Group-based View')
        self.comboBox_view.addItem('Channel-based View')
        self.comboBox_view.setCurrentIndex(1)
        self.horizontalLayout.addWidget(self.comboBox_view)

        self.pushButton_columns = QPushButton(self)
        self.pushButton_columns.setText('Columns')
        self.horizontalLayout.addWidget(self.pushButton_columns)

        self.checkBox_sortable = QCheckBox(self)
        self.checkBox_sortable.setText('Sortable')
        self.checkBox_sortable.setChecked(False)
        self.horizontalLayout.addWidget(self.checkBox_sortable)

        self.verticalLayout = QVBoxLayout(self)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.addWidget(self.stackedWidget)
        self.verticalLayout.addLayout(self.horizontalLayout)

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

        self.emit(SIGNAL('ssDBViewVisibleColumnsChagned'),
                  self.vis_col_name_list)

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
class ConfigDBTableViewItemDelegate(QStyledItemDelegate):
    """"""

    #----------------------------------------------------------------------
    def __init__(self, view, config_table_model, parent=None):
        """Constructor"""

        QStyledItemDelegate.__init__(self, parent)

        self.view = view

        self.config_table    = config_table_model
        self.config_abstract = self.config_table.abstract

    #----------------------------------------------------------------------
    def getCheckBoxRect(self, option):
        """"""

        opt = QStyleOptionButton()
        style = self.view.style()
        checkbox_rect = style.subElementRect(QStyle.SE_CheckBoxIndicator, opt)

        checkbox_point = QPoint( option.rect.x() +
                                 option.rect.width() / 2 -
                                 checkbox_rect.width() / 2,
                                 option.rect.y() +
                                 option.rect.height() / 2 -
                                 checkbox_rect.height() / 2 )

        return QRect(checkbox_point, checkbox_rect.size())

    #----------------------------------------------------------------------
    def paint(self, painter, option, index):
        """"""

        QStyledItemDelegate.paint(self, painter, option, index) # Need to
        # call the standard paint() in order to keep the color change when
        # selected.

        row = index.row()
        col = index.column()

        col_key    = self.config_abstract.all_col_keys[col]
        str_format = self.config_abstract.all_str_formats[col]

        '''
        Somehow after upgrading to Debian 7 or on Ubuntu 12.04, the creation
        of QStylePainter object with

        > stylePainter = QStylePainter(painter.device(), self.view)

        results in Segmentation Fault, right before paintEvent by
        QTableView associated with this delegate is finished.

        Creation of QStylePainter object with

        > stylePainter = QStylePainter(self.view)

        does not result in Seg. Fault., but it does not render the view
        correctly.

        The solution to the problem is to use QStyle.drawControl &
        QStyle.drawComplexControl, instead of the corresponding functions
        of QStylePainter.

        As a result QStylePainter.save() & QStylePainter.restore() have been
        commented out.
        '''
        style = self.view.style()

        if col_key == 'caput_enabled':

            value = index.model().data(index, role=Qt.UserRole)

            checked = value

            opt = QStyleOptionButton()

            if int(index.flags() & Qt.ItemIsEditable) > 0:
                opt.state |= QStyle.State_Enabled
            else:
                opt.state |= QStyle.State_ReadOnly

            if checked:
                opt.state |= QStyle.State_On
            else:
                opt.state |= QStyle.State_Off

            # Centering of Checkbox
            opt.rect = self.getCheckBoxRect(option)

            style.drawControl(QStyle.CE_CheckBox, opt, painter, self.view)

    #----------------------------------------------------------------------
    def setModelData(self, editor, model, index):
        """"""

        col = index.column()
        col_key = self.config_abstract.all_col_keys[col]

        if col_key == 'caput_enabled': # editor = QCheckbox
            old_value = model.data(index, Qt.UserRole)

            # Change the check state to opposite if editable
            if int(index.flags() & Qt.ItemIsEditable) > 0:
                checked = not old_value
                if checked:
                    checked_value = 1
                else:
                    checked_value = 0
                model.setData(index, checked_value, role=Qt.EditRole)
        else:
            QStyledItemDelegate.setModelData(self, editor, model, index)

    #----------------------------------------------------------------------
    def editorEvent(self, event, model, option, index):
        """"""

        col = index.column()
        col_key = self.config_abstract.all_col_keys[col]

        if col_key == 'caput_enabled':

            if not ( int(index.flags() & Qt.ItemIsEditable) > 0 ):
                return False

            # Do not change the checkbox state
            if event.type() == QEvent.MouseButtonRelease or \
               event.type() == QEvent.MouseButtonDblClick:
                if event.button() != Qt.LeftButton or \
                   not self.getCheckBoxRect(option).contains(event.pos()):
                    return False
                if event.type() == QEvent.MouseButtonDblClick:
                    return True
            elif event.type() == QEvent.KeyPress:
                if (event.key() != Qt.Key_Space) and \
                   (event.key() != Qt.Key_Select):
                    return False
            else:
                return False

            # Change the checkbox state
            self.setModelData(None, model, index)
            return True

        else:
            return QStyledItemDelegate.editorEvent(self, event, model, option,
                                                   index)

    #----------------------------------------------------------------------
    def createEditor(self, parent, option, index):
        """"""

        col = index.column()
        col_key = self.config_abstract.all_col_keys[col]

        if col_key == 'caput_enabled':
            # Must be None, otherwise an editor is created if a user clicks
            # this cell
            return None
        else:
            return QStyledItemDelegate.createEditor(self, parent, option, index)

    #----------------------------------------------------------------------
    def setEditorData(self, editor, index):
        """"""

        value = index.model().data(index, Qt.DisplayRole)

        col = index.column()
        col_key = self.config_abstract.all_col_keys[col]

        if col_key == 'caput_enabled':
            checked = value
            editor.setChecked(checked)

            editor.close()
        else:
            QStyledItemDelegate.setEditorData(self, editor, index)

########################################################################
class SnapshotDBTableViewItemDelegate(QStyledItemDelegate):
    """"""

    #----------------------------------------------------------------------
    def __init__(self, view, snapshot_table_model, parent=None):
        """Constructor"""

        QStyledItemDelegate.__init__(self, parent)

        self.view = view

        self.ss_table        = snapshot_table_model
        self.ss_abstract     = self.ss_table.abstract

    #----------------------------------------------------------------------
    def getCheckBoxRect(self, option):
        """"""

        opt = QStyleOptionButton()
        style = self.view.style()
        checkbox_rect = style.subElementRect(QStyle.SE_CheckBoxIndicator, opt)

        checkbox_point = QPoint( option.rect.x() +
                                 option.rect.width() / 2 -
                                 checkbox_rect.width() / 2,
                                 option.rect.y() +
                                 option.rect.height() / 2 -
                                 checkbox_rect.height() / 2 )

        return QRect(checkbox_point, checkbox_rect.size())

    #----------------------------------------------------------------------
    def paint(self, painter, option, index):
        """"""

        QStyledItemDelegate.paint(self, painter, option, index) # Need to
        # call the standard paint() in order to keep the color change when
        # selected.

        row = index.row()
        col = index.column()

        col_key    = self.ss_abstract.all_col_keys[col]
        str_format = self.ss_abstract.all_str_formats[col]

        '''
        Somehow after upgrading to Debian 7 or on Ubuntu 12.04, the creation
        of QStylePainter object with

        > stylePainter = QStylePainter(painter.device(), self.view)

        results in Segmentation Fault, right before paintEvent by
        QTableView associated with this delegate is finished.

        Creation of QStylePainter object with

        > stylePainter = QStylePainter(self.view)

        does not result in Seg. Fault., but it does not render the view
        correctly.

        The solution to the problem is to use QStyle.drawControl &
        QStyle.drawComplexControl, instead of the corresponding functions
        of QStylePainter.

        As a result QStylePainter.save() & QStylePainter.restore() have been
        commented out.
        '''
        style = self.view.style()

        if col_key == 'caput_enabled':

            value = index.model().data(index, role=Qt.UserRole)

            checked = value

            opt = QStyleOptionButton()

            if int(index.flags() & Qt.ItemIsEditable) > 0:
                opt.state |= QStyle.State_Enabled
            else:
                opt.state |= QStyle.State_ReadOnly

            if checked:
                opt.state |= QStyle.State_On
            else:
                opt.state |= QStyle.State_Off

            # Centering of Checkbox
            opt.rect = self.getCheckBoxRect(option)

            style.drawControl(QStyle.CE_CheckBox, opt, painter, self.view)

    #----------------------------------------------------------------------
    def setModelData(self, editor, model, index):
        """"""

        col = index.column()
        col_key = self.ss_abstract.all_col_keys[col]

        if col_key == 'caput_enabled': # editor = QCheckbox
            old_value = model.data(index, Qt.UserRole)

            # Change the check state to opposite if editable
            if int(index.flags() & Qt.ItemIsEditable) > 0:
                checked = not old_value
                if checked:
                    checked_value = 1
                else:
                    checked_value = 0
                model.setData(index, checked_value, role=Qt.EditRole)
        else:
            QStyledItemDelegate.setModelData(self, editor, model, index)

    #----------------------------------------------------------------------
    def editorEvent(self, event, model, option, index):
        """"""

        col = index.column()
        col_key = self.ss_abstract.all_col_keys[col]

        if col_key == 'caput_enabled':

            if not ( int(index.flags() & Qt.ItemIsEditable) > 0 ):
                return False

            # Do not change the checkbox state
            if event.type() == QEvent.MouseButtonRelease or \
               event.type() == QEvent.MouseButtonDblClick:
                if event.button() != Qt.LeftButton or \
                   not self.getCheckBoxRect(option).contains(event.pos()):
                    return False
                if event.type() == QEvent.MouseButtonDblClick:
                    return True
            elif event.type() == QEvent.KeyPress:
                if (event.key() != Qt.Key_Space) and \
                   (event.key() != Qt.Key_Select):
                    return False
            else:
                return False

            # Change the checkbox state
            self.setModelData(None, model, index)
            return True

        else:
            return QStyledItemDelegate.editorEvent(self, event, model, option,
                                                   index)

    #----------------------------------------------------------------------
    def createEditor(self, parent, option, index):
        """"""

        col = index.column()
        col_key = self.ss_abstract.all_col_keys[col]

        if col_key == 'caput_enabled':
            # Must be None, otherwise an editor is created if a user clicks
            # this cell
            return None
        else:
            return QStyledItemDelegate.createEditor(self, parent, option, index)

    #----------------------------------------------------------------------
    def setEditorData(self, editor, index):
        """"""

        value = index.model().data(index, Qt.DisplayRole)

        col = index.column()
        col_key = self.ss_abstract.all_col_keys[col]

        if col_key == 'caput_enabled':
            checked = value
            editor.setChecked(checked)

            editor.close()
        else:
            QStyledItemDelegate.setEditorData(self, editor, index)
