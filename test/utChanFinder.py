#!/usr/bin/env python

import hla
import unittest
import sys, os
import numpy as np

from cothread.catools import caget

import matplotlib.pylab as plt

class TestChanFinderAgent(unittest.TestCase):

    def setUp(self):
        self.assertTrue(os.path.exists('chanfinder.pkl'))

        self.cfa = hla.chanfinder.ChannelFinderAgent()
        self.cfa.load('chanfinder.pkl')
        pass

    def test_pvExists(self):
        pvs = self.cfa.getChannels()
        self.assertTrue(len(pvs) > 2000)

        live, dead = [], []
        n = 0
        for k, v in enumerate(pvs):
            n += 1
            #print k, v, len(live), len(dead)
            try:
                x = caget(v.encode('ascii'), timeout=5)
                live.append(v)
            except:
                dead.append(v)
            self.assertEqual(n, len(live))

        print "Live: ", len(live), "  Dead:", len(dead)
        self.assertTrue(len(dead) == 0)

if __name__ == "__main__":
    unittest.main()


