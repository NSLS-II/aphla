#! /usr/bin/env python

import sip
sip.setapi('QString', 2)
sip.setapi('QVariant', 2)

import sys, os
import h5py
import json
import time

from PyQt4.QtCore import (Qt, SIGNAL, QObject, QSettings, QSize)
from PyQt4.QtGui import (
    QApplication, QDialog, QSortFilterProxyModel, QAbstractItemView, QAction,
    QIcon, QFileDialog, QMessageBox, QInputDialog, QMenu, QTextEdit, QFont
)

import cothread

import aphla as ap

import config
from tinkerModels import (ConfigAbstractModel, ConfigTableModel,
                          ConfigTreeModel)
from tinkerdb import (TinkerMainDatabase, unitsys_id_raw, pv_id_NonSpecified)
from ui_tinkerConfigSetupDialog import Ui_Dialog
from aphla.gui import channelexplorer
from aphla.gui.utils.tictoc import tic, toc

FILE_FILTER_DICT = {'Text File': 'Text files (*.txt)',
                    'HDF5 File': 'HDF5 files (*.h5 *.hdf5)',
                    'JSON File': 'JSON files (*.json)',
                    }

########################################################################
class SmartSizedMessageBox(QMessageBox):
    """
    Taken from the answer by Paul Etherton at

    http://stackoverflow.com/questions/2655354/how-to-allow-resizing-of-qmessagebox-in-pyqt4
    """

    #----------------------------------------------------------------------
    def __init__(self, *args, **kwargs):
        """Constructor"""

        super(SmartSizedMessageBox, self).__init__(*args, **kwargs)

    #----------------------------------------------------------------------
    def resizeEvent(self, event):
        """
        We only need to extend resizeEvent, not every event.
        """

        result = super(SmartSizedMessageBox, self).resizeEvent(event)

        f = QFont('Monospace')
        f.setPointSize(14)
        f.setStyleHint(QFont.TypeWriter)

        details_box = self.findChild(QTextEdit)
        details_box.setFont(f)
        fm = details_box.fontMetrics()
        text = details_box.property('plainText')
        lines = text.split('\n')
        rect = fm.boundingRect(lines[0])
        width  = int(rect.width()*1.5)
        height = int(rect.height()*len(lines)*1.5)
        if details_box is not None:
            details_box.setFixedSize(QSize(width, height))

        return result

########################################################################
class Settings():
    """"""

    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""

        self._settings = QSettings('APHLA', 'TinkerConfigSetupDialog')

        self.loadViewSizeSettings()
        self.loadMiscSettings()

    #----------------------------------------------------------------------
    def loadViewSizeSettings(self):
        """"""

        self._settings.beginGroup('viewSize')

        self._position = self._settings.value('position')

        self._splitter_left_right_sizes = \
            self._settings.value('splitter_left_right_sizes')
        if self._splitter_left_right_sizes is not None:
            self._splitter_left_right_sizes = [
                int(s) for s in  self._splitter_left_right_sizes]

        self._splitter_top_bottom_sizes = \
            self._settings.value('splitter_top_bottom_sizes')
        if self._splitter_top_bottom_sizes is not None:
            self._splitter_top_bottom_sizes = [
                int(s) for s in self._splitter_top_bottom_sizes]

        self._settings.endGroup()

    #----------------------------------------------------------------------
    def loadMiscSettings(self):
        """"""

        self._settings.beginGroup('misc')

        self.visible_col_key_list = self._settings.value('visible_col_key_list')
        if self.visible_col_key_list is None:
            self.visible_col_key_list = \
                config.DEF_VIS_COL_KEYS['config_setup'][:]

        self.last_directory_path = self._settings.value('last_directory_path')
        if self.last_directory_path is None:
            self.last_directory_path = os.getcwd()

        self._settings.endGroup()

    #----------------------------------------------------------------------
    def saveViewSizeSettings(self):
        """"""

        self._settings.beginGroup('viewSize')

        self._settings.setValue('position', self._position)
        self._settings.setValue('splitter_left_right_sizes',
                                self._splitter_left_right_sizes)
        self._settings.setValue('splitter_top_bottom_sizes',
                                self._splitter_top_bottom_sizes)

        self._settings.endGroup()

    #----------------------------------------------------------------------
    def saveMiscSettings(self):
        """"""

        self._settings.beginGroup('misc')

        self._settings.setValue('visible_col_key_list',
                                self.visible_col_key_list)
        self._settings.setValue('last_directory_path',
                                self.last_directory_path)

        self._settings.endGroup()

########################################################################
class Model(QObject):
    """"""

    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""

        QObject.__init__(self)

        self.abstract = ConfigAbstractModel()
        self.table    = ConfigTableModel(abstract_model=self.abstract)
        #self.tree     = ConfigTreeModel()

        self.db = self.abstract.db

        self.output = None

    #----------------------------------------------------------------------
    def importNewChannelsFromSelector(self, selection_dict, channel_group_info):
        """"""

        machine               = selection_dict['machine']
        lattice               = selection_dict['lattice']
        elem_obj_field_tuples = selection_dict['selection']

        machine_name_id = self.db.getMatchingPrimaryKeyIdFrom2ColTable(
            'machine_name_table', 'machine_name_id', 'machine_name', machine,
            append_new=True)
        lattice_name_id = self.db.getMatchingPrimaryKeyIdFrom2ColTable(
            'lattice_name_table', 'lattice_name_id', 'lattice_name', lattice,
            append_new=True)

        unitsys_id = unitsys_id_raw # no unit conversion by default
        NoConversion_unitconv_id = self.db.getColumnDataFromTable(
                    'unitconv_table', column_name_list=['unitconv_id'],
                    condition_str='conv_data_txt=""')[0][0]

        channel_ids   = []
        channel_names = []
        pvsp_ids      = []
        for elem, field in elem_obj_field_tuples:
            elem_prop_id = self.db.get_elem_prop_id(
                machine_name_id, lattice_name_id, elem, append_new=True)
            field_id = self.db.getMatchingPrimaryKeyIdFrom2ColTable(
                'field_table', 'field_id', 'field', field, append_new=True)
            aphla_ch_id = self.db.get_aphla_ch_id(elem_prop_id, field_id,
                                                  append_new=True)
            pvsp = elem._field[field].pvsp
            if pvsp != []:
                pvsp     = pvsp[0]
                readonly = 0
            else:
                pvsp     = ''
                readonly = -1
            pvsp_id = self.db.get_pv_id(pvsp, readonly, append_new=True)
            if pvsp_id is None:
                msg = QMessageBox()
                msg.setText('ID for the following PV could not be found:')
                msg.setInformativeText('"{0:s}"'.format(pvsp))
                msg.exec_()
                return
            elif pvsp_id == -1:
                msg = QMessageBox()
                msg.setText('The following PV could not be connected:')
                msg.setInformativeText('"{0:s}"'.format(pvsp))
                msg.exec_()
                return
            elif pvsp_id == -2:
                return # Error message box is launched in get_pv_id()

            pvrb = elem._field[field].pvrb
            if pvrb != []:
                pvrb     = pvrb[0]
                readonly = 1
            else:
                pvrb     = ''
                readonly = -1
            pvrb_id = self.db.get_pv_id(pvrb, readonly, append_new=True)
            if pvrb_id is None:
                msg = QMessageBox()
                msg.setText('ID for the following PV could not be found:')
                msg.setInformativeText('"{0:s}"'.format(pvrb))
                msg.exec_()
                return
            elif pvrb_id == -1:
                msg = QMessageBox()
                msg.setText('The following PV could not be connected:')
                msg.setInformativeText('"{0:s}"'.format(pvrb))
                msg.exec_()
                return
            elif pvrb_id == -2:
                return # Error message box is launched in get_pv_id()

            channel_name = '{0:s}.{1:s}.{2:s}'.format(lattice, elem.name, field)
            channel_names.append(channel_name)
            channel_name_id = self.db.getMatchingPrimaryKeyIdFrom2ColTable(
                'channel_name_table', 'channel_name_id', 'channel_name',
                channel_name, append_new=True)
            channel_id = self.db.get_channel_id(
                pvsp_id, pvrb_id, unitsys_id, channel_name_id,
                NoConversion_unitconv_id, NoConversion_unitconv_id,
                aphla_ch_id=aphla_ch_id, append_new=True)
            if channel_id is None:
                msg = QMessageBox()
                msg.setText(('The channel could neither be found or created '
                             'for the following PVs:'))
                msg.setInformativeText(
                    'Setpoint PV: "{0:s}"\nReadback PV: "{1:s}"'.format(
                        pvsp, pvrb))
                msg.exec_()
                return
            channel_ids.append(channel_id)
            pvsp_ids.append(pvsp_id)

        n_channels = len(channel_ids)
        if channel_group_info == {}:
            group_name_list = channel_names
            group_name_ids = [
                self.db.getMatchingPrimaryKeyIdFrom2ColTable(
                    'group_name_table', 'group_name_id', 'group_name',
                    group_name, append_new=True)
                for group_name in group_name_list]
            weights = [float('nan')]*n_channels
        else:
            group_name = channel_group_info['name']
            if group_name == '':
                group_name_list = channel_names
                group_name_ids = [
                    self.db.getMatchingPrimaryKeyIdFrom2ColTable(
                        'group_name_table', 'group_name_id', 'group_name',
                        group_name, append_new=True)
                    for group_name in group_name_list]
            else:
                group_name_id = self.db.getMatchingPrimaryKeyIdFrom2ColTable(
                    'group_name_table', 'group_name_id', 'group_name',
                    group_name, append_new=True)
                group_name_ids = [group_name_id]*n_channels

            weights = [channel_group_info['weight']]*n_channels

        self.abstract.group_name_ids.extend(group_name_ids)
        self.abstract.channel_ids.extend(channel_ids)
        self.abstract.weights.extend(weights)

        self.table.updateModel()
        self.table.repaint()

########################################################################
class View(QDialog, Ui_Dialog):
    """"""

    #----------------------------------------------------------------------
    def __init__(self, model, isModal, parentWindow, settings=None):
        """Constructor"""

        QDialog.__init__(self, parent=parentWindow)

        self.setupUi(self)

        self.msg = None

        self.setWindowFlags(Qt.Window) # To add Maximize & Minimize buttons
        self.setModal(isModal)

        self.settings = settings

        self.comboBox_view.setEditable(False)
        self.group_based_view_index = \
            self.comboBox_view.findText('Group-based View')
        self.channel_based_view_index = \
            self.comboBox_view.findText('Channel-based View')
        self.comboBox_view.setCurrentIndex(self.channel_based_view_index)
        self.on_view_base_change(self.channel_based_view_index)

        self.model = model

        self.lineEdit_ref_step_size.setText(
            str(self.model.abstract.ref_step_size))

        self.table_proxyModel = QSortFilterProxyModel()
        self.table_proxyModel.setSourceModel(self.model.table)
        self.table_proxyModel.setDynamicSortFilter(False)
        #
        #self.tree_proxyModel = QSortFilterProxyModel()
        #self.tree_proxyModel.setSourceModel(self.model.tree)
        #self.tree_proxyModel.setDynamicSortFilter(False)

        t = self.tableView
        t.setModel(self.table_proxyModel)
        t.setCornerButtonEnabled(True)
        t.setShowGrid(True)
        t.setSelectionMode(QAbstractItemView.ExtendedSelection)
        t.setSelectionBehavior(QAbstractItemView.SelectItems)
        t.setAlternatingRowColors(True)
        t.setSortingEnabled(False)
        horizHeader = t.horizontalHeader()
        horizHeader.setSortIndicatorShown(False)
        horizHeader.setStretchLastSection(False)
        horizHeader.setMovable(False)
        #
        #t = self.treeView
        #t.setModel(self.tree_proxyModel)
        #t.setItemsExpandable(True)
        #t.setRootIsDecorated(True)
        #t.setAllColumnsShowFocus(False)
        #t.setHeaderHidden(False)
        #t.setSortingEnabled(False)
        #horizHeader = t.header()
        #horizHeader.setSortIndicatorShown(False)
        #horizHeader.setStretchLastSection(False)
        #horizHeader.setMovable(False)
        #self._expandAll_and_resizeColumn()
        #t.setSelectionMode(QAbstractItemView.ExtendedSelection)

        self.actionGroupChannels = QAction(QIcon(), 'Group channels',
                                           self.treeView)
        self.actionUngroupChannels = QAction(QIcon(), 'Ungroup channels',
                                             self.treeView)
        self.popMenu = QMenu(self.treeView)
        self.popMenu.addAction(self.actionUngroupChannels)
        self.popMenu.addAction(self.actionGroupChannels)

        self.connect(self.treeView,
                     SIGNAL('customContextMenuRequested(const QPoint &)'),
                     self._openContextMenu)
        self.connect(self.actionGroupChannels, SIGNAL('triggered()'),
                     self._groupChannels)
        self.connect(self.actionUngroupChannels, SIGNAL('triggered()'),
                     self._ungroupChannels)

    #----------------------------------------------------------------------
    def closeEvent(self, event):
        """"""

        self.model.abstract.channel_ids = []

        event.accept()

    #----------------------------------------------------------------------
    def accept(self):
        """"""

        if not self.model.abstract.isDataValid():
            return

        super(View, self).accept() # will close the dialog

    #----------------------------------------------------------------------
    def reject(self):
        """"""

        self.model.abstract.channel_ids = []

        super(View, self).reject() # will close the dialog

    #----------------------------------------------------------------------
    def on_view_base_change(self, current_comboBox_index):
        """"""

        if current_comboBox_index == self.group_based_view_index:
            page_obj = self.page_tree
        elif current_comboBox_index == self.channel_based_view_index:
            page_obj = self.page_table
        else:
            raise ValueError('Unexpected current ComboBox index: {0:d}'.
                             format(current_comboBox_index))

        self.stackedWidget.setCurrentWidget(page_obj)

    #----------------------------------------------------------------------
    def _expandAll_and_resizeColumn(self):
        """"""

        self.treeView.expandAll()
        self.treeView.resizeColumnToContents(0)

    #----------------------------------------------------------------------
    def _groupChannels(self):
        """"""

        print 'Not implemented yet'

    #----------------------------------------------------------------------
    def _ungroupChannels(self):
        """"""

        print 'Not implemented yet'

    #----------------------------------------------------------------------
    def _openContextMenu(self, point):
        """"""

        self.popMenu.exec_(self.treeView.mapToGlobal(point))


########################################################################
class App(QObject):
    """"""

    #----------------------------------------------------------------------
    def __init__(self, isModal, parentWindow, use_cached_lattice=False):
        """Constructor"""

        QObject.__init__(self)

        self.use_cached_lattice = use_cached_lattice

        self.settings = Settings()

        self._initModel()
        self._initView(isModal, parentWindow)

        self.connect(self.view.pushButton_import, SIGNAL('clicked()'),
                     self._importConfigData)
        self.connect(self.view.pushButton_export,
                     SIGNAL('clicked()'), self._exportConfigData)

        self.connect(self.view.comboBox_view,
                     SIGNAL('currentIndexChanged(int)'),
                     self.view.on_view_base_change)

    #----------------------------------------------------------------------
    def _initModel(self):
        """"""

        self.model = Model()

    #----------------------------------------------------------------------
    def _initView(self, isModal, parentWindow):
        """"""

        self.view = View(self.model, isModal, parentWindow,
                         settings=self.settings)

    #----------------------------------------------------------------------
    def _importConfigData(self):
        """"""

        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)

        import_type = self.view.comboBox_import.currentText()

        if import_type == 'Channel Explorer':
            self._launchChannelExplorer()
        elif import_type == 'Database':
            a = self.model.abstract

            a.db.getColumnDataFromTable()

            a.name = self.view.lineEdit_config_name.text()
            a.description = self.view.textEdit.toPlainText()
            ref_step_size_str = self.view.lineEdit_ref_step_size.text()
            try:
                a.ref_step_size = float(ref_step_size_str)
            except:
                msg.setText(
                    ('Invalid float representation string for reference step '
                     'size: {:s}').format(ref_step_size_str))
                msg.setIcon(QMessageBox.Critical)
            masar_id_str = self.view.lineEdit_masar_id.text()
            try:
                a.masar_id = int(masar_id_str)
            except:
                a.masar_id = None
            a.synced_group_weight = \
                self.view.checkBox_synced_group_weight.isChecked()

        else:
            msg.setText('This export_type is not implemented yet: {:s}'.
                        format(export_type))
            msg.setIcon(QMessageBox.Critical)
            msg.exec_()
            return

            #all_files_filter_str = 'All files (*)'
            #caption = 'Load Tuner Configuration from {0:s}'.format(import_type)
            #filter_str = ';;'.join([FILE_FILTER_DICT[import_type],
                                    #all_files_filter_str])
            #filepath = QFileDialog.getOpenFileName(
                #caption=caption, directory=self.settings.last_directory_path,
                #filter=filter_str)

            #if not filepath:
                #return

            #self.settings.last_directory_path = os.path.dirname(filepath)

            #if import_type == 'Text File':

                #m = TunerTextFileManager(load=True, filepath=filepath)
                #m.exec_()
                #if m.selection is not None:
                    #data = m.loadConfigTextFile()
                #else:
                    #return

                #if data is not None:
                    #self.model.importNewChannelsFromTextFile(data)
                #else:
                    #return

            #elif import_type == 'HDF5 File':
                #raise NotImplementedError(import_type)

            #elif import_type == 'JSON File':
                #with open(filepath, 'r') as f:
                    #data = json.load(f)

                #if data is not None:
                    #self.model.importNewChannelsFromJSONFile(data)
                #else:
                    #return

    #----------------------------------------------------------------------
    def _exportConfigData(self):
        """"""

        if not self.model.abstract.isDataValid():
            return

        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)

        a = self.model.abstract

        a.name = self.view.lineEdit_config_name.text()
        a.description = self.view.textEdit.toPlainText()
        ref_step_size_str = self.view.lineEdit_ref_step_size.text()
        try:
            a.ref_step_size = float(ref_step_size_str)
        except:
            msg.setText(
                ('Invalid float representation string for reference step '
                 'size: {:s}').format(ref_step_size_str))
            msg.setIcon(QMessageBox.Critical)
        masar_id_str = self.view.lineEdit_masar_id.text()
        try:
            a.masar_id = int(masar_id_str)
        except:
            a.masar_id = None
        a.synced_group_weight = \
            self.view.checkBox_synced_group_weight.isChecked()

        export_type = self.view.comboBox_export.currentText()

        if export_type == 'Database':
            a.config_id = a.db.saveConfig(a)
            msg.setText('Config successfully saved to database.')
        else:
            msg.setText('This export_type is not implemented yet: {:s}'.
                        format(export_type))

            #all_files_filter_str = 'All files (*)'
            #caption = 'Save Tuner Configuration to {0:s}'.format(export_type)
            #filter_str = ';;'.join([FILE_FILTER_DICT[export_type],
                                    #all_files_filter_str])
            #save_filepath = QFileDialog.getSaveFileName(
                #caption=caption, directory=self.starting_directory_path,
                #filter=filter_str)
            #if not save_filepath:
                #return

            #self.starting_directory_path = os.path.dirname(save_filepath)

            #if export_type == 'Text File':
                #m = TunerTextFileManager(load=False, filepath=save_filepath)
                #m.exec_()

                #data = self.model.getConfigDataForTextFile(m.selection)

                #m.saveConfigTextFile(data)
            #elif export_type == 'JSON File':
                #self.model.saveConfigToJSON(save_filepath)
            #elif export_type == 'HDF5 File':
                #self.model.saveConfigToHDF5(save_filepath)

            #msgBox.setText('Config successfully saved to {0:s}: {1:s}.'.
                           #format(export_type, save_filepath))

        msg.exec_()

    #----------------------------------------------------------------------
    def _launchChannelExplorer(self):
        """"""

        result = channelexplorer.make(
            modal=True, init_object_type='channel',
            can_modify_object_type=False,
            output_type=channelexplorer.TYPE_OBJECT,
            caller='aptinker', use_cached_lattice=self.use_cached_lattice,
            debug=False)

        selected_channels = result['dialog_result']

        if selected_channels != {}:
            selected_channels, channelGroupInfo = \
                self._askChannelGroupNameAndWeight(selected_channels)
            self.model.importNewChannelsFromSelector(selected_channels,
                                                     channelGroupInfo)

    #----------------------------------------------------------------------
    def _launchConfigDBSelector(self):
        """"""


    #----------------------------------------------------------------------
    def _askChannelGroupNameAndWeight(self, selected_channels):
        """"""

        prompt_text = ('Do you want to group the selected channels together?\n' +
                       'If so, enter a text for Channel Name and press OK.\n' +
                       'Otherwise, leave it blank and press OK, \n' +
                       'or just press Cancel.\n\n' +
                       'Group Name:')
        result = QInputDialog.getText(self.view, 'Group Name',
                        prompt_text)
        group_name = str(result[0]).strip(' \t\n\r')

        if group_name:
            channelGroupInfo = {'name':group_name}

            prompt_text = ('Specify the weight factor for this group.\n' +
                           'If Cancel is pressed, the weight factor will be set ' +
                           'to 0, by default.\n\n' +
                           'Group Weight Factor:')
            result = QInputDialog.getDouble(self.view, 'Group Weight',
                            prompt_text, value = 0., decimals = 8)

            if result[1]: # If OK was pressed
                channelGroupInfo['weight'] = result[0]
            else: # If Cancel was pressed
                channelGroupInfo['weight'] = 0.

        else:
            channelGroupInfo = {}

        return selected_channels, channelGroupInfo


#----------------------------------------------------------------------
def make(isModal=True, parentWindow=None, use_cached_lattice=False):
    """"""

    app = App(isModal, parentWindow, use_cached_lattice=use_cached_lattice)

    if isModal:
        app.view.exec_()
    else:
        app.view.show()

    if app.model.abstract.config_id is not None:
        app.model.abstract.update_config_ctime()

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
        ap.machines.load(config.HLA_MACHINE, use_cache=use_cached_lattice)

    # If Qt is to be used (for any GUI) then the cothread library needs to
    # be informed, before any work is done with Qt. Without this line
    # below, the GUI window will not show up and freeze the program.
    cothread.iqt()

    app = make(use_cached_lattice=use_cached_lattice)

    cothread.WaitForQuit()
    print app.model.output


if __name__ == '__main__':
    main()