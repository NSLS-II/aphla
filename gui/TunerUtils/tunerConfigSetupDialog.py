#! /usr/bin/env python

import sip
sip.setapi('QString', 2)
sip.setapi('QVariant', 2)

import sys, os
from copy import copy
import types
import numpy as np
from datetime import datetime

from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import SIGNAL, QObject
from PyQt4.QtGui import QApplication, QDialog, QStandardItem, \
     QStandardItemModel, QSortFilterProxyModel, QAbstractItemView, \
     QAction, QIcon, QMenu, QInputDialog

import aphla as ap
if ap.machines._lat is None:
    ap.initNSLS2V2()

from tunerModels import AbstractTunerConfigModel
from ui_tunerConfigSetupDialog import Ui_Dialog
import config as const
from aphla.gui import channelexplorer
#if __name__ == '__main__':
    #from ui_tunerConfigSetupDialog import Ui_Dialog
    
    #import config as const
    
    #from aphla.gui import channelexplorer 
    
#else:
    #from ui_tunerConfigSetupDialog import Ui_Dialog
    #import config as const
    #from aphla.gui import channelexplorer

########################################################################
class TunerConfigSetupModel(AbstractTunerConfigModel):
    """"""

    #----------------------------------------------------------------------
    def __init__(self, config_dict=None):
        """Constructor"""
        
        AbstractTunerConfigModel.__init__(
            self, config_dict=config_dict,
            col_name_list=const.ALL_COL_NAMES_CONFIG_SETUP)
        
        #self.SortRole = QtCore.Qt.UserRole
        
        #if init_tuner_config_dict is None:
            #self.name = ''
            #self.description = ''
        
            #self.channel_group_list = []
        #else:
            #key_list = ['name','description','channel_group_list']
            #for k in key_list:
                #setattr(self, k, init_tuner_config_dict[k])
            
        
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

        self.output = {}
        
    #----------------------------------------------------------------------
    def _prepareOutput(self, accepted):
        """"""
        
        if accepted:
            self.output = {'name':self.name,
                           'description':self.description,
                           'channel_group_list':self.channel_group_list}
        else:
            self.output = {}
            

    ##----------------------------------------------------------------------
    #def data(self, modelIndex, role):
        #"""
        #Reimplementation of QStandardItemModel's data()
        #The purpose is to allow sorting by numbers, not just by
        #default string sorting.
        #"""
        
        #if role == self.SortRole:
            #try:
                #value = QStandardItemModel.data(self, modelIndex, QtCore.Qt.DisplayRole)
                #value = float(value)
            #except:
                #pass
        #else:
            #value = QStandardItemModel.data(self, modelIndex, role)
            
        #return value
    
    ##----------------------------------------------------------------------
    #def _getpvs(self, channel_name):
        #""""""
        
        #elemName, fieldName = channel_name.split('.')
        #elem = ap.getElements(elemName)[0]
        #pv = elem.pv(field=fieldName,handle='readback')
        #if len(pv) == 1:
            #pvrb = pv[0]
        #elif len(pv) == 0:
            #pvrb = None
        #else:
            #raise ValueError('Unexpected pv list returned: '+str(pv))
        #pv = elem.pv(field=fieldName,handle='setpoint')
        #if len(pv) == 1:
            #pvsp = pv[0]
        #elif len(pv) == 0:
            #pvsp = None
        #else:
            #raise ValueError('Unexpected pv list returned: '+str(pv))
            
        #return pvrb, pvsp
        
    
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
        
        ## Temporarily block signals emitted from the model
        #self.blockSignals(True)
        
        channelGroupList = []
        if channelGroupInfo == {}:
            for (elemName,chName) in zip(elemName_list,channelName_list):
                default_channel_group_name = elemName
                default_channel_group_weight = 0.
                channelGroup = {'name':default_channel_group_name,
                                'weight':default_channel_group_weight,
                                'channel_name_list': [chName]}
                channelGroupList.append(channelGroup)
                self.channel_group_list.append(channelGroup)
                
            
                
        else:
            channelGroup = {'name': channelGroupInfo['name'],
                            'weight': channelGroupInfo['weight'],
                            'channel_name_list': channelName_list,
                            }
            channelGroupList.append(channelGroup)
            self.channel_group_list.append(channelGroup)
            
            
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
        
        self.updateGroupBasedModel(change_type='append',
                                   channelGroupList=channelGroupList)
        
        
        
        
        
########################################################################
class TunerConfigSetupView(QDialog, Ui_Dialog):
    """"""
    
    #----------------------------------------------------------------------
    def __init__(self, model, isModal, parentWindow):
        """Constructor"""
        
        QDialog.__init__(self, parent=parentWindow)
                
        self.setupUi(self)
        
        self.setWindowFlags(QtCore.Qt.Window) # To add Maximize & Minimize buttons
        self.setModal(isModal)
        
        self.visible_col_list = const.DEFAULT_VISIBLE_COL_LIST_CONFIG_SETUP        
                
        self.model = model
        self.proxyModel = QSortFilterProxyModel()
        self.proxyModel.setSourceModel(self.model)
        self.proxyModel.setDynamicSortFilter(True)
        self.proxyModel.setSortRole(self.model.SortRole)
        
        self.treeView.setModel(self.proxyModel)
        self.treeView.setItemsExpandable(True)
        self.treeView.setRootIsDecorated(True)
        self.treeView.setAllColumnsShowFocus(True)
        self.treeView.setHeaderHidden(False)
        self.treeView.setSortingEnabled(True)
        
        self._expandAll_and_resizeColumn()
        
        self.treeView.setSelectionMode(QAbstractItemView.ExtendedSelection)
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
    
    
    #----------------------------------------------------------------------
    def accept(self):
        """"""
        
        self.model.name = self.lineEdit_config_name.text()
        
        self.model.description = self.textEdit.toPlainText()
    
        saveFileFlag = self.checkBox_save_config_to_file.isChecked()
        if saveFileFlag:
            self.emit(SIGNAL('saveConfigToFile'), self.model)
        
        accepted = True
        self.emit(SIGNAL('prepareOutput'),accepted)
        
        QDialog.accept(self)
        
    
    #----------------------------------------------------------------------
    def reject(self):
        """"""
        
        accepted = False
        self.emit(SIGNAL('prepareOutput'),accepted)
        
        QDialog.reject(self) # will hide the dialog
            
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
class TunerConfigSetupApp(QObject):
    """"""

    #----------------------------------------------------------------------
    def __init__(self, init_tuner_config_dict, isModal, parentWindow):
        """Constructor"""
        
        QObject.__init__(self)
        
        self._initModel(init_tuner_config_dict)
        self._initView(isModal, parentWindow)
        
        self.connect(self.view.pushButton_add_from_GUI_selector,
                     SIGNAL('clicked()'), self._launchChannelExplorer)
        self.connect(self, SIGNAL('channelsSelected'),
                     self._askChannelGroupNameAndWeight)
        self.connect(self, SIGNAL('channelGroupInfoObtained'),
                     self.model.importNewChannels)
        self.connect(self.model, SIGNAL('modelUpdated'),
                     self.view._updateProxyModel)
        self.connect(self.model, SIGNAL('modelUpdated'),
                     self.view._expandAll_and_resizeColumn)
        
        self.connect(self.view, SIGNAL('prepareOutput'),
                     self.model._prepareOutput)
        
    #----------------------------------------------------------------------
    def _initModel(self, init_tuner_config_dict=None):
        """"""
        
        self.model = TunerConfigSetupModel(init_tuner_config_dict)
        
    #----------------------------------------------------------------------
    def _initView(self, isModal, parentWindow):
        """"""
        
        self.view = TunerConfigSetupView(self.model, isModal, parentWindow)
        
    #----------------------------------------------------------------------
    def _launchChannelExplorer(self):
        """"""
                
        result = channelexplorer.make(modal=True, 
                    init_object_type='channel', can_modify_object_type=False,
                    output_type=channelexplorer.TYPE_OBJECT)
        
        selected_channels = result['dialog_result']
        
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
def make(init_tuner_config_dict=None, isModal=True, parentWindow=None):
    """"""
    
    app = TunerConfigSetupApp(init_tuner_config_dict, isModal, parentWindow)
    
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

    app = make(isModal=True)
        
    if using_cothread:
        cothread.WaitForQuit()
        print app.model.output        
    else:
        exit_status = qapp.exec_()
        print app.model.output        
        sys.exit(exit_status)

    
    
#----------------------------------------------------------------------    
if __name__ == "__main__" :
    main(sys.argv)
    