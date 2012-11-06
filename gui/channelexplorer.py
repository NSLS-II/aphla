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

import sip
sip.setapi('QString', 2)
sip.setapi('QVariant', 2)

import sys
from fnmatch import fnmatchcase
from operator import and_, not_, add

import cothread

#import PyQt4.Qt as Qt
from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import SIGNAL, QObject
from PyQt4.QtGui import QDialog, QStandardItemModel, QStandardItem, \
     QComboBox, QTableWidgetItem, QRadioButton, QCheckBox

from Qt4Designer_files.ui_channel_explorer import Ui_Dialog

import aphla as ap

if not ap.machines._lat:
    print 'Initializing lattice...'
    ap.initNSLS2V1()
    print 'Done.'

# Output Type Enums
TYPE_OBJECT = 1
TYPE_NAME   = 2


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
PROP_NAME_LIST = sorted(ELEM_PROPERTIES.keys())

FILTER_OPERATOR_DICT = {'int': ['==(num)','<=','>='],
                        'bool': ['==(num)'],
                        'float': ['<=','>='],
                        'string': ['==(char)'],
                        'string_list': ['==(char)'],
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
class ElementSelectorModel(QObject):
    """ """

    #----------------------------------------------------------------------
    def __init__(self, object_type='element'):
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
        
        self.object_type = object_type
        
        self.is_case_sensitive = False
        
        ## key   = property name of Element object
        ## value = displayed column name for tables showing choices and matches
        #self.elem_property_vs_col_name = \
            #{'name':'Name', 'devname':'Dev. Name', 'cell':'Cell', 
             #'family':'Family', 'girder':'Girder', 'group':'Group', 
             #'index':'Lat. Index', 'length':'Eff.Len', 'phylen':'Phys. Len.',
             #'pv':'PV', 'sb':'sb', 'se':'se', 'symmetry':'Symmetry',
             #'virtual':'Virtual', 'sequence':'Sequence'}
        
        ## key   = property name of Element object & exclusion flag
        ## value = displayed column name for table showing filters
        #self.filter_property_vs_col_name = \
            #self.elem_property_vs_col_name.copy()
        #self.filter_property_vs_col_name.update({'exclude':'Excl.'}) # adding extra column
        
        ## Specify the default column order you want for tables showing
        ## choices and matches.
        #self.elem_property_list = ['family', 'name', 'devname', 'cell',
                                   #'girder', 'symmetry', 'group', 'virtual',
                                   #'sb', 'se', 'pv', 'length', 'phylen',
                                   #'index', 'sequence']
        self.col_name_list = [ELEM_PROPERTIES[name][ENUM_ELEM_SHORT_DESCRIP_NAME]
                              for name in PROP_NAME_LIST]
        #self.choice_dict = dict.fromkeys(self.elem_property_list)
        
        ## Specify the default column order you want for table showing
        ## filters.
        #self.filter_property_list = self.elem_property_list[:]
        #self.filter_property_list.insert(0, 'exclude')
        #self.filter_col_name_list = [self.filter_property_vs_col_name[prop]
                         #for prop in self.filter_property_list]
        #self.filter_dict = dict.fromkeys(self.filter_property_list)
        
        #self.numeric_filter_list = ['index', 'phylen', 'length', 'sb', 'se']
        #self.not_implemented_filter_list = ['sequence']
        
        #self.filter_spec = filter_spec
        
        self.allElements = ap.getElements('*')
        self.allFields = []
        for e in self.allElements:
            fields = e.fields()
            self.allFields.extend(fields)
        self.allFields = sorted(list(set(self.allFields)))
        self.allChannels = self.convertElemListToChannelList(self.allElements)

        if object_type == 'element':
            self.currentParentSet = self.allElements[:]
            
        elif object_type == 'channel':
            self.currentParentSet = self.allChannels[:]
        else:
            raise ValueError('Unexpected object_type: '+object_type)
        
        
        ## Initialization of matching data information
        #self.matched = [ [True]*len(self.allElements) ]
        #self.combine_matched_list()
        #self.update_choice_dict()
        
        ## Apply initial filters provided by a user, if any.
        #if self.filter_spec:
            #isCaseSensitive = False
            #self.filterData(range(len(self.filter_spec)), isCaseSensitive)
        
        self.selectedObjects = []
        
        # For "simple" mode
        filter_name = 'simple_filter'
        self.filters = [Filter(filter_name,self)]
        
        # For "advanced" mode
        #filter_name = 'filter1'
        self.hidden_filters = []
        
        self.selected_filter_index = 0
        
        
    #----------------------------------------------------------------------
    def updateCaseSensitiveState(self, checkBoxState):
        """"""
        
        self.is_case_sensitive = checkBoxState
        
        self.emit(SIGNAL('filtersChanged'),None)
        
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
        
        self.emit(SIGNAL('filtersChanged'), current_filter.name)
        
    #----------------------------------------------------------------------
    def updateFilters(self, modified_filter_name):
        """
        Assuming that filter sets available to a filter are only
        those filters defined above the filter of interest.
        """
        
        if modified_filter_name is None:
            for f in self.filters:
                self._updateFilter(f)
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
            if not self.is_case_sensitive: # case-insensitive search
                filter_str = f.filter_value.upper()
                parent_set_str_list = [ 
                    getattr(self.get(obj,f.property_name),'__str__')().upper()
                    for obj in f.parentSet]
            else: # case-sensitive search
                filter_str = f.filter_value
                parent_set_str_list = [
                    getattr(self.get(obj,f.property_name),'__str__')()
                    for obj in f.parentSet]
            
            if f.NOT:
                f.matched_index_list = [i for (i,s) in enumerate(parent_set_str_list)
                                        if not fnmatchcase(s,filter_str)]
            else:
                f.matched_index_list = [i for (i,s) in enumerate(parent_set_str_list)
                                        if fnmatchcase(s,filter_str)]
            
        elif data_type == 'string_list':
            
            try:
                index = int(f.index)
            except:
                index = None
            
            list_of_str_list = [self.get(obj,f.property_name) 
                                for obj in f.parentSet]
            
            if index is not None:
                
                if not self.is_case_sensitive: # case-insensitive search
                    filter_str = f.filter_value.upper()
                    parent_set_str_list = [getattr(L[index],'__str__')().upper()
                                           for L in list_of_str_list]
                else: # case-sensitive search
                    filter_str = f.filter_value
                    parent_set_str_list = [getattr(L[index],'__str__')()
                                           for L in list_of_str_list]
                            
                if f.NOT:
                    f.matched_index_list = [i for (i,s) in enumerate(parent_set_str_list)
                                            if not fnmatchcase(s,filter_str)]
                else:
                    f.matched_index_list = [i for (i,s) in enumerate(parent_set_str_list)
                                            if fnmatchcase(s,filter_str)]
            
            else:
                
                matched_index_list = []

                if not self.is_case_sensitive: # case-insensitive search
                    filter_str = f.filter_value.upper()

                    for (i,L) in enumerate(list_of_str_list):
                        matched_list = [getattr(n,'__str__')().upper() for n in L
                                        if fnmatchcase(getattr(n,'__str__')().upper(), filter_str)]
                        if len(matched_list) >= 1:
                            matched_index_list.append(i)

                else: # case-sensitive search
                    filter_str = f.filter_value
                
                    for (i,L) in enumerate(list_of_str_list):
                        matched_list = [getattr(n,'__str__')() for n in L
                                        if fnmatchcase(getattr(n,'__str__')(), filter_str)]
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
        
        self.emit(SIGNAL("sigDataFiltered"),())
        
    
    
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
        
        # Get only matched elements from current parent set
        matchedElements = [self.currentParentSet[i] 
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
        f = self.filters[self.selected_filter_index]
        matched_obj_list = [f.parentSet[i] for i in f.matched_index_list]
        self.selectedObjects = [matched_obj_list[i] for i in selectedRowIndList]
                
        #matchedElemList = [
            #self.allElements[i] 
            #for (i,matched) in enumerate(self.combined_matched)
            #if matched] 
        #self.selectedObjects = [matchedElemList[i] 
                                 #for i in selectedRowIndList]
        
        self.emit(SIGNAL("readyForClosing"),())

                
        

########################################################################
class ElementSelectorView(QDialog, Ui_Dialog):
    """ """
    
    #----------------------------------------------------------------------
    def __init__(self, model, isModal, parentWindow = None):
        """Constructor"""
        
        QDialog.__init__(self, parent = parentWindow)
        
        self.setWindowFlags(QtCore.Qt.Window) # To add Maximize & Minimize buttons
        
        self.model = model
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
        
        self._initFilterView()
        self._initChoiceList()
        self._initMatchTable()
        
        self.model.updateFilters(None)                
        #self.update_tables()
        #self.update_matched_and_selected_numbers()
        #self.updateChoiceListComboBox()
        #self.updateChoiceListView()
    
    #----------------------------------------------------------------------
    def updateChoiceListComboBox(self):
        """"""
        
        choice_combobox_model = self.comboBox_choice_list.model()
        
        matched_model = self.tableWidget_matched.model()
        
        t = self.tableWidget_matched
        
        nCols = matched_model.columnCount()
        nRows = matched_model.rowCount()
        column_name_list = [t.horizontalHeaderItem(i).text()
                            for i in range(nCols)]
        for i in range(nCols):
            col_name = column_name_list[i]
            prop_name_and_full_name_and_data_type = \
                [(k,v[ENUM_ELEM_FULL_DESCRIP_NAME],v[ENUM_ELEM_DATA_TYPE])
                 for (k,v) in ELEM_PROPERTIES.iteritems()
                 if v[ENUM_ELEM_SHORT_DESCRIP_NAME] == col_name][0]
            prop_name, full_name, data_type = \
                prop_name_and_full_name_and_data_type
            self.choice_dict[prop_name] = \
                [matched_model.data(matched_model.index(j,i))
                 for j in range(nRows)]
            if data_type.endswith('_list'):
                # First need to convert the string representation of the list into a real list
                self.choice_dict[prop_name] = [eval(s) for s in self.choice_dict[prop_name]]
                # Then flatten the list of lists
                self.choice_dict[prop_name] = reduce(add, self.choice_dict[prop_name])
            self.choice_dict[prop_name] = sorted(list(set(self.choice_dict[prop_name])))
            
            choice_combobox_model.setData(
                choice_combobox_model.index(i,0),
                (full_name + ' [' + str(len(self.choice_dict[prop_name])) 
                 + ']')
            )
    
    #----------------------------------------------------------------------
    def updateChoiceListView(self):
        """"""
        
        choice_list_model = self.listView_choice_list.model()
        
        full_prop_name = self.comboBox_choice_list.currentText().split('[')[0].strip()
        prop_name = [k for (k,v) in ELEM_PROPERTIES.iteritems()
                     if v[ENUM_ELEM_FULL_DESCRIP_NAME]==full_prop_name][0]
        
        choice_list = self.choice_dict[prop_name]
        choice_list_model.setRowCount(len(choice_list))
        choice_list_model.setColumnCount(1)
        for (i,v) in enumerate(choice_list):
            choice_list_model.setData(choice_list_model.index(i,0), v)
        
                    
    
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
            value_list = sorted( list(set(value_list)) )
        else:
            value_list = sorted( list(set( reduce(add, value_list) )) )
        model_value = QStandardItemModel(len(value_list)+1,1,comboBox_value)
        current_value = comboBox_value.currentText()
        model_value.setData(model_value.index(0,0),current_value)
        for (i,v) in enumerate(value_list):
            model_value.setData(model_value.index(i+1,0),v)
        comboBox_value.setModel(model_value)
        comboBox_value.setSizeAdjustPolicy(QComboBox.AdjustToContents)
        
            
    #----------------------------------------------------------------------
    def _initChoiceList(self):
        """"""
        
        model_property = self.createPropertyListModel(
            self.comboBox_choice_list)
        self.comboBox_choice_list.setModel(model_property)
        self.comboBox_choice_list.setSizeAdjustPolicy(
            QComboBox.AdjustToContents)
        
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
        for (i,name) in enumerate(PROP_NAME_LIST):
            model_property.setData(model_property.index(i,0),
                                   ELEM_PROPERTIES[name][ENUM_ELEM_FULL_DESCRIP_NAME])
        
        #model_property = QStandardItemModel(
            #len(PROP_NAME_LIST)+len(self.model.allFields),1,
            #self.comboBox_simple_property)
        #for (i,fname) in enumerate(self.model.allFields):
            #model_property.setData(model_property.index(i+len(PROP_NAME_LIST),0),
                                   #'Field:'+fname)            
        
        return model_property
        
    #----------------------------------------------------------------------
    def _initFilterView(self):
        """"""
        
        self.tableWidget_filter.setRowCount(0)
        
        
        self.stackedWidget.setCurrentWidget(self.page_simple)
        
        filterModeStr = self.getFilterModeStr()
        if filterModeStr == 'simple':
            
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
            filter_operators = FILTER_OPERATOR_DICT[data_type]
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
            value_list = list(set([self.model.get(e,init_property_name)
                                   for e in self.model.currentParentSet]))
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
            pass
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
    def _initFilterTable(self):
        """
        Perform initial population and formating for tableWidget_filter
        """

        t = self.tableWidget_filter # shorthand notation

        ### Header population & properties
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
                              Qt.QTableWidgetItem(item_string))
                    
                    t.item(j,i).setFlags(Qt.Qt.ItemIsSelectable|
                                         Qt.Qt.ItemIsEditable|
                                         Qt.Qt.ItemIsDragEnabled|
                                         Qt.Qt.ItemIsEnabled) # Make it editable
                else:
                    t.setItem(j,i,Qt.QTableWidgetItem(''))
                    
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
        
        t.setColumnCount(len(self.model.col_name_list))
        t.setHorizontalHeaderLabels(self.model.col_name_list)
        
        t.horizontalHeader().setMovable(True)
                
        t.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        
        
    #----------------------------------------------------------------------
    def update_tables(self):
        """ """
        
        #"""###########################
        #Update tableWidget_choice_list
        #"""###########################
        
        #t = self.tableWidget_choice_list # shorthand notation
        
        #t.clearContents()
        
        #### Item population
        
        #nRows = max([len(choice_list) 
                     #for choice_list in self.model.choice_dict.values()])
        #t.setRowCount(nRows)
        #for (i, elem_prop) in enumerate(self.model.elem_property_list):
            #choice_list = self.model.choice_dict[elem_prop]
            #for (j, value) in enumerate(choice_list):
                #t.setItem(j,i,Qt.QTableWidgetItem(value.__str__()))
                #t.item(j,i).setFlags(Qt.Qt.ItemIsSelectable|
                                     #Qt.Qt.ItemIsDragEnabled|
                                     #Qt.Qt.ItemIsEnabled) # Make it non-editable
        
        #### Presentation formatting
        #t.resizeColumnsToContents()
        #for i in range(t.columnCount()):
            #if t.columnWidth(i) > self.max_auto_adjust_column_width:
                #t.setColumnWidth(i,self.max_auto_adjust_column_width)
                
        
        
        """####################################
        Populate and format tableWidget_matched
        """####################################
        
        f = self.model.filters[self.model.selected_filter_index]
        isinstance(f,Filter)
        
        t = self.tableWidget_matched # shorthand notation
        
        t.clearContents()
        
        ### Item population
        
        # Get only matched objects from all the objects
        matched_obj_list = [f.parentSet[i] for i in f.matched_index_list]
        nRows = len(matched_obj_list)
        t.setRowCount(nRows)
        nCols = len(PROP_NAME_LIST)
        t.setColumnCount(nCols)
        for (i,obj) in enumerate(matched_obj_list):
            for (j,prop_name) in enumerate(PROP_NAME_LIST):
                value = self.model.get(obj,prop_name)
                t.setItem( i, j, QTableWidgetItem(value.__str__()) )
                t.item(i,j).setFlags(QtCore.Qt.ItemIsSelectable |
                                     QtCore.Qt.ItemIsDragEnabled |
                                     QtCore.Qt.ItemIsEnabled) # Make it non-editable        
                
        
        ### Presentation formatting
        t.resizeColumnsToContents()
        for i in range(t.columnCount()):
            if t.columnWidth(i) > self.max_auto_adjust_column_width:
                t.setColumnWidth(i,self.max_auto_adjust_column_width)
        
        ### Reset selection to all available
        t.selectAll()
        
        self.emit(SIGNAL('readyForChoiceListUpdate'))


    #----------------------------------------------------------------------
    def update_matched_and_selected_numbers(self):
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
    def on_case_sensitive_state_change(self, checkBoxState):
        """ """
        
        #nRows = self.tableWidget_filter.rowCount()
        
        isCaseSensitive = checkBoxState
        
        ## Request re-doing all the filtering with the new case-sensitivity
        ## choice.
        #self.emit(SIGNAL("sigReadyForFiltering"), 
                  #range(nRows), isCaseSensitive)
    
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
                value_list = sorted( list(set( reduce(add, value_list) )) )
            else:
                index = int(f.index_displayed)
                value_list = sorted( list(set( [v[index] for v in value_list]) ) )
            
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
    
        qModelIndexList = self.tableWidget_matched.selectedIndexes()
        selectedRowIndList = list(set([q.row() for q in qModelIndexList]))
        
        return selectedRowIndList
        
    #----------------------------------------------------------------------
    def accept(self):
        """ """
        
        # Update currently selected elements before exiting the dialog
        selectedRowIndList = self.selectedRowIndList()
        
        self.emit(SIGNAL("updateFinalSelection"),
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
class ElementSelectorApp(QObject):
    """ """

    #----------------------------------------------------------------------
    def __init__(self, modal = True, parentWindow = None, 
                 object_type = 'element'):
        """Constructor"""
        
        QObject.__init__(self)
        
        self.modal = modal
        self.parentWindow = parentWindow
        
        self._initModel(object_type)
        self._initView()
        
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
                     
        
        
        ## Once the pre-processing of the filter specification is done,
        ## tell the data to perform the filtering based on the modified
        ## filter specification.
        #self.connect(self.view, SIGNAL("sigReadyForFiltering"),
                     #self.model.filterData)
        #self.connect(self.model, SIGNAL("sigReadyForFiltering"),
                     #self.model.filterData)

        # After new filtering is performed, update the view based on
        # the new filtered data.
        self.connect(self.model, SIGNAL("filtersUpdated"),
                     self.view.update_tables)
        self.connect(self.model, SIGNAL("filtersUpdated"),
                     self.view.update_matched_and_selected_numbers)
        
        self.connect(self.view.tableWidget_matched,
                     SIGNAL('itemSelectionChanged()'),
                     self.view.update_matched_and_selected_numbers)
        
        #self.connect(self.view.pushButton_add_row, SIGNAL("clicked()"),
                     #self.view.add_row_to_filter_table)
        #self.connect(self.view, SIGNAL("sigFilterRowAdded"),
                     #self.model.add_row_to_filter_spec)
                     
        self.connect(self.view.pushButton_add_row, SIGNAL('clicked()'),
                     self.view.add_row_to_filter_table)
        
        
        self.connect(self.view, SIGNAL("updateFinalSelection"),
                     self.model.update_selected_elements)
        self.connect(self.model, SIGNAL("readyForClosing"),
                     self.view.accept_and_close)
        
        
    #----------------------------------------------------------------------
    def _initModel(self, object_type):
        """ """
        
        self.model = ElementSelectorModel(object_type=object_type)
        
    #----------------------------------------------------------------------
    def _initView(self, out_type = TYPE_OBJECT):
        """ """
        
        self.view = ElementSelectorView(self.model, self.modal,
                                        parentWindow = self.parentWindow)
        

#----------------------------------------------------------------------
def make(modal = True, parentWindow = None, object_type = 'element',
         output_type = TYPE_OBJECT):
    """ """
    
    app = ElementSelectorApp(modal, parentWindow, object_type)
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
                  object_type='channel')
    
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
    
