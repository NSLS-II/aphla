#!/usr/bin/env python

"""
:author: Lingyun Yang
:license: (empty ? GPL ? EPICS ?)
"""

from . import _lat, _cfa
from cothread.catools import caget, caput

#

#__all__ = ['getElements', 'getLocations']

def getElements(group, cell = [], girder = [], sequence = []):
    return _lat.getElementsCgs(group, cell, girder, sequence)

def getLocations(group, s='end'):
    """Get the location of a group, either returned as a dictionary in
    which the key is element physics name, value is the location.
    """
    if isinstance(group, list):
        return _lat.getLocations(group, s)
    elif isinstance(group, str):
        elem, loc = _lat.getElements(group, 'end')
        return loc
    else:
        raise ValueError("parameter *group* must be a list of string")
def getRbChannels(elemlist):
    """get the pv names for a list of elements"""
    
    return _cfa.getElementChannel(elemlist, {'handle': 'get'}, tags = ['default'], unique=False)

def addGroup(group):
    """
    add a new group, *group* should be plain string, characters in
    \[a-zA-Z0-9\_\]
    """
    return _lat.addGroup(group)

def removeGroup(group):
    """
    Remove a group if it is empty
    """
    _lat.removeGroup(group)

def addGroupMembers(group, member):
    """Add a new member to a existing group"""
    if isinstance(member, str):
        _lat.addGroupMember(group, member)
    elif isinstance(member, list):
        for m in member:
            _lat.addGroupMember(group, m)
    else:
        raise ValueError("member can only be string or list")

def removeGroupMembers(group, member):
    """Remove a member from group"""
    if isinstance(member, str):
        _lat.removeGroupMember(group, member)
    elif isinstance(member, list):
        for m in member: _lat.removeGroupMember(group, m)
    else:
        raise ValueError("member can only be string or list")

def getGroups(element = '*'):
    """
    Get all groups own these elements, '*' returns all possible groups,
    since it matches every element
    """
    return _lat.getGroups(element)

def getGroupMembers(groups, op = 'intersection'):
    """
    Get all elements in a group. If group is a list, consider which op:

    - op = "union", consider elements in the union of the groups
    - op = "intersection", consider elements in the intersect of the groups
    """
    return _lat.getGroupMembers(groups, op)

def getNeighbors(element, group, n = 3):
    """
    Get a list of n elements belongs to group. The list is sorted along s
    (the beam direction).

    .. seealso::
        
        :class:`~hla.lattice.Lattice`
        :meth:`~hla.lattice.Lattice.getNeighbors` For getting list of neighbors. :py:func:`hla.lattice.Lattice.getNeighbors`
    """
    return _lat.getNeighbors(element, group, n)


def getStepSize(element):
    """Return default stepsize of a given element"""
    raise NotImplementedError()
    return None

#
#
#
def getPhase(group, loc = 'end'):
    """
    get the phase from stored data
    """
    elem = getElements(group)

    if isinstance(elem, list):
        return _lat.getPhase(elem)
    elif isinstance(elem, str):
        return _lat.getPhase(elemlst = [elem])
    else:
        return None

#
#
def getBeta(group, loc = 'end'):
    """
    get the beta function from stored data
    """
    elem = getElements(group)

    if isinstance(elem, list):
        return _lat.getBeta(elem)
    elif isinstance(elem, str):
        return _lat.getBeta(elemlst = [elem])
    else:
        return None

def getDispersion(group, loc = 'end'):
    """
    get the dispersion
    """
    return getEta(group, loc)

def getEta(group, loc = 'end'):
    """
    get the dispersion from stored data
    """
    elem = getElements(group)

    if isinstance(elem, list):
        return _lat.getEta(elem)
    elif isinstance(elem, str):
        return _lat.getEta(elemlst = [elem])
    else:
        return None

def getChromaticity(group, plane = 'hv', mode = ''):
    raise NotImplementedError()
    return None

def getTunes(source='machine'):
    if source == 'machine':
        pv = _cfa.getElementChannel(['TUNEX', 'TUNEY'], {'handle': 'get'})
        nux = caget(pv[0])
        nuy = caget(pv[1])
        return nux, nuy
    elif source == 'model':
        pass
    elif source == 'database':
        return _lat.getTunes()

def getTune(plane = 'hv'):
    nux, nuy = getTunes()
    if plane == 'h': return nux
    elif plane == 'v': return nuy
    else:
        raise ValueError("plane must be h/v")

def getFftTune(plane = 'hv', mode = ''):
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
    raise NotImplementedError()
    return current_mode

def getModes(self):
    raise NotImplementedError()
    return None

def saveMode(self, mode, dest):
    """Save current states to a new mode"""
    raise NotImplementedError()


