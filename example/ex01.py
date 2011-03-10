#!/usr/bin/env python

"""
An orbit display example

:author: Lingyun Yang
:date: 2011-03-09
"""


import hla
import matplotlib.pylab as plt
import numpy as np

if __name__ == '__main__':
    # initialize when no real machine exists
    hla.clean_init()

    # orbit at cell 3-6 BPMs
    bpm = hla.getElements('P*C0[3-6]*')
    s1 = hla.getLocations(bpm)
    x1, y1 = hla.getOrbit(bpm)
    
    s2x = hla.getLocations('BPMX')
    x2, y2 = hla.getOrbit()

    plt.clf()
    plt.plot(s1, x1, 'x-')
    plt.plot(s2x, x2, '--')
    plt.savefig('test.png')
