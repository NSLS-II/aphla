#!/usr/bin/env python

import hla
import unittest
import sys

from cothread.catools import caget

class TestConf(unittest.TestCase):
    def setUp(self):
        pass

    def test_pvExists(self):
        return True
        rec = {}
        n = 0
        for k, v in enumerate(hla.conf.ca.getChannels()):
            n += 1
            try:
                x = caget(v, timeout=2)
                sys.stdout.write('-')
            except:
                #print "TIME OUT"
                rec[v] = 1
                sys.stdout.write('\nx %6d  %s' % (n,v))
                
            sys.stdout.flush()
        print ""
        for k,v in rec.items():
            print k, v

    def test_elements(self):
        elem = hla.getElements('P*')
        s    = hla.getLocation('P*')
        print s,
        print elem
        print len(s), len(elem)
        for i in range(len(s)):
            print s[i], elem[i]

if __name__ == "__main__":
    unittest.main()


