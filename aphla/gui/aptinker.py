#! /usr/bin/env python
from __future__ import print_function, division, absolute_import

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
import os.path as osp
import numpy as np
from copy import deepcopy
import json
from subprocess import Popen, PIPE
import argparse

import cothread
from cothread.catools import caget, caput, camonitor, FORMAT_TIME

from PyQt4.QtCore import (
    Qt, QObject, SIGNAL, QSize, QSettings, QRect, QMetaObject, QModelIndex,
    Q_ARG, Q_CLASSINFO, pyqtSlot
)
from PyQt4.QtGui import (
    QApplication, QMainWindow, QDockWidget, QWidget, QTabWidget,
    QSortFilterProxyModel, QGridLayout, QSplitter, QTreeView, QTableView,
    QVBoxLayout, QHBoxLayout, QPushButton, QSpacerItem, QCheckBox, QLineEdit,
    QSizePolicy, QComboBox, QLabel, QTextEdit, QStackedWidget,
    QAbstractItemView, QToolButton, QStyle, QMessageBox, QIcon, QDialog, QFont,
    QIntValidator, QItemSelectionModel, QMenu, QAction, QInputDialog,
    QFileDialog
)
from PyQt4.QtDBus import (
    QDBusConnection, QDBusInterface, QDBusReply, QDBusAbstractInterface,
    QDBusAbstractAdaptor)

import aphla as ap
import utils.gui_icons
from aphla.gui.utils.orderselector import ColumnsDialog
from Qt4Designer_files.ui_aptinker import Ui_MainWindow
from TinkerUtils.ui_aptinker_pref import Ui_Dialog as Ui_Dialog_Pref
from TinkerUtils.ui_configSaveDialog import Ui_Dialog as Ui_Dialog_ConfSave
from TinkerUtils import (config, tinkerModels, datestr, datestr_ns,
                         tinkerConfigSetupDialog, tinkerConfigDBSelector,
                         tinkerSnapshotDBSelector)
from TinkerUtils.tinkerModels import (
    getuserinfo,
    ConfigAbstractModel, ConfigTableModel,
    SnapshotAbstractModel, SnapshotTableModel)
from TinkerUtils.tinkerdb import (TinkerMainDatabase)
from TinkerUtils.dbviews import (
    ConfigDBViewWidget, SnapshotDBViewWidget, ConfigMetaDBViewWidget,
    ConfigDBTableViewItemDelegate, SnapshotDBTableViewItemDelegate)

HOME_PATH             = osp.expanduser('~')
APHLA_USER_CONFIG_DIR = osp.join(HOME_PATH, '.aphla')
if not osp.exists(APHLA_USER_CONFIG_DIR):
    os.makedirs(APHLA_USER_CONFIG_DIR)

PREF_JSON_FILEPATH = osp.join(APHLA_USER_CONFIG_DIR,
                              'aptinker_startup_pref.json')

# Check existence of DB files. Initialize DB file, if not.
# Need `vacuum` option to be False. Otherwise, this section could take long.
_ = TinkerMainDatabase(); _.close(vacuum=False)

#----------------------------------------------------------------------
def get_preferences(default=False):
    """"""

    if (not default) and osp.exists(PREF_JSON_FILEPATH):
        with open(PREF_JSON_FILEPATH, 'r') as f:
            pref = json.load(f)
    else:
        # Use default startup preferences
        pref = dict(
            font_size=16,
            vis_col_keys=config.DEF_VIS_COL_KEYS['snapshot_view'],
            view_mode='Channel-based View',
            caget_timeout=3.0, caput_timeout=3.0,
            auto_caget_periodic_checked=False,
            auto_caget_periodic_interval=5.0,
            auto_caget_after_caput_checked=True,
            auto_caget_after_caput_delay=1.0
        )

    return pref

#----------------------------------------------------------------------
def get_running_aptinker_pids():
    """"""

    p1 = Popen(['ps'], stdout=PIPE, stderr=PIPE)
    p2 = Popen(['grep', 'aptinker'], stdin=p1.stdout, stdout=PIPE,
               stderr=PIPE)
    out, err = p2.communicate()

    if err:
        print('ERROR:')
        print(err)
        return None

    if out == '':
        return None
    else:
        pids = [int(line.split()[0]) for line in out.splitlines()]

        this_pid = os.getpid()
        if this_pid in pids:
            pids.remove(this_pid)
            if pids == []:
                pids = None

        return pids

########################################################################
class ConfigSaveDialog(QDialog, Ui_Dialog_ConfSave):
    """"""

    #----------------------------------------------------------------------
    def __init__(self, config_title):
        """Constructor"""

        QDialog.__init__(self)

        self.setupUi(self)

        self.setWindowFlags(Qt.Window) # To add Maximize & Minimize buttons
        self.setWindowTitle('Save Configuration')

        self.lineEdit_name.setText(config_title)
        self.plainTextEdit_description.setReadOnly(False)
        self.lineEdit_masar_id.setText('')

    #----------------------------------------------------------------------
    def closeEvent(self, event):
        """"""

        event.accept()

    #----------------------------------------------------------------------
    def accept(self):
        """"""

        super(ConfigSaveDialog, self).accept() # will close the dialog

    #----------------------------------------------------------------------
    def reject(self):
        """"""

        super(ConfigSaveDialog, self).reject() # will close the dialog

########################################################################
class SnapshotSaveDialog(QDialog, Ui_Dialog_ConfSave):
    """"""

    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""

        QDialog.__init__(self)

        self.setupUi(self)

        self.setWindowFlags(Qt.Window) # To add Maximize & Minimize buttons
        self.setWindowTitle('Save Snapshot')

        self.lineEdit_name.setText('')
        self.plainTextEdit_description.setReadOnly(False)
        self.lineEdit_masar_id.setText('')

    #----------------------------------------------------------------------
    def closeEvent(self, event):
        """"""

        event.accept()

    #----------------------------------------------------------------------
    def accept(self):
        """"""

        super(SnapshotSaveDialog, self).accept() # will close the dialog

    #----------------------------------------------------------------------
    def reject(self):
        """"""

        super(SnapshotSaveDialog, self).reject() # will close the dialog

########################################################################
class PreferencesEditor(QDialog, Ui_Dialog_Pref):
    """"""

    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""

        QDialog.__init__(self)

        self.setupUi(self)

        self.setWindowTitle('Startup Preferences')

        self.default_pref = get_preferences(default=True)

        (self.all_col_keys, self.all_col_names) = \
            map(list, config.COL_DEF.getColumnDataFromTable(
                'column_table',
                column_name_list=['column_key', 'short_descrip_name'])
                )

        self.load_pref_json()

        self.connect(self.pushButton_restore_default, SIGNAL('clicked()'),
                     self.restore_default_pref)
        self.connect(self.pushButton_edit_visible_columns, SIGNAL('clicked()'),
                     self.launchColumnsDialog)

        self.connect(self.lineEdit_caget_timeout, SIGNAL('editingFinished()'),
                     self.validate_time_duration)
        self.connect(self.lineEdit_caput_timeout, SIGNAL('editingFinished()'),
                     self.validate_time_duration)
        self.connect(self.lineEdit_auto_caget_periodic,
                     SIGNAL('editingFinished()'),
                     self.validate_time_duration)
        self.connect(self.lineEdit_auto_caget_after_caput,
                     SIGNAL('editingFinished()'),
                     self.validate_time_duration)

    #----------------------------------------------------------------------
    def validate_time_duration(self):
        """"""

        sender = self.sender()

        try:
            float(sender.text())
        except:
            sender.setText('nan')

    #----------------------------------------------------------------------
    def load_pref_json(self):
        """"""

        self.pref = get_preferences()

        self.update_view()

    #----------------------------------------------------------------------
    def save_pref_json(self):
        """"""

        with open(PREF_JSON_FILEPATH, 'w') as f:
            json.dump(self.pref, f, indent=3, sort_keys=True,
                      separators=(',', ': '))

    #----------------------------------------------------------------------
    def restore_default_pref(self):
        """"""

        self.pref = deepcopy(self.default_pref)
        self.update_view()

    #----------------------------------------------------------------------
    def update_view(self):
        """"""

        index = self.comboBox_font_size.findText(str(self.pref['font_size']),
                                                 Qt.MatchExactly)
        self.comboBox_font_size.setCurrentIndex(index)

        self.update_column_list_only()

        index = self.comboBox_view_mode.findText(self.pref['view_mode'],
                                                 Qt.MatchExactly)
        self.comboBox_view_mode.setCurrentIndex(index)

        self.lineEdit_caget_timeout.setText(str(self.pref['caget_timeout']))
        self.lineEdit_caput_timeout.setText(str(self.pref['caput_timeout']))

        self.checkBox_auto_caget_periodic.setChecked(
            self.pref['auto_caget_periodic_checked'])
        self.lineEdit_auto_caget_periodic.setText(
            str(self.pref['auto_caget_periodic_interval']))

        self.checkBox_auto_caget_after_caput.setChecked(
            self.pref['auto_caget_after_caput_checked'])
        self.lineEdit_auto_caget_after_caput.setText(
            str(self.pref['auto_caget_after_caput_delay']))

    #----------------------------------------------------------------------
    def update_column_list_only(self):
        """"""

        self.listWidget_visible_columns.clear()

        vis_col_names = [self.all_col_names[self.all_col_keys.index(k)]
                         for k in self.pref['vis_col_keys']]

        self.listWidget_visible_columns.addItems(vis_col_names)

    #----------------------------------------------------------------------
    def launchColumnsDialog(self):
        """"""

        visible_col_names = [self.all_col_names[self.all_col_keys.index(k)]
                             for k in self.pref['vis_col_keys']]
        permanently_visible_col_keys = ['group_name']
        permanently_visible_col_names = [
            self.all_col_names[self.all_col_keys.index(k)]
            for k in permanently_visible_col_keys]

        dialog = ColumnsDialog(self.all_col_names, visible_col_names,
                               permanently_visible_col_names, parentWindow=self)
        dialog.exec_()

        if dialog.output is not None:
            self.pref['vis_col_keys'] = [
                self.all_col_keys[self.all_col_names.index(col_name)]
                for col_name in dialog.output]
            self.update_column_list_only()

    #----------------------------------------------------------------------
    def accept(self):
        """"""

        self.pref['font_size'] = int(self.comboBox_font_size.currentText())

        # self.pref['vis_col_keys'] is already updated whenever the list is
        # modified by column dialog. So, there is no need to update here.

        self.pref['view_mode'] = self.comboBox_view_mode.currentText()

        self.pref['caget_timeout'] = float(self.lineEdit_caget_timeout.text())
        self.pref['caput_timeout'] = float(self.lineEdit_caput_timeout.text())

        self.pref['auto_caget_periodic_checked'] = \
            self.checkBox_auto_caget_periodic.isChecked()
        self.pref['auto_caget_periodic_interval'] = \
            float(self.lineEdit_auto_caget_periodic.text())

        self.pref['auto_caget_after_caput_checked'] = \
            self.checkBox_auto_caget_after_caput.isChecked()
        self.pref['auto_caget_after_caput_delay'] = \
            float(self.lineEdit_auto_caget_after_caput.text())

        self.save_pref_json()

        super(PreferencesEditor, self).accept() # will hide the dialog

    #----------------------------------------------------------------------
    def reject(self):
        """"""

        super(PreferencesEditor, self).reject() # will hide the dialog

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
    def __init__(self, config_abstract_model, parent, ss_abstract=None):
        """Constructor"""

        self._main_settings = parent._settings

        isinstance(config_abstract_model, ConfigAbstractModel)
        isinstance(ss_abstract, SnapshotAbstractModel)

        self.config_abstract = config_abstract_model

        pref = get_preferences()
        self.ss_abstract = SnapshotAbstractModel(config_abstract_model,
                                                 pref['vis_col_keys'])
        if ss_abstract is not None:
            _sa = self.ss_abstract
            _sa.ss_id         = ss_abstract.ss_id
            _sa.name          = ss_abstract.name
            _sa.description   = ss_abstract.description
            _sa.ss_ctime      = ss_abstract.ss_ctime
            _sa.ref_step_size = ss_abstract.ref_step_size
            _sa.synced_group_weight = ss_abstract.synced_group_weight

            _sa.visible_col_keys = pref['vis_col_keys']

        self.ss_table = SnapshotTableModel(self.ss_abstract)
        if ss_abstract is not None:
            from_DB = True
            self.ss_table.update_snapshot_columns(from_DB)


        self._initUI(parent)

        for col_key, editable in self.ss_abstract.user_editable.items():
            if editable:
                self.ssDBView.comboBox_column_name.addItem(
                    self.ss_abstract.all_col_names[
                        self.ss_abstract.all_col_keys.index(col_key)])
        self.ssDBView.comboBox_column_name.setCurrentIndex(0)

        self.lineEdit_auto_caget_after_caput_delay.setText(
            str(self.ss_abstract.auto_caget_delay_after_caput))
        self.lineEdit_ref_step_size.setText('{0:.8g}'.format(
            self.ss_abstract.ref_step_size))
        self.checkBox_synced_group_weight.setChecked(
            self.ss_abstract.synced_group_weight)

        self._settings = QSettings('APHLA', 'TinkerDockWidget')

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

        vis_col_names = [
            self.ss_abstract.all_col_names[
                self.ss_abstract.all_col_keys.index(k)]
            for k in self.ss_abstract.visible_col_keys]
        self.ssDBView.on_column_selection_change(vis_col_names,
                                                 force_visibility_update=True)

        self.last_caget_sent_ts_lineEdits_updated = False
        self.last_caput_sent_ts_lineEdits_updated = False
        self.update_last_ca_sent_ts()

        self.customTitleBar = CustomDockWidgetTitleBar(self)
        self.setTitleBarWidget(self.customTitleBar)
        self.connect(self.customTitleBar, SIGNAL('customDockTitleChanged'),
                     self._updateWindowTitle)

        self.connect(self.pushButton_update, SIGNAL('clicked()'),
                     self.ss_abstract.update_pv_vals)
        self.connect(self.lineEdit_ref_step_size, SIGNAL('editingFinished()'),
                     self.update_ref_step_size)
        self.connect(self.lineEdit_mult_factor, SIGNAL('editingFinished()'),
                     self.update_mult_factor)

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
        self.connect(self.pushButton_multiply, SIGNAL('clicked()'),
                     self.ss_abstract.multiply)
        self.connect(self.pushButton_divide, SIGNAL('clicked()'),
                     self.ss_abstract.divide)

        self.connect(self.lineEdit_caget_timeout, SIGNAL('editingFinished()'),
                     self.validate_timeout)
        self.connect(self.lineEdit_caput_timeout, SIGNAL('editingFinished()'),
                     self.validate_timeout)

        self.connect(self.ssDBView.pushButton_load_column_from_file,
                     SIGNAL('clicked()'), self.load_column_from_file)

        self.connect(self.ssDBView.pushButton_restore_init,
                     SIGNAL('clicked()'), self.restore_IniSP)

        self.connect(self.ss_abstract, SIGNAL('pvValuesUpdatedInSSAbstract'),
                     self.update_last_ca_sent_ts)

        self.connect(self.ssDBView, SIGNAL('ssDBViewVisibleColumnsChagned'),
                     self.ss_abstract.on_visible_column_change)
        self.connect(self.ssDBView, SIGNAL('ssDBViewVisibleColumnsChagned'),
                     self.ss_table.on_visible_column_change)

        self.visible = False
        self.connect(self, SIGNAL('visibilityChanged(bool)'),
                     self.updateVisibility)

        self.checkBox_auto_update.setToolTip(
            '''Start auto-update when the box is checked and a valid float
is specfied. If it does not start, try toggling the check states.''')
        self.auto_updater = None
        self.connect(self.checkBox_auto_update, SIGNAL('stateChanged(int)'),
                     self.toggle_auto_updater)

    #----------------------------------------------------------------------
    def toggle_auto_updater(self, state):
        """"""

        if state != Qt.Checked:
            if self.auto_updater is not None:
                # Stop the timer
                self.auto_updater.reset(None)
            return

        try:
            period = float(self.lineEdit_auto_update_interval.text()) # [s]
        except:
            # Invalid period specified. Do not start auto-updater.
            return

        if self.auto_updater is None:
            self.auto_updater = cothread.Timer(
                period, self.ss_abstract.update_pv_vals,
                retrigger=True, reuse=True)
        else:
            self.auto_updater.reset(period, retrigger=True)

    #----------------------------------------------------------------------
    def updateVisibility(self, visible):
        """
        If floating, the dockWidget will be "visible".

        If tabified, only the top dockWidget will be "visible".
        """

        self.visible = visible

    #----------------------------------------------------------------------
    def update_last_ca_sent_ts(self):
        """"""

        if self.ss_abstract.caget_sent_ts_second is not None:
            self.lineEdit_caget_sent_ts_second_step.setText(datestr(
                self.ss_abstract.caget_sent_ts_second))
            self.lineEdit_caget_sent_ts_second_target.setText(datestr(
                self.ss_abstract.caget_sent_ts_second))
            if not self.last_caget_sent_ts_lineEdits_updated:
                self.resizeLineEditToContents(
                    self.lineEdit_caget_sent_ts_second_step)
                self.resizeLineEditToContents(
                    self.lineEdit_caget_sent_ts_second_target)
                self.last_caget_sent_ts_lineEdits_updated = True
        if self.ss_abstract.caput_sent_ts_second is not None:
            self.lineEdit_caput_sent_ts_second_step.setText(datestr(
                self.ss_abstract.caput_sent_ts_second))
            self.lineEdit_caput_sent_ts_second_target.setText(datestr(
                self.ss_abstract.caput_sent_ts_second))
            if not self.last_caput_sent_ts_lineEdits_updated:
                self.resizeLineEditToContents(
                    self.lineEdit_caput_sent_ts_second_step)
                self.resizeLineEditToContents(
                    self.lineEdit_caput_sent_ts_second_target)
                self.last_caput_sent_ts_lineEdits_updated = True

    #----------------------------------------------------------------------
    def validate_timeout(self):
        """"""

        sender = self.sender()

        try:
            timeout = float(sender.text())
        except:
            sender.setText('nan')
            timeout = None

        if sender == self.lineEdit_caget_timeout:
            self.ss_abstract.caget_timeout = timeout
        else:
            self.ss_abstract.caput_timeout = timeout

    #----------------------------------------------------------------------
    def closeEvent(self, event):
        """"""

        self.saveViewSizeSettings()
        self.saveMiscSettings()

        self.emit(SIGNAL('dockAboutTobeClosed'), self.sender())

        event.accept()

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
    def update_mult_factor(self):
        """"""

        try:
            new_mult_factor = float(self.lineEdit_mult_factor.text())
        except:
            new_mult_factor = float('nan')
            self.lineEdit_mult_factor.setText('nan')

        self.ss_abstract.mult_factor = new_mult_factor

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
        dockWidgetContents.setContentsMargins(0, 0, 0, 0)
        top_gridLayout = QGridLayout(dockWidgetContents)
        #
        self.splitter = QSplitter(dockWidgetContents)
        self.splitter.setOrientation(Qt.Vertical)
        #
        self.ssDBView = SnapshotDBViewWidget(self.splitter)
        self.stackedWidget = self.ssDBView.stackedWidget
        self.page_tree  = self.ssDBView.page_tree
        self.page_table = self.ssDBView.page_table
        self.treeView  = self.ssDBView.treeView
        self.tableView = self.ssDBView.tableView
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

        self.tableView.setItemDelegate(SnapshotDBTableViewItemDelegate(
            self.tableView, self.ss_table, parent))
        self.tableView.setEditTriggers(QAbstractItemView.SelectedClicked)

        button_size = QSize(32,32)

        self.tabWidget_mode = QTabWidget(self.splitter)

        ## Step Mode Tab
        self.tab_step_mode = QWidget()
        verticalLayout_1 = QVBoxLayout(self.tab_step_mode)
        horizontalLayout_1 = QHBoxLayout()
        self.pushButton_step_up = QPushButton(self.tab_step_mode)
        self.pushButton_step_up.setToolTip(
            'Step Up Setpoints (not applicable to setpoint PVs whose\n'
            '"StepSize" or "Cur.SP" values are "nan", or whose "caput ON"\n'
            'are unchecked)')
        self.pushButton_step_up.setIcon(QIcon(':/plus48.png'))
        self.pushButton_step_up.setIconSize(button_size)
        horizontalLayout_1.addWidget(self.pushButton_step_up)
        self.pushButton_step_down = QPushButton(self.tab_step_mode)
        self.pushButton_step_down.setToolTip(
            'Step Down Setpoints (not applicable to setpoint PVs whose\n'
            '"StepSize" or "Cur.SP" values are "nan", or whose "caput ON"\n'
            'are unchecked)')
        self.pushButton_step_down.setIcon(QIcon(':/minus48.png'))
        self.pushButton_step_down.setIconSize(button_size)
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
        self.pushButton_multiply.setToolTip(
            'Multiply Setpoints (not applicable to setpoint PVs whose\n'
            '"Cur.SP" values are "nan", or whose "caput ON" are unchecked)')
        self.pushButton_multiply.setIcon(QIcon(':/multiply48.png'))
        self.pushButton_multiply.setIconSize(button_size)
        horizontalLayout_1.addWidget(self.pushButton_multiply)
        self.pushButton_divide = QPushButton(self.tab_step_mode)
        self.pushButton_divide.setToolTip(
            'Divide Setpoints (not applicable to setpoint PVs whose\n'
            '"Cur.SP" values are "nan", or whose "caput ON" are unchecked)')
        self.pushButton_divide.setIcon(QIcon(':/divide48.png'))
        self.pushButton_divide.setIconSize(button_size)
        horizontalLayout_1.addWidget(self.pushButton_divide)
        label_tab_step_2 = QLabel(self.tab_step_mode)
        label_tab_step_2.setText('Multiplication Factor:')
        horizontalLayout_1.addWidget(label_tab_step_2)
        self.lineEdit_mult_factor = QLineEdit(self.tab_step_mode)
        self.lineEdit_mult_factor.setText('1.0')
        horizontalLayout_1.addWidget(self.lineEdit_mult_factor)
        spacerItem_1 = QSpacerItem(40,20,QSizePolicy.Expanding,
                                   QSizePolicy.Minimum)
        horizontalLayout_1.addItem(spacerItem_1)
        verticalLayout_1.addLayout(horizontalLayout_1)

        hLayout = QHBoxLayout()
        label = QLabel(self.tab_step_mode)
        label.setText('Last caget sent on')
        hLayout.addWidget(label)
        self.lineEdit_caget_sent_ts_second_step = QLineEdit(self.tab_step_mode)
        self.lineEdit_caget_sent_ts_second_step.setText('Not sent yet')
        self.lineEdit_caget_sent_ts_second_step.setReadOnly(True)
        hLayout.addWidget(self.lineEdit_caget_sent_ts_second_step)
        label = QLabel(self.tab_step_mode)
        label.setText('Last caput sent on')
        hLayout.addWidget(label)
        self.lineEdit_caput_sent_ts_second_step = QLineEdit(self.tab_step_mode)
        self.lineEdit_caput_sent_ts_second_step.setText('Not sent yet')
        self.lineEdit_caput_sent_ts_second_step.setReadOnly(True)
        hLayout.addWidget(self.lineEdit_caput_sent_ts_second_step)
        spacerItem = QSpacerItem(40, 20, QSizePolicy.Expanding,
                                 QSizePolicy.Minimum)
        hLayout.addItem(spacerItem)
        verticalLayout_1.addLayout(hLayout)

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
        self.checkBox_auto_caget_after_caput.setText(
            'Auto caget after caput: Delay [s]')
        self.checkBox_auto_caget_after_caput.setChecked(True)
        horizontalLayout_2.addWidget(self.checkBox_auto_caget_after_caput)
        self.lineEdit_auto_caget_after_caput_delay = QLineEdit(
            self.tab_step_mode)
        self.lineEdit_auto_caget_after_caput_delay.setText('1.0')
        horizontalLayout_2.addWidget(self.lineEdit_auto_caget_after_caput_delay)
        spacerItem_2 = QSpacerItem(40, 20, QSizePolicy.Expanding,
                                   QSizePolicy.Minimum)
        horizontalLayout_2.addItem(spacerItem_2)
        verticalLayout_1.addLayout(horizontalLayout_2)
        self.tabWidget_mode.addTab(self.tab_step_mode,'Step Mode')

        spacerItem = QSpacerItem(40, 20, QSizePolicy.Minimum,
                                 QSizePolicy.Expanding)
        verticalLayout_1.addItem(spacerItem)

        ## Target Mode Tab
        self.tab_target_mode = QWidget()

        vLayout = QVBoxLayout(self.tab_target_mode)

        hLayout = QHBoxLayout()
        self.pushButton_copy = QPushButton(self.tab_target_mode)
        self.pushButton_copy.setText('Copy')
        hLayout.addWidget(self.pushButton_copy)
        self.comboBox_setpoint_copy_source = QComboBox(self.tab_target_mode)
        self.comboBox_setpoint_copy_source.addItem('Current')
        self.comboBox_setpoint_copy_source.addItem('Initial')
        self.comboBox_setpoint_copy_source.addItem('Snapshot')
        hLayout.addWidget(self.comboBox_setpoint_copy_source)
        label = QLabel(self.tab_target_mode)
        label.setText('setpoints into Target Setpoints Column')
        hLayout.addWidget(label)
        spacerItem = QSpacerItem(40, 20, QSizePolicy.Expanding,
                                 QSizePolicy.Minimum)
        hLayout.addItem(spacerItem)
        vLayout.addLayout(hLayout)

        hLayout_1 = QHBoxLayout()
        self.pushButton_start = QPushButton(self.tab_target_mode)
        self.pushButton_start.setText('Start')
        hLayout_1.addWidget(self.pushButton_start)
        self.pushButton_stop = QPushButton(self.tab_target_mode)
        self.pushButton_stop.setText('Stop')
        hLayout_1.addWidget(self.pushButton_stop)
        self.pushButton_revert = QPushButton(self.tab_target_mode)
        self.pushButton_revert.setText('Revert')
        hLayout_1.addWidget(self.pushButton_revert)
        label_tab_target_1 = QLabel(self.tab_target_mode)
        label_tab_target_1.setText('Number of Steps:')
        hLayout_1.addWidget(label_tab_target_1)
        self.lineEdit_nSteps = QLineEdit(self.tab_target_mode)
        hLayout_1.addWidget(self.lineEdit_nSteps)
        label_tab_target_2 = QLabel(self.tab_target_mode)
        label_tab_target_2.setText('Wait after Each Step [s]:')
        hLayout_1.addWidget(label_tab_target_2)
        self.lineEdit_wait_after_each_step = QLineEdit(self.tab_target_mode)
        hLayout_1.addWidget(self.lineEdit_wait_after_each_step)
        spacerItem = QSpacerItem(40, 20, QSizePolicy.Expanding,
                                 QSizePolicy.Minimum)
        hLayout_1.addItem(spacerItem)
        vLayout.addLayout(hLayout_1)

        hLayout_2 = QHBoxLayout()
        label = QLabel(self.tab_step_mode)
        label.setText('Last caget sent on')
        hLayout_2.addWidget(label)
        self.lineEdit_caget_sent_ts_second_target = QLineEdit(self.tab_step_mode)
        self.lineEdit_caget_sent_ts_second_target.setText('Not sent yet')
        self.lineEdit_caget_sent_ts_second_target.setReadOnly(True)
        hLayout_2.addWidget(self.lineEdit_caget_sent_ts_second_target)
        label = QLabel(self.tab_step_mode)
        label.setText('Last caput sent on')
        hLayout_2.addWidget(label)
        self.lineEdit_caput_sent_ts_second_target = QLineEdit(self.tab_step_mode)
        self.lineEdit_caput_sent_ts_second_target.setText('Not sent yet')
        self.lineEdit_caput_sent_ts_second_target.setReadOnly(True)
        hLayout_2.addWidget(self.lineEdit_caput_sent_ts_second_target)
        spacerItem = QSpacerItem(40, 20, QSizePolicy.Expanding,
                                 QSizePolicy.Minimum)
        hLayout_2.addItem(spacerItem)
        vLayout.addLayout(hLayout_2)

        spacerItem = QSpacerItem(40, 20, QSizePolicy.Minimum,
                                 QSizePolicy.Expanding)
        vLayout.addItem(spacerItem)

        self.tabWidget_mode.addTab(self.tab_target_mode,'Target Mode')

        ## Timeout Tab
        default_pref = get_preferences(default=True)
        self.tab_timeout = QWidget()
        horizontalLayout = QHBoxLayout()
        label = QLabel('caget [seconds]')
        horizontalLayout.addWidget(label)
        self.lineEdit_caget_timeout = QLineEdit(self.tab_timeout)
        self.lineEdit_caget_timeout.setText(str(default_pref['caget_timeout']))
        self.lineEdit_caget_timeout.setToolTip(
            'If nan, no timeout will occur. If 0, it will timeout immediately.')
        horizontalLayout.addWidget(self.lineEdit_caget_timeout)
        spacerItem = QSpacerItem(40, 20, QSizePolicy.Expanding,
                                 QSizePolicy.Minimum)
        horizontalLayout.addItem(spacerItem)
        horizontalLayout_2 = QHBoxLayout()
        label = QLabel('caput [seconds]')
        horizontalLayout_2.addWidget(label)
        self.lineEdit_caput_timeout = QLineEdit(self.tab_timeout)
        self.lineEdit_caput_timeout.setText(str(default_pref['caput_timeout']))
        self.lineEdit_caput_timeout.setToolTip(
            'If nan, no timeout will occur. If 0, it will timeout immediately.')
        horizontalLayout_2.addWidget(self.lineEdit_caput_timeout)
        spacerItem = QSpacerItem(40, 20, QSizePolicy.Expanding,
                                 QSizePolicy.Minimum)
        horizontalLayout_2.addItem(spacerItem)
        spacerItem = QSpacerItem(40, 20, QSizePolicy.Minimum,
                                         QSizePolicy.Expanding)
        verticalLayout = QVBoxLayout(self.tab_timeout)
        verticalLayout.addLayout(horizontalLayout)
        verticalLayout.addLayout(horizontalLayout_2)
        verticalLayout.addItem(spacerItem)
        self.tabWidget_mode.addTab(self.tab_timeout, 'CA Timeout')

        self.tabWidget_metadata = QTabWidget(self.splitter)
        #
        ## Config Metadata Tab
        self.tab_config_metadata = QWidget()
        verticalLayout_21 = QVBoxLayout(self.tab_config_metadata)
        horizontalLayout_21 = QHBoxLayout()
        label = QLabel(self.tab_config_metadata)
        label.setText('ID')
        horizontalLayout_21.addWidget(label)
        self.lineEdit_config_id = QLineEdit(self.tab_config_metadata)
        self.lineEdit_config_id.setReadOnly(True)
        horizontalLayout_21.addWidget(self.lineEdit_config_id)
        label = QLabel(self.tab_config_metadata)
        label.setText('Config Name')
        horizontalLayout_21.addWidget(label)
        self.lineEdit_config_name = QLineEdit(self.tab_config_metadata)
        self.lineEdit_config_name.setReadOnly(True)
        horizontalLayout_21.addWidget(self.lineEdit_config_name)
        label = QLabel(self.tab_config_metadata)
        label.setText('Created by')
        horizontalLayout_21.addWidget(label)
        self.lineEdit_config_username = QLineEdit(self.tab_config_metadata)
        self.lineEdit_config_username.setReadOnly(True)
        horizontalLayout_21.addWidget(self.lineEdit_config_username)
        label = QLabel(self.tab_config_metadata)
        label.setText('Created on')
        horizontalLayout_21.addWidget(label)
        self.lineEdit_config_timestamp = QLineEdit(self.tab_config_metadata)
        self.lineEdit_config_timestamp.setReadOnly(True)
        horizontalLayout_21.addWidget(self.lineEdit_config_timestamp)
        spacerItem_5 = QSpacerItem(40, 20, QSizePolicy.Expanding,
                                   QSizePolicy.Minimum)
        horizontalLayout_21.addItem(spacerItem_5)
        verticalLayout_21.addLayout(horizontalLayout_21)
        horizontalLayout_22 = QHBoxLayout()
        verticalLayout_22 = QVBoxLayout()
        label = QLabel(self.tab_config_metadata)
        label.setText('Description')
        verticalLayout_22.addWidget(label)
        spacerItem_6 = QSpacerItem(20, 40, QSizePolicy.Minimum,
                                   QSizePolicy.Expanding)
        verticalLayout_22.addItem(spacerItem_6)
        horizontalLayout_22.addLayout(verticalLayout_22)
        self.textEdit_config_description = QTextEdit(self.tab_config_metadata)
        self.textEdit_config_description.setReadOnly(True)
        horizontalLayout_22.addWidget(self.textEdit_config_description)
        verticalLayout_21.addLayout(horizontalLayout_22)
        self.tabWidget_metadata.addTab(self.tab_config_metadata,
                                       'Config Metadata')
        #
        ## Snapshot Metadata Tab
        self.tab_snapshot_metadata = QWidget()
        verticalLayout_31 = QVBoxLayout(self.tab_snapshot_metadata)
        horizontalLayout_31 = QHBoxLayout()
        label = QLabel(self.tab_snapshot_metadata)
        label.setText('ID')
        horizontalLayout_31.addWidget(label)
        self.lineEdit_ss_id = QLineEdit(self.tab_snapshot_metadata)
        self.lineEdit_ss_id.setReadOnly(True)
        horizontalLayout_31.addWidget(self.lineEdit_ss_id)
        label = QLabel(self.tab_snapshot_metadata)
        label.setText('Snapshot Name')
        horizontalLayout_31.addWidget(label)
        self.lineEdit_ss_name = QLineEdit(self.tab_snapshot_metadata)
        self.lineEdit_ss_name.setReadOnly(True)
        horizontalLayout_31.addWidget(self.lineEdit_ss_name)
        label = QLabel(self.tab_snapshot_metadata)
        label.setText('Created by')
        horizontalLayout_31.addWidget(label)
        self.lineEdit_snapshot_username = QLineEdit(self.tab_snapshot_metadata)
        self.lineEdit_snapshot_username.setReadOnly(True)
        horizontalLayout_31.addWidget(self.lineEdit_snapshot_username)
        label = QLabel(self.tab_snapshot_metadata)
        label.setText('Created on')
        horizontalLayout_31.addWidget(label)
        self.lineEdit_snapshot_timestamp = QLineEdit(self.tab_snapshot_metadata)
        self.lineEdit_snapshot_timestamp.setReadOnly(True)
        horizontalLayout_31.addWidget(self.lineEdit_snapshot_timestamp)
        spacerItem_7 = QSpacerItem(40, 20, QSizePolicy.Expanding,
                                   QSizePolicy.Minimum)
        horizontalLayout_31.addItem(spacerItem_7)
        verticalLayout_31.addLayout(horizontalLayout_31)
        horizontalLayout_32 = QHBoxLayout()
        verticalLayout_32 = QVBoxLayout()
        label = QLabel(self.tab_snapshot_metadata)
        label.setText('Description')
        verticalLayout_32.addWidget(label)
        spacerItem_8 = QSpacerItem(20, 40, QSizePolicy.Minimum,
                                   QSizePolicy.Expanding)
        verticalLayout_32.addItem(spacerItem_8)
        horizontalLayout_32.addLayout(verticalLayout_32)
        self.textEdit_snapshot_description = QTextEdit(
            self.tab_snapshot_metadata)
        self.textEdit_snapshot_description.setReadOnly(True)
        horizontalLayout_32.addWidget(self.textEdit_snapshot_description)
        verticalLayout_31.addLayout(horizontalLayout_32)
        self.tabWidget_metadata.addTab(self.tab_snapshot_metadata,
                                       'Snapshot Metadata')

        top_gridLayout.addWidget(self.splitter, 0, 0, 1, 1)
        self.setWidget(dockWidgetContents)

    #----------------------------------------------------------------------
    def loadViewSizeSettings(self):

        self._settings.beginGroup('viewSize')

        self._position = self._settings.value('position')
        if self._position is None:
            sizeHint = self.sizeHint()
            self._position = QRect(0, 0, sizeHint.width(), sizeHint.height())
        self.setGeometry(self._position)

        self._splitter_sizes = self._settings.value('splitter_sizes')
        if self._splitter_sizes is None:
            third_height = int(self.height()/3.0)
            self._splitter_sizes = [third_height]*3
        if not isinstance(self._splitter_sizes[0], int):
            self._splitter_sizes = [int(s) for s in self._splitter_sizes]
        self.splitter.setSizes(self._splitter_sizes)

        self._settings.endGroup()

    #----------------------------------------------------------------------
    def saveViewSizeSettings(self):

        self._settings.beginGroup('viewSize')

        self._position = self.geometry()
        self._settings.setValue('position', self._position)

        self._splitter_sizes = self.splitter.sizes()
        self._settings.setValue('splitter_sizes', self._splitter_sizes)

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

        print('Updating window title')

    #----------------------------------------------------------------------
    def updateMetaDataTab(self):
        """"""

        ## Update config tab
        if self.config_abstract.config_id is not None:
            config_id_text = str(self.config_abstract.config_id)
        else:
            config_id_text = 'Not saved yet'
        self.lineEdit_config_id.setText(config_id_text)
        self.resizeLineEditToContents(self.lineEdit_config_id)
        #
        self.lineEdit_config_name.setText(self.config_abstract.name)
        self.resizeLineEditToContents(self.lineEdit_config_name)
        #
        self.lineEdit_config_username.setText(self.config_abstract.userinfo[0])
        self.resizeLineEditToContents(self.lineEdit_config_username)
        #
        if self.config_abstract.config_ctime is not None:
            timestamp_text = datestr(self.config_abstract.config_ctime)
        else:
            timestamp_text = 'Not saved yet'
        self.lineEdit_config_timestamp.setText(timestamp_text)
        self.resizeLineEditToContents(self.lineEdit_config_timestamp)
        #
        self.textEdit_config_description.setText(self.config_abstract.description)

        ## Update snapshot tab
        if self.ss_abstract.ss_id is not None:
            ss_id_text = str(self.ss_abstract.ss_id)
        else:
            ss_id_text = 'Not saved yet'
        self.lineEdit_ss_id.setText(ss_id_text)
        self.resizeLineEditToContents(self.lineEdit_ss_id)
        #
        self.lineEdit_ss_name.setText(self.ss_abstract.name)
        self.resizeLineEditToContents(self.lineEdit_ss_name)
        #
        self.lineEdit_snapshot_username.setText(self.ss_abstract.userinfo[0])
        self.resizeLineEditToContents(self.lineEdit_snapshot_username)
        #
        if self.ss_abstract.ss_ctime is not None:
            timestamp_text = datestr(self.ss_abstract.ss_ctime)
        else:
            timestamp_text = 'Not saved yet'
        self.lineEdit_snapshot_timestamp.setText(timestamp_text)
        self.resizeLineEditToContents(self.lineEdit_snapshot_timestamp)
        #
        self.textEdit_snapshot_description.setText(self.ss_abstract.description)

    #----------------------------------------------------------------------
    def resizeLineEditToContents(self, lineEdit):
        """"""

        text = lineEdit.text()
        fm = lineEdit.fontMetrics()
        width = fm.boundingRect('x'*len(text)).width()
        lineEdit.setMinimumWidth(max([width, 50]))

    #----------------------------------------------------------------------
    def load_column_from_file(self):
        """"""

        last_directory_path = self._main_settings.last_directory_path
        caption = 'Load single-column data from a file'
        selected_filter_str = ('Single-Column Text files (*.txt)')
        filter_str = ';;'.join([selected_filter_str, 'All files (*)'])
        filepath = QFileDialog.getOpenFileName(
            caption=caption, directory=last_directory_path, filter=filter_str)

        if not filepath:
            return
        else:
            self._main_settings.last_directory_path = osp.dirname(filepath)

        selected_col_key = self.ss_abstract.all_col_keys[
            self.ss_abstract.all_col_names.index(
                self.ssDBView.comboBox_column_name.currentText())]

        self.ss_table.load_column_from_file(filepath, selected_col_key)

    #----------------------------------------------------------------------
    def restore_IniSP(self):
        """"""

        title = 'Restore Machine to Initial Setpoints'
        prompt_text = ('Are you sure you want to restore the machine to '
                       'initial setpoints?\n\n'
                       'If so, enter the number of steps into which this '
                       'restoration action should be divided, and hit OK.\n\n'
                       'Number of Steps:')
        default_val = 1
        result = QInputDialog.getInt(self, title, prompt_text, default_val,
                                     min=1, max=100, step=1)

        if result[1]: # If OK was pressed
            n_steps = result[0]
            default_val = 3 # [sec]
            prompt_text = 'Wait Time at Each Step [seconds]:'
            result = QInputDialog.getInt(
                self, title, prompt_text, default_val, min=0, max=3600, step=1)
            if result[1]: # If OK was pressed
                wait_time = float(result[0])
                self.ss_table.restore_IniSP(n_steps, wait_time)
            else: # If Cancel was pressed
                return
        else: # If Cancel was pressed
            return

########################################################################
class TinkerView(QMainWindow, Ui_MainWindow):
    """"""

    #----------------------------------------------------------------------
    def __init__(self, config_id_to_open=None):
        """Constructor"""

        QMainWindow.__init__(self)

        self.setupUi(self)
        self.dockWidget_example.deleteLater()

        self.centralwidget = QWidget(self)
        self.setCentralWidget(self.centralwidget)
        self.centralWidget().hide()

        self.menuWindow.addAction('Tabify', self.tabifyWindows)
        self.menuWindow.addAction('Tile Horizontally',
                                  self.tileWindowsHorizontally)
        self.menuWindow.addAction('Tile Vertically',
                                  self.tileWindowsVertically)
        self.menuWindow.addSeparator()

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

        self._settings = QSettings('APHLA', 'Tinker')
        self.loadViewSizeSettings()
        if not config_id_to_open:
            self.loadMiscSettings(load_last_open_configs=True)
        else:
            self.loadConfigFromConfigIDs([config_id_to_open])
            self.loadMiscSettings(load_last_open_configs=False)

        self.connect(self.actionLoadConfig, SIGNAL('triggered()'),
                     self.launchConfigDBSelector)
        self.connect(self.actionLoadSnapshot, SIGNAL('triggered()'),
                     self.launchSnapshotDBSelector)
        self.connect(self.actionSaveConfig, SIGNAL('triggered()'),
                     self.saveConfig)
        self.connect(self.actionSaveSnapshot, SIGNAL('triggered()'),
                     self.saveSnapshot)
        self.connect(self.actionPreferences, SIGNAL('triggered()'),
                     self.launchPrefEditor)

    #----------------------------------------------------------------------
    def closeEvent(self, event):
        """"""

        self.saveViewSizeSettings()
        self.saveMiscSettings()

        event.accept()

    #----------------------------------------------------------------------
    def loadViewSizeSettings(self):
        """"""

        self._settings.beginGroup('viewSize')

        self._position = self._settings.value('position')
        if self._position is None:
            sizeHint = self.sizeHint()
            self._position = QRect(0, 0, sizeHint.width(), sizeHint.height())
        self.setGeometry(self._position)

        self._settings.endGroup()

    #----------------------------------------------------------------------
    def saveViewSizeSettings(self):
        """"""

        self._settings.beginGroup('viewSize')

        self._position = self.geometry()
        self._settings.setValue('position', self._position)

        self._settings.endGroup()

    #----------------------------------------------------------------------
    def loadMiscSettings(self, load_last_open_configs=True):
        """"""

        if load_last_open_configs:
            self._settings.beginGroup('misc')

            open_config_ids = self._settings.value('open_config_ids')
            if open_config_ids is not None:
                open_config_ids = [int(s) if s is not None else None
                                   for s in open_config_ids]
                self.loadConfigFromConfigIDs(open_config_ids)

            self._settings.endGroup()

        self._settings.beginGroup('fileSystem')

        self._settings.last_directory_path = \
            self._settings.value('last_directory_path')
        if self._settings.last_directory_path is None:
            self._settings.last_directory_path = ''

        self._settings.endGroup()

    #----------------------------------------------------------------------
    def saveMiscSettings(self):
        """"""

        self._settings.beginGroup('misc')

        open_config_ids = []
        w = None
        for w in self.dockWidgetList:
            open_config_ids.append(w.config_abstract.config_id)
        self._settings.setValue('open_config_ids', open_config_ids)

        # Save settings of the last dock widget, if exists
        if w is not None:
            w.saveViewSizeSettings()
            w.saveMiscSettings()

        self._settings.endGroup()

        self._settings.beginGroup('fileSystem')

        self._settings.setValue('last_directory_path',
                                self._settings.last_directory_path)

        self._settings.endGroup()

    #----------------------------------------------------------------------
    def tabifyWindows(self):
        """"""

        for i, w in enumerate(self.dockWidgetList):
            w.setFloating(False) # Dock the new dockwidget
            if i >= 1:
                self.tabifyDockWidget(self.dockWidgetList[i-1], w)

    #----------------------------------------------------------------------
    def tileWindowsHorizontally(self):
        """"""

        for i, w in enumerate(self.dockWidgetList):
            if np.mod(i,2) == 0:
                self.addDockWidget(Qt.LeftDockWidgetArea, w)
            else:
                self.addDockWidget(Qt.RightDockWidgetArea, w)

    #----------------------------------------------------------------------
    def tileWindowsVertically(self):
        """"""

        for i, w in enumerate(self.dockWidgetList):
            if np.mod(i,2) == 0:
                self.addDockWidget(Qt.TopDockWidgetArea, w)
            else:
                self.addDockWidget(Qt.BottomDockWidgetArea, w)

    #----------------------------------------------------------------------
    def saveSnapshot(self):
        """"""

        visible_dockWidget_list = [w for w in self.dockWidgetList if w.visible]

        if visible_dockWidget_list == []:
            msg = QMessageBox()
            msg.setText('No configuration is loaded.')
            msg.setIcon(QMessageBox.Critical)
            msg.exec_()
            return

        if len(visible_dockWidget_list) >= 2:
            visible_dockWidget_titles = [w.windowTitle()
                                         for w in visible_dockWidget_list]

            title = 'Select configuration for which a snapshot is to be saved'
            prompt = 'Configuration Window Title:'
            result = QInputDialog.getItem(
                self, title, prompt, visible_dockWidget_titles, editable=False)

            if not result[1]:
                return

            config_title = result[0]

            w = visible_dockWidget_list[
                visible_dockWidget_titles.index(config_title)]
        else:
            w = visible_dockWidget_list[0]
            config_title = w.windowTitle()

        if w.config_abstract.config_id is None:
            msg = QMessageBox()
            msg.setText('The selected configuration has not been saved to '
                        'the database yet. Do you want to save the '
                        'configuration now?')
            msg.setInformativeText(
                'Before you can save a snapshot for a configuration, '
                'the configuration must be saved to the database.')
            msg.addButton(QMessageBox.Yes)
            msg.addButton(QMessageBox.No)
            msg.setDefaultButton(QMessageBox.No)
            msg.setEscapeButton(QMessageBox.No)
            msg.setIcon(QMessageBox.Question)
            choice = msg.exec_()
            if choice == QMessageBox.No:
                return

            w = self.saveConfig(w)

            if w is None:
                return

        dialog = SnapshotSaveDialog()
        dialog.exec_()

        if dialog.result() == QDialog.Accepted:

            _sa = w.ss_abstract
            _ca = _sa._config_abstract

            _sa.name = dialog.lineEdit_name.text().strip()
            _sa.description = dialog.plainTextEdit_description.property(
                'plainText')
            try:
                _sa.masar_id = int(dialog.lineEdit_masar_id.text())
            except:
                _sa.masar_id = None
            # The following are already up to date:
            #    _sa.config_id, _sa.ref_step_size, _sa.synced_group_weight,
            #    _sa.caget_sent_ts_second

            _sa.userinfo = getuserinfo()
            _sa.db.saveSnapshot(_sa)
            msg = QMessageBox()
            msg.setText('Snapshot successfully saved to database.')
            msg.exec_()

            # Update snapshot-related columns
            from_DB = False
            w.ss_table.update_snapshot_columns(from_DB)

            # Update snapshot tab on the dock widget
            w.lineEdit_ss_id.setText('{0:d}'.format(_sa.ss_id))
            w.lineEdit_ss_name.setText(_sa.name)
            w.textEdit_snapshot_description.setProperty('plainText',
                                                        _sa.description)
            w.lineEdit_snapshot_username.setText(_sa.userinfo[0])
            w.lineEdit_snapshot_timestamp.setText(datestr(_sa.ss_ctime))

    #----------------------------------------------------------------------
    def saveConfig(self, selected_dock_widget=None):
        """"""

        if selected_dock_widget is None:
            visible_dockWidget_list = [w for w in self.dockWidgetList if w.visible]

            if visible_dockWidget_list == []:
                msg = QMessageBox()
                msg.setText('No configuration is loaded.')
                msg.setIcon(QMessageBox.Critical)
                msg.exec_()
                return

            if len(visible_dockWidget_list) >= 2:
                visible_dockWidget_titles = [w.windowTitle()
                                             for w in visible_dockWidget_list]

                title = 'Select configuration to save'
                prompt = 'Configuration Window Title:'
                result = QInputDialog.getItem(
                    self, title, prompt, visible_dockWidget_titles, editable=False)

                if not result[1]:
                    return

                config_title = result[0]

                w = visible_dockWidget_list[
                    visible_dockWidget_titles.index(config_title)]
            else:
                w = visible_dockWidget_list[0]
                config_title = w.windowTitle()
        else:
            w = selected_dock_widget
            config_title = w.windowTitle()

        dialog = ConfigSaveDialog(config_title)
        dialog.exec_()

        if dialog.result() == QDialog.Accepted:

            _sa = w.ss_abstract
            _ca = w.ss_abstract._config_abstract

            _ca.name = dialog.lineEdit_name.text().strip()
            _ca.description = dialog.plainTextEdit_description.property(
                'plainText')
            try:
                _ca.masar_id = int(dialog.lineEdit_masar_id.text())
            except:
                _ca.masar_id = None
            _ca.ref_step_size = _sa.ref_step_size
            _ca.synced_group_weight = _sa.synced_group_weight

            _ca.weights            = _sa.weight_array.tolist()
            _ca.caput_enabled_rows = _sa.caput_enabled_rows.tolist()

            _ca.userinfo = getuserinfo()
            _ca.db.saveConfig(_ca)
            msg = QMessageBox()
            msg.setText('Config successfully saved to database.')
            msg.exec_()

            _sa.config_id = _ca.config_id

            # Update config tab on the dock widget
            w.lineEdit_config_id.setText('{0:d}'.format(_ca.config_id))
            w.lineEdit_config_name.setText(_ca.name)
            w.textEdit_config_description.setProperty('plainText',
                                                      _ca.description)
            w.lineEdit_config_username.setText(_ca.userinfo[0])
            w.lineEdit_config_timestamp.setText(datestr(_ca.config_ctime))

            return w

    #----------------------------------------------------------------------
    def launchConfigDBSelector(self):
        """"""

        result = tinkerConfigDBSelector.make(isModal=True, parentWindow=self,
                                             aptinkerQSettings=self._settings)

        config_abstract_model = result.config_model.abstract

        if config_abstract_model.channel_ids != []:
            self.createDockWidget(config_abstract_model)

    #----------------------------------------------------------------------
    def launchSnapshotDBSelector(self):
        """"""

        result = tinkerSnapshotDBSelector.make(isModal=True, parentWindow=self,
                                               aptinkerQSettings=self._settings)

        ss_abstract_model = result.ss_model.abstract
        config_abstract_model = ss_abstract_model._config_abstract

        if config_abstract_model.channel_ids != []:
            self.createDockWidget(config_abstract_model,
                                  ss_abstract=ss_abstract_model)

    #----------------------------------------------------------------------
    def launchPrefEditor(self):
        """"""

        dialog = PreferencesEditor()
        dialog.exec_()

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
    def createDockWidget(self, config_abstract_model, ss_abstract=None):
        """"""

        isinstance(config_abstract_model, ConfigAbstractModel)

        dockWidget = TinkerDockWidget(config_abstract_model, self,
                                      ss_abstract=ss_abstract)
        self.addDockWidget(Qt.DockWidgetArea(1), dockWidget)

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
        dockWidget.setVisible(True) # Need this line before raise_(). Otherwise,
        # raise_() will not bring the dockwidget to the front.
        dockWidget.raise_()

        dockWidget.stackedWidget.setCurrentWidget(dockWidget.page_table)
        #dockWidget.stackedWidget.setCurrentWidget(dockWidget.page_tree)

        dockWidget.updateMetaDataTab()

        self.menuWindow.addAction(dockWidget.toggleViewAction())

        self.connect(dockWidget, SIGNAL('dockAboutTobeClosed'),
                     self.onDockWidgetClose)

        return dockWidget

    #----------------------------------------------------------------------
    def onDockWidgetClose(self, close_signal_sender):
        """"""

        # If the "close" signal was sent from toggleViewAction(), then
        # the dockWidget should be simply hidden, not removed.
        #
        # On the other hand, if the "close" signal was sent from QToolButton,
        # then the user wanted to actually close the dockWidget. So, it must
        # be removed.
        if isinstance(close_signal_sender, QToolButton):
            dockWidget = self.sender()
            self.dockWidgetList.remove(dockWidget)
            self.menuWindow.removeAction(dockWidget.toggleViewAction())

            # Shut down the timer to avoid memory leak
            if dockWidget.auto_updater is not None:
                dockWidget.auto_updater.cancel()

    #----------------------------------------------------------------------
    def loadConfigFromConfigIDs(self, config_ids):
        """"""

        db = TinkerMainDatabase()

        if '[config_meta_table text view]' \
           not in db.getViewNames(square_brackets=True):
            db.create_temp_config_meta_table_text_view()

        if isinstance(config_ids, int):
            config_ids = [config_ids]

        newly_created_dockwidgets = []
        for config_id in config_ids:
            if config_id is None:
                continue

            print('Loading Configuration (ID={0:d})...'.format(config_id))
            m = ConfigAbstractModel()

            m.config_id = config_id

            out = db.getColumnDataFromTable(
                '[config_meta_table text view]',
                column_name_list=[
                    'config_name', 'config_description', 'config_masar_id',
                    'config_ref_step_size', 'config_synced_group_weight',
                    'config_ctime'],
                condition_str='config_id={0:d}'.format(config_id))

            if out == []:
                print('config_id of {0:d} could not be found.'.format(
                    config_id))
                continue

            ((m.name,), (m.description,), (m.masar_id,), (m.ref_step_size,),
             (synced_group_weight,), (m.config_ctime,)) = out

            if synced_group_weight: m.synced_group_weight = True
            else                  : m.synced_group_weight = False

            out = db.getColumnDataFromTable(
                'config_table',
                column_name_list=['group_name_id', 'channel_id',
                                  'config_weight', 'config_caput_enabled'],
                condition_str='config_id={0:d}'.format(config_id))
            (m.group_name_ids, m.channel_ids, m.weights,
             m.caput_enabled_rows) = map(list, out)

            if m.channel_ids != []:
                if m.check_aphla_unitconv_updates():
                    newly_created_dockwidgets.append(self.createDockWidget(m))
                else:
                    print('Aborting configuration loading.')

            print('Configuration loading process finished.')

        db.close(vacuum=False)

        return newly_created_dockwidgets

########################################################################
class TinkerApp(QObject):
    """"""

    #----------------------------------------------------------------------
    def __init__(self, use_cached_lattice=False, config_id_to_open=None):
        """Constructor"""

        QObject.__init__(self)

        self.use_cached_lattice = use_cached_lattice

        self._initView(config_id_to_open=config_id_to_open)

        self.connect(self.view.actionNewConfig, SIGNAL('triggered(bool)'),
                     self.openNewConfigSetupDialog)

    #----------------------------------------------------------------------
    def _initView(self, config_id_to_open=None):
        """"""

        self.view = TinkerView(config_id_to_open=config_id_to_open)

    #----------------------------------------------------------------------
    def openNewConfigSetupDialog(self, _):
        """"""

        result = tinkerConfigSetupDialog.make(
            isModal=True, parentWindow=self.view,
            use_cached_lattice=self.use_cached_lattice,
            aptinkerQSettings=self.view._settings)

        config_abstract_model = result.model.abstract

        if config_abstract_model.channel_ids != []:
            self.view.createDockWidget(config_abstract_model)

########################################################################
class DBusInterface(QDBusAbstractInterface):
    """"""

    #----------------------------------------------------------------------
    def __init__(self, service, path, connection, parent=None):
        """Constructor"""

        super(DBusInterface, self).__init__(
            service, path, 'org.aphla.aptinker.Interface',
            connection, parent)

    #----------------------------------------------------------------------
    def loadConfigFromConfigID(self, config_id):
        """"""

        self.asyncCall('loadConfigFromConfigID', config_id)

########################################################################
class DBusInterfaceAdaptor(QDBusAbstractAdaptor):
    """"""

    Q_CLASSINFO('D-Bus Interface', 'org.aphla.aptinker.Interface')
    Q_CLASSINFO('D-Bus Introspection', ''
            ' <interface name="org.aphla.aptinker.Interface">\n'
            ' <method name="loadConfigFromConfigID"/>\n'
            ' </interface>\n'
            '')

    #----------------------------------------------------------------------
    def __init__(self, parent):
        """Constructor"""

        super(DBusInterfaceAdaptor, self).__init__(parent)

        self.setAutoRelaySignals(True)

    #----------------------------------------------------------------------
    @pyqtSlot(int)
    def loadConfigFromConfigID(self, config_id):
        """"""

        self.parent().loadConfigFromConfigIDs([config_id])

#----------------------------------------------------------------------
def make(use_cached_lattice=False, config_id_to_open=None):
    """"""

    app = TinkerApp(use_cached_lattice=use_cached_lattice,
                    config_id_to_open=config_id_to_open)
    app.view.show()

    return app

#----------------------------------------------------------------------
def main():
    """"""

    # If Qt is to be used (for any GUI) then the cothread library needs to
    # be informed, before any work is done with Qt. Without this line
    # below, the GUI window will not show up and freeze the program.
    qapp = cothread.iqt()

    parser = argparse.ArgumentParser(
        description='APTINKER (Pre-Tune)', add_help=True)
    parser.add_argument('--use-cache', '-u', action='store_true',
                        help=('Use cached APHLA machine information for '
                              'faster loading'))
    parser.add_argument('--config-id', '--conf-id', '-c', type=int,
                        help=('APTINKER configuration ID to load'))
    args = parser.parse_args()

    if args.config_id is not None:
        pids = get_running_aptinker_pids()
        if pids is not None:
            interface = DBusInterface(
                'org.aphla.aptinker', '/TinkerView',
                QDBusConnection.sessionBus(), parent=None)
            interface.loadConfigFromConfigID(args.config_id)
            return

    if ap.machines._lat is None:
        try:
            print('Trying to load machine "{0}"...'.format(config.HLA_MACHINE))
            ap.machines.load(config.HLA_MACHINE, use_cache=args.use_cache)
            success = True
            print('Successfully loaded {0}'.format(config.HLA_MACHINE))
        except:
            print('Failed to load {0}'.format(config.HLA_MACHINE))
            success = False

        if not success:
            for machine_name in ap.machines.machines():
                if machine_name != config.HLA_MACHINE:
                    try:
                        print('Trying to load machine "{0}"...'.format(
                            machine_name))
                        ap.machines.load(machine_name,
                                         use_cache=args.use_cache)
                        print('Successfully loaded {0}'.format(machine_name))
                        break
                    except:
                        print('Failed to load {0}'.format(machine_name))

    pref = get_preferences()
    font = QFont()
    font.setPointSize(pref['font_size'])
    qapp.setFont(font)

    app = make(use_cached_lattice=args.use_cache,
               config_id_to_open=args.config_id)

    adaptor = DBusInterfaceAdaptor(app.view)
    connection = QDBusConnection.sessionBus()
    connection.registerObject('/TinkerView', app.view)
    connection.registerService('org.aphla.aptinker')

    cothread.WaitForQuit()

#----------------------------------------------------------------------
if __name__ == "__main__" :
    main()
