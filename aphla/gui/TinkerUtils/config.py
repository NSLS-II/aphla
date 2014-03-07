import os
import os.path as osp

from tinkerdb import SQLiteDatabase

HOME = osp.expanduser('~')
HLA_MACHINE = os.environ.get('HLA_MACHINE', 'nsls2')

DB_FOLDERPATH = '/home/yhidaka/hg_repos/hla/aphla/gui/TinkerUtils'

COLUMN_DEFINITION_DB_FILEPATH = osp.join(DB_FOLDERPATH,
                                         'tinker_columns.sqlite')
COL_DEF = SQLiteDatabase(filepath=COLUMN_DEFINITION_DB_FILEPATH,
                         create_folder=False)

MAIN_DB_FILEPATH = osp.join(DB_FOLDERPATH, 'test_tinker.sqlite')
#CONFIG_DB_FILEPATH = '/epics/op/apps/apscripts/db/aptinker_configs.db'


DEF_VIS_COL_KEYS = {
    'config_setup': [
        'group_name',
        'pvsp',
        'pvrb',
        'elem_name',
        'field',
        'weight',
        ],
    'snapshot_view': [
        'group_name',
        'pvsp',
        'pvrb',
        'channel_name',
        'weight',
        'step_size',
        'cur_RB',
        'cur_RB_ioc_ts',
        'cur_SP',
        'cur_SP_ioc_ts',
        'cur_SentSP'
    ],
}

