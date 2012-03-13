#! /usr/bin/env python

"""

GUI application for selecting HLA channel(s) interactively

:author: Yoshiteru Hidaka
:license:

This GUI application is a dialog that allows users to see all the available
channels, narrow them down by search filtering, and finally select the channels
of interest and return the selected channels as an input to another function
or GUI application.

Here, a channel is defined by an element and its field name such as None,
x, or y.

Furthermore, a channel can be sub-classified as the following depending on the
read/write properties:
1) Indicator = A channel with a read PV only (no write PV). Examples include BPM and Hall probes.
2) Knob = A channel with a write PV. A knob can have a read PV, but is not required
to have a read PV. A knob simply needs to be able to change setpoints.

"""

import sys

USE_DEV_SRC = True
if USE_DEV_SRC:
    # Force Python to use your development modules,
    # instead of the modules already installed on the system.
    import os
    if os.environ.has_key('HLA_DEV_SRC'):
        dev_src_dir_path = os.environ['HLA_DEV_SRC']

        if dev_src_dir_path in sys.path:
            sys.path.remove(dev_src_dir_path)
        
        sys.path.insert(0, dev_src_dir_path)
            
    else:
        print 'Environment variable named "HLA_DEV_SRC" is not defined. Using default HLA.'

import fnmatch
from operator import and_, not_

import cothread

import PyQt4.Qt as Qt

if __name__ == "__main__" :
    from ui_channelSelectorDialog import Ui_Dialog
else:
    from .ui_channelSelectorDialog import Ui_Dialog

#import tictoc
import hla
if not hla.machines._lat :
    #tStart = tictoc.tic()    
    hla.initNSLS2VSR()
    #print tictoc.toc(tStart)
#import aphla
#if not aphla.machines._lat :
    ##tStart = tictoc.tic()
    #aphla.initNSLS2VSR()
    ##print tictoc.toc(tStart)

# Output Type Enums
TYPE_CHANNEL = 1
TYPE_NAME    = 2

# FIXIT:
#

# TODO:
# 1) Create a tab for each selection, and allow OR operation
# to different tabs.

########################################################################
class Channel:
    """"""

    #----------------------------------------------------------------------
    def __init__(self, element_obj, field_name):
        """
        """
        
        if field_name not in ['value', 'x', 'y']:
            raise ValueError('Field name (' + field_name + ') passed as ' +
                             '2nd argument must be ' + 
                             'either "value", "x", or "y".')
        
        if field_name not in element_obj.fields():
            raise ValueError('Field name (' + field_name + ') passed as ' +
                             '2nd argument does not match any of field ' +
                             'names for the Element object passed as 1st ' +
                             'argument.')
        
        self.name = element_obj.name + '.' + field_name
        
        self.elem_name = element_obj.name
        self.field_name = field_name
        
        self.pvrb = element_obj._field[field_name].pvrb
        self.pvsp = element_obj._field[field_name].pvsp
        
        '''
        if (len(self.pvrb) >= 2) or (len(self.pvsp) >= 2):
            raise ValueError('Field name (' + field_name + ') passed as ' +
                             '2nd argument returned more than one PV. ' +
                             'Change field name.')
        '''
        
        
        if not self.pvsp:
            self.read_only = True
            
            if not self.pvrb:
                raise ValueError('Element object passed as 1st argument ' +
                                 'is not associated with any PV.')
        else:
            self.read_only = False
        
        list_of_elem_prop_to_be_copied = [
            'devname', 'cell', 'family', 'girder', 'group', 'index',
            'length', 'phylen', 'sb', 'se', 'symmetry', 'virtual',
            'sequence']
        
        for prop in list_of_elem_prop_to_be_copied:                   
            setattr(self, prop, getattr(element_obj,prop))
        
    #----------------------------------------------------------------------
    @staticmethod
    def getAllAvailableChannelsFromElement(element_obj):
        """"""
        
        field_list = element_obj.fields()
        
        field_list.remove('status') # 'status' does not exist in aphla, but did exist in hla
        
        if field_list == ['value']: # When there is no field other than 'value'.
            # This case usually applies to an element that has no separate 
            # control in different orientations 'x' and 'y', e.g., a quadrupole.
            channel_list = [Channel(element_obj, 'value')]
        else:
            
            if 'value' in field_list:
                field_list.remove('value')
            else:
                raise ValueError('Passed element object does not contain "value" field.')
            
            channel_list = []
            
            for field in field_list:
                channel_list.append(Channel(element_obj,field))
            
        
        return channel_list
        
    #----------------------------------------------------------------------
    @staticmethod
    def getAllAvailableChannelsFromElementList(element_obj_list):
        """"""
        
        list_of_channel_list = [Channel.getAllAvailableChannelsFromElement(e)
                                for e in element_obj_list]
        
        import operator
        channel_list = reduce(operator.add, list_of_channel_list)
        
        return channel_list
    
    
########################################################################
class ChannelSelectorModel(Qt.QObject):
    """"""

    #----------------------------------------------------------------------
    def __init__(self, filter_spec = [ [{},False] ]):
        """
        The optional input argument "filter_spec" must be either an empty
        list, or a list of lists, each of contains a dictionary and a bool. 
        The keys of each dictionary must be property names of the Element
        object. The bool is the exclusion flag. If true, then the matching is
        reversed. The values of each dictionary are user-supplied filter
        strings. When the argument is empty, there will be no initial
        filtering. If not empty, filtering specified by each dictionary and
        exclusion flag will be applied in the order the dictionary appears
        in the list.
        
        For example, "filter_spec" may look like
        
        filter_spec = [ [{'family':'*COR', 'cell':'C01'}, False],
                        [{'family':'H*'}                , True ] ]
                        
        Then, the initial filtering proceeds as follows. First, filtering
        of '*COR' on 'family' and 'C01' on 'cell' will be applied. The
        application ordering depends on the order the dictionary iterates
        the items, i.e., unpredictable, but the result does not change.
        Since the exclusion flag is False for this tuple, selection will
        not be reversed. The resulting list is saved to self.matched[0].
        
        As a second step, filtering of 'H*' on 'family' will be applied on
        ALL THE ELEMENTS, NOT on the elements based on self.matched[0].
        This filtered result will be now reversed, because the exclusion
        flag for this tuple is True. The resulting list is saved to
        self.matched[1].
        
        Finally, we will take intersection of self.matched[0] & self.matched[1]
        to come up with the final filtered list self.combined_matched.
                        
        """
        
        Qt.QObject.__init__(self)
        
        # key   = property name of a Channel (indicator [read-only] or knob [writeable])
        # value = displayed column name for tables showing choices and matches
        self.ch_property_vs_col_name = \
            {'name':'Ch. Name', 'read_only':'Read-Only', 
             'elem_name':'Elem. Name', 'field_name':'Field',
             'devname':'Dev. Name', 'cell':'Cell', 'family':'Family', 
             'girder':'Girder', 'group':'Group', 'index':'Lat. Index', 
             'length':'Eff.Len', 'phylen':'Phys. Len.',
             'pvrb':'PV RB', 'pvsp':'PV SP', 'sb':'sb', 'se':'se', 
             'symmetry':'Symmetry', 'virtual':'Virtual', 'sequence':'Sequence'}
        
        # key   = property name of Channel object & exclusion flag
        # value = displayed column name for table showing filters
        self.filter_property_vs_col_name = \
            self.ch_property_vs_col_name.copy()
        self.filter_property_vs_col_name.update({'exclude':'Excl.'}) # adding extra column
        
        # Specify the default column order you want for tables showing
        # choices and matches.
        self.ch_property_list = ['name', 'read_only', 'elem_name',
                                 'field_name', 'family',
                                 'devname', 'cell',
                                 'girder', 'symmetry', 'group', 'virtual',
                                 'sb', 'se', 'pvrb', 'pvsp', 'length', 'phylen',
                                 'index', 'sequence']
        self.col_name_list = [self.ch_property_vs_col_name[prop]
                         for prop in self.ch_property_list]
        self.choice_dict = dict.fromkeys(self.ch_property_list)
        
        # Specify the default column order you want for table showing
        # filters.
        self.filter_property_list = self.ch_property_list[:]
        self.filter_property_list.insert(0, 'exclude')
        self.filter_col_name_list = [self.filter_property_vs_col_name[prop]
                         for prop in self.filter_property_list]
        self.filter_dict = dict.fromkeys(self.filter_property_list)
        
        self.numeric_filter_list = ['index', 'phylen', 'length', 'sb', 'se']
        self.not_implemented_filter_list = ['sequence']
        
        self.filter_spec = filter_spec
        
        allElements = hla.getElements('*')
        self.allChannels = Channel.getAllAvailableChannelsFromElementList(
            allElements)
        full_channel_name_list = [c.name for c in self.allChannels]
        if len(full_channel_name_list) != len(set(full_channel_name_list)):
            raise Exception, "Duplicate channel name found."
        
        # Initialization of matching data information
        self.matched = [ [True]*len(self.allChannels) ]
        self.combine_matched_list()
        self.update_choice_dict()
        
        # Apply initial filters provided by a user, if any.
        if self.filter_spec:
            isCaseSensitive = False
            self.filterData(range(len(self.filter_spec)), isCaseSensitive)
        
        self.selectedChannels = []
        
        self.output = []
    
    #----------------------------------------------------------------------
    def combine_matched_list(self):
        """"""
        
        nFilterGroups = len(self.filter_spec)
        
        if not self.filter_spec:
            self.combined_matched = [True]*len(self.allChannels)
        elif nFilterGroups == 1:
            self.combined_matched = self.matched[0]
        elif nFilterGroups == 2:
            self.combined_matched = map(and_, self.matched[0], self.matched[1])
        elif nFilterGroups >= 3:
            self.combined_matched = map(and_, self.matched[0], self.matched[1])
            for i in range(2,nFilterGroups):
                self.combined_matched = map(and_, self.combined_matched,
                                            self.matched[i])
    
    #----------------------------------------------------------------------
    def patternFilterData(self, filter_group_index, isCaseSensitive = False):
        """

        Perform only pattern match filtering here. This function does not
        perform inversion filtering.
        
        filter_group_index = Row index of the filter table. It represents 
                             the index of self.filter_spec list.
        
        """

        index = filter_group_index # short-hand notation
        
        pattern_filter_dict = self.filter_spec[index][0]
                
        # Initialization: Remove all filters
        self.matched[index] = [True]*len(self.allChannels)
            
        for (prop, val) in pattern_filter_dict.iteritems():
            if prop in self.not_implemented_filter_list:
                pass
            elif prop in self.numeric_filter_list: # numerical filter
                pass
            else: # string filter
                    
                matchedItemsZipped = [ 
                    (j,elem) for (j,elem) in enumerate(self.allChannels)
                    if self.matched[index][j] ]
                    
                if matchedItemsZipped: # When there are some matched channels
                    matchedItemsUnzipped = zip(*matchedItemsZipped)
                    matchedInd      = list(matchedItemsUnzipped[0])
                    matchedChannels = list(matchedItemsUnzipped[1])
                else: # When there is no matched item, no need for futher filtering
                    self.matched[index] = [False]*len(self.allChannels)
                    return
                    
                '''
                The reason why __str__() is being used here to retrieve
                strings is that this method can handle None values as
                well.
                '''
                if not isCaseSensitive: # case-insensitive search
                    filter_str = val.upper()
                    matchedChStrings = [ 
                        getattr(getattr(e,prop),'__str__')().upper()
                        for e in matchedChannels]
                else: # case-sensitive search
                    filter_str = val
                    matchedChStrings = [
                        getattr(getattr(e,prop),'__str__')()
                        for e in matchedChannels]
                
                reducedNewMatchedInd = [ 
                    j for (j,s) in enumerate(matchedChStrings)
                    if fnmatch.fnmatchcase(s,filter_str)]
                    
                newMatchedInd = [matchedInd[j] 
                                 for j in reducedNewMatchedInd]
                    
                self.matched[index] = [ 
                    (j in newMatchedInd) 
                    for j in range(len(self.allChannels))]
                    
                    
    #----------------------------------------------------------------------
    def filterData(self, filter_group_indices, isCaseSensitive = False):
        """
        
        Data filtering is done by 2 steps for each filter group.
        
        First, all the filters using pattern matching, i.e, string and
        numerical matching, are performed. Then, the inversion filtering
        is applied to the filtered result, if exclude flag is True.
        
        Repeat this for each filter group. Then combine each filter
        group result with logical AND operation to get the final filtered
        result.
        
        filter_group_indices = Row indices of the filter table. It is a list
                               of indices of the self.filter_spec list.
                               
        """
        
        for index in filter_group_indices:
            
            self.patternFilterData(index, isCaseSensitive)
        
            exclude_flag = self.filter_spec[index][1]
            if exclude_flag:
                self.matched[index] = map(not_, self.matched[index])
        
        
        self.combine_matched_list()
        
        self.update_choice_dict()
        
        self.emit(Qt.SIGNAL("sigDataFiltered"),())
        
    
    
    #----------------------------------------------------------------------
    def add_row_to_filter_spec(self):
        """"""
        
        self.filter_spec.append( [{},False] )
        
        self.matched.append( [True]*len(self.allChannels) )
        
        # self.combined_matched stays the same
        
    #----------------------------------------------------------------------
    def modify_filter_spec(self, filter_property_index, filter_val,
                           filter_group_index, isCaseSensitive):
        """"""

        filter_property = self.filter_property_list[filter_property_index]
        
        if filter_property is not 'exclude':
            if filter_val: # If not empty string
                self.filter_spec[filter_group_index][0][filter_property] = \
                    filter_val
            else: # If empty string, then remove the filter to save some data filtering time
                del self.filter_spec[filter_group_index][0][filter_property]
        else:
            self.filter_spec[filter_group_index][1] = filter_val
        
        # Request re-doing all the filtering with the modified filter spec.
        self.emit(Qt.SIGNAL("sigReadyForFiltering"), 
                  [filter_group_index], isCaseSensitive)
    
    #----------------------------------------------------------------------
    def update_choice_dict(self):
        """"""
        
        # Get only matched channels from all the channels
        matchedChannels = [self.allChannels[i] 
                           for (i,matched) in enumerate(self.combined_matched)
                           if matched]
        
        # If there is no match
        if not matchedChannels:
            for prop in self.ch_property_list:
                self.choice_dict[prop] = []
            return
        
        # If there is some matched channel(s)
        for prop in self.ch_property_list:
            if callable(getattr(matchedChannels[0],prop)): # if property is a function
                prop_val_list = [getattr(e,prop)() for e in matchedChannels]
            else: # if property is a value
                prop_val_list = [getattr(e,prop)   for e in matchedChannels]
            # Since prop_val_list may contain lists inside, we must remove
            # those items from the list before we can apply set()
            # to find unique elements.
            nested_list_indices = [i for (i,val) in enumerate(prop_val_list) 
                                   if isinstance(val,list)]
            hashable_list = [item for (i,item) in enumerate(prop_val_list)
                             if i not in nested_list_indices]
            nonhashable_list = [item for (i,item) in enumerate(prop_val_list)
                                if i in nested_list_indices]
            unique_prop_val_set = set(hashable_list)
            unique_prop_val_list = list(unique_prop_val_set)
            # TODO: also check if nonhashable_list contains duplicate items
            unique_prop_val_list.extend(nonhashable_list)
            unique_prop_val_list.sort()
            self.choice_dict[prop] = unique_prop_val_list
                        
            # print prop, len(self.choice_dict[prop])
        
            
    #----------------------------------------------------------------------
    def update_selected_channels(self, selectedRowIndList):
        """"""
        
        # Update currently selected channels before exiting the dialog
        matchedChannelList = [
            self.allChannels[i] 
            for (i,matched) in enumerate(self.combined_matched)
            if matched] 
        self.selectedChannels = [matchedChannelList[i] 
                                 for i in selectedRowIndList]
        
        self.emit(Qt.SIGNAL("sigReadyForClosing"),())

                
        

########################################################################
class ChannelSelectorView(Qt.QDialog, Ui_Dialog):
    """"""
    
    #----------------------------------------------------------------------
    def __init__(self, model, modal, output_type, parentWindow = None):
        """Constructor"""
        
        Qt.QDialog.__init__(self, parent = parentWindow)
        
        self.setWindowFlags(Qt.Qt.Window) # To add Maximize & Minimize buttons
        
        self.model = model
        
        self.output_type = output_type
        
        # Set up the user interface from Designer
        self.setupUi(self)
    
        self.setModal(modal)
        
        self.max_auto_adjust_column_width = 100
        
        self._initFilterTable()
        self._initChoiceTable()
        self._initMatchTable()
        
        self.update_tables()
        
        self.update_matched_and_selected_numbers()
        
    
    #----------------------------------------------------------------------
    def _initFilterTable(self):
        """
        Perform initial population and formating for tableWidget_filter
        """

        t = self.tableWidget_filter # shorthand notation

        ### Header population & properties
        nCols = len(self.model.filter_col_name_list)
        t.setColumnCount(nCols)
        
        t.setHorizontalHeaderLabels(self.model.filter_col_name_list)

        t.horizontalHeader().setMovable(True)
        
        ### Item population
        nRows = len(self.model.filter_spec)
        t.setRowCount(nRows)
        for (j, spec) in enumerate(self.model.filter_spec):
            for (i, filter_prop) in enumerate(self.model.filter_property_list):
                if filter_prop is not 'exclude':
                    if spec[0].has_key(filter_prop):
                        item_string = spec[0][filter_prop]
                    else:
                        item_string = ''
                    t.setItem(j,i,
                              Qt.QTableWidgetItem(Qt.QString(item_string)))
                    
                    t.item(j,i).setFlags(Qt.Qt.ItemIsSelectable|
                                         Qt.Qt.ItemIsEditable|
                                         Qt.Qt.ItemIsDragEnabled|
                                         Qt.Qt.ItemIsEnabled) # Make it editable
                else:
                    t.setItem(j,i,Qt.QTableWidgetItem(Qt.QString()))
                    
                    t.item(j,i).setFlags(Qt.Qt.ItemIsSelectable|
                                         Qt.Qt.ItemIsEditable|
                                         Qt.Qt.ItemIsDragEnabled|
                                         Qt.Qt.ItemIsUserCheckable|
                                         Qt.Qt.ItemIsEnabled) # Make it checkable
                    if spec[1]: # exclusion flag
                        t.item(j,i).setCheckState(Qt.Qt.Checked)
                    else:
                        t.item(j,i).setCheckState(Qt.Qt.Unchecked)
                   
                    
        
        ### Presentation formatting
        t.resizeColumnsToContents()
        for i in range(t.columnCount()):
            if t.columnWidth(i) > self.max_auto_adjust_column_width:
                t.setColumnWidth(i,self.max_auto_adjust_column_width)
        
    
        
    #----------------------------------------------------------------------
    def _initChoiceTable(self):
        """
        Perform initial formating for tableWidget_choice_list
        """
        
        t = self.tableWidget_choice_list # shorthand notation
        
        
        ### Header popluation & properties
        nCols = len(self.model.col_name_list)
        t.setColumnCount(nCols)
        
        '''
        for (i, col_name) in enumerate(self.model.col_name_list):
            # Order the column labels as in the order of the definition
            # of the dictionary for the element property names and the
            # column names
            t.horizontalHeaderItem(i).setText(col_name)
        '''
        # or
        t.setHorizontalHeaderLabels(self.model.col_name_list)
        
        t.horizontalHeader().setMovable(True)
    
    #----------------------------------------------------------------------
    def _initMatchTable(self):
        """
        Perform initial formating for tableWidget_choice_list
        """
        
        t = self.tableWidget_matched # shorthand notation
        
        ### Header population & properties
        nCols = len(self.model.col_name_list)
        t.setColumnCount(nCols)
        
        t.setHorizontalHeaderLabels(self.model.col_name_list)        

        t.horizontalHeader().setMovable(True)
        
        
    #----------------------------------------------------------------------
    def update_tables(self):
        """"""
        
        """###########################
        Update tableWidget_choice_list
        """###########################
        
        t = self.tableWidget_choice_list # shorthand notation
        
        t.clearContents()
        
        ### Item population
        
        nRows = max([len(choice_list) 
                     for choice_list in self.model.choice_dict.values()])
        t.setRowCount(nRows)
        for (i, ch_prop) in enumerate(self.model.ch_property_list):
            choice_list = self.model.choice_dict[ch_prop]
            for (j, value) in enumerate(choice_list):
                t.setItem(j,i,Qt.QTableWidgetItem(value.__str__()))
                t.item(j,i).setFlags(Qt.Qt.ItemIsSelectable|
                                     Qt.Qt.ItemIsDragEnabled|
                                     Qt.Qt.ItemIsEnabled) # Make it non-editable
        
        ### Presentation formatting
        t.resizeColumnsToContents()
        for i in range(t.columnCount()):
            if t.columnWidth(i) > self.max_auto_adjust_column_width:
                t.setColumnWidth(i,self.max_auto_adjust_column_width)
                
        
        
        """####################################
        Populate and format tableWidget_matched
        """####################################
        
        t = self.tableWidget_matched # shorthand notation
        
        t.clearContents()
        
        ### Item population
        
        # Get only matched elements from all the elements
        m = [self.model.allChannels[i] 
             for (i,matched) in enumerate(self.model.combined_matched)
             if matched]
        nRows = len(m)
        t.setRowCount(nRows)
        for (i, ch_prop) in enumerate(self.model.ch_property_list):
            for (j, ch) in enumerate(m):
                value = getattr(ch,ch_prop)
                if callable(value):
                    value = value.__call__()
                t.setItem(j, i, Qt.QTableWidgetItem(value.__str__() ) )
                t.item(j,i).setFlags(Qt.Qt.ItemIsSelectable|
                                     Qt.Qt.ItemIsDragEnabled|
                                     Qt.Qt.ItemIsEnabled) # Make it non-editable        
        
        ### Presentation formatting
        t.resizeColumnsToContents()
        for i in range(t.columnCount()):
            if t.columnWidth(i) > self.max_auto_adjust_column_width:
                t.setColumnWidth(i,self.max_auto_adjust_column_width)
        
        ### Reset selection to all available
        t.selectAll()


    #----------------------------------------------------------------------
    def update_matched_and_selected_numbers(self):
        """"""
        
        nMatched = sum(self.model.combined_matched)
        nSelected = 0
        
        self.label_nMatched_nSelected.setText(
            'Matched Channels (' + str(nMatched) + ' matched, ' 
            + str(nSelected) + ' selected)')
        
    #----------------------------------------------------------------------
    def add_row_to_filter_table(self):
        """"""
        
        # Need to disconnect this signal-slot since each change in each item
        # will cause re-filtering, which const a lot of time. It will be
        # reconnected at the end of this function.
        self.disconnect(self.tableWidget_filter, 
                        Qt.SIGNAL('itemChanged(QTableWidgetItem *)'),
                        self.on_filter_item_change)
        
        t = self.tableWidget_filter # shorthand notation
        
        nRows = t.rowCount()+1
 
        t.setRowCount(nRows) # Add a new row to the table
        
        # Need to initialize the new items in the newly added row
        # with empty filters and the exclulsion flag unchecked
        new_row_index = nRows-1
        for (i, filter_prop) in enumerate(self.model.filter_property_list):
            if filter_prop is not 'exclude':
                t.setItem(new_row_index,i,
                          Qt.QTableWidgetItem(Qt.QString()))
                    
                t.item(new_row_index,i).setFlags(Qt.Qt.ItemIsSelectable|
                                                 Qt.Qt.ItemIsEditable|
                                                 Qt.Qt.ItemIsDragEnabled|
                                                 Qt.Qt.ItemIsEnabled) # Make it editable
            else:
                t.setItem(new_row_index,i,Qt.QTableWidgetItem(Qt.QString()))
                
                t.item(new_row_index,i).setFlags(Qt.Qt.ItemIsSelectable|
                                                 Qt.Qt.ItemIsEditable|
                                                 Qt.Qt.ItemIsDragEnabled|
                                                 Qt.Qt.ItemIsUserCheckable|
                                                 Qt.Qt.ItemIsEnabled) # Make it checkable
                
                t.item(new_row_index,i).setCheckState(Qt.Qt.Unchecked)
                        
        
        # Reconnecting the temporarily disconnected signal-slot
        self.connect(self.tableWidget_filter, 
                     Qt.SIGNAL('itemChanged(QTableWidgetItem *)'),
                     self.on_filter_item_change)
        
        
        self.emit(Qt.SIGNAL("sigFilterRowAdded"),())
    
    #----------------------------------------------------------------------
    def on_case_sensitive_state_change(self, checkBoxState):
        """"""
        
        nRows = self.tableWidget_filter.rowCount()
        
        isCaseSensitive = checkBoxState
        
        # Request re-doing all the filtering with the new case-sensitivity
        # choice.
        self.emit(Qt.SIGNAL("sigReadyForFiltering"), 
                  range(nRows), isCaseSensitive)
    
    #----------------------------------------------------------------------
    def isItemUserCheckable(self, qTableWidgetItem):
        """"""
        
        qtItemFlagsObj = qTableWidgetItem.flags()
        qtItemFlagsInt = int(qtItemFlagsObj)
        
        if qtItemFlagsInt >= Qt.Qt.ItemIsTristate:
            qtItemFlagsInt -= Qt.Qt.ItemIsTristate
            
        if qtItemFlagsInt >= Qt.Qt.ItemIsEnabled:
            qtItemFlagsInt -= Qt.Qt.ItemIsEnabled
            
        if qtItemFlagsInt >= Qt.Qt.ItemIsUserCheckable:
            return True
        else:
            return False
        
        
    
    #----------------------------------------------------------------------
    def on_filter_item_change(self, qTableWidgetItem):
        """
        
        """
        
        if not self.isItemUserCheckable(qTableWidgetItem):
            filter_val = str(
                qTableWidgetItem.data(Qt.Qt.DisplayRole).toString() )
        else:
            filter_val = (qTableWidgetItem.checkState() == Qt.Qt.Checked)
        
        filter_group_index    = qTableWidgetItem.row()
        filter_property_index = qTableWidgetItem.column()
        
        isCaseSensitive = self.checkBox_filter_case_sensitive.isChecked()

        self.emit(Qt.SIGNAL("sigFilterSpecNeedsChange"),
                  filter_property_index, filter_val, 
                  filter_group_index, isCaseSensitive)
        
        
        
    #----------------------------------------------------------------------
    def accept(self):
        """"""
        
        # Update currently selected elements before exiting the dialog
        qModelIndexList = self.tableWidget_matched.selectedIndexes()
        selectedRowIndList = list(set([q.row() for q in qModelIndexList]))
        
        self.emit(Qt.SIGNAL("sigUpdateFinalSelected"),
                  selectedRowIndList)
        
    #----------------------------------------------------------------------
    def _prepareOutput(self):
        """"""
        
        if self.output_type == TYPE_CHANNEL:
            self.model.output = self.model.selectedChannels
        elif self.output_type == TYPE_NAME:
            self.model.output = [c.name for c in self.model.selectedChannels]
        
        super(ChannelSelectorView, self).accept() # will hide the dialog
        
        
    #----------------------------------------------------------------------
    def reject(self):
        """"""
        
        self.model.output = []
        
        super(ChannelSelectorView, self).reject() # will hide the dialog
    

########################################################################
class ChannelSelectorApp(Qt.QObject):
    """"""

    #----------------------------------------------------------------------
    def __init__(self, modal = True, parentWindow = None, 
                 filter_spec = [ [{},False] ], output_type = TYPE_CHANNEL):
        """Constructor"""
        
        Qt.QObject.__init__(self)
        
        self.modal = modal
        self.parentWindow = parentWindow
        
        self._initModel(filter_spec)
        self._initView(output_type)
        
        # When a filter item is changed, signal the data to modify
        # filter_spec, and then signal "ready for filtering" to the data.
        self.connect(self.view.tableWidget_filter, 
                     Qt.SIGNAL('itemChanged(QTableWidgetItem *)'),
                     self.view.on_filter_item_change)
        self.connect(self.view, Qt.SIGNAL("sigFilterSpecNeedsChange"),
                     self.model.modify_filter_spec)
        
        # When the checkbox for "case-sensitive" is toggled, the view
        # does pre-processing, and signals "ready for filtering" to the data.
        self.connect(self.view.checkBox_filter_case_sensitive, 
                     Qt.SIGNAL("toggled(bool)"),
                     self.view.on_case_sensitive_state_change)
        
        # Once the pre-processing of the filter specification is done,
        # tell the data to perform the filtering based on the modified
        # filter specification.
        self.connect(self.view, Qt.SIGNAL("sigReadyForFiltering"),
                     self.model.filterData)
        self.connect(self.model, Qt.SIGNAL("sigReadyForFiltering"),
                     self.model.filterData)

        # After new filtering is performed, update the view based on
        # the new filtered data.
        self.connect(self.model, Qt.SIGNAL("sigDataFiltered"),
                     self.view.update_tables)
        self.connect(self.model, Qt.SIGNAL("sigDataFiltered"),
                     self.view.update_matched_and_selected_numbers)
        
        
        self.connect(self.view.pushButton_add_row, Qt.SIGNAL("clicked()"),
                     self.view.add_row_to_filter_table)
        self.connect(self.view, Qt.SIGNAL("sigFilterRowAdded"),
                     self.model.add_row_to_filter_spec)
        
        
        self.connect(self.view, Qt.SIGNAL("sigUpdateFinalSelected"),
                     self.model.update_selected_channels)
        self.connect(self.model, Qt.SIGNAL("sigReadyForClosing"),
                     self.view._prepareOutput)
        
    #----------------------------------------------------------------------
    def _initModel(self, filter_spec):
        """"""
        
        self.model = ChannelSelectorModel(filter_spec)
        
    #----------------------------------------------------------------------
    def _initView(self, out_type = TYPE_CHANNEL):
        """"""
        
        self.view = ChannelSelectorView(self.model, self.modal, out_type,
                                        parentWindow = self.parentWindow)


#----------------------------------------------------------------------
def make(**kwargs):
    """"""
    
    modal = kwargs.get('modal', True)
    parentWindow = kwargs.get('parentWindow', None)
    filter_spec = kwargs.get('filter_spec', [ [{},False] ])
    output_type = kwargs.get('output_type', TYPE_CHANNEL)
    
    app = ChannelSelectorApp(modal, parentWindow, filter_spec, output_type)
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
    "user_timer" to be True. However, if you use "use_timer", it will
    Segmentation Fault at the end of running the main function.
    '''
    #qtapp = cothread.iqt(use_timer = True)
    qtapp = cothread.iqt()
    #qtapp = Qt.QApplication(sys.argv) # use this if you are not using "cothread" module at all in your application


    result = make(output_type = TYPE_NAME)
    
    print result
    print 'Length = ', len(result)
    
        
    

#----------------------------------------------------------------------    
if __name__ == "__main__" :
    main(sys.argv)
    
