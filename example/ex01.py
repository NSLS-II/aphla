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
    hla.initNSLS2VSR()
    hla.machines.use('SR')

    # orbit at cell 3-6 BPMs
    bpm = hla.getElements('P*C0[3-6]*')
    s1 = [b.sb for b in bpm]
    x1 = [b.x for b in bpm]
    y1 = [b.y for b in bpm]
    
    allbpms = hla.getElements('BPM')
    s2x = [b.sb for b in allbpms]

    # for each element, do data acquisition to b.x and b.y (slow)
    #obt = np.array([(b.x, b.y) for b in allbpms], 'd')

    # get the orbit and locations of BPMS: (x,y,s)
    obt2 = np.array(hla.getOrbit(spos = True), 'd')

    plt.clf()
    plt.plot(s1, x1, 'x-')
    #plt.plot(s2x, obt[:,0], '--')
    plt.plot(obt2[:,-1], obt2[:,0], '--')
    plt.savefig('orbit.png')
