#!/usr/bin/env python

"""
    hla.current
    ~~~~~~~~~~~~~~~~

    Beam current related routines

    :author: Lingyun Yang
    :license: (empty ? GPL ? EPICS ?)

"""

#from cothread.catools import caget, caput
import numpy as np
import datetime, time
from catools import caget, caput


#----------------------------------------------------------------------
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
    
    if isinstance(t, (float,int)) :
        t = np.array([t])
    elif isinstance(t, list) :
        t = np.array(t)
    elif isinstance(t, np.ndarray) :
        pass
    else :
        raise ValueError('The time input argument must be either ',
                         'float, int, or list of (int,float), or NumPy array.')
    
        
    if isinstance(I, (float,int)) :
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
            print 'The final subdivision does not contain enough data points ' \
                  + 'for lifetime estimation. So, it is ignored.'
        
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
            print 'The final subdivision does not contain enough data points ' \
                  + 'for lifetime estimation. So, it is ignored.'
        
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