#!/usr/bin/env python
import sys, os, time
from numpy import random
from cothread.catools import caget, caput

if __name__ == "__main__":
    f = open('../machine/nsls2/pvlist_2011_04_08.txt', 'r')
    pv = []
    for p in f.readlines():
        p = p.strip()
        if not p.endswith('-SP'): continue
        if p.find('Cor:') < 0: continue
        pv.append(p)

    pvx0 = caget(pv)
    runid = 4692 # lingyun extension

    if len(sys.argv) > 1:
        n  = int(sys.argv[1])
    else:
        n = 10

    for k in range(n):
        print k,
        i = random.randint(len(pv))
        caput(pv[i], random.rand() * 1e-4)
        print pv[i], caget(pv[i])
        sys.stdout.flush()
        time.sleep(4)
    caput(pv, pvx0)
    print "DONE"

