from pathlib import Path
import gzip
import pickle
import tempfile

from .. import facility_d
from .. import machines
from .. import engines

_SEL_MODEL = None

_MODELS = {}
if 'models' in facility_d:
    for _submachine in list(facility_d['models']):
        _MODELS[_submachine] = {}
        for _engine_name in list(facility_d['models'][_submachine]):
            _MODELS[_submachine][_engine_name] = {
                _model_name: None for _model_name in
                facility_d['models'][_submachine][_engine_name]['available']}

def avail_names():
    """
    Return all available lattice model names for the currently selected
    submachine/engine.
    """

    _names_d = {subm: {} for subm in list(facility_d['models'])}

    for subm, v1 in facility_d['models'].items():
        for eng, v2 in v1.items():
            _names_d[subm][eng] = v2['available']

    return _names_d

def names():
    """
    Return all the loaded lattice model names for the currently selected
    submachine/engine.
    """

    submachine = machines.getMachineName()
    engine_name = engines.getEngineName()

    return [_model_name for _model_name, _model
            in _MODELS[submachine][engine_name].items()
            if _model is not None]

def load(submachine='', engine_name='', model_name=''):
    """
    Load the selected lattice model. If the model has been modified in the
    simulation mode, this function will reset to the specified design model.
    """

    if submachine == '':
        # Use the "submachine" currently loaded for "machines"
        try:
            submachine = machines.getMachineName()
        except:
            raise RuntimeError('Before you can load a model, you must load a (sub)machine.')

    if engine_name == '':
        engine_name = engines.getEngineName()
        if engine_name == '':
            engines.load() # Load default engine
            engine_name = engines.getEngineName()
    else:
        engines.load(engine_name=engine_name)

    if model_name == '':
        # Use the "default", if available. If not, use the first available model.
        model_name = facility_d['models'][submachine][engine_name].get('default', '')
        if model_name == '':
            try:
                model_name = avail_names()[submachine][engine_name][0]
            except:
                raise RuntimeError('Failed to automatically determine a model name')

    if model_name not in _MODELS[submachine][engine_name]:
        raise ValueError((
            f'Specified model "{model_name}" is not available.\n'
            f'Use ap.models.avail_names() to see all available model names.'))

    try:
        _MODELS[submachine][engine_name][model_name] = VariableModel(
            submachine, engine_name, model_name)
    except:
        print(f'ERROR: Model "{model_name}" could NOT be loaded')
        raise

def use(model_name):
    """
    Select the specified model for the currently selected submachine/engine.
    """

    submachine = machines.getMachineName()
    engine_name = engines.getEngineName()

    if _MODELS[submachine][engine_name][model_name] is None:
        load(model_name)

    if _MODELS[submachine][engine_name][model_name] is None:
        raise RuntimeError(
            f'Cannot use specified model "{model_name}" as loading failed.')
    else:
        global _SEL_MODEL
        _SEL_MODEL = _MODELS[submachine][engine_name][model_name]

def getModel():
    """
    Get the currently selected model.
    """

    return _SEL_MODEL

def modelget(model_maps):
    """"""

    return _SEL_MODEL.get(model_maps)

def modelput(model_maps, model_values):
    """"""

    return _SEL_MODEL.put(model_maps, model_values)

class VariableModel():
    """
    Only captures model propreties that can be varied during machine studies.
    The other static properties that could change should be represented by
    different base model files.
    """

    def __init__(self, submachine, engine_name, model_name):
        """Constructor"""

        self.submachine = submachine
        self.engine_name = engine_name
        self.model_name = model_name

        self.model_data_filepath = Path(machines.HLA_CONFIG_DIR).joinpath(
            'models', submachine, engine_name, f'{model_name}.pgz')

        self.make_tempdir(tempdir_path=None)

    def __del__(self):
        """"""

        self.remove_tempdir()

    def make_tempdir(self, tempdir_path=None):
        """"""

        self.tempdir = tempfile.TemporaryDirectory(
            prefix='tmpAphlaVarModel_', dir=tempdir_path)

    def remove_tempdir(self):
        """"""

        self.tempdir.cleanup()

    def get(self, name, field, *args, **kwargs):
        """"""

        pass
        #return [self.elems[m_d['elem_name']][m_d['property']]
                #for m_d in model_maps]

    def put(self, name, field, value, *args, **kwargs):
        """"""

        pass
        #assert len(model_maps) == len(model_values)

        #for m_d, val in zip(model_maps, model_values):
            #self.elems[m_d['elem_name']][m_d['property']] = val

        # When some properties are changed, use flags to indicate what lattice
        # properties need to be re-computed. For example, if you change quad K1
        # values, you will want to compute Twiss parameters as well as orbit.

class PyElegantVariableModel(VariableModel):
    """"""

    def __init__(self, submachine, engine_name, model_name):
        """"""

        super().__init__(submachine, engine_name, model_name)

        with gzip.GzipFile(self.model_data_filepath, 'rb') as f:
            self.LTE_filepath, self.used_beamline_name = pickle.load(f)
            self.elem_defs, self.beamline_defs = pickle.load(f)
            self.elem_name_index_maps = pickle.load(f)

        pe = self.engine = engines.getEngine()

        self.LTE = pe.ltemanager.Lattice(
            LTE_filepath=self.LTE_filepath,
            used_beamline_name=self.used_beamline_name)

        tmp = tempfile.NamedTemporaryFile(dir=self.tempdir.name, delete=True)
        temp_file_path_prefix = str(Path(tmp.name).resolve())
        tmp.close()

        self.temp_LTE_filepath = f'{temp_file_path_prefix}.lte'
        self.temp_ELE_filepath = f'{temp_file_path_prefix}.ele'

    def get(self, name, field):
        """"""

        elem_ind = self.elem_name_index_maps[name]
        elem_def = self.elem_defs[elem_ind]

        return self.LTE.parse_elem_properties(elem_def[2])[field]

    def put(self, name, field, value):
        """"""

        elem_ind = self.elem_name_index_maps[name]
        elem_def = self.elem_defs[elem_ind]

        mod_prop = {field: value}

        elem_def = self.LTE.modify_elem_def(elem_def, mod_prop)

        self.elem_defs[elem_ind] = elem_def

    def write_LTE(self):
        """"""

        self.LTE.write_LTE(self.temp_LTE_filepath, self.used_beamline_name,
                           self.elem_defs, self.beamline_defs)