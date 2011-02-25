#!/usr/bin/env python


"""
   HLA Module
   -----------

   HLA module
   
   :author:
   :license:

   HLA
"""

from cadict import CADict
import conf

#
# testing, bypass the IRMIS database.
#

import os

# get the HLA root directory
pt = os.path.dirname(os.path.abspath(__file__))
xmlconf = "%s/../../%s/main.xml" % (pt, conf.root['nsls2'])
print "Using conf file:", xmlconf
ca = CADict(xmlconf)
quad = ca.findGroup("QUAD")
quadpv = ca.getChannels(quad[:5], mode="fieldRB")
print ca.getGroups()
#print ca.getGroups('long')

#print quad

def abc():
    """abc, def"""
    print ca.getGroups()
    return None


from latmode import *
from latgroup import *
from latgeom import *
from meastwiss import *
from measorm import *
from current import *

def test():
    measBeta(quad[:5], ca=ca)
    
