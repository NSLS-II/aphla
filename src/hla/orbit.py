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
from . import _lat, eget

def getFullOrbit(group = '*', sequence = None):
    """Return orbit"""
    x = caget("SR:C00-Glb:G00{ORBIT:00}RB-X")
    y = caget("SR:C00-Glb:G00{ORBIT:00}RB-Y")
    s = caget("SR:C00-Glb:G00{POS:00}RB-S")
    ret = []
    for i in range(len(s)):
        ret.append([s[i], x[i], y[i]])
    return ret

def getOrbit(group = '*'):
    """Return orbit"""
    if isinstance(group, str):
        #print __file__, "group = ", group
        elemx = _lat.getGroupMembers([group, 'BPMX'], op = 'intersection')
        elemy = _lat.getGroupMembers([group, 'BPMY'], op = 'intersection')
    elif isinstance(group, list):
        elemx = group[:]
        elemy = group[:]

    orbx, pvx = eget(elemx, full=True, tags=['H'], unique=True)
    orby, pvy = eget(elemy, full=True, tags=['V'], unique=True)
    #print __file__, len(elemx), len(elemy), len(orbx), len(orby)
    #print __file__, orbx[0], elemx[0], pvx[0], caget(pvx[0][0])
    #print __file__, orbx, orby
    return orbx, orby


def getOrbitRm():
    raise NotImplementedError()
    return None

def perturbOrbit(hcm = 'SR:C30-MG:G04B<HCM:M1>Fld-SP',
                 vcm = 'SR:C30-MG:G02A<VCM:H>Fld-SP'):
    caput(hcm, .0002)
    caput(vcm, .0001)

