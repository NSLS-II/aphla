#!/usr/bin/env python

"""
CA Tools
~~~~~~~~

Channel access tools.

:author: Lingyun Yang
"""

__all__ = [
    'caget', 'caput', 'Timedout', 'CA_OFFLINE', 'FORMAT_TIME'
]

import sys, time, os
import cothread
import cothread.catools as ct
from cothread import Timedout
from cothread.catools import camonitor, FORMAT_TIME
import random

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
    return ct.ca_nothing

def caget(pvs, timeout=5, datatype=None, format=ct.FORMAT_RAW,
           count=0, throw=True):
    """
    channel access read, a simple wrap of cothread.catools, support UTF8 string

    Example::

      caget('SR:C01-MG:G04B{Quad:M1}Fld-I')
      caget(['SR:C01-MG:G04B{HCor:M1}Fld-I', 'SR:C01-MG:G04B{VCor:M1}Fld-I'])

    Throw cothread.Timedout exception when timeout. This is a wrap of original
    `cothread.catools.caget`.

    .. seealso:: 

      :func:`~aphla.catools.caput`
    """
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
    except cothread.Timedout:
        if os.environ.get('APHLAS_DISABLE_CA', 0):
            print "TIMEOUT: reading", pvs
            if isinstance(pvs, (unicode, str)): return 0.0
            else: return [0.0] * len(pvs2)
        else:
            raise cothread.Timedout

def caput(pvs, values, timeout=5, wait=True, throw=True):
    """
    channel access write, wrap to support UTF8 string

    ::

      caput('SR:C01-MG:G04B{Quad:M1}Fld-I', 0.1)
      caput(['SR:C01-MG:G04B{HCor:M1}Fld-I', 'SR:C01-MG:G04B{VCor:M1}Fld-I'], [0.1, 0.2])

    Throw cothread.Timedout exception when timeout.
    
    see original :func:`cothread.catools.caput` for details

    .. seealso::

      :func:`aphla.catools.caget`
    """
    if CA_OFFLINE: return _ca_put_sim(pvs)

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

def caputwait(pv, value, pvmonitors, diffstd=1e-6, wait=2,  maxtrial=20):
    """
    set a pv(or list of pvs), monitoring  PVs until certain degree of changes.

    - *wait* [seconds] minimum wait between each check.
    - *maxtrial* maximum number of checks.
    - *diffstd* return if the std of pvmonitors chenges:  std(after-before),
      exceed this number.

    It is good for ORM measurement where setting a trim and observing a
    list of BPM.
    """
    if CA_OFFLINE:
        time.sleep(wait)
        return True

    v0 = np.array(caget(pvmonitors))
    ntrial = 0
    while True:
        caput(pv, value)
        time.sleep(wait)
        ntrial = ntrial + 1
        v1 = np.array(caget(pvmonitors))
        if np.std(v1 - v0) > diffstd:
            return True
        elif ntrial > maxtrial:
            return False

