import os

HOME = os.path.expanduser('~')
HLA_MACHINE = os.environ.get('HLA_MACHINE', None)

CLIENT_DATA_FOLDERPATH = os.path.join(HOME,'.hla',HLA_MACHINE,'tuner_client')
SERVER_DATA_FOLDERPATH = os.path.join(HOME,'.hla',HLA_MACHINE,'tuner_server')
MAIN_DB_FILENAME = 'tuner.sqlite'
NEW_MAIN_DB_FILENAME = 'new_tuner.sqlite'
LAST_SYNCED_MAIN_DB_FILENAME = 'last_synced_tuner.sqlite'
CLIENT_DELTA_DB_FILENAME = 'client_delta.sqlite'
SERVER_DELTA_DB_FILENAME = 'server_delta.sqlite'
CLIENT_SERVER_DELTA_DB_FILENAME = 'client_server_delta.sqlite'

STR_FMT_DEFAULT = ''
STR_FMT_WEIGHT_FACTOR = ':.8g'
STR_FMT_LENGTH_METER = ':.6g'
STR_FMT_PV_VAL = ':.4g'
STR_FMT_TIMESTAMP = 'timestamp'
STR_FMT_GUI = 'gui'

ENUM_FULL_DESCRIP_NAME = 0
ENUM_SHORT_DESCRIP_NAME = 1 # used for column headers
ENUM_DATA_TYPE = 2
ENUM_ONLY_FOR_SNAPSHOT = 3
ENUM_STR_FORMAT = 4
ENUM_EDITABLE = 5
PROP_DICT = {
    'group_name'  : ['Group Name', 'GroupName', 'string', False, STR_FMT_DEFAULT, True],
    'machine_name': ['Machine', 'Machine', 'string', False, STR_FMT_DEFAULT, False],
    'lattice_name': ['Lattice', 'Lattice', 'string', False, STR_FMT_DEFAULT, False],
    'channel_name': ['Channel Name', 'ChannelName', 'string', False, STR_FMT_DEFAULT, False], # can be either a channel name (elem_name.field_name) or PV tuple (PV_readback, PV_setpoint)
    'elem_name'   : ['Element Name', 'Elem.Name', 'string', False, STR_FMT_DEFAULT, False],
    'field'       : ['Field', 'Field', 'string', False, STR_FMT_DEFAULT, False],
    'pvrb'        : ['PV-RB Name', 'PVRB', 'string', False, STR_FMT_DEFAULT, False],
    'pvsp'        : ['PV-SP Name', 'PVSP', 'string', False, STR_FMT_DEFAULT, False],
    'golden'      : ['Golden', 'Golden', 'float', False, STR_FMT_PV_VAL, False],
    'devname'     : ['Device Name', 'Dev.Name', 'string', False, STR_FMT_DEFAULT, False],
    'cell'        : ['Cell', 'Cell', 'string', False, STR_FMT_DEFAULT, False],
    'family'      : ['Family', 'Family', 'string', False, STR_FMT_DEFAULT, False],
    'girder'      : ['Girder', 'Girder', 'string', False, STR_FMT_DEFAULT, False],
    'elem_group'  : ['Element Group', 'Elem.Group', 'string', False, STR_FMT_DEFAULT, False],
    'lat_index'   : ['Lattice Index', 'Lat.Index', 'int', False, STR_FMT_DEFAULT, False],
    'eff_len'     : ['Effective Length', 'Eff.Len.', 'float', False, STR_FMT_LENGTH_METER, False],
    'phys_len'    : ['Physical Length', 'Phys.Len.', 'float', False, STR_FMT_LENGTH_METER, False],
    'sb'          : ['s(beginning)', 'sb', 'float', False, STR_FMT_LENGTH_METER, False],
    'se'          : ['s(end)', 'se', 'float', False, STR_FMT_LENGTH_METER, False],
    'symmetry'    : ['Symmetry', 'Symmetry', 'string', False, STR_FMT_DEFAULT, False],
    'unitsymb'    : ['Unit Symbol', 'Unit Symb.', 'string', False, STR_FMT_DEFAULT, False],
    'unitsys'     : ['Unit System', 'Unit Sys.', 'string', False, STR_FMT_DEFAULT, False],
    'unicon'      : ['Unit Conversion', 'Uni.Con.', 'string', False, STR_FMT_DEFAULT, False],
    'weight'      : ['Weight', 'Weight', 'float', False, STR_FMT_WEIGHT_FACTOR, True],
    'step_size'   : ['Step Size', 'StepSize', 'float', False, STR_FMT_PV_VAL, True],
    #'indiv_step_up': ['Individual Step-Up Control', '', 'N/A', False, STR_FMT_GUI, False],
    #'indiv_step_down': ['Individual Step-Down Control', '', 'N/A', False, STR_FMT_GUI, False],
    #'indiv_rollback': ['Individual Rollback Control', '', 'N/A', False, STR_FMT_GUI, False],
    #'indiv_ramp': ['Individual Ramp Control', 'Indiv.Ramp', 'BLOB', False, STR_FMT_GUI, True],
    ## Only apllicable for Snapshot below this point
    'cur_RB'      : ['Current Readback', 'Curr.RB', 'float', True, STR_FMT_PV_VAL, False],
    'cur_RB_pT'   : ['Current Readback PC Time', 'Curr.RB.PCTime', 'float', True, STR_FMT_TIMESTAMP, False],
    'cur_RB_iT'   : ['Current Readback IOC Time', 'Curr.RB.IOCTime', 'float', True, STR_FMT_TIMESTAMP, False],
    'cur_SP'      : ['Current Setpoint', 'Curr.SP', 'float', True, STR_FMT_PV_VAL, False],
    'cur_SP_pT'   : ['Current Setpoint PC Time', 'Curr.SP.PCTime', 'float', True, STR_FMT_TIMESTAMP, False],
    'cur_SP_iT'   : ['Current Setpoint IOC Time', 'Curr.SP.IOCTime', 'float', True, STR_FMT_TIMESTAMP, False],
    'ss_RB'       : ['Snapshot Readback', 'S.Shot.RB', 'float', True, STR_FMT_PV_VAL, False],
    'ss_RB_pT'    : ['Snapshot Readback PC Time', 'S.Shot.RB.PCTime', 'float', True, STR_FMT_TIMESTAMP, False],
    'ss_RB_iT'    : ['Snapshot Readback IOC Time', 'S.Shot.RB.IOCTime', 'float', True, STR_FMT_TIMESTAMP, False],
    'ss_SP'       : ['Snapshot Setpoint', 'S.Shot.SP', 'float', True, STR_FMT_PV_VAL, False],
    'ss_SP_pc'    : ['Snapshot PC Setpoint', 'S.Shot.SP@PC', 'float', True, STR_FMT_PV_VAL, False],
    'ss_SP_pT'    : ['Snapshot Setpoint PC Time', 'S.Shot.SP.PCTime', 'float', True, STR_FMT_TIMESTAMP, False],
    'ss_SP_iT'    : ['Snapshot Setpoint IOC Time', 'S.Shot.SP.IOCTime', 'float', True, STR_FMT_TIMESTAMP, False],
    'ini_RB'      : ['Initial Readback', 'Init.RB', 'float', True, STR_FMT_PV_VAL, False],
    'ini_RB_pT'   : ['Initial Readback PC Time', 'Init.RB.PCTime', 'float', True, STR_FMT_TIMESTAMP, False],
    'ini_RB_iT'   : ['Initial Readback IOC Time', 'Init.RB.IOCTime', 'float', True, STR_FMT_TIMESTAMP, False],
    'ini_SP'      : ['Initial Setpoint', 'Init.SP', 'float', True, STR_FMT_PV_VAL, False],
    'ini_SP_pT'   : ['Initial Setpoint PC Time', 'Init.SP.PCTime', 'float', True, STR_FMT_TIMESTAMP, False],
    'ini_SP_iT'   : ['Initial Setpoint IOC Time', 'Init.SP.IOCTime', 'float', True, STR_FMT_TIMESTAMP, False],
    'tar_SP'      : ['Target Setpoint', 'Target.SP', 'float', True, STR_FMT_PV_VAL, True],
    'D_cur_RB_ini_RB': ['(Current Readback)-(Initial Readback)','(Curr.RB)-(Init.RB)', 'float', True, STR_FMT_PV_VAL, False],
    'D_cur_SP_ini_SP': ['(Current Setpoint)-(Initial Setpoint)','(Curr.SP)-(Init.SP)', 'float', True, STR_FMT_PV_VAL, False],
    'D_cur_RB_cur_SP': ['(Current Readback)-(Current Setpoint)','(Curr.RB)-(Curr.SP)', 'float', True, STR_FMT_PV_VAL, False],
    'D_tar_SP_cur_SP': ['(Target Setpoint)-(Current Setpoint)', '(Target.SP)-(Curr.SP)', 'float', True, STR_FMT_PV_VAL, False],
    #'tolerance': ['Tolerance', 'Tolerance', 'float', True, STR_FMT_PV_VAL, False],
    #'hi_limit': ['High Limit', 'Hi.Lim', 'float', True, STR_FMT_PV_VAL, False],
    #'lo_limit': ['Low Limit', 'Lo.Lim', 'float', True, STR_FMT_PV_VAL, False],
    #'locked': ['Locked', 'Locked', 'bool', True, STR_FMT_DEFAULT, False],
    #'error': ['Error', 'Error', 'string', True, STR_FMT_DEFAULT, False],
    }

CHANNEL_PROP_DICT = {
    # (PROP_DICT's key) (Corresponding HLA Channel Attribute Name)
    'machine_name': '#machine_name', # Non-HLA Channel Attribute
    'lattice_name': '#lattice_name', # Non-HLA Channel Attribute
    'elem_name'   : 'name',
    'field'       : 'fields',
    'pvrb'        : 'pvrb',
    'pvsp'        : 'pvsp',
    'devname'     : 'devname',
    'cell'        : 'cell',
    'family'      : 'family',
    'girder'      : 'girder',
    'elem_group'  : 'group',
    'lat_index'   : 'index',
    'eff_len'     : 'length',
    'phys_len'    : 'phylen',
    'sb'          : 'sb',
    'se'          : 'se',
    'symmetry'    : 'symmetry',
    'unitsymb'    : '#unitsymb',# Non-HLA Channel Attribute
    'unitsys'     : '#unitsys', # Non-HLA Channel Attribute
    'unicon'      : '#unicon',  # Non-HLA Channel Attribute
    'golden'      : '#golden',  # Non-HLA Channel Attribute
    }

# Full list of all the available column names for
# Tuner Configuration Setup Dialog
ALL_PROP_KEYS_CONFIG_SETUP = sorted(
    [k for (k,v) in PROP_DICT.iteritems() if not v[ENUM_ONLY_FOR_SNAPSHOT]], key=str.lower)
ALL_PROP_KEYS_CONFIG_SETUP.remove('group_name')
ALL_PROP_KEYS_CONFIG_SETUP.insert(0,'group_name')
# 'group_name' must be the first column so that it can have a tree structure


# Full list of all the available column names for
# Main Tuner GUI
ALL_PROP_KEYS = sorted(PROP_DICT.keys(),key=str.lower)
ALL_PROP_KEYS.remove('group_name')
ALL_PROP_KEYS.insert(0,'group_name')
# 'group_name' must be the first column so that it can have a tree structure

FULL_DESCRIP_NAME_LIST = [PROP_DICT[name][ENUM_FULL_DESCRIP_NAME]
                          for name in ALL_PROP_KEYS]

EDITABLE_COL_KEYS = [k for (k,v) in PROP_DICT.iteritems() if v[ENUM_EDITABLE]]

DEFAULT_VISIBLE_COL_KEYS_FOR_CONFIG_SETUP = [
    'group_name',
    'channel_name',
    #'unitsymb',
    #'unitsys',
    'weight',
]

DEFAULT_VISIBLE_COL_KEYS_FOR_SNAPSHOT_VIEW = [
    'group_name',
    'channel_name',
    #'unitsymb',
    #'unitsys',
    'weight',
    'step_size',
    #'indiv_step_up',
    #'indiv_step_down',
    #'indiv_reset',
    #'indiv_ramp',
    'cur_RB',
    'cur_SP',
    'ss_RB',
    'ss_SP',
    'ss_SP_pc',
    'tar_SP',
    'D_tar_SP_cur_SP',
    'ini_RB',
    'ini_SP',
    'D_cur_RB_ini_RB',
    'D_cur_SP_ini_SP',
    'D_cur_RB_cur_SP',
    #'locked',
    #'error',
    ]

