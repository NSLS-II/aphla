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
import traceback

from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import (SIGNAL, QObject, QSettings)
from PyQt4.QtCore import Qt
from PyQt4.QtGui import (qApp, QApplication, QDialog, QStandardItem,
     QStandardItemModel, QSortFilterProxyModel, QAbstractItemView,
     QAction, QIcon, QMenu, QInputDialog, QKeySequence, QItemSelection,
     QItemSelectionModel, QItemSelectionRange, QTableView, QFileDialog,
     QMessageBox)

import aphla as ap
if ap.machines._lat is None:
    ap.initNSLS2V2()

from tunerModels import (TreeItem, TreeModel, TunerConfigSetupBaseModel,
                         TunerConfigSetupTableModel, TunerConfigSetupTreeModel)
from ui_tunerConfigSetupDialog import Ui_Dialog
import config as const
from config import (CLIENT_DATA_FOLDERPATH, SERVER_DATA_FOLDERPATH,
                    MAIN_DB_FILENAME, LAST_SYNCED_MAIN_DB_FILENAME,
                    CLIENT_DELTA_DB_FILENAME, SERVER_DELTA_DB_FILENAME)
from aphla.gui import channelexplorer
from tunerdb import (TunerHDF5Manager, TunerTextFileManager,
                     TunerDeltaDatabase, TunerMainDatabase)
from aphla.gui.utils.tictoc import tic, toc


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
    def getConfigDataForTextFile(self, column_selection_dict):
        """"""

        b = self.base_model
        
        
        nCols = sum(column_selection_dict.values())
        
        flat_channel_name_list = [name for name in b.k_channel_name]
        nRows = len(flat_channel_name_list)
        
        data = np.empty((nRows,nCols),dtype=np.object)
        
        col_ind = 0
        
        if column_selection_dict['group_names']:
            flat_group_name_list = b.k_group_name
            data[:,col_ind] = flat_group_name_list
            col_ind += 1

        data[:,col_ind] = flat_channel_name_list
        col_ind += 1
        
        weight_list = b.k_weight
        data[:,col_ind] = ['{0:.16g}'.format(w) for w in weight_list]
        col_ind += 1
        
        if column_selection_dict['step_sizes']:
            step_size_list = b.k_step_size
            data[:,col_ind] = ['{0:.16g}'.format(s) for s in step_size_list]
        
        return data
        
    #----------------------------------------------------------------------
    def saveConfigToHDF5(self, save_filepath):
        """"""
        
        b = self.base_model
        
        flat_channel_name_list = [name.encode('ascii') for name in b.k_channel_name]

        if h5py.version.version_tuple[:3] < (2,1,1):
            b.config_name = b.config_name.encode('ascii')
            b.description = b.description.encode('ascii')
            b.appended_descriptions = b.appended_descriptions.encode('ascii')

        record = {}
        record['ip_str'], record['mac_str'], record['username'] = b.userinfo
        record['config_name'] = b.config_name
        record['time_created'] = b.time_created
        record['description'] = b.description
        record['appended_descriptions'] = b.appended_descriptions
        record['flat_channel_name_list'] = flat_channel_name_list
        record['group_name_list'] = b.group_name_list
        record['grouped_ind_list'] = b.grouped_ind_list
        record['weight_list'] = b.k_weight
        record['step_size_list'] = b.k_step_size
        record['indiv_ramp_table'] = [np.nan for name in b.k_channel_name]
            
        f = TunerHDF5Manager(save_filepath, mode='w',create_fresh=True)
        f.createConfigRecordHDF5(record, close_on_exit=True)
        
    #----------------------------------------------------------------------
    def saveConfigToDB(self):
        """"""

        b = self.base_model
        
        record = {}
        record['ip_str'], record['mac_str'], record['username'] = b.userinfo
        record['config_name'] = b.config_name
        record['time_created'] = b.time_created
        record['description'] = b.description
        record['appended_descriptions'] = b.appended_descriptions
        record['flat_channel_name_list'] = [name for name in b.k_channel_name]
        record['group_name_list'] = b.group_name_list
        record['grouped_ind_list'] = b.grouped_ind_list
        record['weight_list'] = b.k_weight
        record['step_size_list'] = b.k_step_size
        record['indiv_ramp_table'] = [None for name in b.k_channel_name]
        
        client_delta_filepath = os.path.join(CLIENT_DATA_FOLDERPATH,
                                             CLIENT_DELTA_DB_FILENAME)        
        client_delta_db = TunerDeltaDatabase(filepath=client_delta_filepath)
        client_delta_db.insertConfigRecordOnClient(record)
            
        
    #----------------------------------------------------------------------
    def importNewChannelsFromSelector(self, selected_channels, channelGroupInfo):
        """"""
        
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

        self.updateModels(new_lists_dict)
        
    #----------------------------------------------------------------------
    def importNewChannelsFromTextFile(self, list_of_lists):
        """"""
        
        channelGroupName_list, channelName_list, weight_list, step_size_list = \
            zip(*list_of_lists)
        
        new_lists_dict = {'group_name': channelGroupName_list,
                          'channel_name': channelName_list,
                          'weight': weight_list,
                          'step_size': step_size_list}
        
        self.updateModels(new_lists_dict)
        
    #----------------------------------------------------------------------
    def updateModels(self, new_lists_dict):
        """"""

        tStart = tic()
        self.base_model.appendChannels(new_lists_dict)
        print 'before reset', toc(tStart)
        self.table_model.resetModel()
        self.tree_model.resetModel()
        print 'after reset', toc(tStart)
        
        
        
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
        
        self.comboBox_view.setEditable(False)
        self.GROUP_BASED_VIEW = self.comboBox_view.findText('Group-based View')
        self.CHANNEL_BASED_VIEW = self.comboBox_view.findText('Channel-based View')
        self.comboBox_view.setCurrentIndex(self.CHANNEL_BASED_VIEW)
        if self.comboBox_view.currentIndex() == self.GROUP_BASED_VIEW:
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
        
        self._initContextMenuItems()
        self.clipboard = np.array([])
        
        
    #----------------------------------------------------------------------
    def debug(self):
        """"""
        
        #self.treeView.setVisible(False)
        ##self.model.table_model.reset()
        #self.proxyModel.setSourceModel(self.model.table_model)
        #self.treeView.setVisible(True)
        
    #----------------------------------------------------------------------
    def _initContextMenuItems(self):
        """"""
        
        t = self.tableView
        
        t.actionCopySelectedItemsTexts = QAction(QIcon(), 'copy', t)
        
        t.actionCopySelectedItemsTexts.setShortcut(
            QKeySequence(Qt.ControlModifier + Qt.Key_C) )
        self.addAction(t.actionCopySelectedItemsTexts)
        ''' This addAction is critical for the shortcut to always work.
        If you only do addAction for the context menu below, the
        shortcut will not work, because the widget to which this
        action is added will be listening for key events.
        '''
        
        self.connect(t.actionCopySelectedItemsTexts, SIGNAL('triggered()'),
                     self.copySelectedItemsTexts)
        
        t.setContextMenuPolicy(Qt.CustomContextMenu)
        t.contextMenu = QMenu()
        t.contextMenu.addAction(t.actionCopySelectedItemsTexts)
        t.contextMenu.setDefaultAction(t.actionCopySelectedItemsTexts)
        
        ###
        
        #t = self.treeView
        
    #----------------------------------------------------------------------
    def copySelectedItemsTexts(self):
        """"""
        
        action = self.sender()
        view = action.parent()
        
        if not isinstance(view, QTableView):
            raise TypeError('Only implemented for TableView')
        
        proxyItemSelectionModel = view.selectionModel()
        proxyItemSelection = proxyItemSelectionModel.selection()
        
        proxyMod = view.model()
        
        proxyItemSelectionCount = proxyItemSelection.count()
        if proxyItemSelectionCount == 0:
            return
        else:
            h = view.horizontalHeader()
            v = view.verticalHeader()
            all_inds = []
            all_rows = []
            all_cols = []
            for sel in proxyItemSelection:
                z = [( ind, v.visualIndex(ind.row()), h.visualIndex(ind.column()) )
                     for ind in sel.indexes() if not h.isSectionHidden(ind.column())]
                inds, rows, cols = zip(*z)
                all_inds.extend(inds)
                all_rows.extend(rows)
                all_cols.extend(cols)
            nRows = max(all_rows) - min(all_rows) + 1
            nCols = max(all_cols) - min(all_cols) + 1
            min_row = min(all_rows)
            min_col = min(all_cols)
            all_rows = [row - min_row for row in all_rows]
            all_cols = [col - min_col for col in all_cols]
            self.clipboard = np.empty((nRows,nCols),dtype=np.object)
            self.clipboard.fill('')
            for (ind,row,col) in zip(all_inds,all_rows,all_cols):
                self.clipboard[row,col] = str( proxyMod.data(ind) )
            #print self.clipboard
            
            # Find maximum string length for each column
            str_width_list = [len( max(a,key=len) )
                              for a in self.clipboard.transpose()]
            
            formatted_line_list = [[] for i in range(nRows)]
            for (i,row) in enumerate(self.clipboard):
                formatted_line_list[i] = ' '.join(
                    [s.ljust(w) for (s,w) in zip(row,str_width_list)] )

            system_clipboard = qApp.clipboard()
            system_clipboard.setText('\n'.join(formatted_line_list))
            
        
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
            # Adjust left-right splitter so that right widget takes max width
            # and left widget takes min width
            # QSplitter::setStretchFactor(int index, int stretch)
            self.splitter_left_right.setStretchFactor(0,0)
            self.splitter_left_right.setStretchFactor(1,1)
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
        base_model.description = self.textEdit.toPlainText()
        
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
    def on_view_base_change(self, current_comboBox_index):
        """"""
        
        if current_comboBox_index == self.GROUP_BASED_VIEW:
            self.stackedWidget.setCurrentWidget(self.page_tree)
        elif current_comboBox_index == self.CHANNEL_BASED_VIEW:
            self.stackedWidget.setCurrentWidget(self.page_table)
        else:
            raise ValueError('Unexpected current ComboBox index: '+
                             str(current_comboBox_index))
        
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
        
        self.starting_directory_path = os.getcwd()
        
        self._initModel()
        self._initView(isModal, parentWindow)
        
        self.connect(self.view.pushButton_import,
                     SIGNAL('clicked()'), self._importConfigData)
        self.connect(self.view.pushButton_export,
                     SIGNAL('clicked()'), self._exportConfigData)
        
        self.connect(self.view, SIGNAL('prepareOutput'),
                     self.model._prepareOutput)
        
        self.connect(self.view.comboBox_view, 
                     SIGNAL('currentIndexChanged(int)'),
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
    def _importConfigData(self):
        """"""
        
        import_type = self.view.comboBox_import.currentText()
        
        if import_type == 'Channel Explorer':
            self._launchChannelExplorer()
        elif import_type == 'Database':
            raise NotImplementedError(import_type)
        elif import_type == 'Text File':

            caption = 'Load Tuner Configuration Data from Text File'
            text_files_filter_str = 'Text files (*.txt)'
            all_files_filter_str = 'All files (*)'
            filter_str = ';;'.join([text_files_filter_str, all_files_filter_str])
            #selected_filter_str = text_files_filter_str
            filepath = QFileDialog.getOpenFileName(
                caption=caption, directory=self.starting_directory_path,
                filter=filter_str)
            
            if not filepath:
                return
            
            self.starting_directory_path = os.path.dirname(filepath)
            
            m = TunerTextFileManager(load=True, filepath=filepath)
            m.exec_()
            data = m.loadConfigTextFile()
            
            if data is not None:
                self.model.importNewChannelsFromTextFile(data)

        elif import_type == 'HDF5 File':
            raise NotImplementedError(import_type)
        else:
            raise ValueError('Unexpected import_type selected: '+str(import_type))

    #----------------------------------------------------------------------
    def _exportConfigData(self):
        """"""
        
        msgBox = QMessageBox()
        msgBox.setIcon(QMessageBox.Information)
        
        import_type = self.view.comboBox_export.currentText()
        
        if import_type == 'Database':
            
            self.model.saveConfigToDB()
            msgBox.setText('Config successfully saved to database.')
            
        elif import_type == 'Text File':
            
            caption = 'Save Tuner Configuration Data to Text File'
            text_files_filter_str = 'Text files (*.txt)'
            all_files_filter_str = 'All files (*)'
            filter_str = ';;'.join([text_files_filter_str, all_files_filter_str])
            #selected_filter_str = text_files_filter_str
            save_filepath = QFileDialog.getSaveFileName(
                caption=caption, directory=self.starting_directory_path,
                filter=filter_str)        
            if not save_filepath:
                return
        
            self.starting_directory_path = os.path.dirname(save_filepath)

            m = TunerTextFileManager(load=False, filepath=save_filepath)
            m.exec_()
            
            data = self.model.getConfigDataForTextFile(m.selection)
            
            m.saveConfigTextFile(data)

            msgBox.setText('Config successfully saved to Text file.')
            
        elif import_type == 'HDF5 File':
            
            caption = 'Save Tuner Configuration Data to HDF5 File'
            text_files_filter_str = 'HDF5 files (*.h5 *.hdf5)'
            all_files_filter_str = 'All files (*)'
            filter_str = ';;'.join([text_files_filter_str, all_files_filter_str])
            #selected_filter_str = text_files_filter_str
            save_filepath = QFileDialog.getSaveFileName(
                caption=caption, directory=self.starting_directory_path,
                filter=filter_str)        
            if not save_filepath:
                return
        
            self.starting_directory_path = os.path.dirname(save_filepath)
            
            self.model.saveConfigToHDF5(save_filepath)
            msgBox.setText('Config successfully saved to HDF5 file.')
        else:
            raise ValueError('Unexpected import_type selected: '+str(import_type))

        msgBox.exec_()
        
        
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
            selected_channels, channelGroupInfo = \
                self._askChannelGroupNameAndWeight(selected_channels)
            self.model.importNewChannelsFromSelector(selected_channels,
                                                     channelGroupInfo)
        
        
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
        
        return selected_channels, channelGroupInfo

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
    