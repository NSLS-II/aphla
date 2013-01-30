#!/usr/bin/env python

"""
Unit Test: NSLS2 V3 BSR+3SR 
---------------------------
"""

# :author: Lingyun Yang <lyyang@bnl.gov>

import sys, os, time
from fnmatch import fnmatch

if sys.version_info[:2] == (2, 6):
    import unittest2 as unittest
elif sys.version_info[:2] == (2,7):
    import unittest

import numpy as np
import random

import logging
logging.basicConfig(filename="utest.log",
    format='%(asctime)s - %(name)s [%(levelname)s]: %(message)s',
    level=logging.DEBUG)


logging.info("initializing NSLS2V3")
import aphla as ap
ap.machines.init("nsls2v3bsrline")

logging.info("'nsls2v3bsrline' initialized")

#class Test0(unittest.TestCase):
#    def setUp(self):
#        pass
#
#    def test_l0(self):
#        self.assertEqual(0, 1)

"""
Element
~~~~~~~
"""

class Test0Element(unittest.TestCase):
    def setUp(self):
        ap.machines.use("V3BSRLINE")
        pass 
        
    def tearDown(self):
        pass

    def test_bpm_l0(self):
        bpms = ap.getElements('BPM')
        self.assertGreaterEqual(len(bpms), 180*3)

        for i in range(1, len(bpms)):
            self.assertGreater(bpms[i].sb, bpms[i-1].sb)
            self.assertGreater(bpms[i].se, bpms[i-1].se)

        bpm = bpms[0]
        #self.assertEqual(bpm.pv(field='xref'), [pvxbba, pvxgold])
        self.assertGreater(bpm.index, 1)
        self.assertFalse(bpm.virtual)
        self.assertEqual(bpm.virtual, 0)
        #self.assertEqual(len(bpm.value), 2)

        self.assertIn('x', bpm.fields())
        self.assertIn('y', bpm.fields())
        self.assertEqual(len(bpm.get(['x', 'y'], unit=None)), 2)
        self.assertEqual(len(ap.eget('BPM', 'x', unit=None)), len(bpms))
        self.assertEqual(len(ap.eget('BPM', ['x', 'y'], unit=None)), len(bpms))

        self.assertGreater(ap.getDistance(bpms[0].name, bpms[1].name), 0.0)

    def test_vbpm(self):
        vbpms = ap.getElements('HLA:VBPM', include_virtual=True)
        self.assertIsNotNone(vbpms)
        vbpm = vbpms[0]
        self.assertIn('x', vbpm.fields())
        self.assertIn('y', vbpm.fields())

        bpms = ap.getElements('BPM')
        nbpm = len(bpms)
        self.assertEqual(len(vbpm.x), nbpm)
        self.assertEqual(len(vbpm.y), nbpm)
        self.assertEqual(len(vbpm.sb), nbpm)
        #print vbpm.x, np.std(vbpm.x)
        #print vbpm.y, np.std(vbpm.y)
        self.assertGreaterEqual(np.std(vbpm.x), 0.0)
        self.assertGreaterEqual(np.std(vbpm.y), 0.0)

    def test_hcor(self):
        # hcor
        hcor = ap.element.CaElement(
            name = 'cxl1g2c01a', index = 125, cell = 'C01',
            devname = 'cl1g2c01a', family = 'HCOR', girder = 'G2', length = 0.2,
            sb = 30.4673, se = 30.6673, symmetry = 'A')

        self.assertTrue(hcor.name == 'cxl1g2c01a')
        self.assertTrue(hcor.cell == 'C01')
        self.assertTrue(hcor.girder == 'G2')
        self.assertTrue(hcor.devname == 'cl1g2c01a')
        self.assertTrue(hcor.family == 'HCOR')
        self.assertTrue(hcor.symmetry == 'A')


        self.assertAlmostEqual(hcor.length, 0.2)
        self.assertAlmostEqual(hcor.sb, 30.4673)
        self.assertAlmostEqual(hcor.se, 30.6673)

        pvrb = 'SR:C01-MG:G02A{HCor:L1}Fld-I'
        pvsp = 'SR:C01-MG:G02A{HCor:L1}Fld-SP'
        hcor.updatePvRecord(pvrb, {'handle': 'readback', 'field': 'x'})
        hcor.updatePvRecord(pvsp, {'handle': 'setpoint', 'field': 'x'}) 

        self.assertIn('x', hcor.fields())
        self.assertEqual(hcor.pv(field='x', handle='readback'), [pvrb])
        self.assertEqual(hcor.pv(field='x', handle='setpoint'), [pvsp])

        self.assertEqual(hcor.pv(field='y'), [])
        self.assertEqual(hcor.pv(field='y', handle='readback'), [])
        self.assertEqual(hcor.pv(field='y', handle='setpoint'), [])
        

    def test_chained_quad(self):
        pvs = ['V:3-BSR-MG{QL3G2C29A_T1:3694}Fld:I', 
               'V:3-BSR-MG{QL3G2C29A_T2:7304}Fld:I', 
               'V:3-BSR-MG{QL3G2C29A_T3:10914}Fld:I']
        qs = ap.getElements('ql3g2c29a')
        self.assertEqual(len(qs), 1)
        k1 = ap.caget(pvs)
        self.assertLess(k1[1]/k1[0] - 1.0, 0.005)
        self.assertLess(k1[2]/k1[0] - 1.0, 0.005)

        qs[0].k1 = k1[0] * (1+0.01)
        k1b = ap.caget(pvs)
        self.assertGreater(qs[0].k1 / k1[0] - 1, 0.005)
        self.assertLess(k1b[1]/k1b[0] - 1.0, 0.005)
        self.assertLess(k1b[2]/k1b[0] - 1.0, 0.005)
   

"""
Lattice
-------------
"""

class Test0Lattice(unittest.TestCase):
    """
    Lattice testing
    """
    def setUp(self):
        logging.info("TestLattice")
        ap.machines.use("V3BSRLINE")
        # this is the internal default lattice
        self.lat = ap.machines.getLattice('V3BSRLINE')
        self.assertTrue(self.lat)
        self.logger = logging.getLogger('tests.TestLattice')

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
        velem = ap.machines.HLA_VFAMILY
        elem = self.lat.getElementList(velem)
        self.assertTrue(elem)
        #elem = self.lat.getElementList(velem, 
        self.assertTrue(self.lat.hasGroup(ap.machines.HLA_VFAMILY))
        vbpm = elem[0]
        for i in range(1, len(vbpm.sb)):
            self.assertGreaterEqual(vbpm.sb[i], vbpm.sb[i-1], 
                "'{0}':{2} is not after '{1}':{3} with sb".format(vbpm._name[i], vbpm._name[i-1],
                     vbpm.sb[i], vbpm.sb[i-1]))
            self.assertGreaterEqual(vbpm.se[i], vbpm.se[i-1],
                "'{0}' is not after '{1}' with se".format(vbpm._name[i], vbpm._name[i-1]))

    def test_getelements(self):
        elems = self.lat.getElementList('BPM')
        self.assertGreater(len(elems), 0)
        

    def test_locations(self):
        elem1 = self.lat.getElementList('*')
        for i in range(1, len(elem1)):
            if elem1[i-1].virtual: continue
            if elem1[i].virtual: continue
            #self.assertGreaterEqual(elem1[i].sb, elem1[i-1].sb,
            #                        msg="{0}({4},sb={1})<{2}({5}, sb={3}), d={6}".format(
            #                            elem1[i].name, elem1[i].sb, 
            #                            elem1[i-1].name, elem1[i-1].sb,
            #                            elem1[i].index, elem1[i-1].index,
            #                            elem1[i].sb - elem1[i-1].sb))
            self.assertGreaterEqual(elem1[i].sb - elem1[i-1].sb, -1e-9,
                                    msg="{0}({4},sb={1})<{2}({5}, sb={3}), d={6}".format(
                                        elem1[i].name, elem1[i].sb, 
                                        elem1[i-1].name, elem1[i-1].sb,
                                        elem1[i].index, elem1[i-1].index,
                                        elem1[i].sb - elem1[i-1].sb))
            
            self.assertGreaterEqual(elem1[i].se, elem1[i-1].sb,
                                    "{0}({4},se={1})<{2}(sb={3})".format(
                    elem1[i].name, elem1[i].se, elem1[i-1].name, elem1[i-1].sb, 
                    i))

        elem1 = self.lat.getElementList('BPM')
        for i in range(1, len(elem1)):
            self.assertGreaterEqual(elem1[i].sb, elem1[i-1].sb,
                                    "%f (%s) %f (%s)" % (
                    elem1[i].sb, elem1[i].name,
                    elem1[i-1].sb, elem1[i-1].name))
            
        elem1 = self.lat.getElementList('QUAD')
        for i in range(1, len(elem1)):
            self.assertGreaterEqual(elem1[i].sb, elem1[i-1].sb,
                                    "%f (%s) %f (%s)" % (
                    elem1[i].sb, elem1[i].name,
                    elem1[i-1].sb, elem1[i-1].name))
        

    def test_groups(self):
        grp = 'HLATEST'
        self.assertFalse(self.lat.hasGroup(grp))
        self.lat.addGroup(grp)
        self.assertTrue(self.lat.hasGroup(grp))

        #with self.assertRaises(ValueError) as ve:
        #    self.lat.addGroupMember(grp, 'A')
        #self.assertEqual(ve.exception, ValueError)

        self.lat.removeGroup(grp)
        self.assertFalse(self.lat.hasGroup(grp))

        
class Test1LatticeSr(unittest.TestCase):
    def setUp(self):
        logging.info("TestLatticeSr")
        self.lat = ap.machines.getLattice('V3BSRLINE')
        self.logger = logging.getLogger('tests.TestLatticeSr')
        pass

    def test_hvcors_l0(self):
        hc = self.lat.getElementList("HCOR")
        self.assertEqual(len(hc), 188)

    def test_groups_l0(self):
        #self.assertEqual(0, 1)
        g = self.lat.getGroups()
        self.assertGreater(len(g), 0)
        #self.assertEqual(len(g), 0)
        self.assertIn('HCOR', g)
        self.assertIn('VCOR', g)
        self.assertNotIn('TRIM', g)
        self.assertNotIn('TRIMX', g)
        self.assertNotIn('TRIMY', g)


    def test_orbit(self):
        v = ap.getOrbit()

    @unittest.skip("no tunes for line")
    def test_tunes(self):
        tune, = self.lat.getElementList('tune')
        self.assertTrue(abs(tune.x) > 0)
        self.assertTrue(abs(tune.y) > 0)
        
    @unittest.skip("no DCCT for line")
    def test_current(self):
        self.assertTrue(self.lat.hasElement('dcct'))
        
        cur1a = self.lat['dcct']
        cur1b, = self.lat.getElementList('dcct')
        self.assertLessEqual(cur1a.sb, 0.0)
        self.assertGreater(cur1a.value, 0.0)
        self.assertGreater(cur1b.value, 0.0)

    def test_lines(self):
        elem1 = self.lat.getElementList('DIPOLE')
        s0, s1 = elem1[0].sb, elem1[0].se
        i = self.lat._find_element_s((s0+s1)/2.0)
        self.assertTrue(i >= 0)
        i = self.lat.getLine(srange=(0, 25))
        self.assertGreater(len(i), 1)

    def test_getelements_sr(self):
        elems = self.lat.getElementList(['pl1g2c01a', 'pl2g2c01a'])
        self.assertTrue(len(elems) == 2)
        
        # only cell 1,3,5,7,9 and PL1, PL2
        elems = self.lat.getElementList('pl*g2c0*_t1')
        self.assertEqual(len(elems), 10, msg="{0}".format(elems))

    def test_groupmembers(self):
        bpm1 = self.lat.getElementList('BPM')
        g2a = self.lat.getElementList('G2')
        
        b1 = self.lat.getGroupMembers(['BPM', 'C20'], op='intersection')
        self.assertEqual(len(b1), 6*3)
        
        b1 = self.lat.getGroupMembers(['BPM', 'G2'], op='union')
        self.assertGreater(len(b1), len(bpm1))
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
        self.assertEqual(len(el1), 4*3)

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
            # the new setting has H/V COR combined. H/V COR is a group name now
            #else:
            #    self.assertTrue(False,
            #"AttributeError exception expected")



class TestLatticeLtb(unittest.TestCase):
    def setUp(self):
        logging.info("TestLatticeLtb")
        ap.machines.use("V3BSRLINE")
        self.lat  = ap.machines.getLattice('V3BSRLINE')
        self.assertTrue(self.lat)
        self.logger = logging.getLogger('tests.TestLatticeLtb')

    def readInvalidFieldY(self, e):
        k = e.y
        
    def test_field(self):
        bpmlst = self.lat.getElementList('BPM')
        self.assertGreater(len(bpmlst), 0)
        
        elem = bpmlst[0]
        self.assertGreaterEqual(abs(elem.x), 0)
        self.assertGreaterEqual(abs(elem.y), 0)

        hcorlst = self.lat.getElementList('COR')
        self.assertGreater(len(hcorlst), 0)
        for e in hcorlst: 
            self.logger.warn("Skipping 'x' of %s" % e.name)
            #self.assertGreaterEqual(abs(e.x), 0.0)
            #k = e.x
            #e.x = k + 1e-10
            #self.assertGreaterEqual(abs(e.x), 0.0)
            pass

    def test_virtualelements(self):
        pass

class TestNSLS2V2(unittest.TestCase):
    def setUp(self):
        ap.machines.use("V3BSRLINE")
        pass

    def test_elements(self):
        el = ap.getElements(['AA'])
        self.assertEqual(len(el), 1)
        self.assertIsNone(el[0])


"""
Orbit
~~~~~~
"""

class TestOrbit(unittest.TestCase):
    """
    Tested:

    - orbit dimension
    """

    def setUp(self):
        ap.machines.use("V3BSRLINE")
        self.logger = logging.getLogger("tests.TestOrbit")
        self.lat = ap.machines.getLattice('V3BSRLINE')
        self.assertTrue(self.lat)

    def tearDown(self):
        self.logger.info("tearDown")
        pass
        
    def test_orbit_read(self):
        self.logger.info("reading orbit")    
        self.assertGreater(len(ap.getElements('BPM')), 0)
        bpm = ap.getElements('BPM')
        for i,e in enumerate(bpm):
            self.assertGreaterEqual(abs(e.x), 0)
            self.assertGreaterEqual(abs(e.y), 0)

        v = ap.getOrbit()
        self.assertGreater(len(v), 0)
        v = ap.getOrbit('*')
        self.assertGreater(len(v), 0)
        v = ap.getOrbit('p[lhm]*')
        self.assertGreater(len(v), 0)

    @unittest.skip
    def test_orbit_bump(self):
        v0 = ap.getOrbit()
        bpm = ap.getElements('BPM')
        hcor = ap.getElements('HCOR')
        hcor1 = ap.getElements('cx*')
        vcor = ap.getElements('VCOR')
        vcor1 = ap.getElements('cy*')
        #for e in hcor:
        #    print e.name, e.pv(field='x')

        self.assertGreater(len(v0), 0)
        self.assertGreaterEqual(len(bpm), 180)
        self.assertEqual(len(hcor1), 180)
        self.assertGreaterEqual(len(hcor), 180)
        self.assertEqual(len(vcor1), 180)
        self.assertGreaterEqual(len(vcor), 180)

        # maximum deviation
        mx, my = max(abs(v0[:,0])), max(abs(v0[:,1]))
        ih = np.random.randint(0, len(hcor), 3)
        iv = np.random.randint(0, len(vcor), 4)

        for i in ih: hcor[i].x = hcor[i].x+np.random.rand()*1e-6
        for i in iv: vcor[i].y = vcor[i].y+np.random.rand()*1e-6

        ap.hlalib.waitStableOrbit(v0, minwait=5)

        v1 = ap.getOrbit()
        self.assertNotEqual(np.std(v1[:,0]), np.std(v0[:,0]))
        self.logger.info("resetting trims")
        ap.hlalib._reset_trims()
        time.sleep(10)

class TestOrbitControl(unittest.TestCase): 
    def setUp(self):
        ap.machines.use("V2SR")

    def tearDown(self):
        ap.hlalib._reset_trims()

    @unittest.skip("orm data is not ready")
    def test_correct_orbit(self):
        ap.hlalib._reset_trims()

        # a list of horizontal corrector
        hcor = ap.getElements('HCOR')
        hcor_v0 = [e.x for e in hcor]
        # a list of vertical corrector
        vcor = ap.getElements('VCOR')
        vcor_v0 = [e.y for e in vcor]

        bpm = ap.getElements('BPM')
        bpm_v0 = np.array([(e.x, e.y) for e in bpm], 'd')

        norm0 = (np.linalg.norm(bpm_v0[:,0]), np.linalg.norm(bpm_v0[:,1]))

        ih = np.random.randint(0, len(hcor), 4)
        for i in ih:
            hcor[i].x = np.random.rand() * 1e-5

        iv = np.random.randint(0, len(vcor), 4)
        for i in iv:
            vcor[i].y = np.random.rand() * 1e-5

        #raw_input("Press Enter to correct orbit...")
        time.sleep(4)

        cor = []
        #cor.extend([e.name for e in hcor])
        #cor.extend([e.name for e in vcor])
        cor.extend([hcor[i].name for i in ih])
        cor.extend([vcor[i].name for i in iv])

        bpm_v1 = np.array([(e.x, e.y) for e in bpm], 'd')
        norm1 = (np.linalg.norm(bpm_v1[:,0]), np.linalg.norm(bpm_v1[:,1]))

        self.assertGreater(norm1[0], norm0[0])

        ap.correctOrbit([e.name for e in bpm], cor)
        ap.correctOrbit(bpm, cor)

        #raw_input("Press Enter to recover orbit...")
        bpm_v2 = np.array([(e.x, e.y) for e in bpm], 'd')
        #print "Euclidian norm:", 
        norm2 = (np.linalg.norm(bpm_v2[:,0]), np.linalg.norm(bpm_v2[:,1]))
        self.assertLess(norm2[0], norm1[0])
        self.assertLess(norm2[1], norm1[1])

        for i in ih:
            hcor[i].x = hcor_v0[i]

        for i in iv:
            vcor[i].y = vcor_v0[i]

        time.sleep(4)
        #raw_input("Press Enter ...")
        bpm_v3 = np.array([(e.x, e.y) for e in bpm], 'd')
        #print "Euclidian norm:", 
        norm3 = (np.linalg.norm(bpm_v3[:,0]), np.linalg.norm(bpm_v3[:,1]))
        self.assertLess(norm3[0], norm1[0])
        self.assertLess(norm3[0], norm1[0])

        #for i in range(len(ih)):
        #    x, y = hcor[ih[i]].x, vcor[iv[i]].y
        #    print i, (x - hcor_v0[ih[i]]), (y - vcor_v0[iv[i]])

    @unittest.skip("orm data is not ready")
    def test_local_bump(self):
        hcor = ap.getElements('HCOR')
        hcor_v0 = [e.x for e in hcor]
        vcor = ap.getElements('VCOR')
        vcor_v0 = [e.y for e in vcor]

        bpm = ap.getElements('BPM')
        bpm_v0 = [[e.x, e.y] for e in bpm]

        bpm_v1 = [[e.x, e.y] for e in bpm]

        bpm_v1[0] = [0, 0]
        bpm_v1[1] = [0, 1e-4]
        bpm_v1[2] = [2e-4, 1e-4]
        bpm_v1[3] = [5e-7, 1e-4]
        bpm_v1[4] = [0, 1e-4]
        bpm_v1[5] = [0, 1e-4]
        for i in range(6, len(bpm)):
            bpm_v1[i] = [0, 0]

        ap.setLocalBump(bpm, hcor+vcor, bpm_v1)



"""
ORM
~~~~
"""

class TestOrmData(unittest.TestCase):
    def setUp(self):
        self.h5filename = "us_nsls2_v2sr_orm.hdf5"
        pass

    def tearDown(self):
        pass

    @unittest.skip("orm data is not ready")
    def test_trim_bpm(self):
        self.assertTrue(ap.conf.has(self.h5filename))
        ormdata = ap.OrmData(ap.conf.filename(self.h5filename))

        trimx = ['fxl2g1c07a', 'cxh1g6c15b']
        for trim in trimx:
            self.assertTrue(ormdata.hasTrim(trim))

        bpmx = ap.getGroupMembers(['BPM', 'C0[2-4]'], op='intersection')
        self.assertEqual(len(bpmx), 18)
        for bpm in bpmx:
            self.assertTrue(ormdata.hasBpm(bpm.name))
        

    @unittest.skip("orm data is not ready")
    def test_measure_orm(self):
        return True
        if hla.NETWORK_DOWN: return True
        hla.reset_trims()
        trimx = ['cxh1g6c15b', 'cyhg2c30a', 'cxl2g6c14b']
        #trimx = ['CXH1G6C15B']
        bpmx = ['ph1g2c30a', 'pl1g2c01a', 'ph1g6c29b', 'ph2g2c30a', 'pm1g4c30a']
        #hla.reset_trims()
        orm = hla.measorm.Orm(bpm = bpmx, trim = trimx)
        orm.measure("orm-test.pkl", verbose=1)
        orm.measure_update(bpm=bpmx, trim=trimx[:2], verbose=1, dkick=5e-5)
        orm.save("orm-test-update.pkl")
        #orm.checkLinearity()
        pass

    @unittest.skip("orm data is not ready")
    def test_measure_orm_sub1(self):
        return True
        if hla.NETWORK_DOWN: return True

        trim = ['cxl1g2c05a', 'cxh2g6c05b', 'cxh1g6c05b', 'fxh2g1c10a',
                'cxm1g4c12a', 'cxh2g6c15b', 'cxl1g2c25a', 'fxh1g1c28a',
                'cyl2g6c30b', 'fyh1g1c16a']
        #trimx = ['CXH1G6C15B']
        bpmx = hla.getGroupMembers(['*', 'BPMX'], op='intersection')
        
        #hla.reset_trims()
        orm = hla.measorm.Orm(bpm = bpmx, trim = trim)
        orm.TSLEEP=15
        orm.measure(output="orm-sub1.pkl", verbose=0)
        #orm.checkLinearity()
        pass

    @unittest.skip("orm data is not ready")
    def test_measure_full_orm(self):
        return True
        if hla.NETWORK_DOWN: return True
        hla.reset_trims()
        bpm = hla.getGroupMembers(['*', 'BPMX'], op='intersection')
        trimx = hla.getGroupMembers(['*', 'TRIMX'], op='intersection')
        trimy = hla.getGroupMembers(['*', 'TRIMY'], op='intersection')
        trim = trimx[:]
        trim.extend(trimy)
        #print bpm, trim
        print "start:", time.time(), " version:", hg_parent_rev()
        orm = hla.measorm.Orm(bpm=bpm, trim=trim)
        orm.TSLEEP = 12
        orm.measure(output=self.full_orm, verbose=0)

    @unittest.skip("orm data is not ready")
    def test_linearity(self):
        return True
        #if hla.NETWORK_DOWN: return True
        orm = hla.measorm.Orm(bpm = [], trim = [])
        #orm.load('orm-test.pkl')
        #orm.load('/home/lyyang/devel/nsls2-hla/machine/nsls2/orm.pkl')
        hla.reset_trims()
        orm.load('./dat/orm-full-0181.pkl')
        #orm.maskCrossTerms()
        bpmpv = [b[2] for i,b in enumerate(orm.bpm)]
        for i,t in enumerate(orm.trim):
            k0 = hla.caget(t[3])
            v0 = np.array(hla.caget(bpmpv))
            caput(t[3], k0 + 1e-6)
            for j in range(10):
                time.sleep(2)
                v1 = np.array(hla.caget(bpmpv))
                print np.std(v1-v0),
                sys.stdout.flush()
            print ""
            caput(t[3], k0)
            if i > 20: break
        #print orm
        #for i,b in enumerate(orm.bpm):
        #    print i, b[0], b[2]
        #orm.checkLinearity(plot=True)
        pass

    @unittest.skip("orm data is not ready")
    def test_update(self):
        """
        same data different mask
        """
        self.assertTrue(ap.conf.has(self.h5filename))
        ormdata_dst = ap.OrmData(ap.conf.filename(self.h5filename))
        ormdata_src = ap.OrmData(ap.conf.filename(self.h5filename))
        
        nrow, ncol = len(ormdata_src.bpm), len(ormdata_src.trim)
        # reset data
        for i in range(nrow):
            for j in range(ncol):
                ormdata_src.m[i,j] = 0.0

        for itrial in range(3):
            idx = []
            for i in range(nrow*ncol//4):
                k = random.randint(0, nrow*ncol-1)
                idx.append(divmod(k, ncol))
                ormdata_src._mask[idx[-1][0]][idx[-1][1]] = 0

        ormdata_dst.update(ormdata_src)
        for i,j in idx:
            self.assertEqual(ormdata_dst.m[i,j], 0.0)

    @unittest.skip("orm data is not ready")
    def test_update_swapped(self):
        """
        same dimension, swapped rows
        """
        self.assertTrue(ap.conf.has(self.h5filename))
        ormdata_dst = ap.OrmData(ap.conf.filename(self.h5filename))
        ormdata_src = ap.OrmData(ap.conf.filename(self.h5filename))
        
        nrow, ncol = len(ormdata_src.bpm), len(ormdata_src.trim)
        # reset data
        for i in range(nrow):
            for j in range(ncol):
                ormdata_src.m[i,j] = 0.0

        # rotate the rows down by 2
        import collections
        rbpm = collections.deque(ormdata_src.bpm)
        rbpm.rotate(2)
        ormdata_src.bpm = [b for b in rbpm]

        for itrial in range(10):
            idx = []
            for i in range(nrow*ncol//4):
                k = random.randint(0, nrow*ncol-1)
                idx.append(divmod(k, ncol))
                ormdata_src._mask[idx[-1][0]][idx[-1][1]] = 0

        ormdata_dst.update(ormdata_src)
        for i,j in idx:
            i0, j0 = (i-2+nrow) % nrow, (j + ncol) % ncol
            self.assertEqual(ormdata_dst.m[i0,j0], 0.0)

    @unittest.skip("no sub matrix")
    def test_update_submatrix(self):
        """
        same dimension, swapped rows
        """
        self.assertTrue(ap.conf.has(self.h5filename))
        ormdata = ap.OrmData(ap.conf.filename(self.h5filename))
        nrow, ncol = len(ormdata.bpm), len(ormdata.trim)

        # prepare for subset
        for itrial1 in range(10):
            idx = []
            bpms, trims = set([]), set([])
            planes = [set([]), set([])]
            for itrial2 in range(nrow*ncol//4):
                k = random.randint(0, nrow*ncol-1)
                i,j = divmod(k, ncol)
                idx.append([i, j])
                bpms.add(ormdata.bpm[i][0])
                planes[0].add(ormdata.bpm[i][1])
                trims.add(ormdata.trim[j][0])
                planes[1].add(ormdata.trim[j][1])

            m = ormdata.getSubMatrix(bpm, trim, planes)

            for i,j in idx:
                self.assertEqual(ormdata_dst.m[i0,j0], 0.0)

        #orm1 = hla.measorm.Orm(bpm = [], trim = [])
        #orm1.load('a.hdf5')
        #orm2 = hla.measorm.Orm(bpm = [], trim = [])
        #orm2.load('b.hdf5')
        #orm = orm1.merge(orm2)
        #orm.checkLinearity()
        #orm.save('c.hdf5')
        
    @unittest.skip("empty")
    def test_shelve(self):
        return True
        #orm = hla.measorm.Orm(bpm = [], trim = [])
        #orm.load('c.hdf5')
        #orm.save('o1.pkl', format='shelve')
        #orm.load('o1.pkl', format='shelve')
        #orm.checkLinearity()

    @unittest.skip("empty")
    def test_orbitreproduce(self):
        return True

        t0 = time.time()
        hla.reset_trims()
        #time.sleep(10)
        t1 = time.time()

        pkl = './dat/orm-full-0181.pkl'
        orm = hla.measorm.Orm([], [])
        if not os.path.exists(pkl): return True
        else: orm.load(pkl)
        print orm
        #print "delay: ", orm.TSLEEP, " seconds"

        dk = 2e-4
        bpm_pvs = [b[2] for i,b in enumerate(orm.bpm)]
        x0 = np.zeros(len(bpm_pvs), 'd')
        #print bpm_pvs[:10]
        trim_k = np.zeros((len(orm.trim), 3), 'd')
        for j,t in enumerate(orm.trim):
            k0 = hla.caget(t[3])
            klst = np.linspace(1000*(k0-dk), 1000*(k0+dk), 20)
            print "%4d/%d" % (j, len(orm.trim)), t, k0
            trim_k[j,1] = k0
            x = np.zeros((len(bpm_pvs), 5), 'd')
            x0 = hla.caget(bpm_pvs)
            x[:,0] = x0
            x[:,2] = x0
            #print bpm_pvs[0], x[0,0], x[0,2]

            t2 = time.time()
            hla.caputwait(t[3], k0-dk, bpm_pvs[0])
            #time.sleep(orm.TSLEEP)
            trim_k[j,0] = k0 - dk
            x[:,1] = hla.caget(bpm_pvs)
            #print time.time() - t2, bpm_pvs[0], x[0,1]
            #time.sleep(orm.TSLEEP)

            hla.caputwait(t[3], k0+dk, bpm_pvs[0])
            #time.sleep(orm.TSLEEP)
            trim_k[j,2] = k0+dk
            
            x[:,3] = hla.caget(bpm_pvs)
            x[:,3] = hla.caget(bpm_pvs)
            #print bpm_pvs[0], x[0,3]

            hla.caputwait(t[3], k0, bpm_pvs[0])
            #time.sleep(3)
            #print x[0,:]

            mask = np.zeros(len(bpm_pvs), 'i')
            x1 = x0[:] - orm.m[:,j] * dk
            x2 = x0[:] + orm.m[:,j] * dk
            for i,b in enumerate(orm.bpm):
                if abs(x2[i] - x1[i]) < 3e-6: continue
                if abs(x2[i] - x[i,3]) < 5e-6 and abs(x1[i]-x[i,1]) < 5e-6:
                    continue
                plt.clf()
                plt.subplot(211)
                plt.plot(trim_k[j,:]*1000.0, np.transpose(1000.*x[i,1:4]), '--o')
                plt.plot(1000*orm._rawkick[j,:], 1000*orm._rawmatrix[:,i,j], 'x')
                plt.plot(klst, 1000.0*x0[i] + orm.m[i,j]*klst, '-')
                plt.grid(True)
                if orm._mask[i,j]: plt.title("%s.%s (masked)" % (t[0], t[1]))
                else: plt.title("%s.%s" % (t[0], t[1]))
                plt.xlabel("angle [mrad]")
                plt.ylabel('orbit [mm]')
                plt.subplot(212)
                plt.plot(1000*orm._rawkick[j,:], 1e6*((orm._rawmatrix[:,i,j] - orm._rawmatrix[0,i,j]) - \
                             orm.m[i,j]*orm._rawkick[j,:]), 'x')
                plt.plot(trim_k[j,:]*1000.0, 1e6*((x[i,1:4] - x[i,0])- trim_k[j,:]*orm.m[i,j]), 'o')
                plt.ylabel("Difference from prediction [um]")
                plt.xlabel("kick [mrad]")
                plt.savefig("orm-check-t%03d-%03d.png" % (j,i))
                if i > 100: break
            break
        print "Time:", time.time() - t1




if __name__ == "__main__":
    logging.info("Main")
    unittest.main()
    pass


