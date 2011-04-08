import sys, os
import unittest

import utChanFinder
import utLattice
import utAllPVs
#import utOrm
#import ut1
#import ut2

loader = unittest.TestLoader()

suite = loader.loadTestsFromModule(utChanFinder)
#suite.addTests(loader.loadTestsFromModule(utAllPVs))
suite.addTests(loader.loadTestsFromModule(utLattice))

runner = unittest.TextTestRunner(verbosity=2)
result = runner.run(suite)

print result
sys.exit(len(result.failures))


