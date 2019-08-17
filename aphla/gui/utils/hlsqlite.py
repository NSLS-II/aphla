from __future__ import print_function, division, absolute_import

'''
High-Level Interface to SQLite
'''

import os
import sqlite3 # command-line SQLite3 does NOT need to be installed to use
# this Python module
from time import time, sleep
import zlib
from six.moves import cPickle as pickle
import traceback
from pprint import pprint
from collections import namedtuple

__version__ = '1.0.0'

MEMORY = ':memory:'

DEBUG = False

#----------------------------------------------------------------------
def blobdumps(py_obj, cPickle_protocol=2, compression_level=7):
    """
    Pickle any Python object, and compress the pickled object.

    Returns a binary string.

    `compression_level`: Between 1 and 9
        The higher the level is, the more compressed the object will be.
    """

    return zlib.compress(pickle.dumps(py_obj, cPickle_protocol),
                         compression_level).decode('latin1')

#----------------------------------------------------------------------
def blobloads(blob):
    """
    Inverse of blobdumps().

    Decompress the pickled object, and unpickle the uncompressed object.

    Returns a Python object.
    """

    return pickle.loads(zlib.decompress(blob.encode('latin1')))
    # No need to specify pickle protocol, as it will be automatically
    # determined.

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
                print('Folder', parent_folderpath, 'must exist.')
                print('Or, set "create_folder=True" when instantiating ' +
                      'SQLiteDatabase class to have the folder created automatically.')
                return

        self.cur = self.con.cursor()

    #----------------------------------------------------------------------
    def close(self, vacuum=False):
        """"""

        if vacuum:
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
    def getTableNames(self, square_brackets=True):
        """
        Show all the table names (including temporary ones)

        If a table name contains a whitespace, the table name will be
        enclosed by square brackets if `square_brackets` is True. If False,
        the table name will be enclosed by double quotes (").
        """

        if square_brackets:
            enclosures = ['[', ']']
        else:
            enclosures = ['"', '"']

        self.cur.execute(
            '''SELECT name FROM
                   (SELECT * FROM sqlite_master UNION ALL
                    SELECT * FROM sqlite_temp_master)
               WHERE type="table" ORDER BY name''')
        table_name_list = [tup[0] if len(tup[0].split()) == 1 else
                           '{0}{1}{2}'.format(enclosures[0], tup[0],
                                              enclosures[1])
                           for tup in self.cur.fetchall()]

        if DEBUG:
            print('Existing tables:', table_name_list)

        return table_name_list

    #----------------------------------------------------------------------
    def getViewNames(self, square_brackets=True):
        """
        Show all the view names (including temporary ones)

        If a table name contains a whitespace, the table name will be
        enclosed by square brackets if `square_brackets` is True. If False,
        the table name will be enclosed by double quotes (").
        """

        if square_brackets:
            enclosures = ['[', ']']
        else:
            enclosures = ['"', '"']

        self.cur.execute(
            '''SELECT name FROM
                   (SELECT * FROM sqlite_master UNION ALL
                    SELECT * FROM sqlite_temp_master)
               WHERE type="view" ORDER BY name''')
        view_name_list = [tup[0] if len(tup[0].split()) == 1 else
                          '{0}{1}{2}'.format(enclosures[0], tup[0],
                                             enclosures[1])
                          for tup in self.cur.fetchall()]

        if DEBUG:
            print('Existing tables:', view_name_list)

        return view_name_list

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
        """
        Returns None where there is no row.
        """

        sql_cmd = self.createSelectSQLStatement(table_name,
            column_name_list=['max('+column_name+')'],
            condition_str=condition_str, order_by_str=order_by_str)

        self.cur.execute(sql_cmd)

        z = self.cur.fetchall()

        return z[0][0]

    #----------------------------------------------------------------------
    def getAllColumnDataFromTable(self, table_name):
        """"""

        return self.getColumnDataFromTable(table_name, column_name_list=None,
                                           condition_str='', order_by_str='',
                                           binding_tuple=None,
                                           print_cmd=False)

    #----------------------------------------------------------------------
    def pprintColumnDataFromTable(self, table_name, column_name_list=None,
                                  condition_str='', order_by_str='',
                                  binding_tuple=None,
                                  binding_list_of_tuples=None,
                                  print_cmd=False):
        """"""

        list_of_columns = self.getColumnDataFromTable(
            table_name, column_name_list=column_name_list, condition_str=condition_str,
            order_by_str=order_by_str, binding_tuple=binding_tuple,
            binding_list_of_tuples=binding_list_of_tuples, print_cmd=print_cmd)

        list_of_rows = zip(*list_of_columns)

        if column_name_list is None:
            column_name_list = self.getColumnNames(table_name)

        self.pprinttable(list_of_rows, column_name_list=column_name_list,
                         force_table_view=True)

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
            print(sql_cmd)

        if binding_tuple is not None:
            self.cur.execute(sql_cmd, binding_tuple)
            z = self.cur.fetchall()

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
    def getMatchedColumnDataFromTable(
        self, table_name, matched_column_name, matching_val_list,
        matching_format, column_name_return_list=None):
        """
        """

        if column_name_return_list is None:
            column_name_return_list = self.getColumnNames(table_name)

        col_name_list = [matched_column_name] + column_name_return_list

        comp_val_str_list = ['"{0}"'.format(v if v is not None else '')
                             if matching_format.endswith('s')
                             else ('{0'+matching_format+'}').format(v)
                             for v in matching_val_list]

        unique_out = self.getColumnDataFromTable(
            table_name, column_name_list=col_name_list,
            condition_str='{0} IN ({1})'.format(
                matched_column_name, ','.join(set(comp_val_str_list))))

        if unique_out == []:
            return None

        unique_matched_item_list = list(unique_out[0])

        mapping = [unique_matched_item_list.index(v)
                   if v in unique_matched_item_list else None
                   for v in matching_val_list]

        out = []
        for uo in unique_out[1:]:
            out.append([uo[i] if i is not None else None for i in mapping])

        return out

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
    def createFTS4VirtualTable(self, table_name, column_definition_list,
                               tokenizer_str=''):
        """"""

        self.dropTable(table_name)

        sql_cmd = 'CREATE VIRTUAL TABLE ' + table_name + ' using fts4 ('

        for col in column_definition_list:
            if isinstance(col, Column):
                sql_cmd += col.name
            else:
                raise ValueError('Unexpected column class: '+type(col))

            sql_cmd += ', '

        if tokenizer_str:
            sql_cmd += 'tokenize={0:s})'.format(tokenizer_str)
        else:
            sql_cmd = sql_cmd[:-2] + ')'

        try:
            if DEBUG:
                print(sql_cmd)

            with self.con:
                self.cur.execute(sql_cmd)
        except:
            traceback.print_exc()
            print('SQL cmd:', sql_cmd)

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
                print(sql_cmd)

            with self.con:
                self.cur.execute(sql_cmd)
        except:
            traceback.print_exc()
            print('SQL cmd:', sql_cmd)

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

        select_sql_cmd = self.createSelectSQLStatement(
            foreign_database_name + '.' + foreign_table_name,
            column_name_list=foreign_column_name_list,
            condition_str=condition_str, order_by_str=order_by_str
        )

        sql_cmd = ('INSERT INTO ' + table_name + local_column_name_str + ' ' +
                   select_sql_cmd)

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

        with self.con:
            self.cur.executemany(sql_cmd, list_of_tuples)

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

    #----------------------------------------------------------------------
    def lockDatabase(self):
        """"""

        self.cur.execute('PRAGMA locking_mode = EXCLUSIVE')
        self.cur.execute('BEGIN EXCLUSIVE')
        self.con.commit()

    #----------------------------------------------------------------------
    def unlockDatabase(self):
        """"""

        self.cur.execute('PRAGMA locking_mode = NORMAL')
        self.con.commit()

        self.getTableNames()

    #----------------------------------------------------------------------
    @staticmethod
    def pprinttable(list_of_rows, column_name_list=None, force_table_view=True):
        """
        Pretty-printing ASCII tables

        Given a list of rows such as [(1,2), (3,4)] and column name
        list such as ['Index 1', 'Index 2'], this function will print the following:

        Index 1 | Index 2
        --------+--------
              1 |       2
              3 |       4

        Copied from an answer at
        http://stackoverflow.com/questions/5909873/python-pretty-printing-ascii-tables

        with my bug fix and additional optional argument.
        """

        n_rows = len(list_of_rows)
        n_cols = len(list_of_rows[0])

        if column_name_list is None:
            column_name_list = ['Column {0:d}'.format(i+1) for i in range(n_rows)]
        if len(column_name_list) != n_cols:
            raise ValueError('Length of "column_name_list" must agree with the number of columns in "list_of_rows".')

        Row = namedtuple('Row', column_name_list)
        rows = map(Row._make, list_of_rows)

        if (len(rows) > 1) or force_table_view:
            headers = rows[0]._fields
            lens = []
            for i in range(len(rows[0])):
                lens.append(len(str(
                    max([x[i] for x in rows] + [headers[i]],key=lambda x:len(str(x)))
                )))
            formats = []
            hformats = []
            for i in range(len(rows[0])):
                if isinstance(rows[0][i], int):
                    formats.append("%%%dd" % lens[i])
                else:
                    formats.append("%%-%ds" % lens[i])
                hformats.append("%%-%ds" % lens[i])
            pattern = " | ".join(formats)
            hpattern = " | ".join(hformats)
            separator = "-+-".join(['-' * n for n in lens])
            print(hpattern % tuple(headers))
            print(separator)
            for line in rows:
                print(pattern % tuple(line))
        elif len(rows) == 1:
            row = rows[0]
            hwidth = len(max(row._fields,key=lambda x: len(x)))
            for i in range(len(row)):
                print("%*s = %s" % (hwidth,row._fields[i],row[i]))
