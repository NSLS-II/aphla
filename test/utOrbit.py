#!/usr/bin/env python

from conf import *

import hla
import unittest
import sys, os
import numpy as np
import random


class TestOrbit(unittest.TestCase):
    """
    Tested:

    - orbit dimension
    """
    _eget = 'default.eget'
    _eput = 'default.eput'

    def setUp(self):
        self.assertTrue(os.path.exists(CFAPKL))
        self.orbit = hla.orbit.Orbit(hla._cfa)
        pass

    def test_orbit(self):
        self.assertTrue(len(self.orbit.get()) > 0)

if __name__ == "__main__":
    unittest.main()

