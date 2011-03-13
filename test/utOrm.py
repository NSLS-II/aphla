#!/usr/bin/env python

import hla
import unittest
import sys
import numpy as np

from cothread.catools import caget
import matplotlib.pylab as plt

class TestConf(unittest.TestCase):
    def setUp(self):
        #print "HLA clean init() "
        #hla.clean_init()
        pass

    def test_measure_orm(self):
        return True
        #trimx = hla.getGroupMembers(['*', 'TRIMX'], op='intersection')
        #print hla.getGroupMembers(['*', 'TRIMX'], op='intersection')
        trimx = ['CFXL2G1C07A', 'CFXL2G1C11A', 'CXH1G6C15B']
        #print hla.getSpChannels(trimx)

        bpmx = hla.getGroupMembers(['*', 'BPMX'], op='intersection')

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

        #return True
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
        
if __name__ == "__main__":
    hla.clean_init()
    unittest.main()


