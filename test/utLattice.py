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
    def setUp(self):
        #self.lat = lattice.createLatticeFromTxtTable(LATCONF)
        machines.initNSLS2VSR()
        self.cfslat = machines._lat
        bpmx = self.cfslat.getElements('HLA:BPMX')
        bpmy = self.cfslat.getElements('HLA:BPMY')
        self.current = self.cfslat['DCCT']

    def test_getelements(self):
        elems = self.cfslat.getElements('HLA*')
        self.assertTrue(len(elems) == 2)
        
        elems = self.cfslat.getElements(['PL1G2C01A', 'PL2G2C01A'])
        self.assertTrue(len(elems) == 2)
        
        # only cell 1,3,5,7,9 and PL1, PL2
        elems = self.cfslat.getElements('PL*G2C0*')
        self.assertTrue(len(elems) == 10)

    def test_locations(self):
        elem = self.cfslat.getElements('*')
        for i,e in enumerate(elem):
            if e.name.startswith('HLA'): continue
            if i == 0: continue
            self.assertTrue(elem[i].s >= elem[i-1].s)

        elem = self.cfslat.getElements('BPMX')
        for i,e in enumerate(elem):
            if i == 0: continue
            self.assertTrue(elem[i].s >= elem[i-1].s,
                            "%f (%s) %f (%s)" % (elem[i].s, elem[i].name,
                                                 elem[i-1].s, elem[i-1].name))

        elem = self.cfslat.getElements('QUAD')
        for i,e in enumerate(elem):
            if i == 0: continue
            self.assertTrue(elem[i].s >= elem[i-1].s)


        pass

    def test_format(self):
        element.Element.STR_FORMAT = \
            "%4d %10s %6s %9.4f %9.4f %10s %3s %2s %s %s"
        for i in range(self.cfslat.size()):
            #s = self.cfslat[i].status
            pass

    def test_current(self):
        self.assertTrue(self.cfslat.hasElement('DCCT'))
        
        cur = self.cfslat.getElements('DCCT')
        self.assertTrue(cur.s == 0.0)
        self.assertTrue(self.current.value > 0.0)
        self.assertTrue(cur.value > 0.0)

    def test_groupmembers(self):
        bx = self.cfslat.getElements('BPMX')
        by = self.cfslat.getElements('BPMY')

        b = self.cfslat.getGroupMembers(['BPMX', 'BPMY'], op='intersection')
        self.assertTrue(len(b) == len(bx))
        self.assertTrue(len(b) == len(by))

        b = self.cfslat.getGroupMembers(['BPMX', 'BPMY'], op='union')
        self.assertTrue(len(b) == len(bx))
        self.assertTrue(len(b) == len(by))

        cx = self.cfslat.getElements('TRIMX')
        cy = self.cfslat.getElements('TRIMY')
        c = self.cfslat.getGroupMembers(['TRIMX', 'QUAD'], op = 'intersection')
        self.assertFalse(c)

        elem = self.cfslat.getGroupMembers(
            ['BPMX', 'TRIMX', 'QUAD', 'TRIMY'], op='union')
        self.assertTrue(len(elem) > 120)
        for i,e in enumerate(elem):
            if i == 0: continue
            self.assertTrue(elem[i].s >= elem[i-1].s)


if __name__ == "__main__":
    unittest.main()

