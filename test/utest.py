import sys, os
import unittest

if not 'HLA_ROOT' in os.environ:
    rt,ext = os.path.splitext(os.path.realpath(sys.argv[0]))
    HLA_ROOT = os.path.split(os.path.split(rt)[0])[0]
else:
    HLA_ROOT = os.environ['HLA_ROOT']
    
print "HLA root directory: ", HLA_ROOT
sys.path.append(os.path.join(HLA_ROOT, 'src'))
sys.path.append(os.path.join(HLA_ROOT, 'test'))

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


