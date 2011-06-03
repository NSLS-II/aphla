#!/usr/bin/env python

import unittest
import sys, os
import numpy as np
import matplotlib.pylab as plt

from conf import *

import lattice, element
from cothread.catools import caget

class TestLattice(unittest.TestCase):
    def setUp(self):
        #self.lat = lattice.createLatticeFromTxtTable(LATCONF)
        self.cfslat = lattice.createLatticeFromCf()
        bpmx = self.cfslat.getElements('HLA:BPMX')
        bpmy = self.cfslat.getElements('HLA:BPMY')
        #print bpmx.status
        #print bpmy.status

    def test_getelements(self):
        elems = self.cfslat.getElements('HLA*')
        self.assertTrue(len(elems) == 2)
        
    def test_format(self):
        element.Element.STR_FORMAT = "%4d %10s %6s %9.4f %9.4f %10s %3s %2s %s %s"
        for i in range(self.cfslat.size()):
            #s = self.cfslat[i].status
            pass

if __name__ == "__main__":
    unittest.main()

