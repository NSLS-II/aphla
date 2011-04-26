#!/usr/bin/env python

from conf import *

import hla
import unittest
import sys, time
import numpy as np

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
        hla.reset_trims()
        trimx = ['CXH1G6C15B', 'CYHG2C30A', 'CXL2G6C14B']
        #trimx = ['CXH1G6C15B']
        bpmx = ['PH1G2C30A', 'PL1G2C01A', 'PH1G6C29B', 'PH2G2C30A', 'PM1G4C30A']
        #hla.reset_trims()
        orm = hla.measorm.Orm(bpm = bpmx, trim = trimx)
        orm.measure("orm-test.pkl", verbose=0)
        orm.measure_update(bpm=bpmx, trim=trimx[:2], verbose=1, dkick=5e-5)
        orm.save("orm-test-update.pkl")
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
        #return True
        if hla.NETWORK_DOWN: return True
        hla.reset_trims()
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
        return True

        if hla.NETWORK_DOWN: return True

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

