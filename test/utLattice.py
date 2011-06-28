#!/usr/bin/env python

import unittest
import sys, os
import numpy as np

from conf import *
import machines

import lattice, element
from cothread.catools import caget


class TestLattice(unittest.TestCase):
    #class TestLattice:
    def test_virtualelements(self):
        elem = self.lat.getElements('HLA:*')
        self.assertTrue(elem)

    def test_getelements(self):

        elems = self.lat.getElements('BPM')
        self.assertTrue(len(elems) == 180)
        elems = self.lat.getElements('BPM')
        self.assertTrue(len(elems) == 180)
        
        elems = self.lat.getElements(['PL1G2C01A', 'PL2G2C01A'])
        self.assertTrue(len(elems) == 2)
        elems = self.lat.getElements(['PL1G2C01A', 'PL2G2C01A'])
        self.assertTrue(len(elems) == 2)
        
        # only cell 1,3,5,7,9 and PL1, PL2
        elems = self.lat.getElements('PL*G2C0*')
        self.assertTrue(len(elems) == 10)
        elems = self.lat.getElements('PL*G2C0*')
        self.assertTrue(len(elems) == 10)

    def test_locations(self):
        elem1 = self.lat.getElements('*')
        elem2 = self.lat.getElements('*')
        self.assertTrue(len(elem1) == len(elem2), '%d != %d' % (len(elem1), len(elem2)))
        for i in range(len(elem1)):
            if elem1[i].name.startswith('HLA'): continue
            if elem2[i].name.startswith('HLA'): continue
            if i == 0: continue
            self.assertTrue(elem1[i].sb >= elem1[i-1].sb)
            self.assertTrue(elem2[i].sb >= elem2[i-1].sb)
            self.assertTrue(elem1[i].se >= elem1[i-1].sb)
            self.assertTrue(elem2[i].se >= elem2[i-1].sb)

        elem1 = self.lat.getElements('BPM')
        elem2 = self.lat.getElements('BPM')
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
            
        elem1 = self.lat.getElements('QUAD')
        elem2 = self.lat.getElements('QUAD')
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
        for i in range(self.lat.size()):
            #s = self.cfslat[i].status
            pass

    def test_current(self):
        self.assertTrue(self.lat.hasElement('DCCT'))
        
        cur1a = self.lat['DCCT']
        cur1b = self.lat.getElements('DCCT')
        self.assertTrue(cur1a.sb == 0.0)
        self.assertTrue(cur1a.value > 0.0)
        self.assertTrue(cur1b.value > 0.0)

    def test_groups(self):
        grp = 'HLATEST'
        self.assertFalse(self.lat.hasGroup(grp))
        self.assertFalse(self.lat.hasGroup(grp))
        self.lat.addGroup(grp)
        self.assertTrue(self.lat.hasGroup(grp))
        try:
            self.lat.addGroupMember(grp, 'A')
        except ValueError as e:
            pass
        self.lat.removeGroup(grp)
        self.assertFalse(self.lat.hasGroup(grp))

    def test_groupmembers(self):
        bpm1 = self.lat.getElements('BPM')
        bpm2 = self.lat.getElements('BPM')
        g2a = self.lat.getElements('G2')
        g2b = self.lat.getElements('G2')
        
        b1 = self.lat.getGroupMembers(['BPM', 'C20'], op='intersection')
        b2 = self.lat.getGroupMembers(['BPM', 'C20'], op='intersection')
        self.assertTrue(len(b1) == 6)
        self.assertTrue(len(b2) == len(b1))
        
        b1 = self.lat.getGroupMembers(['BPM', 'G2'], op='union')
        self.assertTrue(len(b1) > len(bpm1))
        self.assertTrue(len(b1) > len(g2a))
        self.assertTrue(len(b1) < len(bpm1) + len(g2a))
        
        cx1 = self.lat.getElements('TRIMX')
        cy1 = self.lat.getElements('TRIMY')
        c1 = self.lat.getGroupMembers(['TRIMX', 'QUAD'],
                                            op = 'intersection')
        self.assertFalse(c1)

        elem1 = self.lat.getGroupMembers(
            ['BPMX', 'TRIMX', 'QUAD', 'TRIMY'], op='union')
        elem2 = self.lat.getGroupMembers(
            ['BPMX', 'TRIMX', 'QUAD', 'TRIMY'], op='union')
        self.assertTrue(len(elem1) == len(elem2))
        self.assertTrue(len(elem1) > 120)
        for i in range(len(elem1)):
            self.assertTrue(elem1[i].name == elem2[i].name)
            if i == 0: continue
            self.assertTrue(elem1[i].sb >= elem1[i-1].sb)
            self.assertTrue(elem2[i].sb >= elem2[i-1].sb)

        el1 = self.lat.getGroupMembers(['BPM', 'C0[2-3]', 'G2'],
                                            op='intersection')
        el2 = self.lat.getGroupMembers(['BPM', 'C0[2-3]', 'G2'],
                                             op='intersection')
        self.assertTrue(len(el1) == len(el2))
        self.assertTrue(len(el1) == 4)
        
    def test_lines(self):
        elem1 = self.lat.getElements('DIPOLE')
        elem2 = self.lat.getElements('DIPOLE')
        self.assertTrue(len(elem1) == len(elem2))
        self.assertTrue(elem1[0].sb == elem2[0].sb)
        s0, s1 = elem1[0].sb, elem1[0].se
        i = self.lat._find_element_s((s0+s1)/2.0)
        self.assertTrue(i >= 0)
        i = self.lat.getLine(srange=(0, 25))
        self.assertTrue(len(i) > 1)


class TestLatticeCf(TestLattice):
    def setUp(self):
        machines.initNSLS2VSR()
        self.lat  = machines.getLattice('SR')

class TestLatticeTxt(TestLattice):
    def setUp(self):
        machines.initNSLS2VSRTxt()
        self.lat = machines.getLattice('SR-txt')

    def test_field(self):
        bpm = self.lat.getElements('BPM')
        self.assertTrue(len(bpm) > 0)
        for e in bpm: 
            self.assertTrue(abs(e.x) > 0)
            self.assertTrue(abs(e.y) > 0)

        hcor = self.lat.getElements('HCOR')
        self.assertTrue(len(bpm) > 0)
        for e in hcor: 
            k = e.x
            e.x = 1e-8
            self.assertTrue(abs(e.x) >= 0)
            e.x = k
            try:
                k = e.y
            except:
                pass
            else:
                self.assertTrue(False,
                                "AttributeError exception expected")
