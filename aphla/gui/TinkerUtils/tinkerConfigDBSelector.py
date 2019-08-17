from __future__ import print_function, division, absolute_import

import sip
sip.setapi('QString', 2)
sip.setapi('QVariant', 2)

import os, sys
import os.path as osp
import numpy as np
import json
import time

from PyQt4.QtCore import (
    Qt, QObject, SIGNAL, QSettings, QRect, QDateTime, QMetaObject
)
from PyQt4.QtGui import (
    QSortFilterProxyModel, QMessageBox, QIcon, QDialog, QIntValidator,
    QItemSelectionModel, QInputDialog, QSplitter
)

import cothread

import config
try:
    from . import (datestr)
except:
    from aphla.gui.TinkerUtils import (datestr)
from tinkerModels import (MetaTableModel, ConfigAbstractModel,
                          ConfigTableModel, getusername)
from dbviews import (ConfigDBViewWidget, ConfigMetaDBViewWidget,
                     ConfigDBTableViewItemDelegate)
from tinkerdb import TinkerMainDatabase
from ui_tinkerConfigDBSelector import Ui_Dialog
from ui_configDescriptionEditor import Ui_Dialog as Ui_Dialog_confDescEdit

HOME_PATH             = osp.expanduser('~')
APHLA_USER_CONFIG_DIR = osp.join(HOME_PATH, '.aphla')
if not osp.exists(APHLA_USER_CONFIG_DIR):
    os.makedirs(APHLA_USER_CONFIG_DIR)

PREF_CONFIG_META_JSON_FILEPATH = osp.join(
    APHLA_USER_CONFIG_DIR, 'aptinker_ConfigDBSelector_ConfigMeta_pref.json')
PREF_CONFIG_JSON_FILEPATH = osp.join(
    APHLA_USER_CONFIG_DIR, 'aptinker_ConfigDBSelector_Config_pref.json')

########################################################################
class ConfigDescriptionEditor(QDialog, Ui_Dialog_confDescEdit):
    """"""

    #----------------------------------------------------------------------
    def __init__(self, current_description, parent=None):
        """Constructor"""

        QDialog.__init__(self, parent=parent)

        self.setupUi(self)

        self.setWindowFlags(Qt.Window) # To add Maximize & Minimize buttons
        self.setWindowTitle('Append new description')

        self.plainTextEdit_current.setProperty('plainText',
                                               current_description)
        self.plainTextEdit_current.setReadOnly(True)

        self.plainTextEdit_new.setReadOnly(False)

    #----------------------------------------------------------------------
    def closeEvent(self, event):
        """"""

        event.accept()

    #----------------------------------------------------------------------
    def accept(self):
        """"""

        super(ConfigDescriptionEditor, self).accept() # will close the dialog

    #----------------------------------------------------------------------
    def reject(self):
        """"""

        super(ConfigDescriptionEditor, self).reject() # will close the dialog

########################################################################
class ConfigDBSelector(QDialog, Ui_Dialog):
    """"""

    #----------------------------------------------------------------------
    def __init__(self, parent=None, aptinkerQSettings=None):
        """Constructor"""

        QDialog.__init__(self, parent=parent)

        self.setupUi(self)

        self.setWindowFlags(Qt.Window) # To add Maximize & Minimize buttons
        self.setWindowTitle('Select Configuration from Database')

        # Load Startup Preferences for Config Table
        self.default_config_pref = dict(
            vis_col_key_list=config.DEF_VIS_COL_KEYS['config_setup'][:])
        if osp.exists(PREF_CONFIG_JSON_FILEPATH):
            with open(PREF_CONFIG_JSON_FILEPATH, 'r') as f:
                self.config_pref = json.load(f)
        else:
            self.config_pref = self.default_config_pref

        # Load Startup Preferences for Config Meta Table
        self.default_config_meta_pref = dict(
            vis_col_key_list=['config_id', 'config_ctime', 'config_name',
                              'username', 'config_ref_step_size',
                              'config_masar_id'])
        if osp.exists(PREF_CONFIG_META_JSON_FILEPATH):
            with open(PREF_CONFIG_META_JSON_FILEPATH, 'r') as f:
                self.config_meta_pref = json.load(f)
        else:
            self.config_meta_pref = self.default_config_meta_pref

        self.configDBViewWidget = ConfigDBViewWidget(
            self.groupBox_selected_conf)
        self.tableView_config = self.configDBViewWidget.tableView

        self.configMetaDBViewWidget = ConfigMetaDBViewWidget(
            self.groupBox_search_result)
        self.tableView_config_meta = self.configMetaDBViewWidget.tableView
        self.textEdit_description = \
            self.configMetaDBViewWidget.textEdit_description

        self.settings = QSettings('APHLA', 'TinkerConfigDBSelector')
        self.loadViewSettings()

        self._aptinkerQSettings = aptinkerQSettings

        self.pushButton_search.setIcon(QIcon(':/search.png'))

        all_ctime_operators = [
            self.comboBox_time_created_1.itemText(i)
            for i in range(self.comboBox_time_created_1.count())]
        self.comboBox_time_created_1.setCurrentIndex(
            all_ctime_operators.index(''))
        self.dateTimeEdit_time_created_1.setDateTime(
            QDateTime.currentDateTime())
        self.dateTimeEdit_time_created_2.setDateTime(
            QDateTime.currentDateTime())

        self.search_params = dict(
            config_id_1='', config_id_2='',
            ref_step_size_1='', ref_step_size_2='',
            config_name='', config_desc='', username='',
            ctime_1='', ctime_2='',
            synced_gruop_weight='',
            masar_id_1='', masar_id_2='')

        db_id_validator = QIntValidator()
        db_id_validator.setBottom(1)
        self.lineEdit_config_id_1.setValidator(db_id_validator)
        self.lineEdit_config_id_2.setValidator(db_id_validator)
        self.lineEdit_masar_id_1.setValidator(db_id_validator)
        self.lineEdit_masar_id_2.setValidator(db_id_validator)

        self.prev_valid_ref_step_sizes = dict(
            lineEdit_ref_step_size_1=np.nan, lineEdit_ref_step_size_2=np.nan)

        # Set up Config Table
        self.config_model = ConfigModel()
        self.tableModel_config = self.config_model.table
        proxyModel = QSortFilterProxyModel()
        proxyModel.setSourceModel(self.tableModel_config)
        proxyModel.setDynamicSortFilter(False)
        tbV = self.tableView_config
        tbV.setModel(proxyModel)
        tbV.setItemDelegate(ConfigDBTableViewItemDelegate(
            tbV, self.tableModel_config, tbV.parent()))

        self.db = self.config_model.db
        if '[config_meta_table text view]' not in self.db.getViewNames(
            square_brackets=True):
            self.db.create_temp_config_meta_table_text_view()

        # Set up Config Meta Table
        self.config_meta_all_col_keys = self.configMetaDBViewWidget.all_col_keys
        self.search_result = {k: [] for k in self.config_meta_all_col_keys}

        self.tableModel_config_meta = MetaTableModel(
            self.search_result, self.configMetaDBViewWidget)
        proxyModel = QSortFilterProxyModel()
        proxyModel.setSourceModel(self.tableModel_config_meta)
        proxyModel.setDynamicSortFilter(False)
        tbV = self.tableView_config_meta
        tbV.setModel(proxyModel)
        self.selectionModel = QItemSelectionModel(proxyModel)
        tbV.setSelectionModel(self.selectionModel)

        # Apply Visible Column Preference to Config Table
        (col_keys, col_names) = config.COL_DEF.getColumnDataFromTable(
            'column_table',
            column_name_list=['column_key','short_descrip_name'],
            condition_str='column_key in ({0:s})'.format(
                ','.join(['"{0:s}"'.format(k)
                          for k in self.config_pref['vis_col_key_list']]
                         )
            )
        )
        config_vis_col_name_list = [
            col_names[col_keys.index(k)]
            for k in self.config_pref['vis_col_key_list']]
        self.configDBViewWidget.on_column_selection_change(
            config_vis_col_name_list, force_visibility_update=True)

        # Apply Visible Column Preference to Config Meta Table
        config_meta_vis_col_name_list = [
            self.configMetaDBViewWidget.col_names_wo_desc[
                self.configMetaDBViewWidget.col_keys_wo_desc.index(k)]
            for k in self.config_meta_pref['vis_col_key_list']]
        self.configMetaDBViewWidget.on_column_selection_change(
            config_meta_vis_col_name_list, force_visibility_update=True)

        # Make connection

        self.connect(self.lineEdit_ref_step_size_1, SIGNAL('editingFinished()'),
                     self.validate_ref_step_size)
        self.connect(self.lineEdit_ref_step_size_2, SIGNAL('editingFinished()'),
                     self.validate_ref_step_size)

        self.connect(self.pushButton_search, SIGNAL('clicked()'),
                     self.update_search)

        self.connect(
            self.selectionModel,
            SIGNAL(
                'currentRowChanged(const QModelIndex &, const QModelIndex &)'),
            self.on_selection_change
        )

        self.connect(self.configMetaDBViewWidget, SIGNAL('exportConfigToFile'),
                     self.exportConfigToFile)
        self.connect(self.configMetaDBViewWidget,
                     SIGNAL('editConfigNameOrDescription'),
                     self.editConfigNameOrDescription)

    #----------------------------------------------------------------------
    def exportConfigToFile(self):
        """"""

        msg = QMessageBox()

        inds = self.selectionModel.selectedRows()

        if inds != []:
            row = inds[0].row()
            config_id = self.search_result['config_id'][row]
            saved_filepath = self.config_model.abstract.exportToFile(
                config_id, self._aptinkerQSettings)
            if saved_filepath:
                msg.setText(
                    'Successfully exported config (ID={0:d}) to the file "{1}".'.
                    format(config_id, saved_filepath))
                msg.exec_()
        else:
            msg.setText('You must select a configuration to be exported.')
            msg.setIcon(QMessageBox.Critical)
            msg.exec_()

    #----------------------------------------------------------------------
    def editConfigNameOrDescription(self):
        """"""

        msg = QMessageBox()

        inds = self.selectionModel.selectedRows()

        if inds != []:
            row = inds[0].row()
            config_id = self.search_result['config_id'][row]

            title = 'Edit Config Name or Description'
            prompt = 'Property to Edit:'
            result = QInputDialog.getItem(
                self, title, prompt, ['Name', 'Description'], current=1,
                editable=False)

            if result[1]:
                table_name = 'config_meta_text_search_table'
                if result[0] == 'Name':
                    current_name, current_desc = self.db.getColumnDataFromTable(
                        table_name, column_name_list=['config_name',
                                                      'config_description'],
                        condition_str='config_id={0:d}'.format(config_id))
                    current_name = current_name[0]
                    current_desc = current_desc[0]

                    title = 'Edit Config Name'
                    prompt = 'Enter a new name:'
                    result = QInputDialog.getText(self, title, prompt,
                                                  text=current_name)

                    if result[1]:
                        new_name = result[0]

                        mod_time_str = datestr(time.time())
                        new_desc = current_desc + (
                            ('\n### Modified by "{0}" on {1}###\n  Config Name '
                             'changed from "{2}" to "{3}"\n').format(
                                 getusername(), mod_time_str, current_name,
                                 new_name))

                        self.db.changeValues(
                            table_name, 'config_name',
                            '"{0}"'.format(new_name.replace('"', '""')),
                            condition_str='config_id={0:d}'.format(config_id))
                        self.db.changeValues(
                            table_name, 'config_description',
                            '"{0}"'.format(new_desc.replace('"', '""')),
                            condition_str='config_id={0:d}'.format(config_id))

                        # Update Config Meta DB Table
                        row = self.search_result['config_id'].index(config_id)
                        self.search_result['config_name'][row] = new_name
                        self.search_result['config_description'][row] = new_desc
                        self.tableModel_config_meta.repaint()
                        self.on_selection_change(None, None)

                else:
                    current_desc, = self.db.getColumnDataFromTable(
                        table_name, column_name_list=['config_description'],
                        condition_str='config_id={0:d}'.format(config_id))
                    current_desc = current_desc[0]

                    dialog = ConfigDescriptionEditor(current_desc, parent=self)
                    dialog.exec_()

                    if dialog.result() == QDialog.Accepted:
                        mod_time_str = datestr(time.time())
                        temp_new_desc = dialog.plainTextEdit_new.property(
                            'plainText')

                        new_desc = current_desc + (
                            ('\n### Modified by "{0}" on {1}###\n{2}\n'.format(
                            getusername(), mod_time_str, temp_new_desc))
                        )

                        self.db.changeValues(
                            table_name, 'config_description',
                            '"{0}"'.format(new_desc.replace('"', '""')),
                            condition_str='config_id={0:d}'.format(config_id))

                        # Update Config Meta DB Table
                        row = self.search_result['config_id'].index(config_id)
                        self.search_result['config_description'][row] = new_desc
                        self.tableModel_config_meta.repaint()
                        self.on_selection_change(None, None)

        else:
            msg.setText('You must select a configuration whose name or '
                        'description to be edited.')
            msg.setIcon(QMessageBox.Critical)
            msg.exec_()

    #----------------------------------------------------------------------
    def closeEvent(self, event):
        """"""

        self.saveViewSettings()

        self.config_model.abstract.channel_ids = []

        event.accept()

    #----------------------------------------------------------------------
    def accept(self):
        """"""

        a = self.config_model.abstract

        if not a.isDataValid():
            return

        if not a.check_aphla_unitconv_updates():
            return

        self.saveViewSettings()

        super(ConfigDBSelector, self).accept() # will close the dialog

    #----------------------------------------------------------------------
    def reject(self):
        """"""

        self.config_model.abstract.channel_ids = []

        self.saveViewSettings()

        super(ConfigDBSelector, self).reject() # will close the dialog

    #----------------------------------------------------------------------
    def loadViewSettings(self):
        """"""

        self.settings.beginGroup('viewSize')

        rect = self.settings.value('position')
        if not rect:
            rect = QRect(0, 0, self.sizeHint().width(), self.sizeHint().height())
        self.setGeometry(rect)

        splitter_sizes = self.settings.value('splitter_1')
        if splitter_sizes is None:
            splitter_sizes = [self.width()*(1./2), self.width()*(1./2)]
        else:
            splitter_sizes = [int(s) for s in splitter_sizes]
        self.splitter.setSizes(splitter_sizes)

        splitter_sizes = self.settings.value('splitter_2')
        if splitter_sizes is None:
            splitter_sizes = [self.width()*(1./5), self.width()*(4./5)]
        else:
            splitter_sizes = [int(s) for s in splitter_sizes]
        self.splitter_2.setSizes(splitter_sizes)

        splitter_sizes = self.settings.value('splitter_3')
        if splitter_sizes is None:
            splitter_sizes = [self.configMetaDBViewWidget.height()*(2./3),
                              self.configMetaDBViewWidget.height()*(1./3)]
        else:
            splitter_sizes = [int(s) for s in splitter_sizes]
        self.configMetaDBViewWidget.splitter.setSizes(splitter_sizes)

        self.settings.endGroup()

    #----------------------------------------------------------------------
    def saveViewSettings(self):
        """"""

        self.settings.beginGroup('viewSize')

        self.settings.setValue('position', self.geometry())

        self.settings.setValue('splitter_1', self.splitter.sizes())
        self.settings.setValue('splitter_2', self.splitter_2.sizes())
        self.settings.setValue('splitter_3',
                               self.configMetaDBViewWidget.splitter.sizes())

        self.settings.endGroup()

    #----------------------------------------------------------------------
    def validate_ref_step_size(self):
        """"""

        sender = self.sender()
        name = sender.objectName()
        text = sender.text().strip()
        if text == '':
            text = 'nan'

        try:
            new_float = float(text)
            if np.isnan(new_float):
                sender.setText('')
            self.prev_valid_ref_step_sizes[name] = new_float
        except:
            msg = QMessageBox()
            msg.setText('Invalid float string: {0:s}'.format(text))
            msg.setIcon(QMessageBox.Critical)
            msg.exec_()
            if np.isnan(self.prev_valid_ref_step_sizes[name]):
                sender.setText('')
            else:
                sender.setText(str(self.prev_valid_ref_step_sizes[name]))

    #----------------------------------------------------------------------
    def update_search(self):
        """"""

        try:
            config_id_1_text = str(int(self.lineEdit_config_id_1.text()))
        except:
            config_id_1_text = ''
        try:
            config_id_2_text = str(int(self.lineEdit_config_id_2.text()))
        except:
            config_id_2_text = ''
        config_id_1_operator = \
            self.comboBox_config_id_1.currentText().strip()
        config_id_2_operator = \
            self.comboBox_config_id_2.currentText().strip()
        if (config_id_1_text != '') and (config_id_1_operator != ''):
            self.search_params['config_id_1'] = (
                'config_id {0:s} {1:s}'.format(config_id_1_operator,
                                               config_id_1_text))
        else:
            self.search_params['config_id_1'] = ''
        if (config_id_2_text != '') and (config_id_2_operator != ''):
            self.search_params['config_id_2'] = (
                'config_id {0:s} {1:s}'.format(config_id_2_operator,
                                               config_id_2_text))
        else:
            self.search_params['config_id_2'] = ''

        try:
            masar_id_1_text = str(int(self.lineEdit_masar_id_1.text()))
        except:
            masar_id_1_text = ''
        try:
            masar_id_2_text = str(int(self.lineEdit_masar_id_2.text()))
        except:
            masar_id_2_text = ''
        masar_id_1_operator = \
            self.comboBox_masar_id_1.currentText().strip()
        masar_id_2_operator = \
            self.comboBox_masar_id_2.currentText().strip()
        if (masar_id_1_text != '') and (masar_id_1_operator != ''):
            self.search_params['masar_id_1'] = (
                'config_masar_id {0:s} {1:s}'.format(masar_id_1_operator,
                                                     masar_id_1_text))
        else:
            self.search_params['masar_id_1'] = ''
        if (masar_id_2_text != '') and (masar_id_2_operator != ''):
            self.search_params['masar_id_2'] = (
                'config_masar_id {0:s} {1:s}'.format(masar_id_2_operator,
                                                     masar_id_2_text))
        else:
            self.search_params['masar_id_2'] = ''

        try:
            ref_step_size_1_text = '{0:.9e}'.format(
                float(self.lineEdit_ref_step_size_1.text()))
        except:
            ref_step_size_1_text = ''
        try:
            ref_step_size_2_text = '{0:.9e}'.format(
                float(self.lineEdit_ref_step_size_2.text()))
        except:
            ref_step_size_2_text = ''
        ref_step_size_1_operator = \
            self.comboBox_ref_step_size_1.currentText().strip()
        ref_step_size_2_operator = \
            self.comboBox_ref_step_size_2.currentText().strip()
        if (ref_step_size_1_text != '') and (ref_step_size_1_operator != ''):
            self.search_params['ref_step_size_1'] = (
                'config_ref_step_size {0:s} {1:s}'.format(
                    ref_step_size_1_operator, ref_step_size_1_text))
        else:
            self.search_params['ref_step_size_1'] = ''
        if (ref_step_size_2_text != '') and (ref_step_size_2_operator != ''):
            self.search_params['ref_step_size_2'] = (
                'config_ref_step_size {0:s} {1:s}'.format(
                    ref_step_size_2_operator, ref_step_size_2_text))
        else:
            self.search_params['ref_step_size_2'] = ''

        synced_group_weight_text = \
            self.comboBox_synced_group_weight.currentText()
        if synced_group_weight_text == 'False':
            self.search_params['synced_group_weight'] = \
                'config_synced_group_weight = 0'
        elif synced_group_weight_text == 'True':
            self.search_params['synced_group_weight'] = \
                'config_synced_group_weight = 1'
        else:
            self.search_params['synced_group_weight'] = ''

        config_name_text = self.lineEdit_config_name.text().strip()
        if config_name_text != '':
            cond_str = self.db.get_MATCH_condition_str(config_name_text)
            if cond_str is not None:
                try:
                    self.search_params['config_name'] = \
                        self.db.get_config_ids_with_MATCH(cond_str, 'config_name')
                except:
                    msg = QMessageBox()
                    msg.setText('Invalid search strings for "Config Name"')
                    msg.setInformativeText(sys.exc_info()[1].__repr__())
                    msg.setIcon(QMessageBox.Critical)
                    msg.exec_()
                    return
            else:
                return
        else:
            self.search_params['config_name'] = []

        config_desc_text = self.lineEdit_config_description.text().strip()
        if config_desc_text != '':
            cond_str = self.db.get_MATCH_condition_str(config_desc_text)
            if cond_str is not None:
                try:
                    self.search_params['config_description'] = \
                        self.db.get_config_ids_with_MATCH(cond_str, 'config_description')
                except:
                    msg = QMessageBox()
                    msg.setText('Invalid search strings for "Config Description"')
                    msg.setInformativeText(sys.exc_info()[1].__repr__())
                    msg.setIcon(QMessageBox.Critical)
                    msg.exec_()
                    return
            else:
                return
        else:
            self.search_params['config_description'] = []

        username_text = self.lineEdit_username.text().strip()
        if username_text != '':
            self.search_params['username'] = \
                self.db.get_GLOB_condition_str(username_text, 'username')
        else:
            self.search_params['username'] = ''

        ctime_1_operator = self.comboBox_time_created_1.currentText().strip()
        if ctime_1_operator != '':
            ctime_epoch_1 = self.dateTimeEdit_time_created_1.dateTime()
            ctime_epoch_1 = time.mktime(ctime_epoch_1.toPyDateTime().timetuple())
            self.search_params['ctime_1'] = (
                'config_ctime {0:s} {1:.3f}'.format(ctime_1_operator, ctime_epoch_1))
        else:
            self.search_params['ctime_1'] = ''
        ctime_2_operator = self.comboBox_time_created_2.currentText().strip()
        if ctime_2_operator != '':
            ctime_epoch_2 = self.dateTimeEdit_time_created_2.dateTime()
            ctime_epoch_2 = time.mktime(ctime_epoch_2.toPyDateTime().timetuple())
            self.search_params['ctime_2'] = (
                'config_ctime {0:s} {1:.3f}'.format(ctime_2_operator, ctime_epoch_2))
        else:
            self.search_params['ctime_2'] = ''

        if (self.search_params['config_name'] is None) or \
           (self.search_params['config_description'] is None):
            for k in self.config_meta_all_col_keys:
                self.search_result[k] = []
        else:
            condition_str = ''
            for k, v in self.search_params.items():
                if k in ('config_name', 'config_description'):
                    if v:
                        if condition_str != '':
                            condition_str += ' AND '
                        condition_str += '(config_id IN ({0:s}))'.format(
                            ','.join([str(i) for i in v]))
                else:
                    if v:
                        if condition_str != '':
                            condition_str += ' AND '
                        condition_str += '({0:s})'.format(v)
            out = self.db.getColumnDataFromTable(
                '[config_meta_table text view]',
                column_name_list=self.config_meta_all_col_keys,
                condition_str=condition_str, order_by_str='config_id')
            if out != []:
                if self.checkBox_hide_NG.isChecked():
                    config_name_col_ind = self.config_meta_all_col_keys.index(
                        'config_name')
                    valid_indexes = [
                        i for i, name in enumerate(out[config_name_col_ind])
                        if '$NG$' not in name]
                else:
                    valid_indexes = range(len(out[0]))
                for k, v in zip(self.config_meta_all_col_keys, out):
                    self.search_result[k] = [x for i, x in enumerate(v)
                                             if i in valid_indexes]
            else:
                for k in self.config_meta_all_col_keys:
                    self.search_result[k] = []

        self.tableModel_config_meta.repaint()

        self.on_selection_change(None, None)

    #----------------------------------------------------------------------
    def convert_GLOB_to_LIKE_wildcards(self, char):
        """"""

        if char == '*':
            return '%'
        elif char == '?':
            return '_'
        else:
            raise ValueError('Unexpected char: {0:s}'.format(char))

    #----------------------------------------------------------------------
    def get_LIKE_condition_str(self, glob_pattern, column_name):
        """"""

        backslahs_inds = [i for i, c in enumerate(glob_pattern) if c == '\\']
        like_pattern = ''.join(
            [self.convert_GLOB_to_LIKE_wildcards(c)
             if (c in ('*','?')) and (i-1 not in backslahs_inds) else c
             for i, c in enumerate(glob_pattern)])
        cond_str = '({0:s} LIKE "{1:s}" ESCAPE "\\")'.format(column_name,
                                                             like_pattern)

        return cond_str

    #----------------------------------------------------------------------
    def on_selection_change(self, current_index, previous_index):
        """"""

        a = self.config_model.abstract

        if current_index is None:
            self.textEdit_description.setText('')
            a.ref_step_size = np.nan
            (a.group_name_ids, a.channel_ids, a.weights,
             a.caput_enabled_rows) = [], [], [], []
        else:
            row = current_index.row()

            a.config_id    = self.search_result['config_id'][row]
            a.name         = self.search_result['config_name'][row]
            a.description  = self.search_result['config_description'][row]
            a.config_ctime = self.search_result['config_ctime'][row]

            self.textEdit_description.setText(a.description)

            a.ref_step_size = self.search_result['config_ref_step_size'][row]
            out = self.db.getColumnDataFromTable(
                'config_table',
                column_name_list=['group_name_id', 'channel_id',
                                  'config_weight', 'config_caput_enabled'],
                condition_str='config_id={0:d}'.format(
                    self.search_result['config_id'][row]))

            if out != []:
                (a.group_name_ids, a.channel_ids, a.weights,
                 a.caput_enabled_rows) = map(list, out)
            else:
                (a.group_name_ids, a.channel_ids, a.weights,
                 a.caput_enabled_rows) = [], [], [], []

            a.weights = [w if w is not None else np.nan for w in a.weights]

        self.config_model.table.updateModel()
        self.config_model.table.repaint()

########################################################################
class ConfigModel(QObject):
    """"""

    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""

        QObject.__init__(self)

        self.abstract = ConfigAbstractModel()
        self.table    = ConfigTableModel(abstract_model=self.abstract,
                                         readonly=True)
        #self.tree     = ConfigTreeModel()

        self.db = self.abstract.db

#----------------------------------------------------------------------
def exportAllConfigsToFiles():
    """"""

    db = TinkerMainDatabase()

    max_config_id = db.getMaxInColumn('config_meta_table', 'config_id')

    if '[config_meta_table text view]' \
       not in db.getViewNames():
        db.create_temp_config_meta_table_text_view()

    for config_id in range(1, max_config_id+1):
        config_abs = ConfigAbstractModel()
        config_abs.exportToFile(config_id, qsettings=None, auto=True)

#----------------------------------------------------------------------
def make(isModal=True, parentWindow=None, aptinkerQSettings=None):
    """"""

    dialog = ConfigDBSelector(parent=parentWindow,
                              aptinkerQSettings=aptinkerQSettings)

    if isModal:
        dialog.exec_()
    else:
        dialog.show()

    return dialog

#----------------------------------------------------------------------
def main():
    """"""

    args = sys.argv

    # If Qt is to be used (for any GUI) then the cothread library needs to
    # be informed, before any work is done with Qt. Without this line
    # below, the GUI window will not show up and freeze the program.
    cothread.iqt()

    dialog = make(isModal=False, parentWindow=None)

    cothread.WaitForQuit()
    print(dialog.config_model.abstract.channel_ids)

if __name__ == '__main__':
    #main()

    exportAllConfigsToFiles()