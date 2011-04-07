#!/usr/bin/env python

import hla
import unittest
import sys, os
import numpy as np
import random

from cothread.catools import caget

import matplotlib.pylab as plt

class TestChanFinderAgent(unittest.TestCase):
    _eget = 'default.get'
    _eput = 'default.put'

    def setUp(self):
        self.assertTrue(os.path.exists('chanfinder.pkl'))

        self.cfa = hla.chanfinder.ChannelFinderAgent()
        self.cfa.load('chanfinder.pkl')
        pass

    def test_match_properties1(self):
        self.assertTrue(
            self.cfa.matchProperties(
                'SR:C30-MG:G02A{HCM:H}Fld-I',
                {'cell':'C30', 'girder':'G02'}))
        self.assertTrue(
            self.cfa.matchProperties(
                'SR:C30-MG:G02A{HCM:H}Fld-I',
                {'elem_name': 'CXHG2C30A', 'elem_type':'TRIMX'}))
        
        
    def test_match_properties2(self):
        self.assertTrue(os.path.exists('lat_conf_table.txt'))
        #f = open('tmp.txt', 'w')
        #f.write(str(self.cfa))
        #f.close()

        for s in open('lat_conf_table.txt').readlines()[1:]:
            idx = int(s.split()[0])
            pv1 = s.split()[1]
            pv2 = s.split()[2]
            phy = s.split()[3]
            L   = float(s.split()[4])
            spos = float(s.split()[5])
            grp  = s.split()[6]
            #prpt = self.cfa.getChannelProperties(pv1)
            #if prpt: print "'%s' '%d' '%s' '%s'" % (
            #    phy, prpt['ordinal'], prpt['elem_name'], prpt['elem_type']), grp
            #prpt = self.cfa.getChannelProperties(pv2)
            #if prpt: print "'%s' '%d' '%s'" % (phy, prpt['ordinal'], prpt['elem_name']), grp
            #sys.stdout.flush()
            if pv1 != 'NULL':
                self.assertTrue(self.cfa.matchProperties(pv1, {'elem_name':phy}))
                self.assertTrue(self.cfa.matchProperties(pv1, {'elem_type':grp}))
                self.assertTrue(self.cfa.matchProperties(pv1, {'ordinal':idx}))
            if pv2 != 'NULL':
                self.assertTrue(self.cfa.matchProperties(pv2, {'elem_name':phy}))
                self.assertTrue(self.cfa.matchProperties(pv2, {'elem_type':grp}))
                self.assertTrue(self.cfa.matchProperties(pv2, {'ordinal':idx}))

    def test_match_tags(self):
        print self.cfa.channel('SR:C30-MG:G04A{VCM:FM1}Fld-SP')
        print self.cfa.channel('SR:C30-MG:G01A{HCM:FH2}Fld-I')

        self.assertTrue(
            self.cfa.matchTags(
                'SR:C30-MG:G04A{VCM:FM1}Fld-SP'))
        self.assertTrue(
            self.cfa.matchTags('SR:C30-MG:G01A{HCM:FH2}Fld-I',
                               tags = [self._eget]))

    def test_properties(self):
        prop = self.cfa.getElementProperties('PH1G2C30A')
        self.assertEqual(prop['cell'], 'C30')
        self.assertEqual(prop['girder'], 'G02')
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
        
if __name__ == "__main__":
    unittest.main()


