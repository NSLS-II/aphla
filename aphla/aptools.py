#!/usr/bin/env python


"""
Accelerator Physics Tools
~~~~~~~~~~~~~~~~~~~~~~~~~~

:author: Lingyun Yang

Accelerator Physics Tools

"""

from __future__ import print_function

import numpy as np
import time, datetime, sys
#import matplotlib.pylab as plt

from . import machines
from catools import caput, caget 
from hlalib import (getCurrent, getElements, getNeighbors, getClosest,
                    getRfFrequency, putRfFrequency, getTunes, getOrbit,
                    getLocations)
#from bba import BbaBowtie
import logging

__all__ = [
    'getLifetime',  
    'correctOrbit', 'createLocalBump', 'setLocalBump',
    'saveImage', 'fitGaussian1', 'fitGaussianImage'
]

logger = logging.getLogger(__name__)

def getLifetime(tinterval=3, npoints = 8, verbose=False):
    """
    Monitor current change with, calculate lifetime dI/dt

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



# def measDispersion(gamma = 3.0e3/.511, alphac = 3.6261976841792413e-04,
#                    df = 1e-4, numpoints=5):
#     """
#     Measure the dispersion
#     """

#     eta = alphac - 1/gamma/gamma

#     #bpm = getElements('P*C0[3-6]*')
#     bpm = getElements('P*')
#     #print gamma, bpm
#     s1 = getLocations(bpm)
#     #eta0 = getDispersion(bpm)
    
#     # f in MHz
#     f0 = getRfFrequency()
#     f = np.linspace(f0 - abs(df), f0 + abs(df), numpoints)

#     # avoid a bug in virtac
#     obt = getOrbit(bpm)
#     x0 = np.array([v[0] for v in obt])
#     y0 = np.array([v[1] for v in obt])
#     time.sleep(4)

#     codx = np.zeros((len(f), len(bpm)), 'd')
#     cody = np.zeros((len(f), len(bpm)), 'd')

#     for i,f1 in enumerate(f): 
#         putRfFrequency(f1)
#         time.sleep(6)
#         obt = np.array(getOrbit(bpm))
#         x1, y1 = obt[:,0], obt[:,1] 

#         putRfFrequency(f1)
#         time.sleep(6)
#         obt = np.array(getOrbit(bpm))
#         x2, y2  = obt[:,0], obt[:,1]
#         #print(i, getRfFrequency(), x1[0], x2[0], x1[2], x2[2])
#         codx[i,:] = x2[:]
#         cody[i,:] = y2[:]

#     putRfFrequency(f0)

#     #plt.clf()
#     #for i in range(len(bpm)):
#     #    plt.plot(f, codx[:,i], 'o-')
#     #plt.savefig('test-cod.png')

#     codx0 = np.zeros(np.shape(codx), 'd')
#     for i in range(len(f)):
#         codx0[i,:] = x0[:]
#     dxc = codx - codx0
#     df = -(f - f0)/f0/eta
#     #print(df)
#     #print(dxc)
#     # p[0,len(bpm)]
#     p = np.polyfit(df, dxc, 1)
#     #print("first order:", p[0,:])
#     t = np.linspace(df[0], df[-1], 20)
#     #plt.clf()
#     #for i in range(len(bpm)):
#     #    plt.plot(df, dxc[:,i], 'o')
#     #    plt.plot(t, p[0,i]*t + p[1,i], '--')
#     #plt.savefig('test-disp.png')


#     #print(eta, f0)
#     #plt.clf()
#     #plt.plot(s1, eta0[:,0], 'x-', label="Twiss Calc")
#     #plt.plot(s1, p[0,:], 'o--', label="Fit")
#     #plt.legend()
#     #plt.savefig('test.png')

#     #dat = [(bpm[i], s1[i], p[0,i], eta0[i,0]) for i in range(len(bpm))]
#     #f = shelve.open("dispersion.pkl", 'c')
#     #f["dispersion"] = dat
#     #f.close()
    
#     return s1, p[0,:]


def _correctOrbitPv(bpm, trim, m, **kwarg):
    """
    correct orbit use direct pv and catools

    - the input bpm and trim should be uniq in pv names.
    - ormdata a valid OrmData object
    - scale factor for calculated dx
    - ref reference orbit
    - check stop if the orbit gets worse.
    """
    scale = kwarg.get('scale', 0.68)
    ref = kwarg.get('ref', None)
    check = kwarg.get('check', True)

    verbose = kwarg.get('verbose', 1)

    #if ormdata is not None:
    #    print("BPM PV:", bpm)
    #    print("Trim PV:", trim)
    #    m = ormdata.getSubMatrixPv(bpm, trim)
    #elif machines._lat.ormdata is not None:
    #    m = machines._lat.ormdata.getSubMatrixPv(bpm, trim)
    #else:
    #    raise RuntimeError("no ORM data defined from orbit correction")

    v0 = np.array(caget(bpm), 'd')
    if ref is not None: v0 = v0 - ref
    
    # the initial norm
    norm0 = np.linalg.norm(v0)

    # solve for m*dk + (v0 - ref) = 0
    dk, resids, rank, s = np.linalg.lstsq(m, -1.0*v0, rcond = 1e-4)

    norm1 = np.linalg.norm(m.dot(dk*scale) + v0)
    k0 = np.array(caget(trim), 'd')
    caput(trim, k0+dk*scale)

    # wait and check
    if check == True:
        time.sleep(5)
        v1 = np.array(caget(bpm), 'd')
        if ref is not None: v1 = v1 - np.array(ref)
        norm2 = np.linalg.norm(v1)
        print("Euclidian norm: predicted/realized", norm1/norm0, norm2/norm0)
        if norm2 > norm0:
            print("Failed to reduce orbit distortion, restoring...", 
                  norm0, norm2)
            caput(trim, k0)
            return False
        else:
            return True
    else:
        return None

    
def createLocalBump(bpm, trim, ref, **kwargs):
    """
    this is not a good name, use :func:`setLocalBump` instead.
    """
    import warning
    warning.warn("will be deprecated, use setLocalBump instead", 
                 PendingDeprecationWarning)

    setLocalBump(bpm, trim, ref, **kwargs)

    
def setLocalBump(bpm, trim, ref, **kwargs):
    """
    create a local bump at certain BPM, while keep all other orbit untouched
    
    :param bpm: BPMs for new bumpped orbit. 
    :type bpm: str, list
    :param trim: correctors used for orbit correction. 
    :type trim: str, list
    :param ref: target orbit, (len(bpm),2)
    :type ref: matrix shape (n,2).
    :param scale: factor for calculated kick strength change, between 0 and 1.0
    :param check: ignore if the orbit gets worse

    `bpm` and `trim` can be a pattern, a group name, a list of exact element
    names or a list of objects. if `ref[i][j]` is `None`, use the current
    hardware result, i.e. try not to change the orbit at that location.

    :Examples:

        >>> bpms = [b.name for b in getGroupMembers(['BPM', 'C02'])]
        >>> newobt = [[1.0, 1.5]] * len(bpms)
        >>> createLocalBump(bpms, 'HCOR', newobt)

    """
    ormdata = kwargs.get('ormdata', None)
    repeat = kwargs.get('repeat', 1)

    if ormdata is None: ormdata = machines._lat.ormdata
    
    if ormdata is None:
        raise RuntimeError("No Orbit Response Matrix available")

    bpmfulllst = getElements(ormdata.getBpmNames())
    bpmlst, trimlst = getElements(bpm), getElements(trim)
    bpmnames = [b.name for b in bpmlst]

    for i,b in enumerate(bpmlst):
        if not ormdata.hasBpm(b.name):
            raise RuntimeError("No BPM '%s' found in the ORM data" % (b.name))
    
    bpmrec, trimrec = [], []
    for i,b in enumerate(bpmfulllst):
        # if the bpm is in the list, set the target orbit, otherwise use None
        if b.name in bpmnames:
            obtx, obty = ref[bpmnames.index(b.name)]
        else:
            obtx, obty = None, None
        ix, iy = ormdata.index(b.name, ['x', 'y'])
        if ix is not None: bpmrec.append((ix, obtx))
        if iy is not None: bpmrec.append((iy, obty))

    for i,t in enumerate(trimlst):
        if not ormdata.hasTrim(t.name):
            raise RuntimeError("No Trim '%s' found in the ORM data" % (t.name))
        ix, iy = ormdata.index(t.name, ['x', 'y'])
        if ix is not None: trimrec.append((ix,))
        if iy is not None: trimrec.append((iy,))


    # now mv to PV Group read/write
    # expand the PV and ref in 1D array: [x y]
    bpmpvs  = [ormdata.bpm[r[0]][-1] for r in bpmrec]
    trimpvs = [ormdata.trim[r[0]][-1] for r in trimrec]
    bpmref  = []
    for i,r in enumerate(bpmrec):
        if r[1] is None: bpmref.append(caget(bpmpvs[i]))
        else: bpmref.append(r[1])

    # bpm
    #print("ORM dimension", np.shape(ormdata.m), type(ormdata.m))
    #print("  {0}".format([r[0] for r in bpmrec]))
    #print("  {0}".format(np.take(ormdata.m, [r[0] for r in bpmrec])))

    m = np.take(np.take(ormdata.m, [r[0] for r in bpmrec], axis=0), 
                [r[0] for r in trimrec], axis=1)

    # test
    for i in range(len(bpmpvs)):
        logging.debug("{0} {1} val= {2} target={3}".format(
                i, bpmpvs[i], caget(bpmpvs[i]), bpmref[i]))

    # correct orbit using default ORM (from current lattice)
    for i in range(repeat):
        _correctOrbitPv(bpmpvs, trimpvs, m, ref=np.array(bpmref), **kwargs)

        
def correctOrbit(bpm = None, trim = None, **kwargs):
    """
    correct the orbit with given BPMs and Trims

    :param plane: [HV|H|V]
    :param repeat: numbers of correction 

    :Example:

        >>> correctOrbit(['BPM1', 'BPM2'], ['T1', 'T2', 'T3'])

    The orbit not in BPM list may change.

    seealso :func:`~aphla.hlalib.getElements`, :func:`~aphla.getSubOrm`
    """

    plane = kwargs.get('plane', 'HV')

    # an orbit based these bpm
    if bpm is None:
        bpmlst = getElements('BPM')
    else:
        bpmlst = getElements(bpm)

    if plane == 'H': ref = zip([0.0] * len(bpmlst), [None] * len(bpmlst))
    elif plane == 'V': ref = zip([None] * len(bpmlst), [0.0] * len(bpmlst))
    else: ref = np.zeros((len(bpmlst), 2), 'd')

    # pv for trim
    if trim is None:
        trimlst = getElements('HCOR') + getElements('VCOR')
    else:
        trimlst = getElements(trim)

    setLocalBump([b.name for b in bpmlst], trimlst, ref, **kwargs)

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
    """
    :author: Yoshiteru Hidaka
    
    This function returns beam lifetime array or scalar value with
    different data subdivision and calculation methods, given arrays
    of time (t) in hours and beam current (I) in whatever unit.
    
    subNPoints is only used if data_subdiv_method = 'SubdivEqualNPoints'
    
    subDurationSeconds is only used if data_subdiv_method = 'SubdivEqualSeconds'
    
    **kwargs can contain optional parameters "p0" (initial guess for
    the fit parameters) and "sigma" (weight factors) for
    scipy.optimize.curve_fit.
    
    data_subdiv_method = {
        'NoSubdiv' :
             The function will apply the specified lifetime calculation
             method on the entire time and beam current data. Hence, only
             a single value of lifetime will be returned. The time corresponding
             for the single lifetime value is calculated as (t_start + t_end)/2,
             and will be returned along with the lifetime value.

        'SubdivEqualNPoints' :
             The function will first subdivide the given time and beam current
             data into a data subset with an equal number of data points specified
             by the optional input arument "subNPoints".
             For each data subset, the specified lifetime calculation method will
             be applied. Hence, a vector of lifetime values will be returned.
             The corresponding time vector is calculated using the same method
             as in 'NoSubdiv', applied for each data subset. This time vector
             will be returned along with the lifetime vector.
             
        'SubdivEqualSeconds' :
             This is similar to 'SubdivEqualNPoints', but the subdivision
             occurs based on an equal time period in seconds specified by
             the optional input argument "subDurationSeconds".
             
        }
        
    calc_method = {
        'expDecayFit' :
             The function will estimate the lifetime "tau" [hr] by fitting a
             data set of time (t) and current (I) to the exponential decay
             equation:
             
                        I(t) = I_0 * exp( - t / tau )
                        
        'avg_I_over_MaxDropRate' :
             The function will estimate the lifetime value by dividing the
             average beam current over the given data set by the maximum
             current drop rate ( = Delta_I / Delta_t). The average current
             is given by calculating the mean of the beam current vector in
             the data set. The maximum current drop rate is defined as
             (I_max - I_min) divided by (t_end - t_start).
             
        'avg_I_over_LinearFitDropRate' :
             The function will estimate the lifetime value by dividing the
             average beam current over the given data set by the linearly
             fit current drop rate ( = dI/dt). The average current is given
             by calculating the mean of the beam current vector in the data
             set. The current drop rate is given by the slope of the best
             line fit to the data set.
        }
    
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

