#! /usr/bin/env python

"""

GUI application for adjusting lattice parameters with certain ratios
between different groups of parameters.

:author: Yoshiteru Hidaka
:license:

This GUI application is a lattice turning program that allows a user to
define a set of lattice devices to be simultaneously adjusted with
certain step size ratios between them.

"""

import sys
import os

#USE_DEV_SRC = True
#if USE_DEV_SRC:
    ## Force Python to use your development modules,
    ## instead of the modules already installed on the system.
    #if os.environ.has_key('HLA_DEV_SRC'):
        #dev_src_dir_path = os.environ['HLA_DEV_SRC']

        #if dev_src_dir_path in sys.path:
            #sys.path.remove(dev_src_dir_path)
        
        #sys.path.insert(0, dev_src_dir_path)
            
    #else:
        #print 'Environment variable named "HLA_DEV_SRC" is not defined. Using default HLA.'

import datetime
import operator

import cothread

import PyQt4.Qt as Qt
import gui_icons

from Qt4Designer_files.ui_lattice_tuner import Ui_MainWindow


import TunerUtils.config as const
from TunerUtils.knob import Knob, KnobGroup, KnobGroupList
from TunerUtils.tuner_file_manager import TunerFileManager
import TunerUtils.preferencesDialogForTuner \
       as PreferencesDialogForTuner
import TunerUtils.tunerConfigSetupDialog \
       as TunerConfigSetupDialog
# from TunerUtils.channelSelectorDialog import Channel

import aphla
#if not hla.machines._lat :
    #hla.initNSLS2VSR()
from hla.catools import caget, caput

# TODO:
# *) Add Preferences info for Channel Selector GUI
# *) allow grouping/ungrouping in setup dialog
# *) eliminate duplicate knobs in a knob group list(check this in setup dialog)
# *) Use direct caget & caput for faster
# *) Accept expression for weight specification
# *) Ramping capability
# *) Cancel tab motion for "plus_tab"
# *) If config not saved to a file, ask user if want to save
# *) show asterisk if config is not saved
# *) Light version of config file (description, knob name list, corresponding knob group, weight, step size, and unit list only)
# *) Light version of snapshot file (light version of config file + snapshot pv values (read&setp) with timestamps + description)
# *) Fix bugs associated with column motion (Freeze them if not fixable)
# *) Allow read-only devices to be in config (always force weight to 0)
# *) Don't allow duplicate group names in Tuner & Tuner Config GUI
# *) Separate visual column order from model item order
# *) Add sorting ability to "visible column list available"
# *) When opening column preferences, instead of loading from
# self.visible_col_name_list, load it from the current visual column order
# *) Make COL_WEIGHT available to Tuner Config GUI


########################################################################
class TunerModel(Qt.QStandardItemModel):
    """"""

    #----------------------------------------------------------------------
    def __init__(self, knob_group_list, **kwargs):
        """Constructor"""
        
        Qt.QStandardItemModel.__init__(self, \
            parent = kwargs.get('parent',None))
        
        visible_column_name_list = kwargs.get( \
            'visible_column_name_list',
            const.DEFAULT_VISIBLE_COL_LIST)

        # Configuration-related data
        self.knobGroupList = knob_group_list
        self.config_name = ''
        self.config_description = ''

        # Snapshot-related data
        self.flat_knob_list = []
        for kg in self.knobGroupList.knobGroups:
            self.flat_knob_list.extend(kg.knobs)
        self.snapshot_read = [] # can be populated by loading snapshot file or taking a snapshot
        self.snapshot_setp = []
        self.snapshot_read_timestamp = []
        self.snapshot_setp_timestamp = []
        self.snapshot_description = ''
        
        # PV lists
        pvrb_list_of_list = \
            [k.pvrb for k in self.flat_knob_list]
        pvsp_list_of_list = \
            [k.pvsp for k in self.flat_knob_list]
        self.flat_pvrb_list = reduce(operator.add, pvrb_list_of_list)
        self.flat_pvsp_list = reduce(operator.add, pvsp_list_of_list)
        self.flat_pv_list = self.flat_pvrb_list + self.flat_pvsp_list

        # Fetch the latest PV readings
        self._getLatestPVData()

        # Store initial PV readings
        self.start_PV_read = [k.pvrb_val for k in self.flat_knob_list]
        self.start_PV_setp = [k.pvsp_val for k in self.flat_knob_list]
        
        self.isGroupBasedView = True
        
        self.nRows = 0
        
        self.col_name_dict = const.DICT_COL_NAME
        
        # Specify the visible columns in the order
        # of your preference
        self.col_name_list = visible_column_name_list
        
        self._updateModel()
        
        self._connect_itemChanged_signal(True)

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
            if p:
                group_name = str(p.text())
            else:
                model = item.model()
                group_name_col_index = \
                    self.col_name_list.index(const.COL_GROUP_NAME)
                knob_group_item = model.item(item.row(),
                                             group_name_col_index)
                group_name = str(knob_group_item.text())
            
            for i, kg in enumerate(self.knobGroupList.knobGroups):
                if group_name == kg.name:
                    knob_group = kg
                    knob_group_index = i
                    break
                    
            col_name = self.col_name_list[item.column()]

            if col_name == const.COL_WEIGHT:
                try:
                    new_weight = float(new_input)
                except ValueError:
                    item.setText(const.STR_FORMAT_WEIGHT_FACTOR
                                 % knob_group.weight)
                    Qt.QMessageBox.critical(None, 'ERROR', 
                        'You must enter a numeric value.')
                    # Re-enable the temporarily disconnected signal       
                    self._connect_itemChanged_signal(True)
                    return
                
                if (new_weight == 0.0) and (\
                    knob_group_index == self.knobGroupList.ref_index):
                    item.setText(const.STR_FORMAT_WEIGHT_FACTOR
                                 % knob_group.weight)
                    Qt.QMessageBox.critical(None, 'ERROR', 
                        ('Weight of reference group cannot be zero. ' +
                         'Change reference group, or enter non-zero weight.') )
                    # Re-enable the temporarily disconnected signal       
                    self._connect_itemChanged_signal(True)
                    return
                
                knob_group.weight = new_weight
                self.knobGroupList.updateDerivedProperties()
                
                self._updateModel()
                
            elif col_name == const.COL_STEP_SIZE:
                
                kg_list = self.knobGroupList

                step_size_list = getattr(kg_list,
                                         self.col_name_dict[col_name][1])
                previous_step_size = step_size_list[knob_group_index]
                
                try:
                    new_step_size = float(str(item.text()))
                except ValueError:
                    str_format = self.col_name_dict[col_name][2]
                    item.setText(str_format % previous_step_size)
                    Qt.QMessageBox.critical(None, 'ERROR', 
                        'You must enter a numeric value.')
                    # Re-enable the temporarily disconnected signal       
                    self._connect_itemChanged_signal(True)
                    return
                
                ref_weight = kg_list.knobGroups[kg_list.ref_index].weight
                        
                this_weight = knob_group.weight
                
                if this_weight == 0.0:
                    str_format = self.col_name_dict[col_name][2]
                    item.setText(str_format % previous_step_size)
                    Qt.QMessageBox.critical(None, 'ERROR', 
                        ('Step size must be zero for this item since its weight ' +
                         'is zero. Change to non-zero weight first before entering ' +
                         'non-zero step size.') )
                    # Re-enable the temporarily disconnected signal       
                    self._connect_itemChanged_signal(True)
                    return
                
                new_refStepSize = ref_weight*(new_step_size/this_weight)
                kg_list._changeRefStepSize(new_refStepSize)
                                        
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
                    knob.setFlags(knob.flags() & 
                                  ~Qt.Qt.ItemIsEditable) # Make the item NOT editable
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
                knob.setFlags(knob.flags() & 
                              ~Qt.Qt.ItemIsEditable) # Make the item NOT editable
                
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

        self.emit(Qt.SIGNAL('modelUpdated'), self)

    #----------------------------------------------------------------------
    def _getColumnIndex(self, column_name):
        """"""
        
        if column_name in self.col_name_list:
            return self.col_name_list.index(column_name)
        else:
            return None


    #----------------------------------------------------------------------
    def _getLatestPVData(self):
        """"""
                
        pv_data = caget(self.flat_pv_list)
        
        pvrb_data = pv_data[:len(self.flat_pvrb_list)]
        pvsp_data = pv_data[len(self.flat_pvrb_list):]
        
        for i,k in enumerate(self.flat_knob_list):
            k.pvrb_val = pvrb_data[i]
            k.pvsp_val = pvsp_data[i]

    #----------------------------------------------------------------------
    def _takeSnapshot(self):
        """"""
        
        # Ask for snapshot description here
        
        self._getLatestPVData()
        
        self.snapshot_read = [k.pvrb_val for k in self.flat_knob_list]
        self.snapshot_setp = [k.pvsp_val for k in self.flat_knob_list]
        self.snapshot_read_timestamp = [
            k.pvrb_val_time_stamp for k in self.flat_knob_list]
        self.snapshot_setp_timestamp = [
            k.pvsp_val_time_stamp for k in self.flat_knob_list]
        
        
########################################################################
class TunerView(Qt.QMainWindow, Ui_MainWindow):
    """"""

    #----------------------------------------------------------------------
    def __init__(self, model_list):
        """Constructor"""
        
        Qt.QMainWindow.__init__(self)
        
        self.model_list = model_list
        self.closingDisabled = False
    
        self.setupUi(self)
        
        self.tabWidget = EditableTabTextTabWidget(self.centralwidget)

        self.tabWidget.setGeometry(Qt.QRect(20, 10, 971, 651))
        self.tabWidget.setTabsClosable(True)
        self.tabWidget.setMovable(True)
        self.tabWidget.setObjectName("tabWidget")        
        
        # Create the special tab for adding more tabs
        self.tab_plus = Qt.QWidget()
        self.tab_plus.setObjectName("tab_plus")
        self.tab_plus.setDisabled(True)
        self.tabWidget.addTab(self.tab_plus, "")
        #
        tab_plus_index = 0
        self.tab_plus_button = Qt.QPushButton(
            Qt.QIcon(":/plus.png"),'')
        tabBar = self.tabWidget.tabBar()
        tabBar.setTabButton(tab_plus_index, Qt.QTabBar.RightSide,
                            self.tab_plus_button)
        #
        self.tabWidget.setCurrentIndex(tab_plus_index)
        
        # Add configuration tab(s)
        for m in self.model_list:
            model_to_be_replaced = None
            config_name = ''
            self._addTab(model_to_be_replaced, config_name, m)
        
        # Add layout
        self.groupBox_switch_view.setMinimumSize(Qt.QSize(181,41))
        #
        self.radioButton_knobs.setParent(self.groupBox_switch_view)
        self.radioButton_knob_groups.setParent(self.groupBox_switch_view)
        #
        button_width = 50
        button_height = 50
        icon_width = int(button_width*0.8)
        icon_height = int(button_height*0.8)
        icon_size = Qt.QSize(icon_width,icon_height)
        self.pushButton_step_up.setMinimumSize(Qt.QSize(button_width,button_height))
        self.pushButton_step_up.setMaximumSize(Qt.QSize(button_width,button_height))
        self.pushButton_step_up.setIcon(Qt.QIcon(':/up_arrow.png'))
        self.pushButton_step_up.setIconSize(icon_size)
        self.pushButton_step_up.setText('')
        self.pushButton_step_down.setMinimumSize(Qt.QSize(button_width,button_height))
        self.pushButton_step_down.setMaximumSize(Qt.QSize(button_width,button_height))
        self.pushButton_step_down.setIcon(Qt.QIcon(':/down_arrow.png'))
        self.pushButton_step_down.setIconSize(icon_size)
        self.pushButton_step_down.setText('')
        #
        horizontalLayout1 = Qt.QHBoxLayout()
        horizontalLayout1.setMargin(0)
        horizontalLayout1.setObjectName('horizontalLayout1')
        self.horizontalLayout1 = horizontalLayout1
        #
        self.horizontalLayout1.addWidget(self.radioButton_knob_groups)
        self.horizontalLayout1.addWidget(self.radioButton_knobs)
        #
        verticalLayout1 = Qt.QVBoxLayout(self.groupBox_switch_view)
        verticalLayout1.setObjectName('verticalLayout1')
        self.verticalLayout1 = verticalLayout1
        #
        self.verticalLayout1.addLayout(self.horizontalLayout1)
        #        
        spacerItem1 = Qt.QSpacerItem(40,20,Qt.QSizePolicy.Expanding,
                                     Qt.QSizePolicy.Minimum)
        spacerItem2 = Qt.QSpacerItem(40,20,Qt.QSizePolicy.Expanding, 
                                     Qt.QSizePolicy.Minimum)
        spacerItem3 = Qt.QSpacerItem(488,20,Qt.QSizePolicy.Expanding, 
                                     Qt.QSizePolicy.Minimum)
        #
        horizontalLayout2 = Qt.QHBoxLayout()
        horizontalLayout2.setObjectName('horizontalLayout2')
        self.horizontalLayout2 = horizontalLayout2
        #
        self.horizontalLayout2.addWidget(self.groupBox_switch_view)
        self.horizontalLayout2.addItem(spacerItem1)
        self.horizontalLayout2.addWidget(self.pushButton_updatePV)
        self.horizontalLayout2.addItem(spacerItem2)
        self.horizontalLayout2.addWidget(self.pushButton_step_up)
        self.horizontalLayout2.addWidget(self.pushButton_step_down)
        self.horizontalLayout2.addItem(spacerItem3)
        #
        verticalLayout2 = Qt.QVBoxLayout()
        verticalLayout2.setMargin(0)
        verticalLayout2.setObjectName('verticalLayout2')
        self.verticalLayout2 = verticalLayout2
        #
        self.verticalLayout2.addWidget(self.tabWidget)
        self.verticalLayout2.addLayout(self.horizontalLayout2)
        #
        self.gridLayout = Qt.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName('gridLayout')
        self.gridLayout.addLayout(self.verticalLayout2, 0, 0, 1, 1)
        
        # Connect signals/slots
        self.connect(self.tabWidget,
                     Qt.SIGNAL('tabCloseRequested(int)'),
                     self._closeTab);
        #
        self.connect(self.buttonGroup, 
                     Qt.SIGNAL('buttonClicked(QAbstractButton *)'),
                     self._switch_view_base)        

    
    #----------------------------------------------------------------------
    def closeEvent(self, event):
        """"""
        
        if self.closingDisabled:
            event.ignore()
    
    #----------------------------------------------------------------------
    def columnMoved(self, logicalIndex, oldVisualIndex, newVisualIndex):
        """"""
        
        current_model = self._getCurrentModel()
        
        
    #----------------------------------------------------------------------
    def _closeTab(self, tab_index):
        """"""
        
        # If the tab about to be closed is the special tab that
        # add a new tab, then ignore the close reqest.
        tab_plus_index = self.tabWidget.indexOf(self.tab_plus)
        if tab_index != tab_plus_index:
            w = self.tabWidget.widget(tab_index)
            model_to_be_removed = w.findChild(Qt.QTreeView).model()
            self.emit(Qt.SIGNAL('sigRemoveModel'),
                      model_to_be_removed)
            self.tabWidget.removeTab(tab_index);

    #----------------------------------------------------------------------
    def _addTab(self, model_to_be_replaced, tab_name, 
                model_to_be_added):
        """"""

        nTabs = self.tabWidget.count()
        
        if tab_name:
            new_tab_name = tab_name
        else:
            new_tab_name = 'Config ' + str(nTabs)
        
        if model_to_be_replaced:
            model_list = []
            tab_index_list = []
            for tab_index in range(nTabs):
                tree = self.tabWidget.widget(tab_index).findChild(Qt.QTreeView)
                if tree:
                    model_list.append(tree.model())
                    tab_index_list.append(tab_index)
            
            tab_index_to_be_replaced = tab_index_list[
                model_list.index(model_to_be_replaced)]
            
            self.tabWidget.removeTab(tab_index_to_be_replaced)
            
            tab_index_to_be_inserted = tab_index_to_be_replaced
            
        else:
            tab_plus_index = self.tabWidget.indexOf(self.tab_plus)
            
            tab_index_to_be_inserted = tab_plus_index
                
        new_tab = Qt.QWidget()
        new_tab.setObjectName(new_tab_name)
        new_treeView = Qt.QTreeView(new_tab)
        new_treeView.setGeometry(Qt.QRect(20, 10, 931, 591))
        new_treeView.setMidLineWidth(0)
        new_treeView.setAlternatingRowColors(True)
        new_treeView.setRootIsDecorated(True)
        new_treeView.setSelectionMode(Qt.QAbstractItemView.ExtendedSelection)
        verticalLayout = Qt.QVBoxLayout(new_tab)
        verticalLayout.addWidget(new_treeView) # Allow the TreeView to expand together with the tab
        new_tab_index = self.tabWidget.insertTab(tab_index_to_be_inserted,
                                                 new_tab, new_tab_name)
        self.tabWidget.setCurrentIndex(new_tab_index)
    
        
        ## FIXIT:
        ## If activated, and tab moved to the right of tab_plus, then
        ## it ends up with infinite recursion error.
        #self.connect(self.tabWidget.tabBar(), 
                     #Qt.SIGNAL('tabMoved(int,int)'),
                     #self._cancelTabMotionForPlusTab)
        
        
        new_treeView.setModel(model_to_be_added)
    
        self._expandAll_and_resizeColumn(new_treeView)
        
        self.connect(new_treeView.header(), 
                     Qt.SIGNAL('sectionMoved(int,int,int)'),
                     self.columnMoved)
        
        self.connect(model_to_be_added, Qt.SIGNAL('modelUpdated'),
                     self._expandAll_and_resizeColumn)
        
    #----------------------------------------------------------------------
    def _expandAll_and_resizeColumn(self, treeView_or_model):
        """"""

        if isinstance(treeView_or_model, Qt.QTreeView):
            treeView = treeView_or_model
        else:
            model = treeView_or_model

            treeView_list = self.tabWidget.findChildren(Qt.QTreeView)
            model_list = [t.model() for t in treeView_list]
            
            for i, t in enumerate(treeView_list):
                if model_list[i] == model:
                    treeView = t
                    break

        treeView.expandAll()
        treeView.resizeColumnToContents(0)

    
    #----------------------------------------------------------------------
    def _switch_view_base(self, button):
        """"""
        
        treeView_list = self.tabWidget.findChildren(Qt.QTreeView)
        model_list = [t.model() for t in treeView_list]
        
        if not model_list:
            return
        
        current_model = self._getCurrentModel()
        
        if current_model:
            # When a tab with a TreeView is currently being selected,
            # change the order of the model and TreeView list so
            # that the selected one will be processed first
            current_model_index = model_list.index(current_model)
        
            model_list.remove(current_model)
            model_list.insert(0, current_model)
            current_treeView = treeView_list.pop(current_model_index)
            treeView_list.insert(0, current_treeView)
        else: # When "plus_tab" is being currently selected
            pass

        if button == self.radioButton_knobs:
            isGroupBasedView = False
        elif button == self.radioButton_knob_groups:
            isGroupBasedView = True
        else:
            raise Exception, "Unknown button press received."
        
        for index in range(len(model_list)):
            m = model_list[index]
            treeView = treeView_list[index]
            
            m.isGroupBasedView = isGroupBasedView
            m._updateModel()
            
        
    #----------------------------------------------------------------------
    def _getCurrentTreeView(self):
        """"""
        
        current_widget = self.tabWidget.currentWidget()
        
        return current_widget.findChild(Qt.QTreeView)

    #----------------------------------------------------------------------
    def _getCurrentModel(self):
        """"""
    
        current_TreeView = self._getCurrentTreeView()
        
        if current_TreeView:
            return current_TreeView.model()
        else:
            return None

    #----------------------------------------------------------------------
    def _cancelTabMotionForPlusTab(self, from_index, to_index):
        """"""
        
        tab_plus_index = self.tabWidget.indexOf(self.tab_plus)
        
        if to_index == tab_plus_index:
            self.tabWidget.tabBar().moveTab(to_index, from_index)
        
    
########################################################################
class TunerApp(Qt.QObject):
    """"""

    #----------------------------------------------------------------------
    def __init__(self, **kwargs):
        """Constructor"""
        
        Qt.QObject.__init__(self)
        
        # Setting "default" visible column name list
        # (either hard-coded default list or user-specified
        # default list)
        self.visible_column_name_list = kwargs.get(
            'visible_column_name_list',
            const.DEFAULT_VISIBLE_COL_LIST)
                
        self._initModelList()
        self._initView()
        self._initFileManager()
        
        # Connections related to open the new configuration
        # setup dialog.
        self.connect(self.view.tab_plus_button,
                     Qt.SIGNAL('clicked()'),
                     self._launchConfigSetupDialog)
        self.connect(self.view.actionNewConfig,
                     Qt.SIGNAL('triggered()'),
                     self._launchConfigSetupDialog)
        self.connect(self, Qt.SIGNAL('configDataLoaded'),
                     self._addModel)
        
        # Connections related to Preferences change
        self.connect(self.view.actionPreferences,
                     Qt.SIGNAL('triggered()'),
                     self._launchPrefDialog)
        self.connect(self,
                     Qt.SIGNAL('readyForUpdateOnPrefChange'),
                     self._updateOnPreferencesChange)


        self.connect(self.view, Qt.SIGNAL('sigRemoveModel'),
                     self._removeModel)
        
        
        
        self.connect(self.view.pushButton_updatePV,
                     Qt.SIGNAL('clicked()'),
                     self._updatePVData)
        
        self.connect(self.view.pushButton_step_up, 
                     Qt.SIGNAL('clicked()'),
                     self.step_up)
        self.connect(self.view.pushButton_step_down, 
                     Qt.SIGNAL('clicked()'),
                     self.step_down)

    #----------------------------------------------------------------------
    def step_up(self):
        """"""
        
        m = self.view._getCurrentModel()
        
        m._getLatestPVData()
        
        kg_list = m.knobGroupList
        step_size_list = kg_list.step_size_list
        flat_step_size_list = []
        for (i,kg) in enumerate(kg_list.knobGroups):
            flat_step_size_list.extend(
                [step_size_list[i]]*len(kg.knobs))
        
        current_pvsp_val_list = [k.pvsp_val for k in m.flat_knob_list]
        target_pvsp_val_list = map(operator.add,
                                   current_pvsp_val_list,
                                   flat_step_size_list)
        
        caput(m.flat_pvsp_list, target_pvsp_val_list)
        
        m._getLatestPVData()

        m._updateModel()
        
        
    #----------------------------------------------------------------------
    def step_down(self):
        """"""
        
        m = self.view._getCurrentModel()
        
        m._getLatestPVData()
        
        kg_list = m.knobGroupList
        step_size_list = kg_list.step_size_list
        flat_step_size_list = []
        for (i,kg) in enumerate(kg_list.knobGroups):
            flat_step_size_list.extend(
                [step_size_list[i]]*len(kg.knobs))
        
        current_pvsp_val_list = [k.pvsp_val for k in m.flat_knob_list]
        target_pvsp_val_list = map(operator.sub,
                                   current_pvsp_val_list,
                                   flat_step_size_list)
        
        caput(m.flat_pvsp_list, target_pvsp_val_list)
        
        m._getLatestPVData()

        m._updateModel()

    #----------------------------------------------------------------------
    def _initModelList(self):
        """"""
        
        self.model_list = []
        
    #----------------------------------------------------------------------
    def _initView(self):
        """"""
        
        self.view = TunerView(self.model_list)
        
    #----------------------------------------------------------------------
    def _initFileManager(self):
        """"""
        
        self.fileManager = TunerFileManager()
        
        # Connections related to saving configuration to file
        self.connect(self.view.actionSaveConfigFile, 
                     Qt.SIGNAL('triggered()'),
                     self._prepareForConfigFileSave)
        self.connect(self, Qt.SIGNAL('readyToSendSaveConfigRequest'),
                     self._sendSaveConfigRequestFromTunerApp)

        # Connections related to loading configuration from file
        self.connect(self.view.actionLoadConfigFileInNewTab, 
                     Qt.SIGNAL('triggered()'),
                     self._loadConfigFileInNewTab)
        self.connect(self.view.actionLoadConfigFileInCurrentTab, 
                     Qt.SIGNAL('triggered()'),
                     self._loadConfigFileInCurrentTab)
        self.connect(self, Qt.SIGNAL('readyToLoadConfig'),
                     self.fileManager.loadConfigFile)
        self.connect(self.fileManager, Qt.SIGNAL('configFileLoaded'),
                     self._addModel)

        # Connections related to saving snapshot to file
        self.connect(self.view.actionSaveSnapshotFile, 
                     Qt.SIGNAL('triggered()'),
                     self._prepareForSnapshotFileSave)
        self.connect(self, Qt.SIGNAL('readyToSendSaveSnapshotRequest'),
                     self._sendSaveSnapshotRequestFromTunerApp)

        # Connections related to loading snapshot from file
        self.connect(self.view.actionLoadSnapshotFileInNewTab, 
                     Qt.SIGNAL('triggered()'),
                     self._loadSnapshotFileInNewTab)
        self.connect(self.view.actionLoadSnapshotFileInCurrentTab,
                     Qt.SIGNAL('triggered()'),
                     self._loadSnapshotFileInCurrentTab)
        self.connect(self, Qt.SIGNAL('readyToLoadSnapshot'),
                     self.fileManager.loadSnapshotFile)
        self.connect(self.fileManager, Qt.SIGNAL('snapshotFileLoaded'),
                     self._addModel)

    #----------------------------------------------------------------------
    def _updatePVData(self):
        """"""
        
        m = self.view._getCurrentModel()
        m._getLatestPVData()
        m._updateModel()
        
        
    #----------------------------------------------------------------------
    def _prepareForConfigFileSave(self):
        """"""
        
        current_model = self.view._getCurrentModel()
        
        if current_model:
            # Update "config_name"
            tabBar = self.view.tabWidget.tabBar()
            current_model.config_name = tabBar.tabText(tabBar.currentIndex())
            
            self.emit(Qt.SIGNAL('readyToSendSaveConfigRequest'),
                      current_model)
        else:
            Qt.QMessageBox.critical(None, 'ERROR',
                'A configuration tab to be saved must be selected.')
    
    #----------------------------------------------------------------------
    def _sendSaveConfigRequestFromTunerApp(self, model_to_be_saved):
        """"""
        
        self.fileManager.saveConfigFile(model_to_be_saved)
        
    #----------------------------------------------------------------------
    def _prepareForSnapshotFileSave(self):
        """"""
        
        current_model = self.view._getCurrentModel()
        
        if current_model:
            # Update "config_name"
            tabBar = self.view.tabWidget.tabBar()
            current_model.config_name = tabBar.tabText(tabBar.currentIndex())
            
            self.emit(Qt.SIGNAL('readyToSendSaveSnapshotRequest'),
                      current_model)
        else:
            Qt.QMessageBox.critical(None, 'ERROR',
                'A configuration tab for which a snapshot will be saved must be selected.')
            
    #----------------------------------------------------------------------
    def _sendSaveSnapshotRequestFromTunerApp(self, model_to_be_saved):
        """"""
        
        self.fileManager.saveSnapshotFile(model_to_be_saved)

    #----------------------------------------------------------------------
    def _loadConfigFileInNewTab(self):
        """"""
        
        model_to_be_replaced = None
        
        self.emit(Qt.SIGNAL('readyToLoadConfig'), 
                  model_to_be_replaced)
    
    #----------------------------------------------------------------------
    def _loadConfigFileInCurrentTab(self):
        """"""
        
        model_to_be_replaced = self.view._getCurrentModel()
        
        self.emit(Qt.SIGNAL('readyToLoadConfig'),
                  model_to_be_replaced)

    #----------------------------------------------------------------------
    def _loadSnapshotFileInNewTab(self):
        """"""
        
        model_to_be_replaced = None
        
        self.emit(Qt.SIGNAL('readyToLoadSnapshot'), 
                  model_to_be_replaced)

    #----------------------------------------------------------------------
    def _loadSnapshotFileInCurrentTab(self):
        """"""
        
        model_to_be_replaced = self.view._getCurrentModel()
        
        self.emit(Qt.SIGNAL('readyToLoadSnapshot'),
                  model_to_be_replaced)
        
    #----------------------------------------------------------------------
    def _launchConfigSetupDialog(self):
        """"""
        
        starting_TunerModel = None
        result = TunerConfigSetupDialog.make(
            starting_TunerModel)
                
        if not result: # Dialog cancelled
            return
        
        model_to_be_replaced = None
        snapshot_data = {}
        self.emit(Qt.SIGNAL('configDataLoaded'),
                  model_to_be_replaced,
                  result['config_data'],
                  snapshot_data,
                  result['saveFileFlag'])

    #----------------------------------------------------------------------
    def _launchPrefDialog(self):
        """"""
        
        full_string_list = const.COL_ALL_NAMES
        
        current_model = self.view._getCurrentModel()
        if current_model:
            current_selected_string_list = current_model.col_name_list
        else:
            current_selected_string_list = self.visible_column_name_list
        
        result = PreferencesDialogForTuner.make(
            full_string_list, 
            permanently_selected_string_list = 
            const.ALWAYS_VISIBLE_COL_LIST,
            selected_string_list =
            current_selected_string_list,
            output_type = 
            PreferencesDialogForTuner.OUTPUT_TYPE_STRING_LIST)
        
        if not result: # Dialog cancelled
            return
        
        self.emit(Qt.SIGNAL('readyForUpdateOnPrefChange'),
                  result['selected_list'],
                  result['checkedSetAsDefault'],
                  result['checkedApplyToAllTabs'])

    #----------------------------------------------------------------------
    def _updateOnPreferencesChange(self,
                                   visible_column_name_list,
                                   checkedSetAsDefault,
                                   checkedApplyToAllTabs):
        """"""
        
        current_model = self.view._getCurrentModel()
        
        if checkedSetAsDefault or (not current_model):
            self.visible_column_name_list = visible_column_name_list
        
        treeView_list = self.view.tabWidget.findChildren(Qt.QTreeView)

        if current_model:
            current_model.col_name_list = visible_column_name_list
            current_model._updateModel()
            #current_treeView = [t for t in treeView_list
            #                    if t.model() == current_model][0]
            #self.view._expandAll_and_resizeColumn(current_treeView)

        if checkedApplyToAllTabs:
            other_models = self.model_list
            if current_model:
                other_models.remove(current_model)
            
            for m in other_models:
                m.col_name_list = visible_column_name_list
                m._updateModel()
                #treeView = [t for t in treeView_list
                #            if t.model() == m][0]
                #self.view._expandAll_and_resizeColumn(treeView)
        
    #----------------------------------------------------------------------
    def _addModel(self, model_to_be_replaced, config_data,
                  *args):
        """"""
        
        for k in config_data.keys():
            globals()[k] = config_data[k]
        
        if len(args) == 2:
            snapshot_data = args[0]
            saveFileFlag  = args[1]
        elif len(args) == 1:
            snapshot_data = args[0]
            saveFileFlag  = False
        else:
            snapshot_data = {}
            saveFileFlag  = False
        
        
        if visible_col_list:
            new_model = TunerModel(knobGroupList,
                visible_column_name_list = visible_col_list)
        else:
            new_model = TunerModel(knobGroupList)
            
        new_model.config_description = config_description
        
        if snapshot_data:
            for k in snapshot_data.keys():
                setattr(new_model, k, snapshot_data[k])
                
        
        if model_to_be_replaced:
            index = self.model_list.index(model_to_be_replaced)
            self.model_list.insert(index, new_model)
            self.model_list.remove(model_to_be_replaced)
        else:
            self.model_list.append(new_model)
        
        
        self.view._addTab(model_to_be_replaced, config_name,
                          new_model)

        if saveFileFlag:
            self._prepareForConfigFileSave()
        
    #----------------------------------------------------------------------
    def _removeModel(self, model):
        """"""
        
        self.model_list.remove(model)

        
########################################################################
class EditableTabTextTabWidget(Qt.QTabWidget):
    """"""

    #----------------------------------------------------------------------
    def __init__(self, *args):
        """Constructor"""
        
        super(EditableTabTextTabWidget,self).__init__(*args)
    
        tabBar = EditableTabTextTabBar()
        self.setTabBar(tabBar)
    
        
########################################################################
class EditableTabTextTabBar(Qt.QTabBar):
    """"""

    #----------------------------------------------------------------------
    def __init__(self, *args):
        """Constructor"""
        
        super(EditableTabTextTabBar,self).__init__(*args)
        
        self._lineEdit = LineEditForTabText()
        
        self.selectedTabIndexHistory = [0, 0]
        
        self.connect(self._lineEdit, Qt.SIGNAL('newTabTextEntered'),
                     self.setCurrentTabText)
        
    #----------------------------------------------------------------------
    def mouseDoubleClickEvent(self, event):
        """"""
    
        # Ignore the double-click event, if the "tab_plus" tab was
        # double-clicked.
        if self.tabText(self.currentIndex()) != '':
            self._lineEdit.setText(self.tabText(self.currentIndex()))
            self._lineEdit.move(self.mapToGlobal(event.pos()))
                    
    #----------------------------------------------------------------------
    def setCurrentTabText(self, text):
        """"""
        
        self.setTabText(self.currentIndex(), text)
    
                
    #----------------------------------------------------------------------
    def mousePressEvent(self, event):
        """"""
        
        super(EditableTabTextTabBar,self).mousePressEvent(event)
        
        if self.tabText(self.currentIndex()) == '':
            self.setCurrentIndex(self.selectedTabIndexHistory[0])
        
    
    
########################################################################
class LineEditForTabText(Qt.QLineEdit):
    """"""

    #----------------------------------------------------------------------
    def __init__(self, *args):
        """Constructor"""
        
        super(LineEditForTabText, self).__init__(*args)
        
        self.connect(self, Qt.SIGNAL('editingFinished()'),
                     self.publishText)
        self.setWindowFlags(Qt.Qt.CustomizeWindowHint)
        
    #----------------------------------------------------------------------
    def setText(self, new_text):
        """"""
        
        super(LineEditForTabText, self).setText(new_text)
        self.setFocus()
        self.selectAll()
        self.show()
        
    #----------------------------------------------------------------------
    def keyPressEvent(self, event):
        """"""
    
        super(LineEditForTabText, self).keyPressEvent(event)
        if (event.key() == Qt.Qt.Key_Escape):
            self.setText('')
            self.hide()
   
    #----------------------------------------------------------------------
    def focusOutEvent(self, event):
        """"""
    
        super(LineEditForTabText,self).focusOutEvent(event)
        
        self.emit(Qt.SIGNAL('editingFinished()'))
        
    #----------------------------------------------------------------------
    def publishText(self):
        """"""
        
        if (self.text() != ''):
            self.emit(Qt.SIGNAL('newTabTextEntered'), self.text())
        self.hide()

    
#----------------------------------------------------------------------
def make():
    """"""
    
    app = TunerApp()
    app.view.show()
    
    return app
    
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

    
    app = make()
    
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
    