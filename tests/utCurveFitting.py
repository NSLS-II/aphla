#! /usr/bin/env python

DEBUG = True
if DEBUG:
    import os, sys
    abs_file_path = '/home/yoshiteru/Desktop/HLA/working_source_dir/hla/src/hla'
    abs_folder_path = os.path.dirname(abs_file_path)
    if abs_folder_path not in sys.path :
        sys.path.insert(0, abs_folder_path) # Inser the folder path as the 1st search directory.
        # This will allow you to force Python to use your (development) modules
        # instead of the ones installed on the system.
        
import unittest

import pylab as plt
import numpy as np
import hla.curve_fitting as curve_fitting

########################################################################
class TestCurveFitting(unittest.TestCase):
    """"""
            
    #----------------------------------------------------------------------
    def setUp(self):
        self.x = np.array([0.0, 1.0, 2.0, 3.0, 4.0, 5.0])
                        
        self.y = np.array([-1.78, 4.09, 8.85, 17.9, 26.1, 35.2])
     
        self.y_stdev = np.array([0.460, 0.658, 0.528, 1.34, 1.09, 0.786])
     
        self.init_param_guess = [1.0, 3.0, -2.0]
        
        self.decimal_places = 7
        
        
    #----------------------------------------------------------------------
    def test_Polynomial(self):
        """"""
        
        print '\n### Fitting based on numpy.polyfit ###'

        deg = 2
                        
        fitObject_poly = curve_fitting.Polynomial(self.x, self.y, deg)
     
        print fitObject_poly
        
        p = fitObject_poly.opt_fit_param_values
        self.assertAlmostEqual(p[0],  0.53410714, places = self.decimal_places)
        self.assertAlmostEqual(p[1],  4.75746429, places = self.decimal_places)
        self.assertAlmostEqual(p[2], -1.72964286, places = self.decimal_places)
        
        u = fitObject_poly.opt_fit_uncertainties
        self.assertAlmostEqual(u[0], 0.12822913, places = self.decimal_places)
        self.assertAlmostEqual(u[1], 0.66794127, places = self.decimal_places)
        self.assertAlmostEqual(u[2], 0.71010078, places = self.decimal_places)
        
        self.assertAlmostEqual(fitObject_poly.opt_fit_chi_sq,
                               1.84158357, places = self.decimal_places)
        self.assertEqual(fitObject_poly.opt_fit_dof, 3)
        self.assertAlmostEqual(fitObject_poly.opt_fit_reduced_chi_sq,
                               0.61386119, places = self.decimal_places)
        
     
        yfit_poly = np.polyval(fitObject_poly.opt_fit_param_values, self.x)

        self.yfit_poly = yfit_poly
        
        
    #----------------------------------------------------------------------
    def test_Custom(self):
        """"""
        
        print '\n### Fitting based on scipy.optimize.curve_fit ###'
        
        def polyDeg2 (x, a, b, c) :
            return ( a*(x**2) + b*x + c )
           
        fitObject_custom = curve_fitting.Custom(polyDeg2, self.x, self.y)
     
        print fitObject_custom
        
        p = fitObject_custom.opt_fit_param_values
        self.assertAlmostEqual(p[0],  0.53410714, places = self.decimal_places)
        self.assertAlmostEqual(p[1],  4.75746429, places = self.decimal_places)
        self.assertAlmostEqual(p[2], -1.72964286, places = self.decimal_places)
        
        u = fitObject_custom.opt_fit_uncertainties
        self.assertAlmostEqual(u[0], 0.12822913, places = self.decimal_places)
        self.assertAlmostEqual(u[1], 0.66794127, places = self.decimal_places)
        self.assertAlmostEqual(u[2], 0.71010078, places = self.decimal_places)
        
        self.assertAlmostEqual(fitObject_custom.opt_fit_chi_sq,
                               1.84158357, places = self.decimal_places)
        self.assertEqual(fitObject_custom.opt_fit_dof, 3)
        self.assertAlmostEqual(fitObject_custom.opt_fit_reduced_chi_sq,
                               0.61386119, places = self.decimal_places)
        
        yfit_custom = polyDeg2(self.x, *fitObject_custom.opt_fit_param_values)
    
        self.yfit_custom = yfit_custom
        
        '''
        plt.clf()
        plt.plot(self.x, self.y, 'b', 
                 self.x, self.yfit_poly, 'r:', 
                 self.x, self.yfit_custom, 'g-.')
        plt.legend( ('Data', 'Fit by polyfit', 'Fit by curve_fit') )
        plt.show()
        '''

if __name__ == "__main__" :
    unittest.main()
    