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
import hla
import hla.curve_fitting as curve_fitting
import cPickle
import zlib
import time

#----------------------------------------------------------------------
def plot_results(t_hr, I_mA, avg_t_hr, lifetime_hr, lifetime_error = None,
                 show_plot = False):
    """"""
    
    # Set show_plot to True to stop the code here for examining the plot
    if show_plot:
        fig = plt.figure()
            
        ax1 = fig.add_subplot(111)
        h1 = ax1.plot(t_hr, I_mA, '.-', label='Data', linewidth=0.5)
        ax1.set_xlabel('Time [hr]')
        ax1.set_ylabel('Beam Current [mA]')
            
        ax2 = ax1.twinx()
        
        if lifetime_error is not None :
            h2 = ax2.errorbar(avg_t_hr, lifetime_hr,
                              yerr = lifetime_error,
                              fmt = '-', ecolor = 'r',
                              color = 'r', linestyle = '-', marker = '.', 
                              label = 'Lifetime')
        else :
            h2 = ax2.plot(avg_t_hr, lifetime_hr,
                          color = 'r', linestyle = '-', marker = '.',
                          label = 'Lifetime')
            
        ax2.set_ylabel('Lifetime [hr]')
            
        plt.figlegend( (h1[0], h2[0]), 
                       (h1[0].get_label(), h2[0].get_label()), 
                       loc='upper right')

        plt.show()  
            
########################################################################
class TestLT_MaxDropRate(unittest.TestCase):
    """
    Testing lifetime estimate functionality based on max current drop rate
    """

    #----------------------------------------------------------------------
    def setUp(self):
        
        tStart = time.time()
        
        compressed_str = cPickle.load(open('sample_beam_current_data.pkl', 'rb'))
        decompressed_str = zlib.decompress(compressed_str)
        beam_history_data = cPickle.loads(decompressed_str)
        
        self.t_hr = beam_history_data['t_hr']
        self.I_mA = beam_history_data['I_mA']
        
        print 'Elapsed time for setUp is %.4g seconds' % (time.time()-tStart)

    #----------------------------------------------------------------------
    def testSubdivEqualNPoints_maxDropRate(self):
        """
        Test 'SubdivEqualNPoints" option with other default arguments,
        using max drop rate estimates.
        """
        
        tStart = time.time()
        
        print '\n ##### ' + self._testMethodName + ' #####'

        result = hla.current.calcLifetime(
            self.t_hr, self.I_mA, 
            data_subdiv_method = 'SubdivEqualNPoints',
            calc_method = 'avg_I_over_MaxDropRate')
        
        plot_results(self.t_hr, self.I_mA, 
                     result["avg_time_hr_array"], result["lifetime_hr_list"],
                     show_plot = False)
        
        print 'Elapsed time is %.4g seconds' % (time.time()-tStart)
     
     
     #----------------------------------------------------------------------
    def testSubdivEqualNPoints100_maxDropRate(self):
        """
        Test 'SubdivEqualNPoints" option with each subdivision of 100 data points
        for lifetime estimation, using max drop rate estimates.
        """
        
        tStart = time.time()
        
        print '\n ##### ' + self._testMethodName + ' #####'

        result = hla.current.calcLifetime(
            self.t_hr, self.I_mA, 
            data_subdiv_method = 'SubdivEqualNPoints',
            subNPoints = 100,
            calc_method = 'avg_I_over_MaxDropRate')
        
        
        self.assertEqual(len(result["lifetime_hr_list"]), 171)
        print 'Lifetime has been estimated for ' + \
              str(len(result["lifetime_hr_list"])) + ' points.'
        
        plot_results(self.t_hr, self.I_mA, 
                     result["avg_time_hr_array"], result["lifetime_hr_list"],
                     show_plot = False)

        print 'Elapsed time is %.4g seconds' % (time.time()-tStart)
    
    #----------------------------------------------------------------------
    def testSubdivEqualNPoints101_maxDropRate(self):
        """
        Test 'SubdivEqualNPoints" option with each subdivision of 101 data points
        for lifetime estimation. Check if the final subdivision which
        contains only 1 data points will be removed from the data set
        since that final subdivision does not have enough data points to
        estimate the lifetime from. Using max drop rate estimates.
        """
        
        tStart = time.time()

        print '\n ##### ' + self._testMethodName + ' #####'
        
        result = hla.current.calcLifetime(
            self.t_hr, self.I_mA, 
            data_subdiv_method = 'SubdivEqualNPoints',
            subNPoints = 101,
            calc_method = 'avg_I_over_MaxDropRate')
        
        self.assertEqual(len(result["lifetime_hr_list"]), 169)
        print 'Lifetime has been estimated for ' + \
              str(len(result["lifetime_hr_list"])) + ' points.'
        
        plot_results(self.t_hr, self.I_mA, 
                     result["avg_time_hr_array"], result["lifetime_hr_list"],
                     show_plot = False) 

        print 'Elapsed time is %.4g seconds' % (time.time()-tStart)
     
     
     #----------------------------------------------------------------------
    def testSubdivEqualSeconds_maxDropRate(self):
        """
        Test 'SubdivEqualSeconds" option with other default arguments,
        using max drop rate estimates.
        """
        
        tStart = time.time()
        
        print '\n ##### ' + self._testMethodName + ' #####'

        result = hla.current.calcLifetime(
            self.t_hr, self.I_mA,
            data_subdiv_method = 'SubdivEqualSeconds',
            calc_method = 'avg_I_over_MaxDropRate')
        
        plot_results(self.t_hr, self.I_mA, 
                     result["avg_time_hr_array"], result["lifetime_hr_list"],
                     show_plot = False) 

        print 'Elapsed time is %.4g seconds' % (time.time()-tStart)
        
    #----------------------------------------------------------------------
    def testSubdivEqualSeconds100_maxDropRate(self):
        """
        Test 'SubdivEqualSeconds" option with each subdivision of 100-sec
        duration for lifetime estimation. Using max drop rate estimates.
        """
        
        tStart = time.time()
        
        print '\n ##### ' + self._testMethodName + ' #####'

        result = hla.current.calcLifetime(
            self.t_hr, self.I_mA,
            data_subdiv_method = 'SubdivEqualSeconds',
            subDurationSeconds = 100,
            calc_method = 'avg_I_over_MaxDropRate')
        
        
        self.assertEqual(len(result["lifetime_hr_list"]), 177)
        print 'Lifetime has been estimated for ' + \
              str(len(result["lifetime_hr_list"])) + ' points.'
        
        plot_results(self.t_hr, self.I_mA, 
                     result["avg_time_hr_array"], result["lifetime_hr_list"],
                     show_plot = False) 
        
        print 'Elapsed time is %.4g seconds' % (time.time()-tStart) 
        
        

########################################################################
class TestLT_LinFitDropRate(unittest.TestCase):
    """
    Testing lifetime estimate functionality based on linear-fit current
    drop rate
    """

    #----------------------------------------------------------------------
    def setUp(self):
        
        tStart = time.time()
        
        compressed_str = cPickle.load(open('sample_beam_current_data.pkl', 'rb'))
        decompressed_str = zlib.decompress(compressed_str)
        beam_history_data = cPickle.loads(decompressed_str)
        
        self.t_hr = beam_history_data['t_hr']
        self.I_mA = beam_history_data['I_mA']
        
        print 'Elapsed time for setUp is %.4g seconds' % (time.time()-tStart)

    #----------------------------------------------------------------------
    def testSubdivEqualNPoints_linFitDropRate(self):
        """
        Test 'SubdivEqualNPoints" option with other default arguments,
        using linear-fit drop rate estimates.
        """
        
        tStart = time.time()
        
        print '\n ##### ' + self._testMethodName + ' #####'

        result = hla.current.calcLifetime(
            self.t_hr, self.I_mA, 
            data_subdiv_method = 'SubdivEqualNPoints',
            calc_method = 'avg_I_over_LinearFitDropRate')
        
        plot_results(self.t_hr, self.I_mA, 
                     result["avg_time_hr_array"], result["lifetime_hr_list"],
                     lifetime_error = result["lifetime_hr_error_list"],
                     show_plot = False)
        
        print 'Elapsed time is %.4g seconds' % (time.time()-tStart)
     
     
     #----------------------------------------------------------------------
    def testSubdivEqualNPoints100_linFitDropRate(self):
        """
        Test 'SubdivEqualNPoints" option with each subdivision of 100 data points
        for lifetime estimation, using linear-fit drop rate estimates.
        """
        
        tStart = time.time()
        
        print '\n ##### ' + self._testMethodName + ' #####'

        result = hla.current.calcLifetime(
            self.t_hr, self.I_mA, 
            data_subdiv_method = 'SubdivEqualNPoints',
            subNPoints = 100,
            calc_method = 'avg_I_over_LinearFitDropRate')
        
        
        self.assertEqual(len(result["lifetime_hr_list"]), 171)
        print 'Lifetime has been estimated for ' + \
              str(len(result["lifetime_hr_list"])) + ' points.'
        
        plot_results(self.t_hr, self.I_mA, 
                     result["avg_time_hr_array"], result["lifetime_hr_list"],
                     lifetime_error = result["lifetime_hr_error_list"],
                     show_plot = False)

        print 'Elapsed time is %.4g seconds' % (time.time()-tStart)
    
    #----------------------------------------------------------------------
    def testSubdivEqualNPoints101_linFitDropRate(self):
        """
        Test 'SubdivEqualNPoints" option with each subdivision of 101 data points
        for lifetime estimation. Check if the final subdivision which
        contains only 1 data points will be removed from the data set
        since that final subdivision does not have enough data points to
        estimate the lifetime from. Using linear-fit drop rate estimates.
        """
        
        tStart = time.time()

        print '\n ##### ' + self._testMethodName + ' #####'
        
        result = hla.current.calcLifetime(
            self.t_hr, self.I_mA, 
            data_subdiv_method = 'SubdivEqualNPoints',
            subNPoints = 101,
            calc_method = 'avg_I_over_LinearFitDropRate')
        
        self.assertEqual(len(result["lifetime_hr_list"]), 169)
        print 'Lifetime has been estimated for ' + \
              str(len(result["lifetime_hr_list"])) + ' points.'
        
        plot_results(self.t_hr, self.I_mA, 
                     result["avg_time_hr_array"], result["lifetime_hr_list"],
                     lifetime_error = result["lifetime_hr_error_list"],
                     show_plot = False)

        print 'Elapsed time is %.4g seconds' % (time.time()-tStart)
     
     
     #----------------------------------------------------------------------
    def testSubdivEqualSeconds_linFitDropRate(self):
        """
        Test 'SubdivEqualSeconds" option with other default arguments,
        using linear-fit drop rate estimates.
        """
        
        tStart = time.time()
        
        print '\n ##### ' + self._testMethodName + ' #####'

        result = hla.current.calcLifetime(
            self.t_hr, self.I_mA,
            data_subdiv_method = 'SubdivEqualSeconds',
            calc_method = 'avg_I_over_LinearFitDropRate')
        
        plot_results(self.t_hr, self.I_mA, 
                     result["avg_time_hr_array"], result["lifetime_hr_list"],
                     lifetime_error = result["lifetime_hr_error_list"],
                     show_plot = False)

        print 'Elapsed time is %.4g seconds' % (time.time()-tStart)
        
    #----------------------------------------------------------------------
    def testSubdivEqualSeconds100_linFitDropRate(self):
        """
        Test 'SubdivEqualSeconds" option with each subdivision of 100-sec
        duration for lifetime estimation. Using linear-fit drop rate estimates.
        """
        
        tStart = time.time()
        
        print '\n ##### ' + self._testMethodName + ' #####'

        result = hla.current.calcLifetime(
            self.t_hr, self.I_mA,
            data_subdiv_method = 'SubdivEqualSeconds',
            subDurationSeconds = 100,
            calc_method = 'avg_I_over_LinearFitDropRate')
        
        
        self.assertEqual(len(result["lifetime_hr_list"]), 177)
        print 'Lifetime has been estimated for ' + \
              str(len(result["lifetime_hr_list"])) + ' points.'
        
        plot_results(self.t_hr, self.I_mA, 
                     result["avg_time_hr_array"], result["lifetime_hr_list"],
                     lifetime_error = result["lifetime_hr_error_list"],
                     show_plot = False)
        
        print 'Elapsed time is %.4g seconds' % (time.time()-tStart) 
        
        


########################################################################
class TestLT_ExpDecayFit(unittest.TestCase):
    """
    Testing lifetime estimate functionality based on exponential decay fit
    """

    #----------------------------------------------------------------------
    def setUp(self):
        
        tStart = time.time()
        
        compressed_str = cPickle.load(open('sample_beam_current_data.pkl', 'rb'))
        decompressed_str = zlib.decompress(compressed_str)
        beam_history_data = cPickle.loads(decompressed_str)
        
        self.t_hr = beam_history_data['t_hr']
        self.I_mA = beam_history_data['I_mA']
        
        print 'Elapsed time for setUp is %.4g seconds' % (time.time()-tStart)
        
        
    #----------------------------------------------------------------------
    def test_plot_loaded_data(self):
        """"""
        
        tStart = time.time()
        
        show_plot = False # Set to True to stop the code here for examining the plot
        if show_plot:
            plt.clf()
            plt.plot(self.t_hr, self.I_mA, '.-')
            plt.xlabel('Time [hr]')
            plt.ylabel('Beam Current [mA]')
            plt.show()

        print 'Elapsed time is %.4g seconds' % (time.time()-tStart)

    #----------------------------------------------------------------------
    def testDefaultInputs(self):
        """
        Tests whether it runs without any errors with default inputs,
        i.e., with no subdivision and exponential decay fitting.
        """
        
        tStart = time.time()
        
        print '\n ##### ' + self._testMethodName + ' #####'

        result = hla.current.calcLifetime(self.t_hr, self.I_mA)
        
        print result["fit_object_list"][0]
        
        show_plot = False # Set to True to stop the code here for examining the plot
        if show_plot:
            plt.clf()
            plt.plot(self.t_hr, self.I_mA, '.-', label='Data', linewidth=0.5)
            plt.plot(result["t_fit_list"][0], result["I_fit_list"][0], 'r.-', 
                     label='Exp. Fit', linewidth=0.5)
            plt.xlabel('Time [hr]')
            plt.ylabel('Beam Current [mA]')
            plt.legend()
            plt.title( r'Lifetime [hr] = %.4g $\pm$ %.4g' 
                       % (result["lifetime_hr_list"][0],
                          result["lifetime_hr_error_list"][0] ) )
            plt.show()
            
        print 'Elapsed time is %.4g seconds' % (time.time()-tStart)


    
    
    
        
    #----------------------------------------------------------------------
    def testSubdivEqualNPoints_expDecay(self):
        """
        Test 'SubdivEqualNPoints" option with other default arguments,
        using exponential decay fit.
        """
        
        tStart = time.time()
        
        print '\n ##### ' + self._testMethodName + ' #####'

        result = hla.current.calcLifetime(
            self.t_hr, self.I_mA, 
            data_subdiv_method = 'SubdivEqualNPoints')
        
        plot_results(self.t_hr, self.I_mA, 
                     result["avg_time_hr_array"], result["lifetime_hr_list"],
                     lifetime_error = result["lifetime_hr_error_list"],
                     show_plot = False)
        
        print 'Elapsed time is %.4g seconds' % (time.time()-tStart)
     
    #----------------------------------------------------------------------
    def testSubdivEqualNPoints100_expDecay(self):
        """
        Test 'SubdivEqualNPoints" option with each subdivision of 100 data points
        for lifetime estimation, using exponential decay fit.
        """
        
        tStart = time.time()
        
        print '\n ##### ' + self._testMethodName + ' #####'

        result = hla.current.calcLifetime(
            self.t_hr, self.I_mA, 
            data_subdiv_method = 'SubdivEqualNPoints',
            subNPoints = 100)
        
        
        self.assertEqual(len(result["lifetime_hr_list"]), 171)
        print 'Lifetime has been estimated for ' + \
              str(len(result["lifetime_hr_list"])) + ' points.'
        
        plot_results(self.t_hr, self.I_mA, 
                     result["avg_time_hr_array"], result["lifetime_hr_list"],
                     lifetime_error = result["lifetime_hr_error_list"],
                     show_plot = False) 

        print 'Elapsed time is %.4g seconds' % (time.time()-tStart)

    #----------------------------------------------------------------------
    def testSubdivEqualNPoints101_expDecay(self):
        """
        Test 'SubdivEqualNPoints" option with each subdivision of 101 data points
        for lifetime estimation. Check if the final subdivision which
        contains only 1 data points will be removed from the data set
        since that final subdivision does not have enough data points to
        estimate the lifetime from. Using exponential decay fit.
        """
        
        tStart = time.time()

        print '\n ##### ' + self._testMethodName + ' #####'
        
        result = hla.current.calcLifetime(
            self.t_hr, self.I_mA, 
            data_subdiv_method = 'SubdivEqualNPoints',
            subNPoints = 101)
        
        self.assertEqual(len(result["lifetime_hr_list"]), 169)
        print 'Lifetime has been estimated for ' + \
              str(len(result["lifetime_hr_list"])) + ' points.'
        
        plot_results(self.t_hr, self.I_mA, 
                     result["avg_time_hr_array"], result["lifetime_hr_list"],
                     lifetime_error = result["lifetime_hr_error_list"],
                     show_plot = False) 

        print 'Elapsed time is %.4g seconds' % (time.time()-tStart)
    
    #----------------------------------------------------------------------
    def testSubdivEqualSeconds_expDecay(self):
        """
        Test 'SubdivEqualSeconds" option with other default arguments,
        using exponential decay fit.
        """
        
        tStart = time.time()
        
        print '\n ##### ' + self._testMethodName + ' #####'

        result = hla.current.calcLifetime(
            self.t_hr, self.I_mA, 
            data_subdiv_method = 'SubdivEqualSeconds')
        
        
        plot_results(self.t_hr, self.I_mA, 
                     result["avg_time_hr_array"], result["lifetime_hr_list"],
                     lifetime_error = result["lifetime_hr_error_list"],
                     show_plot = False) 

        print 'Elapsed time is %.4g seconds' % (time.time()-tStart)
   
   #----------------------------------------------------------------------
    def testSubdivEqualSeconds100_expDecay(self):
        """
        Test 'SubdivEqualSeconds" option with each subdivision of 100-sec
        duration for lifetime estimation. Using exponential decay fit.
        """
        
        tStart = time.time()
        
        print '\n ##### ' + self._testMethodName + ' #####'

        result = hla.current.calcLifetime(
            self.t_hr, self.I_mA, 
            data_subdiv_method = 'SubdivEqualSeconds',
            subDurationSeconds = 100)
        
        
        self.assertEqual(len(result["lifetime_hr_list"]), 177)
        print 'Lifetime has been estimated for ' + \
              str(len(result["lifetime_hr_list"])) + ' points.'
        
        plot_results(self.t_hr, self.I_mA, 
                     result["avg_time_hr_array"], result["lifetime_hr_list"],
                     lifetime_error = result["lifetime_hr_error_list"],
                     show_plot = False) 

        print 'Elapsed time is %.4g seconds' % (time.time()-tStart) 
    
        
if __name__ == "__main__" :
    unittest.main()
    