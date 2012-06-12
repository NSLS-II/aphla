#!/usr/bin/env python

import aphla as ap
import unittest
import sys, os
import numpy as np
import random

from conf import *

class TestChanFinderData(unittest.TestCase):
    def setUp(self):
        self.HLA_CFS_URL=os.environ.get('HLA_CFS_URL', None)
        pass
    
    def test_sys(self):
        pass

class TestChanFinderAgent(unittest.TestCase):
    """
    """

    def setUp(self):
        #http://web01.nsls2.bnl.gov/ChannelFinder
        self.HLA_CFS_URL=os.environ.get('HLA_CFS_URL', None)
        self.cfa = ap.chanfinder.ChannelFinderAgent()
        self.cfa.downloadCfs(self.HLA_CFS_URL, tagName='aphla.*')
        pass

    def test_match_properties1(self):
        tags = self.cfa.tags('aphla.sys.*')
        self.assertGreater(len(tags), 0)
        self.assertTrue('aphla.sys.SR' in tags)
        self.assertTrue('aphla.sys.LTD1' in tags)
        self.assertTrue('aphla.sys.LTD2' in tags)
        self.assertTrue('aphla.sys.LTB' in tags)

        
