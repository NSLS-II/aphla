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
    'caget', 'caput', 'caputwait', 'caRmCorrect', 
    'Timedout', 'CA_OFFLINE', 'FORMAT_TIME'
]

import sys, time, os
import cothread
import cothread.catools as ct
from cothread import Timedout
from cothread.catools import camonitor, FORMAT_TIME, FORMAT_CTRL
import random

import numpy as np

import logging
_logger = logging.getLogger(__name__)

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

def caget(pvs, timeout=1, datatype=None, format=ct.FORMAT_RAW,
           count=0, throw=False):
    """channel access read
    
    This is a simple wrap of cothread.catools, support UTF8 string

    Throw cothread.Timedout exception when timeout. This is a wrap of original
    `cothread.catools.caget`.

    seealso :func:`~aphla.catools.caput`

    Parameters
    -----------
    pvs : str, list. process variables
    timeout : int. timeout in seconds
    throw : bool. throw exception or not
    count : specify number of waveform points
    
    Returns
    ---------
    val : list or value. channel value

    Examples
    ----------
    >>> caget('SR:C01-MG:G04B{Quad:M1}Fld-I')
    >>> caget(['SR:PV1', 'SR:PV2', 'SR:PV3'])

    """
    #print "AA"
    #logger.info("caget %s" % str(pvs))
    #logging.getLogger("aphla").info("testing")

    # in case of testing ...
    if CA_OFFLINE: return _ca_get_sim(pvs)

    if isinstance(pvs, str):
        return ct.caget(pvs, timeout=timeout, datatype=datatype,
                        format=format, count=count, throw=throw)
    elif isinstance(pvs, unicode):
        pvs2 = pvs.encode("ascii")
        return ct.caget(pvs2, timeout=timeout, datatype=datatype,
                        format=format, count=count, throw=throw)
    elif isinstance(pvs, (tuple, list)):
        pvs2 = [pv.encode("ascii") for pv in pvs if pv]
        dr = ct.caget(pvs2, timeout=timeout, datatype=datatype,
                      format=format, count=count, throw=throw)
        if len(pvs2) == len(pvs): return [v for v in dr]

        j, rt = 0, []
        for i,pv in enumerate(pvs):
            if not pv: 
                rt.append(None)
                continue
            rt.append(dr[j])
            j += 1
        return rt
    else:
        raise ValueError("Unknown type " + str(type(pvs)))

def cagetr(pvs, **kwargs):
    """caget recursive version"""
    if not pvs: return None
    if isinstance(pvs, (str, unicode)): return caget(pvs, **kwargs)
    if all([isinstance(pv, (str, unicode)) or pv is None for pv in pvs]):
        return caget(pvs, **kwargs)
    return [cagetr(pv, **kwargs) for pv in pvs]


def caput(pvs, values, timeout=2, wait=True, throw=True):
    """channel access write.

    This is simple wrap of `cothread.catools.caput` to support UTF8 string

    see original :func:`cothread.catools.caput` for details

    Parameters
    -----------
    pvs : str, list. process variables
    values : float/int, list. setting values
    timeout : int.
    wait : bool.
    throw : bool.

    Returns
    ---------
    see :func:`cothread.catools.caput`

    Examples
    ----------
    >>> caput('SR:C01-MG:G04B{Quad:M1}Fld-I', 0.1)
    >>> caput(['SR:PV1', 'SR:PV2'], [0.1, 0.2])

    """

    _logger.debug("setting '%s' '%s'" % (str(pvs), str(values)))

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

def caputwait(pvs, values, pvmonitors, diffstd=1e-6, wait=(2, 1), maxtrial=20):
    """set pvs and waiting until the setting takes effect

    Parameters
    ------------
    pvs : str, list. PVs for setting
    values : list. setting values for *pvs*
    pvmonitors : list. PVs for testing the effects of new PV setting.
    diffstd : float. optional(1e-6). threshold value of effective change 
        of *pvmonitors*.
    wait : tuple, optional(2,1). waiting time for initial and each step,
        in seconds
    maxtrial : maximum trial before return.

    Returns
    ----------
    b : True if pvmonitors change significant enough, False otherwise.

    Notes
    -------
    It sets the pvs with new values and tests the monitor values see if the
    changes are significant enough. This significance is measured by comparing
    the std of monitor value changes due to the *pvs* changes. If it exceeds
    *diffstd* then return, otherwise wait for *wait* seconds and test
    again. The maximum trial is *maxtrial*.

    It is good for ORM measurement where setting a trim and observing a list
    of BPM.
    """

    time.sleep(wait[0])

    if CA_OFFLINE:
        return True

    v0 = np.array(caget(pvmonitors))
    ntrial = 0
    while True:
        caput(pvs, values)
        time.sleep(wait[1])
        ntrial = ntrial + 1
        v1 = np.array(caget(pvmonitors))
        if np.std(v1 - v0) > diffstd:
            return True
        elif ntrial > maxtrial:
            return False


def caRmCorrect(resp, kker, m, **kwarg):
    """correct the resp using kker and response matrix.

    Parameters
    ------------
    resp : PV list of the response target, e.g. orbit, tune
    kker : PV list of the controllers, e.g. corrector
    m : response matrix where :math:`m_{ij}=\Delta resp_i/\Delta kker_j`
    scale : scaling factor applied to the calculated kker
    ref : the targeting value of resp PVs
    rcond : the rcond for cutting singular values. 
    check : stop if the orbit gets worse.
    wait : waiting (seconds) before check.
    bc: str. bounds checking. 'exception', 'ignore', 'abort', 'boundary', None
    kkerlim: (ncor, 2) array. The limits for controllers

    Returns
    --------
    err : converged or not checked (0), error (>0).
    msg : error message or None

    """
    scale = kwarg.get('scale', 0.68)
    ref   = kwarg.get('ref', None)
    check = kwarg.get('check', True)
    wait  = kwarg.get('wait', 6)
    rcond = kwarg.get('rcond', 1e-3)
    verb  = kwarg.get('verbose', 0)
    lim   = kwarg.get('kkerlim', None)
    bc    = kwarg.get('bc', None)

    _logger.info("nkk={0}, nresp={1}, scale={2}, rcond={3}, wait={4}".format(
            len(kker), len(resp), scale, rcond, wait))

    if lim is None:
        lim = np.zeros((len(kker), 2), 'd')
        for i,pv in enumerate(kker):
            v = caget(pv, timeout=2, format=ct.FORMAT_CTRL)
            lim[i,:] = (v.lower_ctrl_limit, v.upper_ctrl_limit)

    v0 = np.array(caget(resp), 'd')
    if ref is not None: v0 = v0 - ref
    
    # the initial norm
    norm0 = np.linalg.norm(v0)

    # solve for m*dk + (v0 - ref) = 0
    dk, resids, rank, s = np.linalg.lstsq(m, -1.0*v0, rcond = rcond)

    norm1 = np.linalg.norm(m.dot(dk*scale) + v0)
    k0 = np.array(caget(kker), 'd')
    k1 = k0 + dk*scale

    kkerin, k1in = [], []
    # bounds checking
    for i in range(len(kker)):
        # force setting, rely on the lower level rules.
        if bc is None or bc == 'force':
            kkerin.append(kker[i])
            k1in.append(k1[i])
            continue

        if k1[i] < lim[i,0]:
            msg = "{0} value {1} exceeds lower boundary {2}".format(
                    kker[i], k1[i], lim[i,0])
            _logger.warn(msg)
            if bc == 'abort':
                return (1, msg)
            elif bc == 'exception':
                raise ValueError(msg)
            elif bc == 'boundary':
                kkerin.append(kker[i])
                k1in.append(lim[i,0])
            elif bc == 'ignore':
                continue
            # end of lower bc 
        elif k1[i] > lim[i,1]:
            msg = "{0} value {1} exceeds upper boundary {2}".format(
                    kker[i], k1[i], lim[i,1])
            _logger.warn(msg)
            if bc == 'abort':
                return (1, msg)
            elif bc == 'exception':
                raise ValueError(msg)
            elif bc == 'boundary':
                kkerin.append(kker[i])
                k1in.append(lim[i,1])
            elif bc == 'ignore':
                continue
            # end of lower bc 
        else:
            kkerin.append(kker[i])
            k1in.append(k1[i])

    # the real setting
    caput(kkerin, k1in)

    # wait and check
    if check == True:
        time.sleep(wait)
        v1 = np.array(caget(resp), 'd')

        if ref is not None: v1 = v1 - np.array(ref)
        norm2 = np.linalg.norm(v1)
        msg = "Euclidian norm: pred./realized", norm1/norm0, norm2/norm0
        _logger.info(msg)
        if verb > 0:
            print(msg)
        if norm2 > norm0:
            msg = "Failed to reduce orbit distortion, restoring..." 
            _logger.warn(msg) 
            print(msg, norm0, norm2)
            caput(kker, k0)
            return (2, msg)
        else:
            return (0, None)
    else:
        return (0, None)

def save_lat_epics(fname, pvs, **kwargs):

    group  = kwargs.get("group", None)
    mode   = kwargs.get("mode", 'a')
    ignore = kwargs.get("ignore", [])
    timeout = kwargs.get("timeout", 10)
    extrapvs = kwargs.get("extrapvs", [])

    import h5py
    h5f = h5py.File(fname, mode)
    if not group: grp = h5f.create_group(lat.name)
    else: grp = h5f.create_group(group)

    # get the pv list
    datnames = []
    for pv, name, fam, fld, rw in pvs:
        datnames.append((name, fld, rw, pv))
    #print datnames
    allpvs = [v[3] for v in datnames] + extrapvs
    alldat = caget(allpvs, format=FORMAT_TIME, timeout=timeout)
    scalars, dead = [], []
    sz_name, sz_fld, sz_pv = 0, 0, 0
    for i,dat in enumerate(alldat):
        name, fld, rb, pv = datnames[i][:4]
        if len(name) > sz_name: sz_name = len(name)
        if len(fld) > sz_fld: sz_fld = len(fld)
        if len(pv) > sz_pv: sz_pv = len(pv)
        if not dat.ok:
            dead.append((name,fld,rb,pv,np.nan, 0.0, ""))
        elif isinstance(dat, cothread.dbr.ca_array):
            dsname = "wf_{0}.{1}_{2}".format(name,fld,rb)
            grp[dsname] = dat
            grp[dsname].attrs["element"] = name
            grp[dsname].attrs["field"] = fld
            grp[dsname].attrs["pv"] = pv
            grp[dsname].attrs["rw"] = rb
            grp[dsname].attrs["datetime"] = str(dat.datetime)
            grp[dsname].attrs["timestamp"] = dat.timestamp
        else:
            scalars.append((name,fld,rb,pv,dat, dat.timestamp,
                            str(dat.datetime)))

    if not scalars: return

    dt = np.dtype([("element", 'S%d' % sz_name),
                   ('field', 'S%d' % sz_fld),
                   ('rw', 'i'), 
                   ('pv', 'S%d' % sz_pv),
                   ('value', 'd'),
                   ('timestamp', 'd'),
                   ('datetime', 'S32')])
    grp["__scalars__"] = np.array(scalars, dtype=dt)
    grp["__dead__"] = np.array(dead, dtype=dt)
    h5f.close()


