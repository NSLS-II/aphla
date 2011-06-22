#!/usr/bin/env python

import unittest
import sys, os
import numpy as np
import matplotlib.pylab as plt

from conf import *
import machines

import lattice, element
from cothread.catools import caget

class TestLattice(unittest.TestCase):
    #class TestLattice:
    def setUp(self):
        #self.lat = lattice.createLatticeFromTxtTable(LATCONF)
        #machines.initNSLS2VSR()
        machines.initNSLS2VSR()
        self.cfslat_cf  = machines.getLattice('sr')
        machines.initNSLS2VSRTxt()
        self.cfslat_txt = machines.getLattice('sr-txt')
        

    def test_getelements(self):

        elems = self.cfslat_cf.getElements('BPM')
        self.assertTrue(len(elems) == 180)
        elems = self.cfslat_txt.getElements('BPM')
        self.assertTrue(len(elems) == 180)
        
        elems = self.cfslat_cf.getElements(['PL1G2C01A', 'PL2G2C01A'])
        self.assertTrue(len(elems) == 2)
        elems = self.cfslat_txt.getElements(['PL1G2C01A', 'PL2G2C01A'])
        self.assertTrue(len(elems) == 2)
        
        # only cell 1,3,5,7,9 and PL1, PL2
        elems = self.cfslat_cf.getElements('PL*G2C0*')
        self.assertTrue(len(elems) == 10)
        elems = self.cfslat_txt.getElements('PL*G2C0*')
        self.assertTrue(len(elems) == 10)

    def test_locations(self):
        elem1 = self.cfslat_cf.getElements('*')
        elem2 = self.cfslat_txt.getElements('*')
        self.assertTrue(len(elem1) == len(elem2))
        for i in range(len(elem1)):
            if elem1[i].name.startswith('HLA'): continue
            if elem2[i].name.startswith('HLA'): continue
            if i == 0: continue
            self.assertTrue(elem1[i].sb >= elem1[i-1].sb)
            self.assertTrue(elem2[i].sb >= elem2[i-1].sb)
            self.assertTrue(elem1[i].se >= elem1[i-1].sb)
            self.assertTrue(elem2[i].se >= elem2[i-1].sb)

        elem1 = self.cfslat_cf.getElements('BPM')
        elem2 = self.cfslat_txt.getElements('BPM')
        self.assertTrue(len(elem1) == len(elem2))
        for i in range(len(elem1)):
            self.assertTrue(elem1[i].name == elem2[i].name)
            if i == 0: continue
            self.assertTrue(elem1[i].sb >= elem1[i-1].sb,
                            "%f (%s) %f (%s)" % (
                                elem1[i].sb, elem1[i].name,
                                elem1[i-1].sb, elem1[i-1].name))
            self.assertTrue(elem2[i].sb >= elem2[i-1].sb,
                            "%f (%s) %f (%s)" % (
                                elem2[i].sb, elem2[i].name,
                                elem2[i-1].sb, elem2[i-1].name))
            
        elem1 = self.cfslat_cf.getElements('QUAD')
        elem2 = self.cfslat_txt.getElements('QUAD')
        self.assertTrue(len(elem1) == len(elem2))
        for i in range(len(elem1)):
            self.assertTrue(elem1[i].name == elem2[i].name)
            if i == 0: continue
            self.assertTrue(elem1[i].sb >= elem1[i-1].sb)
            self.assertTrue(elem2[i].sb >= elem2[i-1].sb)
            

        pass

    def test_format(self):
        element.Element.STR_FORMAT = \
            "%4d %10s %6s %9.4f %9.4f %10s %3s %2s %s %s"
        for i in range(self.cfslat_cf.size()):
            #s = self.cfslat[i].status
            pass

    def test_current(self):
        self.assertTrue(self.cfslat_cf.hasElement('DCCT'))
        
        cur1a = self.cfslat_cf['DCCT']
        cur1b = self.cfslat_cf.getElements('DCCT')
        self.assertTrue(cur1a.sb == 0.0)
        self.assertTrue(cur1a.value > 0.0)
        self.assertTrue(cur1b.value > 0.0)

    def test_groups(self):
        grp = 'HLATEST'
        self.assertFalse(self.cfslat_cf.hasGroup(grp))
        self.assertFalse(self.cfslat_txt.hasGroup(grp))
        self.cfslat_cf.addGroup(grp)
        self.assertTrue(self.cfslat_cf.hasGroup(grp))
        try:
            self.cfslat_cf.addGroupMember(grp, 'A')
        except ValueError as e:
            pass
        self.cfslat_cf.removeGroup(grp)
        self.assertFalse(self.cfslat_cf.hasGroup(grp))

    def test_groupmembers(self):
        bpm1 = self.cfslat_cf.getElements('BPM')
        bpm2 = self.cfslat_txt.getElements('BPM')
        g2a = self.cfslat_cf.getElements('G2')
        g2b = self.cfslat_txt.getElements('G2')
        
        b1 = self.cfslat_cf.getGroupMembers(['BPM', 'C20'], op='intersection')
        b2 = self.cfslat_txt.getGroupMembers(['BPM', 'C20'], op='intersection')
        self.assertTrue(len(b1) == 6)
        self.assertTrue(len(b2) == len(b1))
        
        b1 = self.cfslat_cf.getGroupMembers(['BPM', 'G2'], op='union')
        self.assertTrue(len(b1) > len(bpm1))
        self.assertTrue(len(b1) > len(g2a))
        self.assertTrue(len(b1) < len(bpm1) + len(g2a))
        
        cx1 = self.cfslat_cf.getElements('TRIMX')
        cy1 = self.cfslat_cf.getElements('TRIMY')
        c1 = self.cfslat_cf.getGroupMembers(['TRIMX', 'QUAD'],
                                            op = 'intersection')
        self.assertFalse(c1)

        elem1 = self.cfslat_cf.getGroupMembers(
            ['BPMX', 'TRIMX', 'QUAD', 'TRIMY'], op='union')
        elem2 = self.cfslat_txt.getGroupMembers(
            ['BPMX', 'TRIMX', 'QUAD', 'TRIMY'], op='union')
        self.assertTrue(len(elem1) == len(elem2))
        self.assertTrue(len(elem1) > 120)
        for i in range(len(elem1)):
            self.assertTrue(elem1[i].name == elem2[i].name)
            if i == 0: continue
            self.assertTrue(elem1[i].sb >= elem1[i-1].sb)
            self.assertTrue(elem2[i].sb >= elem2[i-1].sb)

        el1 = self.cfslat_cf.getGroupMembers(['BPM', 'C0[2-3]', 'G2'],
                                            op='intersection')
        el2 = self.cfslat_txt.getGroupMembers(['BPM', 'C0[2-3]', 'G2'],
                                             op='intersection')
        self.assertTrue(len(el1) == len(el2))
        self.assertTrue(len(el1) == 4)
        
    def test_lines(self):
        elem1 = self.cfslat_cf.getElements('DIPOLE')
        elem2 = self.cfslat_txt.getElements('DIPOLE')
        self.assertTrue(len(elem1) == len(elem2))
        self.assertTrue(elem1[0].sb == elem2[0].sb)
        s0, s1 = elem1[0].sb, elem1[0].se
        i,l = self.cfslat_cf._find_element_s((s0+s1)/2.0)
        self.assertTrue(l)
        l = self.cfslat_cf.getLine(srange=(0, 25))
        self.assertTrue(len(l) > 1)


if __name__ == "__main__":
    machines.initNSLS2VSR()
    machines.initNSLS2VSRTxt()
    unittest.main()

