#! /usr/bin/env python

"""

GUI application for adjusting lattice parameters with certain ratios
between different groups of parameters.

:author: Yoshiteru Hidaka
:license:

This GUI application is a lattice turning program that allows a user to
define a set of lattice devices to be simultaneously adjusted with
certain step size ratios between them.

"""

import sys, os
from subprocess import Popen, PIPE
from time import time, strftime, localtime
from math import floor
from copy import copy
import types

from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import QObject, QSize, SIGNAL
from PyQt4.QtGui import QApplication, QMainWindow, QStandardItemModel, \
     QStandardItem, QDockWidget, QWidget, QGridLayout, QSplitter, \
     QTreeView, QTabWidget,QVBoxLayout, QHBoxLayout, QPushButton, \
     QSpacerItem, QSizePolicy, QCheckBox, QLineEdit, QLabel, QTextEdit, \
     QAction

from Qt4Designer_files.ui_lattice_tuner_for_reference import Ui_MainWindow

import TunerUtils.config as const

import aphla as ap
if ap.machines._lat is None:
    ap.initNSLS2V1()

#----------------------------------------------------------------------
def datestr(time_in_seconds_from_Epoch):
    """"""
    
    frac_sec = time_in_seconds_from_Epoch - floor(time_in_seconds_from_Epoch)
    time_format = '%Y-%m-%d (%a) %H:%M:%S.' + str(frac_sec)[2:]
    
    return strftime(time_format, localtime(time_in_seconds_from_Epoch))
    
#----------------------------------------------------------------------
def getusername():
    """"""
    
    p = Popen('whoami',stdout=PIPE,stderr=PIPE)
    username, error = p.communicate()    

    if error:
        raise OSError('Error for whoami: '+error)
    else:
        return username
    
        
        
########################################################################
class TunerConfigModel(QStandardItemModel):
    """"""

    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        
        QStandardItemModel.__init__(self)
        
        # Metadata
        self.name = ''
        self.username = getusername()
        self.time_created = time() # current time in seconds from Epoch
        self.description = ''
        
        self.channel_group_list = []
        self.ref_channel_group = {'name:':0., 'weight':'', 'channel_name_list':[]}
        self.ref_channel_group_index = 0
        self.ref_step_size = 0.
        self.normalized_weight_list = []
        self.step_size_list = []
        
        self._get_channel_name_flat_list()
        
        self._get_pv_flat_list()
        
    #----------------------------------------------------------------------
    def _get_channel_name_flat_list(self):
        """"""
        
        self._all_channel_name_flat_list = []
        for g in self.channel_group_list:
            self._all_channel_name_flat_list.extend(g['channel_name_list'])
        
    #----------------------------------------------------------------------
    def _get_pv_flat_list(self):
        """"""
        
        self._pvrb_flat_list = []
        self._pvrb_nonempty_ind_list = []
        self._pvsp_flat_list = []
        self._pvsp_nonempty_ind_list = []
        for (i,ch) in enumerate(self._all_channel_name_flat_list):
            elemName, fieldName = ch.split('.')
            elem = ap.getElements(elemName)[0]
            pv = elem.pv(field=fieldName,handle='readback')
            if len(pv) == 1:
                self._pvrb_flat_list.append(pv[0])
                self._pvrb_nonempty_ind_list.append(i)
            pv = elem.pv(field=fieldName,handle='setpoint')
            if len(pv) == 1:
                self._pvsp_flat_list.append(pv[0])
                self._pvsp_nonempty_ind_list.append(i)
                
        
        
        

########################################################################
class TurnerSnapshotModel(TunerConfigModel):
    """"""
        
    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
                
        TunerConfigModel.__init__(self)
        
        # Metadata
        self.snapshot_name = ''
        self.snapshot_username = getusername()
        self.snapshot_time_created = time() # current time in seconds from Epoch
        self.snapshot_description = ''
        
        
        self.all_channel_name_flat_list = []
        self.pvrb_values = [] #[(val1,timestamp1),(val2,timestamp2)] # in the order of flat channel list
        self.pvsp_values = [] #[(val1,timestamp1),(val2,timestamp2)]
        
########################################################################
class TunerConfigDockWidget(QDockWidget):
    """"""
    
    #----------------------------------------------------------------------
    def __init__(self, parent):
        """Constructor"""
        
        QDockWidget.__init__(self, parent)
        
        dockWidgetContents = QWidget()
        gridLayout = QGridLayout(dockWidgetContents)
        self.splitter = QSplitter(dockWidgetContents)
        self.splitter.setOrientation(QtCore.Qt.Vertical)
        self.treeView = QTreeView(self.splitter)
        
        self.tabWidget_mode = QTabWidget(self.splitter)
        #
        self.tab_step_mode = QWidget()
        verticalLayout_1 = QVBoxLayout(self.tab_step_mode)
        horizontalLayout_1 = QHBoxLayout()
        self.pushButton_step_up = QPushButton(self.tab_step_mode)
        self.pushButton_step_up.setText('Up')
        horizontalLayout_1.addWidget(self.pushButton_step_up)
        self.pushButton_step_down = QPushButton(self.tab_step_mode)
        self.pushButton_step_down.setText('Down')
        horizontalLayout_1.addWidget(self.pushButton_step_down)
        spacerItem_1 = QSpacerItem(40,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        horizontalLayout_1.addItem(spacerItem_1)
        verticalLayout_1.addLayout(horizontalLayout_1)
        horizontalLayout_2 = QHBoxLayout()
        self.pushButton_update = QPushButton(self.tab_step_mode)
        self.pushButton_update.setText('Update')
        horizontalLayout_2.addWidget(self.pushButton_update)
        self.checkBox_auto = QCheckBox(self.tab_step_mode)
        self.checkBox_auto.setMinimumSize(QSize(141,0))
        self.checkBox_auto.setText('Auto: Interval [s]')
        horizontalLayout_2.addWidget(self.checkBox_auto)
        self.lineEdit_auto_update_interval = QLineEdit(self.tab_step_mode)
        horizontalLayout_2.addWidget(self.lineEdit_auto_update_interval)
        spacerItem_2 = QSpacerItem(40,20,QSizePolicy.Expanding, QSizePolicy.Minimum)
        horizontalLayout_2.addItem(spacerItem_2)
        verticalLayout_1.addLayout(horizontalLayout_2)
        self.tabWidget_mode.addTab(self.tab_step_mode,'Step Mode')
        #
        self.tab_ramp_mode = QWidget()
        verticalLayout_11 = QVBoxLayout(self.tab_ramp_mode)
        horizontalLayout_11 = QHBoxLayout()
        label = QLabel(self.tab_ramp_mode)
        label.setText('Copy into target set points:')
        horizontalLayout_11.addWidget(label)
        self.pushButton_copy_current_setp = QPushButton(self.tab_ramp_mode)
        self.pushButton_copy_current_setp.setText('Current Setpoints')
        horizontalLayout_11.addWidget(self.pushButton_copy_current_setp)
        self.pushButton_copy_init_setp = QPushButton(self.tab_ramp_mode)
        self.pushButton_copy_init_setp.setText('Init. Setpoints')
        horizontalLayout_11.addWidget(self.pushButton_copy_init_setp)
        self.pushButton_copy_snapshot_setp = QPushButton(self.tab_ramp_mode)
        self.pushButton_copy_snapshot_setp.setText('Snapshot Setpoints')
        horizontalLayout_11.addWidget(self.pushButton_copy_snapshot_setp)
        spacerItem_3 = QSpacerItem(40, 20, QSizePolicy.Expanding,QSizePolicy.Minimum)
        horizontalLayout_11.addItem(spacerItem_3)
        verticalLayout_11.addLayout(horizontalLayout_11)
        horizontalLayout_12 = QHBoxLayout()
        label = QLabel(self.tab_ramp_mode)
        label.setText('Number of Steps:')
        horizontalLayout_12.addWidget(label)
        self.lineEdit_nSteps = QLineEdit(self.tab_ramp_mode)
        horizontalLayout_12.addWidget(self.lineEdit_nSteps)
        label = QLabel(self.tab_ramp_mode)
        label.setText('Wait after Each Step [s]:')
        horizontalLayout_12.addWidget(label)
        self.lineEdit_wait_after_each_step = QLineEdit(self.tab_ramp_mode)
        horizontalLayout_12.addWidget(self.lineEdit_wait_after_each_step)
        self.pushButton_start = QPushButton(self.tab_ramp_mode)
        self.pushButton_start.setText('Start')
        horizontalLayout_12.addWidget(self.pushButton_start)
        self.pushButton_stop = QPushButton(self.tab_ramp_mode)
        self.pushButton_stop.setText('Stop')
        horizontalLayout_12.addWidget(self.pushButton_stop)
        self.pushButton_revert = QPushButton(self.tab_ramp_mode)
        self.pushButton_revert.setText('Revert')
        horizontalLayout_12.addWidget(self.pushButton_revert)
        spacerItem_4 = QSpacerItem(40,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        horizontalLayout_12.addItem(spacerItem_4)
        verticalLayout_11.addLayout(horizontalLayout_12)
        self.tabWidget_mode.addTab(self.tab_ramp_mode, 'Ramp Mode')
        
        self.tabWidget_metadata = QTabWidget(self.splitter)
        #
        self.tab_config_metadata = QWidget()
        verticalLayout_21 = QVBoxLayout(self.tab_config_metadata)
        horizontalLayout_21 = QHBoxLayout()
        label = QLabel(self.tab_config_metadata)
        label.setText('Created by')
        horizontalLayout_21.addWidget(label)
        self.lineEdit_config_username = QLineEdit(self.tab_config_metadata)
        horizontalLayout_21.addWidget(self.lineEdit_config_username)
        label = QLabel(self.tab_config_metadata)
        label.setText('Created on')
        horizontalLayout_21.addWidget(label)
        self.lineEdit_config_timestamp = QLineEdit(self.tab_config_metadata)
        horizontalLayout_21.addWidget(self.lineEdit_config_timestamp)
        spacerItem_5 = QSpacerItem(40,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        horizontalLayout_21.addItem(spacerItem_5)
        verticalLayout_21.addLayout(horizontalLayout_21)
        horizontalLayout_22 = QHBoxLayout()
        verticalLayout_22 = QVBoxLayout()
        label = QLabel(self.tab_config_metadata)
        label.setText('Description')
        verticalLayout_22.addWidget(label)
        spacerItem_6 = QSpacerItem(20,40,QSizePolicy.Minimum,QSizePolicy.Expanding)
        verticalLayout_22.addItem(spacerItem_6)
        horizontalLayout_22.addLayout(verticalLayout_22)
        self.textEdit_config_description = QTextEdit(self.tab_config_metadata)
        horizontalLayout_22.addWidget(self.textEdit_config_description)
        verticalLayout_21.addLayout(horizontalLayout_22)
        self.tabWidget_metadata.addTab(self.tab_config_metadata,'Config Metadata')
        #
        self.tab_snapshot_metadata = QWidget()
        verticalLayout_31 = QVBoxLayout(self.tab_snapshot_metadata)
        horizontalLayout_31 = QHBoxLayout()
        label = QLabel(self.tab_snapshot_metadata)
        label.setText('Created by')
        horizontalLayout_31.addWidget(label)
        self.lineEdit_snapshot_username = QLineEdit(self.tab_snapshot_metadata)
        horizontalLayout_31.addWidget(self.lineEdit_snapshot_username)
        label = QLabel(self.tab_snapshot_metadata)
        label.setText('Created on')
        horizontalLayout_31.addWidget(label)
        self.lineEdit_snapshot_timestamp = QLineEdit(self.tab_snapshot_metadata)
        horizontalLayout_31.addWidget(self.lineEdit_snapshot_timestamp)
        spacerItem_7 = QSpacerItem(40,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        horizontalLayout_31.addItem(spacerItem_7)
        verticalLayout_31.addLayout(horizontalLayout_31)
        horizontalLayout_32 = QHBoxLayout()
        verticalLayout_32 = QVBoxLayout()
        label = QLabel(self.tab_snapshot_metadata)
        label.setText('Description')
        verticalLayout_32.addWidget(label)
        spacerItem_8 = QSpacerItem(20,40,QSizePolicy.Minimum,QSizePolicy.Expanding)
        verticalLayout_32.addItem(spacerItem_8)
        horizontalLayout_32.addLayout(verticalLayout_32)
        self.textEdit_snapshot_description = QTextEdit(self.tab_snapshot_metadata)
        horizontalLayout_32.addWidget(self.textEdit_snapshot_description)
        verticalLayout_31.addLayout(horizontalLayout_32)
        self.tabWidget_metadata.addTab(self.tab_snapshot_metadata,'Snapshot Metadata')
        
        gridLayout.addWidget(self.splitter, 0, 0, 1, 1)
        self.setWidget(dockWidgetContents)
                                
        
        

########################################################################
class TunerModel(QObject):
    """"""

    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        
        QObject.__init__(self)
        
        self.model_list = [] # A list of TunerConfigModel and/or TunerSnapshotModel objects
        
    #----------------------------------------------------------------------
    def createNewConfig(self):
        """"""
        
        newConfigModel = TunerConfigModel()
        
    
########################################################################
class TunerView(QMainWindow, Ui_MainWindow):
    """"""

    #----------------------------------------------------------------------
    def __init__(self, model):
        """Constructor"""
        
        QMainWindow.__init__(self)
        
        self.model = model
        
        self.setupUi(self)
        self.dockWidget_example.deleteLater()
        
        self.centralwidget = QWidget(self)
        self.setCentralWidget(self.centralwidget)
        self.centralWidget().hide()
        
        self.dockWidget = TunerConfigDockWidget(self)
        self.dockWidget.setWindowTitle('title1')
        self.addDockWidget(QtCore.Qt.DockWidgetArea(1), self.dockWidget)
                
        self.setTabPosition(QtCore.Qt.TopDockWidgetArea,
                            QTabWidget.North)
        self.setTabPosition(QtCore.Qt.BottomDockWidgetArea,
                            QTabWidget.North)
        self.setTabPosition(QtCore.Qt.RightDockWidgetArea,
                            QTabWidget.North)
        self.setTabPosition(QtCore.Qt.LeftDockWidgetArea,
                            QTabWidget.North)
        
        self.tabifyDockWidget(self.dockWidget_example, self.dockWidget)
        self.dockWidget.raise_()

        
        
    
########################################################################
class TunerApp(QObject):
    """"""

    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        
        QObject.__init__(self)
        
        self._initModel()
        self._initView(self.model)
        
        self.connect(self.view.actionNewConfig,SIGNAL('triggered(bool)'),
                     self.openNewConfigSetupDialog)
        
    
    #----------------------------------------------------------------------
    def _initModel(self):
        """"""
        
        self.model = TunerModel()
        
    #----------------------------------------------------------------------
    def _initView(self, model):
        """"""
        
        self.view = TunerView(model)
    
    
    #----------------------------------------------------------------------
    def openNewConfigSetupDialog(self, garbage):
        """"""
        
        pass
    
        

    
#----------------------------------------------------------------------
def make():
    """"""
    
    app = TunerApp()
    app.view.show()
    
    return app

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
def main(args):
    """"""

    using_cothread = isCothreadUsed()
    
    if using_cothread:
        # If Qt is to be used (for any GUI) then the cothread library needs to be informed,
        # before any work is done with Qt. Without this line below, the GUI window will not
        # show up and freeze the program.
        # Note that for a dialog box to be modal, i.e., blocking the application
        # execution until user input is given, you need to set the input
        # argument "user_timer" to be True.        
        #cothread.iqt(use_timer = True)
        cothread.iqt()
    else:
        qapp = QApplication(args)

    
    app = make()

    if using_cothread:
        cothread.WaitForQuit()
    else:
        exit_status = qapp.exec_()
        sys.exit(exit_status)
    
    

#----------------------------------------------------------------------    
if __name__ == "__main__" :
    main(sys.argv)
    
