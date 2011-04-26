#!/usr/bin/env python


import sys, time
import cothread
import cothread.catools as ct
from cothread import Timedout

def caget(pvs, timeout=5, datatype=None, format=ct.FORMAT_RAW,
           count=0, throw=True):

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
        sys.exit(0)

def caput(pvs, values, timeout=5, throw=True):
    if isinstance(pvs, str):
        pvs2 = pvs
    elif isinstance(pvs, unicode):
        pvs2 = pvs.encode("ascii")
    elif isinstance(pvs, list):
        pvs2 = [pv.encode("ascii") for pv in pvs]
    else:
        raise ValueError("Unknown type " + str(type(pvs)))

    try:
        return ct.caput(pvs2, values, timeout=timeout, wait=True, throw=throw)
    except cothread.Timedout:
        print "TIMEOUT: ", pvs
        sys.exit(0)

def caputwait(pv, value, pvmonitor, change=("REL", 0.1), wait=3, \
                  maxtrial=10):
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


caget.__doc__ = ct.caget.__doc__
