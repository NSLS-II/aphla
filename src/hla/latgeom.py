#!/usr/bin/env python

"""
    hla.latgeom
    ~~~~~~~~~~~~~~~~

    Lattice geometry management

    :author: Lingyun Yang
    :license: (empty ? GPL ? EPICS ?)


    Lattice geometry information are stored in IRMIS, and have a service for
    retrieve it. A local XML could be provided as a buffer.

    This module provides routines operating on IRMIS/E4Service or local
    XML file. 
"""

import conf

def getLocation(group):
    """
    Get the location of a group, either returned as a dictionary in which
    the key is element physics name, value is the location.
    """
    
    return None


