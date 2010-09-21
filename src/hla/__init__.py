#!/usr/bin/env python

import sys, os
from hla.capi import *

_family = []

def init(conf):
    if os.path.exists(conf):
        print "Yes! I found it"
    f = os.path.join(conf, 'lattice_channels.txt')
    if os.path.exists(f):
        print "Yes! I also find the file: ", f
    _family.append(0)

if __name__ == "__main__":
    init('.')

