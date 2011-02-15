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


def addGroup(group):
    """Add a new group"""
    return None

def removeGroup(group):
    """Remove a group if it is empty"""
    return None

def addGroupMember(group, member):
    """Add a new member to group"""
    return None
  
def removeGroupMember(group, member):
    """Remove a member from group"""
    return None

def getGroups(element = ''):
    """Get all groups own this element, '' returns all"""
    return None

def getGroupMembers(group):
    return None

