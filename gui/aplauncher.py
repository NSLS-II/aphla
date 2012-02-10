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

#import config # gives access to qtapp variable that holds a Qt.QApplication instance

import sys
import math
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

from Qt4Designer_files.ui_launcher import Ui_MainWindow

import aphla

# TODO:
# *) Allow passing arguments to make(). This will allow
# a user to launch some application with their preferences,
# not with default preferences.
# *) Allow user to change the XML file from inside the launcher


########################################################################
class LauncherButton(QPushButton):
    """
    """

    #----------------------------------------------------------------------
    def __init__(self, linked_persistent_model_index, *args):
        """Constructor"""
        
        super(LauncherButton, self).__init__(*args)
        
        self.p_model_index = linked_persistent_model_index;

########################################################################
class LauncherTabPage(Qt.QWidget):
    """
    """

    #----------------------------------------------------------------------
    def __init__(self, linked_persistent_model_index, *args):
        """Constructor"""
        
        Qt.QWidget.__init__(self, *args)
        
        self.p_model_index = linked_persistent_model_index;
    
    

########################################################################
class LauncherModel(Qt.QStandardItemModel):
    """
    """

    #----------------------------------------------------------------------
    def __init__(self, *args):
        """Constructor"""
        
        Qt.QStandardItemModel.__init__(self, *args)
    
        self.item_color_for_page = Qt.Qt.black
        self.item_color_for_app  = Qt.Qt.red
        
        doc = self.open_XML_hierarchy_file()
    
        self.nRows = 0
        self.construct_tree_model(doc.firstChild()) # Recursively search through 
        # the XML file to build the corresponding tree structure.
        
        self.setHeaderData(0, Qt.Qt.Horizontal, 
                           Qt.QVariant(Qt.QString('Page Hierarchy')),
                           Qt.Qt.DisplayRole)
        
    #----------------------------------------------------------------------
    def construct_tree_model(self, dom, parent_item = None, 
                             child_index = None):
        """
        """
        
        info = self.getItemInfo(dom)
        
        if info:
            dispName = str(info['dispName'])
            
            item = LauncherModelItem(dispName)
            item.name = info['name']
            item.item_type = info['type']
            item.abs_dir_path = info['abs_dir_path']
            item.module_name = info['module_name']
            
            if item.item_type == 'app':
                item.setForeground(Qt.QBrush(self.item_color_for_app))
            elif item.item_type == 'page':
                item.setForeground(Qt.QBrush(self.item_color_for_page))
            else:
                pass
            
            for sibling_dom in info['sibling_DOMs']:
                item.appendRow(LauncherModelItem())

            if (parent_item is not None) and (child_index is not None):
                parent_item.setChild(child_index, item)
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
        
        info = {'name':None, 'dispName':None,
                'abs_dir_path':None, 'module_name':None,
                'sibling_DOMs':[]}
        
        while not node.isNull():
            nodeName = str(node.nodeName())
            if nodeName in ('name', 'dispName', 'abs_dir_path',
                            'module_name'):
                info[nodeName] = str(node.firstChild().nodeValue())
            elif nodeName in ('page', 'app'):
                info['sibling_DOMs'].append(node)
                
            node = node.nextSibling()
    
        if info['name']:
            info['type'] = str(dom.nodeName())
        else:
            info = {}
                    
        return info
    
    #----------------------------------------------------------------------
    def open_XML_hierarchy_file(self):
        """
        """
        
        doc = QDomDocument('')
        f = Qt.QFile(aphla.conf.filename("app_launcher_hierarchy.xml"))
        if not f.open(Qt.QIODevice.ReadOnly):
            raise IOError('Failed to open file.')
        if not doc.setContent(f):
            f.close()
            raise IOError('Failed to parse file.')
        f.close()

        return doc
    
    
########################################################################
class LauncherModelItem(Qt.QStandardItem):
    """
    """

    #----------------------------------------------------------------------
    def __init__(self, *args):
        """Constructor"""
        
        Qt.QStandardItem.__init__(self, *args)
        
        # Initialized to empty, but will not be empty for both 'app' and
        # 'page' type elements
        self.name = '' 
        # Empty string for 'page'; Can be empty for 'app', too, if the
        # application being invoked is in the path
        self.abs_dir_path = '' 
        self.module_name = '' # Empty string for 'page'
        self.item_type = '' # Either 'app' or 'page'
               
        # Make the item NOT editable
        self.setFlags(self.flags() & ~Qt.Qt.ItemIsEditable)
        
########################################################################
class LauncherView(Qt.QMainWindow, Ui_MainWindow):
    """
    """

    #----------------------------------------------------------------------
    def __init__(self, model):
        """Constructor"""
        
        Qt.QMainWindow.__init__(self)
        
        self.model = model
        
        
    
        self.setupUi(self)
        
        self.splitter.setSizes(
            [self.width()*(1./5),self.width()*(4./5)])
        
        self.treeView.setModel(self.model)
        
        self.tabWidget.removeTab(0) # Remove the tab page generated
        # by Qt Designer by default.
        
        '''
        Initialization of the tab widget with the root item cannot be
        done here, since the correct width of tabWidget will not be
        available at this point. The main window needs to finish painting
        itself before the correct width can be obtained. Thus, the tab
        initialization is delayed until the paintEvent function is called,
        i.e., when it finishes painting.
        '''
        self.tab_initialized = False
        
        # Specify # of columns for pushbuttons for each row on the
        # tab page.
        self.nCol_buttons = 4
        
        self.connect(self.treeView,
                     Qt.SIGNAL('doubleClicked(const QModelIndex &)'),
                     self._act_to_click_on_treeView_item)
        self.connect(self.treeView,
                     Qt.SIGNAL('clicked(const QModelIndex &)'),
                     self._act_to_click_on_treeView_item)
    
        self.connect(self.tabWidget,
                     Qt.SIGNAL('tabCloseRequested(int)'),
                     self.closeTab);
        self.connect(self.tabWidget,
                     Qt.SIGNAL('currentChanged(int)'),
                     self._change_selection_on_tree)
        
    
    #----------------------------------------------------------------------
    def closeTab(self, tab_index):
        """ """
        
        self.tabWidget.removeTab(tab_index);
        
    
    #----------------------------------------------------------------------
    def _act_to_click_on_pushbutton(self):
        """ """
        
        pushbutton = self.sender()
        
        self._act_to_click_on_treeView_item(
            pushbutton.p_model_index)
        
    #----------------------------------------------------------------------
    def _act_to_click_on_treeView_item(self, model_index):
        """ """
        
        if model_index.isValid():
            p_model_index = Qt.QPersistentModelIndex(model_index)
        else:
            print 'Invalid model index detected.'
            return

        item = self.model.itemFromIndex(Qt.QModelIndex(p_model_index))
        

        if item.item_type == 'page':
            
            existing_tab_pages = \
                self.tabWidget.findChildren(LauncherTabPage)
            
            index_list = [p.p_model_index for p in existing_tab_pages]
            if p_model_index in index_list: # Utilize existing tab page
                temp_list_index = index_list.index(p_model_index)
                tab_index = self.tabWidget.indexOf(
                    existing_tab_pages[temp_list_index])
                # The tab indices the QTabWidget keeps record of will likely
                # change over the time. Thus we need to find the tab index
                # by searching by the QWidget.
                self.tabWidget.setCurrentIndex(tab_index)
                return
            
            new_tab_page = LauncherTabPage(p_model_index)
            
            nItems = item.rowCount()
            nRow_buttons = int(
                math.ceil(float(nItems)/self.nCol_buttons) )
            button_width = \
                self.tabWidget.width()/self.nCol_buttons - 4
        
            for i in range(nRow_buttons):
                for j in range(self.nCol_buttons):
                    iButton = i*self.nCol_buttons + j
                    if iButton >= nItems:
                        break
                    child_item = item.child(iButton)
                    new_pushbutton = LauncherButton(
                        Qt.QPersistentModelIndex(child_item.index()),
                        new_tab_page)
                    if child_item.item_type == 'app':
                        text_color = 'QPushButton {color: red}'
                    elif child_item.item_type == 'page':
                        text_color = 'QPushButton {color: black}'
                    new_pushbutton.setStyleSheet(text_color)
                    new_pushbutton.setGeometry(
                        Qt.QRect(5+j*(button_width+2), 5+i*27, 
                                 button_width, 27))
                    new_pushbutton.setText(child_item.text())
                    self.connect(new_pushbutton, Qt.SIGNAL("clicked()"),
                                 self._act_to_click_on_pushbutton)
                    
                    
            tab_index = self.tabWidget.addTab(new_tab_page, 
                                              item.text())
            self.tabWidget.setCurrentIndex(tab_index)
            
        elif item.item_type == 'app':
            
            self.emit(Qt.SIGNAL('sigAppExecutionRequested'),
                      item.module_name, item.abs_dir_path)
        
    
    #----------------------------------------------------------------------
    def _change_selection_on_tree(self, newly_selected_tab_index):
        """ """
        
        current_model_index = self.tabWidget.currentWidget().p_model_index
        
        if current_model_index.isValid():
            self.treeView.setCurrentIndex(Qt.QModelIndex(current_model_index))
        else:
            print 'Invalid model index detected.'
            return
        
    #----------------------------------------------------------------------
    def paintEvent(self, event):
        """ """
        
        if not self.tab_initialized:
            self._initTab()
            self.tab_initialized = True
            
        super(Qt.QMainWindow,self).paintEvent(event)
        
    #----------------------------------------------------------------------
    def _initTab(self):
        """ """
        
        # Initialization of the tab widget, i.e.,
        # making the tab page for the root item, by emulating
        # a clicking on the "Root" item on the tree view.
        root_item = self.model.item(0)
        self._act_to_click_on_treeView_item(root_item.index())
        
        
########################################################################
class LauncherApp(Qt.QObject):
    """ """

    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        
        Qt.QObject.__init__(self)
        
        self.app_list = []
        
        self._initModel()
        
        self._initView()
        
        self.connect(self.view, Qt.SIGNAL('sigAppExecutionRequested'),
                     self.launch_app)
            
    #----------------------------------------------------------------------
    def _initModel(self):
        """ """
        
        self.model = LauncherModel()
        
    #----------------------------------------------------------------------
    def _initView(self):
        """ """
        
        self.view = LauncherView(self.model)

    #----------------------------------------------------------------------
    def launch_app(self, app_module_name, abs_dir_path = ''):
        """ """
        
        if abs_dir_path is not '':
            sys.path.insert(0, abs_dir_path)
            
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
        #self.app_list.append(__import__(app_module_name).make())
        subprocess.Popen([app_module_name])


#----------------------------------------------------------------------
def main(args = None):
    """ """
    
    cothread.iqt(use_timer = True)
    
    app = LauncherApp()
    app.view.show()
    
    ''' # You can use this if you are NOT using cothread, instead of
    # cothread.WaitForQuit() below.
    exit_status = config.qtapp[0].exec_()
    sys.exit(exit_status)
    '''
    
    cothread.WaitForQuit()
    

#----------------------------------------------------------------------    
if __name__ == "__main__" :
    main(sys.argv)
    
