#!/usr/bin/env python
import sys, os, time
from numpy import arange, sin, pi, random, sqrt
from scipy.optimize import fmin, fmin_cg, fmin_powell
import matplotlib.pylab as plt

import cothread
import cothread.catools as catools
import latman


def theo_local_bump1(lat):
    # all elements
    betax = [v for v in catools.caget("SR:C00-Glb:G00<BETA:00>RB:X")]
    phix = [v for v in catools.caget("SR:C00-Glb:G00<PHI:00>RB:X")]
    bpm_idx = lat.group_index("@BpmX")
    ch_idx = lat.group_index("@CorrectorX")

    # two kicker, 11*2pi phase advance.
    hc1="SR:C01-MG:G02A<HCM:H1>Fld:SP"
    hc2=hc1
    hc3="SR:C10-MG:G06A<HCM:H2>Fld:SP"
    
    ic1 = lat.pvindex(hc1)
    ic2 = lat.pvindex(hc2)
    ic3 = lat.pvindex(hc3)
    print "index:", ic1, ic2, ic3
    print "beta", betax[ic1], betax[ic2], betax[ic3]
    print "s_end", lat.s_end(hc1), lat.s_end(hc2), lat.s_end(hc3)
    print "phase:", phix[ic1], phix[ic2], phix[ic3]
    c1 = 1e-5
    catools.caput(hc1, c1)
    catools.caput(hc3, -c1*sqrt(betax[ic1]/betax[ic3]))
    time.sleep(4)
    s,x1,y1 = get_orbit(lat, 4)
    print "get orbit"


def theoretical_strength(lat, hclst, theta):
    betax = [v for v in catools.caget("SR:C00-Glb:G00<BETA:00>RB:X")]
    phix = [v*2.0*3.1415926 for v in catools.caget("SR:C00-Glb:G00<PHI:00>RB:X")]
    bpm_idx = lat.group_index("@BpmX")
    ch_idx = lat.group_index("@CorrectorX")

    # three kicker
    ic1 = lat.pvindex(hclst[0])
    ic2 = lat.pvindex(hclst[1])
    ic3 = lat.pvindex(hclst[2])
    if ic1 == -1 or ic2 == -1 or ic3 == -1:
        print "Can not find PV"
        return None

    print "index:", ic1, ic2, ic3
    print "beta", betax[ic1], betax[ic2], betax[ic3]
    print "s_end", lat.s_end(hc1), lat.s_end(hc2), lat.s_end(hc3)
    print "phase:", phix[ic1], phix[ic2], phix[ic3]
    c1 = theta
    c2 = sqrt(betax[ic1]/betax[ic2])*sin(phix[ic3]-phix[ic1])/sin(phix[ic3]-phix[ic2])
    c3 = sqrt(betax[ic1]/betax[ic3])*sin(phix[ic2]-phix[ic1])/sin(phix[ic3]-phix[ic2])
    return -c1*c2, c1*c3
    
def theo_local_bump2(lat):
    # all elements
    hc1="SR:C03-MG:G02A<HCM:H1>Fld:SP"
    hc2="SR:C03-MG:G02A<HCM:H2>Fld:SP"
    hc3="SR:C03-MG:G04B<HCM:M1>Fld:SP"

    c1 = 1e-5
    c2, c3 = theoretical_strength(lat, (hc1, hc2, hc3), c1)
    catools.caput(hc1, c1)
    catools.caput(hc2, c2)
    catools.caput(hc3, c3)
    time.sleep(6)
    s, x, y = get_orbit(lat)
    

def get_orbit(lat, delay=2):
    time.sleep(delay)
    vs = [v for v in catools.caget("SR:C00-Glb:G00<POS:00>RB:S")]
    vx = [v for v in catools.caget("SR:C00-Glb:G00<ORBIT:00>RB:X")]
    vy = [v for v in catools.caget("SR:C00-Glb:G00<ORBIT:00>RB:Y")]
    #print len(vs), len(vx), len(vy)
    bpm = lat.group_index("@BpmX")
    #print bpm
    s = [vs[i] for i in bpm]
    x = [vx[i] for i in bpm]
    y = [vy[i] for i in bpm]
    return s, x, y

def orbit_dev(x, lat, hclst):
    #hc1="SR:C01-MG:G02A<HCM:H1>Fld:SP"
    #hc2="SR:C01-MG:G02A<HCM:H2>Fld:SP"
    #hc3="SR:C01-MG:G04B<HCM:M1>Fld:SP"
    
    # check against boundary of corrector strength
    print "Setting % .4e % .4e" % (x[0], x[1]),
    for cx in x:
        if abs(cx) > 1e-2: 
            print ""
            return 1e30

    catools.caput(hclst[1], x[0])
    catools.caput(hclst[2], x[1])
    # wait for 4 seconds
    time.sleep(6)
    s, x, y = get_orbit(lat)
    plt.clf()
    plt.plot(s, x, 'r-')
    plt.plot(s, y, 'g-')
    plt.plot(s[1:4], x[1:4], 'ro')
    plt.plot(s[1:4], y[1:4], 'gx')
    plt.savefig("orbit.png")

    #sys.exit(0)

    orb = 0.0
    for i in range(len(x)):
        # skip bpms close to correctors
        if i > 0 and i < 4: continue
        orb += x[i]**2 + y[i]**2
    print "% .6e" % orb
    return orb

if __name__ == "__main__":
    hc1="SR:C01-MG:G02A<HCM:H1>Fld:SP"
    hc2="SR:C01-MG:G02A<HCM:H2>Fld:SP"
    hc3="SR:C01-MG:G04B<HCM:M1>Fld:SP"
    lat = latman.LatticeManager("../nsls2/conf/lattice_channels.txt")
    catools.caput(hc1, 0.0)
    catools.caput(hc2, 0.0)
    catools.caput(hc3, 0.0)

    #theo_local_bump2(lat)
    #sys.exit(0)

    time.sleep(2)
    print hc1,catools.caget(hc1)
    print hc2,catools.caget(hc2)
    print hc3,catools.caget(hc3)
    print "Clear 3 kickers"
    s, x, y = get_orbit(lat, 6)
    plt.clf()
    plt.plot(s, x, 'rx-')
    plt.plot(s, y, 'go-')
    plt.savefig("orbit-00.png")

    c1 = 1e-5
    catools.caput(hc1, c1)
    c2, c3 = theoretical_strength(lat, (hc1, hc2, hc3), c1)

    x0 = [c2, c3]
    xopt = fmin(orbit_dev, x0, args=(lat,(hc1, hc2, hc3)), xtol=1e-9, maxiter=5,full_output=True)
    print xopt

    print "DONE"
