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
#from cothread.catools import caget, caput, camonitor
from . import _lat, _cfa, eget, TAG_DEFAULT_PUT, TAG_DEFAULT_GET
from catools import caget, caput

class Orbit:
    def __init__(self, cfa = None):
        if cfa == None:
            self.bpm = []
            self.bpm_mask = []
            self.pvrb = []
            self.offset = []
            self.WAVEFORM = False
            self.bpm_wave_idx = []
            self.wavepv = None
            self.spv = None
            self.s = []
        else:
            self.initializeBpmPv(cfa)
        

    def initializeBpmPv(self, cfa):
        elemx = _lat.getGroupMembers(['*', 'BPMX'], op = 'intersection')
        elemy = _lat.getGroupMembers(['*', 'BPMY'], op = 'intersection')
        self.bpm = zip(elemx, elemy)
        self.bpm_mask = [(0, 0)] * len(elemx)

        sx = [_cfa.getElementProperties(e, [_cfa.SPOSITION])[_cfa.SPOSITION] \
                  for e in elemx]
        sy = [_cfa.getElementProperties(e, [_cfa.SPOSITION])[_cfa.SPOSITION] \
                  for e in elemy]
        self.s = zip(sx, sy)
        #print self.s
        pvx = _cfa.getElementChannels(elemx, tags=[TAG_DEFAULT_GET, 'X'])
        pvy = _cfa.getElementChannels(elemx, tags=[TAG_DEFAULT_GET, 'Y'])

        if not pvx or not pvy:
            self.pvrb = []
        else:
            self.pvrb = zip([p[0] for p in pvx], [p[0] for p in pvy])

        pvx = _cfa.getElementChannels(elemx, tags=['OFFSET', 'X'])
        pvy = _cfa.getElementChannels(elemx, tags=['OFFSET', 'Y'])
        self.offset = zip([p[0] for p in pvx], [p[0] for p in pvy])
        
        self.WAVEFORM = True
        self.wavepv = ("SR:C00-Glb:G00{ORBIT:00}RB-X", 
                       "SR:C00-Glb:G00{ORBIT:00}RB-Y")
        self.spv = "SR:C00-Glb:G00{POS:00}RB-S"
        
        ix, iy = [], []
        for e in elemx: 
            ix.append(_cfa.getElementProperties(e, [_cfa.ELEMIDX])[_cfa.ELEMIDX])
        for e in elemy: 
            iy.append(_cfa.getElementProperties(e, [_cfa.ELEMIDX])[_cfa.ELEMIDX])
        self.bpm_wave_idx = zip(ix, iy)

    def __iterate_pvrb(self):
        ret = np.zeros((len(self.pvrb), 2), 'd')
        for i in range(len(self.pvrb)):
            ret[i,0] = caget(self.pvrb[i][0])
            ret[i,1] = caget(self.pvrb[i][1])
        return ret

    def get_wave(self):
        return caget(self.spv), caget(self.wavepv)

    def get(self):
        """get the orbit in (n,2) matrix for n BPMs."""
        if self.WAVEFORM:
            s, val = self.get_wave()
            ret = np.zeros((len(self.bpm_wave_idx), 2), 'd')
            for i in range(len(self.bpm_wave_idx)):
                ret[i, 0] = val[0][self.bpm_wave_idx[i][0]]
                ret[i, 1] = val[1][self.bpm_wave_idx[i][1]]
            return ret
        else:
            return __iterate_pvrb()
    
