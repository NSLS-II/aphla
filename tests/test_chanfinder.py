#!/usr/bin/env python

import aphla as ap
import unittest
import sys, os
import numpy as np
import random

from conf import *

class TestChanFinderCsvData(unittest.TestCase):
    """
    """
    def setUp(self):
        self.cfa = ap.chanfinder.ChannelFinderAgent()
        self.cfa.importCsv(ap.conf.filename('us_nsls2_vsr_cfs.csv'))
        self.VSUB = 'V1'

    def test_tags(self):
        # e.g: aphla.sys + . + V1
        vstag = ap.machines.HLA_TAG_SYS_PREFIX + '.' + self.VSUB
        tags = self.cfa.tags(vstag + '*')
        for t in ['SR', 'LTB', 'LTD1', 'LTD2']:
            self.assertIn(vstag + t, tags)

    def test_match_properties1(self):
        pass
        
class TestChanFinderData(unittest.TestCase):
    def setUp(self):
        #http://web01.nsls2.bnl.gov/ChannelFinder
        self.HLA_CFS_URL=os.environ.get('HLA_CFS_URL', None)
        self.cfa = ap.chanfinder.ChannelFinderAgent()
        self.cfa.downloadCfs(self.HLA_CFS_URL, tagName='aphla.*')
        self.VSUB='V1'
        pass
    
    def test_sys_tags(self):
        vstag = ap.machines.HLA_TAG_SYS_PREFIX + '.' + self.VSUB
        tags = self.cfa.tags(vstag + '*')
        for t in ['SR', 'LTB', 'LTD1', 'LTD2']:
            self.assertIn(vstag + t, tags)
        pass

