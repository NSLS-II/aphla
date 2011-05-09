#!/usr/bin/env python


import sys, time
import cothread
import cothread.catools as ct
from cothread import Timedout

def caget(pvs, timeout=5, datatype=None, format=ct.FORMAT_RAW,
           count=0, throw=True):
    """
    channel access read, a simple wrap of cothread.catools, support UTF8 string

    Example::

      >>> caget('SR:C01-MG:G04B{Quad:M1}Fld-I')
      >>> caget(['SR:C01-MG:G04B{HCor:M1}Fld-I', 'SR:C01-MG:G04B{VCor:M1}Fld-I'])

    Throw cothread.Timedout exception when timeout.
    """
    if isinstance(pvs, str):
        pvs2 = pvs
    elif isinstance(pvs, unicode):
        pvs2 = pvs.encode("ascii")
    elif isinstance(pvs, list):
        pvs2 = [pv.encode("ascii") for pv in pvs]
    elif isinstance(pvs, tuple):
        pvs2 = [pv.encode("ascii") for pv in pvs]
    else:
        raise ValueError("Unknown type " + str(type(pvs)))

    try:
        return ct.caget(pvs2, timeout=timeout, datatype=datatype,
                        format=format, count=count, throw=throw)
    except cothread.Timedout:
        print "TIMEOUT: ", pvs
        raise cothread.Timedout

def caput(pvs, values, timeout=5, wait=True, throw=True):
    """
    channel access write, wrap to support UTF8 string

    Example::

      caput('SR:C01-MG:G04B{Quad:M1}Fld-I', 0.1)
      caput(['SR:C01-MG:G04B{HCor:M1}Fld-I', 'SR:C01-MG:G04B{VCor:M1}Fld-I'], [0.1, 0.2])

    Throw cothread.Timedout exception when timeout.
    """
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
        print "TIMEOUT: ", pvs
        raise cothread.Timedout

def caputwait(pv, value, pvmonitors, diffstd=1e-6, wait=2,  maxtrial=20):
    """
    set a pv(or list of pvs), monitoring certain PV until certain change
    """
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


#caget.__doc__ = caget.__doc__ + ct.caget.__doc__
#caput.__doc__ = caput.__doc__ + ct.caput.__doc__
