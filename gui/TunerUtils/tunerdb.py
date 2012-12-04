#! /usr/bin/env python

import sys, os
import numpy as np
from time import time, strftime, localtime, sleep
import h5py
import sqlite3
import cPickle as pickle
import traceback
from pprint import pprint
import shutil

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

#########################################################################
#class TunerServerDatabase(TunerAbstractDatabase):
    #""""""
    
    ##----------------------------------------------------------------------
    #def __init__(self, filepath=TUNER_SERVER_SQLITE_FILEPATH_ON_SERVER):
        #"""Constructor"""
        
        #folder_path = os.path.dirname(filepath)
        #if not os.path.exists(folder_path):
            #os.mkdir(folder_path)
        
        #TunerAbstractDatabase.__init__(self, filepath=filepath)

    ##----------------------------------------------------------------------
    #def _initH5(self):
        #""""""
        
        #server_data_folder_path = os.path.dirname(TUNER_SERVER_HDF5_FILEPATH)
        #if not os.path.exists(server_data_folder_path):
            #os.mkdir(server_data_folder_path)
        
        #f = self.getFreshHDF5FileObj(TUNER_SERVER_HDF5_FILEPATH)
        ##if os.path.exists(TUNER_SERVER_HDF5_FILEPATH):
            ##os.remove(TUNER_SERVER_HDF5_FILEPATH)
            ##sleep(1.)
        
        ##nMaxTrials = 5
        ##for i in range(nMaxTrials):
            ##try:
                ##f = h5py.File(TUNER_SERVER_HDF5_FILEPATH,'w')
            ##except:
                ##print 'Trial #' + int(i) + ': Opening ' + \
                      ##TUNER_SERVER_HDF5_FILEPATH + ' failed.'
                ##if i == nMaxTrials:
                    ##raise IOError('Failed opening '+TUNER_SERVER_HDF5_FILEPATH)
                ##sleep(1.)
            ##else:
                ##break

        #f.create_dataset('max_user_id', (1,), data=0,
                         #compression=H5_COMPRESSION)
        #f.create_group('user_ids')
        #f.create_dataset('max_record_id', (1,), data=0,
                         #compression=H5_COMPRESSION)
        
        #f.close()
        
    ##----------------------------------------------------------------------
    #def _initDB(self):
        #""""""

        #server_data_folder_path = os.path.dirname(TUNER_SERVER_HDF5_FILEPATH)
        #if not os.path.exists(server_data_folder_path):
            #os.mkdir(server_data_folder_path)
        
        #self._initTables()

    ##----------------------------------------------------------------------
    #def getUserIDFromServerDB(self, ip_str, mac_str, username):
        #""""""
        
        #ip_str = quote_string(ip_str)
        #mac_str = quote_string(mac_str)
        #username = quote_string(username)
        
        #matched_user_id_list = self.getColumnDataFromTable(
            #'user_table', column_name_list=['user_id'],
            #condition_str='ip_str=? AND mac_str=? AND username=?',
            #binding_tuple=(ip_str,mac_str,username))
        
        #if matched_user_id_list == []:
            #return None
        #elif len(matched_user_id_list) > 1:
            #raise ValueError('More than 1 match for user_id detected.')
        #else:
            #return matched_user_id_list[0]
        
        
    ##----------------------------------------------------------------------
    #def createServerUpdateH5(self):
        #"""
        #Create server_update.h5 from client.h5.

        #After creation of server_update.h5, do NOT delete client.h5 yet,
        #since it will be needed at a later step.
        #"""
        
        #if not os.path.exists(TUNER_CLIENT_HDF5_FILEPATH_ON_SERVER):
            #print 'No tuner_client.h5 found.'
            #return

        #f_client = h5py.File(TUNER_CLIENT_HDF5_FILEPATH_ON_SERVER,'r')
        
        #f_server_update = self.getFreshHDF5FileObj(TUNER_SERVER_UPDATE_HDF5_FILEPATH)
        
        #user_id = f_client['user_id']
        
        #ip_str = user_id['ip_str'][0]
        #mac_str = user_id['mac_str'][0]
        #username = user_id['username'][0]
        
        #g = f_server_update.create_group('user_id')
        #g.create_dataset('ip_str', (1,), data=ip_str,
                         #dtype=H5_VARLENSTR, compression=H5_COMPRESSION)
        #g.create_dataset('mac_str', (1,), data=mac_str,
                         #dtype=H5_VARLENSTR, compression=H5_COMPRESSION)
        #g.create_dataset('username', (1,), data=username,
                         #dtype=H5_VARLENSTR, compression=H5_COMPRESSION)
            
        #transaction_id_list = [int(k) for k in f_client.keys() if k not in
                               #('user_id','max_transaction_id','max_record_id')]
        #for (i, transaction_id) in enumerate(transaction_id_list):
            #client_record = f_client[str(transaction_id)]
            #record_group_name = str(i+1)
            #f_client.copy(client_record, f_server_update, name=record_group_name)
            #g = f_server_update[record_group_name]
            #g.create_dataset('transaction_id', (1,), data=transaction_id,
                             #compression=H5_COMPRESSION)
            
        
        #f_server_update.close()
        #f_client.close()

    ##----------------------------------------------------------------------
    #def updateServerDB(self):
        #"""
        #Use server_update.h5 to update server.sqlite.
        
        #After update, delete server_update.h5.
        #"""
        
        #f = h5py.File(TUNER_SERVER_UPDATE_HDF5_FILEPATH,'r')
        
        #u = f['user_id']
        
        #ip_str   = u['ip_str'][0]
        #mac_str  = u['mac_str'][0]
        #username = u['username'][0]

        #matched_user_id = self.getUserIDFromServerDB(ip_str, mac_str, username)
        #if matched_user_id is None:
            #time_added = time()
            #list_of_tuples = [(ip_str, mac_str, username, time_added),]
            #self.insertRows('user_table',list_of_tuples)
            #matched_user_id = self.getUserIDFromServerDB(ip_str, mac_str, username)
        

        #record_id_list = [int(k) for k in f.keys() 
                          #if k not in ('new_user_id')]
        
        #for i in record_id_list:
            #rec = f[str(i)]
            #transaction_id = rec['transaction_id'][0]
            #time_added     = time()
            #command        = rec['command'][0]
            #args           = rec['args']
            
            #if command == 'insert config':
                #list_of_tuples = [(args['config_name'], matched_user_id, 
                                   #transaction_id, args['time_created'],
                                   #args['description'], args['appended_descriptions'],
                                   #time_added)]
                #self.insertRows('config_meta_table',list_of_tuples)
                
                #list_of_tuples = [(group_name,) for group_name 
                                  #in args['group_name_list']]
                #self.insertRows('channel_group_name_table',list_of_tuples)
                
                #list_of_tuples = [(channel_name,) for channel_name in
                                  #args['flat_channel_name_list']]
                #self.insertRows('channel_name_table',list_of_tuples,
                                #on_conflict='IGNORE')
                #''' Since channel_name column in channel_name_table is UNIQUE,
                #trying to add existing channels will result in conflict,
                #which will be ignored by setting on_conflict='IGNORE'. '''
                
                #self.insertRows('channel_table',list_of_tuples)
                
                #self.insertRows('config_table',list_of_tuples)
                
            #elif command == 'insert snapshot':
                #raise NotImplementedError('insert snapshot is not yet implemented.')
            #else:
                #raise ValueError('Unexpected command type: '+command)
        
        
        #f.close()

        #try:
            #os.remove(TUNER_SERVER_UPDATE_HDF5_FILEPATH)
        #except:
            #print 'Failed deleting', TUNER_SERVER_UPDATE_HDF5_FILEPATH
        
        
    ##----------------------------------------------------------------------
    #def createClientUpdateH5(self):
        #"""
        #Create client_update.h5 from server.h5, only including the
        #records in server.h5 with record_id larger than max_record_id
        #in client.h5.
        
        #After creation of client_update.h5, delete client.h5.
        #"""
        
    ##----------------------------------------------------------------------
    #def sendClientUpdateH5toClient(self):
        #"""
        #Send client_update.h5 to the client.
        
        #Then delete client_update.h5 on the server.
        #"""

        
#########################################################################
#class TunerClientDatabase(TunerAbstractDatabase):
    #""""""
    
    ##----------------------------------------------------------------------
    #def __init__(self, filepath=TUNER_CLIENT_SQLITE_FILEPATH):
        #"""Constructor"""
        
        #folder_path = os.path.dirname(filepath)
        #if not os.path.exists(folder_path):
            #os.mkdir(folder_path)
         
        #TunerAbstractDatabase.__init__(self, filepath=filepath)
        
    ##----------------------------------------------------------------------
    #def _initH5(self):
        #""""""
        
        #client_data_folder_path = os.path.dirname(TUNER_CLIENT_HDF5_FILEPATH_ON_CLIENT)
        #if not os.path.exists(client_data_folder_path):
            #os.mkdir(client_data_folder_path)
        
        #f = self.getFreshHDF5FileObj(TUNER_CLIENT_HDF5_FILEPATH_ON_CLIENT)
        ##if os.path.exists(TUNER_CLIENT_HDF5_FILEPATH_ON_CLIENT):
            ##os.remove(TUNER_CLIENT_HDF5_FILEPATH_ON_CLIENT)
            ##sleep(1.)
        
        ##nMaxTrials = 5
        ##for i in range(nMaxTrials):
            ##try:
                ##f = h5py.File(TUNER_CLIENT_HDF5_FILEPATH_ON_CLIENT,'w')
            ##except:
                ##print 'Trial #' + int(i) + ': Opening ' + \
                      ##TUNER_CLIENT_HDF5_FILEPATH_ON_CLIENT + ' failed.'
                ##if i == nMaxTrials:
                    ##raise IOError('Failed opening '+TUNER_CLIENT_HDF5_FILEPATH_ON_CLIENT)
                ##sleep(1.)
            ##else:
                ##break

        #user_id = f.create_group('user_id')
        #ip_str, mac_str, username = getuserinfo()
        #user_id.create_dataset('ip_str', (1,), data=ip_str,
                               #dtype=H5_VARLENSTR, compression=H5_COMPRESSION)
        #user_id.create_dataset('mac_str', (1,), data=mac_str,
                               #dtype=H5_VARLENSTR, compression=H5_COMPRESSION)
        #user_id.create_dataset('username', (1,), data=username,
                               #dtype=H5_VARLENSTR, compression=H5_COMPRESSION)
        
        #f.create_dataset('max_transaction_id', (1,), data=0,
                         #compression=H5_COMPRESSION)

        #f.create_dataset('max_record_id', (1,), data=0,
                         #compression=H5_COMPRESSION)
        
        #f.close()

        
    ##----------------------------------------------------------------------
    #def _initDB(self):
        #""""""
        
        #client_data_folder_path = os.path.dirname(TUNER_CLIENT_HDF5_FILEPATH_ON_CLIENT)
        #if not os.path.exists(client_data_folder_path):
            #os.mkdir(client_data_folder_path)

        #self._initTables()
    
    ##----------------------------------------------------------------------
    #def updateUserIDinClientH5(self, h5FileObject=None):
        #""""""
        
        #if h5FileObject is None:
            #f = h5py.File(TUNER_CLIENT_HDF5_FILEPATH_ON_CLIENT,'a')
        #else:
            #f = h5FileObject
        
        #user_id = f['user_id']
        
        #ip_str, mac_str, username = getuserinfo()
        
        #for k in ['ip_str','mac_str','username']:
            #del user_id[k]

        #user_id.create_dataset('ip_str', (1,), data=ip_str,
                               #dtype=H5_VARLENSTR, compression=H5_COMPRESSION)
        #user_id.create_dataset('mac_str', (1,), data=mac_str,
                               #dtype=H5_VARLENSTR, compression=H5_COMPRESSION)
        #user_id.create_dataset('username', (1,), data=username,
                               #dtype=H5_VARLENSTR, compression=H5_COMPRESSION)
        
        #if h5FileObject is None:
            #f.close()

    ##----------------------------------------------------------------------
    #def getMaxUserRecordIDinClientH5(self, h5FileObject=None):
        #""""""
        
        #if h5FileObject is None:
            #f = h5py.File(TUNER_CLIENT_HDF5_FILEPATH_ON_CLIENT,'a')
        #else:
            #f = h5FileObject
            
        #max_transaction_id = f['max_transaction_id'][0]
                
        #if h5FileObject is None:
            #f.close()
            
        #return max_transaction_id

    ##----------------------------------------------------------------------
    #def updateMaxUserRecordIDinClientH5(self, h5FileObject=None):
        #""""""

        #if h5FileObject is None:
            #f = h5py.File(TUNER_CLIENT_HDF5_FILEPATH_ON_CLIENT,'a')
        #else:
            #f = h5FileObject
        
        #transaction_id_list = [int(k) for k in f.keys() if k not in
                               #('user_id','max_transaction_id','max_record_id')]
        
        #if transaction_id_list != []:
            #del f['max_transaction_id']
            #f['max_transaction_id'] = [max(transaction_id_list)]
                
        #if h5FileObject is None:
            #f.close()
    
    ##----------------------------------------------------------------------
    #def getMaxRecordIDinServerDB(self):
        #""""""

        #server_db = TunerClientDatabase(
            #filepath=TUNER_SERVER_SQLITE_FILEPATH_ON_CLIENT)
        
        #return server_db.getColumnDataFromTable('record_index_table')[0][0]
        
    ##----------------------------------------------------------------------
    #def updateMaxRecordIDinClientH5(self, h5FileObject=None):
        #""""""
        
        #if h5FileObject is None:
            #f = h5py.File(TUNER_CLIENT_HDF5_FILEPATH_ON_CLIENT,'a')
        #else:
            #f = h5FileObject

        #max_record_id_in_server_DB = self.getMaxRecordIDinServerDB()
        
        #del f['max_record_id']
        #f['max_record_id'] = [max_record_id_in_server_DB]
                
        #if h5FileObject is None:
            #f.close()

    ##----------------------------------------------------------------------
    #def addRecordIntoClientH5(self, record_dict, h5FileObject=None):
        #""""""

        #if h5FileObject is None:
            #f = h5py.File(TUNER_CLIENT_HDF5_FILEPATH_ON_CLIENT,'a')
        #else:
            #f = h5FileObject
            
        #self.updateUserIDinClientH5(f)
        
        #max_transaction_id = self.getMaxUserRecordIDinClientH5(f)
        
        #new_transaction_id = max_transaction_id + 1
        #record = f.create_group(str(new_transaction_id))

        #record.create_dataset('command', (1,), data='insert config',
                              #dtype=H5_VARLENSTR, compression=H5_COMPRESSION)
        
        #args = record.create_group('args')
        #args.create_dataset('config_name', (1,), data=record_dict['config_name'], 
                            #dtype=H5_VARLENSTR, compression=H5_COMPRESSION)
        #args.create_dataset('time_created', (1,), data=record_dict['time_created'], 
                            #compression=H5_COMPRESSION)
        #args.create_dataset('description', (1,), data=record_dict['description'],
                            #dtype=H5_VARLENSTR, compression=H5_COMPRESSION)
        #args.create_dataset('appended_descriptions', (1,), 
                            #data=record_dict['appended_descriptions'], 
                            #dtype=H5_VARLENSTR, compression=H5_COMPRESSION)
        #flat_channel_name_list = record_dict['flat_channel_name_list']
        #nChannels = len(flat_channel_name_list)
        #args.create_dataset('flat_channel_name_list', (nChannels,),
                            #data=flat_channel_name_list, dtype=H5_VARLENSTR,
                            #compression=H5_COMPRESSION)
        #group_name_list = record_dict['group_name_list']
        #nGroups = len(group_name_list)
        #args.create_dataset('group_name_list',(nGroups,),
                            #data=group_name_list, dtype=H5_VARLENSTR,
                            #compression=H5_COMPRESSION)
        #grouped_ind_list = record_dict['grouped_ind_list']
        #g = args.create_group('grouped_ind_list')
        #for (group_ind,group_name) in enumerate(group_name_list):
            #index_list = grouped_ind_list[group_ind]
            #g.create_dataset(group_name,(len(index_list),),
                             #data=index_list, compression=H5_COMPRESSION)
        
        #self.updateMaxUserRecordIDinClientH5(f)
        
        #self.updateMaxRecordIDinClientH5(f)

        #if h5FileObject is None:
            #f.close()
        
        


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
def main(args):
    """
    """
    
    pass

#----------------------------------------------------------------------
def debug():
    """"""

    pass

#----------------------------------------------------------------------
def test_initializationAtFirstEverTunerStartup():
    """"""
    
    ## Server Initialization
    server_main_filepath = os.path.join(SERVER_DATA_FOLDERPATH, 
                                        MAIN_DB_FILENAME)
    server_main_db = TunerMainDatabase(filepath=server_main_filepath,
                                       create_folder=True)
    server_main_db._initTables()
    #
    server_delta_filepath = os.path.join(SERVER_DATA_FOLDERPATH, 
                                         SERVER_DELTA_DB_FILENAME)
    server_delta_db = TunerDeltaDatabase(filepath=server_delta_filepath,
                                         create_folder=True)
    server_delta_db._initTables()
    
    ## Client Initialization
    client_delta_filepath = os.path.join(CLIENT_DATA_FOLDERPATH,
                                         CLIENT_DELTA_DB_FILENAME)
    client_delta_db = TunerDeltaDatabase(filepath=client_delta_filepath,
                                         create_folder=True)
    client_delta_db._initTables()
    #
    client_main_filepath = os.path.join(CLIENT_DATA_FOLDERPATH,
                                        MAIN_DB_FILENAME)
    shutil.copy(server_main_filepath, client_main_filepath)
    #
    client_last_synced_main_filepath = os.path.join(CLIENT_DATA_FOLDERPATH,
                                                    LAST_SYNCED_MAIN_DB_FILENAME)
    shutil.copy(client_main_filepath, client_last_synced_main_filepath)
    
#----------------------------------------------------------------------
def test_readClientDeltaDB():
    """"""
    
    client_delta_filepath = os.path.join(CLIENT_DATA_FOLDERPATH,
                                         CLIENT_DELTA_DB_FILENAME)
    client_delta_db = TunerDeltaDatabase(filepath=client_delta_filepath)
    
    #client_delta_db.ys.view(1,'delta_table')
    ##
    #print client_delta_db.ys.select(0,'delta_table') # get most recent n-th entry ->
    ## 0 means the most recent record
    ##
    print client_delta_db.getColumnDataFromTable('delta_table')
    print client_delta_db.getColumnDataFromTable('sync_table')
    
#----------------------------------------------------------------------
def test_sendClientDeltaToServerAndAddToServerDelta():
    """"""
    
    client_delta_filepath_on_client = os.path.join(CLIENT_DATA_FOLDERPATH,
                                                   CLIENT_DELTA_DB_FILENAME)
    client_delta_filepath_on_server = os.path.join(SERVER_DATA_FOLDERPATH,
                                                   CLIENT_DELTA_DB_FILENAME)
    shutil.copy(client_delta_filepath_on_client, client_delta_filepath_on_server)
    
    server_delta_filepath = os.path.join(SERVER_DATA_FOLDERPATH,
                                         SERVER_DELTA_DB_FILENAME)
    server_delta_db = TunerDeltaDatabase(filepath=server_delta_filepath)
    
    server_delta_db._initTables() # Making sure server_delta is clean for this
    # testing purpose
    
    server_delta_db.insertConfigRecordsOnServer()
    
#----------------------------------------------------------------------
def test_readServerDeltaDB():
    """"""
    
    server_delta_filepath = os.path.join(SERVER_DATA_FOLDERPATH,
                                         SERVER_DELTA_DB_FILENAME)
    server_delta_db = TunerDeltaDatabase(filepath=server_delta_filepath)
    
    print server_delta_db.getColumnDataFromTable('delta_table')
    print server_delta_db.getColumnDataFromTable('sync_table')
    
#----------------------------------------------------------------------
def test_createClientServerDeltaDB():
    """"""
    
    client_delta_filepath_on_server = os.path.join(SERVER_DATA_FOLDERPATH,
                                                   CLIENT_DELTA_DB_FILENAME)
    client_delta_db_on_server = TunerDeltaDatabase(
        filepath=client_delta_filepath_on_server)
    client_last_sync_timestamp =  client_delta_db_on_server.getColumnDataFromTable(
        'sync_table', column_name_list=['last_timestamp'])[0][0]
    client_delta_db_on_server.close()
    
    server_delta_filepath = os.path.join(SERVER_DATA_FOLDERPATH,
                                         SERVER_DELTA_DB_FILENAME)
    server_delta_db = TunerDeltaDatabase(filepath=server_delta_filepath)
    
    client_server_delta_filepath_on_server = os.path.join(SERVER_DATA_FOLDERPATH,
                                                          CLIENT_SERVER_DELTA_DB_FILENAME)
    client_server_delta_db = TunerDeltaDatabase(
        filepath=client_server_delta_filepath_on_server)
    client_server_delta_db._initTables()
    client_server_delta_db.attachDatabase(server_delta_filepath, 'server_delta_db')
    client_server_delta_db.insertTable('delta_table',
                                       foreign_database_name='server_delta_db',
                                       foreign_table_name='delta_table')
    
    print client_server_delta_db.getColumnDataFromTable('delta_table')
    print client_server_delta_db.getColumnDataFromTable('sync_table')    

    os.remove(client_delta_filepath_on_server)
    
#----------------------------------------------------------------------
def test_sendClientServerDeltaToClientAndDeleteItOnServer():
    """"""
    
    client_server_delta_filepath_on_client = os.path.join(
        CLIENT_DATA_FOLDERPATH, CLIENT_SERVER_DELTA_DB_FILENAME)
    client_server_delta_filepath_on_server = os.path.join(
        SERVER_DATA_FOLDERPATH, CLIENT_SERVER_DELTA_DB_FILENAME)
    shutil.copy(client_server_delta_filepath_on_server,
                client_server_delta_filepath_on_client)
    
    os.remove(client_server_delta_filepath_on_server)
    
    
#----------------------------------------------------------------------
def test_createNewTunerDBOnClient_applyClientServerDeltaToNewMainDB():
    """"""

    last_synced_tuner_db_filepath = os.path.join(CLIENT_DATA_FOLDERPATH,
                                                 LAST_SYNCED_MAIN_DB_FILENAME)
    new_tuner_db_filepath = os.path.join(CLIENT_DATA_FOLDERPATH,
                                         NEW_MAIN_DB_FILENAME)
    shutil.copy(last_synced_tuner_db_filepath,
                new_tuner_db_filepath)

    
    client_server_delta_filepath = os.path.join(
        CLIENT_DATA_FOLDERPATH, CLIENT_SERVER_DELTA_DB_FILENAME)
    
    client_server_delta_db = TunerDeltaDatabase(
        filepath=client_server_delta_filepath)
    new_tuner_db = TunerMainDatabase(filepath=new_tuner_db_filepath)
    
    last_transaction_id = new_tuner_db.getColumnDataFromTable(
        'transaction_table', column_name_list=['last_transaction_id'])
    if last_transaction_id == []:
        last_transaction_id = 0
    else:
        last_transaction_id = last_transaction_id[0][0]
    
    new_transaction_id_list, new_timestamp_list, new_transaction_type_list, \
        new_transaction_data_list = client_server_delta_db.getColumnDataFromTable(
            'delta_table', column_name_list=['*'],condition_str=' kid > ?',
            order_by_str='kid', binding_tuple=(last_transaction_id,))
    
    for (transaction_id, timestamp, trans_type, trans_data) in \
        zip(new_transaction_id_list, new_timestamp_list, new_transaction_type_list,
            new_transaction_data_list):

        user_id = new_tuner_db.checkUserID(trans_data['ip_str'],trans_data['mac_str'],
                                           trans_data['username'])

        if trans_type == 'insert_config':
            list_of_tuples=[(trans_data['config_name'],
                             user_id, transaction_id,
                             trans_data['time_created'],
                             trans_data['description'],
                             trans_data['appended_descriptions']),]
            new_tuner_db.insertRows('config_meta_table',
                                    list_of_tuples=list_of_tuples)
            print 'config_meta_table'
            pprint( new_tuner_db.getAllColumnDataFromTable('config_meta_table') )

            config_id = new_tuner_db.getMaxInColumn('config_meta_table','config_id')
            
            channel_name_list_of_tuples = [tuple((ch_name,)) for ch_name in
                                           trans_data['flat_channel_name_list']]
            new_tuner_db.insertRows('channel_name_table',
                                    list_of_tuples=channel_name_list_of_tuples,
                                    on_conflict='IGNORE')
            print 'channel_name_table'
            pprint( new_tuner_db.getAllColumnDataFromTable('channel_name_table') )            

            channel_name_id_list = new_tuner_db.getColumnDataFromTable(
                'channel_name_table',column_name_list=['channel_name_id'],
                condition_str='channel_name = ?',
                binding_list_of_tuples=channel_name_list_of_tuples
            )[0]
            pvrb_name_list, pvsp_name_list = getpvnames(
                trans_data['flat_channel_name_list'], return_zipped=False)
            list_of_tuples = zip(channel_name_id_list,pvrb_name_list,pvsp_name_list)
            bind_replacement_list_of_tuples = [
                (-1, new_tuner_db.getCurrentEpochTimestampSQLiteFuncStr(data_type='float'))
                ]
            new_tuner_db.insertRows('channel_table',list_of_tuples=list_of_tuples,
                                    on_conflict='IGNORE',
                                    bind_replacement_list_of_tuples=bind_replacement_list_of_tuples)
            print 'channel_table'
            pprint(new_tuner_db.getAllColumnDataFromTable('channel_table'))
            
            group_name_list = trans_data['group_name_list']
            list_of_tuples = [tuple((g_name,)) for g_name in group_name_list]
            new_tuner_db.insertRows('channel_group_name_table',
                                    list_of_tuples=list_of_tuples,
                                    on_conflict='IGNORE')
            print 'channel_group_name_table'
            pprint( new_tuner_db.getAllColumnDataFromTable('channel_group_name_table') )

            config_id_list = [config_id]*len(channel_name_id_list)
            channel_group_name_id_list = [0]*len(channel_name_id_list)
            channel_group_name_id_unique_list = new_tuner_db.getColumnDataFromTable(
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
            new_tuner_db.insertRows('config_table',list_of_tuples=list_of_tuples)
            print 'config_table'
            pprint( new_tuner_db.getAllColumnDataFromTable('config_table') )
            
        else:
            raise NotImplementedError('transaction type: ' + trans_type)
    
#----------------------------------------------------------------------
def test_finalizeClientMainDBUpdate():
    """"""
    client_server_delta_filepath = os.path.join(
            CLIENT_DATA_FOLDERPATH, CLIENT_SERVER_DELTA_DB_FILENAME)
    new_tuner_db_filepath = os.path.join(CLIENT_DATA_FOLDERPATH,
                                         NEW_MAIN_DB_FILENAME)
    
    client_server_delta_db = TunerDeltaDatabase(
        filepath=client_server_delta_filepath)
    new_tuner_db = TunerMainDatabase(filepath=new_tuner_db_filepath)

    last_transaction_id = client_server_delta_db.getMaxInColumn('delta_table','kid')
    last_timestamp = client_server_delta_db.getColumnDataFromTable('delta_table',
        column_name_list=['tunix'], condition_str='kid = ?', 
        binding_tuple=(last_transaction_id,))[0][0]
    new_tuner_db.changeValues('transaction_table','last_transaction_id','?',
                              binding_tuple=(last_transaction_id,))
    new_tuner_db.changeValues('transaction_table','last_timestamp','?',
                              binding_tuple=(last_timestamp,))


    tuner_db_filepath = os.path.join(CLIENT_DATA_FOLDERPATH,
                                     MAIN_DB_FILENAME)
    shutil.move(new_tuner_db_filepath, tuner_db_filepath)

    last_synced_db_filepath = os.path.join(CLIENT_DATA_FOLDERPATH,
                                           LAST_SYNCED_MAIN_DB_FILENAME)
    shutil.copy(tuner_db_filepath, last_synced_db_filepath)
    
    os.remove(client_server_delta_filepath)
    
    client_delta_filepath = os.path.join(CLIENT_DATA_FOLDERPATH,
                                         CLIENT_DELTA_DB_FILENAME)
    client_delta_db = TunerDeltaDatabase(filepath=client_delta_filepath)
    client_delta_db.deleteRows('delta_table') # delete all rows in "delta_table"
    client_delta_db.changeValues('sync_table','last_timestamp',
        client_delta_db.getCurrentEpochTimestampSQLiteFuncStr(data_type='float'))

#----------------------------------------------------------------------
def test_loadConfigFromDB(config_id):
    """"""
    
    client_main_db_filepath = os.path.join(CLIENT_DATA_FOLDERPATH,
                                           MAIN_DB_FILENAME)
    client_main_db = TunerMainDatabase(filepath=client_main_db_filepath)
    
    column_name_list = client_main_db.getColumnNames(
        'config_meta_table cm JOIN user_table u ON (cm.user_id=u.user_id)')
    column_name_list = [col for col in column_name_list if not col.startswith('user_id')]
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
        col.startswith('channel_group_name_id')
        or col.startswith('channel_name_id') )] 
    pprint( column_name_list )
    
    config_view = client_main_db.getColumnDataFromTable('config_view',column_name_list=['*'],
                                                        condition_str='config_id = ?',
                                                        binding_tuple=(config_id,))
    pprint( np.array(zip(*config_view)) )
    
#----------------------------------------------------------------------    
if __name__ == "__main__" :
    
    #test_initializationAtFirstEverTunerStartup()
    ## using Tuner Config Setup, save some sample config to client_delta
    #test_readClientDeltaDB()
    #test_sendClientDeltaToServerAndAddToServerDelta()
    #test_readServerDeltaDB()
    #test_createClientServerDeltaDB()
    #test_sendClientServerDeltaToClientAndDeleteItOnServer()
    #test_createNewTunerDBOnClient_applyClientServerDeltaToNewMainDB()
    #test_finalizeClientMainDBUpdate()
    test_loadConfigFromDB(config_id=1)
    
    