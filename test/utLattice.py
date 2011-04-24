#!/usr/bin/env python

import hla
import unittest
import sys, os
import numpy as np

from cothread.catools import caget

#import matplotlib
import matplotlib.pylab as plt

from conf import *

class TestLattice(unittest.TestCase):
    def setUp(self):
        self.assertTrue(os.path.exists(CFAPKL))

        self.cfa = hla.chanfinder.ChannelFinderAgent()
        self.cfa.load(CFAPKL)
        self.lat = hla.lattice.Lattice()
        #self.lat.importChannelFinderData(self.cfa)
        self.lat.load(HLAPKL, mode='virtac')
        self.lat.mergeGroups('TRIM', ['TRIMX', 'TRIMY'])
        self.lat.mergeGroups('BPM', ['BPMX', 'BPMY'])
        #self.lat.init_virtac_twiss()
        #self.lat.mode = 'virtac'
        #self.lat.save('lattice.pkl')
        #self.lat.load('lattice.pkl', mode='virtac')
        

    def test_elements(self):
        elem = self.lat.getElements('P*')
        s    = self.lat.getLocations('P*', point='end')
        self.assertEqual(len(elem), 180)
        self.assertEqual(len(s), 180)
        
        self.assertEqual(len(self.lat.getElements('*')), 
                         len(set(self.lat.getElements('*'))))

        s = self.lat.getLocations(['PH2G6C29B', 'CFYH2G1C30A', 'C'], point='end')
        self.assertEqual(len(s), 3)
        self.assertEqual(s[-1], None)

    def test_group(self):
        """
        >>> hla.getGroups('P*C01*')
        ['A', 'BPM', 'C01', 'G6', 'G4', 'G2', 'B']
        """
        self.lat.addGroup('BPM')
        self.assertRaises(ValueError, self.lat.addGroup, "h*")
        grp = self.lat.getGroups('P*C01*')
        #print "group:", grp
        for g in ['A', 'BPM', 'G6', 'G4', 'G2', 'BPMY', 'C01', 'BPMX', 'B']:
            #print g,
            self.assertTrue(g in grp)
        #print self.lat.getGroups('FYH2G1C30A')
        g1 = self.lat.getGroupMembers(['BPM', 'C02'], op = 'intersection')
        g2 = self.lat.getElements('P*C02*')
        for g in g1:
            self.assertTrue(g in g2)
        for g in g2:
            self.assertTrue(g in g1)

        # popular group name
        self.assertEqual(len(self.lat.getElements('TRIM')), 540)
        self.assertEqual(len(self.lat.getElements('TRIMX')), 270)
        self.assertEqual(len(self.lat.getElements('TRIMY')), 270)
        # BPMX = BPMY = BPM, all same name
        self.assertEqual(len(self.lat.getElements('BPM')), 180)
        self.assertEqual(len(self.lat.getElements('BPMX')), 180)
        self.assertEqual(len(self.lat.getElements('BPMY')), 180)
        self.assertEqual(len(self.lat.getElements('QUAD')), 300)

        self.assertEqual(len(self.lat.getElements('C01')), 46)
        self.assertEqual(len(self.lat.getElements('C30')), 46)
        self.assertEqual(len(self.lat.getElements('C11')), 46)

        self.assertEqual(len(self.lat.getElements('G2')), 375)

    def test_neighbors1(self):
        # find BPMs near CFYH2G1C30A
        vcm = 'FYH2G1C30A'
        self.assertEqual(self.lat.getElements(vcm), [vcm])

        n = 3
        nb = self.lat.getNeighbors(vcm, 'BPM', n)
        s0 = self.lat.getLocations(vcm, 'end')
        self.assertEqual(len(s0), 1)
        self.assertEqual(len(nb), 2*n+1)
        
        nb2 = self.lat.getNeighbors(vcm, 'P*', n)
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
        self.assertEqual(len(self.lat.getTunes()), 2)
        self.assertTrue(len(self.lat.twiss) > 1)

        elem = self.lat.getElements('*')
        #print len(elem), self.lat.getBeta(elem)
        
        self.assertEqual(len(self.lat.getPhase(elem)),
                         len(self.lat.getElements('*')))
        self.assertEqual(len(self.lat.getPhase(elem)),
                         len(self.lat.getElements('*')))
        self.assertEqual(len(self.lat.getBeta(elem)),
                         len(self.lat.getElements('*')))
        self.assertEqual(len(self.lat.getBeta(elem)),
                         len(self.lat.getElements('*')))

        phi = self.lat.getPhase('P*C01*')
        beta = self.lat.getBeta(elem)
        s = self.lat.getLocations(elem, 'end')
        elem2 = self.lat.getElements('P*')
        eta = self.lat.getEta('P*')
        s2 = self.lat.getLocations('P*', 'end')

        #print len(s), len(eta), len(phi), len(beta), len(s2)
        #print s2, eta
        
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

    def test_beamlineprofile(self):
        #
        prof = self.lat.getBeamlineProfile(0.0, 30)
        for p in prof:
            plt.plot(p[0], p[1], p[2])
        #plt.plot([prof[0][0], prof[-1][0]], [0,0], 'k')
        plt.ylim([-2.5, 2.5])
        plt.savefig('test_beamline_profile.png')

if __name__ == "__main__":
    unittest.main()

