#!/usr/bin/env python

import unittest
import sys, os, time
import numpy as np

from aphla import element
from aphla.catools import caget, caput, Timedout
import pickle, shelve


class TestElement(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_dcct(self):
        # current
        pv = u'SR:C00-BI:G00{DCCT:00}CUR-RB'
        dcct = element.CaElement(
            name = 'CURRENT', index = -1, devname = 'DCCT', family = 'DCCT')
        dcct.updatePvRecord(pv, None, ['aphla.eget', 'aphla.sys.SR'])

        self.assertEqual(dcct.name,    'CURRENT')
        self.assertEqual(dcct.devname, 'DCCT')
        self.assertEqual(dcct.family,  'DCCT')
        self.assertEqual(len(dcct.pv()), 1)
        self.assertEqual(dcct.pv(tag='aphla.eget'), [pv])
        self.assertEqual(dcct.pv(tag='aphla.sys.SR'), [pv])
        self.assertEqual(dcct.pv(tags=['aphla.eget', 'aphla.sys.SR']), [pv])

    def test_bpm(self):
        pvx0 = 'SR:C29-BI:G06B{BPM:H1}SA:X-I'
        pvy0 = 'SR:C29-BI:G06B{BPM:H1}SA:Y-I',
        pvxbba = 'SR:C29-BI:G06B{BPM:H1}BBA:X'
        pvybba = 'SR:C29-BI:G06B{BPM:H1}BBA:Y'
        pvxgold = 'SR:C29-BI:G06B{BPM:H1}GOLDEN:X'
        pvygold = 'SR:C29-BI:G06B{BPM:H1}GOLDEN:Y'

        bpm = element.CaElement(name = 'PH1G6C29B',
            index = -1, devname = 'PH1G6C29B', family = 'BPM')
        bpm.updatePvRecord(pvx0, None, ['aphla.elemfield.x[0]'])
        bpm.updatePvRecord(pvy0, None, ['aphla.elemfield.y[0]'])
        bpm.updatePvRecord(pvxbba, None, ['aphla.elemfield.xref[0]'])
        bpm.updatePvRecord(pvybba, None, ['aphla.elemfield.yref[0]'])
        bpm.updatePvRecord(pvxgold, None, ['aphla.elemfield.xref[1]'])
        bpm.updatePvRecord(pvygold, None, ['aphla.elemfield.yref[1]'])

        self.assertEqual(bpm.pv(field='xref'), [pvxbba, pvxgold])
        self.assertEqual(bpm.index, -1)
        self.assertFalse(bpm.virtual)
        self.assertEqual(bpm.virtual, 0)

    def test_hcor(self):
        # hcor
        hcor = element.CaElement(
            name = 'CXL1G2C01A', index = 125, cell = 'C01',
            devname = 'CL1G2C01A', family = 'HCOR', girder = 'G2', length = 0.2,
            se = 30.6673, symmetry = 'A')

        self.assertTrue(hcor.name == 'CXL1G2C01A')
        self.assertTrue(hcor.cell == 'C01')
        self.assertTrue(hcor.girder == 'G2')
        self.assertTrue(hcor.devname == 'CL1G2C01A')
        self.assertTrue(hcor.family == 'HCOR')
        self.assertTrue(hcor.symmetry == 'A')
        self.assertAlmostEqual(hcor.length, 0.2)
        self.assertAlmostEqual(hcor.se, 30.6673)

        pvrb = 'SR:C01-MG:G02A{HCor:L1}Fld-I'
        pvsp = 'SR:C01-MG:G02A{HCor:L1}Fld-SP'
        hcor.updatePvRecord(pvrb, 
                            {'handle': 'READBACK'}, 
                            ['aphla.elemfield.x'])
        hcor.updatePvRecord(pvsp, 
                            {'handle': 'SETPOINT'}, 
                            ['aphla.elemfield.x'])
        self.assertEqual(hcor.pv(field='x', handle='readback'), [pvrb])
        self.assertEqual(hcor.pv(field='x', handle='setpoint'), [pvsp])

        self.assertEqual(hcor.pv(field='y'), [])
        self.assertEqual(hcor.pv(field='y', handle='readback'), [])
        self.assertEqual(hcor.pv(field='y', handle='setpoint'), [])
        

    def compareElements(self, e1, e2):
        self.assertEqual(e1.__dict__.keys(), e2.__dict__.keys())
        for k,v in e1.__dict__.iteritems():
            v2 = getattr(e2, k)
            self.assertEqual(
                v, v2, "{0} field {1}: {2} != {3}".format(e1.name, k, v,v2))

        
    @unittest.skip
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

    @unittest.skip
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

    @unittest.skip
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

    @unittest.skip
    def test_read(self):
        #print self.hcor._field['x'].pvrb
        #print self.hcor._field['x'].pvsp

        self.assertTrue(self.bpm1.name)

        #self.assertTrue(abs(self.quad.value) >= 0)
        self.assertTrue(abs(self.hcor.x) >= 0)

        print "bpm", self.bpm1._field['x'].pvrb
        self.assertTrue(abs(self.bpm1.x) >= 0)
        self.assertTrue(abs(self.bpm1.y) >= 0)
        print self.bpm1.fields()
        if 'xref' in self.bpm1.fields(): print self.bpm1.xref
        if 'yref' in self.bpm1.fields(): print self.bpm1.yref
        self.assertTrue(abs(self.hcor.x) >= 0)

    @unittest.skip
    def test_exception_non(self):
        self.assertRaises(AttributeError, self.readValidField)
        
    @unittest.skip
    def test_exception(self):
        self.assertRaises(AttributeError, self.readInvalidField)
        self.assertRaises(ValueError, self.writeInvalidField)

    @unittest.skip
    def readValidField(self):
        x = self.bpm1.x

    @unittest.skip
    def readInvalidField(self):
        x = self.bpm2.x

    @unittest.skip
    def writeInvalidField(self):
        self.dcct.value = 0

    @unittest.skip
    def test_readwrite(self):
        """
        write the trim, check orbit change
        """
        #print "\n\nStart",
        trim_pvrb = ['SR:C01-MG:G02A{HCor:L1}Fld-I',
                     'SR:C01-MG:G02A{VCor:L2}Fld-I']
        trim_pvsp = ['SR:C01-MG:G02A{HCor:L1}Fld-SP',
                     'SR:C01-MG:G02A{VCor:L2}Fld-SP']
        #print "yes", caget(trim_pvrb),
        try:
            trim_v0 = caget(trim_pvrb)
        except Timedout:
            return
        #print trim_v0

        rb1 = self.bpm2.value
        #print "Initial trim: ", trim_v0, rb1

        markForStablePv()
        trim_v1 = [v - 2e-5 for v in trim_v0]
        try:
            caput(trim_pvsp, trim_v1, wait=True)
        except Timedout:
            return

        waitForStablePv(minwait=5)
        trim_v2 = caget(trim_pvrb)
        trim_v3 = caget(trim_pvsp)
        for i in range(len(trim_v0)):
            self.assertAlmostEqual(trim_v2[i], trim_v3[i])

        rb2 = self.bpm2.value
        for i in range(len(rb1)):
            self.assertTrue(
                abs(rb1[i] - rb2[i]) > 1e-8,
                'orbit diff {0} = {1} - {2} = {3}'.format(
                    i, rb1[i], rb2[i], rb1[i] - rb2[i]))

        markForStablePv()
        # restore
        caput(trim_pvsp, trim_v0, wait=True)
        waitForStablePv(minwait=5)
        rb3 = self.bpm2.value
        #print rb3, self.bpm2.value
        #print "Final trim:", caget(trim_pvrb), caget(trim_pvsp)
        for i in range(len(rb1)):
            self.assertAlmostEqual(
                rb1[i], rb3[i], 5,
                "orbit {0} = {1} -> {2} -> {3}".format(
                    i, rb1[i], rb2[i], rb3[i]))
        

    @unittest.skip
    def test_sort(self):
        elem1 = element.Element(name= 'E1', sb= 0.0)
        elem2 = element.Element(name= 'E1', sb= 2.0)
        elem3 = element.Element(name= 'E1', sb= 1.0)
        el = sorted([elem1, elem2, elem3])
        self.assertTrue(el[0].sb < el[1].sb)
        self.assertTrue(el[1].sb < el[2].sb)
        
    @unittest.skip
    def test_field(self):
        v0, = self.hcor.x
        pvrb = self.hcor.pv(field='x', handle='readback')[0]#.encode('ascii')
        pvsp = self.hcor.pv(field='x', handle='setpoint')[0]#.encode('ascii')
        #print pvrb, pvsp
        # PV from channel finder is UTF8 encoded
        caput(pvsp, v0 - 1e-4, wait=True)
        v1a = self.hcor.x
        v1b = caget(pvsp)
        self.assertAlmostEqual(v1a, v1b, 7)
        self.assertAlmostEqual(v1b, v0 - 1e-4, 7,
            "pv={0} {1} != {2}".format(pvsp, v1b, v0 - 1e-4))
        self.assertAlmostEqual(v1a, v0 - 1e-4)

        # 
        caput(pvsp, v0, wait=True)

        self.hcor.x = v0 - 5e-5

        self.assertAlmostEqual(self.hcor.x, v0 - 5e-5)

        self.hcor.x = v0
    
    @unittest.skip
    def test_hcor_bpm(self):
        rb1 = self.bpm2.value
        v0 = self.hcor.x
        v1 = v0 - 1e-4
        try:
            markForStablePv()
            self.hcor.x = v1
            waitForStablePv()
            rb2 = self.bpm2.value
            for i in range(len(rb1)):
                self.assertTrue(
                    abs(rb1[i] - rb2[i]) > 1e-6,
                    'orbit diff {3}  = {0} - {1} = {2}'.format(
                        rb1[i], rb2[i], rb1[i] - rb2[i], i))
        except:
            self.hcor.x = v0

        markForStablePv()
        self.hcor.x = v0
        waitForStablePv(minwait=4)

if __name__ == "__main__":
    unittest.main()

