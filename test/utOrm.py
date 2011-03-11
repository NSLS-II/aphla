#!/usr/bin/env python

import hla
import unittest
import sys
import numpy as np

from cothread.catools import caget
import matplotlib.pylab as plt

class TestConf(unittest.TestCase):
    def setUp(self):
        #print "HLA clean init() "
        #hla.clean_init()
        pass

    def test_measure_orm(self):
        trimx = hla.getGroupMembers(['*', 'TRIMX', 'G2', 'C02'], op='intersection')
        bpmx = hla.getGroupMembers(['*', 'BPMX', 'C03'], op='intersection')

        trimxsp = [v[0] for v in hla.getSpChannels(trimx)]
        trimxrb = [v[0] for v in hla.getRbChannels(trimx)]
        bpmxrb  = [v[0] for v in hla.getRbChannels(bpmx)]

        for i in range(len(trimx)):
            print i, trimx[i], trimxsp[i], trimxrb[i]
        for i in range(len(bpmx)):
            print i, bpmx[i], bpmxrb[i]

        orm = hla.measOrbitRm(bpm = bpmx, trim = trimx)
        pass


if __name__ == "__main__":
    hla.clean_init()
    unittest.main()


