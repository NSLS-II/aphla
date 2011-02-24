#!/usr/bin/env python

"""
    hla.latmode
    ~~~~~~~~~~~~~~~~

    Lattice mode management

    :author: Lingyun Yang
    :license: (empty ? GPL ? EPICS ?)


    Lattice mode information are stored in IRMIS, and have a service for
    retrieve it. This module provides routines operating on
    IRMIS/E4Service or local XML file.
"""


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


