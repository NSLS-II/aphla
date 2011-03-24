import unittest

import utChanFinder

#import utLattice
#import utOrm
#import ut1
#import ut2

loader = unittest.TestLoader()

suite = loader.loadTestsFromModule(utChanFinder)
#suite.addTests(loader.loadTestsFromModule(ut1))
#suite.addTests(loader.loadTestsFromModule(ut2))

runner = unittest.TextTestRunner(verbosity=2)
result = runner.run(suite)

