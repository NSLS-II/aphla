#! /usr/bin/env python

import sip
sip.setapi('QString', 2)
sip.setapi('QVariant', 2)

import sys, os
import numpy as np
from datetime import datetime
from time import time, strftime, localtime
from subprocess import Popen, PIPE

from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import (SIGNAL, QObject, QAbstractItemModel,
                          QAbstractTableModel, QModelIndex)
from PyQt4.QtGui import (QStandardItem, QStandardItemModel, QMessageBox)

import aphla as ap
if ap.machines._lat is None:
    ap.initNSLS2V2()

import config as const
from aphla.gui.utils.addr import (getIPs, getMACs)

#----------------------------------------------------------------------
def getusername():
    """"""

    p = Popen('whoami',stdout=PIPE,stderr=PIPE)
    username, error = p.communicate()

    if error:
        raise OSError('Error for whoami: '+error)
    else:
        return username.strip()

#----------------------------------------------------------------------
def getuserinfo():
    """"""

    ips = getIPs()
    ip_str_list = [ip.str for ip in ips]
    ip_str = ', '.join(ip_str_list)

    macs = getMACs()
    mac_str_list = [mac.str for mac in macs]
    mac_str = ', '.join(mac_str_list)

    return ip_str, mac_str, getusername()


#----------------------------------------------------------------------
def getChannelProperty(obj, propertyName):
    """
    propertyName can be a property of element or a function of element
    """

    element, field = obj

    if propertyName == 'fields':
        return field

    if propertyName not in ('pvrb','pvsp'):

        x = getattr(element, propertyName)

    elif propertyName == 'pvrb':
        try:
            x = element.pv(field=field,handle='readback')[:]
            if len(x) >= 2:
                msgBox = QMessageBox()
                msgBox.setIcon(QMessageBox.Critical)
                info_str = 'More than one PV is assigned for '+element.name+': '+str(x)
                msgBox.setText(info_str)
                msgBox.exec_()
                return
            else:
                x = x[0]
        except: # For DIPOLE, there is no field specified
            x = ''
    elif propertyName == 'pvsp':
        try:
            x = element.pv(field=field,handle='setpoint')[:]
            if len(x) >= 2:
                msgBox = QMessageBox()
                msgBox.setIcon(QMessageBox.Critical)
                info_str = 'More than one PV is assigned for '+element.name+': '+str(x)
                msgBox.setText(info_str)
                msgBox.exec_()
                return
            else:
                x = x[0]
        except: # For DIPOLE, there is no field specified
            x = ''

    return x

#----------------------------------------------------------------------
def getChannelObjectList(channel_name_list):
    """"""

    elem_field_tuple_list = [ch_name.split('.') for ch_name in channel_name_list]

    return [(ap.getElements(elem_name)[0], field_name)
            for (elem_name,field_name) in elem_field_tuple_list]

#----------------------------------------------------------------------
def getChannelPropertyListsDict(channel_name_list):
    """"""

    channel_object_list = getChannelObjectList(channel_name_list)

    D = {}
    for (k,v) in const.CHANNEL_PROP_DICT.iteritems():
        D[k] = [getChannelProperty(c,v) for c in channel_object_list]

    return D


########################################################################
class ConfigChannel(object):
    """"""

    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""

        self._config_id = None
        self._channel_name_id = None
        self._channel_group_name_id = None

        for k in const.ALL_PROP_KEYS_CONFIG_SETUP:
            data_type = const.PROP_DICT[k][const.ENUM_DATA_TYPE]
            if data_type == 'string':
                default_val = ''
            elif data_type in ('float','int'):
                default_val = float('NaN')
            elif data_type == ('N/A','BLOB'):
                default_val = None
            else:
                raise ValueError('Unexpected data type: ' + data_type)
            setattr(self, k, default_val)

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
    def data(self, index, role=QtCore.Qt.DisplayRole):
        """"""

        if not index.isValid():
            return None

        if role != QtCore.Qt.DisplayRole:
            return None

        item = index.internalPointer()

        return item.data(index.column())

    #----------------------------------------------------------------------
    def flags(self, index):
        """"""

        if not index.isValid():
            return 0

        return (QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)

    #----------------------------------------------------------------------
    def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):
        """"""

        if (orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole):
            return self.rootItem.data(section)
        else:
            return None

    #----------------------------------------------------------------------
    def reset(self):
        """"""

        QAbstractItemModel.reset(self)




########################################################################
class TunerConfigSetupBaseModel(QObject):
    """"""

    #----------------------------------------------------------------------
    def __init__(self, all_col_key_list=None):
        """Constructor"""

        self._config_id = None
        self.config_name = ''
        self.userinfo = getuserinfo()
        self.time_created = None
        self.description = ''
        self.appended_descriptions = '' # include modified times as part of the appended text

        if all_col_key_list is None:
            self.all_col_key_list = const.ALL_PROP_KEYS_CONFIG_SETUP
        else:
            self.all_col_key_list = all_col_key_list
        self.all_col_name_list = [const.PROP_DICT[k][const.ENUM_SHORT_DESCRIP_NAME]
                                  for k in self.all_col_key_list]

        for k in const.ALL_PROP_KEYS_CONFIG_SETUP:
            setattr(self, 'k_'+k, [])

        self.group_name_list = []
        self.grouped_ind_list = []

    #----------------------------------------------------------------------
    def findDuplicateChannels(self, new_channel_name_list):
        """"""

        existing_channel_name_list = self.k_channel_name[:]

        return list(np.intersect1d(existing_channel_name_list, new_channel_name_list))

    #----------------------------------------------------------------------
    def findNonExistentChannels(self, new_channel_name_list):
        """"""

        elem_name_tuple, field_tuple = zip(*[ch.split('.')
                                             for ch in new_channel_name_list])

        # First find if the corresponding elements exist
        non_existent_elem_name_list = [elem_name for elem_name in elem_name_tuple
                                       if ap.getElements(elem_name)==[]]
        if non_existent_elem_name_list:
            msgBox = QMessageBox()
            msgBox.setText('Non-existent Element Name(s) Found')
            info_text_list = ['The following element names do not exist in the lattice:'] + \
                [''] + non_existent_elem_name_list + ['']
            info_text = '\n'.join(info_text_list)
            msgBox.setInformativeText(info_text)
            msgBox.setIcon(QMessageBox.Critical)
            msgBox.exec_()
            return non_existent_elem_name_list

        # Then check if the field exists for the corresponding elements
        elem_list = [ap.getElements(elem_name)[0] for elem_name in elem_name_tuple]
        non_existent_channel_name_list = [elem.name+field for (field, elem)
                                          in zip(field_tuple, elem_list)
                                          if field not in elem.fields()]
        if non_existent_channel_name_list:
            msgBox = QMessageBox()
            msgBox.setText('Non-existent Channel Name(s) Found')
            info_text_list = ['The following channel field names do not exist in the lattice:'] + \
                [''] + non_existent_channel_name_list+ ['']
            info_text = '\n'.join(info_text_list)
            msgBox.setInformativeText(info_text)
            msgBox.setIcon(QMessageBox.Critical)
            msgBox.exec_()
            return non_existent_channel_name_list

        return []

    #----------------------------------------------------------------------
    def appendChannels(self, new_lists_dict):
        """"""

        if self.findNonExistentChannels(new_lists_dict['channel_name']) != []:
            return

        dupChannels = self.findDuplicateChannels(new_lists_dict['channel_name'])
        if dupChannels != []:
            info_text_list = ['The following channel names already exist:'] + \
                [''] + dupChannels + [''] + \
                ['Do you want to proceed by adding only new non-duplicate channels?']
            info_text = '\n'.join(info_text_list)
            msg = QMessageBox()
            msg.setText('Duplicate Channel Name(s) Found')
            msg.setInformativeText(info_text)
            msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            msg.setDefaultButton(QMessageBox.No)
            result = msg.exec_()

            if result == QMessageBox.No:
                return
            else:
                new_channel_list = new_lists_dict['channel_name'][:]
                dup_ind_list = [i for (i,ch) in enumerate(new_channel_list)
                                if ch in dupChannels]
                for (k,v_list) in new_lists_dict.iteritems():
                    new_lists_dict[k] = [v for (i,v) in enumerate(v_list)
                                         if i not in dup_ind_list]

        for (k,v) in new_lists_dict.iteritems():
            getattr(self, 'k_'+k).extend(v)
            if k == 'channel_name':
                channelPropertyListsDict = getChannelPropertyListsDict(v)
                for (k2, v2) in channelPropertyListsDict.iteritems():
                    getattr(self, 'k_'+k2).extend(v2)

        self.update_grouped_ind_list()

    #----------------------------------------------------------------------
    def update_grouped_ind_list(self):
        """"""

        self.update_group_name_list()

        grouped_ind_list = []
        for gn in self.group_name_list:
            grouped_ind_list.append([i for (i,n) in enumerate(self.k_group_name)
                                     if n == gn])

        self.grouped_ind_list = grouped_ind_list

    #----------------------------------------------------------------------
    def update_group_name_list(self):
        """
        Group name order should be in the order of first appearnce in self.k_group_name list.
        """

        unique_group_name_list = list(set(self.k_group_name))

        first_appearance_ind_list = [self.k_group_name.index(g)
                                     for g in unique_group_name_list]

        sort_ind = list(np.argsort(first_appearance_ind_list))

        self.group_name_list = [unique_group_name_list[i] for i in sort_ind]



########################################################################
class TunerConfigSetupTableModel(QAbstractTableModel):
    """"""

    #----------------------------------------------------------------------
    def __init__(self, base_model=None):
        """Constructor"""

        QAbstractTableModel.__init__(self)

        if base_model is None:
            self.base_model = TunerConfigSetupBaseModel()
        else:
            self.base_model = base_model

    #----------------------------------------------------------------------
    def resetModel(self):
        """"""

        self.reset() # Initiate repaint

    #----------------------------------------------------------------------
    def rowCount(self, parent=QModelIndex()):
        """"""

        return len(self.base_model.k_channel_name)

    #----------------------------------------------------------------------
    def columnCount(self, parent=QModelIndex()):
        """"""

        return len(self.base_model.all_col_name_list)

    #----------------------------------------------------------------------
    def data(self, index, role=QtCore.Qt.DisplayRole):
        """"""

        b = self.base_model

        row = index.row()
        col_key = b.all_col_key_list[index.column()]

        if ( not index.isValid() ) or \
           ( not (0 <= row < self.rowCount()) ):
            return None

        if role == QtCore.Qt.DisplayRole:
            #value = getattr(b.config_channel_list[row], col_key)
            value = getattr(b,'k_'+col_key)[row]
            return value
        else:
            return None

    #----------------------------------------------------------------------
    def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):
        """"""

        if role == QtCore.Qt.TextAlignmentRole:
            if orientation == QtCore.Qt.Horizontal:
                return int(QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
            else:
                return int(QtCore.Qt.AlignRight|QtCore.Qt.AlignVCenter)

        elif role != QtCore.Qt.DisplayRole:
            return None

        elif orientation == QtCore.Qt.Horizontal: # Horizontal Header display name requested
            return self.base_model.all_col_name_list[section]

        else: # Vertical Header display name requested
            return int(section+1) # row number

    #----------------------------------------------------------------------
    def flags(self, index):
        """"""

        default_flags = QAbstractTableModel.flags(self, index) # non-editable

        if not index.isValid(): return default_flags

        col_key = self.base_model.all_col_key_list[index.column()]
        if const.PROP_DICT[col_key][const.ENUM_EDITABLE]:
            return QtCore.Qt.ItemFlags(default_flags | QtCore.Qt.ItemIsEditable) # editable
        else:
            return default_flags # non-editable

    #----------------------------------------------------------------------
    def setData(self, index, value, role=QtCore.Qt.EditRole):
        """"""

        row = index.row()
        col = index.column()
        col_key = self.base_model.all_col_key_list[col]

        if ( not index.isValid() ) or \
           ( not (0 <= row < self.rowCount()) ):

            return False

        else:
            L = getattr(self.base_model, 'k_'+col_key)
            L[row] = value
            #setattr(self.base_model.config_channel_list[row], col_key, value)

            self.emit(SIGNAL('dataChanged(QModelIndex,QModelIndex)'),
                      index, index)
            return True







########################################################################
class TunerConfigSetupTreeModel(TreeModel):
    """"""

    #----------------------------------------------------------------------
    def __init__(self, all_column_name_list, base_model=None):
        """Constructor"""

        if base_model is None:
            self.base_model = TunerConfigSetupBaseModel()
        else:
            self.base_model = base_model

        TreeModel.__init__(self, all_column_name_list)

    #----------------------------------------------------------------------
    def resetModel(self):
        """"""

        b = self.base_model

        self.beginResetModel()

        tree_key_list = const.ALL_PROP_KEYS_CONFIG_SETUP[:]
        index = tree_key_list.index('group_name')
        tree_key_list.remove('group_name')
        tree_key_list.insert(index,'channel_name')
        '''
        By replacing 'group_name' with 'channel_name', it will
        display channel names under a group name.
        '''

        matrix = np.array([getattr(b, 'k_'+key) for key in tree_key_list]).transpose()
        group_items = [TreeItem([group_name]) for group_name in b.group_name_list]
        for (group_ind, group_item) in enumerate(group_items):
            child_items = [TreeItem(list(matrix[channel_ind,:]))
                           for channel_ind in b.grouped_ind_list[group_ind]]
            group_item.appendChildren(child_items)

        self.rootItem.deleteChildren()
        self.rootItem.appendChildren(group_items)

        self.endResetModel()


########################################################################
class TunerSnapshotBaseModel(QObject):
    """"""

    #----------------------------------------------------------------------
    def __init__(self, config_base_model, all_col_key_list=None):
        """Constructor"""

        self._config_base_model = config_base_model

        self._snapshot_id = None
        self.snapshot_name = ''
        self.userinfo = getuserinfo()
        self.time_snapshot_taken = None
        self.description = ''
        self.appended_descriptions = '' # include modified times as part of the appended text
        self.masar_event_id = None

        if all_col_key_list is None:
            self.all_col_key_list = const.ALL_PROP_KEYS
        else:
            self.all_col_key_list = all_col_key_list
        self.all_col_name_list = [const.PROP_DICT[k][const.ENUM_SHORT_DESCRIP_NAME]
                                  for k in self.all_col_key_list]

        for k in const.ALL_PROP_KEYS:
            attr_name = 'k_'+k
            if k in const.ALL_PROP_KEYS_CONFIG_SETUP:
                setattr(self, attr_name,
                        getattr(self._config_base_model, attr_name))
            else:
                setattr(self, attr_name, [])

        self.group_name_list = self._config_base_model.group_name_list
        self.grouped_ind_list = self._config_base_model.grouped_ind_list

    #----------------------------------------------------------------------
    def isSnapshot(self):
        """"""

        if self._snapshot_id is None:
            return False
        else:
            return True

    #----------------------------------------------------------------------
    def update_grouped_ind_list(self):
        """"""

        self._config_base_model.update_grouped_ind_list()

    #----------------------------------------------------------------------
    def update_group_name_list(self):
        """"""

        self._config_base_model.update_group_name_list()

    #----------------------------------------------------------------------
    def getName(self, source='config'):
        """"""

        if source == 'config':
            return self._config_base_model.config_name
        elif source == 'snapshot':
            return self.snapshot_name
        else:
            raise ValueError('First argument must be either "config" or "snapshot".')

    #----------------------------------------------------------------------
    def getUserInfo(self, source='config'):
        """"""

        if source == 'config':
            return self._config_base_model.userinfo
        elif source == 'snapshot':
            return self.userinfo
        else:
            raise ValueError('First argument must be either "config" or "snapshot".')

    #----------------------------------------------------------------------
    def getTimeCreated(self, source='config'):
        """"""

        if source == 'config':
            return self._config_base_model.time_created
        elif source == 'snapshot':
            return self.time_snapshot_taken
        else:
            raise ValueError('First argument must be either "config" or "snapshot".')

    #----------------------------------------------------------------------
    def getDescription(self, source='config', include_appended=True):
        """"""

        if source == 'config':
            desc = self._config_base_model.description
            if include_appended:
                desc += '\n' + self._config_base_model.appended_descriptions
        elif source == 'snapshot':
            desc = self.description
            if include_appended:
                desc += '\n' + self.appended_descriptions
        else:
            raise ValueError('First argument must be either "config" or "snapshot".')

        return desc


########################################################################
class TunerSnapshotTableModel(TunerConfigSetupTableModel):
    """"""

    #----------------------------------------------------------------------
    def __init__(self, base_model):
        """Constructor"""

        TunerConfigSetupTableModel.__init__(self, base_model=base_model)




########################################################################
class TunerSnapshotTreeModel(TunerConfigSetupTreeModel):
    """"""

    #----------------------------------------------------------------------
    def __init__(self, all_column_name_list, base_model):
        """Constructor"""

        TunerConfigSetupTreeModel.__init__(self,
                                           all_column_name_list=all_column_name_list,
                                           base_model=base_model)




########################################################################
class TunerConfigAbstractModel(object):
    """"""

    #----------------------------------------------------------------------
    def __init__(self, config_name='', description='',
                 config_channel_list=None, col_name_list=None):
        """Constructor
        """

        self.time_created = time() # current time in seconds from Epoch
        self.username = getusername()

        if config_channel_list is None:
            self.config_channel_list = []
        else:
            self.config_channel_list = config_channel_list[:]

        self.update_channel_name_flat_list()

        self.update_pv_flat_list()

    #----------------------------------------------------------------------
    def update_channel_name_flat_list(self):
        """"""

        self.channel_name_flat_list = [cc.channel_name for cc in self.config_channel_list]

        if len(self.channel_name_flat_list) != len(set(self.channel_name_flat_list)):
            raise ValueError('Duplicate found in channel names.')

    #----------------------------------------------------------------------
    def update_pv_flat_list(self):
        """"""

        self.pvrb_flat_list = []
        self.pvrb_dict = {}
        self.pvsp_flat_list = []
        self.pvsp_dict = {}

        for (i,ch) in enumerate(self.channel_name_flat_list):
            elemName, fieldName = ch.split('.')
            elem = ap.getElements(elemName)[0]
            pv = elem.pv(field=fieldName,handle='readback')
            if len(pv) == 1:
                self.pvrb_flat_list.append(pv[0])
                self.pvrb_dict[ch] = len(self.pvrb_flat_list)-1
            elif len(pv) == 0:
                pass
            else:
                raise ValueError("Multiple pv's found for readback: "+str(pv))
            pv = elem.pv(field=fieldName,handle='setpoint')
            if len(pv) == 1:
                self.pvsp_flat_list.append(pv[0])
                self.pvsp_dict[ch] = len(self.pvsp_flat_list)-1
            elif len(pv) == 0:
                pass
            else:
                raise ValueError("Multiple pv's found for setpoint: "+str(pv))

        self.pv_flat_list = self.pvrb_flat_list + self.pvsp_flat_list




########################################################################
class TunerConfigSetupAbstractModel(QAbstractItemModel):
    """"""

    #----------------------------------------------------------------------
    def __init__(self, config_name='', description='',
                 config_channel_list=None, col_name_list=None,
                 grouped=True, parent=None):
        """Constructor

        The following explains how the model behaves when a user changes
        a weight or a step size for a given channel:

        If a user changes the weight for a channel, then only this weight
        will change, and the weights of all the other channels will NOT be changed.
        However, the step size of the channel whose weight has been just
        changed will be updated as follows.
              (Weight) (Step Size)    (Weight)  (Step Size)
        Ch.1: NaN -> 0  NaN        => 0          0
        Ch.2: 1         100           1          100
        Ch.3: 0         0             0          0
        Ch.4: NaN       NaN           NaN        NaN

        Ch.1: NaN -> 2  NaN        => 2          200 (=2*100/1)
        Ch.2: 1         100           1          100
        Ch.3: 0         0             0          0
        Ch.4: NaN       NaN           NaN        NaN

              (Weight) (Step Size)    (Weight)  (Step Size)
        Ch.1: 0 -> NaN  0          => NaN        NaN
        Ch.2: 1         100           1          100
        Ch.3: 0         0             0          0
        Ch.4: NaN       NaN           NaN        NaN

        Ch.1: 0 -> 2    0          => 2          200 (=2*100/1)
        Ch.2: 1         100           1          100
        Ch.3: 0         0             0          0
        Ch.4: NaN       NaN           NaN        NaN

              (Weight) (Step Size)    (Weight)  (Step Size)
        Ch.1: 3 -> NaN  300        => NaN        NaN
        Ch.2: 1         100           1          100
        Ch.3: 0         0             0          0
        Ch.4: NaN       NaN           NaN        NaN

        Ch.1: 3 -> 0    300        => 0          0
        Ch.2: 1         100           1          100
        Ch.3: 0         0             0          0
        Ch.4: NaN       NaN           NaN        NaN

        Ch.1: 3 -> 2    300        => 2          200 (=2*100/1)
        Ch.2: 1         100           1          100
        Ch.3: 0         0             0          0
        Ch.4: NaN       NaN           NaN        NaN

        If there is no other channel with non-zero numeric weight:
              (Weight) (Step Size)    (Weight)  (Step Size)
        Ch.1: NaN -> 0  NaN        => 0          0
        Ch.2: 0         0             0          0
        Ch.3: NaN       NaN           NaN        NaN

        Ch.1: NaN -> 2  NaN        => 2          2
        Ch.2: 0         0             0          0
        Ch.3: NaN       NaN           NaN        NaN

              (Weight) (Step Size)    (Weight)  (Step Size)
        Ch.1: 0 -> NaN  0          => NaN        NaN
        Ch.2: 0         0             0          0
        Ch.3: NaN       NaN           NaN        NaN

        Ch.1: 0 -> 2    0          => 2          2
        Ch.2: 0         0             0          0
        Ch.3: NaN       NaN           NaN        NaN

              (Weight) (Step Size)    (Weight)  (Step Size)
        Ch.1: 3 -> NaN  300        => NaN        NaN
        Ch.2: 0         0             0          0
        Ch.3: NaN       NaN           NaN        NaN

        Ch.1: 3 -> 0    300        => 0          0
        Ch.2: 0         0             0          0
        Ch.3: NaN       NaN           NaN        NaN

        Ch.1: 3 -> 2    300        => 2          200 (=2*300/3)
        Ch.2: 0         0             0          0
        Ch.3: NaN       NaN           NaN        NaN

        If a user changes the step size for a channel, then none
        of the weights will be changed, but the step sizes of all
        the other channels will be updated (unless the weight of
        the changed channel is either 0 or NaN) according to these
        unchagned weights as follows.
        Note that if the weight of a channel is NaN, then the step
        size of the channel will always be NaN, no matter how a
        user tries to change the step size to other than NaN. If the
        weight of a channel is zero, then the step size of the
        channel will always be 0 if a user tries to change the step
        size to non-zero number, or NaN if a user tries to change
        the step size to NaN.
              (Weight) (Step Size)    (Weight)  (Step Size)
        Ch.1: NaN       NaN -> 0   => NaN        NaN
        Ch.2: 1         100           1          100
        Ch.3: 0         0             0          0
        Ch.4: NaN       NaN           NaN        NaN

        Ch.1: NaN       NaN -> 200 => NaN        NaN
        Ch.2: 1         100           1          100
        Ch.3: 0         0             0          0
        Ch.4: NaN       NaN           NaN        NaN

              (Weight) (Step Size)    (Weight)  (Step Size)
        Ch.1: 0         0 -> NaN   => 0          NaN (=0*NaN)
        Ch.2: 1         100           1          100
        Ch.3: 0         0             0          0
        Ch.4: NaN       NaN           NaN        NaN

        Ch.1: 0         0 -> 2     => 0          0 (=0*2)
        Ch.2: 1         100           1          100
        Ch.3: 0         0             0          0
        Ch.4: NaN       NaN           NaN        NaN

              (Weight) (Step Size)    (Weight)  (Step Size)
        Ch.1: 3         300 -> NaN => 3          NaN
        Ch.2: 1         100           1          NaN (=1*NaN/3)
        Ch.3: 0         0             0          NaN (=0*NaN/3)
        Ch.4: NaN       NaN           NaN        NaN

        Ch.1: 3         300 -> 0   => 3          0
        Ch.2: 1         100           1          0 (=1*0/3)
        Ch.3: 0         0             0          0 (=0*0/3)
        Ch.4: NaN       NaN           NaN        NaN

        Ch.1: 3         300 -> 150 => 3          150
        Ch.2: 1         100           1          50 (=1*150/3)
        Ch.3: 0         0             0          0 (=0*150/3)
        Ch.4: NaN       NaN           NaN        NaN


        """

        QAbstractItemModel.__init__(self, parent)

        #self.time_created = time() # current time in seconds from Epoch
        #self.username = getusername()

        #self.grouped = grouped

        #if config_channel_list is None:
            #self.config_channel_list = []
        #else:
            #self.config_channel_list = config_channel_list[:]

        #self.update_channel_name_flat_list()

        #self.update_pv_flat_list()

        # Up to here needed for ConfigSetup

        self.update_pv_values()

        self.init_RB = self.current_RB[:]
        self.init_SP = self.current_SP[:]
        self.init_RB_ioc_time = self.current_RB_ioc_time[:]
        self.init_SP_ioc_time = self.current_SP_ioc_time[:]
        self.init_RB_pc_time = [self.current_PC_time for rb in self.current_RB]
        self.init_SP_pc_time = [self.current_PC_time for rb in self.current_RB]

        self.target_SP = self.init_SP[:]

        self.update_derived_pv_values()

        if col_name_list is None:
            #self.col_name_list = const.ALL_COL_NAMES[:]
            self.col_name_list = [const.PROP_DICT[k][const.ENUM_SHORT_DESCRIP_NAME]
                                  for k in const.ALL_PROP_KEYS]
        else:
            self.col_name_list = col_name_list[:]

        if self.col_name_list[0] != 'group_name':
            raise ValueError('First column key must be "group_name".')



        #self.setHorizontalHeaderLabels(self.col_name_list)
        #self.setColumnCount(len(self.col_name_list))
        #self.removeRows(0,self.rowCount()) # clear contents


    #----------------------------------------------------------------------
    def update_channel_name_flat_list(self):
        """"""

        self.channel_name_flat_list = [cc.channel_name for cc in self.config_channel_list]

        if len(self.channel_name_flat_list) != len(set(self.channel_name_flat_list)):
            raise ValueError('Duplicate found in channel names.')

    #----------------------------------------------------------------------
    def update_pv_flat_list(self):
        """"""

        self.pvrb_flat_list = []
        self.pvrb_dict = {}
        self.pvsp_flat_list = []
        self.pvsp_dict = {}

        for (i,ch) in enumerate(self.channel_name_flat_list):
            elemName, fieldName = ch.split('.')
            elem = ap.getElements(elemName)[0]
            pv = elem.pv(field=fieldName,handle='readback')
            if len(pv) == 1:
                self.pvrb_flat_list.append(pv[0])
                self.pvrb_dict[ch] = len(self.pvrb_flat_list)-1
            elif len(pv) == 0:
                pass
            else:
                raise ValueError("Multiple pv's found for readback: "+str(pv))
            pv = elem.pv(field=fieldName,handle='setpoint')
            if len(pv) == 1:
                self.pvsp_flat_list.append(pv[0])
                self.pvsp_dict[ch] = len(self.pvsp_flat_list)-1
            elif len(pv) == 0:
                pass
            else:
                raise ValueError("Multiple pv's found for setpoint: "+str(pv))

        self.pv_flat_list = self.pvrb_flat_list + self.pvsp_flat_list

    #----------------------------------------------------------------------
    def update_pv_values(self):
        """"""

        self.current_PC_time = time() # current time in seconds from Epoch

        pv_results = caget(self.pv_flat_list,format=FORMAT_TIME)
        pvrb_results = pv_results[:len(self.pvrb_flat_list)]
        pvsp_results = pv_results[len(self.pvrb_flat_list):]

        pvrb_dict_keys = self.pvrb_dict.keys()
        self.current_RB = np.array([pvrb_results[self.pvrb_dict[c]].real
                                    if c in pvrb_dict_keys
                                    else float('NaN')
                                    for c in self.channel_name_flat_list])
        self.current_RB_ioc_time = np.array([pvrb_results[self.pvrb_dict[c]].timestamp
                                             if c in pvrb_dict_keys
                                             else float('NaN')
                                             for c in self.channel_name_flat_list])

        pvsp_dict_keys = self.pvsp_dict.keys()
        self.current_SP = np.array([pvsp_results[self.pvsp_dict[c]].real
                                    if c in pvsp_dict_keys
                                    else float('NaN')
                                    for c in self.channel_name_flat_list])
        self.current_SP_ioc_time = np.array([pvsp_results[self.pvsp_dict[c]].timestamp
                                             if c in pvsp_dict_keys
                                             else float('NaN')
                                             for c in self.channel_name_flat_list])

    #----------------------------------------------------------------------
    def update_derived_pv_values(self):
        """"""

        self.D_target_SP_current_SP = self.target_SP - self.current_SP
        self.D_current_RB_init_RB = self.current_RB - self.init_RB
        self.D_current_SP_init_SP = self.current_SP - self.init_SP
        self.D_current_RB_current_SP = self.current_RB - self.current_SP

    #----------------------------------------------------------------------
    def index(self, row, column, parent=QModelIndex()):
        """"""

        if not parent.isValid():
            return self.createIndex(row, column, self.rootNodes[row])
        else:
            parentNode = parent.internalPointer()
            return self.createIndex(row, column, parentNode.subnodes[row])


    #----------------------------------------------------------------------
    def parent(self, index):
        """"""

        if not index.isValid():
            return QModelIndex()

        node = index.internalPointer()
        if node.parent is None:
            return QModelIndex()
        else:
            # Assuming only the first column can have children
            return self.createIndex(node.parent.row, 0, node.parent)


    #----------------------------------------------------------------------
    def rowCount(self, parent=QModelIndex()):
        """"""

        return len(self.channel_name_flat_list)

    #----------------------------------------------------------------------
    def columnCount(self, parent=QModelIndex()):
        """"""

        return len(self.col_name_list)

    #----------------------------------------------------------------------
    def data(self, index, role=QtCore.Qt.DisplayRole):
        """"""

        row = index.row()
        col_key = FILTER_TABLE_COLUMN_HANDLE_LIST[index.column()]

        if ( not index.isValid() ) or \
           ( not (0 <= row < self.rowCount()) ):
            return None

        if role == QtCore.Qt.DisplayRole:
            value = getattr(self._filter_list[row], col_handle)
            return value
        else:
            return None



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
