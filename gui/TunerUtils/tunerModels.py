#! /usr/bin/env python

import sip
sip.setapi('QString', 2)
sip.setapi('QVariant', 2)

import sys, os
import numpy as np
from datetime import datetime

from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import SIGNAL, QObject
from PyQt4.QtGui import QStandardItem, QStandardItemModel

import aphla as ap
if ap.machines._lat is None:
    ap.initNSLS2V1()

import config as const

########################################################################
class AbstractTunerConfigModel(QStandardItemModel):
    """"""

    #----------------------------------------------------------------------
    def __init__(self, config_dict=None, col_name_list=None):
        """Constructor"""
        
        QStandardItemModel.__init__(self)
        
        self.SortRole = QtCore.Qt.UserRole
        
        if config_dict is None:
            self.name = ''
            self.description = ''
        
            self.channel_group_list = []
        else:
            key_list = ['name','description','channel_group_list']
            for k in key_list:
                setattr(self, k, config_dict[k])

        if col_name_list is None:
            self.col_name_list = const.ALL_COL_NAMES[:]
        else:
            self.col_name_list = col_name_list[:]
            
        if const.COL_GROUP_NAME not in self.col_name_list:
            raise ValueError('Column name list must contain COL_GROUP_NAME')
        else:
            self.col_name_list.remove(const.COL_GROUP_NAME)
            self.col_name_list.insert(0,const.COL_GROUP_NAME)
        
        self.get_group_level_col_list()
        self.get_channel_level_col_list()
        
        self.setHorizontalHeaderLabels(self.col_name_list)
        self.setColumnCount(len(self.col_name_list))
        self.removeRows(0,self.rowCount()) # clear contents
        
        
    #----------------------------------------------------------------------
    def get_group_level_col_list(self):
        """"""
        
        self.group_level_col_list = const.GROUP_LEVEL_COL_LIST[:]
        self.group_level_col_list.remove(const.COL_GROUP_NAME)
        self.group_level_col_list = list(np.intersect1d(
            np.array(self.group_level_col_list),
            np.array(self.col_name_list) ) )
        
    #----------------------------------------------------------------------
    def get_channel_level_col_list(self):
        """"""
        
        self.channel_level_col_list = const.CHANNEL_LEVEL_COL_LIST[:]
        self.channel_level_col_list = list(np.intersect1d(
            np.array(self.channel_level_col_list),
            np.array(self.col_name_list) ) )
        
    #----------------------------------------------------------------------
    def data(self, modelIndex, role):
        """
        Reimplementation of QStandardItemModel's data()
        The purpose is to allow sorting by numbers, not just by
        default string sorting.
        """
        
        if role == self.SortRole:
            try:
                value = QStandardItemModel.data(self, modelIndex, QtCore.Qt.DisplayRole)
                value = float(value)
            except:
                pass
        else:
            value = QStandardItemModel.data(self, modelIndex, role)
            
        return value
        
    #----------------------------------------------------------------------
    def getColumnIndex(self, column_name):
        """"""
        
        if column_name in self.col_name_list:
            return self.col_name_list.index(column_name)
        else:
            return None
        
    
    #----------------------------------------------------------------------
    def updateGroupBasedModel(self, change_type='rebuild', **kwargs):
        """"""
        
        str_format_index = const.ENUM_STR_FORMAT
        prop_name_index = const.ENUM_PROP_NAME
        
        group_col_ind = self.getColumnIndex(const.COL_GROUP_NAME)        
        
        # Temporarily block signals emitted from the model
        self.blockSignals(True)
        
        if change_type == 'rebuild':
            self.removeRows(0,self.rowCount()) # clear contents
            nRows = self.rowCount()
            if nRows != 0:
                raise ValueError('nRows should be 0 at this point.')
            
            channel_group_list = self.channel_group_list[:]
            
            self.setRowCount(len(channel_group_list))
            row_index_offset = 0

        elif change_type == 'remove':
            start_row_index = kwargs.get('start_row_index',None)
            row_counts = kwargs.get('row_counts',1)
            if start_row_index is not None:
                self.removeRows(start_row_index,row_counts)
            else:
                start_col_index = kwargs.get('start_col_index',None)
                col_counts = kwargs.get('col_counts',1)
                if start_col_index is not None:
                    self.removeColumns(start_col_index,col_counts)
                else:
                    raise ValueError('Insufficient arguments passed for removal of row(s) & column(s)')
            
            channel_group_list = [] # Set this to empty so that the for-loop section below to add items will be skipped    
            
        elif change_type == 'append':
            channelGroupList = kwargs.get('channelGroupList',None)
            if channelGroupList is not None:
                channel_group_list = channelGroupList
            else:
                raise ValueError('Argument "channelGroupList" is needed for "append" change_type')
            
            nRows = self.rowCount()
            row_index_offset = nRows
            self.setRowCount(nRows+len(channel_group_list))
            
        else:
            raise ValueError('Unexpected change_type: '+change_type)
        
        
        for (row_index, channelGroup) in enumerate(channel_group_list):
            row_index += row_index_offset
            
            groupName = channelGroup['name']
            chNameList = channelGroup['channel_name_list']
            
            groupItem = QStandardItem(groupName)
            groupItem.setFlags(groupItem.flags() |
                               QtCore.Qt.ItemIsEditable) # Make the item editable
    
            for c in self.group_level_col_list:
                col_index = self.getColumnIndex(c)
                cc = const.DICT_COL[c]
                str_format = cc[str_format_index]
                prop_name = cc[prop_name_index]
                if prop_name == 'weight':
                    prop_val = channelGroup[prop_name]
                elif prop_name == 'normalized_weight_list':
                    prop_val = self.normalized_weight_list[row_index]
                elif prop_name == 'step_size_list':
                    prop_val == self.step_size_list[row_index]
                else:
                    raise ValueError('Unexpected property name: '+prop_name)
                item = QStandardItem(('{0'+str_format+'}').format(prop_val))
                if c in const.EDITABLE_COL_NAME_LIST:
                    item.setFlags(item.flags() |
                                  QtCore.Qt.ItemIsEditable) # Make the item editable
                else:
                    item.setFlags(item.flags() &
                                  ~QtCore.Qt.ItemIsEditable) # Make the item NOT editable
                    
                self.setItem(row_index, col_index, item)
                for child_index in range(len(chNameList)):
                    groupItem.setChild(child_index, col_index, item.clone())
                
            for (child_index, chName) in enumerate(chNameList):
                elemName, fieldName = chName.split('.')
                elem = ap.getElements(elemName)[0]
                channelNameItem = QStandardItem(chName)
                channelNameItem.setFlags(channelNameItem.flags() & 
                                         ~QtCore.Qt.ItemIsEditable) # Make the item NOT editable
                groupItem.setChild(child_index, group_col_ind, channelNameItem)
                
                for c in self.channel_level_col_list:
                    col_index = self.getColumnIndex(c)
                    cc = const.DICT_COL[c]
                    str_format = cc[str_format_index]
                    prop_name =  cc[prop_name_index]
                    try:
                        value = getattr(elem,prop_name)
                    except:
                        if prop_name == 'pvrb':
                            pvrb, garbage = self._getpv_names(chName,handle='readback')
                            value = pvrb
                        elif prop_name == 'pvsp':
                            garbage, pvsp = self._getpv_names(chName,handle='setpoint')
                            value = pvsp
                        elif prop_name == 'channel_name':
                            value = chName
                        elif prop_name == 'field':
                            value = fieldName
                        elif prop_name == 'curr_RB':
                            value = self._current_RB[self._all_channel_name_flat_list.index(chName)]
                        elif prop_name == 'curr_SP':
                            value = self._current_SP[self._all_channel_name_flat_list.index(chName)]
                        elif prop_name == 'curr_RB_time':
                            value = self._current_RB_time[self._all_channel_name_flat_list.index(chName)]
                        elif prop_name == 'curr_SP_time':
                            value = self._current_SP_time[self._all_channel_name_flat_list.index(chName)]
                        elif prop_name == 'snapshot_RB':
                            value = None
                        elif prop_name == 'snapshot_SP':
                            value = None
                        elif prop_name == 'snapshot_RB_time':
                            value = None
                        elif prop_name == 'snapshot_SP_time':
                            value = None
                        elif prop_name == 'target_SP':
                            value = self._target_SP[self._all_channel_name_flat_list.index(chName)]
                        elif prop_name == 'D_target_SP_curr_SP':
                            value = self._D_target_SP_current_SP[self._all_channel_name_flat_list.index(chName)]                            
                        elif prop_name == 'init_RB':
                            value = self._init_RB[self._all_channel_name_flat_list.index(chName)]
                        elif prop_name == 'init_SP':
                            value = self._init_SP[self._all_channel_name_flat_list.index(chName)]
                        elif prop_name == 'init_RB_time':
                            value = self._init_RB_time[self._all_channel_name_flat_list.index(chName)]
                        elif prop_name == 'init_SP_time':
                            value = self._init_SP_time[self._all_channel_name_flat_list.index(chName)]
                        elif prop_name == 'D_curr_RB_init_RB':
                            value = self._D_current_RB_init_RB[self._all_channel_name_flat_list.index(chName)]
                        elif prop_name == 'D_curr_SP_init_SP':
                            value = self._D_current_SP_init_SP[self._all_channel_name_flat_list.index(chName)]
                        elif prop_name == 'D_curr_RB_curr_SP':
                            value = self._D_current_RB_current_SP[self._all_channel_name_flat_list.index(chName)]
                        else:
                            raise NotImplementedError(prop_name)
                    
                    if str_format != 'timestamp':
                        if (value == None) or isinstance(value,list) \
                           or isinstance(value,tuple):
                            str_format = ':s'
                        else:
                            pass
                        item = QStandardItem(('{0'+str_format+'}').format(value))
                    else:
                        if value is None:
                            time_str = 'None'
                        elif np.isnan(value):
                            time_str = 'nan'
                        else:
                            time_str = datetime.fromtimestamp(value).isoformat()
                        item = QStandardItem(time_str)
                    
                    item.setFlags(item.flags() &
                                  ~QtCore.Qt.ItemIsEditable) # Make the item NOT editable
                    
                    groupItem.setChild(child_index, col_index, item)
            
            self.setItem(row_index, group_col_ind, groupItem)
                
                
    
        # Re-enable the blocked signals emitted from the model
        self.blockSignals(False)
        
        
        self.emit(SIGNAL('modelUpdated'))           
    
    #----------------------------------------------------------------------
    def updateChannelBasedModel(self):
        """"""
        
        pass
    
        
    #----------------------------------------------------------------------
    def _getpv_names(self, channel_name, handle='both'):
        """"""
        
        elemName, fieldName = channel_name.split('.')
        elem = ap.getElements(elemName)[0]
        
        if (handle == 'both') or (handle == 'readback'):
            pv = elem.pv(field=fieldName,handle='readback')
            if len(pv) == 1:
                pvrb = pv[0]
            elif len(pv) == 0:
                pvrb = None
            else:
                raise ValueError('Unexpected pv list returned: '+str(pv))
        else:
            pvrb = None
            
        
        if (handle == 'both') or (handle == 'setpoint'):
            pv = elem.pv(field=fieldName,handle='setpoint')
            if len(pv) == 1:
                pvsp = pv[0]
            elif len(pv) == 0:
                pvsp = None
            else:
                raise ValueError('Unexpected pv list returned: '+str(pv))
        else:
            pvsp = None
            
        return pvrb, pvsp
