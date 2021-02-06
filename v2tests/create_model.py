import gzip
import pickle
from pathlib import Path
import os
import traceback
from copy import deepcopy

import numpy as np
import pyelegant as pe

aphla_config_folderp = Path('/epics/aphla/apconf/nsls2')

#base_LTE_filepath = '/home/yhidaka/git_repos/aphla/utils/20190125_VS_nsls2sr17idsmt_SQLC16.lte'
base_LTE_filepath = str(aphla_config_folderp.joinpath(
    'models', 'SR', 'pyelegant', 'LTEs', '20190125_VS_nsls2sr17idsmt_SQLC16.lte'))

used_beamline_name = 'RING'

LTE = pe.ltemanager.Lattice(LTE_filepath=base_LTE_filepath,
                            used_beamline_name=used_beamline_name)
LTE_d = LTE.get_used_beamline_element_defs()
flat_used_elem_names = LTE_d['flat_used_elem_names']
elem_defs = LTE_d['elem_defs']

elem_names = [v[0] for v in elem_defs]
elem_types = [v[1] for v in elem_defs]
props = [v[2] for v in elem_defs]

ordered_quad_names = [name for name in flat_used_elem_names
                      if (elem_types[elem_names.index(name)] == 'KQUAD') and
                      'TILT' not in props[elem_names.index(name)]]
ordered_quad_counts = [flat_used_elem_names.count(name)
                       for name in flat_used_elem_names
                       if (elem_types[elem_names.index(name)] == 'KQUAD') and
                       'TILT' not in props[elem_names.index(name)]]
assert np.all(np.array(ordered_quad_counts) == 1)
assert len(ordered_quad_names) == 300

ordered_skquad_names = [name for name in flat_used_elem_names
                        if (elem_types[elem_names.index(name)] == 'KQUAD') and
                        'TILT' in props[elem_names.index(name)]]
ordered_skquad_counts = [flat_used_elem_names.count(name)
                         for name in flat_used_elem_names
                         if (elem_types[elem_names.index(name)] == 'KQUAD') and
                         'TILT' in props[elem_names.index(name)]]
assert np.all(np.array(ordered_skquad_counts) == 2)
ordered_skquad_names = np.array(ordered_skquad_names)
assert np.all(ordered_skquad_names[::2] == ordered_skquad_names[1::2])
ordered_skquad_names = ordered_skquad_names[::2].tolist()
assert len(ordered_skquad_names) == 30+1 # "+1" for C16SQL

ordered_sext_names = [name for name in flat_used_elem_names
                      if (elem_types[elem_names.index(name)] == 'KSEXT')]
ordered_sext_counts = [flat_used_elem_names.count(name)
                       for name in flat_used_elem_names
                       if (elem_types[elem_names.index(name)] == 'KSEXT')]
assert np.all(np.array(ordered_sext_counts) == 1)
assert len(ordered_sext_names) == 270

ordered_bend_names = [name for name in flat_used_elem_names
                      if (elem_types[elem_names.index(name)] == 'CSBEND')]
ordered_bend_counts = [flat_used_elem_names.count(name)
                       for name in flat_used_elem_names
                       if (elem_types[elem_names.index(name)] == 'CSBEND')]
assert np.all(np.array(ordered_bend_counts) == 1)
assert len(ordered_bend_names) == 60

ordered_rbpm_names = [name for name in flat_used_elem_names
                      if (elem_types[elem_names.index(name)] == 'MONI')
                      and name.startswith(('PH', 'PL', 'PM'))]
ordered_rbpm_counts = [flat_used_elem_names.count(name)
                      for name in flat_used_elem_names
                      if (elem_types[elem_names.index(name)] == 'MONI')
                      and name.startswith(('PH', 'PL', 'PM'))]
assert np.all(np.array(ordered_rbpm_counts) == 1)
assert len(ordered_rbpm_names) == 180

ordered_ubpm_names = [name for name in flat_used_elem_names
                      if (elem_types[elem_names.index(name)] == 'MONI')
                      and name.startswith(('PU',))]
ordered_ubpm_counts = [flat_used_elem_names.count(name)
                      for name in flat_used_elem_names
                      if (elem_types[elem_names.index(name)] == 'MONI')
                      and name.startswith(('PU',))]
assert np.all(np.array(ordered_ubpm_counts) == 1)
assert len(ordered_ubpm_names) == 43 # as of 02/03/2021

ordered_cor_names = [name for name in flat_used_elem_names
                      if (elem_types[elem_names.index(name)] == 'KICKER')
                      and name.startswith(('CH', 'CL', 'CM'))]
ordered_cor_counts = [flat_used_elem_names.count(name)
                      for name in flat_used_elem_names
                      if (elem_types[elem_names.index(name)] == 'KICKER')
                      and name.startswith(('CH', 'CL', 'CM'))]
assert np.all(np.array(ordered_cor_counts) == 1)
assert len(ordered_cor_names) == 360
ordered_corY_names = []
for n1, n2 in zip(ordered_cor_names[::2], ordered_cor_names[1::2]):
    if 'YG' in n1:
        assert n1 == n2.replace('XG', 'YG')
        ordered_corY_names.append(n1)
    else:
        assert n1.replace('XG', 'YG') == n2
        ordered_corY_names.append(n2)
assert len(ordered_corY_names) == 180
ordered_cor_names = ordered_corY_names

ordered_fcor_names = [name for name in flat_used_elem_names
                      if (elem_types[elem_names.index(name)] == 'KICKER')
                      and name.startswith('F')]
ordered_fcor_counts = [flat_used_elem_names.count(name)
                      for name in flat_used_elem_names
                      if (elem_types[elem_names.index(name)] == 'KICKER')
                      and name.startswith('F')]
assert np.all(np.array(ordered_fcor_counts) == 1)
assert len(ordered_fcor_names) == 90

ordered_ukickmap_names = [name for name in flat_used_elem_names
                          if (elem_types[elem_names.index(name)] == 'UKICKMAP')]
ordered_ukickmap_counts = [flat_used_elem_names.count(name)
                           for name in flat_used_elem_names
                           if (elem_types[elem_names.index(name)] == 'UKICKMAP')]
assert np.all(np.array(ordered_ukickmap_counts) == 1)
assert len(ordered_ukickmap_names) == 17 + 2*3


all_variable_elem_names = (
    ordered_bend_names +
    ordered_quad_names +
    ordered_skquad_names +
    ordered_sext_names +
    ordered_cor_names +
    ordered_fcor_names +
    ordered_rbpm_names +
    ordered_ubpm_names +
    ordered_ukickmap_names
)
assert len(all_variable_elem_names) == len(np.unique(all_variable_elem_names))
sort_inds = np.argsort([
    flat_used_elem_names.index(name) for name in all_variable_elem_names])
all_variable_elem_names_ordered = np.array(all_variable_elem_names)[sort_inds].tolist()

elem_name_index_maps = {}
for name in all_variable_elem_names_ordered:
    i = elem_names.index(name)
    #print(name)
    #print(elem_defs[i])
    #print(LTE.parse_elem_properties(elem_defs[i][2]))
    elem_name_index_maps[name] = i

# You can create a new LTE file with only a certain property modified based
# on the base LTE file as follows:
'''
    name = ordered_quad_names[0]
    elem_ind = elem_name_index_maps[name]
    orig_elem_def = LTE_d['elem_defs'][elem_ind]
    assert name == orig_elem_def[0]

    mod_prop = {'K1': -0.58}
    new_elem_def = LTE.modify_elem_def(orig_elem_def, mod_prop)
    LTE_d['elem_defs'][elem_ind] = new_elem_def

    LTE.write_LTE(
        new_LTE_filepath, used_beamline_name,
        LTE_d['elem_defs'], LTE_d['beamline_defs'])
'''

model_name = '17ids'
model_filepath = aphla_config_folderp.joinpath(
    'models', 'SR', 'pyelegant', f'{model_name}.pgz')
with gzip.GzipFile(model_filepath, 'wb') as f:
    pickle.dump([base_LTE_filepath, used_beamline_name], f)
    pickle.dump([LTE_d['elem_defs'], LTE_d['beamline_defs']], f)
    pickle.dump(elem_name_index_maps, f)
os.chmod(model_filepath, 0o644)

# --------------- 3DW Lattice ---------------

dw3_LTE_filepath = str(aphla_config_folderp.joinpath(
    'models', 'SR', 'pyelegant', 'LTEs', 'nsls2sr_dw_20141119.lte'))
used_beamline_name = 'RING'

dw3_LTE = pe.ltemanager.Lattice(LTE_filepath=dw3_LTE_filepath,
                                used_beamline_name=used_beamline_name)
dw3_LTE_d = dw3_LTE.get_used_beamline_element_defs()
dw3_elem_defs = dw3_LTE_d['elem_defs']
dw3_elem_names = [v[0] for v in dw3_elem_defs]

mod_elem_defs = deepcopy(LTE_d['elem_defs'])

# Only need to modify Quads properties, but check all sext K2 values are the same
for name, index in elem_name_index_maps.items():
    assert mod_elem_defs[index][0] == name
    if mod_elem_defs[index][1] == 'UKICKMAP':
        # Open all non-DW kickmaps
        if not name.startswith('DW100'):
            mod_prop = LTE.parse_elem_properties(mod_elem_defs[index][2])
            mod_prop['FIELD_FACTOR'] = 0.0
            mod_elem_defs[index] = LTE.modify_elem_def(mod_elem_defs[index],
                                                       mod_prop)
    elif name != 'SQLG6C16B':
        i = dw3_elem_names.index(name)
        assert dw3_elem_defs[i][0] == name

        if name.startswith('Q'):
            assert mod_elem_defs[index][1] == dw3_elem_defs[i][1] == 'KQUAD'

            print(
                name,
                LTE.parse_elem_properties(dw3_elem_defs[i][2]),
                LTE.parse_elem_properties(mod_elem_defs[index][2]))

            orig_prop = LTE.parse_elem_properties(mod_elem_defs[index][2])
            new_prop = LTE.parse_elem_properties(dw3_elem_defs[i][2])
            assert set(list(orig_prop)) == set(list(new_prop))

            assert orig_prop['L'] == new_prop['L']

            new_elem_def = LTE.modify_elem_def(mod_elem_defs[index], new_prop)
            mod_elem_defs[index] = new_elem_def

        elif name.startswith(('SH', 'SL', 'SM')):
            assert mod_elem_defs[index][1] == dw3_elem_defs[i][1] == 'KSEXT'

            #print(
                #name,
                #LTE.parse_elem_properties(dw3_elem_defs[i][2]),
                #LTE.parse_elem_properties(mod_elem_defs[index][2]))

            orig_prop = LTE.parse_elem_properties(mod_elem_defs[index][2])
            new_prop = LTE.parse_elem_properties(dw3_elem_defs[i][2])
            assert set(list(orig_prop)) == set(list(new_prop))
            for k, v in orig_prop.items():
                assert v == new_prop[k]
    else:
        pass

model_name = '3dw'
model_filepath = aphla_config_folderp.joinpath(
    'models', 'SR', 'pyelegant', f'{model_name}.pgz')
with gzip.GzipFile(model_filepath, 'wb') as f:
    pickle.dump([dw3_LTE_filepath, used_beamline_name], f)
    pickle.dump([mod_elem_defs, LTE_d['beamline_defs']], f)
    pickle.dump(elem_name_index_maps, f)
os.chmod(model_filepath, 0o644)


# --------------- Bare Lattice ---------------

#bare_LTE_filename = '20140204_nsls2_bare.lte'
# ^ This file is not usable for the purpose here, as the RING beamline is one
#   super-period simply multiplied by 15. In other words, not enough individualized
#   element names. Must use the lattice file below.
bare_LTE_filename = 'nsls2sr_bare_20141015.lte'

bare_LTE_filepath = str(aphla_config_folderp.joinpath(
    'models', 'SR', 'pyelegant', 'LTEs', bare_LTE_filename))
used_beamline_name = 'RING'

bare_LTE = pe.ltemanager.Lattice(LTE_filepath=bare_LTE_filepath,
                                 used_beamline_name=used_beamline_name)
bare_LTE_d = bare_LTE.get_used_beamline_element_defs()
bare_elem_defs = bare_LTE_d['elem_defs']
bare_elem_names = [v[0] for v in bare_elem_defs]

mod_elem_defs = deepcopy(LTE_d['elem_defs'])

# Only need to modify Quads properties, but check all sext K2 values are the same
for name, index in elem_name_index_maps.items():
    assert mod_elem_defs[index][0] == name
    if mod_elem_defs[index][1] == 'UKICKMAP':
        # Open all kickmaps
        mod_prop = LTE.parse_elem_properties(mod_elem_defs[index][2])
        mod_prop['FIELD_FACTOR'] = 0.0
        mod_elem_defs[index] = LTE.modify_elem_def(mod_elem_defs[index],
                                                   mod_prop)
    elif name != 'SQLG6C16B':
        i = bare_elem_names.index(name)
        assert bare_elem_defs[i][0] == name

        if name.startswith('Q'):
            assert mod_elem_defs[index][1] == bare_elem_defs[i][1] == 'KQUAD'

            print(
                name,
                LTE.parse_elem_properties(bare_elem_defs[i][2]),
                LTE.parse_elem_properties(mod_elem_defs[index][2]))

            orig_prop = LTE.parse_elem_properties(mod_elem_defs[index][2])
            new_prop = LTE.parse_elem_properties(bare_elem_defs[i][2])
            assert set(list(orig_prop)) == set(list(new_prop))

            assert orig_prop['L'] == new_prop['L']

            new_elem_def = LTE.modify_elem_def(mod_elem_defs[index], new_prop)
            mod_elem_defs[index] = new_elem_def

        elif name.startswith(('SH', 'SL', 'SM')):
            assert mod_elem_defs[index][1] == bare_elem_defs[i][1] == 'KSEXT'

            #print(
                #name,
                #LTE.parse_elem_properties(bare_elem_defs[i][2]),
                #LTE.parse_elem_properties(mod_elem_defs[index][2]))

            orig_prop = LTE.parse_elem_properties(mod_elem_defs[index][2])
            new_prop = LTE.parse_elem_properties(bare_elem_defs[i][2])
            assert set(list(orig_prop)) == set(list(new_prop))
            for k, v in orig_prop.items():
                assert v == new_prop[k]
    else:
        pass

model_name = 'bare'
model_filepath = aphla_config_folderp.joinpath(
    'models', 'SR', 'pyelegant', f'{model_name}.pgz')
with gzip.GzipFile(model_filepath, 'wb') as f:
    pickle.dump([bare_LTE_filepath, used_beamline_name], f)
    pickle.dump([mod_elem_defs, LTE_d['beamline_defs']], f)
    pickle.dump(elem_name_index_maps, f)
os.chmod(model_filepath, 0o644)

print('Finished')

