#! /usr/bin/env python

import time

#----------------------------------------------------------------------
def tic():
    """"""
    
    return time.time()
    
#----------------------------------------------------------------------
def toc(tStart):
    """"""
    
    tEnd = time.time()
    
    elapsed_time = tEnd - tStart
    
    return elapsed_time

''' TODO
*) Add QSettings for window size, etc. (add "caller" so that depending on which
application calls this GUI, this GUI will know which preferences to load)
   - default visible columns & their order (Column View)
   - OOO column sorting init state (General)
   - OOO case-sensitive (General)
   - OOO simple or advanced (General)
   - XXXX elements or channels (General)
   - OOO lattice initialization func name (General)
   - OOO default lattice name (General)
Use VisibleOrderPreferencesDialog class
   
*) Implement advanced filters
*) Allow filtering from choice_list selection w/ right click (like multiple cell selections)
context menu for "simple":
Apply this filter
context menu for "advanced"
Apply this filter -> list of existing filter set(s)
'''

"""

GUI application for selecting HLA element(s) interactively

:author: Yoshiteru Hidaka
:license:

This GUI application is a dialog that allows users to see all the available
elements, narrow them down by search filtering, and finally select the elements
of interest and return the selected elements as an input to another function
or GUI application.

"""

import sip
sip.setapi('QString', 2)
sip.setapi('QVariant', 2)

import sys
from fnmatch import fnmatchcase
from operator import and_, not_, add
import numpy as np

import cothread

from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import (SIGNAL, QObject, QSize, QSettings, QRect)
from PyQt4.QtGui import (qApp, QDialog, QStandardItemModel, QStandardItem,
                         QComboBox, QTableView, QSortFilterProxyModel,
                         QAbstractItemView, QMenu, QAction, QIcon,
                         QCursor, QItemSelection, QItemSelectionModel,
                         QRadioButton, QCheckBox, QSizePolicy,
                         QKeySequence)

from Qt4Designer_files.ui_channel_explorer import Ui_Dialog
from Qt4Designer_files.ui_channel_explorer_pref_dialog import Ui_Dialog as Ui_Dialog_preferences
from orderprefdlg import OrderSelector

import aphla as ap


# Output Type Enums
TYPE_OBJECT = 1
TYPE_NAME   = 2

MACHINE_DICT = { # (Machine Display Name): (Initialization Function Name)
    'NSLS2': 'initNSLS2',
    'NSLS2V2': 'initNSLS2V2',
    }

ENUM_ELEM_FULL_DESCRIP_NAME = 0
ENUM_ELEM_SHORT_DESCRIP_NAME = 1
ENUM_ELEM_DATA_TYPE = 2
ELEM_PROPERTIES ={
    'name': ['Name','Name','string'],
    'devname': ['Device Name','Dev.Name','string'],
    'cell': ['Cell','Cell','string'],
    'family': ['Family','Family','string'],
    'girder': ['Girder','Girder','string'],
    'group': ['Group','Group','string_list'],
    'index': ['Lattice Index','Lat.Ind.','int'],
    'length': ['Effective Length','Eff.Len.','float'],
    'phylen': ['Physical Length','Phys.Len.','float'],
    'pv': ['PV(s)','PV(s)','string_list'], # callable
    'sb': ['s(beginning)','sb','float'],
    'se': ['s(end)','se','float'],
    'symmetry': ['Symmetry','Symmetry','string'],
    'virtual': ['Virtual','Virtual','bool'],
    'sequence': ['Sequence','Sequence','int_list'],
    'fields':['Fields','Fields','string_list'], # callable
    }
PROP_NAME_LIST = sorted(ELEM_PROPERTIES.keys(),key=str.lower)

FILTER_OPERATOR_DICT = {'int': ['==(num)','<=','>='],
                        'bool': ['==(num)'],
                        'float': ['<=','>='],
                        'string': ['==(char)','IN'],
                        'string_list': ['==(char)','IN'],
                        'int_list': ['==(num)','<=','>='],
                        }
ALL_FILTER_OPERATORS = FILTER_OPERATOR_DICT.values()
ALL_FILTER_OPERATORS = reduce(add, ALL_FILTER_OPERATORS) # flattening list of lists
ALL_FILTER_OPERATORS = list(set(ALL_FILTER_OPERATORS))

########################################################################
class Filter():
    """"""

    #----------------------------------------------------------------------
    def __init__(self, name, model):
        """Constructor"""
        
        self.name = name
        self.name_displayed = self.name
        
        self.model = model

        self.object_type = self.model.object_type

        if self.object_type == 'element':
            self.allObjects = self.model.allElements
        elif self.object_type == 'channel':
            self.allObjects = self.model.allChannels
        
        self.set1_name = 'ALL'
        self.set1_name_displayed = self.set1_name
        self.set1 = self.allObjects
            
        self.set_operator = 'AND' # 'AND' or 'OR'
        self.set_operator_displayed = self.set_operator
        self.updateParentSet()
        
        self.set2_name = 'NEW'
        self.set2_name_displayed = self.set2_name
        self.set2 = []
        
        self.NOT = False
        self.NOT_displayed = self.NOT
        
        self.property_name = 'family'
        self.property_name_displayed = self.property_name

        self.filter_operator = '==(char)'
        self.filter_operator_displayed = self.filter_operator

        self.index = ''
        self.index_displayed = self.index

        self.filter_value = '*'
        self.filter_value_displayed = self.filter_value
        
        self.matched_index_list = []
        
    #----------------------------------------------------------------------
    def commit_displayed_properties(self):
        """"""
        
        prop_names = ['name', 'set1_name','set_operator','set2_name',
                      'NOT','property_name','filter_operator',
                      'index','filter_value']
        
        for name in prop_names:
            setattr(self, name, getattr(self, name+'_displayed'))
        
        
    #----------------------------------------------------------------------
    def updateParentSet(self):
        """"""
        
        if self.set_operator == 'AND':
            self.parentSet = self.set1
        elif self.set_operator == 'OR':
            self.parentSet = self.allObjects
        else:
            raise ValueError('set_operator must be AND or OR')
        
########################################################################
class NumericallySortableItemModel(QStandardItemModel):
    """"""

    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        
        QStandardItemModel.__init__(self)
        
        self.SortRole = QtCore.Qt.UserRole
        
        self.underlying2DTable = np.array([])
        
    #----------------------------------------------------------------------
    def data(self, modelIndex, role):
        """
        Reimplementation of QStandardItemModel's data()
        The purpose is to allow sorting by numbers, not just by
        default string sorting.
        """
        
        if role == self.SortRole:
            value = self.underlying2DTable[modelIndex.row(), modelIndex.column()]
        else:
            value = QStandardItemModel.data(self, modelIndex, role)

        return value

########################################################################
class ChannelExplorerModel(QObject):
    """ """

    #----------------------------------------------------------------------
    def __init__(self, machine_name, object_type='element', settings=None):
        """
        The optional input argument "filter_spec" must be either an empty
        list, or a list of lists, each of which contains a dictionary and a bool. 
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
        
        QObject.__init__(self)
        
        self.settings = settings # QSettings object
        
        self.machine_name = machine_name
        
        self.object_type = object_type
        
        self.settings.beginGroup('General')
        self.is_case_sensitive = self.settings.value('is_case_sensitive')
        if self.is_case_sensitive is None:
            self.is_case_sensitive = False
        self.is_column_sorting = self.settings.value('is_column_sorting')
        if self.is_column_sorting is None:
            self.is_column_sorting = False
        self.settings.endGroup()
        
        self.col_name_list = [ELEM_PROPERTIES[name][ENUM_ELEM_SHORT_DESCRIP_NAME]
                              for name in PROP_NAME_LIST]
        
        self.reconstructModel(object_type)
        
        self.table_model_matched = NumericallySortableItemModel()
        self.table_model_matched.setColumnCount(len(self.col_name_list))
        self.table_model_matched.setHorizontalHeaderLabels(self.col_name_list)
        
        self.table_model_filter = NumericallySortableItemModel()
        
        
    #----------------------------------------------------------------------
    def reconstructModel(self, object_type):
        """"""
        
        self.allElements = ap.getElements('*')
        self.allFields = []
        for e in self.allElements:
            fields = e.fields()
            self.allFields.extend(fields)
        self.allFields = sorted(list(set(self.allFields)),key=lower)
        self.allChannels = self.convertElemListToChannelList(self.allElements)
        
        if object_type == 'element':
            self.currentParentSet = self.allElements[:]
            
        elif object_type == 'channel':
            self.currentParentSet = self.allChannels[:]
        else:
            raise ValueError('Unexpected object_type: '+object_type)

        
        self.selectedObjects = []
        
        # For "simple" mode
        filter_name = 'simple_filter'
        self.filters = [Filter(filter_name,self)]
        
        # For "advanced" mode
        #filter_name = 'filter1'
        self.hidden_filters = []
        
        self.selected_filter_index = 0
        
        
    #----------------------------------------------------------------------
    def on_machine_change(self, machine_name):
        """"""
        
        initMachine(machine_name)
        
        self.emit(SIGNAL('machineChanged'))
        
        
    #----------------------------------------------------------------------
    def on_lattice_change(self, lattice_name):
        """"""
        
        print 'Using Lattice:', lattice_name
        ap.machines.use(lattice_name)
                
        self.reconstructModel(self.object_type)
        
        self.emit(SIGNAL('modelReconstructedOnLatticeChange'))
        
        
    #----------------------------------------------------------------------
    def _changeObjectType(self, object_type):
        """"""
        
        self.object_type = object_type
        
        for f in self.filters:
            f.object_type = self.object_type
            if f.object_type == 'element':
                f.allObjects = self.allElements
                f.set1 = self.convertChannelListToElemList(f.set1)
                f.set2 = self.convertChannelListToElemList(f.set2)
            elif f.object_type == 'channel':
                f.allObjects = self.allChannels
                f.set1 = self.convertElemListToChannelList(f.set1)
                f.set2 = self.convertElemListToChannelList(f.set2)
        
        f.updateParentSet()
        
    #----------------------------------------------------------------------
    def convertElemListToChannelList(self, elemList):
        """"""
        
        channelList = []
        
        for e in elemList:
            fields = e.fields()
            if fields == []:
                channelList.append((e,''))
            else:
                for f in fields:
                    channelList.append((e,f))
        
        return channelList
        
    #----------------------------------------------------------------------
    def convertChannelListToElemList(self, channelList):
        """"""
        
        elemList = list(set([c[0] for c in channelList]))
        
        return elemList
        
        
    #----------------------------------------------------------------------
    def get(self, obj, propertyName):
        """
        propertyName can be a property of element or a function of element
        """
        
        if not isinstance(obj,tuple): # for 'element' object
            
            element = obj
            
            x = getattr(element,propertyName)

            if callable(x):
                x = x()

        else: # for 'channel' object (= tuple of 'element' object & field name)
            
            element = obj[0]
            field = obj[1]
            
            x = getattr(element,propertyName)
            
            if propertyName == 'fields':
                x = [field]
            elif propertyName == 'pv':
                try:
                    x = element.pv(field=field,handle='readback')[:]
                    x.extend(element.pv(field=field,handle='setpoint')[:])
                    #x = element._field[field].pvrb
                    #x.extend(element._field[field].pvsp)
                except: # For DIPOLE, there is no field specified
                    x = element.pv()[:]
        
        return x
    
        
    #----------------------------------------------------------------------
    def search(self):
        """"""
        
        current_filter = self.filters[self.selected_filter_index]
        
        current_filter.commit_displayed_properties()
        
        tStart = tic()
        self.emit(SIGNAL('filtersChanged'), current_filter.name)
        print 'Search update took', toc(tStart), ' seconds'
        
    #----------------------------------------------------------------------
    def updateFilters(self, modified_filter_name):
        """
        Assuming that filter sets available to a filter are only
        those filters defined above the filter of interest.
        """
        
        if modified_filter_name is None:
            for f in self.filters:
                f.matched_index_list = []
                #self._updateFilter(f)
        else:
        
            # First change the modified filter itself
            modified_filter_tuple = [(i,f) for (i,f) in enumerate(self.filters)
                                     if f.name == modified_filter_name]
            if len(modified_filter_tuple) == 1:
                modified_filter_index = modified_filter_tuple[0][0]
                modified_filter = modified_filter_tuple[0][1]
            else:
                raise ValueError('There is no matched filter name or more than one match found.')
            self._updateFilter(modified_filter)
        
            # Then, change all the other filters that are
            # affected by the filter change above
            for f in self.filters[modified_filter_index+1:]:
                if modified_filter_name in (f.set1_name,f.set2_name):
                    self._updateFilter(f)
                
        self.emit(SIGNAL('filtersUpdated'))
           
    #----------------------------------------------------------------------
    def update_table_models(self):
        """"""
        
        f = self.filters[self.selected_filter_index]
        isinstance(f,Filter) # WingHelper TODELETE
        
        model_m = self.table_model_matched
        
        model_m.blockSignals(True)
        
        model_m.removeRows(0,model_m.rowCount()) # clear contents
        
        # Get only matched objects from all the objects
        matched_obj_list = [f.parentSet[i] for i in f.matched_index_list]
        nRows = len(matched_obj_list)
        model_m.setRowCount(nRows)
        nCols = len(PROP_NAME_LIST)
        model_m.setColumnCount(nCols)
        model_m.underlying2DTable = np.empty((nRows,nCols),dtype=np.object)
        template_item = QStandardItem()
        template_item.setFlags((QtCore.Qt.ItemIsSelectable |
                                QtCore.Qt.ItemIsDragEnabled |
                                QtCore.Qt.ItemIsEnabled)
                               & (~QtCore.Qt.ItemIsEditable) ) # Make it non-editable
        for (j,prop_name) in enumerate(PROP_NAME_LIST):
            
            item_list = [template_item.clone() for i in range(nRows)]
            if not( (prop_name == 'fields') and (self.object_type == 'channel') ):
                value_list = [self.get(obj,prop_name) for obj in matched_obj_list]
            else:
                '''
                For 'fields' with 'channel' object type selected, value will be 
                a single-element list. So, pull out the element out of the list.
                '''
                value_list = [self.get(obj,prop_name)[0] for obj in matched_obj_list]
            model_m.underlying2DTable[:,j] = value_list
            item_value_list = zip(item_list, value_list)
            for (i,(item,value)) in enumerate(item_value_list):
                item.setText(value.__str__())
                model_m.setItem(i, j, item)

        model_m.blockSignals(False)
        
        model_m.emit(SIGNAL('modelReset()'))
        
        model_f = self.table_model_filter
        
                
    #----------------------------------------------------------------------
    def any_fnmatchcase_for_pattern_str_list(self, string, pattern_str_list):
        """"""
        
        at_least_one_pattern_str_matched = False
        for pattern_str in pattern_str_list:
            if fnmatchcase(string, pattern_str):
                at_least_one_pattern_str_matched = True
                break
            
        return at_least_one_pattern_str_matched
        
    #----------------------------------------------------------------------
    def get_filter_str_list(self, is_case_sensitive, filter_operator, filter_value):
        """"""
        
        if filter_operator == '==(char)':
            if not is_case_sensitive: # case-insensitive search
                filter_str = filter_value.upper()
            else: # case-sensitive search
                filter_str = filter_value
            
            filter_str_list = [filter_str]
            
        elif filter_operator == 'IN':
            if not is_case_sensitive: # case-insensitive search
                filter_str_list = [v.strip().upper() for v in filter_value.split(',')]
            else: # case-sensitive search
                filter_str_list = [v.strip()         for v in filter_value.split(',')]
        
        else:
            raise ValueError('Unexpected filter_operator: '+filter_operator)
        
        return filter_str_list

        
    #----------------------------------------------------------------------
    def _updateFilter(self, modified_filter):
        """"""
        
        if not isinstance(modified_filter,Filter):
            raise ValueError('Input argument must be of class Filter.')
        
        f = modified_filter # for shorthand
        
        if f.set_operator == 'AND':
            f.parentSet = f.set1
        elif f.set_operator == 'OR':
            f.parentSet = f.allObjects
        else:
            raise ValueError('set_operator must be AND or OR')
        
        data_type = ELEM_PROPERTIES[f.property_name][ENUM_ELEM_DATA_TYPE]
        
        if data_type == 'string':
            '''
            The reason why __str__() is being used here to retrieve
            strings is that this method can handle None values as
            well.
            '''

            filter_str_list = self.get_filter_str_list(self.is_case_sensitive, f.filter_operator, f.filter_value)

            if not self.is_case_sensitive: # case-insensitive search
                parent_set_str_list = [ 
                    getattr(self.get(obj,f.property_name),'__str__')().upper()
                    for obj in f.parentSet]
            else: # case-sensitive search
                parent_set_str_list = [
                    getattr(self.get(obj,f.property_name),'__str__')()
                    for obj in f.parentSet]

            if f.NOT:
                f.matched_index_list = [i for (i,s) in enumerate(parent_set_str_list)
                                        if not self.any_fnmatchcase_for_pattern_str_list(s,filter_str_list)]                
            else:
                f.matched_index_list = [i for (i,s) in enumerate(parent_set_str_list)
                                        if self.any_fnmatchcase_for_pattern_str_list(s,filter_str_list)]
            
        elif data_type == 'string_list':

            filter_str_list = self.get_filter_str_list(self.is_case_sensitive, f.filter_operator, f.filter_value)
            
            try:
                index = int(f.index)
            except:
                index = None
            
            list_of_str_list = [self.get(obj,f.property_name) 
                                for obj in f.parentSet]
            
            if index is not None:
                
                if not self.is_case_sensitive: # case-insensitive search
                    parent_set_str_list = [getattr(L[index],'__str__')().upper()
                                           for L in list_of_str_list]
                else: # case-sensitive search
                    parent_set_str_list = [getattr(L[index],'__str__')()
                                           for L in list_of_str_list]
                
                if f.NOT:
                    f.matched_index_list = [i for (i,s) in enumerate(parent_set_str_list)
                                            if not self.any_fnmatchcase_for_pattern_str_list(s,filter_str_list)]                
                else:
                    f.matched_index_list = [i for (i,s) in enumerate(parent_set_str_list)
                                            if self.any_fnmatchcase_for_pattern_str_list(s,filter_str_list)]
                    
            
            else:
                
                matched_index_list = []

                if not self.is_case_sensitive: # case-insensitive search

                    for (i,L) in enumerate(list_of_str_list):
                        matched_list = [getattr(n,'__str__')().upper() for n in L
                                        if self.any_fnmatchcase_for_pattern_str_list(getattr(n,'__str__')().upper(),
                                                                                     filter_str_list)]
                        if len(matched_list) >= 1:
                            matched_index_list.append(i)

                else: # case-sensitive search
                
                    for (i,L) in enumerate(list_of_str_list):
                        matched_list = [getattr(n,'__str__')() for n in L
                                        if self.any_fnmatchcase_for_pattern_str_list(getattr(n,'__str__')(),
                                                                                     filter_str_list)]                        
                        if len(matched_list) >= 1:
                            matched_index_list.append(i)
                    
                if f.NOT:
                    f.matched_index_list = [i for i in range(len(list_of_str_list))
                                            if i not in matched_index_list]
                else:
                    f.matched_index_list = matched_index_list
                    
        elif data_type in ('int','bool','float'):
            
            if f.filter_value.upper() in ('*','ALL'):
                if f.NOT:
                    f.matched_index_list = []
                else:
                    f.matched_index_list = range(len(f.parentSet))
                return
            
            try:
                if data_type in ('int','bool'):
                    filter_num = int(f.filter_value)
                    num_list = [int(self.get(obj,f.property_name))
                                for obj in f.parentSet]
                else:
                    filter_num = float(f.filter_value)
                    num_list = [float(self.get(obj,f.property_name))
                                for obj in f.parentSet]
            except:
                if f.NOT:
                    f.matched_index_list = range(len(f.parentSet))
                else:
                    f.matched_index_list = []
                return            
            
            if f.filter_operator == '==(num)':
                matched_index_list = [i for (i,v) in enumerate(num_list)
                                      if v == filter_num]
            elif f.filter_operator == '<=':
                matched_index_list = [i for (i,v) in enumerate(num_list)
                                      if v <= filter_num]
            elif f.filter_operator == '>=':
                matched_index_list = [i for (i,v) in enumerate(num_list)
                                      if v >= filter_num]
            else:
                raise ValueError('Unexpected filter_operator: '+f.filter_operator)

            if f.NOT:
                f.matched_index_list = [i for i in range(len(num_list))
                                        if i not in matched_index_list]
            else:
                f.matched_index_list = matched_index_list
        
        elif data_type == 'int_list':
            
            if f.filter_value.upper() in ('*','ALL'):
                if f.NOT:
                    f.matched_index_list = []
                else:
                    f.matched_index_list = range(len(f.parentSet))
                return
            
            try:
                filter_num = int(f.filter_value)
            except:
                if f.NOT:
                    f.matched_index_list = range(len(f.parentSet))
                else:
                    f.matched_index_list = []
                return

            try:
                index = int(f.index)
            except:
                index = None
            
            list_of_int_list = [self.get(obj,f.property_name) 
                                for obj in f.parentSet]
            
            if index is not None:
                
                num_list = [L[index] for L in list_of_int_list]
                            
                if f.filter_operator == '==(num)':
                    matched_index_list = [i for (i,v) in enumerate(num_list)
                                          if v == filter_num]
                elif f.filter_operator == '<=':
                    matched_index_list = [i for (i,v) in enumerate(num_list)
                                          if v <= filter_num]
                elif f.filter_operator == '>=':
                    matched_index_list = [i for (i,v) in enumerate(num_list)
                                          if v >= filter_num]
                else:
                    raise ValueError('Unexpected filter_operator: '+f.filter_operator)
    
                if f.NOT:
                    f.matched_index_list = [i for i in range(len(num_list))
                                            if i not in matched_index_list]
                else:
                    f.matched_index_list = matched_index_list
            
            else:
                
                matched_index_list = []

                if f.filter_operator == '==(num)':
                    for (i,L) in enumerate(list_of_int_list):
                        matched_list = [v for v in L if v == filter_num]
                        if len(matched_list) >= 1:
                            matched_index_list.append(i)
                elif f.filter_operator == '<=':
                    for (i,L) in enumerate(list_of_int_list):
                        matched_list = [v for v in L if v <= filter_num]
                        if len(matched_list) >= 1:
                            matched_index_list.append(i)
                elif f.filter_operator == '>=':
                    for (i,L) in enumerate(list_of_int_list):
                        matched_list = [v for v in L if v >= filter_num]
                        if len(matched_list) >= 1:
                            matched_index_list.append(i)
                else:
                    raise ValueError('Unexpected filter_operator: '+f.filter_operator)
                        
                    
                if f.NOT:
                    f.matched_index_list = [i for i in range(len(list_of_int_list))
                                            if i not in matched_index_list]
                else:
                    f.matched_index_list = matched_index_list
                    
                    
        else:
            raise NotImplementedError('data_type: '+data_type)
        
            
    #----------------------------------------------------------------------
    def update_selected_elements(self, selected_row_ind_list):
        """ """
        
        # Update currently selected elements before exiting the dialog
        f = self.filters[self.selected_filter_index]
        matched_obj_list = [f.parentSet[i] for i in f.matched_index_list]
        self.selectedObjects = [matched_obj_list[i] for i in selected_row_ind_list]
                        
        self.emit(SIGNAL("readyForClosing"),())

                
        

########################################################################
class ChannelExplorerView(QDialog, Ui_Dialog):
    """ """
    
    #----------------------------------------------------------------------
    def __init__(self, model, isModal, can_modify_object_type, 
                 lattice_name, caller, parentWindow = None, settings = None):
        """Constructor"""
        
        QDialog.__init__(self, parent = parentWindow)
        
        self.settings = settings # QSettings object
        
        self.setWindowFlags(QtCore.Qt.Window) # To add Maximize & Minimize buttons
        
        self.model = model
        self.table_model_matched = model.table_model_matched
        self.table_model_filter = model.table_model_filter
        self.choice_dict = dict.fromkeys(PROP_NAME_LIST)
        
        # Set up the user interface from Designer
        self.setupUi(self)
    
        self.setModal(isModal)
        
        self.max_auto_adjust_column_width = 100
        
        if self.model.object_type == 'channel':
            self.radioButton_channels.setChecked(True)
        elif self.model.object_type == 'element':
            self.radioButton_elements.setChecked(True)
        else:
            raise ValueError('')
        
        if not can_modify_object_type:
            self.radioButton_channels.setEnabled(False)
            self.radioButton_elements.setEnabled(False)
        
        machine_name_list = MACHINE_DICT.keys()
        comboBox_machine_model = QStandardItemModel()
        for machine in machine_name_list:
            comboBox_machine_model.appendRow(QStandardItem(machine))
        self.comboBox_machine.setModel(comboBox_machine_model)
        self.comboBox_machine.setEditable(False)
        self.comboBox_machine.setSizeAdjustPolicy(QComboBox.AdjustToContents)
        self.comboBox_machine.setMinimumWidth(self.comboBox_machine.sizeHint().width())
        try:
            self.comboBox_machine.setCurrentIndex(machine_name_list.index(self.model.machine_name))
        except:
            self.comboBox_machine.setCurrentIndex(0)
        
        self._initLatticeList(lattice_name)
        #lattice_name_list = ap.machines.lattices()
        #comboBox_lattice_model = QStandardItemModel()
        #for lat in lattice_name_list:
            #comboBox_lattice_model.appendRow(QStandardItem(lat))
        #self.comboBox_lattice.setModel(comboBox_lattice_model)
        #self.comboBox_lattice.setEditable(False)
        #self.comboBox_lattice.setSizeAdjustPolicy(QComboBox.AdjustToContentsOnFirstShow)
        #try:
            #self.comboBox_lattice.setCurrentIndex(lattice_name_list.index(lattice_name))
        #except:
            #self.comboBox_lattice.setCurrentIndex(0)
        
        self.on_lattice_change()
        
        self._initContextMenuItems(caller)
        
        self.clipboard = np.array([])
        
        # Load QSettings
        self.loadViewSizeSettings()
        
    #----------------------------------------------------------------------
    def keyPressEvent(self, keyEvent):
        """"""
        
        if (self.focusWidget() is self.comboBox_simple_value) and \
           ( (keyEvent.key() == QtCore.Qt.Key_Enter) or \
             (keyEvent.key() == QtCore.Qt.Key_Return) ):
            self.pushButton_search.click()
        else:
            QDialog.keyPressEvent(self, keyEvent)

    #----------------------------------------------------------------------
    def _initLatticeList(self, lattice_name):
        """"""
                
        lattice_name_list = ap.machines.lattices()
        comboBox_lattice_model = QStandardItemModel()
        for lat in lattice_name_list:
            comboBox_lattice_model.appendRow(QStandardItem(lat))
        self.comboBox_lattice.setModel(comboBox_lattice_model)
        self.comboBox_lattice.setEditable(False)
        self.comboBox_lattice.setSizeAdjustPolicy(QComboBox.AdjustToContents)
        self.comboBox_lattice.setMinimumWidth(self.comboBox_lattice.sizeHint().width())
        try:
            self.comboBox_lattice.setCurrentIndex(lattice_name_list.index(lattice_name))
        except:
            self.comboBox_lattice.setCurrentIndex(0)
                

    #----------------------------------------------------------------------
    def saveViewSizeSettings(self):
        """"""
        
        settings = self.settings
        
        settings.beginGroup('DialogWindow')
        settings.setValue('position',self.geometry())
        settings.setValue('splitter_left_right_sizes',self.splitter_left_right.sizes())
        settings.setValue('splitter_top_bottom_sizes',self.splitter_top_bottom.sizes())
        settings.endGroup()
        
        print 'Settings saved.'
        
    #----------------------------------------------------------------------
    def loadViewSizeSettings(self):
        """"""
        
        settings = self.settings
        
        settings.beginGroup('DialogWindow')
        rect = settings.value('position')
        if rect is None:
            rect = QRect(0,0,self.sizeHint().width(),self.sizeHint().height())
        self.setGeometry(rect)
        
        splitter_left_right_sizes = settings.value('splitter_left_right_sizes')
        if splitter_left_right_sizes is None:
            # Adjust left-right splitter so that left widget takes max width
            # and right widget takes min width
            # QSplitter::setStretchFactor(int index, int stretch)
            self.splitter_left_right.setStretchFactor(0,1)
            self.splitter_left_right.setStretchFactor(1,0)
        else:
            splitter_sizes = [int(s) for s in splitter_left_right_sizes] # convert from string to int
            self.splitter_left_right.setSizes(splitter_sizes)

        splitter_top_bottom_sizes = settings.value('splitter_top_bottom_sizes')
        if splitter_top_bottom_sizes is None:
            # setStretchFactor does not work for the top-bottom splitter, since
            # I can't figure out how to minimize QStackedWidget. The following method
            # works. As long as the height fraction of the top portion is small
            # enough, the stacked widget will be minimized.
            splitter_sizes = [self.height()*(1./10.), self.height()*(9./10.)]
        else:
            splitter_sizes = [int(s) for s in splitter_top_bottom_sizes] # convert from string to int
        self.splitter_top_bottom.setSizes(splitter_sizes)
        
        
        settings.endGroup()
        
        print 'Settings loaded.'
        
        
            
    #----------------------------------------------------------------------
    def _initContextMenuItems(self, caller):
        """"""
        
        t = self.tableView_matched

        t.actionCopySelectedItemsTexts = QAction(
            QIcon(), 'Copy texts of selected item(s)', t)

        t.actionCopySelectedItemsTexts.setShortcut(
            QKeySequence(QtCore.Qt.ControlModifier + QtCore.Qt.Key_C))
        self.addAction(t.actionCopySelectedItemsTexts)
        ''' This addAction is critical for the shortcut to always work.
        If you only do addAction for the context menu below, the
        shortcut will not work, because the widget to which this
        action is added will be listening for key events.
        '''
        
        t.actionOpenTunerForSelectedChannels = QAction(
            QIcon(), 'Open tuner for selected channel(s)', t)
        
        t.actionOpenPlotterForSelectedChannels = QAction(
            QIcon(), 'Open plotter for selected channel(s)', t)
        
        self.connect(t.actionCopySelectedItemsTexts,
                     SIGNAL('triggered()'),
                     self.copySelectedItemsTexts)
        self.connect(t.actionOpenTunerForSelectedChannels,
                     SIGNAL('triggered()'),
                     self.openTunerForSelectedChannels)
        self.connect(t.actionOpenPlotterForSelectedChannels,
                     SIGNAL('triggered()'),
                     self.openPlotterForSelectedChannels)
        
        t.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        t.contextMenuForChannels = QMenu()
        t.contextMenuForElems = QMenu()
        
        if caller == 'aplattuner':
            t.contextMenuForChannels.addAction(t.actionCopySelectedItemsTexts)            

            t.contextMenuForElems.addAction(t.actionCopySelectedItemsTexts)            

        elif caller in ('__main__', None):
            t.contextMenuForChannels.addAction(t.actionCopySelectedItemsTexts)    
            t.contextMenuForChannels.addSeparator()
            t.contextMenuForChannels.addAction(t.actionOpenTunerForSelectedChannels)
            t.contextMenuForChannels.addSeparator()
            t.contextMenuForChannels.addAction(t.actionOpenPlotterForSelectedChannels)
            
            t.contextMenuForElems.addAction(t.actionCopySelectedItemsTexts)
        
        else:
            raise NotImplementedError('caller name: '+str(caller))
        
        t.contextMenuForChannels.setDefaultAction(t.actionCopySelectedItemsTexts)
        t.contextMenuForElems.setDefaultAction(t.actionCopySelectedItemsTexts)
            
        
    #----------------------------------------------------------------------
    def openContextMenu(self, qpoint):
        """"""
        
        if self.selectedRowIndList() == []:
            return
        
        sender = self.sender()
        
        cursor_pos = QCursor.pos()
        
        object_type = self.model.object_type 
        if object_type == 'channel':
            sender.contextMenuForChannels.exec_(cursor_pos)
        elif object_type == 'element':
            sender.contextMenuForElems.exec_(cursor_pos)
        else:
            raise ValueError('Unexpected object_type: '+object_type)

    #----------------------------------------------------------------------
    def copySelectedItemsTexts(self):
        """"""
        
        t = self.tableView_matched
        
        proxyItemSelectionModel = t.selectionModel()
        proxyItemSelection = proxyItemSelectionModel.selection()
        
        #proxyModelIndexList = t.selectedIndexes()
        
        proxyMod = t.model()

        proxyItemSelectionCount = proxyItemSelection.count()
        if proxyItemSelectionCount == 0:
            return
        else:
            #proxyItemSelectionRange = proxyItemSelection.first()
            #proxyModelIndexList = proxyItemSelectionRange.indexes()
            #nRows = proxyItemSelectionRange.height()
            #nCols = proxyItemSelectionRange.width()
            #self.clipboard = np.empty((nRows,nCols),dtype=np.object)
            #flat = self.clipboard.transpose().flatten()
            proxyModelIndexList = proxyItemSelection.indexes()
            self.clipboard = np.empty(len(proxyModelIndexList),dtype=np.object)
            for (i,proxyInd) in enumerate(proxyModelIndexList):
                text = proxyMod.data(proxyInd)
                #flat[i] = text
                self.clipboard[i] = text
            #self.clipboard = flat.reshape((nCols,nRows)).transpose()
            
            #print self.clipboard
            system_clipboard = qApp.clipboard()
            system_clipboard.setText('\n'.join(self.clipboard))

        
        
    #----------------------------------------------------------------------
    def openTunerForSelectedChannels(self):
        """"""
        
        print 'Not implemented yet'
        
    #----------------------------------------------------------------------
    def openPlotterForSelectedChannels(self):
        """"""

        print 'Not implemented yet'
        
    
    #----------------------------------------------------------------------
    def updateChoiceListComboBox(self):
        """"""
        
        choice_combobox_model = self.comboBox_choice_list.model()
        
        matched_model = self.table_model_matched
        
        nCols = matched_model.columnCount()
        nRows = matched_model.rowCount()
        column_name_list = [matched_model.horizontalHeaderItem(i).text()
                            for i in range(nCols)]
        
        for i in range(nCols):
                
            col_name = column_name_list[i]
            prop_name_and_full_name_and_data_type = \
                [(k,v[ENUM_ELEM_FULL_DESCRIP_NAME],v[ENUM_ELEM_DATA_TYPE])
                 for (k,v) in ELEM_PROPERTIES.iteritems()
                 if v[ENUM_ELEM_SHORT_DESCRIP_NAME] == col_name][0]
            prop_name, full_name, data_type = \
                prop_name_and_full_name_and_data_type
            self.choice_dict[prop_name] = list(matched_model.underlying2DTable[:,i])
            if data_type.endswith('_list'): # and (not ( (prop_name == 'fields') and (self.model.object_type) ) ):
                # Flatten the list of lists
                if (self.choice_dict[prop_name] != []) and ( isinstance(self.choice_dict[prop_name][0], list) ):
                    if data_type.startswith('string'):
                        empty_list_filler = ''
                    else:
                        empty_list_filler = None
                    filled_list = [L if L != [] else [empty_list_filler] for L in self.choice_dict[prop_name]]
                    self.choice_dict[prop_name] = [x for L in filled_list for x in L]
                    #new_choice_list = []
                    #for L in self.choice_dict[prop_name]:
                        #if L != []:
                            #for x in L:
                                #new_choice_list.append(x)
                        #else: # If self.choice_dict[prop_name] was [[],[],...,[]]
                            #if data_type.startswith('string'):
                                #new_choice_list.append('')
                            #else:
                                #new_choice_list.append(None)
                    #self.choice_dict[prop_name] = new_choice_list
            if data_type.startswith('string'):
                key_func = lower
            else:
                key_func = None
            self.choice_dict[prop_name] = sorted(set(self.choice_dict[prop_name]),key=key_func)
            
            choice_combobox_model.setData(
                choice_combobox_model.index(i,0),
                (full_name + ' [' + str(len(self.choice_dict[prop_name])) 
                 + ']')
            )
        
        self.comboBox_choice_list.update()
        
        self.updateChoiceListView()
        
    
    #----------------------------------------------------------------------
    def updateChoiceListView(self):
        """"""
        
        choice_list_model = self.listView_choice_list.model()
        
        full_prop_name = self.comboBox_choice_list.currentText().split('[')[0].strip()
        prop_name = [k for (k,v) in ELEM_PROPERTIES.iteritems()
                     if v[ENUM_ELEM_FULL_DESCRIP_NAME]==full_prop_name][0]
        
        choice_list = self.choice_dict[prop_name]
        if choice_list is not None:
            choice_list_model.setRowCount(len(choice_list))
            choice_list_model.setColumnCount(1)
            for (i,v) in enumerate(choice_list):
                #choice_list_model.setData(choice_list_model.index(i,0), str(v))
                # or
                choice_list_model.setItem(i,0,QStandardItem(str(v)))
                choice_list_model.item(i,0).setEditable(False)
                    
    
    #----------------------------------------------------------------------
    def updateSmartComboBoxes(self, filterObject):
        """"""
        
        displayed_property_name = filterObject.property_name_displayed
        
        if self.radioButton_simple.isChecked():
            comboBox_operator = self.comboBox_simple_operator
            comboBox_property = self.comboBox_simple_property
            comboBox_value = self.comboBox_simple_value
        else:
            filter_index = self.model.filters.index(filterObject)
            # comboBox_operator = ???
            raise NotImplementedError('')
        
        data_type = ELEM_PROPERTIES[displayed_property_name][ENUM_ELEM_DATA_TYPE]
        filter_operators = FILTER_OPERATOR_DICT[data_type]
        model_operator = QStandardItemModel(len(filter_operators),1,comboBox_operator)
        for (i,op) in enumerate(filter_operators):
            model_operator.setData(model_operator.index(i,0),op)
        comboBox_operator.setModel(model_operator)
        comboBox_operator.setSizeAdjustPolicy(QComboBox.AdjustToContents)
                
        self.updateIndexComboBox(comboBox_property.currentText())
        
        value_list = [self.model.get(o,displayed_property_name)
                      for o in filterObject.parentSet]
        if not data_type.endswith('_list'):
            value_list = sorted( list(set(value_list)), key=lower )
        else:
            value_list = sorted( list(set( reduce(add, value_list) )), key=lower )
        model_value = QStandardItemModel(len(value_list)+1,1,comboBox_value)
        current_value = comboBox_value.currentText()
        model_value.setData(model_value.index(0,0),current_value)
        for (i,v) in enumerate(value_list):
            model_value.setData(model_value.index(i+1,0),v)
        comboBox_value.setModel(model_value)
        comboBox_value.setInsertPolicy(QComboBox.InsertAlphabetically)
        comboBox_value.setSizeAdjustPolicy(QComboBox.AdjustToContents)
        comboBox_value.adjustSize()
            
    #----------------------------------------------------------------------
    def _initChoiceList(self):
        """"""
        
        model_property = self.createPropertyListModel(
            self.comboBox_choice_list)
        self.comboBox_choice_list.setModel(model_property)
        self.comboBox_choice_list.setSizeAdjustPolicy(
            QComboBox.AdjustToContents)
        self.comboBox_choice_list.setMinimumWidth(
            self.comboBox_choice_list.sizeHint().width())
        
        model_choice_list = QStandardItemModel()
        self.listView_choice_list.setModel(model_choice_list)
        
        
    #----------------------------------------------------------------------
    def _changeFilterMode(self, checked):
        """"""
        
        if not checked:
            return
        
        sender = self.sender()
        
        if sender == self.radioButton_simple:
            self.stackedWidget.setCurrentWidget(self.page_simple)
            advanced_filters = self.model.filters
            self.model.filters = self.model.hidden_filters
            self.model.hidden_filters = advanced_filters
        elif sender == self.radioButton_advanced:
            self.stackedWidget.setCurrentWidget(self.page_advanced)
            simple_filters = self.model.filters
            self.model.filters = self.model.hidden_filters
            self.model.hidden_filters = simple_filters
        else:
            raise ValueError('Unexpected sender')
        
        self.model.selected_filter_index = 0
        
    #----------------------------------------------------------------------
    def _changeObjectType(self, checked):
        """"""
        
        if checked:
            
            sender = self.sender()

            if sender == self.radioButton_elements:
                object_type = 'element'               
            elif sender == self.radioButton_channels:
                object_type = 'channel'               
            else:
                raise ValueError('Unexpected sender')
            
            self.emit(SIGNAL('objectTypeChanged'),object_type)
        
        
    #----------------------------------------------------------------------
    def getFilterModeStr(self):
        """"""
        
        currentWidget = self.stackedWidget.currentWidget()
        
        if currentWidget == self.page_simple:
            return 'simple'
        elif currentWidget == self.page_advanced:
            return 'advanced'
        else:
            raise ValueError('Unexpected current widget for QStackedWidget')
        
    
    #----------------------------------------------------------------------
    def createPropertyListModel(self, parent):
        """"""
        
        model_property = QStandardItemModel(len(PROP_NAME_LIST),1, parent)
        property_display_name_list = sorted([
            ELEM_PROPERTIES[name][ENUM_ELEM_FULL_DESCRIP_NAME]
            for name in PROP_NAME_LIST], key=str.lower)
        for (i,name) in enumerate(property_display_name_list):
            model_property.setData(model_property.index(i,0), name)
        
        return model_property
        
    #----------------------------------------------------------------------
    def _initFilterView(self):
        """"""
        
        self.tableWidget_filter.setRowCount(0)
        
        self.settings.beginGroup('General')
        filter_mode_str = self.settings.value('filter_mode_string')
        if filter_mode_str is None:
            filter_mode_str = 'simple'
        if filter_mode_str == 'simple':
            page_obj = self.page_simple
        elif filter_mode_str == 'advanced':
            page_obj = self.page_advanced
        else:
            raise ValueError('Unexpected filter mode: '+filter_mode_str)
        self.stackedWidget.setCurrentWidget(page_obj)
        self.settings.endGroup()
        
        
        filterModeStr = self.getFilterModeStr()
        if filterModeStr == 'simple':
            
            self.tableWidget_filter.setHidden(True) # By hiding this table, screen real estate is maximized for splitter.
            
            
            self.radioButton_simple.setChecked(True)
            self.stackedWidget.setCurrentWidget(self.page_simple)
                        
            NOT_checked = False
            self.checkBox_simple_NOT.setChecked(NOT_checked)
            
            init_property_name = 'family'
            model_property = self.createPropertyListModel(
                self.comboBox_simple_property)
            self.comboBox_simple_property.setModel(model_property)
            self.comboBox_simple_property.setSizeAdjustPolicy(
                QComboBox.AdjustToContents)
            self.comboBox_simple_property.setCurrentIndex(
                self.comboBox_simple_property.findText(
                    ELEM_PROPERTIES[init_property_name][ENUM_ELEM_FULL_DESCRIP_NAME],
                    flags=(QtCore.Qt.MatchExactly | QtCore.Qt.MatchCaseSensitive)
                    )
                )
            
            data_type = ELEM_PROPERTIES[init_property_name][ENUM_ELEM_DATA_TYPE]
            filter_operators = sorted(FILTER_OPERATOR_DICT[data_type],key=str.lower)
            model_operator = QStandardItemModel(len(filter_operators),1,
                self.comboBox_simple_operator)
            for (i,op) in enumerate(filter_operators):
                model_operator.setData(model_operator.index(i,0),op)
            self.comboBox_simple_operator.setModel(model_operator)
            self.comboBox_simple_operator.setSizeAdjustPolicy(
                QComboBox.AdjustToContents)
            
            
            self.updateIndexComboBox(self.comboBox_simple_property.currentText())
            
            if data_type in ('string','string_list'):
                init_value = '*'
            else:
                init_value = 'ALL'
            value_list = sorted(list(set([self.model.get(e,init_property_name)
                                          for e in self.model.currentParentSet])),
                                key=lower)
            model_value = QStandardItemModel(len(value_list)+1,1,
                                             self.comboBox_simple_value)
            model_value.setData(model_value.index(0,0),init_value)
            for (i,v) in enumerate(value_list):
                model_value.setData(model_value.index(i+1,0),v)
            self.comboBox_simple_value.setModel(model_value)
            self.comboBox_simple_value.setSizeAdjustPolicy(
                QComboBox.AdjustToContents)
            
            self.model.filters[0].NOT_displayed = NOT_checked
            self.model.filters[0].property_name_displayed = init_property_name
            self.model.filters[0].filter_operator_displayed = self.comboBox_simple_operator.currentText()
            self.model.filters[0].index_displayed = self.comboBox_simple_index.currentText()
            self.model.filters[0].filter_value_displayed = self.comboBox_simple_value.currentText()
            
            self.model.filters[0].commit_displayed_properties()
            
            modified_filter_name = self.model.filters[0].name
            
            self.emit(SIGNAL('filtersChanged'), modified_filter_name)
            
            
        elif filterModeStr == 'advanced':
            self.tableWidget_filter.setHidden(False)

        else:
            raise ValueError('Unexpected filterModeStr')
        
        
    #----------------------------------------------------------------------
    def updateIndexComboBox(self, property_text):
        """"""
        
        filterModeStr = self.getFilterModeStr()
        if filterModeStr == 'simple':
            indexComboBox = self.comboBox_simple_index
        elif filterModeStr == 'advanced':
            sender = self.sender()
            raise NotImplementedError('')
        else:
            raise ValueError('Unexpected filterModeStr')
        
        
        if property_text.startswith('Field:'):
            isList = False
        else:
            for (k,v) in ELEM_PROPERTIES.iteritems():
                if v[ENUM_ELEM_FULL_DESCRIP_NAME] == property_text:
                    data_type = v[ENUM_ELEM_DATA_TYPE]
                    property_name = k                    
                    break
            if data_type.endswith('_list'):
                isList = True
            else:
                isList = False
            
        if not isList:
            indexComboBoxModel = QStandardItemModel(1,1,indexComboBox)
            indexComboBoxModel.setData(indexComboBoxModel.index(0,0),'N/A')
        else:
            first_list_len = len(
                self.model.get(self.model.currentParentSet[0],property_name)
            )
            isEqualLen = all(
                [len(self.model.get(e,property_name)) == first_list_len 
                 for e in self.model.currentParentSet] )
            
            if isEqualLen:
                indexComboBoxModel = QStandardItemModel(first_list_len+1,1,
                                                        indexComboBox)
                indexComboBoxModel.setData(indexComboBoxModel.index(0,0),'ALL')
                for i in range(first_list_len):
                    indexComboBoxModel.setData(indexComboBoxModel.index(i+1,0), str(i))
            else:
                indexComboBoxModel = QStandardItemModel(1,1,indexComboBox)
                indexComboBoxModel.setData(indexComboBoxModel.index(0,0),'N/A')
                

        indexComboBox.setModel(indexComboBoxModel)
        indexComboBox.setSizeAdjustPolicy(QComboBox.AdjustToContents)
            
        
    #----------------------------------------------------------------------
    def _initMatchTable(self):
        """
        Perform initial formating for tableWidget_choice_list
        """
                
        self.table_proxyModel_matched = QSortFilterProxyModel()
        self.table_proxyModel_matched.setSourceModel(self.table_model_matched)
        self.table_proxyModel_matched.setDynamicSortFilter(False)
        self.table_proxyModel_matched.setSortRole(self.table_model_matched.SortRole)
        
        t = self.tableView_matched # shorthand notation
        t.setModel(self.table_proxyModel_matched)
        t.setCornerButtonEnabled(True)
        t.setShowGrid(True)
        t.setSelectionMode(QAbstractItemView.ExtendedSelection)
        t.setSelectionBehavior(QAbstractItemView.SelectItems)
        t.setAlternatingRowColors(True)
        horizHeader = t.horizontalHeader()
        horizHeader.setSortIndicatorShown(True)
        horizHeader.setStretchLastSection(True)
        horizHeader.setMovable(True)
        t.resizeColumnsToContents()
        self.checkBox_matched_table_column_sorting.setChecked(self.model.is_column_sorting)
        t.setSortingEnabled(self.model.is_column_sorting)
        
        self.proxyItemSelModel_matched = QItemSelectionModel(self.table_proxyModel_matched)
        t.setSelectionModel(self.proxyItemSelModel_matched)

        '''
        It is important that this connection is made here, not in ChannelExplorerApp.__init__().
        The reason is that the sender (the selection model) will be created as new, 
        whenever this function is called. Hence, the previously made connections will be
        invalidated, and you have to reconnect the signal to the newly created selection
        model here. 
        '''
        self.connect(self.proxyItemSelModel_matched,
                     SIGNAL('selectionChanged(const QItemSelection &, const QItemSelection &)'),
                     self.update_matched_and_selected_numbers)

        
    #----------------------------------------------------------------------
    def update_tables(self):
        """ """
        
        t = self.tableView_matched # shorthand notation
        t.resizeColumnsToContents()
        proxyModel = t.model()
        m = proxyModel.sourceModel()
        for i in range(m.columnCount()):
            if t.columnWidth(i) > self.max_auto_adjust_column_width:
                t.setColumnWidth(i,self.max_auto_adjust_column_width)
        
        ### Reset selection to all available
        t.selectAll()
        
        self.emit(SIGNAL('readyForChoiceListUpdate'))


    #----------------------------------------------------------------------
    def setMatchedTableColumnSortingEnabled(self, check_state_int):
        """"""
        
        if check_state_int == QtCore.Qt.Unchecked:
            self.tableView_matched.setSortingEnabled(False)
        elif check_state_int == QtCore.Qt.Checked:
            self.tableView_matched.setSortingEnabled(True)
        else:
            raise ValueError('Partially checked state is NOT expected for column sorting checkbox.')
        
    #----------------------------------------------------------------------
    def update_matched_and_selected_numbers(self, selected=None, deselected=None):
        """ """
        
        f = self.model.filters[self.model.selected_filter_index]
        
        nMatched = len(f.matched_index_list)
        
        nSelected = len(self.selectedRowIndList())                        
        
        self.label_nMatched_nSelected.setText(
            'Matched Elements (' + str(nMatched) + ' matched, ' 
            + str(nSelected) + ' selected)')
        
    #----------------------------------------------------------------------
    def auto_increment_filter_name(self):
        """"""

        new_filter_name = 'filter1'
        
        if self.model.filters == []:
            return new_filter_name
        
        existing_names = [f.name for f in self.model.filters
                          if f.name.startswith('filter')]
        
        if existing_names == []:
            return new_filter_name
        
        filter_name_numbers = []
        for n in existing_names:
            try:
                filter_name_numbers.append( int(n.replace('filter','')) )
            except:
                filter_name_numbers.append( 0 )
        
        new_filter_name = 'filter' + str(max(filter_name_numbers)+1)
        
        return new_filter_name
        
    #----------------------------------------------------------------------
    def enforce_exclusiveness(self, clickedRadiobutton=None):
        """"""
        
        if clickedRadiobutton is None:
            clickedRadiobutton = self.sender()
            
        t = self.tableWidget_filter
        
        nRows = t.rowCount()
        
        for i in range(nRows):
            if t.cellWidget(i,0) != clickedRadiobutton:
                t.cellWidget(i,0).setChecked(False)
            else:
                t.cellWidget(i,0).setChecked(True)
            
        
        
    #----------------------------------------------------------------------
    def add_row_to_filter_table(self):
        """ """
        
        newf = Filter(self.auto_increment_filter_name(), self.model)
        
        self.model.filters.append(newf)
        
        ## Need to disconnect this signal-slot since each change in each item
        ## will cause re-filtering, which const a lot of time. It will be
        ## reconnected at the end of this function.
        #self.disconnect(self.tableWidget_filter, 
                        #Qt.SIGNAL('itemChanged(QTableWidgetItem *)'),
                        #self.on_filter_item_change)
        
        t = self.tableWidget_filter # shorthand notation
        
        nRows = t.rowCount()+1
 
        t.setRowCount(nRows) # Add a new row to the table
        
        new_row_index = nRows-1
        
        obj = QRadioButton()
        obj.setChecked(True)
        t.setCellWidget(new_row_index,0,obj)
        self.enforce_exclusiveness(obj)
        self.connect(obj, SIGNAL('clicked()'),
                     self.enforce_exclusiveness)
        
        t.setItem(new_row_index,1,
                  QtGui.QTableWidgetItem(newf.name))
        
        obj = QComboBox()
        available_filters = self.model.filters[:new_row_index]
        m = QStandardItemModel(len(available_filters)+1, 1)
        m.setData(m.index(0,0),'ALL')
        for (i,f) in enumerate(available_filters):
            m.setData(m.index(i+1,0), f.name)
        obj.setModel(m)
        t.setCellWidget(new_row_index,2,obj)
        
        obj = QComboBox()
        m = QStandardItemModel(2,1)
        m.setData(m.index(0,0),'AND')
        m.setData(m.index(1,0),'OR')
        obj.setModel(m)
        t.setCellWidget(new_row_index,3,obj)
        
        obj = QComboBox()
        m = QStandardItemModel(len(available_filters)+2, 1)
        m.setData(m.index(0,0),'NEW')
        m.setData(m.index(1,0),'ALL')
        for (i,f) in enumerate(available_filters):
            m.setData(m.index(i+2,0), f.name)
        obj.setModel(m)
        t.setCellWidget(new_row_index,4,obj)

        t.setCellWidget(new_row_index,5,QCheckBox())
        
        obj = QComboBox()
        m = QStandardItemModel(len(PROP_NAME_LIST), 1)
        for (i,n) in enumerate(PROP_NAME_LIST):
            m.setData(m.index(i,0), 
                      ELEM_PROPERTIES[n][ENUM_ELEM_FULL_DESCRIP_NAME])
        obj.setModel(m)
        t.setCellWidget(new_row_index,6,obj)

        t.setCellWidget(new_row_index,7,QComboBox())
        t.setCellWidget(new_row_index,8,QComboBox())
        t.setCellWidget(new_row_index,9,QComboBox())

        #for (i, filter_prop) in enumerate(self.model.filter_property_list):
            #if filter_prop is not 'exclude':
                #t.setItem(new_row_index,i,
                          #Qt.QTableWidgetItem(''))
                    
                #t.item(new_row_index,i).setFlags(Qt.Qt.ItemIsSelectable|
                                                 #Qt.Qt.ItemIsEditable|
                                                 #Qt.Qt.ItemIsDragEnabled|
                                                 #Qt.Qt.ItemIsEnabled) # Make it editable
            #else:
                #t.setItem(new_row_index,i,Qt.QTableWidgetItem(''))
                
                #t.item(new_row_index,i).setFlags(Qt.Qt.ItemIsSelectable|
                                                 #Qt.Qt.ItemIsEditable|
                                                 #Qt.Qt.ItemIsDragEnabled|
                                                 #Qt.Qt.ItemIsUserCheckable|
                                                 #Qt.Qt.ItemIsEnabled) # Make it checkable
                
                #t.item(new_row_index,i).setCheckState(Qt.Qt.Unchecked)
                        
        
        ## Reconnecting the temporarily disconnected signal-slot
        #self.connect(self.tableWidget_filter, 
                     #Qt.SIGNAL('itemChanged(QTableWidgetItem *)'),
                     #self.on_filter_item_change)
        
        
        self.emit(SIGNAL("filterRowAdded"),())
    
    
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
    def on_machine_change(self, lattice_name=''):
        """"""
        
        self._initLatticeList(lattice_name)
        
        lattice_name_list = ap.machines.lattices()
        selected_lattice_name = lattice_name_list[
            self.comboBox_lattice.currentIndex()]
                
    #----------------------------------------------------------------------
    def on_lattice_change(self):
        """"""
        
        try:
            self._initFilterView()
            self._initChoiceList()
            self._initMatchTable()
        
            self.model.updateFilters(None)
        except:
            print 'Exception on view.on_lattice_change'
            #pass
        
    #----------------------------------------------------------------------
    def on_NOT_change(self, checked):
        """"""
        
        f = self.model.filters[self.model.selected_filter_index]
        f.NOT_displayed = checked

    #----------------------------------------------------------------------
    def on_property_change(self, displayed_text):
        """"""
        
        f = self.model.filters[self.model.selected_filter_index]
        
        if ':' in displayed_text:
            pass
        else:
            for (k,v) in ELEM_PROPERTIES.iteritems():
                if v[ENUM_ELEM_FULL_DESCRIP_NAME] == displayed_text:
                    f.property_name_displayed = k
                    break
        
        self.emit(SIGNAL('displayedFilterPropertyChanged'), f)

    #----------------------------------------------------------------------
    def on_filter_operator_change(self, displayed_text):
        """"""
        
        f = self.model.filters[self.model.selected_filter_index]
        f.filter_operator_displayed = displayed_text

    #----------------------------------------------------------------------
    def on_index_change(self, displayed_text):
        """"""
        
        f = self.model.filters[self.model.selected_filter_index]
        f.index_displayed = displayed_text
        
        if f.index_displayed != 'N/A':
            value_list = [self.model.get(o,f.property_name_displayed)
                          for o in f.parentSet]
            if f.index_displayed == 'ALL':
                value_list = sorted( list(set( reduce(add, value_list) )), key=lower )
            else:
                index = int(f.index_displayed)
                value_list = sorted( list(set( [v[index] for v in value_list]) ), key=lower )
            
            if self.radioButton_simple.isChecked():
                comboBox_value = self.comboBox_simple_value
            else:
                comboBox_value = []
                raise NotImplementedError('')
            
            model_value = QStandardItemModel(len(value_list)+1,1,comboBox_value)
            current_value = comboBox_value.currentText()
            model_value.setData(model_value.index(0,0),current_value)
            for (i,v) in enumerate(value_list):
                model_value.setData(model_value.index(i+1,0),v)
            comboBox_value.setModel(model_value)
            comboBox_value.setSizeAdjustPolicy(QComboBox.AdjustToContents)
        
        
    #----------------------------------------------------------------------
    def on_filter_value_change(self, displayed_text):
        """"""
        
        f = self.model.filters[self.model.selected_filter_index]
        f.filter_value_displayed = displayed_text
        
    
    #----------------------------------------------------------------------
    def on_filter_item_change(self, qTableWidgetItem):
        """
        
        """
        
        if not self.isItemUserCheckable(qTableWidgetItem):
            filter_val = str(
                qTableWidgetItem.data(Qt.Qt.DisplayRole) )
        else:
            filter_val = (qTableWidgetItem.checkState() == Qt.Qt.Checked)
        
        filter_group_index    = qTableWidgetItem.row()
        filter_property_index = qTableWidgetItem.column()
        
        isCaseSensitive = self.checkBox_filter_case_sensitive.isChecked()

        self.emit(Qt.SIGNAL("sigFilterSpecNeedsChange"),
                  filter_property_index, filter_val, 
                  filter_group_index, isCaseSensitive)
        
    #----------------------------------------------------------------------
    def selectedRowIndList(self):
        """"""
    
        qProxyModelIndexList = self.tableView_matched.selectedIndexes()
        row_ind_list = sorted(set([q.row() for q in qProxyModelIndexList]))
        
        return row_ind_list
        
        
    #----------------------------------------------------------------------
    def closeEvent(self, event):
        """"""
        
        # Save QSettings
        self.saveViewSizeSettings()
        
        event.accept()
        
    #----------------------------------------------------------------------
    def accept(self):
        """ """
        
        # Update currently selected elements before exiting the dialog
        selected_row_ind_list = self.selectedRowIndList()
                
        self.emit(SIGNAL("updateFinalSelection"),
                  selected_row_ind_list)
        
    #----------------------------------------------------------------------
    def accept_and_close(self):
        """ """
        
        super(ChannelExplorerView, self).accept() # will close the dialog
        
        
    #----------------------------------------------------------------------
    def reject(self):
        """ """
        
        super(ChannelExplorerView, self).reject() # will close the dialog
    

########################################################################
class ChannelExplorerApp(QObject):
    """ """

    #----------------------------------------------------------------------
    def __init__(self, modal = True, parentWindow = None, 
                 init_object_type = 'element', can_modify_object_type = True,
                 machine_name = None, lattice_name = None, caller = None):
        """Constructor"""
        
        QObject.__init__(self)
        
        self.settings = QSettings('HLA','ChannelExplorer')
        
        ###
        self.settings.beginGroup('General')
        
        if machine_name is None:
            machine_name = self.settings.value('machine_name')
            if machine_name is None:
                machine_name = 'NSLS2V2'
                
        initMachine(machine_name)
            
        if lattice_name is None:
            lattice_name = self.settings.value('lattice_name')
            if lattice_name is None:
                lattice_name = 'V2SR'
                
        print 'Using Lattice:', lattice_name
        ap.machines.use(lattice_name)
        
        self.settings.endGroup()
        ###
        
        self.modal = modal
        self.parentWindow = parentWindow
        
        self._initModel(machine_name, init_object_type)
        self._initView(can_modify_object_type, lattice_name, caller)
        
        self.connect(self.view.radioButton_simple,SIGNAL('toggled(bool)'),
                     self.view._changeFilterMode)
        self.connect(self.view.radioButton_advanced,SIGNAL('toggled(bool)'),
                     self.view._changeFilterMode)
        
        self.connect(self.view.radioButton_elements,SIGNAL('toggled(bool)'),
                     self.view._changeObjectType)
        self.connect(self.view.radioButton_channels,SIGNAL('toggled(bool)'),
                     self.view._changeObjectType)
        self.connect(self.view,SIGNAL('objectTypeChanged'),
                     self.model._changeObjectType)
        
        self.connect(self.view.checkBox_simple_NOT,SIGNAL('toggled(bool)'),
                     self.view.on_NOT_change)
        self.connect(self.view.comboBox_simple_property,
                     SIGNAL('currentIndexChanged(const QString &)'),
                     self.view.on_property_change)
        self.connect(self.view.comboBox_simple_operator,
                     SIGNAL('currentIndexChanged(const QString &)'),
                     self.view.on_filter_operator_change)
        self.connect(self.view.comboBox_simple_index,
                     SIGNAL('currentIndexChanged(const QString &)'),
                     self.view.on_index_change)
        self.connect(self.view.comboBox_simple_value,
                     SIGNAL('currentIndexChanged(const QString &)'),
                     self.view.on_filter_value_change)
        self.connect(self.view.comboBox_simple_value,
                     SIGNAL('editTextChanged(const QString &)'),
                     self.view.on_filter_value_change)
        
        self.connect(self.view, SIGNAL('displayedFilterPropertyChanged'),
                     self.view.updateSmartComboBoxes)
        
        self.connect(self.view.comboBox_simple_property,
                     SIGNAL('currentIndexChanged(const QString &)'),
                     self.view.updateIndexComboBox)

        self.connect(self.view.pushButton_search, SIGNAL('clicked()'),
                     self.model.search)
        self.connect(self.view, SIGNAL('filtersChanged'),
                     self.model.updateFilters)
        self.connect(self.model, SIGNAL('filtersChanged'),
                     self.model.updateFilters)
        
        self.connect(self.view, SIGNAL('readyForChoiceListUpdate'),
                     self.view.updateChoiceListComboBox)
        
        self.connect(self.view.comboBox_choice_list,
                     SIGNAL('currentIndexChanged(const QString &)'),
                     self.view.updateChoiceListView)


        # After new filtering is performed, update the view based on
        # the new filtered data.
        self.connect(self.model, SIGNAL('filtersUpdated'),
                     self.model.update_table_models)
        self.connect(self.model, SIGNAL('filtersUpdated'),
                     self.view.update_tables)
        self.connect(self.model, SIGNAL('filtersUpdated'),
                     self.view.update_matched_and_selected_numbers)
        
        
        #self.connect(self.view.pushButton_add_row, SIGNAL("clicked()"),
                     #self.view.add_row_to_filter_table)
        #self.connect(self.view, SIGNAL("sigFilterRowAdded"),
                     #self.model.add_row_to_filter_spec)
                     
        self.connect(self.view.pushButton_add_row, SIGNAL('clicked()'),
                     self.view.add_row_to_filter_table)
        
        
        self.connect(self.view.checkBox_matched_table_column_sorting,
                     SIGNAL('stateChanged(int)'),
                     self.view.setMatchedTableColumnSortingEnabled)
        
        self.connect(self.view.comboBox_machine,
                     SIGNAL('currentIndexChanged(const QString &)'),
                     self.model.on_machine_change)
        self.connect(self.model, SIGNAL('machineChanged'),
                     self.view.on_machine_change)
        #
        self.connect(self.view.comboBox_lattice,
                     SIGNAL('currentIndexChanged(const QString &)'),
                     self.model.on_lattice_change)
        #
        self.connect(self.model,
                     SIGNAL('modelReconstructedOnLatticeChange'),
                     self.view.on_lattice_change)

        
        self.connect(self.view, SIGNAL("updateFinalSelection"),
                     self.model.update_selected_elements)
        self.connect(self.model, SIGNAL("readyForClosing"),
                     self.view.accept_and_close)
        
        self.connect(self.view.tableView_matched,
                     SIGNAL('customContextMenuRequested(const QPoint &)'),
                     self.view.openContextMenu)
        
        self.connect(self.view.pushButton_preferences,
                     SIGNAL('clicked()'),
                     self.launchPrefDialog)
        
        
    #----------------------------------------------------------------------
    def debug(self):
        """"""
        
        print 'debug'
                
    #----------------------------------------------------------------------
    def launchPrefDialog(self):
        """"""
        
        prefDialog = Preferences(parentWindow=self.view)
        prefDialog.show()
        
    #----------------------------------------------------------------------
    def _initModel(self, machine_name, object_type):
        """ """
        
        self.model = ChannelExplorerModel(machine_name,
                                          object_type=object_type,
                                          settings=self.settings)
        
    #----------------------------------------------------------------------
    def _initView(self, can_modify_object_type, lattice_name, caller):
        """ """
        
        self.view = ChannelExplorerView(self.model, self.modal,
                                        can_modify_object_type,
                                        lattice_name, caller,
                                        parentWindow = self.parentWindow,
                                        settings = self.settings)
        
########################################################################
class Preferences(QDialog, Ui_Dialog_preferences):
    """"""

    #----------------------------------------------------------------------
    def __init__(self, parentWindow = None):
        """Constructor"""
        
        QDialog.__init__(self, parent=parentWindow)
        
        self.setupUi(self)
        
        selector = OrderSelector(parentWidget=self.page_column_visibility_order,
                                 label_text_NotSelected='NOT Visible Column Names:',
                                 label_text_Selected='Visible Column Names:')
        
        
        self.listWidget_NotSelected = selector.listWidget_NotSelected
        
        self.stackedWidget.setCurrentWidget(self.page_column_visibility_order)
        self.listWidget_group.setCurrentItem(
            self.listWidget_group.findItems('Columns',QtCore.Qt.MatchExactly)[0]
            )
        
        self.connect(self.listWidget_group,
                     SIGNAL('currentItemChanged(QListWidgetItem *, QListWidgetItem *)'),
                     self.changePage)
        
    #----------------------------------------------------------------------
    def changePage(self, currentItem, previousItem):
        """"""
        
        selected_text = currentItem.text()
        if selected_text == 'Columns':
            self.stackedWidget.setCurrentWidget(self.page_column_visibility_order)
        elif selected_text == 'Miscellaneous':
            self.stackedWidget.setCurrentWidget(self.page_misc)
        else:
            raise ValueError('Unexpected selected text: '+selected_text)
        
        
    


#----------------------------------------------------------------------
def lower(none_or_str_or_unicode_string):
    """"""
    
    try:
        return none_or_str_or_unicode_string.lower()
    except:
        return str(none_or_str_or_unicode_string).lower()
    
#----------------------------------------------------------------------
def initMachine(machine_name):
    """"""
    
    aphla_init_func_name = MACHINE_DICT[machine_name]
            
    if ap.machines._lat:
        ap.machines._lat = None
        ap.machines._lattice_dict = {}

    aphla_init_func = getattr(ap, aphla_init_func_name)
    print 'Initializing lattices...'
    tStart = tic()
    aphla_init_func()
    print 'Initialization took', toc(tStart), 'seconds.'
    #print 'Done.'
    
    

#----------------------------------------------------------------------
def make(modal = True, parentWindow = None, 
         init_object_type = 'element', can_modify_object_type = True,
         output_type = TYPE_OBJECT,
         machine_name = None, lattice_name = None,
         caller = None):
    """ """
    
    #if not ap.machines._lat:
        #print 'Initializing lattices...'
        #tStart = tic()
        #aphla_init_func()
        #print str(toc(tStart))
        #print 'Done.'    

    #print 'Using Lattice:', lattice_name
    #ap.machines.use(lattice_name)
    
    app = ChannelExplorerApp(modal, parentWindow, 
                             init_object_type, can_modify_object_type,
                             machine_name, lattice_name, caller)
    view = app.view
        
    if app.modal :
        view.exec_()
        
        if view.result() == QDialog.Accepted:
            if output_type == TYPE_OBJECT:
                output = app.model.selectedObjects
            elif output_type == TYPE_NAME:
                try:
                    output = [e.name for e in app.model.selectedObjects]
                except:
                    output = [(e[0].name,e[1]) for e in app.model.selectedObjects]
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
        
    #qapp = Qt.QApplication(args) # Necessary whether modal or non-modal
    
    #result = make(modal = True, output_type = TYPE_OBJECT)
    
    #if result.has_key('dialog_result'): # When modal
        #app           = result['app']
        #dialog_result = result['dialog_result']
        
        #print dialog_result
        #print 'Length = ', len(dialog_result)
        
        
    #else: # When non-modal
        #app = result['app']
        #exit_status = qapp.exec_()
        #sys.exit(exit_status)
        
    cothread.iqt()
    
    result = make(modal=True, output_type=TYPE_OBJECT,
                  init_object_type='channel',
                  caller='__main__')
    
    if result.has_key('dialog_result'): # When modal
        app           = result['app']
        dialog_result = result['dialog_result']
        
        print dialog_result
        print 'Length = ', len(dialog_result)
        
        
    else: # When non-modal
        app = result['app']
        #exit_status = qapp.exec_()
        #sys.exit(exit_status)
    
    cothread.WaitForQuit()
    

#----------------------------------------------------------------------    
if __name__ == "__main__" :
    main(sys.argv)
    
