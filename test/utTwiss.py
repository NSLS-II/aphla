#!/usr/bin/env python

import unittest
import sys, os
import numpy as np
import matplotlib.pylab as plt

from conf import *
import machines

import lattice, element
from cothread.catools import caget

class TestLattice(unittest.TestCase):
    def setUp(self):
        machines.initNSLS2VSR()
        machines.initNSLS2VSRTwiss()
        machines.initNSLS2VSRTxt()
        self.cfslat_cf = machines.use('sr')
        self.cfslat_txt = machines.use('sr-txt')
        
    def test_element(self):
        #print machines._twiss[-1]
        #print machines._twiss
        #print len(machines._twiss._twlist), len(machines._twiss._elements)
        self.assertTrue(len(machines._twiss._twlist) == \
                            len(machines._twiss._elements))
        self.assertTrue(machines._twiss[-1]._s >= 791.958)

if __name__ == "__main__":
    unittest.main()

