#!/usr/bin/env python

"""
Response Matrix Measurement
----------------------------------

"""

import os, sys, time
#import numpy as np
#import shelve

from orm import Orm

import logging
logger = logging.getLogger(__name__)

def measOrbitRm(bpm, trim, output):
    """
    Measure the beta function by varying quadrupole strength
    """
    #print "BPM: ", len(bpm)
    #print "TRIM:", len(trim)
    logger.info("Orbit RM shape (%d %d)" % (len(bpm), len(trim)))
    orm = Orm(bpm, trim)
    orm.measure(output = output, verbose=1)
    return orm


def measChromRm():
    """
    measure chromaticity response matrix
    
    NotImplemented
    """
    raise NotImplementedError()

def getSubOrm(bpm, trim, flags = 'XX'):
    """
    get submatrix of Orm

    NotImplemented
    """
    #return _orm.getSubMatrix(bpm, trim, flags)
    raise NotImplementedError()


