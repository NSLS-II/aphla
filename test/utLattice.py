#!/usr/bin/env python

import unittest
import sys, os
import numpy as np

from conf import *
import machines

import lattice, element
import cothread
from cothread.catools import caget

machine_initialized = False

def initialize_the_machine():
    machines.initNSLS2VSR()
    machines.initNSLS2VSRTxt()

class TestLattice(unittest.TestCase):
    def setUp(self):
        global machine_initialized
        if not machine_initialized:
            initialize_the_machine()
            machine_initialized = True
        self.lat = machines.getLattice('SR')
        self.assertTrue(self.lat)

    def test_neighbors(self):
        bpm = self.lat.getElements('BPM')
        self.assertTrue(bpm)
        
        if len(bpm) >= 5:
            el = self.lat.getNeighbors(bpm[2].name, 'BPM', 2)
            self.assertTrue(len(el) == 5)
            #print [e.name for e in el]
            #print [e.name for e in bpm[:5]]
            for i in range(5):
                self.assertTrue(el[i].name == bpm[i].name,
                                "%d: %s != %s" % (i, el[i].name, bpm[i].name))
        elif len(bpm) >= 3:
            el = self.lat.getNeighbors(bpm[1].name, 'BPM', 1)
            self.assertTrue(len(el) == 3)
            for i in range(3): self.assertTrue(el[i].name == bpm[i].name)
            

    #class TestLattice:
    def test_virtualelements(self):
        elem = self.lat.getElements('HLA:*')
        self.assertTrue(elem)


    def test_getelements(self):
        elems = self.lat.getElements('BPM')
        self.assertTrue(len(elems) > 0)
        

    def test_locations(self):
        elem1 = self.lat.getElements('*')
        for i in range(len(elem1)):
            if elem1[i].name.startswith('HLA'): continue
            if i == 0: continue
            self.assertTrue(elem1[i].sb >= elem1[i-1].sb)
            self.assertTrue(elem1[i].se >= elem1[i-1].sb)

        elem1 = self.lat.getElements('BPM')
        for i in range(len(elem1)):
            if i == 0: continue
            self.assertTrue(elem1[i].sb >= elem1[i-1].sb,
                            "%f (%s) %f (%s)" % (
                                elem1[i].sb, elem1[i].name,
                                elem1[i-1].sb, elem1[i-1].name))
            
        elem1 = self.lat.getElements('QUAD')
        for i in range(len(elem1)):
            if i == 0: continue
            self.assertTrue(elem1[i].sb >= elem1[i-1].sb)
            

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

        
    def test_values(self):
        bpm = self.lat.getElements('BPM')
        try:
            for e in bpm:
                self.assertTrue(len(e.value) == 2, 
                                "element: %s, %s" % (e.name, e._field))
        except cothread.Timedout:
            pass
            

class TestLatticeSr(TestLattice):
    def setUp(self):
        global machine_initialized
        if not machine_initialized:
            initialize_the_machine()
            #machines.initNSLS2VSR()
            #machines.initNSLS2VSRTxt()
            machine_initialized = True
        self.lat = machines.getLattice('SR')
        pass

    def test_tunes(self):
        tx = self.lat.getElements('TUNEX')
        ty = self.lat.getElements('TUNEY')
        self.assertTrue(abs(tx.value) > 0)
        self.assertTrue(abs(ty.value) > 0)
        
    def test_current(self):
        self.assertTrue(self.lat.hasElement('DCCT'))
        
        cur1a = self.lat['DCCT']
        cur1b = self.lat.getElements('DCCT')
        self.assertTrue(cur1a.sb <= 0.0)
        self.assertTrue(cur1a.value > 0.0)
        self.assertTrue(cur1b.value > 0.0)

    def test_lines(self):
        elem1 = self.lat.getElements('DIPOLE')
        s0, s1 = elem1[0].sb, elem1[0].se
        i = self.lat._find_element_s((s0+s1)/2.0)
        self.assertTrue(i >= 0)
        i = self.lat.getLine(srange=(0, 25))
        self.assertTrue(len(i) > 1)

    def test_getelements_sr(self):
        elems = self.lat.getElements(['PL1G2C01A', 'PL2G2C01A'])
        self.assertTrue(len(elems) == 2)
        
        # only cell 1,3,5,7,9 and PL1, PL2
        elems = self.lat.getElements('PL*G2C0*')
        self.assertTrue(len(elems) == 10)

    def test_groupmembers(self):
        bpm1 = self.lat.getElements('BPM')
        g2a = self.lat.getElements('G2')
        
        b1 = self.lat.getGroupMembers(['BPM', 'C20'], op='intersection')
        self.assertTrue(len(b1) == 6)
        
        b1 = self.lat.getGroupMembers(['BPM', 'G2'], op='union')
        self.assertTrue(len(b1) > len(bpm1))
        self.assertTrue(len(b1) > len(g2a))
        self.assertTrue(len(b1) < len(bpm1) + len(g2a))
        
        cx1 = self.lat.getElements('HCOR')
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

class TestLatticeSrCf(TestLatticeSr):
    def setUp(self):
        global machine_initialized
        if not machine_initialized:
            initialize_the_machine()
            #machines.initNSLS2VSR()
            machine_initialized = True
        self.lat = machines.getLattice('SR')
        
class TestLatticeSrTxt(TestLatticeSr):
    def setUp(self):
        global machine_initialized
        if not machine_initialized:
            initialize_the_machine()
            #machines.initNSLS2VSRTxt()
            machine_initialized = True
        self.lat = machines.getLattice('SR-txt')


class TestLatticeLtb(TestLattice):
    def setUp(self):
        global machine_initialized
        if not machine_initialized:
            initialize_the_machine()
            #machines.initNSLS2VSR()
            machine_initialized = True
        self.lat  = machines.getLattice('LTB')

    def test_field(self):
        bpm = self.lat.getElements('BPM')
        self.assertTrue(len(bpm) > 0)
        for e in bpm: 
            try:
                self.assertTrue(abs(e.x) >= 0)
                self.assertTrue(abs(e.y) >= 0)
            except cothread.Timedout:
                print "Timeout: ", e.name
                pass

        hcor = self.lat.getElements('HCOR')
        self.assertTrue(len(bpm) > 0)
        try:
            for e in hcor: 
                k = e.x
                e.x = 1e-8
                self.assertTrue(abs(e.x) >= 0)
                e.x = k
                k = e.y
                self.assertTrue(False,
                                "AttributeError exception expected")
        except cothread.Timedout:
            print "Timeout:", e.name
            pass
        except AttributeError as e:
            print "No attribute", e

class TestLatticeLtbCf(TestLatticeLtb):
    def setUp(self):
        global machine_initialized
        if not machine_initialized:
            initialize_the_machine()
            #machines.initNSLS2VSR()
            machine_initialized = True
        self.lat  = machines.getLattice('LTB')


class TestLatticeLtbTxt(TestLatticeLtb):
    def setUp(self):
        global machine_initialized
        if not machine_initialized:
            initialize_the_machine()
            #machines.initNSLS2VSRTxt()
        self.lat = machines.getLattice('LTB-txt')

    def test_cor(self):
        hcor = self.lat.getElements('HCOR')
        
        try:
            for e in hcor:
                v = e.value
                self.assertFalse(isinstance(v, list),
                                 "element: %s, %s" % (e.name, e._field['value']))
            vcor = self.lat.getElements('VCOR')
            for e in vcor:
                v = e.value
                self.assertFalse(isinstance(v, list),
                                 "element: %s, %s" % (e.name, e._field['value']))
        except cothread.Timedout:
            print "Timeout: ", e.name, e._field['value']

