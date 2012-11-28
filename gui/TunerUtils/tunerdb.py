#! /usr/bin/env python

import sip
sip.setapi('QString', 2)
sip.setapi('QVariant', 2)

import sys, os
import numpy as np
from time import time, strftime, localtime
import h5py
import sqlite3
import traceback
from pprint import pprint

from config import (TUNER_CLIENT_HDF5_FILEPATH, TUNER_CLIENT_SQLITE_FILEPATH)

MEMORY = ':memory:'

DEBUG = False

########################################################################
class Column():
    """"""

    #----------------------------------------------------------------------
    def __init__(self, name, data_type, allow_null=True, unique=False,
                 allow_default=False, default_value=None):
        """Constructor"""
        
        self.name = name
        
        if data_type not in ('TEXT', 'REAL', 'INT', 'INTEGER', 'BLOB',
                             'INTEGER PRIMARY KEY'):
            raise ValueError('Unexpected data type: '+data_type)
        else:
            self.data_type = data_type
            
        self.allow_null = allow_null

        self.unique = unique

        self.allow_default = allow_default
        
        self.default_value = default_value
        
        
########################################################################
class ForeignKeyConstraint():
    """"""

    #----------------------------------------------------------------------
    def __init__(self, constraint_name, column_name, 
                 foreign_table_name, foreign_column_name):
        """Constructor"""
        
        self.name = constraint_name
        
        self.column_name = column_name
        
        # Foreign Key Clause
        self.foreign_table_name = foreign_table_name
        self.foreign_column_name = foreign_column_name
        
    
########################################################################
class SQLiteDatabase():
    """"""

    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        
        self.con = sqlite3.connect(TUNER_CLIENT_SQLITE_FILEPATH)
        self.cur = self.con.cursor()
        
        isinstance(self.con, sqlite3.Connection)
        isinstance(self.cur, sqlite3.Cursor)
    
    #----------------------------------------------------------------------
    def close(self):
        """"""
        
        with self.con:
            self.cur.execute('VACUUM')
        
        self.con.close()
    
    #----------------------------------------------------------------------
    def getTableNames(self):
        """"""

        self.cur.execute('SELECT name from sqlite_master WHERE type="table" ORDER BY name')
        table_name_list = self.cur.fetchall()
        
        if DEBUG:
            print 'Existing tables:', table_name_list
        
        return table_name_list
    
    #----------------------------------------------------------------------
    def getTableInfo(self, table_name):
        """"""
        
        self.cur.execute('PRAGMA table_info('+table_name+')')
        
        table_info_tuple = self.cur.fetchall()
        # List of tuples "t":
        #   t[0] = column order number
        #   t[1] = column name (Unicode)
        #   t[2] = data type (Unicode)
        #   t[3] = 1 if NOT NULL is specified
        #   t[4] = default value (Unicode)
        #   t[5] = 1 if integer primary key, 0 otherwise
        
        #if DEBUG:
            #pprint(table_info_tuple)
        
        table_info_dict_list = []
        for tup in table_info_tuple:
            table_info_dict = {}
            table_info_dict['column_number'] = tup[0]
            table_info_dict['column_name'] = tup[1]
            table_info_dict['data_type'] = tup[2]
            table_info_dict['allow_null'] = (tup[3]==0)
            table_info_dict['default_value'] = tup[4]
            table_info_dict['primary_key'] = (tup[5]==1)
            table_info_dict_list.append(table_info_dict)
            
        return table_info_dict_list
        
    #----------------------------------------------------------------------
    def getAllColumnDataFromTable(self, table_name):
        """"""
        
        self.cur.execute('SELECT * FROM ' + table_name)
        
        all_rows = self.cur.fetchall()
        
        return all_rows
    
    #----------------------------------------------------------------------
    @staticmethod
    def createSelectSQLStatement(table_name, column_name_list=None,
                                 condition_str='', order_by_str=''):
        """"""

        if column_name_list is None:
            column_name_list = ['*']
        
        column_str = ', '.join(column_name_list)
        
        sql_cmd = 'SELECT ' + column_str + ' FROM ' + table_name
        if condition_str != '':
            sql_cmd += ' WHERE ' + condition_str
        if order_by_str != '':
            sql_cmd += ' ORDER BY ' + order_by_str

        return sql_cmd
    
    #----------------------------------------------------------------------
    def getColumnDataFromTable(self, table_name, column_name_list=None,
                               condition_str='', order_by_str='',
                               placeholder_replacement_tuple=None):
        """
        Return a tuple of column data.
        
        placeholder_replacement_tuple will be inserted into '?' appearing in the SQL command
        """
        
        sql_cmd = self.createSelectSQLStatement(table_name, column_name_list, 
                                                condition_str, order_by_str)
        
        if placeholder_replacement_tuple is None:
            self.cur.execute(sql_cmd)
        else:
            self.cur.execute(sql_cmd, placeholder_replacement_tuple)
        
        z = self.cur.fetchall()
        #z = []
        #for row in self.cur:
            #z.append(row)
        
        return zip(*z)
        
    #----------------------------------------------------------------------
    def createTempView(self, view_name, table_name, column_name_list=None,
                       condition_str='', order_by_str='',
                       placeholder_replacement_tuple=None):
        """"""
        
        select_sql = self.createSelectSQLStatement(table_name, column_name_list,
                                                   condition_str, order_by_str)
        
        sql_cmd = 'CREATE TEMP VIEW ' + view_name + ' AS ' + select_sql
        
        if placeholder_replacement_tuple is None:
            self.cur.execute(sql_cmd)
        else:
            self.cur.execute(sql_cmd, placeholder_replacement_tuple)
        
    #----------------------------------------------------------------------
    def createTable(self, table_name, column_definition_list):
        """"""
        
        self.deleteTable(table_name)
        
        sql_cmd = 'CREATE TABLE ' + table_name + ' ('
        
        for col in column_definition_list:
            
            if isinstance(col, Column):
                L = [col.name, col.data_type]

                if col.data_type != 'INTEGER PRIMARY KEY':
                    if not col.allow_null:
                        L.append('NOT NULL')
                    if col.unique:
                        L.append('UNIQUE')
                    if col.allow_default:
                        default_str = 'DEFAULT '
                        if col.default_value is None:
                            default_str += 'NULL'
                        else:
                            default_str += str(col.default_value)
                        L.append(default_str)

                sql_cmd += ' '.join(L) + ', '
            
            elif isinstance(col, ForeignKeyConstraint):
                sql_cmd += ('CONSTRAINT ' + col.name +
                            ' FOREIGN KEY(' + col.column_name + ') ' +
                            'REFERENCES ' + col.foreign_table_name +
                            '(' + col.foreign_column_name + ')' + ', '
                            )
            
            else:
                raise ValueError('Unexpected column class')
        
        sql_cmd = sql_cmd[:-2] + ')'
        
        try:
            #print sql_cmd
            
            with self.con:
                self.cur.execute(sql_cmd)
        except:
            traceback.print_exc()
            print 'SQL cmd:', sql_cmd
                
    #----------------------------------------------------------------------
    def deleteTable(self, table_name):
        """"""
        
        with self.con:
            self.cur.execute('DROP TABLE IF EXISTS '+table_name)
        
    #----------------------------------------------------------------------
    def insertRows(self, table_name, list_of_tuples):
        """"""
        
        sql_cmd = 'INSERT INTO ' + table_name + ' VALUES '
        
        placeholder_list = ['?' if not info_dict['primary_key'] else 'null'
                            for info_dict in self.getTableInfo(table_name)]
        placeholder_str = '(' + ', '.join(placeholder_list) + ')'
        
        sql_cmd += placeholder_str
        
        try:
            with self.con:
                self.cur.executemany(sql_cmd, list_of_tuples)
        except:
            traceback.print_exc()
            
    #----------------------------------------------------------------------
    def setForeignKeysEnabled(self, TF):
        """"""
        
        if TF:
            state = 'ON'
        else:
            state = 'OFF'
        
        self.cur.execute('PRAGMA foreign_keys = '+state)
        self.con.commit()        
        
    
########################################################################
class TunerDatabase(SQLiteDatabase):
    """"""
    
    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        
        SQLiteDatabase.__init__(self)
        
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
        
        global DEBUG
        DEBUG = False
        
        db = SQLiteDatabase()
    
        #try:
            #os.remove(TUNER_CLIENT_SQLITE_FILEPATH)
        #except:
            #print 'Deleting database file failed.'
        
        db.setForeignKeysEnabled(True)
        
        table_name = 'record_index_table'
        column_def = [
            Column('last_record_id','INT',allow_default=True,default_value=0),
        ]
        db.createTable(table_name, column_def)    
        
        table_name = 'user_table'
        column_def = [
            Column('user_id','INTEGER PRIMARY KEY'),
            Column('ip_str','TEXT',allow_null=False),
            Column('mac_str','TEXT',allow_null=False),
            Column('username','TEXT',allow_null=False),        
        ]
        db.createTable(table_name, column_def)
    
        table_name = 'channel_name_table'
        column_def = [
            Column('channel_name_id','INTEGER PRIMARY KEY'),
            Column('channel_name','TEXT',unique=True,allow_null=False),
        ]
        db.createTable(table_name, column_def)    
        
        table_name = 'channel_table'
        column_def = [
            Column('channel_id','INTEGER PRIMARY KEY'),
            Column('channel_name_id','INTEGER',allow_null=False),
            Column('pvrb_name','TEXT',allow_default=True,default_value=None),
            Column('pvsp_name','TEXT',allow_default=True,default_value=None),
            Column('time_created','REAL',allow_null=False),
            ForeignKeyConstraint('fk_channel_name_id', 'channel_name_id',
                                 'channel_name_table', 'channel_name_id'),        
        ]
        db.createTable(table_name, column_def)
        
        table_name = 'channel_group_name_table'
        column_def = [
            Column('channel_group_name_id','INTEGER PRIMARY KEY'),
            Column('channel_group_name','TEXT',allow_null=False),
        ]
        db.createTable(table_name, column_def)
        
        table_name = 'config_meta_table'
        column_def = [
            Column('config_id','INTEGER PRIMARY KEY'),
            Column('config_name','TEXT',allow_default=True,default_value='""'),
            Column('user_id','INTEGER',allow_null=False),
            Column('user_record_id','INTEGER',allow_null=False),
            Column('time_created','REAL',allow_null=False),
            Column('description','TEXT',allow_default=True,default_value='""'),
            Column('appended_descriptions','TEXT',allow_default=True,default_value='""'), # include modified time as part of the text in this
            ForeignKeyConstraint('fk_user_id', 'user_id',
                                 'user_table', 'user_id'),        
        ]
        db.createTable(table_name, column_def)    
        
        table_name = 'config_table'
        column_def = [
            Column('config_id','INTEGER',allow_null=False),
            Column('channel_name_id','INTEGER',allow_null=False),
            Column('channel_group_name_id','INTEGER',allow_null=False),
            Column('weight','REAL',allow_default=True,default_value=None),
            Column('step_size','REAL',allow_default=True,default_value=None),
            Column('indiv_ramp_table','BLOB',allow_default=True,default_value=None),
            ForeignKeyConstraint('fk_config_id', 'config_id',
                                 'config_meta_table', 'config_id'),        
            ForeignKeyConstraint('fk_channel_name_id', 'channel_name_id',
                                 'channel_name_table', 'channel_name_id'),        
            ForeignKeyConstraint('fk_channel_group_name_id', 'channel_group_name_id',
                                 'channel_group_name_table', 'channel_group_name_id'),                
        ]
        db.createTable(table_name, column_def)    
        
        table_name = 'snapshot_meta_table'
        column_def = [
            Column('snapshot_id','INTEGER PRIMARY KEY'),
            Column('config_id','INTEGER',allow_null=False),
            Column('snapshot_name','TEXT',allow_default=True,default_value='""'),
            Column('user_id','INTEGER',allow_null=False),
            Column('user_record_id','INTEGER',allow_null=False),
            Column('time_snapshot_taken','REAL',allow_null=False),        
            Column('description','TEXT',allow_default=True,default_value='""'),
            Column('appended_descriptions','TEXT',allow_default=True,default_value='""'), # include modified time as part of the text in this
            Column('masar_event_id','INTEGER',allow_default=True,default_value=None),
            ForeignKeyConstraint('fk_config_id', 'config_id',
                                 'config_meta_table', 'config_id'),        
            ForeignKeyConstraint('fk_user_id', 'user_id',
                                 'user_table', 'user_id'),        
        ]
        db.createTable(table_name, column_def)    
        
        table_name = 'snapshot_table'
        column_def = [
            Column('snapshot_id','INTEGER',allow_null=False),
            Column('channel_id','INTEGER',allow_null=False),
            Column('pvrb_value','REAL',allow_default=True,default_value=None),
            Column('pvrb_ioc_timestamp','INTEGER',allow_default=True,default_value=None),
            Column('pvrb_pc_timestamp','REAL',allow_default=True,default_value=None),
            Column('pvsp_value','REAL',allow_default=True,default_value=None),
            Column('pvsp_ioc_timestamp','INTEGER',allow_default=True,default_value=None),
            Column('pvsp_pc_timestamp','REAL',allow_default=True,default_value=None),
            ForeignKeyConstraint('fk_snapshot_id', 'snapshot_id',
                                 'snapshot_meta_table', 'snapshot_id'),        
            ForeignKeyConstraint('fk_channel_id', 'channel_id',
                                 'channel_table', 'channel_id'),        
        ]
        '''Note that the 2nd column is 'channel_id', NOT 'channel_name_id' as in config_table.
        This is because channel_name_id may point to different PV's at some later time,
        but channel_id will always point to the same PV's, which may or may not
        exist later.
        '''
        db.createTable(table_name, column_def)    
        
        print 'Successfully initialized database tables for aplattuner.'        
        
    #----------------------------------------------------------------------
    def updateClientDB(self):
        """"""
        
    #----------------------------------------------------------------------
    def loadClientHDF5(self):
        """"""

#----------------------------------------------------------------------
def test1(args):
    """"""
    
    global DEBUG
    DEBUG = False
    
    db = TunerDatabase()
    
    db.getTableNames()
    
    try:
        table_name = 'channelNames'
        column_def = [
            Column('channel_name_id','INTEGER PRIMARY KEY'),
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
            Column('channel_id','INTEGER PRIMARY KEY'),
            Column('channel_name_id','INT',allow_null=False),
            Column('pvrb_name','TEXT',allow_default=True,default_value=None),
            Column('pvsp_name','TEXT',allow_default=True,default_value=None),
            Column('time_created','REAL',allow_null=False),
            ForeignKeyConstraint('fk_channel_name_id', 'channel_name_id',
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
            Column('channel_group_id','INTEGER PRIMARY KEY'),
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
            Column('channel_order_in_group','INTEGER PRIMARY KEY'),
            Column('channel_group_id','INT',allow_null=False),
            Column('channel_name_id','INT',allow_null=False),
            ForeignKeyConstraint('fk_channel_group_id', 'channel_group_id',
                                 'channelGroupsMeta', 'channel_group_id'),            
            ForeignKeyConstraint('fk_channel_name_id', 'channel_name_id',
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
            Column('config_id','INTEGER PRIMARY KEY'),
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
            Column('group_order_in_config','INTEGER PRIMARY KEY'),
            Column('config_id','INT',allow_null=False),
            Column('channel_group_id','INT',allow_null=False),
            Column('weight','REAL',allow_null=False),
            ForeignKeyConstraint('fk_config_id', 'config_id',
                                 'configsMeta', 'config_id'),            
            ForeignKeyConstraint('fk_channel_group_id', 'channel_group_id',
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
            condition_str='channel_group_id=?', placeholder_replacement_tuple=(channel_group_id,)) 
        channel_group_name = channel_group_name[0]
        
        channel_name_ids, = db.getColumnDataFromTable(
            'channelGroups',column_name_list=['channel_name_id'],
            condition_str='channel_group_id=?', placeholder_replacement_tuple=(channel_group_id,))         
        #print 'channel_name_ids', channel_name_ids
        
        latest_channel_ids = []
        latest_pvrb_names = []
        latest_pvsp_names = []
        latest_times_created = []
        channel_names = []
        for channel_name_id in channel_name_ids:
            channel_name, = db.getColumnDataFromTable(
                'channelNames',column_name_list=['channel_name'],
                condition_str='channel_name_id=?', placeholder_replacement_tuple=(channel_name_id,))
            channel_names.append(channel_name[0])

            channel_ids, pvrb_names, pvsp_names, times_created = db.getColumnDataFromTable(
                'channels',column_name_list=['channel_id', 'pvrb_name', 'pvsp_name', 'time_created'],
                condition_str='channel_name_id=?', placeholder_replacement_tuple=(channel_name_id,))
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

    db = TunerDatabase()
    db._initTables()

#----------------------------------------------------------------------    
if __name__ == "__main__" :
    #test1(sys.argv)
    main(sys.argv)