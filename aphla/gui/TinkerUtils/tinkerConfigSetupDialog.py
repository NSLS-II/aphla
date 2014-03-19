#! /usr/bin/env python

import sip
sip.setapi('QString', 2)
sip.setapi('QVariant', 2)

import sys, os
import os.path as osp
import h5py
import json
import time
from copy import deepcopy

from PyQt4.QtCore import (Qt, SIGNAL, QObject, QSettings, QSize, QMetaObject,
                          Q_ARG, QRect)
from PyQt4.QtGui import (
    QApplication, QDialog, QSortFilterProxyModel, QAbstractItemView, QAction,
    QIcon, QFileDialog, QMessageBox, QInputDialog, QMenu, QTextEdit, QFont,
    QItemSelectionModel
)

import cothread

import aphla as ap

import config
from tinkerModels import (ConfigAbstractModel, ConfigTableModel,
                          ConfigTreeModel)
from tinkerdb import (TinkerMainDatabase, unitsys_id_raw, pv_id_NonSpecified)
from dbviews import ConfigDBViewWidget
from ui_tinkerConfigSetupDialog import Ui_Dialog
from ui_tinkerConfigSetupPref import Ui_Dialog as Ui_PrefDialog
from aphla.gui import channelexplorer
from aphla.gui.utils.tictoc import tic, toc
from aphla.gui.utils.orderselector import ColumnsDialog

FILE_FILTER_DICT = {'Text File': 'Tinker configuration text files (*.txt)',
                    'HDF5 File': 'HDF5 files (*.h5 *.hdf5)',
                    'JSON File': 'Tinker configuration JSON files (*.json)',
                    }

HOME_PATH             = osp.expanduser('~')
APHLA_USER_CONFIG_DIR = osp.join(HOME_PATH, '.aphla')
if not osp.exists(APHLA_USER_CONFIG_DIR):
    os.makedirs(APHLA_USER_CONFIG_DIR)

PREF_JSON_FILEPATH = osp.join(APHLA_USER_CONFIG_DIR,
                              'aptinker_ConfigSetupDialog_startup_pref.json')

########################################################################
class PreferencesEditor(QDialog, Ui_PrefDialog):
    """"""

    #----------------------------------------------------------------------
    def __init__(self, default_pref):
        """Constructor"""

        QDialog.__init__(self)

        self.setupUi(self)

        self.setWindowTitle('Startup Preferences')

        self.default_pref = default_pref

        (self.all_col_keys, self.all_col_names) = map(
            list,
            config.COL_DEF.getColumnDataFromTable(
                'column_table',
                column_name_list=['column_key', 'short_descrip_name'],
                condition_str='only_for_ss=0')
        )

        self.load_pref_json()

        self.connect(self.pushButton_restore_default, SIGNAL('clicked()'),
                     self.restore_default_pref)
        self.connect(self.pushButton_edit_visible_columns, SIGNAL('clicked()'),
                     self.launchColumnsDialog)

    #----------------------------------------------------------------------
    def load_pref_json(self):
        """"""

        if osp.exists(PREF_JSON_FILEPATH):
            with open(PREF_JSON_FILEPATH, 'r') as f:
                self.pref = json.load(f)
        else:
            # Use default startup preferences
            self.pref = deepcopy(self.default_pref)

        self.update_view()

    #----------------------------------------------------------------------
    def save_pref_json(self):
        """"""

        with open(PREF_JSON_FILEPATH, 'w') as f:
            json.dump(self.pref, f, indent=3, sort_keys=True,
                      separators=(',', ': '))

    #----------------------------------------------------------------------
    def restore_default_pref(self):
        """"""

        self.pref = deepcopy(self.default_pref)
        self.update_view()

    #----------------------------------------------------------------------
    def update_view(self):
        """"""

        self.update_column_list_only()

    #----------------------------------------------------------------------
    def update_column_list_only(self):
        """"""

        self.listWidget_visible_columns.clear()
        self.listWidget_visible_columns.addItems(
            self.convert_col_keys_to_names(self.pref['vis_col_key_list'])
        )

    #----------------------------------------------------------------------
    def convert_col_keys_to_names(self, keys):
        """"""

        return [self.all_col_names[self.all_col_keys.index(k)] for k in keys]

    #----------------------------------------------------------------------
    def convert_col_names_to_keys(self, names):
        """"""

        return [self.all_col_keys[self.all_col_names.index(n)] for n in names]

    #----------------------------------------------------------------------
    def launchColumnsDialog(self):
        """"""

        all_column_name_list = self.all_col_names[:]
        visible_column_name_list = self.convert_col_keys_to_names(
            self.pref['vis_col_key_list'])
        permanently_visible_column_name_list = \
            [self.all_col_names[self.all_col_keys.index('group_name')]]

        dialog = ColumnsDialog(all_column_name_list,
                               visible_column_name_list,
                               permanently_visible_column_name_list,
                               parentWindow=self)
        dialog.exec_()

        if dialog.output is not None:
            self.pref['vis_col_key_list'] = self.convert_col_names_to_keys(
                dialog.output)
            self.update_column_list_only()

    #----------------------------------------------------------------------
    def accept(self):
        """"""

        # self.pref['vis_col_key_list'] is already updated whenever the list is
        # modified by column dialog. So, there is no need to update here.

        self.save_pref_json()

        super(PreferencesEditor, self).accept() # will hide the dialog

    #----------------------------------------------------------------------
    def reject(self):
        """"""

        super(PreferencesEditor, self).reject() # will hide the dialog

########################################################################
class Settings():
    """"""

    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""

        self._settings = QSettings('APHLA', 'TinkerConfigSetupDialog')

        self.loadMiscSettings()

    #----------------------------------------------------------------------
    def loadViewSizeSettings(self, view):
        """"""

        self._settings.beginGroup('viewSize')

        self._position = self._settings.value('position')
        if self._position is None:
            sizeHint = view.sizeHint()
            self._position = QRect(0, 0, sizeHint.width(), sizeHint.height())
        view.setGeometry(self._position)

        self._splitter_top_bottom_sizes = self._settings.value(
            'splitter_top_bottom_sizes')
        if self._splitter_top_bottom_sizes is None:
            half_height = int(view.height()/2.0)
            self._splitter_top_bottom_sizes = [half_height, half_height]
        if not isinstance(self._splitter_top_bottom_sizes[0], int):
            self._splitter_top_bottom_sizes = [int(s) for s in
                                               self._splitter_top_bottom_sizes]
        view.splitter.setSizes(self._splitter_top_bottom_sizes)

        self._settings.endGroup()

    #----------------------------------------------------------------------
    def saveViewSizeSettings(self, view):
        """"""

        self._settings.beginGroup('viewSize')

        self._position = view.geometry()
        self._settings.setValue('position', self._position)

        self._splitter_top_bottom_sizes = view.splitter.sizes()
        self._settings.setValue('splitter_top_bottom_sizes',
                                self._splitter_top_bottom_sizes)

        self._settings.endGroup()

    #----------------------------------------------------------------------
    def loadMiscSettings(self):
        """"""

        self._settings.beginGroup('fileSystem')

        self._last_directory_path = self._settings.value('last_directory_path')
        if self._last_directory_path is None:
            self._last_directory_path = os.getcwd()

        self._settings.endGroup()

    #----------------------------------------------------------------------
    def saveMiscSettings(self):
        """"""

        self._settings.beginGroup('fileSystem')

        self._settings.setValue('last_directory_path', self._last_directory_path)

        self._settings.endGroup()

########################################################################
class Model(QObject):
    """"""

    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""

        QObject.__init__(self)

        self.abstract = ConfigAbstractModel()
        self.table    = ConfigTableModel(abstract_model=self.abstract)
        #self.tree     = ConfigTreeModel()

        self.db = self.abstract.db

        self.output = None

    #----------------------------------------------------------------------
    def get_channel_ids(
        self, pvsp_list, pvrb_list, channel_name_list,
        unitsys_list=None, unitconv_key_list=None, unitconv_dict=None,
        aphla_channel_name_list=None):
        """
        If `unitsys_list` is not None, either `unitconv_key_list` (for
        non-APHLA channels) or `aphla_channel_name_list` (for APHLA channels)
        must be also provided.

        If `unitconv_key_list` is provided, `unitconv_dict` must be also
        provided.

        If both `unitconv_key` and `aphla_channel_name` are provided for
        a channel, `unitconv_key` will override `aphla_channel_name`.
        """

        msg = QMessageBox()

        NoSymb_id = self.db.getMatchingPrimaryKeyIdFrom2ColTable(
            'unitsymb_table', 'unitsymb_id', 'unitsymb', '', append_new=True)
        NoConv_NoSymb_unitconv_id = self.db.getColumnDataFromTable(
            'unitconv_table', column_name_list=['unitconv_id'],
            condition_str=('conv_data_txt="" AND src_unitsys_id={0:d} '
                           'AND dst_unitsys_id={0:d}').format(NoSymb_id))[0][0]

        n_channels = len(pvsp_list)

        if unitsys_list is None:
            # No unit conversion w/o unit symbol by default
            unitsys_id_list = [unitsys_id_raw]*n_channels
            unitconv_toraw_id_list   = [NoConv_NoSymb_unitconv_id]*n_channels
            unitconv_fromraw_id_list = [NoConv_NoSymb_unitconv_id]*n_channels
        else:
            unitsys_list = [s if s is not None else '' for s in unitsys_list]

            unitsys_id_list = [
                self.db.getMatchingPrimaryKeyIdFrom2ColTable(
                    'unitsys_table', 'unitsys_id', 'unitsys', v, append_new=True)
                for v in unitsys_list]

            unitconv_toraw_id_list   = [None]*n_channels
            unitconv_fromraw_id_list = [None]*n_channels
            aphla_ch_id_list         = [None]*n_channels

            if aphla_channel_name_list is not None:
                for i, (ap_ch_name, unitsys, unitsys_id) in enumerate(zip(
                    aphla_channel_name_list, unitsys_list, unitsys_id_list)):
                    if ap_ch_name in ('', None):
                        pass
                    else:
                        machine_name, lattice_name, elem_name, field = \
                            ap_ch_name.split('.')
                        if machine_name not in get_loaded_ap_machines():
                            ap.machines.load(machine_name)
                        ap.machines.use(lattice_name)
                        aphla_elem = ap.getElements(elem_name)[0]
                        uc_dict = aphla_elem._field[field].unitconv

                        machine_name_id = \
                            self.db.getMatchingPrimaryKeyIdFrom2ColTable(
                                'machine_name_table',
                                'machine_name_id', 'machine_name',
                                machine_name, append_new=True)
                        lattice_name_id = \
                            self.db.getMatchingPrimaryKeyIdFrom2ColTable(
                                'lattice_name_table', 'lattice_name_id',
                                'lattice_name', lattice_name, append_new=True)
                        elem_prop_id = self.db.get_elem_prop_id(
                            machine_name_id, lattice_name_id, aphla_elem,
                            append_new=True)
                        field_id = self.db.getMatchingPrimaryKeyIdFrom2ColTable(
                            'field_table', 'field_id', 'field', field,
                            append_new=True)
                        aphla_ch_id = self.db.get_aphla_ch_id(
                            elem_prop_id, field_id, append_new=True)
                        aphla_ch_id_list[i] = aphla_ch_id

                        src_unitsymb = aphla_elem.getUnit(field, unitsys=None)
                        dst_unitsymb = aphla_elem.getUnit(
                            field, unitsys=(unitsys if unitsys else None))

                        if unitsys == '':
                            uc = dict(type='NoConversion', src_unitsys='',
                                      dst_unitsys='', src_unitsymb=src_unitsymb,
                                      dst_unitsymb=dst_unitsymb, inv=0,
                                      conv_data='')

                            uc_id = self.db.get_unitconv_id(
                                uc, src_unitsys_id=None, dst_unitsys_id=None,
                                src_unitsymb=None, dst_unitsymb=None, inv=None,
                                append_new=True)

                            unitconv_fromraw_id_list[i] = uc_id
                            unitconv_toraw_id_list[i]   = uc_id

                            continue

                        inv = 0
                        if uc_dict.has_key((None, unitsys)):
                            uc = uc_dict[(None, unitsys)]
                        elif uc_dict.has_key((unitsys, None)):
                            uc = uc_dict[(unitsys, None)]
                            if uc.invertible:
                                inv = 1
                            else:
                                uc = None
                        else:
                            uc = None

                        unitconv_fromraw_id_list[i] = self.db.get_unitconv_id(
                            uc, src_unitsys_id=unitsys_id_raw,
                            dst_unitsys_id=unitsys_id,
                            src_unitsymb=src_unitsymb,
                            dst_unitsymb=dst_unitsymb, inv=inv,
                            append_new=True)

                        src_unitsymb, dst_unitsymb = dst_unitsymb, src_unitsymb

                        inv = 0
                        if uc_dict.has_key((unitsys, None)):
                            uc = uc_dict[(unitsys, None)]
                        elif uc_dict.has_key((None, unitsys)):
                            uc = uc_dict[(None, unitsys)]
                            if uc.invertible:
                                inv = 1
                            else:
                                uc = None
                        else:
                            uc = None

                        unitconv_toraw_id_list[i] = self.db.get_unitconv_id(
                            uc, src_unitsys_id=unitsys_id,
                            dst_unitsys_id=unitsys_id_raw,
                            src_unitsymb=src_unitsymb,
                            dst_unitsymb=dst_unitsymb, inv=inv,
                            append_new=True)

            # If both `unitconv_key` and `aphla_channel_name` are provided for
            # a channel, `unitconv_key` will override `aphla_channel_name`
            # unit conversion data here.
            if unitconv_key_list is not None:
                if unitconv_dict is None:
                    msg.setText(('If `unitconv_key_list` is specified, '
                                 '`unitconv_dict` must be also specified.'))
                    msg.exec_()
                    return
                else:
                    for _, v in unitconv_dict.iteritems():
                        for dd in v:
                            if dd['src_unitsys'] is None: dd['src_unitsys'] = ''
                            if dd['dst_unitsys'] is None: dd['dst_unitsys'] = ''

                    for i, (key, unitsys) in enumerate(zip(
                        unitconv_key_list, unitsys_list)):
                        if key in ('', None):
                            pass
                        elif unitconv_dict.has_key(key):
                            uc_list = unitconv_dict[key]
                            for uc in uc_list:
                                if (uc['src_unitsys'] == '') and \
                                   (uc['dst_unitsys'] == unitsys):
                                    break
                            unitconv_fromraw_id_list[i] = \
                                self.db.get_unitconv_id(
                                    uc, src_unitsys_id=None,
                                    dst_unitsys_id=None, src_unitsymb=None,
                                    dst_unitsymb=None, inv=None, append_new=True)
                            for uc in uc_list:
                                if (uc['src_unitsys'] == unitsys) and \
                                   (uc['dst_unitsys'] == ''):
                                    break
                            unitconv_toraw_id_list[i] = \
                                self.db.get_unitconv_id(
                                    uc, src_unitsys_id=None,
                                    dst_unitsys_id=None, src_unitsymb=None,
                                    dst_unitsymb=None, inv=None, append_new=True)
                        else:
                            msg.setText('Key not found in `unitconv_dict`: {0}'.
                                        format(key))
                            msg.exec_()
                            return

        channel_ids = []

        for (pvsp, pvrb, ch_name, unitsys_id, unitconv_toraw_id,
             unitconv_fromraw_id, aphla_ch_id) in zip(
                 pvsp_list, pvrb_list, channel_name_list, unitsys_id_list,
                 unitconv_toraw_id_list, unitconv_fromraw_id_list,
                 aphla_ch_id_list):

            if pvsp == '': readonly = -1
            else         : readonly = 0
            pvsp_id = self.db.get_pv_id(pvsp, readonly, append_new=True)
            if pvsp_id is None:
                msg.setText('ID for the following PV could not be found:')
                msg.setInformativeText('"{0:s}"'.format(pvsp))
                msg.exec_()
                return
            elif pvsp_id == -1:
                msg.setText('The following PV could not be connected:')
                msg.setInformativeText('"{0:s}"'.format(pvsp))
                msg.exec_()
                return
            elif pvsp_id == -2:
                return # Error message box is launched in get_pv_id()

            if pvrb == '': readonly = -1
            else         : readonly = 1
            pvrb_id = self.db.get_pv_id(pvrb, readonly, append_new=True)
            if pvrb_id is None:
                msg.setText('ID for the following PV could not be found:')
                msg.setInformativeText('"{0:s}"'.format(pvrb))
                msg.exec_()
                return
            elif pvrb_id == -1:
                msg.setText('The following PV could not be connected:')
                msg.setInformativeText('"{0:s}"'.format(pvrb))
                msg.exec_()
                return
            elif pvrb_id == -2:
                return # Error message box is launched in get_pv_id()

            channel_name_id = self.db.getMatchingPrimaryKeyIdFrom2ColTable(
                'channel_name_table', 'channel_name_id', 'channel_name',
                ch_name, append_new=True)

            channel_id = self.db.get_channel_id(
                pvsp_id, pvrb_id, unitsys_id, channel_name_id,
                unitconv_toraw_id, unitconv_fromraw_id,
                aphla_ch_id=aphla_ch_id, append_new=True)

            channel_ids.append(channel_id)

        return channel_ids

    #----------------------------------------------------------------------
    def importNewChannelsFromJSONFile(self, json_dict):
        """"""

        d = {}
        for i, k in enumerate(json_dict['column_names']):
            if isinstance(json_dict['channels'][0][i], unicode):
                # It is critical to convert "unicode" to "str" for catools
                # functions, as if the PV strings are not type "str", the
                # functions will assume the PV name to be a list of PVs
                # with each character as a PV name.
                d[k] = [str(c[i]) for c in json_dict['channels']]
            else:
                d[k] = [c[i] for c in json_dict['channels']]

        group_name_ids = [
            self.db.getMatchingPrimaryKeyIdFrom2ColTable(
                'group_name_table', 'group_name_id', 'group_name',
                group_name, append_new=True)
            for group_name in d['group_name']]

        if not d.has_key('unitsys'):
            channel_ids = self.get_channel_ids(d['pvsp'], d['pvrb'],
                                               d['channel_name'])
        else:
            if (not d.has_key('unitconv_key')) and \
               (not d.has_key('aphla_channel_name')):
                msg = QMessageBox()
                msg.setText(
                    ('If `column_names` include "unitsys", `column_names` '
                     'must also include either "unitconv_key" or '
                     '"aphla_channel_name" in your JSON config file.'))
                msg.exec_()
                return

            if d.has_key('unitconv_key'):
                unitconv_key_list = d['unitconv_key']
                if json_dict.has_key('unitconv_dict'):
                    unitconv_dict = json_dict['unitconv_dict']
                else:
                    msg = QMessageBox()
                    msg.setText(
                        ('If `column_names` include "unitconv_key", you '
                         'must also specify `unitconv_dict` in your JSON config '
                         'file.'))
                    msg.exec_()
                    return
            else:
                unitconv_key_list = None
                unitconv_dict     = None

            if d.has_key('aphla_channel_name'):
                aphla_channel_name_list = d['aphla_channel_name']
            else:
                aphla_channel_name_list = None

            channel_ids = self.get_channel_ids(
                d['pvsp'], d['pvrb'], d['channel_name'],
                unitsys_list=d['unitsys'], unitconv_key_list=unitconv_key_list,
                unitconv_dict=unitconv_dict,
                aphla_channel_name_list=aphla_channel_name_list)

        self.abstract.group_name_ids.extend(group_name_ids)
        self.abstract.channel_ids.extend(channel_ids)
        self.abstract.weights.extend(d['config_weight'])

        self.table.updateModel()
        self.table.repaint()

    #----------------------------------------------------------------------
    def importNewChannelsFromSelector(self, selection_dict, channel_group_info):
        """"""

        machine               = selection_dict['machine']
        lattice               = selection_dict['lattice']
        elem_obj_field_tuples = selection_dict['selection']

        machine_name_id = self.db.getMatchingPrimaryKeyIdFrom2ColTable(
            'machine_name_table', 'machine_name_id', 'machine_name', machine,
            append_new=True)
        lattice_name_id = self.db.getMatchingPrimaryKeyIdFrom2ColTable(
            'lattice_name_table', 'lattice_name_id', 'lattice_name', lattice,
            append_new=True)

        unitsys_id_phy = self.db.getMatchingPrimaryKeyIdFrom2ColTable(
            'unitsys_table', 'unitsys_id', 'unitsys', 'phy', append_new=True)

        channel_ids   = []
        channel_names = []
        pvsp_ids      = []
        for elem, field in elem_obj_field_tuples:
            elem_prop_id = self.db.get_elem_prop_id(
                machine_name_id, lattice_name_id, elem, append_new=True)
            field_id = self.db.getMatchingPrimaryKeyIdFrom2ColTable(
                'field_table', 'field_id', 'field', field, append_new=True)
            aphla_ch_id = self.db.get_aphla_ch_id(elem_prop_id, field_id,
                                                  append_new=True)
            pvsp = elem._field[field].pvsp
            if pvsp != []:
                pvsp     = pvsp[0]
                readonly = 0
            else:
                pvsp     = ''
                readonly = -1
            pvsp_id = self.db.get_pv_id(pvsp, readonly, append_new=True)
            if pvsp_id is None:
                msg = QMessageBox()
                msg.setText('ID for the following PV could not be found:')
                msg.setInformativeText('"{0:s}"'.format(pvsp))
                msg.exec_()
                return
            elif pvsp_id == -1:
                msg = QMessageBox()
                msg.setText('The following PV could not be connected:')
                msg.setInformativeText('"{0:s}"'.format(pvsp))
                msg.exec_()
                return
            elif pvsp_id == -2:
                return # Error message box is launched in get_pv_id()

            pvrb = elem._field[field].pvrb
            if pvrb != []:
                pvrb     = pvrb[0]
                readonly = 1
            else:
                pvrb     = ''
                readonly = -1
            pvrb_id = self.db.get_pv_id(pvrb, readonly, append_new=True)
            if pvrb_id is None:
                msg = QMessageBox()
                msg.setText('ID for the following PV could not be found:')
                msg.setInformativeText('"{0:s}"'.format(pvrb))
                msg.exec_()
                return
            elif pvrb_id == -1:
                msg = QMessageBox()
                msg.setText('The following PV could not be connected:')
                msg.setInformativeText('"{0:s}"'.format(pvrb))
                msg.exec_()
                return
            elif pvrb_id == -2:
                return # Error message box is launched in get_pv_id()

            channel_name = '{0:s}.{1:s}.{2:s}'.format(lattice, elem.name, field)
            channel_names.append(channel_name)
            channel_name_id = self.db.getMatchingPrimaryKeyIdFrom2ColTable(
                'channel_name_table', 'channel_name_id', 'channel_name',
                channel_name, append_new=True)

            uc_dict = elem._field[field].unitconv
            available_unitsys_list = elem.getUnitSystems(field)
            if 'phy' in available_unitsys_list:
                unitsys_id = unitsys_id_phy
                unitconv_toraw_id, unitconv_fromraw_id = \
                    self.db.get_unitconv_toraw_fromraw_ids(
                        uc_dict, dst_unitsys='phy',
                        dst_unitsys_id=unitsys_id_phy,
                        src_unitsymb=elem.getUnit(field, unitsys=None),
                        dst_unitsymb=elem.getUnit(field, unitsys='phy'),
                        append_new=True)
            else:
                unitsys_id = unitsys_id_raw # no unit conversion
                unitconv_toraw_id, unitconv_fromraw_id = \
                    self.db.get_unitconv_toraw_fromraw_ids(
                        uc_dict, dst_unitsys=None,
                        dst_unitsys_id=unitsys_id_raw,
                        src_unitsymb=elem.getUnit(field, unitsys=None),
                        dst_unitsymb=elem.getUnit(field, unitsys=None),
                        append_new=True)

            channel_id = self.db.get_channel_id(
                pvsp_id, pvrb_id, unitsys_id, channel_name_id,
                unitconv_toraw_id, unitconv_fromraw_id,
                aphla_ch_id=aphla_ch_id, append_new=True)
            if channel_id is None:
                msg = QMessageBox()
                msg.setText(('The channel could neither be found or created '
                             'for the following PVs:'))
                msg.setInformativeText(
                    'Setpoint PV: "{0:s}"\nReadback PV: "{1:s}"'.format(
                        pvsp, pvrb))
                msg.exec_()
                return
            channel_ids.append(channel_id)
            pvsp_ids.append(pvsp_id)

        n_channels = len(channel_ids)
        if channel_group_info == {}:
            group_name_list = channel_names
            group_name_ids = [
                self.db.getMatchingPrimaryKeyIdFrom2ColTable(
                    'group_name_table', 'group_name_id', 'group_name',
                    group_name, append_new=True)
                for group_name in group_name_list]
            weights = [float('nan')]*n_channels
        else:
            group_name = channel_group_info['name']
            if group_name == '':
                group_name_list = channel_names
                group_name_ids = [
                    self.db.getMatchingPrimaryKeyIdFrom2ColTable(
                        'group_name_table', 'group_name_id', 'group_name',
                        group_name, append_new=True)
                    for group_name in group_name_list]
            else:
                group_name_id = self.db.getMatchingPrimaryKeyIdFrom2ColTable(
                    'group_name_table', 'group_name_id', 'group_name',
                    group_name, append_new=True)
                group_name_ids = [group_name_id]*n_channels

            weights = [channel_group_info['weight']]*n_channels

        self.abstract.group_name_ids.extend(group_name_ids)
        self.abstract.channel_ids.extend(channel_ids)
        self.abstract.weights.extend(weights)

        self.table.updateModel()
        self.table.repaint()

########################################################################
class View(QDialog, Ui_Dialog):
    """"""

    #----------------------------------------------------------------------
    def __init__(self, model, isModal, parentWindow, settings=None):
        """Constructor"""

        QDialog.__init__(self, parent=parentWindow)

        # Load Startup Preferences
        self.default_pref = dict(
            vis_col_key_list=config.DEF_VIS_COL_KEYS['config_setup'][:])
        if osp.exists(PREF_JSON_FILEPATH):
            with open(PREF_JSON_FILEPATH, 'r') as f:
                pref = json.load(f)
        else:
            pref = self.default_pref

        (col_keys, col_names) = config.COL_DEF.getColumnDataFromTable(
            'column_table',
            column_name_list=['column_key','short_descrip_name'],
            condition_str='column_key in ({0:s})'.format(
                ','.join(['"{0:s}"'.format(k)
                          for k in pref['vis_col_key_list']]
                         )
            )
        )
        self.vis_col_name_list = [col_names[col_keys.index(k)]
                                  for k in pref['vis_col_key_list']]

        self.setupUi(self)

        self.widget_configDBView.deleteLater()
        self.configDBView = ConfigDBViewWidget(self.layoutWidget,
                                               self.gridLayout_configDBView)

        self.tableView = self.configDBView.tableView
        self.treeView  = self.configDBView.treeView

        self.msg = None

        self.setWindowFlags(Qt.Window) # To add Maximize & Minimize buttons
        self.setModal(isModal)

        self.settings = settings
        self.settings.loadViewSizeSettings(self)

        self.model = model

        self.lineEdit_ref_step_size.setText(
            str(self.model.abstract.ref_step_size))

        self.table_proxyModel = QSortFilterProxyModel()
        self.table_proxyModel.setSourceModel(self.model.table)
        self.table_proxyModel.setDynamicSortFilter(False)
        #
        #self.tree_proxyModel = QSortFilterProxyModel()
        #self.tree_proxyModel.setSourceModel(self.model.tree)
        #self.tree_proxyModel.setDynamicSortFilter(False)

        t = self.tableView
        # Model setup
        t.setModel(self.table_proxyModel)
        # Selection setup
        t.setSelectionModel(QItemSelectionModel(self.table_proxyModel))
        t.setSelectionMode(QAbstractItemView.ExtendedSelection)
        t.setSelectionBehavior(QAbstractItemView.SelectItems)
        # View setup
        t.setCornerButtonEnabled(True)
        t.setShowGrid(True)
        t.setAlternatingRowColors(True)
        t.setSortingEnabled(False)
        # Header setup
        horizHeader = t.horizontalHeader()
        horizHeader.setSortIndicatorShown(False)
        horizHeader.setStretchLastSection(False)
        horizHeader.setMovable(False)
        #
        #t = self.treeView
        #t.setModel(self.tree_proxyModel)
        #t.setItemsExpandable(True)
        #t.setRootIsDecorated(True)
        #t.setAllColumnsShowFocus(False)
        #t.setHeaderHidden(False)
        #t.setSortingEnabled(False)
        #horizHeader = t.header()
        #horizHeader.setSortIndicatorShown(False)
        #horizHeader.setStretchLastSection(False)
        #horizHeader.setMovable(False)
        #self._expandAll_and_resizeColumn()
        #t.setSelectionMode(QAbstractItemView.ExtendedSelection)

        self.actionGroupChannels = QAction(QIcon(), 'Group channels',
                                           self.treeView)
        self.actionUngroupChannels = QAction(QIcon(), 'Ungroup channels',
                                             self.treeView)
        self.popMenu = QMenu(self.treeView)
        self.popMenu.addAction(self.actionUngroupChannels)
        self.popMenu.addAction(self.actionGroupChannels)

        self.connect(self.treeView,
                     SIGNAL('customContextMenuRequested(const QPoint &)'),
                     self._openContextMenu)
        self.connect(self.actionGroupChannels, SIGNAL('triggered()'),
                     self._groupChannels)
        self.connect(self.actionUngroupChannels, SIGNAL('triggered()'),
                     self._ungroupChannels)

        self.connect(self.pushButton_preferences, SIGNAL('clicked(bool)'),
                     self._launchPrefDialog)

        self.connect(
            self.tableView,
            SIGNAL('dataChanged(const QModelIndex &, const QModelIndex &)'),
            self.on_table_data_change)

        self.configDBView.on_column_selection_change(
            self.vis_col_name_list, force_visibility_update=True)

        self.connect(self.lineEdit_ref_step_size, SIGNAL('editingFinished()'),
                     self.update_ref_step_size)
        self.connect(self.checkBox_synced_group_weight,
                     SIGNAL('stateChanged(int)'),
                     self.update_synced_group_weight)

    #----------------------------------------------------------------------
    def update_synced_group_weight(self, state):
        """"""

        if state == Qt.Checked:
            self.model.abstract.synced_group_weight = True
        else:
            self.model.abstract.synced_group_weight = False

    #----------------------------------------------------------------------
    def update_ref_step_size(self):
        """"""

        try:
            new_ref_step_size = float(self.lineEdit_ref_step_size.text())
        except:
            new_ref_step_size = float('nan')
            self.lineEdit_ref_step_size.setText('nan')

        self.model.table.on_ref_step_size_change(new_ref_step_size)

    ##----------------------------------------------------------------------
    #def relayDataChangedSignal(self, proxyTopLeftIndex, proxyBottomRightIndex):
        #""""""

        #proxyModel = self.tableView.model()

        #QMetaObject.invokeMethod(
            #self.tableView, 'dataChanged', Qt.QueuedConnection,
            #Q_ARG(QModelIndex, proxyModel.mapFromSource(proxyTopLeftIndex)),
            #Q_ARG(QModelIndex, proxyModel.mapFromSource(proxyBottomRightIndex)))

    #----------------------------------------------------------------------
    def on_table_data_change(self, proxyTopLeftIndex, proxyBottomRightIndex):
        """"""

        proxyModel = self.tableView.model()

        proxy_row_i = proxyTopLeftIndex.row()
        proxy_row_f = proxyBottomRightIndex.row()
        proxy_col_i = proxyTopLeftIndex.column()
        proxy_col_f = proxyBottomRightIndex.column()



        topLeft     = proxyModel.mapToSource(proxyTopLeftIndex)
        bottomRight = proxyModel.mapToSource(proxyBottomRightIndex)

        #if

    #----------------------------------------------------------------------
    def saveQSettings(self):
        """"""

        self.settings.saveViewSizeSettings(self)
        self.settings.saveMiscSettings()

    #----------------------------------------------------------------------
    def _launchPrefDialog(self, checked):
        """"""

        dialog = PreferencesEditor(self.default_pref)
        dialog.exec_()

    #----------------------------------------------------------------------
    def closeEvent(self, event):
        """"""

        self.saveQSettings()

        self.model.abstract.channel_ids = []

        event.accept()

    #----------------------------------------------------------------------
    def accept(self):
        """"""

        self.saveQSettings()

        if not self.model.abstract.isDataValid():
            return

        super(View, self).accept() # will close the dialog

    #----------------------------------------------------------------------
    def reject(self):
        """"""

        self.saveQSettings()

        self.model.abstract.channel_ids = []

        super(View, self).reject() # will close the dialog

    #----------------------------------------------------------------------
    def _expandAll_and_resizeColumn(self):
        """"""

        self.treeView.expandAll()
        self.treeView.resizeColumnToContents(0)

    #----------------------------------------------------------------------
    def _groupChannels(self):
        """"""

        print 'Not implemented yet'

    #----------------------------------------------------------------------
    def _ungroupChannels(self):
        """"""

        print 'Not implemented yet'

    #----------------------------------------------------------------------
    def _openContextMenu(self, point):
        """"""

        self.popMenu.exec_(self.treeView.mapToGlobal(point))


########################################################################
class App(QObject):
    """"""

    #----------------------------------------------------------------------
    def __init__(self, isModal, parentWindow, use_cached_lattice=False):
        """Constructor"""

        QObject.__init__(self)

        self.use_cached_lattice = use_cached_lattice

        self.settings = Settings()

        self._initModel()
        self._initView(isModal, parentWindow)

        self.connect(self.view.pushButton_import, SIGNAL('clicked()'),
                     self._importConfigData)
        self.connect(self.view.pushButton_export,
                     SIGNAL('clicked()'), self._exportConfigData)

    #----------------------------------------------------------------------
    def _initModel(self):
        """"""

        self.model = Model()

    #----------------------------------------------------------------------
    def _initView(self, isModal, parentWindow):
        """"""

        self.view = View(self.model, isModal, parentWindow,
                         settings=self.settings)

    #----------------------------------------------------------------------
    def _importConfigData(self):
        """"""

        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)

        import_type = self.view.comboBox_import.currentText()

        if import_type == 'Channel Explorer':
            self._launchChannelExplorer()
        elif import_type == 'Database':
            a = self.model.abstract

            #a.db.getColumnDataFromTable()

            a.name = self.view.lineEdit_config_name.text()
            a.description = self.view.textEdit.toPlainText()
            ref_step_size_str = self.view.lineEdit_ref_step_size.text()
            try:
                a.ref_step_size = float(ref_step_size_str)
            except:
                msg.setText(
                    ('Invalid float representation string for reference step '
                     'size: {:s}').format(ref_step_size_str))
                msg.setIcon(QMessageBox.Critical)
            masar_id_str = self.view.lineEdit_masar_id.text()
            try:
                a.masar_id = int(masar_id_str)
            except:
                a.masar_id = None
            a.synced_group_weight = \
                self.view.checkBox_synced_group_weight.isChecked()

        else:

            all_files_filter_str = 'All files (*)'
            caption = 'Load `aptinker` configuration file from {0:s}'.format(
                import_type)
            filter_str = ';;'.join([FILE_FILTER_DICT[import_type],
                                    all_files_filter_str])
            filepath = QFileDialog.getOpenFileName(
                caption=caption, directory=self.settings._last_directory_path,
                filter=filter_str)

            if not filepath:
                return

            self.settings._last_directory_path = osp.dirname(filepath)

            if import_type == 'Text File':

                msg.setText('This export_type is not implemented yet: {:s}'.
                            format(export_type))
                msg.setIcon(QMessageBox.Critical)
                msg.exec_()
                return

                #m = TunerTextFileManager(load=True, filepath=filepath)
                #m.exec_()
                #if m.selection is not None:
                    #data = m.loadConfigTextFile()
                #else:
                    #return

                #if data is not None:
                    #self.model.importNewChannelsFromTextFile(data)
                #else:
                    #return

            elif import_type == 'HDF5 File':
                msg.setText('This export_type is not implemented yet: {:s}'.
                            format(export_type))
                msg.setIcon(QMessageBox.Critical)
                msg.exec_()
                return

            elif import_type == 'JSON File':
                with open(filepath, 'r') as f:
                    data = json.load(f)

                if data is not None:
                    self.model.importNewChannelsFromJSONFile(data)
                else:
                    return

    #----------------------------------------------------------------------
    def _exportConfigData(self):
        """"""

        if not self.model.abstract.isDataValid():
            return

        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)

        a = self.model.abstract

        a.name = self.view.lineEdit_config_name.text()
        a.description = self.view.textEdit.toPlainText()
        ref_step_size_str = self.view.lineEdit_ref_step_size.text()
        try:
            a.ref_step_size = float(ref_step_size_str)
        except:
            msg.setText(
                ('Invalid float representation string for reference step '
                 'size: {:s}').format(ref_step_size_str))
            msg.setIcon(QMessageBox.Critical)
        masar_id_str = self.view.lineEdit_masar_id.text()
        try:
            a.masar_id = int(masar_id_str)
        except:
            a.masar_id = None
        a.synced_group_weight = \
            self.view.checkBox_synced_group_weight.isChecked()

        export_type = self.view.comboBox_export.currentText()

        if export_type == 'Database':
            a.config_id = a.db.saveConfig(a)
            msg.setText('Config successfully saved to database.')
        else:
            msg.setText('This export_type is not implemented yet: {:s}'.
                        format(export_type))

            #all_files_filter_str = 'All files (*)'
            #caption = 'Save Tuner Configuration to {0:s}'.format(export_type)
            #filter_str = ';;'.join([FILE_FILTER_DICT[export_type],
                                    #all_files_filter_str])
            #save_filepath = QFileDialog.getSaveFileName(
                #caption=caption, directory=self.starting_directory_path,
                #filter=filter_str)
            #if not save_filepath:
                #return

            #self.starting_directory_path = os.path.dirname(save_filepath)

            #if export_type == 'Text File':
                #m = TunerTextFileManager(load=False, filepath=save_filepath)
                #m.exec_()

                #data = self.model.getConfigDataForTextFile(m.selection)

                #m.saveConfigTextFile(data)
            #elif export_type == 'JSON File':
                #self.model.saveConfigToJSON(save_filepath)
            #elif export_type == 'HDF5 File':
                #self.model.saveConfigToHDF5(save_filepath)

            #msgBox.setText('Config successfully saved to {0:s}: {1:s}.'.
                           #format(export_type, save_filepath))

        msg.exec_()

    #----------------------------------------------------------------------
    def _launchChannelExplorer(self):
        """"""

        if not self.use_cached_lattice:
            save_cache = True
        else:
            save_cache = False

        result = channelexplorer.make(
            modal=True, init_object_type='channel',
            can_modify_object_type=False,
            output_type=channelexplorer.TYPE_OBJECT,
            caller='aptinker', use_cached_lattice=self.use_cached_lattice,
            save_lattice_to_cache=save_cache, debug=False)

        self.use_cached_lattice = True # Use cache from 2nd time on to reduce
        # loading time.

        selected_channels = result['dialog_result']

        if selected_channels['selection'] != []:
            channelGroupInfo = self._askChannelGroupNameAndWeight()
            self.model.importNewChannelsFromSelector(selected_channels,
                                                     channelGroupInfo)

    #----------------------------------------------------------------------
    def _launchConfigDBSelector(self):
        """"""


    #----------------------------------------------------------------------
    def _askChannelGroupNameAndWeight(self):
        """"""

        prompt_text = ('Do you want to group the selected channels together?\n' +
                       'If so, enter a text for Channel Name and press OK.\n' +
                       'Otherwise, leave it blank and press OK, \n' +
                       'or just press Cancel.\n\n' +
                       'Group Name:')
        result = QInputDialog.getText(self.view, 'Group Name',
                        prompt_text)
        group_name = str(result[0]).strip(' \t\n\r')

        if group_name:
            channelGroupInfo = {'name':group_name}

            prompt_text = ('Specify the weight factor for this group.\n' +
                           'If Cancel is pressed, the weight factor will be set ' +
                           'to 0, by default.\n\n' +
                           'Group Weight Factor:')
            result = QInputDialog.getDouble(self.view, 'Group Weight',
                            prompt_text, value = 0., decimals = 8)

            if result[1]: # If OK was pressed
                channelGroupInfo['weight'] = result[0]
            else: # If Cancel was pressed
                channelGroupInfo['weight'] = 0.

        else:
            channelGroupInfo = {}

        return channelGroupInfo

#----------------------------------------------------------------------
def get_loaded_ap_machines():
    """"""

    return list(set([ap.machines.getLattice(latname).machine
                     for latname in ap.machines.lattices()]))

#----------------------------------------------------------------------
def make(isModal=True, parentWindow=None, use_cached_lattice=False):
    """"""

    app = App(isModal, parentWindow, use_cached_lattice=use_cached_lattice)

    if isModal:
        app.view.exec_()
    else:
        app.view.show()

    if app.model.abstract.config_id is not None:
        app.model.abstract.update_config_ctime()

    return app

#----------------------------------------------------------------------
def main():
    """"""

    args = sys.argv

    if len(args) == 1:
        use_cached_lattice = False
    elif len(args) == 2:
        if args[1] == '--use-cache':
            use_cached_lattice = True
        else:
            use_cached_lattice = False

    if ap.machines._lat is None:
        ap.machines.load(config.HLA_MACHINE, use_cache=use_cached_lattice)

    # If Qt is to be used (for any GUI) then the cothread library needs to
    # be informed, before any work is done with Qt. Without this line
    # below, the GUI window will not show up and freeze the program.
    cothread.iqt()

    app = make(use_cached_lattice=use_cached_lattice)

    cothread.WaitForQuit()
    print app.model.output


if __name__ == '__main__':
    main()