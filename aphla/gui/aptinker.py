#! /usr/bin/env python
"""GUI application for adjusting lattice parameters with certain ratios
between different groups of parameters.

:author: Yoshiteru Hidaka
:license:

This GUI application is a lattice turning program that allows a user to
define a set of lattice devices to be simultaneously adjusted with
certain step size ratios between them.
"""

import sip
sip.setapi('QString', 2)
sip.setapi('QVariant', 2)

import sys, os
import numpy as np

import cothread
from cothread.catools import caget, caput, camonitor, FORMAT_TIME

from PyQt4.QtCore import (
    Qt, QObject, SIGNAL, QSize, QSettings, QRect, QMetaObject, QModelIndex,
    Q_ARG
)
from PyQt4.QtGui import (
    QApplication, QMainWindow, QDockWidget, QWidget, QTabWidget,
    QSortFilterProxyModel, QGridLayout, QSplitter, QTreeView, QTableView,
    QVBoxLayout, QHBoxLayout, QPushButton, QSpacerItem, QCheckBox, QLineEdit,
    QSizePolicy, QComboBox, QLabel, QTextEdit, QStackedWidget,
    QAbstractItemView, QToolButton, QStyle, QMessageBox, QIcon
)

from Qt4Designer_files.ui_aptinker import Ui_MainWindow
from TinkerUtils import (config, tinkerConfigSetupDialog, tinkerModels,
                         datestr, datestr_ns)
from TinkerUtils.tinkerModels import (
    ConfigAbstractModel, ConfigTableModel,
    SnapshotAbstractModel, SnapshotTableModel)
from TinkerUtils.tinkerdb import (TinkerMainDatabase)
from TinkerUtils.dbviews import SnapshotDBViewWidget

import aphla as ap
import aphla.gui.utils.gui_icons

########################################################################
class TitleRenameLineEdit(QLineEdit):
    """"""

    #----------------------------------------------------------------------
    def __init__(self, parent):
        """Constructor"""

        QLineEdit.__init__(self, parent)

        self.connect(self, SIGNAL('editingFinished()'),
                     self.finalizeText)

        self.setWindowFlags(Qt.CustomizeWindowHint)

        self.hide()

    #----------------------------------------------------------------------
    def setText(self, text):
        """"""

        QLineEdit.setText(self, text)
        title_label = self.parent().title
        label_rect = title_label.geometry()
        w = self.fontMetrics().width(text+'extra')
        h = self.fontMetrics().height()*2
        self.setGeometry(QRect(0,label_rect.y(),w,h))
        self.setFocus()
        self.selectAll()
        self.show()

    #----------------------------------------------------------------------
    def keyPressEvent(self, event):
        """"""

        if (event.key() == Qt.Key_Escape):
            QLineEdit.setText(self, '')
            self.hide()
        else:
            QLineEdit.keyPressEvent(self, event)

    #----------------------------------------------------------------------
    def focusOutEvent(self, event):
        """"""

        QLineEdit.focusOutEvent(self, event)

        self.emit(SIGNAL('editingFinished()'))

    #----------------------------------------------------------------------
    def finalizeText(self):
        """"""

        if self.text() != '':
            self.parent().title.setText(self.text())

        self.hide()

        self.emit(SIGNAL('dockTitleChangeFinalized'))


########################################################################
class TitleLabel(QLabel):
    """"""

    #----------------------------------------------------------------------
    def __init__(self, *args):
        """Constructor"""

        QLabel.__init__(self, *args)

        self._editor = TitleRenameLineEdit(self.parent())
        self.connect(self._editor, SIGNAL('dockTitleChangeFinalized'),
                     self.emitTitleChangedSignal)

    #----------------------------------------------------------------------
    def emitTitleChangedSignal(self):
        """"""

        self.emit(SIGNAL('dockTitleChanged'))

    #----------------------------------------------------------------------
    def mouseDoubleClickEvent(self, event):
        """"""

        self.edit()

        event.accept()

    #----------------------------------------------------------------------
    def edit(self):
        """"""

        self._editor.setText(self.text())

########################################################################
class CustomDockWidgetTitleBar(QWidget):
    """"""

    #----------------------------------------------------------------------
    def __init__(self, parentDockWidget):
        """Constructor"""

        QWidget.__init__(self, parentDockWidget)

        self.dockWidget = parentDockWidget

        self.title = TitleLabel(self)
        self.title.setText('untitled')
        self.connect(self.title, SIGNAL('dockTitleChanged'),
                     self._emitTitleChangeSignal)

        min_button_height = 10

        self.minimizeButton = QToolButton(self)
        #self.minimizeButton.setIcon(QIcon(':/up_arrow.png'))
        self.minimizeButton.setIcon( QApplication.style().standardIcon(
            QStyle.SP_TitleBarMinButton) )
        self.minimizeButton.setToolTip('Minimize')
        self.minimizeButton.setMinimumHeight(min_button_height)
        #
        self.maximizeButton = QToolButton(self)
        self.maximizeButton.setToolTip('Maximize')
        self.maximizeButton.setIcon( QApplication.style().standardIcon(
            QStyle.SP_TitleBarMaxButton) )
        self.maximizeButton.setMinimumHeight(min_button_height)
        #
        self.restoreButton = QToolButton(self)
        self.restoreButton.setToolTip('Restore')
        self.restoreButton.setIcon( QApplication.style().standardIcon(
            QStyle.SP_TitleBarNormalButton) )
        self.restoreButton.setMinimumHeight(min_button_height)
        #
        self.undockButton = QToolButton(self)
        self.undockButton.setToolTip('Undock')
        self.undockButton.setIcon( QApplication.style().standardIcon(
            QStyle.SP_TitleBarNormalButton) )
        self.undockButton.setMinimumHeight(min_button_height)
        #
        self.dockButton = QToolButton(self)
        self.dockButton.setToolTip('Dock')
        self.dockButton.setIcon( QApplication.style().standardIcon(
            QStyle.SP_TitleBarNormalButton) )
        self.dockButton.setMinimumHeight(min_button_height)
        #
        self.closeButton = QToolButton(self)
        self.closeButton.setToolTip('Close')
        self.closeButton.setIcon( QApplication.style().standardIcon(
            QStyle.SP_TitleBarCloseButton) )
        self.closeButton.setMinimumHeight(min_button_height)

        self.connect(self.minimizeButton,SIGNAL('clicked()'),
                     self.minimizeDockWidget)
        self.connect(self.maximizeButton,SIGNAL('clicked()'),
                     self.maximizeDockWidget)
        self.connect(self.restoreButton,SIGNAL('clicked()'),
                     self.restoreDockWidget)
        self.connect(self.undockButton,SIGNAL('clicked()'),
                     self.undockDockWidget)
        self.connect(self.dockButton,SIGNAL('clicked()'),
                     self.dockDockWidget)
        self.connect(self.closeButton,SIGNAL('clicked()'),
                     self.closeDockWidget)

        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)


        hbox = QHBoxLayout(self)
        #
        hbox.addWidget(self.title)
        hbox.addWidget(self.minimizeButton)
        hbox.addWidget(self.restoreButton)
        hbox.addWidget(self.maximizeButton)
        hbox.addWidget(self.undockButton)
        hbox.addWidget(self.dockButton)
        hbox.addWidget(self.closeButton)
        #
        hbox.insertStretch(1,500)
        hbox.setSpacing(0)

        self.window_state = Qt.WindowNoState
        self.float_state = False
        self.updateButtons()

        self.connect(self.dockWidget,
                     SIGNAL('topLevelChanged(bool)'),
                     self.updateButtons)

    #----------------------------------------------------------------------
    def renameTitle(self):
        """"""

        self.title.edit()

    #----------------------------------------------------------------------
    def _emitTitleChangeSignal(self):
        """"""
        self.emit(SIGNAL('customDockTitleChanged'))

    #----------------------------------------------------------------------
    def updateButtons(self, floating=None):
        """"""

        if floating is None:
            floating = self.dockWidget.isFloating()

        if floating:
            self.dockButton.show()
            self.undockButton.hide()
            self.minimizeButton.show()
            if self.window_state == Qt.WindowMaximized:
                self.restoreButton.show()
                self.maximizeButton.hide()
            else:
                self.restoreButton.hide()
                self.maximizeButton.show()
        else:
            self.dockButton.hide()
            self.undockButton.show()
            self.minimizeButton.hide()
            self.restoreButton.hide()
            self.maximizeButton.hide()

    #----------------------------------------------------------------------
    def minimizeDockWidget(self):
        """"""

        if self.dockWidget.windowState() not in (Qt.WindowNoState,
                                                 Qt.WindowMaximized,
                                                 Qt.WindowFullScreen,
                                                 Qt.WindowActive):
            self.dockWidget.setWindowState(Qt.WindowActive)
        '''This section is needed because when the dockWidget is undocked by
        dragging, the window state is somehow set to WindowMinimized,
        even though the window is floating WITHOUT being minimized.
        Therefore, nothing happens when minimize button is pressed.
        So, the window state must be changed to something other than
        WindowMinimized for the minimization process to happen. Here,
        WindowActive state is being used for that purpose.
        '''

        self.dockWidget.showMinimized()
        ## or
        #self.dockWidget.setWindowState(Qt.WindowMinimized)

        self.window_state = Qt.WindowMinimized
        self.updateButtons()

    #----------------------------------------------------------------------
    def maximizeDockWidget(self):
        """"""

        self.dockWidget.showMaximized()

        self.window_state = Qt.WindowMaximized
        self.updateButtons()

    #----------------------------------------------------------------------
    def restoreDockWidget(self):
        """"""

        self.dockWidget.showNormal()

        self.window_state = Qt.WindowNoState
        self.updateButtons()

    #----------------------------------------------------------------------
    def undockDockWidget(self):
        """"""

        self.dockWidget.setFloating(True)

        self.updateButtons()

    #----------------------------------------------------------------------
    def dockDockWidget(self):
        """"""

        self.dockWidget.setFloating(False)

        self.updateButtons()

    #----------------------------------------------------------------------
    def closeDockWidget(self):
        """"""
        self.dockWidget.close()

########################################################################
class TinkerDockWidget(QDockWidget):
    """"""

    #----------------------------------------------------------------------
    def __init__(self, config_abstract_model, parent):
        """Constructor"""

        isinstance(config_abstract_model, ConfigAbstractModel)

        self._initUI(parent)

        self.config_abstract = config_abstract_model

        self.ss_abstract = SnapshotAbstractModel(config_abstract_model)
        self.ss_table = SnapshotTableModel(self.ss_abstract)

        self._settings = QSettings('APHLA', 'Tinker')

        self.loadViewSizeSettings()
        self.loadMiscSettings()

        # Set up table view
        tbV = self.tableView
        proxyModel = QSortFilterProxyModel()
        proxyModel.setSourceModel(self.ss_table)
        proxyModel.setDynamicSortFilter(False)
        tbV.setModel(proxyModel)
        tbV.setCornerButtonEnabled(True)
        tbV.setShowGrid(True)
        tbV.setSelectionMode(QAbstractItemView.ExtendedSelection)
        tbV.setSelectionBehavior(QAbstractItemView.SelectItems)
        tbV.setAlternatingRowColors(True)
        tbV.setSortingEnabled(False)
        horizHeader = tbV.horizontalHeader()
        horizHeader.setSortIndicatorShown(False)
        horizHeader.setStretchLastSection(False)
        horizHeader.setMovable(False)

        # Set up tree view
        trV = self.treeView
        proxyModel = QSortFilterProxyModel()
        #proxyModel.setSourceModel(self.model.tree_model)
        #proxyModel.setDynamicSortFilter(False)
        #trV.setModel(proxyModel)
        #trV.setItemsExpandable(True)
        #trV.setRootIsDecorated(True)
        #trV.setAllColumnsShowFocus(True)
        #trV.setHeaderHidden(False)
        #trV.setSortingEnabled(True)
        #trV.setSelectionMode(QAbstractItemView.ExtendedSelection)
        #horizHeader = trV.header()
        #horizHeader.setSortIndicatorShown(True)
        #horizHeader.setStretchLastSection(True)
        #horizHeader.setMovable(False)
        #self._expandAll_and_resizeColumn()

        self.customTitleBar = CustomDockWidgetTitleBar(self)
        self.setTitleBarWidget(self.customTitleBar)
        self.connect(self.customTitleBar, SIGNAL('customDockTitleChanged'),
                     self._updateWindowTitle)

        self.connect(self.pushButton_update, SIGNAL('clicked()'),
                     self.ss_abstract.update_pv_vals)
        self.connect(self.lineEdit_ref_step_size, SIGNAL('editingFinished()'),
                     self.update_ref_step_size)

        self.connect(
            self.ss_table,
            SIGNAL('dataChanged(const QModelIndex &, const QModelIndex &)'),
            self.relayDataChangedSignal)
        self.connect(self.checkBox_synced_group_weight,
                     SIGNAL('stateChanged(int)'),
                     self.update_synced_group_weight)

        self.connect(self.checkBox_auto_caget_after_caput,
                     SIGNAL('stateChanged(int)'),
                     self.update_auto_caget_delay_after_caput)
        self.connect(self.lineEdit_auto_caget_after_caput_delay,
                     SIGNAL('editingFinished()'),
                     self.update_auto_caget_delay_after_caput)

        self.connect(self.pushButton_step_up, SIGNAL('clicked()'),
                     self.ss_abstract.step_up)
        self.connect(self.pushButton_step_down, SIGNAL('clicked()'),
                     self.ss_abstract.step_down)

    #----------------------------------------------------------------------
    def update_auto_caget_delay_after_caput(self, state=None):
        """"""

        if self.sender() == self.checkBox_auto_caget_after_caput:
            if state == Qt.Checked:
                try:
                    auto_caget_delay_after_caput = float(
                        self.lineEdit_auto_caget_after_caput_delay.text())
                except:
                    auto_caget_delay_after_caput = np.nan
                    self.lineEdit_auto_caget_after_caput_delay.setText('nan')
            else:
                auto_caget_delay_after_caput = np.nan

        elif self.sender() == self.lineEdit_auto_caget_after_caput_delay:
            if self.checkBox_auto_caget_after_caput.isChecked():
                try:
                    auto_caget_delay_after_caput = float(
                        self.lineEdit_auto_caget_after_caput_delay.text())
                except:
                    auto_caget_delay_after_caput = np.nan
                    self.lineEdit_auto_caget_after_caput_delay.setText('nan')
            else:
                auto_caget_delay_after_caput = np.nan

        else:
            raise ValueError('Unexpected sender: {0:s}'.format(
                self.sender().__repr__()))

        self.ss_abstract.auto_caget_delay_after_caput = \
            auto_caget_delay_after_caput

    #----------------------------------------------------------------------
    def update_synced_group_weight(self, state):
        """"""

        if state == Qt.Checked:
            self.config_abstract.synced_group_weight = True
            self.ss_abstract.synced_group_weight     = True
        else:
            self.config_abstract.synced_group_weight = False
            self.ss_abstract.synced_group_weight     = False

    #----------------------------------------------------------------------
    def update_ref_step_size(self):
        """"""

        try:
            new_ref_step_size = float(self.lineEdit_ref_step_size.text())
        except:
            new_ref_step_size = float('nan')
            self.lineEdit_ref_step_size.setText('nan')

        self.ss_abstract._config_table.on_ref_step_size_change(
            new_ref_step_size)
        self.ss_table.on_ref_step_size_change(new_ref_step_size)

    #----------------------------------------------------------------------
    def relayDataChangedSignal(self, proxyTopLeftIndex, proxyBottomRightIndex):
        """"""

        proxyModel = self.tableView.model()

        QMetaObject.invokeMethod(
            self.tableView, 'dataChanged', Qt.QueuedConnection,
            Q_ARG(QModelIndex, proxyModel.mapFromSource(proxyTopLeftIndex)),
            Q_ARG(QModelIndex, proxyModel.mapFromSource(proxyBottomRightIndex)))

    #----------------------------------------------------------------------
    def _initUI(self, parent):
        """"""

        QDockWidget.__init__(self, parent)

        dockWidgetContents = QWidget()
        top_gridLayout = QGridLayout(dockWidgetContents)
        #
        self.splitter = QSplitter(dockWidgetContents)
        self.splitter.setOrientation(Qt.Vertical)
        #
        self.stackedWidget = SnapshotDBViewWidget(self.splitter)
        self.page_tree  = self.stackedWidget.page_tree
        self.page_table = self.stackedWidget.page_table
        self.treeView  = self.stackedWidget.treeView
        self.tableView = self.stackedWidget.tableView
        #self.stackedWidget = QStackedWidget(self.splitter)
        ##
        #self.page_tree = QWidget()
        #gridLayout = QGridLayout(self.page_tree)
        #self.treeView = QTreeView(self.page_tree)
        #gridLayout.addWidget(self.treeView, 0, 0, 1, 1)
        #self.stackedWidget.addWidget(self.page_tree)
        ##
        #self.page_table = QWidget()
        #gridLayout = QGridLayout(self.page_table)
        #self.tableView = QTableView(self.page_table)
        #gridLayout.addWidget(self.tableView, 0, 0, 1, 1)
        #self.stackedWidget.addWidget(self.page_table)

        ## Step Mode Tab
        self.tabWidget_mode = QTabWidget(self.splitter)
        #
        self.tab_step_mode = QWidget()
        verticalLayout_1 = QVBoxLayout(self.tab_step_mode)
        horizontalLayout_1 = QHBoxLayout()
        self.pushButton_step_up = QPushButton(self.tab_step_mode)
        self.pushButton_step_up.setToolTip('Step Up')
        self.pushButton_step_up.setIcon(QIcon(':/up_arrow.png'))
        horizontalLayout_1.addWidget(self.pushButton_step_up)
        self.pushButton_step_down = QPushButton(self.tab_step_mode)
        self.pushButton_step_down.setToolTip('Step Down')
        self.pushButton_step_down.setIcon(QIcon(':/down_arrow.png'))
        horizontalLayout_1.addWidget(self.pushButton_step_down)
        label_tab_step_1 = QLabel(self.tab_step_mode)
        label_tab_step_1.setText('Ref. Step Size:')
        horizontalLayout_1.addWidget(label_tab_step_1)
        self.lineEdit_ref_step_size = QLineEdit(self.tab_step_mode)
        self.lineEdit_ref_step_size.setText('1.0')
        horizontalLayout_1.addWidget(self.lineEdit_ref_step_size)
        self.checkBox_synced_group_weight = QCheckBox(self.tab_step_mode)
        self.checkBox_synced_group_weight.setText('Sync Group Weight')
        self.checkBox_synced_group_weight.setChecked(True)
        horizontalLayout_1.addWidget(self.checkBox_synced_group_weight)

        self.pushButton_multiply = QPushButton(self.tab_step_mode)
        self.pushButton_multiply.setText('Multiply')
        self.pushButton_multiply.setToolTip('Multiply Setpoints')
        horizontalLayout_1.addWidget(self.pushButton_multiply)
        self.pushButton_divide = QPushButton(self.tab_step_mode)
        self.pushButton_divide.setText('Divide')
        self.pushButton_divide.setToolTip('Divide Setpoints')
        horizontalLayout_1.addWidget(self.pushButton_divide)
        label_tab_step_2 = QLabel(self.tab_step_mode)
        label_tab_step_2.setText('Multiplication Factor:')
        horizontalLayout_1.addWidget(label_tab_step_2)
        self.lineEdit_mult_factor = QLineEdit(self.tab_step_mode)
        self.lineEdit_mult_factor.setText('1.0')
        horizontalLayout_1.addWidget(self.lineEdit_mult_factor)
        spacerItem_1 = QSpacerItem(40,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        horizontalLayout_1.addItem(spacerItem_1)
        verticalLayout_1.addLayout(horizontalLayout_1)

        horizontalLayout_2 = QHBoxLayout()
        self.pushButton_update = QPushButton(self.tab_step_mode)
        self.pushButton_update.setText('Update')
        self.pushButton_update.setToolTip('Update PV Values')
        horizontalLayout_2.addWidget(self.pushButton_update)
        self.checkBox_auto_update = QCheckBox(self.tab_step_mode)
        self.checkBox_auto_update.setText('Auto Update: Interval [s]')
        horizontalLayout_2.addWidget(self.checkBox_auto_update)
        self.lineEdit_auto_update_interval = QLineEdit(self.tab_step_mode)
        horizontalLayout_2.addWidget(self.lineEdit_auto_update_interval)
        self.checkBox_auto_caget_after_caput = QCheckBox(self.tab_step_mode)
        self.checkBox_auto_caget_after_caput.setText('Auto caget after caput: Delay [s]')
        horizontalLayout_2.addWidget(self.checkBox_auto_caget_after_caput)
        self.lineEdit_auto_caget_after_caput_delay = QLineEdit(self.tab_step_mode)
        horizontalLayout_2.addWidget(self.lineEdit_auto_caget_after_caput_delay)
        spacerItem_2 = QSpacerItem(40,20,QSizePolicy.Expanding, QSizePolicy.Minimum)
        horizontalLayout_2.addItem(spacerItem_2)
        verticalLayout_1.addLayout(horizontalLayout_2)

        ## Ramp Mode Tab
        self.tabWidget_mode.addTab(self.tab_step_mode,'Step Mode')
        #
        self.tab_ramp_mode = QWidget()
        horizontalLayout_10 = QHBoxLayout(self.tab_ramp_mode)
        verticalLayout_tab_ramp_1 = QVBoxLayout()
        horizontalLayout_tab_ramp_2 = QHBoxLayout()
        self.pushButton_copy = QPushButton(self.tab_ramp_mode)
        self.pushButton_copy.setText('Copy')
        horizontalLayout_tab_ramp_2.addWidget(self.pushButton_copy)
        self.comboBox_setpoint_copy_source = QComboBox(self.tab_ramp_mode)
        self.comboBox_setpoint_copy_source.addItem('Current')
        self.comboBox_setpoint_copy_source.addItem('Initial')
        self.comboBox_setpoint_copy_source.addItem('Snapshot')
        horizontalLayout_tab_ramp_2.addWidget(self.comboBox_setpoint_copy_source)
        label_tab_ramp_3 = QLabel(self.tab_ramp_mode)
        label_tab_ramp_3.setText('setpoints into target setpoints')
        horizontalLayout_tab_ramp_2.addWidget(label_tab_ramp_3)
        spacerItem = QSpacerItem(40,20,QSizePolicy.Expanding, QSizePolicy.Minimum)
        horizontalLayout_tab_ramp_2.addItem(spacerItem)
        verticalLayout_tab_ramp_1.addLayout(horizontalLayout_tab_ramp_2)
        horizontalLayout_tab_ramp_1 = QHBoxLayout()
        label_tab_ramp_1 = QLabel(self.tab_ramp_mode)
        label_tab_ramp_1.setText('Number of Steps:')
        horizontalLayout_tab_ramp_1.addWidget(label_tab_ramp_1)
        self.lineEdit_nSteps = QLineEdit(self.tab_ramp_mode)
        horizontalLayout_tab_ramp_1.addWidget(self.lineEdit_nSteps)
        label_tab_ramp_2 = QLabel(self.tab_ramp_mode)
        label_tab_ramp_2.setText('Wait after Each Step [s]:')
        horizontalLayout_tab_ramp_1.addWidget(label_tab_ramp_2)
        self.lineEdit_wait_after_each_step = QLineEdit(self.tab_ramp_mode)
        horizontalLayout_tab_ramp_1.addWidget(self.lineEdit_wait_after_each_step)
        verticalLayout_tab_ramp_1.addLayout(horizontalLayout_tab_ramp_1)
        horizontalLayout_10.addLayout(verticalLayout_tab_ramp_1)
        self.pushButton_start = QPushButton(self.tab_ramp_mode)
        self.pushButton_start.setText('Start')
        horizontalLayout_10.addWidget(self.pushButton_start)
        self.pushButton_stop = QPushButton(self.tab_ramp_mode)
        self.pushButton_stop.setText('Stop')
        horizontalLayout_10.addWidget(self.pushButton_stop)
        self.pushButton_revert = QPushButton(self.tab_ramp_mode)
        self.pushButton_revert.setText('Revert')
        horizontalLayout_10.addWidget(self.pushButton_revert)
        spacerItem = QSpacerItem(137,20,QSizePolicy.Expanding, QSizePolicy.Minimum)
        horizontalLayout_10.addItem(spacerItem)
        self.tabWidget_mode.addTab(self.tab_ramp_mode,'Ramp Mode')

        ##
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

        top_gridLayout.addWidget(self.splitter, 0, 0, 1, 1)
        self.setWidget(dockWidgetContents)

    #----------------------------------------------------------------------
    def loadViewSizeSettings(self):

        self._settings.beginGroup('viewSize')

        self._position = self._settings.value('position')

        self._settings.endGroup()

    #----------------------------------------------------------------------
    def saveViewSizeSettings(self):

        self._settings.beginGroup('viewSize')

        self._settings.setValue('position', self._position)

        self._settings.endGroup()

    #----------------------------------------------------------------------
    def loadMiscSettings(self):

        self._settings.beginGroup('misc')

        self.visible_col_key_list = \
            self._settings.value('visible_col_key_list')
        if self.visible_col_key_list is None:
            self.visible_col_key_list = config.DEF_VIS_COL_KEYS['snapshot_view']

        self._settings.endGroup()

    #----------------------------------------------------------------------
    def saveMiscSettings(self):

        self._settings.beginGroup('misc')

        self._settings.setValue('visible_col_key_list',
                                self.visible_col_key_list)

        self._settings.endGroup()

    #----------------------------------------------------------------------
    def _updateWindowTitle(self):
        """
        As the built-in window title does not get automatically changed,
        when the custom window title is changed, this update is being
        performed in this function.
        """

        # This title appears at the top of the dock either when docked,
        # tabified, or floated. And this is editable.
        dock_title = self.customTitleBar.title.text()

        # This tile appears at the bottom of the dock tab only when more than
        # one docks are tabified. And this is not editable.
        self.setWindowTitle(dock_title)

        self.update()

        print 'Updating window title'

    #----------------------------------------------------------------------
    def updateMetaDataTab(self):
        """"""

        ## Update config tab
        self.lineEdit_config_username.setText(self.config_abstract.userinfo[0])
        #
        if self.config_abstract.config_ctime is not None:
            timestamp_text = datestr(self.config_abstract.config_ctime)
        else:
            timestamp_text = 'This config has not been saved yet.'
        self.lineEdit_config_timestamp.setText(timestamp_text)
        #
        self.textEdit_config_description.setText(self.config_abstract.description)

        ## Update snapshot tab
        self.lineEdit_snapshot_username.setText(self.ss_abstract.userinfo[0])
        #
        if self.ss_abstract.ss_ctime is not None:
            timestamp_text = datestr(self.ss_abstract.ss_ctime)
        else:
            timestamp_text = 'This snapshot has not been saved yet.'
        self.lineEdit_snapshot_timestamp.setText(timestamp_text)
        #
        self.textEdit_snapshot_description.setText(self.ss_abstract.description)


########################################################################
class TinkerModel(QObject):
    """"""

    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""

        QObject.__init__(self)

        self.model_list = []

########################################################################
class TinkerView(QMainWindow, Ui_MainWindow):
    """"""

    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""

        QMainWindow.__init__(self)

        self.setupUi(self)
        self.dockWidget_example.deleteLater()

        self.centralwidget = QWidget(self)
        self.setCentralWidget(self.centralwidget)
        self.centralWidget().hide()

        self.setDockNestingEnabled(True)

        tab_position = QTabWidget.South
        self.setTabPosition(Qt.TopDockWidgetArea, tab_position)
        self.setTabPosition(Qt.BottomDockWidgetArea, tab_position)
        self.setTabPosition(Qt.RightDockWidgetArea, tab_position)
        self.setTabPosition(Qt.LeftDockWidgetArea, tab_position)

        self.dockWidgetList = []
        self.next_dockWidget_index = 1

        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.connect(self, SIGNAL('customContextMenuRequested(const QPoint &)'),
                     self.openContextMenu)

        self.connect(self.actionLoadConfig, SIGNAL('triggered()'),
                     self.load_config_test)

    #----------------------------------------------------------------------
    def load_config_test(self):
        """"""

        db = TinkerMainDatabase()

        config_id = 2 # same array size

        c_abs = ConfigAbstractModel()

        (c_abs.name,), (c_abs.description,), (user_id,), (c_abs.masar_id,), \
            (c_abs.ref_step_size,), (c_abs.synced_group_weight,), \
            (c_abs.config_ctime,) = db.getColumnDataFromTable(
                'config_meta_table',
                column_name_list=['config_name', 'config_description',
                                  'config_user_id', 'config_masar_id',
                                  'config_ref_step_size',
                                  'config_synced_group_weight', 'config_ctime'],
                condition_str='config_id={0:d}'.format(config_id))

        c_abs.userinfo = zip(*db.getColumnDataFromTable(
            'user_table',
            column_name_list=['username', 'hostname', 'ip_str', 'mac_str'],
            condition_str='user_id={0:d}'.format(user_id)))[0]

        (_, c_abs.group_name_ids, c_abs.channel_ids,
         c_abs.weights) = map(list, db.getColumnDataFromTable(
             'config_table', order_by_str='config_row_id',
             column_name_list=['config_row_id', 'group_name_id', 'channel_id',
                               'config_weight'],
             condition_str='config_id={0:d}'.format(config_id)))

        if c_abs.channel_ids != []:
            self.createDockWidget(c_abs)

    #----------------------------------------------------------------------
    def openContextMenu(self):
        """
        Default context menu would show nothing if no dockwidget has been
        created yet. However, once a dockwidget is created, it will show
        the list of dockwidgets to allow users to show/hide dockwidgets.

        Instead of this default context menu, a custom context menu will be shown.
        """

        pass

    #----------------------------------------------------------------------
    def createDockWidget(self, config_abstract_model):
        """"""

        isinstance(config_abstract_model, ConfigAbstractModel)

        dockWidget = TinkerDockWidget(config_abstract_model, self)
        self.addDockWidget(Qt.DockWidgetArea(1), dockWidget)

        dockWidget.lineEdit_config_username.setReadOnly(True)
        dockWidget.lineEdit_config_timestamp.setReadOnly(True)
        dockWidget.textEdit_config_description.setReadOnly(True)
        dockWidget.lineEdit_snapshot_username.setReadOnly(True)
        dockWidget.lineEdit_snapshot_timestamp.setReadOnly(True)
        dockWidget.textEdit_snapshot_description.setReadOnly(True)

        self.dockWidgetList.append(dockWidget)
        dockWidget.setObjectName('dock{0:d}'.format(self.next_dockWidget_index))

        dock_title = config_abstract_model.name
        if dock_title == '':
            dock_title = 'untitled{0:d}'.format(self.next_dockWidget_index)

        self.next_dockWidget_index += 1

        # This tile appears at the bottom of the dock tab only when more than
        # one docks are tabified. And this is not editable.
        dockWidget.setWindowTitle(dock_title)

        # This title appears at the top of the dock either when docked,
        # tabified, or floated. And this is editable.
        dockWidget.customTitleBar.title.setText(dock_title)

        dockWidget.setFloating(False) # Dock the new dockwidget by default
        if len(self.dockWidgetList) >= 2:
            self.tabifyDockWidget(self.dockWidgetList[-2], dockWidget)
        #dockWidget.raise_()

        dockWidget.stackedWidget.setCurrentWidget(dockWidget.page_table)
        #dockWidget.stackedWidget.setCurrentWidget(dockWidget.page_tree)

        dockWidget.updateMetaDataTab()

        #self.updateMetadataTab(dockWidget, base_model, page='config')
        #if base_model.isSnapshot():
            #self.updateMetadataTab(dockWidget, base_model, page='snapshot')


########################################################################
class TinkerApp(QObject):
    """"""

    #----------------------------------------------------------------------
    def __init__(self, use_cached_lattice=False):
        """Constructor"""

        QObject.__init__(self)

        self.use_cached_lattice = use_cached_lattice

        self._initView()

        self.connect(self.view.actionNewConfig,SIGNAL('triggered(bool)'),
                     self.openNewConfigSetupDialog)

    #----------------------------------------------------------------------
    def _initView(self):
        """"""

        self.view = TinkerView()

    #----------------------------------------------------------------------
    def openNewConfigSetupDialog(self, _):
        """"""

        result = tinkerConfigSetupDialog.make(
            isModal=True, parentWindow=self.view,
            use_cached_lattice=self.use_cached_lattice)

        config_abstract_model = result.model.abstract

        if config_abstract_model.channel_ids != []:
            self.view.createDockWidget(config_abstract_model)

#----------------------------------------------------------------------
def make(use_cached_lattice=False):
    """"""

    app = TinkerApp(use_cached_lattice=use_cached_lattice)
    app.view.show()

    return app

#----------------------------------------------------------------------
def main():
    """"""

    args = sys.argv

    if len(args) == 1:
        use_cached_lattice = False
    elif len(args) == 2:
        if args[1] == '--use-cache':
            use_cached_lattice = True
        else:
            use_cached_lattice = False

    if ap.machines._lat is None:
        try:
            ap.machines.load(config.HLA_MACHINE, use_cache=use_cached_lattice)
        except RuntimeError as e:
            # TODO: remove this error handling
            config.HLA_MACHINE = 'nsls2v2'
            ap.machines.load(config.HLA_MACHINE, use_cache=use_cached_lattice)

    # If Qt is to be used (for any GUI) then the cothread library needs to
    # be informed, before any work is done with Qt. Without this line
    # below, the GUI window will not show up and freeze the program.
    cothread.iqt()

    app = make(use_cached_lattice=use_cached_lattice)

    cothread.WaitForQuit()

#----------------------------------------------------------------------
if __name__ == "__main__" :
    main()
