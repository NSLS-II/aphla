#!/usr/bin/env python

"""
    hla.current
    ~~~~~~~~~~~~~~~~

    Beam current related routines

    :author: Lingyun Yang
    :license: (empty ? GPL ? EPICS ?)

"""

from cothread.catools import caget, caput
import numpy as np
import datetime, time

def getCurrent():
    """Get the current"""
    return caget("SR:C00-BI:G00<DCCT:00>CUR-RB")

def getLifetime():
    """Monitor current change, calculate lifetime"""

    N = 10
    ret = np.zeros((N, 2), 'd')
    d0 = datetime.datetime.now()
    ret[0, 1] = getCurrent()
    for i in range(1, N):
        time.sleep(3)
        ret[i,1] = getCurrent()
        dt = datetime.datetime.now() - d0
        ret[i,0] = (dt.microseconds/1000000.0 + dt.seconds)/3600.0 + dt.days*24.0
    dI = max(ret[:,1]) - min(ret[:,1]) 
    dt = max(ret[:,0]) - min(ret[:,0])
    print np.average(ret[:,1]), dI, dt
    print np.average(ret[:,1]) / (dI / dt), "H"
    return ret

def saveMode(self, mode, dest):
    """Save current states to a new mode"""
    current_mode


