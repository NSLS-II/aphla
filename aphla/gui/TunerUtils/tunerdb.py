#! /usr/bin/env python
import sip
sip.setapi('QString', 2)
sip.setapi('QVariant', 2)

import sys, os
import numpy as np
from time import time, strftime, localtime, sleep
import h5py
import sqlite3
import cPickle as pickle
import traceback
from pprint import pprint
import shutil
import logging
from difflib import ndiff, context_diff

from PyQt4.QtCore import (SIGNAL, Qt)
from PyQt4.QtGui import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                         QCheckBox, QDialogButtonBox, QApplication,
                         QMessageBox)

import aphla as ap
from aphla.gui.utils.hlsqlite import (MEMORY, SQLiteDatabase, Column, 
                                      ForeignKeyConstraint, PrimaryKeyTableConstraint,
                                      UniqueTableConstraint)
from config import (CLIENT_DATA_FOLDERPATH, SERVER_DATA_FOLDERPATH,
                    MAIN_DB_FILENAME, LAST_SYNCED_MAIN_DB_FILENAME,
                    CLIENT_DELTA_DB_FILENAME, SERVER_DELTA_DB_FILENAME,
                    CLIENT_SERVER_DELTA_DB_FILENAME, NEW_MAIN_DB_FILENAME)
from tunerModels import getuserinfo
import aphla.gui.utils.y_serial as y_serial
import aphla.gui.utils.tcpip as tcpip
from aphla.gui.utils.tcpip import BLOCK_SIZE
from aphla.gui.utils.formattext import tab_delimited_formatted_lines

DEBUG = False
H5_COMPRESSION = 'gzip'
H5_VARLENSTR = h5py.new_vlen(str)

#----------------------------------------------------------------------
def quote_string(string, quote='single'):
    """"""
    
    if quote == 'single':
        return "'" + string + "'"
    elif quote == 'double':
        return '"' + string + '"'
    else:
        raise ValueError('Unexpected quote type: '+str(quote))
    
#----------------------------------------------------------------------
def getpvnames(channel_name_list, return_zipped=True):
    """"""
    
    if return_zipped:
        pvrb_pvsp_pair_name_list = []
        for ch_name in channel_name_list:
            elemName, field = ch_name.split('.')
            elem = ap.getElements(elemName)
            if field != '':
                try:
                    pvrb_name = elem.pv(field=field,handle='readback')[0]
                except:
                    pvrb_name = ''
                try:
                    pvsp_name = elem.pv(field=field,handle='setpoint')[0]
                except:
                    pvsp_name = ''
                pvrb_pvsp_pair_name_list.append([pvrb_name, pvsp_name])
            else: # For DIPOLE, there is no field specified
                pvrb_pvsp_pair_name_list.append(elem.pv()[:])
            
        return pvrb_pvsp_pair_name_list
    
    else:
        pvrb_name_list = []
        pvsp_name_list = []

        for ch_name in channel_name_list:
            elemName, field = ch_name.split('.')
            elem = ap.getElements(elemName)[0]
            if field != '':
                try:
                    pvrb_name = elem.pv(field=field,handle='readback')[0]
                except:
                    pvrb_name = ''
                try:
                    pvsp_name = elem.pv(field=field,handle='setpoint')[0]
                except:
                    pvsp_name = ''
                pvrb_name_list.append(pvrb_name)
                pvsp_name_list.append(pvsp_name)
            else: # For DIPOLE, there is no field specified
                pv_list = elem.pv()[:]
                try:
                    pvrb_name_list.append(pv_list[0])
                except:
                    pvrb_name_list.append('')
                try:
                    pvsp_name_list.append(pv_list[1])
                except:
                    pvsp_name_list.append('')

        return pvrb_name_list, pvsp_name_list
        
      
########################################################################
class TunerServer(tcpip.Server):
    """"""

    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        
        logfilepath = os.path.join(CLIENT_DATA_FOLDERPATH,'server.log')
        logging.basicConfig(filename=logfilepath,level=logging.DEBUG,
                            format='%(asctime)s:%(levelname)s:%(message)s')        
        
        tcpip.Server.__init__(self)
        
        # Persistent files
        self.server_main_db_filepath = os.path.join(
            SERVER_DATA_FOLDERPATH, MAIN_DB_FILENAME)
        self.server_delta_db_filepath = os.path.join(
            SERVER_DATA_FOLDERPATH, SERVER_DELTA_DB_FILENAME)
        # Temporary files
        self.client_delta_db_filepath = os.path.join(
            SERVER_DATA_FOLDERPATH, CLIENT_DELTA_DB_FILENAME)
        self.client_server_delta_db_filepath = os.path.join(
            SERVER_DATA_FOLDERPATH, CLIENT_SERVER_DELTA_DB_FILENAME)
        self.new_server_main_db_filepath = os.path.join(
            SERVER_DATA_FOLDERPATH, NEW_MAIN_DB_FILENAME)

        
        if os.path.exists(self.server_delta_db_filepath):
            self.server_delta_db = TunerDeltaDatabase(
                filepath=self.server_delta_db_filepath)
        else:
            self.server_delta_db = None

        if os.path.exists(self.server_main_db_filepath):
            self.server_main_db = TunerMainDatabase(
                filepath=self.server_main_db_filepath)
        else:
            self.server_main_db = None
            
            
    #----------------------------------------------------------------------
    def _initDBFiles(self):
        """"""
        
        # Initialize main DB
        server_main_db = TunerMainDatabase(filepath=self.server_main_db_filepath,
                                           create_folder=True)
        server_main_db._initTables()
        

        # Initialize delta DB that contains all the transactions
        # from all the clients
        server_delta_db = TunerDeltaDatabase(filepath=self.server_delta_db_filepath,
                                             create_folder=True)
        server_delta_db._initTables()
        
    #----------------------------------------------------------------------
    def updateServerMainDB(self):
        """"""
        
        print 'Periodic update of main database file (tuner.sqlite) begins...'
        try:
            shutil.copy(self.server_main_db_filepath, self.new_server_main_db_filepath)
            
            new_main_db = TunerMainDatabase(filepath=self.new_server_main_db_filepath)
            
            new_main_db.update(self.server_delta_db)
            
            self.server_delta_db.updateDeltaDBOnSyncSuccess()
            
            shutil.move(self.new_server_main_db_filepath,
                        self.server_main_db_filepath)
            
        except:
            traceback.print_exc()
            print 'Failed to apply transaction(s) to Server main database.'
            raise RuntimeError()
        else:
            print 'Periodic update of main database file was successful.'
        
    #----------------------------------------------------------------------
    def insertConfigRecordsOnServer(self, debug=False):
        """"""
        
        if debug:
            self.server_delta_db._initTables() # Making sure server_delta is clean for this
            # testing purpose
        
        self.server_delta_db.insertConfigRecordsOnServer()
        
    #----------------------------------------------------------------------
    def createClientServerDeltaDB(self):
        """"""
        
        print 'Creating client_server_delta DB file...'
        
        client_delta_db = TunerDeltaDatabase(filepath=self.client_delta_db_filepath)
        client_server_delta_db = TunerDeltaDatabase(
            filepath=self.client_server_delta_db_filepath)
        
        client_last_sync_timestamp = client_delta_db.getColumnDataFromTable(
            'sync_table',column_name_list=['last_timestamp'])[0][0]
        client_delta_db.close()
        
        client_server_delta_db._initTables()
        client_server_delta_db.attachDatabase(self.server_delta_db_filepath,
                                              'server_delta_db')
        client_server_delta_db.insertTable('delta_table',
                                           foreign_database_name='server_delta_db',
                                           foreign_table_name='delta_table',
                                           condition_str='server_delta_db.delta_table.tunix > ?',
                                           binding_tuple=(client_last_sync_timestamp,))
        client_server_delta_db.close()

        print 'Done.'
        
        print 'Removing client_delta DB file sent from Client...'
        os.remove(self.client_delta_db_filepath)
        print 'Done.'
        
    #----------------------------------------------------------------------
    def sendClientServerDelta(self):
        """"""
        
        self.insertConfigRecordsOnServer()
        
        self.createClientServerDeltaDB()
        
        connection, client_address = self.sock.accept()        
        try:
            f = open(self.client_server_delta_db_filepath,'rb')
            print 'Sending client_server_delta DB file to Client...'
            
            while True:
                data = f.read(BLOCK_SIZE)
                if not data: f.close(); break
                connection.sendall(data)
            print 'Done.'
        except:
            traceback.print_exc()
            raise RuntimeError()
        
        print 'Closing client connection'
        connection.close()
        
        print 'Removing client_server_delta DB file...'
        os.remove(self.client_server_delta_db_filepath)
        print 'Done.'
        
        
        
########################################################################
class TunerClient(tcpip.Client):
    """"""

    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        
        logfilepath = os.path.join(CLIENT_DATA_FOLDERPATH,'client.log')
        logging.basicConfig(filename=logfilepath,level=logging.DEBUG,
                            format='%(asctime)s:%(levelname)s:%(message)s')
        
        tcpip.Client.__init__(self)
        
        # Persistent files
        self.client_delta_db_filepath = os.path.join(
            CLIENT_DATA_FOLDERPATH, CLIENT_DELTA_DB_FILENAME)
        self.client_main_db_filepath = os.path.join(
            CLIENT_DATA_FOLDERPATH, MAIN_DB_FILENAME)
        self.last_synced_main_db_filepath = os.path.join(
            CLIENT_DATA_FOLDERPATH, LAST_SYNCED_MAIN_DB_FILENAME)
        # Temporary files
        self.new_client_main_db_filepath = os.path.join(
            CLIENT_DATA_FOLDERPATH, NEW_MAIN_DB_FILENAME)
        self.client_server_delta_db_filepath = os.path.join(
            CLIENT_DATA_FOLDERPATH, CLIENT_SERVER_DELTA_DB_FILENAME)
        
        if os.path.exists(self.client_delta_db_filepath):
            self.client_delta_db = TunerDeltaDatabase(
                self.client_delta_db_filepath)
        else:
            self.client_delta_db = None

        if os.path.exists(self.client_main_db_filepath):
            self.client_main_db = TunerMainDatabase(
                self.client_main_db_filepath)
        else:
            self.client_main_db = None
        
    #----------------------------------------------------------------------
    def _initDBFiles(self):
        """"""
        
        # Initialize delta DB that contains all the transactions
        # performed by this client only
        client_delta_db = TunerDeltaDatabase(self.client_delta_db_filepath,
                                             create_folder=True)
        client_delta_db._initTables()

        # Copy the main DB file from the server
        self._copyMainDBFileFromServer()
        
        # Make a backup copy of the main DB file for easy syncing later on
        self._backupMainDBFile()
        
    #----------------------------------------------------------------------
    def _copyMainDBFileFromServer(self):
        """"""
        
        # Make sure that the main DB file on the server is fully updated with
        # the server's delta DB file, before copying the file over.

        #shutil.copy(self.server_main_db_filepath, self.client_main_db_filepath)
        self.receiveFile(MAIN_DB_FILENAME, src_folderpath=SERVER_DATA_FOLDERPATH)
        shutil.move(MAIN_DB_FILENAME, self.client_main_db_filepath)
        
    #----------------------------------------------------------------------
    def _backupMainDBFile(self):
        """"""
        
        shutil.copy(self.client_main_db_filepath,
                    self.last_synced_main_db_filepath)
        
    #----------------------------------------------------------------------
    def _getClientServerDelta(self):
        """"""

        try:
            self.sendRequestHeader('sendClientServerDelta')
        except:
            print 'ERROR: There appears to be a network problem.'
            print 'Make sure that the server is running.'
            return
        
        self.connectToServer(timeout=600.)
        #
        try:
            f = open(self.client_server_delta_db_filepath,'wb')
            print 'Downloading client_server_delta DB file from server...'
            
            while True:
                data = self.sock.recv(BLOCK_SIZE)
                if not data: f.close(); break
                f.write(data)
            print 'Finished downloading successfully.'
        except:
            traceback.print_exc()
            print 'Error while receiving client_server_delta DB file from Server.'
        #
        self.closeSocket()
        
    #----------------------------------------------------------------------
    def _updateDBOnClient(self):
        """"""
        
        shutil.copy(self.last_synced_main_db_filepath,
                    self.new_client_main_db_filepath)
        
        try:
            new_main_db = TunerMainDatabase(filepath=self.new_client_main_db_filepath)
        
            client_server_delta_db = TunerDeltaDatabase(
                filepath=self.client_server_delta_db_filepath)
        
            new_main_db.update(client_server_delta_db)

        except:
            traceback.print_exc()
            print 'Failed to appply transaction(s) to Client main database.'
            raise RuntimeError()
        
    #----------------------------------------------------------------------
    def _finalizeSync(self):
        """"""
        
        self.client_delta_db.updateDeltaDBOnSyncSuccess()
        self.client_delta_db.deleteRows('delta_table') # delete all rows in "delta_table"
        
        os.remove(self.client_server_delta_db_filepath)
        
        shutil.move(self.new_client_main_db_filepath,
                    self.client_main_db_filepath)
        
        shutil.copy(self.client_main_db_filepath,
                    self.last_synced_main_db_filepath)
        
    #----------------------------------------------------------------------
    def syncWithServer(self):
        """"""
        
        try:
            print 'Sending client_delta DB file from Client to Server...'
            self.sendFile(self.client_delta_db_filepath,
                          destination_folderpath=SERVER_DATA_FOLDERPATH,
                          debug=False)
        except:
            traceback.print_exc()
            print 'ServerSyncFailure: Failed to send client_delta DB file to Server.'
            return
        else:
            print 'Finished sending client_delta DB file successfully.'
        
        try:
            print 'Waiting for Server to send update DB file...'            
            self._getClientServerDelta()
        except:
            traceback.print_exc()
            print 'ServerSyncFailure: Failed to receive client_server_delta DB file from Server.'

            try: os.remove(self.client_server_delta_db_filepath)
            except: pass
            
            return
        else:
            print 'Successfully received update DB file from Server.'
        
        try:
            print 'Applying the update from Server to Client DB...'
            self._updateDBOnClient()
        except:
            traceback.print_exc()
            print 'ServerSyncFailure: Failed to apply update from Server.'
            
            try: os.remove(self.client_server_delta_db_filepath)
            except: pass
            try: os.remove(self.new_client_main_db_filepath)
            except: pass
            
            return
        else:
            print 'Successfully applied update to Client DB.'
        
        try:
            print 'Finalizing sync with Server...'
            self._finalizeSync()
        except:
            traceback.print_exc()
            msg = 'ServerSyncFailure: Failed to finalize sync w/ Server.'
            print msg
            
            logging.critical(msg+':'+str(sys.exc_info()))
            
            return
        else:
            print 'Syncing with Server successfully finished.'
        
########################################################################
class TunerTextFileManager(QDialog):
    """"""
    
    #----------------------------------------------------------------------
    def __init__(self, load, filepath):
        """Constructor"""
        
        self.load = load
        self.filepath = filepath
        
        QDialog.__init__(self)
        
        self.setWindowTitle('Text Column Specification')
        self.verticalLayout = QVBoxLayout(self)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label = QLabel(self)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.checkBox_group_names = QCheckBox(self)
        self.checkBox_group_names.setText('Group Names')
        self.checkBox_group_names.setChecked(True)
        self.checkBox_group_names.setObjectName("checkBox_group_names")
        self.horizontalLayout.addWidget(self.checkBox_group_names)
        self.checkBox_channel_names = QCheckBox(self)
        self.checkBox_channel_names.setText('Channel Names')
        self.checkBox_channel_names.setEnabled(False)
        self.checkBox_channel_names.setChecked(True)
        self.checkBox_channel_names.setObjectName("checkBox_channel_names")
        self.horizontalLayout.addWidget(self.checkBox_channel_names)
        self.checkBox_weights = QCheckBox(self)
        self.checkBox_weights.setText('Weights')
        self.checkBox_weights.setEnabled(False)
        self.checkBox_weights.setChecked(True)
        self.checkBox_weights.setObjectName("checkBox_weights")
        self.horizontalLayout.addWidget(self.checkBox_weights)
        self.checkBox_step_sizes = QCheckBox(self)
        self.checkBox_step_sizes.setText('Step Sizes')
        self.checkBox_step_sizes.setObjectName("checkBox_step_sizes")
        self.horizontalLayout.addWidget(self.checkBox_step_sizes)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.buttonBox = QDialogButtonBox(self)
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.connect(self.buttonBox, SIGNAL("accepted()"), self.accept)
        self.connect(self.buttonBox, SIGNAL("rejected()"), self.reject)
        
        if self.load:
            prompt = 'Check all the columns your text file contains:\n' + \
                '(The order of the columns must be as shown below.)'
        else:
            prompt = 'Check all the columns you want the text file to contain:\n' + \
                '(The order of the columns will be as shown below.)'
        self.label.setText(prompt)
        
        self.updateColumnSelection()
        
    #----------------------------------------------------------------------
    def updateColumnSelection(self):
        """"""
        
        self.selection = {
            'group_names': self.checkBox_group_names.isChecked(),
            'channel_names': self.checkBox_channel_names.isChecked(),
            'weights': self.checkBox_weights.isChecked(),
            'step_sizes': self.checkBox_step_sizes.isChecked(),
        }
        
    #----------------------------------------------------------------------
    def accept(self):
        """"""
        
        self.updateColumnSelection()        
        QDialog.accept(self)
        
    #----------------------------------------------------------------------
    def reject(self):
        """"""
        
        self.selection = None        
        QDialog.reject(self)
        
    #----------------------------------------------------------------------
    def closeEvent(self, event):
        """"""
        
        self.selection = None
        event.accept()
        
    #----------------------------------------------------------------------
    def saveConfigTextFile(self, data):
        """"""
        
        formatted_lines = tab_delimited_formatted_lines(data,
            always_tab_end=True, newline_end=True)
        
        f = open(self.filepath, 'w')
        try:
            f.writelines(formatted_lines)
        finally:
            f.close()
        
        
    #----------------------------------------------------------------------
    def loadConfigTextFile(self):
        """"""
        
        f = open(self.filepath, 'r')
        try:
            all_texts = f.read()
        finally:
            f.close()
        
        lines = all_texts.split('\n')
        data = [line.split() for line in lines if line != '']
        
        if sum(self.selection.values()) != len(data[0]):
            msgBox = QMessageBox()
            msgBox.setIcon(QMessageBox.Critical)
            msgBox.setText('Number of columns ('+str(len(data[0]))+
                           ') in your text file does not match '+
                           'the number of columns ('+
                           str(sum(self.selection.values()))+
                           ') you told in the previous dialog box.')
            msgBox.exec_()
            return None
        
        # Create group name from channel name, if group name is not provided
        if not self.selection['group_names']:
            for row in data: row.insert(0,row[0])

        # Change the data type of weight from string to float
        for row in data: row[2] = float(row[2])
        
        # Create step size from weight, if step size is not provided
        if not self.selection['step_sizes']:
            for row in data: row.append(row[-1])
        
        return data
            
        
        
########################################################################
class TunerHDF5Manager():
    """"""

    #----------------------------------------------------------------------
    def __init__(self, filepath, mode='r', create_fresh=False):
        """Constructor"""
        
        if mode in ('r','a'):
            self.fileObj = h5py.File(filepath,mode)
        elif mode == 'w':    
            if create_fresh:
                self.fileObj = self.getFreshHDF5FileObj(filepath)
            else:
                self.fileObj = h5py.File(filepath,'w')
        else:
            raise ValueError('mode argument must be "r", "a", or "w".')
        
        self.mode = mode
        
    #----------------------------------------------------------------------
    def close(self):
        """"""
        
        self.fileObj.close()
        
    #----------------------------------------------------------------------
    def getFreshHDF5FileObj(self, filepath):
        """
        After removing the existing HDF5 file, if you try to create a fresh
        HDF5 file with the same name, you may encounter an IO error.
        To avoid this race condition issue, wait a little before opening,
        and also do multiple trials until successful opening.
        """
        
        if os.path.exists(filepath):
            os.remove(filepath)
            sleep(1.)
        
        nMaxTrials = 5
        for i in range(nMaxTrials):
            try:
                f = h5py.File(filepath,'w')
            except:
                print 'Trial #' + int(i) + ': Opening ' + \
                      filepath + ' failed.'
                if i == nMaxTrials:
                    raise IOError('Failed opening '+filepath)
                sleep(1.)
            else:
                break        
        
        return f
        
    #----------------------------------------------------------------------
    def createConfigRecordHDF5(self, record_dict, close_on_exit=True):
        """"""
        
        f = self.fileObj
        
        user_id = f.create_group('user_id')
        
        ip_str, mac_str, username = getuserinfo()
        
        user_id.create_dataset('ip_str', (1,), data=ip_str,
                               dtype=H5_VARLENSTR, compression=H5_COMPRESSION)
        user_id.create_dataset('mac_str', (1,), data=mac_str,
                               dtype=H5_VARLENSTR, compression=H5_COMPRESSION)
        user_id.create_dataset('username', (1,), data=username,
                               dtype=H5_VARLENSTR, compression=H5_COMPRESSION)        
        
        f.create_dataset('transaction_type', (1,), data='insert_config',
                         dtype=H5_VARLENSTR, compression=H5_COMPRESSION)
        
        args = f.create_group('transaction_data')
        args.create_dataset('config_name', (1,), data=record_dict['config_name'], 
                            dtype=H5_VARLENSTR, compression=H5_COMPRESSION)
        args.create_dataset('time_created', (1,), data=record_dict['time_created'], 
                            compression=H5_COMPRESSION)
        args.create_dataset('description', (1,), data=record_dict['description'],
                            dtype=H5_VARLENSTR, compression=H5_COMPRESSION)
        args.create_dataset('appended_descriptions', (1,), 
                            data=record_dict['appended_descriptions'], 
                            dtype=H5_VARLENSTR, compression=H5_COMPRESSION)
        flat_channel_name_list = record_dict['flat_channel_name_list']
        nChannels = len(flat_channel_name_list)
        args.create_dataset('flat_channel_name_list', (nChannels,),
                            data=flat_channel_name_list, dtype=H5_VARLENSTR,
                            compression=H5_COMPRESSION)
        weight_list = record_dict['weight_list']
        args.create_dataset('weight_list', (nChannels,),
                            data=weight_list, compression=H5_COMPRESSION)
        step_size_list = record_dict['step_size_list']
        args.create_dataset('step_size_list', (nChannels,),
                            data=weight_list, compression=H5_COMPRESSION)
        indiv_ramp_table = record_dict['indiv_ramp_table']
        args.create_dataset('indiv_ramp_table', (nChannels,),
                            data=indiv_ramp_table, compression=H5_COMPRESSION)        
        group_name_list = record_dict['group_name_list']
        nGroups = len(group_name_list)
        args.create_dataset('group_name_list',(nGroups,),
                            data=group_name_list, dtype=H5_VARLENSTR,
                            compression=H5_COMPRESSION)
        grouped_ind_list = record_dict['grouped_ind_list']
        g = args.create_group('grouped_ind_list')
        for (group_ind,group_name) in enumerate(group_name_list):
            index_list = grouped_ind_list[group_ind]
            g.create_dataset(group_name,(len(index_list),),
                             data=index_list, compression=H5_COMPRESSION)
        
        
        if close_on_exit:
            self.close()
        
        
        
    
    
########################################################################
class TunerMainDatabase(SQLiteDatabase):
    """"""
    
    #----------------------------------------------------------------------
    def __init__(self, filepath=MEMORY, create_folder=False):
        """Constructor"""
        
        SQLiteDatabase.__init__(self, filepath=filepath,
                                create_folder=create_folder)

    #----------------------------------------------------------------------
    def _initTables(self):
        """
        Assumption: Channel name will NEVER be changed, but PV name(s) associated
        with channel name MIGHT be changed.
        
        When associated PV name(s) are changed for a channel name, create a new
        channel ID for the new association. For config and new snapshots, use the
        latest channel ID. For old snapshots, the snapshot contains a channel ID,
        NOT channe name, so that there will be no ambiguity as to which PV's the
        old snapshot used when the snapshot was taken.
        """
        
        self.dropAllTables()
        
        global DEBUG
        DEBUG = False
        
        self.setForeignKeysEnabled(True)
        
        table_name = 'transaction_table'
        column_def = [
            Column('last_transaction_id','INTEGER',allow_null=False),
            Column('last_timestamp','REAL',allow_null=False),
        ]
        self.createTable(table_name, column_def)
        self.insertRows(table_name,list_of_tuples=[(0,),],
            bind_replacement_list_of_tuples=
            [(1,self.getCurrentEpochTimestampSQLiteFuncStr(data_type='float')),])

        table_name = 'unit_table'
        column_def = [
            Column('unit_id','INTEGER',primary_key=True),
            Column('unit_name','TEXT',allow_null=False,unique=True),
        ]
        self.createTable(table_name, column_def)
        self.insertRows(table_name,[('unknown',),
                                    ('dimensionless',),])
        
        table_name = 'user_table'
        column_def = [
            Column('user_id','INTEGER',primary_key=True),
            Column('ip_str','TEXT',allow_null=False),
            Column('mac_str','TEXT',allow_null=False),
            Column('username','TEXT',allow_null=False),
        ]
        self.createTable(table_name, column_def)
    
        table_name = 'channel_name_table'
        column_def = [
            Column('channel_name_id','INTEGER',primary_key=True),
            Column('channel_name','TEXT',unique=True,allow_null=False),
        ]
        self.createTable(table_name, column_def)    
        
        table_name = 'channel_table'
        column_def = [
            Column('channel_id','INTEGER',primary_key=True),
            Column('channel_name_id','INTEGER',allow_null=False),
            Column('pvrb_name','TEXT',allow_default=True,default_value=None),
            Column('pvsp_name','TEXT',allow_default=True,default_value=None),
            Column('time_created','REAL',allow_null=False),
            ForeignKeyConstraint(self,
                                 'fk_channel_name_id', 'channel_name_id',
                                 'channel_name_table', 'channel_name_id'),  
            UniqueTableConstraint(['channel_name_id','pvrb_name','pvsp_name']),
        ]
        self.createTable(table_name, column_def)
        
        table_name = 'channel_group_name_table'
        column_def = [
            Column('channel_group_name_id','INTEGER',primary_key=True),
            Column('channel_group_name','TEXT',unique=True,allow_null=False),
        ]
        self.createTable(table_name, column_def)
        
        table_name = 'config_meta_table'
        column_def = [
            Column('config_id','INTEGER',primary_key=True),
            Column('config_name','TEXT',allow_default=True,default_value='""'),
            Column('user_id','INTEGER',allow_null=False),
            Column('transaction_id','INTEGER',allow_null=False),
            Column('time_created','REAL',allow_null=False),
            Column('description','TEXT',allow_default=True,default_value='""'),
            Column('appended_descriptions','TEXT',allow_default=True,default_value='""'), # include modified time as part of the text in this
            ForeignKeyConstraint(self,
                                 'fk_user_id', 'user_id',
                                 'user_table', 'user_id'),        
        ]
        self.createTable(table_name, column_def)    
        
        table_name = 'config_table'
        column_def = [
            Column('config_id','INTEGER',allow_null=False),
            Column('channel_name_id','INTEGER',allow_null=False),
            Column('channel_group_name_id','INTEGER',allow_null=False),
            Column('weight','REAL',allow_default=True,default_value=None),
            Column('step_size','REAL',allow_default=True,default_value=None),
            Column('indiv_ramp_table','BLOB',allow_default=True,default_value=None),
            ForeignKeyConstraint(self,
                                 'fk_config_id', 'config_id',
                                 'config_meta_table', 'config_id'),        
            ForeignKeyConstraint(self,
                                 'fk_channel_name_id', 'channel_name_id',
                                 'channel_name_table', 'channel_name_id'),        
            ForeignKeyConstraint(self,
                                 'fk_channel_group_name_id', 'channel_group_name_id',
                                 'channel_group_name_table', 'channel_group_name_id'),                
        ]
        self.createTable(table_name, column_def)    
        
        table_name = 'snapshot_meta_table'
        column_def = [
            Column('snapshot_id','INTEGER',primary_key=True),
            Column('config_id','INTEGER',allow_null=False),
            Column('snapshot_name','TEXT',allow_default=True,default_value='""'),
            Column('user_id','INTEGER',allow_null=False),
            Column('transaction_id','INTEGER',allow_null=False),
            Column('time_snapshot_taken','REAL',allow_null=False),        
            Column('description','TEXT',allow_default=True,default_value='""'),
            Column('appended_descriptions','TEXT',allow_default=True,default_value='""'), # include modified time as part of the text in this
            Column('masar_event_id','INTEGER',allow_default=True,default_value=None),
            ForeignKeyConstraint(self,
                                 'fk_config_id', 'config_id',
                                 'config_meta_table', 'config_id'),        
            ForeignKeyConstraint(self,
                                 'fk_user_id', 'user_id',
                                 'user_table', 'user_id'),        
        ]
        self.createTable(table_name, column_def)    
        
        table_name = 'snapshot_table'
        column_def = [
            Column('snapshot_id','INTEGER',allow_null=False),
            Column('channel_id','INTEGER',allow_null=False),
            Column('pvrb_raw_value','REAL',allow_default=True,default_value=None),
            Column('pvrb_unit_value','REAL',allow_default=True,default_value=None),
            Column('pvrb_unit_id','INTEGER',allow_default=True,default_value=1),
            Column('pvrb_ioc_timestamp','INTEGER',allow_default=True,default_value=None),
            Column('pvrb_pc_timestamp','REAL',allow_default=True,default_value=None),
            Column('pvsp_raw_value','REAL',allow_default=True,default_value=None),
            Column('pvsp_unit_value','REAL',allow_default=True,default_value=None),
            Column('pvsp_unit_id','INTEGER',allow_default=True,default_value=1),
            Column('pvsp_ioc_timestamp','INTEGER',allow_default=True,default_value=None),
            Column('pvsp_pc_timestamp','REAL',allow_default=True,default_value=None),
            ForeignKeyConstraint(self,
                                 'fk_snapshot_id', 'snapshot_id',
                                 'snapshot_meta_table', 'snapshot_id'),        
            ForeignKeyConstraint(self,
                                 'fk_channel_id', 'channel_id',
                                 'channel_table', 'channel_id'),        
            ForeignKeyConstraint(self,
                                 'fk_pvrb_unit_id', 'pvrb_unit_id',
                                 'unit_table', 'unit_id'),        
            ForeignKeyConstraint(self,
                                 'fk_pvsp_unit_id', 'pvsp_unit_id',
                                 'unit_table', 'unit_id'),        
        ]
        '''Note that the 2nd column is 'channel_id', NOT 'channel_name_id' as in config_table.
        This is because channel_name_id may point to different PV's at some later time,
        but channel_id will always point to the same PV's, which may or may not
        exist later.
        '''
        self.createTable(table_name, column_def)    
        
        print 'Successfully initialized main database tables for aplattuner.'        
        
    #----------------------------------------------------------------------
    def checkUserID(self, ip_str, mac_str, username):
        """
        Check if a new user signature already exists in "user_table".
        
        If it does exist, then return the user_id.
        If not, add the new user signature, and return the newly created
        user_id.
        """
        
        user_id_list = self.getColumnDataFromTable(
            'user_table',column_name_list=['user_id'],
            condition_str='ip_str = ? AND mac_str = ? AND username = ?',
            binding_tuple=(ip_str,mac_str,username))
        if user_id_list == []:
            self.insertRows('user_table',list_of_tuples=[(ip_str,mac_str,username),])
            user_id = self.getMaxInColumn('user_table','user_id')
        else:
            user_id = user_id_list[0][0]
            
        
        return user_id
    
    #----------------------------------------------------------------------
    def getLastTransactionID(self):
        """"""
        
        last_transaction_id = self.getColumnDataFromTable(
            'transaction_table', column_name_list=['last_transaction_id'])
        if last_transaction_id == []:
            last_transaction_id = 0
        else:
            last_transaction_id = last_transaction_id[0][0]
            
        return last_transaction_id
        
    #----------------------------------------------------------------------
    def update(self, delta_db):
        """"""
        
        last_transaction_id = self.getLastTransactionID()
        
        tuple_of_lists = delta_db.getColumnDataFromTable(
            'delta_table', column_name_list=['*'],condition_str=' kid > ?',
            order_by_str='kid', binding_tuple=(last_transaction_id,))
        if tuple_of_lists == []:
            print 'Main DB file already up-to-date.'
            return
        else:
            new_transaction_id_list, new_timestamp_list, new_transaction_type_list, \
                new_transaction_data_list = tuple_of_lists
        
        for (trans_id, timestamp, trans_type, trans_data) in \
            zip(new_transaction_id_list, new_timestamp_list, 
                new_transaction_type_list, new_transaction_data_list):
    
            user_id = self.checkUserID(trans_data['ip_str'],trans_data['mac_str'],
                                       trans_data['username'])
        
            if trans_type == 'insert_config':
                self.insertConfig(user_id, trans_id, trans_data)
            elif trans_type == 'insert_snapshot':
                raise NotImplementedError('transaction type: ' + trans_type)
            elif trans_type == 'append_description':
                raise NotImplementedError('transaction type: ' + trans_type)
            else:
                raise NotImplementedError('transaction type: ' + trans_type)
        
        self.updateTransactionTable(delta_db)
        
    #----------------------------------------------------------------------
    def updateTransactionTable(self, delta_db):
        """"""
        
        last_transaction_id = delta_db.getMaxInColumn(
            'delta_table','kid')
        last_timestamp = delta_db.getColumnDataFromTable(
            'delta_table', column_name_list=['tunix'], 
            condition_str='kid = ?', binding_tuple=(last_transaction_id,))[0][0]
        
        self.changeValues('transaction_table','last_transaction_id','?',
                          binding_tuple=(last_transaction_id,))
        self.changeValues('transaction_table','last_timestamp','?',
                          binding_tuple=(last_timestamp,))
        
        
        
    #----------------------------------------------------------------------
    def insertConfig(self, user_id, trans_id, trans_data):
        """"""
        
        # Update "config_meta_table"
        list_of_tuples=[(trans_data['config_name'],
                         user_id, trans_id,
                         trans_data['time_created'],
                         trans_data['description'],
                         trans_data['appended_descriptions']),]
        self.insertRows('config_meta_table',
                        list_of_tuples=list_of_tuples)

        # Update "channel_name_table"
        config_id = self.getMaxInColumn('config_meta_table','config_id')
        
        channel_name_list_of_tuples = [tuple((ch_name,)) for ch_name in
                                       trans_data['flat_channel_name_list']]
        self.insertRows('channel_name_table',
                        list_of_tuples=channel_name_list_of_tuples,
                        on_conflict='IGNORE')

        # Update "channel_table"
        channel_name_id_list = self.getColumnDataFromTable(
            'channel_name_table',column_name_list=['channel_name_id'],
            condition_str='channel_name = ?',
            binding_list_of_tuples=channel_name_list_of_tuples
            )[0]
        pvrb_name_list, pvsp_name_list = getpvnames(
            trans_data['flat_channel_name_list'], return_zipped=False)
        time_created_list = [trans_data['time_created']]*len(channel_name_id_list)
        list_of_tuples = zip(channel_name_id_list,pvrb_name_list,pvsp_name_list,
                             time_created_list)
        #list_of_tuples = zip(channel_name_id_list,pvrb_name_list,pvsp_name_list)
        #bind_replacement_list_of_tuples = [
            #(-1, self.getCurrentEpochTimestampSQLiteFuncStr(data_type='float'))
        #]
        #self.insertRows('channel_table',list_of_tuples=list_of_tuples,
                        #on_conflict='IGNORE',
                        #bind_replacement_list_of_tuples=bind_replacement_list_of_tuples)
        self.insertRows('channel_table',list_of_tuples=list_of_tuples,
                        on_conflict='IGNORE')
        
        # Update "channel_group_name_table"
        group_name_list = trans_data['group_name_list']
        list_of_tuples = [tuple((g_name,)) for g_name in group_name_list]
        self.insertRows('channel_group_name_table',
                        list_of_tuples=list_of_tuples, on_conflict='IGNORE')

        # Update "config_table"
        config_id_list = [config_id]*len(channel_name_id_list)
        channel_group_name_id_list = [0]*len(channel_name_id_list)
        channel_group_name_id_unique_list = self.getColumnDataFromTable(
            'channel_group_name_table', column_name_list=['channel_group_name_id'],
            condition_str='channel_group_name = ?', 
            binding_list_of_tuples=[tuple((g,)) for g in group_name_list])[0]
        for (gid, ind_list) in zip(channel_group_name_id_unique_list,
                                   trans_data['grouped_ind_list']):
            for i in ind_list: channel_group_name_id_list[i] = gid
        weight_list = trans_data['weight_list']
        step_size_list = trans_data['step_size_list']
        indiv_ramp_table_list = [sqlite3.Binary(pickle.dumps(obj,protocol=2)) 
                                 for obj in trans_data['indiv_ramp_table']]
        list_of_tuples = zip(config_id_list, channel_name_id_list, channel_group_name_id_list,
                             weight_list, step_size_list, indiv_ramp_table_list)
        self.insertRows('config_table',list_of_tuples=list_of_tuples)
        
    
########################################################################
class TunerDeltaDatabase(SQLiteDatabase):
    """"""
    
    #----------------------------------------------------------------------
    def __init__(self, filepath=MEMORY, create_folder=False):
        """Constructor"""

        SQLiteDatabase.__init__(self, filepath=filepath,
                                create_folder=create_folder)

        self.ys = y_serial.Main(self.filepath)

    #----------------------------------------------------------------------
    def _initTables(self):
        """
        """
        
        self.dropAllTables()
        
        self.ys.createtable(table='delta_table')
        
        global DEBUG
        DEBUG = False
        
        table_name = 'sync_table'
        column_def = [
            Column('last_timestamp','REAL',allow_null=False),
        ]
        self.createTable(table_name, column_def)
        
        list_of_tuples = [(self.getCurrentEpochTimestamp(
            program='sqlite',return_type='float'),),]
        self.insertRows('sync_table',list_of_tuples)    
        
        print 'Successfully initialized delta database tables for aplattuner.'      
    
    #----------------------------------------------------------------------
    def insertConfigRecordOnClient(self, transaction_data):
        """"""
        
        transaction_type = 'insert_config'
        
        self.ys.insert(transaction_data, notes=transaction_type,
                       table='delta_table')
    
    #----------------------------------------------------------------------
    def insertConfigRecordsOnServer(self):
        """"""
        
        client_delta_filepath = os.path.join(SERVER_DATA_FOLDERPATH,
                                             CLIENT_DELTA_DB_FILENAME)
        server_delta_filepath = os.path.join(SERVER_DATA_FOLDERPATH,
                                             SERVER_DELTA_DB_FILENAME)
        
        client_delta_db = TunerDeltaDatabase(filepath=client_delta_filepath)
        timestamp_tuple, transaction_type_tuple, transaction_data_tuple = \
            client_delta_db.getColumnDataFromTable('delta_table',
            column_name_list=['tunix','notes','pzblob'])
        
        server_delta_db = TunerDeltaDatabase(filepath=server_delta_filepath)
        for (timestamp, transaction_type, transaction_data) in \
            zip(timestamp_tuple, transaction_type_tuple, transaction_data_tuple):
            server_delta_db.ys.insert(transaction_data, notes=transaction_type,
                                      table='delta_table')
        
        server_delta_db.changeValues('sync_table',column_name='last_timestamp',
            expression=server_delta_db.getCurrentEpochTimestampSQLiteFuncStr('float'))
    
    
    #----------------------------------------------------------------------
    def getColumnDataFromTable(self, table_name, column_name_list=None,
                               condition_str='', order_by_str='',
                               binding_tuple=None, binding_list_of_tuples=None,
                               print_cmd=False):
        """"""
        
        result_list_of_tuples = SQLiteDatabase.getColumnDataFromTable(
            self,table_name, column_name_list=column_name_list, 
            condition_str=condition_str, order_by_str=order_by_str,
            binding_tuple=binding_tuple, binding_list_of_tuples=binding_list_of_tuples,
            print_cmd=print_cmd)
        
        if result_list_of_tuples == []:
            return result_list_of_tuples
        
        if (table_name == 'delta_table'):
            select_request_contains_pzblob = (
                (column_name_list is None) or
                ('*' in column_name_list) or
                ('pzblob' in column_name_list)
            )
            if select_request_contains_pzblob:
                pzblob_col_ind = [i for (i,tup) in enumerate(result_list_of_tuples)
                                  if isinstance(tup[0],buffer)][0]
                pzblob_tuple = result_list_of_tuples[pzblob_col_ind]
                # Convert the binary "buffer" object to original Python object
                pyobj_list = [y_serial.pzloads(pzblob) for pzblob in pzblob_tuple]
                result_list_of_tuples[pzblob_col_ind] = tuple(pyobj_list)
        
        return result_list_of_tuples

    #----------------------------------------------------------------------
    def updateDeltaDBOnSyncSuccess(self):
        """"""
        
        self.changeValues('sync_table','last_timestamp',
            self.getCurrentEpochTimestampSQLiteFuncStr(data_type='float'))


#----------------------------------------------------------------------
def test1(args):
    """"""
    
    global DEBUG
    DEBUG = False
    
    db = TunerAbstractDatabase('test1.sqlite')
    
    db.getTableNames()
    
    try:
        table_name = 'channelNames'
        column_def = [
            Column('channel_name_id','INTEGER',primary_key=True),
            Column('channel_name','TEXT',allow_null=False,unique=True),
        ]
        db.createTable(table_name, column_def)
        db.getTableNames()
        db.getTableInfo(table_name)
        
        list_of_tuples = [
            ('QH1_1.K1',),
            ('QH1_2.K1',),
            ('QH2_1.K1',),
            ('QH3_1.K1',),
            ('QL1_1.K1',),
            ('QL2_1.K1',),
        ]
        db.insertRows(table_name, list_of_tuples)
        #pprint( db.getAllColumnDataFromTable(table_name) )
    except:
        traceback.print_exc()
    
    try:    
        table_name = 'channels'
        column_def = [
            Column('channel_id','INTEGER',primary_key=True),
            Column('channel_name_id','INT',allow_null=False),
            Column('pvrb_name','TEXT',allow_default=True,default_value=None),
            Column('pvsp_name','TEXT',allow_default=True,default_value=None),
            Column('time_created','REAL',allow_null=False),
            ForeignKeyConstraint(db,
                                 'fk_channel_name_id', 'channel_name_id',
                                 'channelNames', 'channel_name_id'),
        ]
        db.createTable(table_name, column_def)
        db.getTableNames()
        db.getTableInfo(table_name)
    
        list_of_tuples = [
            (1,'pvrb_QH1_1','pvsp_QH1_1',time()),
            (2,'pvrb_QH1_2','pvsp_QH1_2',time()),
            (3,'pvrb_QH2_1','pvsp_QH2_1',time()),
            (4,'pvrb_QH3_1','pvsp_QH3_1',time()),
            (5,'pvrb_QL1_1','pvsp_QL1_1',time()),
            (6,'pvrb_QL2_1','pvsp_QL2_1',time()),
            (2,'pvrb_QH1_2_new','pvsp_QH1_2',time()),
        ]
        db.insertRows(table_name, list_of_tuples)
        #pprint( db.getAllColumnDataFromTable(table_name) )
    except:
        traceback.print_exc()
        
    try:
        table_name = 'channelGroupsMeta'
        column_def = [
            Column('channel_group_id','INTEGER',primary_key=True),
            Column('channel_group_name','TEXT',allow_null=False),
        ]
        db.createTable(table_name, column_def)
        db.getTableNames()
        db.getTableInfo(table_name)
        
        list_of_tuples = [
            ('QH1',),
            ('QH2',),
            ('QH3',),
            ('QL1',),
            ('QL2',),
        ]
        db.insertRows(table_name, list_of_tuples)
        #pprint( db.getAllColumnDataFromTable(table_name) )
    except:
        traceback.print_exc()        

    try:
        table_name = 'channelGroups'
        column_def = [
            Column('channel_order_in_group','INTEGER',primary_key=True),
            Column('channel_group_id','INT',allow_null=False),
            Column('channel_name_id','INT',allow_null=False),
            ForeignKeyConstraint(db,
                                 'fk_channel_group_id', 'channel_group_id',
                                 'channelGroupsMeta', 'channel_group_id'),            
            ForeignKeyConstraint(db,
                                 'fk_channel_name_id', 'channel_name_id',
                                 'channelNames', 'channel_name_id'),            
        ]
        db.createTable(table_name, column_def)
        db.getTableNames()
        db.getTableInfo(table_name)
        
        list_of_tuples = [
            (1,2),
            (1,1),
            (2,3),
            (3,4),
            (4,5),
            (5,6),
        ]
        db.insertRows(table_name, list_of_tuples)
        #pprint( db.getAllColumnDataFromTable(table_name) )
    except:
        traceback.print_exc()        
        

    try:
        table_name = 'configsMeta'
        column_def = [
            Column('config_id','INTEGER',primary_key=True),
            Column('config_name','TEXT',allow_default=True,default_value=None),
            Column('username','TEXT',allow_null=False),
            Column('time_created','REAL',allow_null=False),
            Column('description','TEXT',allow_default=True,default_value=None),
            Column('appended_descriptions','TEXT',allow_default=True,default_value=None),
            Column('masar_event_id','INT',allow_default=True,default_value=None),            
        ]
        db.createTable(table_name, column_def)
        db.getTableNames()
        db.getTableInfo(table_name)
        
        list_of_tuples = [
            ('conf1','yhidaka',time(),'orig. desc. 1','Appended by yhidaka on 11/01/2012 10:10:10.1000 : appended description',None),
            ('conf2','lyyang',time(),'orig. desc. 2',None,None),
            ('conf3','yhidaka',time(),None,None,12345),
        ]
        db.insertRows(table_name, list_of_tuples)
        #pprint( db.getAllColumnDataFromTable(table_name) )
    except:
        traceback.print_exc()        
    
    try:
        table_name = 'configs'
        column_def = [
            Column('group_order_in_config','INTEGER',primary_key=True),
            Column('config_id','INT',allow_null=False),
            Column('channel_group_id','INT',allow_null=False),
            Column('weight','REAL',allow_null=False),
            ForeignKeyConstraint(db,
                                 'fk_config_id', 'config_id',
                                 'configsMeta', 'config_id'),            
            ForeignKeyConstraint(db,
                                 'fk_channel_group_id', 'channel_group_id',
                                 'channelGroupsMeta', 'channel_group_id'),            
        ]
        db.createTable(table_name, column_def)
        db.getTableNames()
        db.getTableInfo(table_name)
        
        list_of_tuples = [
            (1,1,1.1),
            (1,2,1.2),
            (1,3,1.3),
            (2,1,2.1),
            (2,2,2.2),
            (2,3,2.3),
            (3,4,0.5),
            (3,5,0.9),
        ]
        db.insertRows(table_name, list_of_tuples)
        #pprint( db.getAllColumnDataFromTable(table_name) )
    except:
        traceback.print_exc()        

    
    pprint( db.getColumnDataFromTable('configsMeta',column_name_list=['*'],
                                      condition_str='config_id=1') )
    pprint( db.getColumnDataFromTable('configs',column_name_list=['*'],
                                      condition_str='config_id=1') )
    channel_group_ids, weight = db.getColumnDataFromTable(
        'configs', column_name_list=['channel_group_id','weight'],
        condition_str='config_id=1')
    print "Channel Group ID's:", channel_group_ids
    print 'Weight:', weight
    
    for channel_group_id in channel_group_ids:
        channel_group_name, = db.getColumnDataFromTable(
            'channelGroupsMeta',column_name_list=['channel_group_name'],
            condition_str='channel_group_id=?', binding_tuple=(channel_group_id,)) 
        channel_group_name = channel_group_name[0]
        
        channel_name_ids, = db.getColumnDataFromTable(
            'channelGroups',column_name_list=['channel_name_id'],
            condition_str='channel_group_id=?', binding_tuple=(channel_group_id,))         
        #print 'channel_name_ids', channel_name_ids
        
        latest_channel_ids = []
        latest_pvrb_names = []
        latest_pvsp_names = []
        latest_times_created = []
        channel_names = []
        for channel_name_id in channel_name_ids:
            channel_name, = db.getColumnDataFromTable(
                'channelNames',column_name_list=['channel_name'],
                condition_str='channel_name_id=?', binding_tuple=(channel_name_id,))
            channel_names.append(channel_name[0])

            channel_ids, pvrb_names, pvsp_names, times_created = db.getColumnDataFromTable(
                'channels',column_name_list=['channel_id', 'pvrb_name', 'pvsp_name', 'time_created'],
                condition_str='channel_name_id=?', binding_tuple=(channel_name_id,))
            if len(channel_ids) == 1:
                latest_channel_ids.append( channel_ids[0] )
                latest_pvrb_names.append( pvrb_names[0] )
                latest_pvsp_names.append( pvsp_names[0] )
                latest_times_created.append( times_created[0] )
            else:
                print 'More than one channel_id has been found for channel_name_id:', channel_name_id, '(channel name:', channel_name, ')'
                latest_channel_ids.append( max(channel_ids) )
                latest_ind = channel_ids.index( max(channel_ids) )
                latest_pvrb_names.append( pvrb_names[latest_ind] )
                latest_pvsp_names.append( pvsp_names[latest_ind] )
                latest_times_created.append( times_created[latest_ind] )

        print 'Channel Group ID:', channel_group_id, 'Channel Group Name:', channel_group_name, \
              "Channel Name ID's:", channel_name_ids, "Latest Channel ID's:", latest_channel_ids, \
              'Channel Names:', channel_names, "Latest PV-RB's:", latest_pvrb_names, "Latest PV-SP's:", latest_pvsp_names, \
              "Latest Created Times:", latest_times_created 
            
    db.createTempView('[channel groups view incomplete]', 
                      'configs cf JOIN configsMeta cfM ON (cf.config_id=cfM.config_id)', # table_name
                      column_name_list=['cf.group_order_in_config', 'cf.channel_group_id', 'cf.weight'],
                      condition_str='cf.config_id=1')
    db.createTempView('[channel groups view]', 
                      '[channel groups view incomplete] v_chG JOIN channelGroupsMeta chGM ON (v_chG.channel_group_id=chGM.channel_group_id)', # table_name
                      column_name_list=['v_chG.group_order_in_config', 'v_chG.channel_group_id', 'chGM.channel_group_name', 'v_chG.weight'],
                      order_by_str='v_chG.channel_group_id')
    db.createTempView('[channels view incomplete A]', 
                      'channelGroups chG JOIN [channel groups view] v_chG ON (chG.channel_group_id = v_chG.channel_group_id)', # table_name
                      column_name_list=['chG.channel_group_id', 'v_chG.channel_group_name', 
                                        'chG.channel_name_id', 'v_chG.weight', 'v_chG.group_order_in_config', 
                                        'chG.channel_order_in_group'])
    db.createTempView('[channels view incomplete B]', 
                      'channels ch JOIN channelNames chN ON (ch.channel_name_id = chN.channel_name_id)', # table_name
                      column_name_list=['ch.channel_name_id', 'chN.channel_name', 'ch.pvrb_name', 
                                        'ch.pvsp_name', 'ch.time_created'],
                      condition_str='chN.channel_name_id IN (SELECT v_ch_incomp.channel_name_id FROM [channels view incomplete A] v_ch_incomp)')
    db.createTempView('[channels view]', 
                      '[channels view incomplete A] v_ch_A, [channels view incomplete B] v_ch_B ON (v_ch_A.channel_name_id = v_ch_B.channel_name_id)', # table_name
                      column_name_list=['v_ch_A.channel_group_name', 'v_ch_A.weight', 
                                        'v_ch_A.group_order_in_config', 'v_ch_A.channel_order_in_group',
                                        'v_ch_B.channel_name', 'v_ch_B.pvrb_name', 'v_ch_B.pvsp_name',
                                        'v_ch_B.time_created'])
    
    print 'Channel Groups:', db.getColumnDataFromTable('[channel groups view]')
    print 'Channels A:'
    pprint( db.getColumnDataFromTable('[channels view incomplete A]') )
    print 'Channels B:'
    pprint( db.getColumnDataFromTable('[channels view incomplete B]') )
    print 'Channels:'
    pprint( db.getColumnDataFromTable('[channels view]', 
                                      order_by_str='group_order_in_config, channel_order_in_group') )
    
    sql_cmd = '''
       SELECT chN.channel_name
       FROM channelNames chN
       WHERE chN.channel_name_id IN
       (SELECT chG.channel_name_id
           FROM channelGroups chG
           WHERE chG.channel_group_id IN (SELECT channel_group_id FROM [channel groups view])
           );
           '''
    db.cur.execute(sql_cmd)
    z = db.cur.fetchall()
    print len(z)
    pprint(z)
    
    print 'finished successfully'
    
    db.close()


#----------------------------------------------------------------------
def startServer():
    """"""
    
    s = TunerServer()
    
    # Specify server DB updating function, which is to be performed
    # regularly when the server is idling.
    task = tcpip.ServerTask(min_interval=3.,
                            client_connection_timeout=1.)
    #task = tcpip.ServerTask(min_interval=24.*60.*60.,
                            #client_connection_timeout=30.*60.)
    #task.initialFunc = s.updateServerMainDB
    task.periodicFunc = s.updateServerMainDB
    s.task_list.append(task)

    s.startListening()
    
#----------------------------------------------------------------------
def initServerDBFiles():
    """
    Initialization of database files on Server.
    
    WARNING: All data in server datbase files will be wiped clean! 
    """

    server = TunerServer()
    server._initDBFiles()

#----------------------------------------------------------------------
def initClientDBFiles():
    """
    Initialization of database files on Client.
    
    WARNING: All data in client datbase files will be wiped clean! 
    """

    client = TunerClient()
    client._initDBFiles()
        
#----------------------------------------------------------------------
def test_syncWithServer():
    """"""

    ## Server Initialization
    initServerDBFiles()
    
    ## Client Initialization
    initClientDBFiles()
    
    ### using Tuner Config Setup, save some sample config to client_delta
    ## or use an already created client_delta, copy it and rename it
    shutil.copy('/home/yhidaka/.hla/nsls2/tuner_client/client_delta.sqlite.backup',
                '/home/yhidaka/.hla/nsls2/tuner_client/client_delta.sqlite')
    
    ## Try syncing
    client = TunerClient()
    client.syncWithServer()
    
    ## Check if tuner_client/tuner.sqlite == tuner_client/last_synced_tuner.sqlite
    dump1_filepath = os.path.join(CLIENT_DATA_FOLDERPATH, 'd1.dump')
    dump2_filepath = os.path.join(CLIENT_DATA_FOLDERPATH, 'd2.dump')
    client_main_db = TunerMainDatabase(filepath=client.client_main_db_filepath)
    client_main_db.dump(dump1_filepath)
    last_sync_db = TunerMainDatabase(filepath=client.last_synced_main_db_filepath)
    last_sync_db.dump(dump2_filepath)
    with open(dump1_filepath,'r') as f:
        t1 = f.read()
    with open(dump2_filepath,'r') as f:
        t2 = f.read()
    if t1 != t2:
        d = context_diff(t1.splitlines(1), t2.splitlines(1))
        pprint(list(d))
    
    ## Check if tuner_client/tuner.sqlite == tuner_server/tuner.sqlite
    try:
        client.sendRequestHeader('updateServerMainDB')
    except:
        print 'ERROR: There appears to be a network problem.'
        print 'Make sure that the server is running.'
        return
    print 'wating for server to finish update its database...'
    sleep(5.)
    print 'Done waiting.'
    server = TunerServer()
    dump3_filepath = os.path.join(CLIENT_DATA_FOLDERPATH, 'd3.dump')
    server_main_db = TunerMainDatabase(filepath=server.server_main_db_filepath)
    server_main_db.dump(dump3_filepath)
    with open(dump3_filepath,'r') as f:
        t3 = f.read()
    if t1 != t3:
        d = context_diff(t1.splitlines(1), t3.splitlines(1))
        pprint(list(d))
        
    os.remove(dump1_filepath)
    os.remove(dump2_filepath)
    os.remove(dump3_filepath)
        
    print 'File equality checks finished.'

    
#----------------------------------------------------------------------
def test_loadConfigFromDB(config_id):
    """"""
    
    client_main_db_filepath = os.path.join(CLIENT_DATA_FOLDERPATH,
                                           MAIN_DB_FILENAME)
    client_main_db = TunerMainDatabase(filepath=client_main_db_filepath)
    
    column_name_list = client_main_db.getColumnNames(
        'config_meta_table cm JOIN user_table u ON (cm.user_id=u.user_id)')
    column_name_list = [col for col in column_name_list if not (
        (col == 'user_id') or col.startswith('user_id:') )]
    #
    meta_data_list_of_tuples = client_main_db.getColumnDataFromTable(
        'config_meta_table cm JOIN user_table u ON (cm.user_id=u.user_id)',
        column_name_list=['*'], condition_str='cm.config_id = ?', binding_tuple=(config_id,))
    meta_data = {}
    for (col,tup) in zip(column_name_list, meta_data_list_of_tuples):
        meta_data[col] = tup[0]

    pprint( meta_data )
        
    client_main_db.createTempView('cf_cgn',
        'config_table cf JOIN channel_group_name_table cgn ON (cf.channel_group_name_id=cgn.channel_group_name_id)')
    client_main_db.createTempView('cf_cgn_cn',
            'cf_cgn JOIN channel_name_table cn ON (cf_cgn.channel_name_id=cn.channel_name_id)')
    client_main_db.createTempView('config_view',
            'cf_cgn_cn JOIN channel_table c ON (cf_cgn_cn.channel_name_id=c.channel_name_id)')
    
    column_name_list = client_main_db.getColumnNames('config_view')
    column_name_list = [col for col in column_name_list if not (
        (col == 'channel_group_name_id') or col.startswith('channel_group_name_id:') or
        (col == 'channel_name_id') or col.startswith('channel_name_id:') )] 
    pprint( column_name_list )
    
    config_view = client_main_db.getColumnDataFromTable('config_view',column_name_list=['*'],
                                                        condition_str='config_id = ?',
                                                        binding_tuple=(config_id,))
    pprint( np.array(zip(*config_view)) )
    
#----------------------------------------------------------------------    
if __name__ == "__main__" :
    
    #test_syncWithServer()
    
    test_loadConfigFromDB(config_id=1)
        