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

from . import _cfa


