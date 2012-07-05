import unittest
import numpy as np
import aphla as ap
#import matplotlib.pylab as plt
import sys, time

class TestBba(unittest.TestCase):
    def setUp(self):
        ap.initNSLS2V1()
        ap.hlalib._reset_trims()
        pass

    def test_quad(self):
        qnamelist = ['QH1G2C02A', 'QH1G2C04A', 'QH1G2C06A', 'QH1G2C08A']

        qlst = ap.getElements(qnamelist)
        for i,q in enumerate(qnamelist):
            self.assertGreater(abs(qlst[i].k1), 0.0)

        #qlst[0].value = -0.633004

        for i,qd in enumerate(qlst):
            self.assertGreater(qd.sb, 0.0)
            self.assertEqual(qd.name, qnamelist[i])

            bpm = ap.getClosest(qd.name, 'BPM')
            self.assertTrue(bpm.name)
            self.assertGreater(bpm.sb, 0.0)
            self.assertGreaterEqual(abs(bpm.x), 0.0)
            self.assertGreaterEqual(abs(bpm.y), 0.0)

            hc = ap.getNeighbors(bpm.name, 'HCOR', 1)
            self.assertEqual(len(hc), 3)
            self.assertEqual(hc[1].name, bpm.name)
            self.assertGreaterEqual(abs(hc[0].x), 0.0)
            
        #ap.createLocalBump([], [], [])


