#! /usr/bin/env python

"""

"""

import sys
import os

USE_DEV_SRC = True
if USE_DEV_SRC:
    # Force Python to use your development modules,
    # instead of the modules already installed on the system.
    if os.environ.has_key('HLA_DEV_SRC'):
        dev_src_dir_path = os.environ['HLA_DEV_SRC']

        if dev_src_dir_path in sys.path:
            sys.path.remove(dev_src_dir_path)
        
        sys.path.insert(0, dev_src_dir_path)
            
    else:
        print 'Environment variable named "HLA_DEV_SRC" is not defined.'

import hla
if not hla.machines._lat:
    hla.initNSLS2VSR()

import datetime

import cothread

import PyQt4.Qt as Qt
from . import gui_icons # Note that you cannot use main() with relative importing

from .ui_tunerConfigSetupDialog import Ui_Dialog

from . import config as const
from .knob import Knob, KnobGroup, KnobGroupList
from .tuner_file_manager import TunerFileManager
from . import preferencesDialogForConfigSetup \
       as PreferencesDialogForConfigSetup
from . import channelSelectorDialog \
       as ChannelSelectorDialog


# TODO:
# *) Add Preferences info for Config Setup GUI & Channel Selector GUI
# *) allow manual knob addition using a lineEdit box
# *) allow grouping/ungrouping in setup dialog
# *) eliminate duplicate knobs in a knob group list(check this in setup dialog)
# *) Use direct caget & caput for faster
# *) Make a realistic config file
# *) Accept expression for weight specification
# *) Ramping capability
# *) If config not saved to a file, ask user if want to save
# *) show asterisk if config is not saved
         

########################################################################
class TunerConfigSetupModel(Qt.QStandardItemModel):
    """"""

    #----------------------------------------------------------------------
    def __init__(self, knob_group_list, **kwargs):
        """Constructor"""
        
        Qt.QStandardItemModel.__init__(self, \
            parent = kwargs.get('parent',None))
        
        self.output = {}
        
        visible_column_name_list = kwargs.get( \
            'visible_column_name_list',
            const.DEFAULT_VISIBLE_COL_LIST_CONFIG_SETUP)
        
        # Configuration-related data
        self.knobGroupList = knob_group_list
        self.config_name = ''
        self.config_description = ''
        
        self._updateFlatKnobList()

        self.isGroupBasedView = True
        
        self.nRows = 0
        
        self.col_name_dict = const.DICT_COL_NAME
        
        # Specify the visible columns in the order
        # of your preference
        self.col_name_list = visible_column_name_list
        
        self._updateModel()
        
        self._connect_itemChanged_signal(True)

    #----------------------------------------------------------------------
    def _updateFlatKnobList(self):
        """"""
        
        self.flat_knob_list = []
        for kg in self.knobGroupList.knobGroups:
            self.flat_knob_list.extend(kg.knobs)
        
    #----------------------------------------------------------------------
    def _connect_itemChanged_signal(self, turn_on):
        """"""
        
        if turn_on:
            self.connect(self, Qt.SIGNAL('itemChanged(QStandardItem *)'),
                         self._validateItemChange)
        else:
            self.disconnect(self, Qt.SIGNAL('itemChanged(QStandardItem *)'),
                            self._validateItemChange)
    
    #----------------------------------------------------------------------
    def _isValidKnobName(self, new_name):
        """"""
        
        splitted_new_name = new_name.split('.')

        if len(splitted_new_name) != 2:
            return False
                
        elem_name, field_name = splitted_new_name
                
        elem = hla.getElements(elem_name)
        if not elem:
            return False
                    
        if field_name not in elem.fields():
            return False
        
        return True
                
    #----------------------------------------------------------------------
    def _validateItemChange(self, item):
        """"""
                
        # Temporarily disconnect the itemChanged signal so that
        # checking/unchecking items while enforcing mutual
        # exclusiveness does not call this function again recursively.
        self._connect_itemChanged_signal(False)
    
        p = item.parent()
        new_input = str(item.text())

        if item.isCheckable(): # When Group Name item is changed
            if item.hasChildren(): # Knob-groups-based view
                one_knob_name = str(item.child(0).text())
            else: # Knob-based view
                model = item.model()
                knob_name_col_index = \
                    self.col_name_list.index(const.COL_KNOB_NAME)
                knob_item = model.item(item.row(), knob_name_col_index)
                one_knob_name = str(knob_item.text())
            
            for kg in self.knobGroupList.knobGroups:
                if one_knob_name in [k.name for k in kg.knobs]:
                    kg.name = new_input
                    break
            
            self._enforceRefGroupMutualExclusiveness(item)
        else:
            group_name_col_index = \
                self.col_name_list.index(const.COL_GROUP_NAME)

            if p:
                group_name = str(p.text())
            else:
                model = item.model()
                knob_group_item = model.item(item.row(),
                                             group_name_col_index)
                group_name = str(knob_group_item.text())
                
            for i, kg in enumerate(self.knobGroupList.knobGroups):
                if group_name == kg.name:
                    knob_group = kg
                    knob_group_index = i
                    break
            
            if p:
                knob = knob_group.knobs[item.row()]
            else:
                knob = self.flat_knob_list[item.row()]
            
            col_name = self.col_name_list[item.column()]

            if col_name == const.COL_KNOB_NAME:
                
                new_name = str(item.text())
                
                if not self._isValidKnobName(new_name):
                    item.setText(knob.name)
                    error_str = 'Invalid knob name entered.'
                    Qt.QMessageBox.critical(None,'ERROR',error_str)
                    # Re-enable the temporarily disconnected signal       
                    self._connect_itemChanged_signal(True)
                    return
                                        
                # Update the underlying data
                knob.name = new_name
                
                # Also change the knob name shown as a child of the 
                # knob group item, if the view is knob-group-based.
                if p:
                    knob_name_item_under_group_name_item = \
                        p.child(item.row(),group_name_col_index)
                    knob_name_item_under_group_name_item.setText(new_name)
                                
            elif col_name == const.COL_GROUP_NAME:
                # When the knob name item under a parent knob group name item
                # is changed in the knob-group-based view.
                
                if not self.isGroupBasedView:
                    raise Exception, 'The current view cannot be knob-based. Something went wrong.'
                
                new_name = str(item.text())
                
                if not self._isValidKnobName(new_name):
                    item.setText(knob.name)
                    error_str = 'Invalid knob name entered.'
                    Qt.QMessageBox.critical(None,'ERROR',error_str)
                    # Re-enable the temporarily disconnected signal       
                    self._connect_itemChanged_signal(True)
                    return
                
                # Update the underlying data
                knob.name = new_name
                
                # Also change the knob name item in the knob name column
                p = item.parent()
                knob_name_item_in_knob_name_column = \
                    p.child(item.row(),self.col_name_list.
                            index(const.COL_KNOB_NAME))
                knob_name_item_in_knob_name_column.setText(new_name)
                                
            else:
                raise Exception, 'This property (' + c + \
                                 ') should not be editable.'
            
            
            self._updateFlatKnobList()
            self._updateModel()
                
        # Re-enable the temporarily disconnected signal       
        self._connect_itemChanged_signal(True)

            
    #----------------------------------------------------------------------
    def _enforceRefGroupMutualExclusiveness(self, item):
        """"""
                
        group_name_col_index = item.column()
        this_row = item.row()
        newRefGroupName = str(item.text())
            
        m = self # = item.model()
            
        exception_str = 'Enforcement of mutual exclusiveness for the selection of group name failed.'

        group_name_check_state_list = \
            self._getGroupNameCheckStateList(m, group_name_col_index)
            
        if m.isGroupBasedView: # If knob-group-based view is being used
                
            if group_name_check_state_list.count(True) == 1:
                self._connect_itemChanged_signal(True)
                return
            
            if group_name_check_state_list[this_row]:
                group_name_check_state_list[this_row] = False
                index_to_be_unchecked = \
                    group_name_check_state_list.index(True)
                item_to_be_unchecked = m.item(index_to_be_unchecked,
                                              group_name_col_index)
                item_to_be_unchecked.setCheckState(Qt.Qt.Unchecked)
            
                m.knobGroupList._changeRefKnobGroupName(
                    newRefGroupName)
                m._updateModel()
                
            else:
                item.setCheckState(Qt.Qt.Checked)
                
            # Check if there is only one group being checked
            group_name_check_state_list = \
                self._getGroupNameCheckStateList(m, group_name_col_index)
            if group_name_check_state_list.count(True) != 1:
                raise Exception, exception_str
            else:
                pass
            
        else: # If knob-based view is being used

            currentRefKnobGroup = self.knobGroupList.knobGroups[
                self.knobGroupList.ref_index]
            nCurrentRefKnobs = len(currentRefKnobGroup.knobs)
            if group_name_check_state_list.count(True) == \
               nCurrentRefKnobs:
                self._connect_itemChanged_signal(False)
                return
                
            if group_name_check_state_list[this_row]:
                group_name_check_state_list[this_row] = False
                items_to_be_unchecked = [
                    m.item(i,group_name_col_index)
                    for i in range(len(group_name_check_state_list))
                    if group_name_check_state_list[i] ]
                for i in items_to_be_unchecked:
                    i.setCheckState(Qt.Qt.Unchecked)
                
                items_to_be_checked = [
                    m.item(i,group_name_col_index)
                    for i in range(len(group_name_check_state_list))
                    if str(m.item(i,group_name_col_index).text()) 
                    == newRefGroupName ]
                for i in items_to_be_checked:
                    i.setCheckState(Qt.Qt.Checked)
                        
                m.knobGroupList._changeRefKnobGroupName(
                    newRefGroupName )
                m._updateModel()
                
            else:
                item.setCheckState(Qt.Qt.Checked)
                
            # Check if there is only one group being checked
            group_name_check_state_list = \
                self._getGroupNameCheckStateList(
                    m, group_name_col_index)
            currentRefKnobGroup = self.knobGroupList.knobGroups[
                self.knobGroupList.ref_index]
            nCurrentRefKnobs = len(currentRefKnobGroup.knobs)
            if group_name_check_state_list.count(True) != nCurrentRefKnobs:
                raise Exception, exception_str
            else:
                pass
                

    
    #----------------------------------------------------------------------
    def _getGroupNameCheckStateList(self, model,
                                    group_name_col_index):
        """"""
        
        nRows = model.rowCount()
        
        group_name_check_state_list = []
        for row in range(nRows):
            i = model.item(row, group_name_col_index)
            group_name_check_state_list.append(
                (i.checkState() == Qt.Qt.Checked) )
        
        return group_name_check_state_list
    
        
    
    #----------------------------------------------------------------------
    def _getColumnIndex(self, column_name):
        """"""
        
        if column_name in self.col_name_list:
            return self.col_name_list.index(column_name)
        else:
            return None
        
    
    #----------------------------------------------------------------------
    def convertChannelsToKnobs(self, channel_list):
        """"""
        
        knob_list = []
        for c in channel_list:
            knob_list.append(Knob(c))
        
        return knob_list
    
    #----------------------------------------------------------------------
    def _addNewKnobGroupsToModel(self, new_KnobGroupList):
        """"""
                
        self.knobGroupList.extend(new_KnobGroupList)
        
        self._updateFlatKnobList()

        self._updateModel()


    #----------------------------------------------------------------------
    def _importNewChannelsToModel(self, selectedChannels, knobGroupInfo):
        """"""
        
        selectedKnobs = self.convertChannelsToKnobs(selectedChannels)

        if knobGroupInfo:
            knobGroup = KnobGroup(knobGroupInfo['name'], selectedKnobs,
                                  knobGroupInfo['weight'])
            self.knobGroupList.knobGroups.append(knobGroup)
            self.knobGroupList.updateDerivedProperties()
        else:
            for k in selectedKnobs:
                default_knob_group_name = k.name
                default_knob_group_weight = 1
                knobGroup = KnobGroup(default_knob_group_name, [k],
                                      default_knob_group_weight)
                self.knobGroupList.knobGroups.append(knobGroup)
                self.knobGroupList.updateDerivedProperties()
         
        self._updateModel()    
        

    #----------------------------------------------------------------------
    def _updateModel(self):
        """"""
        
        self.setHorizontalHeaderLabels(self.col_name_list)
        
        self.setColumnCount(len(self.col_name_list))

        # Clear contents
        self.removeRows(0,self.rowCount())
        
        # Stop here if there is no knob group specified.
        if not self.knobGroupList.knobGroups:
            return
        
        self.nRows = 0
        
        # Temporarily block signals emitted from the model
        self.blockSignals(True)
        
        if self.isGroupBasedView: # Use Knob-Group-based View
            
            group_col_ind = self._getColumnIndex(const.COL_GROUP_NAME)
            if group_col_ind != 0: # If COL_GROUP_NAME is not included in
                # visible column list, or it is not specified as
                # the first column, force it to be visible at
                # the 1st column, since Group-based view is being
                # selected. Note that NOT having COL_GROUP_NAME
                # at 1st column results in not being able to
                # expand/collapse the Group Name cells.
                if group_col_ind == None:
                    self.col_name_list.insert(0,const.COL_GROUP_NAME)
                else:
                    self.col_name_list.remove(const.COL_GROUP_NAME)
                    self.col_name_list.insert(0,const.COL_GROUP_NAME)
                group_col_ind = 0
                self.setHorizontalHeaderLabels(self.col_name_list)
                
            for (index, kg) in enumerate(self.knobGroupList.knobGroups):
                group = Qt.QStandardItem(kg.name)
                group.setFlags(group.flags() |
                               Qt.Qt.ItemIsEditable | # Make the item editable
                               Qt.Qt.ItemIsUserCheckable) # Make it checkable
                if index == self.knobGroupList.ref_index:
                    group.setCheckState(Qt.Qt.Checked)
                else:
                    group.setCheckState(Qt.Qt.Unchecked)
                
                ### Populate group-level property items
                group_level_col_list = self.col_name_list[:]
                group_level_col_list.remove(const.COL_GROUP_NAME)
                group_level_col_list = \
                    [c for c in group_level_col_list
                     if ( (self.col_name_dict[c][0] == 'KnobGroup') or
                          (self.col_name_dict[c][0] == 'KnobGroupList') )]
                #
                for c in group_level_col_list:
                    if self.col_name_dict[c][0] == 'KnobGroup':
                        if c == const.COL_WEIGHT:
                            item = Qt.QStandardItem(
                                const.STR_FORMAT_WEIGHT_FACTOR
                                % kg.weight)
                        else:
                            raise Exception, 'Unexpected error. Group level properties associated with KnobGroup class is supposed to be only group name and weight.'
                    else: # if self.col_name_dict[c][0] == 'KnobGroupList'
                        array = getattr(self.knobGroupList,
                                        self.col_name_dict[c][1])
                        str_format = self.col_name_dict[c][2]
                        item = Qt.QStandardItem(str_format 
                                                % array[index])
                        if c == const.COL_NORMALIZED_WEIGHT:
                            item.setFlags(item.flags() &
                                          ~Qt.Qt.ItemIsEditable) # Make the item NOT editable
                                
                    self.setItem(self.nRows, self._getColumnIndex(c),
                                 item)
                    for child_index in range(len(kg.knobs)):
                        group.setChild(child_index, 
                                       self._getColumnIndex(c), 
                                       item.clone())
                    
                
                ### Populate knob-level property items
                knob_level_col_list = self.col_name_list[:]
                knob_level_col_list = \
                    [c for c in knob_level_col_list
                     if self.col_name_dict[c][0] == 'Knob']
                model_stored_col_list = self.col_name_list[:]
                model_stored_col_list = \
                    [c for c in model_stored_col_list
                     if self.col_name_dict[c][0] == 'TunerModel']
                #    
                for (child_index, k) in enumerate(kg.knobs):
                    knob = Qt.QStandardItem(k.name)
                    knob.setFlags(knob.flags() | 
                                  Qt.Qt.ItemIsEditable) # Make the item editable
                    group.setChild(child_index, 
                                   self._getColumnIndex(const.COL_GROUP_NAME),
                                   knob)
                    
                    for c in knob_level_col_list:
                        value = getattr(k, self.col_name_dict[c][1])
                        str_format = self.col_name_dict[c][2]
                        if str_format != 'timestamp':
                            if (value == None) or (type(value) == list):
                                str_format = '%s'
                            elif (type(value) == tuple):
                                str_format = '%s'
                                value = str(value)
                            else:
                                pass
                            item = Qt.QStandardItem(str_format % value)
                        else:
                            if value == None:
                                time_str = 'None'
                            else:
                                time_str = datetime.datetime.fromtimestamp(
                                    value).isoformat()
                            item = Qt.QStandardItem(time_str)
                        
                        if c != const.COL_KNOB_NAME:
                            item.setFlags(item.flags() &
                                          ~Qt.Qt.ItemIsEditable) # Make the item NOT editable
                        
                        group.setChild(child_index, 
                                       self._getColumnIndex(c), item)
                    
                    for c in model_stored_col_list:
                        flat_index = self.flat_knob_list.index(k)
                        array = getattr(self, self.col_name_dict[c][1])
                        value = array[flat_index]
                        str_format = self.col_name_dict[c][2]
                        if str_format != 'timestamp':
                            if (value == None) or (type(value) == list):
                                str_format = '%s'
                            elif (type(value) == tuple):
                                str_format = '%s'
                                value = str(value)
                            else:
                                pass
                            item = Qt.QStandardItem(str_format % value)
                        else:
                            if value == None:
                                time_str = 'None'
                            else:
                                time_str = datetime.datetime.fromtimestamp(
                                    value).isoformat()
                            item = Qt.QStandardItem(time_str)
                        if (c != const.COL_TARGET_SETP):
                            item.setFlags(item.flags() &
                                          ~Qt.Qt.ItemIsEditable) # Make the item NOT editable
                        group.setChild(child_index, 
                                       self._getColumnIndex(c), item)
                            
                
                self.setItem(self.nRows, group_col_ind, group)
                
                
                
                self.nRows += 1
                    
        else: # Use Knob-based View

            kg_list = self.knobGroupList
            knob_group_index_list = []
            for (i, kg) in enumerate(kg_list.knobGroups):
                knob_group_index_list.extend([i]*len(kg.knobs))
                
            knob_name_col_ind = self._getColumnIndex(const.COL_KNOB_NAME)
            if knob_name_col_ind == None: # If COL_KNOB_NAME is not included in
                # visible column list, force it to be visible at
                # the 1st column, since Knob-based view is being
                # selected.
                self.col_name_list.insert(0,const.COL_KNOB_NAME)
                knob_name_col_ind = 0
                self.setHorizontalHeaderLabels(self.col_name_list)
                    
            for (i, k) in enumerate(self.flat_knob_list):
                kg_index = knob_group_index_list[i]
                kg = kg_list.knobGroups[kg_index]
                knob = Qt.QStandardItem(k.name)
                knob.setFlags(knob.flags() |
                              Qt.Qt.ItemIsEditable) # Make the item editable
                
                self.setItem(self.nRows, knob_name_col_ind, knob)
                
                ### Populate knob-level property items
                knob_level_col_list = self.col_name_list[:]
                knob_level_col_list.remove(const.COL_KNOB_NAME)
                #    
                for c in knob_level_col_list:
                    if self.col_name_dict[c][0] == 'Knob':
                        value = getattr(k, self.col_name_dict[c][1])
                        str_format = self.col_name_dict[c][2]
                        if str_format != 'timestamp':
                            if (value == None) or (type(value) == list):
                                str_format = '%s'
                            elif (type(value) == tuple):
                                str_format = '%s'
                                value = str(value)
                            else:
                                pass
                            item = Qt.QStandardItem(str_format % value)
                        else:
                            if value == None:
                                time_str = 'None'
                            else:
                                time_str = datetime.datetime.fromtimestamp(
                                    value).isoformat()
                            item = Qt.QStandardItem(time_str)
                        
                        item.setFlags(item.flags() &
                                      ~Qt.Qt.ItemIsEditable) # Make the item NOT editable
                    elif self.col_name_dict[c][0] == 'KnobGroup':
                        if c == const.COL_GROUP_NAME:
                            item = Qt.QStandardItem(kg.name)
                            item.setFlags(item.flags() |
                                          Qt.Qt.ItemIsEditable | # Make the item editable
                                          Qt.Qt.ItemIsUserCheckable) # Make it checkable
                            if kg_index == self.knobGroupList.ref_index:
                                item.setCheckState(Qt.Qt.Checked)
                            else:
                                item.setCheckState(Qt.Qt.Unchecked)
                        elif c == const.COL_WEIGHT:
                            item = Qt.QStandardItem(
                                const.STR_FORMAT_WEIGHT_FACTOR
                                % kg.weight)
                        else:
                            raise Exception, 'Unexpected error. Group level properties associated with KnobGroup class is supposed to be only group name and weight.'
                    elif self.col_name_dict[c][0] == 'KnobGroupList':
                        array = getattr(self.knobGroupList,
                                        self.col_name_dict[c][1])
                        value = array[kg_index]
                        str_format = self.col_name_dict[c][2]
                        item = Qt.QStandardItem(str_format % value)
                        if c != const.COL_STEP_SIZE:
                            item.setFlags(item.flags() &
                                          ~Qt.Qt.ItemIsEditable) # Make the item NOT editable
                    elif self.col_name_dict[c][0] == 'TunerModel':
                        flat_index = self.flat_knob_list.index(k)
                        array = getattr(self, self.col_name_dict[c][1])
                        value = array[flat_index]
                        str_format = self.col_name_dict[c][2]
                        if str_format != 'timestamp':
                            if (value == None) or (type(value) == list):
                                str_format = '%s'
                            elif (type(value) == tuple):
                                str_format = '%s'
                                value = str(value)
                            else:
                                pass
                            item = Qt.QStandardItem(str_format % value)
                        if c != const.COL_TARGET_SETP:
                            item.setFlags(item.flags() &
                                          ~Qt.Qt.ItemIsEditable) # Make the item NOT editable
                    else:
                        item = Qt.QStandardItem('')
                        item.setFlags(item.flags() &
                                      ~Qt.Qt.ItemIsEditable) # Make the item NOT editable
                                
                    self.setItem(self.nRows, self._getColumnIndex(c),
                                 item)
                    
                self.nRows += 1
        
        # Re-enable the blocked signals emitted from the model
        self.blockSignals(False)

        self.emit(Qt.SIGNAL('modelUpdated'))

    
    #----------------------------------------------------------------------
    def _removeDuplicateKnobs(self):
        """"""
        
        kgs = self.knobGroupList.knobGroups
        
        flat_knob_list = []
        flat_knob_name_list = []
        flat_knobGroup_name_list = []
        for kg in kgs:
            flat_knob_list.extend(kg.knobs)
            flat_knob_name_list.extend(
                [k.name for k in kg.knobs])
            flat_knobGroup_name_list.extend(
                [kg.name]*len(kg.knobs))
        
        # When there is no duplicate found
        unique_flat_knob_name_set = set(flat_knob_name_list)
        if len(unique_flat_knob_name_set) == len(flat_knob_name_list):
            print 'No duplicate knobs were found.'
            return

        # When there are some duplicates
        seen = set()
        seen_add = seen.add
        noDup_zipped_list = [
            (flat_knob_list[i], flat_knob_name_list[i],
             flat_knobGroup_name_list[i])
            for i in range(len(flat_knob_list))
            if flat_knob_name_list[i] not in seen and
            not seen_add(flat_knob_name_list[i])
        ]
        x, y, z = zip(*noDup_zipped_list)
        noDup_flat_knob_list = list(x)
        noDup_flat_knob_name_list = list(y)
        noDup_flat_knobGroup_name_list = list(z)
        # create new KnobGroupList object without any duplicate knobs
        knobGroup_name_list = [kg.name for kg in kgs]
        newKnobGroups = []
        for (ind,kg_name) in enumerate(knobGroup_name_list):
            if kg_name not in noDup_flat_knobGroup_name_list:
                continue
            else:
                new_knob_list = [k for (i,k) in 
                    enumerate(noDup_flat_knob_list)
                    if noDup_flat_knobGroup_name_list[i]
                    == kg_name]
                newKnobGroups.append(
                    KnobGroup(kg_name, new_knob_list,
                              kgs[ind].weight) )
        
        self.knobGroupList.knobGroups = newKnobGroups
        self.knobGroupList.updateDerivedProperties()
        self._updateModel()
        
        
        
        
########################################################################
class TunerConfigSetupView(Qt.QDialog, Ui_Dialog):
    """"""

    #----------------------------------------------------------------------
    def __init__(self, model, modal, parentWindow):
        """Constructor"""
        
        Qt.QDialog.__init__(self, parent = parentWindow)
        
        self.model = model
    
        self.setupUi(self)
        
        self.setWindowFlags(Qt.Qt.Window) # To add Maximize & Minimize buttons
        
        self.setModal(modal)
        
        self.treeView.setSelectionMode(
            Qt.QAbstractItemView.ExtendedSelection)
    
        self.treeView.setModel(self.model)
    
        self._expandAll_and_resizeColumn()
            
        self.treeView.setContextMenuPolicy(Qt.Qt.CustomContextMenu)
        self.actionGroup = Qt.QAction(Qt.QIcon(), 'Group knobs',
                                      self.treeView)
        self.actionUngroup = Qt.QAction(Qt.QIcon(), 'Ungroup knobs',
                                        self.treeView)
        self.popMenu = Qt.QMenu(self.treeView)
        self.popMenu.addAction(self.actionUngroup)
        self.popMenu.addAction(self.actionGroup)
        
        self.connect(self.buttonGroup, 
                     Qt.SIGNAL('buttonClicked(QAbstractButton *)'),
                     self._switch_view_base)
        
        
        self.connect(self.treeView,
                     Qt.SIGNAL(
                         'customContextMenuRequested(const QPoint &)'),
                     self._openContextMenu)
        self.connect(self.actionGroup, Qt.SIGNAL('triggered()'),
                     self._groupKnobs)
        self.connect(self.actionUngroup, Qt.SIGNAL('triggered()'),
                     self._ungroupKnobs)
        
          
    #----------------------------------------------------------------------
    def _groupKnobs(self):
        """"""
        
        print 'group knobs'
    
    #----------------------------------------------------------------------
    def _ungroupKnobs(self):
        """"""
        
        print 'ungroup knobs'
    
    
    
    #----------------------------------------------------------------------
    def _openContextMenu(self, point):
        """"""
        
        self.popMenu.exec_(self.treeView.mapToGlobal(point))
        
        
    #----------------------------------------------------------------------
    def _switch_view_base(self, button):
        """"""
                
        if button == self.radioButton_knobs:
            self.model.isGroupBasedView = False
        elif button == self.radioButton_knob_groups:
            self.model.isGroupBasedView = True
        else:
            raise Exception, "Unknown button press received."
        
        self.model._updateModel()
        

    #----------------------------------------------------------------------
    def _expandAll_and_resizeColumn(self):
        """"""

        self.treeView.expandAll()
        self.treeView.resizeColumnToContents(0)

    #----------------------------------------------------------------------
    def _prepareOutput(self, config_data, saveFileFlag):
        """"""
        
        self.model.output = {'config_data':config_data,
                             'saveFileFlag':saveFileFlag}
        
        super(TunerConfigSetupView, self).accept() # will hide the dialog
        
    #----------------------------------------------------------------------
    def accept(self):
        """"""
        
        self.model.config_name = str(self.lineEdit_config_name.text())
        
        self.model.config_description = \
            str(self.textEdit_config_description.toPlainText())

        saveFileFlag = self.checkBox_save_to_file.isChecked()
        
        self.emit(Qt.SIGNAL('configAccepted'), self.model, saveFileFlag)
        
        
    #----------------------------------------------------------------------
    def reject(self):
        """"""
        
        self.model.output = {}

        super(TunerConfigSetupView, self).reject() # will hide the dialog

    
        
    #----------------------------------------------------------------------
    def debug_func(self):
        """"""
        
        import pickle
        f = open('selected_knobs.pkl','r')
        selectedChannels = pickle.load(f)
        f.close()
        f = open('knobGroupInfo.pkl','r')
        knobGroupInfo = pickle.load(f)
        f.close()
        
        model = self._getCurrentModel()
        
        if model:
            model._importNewChannelsToModel(selectedChannels, knobGroupInfo)
            model._importNewChannelsToModel(selectedChannels, {})
        
            model._updateModel()
            

########################################################################
class TunerConfigSetupApp(Qt.QObject):
    """"""

    #----------------------------------------------------------------------
    def __init__(self, starting_TunerModel, modal, 
                 parentWindow, **kwargs):

        """Constructor"""
        
        Qt.QObject.__init__(self)
        
        # Setting "default" visible column name list
        # (either hard-coded default list or user-specified
        # default list)
        self.visible_column_name_list = kwargs.get(
            'visible_column_name_list', 
            const.DEFAULT_VISIBLE_COL_LIST_CONFIG_SETUP)

        self._initModel()
        self._initView(modal, parentWindow)
        self._initFileManager()
        
        
        self.connect(self.view, Qt.SIGNAL('configAccepted'),
                     self.fileManager._finalizeConfigFromSetupGUI)
        self.connect(self.fileManager,
                     Qt.SIGNAL('finalizedConfigFromSetupGUI'),
                     self.view._prepareOutput)
        
        self.connect(self.view.pushButton_remove_duplicates,
                     Qt.SIGNAL('clicked()'),
                     self.model._removeDuplicateKnobs)
        
        self.connect(self.model,
                     Qt.SIGNAL('modelUpdated'),
                     self.view._expandAll_and_resizeColumn)


        # Connections related to saving preferences to file
        self.connect(self.view.pushButton_preferences,
                     Qt.SIGNAL('clicked()'),
                     self._launchPrefDialog)
        self.connect(self,
                     Qt.SIGNAL('readyForUpdateOnPrefChange'),
                     self._updateOnPreferencesChange)

        # Connections related to launch Channel Selector Dialog
        self.connect(self.view.pushButton_add_from_selector_GUI,
                     Qt.SIGNAL('clicked()'),
                     self._launchChannelSelectorDialog)
        self.connect(self, Qt.SIGNAL('channelsSelected'), 
                     self._checkIfAllChannelsAreKnobs)
        self.connect(self, Qt.SIGNAL('checkedAllKnobs'),
                     self._askKnobGroupNameAndWeight)
        self.connect(self, Qt.SIGNAL('knobGroupInfoObtained'),
                     self.model._importNewChannelsToModel)

    #----------------------------------------------------------------------
    def _initFileManager(self):
        """"""
        
        self.fileManager = TunerFileManager()
        
        # Connections related to loading configuration from file
        self.connect(self.view.pushButton_add_from_file,
                     Qt.SIGNAL('clicked()'),
                     self._prepareForAddFromFile)
        self.connect(self, Qt.SIGNAL('readyForLoadConfigOrSnapshotFile'),
                     self.fileManager.loadConfigOrSnapshotFileToSetupGUI)
        self.connect(self.fileManager,
                     Qt.SIGNAL('knobGroupListLoaded'),
                     self.model._addNewKnobGroupsToModel)


    #----------------------------------------------------------------------
    def _prepareForAddFromFile(self):
        """"""
        
        self.emit(Qt.SIGNAL('readyForLoadConfigOrSnapshotFile'))
    
    #----------------------------------------------------------------------
    def _getCurrentModelOrApp(self):
        """"""

        model = self.view._getCurrentModel()
    
        if model:
            model_or_app = model
        else:
            model_or_app = self
            
        return model_or_app
            
    #----------------------------------------------------------------------
    def _launchPrefDialog(self):
        """"""
        
        full_string_list = const.COL_ALL_NAMES_CONFIG_SETUP
        current_selected_string_list = self.model.col_name_list
        
        result = PreferencesDialogForConfigSetup.make(
            full_string_list, 
            permanently_selected_string_list = 
            const.ALWAYS_VISIBLE_COL_LIST,
            selected_string_list =
            current_selected_string_list,
            output_type = PreferencesDialogForConfigSetup.OUTPUT_TYPE_STRING_LIST)
        
        if not result: # Dialog cancelled
            return
        
        self.emit(Qt.SIGNAL('readyForUpdateOnPrefChange'),
                  result['selected_list'])
        
    #----------------------------------------------------------------------
    def _launchChannelSelectorDialog(self):
        """"""
        
        selected_channels = ChannelSelectorDialog.make(
            filter_spec = [ [{'read_only':'False'},False] ],
            output_type = ChannelSelectorDialog.TYPE_CHANNEL)
        
        self.emit(Qt.SIGNAL('channelsSelected'), selected_channels)
        
    #----------------------------------------------------------------------
    def _checkIfAllChannelsAreKnobs(self, channels):
        """"""
        
        if not channels:
            return
        
        # Check if the channels are all knobs (= writeable channels,
        # NOT read-only channels)
        if all([not c.read_only for c in channels]):
            self.emit(Qt.SIGNAL('checkedAllKnobs'), channels)
        else:
            Qt.QMessageBox.critical(
                None,'ERROR','Not all the channels are knobs, i.e., ' + \
                'writeable channels, NOT read-only channels.')
        
    #----------------------------------------------------------------------
    def _askKnobGroupNameAndWeight(self, selectedKnobs):
        """"""

        prompt_text = ('Do you want to group the selected knobs together?\n' +
                       'If so, enter a text for Group Name and press OK.\n' +
                       'Otherwise, leave it blank and press OK, \n' +
                       'or just press Cancel.\n\n' +
                       'Group Name:')
        result = Qt.QInputDialog.getText(self.view, 'Group Name', 
                        prompt_text)
        group_name = str(result[0]).strip(' \t\n\r')
        
        if group_name:
            knobGroupInfo = {'name':group_name}
            
            prompt_text = ('Specify the weight factor for this group.\n' +
                           'If Cancel is pressed, the weight factor will be set ' +
                           'to 1, by default.\n\n' +
                           'Group Weight Factor:')
            result = Qt.QInputDialog.getDouble(self.view, 'Group Weight', 
                            prompt_text, value = 1, decimals = 8)
            
            if result[1]: # If OK was pressed
                knobGroupInfo['weight'] = result[0]
            else: # If Cancel was pressed
                knobGroupInfo['weight'] = 1
                
        else:
            knobGroupInfo = {}
        
        self.emit(Qt.SIGNAL("knobGroupInfoObtained"), selectedKnobs,
                  knobGroupInfo)

    #----------------------------------------------------------------------
    def _updateOnPreferencesChange(self,
                                   visible_column_name_list):
        """"""
        
        self.visible_column_name_list = \
            visible_column_name_list
        
        self.model.col_name_list = visible_column_name_list
        
        self.model._updateModel()
        
        
    #----------------------------------------------------------------------
    def _prepareForPrefFileSave(self):
        """"""
        
        self.emit(Qt.SIGNAL('sigReadyToSavePref'),
                  self.model.col_name_list)
        
        
    #----------------------------------------------------------------------
    def _prepareForConfigFileSave(self):
        """"""
        
        signal = Qt.SIGNAL('sigGotModelAndConfigNameToBeSaved')
        self.connect(self.view, signal,
                     self.fileManager.saveConfigFile)
        self.disconnect(self.view, signal,
                        self.fileManager.saveSnapshotFile)
        
        self.view._getModelAndConfigNameForSaving()
        
        
    #----------------------------------------------------------------------
    def _initModel(self):
        """"""
        
        self.model = TunerConfigSetupModel(KnobGroupList())
        
    #----------------------------------------------------------------------
    def _initView(self, modal, parentWindow):
        """"""
        
        self.view = TunerConfigSetupView(self.model,
                                         modal,
                                         parentWindow)
        
    #----------------------------------------------------------------------
    def _loadConfigFileInNewTab(self):
        """"""
        
        self.emit(Qt.SIGNAL('sigReadyToLoadConfig'), None)
                
    
    
        
        
#----------------------------------------------------------------------
def make(starting_TunerModel, **kwargs):
    """"""
    
    modal = kwargs.get('modal', True)
    parentWindow = kwargs.get('parentWindow', None)
    
    app = TunerConfigSetupApp(starting_TunerModel,
                              modal, parentWindow)
    view = app.view
    view.exec_()
    
    return app.model.output
    
#----------------------------------------------------------------------
def main(args):
    """"""

    '''
    If Qt is to be used (for any GUI) then the cothread library needs to 
    be informed, before any work is done with Qt. Without this line below,
    the GUI window will not show up and freeze the program. 
    
    Note that for a dialog box to be modal, i.e., blocking the application
    execution until user input is given, you need to set the input argument 
    "user_timer" to be True. However, if you use "use_timer", it may
    Segmentation Fault at the end of running the main function.
    '''
    qtapp = cothread.iqt(use_timer = True)
    #qtapp = cothread.iqt()
    #qtapp = Qt.QApplication(sys.argv) # use this if you are not using "cothread" module at all in your application


    starting_TunerModel = None
    
    result = make(starting_TunerModel)
    
    print result
    
    '''
    # You can use this if you are NOT using cothread, instead of
    # cothread.WaitForQuit() below.
    exit_status = config.qtapp[0].exec_()
    sys.exit(exit_status)
    '''
    
    
    cothread.WaitForQuit()
    

#----------------------------------------------------------------------    
if __name__ == "__main__" :
    main(sys.argv)
    