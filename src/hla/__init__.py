#!/usr/bin/env python


"""
   HLA Module
   -----------

   HLA module
   
   :author:
   :license:

   HLA
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
from meastwiss import *
from measorm import *
from orbit import *
from current import *

def test():
    measBeta(quad[:5], ca=ca)
    
def init(lat):
    """Initialize HLA"""
    _cfa.load("%s/../../%s/hla.pkl" % (pt, root[lat]))
    _lat.load("%s/../../%s/hla.pkl" % (pt, root[lat]))

#
# initialize the configuration 
# init("nsls2")

def clean_init():
    d = chanfinder.ChannelFinderAgent()
    #d.importXml('/home/lyyang/devel/nsls2-hla/machine/nsls2/main.xml')
    hlaroot = '/home/lyyang/devel/nsls2-hla/'
    d.importLatticeTable(hlaroot + 'machine/nsls2/lat_conf_table.txt')
    #print d.getElements("P*")

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
    
    init("nsls2")

