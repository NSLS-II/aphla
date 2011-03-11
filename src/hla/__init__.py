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

import os, sys

# are we using virtual ac
virtac = True
INF = 1e30

#from chanfinder import ChannelFinderAgent
#from lattice import Lattice
#
# root of stored data
root={
    "nsls2" : "machine/nsls2"
}

import lattice
_lat = lattice.Lattice()

import chanfinder
_cfa = chanfinder.ChannelFinderAgent()

# get the HLA root directory
pt = os.path.dirname(os.path.abspath(__file__))

#
# testing, bypass the IRMIS database.
#

from latmanage import *
from current import *
from rf import *

def init(lat):
    """Initialize HLA"""
    _cfa.load("%s/../../%s/hla.pkl" % (pt, root[lat]))
    _lat.load("%s/../../%s/hla.pkl" % (pt, root[lat]))

#
# initialize the configuration 
# init("nsls2")

def clean_init():
    """Clean initialization, will call init

    .. warning::

      Only used for testing software while the real machine is not built
      yet. --L.Y.
    """
    d = chanfinder.ChannelFinderAgent()
    #d.importXml('/home/lyyang/devel/nsls2-hla/machine/nsls2/main.xml')
    hlaroot = '/home/lyyang/devel/nsls2-hla/'
    d.importLatticeTable(hlaroot + 'machine/nsls2/lat_conf_table.txt')
    d.import_virtac_pvs()
    d.fix_bpm_xy()
    #print d.getElements("P*")
    #d.clear_trim_settings()

    #d.checkMissingChannels(hlaroot + 'machine/nsls2/pvlist_2011_03_03.txt')
    d.save(hlaroot + 'machine/nsls2/hla.pkl')
    #print d

    # load lattice
    lat = lattice.Lattice()
    lat.importLatticeTable(hlaroot + 'machine/nsls2/lat_conf_table.txt')
    lat.init_virtac_twiss()
    lat.init_virtac_group()
    lat.save(hlaroot + 'machine/nsls2/hla.pkl')
    #print lat

    # set RF frequency
    caput('SR:C00-RF:G00<RF:00>Freq-SP', 499.680528631)

    init("nsls2")

def check():
    """
    .. note::

        Used by Lingyun Yang for testing
    """
    _cfa.checkMissingChannels('/home/lyyang/devel/nsls2-hla/machine/nsls2/pvlist_2011_03_03.txt')


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

#from meastwiss import *
from measorm import *
from orbit import *
