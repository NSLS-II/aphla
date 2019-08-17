#! /usr/bin/env python
from __future__ import print_function, division, absolute_import

import sip
sip.setapi('QString', 2)
sip.setapi('QVariant', 2)

import sys, os
import os.path as osp
import numpy as np
import time
from subprocess import Popen, PIPE
from collections import OrderedDict
from copy import deepcopy
import json
import h5py

from PyQt4.QtCore import (QObject, Qt, SIGNAL, QAbstractItemModel,
                          QAbstractTableModel, QModelIndex)
from PyQt4.QtGui import (QMessageBox, QFileDialog)

from cothread import Sleep
from cothread.catools import caget, caput, FORMAT_TIME, FORMAT_CTRL
import cothread.catools as catools

import aphla as ap

import config
try:
    from . import (SmartSizedMessageBox, datestr, datestr_ns,
                   date_month_folder_str, date_snapshot_filename_str)
except:
    from aphla.gui.TinkerUtils import (
        SmartSizedMessageBox, datestr, datestr_ns, date_month_folder_str,
        date_snapshot_filename_str)
from aphla.gui.utils.addr import (getIPs, getMACs)
import tinkerdb

#----------------------------------------------------------------------
def getusername():
    """"""

    p = Popen('whoami', stdout=PIPE, stderr=PIPE)
    username, error = p.communicate()

    if error:
        raise OSError('Error for whoami: '+error)
    else:
        return username.strip()

#----------------------------------------------------------------------
def gethostname():
    """"""

    p = Popen('hostname', stdout=PIPE, stderr=PIPE)
    hostname, error = p.communicate()

    if error:
        raise OSError('Error for hostname: '+error)
    else:
        return hostname.strip()

#----------------------------------------------------------------------
def getuserinfo():
    """"""

    ips = getIPs()
    ip_str_list = [ip.str for ip in ips]
    ip_str = ', '.join(ip_str_list)

    macs = getMACs()
    mac_str_list = [mac.str for mac in macs]
    mac_str = ', '.join(mac_str_list)

    return getusername(), gethostname(), ip_str, mac_str

#----------------------------------------------------------------------
def get_contiguous_col_ind_pairs(col_inds):
    """"""

    col_inds = sorted(col_inds)

    contig_tuple_list = []
    left_col = col_inds[0]
    prev_col = left_col
    for c in col_inds[1:]:
        if (c - prev_col) != 1:
            contig_tuple_list.append((left_col, prev_col))
            left_col = c
        prev_col = c

    contig_tuple_list.append((left_col, c))

    return contig_tuple_list

########################################################################
class MetaTableModel(QAbstractTableModel):

    #----------------------------------------------------------------------
    def __init__(self, search_result_dict, metaDBViewWidget):
        """Constructor"""

        QAbstractTableModel.__init__(self)

        self.search_result     = search_result_dict
        self.all_col_keys      = metaDBViewWidget.all_col_keys[:]
        self.col_keys_wo_desc  = metaDBViewWidget.col_keys_wo_desc[:]
        self.col_names_wo_desc = metaDBViewWidget.col_names_wo_desc[:]

        self.nRows = len(self.search_result[self.col_keys_wo_desc[0]])
        self.nCols = len(self.col_keys_wo_desc)

        self.str_formats = [':s']*self.nCols
        for i, k in enumerate(self.col_keys_wo_desc):
            if k.endswith('_id') or k.endswith('_synced_group_weight'):
                self.str_formats[i] = ':d'
            elif k.endswith('_ref_step_size'):
                self.str_formats[i] = ':.6g'
            elif k.endswith('_ctime'):
                self.str_formats[i] = 'timestamp'

    #----------------------------------------------------------------------
    def repaint(self):
        """"""

        self.nRows = len(self.search_result[self.col_keys_wo_desc[0]])
        self.reset() # Inititate repaint

    #----------------------------------------------------------------------
    def rowCount(self, parent=QModelIndex()):
        """"""

        return self.nRows

    #----------------------------------------------------------------------
    def columnCount(self, parent=QModelIndex()):
        """"""

        return self.nCols

    #----------------------------------------------------------------------
    def data(self, index, role=Qt.DisplayRole):
        """"""

        row = index.row()
        col = index.column()

        col_key    = self.col_keys_wo_desc[col]
        str_format = self.str_formats[col]

        if ( not index.isValid() ) or \
           ( not (0 <= row < self.rowCount()) ):
            return None

        if role in (Qt.DisplayRole,):

            col_list = self.search_result[col_key]
            if len(col_list) != 0: value = col_list[row]
            else                 : return 'N/A'

            if value is None:
                return 'None'
            elif value is '':
                return "''"
            elif isinstance(value, (list, tuple, set, np.ndarray)):
                return str(value)
            elif str_format == 'timestamp':
                return datestr(value)
            else:
                return '{{{:s}}}'.format(str_format).format(value)
        else:
            return None

    #----------------------------------------------------------------------
    def setData(self, index, value, role=Qt.EditRole):
        """"""

        return False # No item should be editable

    #----------------------------------------------------------------------
    def headerData(self, section, orientation, role=Qt.DisplayRole):
        """"""

        if role == Qt.TextAlignmentRole:
            if orientation == Qt.Horizontal:
                return int(Qt.AlignLeft|Qt.AlignVCenter)
            else:
                return int(Qt.AlignRight|Qt.AlignVCenter)

        elif role != Qt.DisplayRole:
            return None

        elif orientation == Qt.Horizontal:
            # Horizontal Header display name requested
            return self.col_names_wo_desc[section]

        else: # Vertical Header display name requested
            return int(section+1) # row number

    #----------------------------------------------------------------------
    def flags(self, index):
        """"""

        default_flags = QAbstractTableModel.flags(self, index) # non-editable

        if not index.isValid(): return default_flags

        return default_flags # non-editable

########################################################################
class ConfigAbstractModel(QObject):
    """"""

    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""

        QObject.__init__(self)

        self.config_id           = None
        self.name                = ''
        self.description         = ''
        self.userinfo            = getuserinfo()
        self.masar_id            = None
        self.ref_step_size       = 1.0
        self.synced_group_weight = True
        self.config_ctime        = None

        self.db = tinkerdb.TinkerMainDatabase()

        (self.all_col_keys, self.all_col_names, self.all_str_formats,
         user_editable_list) = config.COL_DEF.getColumnDataFromTable(
             'column_table',
             column_name_list=['column_key', 'short_descrip_name',
                               'str_format', 'user_editable_in_conf_setup'],
             condition_str='only_for_ss=0')

        self.all_str_formats = [f if f is not None else ':s'
                                for f in self.all_str_formats]

        self.visible_col_keys = self.all_col_keys[:]

        self.user_editable = dict(zip(self.all_col_keys,
                                      [True if u == 1 else False
                                       for u in user_editable_list]))

        self.group_name_ids     = []
        self.channel_ids        = []
        self.weights            = []
        self.caput_enabled_rows = []

        self.pvsp_ids = []

    #----------------------------------------------------------------------
    def exportToFile(self, config_id, qsettings=None, auto=False):
        """"""

        if auto:
            save_filepath = 'config_{0:d}.json'.format(config_id)
        else:
            if qsettings:
                last_directory_path = qsettings.last_directory_path
            else:
                last_directory_path = ''
            caption = 'Export configuration to a file'
            selected_filter_str = ('JSON files (*.json)')
            filter_str = ';;'.join([selected_filter_str, 'All files (*)'])
            save_filepath = QFileDialog.getSaveFileName(
                caption=caption, directory=last_directory_path, filter=filter_str)

            if not save_filepath:
                return

            qsettings.last_directory_path = osp.dirname(save_filepath)

        d = {}

        d['config_id'] = config_id

        if '[config_meta_table text view]' \
           not in self.db.getViewNames(square_brackets=True):
            self.db.create_temp_config_meta_table_text_view()

        ((d['config_name'],), (d['config_description'],), (d['username'],),
         (d['config_masar_id'],), (d['config_ref_step_size'],),
         (d['config_synced_group_weight'],), (config_ctime,)) = \
            self.db.getColumnDataFromTable(
                '[config_meta_table text view]',
                column_name_list=['config_name', 'config_description', 'username',
                                  'config_masar_id', 'config_ref_step_size',
                                  'config_synced_group_weight', 'config_ctime'],
                condition_str='config_id={0:d}'.format(config_id))

        d['config_ctime'] = datestr(config_ctime)

        if '[config_table text view]' \
           not in self.db.getViewNames(square_brackets=True):
            self.db.create_temp_config_table_text_view()

        out = self.db.getColumnDataFromTable(
            '[config_table text view]',
            column_name_list=[
                'group_name', 'channel_name', 'weight', 'caput_enabled',
                'pvsp', 'pvrb',
                'machine_name', 'lattice_name', 'elem_name', 'field', # related to APHLA channel
                'unitsys', 'unitconv_type', 'polarity', 'unitsymb',
                'unitsymb_raw', 'unitconv_blob_toraw', 'unitconv_blob_fromraw',
                'unitconv_inv_toraw', 'unitconv_inv_fromraw'],
            condition_str='config_id={0:d}'.format(config_id))

        unitconv_dict = {}
        d['channels'] = []
        for i, (group_name, channel_name, weight, caput_enabled, pvsp, pvrb,
                machine_name, lattice_name, elem_name, field,
                unitsys, unitconv_type, polarity, unitsymb, unitsymb_raw,
                unitconv_blob_toraw, unitconv_blob_fromraw, unitconv_inv_toraw,
                unitconv_inv_fromraw) in enumerate(zip(*out)):

            if unitconv_type in ('poly', 'interp1'):
                conv_data_fromraw = tinkerdb.blobloads(unitconv_blob_fromraw)
                conv_data_toraw   = tinkerdb.blobloads(unitconv_blob_toraw)
            elif unitconv_type == 'NoConversion':
                conv_data_fromraw = conv_data_toraw = None
            else:
                raise ValueError('Unexpected unitconv_type: {0}'.format(
                    unitconv_type))

            unitconv_key = 'ch{0:d}'.format(i)
            unitconv_dict[unitconv_key] = [
                dict(type=unitconv_type, polarity=polarity, src_unitsys=None,
                     dst_unitsys=unitsys, src_unitsymb=unitsymb_raw,
                     dst_unitsymb=unitsymb, inv=unitconv_inv_fromraw,
                     conv_data=conv_data_fromraw),
                dict(type=unitconv_type, polarity=polarity, src_unitsys=unitsys,
                     dst_unitsys=None, src_unitsymb=unitsymb,
                     dst_unitsymb=unitsymb_raw, inv=unitconv_inv_toraw,
                     conv_data=conv_data_toraw)]

            if machine_name is not None:
                aphla_channel_name = '.'.join([machine_name, lattice_name,
                                               elem_name, field])
            else:
                aphla_channel_name = None

            d['channels'].append([group_name, channel_name, weight,
                                  caput_enabled, pvsp, pvrb, aphla_channel_name,
                                  unitsys, unitconv_key])

        # Only keep unique elements in unitconv_dict
        key_inds_for_unique_elements = []
        keys_to_be_checked = unitconv_dict.keys()[::-1]
        while keys_to_be_checked != []:
            k = keys_to_be_checked.pop()
            temp_keys = [k]
            for kk in keys_to_be_checked:
                if unitconv_dict[k] == unitconv_dict[kk]:
                    temp_keys.append(kk)
            for kk in temp_keys[1:]:
                keys_to_be_checked.remove(kk)
                del unitconv_dict[kk]
            key_inds_for_unique_elements.append([int(k[2:]) for k in temp_keys])
        for key_inds in key_inds_for_unique_elements:
            k = 'ch{0:d}'.format(key_inds[0])
            for ind in key_inds[1:]:
                d['channels'][ind][-1] = k
        #
        d['unitconv_dict'] = unitconv_dict

        d['column_names'] = [
            'group_name', 'channel_name', 'config_weight',
            'config_caput_enabled', 'pvsp', 'pvrb', 'aphla_channel_name',
            'unitsys', 'unitconv_key']

        orig_float_repr = json.encoder.FLOAT_REPR
        json.encoder.FLOAT_REPR = lambda f: (
            '%{0}'.format(tinkerdb.UNITCONV_DATA_PRECISION) % f)
        with open(save_filepath, 'w') as f:
            json.dump(d, f, indent=2, sort_keys=True, separators=(',', ': '))
        json.encoder.FLOAT_REPR = orig_float_repr

        return save_filepath

    #----------------------------------------------------------------------
    def isDataValid(self):
        """"""

        if self.channel_ids == []:
            msg = QMessageBox()
            msg.setText('No channels specified.')
            msg.exec_()
            return False

        dup_ch_info_list = self.check_duplicate_channel_ids()
        if dup_ch_info_list != []:
            self.msg = SmartSizedMessageBox()
            self.msg.setText(
                'Duplicate channels are NOT allowed in aptinker config.')
            template = '{0:>7}  : {1:<23}: {2:<27}: {3:<27}: {4:^12}'
            header = (
                '(Ch. ID) :       (Ch. Name)       :           (PVSP)           :'
                '           (PVRB)           : (UnitSystem)')
            self.msg.setDetailedText('\n'.join(
                [header] + [template.format(ch_id, ch_name, pvsp, pvrb, unitsys)
                            for ch_id, pvsp, pvrb, unitsys, ch_name
                            in zip(*dup_ch_info_list)]))
            self.msg.exec_()
            return False

        dup_pvsp_names = self.check_duplicate_pvsp()
        if dup_pvsp_names != []:
            dup_pvsp_names.sort()
            msg = QMessageBox()
            msg.setText(
                'Duplicate setpoint PVs are NOT allowed in aptinker config.')
            msg.setDetailedText('\n'.join(['Duplicate Setpoint PVs:']+
                                          dup_pvsp_names))
            msg.exec_()
            return False

        return True

    #----------------------------------------------------------------------
    def check_aphla_unitconv_updates(self):
        """
        Return True if it is ready to proceed for loading this config.
        Return False otherwise.
        """

        uc_changes = self.get_aphla_unitconv_data_changes()
        if uc_changes != []:
            msg = QMessageBox()
            msg.setText('Unit conversion data associated with APHLA elements '
                        'have changed compared to the data when this '
                        'configuration was saved.\n\nDo you want to save a new '
                        'configuration with the latest unit conversion data '
                        'and load this newly saved configuration?\n\nIf No is '
                        'selected, then it will load the configuration with the '
                        'old unit conversion.\n\nIf Cancel is selected, '
                        'configuration loading will be cancelled.')
            msg.addButton(QMessageBox.Yes)
            msg.addButton(QMessageBox.No)
            msg.addButton(QMessageBox.Cancel)
            msg.setDefaultButton(QMessageBox.Yes)
            msg.setEscapeButton(QMessageBox.Cancel)
            msg.setIcon(QMessageBox.Question)
            choice = msg.exec_()
            if choice == QMessageBox.Cancel:
                return False
            elif choice == QMessageBox.No:
                # Load the config as is (i.e., using old unit conversion)
                pass
            else:
                # get_aphla_unitconv_data_changes() should have already added
                # the new unit conversions to unitconv_table. So, it's just
                # a matter of replacing old channel_id's with new channel_id's
                (pvsp_ids, pvrb_ids, unitsys_ids, channel_name_ids,
                 aphla_ch_ids) = self.db.getMatchedColumnDataFromTable(
                     'channel_table', 'channel_id',
                     [self.channel_ids[row] for row, _, _ in uc_changes], ':d',
                     column_name_return_list=['pvsp_id', 'pvrb_id', 'unitsys_id',
                                              'channel_name_id', 'aphla_ch_id'])
                for (pvsp_id, pvrb_id, unitsys_id, channel_name_id, aphla_ch_id,
                     (row, new_uc_toraw_id, new_uc_fromraw_id)) in \
                    zip(pvsp_ids, pvrb_ids, unitsys_ids, channel_name_ids,
                        aphla_ch_ids, uc_changes):

                    new_channel_id, = self.db.get_channel_id(
                        pvsp_id, pvrb_id, unitsys_id, channel_name_id,
                        new_uc_toraw_id, new_uc_fromraw_id,
                        aphla_ch_id=aphla_ch_id, append_new=True)

                    self.channel_ids[row] = new_channel_id

                self.db.saveConfig(self)

        return True

    #----------------------------------------------------------------------
    def get_aphla_unitconv_data_changes(self):
        """"""

        unitconv_changes = []

        table_name = '[aphla channel prop text view]'
        if table_name not in self.db.getViewNames(square_brackets=True):
            self.db.create_temp_aphla_channel_prop_text_view()
        elem_names, fields = self.db.getMatchedColumnDataFromTable(
            table_name, 'channel_id', self.channel_ids, ':d',
            column_name_return_list=['elem_name', 'field'])
        elems = ap.getElements(elem_names)

        old_unitconv_fromraw_ids, old_unitconv_toraw_ids = \
            self.db.getMatchedColumnDataFromTable(
                'channel_table', 'channel_id', self.channel_ids, ':d',
                column_name_return_list=['unitconv_fromraw_id',
                                         'unitconv_toraw_id'])

        table_name = '[unitconv_table text view]'
        if table_name not in self.db.getViewNames(square_brackets=True):
            self.db.create_temp_unitconv_table_text_view()
        dst_unitsyses, dst_unitsys_ids, src_unitsymbs, dst_unitsymbs = \
            self.db.getMatchedColumnDataFromTable(
                table_name, 'unitconv_id', old_unitconv_fromraw_ids, ':d',
                column_name_return_list=['dst_unitsys', 'dst_unitsys_id',
                                         'src_unitsymb', 'dst_unitsymb'])

        for i, (elem, field, old_unitconv_fromraw_id, old_unitconv_toraw_id,
                dst_unitsys, dst_unitsys_id, src_unitsymb, dst_unitsymb) in \
            enumerate(zip(elems, fields, old_unitconv_fromraw_ids,
                          old_unitconv_toraw_ids, dst_unitsyses,
                          dst_unitsys_ids, src_unitsymbs, dst_unitsymbs)):

            if elem is None:
                continue

            uc_dict = elem._field[field].unitconv

            latest_unitconv_toraw_id, latest_unitconv_fromraw_id = \
                self.db.get_unitconv_toraw_fromraw_ids(
                    uc_dict, dst_unitsys=dst_unitsys,
                    dst_unitsys_id=dst_unitsys_id, src_unitsymb=src_unitsymb,
                    dst_unitsymb=dst_unitsymb, append_new=True)

            if (old_unitconv_fromraw_id != latest_unitconv_fromraw_id) or \
               (old_unitconv_toraw_id != latest_unitconv_toraw_id):
                unitconv_changes.append([i, latest_unitconv_toraw_id,
                                         latest_unitconv_fromraw_id])

        return unitconv_changes

    #----------------------------------------------------------------------
    def check_duplicate_channel_ids(self):
        """
        Duplicate channels are not allowed in aptinker.
        """

        if len(self.channel_ids) != len(set(self.channel_ids)):
            dup_ch_ids = [ch_id for ch_id in set(self.channel_ids)
                          if self.channel_ids.count(ch_id) != 1]

            if '[channel_table text view]' not in self.db.getViewNames():
                self.db.create_temp_channel_table_text_view()

            dup_ch_infos = self.db.getColumnDataFromTable(
                '[channel_table text view]',
                column_name_list=['channel_id', 'pvsp', 'pvrb', 'unitsys',
                                  'channel_name'],
                condition_str='channel_id in ({0:s})'.format(
                    ','.join([str(i) for i in dup_ch_ids])))
        else:
            dup_ch_infos = []

        return dup_ch_infos

    #----------------------------------------------------------------------
    def check_duplicate_pvsp(self):
        """
        Duplicate setpoint PV's are not allowed in aptinker, though
        duplicate readback PV's are allowed.

        The only exception is the non-specified PV (i.e., empty PV string),
        whose database ID (pv_id) is 1.
        """

        self.pvsp_ids = []
        for ch_id in self.channel_ids:
            self.pvsp_ids.append(
                self.db.getColumnDataFromTable(
                    'channel_table', column_name_list=['pvsp_id'],
                    condition_str='channel_id={0:d}'.format(ch_id))[0][0]
            )

        # Removing the non-specified PV from the PV ID list, since multiple
        # non-specified PVs are allowed.
        pvsp_ids_wo_nonspec = [i for i in self.pvsp_ids
                               if i != tinkerdb.pv_id_NonSpecified]

        if len(pvsp_ids_wo_nonspec) != len(set(pvsp_ids_wo_nonspec)):
            dup_pv_names = [
                self.db.getColumnDataFromTable(
                    'pv_table', column_name_list=['pv'],
                    condition_str='pv_id={0:d}'.format(pvsp_id))[0][0]
                for pvsp_id in set(pvsp_ids_wo_nonspec)
                if pvsp_ids_wo_nonspec.count(pvsp_id) != 1]
        else:
            dup_pv_names = []

        return dup_pv_names

    #----------------------------------------------------------------------
    def update_config_ctime(self):
        """"""

        if self.config_id is not None:
            self.config_ctime = self.db.getColumnDataFromTable(
                'config_meta_table', column_name_list=['config_ctime'],
                condition_str='config_id={0:d}'.format(self.config_id))[0][0]

    #----------------------------------------------------------------------
    def modify_data(self, new_val, col_ind, row_inds):
        """"""

        col_key = self.all_col_keys[col_ind]

        if self.synced_group_weight:
            group_ids = set(self.group_name_ids[r] for r in row_inds)

        if col_key == 'weight':
            if self.synced_group_weight:
                synced_row_inds = []
                for gid in group_ids:
                    synced_row_inds.extend([
                        r for r, i in enumerate(self.group_name_ids)
                        if (i == gid)])
                row_inds = set(row_inds + synced_row_inds)

            for r in row_inds:
                self.weights[r] = new_val
        elif col_key == 'step_size':
            if (self.ref_step_size == 0.0) or (np.isnan(self.ref_step_size)):
                raise ValueError('You should not be able to reach here.')
            else:
                if self.synced_group_weight:
                    synced_row_inds = []
                    for gid in group_ids:
                        synced_row_inds.extend([
                            r for r, i in enumerate(self.group_name_ids)
                            if (i == gid)])
                    row_inds = set(row_inds + synced_row_inds)

                for r in row_inds:
                    self.weights[r] = new_val / self.ref_step_size
        elif col_key == 'unitsys':
            new_unitsys_id = self.db.getMatchingPrimaryKeyIdFrom2ColTable(
                'unitsys_table', 'unitsys_id', 'unitsys', new_val,
                append_new=True)
            for r in row_inds:
                self.on_unitsys_change(r, new_unitsys_id)

        elif col_key == 'group_name':
            group_name_id = self.db.getMatchingPrimaryKeyIdFrom2ColTable(
                'group_name_table', 'group_name_id', 'group_name', new_val,
                append_new=True)
            for r in row_inds:
                self.group_name_ids[r] = group_name_id

            if self.synced_group_weight:
                sample_weight = self.weights[row_inds[0]]
                synced_row_inds = [
                    r for r, i in enumerate(self.group_name_ids)
                    if (i == group_name_id)]
                for r in synced_row_inds:
                    self.weights[r] = sample_weight

        elif col_key == 'channel_name':

            new_channel_name_id = self.db.getMatchingPrimaryKeyIdFrom2ColTable(
                'channel_name_table', 'channel_name_id', 'channel_name',
                new_val, append_new=True)

            for r in row_inds:
                current_channel_id = self.channel_ids[r]

                ((pvsp_id,), (pvrb_id,), (channel_name_id,), (unitsys_id,),
                 (unitconv_toraw_id,), (unitconv_fromraw_id,),
                 (aphla_ch_id,)) = self.db.getColumnDataFromTable(
                     'channel_table',
                     column_name_list=[
                         'pvsp_id', 'pvrb_id', 'channel_name_id', 'unitsys_id',
                         'unitconv_toraw_id', 'unitconv_fromraw_id',
                         'aphla_ch_id'],
                     condition_str='channel_id={0:d}'.format(current_channel_id))

                new_channel_id = self.db.get_channel_id(
                    pvsp_id, pvrb_id, unitsys_id, new_channel_name_id,
                    unitconv_toraw_id, unitconv_fromraw_id,
                    aphla_ch_id=aphla_ch_id, append_new=True)

                self.channel_ids[r] = new_channel_id

        elif col_key == 'pvsp':

            if len(row_inds) != 1:
                raise ValueError('No duplicate setpoint PVs allowed.')
            else:
                r = row_inds[0]

            readonly = False
            new_pvsp_id = self.db.get_pv_id(new_val, readonly, append_new=True)

            if new_pvsp_id in (-1, -2):
                # Non-exising or disconnected PV for -1
                # Unacceptable PV data type for -2
                return

            current_channel_id = self.channel_ids[r]

            ((pvsp_id,), (pvrb_id,), (channel_name_id,), (unitsys_id,),
             (unitconv_toraw_id,), (unitconv_fromraw_id,),
             (aphla_ch_id,)) = self.db.getColumnDataFromTable(
                 'channel_table',
                 column_name_list=[
                     'pvsp_id', 'pvrb_id', 'channel_name_id', 'unitsys_id',
                     'unitconv_toraw_id', 'unitconv_fromraw_id',
                     'aphla_ch_id'],
                 condition_str='channel_id={0:d}'.format(current_channel_id))

            new_channel_id = self.db.get_channel_id(
                new_pvsp_id, pvrb_id, unitsys_id, channel_name_id,
                unitconv_toraw_id, unitconv_fromraw_id,
                aphla_ch_id=aphla_ch_id, append_new=True)

            self.channel_ids[r] = new_channel_id

        elif col_key == 'pvrb':

            readonly = True
            new_pvrb_id = self.db.get_pv_id(new_val, readonly, append_new=True)

            if new_pvrb_id in (-1, -2):
                # Non-exising or disconnected PV for -1
                # Unacceptable PV data type for -2
                return

            for r in row_inds:
                current_channel_id = self.channel_ids[r]

                ((pvsp_id,), (pvrb_id,), (channel_name_id,), (unitsys_id,),
                 (unitconv_toraw_id,), (unitconv_fromraw_id,),
                 (aphla_ch_id,)) = self.db.getColumnDataFromTable(
                     'channel_table',
                     column_name_list=[
                         'pvsp_id', 'pvrb_id', 'channel_name_id', 'unitsys_id',
                         'unitconv_toraw_id', 'unitconv_fromraw_id',
                         'aphla_ch_id'],
                     condition_str='channel_id={0:d}'.format(current_channel_id))

                new_channel_id = self.db.get_channel_id(
                    pvsp_id, new_pvrb_id, unitsys_id, channel_name_id,
                    unitconv_toraw_id, unitconv_fromraw_id,
                    aphla_ch_id=aphla_ch_id, append_new=True)

                self.channel_ids[r] = new_channel_id

        elif col_key == 'caput_enabled':
            for r in row_inds:
                self.caput_enabled_rows[r] = new_val

        else:
            raise ValueError('Unexpected col_key: {0:s}'.format(col_key))

    #----------------------------------------------------------------------
    def on_unitsys_change(self, row_ind, new_unitsys_id):
        """"""

        current_channel_id = self.channel_ids[row_ind]

        ((pvsp_id,), (pvrb_id,), (channel_name_id,), (unitsys_id,),
         (unitconv_toraw_id,), (unitconv_fromraw_id,),
         (aphla_ch_id,)) = self.db.getColumnDataFromTable(
            'channel_table',
            column_name_list=[
                'pvsp_id', 'pvrb_id', 'channel_name_id', 'unitsys_id',
                'unitconv_toraw_id', 'unitconv_fromraw_id',
                'aphla_ch_id'],
            condition_str='channel_id={0:d}'.format(current_channel_id))

        new_channel_id = self.db.get_channel_id(
            pvsp_id, pvrb_id, new_unitsys_id, channel_name_id,
            unitconv_toraw_id, unitconv_fromraw_id,
            aphla_ch_id=aphla_ch_id, append_new=True)

        self.channel_ids[row_ind] = new_channel_id

########################################################################
class ConfigTableModel(QAbstractTableModel):
    """"""

    #----------------------------------------------------------------------
    def __init__(self, abstract_model=None, readonly=False):
        """Constructor"""

        QAbstractTableModel.__init__(self)

        if abstract_model is None:
            self.abstract = ConfigAbstractModel()
        else:
            self.abstract = abstract_model

        self.readonly = readonly

        # Short-hand notation
        self.db = self.abstract.db

        if '[unitconv_table text view]' not in self.db.getViewNames():
            self.db.create_temp_unitconv_table_text_view()

        self.static_col_keys = config.COL_DEF.getColumnDataFromTable(
            'column_table', column_name_list=['column_key'],
            condition_str='static_in_conf_setup=1')[0]

        self.d = OrderedDict()
        for k in self.abstract.all_col_keys:
            self.d[k] = []

        self.connect(
            self,
            SIGNAL('dataChanged(const QModelIndex &, const QModelIndex &)'),
            self.propagate_change_to_abstract)

    #----------------------------------------------------------------------
    def propagate_change_to_abstract(self, topLeftIndex, bottomRightIndex):
        """"""

        col_left_index  = topLeftIndex.column()
        col_right_index = bottomRightIndex.column()
        row_top_index    = topLeftIndex.row()
        row_bottom_index = bottomRightIndex.row()

        if ((col_left_index == col_right_index) and
            (self.abstract.all_col_keys[col_left_index] == 'caput_enabled')):
            row_inds = range(row_top_index, row_bottom_index+1)
            if len(row_inds) >= 2:
                raise ValueError('Unexpected number of rows')
        elif ((col_left_index == col_right_index) and
              (row_top_index == row_bottom_index)):
            pass
        else:
            return

        index = topLeftIndex
        row_ind = row_top_index
        col_ind = col_left_index
        col_key = self.abstract.all_col_keys[col_ind]

        if self.abstract.synced_group_weight and \
           (col_key in ('weight', 'step_size', 'group_name')):
            gid = self.abstract.group_name_ids[row_ind]
            synced_row_inds = [
                r for r, i in enumerate(self.abstract.group_name_ids)
                if (i == gid) and (r != row_ind)]

        if col_key == 'weight':
            self.abstract.weights[row_ind] = float(self.data(index))
            if self.abstract.synced_group_weight:
                new_weight = float(self.data(index))
                for r in synced_row_inds:
                    self.abstract.weights[r] = new_weight

        elif col_key == 'step_size':
            if (self.abstract.ref_step_size == 0.0) or \
               (np.isnan(self.abstract.ref_step_size)):
                raise ValueError('You should not be able to reach here.')
            else:
                self.abstract.weights[row_ind] = \
                    float(self.data(index)) / self.abstract.ref_step_size
                if self.abstract.synced_group_weight:
                    new_weight = float(self.data(index)) / \
                        self.abstract.ref_step_size
                    for r in synced_row_inds:
                        self.abstract.weights[r] = new_weight

        elif col_key == 'group_name':
            new_group_name = self.data(index)
            new_group_name_id = self.db.getMatchingPrimaryKeyIdFrom2ColTable(
                'group_name_table', 'group_name_id', 'group_name',
                new_group_name, append_new=True)
            self.abstract.group_name_ids[row_ind] = new_group_name_id
            if self.abstract.synced_group_weight:
                synced_row_inds = [
                    r for r, i in enumerate(self.abstract.group_name_ids)
                    if (i == new_group_name_id) and (r != row_ind)]
                if synced_row_inds != []:
                    self.abstract.weights[row_ind] = \
                        self.abstract.weights[synced_row_inds[0]]

        elif col_key == 'unitsys':
            new_unitsys = self.data(index)
            new_unitsys_id = self.db.getMatchingPrimaryKeyIdFrom2ColTable(
                'unitsys_table', 'unitsys_id', 'unitsys', new_unitsys,
                append_new=True)
            self.abstract.on_unitsys_change(row_ind, new_unitsys_id)

        elif col_key == 'caput_enabled':
            new_val = self.data(self.index(row_ind, col_ind), role=Qt.UserRole)
            self.abstract.modify_data(new_val, col_ind, [row_ind])

        elif col_key in ('channel_name', 'pvsp', 'pvrb'):
            new_val = self.data(self.index(row_ind, col_ind))
            self.abstract.modify_data(new_val, col_ind, [row_ind])

        else:
            raise ValueError('Unexpected col_key: {0}'.format(col_key))

        self.updateModel()
        self.repaint()

    #----------------------------------------------------------------------
    def on_ref_step_size_change(self, new_ref_step_size):
        """"""

        self.abstract.ref_step_size = new_ref_step_size

        self.d['step_size'] = \
            np.array(self.d['weight']) * self.abstract.ref_step_size

        self.updateModel()

        self.repaint()

    #----------------------------------------------------------------------
    def modifyAbstractModel(self, new_val, col_ind, row_inds):
        """"""

        self.abstract.modify_data(new_val, col_ind, row_inds)

        self.updateModel()

        self.repaint()

    #----------------------------------------------------------------------
    def updateModel(self):
        """"""

        if self.abstract.channel_ids == []:
            return

        unique_group_name_ids, unique_group_names = \
            self.db.getColumnDataFromTable(
                'group_name_table',
                column_name_list=['group_name_id', 'group_name'],
                condition_str='group_name_id IN ({0:s})'.format(
                    ','.join([str(i) for i
                              in set(self.abstract.group_name_ids)]))
            )
        id_map = [unique_group_name_ids.index(i)
                  for i in self.abstract.group_name_ids]
        self.d['group_name'] = [unique_group_names[i] for i in id_map]

        if '[channel_table text view]' not in self.db.getViewNames():
            self.db.create_temp_channel_table_text_view()

        unique = {}
        (u_channel_ids, unique['pvsp'], unique['pvrb'],
         unique['pvsp_array_size'], unique['pvrb_array_size'],
         unique['unitsys'], u_unitconv_toraw_ids, u_unitconv_fromraw_ids,
         unique['channel_name']) = self.db.getColumnDataFromTable(
             '[channel_table text view]',
             column_name_list=[
                 'channel_id', 'pvsp', 'pvrb', 'pvsp_array_size',
                 'pvrb_array_size', 'unitsys', 'unitconv_toraw_id',
                 'unitconv_fromraw_id', 'channel_name'],
             condition_str='channel_id IN ({0:s})'.format(
                 ','.join([str(ch_id) for ch_id
                           in set(self.abstract.channel_ids)]))
         )
        id_map = [u_channel_ids.index(i) for i in self.abstract.channel_ids]
        for k, v in unique.items():
            self.d[k] = [v[i] for i in id_map]
        unitconv_toraw_ids   = [u_unitconv_toraw_ids[i]   for i in id_map]
        unitconv_fromraw_ids = [u_unitconv_fromraw_ids[i] for i in id_map]

        if '[aphla channel prop text view]' not in self.db.getViewNames():
            self.db.create_temp_aphla_channel_prop_text_view()

        unique = {}
        (u_channel_ids, unique['field'], unique['machine_name'],
         unique['lattice_name'], unique['elem_name'], unique['elem_family'],
         unique['elem_cell'], unique['elem_devname'], unique['elem_efflen'],
         unique['elem_physlen'], unique['elem_fields'], unique['elem_girder'],
         unique['elem_group'], unique['elem_sb'], unique['elem_se'],
         unique['elem_sequence'], unique['elem_symmetry'], unique['elem_pvs']
         ) = self.db.getColumnDataFromTable(
            '[aphla channel prop text view]',
            column_name_list=[
                'channel_id', 'field', 'machine_name', 'lattice_name',
                'elem_name', 'elem_family', 'elem_cell', 'elem_devname',
                'elem_efflen', 'elem_physlen', 'elem_fields', 'elem_girder',
                'elem_group', 'elem_sb', 'elem_se', 'elem_sequence',
                'elem_symmetry', 'elem_pvs',],
            condition_str='channel_id IN ({0:s})'.format(
                ','.join([str(ch_id) for ch_id in u_channel_ids]))
        )
        id_map = [u_channel_ids.index(i) for i in self.abstract.channel_ids]
        for k, v in unique.items():
            self.d[k] = [v[i] for i in id_map]

        # Change string representation into floats so that these columns
        # can be sortable
        float_keys = ['elem_efflen', 'elem_physlen', 'elem_sb', 'elem_se']
        for k in float_keys:
            self.d[k] = [float(x) if x is not None else np.nan
                         for x in self.d[k]]

        if '[unitconv_table text view]' not in self.db.getViewNames():
            self.db.create_temp_unitconv_table_text_view()

        unitsymb_list              = []
        unitsymb_raw_list          = []
        unitconv_type_list         = []
        polarity_list              = []
        conv_data_txt_fromraw_list = []
        conv_data_txt_toraw_list   = []
        unitconv_inv_toraw_list    = []
        unitconv_inv_fromraw_list  = []
        for unitconv_toraw_id, unitconv_fromraw_id \
            in zip(unitconv_toraw_ids, unitconv_fromraw_ids):
            (unitsymb,), (unitsymb_raw,), (unitconv_type,), \
                (unitconv_blob,), (inv,), (polarity,)= \
                self.db.getColumnDataFromTable(
                    '[unitconv_table text view]',
                    column_name_list=['dst_unitsymb', 'src_unitsymb',
                                      'unitconv_type', 'unitconv_blob',
                                      'inv', 'polarity'],
                    condition_str=('unitconv_id={0:d}'.
                                   format(unitconv_fromraw_id)))

            unitsymb_list.append(unitsymb)
            unitsymb_raw_list.append(unitsymb_raw)
            unitconv_type_list.append(unitconv_type)
            polarity_list.append(polarity)

            conv_data_txt = str(tinkerdb.blobloads(unitconv_blob))
            conv_data_txt_fromraw_list.append(conv_data_txt)
            if inv == 0: inv = 'False'
            else       : inv = 'True'
            unitconv_inv_fromraw_list.append(inv)

            (unitconv_blob,), (inv,) = self.db.getColumnDataFromTable(
                '[unitconv_table text view]',
                column_name_list=['unitconv_blob', 'inv'],
                condition_str=('unitconv_id={0:d}'.
                               format(unitconv_toraw_id)))

            conv_data_txt = str(tinkerdb.blobloads(unitconv_blob))
            conv_data_txt_toraw_list.append(conv_data_txt)
            if inv == 0: inv = 'False'
            else       : inv = 'True'
            unitconv_inv_toraw_list.append(inv)

        self.d['unitsymb']              = unitsymb_list
        self.d['unitsymb_raw']          = unitsymb_raw_list
        self.d['unitconv_type']         = unitconv_type_list
        self.d['unitconv_polarity']     = polarity_list
        self.d['unitconv_data_toraw']   = conv_data_txt_toraw_list
        self.d['unitconv_inv_toraw']    = unitconv_inv_toraw_list
        self.d['unitconv_data_fromraw'] = conv_data_txt_fromraw_list
        self.d['unitconv_inv_fromraw']  = unitconv_inv_fromraw_list

        self.d['weight'] = np.array([w if w is not None else np.nan
                                     for w in self.abstract.weights])
        self.d['step_size'] = self.abstract.ref_step_size * self.d['weight']

        self.d['caput_enabled'] = np.array(self.abstract.caput_enabled_rows)

    #----------------------------------------------------------------------
    def repaint(self):
        """"""

        self.reset() # Inititate repaint

    #----------------------------------------------------------------------
    def rowCount(self, parent=QModelIndex()):
        """"""

        return len(self.abstract.channel_ids)

    #----------------------------------------------------------------------
    def columnCount(self, parent=QModelIndex()):
        """"""

        return len(self.abstract.all_col_keys)

    #----------------------------------------------------------------------
    def data(self, index, role=Qt.DisplayRole):
        """"""

        row = index.row()
        col = index.column()

        col_key    = self.abstract.all_col_keys[col]
        str_format = self.abstract.all_str_formats[col]

        col_list = self.d[col_key]

        if ( not index.isValid() ) or \
           ( not (0 <= row < self.rowCount()) ):
            return None

        if (str_format != 'checkbox') and (role in (Qt.DisplayRole, Qt.EditRole)):
            # ^ Need "EditRole". Otherwise, existing text will disappear
            # when trying to edit.

            if len(col_list) != 0: value = col_list[row]
            else                 : return 'N/A'

            if value is None:
                return 'None'
            elif value is '':
                return "''"
            elif isinstance(value, (list, tuple, set, np.ndarray)):
                return str(value)
            else:
                return '{{{:s}}}'.format(str_format).format(value)

        elif str_format == 'checkbox':

            value = col_list[row]

            if role == Qt.DisplayRole:
                return None
            elif role in (Qt.EditRole, Qt.UserRole):
                if value == 1:
                    return True
                else:
                    return False

        else:
            return None

    #----------------------------------------------------------------------
    def setData(self, index, value, role=Qt.EditRole):
        """"""

        row = index.row()
        col = index.column()

        col_key    = self.abstract.all_col_keys[col]
        str_format = self.abstract.all_str_formats[col]

        if ( not index.isValid() ) or \
           ( not (0 <= row < self.rowCount()) ):

            return False

        elif (col_key in ('channel_name', 'pvsp', 'pvrb')) and \
             (self.d['elem_name'][row] is not None) and \
             (value != self.d[col_key][row]):

            msg = QMessageBox()
            msg.setText('''This property cannot be changed as it is defined by
            the linked aphla element object.
            ''')
            msg.setIcon(QMessageBox.Critical)
            msg.exec_()

            return False

        elif (col_key == 'group_name') and (value == ''):

            msg = QMessageBox()
            msg.setText('''Group name cannot be empty.''')
            msg.setIcon(QMessageBox.Critical)
            msg.exec_()

            return False

        else:
            L = self.d[col_key]

            if (str_format is None) or (str_format in (':s', 'checkbox')):
                L[row] = value
            elif str_format.endswith('g'):
                if value == '':
                    return False
                try:
                    L[row] = float(value)
                except:
                    L[row] = float('nan')
            else:
                raise ValueError('Unexpected str_format: {:s}'.
                                 format(str_format))

            self.emit(
                SIGNAL('dataChanged(const QModelIndex &, const QModelIndex &)'),
                index, index)

            return True

    #----------------------------------------------------------------------
    def headerData(self, section, orientation, role=Qt.DisplayRole):
        """"""

        if role == Qt.TextAlignmentRole:
            if orientation == Qt.Horizontal:
                return int(Qt.AlignLeft|Qt.AlignVCenter)
            else:
                return int(Qt.AlignRight|Qt.AlignVCenter)

        elif role != Qt.DisplayRole:
            return None

        elif orientation == Qt.Horizontal:
            # Horizontal Header display name requested
            return self.abstract.all_col_names[section]

        else: # Vertical Header display name requested
            return int(section+1) # row number

    #----------------------------------------------------------------------
    def flags(self, index):
        """"""

        default_flags = QAbstractTableModel.flags(self, index) # non-editable

        if self.readonly: return default_flags

        if not index.isValid(): return default_flags

        col_key = self.abstract.all_col_keys[index.column()]
        if self.abstract.user_editable[col_key]:
            if (col_key == 'step_size') and \
               ((self.abstract.ref_step_size == 0.0) or \
                np.isnan(self.abstract.ref_step_size)):
                return default_flags
            else:
                self.d[col_key] = list(self.d[col_key])
                # ^ self.d[col_key] may be a tuple. In this case, this column will
                # not be editable. So, it is made sure that self.d[col_key] is a
                # list here.
                return Qt.ItemFlags(default_flags | Qt.ItemIsEditable) # editable
        else:
            return default_flags # non-editable

    #----------------------------------------------------------------------
    def removeRows(self, row, count, parent=QModelIndex()):
        """"""

        row_list = [row+i for i in range(count)]

        self.blockSignals(True)

        try:
            for r in row_list[::-1]:
                self.beginRemoveRows(parent, r, r)
            self.endRemoveRows()
            self.blockSignals(False)
        except:
            self.blockSignals(False)
            return False

        np_array_keys = [k for k, v in self.d.items()
                         if isinstance(v, np.ndarray)]

        for r in row_list[::-1]:
            self.abstract.group_name_ids.pop(r)
            self.abstract.channel_ids.pop(r)
            self.abstract.weights.pop(r)
            self.abstract.caput_enabled_rows.pop(r)

            for k, v in self.d.items():
                if k not in np_array_keys:
                    v.pop(r)

        for k in np_array_keys:
            self.d[k] = np.delete(self.d[k], row_list, axis=0)

        self.repaint()

        return True

########################################################################
class TreeItem(object):
    """
    """

    #----------------------------------------------------------------------
    def __init__(self, data_list, parent=None):
        """Constructor"""

        self.parentItem = parent
        self.itemData = data_list
        self.childItems = []

    #----------------------------------------------------------------------
    def appendChild(self, item):
        """"""

        item.parentItem = self
        self.childItems.append(item)

    #----------------------------------------------------------------------
    def appendChildren(self, item_list):
        """"""

        for item in item_list: item.parentItem = self
        self.childItems.extend(item_list)

    #----------------------------------------------------------------------
    def deleteChildren(self):
        """"""

        self.childItems = []

    #----------------------------------------------------------------------
    def child(self, row):
        """"""

        return self.childItems[row]

    #----------------------------------------------------------------------
    def childCount(self):
        """"""

        return len(self.childItems)

    #----------------------------------------------------------------------
    def row(self):
        """"""

        if self.parentItem is not None:
            return self.parentItem.childItems.index(self)
        else:
            return 0

    #----------------------------------------------------------------------
    def columnCount(self):
        """"""

        return len(const.ALL_PROP_KEYS_CONFIG_SETUP)

    #----------------------------------------------------------------------
    def data(self, column):
        """"""

        try:
            return self.itemData[column]
        except:
            return None

    #----------------------------------------------------------------------
    def parent(self):
        """"""

        return self.parentItem

########################################################################
class TreeModel(QAbstractItemModel):
    """
    """

    #----------------------------------------------------------------------
    def __init__(self, rootDataList=None):
        """Constructor"""

        QAbstractItemModel.__init__(self)

        if rootDataList is None:
            rootDataList = []

        self.rootItem = TreeItem(rootDataList)


    #----------------------------------------------------------------------
    def index(self, row, column, parent):
        """"""

        if not self.hasIndex(row, column, parent):
            return QModelIndex()

        if not parent.isValid():
            parentItem = self.rootItem
        else:
            parentItem = parent.internalPointer()

        childItem = parentItem.child(row)

        if childItem:
            return self.createIndex(row, column, childItem)
        else:
            return QModelIndex()


    #----------------------------------------------------------------------
    def parent(self, index):
        """"""
        if not index.isValid():
            return QModelIndex()

        childItem = index.internalPointer()
        parentItem = childItem.parent()

        if (parentItem == None) or (parentItem == self.rootItem):
            return QModelIndex()
        else:
            # Assuming that only Column 0 has children
            return self.createIndex(parentItem.row(), 0, parentItem)

    #----------------------------------------------------------------------
    def rowCount(self, parent):
        """"""

        # Assuming only Column 0 has children
        if parent.column() > 0:
            return 0

        if not parent.isValid():
            parentItem = self.rootItem
        else:
            parentItem = parent.internalPointer()

        return parentItem.childCount()


    #----------------------------------------------------------------------
    def columnCount(self, parent):
        """"""

        if parent.isValid():
            return parent.internalPointer().columnCount()
        else:
            return self.rootItem.columnCount()

    #----------------------------------------------------------------------
    def data(self, index, role=Qt.DisplayRole):
        """"""

        if not index.isValid():
            return None

        if role != Qt.DisplayRole:
            return None

        item = index.internalPointer()

        return item.data(index.column())

    #----------------------------------------------------------------------
    def flags(self, index):
        """"""

        if not index.isValid():
            return 0

        return (Qt.ItemIsEnabled | Qt.ItemIsSelectable)

    #----------------------------------------------------------------------
    def headerData(self, section, orientation, role=Qt.DisplayRole):
        """"""

        if (orientation == Qt.Horizontal and role == Qt.DisplayRole):
            return self.rootItem.data(section)
        else:
            return None

    #----------------------------------------------------------------------
    def reset(self):
        """"""

        QAbstractItemModel.reset(self)

########################################################################
class ConfigTreeModel(TreeModel):
    """"""

    #----------------------------------------------------------------------
    def __init__(self, all_column_name_list, abstract_model=None):
        """Constructor"""

        TreeModel.__init__(self, all_column_name_list)

        if abstract_model is None:
            self.abstract = ConfigAbstractModel()
        else:
            self.abstract = abstract_model

        self.resetModel()

    #----------------------------------------------------------------------
    def resetModel(self):
        """"""


########################################################################
class SnapshotAbstractModel(QObject):
    """"""

    #----------------------------------------------------------------------
    def __init__(self, config_abstract_model, vis_col_key_list,
                 DB_view=False):
        """Constructor

        Size List:
            self.nRows:
                self._config_abstract.channel_ids
                self.weight_array
                self.step_size_array
                self.caput_enabled_rows

            self.n_caget_pvs:
                self.caget_raws
                self.caget_convs # unit-converted caget data
                self.caget_unitconvs # from-raw unit conversion objects for caput
                self.caget_ioc_ts_tuples
                self.caget_pv_str_list
                self.caget_pv_map_list
                self.caget_pv_size_list

            self.n_caput_pvs:
                self.caput_raws
                self.caput_convs # unit-converted sent caput data
                self.caput_fromraw_unitconvs # from-raw unit conversion objects for caput
                self.caput_toraw_unitconvs # to-raw unit conversion objects for caput
                self.caput_pv_str_list
                self.caput_pv_map_list
                self.caput_pv_size_list
                self.caput_enabled_indexes

        self.maps[column_key] = [({row index in GUI Table},
                                  {corresponding index in caget_pv_map_list
                                                       or caput_pv_map_list})]
                                for the column specified with column_key
        """

        isinstance(config_abstract_model, ConfigAbstractModel)

        QObject.__init__(self)

        self.DB_view = DB_view

        self.caget_timeout = 3.0 # [s]
        self.caput_timeout = 3.0 # [s]

        self.auto_caget_delay_after_caput = 1.0 # [s]

        self._config_abstract = config_abstract_model
        self._config_table = ConfigTableModel(
            abstract_model=config_abstract_model)
        self._config_table.updateModel()

        # Short-hand notation
        _ca = self._config_abstract
        _ct = self._config_table

        self.nRows = len(_ca.channel_ids)

        self.ss_id                = None
        self.config_id            = _ca.config_id
        self.name                 = ''
        self.description          = ''
        self.userinfo             = getuserinfo()
        self.masar_id             = _ca.masar_id
        self.ref_step_size        = _ca.ref_step_size
        self.synced_group_weight  = _ca.synced_group_weight
        self.mult_factor          = 1.0
        self.caget_sent_ts_second = None
        self.caput_sent_ts_second = None
        self.ss_ctime             = None

        self.weight_array        = np.array(_ct.d['weight'])
        self.step_size_array     = self.ref_step_size * self.weight_array
        self.caput_enabled_rows  = _ct.d['caput_enabled']

        self.db = _ca.db

        (self.all_col_keys, self.all_col_names, self.all_str_formats,
         user_editable_list, static_in_ss_list) = \
            config.COL_DEF.getColumnDataFromTable(
                'column_table',
                column_name_list=['column_key', 'short_descrip_name',
                                  'str_format', 'user_editable_in_ss',
                                  'static_in_ss'])

        self.all_str_formats = [f if f is not None else ':s'
                                for f in self.all_str_formats]

        self.visible_col_keys = vis_col_key_list[:]

        self.user_editable = dict(zip(self.all_col_keys,
                                      [True if u == 1 else False
                                       for u in user_editable_list]))

        self.dynamic_col_keys = [
            k for k, static in zip(self.all_col_keys, static_in_ss_list)
            if not static]

        self.ss_only_col_keys = config.COL_DEF.getColumnDataFromTable(
            'column_table', column_name_list=['column_key'],
            condition_str='only_for_ss==1')[0]

        self.col_ids = {}
        for k in self.ss_only_col_keys:
            self.col_ids[k] = self.all_col_keys.index(k)

        # Compile caget list
        self.update_caget_list()

        # Compile caput list
        self.update_caput_list()

        self.update_rb_sp_same_size_rows_list()

        # Dict whose item contains a list of 2-element tuple.
        # The 2-element tuple consists of the row index in the GUI table
        # and the list index of flattened pv list that correspond to the row
        self.maps = {}
        self.update_maps()

        self.caput_not_yet = True

        if not self.DB_view:
            self.init_unitconv()

            self.update_pv_vals()

            self.update_init_pv_vals()

            self.get_lo_hi_lims()

    #----------------------------------------------------------------------
    def update_rb_sp_same_size_rows_list(self):
        """"""

        _ct = self._config_table

        self.rb_sp_same_size_rows = []
        for i, (sp_size, rb_size) in enumerate(zip(
            _ct.d['pvsp_array_size'], _ct.d['pvrb_array_size'])):
            if sp_size == rb_size:
                self.rb_sp_same_size_rows.append(i)

    #----------------------------------------------------------------------
    def update_caget_list(self):
        """"""

        _ct = self._config_table

        outs = zip(*[((i, self.col_ids['cur_SP']), pvsp, array_size)
                     for i, (pvsp, array_size)
                     in enumerate(zip(_ct.d['pvsp'], _ct.d['pvsp_array_size']))
                     if (array_size == 1) and (pvsp != '')])
        if outs != []:
            self.caget_SP_scalar_maps  = list(outs[0])
            self.caget_SP_scalar_strs  = list(outs[1])
            self.caget_SP_scalar_sizes = list(outs[2]) # Should be all 1
        else:
            self.caget_SP_scalar_maps  = []
            self.caget_SP_scalar_strs  = []
            self.caget_SP_scalar_sizes = []

        outs = zip(*[((i, self.col_ids['cur_RB']), pvrb, array_size)
                     for i, (pvrb, array_size)
                     in enumerate(zip(_ct.d['pvrb'], _ct.d['pvrb_array_size']))
                     if (array_size == 1) and (pvrb != '')])
        if outs != []:
            self.caget_RB_scalar_maps = list(outs[0])
            self.caget_RB_scalar_strs = list(outs[1])
            self.caget_RB_scalar_sizes = list(outs[2]) # Should be all 1
        else:
            self.caget_RB_scalar_maps  = []
            self.caget_RB_scalar_strs  = []
            self.caget_RB_scalar_sizes = []

        outs = zip(*[((i, self.col_ids['cur_SP']), pvsp, array_size)
                     for i, (pvsp, array_size)
                     in enumerate(zip(_ct.d['pvsp'], _ct.d['pvsp_array_size']))
                     if (array_size != 1) and (pvsp != '')])
        if outs != []:
            self.caget_SP_array_maps  = list(outs[0])
            self.caget_SP_array_strs  = list(outs[1])
            self.caget_SP_array_sizes = list(outs[2])
        else:
            self.caget_SP_array_maps  = []
            self.caget_SP_array_strs  = []
            self.caget_SP_array_sizes = []

        outs = zip(*[((i, self.col_ids['cur_RB']), pvrb, array_size)
                     for i, (pvrb, array_size)
                     in enumerate(zip(_ct.d['pvrb'], _ct.d['pvrb_array_size']))
                     if (array_size != 1) and (pvrb != '')])
        if outs != []:
            self.caget_RB_array_maps  = list(outs[0])
            self.caget_RB_array_strs  = list(outs[1])
            self.caget_RB_array_sizes = list(outs[2])
        else:
            self.caget_RB_array_maps  = []
            self.caget_RB_array_strs  = []
            self.caget_RB_array_sizes = []

        self.caget_pv_str_list = \
            self.caget_SP_scalar_strs + self.caget_RB_scalar_strs + \
            self.caget_SP_array_strs  + self.caget_RB_array_strs
        self.caget_pv_map_list = \
            self.caget_SP_scalar_maps + self.caget_RB_scalar_maps + \
            self.caget_SP_array_maps  + self.caget_RB_array_maps
        self.caget_pv_size_list = \
            self.caget_SP_scalar_sizes + self.caget_RB_scalar_sizes + \
            self.caget_SP_array_sizes  + self.caget_RB_array_sizes

        #self.caget_pv_dtype_list = np.dtype(
            #[('data'+str(i), np.float64) if size == 1
             #else ('data'+str(i), (np.float64, size))
             #for i, size in enumerate(self.caget_pv_size_list)])

        self.n_caget_pvs = len(self.caget_pv_str_list)

        self.caget_raws  = np.ones(self.n_caget_pvs, dtype=object)*np.nan
        self.caget_convs = np.ones(self.n_caget_pvs, dtype=object)*np.nan
        self.caget_ioc_ts_tuples = np.array([(None,None)]*self.n_caget_pvs)

    #----------------------------------------------------------------------
    def update_caput_list(self):
        """"""

        _ct = self._config_table

        outs = zip(*[((i, self.col_ids['cur_SentSP']), pvsp, array_size)
                     for i, (pvsp, array_size)
                     in enumerate(zip(_ct.d['pvsp'], _ct.d['pvsp_array_size']))
                     if (array_size == 1) and (pvsp != '')])
        if outs != []:
            self.caput_SP_scalar_maps  = list(outs[0])
            self.caput_SP_scalar_strs  = list(outs[1])
            self.caput_SP_scalar_sizes = list(outs[2])
        else:
            self.caput_SP_scalar_maps  = []
            self.caput_SP_scalar_strs  = []
            self.caput_SP_scalar_sizes = []

        outs = zip(*[((i, self.col_ids['cur_SentSP']), pvsp, array_size)
                     for i, (pvsp, array_size)
                     in enumerate(zip(_ct.d['pvsp'], _ct.d['pvsp_array_size']))
                     if (array_size != 1) and (pvsp != '')])
        if outs != []:
            self.caput_SP_array_maps  = list(outs[0])
            self.caput_SP_array_strs  = list(outs[1])
            self.caput_SP_array_sizes = list(outs[2])
        else:
            self.caput_SP_array_maps  = []
            self.caput_SP_array_strs  = []
            self.caput_SP_array_sizes = []

        self.caput_pv_str_list = \
            self.caput_SP_scalar_strs + self.caput_SP_array_strs
        self.caput_pv_map_list = \
            self.caput_SP_scalar_maps + self.caput_SP_array_maps
        self.caput_pv_size_list = \
            self.caput_SP_scalar_sizes + self.caput_SP_array_sizes

        #self.caput_pv_dtype_list = np.dtype(
            #[('data'+str(i), np.float64) if size == 1
             #else ('data'+str(i), (np.float64, size))
             #for i, size in enumerate(self.caput_pv_size_list)])

        self.n_caput_pvs = len(self.caput_pv_str_list)

        self.caput_raws  = np.ones(self.n_caput_pvs, dtype=object)*np.nan
        self.caput_convs = np.ones(self.n_caput_pvs, dtype=object)*np.nan

    #----------------------------------------------------------------------
    def update_maps(self):
        """
        self.maps: Dict whose item contains a list of 2-element tuple.

        The 2-element tuple consists of the row index in the GUI table
        and the list index of flattened pv list that correspond to the row.
        """

        self.maps['cur_SP'] = [
            (row, i) for i, (row, col) in enumerate(self.caget_pv_map_list)
            if col == self.col_ids['cur_SP']]
        self.maps['cur_RB'] = [
            (row, i) for i, (row, col) in enumerate(self.caget_pv_map_list)
            if col == self.col_ids['cur_RB']]
        self.maps['cur_SentSP'] = [
            (row, i) for i, (row, col) in enumerate(self.caput_pv_map_list)
            if col == self.col_ids['cur_SentSP']]
        self.maps['cur_SP_ioc_ts'] = deepcopy(self.maps['cur_SP'])
        self.maps['cur_RB_ioc_ts'] = deepcopy(self.maps['cur_RB'])
        self.maps['cur_ConvSP']    = deepcopy(self.maps['cur_SP'])
        self.maps['cur_ConvRB']    = deepcopy(self.maps['cur_RB'])
        self.maps['cur_ConvSentSP']= deepcopy(self.maps['cur_SentSP'])
        self.maps['ini_SP']        = deepcopy(self.maps['cur_SP'])
        self.maps['ini_SP_ioc_ts'] = deepcopy(self.maps['cur_SP'])
        self.maps['ini_RB']        = deepcopy(self.maps['cur_RB'])
        self.maps['ini_RB_ioc_ts'] = deepcopy(self.maps['cur_RB'])
        self.maps['ini_ConvSP']    = deepcopy(self.maps['ini_SP'])
        self.maps['ini_ConvRB']    = deepcopy(self.maps['ini_RB'])

    #----------------------------------------------------------------------
    def get_unitconv_callable(self, conv_type, conv_inv, polarity, conv_data):
        """"""

        if conv_type == 'NoConversion':
            return lambda val: val
        elif (conv_type == 'poly') and (conv_inv == 0):
            coeffs = list(conv_data)
            return np.poly1d(coeffs)*polarity
        elif (conv_type == 'poly') and (conv_inv == 1):
            a, b = conv_data
            ar, br = polarity/a, -b/a
            return np.poly1d([ar, br])
        elif (conv_type == 'interp1') and (conv_inv == 0):
            xp = list(conv_data[0])
            fp = list(conv_data[1])
            # `xp` is assumed to be monotonically increasing. Otherwise,
            # interpolation will make no sense.
            return lambda x: polarity*np.interp(x, xp, fp,
                                                left=np.nan, right=np.nan)
        elif (conv_type == 'interp1') and (conv_inv == 1):
            xp = list(conv_data[0])
            fp = list(conv_data[1])
            # `xp` is assumed to be monotonically increasing. Otherwise,
            # interpolation will make no sense.
            # `fp` is assumed to be monotonically increasing or decreasing.
            # Otherwise, this interpolation definition is not invertible.
            if np.all(np.diff(fp) > 0.0):
                xp_inv = fp
                fp_inv = xp
            elif np.all(np.diff(fp) < 0.0):
                xp_inv = np.flipud(fp)
                fp_inv = np.flipud(xp)
            return lambda x: np.interp(polarity*x, xp_inv, fp_inv,
                                       left=np.nan, right=np.nan)
        else:
            raise ValueError('Unexpected unit conversion type: {0}'.format(
                conv_type))

    #----------------------------------------------------------------------
    def init_unitconv(self):
        """"""

        channel_ids = self._config_abstract.channel_ids[:]

        unitconv_toraw_ids, unitconv_fromraw_ids = \
            self.db.getMatchedColumnDataFromTable(
                'channel_table', 'channel_id', channel_ids, ':d',
                column_name_return_list=['unitconv_toraw_id',
                                         'unitconv_fromraw_id'])

        if '[unitconv_table text view]' \
           not in self.db.getViewNames(square_brackets=True):
            self.db.create_temp_unitconv_table_text_view()

        ## Initialize unit conversion data for caget

        (fromraw_conv_types, fromraw_unitconv_blobs, fromraw_conv_invs,
         fromraw_polarities) = self.db.getMatchedColumnDataFromTable(
             '[unitconv_table text view]', 'unitconv_id',
             unitconv_fromraw_ids, ':d',
             column_name_return_list=['unitconv_type', 'unitconv_blob',
                                      'inv', 'polarity'])

        fromraw_conv_data = [tinkerdb.blobloads(blob)
                             for blob in fromraw_unitconv_blobs]

        self.caget_unitconvs = [None]*self.n_caget_pvs

        rb_map_row_list = [x[0] for x in self.maps['cur_RB']]
        sp_map_row_list = [x[0] for x in self.maps['cur_SP']]
        for row, (conv_type, conv_data, conv_inv, polarity) in enumerate(zip(
            fromraw_conv_types, fromraw_conv_data, fromraw_conv_invs,
            fromraw_polarities)):

            uc_callable = self.get_unitconv_callable(
                conv_type, conv_inv, polarity, conv_data)

            if row in rb_map_row_list:
                i = self.maps['cur_RB'][rb_map_row_list.index(row)][1]
                self.caget_unitconvs[i] = uc_callable
            if row in sp_map_row_list:
                i = self.maps['cur_SP'][sp_map_row_list.index(row)][1]
                self.caget_unitconvs[i] = uc_callable

        ## Initialize unit conversion data for caput

        (toraw_conv_types, toraw_unitconv_blobs, toraw_conv_invs,
         toraw_polarities) = self.db.getMatchedColumnDataFromTable(
             '[unitconv_table text view]', 'unitconv_id',
             unitconv_toraw_ids, ':d',
             column_name_return_list=['unitconv_type', 'unitconv_blob',
                                      'inv', 'polarity'])

        toraw_conv_data = [tinkerdb.blobloads(blob)
                           for blob in toraw_unitconv_blobs]

        self.caput_toraw_unitconvs   = [None]*self.n_caput_pvs
        self.caput_fromraw_unitconvs = [None]*self.n_caput_pvs

        sp_map_row_list = [x[0] for x in self.maps['cur_SentSP']]

        # First get unit conversion to-raw
        for row, (conv_type, conv_data, conv_inv, polarity) in enumerate(zip(
            toraw_conv_types, toraw_conv_data, toraw_conv_invs,
            toraw_polarities)):

            uc_callable = self.get_unitconv_callable(
                conv_type, conv_inv, polarity, conv_data)

            if row in sp_map_row_list:
                i = self.maps['cur_SentSP'][sp_map_row_list.index(row)][1]
                self.caput_toraw_unitconvs[i] = uc_callable

        # Then get unit conversion from-raw
        for row, (conv_type, conv_data, conv_inv, polarity) in enumerate(zip(
            fromraw_conv_types, fromraw_conv_data, fromraw_conv_invs,
            fromraw_polarities)):

            uc_callable = self.get_unitconv_callable(
                conv_type, conv_inv, polarity, conv_data)

            if row in sp_map_row_list:
                i = self.maps['cur_SentSP'][sp_map_row_list.index(row)][1]
                self.caput_fromraw_unitconvs[i] = uc_callable

    #----------------------------------------------------------------------
    def update_caput_enabled_indexes(self):
        """"""

        self.caput_enabled_indexes = np.array([True]*self.n_caput_pvs)
        for row, index in self.maps['cur_SentSP']:
            self.caput_enabled_indexes[index] = self.caput_enabled_rows[row]

    #----------------------------------------------------------------------
    def get_lo_hi_lims(self):
        """"""

        ca_ctrls = caget(self.caput_pv_str_list, format=FORMAT_CTRL,
                         throw=False, timeout=self.caget_timeout)

        self.lo_lims_raw = np.array([
            c.lower_ctrl_limit if hasattr(c, 'lower_ctrl_limit') else np.nan
            for c in ca_ctrls])
        self.hi_lims_raw = np.array([
            c.upper_ctrl_limit if hasattr(c, 'upper_ctrl_limit') else np.nan
            for c in ca_ctrls])

        self.lo_lims_conv = np.array(
            [uc(r) if uc is not None else r for r, uc
             in zip(self.lo_lims_raw, self.caput_fromraw_unitconvs)])
        self.hi_lims_conv = np.array(
            [uc(r) if uc is not None else r for r, uc
             in zip(self.hi_lims_raw, self.caput_fromraw_unitconvs)])

    #----------------------------------------------------------------------
    def update_pv_vals(self):
        """"""

        self.caget_sent_ts_second = time.time()

        ca_raws = caget(self.caget_pv_str_list, format=FORMAT_TIME,
                        throw=False, timeout=self.caget_timeout)

        tEnd_caget = time.time()

        self.caget_raws = np.array(
            [r if r.ok else (np.nan if size == 1 else np.ones(size)*np.nan)
             for r, size in zip(ca_raws, self.caget_pv_size_list)],
            dtype=object)
        self.caget_convs = np.array(
            [uc(r) if uc is not None else r for r, uc
             in zip(self.caget_raws, self.caget_unitconvs)], dtype=object)

        if self.caget_raws.ndim != 1:
            nRow, nCol = self.caget_raws.shape
            temp = np.zeros(nRow, dtype=object)
            for i in range(nRow):
                temp[i] = self.caget_raws[i,:]
            self.caget_raws = temp
            temp = np.zeros(nRow, dtype=object)
            for i in range(nRow):
                temp[i] = self.caget_convs[i,:]
            self.caget_convs[i,:]

        self.caget_ioc_ts_tuples = np.fromiter(
            (r.raw_stamp if r.ok else (-1,-1) for r in ca_raws),
            dtype=np.dtype([('s',np.int64), ('ns', np.int64)]),
            count=self.n_caget_pvs)

        self.emit(SIGNAL('pvValuesUpdatedInSSAbstract'))

        tEnd_model_view = time.time()

        print('# caget update only took {:.6f} seconds'.format(
            tEnd_caget - self.caget_sent_ts_second))
        print('# caget & model/view update took {:.6f} seconds'.format(
            tEnd_model_view - self.caget_sent_ts_second))

    #----------------------------------------------------------------------
    def get_index_map_get2put(self):
        """"""

        rows_caget, indexes_caget = map(list, zip(*self.maps['cur_SP']))
        rows_caput, indexes_caput = map(list, zip(*self.maps['cur_SentSP']))
        index_map_get2put = [indexes_caput[rows_caput.index(r)]
                             for r in rows_caget]

        return index_map_get2put, indexes_caget

    #----------------------------------------------------------------------
    def get_index_map_put2get(self):
        """"""

        rows_caget, indexes_caget = map(list, zip(*self.maps['cur_SP']))
        rows_caput, indexes_caput = map(list, zip(*self.maps['cur_SentSP']))

        index_map_put2get = [indexes_caget[rows_caget.index(r)]
                             for r in rows_caput]

        return index_map_put2get, indexes_caput

    #----------------------------------------------------------------------
    def update_init_pv_vals(self):
        """"""

        self.caget_ini_raws  = np.copy(self.caget_raws)
        self.caget_ini_convs = np.copy(self.caget_raws)

        self.caput_ini_raws = np.copy(self.caput_raws)
        index_map_get2put, indexes_caget = self.get_index_map_get2put()
        self.caput_ini_raws[index_map_get2put] = \
            self.caget_ini_raws[indexes_caget]

    #----------------------------------------------------------------------
    def update_ss_ctime(self):
        """"""

        if self.ss_id is not None:
            self.ss_ctime = self.db.getColumnDataFromTable(
                'snapshot_meta_table', column_name_list=['ss_ctime'],
                condition_str='ss_id={0:d}'.format(self.ss_id))[0][0]

    #----------------------------------------------------------------------
    def modify_data(self, new_val, col_ind, row_inds):
        """"""

        col_key = self.all_col_keys[col_ind]

        _ca = self._config_abstract

        if self.synced_group_weight:
            group_ids = set(_ca.group_name_ids[r] for r in row_inds)

        if col_key == 'weight':
            if self.synced_group_weight:
                synced_row_inds = []
                for gid in group_ids:
                    synced_row_inds.extend([
                        r for r, i in enumerate(_ca.group_name_ids)
                        if (i == gid)])
                row_inds = set(row_inds + synced_row_inds)

            for r in row_inds:
                self.weight_array[r] = new_val

        elif col_key == 'step_size':
            if (self.ref_step_size == 0.0) or (np.isnan(self.ref_step_size)):
                raise ValueError('You should not be able to reach here.')
            else:
                if self.synced_group_weight:
                    synced_row_inds = []
                    for gid in group_ids:
                        synced_row_inds.extend([
                            r for r, i in enumerate(_ca.group_name_ids)
                            if (i == gid)])
                    row_inds = set(row_inds + synced_row_inds)

                for r in row_inds:
                    self.weight_array[r] = new_val / self.ref_step_size

        elif col_key == 'caput_enabled':
            for r in row_inds:
                self.caput_enabled_rows[r] = new_val

        else:
            raise ValueError('Unexpected col_key: {0:s}'.format(col_key))

    #----------------------------------------------------------------------
    def update_NaNs_in_caput_raws(self):
        """"""

        index_map_get2put, indexes_caget = self.get_index_map_get2put()
        index_map_put2get, indexes_caput = self.get_index_map_put2get()

        if self.caput_not_yet:
            self.caput_raws[index_map_get2put] = self.caget_raws[indexes_caget]
            self.caput_convs = np.array(
                [uc(r) if uc is not None else r for r, uc
                 in zip(self.caput_raws,
                        self.caput_fromraw_unitconvs)],
                dtype=object)
            self.caput_not_yet = False
        else:
            nan_inds = [i for i, r, in enumerate(self.caput_raws)
                        if np.any(np.isnan(
                            r if not isinstance(r, catools.dbr.ca_array)
                            else r.__array__().astype(float)))]
            if nan_inds != []:
                for i in nan_inds:
                    self.caput_raws[i] = self.caget_raws[index_map_put2get[i]]
                    r  = self.caput_raws[i]
                    uc = self.caput_fromraw_unitconvs[i]
                    self.caput_convs[i] = uc(r) if uc is not None else r

        self.caput_convs = self.convert_caput_raws(
            self.caput_raws, self.caput_fromraw_unitconvs)

    #----------------------------------------------------------------------
    def convert_caput_raws(self, caput_raws, caput_fromraw_unitconv_list):
        """"""

        caput_raws = [r if not isinstance(r, catools.dbr.ca_array)
                      else r.__array__().astype(float) for r in caput_raws]

        return np.array(
            [uc(r) if uc is not None else r for r, uc
             in zip(caput_raws, caput_fromraw_unitconv_list)],
            dtype=object)

    #----------------------------------------------------------------------
    def invoke_caput(self):
        """"""

        out = [(i, r) for i, (r, enabled)
               in enumerate(zip(self.caput_raws, self.caput_enabled_indexes))
               if enabled and (not np.any(np.isnan(
                   r if not isinstance(r, catools.dbr.ca_array)
                   else r.__array__().astype(float))))]
        if out != []:
            enabled_indexes, caput_raws = map(list, zip(*out))
            caput_pv_str_list = [pv for i, pv
                                 in enumerate(self.caput_pv_str_list)
                                 if i in enabled_indexes]
            caput_pv_map_list = [m for i, m in enumerate(self.caput_pv_map_list)
                                 if i in enabled_indexes]
        else:
            msg = QMessageBox()
            msg.setText(('All writeable PVs are disabled. '
                         'No caput will be performed.'))
            msg.exec_()
            return

        self.caput_sent_ts_second = time.time()
        caput(caput_pv_str_list, caput_raws, throw=False,
              timeout=self.caput_timeout)

        # Update unit-converted SentSP
        self.caput_convs[enabled_indexes] = self.convert_caput_raws(
            caput_raws, [self.caput_fromraw_unitconvs[i]
                         for i in enabled_indexes])

        if not np.isnan(self.auto_caget_delay_after_caput):
            Sleep(self.auto_caget_delay_after_caput)
            self.update_pv_vals()
        else:
            self.emit(SIGNAL('pvValuesUpdatedInSSAbstract'))

    #----------------------------------------------------------------------
    def step_up(self, positive=True):
        """"""

        self.update_NaNs_in_caput_raws()

        self.update_caput_enabled_indexes()

        #uc_list = list(
            #np.array(self.caput_toraw_unitconvs,
                     #dtype=object)[self.caput_enabled_indexes])
        #
        # TODO: Need to test the following block against real machine
        uc_list = [uc for uc, enabled in zip(self.caput_toraw_unitconvs,
                                             self.caput_enabled_indexes)
                   if enabled]

        current_caput_raws = self.caput_raws[self.caput_enabled_indexes]
        current_caput_raws = np.array(
            [o if not isinstance(o, catools.dbr.ca_array) else o.__array__()
             for o in current_caput_raws],
            dtype=object)
        current_caput_convs = self.caput_convs[self.caput_enabled_indexes]

        enabled = self.caput_enabled_rows.astype(bool)
        converted_step_size_array = self.step_size_array[enabled]
        # Now need to re-sort `converted_step_size_array`
        enabled_rows = np.where(enabled)[0]
        rows, indexes = map(list, zip(*self.maps['cur_SentSP']))
        enabled_indexes = [rows.index(r) for r in enabled_rows]
        converted_step_size_array = converted_step_size_array[
            np.argsort(enabled_indexes)]

        if positive:
            new_caput_convs = current_caput_convs + converted_step_size_array
        else:
            new_caput_convs = current_caput_convs - converted_step_size_array
        new_caput_raws = np.array(
            [uc(caput_conv) if uc is not None else caput_conv
             for (caput_conv, uc) in zip(new_caput_convs, uc_list)],
            dtype=object)
        if new_caput_raws.ndim != 1:
            nRow, nCol = new_caput_raws.shape
            temp = np.zeros(nRow, dtype=object)
            for i in range(nRow):
                temp[i] = new_caput_raws[i,:]
            new_caput_raws = temp
        if current_caput_raws.ndim != 1:
            nRow, nCol = current_caput_raws.shape
            temp = np.zeros(nRow, dtype=object)
            for i in range(nRow):
                temp[i] = current_caput_raws[i,:]
            current_caput_raws = temp

        new_caput_raws_nan_inds = np.array(
            [True if np.any(np.isnan(r)) else False for r in new_caput_raws])
        if np.any(new_caput_raws_nan_inds):
            enabled_indexes = np.where(self.caput_enabled_indexes)[0]
            invalid_change_indexes = enabled_indexes[new_caput_raws_nan_inds]
            rows, indexes = map(list, zip(*self.maps['cur_SentSP']))
            invalid_row_strings = [str(rows[indexes.index(i)]+1) # 1-indexed
                                   for i in invalid_change_indexes]
            msg = QMessageBox()
            msg.setWindowTitle('Aborting Step Change')
            msg.setText('One or more of the desired changes will result in unit '
                        'conversion failure. Most likely cause is due to '
                        'out of interpolation range. Try reducing the change.')
            msg.setInformativeText('The following rows will be invalid: {0}'.
                                   format(', '.join(invalid_row_strings)))
            msg.setIcon(QMessageBox.Critical)
            msg.exec_()
            return

        raw_step_size_array = new_caput_raws - current_caput_raws

        self.caput_raws[self.caput_enabled_indexes] += raw_step_size_array

        self.invoke_caput()

    #----------------------------------------------------------------------
    def step_down(self):
        """"""

        self.step_up(positive=False)

    #----------------------------------------------------------------------
    def multiply(self, positive=True):
        """"""

        self.update_NaNs_in_caput_raws()

        self.update_caput_enabled_indexes()

        #uc_list = list(
            #np.array(self.caput_toraw_unitconvs,
                     #dtype=object)[self.caput_enabled_indexes])
        #
        # TODO: Need to test the following block against real machine
        uc_list = [uc for uc, enabled in zip(self.caput_toraw_unitconvs,
                                             self.caput_enabled_indexes)
                   if enabled]

        current_caput_convs = self.caput_convs[self.caput_enabled_indexes]

        if positive:
            if self.mult_factor > 2.0:
                msg = QMessageBox()
                msg.addButton(QMessageBox.Yes)
                msg.addButton(QMessageBox.No)
                msg.setDefaultButton(QMessageBox.No)
                msg.setEscapeButton(QMessageBox.No)
                msg.setText(('Setpoints will be more than doubled. '
                             'Do you really want to proceed?'))
                msg.setIcon(QMessageBox.Question)
                msg.setWindowTitle('Large Setpoint Changes')
                choice = msg.exec_()
                if choice == QMessageBox.No:
                    return

            mult_factor = self.mult_factor

        else:
            if self.mult_factor != 0.0:
                if self.mult_factor < 0.5:
                    msg = QMessageBox()
                    msg.addButton(QMessageBox.Yes)
                    msg.addButton(QMessageBox.No)
                    msg.setDefaultButton(QMessageBox.No)
                    msg.setEscapeButton(QMessageBox.No)
                    msg.setText(('Setpoints will be more than doubled. '
                                 'Do you really want to proceed?'))
                    msg.setIcon(QMessageBox.Question)
                    msg.setWindowTitle('Large Setpoint Changes')
                    choice = msg.exec_()
                    if choice == QMessageBox.No:
                        return

                mult_factor = 1.0/self.mult_factor

            else:
                msg = QMessageBox()
                msg.setText('Setpoints cannot be divided by 0.')
                msg.setIcon(QMessageBox.Warning)
                msg.exec_()
                return

        new_caput_convs = current_caput_convs * mult_factor

        new_caput_raws = np.array(
            [uc(caput_conv) if uc is not None else caput_conv
             for (caput_conv, uc) in zip(new_caput_convs, uc_list)],
            dtype=object)

        self.caput_raws[self.caput_enabled_indexes] = new_caput_raws

        self.invoke_caput()

    #----------------------------------------------------------------------
    def divide(self):
        """"""

        self.multiply(positive=False)

    #----------------------------------------------------------------------
    def on_visible_column_change(self, visible_col_name_list):
        """"""

        self.visible_col_keys = [
            self.all_col_keys[self.all_col_names.index(name)]
            for name in visible_col_name_list
        ]

    #----------------------------------------------------------------------
    def restore_IniSP(self, n_steps, wait_time):
        """"""

        self.update_NaNs_in_caput_raws()

        self.update_caput_enabled_indexes()

        current_caput_raws = self.caput_raws[self.caput_enabled_indexes]
        current_caput_raws = np.array(
            [o if not isinstance(o, catools.dbr.ca_array) else o.__array__()
             for o in current_caput_raws],
            dtype=object)
        if current_caput_raws.ndim != 1:
            nRow, nCol = current_caput_raws.shape
            temp = np.zeros(nRow, dtype=object)
            for i in range(nRow):
                temp[i] = current_caput_raws[i,:]
            current_caput_raws = temp

        ini_caput_raws = self.caput_ini_raws[self.caput_enabled_indexes]
        ini_caput_raws = np.array(
            [o if not isinstance(o, catools.dbr.ca_array) else o.__array__()
             for o in ini_caput_raws],
            dtype=object)
        if ini_caput_raws.ndim != 1:
            nRow, nCol = ini_caput_raws.shape
            temp = np.zeros(nRow, dtype=object)
            for i in range(nRow):
                temp[i] = ini_caput_raws[i,:]
            ini_caput_raws = temp

        raw_step_size_array = (current_caput_raws - ini_caput_raws) / n_steps

        # Disable temporarily auto caget update, if enabled
        orig_auto_caget_delay_after_caput = self.auto_caget_delay_after_caput
        self.auto_caget_delay_after_caput = np.nan

        for i in range(n_steps):

            self.caput_raws[self.caput_enabled_indexes] -= raw_step_size_array

            self.invoke_caput()

            Sleep(wait_time)
            self.update_pv_vals()

        # Restore auto caget update
        self.auto_caget_delay_after_caput = orig_auto_caget_delay_after_caput

########################################################################
class SnapshotTableModel(QAbstractTableModel):
    """"""

    #----------------------------------------------------------------------
    def __init__(self, snapshot_abstract_model, DB_view=False):
        """Constructor"""

        isinstance(snapshot_abstract_model, SnapshotAbstractModel)

        QAbstractTableModel.__init__(self)

        self.abstract = snapshot_abstract_model

        self.DB_view = DB_view
        if self.DB_view:
            self.readonly = True
        else:
            self.readonly = False

        self._config_abstract = self.abstract._config_abstract
        self._config_table    = self.abstract._config_table

        # Short-hand notation
        self.db = self.abstract.db

        if '[unitconv_table text view]' not in self.db.getViewNames():
            self.db.create_temp_unitconv_table_text_view()

        self.d = OrderedDict()
        for k in self.abstract.all_col_keys:
            self.d[k] = []

        self._init_d()

        if not self.DB_view:
            # Update static column data
            self.update_init_pv_column_data()
            self.update_limits_columns()

            # Update dynamic column data
            self.visible_dynamic_col_keys = [
                k for k in self.abstract.dynamic_col_keys
                if (k in self.abstract.visible_col_keys) and
                (k not in ('weight', 'step_size', 'caput_enabled'))]

            self.non_visible_required_col_keys = [
                'cur_SP_ioc_ts', 'cur_RB_ioc_ts',
                # ^ always needed for ss_cur_SP_ioc_ts & ss_cur_RB_ioc_ts
            ]

        else:
            # Update dynamic column data
            self.visible_dynamic_col_keys = [
                k for k in self.abstract.all_col_keys
                if (k in self.abstract.visible_col_keys) and
                k.startswith('ss_')]

            self.non_visible_required_col_keys = []

        self.update_visible_dynamic_columns()

        self.connect(self.abstract, SIGNAL('pvValuesUpdatedInSSAbstract'),
                     self.update_visible_dynamic_columns)

        self.connect(
            self,
            SIGNAL('dataChanged(const QModelIndex &, const QModelIndex &)'),
            self.propagate_change_to_abstract)

    #----------------------------------------------------------------------
    def _init_d(self):
        """"""

        for k, v in self._config_table.d.items():
            self.d[k] = v

        for k in self.abstract.ss_only_col_keys:
            self.d[k] = np.ones(self.abstract.nRows, dtype=object)*np.nan

        self.d['caput_enabled'] = self.abstract.caput_enabled_rows

    #----------------------------------------------------------------------
    def load_column_from_file(self, filepath, selected_col_key):
        """"""

        msg = QMessageBox()

        try:
            col_data = np.loadtxt(filepath, comments='#')
        except:
            msg.setText('Invalid file. Failed to load column data from the file.')
            msg.setInformativeText(sys.exc_value.__repr__())
            msg.setIcon(QMessageBox.Critical)
            msg.exec_()
            return

        if col_data.ndim != 1:
            msg.setText('Text file must contain only one column of data.')
            msg.setIcon(QMessageBox.Critical)
            msg.exec_()
            return

        nRows = self.d[selected_col_key].size
        if col_data.size != nRows:
            msg.setText('Number of rows ({0:d}) in the file does not match '
                        'with number of rows ({1:d}) in the table.'.
                        format(col_data.size, nRows))
            msg.setIcon(QMessageBox.Critical)
            msg.exec_()
            return

        if selected_col_key == 'caput_enabled':
            not_0_or_1_inds = [i for i, v in enumerate(col_data)
                               if v not in (0, 1)]
            if not_0_or_1_inds != []:
                msg.setText('For "caput_ON" column, column data must be an '
                            'array of either 0 & 1.')
                msg.setIcon(QMessageBox.Critical)
                msg.exec_()
                return

        try:
            self.d[selected_col_key] = col_data

            col_ind = self.abstract.all_col_keys.index(selected_col_key)

            topLeftIndex     = self.index(0      , col_ind)
            bottomRightIndex = self.index(nRows-1, col_ind)

            # Need to uncheck "Synced Group Weight" temporarily
            orig_synced_group_weight_state = self.abstract.synced_group_weight
            self.abstract.synced_group_weight = False
            #
            self.emit(
                SIGNAL('dataChanged(const QModelIndex &, const QModelIndex &)'),
                topLeftIndex, bottomRightIndex)
            # Restore original state of "Synced Group Weight"
            self.abstract.synced_group_weight = orig_synced_group_weight_state
        except:
            msg.setText('Failed to load column data from the file.')
            msg.setInformativeText(sys.exc_value.__repr__())
            msg.setIcon(QMessageBox.Critical)
            msg.exec_()
            return

    #----------------------------------------------------------------------
    def on_visible_column_change(self):
        """"""

        self.visible_dynamic_col_keys = [
            k for k in self.abstract.dynamic_col_keys
            if (k in self.abstract.visible_col_keys) and
            (k not in ('weight', 'step_size', 'caput_enabled'))
        ]

        self.update_visible_dynamic_columns()

    #----------------------------------------------------------------------
    def propagate_change_to_abstract(self, topLeftIndex, bottomRightIndex):
        """"""

        col_left_index  = topLeftIndex.column()
        col_right_index = bottomRightIndex.column()
        row_top_index    = topLeftIndex.row()
        row_bottom_index = bottomRightIndex.row()

        if (col_left_index == col_right_index):
            col_ind = col_left_index
            col_key = self.abstract.all_col_keys[col_ind]
            row_inds = range(row_top_index, row_bottom_index+1)
        else:
            return

        if col_key == 'caput_enabled':

            for r in row_inds:
                self.abstract.caput_enabled_rows[r] = \
                    self.data(self.index(r, col_ind), role=Qt.UserRole)
            return

        if len(row_inds) == 1:

            index = topLeftIndex
            row_ind = row_top_index

            if row_ind == -1:
                return

            if self.abstract.synced_group_weight:
                gid = self._config_abstract.group_name_ids[row_ind]
                synced_row_inds = [
                    r for r, i in enumerate(self._config_abstract.group_name_ids)
                    if (i == gid) and (r != row_ind)]

            if col_key == 'weight':
                new_weight = float(self.data(index))
                self._config_abstract.weights[row_ind] = new_weight
                self.abstract.weight_array[row_ind]    = new_weight
                if self.abstract.synced_group_weight:
                    for r in synced_row_inds:
                        self._config_abstract.weights[r] = new_weight
                        self.abstract.weight_array[r]    = new_weight

            elif col_key == 'step_size':
                if (self.abstract.ref_step_size == 0.0) or \
                   (np.isnan(self.abstract.ref_step_size)):
                    raise ValueError('You should not be able to reach here.')
                else:
                    new_weight = \
                        float(self.data(index)) / self.abstract.ref_step_size
                    self._config_abstract.weights[row_ind] = new_weight
                    self.abstract.weight_array[row_ind]    = new_weight
                    if self.abstract.synced_group_weight:
                        for r in synced_row_inds:
                            self._config_abstract.weights[r] = new_weight
                            self.abstract.weight_array[r]    = new_weight
            elif col_key in ('tar_SP', 'tar_ConvSP'):
                print('WARNING: tar_SP & tar_ConvSP are not implemented yet in')
                print('tinkerModels.py: SnapshotTableModel.propagate_change_to_abstract')
            else:
                return
        else:

            if col_key == 'weight':
                self._config_abstract.weights = [
                    float(self.data(self.index(row_ind, col_ind)))
                    for row_ind in row_inds]
                self.abstract.weight_array = np.array(
                    self._config_abstract.weights[:])
            elif col_key == 'step_size':
                new_step_size_array = np.array([
                    float(self.data(self.index(row_ind, col_ind)))
                    for row_ind in row_inds])
                new_weight_array = \
                    new_step_size_array / self.abstract.ref_step_size
                self._config_abstract.weights = new_weight_array.tolist()
                self.abstract.weight_array = new_weight_array
            elif col_key in ('tar_SP', 'tar_ConvSP'):
                print('WARNING: tar_SP & tar_ConvSP are not implemented yet in')
                print('tinkerModels.py: SnapshotTableModel.propagate_change_to_abstract')
            else:
                return

        self.d['weight']    = self.abstract.weight_array
        self.d['step_size'] = self.abstract.ref_step_size * self.d['weight']
        self.abstract.step_size_array = self.d['step_size']

        self.repaint()

    #----------------------------------------------------------------------
    def on_ref_step_size_change(self, new_ref_step_size):
        """"""

        self.abstract.ref_step_size = new_ref_step_size

        self.d['step_size'] = \
            np.array(self.d['weight']) * self.abstract.ref_step_size
        self.abstract.step_size_array = self.d['step_size']

        step_size_col_ind = self.abstract.all_col_keys.index('step_size')
        topLeftIndex     = self.index(0, step_size_col_ind)
        bottomRightIndex = self.index(self.rowCount()-1, step_size_col_ind)
        self.emit(
            SIGNAL('dataChanged(const QModelIndex &, const QModelIndex &)'),
            topLeftIndex, bottomRightIndex)

    #----------------------------------------------------------------------
    def modifyAbstractModel(self, new_val, col_ind, row_inds):
        """"""

        self.abstract.modify_data(new_val, col_ind, row_inds)

        self.updateUserEdits(col_ind)

        self.repaint()

    #----------------------------------------------------------------------
    def updateUserEdits(self, col_ind):
        """"""

        col_key = self.abstract.all_col_keys[col_ind]

        if col_key in ('weight', 'step_size'):
            self.d['weight'] = self.abstract.weight_array[:]
            self.d['step_size'] = self.abstract.ref_step_size * self.d['weight']
        elif col_key == 'caput_enabled':
            self.d[col_key] = self.abstract.caput_enabled_rows[:]

    #----------------------------------------------------------------------
    def update_visible_dynamic_columns(self):
        """"""

        for k in self.non_visible_required_col_keys:
            self.update_column_data(k)

        for k in self.visible_dynamic_col_keys:
            self.update_column_data(k)

        modified_col_inds = [self.abstract.all_col_keys.index(k)
                             for k in self.visible_dynamic_col_keys]
        contig_modified_col_ind_pairs = get_contiguous_col_ind_pairs(
            modified_col_inds)

        for (leftCol, rightCol) in contig_modified_col_ind_pairs:
            topLeftIndex = self.index(0, leftCol)
            bottomRightIndex = self.index(self.abstract.nRows, rightCol)
            self.emit(
                SIGNAL('dataChanged(const QModelIndex &, const QModelIndex &)'),
                topLeftIndex, bottomRightIndex)

    #----------------------------------------------------------------------
    def update_column_data(self, col_key):
        """"""

        if col_key in ('cur_SP', 'cur_RB', 'cur_SentSP',
                       'cur_SP_ioc_ts', 'cur_RB_ioc_ts',
                       'cur_ConvSP', 'cur_ConvRB', 'cur_ConvSentSP'):

            rows, indexes = map(list, zip(*self.abstract.maps[col_key]))

            if col_key in ('cur_SP', 'cur_RB'):
                self.d[col_key][rows] = self.abstract.caget_raws[indexes]
            elif col_key in ('cur_SentSP'):
                self.d[col_key][rows] = self.abstract.caput_raws[indexes]
            elif col_key in ('cur_SP_ioc_ts', 'cur_RB_ioc_ts'):
                self.d[col_key][rows] = self.abstract.caget_ioc_ts_tuples[indexes]
            elif col_key in ('cur_ConvSP', 'cur_ConvRB'):
                self.d[col_key][rows] = self.abstract.caget_convs[indexes]
            elif col_key in ('cur_ConvSentSP'):
                self.d[col_key][rows] = self.abstract.caput_convs[indexes]

        elif col_key == 'D_cur_SP_ini_SP':
            self.d[col_key] = self.d['cur_SP'] - self.d['ini_SP']
        elif col_key == 'D_cur_ConvSP_ini_ConvSP':
            self.d[col_key] = self.d['cur_ConvSP'] - self.d['ini_ConvSP']
        elif col_key == 'D_cur_RB_ini_RB':
            self.d[col_key] = self.d['cur_RB'] - self.d['ini_RB']
        elif col_key == 'D_cur_ConvRB_ini_ConvRB':
            self.d[col_key] = self.d['cur_ConvRB'] - self.d['ini_ConvRB']
        elif col_key == 'D_cur_RB_cur_SP':
            rows = self.abstract.rb_sp_same_size_rows
            self.d[col_key][rows] = \
                self.d['cur_RB'][rows] - self.d['cur_SP'][rows]
        elif col_key == 'D_cur_ConvRB_cur_ConvSP':
            rows = self.abstract.rb_sp_same_size_rows
            self.d[col_key][rows] = \
                self.d['cur_ConvRB'][rows] - self.d['cur_ConvSP'][rows]
        elif col_key == 'D_cur_RB_cur_SentSP':
            rows = self.abstract.rb_sp_same_size_rows
            self.d[col_key][rows] = \
                self.d['cur_RB'][rows] - self.d['cur_SentSP'][rows]
        elif col_key == 'D_cur_ConvRB_cur_ConvSentSP':
            rows = self.abstract.rb_sp_same_size_rows
            self.d[col_key][rows] = \
                self.d['cur_ConvRB'][rows] - self.d['cur_ConvSentSP'][rows]
        elif col_key == 'D_cur_SP_cur_SentSP':
            self.d[col_key] = self.d['cur_SP'] - self.d['cur_SentSP']
        elif col_key == 'D_cur_ConvSP_cur_ConvSentSP':
            self.d[col_key] = self.d['cur_ConvSP'] - self.d['cur_ConvSentSP']
        elif col_key == 'D_tar_SP_cur_SP':
            pass
        elif col_key == 'D_tar_ConvSP_cur_ConvSP':
            pass
        elif col_key.startswith('ss_'):
            # These snapshot columns will be updated ONLY when a snapshot is
            # being saved, so they should NOT be updated here. Just pass.
            pass
        else:
            self.d[col_key] = np.ones((self.abstract.nRows,))*np.nan

    #----------------------------------------------------------------------
    def update_init_pv_column_data(self):
        """"""

        ini_val_col_keys      = ['ini_SP'       , 'ini_RB'       ]
        ini_conv_val_col_keys = ['ini_ConvSP'   , 'ini_ConvRB'   ]
        ini_ts_col_keys       = ['ini_SP_ioc_ts', 'ini_RB_ioc_ts']

        for col_key in ini_val_col_keys:
            if self.abstract.maps[col_key] != []:
                rows, indexes = map(list, zip(*self.abstract.maps[col_key]))
                self.d[col_key][rows] = self.abstract.caget_raws[indexes]

        for col_key in ini_conv_val_col_keys:
            if self.abstract.maps[col_key] != []:
                rows, indexes = map(list, zip(*self.abstract.maps[col_key]))
                self.d[col_key][rows] = self.abstract.caget_convs[indexes]

        for col_key in ini_ts_col_keys:
            if self.abstract.maps[col_key] != []:
                rows, indexes = map(list, zip(*self.abstract.maps[col_key]))
                self.d[col_key][rows] = self.abstract.caget_ioc_ts_tuples[indexes]

    #----------------------------------------------------------------------
    def update_limits_columns(self):
        """"""

        rows, indexes = map(list, zip(*self.abstract.maps['cur_SentSP']))

        self.d['lo_lim'][rows] = self.abstract.lo_lims_raw[indexes]
        self.d['hi_lim'][rows] = self.abstract.hi_lims_raw[indexes]

        self.d['lo_lim_conv'][rows] = self.abstract.lo_lims_conv[indexes]
        self.d['hi_lim_conv'][rows] = self.abstract.hi_lims_conv[indexes]

    #----------------------------------------------------------------------
    def update_snapshot_columns(self, from_DB):
        """"""

        a = self.abstract

        key_list = ['SentSP', 'ConvSentSP', 'SP', 'SP_ioc_ts', 'ConvSP',
                    'RB', 'RB_ioc_ts', 'ConvRB']
        ss_key_list = ['ss_'+k for k in key_list]

        if not from_DB:
            for k in key_list:
                self.d['ss_'+k] = self.d['cur_'+k]
        else:
            if a.ss_id is not None:
                if '[ss_meta_table text view]' not in self.db.getViewNames(
                    square_brackets=True):
                    self.db.create_temp_ss_meta_table_text_view()
                ss_username = self.db.getColumnDataFromTable(
                    '[ss_meta_table text view]',
                    column_name_list=['ss_username'],
                    condition_str='ss_id={0:d}'.format(a.ss_id))[0][0]

                hdf5filepath = osp.join(
                    config.SNAPSHOT_FOLDERPATH,
                    date_month_folder_str(a.ss_ctime),
                    date_snapshot_filename_str(a.ss_ctime, ss_username))

                try:
                    f = h5py.File(hdf5filepath, 'r')
                except:
                    msg = QMessageBox()
                    msg.setText(('Data file "{0}" for Snapshot ID #{1:d} could '
                                 'not be found.').format(hdf5filepath, a.ss_id))
                    msg.setIcon(QMessageBox.Critical)
                    msg.exec_()
                    return

                self.d['weight'] = f['weights'].value
                self.d['caput_enabled'] = f['caput_enabled_rows'].value

                caget_ioc_ts_tuples = f['caget_ioc_ts_tuples'].value

                caget_raws_arrays = []
                if 'caget_raws_arrays' in f:
                    for k, v in f['caget_raws_arrays'].items():
                        caget_raws_arrays.append(v.value)
                caget_raws = np.array(
                    f['caget_raws_scalars'].value.tolist() + caget_raws_arrays,
                    dtype=object)
                caget_convs = np.array(
                    [uc(r) if uc is not None else r for r, uc
                     in zip(caget_raws, self.abstract.caget_unitconvs)],
                    dtype=object)
                rows, indexes = map(list, zip(*self.abstract.maps['cur_SP']))
                self.d['ss_SP'][rows]     = caget_raws[indexes]
                self.d['ss_ConvSP'][rows] = caget_convs[indexes]
                self.d['ss_SP_ioc_ts'][rows] = caget_ioc_ts_tuples[indexes]
                rows, indexes = map(list, zip(*self.abstract.maps['cur_RB']))
                self.d['ss_RB'][rows]     = caget_raws[indexes]
                self.d['ss_ConvRB'][rows] = caget_convs[indexes]
                self.d['ss_RB_ioc_ts'][rows] = caget_ioc_ts_tuples[indexes]

                caput_raws_arrays = []
                if 'caput_raws_arrays' in f:
                    for k, v in f['caput_raws_arrays'].items():
                        caput_raws_arrays.append(v.value)
                caput_raws = np.array(
                    f['caput_raws_scalars'].value.tolist() + caput_raws_arrays,
                    dtype=object)
                caput_convs = self.abstract.convert_caput_raws(
                    caput_raws, self.abstract.caput_fromraw_unitconvs)
                rows, indexes = map(list, zip(*self.abstract.maps['cur_SentSP']))
                self.d['ss_SentSP'][rows]     = caput_raws[indexes]
                self.d['ss_ConvSentSP'][rows] = caput_convs[indexes]

                f.close()

        modified_col_inds = [
            a.all_col_keys.index(k) for k in ss_key_list]
        if modified_col_inds == []:
            return

        contig_modified_col_ind_pairs = get_contiguous_col_ind_pairs(
            modified_col_inds)

        for (leftCol, rightCol) in contig_modified_col_ind_pairs:
            topLeftIndex = self.index(0, leftCol)
            bottomRightIndex = self.index(a.nRows, rightCol)
            self.emit(
                SIGNAL('dataChanged(const QModelIndex &, const QModelIndex &)'),
                topLeftIndex, bottomRightIndex)

    #----------------------------------------------------------------------
    def repaint(self):
        """"""

        self.reset() # Initiate repaint

    #----------------------------------------------------------------------
    def rowCount(self, parent=QModelIndex()):
        """"""

        return len(self._config_abstract.channel_ids)

    #----------------------------------------------------------------------
    def columnCount(self, parent=QModelIndex()):
        """"""

        return len(self.abstract.all_col_keys)

    #----------------------------------------------------------------------
    def data(self, index, role=Qt.DisplayRole):
        """"""

        row = index.row()
        col = index.column()

        col_key    = self.abstract.all_col_keys[col]
        str_format = self.abstract.all_str_formats[col]

        col_list = self.d[col_key]

        if ( not index.isValid() ) or \
           ( not (0 <= row < self.rowCount()) ):
            return None

        if (str_format != 'checkbox') and (role in (Qt.DisplayRole, Qt.EditRole)):
            # ^ Need "EditRole". Otherwise, existing text will disappear
            # when trying to edit.

            if len(col_list) != 0: value = col_list[row]
            else                 : return 'N/A'

            if value is None:
                return 'None'
            elif value is '':
                return "''"
            elif str_format == 'timestamp_ns': # This case check must come
                # before "if isinstance(value, tuple)", as the value for this
                # case is a tuple.
                try:
                    return datestr_ns(value)
                except:
                    return 'None'
            elif isinstance(value, (list, tuple, set, np.ndarray)):
                return str(value)
            else:
                return '{{{:s}}}'.format(str_format).format(value)

        elif str_format == 'checkbox':

            value = col_list[row]

            if role == Qt.DisplayRole:
                return None
            elif role in (Qt.EditRole, Qt.UserRole):
                if value == 1:
                    return True
                else:
                    return False

        else:
            return None

    #----------------------------------------------------------------------
    def setData(self, index, value, role=Qt.EditRole):
        """"""

        row = index.row()
        col = index.column()

        col_key    = self.abstract.all_col_keys[col]
        str_format = self.abstract.all_str_formats[col]

        if ( not index.isValid() ) or \
           ( not (0 <= row < self.rowCount()) ):

            return False

        else:
            L = self.d[col_key]

            if (str_format is None) or (str_format in (':s', 'checkbox')):
                L[row] = value
            elif str_format.endswith('g'):
                if value == '':
                    return False
                try:
                    L[row] = float(value)
                except:
                    L[row] = float('nan')
            else:
                raise ValueError('Unexpected str_format: {:s}'.
                                 format(str_format))

            self.emit(
                SIGNAL('dataChanged(const QModelIndex &, const QModelIndex &)'),
                index, index)

            return True

    #----------------------------------------------------------------------
    def headerData(self, section, orientation, role=Qt.DisplayRole):
        """"""

        if role == Qt.TextAlignmentRole:
            if orientation == Qt.Horizontal:
                return int(Qt.AlignLeft|Qt.AlignVCenter)
            else:
                return int(Qt.AlignRight|Qt.AlignVCenter)

        elif role != Qt.DisplayRole:
            return None

        elif orientation == Qt.Horizontal:
            # Horizontal Header display name requested
            return self.abstract.all_col_names[section]

        else: # Vertical Header display name requested
            return int(section+1) # row number

    #----------------------------------------------------------------------
    def flags(self, index):
        """"""

        default_flags = QAbstractTableModel.flags(self, index) # non-editable

        if self.readonly: return default_flags

        if not index.isValid(): return default_flags

        col_key = self.abstract.all_col_keys[index.column()]
        if self.abstract.user_editable[col_key]:
            if (col_key == 'step_size') and \
               ((self.abstract.ref_step_size == 0.0) or \
                np.isnan(self.abstract.ref_step_size)):
                return default_flags
            else:
                self.d[col_key] = np.array(self.d[col_key])
                # ^ self.d[col_key] may be a tuple. In this case, this column will
                # not be editable. So, it is made sure that self.d[col_key] is a
                # modifiable numpy array here.
                return Qt.ItemFlags(default_flags | Qt.ItemIsEditable) # editable
        else:
            return default_flags # non-editable

    #----------------------------------------------------------------------
    def restore_IniSP(self, n_steps, wait_time):
        """
        """

        msg = QMessageBox()
        msg.addButton(QMessageBox.Yes)
        msg.addButton(QMessageBox.No)
        msg.setDefaultButton(QMessageBox.No)
        msg.setEscapeButton(QMessageBox.No)
        msg.setIcon(QMessageBox.Question)
        msg.setText('Only setpoint PVs whose "caput ON" is checked '
                    'will be restored:\n\n'
                    'Would you like to proceed for restoration?')
        msg.setWindowTitle('Final Confirmation for Restoration')
        choice = msg.exec_()
        if choice == QMessageBox.No:
            return

        self.abstract.restore_IniSP(n_steps, wait_time)

