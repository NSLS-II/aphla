import sip
sip.setapi('QString', 2)
sip.setapi('QVariant', 2)

import os, sys
import os.path as osp
import numpy as np
import json

from PyQt4.QtCore import (
    Qt, QObject, SIGNAL, QSettings, QRect
)
from PyQt4.QtGui import (
    QSortFilterProxyModel, QMessageBox, QIcon, QDialog, QIntValidator,
    QItemSelectionModel
)

import cothread

import config
from tinkerModels import (ConfigMetaTableModel, ConfigAbstractModel,
                          ConfigTableModel)
from dbviews import (ConfigDBViewWidget, ConfigMetaDBViewWidget)
from ui_tinkerConfigDBSelector import Ui_Dialog

HOME_PATH             = osp.expanduser('~')
APHLA_USER_CONFIG_DIR = osp.join(HOME_PATH, '.aphla')
if not osp.exists(APHLA_USER_CONFIG_DIR):
    os.makedirs(APHLA_USER_CONFIG_DIR)

PREF_CONFIG_META_JSON_FILEPATH = osp.join(
    APHLA_USER_CONFIG_DIR, 'aptinker_ConfigDBSelector_ConfigMeta_pref.json')
PREF_CONFIG_JSON_FILEPATH = osp.join(
    APHLA_USER_CONFIG_DIR, 'aptinker_ConfigDBSelector_Config_pref.json')

########################################################################
class ConfigDBSelector(QDialog, Ui_Dialog):
    """"""

    #----------------------------------------------------------------------
    def __init__(self, parent=None):
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

        self.pushButton_search.setIcon(QIcon(':/search.png'))

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

        self.db = self.config_model.db
        self.db.create_temp_config_meta_table_text_view()

        # Set up Config Meta Table
        self.config_meta_all_col_keys = \
            self.db.getColumnNames('[config_meta_table text view]')
        self.search_result = {k: [] for k in self.config_meta_all_col_keys}

        self.tableModel_config_meta = ConfigMetaTableModel(
            self.search_result, self.config_meta_all_col_keys)
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

    #----------------------------------------------------------------------
    def closeEvent(self, event):
        """"""

        self.saveViewSettings()

        self.config_model.abstract.channel_ids = []

        event.accept()

    #----------------------------------------------------------------------
    def accept(self):
        """"""

        if not self.config_model.abstract.isDataValid():
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

        condition_str = ''
        for _, v in self.search_params.iteritems():
            if v:
                if condition_str != '':
                    condition_str += ' AND '
                condition_str += '({0:s})'.format(v)
        out = self.db.getColumnDataFromTable(
            '[config_meta_table text view]',
            column_name_list=self.config_meta_all_col_keys,
            condition_str=condition_str, order_by_str='config_id')
        if out != []:
            for k, v in zip(self.config_meta_all_col_keys, out):
                self.search_result[k] = list(v)
        else:
            for k in self.config_meta_all_col_keys:
                self.search_result[k] = []

        self.tableModel_config_meta.repaint()

    #----------------------------------------------------------------------
    def on_selection_change(self, current_index, previous_index):
        """"""

        row = current_index.row()

        description = self.search_result['config_description'][row]

        self.textEdit_description.setText(description)

        a = self.config_model.abstract
        a.ref_step_size = self.search_result['config_ref_step_size'][row]
        out = self.db.getColumnDataFromTable(
            'config_table',
            column_name_list=['group_name_id', 'channel_id', 'config_weight'],
            condition_str='config_id={0:d}'.format(
                self.search_result['config_id'][row]))

        if out != []:
            (a.group_name_ids, a.channel_ids, a.weights) = map(list, out)
        else:
            (a.group_name_ids, a.channel_ids, a.weights) = [], [], []

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

        self.output = None

#----------------------------------------------------------------------
def make(isModal=True, parentWindow=None):
    """"""

    dialog = ConfigDBSelector(parent=parentWindow)

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
    print dialog.config_model.abstract.channel_ids

if __name__ == '__main__':
    main()
