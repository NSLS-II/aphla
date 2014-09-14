"""
nsls2 specific routines for physics IOCs

Copyright (C) 2014, BNL
Copyright (C) 2014, Lingyun Yang
"""

import aphla as ap


def init():
    ap.machines.load("nsls2", "SR")

def measTbtBetaPhi(nturns = 2000):
    """
    measure the beta function, phase and tune

    >>> beta, phi, tune = measTbtBetaPhi()
    """
    tw = ap.getTwiss('p*c*', ['s', 'betax', 'betay', 'etax', 'phix', 'phiy'])
    # trig=0 is internal, trig=1 is external
    names, x0, y0, Isum0, timestamp, offset = \
        ap.nsls2.getSrBpmData(waveform="Tbt",trig=1, count=nturns, output=False)
    # adjust the offset, align to the original zero
    nbpm, nturns = np.shape(Isum0)
    nturns = nturns + np.max(offset)
    x = np.zeros((nbpm, nturns), 'd')
    y = np.zeros((nbpm, nturns), 'd')
    Isum = np.zeros((nbpm, nturns), 'd')
    # convert nm to mm
    for i in range(nbpm):
        x[i,offset[i]:offset[i]+nturns] = x0[i,:]*1e-6
        y[i,offset[i]:offset[i]+nturns] = y0[i,:]*1e-6
        Isum[i,offset[i]:offset[i]+nturns] = Isum0[i,:]

    n = nturns - 200
    btx = ap.calcBetaAu(x[:,3:n], ref=tw[:,1])
    bty = ap.calcBetaAu(y[:,3:n], ref=tw[:,2])
    phix = ap.calcPhase(x[:,3:n], ref=tw[:,4])
    phiy = ap.calcPhase(y[:,3:n], ref=tw[:,5])
    return (btx, bty), (phix, phiy), None
