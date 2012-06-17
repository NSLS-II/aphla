#!/usr/bin/env python

from conf import *

import unittest
import aphla as ap
import sys, os
import numpy as np
import random
import logging

# which 
VSUB = 'V1'

class TestOrbit(unittest.TestCase):
    """
    Tested:

    - orbit dimension
    """

    def setUp(self):
        self.logger = logging.getLogger("tests.TestOrbit")
        ap.initNSLS2VSR()
        self.lat = ap.machines.getLattice('V1SR')
        self.assertTrue(self.lat)

    def tearDown(self):
        self.logger.info("tearDown")
        pass
        
    def test_orbit_read(self):
        self.logger.info("reading orbit")    
        self.assertGreater(len(ap.getElements('BPM')), 0)
        bpm = ap.getElements('BPM')
        for i,e in enumerate(bpm):
            self.assertGreaterEqual(abs(e.x), 0)
            self.assertGreaterEqual(abs(e.y), 0)

        v = ap.getOrbit()
        self.assertGreater(len(v), 0)
        v = ap.getOrbit('*')
        self.assertGreater(len(v), 0)
        v = ap.getOrbit('P*')
        self.assertGreater(len(v), 0)

    def test_orbit_bump(self):
        v0 = ap.getOrbit()
        bpm = ap.getElements('BPM')
        hcor = ap.getElements('HCOR')
        vcor = ap.getElements('VCOR')
        #for e in hcor:
        #    print e.name, e.pv(field='x')

        self.assertGreater(len(v0), 0)
        self.assertEqual(len(bpm), 180)
        self.assertEqual(len(hcor), 180)
        self.assertEqual(len(vcor), 180)

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

class TestOrbitControl(unittest.TestCase): 
    def test_correct_orbit(self):
        ap.initNSLS2VSR()
        ap.hlalib._reset_trims()

        # a list of horizontal corrector
        hcor = ap.getElements('HCOR')
        hcor_v0 = [e.x for e in hcor]
        # a list of vertical corrector
        vcor = ap.getElements('VCOR')
        vcor_v0 = [e.y for e in vcor]

        bpm = ap.getElements('BPM')
        bpm_v0 = np.array([(e.x, e.y) for e in bpm], 'd')

        norm0 = (np.linalg.norm(bpm_v0[:,0]), np.linalg.norm(bpm_v0[:,1]))

        ih = np.random.randint(0, len(hcor), 4)
        for i in ih:
            hcor[i].x = np.random.rand() * 1e-5

        iv = np.random.randint(0, len(vcor), 4)
        for i in iv:
            vcor[i].y = np.random.rand() * 1e-5

        #raw_input("Press Enter to correct orbit...")
        time.sleep(4)

        cor = []
        #cor.extend([e.name for e in hcor])
        #cor.extend([e.name for e in vcor])
        cor.extend([hcor[i].name for i in ih])
        cor.extend([vcor[i].name for i in iv])

        bpm_v1 = np.array([(e.x, e.y) for e in bpm], 'd')
        norm1 = (np.linalg.norm(bpm_v1[:,0]), np.linalg.norm(bpm_v1[:,1]))

        self.assertGreater(norm1[0], norm0[0])

        ap.correctOrbit([e.name for e in bpm], cor)

        #raw_input("Press Enter to recover orbit...")
        bpm_v2 = np.array([(e.x, e.y) for e in bpm], 'd')
        #print "Euclidian norm:", 
        norm2 = (np.linalg.norm(bpm_v2[:,0]), np.linalg.norm(bpm_v2[:,1]))
        self.assertLess(norm2[0], norm1[0])
        self.assertLess(norm2[1], norm1[1])

        for i in ih:
            hcor[i].x = hcor_v0[i]

        for i in iv:
            vcor[i].y = vcor_v0[i]

        time.sleep(4)
        #raw_input("Press Enter ...")
        bpm_v3 = np.array([(e.x, e.y) for e in bpm], 'd')
        #print "Euclidian norm:", 
        norm3 = (np.linalg.norm(bpm_v3[:,0]), np.linalg.norm(bpm_v3[:,1]))
        self.assertLess(norm3[0], norm1[0])
        self.assertLess(norm3[0], norm1[0])

        #for i in range(len(ih)):
        #    x, y = hcor[ih[i]].x, vcor[iv[i]].y
        #    print i, (x - hcor_v0[ih[i]]), (y - vcor_v0[iv[i]])


if __name__ == "__main__":
    unittest.main()

