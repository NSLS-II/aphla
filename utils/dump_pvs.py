#!/usr/bin/env python
import sys, os, time, datetime
from numpy import random
from cothread.catools import caget, caput
import shelve

def read():
    f = open('../machine/nsls2/pvlist_2011_04_08.txt', 'r')
    pv = [p.strip() for p in f.readlines()]
    pvx0 = caget(pv)
    #for i,p in enumerate(pv):
    #    print i, pv[i], pvx0[i]
    s = datetime.datetime.now().strftime("%Y_%m_%d_%H%M%S")
    f = shelve.open('dump_pvs_%s.pkl' % s)
    f['pvs'] = pv
    f['values'] = pvx0
    f.close()

def write(f):
    for s in open(f, 'r').readlines():
        i, pv, x = s.split()
        caput(pv.strip(), x)
        print i, pv, caget(pv.strip())

if __name__ == "__main__":
    if len(sys.argv) == 1 or sys.argv[1] == '-r':
        read()
    elif len(sys.argv) == 3:
        write(sys.argv[2])


