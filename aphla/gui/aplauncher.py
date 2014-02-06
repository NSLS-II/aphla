#! /usr/bin/env python

"""GUI application for launching other GUI applications

Version 1.0.0

:author: Yoshiteru Hidaka
:license:

This GUI application is a launcher program that allows users to start any
individual application they want to use with a single click on the launcher
panel.

This application also provides a hierarchical view of available applications
through which users can find and launch an application of interest. It can
also search an application by keywords.
"""

import sys, os
import os.path as osp
import errno
import time
import posixpath
from copy import copy, deepcopy
import types
from subprocess import Popen, PIPE
import traceback
import re
import shutil
from cStringIO import StringIO
import sip
sip.setapi('QString', 2)
sip.setapi('QVariant', 2)

import cothread

from PyQt4.QtCore import (
    Qt, SIGNAL, QObject, QDir, QFile, QIODevice, QTextStream, QModelIndex,
    QPersistentModelIndex, QSettings, QRect, QSize)
from PyQt4.QtGui import (
    QApplication, QFont, QWidget, QStandardItemModel, QStandardItem, QComboBox,
    QCompleter, QDialog, QMessageBox, QFileDialog, QIcon, QBrush, QTreeView,
    QAbstractItemView, QListView, QSortFilterProxyModel, QMainWindow, QMenu,
    QStackedWidget, QTabWidget, QGridLayout, QAction, QActionGroup,
    QKeySequence
)
from PyQt4.QtXml import QDomDocument

APP = None

ORIGINAL_SYS_PATH = sys.path[:]

XML_ITEM_TAG_NAME = 'item'
XML_ITEM_COMMON_PROPERTY_NAMES = ['dispName', 'desc', 'icon', 'itemType']
XML_ITEM_PROPERTY_NAME_DICT = dict(
    page=[],
    info=[],
    txt =['sourceFilepath', 'editor', 'helpHeader'],
    py  =['moduleName', 'cwd', 'args', 'editor'],
    exe =['command', 'cwd', 'sourceFilepath', 'editor', 'helpHeader'],
)
XML_ITEM_TYPE_SPECIFIC_PROP_NAMES = list(set(
    sum(XML_ITEM_PROPERTY_NAME_DICT.values(), [])))
XML_ITEM_PROPERTY_NAMES = XML_ITEM_COMMON_PROPERTY_NAMES[:] + \
    XML_ITEM_TYPE_SPECIFIC_PROP_NAMES[:]
MODEL_ITEM_PROPERTY_NAME_DICT = deepcopy(XML_ITEM_PROPERTY_NAME_DICT)
MODEL_ITEM_PROPERTY_NAMES = XML_ITEM_PROPERTY_NAMES[:]
MODEL_ITEM_PROPERTY_NAMES.remove('dispName')
MODEL_ITEM_PROPERTY_NAMES.remove('icon')
MODEL_ITEM_PROPERTY_NAMES.insert(0, 'path')
MODEL_ITEM_PROPERTY_NAMES.append('help')
COLUMN_NAME_DICT = dict(
    path='Parent Path', itemType='Item Type', command='Command',
    cwd='Working Directory', editor='Editor', sourceFilepath='Source Filepath',
    helpHeader='Help Header Type', moduleName='Module Name', args='Import Args',
    desc='Description', help='Help Text',
)
ALL_COLUMN_NAMES = ['Name'] + [COLUMN_NAME_DICT[prop_name]
                               for prop_name in MODEL_ITEM_PROPERTY_NAMES]
DEFAULT_VISIBLE_COL_NAMES = ['Name', 'Item Type', 'Command', 'Help Text',
                             'Description']
PERM_VISIBLE_COL_NAMES = ['Name']
DEFAULT_XML_ITEM = dict(
    dispName='', desc='', icon='page', itemType='page', command='', cwd='',
    editor='gedit', sourceFilepath='', helpHeader='python', moduleName='',
    args='',
)
ICONS = dict(page=':/folder.png', info=':/info_item.png', txt=':/txt_item.png',
             py=':/python.png', gui_app=':/generic_app.png',
             cmd_app=':/cmd_app.png', css=':/css48.png',
             mfile=':/matlab_mfile.png')
DEFAULT_ICON_NAMES = dict(page='page', info='info', txt='txt', py='py',
                          exe='gui_app')
DEFAULT_ICONS = {k: ICONS[v] for (k,v) in DEFAULT_ICON_NAMES.iteritems()}
ITEM_PROPERTIES_DIALOG_OBJECTS = dict(
    dispName = 'lineEdit_dispName',
    itemType = 'comboBox_itemType',
    icon     = 'pushButton_icon',
    page= dict(desc='plainTextEdit_page_description'),
    info= dict(desc='plainTextEdit_info_description'),
    txt = dict(sourceFilepath='lineEdit_txt_src_filepath',
               browse        ='pushButton_txt_browse',
               editor        ='comboBox_txt_editor',
               helpHeader    ='comboBox_txt_helpHeaderType',
               help          ='plainTextEdit_txt_help',
               desc          ='plainTextEdit_txt_description',),
    py  = dict(moduleName='comboBox_py_moduleName',
               cwd       ='lineEdit_py_workingDir',
               browseWD  ='pushButton_py_browseWD',
               args      ='lineEdit_py_args',
               editor    ='comboBox_py_editor',
               help      ='plainTextEdit_py_help',
               desc      ='plainTextEdit_py_description',),
    exe = dict(command     ='comboBox_exe_command',
               cwd         ='lineEdit_exe_workingDir',
               browseWD    ='pushButton_exe_browseWD',
               sourceFilepath='lineEdit_exe_src_filepath',
               browse        ='pushButton_exe_browse',
               editor        ='comboBox_exe_editor',
               helpHeader    ='comboBox_exe_helpHeaderType',
               help          ='plainTextEdit_exe_help',
               desc          ='plainTextEdit_exe_description',),
)
ITEM_PROP_DLG_OBJ_ENABLED_EXE_NONEMPTY_SRC_FILEPATH = [
    'comboBox_exe_editor', 'comboBox_exe_helpHeaderType']

ITEM_COLOR_PAGE = Qt.black
ITEM_COLOR_INFO = Qt.black
ITEM_COLOR_PY   = Qt.blue
ITEM_COLOR_EXE  = Qt.blue
ITEM_COLOR_TXT  = Qt.magenta

# Forward slash '/' will be used as a file path separator for both
# in Linux & Windows. Even if '/' is used in Windows, shutil and os functions
# still properly work.
# QDir.homePath() will return the home path string using '/' even on Windows.
# Therefore, '/' is being used consistently in this code.
#
# By the way, the QFile document says "QFile expects the file separator to be
# '/' regardless of operating system.
# The use of other separators (e.g., '\') is not supported."
# However, on Windows, using '\' still works fine.
SEPARATOR = '/' # used as system file path separator as well as launcher page
                # path separator
HOME_PATH = str(QDir.homePath())
DOT_HLA_QFILEPATH = HOME_PATH + SEPARATOR + '.hla'
SYSTEM_XML_FILENAME    = 'us_nsls2_launcher_hierarchy.xml'
USER_XML_FILENAME      = 'user_launcher_hierarchy.xml'
USER_TEMP_XML_FILENAME = 'user_launcher_hierarchy.xml.temp'
USER_XML_FILEPATH      = DOT_HLA_QFILEPATH + SEPARATOR + USER_XML_FILENAME
USER_TEMP_XML_FILEPATH = DOT_HLA_QFILEPATH + SEPARATOR + USER_TEMP_XML_FILENAME
USER_MODIFIABLE_ROOT_PATH = '/root/Favorites'

import utils.gui_icons
from Qt4Designer_files.ui_launcher import Ui_MainWindow
from Qt4Designer_files.ui_launcher_item_properties import Ui_Dialog
from Qt4Designer_files.ui_launcher_restore_hierarchy import Ui_Dialog \
     as Ui_Dialog_restore_hie
from Qt4Designer_files.ui_icon_picker import Ui_Dialog as Ui_Dialog_icon

import aphla as ap
from aphla.gui.utils.orderselector import ColumnsDialog
from aphla.gui.utils import xmltodict

MACHINES_FOLDERPATH = os.path.dirname(os.path.abspath(ap.machines.__file__))

## TODO ##
# *) Highlight the search matching portion of texts in QTreeView and QListView
# *) Bypass XML tree construction, if XML file not changed. Load
# directly the tree model data for faster start-up.
# *) Use database for in-code help texts for performance
# *) Implement page jumping with the path buttons hidden under
# the path line editbox.
# *) path auto completion & naviation from path line editbox
# *) More thorough separate search window
# *) Add PYTHONPATH editor

## FIXIT
# *) Header not visible in main Tree View, if no item exists

########################################################################
class StartDirPaths():
    """"""

    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""

        cwd = os.getcwd()

        self.restore_hierarchy              = cwd
        self.item_properties_workingDir     = cwd
        self.item_properties_sourceFilepath = cwd
        self.export_user_xml                = cwd
        self.import_user_xml                = cwd


START_DIRS = StartDirPaths()


########################################################################
class SearchModel(QStandardItemModel):
    """
    """

    #----------------------------------------------------------------------
    def __init__(self, model, *args):
        """Constructor"""

        QStandardItemModel.__init__(self, *args)

        self.setHorizontalHeaderLabels(model.headerLabels)

        rootItem = LauncherModelItem('searchRoot')
        #rootItem.ItemType = 'page'
        rootItem.path = SEPARATOR + rootItem.dispName
        #rootItem.command = ''
        #rootItem.workingDir = ''
        #rootItem.importArgs = ''
        #rootItem.useImport = False
        #rootItem.singleton = False
        rootItem.updateIconAndColor()
        self.setItem(0, rootItem)

########################################################################
class LauncherModel(QStandardItemModel):
    """
    """

    #----------------------------------------------------------------------
    def __init__(self, *args):
        """Constructor"""

        QStandardItemModel.__init__(self, *args)

        self.headerLabels = ALL_COLUMN_NAMES
        self.setHorizontalHeaderLabels(self.headerLabels)
        self.setColumnCount(len(self.headerLabels))

        self.pathList = []
        self.pModelIndList = []

        # Initial list population will occur when a
        # LauncherModelItemPropertiesDialog is created for the first time.
        self.commandList    = []
        self.moduleNameList = []

        ## First, parse system XML file and construct a tree model
        system_XML_Filepath = os.path.join(MACHINES_FOLDERPATH,
                                           SYSTEM_XML_FILENAME)
        system_XML_Filepath.replace('\\','/') # On Windows, convert Windows
        # path separator ('\\') to Linux path separator ('/')
        #
        self.nRows = 0
        doc = self.open_XML_HierarchyFile(system_XML_Filepath)
        self.construct_tree_model(doc.firstChild()) # Recursively search through
        # the XML file to build the corresponding tree structure.

        ## Then parse user XML file and append the data to the tree model
        doc = self.open_XML_HierarchyFile(USER_XML_FILEPATH)
        rootItem = self.item(0,0)
        self.construct_tree_model(doc.firstChild(),
                                  parent_item=rootItem,
                                  child_index=rootItem.rowCount())

        # Set up completer for search
        self.completer = QCompleter()
        self.completer.setCompletionRole(Qt.DisplayRole)
        self.completer.setCompletionColumn = 0
        self.completer.setCaseSensitivity(False)
        self.completer.setCompletionMode(QCompleter.PopupCompletion)
        self.updateCompleterModel(SEPARATOR + 'root')

        # Create search indexes
        self.search_index_item_list = []
        self.search_index_path_list = []
        self.search_index_name_list = []
        self.search_index_desc_list = []
        self.search_index_help_list = []
        self.update_search_index()

    #----------------------------------------------------------------------
    def update_search_index(self, parent_item=None, index_item=None,
                            index_path=None, index_name=None, index_desc=None,
                            index_help=None):
        """
        """

        col_ind_path = self.headerLabels.index('Parent Path')
        col_ind_name = self.headerLabels.index('Name')
        col_ind_desc = self.headerLabels.index('Description')
        col_ind_help = self.headerLabels.index('Help Text')

        if index_item is None: index_item = []
        if index_path is None: index_path = []
        if index_name is None: index_name = []
        if index_desc is None: index_desc = []
        if index_help is None: index_help = []

        if parent_item is None:
            rootItem    = self.item(0,0)
            parent_item = rootItem

            root = True
        else:
            root = False

        for row in range(parent_item.rowCount()):
            index_item.append(parent_item.child(row))
            index_path.append(parent_item.child(row,col_ind_path).text().lower())
            index_name.append(parent_item.child(row,col_ind_name).text().lower())
            index_desc.append(parent_item.child(row,col_ind_desc).text().lower())
            index_help.append(parent_item.child(row,col_ind_help).text().lower())
            if parent_item.child(row).hasChildren():
                self.update_search_index(parent_item=parent_item.child(row),
                                         index_item=index_item,
                                         index_path=index_path,
                                         index_name=index_name,
                                         index_desc=index_desc,
                                         index_help=index_help)

        if root:
            self.search_index_item_list = index_item
            self.search_index_path_list = index_path
            self.search_index_name_list = index_name
            self.search_index_desc_list = index_desc
            self.search_index_help_list = index_help

    #----------------------------------------------------------------------
    def get_help_header_text(self, item):
        """"""

        if item.itemType == 'txt':
            f = item.sourceFilepath
            header_type = item.helpHeader
        elif item.itemType == 'py':
            try:
                sys.path = ORIGINAL_SYS_PATH[:]
                if item.cwd not in ('','N/A'):
                    cwd = _subs_tilde_with_home(item.cwd)
                    if osp.exists(cwd):
                        print 'Changing directory to {0:s}'.format(cwd)
                        os.chdir(cwd)
                        if cwd not in sys.path:
                            sys.path.insert(0, cwd)
                    else:
                        print 'No such directory exist: {0:s}'.format(cwd)
                        print ('Trying to import "{0:s}" without cd...'.
                               format(item.moduleName))

                topLevelModule = __import__(item.moduleName)
                submod_list = item.moduleName.split('.')
                if len(submod_list) == 1:
                    f = topLevelModule.__file__
                else:
                    m = topLevelModule
                    for submod in submod_list[1:]:
                        m = getattr(m, submod)
                    f = m.__file__
                if f.endswith('.pyc'): f = f[:-1]
            except ImportError:
                f = ''
            header_type = 'python'
        elif item.itemType == 'exe':
            f = item.sourceFilepath
            header_type = item.helpHeader
        else:
            return 'N/A'

        help_text = ''

        if (header_type == 'None') or (f == ''):
            pass

        elif header_type == 'python':
            help_header_quote = ''
            with open(f, 'r') as fobj:
                for line in fobj:
                    if help_header_quote == '':
                        line = line.lstrip()
                        if line.startswith('#') or (line == ''):
                            pass
                        elif line.startswith(('"""', "'''")):
                            help_header_quote = line[:3]
                            help_text = line[3:]
                            if help_header_quote in help_text:
                                i = help_text.index(help_header_quote)
                                help_text = help_text[:i]
                                break
                        else:
                            break
                    else:
                        if ('"""' in line) or ("'''" in line):
                            i = line.index(help_header_quote)
                            help_text += line[:i]
                            break
                        else:
                            help_text += line

        elif header_type == 'matlab':
            in_header_quote = False
            with open(f, 'r') as fobj:
                for line in fobj:
                    line = line.lstrip()
                    if not in_header_quote:
                        if line == '':
                            pass
                        elif line.startswith('%'):
                            in_header_quote = True
                            help_text = line[1:]
                        else:
                            break
                    else:
                        if line.startswith('%'):
                            help_text += line[1:]
                        else:
                            break

        elif header_type == 'CSS':

            with open(f, 'r') as fobj:
                css_text = fobj.read()

            source_file_dirpath = osp.dirname(f)

            source_dict = xmltodict.parse(css_text)
            help_button_widget = [
                w for w in source_dict['display']['widget']
                if w.has_key('text') \
                and isinstance(w['text'], (str, unicode)) \
                and (w['text'].strip().lower() == 'help') \
                and w.has_key('@typeId') \
                and (w['@typeId'] ==
                     'org.csstudio.opibuilder.widgets.ActionButton') \
                and w.has_key('actions') \
                and w['actions'].has_key('action') \
                and w['actions']['action'].has_key('@type') \
                and (w['actions']['action']['@type'] == 'OPEN_DISPLAY') \
                and w['actions']['action'].has_key('path')
            ]

            if len(help_button_widget) == 0:
                help_button_widget = None
            elif len(help_button_widget) == 1:
                help_button_widget = help_button_widget[0]
            else:
                print ('WARNING: multiple help buttons found in specified CSS '
                       'source OPI file.')
                print ('Help text being displayed corresponds to the first one '
                       'detected.')
                help_button_widget = help_button_widget[0]

            if help_button_widget is None:
                help_text = ''
            else:
                help_filename = help_button_widget['actions']['action']['path']
                help_filepath = osp.join(source_file_dirpath,
                                         help_filename)
                if not osp.exists(help_filepath):
                    print ('WARNING: Found linked help filepath does not '
                           'exist: {0:s}'.format(help_filepath))
                    help_text = ''
                else:
                    with open(help_filepath, 'r') as fobj:
                        raw_help_text = fobj.read()

                    help_dict = xmltodict.parse(raw_help_text)
                    help_label_widget = [
                        w['widget'] for w in help_dict['display']['widget']
                        if (w['@typeId'] ==
                            'org.csstudio.opibuilder.widgets.groupingContainer') \
                        and w['widget'].has_key('@typeId') \
                        and (w['widget']['@typeId'] ==
                             'org.csstudio.opibuilder.widgets.Label')
                        and w['widget'].has_key('text')
                    ]

                    if len(help_label_widget) == 0:
                        help_label_widget = None
                    elif len(help_label_widget) == 1:
                        help_label_widget = help_label_widget[0]
                    else:
                        print ('WARNING: multiple help labels found in '
                               'linked help CSS OPI file.')
                        print ('Help text being displayed corresponds to the '
                               'first one detected.')
                        help_label_widget = help_label_widget[0]

                    if help_label_widget is None:
                        help_text = ''
                    else:
                        help_text = help_label_widget['text']

        else:
            raise ValueError('Unexpected help header type: {0:s}'.
                             format(header_type))

        return help_text

    #----------------------------------------------------------------------
    def construct_tree_model(self, dom, parent_item = None,
                             child_index = None):
        """
        """

        info = self.getItemInfo(dom)

        if info:
            dispName = str(info['dispName'])

            item = LauncherModelItem(dispName)

            for prop_name in MODEL_ITEM_PROPERTY_NAMES:
                if prop_name != 'path':
                    setattr(item, prop_name, 'N/A')

            item.path     = item.path + item.dispName # This assignment is
            # meaningful only for "/root".
            item.desc     = info['desc']
            item.icon     = info['icon']
            item.itemType = info['itemType']

            for prop_name in MODEL_ITEM_PROPERTY_NAME_DICT[item.itemType]:
                setattr(item, prop_name, info[prop_name])

            if item.helpHeader == '':
                item.helpHeader = 'None'

            # Get help text at the header of the source file
            item.help = self.get_help_header_text(item)

            item.updateIconAndColor()

            for sibling_dom in info['sibling_DOMs']:
                item.appendRow(LauncherModelItem())

            if (parent_item is not None) and (child_index is not None):
                item.path = parent_item.path + item.path
                if item.path not in self.pathList:
                    self.pathList.append(item.path)
                else:
                    raise ValueError('Duplicate path found: '+item.path)

                if item.path.startswith(USER_MODIFIABLE_ROOT_PATH+SEPARATOR):
                    item.setEditable(True)
                else:
                    item.setEditable(False)

                parent_item.setChild(child_index, 0, item)
                for (ii,prop_name) in enumerate(MODEL_ITEM_PROPERTY_NAMES):
                    p = getattr(item,prop_name)
                    #if not isinstance(p,str):
                        #p = str(p)
                    parent_item.setChild(child_index, ii+1,QStandardItem(p))

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
    def _getXMLPropNames(self, itemType):
        """"""

        if itemType in ('page', 'info'):
            return XML_ITEM_COMMON_PROPERTY_NAMES
        else:
            return XML_ITEM_COMMON_PROPERTY_NAMES[:] + \
                   XML_ITEM_PROPERTY_NAME_DICT[itemType]

    #----------------------------------------------------------------------
    def constructXMLElementsFromModel(self, doc, parentModelItem, parentDOMElement):
        """"""

        childItemList = [parentModelItem.child(i,0) for i in
                         range(parentModelItem.rowCount())]
        for childItem in childItemList:
            childElement = doc.createElement(XML_ITEM_TAG_NAME)

            itemType = childItem.itemType

            for prop_name in self._getXMLPropNames(itemType):
                p = getattr(childItem,prop_name)
                #if not isinstance(p,str):
                    #p = str(p)
                if p == 'N/A': p = ''
                elem = doc.createElement(prop_name)
                elemNodeText = doc.createTextNode(p)
                elem.appendChild(elemNodeText)
                childElement.appendChild(elem)
                #if (prop_name == 'itemType') and (p == 'page'):
                    #break

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
        prop_name_list = XML_ITEM_COMMON_PROPERTY_NAMES
        for prop_name in prop_name_list:
        #for (ii,prop_name) in enumerate(XML_ITEM_PROPERTY_NAMES):
            p = getattr(rootModelItem,prop_name)
            #if not isinstance(p,str):
                #p = str(p)
            if p == 'N/A': p = ''
            elem = doc.createElement(prop_name)
            elemNodeText = doc.createTextNode(p)
            elem.appendChild(elemNodeText)
            modelRootDOMElement.appendChild(elem)
            #if (prop_name == 'itemType') and (p == 'page'):
                #break


        # Append the XML element corresponding to the root model item as a child of
        # the XML root element
        xmlRootDOMElement.appendChild(modelRootDOMElement)

        # Construct all the child elements recursively based on all the child model
        # items of the given root model item
        self.constructXMLElementsFromModel(doc, rootModelItem, modelRootDOMElement)

        # Finally, append the XML root element to the DOM object
        doc.appendChild(xmlRootDOMElement)


        f = QFile(XML_Filepath)

        if not f.open(QIODevice.WriteOnly | QIODevice.Text):
            raise IOError('Failed to open ' + XML_Filepath + ' for writing.')

        stream = QTextStream(f)

        indent = 4
        stream << doc.toString(indent)

        f.close()



    #----------------------------------------------------------------------
    def open_XML_HierarchyFile(self, XML_Filepath):
        """
        """


        f = QFile(XML_Filepath)
        if not f.exists():
            # If the system XML file cannot be located, stop here.
            XML_Filename = os.path.split(XML_Filepath)
            if SYSTEM_XML_FILENAME == XML_Filename:
                raise OSError(XML_Filepath + ' does not exist.')

            # If the user XML file cannot be found, then create an empty one in
            # ".hla" directory under the user home directory.

            # This section of code creates ".hla" directory under th user home directory,
            # if it does not already exist. This method assures no race condtion will happen
            # in the process of creating the new directory.
            try:
                os.makedirs(DOT_HLA_QFILEPATH)
            except OSError, e:
                if e.errno != errno.EEXIST:
                    raise OSError('Failed to create .hla directory')

            # Create an empty user XML file
            rootModelItem = LauncherModelItem('Favorites')
            self.writeToXMLFile(XML_Filepath, rootModelItem)
            # Make sure that the file has been successfully created.
            if not f.exists():
                raise IOError('Failed to create an empty User XML file')

        if not f.open(QIODevice.ReadOnly):
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
        self.pathElementModel = QStandardItemModel(
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
            self.pModelIndList = [QPersistentModelIndex(self.indexFromItem(rootItem))]
            parentItem = rootItem

        for i in range(parentItem.rowCount()):
            childItem = parentItem.child(i,0)
            if childItem.path not in self.pathList:
                self.pathList.append(childItem.path)
            else:
                raise ValueError('Duplicate path found: ' + childItem.path)
            self.pModelIndList.append(QPersistentModelIndex(self.indexFromItem(childItem)))

            self.updatePathLookupLists(childItem)



    #----------------------------------------------------------------------
    def pModelIndexFromPath(self, path):
        """"""

        index = self.pathList.index(path)

        return self.pModelIndList[index]


########################################################################
class LauncherRestoreHierarchyDialog(QDialog, Ui_Dialog_restore_hie):
    """"""

    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""

        QDialog.__init__(self)

        self.setupUi(self)

        self.start_dirs = START_DIRS

        self.checkBox_backup.setChecked(False)
        self.lineEdit_backup_filepath.setEnabled(False)

        self.connect(self.pushButton_browse, SIGNAL('clicked()'),
                     self.openFileSelector)
        self.connect(self.checkBox_backup, SIGNAL('stateChanged(int)'),
                     self._updateEnableStates)

    #----------------------------------------------------------------------
    def _updateEnableStates(self, qtCheckState):
        """"""

        if qtCheckState == Qt.Checked:
            self.lineEdit_backup_filepath.setEnabled(True)
        elif qtCheckState == Qt.Unchecked:
            self.lineEdit_backup_filepath.setEnabled(False)
        else:
            raise ValueError('Unexpected Qt CheckedState value.')

    #----------------------------------------------------------------------
    def accept(self):
        """"""

        if self.checkBox_backup.isChecked():
            msgBox = QMessageBox()
            backup_filepath = self.lineEdit_backup_filepath.text()
            if osp.exists(osp.dirname(backup_filepath)):
                shutil.copy(USER_XML_FILEPATH, backup_filepath)
                msgBox.setText('Successfully backed up the current hierarchy to:')
                msgBox.setInformativeText('{0:s}'.format(backup_filepath))
                msgBox.setIcon(QMessageBox.Information)
                msgBox.exec_()
            else:
                msgBox.setText('Invalid file path specified:')
                msgBox.setInformativeText('{0:s} does not exist'.format(
                    osp.dirname(backup_filepath)))
                msgBox.setIcon(QMessageBox.Critical)
                msgBox.exec_()
                return

        super(LauncherRestoreHierarchyDialog, self).accept()
        # will hide the dialog

    #----------------------------------------------------------------------
    def reject(self):
        """"""

        super(LauncherRestoreHierarchyDialog, self).reject()
        # will hide the dialog

    #----------------------------------------------------------------------
    def openFileSelector(self):
        """"""

        caption = 'Save Current User Hierarchy File'
        selected_filter_str = ('XML files (*.xml)')
        filter_str = ';;'.join([selected_filter_str, 'All files (*)'])
        save_filepath = QFileDialog.getSaveFileName(
            caption=caption, directory=self.start_dirs.restore_hierarchy,
            filter=filter_str)
        if not save_filepath:
            return

        self.start_dirs.restore_hierarchy = osp.dirname(save_filepath)

        self.lineEdit_backup_filepath.setText(save_filepath)

########################################################################
class IconPickerDialog(QDialog, Ui_Dialog_icon):
    """"""

    #----------------------------------------------------------------------
    def __init__(self, item):
        """Constructor"""

        QDialog.__init__(self)

        self.setupUi(self)

        self.item = item

        self.setWindowTitle('Pick an Icon')

        self.model = IconPickerModel()

        self.listView.setModel(self.model)
        self.listView.setViewMode(QListView.IconMode)
        self.listView.setWrapping(True)
        self.listView.setIconSize(QSize(50,50))
        self.listView.setGridSize(QSize(70,70))
        self.listView.setUniformItemSizes(True)
        self.listView.setResizeMode(QListView.Adjust)
        self.listView.setMovement(QListView.Static)

    #----------------------------------------------------------------------
    def accept(self):
        """"""

        self.item.icon = self.model.itemFromIndex(
            self.listView.selectedIndexes()[0]).toolTip()

        super(IconPickerDialog, self).accept() # will hide the dialog

    #----------------------------------------------------------------------
    def reject(self):
        """"""

        super(IconPickerDialog, self).reject() # will hide the dialog


########################################################################
class IconPickerModel(QStandardItemModel):
    """"""

    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""

        QStandardItemModel.__init__(self)

        for i, (k, v) in enumerate(ICONS.iteritems()):
            item = QStandardItem()
            item.setToolTip(k)
            item.setIcon(QIcon(v))
            self.insertRow(i, item)

########################################################################
class LauncherModelItemPropertiesDialog(QDialog, Ui_Dialog):
    """"""

    #----------------------------------------------------------------------
    def __init__(self, model, selectedItem, parentItem, *args):
        """Constructor"""

        QDialog.__init__(self, *args)

        self.setupUi(self)

        self.setWindowFlags(Qt.Window) # To add Maximize & Minimize buttons

        self.model = model
        self.origItem = selectedItem
        self.item     = selectedItem.shallowCopy()

        # Update the list of command strings and module names that already
        #exist in the model
        itemList = [model.itemFromIndex(QModelIndex(pInd))
                    for pInd in model.pModelIndList]
        model.commandList    = list(set([item.command    for item in itemList
                                         if item.command    != 'N/A']))
        model.moduleNameList = list(set([item.moduleName for item in itemList
                                         if item.moduleName != 'N/A']))

        #partitionedStrings = self.item.path.rpartition(SEPARATOR)
        #self.parentPath = partitionedStrings[0]
        if parentItem is not None:
            self.parentPath = parentItem.path
        else:
            self.parentPath = SEPARATOR
        self.lineEdit_parentPath.setText(self.parentPath)

        # Create list of existing paths to be compared with a new path.
        self.existingPathList = model.pathList[:]
        # If this dialog is created for modifying an existing item, you must
        # remove the path of this item from the list.
        if self.item.path in self.existingPathList:
            self.existingPathList.remove(self.item.path)

        itemType = self.item.itemType
        propNameList = ['dispName', 'itemType', 'icon']
        objNameList = [ITEM_PROPERTIES_DIALOG_OBJECTS[k] for k in propNameList]
        propNameList += ITEM_PROPERTIES_DIALOG_OBJECTS[itemType].keys()
        objNameList  += [ITEM_PROPERTIES_DIALOG_OBJECTS[itemType][k] for k in
                         ITEM_PROPERTIES_DIALOG_OBJECTS[itemType]]

        for (propName, objName) in zip(propNameList, objNameList):
            obj = getattr(self, objName)
            if objName.startswith('lineEdit'):
                obj.setText(getattr(self.item, propName))
            elif objName.startswith('comboBox'):

                if propName == 'command':
                    obj.addItems(model.commandList)
                elif propName == 'moduleName':
                    obj.addItems(model.moduleNameList)

                if propName != 'itemType':
                    search_string = getattr(self.item, propName)
                else:
                    search_string = self._getDescriptiveItemType(
                        getattr(self.item, propName))

                if search_string == '':
                    obj.setCurrentIndex(0)
                else:
                    matchedInd = obj.findText(search_string,
                                              Qt.MatchExactly)

                    # If no match found, try case-insensitive search
                    if matchedInd == -1:
                        matchedInd = obj.findText(search_string,
                                                  Qt.MatchFixedString)

                    if matchedInd != -1:
                        obj.setCurrentIndex(matchedInd)
                    else:
                        print 'No matching item found in {0:s}'.format(objName)
                        search_string = DEFAULT_XML_ITEM[propName]
                        print ('Using default value of "{0:s}" for "{1:s}"'.
                               format(search_string, propName))
                        matchedInd = obj.findText(search_string,
                                                  Qt.MatchExactly)

                        if matchedInd == -1:
                            raise ValueError('Default value not found in combobox choices.')
                        else:
                            obj.setCurrentIndex(matchedInd)

            elif objName.startswith('plainTextEdit'):
                if objName.endswith('description'):
                    obj.setProperty('plainText', self.item.desc)
                elif objName.endswith('help'):
                    obj.setProperty('plainText', self.item.help)
                else:
                    raise ValueError('Unexpected object name: {0:s}'.
                                     format(objName))

            elif objName.startswith('pushButton'):
                if objName == 'pushButton_icon':
                    obj.setIcon(QIcon(ICONS[self.item.icon]))
                    obj.setIconSize(QSize(50,50))
                    obj.setToolTip(self.item.icon)
                else:
                    pass
            else:
                raise ValueError('Unexpected object name: {0:s}'.
                                 format(objName))

        self.connect(self.comboBox_itemType,
                     SIGNAL('currentIndexChanged(const QString &)'),
                     self.switchItemSpecificPropObjects)
        self.connect(self.lineEdit_exe_src_filepath,
                     SIGNAL('textChanged(const QString &)'),
                     self._updateEnableStates)
        self.connect(self.pushButton_txt_browse, SIGNAL('clicked()'),
                     self._getExistingFile)
        self.connect(self.pushButton_py_browseWD, SIGNAL('clicked()'),
                     self._getExistingDir)
        self.connect(self.pushButton_exe_browse, SIGNAL('clicked()'),
                     self._getExistingFile)
        self.connect(self.pushButton_exe_browseWD, SIGNAL('clicked()'),
                     self._getExistingDir)
        self.connect(self.lineEdit_exe_src_filepath,
                     SIGNAL('editingFinished()'),
                     self._updateHelpTxt_src_lineEdit)
        self.connect(self.lineEdit_txt_src_filepath,
                     SIGNAL('editingFinished()'),
                     self._updateHelpTxt_src_lineEdit)
        self.connect(self.comboBox_exe_helpHeaderType,
                     SIGNAL('currentIndexChanged(const QString &)'),
                     self._updateHelpTxt_combo_helpHeader)
        self.connect(self.comboBox_txt_helpHeaderType,
                     SIGNAL('currentIndexChanged(const QString &)'),
                     self._updateHelpTxt_combo_helpHeader)
        self.connect(self.comboBox_py_moduleName,
                     SIGNAL('currentIndexChanged(const QString &)'),
                     self._updateHelpTxt_combo_moduleName)
        self.connect(self.lineEdit_py_workingDir, SIGNAL('editingFinished()'),
                     self._updateHelpTxt_py_cwd_lineEdit)
        self.connect(self.pushButton_icon, SIGNAL('clicked()'),
                     self.showIconList)

        self.isItemPropertiesModifiable = self.item.path.startswith(
            USER_MODIFIABLE_ROOT_PATH+SEPARATOR)
        # Adding SEPARATOR at the end of USER_MODIFIABLE_ROOT_PATH is essential
        # to exclude USER_MODIFIABLE_ROOT_PATH itself from modifiable item list

        self.switchItemSpecificPropObjects(self.item.itemType,
                                           use_default_icon=False)

    #----------------------------------------------------------------------
    def showIconList(self):
        """"""

        p = IconPickerDialog(self.item)
        p.exec_()

        obj = getattr(self, ITEM_PROPERTIES_DIALOG_OBJECTS['icon'])
        obj.setIcon(QIcon(ICONS[self.item.icon]))
        obj.setToolTip(self.item.icon)

    #----------------------------------------------------------------------
    def _getExistingDir(self):
        """"""

        if self.sender() == self.pushButton_exe_browseWD:
            receiving_lineEdit = self.lineEdit_exe_workingDir
        elif self.sender() == self.pushButton_py_browseWD:
            receiving_lineEdit = self.lineEdit_py_workingDir
        else:
            raise ValueError('Unexpected sender: {0:s}'.
                             format(self.sender().__repr__()))

        caption = 'Select Working Directory'
        if osp.exists(receiving_lineEdit.text()):
            starting_dir_path = receiving_lineEdit.text()
        else:
            starting_dir_path = START_DIRS.item_properties_workingDir
        dir_path = QFileDialog.getExistingDirectory(
            self, caption, starting_dir_path)

        if not dir_path:
            return

        START_DIRS.item_properties_workingDir = dir_path

        receiving_lineEdit.setText(dir_path)

        if self.item.itemType == 'py':
            self.item.cwd = dir_path
            help_text = self.model.get_help_header_text(self.item)
            self.plainTextEdit_py_help.setProperty('plainText', help_text)

    #----------------------------------------------------------------------
    def _getExistingFile(self):
        """"""

        if self.sender() == self.pushButton_exe_browse:
            receiving_lineEdit = self.lineEdit_exe_src_filepath

        elif self.sender() == self.pushButton_txt_browse:
            receiving_lineEdit = self.lineEdit_txt_src_filepath
        else:
            raise ValueError('Unexpected sender: {0:s}'.
                             format(self.sender().__repr__()))

        caption = 'Select Source File'
        if osp.exists(receiving_lineEdit.text()):
            starting_dir_path = osp.dirname(receiving_lineEdit.text())
        else:
            starting_dir_path = START_DIRS.item_properties_sourceFilepath

        all_files_filter_str = 'All files (*)'
        filepath = QFileDialog.getOpenFileName(
            caption=caption, directory=starting_dir_path,
            filter=all_files_filter_str)

        if not filepath:
            return

        START_DIRS.item_properties_sourceFilepath = osp.dirname(filepath)

        receiving_lineEdit.setText(filepath)

        self._updateHelpTxt_browse(filepath)

    #----------------------------------------------------------------------
    def _updateHelpTxt_py_cwd_lineEdit(self):
        """"""

        self.item.cwd = self.lineEdit_py_workingDir.text()
        help_text = self.model.get_help_header_text(self.item)
        self.plainTextEdit_py_help.setProperty('plainText', help_text)

    #----------------------------------------------------------------------
    def _updateHelpTxt_browse(self, new_src_filepath):
        """"""

        if self.item.itemType == 'exe':
            plainTextEdit = self.plainTextEdit_exe_help
            self.item.helpHeader = self.comboBox_exe_helpHeaderType.currentText()
        elif self.item.itemType == 'txt':
            plainTextEdit = self.plainTextEdit_txt_help
            self.item.helpHeader = self.comboBox_txt_helpHeaderType.currentText()
        else:
            raise ValueError('Unexpected itemType: {0:s}'.
                             format(self.item.itemType))

        if osp.exists(new_src_filepath):
            self.item.sourceFilepath = new_src_filepath
            help_text = self.model.get_help_header_text(self.item)
        else:
            help_text = ''

        plainTextEdit.setProperty('plainText', help_text)

    #----------------------------------------------------------------------
    def _updateHelpTxt_src_lineEdit(self):
        """"""

        if self.item.itemType == 'exe':
            plainTextEdit = self.plainTextEdit_exe_help
            self.item.helpHeader = self.comboBox_exe_helpHeaderType.currentText()
            new_src_filepath = self.lineEdit_exe_src_filepath.text()
        elif self.item.itemType == 'txt':
            plainTextEdit = self.plainTextEdit_txt_help
            self.item.helpHeader = self.comboBox_txt_helpHeaderType.currentText()
            new_src_filepath = self.lineEdit_txt_src_filepath.text()
        else:
            raise ValueError('Unexpected itemType: {0:s}'.
                             format(self.item.itemType))

        if osp.exists(new_src_filepath):
            self.item.sourceFilepath = new_src_filepath
            help_text = self.model.get_help_header_text(self.item)
        else:
            help_text = ''

        plainTextEdit.setProperty('plainText', help_text)

    #----------------------------------------------------------------------
    def _updateHelpTxt_combo_helpHeader(self, helpHeaderType):
        """"""

        self.item.helpHeader = helpHeaderType

        if self.item.itemType == 'exe':
            plainTextEdit = self.plainTextEdit_exe_help
        elif self.item.itemType == 'txt':
            plainTextEdit = self.plainTextEdit_txt_help
        else:
            raise ValueError('Unexpected itemType: {0:s}'.
                             format(self.item.itemType))

        help_text = self.model.get_help_header_text(self.item)

        plainTextEdit.setProperty('plainText', help_text)

    #----------------------------------------------------------------------
    def _updateHelpTxt_combo_moduleName(self, moduleName):
        """"""

        self.item.moduleName = self.comboBox_py_moduleName.currentText()
        self.item.cwd = self.lineEdit_py_workingDir.text()

        help_text = self.model.get_help_header_text(self.item)

        self.plainTextEdit_py_help.setProperty('plainText', help_text)

    #----------------------------------------------------------------------
    def _updateEnableStates(self, new_text):
        """"""

        if new_text == '':
            disabledObjectNames = \
                ITEM_PROP_DLG_OBJ_ENABLED_EXE_NONEMPTY_SRC_FILEPATH
        else:
            disabledObjectNames = []

        for objName in ITEM_PROP_DLG_OBJ_ENABLED_EXE_NONEMPTY_SRC_FILEPATH:
            obj = getattr(self, objName)
            if objName in disabledObjectNames:
                obj.setEnabled(False)
            else:
                obj.setEnabled(True)

    #----------------------------------------------------------------------
    def _getItemType(self, descriptiveItemTypeStr):
        """"""

        if descriptiveItemTypeStr in ('Executable (Popen)', 'exe'):
            itemType = 'exe'
        elif descriptiveItemTypeStr in ('Python Module (import executable)', 'py'):
            itemType = 'py'
        elif descriptiveItemTypeStr in ('Page', 'page'):
            itemType = 'page'
        elif descriptiveItemTypeStr in ('Info', 'info'):
            itemType = 'info'
        elif descriptiveItemTypeStr in ('Text', 'txt'):
            itemType = 'txt'
        else:
            raise ValueError('Unexected descriptive item type string: {0:s}'.
                             format(descriptiveItemTypeStr))

        return itemType

    #----------------------------------------------------------------------
    def _getDescriptiveItemType(self, itemType):
        """"""

        if itemType == 'exe':
            descriptiveItemTypeStr = 'Executable (Popen)'
        elif itemType == 'py':
            descriptiveItemTypeStr = 'Python Module (import executable)'
        elif itemType == 'page':
            descriptiveItemTypeStr = 'Page'
        elif itemType == 'info':
            descriptiveItemTypeStr = 'Info'
        elif itemType == 'txt':
            descriptiveItemTypeStr = 'Text'
        else:
            raise ValueError('Unexected itemType: {0:s}'.
                             format(itemType))

        return descriptiveItemTypeStr

    #----------------------------------------------------------------------
    def switchItemSpecificPropObjects(self, itemType_or_descriptiveItemTypeStr,
                                      use_default_icon=True):
        """"""

        itemType = self._getItemType(itemType_or_descriptiveItemTypeStr)
        self.item.itemType = itemType

        itemTypeList = ['page', 'info', 'txt', 'py', 'exe']
        self.stackedWidget.setCurrentIndex(itemTypeList.index(itemType))

        if not self.isItemPropertiesModifiable:

            obj = getattr(self, ITEM_PROPERTIES_DIALOG_OBJECTS['dispName'])
            obj.setEnabled(False)
            obj = getattr(self, ITEM_PROPERTIES_DIALOG_OBJECTS['itemType'])
            obj.setEnabled(False)
            obj = getattr(self, ITEM_PROPERTIES_DIALOG_OBJECTS['icon'])
            obj.setEnabled(False)

            for (propName, objName) in ITEM_PROPERTIES_DIALOG_OBJECTS[itemType].iteritems():
                obj = getattr(self, objName)
                obj.setEnabled(False)

            return

        else:
            if (itemType == 'exe') and \
               (getattr(self, ITEM_PROPERTIES_DIALOG_OBJECTS['exe']\
                        ['sourceFilepath']).text() == ''):
                disabledObjectNames = \
                    ITEM_PROP_DLG_OBJ_ENABLED_EXE_NONEMPTY_SRC_FILEPATH
            else:
                disabledObjectNames = []

            if use_default_icon:
                obj = getattr(self, ITEM_PROPERTIES_DIALOG_OBJECTS['icon'])
                obj.setIcon(QIcon(DEFAULT_ICONS[itemType]))
                obj.setToolTip(DEFAULT_ICON_NAMES[itemType])

        for (propName, objName) in ITEM_PROPERTIES_DIALOG_OBJECTS[itemType].iteritems():
            obj = getattr(self, objName)
            if objName in disabledObjectNames:
                obj.setEnabled(False)

                # Reset values to default
                if objName.startswith('lineEdit'):
                    obj.setText(DEFAULT_XML_ITEM[propName])
                elif objName.startswith('comboBox'):

                    search_string = DEFAULT_XML_ITEM[propName]
                    matchedInd = obj.findText(search_string, Qt.MatchExactly)
                    # If no match found, try case-insensitive search
                    if matchedInd == -1:
                        matchedInd = obj.findText(search_string,
                                                  Qt.MatchFixedString)
                    if matchedInd != -1:
                        obj.setCurrentIndex(matchedInd)
                    else:
                        msgBox = QMessageBox()
                        msgBox.setText( (
                            'No matching item found in ' + objName) )
                        msgBox.setInformativeText( str(sys.exc_info()) )
                        msgBox.setIcon(QMessageBox.Critical)
                        msgBox.exec_()

                elif objName.startswith(('plainTextEdit', 'pushButton')):
                    pass
                else:
                    raise ValueError('Unexpected object name: {0:s}'.
                                     format(objName))

            else:
                obj.setEnabled(True)

    #----------------------------------------------------------------------
    def accept(self):
        """"""

        dispName = str(self.lineEdit_dispName.text())
        if dispName == '':
            msgBox = QMessageBox()
            msgBox.setText( (
                'Empty item name not allowed.') )
            msgBox.setInformativeText(
                'Please enter a non-empty string as an item name.')
            msgBox.setIcon(QMessageBox.Critical)
            msgBox.exec_()
            return

        path = self.parentPath + SEPARATOR + dispName
        if path in self.existingPathList:
            msgBox = QMessageBox()
            msgBox.setText( (
                'Duplicate item name detected.') )
            msgBox.setInformativeText(
                'The name ' + '"' + dispName + '"' +
                ' is already used in this page. Please use a different name.')
            msgBox.setIcon(QMessageBox.Critical)
            msgBox.exec_()
            return
        else:
            self.lineEdit_dispName.setText(dispName)

        obj = getattr(self, ITEM_PROPERTIES_DIALOG_OBJECTS['dispName'])
        self.origItem.dispName = obj.text()
        self.origItem.setText(self.origItem.dispName)

        obj = getattr(self, ITEM_PROPERTIES_DIALOG_OBJECTS['itemType'])
        itemType = self._getItemType(obj.currentText())
        self.origItem.itemType = itemType

        obj = getattr(self, ITEM_PROPERTIES_DIALOG_OBJECTS['icon'])
        self.origItem.icon = obj.toolTip()

        for (propName, objName) in \
            ITEM_PROPERTIES_DIALOG_OBJECTS[itemType].iteritems():
            obj = getattr(self, objName)
            if objName.startswith('lineEdit'):
                setattr(self.origItem, propName, obj.text())
            elif objName.startswith('comboBox'):
                setattr(self.origItem, propName, obj.currentText())
            elif objName.startswith('plainTextEdit') and \
                 objName.endswith(('description','help')):
                self.origItem.desc = obj.property('plainText')
            elif objName.startswith('pushButton'):
                pass
            else:
                raise ValueError('Unexpected object name: {0:s}'.format(objName))

        super(LauncherModelItemPropertiesDialog, self).accept()
        # will hide the dialog

    #----------------------------------------------------------------------
    def reject(self):
        """"""

        super(LauncherModelItemPropertiesDialog, self).reject()
        # will hide the dialog

########################################################################
class LauncherModelItem(QStandardItem):
    """
    """

    #----------------------------------------------------------------------
    def __init__(self, *args):
        """Constructor"""

        QStandardItem.__init__(self, *args)

        self.path = SEPARATOR
        if args:
            self.dispName = args[0]
        else:
            self.dispName = DEFAULT_XML_ITEM['dispName']
        self.desc     = DEFAULT_XML_ITEM['desc']
        self.icon     = DEFAULT_XML_ITEM['icon']
        self.itemType = DEFAULT_XML_ITEM['itemType']

        self.help     = 'N/A'

        for prop_name in XML_ITEM_TYPE_SPECIFIC_PROP_NAMES:
            setattr(self, prop_name, 'N/A')

        for prop_name in XML_ITEM_PROPERTY_NAME_DICT[self.itemType]:
            setattr(self, prop_name, DEFAULT_XML_ITEM[prop_name])

        # Make the item NOT editable by default
        self.setFlags(self.flags() & ~Qt.ItemIsEditable)

    #----------------------------------------------------------------------
    def shallowCopy(self):
        """"""

        copiedItem = LauncherModelItem(self.dispName)

        copiedItem.setFlags(self.flags())

        copiedItem.icon = self.icon

        for p in MODEL_ITEM_PROPERTY_NAMES:
            setattr(copiedItem, p, getattr(self, p))

        copiedItem.updateIconAndColor()

        return copiedItem


    #----------------------------------------------------------------------
    def updateIconAndColor(self):
        """"""

        if self.itemType == 'page':
            #self.setIcon(QIcon(":/folder.png"))
            self.setForeground(QBrush(ITEM_COLOR_PAGE))
        elif self.itemType == 'info':
            #self.setIcon(QIcon(":/info_item.png"))
            self.setForeground(QBrush(ITEM_COLOR_INFO))
        elif self.itemType == 'txt':
            #self.setIcon(QIcon(":/txt_item.png"))
            self.setForeground(QBrush(ITEM_COLOR_TXT))
        elif self.itemType == 'py':
            #self.setIcon(QIcon(":/python.png"))
            self.setForeground(QBrush(ITEM_COLOR_PY))
        elif self.itemType == 'exe':
            #self.setIcon(QIcon(":/generic_app.png"))
            self.setForeground(QBrush(ITEM_COLOR_EXE))
        else:
            raise ValueError('Unexpected itemType: {0:s}'.format(self.itemType))

        if self.icon in ICONS.keys():
            self.setIcon(QIcon(ICONS[self.icon]))
        else:
            raise ValueError('Unexpected icon: {0:s}'.format(self.icon))

########################################################################
class CustomTreeView(QTreeView):
    """"""

    #----------------------------------------------------------------------
    def __init__(self, *args):
        """Constructor"""

        QTreeView.__init__(self, *args)

    #----------------------------------------------------------------------
    def focusInEvent(self, event):
        """"""

        super(CustomTreeView,self).focusInEvent(event)

        self.emit(SIGNAL('focusObtained()'))

    #----------------------------------------------------------------------
    def focusOutEvent(self, event):
        """"""

        super(CustomTreeView,self).focusOutEvent(event)

        self.emit(SIGNAL('focusLost()'))

    #----------------------------------------------------------------------
    def closeEditor(self, editor, hint):
        """
        overwriting QAbstractItemView virtual protected slot
        """

        super(QTreeView,self).closeEditor(editor,hint)

        self.emit(SIGNAL('closingItemRenameEditor'), editor)

    #----------------------------------------------------------------------
    def editSlot(self, modelIndex):
        """"""

        m = self.model()
        if isinstance(m, QSortFilterProxyModel):
            sm = m.sourceModel()
            item = sm.itemFromIndex(m.mapToSource(modelIndex))
        else:
            item = m.itemFromIndex(modelIndex)

        # This check here should not be needed, but it is necessary for now
        # to have this code work properly
        if ( not isinstance(item, QStandardItem) ) and \
           item.path.startswith(USER_MODIFIABLE_ROOT_PATH+SEPARATOR):
            item.setEditable(True)
        else:
            item.setEditable(False)

        dispName_col = 0
        if (item.column() == dispName_col) and item.isEditable():
            pass
        else:
            if isinstance(m, QSortFilterProxyModel):
                dispName_sourceIndex = sm.index(item.row(), dispName_col,
                                                item.parent().index())
                modelIndex = m.mapFromSource(dispName_sourceIndex)
                dispName_item = sm.itemFromIndex(dispName_sourceIndex)
                if not dispName_item.isEditable():
                    return
            else:
                modelIndex = m.index(item.row(), dispName_col,
                                     item.parent().index())
                dispName_item = m.itemFromIndex(modelIndex)
                if not dispName_item.isEditable():
                    return

        super(QTreeView,self).edit(modelIndex)

    #----------------------------------------------------------------------
    def edit(self, modelIndex, trigger, event):
        """"""

        m = self.model()
        if isinstance(m, QSortFilterProxyModel):
            sm = m.sourceModel()
            item = sm.itemFromIndex(m.mapToSource(modelIndex))
        else:
            item = m.itemFromIndex(modelIndex)

        dispName_col = 0
        if item is None: # No selection
            pass
        elif (item.column() == dispName_col) and item.isEditable():
            pass
        else:
            trigger = QAbstractItemView.NoEditTriggers # diable editing

        if trigger == QAbstractItemView.AllEditTriggers:
            self.modelIndexBeingRenamed = modelIndex

        return super(QTreeView,self).edit(modelIndex, trigger, event)


########################################################################
class CustomListView(QListView):
    """"""

    #----------------------------------------------------------------------
    def __init__(self, *args):
        """Constructor"""

        QListView.__init__(self, *args)

        self.modelIndexBeingRenamed = None

    #----------------------------------------------------------------------
    def focusInEvent(self, event):
        """"""

        super(CustomListView,self).focusInEvent(event)

        self.emit(SIGNAL('focusObtained()'))

    #----------------------------------------------------------------------
    def focusOutEvent(self, event):
        """"""

        super(CustomListView,self).focusOutEvent(event)

        self.emit(SIGNAL('focusLost()'))

    #----------------------------------------------------------------------
    def closeEditor(self, editor, hint):
        """
        overwriting QAbstractItemView virtual protected slot
        """

        super(QListView,self).closeEditor(editor,hint)

        self.emit(SIGNAL('closingItemRenameEditor'), editor)

    #----------------------------------------------------------------------
    def editSlot(self, modelIndex):
        """"""

        m = self.model()
        if isinstance(m, QSortFilterProxyModel):
            sm = m.sourceModel()
            item = sm.itemFromIndex(m.mapToSource(modelIndex))
        else:
            item = m.itemFromIndex(modelIndex)

        # This check here should not be needed, but it is necessary for now
        # to have this code work properly
        if item.path.startswith(USER_MODIFIABLE_ROOT_PATH+SEPARATOR):
            item.setEditable(True)
        else:
            item.setEditable(False)

        dispName_col = 0
        if (item.column() == dispName_col) and item.isEditable():
                pass
        else:
            if isinstance(m, QSortFilterProxyModel):
                dispName_sourceIndex = sm.index(item.row(), dispName_col,
                                                item.parent().index())
                modelIndex = m.mapFromSource(dispName_sourceIndex)
                dispName_item = sm.itemFromIndex(dispName_sourceIndex)
                if not dispName_item.isEditable():
                    return
            else:
                modelIndex = m.index(item.row(), dispName_col,
                                     item.parent().index())
                dispName_item = m.itemFromIndex(modelIndex)
                if not dispName_item.isEditable():
                    return

        super(QListView,self).edit(modelIndex)

    #----------------------------------------------------------------------
    def edit(self, modelIndex, trigger, event):
        """"""

        m = self.model()
        if isinstance(m, QSortFilterProxyModel):
            sm = m.sourceModel()
            item = sm.itemFromIndex(m.mapToSource(modelIndex))
        else:
            item = m.itemFromIndex(modelIndex)

        dispName_col = 0
        if item is None: # No selection
            pass
        elif (item.column() == dispName_col) and item.isEditable():
            pass
        else:
            trigger = QAbstractItemView.NoEditTriggers # diable editing

        if trigger == QAbstractItemView.AllEditTriggers:
            self.modelIndexBeingRenamed = modelIndex

        return super(QListView,self).edit(modelIndex, trigger, event)


########################################################################
class MainPane(QWidget):
    """"""

    #----------------------------------------------------------------------
    def __init__(self, model, initRootModelIndex, stackedWidget, listView, treeView,
                 initListViewMode=CustomListView.IconMode):
        """Constructor"""

        QWidget.__init__(self)

        self.proxyModel = QSortFilterProxyModel() # Used for views on main
        # pane for which sorting is enabled
        self.proxyModel.setSourceModel(model)

        initRootProxyModelIndex = self.proxyModel.mapFromSource(initRootModelIndex)

        listView.setModel(self.proxyModel)
        listView.setRootIndex(initRootProxyModelIndex)
        listView.setViewMode(initListViewMode)
        listView.setContextMenuPolicy(Qt.CustomContextMenu)
        self.listView_IconMode_grid_width = 100
        self.listView_IconMode_grid_height = 100
        if listView.viewMode() == CustomListView.IconMode:
            listView.setGridSize(QSize(self.listView_IconMode_grid_width,
                                       self.listView_IconMode_grid_height))
        else:
            listView.setGridSize(Qsize())
        listView.setWrapping(True) # for layout wrapping
        listView.setWordWrap(True) # for word wrapping
        self.listView = listView

        treeView.setModel(self.proxyModel)
        treeView.setRootIndex(initRootProxyModelIndex)
        treeView.setItemsExpandable(True)
        treeView.setRootIsDecorated(True)
        treeView.setAllColumnsShowFocus(True)
        treeView.setHeaderHidden(False)
        treeView.setSortingEnabled(True)
        treeView.setContextMenuPolicy(Qt.CustomContextMenu)
        self.treeView = treeView

        self.stackedWidget = stackedWidget

        self.searchModel = SearchModel(model)
        self.searchItemBeingEdited = None

        self.pathHistory = [QPersistentModelIndex(initRootModelIndex)]
        self.pathHistoryCurrentIndex = 0


########################################################################
class LauncherView(QMainWindow, Ui_MainWindow):
    """
    """

    #----------------------------------------------------------------------
    def __init__(self, model, initRootPath):
        """Constructor"""

        QMainWindow.__init__(self)

        self._initActions()
        self._initMainToolbar()

        self.model = model # Used for TreeView on side pane for which
                           # sorting is disabled

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
        self.treeViewSide.setContextMenuPolicy(Qt.CustomContextMenu)
        self.treeViewSide.setSelectionMode(QAbstractItemView.SingleSelection)
        self.treeViewSide.setEditTriggers(QAbstractItemView.EditKeyPressed |
                                          QAbstractItemView.SelectedClicked)
        self.connect(self.treeViewSide, SIGNAL('focusObtained()'),
                     self.onSidePaneFocusIn)
        self.connect(self.treeViewSide, SIGNAL('focusLost()'),
                     self.onSidePaneFocusOut)
        self.connect(self.treeViewSide, SIGNAL('closingItemRenameEditor'),
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
        rootModelIndex = QModelIndex(rootPModelIndex)
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
        self.contextMenu = QMenu()

        ## Initialize clipboard
        self.clipboard = []
        self.clipboardType = 'copy' # Either 'copy' or 'cut'

        ## Update path
        self.updatePath()

        self.lineEdit_search.setCompleter(self.model.completer)


        ## Make connections
        self.connect(self.treeViewSide.selectionModel(),
                     SIGNAL('selectionChanged(const QItemSelection &, const QItemSelection &)'),
                     self.onSelectionChange)
        self.connect(self.treeViewSide,
                     SIGNAL('doubleClicked(const QModelIndex &)'),
                     self._callbackDoubleClickOnSidePaneItem)
        self.connect(self.treeViewSide,
                     SIGNAL('clicked(const QModelIndex &)'),
                     self._callbackClickOnSidePaneItem)
        self.connect(self.treeViewSide,
                     SIGNAL('customContextMenuRequested(const QPoint &)'),
                     self.openContextMenu)


        self.connect(self.comboBox_view_mode,
                     SIGNAL('currentIndexChanged(const QString &)'),
                     self.updateMainPaneViewMode)


        # Use "textChanged" signal to include programmatic changes of search text.
        # However, if this causes crashes (this tends to happen when you add
        # a breakpoint in the callback function), switch the signal back to "textEdited"
        # and try to debug the code.
        self.connect(self.lineEdit_search, SIGNAL('textChanged(const QString &)'),
                     self.onSearchTextChange)

        self.connect(self, SIGNAL('sigClearSelection'),
                     self.clearSelection)

        # Load QSettings
        self.loadSettings()

        self.visible_column_full_name_list = PERM_VISIBLE_COL_NAMES
        self.onColumnSelectionChange(DEFAULT_VISIBLE_COL_NAMES,
                                     force_visibility_update=True)

    #----------------------------------------------------------------------
    def closeEvent(self, event):
        """"""

        # Save the current hierarchy in the user-modifiable section to
        # the user hierarchy XML file.
        rootModelItem = self.model.itemFromIndex( QModelIndex(
            self.model.pModelIndexFromPath(USER_MODIFIABLE_ROOT_PATH) ) )
        self.model.writeToXMLFile(USER_XML_FILEPATH, rootModelItem)

        if osp.exists(USER_TEMP_XML_FILEPATH):
            try: os.remove(USER_TEMP_XML_FILEPATH)
            except:
                print ' '
                print 'WARNING: Failed to delete temporary user XML file.'
                print ' '

        # Save QSettings
        self.saveSettings()

        event.accept()

    #----------------------------------------------------------------------
    def saveTempUserHierarchy(self):
        """
        To avoid losing a user change in the hierarchy due to a crash,
        whenever a change in the hierarchy is detected, the change is saved
        into a temporary file.

        In the event of a crash, a user will be asked if he/she wants to
        restore the temporary saved file.
        """

        # Save the current hierarchy in the user-modifiable section to
        # a temporary user hierarchy XML file.
        rootModelItem = self.model.itemFromIndex( QModelIndex(
            self.model.pModelIndexFromPath(USER_MODIFIABLE_ROOT_PATH) ) )
        self.model.writeToXMLFile(USER_TEMP_XML_FILEPATH, rootModelItem)

    #----------------------------------------------------------------------
    def saveSettings(self):
        """"""

        settings = QSettings('HLA','Launcher')

        settings.beginGroup('MainWindow')
        settings.setValue('position',self.geometry())
        settings.setValue('splitterPanes_sizes',self.splitterPanes.sizes())
        settings.endGroup()

        #print 'Settings saved.'

    #----------------------------------------------------------------------
    def loadSettings(self):
        """"""

        settings = QSettings('HLA','Launcher')

        settings.beginGroup('MainWindow')
        rect = settings.value('position')
        if not rect:
            rect = QRect(0,0,self.sizeHint().width(),self.sizeHint().height())
        self.setGeometry(rect)
        splitterPanes_sizes = settings.value('splitterPanes_sizes')
        if splitterPanes_sizes == None:
            splitterPanes_sizes = [self.width()*(1./5), self.width()*(4./5)]
        else:
            splitterPanes_sizes = [int(s) for s in splitterPanes_sizes]
        self.splitterPanes.setSizes(splitterPanes_sizes)

        settings.endGroup()

        #print 'Settings loaded.'

    #----------------------------------------------------------------------
    def sizeHint(self):
        """"""

        return QSize(800, 600)

    #----------------------------------------------------------------------
    def onViewModeActionGroupTriggered(self, action):
        """"""

        m = self.getCurrentMainPane()
        s = m.stackedWidget;

        if action == self.actionIconsView:
            if s.currentIndex() == self.treeView_stack_index:
                s.setCurrentIndex(self.listView_stack_index)
            m.listView.setViewMode(CustomListView.IconMode)
            m.listView.setGridSize(QSize(m.listView_IconMode_grid_width,
                                         m.listView_IconMode_grid_height))
            index = self.comboBox_view_mode.findText('Icons View',
                                                     Qt.MatchExactly)
        elif action == self.actionListView:
            if s.currentIndex() == self.treeView_stack_index:
                s.setCurrentIndex(self.listView_stack_index)
            m.listView.setViewMode(CustomListView.ListMode)
            m.listView.setGridSize(QSize())
            index = self.comboBox_view_mode.findText('List View',
                                                     Qt.MatchExactly)
        elif action == self.actionDetailsView:
            if s.currentIndex() == self.listView_stack_index:
                s.setCurrentIndex(self.treeView_stack_index)
            for c in range(self.model.columnCount()):
                m.treeView.resizeColumnToContents(c)
            index = self.comboBox_view_mode.findText('Details View',
                                                     Qt.MatchExactly)
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
    def _search_tokens_found(self, newSearchText_tokens, text):
        """
        Return True if all tokens are found in the text being searched.
        Return False otherwise.
        """

        return all([token in text for token in newSearchText_tokens])

    #----------------------------------------------------------------------
    def onSearchTextChange(self, newSearchText):
        """"""

        m = self.getCurrentMainPane()
        currentPath = m.pathHistory[m.pathHistoryCurrentIndex]
        # If currentPath is a persistent model index of "searchModel",
        # then you need to convert currentPath into the corresponding
        # persistent model index of "self.model" first.
        if ( type(currentPath) == QPersistentModelIndex ) and \
           ( type(currentPath.model()) == SearchModel ):
            currentPath = self.convertSearchModelPModIndToModelPModInd(
                m.searchModel, currentPath)

        if not newSearchText:
            # If the latest history path is a search result,
            # then remove the path, since user decided not to do search
            # any more.
            if type(currentPath) != QPersistentModelIndex:
                m.pathHistory = m.pathHistory[:m.pathHistoryCurrentIndex]
                m.pathHistoryCurrentIndex = len(m.pathHistory)-1
                # History update must happen before calling "self.updateView"
                # function for the view update to work properly.
                self.updateView(m)

            return

        if type(currentPath) == QPersistentModelIndex:
            searchRootIndex = QModelIndex(currentPath)
            m.pathHistory = m.pathHistory[:(m.pathHistoryCurrentIndex+1)]
            m.pathHistory.append({'searchText':newSearchText,
                                  'searchRootIndex':currentPath})
            m.pathHistoryCurrentIndex = len(m.pathHistory)-1
        else:
            searchRootIndex = QModelIndex(currentPath['searchRootIndex'])
            m.pathHistory[m.pathHistoryCurrentIndex] = \
                {'searchText':newSearchText,
                 'searchRootIndex':currentPath['searchRootIndex']}

        if newSearchText.startswith(('"',"'")) and \
           newSearchText.endswith  (('"',"'")): # exact word searching
            newSearchText_tokens = [newSearchText[1:-1]]
        else: # token searching
            newSearchText_tokens = newSearchText.lower().split()

        searchRootItem = self.model.itemFromIndex(searchRootIndex)
        search_root_path = searchRootItem.path.lower()

        matchedItems = [
            item for item, path, name, desc, helptxt in zip(
                self.model.search_index_item_list,
                self.model.search_index_path_list,
                self.model.search_index_name_list,
                self.model.search_index_desc_list,
                self.model.search_index_help_list,
            )
            if path.startswith(search_root_path) and
            (self._search_tokens_found(newSearchText_tokens, name) or
             self._search_tokens_found(newSearchText_tokens, desc) or
             self._search_tokens_found(newSearchText_tokens, helptxt))]

        # Update completer model
        self.model.updateCompleterModel(searchRootItem.path)

        dispNameList = [str(i.text()) for i in matchedItems]
        #print dispNameList

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
                QPersistentModelIndex(self.model.indexFromItem(item))
            ## TODO: Highlight the search matching portion of the dispaly text
            rootItem.setChild(i,0,newItem)
            for (j,prop_name) in enumerate(MODEL_ITEM_PROPERTY_NAMES):
                p = getattr(item,prop_name)
                #if not isinstance(p,str):
                    #p = str(p)
                rootItem.setChild(i,j+1,QStandardItem(p))

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

        #print 'Opening context menu'

        self.updateMenuItems()

        sender = self.sender()

        globalClickPos = sender.mapToGlobal(qpoint)

        m = self.getParentMainPane(sender)

        if m: # When right-clicked on main pane

            self.contextMenu.exec_(globalClickPos)

            self.selectedViewType = type(sender)
            self.selectedListViewMode = m.listView.viewMode()

        else: # When right-clicked on side pane

            print self.getCurrentRootPath()

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

        newTreeView.setSelectionMode(QAbstractItemView.ExtendedSelection)
        newTreeView.setSelectionBehavior(QAbstractItemView.SelectRows)

        newTreeView.setUniformRowHeights(True)

        newTreeView.setDragDropMode(QAbstractItemView.NoDragDrop)

        newTreeView.setEditTriggers(QAbstractItemView.EditKeyPressed |
                                    QAbstractItemView.SelectedClicked)

        self.connect(newTreeView.selectionModel(),
                     SIGNAL('selectionChanged(const QItemSelection &, const QItemSelection &)'),
                     self.onSelectionChange)
        self.connect(newTreeView,
                     SIGNAL('customContextMenuRequested(const QPoint &)'),
                     self.openContextMenu)
        self.connect(newTreeView,
                     SIGNAL('doubleClicked(const QModelIndex &)'),
                     self._callbackDoubleClickOnMainPaneItem)
        self.connect(newTreeView,
                     SIGNAL('clicked(const QModelIndex &)'),
                     self._callbackClickOnMainPaneItem)
        self.connect(newTreeView, SIGNAL('focusObtained()'),
                     self.onMainPaneFocusIn)
        self.connect(newTreeView, SIGNAL('focusLost()'),
                     self.onMainPaneFocusOut)
        self.connect(newTreeView, SIGNAL('closingItemRenameEditor'),
                     self.onItemRenameEditorClosing)


    #----------------------------------------------------------------------
    def _initMainPaneListViewSettings(self, newListView):
        """"""

        newListView.setSelectionMode(QAbstractItemView.ExtendedSelection)
        newListView.setSelectionBehavior(QAbstractItemView.SelectRows)

        newListView.setResizeMode(CustomListView.Adjust)
        newListView.setWrapping(True)
        newListView.setDragDropMode(QAbstractItemView.NoDragDrop)

        newListView.setEditTriggers(QAbstractItemView.EditKeyPressed |
                                    QAbstractItemView.SelectedClicked)


        self.connect(newListView.selectionModel(),
                     SIGNAL('selectionChanged(const QItemSelection &, const QItemSelection &)'),
                     self.onSelectionChange)
        self.connect(newListView,
                     SIGNAL('customContextMenuRequested(const QPoint &)'),
                     self.openContextMenu)
        self.connect(newListView,
                     SIGNAL('doubleClicked(const QModelIndex &)'),
                     self._callbackDoubleClickOnMainPaneItem)
        self.connect(newListView,
                     SIGNAL('clicked(const QModelIndex &)'),
                     self._callbackClickOnMainPaneItem)
        self.connect(newListView, SIGNAL('focusObtained()'),
                     self.onMainPaneFocusIn)
        self.connect(newListView, SIGNAL('focusLost()'),
                     self.onMainPaneFocusOut)
        self.connect(newListView, SIGNAL('closingItemRenameEditor'),
                     self.onItemRenameEditorClosing)

    #----------------------------------------------------------------------
    def onItemRenameEditorClosing(self, editor):
        """"""

        editorText = editor.text()
        selectedModelIndex = editor.parent().parent().modelIndexBeingRenamed

        sourceItem = self.itemFromIndex(selectedModelIndex)
        parentItem = sourceItem.parent()
        originalSourceItemPath = sourceItem.path

        # Check item name validity (i.e., checking whether dispName is an empty string
        # and whether there will be no duplicate path if the new dispName is accepted.
        dispName = str(editorText)
        if dispName == '':
            msgBox = QMessageBox()
            msgBox.setText( (
                'Empty item name not allowed.') )
            msgBox.setInformativeText( 'Please enter a non-empty string as an item name.')
            msgBox.setIcon(QMessageBox.Critical)
            msgBox.exec_()
            self.renameItem() # Re-open the editor
            return
        #
        path = parentItem.path + SEPARATOR + dispName
        existingPathList = self.model.pathList[:]
        if originalSourceItemPath in existingPathList:
            existingPathList.remove(originalSourceItemPath)
        if path in existingPathList:
            msgBox = QMessageBox()
            msgBox.setText( (
                'Duplicate item name detected.') )
            msgBox.setInformativeText( 'The name ' + '"' + dispName + '"' +
                                       ' is already used in this page. Please use a different name.')
            msgBox.setIcon(QMessageBox.Critical)
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

        self.model.update_search_index()
        self.saveTempUserHierarchy()

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

        if deselected is None:
            itemSelectionModel = selected
        else:
            itemSelectionModel = self.sender()
        #print 'Old Selection Empty? ', deselected.isEmpty()
        #print 'New Selection Empty? ', selected.isEmpty()
        #print itemSelectionModel.selectedIndexes()
        #print '# of selected indexes = ', len(itemSelectionModel.selectedIndexes())
        #print itemSelectionModel.selectedRows()
        #print '# of selected rows = ', len(itemSelectionModel.selectedRows())

        clickedOnSearchModeMainPane = False

        model = itemSelectionModel.model()
        if type(model) == QSortFilterProxyModel: # When selection change ocurred on a Main Pane
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
                self.selectedPersModelIndexList = [QPersistentModelIndex(i)
                                                   for i in sourceModelIndexList]
            else:
                raise ValueError('Invalid model index detected.')

            self.selectedItemList = [self.model.itemFromIndex(i)
                                     for i in sourceModelIndexList]
        else: # For selection change on a Mane Pane in Search Mode
            self.selectedItemList = [self.model.itemFromIndex(QModelIndex(pModInd))
                                     for pModInd in self.selectedPersModelIndexList]

        #if self.selectedItemList:
            #print 'Selection changed to ' + self.selectedItemList[0].path
        #else:
            #print 'Selection changed to None'


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
        currentStackedWidget = tab_page.findChildren(QStackedWidget)[0]
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

            self.onSelectionChange(listView.selectionModel(), None)

        elif visibleViewIndex == self.treeView_stack_index:
            self.comboBox_view_mode.setCurrentIndex(self.view_mode_index_details)

            treeView = currentStackedWidget.findChildren(CustomTreeView)[0]

            self.onSelectionChange(treeView.selectionModel(), None)

        else:
            print 'invalid visible stack page index'

        self.updatePath()

    #----------------------------------------------------------------------
    def runExecutable(self):
        """"""

        selectionType = self.getSelectionType()

        if selectionType in ('SingleExeSelection',
                             'SinglePyModuleSelection',
                             'MultipleExecutableSelection'):
            for item in self.selectedItemList:
                if item.itemType == 'exe':
                    self.emit(SIGNAL('sigExeRunRequested'),
                              item.path, item.command, item.cwd)
                elif item.itemType == 'py':
                    self.emit(SIGNAL('sigPyModRunRequested'),
                              item.moduleName, item.cwd, item.args)
        else:
            raise ValueError('Unexpected selectionType: {0:s}'.
                             format(selectionType))

    #----------------------------------------------------------------------
    def editTxtFile(self):
        """"""

        selectionType = self.getSelectionType()

        if selectionType in ('SingleTxtSelection',
                             'MultipleTxtSelection'):
            for item in self.selectedItemList:
                self.emit(SIGNAL('sigTxtOpenRequested'),
                          item.path, item.sourceFilepath, item.editor)
        else:
            raise ValueError('Unexpected selectionType: {0:s}'.
                             format(selectionType))

    #----------------------------------------------------------------------
    def openPage(self):
        """"""

        selectionType = self.getSelectionType()

        if selectionType == 'SinglePageSelection':
            self._callbackDoubleClickOnMainPaneItem(None)
        elif selectionType == 'MultiplePageSelection':
            raise ValueError('Menu of opening page for multiple page selection'
                             'should have been disabled.')
        else:
            raise ValueError('Unexpected selectionType: {0:s}'.
                             format(selectionType))


    #----------------------------------------------------------------------
    def openInNewTab(self):
        """"""

        if len(self.mainPaneList) == 1: # No tab has been created

            m = self.getCurrentMainPane()

            original_splitter_sizes = self.splitterPanes.sizes()

            self.tabWidget = QTabWidget(self.splitterPanes)
            self.tabWidget.setObjectName("tabWidget")
            self.tabWidget.setVisible(True)
            self.tabWidget.setTabsClosable(True)
            self.tabWidget.setMovable(True)

            # Move the current stacked widget to a tab
            new_tab = QWidget()
            m.stackedWidget.setParent(new_tab)
            currentHistoryItem = m.pathHistory[m.pathHistoryCurrentIndex]
            if type(currentHistoryItem) == dict:
                currentRootPersModInd = currentHistoryItem['searchRootIndex']
            else:
                currentRootPersModInd = currentHistoryItem
            currentRootItem = self.model.itemFromIndex(
                QModelIndex(currentRootPersModInd) )
            self.tabWidget.addTab(new_tab, currentRootItem.dispName)
            #
            tab_gridLayout = QGridLayout(new_tab)
            tab_gridLayout.addWidget(m.stackedWidget,0,0,1,1)

            self.splitterPanes.setSizes(original_splitter_sizes)

            self.connect(self.tabWidget,
                         SIGNAL('tabCloseRequested(int)'), self.closeTab);
            self.connect(self.tabWidget, SIGNAL("currentChanged(int)"),
                         self.onTabSelectionChange)


        for selectedItem in self.selectedItemList:
            new_tab = QWidget()
            new_stackedWidget = QStackedWidget(new_tab)
            #
            tab_gridLayout = QGridLayout(new_tab)
            tab_gridLayout.addWidget(new_stackedWidget,0,0,1,1)
            #
            new_page1 = QWidget()
            page1_gridLayout = QGridLayout(new_page1)
            page1_gridLayout.setContentsMargins(-1, 0, 0, 0)
            new_listView = CustomListView(new_page1)
            new_listView.setViewMode(self.selectedListViewMode)
            page1_gridLayout.addWidget(new_listView, 0, 0, 1, 1)
            new_stackedWidget.addWidget(new_page1)
            new_page2 = QWidget()
            page2_gridLayout = QGridLayout(new_page2)
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

        for selectedItem in self.selectedItemList:
            self.emit(SIGNAL('sigPyModRunRequested'),
                      'aphla.gui.aplauncher', selectedItem.cwd,
                      selectedItem.path)

    #----------------------------------------------------------------------
    def disableTabView(self):
        """"""

        self.disconnect(self.tabWidget,
                        SIGNAL('tabCloseRequested(int)'), self.closeTab);
        self.disconnect(self.tabWidget, SIGNAL("currentChanged(int)"),
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
        self.actionGoBack = QAction(QIcon(":/left_arrow.png"), "Back", self)
        self.actionGoBack.setCheckable(False)
        self.actionGoBack.setEnabled(False)
        self.addAction(self.actionGoBack)
        self.connect(self.actionGoBack, SIGNAL("triggered()"),
                     self.goBack)

        # Action for Forward button
        self.actionGoForward = QAction(QIcon(":/right_arrow.png"), "Forward",
                                       self)
        self.actionGoForward.setCheckable(False)
        self.actionGoForward.setEnabled(False)
        self.addAction(self.actionGoForward)
        self.connect(self.actionGoForward, SIGNAL("triggered()"),
                     self.goForward)

        # Action for Up button
        self.actionGoUp = QAction(QIcon(":/up_arrow.png"), "Open Parent", self)
        self.actionGoUp.setCheckable(False)
        self.actionGoUp.setEnabled(False)
        self.addAction(self.actionGoUp)
        self.connect(self.actionGoUp, SIGNAL("triggered()"),
                     self.goUp)


        self.actionOpen = QAction(QIcon(), 'Open', self)
        self.connect(self.actionOpen, SIGNAL('triggered()'),
                     self.openPage)

        self.actionOpenInNewTab = QAction(QIcon(),
                                          'Open in New Tab', self)
        self.connect(self.actionOpenInNewTab, SIGNAL('triggered()'),
                     self.openInNewTab)

        self.actionOpenInNewWindow = QAction(QIcon(),
                                             'Open in New Window', self)
        self.connect(self.actionOpenInNewWindow, SIGNAL('triggered()'),
                     self.openInNewWindow)

        self.actionRun = QAction(QIcon(), 'Run', self)
        self.connect(self.actionRun, SIGNAL('triggered()'),
                     self.runExecutable)

        self.actionEditTxt = QAction(QIcon(), 'Edit', self)
        self.connect(self.actionEditTxt, SIGNAL('triggered()'),
                     self.editTxtFile)

        self.actionCut = QAction(QIcon(), 'Cut', self)
        self.actionCut.setShortcut(
            QKeySequence(Qt.ControlModifier + Qt.Key_X))
        self.addAction(self.actionCut)
        self.connect(self.actionCut, SIGNAL('triggered()'),
                     self.cutItems)

        self.actionCopy = QAction(QIcon(), 'Copy', self)
        self.actionCopy.setShortcut(
            QKeySequence(Qt.ControlModifier + Qt.Key_C))
        self.addAction(self.actionCopy)
        self.connect(self.actionCopy, SIGNAL('triggered()'),
                     self.copyItems)

        self.actionPaste = QAction(QIcon(), 'Paste', self)
        self.actionPaste.setShortcut(
            QKeySequence(Qt.ControlModifier + Qt.Key_V))
        self.addAction(self.actionPaste)
        self.connect(self.actionPaste, SIGNAL('triggered()'),
                     self.pasteItems)


        self.actionRename = QAction(QIcon(), 'Rename', self)
        self.actionRename.setShortcut(Qt.Key_F2)
        self.addAction(self.actionRename)
        self.connect(self.actionRename, SIGNAL('triggered()'),
                     self.renameItem)

        self.actionProperties = QAction(QIcon(), 'Properties', self)
        self.actionProperties.setShortcut(
            QKeySequence(Qt.AltModifier + Qt.Key_Return))
        self.addAction(self.actionProperties)
        self.connect(self.actionProperties, SIGNAL('triggered()'),
                     self.openPropertiesDialog)


        self.actionCreateNewPage = QAction(QIcon(),
                                           'Create New Page Item', self)
        self.connect(self.actionCreateNewPage, SIGNAL('triggered()'),
                     self.openPropertiesDialog)

        self.actionCreateNewExe = QAction(QIcon(),
                                          'Create New Executable Item', self)
        self.connect(self.actionCreateNewExe, SIGNAL('triggered()'),
                     self.openPropertiesDialog)

        self.actionCreateNewPyMod = QAction(
            QIcon(), 'Create New Executable Python Module Item', self)
        self.connect(self.actionCreateNewPyMod, SIGNAL('triggered()'),
                     self.openPropertiesDialog)

        self.actionCreateNewTxt = QAction(QIcon(),
                                          'Create New Text Item', self)
        self.connect(self.actionCreateNewTxt, SIGNAL('triggered()'),
                     self.openPropertiesDialog)

        self.actionCreateNewInfo = QAction(QIcon(),
                                           'Create New Info Item', self)
        self.connect(self.actionCreateNewInfo, SIGNAL('triggered()'),
                     self.openPropertiesDialog)

        self.actionVisibleColumns = QAction(QIcon(), 'Visible Columns...',
                                            self)
        self.connect(self.actionVisibleColumns, SIGNAL('triggered()'),
                     self.launchColumnsDialog)
        self.connect(self, SIGNAL('columnSelectionReturned'),
                     self.onColumnSelectionChange)

        self.actionDelete = QAction(QIcon(), 'Delete', self)
        self.actionDelete.setShortcut(Qt.Key_Delete)
        self.addAction(self.actionDelete)
        self.connect(self.actionDelete, SIGNAL('triggered()'),
                     self.deleteItems)

        self.actionImportUserXML = QAction(
            QIcon(), 'Import user hierarchy...', self)
        self.addAction(self.actionImportUserXML)
        self.connect(self.actionImportUserXML, SIGNAL('triggered()'),
                     self.importUserXML)

        self.actionExportUserXML = QAction(
            QIcon(), 'Export user hierarchy...', self)
        self.addAction(self.actionExportUserXML)
        self.connect(self.actionExportUserXML, SIGNAL('triggered()'),
                     self.exportUserXML)

        self.actionCloseTabOrWindow = QAction(QIcon(), 'Close', self)
        self.actionCloseTabOrWindow.setShortcut(
            QKeySequence(Qt.ControlModifier + Qt.Key_W))
        self.addAction(self.actionCloseTabOrWindow)
        self.connect(self.actionCloseTabOrWindow, SIGNAL('triggered()'),
                     self.closeTabOrWindow)

        self.actionSelectAll = QAction(QIcon(), 'Select All', self)
        #self.actionSelectAll.setShortcut(
            #QKeySequence(Qt.ControlModifier + Qt.Key_A))
        self.actionSelectAll.setShortcut(QKeySequence.SelectAll)
        self.addAction(self.actionSelectAll)
        self.connect(self.actionSelectAll, SIGNAL('triggered()'),
                     self._not_implemented_yet)

        self.actionToggleSidePaneVisibility = \
            QAction(QIcon(), 'Side Pane', self)
        self.actionToggleSidePaneVisibility.setShortcut(Qt.Key_F9)
        self.addAction(self.actionToggleSidePaneVisibility)
        self.actionToggleSidePaneVisibility.setCheckable(True)
        self.actionToggleSidePaneVisibility.setChecked(True)
        self.connect(self.actionToggleSidePaneVisibility,
                     SIGNAL('triggered(bool)'),
                     self.toggleSidePaneVisibility)


        # Action Group for Main Pane View Mode
        self.actionGroupViewMode = QActionGroup(self)
        self.actionGroupViewMode.setExclusive(True)
        self.actionIconsView = QAction(QIcon(), 'Icons View',
                                       self.actionGroupViewMode)
        self.actionIconsView.setCheckable(True)
        self.actionIconsView.setShortcut(
            QKeySequence(Qt.ControlModifier + Qt.Key_1))
        self.addAction(self.actionIconsView)
        self.actionListView = QAction(QIcon(), 'List View',
                                      self.actionGroupViewMode)
        self.actionListView.setCheckable(True)
        self.actionListView.setShortcut(
            QKeySequence(Qt.ControlModifier + Qt.Key_2))
        self.addAction(self.actionListView)
        self.actionDetailsView = QAction(QIcon(), 'Details View',
                                         self.actionGroupViewMode)
        self.actionDetailsView.setCheckable(True)
        self.actionDetailsView.setShortcut(
            QKeySequence(Qt.ControlModifier + Qt.Key_3))
        self.addAction(self.actionDetailsView)
        self.actionIconsView.setChecked(True) # Default selection for the view mode
        self.connect(self.actionGroupViewMode, SIGNAL('triggered(QAction *)'),
                     self.onViewModeActionGroupTriggered)

        self.actionRunningSubprocs = QAction(QIcon(), 'Runngin Subprocesses...',
                                             self)
        self.addAction(self.actionRunningSubprocs)
        self.connect(self.actionRunningSubprocs,
                     SIGNAL('triggered()'), self.print_running_subprocs)

        self.actionHelpAbout = QAction(QIcon(), 'About...', self)
        self.addAction(self.actionHelpAbout)
        self.connect(self.actionHelpAbout, SIGNAL('triggered()'),
                     self.showHelpAbout)

    #----------------------------------------------------------------------
    def showHelpAbout(self):
        """"""

        msgBox = QMessageBox()
        msgBox.setWindowTitle('HLA Launcher')
        msgBox.setInformativeText(__doc__)
        msgBox.setIcon(QMessageBox.Information)
        msgBox.exec_()
        return

    #----------------------------------------------------------------------
    def _not_implemented_yet(self):
        """"""

        msgBox = QMessageBox()
        msgBox.setText( (
            'This action has not been implemented yet.') )
        msgBox.setInformativeText(self.sender().text())
        msgBox.setIcon(QMessageBox.Critical)
        msgBox.exec_()
        return

    #----------------------------------------------------------------------
    def launchColumnsDialog(self):
        """"""

        all_column_full_name_list = ALL_COLUMN_NAMES
        visible_column_full_name_list = self.visible_column_full_name_list
        permanently_visible_column_full_name_list = PERM_VISIBLE_COL_NAMES

        dialog = ColumnsDialog(all_column_full_name_list,
                               visible_column_full_name_list,
                               permanently_visible_column_full_name_list,
                               parentWindow=self)
        dialog.exec_()

        if dialog.output is not None:
            self.emit(SIGNAL('columnSelectionReturned'), dialog.output)

    #----------------------------------------------------------------------
    def onColumnSelectionChange(self, new_vis_col_full_names,
                                force_visibility_update=False):
        """"""

        if (not force_visibility_update) and \
           (new_vis_col_full_names == self.visible_column_full_name_list):
            return

        new_vis_col_logical_indexes = [ALL_COLUMN_NAMES.index(full_name)
                                       for full_name in new_vis_col_full_names]

        m = self.getCurrentMainPane()

        header = m.treeView.header()

        for (i, col_logical_ind) in enumerate(new_vis_col_logical_indexes):
            new_visual_ind = i
            current_visual_ind = header.visualIndex(col_logical_ind)
            header.moveSection(current_visual_ind, new_visual_ind)

        for i in range(len(ALL_COLUMN_NAMES)):
            if i not in new_vis_col_logical_indexes:
                header.hideSection(i)
            else:
                header.showSection(i)

        self.visible_column_full_name_list = new_vis_col_full_names

    #----------------------------------------------------------------------
    def _initMenus(self):
        """"""

        self.menuFile.setTitle('&File')
        self.menuEdit.setTitle('&Edit')
        self.menuView.setTitle('&View')
        self.menuGo.setTitle('&Go')
        self.menuHelp.setTitle('&Help')

        self.connect(self.menuFile, SIGNAL('aboutToShow()'),
                     self.updateMenuItems)
        self.connect(self.menuEdit, SIGNAL('aboutToShow()'),
                     self.updateMenuItems)
        self.connect(self.menuView, SIGNAL('aboutToShow()'),
                     self.updateMenuItems)
        self.connect(self.menuGo, SIGNAL('aboutToShow()'),
                     self.updateMenuItems)
        self.connect(self.menuHelp, SIGNAL('aboutToShow()'),
                     self.updateMenuItems)

    #----------------------------------------------------------------------
    def toggleSidePaneVisibility(self, TF):
        """"""

        if TF:
            self.treeViewSide.setVisible(True)
        else:
            self.treeViewSide.setVisible(False)

    #----------------------------------------------------------------------
    def importUserXML(self):
        """"""

        all_files_filter_str = 'All files (*)'
        caption = 'Import Launcher User Hierarchy XML'
        filter_str = ';;'.join(['XML files (*.xml)',
                                all_files_filter_str])
        filepath = QFileDialog.getOpenFileName(
            caption=caption, directory=START_DIRS.import_user_xml,
            filter=filter_str)
        if not filepath:
            return

        START_DIRS.import_user_xml = os.path.dirname(filepath)

        shutil.copy(filepath, USER_XML_FILEPATH)

        self.emit(SIGNAL('sigRestartLauncher'), filepath)

    #----------------------------------------------------------------------
    def exportUserXML(self):
        """"""

        all_files_filter_str = 'All files (*)'
        caption = 'Export Current Launcher User Hierarchy XML'
        filter_str = ';;'.join(['XML files (*.xml)',
                                all_files_filter_str])
        save_filepath = QFileDialog.getSaveFileName(
            caption=caption, directory=START_DIRS.export_user_xml,
            filter=filter_str)
        if not save_filepath:
            return

        START_DIRS.export_user_xml = os.path.dirname(save_filepath)

        if osp.exists(USER_TEMP_XML_FILEPATH):
            shutil.copy(USER_TEMP_XML_FILEPATH, save_filepath)
        else:
            shutil.copy(USER_XML_FILEPATH, save_filepath)

        print ('Successfully exported current launcher user hierarchy to {0:s}'.
               format(save_filepath))

    #----------------------------------------------------------------------
    def openPropertiesDialog(self):
        """"""

        m = self.getCurrentMainPane()
        parentItem = self.itemFromIndex(m.listView.rootIndex())

        if self.sender() in (self.actionCreateNewPage, self.actionCreateNewExe,
                             self.actionCreateNewPyMod,
                             self.actionCreateNewTxt, self.actionCreateNewInfo):
            selectedItem = LauncherModelItem()
            selectedItem.path = parentItem.path + SEPARATOR # Without adding SEPARATOR
            # at the end of parent item path, users will not be able to add a new item
            # right below USER_MODIFIABLE_ROOT_PATH.
            if self.sender() == self.actionCreateNewPage:
                selectedItem.itemType = 'page'
            elif self.sender() == self.actionCreateNewExe:
                selectedItem.itemType       = 'exe'
                selectedItem.command        = ''
                selectedItem.cwd            = ''
                selectedItem.sourceFilepath = ''
                selectedItem.editor         = '$wing_new_window'
                selectedItem.helpHeader     = 'python'
                selectedItem.help = ''
            elif self.sender() == self.actionCreateNewPyMod:
                selectedItem.itemType = 'py'
                selectedItem.moduleName = ''
                selectedItem.help = ''
            elif self.sender() == self.actionCreateNewTxt:
                selectedItem.itemType = 'txt'
                selectedItem.sourceFilepath = ''
                selectedItem.help           = ''
            elif self.sender() == self.actionCreateNewInfo:
                selectedItem.itemType = 'info'
            createNewItem = True

        elif self.sender() in (self.actionProperties,
                               self): # When info item is double clicked
            if self.selectedItemList:
                selectedItem = self.selectedItemList[0]
            else:
                selectedItem = parentItem
                self.selectedItemList = [selectedItem]
                parentItem = parentItem.parent()
            createNewItem = False
        else:
            raise ValueError('Unexpected sender: ' + self.sender().text())

        self.propertiesDialogView = \
            LauncherModelItemPropertiesDialog(self.model, selectedItem,
                                              parentItem)
        self.propertiesDialogView.exec_()

        isModifiable = selectedItem.path.startswith(USER_MODIFIABLE_ROOT_PATH)
        if not isModifiable:
            return

        if self.propertiesDialogView.result() == QDialog.Accepted:
            if not createNewItem:
                parentItem = selectedItem.parent()
                if parentItem is not None:
                    parentPath = parentItem.path
                else:
                    parentPath = ''
                selectedItem.path = parentPath + SEPARATOR + \
                    selectedItem.dispName
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

                        #if not isinstance(p,str):
                            #p = str(p)

                        parentSearchItem.setChild(row, ii+1, QStandardItem(p))

                    self.model.updateCompleterModel(self.getCurrentRootPath())

            else:
                selectedItem.setText(selectedItem.dispName)
                selectedItem.path = parentItem.path + SEPARATOR + selectedItem.dispName
                selectedItem.updateIconAndColor()

                parentItem.appendRow(selectedItem)
                row = selectedItem.row()

                for (ii,propName) in enumerate(MODEL_ITEM_PROPERTY_NAMES):

                    p = getattr(selectedItem, propName)

                    #if not isinstance(p,str):
                        #p = str(p)

                    parentItem.setChild(row, ii+1, QStandardItem(p))


                self.model.updatePathLookupLists() # Do not pass any argument in order to refresh entire path list

            self.updatePath()

            self.model.update_search_index()
            self.saveTempUserHierarchy()

    #----------------------------------------------------------------------
    def updateRow(self, updated1stColumnItem):
        """"""

        updated1stColumnItem.updateIconAndColor()

        parentItem = updated1stColumnItem.parent()
        row = updated1stColumnItem.row()

        for (ii,propName) in enumerate(MODEL_ITEM_PROPERTY_NAMES):

            p = getattr(updated1stColumnItem, propName)

            #if not isinstance(p,str):
                #p = str(p)

            parentItem.child(row,ii+1).setText(p)

        self.model.updatePathLookupLists() # Do not pass any argument in order to refresh entire path list


    #----------------------------------------------------------------------
    def deleteItems(self):
        """"""

        if self.getCurrentMainPanePath().startswith(USER_MODIFIABLE_ROOT_PATH):
            selectedDeletableItems = self.selectedItemList
        else:
            msgBox = QMessageBox()
            msgBox.setText( (
                'All selected items cannot be deleted. You do not have write permission.') )
            msgBox.setInformativeText( str(sys.exc_info()) )
            msgBox.setIcon(QMessageBox.Critical)
            msgBox.exec_()
            return

        msgBox = QMessageBox()
        msgBox.addButton(QMessageBox.Yes)
        msgBox.addButton(QMessageBox.Cancel)
        msgBox.setDefaultButton(QMessageBox.Cancel)
        msgBox.setEscapeButton(QMessageBox.Cancel)
        msgBox.setText( 'Delete selected items"?' )
        infoText = ''
        for item in selectedDeletableItems:
            infoText += item.path + '\n'
        msgBox.setInformativeText(infoText)
        msgBox.setIcon(QMessageBox.Question)
        msgBox.setWindowTitle('Delete')
        choice = msgBox.exec_()
        if choice == QMessageBox.Cancel:
            return

        for item in selectedDeletableItems:
            self.model.removeRow(item.row(),
                                 item.parent().index())

        self.model.updatePathLookupLists() # Do not pass any argument in order to refresh entire path list
        self.removeDeletedItemsFromHistory()
        self.updatePath()

        self.model.update_search_index()
        self.saveTempUserHierarchy()

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
                if type(p) == QPersistentModelIndex:
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
                msgBox = QMessageBox()
                msgBox.setText( (
                    'You cannot paste a parent item into a sub-item.') )
                msgBox.setIcon(QMessageBox.Critical)
                msgBox.exec_()
                self.renameItem() # Re-open the editor
                return

            rowIndex = currentRootItem.rowCount()
            parentPath = item.parent().path
            pastedItem = item.shallowCopy()
            pastedItem.setEditable(True)
            newPath = currentRootItem.path + SEPARATOR + pastedItem.dispName
            if newPath == item.path: # When source item path and target item
                # path are exactly the same, rename the target item dispName
                # with "(copy)" appended, if the pasted item is due to "copy".
                # If the pasted item is due to "cut", then stop the paste
                # action.
                if self.clipboardType == 'cut':
                    msgBox = QMessageBox()
                    msgBox.setText( (
                        'You cannot paste a cut item into the same page.') )
                    msgBox.setIcon(QMessageBox.Critical)
                    msgBox.exec_()
                    return
                else:
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
                    msgBox = QMessageBox()
                    msgBox.addButton(QMessageBox.YesToAll)
                    msgBox.addButton(QMessageBox.Yes)
                    msgBox.addButton(QMessageBox.No)
                    msgBox.addButton(QMessageBox.NoToAll)
                    msgBox.setDefaultButton(QMessageBox.No)
                    msgBox.setEscapeButton(QMessageBox.No)
                    msgBox.setText( (
                        'Replace item "' + pastedItem.dispName + '"?') )
                    msgBox.setInformativeText(
                        'An item with the same name already exists in "' + parentPath +
                        '". Replacing it will overwrite the item.')
                    msgBox.setIcon(QMessageBox.Question)
                    msgBox.setWindowTitle('Item Conflict')
                    choice = msgBox.exec_()
                else:
                    choice = QMessageBox.Yes

                if (choice == QMessageBox.Yes) or \
                   (choice == QMessageBox.YesToAll):
                    if choice == QMessageBox.YesToAll:
                        replaceAll = True
                    # Remove the conflicting item
                    persModIndToBeRemoved = self.model.pModelIndexFromPath(newPath)
                    itemToBeRemoved = self.itemFromIndex(
                        QModelIndex(persModIndToBeRemoved))
                    self.model.pathList.remove(newPath)
                    removeSucess = self.model.removeRow(
                        itemToBeRemoved.row(),
                        itemToBeRemoved.parent().index())
                    if removeSucess:
                        rowIndex -= 1
                        self.model.updatePathLookupLists() # Do not pass any argument in order to refresh entire path list
                    else:
                        raise ValueError('Item removal failed.')
                elif choice == QMessageBox.No:
                    continue
                elif choice == QMessageBox.NoToAll:
                    break
                else:
                    raise ValueError('Unexpected selection')
            pastedItem.path = newPath
            self.model.pathList.append(pastedItem.path)
            currentRootItem.setChild(rowIndex, 0, pastedItem)
            for (i,prop_name) in enumerate(MODEL_ITEM_PROPERTY_NAMES):
                p = getattr(pastedItem,prop_name)
                #if not isinstance(p,str):
                    #p = str(p)
                currentRootItem.setChild(rowIndex,i+1,QStandardItem(p))

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

        self.model.update_search_index()
        self.saveTempUserHierarchy()

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
                    #if not isinstance(p,str):
                        #p = str(p)
                    targetParentItem.setChild(r,i+1,QStandardItem(p))

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
            selectedItem = self.itemFromIndex(selectedModelIndex)
            if not selectedItem.isEditable():
                selectedItem.setEditable(True)
            self.lastFocusedView.editSlot(selectedModelIndex)



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
        viewModeComboBox = QComboBox(viewModeToolbar)
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

        self.selectedItemList = []

        w = self.tabWidget.widget(tab_index)

        w.deleteLater()

        self.tabWidget.removeTab(tab_index);

        # Remove MainPane from self.mainPaneList
        stackedWidget = w.findChild(QStackedWidget)
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

        else:
            pass

    #----------------------------------------------------------------------
    def clearSelection(self):
        """

        """

        #print 'clearSelection called'
        m = self.getCurrentMainPane()
        m.listView.selectionModel().clearSelection()
        m.treeView.selectionModel().clearSelection()
        self.treeViewSide.selectionModel().clearSelection()
        self.selectedItemList = []
        self.selectedPersModelIndexList = []

    #----------------------------------------------------------------------
    def selectAllItems(self):
        """"""

        #m = self.getCurrentMainPane()
        #m.listView.selectionModel().select()
        self._not_implemented_yet()

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

        elif item.itemType == 'exe':
            self.emit(SIGNAL('sigExeRunRequested'),
                      item.path, item.command, item.cwd)
        elif item.itemType == 'py':
            self.emit(SIGNAL('sigPyModRunRequested'),
                      item.moduleName, item.cwd, item.args)
        elif item.itemType == 'txt':
            self.emit(SIGNAL('sigTxtOpenRequested'),
                      item.path, item.sourceFilepath, item.editor)
        elif item.itemType == 'info':
            self.emit(SIGNAL('sigPropertiesOpenRequested'),)
        else:
            raise ValueError('Unexpected itemType: {0:s}'.format(item.itemType))


    #----------------------------------------------------------------------
    def _callbackDoubleClickOnSidePaneItem(self, modelIndex_NotUsed):
        """ """

        if not self.selectedItemList:
            return

        item = self.selectedItemList[0]

        if item.itemType == 'page':
            pass
        elif item.itemType == 'exe':
            self.emit(SIGNAL('sigExeRunRequested'),
                      item.path, item.command, item.cwd)
        elif item.itemType == 'py':
            self.emit(SIGNAL('sigPyModRunRequested'),
                      item.moduleName, item.cwd, item.args)
        elif item.itemType == 'txt':
            self.emit(SIGNAL('sigTxtOpenRequested'),
                      item.path, item.sourceFilepath, item.editor)
        elif item.itemType == 'info':
            self.emit(SIGNAL('sigPropertiesOpenRequested'),)
        else:
            raise ValueError('Unexpected itemType: {0:s}'.format(item.itemType))

    #----------------------------------------------------------------------
    def itemFromIndex(self, modelIndex):
        """
        "modelIndex" can be a QModelIndex that is coming from Main Pane
        views either on search mode or on non-search mode, as well as coming
        from Side Pane.
        """


        m = self.getCurrentMainPane()

        if type(modelIndex.model()) == QSortFilterProxyModel:
            proxyModelIndex = modelIndex
            sourceModelIndex = m.proxyModel.mapToSource(proxyModelIndex)

            if self.inSearchMode():
                searchItem = m.searchModel.itemFromIndex(sourceModelIndex)
                currentHistoryItem = m.pathHistory[m.pathHistoryCurrentIndex]
                sourceModelIndex = QModelIndex(currentHistoryItem['searchRootIndex'])
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

        return QModelIndex(currentRootPersModInd)

    #----------------------------------------------------------------------
    def getCurrentRootPath(self):
        """"""

        rootIndex = self.getCurrentRootIndex() # QModelIndex

        rootItem = self.model.itemFromIndex(rootIndex)

        return rootItem.path


    #----------------------------------------------------------------------
    def getSourceModelIndex(self, proxyOrSourceModelIndex, mainPane):
        """"""

        if type(proxyOrSourceModelIndex.model()) == QSortFilterProxyModel:
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
        if type(persistentSourceModelIndex) == QPersistentModelIndex: # When the main pane is showing non-search info
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

            sourceModelIndex = QModelIndex(
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

        self.tabWidget # After creating tabs, somehow without this line,
        # sometimes I get "RuntimeError: wrapped C/C++ object of %S has been
        # deleted".

        if self.tabWidget:
            currentTabPage = self.tabWidget.currentWidget()
            currentStackedWidget = currentTabPage.findChildren(QStackedWidget)[0]
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

        if childWidgetType == QStackedWidget:
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
            QModelIndex(searchModelPerModInd))

        return searchModelItem.sourcePersistentModelIndex

    #----------------------------------------------------------------------
    def getCurrentMainPanePath(self):
        """
        It is necessary for pathHistory and pathHistoryCurrentIndex to be
        updated already before this function is called. Otherwise, update
        will not work properly.
        """

        m = self.getCurrentMainPane()
        pModInd = m.pathHistory[m.pathHistoryCurrentIndex]
        if type(pModInd) == QPersistentModelIndex:
            # If pModInd is a persistent model index of "searchModel",
            # then you need to convert pModInd into the corresponding
            # persistent model index of "self.model" first.
            if type(pModInd.model()) == SearchModel:
                pModInd = self.convertSearchModelPModIndToModelPModInd(
                    m.searchModel, pModInd)

            currentRootItem = self.model.itemFromIndex(QModelIndex(pModInd))
            pathStr = currentRootItem.path
        else: # When main pane is showing search info
            searchInfo = pModInd
            searchRootIndex = searchInfo['searchRootIndex']
            searchRootItem = self.model.itemFromIndex(
                QModelIndex(searchRootIndex))
            pathStr = ('Search Results in ' + searchRootItem.path)

        return pathStr

    #----------------------------------------------------------------------
    def updatePath(self):
        """
        """

        #m = self.getCurrentMainPane()
        #pModInd = m.pathHistory[m.pathHistoryCurrentIndex]
        #if type(pModInd) == QPersistentModelIndex:
            ## If pModInd is a persistent model index of "searchModel",
            ## then you need to convert pModInd into the corresponding
            ## persistent model index of "self.model" first.
            #if type(pModInd.model()) == SearchModel:
                #pModInd = self.convertSearchModelPModIndToModelPModInd(
                    #m.searchModel, pModInd)

            #currentRootItem = self.model.itemFromIndex(QModelIndex(pModInd))
            #pathStr = currentRootItem.path
        #else: # When main pane is showing search info
            #searchInfo = pModInd
            #searchRootIndex = searchInfo['searchRootIndex']
            #searchRootItem = self.model.itemFromIndex(
                #QModelIndex(searchRootIndex))
            #pathStr = ('Search Results in ' + searchRootItem.path)

        self.lineEdit_path.setText(self.getCurrentMainPanePath())

        self.updateStatesOfNavigationButtons()

    #----------------------------------------------------------------------
    def goUp(self):
        """"""

        m = self.getCurrentMainPane()
        currentIndex = QModelIndex(m.pathHistory[m.pathHistoryCurrentIndex])
        currentPathItem = self.model.itemFromIndex(currentIndex)
        parentPathItem = currentPathItem.parent()
        parentPathIndex = self.model.indexFromItem(parentPathItem)

        if parentPathIndex.isValid():
            pModelIndex = QPersistentModelIndex(parentPathIndex)
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

        self.emit(SIGNAL('sigClearSelection'))


    #----------------------------------------------------------------------
    def goBack(self):
        """"""

        m = self.getCurrentMainPane()
        if m.pathHistoryCurrentIndex >= 1:

            m.pathHistoryCurrentIndex -= 1
            # path history must be updated before calling "updateView" function
            self.updateView(m)

            self.updateStatesOfNavigationButtons()

            self.emit(SIGNAL('sigClearSelection'))


    #----------------------------------------------------------------------
    def goForward(self):
        """"""

        m = self.getCurrentMainPane()
        if m.pathHistoryCurrentIndex <= len(m.pathHistory)-2:

            m.pathHistoryCurrentIndex += 1
            # path history must be updated before calling "updateView" function
            self.updateView(m)

            self.updateStatesOfNavigationButtons()

            self.emit(SIGNAL('sigClearSelection'))


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
        if type(currentPerModInd) == QPersistentModelIndex:
            # If currentPerModInd is a persistent model index of "searchModel",
            # then you need to convert currentPerModInd into the corresponding
            # persistent model index of "self.model" first.
            if type(currentPerModInd.model()) == SearchModel:
                currentPerModInd = self.convertSearchModelPModIndToModelPModInd(
                    m.searchModel, currentPerModInd)

            currentPathIndex = QModelIndex(currentPerModInd)
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
        self.actionGroupViewMode.emit(SIGNAL('triggered(QAction *)'),
                                      triggeredAction)

    #----------------------------------------------------------------------
    def getSelectionType(self):
        """"""

        if not self.selectedItemList:
            selectionType = 'NoSelection'
        else:
            if len(self.selectedItemList) == 1:
                itemType = self.selectedItemList[0].itemType
                if itemType == 'page':
                    selectionType = 'SinglePageSelection'
                elif itemType == 'exe':
                    selectionType = 'SingleExeSelection'
                elif itemType == 'py':
                    selectionType = 'SinglePyModuleSelection'
                elif itemType == 'txt':
                    selectionType = 'SingleTxtSelection'
                elif itemType == 'info':
                    selectionType = 'SingleInfoSelection'
                else:
                    raise ValueError('Unexpected itemType: {0:s}'.
                                     format(itemType))
            else:
                itemTypes = set([item.itemType for item
                                 in self.selectedItemList])
                if itemTypes == set(['page']):
                    selectionType = 'MultiplePageSelection'
                elif itemTypes in (set(['exe']), set(['py']),
                                   set(['exe','py'])):
                    selectionType = 'MultipleExecutableSelection'
                elif itemTypes == set(['txt']):
                    selectionType = 'MultipleTxtSelection'
                else:
                    selectionType = 'MultipleMixedTypeSelection'

        return selectionType

    #----------------------------------------------------------------------
    def updateMenuItems(self):
        """"""

        m = self.getCurrentMainPane()

        # First categorize current selection
        selectionType = self.getSelectionType()

        # Update enable states for actions that can modify the data,
        # depending on the current root path. If the current path is not in the
        # user modifiable section (i.e., not under /root/Favorites page), then
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
                QModelIndex(currentRootPersModInd) )
            searchModeDisabledActionList = [self.actionPaste,
                                            self.actionCreateNewPage,
                                            self.actionCreateNewInfo,
                                            self.actionCreateNewTxt,
                                            self.actionCreateNewPyMod,
                                            self.actionCreateNewExe]

        isModifiable = currentRootItem.path.startswith(
            USER_MODIFIABLE_ROOT_PATH)
        modificationActionList = [
            self.actionCut, self.actionPaste, self.actionRename,
            self.actionDelete, self.actionCreateNewPage,
            self.actionCreateNewInfo, self.actionCreateNewTxt,
            self.actionCreateNewPyMod, self.actionCreateNewExe
        ]
        if isModifiable:
            enableState = True
        else:
            enableState = False
        for a in modificationActionList:
            a.setEnabled(enableState)

        self.actionProperties.setEnabled(True)

        # Override Enable states for actions that should be disabled if
        # Main Pane is currently in Search Mode
        for a in searchModeDisabledActionList:
            a.setEnabled(False)

        # Override Enable state for "Paste" if self.clipboard is an empty list
        if self.clipboard:
            self.actionPaste.setEnabled(True)
        else:
            self.actionPaste.setEnabled(False)

        # Override Enable state for "Delete" to disabled.
        # If the selected item on Side Tree View is deleted, then
        # it will cause a problem with the current root item of Main Pane.
        if self.selectedItemList and \
           (currentRootItem.path in [item.path for item in self.selectedItemList]):
            self.actionDelete.setEnabled(False)

        # TODO: Re-enable tabs once known bugs related to tabs are resolved
        self.actionOpenInNewTab.setEnabled(False)

        sender = self.sender()
        #print sender.title()

        if type(sender) == QMenu: # Clicked on Menu Bar

            sender.clear()

            if sender == self.menuFile:

                if selectionType in ('SinglePageSelection',
                                     'MultiplePageSelection'):
                    sender.addSeparator()
                    sender.addAction(self.actionOpen)
                    if selectionType == 'MultiplePageSelection':
                        self.actionOpen.setEnabled(False)
                    sender.addAction(self.actionOpenInNewTab)
                    sender.addAction(self.actionOpenInNewWindow)
                elif selectionType in ('SingleExeSelection',
                                       'SinglePyModuleSelection',
                                       'MultipleExecutableSelection'):
                    sender.addSeparator()
                    sender.addAction(self.actionRun)
                elif selectionType in ('SingleTxtSelection',
                                       'MultipleTxtSelection'):
                    sender.addSeparator()
                    sender.addAction(self.actionEditTxt)
                elif selectionType in ('SingleInfoSelection'):
                    pass
                else:
                    pass

                if selectionType == 'NoSelection':
                    sender.addAction(self.actionCreateNewPage)
                    sender.addAction(self.actionCreateNewExe)
                    sender.addAction(self.actionCreateNewTxt)
                    sender.addAction(self.actionCreateNewInfo)

                if selectionType in ('NoSelection',
                                     'SinglePageSelection',
                                     'SingleExeSelection',
                                     'SinglePyModuleSelection',
                                     'SingleTxtSelection',
                                     'SingleInfoSelection'):
                    sender.addSeparator()
                    sender.addAction(self.actionProperties)

                sender.addSeparator()
                sender.addAction(self.actionImportUserXML)
                sender.addAction(self.actionExportUserXML)

                sender.addSeparator()
                sender.addAction(self.actionCloseTabOrWindow)

            elif sender == self.menuEdit:

                if selectionType != 'NoSelection':
                    sender.addAction(self.actionCut)
                    sender.addAction(self.actionCopy)
                sender.addAction(self.actionPaste)

                sender.addSeparator()
                sender.addAction(self.actionSelectAll)

                if selectionType.startswith('Single'):
                    sender.addSeparator()
                    sender.addAction(self.actionRename)

                if selectionType != 'NoSelection':
                    sender.addSeparator()
                    sender.addAction(self.actionDelete)

            elif sender == self.menuView:

                sender.addAction(self.actionToggleSidePaneVisibility)

                if m.stackedWidget.currentIndex() == self.treeView_stack_index:
                    sender.addSeparator()
                    sender.addAction(self.actionVisibleColumns)

                sender.addSeparator()
                sender.addAction(self.actionIconsView)
                sender.addAction(self.actionListView)
                sender.addAction(self.actionDetailsView)

                sender.addSeparator()
                sender.addAction(self.actionRunningSubprocs)

            elif sender == self.menuGo:

                sender.addAction(self.actionGoUp)
                sender.addAction(self.actionGoBack)
                sender.addAction(self.actionGoForward)

            elif sender == self.menuHelp:

                sender.addAction(self.actionHelpAbout)

            else:
                raise('Unexpected menu sender '+sender.title())

        elif sender == self.treeViewSide: # Clicked on Tree View on Side Pane


            if selectionType == 'NoSelection':
                return

            self.contextMenu.clear()

            if selectionType == 'SinglePageSelection':
                self.contextMenu.addAction(self.actionOpen)
                self.contextMenu.addAction(self.actionOpenInNewTab)
                self.contextMenu.addAction(self.actionOpenInNewWindow)
                self.contextMenu.setDefaultAction(self.actionOpen)
            elif selectionType in ('SingleExeSelection',
                                   'SinglePyModuleSelection'):
                self.contextMenu.addAction(self.actionRun)
                self.contextMenu.setDefaultAction(self.actionRun)
            elif selectionType in ('SingleTxtSelection'):
                self.contextMenu.addAction(self.actionEditTxt)
                self.contextMenu.setDefaultAction(self.actionEditTxt)
            elif selectionType in ('SingleInfoSelection'):
                self.contextMenu.setDefaultAction(self.actionProperties)
            else:
                raise ValueError('Unexpected selection type detected: ' + selectionType)

            self.contextMenu.addSeparator()
            self.contextMenu.addAction(self.actionCut)
            self.contextMenu.addAction(self.actionCopy)

            self.contextMenu.addSeparator()
            self.contextMenu.addAction(self.actionDelete)

            self.contextMenu.addSeparator()
            self.contextMenu.addAction(self.actionProperties)

        else: # (type(sender) == CustomListView) or (type(sender) == CustomTreeView)
            # Clicked on List View or Tree View on Main Pane

            self.validateSelectedItemList(m)
            # Since "validateSelectedItemList()" function may have cleared
            # selection, selectionType must be updated to reflect the change.
            selectionType = self.getSelectionType()

            self.contextMenu.clear()

            if selectionType == 'NoSelection':

                self.contextMenu.addAction(self.actionCreateNewPage)
                self.contextMenu.addAction(self.actionCreateNewExe)
                self.contextMenu.addAction(self.actionCreateNewTxt)
                self.contextMenu.addAction(self.actionCreateNewInfo)

                self.contextMenu.addSeparator()
                self.contextMenu.addAction(self.actionPaste)

                if m.stackedWidget.currentIndex() == self.treeView_stack_index:
                    self.contextMenu.addSeparator()
                    self.contextMenu.addAction(self.actionVisibleColumns)

                self.contextMenu.addSeparator()
                self.contextMenu.addAction(self.actionProperties)

            elif selectionType in ('SinglePageSelection',
                                   'MultiplePageSelection'):

                self.contextMenu.addAction(self.actionOpen)
                self.contextMenu.addAction(self.actionOpenInNewTab)
                self.contextMenu.addAction(self.actionOpenInNewWindow)

                self.add_basic_item_context_menus(m)

                if selectionType == 'MultiplePageSelection':
                    self.actionOpen.setEnabled(False)
                    #
                    self.actionPaste.setEnabled(False)
                    #
                    self.actionRename.setEnabled(False)
                    #
                    self.actionProperties.setEnabled(False)

                self.contextMenu.setDefaultAction(self.actionOpen)

            elif selectionType in ('SingleExeSelection',
                                   'SinglePyModuleSelection',
                                   'MultipleExecutableSelection'):

                self.contextMenu.addAction(self.actionRun)

                self.add_basic_item_context_menus(m)

                if selectionType == 'MultipleExecutableSelection':
                    self.actionRename.setEnabled(False)
                    #
                    self.actionProperties.setEnabled(False)

                self.contextMenu.setDefaultAction(self.actionRun)

            elif selectionType in ('SingleTxtSelection',
                                   'MultipleTxtSelection'):

                self.contextMenu.addAction(self.actionEditTxt)

                self.add_basic_item_context_menus(m)

                if selectionType == 'MultipleTxtSelection':
                    self.actionRename.setEnabled(False)
                    #
                    self.actionProperties.setEnabled(False)

                self.contextMenu.setDefaultAction(self.actionEditTxt)

            elif selectionType in ('SingleInfoSelection'):

                self.add_basic_item_context_menus(m)

                self.contextMenu.setDefaultAction(self.actionProperties)

            elif selectionType == 'MultipleMixedTypeSelection':

                self.add_basic_item_context_menus(m)

                self.actionRename.setEnabled(False)
                #
                self.actionProperties.setEnabled(False)

            else:
                raise TypeError('Unexpected selection type: ' + selectionType)

    #----------------------------------------------------------------------
    def add_basic_item_context_menus(self, currentMainPane):
        """"""

        self.contextMenu.addSeparator()
        self.contextMenu.addAction(self.actionCut)
        self.contextMenu.addAction(self.actionCopy)
        self.contextMenu.addAction(self.actionPaste)

        self.contextMenu.addSeparator()
        self.contextMenu.addAction(self.actionRename)

        self.contextMenu.addSeparator()
        self.contextMenu.addAction(self.actionDelete)

        if currentMainPane.stackedWidget.currentIndex() == \
           self.treeView_stack_index:
            self.contextMenu.addSeparator()
            self.contextMenu.addAction(self.actionVisibleColumns)

        self.contextMenu.addSeparator()
        self.contextMenu.addAction(self.actionProperties)

    #----------------------------------------------------------------------
    def print_running_subprocs(self):
        """"""

        self.emit(SIGNAL('printRunningSubprocs'))


########################################################################
class LauncherApp(QObject):
    """ """

    #----------------------------------------------------------------------
    def __init__(self, initRootPath):
        """Constructor"""

        QObject.__init__(self)

        self.appList  = []
        self.subprocs = []

        self._initModel()

        self._initView(initRootPath)

        self.connect(self.view, SIGNAL('sigExeRunRequested'),
                     self.launchExe)
        self.connect(self.view, SIGNAL('sigPyModRunRequested'),
                     self.launchPyModule)
        self.connect(self.view, SIGNAL('sigTxtOpenRequested'),
                     self.openTxtFile)
        self.connect(self.view, SIGNAL('sigPropertiesOpenRequested'),
                     self.view.openPropertiesDialog)
        self.connect(self.view, SIGNAL('printRunningSubprocs'),
                     self.print_running_subprocs)

    #----------------------------------------------------------------------
    def _shutdown(self):
        """
        TODO: Gracefully terminate all the running subprocesses
        """




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
    def launchExe(self, item_path, appCommand, workingDir):
        """"""

        if workingDir in ('', 'N/A'):
            workingDir = os.getcwd()
        else:
            workingDir = _subs_tilde_with_home(workingDir)

        try:
            command_expression = appCommand
            message = ('### Trying to launch "{0:s}"...'.
                       format(command_expression))
            self.view.statusBar().showMessage(message)
            print message
            self.view.repaint()
            subs_cmd = _subs_tilde_with_home(command_expression)
            p = Popen(subs_cmd, shell=True, stdin=PIPE,
                      cwd=workingDir)
            print '** PID = {0:d}'.format(p.pid)
            print ' '
            message = ('# Launch sequence for "{0:s}" has been completed.'.
                       format(subs_cmd))
            self.view.statusBar().showMessage(message)
            print ' '
            print message
            self.subprocs.append(dict(p=p, path=item_path,
                                      cmd=command_expression))
        except:
            msgBox = QMessageBox()
            message = ('Launching ' + '"'+command_expression+'"' +
                       ' with Popen has failed.')
            msgBox.setText(message)
            ei = sys.exc_info()
            err_info_str = ei[1].__repr__()
            err_info_str += ('\nError occurred at aplauncher.py on Line '
                             '{0:d}'.format(ei[-1].tb_lineno))
            msgBox.setInformativeText(err_info_str)
            print '#', message
            print err_info_str
            msgBox.setIcon(QMessageBox.Critical)
            msgBox.exec_()

    #----------------------------------------------------------------------
    def which(self, cmd):
        """"""

        p = Popen('bash -c "which {0:s}"'.format(cmd), shell=True, stdout=PIPE)
        out, err = p.communicate()
        if err:
            raise ValueError(err)
        else:
            return out

    #----------------------------------------------------------------------
    def openTxtFile(self, item_path, filepath, editor):
        """"""

        if filepath == '':
            return

        filepath = _subs_tilde_with_home(filepath)

        try:
            if not editor.startswith('$'):
                cmd = editor.split()[0]
                if self.which(cmd) != '':
                    cmd = ' '.join([editor, filepath])
                else:
                    raise ValueError('Command not found: {0:s}'.format(cmd))
            elif editor in ('$nano', '$vi'):
                cmd = editor[1:]
                if self.which(cmd) != '':
                    cmd = 'gnome-terminal -e "{0:s} {1:s}"'.format(editor[1:],
                                                                   filepath)
                else:
                    raise ValueError('Command not found: {0:s}'.format(cmd))
            elif editor == '$matlab':
                if self.which('matlabl') != '':
                    cmd = 'matlab -r "edit {0:s}"'.format(filepath)
                else:
                    raise ValueError('Command not found: matlab')
            elif editor.startswith('$wing'):
                if editor.endswith('_new_window'):
                    new_window_flag = '--new'
                else:
                    new_window_flag = ''
                p = Popen('bash -c "compgen -ac | grep wing"', shell=True,
                          stdout=PIPE)
                out, err = p.communicate()
                available_wings = list(set(out.split()))
                if 'wing-101-4.1' in available_wings:
                    cmd = 'wing-101-4.1 {0:s} {1:s}'.format(new_window_flag,
                                                            filepath)
                elif 'wing64_4.1' in available_wings:
                    cmd = 'wing64_4.1 {0:s} {1:s}'.format(new_window_flag,
                                                          filepath)
                else:
                    raise ValueError('Wing IDE not found')
            else:
                raise ValueError('Unexpected editor: {0:s}'.format(editor))

            message = ('### Trying to open "{0:s}" with the editor "{1:s}"...'.
                       format(filepath, editor))
            self.view.statusBar().showMessage(message)
            print message
            self.view.repaint()
            if editor == 'gedit':
                stdin = open(os.devnull, 'r')
            else:
                stdin = PIPE
            p = Popen(cmd, shell=True, stdin=stdin)
            print '** PID = {0:d}'.format(p.pid)
            print ' '
            message = ('# Launch sequence for editing "{0:s}" has been completed.'.
                       format(filepath))
            self.view.statusBar().showMessage(message)
            print ' '
            print message
            self.subprocs.append(dict(p=p, path=item_path, cmd=cmd))

        except:
            msgBox = QMessageBox()
            message = ('Opening "{0:s}" with the editor "{1:s}" has failed.'.
                       format(filepath, editor))
            msgBox.setText(message)
            ei = sys.exc_info()
            err_info_str = ei[1].__repr__()
            err_info_str += ('\nError occurred at aplauncher.py on Line '
                             '{0:d}'.format(ei[-1].tb_lineno))
            msgBox.setInformativeText(err_info_str)
            print '#', message
            print err_info_str
            msgBox.setIcon(QMessageBox.Critical)
            msgBox.exec_()

    #----------------------------------------------------------------------
    def launchPyModule(self, module_name, workingDir, args):
        """
        You need to make sure that the object returned from the
        "make()" function will not get erased at the end of this
        function call. The object is a GUI object. If it is
        cleared, the GUI window will also disappear. In order
        to keep the object in the memory, one way is to store it in
        "self", which is the method employed here. Or you could declare
        the returned object as "global". With either way, the opened GUI
        window will not disappear immediately.
        """

        sys.path = ORIGINAL_SYS_PATH[:]

        if workingDir in ('', 'N/A'):
            pass
        else:
            workingDir = _subs_tilde_with_home(workingDir)
            os.chdir(workingDir)
            print 'Changed working directory to {0:s}'.format(workingDir)
            if workingDir not in sys.path:
                sys.path.insert(0, workingDir)

        module = None

        try:
            message = 'Trying to import ' + module_name + '...'
            self.view.statusBar().showMessage(message)
            print message
            self.view.repaint()
            __import__(module_name)
            module = sys.modules[module_name]
        except ImportError as e:
            message = 'Importing {0:s} failed: {1:s}'.format(module_name, str(e))
            self.view.statusBar().showMessage(message)
            print message
            msgBox = QMessageBox()
            msgBox.setText(message)
            msgBox.setInformativeText( str(errorMessage) )
            msgBox.setIcon(QMessageBox.Critical)
            msgBox.exec_()
        except:
            msgBox = QMessageBox()
            msgBox.setText( (
                'Unexpected error while launching an app w/ import: ') )
            msgBox.setInformativeText( str(sys.exc_info()) )
            msgBox.setIcon(QMessageBox.Critical)
            msgBox.exec_()

        if module:
            try:
                message = 'Trying to launch ' + module_name + '...'
                self.view.statusBar().showMessage(message)
                print message
                self.view.repaint()
                if args not in ('', 'N/A'):
                    self.appList.append(module.make(*args.split()))
                else:
                    self.appList.append(module.make())
                message = module_name + ' successfully launched.'
                self.view.statusBar().showMessage(message)
                print message
            except:
                msgBox = QMessageBox()
                msgBox.setText( (
                    'Error while launching an app w/ import: ') )
                #msgBox.setInformativeText( str(sys.exc_info()) )
                stderr_backup = sys.stderr
                sys.stderr = mystderr = StringIO()
                traceback.print_exc(None,mystderr)
                msgBox.setInformativeText( mystderr.getvalue() )
                sys.stderr = stderr_backup
                msgBox.setIcon(QMessageBox.Critical)
                msgBox.exec_()

    #----------------------------------------------------------------------
    def print_running_subprocs(self):
        """"""

        print '### Currently Running Subprocesses ###'
        print '(PID) : (Path in Launcher) : (Command Expression)'

        finished_subp_inds = []
        for i, subp_dict in enumerate(self.subprocs):
            p = subp_dict['p']
            if p.poll() is None:
                print '{0:d} : {1:s} : {2:s}'.format(
                    p.pid, subp_dict['path'], subp_dict['cmd'])
            else:
                finished_subp_inds.append(i)

        for ind in finished_subp_inds[::-1]:
            self.subprocs.pop(ind)

        if len(self.subprocs) == 0:
            print '* There is currently no running subprocess.'

#----------------------------------------------------------------------
def _subs_tilde_with_home(string):
    """"""

    if string.startswith('~'):
        string = HOME_PATH + string[1:]
    string = string.replace(' ~', ' '+HOME_PATH)

    return string

#----------------------------------------------------------------------
def make(initRootPath=''):
    """"""

    # If the platform is other than a POSIX system, then convert
    # the root path separator to the valid path separator of the OS.
    if initRootPath:
        initRootPath.replace(posixpath.sep, os.sep)

    global APP

    APP = LauncherApp(initRootPath)
    APP.view.show()

    return APP

#----------------------------------------------------------------------
def isCothreadUsed():
    """"""

    g = copy(globals())

    using_cothread = False
    for (k,v) in g.iteritems():
        if isinstance(v, types.ModuleType):
            if v.__name__ == 'cothread':
                using_cothread = True
                break

    return using_cothread

#----------------------------------------------------------------------
def restartLauncher(imported_xml_filepath):
    """"""

    initRootPath = SEPARATOR + 'root'
    new_app = LauncherApp(initRootPath)
    new_app.view.show()

    print ('Successfully imported launcher user hierarchy from {0:s}'.
           format(imported_xml_filepath))

    global APP

    APP.view.close()

    APP = new_app
    APP.connect(APP.view, SIGNAL('sigRestartLauncher'), restartLauncher)

#----------------------------------------------------------------------
def main(args = None):
    """ """

    using_cothread = isCothreadUsed()

    if using_cothread:
        # If Qt is to be used (for any GUI) then the cothread library needs to be informed,
        # before any work is done with Qt. Without this line below, the GUI window will not
        # show up and freeze the program.
        # Note that for a dialog box to be modal, i.e., blocking the application
        # execution until user input is given, you need to set the input
        # argument "user_timer" to be True.
        #cothread.iqt(use_timer = True)
        qapp = cothread.iqt()
    else:
        qapp = QApplication(args)

    font = QFont()
    font.setPointSize(16)
    qapp.setFont(font)

    global APP

    initRootPath = SEPARATOR + 'root'
    APP = LauncherApp(initRootPath)
    APP.view.show()

    # Check if there is a temporarily saved user file from an
    # ungracefully terminated previous session. If found, ask a user if he/she
    # wants to use this file, instead of the last successfully saved official
    # user file.
    if osp.exists(USER_TEMP_XML_FILEPATH):
        restoreHierarchyDialog = LauncherRestoreHierarchyDialog()
        restoreHierarchyDialog.exec_()

        if restoreHierarchyDialog.result() == QDialog.Accepted:
            shutil.move(USER_TEMP_XML_FILEPATH, USER_XML_FILEPATH)

            new_app = LauncherApp(initRootPath)
            new_app.view.show()

            APP.view.close()

            APP = new_app

    APP.connect(APP.view, SIGNAL('sigRestartLauncher'), restartLauncher)

    if using_cothread:
        cothread.WaitForQuit()
    else:
        exit_status = qapp.exec_()
        sys.exit(exit_status)


#----------------------------------------------------------------------
if __name__ == "__main__" :
    main(sys.argv)

