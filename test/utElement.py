#!/usr/bin/env python

import unittest
import sys, os, time
import numpy as np
#import matplotlib.pylab as plt

from conf import *
import element
from cothread.catools import caget, caput

class TestElement(unittest.TestCase):
    def setUp(self):
        pass

    def test_read(self):
        elem = element.Element(
            name= 'CURRENT',
            index = -1,
            devname = 'DCCT',
            family = 'DCCT',
            eget = [(caget, 'SR:C00-BI:G00{DCCT:00}CUR-RB', 'I')])
        self.assertTrue(len(str(elem)) > 0)
        self.assertTrue(abs(elem.value) > 0)

    def test_readwrite(self):
        elem = element.Element(
            name = 'BPM',
            index = -1,
            devname = 'BPM',
            pvs = [(caget, 'SR:C29-BI:G06B{BPM:H1}SA:Y-I', 'P1'),
                   (caget, 'SR:C29-BI:G06B{BPM:H1}GOLDEN:Y', 'P2'),
                   (caget, 'SR:C29-BI:G06B{BPM:H1}BBA:Y', 'P3')],
            eget = [(caget, ['SR:C29-BI:G06B{BPM:H1}SA:X-I',
                             'SR:C29-BI:G06B{BPM:H1}SA:Y-I'], 'orbit')],
            eput = [(caput, 'SR:C29-BI:G06B{BPM:H1}GOLDEN:Y', 'golden')])
        self.assertTrue(len(str(elem)) > 0)
        x = elem.value
        elem.value = .001
        self.assertTrue(len(x) == 2)
        self.assertTrue(len(str(elem.status)) > 0)

    def test_sort(self):
        elem1 = element.Element(name= 'E1', sb= 0.0)
        elem2 = element.Element(name= 'E1', sb= 2.0)
        elem3 = element.Element(name= 'E1', sb= 1.0)
        el = sorted([elem1, elem2, elem3])
        self.assertTrue(el[0].sb < el[1].sb)
        self.assertTrue(el[1].sb < el[2].sb)
        
    def test_field(self):
        elem = element.Element(
            name = 'BPM',
            index = -1,
            devname = 'BPM',
            pvs = [(caget, 'SR:C29-BI:G06B{BPM:H1}SA:Y-I', 'P1'),
                   (caget, 'SR:C29-BI:G06B{BPM:H1}GOLDEN:Y', 'P2'),
                   (caget, 'SR:C29-BI:G06B{BPM:H1}BBA:Y', 'P3')],
            eget = [(caget, ['SR:C29-BI:G06B{BPM:H1}SA:X-I',
                             'SR:C29-BI:G06B{BPM:H1}SA:Y-I'], 'orbit')],
            eput = [(caput, 'SR:C29-BI:G06B{BPM:H1}GOLDEN:Y', 'golden')])

        elem._field = {'x': [(caget, 'SR:C29-BI:G06B{BPM:H1}SA:Y-I', 'P1'),
                             (caput, 'SR:C29-BI:G06B{BPM:H1}GOLDEN:Y', 'golden')]}
        val = elem.x
	self.assertTrue(abs(val) > 0)


if __name__ == "__main__":
    unittest.main()

