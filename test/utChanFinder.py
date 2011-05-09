#!/usr/bin/env python

import hla
import unittest
import sys, os
import numpy as np
import random

from cothread.catools import caget

#import matplotlib.pylab as plt

from conf import *

class TestChanFinderAgent(unittest.TestCase):
    """
    Tested:

    - against lat_conf_table.txt
    - pv name agrees with cell, girder, symmetry, sp and readback
    - 
    """
    _eget = 'default.eget'
    _eput = 'default.eput'

    def setUp(self):
        self.assertTrue(os.path.exists(CFAPKL))
        self.cfa = hla.chanfinder.ChannelFinderAgent()
        self.cfa.load(CFAPKL)
        pass

    def test_match_properties1(self):
        self.assertTrue(
            self.cfa.matchProperties(
                'SR:C30-MG:G02A{HCor:H}Fld-I',
                {'cell':'C30', 'girder':'G2'}))
        self.assertTrue(
            self.cfa.matchProperties(
                'SR:C30-MG:G02A{HCor:H}Fld-I',
                {'elem_name': 'CXHG2C30A', 'elem_type':'TRIMX'}))
        
        
    def test_lat_conf_table(self):
        self.assertTrue(os.path.exists(LATCONF))

        for s in open(LATCONF).readlines()[1:]:
            idx = int(s.split()[0])
            pv1 = s.split()[1]
            pv2 = s.split()[2]
            phy = s.split()[3]
            L   = float(s.split()[4])
            spos = float(s.split()[5])
            grp  = s.split()[6]
            dev  = s.split()[7]

            if pv1 != 'NULL':
                try:
                    self.assertTrue(self.cfa.matchProperties(pv1, {'elem_name':phy}))
                except AssertionError:
                    print phy, self.cfa.channel(pv1)
                    raise AssertionError("%s != %s" % (phy, self.cfa.channel(pv1)))

                self.assertTrue(self.cfa.matchProperties(pv1, {'elem_type':grp}))
                try:
                    self.assertTrue(self.cfa.matchProperties(pv1, {'ordinal':idx}))
                except AssertionError:
                    print idx, self.cfa.channel(pv1)
                self.assertTrue(self.cfa.matchProperties(pv1, {'dev_name': dev}))
            if pv2 != 'NULL':
                self.assertTrue(self.cfa.matchProperties(pv2, {'elem_name':phy}))
                self.assertTrue(self.cfa.matchProperties(pv2, {'elem_type':grp}))
                self.assertTrue(self.cfa.matchProperties(pv2, {'ordinal':idx}))
                self.assertTrue(self.cfa.matchProperties(pv2, {'dev_name': dev}))

    def test_match_tags(self):
        #print self.cfa.channel('SR:C30-MG:G04A{VCM:FM1}Fld-SP')
        #print self.cfa.channel('SR:C30-MG:G01A{HCM:FH2}Fld-I')

        self.assertTrue(
            self.cfa.matchTags(
                'SR:C30-MG:G04A{VFCor:FM1}Fld-SP', None))
        self.assertTrue(
            self.cfa.matchTags('SR:C30-MG:G01A{HFCor:FH2}Fld-I',
                               tags = [self._eget]))

    def test_properties(self):
        prop = self.cfa.getElementProperties('PH1G2C30A')
        self.assertEqual(prop['cell'], 'C30')
        self.assertEqual(prop['girder'], 'G2')
        self.assertEqual(prop['elem_name'], 'PH1G2C30A')

    def test_sortelement(self):
        elem = ["QH2G2C30A", "QH2G2C02A", "QH2G2C04A", "QH2G2C06A", "QH2G2C08A",
                "QH2G2C10A", "QH2G2C12A", "QH2G2C14A", "QH2G2C16A", "QH2G2C18A",
                "QH2G2C20A", "QH2G2C22A", "QH2G2C24A", "QH2G2C26A", "QH2G2C28A"]
        idx = range(len(elem))
        random.shuffle(idx)
        elem2 = self.cfa.sortElements([elem[i] for i in idx])
        for i in range(2, len(elem2)):
            self.assertTrue(elem2[i-1] < elem2[i])

    def test_default_eget(self):
        for s in open(LATCONF).readlines()[1:]:
            idx = int(s.split()[0])
            pv1 = s.split()[1]
            pv2 = s.split()[2]
            phy = s.split()[3]
            L   = float(s.split()[4])
            spos = float(s.split()[5])
            grp  = s.split()[6]
            dev  = s.split()[7]
            
            pvget = self.cfa.getChannels(prop={'elem_name': phy}, tags=['default.eget'])
            pvput = self.cfa.getChannels(prop={'elem_name': phy}, tags=['default.eput'])
            if grp in [ 'BPMX', 'BPMY' ]:
                self.assertEqual(len(pvget), 2)
                self.assertEqual(len(pvput), 0)
            elif grp in ['SEXT'] and phy == 'SM2HG4C29B':
                pass
            elif grp in ['CHROM', 'OMEGA', 'MCF', 'TUNE', 'DCCT']:
                pass
            else:
                self.assertEqual(len(pvget), 1)
                self.assertEqual(len(pvput), 1)

if __name__ == "__main__":
    unittest.main()


