'''
High-Level Interface to SQLite
'''

import os
import sqlite3
from time import time, sleep
import traceback
from pprint import pprint

MEMORY = ':memory:'

DEBUG = False

########################################################################
class Column():
    """"""

    #----------------------------------------------------------------------
    def __init__(self, name, data_type, primary_key=False,
                 allow_null=True, unique=False,
                 allow_default=False, default_value=None):
        """Constructor"""

        self.name = name

        data_type = data_type.upper()

        if data_type not in ('TEXT', 'REAL', 'INT', 'INTEGER', 'BLOB'):
            raise ValueError('Unexpected data type: '+data_type)
        else:
            self.data_type = data_type

        if primary_key:
            self.primary_key_str = 'PRIMARY KEY'
        else:
            self.primary_key_str = ''

        self.allow_null = allow_null

        self.unique = unique

        self.allow_default = allow_default

        self.default_value = default_value


########################################################################
class ForeignKeyConstraint():
    """"""

    #----------------------------------------------------------------------
    def __init__(self, database_object, constraint_name, column_name,
                 foreign_table_name, foreign_column_name,
                 on_delete_action='RESTRICT', on_update_action='CASCADE'):
        """Constructor"""

        if not database_object.foreignKeysEnabled():
            database_object.setForeignKeysEnabled(True)

        self.name = constraint_name

        self.column_name = column_name

        # Foreign Key Clause
        self.foreign_table_name = foreign_table_name
        self.foreign_column_name = foreign_column_name
        self.on_delete_action = on_delete_action.upper()
        self.on_update_action = on_update_action.upper()

########################################################################
class PrimaryKeyTableConstraint():
    """"""

    #----------------------------------------------------------------------
    def __init__(self, column_name_list):
        """Constructor"""

        self.column_name_list = column_name_list

########################################################################
class UniqueTableConstraint():
    """"""

    #----------------------------------------------------------------------
    def __init__(self, column_name_list):
        """Constructor"""

        self.column_name_list = column_name_list



########################################################################
class SQLiteDatabase():
    """"""

    #----------------------------------------------------------------------
    def __init__(self, filepath='', create_folder=False):
        """Constructor"""

        self.filepath = os.path.abspath(filepath)

        try:
            self.con = sqlite3.connect(self.filepath)
        except:
            parent_folderpath = os.path.dirname(self.filepath)
            if create_folder:
                os.mkdir(parent_folderpath)
                sleep(1.)
                self.con = sqlite3.connect(self.filepath)
            else:
                print 'Folder', parent_folderpath, 'must exist.'
                print 'Or, set "create_folder=True" when instantiating ' + \
                      'SQLiteDatabase class to have the folder created automatically.'
                return

        self.cur = self.con.cursor()

        # for WingIDE real-time assistance
        isinstance(self.con, sqlite3.Connection)
        isinstance(self.cur, sqlite3.Cursor)

    #----------------------------------------------------------------------
    def close(self):
        """"""

        with self.con:
            self.cur.execute('VACUUM')

        self.con.close()

    #----------------------------------------------------------------------
    def getCurrentEpochTimestampSQLiteFuncStr(self, data_type='float'):
        """
        See getCurrentEpochTimestamp() function below
        """

        if data_type == 'int':
            func_str = "strftime('%s','now')"
        elif data_type == 'float':
            func_str = "(julianday('now') - 2440587.5)*86400.0"
        else:
            raise ValueError('return_type must be "int" or "float".')

        return func_str

    #----------------------------------------------------------------------
    def getCurrentEpochTimestamp(self, program='sqlite', return_type='float'):
        """
        Returns either int or float representing time elapsed since
        01/01/1970 UTC in seconds.

        "program" argument specifies whether to use SQLite built-in timestamp
        methods or Python built-in epoch timestamp method. Depending on platforms,
        these different methods may differ by up to ~1ms, from limited
        personal observations (Y. Hidaka).
        """

        if return_type == 'int':
            isFloat = False
        elif return_type == 'float':
            isFloat = True
        else:
            raise ValueError('return_type must be "int" or "float".')

        if program == 'sqlite':
            if isFloat:
                self.cur.execute("SELECT (julianday('now') - 2440587.5)*86400.0")
                return self.cur.fetchall()[0][0]
            else:
                self.cur.execute("SELECT strftime('%s','now')")
                unicode_int_string = self.cur.fetchall()[0][0]
                return int(unicode_int_string)
        elif program == 'python':
            t = time()
            if isFloat:
                return t
            else:
                return int(t)
        else:
            raise ValueError(
                '"program" argument must be either "sqlite" or "python". ' +
                'Unexpected program: ',str(program))

    #----------------------------------------------------------------------
    def dump(self, dump_filepath):
        """"""

        with open(dump_filepath, 'w') as f:
            for line in self.con.iterdump():
                f.write('{0:s}\n'.format(line))

    #----------------------------------------------------------------------
    def getTableNames(self):
        """"""

        self.cur.execute('SELECT name FROM sqlite_master WHERE type="table" ORDER BY name')
        table_name_list = [tup[0] for tup in self.cur.fetchall()]

        if DEBUG:
            print 'Existing tables:', table_name_list

        return table_name_list

    #----------------------------------------------------------------------
    def getColumnNames(self, table_name):
        """"""

        try:
            table_info_dict_list = self.getTableInfo(table_name)
        except:
            self.createTempView('temp_view', table_name, column_name_list=['*'])
            table_info_dict_list = self.getTableInfo('temp_view')
            self.dropView('temp_view')

        column_name_list = [d['column_name'] for d in table_info_dict_list]
        return column_name_list


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
    def getMaxInColumn(self, table_name, column_name,
                       condition_str='', order_by_str=''):
        """"""

        sql_cmd = self.createSelectSQLStatement(table_name,
            column_name_list=['max('+column_name+')'],
            condition_str=condition_str, order_by_str=order_by_str)

        self.cur.execute(sql_cmd)

        z = self.cur.fetchall()

        return z[0][0]

    #----------------------------------------------------------------------
    def getAllColumnDataFromTable(self, table_name):
        """"""

        #self.cur.execute('SELECT * FROM ' + table_name)

        #all_rows = self.cur.fetchall()

        #return zip(*all_rows)

        return self.getColumnDataFromTable(table_name, column_name_list=None,
                                           condition_str='', order_by_str='',
                                           binding_tuple=None,
                                           print_cmd=False)

    #----------------------------------------------------------------------
    def getColumnDataFromTable(self, table_name, column_name_list=None,
                               condition_str='', order_by_str='',
                               binding_tuple=None,
                               binding_list_of_tuples=None,
                               print_cmd=False):
        """
        Return a list of column data (tuples).

        binding_tuple will be inserted into '?' appearing in the SQL command

        """

        sql_cmd = self.createSelectSQLStatement(table_name, column_name_list,
                                                condition_str, order_by_str)
        if print_cmd:
            print sql_cmd

        if binding_tuple is not None:
            self.cur.execute(sql_cmd, binding_tuple)
            z = self.cur.fetchall()
            #z = []
            #for row in self.cur:
                #z.append(row)

        elif binding_list_of_tuples is not None:
            zall = []
            for binding_tuple in binding_list_of_tuples:
                self.cur.execute(sql_cmd, binding_tuple)
                z = self.cur.fetchall()
                zall.extend(z)

            z = zall

        else:
            self.cur.execute(sql_cmd)
            z = self.cur.fetchall()

        return zip(*z)

    #----------------------------------------------------------------------
    def createTempView(self, view_name, table_name, column_name_list=None,
                       condition_str='', order_by_str='',
                       binding_tuple=None):
        """"""

        select_sql = self.createSelectSQLStatement(table_name, column_name_list,
                                                   condition_str, order_by_str)

        sql_cmd = 'CREATE TEMP VIEW ' + view_name + ' AS ' + select_sql

        if binding_tuple is None:
            self.cur.execute(sql_cmd)
        else:
            self.cur.execute(sql_cmd, binding_tuple)

    #----------------------------------------------------------------------
    def createTable(self, table_name, column_definition_list):
        """"""

        self.dropTable(table_name)

        sql_cmd = 'CREATE TABLE ' + table_name + ' ('

        for col in column_definition_list:

            if isinstance(col, Column):
                if (col.primary_key_str == 'PRIMARY KEY') and \
                   (col.data_type == 'INT'):
                    col.data_type = 'INTEGER'
                L = [col.name, col.data_type, col.primary_key_str]

                if col.primary_key_str == '':
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

                sql_cmd += ' '.join(L)

            elif isinstance(col, ForeignKeyConstraint):
                sql_cmd += ('CONSTRAINT ' + col.name +
                            ' FOREIGN KEY(' + col.column_name + ') ' +
                            'REFERENCES ' + col.foreign_table_name +
                            '(' + col.foreign_column_name + ') ' +
                            'ON DELETE ' + col.on_delete_action + ' ' +
                            'ON UPDATE ' + col.on_update_action
                            )

            elif isinstance(col, PrimaryKeyTableConstraint):
                sql_cmd += 'PRIMARY KEY ' + \
                    '(' + ','.join(col.column_name_list) + ')'

            elif isinstance(col, UniqueTableConstraint):
                sql_cmd += 'UNIQUE ' + \
                    '(' + ','.join(col.column_name_list) + ')'

            else:
                raise ValueError('Unexpected column class: '+type(col))

            sql_cmd += ', '

        sql_cmd = sql_cmd[:-2] + ')'

        try:
            if DEBUG:
                print sql_cmd

            with self.con:
                self.cur.execute(sql_cmd)
        except:
            traceback.print_exc()
            print 'SQL cmd:', sql_cmd

    #----------------------------------------------------------------------
    def dropAllTables(self):
        """"""

        table_name_list = self.getTableNames()
        for table_name in table_name_list:
            self.dropTable(table_name)

    #----------------------------------------------------------------------
    def dropTable(self, table_name):
        """"""

        with self.con:
            self.cur.execute('DROP TABLE IF EXISTS '+table_name)

    #----------------------------------------------------------------------
    def dropView(self, view_name):
        """"""

        with self.con:
            self.cur.execute('DROP VIEW IF EXISTS '+view_name)


    #----------------------------------------------------------------------
    def insertTable(self, table_name, foreign_database_name, foreign_table_name,
                    local_column_name_list=None, foreign_column_name_list=None,
                    condition_str='', order_by_str='',
                    binding_tuple=None):
        """"""

        if local_column_name_list is None:
            local_column_name_str = ''
        else:
            local_column_name_str = '(' + ','.join(local_column_name_list) + ')'

        #if foreign_column_name_list is None:
            #foreign_column_name_list = ['*']
        #foreign_column_name_str = ','.join(foreign_column_name_list)

        select_sql_cmd = self.createSelectSQLStatement(
            foreign_database_name + '.' + foreign_table_name,
            column_name_list=foreign_column_name_list,
            condition_str=condition_str, order_by_str=order_by_str
        )

        sql_cmd = 'INSERT INTO ' + table_name + local_column_name_str + ' ' + select_sql_cmd
        #sql_cmd = 'INSERT INTO ' + table_name + local_column_name_str + \
            #' SELECT ' + foreign_column_name_str + ' FROM ' + \
            #foreign_database_name + '.' + foreign_table_name

        if binding_tuple is None:
            self.cur.execute(sql_cmd)
        else:
            self.cur.execute(sql_cmd, binding_tuple)
        self.con.commit()

    #----------------------------------------------------------------------
    def insertRows(self, table_name, list_of_tuples, on_conflict=None,
                   bind_replacement_list_of_tuples=None):
        """
        The argument "bind_replacement_list_of_tuples" is used to replace
        "?" in "bind_list" with a SQLite function.

        This is useful if a column contains timestamps for row insertion.
        In this case, instead of providing a timestamp value to database,
        you can have the database automatically timestamp row insertion,
        by replacing "?" with a SQLite function string such as
        "strftime('%s','now')".

        To specify this replacement, you must specify a tuple whose first
        element is the index of "?" in "bind_list" and whose second element
        is a valid SQLite expression string. For example, if you have a
        bind list ['?', '?', '?'], and want to have the 2nd '?' replaced with
        "strtime('%s','now')", then
           bind_replacement_list_of_tuples = [(1,"strtime('%s','now')"),]
        """

        if on_conflict is None:
            sql_cmd = 'INSERT INTO ' + table_name + ' VALUES '
        else:
            sql_cmd = 'INSERT OR ' + on_conflict + ' INTO ' + table_name + ' VALUES '

        bind_list = ['?' if not info_dict['primary_key'] else 'null'
                     for info_dict in self.getTableInfo(table_name)]

        if isinstance(bind_replacement_list_of_tuples,list) or \
           isinstance(bind_replacement_list_of_tuples,tuple):
            for tup in bind_replacement_list_of_tuples:
                bind_list[tup[0]] = tup[1]

        placeholder_str = '(' + ', '.join(bind_list) + ')'

        sql_cmd += placeholder_str

        try:
            with self.con:
                self.cur.executemany(sql_cmd, list_of_tuples)
        except sqlite3.IntegrityError as e:
            raise e
        except:
            traceback.print_exc()

    #----------------------------------------------------------------------
    def deleteRows(self, table_name, condition_str='',
                   binding_tuple=None):
        """"""

        sql_cmd = 'DELETE FROM ' + table_name

        if condition_str != '':
            sql_cmd += ' WHERE ' + condition_str

        if binding_tuple is None:
            self.cur.execute(sql_cmd)
        else:
            self.cur.execute(sql_cmd, binding_tuple)

        self.con.commit()

    #----------------------------------------------------------------------
    def attachDatabase(self, filepath, database_name):
        """"""

        sql_cmd = 'ATTACH DATABASE ' + '"' + filepath + '"' + ' AS ' + database_name
        self.cur.execute(sql_cmd)
        self.con.commit()

    #----------------------------------------------------------------------
    def detachDatabase(self, database_name):
        """"""

        sql_cmd = 'DETACH DATABASE ' + database_name
        self.cur.execute(sql_cmd)
        self.con.commit()

    #----------------------------------------------------------------------
    def changeValues(self, table_name, column_name, expression,
                     condition_str='', binding_tuple=None):
        """"""

        sql_cmd = 'UPDATE ' + table_name + ' SET ' +  column_name + \
            ' = ' + str(expression)

        if condition_str != '':
            sql_cmd += ' WHERE ' + condition_str

        if binding_tuple is None:
            self.cur.execute(sql_cmd)
        else:
            self.cur.execute(sql_cmd, binding_tuple)

        self.con.commit()

    #----------------------------------------------------------------------
    def foreignKeysEnabled(self):
        """"""

        self.cur.execute('PRAGMA foreign_keys')
        result = self.cur.fetchall()

        if result[0][0] == 0:
            return False
        else:
            return True


    #----------------------------------------------------------------------
    def setForeignKeysEnabled(self, TF):
        """"""

        if TF:
            state = 'ON'
        else:
            state = 'OFF'

        self.cur.execute('PRAGMA foreign_keys = '+state)
        self.con.commit()
