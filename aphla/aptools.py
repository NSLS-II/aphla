"""
:author: Lingyun Yang <lyyang@bnl.gov>
:license:

Accelerator Physics Tools module defines some small AP routines.

"""

from __future__ import print_function

import numpy as np
import time, sys, os
from datetime import datetime
import itertools
import tempfile
import h5py

from . import machines
from catools import caRmCorrect, measCaRmCol
from hlalib import (getCurrent, getLifetimeCurrent, getExactElement,
    getElements, getNeighbors,
    getClosest, getRfFrequency, putRfFrequency, getTunes, getOrbit,
    getLocations, outputFileName, fget, fput, getBoundedElements,
    getGroupMembers)

import logging

__all__ = [ 'calcLifetime', 'measLifetime',  'measOrbitRm',
    'correctOrbit', 'setLocalBump', 'measTuneRm',
    'saveImage', 'fitGaussian1', 'fitGaussianImage',
    'stripView', 'measRmCol', 'getArchiverData',
    '_set3CorBump', 'setIdBump'
]

_logger = logging.getLogger(__name__)

def _zip_element_field(elems, fields, **kwargs):
    """
    * compress=True
    >>> _element_fields(getElements(['BPM1']), ['x', 'y'])
    
    returns a flat list of (name, field)
    """
    compress = kwargs.get('compress', True)
    choices  = kwargs.get('choices', [e.name for e in elems])
    ret = []
    for b,f in itertools.product(elems, fields):
        if b.name not in choices: continue
        if f in b.fields():
            ret.append((b.name, f))
        elif not compress:
            ret.append((b.name, None))
    return ret


def measLifetime(tinterval=3, npoints = 8, verbose=False):
    """
    Monitor current change in a time interval, calculate lifetime I/(dI/dt)

    :param tinterval: time interval between each measurement, in seconds.
    :param npoints: number of points for fitting the lifetime
    :param verbose: verbosity
    :return: life time in hours

    It takes about 30 seconds, 10 points will be recorded, about 3 seconds
    delay between each.

    least square linear fitting is applied for slop dI/dt
    """

    # data points
    ret = np.zeros((npoints, 2), 'd')
    d0 = datetime.now()
    ret[0, 1] = getCurrent()
    for i in range(1, npoints):
        # sleep for next reading
        time.sleep(tinterval)
        ret[i, 1] = getCurrent()
        dt = datetime.now() - d0
        ret[i, 0] = (dt.microseconds/1000000.0 + dt.seconds)/3600.0 + \
            dt.days*24.0
        if verbose:
            print(i, dt, ret[i, 1])
    dI = max(ret[:, 1]) - min(ret[:, 1]) 
    dt = max(ret[:, 0]) - min(ret[:, 0])
    lft_hour = np.average(ret[:, 1]) / (dI / dt)
    return lft_hour


def setLocalBump(bpmrec, correc, ref, **kwargs):
    """
    create a local bump at certain BPM, while keep all other orbit untouched
    
    :param list bpm: list of (name, field) for BPMs. 
    :param list trim: list of (name, field) for correctors. 
    :param list dead: name list of dead BPMs and correctors names.
    :param list ref: target values for the list of (bpmname, field).
    :param float scale: optional, factor to scale calculated kick strength change, between 0 and 1.0
    :param bool check: optional, roll back the corrector settings if the orbit gets worse.
    :param float rcond: optional, (1e-4). rcond*max_singularvalue will be kept.
    :param ormdata: optional, :class:`~aphla.apdata.OrmData`. Use provided OrmData instead of the system default.
    :return: `(err, msg)`. The error code and message.

    Notes
    ------
    if `ref[i][j]` is `None`, use the current hardware result, i.e. try not to
    change the orbit at that location.

    The bpm and corrector must have 'x' and 'y' field.

    This is a least square fitting method. It is possible that the orbit at
    the other BPMs may change slightly although they are told to be fixed.

    see also :func:`~aphla.catools.caRmCorrect` for EPICS based
    system. :func:`~aphla.apdata.OrmData.getMatrix`

    Examples
    ---------
    >>> bpms = getGroupMembers(['BPM', 'C02'])
    >>> newobt = [[1.0, 1.5]] * len(bpms)
    >>> createLocalBump(bpms, getElements('HCOR'), newobt)
    
    """

    ormdata = kwargs.pop('ormdata', machines._lat.ormdata)
    repeat = kwargs.pop('repeat', 1)
    fullm = kwargs.pop("fullm", True)

    if ormdata is None:
        raise RuntimeError("No Orbit Response Matrix available for '%s'" %
            machines._lat.name)
    if fullm:
        # use the full available matrix
        bpmr = ormdata.getBpm()
        corr = ormdata.getCor()
        m = ormdata.m
        obtref = [None] * len(m)
        for i,(b,fld) in enumerate(bpmr):
            if (b,fld) not in bpmrec: continue
            k = bpmrec.index((b, fld))
            obtref[i] = ref[k]
    else:
        # use the sub common set
        bpmr = [r for r in ormdata.bpm if r in bpmrec]
        corr = [r for r in ormdata.cor if r in correc]
        m = np.zeros((len(bpmr), len(corr)), 'd')
        obtref = [None] * len(bpmr)
        for i,br in enumerate(bpmr):
            k = bpmrec.index(br)
            obtref[i] = ref[k]
            for j,cr in enumerate(corr):
                m[i,j] = ormdata.get(br, cr)

    # if ref orbit is not provided, use the current reading
    for i,(name,field) in enumerate(bpmr):
        if obtref[i] is not None: continue
        obtref[i] = getExactElement(name).get(field, unitsys=None)

    bpmpvs = [getExactElement(b).pv(field=f)[0] for b,f in bpmr]
    corpvs = [getExactElement(t).pv(field=f, handle='setpoint')[0] 
               for t,f in corr]

    # correct orbit using default ORM (from current lattice)
    norm0, norm1, norm2, corvals = None, None, None, None
    for i in range(repeat):
        #for k,b in enumerate(bpmpvs):
        #    if bpmref[k] != 0.0: print(k, bpmlst[k], b, bpmref[k])
        norm0, norm1, norm2, corvals = \
            caRmCorrect(bpmpvs, corpvs, m, ref=np.array(obtref), **kwargs)
        if corvals is None: break

    return norm0, norm1, norm2, corvals


def correctOrbit(bpm, cor, **kwargs):
    """
    correct the orbit with given BPMs and Trims

    Parameters
    -----------
    bpm : list of BPM objects, default all 'BPM'
    cor : list of Trim objects, default all 'COR'
    plane : optional, [ 'XY' | 'X' | 'Y' ], default 'XY'
    rcond : optional, cutting ratio for singular values, default 1e-4.
    scale : optional, scaling corrector strength, default 0.68
    repeat : optional, integer, default 1. numbers of correction 
    deadlst : list of dead BPM and corrector names.
    dImax : optional, maximum corrector change at correction.


    Notes
    -----
    This routine prepares the target orbit and then calls :func:`setLocalBump`.

    seealso :func:`~aphla.hlalib.getElements`, :func:`~aphla.getSubOrm`,
    :func:`setLocalBump`.

    Examples
    ---------
    >>> bpms = getElements(['BPM1', 'BPM2'])
    >>> trims = getElements(['T1', 'T2', 'T3'])
    >>> correctOrbit(bpms, trims) 
    """

    plane = kwargs.pop('plane', 'XY').lower()

    # using rcond 1e-4 if not provided.
    kwargs.setdefault('rcond', 1e-4)
    kwargs.setdefault('scale', 0.68)

    bpmlst = [e for e in getElements(bpm) if e.isEnabled()]
    corlst = [e for e in getElements(cor) if e.isEnabled()]

    if kwargs.get("verbose", 0) > 0:
        print("Using: %d bpms, %d cors" % (len(bpmlst), len(corlst)))
    bpmr, corr, ref = [], [], []
    for fld in ["x", "y"]:
        for bpm in bpmlst:
            if fld in bpm.fields() and fld in plane:
                bpmr.append((bpm.name, fld))
                ref.append(0.0)
        for cor in corlst:
            if fld in cor.fields() and fld in plane:
                corr.append((cor.name, fld))

    if kwargs.get("verbose", 0) > 0:
        print("Using: %d bpms, %d cors" % (len(bpmr), len(corr)))
    kwargs["fullm"] = False
    return setLocalBump(bpmr, corr, ref, **kwargs)


def _random_kick(plane = 'V', amp=1e-9, verbose = 0):
    """
    kick the beam with a random kicker
    """
    
    dk = np.random.rand() * amp
    if plane == 'V':
        trim = getElements('VCOR')
    elif plane == 'H':
        trim = getElements('HCOR')
    else:
        raise ValueError("unknow plane '%s'" % plane)

    i = np.random.randint(len(trim))
    k0 = trim[i].value
    if verbose:
        print("setting %s %e shift %e" % (trim[i].name, k0, dk))
    trim[i].value = k0 + dk
    

def calcLifetime(t, I, data_subdiv_method = 'NoSubdiv',
                 calc_method = 'expDecayFit', subNPoints = 10,
                 subDurationSeconds = 10.0, **kwargs):
    """calculate beam lifetime.

    :author: Yoshiteru Hidaka
    
    *kwargs* can contain optional parameters "p0" (initial guess for
    the fit parameters) and "sigma" (weight factors) for
    scipy.optimize.curve_fit.
    
    Parameters
    -----------
    data_subdiv_method : 'NoSubdiv', 'SubdivEqualNPoints', 'SubdivEqualSeconds'
        'NoSubdiv', The function will apply the specified lifetime calculation
        method on the entire time and beam current data. Hence, only a single
        value of lifetime will be returned. The time corresponding for the
        single lifetime value is calculated as (t_start + t_end)/2, and will
        be returned along with the lifetime value.

        'SubdivEqualNPoints', The function will first subdivide the given time
        and beam current data into a data subset with an equal number of data
        points specified by the optional input arument "subNPoints".  For each
        data subset, the specified lifetime calculation method will be
        applied. Hence, a vector of lifetime values will be returned.  The
        corresponding time vector is calculated using the same method as in
        'NoSubdiv', applied for each data subset. This time vector will be
        returned along with the lifetime vector.
             
        'SubdivEqualSeconds', This is similar to 'SubdivEqualNPoints', but the
        subdivision occurs based on an equal time period in seconds specified
        by the optional input argument "subDurationSeconds".
    calc_method : 'expDecayFit', 'avg_I_over_MaxDropRate', 'avg_I_over_LinearFitDropRate'
        'expDecayFit': The function will estimate the lifetime "tau" [hr] by fitting a
        data set of time (t) and current (I) to the exponential decay
        equation: I(t) = I_0 * exp( - t / tau )
                        
        'avg_I_over_MaxDropRate', The function will estimate the lifetime
        value by dividing the average beam current over the given data set by
        the maximum current drop rate ( = Delta_I / Delta_t). The average
        current is given by calculating the mean of the beam current vector in
        the data set. The maximum current drop rate is defined as (I_max -
        I_min) divided by (t_end - t_start).
             
        'avg_I_over_LinearFitDropRate', The function will estimate the
        lifetime value by dividing the average beam current over the given
        data set by the linearly fit current drop rate ( = dI/dt). The average
        current is given by calculating the mean of the beam current vector in
        the data set. The current drop rate is given by the slope of the best
        line fit to the data set.
    subNPoints: is only used if data_subdiv_method = 'SubdivEqualNPoints'
    subDurationSeconds : is only used if data_subdiv_method = 'SubdivEqualSeconds'

    Returns
    -------
    returns: This function returns beam lifetime array or scalar value with
        different data subdivision and calculation methods, given arrays
        of time (t) in hours and beam current (I) in whatever unit.

    """
    
    if isinstance(t, (float, int)) :
        t = np.array([t])
    elif isinstance(t, list) :
        t = np.array(t)
    elif isinstance(t, np.ndarray) :
        pass
    else :
        raise ValueError('The time input argument must be either ',
                         'float, int, or list of (int,float), or NumPy array.')
    
        
    if isinstance(I, (float, int)) :
        I = np.array([I])
    elif isinstance(I, list) :
        I = np.array(I)
    elif isinstance(I, np.ndarray) :
        pass
    else :
        raise ValueError('The beam current input argument must be either ',
                         'float, int, or list of (int,float), or NumPy array.')
    
    minNPoints = 6
    
    if data_subdiv_method is 'NoSubdiv' :
        t_list = [t]
        I_list = [I]
        t_avg = [(t[0]+t[-1])/2]
        
    elif data_subdiv_method is 'SubdivEqualNPoints' :
        if subNPoints < minNPoints:
            raise ValueError('Number of data points for lifetime estimation ' +
                             'should be larger than ' + str(minNPoints) + '.')
        
        start_ind = range(0,            len(t), subNPoints)
        end_ind   = range(subNPoints-1, len(t), subNPoints)
        
        if len(start_ind) == ( len(end_ind)+1 ) :
            end_ind.append(len(t)-1)
        elif len(start_ind) == len(end_ind) :
            pass
        else :
            raise ValueError('You should not see this message.')
        
        t_list = [t[start_ind[i]:end_ind[i]] for i in range(len(start_ind))]
        I_list = [I[start_ind[i]:end_ind[i]] for i in range(len(start_ind))]
                
        # If the final subdivision contains less than minNPoints, then
        # remove the final subdivision since you cannot estimate lifetime
        # with that few data points.
        if len(t_list[-1]) < minNPoints :
            t_list = t_list[:-1]
            I_list = I_list[:-1]
            print('The final subdivision does not contain enough data points '
                  'for lifetime estimation. So, it is ignored.')
        
        t_avg = [(t[0]+t[-1])/2 for t in t_list]

    elif data_subdiv_method is 'SubdivEqualSeconds' :

        subDurationSeconds = float(subDurationSeconds)
        
        if subDurationSeconds <= 0:
            raise ValueError('Duration of each time subarray for lifetime ' +
                             'estimation must be positive.')
        dt_sec = (t - t[0])*60*60 # [seconds]
        
        nSubdiv = int(np.ceil(dt_sec[-1]/subDurationSeconds))
        
        t_list = []
        start_ind = [0]
        end_ind = []
        for i in range(nSubdiv):
            for j in range(start_ind[i], len(dt_sec)):
                if dt_sec[j] > (subDurationSeconds*(i+1)) :
                    if j+1 != len(dt_sec) : # When the end of dt_sec is not yet reached
                        end_ind.append(j)
                        start_ind.append(j+1)
                        break
                    else : # When the end of dt_sec is reached
                        end_ind.append(j)
                elif j+1 == len(dt_sec) : # When the end of dt_sec is reached
                    end_ind.append(j)
                    
        t_list = [t[start_ind[i]:end_ind[i]] for i in range(len(start_ind))]
        I_list = [I[start_ind[i]:end_ind[i]] for i in range(len(start_ind))]
                
        # If the final subdivision contains less than minNPoints, then
        # remove the final subdivision since you cannot estimate lifetime
        # with that few data points.
        if len(t_list[-1]) < minNPoints :
            t_list = t_list[:-1]
            I_list = I_list[:-1]
            print('The final subdivision does not contain enough data points '
                  'for lifetime estimation. So, it is ignored.')
        
        t_avg = [(t[0]+t[-1])/2 for t in t_list]
                                
    else :
        raise ValueError('Invalide data subdivision method name.')
    
    result = {}
    
    result["avg_time_hr_array"] = t_avg
    
    import hla.curve_fitting as curve_fitting
    
    if calc_method is 'expDecayFit' :
        
        def exp_decay (t_vec, I_0, tau) :
            return I_0 * np.exp( - (t_vec-t_vec[0]) / tau )
                
        fit_object_list = []
        lifetime_hr_list = []
        lifetime_hr_error_list = []
        t_fit_list = []
        I_fit_list = []
        
        
        p0 = kwargs.get('p0', None)
        sigma = kwargs.get('sigma', None)

        for ii in range(len(t_list)) :
            
            if p0 is None :
                tau_estimate = np.mean(I_list[ii]) /    \
                ((np.max(I_list[ii])-np.min(I_list[ii]))/(t_list[ii][-1]-t_list[ii][0]))
                p0 = (I_list[ii][0], tau_estimate)
            if sigma is None :
                pass

            fit_object_list.append( curve_fitting.Custom(
                exp_decay, t_list[ii], I_list[ii], p0, sigma ) )
        
            lifetime_hr_list.append(
                fit_object_list[ii].opt_fit_param_values[1] )
            lifetime_hr_error_list.append(
                fit_object_list[ii].opt_fit_uncertainties[1] )
            
            t_fit_list.append( t_list[ii] )
            I_fit_list.append(
                exp_decay(t_list[ii], *fit_object_list[ii].opt_fit_param_values)
                )
        
        result["fit_object_list"] = fit_object_list
        result["lifetime_hr_list"] = lifetime_hr_list
        result["lifetime_hr_error_list"] = lifetime_hr_error_list
        result["t_fit_list"] = t_fit_list
        result["I_fit_list"] = I_fit_list
        
    elif calc_method is 'avg_I_over_MaxDropRate' :
        
        lifetime_hr_list = []
        
        for ii in range(len(t_list)) :
            
            t_sub = t_list[ii]
            I_sub = I_list[ii]
            
            avg_I = np.mean(I_sub)
            
            max_current_drop_rate = \
                (np.max(I_sub) - np.min(I_sub)) /    \
                (t_sub[-1] - t_sub[0])
            
            lifetime_hr_list.append( avg_I/max_current_drop_rate )
            
        result["lifetime_hr_list"] = lifetime_hr_list
        
    elif calc_method is 'avg_I_over_LinearFitDropRate' :
        
        fit_object_list = []
        lifetime_hr_list = []
        lifetime_hr_error_list = []
        t_fit_list = []
        I_fit_list = []
        
        for ii in range(len(t_list)) :
            
            t_sub = t_list[ii]
            I_sub = I_list[ii]
            
            avg_I = np.mean(I_sub)
            
            deg = 1

            fit_object_list.append( curve_fitting.Polynomial(t_sub, I_sub, deg) )
            
            linear_fit_current_drop_rate = np.abs(
                fit_object_list[ii].opt_fit_param_values[0] )
            linear_fit_current_drop_rate_error = \
                fit_object_list[ii].opt_fit_uncertainties[0]
            fractional_error = \
                linear_fit_current_drop_rate_error/linear_fit_current_drop_rate
            
            lifetime_hr = avg_I/linear_fit_current_drop_rate
            
            lifetime_hr_list.append( lifetime_hr )
            lifetime_hr_error_list.append( lifetime_hr*fractional_error )
            
            t_fit_list.append(t_sub)
            I_fit_list.append(
                np.polyval(fit_object_list[ii].opt_fit_param_values, t_sub) )
        
        
        result["fit_object_list"] = fit_object_list
        result["lifetime_hr_list"] = lifetime_hr_list
        result["lifetime_hr_error_list"] = lifetime_hr_error_list
        result["t_fit_list"] = t_fit_list
        result["I_fit_list"] = I_fit_list
        
    else :
        raise ValueError('Invalid lifetime calculation method name.')
    
    
    
    return result


#---
def _gaussian(height, center_x, center_y, width_x, width_y):
    """Returns a gaussian function with the given parameters"""
    width_x = float(width_x)
    width_y = float(width_y)
    return lambda x,y: height*np.exp(
                -(((center_x-x)/width_x)**2+((center_y-y)/width_y)**2)/2)

def _moments(data):
    """
    Returns (height, x1, x2, width1, width2)
    the gaussian parameters of a 2D distribution by calculating its
    moments
    """
    total = data.sum()
    X, Y = np.indices(data.shape)
    x = (X*data).sum()/total
    y = (Y*data).sum()/total
    col = data[:, int(y)]
    width_x = np.sqrt(abs((np.arange(col.size)-y)**2*col).sum()/col.sum())
    row = data[int(x), :]
    width_y = np.sqrt(abs((np.arange(row.size)-x)**2*row).sum()/row.sum())
    height = data.max()
    return height, x, y, width_x, width_y

def _fitgaussian(data):
    """
    Returns (height, x, y, width_x, width_y)
    the gaussian parameters of a 2D distribution found by a fit
    """
    from scipy import optimize
    params = _moments(data)
    errorfunction = lambda p: \
        np.ravel(_gaussian(*p)(*np.indices(data.shape)) - data)
    p, success = optimize.leastsq(errorfunction, params)
    return p

def fitGaussian1(x, y):
    """
    fit y=A*exp(-(x-u)**2/2*sig**2) from moments, returns A, u, sig
    """
    u = np.sum(x*y)/np.sum(y)
    w = np.sqrt(np.abs(np.sum((x-u)**2*y)/np.sum(y)))
    A = np.max(y)
    return A, u, w

def fitGaussianImage(data):
    """
    2D gaussian fitting.

    :param data: 2D matrix
    :rtype: (height, x1, x2, width1, width2)

    The "1" and "2" are first and second indeces of input data matrix.
    """
    return _fitgaussian(data)


def saveImage(elemname, filename, **kwargs):
    """
    save field as image file

    :param field: element field to save, default 'image'
    :param filename: output file name
    :param width: image width (pixel), default 'image_nx'
    :param height: image height (pixel), default 'image_ny'
    :param xlim: range of pixels, e.g. (700, 900)
    :param ylim: range of pixels, e.g. (700, 900)

    :Example:

        >>> saveImage('VF1BD1', 'test.png', fitgaussian=True, xlim=(750,850), ylim=(550,650))

    The tag of CFS should give "field_nx" and "field_ny" for field.

    if width or height is None, use "field_nx" and "field_ny".
    """
    #import Image
    #import ImageDraw
    import matplotlib.pylab as plt
    import numpy as np
    field = kwargs.get('field', 'image')
    fitgaussian = kwargs.get('fitgaussian', False)
    elem = getElements(elemname)[0]
    d = elem.get(field, unitsys=None)
    width = kwargs.get('width', elem.get(field + "_nx", unitsys=None))
    height = kwargs.get('height', elem.get(field + "_ny", unitsys=None))
    xlim = kwargs.get('xlim', (0, width))
    ylim = kwargs.get('ylim', (0, height))
    d2 = np.reshape(d, (height, width))
    use_pil = False
    if use_pil:
        im = Image.fromarray(d2)
        im.save(filename)
    else:
        plt.clf()
        fig = plt.figure()
        ax = fig.add_subplot(111)
        im = ax.imshow(d2, interpolation="nearest", cmap=plt.cm.jet,
                       origin=kwargs.get("origin", "upper"))
        cb = plt.colorbar(im)
        #ax.set_xlim(xlim)
        #ax.set_ylim(ylim)
        if fitgaussian:
            params = fitGaussianImage(d2)
            (height, y, x, width_y, width_x) = params

            ax.text(0.95, 0.05, "x : %.1f\ny : %.1f\n" \
                        "width_x : %.1f\nwidth_y : %.1f" % \
                        (x, y, width_x, width_y),
                    fontsize=16, horizontalalignment='right',
                    verticalalignment='bottom', transform=ax.transAxes)
        plt.savefig(filename)


def _checkOrbitRmData(od):
    vbpm, vtrim = [], []
    for rec in od.bpm:
        if rec[0] is None:
            vbpm.append([None, None, None])
            continue
        elem = getElements(rec[0].lower())
        if not elem:
            vbpm.append([rec[0], None, None])
            continue
        pv = elem[0].pv(field=rec[1].lower(), handle='readback')
        if pv != rec[2]:
            vbpm.append([elem[0].name, rec[2], pv])
    #for v in vbpm: print (v)

    for rec in od.trim:
        if rec[0] is None:
            vtrim.append([None, None, None, None])
            continue
        elem = getElements(rec[0].lower())
        if not elem:
            vtrim.append([rec[0], None, None, None])
            continue
        pv = elem[0].pv(field=rec[1].lower(), handle='readback')
        if pv != rec[2]:
            vtrim.append([elem[0].name, rec[2], pv])

        pv = elem[0].pv(field=rec[1].lower(), handle='setpoint')
        if pv != rec[3]:
            vtrim.append([elem[0].name, rec[3], pv])
    #for v in vtrim: print (v)
        
    return vbpm, vtrim

def measTuneRm(quad, **kwargs):
    """
    measure the tune response matrix
    """
    output = kwargs.pop("output", None)
    if output is True:
        output = outputFileName("respm", "tunerm")

    qls = getElements(quad)
    _logger.info("Tune RM: {0}".format([q.name for q in qls]))
    quads = []
    for i,q in enumerate(qls):
        pv = q.pv(field="b1", handle="setpoint")
        if not pv: continue
        assert len(pv) == 1, "More than 1 pv found for {0}".format(q.name)
        quads.append((q.name, "b1", pv[0]))
    tune = getElements("tune")
    if not tune:
        raise RuntimeError("Can not find tune element")
    assert "x" in tune[0].fields(), "Can not find tune x"
    assert "y" in tune[0].fields(), "Can not find tune y"

    nupvs = [tune[0].pv(field="x", handle="readback")[0],
             tune[0].pv(field="y", handle="readback")[0]]
    m = np.zeros((2, len(quads)), 'd')

    for i,(name,fld,pv) in enumerate(quads):
        mc, dxlst, rawdat = measCaRmCol(pv, nupvs, **kwargs)
        m[:,i] = mc
        time.sleep(kwargs.get("wait", 1.5))
        if output:
            f = h5py.File(output)
            if pv in f:
                del f[pv]
            g = f.create_group(pv)
            g["m"] = m[:,i]
            g["m"].attrs["quad_name"] = name
            g["m"].attrs["quad_field"] = fld
            g["m"].attrs["quad_pv"] = pv
            g["tunes"] = rawdat
            g["tunes"].attrs["pv"] = nupvs
            g["dx"] = dxlst
            f.close()
    if output:
        f = h5py.File(output)
        if "m" in f:
            del f["m"]
        f["m"] = m
        f["m"].attrs["quad_name"]  = [r[0] for r in quads]
        f["m"].attrs["quad_field"] = [r[1] for r in quads]
        f["m"].attrs["quad_pv"]    = [r[2] for r in quads]
        f.close()

    return m


def measChromRm(sextlst):
    """
    measure chromaticity response matrix for sextupoles
    
    seealso :func:`~aphla.hlalib.getTunes`

    :warn: NotImplemented
    """
    raise NotImplementedError()

def measRmCol(resp, kker, kfld, dklst, **kwargs):
    """
    measure the response matrix of `resp` from `kicker`

    :param list resp: list of the response (elem, field)
    :param kker: the kicker object
    :param kfld: the kicker field
    :param list dklst: the kicker setpoints (ki0, ki1, ...)
    :param int sample: observatins per kicker setpoint
    :param int deg: degree of the fitting polynomial
    :param int verbose:

    returns slope, klst(readback), rawdata (nk, nresp, nsamle)
    """
    unitsys = kwargs.pop("unitsys", None)
    sample  = kwargs.pop("sample", 3)
    deg     = kwargs.pop("deg", 1)
    minwait = kwargs.pop("minwait", 0.0)

    dat = np.zeros((len(dklst), len(resp), sample), 'd')
    klstrb = np.zeros((len(dklst), sample), 'd')
    k0 = kker.get(kfld, handle="setpoint", unitsys=None)
    for i,dki in enumerate(dklst):
        try:
            fput([(kker, kfld, k0+dki),], unitsys=unitsys,
                 wait_readback=True, verbose=1)
        except:
            #kker.put(kfld, k0, unitsys=None)
            _logger.error("{0}".format(sys.exc_info()[0]))
            _logger.error("{0}".format(sys.exc_info()[1]))
            #_logger.error("{0}".format(sys.exc_info()[2]))
            msg = "Timeout at setting {0}.{1}= {2}, i= {3}, delta= {4}".format(
                kker.name, kfld, k0+dki, i, dki)
            _logger.warn(msg)
            time.sleep(5.0)
            print("{0}.{1}= {2} (set:{3}). continued after 5.0 second".format(
                    kker.name, kfld,
                    kker.get(kfld, unitsys=unitsys), k0+dki))
            sys.stdout.flush()

        time.sleep(minwait)
        for j in range(sample):
            klstrb[i,j] = kker.get(kfld, handle="readback", unitsys=unitsys)
            if kwargs.get("verbose", 0) > 0:
                print("Reading", kker, klstrb[i,j])
            dat[i,:,j] = fget(resp, unitsys=None, **kwargs)

    # nonblocking
    kker.put(kfld, k0, unitsys=None)
    p, resi, rank, sv, rcond = np.polyfit(
        dklst, np.average(dat, axis=-1), deg, full = True)
    # blocking
    try:
        fput([(kker, kfld, k0),], unitsys=None, wait_readback=True)
    except:
        kker.put(kfld, k0, unitsys=None)
        msg = "Timeout at restoring {0}.{1}= {2}".format(kker.name, kfld, k0)
        _logger.warn(msg)
        print(msg)
        sys.stdout.flush()
        
    return p[-2,:], klstrb, dat

#
def measOrbitRm(bpmfld, corfld, **kwargs):
    """
    Measure the orbit response matrix

    :param list bpm: list of (bpm, field)
    :param list trim: list of (trim, field)
    :param str output: output filename
    :param str h5group: data group name for HDF5 output, "OrbitResponseMatrix"
    :param float minwait: waiting seconds before each orbit measurement.
    :param list dxlst:
    :param list dxmax: 
    :param int nx: default 4

    seealso :class:`~aphla.respmat.OrbitRespMat`, 
    :func:`~aphla.respmat.OrbitRespMat.measure`

    quit when beam current < Imin(0.1mA)
    """
    verbose = kwargs.pop("verbose", 0)
    output  = kwargs.pop("output", None)
    Imin    = kwargs.pop("Imin", 0.1)
    minwait = kwargs.get("minwait", 0.0)

    if output is True:
        output = outputFileName("respm", "orm")
    h5group = kwargs.pop("h5group", "OrbitResponseMatrix")

    _logger.info("Orbit RM shape (%d %d)" % (len(bpmfld), len(corfld)))
    #bpms, cors = [], []
    ## if it is EPICS
    #for fld in ["x", "y", "db0"]:
    #    for e in getElements(bpm):
    #        if fld not in e.fields(): continue
    #        for pv in e.pv(field=fld, handle="readback"):
    #            bpms.append((e.name, fld, pv))
    #    for e in getElements(cor):
    #        if fld not in e.fields(): continue
    #        for pv in e.pv(field=fld, handle="setpoint"):
    #            cors.append((e.name, fld, pv))
    # measure the column

    if "dxlst" in kwargs:
        dxlst = kwargs.pop("dxlst")
    elif "dxmax" in kwargs:
        dxmax, nx = np.abs(kwargs.pop("dxmax", 0.0)), kwargs.pop("nx", 4)
        dxlst = list(np.linspace(-dxmax, dxmax, nx))
    else:
        raise RuntimeError("need input for at least of the parameters: "
                           "dxlst, dxmax")

    t0 = datetime.now()
    tau0, Icur0 = getLifetimeCurrent()
    m = np.zeros((len(bpmfld), len(corfld)), 'd')
    if verbose > 0:
        print("total steps: %d" % len(corfld))
        kwargs["verbose"] = verbose - 1
    
    for i,(cor, fld) in enumerate(corfld):
        # save each column
        m[:,i], xlst, dat = measRmCol(bpmfld, cor, fld, dxlst, **kwargs)
        tau, Icur = getLifetimeCurrent()
        if verbose:
            print("%d/%d" % (i, len(corfld)), cor.name, np.min(m[:,i]), np.max(m[:,i]))

        if output:
            f = h5py.File(output)
            #g0 = f.require_group("OrbitResponseMatrix")
            g0 = f.require_group(h5group)
            grpname = "resp__%s.%s" % (cor.name, fld)
            if grpname in g0: del g0[pv]
            g = g0.create_group(grpname)
            g.attrs["lifetime"] = tau
            g.attrs["current"] = Icur
            g["m"] = m[:,i]
            g["m"].attrs["cor_name"] = cor.name
            g["m"].attrs["cor_field"] = fld
            g["m"].attrs["cor_dxlst_sp"] = dxlst
            g["m"].attrs["cor_xlst_rb"] = xlst
            #g["m"].attrs["cor_pv"] = cor.pv(field=fld, handle="setpoint")
            #g["m"].attrs["bpm_pv"] = [b.pv(field=fld) for b,fld in bpmfld]
            g["m"].attrs["bpm_name"] = [b.name for b,fld in bpmfld]
            g["m"].attrs["bpm_field"] = [fld for b,fld in bpmfld]
            g["orbit"] = dat
            #g["orbit"].attrs["pv"] = [b.pv(field=fld) for b,fld in bpmfld]
            g["cor"] = xlst
            f.close()
        if Icur < Imin: break

    t1 = datetime.now()
    tau1, Icur1 = getLifetimeCurrent()
    if output:
        # save the overall matrix
        f = h5py.File(output)
        g = f.require_group(h5group)
        if "m" in g:
            del g["m"]
        g["m"] = m
        g["m"].attrs["cor_name"]  = [c.name for c,fld in corfld]
        g["m"].attrs["cor_field"] = [fld for c,fld in corfld]
        #corpvs = reduce(lambda x,y: x+y, [c.pv(field=fld) for c,fld in corfld])
        #g["m"].attrs["cor_pv"]    = corpvs
        g["m"].attrs["bpm_name"]  = [b.name for b,fld in bpmfld]
        g["m"].attrs["bpm_field"] = [fld for b,fld in bpmfld]
        #g["m"].attrs["bpm_pv"]    = pv_bpm
        try:
            import getpass
            g["m"].attrs["_author_"] = getpass.getuser()
        except:
            pass
        g["m"].attrs["t_start"] = t0.strftime("%Y-%m-%d %H:%M:%S.%f")
        g["m"].attrs["t_end"] = t1.strftime("%Y-%m-%d %H:%M:%S.%f")
        g.attrs["timespan"] = (t1-t0).total_seconds()
        g.attrs["current"] = [Icur0, Icur1]
        g.attrs["lifetime"] = [tau0, tau1]
        f.close()

    return m, output


def getSubOrm(bpm, trim, flags = 'XX'):
    """
    get submatrix of Orm

    :warn: NotImplemented
    """
    #return _orm.getSubMatrix(bpm, trim, flags)
    raise NotImplementedError()


def stripView(elempat, field, **kwargs):
    """
    open a striptool to view live stream data

    - elempat, element name, name list, object list, family or pattern.
    - field, element field
    - handle, optional, "readback" or "setpoint"
    - pvs, optional, extra list of PVs.
    """
    handle = kwargs.get("handle", "readback")
    pvs = kwargs.get("pvs", [])
    for e in getElements(elempat):
        pvs.extend(e.pv(field=field, handle=handle))

    fcfg, fname = tempfile.mkstemp(suffix=".stp", prefix="aphla-", text=True)
    import os
    os.write(fcfg, """StripConfig                   1.2
Strip.Time.Timespan           300
Strip.Time.NumSamples         7200
Strip.Time.SampleInterval     1.000000
Strip.Time.RefreshInterval    1.000000
Strip.Color.Background        65535     65535     65535     
Strip.Color.Foreground        0         0         0         
Strip.Color.Grid              49087     49087     49087     
Strip.Color.Color1            0         0         65535     
Strip.Color.Color2            27499     36494     8995      
Strip.Color.Color3            42405     10794     10794     
Strip.Color.Color4            24415     40606     41120     
Strip.Color.Color5            65535     42405     0         
Strip.Color.Color6            41120     8224      61680     
Strip.Color.Color7            65535     0         0         
Strip.Color.Color8            65535     55255     0         
Strip.Color.Color9            48316     36751     36751     
Strip.Color.Color10           39578     52685     12850     
Strip.Option.GridXon          1
Strip.Option.GridYon          1
Strip.Option.AxisYcolorStat   1
Strip.Option.GraphLineWidth   2
""")
    for i,pv in enumerate(pvs):
        os.write(fcfg, "Strip.Curve.%d.Name       %s\n" % (i, pv))
        #os.write(fcfg, "Strip.Curve.%d.Units      mA\n" % i)
        #os.write(fcfg, "Strip.Curve.%d.Min      0.0\n" % i)
        #os.write(fcfg, "Strip.Curve.%d.Max      1.0\n" % i)
        #os.write(fcfg, "Strip.Curve.%d.Comment    %d\n" % (i, i))
        os.write(fcfg, "Strip.Curve.%d.Precision  6\n" % i)
        os.write(fcfg, "Strip.Curve.%d.Scale      0\n" % i)
        os.write(fcfg, "Strip.Curve.%d.PlotStatus 1\n" % i)
    os.close(fcfg)

    from subprocess import Popen
    Popen(["striptool", fname])


def getArchiverData(*argv, **kwargs):
    """
    >>> getArchiverData("DCCT", "I")
    >>> getArchiverData(["SR:C03-BI{DCCT:1}AveI-I",])
    >>> getArchiverData(["pv1", "pv2"], s="-1 h")
    >>> getArchiverData(["pv1", "pv2"], s="-2 h", e="-1 h")
    >>> getArchiverData(["pv1", "pv2"], s="2014-11-11 00:00:00", e="-1 h")

    see manual arget for "-s" and "-e" parameter.

    Returns a dictionary of (pv, data). The data is (n,2) array. 2 columns are
    t seconds and the data. If data is an empty list, the pv might not being
    archived.
    """
    if len(argv) == 1 and isinstance(argv[0], (str, unicode)):
        pvs = argv
    elif len(argv) == 1 and isinstance(argv[0], (list, tuple)):
        pvs = argv[0]
    elif len(argv) == 2:
        pvs = reduce(lambda x,y: x + y, 
                     [e.pv(field=argv[1],
                           handle=kwargs.get("handle", "readback"))
                      for e in getElements(argv[0])])
    fh, fname = tempfile.mkstemp(prefix="aphla_arget_")
    for pv in pvs:
        os.write(fh, "%s\n" % pv)
    os.close(fh)

    t0 = float(datetime.now().strftime("%s.%f"))
    import subprocess
    tspan = ["--start", kwargs.get("start", "-24 h") ]
    if kwargs.has_key("end"):
        tspan.extend(["--end", kwargs["end"]])
    if kwargs.has_key("count"):
        tspan.extend(["--count", str(kwargs["count"])])
    out = subprocess.check_output(["arget", "--pv-list", fname, "-T", "posix"]
                                  + tspan + pvs)
    if kwargs.get("debug", 0):
        print(out)
    os.remove(fname)

    import re
    pv, dat = "", {}
    for s in out.split("\n"):
        if re.match(r"Found [0-9]+ points", s): continue
        rec = s.split()
        #if s.find("Disconnected") > 0: continue
        if not rec: continue
        # a single line PV name
        if rec[0] in pvs:
            pv = s.strip()
            dat.setdefault(pv, [])
            continue

        try:
            d0, v = rec[0], rec[1]
            #dat[pv].append((float(d0)-t0, float(v)))
            dat[pv].append((float(d0), float(v)))
        except:
            print("invalid format '{0}' for {1}".format(s, pv))
            raise
    return dict([(k, np.array(v)) for k,v in dat.items()])


def _set3CorBump(cors, dIc0, bpmins, bpmouts, **kwargs):
    """
    cors - list of three correctors
    dIc0 - the I change for the first corrector in *cors* (i.e. raw unit)
    bpmouts - bpm outside the bump
    bpmins - bpm inside the bump
    plane - 'x' or 'y' (default 'x')
    dxmax - max dI for ORM measurement, default 0.2
    orm - optional, orbit response matrix (n,3) shape.

    set the cors and returns the current change (i.e. delta I)

    returns orbit change outside bump, inside bump and current change of cors.
    if no bpmins provided, None returned for orbit change inside bump.
    """
    corls = getElements(cors)
    plane = kwargs.get("plane", 'x').lower()
    dxmax = kwargs.get("dxmax", 0.2)
    m = kwargs.get("orm", None)

    obt0 = fget(bpmouts+bpmins, plane, unitsys=None, sample=5)

    # remeasure the response matrix (n,3)
    if m is None:
        m, output = measOrbitRm([(b, plane) for b in bpmouts],
                                [(c, plane) for c in corls[1:]],
                                dxmax = dxmax, nx = 2, unitsys=None)
    print("ORM:", m)
    print("output:", output)
    bpmpvs = [b.pv(field=plane)[0] for b in bpmouts]
    corpvs = [c.pv(field=plane)[0] for c in corls[1:]]

    cv0 = fget(corls, plane, unitsys=None, handle="setpoint")
    cors[0].put(plane, cv0[0] + dIc0, unitsys=None)
    time.sleep(0.3)

    obt1 = fget(bpmouts+bpmins, plane, unitsys=None, sample=5)
    print("dx after one kick:", obt1 - obt0)
    err, msg = caRmCorrect(bpmpvs, corpvs, m)
    cv1 = fget(cors, plane, unitsys=None)
    obt2 = fget(bpmouts+bpmins, plane, unitsys=None, sample=5)
    dc = [cv1[i] - cv0[i] for i,c in enumerate(corls)]
    dxins = (obt2 - obt0)[len(bpmouts):] if bpmins else None
    dxouts = (obt2 - obt0)[:len(bpmouts)]
    return dxouts, dxins, dc


def _meas4CorBump(cors, bpmins, bpmouts, bpmdx, **kwargs):
    """
    superposition of two 3Cor bumps
    
    cors - list of correctors (4)
    bpmins - BPMs inside the bump
    bpmouts - 
    bpmdx - desired change of orbit for bpmins

    dA1 - change of one cor for ORM fitting, default 0.2
    dA2 - change of one cor for ORM fitting, default 0.2

    """
    dA1 = kwargs.pop("dA1", 0.2)
    dA2 = kwargs.pop("dA2", 0.2)
    plane = kwargs.get("plane", 'x')

    # two bpms
    if len(bpmins) != 2 or len(cors) != 4:
        raise RuntimeError("wrong number of bpms/cors, {0}/{1}".format(
                len(bpmins), len(cors)))

    xv0 = fget(bpmins, plane, unitsys=None, sample=5)
    cv0 = fget(cors, plane, unitsys=None, handle="setpoint")

    m = np.zeros((2, 2), 'd')
    dxout1, dxin1, dcls1 = set3CorBump(cors[:3], dA1, bpmins, bpmouts, **kwargs)
    fput([(cors[i], plane, cv0[i]) for i in range(len(cors))], unitsys=None)
    time.sleep(0.5)
    xv1 = fget(bpmins, plane, unitsys=None, sample=5)
    cv1 = fget(cors, plane, unitsys=None, handle="setpoint")

    dxout2, dxin2, dcls2 = set3CorBump(cors[1:], dA2, bpmins, bpmouts, **kwargs)
    fput([(cors[i], plane, cv0[i]) for i in range(len(cors))], unitsys=None)
    time.sleep(0.5)
    xv2 = fget(bpmins, plane, unitsys=None, sample=5)
    cv2 = fget(cors, plane, unitsys=None, handle="setpoint")
    
    m[:,0] = dxin1 / dA1
    m[:,1] = dxin2 / dA2

    mdet = np.linalg.det(m)
    if mdet == 0.0:
        raise RuntimeError("singular config of ({0},{1}) vs ({2},{3})".format(
                bpmins[0].name, bpmins[1].name,
                cors[0].name, cors[1].name))
    dc1 = (m[1,1]*bpmdx[0] - m[0,1]*bpmdx[1]) / mdet
    dc2 = (-m[1,0]*bpmdx[0] + m[0,0]*bpmdx[1]) / mdet
    dcs = np.zeros(4, 'd')
    for i in range(3):
        dcs[i] = dcs[i] + dcls1[i] / dA1 *dc1
        dcs[i+1] = dcs[i+1] + dcls2[i] / dA2 *dc2
    return dcs


def _setIdBump(idname, xc, thetac, **kwargs):
    """
    idname - name of ID in the middle of 4 BPMs. 2 BPMs each side.
    xc - beam position at center of ID. [mm]
    thetac - bema angle at center of ID. [mrad]
    plane - 'x' or 'y'. default 'x'.

    Hard coded Error if absolute value:
      - bpms distance > 20.0m or,
      - xc > 5mm, or
      - thetac > 1mrad

    TODO: fix the [mm], [mrad] default unit
    """
    if kwargs.get("manual", False) and (np.abs(xc) > 5.0 or np.abs(thetac) > 1.0):
        raise RuntimeError("xc or thetac overflow: {0}, {1}".format(
                xc, thetac))

    plane = kwargs.get("plane", 'x')

    nbs = getNeighbors(idname, "COR", n = 2)
    cors = [nbs[0], nbs[1], nbs[-2], nbs[-1]]
    cx0 = fget(cors, plane, unitsys=None, handle="setpoint")

    # assuming each ID has two UBPM
    bpmsact = getNeighbors(idname, "BPM", n = 1)
    if len(bpmsact) < 3:
        raise RuntimeError("can not find two bounding UBPMs "
                           "for {0}".format(idname))
    bpmsact = [bpmsact[0], bpmsact[-1]]
    allbpms = getGroupMembers(["BPM", "UBPM"], op="union")
    bpmsi, bpmso = getBoundedElements(allbpms, cors[0].sb, cors[-1].se)
    vx0 = fget(bpmsact, plane, unitsys=None)
    # sposition of bpms and ID center
    s0, s1 = [(b.se + b.sb) / 2.0 for b in bpmsact]
    sc = [(c.sb + c.se) / 2.0 for c in getElements(idname)][0]
    L = (bpmsact[-1].se + bpmsact[-1].sb) / 2.0 - \
        (bpmsact[0].se + bpmsact[0].sb) / 2.0
    if L <= 0.0 or L > 20.0:
        raise RuntimeError("ID BPM distance might be wrong: {0}".format(L))
    x0 = xc - (sc-s0)/1000.0 * thetac
    x1 = xc + (s1-sc)/1000.0 * thetac
    dvx = np.array([x0, x1], 'd') - vx0
    dcs = meas4CorBump(cors, bpmsact, bpmso, dvx)
    for i,c in enumerate(cors):
        print(i, c.name, dcs[i])
        c.put(plane, dcs[i] + cx0[i], unitsys=None)


def setIdBump(idname, xc, thetac, **kwargs):
    """
    idname - name of ID in the middle of 4 BPMs. 2 BPMs each side.
    xc - beam position at center of ID. [mm]
    thetac - bema angle at center of ID. [mrad]
    plane - 'x' or 'y'. default 'x'.
    ncor - number of correctors, default 6 each side.
    check - True/False, default True

    Hard coded Error if absolute value:
      - bpms distance > 20.0m or,
      - xc > 5mm, or
      - thetac > 1mrad

    TODO: fix the [mm], [mrad] default unit
    """
    if not kwargs.pop("manual", False) and (np.abs(xc) > 5.0 or np.abs(thetac) > 1.0):
        raise RuntimeError("xc or thetac overflow: {0}, {1}".format(
                xc, thetac))

    fld = kwargs.pop("plane", 'x')
    ncor = kwargs.pop("ncor", 6)
    dImax = kwargs.pop("dImax", 0.5)
    check = kwargs.pop("check", True)
    ignores = kwargs.pop("ignores", [])
    
    idobj = getElements(idname)[0]

    # find the correctors, 3 before ID, 3 after
    cors_ = getNeighbors(idname, "COR", n=ncor)
    cors = cors_[:ncor] + cors_[-ncor:]

    bpms_c = getNeighbors(idname, ["BPM", "UBPM"], n = 1)
    bpms_l = getNeighbors(cors[0].name, "BPM", n = ncor-1)[:ncor-1]
    bpms_r = getNeighbors(cors[-1].name, "BPM", n = ncor-1)[1-ncor:]
    bpms = bpms_l + bpms_c[:1] + bpms_c[-1:] + bpms_r

    ref = fget(bpms, fld, unitsys=None)
    b0, b1 = bpms[ncor-1], bpms[ncor]
    L = b1.sb - b0.sb
    ref[ncor-1] = xc - L*thetac/2.0
    ref[ncor] =xc + L*thetac/2.0
    norm0, norm1, norm2, corvals = \
        setLocalBump([(b.name, fld) for b in bpms
                      if (b.name, fld) not in ignores],
                     [(c.name, fld) for c in cors
                      if (c.name, fld) not in ignores],
                     ref, dImax=dImax, check=check, fullm=False, **kwargs)
    return norm0, norm1, norm2, corvals

