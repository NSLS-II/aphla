import traceback

import aphla as ap

ap.machines.load('nsls2', 'SR')
#ap.machines.load('nsls2', 'SR', use_cache=True)
#ap.machines.load('nsls2', 'SR', save_cache=True)

# Generate a model

engine_name = 'pyelegant'
model_name = '17ids'
model = ap.models.VariableModel(engine_name, model_name)


#ap.engines.load()
#ap.engines.load('pyelegant')

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


out = ap.getBeta('BPM')


bpm = ap.getElements('BPM')[0]

bpm.get('x0', handle='readback', unitsys='model')

print