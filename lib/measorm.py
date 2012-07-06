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

from orm import Orm

import logging
logger = logging.getLogger(__name__)

def measOrbitRm(bpm, trim, output):
    """Measure the beta function by varying quadrupole strength"""
    #print "BPM: ", len(bpm)
    #print "TRIM:", len(trim)
    logger.info("Orbit RM shape (%d %d)" % (len(bpm), len(trim)))
    orm = Orm(bpm, trim)
    orm.measure(output = output, verbose=1)
    return orm

# testing ...

def measChromRm():
    """
    measure chromaticity response matrix
    """
    pass

def getSubOrm(bpm, trim, flags = 'XX'):
    """
    get submatrix of Orm
    """
    #return _orm.getSubMatrix(bpm, trim, flags)
    pass


