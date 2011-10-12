#!/usr/bin/env python

import unittest
import sys, os, time
import numpy as np
#import matplotlib.pylab as plt

from conf import *
import element
from catools import caget, caput
import shelve

class TestElement(unittest.TestCase):
    def setUp(self):
        # current
        self.dcct = element.Element(
            name = 'CURRENT', index = -1, devname = 'DCCT', family = 'DCCT')
        self.dcct.addEGet('SR:C00-BI:G00{DCCT:00}CUR-RB')

        # bpm1
        self.bpm1 = element.Element(
            name = 'BPM1', index = -1, devname = 'BPM', family = 'BPM')
        self.bpm1.addEGet('SR:C29-BI:G06B{BPM:H1}SA:Y-I')
        self.bpm1.addEGet('SR:C29-BI:G06B{BPM:H1}SA:X-I')
        self.bpm1.addEPut('SR:C29-BI:G06B{BPM:H1}GOLDEN:Y')
        self.bpm1.addEPut('SR:C29-BI:G06B{BPM:H1}GOLDEN:X')

        # bpm2
        self.bpm2 = element.Element(
            name = 'V:BPM:X', index = -1, devname = 'BPM', virtual = 1)
        self.bpm2.addEGet('SR:C01-BI:G06B{BPM:H2}SA:X-I')
        self.bpm2.addEGet('SR:C01-BI:G04B{BPM:M1}SA:X-I')
        self.bpm2.addEGet('SR:C01-BI:G02A{BPM:L1}SA:X-I')
        self.bpm2.addEGet('SR:C01-BI:G02A{BPM:L2}SA:X-I')
        self.bpm2.addEGet('SR:C01-BI:G04A{BPM:M1}SA:X-I')
        self.bpm2.addEGet('SR:C01-BI:G06B{BPM:H1}SA:X-I')

        # trim x
        # SR:C01-MG:G02A{HCor:L1}Fld-I;
        # cell = C01, devName = CL1G2C01A, elemField = x, elemName = CXL1G2C01A,
        # elemType = HCOR, girder = G2, handle = READBACK, length = 0.2,
        # ordinal = 125, sEnd = 30.6673, symmetry = A;
        # aphla.eget, aphla.x, aphla.sys.SR
        self.hcor = element.Element(
            name = 'CXL1G2C01A', index = 125, cell = 'C01',
            devname = 'CL1G2C01A', family = 'HCOR', girder = 'G2', length = 0.2,
            se = 30.6673, symmetry = 'A')
        self.hcor.addEGet('SR:C01-MG:G02A{HCor:L1}Fld-I')
        self.hcor.addEPut('SR:C01-MG:G02A{HCor:L1}Fld-SP')

        # quad
        # SR:C01-MG:G02A{Quad:L2}Fld-I;
        # cell = C01, devName = QL2G2C01A, elemName = QL2G2C01A,
        # elemType = QUAD, girder = G2, handle = READBACK, length = 0.448,
        # ordinal = 130, sEnd = 31.6966, symmetry = A;
        # aphla.eget, aphla.sys.SR
        self.quad = element.Element(
            cell = 'C01', devname = 'QL2G2C01A', name = 'QL2G2C01A',
            family = 'QUAD', girder = 'G2', length = 0.448, index = 130, 
            se = 31.6966, symmetry = 'A')
        self.quad.addEGet('SR:C01-MG:G02A{Quad:L2}Fld-I')
        self.quad.addEPut('SR:C01-MG:G02A{Quad:L2}Fld-SP')


    def test_pickle(self):
        pass

    def test_shelve(self):
        elem = element.Element(
            name= 'CURRENT', eget = caget, eput = caput,
            index = -1,
            devname = 'DCCT',
            family = 'DCCT')
        elem.addEGet('SR:C29-BI:G06B{BPM:H1}SA:Y-I')
        elem.addEGet('SR:C29-BI:G06B{BPM:H1}SA:X-I')
        elem.setFieldGetAction('x', 'SR:C29-BI:G06B{BPM:H1}SA:X-I', 'X plane')
        elem.setFieldPutAction('x', 'SR:C29-BI:G06B{BPM:H1}GOLDEN:X', 'X plane')
        d = shelve.open("utElement.pkl")
        d['DCCT'] = elem
        d.close()

        #sys.setrecursionlimit(50)
        d2= shelve.open('utElement.pkl')
        elem2 = d2['DCCT']
        d2.close()

    def test_read(self):
        elem = element.Element(
            name= 'CURRENT', eget = caget, eput = caput,
            index = -1,
            devname = 'DCCT',
            family = 'DCCT')
        elem.addEGet('SR:C00-BI:G00{DCCT:00}CUR-RB')
        self.assertTrue(len(str(elem)) > 0)
        self.assertTrue(abs(elem.value) > 0)

    def test_readwrite(self):
        elem = element.Element(
            name = 'BPM', eget = caget, eput = caput,
            index = -1, devname = 'BPM')
        elem.addEGet('SR:C29-BI:G06B{BPM:H1}SA:Y-I')
        elem.addEGet('SR:C29-BI:G06B{BPM:H1}SA:X-I')
        elem.addEPut('SR:C29-BI:G06B{BPM:H1}GOLDEN:Y')
        elem.addEPut('SR:C29-BI:G06B{BPM:H1}GOLDEN:X')
        self.assertTrue(len(str(elem)) > 0)
        #print elem._field
        #print elem.status()
        #print caget(['SR:C29-BI:G06B{BPM:H1}SA:X-I', 'SR:C29-BI:G06B{BPM:H1}SA:Y-I'])
        caput(['SR:C29-BI:G06B{BPM:H1}GOLDEN:X', 'SR:C29-BI:G06B{BPM:H1}GOLDEN:Y'], 0.0, wait=True)
        #print caget(['SR:C29-BI:G06B{BPM:H1}GOLDEN:X', 'SR:C29-BI:G06B{BPM:H1}GOLDEN:Y'])
        #time.sleep(3)
        #elem.value = 0
        x0 = elem.value
        #print x0
        self.assertTrue(len(x0) == 2)
        elem.value = .01
        time.sleep(4)
        x1 = elem.value
        #print x0, x1
        self.assertTrue(x1[0] >= -0.01 - 2*abs(x0[0]))
        self.assertTrue(x1[1] >= -0.01 - 2*abs(x0[1]))
        self.assertTrue(x1[0] <= 2*abs(x0[0]) - 0.01, "%.8e %.8e" % (x0[0]-0.01, x1[0]))

        elem.value = [0.003, 0.002]
        x2 = elem.value
        self.assertTrue(x2[0] <= 0.003 + abs(x0[0]))
        self.assertTrue(x2[1] <= 0.002 + abs(x0[1]))

        elem.value = 0
        self.assertTrue(len(str(elem.status)) > 0)

    def test_sort(self):
        elem1 = element.Element(name= 'E1', sb= 0.0)
        elem2 = element.Element(name= 'E1', sb= 2.0)
        elem3 = element.Element(name= 'E1', sb= 1.0)
        el = sorted([elem1, elem2, elem3])
        self.assertTrue(el[0].sb < el[1].sb)
        self.assertTrue(el[1].sb < el[2].sb)
        
    def test_field(self):
        elem = element.Element(
            name = 'V:BPM', eget = caget, eput = caput,
            index = -1, devname = 'BPM')
        elem.addEGet('SR:C29-BI:G06B{BPM:H1}SA:Y-I')
        elem.addEGet('SR:C29-BI:G06B{BPM:H1}SA:X-I')
        elem.setFieldGetAction('x', 'SR:C29-BI:G06B{BPM:H1}SA:X-I', 'X plane')
        elem.setFieldPutAction('x', 'SR:C29-BI:G06B{BPM:H1}GOLDEN:X', 'X plane')
        self.assertTrue(len(elem.value) == 2,
                        "element: %s, %s" % (elem.name, elem._field['value']))
        val = elem.x
	self.assertTrue(abs(val) > 0)
        elem.x = 0.01
        time.sleep(2)
        #print "val and new x", val, elem.x
        self.assertTrue(abs(elem.x) > 10*abs(val)) 

    def test_pv(self):
        elem = element.Element(
            name = 'V:BPM', eget = caget, eput = caput,
            index = -1, devname = 'BPM')
        elem.addEGet('SR:C29-BI:G06B{BPM:H1}SA:Y-I')
        elem.addEGet('SR:C29-BI:G06B{BPM:H1}SA:X-I')
        elem.setFieldGetAction('x', 'SR:C29-BI:G06B{BPM:H1}SA:X-I', 'X plane')
        elem.setFieldPutAction('x', 'SR:C29-BI:G06B{BPM:H1}GOLDEN:X', 'X plane')

        elem.updateCfsTags('SR:C29-BI:G06B{BPM:H1}SA:X-I', ['aphla.X', 'aphla.EGET'])

        pv = elem._pv_tags(["aphla.X"])
        #print pv
        #print elem._pv_fields(["x"])
        self.assertTrue(len(pv) == 1)
        pv = elem.pv(field = "x", handle="readback")
        self.assertTrue(len(pv) == 1)
        pv = elem.pv(field = "x", handle="setpoint")
        self.assertTrue(len(pv) == 1)

if __name__ == "__main__":
    unittest.main()

