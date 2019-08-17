from __future__ import print_function, division, absolute_import

import sys, os
import os.path as osp
import stat
import numpy as np
from time import time, strftime, localtime, sleep
import h5py
h5zip = 'gzip'
import sqlite3

from PyQt4.QtCore import (SIGNAL, Qt)
from PyQt4.QtGui import (qApp, QMessageBox)

from cothread import catools

import aphla as ap
from aphla.gui.utils.hlsqlite import (
    MEMORY, SQLiteDatabase, Column, ForeignKeyConstraint,
    PrimaryKeyTableConstraint, UniqueTableConstraint, blobdumps, blobloads)
import config
try:
    from . import (date_month_folder_str, date_snapshot_filename_str)
except:
    from aphla.gui.TinkerUtils import (date_month_folder_str,
                                       date_snapshot_filename_str)

DEBUG_ConfigDatabase = True

UNITCONV_DATA_PRECISION = '.16e'
LENGTH_METER_PRECISION = 9
LENGTH_METER_FORMAT = '{{0:.{0:d}f}}'.format(LENGTH_METER_PRECISION)

ELEM_KEYS = ['elem_name', 'elem_family', 'elem_cell', 'elem_devname',
             'elem_efflen', 'elem_physlen', 'elem_fields', 'elem_girder',
             'elem_group', 'elem_sb', 'elem_se', 'elem_sequence',
             'elem_symmetry', 'elem_pvs']
ELEM_ATTRS = ['name', 'family', 'cell', 'devname',
              'length', 'phylen', 'fields', 'girder',
              'group', 'sb', 'se', 'sequence',
              'symmetry', 'pv']

unitsys_id_raw     = 1
pv_id_NonSpecified = 1

CA_DATATYPES = ['string', 'short', 'float', 'enum', 'char', 'long', 'double',
                'no access', ''] # Empty string for cainfo failure
CA_DATATYPES_TINKERABLE = ['short', 'float', 'enum', 'long', 'double']

########################################################################
class TinkerMainDatabase(SQLiteDatabase):
    """"""

    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""

        SQLiteDatabase.__init__(self, filepath=config.MAIN_DB_FILEPATH,
                                create_folder=False)

        if self.getTableNames() == []:
            filepath = self.filepath
            self.close(vacuum=False)
            st = os.stat(filepath)
            # Add write permission to group
            os.chmod(filepath, st.st_mode | stat.S_IWGRP)
            SQLiteDatabase.__init__(self, filepath=filepath,
                                    create_folder=False)
            print('aptinker Main database file not found.')
            print('Creating and initializing the Main database...')
            self._initTables()
            print('Done')

    #----------------------------------------------------------------------
    def _initTables(self):
        """"""

        self.setForeignKeysEnabled(False)

        self.dropAllTables()

        self.setForeignKeysEnabled(True)

        self._initChannelTables()
        self._initConfigTables()
        self._initSnapshotTables()

    #----------------------------------------------------------------------
    def _initChannelTables(self):
        """"""

        table_name = 'machine_name_table'
        column_def = [
            Column('machine_name_id', 'INTEGER', primary_key=True),
            Column('machine_name', 'TEXT', allow_null=False, unique=True),
        ]
        self.createTable(table_name, column_def)
        #self.insertRows(table_name, [(m,) for m in ap.machines.machines()])
        self.insertRows(table_name, [(config.HLA_MACHINE,)])

        table_name = 'lattice_name_table'
        column_def = [
            Column('lattice_name_id', 'INTEGER', primary_key=True),
            Column('lattice_name', 'TEXT', allow_null=False, unique=True),
        ]
        self.createTable(table_name, column_def)
        all_lattice_names = []
        #for m in ap.machines.machines():
            #try:
                #ap.machines.load(m)
                #all_lattice_names.extend(ap.machines.lattices())
            #except:
                #pass
        ap.machines.load(config.HLA_MACHINE)
        all_lattice_names.extend(ap.machines.lattices())
        all_lattice_names = list(set(all_lattice_names))
        self.insertRows(table_name, [(n,) for n in all_lattice_names])

        all_elems = []
        all_elem_tuples = []
        machine = config.HLA_MACHINE
        for lat in ap.machines.lattices():
            ap.machines.use(lat)
            all_elems.extend(ap.getElements('*'))
            all_elem_tuples.extend([(machine, lat, e) for e in ap.getElements('*')])
        all_elem_names = list(set(e.name if e.name is not None else ''
                                  for e in all_elems))
        all_elem_families = list(set(e.family if e.family is not None else ''
                                     for e in all_elems))
        all_elem_cells = list(set(e.cell if e.cell is not None else ''
                                  for e in all_elems))
        all_elem_fields = list(set(e.fields().__repr__()
                                   if e.fields() is not None else ''
                                   for e in all_elems))
        all_fields_flat = list(set(sum([e.fields() for e in all_elems], [])))
        all_elem_devnames = list(set(e.devname if e.devname is not None else ''
                                     for e in all_elems))
        all_elem_efflens = list(set(LENGTH_METER_FORMAT.format(e.length)
                                    if e.length is not None else ''
                                    for e in all_elems))
        all_elem_physlens = list(set(LENGTH_METER_FORMAT.format(e.phylen)
                                     if e.phylen is not None else ''
                                     for e in all_elems))
        all_elem_girders = list(set(e.girder if e.girder is not None else ''
                                    for e in all_elems))
        all_elem_groups = list(set(e.group.__repr__() if e.group is not None
                                   else '' for e in all_elems))
        all_elem_sbs = list(set(LENGTH_METER_FORMAT.format(e.sb)
                                if e.sb is not None else '' for e in all_elems))
        all_elem_ses = list(set(LENGTH_METER_FORMAT.format(e.se)
                                if e.se is not None else '' for e in all_elems))
        all_elem_sequences = list(set(e.sequence.__repr__()
                                      if e.sequence is not None else ''
                                      for e in all_elems))
        all_elem_symmetries = list(set(e.symmetry.__repr__()
                                       if e.symmetry is not None else ''
                                       for e in all_elems))
        all_elem_pvs = list(set(e.pv().__repr__() if e.pv() is not None
                                else '' for e in all_elems))
        all_unitsystems = list(set(
            sum([sum(e.getUnitSystems().values(), []) for e in all_elems], [])))

        all_unitsymbs = []
        all_pvsps = []
        all_pvrbs = []
        for e in all_elems:
            for f in e.fields():
                all_pvsps.append(e.pv(field=f, handle='setpoint'))
                all_pvrbs.append(e.pv(field=f, handle='readback'))
                for unitsys in all_unitsystems:
                #for unitsys in [None, 'phy']:
                    all_unitsymbs.append(e.getUnit(f, unitsys=unitsys))
        all_unitsymbs = list(set(all_unitsymbs))
        if None in all_unitsymbs:
            all_unitsymbs.remove(None)
            if '' not in all_unitsymbs:
                all_unitsymbs.append('')
        all_pvsps = list(set(sum(all_pvsps, [])))
        all_pvrbs = list(set(sum(all_pvrbs, [])))
        cainfos = catools.connect(all_pvsps+all_pvrbs, cainfo=True, throw=False)
        all_pv_data_type_ids = [ci.datatype+1 if ci.ok else len(CA_DATATYPES)
                                for ci in cainfos]
        all_pv_array_sizes = [ci.count if ci.ok else 0 for ci in cainfos]
        all_pvs = [(pv, False, array_size, data_type_id)
                   for (pv, array_size, data_type_id) in
                   zip(all_pvsps, all_pv_array_sizes[:len(all_pvsps)],
                       all_pv_data_type_ids[:len(all_pvsps)])] + \
                  [(pv, True, array_size, data_type_id)
                   for (pv, array_size, data_type_id) in
                   zip(all_pvrbs, all_pv_array_sizes[len(all_pvsps):],
                       all_pv_data_type_ids[len(all_pvsps):], )]
        # ^ 2nd element := Read-only
        all_pvs = list(set(all_pvs)) # Remove duplicates

        table_name = 'elem_name_table'
        column_def = [
            Column('elem_name_id', 'INTEGER', primary_key=True),
            Column('elem_name', 'TEXT', allow_null=False, unique=True),
        ]
        self.createTable(table_name, column_def)
        self.insertRows(table_name, [(n,) for n in all_elem_names])

        table_name = 'elem_family_table'
        column_def = [
            Column('elem_family_id', 'INTEGER', primary_key=True),
            Column('elem_family', 'TEXT', allow_null=False, unique=True),
        ]
        self.createTable(table_name, column_def)
        self.insertRows(table_name, [(n,) for n in all_elem_families])

        table_name = 'elem_cell_table'
        column_def = [
            Column('elem_cell_id', 'INTEGER', primary_key=True),
            Column('elem_cell', 'TEXT', allow_null=False, unique=True),
        ]
        self.createTable(table_name, column_def)
        self.insertRows(table_name, [(n,) for n in all_elem_cells])

        table_name = 'elem_fields_table'
        column_def = [
            Column('elem_fields_id', 'INTEGER', primary_key=True),
            Column('elem_fields', 'TEXT', allow_null=False, unique=True),
        ]
        self.createTable(table_name, column_def)
        self.insertRows(table_name, [(n,) for n in all_elem_fields])

        table_name = 'field_table'
        column_def = [
            Column('field_id', 'INTEGER', primary_key=True),
            Column('field', 'TEXT', allow_null=False, unique=True),
        ]
        self.createTable(table_name, column_def)
        self.insertRows(table_name, [(n,) for n in all_fields_flat])

        table_name = 'elem_devname_table'
        column_def = [
            Column('elem_devname_id', 'INTEGER', primary_key=True),
            Column('elem_devname', 'TEXT', allow_null=False, unique=True),
        ]
        self.createTable(table_name, column_def)
        self.insertRows(table_name, [(n,) for n in all_elem_devnames])

        table_name = 'elem_efflen_table'
        column_def = [
            Column('elem_efflen_id', 'INTEGER', primary_key=True),
            Column('elem_efflen', 'TEXT', allow_null=False, unique=True),
        ]
        self.createTable(table_name, column_def)
        self.insertRows(table_name, [(n,) for n in all_elem_efflens])

        table_name = 'elem_physlen_table'
        column_def = [
            Column('elem_physlen_id', 'INTEGER', primary_key=True),
            Column('elem_physlen', 'TEXT', allow_null=False, unique=True),
        ]
        self.createTable(table_name, column_def)
        self.insertRows(table_name, [(n,) for n in all_elem_physlens])

        table_name = 'elem_girder_table'
        column_def = [
            Column('elem_girder_id', 'INTEGER', primary_key=True),
            Column('elem_girder', 'TEXT', allow_null=False, unique=True),
        ]
        self.createTable(table_name, column_def)
        self.insertRows(table_name, [(n,) for n in all_elem_girders])

        table_name = 'elem_group_table'
        column_def = [
            Column('elem_group_id', 'INTEGER', primary_key=True),
            Column('elem_group', 'TEXT', allow_null=False, unique=True),
        ]
        self.createTable(table_name, column_def)
        self.insertRows(table_name, [(n,) for n in all_elem_groups])

        table_name = 'elem_sb_table'
        column_def = [
            Column('elem_sb_id', 'INTEGER', primary_key=True),
            Column('elem_sb', 'REAL', allow_null=False, unique=True),
        ]
        self.createTable(table_name, column_def)
        self.insertRows(table_name, [(n,) for n in all_elem_sbs])

        table_name = 'elem_se_table'
        column_def = [
            Column('elem_se_id', 'INTEGER', primary_key=True),
            Column('elem_se', 'REAL', allow_null=False, unique=True),
        ]
        self.createTable(table_name, column_def)
        self.insertRows(table_name, [(n,) for n in all_elem_ses])

        table_name = 'elem_sequence_table'
        column_def = [
            Column('elem_sequence_id', 'INTEGER', primary_key=True),
            Column('elem_sequence', 'TEXT', allow_null=False, unique=True),
        ]
        self.createTable(table_name, column_def)
        self.insertRows(table_name, [(n,) for n in all_elem_sequences])

        table_name = 'elem_symmetry_table'
        column_def = [
            Column('elem_symmetry_id', 'INTEGER', primary_key=True),
            Column('elem_symmetry', 'TEXT', allow_null=False, unique=True),
        ]
        self.createTable(table_name, column_def)
        self.insertRows(table_name, [(n,) for n in all_elem_symmetries])

        table_name = 'elem_pvs_table'
        column_def = [
            Column('elem_pvs_id', 'INTEGER', primary_key=True),
            Column('elem_pvs', 'TEXT', allow_null=False, unique=True),
        ]
        self.createTable(table_name, column_def)
        self.insertRows(table_name, [(n,) for n in all_elem_pvs])

        table_name = 'unitsys_table'
        column_def = [
            Column('unitsys_id', 'INTEGER', primary_key=True),
            Column('unitsys', 'TEXT', allow_null=False, unique=True),
        ]
        self.createTable(table_name, column_def)
        self.insertRows(table_name, [('',), ('phy',)])

        table_name = 'unitsymb_table'
        column_def = [
            Column('unitsymb_id', 'INTEGER', primary_key=True),
            Column('unitsymb', 'TEXT', allow_null=False, unique=True),
        ]
        self.createTable(table_name, column_def)
        self.insertRows(table_name, [(s,) for s in all_unitsymbs])

        table_name = 'pv_data_type_table'
        column_def = [
            Column('pv_data_type_id', 'INTEGER', primary_key=True),
            Column('pv_data_type', 'TEXT', allow_null=False, unique=True)
        ]
        self.createTable(table_name, column_def)
        list_of_tuples = [(data_type,) for data_type in CA_DATATYPES]
        self.insertRows(table_name, list_of_tuples)

        table_name = 'pv_table'
        column_def = [
            Column('pv_id', 'INTEGER', primary_key=True),
            Column('pv', 'TEXT', allow_null=False),
            # ^ Virtual PV names start with '@'
            Column('readonly', 'INTEGER', allow_null=False),
            # ^ 1: read-only PV, 0: writeable PV, -1: no PV
            Column('array_size', 'INTEGER', allow_null=False),
            # ^ 1: scalar, > 1: array, null: cainfo failure
            Column('pv_data_type_id', 'INTEGER', allow_null=False),
            ForeignKeyConstraint(self,
                                 'fk_pv_data_type_id', 'pv_data_type_id',
                                 'pv_data_type_table', 'pv_data_type_id'),
        ]
        self.createTable(table_name, column_def)
        list_of_tuples = [('', -1, 0, len(CA_DATATYPES))]
        list_of_tuples += [
            (p, readonly, array_size, data_type_id)
            for (p, readonly, array_size, data_type_id) in all_pvs]
        self.insertRows(table_name, list_of_tuples)

        table_name = 'virt_pv_table'
        column_def = [
            Column('virt_pv_id', 'INTEGER', primary_key=True),
            Column('pv_id', 'INTEGER', allow_null=False),
            Column('func_def', 'TEXT', allow_null=False),
            Column('read', 'INTEGER', allow_null=False), # 1: read, 0: write
            Column('pv_id_to_write', 'INTEGER', allow_null=True),
            Column('aphla_ch_id_to_write', 'INTEGER', allow_null=True),
            # Either one of "pv_id_to_write" and "aphla_ch_id_to_write"
            # is required to be non-null if "read" = 0.
            Column('user_id', 'INTEGER', allow_null=False),
            Column('virt_pv_ctime', 'REAL', allow_null=False),
            ForeignKeyConstraint(self,
                                 'fk_pv_id', 'pv_id',
                                 'pv_table', 'pv_id'),
            ForeignKeyConstraint(self,
                                 'fk_pv_id_to_write', 'pv_id_to_write',
                                 'pv_table', 'pv_id'),
            ForeignKeyConstraint(self,
                                 'fk_aphla_ch_id_to_write', 'aphla_ch_id_to_write',
                                 'aphla_channel_table', 'aphla_ch_id'),
            ForeignKeyConstraint(self,
                                 'fk_user_id', 'user_id',
                                 'user_table', 'user_id'),
        ]
        self.createTable(table_name, column_def)

        table_name = 'virt_pv_input_pv_list_table'
        column_def = [
            Column('virt_pv_id', 'INTEGER', allow_null=False),
            Column('pv_id', 'INTEGER', allow_null=False),
            ForeignKeyConstraint(self,
                                 'fk_virt_pv_id', 'virt_pv_id',
                                 'virt_pv_table', 'virt_pv_id'),
            ForeignKeyConstraint(self,
                                 'fk_pv_id', 'pv_id',
                                 'pv_table', 'pv_id'),
        ]
        self.createTable(table_name, column_def)

        table_name = 'virt_pv_input_aphla_ch_list_table'
        column_def = [
            Column('virt_pv_id', 'INTEGER', allow_null=False),
            Column('aphla_ch_id', 'INTEGER', allow_null=False),
            ForeignKeyConstraint(self,
                                 'fk_virt_pv_id', 'virt_pv_id',
                                 'virt_pv_table', 'virt_pv_id'),
            ForeignKeyConstraint(self,
                                 'fk_aphla_ch_id', 'aphla_ch_id',
                                 'aphla_channel_table', 'aphla_ch_id'),
        ]
        self.createTable(table_name, column_def)

        unitconv_types = ['NoConversion', 'poly', 'interp1']
        table_name = 'unitconv_type_table'
        column_def = [
            Column('unitconv_type_id', 'INTEGER', primary_key=True),
            Column('unitconv_type', 'TEXT', allow_null=False, unique=True),
        ]
        self.createTable(table_name, column_def)
        self.insertRows(table_name, [(t,) for t in unitconv_types])

        unitconv_list  = []
        conv_data_list = []
        for e in all_elems:
            d = e.getUnitSystems()
            for f, unitsys in d.items():
                if len(unitsys) == 1:
                    inv = 0
                    polarity = +1
                    if unitsys[0] is not None:
                        raise ValueError('When there is only 1 unit system, it should be None.')
                    unitconv_type = 'NoConversion'
                    src_unitsys   = None
                    dst_unitsys   = None
                    src_unitsymb  = dst_unitsymb = e.getUnit(f, unitsys=None)
                    conv_data     = None

                    if src_unitsys is None: src_unitsys = ''
                    if dst_unitsys is None: dst_unitsys = ''
                    if src_unitsymb is None: src_unitsymb = ''
                    if dst_unitsymb is None: dst_unitsymb = ''
                    unitconv_list.append(
                        (unitconv_type, src_unitsys, dst_unitsys, src_unitsymb,
                         dst_unitsymb, inv, polarity, conv_data))
                    conv_data_list.append(conv_data)

                else:
                    for k, v in e._field[f].unitconv.items():
                        inv = 0
                        src_unitsys, dst_unitsys = k
                        src_unitsymb = e.getUnit(f, unitsys=src_unitsys)
                        dst_unitsymb = e.getUnit(f, unitsys=dst_unitsys)
                        if isinstance(v, ap.unitconv.UcPoly):
                            unitconv_type = 'poly'
                            polarity = int(v.polarity)
                            conv_data = tuple(v.p.coeffs)
                        elif isinstance(v, ap.unitconv.UcInterp1):
                            unitconv_type = 'interp1'
                            polarity = int(v.polarity)
                            conv_data = tuple([tuple(v.xp), tuple(v.fp)])
                        else:
                            raise ValueError('Unexpected unitconv type: {0:s}'.
                                             format(v.__repr__()))

                        if src_unitsys is None: src_unitsys = ''
                        if dst_unitsys is None: dst_unitsys = ''
                        if src_unitsymb is None: src_unitsymb = ''
                        if dst_unitsymb is None: dst_unitsymb = ''
                        unitconv_list.append(
                            (unitconv_type, src_unitsys, dst_unitsys,
                             src_unitsymb, dst_unitsymb, inv, polarity,
                             conv_data))
                        conv_data_list.append(conv_data)

                        if hasattr(v, 'invertible') and v.invertible:
                            inv = 1
                            src_unitsys, dst_unitsys = dst_unitsys, src_unitsys
                            src_unitsymb, dst_unitsymb = dst_unitsymb, src_unitsymb

                            unitconv_list.append(
                                (unitconv_type, src_unitsys, dst_unitsys,
                                 src_unitsymb, dst_unitsymb, inv, polarity,
                                 conv_data))

        conv_data_list_of_tuples = [
            (blobdumps(data),) for data in set(conv_data_list)]
        table_name = 'unitconv_blob_table'
        column_def = [
            Column('unitconv_blob_id', 'INTEGER', primary_key=True),
            Column('unitconv_blob', 'BLOB', allow_null=False),
        ]
        self.createTable(table_name, column_def)
        self.insertRows(table_name, conv_data_list_of_tuples)

        unitconv_list = list(set(unitconv_list))
        unitconv_list_of_tuples = []
        for unitconv_type, src_unitsys, dst_unitsys, src_unitsymb, \
            dst_unitsymb, inv, polarity, conv_data in unitconv_list:
            unitconv_type_id = self.getMatchingPrimaryKeyIdFrom2ColTable(
                'unitconv_type_table', 'unitconv_type_id', 'unitconv_type',
                unitconv_type, append_new=True)
            src_unitsys_id = self.getMatchingPrimaryKeyIdFrom2ColTable(
                'unitsys_table', 'unitsys_id', 'unitsys', src_unitsys,
                append_new=True)
            dst_unitsys_id = self.getMatchingPrimaryKeyIdFrom2ColTable(
                'unitsys_table', 'unitsys_id', 'unitsys', dst_unitsys,
                append_new=True)
            src_unitsymb_id = self.getMatchingPrimaryKeyIdFrom2ColTable(
                'unitsymb_table', 'unitsymb_id', 'unitsymb', src_unitsymb,
                append_new=True)
            dst_unitsymb_id = self.getMatchingPrimaryKeyIdFrom2ColTable(
                'unitsymb_table', 'unitsymb_id', 'unitsymb', dst_unitsymb,
                append_new=True)
            unitconv_blob_id = self.getMatchingPrimaryKeyIdFrom2ColTable(
                'unitconv_blob_table', 'unitconv_blob_id', 'unitconv_blob',
                blobdumps(conv_data), blob=True, append_new=True)
            unitconv_list_of_tuples.append(
                (unitconv_type_id, src_unitsys_id, dst_unitsys_id,
                 src_unitsymb_id, dst_unitsymb_id, inv, polarity,
                 unitconv_blob_id))

        table_name = 'unitconv_table'
        column_def = [
            Column('unitconv_id', 'INTEGER', primary_key=True),
            Column('unitconv_type_id', 'INTEGER', allow_null=False),
            Column('src_unitsys_id', 'INTEGER', allow_null=False),
            Column('dst_unitsys_id', 'INTEGER', allow_null=False),
            Column('src_unitsymb_id', 'INTEGER', allow_null=False),
            Column('dst_unitsymb_id', 'INTEGER', allow_null=False),
            Column('inv', 'INTEGER', allow_null=False),
            Column('polarity', 'INTEGER', allow_null=False), # +1 or -1
            Column('unitconv_blob_id', 'INTEGER', allow_null=False),
            Column('unitconv_ctime', 'REAL', allow_null=False),
            ForeignKeyConstraint(self,
                                 'fk_unitconv_type_id', 'unitconv_type_id',
                                 'unitconv_type_table', 'unitconv_type_id'),
            ForeignKeyConstraint(self,
                                 'fk_src_unitsys_id', 'src_unitsys_id',
                                 'unitsys_table', 'unitsys_id'),
            ForeignKeyConstraint(self,
                                 'fk_dst_unitsys_id', 'dst_unitsys_id',
                                 'unitsys_table', 'unitsys_id'),
            ForeignKeyConstraint(self,
                                 'fk_src_unitsymb_id', 'src_unitsymb_id',
                                 'unitsymb_table', 'unitsymb_id'),
            ForeignKeyConstraint(self,
                                 'fk_dst_unitsymb_id', 'dst_unitsymb_id',
                                 'unitsymb_table', 'unitsymb_id'),
            ForeignKeyConstraint(self,
                                 'fk_unitconv_blob_id', 'unitconv_blob_id',
                                 'unitconv_blob_table', 'unitconv_blob_id'),
        ]
        self.createTable(table_name, column_def)
        self.insertRows(table_name, list_of_tuples=unitconv_list_of_tuples,
                        bind_replacement_list_of_tuples=
                        [(sum([isinstance(c, Column) for c in column_def])-1,
                          self.getCurrentEpochTimestampSQLiteFuncStr(
                              data_type='float'))])

        all_elem_prop_list_of_tuples = []
        for machine, lat, e in all_elem_tuples:
            machine_id = self.getColumnDataFromTable(
                'machine_name_table', column_name_list=['machine_name_id'],
                condition_str='machine_name="{0:s}"'.format(machine))[0][0]
            lat_id = self.getColumnDataFromTable(
                'lattice_name_table', column_name_list=['lattice_name_id'],
                condition_str='lattice_name="{0:s}"'.format(lat))[0][0]
            elem_name_id = self.getColumnDataFromTable(
                'elem_name_table', column_name_list=['elem_name_id'],
                condition_str='elem_name="{0:s}"'.format(
                    e.name if e.name is not None else ''))[0][0]
            elem_family_id = self.getColumnDataFromTable(
                'elem_family_table', column_name_list=['elem_family_id'],
                condition_str='elem_family="{0:s}"'.format(
                    e.family if e.family is not None else ''))[0][0]
            elem_cell_id = self.getColumnDataFromTable(
                'elem_cell_table', column_name_list=['elem_cell_id'],
                condition_str='elem_cell="{0:s}"'.format(
                    e.cell if e.cell is not None else ''))[0][0]
            elem_devname_id = self.getColumnDataFromTable(
                'elem_devname_table', column_name_list=['elem_devname_id'],
                condition_str='elem_devname="{0:s}"'.format(
                    e.devname if e.devname is not None else ''))[0][0]
            elem_efflen_id = self.getColumnDataFromTable(
                'elem_efflen_table', column_name_list=['elem_efflen_id'],
                condition_str='elem_efflen="{0:s}"'.format(
                    LENGTH_METER_FORMAT.format(e.length)
                    if e.length is not None else ''))[0][0]
            elem_physlen_id = self.getColumnDataFromTable(
                'elem_physlen_table', column_name_list=['elem_physlen_id'],
                condition_str='elem_physlen="{0:s}"'.format(
                    LENGTH_METER_FORMAT.format(e.phylen)
                    if e.phylen is not None else ''))[0][0]
            elem_fields_id = self.getColumnDataFromTable(
                'elem_fields_table', column_name_list=['elem_fields_id'],
                condition_str='elem_fields="{0:s}"'.format(
                    e.fields().__repr__()
                    if e.fields() is not None else ''))[0][0]
            elem_girder_id = self.getColumnDataFromTable(
                'elem_girder_table', column_name_list=['elem_girder_id'],
                condition_str='elem_girder="{0:s}"'.format(
                    e.girder if e.girder is not None else ''))[0][0]
            elem_group_id = self.getColumnDataFromTable(
                'elem_group_table', column_name_list=['elem_group_id'],
                condition_str='elem_group="{0:s}"'.format(
                    e.group.__repr__() if e.group is not None else ''))[0][0]
            elem_sb_id = self.getColumnDataFromTable(
                'elem_sb_table', column_name_list=['elem_sb_id'],
                condition_str='elem_sb="{0:s}"'.format(
                    LENGTH_METER_FORMAT.format(e.sb)
                    if e.sb is not None else ''))[0][0]
            elem_se_id = self.getColumnDataFromTable(
                'elem_se_table', column_name_list=['elem_se_id'],
                condition_str='elem_se="{0:s}"'.format(
                    LENGTH_METER_FORMAT.format(e.se)
                    if e.se is not None else ''))[0][0]
            elem_sequence_id = self.getColumnDataFromTable(
                'elem_sequence_table', column_name_list=['elem_sequence_id'],
                condition_str='elem_sequence="{0:s}"'.format(
                    e.sequence.__repr__()
                    if e.sequence is not None else ''))[0][0]
            elem_symmetry_id = self.getColumnDataFromTable(
                'elem_symmetry_table', column_name_list=['elem_symmetry_id'],
                condition_str='elem_symmetry="{0:s}"'.format(
                    e.symmetry.__repr__()
                    if e.symmetry is not None else ''))[0][0]
            elem_pvs_id = self.getColumnDataFromTable(
                'elem_pvs_table', column_name_list=['elem_pvs_id'],
                condition_str='elem_pvs="{0:s}"'.format(
                    e.pv().__repr__() if e.pv() is not None else ''))[0][0]

            all_elem_prop_list_of_tuples.append(
                (machine_id, lat_id, elem_name_id, elem_family_id, elem_cell_id,
                 elem_devname_id, elem_efflen_id, elem_physlen_id,
                 elem_fields_id, elem_girder_id, elem_group_id, elem_sb_id,
                 elem_se_id, elem_sequence_id, elem_symmetry_id, elem_pvs_id)
            )

        table_name = 'elem_prop_table'
        column_def = [
            Column('elem_prop_id', 'INTEGER', primary_key=True),
            Column('machine_name_id', 'INTEGER', allow_null=False),
            Column('lattice_name_id', 'INTEGER', allow_null=False),
        ]
        column_def += [Column(k+'_id', 'INTEGER', allow_null=False)
                       for k in ELEM_KEYS]
        column_def += [Column('elem_prop_ctime', 'REAL', allow_null=False)]
        keys = ['machine_name', 'lattice_name'] + ELEM_KEYS
        column_def += [ForeignKeyConstraint(self,
                                            'fk_{0:s}_id'.format(k),
                                            '{0:s}_id'.format(k),
                                            '{0:s}_table'.format(k),
                                            '{0:s}_id'.format(k))
                       for k in keys]
        self.createTable(table_name, column_def)
        nCol = len(self.getColumnNames(table_name))
        self.insertRows(table_name, list_of_tuples=all_elem_prop_list_of_tuples,
                        bind_replacement_list_of_tuples=
                        [(nCol-1,
                          self.getCurrentEpochTimestampSQLiteFuncStr(
                              data_type='float'))])

        if '[unitconv_table text view]' not in self.getViewNames():
            self.create_temp_unitconv_table_text_view()
        all_aphla_ch_list_of_tuples = []
        for machine, lat, e in all_elem_tuples:
            machine_id = self.getColumnDataFromTable(
                'machine_name_table', column_name_list=['machine_name_id'],
                condition_str='machine_name="{0:s}"'.format(machine))[0][0]
            lat_id = self.getColumnDataFromTable(
                'lattice_name_table', column_name_list=['lattice_name_id'],
                condition_str='lattice_name="{0:s}"'.format(lat))[0][0]
            elem_name_id = self.getColumnDataFromTable(
                'elem_name_table', column_name_list=['elem_name_id'],
                condition_str='elem_name="{0:s}"'.format(
                    e.name if e.name is not None else ''))[0][0]
            (elem_prop_id,), (elem_fields_id,) = self.getColumnDataFromTable(
                'elem_prop_table',
                column_name_list=['elem_prop_id', 'elem_fields_id'],
                condition_str=('machine_name_id={0:d} and lattice_name_id={1:d} '
                               'and elem_name_id={2:d}'.format(
                                   machine_id, lat_id, elem_name_id)))
            fields = self.getColumnDataFromTable(
                'elem_fields_table', column_name_list=['elem_fields'],
                condition_str='elem_fields_id={0:d}'.
                format(elem_fields_id))[0][0]
            fields = eval(fields)
            for f in fields:
                field_id = self.getColumnDataFromTable(
                    'field_table', column_name_list=['field_id'],
                    condition_str='field="{0:s}"'.format(f))[0][0]

                all_aphla_ch_list_of_tuples.append((elem_prop_id, field_id))

        table_name = 'aphla_channel_table'
        column_def = [
            Column('aphla_ch_id', 'INTEGER', primary_key=True),
            Column('elem_prop_id', 'INTEGER', allow_null=False),
            Column('field_id', 'INTEGER', allow_null=False),
            ForeignKeyConstraint(self,
                                 'fk_elem_prop_id', 'elem_prop_id',
                                 'elem_prop_table', 'elem_prop_id'),
            ForeignKeyConstraint(self,
                                 'fk_field_id', 'field_id',
                                 'field_table', 'field_id'),
        ]
        self.createTable(table_name, column_def)
        self.insertRows(table_name, list_of_tuples=all_aphla_ch_list_of_tuples)

    #----------------------------------------------------------------------
    def _initConfigTables(self):
        """"""

        table_name = 'group_name_table'
        column_def = [
            Column('group_name_id', 'INTEGER', primary_key=True),
            Column('group_name', 'TEXT', allow_null=False, unique=True),
        ]
        self.createTable(table_name, column_def)

        table_name = 'user_table'
        column_def = [
            Column('user_id','INTEGER',primary_key=True),
            Column('username','TEXT',allow_null=False),
            Column('hostname','TEXT',allow_null=False),
            Column('ip_str','TEXT',allow_null=False),
            Column('mac_str','TEXT',allow_null=False),
        ]
        self.createTable(table_name, column_def)

        table_name = 'channel_name_table'
        column_def = [
            Column('channel_name_id','INTEGER',primary_key=True),
            Column('channel_name','TEXT', allow_null=False, unique=True),
        ]
        self.createTable(table_name, column_def)
        self.insertRows(table_name, list_of_tuples=[('',)])

        table_name = 'channel_table'
        column_def = [
            Column('channel_id', 'INTEGER', primary_key=True),
            Column('pvsp_id', 'INTEGER', allow_null=False),
            Column('pvrb_id', 'INTEGER', allow_null=False),
            Column('pvsp_array_size', 'INTEGER', allow_null=False),
            Column('pvrb_array_size', 'INTEGER', allow_null=False),
            Column('aphla_ch_id', 'INTEGER', allow_null=True),
            Column('unitsys_id', 'INTEGER', allow_null=False,
                   allow_default=True, default_value=unitsys_id_raw),
            Column('unitconv_toraw_id', 'INTEGER', allow_null=False),
            Column('unitconv_fromraw_id', 'INTEGER', allow_null=False),
            Column('channel_name_id', 'INTEGER', allow_null=False),
            Column('channel_ctime', 'REAL', allow_null=False),
            ForeignKeyConstraint(self,
                                 'fk_pvsp_id', 'pvsp_id',
                                 'pv_table', 'pv_id'),
            ForeignKeyConstraint(self,
                                 'fk_pvrb_id', 'pvrb_id',
                                 'pv_table', 'pv_id'),
            ForeignKeyConstraint(self,
                                 'fk_aphla_ch_id', 'aphla_ch_id',
                                 'aphla_channel_table', 'aphla_ch_id'),
            ForeignKeyConstraint(self,
                                 'fk_unitsys_id', 'unitsys_id',
                                 'unitsys_table', 'unitsys_id'),
            ForeignKeyConstraint(self,
                                 'fk_unitconv_toraw_id', 'unitconv_toraw_id',
                                 'unitconv_table', 'unitconv_id'),
            ForeignKeyConstraint(self,
                                 'fk_unitconv_fromraw_id', 'unitconv_fromraw_id',
                                 'unitconv_table', 'unitconv_id'),
        ]
        self.createTable(table_name, column_def)

        table_name = 'config_meta_table'
        column_def = [
            Column('config_id', 'INTEGER', primary_key=True),
            Column('config_user_id', 'INTEGER', allow_null=False),
            Column('config_masar_id', 'INTEGER', allow_null=True),
            Column('config_ref_step_size', 'REAL', allow_null=False),
            Column('config_synced_group_weight', 'INTEGER', allow_null=False),
            Column('config_ctime', 'REAL', allow_null=False),
            ForeignKeyConstraint(self,
                                 'fk_user_id', 'config_user_id',
                                 'user_table', 'user_id'),
        ]
        self.createTable(table_name, column_def)

        table_name = 'config_meta_text_search_table'
        column_def = [
            Column('config_id', 'INTEGER', allow_null=False, unique=True),
            Column('config_name', 'TEXT', allow_default=True,
                   default_value='""'),
            Column('config_description', 'TEXT', allow_default=True,
                   default_value='""'),
        ]
        self.createFTS4VirtualTable(table_name, column_def, tokenizer_str='')

        table_name = 'config_table'
        column_def = [
            Column('config_id', 'INTEGER', allow_null=False),
            Column('group_name_id', 'INTEGER', allow_null=False),
            Column('channel_id', 'INTEGER', allow_null=False),
            Column('config_weight', 'REAL', allow_default=True,
                   default_value='NaN'),
            Column('config_caput_enabled', 'INTEGER', allow_null=False,
                   allow_default=True, default_value=1),
            ForeignKeyConstraint(self,
                                 'fk_config_id', 'config_id',
                                 'config_meta_table', 'config_id'),
            ForeignKeyConstraint(self,
                                 'fk_group_name_id', 'group_name_id',
                                 'group_name_table', 'group_name_id'),
            ForeignKeyConstraint(self,
                                 'fk_channel_id', 'channel_id',
                                 'channel_table', 'channel_id'),
        ]
        self.createTable(table_name, column_def)

    #----------------------------------------------------------------------
    def _initSnapshotTables(self):
        """"""

        table_name = 'snapshot_meta_table'
        column_def = [
            Column('ss_id', 'INTEGER', primary_key=True),
            Column('config_id', 'INTEGER', allow_null=False),
            Column('ss_user_id', 'INTEGER', allow_null=False),
            Column('ss_masar_id', 'INTEGER', allow_null=True),
            Column('ss_ref_step_size', 'REAL', allow_null=False),
            Column('ss_synced_group_weight', 'INTEGER', allow_null=False),
            Column('caget_sent_ts_second', 'REAL', allow_null=False),
            Column('caput_sent_ts_second', 'REAL', allow_null=True),
            Column('ss_ctime', 'REAL', allow_null=False),
            ForeignKeyConstraint(self,
                                 'fk_config_id', 'config_id',
                                 'config_meta_table', 'config_id'),
            ForeignKeyConstraint(self,
                                 'fk_user_id', 'ss_user_id',
                                 'user_table', 'user_id'),
        ]
        self.createTable(table_name, column_def)

        table_name = 'snapshot_meta_text_search_table'
        column_def = [
            Column('ss_id', 'INTEGER', allow_null=False, unique=True),
            Column('ss_name', 'TEXT', allow_default=True, default_value='""'),
            Column('ss_description', 'TEXT', allow_default=True,
                   default_value='""'),
        ]
        self.createFTS4VirtualTable(table_name, column_def, tokenizer_str='')

    #----------------------------------------------------------------------
    def create_temp_unitconv_table_text_view(self):
        """"""

        self.createTempView(
            '[unitconv_table text view]',
            '''unitconv_table uc
            LEFT JOIN unitconv_type_table u1 ON uc.unitconv_type_id = u1.unitconv_type_id
            LEFT JOIN unitsys_table us1 ON us1.unitsys_id = uc.src_unitsys_id
            LEFT JOIN unitsys_table us2 ON us2.unitsys_id = uc.dst_unitsys_id
            LEFT JOIN unitsymb_table u2 ON uc.src_unitsymb_id = u2.unitsymb_id
            LEFT JOIN unitsymb_table u3 ON uc.dst_unitsymb_id = u3.unitsymb_id
            LEFT JOIN unitconv_blob_table ub ON uc.unitconv_blob_id = ub.unitconv_blob_id
            ''' ,
            column_name_list=[
                'uc.unitconv_id',
                'u1.unitconv_type AS unitconv_type',
                'uc.src_unitsys_id',
                'uc.dst_unitsys_id',
                'us1.unitsys AS src_unitsys',
                'us2.unitsys AS dst_unitsys',
                'ub.unitconv_blob',
                'u2.unitsymb AS src_unitsymb',
                'u3.unitsymb AS dst_unitsymb',
                'uc.inv',
                'uc.polarity',
                ])

    #----------------------------------------------------------------------
    def create_temp_channel_table_text_view(self):
        """"""

        self.createTempView(
            '[channel_table text view]',
            '''channel_table ct
            LEFT JOIN pv_table p1 ON ct.pvsp_id = p1.pv_id
            LEFT JOIN pv_table p2 ON ct.pvrb_id = p2.pv_id
            LEFT JOIN unitsys_table us ON ct.unitsys_id = us.unitsys_id
            LEFT JOIN channel_name_table cnt ON ct.channel_name_id = cnt.channel_name_id
            ''',
               column_name_list=[
                   'ct.channel_id',
                   'p1.pv AS pvsp',
                   'p2.pv AS pvrb',
                   'ct.pvsp_array_size',
                   'ct.pvrb_array_size',
                   'ct.aphla_ch_id',
                   'us.unitsys',
                   'ct.unitconv_toraw_id',
                   'ct.unitconv_fromraw_id',
                   'cnt.channel_name'
               ]
        )

    #----------------------------------------------------------------------
    def create_temp_config_meta_full_table_view(self):
        """"""

        self.createTempView(
            '[config_meta_table full view]',
            '''config_meta_table cmt
            LEFT JOIN config_meta_text_search_table cmtst ON cmt.config_id = cmtst.config_id
            ''',
               column_name_list=[
                   'cmt.config_id',
                   'cmtst.config_name',
                   'cmtst.config_description',
                   'cmt.config_user_id',
                   'cmt.config_masar_id',
                   'cmt.config_ref_step_size',
                   'cmt.config_synced_group_weight',
                   'cmt.config_ctime',
               ]
        )

    #----------------------------------------------------------------------
    def create_temp_config_meta_table_text_view(self):
        """"""

        self.createTempView(
            '[config_meta_table text view]',
            '''config_meta_table cmt
            LEFT JOIN config_meta_text_search_table cmtst ON cmt.config_id = cmtst.config_id
            LEFT JOIN user_table ut ON cmt.config_user_id = ut.user_id
            ''',
               column_name_list=[
                   'cmt.config_id',
                   'cmtst.config_name',
                   'cmtst.config_description',
                   'ut.username',
                   'cmt.config_masar_id',
                   'cmt.config_ref_step_size',
                   'cmt.config_synced_group_weight',
                   'cmt.config_ctime',
               ]
        )

    #----------------------------------------------------------------------
    def create_temp_ss_meta_table_text_view(self):
        """"""

        if '[config_meta_table text view]' not in self.getViewNames(
            square_brackets=True):
            self.create_temp_config_meta_table_text_view()

        self.createTempView(
            '[ss_meta_table text view]',
            '''snapshot_meta_table smt
            LEFT JOIN snapshot_meta_text_search_table smtst ON smt.ss_id = smtst.ss_id
            LEFT JOIN user_table ut ON smt.ss_user_id = ut.user_id
            LEFT JOIN [config_meta_table text view] cmt ON cmt.config_id = smt.config_id
            ''',
               column_name_list=[
                   'smt.ss_id',
                   'smtst.ss_name',
                   'smtst.ss_description',
                   'ut.username AS ss_username',
                   'smt.ss_masar_id',
                   'smt.ss_ref_step_size',
                   'smt.ss_synced_group_weight',
                   'smt.ss_ctime',
                   'cmt.config_id',
                   'cmt.config_name',
                   'cmt.config_description',
                   'cmt.username AS config_username',
                   'cmt.config_masar_id',
                   'cmt.config_ref_step_size',
                   'cmt.config_synced_group_weight',
                   'cmt.config_ctime',
               ]
        )

    #----------------------------------------------------------------------
    def create_temp_config_table_text_view(self):
        """"""

        if '[channel_table text view]' not in \
           self.getViewNames(square_brackets=True):
            self.create_temp_channel_table_text_view()
        if '[aphla channel prop text view]' not in \
           self.getViewNames(square_brackets=True):
            self.create_temp_aphla_channel_prop_text_view()
        if '[unitconv_table text view]' not in \
           self.getViewNames(square_brackets=True):
            self.create_temp_unitconv_table_text_view()

        self.createTempView(
            '[config_table text view]',
            '''config_table ct
            LEFT JOIN group_name_table gnt ON ct.group_name_id = gnt.group_name_id
            LEFT JOIN [channel_table text view] cht ON ct.channel_id = cht.channel_id
            LEFT JOIN [aphla channel prop text view] at ON cht.aphla_ch_id = at.aphla_ch_id
            LEFT JOIN [unitconv_table text view] ut1 ON cht.unitconv_toraw_id = ut1.unitconv_id
            LEFT JOIN [unitconv_table text view] ut2 ON cht.unitconv_fromraw_id = ut2.unitconv_id
            ''',
               column_name_list=[
                   'ct.rowid',
                   'ct.config_id',
                   'gnt.group_name',
                   'cht.channel_name',
                   'cht.pvsp',
                   'cht.pvrb',
                   'cht.pvsp_array_size',
                   'cht.pvrb_array_size',
                   'ct.config_weight AS weight',
                   'ct.config_caput_enabled AS caput_enabled',
                   'at.field',
                   'at.machine_name',
                   'at.lattice_name',
                   'at.elem_name',
                   'at.elem_family',
                   'at.elem_cell',
                   'at.elem_devname',
                   'at.elem_efflen',
                   'at.elem_physlen',
                   'at.elem_fields',
                   'at.elem_girder',
                   'at.elem_group',
                   'at.elem_sb',
                   'at.elem_se',
                   'at.elem_sequence',
                   'at.elem_symmetry',
                   'at.elem_pvs',
                   'cht.unitsys',
                   'ut1.unitconv_type',
                   'ut1.polarity',
                   'ut1.src_unitsymb AS unitsymb',
                   'ut1.dst_unitsymb AS unitsymb_raw',
                   'ut1.unitconv_blob AS unitconv_blob_toraw',
                   'ut2.unitconv_blob AS unitconv_blob_fromraw',
                   'ut1.inv AS unitconv_inv_toraw',
                   'ut2.inv AS unitconv_inv_fromraw',
               ]
        )

    #----------------------------------------------------------------------
    def create_temp_aphla_channel_prop_text_view(self):
        """"""

        self.createTempView(
            '[aphla channel prop text view]',
            '''channel_table ct
            LEFT JOIN aphla_channel_table act ON ct.aphla_ch_id = act.aphla_ch_id
            LEFT JOIN field_table ft ON act.field_id = ft.field_id
            LEFT JOIN elem_prop_table ept ON ept.elem_prop_id = act.elem_prop_id
            LEFT JOIN machine_name_table mnt ON ept.machine_name_id = mnt.machine_name_id
            LEFT JOIN lattice_name_table lnt ON ept.lattice_name_id = lnt.lattice_name_id
            LEFT JOIN elem_name_table ent ON ept.elem_name_id = ent.elem_name_id
            LEFT JOIN elem_family_table eft ON ept.elem_family_id = eft.elem_family_id
            LEFT JOIN elem_cell_table ect ON ept.elem_cell_id = ect.elem_cell_id
            LEFT JOIN elem_devname_table edt ON ept.elem_devname_id = edt.elem_devname_id
            LEFT JOIN elem_efflen_table eet ON ept.elem_efflen_id = eet.elem_efflen_id
            LEFT JOIN elem_physlen_table eplt ON ept.elem_physlen_id = eplt.elem_physlen_id
            LEFT JOIN elem_fields_table efst ON ept.elem_fields_id = efst.elem_fields_id
            LEFT JOIN elem_girder_table egt ON ept.elem_girder_id = egt.elem_girder_id
            LEFT JOIN elem_group_table egpt ON ept.elem_group_id = egpt.elem_group_id
            LEFT JOIN elem_sb_table esb ON ept.elem_sb_id = esb.elem_sb_id
            LEFT JOIN elem_se_table ese ON ept.elem_se_id = ese.elem_se_id
            LEFT JOIN elem_sequence_table esqt ON ept.elem_sequence_id = esqt.elem_sequence_id
            LEFT JOIN elem_symmetry_table esyt ON ept.elem_symmetry_id = esyt.elem_symmetry_id
            LEFT JOIN elem_pvs_table epvs ON ept.elem_pvs_id = epvs.elem_pvs_id
            ''',
               column_name_list=[
                   'ct.channel_id',
                   'ct.aphla_ch_id',
                   'ft.field',
                   'mnt.machine_name',
                   'lnt.lattice_name',
                   'ent.elem_name',
                   'eft.elem_family',
                   'ect.elem_cell',
                   'edt.elem_devname',
                   'eet.elem_efflen',
                   'eplt.elem_physlen',
                   'efst.elem_fields',
                   'egt.elem_girder',
                   'egpt.elem_group',
                   'esb.elem_sb',
                   'ese.elem_se',
                   'esqt.elem_sequence',
                   'esyt.elem_symmetry',
                   'epvs.elem_pvs',
               ]
        )

    #----------------------------------------------------------------------
    def get_unitconv_toraw_fromraw_ids(
        self, unitconv_dict, dst_unitsys=None, dst_unitsys_id=None,
        src_unitsymb=None, dst_unitsymb=None, append_new=True):
        """
        This function is to be used only for APHLA elements
        """

        uc_d_keys = unitconv_dict.keys()

        if uc_d_keys == []:
            unitconv_fromraw_id = unitconv_toraw_id = self.get_unitconv_id(
                unitconv_dict, src_unitsys_id=unitsys_id_raw,
                dst_unitsys_id=unitsys_id_raw, src_unitsymb=src_unitsymb,
                dst_unitsymb=src_unitsymb, inv=0, append_new=append_new)
        else:

            if (dst_unitsys is None) or (dst_unitsys == ''):
                unitconv_fromraw_id = self.get_unitconv_id(
                    {}, src_unitsys_id=unitsys_id_raw,
                    dst_unitsys_id=unitsys_id_raw, src_unitsymb=src_unitsymb,
                    dst_unitsymb=dst_unitsymb, inv=0, append_new=append_new)
                unitconv_toraw_id = self.get_unitconv_id(
                    {}, src_unitsys_id=unitsys_id_raw,
                    dst_unitsys_id=unitsys_id_raw, src_unitsymb=dst_unitsymb,
                    dst_unitsymb=src_unitsymb, inv=0, append_new=append_new)
            else:
                inv = 0
                if (None, dst_unitsys) in unitconv_dict:
                    uc = unitconv_dict[(None, dst_unitsys)]
                elif (dst_unitsys, None) in unitconv_dict:
                    uc = unitconv_dict[(dst_unitsys, None)]
                    if uc.invertible:
                        inv = 1
                    else:
                        uc = None
                else:
                    uc = None

                if uc is None:
                    raise ValueError('No unit conversion available')

                if dst_unitsys_id is None:
                    dst_unitsys_id = self.getMatchingPrimaryKeyIdFrom2ColTable(
                        'unitsys_table', 'unitsys_id', 'unitsys', dst_unitsys,
                        append_new=append_new)

                unitconv_fromraw_id = self.get_unitconv_id(
                    uc, src_unitsys_id=unitsys_id_raw,
                    dst_unitsys_id=dst_unitsys_id, src_unitsymb=src_unitsymb,
                    dst_unitsymb=dst_unitsymb, inv=inv, append_new=append_new)

                inv = 0
                if (dst_unitsys, None) in unitconv_dict:
                    uc = unitconv_dict[(dst_unitsys, None)]
                elif (None, dst_unitsys) in unitconv_dict:
                    uc = unitconv_dict[(None, dst_unitsys)]
                    if uc.invertible:
                        inv = 1
                    else:
                        uc = None
                else:
                    uc = None

                if uc is None:
                    raise ValueError('No unit conversion available')

                unitconv_toraw_id = self.get_unitconv_id(
                    uc, src_unitsys_id=dst_unitsys_id,
                    dst_unitsys_id=unitsys_id_raw, src_unitsymb=dst_unitsymb,
                    dst_unitsymb=src_unitsymb, inv=inv, append_new=append_new)

        return unitconv_toraw_id, unitconv_fromraw_id

    #----------------------------------------------------------------------
    def get_unitconv_id(
        self, unitconv, src_unitsys_id=None, dst_unitsys_id=None,
        src_unitsymb=None, dst_unitsymb=None, inv=None, append_new=True):
        """
        If `unitconv` is either UcPoly or UcInterp1 object, then
        `src_unitsys_id`, `dst_unitsys_id`, `src_unitsymb`, `dst_unitsymb`,
        and `inv` are all required.

        If `unitconv` is a dict (coming from a JSON file), then these arguments
        will be ignored, even if given, as the dict contains all the necessary
        information.
        """

        uc = unitconv

        if isinstance(uc, ap.unitconv.UcPoly):
            unitconv_type = 'poly'
            polarity = uc.polarity
            conv_data = tuple(uc.p.coeffs)
        elif isinstance(uc, ap.unitconv.UcInterp1):
            unitconv_type = 'interp1'
            polarity = uc.polarity
            conv_data = tuple([tuple(uc.xp), tuple(uc.fp)])
        elif uc == {}:
            unitconv_type = 'NoConversion'
            src_unitsys_id = dst_unitsys_id = unitsys_id_raw
            conv_data = None
            inv = 0
            polarity = +1
        elif isinstance(uc, dict):
            unitconv_type = uc['type']
            src_unitsymb = uc['src_unitsymb']
            dst_unitsymb = uc['dst_unitsymb']
            inv          = uc['inv']
            polarity     = uc['polarity']
            src_unitsys_id = self.getMatchingPrimaryKeyIdFrom2ColTable(
                'unitsys_table', 'unitsys_id', 'unitsys', uc['src_unitsys'],
                append_new=True)
            dst_unitsys_id = self.getMatchingPrimaryKeyIdFrom2ColTable(
                'unitsys_table', 'unitsys_id', 'unitsys', uc['dst_unitsys'],
                append_new=True)
            if unitconv_type == 'poly':
                conv_data = tuple(uc['conv_data'])
            elif unitconv_type == 'interp1':
                xp, fp = uc['conv_data']
                if not np.all(np.diff(xp) > 0.0):
                    print('Error for unit conversion definition: ')
                    print(uc)
                    raise ValueError('Monotonically increasing x array needed '
                                     'for interpolation')
                if (inv == 1) and \
                   (not np.all(np.diff(fp) > 0.0)) and \
                   (not np.all(np.diff(fp) < 0.0)):
                    print('Error for unit conversion definition: ')
                    print(uc)
                    raise ValueError(
                        'y array must be monotonically increasing or decreasing '
                        'for the interpolation to be invertible.')
                conv_data = tuple([tuple(xp), tuple(fp)])
            elif unitconv_type == 'NoConversion':
                conv_data = None
            else:
                raise ValueError('Unexpected unitconv type: {0:s}'.format(
                    unitconv_type))

        else:
            raise ValueError('Unexpected unitconv type: {0:s}'.
                             format(uc.__repr__()))

        if src_unitsymb is None: src_unitsymb = ''
        if dst_unitsymb is None: dst_unitsymb = ''

        if '[unitconv_table text view]' not in self.getViewNames():
            self.create_temp_unitconv_table_text_view()

        unitconv_id = self.getColumnDataFromTable(
            '[unitconv_table text view]',
            column_name_list=['unitconv_id'],
            condition_str=(
                'unitconv_type="{0:s}" and '
                'src_unitsys_id="{1:d}" and '
                'dst_unitsys_id="{2:d}" and '
                'unitconv_blob=? and '
                'src_unitsymb="{3:s}" and '
                'dst_unitsymb="{4:s}" and '
                'inv={5:d} and polarity={6:d}').format(
                    unitconv_type, src_unitsys_id, dst_unitsys_id,
                    src_unitsymb, dst_unitsymb, inv, polarity
                ),
            binding_tuple=(blobdumps(conv_data),)
        )

        if unitconv_id == []:
            if append_new:
                unitconv_blob_id = self.getMatchingPrimaryKeyIdFrom2ColTable(
                    'unitconv_blob_table', 'unitconv_blob_id', 'unitconv_blob',
                    blobdumps(conv_data), blob=True, append_new=True)
                unitconv_type_id = self.getMatchingPrimaryKeyIdFrom2ColTable(
                    'unitconv_type_table', 'unitconv_type_id', 'unitconv_type',
                    unitconv_type, append_new=True)
                src_unitsymb_id = self.getMatchingPrimaryKeyIdFrom2ColTable(
                    'unitsymb_table', 'unitsymb_id', 'unitsymb', src_unitsymb,
                    append_new=True)
                dst_unitsymb_id = self.getMatchingPrimaryKeyIdFrom2ColTable(
                    'unitsymb_table', 'unitsymb_id', 'unitsymb', dst_unitsymb,
                    append_new=True)
                table_name = 'unitconv_table'
                nCol = len(self.getColumnNames(table_name))
                list_of_tuples = [
                    (unitconv_type_id, src_unitsys_id, dst_unitsys_id,
                     src_unitsymb_id, dst_unitsymb_id, inv, polarity,
                     unitconv_blob_id)]
                self.insertRows(table_name, list_of_tuples,
                                bind_replacement_list_of_tuples=[
                                (nCol-1,
                                 self.getCurrentEpochTimestampSQLiteFuncStr(
                                     data_type='float'))])
                print('Added the following as a new row to Table "{0:s}"'.
                      format(table_name))
                print(list_of_tuples)
                return self.get_unitconv_id(
                    uc, src_unitsys_id, dst_unitsys_id,
                    src_unitsymb, dst_unitsymb, inv, append_new=False)
            else:
                return None
        elif len(unitconv_id) == 1:
            return unitconv_id[0][0]
        else:
            raise ValueError("Duplicate ID's have been found")

    #----------------------------------------------------------------------
    def getMatchingPrimaryKeyIdFrom2ColTable(
        self, table_name, primary_col_name, comparison_col_name,
        comparison_value, blob=False, append_new=True):
        """
        This function will get a unique ID in `primary_col_name` that matches
        the given `comparison_value` for the column `comparison_col_name` from
        a table consisting of 2 columns, one of which is a primary key column
        and the other is a value column.

        If `append_new` is True, the given value will be added to the table
        and the newly generated ID will be returned if the given value is not
        found in the table. If `append_new` is False, this function will
        return `None`.
        """

        col_names = self.getColumnNames(table_name)
        if len(col_names) != 2:
            raise ValueError('Number of columns in the table must be 2.')
        if not ((primary_col_name in col_names) and
                (comparison_col_name in col_names)):
            raise ValueError('The table must consist of columns with '
                             'primary_col_name and comparison_col_name. ')

        if not blob:
            if isinstance(comparison_value, (str, unicode)):
                str_format = '{0:s}="{1:s}"'
            elif isinstance(comparison_value, int):
                str_format = '{0:s}={1:d}'
            elif isinstance(comparison_value, float):
                conv_format = '{{0:.{0:d}f}}'.format(LENGTH_METER_PRECISION)
                comparison_value = conv_format.format(comparison_value)
                str_format = '{0:s}="{1:s}"'
            elif isinstance(comparison_value, type(None)):
                comparison_value = ''
                str_format = '{0:s}="{1:s}"'
            elif callable(comparison_value):
                comparison_value = comparison_value().__repr__()
                str_format = '{0:s}="{1:s}"'
            elif isinstance(comparison_value, (list, tuple, set)):
                comparison_value = comparison_value.__repr__()
                str_format = '{0:s}="{1:s}"'
            else:
                raise ValueError('Unexpected comparison_value type: {0:s}'.
                                 format(type(comparison_value)))

            unique_id = self.getColumnDataFromTable(
                table_name, column_name_list=[primary_col_name],
                condition_str=str_format.format(comparison_col_name,
                                                comparison_value))
        else:
            unique_id = self.getColumnDataFromTable(
                table_name, column_name_list=[primary_col_name],
                condition_str='{0}=?'.format(comparison_col_name),
                binding_tuple=(comparison_value,))

        if unique_id == []:
            if append_new:
                self.insertRows(table_name, [(comparison_value,)])
                if not blob:
                    comparison_value_repr = comparison_value
                else:
                    comparison_value_repr = blobloads(comparison_value)
                print('Added a new row with', comparison_value_repr,
                      ('for Column "{0:s}" in Table "{1:s}"'.
                       format(comparison_col_name, table_name)))
                return self.getMatchingPrimaryKeyIdFrom2ColTable(
                    table_name, primary_col_name, comparison_col_name,
                    comparison_value, blob=blob, append_new=False)
            else:
                return None
        elif len(unique_id[0]) == 1:
            return unique_id[0][0]
        else:
            raise ValueError("Duplicate ID's have been found")

    #----------------------------------------------------------------------
    def get_elem_prop_id(
        self, machine_name_id, lattice_name_id, aphla_elem, append_new=True):
        """
        This function will get the primary key ID that matches
        the given `machine_name_id`, `lattice_name_id` and `elem_name_id`
        from `elem_prop_table`.

        If `append_new` is True, a new row with the corresponding information
        will be added to the table and the newly generated ID will be returned
        if a match is not found in the table. If `append_new` is False, this
        function will return `None`.
        """

        table_name       = 'elem_prop_table'
        primary_col_name = 'elem_prop_id'

        elem_id_dict = {}
        for k, a in zip(ELEM_KEYS, ELEM_ATTRS):
            elem_id_dict[k] = self.getMatchingPrimaryKeyIdFrom2ColTable(
                '{:s}_table'.format(k), '{:s}_id'.format(k), k,
                getattr(aphla_elem, a), append_new=append_new)

        condition_str = ('machine_name_id={0:d} and lattice_name_id={1:d}'.
                         format(machine_name_id, lattice_name_id))
        for k in ELEM_KEYS:
            condition_str += ' and {0:s}={1:d}'.format(k+'_id', elem_id_dict[k])

        elem_prop_id = self.getColumnDataFromTable(
            table_name, column_name_list=[primary_col_name],
            condition_str=condition_str)

        if elem_prop_id == []:
            if append_new:
                nCol = len(self.getColumnNames(table_name))
                list_of_tuples = [tuple([machine_name_id, lattice_name_id] +
                           [elem_id_dict[k] for k in ELEM_KEYS])]
                self.insertRows(table_name, list_of_tuples,
                                bind_replacement_list_of_tuples=[
                                    (nCol-1,
                                     self.getCurrentEpochTimestampSQLiteFuncStr(
                                         data_type='float'))])
                print('Added the following as a new row to Table "{0:s}"'.
                      format(table_name))
                print(list_of_tuples)
                return self.get_elem_prop_id(
                    machine_name_id, lattice_name_id, aphla_elem,
                    append_new=False)
            else:
                return None
        elif len(elem_prop_id[0]) == 1:
            return elem_prop_id[0][0]
        else:
            raise ValueError("Duplicate ID's have been found")

    #----------------------------------------------------------------------
    def get_aphla_ch_id(
        self, elem_prop_id, field_id, append_new=True):
        """
        """

        table_name       = 'aphla_channel_table'
        primary_col_name = 'aphla_ch_id'

        aphla_ch_id = self.getColumnDataFromTable(
            table_name, column_name_list=[primary_col_name],
            condition_str=(
                'elem_prop_id={0:d} and field_id={1:d}').format(
                    elem_prop_id, field_id))

        if aphla_ch_id == []:
            if append_new:

                list_of_tuples = [(elem_prop_id, field_id)]
                self.insertRows(table_name, list_of_tuples)
                print('Added the following as a new row to Table "{0:s}"'.
                      format(table_name))
                print(list_of_tuples)
                return self.get_aphla_ch_id(
                    elem_prop_id, field_id, append_new=False)

            else:
                return None
        elif len(aphla_ch_id[0]) == 1:
            return aphla_ch_id[0][0]
        else:
            raise ValueError("Duplicate ID's have been found")

    #----------------------------------------------------------------------
    def get_aphla_elem_obj(self, elem_prop_id):
        """"""

        out = self.getColumnDataFromTable(
            'elem_prop_table',
            column_name_list=['machine_name_id', 'lattice_name_id',
                              'elem_name_id'],
            condition_str='elem_prop_id={0:d}'.format(elem_prop_id))

        if out == []:
            return None
        elif len(out[0]) == 1:
            (machine_name_id,), (lattice_name_id,), (elem_name_id,) = out
            machine_name = self.getColumnDataFromTable(
                'machine_name_table', column_name_list=['machine_name'],
                condition_str=('machine_name_id={0:d}'.
                               format(machine_name_id)))[0][0]
            current_machine = ap.machines.getLattice().machine
            if current_machine != machine_name:
                ap.machines.load(machine_name)
            lattice_name = self.getColumnDataFromTable(
                'lattice_name_table', column_name_list=['lattice_name'],
                condition_str=('lattice_name_id={0:d}'.
                               format(lattice_name_id)))[0][0]
            ap.machines.use(lattice_name)
            elem_name = self.getColumnDataFromTable(
                'elem_name_table', column_name_list=['elem_name'],
                condition_str=('elem_name_id={0:d}'.
                               format(elem_name_id)))[0][0]
            return ap.getElements(elem_name)[0]
        else:
            raise ValueError('Duplicate match found')

    #----------------------------------------------------------------------
    def get_pv_id(self, pv_str, readonly, append_new=True):
        """"""

        if pv_str == '':
            return 1 # pv_id for non-specified PV is 1.

        cainfo = catools.connect(str(pv_str), cainfo=True, throw=False)
        # ^ Need to make sure `pv_str` is type "str", not "unicode".
        # Otherwise, catools.connect() will divide the unicode into a list of
        # each character.
        if cainfo.ok:
            array_size      = cainfo.count
            pv_data_type_id = cainfo.datatype + 1
        else:
            msg = QMessageBox()
            msg.setText('Non-existing or disconnected PV.')
            msg.setInformativeText(pv_str)
            msg.setIcon(QMessageBox.Critical)
            msg.exec_()
            return -1

        if CA_DATATYPES[pv_data_type_id-1] not in CA_DATATYPES_TINKERABLE:
            msg = QMessageBox()
            msg.setText(('The following PV cannot be used in aptinker due to '
                         'its data type being {0:s}.'.format(
                             CA_DATATYPES[pv_data_type_id-1])))
            msg.setInformativeText(pv_str)
            msg.setIcon(QMessageBox.Critical)
            msg.exec_()
            return -2

        table_name = 'pv_table'

        out = self.getColumnDataFromTable(
            table_name,
            column_name_list=['pv_id', 'array_size', 'pv_data_type_id'],
            condition_str='pv="{0:s}" and readonly={1:d}'.format(pv_str,
                                                                 readonly))

        if out == []:
            if append_new:
                list_of_tuples = [(pv_str, readonly, array_size,
                                   pv_data_type_id)]
                self.insertRows(table_name, list_of_tuples)
                print('Added the following as a new row to Table "{0:s}"'.
                      format(table_name))
                print(list_of_tuples)
                return self.get_pv_id(pv_str, readonly, append_new=False)
            else:
                return None
        elif len(out[0]) == 1:
            (pv_id,), (old_array_size,), (old_pv_data_type_id,) = out
            if (old_array_size is None) or (old_array_size != array_size):
                self.changeValues(table_name, 'array_size', array_size,
                                  condition_str='pv_id={0:d}'.format(pv_id))
                self.changeValues(
                    table_name, 'pv_data_type_id', pv_data_type_id,
                    condition_str='pv_id={0:d}'.format(pv_id))
            return pv_id
        else:
            raise ValueError("Duplicate ID's have been found")

    #----------------------------------------------------------------------
    def is_pv_scalar(self, pv_id):
        """"""

        table_name = 'pv_table'

        array_size = self.getColumnDataFromTable(
            table_name, column_name_list=['array_size'],
            condition_str='pv_id={0:d}'.format(pv_id))

        if array_size == []:
            return None
        elif len(array_size[0]) == 1:
            array_size = array_size[0][0]
            if array_size == 1:
                return True
            elif array_size is None:
                return None
            else:
                return False
        else:
            raise ValueError("Duplicate ID's have been found")

    #----------------------------------------------------------------------
    def get_pv_array_sizes(self, pvsp_id, pvrb_id):
        """"""

        table_name = 'pv_table'

        out = self.getColumnDataFromTable(
            table_name, column_name_list=['pv_id', 'array_size'],
            condition_str='pv_id in ({0:d}, {1:d})'.format(pvsp_id, pvrb_id))

        if out == []:
            return None
        else:
            if pvsp_id == pvrb_id:
                return [out[1][0]]*2
            else:
                return [out[1][out[0].index(pvsp_id)],
                        out[1][out[0].index(pvrb_id)]]

    #----------------------------------------------------------------------
    def get_channel_id(
        self, pvsp_id, pvrb_id, unitsys_id, channel_name_id,
        unitconv_toraw_id, unitconv_fromraw_id, aphla_ch_id=None,
        append_new=True):
        """
        """

        table_name = 'channel_table'

        if aphla_ch_id is not None:
            condition_str = (
                ('pvsp_id={0:d} and pvrb_id={1:d} and '
                 'unitsys_id={2:d} and unitconv_toraw_id={3:d} '
                 'and unitconv_fromraw_id={4:d} and '
                 'channel_name_id={5:d} and aphla_ch_id={6:d}').
                format(pvsp_id, pvrb_id, unitsys_id,
                       unitconv_toraw_id, unitconv_fromraw_id,
                       channel_name_id, aphla_ch_id)
            )
        else:
            condition_str = (
                ('pvsp_id={0:d} and pvrb_id={1:d} and '
                 'unitsys_id={2:d} and unitconv_toraw_id={3:d} '
                 'and unitconv_fromraw_id={4:d} and '
                 'channel_name_id={5:d}').
                format(pvsp_id, pvrb_id, unitsys_id,
                       unitconv_toraw_id, unitconv_fromraw_id,
                       channel_name_id)
            )

        channel_id = self.getColumnDataFromTable(
            table_name, column_name_list=['channel_id'],
            condition_str=condition_str)

        if channel_id == []:
            if append_new:
                pv_array_sizes = self.get_pv_array_sizes(pvsp_id, pvrb_id)
                if pv_array_sizes is None:
                    print('PV ids not found. A new channel will NOT be created.')
                else:
                    pvsp_array_size, pvrb_array_size = pv_array_sizes
                nCol = len(self.getColumnNames(table_name))
                list_of_tuples = [(pvsp_id, pvrb_id, pvsp_array_size,
                                   pvrb_array_size, aphla_ch_id,
                                   unitsys_id, unitconv_toraw_id,
                                   unitconv_fromraw_id, channel_name_id)]
                self.insertRows(table_name, list_of_tuples,
                                bind_replacement_list_of_tuples=[
                                    (nCol-1,
                                     self.getCurrentEpochTimestampSQLiteFuncStr(
                                         data_type='float'))])
                print('Added the following as a new row to Table "{0:s}"'.
                      format(table_name))
                print(list_of_tuples)
                return self.get_channel_id(
                    pvsp_id, pvrb_id, unitsys_id, channel_name_id,
                    unitconv_toraw_id, unitconv_fromraw_id,
                    aphla_ch_id=aphla_ch_id, append_new=False)
            else:
                return None
        elif len(channel_id[0]) == 1:
            return channel_id[0][0]
        else:
            raise ValueError("Duplicate ID's have been found")

    #----------------------------------------------------------------------
    def saveSnapshot(self, snapshot_abstract_model):
        """"""

        a = snapshot_abstract_model

        table_name_meta             = 'snapshot_meta_table'
        table_name_meta_text_search = 'snapshot_meta_text_search_table'

        meta_list_of_tuples = [
            (a.config_id, self.get_user_id(a.userinfo, append_new=True),
             a.masar_id, a.ref_step_size, a.synced_group_weight,
             a.caget_sent_ts_second, a.caput_sent_ts_second)]

        nCol = len(self.getColumnNames(table_name_meta))

        self.lockDatabase()

        maxID_meta = self.getMaxInColumn(table_name_meta, 'ss_id')
        if maxID_meta is not None:
            ss_id = maxID_meta + 1
        else:
            ss_id = 1

        meta_text_search_list_of_tuples = [(ss_id, a.name, a.description)]

        self.insertRows(table_name_meta, meta_list_of_tuples,
                        bind_replacement_list_of_tuples=[
                            (nCol-1,
                             self.getCurrentEpochTimestampSQLiteFuncStr(
                                 data_type='float'))])

        self.insertRows(table_name_meta_text_search,
                        meta_text_search_list_of_tuples)

        self.unlockDatabase()

        ss_ctime = self.getColumnDataFromTable(
            'snapshot_meta_table', column_name_list=['ss_ctime'],
            condition_str='ss_id={0:d}'.format(ss_id))[0][0]

        a.ss_id = ss_id
        a.ss_ctime = ss_ctime

        ss_folderpath = osp.join(config.SNAPSHOT_FOLDERPATH,
                                 date_month_folder_str(ss_ctime))
        if not osp.exists(ss_folderpath):
            os.makedirs(ss_folderpath, mode=0o764)
            # ^ make the folder also writable by group

        ss_filepath = osp.join(
            ss_folderpath, date_snapshot_filename_str(ss_ctime, a.userinfo[0]))

        _ca = a._config_abstract

        f = h5py.File(ss_filepath, 'w')

        weights = np.array(_ca.weights)
        f.create_dataset('weights', shape=weights.shape, data=weights,
                         compression=h5zip)

        caput_enabled_rows = np.array(_ca.caput_enabled_rows, dtype=np.bool)
        f.create_dataset('caput_enabled_rows', shape=caput_enabled_rows.shape,
                         data=caput_enabled_rows, compression=h5zip)

        # Save "caput_raws"
        caput_raws_sizes = [
            1 if not isinstance(r, catools.dbr.ca_array) else r.size
            for r in a.caput_raws]
        caput_raws_scalars = [
            r for r, size in zip(a.caput_raws, caput_raws_sizes) if size == 1]
        caput_raws_arrays = [
            r.__array__() for r, size in zip(a.caput_raws, caput_raws_sizes)
            if size != 1]
        f.create_dataset('caput_raws_scalars', shape=(len(caput_raws_scalars),),
                         data=caput_raws_scalars, compression=h5zip)
        if caput_raws_arrays != []:
            f.create_group('caput_raws_arrays')
            g = f['caput_raws_arrays']
            for j, array in enumerate(caput_raws_arrays):
                g.create_dataset(str(j), shape=array.shape, data=array,
                                 compression=h5zip)

        # Save "caget_raws"
        caget_raws_sizes = [
            1 if not isinstance(r, catools.dbr.ca_array) else r.size
            for r in a.caget_raws]
        caget_raws_scalars = [
            r for r, size in zip(a.caget_raws, caget_raws_sizes) if size == 1]
        caget_raws_arrays = [
            r.__array__() for r, size in zip(a.caget_raws, caget_raws_sizes)
            if size != 1]
        f.create_dataset('caget_raws_scalars', shape=(len(caget_raws_scalars),),
                         data=caget_raws_scalars, compression=h5zip)
        if caget_raws_arrays != []:
            f.create_group('caget_raws_arrays')
            g = f['caget_raws_arrays']
            for j, array in enumerate(caget_raws_arrays):
                g.create_dataset(str(j), shape=array.shape, data=array,
                                 compression=h5zip)

        f.create_dataset('caget_ioc_ts_tuples',
                         shape=a.caget_ioc_ts_tuples.shape,
                         data=a.caget_ioc_ts_tuples, compression=h5zip)

        f.close()

    #----------------------------------------------------------------------
    def saveConfig(self, config_abstract_model):
        """"""

        a = config_abstract_model

        table_name_meta            = 'config_meta_table'
        table_name_meta_text_seach = 'config_meta_text_search_table'

        meta_list_of_tuples = [
            (self.get_user_id(a.userinfo, append_new=True),
             a.masar_id, a.ref_step_size, a.synced_group_weight)]

        nCol = len(self.getColumnNames(table_name_meta))

        self.lockDatabase()

        maxID_meta = self.getMaxInColumn(table_name_meta, 'config_id')
        if maxID_meta is not None:
            config_id = maxID_meta + 1
        else:
            config_id = 1

        meta_text_search_list_of_tuples = [(config_id, a.name, a.description)]

        self.insertRows(table_name_meta, meta_list_of_tuples,
                        bind_replacement_list_of_tuples=[
                            (nCol-1,
                             self.getCurrentEpochTimestampSQLiteFuncStr(
                                 data_type='float'))])

        self.insertRows(table_name_meta_text_seach,
                        meta_text_search_list_of_tuples)

        self.unlockDatabase()

        config_ctime = self.getColumnDataFromTable(
            'config_meta_table', column_name_list=['config_ctime'],
        condition_str='config_id={0:d}'.format(config_id))[0][0]

        a.config_id = config_id
        a.config_ctime = config_ctime

        table_name = 'config_table'

        list_of_tuples = [(config_id, gn_id, ch_id, w, bool(caput_enabled))
                          for gn_id, ch_id, w, caput_enabled
                          in zip(a.group_name_ids, a.channel_ids, a.weights,
                                 a.caput_enabled_rows)]
        self.insertRows(table_name, list_of_tuples)

    #----------------------------------------------------------------------
    def get_user_id(self, userinfo_tuple, append_new=True):
        """"""

        table_name = 'user_table'

        user_id = self.getColumnDataFromTable(
            table_name, column_name_list=['user_id'],
            condition_str=('username="{0:s}" and hostname="{1:s}" and '
                           'ip_str="{2:s}" and mac_str="{3:s}"').format(
                               *userinfo_tuple))

        if user_id == []:
            if append_new:
                list_of_tuples = [userinfo_tuple]
                self.insertRows(table_name, list_of_tuples)
                print('Added the following as a new row to Table "{0:s}"'.
                      format(table_name))
                print(list_of_tuples)
                return self.get_user_id(userinfo_tuple, append_new=False)
            else:
                return None
        elif len(user_id[0]) == 1:
            return user_id[0][0]
        else:
            raise ValueError("Duplicate ID's have been found")

    #----------------------------------------------------------------------
    def get_config_ids(self, config_name, config_description, config_user_id,
                       config_masar_id, config_ref_step_size,
                       config_synced_group_weight):
        """"""

        table_name = '[config_meta_table full view]'
        if table_name not in self.getViewNames(square_brackets=True):
            self.create_temp_config_meta_full_table_view()

        if config_masar_id is None:
            config_masar_id_condition_str = '(config_masar_id is null)'
        else:
            config_masar_id_condition_str = ('config_masar_id={0:d}'.
                                             format(config_masar_id))

        if config_synced_group_weight:
            config_synced_group_weight_int = 1
        else:
            config_synced_group_weight_int = 0

        config_ids = self.getColumnDataFromTable(
            table_name, column_name_list=['config_id'],
            condition_str=\
            '''config_name="{0:s}" and
               config_description="{1:s}" and
               config_user_id={2:d} and {3:s} and
               (config_ref_step_size - {4:.12f} < 1e-10) and
               config_synced_group_weight={5:d}
            '''.format(config_name, config_description, config_user_id,
                       config_masar_id_condition_str, config_ref_step_size,
                       config_synced_group_weight_int))

        if config_ids == []:
            return None
        else:
            return config_ids[0]

    #----------------------------------------------------------------------
    def get_GLOB_condition_str(self, glob_pattern, column_name):
        """
        ESCAPE command is not implemented for GLOB by SQLite, even though the
        syntax diagram says it is.

        The workaround for escaping glob special characters is provided here.
        """

        glob_pattern = glob_pattern.replace(r'\*', '[*]')
        glob_pattern = glob_pattern.replace(r'\?', '[?]')
        glob_pattern = glob_pattern.replace(r'\[', '[[]')
        glob_pattern = glob_pattern.replace(r'\]', '[]]')

        cond_str = '({0:s} GLOB "{1:s}")'.format(column_name, glob_pattern)

        return cond_str

    #----------------------------------------------------------------------
    def get_MATCH_condition_str(self, full_search_string):
        """
        Full-text searching provided by MATCH only works for FTS4 virtual table
        """

        if full_search_string.startswith('-'):
            msg = QMessageBox()
            msg.setText('First search string cannot start with "-" (minus).')
            msg.setIcon(QMessageBox.Critical)
            msg.exec_()
            return

        full_search_string = full_search_string.replace(r'\*', '[*]')
        full_search_string = full_search_string.replace(r'\?', '[?]')
        full_search_string = full_search_string.replace(r'\[', '[[]')
        full_search_string = full_search_string.replace(r'\]', '[]]')

        quote_found = ''
        quote_inds = []
        non_quote_inds = []
        for i, c in enumerate(full_search_string):
            if c in ("'", '"'):
                if quote_found == '':
                    quote_found = c
                    quote_inds.append(i)
                elif quote_found == c:
                    quote_inds.append(i)
                    quote_found = ''
                else:
                    non_quote_inds.append(i)

        if quote_found != '':
            non_quote_inds.append(quote_inds.pop())
            non_quote_inds.sort()

        tokens = []
        for i in range(len(quote_inds))[::-2]:
            ini = quote_inds[i-1]
            end = quote_inds[i]
            tokens.append(full_search_string[(ini+1):end])
            full_search_string = full_search_string[:ini] + \
                full_search_string[(end+1):]
        tokens += full_search_string.split()

        cond_str = ' '.join(['"{0:s}"'.format(t.replace("'", "''")) if ' ' in t
                             else t.replace("'", "''") for t in tokens])

        return cond_str

    #----------------------------------------------------------------------
    def get_config_ids_with_MATCH(self, MATCH_cond_str, column_name):
        """"""

        fts_condition_str = "{0:s} MATCH '{1:s}'".format(
            column_name, MATCH_cond_str)

        matched_rowids = self.getColumnDataFromTable(
            'config_meta_text_search_table', column_name_list=['config_id'],
            condition_str=fts_condition_str)
        if matched_rowids != []:
            matched_config_ids = list(matched_rowids[0])
        else:
            matched_config_ids = None

        return matched_config_ids

    #----------------------------------------------------------------------
    def get_ss_ids_with_MATCH(self, MATCH_cond_str, column_name):
        """"""

        fts_condition_str = "{0:s} MATCH '{1:s}'".format(
            column_name, MATCH_cond_str)

        matched_rowids = self.getColumnDataFromTable(
            'snapshot_meta_text_search_table', column_name_list=['ss_id'],
            condition_str=fts_condition_str)
        if matched_rowids != []:
            matched_ss_ids = list(matched_rowids[0])
        else:
            matched_ss_ids = None

        return matched_ss_ids

if __name__ == '__main__':
    db = TinkerMainDatabase()
