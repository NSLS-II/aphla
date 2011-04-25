#!/usr/bin/env python

from conf import *

import hla
import unittest
import sys, time
import numpy as np

from cothread.catools import caget, caput
import matplotlib.pylab as plt


def hg_parent_rev():
    import commands
    stat, out = commands.getstatusoutput("hg summary")
    if stat == 0:
        for s in out.split('\n'):
            if s[:7] == 'parent:':
                return int(s.split(":")[1])
    return 0

class TestConf(unittest.TestCase):
    def setUp(self):
        if hla.NETWORK_DOWN: return None
        wait_for_svr()
        self.full_orm = "orm-full-%04d.pkl" % hg_parent_rev()
        pass

    def tearDown(self):
        if hla.NETWORK_DOWN: return None
        reset_svr()

    def test_trim_bpm(self):
        trimx = ['FXL2G1C07A', 'CXH1G6C15B']
        #print hla.getSpChannels(trimx)
        for tr in trimx:
            self.assertTrue(len(hla.getLocations(tr)) == 1)

        self.assertEqual(len(hla.getRbChannels(trimx)), 2)
        self.assertEqual(len(hla.getSpChannels(trimx)), 2)

        bpmx = hla.getGroupMembers(['*', 'BPMX'], op='intersection')
        self.assertTrue(len(bpmx) > 0)
        trimxsp = [v[0] for v in \
                       hla.getSpChannels(trimx, tags=['default.eput', 'X'])]
        self.assertTrue(len(trimxsp) > 0)

        trimxrb = [v[0] for v in \
                   hla.getRbChannels(trimx, tags=['default.eget', 'X'])]
        self.assertTrue(len(trimxrb) > 0)

        bpmxrb  = [v[0] for v in \
                   hla.getRbChannels(bpmx, tags=['default.eget', 'X'])]
        self.assertTrue(len(bpmxrb) > 0)

        self.assertEqual(len(trimx), len(trimxsp))
        self.assertEqual(len(trimx), len(trimxrb))
        self.assertEqual(len(bpmx), len(bpmxrb))

    def test_measure_orm(self):
        return True
        if hla.NETWORK_DOWN: return True

        trimx = ['CXH1G6C15B', 'CYHG2C30A', 'CXL2G6C14B']
        #trimx = ['CXH1G6C15B']
        bpmx = ['PH1G2C30A', 'PL1G2C01A', 'PH1G6C29B', 'PH2G2C30A', 'PM1G4C30A']
        #hla.reset_trims()
        orm = hla.measorm.Orm(bpm = bpmx, trim = trimx)
        orm.measure(verbose=0)
        orm.save("orm-test.pkl")
        #orm.checkLinearity()
        pass

    def test_measure_orm_sub1(self):
        return True
        if hla.NETWORK_DOWN: return True

        trim = ['CXL1G2C05A', 'CXH2G6C05B', 'CXH1G6C05B', 'FXH2G1C10A',
                'CXM1G4C12A', 'CXH2G6C15B', 'CXL1G2C25A', 'FXH1G1C28A',
                'CYL2G6C30B', 'FYH1G1C16A']
        #trimx = ['CXH1G6C15B']
        bpmx = hla.getGroupMembers(['*', 'BPMX'], op='intersection')
        
        #hla.reset_trims()
        orm = hla.measorm.Orm(bpm = bpmx, trim = trim)
        orm.TSLEEP=15
        orm.measure(output="orm-sub1.pkl", verbose=0)
        #orm.checkLinearity()
        pass

    def test_measure_full_orm(self):
        return True
        #print __file__, "Measure full matrix"
        if hla.NETWORK_DOWN: return True

        bpm = hla.getGroupMembers(['*', 'BPMX'], op='intersection')
        trimx = hla.getGroupMembers(['*', 'TRIMX'], op='intersection')
        trimy = hla.getGroupMembers(['*', 'TRIMY'], op='intersection')
        trim = trimx[:]
        trim.extend(trimy)
        #print bpm, trim
        print "start:", time.time()
        orm = hla.measorm.Orm(bpm=bpm, trim=trim)
        orm.TSLEEP = 12
        orm.measure(output=self.full_orm, verbose=0)

    def test_linearity(self):
        #return True
        #if hla.NETWORK_DOWN: return True
        orm = hla.measorm.Orm(bpm = [], trim = [])
        #orm.load('orm-test.pkl')
        orm.load('/home/lyyang/devel/nsls2-hla/machine/nsls2/orm.pkl')
        orm.maskCrossTerms()
        #print orm
        #for i,b in enumerate(orm.bpm):
        #    print i, b[0], b[2]
        #orm.checkLinearity(plot=True)
        pass

    def test_merge(self):
        if hla.NETWORK_DOWN: return True
        #orm1 = hla.measorm.Orm(bpm = [], trim = [])
        #orm1.load('a.hdf5')
        #orm2 = hla.measorm.Orm(bpm = [], trim = [])
        #orm2.load('b.hdf5')
        #orm = orm1.merge(orm2)
        #orm.checkLinearity()
        #orm.save('c.hdf5')
        
    def test_shelve(self):
        if hla.NETWORK_DOWN: return True
        #orm = hla.measorm.Orm(bpm = [], trim = [])
        #orm.load('c.hdf5')
        #orm.save('o1.pkl', format='shelve')
        #orm.load('o1.pkl', format='shelve')
        #orm.checkLinearity()

    def test_orbitreproduce(self):
        if hla.NETWORK_DOWN: return True

        bpm = hla.getGroupMembers(['*', 'BPMX'], op='intersection')
        trimx = hla.getGroupMembers(['*', 'TRIMX'], op='intersection')
        trimy = hla.getGroupMembers(['*', 'TRIMY'], op='intersection')
        trim = trimx[:]
        trim.extend(trimy)
        #print bpm, trim
        print "start:", time.time()

        orm2 = hla.measorm.Orm([], [])
        if not os.path.exists(self.full_orm): return True

        orm2.load(self.full_orm)
        print orm2
        print "delay: ", orm2.TSLEEP
        orm2.maskCrossTerms()
        x0, x1, dx = orm2.checkOrbitReproduce(bpm, trim[:5])
        ratio = (x1-x0-dx)/x0
        for i in range(len(x0)):
            if x0[i] < 1e-7: ratio[i] = 0.0
        plt.clf()
        plt.plot(ratio, '-o')
        plt.ylabel("[(x1-x0)-dx]/x0")
        plt.savefig("orm-orbit-reproduce-1.png")
        
        plt.clf()
        plt.plot(x0, '--', label='orbit 0')
        plt.plot(x1, '-', label='orbit 1')
        plt.plot(x0+dx, 'x', label='ORM predict')
        
        plt.ylabel("orbit")
        plt.savefig("orm-orbit-reproduce-2.png")

        for i in range(len(bpm)):
            if x0[i]+dx[i] - x1[i] > 1e-4:
                print "Not agree well:", i,bpm[i], x0[i]+dx[i], x1[i]
        print "Done", time.time()
        
def test_delay():
    rx, rt = [], []
    t0 = time.time()
    k0 = caget('SR:C01-MG:G04A{VCM:M}Fld-SP')
    caput('SR:C01-MG:G04A{VCM:M}Fld-SP', k0-3e-6)
    time.sleep(10)
    for k in [k0, k0-2e-6, k0-1e-6, k0-.5e-6, k0+.5e-6, k0+1e-6, k0]:
        x0 = caget('SR:C30-BI:G02A{BPM:H2}SA:Y-I')
        caput('SR:C01-MG:G04A{VCM:M}Fld-SP', k)
        while True:
            time.sleep(0.5)
            x3 = caget('SR:C30-BI:G02A{BPM:H2}SA:Y-I')
            t1 = time.time()
            if abs((x3 - x0)/x0) > 0.05:
                rx.append(x3)
                rt.append(t1)
                break
        print "%10.3e %11.4e %11.4e" % (k, rt[-1]-t0, rx[-1]-x0), 
        print caget('SR:C30-BI:G02A{BPM:H2}SA:Y-I')

def test_1():
    x = []
    t0 = 1299032723.0
    k0 = caget('SR:C01-MG:G04A{VCM:M}Fld-SP')
    for k in [k0, k0-1e-6, k0-.5e-6, k0+.5e-6, k0+1e-6, k0]:
        t1 = time.time()
        #caput('SR:C30-MG:G01A<VCM:H2>Fld-SP', k)
        caput('SR:C01-MG:G04A{VCM:M}Fld-SP', k, wait=True)
        time.sleep(hla.ORBIT_WAIT)
        x3 = caget('SR:C30-BI:G02A{BPM:H2}SA:Y-I')

        caput('SR:C01-MG:G04A{VCM:M}Fld-SP', k, wait=True)
        time.sleep(hla.ORBIT_WAIT)
        x2 = caget('SR:C30-BI:G02A{BPM:H2}SA:Y-I')
        print k, x3, x2
    print x

def test_2(dt = 20, dup=True):
    # stabilize the system
    print "\n# waiting for stable beam ..."
    for i in range(7):
        caput('SR:C01-MG:G04A{VCor:M}Fld-SP', 0.0)
        time.sleep(3)
        print "# %d" % i, caget('SR:C30-BI:G02A{BPM:H2}SA:Y-I')
    print "# beam is stable now, if output is not changing much"
    
    t0 = time.time()
    k0 = caget('SR:C01-MG:G04A{VCor:M}Fld-SP')
    dk = [1e-6, 2e-6, 1e-6, 0.0, -1e-6, -2e-6, -1e-6, 0.0]
    print "\n# if waiting=%d sec is long enough for Tracy," % dt
    print "# two dx should be same"
    print "# also, for same kick, dx should be the same"
    print "# lets see ...."
    for i in range(6):
        k = k0 + dk[i%len(dk)]
        
        caput('SR:C01-MG:G04A{VCor:M}Fld-SP', k, wait=True)
        time.sleep(dt)
        t1 = time.time()
        x2 = caget('SR:C30-BI:G02A{BPM:H2}SA:Y-I')
        
        if dup:
            caput('SR:C01-MG:G04A{VCor:M}Fld-SP', k)
            time.sleep(4)
            t2 = time.time()
            x3 = caget('SR:C30-BI:G02A{BPM:H2}SA:Y-I')

        if dup:
            print "%3d kick=% .2e dx=% .4e dx=% .4e" % (i, k, x2, x3), t2-t0
        else:
            print "%3d kick=% .2e dx=% .4e" % (i, k, x2), t1 - t0

    # stabilize the beam, I believe 3sec*7 is good enough
    print "\n# waiting for stable beam"
    for i in range(7):
        caput('SR:C01-MG:G04A{VCor:M}Fld-SP', 0.0)
        time.sleep(3)
        print "# %d" % i, caget('SR:C30-BI:G02A{BPM:H2}SA:Y-I')
    print "# beam is stable now, if output is not changing much"

if __name__ == "__main__":
    #test_2(dt=6, dup=True)
    #print "# in the above output, second column of dx is more correct"
    #print ""
    #print "--- Now next experiment ..."
    #print ""
    #test_2(dt=10, dup=False)
    #hla.clean_init()
    #hla.reset_trims()
    #test_1()
    #test_delay()
    unittest.main()

