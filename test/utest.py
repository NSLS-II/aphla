import sys, os
import unittest

from conf import *

import utChanFinder
import utLattice
import utAllPVs
import utOrm
import utOrbit

loader = unittest.TestLoader()

suite = loader.loadTestsFromModule(utChanFinder)
suite.addTests(loader.loadTestsFromModule(utLattice))
suite.addTests(loader.loadTestsFromModule(utAllPVs))
suite.addTests(loader.loadTestsFromModule(utOrbit))
suite.addTests(loader.loadTestsFromModule(utOrm))

runner = unittest.TextTestRunner(verbosity=2)
result = runner.run(suite)

print "= Results:", result, len(result.failures), len(result.errors)
sys.exit(len(result.failures) + len(result.errors))


