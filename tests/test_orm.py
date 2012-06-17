#!/usr/bin/env python

import aphla as ap
import unittest
import random
#import sys, time
#import numpy as np

ap.initNSLS2VSR()

class TestOrmData(unittest.TestCase):
    def setUp(self):
        self.h5filename = "us_nsls2_vsr_orm.hdf5"
        pass

    def tearDown(self):
        pass

    def test_trim_bpm(self):
        self.assertTrue(ap.conf.has(self.h5filename))
        ormdata = ap.OrmData(ap.conf.filename(self.h5filename))

        trimx = ['FXL2G1C07A', 'CXH1G6C15B']
        for trim in trimx:
            self.assertTrue(ormdata.hasTrim(trim))

        bpmx = ap.getGroupMembers(['BPM', 'C0[2-4]'], op='intersection')
        self.assertEqual(len(bpmx), 18)
        for bpm in bpmx:
            self.assertTrue(ormdata.hasBpm(bpm.name))
        

    def test_measure_orm(self):
        return True
        if hla.NETWORK_DOWN: return True
        hla.reset_trims()
        trimx = ['CXH1G6C15B', 'CYHG2C30A', 'CXL2G6C14B']
        #trimx = ['CXH1G6C15B']
        bpmx = ['PH1G2C30A', 'PL1G2C01A', 'PH1G6C29B', 'PH2G2C30A', 'PM1G4C30A']
        #hla.reset_trims()
        orm = hla.measorm.Orm(bpm = bpmx, trim = trimx)
        orm.measure("orm-test.pkl", verbose=1)
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
        
    def test_shelve(self):
        return True
        #orm = hla.measorm.Orm(bpm = [], trim = [])
        #orm.load('c.hdf5')
        #orm.save('o1.pkl', format='shelve')
        #orm.load('o1.pkl', format='shelve')
        #orm.checkLinearity()

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

