#! /usr/bin/env python

"""

GUI application for launching other GUI applications

:author: Yoshiteru Hidaka
:license:

This GUI application is a launcher program that allows users to start any
individual application they want to use with a single click on the launcher
panel. This launcher program can also allow sharing of the data between 
each application opened through this program, thereby eliminating
unnecessary duplicate import actions for some modules.

"""

import sys
import math
import os
import errno
import time
import posixpath
import subprocess
import cothread

# If Qt is to be used (for any GUI) then the cothread library needs to be informed,
# before any work is done with Qt. Without this line below, the GUI window will not
# show up and freeze the program.
# Note that for a dialog box to be modal, i.e., blocking the application
# execution until user input is given, you need to set the input
# argument "user_timer" to be True.

import PyQt4.Qt as Qt
from PyQt4.QtGui import QPushButton
from PyQt4.QtXml import QDomDocument

XML_ITEM_TAG_NAME = 'item'
MODEL_ITEM_PROPERTY_NAMES = ['path','linkedFile','args','useImport','singleton','itemType']
COLUMN_NAMES = ['Path','Linked File','Arguments','Use Import','Singleton','Item Type']
XML_ITEM_PROPERTY_NAMES = ['dispName','itemType','linkedFile','useImport','singleton','args']
DEFAULT_XML_ITEM = {'dispName':'', 'itemType':'page', 'linkedFile':'',
                    'useImport':False, 'singleton':False, 'args':''}
ITEM_PROPERTIES_DIALOG_OBJECTS = {'dispName':'lineEdit_dispName',
                                  'itemType':'comboBox_itemType',
                                  'linkedFile':'comboBox_linkedFile',
                                  'useImport':'comboBox_useImport',
                                  'singleton':'comboBox_singleton',
                                  'args':'lineEdit_args'}
ITEM_PROP_DLG_OBJ_ENABLED_FOR_PAGE = ['lineEdit_dispName', 'comboBox_itemType']
ITEM_PROP_DLG_OBJ_ENABLED_FOR_APP = ['lineEdit_dispName', 
                                     'comboBox_itemType',
                                     'comboBox_linkedFile',
                                     'comboBox_useImport',
                                     'comboBox_singleton',
                                     'lineEdit_args']


ITEM_COLOR_PAGE = Qt.Qt.black
ITEM_COLOR_APP = Qt.Qt.red

# Forward slash '/' will be used as a file path separator for both
# in Linux & Windows. Even if '/' is used in Windows, shutil and os functions still properly work.
# Qt.QDir.homePath() will return the home path string using '/' even on Windows.
# Therefore, '/' is being used consistently in this code.
# 
# By the way, the QFile document says "QFile expects the file separator to be '/' regardless of operating system.
# The use of other separators (e.g., '\') is not supported."
# However, on Windows, using '\' still works fine.
SEPARATOR = '/' # used as system file path separator as well as launcher page path separator
DOT_HLA_QFILEPATH = str(Qt.QDir.homePath()) + SEPARATOR + '.hla'
DEVELOPER_XML_FILENAME = 'launcher_hierarchy.xml'
USER_XML_FILENAME = 'user_launcher_hierarchy.xml'
USER_MODIFIABLE_ROOT_PATH = '/root/Users'

import gui_icons
from Qt4Designer_files.ui_launcher import Ui_MainWindow
from Qt4Designer_files.ui_launcher_item_properties import Ui_Dialog

import aphla

## TODO ##
# *) Highlight the search matching portion of texts in QTreeView and QListView
# *) Right-click on column name and allow add/remove visible properties
# *) Bypass XML tree construction, if XML file not changed. Load
# directory the tree model data for faster start-up.
# *) Implement page jumping with the path buttons hidden under
# the path line editbox.
# *) path auto completion & naviation from path line editbox
# *) Add <description> to XML
# *) Implement <singleton>
# *) Implement <args> for popen
# *) More thorough separate search window
# *) Implement "Visible Columns..." & "Arrange Items" actions
# *) Temporary user XML saving functionality whenever hierarchy is changed

## FIXIT
# *) Header not visible in main Tree View, if no item exists
# *) Ctrl+V & Ctrl+W shortcuts not always work


#----------------------------------------------------------------------
def almost_equal(x, y, absTol=1e-18, relTol=1e-7):
    """"""
    
    if (not absTol) and (not relTol):
        raise TypeError('Either absolute or relative tolerance must be specified.')
    tests = []
    if absTol:
        tests.append(absTol)
    if relTol:
        tests.append(relTol*abs(x))
    assert tests
    return abs(x - y) <= max(tests)


########################################################################
class SearchModel(Qt.QStandardItemModel):
    """
    """

    #----------------------------------------------------------------------
    def __init__(self, model, *args):
        """Constructor"""
        
        Qt.QStandardItemModel.__init__(self, *args)
        
        self.setHorizontalHeaderLabels(model.headerLabels)
        
        rootItem = LauncherModelItem('searchRoot')
        rootItem.ItemType = 'page'
        rootItem.path = SEPARATOR + rootItem.dispName
        rootItem.linkedFile = ''
        rootItem.args = ''
        rootItem.useImport = False
        rootItem.singleton = False
        rootItem.updateIconAndColor()
        self.setItem(0, rootItem)
        
            
    
########################################################################
class LauncherModel(Qt.QStandardItemModel):
    """
    """

    #----------------------------------------------------------------------
    def __init__(self, *args):
        """Constructor"""
        
        Qt.QStandardItemModel.__init__(self, *args)
    
        self.headerLabels = ['Name']
        self.headerLabels.extend(COLUMN_NAMES)
        self.setHorizontalHeaderLabels(self.headerLabels)
        self.setColumnCount(len(self.headerLabels))
        
        self.pathList = []
        self.pModelIndList = []
        self.linkedFileList = [] # Initial list population will occur when a
        # LauncherModelItemPropertiesDialog is created for the first time.
        
        ## First, parse developer XML file and construct a tree model
        developer_XML_Filepath = aphla.conf.filename(DEVELOPER_XML_FILENAME)
        developer_XML_Filepath.replace('\\','/') # On Windows, convert Windows path separator ('\\') to Linux path separator ('/')  
        #
        self.nRows = 0
        doc = self.open_XML_HierarchyFile(developer_XML_Filepath)
        self.construct_tree_model(doc.firstChild()) # Recursively search through 
        # the XML file to build the corresponding tree structure.

        ## Then parse user XML file and append the data to the tree model
        user_XML_Filepath = DOT_HLA_QFILEPATH + SEPARATOR + USER_XML_FILENAME
        user_XML_Filepath.replace('\\','/') # On Windows, convert Windows path separator ('\\') to Linux path separator ('/') 
        #
        doc = self.open_XML_HierarchyFile(user_XML_Filepath)
        rootItem = self.item(0,0)
        self.construct_tree_model(doc.firstChild(),
                                  parent_item=rootItem,
                                  child_index=rootItem.rowCount())
        
        # Set up completer for search
        self.completer = Qt.QCompleter()
        self.completer.setCompletionRole(Qt.Qt.DisplayRole)
        self.completer.setCompletionColumn = 0
        self.completer.setCaseSensitivity(False)
        self.completer.setCompletionMode(Qt.QCompleter.PopupCompletion)
        self.updateCompleterModel(SEPARATOR + 'root')
        
        
    #----------------------------------------------------------------------
    def construct_tree_model(self, dom, parent_item = None, 
                             child_index = None):
        """
        """
        
        info = self.getItemInfo(dom)
        
        if info:
            dispName = str(info['dispName'])
            
            item = LauncherModelItem(dispName)
            item.path = item.path + item.dispName
            item.itemType = info['itemType']
            item.linkedFile = info['linkedFile']
            if info['useImport'] == 'True':
                item.useImport = True
            else:
                item.useImport = False
            
            item.updateIconAndColor()
            
            for sibling_dom in info['sibling_DOMs']:
                item.appendRow(LauncherModelItem())

            if (parent_item is not None) and (child_index is not None):
                item.path = parent_item.path + item.path
                if item.path not in self.pathList:
                    self.pathList.append(item.path)
                else:
                    raise ValueError('Duplicate path found: '+item.path)
                parent_item.setChild(child_index, 0, item)
                for (ii,prop_name) in enumerate(MODEL_ITEM_PROPERTY_NAMES):
                    p = getattr(item,prop_name)
                    if not isinstance(p,str):
                        p = str(p)
                    parent_item.setChild(child_index, ii+1,Qt.QStandardItem(p))
                    
            else:
                self.setItem(self.nRows, item)
                self.nRows += 1
        
            parent_item = item
            for (child_index, sibling_dom) in \
                enumerate(info['sibling_DOMs']):
                self.construct_tree_model(sibling_dom, parent_item, 
                                          child_index)
        else:
            if not child_index:
                child_index = 0
                
            self.construct_tree_model(dom.nextSibling().firstChild(),
                                      parent_item, child_index)
            

    #----------------------------------------------------------------------
    def getItemInfo(self, dom):
        """
        """
        
        node = dom.firstChild()
        
        info = DEFAULT_XML_ITEM.copy()
        info['sibling_DOMs'] = []
        
        while not node.isNull():
            nodeName = str(node.nodeName())
            if nodeName in XML_ITEM_PROPERTY_NAMES:
                nodeValue = str(node.firstChild().nodeValue())
                info[nodeName] = nodeValue
            elif nodeName == XML_ITEM_TAG_NAME:
                info['sibling_DOMs'].append(node)
                
            node = node.nextSibling()
            
        if not info['dispName']:
            info = {}
                    
        return info
    
    #----------------------------------------------------------------------
    def constructXMLElementsFromModel(self, doc, parentModelItem, parentDOMElement):
        """"""
        
        childItemList = [parentModelItem.child(i,0) for i in
                         range(parentModelItem.rowCount())]
        for childItem in childItemList:
            childElement = doc.createElement(XML_ITEM_TAG_NAME)
            
            for (ii,prop_name) in enumerate(XML_ITEM_PROPERTY_NAMES):
                p = getattr(childItem,prop_name)
                if not isinstance(p,str):
                    p = str(p)
                elem = doc.createElement(prop_name)
                elemNodeText = doc.createTextNode(p)
                elem.appendChild(elemNodeText)
                childElement.appendChild(elem)
                if (prop_name == 'itemType') and (p == 'page'):
                    break

            if childItem.hasChildren():
                self.constructXMLElementsFromModel(doc, childItem, childElement)
            
            parentDOMElement.appendChild(childElement)
        
        
    #----------------------------------------------------------------------
    def writeToXMLFile(self, XML_Filepath, rootModelItem):
        """"""
                
        if rootModelItem.itemType == 'page':
            pass
        else:
            raise ValueError('Root model item to be written must be type "page".')
        
        doc = QDomDocument('')
            
        # Create XML file declaration header
        header = doc.createProcessingInstruction('xml', 'version="1.0" encoding="UTF-8"')
        doc.appendChild(header)
        
        # Create the XML root element (different from the XML element corresponding
        # to the root model item)
        xmlRootDOMElement = doc.createElement('hierarchy')
        
        # Create the XML element corresponding to the root model item
        modelRootDOMElement = doc.createElement(XML_ITEM_TAG_NAME)
        for (ii,prop_name) in enumerate(XML_ITEM_PROPERTY_NAMES):
            p = getattr(rootModelItem,prop_name)
            if not isinstance(p,str):
                p = str(p)
            elem = doc.createElement(prop_name)
            elemNodeText = doc.createTextNode(p)
            elem.appendChild(elemNodeText)
            modelRootDOMElement.appendChild(elem)
            if (prop_name == 'itemType') and (p == 'page'):
                break
            
        
        # Append the XML element corresponding to the root model item as a child of
        # the XML root element
        xmlRootDOMElement.appendChild(modelRootDOMElement)
        
        # Construct all the child elements recursively based on all the child model
        # items of the given root model item
        self.constructXMLElementsFromModel(doc, rootModelItem, modelRootDOMElement)
                        
        # Finally, append the XML root element to the DOM object
        doc.appendChild(xmlRootDOMElement)
        
        
        f = Qt.QFile(XML_Filepath)
        
        if not f.open(Qt.QIODevice.WriteOnly | Qt.QIODevice.Text):
            raise IOError('Failed to open ' + XML_Filepath + ' for writing.')
        
        stream = Qt.QTextStream(f)
        
        indent = 4
        stream << doc.toString(indent)
        
        f.close()
        
        
    
    #----------------------------------------------------------------------
    def open_XML_HierarchyFile(self, XML_Filepath):
        """
        """
        
            
        f = Qt.QFile(XML_Filepath)
        if not f.exists():
            # If the developer XML file cannot be located, stop here.
            XML_Filename = os.path.split(XML_Filepath)
            if DEVELOPER_XML_FILENAME == XML_Filename:
                raise OSError(XML_Filepath + ' does not exist.')
            
            # If the user XML file cannot be found, then create an empty one in
            # ".hla" directory under the user home directory.
            
            # This section of code create ".hla" directory under th user home directory,
            # if it does not already exist. This method assures no race condtion will happen
            # in the process of creating the new directory.
            try:
                os.makedirs(DOT_HLA_QFILEPATH)
            except OSError, e:
                if e.errno != errno.EEXIST:
                    raise OSError('Failed to create .hla directory')
            
            # Create an empty user XML file
            rootModelItem = LauncherModelItem('Users')
            self.writeToXMLFile(XML_Filepath, rootModelItem)
            # Make sure that the file has been successfully created.
            if not f.exists():
                raise IOError('Failed to create an empty User XML file')
            
        if not f.open(Qt.QIODevice.ReadOnly):
            raise IOError('Failed to open ' + XML_Filepath)

        doc = QDomDocument('')
        
        if not doc.setContent(f):
            f.close()
            raise IOError('Failed to parse ' + XML_Filepath)
        f.close()

        return doc
    
        
    
    #----------------------------------------------------------------------
    def updateCompleterModel(self, currentRootPath):
        """
        """    
        
        branchPathList = [p for p in self.pathList
                          if p.startswith(currentRootPath)]
        
        self.pathElementList = []
        for p in branchPathList:
            self.pathElementList.extend(p.split(SEPARATOR))
        self.pathElementList = list(set(self.pathElementList))
        self.pathElementList.pop(self.pathElementList.index(''))
        self.pathElementModel = Qt.QStandardItemModel(
            len(self.pathElementList), 1, self.completer)
        for (i, p) in enumerate(self.pathElementList):
            self.pathElementModel.setData(self.pathElementModel.index(i,0),
                                          p.strip())        
        
        self.completer.setModel(self.pathElementModel)
        
    #----------------------------------------------------------------------
    def updatePathLookupLists(self, parentItem = None):
        """"""
        
        if not parentItem:
            rootItem = self.item(0,0)
            self.pathList = [rootItem.path]
            self.pModelIndList = [Qt.QPersistentModelIndex(self.indexFromItem(rootItem))]
            parentItem = rootItem
        
        for i in range(parentItem.rowCount()):
            childItem = parentItem.child(i,0)
            if childItem.path not in self.pathList:
                self.pathList.append(childItem.path)
            else:
                raise ValueError('Duplicate path found: ' + childItem.path)
            self.pModelIndList.append(Qt.QPersistentModelIndex(self.indexFromItem(childItem)))
            
            self.updatePathLookupLists(childItem)
            
        
                
    #----------------------------------------------------------------------
    def pModelIndexFromPath(self, path):
        """"""
        
        index = self.pathList.index(path)
        
        return self.pModelIndList[index]
        
    
########################################################################
class LauncherModelItemPropertiesDialog(Qt.QDialog, Ui_Dialog):
    """"""

    #----------------------------------------------------------------------
    def __init__(self, model, selectedItem, *args):
        """Constructor"""
        
        Qt.QDialog.__init__(self, *args)
        
        self.setupUi(self)
        
        self.setWindowFlags(Qt.Qt.Window) # To add Maximize & Minimize buttons
        
        self.item = selectedItem
        
        # Update the list of linkedFile strings that already exist in the model
        itemList = [model.itemFromIndex(Qt.QModelIndex(pInd))
                    for pInd in model.pModelIndList]
        model.linkedFileList = list(set([item.linkedFile for item in itemList]))
        
        partitionedStrings = selectedItem.path.rpartition(SEPARATOR)
        self.parentPath = partitionedStrings[0]
        self.lineEdit_parentPath.setText(self.parentPath)
        
        # Create list of existing paths to be compared with a new path.
        self.existingPathList = model.pathList[:]
        # If this dialog is created for modifying an existing item, you must
        # remove the path of this item from the list.
        if selectedItem.path in self.existingPathList:
            self.existingPathList.remove(selectedItem.path)
        
        for (propName, objName) in ITEM_PROPERTIES_DIALOG_OBJECTS.items():
            obj = getattr(self, objName)
            if objName.startswith('lineEdit'):
                obj.setText(getattr(self.item,propName))
            elif objName.startswith('comboBox'):

                if propName == 'linkedFile':
                    obj.addItems(model.linkedFileList)
                    
                search_string = str(getattr(self.item,propName))
                matchedInd = obj.findText(search_string,
                                          Qt.Qt.MatchExactly)
                
                # If no match found, try case-insensitive search
                if matchedInd == -1:
                    matchedInd = obj.findText(search_string,
                                              Qt.Qt.MatchFixedString)
                
                if matchedInd != -1:
                    obj.setCurrentIndex(matchedInd)
                else:
                    msgBox = Qt.QMessageBox()
                    msgBox.setText( (
                        'No matching item found in ' + objName) )
                    msgBox.setInformativeText( str(sys.exc_info()) )
                    msgBox.setIcon(Qt.QMessageBox.Critical)
                    msgBox.exec_()
                    
        self.connect(self.comboBox_itemType,
                     Qt.SIGNAL('currentIndexChanged(const QString &)'),
                     self.updateEnableStates)
        
        self.isItemPropertiesModifiable = self.item.path.startswith(
            USER_MODIFIABLE_ROOT_PATH+SEPARATOR)
        # Adding SEPARATOR at the end of USER_MODIFIABLE_ROOT_PATH is essential
        # to exclude USER_MODIFIABLE_ROOT_PATH itself from modifiable item list
        
        self.updateEnableStates(self.item.itemType)
        
    #----------------------------------------------------------------------
    def updateEnableStates(self, itemTypeQString):
        """"""
        
        if not self.isItemPropertiesModifiable:
            enabledObjectNames = []
        else:
            if str(itemTypeQString).lower() == 'app':
                enabledObjectNames = ITEM_PROP_DLG_OBJ_ENABLED_FOR_APP
            else: # str(itemTypeQString).lower() == 'page'
                enabledObjectNames = ITEM_PROP_DLG_OBJ_ENABLED_FOR_PAGE
            
        for (propName, objName) in ITEM_PROPERTIES_DIALOG_OBJECTS.items():
            obj = getattr(self, objName)
            if objName in enabledObjectNames:
                obj.setEnabled(True)
            else:
                obj.setEnabled(False)
                
                # If the item whose properties to be shown is read-only,
                # then do not reset the values for disabled objects.
                # However, if the item is writable AND the display object
                # is disabled, then reset the value to the default value.
                if not self.isItemPropertiesModifiable:
                    continue
                
                # Reset values to default
                if objName.startswith('lineEdit'):
                    obj.setText(DEFAULT_XML_ITEM[propName])
                elif objName.startswith('comboBox'):
                    
                    search_string = str(DEFAULT_XML_ITEM[propName])
                    matchedInd = obj.findText(search_string,
                                              Qt.Qt.MatchExactly)
                    # If no match found, try case-insensitive search
                    if matchedInd == -1:
                        matchedInd = obj.findText(search_string,
                                                  Qt.Qt.MatchFixedString)
                    if matchedInd != -1:
                        obj.setCurrentIndex(matchedInd)
                    else:
                        msgBox = Qt.QMessageBox()
                        msgBox.setText( (
                            'No matching item found in ' + objName) )
                        msgBox.setInformativeText( str(sys.exc_info()) )
                        msgBox.setIcon(Qt.QMessageBox.Critical)
                        msgBox.exec_()        

                    
    #----------------------------------------------------------------------
    def accept(self):
        """"""
        
        dispName = str(self.lineEdit_dispName.text())
        if dispName == '':
            msgBox = Qt.QMessageBox()
            msgBox.setText( (
                'Empty item name not allowed.') )
            msgBox.setInformativeText( 'Please enter a non-empty string as an item name.')
            msgBox.setIcon(Qt.QMessageBox.Critical)
            msgBox.exec_()  
            return
        
        path = self.parentPath + SEPARATOR + dispName
        if path in self.existingPathList:
            msgBox = Qt.QMessageBox()
            msgBox.setText( (
                'Duplicate item name detected.') )
            msgBox.setInformativeText( 'The name ' + '"' + dispName + '"' +
                                       ' is already used in this page. Please use a different name.')
            msgBox.setIcon(Qt.QMessageBox.Critical)
            msgBox.exec_()  
            return
        else:
            self.lineEdit_dispName.setText(dispName)
            
        
        for (propName, objName) in ITEM_PROPERTIES_DIALOG_OBJECTS.items():
            obj = getattr(self, objName)
            if objName.startswith('lineEdit'):
                text = str(obj.text())
                setattr(self.item, propName, text)
                if propName == 'dispName':
                    self.item.setText(self.item.dispName)
                    
            elif objName.startswith('comboBox'):
                
                text = str(obj.currentText())
                if objName == 'comboBox_itemType':
                    text = text.lower()
                    setattr(self.item, propName, text)
                elif (objName == 'comboBox_useImport') or \
                     (objName == 'comboBox_singleton'):
                    if text == 'True':
                        setattr(self.item, propName, True)
                    elif text == 'False':
                        setattr(self.item, propName, False)
                    else:
                        raise ValueError('Boolean text representation expected, but received: ' + text)
                else:
                    setattr(self.item, propName, text)
                    
        super(LauncherModelItemPropertiesDialog, self).accept() # will hide the dialog
    
    #----------------------------------------------------------------------
    def reject(self):
        """"""
    
        super(LauncherModelItemPropertiesDialog, self).reject() # will hide the dialog
    
    
    
    

########################################################################
class LauncherModelItem(Qt.QStandardItem):
    """
    """

    #----------------------------------------------------------------------
    def __init__(self, *args):
        """Constructor"""
        
        Qt.QStandardItem.__init__(self, *args)
        
        if args:
            self.dispName = args[0]
        else:
            self.dispName = DEFAULT_XML_ITEM['dispName']
        self.itemType = DEFAULT_XML_ITEM['itemType'] # Either 'app' or 'page'
        self.path = SEPARATOR
        self.linkedFile = DEFAULT_XML_ITEM['linkedFile'] # Empty string for 'page'
        self.args = DEFAULT_XML_ITEM['args'] # Empty string for 'page'
        self.useImport = DEFAULT_XML_ITEM['useImport']
        self.singleton = DEFAULT_XML_ITEM['singleton']
               
        # Make the item NOT editable by default
        self.setFlags(self.flags() & ~Qt.Qt.ItemIsEditable)
        
        
    #----------------------------------------------------------------------
    def shallowCopy(self):
        """"""
        
        copiedItem = LauncherModelItem(self.dispName)
                        
        copiedItem.setFlags(self.flags())
        
        for p in MODEL_ITEM_PROPERTY_NAMES:
            setattr(copiedItem, p, getattr(self, p))
        
        copiedItem.updateIconAndColor()
        
        return copiedItem
    

    #----------------------------------------------------------------------
    def updateIconAndColor(self):
        """"""
        
        if self.itemType == 'app':
            if self.useImport:
                self.setIcon(Qt.QIcon(":/python.png"))
                self.setForeground(Qt.QBrush(ITEM_COLOR_APP))
            else:
                self.setIcon(Qt.QIcon(":/generic_app.png"))
                self.setForeground(Qt.QBrush(ITEM_COLOR_APP))                
        elif self.itemType == 'page':
            self.setIcon(Qt.QIcon(":/folder.png"))
            self.setForeground(Qt.QBrush(ITEM_COLOR_PAGE))
        else:
            pass
        

########################################################################
class CustomTreeView(Qt.QTreeView):
    """"""

    #----------------------------------------------------------------------
    def __init__(self, *args):
        """Constructor"""
        
        Qt.QTreeView.__init__(self, *args)
        
    #----------------------------------------------------------------------
    def focusInEvent(self, event):
        """"""
        
        super(CustomTreeView,self).focusInEvent(event)
        
        self.emit(Qt.SIGNAL('focusObtained()'))
        
    #----------------------------------------------------------------------
    def focusOutEvent(self, event):
        """"""
        
        super(CustomTreeView,self).focusOutEvent(event)
        
        self.emit(Qt.SIGNAL('focusLost()'))

    #----------------------------------------------------------------------
    def closeEditor(self, editor, hint):
        """
        overwriting QAbstractItemView virtual protected slot
        """
        
        super(Qt.QTreeView,self).closeEditor(editor,hint)
        
        self.emit(Qt.SIGNAL('closingItemRenameEditor'), editor.text())
        

    
########################################################################
class CustomListView(Qt.QListView):
    """"""

    #----------------------------------------------------------------------
    def __init__(self, *args):
        """Constructor"""
        
        Qt.QListView.__init__(self, *args)
        
    #----------------------------------------------------------------------
    def focusInEvent(self, event):
        """"""
        
        super(CustomListView,self).focusInEvent(event)
        
        self.emit(Qt.SIGNAL('focusObtained()'))
        
    #----------------------------------------------------------------------
    def focusOutEvent(self, event):
        """"""
        
        super(CustomListView,self).focusOutEvent(event)
        
        self.emit(Qt.SIGNAL('focusLost()'))
        
    #----------------------------------------------------------------------
    def closeEditor(self, editor, hint):
        """
        overwriting QAbstractItemView virtual protected slot
        """
        
        super(Qt.QListView,self).closeEditor(editor,hint)
        
        self.emit(Qt.SIGNAL('closingItemRenameEditor'), editor.text())
        
        

########################################################################
class MainPane(Qt.QWidget):
    """"""

    #----------------------------------------------------------------------
    def __init__(self, model, initRootModelIndex, stackedWidget, listView, treeView,
                 initListViewMode=CustomListView.IconMode):
        """Constructor"""
        
        Qt.QWidget.__init__(self)
        
        self.proxyModel = Qt.QSortFilterProxyModel() # Used for views on main
        # pane for which sorting is enabled
        self.proxyModel.setSourceModel(model)     
        
        initRootProxyModelIndex = self.proxyModel.mapFromSource(initRootModelIndex)
                        
        listView.setModel(self.proxyModel)
        listView.setRootIndex(initRootProxyModelIndex)
        listView.setViewMode(initListViewMode)
        listView.setContextMenuPolicy(Qt.Qt.CustomContextMenu)
        self.listView = listView

        treeView.setModel(self.proxyModel)
        treeView.setRootIndex(initRootProxyModelIndex)
        treeView.setItemsExpandable(True)
        treeView.setRootIsDecorated(True)
        treeView.setAllColumnsShowFocus(True)
        treeView.setHeaderHidden(False)
        treeView.setSortingEnabled(True)
        treeView.setContextMenuPolicy(Qt.Qt.CustomContextMenu)
        self.treeView = treeView       
        
        self.stackedWidget = stackedWidget
            
        self.searchModel = SearchModel(model)
        self.searchItemBeingEdited = None
                
        self.pathHistory = [Qt.QPersistentModelIndex(initRootModelIndex)]
        self.pathHistoryCurrentIndex = 0        
 
 
########################################################################
class LauncherView(Qt.QMainWindow, Ui_MainWindow):
    """
    """

    #----------------------------------------------------------------------
    def __init__(self, model, initRootPath):
        """Constructor"""
        
        Qt.QMainWindow.__init__(self)
        
        self._initActions()
        self._initMainToolbar()
        
        self.model = model # Used for TreeView on side pane for which sorting is disabled
        
        self.setupUi(self)
        
        self.setUpdatesEnabled(True)
        
        # Add the side pane tree view of class CustomTreeView
        self.treeViewSide = CustomTreeView(self.splitterPanes)
        self.treeViewSide.setObjectName('treeViewSide')
        self.splitterPanes.insertWidget(0,self.treeViewSide) # Move Side Pane to the left of Main Pane
        self.treeViewSide.setModel(self.model)
        self.treeViewSide.setItemsExpandable(True)
        self.treeViewSide.setRootIsDecorated(True)
        self.treeViewSide.setAllColumnsShowFocus(False)
        for c in range(self.model.columnCount())[1:]:
            self.treeViewSide.hideColumn(c)
        self.treeViewSide.setHeaderHidden(True)
        self.treeViewSide.setSortingEnabled(False)
        self.treeViewSide.setRootIndex(self.model.indexFromItem(
            self.model.item(0,0) ) )
        self.treeViewSide.setContextMenuPolicy(Qt.Qt.CustomContextMenu)
        self.treeViewSide.setSelectionMode(Qt.QAbstractItemView.SingleSelection)
        self.treeViewSide.setEditTriggers(Qt.QAbstractItemView.EditKeyPressed |
                                          Qt.QAbstractItemView.SelectedClicked)
        self.connect(self.treeViewSide, Qt.SIGNAL('focusObtained()'),
                     self.onSidePaneFocusIn)
        self.connect(self.treeViewSide, Qt.SIGNAL('focusLost()'),
                     self.onSidePaneFocusOut)
        self.connect(self.treeViewSide, Qt.SIGNAL('closingItemRenameEditor'),
                     self.onItemRenameEditorClosing)
        
        # Add the main pane list view & tree view
        self.listViewMain = CustomListView(self.pageListView)
        self.listViewMain.setObjectName('listViewMain')
        self.gridLayout.addWidget(self.listViewMain, 0, 0, 1, 1)
        #
        self.treeViewMain = CustomTreeView(self.pageTreeView)
        self.treeViewMain.setObjectName('treeViewMain')
        self.gridLayout_2.addWidget(self.treeViewMain, 0, 0, 1, 1)        
        
        self._initMenus()
        
        self.tabWidget = None
                
        
        self.listView_stack_index = 0
        self.treeView_stack_index = 1
        
        self.view_mode_index_icons = 0
        self.view_mode_index_list = 1
        self.view_mode_index_details = 2
                
        rootPModelIndex = self.model.pModelIndexFromPath(initRootPath)
        if not rootPModelIndex:
            raise IOError('Invalid initial root path provided: ' + initRootPath)
        rootModelIndex = Qt.QModelIndex(rootPModelIndex)
        self.mainPaneList = [MainPane(model,rootModelIndex,self.stackedWidgetMainPane,
                                      self.listViewMain,self.treeViewMain)]
        
        self.selectedViewType = CustomListView
        self.selectedListViewMode = CustomListView.IconMode
        self.selectedItemList = []
        self.selectedPersModelIndexList = []
        self.selectedSearchItemList = []
        
        self._initMainPane(len(self.mainPaneList)-1)
        
        self.lastFocusedView = None
        
        ## Create context menus
        self.contextMenu = Qt.QMenu()
        
        ## Initialize clipboard
        self.clipboard = []
        self.clipboardType = 'copy' # Either 'copy' or 'cut'
        
        ## Update path
        self.updatePath()
        
        self.lineEdit_search.setCompleter(self.model.completer)
                
        
        ## Make connections
        self.connect(self.treeViewSide.selectionModel(),
                     Qt.SIGNAL('selectionChanged(const QItemSelection &, const QItemSelection &)'),
                     self.onSelectionChange)        
        self.connect(self.treeViewSide,
                     Qt.SIGNAL('doubleClicked(const QModelIndex &)'),
                     self._callbackDoubleClickOnSidePaneItem)
        self.connect(self.treeViewSide,
                     Qt.SIGNAL('clicked(const QModelIndex &)'),
                     self._callbackClickOnSidePaneItem)
        self.connect(self.treeViewSide,
                     Qt.SIGNAL('customContextMenuRequested(const QPoint &)'),
                     self.openContextMenu)        
                
        
        self.connect(self.comboBox_view_mode,
                     Qt.SIGNAL('currentIndexChanged(const QString &)'),
                     self.updateMainPaneViewMode)
        
                     
        # Use "textChanged" signal to include programmatic changes of search text.
        # However, if this causes crashes (this tends to happen when you add
        # a breakpoint in the callback function), switch the signal back to "textEdited"
        # and try to debug the code.
        self.connect(self.lineEdit_search, Qt.SIGNAL('textChanged(const QString &)'),
                     self.onSearchTextChange)
        
        self.connect(self, Qt.SIGNAL('sigClearSelection'),
                     self.clearSelection)
    
        
        # Load QSettings
        self.loadSettings()
    
    #----------------------------------------------------------------------
    def closeEvent(self, event):
        """"""
        
        # Save the current hierarchy in the user-modifiable section to
        # the user hierarchy XML file.
        user_XML_Filepath = DOT_HLA_QFILEPATH + SEPARATOR + USER_XML_FILENAME
        user_XML_Filepath.replace('\\','/') # On Windows, convert Windows path separator ('\\') to Linux path separator ('/') 
        
        rootModelItem = self.model.itemFromIndex( Qt.QModelIndex(
            self.model.pModelIndexFromPath(USER_MODIFIABLE_ROOT_PATH) ) )
        self.model.writeToXMLFile(user_XML_Filepath, rootModelItem)
        
        # Save QSettings
        self.saveSettings()
        
        event.accept()
    
    #----------------------------------------------------------------------
    def saveSettings(self):
        """"""
        
        settings = Qt.QSettings('HLA','Launcher')
        
        settings.beginGroup('MainWindow')
        settings.setValue('position',self.geometry())
        settings.setValue('splitterPanes_sizes',self.splitterPanes.sizes())
        settings.endGroup()
        
        print 'Settings saved.'
        
    
    #----------------------------------------------------------------------
    def loadSettings(self):
        """"""
        
        settings = Qt.QSettings('HLA','Launcher')
                
        settings.beginGroup('MainWindow')
        rect = settings.value('position').toRect()
        if rect == Qt.QRect():
            rect = Qt.QRect(0,0,self.sizeHint().width(),self.sizeHint().height())
        self.setGeometry(rect)
        splitterPanes_sizes = settings.value('splitterPanes_sizes').toList()
        if splitterPanes_sizes == []:
            splitterPanes_sizes = [self.width()*(1./5), self.width()*(4./5)]
        else:
            self.splitterPanes.setSizes([splitterPanes_sizes[0].toInt()[0],
                                         splitterPanes_sizes[1].toInt()[0]])
        settings.endGroup()
        
        print 'Settings loaded.'
    
    
    
    #----------------------------------------------------------------------
    def onViewModeActionGroupTriggered(self, action):
        """"""
        
        m = self.getCurrentMainPane()
        s = m.stackedWidget;        
        
        if action == self.actionIconsView:
            if s.currentIndex() == self.treeView_stack_index:
                s.setCurrentIndex(self.listView_stack_index)
            m.listView.setViewMode(CustomListView.IconMode)
            index = self.comboBox_view_mode.findText('Icons View', Qt.Qt.MatchExactly)
        elif action == self.actionListView:
            if s.currentIndex() == self.treeView_stack_index:
                s.setCurrentIndex(self.listView_stack_index)
            m.listView.setViewMode(CustomListView.ListMode)
            index = self.comboBox_view_mode.findText('List View', Qt.Qt.MatchExactly)
        elif action == self.actionDetailsView:
            if s.currentIndex() == self.listView_stack_index:
                s.setCurrentIndex(self.treeView_stack_index)
            for c in range(self.model.columnCount()):
                m.treeView.resizeColumnToContents(c)
            index = self.comboBox_view_mode.findText('Details View', Qt.Qt.MatchExactly)
        else:
            raise ValueError('Unexpected view mode action')
        
        self.comboBox_view_mode.setCurrentIndex(index)
        

    #----------------------------------------------------------------------
    def onSidePaneFocusIn(self):
        """"""
        
        #print 'Side Pane Focus in'
        self.lastFocusedView = self.sender()
    
    #----------------------------------------------------------------------
    def onSidePaneFocusOut(self):
        """"""
        
        #print 'Side Pane Focus out'

    #----------------------------------------------------------------------
    def onMainPaneFocusIn(self):
        """"""
        
        #print 'Main Pane Focus in'
        self.lastFocusedView = self.sender()
    
    #----------------------------------------------------------------------
    def onMainPaneFocusOut(self):
        """"""
        
        #print 'Main Pane Focus out'
     
    #----------------------------------------------------------------------
    def onSearchTextChange(self, newSearchText):
        """"""
        
        m = self.getCurrentMainPane()
        currentPath = m.pathHistory[m.pathHistoryCurrentIndex]
        # If currentPath is a persistent model index of "searchModel",
        # then you need to convert currentPath into the corresponding
        # persistent model index of "self.model" first.
        if ( type(currentPath) == Qt.QPersistentModelIndex ) and \
           ( type(currentPath.model()) == SearchModel ):
            currentPath = self.convertSearchModelPModIndToModelPModInd(
                m.searchModel, currentPath)
            
        if not newSearchText:
            # If the latest history path is a search result,
            # then remove the path, since user decided not to do search
            # any more.
            if type(currentPath) != Qt.QPersistentModelIndex:
                m.pathHistory = m.pathHistory[:m.pathHistoryCurrentIndex]
                m.pathHistoryCurrentIndex = len(m.pathHistory)-1
                # History update must happen before calling "self.updateView"
                # function for the view update to work properly.            
                self.updateView(m)                
                
            return
        
        if type(currentPath) == Qt.QPersistentModelIndex:
            searchRootIndex = Qt.QModelIndex(currentPath)
            m.pathHistory = m.pathHistory[:(m.pathHistoryCurrentIndex+1)]
            m.pathHistory.append({'searchText':newSearchText,
                                  'searchRootIndex':currentPath})
            m.pathHistoryCurrentIndex = len(m.pathHistory)-1
        else:
            searchRootIndex = Qt.QModelIndex(currentPath['searchRootIndex'])
            m.pathHistory[m.pathHistoryCurrentIndex] = \
                {'searchText':newSearchText,
                 'searchRootIndex':currentPath['searchRootIndex']}
        
        
        # Method 1 (Which one is faster? Method 1 or Method 2?)
        columnIndex = 0
        matchedItems = self.model.findItems(
            newSearchText,
            (Qt.Qt.MatchContains | Qt.Qt.MatchRecursive),
            columnIndex)
        
        ## Method 2
        ## Note that the 1st argyment of "match" function is not
        ## for the model index of partial seaching under that branch.
        ## Rather, it is only used for specifying the search column.
        ## Removal of matched results outside of the selected
        ## branch must be done manually.
        #matchedModelIndices = self.model.match(
            #searchRootIndex, Qt.Qt.DisplayRole, newSearchText,
            #-1, (Qt.Qt.MatchContains | Qt.Qt.MatchRecursive) )
        #matchedItems = [self.model.itemFromIndex(i)
                        #for i in matchedModelIndices]
                        
        
        # Remove the matched items that are not under the branch
        # of the current root index
        searchRootItem = self.model.itemFromIndex(searchRootIndex)
        matchedItems = [i for i in matchedItems 
                        if i.path.startswith(searchRootItem.path)]
        
        # Update completer model
        self.model.updateCompleterModel(searchRootItem.path)
        
        
        dispNameList = [str(i.text()) for i in matchedItems]
        print dispNameList
        
        rootItem = LauncherModelItem()
        m.searchModel.setRowCount(0) # clear all existing rows
        m.searchModel.setItem(0, 0, rootItem)
        for (i, item) in enumerate(matchedItems):
            newItem = item.shallowCopy()
            # Property "sourcePersistentModelIndex" is added to this item
            # so that the persistent model index of searchModel can be
            # referenced back to the corresponding persistent model index of
            # self.model.
            newItem.sourcePersistentModelIndex = \
                Qt.QPersistentModelIndex(self.model.indexFromItem(item))
            ## TODO: Highlight the search matching portion of the dispaly text
            rootItem.setChild(i,0,newItem)
            for (j,prop_name) in enumerate(MODEL_ITEM_PROPERTY_NAMES):
                p = getattr(item,prop_name)
                if not isinstance(p,str):
                    p = str(p)
                rootItem.setChild(i,j+1,Qt.QStandardItem(p))
                
        self.updateView(m)
                
    #----------------------------------------------------------------------
    def validateSelectedItemList(self, rightClickedMainPane):
        """
        The only purpose of this function is to force non-selection
        for the following case.
        
        If you click on a page item that contains no items on the Side Pane,
        current selection will be the clicked page item. After this action,
        even if you click on the empty space on the Main Pane, the current
        selection will not become empty, because there is no item to change
        selection on the Mane Pane.
        
        In other words, if you click on a page item on the Side Pane, there is
        no way to unselect the item by clicking on the Main Pane.
        
        This situation is very inconvenient if you are trying to create a new
        item under that page through right-clicking. This situation is avoided
        if you go into the empty page by staying on the Main Pane.
        
        To work around this issue, the current root item of the Main Pane is
        checked against self.selectedItemList. If the root item is contained
        in the list, that means invalid.
        """
        
        if not self.selectedItemList:
            return
        
        m = rightClickedMainPane
        
        currentRootItem = self.itemFromIndex(m.listView.rootIndex())
        
        if currentRootItem.path in \
           [i.path for i in self.selectedItemList]:
            self.clearSelection()
        
    #----------------------------------------------------------------------
    def openContextMenu(self, qpoint):
        """"""
        
        print 'Opening context menu'
        
        self.updateMenuItems()
        
        sender = self.sender()
        
        globalClickPos = sender.mapToGlobal(qpoint)        
        
        m = self.getParentMainPane(sender)
        
        if m: # When right-clicked on main pane
                                
            self.contextMenu.exec_(globalClickPos)
            
            self.selectedViewType = type(sender)
            self.selectedListViewMode = m.listView.viewMode()            
            
        else: # When right-clicked on side pane

            if not self.selectedItemList:
                return
            
            self.contextMenu.exec_(globalClickPos)
            
            m = self.getCurrentMainPane()
            if m.stackedWidget.currentIndex() == self.listView_stack_index:
                self.selectedViewType = CustomListView
            else:
                self.selectedViewType = CustomTreeView
            self.selectedListViewMode = m.listView.viewMode()
        
    
    #----------------------------------------------------------------------
    def _initMainPaneTreeViewSettings(self, newTreeView):
        """"""
        
        newTreeView.setSelectionMode(Qt.QAbstractItemView.ExtendedSelection)
        newTreeView.setSelectionBehavior(Qt.QAbstractItemView.SelectRows)
        
        newTreeView.setDragDropMode(Qt.QAbstractItemView.NoDragDrop)

        newTreeView.setEditTriggers(Qt.QAbstractItemView.EditKeyPressed |
                                    Qt.QAbstractItemView.SelectedClicked)
                        
        self.connect(newTreeView.selectionModel(),
                     Qt.SIGNAL('selectionChanged(const QItemSelection &, const QItemSelection &)'),
                     self.onSelectionChange)         
        self.connect(newTreeView,
                     Qt.SIGNAL('customContextMenuRequested(const QPoint &)'),
                     self.openContextMenu)
        self.connect(newTreeView,
                     Qt.SIGNAL('doubleClicked(const QModelIndex &)'),
                     self._callbackDoubleClickOnMainPaneItem)
        self.connect(newTreeView,
                     Qt.SIGNAL('clicked(const QModelIndex &)'),
                     self._callbackClickOnMainPaneItem)  
        self.connect(newTreeView, Qt.SIGNAL('focusObtained()'),
                     self.onMainPaneFocusIn)
        self.connect(newTreeView, Qt.SIGNAL('focusLost()'),
                     self.onMainPaneFocusOut)
        self.connect(newTreeView, Qt.SIGNAL('closingItemRenameEditor'),
                     self.onItemRenameEditorClosing)
               
    
    #----------------------------------------------------------------------
    def _initMainPaneListViewSettings(self, newListView):
        """"""
        
        newListView.setSelectionMode(Qt.QAbstractItemView.ExtendedSelection)
        newListView.setSelectionBehavior(Qt.QAbstractItemView.SelectRows)                
        
        newListView.setResizeMode(CustomListView.Adjust)
        newListView.setWrapping(True)
        newListView.setDragDropMode(Qt.QAbstractItemView.NoDragDrop)
        
        newListView.setEditTriggers(Qt.QAbstractItemView.EditKeyPressed |
                                    Qt.QAbstractItemView.SelectedClicked)
                        
        
        self.connect(newListView.selectionModel(),
                     Qt.SIGNAL('selectionChanged(const QItemSelection &, const QItemSelection &)'),
                     self.onSelectionChange)        
        self.connect(newListView,
                     Qt.SIGNAL('customContextMenuRequested(const QPoint &)'),
                     self.openContextMenu)
        self.connect(newListView,
                     Qt.SIGNAL('doubleClicked(const QModelIndex &)'),
                     self._callbackDoubleClickOnMainPaneItem)
        self.connect(newListView,
                     Qt.SIGNAL('clicked(const QModelIndex &)'),
                     self._callbackClickOnMainPaneItem)
        self.connect(newListView, Qt.SIGNAL('focusObtained()'),
                     self.onMainPaneFocusIn)
        self.connect(newListView, Qt.SIGNAL('focusLost()'),
                     self.onMainPaneFocusOut)
        self.connect(newListView, Qt.SIGNAL('closingItemRenameEditor'),
                     self.onItemRenameEditorClosing)
    
    #----------------------------------------------------------------------
    def onItemRenameEditorClosing(self, editorText):
        """"""
        
        sourceItem = self.selectedItemList[0]
        parentItem = sourceItem.parent()
        originalSourceItemPath = sourceItem.path
                        
        # Check item name validity (i.e., checking whether dispName is an empty string
        # and whether there will be no duplicate path if the new dispName is accepted.
        dispName = str(editorText)
        if dispName == '':
            msgBox = Qt.QMessageBox()
            msgBox.setText( (
                'Empty item name not allowed.') )
            msgBox.setInformativeText( 'Please enter a non-empty string as an item name.')
            msgBox.setIcon(Qt.QMessageBox.Critical)
            msgBox.exec_()
            self.renameItem() # Re-open the editor
            return
        #
        path = parentItem.path + SEPARATOR + dispName
        existingPathList = self.model.pathList[:]
        if originalSourceItemPath in existingPathList:
            existingPathList.remove(originalSourceItemPath)
        if path in existingPathList:
            msgBox = Qt.QMessageBox()
            msgBox.setText( (
                'Duplicate item name detected.') )
            msgBox.setInformativeText( 'The name ' + '"' + dispName + '"' +
                                       ' is already used in this page. Please use a different name.')
            msgBox.setIcon(Qt.QMessageBox.Critical)
            msgBox.exec_()
            self.renameItem() # Re-open the editor
            return
            

        sourceItem.dispName = dispName
        sourceItem.setText(dispName)
        sourceItem.path = path
        pathColumnIndex = MODEL_ITEM_PROPERTY_NAMES.index('path')+1
        pathItem = parentItem.child(sourceItem.row(), pathColumnIndex)
        pathItem.setText(sourceItem.path)
        self.model.updatePathLookupLists() # Do not pass any argument in order to refresh entire path list
        self.model.updateCompleterModel(self.getCurrentRootPath())
        self.updatePath()
        
        if self.inSearchMode():
            searchItem = self.selectedSearchItemList[0]
             
            searchItem.dispName = sourceItem.dispName
            searchItem.setText(sourceItem.text())
            searchItem.path = sourceItem.path
            parentSearchItem = searchItem.parent()
            pathSearchItem = parentSearchItem.child(searchItem.row(), 
                                                    pathColumnIndex)
            pathSearchItem.setText(searchItem.path)            
    
    #----------------------------------------------------------------------
    def onSelectionChange(self, selected, deselected):
        """"""
                
        itemSelectionModel = self.sender()
        #print 'Old Selection Empty? ', deselected.isEmpty()
        #print 'New Selection Empty? ', selected.isEmpty() 
        #print itemSelectionModel.selectedIndexes()
        #print '# of selected indexes = ', len(itemSelectionModel.selectedIndexes())
        #print itemSelectionModel.selectedRows()
        #print '# of selected rows = ', len(itemSelectionModel.selectedRows())
                
        clickedOnSearchModeMainPane = False
        
        model = itemSelectionModel.model()
        if type(model) == Qt.QSortFilterProxyModel: # When selection change ocurred on a Main Pane
            m = self.getCurrentMainPane()
            sourceModelIndexList = [m.proxyModel.mapToSource(proxyModelIndex)
                                    for proxyModelIndex
                                    in itemSelectionModel.selectedRows()]
            sourceModel = model.sourceModel()
            if type(sourceModel) == SearchModel: # When selection change ocurred on a Main Pane in Search Mode
                clickedOnSearchModeMainPane = True
                searchModelItemList = [m.searchModel.itemFromIndex(i)
                                       for i in sourceModelIndexList]
                self.selectedPersModelIndexList = [i.sourcePersistentModelIndex
                                                   for i in searchModelItemList]
                self.selectedSearchItemList = searchModelItemList
            else: # When selection change ocurred on a Main Pane in Non-Search Mode
                pass

        else: # When selection change ocurred on a Side Pane
            sourceModelIndexList = itemSelectionModel.selectedRows()
            
        if not clickedOnSearchModeMainPane: # For selection change on a Mane Pane in Non-Search Mode & on a Side Pane
            if all([i.isValid() for i in sourceModelIndexList]):
                self.selectedPersModelIndexList = [Qt.QPersistentModelIndex(i)
                                                   for i in sourceModelIndexList]
            else:
                raise ValueError('Invalid model index detected.')
        
            self.selectedItemList = [self.model.itemFromIndex(i)
                                     for i in sourceModelIndexList]
        else: # For selection change on a Mane Pane in Search Mode
            self.selectedItemList = [self.model.itemFromIndex(Qt.QModelIndex(pModInd))
                                     for pModInd in self.selectedPersModelIndexList]

        if self.selectedItemList:
            print 'Selection changed to ' + self.selectedItemList[0].path
        else:
            print 'Selection changed to None'
            
            
    #----------------------------------------------------------------------
    def _initMainPane(self, main_pane_index):
        """"""
        
        main_pane = self.mainPaneList[main_pane_index]
        
        self._initMainPaneTreeViewSettings(main_pane.treeView)
        self._initMainPaneListViewSettings(main_pane.listView)
        
        
    #----------------------------------------------------------------------
    def onTabSelectionChange(self, new_current_page_index):
        """"""
        
        tab_page = self.tabWidget.widget(new_current_page_index)
        currentStackedWidget = tab_page.findChildren(Qt.QStackedWidget)[0]
        visibleViewIndex = currentStackedWidget.currentIndex()
        
        if visibleViewIndex == self.listView_stack_index:
            # When the visible view is a QListView, find the view mode of the QListView
            listView = currentStackedWidget.findChildren(CustomListView)[0]
            if listView.viewMode() == CustomListView.IconMode:
                self.comboBox_view_mode.setCurrentIndex(self.view_mode_index_icons)
            elif listView.viewMode() == CustomListView.ListMode:
                self.comboBox_view_mode.setCurrentIndex(self.view_mode_index_list)
            else:
                print 'unknown view mode'
            
        elif visibleViewIndex == self.treeView_stack_index:
            self.comboBox_view_mode.setCurrentIndex(self.view_mode_index_details)
        else:
            print 'invalid visible stack page index'
            
        self.updatePath()
    
    #----------------------------------------------------------------------
    def openPageOrApps(self):
        """"""
        
        selectionType = self.getSelectionType()
        
        if selectionType == 'NoSelection':
            raise ValueError('openPageOrApps function should not be called with selectionType = ' + selectionType)
        elif selectionType == 'SinglePageSelection':
            self._callbackDoubleClickOnMainPaneItem(None)
        elif selectionType == 'MultiplePageSelection':
            raise ValueError('openPageOrApps function should not be called with selectionType = ' + selectionType)
        elif (selectionType == 'SingleAppSelection') or \
             (selectionType == 'MultipleAppSelection'):
            sender = self.sender()
            for item in self.selectedItemList:
                if sender == self.actionOpenWithImport:
                    useImport = True
                elif sender == self.actionOpenWithPopen:
                    useImport = False
                elif sender == self.actionOpen:
                    useImport = item.useImport
                else:
                    raise ValueError('Unexpected sender')
                self.emit(Qt.SIGNAL('sigAppExecutionRequested'),
                          item.linkedFile, useImport, item.args)
        elif selectionType == 'MultipleAppAndPageSelection':
            raise ValueError('openPageOrApps function should not be called with selectionType = ' + selectionType)            
        else:
            raise ValueError('Unexpected selection type: ' + selectionType)
        
        
        
    #----------------------------------------------------------------------
    def openInNewTab(self):
        """"""
        
        if len(self.mainPaneList) == 1: # No tab has been created
            
            m = self.getCurrentMainPane()
            
            original_splitter_sizes = self.splitterPanes.sizes()
            
            self.tabWidget = Qt.QTabWidget(self.splitterPanes)
            self.tabWidget.setObjectName("tabWidget")
            self.tabWidget.setVisible(True)
            self.tabWidget.setTabsClosable(True)
            self.tabWidget.setMovable(True)
            
            # Move the current stacked widget to a tab
            new_tab = Qt.QWidget()
            m.stackedWidget.setParent(new_tab)
            currentHistoryItem = m.pathHistory[m.pathHistoryCurrentIndex]
            if type(currentHistoryItem) == dict:
                currentRootPersModInd = currentHistoryItem['searchRootIndex']
            else:
                currentRootPersModInd = currentHistoryItem
            currentRootItem = self.model.itemFromIndex(
                Qt.QModelIndex(currentRootPersModInd) )
            self.tabWidget.addTab(new_tab, currentRootItem.dispName)
            #
            tab_gridLayout = Qt.QGridLayout(new_tab)
            tab_gridLayout.addWidget(m.stackedWidget,0,0,1,1)                                     
            
            self.splitterPanes.setSizes(original_splitter_sizes)
            
            self.connect(self.tabWidget,
                         Qt.SIGNAL('tabCloseRequested(int)'),
                         self.closeTab);          
            self.connect(self.tabWidget, Qt.SIGNAL("currentChanged(int)"),
                         self.onTabSelectionChange)
            
            
        for selectedItem in self.selectedItemList:                
            new_tab = Qt.QWidget()
            new_stackedWidget = Qt.QStackedWidget(new_tab)
            #
            tab_gridLayout = Qt.QGridLayout(new_tab)
            tab_gridLayout.addWidget(new_stackedWidget,0,0,1,1)
            #
            new_page1 = Qt.QWidget()
            page1_gridLayout = Qt.QGridLayout(new_page1)
            page1_gridLayout.setContentsMargins(-1, 0, 0, 0)
            new_listView = CustomListView(new_page1)
            new_listView.setViewMode(self.selectedListViewMode)
            page1_gridLayout.addWidget(new_listView, 0, 0, 1, 1)
            new_stackedWidget.addWidget(new_page1)
            new_page2 = Qt.QWidget()
            page2_gridLayout = Qt.QGridLayout(new_page2)
            page2_gridLayout.setContentsMargins(-1, 0, 0, 0)
            new_treeView = CustomTreeView(new_page2)
            page2_gridLayout.addWidget(new_treeView, 0, 0, 1, 1)
            new_stackedWidget.addWidget(new_page2)
            #
            # Link the model data to the views
            initRootModelIndex = self.model.indexFromItem(selectedItem)
            self.mainPaneList.append(
                MainPane(self.model, initRootModelIndex, new_stackedWidget,
                         new_listView, new_treeView, self.selectedListViewMode) )
            self._initMainPane(len(self.mainPaneList)-1)
            #
            # Reset the view type of the newly created tab to the view type
            # of the previously visible tab
            if self.selectedViewType == CustomListView:
                new_stackedWidget.setCurrentIndex(self.listView_stack_index)
            elif self.selectedViewType == CustomTreeView:
                new_stackedWidget.setCurrentIndex(self.treeView_stack_index)
            #
            self.tabWidget.addTab(new_tab, selectedItem.dispName)
            self.tabWidget.setCurrentWidget(new_tab)
    
    #----------------------------------------------------------------------
    def openInNewWindow(self):
        """"""
        
        appLauncherFilepath = sys.modules[self.__module__].__file__
        appLauncherFilename = os.path.split(appLauncherFilepath)[1]
        if appLauncherFilename.endswith('.pyc'):
            appLauncherFilename = appLauncherFilename.replace('.pyc','')
        elif appLauncherFilename.endswith('.py'):
            appLauncherFilename = appLauncherFilename.replace('.py','')
        useImport = True
        
        for selectedItem in self.selectedItemList:
            args = selectedItem.path
            self.emit(Qt.SIGNAL('sigAppExecutionRequested'),
                      appLauncherFilename, useImport, args)
        
    #----------------------------------------------------------------------
    def disableTabView(self):
        """"""
        
        self.disconnect(self.tabWidget,
                        Qt.SIGNAL('tabCloseRequested(int)'),
                        self.closeTab);          
        self.disconnect(self.tabWidget, Qt.SIGNAL("currentChanged(int)"),
                        self.onTabSelectionChange)        

        m = self.mainPaneList[0]
            
        original_splitter_sizes = self.splitterPanes.sizes()
        
        m.stackedWidget.setParent(self.splitterPanes)
        
        self.tabWidget.hide()
        self.tabWidget.setParent(self.centralwidget)
        self.tabWidget.deleteLater()
        
        self.splitterPanes.setSizes(original_splitter_sizes)
        
        
            
        
    #----------------------------------------------------------------------
    def _initActions(self):
        """"""
        
        # Action for Back button
        self.actionGoBack = Qt.QAction(Qt.QIcon(":/left_arrow.png"),
                                       "Back", self);
        self.actionGoBack.setCheckable(False)
        self.actionGoBack.setEnabled(False)
        self.addAction(self.actionGoBack)
        self.connect(self.actionGoBack, Qt.SIGNAL("triggered()"),
                     self.goBack) 

        # Action for Forward button
        self.actionGoForward = Qt.QAction(Qt.QIcon(":/right_arrow.png"),
                                          "Forward", self);
        self.actionGoForward.setCheckable(False)
        self.actionGoForward.setEnabled(False)
        self.addAction(self.actionGoForward)
        self.connect(self.actionGoForward, Qt.SIGNAL("triggered()"),
                     self.goForward)         

        # Action for Up button
        self.actionGoUp = Qt.QAction(Qt.QIcon(":/up_arrow.png"),
                                     "Open Parent", self);
        self.actionGoUp.setCheckable(False)
        self.actionGoUp.setEnabled(False)
        self.addAction(self.actionGoUp)
        self.connect(self.actionGoUp, Qt.SIGNAL("triggered()"),
                     self.goUp)         
        
        
        self.actionOpenInNewTab = Qt.QAction(Qt.QIcon(),
                                             'Open in New Tab', self)
        self.connect(self.actionOpenInNewTab, Qt.SIGNAL('triggered()'),
                     self.openInNewTab)

        self.actionOpenInNewWindow = Qt.QAction(Qt.QIcon(),
                                                'Open in New Window', self)        
        self.connect(self.actionOpenInNewWindow, Qt.SIGNAL('triggered()'),
                     self.openInNewWindow)
        
        self.actionOpen = Qt.QAction(Qt.QIcon(), 'Open', self)
        self.connect(self.actionOpen, Qt.SIGNAL('triggered()'),
                     self.openPageOrApps)
        
        self.actionOpenWithImport = Qt.QAction(Qt.QIcon(), 'Open w/ import', self)
        self.connect(self.actionOpenWithImport, Qt.SIGNAL('triggered()'),
                     self.openPageOrApps)
        self.actionOpenWithPopen = Qt.QAction(Qt.QIcon(), 'Open w/ Popen', self)
        self.connect(self.actionOpenWithPopen, Qt.SIGNAL('triggered()'),
                     self.openPageOrApps)
        
        self.actionCut = Qt.QAction(Qt.QIcon(), 'Cut', self)
        self.actionCut.setShortcut(
            Qt.QKeySequence(Qt.Qt.ControlModifier + Qt.Qt.Key_X))
        self.connect(self.actionCut, Qt.SIGNAL('triggered()'),
                     self.cutItems)
        
        self.actionCopy = Qt.QAction(Qt.QIcon(), 'Copy', self)
        self.actionCopy.setShortcut(
            Qt.QKeySequence(Qt.Qt.ControlModifier + Qt.Qt.Key_C))
        self.connect(self.actionCopy, Qt.SIGNAL('triggered()'),
                     self.copyItems)
        
        self.actionPaste = Qt.QAction(Qt.QIcon(), 'Paste', self)
        self.actionPaste.setShortcut(
            Qt.QKeySequence(Qt.Qt.ControlModifier + Qt.Qt.Key_V))
        self.connect(self.actionPaste, Qt.SIGNAL('triggered()'),
                     self.pasteItems)


        self.actionRename = Qt.QAction(Qt.QIcon(), 'Rename', self)
        self.actionRename.setShortcut(Qt.Qt.Key_F2)
        self.connect(self.actionRename, Qt.SIGNAL('triggered()'),
                     self.renameItem)
        
        self.actionProperties = Qt.QAction(Qt.QIcon(), 'Properties', self)
        self.actionProperties.setShortcut(
            Qt.QKeySequence(Qt.Qt.AltModifier + Qt.Qt.Key_Return))
        self.connect(self.actionProperties, Qt.SIGNAL('triggered()'),
                     self.openPropertiesDialog)
        
        
        self.actionCreateNewPage = Qt.QAction(Qt.QIcon(), 'Create New Page Item', self)
        self.connect(self.actionCreateNewPage, Qt.SIGNAL('triggered()'),
                     self.openPropertiesDialog)
        
        self.actionCreateNewApp = Qt.QAction(Qt.QIcon(), 'Create New App Item', self)
        self.connect(self.actionCreateNewApp, Qt.SIGNAL('triggered()'),
                     self.openPropertiesDialog)
        
        # TODO
        self.actionArrangeItems = Qt.QAction(Qt.QIcon(), 'Arrange Items', self)
        # TODO
        self.actionVisibleColumns = Qt.QAction(Qt.QIcon(), 'Visible Columns...', self)
        #self.connect()
        
        self.actionDelete = Qt.QAction(Qt.QIcon(), 'Delete', self)
        self.actionDelete.setShortcut(Qt.Qt.Key_Delete)
        self.connect(self.actionDelete, Qt.SIGNAL('triggered()'),
                     self.deleteItems)
        
        self.actionCloseTabOrWindow = Qt.QAction(Qt.QIcon(), 'Close', self)
        self.actionCloseTabOrWindow.setShortcut(
            Qt.QKeySequence(Qt.Qt.ControlModifier + Qt.Qt.Key_W))
        self.connect(self.actionCloseTabOrWindow, Qt.SIGNAL('triggered()'),
                     self.closeTabOrWindow)
                     
        self.actionSelectAll = Qt.QAction(Qt.QIcon(), 'Select All', self)
        #self.actionSelectAll.setShortcut(
            #Qt.QKeySequence(Qt.Qt.ControlModifier + Qt.Qt.Key_A))
        #self.connect()
        
        self.actionToggleSidePaneVisibility = \
            Qt.QAction(Qt.QIcon(), 'Side Pane', self)
        self.actionToggleSidePaneVisibility.setShortcut(Qt.Qt.Key_F9)
        self.actionToggleSidePaneVisibility.setCheckable(True)
        self.actionToggleSidePaneVisibility.setChecked(True)
        self.connect(self.actionToggleSidePaneVisibility,
                     Qt.SIGNAL('triggered(bool)'),
                     self.toggleSidePaneVisibility)
        
        
        # Action Group for Main Pane View Mode
        self.actionGroupViewMode = Qt.QActionGroup(self)
        self.actionGroupViewMode.setExclusive(True)
        self.actionIconsView = Qt.QAction(Qt.QIcon(), 'Icons View',
                                          self.actionGroupViewMode)
        self.actionIconsView.setCheckable(True)
        self.actionIconsView.setShortcut(
            Qt.QKeySequence(Qt.Qt.ControlModifier + Qt.Qt.Key_1))
        self.actionListView = Qt.QAction(Qt.QIcon(), 'List View', 
                                         self.actionGroupViewMode)
        self.actionListView.setCheckable(True)
        self.actionListView.setShortcut(
            Qt.QKeySequence(Qt.Qt.ControlModifier + Qt.Qt.Key_2))
        self.actionDetailsView = Qt.QAction(Qt.QIcon(), 'Details View',
                                            self.actionGroupViewMode)
        self.actionDetailsView.setCheckable(True)
        self.actionDetailsView.setShortcut(
            Qt.QKeySequence(Qt.Qt.ControlModifier + Qt.Qt.Key_3))
        self.actionIconsView.setChecked(True) # Default selection for the view mode
        self.connect(self.actionGroupViewMode, Qt.SIGNAL('triggered(QAction *)'),
                     self.onViewModeActionGroupTriggered)
        
        
    #----------------------------------------------------------------------
    def _initMenus(self):
        """"""
        
        self.menuFile.setTitle('&File')
        self.menuEdit.setTitle('&Edit')
        self.menuView.setTitle('&View')
        self.menuGo.setTitle('&Go')
        self.menuHelp.setTitle('&Help')
                        
        self.connect(self.menuFile, Qt.SIGNAL('aboutToShow()'),
                     self.updateMenuItems)
        self.connect(self.menuEdit, Qt.SIGNAL('aboutToShow()'),
                     self.updateMenuItems)
        self.connect(self.menuView, Qt.SIGNAL('aboutToShow()'),
                     self.updateMenuItems)
        self.connect(self.menuGo, Qt.SIGNAL('aboutToShow()'),
                     self.updateMenuItems)
        self.connect(self.menuHelp, Qt.SIGNAL('aboutToShow()'),
                     self.updateMenuItems)        
    
    #----------------------------------------------------------------------
    def toggleSidePaneVisibility(self, TF):
        """"""
        
        if TF:
            self.treeViewSide.setVisible(True)
        else:
            self.treeViewSide.setVisible(False)
            
    
    #----------------------------------------------------------------------
    def openPropertiesDialog(self):
        """"""
        
        m = self.getCurrentMainPane()
        parentItem = self.itemFromIndex(m.listView.rootIndex())
        
        if self.sender() == self.actionCreateNewPage:
            selectedItem = LauncherModelItem()
            selectedItem.path = parentItem.path + SEPARATOR # Without adding SEPARATOR
            # at the end of parent item path, users will not be able to add a new item
            # right below USER_MODIFIABLE_ROOT_PATH.
            selectedItem.itemType = 'page'
            createNewItem = True
            selectedItem.setFlags(selectedItem.flags() | Qt.Qt.ItemIsEditable)
        elif self.sender() == self.actionCreateNewApp:
            selectedItem = LauncherModelItem()
            selectedItem.path = parentItem.path + SEPARATOR # Without adding SEPARATOR
            # at the end of parent item path, users will not be able to add a new item
            # right below USER_MODIFIABLE_ROOT_PATH.
            selectedItem.itemType = 'app'
            createNewItem = True
            selectedItem.setFlags(selectedItem.flags() | Qt.Qt.ItemIsEditable)
        elif self.sender() == self.actionProperties:
            if self.selectedItemList:
                selectedItem = self.selectedItemList[0]
            else:
                selectedItem = parentItem
                self.selectedItemList = [selectedItem]
            createNewItem = False
        else:
            raise ValueError('Unexpected sender: ' + self.sender().text())
            
            
            
        self.propertiesDialogView = \
            LauncherModelItemPropertiesDialog(self.model, selectedItem)
        self.propertiesDialogView.exec_()
        
        if self.propertiesDialogView.result() == Qt.QDialog.Accepted:
            if not createNewItem:
                parentItem = selectedItem.parent()
                selectedItem.path = parentItem.path + SEPARATOR + selectedItem.dispName
                self.updateRow(selectedItem)
                if self.inSearchMode():
                    searchItem = self.selectedSearchItemList[0]
                    searchItem.dispName = selectedItem.dispName
                    searchItem.setText(selectedItem.text())
                    searchItem.path = selectedItem.path
                    
                    parentSearchItem = searchItem.parent()
                    row = searchItem.row()
                    for (ii,propName) in enumerate(MODEL_ITEM_PROPERTY_NAMES):
                        p = getattr(searchItem, propName)
                        
                        if not isinstance(p,str):
                            p = str(p)
                        
                        parentSearchItem.setChild(row, ii+1, Qt.QStandardItem(p))
                    
                    self.model.updateCompleterModel(self.getCurrentRootPath())
                    
            else:
                selectedItem.setText(selectedItem.dispName)
                selectedItem.path = parentItem.path + SEPARATOR + selectedItem.dispName
                selectedItem.updateIconAndColor()
                
                parentItem.appendRow(selectedItem)
                row = selectedItem.row()

                for (ii,propName) in enumerate(MODEL_ITEM_PROPERTY_NAMES):
        
                    p = getattr(selectedItem, propName)
                
                    if not isinstance(p,str):
                        p = str(p)
                    
                    parentItem.setChild(row, ii+1, Qt.QStandardItem(p))
                
                  
                self.model.updatePathLookupLists() # Do not pass any argument in order to refresh entire path list
            
            self.updatePath()
            
    #----------------------------------------------------------------------
    def updateRow(self, updated1stColumnItem):
        """"""
        
        updated1stColumnItem.updateIconAndColor()
        
        parentItem = updated1stColumnItem.parent()
        row = updated1stColumnItem.row()
    
        for (ii,propName) in enumerate(MODEL_ITEM_PROPERTY_NAMES):

            p = getattr(updated1stColumnItem, propName)
        
            if not isinstance(p,str):
                p = str(p)
            
            parentItem.child(row,ii+1).setText(p)   
        
        self.model.updatePathLookupLists() # Do not pass any argument in order to refresh entire path list
        
    #----------------------------------------------------------------------
    def deleteItems(self):
        """"""
        
        selectedDeletableItems = [item for item in self.selectedItemList
                                  if item.isEditable()]
        
        if not selectedDeletableItems:
            msgBox = Qt.QMessageBox()
            msgBox.setText( (
                'All selected items cannot be deleted. You do not have write permission.') )
            msgBox.setInformativeText( str(sys.exc_info()) )
            msgBox.setIcon(Qt.QMessageBox.Critical)
            msgBox.exec_()            
            return
        
        msgBox = Qt.QMessageBox()
        msgBox.addButton(Qt.QMessageBox.Yes)
        msgBox.addButton(Qt.QMessageBox.Cancel)
        msgBox.setDefaultButton(Qt.QMessageBox.Cancel)
        msgBox.setEscapeButton(Qt.QMessageBox.Cancel)
        msgBox.setText( 'Delete selected items"?' )
        infoText = ''
        for item in selectedDeletableItems:
            infoText += item.path + '\n'
        msgBox.setInformativeText(infoText)
        msgBox.setIcon(Qt.QMessageBox.Question)
        msgBox.setWindowTitle('Delete')
        choice = msgBox.exec_()
        if choice == Qt.QMessageBox.Cancel:
            return
        
        for item in selectedDeletableItems:
            self.model.removeRow(item.row(),
                                 item.parent().index())
                    
        self.model.updatePathLookupLists() # Do not pass any argument in order to refresh entire path list
        self.removeDeletedItemsFromHistory()
        self.updatePath()
        
        if self.inSearchMode():
            self.onSearchTextChange(self.lineEdit_search.text())

    #----------------------------------------------------------------------
    def removeDeletedItemsFromHistory(self):
        """
        If the model structure is changed in any way, then first the list of all
        the valid path must be reconstructed. And then also you need to check the
        history. If an item has been removed, and the past history contains the item,
        it must be removed so that the code does not crash when going back to
        the non-existent item. This function performs the 2nd task.
        """
        
        for m in self.mainPaneList:
            indexesToBeRemovedFrom_History = []
            for (index,p) in enumerate(m.pathHistory):
                if type(p) == Qt.QPersistentModelIndex:
                    pass
                elif type(p) == dict:
                    p = p['searchRootIndex']
                else:
                    raise TypeError('Unexpected history item type: ' + type(p))
                
                if p not in self.model.pModelIndList:
                    indexesToBeRemovedFrom_History.append(index)
        
            indexesToBeRemovedFrom_History.reverse()
            for index in indexesToBeRemovedFrom_History:
                m.pathHistory.pop(index)
                
            # You also need to re-adjust the current index
            m.pathHistoryCurrentIndex -= len(indexesToBeRemovedFrom_History)
            if m.pathHistoryCurrentIndex < 0:
                raise ValueError('After removing deleted items from path history, current history index has become negative.')
        
        
    #----------------------------------------------------------------------
    def copyItems(self):
        """"""
    
        self.clipboard = self.selectedItemList
        self.clipboardType = 'copy'
        
    #----------------------------------------------------------------------
    def cutItems(self):
        """"""
        
        isCuttable = [item.path.startswith(USER_MODIFIABLE_ROOT_PATH+SEPARATOR)
                      for item in self.selectedItemList]
        if all(isCuttable):
            self.clipboard = self.selectedItemList
            self.clipboardType = 'cut'
        else:
            raise ValueError('Non-modifiable items have been allowed to be cut.')
    
    #----------------------------------------------------------------------
    def pasteItems(self):
        """"""
        
        # Check destination is pastable, i.e., is a writeable page
        m = self.getCurrentMainPane()
        currentRootItem = self.itemFromIndex(m.listView.rootIndex())
        if not currentRootItem.path.startswith(USER_MODIFIABLE_ROOT_PATH):
            raise ValueError('Paste option was available at non-writeable page.')
        
        replaceAll = False
        indexListToBeRemovedFromClipboard = []
        for (clipIndex, item) in enumerate(self.clipboard):

            if item.path in currentRootItem.path:
                msgBox = Qt.QMessageBox()
                msgBox.setText( (
                    'You cannot paste a parent item into a sub-item.') )
                msgBox.setIcon(Qt.QMessageBox.Critical)
                msgBox.exec_()
                self.renameItem() # Re-open the editor
                return
                
            rowIndex = currentRootItem.rowCount()
            parentPath = item.parent().path
            pastedItem = item.shallowCopy()
            pastedItem.setEditable(True)
            newPath = currentRootItem.path + SEPARATOR + pastedItem.dispName
            if newPath == item.path: # When source item path and target item path are exactly
                # the same, rename the target item dispName with "(copy)" appended.
                newName = pastedItem.dispName + ' (copy)'
                newPath = currentRootItem.path + SEPARATOR + newName
                copyCounter = 1
                while newPath in self.model.pathList:
                    copyCounter += 1
                    newName = pastedItem.dispName + ' (copy' + str(copyCounter) + ')'
                    newPath = currentRootItem.path + SEPARATOR + newName
                pastedItem.dispName = newName
                pastedItem.setText(pastedItem.dispName)
                
            elif newPath in self.model.pathList: # When source item dispName conflicts with
                # an existing item in the target path, ask the user whether to overwrite or not.
                if not replaceAll:
                    msgBox = Qt.QMessageBox()
                    msgBox.addButton(Qt.QMessageBox.YesToAll)
                    msgBox.addButton(Qt.QMessageBox.Yes)
                    msgBox.addButton(Qt.QMessageBox.No)
                    msgBox.addButton(Qt.QMessageBox.NoToAll)
                    msgBox.setDefaultButton(Qt.QMessageBox.No)
                    msgBox.setEscapeButton(Qt.QMessageBox.No)
                    msgBox.setText( (
                        'Replace item "' + pastedItem.dispName + '"?') )
                    msgBox.setInformativeText(
                        'An item with the same name already exists in "' + parentPath +
                        '". Replacing it will overwrite the item.')
                    msgBox.setIcon(Qt.QMessageBox.Question)
                    msgBox.setWindowTitle('Item Conflict')
                    choice = msgBox.exec_()
                else:
                    choice = Qt.QMessageBox.Yes
                
                if (choice == Qt.QMessageBox.Yes) or \
                   (choice == Qt.QMessageBox.YesToAll):
                    if choice == Qt.QMessageBox.YesToAll:
                        replaceAll = True
                    # Remove the conflicting item
                    persModIndToBeRemoved = self.model.pModelIndexFromPath(newPath)
                    itemToBeRemoved = self.itemFromIndex(
                        Qt.QModelIndex(persModIndToBeRemoved))
                    self.model.pathList.remove(newPath)
                    removeSucess = self.model.removeRow(
                        itemToBeRemoved.row(),
                        itemToBeRemoved.parent().index())
                    if removeSucess:
                        rowIndex -= 1
                        self.model.updatePathLookupLists() # Do not pass any argument in order to refresh entire path list
                    else:
                        raise ValueError('Item removal failed.')
                elif choice == Qt.QMessageBox.No:
                    continue
                elif choice == Qt.QMessageBox.NoToAll:
                    break
                else:
                    raise ValueError('Unexpected selection')
            pastedItem.path = newPath
            self.model.pathList.append(pastedItem.path)
            currentRootItem.setChild(rowIndex, 0, pastedItem)
            for (i,prop_name) in enumerate(MODEL_ITEM_PROPERTY_NAMES):
                p = getattr(pastedItem,prop_name)
                if not isinstance(p,str):
                    p = str(p)
                currentRootItem.setChild(rowIndex,i+1,Qt.QStandardItem(p))
                
            # Recursively paste sub-items, if exist
            self.pasteSubItems(item, pastedItem)
        
            # Remove the pasted item from source, if the item was "cut"
            if self.clipboardType == 'cut':
                if not item.isEditable():
                    raise ValueError('Non-cuttable item somehow managed to be about to be removed.')
                else:
                    self.model.pathList.remove(item.path)
                    self.model.removeRow(item.row(),
                                         item.parent().index())
                    self.model.updatePathLookupLists() # Do not pass any argument in order to refresh entire path list
                    
                    # Flag the index of clipboard item to be removed due to "cut"
                    indexListToBeRemovedFromClipboard.append(clipIndex)
        
        # Remove cut items in clipboard
        indexListToBeRemovedFromClipboard.reverse() # Need to reverse so that each item to be removed
        # can be popped from the end without indexing problem
        for i in indexListToBeRemovedFromClipboard:
            self.clipboard.pop(i)
        
        self.model.updatePathLookupLists() # Do not pass any argument in order to refresh entire path list
        self.updatePath()
        
    #----------------------------------------------------------------------
    def pasteSubItems(self, sourceParentItem, targetParentItem):
        """"""
    
        if not sourceParentItem.hasChildren():
            return
        else:
            for r in range(sourceParentItem.rowCount()):
                childItem = sourceParentItem.child(r)
            
                pastedChildItem = childItem.shallowCopy()
                pastedChildItem.setEditable(True)
                newPath = targetParentItem.path + SEPARATOR + pastedChildItem.dispName
                pastedChildItem.path = newPath
                self.model.pathList.append(pastedChildItem.path)
                targetParentItem.setChild(r, 0, pastedChildItem)
                for (i,propName) in enumerate(MODEL_ITEM_PROPERTY_NAMES):
                    p = getattr(pastedChildItem,propName)
                    if not isinstance(p,str):
                        p = str(p)
                    targetParentItem.setChild(r,i+1,Qt.QStandardItem(p))   
            
                self.pasteSubItems(childItem, pastedChildItem)
            
            
        
    
    
    #----------------------------------------------------------------------
    def renameItem(self):
        """"""

        if not self.lastFocusedView:
            return
        
        if not self.selectedItemList:
            return
        
        if len(self.selectedItemList) > 1:
            pass # Number of selected items for renaming must be exactly 1.
        else:
            selectedModelIndex = self.lastFocusedView.currentIndex()
            self.lastFocusedView.edit(selectedModelIndex)
        
        
        
    #----------------------------------------------------------------------
    def _initMainToolbar(self):
        """"""
        
        # Back button
        backToolbar = self.addToolBar("Back")
        backToolbar.setObjectName("toolbar_back")
        backToolbar.setFloatable(False)
        backToolbar.setMovable(False)
        backToolbar.addAction(self.actionGoBack)
        
        # Forward button
        forwardToolbar = self.addToolBar("Forward")
        forwardToolbar.setObjectName("toolbar_forward")
        forwardToolbar.setFloatable(False)
        forwardToolbar.setMovable(False)
        forwardToolbar.addAction(self.actionGoForward)        
        
        # Up button
        upToolbar = self.addToolBar("Up")
        upToolbar.setObjectName("toolbar_up")
        upToolbar.setFloatable(False)
        upToolbar.setMovable(False)        
        upToolbar.addAction(self.actionGoUp)
        
        # View Mode combo box
        viewModeToolbar = self.addToolBar("View Mode")
        viewModeToolbar.setObjectName("toolbar_view_mode")
        viewModeToolbar.setFloatable(False)
        viewModeToolbar.setMovable(False)
        viewModeComboBox = Qt.QComboBox(viewModeToolbar)
        viewModeComboBox.setObjectName("comboBox_view_mode")
        viewModeComboBox.addItem("Icons View")
        viewModeComboBox.addItem("List View")
        viewModeComboBox.addItem("Details View")
        viewModeComboBox.setMinimumHeight(viewModeToolbar.height()*1.2)
        viewModeComboBox.adjustSize()
        viewModeToolbar.setMinimumWidth(viewModeComboBox.width())
        viewModeToolbar.adjustSize()
        self.comboBox_view_mode = viewModeComboBox

    #----------------------------------------------------------------------
    def closeTabOrWindow(self):
        """"""

        if self.tabWidget:
            self.closeTab(self.tabWidget.currentIndex())
        else:
            self.close()
           
    
    #----------------------------------------------------------------------
    def closeTab(self, tab_index):
        """ """
        
        w = self.tabWidget.widget(tab_index)
        
        w.deleteLater()
        
        self.tabWidget.removeTab(tab_index);

        # Remove MainPane from self.mainPaneList
        stackedWidget = w.findChild(Qt.QStackedWidget)
        self.mainPaneList.remove( self.getParentMainPane(stackedWidget) )

        # Disable tab view since there is only 1 tab now
        if self.tabWidget.count() == 1:
            self.disableTabView()
        
    
    
    #----------------------------------------------------------------------
    def _callbackClickOnMainPaneItem(self, modelIndex_NotUsed):
        """ """
        
        # Do nothing. "onSelectionChange" now handles updates of selected items.
        
        
    #----------------------------------------------------------------------
    def _callbackClickOnSidePaneItem(self, modelIndex_NotUsed):
        """ """
        
        if not self.selectedItemList:
            return
        
        item = self.selectedItemList[0]
        pModelIndex = self.selectedPersModelIndexList[0]
        
        m = self.getCurrentMainPane()        
                                
        if item.itemType == 'page':
                        
            # Check if the new path is the same as the last history path.
            # This check is necessary only for the click on side pane item,
            # not for the click on main pane item.
            if m.pathHistory[m.pathHistoryCurrentIndex] != pModelIndex:
            
                m.pathHistory = m.pathHistory[:(m.pathHistoryCurrentIndex+1)]
                m.pathHistory.append(pModelIndex)
                m.pathHistoryCurrentIndex = len(m.pathHistory)-1
                # History update must happen before calling "self.updateView"
                # function for the view update to work properly.            
                self.updateView(m)
                                        
        elif item.itemType == 'app':
            pass
                
    #----------------------------------------------------------------------
    def clearSelection(self):
        """
              
        """

        print 'clearSelection called'
        m = self.getCurrentMainPane()
        m.listView.selectionModel().clearSelection()
        m.treeView.selectionModel().clearSelection()
        self.treeViewSide.selectionModel().clearSelection()
        self.selectedItemList = []
        self.selectedPersModelIndexList = []
         
    #----------------------------------------------------------------------
    def _callbackDoubleClickOnMainPaneItem(self, modelIndex_NotUsed): 
        """"""
            
        m = self.getCurrentMainPane()
        item = self.selectedItemList[0]
        pModelIndex = self.selectedPersModelIndexList[0]
        
        if item.itemType == 'page':
            
            m.pathHistory = m.pathHistory[:(m.pathHistoryCurrentIndex+1)]
            m.pathHistory.append(pModelIndex)
            m.pathHistoryCurrentIndex = len(m.pathHistory)-1
            # History update must happen before calling "self.updateView"
            # function for the view update to work properly.            
            self.updateView(m)
            
            self.clearSelection()
                                
        elif item.itemType == 'app':
                
            self.emit(Qt.SIGNAL('sigAppExecutionRequested'),
                      item.linkedFile, item.useImport, item.args)    
        
        
    #----------------------------------------------------------------------
    def _callbackDoubleClickOnSidePaneItem(self, modelIndex_NotUsed):
        """ """
        
        if not self.selectedItemList:
            return
        
        item = self.selectedItemList[0]
                        
        if item.itemType == 'page':
            pass
        elif item.itemType == 'app':
            self.emit(Qt.SIGNAL('sigAppExecutionRequested'),
                      item.linkedFile, item.useImport, item.args)   
    
    
    #----------------------------------------------------------------------
    def itemFromIndex(self, modelIndex):
        """
        "modelIndex" can be a Qt.QModelIndex that is coming from Main Pane
        views either on search mode or on non-search mode, as well as coming
        from Side Pane.
        """
        
    
        m = self.getCurrentMainPane()
    
        if type(modelIndex.model()) == Qt.QSortFilterProxyModel:
            proxyModelIndex = modelIndex
            sourceModelIndex = m.proxyModel.mapToSource(proxyModelIndex)
            
            if self.inSearchMode():
                searchItem = m.searchModel.itemFromIndex(sourceModelIndex)
                currentHistoryItem = m.pathHistory[m.pathHistoryCurrentIndex]
                sourceModelIndex = Qt.QModelIndex(currentHistoryItem['searchRootIndex'])
            else:
                pass
            
        else:
            sourceModelIndex = modelIndex
        
        return self.model.itemFromIndex(sourceModelIndex)
    
    #----------------------------------------------------------------------
    def getCurrentRootIndex(self):
        """"""
    
        m = self.getCurrentMainPane()
    
        currentHistoryItem = m.pathHistory[m.pathHistoryCurrentIndex]
        if type(currentHistoryItem) == dict:
            currentRootPersModInd = currentHistoryItem['searchRootIndex']
        else:
            currentRootPersModInd = currentHistoryItem
        
        return Qt.QModelIndex(currentRootPersModInd)
    
    #----------------------------------------------------------------------
    def getCurrentRootPath(self):
        """"""
        
        rootIndex = self.getCurrentRootIndex() # QModelIndex
        
        rootItem = self.model.itemFromIndex(rootIndex)
        
        return rootItem.path
    
    
    #----------------------------------------------------------------------
    def getSourceModelIndex(self, proxyOrSourceModelIndex, mainPane):
        """"""
    
        if type(proxyOrSourceModelIndex.model()) == Qt.QSortFilterProxyModel:
            proxyModelIndex = proxyOrSourceModelIndex
            sourceModelIndex = mainPane.proxyModel.mapToSource(proxyModelIndex)
        else:
            sourceModelIndex = proxyOrSourceModelIndex
            
        return sourceModelIndex
    
    #----------------------------------------------------------------------
    def inSearchMode(self):
        """"""
        
        m = self.getCurrentMainPane()
        
        persistentSourceModelIndex = m.pathHistory[m.pathHistoryCurrentIndex]
        if type(persistentSourceModelIndex) == Qt.QPersistentModelIndex: # When the main pane is showing non-search info
            return False
        else: # When the main pane is showing search info
            return True
        
    #----------------------------------------------------------------------
    def updateView(self, currentMainPane):
        """
        It is necessary for pathHistory and pathHistoryCurrentIndex to be
        updated already before this function is called, since this function
        will call "updatePath" function, which requies this condition.
        Otherwise, update will not work properly.        
        """
        
        m = currentMainPane # for short-hand notation
        
        if not self.inSearchMode(): # When the main pane is showing non-search info
            if m.proxyModel.sourceModel() == m.searchModel:
                m.proxyModel.setSourceModel(self.model)            
                
            sourceModelIndex = Qt.QModelIndex(
                m.pathHistory[m.pathHistoryCurrentIndex])
        
            proxyModelIndex = m.proxyModel.mapFromSource(sourceModelIndex)
            m.listView.setRootIndex(proxyModelIndex)
            m.treeView.setRootIndex(proxyModelIndex)
            self.treeViewSide.setCurrentIndex(sourceModelIndex)
        
            if self.tabWidget:
                tabText = self.model.itemFromIndex(sourceModelIndex).dispName
                self.tabWidget.setTabText(self.tabWidget.currentIndex(),tabText)
            
            self.lineEdit_search.setText('')
            
            
        else: # When the main pane is showing search info
            if m.proxyModel.sourceModel != m.searchModel:
                m.proxyModel.setSourceModel(m.searchModel)
            
            searchInfo = m.pathHistory[m.pathHistoryCurrentIndex]
            self.lineEdit_search.setText(searchInfo['searchText'])
            
            proxyModelIndex = m.proxyModel.mapFromSource(
                m.searchModel.index(0,0) )
            m.listView.setRootIndex(proxyModelIndex)
            m.treeView.setRootIndex(proxyModelIndex)
            
        
        self.updatePath()
            
    #----------------------------------------------------------------------
    def getCurrentMainPane(self):
        """"""
        
        if self.tabWidget:
            currentTabPage = self.tabWidget.currentWidget()
            currentStackedWidget = currentTabPage.findChildren(Qt.QStackedWidget)[0]
            matchedMainPane = [m for m in self.mainPaneList
                               if m.stackedWidget == currentStackedWidget]
            if len(matchedMainPane) == 1:
                return matchedMainPane[0]
            else:
                return None
            
        else:
            return self.mainPaneList[0]
        
    #----------------------------------------------------------------------
    def getParentMainPane(self, childWidget):
        """"""

        childWidgetType = type(childWidget)
        
        if childWidgetType == Qt.QStackedWidget:
            matchedMainPane = [m for m in self.mainPaneList
                               if m.stackedWidget == childWidget]
        elif childWidgetType == CustomListView:
            matchedMainPane = [m for m in self.mainPaneList
                               if m.listView == childWidget]
        elif childWidgetType == CustomTreeView:
            matchedMainPane = [m for m in self.mainPaneList
                               if m.treeView == childWidget]
        else:
            print 'Unexpected child widget type'
            return None
        
        if len(matchedMainPane) == 1:
            return matchedMainPane[0]
        else:
            return None
    
    #----------------------------------------------------------------------
    def convertSearchModelPModIndToModelPModInd(self, searchModel,
                                                searchModelPerModInd):
        """"""
        
        searchModelItem = searchModel.itemFromIndex(
            Qt.QModelIndex(searchModelPerModInd))
        
        return searchModelItem.sourcePersistentModelIndex
    
    #----------------------------------------------------------------------
    def updatePath(self):
        """
        It is necessary for pathHistory and pathHistoryCurrentIndex to be
        updated already before this function is called. Otherwise, update
        will not work properly.
        """
                
        m = self.getCurrentMainPane()
        pModInd = m.pathHistory[m.pathHistoryCurrentIndex]
        if type(pModInd) == Qt.QPersistentModelIndex:
            # If pModInd is a persistent model index of "searchModel",
            # then you need to convert pModInd into the corresponding
            # persistent model index of "self.model" first.
            if type(pModInd.model()) == SearchModel:
                pModInd = self.convertSearchModelPModIndToModelPModInd(
                    m.searchModel, pModInd)
                
            currentRootItem = self.model.itemFromIndex(Qt.QModelIndex(pModInd))
            pathStr = currentRootItem.path
        else: # When main pane is showing search info
            searchInfo = pModInd
            searchRootIndex = searchInfo['searchRootIndex']
            searchRootItem = self.model.itemFromIndex(
                Qt.QModelIndex(searchRootIndex)) 
            pathStr = ('Search Results in ' + searchRootItem.path)
            
        self.lineEdit_path.setText(pathStr)
            
        self.updateStatesOfNavigationButtons()
        
    #----------------------------------------------------------------------
    def goUp(self):
        """"""
                
        m = self.getCurrentMainPane()
        currentIndex = Qt.QModelIndex(m.pathHistory[m.pathHistoryCurrentIndex])
        currentPathItem = self.model.itemFromIndex(currentIndex)
        parentPathItem = currentPathItem.parent()
        parentPathIndex = self.model.indexFromItem(parentPathItem)
        
        if parentPathIndex.isValid():
            pModelIndex = Qt.QPersistentModelIndex(parentPathIndex)
        else:
            print 'Invalid model index detected.'
            return
        
        m.pathHistory = m.pathHistory[:(m.pathHistoryCurrentIndex+1)]
        m.pathHistory.append(pModelIndex)
        m.pathHistoryCurrentIndex = len(m.pathHistory)-1
        # History update must happen before calling "self.updateView"
        # function for the view update to work properly.            
        self.updateView(m)
        
        self.updateStatesOfNavigationButtons()
        
        self.emit(Qt.SIGNAL('sigClearSelection'))   
        
        
    #----------------------------------------------------------------------
    def goBack(self):
        """"""
        
        m = self.getCurrentMainPane()
        if m.pathHistoryCurrentIndex >= 1:
            
            m.pathHistoryCurrentIndex -= 1
            # path history must be updated before calling "updateView" function
            self.updateView(m)
                    
            self.updateStatesOfNavigationButtons()
            
            self.emit(Qt.SIGNAL('sigClearSelection')) 
            

    #----------------------------------------------------------------------
    def goForward(self):
        """"""
        
        m = self.getCurrentMainPane()
        if m.pathHistoryCurrentIndex <= len(m.pathHistory)-2:

            m.pathHistoryCurrentIndex += 1
            # path history must be updated before calling "updateView" function
            self.updateView(m)
            
            self.updateStatesOfNavigationButtons()
            
            self.emit(Qt.SIGNAL('sigClearSelection')) 
            
    
    #----------------------------------------------------------------------
    def updateStatesOfNavigationButtons(self):
        """"""
        
        b = self.actionGoBack
        f = self.actionGoForward
        u = self.actionGoUp
        
        m = self.getCurrentMainPane()
        hist = m.pathHistory
        iHist = m.pathHistoryCurrentIndex
        nHist = len(hist)
        currentPerModInd = hist[iHist]
        if type(currentPerModInd) == Qt.QPersistentModelIndex:
            # If currentPerModInd is a persistent model index of "searchModel",
            # then you need to convert currentPerModInd into the corresponding
            # persistent model index of "self.model" first.
            if type(currentPerModInd.model()) == SearchModel:
                currentPerModInd = self.convertSearchModelPModIndToModelPModInd(
                    m.searchModel, currentPerModInd)            

            currentPathIndex = Qt.QModelIndex(currentPerModInd)
            currentPathStr = self.model.itemFromIndex(currentPathIndex).path
            
            if currentPathStr == (SEPARATOR + 'root'):
                u.setEnabled(False)
            else:
                u.setEnabled(True)
                
        else: # When main pane is showing search info
            u.setEnabled(False)
        
                                    
        if iHist == (nHist-1):
            f.setEnabled(False)
        else:
            f.setEnabled(True)
        
        if iHist == 0:
            b.setEnabled(False)
        else:
            b.setEnabled(True)
        

    #----------------------------------------------------------------------
    def updateMainPaneViewMode(self, view_mode_str):
        """"""
            
        if view_mode_str == 'Icons View':
            triggeredAction = self.actionIconsView
        elif view_mode_str == 'List View':
            triggeredAction = self.actionListView
        elif view_mode_str == 'Details View':
            triggeredAction = self.actionDetailsView
        else:
            print 'Unknown view mode'    

        triggeredAction.setChecked(True)
        self.actionGroupViewMode.emit(Qt.SIGNAL('triggered(QAction *)'),
                                      triggeredAction)

    #----------------------------------------------------------------------
    def getSelectionType(self):
        """"""
        
        if not self.selectedItemList:
            selectionType = 'NoSelection'
        else:
            if len(self.selectedItemList) == 1:
                if self.selectedItemList[0].itemType == 'app':
                    selectionType = 'SingleAppSelection'
                else: # self.selectedItemList[0].itemType == 'page'
                    selectionType = 'SinglePageSelection'
            else:
                itemTypes = list(set([item.itemType for item
                                      in self.selectedItemList]))
                if itemTypes == ['app']:
                    selectionType = 'MultipleAppSelection'
                elif itemTypes == ['page']:
                    selectionType = 'MultiplePageSelection'
                else: # Both app(s) & page(s)
                    selectionType = 'MultipleAppAndPageSelection'
        
        return selectionType
        
    #----------------------------------------------------------------------
    def updateMenuItems(self):
        """"""

        m = self.getCurrentMainPane()
        
        # First categorize current selection
        selectionType = self.getSelectionType()

        # Update enable states for actions that can modify the data,
        # depending on the current root path. If the current path is not in the
        # user modifiable section (i.e., not under /root/Users page), then
        # all the actions that can modify the data structure are disabled here.
        inSearchMode = self.inSearchMode()
        if not inSearchMode:
            currentRootItem = self.model.itemFromIndex(
                self.getSourceModelIndex(m.listView.rootIndex(),m) )
            searchModeDisabledActionList = []
        else:
            currentHistoryItem = m.pathHistory[m.pathHistoryCurrentIndex]
            currentRootPersModInd = currentHistoryItem['searchRootIndex']
            currentRootItem = self.model.itemFromIndex(
                Qt.QModelIndex(currentRootPersModInd) )
            searchModeDisabledActionList = [self.actionPaste,
                                            self.actionCreateNewPage,
                                            self.actionCreateNewApp]
            
        isModifiable = currentRootItem.path.startswith(
            USER_MODIFIABLE_ROOT_PATH)
        modificationActionList = [
            self.actionCut, self.actionPaste, self.actionRename,
            self.actionDelete, self.actionCreateNewApp, self.actionCreateNewPage
        ]
        if isModifiable:
            enableState = True
        else:
            enableState = False
        for a in modificationActionList:
            a.setEnabled(enableState)
        
        # Override Enable states for actions that should be disabled if
        # Main Pane is currently in Search Mode
        for a in searchModeDisabledActionList:
            a.setEnabled(False)
            
            
        # Override Enable state for "Paste" if self.clipboard is an empty list
        if not self.clipboard:
            self.actionPaste.setEnabled(False)
        
        # Override Enable state for "Delete" to disabled.
        # If the selected item on Side Tree View is deleted, then
        # it will cause a problem with the current root item of Main Pane.
        if self.selectedItemList and \
           (currentRootItem.path in [item.path for item in self.selectedItemList]):
            self.actionDelete.setEnabled(False)

        
        sender = self.sender()
        #print sender.title()
        
        if type(sender) == Qt.QMenu: # Clicked on Menu Bar

            sender.clear()
            
            if sender == self.menuFile:

                sender.addAction(self.actionCreateNewPage)
                sender.addAction(self.actionCreateNewApp)

                if (selectionType == 'SinglePageSelection') or \
                   (selectionType == 'MultiplePageSelection'):
                    sender.addSeparator()
                    sender.addAction(self.actionOpen)
                    sender.addAction(self.actionOpenInNewTab)
                    sender.addAction(self.actionOpenInNewWindow)
                elif (selectionType == 'SingleAppSelection') or \
                     (selectionType == 'MultipleAppSelection'):
                    sender.addSeparator()
                    sender.addAction(self.actionOpen)
                    sender.addAction(self.actionOpenWithImport)
                    sender.addAction(self.actionOpenWithPopen)
                else:
                    pass
                
                if (selectionType == 'NoSelection') or \
                   (selectionType == 'SinglePageSelection') or \
                   (selectionType == 'SingleAppSelection'):
                    sender.addSeparator()
                    sender.addAction(self.actionProperties)
                    
                sender.addSeparator()
                sender.addAction(self.actionCloseTabOrWindow)
                
            elif sender == self.menuEdit:
                
                if selectionType != 'NoSelection':
                    sender.addAction(self.actionCut)
                    sender.addAction(self.actionCopy)
                sender.addAction(self.actionPaste)
                if self.clipboard:
                    self.actionPaste.setEnabled(True)
                else:
                    self.actionPaste.setEnabled(False)
                
                sender.addSeparator()
                sender.addAction(self.actionSelectAll)
                
                if (selectionType == 'SinglePageSelection') or \
                   (selectionType == 'SingleAppSelection'):
                    sender.addSeparator()
                    sender.addAction(self.actionRename)
                    
                if selectionType != 'NoSelection':
                    sender.addSeparator()
                    sender.addAction(self.actionDelete)
                
                
            elif sender == self.menuView:
                
                sender.addAction(self.actionToggleSidePaneVisibility)
                
                sender.addSeparator()
                if m.stackedWidget.currentIndex() == self.treeView_stack_index:
                    sender.addAction(self.actionVisibleColumns)
                else:
                    sender.addAction(self.actionArrangeItems)
                    
                sender.addSeparator()
                sender.addAction(self.actionIconsView)
                sender.addAction(self.actionListView)
                sender.addAction(self.actionDetailsView)
                
            elif sender == self.menuGo:
                
                sender.addAction(self.actionGoUp)
                sender.addAction(self.actionGoBack)
                sender.addAction(self.actionGoForward)
                
            elif sender == self.menuHelp:
                pass
            else:
                raise('Unexpected menu sender '+sender.title())
            
        elif sender == self.treeViewSide: # Clicked on Tree View on Side Pane
            

            if selectionType == 'NoSelection':
                return
            
            self.contextMenu.clear()
            
            self.contextMenu.addAction(self.actionOpen)

            if selectionType == 'SinglePageSelection':
                self.contextMenu.addAction(self.actionOpenInNewTab)
                self.contextMenu.addAction(self.actionOpenInNewWindow)
            elif selectionType == 'SingleAppSelection':
                self.contextMenu.addAction(self.actionOpenWithImport)
                self.contextMenu.addAction(self.actionOpenWithPopen)
            else:
                raise ValueError('Unexpected selection type detected: ' + selectionType)
                
            self.contextMenu.addSeparator()
            self.contextMenu.addAction(self.actionCut)
            self.contextMenu.addAction(self.actionCopy)

            self.contextMenu.addSeparator()
            self.contextMenu.addAction(self.actionDelete)
                
            self.contextMenu.addSeparator()
            self.contextMenu.addAction(self.actionProperties)
                
            self.contextMenu.setDefaultAction(self.actionOpen)
              
            
        else: # (type(sender) == CustomListView) or (type(sender) == CustomTreeView)
            # Clicked on List View or Tree View on Main Pane
            
            self.validateSelectedItemList(m)
            # Since "validateSelectedItemList()" function may have cleared
            # selection, selectionType must be updated to reflect the change.
            selectionType = self.getSelectionType()

            self.contextMenu.clear()
            
            if selectionType == 'NoSelection':
                
                self.contextMenu.addAction(self.actionCreateNewPage)
                self.contextMenu.addAction(self.actionCreateNewApp)
                
                self.contextMenu.addSeparator()
                if m.stackedWidget.currentIndex() == self.treeView_stack_index:                
                    self.contextMenu.addAction(self.actionVisibleColumns)
                else:
                    self.contextMenu.addAction(self.actionArrangeItems)

                self.contextMenu.addSeparator()
                self.contextMenu.addAction(self.actionPaste)
                
                self.contextMenu.addSeparator()
                self.contextMenu.addAction(self.actionProperties)
                
                
            elif selectionType == 'SinglePageSelection':
                
                self.contextMenu.addAction(self.actionOpen)
                self.contextMenu.addAction(self.actionOpenInNewTab)
                self.contextMenu.addAction(self.actionOpenInNewWindow)
                
                self.contextMenu.addSeparator()
                self.contextMenu.addAction(self.actionCut)
                self.contextMenu.addAction(self.actionCopy)
                self.contextMenu.addAction(self.actionPaste)
                
                self.contextMenu.addSeparator()
                self.contextMenu.addAction(self.actionRename)
                
                self.contextMenu.addSeparator()
                self.contextMenu.addAction(self.actionDelete)
                
                self.contextMenu.addSeparator()
                self.contextMenu.addAction(self.actionProperties)
                
                self.contextMenu.setDefaultAction(self.actionOpen)
                
            elif selectionType == 'SingleAppSelection':
                
                self.contextMenu.addAction(self.actionOpen)
                self.contextMenu.addAction(self.actionOpenWithImport)
                self.contextMenu.addAction(self.actionOpenWithPopen)
                
                self.contextMenu.addSeparator()
                self.contextMenu.addAction(self.actionCut)
                self.contextMenu.addAction(self.actionCopy)
                self.contextMenu.addAction(self.actionPaste)
                
                self.contextMenu.addSeparator()
                self.contextMenu.addAction(self.actionRename)
                
                self.contextMenu.addSeparator()
                self.contextMenu.addAction(self.actionDelete)
                
                self.contextMenu.addSeparator()
                self.contextMenu.addAction(self.actionProperties)
                
                self.contextMenu.setDefaultAction(self.actionOpen)
                
            elif selectionType == 'MultiplePageSelection':
                
                self.contextMenu.addAction(self.actionOpenInNewTab)
                self.contextMenu.addAction(self.actionOpenInNewWindow)
                
                self.contextMenu.addSeparator()
                self.contextMenu.addAction(self.actionCut)
                self.contextMenu.addAction(self.actionCopy)
                
                self.contextMenu.addSeparator()
                self.contextMenu.addAction(self.actionDelete)
                
            elif selectionType == 'MultipleAppSelection':

                self.contextMenu.addAction(self.actionOpen)
                self.contextMenu.addAction(self.actionOpenWithImport)
                self.contextMenu.addAction(self.actionOpenWithPopen)
                
                self.contextMenu.addSeparator()
                self.contextMenu.addAction(self.actionCut)
                self.contextMenu.addAction(self.actionCopy)
                
                self.contextMenu.addSeparator()
                self.contextMenu.addAction(self.actionDelete)
                
            elif selectionType == 'MultipleAppAndPageSelection':

                self.contextMenu.addAction(self.actionCut)
                self.contextMenu.addAction(self.actionCopy)
                
                self.contextMenu.addSeparator()
                self.contextMenu.addAction(self.actionDelete)
            
            else:
                raise TypeError('Unexpected selection type: ' + selectionType)
            
        
            
        
        
########################################################################
class LauncherApp(Qt.QObject):
    """ """

    #----------------------------------------------------------------------
    def __init__(self, initRootPath):
        """Constructor"""
        
        Qt.QObject.__init__(self)
        
        self.appList = []
        
        self._initModel()
        
        self._initView(initRootPath)
        
        self.connect(self.view, Qt.SIGNAL('sigAppExecutionRequested'),
                     self.launchApp)
            
    #----------------------------------------------------------------------
    def _initModel(self):
        """ """
        
        self.model = LauncherModel() # Used for TreeView on side pane for which sorting is disabled
        
        self.model.updatePathLookupLists() # Do not pass any argument in order to refresh entire path list
        
        
    #----------------------------------------------------------------------
    def _initView(self, initRootPath):
        """ """
        
        if not initRootPath:
            initRootPath = self.model.pathList[0]
        
        self.view = LauncherView(self.model, initRootPath)

    #----------------------------------------------------------------------
    def launchApp(self, appFilename, useImport, args):
        """ """
        
        '''
        You need to make sure that the object returned from the
        "make()" function will not get erased at the end of this
        function call. The object is a GUI object. If it is
        cleared, the GUI window will also disappear. In order
        to keep the object in the memory, one way is to store it in
        "self", which is the method employed here. Or you could declare
        the returned object as "global". With either way, the opened GUI
        window will not disappear immediately.
        '''
        if useImport:

            module = None
            
            try:
                moduleName = 'aphla.gui.'+appFilename
                self.view.statusBar().showMessage(
                    'Trying to import ' + moduleName + '...')
                self.view.repaint()
                __import__(moduleName)
                module = sys.modules[moduleName]
            except ImportError as e:
                self.view.statusBar().showMessage(
                    'Importing ' + moduleName + ' failed: ' + e)                
            except:
                msgBox = Qt.QMessageBox()
                msgBox.setText( (
                    'Unexpected error while launching an app w/ import: ') )
                msgBox.setInformativeText( str(sys.exc_info()) )
                msgBox.setIcon(Qt.QMessageBox.Critical)
                msgBox.exec_()
            
            if not module:
                try:
                    self.view.statusBar().showMessage(
                        'Trying to import ' + appFilename + '...')
                    self.view.repaint()
                    module = __import__(appFilename)
                except ImportError as e:
                    self.view.statusBar().showMessage(
                        'Importing ' + appFilename + ' failed: ' + e) 
                except:
                    msgBox = Qt.QMessageBox()
                    msgBox.setText( (
                        'Unexpected error while launching an app w/ import: ') )
                    msgBox.setInformativeText( str(sys.exc_info()) )
                    msgBox.setIcon(Qt.QMessageBox.Critical)
                    msgBox.exec_()        
                    
            if module:
                try:
                    self.view.statusBar().showMessage(
                        'Trying to launch ' + appFilename + '...')
                    self.view.repaint()
                    if args:
                        self.appList.append(module.make(args))
                    else:
                        self.appList.append(module.make())
                    self.view.statusBar().showMessage(
                        appFilename + ' successfully launched.')                        
                except:
                    msgBox = Qt.QMessageBox()
                    msgBox.setText( (
                        'Error while launching an app w/ import: ') )
                    msgBox.setInformativeText( str(sys.exc_info()) )
                    msgBox.setIcon(Qt.QMessageBox.Critical)
                    msgBox.exec_()        
                    
            else:
                msgBox = Qt.QMessageBox()
                msgBox.setText( ('Importing ' + appFilename + 
                                 ' module has failed.') )
                msgBox.setIcon(Qt.QMessageBox.Critical)
                msgBox.exec_()                
                    
        else:
            try:
                self.view.statusBar().showMessage(
                    'Trying to launch ' + appFilename + '...')
                self.view.repaint()
                p = subprocess.Popen([appFilename])
                self.view.statusBar().showMessage(
                    appFilename + ' successfully launched.')                 
            except:
                msgBox = Qt.QMessageBox()
                msgBox.setText( ('Launching ' + appFilename + 
                                 ' with subprocess.Popen has failed.') )
                msgBox.setInformativeText( str(sys.exc_info()) )
                msgBox.setIcon(Qt.QMessageBox.Critical)
                msgBox.exec_()                        

#----------------------------------------------------------------------
def make(initRootPath=''):
    """"""
    
    # If the platform is other than a POSIX system, then convert
    # the root path separator to the valid path separator of the OS.
    if initRootPath:
        initRootPath.replace(posixpath.sep, os.sep)
    
    app = LauncherApp(initRootPath)
    app.view.show()
        
    return app


#----------------------------------------------------------------------
def main(args = None):
    """ """
    
    if 'cothread' in globals().keys():
        using_cothread = True
    else:
        using_cothread = False
        
    if using_cothread:
        cothread.iqt(use_timer = True)
    else:
        qapp = Qt.QApplication(args)
    
    
    initRootPath = SEPARATOR + 'root'
    app = LauncherApp(initRootPath)
    app.view.show()

    if using_cothread:
        cothread.WaitForQuit()
    else:
        exit_status = qapp.exec_()
        sys.exit(exit_status)
        

#----------------------------------------------------------------------    
if __name__ == "__main__" :
    main(sys.argv)
    
