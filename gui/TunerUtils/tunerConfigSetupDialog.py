#! /usr/bin/env python

# TODO
# *) add default visible column list separate for group-based & channel-based
# *) add ability to remove groups/channels in config setup
# *) add ability to move rows
# *) allow group/ungroup in config setup
# *) allow rename of group in channel-based view, leading to different grouping

import sip
sip.setapi('QString', 2)
sip.setapi('QVariant', 2)

import sys, os
from copy import copy
import types
import numpy as np
from datetime import datetime
from time import time, strftime, localtime
import h5py

from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import (SIGNAL, QObject, QSettings)
from PyQt4.QtGui import (QApplication, QDialog, QStandardItem,
     QStandardItemModel, QSortFilterProxyModel, QAbstractItemView,
     QAction, QIcon, QMenu, QInputDialog)

import aphla as ap
if ap.machines._lat is None:
    ap.initNSLS2V2()

from tunerModels import (ConfigChannel, getuserinfo, 
                         TreeItem, TreeModel, TunerConfigSetupBaseModel,
                         TunerConfigSetupTableModel, TunerConfigSetupTreeModel)
from ui_tunerConfigSetupDialog import Ui_Dialog
import config as const
from config import (TUNER_CLIENT_HDF5_FILEPATH, TUNER_CLIENT_SQLITE_FILEPATH)
from aphla.gui import channelexplorer
from aphla.gui.utils.tictoc import tic, toc

#HOME = os.path.expanduser('~')
#HLA_MACHINE = os.environ.get('HLA_MACHINE', None)

#TUNER_CLIENT_HDF5_FILEPATH = os.path.join(HOME,'.hla', HLA_MACHINE, 
                                          #'tuner_client.h5')
#TUNER_CLIENT_SQLITE_FILEPATH = os.path.join(HOME,'.hla', HLA_MACHINE, 
                                            #'tuner_client.db')

########################################################################
class TunerConfigSetupModel(QObject):
    """"""

    #----------------------------------------------------------------------
    def __init__(self, settings=None):
        """Constructor"""
        
        QObject.__init__(self)

        self.settings = settings
        
        self.base_model = TunerConfigSetupBaseModel()
        self.table_model = TunerConfigSetupTableModel(base_model=self.base_model)
        self.tree_model = TunerConfigSetupTreeModel(
            self.base_model.all_col_name_list, base_model=self.base_model)
        
        
        #self.col_name_list = const.ALL_COL_NAMES_CONFIG_SETUP[:]
        #self.group_level_col_list = const.GROUP_LEVEL_COL_LIST[:]
        #self.group_level_col_list.remove(const.COL_GROUP_NAME)
        #self.group_level_col_list = list(np.intersect1d(
            #np.array(self.group_level_col_list),
            #np.array(const.ALL_COL_NAMES_CONFIG_SETUP) ) )
        #self.channel_level_col_list = const.CHANNEL_LEVEL_COL_LIST[:]
        ##self.channel_level_col_list.remove(const.COL_CHANNEL_NAME)
        #self.channel_level_col_list = list(np.intersect1d(
            #np.array(self.channel_level_col_list),
            #np.array(const.ALL_COL_NAMES_CONFIG_SETUP) ) )
        
        #self.setHorizontalHeaderLabels(self.col_name_list)
        #self.setColumnCount(len(self.col_name_list))
        #self.removeRows(0,self.rowCount()) # clear contents

        #self.output = {}
        self.output = None
        
    #----------------------------------------------------------------------
    def _prepareOutput(self, accepted):
        """"""
        
        if accepted:
            #self.output = {'name':self.name,
                           #'description':self.description,
                           #'channel_group_list':self.channel_group_list}
            self.output = self.base_model
        else:
            #self.output = {}
            self.output = None
        
    #----------------------------------------------------------------------
    def create_new_user_id_in_HDF5(self, user_ids, new_user_id_str,
                                   ip_str, mac_str, username,
                                   compression_type='gzip'):
        """"""

        h5zip = compression_type
        str_type = h5py.new_vlen(str)

        user_id = user_ids.create_group(new_user_id_str)
        user_id.create_dataset('ip_str', (1,), data=ip_str,
                               dtype=str_type, compression=h5zip)
        user_id.create_dataset('mac_str', (1,), data=mac_str,
                               dtype=str_type, compression=h5zip)
        user_id.create_dataset('username', (1,), data=username,
                               dtype=str_type, compression=h5zip)
        last_user_record_id = 0
        user_id.create_dataset('last_user_record_id', (1,),
                               data=last_user_record_id, compression=h5zip)
        
        return user_id, last_user_record_id
        
    #----------------------------------------------------------------------
    def save_hdf5(self):
        """"""
        
        b = self.base_model
        
        flat_channel_name_list = [name.encode('ascii') for name in b.k_channel_name]
        ip_str, mac_str, username = b.userinfo

        if h5py.version.version_tuple[:3] < (2,1,1):
            b.config_name = b.config_name.encode('ascii')
            b.description = b.description.encode('ascii')
            b.appended_descriptions = b.appended_descriptions.encode('ascii')
        
        f = h5py.File(TUNER_CLIENT_HDF5_FILEPATH,'a')
        h5zip = 'gzip'
        str_type = h5py.new_vlen(str)
        
        if not 'user_ids' in f.keys():
            user_ids = f.create_group('user_ids')
            this_user_id = -1
            this_user_id_str = str(this_user_id)
            user_id, last_user_record_id = \
                self.create_new_user_id_in_HDF5(user_ids, this_user_id_str,
                                                ip_str, mac_str, username,
                                                compression_type=h5zip)
            
            last_record_id = 0
            f.create_dataset('last_record_id', (1,), data=last_record_id,
                             compression=h5zip)
        else:
            user_ids = f['user_ids']
            this_user_id_str = [k for (k,v) in user_ids.iteritems()
                                if v['ip_str'][0]==ip_str 
                                and v['mac_str'][0]==mac_str
                                and v['username'][0]==username]
            if this_user_id_str == []: # No match found in existing user ids
                min_user_id = min( 0, min([int(k) for k in user_ids.iterkeys()]) )
                this_user_id = min_user_id - 1
                this_user_id_str = str(this_user_id)
                user_id, last_user_record_id = \
                    self.create_new_user_id_in_HDF5(user_ids, this_user_id_str,
                                                    ip_str, mac_str, username,
                                                    compression_type=h5zip)
            else:
                this_user_id_str = this_user_id_str[0]
                this_user_id = int(this_user_id_str)
                user_id = user_ids[this_user_id_str]
                last_user_record_id = user_id['last_user_record_id'][()]

            last_record_id = f['last_record_id'][()]
            
        last_record_id += 1
        this_record = f.create_group(str(last_record_id))
        del f['last_record_id']
        f['last_record_id'] = last_record_id
        
        this_record.create_dataset('user_id', (1,), data=this_user_id, 
                                   compression=h5zip)
        last_user_record_id += 1
        this_record.create_dataset('user_record_id', (1,), data=last_user_record_id,
                                   compression=h5zip)
        del user_id['last_user_record_id']
        user_id['last_user_record_id'] = last_user_record_id
        
        this_record.create_dataset('command', (1,), data='insert config',
                                   dtype=str_type, compression=h5zip)
        
        args = this_record.create_group('args')
            
        args.create_dataset('config_name', (1,), data=b.config_name, 
                            dtype=str_type, compression=h5zip)
        args.create_dataset('time_created', (1,), data=b.time_created, 
                            compression=h5zip)
        args.create_dataset('description', (1,), data=b.description,
                            dtype=str_type, compression=h5zip)
        args.create_dataset('appended_descriptions', (1,), 
                            data=b.appended_descriptions, dtype=str_type,
                            compression=h5zip)
        
        nChannels = len(flat_channel_name_list)
        args.create_dataset('flat_channel_name_list', (nChannels,),
                            data=flat_channel_name_list, dtype=str_type,
                            compression=h5zip)
        
        nGroups = len(b.group_name_list)
        g = args.create_group('grouped_ind_list')
        for (group_ind,group_name) in enumerate(b.group_name_list):
            index_list = b.grouped_ind_list[group_ind]
            dataset = g.create_dataset(group_name,(len(index_list),),
                                       data=index_list, compression=h5zip)
            
        f.close()
        
    #----------------------------------------------------------------------
    def load_hdf5(self, user_id, user_record_id):
        """"""
        
        f = h5py.File(TUNER_CLIENT_HDF5_FILEPATH,'r')
        
        
        #f['grouped_ind_list']['bpm']['ind_list'][:]
        #f['grouped_ind_list']['hcor']['ind_list'][:]
        
        f.close()
        
        
    #----------------------------------------------------------------------
    def importNewChannels(self, selected_channels, channelGroupInfo):
        """"""
        
        #str_format_index = const.ENUM_STR_FORMAT
        #prop_name_index = const.ENUM_PROP_NAME
        
        #group_col_ind = self.getColumnIndex(const.COL_GROUP_NAME)
        
        #nRows = self.rowCount()
        
        elemName_list = [elem.name for (elem,fieldName) in selected_channels]
        channelName_list = [elem.name+'.'+fieldName
                            for (elem,fieldName) in selected_channels]
        
        if channelGroupInfo == {}:
            channelGroupName_list = channelName_list[:]
            weight_list = [float('nan') for c in channelName_list]
        else:
            channelGroupName_list = [channelGroupInfo['name'] for c in channelName_list]
            weight_list = [channelGroupInfo['weight'] for c in channelName_list]
        step_size_list = weight_list[:]
        
        new_lists_dict = {'group_name': channelGroupName_list,
                          'channel_name': channelName_list,
                          'weight': weight_list,
                          'step_size': step_size_list}
        tStart = tic()
        self.base_model.appendChannels(new_lists_dict)
        print 'before reset', toc(tStart)
        self.table_model.resetModel()
        self.tree_model.resetModel()
        print 'after reset', toc(tStart)
        
        ## Temporarily block signals emitted from the model
        #self.blockSignals(True)
        
        #channelGroupList = []
        #if channelGroupInfo == {}:
            #for (elemName,chName) in zip(elemName_list,channelName_list):
                #default_channel_group_name = elemName
                #default_channel_group_weight = 0.
                #channelGroup = {'name':default_channel_group_name,
                                #'weight':default_channel_group_weight,
                                #'channel_name_list': [chName]}
                #channelGroupList.append(channelGroup)
                #self.channel_group_list.append(channelGroup)
                
            
                
        #else:
            #channelGroup = {'name': channelGroupInfo['name'],
                            #'weight': channelGroupInfo['weight'],
                            #'channel_name_list': channelName_list,
                            #}
            #channelGroupList.append(channelGroup)
            #self.channel_group_list.append(channelGroup)
            
            
            #self.setRowCount(nRows + 1) # Add 1 row
            #nRows = self.rowCount()
            #row_index = nRows - 1 # last row index
            
            #groupItem = QStandardItem(channelGroup['name'])
            #groupItem.setFlags(groupItem.flags() |
                               #QtCore.Qt.ItemIsEditable) # Make the item editable
                        
            #for c in self.group_level_col_list:
                #col_index = self.getColumnIndex(c)
                #cc = const.DICT_COL[c]
                #str_format = cc[str_format_index]
                #prop_val = channelGroup[ cc[prop_name_index] ]
                #item = QStandardItem(('{0'+str_format+'}').format(prop_val))
                #if c in const.EDITABLE_COL_NAME_LIST:
                    #item.setFlags(item.flags() |
                                  #QtCore.Qt.ItemIsEditable) # Make the item editable
                #else:
                    #item.setFlags(item.flags() &
                                  #~QtCore.Qt.ItemIsEditable) # Make the item NOT editable
                    
                #self.setItem(row_index, col_index, item)
                #for child_index in range(len(channelGroup['channel_name_list'])):
                    #groupItem.setChild(child_index, col_index, item.clone())
            
            #for (child_index, chName) in enumerate(channelGroup['channel_name_list']):
                #elemName, fieldName = chName.split('.')
                #elem = ap.getElements(elemName)[0]
                #channelNameItem = QStandardItem(chName)
                #channelNameItem.setFlags(channelNameItem.flags() & 
                                         #~QtCore.Qt.ItemIsEditable) # Make the item NOT editable
                #groupItem.setChild(child_index, group_col_ind, channelNameItem)
                
                #for c in self.channel_level_col_list:
                    #col_index = self.getColumnIndex(c)
                    #cc = const.DICT_COL[c]
                    #str_format = cc[str_format_index]
                    #prop_name =  cc[prop_name_index]
                    #if prop_name not in ('pvrb','pvsp','channel_name','field'):
                        #value = getattr(elem,prop_name)
                    #else:
                        #if prop_name == 'pvrb':
                            #pvrb, pvsp = self._getpvs(chName)
                            #value = pvrb
                        #elif prop_name == 'pvsp':
                            #pvrb, pvsp = self._getpvs(chName)
                            #value = pvsp
                        #elif prop_name == 'channel_name':
                            #value = chName
                        #elif prop_name == 'field':
                            #value = fieldName
                        #else:
                            #raise NotImplementedError(prop_name)
                    
                    #if str_format != 'timestamp':
                        #if (value == None) or isinstance(value,list) \
                           #or isinstance(value,tuple):
                            #str_format = ':s'
                        #else:
                            #pass
                        #item = QStandardItem(('{0'+str_format+'}').format(value))
                    #else:
                        #if value is None:
                            #time_str = 'None'
                        #else:
                            #time_str = datetime.fromtimestamp(value).isoformat()
                        #item = QStandardItem(time_str)
                    
                    #item.setFlags(item.flags() &
                                  #~QtCore.Qt.ItemIsEditable) # Make the item NOT editable
                    
                    #groupItem.setChild(child_index, col_index, item)
            
            #self.setItem(row_index, group_col_ind, groupItem)
            
            
            
        ## Re-enable the blocked signals emitted from the model
        #self.blockSignals(False)
        
        
        #self.emit(SIGNAL('modelUpdated'))           
        
        #self.updateGroupBasedModel(change_type='append',
                                   #channelGroupList=channelGroupList)
        
        
        
        
        
########################################################################
class TunerConfigSetupView(QDialog, Ui_Dialog):
    """"""
    
    #----------------------------------------------------------------------
    def __init__(self, model, isModal, parentWindow, settings = None):
        """Constructor"""
        
        QDialog.__init__(self, parent=parentWindow)
                
        self.setupUi(self)
        
        self.setWindowFlags(QtCore.Qt.Window) # To add Maximize & Minimize buttons
        self.setModal(isModal)

        self.settings = settings
        
        self.radioButton_channel_based.setChecked(True)
        if self.radioButton_group_based.isChecked():
            self.stackedWidget.setCurrentWidget(self.page_tree)
        else:
            self.stackedWidget.setCurrentWidget(self.page_table)
        
        self.model = model
        
        self.table_proxyModel = QSortFilterProxyModel()
        self.table_proxyModel.setSourceModel(self.model.table_model)
        self.table_proxyModel.setDynamicSortFilter(False)
        #
        self.tree_proxyModel = QSortFilterProxyModel()
        self.tree_proxyModel.setSourceModel(self.model.tree_model)
        self.tree_proxyModel.setDynamicSortFilter(False)
        
        t = self.tableView
        t.setModel(self.table_proxyModel)
        t.setCornerButtonEnabled(True)
        t.setShowGrid(True)
        t.setSelectionMode(QAbstractItemView.ExtendedSelection)
        t.setSelectionBehavior(QAbstractItemView.SelectItems)
        t.setAlternatingRowColors(True)
        t.setSortingEnabled(False)
        horizHeader = t.horizontalHeader()
        horizHeader.setSortIndicatorShown(False)
        horizHeader.setStretchLastSection(False)
        horizHeader.setMovable(False)
        #
        t = self.treeView
        t.setModel(self.tree_proxyModel)
        t.setItemsExpandable(True)
        t.setRootIsDecorated(True)
        t.setAllColumnsShowFocus(False)
        t.setHeaderHidden(False)
        t.setSortingEnabled(False)
        horizHeader = t.header()
        horizHeader.setSortIndicatorShown(False)
        horizHeader.setStretchLastSection(False)
        horizHeader.setMovable(False)
        self._expandAll_and_resizeColumn()
        t.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.actionGroupChannels = QAction(QIcon(), 'Group channels', self.treeView)
        self.actionUngroupChannels = QAction(QIcon(), 'Ungroup channels', self.treeView)
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
    
        self.loadViewSizeSettings()

        self.visible_col_key_list = self.settings._visible_col_key_list
        desired_visible_col_full_name_list = [
                    const.PROP_DICT[k][const.ENUM_FULL_DESCRIP_NAME]
                    for k in self.visible_col_key_list]        
        self.on_column_selection_change(desired_visible_col_full_name_list,
                                        force_visibility_update=True)
        
    #----------------------------------------------------------------------
    def debug(self):
        """"""
        
        #self.treeView.setVisible(False)
        ##self.model.table_model.reset()
        #self.proxyModel.setSourceModel(self.model.table_model)
        #self.treeView.setVisible(True)
        
    #----------------------------------------------------------------------
    def saveViewSizeSettings(self):
        """"""
        
        settings = self.settings
        
        settings._position = self.geometry()
        settings._splitter_left_right_sizes = self.splitter_left_right.sizes()
        settings._splitter_top_bottom_sizes = self.splitter_top_bottom.sizes()
        
        settings.saveViewSizeSettings()
        
        
    #----------------------------------------------------------------------
    def loadViewSizeSettings(self):
        """"""
        
        settings = self.settings
        
        rect = self.settings._position
        if rect is None:
            rect = QRect(0,0,self.sizeHint().width(),self.sizeHint().height())
        self.setGeometry(rect)
        
        splitter_left_right_sizes = self.settings._splitter_left_right_sizes
        if splitter_left_right_sizes is None:
            # Adjust left-right splitter so that left widget takes max width
            # and right widget takes min width
            # QSplitter::setStretchFactor(int index, int stretch)
            self.splitter_left_right.setStretchFactor(0,1)
            self.splitter_left_right.setStretchFactor(1,0)
        else:
            self.splitter_left_right.setSizes(splitter_left_right_sizes)
        
        splitter_top_bottom_sizes = self.settings._splitter_top_bottom_sizes
        if splitter_top_bottom_sizes is None:
            # Adjust top-bottom splitter so that top widget takes max heigth
            # and bottom widget takes min height
            # QSplitter::setStretchFactor(int index, int stretch)
            self.splitter_top_bottom.setStretchFactor(0,1)
            self.splitter_top_bottom.setStretchFactor(1,0)
        else:
            self.splitter_top_bottom.setSizes(splitter_top_bottom_sizes)
            
    
    #----------------------------------------------------------------------
    def closeEvent(self, event):
        """"""
        
        self.saveViewSizeSettings()
        
        event.accept()
        
    #----------------------------------------------------------------------
    def accept(self):
        """"""
        
        base_model = self.model.base_model
        base_model.time_created = time() # current time in seconds from Epoch
        base_model.config_name = self.lineEdit_config_name.text()
        #base_model.username
        base_model.description = self.textEdit.toPlainText()
        #base_model.appended_descriptions
    
        saveFileFlag = self.checkBox_save_config_to_file.isChecked()
        if saveFileFlag:
            self.model.save_hdf5()
        
        accepted = True
        self.emit(SIGNAL('prepareOutput'),accepted)
        
        self.saveViewSizeSettings()
        
        QDialog.accept(self)
        
    
    #----------------------------------------------------------------------
    def reject(self):
        """"""
        
        accepted = False
        self.emit(SIGNAL('prepareOutput'),accepted)
        
        self.saveViewSizeSettings()

        QDialog.reject(self) # will hide the dialog
            
    #----------------------------------------------------------------------
    def get_visible_column_order(self):
        """"""
        
        return [self.model.base_model.all_col_key_list.index(key)
                for key in self.visible_col_key_list]
    
    #----------------------------------------------------------------------
    def on_column_selection_change(self, new_visible_col_full_name_list,
                                   force_visibility_update=False):
        """"""
        
        current_visible_col_full_name_list = [const.PROP_DICT[col_key][const.ENUM_FULL_DESCRIP_NAME]
                                              for col_key in self.visible_col_key_list]
        
        if (not force_visibility_update) and \
           (new_visible_col_full_name_list == current_visible_col_full_name_list):
            return

        self.visible_col_key_list = [const.ALL_PROP_KEYS[const.FULL_DESCRIP_NAME_LIST.index(name)]
                                     for name in new_visible_col_full_name_list]
        
        visible_column_order = self.get_visible_column_order()
        
        for horizHeader in [self.treeView.header(), self.tableView.horizontalHeader()]:
            for (i,col_logical_ind) in enumerate(visible_column_order):
                new_visual_index = i
                current_visual_index = horizHeader.visualIndex(col_logical_ind)
                horizHeader.moveSection(current_visual_index,
                                        new_visual_index)
            for i in range(len(const.ALL_PROP_KEYS)):
                if i not in visible_column_order:
                    horizHeader.hideSection(i)
                else:
                    horizHeader.showSection(i)
    
    #----------------------------------------------------------------------
    def on_view_base_change(self):
        """"""
        
        sender = self.sender()
        
        if sender == self.radioButton_group_based:
            self.stackedWidget.setCurrentWidget(self.page_tree)
        elif sender == self.radioButton_channel_based:
            self.stackedWidget.setCurrentWidget(self.page_table)
        else:
            raise ValueError('Unexpected sender: '+str(sender))
        
        
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
        
        
    #----------------------------------------------------------------------
    def _expandAll_and_resizeColumn(self):
        """"""
        
        self.treeView.expandAll()
        self.treeView.resizeColumnToContents(0)
        
    #----------------------------------------------------------------------
    def updateProxyModels(self):
        """"""
        
        self.tree_proxyModel.setSourceModel(self.model.tree_model)        
        
    #----------------------------------------------------------------------
    def _updateProxyModel(self):
        """
        This function is needed to synchronize the proxy
        model and the underlying model. Since I block signals
        while I change the data in the underlying model, 
        automatic update to the proxy model is disabled.
        This is why I need to reset the underlying model with
        this function to reflect any change in the underlying
        model into the proxy model. Otherwise, you will
        not see change in the view.
        """
        
        self.proxyModel.setSourceModel(self.model)
        
        
########################################################################
class TunerConfigSetupAppSettings():
    """"""
    
    #----------------------------------------------------------------------
    def __init__(self):
        """
        Attribute naming convetion:
         1) Double underscore prefix means attributes that should not be
            directly accessed outside of this class.
         2) Single underscore prefix means settings properties related to view size.
         3) No-underscored prefix means settings properties related to miscellaneous.
        """
        
        self.__settings = QSettings('HLA','TunerConfigSetupDialog')
        
        self.loadViewSizeSettings()
        self.loadMiscellaneousSettings()
        
    #----------------------------------------------------------------------
    def loadViewSizeSettings(self):
        """"""
        
        self.__settings.beginGroup('viewSize')
        
        self._position = self.__settings.value('position')

        self._splitter_left_right_sizes = self.__settings.value('splitter_left_right_sizes')
        if self._splitter_left_right_sizes is not None:
            self._splitter_left_right_sizes = [int(s) for s in self._splitter_left_right_sizes] # convert from string to int
          
        self._splitter_top_bottom_sizes = self.__settings.value('splitter_top_bottom_sizes')  
        if self._splitter_top_bottom_sizes is not None:
            self._splitter_top_bottom_sizes = [int(s) for s in self._splitter_top_bottom_sizes] # convert from string to int
        
        self.__settings.endGroup()
        
    #----------------------------------------------------------------------
    def loadMiscellaneousSettings(self):
        """"""
        
        self.__settings.beginGroup('miscellaneous')
        
        self._visible_col_key_list = self.__settings.value('visible_col_key_list')
        if self._visible_col_key_list is None:
            self._visible_col_key_list = const.DEFAULT_VISIBLE_COL_KEYS_FOR_CONFIG_SETUP
        
        self.__settings.endGroup()
        
    #----------------------------------------------------------------------
    def saveViewSizeSettings(self):
        """"""
        
        self.__settings.beginGroup('viewSize')
        
        self.__settings.setValue('position',self._position)
        self.__settings.setValue('splitter_left_right_sizes',self._splitter_left_right_sizes)
        self.__settings.setValue('splitter_top_bottom_sizes',self._splitter_top_bottom_sizes)
        
        self.__settings.endGroup()
        
    #----------------------------------------------------------------------
    def saveMiscellaneousSettings(self):
        """"""
        
        self.__settings.beginGroup('miscellaneous')

        self.__settings.setValue('visible_col_key_list', self._visible_col_key_list)
        
        self.__settings.endGroup()        
        

            
########################################################################
class TunerConfigSetupApp(QObject):
    """"""

    #----------------------------------------------------------------------
    def __init__(self, isModal, parentWindow):
        """Constructor"""
        
        QObject.__init__(self)
        
        self.settings = TunerConfigSetupAppSettings()
        
        self._initModel()
        self._initView(isModal, parentWindow)
        
        self.connect(self.view.pushButton_add_from_GUI_selector,
                     SIGNAL('clicked()'), self._launchChannelExplorer)
        self.connect(self, SIGNAL('channelsSelected'),
                     self._askChannelGroupNameAndWeight)
        self.connect(self, SIGNAL('channelGroupInfoObtained'),
                     self.model.importNewChannels)
        #self.connect(self.model, SIGNAL('modelUpdated'),
                     #self.view._updateProxyModel)
        #self.connect(self.model, SIGNAL('modelUpdated'),
                     #self.view._expandAll_and_resizeColumn)
        
        self.connect(self.view, SIGNAL('prepareOutput'),
                     self.model._prepareOutput)
        
        self.connect(self.view.radioButton_channel_based, SIGNAL('clicked()'),
                     self.view.on_view_base_change)
        self.connect(self.view.radioButton_group_based, SIGNAL('clicked()'),
                     self.view.on_view_base_change)

        
    #----------------------------------------------------------------------
    def _initModel(self):
        """"""
        
        self.model = TunerConfigSetupModel(settings=self.settings)
        
    #----------------------------------------------------------------------
    def _initView(self, isModal, parentWindow):
        """"""
        
        self.view = TunerConfigSetupView(self.model, isModal, parentWindow,
                                         settings=self.settings)
        
    #----------------------------------------------------------------------
    def _launchChannelExplorer(self):
        """"""
                
        result = channelexplorer.make(modal=True, init_object_type='channel',
                                      can_modify_object_type=False,
                                      output_type=channelexplorer.TYPE_OBJECT,
                                      caller='aplattuner', debug=False)
        
        selected_channels = result['dialog_result']
        
        tStart = tic()
        
        if selected_channels != []:
            self.emit(SIGNAL('channelsSelected'), selected_channels)
        
        
    #----------------------------------------------------------------------
    def _askChannelGroupNameAndWeight(self, selected_channels):
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
        
        self.emit(SIGNAL("channelGroupInfoObtained"), selected_channels,
                  channelGroupInfo)

#----------------------------------------------------------------------
def make(isModal=True, parentWindow=None):
    """"""
    
    app = TunerConfigSetupApp(isModal, parentWindow)
    
    if isModal:
        app.view.exec_()
    else:
        app.view.show()
    
    return app


#----------------------------------------------------------------------
def isCothreadUsed():
    """"""

    g = copy(globals())
    
    using_cothread = False
    for (k,v) in g.iteritems():
        if isinstance(v, types.ModuleType):
            if v.__name__ == 'cothread':
                using_cothread = True
                break
            
    return using_cothread
    
#----------------------------------------------------------------------
def main(args):
    """"""

    using_cothread = isCothreadUsed()
    
    if using_cothread:
        # If Qt is to be used (for any GUI) then the cothread library needs to be informed,
        # before any work is done with Qt. Without this line below, the GUI window will not
        # show up and freeze the program.
        # Note that for a dialog box to be modal, i.e., blocking the application
        # execution until user input is given, you need to set the input
        # argument "user_timer" to be True.        
        #cothread.iqt(use_timer = True)
        cothread.iqt()
    else:
        qapp = QApplication(args)

    isModal = True
    app = make(isModal=isModal)
    
    if using_cothread:
        cothread.WaitForQuit()
        print app.model.output        
    else:
        if not isModal:
            exit_status = qapp.exec_()
        else:
            exit_status = 0
        print app.model.output
        sys.exit(exit_status)
    
#----------------------------------------------------------------------    
if __name__ == "__main__" :
    main(sys.argv)
    