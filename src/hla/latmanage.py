#!/usr/bin/env python

"""
    hla.latmanage
    ~~~~~~~~~~~~~~~~

    Lattice management

    :author: Lingyun Yang
    :license: (empty ? GPL ? EPICS ?)


    Lattice information are stored in IRMIS, and have a service for
    retrieve it. A local XML could be provided as a buffer.

    This module provides routines operating on IRMIS/E4Service or local
    XML file.
"""

from . import _lat, _cfa

#
#

#__all__ = ['getElements', 'getLocations']

def getElements(group):
    return _lat.getElements(group, '')

def getLocations(group, s='end'):
    """
    Get the location of a group, either returned as a dictionary in which
    the key is element physics name, value is the location.
    """

    elem, loc = _lat.getElements(group, 'end')
    return loc

def addGroup(group):
    """Add a new group"""
    #print conf.ca
    _lat.addGroup(group)

def removeGroup(group):
    """Remove a group if it is empty"""
    _lat.removeGroup(group)

def addGroupMember(group, member):
    """Add a new member to group"""
    _lat.addGroupMember(group, member)
  
def removeGroupMember(group, member):
    """Remove a member from group"""
    _lat.removeGroupMember(group, member)

def getGroups(element = '*'):
    """Get all groups own this element, '' returns all"""
    return _lat.getGroups(element)

def getGroupMembers(groups, op = 'intersection'):
    """Get all elements in a group. If group is a list, consider which op:

    - op = "union", consider elements in the union of the groups
    - op = "intersection", consider elements in the intersect of the groups
    """
    return _lat.getGroupMembers(groups, op)

def getNeighbors(group, n):
    """Get a list of n elements belongs to group. The list is sorted along
    s (the beam direction).
    """
    raise NotImplementedError()
    return None

def getStepSize(element):
    """Return default stepsize of a given element"""
    raise NotImplementedError()
    return None

#
#
#
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

def getCurrentMode(self):
    """Get the current operation mode"""
    raise NotImplementedError()
    return current_mode

def getModes(self):
    raise NotImplementedError()
    return None

def saveMode(self, mode, dest):
    """Save current states to a new mode"""
    raise NotImplementedError()


