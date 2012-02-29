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

SEPARATOR = os.sep
ITEM_PROPERTY_NAMES = ['path','linkedFile','args','useImport','singleton','itemType']
COLUMN_NAMES = ['Path','Linked File','Arguments','Use Import','Singleton','Item Type']
ITEM_COLOR_PAGE = Qt.Qt.black
ITEM_COLOR_APP = Qt.Qt.red

import gui_icons
from Qt4Designer_files.ui_launcher import Ui_MainWindow

import aphla

## TODO ##
# *) Highlight the search matching portion of texts in QTreeView and QListView
# *) Allow in-program XML file modification
# *) Right-click on column name and allow add/remove visible properties

    
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

        doc = self.open_XML_hierarchy_file()
        
        self.pathList = []
        self.pModelIndList = []
        
        self.nRows = 0
        self.construct_tree_model(doc.firstChild()) # Recursively search through 
        # the XML file to build the corresponding tree structure.
        
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
            if info['import'] == 'True':
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
                for (ii,prop_name) in enumerate(ITEM_PROPERTY_NAMES):
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
            self.construct_tree_model(dom.nextSibling().firstChild())
            

    #----------------------------------------------------------------------
    def getItemInfo(self, dom):
        """
        """
        
        node = dom.firstChild()
        
        info = {'dispName':'',
                'linkedFile':'', 'import':False,
                'singleton':False, 'args':'',
                'sibling_DOMs':[]}
        
        while not node.isNull():
            nodeName = str(node.nodeName())
            if nodeName in ('dispName', 'linkedFile', 'import',
                            'singleton', 'args'):
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
    def open_XML_hierarchy_file(self):
        """
        """
        
        doc = QDomDocument('')
        f = Qt.QFile(aphla.conf.filename("appLauncherHierarchy.xml"))
        if not f.open(Qt.QIODevice.ReadOnly):
            raise IOError('Failed to open file.')
        if not doc.setContent(f):
            f.close()
            raise IOError('Failed to parse file.')
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
        
        for p in ITEM_PROPERTY_NAMES:
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

        rootPModelIndex = self.model.pModelIndexFromPath(initRootPath)
        if not initRootPath:
            raise IOError
        rootModelIndex = Qt.QModelIndex(rootPModelIndex)
        self.mainPaneList = [MainPane(model,rootModelIndex,self.stackedWidgetMainPane,
                                      self.listViewMain,self.treeViewMain)]
        
        self.selectedViewType = 'QListView'
        self.selectedListViewMode = Qt.QListView.IconMode
        self.selectedItem = self.model.itemFromIndex(rootModelIndex)
        self.selectedPersistentModelIndex = rootPModelIndex

        self._initMainPane(len(self.mainPaneList)-1)

        
        ## Definition of Actions
        self.actionOpenInNewTab = Qt.QAction(Qt.QIcon(),
                                             'Open in New Tab', self)
        self.actionOpenInNewWindow = Qt.QAction(Qt.QIcon(),
                                                'Open in New Window', self)        
        self.popMenu = Qt.QMenu()
        self.popMenu.addAction(self.actionOpenInNewTab)
        self.popMenu.addAction(self.actionOpenInNewWindow)        

        ## Update path
        self.updatePath()
        
        self.lineEdit_search.setCompleter(self.model.completer)
        
        ## Make connections
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
        
        self.connect(self.actionOpenInNewTab, Qt.SIGNAL('triggered()'),
                     self.openInNewTab)
        self.connect(self.actionOpenInNewWindow, Qt.SIGNAL('triggered()'),
                     self.openInNewWindow)
                     
        # Use "textChanged" signal to include programmatic changes of search text.
        # However, if this causes crashes (this tends to happen when you add
        # a breakpoint in the callback function), switch the signal back to "textEdited"
        # and try to debug the code.
        self.connect(self.lineEdit_search, Qt.SIGNAL('textChanged(const QString &)'),
                     self.onSearchTextChange)
        
        self.connect(self.splitterPanes, Qt.SIGNAL('splitterMoved(int,int)'),
                     self.onSplitterManualMove)

        
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
            for (j,prop_name) in enumerate(ITEM_PROPERTY_NAMES):
                p = getattr(item,prop_name)
                if not isinstance(p,str):
                    p = str(p)
                rootItem.setChild(i,j+1,Qt.QStandardItem(p))
                
        self.updateView(m)
        
        
    
    #----------------------------------------------------------------------
    def openContextMenu(self, qpoint):
        """"""
        
        sender = self.sender()
        
        m = self.getParentMainPane(sender)
        
        if m: # When right-clicked on main pane
            pModInd = Qt.QPersistentModelIndex(
                m.proxyModel.mapToSource(sender.currentIndex()) )
            if type(m.proxyModel.sourceModel()) == SearchModel:
                pModInd = self.convertSearchModelPModIndToModelPModInd(
                    m.searchModel, pModInd)
                    
            self.selectedItem = self.model.itemFromIndex(Qt.QModelIndex(pModInd))
            self.selectedViewType = type(sender)
            self.selectedListViewMode = m.listView.viewMode()
        else: # When right-clicked on side pane
            self.selectedItem = self.model.itemFromIndex(sender.currentIndex())
            
            m = self.getCurrentMainPane()
            if m.stackedWidget.currentIndex() == self.listView_stack_index:
                self.selectedViewType = Qt.QListView
            else:
                self.selectedViewType = Qt.QTreeView
            self.selectedListViewMode = m.listView.viewMode()
        
        self.popMenu.exec_(sender.mapToGlobal(qpoint))
        
    #----------------------------------------------------------------------
    def _initMainPane(self, main_pane_index):
        """"""
        
        main_pane = self.mainPaneList[main_pane_index]
        
        new_treeView = main_pane.treeView
        new_listView = main_pane.listView
        
        self.connect(new_listView,
                     Qt.SIGNAL('customContextMenuRequested(const QPoint &)'),
                     self.openContextMenu)
        self.connect(new_treeView,
                     Qt.SIGNAL('customContextMenuRequested(const QPoint &)'),
                     self.openContextMenu)
    
        self.connect(new_listView,
                     Qt.SIGNAL('doubleClicked(const QModelIndex &)'),
                     self._callbackDoubleClickOnMainPaneItem)
        self.connect(new_treeView,
                     Qt.SIGNAL('doubleClicked(const QModelIndex &)'),
                     self._callbackDoubleClickOnMainPaneItem)

        self.connect(new_listView,
                     Qt.SIGNAL('clicked(const QModelIndex &)'),
                     self._callbackClickOnMainPaneItem)
        self.connect(new_treeView,
                     Qt.SIGNAL('clicked(const QModelIndex &)'),
                     self._callbackClickOnMainPaneItem)        

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
            currentRootItem = self.model.itemFromIndex(
                Qt.QModelIndex(m.pathHistory[m.pathHistoryCurrentIndex]) )
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
        initRootModelIndex = self.model.indexFromItem(self.selectedItem)
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
        self.tabWidget.addTab(new_tab, self.selectedItem.dispName)
        self.tabWidget.setCurrentWidget(new_tab)
    
    #----------------------------------------------------------------------
    def openInNewWindow(self):
        """"""
        
        appFilepath = sys.modules[self.__module__].__file__
        appFilename = os.path.split(appFilepath)[1]
        if appFilename.endswith('.pyc'):
            appFilename = appFilename.replace('.pyc','')
        elif appFilename.endswith('.py'):
            appFilename = appFilename.replace('.py','')
        useImport = True
        args = self.selectedItem.path
        self.emit(Qt.SIGNAL('sigAppExecutionRequested'),
                  appFilename, useImport, args)
        
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
    def _callbackClickOnMainPaneItem(self, modelIndex):
        """ """
                
        m = self.getCurrentMainPane()
        currentModelIndex = self.getSourceModelIndex(modelIndex, m)
                            
        if currentModelIndex.isValid():
            self.selectedPersistentModelIndex = \
                Qt.QPersistentModelIndex(currentModelIndex)
        else:
            print 'Invalid model index detected.'
            return        
            
        self.selectedItem = m.proxyModel.sourceModel().itemFromIndex(currentModelIndex)
        
    #----------------------------------------------------------------------
    def _callbackClickOnSidePaneItem(self, modelIndex):
        """ """
        
        #self._callbackClickOnMainPaneItem(modelIndex)
        
        if modelIndex.isValid():
            self.selectedPersistentModelIndex = \
                Qt.QPersistentModelIndex(modelIndex)
        else:
            print 'Invalid model index detected.'
            return           
        self.selectedItem = self.model.itemFromIndex(modelIndex)

        pModelIndex = self.selectedPersistentModelIndex
        item = self.selectedItem
        
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
    def _callbackDoubleClickOnMainPaneItem(self, modelIndex_NotUsed): 
        """"""
            
        m = self.getCurrentMainPane()
        item = self.selectedItem
        pModelIndex = self.selectedPersistentModelIndex
        # If pModelIndex is a persistent model index of "searchModel",
        # then you need to convert pModelIndex into the corresponding
        # persistent model index of "self.model" first.
        if type(pModelIndex.model()) == SearchModel:
            pModelIndex = self.convertSearchModelPModIndToModelPModInd(
                m.searchModel, pModelIndex)        
                        
        if item.itemType == 'page':
                
            m.pathHistory = m.pathHistory[:(m.pathHistoryCurrentIndex+1)]
            m.pathHistory.append(pModelIndex)
            m.pathHistoryCurrentIndex = len(m.pathHistory)-1
            # History update must happen before calling "self.updateView"
            # function for the view update to work properly.            
            self.updateView(m)
                                
        elif item.itemType == 'app':
                
            self.emit(Qt.SIGNAL('sigAppExecutionRequested'),
                      item.linkedFile, item.useImport, item.args)    
        
        
    #----------------------------------------------------------------------
    def _callbackDoubleClickOnSidePaneItem(self, modelIndex_NotUsed):
        """ """

        item = self.selectedItem
                        
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
                print 'ERROR:'
                print '# of matched main panes = ' + str(len(matchedMainPane))
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
            print 'ERROR:'
            print '# of matched panes = ' + str(len(matchedMainPane))
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
        
        
    #----------------------------------------------------------------------
    def goBack(self):
        """"""
        
        m = self.getCurrentMainPane()
        if m.pathHistoryCurrentIndex >= 1:
            
            m.pathHistoryCurrentIndex -= 1
            # path history must be updated before calling "updateView" function
            self.updateView(m)
                    
            self.updateStatesOfNavigationButtons()
            

    #----------------------------------------------------------------------
    def goForward(self):
        """"""
        
        m = self.getCurrentMainPane()
        if m.pathHistoryCurrentIndex <= len(m.pathHistory)-2:

            m.pathHistoryCurrentIndex += 1
            # path history must be updated before calling "updateView" function
            self.updateView(m)
            
            self.updateStatesOfNavigationButtons()
            
    
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
            try:
                moduleName = 'aphla.gui.'+appFilename
                __import__(moduleName)
                module = sys.modules[moduleName]
            except ImportError:
                module = __import__(appFilename)
                
            if args:
                self.appList.append(module.make(args))
            else:
                self.appList.append(module.make())
        else:
            subprocess.Popen([appFilename])

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
    
