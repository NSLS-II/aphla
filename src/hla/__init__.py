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
"""

import os, sys, re

# are we using virtual ac
virtac = True
INF = 1e30
ORBIT_WAIT=5

#from chanfinder import ChannelFinderAgent
#from lattice import Lattice
#
# root of stored data
root={
    "nsls2" : "nsls2"
}

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

"""Initialize HLA"""
cfg_pkl = os.path.join(hlaroot, "machine", root["nsls2"], 'hla.pkl')
if not os.path.exists(cfg_pkl):
    raise ValueError("pkl files can not be found: " + cfg_pkl)

print "HLA main configure: ", cfg_pkl
_lat.load(cfg_pkl, mode='virtac')
#_lat.mode = 'virtac'
#_lat.save(cfg_pkl)


cfa_pkl = os.path.join(hlaroot, "machine", root["nsls2"], 'chanfinder.pkl')
if not os.path.exists(cfa_pkl):
    raise ValueError("pkl files can not be found: " + cfa_pkl)

print "HLA channel finder configure: ", cfa_pkl
_cfa.load(cfa_pkl)

# set RF frequency
caput('SR:C00-RF:G00{RF:00}Freq-SP', 499.680528631)


#
#
def eget(element, full = False, tags = [], unique = False):
    """easier get"""
    # some tags + the "default"
    chtags = ['default']
    if tags: chtags.extend(tags)
    #print __file__, tags, chtags
    if isinstance(element, str):
        ret = {}
        elemlst = getElements(element)
        pvl = _cfa.getElementChannel(elemlst, {'handle': 'get'}, 
                                     chtags, unique = unique)
        for i, pvs in enumerate(pvl):
            if len(pvs) == 1:
                ret[elemlst[i]] = caget(pvs[0])
            elif len(pvs) > 1:
                ret[elemlst[i]] = []
                for pv in pvs:
                    ret[elemlst[i]].append(caget(pv))
            else: ret[elemlst[i]] = None
            #print __file__, elemlst[i], pvs, _cfa.getElementChannel([elemlst[i]], unique = False)
        if full:
            return ret, pvl
        else: return ret
    elif isinstance(element, list):
        ret = []
        pvl = _cfa.getElementChannel(element, {'handle': 'get'}, chtags, unique = False)
        for i, pv in enumerate(pvl):
            if len(pv) == 1:
                ret.append(caget(pv[0]))
            elif len(pv) > 1:
                ret.append(caget(pv))
        if full: return ret, pvl
        else: return ret
    else:
        raise ValueError("element can only be a list or group name")


def eput(element, value):
    """
    easier put
    """
    if isinstance(element, list) and len(element) != len(value):
        raise ValueError("element list must have same size as value list")
    elif isinstance(element, str):
        val = [value]
    else: val = value[:]

    pvl = _cfa.getElementChannel(element, {'handle': 'set'}, ['default'])
    
    for i, pv in enumerate(pvl):
        caput(pv, val[i])
        
#print caget(['SR:C01-MG:G02A<VCM:L1>Fld-RB', 'SR:C01-MG:G02A<HCM:L2>Fld-RB'])

def reset_trims():
    trimx = getElements('TRIMX')
    for e in trimx: eput(e, 0.0)
    trimx = getElements('TRIMY')
    for e in trimx: eput(e, 0.0)

#from meastwiss import *
from measorm import *
from orbit import *


def removeLatticeMode(mode):
    cfg = cfg_pkl = os.path.join(hlaroot, "machine", root["nsls2"], 'hla.pkl')
    f = shelve.open(cfg, 'c')
    modes = []
    #del f['lat.twiss']
    #for k in f.keys(): print k
    for k in f.keys():
        if re.match(r'lat\.\w+\.mode', k): print "mode:", k[4:-5]
    if not mode:
        pref = "lat."
    else:
        pref = 'lat.%s.' % mode
    f.close()
