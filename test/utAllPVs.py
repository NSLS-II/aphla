#!/usr/bin/env python

import hla
import unittest
import sys, os
import numpy as np
import random

from cothread.catools import caget

from conf import *

class TestAllPvAgent(unittest.TestCase):

    def setUp(self):
        if hla.NETWORK_DOWN: return
        wait_for_svr()
        self.assertTrue(os.path.exists(CFAPKL))

        self.cfa = hla.chanfinder.ChannelFinderAgent()
        self.cfa.load(CFAPKL)
        
    def tearDown(self):
        if hla.NETWORK_DOWN: return
        reset_svr()

    def test_pvExists(self):
        if hla.NETWORK_DOWN: return
        log_txt = "log_allpv.txt"
        #print "VERSION:", TEST_CONF_VERSION
        if os.path.exists(log_txt):
            f = open(log_txt, 'r').readlines()
            if len(f) >= 1 and TEST_CONF_VERSION <= int(f[0]): return
            
        pvs = [v.encode('ascii') for v in self.cfa.getChannels()]
        self.assertTrue(len(pvs) > 2000)

        #
        try:
            x = caget(pvs, timeout=5)
        except:
            live, dead = [], []
            n = 0
            for k, v in enumerate(pvs):
                n += 1
                try:
                    x = caget(v.encode('ascii'), timeout=5)
                    live.append(v)
                except:
                    dead.append(v)
            self.assertEqual(n, len(live))

            print "Live:", len(live), " Dead:", len(dead),
            self.assertTrue(len(dead) == 0)

        f = open(log_txt, 'w')
        f.write("%d\n" % TEST_CONF_VERSION)
        f.close()
        
if __name__ == "__main__":
    unittest.main()


