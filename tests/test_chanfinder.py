#!/usr/bin/env python

import aphla as ap
import unittest
import sys, os
import numpy as np
import random

from conf import *

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
        #print TEST_CONF_VERSION
        #print self.cfa.tags('aphla.?')
        self.assertTrue(len(self.cfa.tags('aphla.?')) == 2)
        
