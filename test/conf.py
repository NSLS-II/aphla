#!/usr/bin/env python

import sys, os, time
from cothread.catools import caget, caput

# set up directories
if not 'HLA_ROOT' in os.environ:
    rt,ext = os.path.splitext(os.path.realpath(sys.argv[0]))
    HLA_ROOT = os.path.split(os.path.split(rt)[0])[0]
    os.environ['HLA_ROOT'] = HLA_ROOT
else:
    HLA_ROOT = os.environ['HLA_ROOT']
    
print "= HLA root directory: ", HLA_ROOT
sys.path.append(os.path.join(HLA_ROOT, 'src'))
sys.path.append(os.path.join(HLA_ROOT, 'test'))

__RT=os.environ['HLA_ROOT']

HLAPKL  = os.path.join(__RT, 'machine', 'nsls2', 'hla.pkl')
CFAPKL  = os.path.join(__RT, 'machine', 'nsls2', 'chanfinder.pkl')
LATCONF = os.path.join(__RT, 'machine', 'nsls2', 'lat_conf_table.txt')

ORMX = os.path.join(__RT, 'machine', 'nsls2', 'ormx.pkl')
ORMY = os.path.join(__RT, 'machine', 'nsls2', 'ormy.pkl')

def wait_for_svr(val = [0], newval = 2):
    wt = 0
    while True:
        if caget('SVR:LOCKED') in val:
            caput('SVR:LOCKED', newval, wait=True)
            if wt > 0: print ''
            break
        if wt == 0: sys.stdout.write("Waiting ")
        else: sys.stdout.write('.'),
        sys.stdout.flush()
        wt = wt + 1
        time.sleep(30)
    pass

def reset_svr(val = 0):
    caput('SVR:LOCKED', val, wait=True)


