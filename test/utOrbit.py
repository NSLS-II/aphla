#!/usr/bin/env python

from conf import *

import hla
import unittest
import sys, os
import numpy as np
import random

machine_initialized = False

class TestOrbit(unittest.TestCase):
    """
    Tested:

    - orbit dimension
    """

    def setUp(self):
        global machine_initialized
        if not machine_initialized:
            hla.machines.initNSLS2VSR()
            #hla.machines.initNSLS2VSRTxt()
            machine_initialized = True
        self.lat = hla.machines.getLattice('SR')
        self.assertTrue(self.lat)
        
    def test_orbit_read(self):
        self.assertTrue(len(hla.getElements('BPM')) > 0)
        bpm = hla.getElements('BPM')
        for i,e in enumerate(bpm):
            self.assertTrue(abs(e.x) > 0)
            self.assertTrue(abs(e.y) > 0)

        v = hla.getOrbit()
        self.assertTrue(len(v) > 0)
        v = hla.getOrbit('*')
        self.assertTrue(len(v) > 0)
        v = hla.getOrbit('P*')
        self.assertTrue(len(v) > 0)

    def test_orbit_bump(self):
        v0 = hla.getOrbit()
        bpm = hla.getElements('BPM')
        hcor = hla.getElements('HCOR')
        vcor = hla.getElements('VCOR')
        #for e in hcor:
        #    print e.name, e.pv(field='x')

        self.assertTrue(len(v0) > 0)
        self.assertTrue(len(bpm) == 180)
        self.assertTrue(len(hcor) == 180)
        self.assertTrue(len(vcor) == 180)

        mx, my = max(abs(v0[:,0])), max(abs(v0[:,1]))
        ih = np.random.randint(0, len(hcor), 3)
        iv = np.random.randint(0, len(vcor), 4)

        

if __name__ == "__main__":
    unittest.main()

