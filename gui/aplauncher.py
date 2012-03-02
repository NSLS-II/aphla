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

MODEL_ITEM_PROPERTY_NAMES = ['path','linkedFile','args','useImport','singleton','itemType']
COLUMN_NAMES = ['Path','Linked File','Arguments','Use Import','Singleton','Item Type']
XML_ITEM_PROPERTY_NAMES = ['dispName','linkedFile','useImport','singleton','args']
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

import gui_icons
from Qt4Designer_files.ui_launcher import Ui_MainWindow

import aphla

## TODO ##
# *) Highlight the search matching portion of texts in QTreeView and QListView
# *) Allow in-program XML file modification
# *) Right-click on column name and allow add/remove visible properties
# *) Bypass XML tree construction, if XML file not changed. Load
# directory the tree model data for faster start-up.
# *) Implement page jumping with the path buttons hidden under
# the path line editbox.
# *) path auto completion & naviation from path line editbox
# *) Add <description> to XML
# *) Implement <singleton>
# *) Implement <args> for popen
# *) Allow multi-selection for deleting/copying

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
            item.itemType = info['type']
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
                self.pathList.append(item.path)
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
        
        info = {'dispName':'',
                'linkedFile':'', 'useImport':False,
                'singleton':False, 'args':'',
                'sibling_DOMs':[]}
        
        while not node.isNull():
            nodeName = str(node.nodeName())
            if nodeName in XML_ITEM_PROPERTY_NAMES:
                info[nodeName] = str(node.firstChild().nodeValue())
            elif nodeName in ('page', 'app'):
                info['sibling_DOMs'].append(node)
                
            node = node.nextSibling()
    
        if info['dispName']:
            info['type'] = str(dom.nodeName())
        else:
            info = {}
                    
        return info
    
    #----------------------------------------------------------------------
    def constructXMLElementsFromModel(self, doc, parentModelItem, parentDOMElement):
        """"""
        
        childItemList = [parentModelItem.child(i,0) for i in
                         range(parentModelItem.rowCount())]
        for childItem in childItemList:
            childElement = doc.createElement(childItem.itemType)
            
            for (ii,prop_name) in enumerate(XML_ITEM_PROPERTY_NAMES):
                p = getattr(childItem,prop_name)
                if prop_name == 'useImport':
                    print p
                if not isinstance(p,str):
                    p = str(p)
                if p:
                    elem = doc.createElement(prop_name)
                    elemNodeText = doc.createTextNode(p)
                    elem.appendChild(elemNodeText)
                    childElement.appendChild(elem)

            if childItem.hasChildren():
                self.constructXMLElementsFromModel(doc, childItem, childElement)
            
            parentDOMElement.appendChild(childElement)
        
        
    #----------------------------------------------------------------------
    def writeToXMLFile(self, XML_Filepath, rootModelItem):
        """"""
                
        if rootModelItem.itemType == 'page':
            tagItemType = 'page'
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
        modelRootDOMElement = doc.createElement(tagItemType)
        for (ii,prop_name) in enumerate(XML_ITEM_PROPERTY_NAMES):
            p = getattr(rootModelItem,prop_name)
            if not isinstance(p,str):
                p = str(p)
            if p:
                elem = doc.createElement(prop_name)
                elemNodeText = doc.createTextNode(p)
                elem.appendChild(elemNodeText)
                modelRootDOMElement.appendChild(elem)
        
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
        
        stream << doc.toString()
        
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
            self.pathList.append(childItem.path)
            self.pModelIndList.append(Qt.QPersistentModelIndex(self.indexFromItem(childItem)))
            
            #for j in range(childItem.rowCount()):
            self.updatePathLookupLists(childItem)
                
    #----------------------------------------------------------------------
    def pModelIndexFromPath(self, path):
        """"""
        
        index = self.pathList.index(path)
        
        return self.pModelIndList[index]
        
    
    
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
            self.dispName = ''
        self.itemType = 'page' # Either 'app' or 'page'
        self.setIcon(Qt.QIcon(":/folder.png"))
        self.path = SEPARATOR
        self.linkedFile = '' # Empty string for 'page'
        self.args = '' # Empty string for 'page'
        self.useImport = False
        self.singleton = False
               
        # Make the item NOT editable
        self.setFlags(self.flags() & ~Qt.Qt.ItemIsEditable)
        
        
    #----------------------------------------------------------------------
    def shallowCopy(self):
        """"""
        
        copiedItem = LauncherModelItem(self.icon(),self.dispName)
        
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
class MainPane:
    """"""

    #----------------------------------------------------------------------
    def __init__(self, model, initRootModelIndex, stackedWidget, listView, treeView,
                 initListViewMode=Qt.QListView.IconMode):
        """Constructor"""
        
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
        
        self.splitterPanes.setSizes(
            [self.width()*(1./5),self.width()*(4./5)])
        self.manualSplitterSizes = self.splitterPanes.sizes()
        
        self.tabWidget = None
                
        
        self.listView_stack_index = 1
        self.treeView_stack_index = 0
        
        self.view_mode_index_icons = 0
        self.view_mode_index_list = 1
        self.view_mode_index_details = 2
        
        # Initialize the side pane QTreeView
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

        rootPModelIndex = self.model.pModelIndexFromPath(initRootPath)
        if not rootPModelIndex:
            raise IOError('Invalid initial root path provided: ' + initRootPath)
        rootModelIndex = Qt.QModelIndex(rootPModelIndex)
        self.mainPaneList = [MainPane(model,rootModelIndex,self.stackedWidgetMainPane,
                                      self.listViewMain,self.treeViewMain)]
        
        self.selectedViewType = Qt.QListView
        self.selectedListViewMode = Qt.QListView.IconMode
        self.selectedItemList = []
        self.selectedPersModelIndexList = []
        
        self._initMainPane(len(self.mainPaneList)-1)

        
        ## Create context menus
        self.contextMenuSinglePageSelected = Qt.QMenu()
        self.contextMenuSinglePageSelected.addAction(self.actionOpen)
        self.contextMenuSinglePageSelected.addAction(self.actionOpenInNewTab)
        self.contextMenuSinglePageSelected.addAction(self.actionOpenInNewWindow)
        self.contextMenuSinglePageSelected.addSeparator()
        self.contextMenuSinglePageSelected.addAction(self.actionCut)
        self.contextMenuSinglePageSelected.addAction(self.actionCopy)
        self.contextMenuSinglePageSelected.addSeparator()
        self.contextMenuSinglePageSelected.addAction(self.actionRename)
        self.contextMenuSinglePageSelected.addSeparator()
        self.contextMenuSinglePageSelected.addAction(self.actionDelete)
        self.contextMenuSinglePageSelected.addSeparator()
        self.contextMenuSinglePageSelected.addAction(self.actionProperties)        
        #
        self.contextMenuMultiplePagesSelected = Qt.QMenu()
        self.contextMenuMultiplePagesSelected.addAction(self.actionOpenInNewTab)
        self.contextMenuMultiplePagesSelected.addAction(self.actionOpenInNewWindow)
        self.contextMenuMultiplePagesSelected.addSeparator()
        self.contextMenuMultiplePagesSelected.addAction(self.actionCut)
        self.contextMenuMultiplePagesSelected.addAction(self.actionCopy)
        self.contextMenuMultiplePagesSelected.addSeparator()
        self.contextMenuMultiplePagesSelected.addAction(self.actionDelete)
        #        
        self.contextMenuSingleAppSelected = Qt.QMenu()
        self.contextMenuSingleAppSelected.addAction(self.actionOpen)
        self.contextMenuSingleAppSelected.addAction(self.actionOpenWithImport)
        self.contextMenuSingleAppSelected.addAction(self.actionOpenWithPopen)
        self.contextMenuSingleAppSelected.addSeparator()
        self.contextMenuSingleAppSelected.addAction(self.actionCut)
        self.contextMenuSingleAppSelected.addAction(self.actionCopy)
        self.contextMenuSingleAppSelected.addSeparator()
        self.contextMenuSingleAppSelected.addAction(self.actionRename)
        self.contextMenuSingleAppSelected.addSeparator()
        self.contextMenuSingleAppSelected.addAction(self.actionDelete)
        self.contextMenuSingleAppSelected.addSeparator()
        self.contextMenuSingleAppSelected.addAction(self.actionProperties)          
        #        
        self.contextMenuMultipleAppsSelected = Qt.QMenu()
        self.contextMenuMultipleAppsSelected.addAction(self.actionOpen)
        self.contextMenuMultipleAppsSelected.addAction(self.actionOpenWithImport)
        self.contextMenuMultipleAppsSelected.addAction(self.actionOpenWithPopen)
        self.contextMenuMultipleAppsSelected.addSeparator()
        self.contextMenuMultipleAppsSelected.addAction(self.actionCut)
        self.contextMenuMultipleAppsSelected.addAction(self.actionCopy)
        self.contextMenuMultipleAppsSelected.addSeparator()
        self.contextMenuMultipleAppsSelected.addAction(self.actionDelete)
        #        
        self.contextMenuPagesAndAppsSelected = Qt.QMenu()
        self.contextMenuPagesAndAppsSelected.addAction(self.actionCut)
        self.contextMenuPagesAndAppsSelected.addAction(self.actionCopy)
        self.contextMenuPagesAndAppsSelected.addSeparator()
        self.contextMenuPagesAndAppsSelected.addAction(self.actionDelete)
        #
        self.contextMenuNoneSelected = Qt.QMenu()
        self.contextMenuNoneSelected.addAction(self.actionCreateNewPage)
        self.contextMenuNoneSelected.addAction(self.actionCreateNewApp)
        self.contextMenuNoneSelected.addSeparator()
        self.contextMenuNoneSelected.addAction(self.actionArrangeItems) # TODO
        self.contextMenuNoneSelected.addSeparator()
        self.contextMenuNoneSelected.addAction(self.actionPaste)
        self.contextMenuNoneSelected.addSeparator()
        self.contextMenuNoneSelected.addAction(self.actionProperties)
        
        ## Create menus
        self.menuFile.addAction(self.actionOpen)
        self.menuFile.addAction(self.actionOpenInNewTab)
        self.menuFile.addAction(self.actionOpenInNewWindow)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionCut)
        self.menuFile.addAction(self.actionCopy)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionRename)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionDelete)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionProperties)        

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
        
        self.connect(self.splitterPanes, Qt.SIGNAL('splitterMoved(int,int)'),
                     self.onSplitterManualMove)

        self.connect(self, Qt.SIGNAL('sigClearSelection'),
                     self.clearSelection)
        
    #----------------------------------------------------------------------
    def onSplitterManualMove(self, int_pos, int_index):
        """"""
        
        self.manualSplitterSizes = self.splitterPanes.sizes()
        
        
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
        
        currentRootItem = self.model.itemFromIndex(
            m.proxyModel.mapToSource(m.listView.rootIndex()))
        
        if currentRootItem.path in \
           [i.path for i in self.selectedItemList]:
            self.clearSelection()
        
    #----------------------------------------------------------------------
    def openContextMenu(self, qpoint):
        """"""
        
        sender = self.sender()
        
        globalClickPos = sender.mapToGlobal(qpoint)        
        
        m = self.getParentMainPane(sender)
        
        if m: # When right-clicked on main pane
            
            self.validateSelectedItemList(m)
            
            if not self.selectedItemList: # When no item is being selected
                self.contextMenuNoneSelected.exec_(globalClickPos)
            else:
            
                if len(self.selectedItemList) == 1:
                    selectedItem = self.selectedItemList[0]
                    
                    if selectedItem.itemType == 'page': # When a page item is selected
                        self.contextMenuSinglePageSelected.exec_(globalClickPos)
                    else: # When an app item is selected
                        self.contextMenuSingleAppSelected.exec_(globalClickPos)   
                    
                else:
                    selectedItemTypes = list(set([i.itemType for i in self.selectedItemList]))
                    if len(selectedItemTypes) == 2: # When page item(s) and app item(s) are selected
                        self.contextMenuPagesAndAppsSelected.exec_(globalClickPos)
                    elif selectedItemTypes[0] == 'page': # When multiple page items are selected
                        self.contextMenuMultiplePagesSelected.exec_(globalClickPos)
                    else: # When multiple app items are selected
                        self.contextMenuMultipleAppsSelected.exec_(globalClickPos)
                    
            self.selectedViewType = type(sender)
            self.selectedListViewMode = m.listView.viewMode()            
            
        else: # When right-clicked on side pane

            if not self.selectedItemList:
                return
            
            selectedItem = self.selectedItemList[0]
            
            m = self.getCurrentMainPane()
            if m.stackedWidget.currentIndex() == self.listView_stack_index:
                self.selectedViewType = Qt.QListView
            else:
                self.selectedViewType = Qt.QTreeView
            self.selectedListViewMode = m.listView.viewMode()
        
            if selectedItem.itemType == 'page': # When a page item is selected
                self.contextMenuSinglePageSelected.exec_(globalClickPos)
            else: # When an app item is selected
                self.contextMenuSingleAppSelected.exec_(globalClickPos)              
    
    #----------------------------------------------------------------------
    def _initMainPaneTreeViewSettings(self, newTreeView):
        """"""
        
        newTreeView.setSelectionMode(Qt.QAbstractItemView.ExtendedSelection)
        newTreeView.setSelectionBehavior(Qt.QAbstractItemView.SelectRows)
        
        newTreeView.setDragDropMode(Qt.QAbstractItemView.NoDragDrop)
        
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
               
    
    #----------------------------------------------------------------------
    def _initMainPaneListViewSettings(self, newListView):
        """"""
        
        newListView.setSelectionMode(Qt.QAbstractItemView.ExtendedSelection)
        newListView.setSelectionBehavior(Qt.QAbstractItemView.SelectRows)
        
        newListView.setResizeMode(Qt.QListView.Adjust)
        newListView.setWrapping(True)
        newListView.setDragDropMode(Qt.QAbstractItemView.NoDragDrop)
        
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
            listView = currentStackedWidget.findChildren(Qt.QListView)[0]
            if listView.viewMode() == Qt.QListView.IconMode:
                self.comboBox_view_mode.setCurrentIndex(self.view_mode_index_icons)
            elif listView.viewMode() == Qt.QListView.ListMode:
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
            new_treeView = Qt.QTreeView(new_page1)
            page1_gridLayout.addWidget(new_treeView, 0, 0, 1, 1)
            new_stackedWidget.addWidget(new_page1)
            new_page2 = Qt.QWidget()
            page2_gridLayout = Qt.QGridLayout(new_page2)
            page2_gridLayout.setContentsMargins(-1, 0, 0, 0)
            new_listView = Qt.QListView(new_page2)
            new_listView.setViewMode(self.selectedListViewMode)
            page2_gridLayout.addWidget(new_listView, 0, 0, 1, 1)
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
            if self.selectedViewType == Qt.QListView:
                new_stackedWidget.setCurrentIndex(self.listView_stack_index)
            elif self.selectedViewType == Qt.QTreeView:
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
        backAction = Qt.QAction(Qt.QIcon(":/left_arrow.png"),
                                "Back", self);
        backAction.setCheckable(False)
        backAction.setObjectName("action_back")
        backAction.setEnabled(False)
        self.addAction(backAction)
        self.connect(backAction, Qt.SIGNAL("triggered()"),
                     self.goBack) 

        # Action for Forward button
        forwardAction = Qt.QAction(Qt.QIcon(":/right_arrow.png"),
                                "Forward", self);
        forwardAction.setCheckable(False)
        forwardAction.setObjectName("action_forward")
        forwardAction.setEnabled(False)
        self.addAction(forwardAction)
        self.connect(forwardAction, Qt.SIGNAL("triggered()"),
                     self.goForward)         

        # Action for Up button
        upAction = Qt.QAction(Qt.QIcon(":/up_arrow.png"),
                                "Up", self);
        upAction.setCheckable(False)
        upAction.setObjectName("action_up")
        upAction.setEnabled(False)
        self.addAction(upAction)
        self.connect(upAction, Qt.SIGNAL("triggered()"),
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
        #self.connect(self.actionOpen, Qt.SIGNAL('triggered()'),
                     #self.openPageOrApps)
        
        self.actionCut = Qt.QAction(Qt.QIcon(), 'Cut', self)
        self.actionCopy = Qt.QAction(Qt.QIcon(), 'Copy', self)
        self.actionPaste = Qt.QAction(Qt.QIcon(), 'Paste', self)
        self.actionRename = Qt.QAction(Qt.QIcon(), 'Rename', self)
        self.actionProperties = Qt.QAction(Qt.QIcon(), 'Properties', self)
        self.actionOpenWithImport = Qt.QAction(Qt.QIcon(), 'Open w/ import', self)
        self.actionOpenWithPopen = Qt.QAction(Qt.QIcon(), 'Open w/ Popen', self)
        self.actionCreateNewPage = Qt.QAction(Qt.QIcon(), 'Create New Page Item', self)
        self.actionCreateNewApp = Qt.QAction(Qt.QIcon(), 'Create New App Item', self)
        self.actionArrangeItems = Qt.QAction(Qt.QIcon(), 'Arrange Items', self)
        
        self.actionDelete = Qt.QAction(Qt.QIcon(), 'Delete', self)
        self.connect(self.actionDelete, Qt.SIGNAL('triggered()'),
                  self.deleteItems)
        
    #----------------------------------------------------------------------
    def deleteItems(self):
        """"""
        
        self.model.removeRow(self.selectedItemList[0].row(),
                             self.selectedItemList[0].parent().index())
        
        user_XML_Filepath = DOT_HLA_QFILEPATH + SEPARATOR + 'test.xml' #USER_XML_FILENAME
        user_XML_Filepath.replace('\\','/') # On Windows, convert Windows path separator ('\\') to Linux path separator ('/') 
                        
        rootModelItem = self.model.itemFromIndex( Qt.QModelIndex(
            self.model.pModelIndexFromPath('/root/Users') ) )
        self.model.writeToXMLFile(user_XML_Filepath, rootModelItem)
        
    #----------------------------------------------------------------------
    def _initMainToolbar(self):
        """"""
        
        # Back button
        backToolbar = self.addToolBar("Back")
        backToolbar.setObjectName("toolbar_back")
        backToolbar.setFloatable(False)
        backToolbar.setMovable(False)
        backAction = self.findChild(Qt.QAction,"action_back")
        backToolbar.addAction(backAction)
        
        # Forward button
        forwardToolbar = self.addToolBar("Forward")
        forwardToolbar.setObjectName("toolbar_forward")
        forwardToolbar.setFloatable(False)
        forwardToolbar.setMovable(False)
        forwardAction = self.findChild(Qt.QAction,"action_forward")
        forwardToolbar.addAction(forwardAction)        
        
        # Up button
        upToolbar = self.addToolBar("Up")
        upToolbar.setObjectName("toolbar_up")
        upToolbar.setFloatable(False)
        upToolbar.setMovable(False)        
        upAction = self.findChild(Qt.QAction,"action_up")
        upToolbar.addAction(upAction)
        
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

        m = self.getCurrentMainPane()
        m.listView.selectionModel().clearSelection()
        m.treeView.selectionModel().clearSelection()
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
    def getSourceModelIndex(self, proxyOrSourceModelIndex, mainPane):
        """"""
    
        if type(proxyOrSourceModelIndex.model()) == Qt.QSortFilterProxyModel:
            proxyModelIndex = proxyOrSourceModelIndex
            sourceModelIndex = mainPane.proxyModel.mapToSource(proxyModelIndex)
        else:
            sourceModelIndex = proxyOrSourceModelIndex
            
        return sourceModelIndex
        
    #----------------------------------------------------------------------
    def updateView(self, currentMainPane):
        """
        It is necessary for pathHistory and pathHistoryCurrentIndex to be
        updated already before this function is called, since this function
        will call "updatePath" function, which requies this condition.
        Otherwise, update will not work properly.        
        """
        
        m = currentMainPane # for short-hand notation
        
        persistentSourceModelIndex = m.pathHistory[m.pathHistoryCurrentIndex]
        if type(persistentSourceModelIndex) == Qt.QPersistentModelIndex: # When the main pane is showing non-search info
            if m.proxyModel.sourceModel() == m.searchModel:
                m.proxyModel.setSourceModel(self.model)            
                
            sourceModelIndex = Qt.QModelIndex(persistentSourceModelIndex)
        
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
            
            searchInfo = persistentSourceModelIndex
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
        elif childWidgetType == Qt.QListView:
            matchedMainPane = [m for m in self.mainPaneList
                               if m.listView == childWidget]
        elif childWidgetType == Qt.QTreeView:
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
        
        b = self.findChild(Qt.QAction,"action_back")
        f = self.findChild(Qt.QAction,"action_forward")
        u = self.findChild(Qt.QAction,'action_up')
        
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
        
        m = self.getCurrentMainPane()
        s = m.stackedWidget;
        
        if view_mode_str == 'Icons View':
            if s.currentIndex() == self.treeView_stack_index:
                s.setCurrentIndex(self.listView_stack_index)
            m.listView.setViewMode(Qt.QListView.IconMode)            
        elif view_mode_str == 'List View':
            if s.currentIndex() == self.treeView_stack_index:
                s.setCurrentIndex(self.listView_stack_index)
            m.listView.setViewMode(Qt.QListView.ListMode)
        elif view_mode_str == 'Details View':
            if s.currentIndex() == self.listView_stack_index:
                s.setCurrentIndex(self.treeView_stack_index)
            for c in range(self.model.columnCount()):
                m.treeView.resizeColumnToContents(c)
        else:
            print 'Unknown view mode'
            
    ##----------------------------------------------------------------------
    #def focusOutEvent(self, event):
        #""""""
    
        #super(LineEditForTabText,self).focusOutEvent(event)
        
        #self.emit(Qt.SIGNAL('editingFinished()'))
        
        
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
        
        self.model.updatePathLookupLists()
        
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
                __import__(moduleName)
                module = sys.modules[moduleName]
            except ImportError as e:
                importErrorMessage = e
            except:
                msgBox = Qt.QMessageBox()
                msgBox.setText( (
                    'Unexpected error while launching an app w/ import: ') )
                msgBox.setInformativeText( str(sys.exc_info()) )
                msgBox.setIcon(Qt.QMessageBox.Critical)
                msgBox.exec_()
            
            if not module:
                try:
                    module = __import__(appFilename)
                except ImportError:
                    pass
                except:
                    msgBox = Qt.QMessageBox()
                    msgBox.setText( (
                        'Unexpected error while launching an app w/ import: ') )
                    msgBox.setInformativeText( str(sys.exc_info()) )
                    msgBox.setIcon(Qt.QMessageBox.Critical)
                    msgBox.exec_()        
                    
            if module:
                try:
                    if args:
                        self.appList.append(module.make(args))
                    else:
                        self.appList.append(module.make())
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
                msgBox.setInformativeText( str(importErrorMessage) )
                msgBox.setIcon(Qt.QMessageBox.Critical)
                msgBox.exec_()                
                    
        else:
            try:
                subprocess.Popen([appFilename])
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
    
