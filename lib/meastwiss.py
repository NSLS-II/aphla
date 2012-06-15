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
from rf import getRfFrequency, putRfFrequency

def _measBetaQuad(elem, **kwargs):
    dqk1 = abs(kwargs.get('dqk1', 0.01))
    num_points = kwargs.get('num_points', 5)

    qk10 = elem.k1
    qk1 = qk10 + np.linspace(-dqk1, dqk1, num_points)
    nu = np.zeros((num_points, 2), 'd')
    for i,k1 in enumerate(qk1):
        v0 = getOrbit()
        elem.k1 = k1
        waitStableOrbit(v0, maxwait=15)
        nu[i,:] = getTunes()

    elem.k1 = qk10
    return qk1, nu

def measBeta(elem, dqk1 = 0.01, # element or list
             num_points = 3, verbose=0):
    """
    Measure the beta function by varying quadrupole strength
    
    - elem, element name
    - dqk1
    - num_points points to fit the line
    - verbose

    returns k1, nu, beta
    """

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
            print i, q.name, q.k1, 
        p, res, rank, sv, rcond = np.polyfit(k1[:,i], nu[:,2*i:2*i+2], deg=1, full=True)
        beta[:,i] = p[0,:]*4*np.pi/q.length
        # reverse the k1 for vertical direction
        beta[1,i] = -beta[1,i]
        print q.sb, q.name, beta[0,i], beta[1,i]

    return k1, nu, beta

def measDispersion(elem, dfreq = 1e-5, alphac = 3.6261976841792413e-04,
                   gamma = 5.870841487279844e3, num_points = 5,
                   verbose = 0):
    """
    measure dispersion

    - *elem* BPM name, list or pattern
    - *df* frequency change
    - *alphac* 
    - *gamma* 

    ::

      >>> etax, etay = measDispersion('P*C0[1-4]*')
    """

    eta = alphac - 1.0/gamma/gamma

    bpmobj = [ b for b in getElements(elem, return_list = True) 
               if b.family == 'BPM']
    bpmnames = [b.name for b in bpmobj]
    nbpm = len(bpmnames)

    print "elements:", len(bpmnames), bpmnames
    # f in MHz
    f0 = getRfFrequency()
    dflst = np.linspace(-abs(dfreq),  abs(dfreq), num_points)

    # avoid a bug in virtac
    obt0 = getOrbit(bpmnames)

    cod = np.zeros((len(dflst), 2*nbpm), 'd')
    for i,df in enumerate(dflst): 
        v0 = getOrbit()
        putRfFrequency(f0 + df)
        waitStableOrbit(v0)

        # repeat the put/get in case simulator did not response latest results
        obt = getOrbit(bpmnames)
        #print i, obt[0,:2], obt0[0,:2], np.shape(obt), np.shape(obt0)

        cod[i,:nbpm] = obt[:,0] - obt0[:,0]
        cod[i,nbpm:] = obt[:,1] - obt0[:,1]

    
    # restore
    putRfFrequency(f0)

    # fitting
    p = np.polyfit(dflst, cod, deg = 1)
    disp = -p[0,:] * f0 * eta
    return disp[:nbpm], disp[nbpm:]

    
