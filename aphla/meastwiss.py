#!/usr/bin/env python
from __future__ import print_function, division, absolute_import
#
"""
TWISS Measurement
~~~~~~~~~~~~~~~~~

:author: Lingyun Yang
:license:

"""

import os
from os.path import join
from .catools import caget, caput
import time
import numpy as np

from . import facility_d
from . import defaults
from .defaults import Default, set_defaults, getDynamicDefault
from .hlalib import (getOrbit, getElements, getClosest, getNeighbors, getTunes,
                     waitStableOrbit, getRfFrequency, putRfFrequency)
from .machines import getControlLimits

__all__ = [ 'measBeta', 'measDispersion', 'measChromaticity' ]

import logging
_logger = logging.getLogger("aphla.meastwiss")

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
    see `getElements` for acceptable *elem* format. Some users prefer using
    turn-by-turn BPM data to calculate the beta functions
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

def measDispersion(elem, dfmax = 5e-7, alphac = 3.6261976841792413e-04,
                   gamma = 5.870841487279844e3, num_points = 5,
                   full = False, verbose = 0):
    """measure dispersion at BPMs

    Parameters
    -----------
    elem : BPM name, list or pattern
    dfmax : float. frequency change (check the unit)
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
    dflst = np.linspace(-abs(dfmax),  abs(dfmax), num_points)

    # incase RF does not allow large step change, ramp down first
    for df in np.linspace(0, abs(dfmax), num_points)[1:-1]:
        putRfFrequency(f0 - df)
        time.sleep(2.0 / num_points)

    # avoid a bug in virtac
    obt0 = getOrbit(bpmnames)

    cod = np.zeros((len(dflst), 2*nbpm), 'd')
    for i,df in enumerate(dflst):
        v0 = getOrbit()
        putRfFrequency(f0 + df)
        if verbose > 0:
            print(i, "df=", df, " f=", f0)
        waitStableOrbit(v0)

        # repeat the put/get in case simulator did not response latest results
        obt = getOrbit(bpmnames)
        #print i, obt[0,:2], obt0[0,:2], np.shape(obt), np.shape(obt0)

        cod[i,:nbpm] = obt[:,0] - obt0[:,0]
        cod[i,nbpm:] = obt[:,1] - obt0[:,1]

    # restore
    for df in np.linspace(0, abs(dfmax), num_points):
        putRfFrequency(f0 + abs(dfmax) - df)
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


def calcChromaticity(f0, freqlst, tunelst, deg = 2,
                     gamma = 3.0e3/0.511, alphac = 3.6262e-4, verbose=0):
    """
    f0 : original RF frequency
    freqlst : a list of RF frequency for tune measurement
    tunelst : a list of tunes at different RF frequency, (n,2) shape.
    deg : degree for polynomial fitting
    gamma : beam energy. NSLS-II default is 3000.0/0.511.
    alphac : momentum compaction factor. NSLS-II default is 3.6e-4

    return chromaticities (cx, cy)
    """
    eta = alphac - 1/gamma/gamma
    dpp = (freqlst - f0) / (-f0*eta)
    p, resi, rank, sing, rcond = np.polyfit(dpp, tunelst, deg=deg, full=True)
    # chrom = p[-2,:] * (-f0*eta)
    chrom = p[-2,:]
    if verbose > 0:
        print("Coef:", p)
        print("Resi:", resi)
        print("Chrom:", chrom)
    return chrom, dpp, p

@set_defaults('aphla.measChromaticity')
def measChromaticity(
    dfmax = 2e-7, gamma = 3.0e3/0.511, alphac=Default("alphac", None),
    num_points=Default("num_points", 5), fMeasTunes = None, deg = 2,
    verbose=0, **kwargs):
    """Measure the chromaticity

    Parameters
    -----------
    dfmax - max RF frequency change (within plus/minus), 1e-6
    gamma - beam, 3.0/0.511e-3
    alphac - momentum compaction factor, 3.62619e-4
    wait - 1.5 second
    num_points - 5
    fMeasTunes - function used to get tunes. default None, use getTunes().

    returns
    --------
    chrom : chromaticity, (chx, chy)
    info : dictionary
        freq : list of frequency setting
        freq0 : initial frequency setpoint
        tune : list of tunes,  shape (num_points, 2)
        dpp : dp/p energy deviation
        obt : orbit at each f settings (initial, every df, final).
        deg : degree of polynomial fitting.
        p : polynomial coeff, shape (deg+1, 2)


    Note
    -----
    If the dfmax is too large, dispersion induced orbit change may trip the
    beam due to RF vacuum (1khz for NSLS-II case).
    """

    wait = kwargs.get('wait', getDynamicDefault('wait', 0.5))

    lim = getControlLimits()

    return # Temporarily disable this function during testing of "set_defaults"
           # decorator.

    obt = []
    f0 = getRfFrequency(handle="setpoint")

    #names, x0, y0, Isum0, timestamp, offset = \
    #    measKickedTbtData(7, (0.15, 0.2), sleep=10, output=False)
    #nu0 = (calcFftTunes(x0), calcFftTunes(y0))
    nu0 = fMeasTunes() if fMeasTunes else getTunes()


    obt.append(getOrbit(spos=True))
    #_logger.info("Initial RF freq= {0}, tunes= {1}" % (f0, nu0))

    # incase RF does not allow large step change, ramp down first
    if verbose:
        print("Initial RF freq= {0}, stepping down {1} in {2} steps".format(
              f0, -dfmax, num_points))
    for df in np.linspace(0, abs(dfmax), num_points)[1:-1]:
        putRfFrequency(f0 - df)
        time.sleep(2.0 / num_points)

    f = np.linspace(f0 - dfmax, f0 + dfmax, num_points)
    nu = np.zeros((len(f), 2), 'd')
    for i,f1 in enumerate(f):
        if verbose > 0:
            print("dfreq= {0: .2e}".format(f1 - f0), end=" ")
        putRfFrequency(f1)
        time.sleep(wait)
        nu[i,:] = fMeasTunes() if fMeasTunes else getTunes()
        obt.append(getOrbit(spos=True))
        if verbose > 0:
            print("tunes: {0:.5f} {1:.5f}".format(nu[i,0], nu[i,1]),
                  "orbit min-max: {0:.2e} {1:.2e}, {2:.2e} {3:.2e}".format(
                    np.min(obt[-1][:,0]), np.max(obt[-1][:,0]),
                  np.min(obt[-1][:,1]), np.max(obt[-1][:,1])))

    for df in np.linspace(0, abs(dfmax), num_points):
        putRfFrequency(f0 + abs(dfmax) - df)
        time.sleep(2.0 / num_points)
    obt.append(getOrbit(spos=True))

    # calculate chrom, return info
    info = {"freq": f, "tune": nu, "orbit": obt, "freq0": f0, "deg": deg}
    chrom, dpp, p = calcChromaticity(f0, f, nu, deg=deg)
    info["dpp"] = dpp
    info["p"]   = p

    return chrom, info


def _measChromaticity(**kwargs):
    """Measure the chromaticity

    Parameters
    -----------
    dfmax - max RF frequency change (within plus/minus), 1e-6
    gamma - beam, 3.0/0.511e-3
    alphac - momentum compaction factor, 3.62619e-4
    wait - 1.5 second
    num_points - 5

    returns dp/p, nu, chrom
    dpp - dp/p energy deviation
    nu - tunes
    chrom - result chromaticities
    obt - orbit at each f settings (initial, every df, final).
    """
    dfmax  = kwargs.get("dfmax", 1e-6)
    gamma  = kwargs.get("gamma", 3.0e3/.511)
    alphac = kwargs.get("alphac", 3.6261976841792413e-04)
    wait   = kwargs.get("wait", 1.5)
    npt    = kwargs.get("num_points", 5)
    verbose = kwargs.get("verbose", 0)

    eta = alphac - 1/gamma/gamma

    obt = []
    f0 = getRfFrequency(handle="setpoint")
    nu0 = getTunes()
    obt.append(getOrbit(spos=True))
    _logger.info("Initial RF freq= {0}, tunes= {1}" % (f0, nu0))

    # incase RF does not allow large step change, ramp down first
    if verbose:
        print("Initial RF freq= {0}, stepping down {1} in {2} steps".format(
              f0, -dfmax, npt))
    for df in np.linspace(0, abs(dfmax), npt)[1:-1]:
        putRfFrequency(f0 - df)
        time.sleep(2.0 / npt)

    f = np.linspace(f0 - dfmax, f0 + dfmax, npt)
    nu = np.zeros((len(f), 2), 'd')
    for i,f1 in enumerate(f):
        if verbose > 0:
            print("freq= ", f1, end=" ")
        putRfFrequency(f1)
        time.sleep(wait)
        nu[i,:] = getTunes()
        obt.append(getOrbit(spos=True))
        if verbose > 0:
            print("tunes:", nu[i,0], nu[i,1],
                  np.min(obt[-1][:,0]), np.max(obt[-1][:,0]),
                  np.min(obt[-1][:,1]), np.max(obt[-1][:,1]))

    for df in np.linspace(0, abs(dfmax), npt):
        putRfFrequency(f0 + abs(dfmax) - df)
        time.sleep(2.0 / npt)

    obt.append(getOrbit(spos=True))

    df = f - f0
    dnu = nu - np.array(nu0)
    p, resi, rank, sing, rcond = np.polyfit(df, dnu, deg=2, full=True)
    chrom = p[-2,:] * (-f0*eta)
    if verbose > 0:
        print("Coef:", p)
        print("Resi:", resi)
        print("Chrom:", chrom)
    return df/(-f0*eta), nu, chrom, obt

