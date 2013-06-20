#!/usr/bin/python

import sys

from rampgenerator.core.loader import Loader

MAX_TIME_SLICES = 10150  # waveform length
MAX_DELTA = 200 	 # dI/dt
BIPOLAR = True

def main():
    t = [0, 500, 10000, 10149]
    x = [0, 1, 1, 0]
    pv_name = 'BR:A2-PS{6A:CY1}I-SP'

    ramp = zip(t, x)

    rl = Loader('plain', pv_name=pv_name, bipolar=BIPOLAR, max_time_slices=MAX_TIME_SLICES)
    print rl.load_from_list(MAX_DELTA, ramp)

if __name__ == '__main__':
    main()
