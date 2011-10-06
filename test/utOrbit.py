#!/usr/bin/env python

from conf import *

import hla
import unittest
import sys, os
import numpy as np
import random

machine_initialized = False

class TestOrbit(unittest.TestCase):
    """
    Tested:

    - orbit dimension
    """

    def setUp(self):
        global machine_initialized
        if not machine_initialized:
            hla.machines.initNSLS2VSR()
            hla.machines.initNSLS2VSRTxt()
            machine_initialized = True
        self.lat = hla.machines.getLattice('SR')
        self.assertTrue(self.lat)

    def test_orbit(self):
        self.assertTrue(len(hla.getElements('BPM')) > 0)

        v = hla.getOrbit()
        self.assertTrue(len(v) > 0)
        v = hla.getOrbit('*')
        self.assertTrue(len(v) > 0)
        v = hla.getOrbit('P*')
        self.assertTrue(len(v) > 0)

if __name__ == "__main__":
    unittest.main()

