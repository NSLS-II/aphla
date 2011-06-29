import sys, os
import unittest

from conf import *

import hla
print "= HLA used:", hla.__path__

#import utChanFinder
import utElement
import utLattice
import utTwiss
#import utAllPVs
#import utOrm
#import utOrbit

loader = unittest.TestLoader()


suite = unittest.TestSuite()
suite.addTests(loader.loadTestsFromModule(utElement))

suite.addTests(loader.loadTestsFromTestCase(utLattice.TestLatticeSrCf))
suite.addTests(loader.loadTestsFromTestCase(utLattice.TestLatticeSrTxt))
suite.addTests(loader.loadTestsFromTestCase(utLattice.TestLatticeLtbCf))
suite.addTests(loader.loadTestsFromTestCase(utLattice.TestLatticeLtbTxt))

suite.addTests(loader.loadTestsFromModule(utTwiss))

#suite.addTests(loader.loadTestsFromModule(utAllPVs))
#suite.addTests(loader.loadTestsFromModule(utOrbit))
#suite.addTests(loader.loadTestsFromModule(utOrm))

runner = unittest.TextTestRunner(verbosity=2)
result = runner.run(suite)

print "= Results:", result, len(result.failures), len(result.errors)
sys.exit(len(result.failures) + len(result.errors))


