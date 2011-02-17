#!/usr/bin/env python

"""TWISS Measurement
   ------------------

   :author: Lingyun Yang
   :license:

"""

import conf
import cadict

import os
from os.path import join
from cothread.catools import caget, caput

def measBeta(elem, # element or list
             neighbor_quad = True, # use nearby Quad
             num_points = 3, ca=None):
    """Measure the beta function by varying quadrupole strength"""
    pv = ca.getChannels(elem, mode='fieldRB')
    print pv
    print os.environ['EPICS_CA_MAX_ARRAY_BYTES']
    print "env", os.environ['EPICS_CA_ADDR_LIST']
    #print caget('SR:C30-MG:G02A<QDP:H1>Fld-RB')
    #print caget(u'SR:C30-MG:G02A<QDP:H1>Fld-RB')
    print caget(pv[0].encode('ascii', 'ignore'))
# testing ...

if __name__ == "__main__":
    pt = os.path.dirname(os.path.abspath(__file__))
    xmlconf = "%s/../../%s/main.xml" % (pt, conf.root['nsls2'])
    print "Using conf file:", xmlconf
    ca = cadict.CADict(xmlconf)
    #print ca
    quad = ca.findGroup("QUAD")
    measBeta(quad[1:3])
