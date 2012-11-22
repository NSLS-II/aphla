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
    'group_name': ['Group Name', 'GroupName', 'string', False, STR_FMT_DEFAULT, True],
    'channel_name': ['Channel Name', 'Channel Name', 'string', False, STR_FMT_DEFAULT, False], # can be either a channel name (elem_name.field_name) or PV tuple (PV_readback, PV_setpoint)
    'elem_name': ['Element Name', 'Elem.Name', 'string', False, STR_FMT_DEFAULT, False],
    'field': ['Field', 'Field', 'string', False, STR_FMT_DEFAULT, False],
    'pvrb': ['PV-RB Name', 'PVRB', 'string', False, STR_FMT_DEFAULT, False],
    'pvsp': ['PV-SP Name', 'PVSP', 'string', False, STR_FMT_DEFAULT, False],
    'devname': ['Device Name', 'Dev.Name', 'string', False, STR_FMT_DEFAULT, False],
    'cell': ['Cell', 'Cell', 'string', False, STR_FMT_DEFAULT, False],
    'family': ['Family', 'Family', 'string', False, STR_FMT_DEFAULT, False],
    'girder': ['Girder', 'Girder', 'string', False, STR_FMT_DEFAULT, False],
    'elem_group': ['Element Group', 'Elem.Group', 'string', False, STR_FMT_DEFAULT, False],
    'lat_index': ['Lattice Index', 'Lat.Index', 'int', False, STR_FMT_DEFAULT, False],
    'eff_len': ['Effective Length', 'Eff.Len.', 'float', False, STR_FMT_LENGTH_METER, False],
    'phys_len': ['Physical Length', 'Phys.Len.', 'float', False, STR_FMT_LENGTH_METER, False],
    'sb': ['s(beginning)', 'sb', 'float', False, STR_FMT_LENGTH_METER, False],
    'se': ['s(end)', 'se', 'float', False, STR_FMT_LENGTH_METER, False],
    'symmetry': ['Symmetry', 'Symmetry', 'string', False, STR_FMT_DEFAULT, False],
    #'unit': ['Unit', 'Unit', 'string', False, STR_FMT_DEFAULT, False],
    'weight': ['Weight', 'Weight', 'float', False, STR_FMT_WEIGHT_FACTOR, True],
    'step_size': ['Step Size', 'StepSize', 'float', False, STR_FMT_PV_VAL, True],
    #'indiv_step_up': ['Individual Step-Up Control', '', 'N/A', False, STR_FMT_GUI, False],
    #'indiv_step_down': ['Individual Step-Down Control', '', 'N/A', False, STR_FMT_GUI, False],
    #'indiv_rollback': ['Individual Rollback Control', '', 'N/A', False, STR_FMT_GUI, False],
    #'indiv_ramp': ['Individual Ramp Control', 'Indiv.Ramp', 'BLOB', False, STR_FMT_GUI, True],
    ## Only apllicable for Snapshot below this point
    'curr_RB': ['Current Readback', 'Curr.RB', 'float', True, STR_FMT_PV_VAL, False],
    #'curr_RB_pc_time': ['Current Readback PC Time', 'Curr.RB.PCTime', 'float', True, STR_FMT_TIMESTAMP, False],
    'curr_RB_ioc_time': ['Current Readback IOC Time', 'Curr.RB.IOCTime', 'float', True, STR_FMT_TIMESTAMP, False],
    'curr_SP': ['Current Setpoint', 'Curr.SP', 'float', True, STR_FMT_PV_VAL, False],
    #'curr_SP_pc_time': ['Current Setpoint PC Time', 'Curr.SP.PCTime', 'float', True, STR_FMT_TIMESTAMP, False],
    'curr_SP_ioc_time': ['Current Setpoint IOC Time', 'Curr.SP.IOCTime', 'float', True, STR_FMT_TIMESTAMP, False],
    'sshot_RB': ['Snapshot Readback', 'S.Shot.RB', 'float', True, STR_FMT_PV_VAL, False],
    #'sshot_RB_pc_time': ['Snapshot Readback PC Time', 'S.Shot.RB.PCTime', 'float', True, STR_FMT_TIMESTAMP, False],
    'sshot_RB_ioc_time': ['Snapshot Readback IOC Time', 'S.Shot.RB.IOCTime', 'float', True, STR_FMT_TIMESTAMP, False],
    'sshot_SP': ['Snapshot Setpoint', 'S.Shot.SP', 'float', True, STR_FMT_PV_VAL, False],
    #'sshot_SP_pc_time': ['Snapshot Setpoint PC Time', 'S.Shot.SP.PCTime', 'float', True, STR_FMT_TIMESTAMP, False],
    'sshot_SP_ioc_time': ['Snapshot Setpoint IOC Time', 'S.Shot.SP.IOCTime', 'float', True, STR_FMT_TIMESTAMP, False],
    'target_SP': ['Target Setpoint', 'Target.SP', 'float', True, STR_FMT_PV_VAL, True],
    'D_target_SP_curr_SP': ['(Target Setpoint)-(Current Setpoint)', '(Target.SP)-(Curr.SP)', 'float', True, STR_FMT_PV_VAL, False],
    'init_RB': ['Initial Readback', 'Init.RB', 'float', True, STR_FMT_PV_VAL, False],
    #'init_RB_pc_time': ['Initial Readback PC Time', 'Init.RB.PCTime', 'float', True, STR_FMT_TIMESTAMP, False],
    'init_RB_ioc_time': ['Initial Readback IOC Time', 'Init.RB.IOCTime', 'float', True, STR_FMT_TIMESTAMP, False],
    'init_SP': ['Initial Setpoint', 'Init.SP', 'float', True, STR_FMT_PV_VAL, False],
    #'init_SP_pc_time': ['Initial Setpoint PC Time', 'Init.SP.PCTime', 'float', True, STR_FMT_TIMESTAMP, False],
    'init_SP_ioc_time': ['Initial Setpoint IOC Time', 'Init.SP.IOCTime', 'float', True, STR_FMT_TIMESTAMP, False],
    'D_curr_RB_init_RB': ['(Current Readback)-(Initial Readback)','(Curr.RB)-(Init.RB)', 'float', True, STR_FMT_PV_VAL, False],
    'D_curr_SP_init_SP': ['(Current Setpoint)-(Initial Setpoint)','(Curr.SP)-(Init.SP)', 'float', True, STR_FMT_PV_VAL, False],
    'D_curr_RB_curr_SP': ['(Current Readback)-(Current Setpoint)','(Curr.RB)-(Curr.SP)', 'float', True, STR_FMT_PV_VAL, False],
    #'tolerance': ['Tolerance', 'Tolerance', 'float', True, STR_FMT_PV_VAL, False],
    #'hi_limit': ['High Limit', 'Hi.Lim', 'float', True, STR_FMT_PV_VAL, False],
    #'lo_limit': ['Low Limit', 'Lo.Lim', 'float', True, STR_FMT_PV_VAL, False],
    #'locked': ['Locked', 'Locked', 'bool', True, STR_FMT_DEFAULT, False],
    #'error': ['Error', 'Error', 'string', True, STR_FMT_DEFAULT, False],
    }

CHANNEL_PROP_DICT = {
    # (PROP_DICT's key) (Corresponding HLA Channel Attribute Name)
    'elem_name': 'name',
    'field': 'fields',
    'pvrb': 'pvrb',
    'pvsp': 'pvsp',
    'devname': 'devname',
    'cell': 'cell',
    'family': 'family',
    'girder': 'girder',
    'elem_group': 'group',
    'lat_index': 'index',
    'eff_len': 'length',
    'phys_len': 'phylen',
    'sb': 'sb',
    'se': 'se',
    'symmetry': 'symmetry',
    }

#COL_GROUP_NAME       = 'Group Name' # editable
#COL_CHANNEL_NAME     = 'Channel Name' # can be either a channel name (elem_name.field_name) or PV tuple (PV_readback, PV_setpoint)
#COL_ELEM_NAME        = 'Elem. Name'
#COL_FIELD            = 'Field'
#COL_PV_RB_NAME       = 'PV-RB'
#COL_PV_SP_NAME       = 'PV-SP'
#COL_DEV_NAME         = 'Dev.Name'
#COL_CELL             = 'Cell'
#COL_FAMILY           = 'Family'
#COL_GIRDER           = 'Girder'
#COL_ELEMENT_GROUP    = 'Elem.Group'
#COL_LATTICE_INDEX    = 'Lat.Index'
#COL_EFFECTIVE_LENGTH = 'Eff.Len.'
#COL_PHYSICAL_LENGTH  = 'Phys.Len.'
#COL_S_BEGINNING      = 'sb'
#COL_S_END            = 'se'
#COL_SYMMETRY         = 'Symmetry'
##COL_UNIT             = 'Unit'
#COL_WEIGHT           = 'Weight' # editable

# Full list of all the available column names for
# Tuner Configuration Setup Dialog
ALL_PROP_KEYS_CONFIG_SETUP = sorted(
    [k for (k,v) in PROP_DICT.iteritems() if not v[ENUM_ONLY_FOR_SNAPSHOT]], key=str.lower)
#ALL_COL_NAMES_CONFIG_SETUP = [locals()[s] for s in dir()
                              #if s.startswith('COL_')]
#ALL_COL_NAMES_CONFIG_SETUP.remove(COL_GROUP_NAME)
#ALL_COL_NAMES_CONFIG_SETUP.insert(0,COL_GROUP_NAME) # COL_GROUP_NAME must be 1st in column so that it can have a tree structure


#COL_NORMALIZED_WEIGHT   = 'Norm.Weight'
#COL_STEP_SIZE           = 'Step Size' # editable
#COL_CURR_RB             = 'Current RB'
#COL_CURR_SP             = 'Current SP'
#COL_CURR_RB_TIME        = 'Curr. RB Time'
#COL_CURR_SP_TIME        = 'Curr. SP Time'
#COL_SNAPSHOT_RB         = 'S.Shot RB'
#COL_SNAPSHOT_SP         = 'S.Shot SP'
#COL_SNAPSHOT_RB_TIME    = 'S.Shot RB Time'
#COL_SNAPSHOT_SP_TIME    = 'S.Shot SP Time'
#COL_TARGET_SP           = 'Target SP' # editable
#COL_D_TARGET_SP_CURR_SP = '(TargetSP)-(Curr.SP)'
#COL_INIT_RB             = 'Init. RB'
#COL_INIT_SP             = 'Init. SP'
#COL_INIT_RB_TIME        = 'Init.RB Time'
#COL_INIT_SP_TIME        = 'Init.SP Time'
#COL_D_CURR_RB_INIT_RB   = '(Curr.RB)-(Init.RB)'
#COL_D_CURR_SP_INIT_SP   = '(Curr.SP)-(Init.SP)'
#COL_D_CURR_RB_CURR_SP   = '(Curr.RB)-(Curr.SP)'
#COL_TOLERANCE           = 'Tolerance'
#COL_HI_LIMIT            = 'Hi Limit'
#COL_LO_LIMIT            = 'Lo Limit'
#COL_LOCKED              = 'Locked'
#COL_ERROR               = 'ERROR'

# Full list of all the available column names for
# Main Tuner GUI
ALL_PROP_KEYS = sorted(PROP_DICT.keys(),key=str.lower)
ALL_PROP_KEYS.remove('group_name')
ALL_PROP_KEYS.insert(0,'group_name')

FULL_DESCRIP_NAME_LIST = [PROP_DICT[name][ENUM_FULL_DESCRIP_NAME]
                          for name in ALL_PROP_KEYS]

#ALL_COL_NAMES = [locals()[s] for s in dir()
                 #if s.startswith('COL_')]

#if len(ALL_COL_NAMES) != len(list(set(ALL_COL_NAMES))):
    #raise ValueError('Duplicate column names detected')

EDITABLE_COL_KEYS = [k for (k,v) in PROP_DICT.iteritems() if v[ENUM_EDITABLE]]
#EDITABLE_COL_NAME_LIST = [
    #COL_GROUP_NAME,
    #COL_WEIGHT,
    #COL_STEP_SIZE,
    #COL_TARGET_SP,
#] 

DEFAULT_VISIBLE_COL_KEYS_FOR_CONFIG_SETUP = [
    'group_name',
    'channel_name',
    #'unit',
    'weight',
]
#DEFAULT_VISIBLE_COL_LIST_CONFIG_SETUP = [
    #COL_GROUP_NAME,
    #COL_CHANNEL_NAME,
    ##COL_UNIT,
    #COL_WEIGHT,
#]

DEFAULT_VISIBLE_COL_KEYS_FOR_SNAPSHOT_VIEW = [
    'group_name',
    'channel_name',
    #'unit',
    'weight',
    'step_size',
    #'indiv_step_up',
    #'indiv_step_down',
    #'indiv_rollback',
    #'indiv_ramp',
    'curr_RB',
    'curr_SP',
    'sshot_RB',
    'sshot_SP',
    'target_SP',
    'D_target_SP_curr_SP',
    'init_RB',
    'init_SP',
    'D_curr_RB_init_RB',
    'D_curr_SP_init_SP',
    'D_curr_RB_curr_SP',
    #'locked',
    #'error',
    ]

#DEFAULT_VISIBLE_COL_LIST_FOR_SNAPSHOT_VIEW = \
    #DEFAULT_VISIBLE_COL_LIST_CONFIG_SETUP + [
        #COL_NORMALIZED_WEIGHT,
        #COL_STEP_SIZE,
        #COL_CURR_RB,
        #COL_CURR_SP,
        #COL_SNAPSHOT_RB,
        #COL_SNAPSHOT_SP,
        #COL_TARGET_SP,
        #COL_D_TARGET_SP_CURR_SP,
        #COL_INIT_RB,
        #COL_INIT_SP,
        #COL_D_CURR_RB_INIT_RB,
        #COL_D_CURR_SP_INIT_SP,
        #COL_D_CURR_RB_CURR_SP,
        ##COL_LOCKED,
        ##COL_ERROR,
    #]

DEFAULT_VISIBLE_COL_KEYS_FOR_CONFIG_VIEW = \
    DEFAULT_VISIBLE_COL_KEYS_FOR_SNAPSHOT_VIEW[:]
DEFAULT_VISIBLE_COL_KEYS_FOR_CONFIG_VIEW.remove('sshot_RB')
DEFAULT_VISIBLE_COL_KEYS_FOR_CONFIG_VIEW.remove('sshot_SP')

#DEFAULT_VISIBLE_COL_LIST_FOR_CONFIG_VIEW = \
    #DEFAULT_VISIBLE_COL_LIST_FOR_SNAPSHOT_VIEW[:]
#DEFAULT_VISIBLE_COL_LIST_FOR_CONFIG_VIEW.remove(COL_SNAPSHOT_RB)
#DEFAULT_VISIBLE_COL_LIST_FOR_CONFIG_VIEW.remove(COL_SNAPSHOT_SP)

####
#max_decimals_for_weight_factor = 8
#max_decimals_for_length_meter = 6
#max_decimals_for_pv_val = 4


#STR_FORMAT_WEIGHT_FACTOR = \
    #':.' + str(max_decimals_for_weight_factor) + 'g'
#STR_FORMAT_LENGTH_METER = \
    #':.' + str(max_decimals_for_length_meter) + 'g'
#STR_FORMAT_PV_VAL = \
    #':.' + str(max_decimals_for_pv_val) + 'g'

#ENUM_LEVEL = 0
#ENUM_PROP_NAME = 1
#ENUM_STR_FORMAT = 2
#DICT_COL = { #Level, Property Key, String Format
    #COL_GROUP_NAME: ['group','name',':s'],
    #COL_CHANNEL_NAME: ['channel','channel_name',':s'],
    #COL_ELEM_NAME: ['channel','name',':s'],
    #COL_FIELD: ['channel','field',':s'],
    #COL_PV_RB_NAME: ['channel','pvrb',':s'],
    #COL_PV_SP_NAME: ['channel','pvsp',':s'],
    #COL_DEV_NAME: ['channel','devname',':s'],
    #COL_CELL: ['channel','cell',':s'],
    #COL_FAMILY: ['channel','family',':s'],
    #COL_GIRDER: ['channel','girder',':s'],
    #COL_ELEMENT_GROUP: ['channel','group',':s'],
    #COL_LATTICE_INDEX: ['channel','index',':d'],
    #COL_EFFECTIVE_LENGTH: ['channel','length',STR_FORMAT_LENGTH_METER],
    #COL_PHYSICAL_LENGTH: ['channel','phylen',STR_FORMAT_LENGTH_METER],
    #COL_S_BEGINNING: ['channel','sb',STR_FORMAT_LENGTH_METER],
    #COL_S_END: ['channel','se',STR_FORMAT_LENGTH_METER],
    #COL_SYMMETRY: ['channel','symmetry',':s'],
    ##COL_UNIT: ['channel','unit',':s'],
    #COL_WEIGHT: ['group','weight',STR_FORMAT_WEIGHT_FACTOR],
    #COL_NORMALIZED_WEIGHT: ['group','normalized_weight_list',STR_FORMAT_WEIGHT_FACTOR],
    #COL_STEP_SIZE: ['group','step_size_list',STR_FORMAT_PV_VAL],
    #COL_CURR_RB: ['channel','curr_RB',STR_FORMAT_PV_VAL],
    #COL_CURR_SP: ['channel','curr_SP',STR_FORMAT_PV_VAL],
    #COL_CURR_RB_TIME: ['channel','curr_RB_time','timestamp'],
    #COL_CURR_SP_TIME: ['channel','curr_SP_time','timestamp'],
    #COL_SNAPSHOT_RB: ['channel','snapshot_RB',STR_FORMAT_PV_VAL],
    #COL_SNAPSHOT_SP: ['channel','snapshot_SP',STR_FORMAT_PV_VAL],
    #COL_SNAPSHOT_RB_TIME: ['channel','snapshot_RB_time','timestamp'],
    #COL_SNAPSHOT_SP_TIME: ['channel','snapshot_SP_time','timestamp'],
    #COL_TARGET_SP: ['channel','target_SP',STR_FORMAT_PV_VAL],
    #COL_D_TARGET_SP_CURR_SP: ['channel','D_target_SP_curr_SP',STR_FORMAT_PV_VAL],
    #COL_INIT_RB: ['channel','init_RB',STR_FORMAT_PV_VAL],
    #COL_INIT_SP: ['channel','init_SP',STR_FORMAT_PV_VAL],
    #COL_INIT_RB_TIME: ['channel','init_RB_time','timestamp'],
    #COL_INIT_SP_TIME: ['channel','init_SP_time','timestamp'],
    #COL_D_CURR_RB_INIT_RB: ['channel','D_curr_RB_init_RB',STR_FORMAT_PV_VAL],
    #COL_D_CURR_SP_INIT_SP: ['channel','D_curr_SP_init_SP',STR_FORMAT_PV_VAL],
    #COL_D_CURR_RB_CURR_SP: ['channel','D_curr_RB_curr_SP',STR_FORMAT_PV_VAL],
    ##COL_TOLERANCE: ['channel','',STR_FORMAT_PV_VAL],
    ##COL_HI_LIMIT: ['channel','',STR_FORMAT_PV_VAL],
    ##COL_LO_LIMIT: ['channel','',STR_FORMAT_PV_VAL],
    ##COL_LOCKED: ['channel','',':s'],
    ##COL_ERROR: ['channel','',':s'],
    #}

#if set(DICT_COL.keys()) != set(ALL_COL_NAMES):
    #raise ValueError('DICT_COL keys must match with ALL_COL_NAMES')

#GROUP_LEVEL_COL_LIST = [k for (k,v) in DICT_COL.iteritems()
                        #if v[0] == 'group']
#CHANNEL_LEVEL_COL_LIST = [k for (k,v) in DICT_COL.iteritems()
                          #if v[0] == 'channel']
