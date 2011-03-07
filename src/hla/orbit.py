#!/usr/bin/env python

"""
    hla.orbit
    ~~~~~~~~~~~~~~~~

    Lattice mode management

    :author: Lingyun Yang
    :license: (empty ? GPL ? EPICS ?)


    Lattice mode information are stored in IRMIS, and have a service for
    retrieve it. This module provides routines operating on
    IRMIS/E4Service or local XML file.
"""

import numpy as np
from cothread.catools import caget, caput, camonitor

bpmhpv = []
bpmvpv = []
bpms = []

def getFullOrbit(group = '*', sequence = None):
    """Return orbit"""
    x = caget("SR:C00-Glb:G00<ORBIT:00>RB-X")
    y = caget("SR:C00-Glb:G00<ORBIT:00>RB-Y")
    s = caget("SR:C00-Glb:G00<POS:00>RB-S")
    ret = []
    for i in range(len(s)):
        ret.append([s[i], x[i], y[i]])
    return ret

def getOrbit(group = '*', sequence = None):
    """Return orbit"""
    elem = conf.ca.findGroup("BPM")
    hpv = conf.ca.getChannels(elem, mode="xAvg")
    vpv = conf.ca.getChannels(elem, mode="yAvg")
    s = conf.ca.getPositions(elem)
    ret = []
    print "Reading PV data"
    for i in range(len(s)):
        x = caget(hpv[i])
        y = caget(vpv[i])
        ret.append([s[i], x, y])
    return ret

def getOrbitRm():
    raise NotImplementedError()
    return None

def perturbOrbit(hcm = 'SR:C30-MG:G04B<HCM:M1>Fld-SP',
                 vcm = 'SR:C30-MG:G02A<VCM:H>Fld-SP'):
    caput(hcm, .0002)
    caput(vcm, .0001)

if __name__ == "__main__":
    ret = getOrbit()
    print ret
