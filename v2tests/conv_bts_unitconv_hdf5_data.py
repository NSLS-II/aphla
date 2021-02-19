import pickle

import h5py

keys = ['B1_b0_BL(I)', 'B1_b0_I(BL)', 'HCOR_x_BL(I)', 'HCOR_x_I(BL)',
        'ISBU3_b0_BL(I)', 'ISBU4_b0_BL(I)', 'IS_b0_BL(I)', 'SP3_b0_BL(I)',
        'VCOR1_y_BL(I)', 'VCOR1_y_I(BL)',
        'rot_coil_BST-QDP-5200-0004_000.xls_D',
        ]

unitconvs = {}

f = h5py.File('/epics/aphla/apconf/nsls2/bts_unitconv.hdf5', 'r')
g = f['UnitConversion']
for k in keys:
    g[k][()]
    if k == 'rot_coil_BST-QDP-5200-0004_000.xls_D':
        correct_key = 'rot_coil_BST-QDP-5200-0004_000.xls'
    else:
        correct_key = k

    unitconvs[correct_key] = dict(table=g[k][()])

    for k2, v2 in g[k].attrs.items():
        unitconvs[correct_key][k2] = v2
f.close()


table_filepath = 'nsls2bts_unitconv_tables.pkl'
tables = dict(BTS={})
tables['BTD'] = {} # Note that some elements are shared by both BTS and BTD
# lattices, so the unit conversion data need to be copied for BTD as well.
for k, v in unitconvs.items():
    tables['BTS'][k] = v['table']
    tables['BTD'][k] = v['table']
with open(table_filepath, 'wb') as f:
    pickle.dump(tables, f)
