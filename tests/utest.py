import sys, os
import unittest

from conf import *
LOCK_ID = 1
import aphlas as hla

hla.hlalib._wait_for_lock(LOCK_ID, maxwait=3600)

print "= Initializing NSLS2VSR lattice in HLA"
hla.initNSLS2VSR()

print "= HLA used:", hla.__path__

print "= reset trims"
hla.hlalib._reset_trims()
hla.hlalib._reset_bpm_offset()

#import utChanFinder
import test_element
#import utLattice
#import utTwiss
#import utAllPVs
#import utOrm
#import utOrbit

loader = unittest.TestLoader()


suite = unittest.TestSuite()
suite.addTests(loader.loadTestsFromModule(test_element))

#suite.addTests(loader.loadTestsFromTestCase(utLattice.TestLatticeSrCf))
#suite.addTests(loader.loadTestsFromTestCase(utLattice.TestLatticeSrTxt))
#suite.addTests(loader.loadTestsFromTestCase(utLattice.TestLatticeLtbCf))
#suite.addTests(loader.loadTestsFromTestCase(utLattice.TestLatticeLtbTxt))

#suite.addTests(loader.loadTestsFromModule(utTwiss))

#suite.addTests(loader.loadTestsFromModule(utOrbit))

#suite.addTests(loader.loadTestsFromModule(utAllPVs))
#suite.addTests(loader.loadTestsFromModule(utOrm))

#print '%x' % sys.hexversion, sys.hexversion

if sys.hexversion < 0x02070000:
    runner = unittest.TextTestRunner(verbosity=2)
else:
    runner = unittest.TextTestRunner(verbosity=2, failfast=True)

result = runner.run(suite)

print "= Results:", result, len(result.failures), len(result.errors)
hla.hlalib._release_lock(LOCK_ID)

sys.exit(len(result.failures) + len(result.errors))


