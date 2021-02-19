'''
This script should be run in a v2-aphla environment.

Convert the contents of /epics/aphla/apconf/nsls2/nsls2_LTB.sqlite as of
02/19/2020 into a dict in a gzipped pickled file for aphla v2.
'''

import pickle
import gzip
from pprint import pprint
import shutil

submachine_name = 'LTB'

# While running "interactive_sqlite_rows_saving.py" interactively, which calls
# "ap.machines.load('nsls2', submachine_name)", within load() in
# aphla/machines/__init__.py, right after "cfa.loadSqlite(accsqlite)" was
# exectuted, the contents of the list "cfa.rows" was manually saved into the
# following pgz file:
nsls2_sqlite_rows_pgz_file = f'nsls2_{submachine_name.lower()}_sqlite_rows.pgz'
with gzip.GzipFile(nsls2_sqlite_rows_pgz_file, 'rb') as f:
    cfa_rows = pickle.load(f)

# v1 aphla unit conversion file: /epics/aphla/apconf/nsls2/ltb_unitconv.ini

#>> ap.getGroups()
#['BPM', 'FLAG', 'VCOR', 'HCOR', 'QUAD', 'ICT', 'BEND', 'FCT', 'HLA:VIRTUAL']

# >> bpms = ap.getElements('BPM')
# >> e = bpms[0]
# >> [(fld, e._field[fld].pvrb) for fld in e.fields()]
#[('I', ['LTB-BI{BPM:1}I-I']),
 #('goldenX', []),
 #('goldenY', []),
 #('x', ['LTB-BI{BPM:1}Pos:X-I']),
 #('y', ['LTB-BI{BPM:1}Pos:Y-I'])]

# >> [(fld, e._field[fld].pvsp) for fld in e.fields()]
#[('I', []),
 #('goldenX', ['LTB-BI{BPM:1}Pos:UsrXoffset-SP']),
 #('goldenY', ['LTB-BI{BPM:1}Pos:UsrYoffset-SP']),
 #('x', []),
 #('y', [])]

print(len(cfa_rows))
# Output: 207
print(set([t for pv, elem_def, tags in cfa_rows for t in tags]))
# Output: {'aphla.sys.LTB', 'aphla.sys.LTD2', 'aphla.sys.LTD1'}

# Output when run in v1-aphla env for: [e.name for e in ap.getElements('*')]
v1aphal_elem_names = [
    'P1', 'VF1', 'CY1', 'CX1', 'Q1', 'ICT1', 'Q2', 'Q3', 'CY2', 'CX2', 'B1',
    'Q4', 'CY3', 'CX3', 'Q5', 'P2', 'VF2', 'FCT1', 'Q6', 'CY4', 'CX4', 'Q7',
    'Q8', 'Q9', 'CY5', 'CX5', 'P3', 'VF3', 'P4', 'VF4', 'Q10', 'P5', 'CY6',
    'CX6', 'Q11', 'Q12', 'CY7', 'CX7', 'Q13', 'Q14', 'FCT2', 'ICT2', 'VF5',
    'Q15', 'CY8', 'CX8', 'P6',
    ]

print([elem_def['elemName'] for pv, elem_def, tags in cfa_rows
       if elem_def['elemName'] not in v1aphal_elem_names])
# Output: []
_all_rows_elem_names = set([elem_def['elemName'] for pv, elem_def, tags in cfa_rows])
print([name for name in v1aphal_elem_names
       if name not in _all_rows_elem_names])
# Output: []

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