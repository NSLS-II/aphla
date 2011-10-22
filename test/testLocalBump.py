#!/usr/bin/env python

import hla
import numpy as np

if __name__ == "__main__":
    #hla.initNSLS2VSR()
    hla.machines.loadCache()
    #hla.hlalib._reset_trims()
    hcor = hla.getElements('HCOR')
    hcor_v0 = [e.x for e in hcor]
    vcor = hla.getElements('VCOR')
    vcor_v0 = [e.y for e in vcor]

    bpm = hla.getElements('BPM')
    bpm_v0 = [e.value for e in bpm]

    bpm_v1 = [e.value for e in bpm]

    bpm_v1[0] = [0, 0]
    bpm_v1[1] = [0, 1e-4]
    bpm_v1[2] = [2e-4, 1e-4]
    bpm_v1[3] = [5e-7, 1e-4]
    bpm_v1[4] = [0, 1e-4]
    bpm_v1[5] = [0, 1e-4]
    for i in range(6, len(bpm)):
        bpm_v1[i] = [0, 0]

    hla.createLocalBump([e.name for e in bpm], [e.name for e in hcor+vcor], bpm_v1)
    #hla.createLocalBump([e.name for e in bpm], [e.name for e in hcor+vcor], bpm_v1)
