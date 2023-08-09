import json

import numpy as np

import aphla as ap

print(ap.__version__)

ap.machines.load('nsls2', 'SR')

assert str(ap.machines._lat.OUTPUT_DIR) == '/epics/aphla/SR'

bpms = ap.getElements('BPM')
assert len(bpms) == 180

ap.models.load(model_name='bare')

ap.switchToSim()

assert ap.machines.avail_names() == ['LN', 'LTD1', 'LTD2', 'LTB', 'BR', 'BTD', 'BTS', 'SR']

assert ap.machines.names() == ['SR']

assert ap.engines.avail_names() == ['pyelegant']

ap.engines.names() == ['pyelegant']

assert json.dumps(ap.models.avail_names()) == json.dumps({'SR': {'pyelegant': ['bare', '3dw', '17ids']}})

assert json.dumps(ap.models.names()) == json.dumps({'SR': {'pyelegant': ['bare']}})

np.testing.assert_almost_equal(ap.getTunes()[0], 0.22128, decimal=5)
np.testing.assert_almost_equal(ap.getTunes()[1], 0.25978, decimal=5)

ap.switchToOnline()

print(f'Online tunes = {ap.getTunes()}')

ap.switchToSim()

np.testing.assert_almost_equal(ap.getChromaticities()[0], 2.00000, decimal=5)
np.testing.assert_almost_equal(ap.getChromaticities()[1], 1.78989, decimal=5)

print(ap.getBeta('p[hlm]*', spos=True))

assert ap.getTwissUnit('betax') == 'm'
assert ap.getTwissUnit('phix') == 'rad'
assert ap.getTwissUnit('etaxp') == 'unitless'
