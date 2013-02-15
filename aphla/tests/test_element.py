"""
Unit Test: element
-------------------
"""

# :author: Lingyun Yang <lyyang@bnl.gov>

import sys, os, time

if sys.version_info[:2] == (2, 6):
    import unittest2 as unittest
elif sys.version_info[:2] == (2,7):
    import unittest

import numpy as np

from aphla import element
import pickle, shelve


class TestElement(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_dcct_l0(self):
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

    def test_bpm_l0(self):
        pvx0 = 'SR:C29-BI:G06B{BPM:H1}SA:X-I'
        pvy0 = 'SR:C29-BI:G06B{BPM:H1}SA:Y-I'
        pvxbba = 'SR:C29-BI:G06B{BPM:H1}BBA:X'
        pvybba = 'SR:C29-BI:G06B{BPM:H1}BBA:Y'
        pvxgold = 'SR:C29-BI:G06B{BPM:H1}GOLDEN:X'
        pvygold = 'SR:C29-BI:G06B{BPM:H1}GOLDEN:Y'

        bpm = element.CaElement(name = 'PH1G6C29B',
            index = -1, devname = 'PH1G6C29B', family = 'BPM')
        bpm.updatePvRecord(pvx0, {'field':'x[0]'})
        bpm.updatePvRecord(pvy0, {'field':'y[0]'})
        bpm.updatePvRecord(pvxbba, {'field':'xref[0]'})
        bpm.updatePvRecord(pvybba, {'field':'yref[0]'})
        bpm.updatePvRecord(pvxgold, {'field':'xref[1]'})
        bpm.updatePvRecord(pvygold, {'field':'yref[1]'})

        self.assertEqual(bpm.pv(field='xref'), [pvxbba, pvxgold])
        self.assertEqual(bpm.index, -1)
        self.assertFalse(bpm.virtual)
        self.assertEqual(bpm.virtual, 0)
        

    def test_hcor_l0(self):
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
        hcor.updatePvRecord(pvrb, {'handle': 'readback', 'field': 'x'})
        hcor.updatePvRecord(pvsp, {'handle': 'setpoint', 'field': 'x'})
        self.assertEqual(hcor.pv(field='x', handle='readback'), [pvrb])
        self.assertEqual(hcor.pv(field='x', handle='setpoint'), [pvsp])
        self.assertIsNone(hcor.stepSize('x'))
        self.assertIsNone(hcor.boundary('x')[0])
        self.assertIsNone(hcor.boundary('x')[1])
        
        self.assertEqual(hcor.pv(field='y'), [])
        self.assertEqual(hcor.pv(field='y', handle='readback'), [])
        self.assertEqual(hcor.pv(field='y', handle='setpoint'), [])


    def __compareElements(self, e1, e2):
        self.assertEqual(sorted(e1.__dict__.keys()), sorted(e2.__dict__.keys()))
        for k,v in e1.__dict__.iteritems():
            v2 = getattr(e2, k)
            self.assertEqual(
                v, v2, "{0} field {1}: {2} != {3}".format(e1.name, k, v,v2))

        
    def test_pickle_l0(self):
        dcct = element.CaElement(
            name = 'CURRENT', index = -1, devname = 'DCCT', family = 'DCCT')
        dcct.updatePvRecord('PV_1', None, ['aphla.eget', 'aphla.sys.SR'])

        pklf = open('test_element.pkl', 'wb')
        pickle.dump(dcct, pklf)
        pklf.close()

        pkl = open('test_element.pkl', 'rb')
        pkl_dcct = pickle.load(pkl)
        pkl.close()

        # dcct
        self.__compareElements(dcct, pkl_dcct)

    def test_shelve_l0(self):
        dcct = element.CaElement(
            name = 'CURRENT', index = -1, devname = 'DCCT', family = 'DCCT')
        dcct.updatePvRecord('PV_1', None, ['aphla.eget', 'aphla.sys.SR'])

        sh = shelve.open('test_element.shelve')
        sh['dcct'] = dcct
        sh.close()

        sh = shelve.open('test_element.shelve', 'r')
        shv_dcct = sh['dcct']
        sh.close()

        # dcct
        self.__compareElements(dcct, shv_dcct)


    def test_sort_l0(self):
        elem1 = element.AbstractElement(name= 'E1', index = 0, sb= 0.0)
        elem2 = element.AbstractElement(name= 'E1', index = 2, sb= 2.0)
        elem3 = element.AbstractElement(name= 'E1', index = 1, sb= 1.0)
        el = sorted([elem1, elem2, elem3])
        self.assertTrue(el[0].sb < el[1].sb)
        self.assertTrue(el[1].sb < el[2].sb)
        

if __name__ == "__main__":
    unittest.main()

