#!/usr/bin/env python

import unittest
import sys, os
import numpy as np
from aphla.catools import caget, caput, Timedout

from conf import *
from aphla import machines, lattice, element
from aphla.catools import caget

VSUB='V1'

class TestLattice(unittest.TestCase):
    def setUp(self):
        machines.initNSLS2VSR()
        # this is the internal default lattice
        self.lat = machines._lat
        self.assertTrue(self.lat)

    def test_neighbors(self):
        bpm = self.lat.getElementList('BPM')
        self.assertTrue(bpm)
        self.assertGreaterEqual(len(bpm), 180)

        el = self.lat.getNeighbors(bpm[2].name, 'BPM', 2)
        self.assertEqual(len(el), 5)
        for i in range(5):
            self.assertEqual(el[i].name, bpm[i].name,
                             "%d: %s != %s" % (i, el[i].name, bpm[i].name))

    def test_virtualelements(self):
        velem = machines.HLA_VFAMILY
        elem = self.lat.getElementList(velem)
        self.assertTrue(elem)
        #elem = self.lat.getElementList(velem, 
        self.assertIn(machines.HLA_VFAMILY, self.lat._group.keys())

    def test_getelements(self):
        elems = self.lat.getElementList('BPM')
        self.assertGreater(len(elems), 0)
        

    def test_locations(self):
        elem1 = self.lat.getElementList('*')
        for i in range(len(elem1)):
            if elem1[i].virtual: continue
            if i == 0: continue
            self.assertGreaterEqual(elem1[i].sb, elem1[i-1].sb)
            self.assertGreaterEqual(elem1[i].se, elem1[i-1].sb)

        elem1 = self.lat.getElementList('BPM')
        for i in range(len(elem1)):
            if i == 0: continue
            self.assertGreaterEqual(elem1[i].sb, elem1[i-1].sb,
                                    "%f (%s) %f (%s)" % (
                    elem1[i].sb, elem1[i].name,
                    elem1[i-1].sb, elem1[i-1].name))
            
        elem1 = self.lat.getElementList('QUAD')
        for i in range(len(elem1)):
            if i == 0: continue
            self.assertGreaterEqual(elem1[i].sb, elem1[i-1].sb,
                                    "%f (%s) %f (%s)" % (
                    elem1[i].sb, elem1[i].name,
                    elem1[i-1].sb, elem1[i-1].name))
        
            

    def test_groups(self):
        grp = 'HLATEST'
        self.assertFalse(self.lat.hasGroup(grp))
        self.lat.addGroup(grp)
        self.assertTrue(self.lat.hasGroup(grp))
        try:
            self.lat.addGroupMember(grp, 'A')
        except ValueError as e:
            pass
        self.lat.removeGroup(grp)
        self.assertFalse(self.lat.hasGroup(grp))

        
class TestLatticeSr(unittest.TestCase):
    def setUp(self):
        machines.initNSLS2VSR()
        self.lat = machines.getLattice(VSUB + 'SR')
        pass

    def test_tunes(self):
        tune, = self.lat.getElementList('TUNE')
        self.assertTrue(abs(tune.x) > 0)
        self.assertTrue(abs(tune.y) > 0)
        
    def test_current(self):
        self.assertTrue(self.lat.hasElement('DCCT'))
        
        cur1a = self.lat['DCCT']
        cur1b, = self.lat.getElementList('DCCT')
        self.assertTrue(cur1a.sb <= 0.0)
        self.assertTrue(cur1a.value > 0.0)
        self.assertTrue(cur1b.value > 0.0)

    def test_lines(self):
        elem1 = self.lat.getElementList('DIPOLE')
        s0, s1 = elem1[0].sb, elem1[0].se
        i = self.lat._find_element_s((s0+s1)/2.0)
        self.assertTrue(i >= 0)
        i = self.lat.getLine(srange=(0, 25))
        self.assertTrue(len(i) > 1)

    def test_getelements_sr(self):
        elems = self.lat.getElementList(['PL1G2C01A', 'PL2G2C01A'])
        self.assertTrue(len(elems) == 2)
        
        # only cell 1,3,5,7,9 and PL1, PL2
        elems = self.lat.getElementList('PL*G2C0*')
        self.assertTrue(len(elems) == 10)

    def test_groupmembers(self):
        bpm1 = self.lat.getElementList('BPM')
        g2a = self.lat.getElementList('G2')
        
        b1 = self.lat.getGroupMembers(['BPM', 'C20'], op='intersection')
        self.assertTrue(len(b1) == 6)
        
        b1 = self.lat.getGroupMembers(['BPM', 'G2'], op='union')
        self.assertTrue(len(b1) > len(bpm1))
        self.assertTrue(len(b1) > len(g2a))
        self.assertTrue(len(b1) < len(bpm1) + len(g2a))
        
        cx1 = self.lat.getElementList('HCOR')
        c1 = self.lat.getGroupMembers(['HCOR', 'QUAD'],
                                            op = 'intersection')
        self.assertFalse(c1)

        elem1 = self.lat.getGroupMembers(
            ['BPMX', 'TRIMX', 'QUAD', 'TRIMY'], op='union')
        self.assertTrue(len(elem1) > 120)
        for i in range(len(elem1)):
            if i == 0: continue
            self.assertTrue(elem1[i].sb >= elem1[i-1].sb)

        el1 = self.lat.getGroupMembers(['BPM', 'C0[2-3]', 'G2'],
                                            op='intersection')
        self.assertTrue(len(el1) == 4)

    def test_field(self):
        bpm = self.lat.getElementList('BPM')
        self.assertTrue(len(bpm) > 0)
        for e in bpm: 
            self.assertTrue(abs(e.x) >= 0)
            self.assertTrue(abs(e.y) >= 0)

        hcor = self.lat.getElementList('HCOR')
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

class TestLatticeLtb(unittest.TestCase):
    def setUp(self):
        machines.initNSLS2VSR()
        self.lat  = machines.getLattice(VSUB + 'LTB')
        self.assertTrue(self.lat)

    def readInvalidFieldY(self, e):
        k = e.y
        
    def test_field(self):
        bpm = self.lat.getElementList('BPM')
        self.assertGreater(len(bpm), 0)
        for e in bpm: 
            try:
                self.assertGreaterEqual(abs(e.x), 0)
            except:
                print "    Timeout:", e.name, e.pv(field='x', handle='readback')
                break

            try:
                self.assertGreaterEqual(abs(e.y), 0)
            except:
                print "    Timeout:", e.name, e.pv(field='y', handle='readback')
                break

        hcor = self.lat.getElementList('HCOR')
        self.assertGreaterEqual(len(bpm), 0)
        for e in hcor: 
            try:
                k = e.x
            except AttributeError as e:
                print "No attribute", e
            except:
                print "    Timeout:", e.name, e.pv(field='x', handle='readback')
                break

            try:
                e.x = 1e-8
            except:
                print "    Timeout:", e.name, e.pv(field='x', handle='setpoint')
                break

            self.assertGreater(abs(e.x), 0)
            e.x = k
            #print e._field
            self.assertRaises(AttributeError, self.readInvalidFieldY, e)

    def test_virtualelements(self):
        pass
