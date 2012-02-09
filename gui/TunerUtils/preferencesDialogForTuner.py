import sys

USE_DEV_SRC = False
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
        
import PyQt4.Qt as Qt
import gui_icons

if __name__ == "__main__" :
    from ui_preferencesDialogForTuner import Ui_Dialog
    
    from tuner_file_manager import TunerFileManager
else:
    from .ui_preferencesDialogForTuner import Ui_Dialog

    from .tuner_file_manager import TunerFileManager
    

OUTPUT_TYPE_INDEX_LIST = 0
OUTPUT_TYPE_STRING_LIST = 1


########################################################################
class DialogData(Qt.QObject):
    """"""

    #----------------------------------------------------------------------
    def __init__(self, full_string_list, 
                 permanently_selected_string_list,
                 selected_string_list):
        """Constructor"""
        
        Qt.QObject.__init__(self)
        
        self.full_string_list = full_string_list[:]
        
        self.validInput = self._hasNoDuplicateStrings(
            self.full_string_list)
        if not self.validInput:
            return
        
        self.validInput = self._allStringsInList1FoundInList2(
            selected_string_list,
            self.full_string_list)
        if not self.validInput:
            return

        self.validInput = self._allStringsInList1FoundInList2(
            permanently_selected_string_list,
            selected_string_list)
        if not self.validInput:
            return

        self.permanently_selected_string_list = \
            permanently_selected_string_list
        
        self.strings_in_SelectedList = selected_string_list[:]
        
        self.strings_in_NotSelectedList = [
            s for s in self.full_string_list
            if s not in selected_string_list]
        
        self.output = []
    
    #----------------------------------------------------------------------
    def loadNewSelection(self, new_visible_col_name_list):
        """"""
        
        validInput  = self._hasNoDuplicateStrings(
            new_visible_col_name_list)
        if not validInput:
            error_str = 'Loaded newly selected string list was ' + \
                'not valid. Duplicate strings were found in the list.'
            Qt.QMessageBox.critical(None, 'ERROR', error_str)
            return
        
        validInput = self._allStringsInList1FoundInList2(
            new_visible_col_name_list,
            self.full_string_list)
        if not validInput:
            error_str = 'Loaded newly selected string list was ' + \
                'not valid. Some of the newly selected strings ' + \
                'were not found in the full list.'
            Qt.QMessageBox.critical(None, 'ERROR',error_str)
            return

        validInput = self._allStringsInList1FoundInList2(
            self.permanently_selected_string_list,
            new_visible_col_name_list)
        if not validInput:
            error_str = 'Loaded newly selected string list was ' + \
                'not valid. Some of the permanently selected strings ' + \
                'were not found in the newly selected string list.'
            Qt.QMessageBox.critical(None, 'ERROR', error_str)
            return
        
        self.strings_in_SelectedList = new_visible_col_name_list[:]
        
        self.strings_in_NotSelectedList = [
            s for s in self.full_string_list
            if s not in new_visible_col_name_list]
        
        self.emit(Qt.SIGNAL('readyForListsViewUpdate'))
        
    #----------------------------------------------------------------------
    def _hasNoDuplicateStrings(self, str_list):
        """"""
        
        str_set = set(str_list)
        
        if len(str_list) == len(str_set):
            return True
        else:
            return False
        
    #----------------------------------------------------------------------
    def _allStringsInList1FoundInList2(self, str_list_1,
                                       str_list_2):
        """"""
        
        stringsNotFound = [ s for s in str_list_1
                            if s not in str_list_2 ]
        
        if stringsNotFound:
            return False
        else:
            return True
        
        
    #----------------------------------------------------------------------
    def _moveSelectedItemsUp(self, strings_to_be_moved_up):
        """"""
        
        if not strings_to_be_moved_up:
            return
        
        SList = self.strings_in_SelectedList
        
        index_list = [SList.index(string) 
                      for string in strings_to_be_moved_up]
        
        if index_list[0] == 0: # Selected strings cannot be
            # moved further up.
            return
        
        
        temp_list = []
        selection_flags = []
        floating_str = None
        for i in range(len(SList)):
            if (i+1) not in index_list:
                if floating_str:
                    temp_list.append(floating_str)
                    floating_str = None
                else:
                    temp_list.append(SList[i])
                    
                selection_flags.append(False)
                
            else:
                if floating_str:
                    temp_list.append(SList[i+1])
                else:
                    floating_str = SList[i]
                    temp_list.append(SList[i+1])
                
                selection_flags.append(True)
                
        self.strings_in_SelectedList = temp_list

        highlighted_indices = [i for (i,TF) in 
                               enumerate(selection_flags)
                               if TF]
        
        update_only_SelectedList = True        
        self.emit(Qt.SIGNAL('readyForListsViewUpdate'),
                  highlighted_indices,
                  update_only_SelectedList)
        
    
    #----------------------------------------------------------------------
    def _moveSelectedItemsDown(self, strings_to_be_moved_down):
        """"""
        
        if not strings_to_be_moved_down:
            return
        
        rev_strings_to_be_moved_down = strings_to_be_moved_down[:]
        rev_strings_to_be_moved_down.reverse()
        
        SList = self.strings_in_SelectedList
        rev_SList = SList[:]
        rev_SList.reverse()
        
        index_list = [rev_SList.index(string) 
                      for string in rev_strings_to_be_moved_down]
        
        if index_list[0] == 0: # Selected strings
            # cannot be moved further down.
            return
        
        temp_list = []
        selection_flags = []
        floating_str = None
        for i in range(len(rev_SList)):
            if (i+1) not in index_list:
                if floating_str:
                    temp_list.append(floating_str)
                    floating_str = None
                else:
                    temp_list.append(rev_SList[i])
                    
                selection_flags.append(False)
            else:
                if floating_str:
                    temp_list.append(rev_SList[i+1])
                else:
                    floating_str = rev_SList[i]
                    temp_list.append(rev_SList[i+1])
                    
                selection_flags.append(True)
        
        temp_list.reverse()
        selection_flags.reverse()
        
        self.strings_in_SelectedList = temp_list
        
        highlighted_indices = [i for (i,TF) in 
                               enumerate(selection_flags)
                               if TF]
        
        update_only_SelectedList = True
        self.emit(Qt.SIGNAL('readyForListsViewUpdate'),
                  highlighted_indices,
                  update_only_SelectedList)
    
    #----------------------------------------------------------------------
    def _addToSelectedList(self, strings_to_be_added):
        """"""
        
        NList = self.strings_in_NotSelectedList
        SList = self.strings_in_SelectedList
        
        for string in strings_to_be_added:
            NList.remove(string)
            SList.append(string)
            
        self.emit(Qt.SIGNAL('readyForListsViewUpdate'))
    
    #----------------------------------------------------------------------
    def _removeFromSelectedList(self, strings_to_be_removed):
        """"""
        
        # Filter out permanently selected strings, if any,
        # from strings_to_be_removed
        valid_strings_to_be_removed = [
            s for s in strings_to_be_removed
            if s not in self.permanently_selected_string_list
            ]
        
        if len(valid_strings_to_be_removed) != \
           len(strings_to_be_removed):
            error_str = 'You are not allowed to hide columns ' \
                + str(self.permanently_selected_string_list) + '.'
            Qt.QMessageBox.critical(None, 'ERROR', error_str)
        
        NList = self.strings_in_NotSelectedList
        SList = self.strings_in_SelectedList
        
        for string in valid_strings_to_be_removed:
            SList.remove(string)
            NList.append(string)
            
        self.emit(Qt.SIGNAL('readyForListsViewUpdate'))
        
        
########################################################################
class DialogView(Qt.QDialog, Ui_Dialog):
    """"""

    #----------------------------------------------------------------------
    def __init__(self, data, modal, parentWindow, output_type):
        """Constructor"""
        
        Qt.QDialog.__init__(self, parent = parentWindow)
        
        self.data = data
            
        self.setupUi(self)
        
        self.setWindowFlags(Qt.Qt.Window) # To add Maximize & Minimize buttons
        
        self.setModal(modal)
        
        self.output_type = output_type
        
        self.listWidget_NotSelected.setSelectionMode(
            Qt.QAbstractItemView.ExtendedSelection)
        self.listWidget_Selected.setSelectionMode(
            Qt.QAbstractItemView.ExtendedSelection)
                
        self._addIconsToPushButtons()
        
        self._updateLists()
        
        
        self.connect(self.pushButton_right_arrow,
                     Qt.SIGNAL('clicked()'),
                     self._prepareForAddingToSelectedList)
        self.connect(self.pushButton_left_arrow,
                     Qt.SIGNAL('clicked()'),
                     self._prepareForRemovingFromSelectedList)
        self.connect(self.pushButton_up_arrow,
                     Qt.SIGNAL('clicked()'),
                     self._prepareForMovingItemsUp)
        self.connect(self.pushButton_down_arrow,
                     Qt.SIGNAL('clicked()'),
                     self._prepareForMovingItemsDown)
            
    #----------------------------------------------------------------------
    def _updateLists(self, *args):
        """"""
        
        if len(args) == 2:
            highlighted_indices = args[0]
            update_only_SelectedList = args[1]
        elif len(args) == 1:
            highlighted_indices = args[0]
            update_only_SelectedList = False
        else:
            highlighted_indices = []
            update_only_SelectedList = False
         
        SList = self.data.strings_in_SelectedList
        w = self.listWidget_Selected
        q_str_list = Qt.QStringList()
        for string in SList:
            q_str_list.append(string)
        w.clear()
        w.addItems(q_str_list)
        
        selectionModel = w.selectionModel()
        selectionModel.clearSelection()
        for index in highlighted_indices:
            selectionModel.select(
                w.indexFromItem(w.item(index)),
                Qt.QItemSelectionModel.Select )

        if update_only_SelectedList:
            return
        
        NList = self.data.strings_in_NotSelectedList
        w = self.listWidget_NotSelected
        q_str_list = Qt.QStringList()
        for string in NList:
            q_str_list.append(string)
        w.clear()
        w.addItems(q_str_list)

        selectionModel = w.selectionModel()
        selectionModel.clearSelection()
        for index in highlighted_indices:
            selectionModel.select(
                w.indexFromItem(w.item(index)),
                Qt.QItemSelectionModel.Select )
        
    #----------------------------------------------------------------------
    def _prepareForAddingToSelectedList(self):
        """"""
        
        strings_to_be_added = \
            self._getSelectedStrings_in_NotSelectedList()
        
        self.emit(Qt.SIGNAL('sigGotStringsToBeAdded'),
                  strings_to_be_added) 
    
    #----------------------------------------------------------------------
    def _prepareForRemovingFromSelectedList(self):
        """"""
        
        strings_to_be_removed = \
            self._getSelectedStrings_in_SelectedList()
        
        self.emit(Qt.SIGNAL('sigGotStringsToBeRemoved'),
                  strings_to_be_removed)
        
    #----------------------------------------------------------------------
    def _prepareForMovingItemsUp(self):
        """"""
        
        strings_to_be_moved_up = \
            self._getSelectedStrings_in_SelectedList()
        
        self.emit(Qt.SIGNAL('sigGotStringsToBeMovedUp'),
                  strings_to_be_moved_up)
    
    #----------------------------------------------------------------------
    def _prepareForMovingItemsDown(self):
        """"""
        
        strings_to_be_moved_down = \
            self._getSelectedStrings_in_SelectedList()
        
        self.emit(Qt.SIGNAL('sigGotStringsToBeMovedDown'),
                  strings_to_be_moved_down)
    
    
    #----------------------------------------------------------------------
    def _getSelectedStrings_in_NotSelectedList(self):
        """"""
        
        w = self.listWidget_NotSelected
        selected_item_list = w.selectedItems()
        
        return [str(i.text()) for i in selected_item_list]
        
    #----------------------------------------------------------------------
    def _getSelectedStrings_in_SelectedList(self):
        """"""
        
        w = self.listWidget_Selected
        selected_item_list = w.selectedItems()
        
        return [str(i.text()) for i in selected_item_list]
        
        
    #----------------------------------------------------------------------
    def _addIconsToPushButtons(self):
        """"""
        
        icon_width = int(self.pushButton_up_arrow.width()*0.8)
        icon_height = int(self.pushButton_up_arrow.height()*0.8)
        icon_size = Qt.QSize(icon_width,icon_height)
        #
        b = self.pushButton_up_arrow
        b.setIcon(Qt.QIcon(':/up_arrow.png'))
        b.setIconSize(icon_size)
        b.setText('')
        #
        b = self.pushButton_down_arrow
        b.setIcon(Qt.QIcon(':/down_arrow.png'))
        b.setIconSize(icon_size)
        b.setText('')
        #
        b = self.pushButton_right_arrow
        b.setIcon(Qt.QIcon(':/right_arrow.png'))
        b.setIconSize(icon_size)
        b.setText('')
        #
        b = self.pushButton_left_arrow
        b.setIcon(Qt.QIcon(':/left_arrow.png'))
        b.setIconSize(icon_size)
        b.setText('')
        
        
        
    #----------------------------------------------------------------------
    def accept(self):
        """"""
        
        checkedSetAsDefault = self.checkBox_setAsDefault.isChecked()
        
        checkedApplyToAllTabs = self.checkBox_applyToAllTabs.isChecked()
        
        if self.output_type == OUTPUT_TYPE_INDEX_LIST:
            selected_index_list = [
                self.data.full_string_list.index(string) 
                for string in self.data.strings_in_SelectedList]
            selected_list = selected_index_list
        elif self.output_type == OUTPUT_TYPE_STRING_LIST:
            selected_list = self.data.strings_in_SelectedList
            
        self.data.output = {
            'selected_list':selected_list,
            'checkedSetAsDefault':checkedSetAsDefault,
            'checkedApplyToAllTabs':checkedApplyToAllTabs
        }
        
        super(DialogView, self).accept() # will hide the dialog
        
        
    #----------------------------------------------------------------------
    def reject(self):
        """"""
        
        self.data.output = {}

        super(DialogView, self).reject() # will hide the dialog

    
########################################################################
class DialogApp(Qt.QObject):
    """"""

    #----------------------------------------------------------------------
    def __init__(self, full_string_list, 
                 permanently_selected_string_list,
                 selected_string_list,
                 modal, parentWindow, output_type):
        """Constructor"""
        
        super(DialogApp,self).__init__()
        
        self.modal = modal
        self.parentWindow = parentWindow
        self.output_type = output_type
        
        self._initData(full_string_list,
                       permanently_selected_string_list,
                       selected_string_list)
        
        if not self.data.validInput:
            return
        
        self._initView()
        
        self._initFileManager()
        
        
        self.connect(self.view,
                     Qt.SIGNAL('sigGotStringsToBeMovedUp'),
                     self.data._moveSelectedItemsUp)
        self.connect(self.view,
                     Qt.SIGNAL('sigGotStringsToBeMovedDown'),
                     self.data._moveSelectedItemsDown)

        self.connect(self.view,
                     Qt.SIGNAL('sigGotStringsToBeAdded'),
                     self.data._addToSelectedList)
        self.connect(self.view,
                     Qt.SIGNAL('sigGotStringsToBeRemoved'),
                     self.data._removeFromSelectedList)
        
        self.connect(self.data,
                     Qt.SIGNAL('readyForListsViewUpdate'),
                     self.view._updateLists)
        
        # Connections related to saving preferences to file
        self.connect(self.view.pushButton_saveToFile,
                     Qt.SIGNAL('clicked()'),
                     self._prepareForPrefFileSave)
        self.connect(self, Qt.SIGNAL('readyToSavePref'),
                     self.fileManager.savePreferencesFile)
        
        # Connections related to loading preferences from file
        self.connect(self.view.pushButton_loadFromFile,
                     Qt.SIGNAL('clicked()'),
                     self._prepareForPrefFileLoad)
        self.connect(self, Qt.SIGNAL('readyToLoadPref'),
                     self.fileManager.loadPreferencesFile)
        self.connect(self.fileManager,
                     Qt.SIGNAL('readyForUpdateOnPrefChange'),
                     self.data.loadNewSelection)

        
    #----------------------------------------------------------------------
    def _initData(self, full_string_list, 
                  permanently_selected_string_list,
                  selected_string_list):
        """"""
        
        self.data = DialogData(full_string_list,
                               permanently_selected_string_list,
                               selected_string_list)
        
    #----------------------------------------------------------------------
    def _initView(self):
        """"""
        
        self.view = DialogView(self.data, self.modal, 
                               self.parentWindow,
                               self.output_type)
    #----------------------------------------------------------------------
    def _initFileManager(self):
        """"""
        
        self.fileManager = TunerFileManager()
        
        
    #----------------------------------------------------------------------
    def _prepareForPrefFileSave(self):
        """"""
        
        visible_col_name_list = \
            self.data.strings_in_SelectedList
        
        self.emit(Qt.SIGNAL('readyToSavePref'),
                  visible_col_name_list)
        
    #----------------------------------------------------------------------
    def _prepareForPrefFileLoad(self):
        """"""
        
        self.emit(Qt.SIGNAL('readyToLoadPref'))
        
        
#----------------------------------------------------------------------
def make(full_string_list, **kwargs):
    """"""

    modal = kwargs.get('modal', True)
    parentWindow = kwargs.get('parentWindow', None)
    output_type = kwargs.get('output_type', OUTPUT_TYPE_STRING_LIST)
    permanently_selected_string_list = kwargs.get(
        'permanently_selected_string_list', [])
    selected_string_list = kwargs.get(
        'selected_string_list', 
        permanently_selected_string_list)
    
    app = DialogApp(full_string_list, 
                    permanently_selected_string_list,
                    selected_string_list, modal,
                    parentWindow, output_type)
    
    if not app.data.validInput:
        Qt.QMessageBox.critical(
            None, 'ERROR', \
            'Input string list(s) were invalid. ' + \
            'Either there were duplicate strings in the ' +
            'full list, or some of the permanently or ' +
            'initially selected strings were not found ' +
            'in the full list.')
        return []
        
    view = app.view
    view.exec_()
                
    return app.data.output

    
#----------------------------------------------------------------------
def main(args):
    """"""
    
    qapp = Qt.QApplication(args)
    
    full_string_list = ['item01','item02','item03',
                        'item04','item05','item06',
                        'item07','item08','item09']
    always_visible_string_list = ['item03']
    already_selected_string_list = ['item03', 'item05']
    
    result = make(full_string_list, 
                  permanently_selected_string_list =
                  always_visible_string_list,
                  selected_string_list = 
                  already_selected_string_list)
    
    print result

#----------------------------------------------------------------------    
if __name__ == "__main__" :
    main(sys.argv)
        
    