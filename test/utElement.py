#!/usr/bin/env python

import unittest
import sys, os, time
import numpy as np
#import matplotlib.pylab as plt

from conf import *
import element
from catools import caget, caput

class TestElement(unittest.TestCase):
    def setUp(self):
        pass

    def test_read(self):
        elem = element.Element(
            name= 'CURRENT', eget = caget, eput = caput,
            index = -1,
            devname = 'DCCT',
            family = 'DCCT')
        elem.addEGet('SR:C00-BI:G00{DCCT:00}CUR-RB')
        self.assertTrue(len(str(elem)) > 0)
        self.assertTrue(abs(elem.value) > 0)

    def test_readwrite(self):
        elem = element.Element(
            name = 'BPM', eget = caget, eput = caput,
            index = -1, devname = 'BPM')
        elem.addEGet('SR:C29-BI:G06B{BPM:H1}SA:Y-I')
        elem.addEGet('SR:C29-BI:G06B{BPM:H1}SA:X-I')
        elem.addEPut('SR:C29-BI:G06B{BPM:H1}GOLDEN:Y')
        elem.addEPut('SR:C29-BI:G06B{BPM:H1}GOLDEN:X')
        self.assertTrue(len(str(elem)) > 0)
        #print caget(['SR:C29-BI:G06B{BPM:H1}SA:X-I', 'SR:C29-BI:G06B{BPM:H1}SA:Y-I'])
        caput(['SR:C29-BI:G06B{BPM:H1}GOLDEN:X', 'SR:C29-BI:G06B{BPM:H1}GOLDEN:Y'], 0.0, wait=True)
        #print caget(['SR:C29-BI:G06B{BPM:H1}GOLDEN:X', 'SR:C29-BI:G06B{BPM:H1}GOLDEN:Y'])
        #time.sleep(3)
        x0 = elem.value
        #print x0
        self.assertTrue(len(x0) == 2)
        elem.value = .01
        time.sleep(2)
        x1 = elem.value
        #print x0, x1
        self.assertTrue(x1[0] >= -0.01 - 2*abs(x0[0]))
        self.assertTrue(x1[1] >= -0.01 - 2*abs(x0[1]))
        self.assertTrue(x1[0] <= 2*abs(x0[0]) - 0.01, "%.8e %.8e" % (x0[0]-0.01, x1[0]))

        elem.value = [0.003, 0.002]
        x2 = elem.value
        self.assertTrue(x2[0] <= 0.003 + abs(x0[0]))
        self.assertTrue(x2[1] <= 0.002 + abs(x0[1]))

        elem.value = 0
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
            name = 'V:BPM', eget = caget, eput = caput,
            index = -1, devname = 'BPM')
        elem.addEGet('SR:C29-BI:G06B{BPM:H1}SA:Y-I')
        elem.addEGet('SR:C29-BI:G06B{BPM:H1}SA:X-I')
        elem.setFieldGetAction('x', 'SR:C29-BI:G06B{BPM:H1}SA:X-I', 'X')
        elem.setFieldPutAction('x', 'SR:C29-BI:G06B{BPM:H1}GOLDEN:X', 'X')
        self.assertTrue(len(elem.value) == 2,
                        "element: %s, %s" % (elem.name, elem._field['value']))
        val = elem.x
	self.assertTrue(abs(val) > 0)
        elem.x = 0.01
        time.sleep(2)
        #print val, elem.x
        self.assertTrue(abs(elem.x) > 10*abs(val)) 

if __name__ == "__main__":
    unittest.main()

