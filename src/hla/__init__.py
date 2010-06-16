#!/usr/bin/env python

import sys, os

def init(conf):
    if os.path.exists(conf):
        print "Yes! I found it"
    f = os.path.join(conf, 'lattice_channels.txt')
    if os.path.exists(f):
        print "Yes! I also find the file: ", f

if __name__ == "__main__":
    init('.')

