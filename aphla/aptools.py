"""
:author: Lingyun Yang <lyyang@bnl.gov>
:license:

Accelerator Physics Tools module defines some small AP routines.

"""

from __future__ import print_function

import numpy as np
import time, datetime, sys
import itertools

from . import machines
from catools import caRmCorrect 
from hlalib import (getCurrent, getExactElement, getElements, getNeighbors,
    getClosest, getRfFrequency, putRfFrequency, getTunes, getOrbit,
    getLocations)
from orm import Orm
import logging

__all__ = [ 'calcLifetime', 
    'getLifetime',  'measOrbitRm',
    'correctOrbit', 'setLocalBump',
    'saveImage', 'fitGaussian1', 'fitGaussianImage'
]

logger = logging.getLogger(__name__)

def _zip_element_field(elems, fields, **kwargs):
    """
    * compress=True
    >>> _element_fields(getElements(['BPM1']), ['x', 'y'])
    
    returns a flat list of (name, field)
    """
    compress = kwargs.get('compress', True)
    ret = []
    for b,f in itertools.product(elems, fields):
        if f in b.fields():
            ret.append((b.name, f))
        elif not compress:
            ret.append((b.name, None))
    return ret

def getLifetime(tinterval=3, npoints = 8, verbose=False):
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
    d0 = datetime.datetime.now()
    ret[0, 1] = getCurrent()
    for i in range(1, npoints):
        # sleep for next reading
        time.sleep(tinterval)
        ret[i, 1] = getCurrent()
        dt = datetime.datetime.now() - d0
        ret[i, 0] = (dt.microseconds/1000000.0 + dt.seconds)/3600.0 + \
            dt.days*24.0
        if verbose:
            print(i, dt, ret[i, 1])
    dI = max(ret[:, 1]) - min(ret[:, 1]) 
    dt = max(ret[:, 0]) - min(ret[:, 0])
    lft_hour = np.average(ret[:, 1]) / (dI / dt)
    return lft_hour


def setLocalBump(bpm, trim, ref, **kwargs):
    """
    create a local bump at certain BPM, while keep all other orbit untouched
    
    Parameters
    -----------
    bpm: list of BPMs objects for new bumpped orbit. 
    trim: list of corrector objects used for orbit correction. 
    ref: target orbit with shape (len(bpm),2), e.g. [[0, 0], [0, 0], [0, 0]]
    scale: optional, float
        factor to scale calculated kick strength change, between 0 and 1.0
    check: optional, bool
        roll back the corrector settings if the orbit gets worse.
    ormdata: optional, :class:`~aphla.apdata.OrmData`
        use provided OrmData instead of the system default.

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

    ormdata = kwargs.pop('ormdata', None)
    repeat = kwargs.pop('repeat', 1)

    if ormdata is None: ormdata = machines._lat.ormdata
    
    if ormdata is None:
        raise RuntimeError("No Orbit Response Matrix available for '%s'" %
            machines._lat.name)

    # get the matrix and (bpm, field), (trim, field) list as OrmData required
    bpmrec = _zip_element_field(bpm, ['x', 'y'])
    trimrec = _zip_element_field(bpm, ['x', 'y'])
    m, bpmrec, trimrec = ormdata.getMatrix(bpmrec, trimrec, full=True)

    bpmref = []
    for name,field in bpmrec:
        try:
            # find the index of first matching BPM
            i = (i for i,b in enumerate(bpm) if b.name == name).next()
        except:
            v0 = getExactElement(name).get(field, unitsys=None)
            u1 = getExactElement(name).getUnit(field, unitsys=None)
        else:
            if field == 'x': 
                # v0 [m], u1 is lower level unit (EPICS)
                v0, u1 = ref[i][0], bpm[i].getUnit('x', unitsys=None)
            elif field == 'y': 
                v0, u1 = ref[i][1], bpm[i].getUnit('y', unitsys=None)
            else:
                raise RuntimeError("unknow field %s" % field)

        if u1 == 'm': v = v0
        elif u1 == 'mm': v = 1000.0*v0
        elif u1 == 'um': v = 1.0e6*v0
        else: raise RuntimeError("unknow unit '%s'" % u1)

        bpmref.append(v)

    bpmpvs = [getExactElement(b).pv(field=f)[0] for b,f in bpmrec]
    trimpvs = [getExactElement(t).pv(field=f, handle='setpoint')[0] 
               for t,f in trimrec]

    # correct orbit using default ORM (from current lattice)
    for i in range(repeat):
        #for k,b in enumerate(bpmpvs):
        #    if bpmref[k] != 0.0: print(k, bpmlst[k], b, bpmref[k])
        caRmCorrect(bpmpvs, trimpvs, m, ref=np.array(bpmref), **kwargs)


def correctOrbit(bpmlst = None, trimlst = None, **kwargs):
    """
    correct the orbit with given BPMs and Trims

    Parameters
    -----------
    bpm: list of BPM objects, default all 'BPM'
    trimlst: list of Trim objects, default all 'COR'
    plane: optional, [ 'HV' | 'H' | 'V' ], default 'HV'
    repeat: optional, integer, default 1
        numbers of correction 

    Notes
    -----
    This routine prepares the target orbit and then calls :func:`setLocalBump`.

    seealso :func:`~aphla.hlalib.getElements`, :func:`~aphla.getSubOrm`,
    :func:`setLocalBump`.

    Examples
    --------
    >>> bpms = getElements(['BPM1', 'BPM2'])
    >>> trims = getElements(['T1', 'T2', 'T3'])
    >>> correctOrbit(bpms, trims) 
    """

    plane = kwargs.pop('plane', 'HV')

    # an orbit based these bpm
    if bpmlst is None:
        bpmlst = getElements('BPM')

    N = len(bpmlst)
    if plane == 'H': ref = zip([0.0] * N, [None] * N)
    elif plane == 'V': ref = zip([None] * N, [0.0] * N)
    else: ref = zip([0.0]*N, [0.0]*N)
    
    # pv for trim
    if trimlst is None:
        trimlst = getElements('COR')

    setLocalBump(bpmlst, trimlst, ref, **kwargs)

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
    d = elem.get(field)
    width = kwargs.get('width', elem.get(field + "_nx"))
    height = kwargs.get('height', elem.get(field + "_ny"))
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
        ax.imshow(d2, interpolation="nearest", cmap=plt.cm.bwr)
        ax.set_xlim(xlim)
        ax.set_ylim(ylim)
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

def measChromRm(sextlst):
    """
    measure chromaticity response matrix for sextupoles
    
    seealso :func:`~aphla.hlalib.getTunes`

    :warn: NotImplemented
    """
    raise NotImplementedError()

#
def measOrbitRm(bpm, trim, output, **kwargs):
    """
    Measure the orbit response matrix

    :param list bpm: list of bpm names
    :param list trim: list of trim names
    :param str output: output filename
    :param float minwait: waiting seconds before each orbit measurement.

    seealso :class:`~aphla.orm.Orm`, :func:`~aphla.orm.Orm.measure`
    """

    logger.info("Orbit RM shape (%d %d)" % (len(bpm), len(trim)))
    orm = Orm(bpm, trim)
    orm.minwait = kwargs.get('minwait', 3)

    orm.measure(output = output, **kwargs)

    return orm


def getSubOrm(bpm, trim, flags = 'XX'):
    """
    get submatrix of Orm

    :warn: NotImplemented
    """
    #return _orm.getSubMatrix(bpm, trim, flags)
    raise NotImplementedError()


