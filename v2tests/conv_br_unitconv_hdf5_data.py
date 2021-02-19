import pickle

import h5py

keys = ['BD1_b0_B(I)', 'BD1_b0_I(B)', 'BD1_b1_G(I)', 'BD1_b2_S(I)',
        'BD2_b0_B(I)', 'BD2_b0_I(B)', 'BD2_b1_G(I)', 'BD2_b2_S(I)',
        'BF_b0_B(I)', 'BF_b0_I(B)', 'BF_b1_G(I)', 'BF_b2_S(I)',
        'CXW_x_BL(I)', 'CXW_x_I(BL)',
        'CX_b2_BL(I)', 'CX_x_I(BL)',
        'CY_y_BL(I)', 'CY_y_I(BL)',
        'QD_b1_1k_G(I)', 'QD_b1_1k_I(G)',
        'QF_b1_1k_G(I)', 'QF_b1_1k_I(G)',
        'QG_b1_1k_G(I)', 'QG_b1_1k_I(G)',
        'rot_coil_BST-QDP-5200-0004_000.xls',
        'SD_b2_S(I)', 'SD_b2_I(S)',
        'SF_b2_S(I)', 'SF_b2_I(S)',
        ]

unitconvs = {}

f = h5py.File('/epics/aphla/apconf/nsls2/br_unitconv.hdf5', 'r')
g = f['UnitConversion']
for k in keys:
    g[k][()]
    if k == 'CX_b2_BL(I)':
        correct_key = 'CX_x_BL(I)'
    else:
        correct_key = k

    unitconvs[correct_key] = dict(table=g[k][()])

    for k2, v2 in g[k].attrs.items():
        unitconvs[correct_key][k2] = v2
f.close()


table_filepath = 'nsls2br_unitconv_tables.pkl'
tables = dict(BR={})
for k, v in unitconvs.items():
    tables['BR'][k] = v['table']
with open(table_filepath, 'wb') as f:
    pickle.dump(tables, f)
