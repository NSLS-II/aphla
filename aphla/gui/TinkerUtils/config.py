import os
import os.path as osp
import numpy as np
from time import strftime, localtime

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
        'field_name',
        'weight',
        ],
    'snapshot_view': [
        'group_name',
        'pvsp',
        'pvrb',
        'elem_name',
        'field_name',
        'weight',
        'step_size',
        'cur_RB',
        'cur_SP',
    ],
}

#----------------------------------------------------------------------
def datestr(time_in_seconds_from_Epoch):
    """"""

    frac_sec = time_in_seconds_from_Epoch - np.floor(time_in_seconds_from_Epoch)
    time_format = '%Y-%m-%d (%a) %H:%M:%S.' + '{0:.6f}'.format(frac_sec)[2:]

    return strftime(time_format, localtime(time_in_seconds_from_Epoch))

#----------------------------------------------------------------------
def datestr_ns(ioc_raw_timestamp_tuple):
    """"""

    seconds, nanoseconds = ioc_raw_timestamp_tuple

    if nanoseconds == -1:
        return 'None'

    time_format = '%Y-%m-%d (%a) %H:%M:%S.'
    str_upto_seconds = strftime(time_format, localtime(seconds))

    return str_upto_seconds + '{:d}'.format(nanoseconds)
