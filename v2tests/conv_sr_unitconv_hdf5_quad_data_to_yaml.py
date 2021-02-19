import sys
import pickle

import h5py
from ruamel import yaml

quad_sext_unitconvs = {}

f = h5py.File('/epics/aphla/apconf/nsls2/sr_unitconv.hdf5', 'r')
g = f['UnitConversion']
for k in list(g):
    if not k.startswith('rot_coil_'):
        continue

    quad_sext_unitconvs[k] = dict(table=g[k][()])

    for k2, v2 in g[k].attrs.items():
        quad_sext_unitconvs[k][k2] = v2
f.close()


print(set([tuple(list(v)) for k, v in quad_sext_unitconvs.items()]))

for prop in list(quad_sext_unitconvs[list(quad_sext_unitconvs)[0]]):
    if prop in ('table', 'elements', 'handle'):
        continue
    print(prop)
    print(set([v2 for k, v in quad_sext_unitconvs.items()
               for k2, v2 in v.items() if k2 == prop]))

prop = 'elements'
print([v2.astype(str).tolist() for k, v in quad_sext_unitconvs.items()
       for k2, v2 in v.items() if k2 == prop])
print(set([len(v2) for k, v in quad_sext_unitconvs.items()
           for k2, v2 in v.items() if k2 == prop]))

prop = 'handle'
print(set([tuple(v2.astype(str).tolist()) for k, v in quad_sext_unitconvs.items()
           for k2, v2 in v.items() if k2 == prop]))

table_filepath = 'nsls2sr_unitconv_tables.pkl'
tables = dict(SR={})
for k, v in quad_sext_unitconvs.items():
    tables['SR'][k] = v['table']
with open(table_filepath, 'wb') as f:
    pickle.dump(tables, f)

com_seq = yaml.comments.CommentedSeq
com_map = yaml.comments.CommentedMap

yaml_dict = com_map()
anchors = dict(quad=None, sext=None)
# Make sure to convert numpy objects (int & str) into Pytho objects.
# Otherwise, yaml dumping will fail.
for k, v in quad_sext_unitconvs.items():
    assert len(v['elements']) == 1
    elem_name = v['elements'][0].decode()
    assert elem_name not in yaml_dict

    if elem_name.startswith('q'):
        magnet_type = 'quad'
    elif elem_name.startswith('s'):
        magnet_type = 'sext'
    else:
        raise ValueError()

    if anchors[magnet_type] is None:
        d = com_map({
            'elements': com_seq([elem_name]),
            'fields': com_seq([v['field'].decode()]),
            'handles': com_seq(['readback', 'setpoint']),
            'src_unitsys': None, 'dst_unitsys': 'phy',
            'src_unit': 'A', 'dst_unit': v['dst_unit'].decode(),
            'class': 'interpolation', 'invertible': 1, 'calib_factor': 0.9988,
            'polarity': int(v['polarity']), 'table_key': k
        })

        d.yaml_set_anchor(magnet_type)
        anchors[magnet_type] = d
    else:
        d = com_map({
            'elements': com_seq([elem_name]),
            'polarity': int(v['polarity']), 'table_key': k
        })

        d.add_yaml_merge([(0, anchors[magnet_type])])

    yaml_dict.insert(len(yaml_dict), elem_name, d)

    for _k in ['elements', 'fields', 'handles']:
        yaml_dict[elem_name][_k].fa.set_flow_style()

root = com_map()
root.insert(0, 'SR', yaml_dict)

Y = yaml.YAML()
Y.default_flow_style = False
#Y.dump(root, sys.stdout)
with open('nsls2unitconv_quads_sexts.yaml', 'w') as f:
    Y.dump(root, f)
