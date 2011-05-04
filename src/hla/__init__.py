#!/usr/bin/env python


"""
HLA Module
-----------

This is an object-orient high level accelerator control library.

A procedural interface is provided.

   
:author: Lingyun Yang
:license:

Modules include:

    :mod:`hla.lattice`

        define the :class:`~hla.lattice.Element`, :class:`~hla.lattice.Twiss`,
        :class:`~hla.lattice.Lattice` class

    :mod:`hla.chanfinder`

        defines the :class:`~hla.chanfinder.ChannelFinderAgent` class

    :mod:`hla.orbit`

        defines orbit retrieve routines

    :mod:`hla.hlalib`

        defines procedural interface

        
"""

import os, sys, re

# are we using virtual ac
virtac = True
INF = 1e30
ORBIT_WAIT=8
NETWORK_DOWN=False
#from chanfinder import ChannelFinderAgent
#from lattice import Lattice
#
# root of stored data
root={
    "nsls2" : "nsls2"
}

# local catools
from catools import *

import lattice
_lat = lattice.Lattice()

import chanfinder
_cfa = chanfinder.ChannelFinderAgent()

# get the HLA root directory
pt = os.path.dirname(os.path.abspath(__file__))
hlaroot = os.path.normpath(os.path.join(pt, '..', '..'))

#
# testing, bypass the IRMIS database.
#

from latmanage import *
from current import *
from rf import *
from hlalib import *

"""Initialize HLA"""
cfg_pkl = os.path.join(hlaroot, "machine", root["nsls2"], 'hla.pkl')
if not os.path.exists(cfg_pkl):
    raise ValueError("pkl files can not be found: " + cfg_pkl)

print >> sys.stderr, "= HLA main configure: ", cfg_pkl
_lat.load(cfg_pkl, mode='virtac')
#_lat.mode = 'virtac'
#_lat.save(cfg_pkl)


cfa_pkl = os.path.join(hlaroot, "machine", root["nsls2"], 'chanfinder.pkl')
if not os.path.exists(cfa_pkl):
    raise ValueError("pkl files can not be found: " + cfa_pkl)

print >> sys.stderr, "= HLA channel finder configure: ", cfa_pkl
_cfa.load(cfa_pkl)

# set RF frequency
from cothread import catools, Timedout
try:
    catools.caput('SR:C00-RF:G00{RF:00}Freq-SP', 499.680528631)
    print >> sys.stderr, "= Network is fine, using online PVs"
except Timedout:
    NETWORK_DOWN = True
    pass


#from meastwiss import *
from measorm import *
from orbit import *

_orbit = Orbit(_cfa)


