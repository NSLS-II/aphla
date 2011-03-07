#!/usr/bin/env python

"""
    hla.latgroup
    ~~~~~~~~~~~~~~~~

    Lattice group management

    :author: Lingyun Yang
    :license: (empty ? GPL ? EPICS ?)


    Lattice group information are stored in IRMIS, and have a service for
    retrieve it. This module provides routines operating on
    IRMIS/E4Service or local XML file.
"""

from . import conf


def addGroup(group):
    """Add a new group"""
    #print conf.ca

    raise NotImplementedError()
    return None

def removeGroup(group):
    """Remove a group if it is empty"""
    raise NotImplementedError()
    return None

def addGroupMember(group, member):
    """Add a new member to group"""
    raise NotImplementedError()
    return None
  
def removeGroupMember(group, member):
    """Remove a member from group"""
    raise NotImplementedError()
    return None

def getGroups(element = ''):
    """Get all groups own this element, '' returns all"""
    raise NotImplementedError()
    return None

def getGroupMembers(group, op = None):
    """Get all elements in a group. If group is a list, consider which op:

    - op = "union", consider elements in the union of the groups
    - op = "intersect", consider elements in the intersect of the groups
    """
    raise NotImplementedError()
    
    return None

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

def getElements(group):
    return conf.ca.getElements(group)

