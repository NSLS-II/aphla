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
    'readPvs', 'measCaRmCol',
    'Timedout', 'CA_OFFLINE', 'FORMAT_TIME'
]

import sys, time, os
import cothread
import cothread.catools as ct
from datetime import datetime
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

def caget(pvs, timeout=6, datatype=None, format=ct.FORMAT_TIME,
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

def measCaRmCol(kker, resp, **kwargs):
    """
    measure the response matrix column between PVs: dresp/dkker.
    kker - PV for variable
    resp - PV list for response due to change of kker

    Optional:
    wait - default 1.5 seconds
    timeout - default 5 sec, EPICS CA timeout
    sample - default 5, observation per kick
    verbose - default 0
    output - output h5 file name
    dxlst - list of delta kick
    xlist - list of new kick
    dxmax - the range of kick [-dxmax, dxmax]

    returns m, dxlst, raw_data
    m - the response matrix column where m_i=dresp_i/dkker
    dxlst - the trial setpoint of dkker
    raw_data - (len(resp), len(dxlst), len(npoints))
    """

    wait    = kwargs.get("wait", 1.5)
    timeout = kwargs.get("timeout", 5)
    verbose = kwargs.get("verbose", 0)
    sample  = kwargs.get("sample", 5)

    t0 = datetime.now()
    n0 = len(resp)
    dxlst, x0 = [], caget(kker, timeout=timeout)
    if not x0.ok:
        raise RuntimeError("can not get data from %s" % kker)

    if "dxlst" in kwargs:
        dxlst = kwargs.get("dxlst")
    elif "xlst" in kwargs:
        dxlst = [ x - x0 for x in kwargs["xlst"][i]]
    elif "dxmax" in kwargs:
        nx = kwargs.get("nx", 5)
        dxmax = np.abs(kwargs["dxmax"])
        dxlst = list(np.linspace(-dxmax, dxmax, nx))
    else:
        raise RuntimeError("need input for at least of the parameters: "
                           "dxlst, xlst, dxmax")
    if verbose > 0:
        print "dx:", dxlst
    n1 = len(dxlst)
    m = np.zeros(n0, 'd')
    raw_data = np.zeros((n1, n0, sample), 'd')
    for i,dx in enumerate(dxlst):
        caput(kker, x0 + dx)
        time.sleep(wait)
        for j in range(sample):
            raw_data[i,:,j] = caget(resp, timeout=timeout)
            time.sleep(wait)
    caput(kker, x0)

    # return raw_data
    for i in range(n0):
        p, resi, rank, sv, rcond = np.polyfit(
            dxlst, np.average(raw_data[:,i,:], axis=1), 2, full=True)
        m[i] = p[1]
    if verbose > 0:
        print "dy/dx:", m
    t1 = datetime.now()
    output = kwargs.get("output", None)
    if not output:
        return m, dxlst, raw_data, None
    try:
        import h5py
        f = h5py.File(output)
        g = f.create_group(kker)
        g["resp"]     = resp
        g["dxlst"]    = dxlst
        g["raw_data"] = raw_data
        g["rmcol"]    = m
        g.attrs["sample"] = sample
        g.attrs["wait"] = wait
        g.attrs["timeout"] = timeout
        g.attrs["rm_t0"] = t0.strftime("%Y_%m_%d_%H:%M:%S.%f")
        g.attrs["rm_t1"] = t1.strftime("%Y_%m_%d_%H:%M:%S.%f")
        f.close()
    except:
        print "ERROR: can not create output file '%s'" % output
        raise
        return m, dxlst, raw_data
    return m, dxlst, raw_data, output


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
    nsv: use how many singular values, overwrite the option of rcond
    check : stop if the orbit gets worse.
    wait : waiting (seconds) before check.
    bc: str. bounds checking. 'ignore', 'abort', 'boundary', None
    kkerlim: (ncor, 2) array. The limits for controllers

    Returns
    --------
    err : converged or not checked (0), error (>0).
    msg : error message or None

    """
    scale  = kwarg.get('scale', 0.68)
    ref    = kwarg.get('ref', None)
    check  = kwarg.get('check', True)
    wait   = kwarg.get('wait', 6)
    rcond  = kwarg.get('rcond', 1e-3)
    verbose = kwarg.get('verbose', 0)
    lim    = kwarg.get('kkerlim', None)
    bc     = kwarg.get('bc', None)
    dImax  = kwarg.get('dImax', None)
    dryrun = kwarg.get('dryrun', False)

    _logger.info("nkk={0}, nresp={1}, scale={2}, rcond={3}, wait={4}".format(
            len(kker), len(resp), scale, rcond, wait))

    v0 = np.array(caget(resp), 'd')
    if ref is not None: v0 = v0 - ref
    
    # the initial norm
    norm0 = np.linalg.norm(v0)
    U, s, V = np.linalg.svd(m)
    if kwarg.get("nsv", None):
        assert kwarg["nsv"] <= len(s), "maxium singular values: %d" % len(s)
        rcond = s[kwarg["nsv"]-1] / s[0]
    # solve for m*dk + (v0 - ref) = 0
    dk, resids, rank, s = np.linalg.lstsq(m, -1.0*v0, rcond = rcond)

    norm1 = np.linalg.norm(m.dot(dk*scale) + v0)
    k0 = np.array(caget(kker), 'd')
    k1 = k0 + dk*scale

    kkerin, k1in = [], []
    if dImax is not None:
        im = np.argmax(np.abs(dk))
        dk = dk/np.abs(dk[im]) * dImax
        kkerin = [pv for pv in kker]
        k1in = k0 + dk
    elif not lim:
        kkerin = [pv for pv in kker]
        k1in   = [val for val in k1]
    elif np.shape(lim) == (len(dk), 2):
        alim = np.array(lim, 'd')
        kbd0 = min([v for v in (alim[:,1] - k0)/dk if v > 0.0])
        kbd1 = min([v for v in (alim[:,0] - k0)/dk if v > 0.0])
        ksc = min([kbd0, kbd1, scale])
        _logger.info("autoscale the set point with factor {0}({1})".format(
                ksc, scale))
        k1in = [val for val in k0 + dk*ksc]
    else:
        raise RuntimeError("boundary values set but no method")

    if verbose > 0:
        for i,pv in enumerate(kkerin):
            print i, pv, k1in[i], k1in[i] - k0[i]
        
    # the real setting
    if dryrun:
        return (0, "setting {0} cors, min= {1} max= {2}".format(
                len(kkerin), np.min(k1in), np.max(k1in)))
    else:
        caput(kkerin, k1in)

    # wait and check
    if check == True:
        time.sleep(wait)
        v1 = np.array(caget(resp), 'd')

        if ref is not None: v1 = v1 - np.array(ref)
        norm2 = np.linalg.norm(v1)
        msg = "Euclidian norm: pred./realized", norm1/norm0, norm2/norm0
        _logger.info(msg)
        if verbose > 0:
            print(msg)
        if norm2 > norm0:
            msg = "Failed to reduce orbit distortion, restoring..." 
            _logger.warn(msg) 
            #print(msg, norm0, norm2)
            caput(kker, k0)
            return (2, "{0} {1} {2}".format(msg, norm0, norm2))
        else:
            return (0, None)
    else:
        return (0, None)

def readPvs(pvs, **kwargs):
    """
    returns a list of (value, length, timestamp)
    """
    timeout = kwargs.get("timeout", 3)
    niter   = kwargs.get("niter", 3)
    # avoid double read in case pvs has duplicates.
    tmp = dict([(pv, None) for pv in pvs])
    tmppvs = tmp.keys()
    for i in range(niter):
        tmpdat = caget(tmppvs, format=FORMAT_TIME, timeout=timeout)
        dead = []
        for pv,val in zip(tmppvs, tmpdat):
            if not val.ok:
                dead.append(pv)
                continue
            try:
                tmp[pv] = (val, len(val), val.timestamp)
            except:
                tmp[pv] = (val, None, val.timestamp)
        tmppvs = dead
        for pv in tmppvs: tmp[pv] = (val, None, None)
    return [tmp[pv] for pv in pvs]


def savePvData(fname, pvs, **kwargs):
    """
    save pv data
    
    - group, default "/"
    - mode, default 'a' (append)
    - ignore, list of pvs to ignore
    - timeout, CA timeout, default 10 seconds.
    - extrapvs, a list of extra pvs. default []

    status, datetime and timestamp are recorded.
    """
    group  = kwargs.get("group", '/')
    mode   = kwargs.pop("mode", 'a')
    ignore = kwargs.get("ignore", [])
    timeout = kwargs.get("timeout", 10)

    import h5py
    h5f = h5py.File(fname, mode)
    grp = h5f.require_group(group)
    if kwargs.get("notes", ""):
        grp.attrs["notes"] = kwargs["notes"]

    allpvs = list(set(pvs + kwargs.get("extrapvs", [])))
    alldat = caget(allpvs, format=FORMAT_TIME, timeout=timeout)
    ndead, nlive = 0, 0
    for i,pv in enumerate(allpvs):
        dat = alldat[i]
        if not dat.ok:
            grp[pv] = ""
            grp[pv].attrs["ok"] = False
            ndead = ndead + 1
        else:
            grp[pv] = dat
            grp[pv].attrs["ok"] = True
            grp[pv].attrs["datetime"] = str(dat.datetime)
            grp[pv].attrs["timestamp"] = dat.timestamp
            nlive = nlive + 1
    h5f.close()
    return nlive, ndead

def putPvData(fname, group, **kwargs):
    """
    put saved lattice to real machine.

    sponly - only put setpoint pvs to the machine. default True
    """
    sponly = kwargs.get("sponly", True)
    
    import h5py
    h5f = h5py.File(fname, 'r')
    grp = h5f[group]
    
    pv, dat = [], []
    for k,v in grp.items():
        #caput(k, v)
        if sponly and v.attrs.get("setpoint", 0) != 1:
            continue
        pv.append(k)
        dat.append(v)
    caput(pv, dat)

    pass

