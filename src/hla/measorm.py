#!/usr/bin/env python

"""
Response Matrix Measurement
----------------------------------

"""

import os, sys, time
from os.path import join, splitext
#from cothread.catools import caget, caput
import numpy as np
import shelve

from . import _lat
from . import _cfa
from . import _orm
from catools import caget, caput, caputwait, Timedout

import matplotlib.pylab as plt


def measOrbitRm(bpm, trim):
    """Measure the beta function by varying quadrupole strength"""
    print "EPICS_CA_MAX_ARRAY_BYTES:", os.environ['EPICS_CA_MAX_ARRAY_BYTES']
    print "EPICS_CA_ADDR_LIST      :", os.environ['EPICS_CA_ADDR_LIST']
    print "BPM: ", len(bpm)
    print "TRIM:", len(trim)

    orm = Orm(bpm, trim)
    orm.measure(verbose=1)
    return orm

# testing ...

def measChromRm():
    """
    measure chromaticity response matrix
    """
    pass

def getSubOrm(bpm, trim, flags = 'XX'):
    return _orm.getSubMatrix(bpm, trim, flags)


