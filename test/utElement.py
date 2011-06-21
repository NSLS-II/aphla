#!/usr/bin/env python

import unittest
import sys, os, time
import numpy as np
import matplotlib.pylab as plt

from conf import *
import element
from cothread.catools import caget, caput

class TestElement(unittest.TestCase):
    def setUp(self):
        pass

    def test_read(self):
        elem = element.Element(
            'CURRENT',
            index = -1,
            devname = 'DCCT',
            family = 'DCCT',
            eget = (caget, 'SR:C00-BI:G00{DCCT:00}CUR-RB', 'I'))
        print elem
        print elem.value

    def test_readwrite(self):
        elem = element.Element(
            'BPM',
            index = -1,
            devname = 'BPM',
            pvs = [(caget, 'SR:C29-BI:G06B{BPM:H1}SA:Y-I', 'P1'),
                   (caget, 'SR:C29-BI:G06B{BPM:H1}GOLDEN:Y', 'P2'),
                   (caget, 'SR:C29-BI:G06B{BPM:H1}BBA:Y', 'P3')],
            eget = (caget, ['SR:C29-BI:G06B{BPM:H1}SA:X-I', 'SR:C29-BI:G06B{BPM:H1}SA:Y-I'], 'orbit'),
            eput = (caput, 'SR:C29-BI:G06B{BPM:H1}GOLDEN:Y', 'golden'))
        print elem
        x = elem.value
        elem.value = .001
        print x, elem.value, caget('SR:C29-BI:G06B{BPM:H1}GOLDEN:Y')
        print elem.status

    def test_sort(self):
        elem1 = element.Element('E1', sb= 0.0)
        elem2 = element.Element('E1', sb= 2.0)
        elem3 = element.Element('E1', sb= 1.0)
        for e in sorted([elem1, elem2, elem3]):
            print e
        

if __name__ == "__main__":
    unittest.main()

