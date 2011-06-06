#!/usr/bin/env python

"""
    hla.current
    ~~~~~~~~~~~~~~~~

    Beam current related routines

    :author: Lingyun Yang
    :license: (empty ? GPL ? EPICS ?)

"""

#from cothread.catools import caget, caput
import numpy as np
import datetime, time
from catools import caget, caput

def getCurrent():
    """Get the current from channel"""
    
    return caget("SR:C00-BI:G00{DCCT:00}CUR-RB")

def getLifetime(verbose = 0):
    """
    Monitor current change with, calculate lifetime dI/dt

    It takes about 30 seconds, 10 points will be recorded, about 3 seconds
    delay between each.

    least square linear fitting is applied for slop dI/dt
    """

    N = 10
    ret = np.zeros((N, 2), 'd')
    d0 = datetime.datetime.now()
    ret[0, 1] = getCurrent()
    for i in range(1, N):
        time.sleep(3)
        ret[i,1] = getCurrent()
        dt = datetime.datetime.now() - d0
        ret[i,0] = (dt.microseconds/1000000.0 + dt.seconds)/3600.0 + \
            dt.days*24.0
        if verbose:
            print i, dt, ret[i,1]
    dI = max(ret[:,1]) - min(ret[:,1]) 
    dt = max(ret[:,0]) - min(ret[:,0])
    #print np.average(ret[:,1]), dI, dt
    #print np.average(ret[:,1]) / (dI / dt), "H"
    lft_hour = np.average(ret[:,1]) / (dI / dt)
    return lft_hour


