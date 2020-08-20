from __future__ import print_function, division, absolute_import

"""

:author: Yoshiteru Hidaka

This Python file defines classes that, on creation, perform polynomial
fitting and non-linear fitting to any user-defined function of the form
y = f(x, a, b, c, ...), for a data set of one independent variable
(x) and one dependent variable (y). The fitted results are made available
as part of attributes of the created object. The names of those attributes
are prefixed by "opt_fit_" for easy identification.


This is based on the tutorial given by Prof. Alan J. DeWeerd
of University of Redlands available at

http://bulldog2.redlands.edu/facultyfolder/deweerd/tutorials/

for curve fitting using Python.


"""

from math import sqrt
import numpy as np
from scipy.optimize import curve_fit
from inspect import getargspec


########################################################################
class Polynomial(object):
  """
  On creation of this class object, it performs a least squared polynomial
  fitting on a given data set to a polynomial of degree deg of the form
  y = p[0]*(x**deg) + p[1]*(x**(deg-1)) + ... + p[deg], for which "x" is
  an independent variable, "y" is a dependent variable, and p[0], p[1], ...
  p[deg] are fit parameters.

  This is bascially a wrapper class for the NumPy's polyfit function.
  This function adds some information about the goodness of the fit to
  the output. Namely, it calculates and returns the uncertainties in the
  fit parameters from the covariance matrix, as well as Chi square values.

  -----
  Input
  -----
  xdata : An array of length N.
  ydata : An array of length N.
  deg   : Degree of the polynomial fit
  rcond : Optional (See the explanation in numpy.polyfit)
  full  : Optional (see the explanation in numpy.polyfit) Note that if you
          set this input argument to be False, then you will not get the
          uncertaintiy estimates for the optimal fit values. By default,
          this argument is set to True, which is the opposite of NumPy's
          polyfit default value.

  ------
  Output
  ------
  self.opt_fit_param_values   : Optimal fit parameter values in 1-D NumPy array
                                of length equal to (deg+1). This 1-D array corresponds
                                to [ p[0], p[1], ..., p[deg] ].
  self.opt_fit_uncertainties  : 1-D NumPy array of length equal to (deg+1).
                                Estimated uncertainties for the corresponding optimal
                                fit parameter values. If you explicitly set the
                                input argument "full" to False, then this array will
                                contain NaN's.
  self.opt_fit_chi_sq         : Chi square value for the optimal fit
  self.opt_fit_dof            : Degrees of Freedom
  self.opt_fit_reduced_chi_sq : Reduced Chi square value for the optimal fit

  :Example:

     x = np.array([0.0, 1.0, 2.0, 3.0, 4.0, 5.0])
     y = np.array([-1.78, 4.09, 8.85, 17.9, 26.1, 35.2])
     y_stdev = np.array([0.460, 0.658, 0.528, 1.34, 1.09, 0.786])
     init_param_guess = [1.0, 3.0, -2.0]
     deg = 2
     fitObject = curve_fitting.Polynomial(x, y, deg)
     print fitObject
     yfit = np.polyval(fitObject.opt_fit_param_values, x)
     import pylab as plt
     plt.plot(x, y, 'b', x, yfit, 'r:')
  """

  #----------------------------------------------------------------------
  def __init__(self, xdata, ydata, deg, **kwargs):
    """Constructor"""

    dof = len(ydata) - (deg+1) # Degrees of Freedom
    if dof < 0 :
      raise ValueError('You need at least ' + str(nFitParams) +
                       ' data points for the specified custom fitting.')

    rcond = kwargs.get('rcond', None)
    full  = kwargs.get('full', True)

    if full :
      p, residuals, rank, singular_values, rcond = \
        np.polyfit(xdata, ydata, deg, rcond, full)

      A = np.matrix( np.vander(xdata, deg+1) )
      covariance_matrix = (A.T*A).I*float(residuals)/dof

    else :
      p = np.polyfit(xdata, ydata, deg, rcond, full)

      covariance_matrix = None


    # Calculate Chi square
    chi2 = sum( ( np.polyval(p,xdata) - ydata )**2 )

    # Calculate reduced Chi square
    if dof != 0 :
      rchi2 = chi2/dof
    else :
      rchi2 = np.NaN

    # The uncertainties are the square-root of the variances, which
    # are the diagonal elements of the covariance matrix.
    uncertainties = np.zeros(len(p))
    for ii in range(0,len(p)) :
      if covariance_matrix is not None :
        uncertainties[ii] = sqrt(covariance_matrix[ii,ii])
      else :
        uncertainties[ii] = np.NaN


    self.opt_fit_param_values = p
    self.opt_fit_uncertainties = uncertainties
    self.opt_fit_chi_sq = chi2
    self.opt_fit_dof = dof
    self.opt_fit_reduced_chi_sq = rchi2

  #----------------------------------------------------------------------
  def __str__(self):
    """"""

    nFitParams = len(self.opt_fit_param_values)

    function_str = 'Model function : y = '
    for ii in range(0,nFitParams-2) :
      function_str += ' p[' + str(ii) + ']*(x**' + str(nFitParams-ii-1) + ')'
      function_str += ' +'
    function_str += ' p[' + str(nFitParams-2) + ']*x'
    function_str += ' +'
    function_str += ' p[' + str(nFitParams-1) + ']'

    param_val_str = str(self.opt_fit_param_values)

    uncertainties_str = 'Uncertainties :               ' + \
      str(self.opt_fit_uncertainties)

    chi2_str = 'Chi-square : ' + str(self.opt_fit_chi_sq)

    dof_str = 'Deg. of Freedom : ' + str(self.opt_fit_dof)

    rchi2_str = 'Reduced Chi-square : ' + str(self.opt_fit_reduced_chi_sq)

    newline = '\n'

    output_str = function_str + newline + param_val_str + newline \
      + uncertainties_str + newline + chi2_str + newline + dof_str \
      + newline + rchi2_str

    return output_str


########################################################################
class Custom(object) :
  """
  On creation of this class object, it performs a least square fitting
  on a given data set to any user-defined function of the form y = f(x, a,
  b, c, ...), for which "x" is an independent variable, "y" is a dependent
  variable, and "a, b, c, ..." are fit parameters.

  This is bascially a wrapper class for the SciPy's curve_fit function.
  This function adds some information about the goodness of the fit to
  the output. Namely, it calculates and returns the uncertainties in the
  fit parameters from the covariance matrix, as well as Chi square values.

  -----
  Input
  -----
  func : A function object. The function must be defined by a user. It must
     return a single value. When fitting, the least square fitting function
     will assume that the first input argument of the user-specified function
     will accept the independent variable, and the rest of the input arguments
     are fit parameters.
  xdata  : An array of length N.
  ydata  : An array of length N.
  ysigma : None or an array of length N. If provided, it represents the
      standard deviation for each element of ydata. This information
      will be used as a weight in the fitting.

  ------
  Output
  ------
  self.opt_fit_param_values   : Optimal fit parameter values in 1-D NumPy array
                                of length equal to # of fit parameters. If the fit
                                function was the form y = f(x, a, b, c, ...),
                                then this 1-D array corresponds to optimal values
                                of [a, b, c, ...].
  self.opt_fit_uncertainties  : 1-D NumPy array of length equal to # of fit parameters.
                                Estimated uncertainties for the corresponding optimal
                                fit parameter values.
  self.opt_fit_chi_sq         : Chi square value for the optimal fit
  self.opt_fit_dof            : Degrees of Freedom
  self.opt_fit_reduced_chi_sq : Reduced Chi square value for the optimal fit

  -------
  Example
  -------

     x = np.array([0.0, 1.0, 2.0, 3.0, 4.0, 5.0])
     y = np.array([-1.78, 4.09, 8.85, 17.9, 26.1, 35.2])
     y_stdev = np.array([0.460, 0.658, 0.528, 1.34, 1.09, 0.786])
     init_param_guess = [1.0, 3.0, -2.0]
     def myFunction (x, a, b, c) :
           return ( a*(x**2) + b*x + c )
     fitObject = curve_fitting.Custom(myFunction, x, y)
     print fitObject
     yfit = myFunction(x, *fitObject.opt_fit_param_values)
     import pylab as plt
     plt.plot(x, y, 'b', x, yfit, 'r:')

  """

  #----------------------------------------------------------------------
  def __init__(self, func, xdata, ydata, p0 = None, sigma = None, **kwargs):
    """Constructor"""

    argspec = getargspec(func)
    nFitParams = len(argspec.args) - 1

    dof = len(ydata) - nFitParams # Degrees of Freedom

    if dof < 0 :
      raise ValueError('You need at least ' + str(nFitParams) +
                       ' data points for the specified custom fitting.')

    popt, pcov = curve_fit(func, xdata, ydata, p0, sigma, **kwargs)

    # Calculate Chi square
    if sigma is None :
        chi2 = sum( ( func(xdata,*popt) - ydata )**2 )
    else :
        chi2 = sum( ( ( func(xdata,*popt) - ydata )/sigma )**2 )

    # Calculate reduced Chi square
    if dof != 0 :
      rchi2 = chi2/dof
    else :
      rchi2 = np.NaN

    # The uncertainties are the square-root of the variances, which
    # are the diagonal elements of the covariance matrix returned
    # by the SciPy's curve_fit function.
    uncertainties = np.zeros(len(popt))
    for ii in range(len(popt)) :
      if isinstance(pcov, float) : # When fitting fails, pcov is Inf (float), instead of numpy.ndarray
        uncertainties[ii] = np.Inf
      else :
        uncertainties[ii] = sqrt(pcov[ii,ii])

    self.opt_fit_param_values = popt
    self.opt_fit_uncertainties = uncertainties
    self.opt_fit_chi_sq = chi2
    self.opt_fit_dof = dof
    self.opt_fit_reduced_chi_sq = rchi2


  #----------------------------------------------------------------------
  def __str__(self):
    """"""

    param_val_str = 'Optimal fit parameter values :' + \
      str(self.opt_fit_param_values)

    uncertainties_str = 'Uncertainties :               ' + \
      str(self.opt_fit_uncertainties)

    chi2_str = 'Chi-square : ' + str(self.opt_fit_chi_sq)

    dof_str = 'Deg. of Freedom : ' + str(self.opt_fit_dof)

    rchi2_str = 'Reduced Chi-square : ' + str(self.opt_fit_reduced_chi_sq)

    newline = '\n'

    output_str = param_val_str + newline + uncertainties_str + newline \
      + chi2_str + newline + dof_str + newline + rchi2_str

    return output_str


########################################################################
class WeightedPolynomial:
  """
  Not Implemented
  """

  #----------------------------------------------------------------------
  def __init__(self):
    """Constructor"""
    pass








