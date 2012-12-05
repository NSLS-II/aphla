# Column Header Labels (read-only unless noted as writeable)
COL_GROUP_NAME          = 'Group Name' # writeable
COL_KNOB_NAME           = 'Knob Name' # writeable only for Config Setup Dialog
COL_ELEMENT_NAME        = 'Elem.Name'
COL_FIELD_NAME          = 'Field'
COL_PV_READ_NAME        = 'PV-Read'
COL_PV_SETP_NAME        = 'PV-Set'
COL_DEV_NAME            = 'Dev.Name'
COL_CELL                = 'Cell'
COL_FAMILY              = 'Family'
COL_GIRDER              = 'Girder'
COL_ELEMENT_GROUP       = 'Elem.Group'
COL_LATTICE_INDEX       = 'Lat.Index'
COL_EFFECTIVE_LENGTH    = 'Eff.Len.'
COL_PHYSICAL_LENGTH     = 'Phys.Len.'
COL_S_BEGINNING         = 'sb'
COL_S_END               = 'se'
COL_SYMMETRY            = 'Symmetry'
COL_VIRTUAL             = 'Virtual'
COL_SEQUENCE            = 'Sequence'
COL_PV_UNIT             = 'PV Unit'

# Full list of all the available column names for
# Tuner Configuration Setup Dialog
COL_ALL_NAMES_CONFIG_SETUP = [locals()[s] for s in dir() 
                              if s.startswith('COL_')]
if len(COL_ALL_NAMES_CONFIG_SETUP) != \
   len(set(COL_ALL_NAMES_CONFIG_SETUP)):
    raise Exception, \
          'Duplicate column name constant variables found.'

COL_WEIGHT              = 'Weight' # writeable
COL_NORMALIZED_WEIGHT   = 'N.Weight'
COL_STEP_SIZE           = 'Step Size' # writeable
COL_READING             = 'Reading'
COL_SETPOINT            = 'Setpoint'
COL_READ_TSTAMP         = 'Read T.Stamp'
COL_SETP_TSTAMP         = 'Setp T.Stamp'
COL_SNAPSHOT_READ       = 'S.Shot Read'
COL_SNAPSHOT_SETP       = 'S.Shot Setp'
COL_SNAPSHOT_DESCRIP    = 'S.Shot Descrip.'
COL_SNAPSHOT_READ_TSTAMP= 'S.Shot Read T.Stamp'
COL_SNAPSHOT_SETP_TSTAMP= 'S.Shot Setp T.Stamp'
COL_TARGET_SETP         = 'Target Setp' # writeable (manually typed, or snapshot setp automatically transfered)
COL_START_READ          = 'Start Read'
COL_START_SETP          = 'Start Setp'
COL_START_READ_TSTAMP   = 'Start Read T.Stamp'
COL_START_SETP_TSTAMP   = 'Start Setp T.Stamp'
COL_CUM_READ_CHANGE     = 'Cumul. Read Change'
COL_CUM_SETP_CHANGE     = 'Cumul. Setp Change'
COL_DIFF_READ_BTW_SETP  = '(Reading)-(Setpoint)'
COL_DIFF_TARGET_BTW_SETP= '(Target Setp.)-(Curr.Setp.)'
COL_TOLERANCE           = 'Tolerance'
COL_HI_LIMIT            = 'Hi Limit'
COL_LO_LIMIT            = 'Lo Limit'
COL_LOCKED              = 'Locked'
COL_ERROR               = 'ERROR'

# Full list of all the available column names for Tuner GUI
COL_ALL_NAMES = [locals()[s] for s in dir() 
                 if s.startswith('COL_') and 
                 (s != 'COL_ALL_NAMES_CONFIG_SETUP')]

if len(COL_ALL_NAMES) != len(set(COL_ALL_NAMES)):
    raise Exception, \
          'Duplicate column name constant variables found.'

# Following columns cannot be hidden
ALWAYS_VISIBLE_COL_LIST = [
    COL_KNOB_NAME,
    COL_GROUP_NAME
]

if len(ALWAYS_VISIBLE_COL_LIST) != \
   len(set(ALWAYS_VISIBLE_COL_LIST)):
    raise Exception, \
          'Duplicate column names found in ALWAYS_VISIBLE_COL_LIST.'

if [s for s in ALWAYS_VISIBLE_COL_LIST \
    if s not in COL_ALL_NAMES]:
    raise Exception, \
          'ALWAYS_VISIBLE_COL_LIST contains column names not in COL_ALL_NAMES.'

# Default visible column name list for Tuner Configuration
# Setup Dialog in the order of appearance
DEFAULT_VISIBLE_COL_LIST_CONFIG_SETUP = [
    COL_KNOB_NAME,
    COL_GROUP_NAME,
    COL_PV_READ_NAME,
    COL_PV_SETP_NAME,
    COL_PV_UNIT
]

if len(DEFAULT_VISIBLE_COL_LIST_CONFIG_SETUP) != \
   len(set(DEFAULT_VISIBLE_COL_LIST_CONFIG_SETUP)):
    raise Exception, \
          'Duplicate column names found in DEFAULT_VISIBLE_COL_LIST_CONFIG_SETUP.'

if [s for s in DEFAULT_VISIBLE_COL_LIST_CONFIG_SETUP \
    if s not in COL_ALL_NAMES_CONFIG_SETUP]:
    raise Exception, \
          'COL_ALL_NAMES_CONFIG_SETUP must contain all names DEFAULT_VISIBLE_COL_LIST_CONFIG_SETUP.'

if [s for s in ALWAYS_VISIBLE_COL_LIST \
    if s not in DEFAULT_VISIBLE_COL_LIST_CONFIG_SETUP]:
    raise Exception, \
          'DEFAULT_VISIBLE_COL_LIST_CONFIG_SETUP must contain all names in ALWAYS_VISIBLE_COL_LIST.'


# Default visible column name list for Tuner GUI
# in the order of appearance
DEFAULT_VISIBLE_COL_LIST = [
    COL_KNOB_NAME,
    COL_GROUP_NAME,
    COL_WEIGHT,
    COL_NORMALIZED_WEIGHT,
    COL_STEP_SIZE,
    COL_PV_UNIT,
    COL_READING,
    COL_SETPOINT,
    COL_START_READ,
    COL_START_SETP,
    COL_CUM_READ_CHANGE,
    COL_CUM_SETP_CHANGE,
    COL_SNAPSHOT_READ,
    COL_SNAPSHOT_SETP,
    COL_SNAPSHOT_DESCRIP,
    COL_TARGET_SETP
]

if len(DEFAULT_VISIBLE_COL_LIST) != \
   len(set(DEFAULT_VISIBLE_COL_LIST)):
    raise Exception, \
          'Duplicate column names found in DEFAULT_VISIBLE_COL_LIST.'

if [s for s in DEFAULT_VISIBLE_COL_LIST \
    if s not in COL_ALL_NAMES]:
    raise Exception, \
          'COL_ALL_NAMES must contain all names DEFAULT_VISIBLE_COL_LIST.'

if [s for s in ALWAYS_VISIBLE_COL_LIST \
    if s not in DEFAULT_VISIBLE_COL_LIST]:
    raise Exception, \
          'DEFAULT_VISIBLE_COL_LIST must contain all names in ALWAYS_VISIBLE_COL_LIST.'


max_decimals_for_weight_factor = 8
max_decimals_for_length_meter = 6
max_decimals_for_pv_val = 4

STR_FORMAT_WEIGHT_FACTOR = \
    '%.' + str(max_decimals_for_weight_factor) + 'g'
STR_FORMAT_LENGTH_METER = \
    '%.' + str(max_decimals_for_length_meter) + 'g'
STR_FORMAT_PV_VAL = \
    '%.' + str(max_decimals_for_pv_val) + 'g'

DICT_COL_NAME = {         #Class Name, Property Name, String Fromat
    COL_GROUP_NAME       :['KnobGroup','name','%s'],
    COL_KNOB_NAME        :['Knob','name','%s'],
    COL_ELEMENT_NAME     :['Knob','elem_name','%s'],
    COL_FIELD_NAME       :['Knob','field_name','%s'],
    COL_PV_READ_NAME     :['Knob','pvrb','%s'],
    COL_PV_SETP_NAME     :['Knob','pvsp','%s'],
    COL_DEV_NAME         :['Knob','devname','%s'],
    COL_CELL             :['Knob','cell','%s'],
    COL_FAMILY           :['Knob','family','%s'],
    COL_GIRDER           :['Knob','girder','%s'],
    COL_ELEMENT_GROUP    :['Knob','group','%s'],
    COL_LATTICE_INDEX    :['Knob','index','%d'],
    COL_EFFECTIVE_LENGTH :['Knob','length',
                           STR_FORMAT_LENGTH_METER],
    COL_PHYSICAL_LENGTH  :['Knob','phylen',
                           STR_FORMAT_LENGTH_METER],
    COL_S_BEGINNING      :['Knob','sb',
                           STR_FORMAT_LENGTH_METER],
    COL_S_END            :['Knob','se',
                           STR_FORMAT_LENGTH_METER],
    COL_SYMMETRY         :['Knob','symmetry','%s'],
    COL_VIRTUAL          :['Knob','virtual','%s'],
    COL_SEQUENCE         :['Knob','sequence','%s'],
    COL_WEIGHT           :['KnobGroup','weight',
                           STR_FORMAT_WEIGHT_FACTOR],
    COL_NORMALIZED_WEIGHT:['KnobGroupList','normalized_weight_list',
                           STR_FORMAT_WEIGHT_FACTOR],
    COL_STEP_SIZE        :['KnobGroupList','step_size_list',
                           STR_FORMAT_PV_VAL],
    COL_PV_UNIT          :[None, '', '%s'],
    COL_READING          :['Knob','pvrb_val',
                           STR_FORMAT_PV_VAL],
    COL_SETPOINT         :['Knob','pvsp_val',
                           STR_FORMAT_PV_VAL],
    COL_READ_TSTAMP      :['Knob','pvrb_val_time_stamp','timestamp'],
    COL_SETP_TSTAMP      :['Knob','pvsp_val_time_stamp','timestamp'],
    COL_SNAPSHOT_READ    :[None, '', '%s'],
    COL_SNAPSHOT_SETP    :[None, '', '%s'],
    COL_SNAPSHOT_DESCRIP :[None, '', '%s'],
    COL_SNAPSHOT_READ_TSTAMP:[None, '', '%s'],
    COL_SNAPSHOT_SETP_TSTAMP:[None, '', '%s'],
    COL_TARGET_SETP      :[None, '', '%s'],
    COL_START_READ       :['TunerModel', 'start_PV_read', STR_FORMAT_PV_VAL],
    COL_START_SETP       :['TunerModel', 'start_PV_setp', STR_FORMAT_PV_VAL],
    COL_START_READ_TSTAMP:[None, '', '%s'],
    COL_START_SETP_TSTAMP:[None, '', '%s'],
    COL_CUM_READ_CHANGE  :[None, '', '%s'],
    COL_CUM_SETP_CHANGE  :[None, '', '%s'],
    COL_DIFF_READ_BTW_SETP:[None, '', '%s'],
    COL_DIFF_TARGET_BTW_SETP:[None, '', '%s'],
    COL_TOLERANCE        :[None, '', '%s'],
    COL_HI_LIMIT         :[None, '', '%s'],
    COL_LO_LIMIT         :[None, '', '%s'],
    COL_LOCKED           :[None, '', '%s'],
    COL_ERROR            :[None, '', '%s']
}
