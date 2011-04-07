#!/usr/bin/env python

"""
    hla.rf
    ~~~~~~

    RF related

    :author: Lingyun Yang
    :license: (empty ? GPL ? EPICS ?)

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



