import sys, os
import unittest

from conf import *

import utChanFinder
import utLattice
import utAllPVs
import utOrm
#import ut1
#import ut2

loader = unittest.TestLoader()

suite = loader.loadTestsFromModule(utChanFinder)
suite.addTests(loader.loadTestsFromModule(utLattice))
suite.addTests(loader.loadTestsFromModule(utAllPVs))
suite.addTests(loader.loadTestsFromModule(utOrbit))

runner = unittest.TextTestRunner(verbosity=2)
result = runner.run(suite)

print "= Results:", result, len(result.failures), len(result.errors)
sys.exit(len(result.failures) + len(result.errors))


