#!/usr/bin/env python

"""
CA Tools
~~~~~~~~

Channel access tools.

:author: Lingyun Yang

When *CA_OFFLINE* is *True*, only simulation values are used. In this case the
caget will have noises and caput will do nothing.
"""

__all__ = [
    'caget', 'caput', 'caputwait', 'caRmCorrect', 
    'Timedout', 'CA_OFFLINE', 'FORMAT_TIME'
]

import sys, time, os
import cothread
import cothread.catools as ct
from cothread import Timedout
from cothread.catools import camonitor, FORMAT_TIME
import random

import numpy as np

import logging
logger = logging.getLogger(__name__)

CA_OFFLINE = False

def _ca_get_sim(pvs):
    """
    get random simulation double single value or list. No STRING considered.
    """
    if isinstance(pvs, (str, unicode)):
        return random.random()
    elif isinstance(pvs, (tuple, list)):
        return [random.random() for i in range(len(pvs))]
    else:
        return None

def _ca_put_sim(pvs, vals):
    """
    do nothing
    """
    return ct.ca_nothing

def caget(pvs, timeout=5, datatype=None, format=ct.FORMAT_RAW,
           count=0, throw=False):
    """channel access read
    
    This is a simple wrap of cothread.catools, support UTF8 string

    Throw cothread.Timedout exception when timeout. This is a wrap of original
    `cothread.catools.caget`.

    seealso :func:`~aphla.catools.caput`

    Parameters
    -----------
    pvs : str, list. process variables
    timeout : int. timeout in seconds
    throw : bool. throw exception or not
    
    Returns
    ---------
    val : list or value. channel value

    Examples
    ----------
    >>> caget('SR:C01-MG:G04B{Quad:M1}Fld-I')
    >>> caget(['SR:PV1', 'SR:PV2', 'SR:PV3'])

    """
    #print "AA"
    #logger.info("caget %s" % str(pvs))
    #logging.getLogger("aphla").info("testing")

    # in case of testing ...
    if CA_OFFLINE: return _ca_get_sim(pvs)

    if isinstance(pvs, str):
        pvs2 = pvs
    elif isinstance(pvs, unicode):
        pvs2 = pvs.encode("ascii")
    elif isinstance(pvs, (tuple, list)):
        pvs2 = [pv.encode("ascii") for pv in pvs]
    else:
        raise ValueError("Unknown type " + str(type(pvs)))

    try:
        return ct.caget(pvs2, timeout=timeout, datatype=datatype,
                        format=format, count=count, throw=throw)
    except:
        if os.environ.get('APHLAS_DISABLE_CA', 0):
            print "TIMEOUT: reading", pvs
            if isinstance(pvs, (unicode, str)): return 0.0
            else: return [0.0] * len(pvs2)
        else:
            raise

def caput(pvs, values, timeout=5, wait=True, throw=True):
    """channel access write.

    This is simple wrap of `cothread.catools.caput` to support UTF8 string

    see original :func:`cothread.catools.caput` for details

    Parameters
    -----------
    pvs : str, list. process variables
    values : float/int, list. setting values
    timeout : int.
    wait : bool.
    throw : bool.

    Returns
    ---------
    see :func:`cothread.catools.caput`

    Examples
    ----------
    >>> caput('SR:C01-MG:G04B{Quad:M1}Fld-I', 0.1)
    >>> caput(['SR:PV1', 'SR:PV2'], [0.1, 0.2])

    """

    logger.info("setting '%s' '%s'" % (str(pvs), str(values)))

    if CA_OFFLINE: return _ca_put_sim(pvs, values)

    if isinstance(pvs, str):
        pvs2 = pvs
    elif isinstance(pvs, unicode):
        pvs2 = pvs.encode("ascii")
    elif isinstance(pvs, list):
        pvs2 = [pv.encode("ascii") for pv in pvs]
    else:
        raise ValueError("Unknown type " + str(type(pvs)))

    try:
        return ct.caput(pvs2, values, timeout=timeout, wait=wait, throw=throw)
    except cothread.Timedout:
        if os.environ.get('APHLAS_DISABLE_CA', 0):
            print "TIMEOUT: reading", pvs
        else:
            raise cothread.Timedout

def caputwait(pvs, values, pvmonitors, diffstd=1e-6, wait=(2, 1), maxtrial=20):
    """set pvs and waiting until the setting takes effect

    Parameters
    ------------
    pvs : str, list. PVs for setting
    values : list. setting values for *pvs*
    pvmonitors : list. PVs for testing the effects of new PV setting.
    diffstd : float. optional(1e-6). threshold value of effective change 
        of *pvmonitors*.
    wait : tuple, optional(2,1). waiting time for initial and each step,
        in seconds
    maxtrial : maximum trial before return.

    Returns
    ----------
    b : True if pvmonitors change significant enough, False otherwise.

    Notes
    -------
    It sets the pvs with new values and tests the monitor values see if the
    changes are significant enough. This significance is measured by comparing
    the std of monitor value changes due to the *pvs* changes. If it exceeds
    *diffstd* then return, otherwise wait for *wait* seconds and test
    again. The maximum trial is *maxtrial*.

    It is good for ORM measurement where setting a trim and observing a list
    of BPM.
    """

    time.sleep(wait[0])

    if CA_OFFLINE:
        return True

    v0 = np.array(caget(pvmonitors))
    ntrial = 0
    while True:
        caput(pvs, values)
        time.sleep(wait[1])
        ntrial = ntrial + 1
        v1 = np.array(caget(pvmonitors))
        if np.std(v1 - v0) > diffstd:
            return True
        elif ntrial > maxtrial:
            return False


def caRmCorrect(resp, kker, m, **kwarg):
    """correct the resp using kker and response matrix.

    Parameters
    ------------
    resp : PV list of the response target, e.g. orbit, tune
    kker : PV list of the controllers, e.g. corrector
    m : response matrix where :math:`m_{ij}=\Delta resp_i/\Delta kker_j`
    scale : scaling factor applied to the calculated kker
    ref : the targeting value of resp PVs
    rcond : the rcond for cutting singular values. 
    check : stop if the orbit gets worse.
    wait : waiting (seconds) before check.

    Returns
    --------
    b : converged (True) or not (False). None if it did not check.

    """
    scale = kwarg.get('scale', 0.68)
    ref   = kwarg.get('ref', None)
    check = kwarg.get('check', True)
    wait  = kwarg.get('wait', 6)
    rcond = kwarg.get('rcond', 1e-4)
    verb  = kwarg.get('verbose', 0)

    v0 = np.array(caget(resp), 'd')
    if ref is not None: v0 = v0 - ref
    
    # the initial norm
    norm0 = np.linalg.norm(v0)

    # solve for m*dk + (v0 - ref) = 0
    dk, resids, rank, s = np.linalg.lstsq(m, -1.0*v0, rcond = rcond)

    norm1 = np.linalg.norm(m.dot(dk*scale) + v0)
    k0 = np.array(caget(kker), 'd')
    caput(kker, k0+dk*scale)

    # wait and check
    if check == True:
        time.sleep(wait)
        v1 = np.array(caget(resp), 'd')

        if ref is not None: v1 = v1 - np.array(ref)
        norm2 = np.linalg.norm(v1)
        if verb > 0:
            print("Euclidian norm: pred./realized", norm1/norm0, norm2/norm0)
        if norm2 > norm0:
            print("Failed to reduce orbit distortion, restoring...", 
                  norm0, norm2)
            caput(kker, k0)
            return False
        else:
            return True
    else:
        return None

