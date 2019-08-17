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
    Qt, QObject, SIGNAL, QSettings, QDateTime, QRect
)
from PyQt4.QtGui import (
    QSortFilterProxyModel, QMessageBox, QIcon, QDialog, QIntValidator,
    QItemSelectionModel)

import cothread

import config
from tinkerModels import (SnapshotAbstractModel, SnapshotTableModel,
                          MetaTableModel, ConfigAbstractModel)
from dbviews import (SnapshotDBViewWidget, SnapshotMetaDBViewWidget,
                     SnapshotDBTableViewItemDelegate)
from tinkerdb import TinkerMainDatabase
from ui_tinkerSnapshotDBSelector import Ui_Dialog

HOME_PATH             = osp.expanduser('~')
APHLA_USER_CONFIG_DIR = osp.join(HOME_PATH, '.aphla')
if not osp.exists(APHLA_USER_CONFIG_DIR):
    os.makedirs(APHLA_USER_CONFIG_DIR)

PREF_SS_META_JSON_FILEPATH = osp.join(
    APHLA_USER_CONFIG_DIR, 'aptinker_snapshotDBSelector_SSMeta_pref.json')
PREF_SS_JSON_FILEPATH = osp.join(
    APHLA_USER_CONFIG_DIR, 'aptinker_snapshotDBSelector_SS_pref.json')

########################################################################
class SnapshotDBSelector(QDialog, Ui_Dialog):
    """"""

    #----------------------------------------------------------------------
    def __init__(self, parent=None, aptinkerQSettings=None):
        """Constructor"""

        QDialog.__init__(self, parent=parent)

        self.setupUi(self)

        self.setWindowFlags(Qt.Window) # To add Maximize & Minimize buttons
        self.setWindowTitle('Select Snapshot from Database')

        # Load Startup Preferences for Snapshot Table
        self.default_ss_pref = dict(
            vis_col_key_list=config.DEF_VIS_COL_KEYS['snapshot_DB'][:])
        if osp.exists(PREF_SS_JSON_FILEPATH):
            with open(PREF_SS_JSON_FILEPATH, 'r') as f:
                self.ss_pref = json.load(f)
        else:
            self.ss_pref = self.default_ss_pref

        # Load Startup Preferences for Snapshot Meta Table
        self.default_ss_meta_pref = dict(
            vis_col_key_list=['ss_id', 'config_id', 'ss_ctime', 'ss_name',
                              'ss_username'])
        if osp.exists(PREF_SS_META_JSON_FILEPATH):
            with open(PREF_SS_META_JSON_FILEPATH, 'r') as f:
                self.ss_meta_pref = json.load(f)
        else:
            self.ss_meta_pref = self.default_ss_meta_pref

        self.ssDBViewWidget = SnapshotDBViewWidget(self.groupBox_selected_ss,
                                                   DB_selector=True)
        self.tableView_ss = self.ssDBViewWidget.tableView

        self.ssMetaDBViewWidget = SnapshotMetaDBViewWidget(
            self.groupBox_search_result)
        self.tableView_ss_meta = self.ssMetaDBViewWidget.tableView
        self.textEdit_description = \
            self.ssMetaDBViewWidget.textEdit_description

        self.settings = QSettings('APHLA', 'TinkerSSDBSelector')
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
            ss_id_1='', ss_id_2='', config_id_1='', config_id_2='',
            ss_ref_step_size_1='', ss_ref_step_size_2='',
            ss_name='', ss_desc='', ss_username='', ss_ctime_1='', ss_ctime_2='',
            ss_synced_gruop_weight='', ss_masar_id_1='', ss_masar_id_2='')

        db_id_validator = QIntValidator()
        db_id_validator.setBottom(1)
        self.lineEdit_ss_id_1.setValidator(db_id_validator)
        self.lineEdit_ss_id_2.setValidator(db_id_validator)
        self.lineEdit_config_id_1.setValidator(db_id_validator)
        self.lineEdit_config_id_2.setValidator(db_id_validator)
        self.lineEdit_masar_id_1.setValidator(db_id_validator)
        self.lineEdit_masar_id_2.setValidator(db_id_validator)

        self.prev_valid_ref_step_sizes = dict(
            lineEdit_ref_step_size_1=np.nan, lineEdit_ref_step_size_2=np.nan)

        # Set up Snapshot Table
        self.ss_model = SnapshotModel(self.ss_pref['vis_col_key_list'])
        self.tableModel_ss = self.ss_model.table
        proxyModel = QSortFilterProxyModel()
        proxyModel.setSourceModel(self.tableModel_ss)
        proxyModel.setDynamicSortFilter(False)
        tbV = self.tableView_ss
        tbV.setModel(proxyModel)
        tbV.setItemDelegate(SnapshotDBTableViewItemDelegate(
            tbV, self.tableModel_ss, tbV.parent()))

        #self.db = TinkerMainDatabase()
        self.db = self.ss_model.db
        if '[ss_meta_table text view]' not in self.db.getViewNames(
            square_brackets=True):
            self.db.create_temp_ss_meta_table_text_view()

        # Set up Snapshot Meta Table
        self.ss_meta_all_col_keys = self.ssMetaDBViewWidget.all_col_keys
        self.search_result = {k: [] for k in self.ss_meta_all_col_keys}

        self.tableModel_ss_meta = MetaTableModel(
            self.search_result, self.ssMetaDBViewWidget)
        proxyModel = QSortFilterProxyModel()
        proxyModel.setSourceModel(self.tableModel_ss_meta)
        proxyModel.setDynamicSortFilter(False)
        tbV = self.tableView_ss_meta
        tbV.setModel(proxyModel)
        self.selectionModel = QItemSelectionModel(proxyModel)
        tbV.setSelectionModel(self.selectionModel)

        # Apply Visible Column Preference to Snapshot Meta Table
        ss_meta_vis_col_name_list = [
            self.ssMetaDBViewWidget.col_names_wo_desc[
                self.ssMetaDBViewWidget.col_keys_wo_desc.index(k)]
            for k in self.ss_meta_pref['vis_col_key_list']]
        self.ssMetaDBViewWidget.on_column_selection_change(
            ss_meta_vis_col_name_list, force_visibility_update=True)

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

        #self.connect(self.configMetaDBViewWidget, SIGNAL('exportConfigToFile'),
                     #self.exportConfigToFile)
        #self.connect(self.configMetaDBViewWidget,
                     #SIGNAL('editConfigNameOrDescription'),
                     #self.editConfigNameOrDescription)

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
            splitter_sizes = [self.ssMetaDBViewWidget.height()*(2./3),
                              self.ssMetaDBViewWidget.height()*(1./3)]
        else:
            splitter_sizes = [int(s) for s in splitter_sizes]
        self.ssMetaDBViewWidget.splitter.setSizes(splitter_sizes)

        self.settings.endGroup()

    #----------------------------------------------------------------------
    def saveViewSettings(self):
        """"""

        self.settings.beginGroup('viewSize')

        self.settings.setValue('position', self.geometry())

        self.settings.setValue('splitter_1', self.splitter.sizes())
        self.settings.setValue('splitter_2', self.splitter_2.sizes())
        self.settings.setValue('splitter_3',
                               self.ssMetaDBViewWidget.splitter.sizes())

        self.settings.endGroup()

    #----------------------------------------------------------------------
    def update_search(self):
        """"""

        try:
            ss_id_1_text = str(int(self.lineEdit_ss_id_1.text()))
        except:
            ss_id_1_text = ''
        try:
            ss_id_2_text = str(int(self.lineEdit_ss_id_2.text()))
        except:
            ss_id_2_text = ''
        ss_id_1_operator = \
            self.comboBox_ss_id_1.currentText().strip()
        ss_id_2_operator = \
            self.comboBox_ss_id_2.currentText().strip()
        if (ss_id_1_text != '') and (ss_id_1_operator != ''):
            self.search_params['ss_id_1'] = (
                'ss_id {0:s} {1:s}'.format(ss_id_1_operator, ss_id_1_text))
        else:
            self.search_params['ss_id_1'] = ''
        if (ss_id_2_text != '') and (ss_id_2_operator != ''):
            self.search_params['ss_id_2'] = (
                'ss_id {0:s} {1:s}'.format(ss_id_2_operator, ss_id_2_text))
        else:
            self.search_params['ss_id_2'] = ''

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
            self.search_params['ss_masar_id_1'] = (
                'ss_masar_id {0:s} {1:s}'.format(masar_id_1_operator,
                                                 masar_id_1_text))
        else:
            self.search_params['ss_masar_id_1'] = ''
        if (masar_id_2_text != '') and (masar_id_2_operator != ''):
            self.search_params['ss_masar_id_2'] = (
                'ss_masar_id {0:s} {1:s}'.format(masar_id_2_operator,
                                                 masar_id_2_text))
        else:
            self.search_params['ss_masar_id_2'] = ''

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
            self.search_params['ss_ref_step_size_1'] = (
                'ss_ref_step_size {0:s} {1:s}'.format(
                    ref_step_size_1_operator, ref_step_size_1_text))
        else:
            self.search_params['ss_ref_step_size_1'] = ''
        if (ref_step_size_2_text != '') and (ref_step_size_2_operator != ''):
            self.search_params['ss_ref_step_size_2'] = (
                'ss_ref_step_size {0:s} {1:s}'.format(
                    ref_step_size_2_operator, ref_step_size_2_text))
        else:
            self.search_params['ss_ref_step_size_2'] = ''

        ss_synced_group_weight_text = \
            self.comboBox_synced_group_weight.currentText()
        if ss_synced_group_weight_text == 'False':
            self.search_params['ss_synced_group_weight'] = \
                'ss_synced_group_weight = 0'
        elif ss_synced_group_weight_text == 'True':
            self.search_params['ss_synced_group_weight'] = \
                'ss_synced_group_weight = 1'
        else:
            self.search_params['ss_synced_group_weight'] = ''

        ss_name_text = self.lineEdit_ss_name.text().strip()
        if ss_name_text != '':
            cond_str = self.db.get_MATCH_condition_str(ss_name_text)
            if cond_str is not None:
                try:
                    self.search_params['ss_name'] = \
                        self.db.get_ss_ids_with_MATCH(cond_str, 'ss_name')
                except:
                    msg = QMessageBox()
                    msg.setText('Invalid search strings for "Snapshot Name"')
                    msg.setInformativeText(sys.exc_info()[1].__repr__())
                    msg.setIcon(QMessageBox.Critical)
                    msg.exec_()
                    return
            else:
                return
        else:
            self.search_params['ss_name'] = []

        ss_desc_text = self.lineEdit_ss_description.text().strip()
        if ss_desc_text != '':
            cond_str = self.db.get_MATCH_condition_str(ss_desc_text)
            if cond_str is not None:
                try:
                    self.search_params['ss_description'] = \
                        self.db.get_ss_ids_with_MATCH(cond_str, 'ss_description')
                except:
                    msg = QMessageBox()
                    msg.setText('Invalid search strings for "Snapshot Description"')
                    msg.setInformativeText(sys.exc_info()[1].__repr__())
                    msg.setIcon(QMessageBox.Critical)
                    msg.exec_()
                    return
            else:
                return
        else:
            self.search_params['ss_description'] = []

        ss_username_text = self.lineEdit_username.text().strip()
        if ss_username_text != '':
            self.search_params['ss_username'] = \
                self.db.get_GLOB_condition_str(ss_username_text, 'ss_username')
        else:
            self.search_params['ss_username'] = ''

        ctime_1_operator = self.comboBox_time_created_1.currentText().strip()
        if ctime_1_operator != '':
            ctime_epoch_1 = self.dateTimeEdit_time_created_1.dateTime()
            ctime_epoch_1 = time.mktime(ctime_epoch_1.toPyDateTime().timetuple())
            self.search_params['ss_ctime_1'] = (
                'ss_ctime {0:s} {1:.3f}'.format(ctime_1_operator, ctime_epoch_1))
        else:
            self.search_params['ss_ctime_1'] = ''
        ctime_2_operator = self.comboBox_time_created_2.currentText().strip()
        if ctime_2_operator != '':
            ctime_epoch_2 = self.dateTimeEdit_time_created_2.dateTime()
            ctime_epoch_2 = time.mktime(ctime_epoch_2.toPyDateTime().timetuple())
            self.search_params['ss_ctime_2'] = (
                'ss_ctime {0:s} {1:.3f}'.format(ctime_2_operator, ctime_epoch_2))
        else:
            self.search_params['ss_ctime_2'] = ''

        if (self.search_params['ss_name'] is None) or \
           (self.search_params['ss_description'] is None):
            for k in self.ss_meta_all_col_keys:
                self.search_result[k] = []
        else:
            condition_str = ''
            for k, v in self.search_params.items():
                if k in ('ss_name', 'ss_description'):
                    if v:
                        if condition_str != '':
                            condition_str += ' AND '
                        condition_str += '(ss_id IN ({0:s}))'.format(
                            ','.join([str(i) for i in v]))
                else:
                    if v:
                        if condition_str != '':
                            condition_str += ' AND '
                        condition_str += '({0:s})'.format(v)
            out = self.db.getColumnDataFromTable(
                '[ss_meta_table text view]',
                column_name_list=self.ss_meta_all_col_keys,
                condition_str=condition_str, order_by_str='ss_id')
            if out != []:
                if self.checkBox_hide_NG.isChecked():
                    ss_name_col_ind = self.ss_meta_all_col_keys.index('ss_name')
                    valid_indexes = [
                        i for i, name in enumerate(out[ss_name_col_ind])
                        if '$NG$' not in name]
                else:
                    valid_indexes = range(len(out[0]))
                for k, v in zip(self.ss_meta_all_col_keys, out):
                    self.search_result[k] = [x for i, x in enumerate(v)
                                             if i in valid_indexes]
            else:
                for k in self.ss_meta_all_col_keys:
                    self.search_result[k] = []

        self.tableModel_ss_meta.repaint()

        self.on_selection_change(None, None)

    #----------------------------------------------------------------------
    def on_selection_change(self, current_index, previous_index):
        """"""

        _ca = self.ss_model.config_abstract
        _sa = self.ss_model.abstract
        _ct = _sa._config_table
        _st = self.ss_model.table

        if current_index is None:

            _ca.config_id           = None
            _ca.name                = ''
            _ca.description         = ''
            _ca.config_ctime        = None
            _ca.ref_step_size       = np.nan
            _ca.synced_group_weight = True

            (_ca.group_name_ids, _ca.channel_ids, _ca.weights,
             _ca.caput_enabled_rows) = [], [], [], []

            _ca.weights = [w if w is not None else np.nan for w in _ca.weights]

            _ct.updateModel()

            _sa.description = ''

            _sa.ss_id       = None
            _sa.name        = ''
            _sa.description = ''
            _sa.ss_ctime    = None
            _sa.ref_step_size = np.nan
            _sa.synced_group_weight = True

            _sa.nRows = len(_ca.channel_ids)

        else:
            row = current_index.row()

            _ca.config_id    = self.search_result['config_id'][row]
            _ca.name         = self.search_result['config_name'][row]
            _ca.description  = self.search_result['config_description'][row]
            _ca.config_ctime = self.search_result['config_ctime'][row]
            _ca.ref_step_size = self.search_result['config_ref_step_size'][row]
            _ca.synced_group_weight = self.search_result['config_synced_group_weight']

            out = self.db.getColumnDataFromTable(
                'config_table',
                column_name_list=['group_name_id', 'channel_id',
                                  'config_weight', 'config_caput_enabled'],
                condition_str='config_id={0:d}'.format(_ca.config_id))

            if out != []:
                (_ca.group_name_ids, _ca.channel_ids, _ca.weights,
                 _ca.caput_enabled_rows) = map(list, out)
            else:
                (_ca.group_name_ids, _ca.channel_ids, _ca.weights,
                 _ca.caput_enabled_rows) = [], [], [], []

            _ca.weights = [w if w is not None else np.nan for w in _ca.weights]

            _ct.updateModel()

            _sa.ss_id       = self.search_result['ss_id'][row]
            _sa.name        = self.search_result['ss_name'][row]
            _sa.description = self.search_result['ss_description'][row]
            _sa.ss_ctime    = self.search_result['ss_ctime'][row]
            _sa.ref_step_size = self.search_result['ss_ref_step_size'][row]
            _sa.synced_group_weight = \
                self.search_result['ss_synced_group_weight'][row]

            _sa.nRows = len(_ca.channel_ids)

            _sa.update_caget_list()
            _sa.update_caput_list()
            _sa.update_rb_sp_same_size_rows_list()
            _sa.update_maps()
            _sa.init_unitconv()

            _st._init_d()

        self.textEdit_description.setText(_sa.description)

        from_DB = True
        self.ss_model.table.update_snapshot_columns(from_DB)
        self.ss_model.table.repaint()
        if current_index is not None:
            visible_col_names = [_sa.all_col_names[_sa.all_col_keys.index(k)]
                                 for k in _sa.visible_col_keys]
            self.ssDBViewWidget.on_column_selection_change(
                visible_col_names, force_visibility_update=True)

    #----------------------------------------------------------------------
    def closeEvent(self, event):
        """"""

        self.saveViewSettings()

        self.ss_model.abstract.channel_ids = []

        event.accept()

    #----------------------------------------------------------------------
    def accept(self):
        """"""

        _sa = self.ss_model.abstract
        _ca = _sa._config_abstract

        if not _ca.isDataValid():
            return

        if not _ca.check_aphla_unitconv_updates():
            return

        self.saveViewSettings()

        super(SnapshotDBSelector, self).accept() # will close the dialog

    #----------------------------------------------------------------------
    def reject(self):
        """"""

        self.ss_model.abstract._config_abstract.channel_ids = []

        self.saveViewSettings()

        super(SnapshotDBSelector, self).reject() # will close the dialog


########################################################################
class SnapshotModel(QObject):
    """"""

    #----------------------------------------------------------------------
    def __init__(self, vis_col_key_list):
        """Constructor"""

        QObject.__init__(self)

        self.config_abstract = ConfigAbstractModel()

        self.abstract = SnapshotAbstractModel(
            self.config_abstract, vis_col_key_list, DB_view=True)
        self.table = SnapshotTableModel(self.abstract, DB_view=True)
        #self.tree = SnapshotTreeModel()

        self.db = self.abstract.db

#----------------------------------------------------------------------
def make(isModal=True, parentWindow=None, aptinkerQSettings=None):
    """"""

    dialog = SnapshotDBSelector(parent=parentWindow,
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
    main()
