'''
This script should be run in a v2-aphla environment.

Convert the contents of /epics/aphla/apconf/nsls2/nsls2_bts.sqlite as of
02/18/2020 into a dict in a gzipped pickled file for aphla v2.
'''

import pickle
import gzip
from pprint import pprint
import shutil

submachine_name = 'BTS'

# While running "interactive_sqlite_rows_saving.py" interactively, which calls
# "ap.machines.load('nsls2', submachine_name)", within load() in
# aphla/machines/__init__.py, right after "cfa.loadSqlite(accsqlite)" was
# exectuted, the contents of the list "cfa.rows" was manually saved into the
# following pgz file:
nsls2_sqlite_rows_pgz_file = f'nsls2_{submachine_name.lower()}_sqlite_rows.pgz'
with gzip.GzipFile(nsls2_sqlite_rows_pgz_file, 'rb') as f:
    cfa_rows = pickle.load(f)

# v1 aphla unit conversion file: /epics/aphla/apconf/nsls2/bts_unitconv.hdf5

#>> ap.getGroups()
#['COR', 'BEND', 'MONI', 'FLAG', 'BPM', 'WATCH', 'HCOR', 'VCOR', 'QUAD',
 #'MARK', 'TWISS', 'HLA:VIRTUAL']

# >> bpms = ap.getElements('BPM')
# >> e = bpms[0]
# >> [(fld, e._field[fld].pvrb) for fld in e.fields()]
#[('x', ['BTS-BI{BPM:1}Pos:X-I']),
# ('y', ['BTS-BI{BPM:1}Pos:Y-I'])]


# >> [(fld, e._field[fld].pvsp) for fld in e.fields()]
#[('x', []), ('y', [])]

print(set([t for pv, elem_def, tags in cfa_rows for t in tags]))
# Output: {'aphla.sys.BTS'}
print([tags for pv, elem_def, tags in cfa_rows if tags != ['aphla.sys.BTS']])
# Output: [[], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], []]
print([pv for pv, elem_def, tags in cfa_rows if tags != ['aphla.sys.BTS']])
# Output: ['', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '']
print([elem_def for pv, elem_def, tags in cfa_rows if tags != ['aphla.sys.BTS']])
# Output:
#[
    #{
        #'id': 1,
        #'elemName': 'BRCX1SE',
        #'elemType': 'COR',
        #'elemLength': 0.134,
        #'elemPosition': 0.227,
        #'elemIndex': 300,
        #'virtual': 0,
    #},
    #{
        #'id': 2,
        #'elemName': 'BRBU1SE',
        #'elemType': 'BEND',
        #'elemLength': 0.166,
        #'elemPosition': 0.453,
        #'elemIndex': 500,
        #'virtual': 0,
    #},
    #{
        #'id': 3,
        #'elemName': 'BRK1SE',
        #'elemType': 'BEND',
        #'elemLength': 0.200638,
        #'elemPosition': 0.833643,
        #'elemIndex': 700,
        #'virtual': 0,
    #},
    #{
        #'id': 4,
        #'elemName': 'BRK2SE',
        #'elemType': 'BEND',
        #'elemLength': 0.200641,
        #'elemPosition': 1.20366,
        #'elemIndex': 900,
        #'virtual': 0,
    #},
    #{
        #'id': 5,
        #'elemName': 'BRK3SE',
        #'elemType': 'BEND',
        #'elemLength': 0.200644,
        #'elemPosition': 1.573682,
        #'elemIndex': 1100,
        #'virtual': 0,
    #},
    #{
        #'id': 6,
        #'elemName': 'BRK4SE',
        #'elemType': 'BEND',
        #'elemLength': 0.200648,
        #'elemPosition': 1.943711,
        #'elemIndex': 1300,
        #'virtual': 0,
    #},
    #{
        #'id': 7,
        #'elemName': 'BRP1SE',
        #'elemType': 'MONI',
        #'elemLength': 0.0,
        #'elemPosition': 2.345117,
        #'elemIndex': 1500,
        #'virtual': 0,
    #},
    #{
        #'id': 8,
        #'elemName': 'BRBU2SE',
        #'elemType': 'BEND',
        #'elemLength': 0.166,
        #'elemPosition': 2.658131,
        #'elemIndex': 1700,
        #'virtual': 0,
    #},
    #{
        #'id': 10,
        #'elemName': 'BRSP1SE',
        #'elemType': 'BEND',
        #'elemLength': 0.6,
        #'elemPosition': 4.060144,
        #'elemIndex': 2100,
        #'virtual': 0,
    #},
    #{
        #'id': 13,
        #'elemName': 'FT1',
        #'elemType': 'WATCH',
        #'elemLength': 0.0,
        #'elemPosition': 6.399974,
        #'elemIndex': 2700,
        #'virtual': 0,
    #},
    #{
        #'id': 35,
        #'elemName': 'M1',
        #'elemType': 'MARK',
        #'elemLength': 0.0,
        #'elemPosition': 22.90441,
        #'elemIndex': 7500,
        #'virtual': 0,
    #},
    #{
        #'id': 44,
        #'elemName': 'ESLIT',
        #'elemType': 'WATCH',
        #'elemLength': 0.0,
        #'elemPosition': 29.88569,
        #'elemIndex': 9200,
        #'virtual': 0,
    #},
    #{
        #'id': 49,
        #'elemName': 'FT2',
        #'elemType': 'WATCH',
        #'elemLength': 0.0,
        #'elemPosition': 36.82744,
        #'elemIndex': 10200,
        #'virtual': 0,
    #},
    #{
        #'id': 50,
        #'elemName': 'IT1',
        #'elemType': 'WATCH',
        #'elemLength': 0.0,
        #'elemPosition': 37.01984,
        #'elemIndex': 10400,
        #'virtual': 0,
    #},
    #{
        #'id': 61,
        #'elemName': 'ISP3',
        #'elemType': 'MONI',
        #'elemLength': 0.0,
        #'elemPosition': 44.61924,
        #'elemIndex': 12600,
        #'virtual': 0,
    #},
    #{
        #'id': 62,
        #'elemName': 'ISP4',
        #'elemType': 'MONI',
        #'elemLength': 0.0,
        #'elemPosition': 44.67639,
        #'elemIndex': 12800,
        #'virtual': 0,
    #},
    #{
        #'id': 63,
        #'elemName': 'ISBU3',
        #'elemType': 'BEND',
        #'elemLength': 0.65,
        #'elemPosition': 45.67389,
        #'elemIndex': 13000,
        #'virtual': 0,
    #},
    #{
        #'id': 64,
        #'elemName': 'ISP5',
        #'elemType': 'MONI',
        #'elemLength': 0.0,
        #'elemPosition': 45.98152,
        #'elemIndex': 13200,
        #'virtual': 0,
    #},
    #{
        #'id': 65,
        #'elemName': 'ISBU4',
        #'elemType': 'BEND',
        #'elemLength': 0.65,
        #'elemPosition': 47.55389,
        #'elemIndex': 13400,
        #'virtual': 0,
    #},
    #{
        #'id': 68,
        #'elemName': 'twiss',
        #'elemType': 'TWISS',
        #'elemLength': 0.0,
        #'elemPosition': 0.0,
        #'elemIndex': -100,
        #'virtual': 1,
    #},
#]

# Output when run in v1-aphla env for: [e.name for e in ap.getElements('*')]
v1aphal_elem_names = [
    'BRCX1SE', 'BRBU1SE', 'BRK1SE', 'BRK2SE', 'BRK3SE', 'BRK4SE', 'BRP1SE',
    'BRBU2SE', 'VF1', 'BRSP1SE', 'P1', 'SP2', 'FT1', 'C1', 'Q1', 'VF2', 'Q2',
    'B1', 'Q3', 'C2', 'B2', 'P2', 'Q4', 'C3', 'P3', 'VF3', 'Q5', 'VF4', 'P4',
    'Q6', 'C4', 'Q7', 'VF5', 'Q8', 'M1', 'B3', 'Q9', 'C5', 'P5', 'Q10', 'B4',
    'C6', 'Q11', 'ESLIT', 'Q12', 'P6', 'VF6', 'C7', 'FT2', 'IT1', 'P7', 'VF7',
    'Q13', 'Q14', 'C8', 'SP3', 'C9', 'P8', 'IS', 'ISVF1', 'ISP3', 'ISP4',
    'ISBU3', 'ISP5', 'ISBU4']

print([elem_def['elemName'] in v1aphal_elem_names
       for pv, elem_def, tags in cfa_rows if tags != ['aphla.sys.BTS']])
# Output: [True, True, True, True, True, True, True, True, True, True, True,
#          True, True, True, True, True, True, True, True, False]

# Confirm that there are no sys-tagged rows for the elements for which
# there are rows without tags but the corresponding elements exist in
# v1-aphla. (These v1-aphla elements has no fields and PVs associated, but
# they are still there, so I'll be keeping them in v2-aphla as well the same way.)
no_systag_elem_defs = [
    elem_def for pv, elem_def, tags in cfa_rows
    if (tags != ['aphla.sys.BTS']) and
    (elem_def['elemName'] in v1aphal_elem_names) # <- removing def for "twiss" element
]
counts = {elem_def['elemName']: 0 for elem_def in no_systag_elem_defs}
for elem_def in no_systag_elem_defs:
    elem_name = elem_def['elemName']
    for _, _elem_def, _tags in cfa_rows:
        if _elem_def['elemName'] == elem_name:
            counts[elem_name] += 1
            assert _tags == []
assert all([n == 1 for k, n in counts.items()])

# Only remove the row for the "twiss" element, which doesn't exist either in v1-aphla
cfa_rows = [[pv, elem_def, tags] for pv, elem_def, tags in cfa_rows
            if elem_def['elemName'] in v1aphal_elem_names]

assert [elem_def['elemField'] for pv, elem_def, tags in cfa_rows
        if ('elemField' in elem_def) and ('[' in elem_def['elemField'])] == []

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