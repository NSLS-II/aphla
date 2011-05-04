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

def caputwait(pv, value, pvmonitor, change=("REL", 0.1), wait=3, \
                  maxtrial=10):
    """
    set a pv(or list of pvs), monitoring certain PV until certain change

    change could be relative "REL" or absolute "ABS". It tries no more than
    `maxtrial` times. Each trial wait certain seconds.

    Example::

      caputwait("PV1", "PVMON", ("ABS", .1), maxtrial=20)
      
    """
    v0 = caget(pvmonitor)
    ntrial = 0
    while True:
        caput(pv, value)
        time.sleep(wait)
        ntrial = ntrial + 1
        v1 = caget(pvmonitor)
        if change[0] == "REL" and abs((v1-v0)/v0) > change[1]:
            break
        elif change[0] == "ABS" and abs(v1-v0) > change[1]:
            break
        if ntrial > maxtrial: break


#caget.__doc__ = caget.__doc__ + ct.caget.__doc__
#caput.__doc__ = caput.__doc__ + ct.caput.__doc__
