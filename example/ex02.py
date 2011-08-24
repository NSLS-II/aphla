#!/usr/bin/env python

"""
An example of measuring dispersion

:author: Lingyun Yang
:date: 2011-03-10
"""


import time
import hla
import matplotlib.pylab as plt
import numpy as np


if __name__ == '__main__':
    # initialize when no real machine exists
    hla.initNSLS2VSR()
    hla.initNSLS2VSRTwiss()

    alphac = 3.6261976841792413e-04
    gamma = 3.0e3/.511
    eta = alphac - 1/gamma/gamma
    # orbit at cell 3-6 BPMs
    bpmobj = hla.getElements('P*C0[3-6]*')
    bpmnames = [b.name for b in bpmobj]

    s1 = [b.sb for b in bpmobj]
    eta0 = hla.getDispersion(bpmnames)
    print "dispersion:", eta0

    # f in MHz
    f0 = hla.getRfFrequency()
    f = np.linspace(f0 - 1e-5, f0 + 1e-5, 5)

    # avoid a bug in virtac
    obt0 = hla.getOrbit(bpmnames)
    x0, y0 = obt0[:,0], obt0[:,1]
    time.sleep(4)

    codx = np.zeros((len(f), len(bpmobj)), 'd')
    cody = np.zeros((len(f), len(bpmobj)), 'd')
    for i,f1 in enumerate(f): 
        hla.putRfFrequency(f1)
        time.sleep(3)
        obt1 = hla.getOrbit()

        # repeat the put/get in case simulator did not response latest results
        hla.putRfFrequency(f1)
        time.sleep(6)
        obt2 = hla.getOrbit(bpmnames)
        print i, obt1[0,:2], obt2[0,:2]
        codx[i,:] = obt2[:,0]
        cody[i,:] = obt2[:,1]

    hla.putRfFrequency(f0)

    plt.clf()
    for i in range(len(bpmobj)):
        plt.plot(f, codx[:,i], 'o-')
    plt.savefig('test-cod.png')

    codx0 = np.zeros(np.shape(codx), 'd')
    for i in range(len(f)):
        codx0[i,:] = x0[:]
    dxc = codx - codx0
    df = -(f - f0)/f0/eta
    print df
    print dxc
    # p[0,len(bpm)]
    p = np.polyfit(df, dxc, 1)
    print "first order:", p[0,:]
    t = np.linspace(df[0], df[-1], 20)
    plt.clf()
    for i in range(len(bpmobj)):
        plt.plot(df, dxc[:,i], 'o')
        plt.plot(t, p[0,i]*t + p[1,i], '--')
    plt.savefig('test-disp.png')


    print eta, f0
    plt.clf()
    plt.plot(s1, eta0, 'x-', label="Twiss Calc")
    plt.plot(s1, p[0,:], 'o--', label="Fit")
    plt.legend()
    plt.savefig('test.png')
