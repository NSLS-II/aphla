#!/usr/bin/env python
import sys, os, random, time
from PyQt4 import QtGui, QtCore

from numpy import arange, sin, pi, random
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

import cothread
import cothread.catools as catools

def read_correctors(f):
    dat = open(f, 'r').readlines()
    pv = []
    for line in dat:
        if line.split()[2] == 'NULL': continue
        if line.split()[-1].find('TRIM') < 0: continue
        pv.append(line.split()[2])
        #print line.strip()
    return pv

def reset_hvcm(pvlst):
    for pv in pvlst:
        if pv.find("CM") > 0 and pv.find("SP") > 0:
            print "Setting ", pv
            catools.caput(pv, 0.0)
        
def filter_corrector(pvlst):
    pvs = []
    for pv in pvlst:
        if pv.find("CM") > 0 and pv.find("SP") > 0:
            pvs.append(pv)
    return pvs

def random_set(pvs, amp = 1e-6):
    newx = random.randn()*amp
    i = random.randint(len(pvs))
    while abs(newx) > amp:
        newx = random.randn()*amp
    print "Setting ", i, pvs[i], 
    catools.caput(pvs[i], newx)
    sys.stdout.flush()
    time.sleep(2)
    print catools.caget(pvs[i])
    sys.stdout.flush()
    return pvs[i]

if __name__ == "__main__":
    pvlst = read_correctors('../machine/nsls2/va/lat_conf_table.txt')
    #print pv
    reset_hvcm(pvlst)
    pvlst = filter_corrector(pvlst)
    #print pvlst
    #sys.exit(0)

    for i in range(30):
        print i, 
        pv = random_set(pvlst, 2e-6)
        sys.stdout.flush()
        #time.sleep(20)
        #catools.caput(pv, 0.0)
        time.sleep(5)
    print "DONE"
