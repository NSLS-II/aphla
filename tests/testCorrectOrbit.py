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
    bpm_v0 = np.array([e.value for e in bpm], 'd')

    print "Initial Euclidian norm:", np.linalg.norm(bpm_v0[:,0]), \
        np.linalg.norm(bpm_v0[:,1])

    ih = np.random.randint(0, len(hcor), 4)
    for i in ih:
        hcor[i].x = np.random.rand() * 1e-5

    iv = np.random.randint(0, len(vcor), 4)
    for i in iv:
        vcor[i].y = np.random.rand() * 1e-5

    raw_input("Press Enter to correct orbit...")

    cor = []
    #cor.extend([e.name for e in hcor])
    #cor.extend([e.name for e in vcor])
    cor.extend([hcor[i].name for i in ih])
    cor.extend([vcor[i].name for i in iv])

    hla.correctOrbit([e.name for e in bpm], cor)

    raw_input("Press Enter to recover orbit...")
    bpm_v1 = np.array([e.value for e in bpm], 'd')
    print "Euclidian norm:", np.linalg.norm(bpm_v1[:,0]), \
        np.linalg.norm(bpm_v1[:,1])

    for i in ih:
        hcor[i].x = hcor_v0[i]
        
    for i in iv:
        vcor[i].y = vcor_v0[i]

    raw_input("Press Enter ...")
    bpm_v2 = np.array([e.value for e in bpm], 'd')
    print "Euclidian norm:", np.linalg.norm(bpm_v2[:,0]), \
        np.linalg.norm(bpm_v2[:,1])

    for i in range(len(ih)):
        x, y = hcor[ih[i]].x, vcor[iv[i]].y
        print i, (x - hcor_v0[ih[i]]), (y - vcor_v0[iv[i]])

