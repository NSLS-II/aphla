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
    'caget', 'casample', 'caput', 'caputwait', 'caRmCorrect', 
    'readPvs', 'measCaRmCol',
    'Timedout', 'CA_OFFLINE', 'FORMAT_TIME'
]

import sys, time, os
import cothread
import cothread.catools as ct
from datetime import datetime
from cothread import Timedout
from cothread.catools import camonitor, ca_nothing, FORMAT_TIME, FORMAT_CTRL
import random

import numpy as np

import logging
_logger = logging.getLogger(__name__)

CA_OFFLINE = False
CA_TIMEOUT = 10

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

def caget(pvs, timeout=CA_TIMEOUT, datatype=None, format=ct.FORMAT_TIME,
           count=0, throw=False, verbose=0, missing_values = None):
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

        rt, j = [], 0
        for i,pv in enumerate(pvs):
            if not pv:
                rt.append(missing_values)
            else:
                rt.append(dr[j])
                j = j + 1
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

def casample(pvs, nsample = 5, T=1):
    vl = []
    for i in range(nsample):
        vl.append(caget(pvs, missing_values=np.nan))
        time.sleep(T*1.0/nsample)
    va = np.array(vl)
    return np.average(va, axis=0), np.std(va, axis=0)
    
def caput(pvs, values, timeout=CA_TIMEOUT, wait=True, throw=True, verbose = 0):
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

def measCaRmCol(resp, kker, dxlst, **kwargs):
    """
    measure the response matrix column between PVs: dresp/dkker.
    kker - PV for variable
    resp - PV list for response due to change of kker

    Optional:
    wait - default 1.5 seconds
    timeout - default 5 sec, EPICS CA timeout
    sample - default 5, observation per kick
    verbose - default 0
    dxlst - list of delta kick

    returns m, dxlst, raw_data
    m - the response matrix column where m_i=dresp_i/dkker
    dxlst - the trial setpoint of dkker
    raw_data - (len(resp), len(dxlst), len(npoints))
    """

    wait    = kwargs.get("wait", 1.5)
    timeout = kwargs.get("timeout", CA_TIMEOUT)
    verbose = kwargs.get("verbose", 0)
    sample  = kwargs.get("sample", 5)

    t0 = datetime.now()
    n0 = len(resp)
    x0 = caget(kker, timeout=timeout)
    if not x0.ok:
        raise RuntimeError("can not get data from %s" % kker)

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
    return m, dxlst, raw_data


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
    dImax: maximum increase of kker, None if no upper limit.
    nrespavg: takes average for resp

    Returns
    --------
    norm0 : initial norm
    norm1 : calculated norm
    norm2 : realized norm
    kker : setpoint, new or previous one if failed.
    """
    scale  = kwarg.get('scale', 0.68)
    ref    = kwarg.get('ref', None)
    check  = kwarg.get('check', True)
    wait   = kwarg.get('wait', 1)
    rcond  = kwarg.get('rcond', 1e-3)
    verbose = kwarg.get('verbose', 0)
    lim    = kwarg.get('kkerlim', None)
    bc     = kwarg.get('bc', None)
    dImax  = kwarg.get('dImax', None)
    dryrun = kwarg.get('dryrun', False)
    nrespavg = kwarg.get('nrespavg', 5)
    dtresp = kwarg.get("dtresp", 0.2)
    kkerstep = kwarg.get("kkerstep", 1)
    dtkker = kwarg.get("dtkker", 0.3)
    
    _logger.info("nkk={0}, nresp={1}, scale={2}, rcond={3}, wait={4}".format(
            len(kker), len(resp), scale, rcond, wait))

    v0, sig = casample(resp, nsample=nrespavg, T=nrespavg*dtresp)
    if ref is not None: v0 = v0 - ref
    
    # the initial norm
    norm0 = np.linalg.norm(v0)
    U, s, V = np.linalg.svd(m)
    if kwarg.get("nsv", None):
        assert kwarg["nsv"] <= len(s), "maxium singular values: %d" % len(s)
        rcond = s[kwarg["nsv"]-1] / s[0]
    # solve for m*dk + (v0 - ref) = 0
    dk, resids, rank, s = np.linalg.lstsq(m, -1.0*v0, rcond = rcond)

    k0 = np.array(caget(kker), 'd')
    k1 = k0 + dk*scale

    kkerin, k1in = [], []
    if dImax is not None and np.max(np.abs(dk)) > dImax:
        # scale only if necessary
        im = np.argmax(np.abs(dk))
        dk = dk/np.abs(dk[im]) * dImax
        kkerin = [pv for pv in kker]
        #k1in = k0 + dk
    elif not lim:
        kkerin = [pv for pv in kker]
        dk = dk * scale
        #k1in   = [val for val in k1]
    elif np.shape(lim) == (len(dk), 2):
        alim = np.array(lim, 'd')
        kbd0 = min([v for v in (alim[:,1] - k0)/dk if v > 0.0])
        kbd1 = min([v for v in (alim[:,0] - k0)/dk if v > 0.0])
        ksc = min([kbd0, kbd1, scale])
        _logger.info("autoscale the set point with factor {0}({1})".format(
                ksc, scale))
        #k1in = [val for val in k0 + dk*ksc]
        dk = dk * ksc
    else:
        raise RuntimeError("boundary values set but no method")

    if verbose > 0:
        for i,pv in enumerate(kkerin):
            print i, pv, "k0=", k0[i], " dk=", dk[i]

    norm1 = np.linalg.norm(m.dot(dk) + v0)
    # the real setting
    if dryrun:
        return norm0, norm1, norm0, np.zeros_like(dk)
    else:
        for i in range(kkerstep):
            k1in = k0 + dk * (i+1.0) / kkerstep
            caput(kkerin, k1in)
            time.sleep(dtkker)

    # wait and check
    time.sleep(wait)
    v1, sig = casample(resp, nsample=nrespavg, T=nrespavg*dtresp)
    if ref is not None: v1 = v1 - np.array(ref)
    norm2 = np.linalg.norm(v1)

    if check == True:
        msg = "Euclidian norm: pred./realized", norm1/norm0, norm2/norm0
        _logger.info(msg)
        if verbose > 0:
            print(msg)
        if norm2 > norm0:
            msg = "Failed to reduce orbit distortion, restoring..." 
            _logger.warn(msg) 
            #print(msg, norm0, norm2)
            caput(kker, k0)
            return norm0, norm1, norm2, np.zeros_like(k0)

    return norm0, norm1, norm2, dk


def readPvs(pvs, **kwargs):
    """
    returns a list of (value, length, timestamp)
    """
    timeout = kwargs.get("timeout", CA_TIMEOUT)
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
    timeout = kwargs.get("timeout", CA_TIMEOUT)

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

    sponly - only put setpoint pvs to the machine. default True.

    setpoint property is explicit, i.e. ff there is no "setpoint" information about the PV, then it is treated as non-setpoint.
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


def caWait(pvs, stop = 0, timeout = CA_TIMEOUT, dt = 0.2):
    """
    wait until all pvs == stop.
    """
    t0 = datetime.now()
    while True:
        dt10 = (datetime.now() - t0).total_seconds()
        vals = caget(pvs)
        if all([v == stop for v in vals]):
            return dt10
        if dt10 > timeout:
            raise RuntimeError(
                "Timeout ({4}/{2} sec) when waiting for {0} == {1} ({3})".format(
                    pvs, stop, timeout, vals, dt10))
        time.sleep(dt)
    return None


def caWaitStable(pvs, values, vallo, valhi, **kwargs):
    """read pvs and wait until the std less than epsilon

    Parameters
    -----------
    pvs : list or tuple. A list of PVs
    values : list or tuple. Same size as elemfld
    vallo : list or tuple with low boundary values.
    valhi : list or tuple with high boundary values.
    sample : int, optional, default 3, averaged over to compare
    timeout : int, optional, default 5, in seconds.
    dt      : float, default 0.1 second. waiting between each check.
    verbose : int.

    Examples
    ---------
    >>> cors = getElements("COR")
    >>> pvs = [cors[0].pv(field='x', handle="readback")[0], ]
    >>> cors[0].x = 0
    >>> waitReadback(pvs, [0.0, ], [-0.001,], [0.001,])

    """

    nsample = kwargs.pop("sample", 3)
    dt      = kwargs.pop("dt", 0.2)
    verbose = kwargs.get("verbose", 0)

    n, t0 = len(pvs), datetime.now()
    buf = np.zeros((nsample, n), 'd')

    iloop = 0
    while True:
        for i in range(nsample):
            # delay a bit
            time.sleep(dt/(nsample+1.0))
            buf[i,:] = caget(pvs, **kwargs)
            
        avg = np.average(buf, axis=0)
        #if verbose > 0:
        #    print "V:", avg
        #    print vallo
        #    print valhi

        if all([vallo[i] <= avg[i] <= valhi[i] for i in range(n)]):
            break
        t1 = datetime.now()
        if (t1 - t0).total_seconds() > kwargs.get("timeout", CA_TIMEOUT):
            vdiff = [avg[i] - values[i] for i in range(n)]
            raise RuntimeError("Timeout, tried {0} times, pv={1} "
                               "avg_vals= {2} lo= {3} hi={4}\n"
                               "above: {5}\nbelow: {6}".format(
                    iloop, pvs, avg, vallo, valhi, avg-vallo, valhi-avg))
        iloop = iloop + 1
        time.sleep(dt)
