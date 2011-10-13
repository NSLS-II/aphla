#!/usr/bin/env python

import unittest
import sys, os, time
import numpy as np
#import matplotlib.pylab as plt

from conf import *
import element
from catools import caget, caput, Timedout
import pickle, shelve

class TestElement(unittest.TestCase):
    def setUp(self):
        # current
        self.dcct = element.Element(
            name = 'CURRENT', index = -1, devname = 'DCCT', family = 'DCCT')
        self.dcct.addEGet('SR:C00-BI:G00{DCCT:00}CUR-RB')
        self.dcct.updateCfsTags(
            'SR:C00-BI:G00{DCCT:00}CUR-RB', ['aphla.eget', 'aphla.sys.SR'])

        # bpm1
        self.bpm1 = element.Element(name = 'PH1G6C29B',
            index = -1, devname = 'PH1G6C29B', family = 'BPM')
        self.bpm1.addEGet('SR:C29-BI:G06B{BPM:H1}SA:Y-I')
        self.bpm1.addEGet('SR:C29-BI:G06B{BPM:H1}SA:X-I')
        self.bpm1.addEPut('SR:C29-BI:G06B{BPM:H1}GOLDEN:Y')
        self.bpm1.addEPut('SR:C29-BI:G06B{BPM:H1}GOLDEN:X')
        self.bpm1.setFieldGetAction('x', 'SR:C29-BI:G06B{BPM:H1}SA:X-I',
                                    'H plane')
        self.bpm1.setFieldGetAction('y', 'SR:C29-BI:G06B{BPM:H1}SA:Y-I',
                                    'V plane')
        self.bpm1.setFieldPutAction('x', 'SR:C29-BI:G06B{BPM:H1}GOLDEN:X-I',
                                    'H plane')
        self.bpm1.setFieldPutAction('y', 'SR:C29-BI:G06B{BPM:H1}GOLDEN:Y-I',
                                    'V plane')
        self.bpm1.updateCfsTags(
            'SR:C29-BI:G06B{BPM:H1}GOLDEN:X-I',
            ['aphla.offset', 'aphla.eput', 'aphla.x', 'aphla.sys.SR'])
        self.bpm1.updateCfsTags(
            'SR:C29-BI:G06B{BPM:H1}GOLDEN:Y-I',
            ['aphla.offset', 'aphla.eput', 'aphla.y', 'aphla.sys.SR'])
        self.bpm1.updateCfsTags(
            'SR:C29-BI:G06B{BPM:H1}SA:X-I',
            ['aphla.eget', 'aphla.x', 'aphla.sys.SR'])
        self.bpm1.updateCfsTags(
            'SR:C29-BI:G06B{BPM:H1}SA:Y-I',
            ['aphla.eget', 'aphla.y', 'aphla.sys.SR'])

        # bpm2
        self.bpm2 = element.Element(
            name = 'V:BPM:X', index = -1, devname = 'BPM', virtual = 1)
        pvs = ['SR:C01-BI:G06B{BPM:H2}SA:X-I', 'SR:C01-BI:G04B{BPM:M1}SA:X-I',
               'SR:C01-BI:G02A{BPM:L1}SA:X-I', 'SR:C01-BI:G02A{BPM:L2}SA:X-I',
               'SR:C01-BI:G04A{BPM:M1}SA:X-I', 'SR:C01-BI:G06B{BPM:H1}SA:X-I',
               'SR:C01-BI:G06B{BPM:H2}SA:Y-I', 'SR:C01-BI:G04B{BPM:M1}SA:Y-I',
               'SR:C01-BI:G02A{BPM:L1}SA:Y-I', 'SR:C01-BI:G02A{BPM:L2}SA:Y-I',
               'SR:C01-BI:G04A{BPM:M1}SA:Y-I', 'SR:C01-BI:G06B{BPM:H1}SA:Y-I']
        for pv in pvs:
            self.bpm2.addEGet(pv)
            self.bpm2.updateCfsTags(pv, ['aphla.eget'])

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
        self.hcor.setFieldGetAction('x', 'SR:C01-MG:G02A{HCor:L1}Fld-I')
        self.hcor.setFieldPutAction('x', 'SR:C01-MG:G02A{HCor:L1}Fld-SP')
        self.hcorx = caget('SR:C01-MG:G02A{HCor:L1}Fld-I')
        
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

        #
        # pickle objects
        self.pkl = 'utElement.pkl'
        output = open(self.pkl, 'wb')
        # Pickle dictionary using protocol 0.
        pickle.dump(self.dcct, output)
        # Pickle the list using the highest protocol available.
        pickle.dump(self.bpm1, output, -1)
        pickle.dump(self.quad, output)
        output.close()

        # pickle backed shelve
        self.shv = 'utElement.shelve'
        sh = shelve.open(self.shv, 'n')
        sh['dcct'] = self.dcct
        sh['bpm1'] = self.bpm1
        sh['bpm2'] = self.bpm2
        sh['hcor'] = self.hcor
        sh['quad'] = self.quad
        sh.close()

    def tearDown(self):
        #print "reset ", self.hcor.name, self.hcorx
        caput('SR:C01-MG:G02A{HCor:L1}Fld-I', self.hcorx, wait=True)
        #time.sleep(1)

    def test_basicattr(self):
        self.assertTrue(self.dcct.name == 'CURRENT')
        self.assertTrue(self.dcct.family == 'DCCT')

        self.assertTrue(self.bpm1.index == -1)
        self.assertTrue(self.bpm2.virtual)

        # non virtual element
        self.assertFalse(self.bpm1.virtual)
        self.bpm1.virtual = 1
        self.assertTrue(self.bpm1.virtual)
        self.bpm1.virtual = 0

        self.assertTrue(self.hcor.name == 'CXL1G2C01A')
        self.assertTrue(self.hcor.cell == 'C01')
        self.assertTrue(self.hcor.girder == 'G2')
        self.assertTrue(self.hcor.devname == 'CL1G2C01A')
        self.assertTrue(self.hcor.family == 'HCOR')
        self.assertTrue(self.hcor.symmetry == 'A')
        self.assertAlmostEqual(self.hcor.length, 0.2)
        self.assertAlmostEqual(self.hcor.se, 30.6673)

    def compareElements(self, e1, e2):
        self.assertEqual(e1.__dict__.keys(), e2.__dict__.keys())
        for k,v in e1.__dict__.iteritems():
            v2 = getattr(e2, k)
            self.assertEqual(
                v, v2, "{0} field {1}: {2} != {3}".format(e1.name, k, v,v2))

        
    def test_pickle(self):
        pkl = open(self.pkl, 'rb')
        pkl_dcct = pickle.load(pkl)
        pkl_bpm1 = pickle.load(pkl)
        pkl_quad = pickle.load(pkl)
        pkl.close()

        # dcct
        self.compareElements(self.dcct, pkl_dcct)
        self.compareElements(self.bpm1, pkl_bpm1)
        self.compareElements(self.quad, pkl_quad)

    def test_shelve(self):
        sh = shelve.open(self.shv, 'r')
        shv_dcct = sh['dcct']
        shv_bpm1 = sh['bpm1']
        shv_bpm2 = sh['bpm2']
        shv_hcor = sh['hcor']
        shv_quad = sh['quad']
        sh.close()

        # dcct
        self.compareElements(self.dcct, shv_dcct)
        self.compareElements(self.bpm1, shv_bpm1)
        self.compareElements(self.bpm2, shv_bpm2)
        self.compareElements(self.hcor, shv_hcor)
        self.compareElements(self.quad, shv_quad)

    def test_pv(self):
        #print self.bpm1._field['value'].pvsp
        self.assertEqual(len(self.bpm1.pv(tags = ["aphla.x"])), 2)
        self.assertEqual(len(self.bpm1._pvtags.keys()), 4)
        self.assertEqual(len(self.bpm1.pv(field='x')), 2)
        self.assertEqual(len(self.bpm1.pv(field='x', handle='readback')), 1)
        self.assertEqual(len(self.bpm1.pv(field='x', handle='setpoint')), 1)
        self.assertEqual(len(self.bpm1.pv(field='y')), 2)
        self.assertEqual(len(self.bpm1.pv(field='y', handle='readback')), 1)
        self.assertEqual(len(self.bpm1.pv(field='y', handle='setpoint')), 1)
        self.assertEqual(len(self.bpm2.pv(tag = 'aphla.eget')), 12)

    def test_read(self):
        self.assertTrue(self.bpm1.name)
        self.assertTrue(abs(self.quad.value) >= 0)
        self.assertTrue(abs(self.hcor.value) >= 0)

        self.assertTrue(abs(self.bpm1.x) >= 0)
        self.assertTrue(abs(self.bpm1.y) >= 0)

        self.assertTrue(abs(self.hcor.value) >= 0)

    @unittest.expectedFailure
    def test_exception_non(self):
        self.assertRaises(AttributeError, self.readValidField)
        
    def test_exception(self):
        self.assertRaises(AttributeError, self.readInvalidField)
        self.assertRaises(ValueError, self.writeInvalidField)

    def readValidField(self):
        x = self.bpm1.x

    def readInvalidField(self):
        x = self.bpm2.x

    def writeInvalidField(self):
        self.dcct.value = 0

    def test_readwrite(self):
        """
        write the trim, check orbit change
        """
        trim_pvrb = ['SR:C01-MG:G02A{HCor:L1}Fld-I',
                     'SR:C01-MG:G02A{VCor:L2}Fld-I']
        trim_pvsp = ['SR:C01-MG:G02A{HCor:L1}Fld-SP',
                     'SR:C01-MG:G02A{VCor:L2}Fld-SP']
        try:
            trim_v0 = caget(trim_pvrb)
        except Timedout:
            return

        rb1 = self.bpm2.value
        trim_v1 = [v - 1e-5 for v in trim_v0]
        try:
            caput(trim_pvsp, trim_v1, wait=True)
        except Timedout:
            return

        time.sleep(6)
        trim_v2 = caget(trim_pvrb)
        trim_v3 = caget(trim_pvsp)
        for i in range(len(trim_v0)):
            self.assertAlmostEqual(trim_v2[i], trim_v3[i])

        rb2 = self.bpm2.value
        for i in range(len(rb1)):
            self.assertTrue(
                abs(rb1[i] - rb2[i]) > 1e-8,
                'orbit diff  = {0} - {1} = {2}'.format(rb1[i], rb2[i],
                                                      rb1[i] - rb2[i]))

        # restore
        caput(trim_pvsp, trim_v0, wait=True)
        time.sleep(8)
        rb3 = self.bpm2.value
        for i in range(len(rb1)):
            self.assertAlmostEqual(
                rb1[i], rb3[i], 5,
                "orbit {0} = {1}, {2}".format(i, rb1[i], rb3[i]))
        

    def test_sort(self):
        elem1 = element.Element(name= 'E1', sb= 0.0)
        elem2 = element.Element(name= 'E1', sb= 2.0)
        elem3 = element.Element(name= 'E1', sb= 1.0)
        el = sorted([elem1, elem2, elem3])
        self.assertTrue(el[0].sb < el[1].sb)
        self.assertTrue(el[1].sb < el[2].sb)
        
    def test_field(self):
        v0 = self.hcor.x
        pvrb = self.hcor.pv(field='x', handle='readback')[0]
        pvsp = self.hcor.pv(field='x', handle='setpoint')[0]

        caput(pvsp, v0 - 1e-4, wait=True)
        self.assertAlmostEqual(self.hcor.x, v0 - 1e-4)

        caput(pvsp, v0, wait=True)

        self.hcor.x = v0 - 5e-5

        self.assertAlmostEqual(self.hcor.x, v0 - 5e-5)

        self.hcor.x = v0
    
    def test_hcor_bpm(self):
        rb1 = self.bpm2.value
        v0 = self.hcor.x
        v1 = v0 - 1e-4
        try:
            self.hcor.x = v1
            time.sleep(2)
            rb2 = self.bpm2.value
            for i in range(len(rb1)):
                self.assertTrue(
                    abs(rb1[i] - rb2[i]) > 1e-6,
                    'orbit diff {3}  = {0} - {1} = {2}'.format(
                        rb1[i], rb2[i], rb1[i] - rb2[i], i))
        except:
            self.hcor.x = v0

        self.hcor.x = v0

if __name__ == "__main__":
    unittest.main()

