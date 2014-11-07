"""
:author: Lingyun Yang <lyyang@bnl.gov>
:license:

BPM turn-by-turn data analysis
"""

from __future__ import print_function

import numpy as np
import time, datetime, sys, os
import itertools
import tempfile

from . import machines
import logging

__all__ = [ 'calcFftTune', 'calcTunes',
            'calcPhase', 'calcPhaseAdvance', 'calcBetaAu']

_logger = logging.getLogger(__name__)



def calcFftTune(x):
    """
    x - (nbpm, nturns)
    """
    nbpm, nturn = np.shape(x)
    xc = np.average(x, axis=-1)
    Fx = np.zeros_like(x)
    for i in range(nbpm): #[1,2,3,4,5,6]:
        Fx[i,:] = np.abs(np.fft.fft(x[i,:] - xc[i]))
    Fs = np.sum(Fx, axis=0)
    i = np.argmax(Fs[:nturn/2])
    return i * 1.0/nturn

def calcTunes(x, y, **kwargs):
    """
    x, y - (nbpm, nturns) data
    """
    nux = calcFftTune(x)
    nuy = calcFftTune(y)
    return (nux, nuy)

def _calcPhase(x, **kwargs):
    """
    x - 1D Tbt data
    nulim - tuple of tune range
    nu - tune. If not given, use fft on x and find tune within nulim.
    verbose - default 0
    """
    if len(x) < 128 or len(np.shape(x)) > 1:
        raise RuntimeError("only accept 1D array size >= 128")
    N = len(x)
    X = np.fft.fft(x - np.average(x))

    nu = kwargs.get("nu", None)
    if nu is None:
        nulim = kwargs.get("nulim", (0.0, 0.5))
        i0, i1 = int(np.floor(nulim[0] * N)), int(np.ceil(nulim[1] * N))
        f = np.fft.fftfreq(N)
        i = np.argmax(np.abs(X[i0:i1])) + i0
        nu = 1+f[i] if f[i] < 0.0 else f[i] 

    t = np.arange(N)
    c = np.sum(np.cos(2*np.pi*nu*t) * x)
    s = np.sum(np.sin(2*np.pi*nu*t) * x)
    if kwargs.get("verbose", 0) > 0:
        print("Tune:", nu, "s=", s/N*2, " c=", c/N*2, "t=", s/c)
    ph = np.arctan2(-s, c)
    return ph

def calcPhase(xtbt, **kwargs):
    """
    calculate the phase using correlations with sin and cos signal.

    accumulate - return accumulated phase or raw phase data, True
    ref - reference phase to determine initial phase. default None.

    Without ref, there is an undetermined constant in phase. However the phase
    advances is determined.
    """
    acc = kwargs.get("accumulate", True)
    nbpm, N = np.shape(xtbt)
    phs = np.zeros(nbpm + 1, 'd')
    for i in range(nbpm):
        ph = _calcPhase(xtbt[i % nbpm], **kwargs)
        if acc:
            while ph < phs[i]: ph = ph + np.pi
        phs[i+1] = ph
    ref = kwargs.get("ref", None)
    if ref is None: return phs[1:]
    ph0 = np.average(ref) - np.average(phs[1:])
    return phs[1:] + ph0

def _cor(x1, x2):
    xc1 = ( x1 - np.average(x1)) / np.sqrt(2.0 * np.var(x1))
    xc2 = ( x2 - np.average(x2)) / np.sqrt(2.0 * np.var(x2))
    return np.dot(xc1, xc2) / (len(xc1) / 2.0)

def calcPhaseAdvance(xtbt, **kwargs):
    """
    calculate the phase advance from turn-by-turn data
    
    xtbt - turn by turn data (nbpm, nturns)

    Note: This is not the Castro method where tune is needed, from DFT or elsewhere.
    """
    nbpm, N = np.shape(xtbt)
    phi = np.zeros(nbpm, 'd')
    for i in range(nbpm-1):
        phi[i] = np.arccos(_cor(xtbt[i,:], xtbt[i+1,:]))

    phi[-1] = np.arccos(_cor(xtbt[-1,:-1], xtbt[0,1:]))
    return phi


def _filter_lat_rec(r, exclude, exclude_pvs):
    if r[-1] in exclude_pvs: return True
    for expat in exclude:
        v = [re.match(pat, r[i]) for i,pat in enumerate(expat)]
        if all(v): return True


def calcBetaAu(xtbt, **kwargs):
    """
    calculate the beta function in arbitrary unit (Au).

    xtbt - (nbpm, nturns) 2D data
    ref - optional, The reference beta function, default None.

    If ref is given, the arbitrary scaling factor (sqrt(emit)) is determined.
    """
    nbpm, N = np.shape(xtbt)
    A = np.var(xtbt, axis=1)
    bref = kwargs.get("ref", None)
    if bref is None: return A
    assert len(bref) == nbpm, "len(ref) must be equal to len(xtbt)"
    k = np.dot(A, bref) / np.dot(A, A)
    return k*A
