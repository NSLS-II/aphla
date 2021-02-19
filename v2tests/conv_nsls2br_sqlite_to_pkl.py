'''
This script should be run in a v2-aphla environment.

Convert the contents of /epics/aphla/apconf/nsls2/nsls2_BR.sqlite as of
02/18/2020 into a dict in a gzipped pickled file for aphla v2.
'''

import pickle
import gzip
from pprint import pprint
import shutil

submachine_name = 'BR'

# While running "interactive_sqlite_rows_saving.py" interactively, which calls
# "ap.machines.load('nsls2', submachine_name)", within load() in
# aphla/machines/__init__.py, right after "cfa.loadSqlite(accsqlite)" was
# exectuted, the contents of the list "cfa.rows" was manually saved into the
# following pgz file:
nsls2_sqlite_rows_pgz_file = f'nsls2_{submachine_name.lower()}_sqlite_rows.pgz'
with gzip.GzipFile(nsls2_sqlite_rows_pgz_file, 'rb') as f:
    cfa_rows = pickle.load(f)

# v1 aphla unit conversion file: /epics/aphla/apconf/nsls2/br_unitconv.hdf5

#>> ap.getGroups()
#['BPM', 'HCOR', 'QUAD', 'BEND', 'VCOR', 'SEXT', 'HLA:VIRTUAL']


# >> bpms = ap.getElements('BPM')
# >> e = bpms[0]
# >> [(fld, e._field[fld].pvrb) for fld in e.fields()]
#[('I', ['BR:IS-BI{BPM:2}Ampl:Sum-I']),
 #('I1st', ['BR:IS-BI{}BPM:2_1stTurn_Ampl:Sum-I']),
 #('Ifa', ['BR:IS-BI{BPM:2}FA-S']),
 #('Itbt', ['BR:IS-BI{BPM:2}TBT-S']),
 #('delayTBT', []),
 #('enableADC', []),
 #('enableFA', []),
 #('enableTBT', []),
 #('mode', []),
 #('x', ['BR:IS-BI{BPM:2}Pos:X-I']),
 #('x1st', ['BR:IS-BI{}BPM:2_1stTurn_Pos:X-I']),
 #('xfa', ['BR:IS-BI{BPM:2}FA-X']),
 #('xtbt', ['BR:IS-BI{BPM:2}TBT-X']),
 #('y', ['BR:IS-BI{BPM:2}Pos:Y-I']),
 #('y1st', ['BR:IS-BI{}BPM:2_1stTurn_Pos:Y-I']),
 #('yfa', ['BR:IS-BI{BPM:2}FA-Y']),
 #('ytbt', ['BR:IS-BI{BPM:2}TBT-Y'])]

# >> [(fld, e._field[fld].pvsp) for fld in e.fields()]
#[('I', []),
 #('I1st', []),
 #('Ifa', []),
 #('Itbt', []),
 #('delayTBT', ['BR:IS-BI{BPM:2}ddrTbtOffset']),
 #('enableADC', ['BR:IS-BI{BPM:2}ddrAdcWfEnable']),
 #('enableFA', ['BR:IS-BI{BPM:2}ddrFaWfEnable']),
 #('enableTBT', ['BR:IS-BI{BPM:2}ddrTbtWfEnable']),
 #('mode', ['BR:IS-BI{BPM:2}DDR:WfmSel-SP']),
 #('x', []),
 #('x1st', []),
 #('xfa', []),
 #('xtbt', []),
 #('y', []),
 #('y1st', []),
 #('yfa', []),
 #('ytbt', [])]

print(set([t for pv, elem_def, tags in cfa_rows for t in tags]))
# Output: {'aphla.sys.BR'}
print(all([tags == ['aphla.sys.BR'] for pv, elem_def, tags in cfa_rows]))
# Output: True

assert [elem_def['elemField'] for pv, elem_def, tags in cfa_rows
        if '[' in elem_def['elemField']] == []

root = {}
submachine = root[submachine_name] = {}
tags_list = []
for pv, elem_def, tags in cfa_rows:
    tags_list.append(tuple(tags))

    elemName = elem_def.pop('elemName')

    if pv.strip():
        field = elem_def.pop('elemField')

        handle = elem_def.pop('elemHandle')
        assert handle in ('get', 'put')

        epsilon = elem_def.pop('epsilon', None)

        if elemName not in submachine:
            elem = submachine[elemName] = {k: v for k, v in elem_def.items()}
            elem['map'] = {}
            elem['tags'] = tags
        else:
            elem = submachine[elemName]
            for k, v in elem_def.items():
                if k in elem:
                    assert elem[k] == v
                else:
                    # If there are mistakes in the original SQLite file, correct
                    # the data here
                    pass

        if field not in elem['map']:
            elem['map'][field] = {}
        if handle not in elem['map'][field]:
            elem['map'][field][handle] = {}

            elem['map'][field][handle]['mv'] = {}

        # Avoid duplicate definitions
        for k in ['pv', 'epsilon']:
            try:
                assert k not in elem['map'][field][handle]
            except:
                print('-----------------------------')
                print(elemName, k, field, handle, pv)
                #pprint(elem)
                pprint(elem['map'][field])

                break

        elem['map'][field][handle]['pv'] = pv
        if epsilon:
            elem['map'][field][handle]['epsilon'] = epsilon

        # Add model variable (MV) information
        mv_d = dict(elem_name=elemName.upper())

    else:
        assert 'elemField' not in elem_def
        assert 'elemHandle' not in elem_def

        assert elemName not in submachine

        elem = submachine[elemName] = {k: v for k, v in elem_def.items()}

print(set(tags_list))


nsls2_elems_pvs_mvs_pgz_file = f'nsls2_{submachine_name.lower()}_elems_pvs_mvs.pgz'
with gzip.GzipFile(nsls2_elems_pvs_mvs_pgz_file, 'wb') as f:
    pickle.dump(root[submachine_name], f)
shutil.copy(nsls2_elems_pvs_mvs_pgz_file,
            f'/epics/aphla/apconf/nsls2/{nsls2_elems_pvs_mvs_pgz_file}')

#with gzip.GzipFile(nsls2_elems_pvs_mvs_pgz_file, 'rb') as f:
    #loaded_submachine = pickle.load(f)

print('Finished')