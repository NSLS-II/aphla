#!/usr/bin/env python

import hla
import unittest
import sys

from cothread.catools import caget

class TestConf(unittest.TestCase):
    def setUp(self):
        #print "HLA clean init() "
        #hla.clean_init()
        pass

    def test_pvExists(self):
        hla.check()
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
        s    = hla.getLocations('P*')
        s = hla.getLocations(['PH2G6C29B', 'CFYH2G1C30A', 'C'])
        #print s
        #print len(s), len(elem)
        #for i in range(len(s)):
        #    print s[i], elem[i]
    
    def test_group(self):
        """
        >>> hla.getGroups('P*C01*')
        ['A', 'BPM', 'C01', 'G6', 'G4', 'G2', 'B']
        """
        hla.addGroup('BPM')
        try:
            hla.addGroup("h*")
        except ValueError as e:
            print __file__, e
        print __file__, hla.getGroups('P*C01*')
        print __file__, hla.getGroupMembers(['BPM', 'C02'], op = 'intersection')

    def test_neighbors(self):
        print __file__, "neighbors", hla.getNeighbors('CFYH2G1C30A', 'BPM')
        
    def test_twiss(self):
        print hla.getPhase('P*C01*')
        print hla.getBeta('P*C02*')
        print hla.getDispersion('P*C03*')
        print hla.getTunes()

    def test_pvget(self):
        print __file__, hla.eget('P*C01*')

    def test_pvset(self):
        elem = hla.getElements('C[XY]*C01*A')
        print __file__, elem
        print __file__, hla.eget(elem)
        hla.eset(elem, [1e-8, 1e-8, 1e-8, 1e-8, 1e-8, 1e-8])
        print __file__, hla.eget('C[XY]*C01*A')
        hla.eset(elem, [0.0] * 6)
        print __file__, hla.eget(elem)

        pass

if __name__ == "__main__":
    hla.clean_init()
    unittest.main()


