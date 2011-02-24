#!/usr/bin/env python

"""
    hla.lattwiss
    ~~~~~~~~~~~~~~~~

    Lattice twiss data

    :author: Lingyun Yang
    :license: (empty ? GPL ? EPICS ?)


    Measured lattice twiss information are stored in IRMIS, and have a
    service for retrieve it. This module provides routines operating on
    IRMIS/E4Service or local XML file.
"""

def getPhase(group, plane = 'hv', mode = ''):
    """The commands
    :func:`~hla.latmode.getCurrentMode` is good !
    :class:`~hla.cadict.CAElement` is also good.
    :class:`~hla.cadict.CADict` is also good.
    """
    raise NotImplementedError()
    
    return None

def getBeta(group, plane = 'hv', mode = ''):
    """Return beta functions"""
    raise NotImplementedError()
    return None

def getDispersion(group, plane = 'hv', mode = ''):
    """Return dispersion"""
    raise NotImplementedError()
    return None

def getChromaticity(group, plane = 'hv', mode = ''):
    raise NotImplementedError()
    return None

def getTune(plane = 'hv', mode = ''):
    raise NotImplementedError()
    return None

def getFftTune(plane = 'hv', mode = ''):
    """Return tunes from FFT"""
    raise NotImplementedError()
    return None

def savePhase(mode, phase, info):
    raise NotImplementedError()
    return None

def saveBeta(mode, phase, info):
    raise NotImplementedError()
    return None

def saveDispersion(mode, phase, info):
    raise NotImplementedError()
    return None

def saveTune(mode, phase, info):
    raise NotImplementedError()
    return None

def saveTuneRm(mode, phase, info):
    raise NotImplementedError()
    return None

def saveChromaticity(mode, phase, info):
    raise NotImplementedError()
    return None

def saveChromaticityRm(mode, phase, info):
    raise NotImplementedError()
    return None

def getChromaticityRm(mode, phase, info):
    raise NotImplementedError()
    return None, None

def getTuneRm(mode):
    raise NotImplementedError()

