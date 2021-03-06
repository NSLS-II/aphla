import os
import os.path as osp

from aphla.gui.utils.hlsqlite import SQLiteDatabase

HOME = osp.expanduser('~')
HLA_MACHINE = os.environ.get('HLA_MACHINE', 'nsls2')

HOME_PATH             = osp.expanduser('~')
APHLA_USER_CONFIG_DIR = osp.join(HOME_PATH, '.aphla')
APHLA_APSCRIPTS_DIR   = os.environ.get('APHLA_APSCRIPTS_DIR',
                                       APHLA_USER_CONFIG_DIR)
#APHLA_APSCRIPTS_DIR   = APHLA_USER_CONFIG_DIR

DB_FOLDERPATH = osp.join(APHLA_APSCRIPTS_DIR, 'aptinker_db')
if not osp.exists(DB_FOLDERPATH):
    os.makedirs(DB_FOLDERPATH)
MAIN_DB_FILEPATH    = osp.join(DB_FOLDERPATH, 'aptinker_main.sqlite')

SNAPSHOT_FOLDERPATH = osp.join(DB_FOLDERPATH, 'snapshots')

THIS_FOLDERPATH = osp.dirname(osp.abspath(__file__))
COLUMN_DEFINITION_DB_FILEPATH = osp.join(THIS_FOLDERPATH,
                                         'tinker_columns.sqlite')
COL_DEF = SQLiteDatabase(filepath=COLUMN_DEFINITION_DB_FILEPATH,
                         create_folder=False)

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
        'caput_enabled',
        'cur_ConvSP',
        'cur_ConvRB',
        'unitsymb',
        'D_cur_ConvRB_cur_ConvSP',
        'ini_ConvSP'
    ],
    'snapshot_DB': [
        'group_name',
        'pvsp',
        'pvrb',
        'channel_name',
        'ss_ConvSP',
        'ss_ConvSentSP',
        'ss_ConvRB',
        'unitsymb'
    ],
}

