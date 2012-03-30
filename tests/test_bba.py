import unittest
import numpy as np
import aphla as ap
import matplotlib.pylab as plt
import sys, time

class TestBba(unittest.TestCase):
    def setUp(self):
        ap.initNSLS2VSR()
        ap.hlalib._reset_trims()
        pass

    def test_quad(self):
        qnamelist = ['QH1G2C02A', 'QH1G2C04A', 'QH1G2C06A', 'QH1G2C08A']

        qlst = ap.getElements(qnamelist)
        for i,q in enumerate(qnamelist):
            #qlst[i] = ap.getElements(q)
            print qlst[i].k1

        #qlst[0].value = -0.633004

        for i,qd in enumerate(qlst):
            bpm = ap.getClosest(qd.name, 'BPM')
            hc = ap.getNeighbors(bpm.name, 'HCOR', 1)
            print qd.name, bpm.name, hc[0].name, bpm.sb-qd.sb, qd.k1, \
                bpm.x, hc[0].x, qd.sb


        #ap.createLocalBump([], [], [])


