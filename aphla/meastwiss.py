#!/usr/bin/env python

"""
TWISS Measurement
~~~~~~~~~~~~~~~~~

:author: Lingyun Yang
:license:

"""
from __future__ import print_function

import os
from os.path import join
from catools import caget, caput
import time
import numpy as np
from hlalib import (getOrbit, getElements, getClosest, getNeighbors, getTunes, 
                    waitStableOrbit, getRfFrequency, setRfFrequency)

__all__ = [ 'measBeta', 'measDispersion', 'measChromaticity' ]

import logging
_logger = logging.getLogger(__name__)

def _measBetaQuad(elem, **kwargs):
    dqk1 = abs(kwargs.get('dqk1', 0.01))
    num_points = kwargs.get('num_points', 5)
    minwait = kwargs.get('minwait', 3)

    qk10 = elem.k1
    qk1 = qk10 + np.linspace(-dqk1, dqk1, num_points)
    nu = np.zeros((num_points, 2), 'd')
    for i,k1 in enumerate(qk1):
        v0 = getOrbit()
        elem.k1 = k1
        waitStableOrbit(v0, minwait=minwait, maxwait=15)
        nu[i,:] = getTunes()

    elem.k1 = qk10
    return qk1, nu

def measBeta(elem, dqk1 = 0.01, full = False, num_points = 3, verbose=0):
    """
    Measure the beta function by varying quadrupole strength

    Parameters
    -----------
    elem : element name, name list or pattern.
    dqk1 : float. the quadrupole change range [-dqk1, dqk1]
    full : bool. returns more data besides beta
    num_points : int. points in [-dqk1, dqk1] to fit the line, default 3.
    verbose : verbose

    Returns
    --------
    beta : numpy array (N_elements, 3). fitted betax, betay and s_center
    k1, nu : optional. present only if *full*=True.
        k1 is numpy array (N_elements, num_points), quadrupole settings. nu is
        numpy array (N_elements, num_points, 2). tunes.

    Notes
    ------
    see `getElements` for acceptable *elem* format. 

    """

    elems = getElements(elem)
    if elems is None:
        raise ValueError("can not find element '%s'" % elem)
    if verbose:
        print("# fitting %d quadrupoles:" % len(elems))
        print("# " + ' '.join([q.name for q in elems]))
        

    kwargs = {'dqk1': dqk1, 'num_points': num_points, 'verbose': verbose}

    nux, nuy = getTunes()
    nu = np.zeros((len(elems), num_points, 2), 'd')
    k1 = np.zeros((len(elems), num_points), 'd')
    beta = np.zeros((len(elems), 3), 'd')
    for i,q in enumerate(elems):
        beta[i,-1] = (q.sb + q.se)/2.0
        # is an element
        k1[i,:], nu[i,:,:] = _measBetaQuad(q, **kwargs)
        if verbose:
            print(i, q.name, q.k1, end=" ")
        p, res, rank, sv, rcond = np.polyfit(
            k1[i,:], nu[i,:,:], deg=1, full=True)
        # p[0,k] is the highest power for dataset k
        beta[i,:2] = p[0,:]*4*np.pi/q.length
        # reverse the k1 for vertical direction
        beta[i,1] = -beta[i,1]
        print(q.sb, q.name, beta[i,0], beta[i,1], p[0,:])

    if full: return beta, k1, nu
    else: return beta

def measDispersion(elem, dfreq = 5e-7, alphac = 3.6261976841792413e-04,
                   gamma = 5.870841487279844e3, num_points = 5,
                   full = False, verbose = 0):
    """measure dispersion at BPMs

    Parameters
    -----------
    elem : BPM name, list or pattern
    dfreq : float. frequency change (check the unit)
    alphac : float. momentum compaction factor.
    gamma : float. beam energy.
    num_points : int. points to fit line
    full : reserved.

    Returns
    --------
    eta : numpy.array. (nelem, 3) with columns etax, etay and s

    Examples
    ---------
    >>> eta = measDispersion('p*c0[1-4]*')

    """

    eta = alphac - 1.0/gamma/gamma

    bpmobj = [ b for b in getElements(elem) 
               if b.family == 'BPM']
    bpmnames = [b.name for b in bpmobj]
    nbpm = len(bpmnames)

    _logger.info("measure dispersions at %d elements '%s'" % 
                (len(bpmnames), str(elem)))

    f0 = getRfFrequency(handle="setpoint")
    dflst = np.linspace(-abs(dfreq),  abs(dfreq), num_points)

    # incase RF does not allow large step change, ramp down first
    for df in np.linspace(0, abs(dfreq), num_points)[1:]:
        setRfFrequency(f0 - df)
        time.sleep(2.0 / num_points)

    # avoid a bug in virtac
    obt0 = getOrbit(bpmnames)

    cod = np.zeros((len(dflst), 2*nbpm), 'd')
    for i,df in enumerate(dflst): 
        v0 = getOrbit()
        setRfFrequency(f0 + df)
        if verbose > 0:
            print(i, "df=", df, " f=", f0)
        waitStableOrbit(v0)
        
        # repeat the put/get in case simulator did not response latest results
        obt = getOrbit(bpmnames)
        #print i, obt[0,:2], obt0[0,:2], np.shape(obt), np.shape(obt0)

        cod[i,:nbpm] = obt[:,0] - obt0[:,0]
        cod[i,nbpm:] = obt[:,1] - obt0[:,1]

    # restore
    for df in np.linspace(0, abs(dfreq), num_points):
        setRfFrequency(f0 + abs(dfreq) - df)
        time.sleep(2.0 / num_points)

    # fitting
    p = np.polyfit(dflst, cod, deg = 1)
    disp = -p[0,:] * f0 * eta
    s = np.array([e.sb for e in bpmobj], 'd')
    ret = np.zeros((len(bpmobj), 3), 'd')
    ret[:,0] = disp[:nbpm]
    ret[:,1] = disp[nbpm:]
    ret[:,2] = s
    if verbose > 0:
        for i,bpm in enumerate(bpmobj):
            print(i, bpm.name, bpm.sb, ret[i,0], ret[i,1])
    return ret


def measChromaticity(**kwargs):
    """Measure the chromaticity

    Parameters
    -----------
    dfmax - max RF frequency change (within plus/minus), 1e-6
    gamma - beam, 3.0/0.511e-3
    alphac - momentum compaction factor, 3.62619e-4
    wait - 1.5 second

    returns f, nu, chrom
    f - RF frequency setpoint
    nu - tunes 
    chrom - result chromaticities 
    """
    dfreq  = kwargs.get("dfmax", 1e-6)
    gamma  = kwargs.get("gamma", 3.0e3/.511)
    alphac = kwargs.get("alphac", 3.6261976841792413e-04)
    wait   = kwargs.get("wait", 1.5)
    npt    = kwargs.get("npoints", 6)
    verbose = kwargs.get("verbose", 0)

    eta = alphac - 1/gamma/gamma

    f0 = getRfFrequency()
    nu0 = getTunes()
    _logger.info("Initial RF freq=%s, tunes=%s" % (str(f0), str(nu0)))

    f = np.linspace(f0 - dfmax, f0 + dfmax, npt)
    nu = np.zeros((len(f), 2), 'd')
    for i,f1 in enumerate(f):
        if verbose > 0:
            print("freq= ", f1, end=" ")
        putRfFrequency(f1)
        time.sleep(wait)
        nu[i,:] = getTunes()
        if verbose > 0:
            print("tunes:", nu[i,0], nu[i,1])

    putRfFrequency(f0)

    df = f - f0
    dnu = nu - np.array(nu0)
    p, resi, rank, sing, rcond = np.polyfit(df, dnu, deg=2, full=True)
    chrom = p[-2,:] * (-f0*eta)
    if verbose > 0:
        print("Coef:", p)
        print("Resi:", resi)
        print("Chrom:", chrom)
    return f, nu, chrom

