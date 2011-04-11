#!/usr/bin/env python

import hla
import unittest
import sys, os
import numpy as np
import random

from cothread.catools import caget

HLAPKL=os.path.join(os.environ['HLA_ROOT'], 'machine', 'nsls2', 'hla.pkl')
CFAPKL=os.path.join(os.environ['HLA_ROOT'], 'machine', 'nsls2', 'chanfinder.pkl')
LATCONF=os.path.join(os.environ['HLA_ROOT'], 'machine', 'nsls2', 'lat_conf_table.txt')

class TestChanFinderAgent(unittest.TestCase):

    def setUp(self):
        self.assertTrue(os.path.exists(CFAPKL))

        self.cfa = hla.chanfinder.ChannelFinderAgent()
        self.cfa.load(CFAPKL)


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

        print "Live:", len(live), " Dead:", len(dead),
        self.assertTrue(len(dead) == 0)

if __name__ == "__main__":
    unittest.main()


