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
        self.cfslat = machines._lat

    def test_element(self):
        #print machines._twiss[-1]
        #print machines._twiss
        #print len(machines._twiss._twlist), len(machines._twiss._elements)
        self.assertTrue(len(machines._twiss._twlist) == \
                            len(machines._twiss._elements))
        self.assertTrue(machines._twiss[-1]._s >= 791.958)

if __name__ == "__main__":
    machines.initNSLS2VSRTxt()
    machines.initNSLS2VSRTwiss()
    unittest.main()

