#!/usr/bin/env python

from __future__ import print_function


"""
HLA Module
-----------

This is an object-orient high level accelerator control library.

A procedural interface is provided.

   
:author: Lingyun Yang
:license:

Modules include:

    :mod:`hla.machines`

        define machine specific settings, create lattice from channel
        finder service for different accelerator complex.

    :mod:`hla.lattice`

        define the :class:`~hla.lattice.CaElement`, :class:`~hla.lattice.Twiss`,
        :class:`~hla.lattice.Lattice` class

    :mod:`hla.orbit`

        defines orbit retrieve routines

    :mod:`hla.hlalib`

        defines procedural interface
        
"""

__version__ = "0.3.0a1"


#import os, sys, re
import sys

import logging

logging.basicConfig(filename="aphlas.log",
    filemode='w',
    format='%(asctime)s - %(name)s [%(levelname)s]: %(message)s',
    level=logging.DEBUG)
logger = logging.getLogger(__name__)

from catools import *
from machines import initNSLS2VSR, initNSLS2VSRTwiss

#from current import *
from rf import *
from hlalib import *
from orbit import Orbit
from ormdata import OrmData

## """Initialize HLA"""
## cfg_pkl = os.path.join(hlaroot, "machine", root["nsls2"], 'hla.pkl')
## if not os.path.exists(cfg_pkl):
##     raise ValueError("pkl files can not be found: " + cfg_pkl)

## print >> sys.stderr, "= HLA main configure: ", cfg_pkl
## _lat.load(cfg_pkl, mode='virtac')


## cfa_pkl = os.path.join(hlaroot, "machine", root["nsls2"], 'chanfinder.pkl')
## if not os.path.exists(cfa_pkl):
##     raise ValueError("pkl files can not be found: " + cfa_pkl)

## print >> sys.stderr, "= HLA channel finder configure: ", cfa_pkl
## _cfa.load(cfa_pkl)

## import orm
## _orm = orm.Orm(bpm=[], trim=[])
## orm_pkl = os.path.join(hlaroot, "machine", root["nsls2"], 'orm.pkl')
## print >> sys.stderr, "= HLA orbit resp mat: ", orm_pkl
## _orm.load(orm_pkl)


## # set RF frequency
## from cothread import catools, Timedout
NETWORK_DOWN=False
try:
    rfpv = 'SR:C00-RF:G00{RF:00}Freq-SP'
    #print("# checking RF pv: %s" % rfpv)
    caput(rfpv, 499.680528631, timeout=1)
    #print("# Network is fine, using online PVs", file= sys.stderr)
    logger.info("network is connected. use online channel access")
except Timedout:
    logger.info("virtual accelerator is not available")
    NETWORK_DOWN = True
    pass


## #from meastwiss import *
## from measorm import *
## from orbit import *
from aptools import *
import bba
import meastwiss
## _orbit = Orbit(_cfa)


# Added by Y. Hidaka
import curve_fitting
import current

