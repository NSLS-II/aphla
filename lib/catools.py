#!/usr/bin/env python

"""
CA Tools
~~~~~~~~

Channel access tools.

:author: Lingyun Yang

When *CA_OFFLINE* is *True*, only simulation values are used. In this case the
caget will have noises and caput will do nothing.
"""

__all__ = [
    'caget', 'caput', 'caputwait', 'Timedout', 'CA_OFFLINE', 'FORMAT_TIME'
]

import sys, time, os
import cothread
import cothread.catools as ct
from cothread import Timedout
from cothread.catools import camonitor, FORMAT_TIME
import random

import numpy as np

import logging
logger = logging.getLogger(__name__)

CA_OFFLINE = False

def _ca_get_sim(pvs):
    """
    get random simulation double single value or list. No STRING considered.
    """
    if isinstance(pvs, (str, unicode)):
        return random.random()
    elif isinstance(pvs, (tuple, list)):
        return [random.random() for i in range(len(pvs))]
    else:
        return None

def _ca_put_sim(pvs, vals):
    """
    do nothing
    """
    return ct.ca_nothing

def caget(pvs, timeout=5, datatype=None, format=ct.FORMAT_RAW,
           count=0, throw=True):
    """
    channel access read
    
    :param pvs: process variables
    :type pvs: list, string
    :param timeout: timeout in seconds
    :param throw: throw exception or not
    :return: channel value
    :rtype: list or value
    
    This is a simple wrap of cothread.catools, support UTF8 string

    :Example:

        >>> caget('SR:C01-MG:G04B{Quad:M1}Fld-I')
        >>> caget(['SR:PV1', 'SR:PV2', 'SR:PV3'])

    Throw cothread.Timedout exception when timeout. This is a wrap of original
    `cothread.catools.caget`.

    seealso :func:`~aphla.catools.caput`
    """
    # in case of testing ...
    if CA_OFFLINE: return _ca_get_sim(pvs)

    if isinstance(pvs, str):
        pvs2 = pvs
    elif isinstance(pvs, unicode):
        pvs2 = pvs.encode("ascii")
    elif isinstance(pvs, (tuple, list)):
        pvs2 = [pv.encode("ascii") for pv in pvs]
    else:
        raise ValueError("Unknown type " + str(type(pvs)))

    try:
        return ct.caget(pvs2, timeout=timeout, datatype=datatype,
                        format=format, count=count, throw=throw)
    except:
        if os.environ.get('APHLAS_DISABLE_CA', 0):
            print "TIMEOUT: reading", pvs
            if isinstance(pvs, (unicode, str)): return 0.0
            else: return [0.0] * len(pvs2)
        else:
            raise

def caput(pvs, values, timeout=5, wait=True, throw=True):
    """
    channel access write.

    :param pvs: process variables
    :type pvs: list, string
    :param values: setting values
    :type pvs: list, float/int
    :return: see :func:`cothread.catools.caput`
    :rtype: see :func:`cothread.catools.caput`

    :Example:

        caput('SR:C01-MG:G04B{Quad:M1}Fld-I', 0.1)
        caput(['SR:PV1', 'SR:PV2'], [0.1, 0.2])

    This is simple wrap of `cothread.catools.caput` to support UTF8 string

    Throw cothread.Timedout exception when timeout.
    
    see original :func:`cothread.catools.caput` for details

    seealso :func:`~aphla.catools.caget`
    """

    logger.info("setting '%s' '%s'" % (str(pvs), str(values)))

    if CA_OFFLINE: return _ca_put_sim(pvs, values)

    if isinstance(pvs, str):
        pvs2 = pvs
    elif isinstance(pvs, unicode):
        pvs2 = pvs.encode("ascii")
    elif isinstance(pvs, list):
        pvs2 = [pv.encode("ascii") for pv in pvs]
    else:
        raise ValueError("Unknown type " + str(type(pvs)))

    try:
        return ct.caput(pvs2, values, timeout=timeout, wait=wait, throw=throw)
    except cothread.Timedout:
        if os.environ.get('APHLAS_DISABLE_CA', 0):
            print "TIMEOUT: reading", pvs
        else:
            raise cothread.Timedout

def caputwait(pvs, values, pvmonitors, diffstd=1e-6, wait=2,  maxtrial=20):
    """
    set pvs and waiting until the setting takes effect

    :param pvs: PVs for setting
    :type pvs: list, string
    :param values: setting values for *pvs*
    :type values: list, string
    :param pvmonitors: PVs for testing the effects of new PV setting.
    :type pvmonitors: list
    :param diffstd: threshold value of effective change of *pvmonitors*.
    :param wait: waiting time before each test (seconds)
    :param maxtrial: maximum trial before return.
    :return: whether pvmonitors change significant enough.
    :rtype: bool

    It sets the pvs with new values and tests the monitor values see if the
    changes are significant enough. This significance is measured by comparing
    the std of monitor value changes due to the *pvs* changes. If it exceeds
    *diffstd* then return, otherwise wait for *wait* seconds and test
    again. The maximum trial is *maxtrial*.

    It is good for ORM measurement where setting a trim and observing a list
    of BPM.
    """
    if CA_OFFLINE:
        time.sleep(wait)
        return True

    v0 = np.array(caget(pvmonitors))
    ntrial = 0
    while True:
        caput(pvs, values)
        time.sleep(wait)
        ntrial = ntrial + 1
        v1 = np.array(caget(pvmonitors))
        if np.std(v1 - v0) > diffstd:
            return True
        elif ntrial > maxtrial:
            return False

