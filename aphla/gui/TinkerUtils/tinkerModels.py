#! /usr/bin/env python

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

from PyQt4.QtCore import (QObject, Qt, SIGNAL, QAbstractItemModel,
                          QAbstractTableModel, QModelIndex)
from PyQt4.QtGui import (QMessageBox, QFileDialog)

from cothread import Sleep
from cothread.catools import caget, caput, FORMAT_TIME

import aphla as ap

import config
try:
    from . import (SmartSizedMessageBox, datestr, datestr_ns)
except:
    from aphla.gui.TinkerUtils import (SmartSizedMessageBox, datestr, datestr_ns)
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
class ConfigMetaTableModel(QAbstractTableModel):

    #----------------------------------------------------------------------
    def __init__(self, search_result_dict, all_col_keys):
        """Constructor"""

        QAbstractTableModel.__init__(self)

        self.search_result    = search_result_dict
        self.all_col_keys     = all_col_keys
        self.col_keys_wo_desc = all_col_keys[:]
        self.col_keys_wo_desc.remove('config_description')

        self.col_names_wo_desc = [
            'Config.ID', 'Config.Name', 'Username', 'MASAR ID', 'Ref.StepSize',
            'Synced.GroupWeight', 'Time Created']

        self.nRows = len(self.search_result[self.col_keys_wo_desc[0]])
        self.nCols = len(self.col_keys_wo_desc)

        self.str_formats = [':s']*self.nCols
        for i, k in enumerate(self.col_keys_wo_desc):
            if k.endswith('_id') or (k == 'config_synced_group_weight'):
                self.str_formats[i] = ':d'
            elif k == 'config_ref_step_size':
                self.str_formats[i] = ':.6g'
            elif k == 'config_ctime':
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
                'unitsymb_raw', 'unitconv_data_toraw', 'unitconv_data_fromraw',
                'unitconv_inv_toraw', 'unitconv_inv_fromraw'],
            condition_str='config_id={0:d}'.format(config_id))

        unitconv_dict = {}
        d['channels'] = []
        for i, (group_name, channel_name, weight, caput_enabled, pvsp, pvrb,
                machine_name, lattice_name, elem_name, field,
                unitsys, unitconv_type, polarity, unitsymb, unitsymb_raw,
                unitconv_data_toraw, unitconv_data_fromraw, unitconv_inv_toraw,
                unitconv_inv_fromraw) in enumerate(zip(*out)):

            if unitconv_type == 'poly':
                conv_data_fromraw = [float(s) for s
                                     in unitconv_data_fromraw.split(',') if s]
                conv_data_toraw   = [float(s) for s
                                     in unitconv_data_toraw.split(',') if s]
            elif unitconv_type == 'interp1':
                xp_txt, fp_txt = unitconv_data_fromraw.split(';')
                conv_data_fromraw = {'xp': [float(s) for s in xp_txt.split(',')],
                                     'fp': [float(s) for s in fp_txt.split(',')]}
                xp_txt, fp_txt = unitconv_data_toraw.split(';')
                conv_data_toraw   = {'xp': [float(s) for s in xp_txt.split(',')],
                                     'fp': [float(s) for s in fp_txt.split(',')]}
            elif unitconv_type == 'NoConversion':
                conv_data_fromraw = conv_data_toraw = ''
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
                for gi in group_ids:
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
                    for gi in group_ids:
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
            raise NotImplementedError(col_key)
        elif col_key == 'pvsp':
            raise NotImplementedError(col_key)
        elif col_key == 'pvrb':
            raise NotImplementedError(col_key)

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
        elif ((col_left_index == col_right_index) and
              (row_top_index == row_bottom_index)):
            pass
        else:
            return

        index = topLeftIndex
        row_ind = row_top_index
        col_ind = col_left_index
        col_key = self.abstract.all_col_keys[col_ind]

        if self.abstract.synced_group_weight:
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

            for r in row_inds:
                self.abstract.caput_enabled_rows[r] = \
                    self.data(self.index(r, col_ind), role=Qt.UserRole)

        else:
            return

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
        for k, v in unique.iteritems():
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
        for k, v in unique.iteritems():
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
                (conv_data_txt,), (inv,), (polarity,)= \
                self.db.getColumnDataFromTable(
                    '[unitconv_table text view]',
                    column_name_list=['dst_unitsymb', 'src_unitsymb',
                                      'unitconv_type', 'conv_data_txt',
                                      'inv', 'polarity'],
                    condition_str=('unitconv_id={0:d}'.
                                   format(unitconv_fromraw_id)))

            unitsymb_list.append(unitsymb)
            unitsymb_raw_list.append(unitsymb_raw)
            unitconv_type_list.append(unitconv_type)
            polarity_list.append(polarity)

            conv_data_txt_fromraw_list.append(conv_data_txt)
            if inv == 0: inv = 'False'
            else       : inv = 'True'
            unitconv_inv_fromraw_list.append(inv)

            (conv_data_txt,), (inv,) = self.db.getColumnDataFromTable(
                '[unitconv_table text view]',
                column_name_list=['conv_data_txt', 'inv'],
                condition_str=('unitconv_id={0:d}'.
                               format(unitconv_toraw_id)))

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

        self.d['weight'] = np.array(self.abstract.weights)
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
             (self.d['elem_name'][row] != '') and \
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

        np_array_keys = [k for k, v in self.d.iteritems()
                         if isinstance(v, np.ndarray)]

        for r in row_list[::-1]:
            self.abstract.group_name_ids.pop(r)
            self.abstract.channel_ids.pop(r)
            self.abstract.weights.pop(r)
            self.abstract.caput_enabled_rows.pop(r)

            for k, v in self.d.iteritems():
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
    def __init__(self, config_abstract_model, vis_col_key_list):
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
                self.caget_unitconvs # unit conversion objects for caput
                self.caget_ioc_ts_tuples
                self.caget_pv_str_list
                self.caget_pv_map_list
                self.caget_pv_size_list

            self.n_caput_pvs:
                self.caput_raws
                self.caput_convs # unit-converted caput data
                self.caput_unitconvs # unit conversion objects for caput
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
        self.filepath             = ''
        self.ss_ctime             = None

        self.weight_array        = _ct.d['weight']
        self.step_size_array     = self.ref_step_size * self.weight_array
        self.caput_enabled_rows  = _ct.d['caput_enabled']

        self.db = tinkerdb.TinkerMainDatabase()

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

        # Compile caput list

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

        # Dict whose item contains a list of 2-element tuple.
        # The 2-element tuple consists of the row index in the GUI table
        # and the list index of flattened pv list that correspond to the row
        self.maps = {}
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

        self.rb_sp_same_size_rows = []
        for i, (sp_size, rb_size) in enumerate(zip(
            _ct.d['pvsp_array_size'], _ct.d['pvrb_array_size'])):
            if sp_size == rb_size:
                self.rb_sp_same_size_rows.append(i)

        self.n_caget_pvs = len(self.caget_pv_str_list)
        self.n_caput_pvs = len(self.caput_pv_str_list)

        self.caget_raws  = np.ones(self.n_caget_pvs)*np.nan
        self.caget_convs = np.ones(self.n_caget_pvs)*np.nan
        self.caget_ioc_ts_tuples = np.array([(None,None)]*self.n_caget_pvs)

        self.caput_raws  = np.ones(self.n_caput_pvs)*np.nan
        self.caput_convs = np.ones(self.n_caput_pvs)*np.nan

        self.caput_not_yet = True

        self.init_unitconv()

        self.update_pv_vals()

        self.update_init_pv_vals()

    #----------------------------------------------------------------------
    def get_unitconv_callable(self, conv_type, conv_inv, polarity, conv_txt):
        """"""

        if conv_type == 'NoConversion':
            return lambda val: val
        elif (conv_type == 'poly') and (conv_inv == 0):
            coeffs = [float(s) for s in conv_txt.split(',')]
            return np.poly1d(coeffs)*polarity
        elif (conv_type == 'poly') and (conv_inv == 1):
            a, b = [float(s) for s in conv_txt.split(',')]
            ar, br = polarity/a, -b/a
            return np.poly1d([ar, br])
        elif (conv_type == 'interp1') and (conv_inv == 0):
            xp_txt, fp_txt = conv_txt.split(';')
            xp = [float(s) for s in xp_txt.split(',')]
            fp = [float(s) for s in fp_txt.split(',')]
            # `xp` is assumed to be monotonically increasing. Otherwise,
            # interpolation will make no sense.
            return lambda x: polarity*np.interp(x, xp, fp,
                                                left=np.nan, right=np.nan)
        elif (conv_type == 'interp1') and (conv_inv == 1):
            xp_txt, fp_txt = conv_txt.split(';')
            xp = [float(s) for s in xp_txt.split(',')]
            fp = [float(s) for s in fp_txt.split(',')]
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
            return lambda x: polarity*np.interp(x, xp_inv, fp_inv,
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

        (caget_conv_types, caget_conv_data_txts, caget_conv_invs,
         caget_polarities) = self.db.getMatchedColumnDataFromTable(
             '[unitconv_table text view]', 'unitconv_id',
             unitconv_fromraw_ids, ':d',
             column_name_return_list=['unitconv_type', 'conv_data_txt',
                                      'inv', 'polarity'])

        self.caget_unitconvs = [None]*self.n_caget_pvs

        rb_map_row_list = [x[0] for x in self.maps['cur_RB']]
        sp_map_row_list = [x[0] for x in self.maps['cur_SP']]
        for row, (conv_type, conv_txt, conv_inv, polarity) in enumerate(zip(
            caget_conv_types, caget_conv_data_txts, caget_conv_invs,
            caget_polarities)):

            uc_callable = self.get_unitconv_callable(
                conv_type, conv_inv, polarity, conv_txt)

            if row in rb_map_row_list:
                i = self.maps['cur_RB'][rb_map_row_list.index(row)][1]
                self.caget_unitconvs[i] = uc_callable
            if row in sp_map_row_list:
                i = self.maps['cur_SP'][sp_map_row_list.index(row)][1]
                self.caget_unitconvs[i] = uc_callable

        ## Initialize unit conversion data for caput

        (caput_conv_types, caput_conv_data_txts, caput_conv_invs,
         caput_polarities) = self.db.getMatchedColumnDataFromTable(
             '[unitconv_table text view]', 'unitconv_id',
             unitconv_toraw_ids, ':d',
             column_name_return_list=['unitconv_type', 'conv_data_txt',
                                      'inv', 'polarity'])

        self.caput_unitconvs = [None]*self.n_caput_pvs

        sp_map_row_list = [x[0] for x in self.maps['cur_SentSP']]
        for row, (conv_type, conv_txt, conv_inv, polarity) in enumerate(zip(
            caput_conv_types, caput_conv_data_txts, caput_conv_invs,
            caput_polarities)):

            uc_callable = self.get_unitconv_callable(
                conv_type, conv_inv, polarity, conv_txt)

            if row in sp_map_row_list:
                i = self.maps['cur_SentSP'][sp_map_row_list.index(row)][1]
                self.caput_unitconvs[i] = uc_callable

    #----------------------------------------------------------------------
    def update_caput_enabled_indexes(self):
        """"""

        self.caput_enabled_indexes = np.array([True]*self.n_caput_pvs)
        for row, index in self.maps['cur_SP']:
            self.caput_enabled_indexes[index] = self.caput_enabled_rows[row]

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

        print '# caget update only took {:.6f} seconds'.format(
            tEnd_caget - self.caget_sent_ts_second)
        print '# caget & model/view update took {:.6f} seconds'.format(
            tEnd_model_view - self.caget_sent_ts_second)

    #----------------------------------------------------------------------
    def update_init_pv_vals(self):
        """"""

        self.caget_ini_raws  = np.copy(self.caget_raws)
        self.caget_ini_convs = np.copy(self.caget_raws)

    #----------------------------------------------------------------------
    def update_ss_ctime(self):
        """"""

        if self.ss_id is not None:
            self.ss_ctime = self.db.getColumnDataFromTable(
                'snapshot_meta_table', column_name_list=['ss_ctime'],
                condition_str='ss_id={0:d}'.format(self.ss_id))[0][0]

    #----------------------------------------------------------------------
    def update_caput_vectors(self):
        """"""

        if self.caput_not_yet:
            rows, indexes = map(list, zip(*self.maps['cur_SP']))
            self.caput_raws = self.caget_raws[indexes]
            self.caput_convs = np.array(
                [uc(r) if uc is not None else r for r, uc
                 in zip(self.caput_raws, self.caput_unitconvs)])[indexes]
            self.caput_not_yet = False
        else:
            nan_inds = [i for i, r in enumerate(self.caput_raws)
                        if np.any(np.isnan(r))]
            if nan_inds != []:
                rows, indexes = map(list, zip(*self.maps['cur_SP']))
                for i in nan_inds:
                    self.caput_raws[i] = self.caget_raws[indexes[i]]
                    r  = self.caput_raws[i]
                    uc = self.caput_unitconvs[i]
                    self.caput_convs[i] = uc(r) if uc is not None else r

    #----------------------------------------------------------------------
    def invoke_caput(self):
        """"""

        out = [(i, r) for i, (r, enabled)
               in enumerate(zip(self.caput_raws, self.caput_enabled_indexes))
               if enabled and (not np.isnan(r))]
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

        if not np.isnan(self.auto_caget_delay_after_caput):
            Sleep(self.auto_caget_delay_after_caput)
            self.update_pv_vals()
        else:
            self.emit(SIGNAL('pvValuesUpdatedInSSAbstract'))

    #----------------------------------------------------------------------
    def step_up(self, positive=True):
        """"""

        self.update_caput_vectors()

        self.update_caput_enabled_indexes()

        if positive:
            self.caput_raws[self.caput_enabled_indexes] += \
                self.step_size_array[self.caput_enabled_rows]
        else:
            self.caput_raws[self.caput_enabled_indexes] -= \
                self.step_size_array[self.caput_enabled_rows]

        self.invoke_caput()

    #----------------------------------------------------------------------
    def step_down(self):
        """"""

        self.step_up(positive=False)

    #----------------------------------------------------------------------
    def multiply(self, positive=True):
        """"""

        self.update_caput_vectors()

        self.update_caput_enabled_indexes()

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

            self.caput_raws[self.caput_enabled_indexes] *= self.mult_factor
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

                self.caput_raws[self.caput_enabled_indexes] /= self.mult_factor
            else:
                msg = QMessageBox()
                msg.setText('Setpoints cannot be divided by 0.')
                msg.setIcon(QMessageBox.Warning)
                msg.exec_()
                return

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

########################################################################
class SnapshotTableModel(QAbstractTableModel):
    """"""

    #----------------------------------------------------------------------
    def __init__(self, snapshot_abstract_model):
        """Constructor"""

        isinstance(snapshot_abstract_model, SnapshotAbstractModel)

        QAbstractTableModel.__init__(self)

        self.abstract = snapshot_abstract_model

        self._config_abstract = self.abstract._config_abstract
        self._config_table    = self.abstract._config_table

        # Short-hand notation
        self.db = self.abstract.db

        if '[unitconv_table text view]' not in self.db.getViewNames():
            self.db.create_temp_unitconv_table_text_view()

        self.d = OrderedDict()
        for k in self.abstract.all_col_keys:
            self.d[k] = []

        for k, v in self._config_table.d.iteritems():
            self.d[k] = v

        for k in self.abstract.ss_only_col_keys:
            self.d[k] = np.ones(self.abstract.nRows, dtype=object)*np.nan

        self.d['caput_enabled'] = self.abstract.caput_enabled_rows

        # Update static column data
        self.update_init_pv_column_data()

        # Update dynamic column data
        self.visible_dynamic_col_keys = [
            k for k in self.abstract.dynamic_col_keys
            if (k in self.abstract.visible_col_keys) and
            (k not in ('weight', 'step_size', 'caput_enabled'))]

        self.update_visible_dynamic_columns()

        self.connect(self.abstract, SIGNAL('pvValuesUpdatedInSSAbstract'),
                     self.update_visible_dynamic_columns)

        self.connect(
            self,
            SIGNAL('dataChanged(const QModelIndex &, const QModelIndex &)'),
            self.propagate_change_to_abstract)

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

        if ((col_left_index == col_right_index) and
            (self.abstract.all_col_keys[col_left_index] == 'caput_enabled')):
            row_inds = range(row_top_index, row_bottom_index+1)
        elif ((col_left_index == col_right_index) and
              (row_top_index == row_bottom_index)):
            pass
        else:
            return

        index = topLeftIndex
        row_ind = row_top_index
        col_ind = col_left_index
        col_key = self.abstract.all_col_keys[col_ind]

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

        elif col_key == 'caput_enabled':

            for r in row_inds:
                self.abstract.caput_enabled_rows[r] = \
                    self.data(self.index(r, col_ind), role=Qt.UserRole)

            return

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
    def update_visible_dynamic_columns(self):
        """"""

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
        elif col_key == 'D_tar_SP_cur_SP':
            pass
        elif col_key == 'D_tar_ConvSP_cur_ConvSP':
            pass
        else:
            #raise ValueError('Unexpected col_key: {0:s}'.format(col_key))
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





