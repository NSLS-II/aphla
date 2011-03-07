#!/usr/bin/env python


"""
   HLA Module
   -----------

   HLA module
   
   :author:
   :license:

   HLA
"""

import os, sys

import conf

#
# testing, bypass the IRMIS database.
#

from latmode import *
from latgroup import *
from latgeom import *
from meastwiss import *
from measorm import *
from orbit import *
from current import *

def test():
    measBeta(quad[:5], ca=ca)
    
def init(lat):
    print lat
