import traceback

import numpy as  np

import aphla as ap

#ap.machines.load('nsls2', 'SR')
#ap.machines.load('nsls2', 'SR', update_cache=True)
ap.machines.loadfast('nsls2', 'SR') # Deprecated, but kept for backward compatibility

if False:
    print(ap.get_op_mode())
    print(ap.OP_MODE)
    ap.set_op_mode(1)
    print(ap.OP_MODE)
    print(ap.get_op_mode())
    ap.set_op_mode_str('online')
    print(ap.get_op_mode_str())
    try:
        ap.set_op_mode_str('ooo')
    except:
        traceback.print_exc()
    try:
        ap.set_op_mode(2)
    except:
        traceback.print_exc()
    ap.set_op_mode_str('simulation')
else:
    ap.set_op_mode_str('simulation')


#ap.engines.load()
#ap.engines.load('pyelegant')

#ap.models.load() # Load the default "17ids"
#ap.models.load(submachine='SR', engine_name='pyelegant', model_name='3dw')
ap.models.load(submachine='SR', engine_name='pyelegant', model_name='bare')

#pe = ap.engines.getEngine()
#pe.disable_stdout()

bpm = ap.getElements('BPM')[0]
print(bpm.get('x0', handle='readback', unitsys='model'))
#print(bpm.get('x0', handle='readback', unitsys='pyelegant'))

quads = ap.getElements('QUAD')
e = quads[0]
e._field['b1'].mvrb
# [{'pyelegant': {'elem_name': 'QH1G2C30A', 'property': 'K1'}}]

for unitsys in [None, 'phy', 'pyelegant', 'model']:
    print(e.get('b1', handle='readback', unitsys=unitsys),
          e.getUnit('b1', handle='readback', unitsys=unitsys))

print(ap.getTunes(source='machine'))
print(ap.getTunes(source='model'))
for plane in ['x', 'h', 'y', 'v']:
    print(plane, ap.getTune(plane, source='machine'))
    print(plane, ap.getTune(plane, source='model'))
    print(plane, ap.getTune(plane, source='database'))

print(ap.getChromaticities(source='model'))
print(ap.getChromaticities(source='database'))
for plane in ['x', 'h', 'y', 'v']:
    print(ap.getChromaticity(plane, source='model'))
    print(ap.getChromaticity(plane, source='database')) # TODO


ar1 = ap.getBeta('BPM', search_model_elem_names=False) # default = False
ar1a = ap.getBeta('BPM', search_model_elem_names=True) # should result in an empty array
ar1b = ap.getBeta('*', search_model_elem_names=True)
print(ar1.shape, ar1a.shape, ar1b.shape)
ar2 = ap.getBeta('BPM', spos=True)
ar3 = ap.getBeta('BPM', source='model')
ar4 = ap.getBeta('BPM', source='database')

np.max(np.abs(ar3 - ar4))

ar = ap.getAlpha('BPM')
ar = ap.getEta('BPM')
ar = ap.getEtap('BPM')
ar = ap.getPhase('BPM')
ar = ap.getPhi('BPM') # exactly the same as ap.getPhase()

for k in ['s', 'betax', 'betay', 'alphax', 'alphay', 'etax', 'etay',
          'etaxp', 'etayp', 'phix', 'phiy']:
    print(f'{k}: {ap.getTwissUnit(k)}')


print