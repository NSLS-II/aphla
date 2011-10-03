#!/usr/bin/env python
import sys, os, time
from numpy import random
import hla

if __name__ == "__main__":
    hla.initNSLS2VSR()
    hc = hla.getElements('HCOR')
    vc = hla.getElements('VCOR')
    cor = hc + vc

    runid = 4692 # lingyun extension
    hla.hlalib._wait_for_lock(runid)

    for k in range(6):
        print k,
        i = random.randint(len(cor))
        print cor[i].name, cor[i].value,
        cor[i].value = random.rand() * 1e-7
        print cor[i].value
        sys.stdout.flush()
        time.sleep(4)
    print "DONE"
    hla.hlalib._reset_trims()
    hla.hlalib._reset_bpm_offset()

    for i in range(len(cor)):
        print cor[i].value,
    print ""

    hla.hlalib._release_lock(runid)

