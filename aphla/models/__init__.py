from pathlib import Path
import gzip
import pickle
import tempfile

import numpy as np

from .. import facility_d
from .. import machines
from .. import engines
from ..apdata import TwissData

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

    model_config = facility_d['models'][submachine][engine_name]

    if model_name == '':
        # Use the "default", if available. If not, use the first available model.
        model_name = model_config.get('default', '')
        if model_name == '':
            try:
                model_name = avail_names()[submachine][engine_name][0]
            except:
                raise RuntimeError('Failed to automatically determine a model name')

    if model_name not in _MODELS[submachine][engine_name]:
        raise ValueError((
            f'Specified model "{model_name}" is not available.\n'
            f'Use ap.models.avail_names() to see all available model names.'))

    if engine_name == 'pyelegant':
        model_class = PyElegantVariableModel
        model_kwargs = {'N_KICKS': model_config.get('N_KICKS', None)}
    else:
        raise NotImplementedError

    try:
        _MODELS[submachine][engine_name][model_name] = model_class(
            submachine, engine_name, model_name, **model_kwargs)
    except:
        print(f'ERROR: Model "{model_name}" could NOT be loaded')
        raise

    use(model_name) # Select the loaded model

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

def modelget(mv):
    """"""

    if _SEL_MODEL is None:
        raise RuntimeError('You must first load a model before you can call "get"')

    return _SEL_MODEL.get(mv)

def modelput(mv, value):
    """"""

    return _SEL_MODEL.put(mv, value)

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
            facility_d['name'],
            'models',
            submachine,
            engine_name,
            f'{model_name}.pgz')

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

    def get(self, *args, **kwargs):
        """"""

        pass

    def put(self, *args, **kwargs):
        """"""

        pass

        # When some properties are changed, use flags to indicate what lattice
        # properties need to be re-computed. For example, if you change quad K1
        # values, you will want to compute Twiss parameters as well as orbit.

class PyElegantVariableModel(VariableModel):
    """"""

    def __init__(self, submachine, engine_name, model_name, N_KICKS=None):
        """"""

        super().__init__(submachine, engine_name, model_name)

        self.N_KICKS = N_KICKS

        with gzip.GzipFile(self.model_data_filepath, 'rb') as f:
            self.base_LTE_filepath, self.base_used_beamline_name = pickle.load(f)
            self.LTE_filepath, self.used_beamline_name = pickle.load(f)
            # ^ Only informational purpose only to show which LTE file
            #   the magnet setpoints included in this file comes from. For actual
            #   LTE loading, the "base_*" properties will be used.
            self.elem_defs, self.beamline_defs = pickle.load(f)
            self.elem_defs_index_maps = pickle.load(f)
            # ^ Mapping between element names and the indexes for the element
            #   definition list.
            try:
                opt_init_model_data = pickle.load(f)
            except EOFError:
                opt_init_model_data = {}


        pe = self.engine = engines.getEngine()

        self.LTE = pe.ltemanager.Lattice(
            LTE_filepath=self.base_LTE_filepath,
            used_beamline_name=self.base_used_beamline_name)

        tmp = tempfile.NamedTemporaryFile(dir=self.tempdir.name, delete=True)
        temp_file_path_prefix = str(Path(tmp.name).resolve())
        tmp.close()

        self.temp_fielpaths = {}
        self.temp_fielpaths['LTE'] = f'{temp_file_path_prefix}.lte'
        self.temp_fielpaths['ELE'] = f'{temp_file_path_prefix}.ele'
        self.temp_fielpaths['TWI'] = f'{temp_file_path_prefix}.twipgz'

        d = opt_init_model_data.get('flat_elems_index_maps', None)
        if d is not None:
            # Mapping between element names and the indexes for the global
            # flat element list of the specified beamline for each type of
            # PyELEGANT's ".pgz" result files.
            self.flat_elems_index_maps = d
        else:
            # Placeholder for the mapping. Missing mapping will be added
            # to this on demand.
            self.flat_elems_index_maps = dict(closed_orbit={}, twiss={})

        self.need_LTE_write = True

        self.need_recalc = dict(closed_orbit=True, twiss=True, tbt=True)
        self._raw = dict(closed_orbit=None, twiss=None, tbt=None)

        d = opt_init_model_data.get('raw_calc_data', None)
        if d is not None:
            for k, v in d.items():
                self._raw[k] = v
                self.need_recalc[k] = False

        self._twiss = TwissData(f'{submachine}/{engine_name}/{model_name}')
        if self._raw['twiss'] is not None:
            self._update_TwissData_obj()

        self._proc = dict(orm=None) # TODO: ORM data

        d = opt_init_model_data.get('proc_calc_data', None)
        if d is not None:
            for k, v in d.items():
                self._proc[k] = v

    def get(self, mv_list):
        """"""

        values = []

        for mv in mv_list:
            d = mv['pyelegant']
            name = d['elem_name']
            field = d['property']

            if not name.startswith('!'):
                elem_ind = self.elem_defs_index_maps[name]
                elem_def = self.elem_defs[elem_ind]
                elem_type = elem_def[1]
                elem_prop = self.LTE.parse_elem_properties(elem_def[2])

                info = self._get_elem_type_field_info(elem_type, field, 'readback')

                if info['calc_prop'] is None:
                    v = elem_prop.get(field, info['default_val'])
                else:
                    self._recalc(info['calc_prop'])

                    if info['calc_prop'] == 'closed_orbit':
                        v = self._get_closed_orbit(name, field)
                    elif info['calc_prop'] == 'twiss':
                        raise NotImplementedError
                    elif info['calc_prop'] == 'tbt':
                        raise NotImplementedError
                    else:
                        raise ValueError(f'Invalid calculated property: "{prop}"')
            else:
                if field in ('NUX', 'NUY'):
                    self._recalc('twiss')
                    twi = self._raw['twiss']['data']['twi']
                    v = twi['scalars'][field.lower()]
                    v -= np.floor(v) # Take only the fractional part
                else:
                    raise NotImplementedError(f'Element name / field: {name} / {field}')

            values.append(v)

        return values

    def getTune(self, plane, fractional_only=True):
        """"""

        self._recalc('twiss')
        twi = self._raw['twiss']['data']['twi']

        if plane.lower() in ('x', 'h'):
            v = twi['scalars']['nux']
        elif plane.lower() in ('y', 'v'):
            v = twi['scalars']['nuy']
        else:
            raise ValueError('Valid values for "plane": "x", "y", "h", "v"')

        if fractional_only:
            v -= np.floor(v) # Take only the fractional part

        return v

    def getTunes(self, fractional_only=True):
        """"""

        self._recalc('twiss')
        twi = self._raw['twiss']['data']['twi']

        tunes = []
        for plane in ['x', 'y']:
            v = twi['scalars'][f'nu{plane}']
            if fractional_only:
                v -= np.floor(v) # Take only the fractional part
            tunes.append(v)

        return tuple(tunes)

    def getChromaticity(self, plane):
        """"""

        self._recalc('twiss')
        twi = self._raw['twiss']['data']['twi']

        if plane.lower() in ('x', 'h'):
            v = twi['scalars']['dnux/dp']
        elif plane.lower() in ('y', 'v'):
            v = twi['scalars']['dnuy/dp']
        else:
            raise ValueError('Valid values for "plane": "x", "y", "h", "v"')

        return v

    def getChromaticities(self):
        """"""

        self._recalc('twiss')
        twi = self._raw['twiss']['data']['twi']

        return tuple(twi['scalars'][f'dnu{plane}/dp'] for plane in ['x', 'y'])

    def _get_global_index(self, calc_type, elem_name):
        """"""

        if calc_type == 'closed_orbit':
            cols = self._raw['closed_orbit']['columns']
        elif calc_type == 'twiss':
            twi = self._raw['twiss']['data']['twi']
            cols = twi['arrays']
        else:
            raise NotImplementedError

        index = self.flat_elems_index_maps[calc_type].get(elem_name, None)

        if index is None:
            bad_LTE_msg = (
                'Cannot handle elements with more than 2 splits or duplicate '
                'element names. Fix the LTE file.')
            matches = np.where(cols['ElementName'] == elem_name)[0]
            if matches.size == 1:
                index = matches[0]
            elif matches.size == 2:
                # Likely split in half. Must confirm that is the case.
                if cols['s'][matches[0]] == cols['s'][matches[1]-1]:
                    # Take the latter of the split element
                    index = matches[1]
                else:
                    raise RuntimeError(bad_LTE_msg)
            elif matches.size == 0:
                raise RuntimeError(
                    f'No element with name "{elem_name}" found. Check the LTE file.')
            else:
                raise RuntimeError(bad_LTE_msg)

            # Add the newly found mapping to avoid redundant search in the future
            self.flat_elems_index_maps[calc_type][elem_name] = index

        return index

    def _getRawCalcData(self):
        """"""

        for calc_type in list(self.flat_elems_index_maps):
            self._recalc(calc_type)

        return self._raw

    def _getProcessedCalcData(self):
        """"""

        for proc_type in list(self._proc):
            self._reprocess(proc_type)

        return self._proc

    def _reprocess(self, proc_type):

        if proc_type == 'orm':
            pass # TODO
        else:
            raise ValueError

    def getOptionalInitModelData(self):
        """
        Returns a dict with the following optional initial model data
        (these are not required to be pre-computed, but, if provided,
        the computation of the initial model properties every time the model is
        loaded can be skipped):

        flat_elems_index_maps:
          Mapping between element names and the indexes for
          the global flat element list of the specified beamline.
        """

        # This data goes directly into "self._raw" in __init__().
        # Examples: closed orbit, Twiss
        raw_data = self._getRawCalcData()

        # This data goes directly into "self._proc" in __init__().
        # Examples: ORM
        proc_data = self._getProcessedCalcData()

        self._construct_full_flat_elems_index_maps()
        # This data goes directly into "self.flat_elems_index_maps" in __init__().
        flat_elems_index_maps = self.flat_elems_index_maps

        return dict(flat_elems_index_maps=flat_elems_index_maps,
                    raw_calc_data=raw_data,
                    proc_calc_data=proc_data)


    def _construct_full_flat_elems_index_maps(self):
        """"""

        for calc_type, d in self.flat_elems_index_maps.items():

            self._recalc(calc_type)

            d.clear() # Clear the map first before full mapping

            if calc_type == 'closed_orbit':
                cols = self._raw['closed_orbit']['columns']
                flat_elem_names = cols['ElementName']
                for name in flat_elem_names:
                    try:
                        _ = self._get_global_index('closed_orbit', name)
                    except RuntimeError:
                        pass
            elif calc_type == 'twiss':
                twi = self._raw['twiss']['data']['twi']
                arrays = twi['arrays']
                flat_elem_names = arrays['ElementName']
                for name in flat_elem_names:
                    try:
                        _ = self._get_global_index('twiss', name)
                    except RuntimeError:
                        pass
            else:
                raise NotImplementedError


    def _get_closed_orbit(self, elem_name, field):
        """"""

        index = self._get_global_index('closed_orbit', elem_name)

        cols = self._raw['closed_orbit']['columns']

        if field in ('x', 'x0'):
            return cols['x'][index]
        elif field in ('y', 'y0'):
            return cols['y'][index]
        else:
            raise ValueError(f'Invalid field "{field}"')

    def _recalc(self, prop):
        """"""

        if not self.need_recalc[prop]:
            return

        pe = self.engine
        E_MeV = machines.getMachine().E_MeV

        if self.need_LTE_write:
            self.write_LTE()
            self.need_LTE_write = False

        if prop == 'closed_orbit':
            clo_calc = pe.orbit.ClosedOrbitCalculator(
                self.temp_fielpaths['LTE'], E_MeV, fixed_length=True,
                output_monitors_only=False, closed_orbit_accuracy=1e-9,
                closed_orbit_iterations=200, iteration_fraction=0.2, n_turns=1,
                use_beamline=self.base_used_beamline_name, N_KICKS=self.N_KICKS,
                fixed_lattice=True, # not changing steering; using LTE "as is"
            )
            self._raw['closed_orbit'] = clo_calc.calc(run_local=True)

            self.need_recalc['closed_orbit'] = False

        elif prop == 'twiss':

            pe.calc_ring_twiss(
                self.temp_fielpaths['TWI'], self.temp_fielpaths['LTE'],
                E_MeV, use_beamline=self.base_used_beamline_name,
                radiation_integrals=True,
                ele_filepath=self.temp_fielpaths['ELE'],
                output_file_type='pgz',
            )
            self._raw['twiss'] = pe.util.load_pgz_file(self.temp_fielpaths['TWI'])

            self._update_TwissData_obj()

            self.need_recalc['twiss'] = False

        elif prop == 'tbt':
            pass # Not implemented yet

        else:
            raise ValueError(f'Invalid calculated property: "{prop}"')

    def _update_TwissData_obj(self):
        """"""

        twi = self._raw['twiss']['data']['twi']
        scalars = twi['scalars']
        arrays = twi['arrays']

        self._twiss.tune = tuple(scalars[k] for k in ['nux', 'nuy'])
        self._twiss.chrom = tuple(scalars[k] for k in ['dnux/dp', 'dnuy/dp'])
        self._twiss.alphac = scalars['alphac']
        self._twiss.epsx0 = scalars['ex0']
        for k in ['Jx', 'Jy', 'Jdelta', 'taux', 'tauy', 'taudelta']:
            setattr(self._twiss, k, scalars[k])
        self._twiss.U0_MeV = scalars['U0']
        self._twiss.sigma_delta = scalars['Sdelta0']

        self._twiss.element = [name.lower() for name in arrays['ElementName']]
        _twi_list = []
        for col in self._twiss._cols:
            if not col.startswith('phi'):
                _twi_list.append(arrays[col])
            else:
                _twi_list.append(arrays[f'psi{col[-1]}']) # [rad]

        self._twiss._twtable = np.vstack((_twi_list)).T

    def put(self, mv, value):
        """"""

        d = mv['pyelegant']
        name = d['elem_name']
        field = d['property']

        elem_ind = self.elem_defs_index_maps[name]
        elem_def = self.elem_defs[elem_ind]
        elem_type = elem_def[1]

        mod_prop = {field: value}

        elem_def = self.LTE.modify_elem_def(elem_def, mod_prop)

        self.elem_defs[elem_ind] = elem_def

        # Update "need_LTE_write" and "need_recalc" states
        info = self._get_elem_type_field_info(elem_type, field, 'setpoint')
        if not self.need_LTE_write:
            self.need_LTE_write = info['need_LTE_write']
        for k, v in self.need_recalc.items():
            if not v:
                self.need_recalc[k] = info['need_recalc'][k]

    def write_LTE(self):
        """"""

        self.LTE.write_LTE(self.temp_fielpaths['LTE'], self.base_used_beamline_name,
                           self.elem_defs, self.beamline_defs)

    def _get_elem_type_field_info(self, elem_type, field, handle):
        """"""

        if handle not in ('setpoint', 'readback'):
            raise ValueError(f'Invalid handle: {handle}')

        if elem_type in ('KQUAD', 'QUAD'):
            if field == 'K1':
                if handle == 'setpoint':
                    need_LTE_write = True
                    need_recalc = dict(closed_orbit=True, twiss=True, tbt=True)
                else: # handle == 'readback'
                    calc_prop = None
                    def_val = 0.0
            else:
                raise NotImplementedError(f'Invalid quadrupole element property: {field}')
        elif elem_type in ('KSEXT', 'SEXT'):
            if field == 'K2':
                if handle == 'setpoint':
                    need_LTE_write = True
                    need_recalc = dict(closed_orbit=True, twiss=True, tbt=True)
                else: # handle == 'readback'
                    calc_prop = None
                    def_val = 0.0
            else:
                raise NotImplementedError(f'Invalid sextupole element property: {field}')
        elif elem_type in ('KOCT', 'OCTU'):
            if field == 'K3':
                if handle == 'setpoint':
                    need_LTE_write = True
                    need_recalc = dict(closed_orbit=True, twiss=True, tbt=True)
                else: # handle == 'readback'
                    calc_prop = None
                    def_val = 0.0
            else:
                raise NotImplementedError(f'Invalid octupole element property: {field}')
        elif elem_type in ('CSBEND', 'CSBEN', 'SBEN','SBEND', 'CCBEND'):
            if field in [f'K{i:d}' for i in range(1, 8+1)]:
                if handle == 'setpoint':
                    need_LTE_write = True
                    need_recalc = dict(closed_orbit=True, twiss=True, tbt=True)
                else: # handle == 'readback'
                    calc_prop = None
                    def_val = 0.0
            else:
                raise NotImplementedError(f'Invalid bend element property: {field}')
        elif elem_type in ('KICKER', 'EKICKER'):
            if field in ('HKICK', 'VKICK'): # [rad]
                if handle == 'setpoint':
                    need_LTE_write = True
                    need_recalc = dict(closed_orbit=True, twiss=True, tbt=True)
                else: # handle == 'readback'
                    calc_prop = None
                    def_val = 0.0
            else:
                raise NotImplementedError(f'Invalid steering dipole element property: {field}')
        elif elem_type in ('HKICK', 'VKICK', 'EHKICK', 'EVKICK'):
            if field == 'KICK': # [rad]
                if handle == 'setpoint':
                    need_LTE_write = True
                    need_recalc = dict(closed_orbit=True, twiss=True, tbt=True)
                else: # handle == 'readback'
                    calc_prop = None
                    def_val = 0.0
            else:
                raise NotImplementedError(f'Invalid steering dipole element property: {field}')
        elif elem_type == 'MONI':
            if field in ('x', 'x0', 'y', 'y0'):
                if handle == 'readback':
                    calc_prop = 'closed_orbit'
                    def_val = None
                else:
                    raise ValueError(f'BPM setpoint field "{field}" should not be called')
            else:
                raise NotImplementedError(f'Field "{field}" for BPM not yet handled')
        else:
            raise NotImplementedError(f'Unhandled element type: {elem_type}')

        if handle == 'setpoint':
            return dict(need_LTE_write=need_LTE_write, need_recalc=need_recalc)
        else: # handle == 'readback'
            return dict(default_val=def_val, calc_prop=calc_prop)