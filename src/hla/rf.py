#!/usr/bin/env python

"""
RF Control
~~~~~~~~~~

RF related

:author: Lingyun Yang
:license: (empty ? GPL ? EPICS ?)

.. warning::

  Hard coded, simple but not fixed yet.

"""

from catools import caget, caput

def getRfFrequency():
    """Get the RF frequency"""
    return caget("SR:C00-RF:G00{RF:00}Freq-RB")

def putRfFrequency(f):
    """set the rf frequency"""
    caput("SR:C00-RF:G00{RF:00}Freq-SP", f)

def getRfVoltage():
    """Return RF voltage"""
    return caget("SR:C00-RF:G00{RF:00}Volt-RB")


def _reset_rf():
    caput('SR:C00-RF:G00{RF:00}Freq-SP', 499.680528631)


