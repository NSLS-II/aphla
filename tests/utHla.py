#!/usr/bin/env python

import hla
import unittest
import sys
import numpy as np

import matplotlib
import matplotlib.pylab as plt

class TestConf(unittest.TestCase):
    def setUp(self):
        #print "HLA clean init() "
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
        s    = hla.getLocations(elem)
        self.assertEqual(len(elem), 180)
        self.assertEqual(len(s), 180)
        
        s = hla.getLocations(['PH2G6C29B', 'CFYH2G1C30A', 'C'])
        self.assertEqual(len(s), 3)
        self.assertEqual(s[-1], None)

    def test_group(self):
        """
        >>> hla.getGroups('P*C01*')
        ['A', 'BPM', 'C01', 'G6', 'G4', 'G2', 'B']
        """
        return

        hla.addGroup('BPM')
        self.assertRaises(ValueError, hla.addGroup, "h*")
        grp = hla.getGroups('P*C01*')
        for g in ['A', 'BPM', 'G6', 'G4', 'G2', 'BPMY', 'C01', 'BPMX', 'B']:
            self.assertTrue(g in grp)

        g1 = hla.getGroupMembers(['BPM', 'C02'], op = 'intersection')
        g2 = hla.getElements('P*C02*')
        for g in g1:
            self.assertTrue(g in g2)
        for g in g2:
            self.assertTrue(g in g1)

        # popular group name
        self.assertEqual(len(hla.getElements('TRIM')), 540)
        self.assertEqual(len(hla.getElements('TRIMX')), 270)
        self.assertEqual(len(hla.getElements('TRIMY')), 270)
        self.assertEqual(len(hla.getElements('BPM')), 360)
        self.assertEqual(len(hla.getElements('BPMX')), 180)
        self.assertEqual(len(hla.getElements('BPMY')), 180)
        self.assertEqual(len(hla.getElements('QUAD')), 300)

        self.assertEqual(len(hla.getElements('C01')), 52)
        self.assertEqual(len(hla.getElements('C30')), 52)
        self.assertEqual(len(hla.getElements('C11')), 52)

        self.assertEqual(len(hla.getElements('G2')), 435)

    def test_neighbors1(self):
        return
        # find BPMs near CFYH2G1C30A
        vcm = 'CFYH2G1C30A'
        n = 3
        nb = hla.getNeighbors(vcm, 'BPM', n)
        s0 = hla.getLocations(vcm)
        self.assertEqual(len(s0), 1)
        self.assertEqual(len(nb), 2*n+1)
        
        nb2 = hla.getNeighbors(vcm, 'P*', n)
        self.assertEqual(nb, nb2)

        isep = 2*n
        if nb[-1][1] < nb[0][1]:
            # its a ring.
            for i in range(2*n-1, 0, -1):
                if nb[i][1] > nb[i-1][1]: continue
                isep = i
                break
        
        for i, v in enumerate(nb[:isep-1]):
            self.assertTrue(nb[i][1] < nb[i+1][1])
        for i, v in enumerate(nb[isep:]):
            self.assertTrue(nb[i][1] > nb[i-1][1])


    def test_twiss(self):
        self.assertEqual(len(hla.getTunes()), 2)
        return

        phi = hla.getPhase('P*C01*')
        beta = hla.getBeta('*')
        s = hla.getLocations('*')
        eta = hla.getDispersion('P*')
        s2 = hla.getLocations('P*')
        
        plt.clf()
        plt.subplot(211)
        plt.plot(s, beta)
        plt.subplot(212)
        plt.plot(s2, eta)
        plt.savefig("test-twiss.png")
        
    def test_pvget(self):
        return
        #print __file__, hla.eget('P*C01*')
        self.assertEqual(len(hla.eget('P*C0*A')), 27)
        self.assertEqual(len(hla.eget('C')), 0)
        #print hla.eget('QH3*')

    def test_pvset(self):
        return True
        elem = hla.getElements('C[XY]*C01*A')
        print __file__, elem
        print __file__, hla.eget(elem)
        hla.eset(elem, [1e-8, 1e-8, 1e-8, 1e-8, 1e-8, 1e-8])
        print __file__, hla.eget('C[XY]*C01*A')
        hla.eset(elem, [0.0] * 6)
        print __file__, hla.eget(elem)

        pass

    def test_orbit(self):
        return

        elem = hla.getElements('P*C02*')
        s1 = hla.getLocations(elem)
        x1, y1 = hla.getOrbit(elem)

        s = hla.getLocations('BPMX')
        x,y = hla.getOrbit('*')
        
        r = np.array(hla.getFullOrbit())

        plt.clf()
        plt.plot(s, x, 'rx-')
        plt.plot(s, y, 'gx-')
        plt.plot(s1, x1, 'ro')
        plt.plot(s1, y1, 'gx')
        plt.plot(r[:,0], r[:,1], 'k--')
        plt.xlim([0, r[-1,0]/15.0])
        plt.savefig('test.png')

if __name__ == "__main__":
    hla.initNSLS2VSR()
    unittest.main()


