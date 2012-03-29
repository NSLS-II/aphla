#!/usr/bin/env python

from conf import *

import unittest
import aphla as ap
import sys, os
import numpy as np
import random
import logging

machine_initialized = False

class TestOrbit(unittest.TestCase):
    """
    Tested:

    - orbit dimension
    """

    def setUp(self):
        self.logger = logging.getLogger("test_orbit")
        global machine_initialized
        if not machine_initialized:
            ap.machines.initNSLS2VSR()
            machine_initialized = True
        self.lat = ap.machines.getLattice('SR')
        self.assertTrue(self.lat)

    def tearDown(self):
        self.logger.info("tearDown")
        pass
        
    def test_orbit_read(self):
        self.logger.info("reading orbit")    
        self.assertTrue(len(ap.getElements('BPM')) > 0)
        bpm = ap.getElements('BPM')
        for i,e in enumerate(bpm):
            self.assertTrue(abs(e.x) > 0)
            self.assertTrue(abs(e.y) > 0)

        v = ap.getOrbit()
        self.assertTrue(len(v) > 0)
        v = ap.getOrbit('*')
        self.assertTrue(len(v) > 0)
        v = ap.getOrbit('P*')
        self.assertTrue(len(v) > 0)

    def test_orbit_bump(self):
        v0 = ap.getOrbit()
        bpm = ap.getElements('BPM')
        hcor = ap.getElements('HCOR')
        vcor = ap.getElements('VCOR')
        #for e in hcor:
        #    print e.name, e.pv(field='x')

        self.assertTrue(len(v0) > 0)
        self.assertTrue(len(bpm) == 180)
        self.assertTrue(len(hcor) == 180)
        self.assertTrue(len(vcor) == 180)

        # maximum deviation
        mx, my = max(abs(v0[:,0])), max(abs(v0[:,1]))
        ih = np.random.randint(0, len(hcor), 3)
        iv = np.random.randint(0, len(vcor), 4)

        for i in ih: hcor[i].x = np.random.rand()*1e-5
        for i in iv: vcor[i].y = np.random.rand()*1e-5

        ap.hlalib.waitStableOrbit(v0, minwait=5)

        v1 = ap.getOrbit()
        self.assertGreater(np.std(v1[:,0]), np.std(v0[:,0]))
        self.logger.info("resetting trims")
        ap.hlalib._reset_trims()
        time.sleep(10)

if __name__ == "__main__":
    unittest.main()

