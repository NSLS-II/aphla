#!/usr/bin/env python

import unittest
import sys, os, time
import numpy as np

import aphla as ap

refpvrb = [
    "SR:C15-BI:G02A{BPM:L1}SA:X-I",
    "SR:C15-BI:G02A{BPM:L1}SA:Y-I",
    "SR:C15-BI:G02A{BPM:L2}SA:X-I",
    "SR:C15-BI:G02A{BPM:L2}SA:Y-I",
    "SR:C15-BI:G04A{BPM:M1}SA:X-I",
    "SR:C15-BI:G04A{BPM:M1}SA:Y-I",
    "SR:C15-BI:G04B{BPM:M1}SA:X-I",
    "SR:C15-BI:G04B{BPM:M1}SA:Y-I",
    "SR:C15-BI:G06B{BPM:H1}SA:X-I",
    "SR:C15-BI:G06B{BPM:H1}SA:Y-I",
    "SR:C15-BI:G06B{BPM:H2}SA:X-I",
    "SR:C15-BI:G06B{BPM:H2}SA:Y-I"]

ref_v0 = np.array(ap.caget(refpvrb), 'd')

# the virtual accelerator has a prefix of 'V\d+'
VSUB = 'V1'

def markForStablePv():
    global ref_v0, refpvrb
    ref_v0 = np.array(ap.caget(refpvrb), 'd')
    
def waitForStablePv(**kwargs):
    """
    wait for the orbit to be stable.

    This is in hlalib.py, but here does not need the dependance on getOrbit().
    """
    diffstd = kwargs.get('diffstd', 1e-7)
    minwait = kwargs.get('minwait', 2)
    maxwait = kwargs.get('maxwait', 30)
    step    = kwargs.get('step', 2)
    diffstd_list = kwargs.get('diffstd_list', False)
    verbose = kwargs.get('verbose', 0)

    t0 = time.time()
    time.sleep(minwait)
    global ref_v0
    dv = np.array(caget(refpvrb)) - ref_v0
    dvstd = [dv.std()]  # record the history
    timeout = False

    while dv.std() < diffstd:
        time.sleep(step)
        dt = time.time() - t0
        if dt  > maxwait:
            timeout = True
            break
        dv = np.array(caget(refpvrb)) - ref_v0
        dvstd.append(dv.std())

    if diffstd_list:
        return timeout, dvstd

class TestElement(unittest.TestCase):
    def setUp(self):
        ap.initNSLS2V1()
        pass 
        
    def tearDown(self):
        pass

    def test_tune(self):
        tune, = ap.getElements('TUNE')
        nux, nuy = tune.x, tune.y
        val = tune.value
        self.assertTrue(len(val), 2)
        self.assertAlmostEqual(nux, val[0])
        self.assertAlmostEqual(nuy, val[1])
        
    def test_dcct(self):
        dccts = ap.getElements('DCCT')
        self.assertEqual(len(dccts), 1)
        dcct = dccts[0]
        # current
        pv = u'SR:C00-BI:G00{DCCT:00}CUR-RB'
        vsrtag = 'aphla.sys.' + VSUB + 'SR'
        self.assertEqual(dcct.name,    'DCCT')
        self.assertEqual(dcct.devname, 'DCCT')
        self.assertEqual(dcct.family,  'DCCT')
        self.assertEqual(len(dcct.pv()), 1)
        self.assertEqual(dcct.pv(tag='aphla.eget'), [pv])
        self.assertEqual(dcct.pv(tag=vsrtag), [pv])
        self.assertEqual(dcct.pv(tags=['aphla.eget', vsrtag]), [pv])

        self.assertIn('value', dcct.fields())
        self.assertGreater(dcct.value, 1.0)
        self.assertLess(dcct.value, 600.0)

        self.assertGreater(ap.eget('DCCT'), 1.0)

    def test_bpm(self):
        bpms = ap.getElements('BPM')
        self.assertEqual(len(bpms), 180)

        bpm = bpms[0]
        #self.assertEqual(bpm.pv(field='xref'), [pvxbba, pvxgold])
        self.assertGreater(bpm.index, 1)
        self.assertFalse(bpm.virtual)
        self.assertEqual(bpm.virtual, 0)
        self.assertEqual(len(ap.eget(bpm.name)), 2)

    def test_vbpm(self):
        vbpm = ap.getElements('HLA:VBPM', return_list=False, include_virtual=True)
        self.assertIsNotNone(vbpm)
        self.assertIn('x', vbpm.fields())
        self.assertIn('y', vbpm.fields())

        bpms = ap.getElements('BPM')
        nbpm = len(bpms)
        self.assertEqual(len(vbpm.x), nbpm)
        self.assertEqual(len(vbpm.y), nbpm)
        self.assertEqual(len(vbpm.sb), nbpm)
        self.assertGreater(np.std(vbpm.x), 0.0)
        self.assertGreater(np.std(vbpm.y), 0.0)

    def test_local_bump(self):
        bpm = ap.getElements('P*C1[0-3]*')
        trim = ap.getGroupMembers(['*', '[HV]COR'], op='intersection')
        v0 = ap.getOrbit('P*', spos=True)
        ap.correctOrbit([e.name for e in bpm], [e.name for e in trim])
        time.sleep(4)
        v1 = ap.getOrbit('P*', spos=True)
        import matplotlib.pylab as plt
        plt.clf()
        ax = plt.subplot(211) 
        fig = plt.plot(v0[:,-1], v0[:,0], 'r-x', label='X') 
        fig = plt.plot(v0[:,-1], v0[:,1], 'g-o', label='Y')
        ax = plt.subplot(212)
        fig = plt.plot(v1[:,-1], v1[:,0], 'r-x', label='X')
        fig = plt.plot(v1[:,-1], v1[:,1], 'g-o', label='Y')
        plt.savefig("test_nsls2_orbit_correct.png")

    @unittest.skip
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
        print self.hcor._field['x'].pvrb
        print self.hcor._field['x'].pvsp

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

