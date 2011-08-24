#!/usr/bin/env python

"""
TWISS Measurement
~~~~~~~~~~~~~~~~~

:author: Lingyun Yang
:license:

"""

import os
from os.path import join
from catools import caget, caput
import numpy as np
from hlalib import getOrbit, getElements, getClosest, getNeighbors, getTunes, waitStableOrbit

def _measBetaQuad(elem, **kwargs):
    dqk1 = abs(kwargs.get('dqk1', 0.01))
    num_points = kwargs.get('num_points', 5)

    qk10 = elem.value
    qk1 = qk10 + np.linspace(-dqk1, dqk1, num_points)
    nu = np.zeros((num_points, 2), 'd')
    for i,k1 in enumerate(qk1):
        v0 = getOrbit()
        elem.value = k1
        waitStableOrbit(v0, maxwait=15)
        nu[i,:] = getTunes()

    elem.value = qk10
    return qk1, nu

def measBeta(elem, dqk1 = 0.01, # element or list
             num_points = 3, verbose=0):
    """Measure the beta function by varying quadrupole strength"""

    elems = getElements(elem, return_list=True)
    if not elems:
        raise ValueError("can not find element '%s'" % elem)
    if verbose:
        print "# fitting %d quadrupoles:" % len(elems)
        print "# " + ' '.join([q.name for q in elems])
        

    kwargs = {'dqk1': dqk1, 'num_points': num_points, 'verbose': verbose}

    nux, nuy = getTunes()
    nu = np.zeros((num_points, 2*len(elems)), 'd')
    k1 = np.zeros((num_points, len(elems)), 'd')
    beta = np.zeros((2, len(elems)), 'd')
    for i,q in enumerate(elems):
        # is an element
        k1[:,i], nu[:,2*i:2*i+2] = _measBetaQuad(q, **kwargs)
        if verbose:
            print i, q.name, q.value, 
        p, res, rank, sv, rcond = np.polyfit(k1[:,i], nu[:,2*i:2*i+2], deg=1, full=True)
        beta[:,i] = p[0,:]*4*np.pi/q.length
        print q.sb, q.name, beta[0,i], beta[1,i]

    return k1, nu, beta
# testing ...


if __name__ == "__main__":
    pt = os.path.dirname(os.path.abspath(__file__))
    xmlconf = "%s/../../%s/main.xml" % (pt, conf.root['nsls2'])
    print "Using conf file:", xmlconf, "in meastwiss.py"
    ca = cadict.CADict(xmlconf)
    #print ca
    quad = ca.findGroup("QUAD")
    measBeta(quad[1:3])
