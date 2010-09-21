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
        pv.append(line.split()[3])
    #print pv
    return pv

def reset_hvcm(pvlst):
    for pv in pvlst:
        if pv.find("CM") > 0:
            print "Setting ", pv[1:-1]
            catools.caput(pv[1:-1], 0.0)
        
def filter_corrector(pvlst):
    pvs = []
    for pv in pvlst:
        if pv.find("CM") > 0:
            # remove \"\" at both ends.
            pvs.append(pv.strip()[1:-1])
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
    pvlst = read_correctors('../nsls2/conf/lat_conf_table.txt')
    #print pv
    reset_hvcm(pvlst)
    pvlst = filter_corrector(pvlst)
    sys.exit(0)

    for i in range(30):
        print i, 
        pv = random_set(pvlst, 2e-8)
        sys.stdout.flush()
        #time.sleep(20)
        #catools.caput(pv, 0.0)
        time.sleep(5)
    print "DONE"
