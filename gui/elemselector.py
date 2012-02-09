#! /usr/bin/env python

"""

GUI application for selecting HLA element(s) interactively

:author: Yoshiteru Hidaka
:license:

This GUI application is a dialog that allows users to see all the available
elements, narrow them down by search filtering, and finally select the elements
of interest and return the selected elements as an input to another function
or GUI application.

"""

import config # gives access to qtapp variable that holds a Qt.QApplication instance

import sys
import fnmatch
from operator import and_, not_

import cothread

# If Qt is to be used (for any GUI) then the cothread library needs to be informed,
# before any work is done with Qt. Without this line below, the GUI window will not
# show up and freeze the program.
# Note that for a dialog box to be modal, i.e., blocking the application
# execution until user input is given, you need to set the input
# argument "user_timer" to be True.
if not config.qtapp:
    config.qtapp.append( cothread.iqt(use_timer = True) )
    # config.qtapp.append( Qt.QApplication(sys.argv) ) # use this if you are not using "cothread" module at all in your application

import PyQt4.Qt as Qt

import aphlas
from Qt4Designer_files.ui_element_selector import Ui_Dialog

if not aphlas.machines._lat :
    aphlas.initNSLS2VSR()

# Output Type Enums
TYPE_ELEMENT = 1
TYPE_NAME    = 2

# TODO:
# 1) Create a tab for each selection, and allow OR operation
# to different tabs.

########################################################################
class ElementSelectorData(Qt.QObject):
    """ """

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
        
        
        # key   = property name of Element object
        # value = displayed column name for tables showing choices and matches
        self.elem_property_vs_col_name = \
            {'name':'Name', 'devname':'Dev. Name', 'cell':'Cell', 
             'family':'Family', 'girder':'Girder', 'group':'Group', 
             'index':'Lat. Index', 'length':'Eff.Len', 'phylen':'Phys. Len.',
             'pv':'PV', 'sb':'sb', 'se':'se', 'symmetry':'Symmetry',
             'virtual':'Virtual', 'sequence':'Sequence'}
        
        # key   = property name of Element object & exclusion flag
        # value = displayed column name for table showing filters
        self.filter_property_vs_col_name = \
            self.elem_property_vs_col_name.copy()
        self.filter_property_vs_col_name.update({'exclude':'Excl.'}) # adding extra column
        
        # Specify the default column order you want for tables showing
        # choices and matches.
        self.elem_property_list = ['family', 'name', 'devname', 'cell',
                                   'girder', 'symmetry', 'group', 'virtual',
                                   'sb', 'se', 'pv', 'length', 'phylen',
                                   'index', 'sequence']
        self.col_name_list = [self.elem_property_vs_col_name[prop]
                         for prop in self.elem_property_list]
        self.choice_dict = dict.fromkeys(self.elem_property_list)
        
        # Specify the default column order you want for table showing
        # filters.
        self.filter_property_list = self.elem_property_list[:]
        self.filter_property_list.insert(0, 'exclude')
        self.filter_col_name_list = [self.filter_property_vs_col_name[prop]
                         for prop in self.filter_property_list]
        self.filter_dict = dict.fromkeys(self.filter_property_list)
        
        self.numeric_filter_list = ['index', 'phylen', 'length', 'sb', 'se']
        self.not_implemented_filter_list = ['sequence']
        
        self.filter_spec = filter_spec
        
        self.allElements = hla.getElements('*')
        
        # Initialization of matching data information
        self.matched = [ [True]*len(self.allElements) ]
        self.combine_matched_list()
        self.update_choice_dict()
        
        # Apply initial filters provided by a user, if any.
        if self.filter_spec:
            isCaseSensitive = False
            self.filterData(range(len(self.filter_spec)), isCaseSensitive)
        
        self.selectedElements = []
    
    #----------------------------------------------------------------------
    def combine_matched_list(self):
        """ """
        
        nFilterGroups = len(self.filter_spec)
        
        if not self.filter_spec:
            self.combined_matched = [True]*len(self.allElements)
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
        self.matched[index] = [True]*len(self.allElements)
            
        for (prop, val) in pattern_filter_dict.iteritems():
            if prop in self.not_implemented_filter_list:
                pass
            elif prop in self.numeric_filter_list: # numerical filter
                pass
            else: # string filter
                    
                matchedItemsZipped = [ 
                    (j,elem) for (j,elem) in enumerate(self.allElements)
                    if self.matched[index][j] ]
                    
                if matchedItemsZipped: # When there are some matched elements
                    matchedItemsUnzipped = zip(*matchedItemsZipped)
                    matchedInd   = list(matchedItemsUnzipped[0])
                    matchedElems = list(matchedItemsUnzipped[1])
                else: # When there is no matched element, no need for futher filtering
                    self.matched[index] = [False]*len(self.allElements)
                    return
                    
                '''
                The reason why __str__() is being used here to retrieve
                strings is that this method can handle None values as
                well.
                '''
                if not isCaseSensitive: # case-insensitive search
                    filter_str = val.upper()
                    matchedElemStrings = [ 
                        getattr(getattr(e,prop),'__str__')().upper()
                        for e in matchedElems]
                else: # case-sensitive search
                    filter_str = val
                    matchedElemStrings = [
                        getattr(getattr(e,prop),'__str__')()
                        for e in matchedElems]
                
                reducedNewMatchedInd = [ 
                    j for (j,s) in enumerate(matchedElemStrings)
                    if fnmatch.fnmatchcase(s,filter_str)]
                    
                newMatchedInd = [matchedInd[j] 
                                 for j in reducedNewMatchedInd]
                    
                self.matched[index] = [ 
                    (j in newMatchedInd) 
                    for j in range(len(self.allElements))]
                    
                    
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
        """ """
        
        self.filter_spec.append( [{},False] )
        
        self.matched.append( [True]*len(self.allElements) )
        
        # self.combined_matched stays the same
        
    #----------------------------------------------------------------------
    def modify_filter_spec(self, filter_property_index, filter_val,
                           filter_group_index, isCaseSensitive):
        """ """

        filter_property = self.filter_property_list[filter_property_index]
        
        if filter_property is not 'exclude':
            self.filter_spec[filter_group_index][0][filter_property] = \
                filter_val
        else:
            self.filter_spec[filter_group_index][1] = filter_val
        
        # Request re-doing all the filtering with the modified filter spec.
        self.emit(Qt.SIGNAL("sigReadyForFiltering"), 
                  [filter_group_index], isCaseSensitive)
    
    #----------------------------------------------------------------------
    def update_choice_dict(self):
        """ """
        
        # Get only matched elements from all the elements
        matchedElements = [self.allElements[i] 
                           for (i,matched) in enumerate(self.combined_matched)
                           if matched]
        
        # If there is no match
        if not matchedElements:
            for prop in self.elem_property_list:
                self.choice_dict[prop] = []
            return
        
        # If there is some matched element(s)
        for prop in self.elem_property_list:
            if callable(getattr(matchedElements[0],prop)): # if property is a function
                prop_val_list = [getattr(e,prop)() for e in matchedElements]
            else: # if property is a value
                prop_val_list = [getattr(e,prop)   for e in matchedElements]
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
    def update_selected_elements(self, selectedRowIndList):
        """ """
        
        # Update currently selected elements before exiting the dialog
        matchedElemList = [
            self.allElements[i] 
            for (i,matched) in enumerate(self.combined_matched)
            if matched] 
        self.selectedElements = [matchedElemList[i] 
                                 for i in selectedRowIndList]
        
        self.emit(Qt.SIGNAL("sigReadyForClosing"),())

                
        

########################################################################
class ElementSelectorView(Qt.QDialog, Ui_Dialog):
    """ """
    
    #----------------------------------------------------------------------
    def __init__(self, data, modal, parentWindow = None):
        """Constructor"""
        
        Qt.QDialog.__init__(self, parent = parentWindow)
        
        self.setWindowFlags(Qt.Qt.Window) # To add Maximize & Minimize buttons
        
        self.data = data
        
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
        t.setHorizontalHeaderLabels(self.data.filter_col_name_list)
        t.horizontalHeader().setMovable(True)
        
        ### Item population
        nRows = len(self.data.filter_spec)
        t.setRowCount(nRows)
        for (j, spec) in enumerate(self.data.filter_spec):
            for (i, filter_prop) in enumerate(self.data.filter_property_list):
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
        '''
        for (i, col_name) in enumerate(self.data.col_name_list):
            # Order the column labels as in the order of the definition
            # of the dictionary for the element property names and the
            # column names
            t.horizontalHeaderItem(i).setText(col_name)
        '''
        # or
        t.setHorizontalHeaderLabels(self.data.col_name_list)
        
        t.horizontalHeader().setMovable(True)
    
    #----------------------------------------------------------------------
    def _initMatchTable(self):
        """
        Perform initial formating for tableWidget_choice_list
        """
        
        t = self.tableWidget_matched # shorthand notation
        
        ### Header population & properties
        
        t.setHorizontalHeaderLabels(self.data.col_name_list)
        
        t.horizontalHeader().setMovable(True)
        
        
    #----------------------------------------------------------------------
    def update_tables(self):
        """ """
        
        """###########################
        Update tableWidget_choice_list
        """###########################
        
        t = self.tableWidget_choice_list # shorthand notation
        
        t.clearContents()
        
        ### Item population
        
        nRows = max([len(choice_list) 
                     for choice_list in self.data.choice_dict.values()])
        t.setRowCount(nRows)
        for (i, elem_prop) in enumerate(self.data.elem_property_list):
            choice_list = self.data.choice_dict[elem_prop]
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
        m = [self.data.allElements[i] 
             for (i,matched) in enumerate(self.data.combined_matched)
             if matched]
        nRows = len(m)
        t.setRowCount(nRows)
        for (i, elem_prop) in enumerate(self.data.elem_property_list):
            for (j, elem) in enumerate(m):
                value = getattr(elem,elem_prop)
                if callable(value):
                    value = value.__call__()
                t.setItem( j, i, Qt.QTableWidgetItem(value.__str__() ) )
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
        """ """
        
        nMatched = sum(self.data.combined_matched)
        nSelected = 0
        
        self.label_nMatched_nSelected.setText(
            'Matched Elements (' + str(nMatched) + ' matched, ' 
            + str(nSelected) + ' selected)')
        
    #----------------------------------------------------------------------
    def add_row_to_filter_table(self):
        """ """
        
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
        for (i, filter_prop) in enumerate(self.data.filter_property_list):
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
        """ """
        
        nRows = self.tableWidget_filter.rowCount()
        
        isCaseSensitive = checkBoxState
        
        # Request re-doing all the filtering with the new case-sensitivity
        # choice.
        self.emit(Qt.SIGNAL("sigReadyForFiltering"), 
                  range(nRows), isCaseSensitive)
    
    #----------------------------------------------------------------------
    def isItemUserCheckable(self, qTableWidgetItem):
        """ """
        
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
        """ """
        
        # Update currently selected elements before exiting the dialog
        qModelIndexList = self.tableWidget_matched.selectedIndexes()
        selectedRowIndList = list(set([q.row() for q in qModelIndexList]))
        
        self.emit(Qt.SIGNAL("sigUpdateFinalSelected"),
                  selectedRowIndList)
        
    #----------------------------------------------------------------------
    def accept_and_close(self):
        """ """
        
        super(ElementSelectorView, self).accept() # will close the dialog
        
        
    #----------------------------------------------------------------------
    def reject(self):
        """ """
        
        super(ElementSelectorView, self).reject() # will close the dialog
    

########################################################################
class ElementSelectorApp(Qt.QObject):
    """ """

    #----------------------------------------------------------------------
    def __init__(self, modal = True, parentWindow = None, 
                 filter_spec = [ [{},False] ]):
        """Constructor"""
        
        Qt.QObject.__init__(self)
        
        self.modal = modal
        self.parentWindow = parentWindow
        
        self._initData(filter_spec)
        self._initView()
        
        # When a filter item is changed, signal the data to modify
        # filter_spec, and then signal "ready for filtering" to the data.
        self.connect(self.view.tableWidget_filter, 
                     Qt.SIGNAL('itemChanged(QTableWidgetItem *)'),
                     self.view.on_filter_item_change)
        self.connect(self.view, Qt.SIGNAL("sigFilterSpecNeedsChange"),
                     self.data.modify_filter_spec)
        
        # When the checkbox for "case-sensitive" is toggled, the view
        # does pre-processing, and signals "ready for filtering" to the data.
        self.connect(self.view.checkBox_filter_case_sensitive, 
                     Qt.SIGNAL("toggled(bool)"),
                     self.view.on_case_sensitive_state_change)
        
        # Once the pre-processing of the filter specification is done,
        # tell the data to perform the filtering based on the modified
        # filter specification.
        self.connect(self.view, Qt.SIGNAL("sigReadyForFiltering"),
                     self.data.filterData)
        self.connect(self.data, Qt.SIGNAL("sigReadyForFiltering"),
                     self.data.filterData)

        # After new filtering is performed, update the view based on
        # the new filtered data.
        self.connect(self.data, Qt.SIGNAL("sigDataFiltered"),
                     self.view.update_tables)
        self.connect(self.data, Qt.SIGNAL("sigDataFiltered"),
                     self.view.update_matched_and_selected_numbers)
        
        
        self.connect(self.view.pushButton_add_row, Qt.SIGNAL("clicked()"),
                     self.view.add_row_to_filter_table)
        self.connect(self.view, Qt.SIGNAL("sigFilterRowAdded"),
                     self.data.add_row_to_filter_spec)
        
        
        self.connect(self.view, Qt.SIGNAL("sigUpdateFinalSelected"),
                     self.data.update_selected_elements)
        self.connect(self.data, Qt.SIGNAL("sigReadyForClosing"),
                     self.view.accept_and_close)
        
    #----------------------------------------------------------------------
    def _initData(self, filter_spec):
        """ """
        
        self.data = ElementSelectorData(filter_spec)
        
    #----------------------------------------------------------------------
    def _initView(self, out_type = TYPE_ELEMENT):
        """ """
        
        self.view = ElementSelectorView(self.data, self.modal,
                                        parentWindow = self.parentWindow)


#----------------------------------------------------------------------
def make(modal = True, parentWindow = None, filter_spec = [ [{},False] ],
         output_type = TYPE_ELEMENT):
    """ """
    
    app = ElementSelectorApp(modal, parentWindow, filter_spec)
    view = app.view
        
    if app.modal :
        view.exec_()
        
        if view.result() == Qt.QDialog.Accepted:
            if output_type == TYPE_ELEMENT:
                output = app.data.selectedElements
            elif output_type == TYPE_NAME:
                output = [e.name for e in app.data.selectedElements]
            else:
                output = []
        else:
            output = []
        
        result = {'app': app,  
                  'dialog_result': output}
    else : # non-modal
        view.show()
        result = {'app': app}
    
    return result

    
#----------------------------------------------------------------------
def main(args):
    """ """
    
    qapp = Qt.QApplication(args) # Necessary whether modal or non-modal
    
    result = make(modal = True, output_type = TYPE_ELEMENT)
    
    if result.has_key('dialog_result'): # When modal
        app           = result['app']
        dialog_result = result['dialog_result']
        
        print dialog_result
        print 'Length = ', len(dialog_result)
        
        
    else: # When non-modal
        app = result['app']
        exit_status = qapp.exec_()
        sys.exit(exit_status)
        
    

#----------------------------------------------------------------------    
if __name__ == "__main__" :
    main(sys.argv)
    
