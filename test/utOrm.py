#!/usr/bin/env python

import hla
import unittest
import sys, time
import numpy as np

from cothread.catools import caget, caput
import matplotlib.pylab as plt

class TestConf(unittest.TestCase):
    def setUp(self):
        pass

    def test_measure_orm(self):
        #trimx = hla.getGroupMembers(['*', 'TRIMX'], op='intersection')
        #print hla.getGroupMembers(['*', 'TRIMX'], op='intersection')
        trimx = ['FXL2G1C07A', 'CXH1G6C15B']
        #print hla.getSpChannels(trimx)
        for tr in trimx:
            self.assertTrue(len(hla.getLocations(tr)) == 1)
        print hla.getRbChannels(trimx)
        print hla.getSpChannels(trimx)

        bpmx = hla.getGroupMembers(['*', 'BPMX'], op='intersection')
        self.assertTrue(len(bpmx) > 0)

        trimxsp = [v[0] for v in hla.getSpChannels(trimx)]
        trimxrb = [v[0] for v in hla.getRbChannels(trimx)]
        bpmxrb  = [v[0] for v in hla.getRbChannels(bpmx)]

        for i in range(len(trimx)):
            print i, trimx[i], trimxsp[i], trimxrb[i]
        for i in range(len(bpmx)):
            print i, bpmx[i], bpmxrb[i]

        orm = hla.measOrbitRm(bpm = bpmx, trim = trimx)
        #orm = hla.measorm.Orm(bpm = [], trim = [])
        #orm.load('test.hdf5')
        orm.checkLinearity()
        pass


    def test_linearity(self):
        return True
        orm = hla.measorm.Orm(bpm = [], trim = [])
        orm.load('test.hdf5')
        orm.checkLinearity()
        pass

    def test_merge(self):
        return True
        orm1 = hla.measorm.Orm(bpm = [], trim = [])
        orm1.load('a.hdf5')
        orm2 = hla.measorm.Orm(bpm = [], trim = [])
        orm2.load('b.hdf5')
        orm = orm1.merge(orm2)
        orm.checkLinearity()
        orm.save('c.hdf5')
        
    def test_shelve(self):
        return True
        orm = hla.measorm.Orm(bpm = [], trim = [])
        orm.load('c.hdf5')
        orm.save('o1.pkl', format='shelve')
        orm.load('o1.pkl', format='shelve')
        orm.checkLinearity()

    def test_orbitreproduce(self):
        """
        # all G2 Trim
        #BPM, caget, sum M*K, relative diff. 
        PL1G2C03A 2.76106332459e-06 2.76028400607e-06 -0.000282332730237
        PL2G2C03A 2.74567973141e-06 2.74376513312e-06 -0.000697799627985
        PM1G4C03A -3.82555373792e-06 -3.82634380577e-06 0.000206481143403
        PM1G4C03B -2.68739708579e-06 -2.68552390336e-06 -0.000697510989897
        PH2G6C03B 1.68442774752e-06 1.68525899299e-06 0.000493244940091
        PH1G6C03B 3.04211635453e-06 3.04305096591e-06 0.000307129717625
        """

        return True
        orm = hla.measorm.Orm(bpm = [], trim = [])
        orm.load('o1.pkl', format = 'shelve')
        bpm = hla.getGroupMembers(['*', 'BPMX'], op='intersection')
        trim = hla.getGroupMembers(['*', 'TRIMX'], op='intersection')
        kick = None
        #print orm.getSubMatrix(bpm = bpm, trim = trim)
        #bpm = ['PH1G6C03B']
        #trim = ['CXHG2C30A', 'CXH2G2C30A', 'CXHG2C02A']
        #kick = [1e-6] * len(trim)
        orm.checkOrbitReproduce(bpm, trim, kick)
        
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
        caput('SR:C01-MG:G04A{VCM:M}Fld-SP', k)
        time.sleep(hla.ORBIT_WAIT)
        x3 = caget('SR:C30-BI:G02A{BPM:H2}SA:Y-I')

        caput('SR:C01-MG:G04A{VCM:M}Fld-SP', k)
        time.sleep(hla.ORBIT_WAIT)
        x2 = caget('SR:C30-BI:G02A{BPM:H2}SA:Y-I')
        print k, x3, x2
    print x

def test_2(dt = 20, dup=True):
    # stabilize the system
    print "\n# waiting for stable beam ..."
    for i in range(7):
        caput('SR:C01-MG:G04A{VCM:M}Fld-SP', 0.0)
        time.sleep(3)
        print "# %d" % i, caget('SR:C30-BI:G02A{BPM:H2}SA:Y-I')
    print "# beam is stable now, if output is not changing much"
    
    t0 = time.time()
    k0 = caget('SR:C01-MG:G04A{VCM:M}Fld-SP')
    dk = [1e-6, 2e-6, 1e-6, 0.0, -1e-6, -2e-6, -1e-6, 0.0]
    print "\n# if waiting=%d sec is long enough for Tracy," % dt
    print "# two dx should be same"
    print "# also, for same kick, dx should be the same"
    print "# lets see ...."
    for i in range(6):
        k = k0 + dk[i%len(dk)]
        
        caput('SR:C01-MG:G04A{VCM:M}Fld-SP', k)
        time.sleep(dt)
        x2 = caget('SR:C30-BI:G02A{BPM:H2}SA:Y-I')
        
        if dup:
            caput('SR:C01-MG:G04A{VCM:M}Fld-SP', k)
            time.sleep(4)
            x3 = caget('SR:C30-BI:G02A{BPM:H2}SA:Y-I')

        if dup:
            print "%3d kick=% .2e dx=% .4e dx=% .4e" % (i, k, x2, x3)
        else:
            print "%3d kick=% .2e dx=% .4e" % (i, k, x2)

    # stabilize the beam, I believe 3sec*7 is good enough
    print "\n# waiting for stable beam"
    for i in range(7):
        caput('SR:C01-MG:G04A{VCM:M}Fld-SP', 0.0)
        time.sleep(3)
        print "# %d" % i, caget('SR:C30-BI:G02A{BPM:H2}SA:Y-I')
    print "# beam is stable now, if output is not changing much"

if __name__ == "__main__":
    test_2(dt=10, dup=True)
    print "# in the above output, second column of dx is more correct"
    print ""
    print "--- Now next experiment ..."
    print ""
    test_2(dt=25, dup=False)
    #hla.clean_init()
    #hla.reset_trims()
    #test_1()
    #test_delay()
    #unittest.main()

