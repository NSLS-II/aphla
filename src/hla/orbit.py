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

from cothread.catools import caget, caput, camonitor

bpmhpv = {}
bpmvpv = {}

def __init_pv__():
    """Initialize bpm pv dictionary"""
    pass

def getOrbit(group = '*', sequence = None):
    """Return orbit"""
    x = caget("SR:C00-Glb:G00<ORBIT:00>RB-X")
    y = caget("SR:C00-Glb:G00<ORBIT:00>RB-Y")
    s = caget("SR:C00-Glb:G00<POS:00>RB-S")
    ret = []
    for i in range(len(s)):
        ret.append([s[i], x[i], y[i]])
    return ret

def getOrbitRm():
    raise NotImplementedError()
    return None

def perturbOrbit(hcm = 'SR:C30-MG:G04B<HCM:M1>Fld-SP',
                 vcm = 'SR:C30-MG:G02A<VCM:H>Fld-SP'):
    caput(hcm, .0002)
    caput(vcm, .0001)

                 
# initialize pv list
__init_pv__()
