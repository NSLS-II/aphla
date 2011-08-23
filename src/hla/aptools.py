#!/usr/bin/env python


"""
Accelerator Physics Tools
~~~~~~~~~~~~~~~~~~~~~~~~~~

:author: Lingyun Yang

Accelerator Physics Tools

"""

from __future__ import print_function

import numpy as np
import time, shelve, sys
import matplotlib.pylab as plt

import machines
from orbit import Orbit
from catools import caput, caget 
from hlalib import getElements, getNeighbors, getClosest
from bba import BBA

__all__ = [
    'getLifetime',  'measChromaticity', 'measDispersion',
    'correctOrbitPv', 'correctOrbit', 'alignQuadrupole', 'createLocalBump'
]

alphac = 3.6261976841792413e-04

def getLifetime(verbose = 0):
    """
    Monitor current change with, calculate lifetime dI/dt

    It takes about 30 seconds, 10 points will be recorded, about 3 seconds
    delay between each.

    least square linear fitting is applied for slop dI/dt
    """

    # data points
    N = 10
    ret = np.zeros((N, 2), 'd')
    d0 = datetime.datetime.now()
    ret[0, 1] = getCurrent()
    for i in range(1, N):
        # sleep for next reading
        time.sleep(3)
        ret[i,1] = getCurrent()
        dt = datetime.datetime.now() - d0
        ret[i,0] = (dt.microseconds/1000000.0 + dt.seconds)/3600.0 + \
            dt.days*24.0
        if verbose:
            print(i, dt, ret[i,1])
    dI = max(ret[:,1]) - min(ret[:,1]) 
    dt = max(ret[:,0]) - min(ret[:,0])
    #print np.average(ret[:,1]), dI, dt
    #print np.average(ret[:,1]) / (dI / dt), "H"
    lft_hour = np.average(ret[:,1]) / (dI / dt)
    return lft_hour


def measChromaticity():
    """
    Measure the chromaticity
    """
    gamma = 3.0e3/.511
    eta = alphac - 1/gamma/gamma

    f0 = getRfFrequency()
    nu0 = getTunes()
    print(f0, nu0)

    f = np.linspace(f0 - 1e-3, f0 + 1e-3, 6)
    nu = np.zeros((len(f), 2), 'd')
    for i,f1 in enumerate(f): 
        putRfFrequency(f1)
        time.sleep(6)
        nu[i,:] = getTunes()

    df = f - f0
    dnu = nu - np.array(nu0)
    p, resi, rank, sing, rcond = np.polyfit(df, dnu, deg=2, full=True)
    print("Coef:", p)
    print("Resi:", resi)
    chrom = p[-2,:] * (-f0*eta)
    print("Chromx:", chrom)
    
    t = np.linspace(1.1*df[0], 1.1*df[-1], 100)
    plt.clf()
    plt.plot(f - f0, nu[:,0] - nu0[0], '-rx')
    plt.plot(f - f0, nu[:,1] - nu0[1], '-go')
    plt.plot(t, t*t*p[-3,0]+t*p[-2,0] + p[-1,0], '--r',
             label="H: %.1fx^2%+.2fx%+.1f" % (p[-3,0], p[-2,0], p[-1,0]))
    plt.plot(t, t*t*p[-3,1]+t*p[-2,1] + p[-1,1], '--g',
             label="V: %.1fx^2%+.2fx%+.1f" % (p[-3,1], p[-2,1], p[-1,1]))
    plt.text(min(df), min(dnu[:,0]),
             r"$\eta=%.3e,\quad C_x=%.2f,\quad C_y=%.2f$" %\
             (eta, chrom[0], chrom[1]))
    
    plt.legend(loc='upper right')
    plt.xlabel("$f-f_0$ [MHz]")
    plt.ylabel(r"$\nu-\nu_0$")
    plt.savefig('measchrom.png')
    putRfFrequency(f0)
    pass


def measDispersion():
    """
    Measure the dispersion
    """

    #print "Measure dispersion"
    
    gamma = 3.0e3/.511
    eta = alphac - 1/gamma/gamma

    #bpm = getElements('P*C0[3-6]*')
    bpm = getElements('P*')
    #print gamma, bpm
    s1 = getLocations(bpm)
    eta0 = getDispersion(bpm)
    
    # f in MHz
    f0 = getRfFrequency()
    f = np.linspace(f0 - 1e-4, f0 + 1e-4, 5)

    # avoid a bug in virtac
    obt = getOrbit(bpm)
    x0 = np.array([v[0] for v in obt])
    y0 = np.array([v[1] for v in obt])
    time.sleep(4)

    codx = np.zeros((len(f), len(bpm)), 'd')
    cody = np.zeros((len(f), len(bpm)), 'd')

    for i,f1 in enumerate(f): 
        putRfFrequency(f1)
        time.sleep(6)
        obt = np.array(getOrbit(bpm))
        x1, y1 = obt[:,0], obt[:,1] 

        putRfFrequency(f1)
        time.sleep(6)
        obt = np.array(getOrbit(bpm))
        x2, y2  = obt[:,0], obt[:,1]
        print(i, getRfFrequency(), x1[0], x2[0], x1[2], x2[2])
        codx[i,:] = x2[:]
        cody[i,:] = y2[:]

    putRfFrequency(f0)

    plt.clf()
    for i in range(len(bpm)):
        plt.plot(f, codx[:,i], 'o-')
    plt.savefig('test-cod.png')

    codx0 = np.zeros(np.shape(codx), 'd')
    for i in range(len(f)):
        codx0[i,:] = x0[:]
    dxc = codx - codx0
    df = -(f - f0)/f0/eta
    print(df)
    print(dxc)
    # p[0,len(bpm)]
    p = np.polyfit(df, dxc, 1)
    print("first order:", p[0,:])
    t = np.linspace(df[0], df[-1], 20)
    plt.clf()
    for i in range(len(bpm)):
        plt.plot(df, dxc[:,i], 'o')
        plt.plot(t, p[0,i]*t + p[1,i], '--')
    plt.savefig('test-disp.png')


    print(eta, f0)
    plt.clf()
    plt.plot(s1, eta0[:,0], 'x-', label="Twiss Calc")
    plt.plot(s1, p[0,:], 'o--', label="Fit")
    plt.legend()
    plt.savefig('test.png')

    dat = [(bpm[i], s1[i], p[0,i], eta0[i,0]) for i in range(len(bpm))]
    f = shelve.open("dispersion.pkl", 'c')
    f["dispersion"] = dat
    f.close()
    

def correctOrbitPv(bpm, trim, ormdata, ref = None):
    """
    correct orbit use direct pv and catools

    - the input bpm and trim should be uniq in pv names.
    """
    #print "Matrix size: ", len(bpm), len(trim)
    m = np.zeros((len(bpm), len(trim)), 'd')
    for i,b in enumerate(bpm):
        im = ormdata.index(b)
        if im < 0: raise ValueError("PV %s is not found in ormdata" % b)
        for j,t in enumerate(trim):
            jm = ormdata.index(t)
            if jm < 0: raise ValueError("pv %s is not found in ormdata" % t)
            # did not check if the item is masked.
            m[i,j] = ormdata.m[im,jm]

    print(len(ref), len(bpm))
    v0 = np.array(caget(bpm), 'd')
    if ref != None: v0 = v0 - ref

    dk, resids, rank, s = np.linalg.lstsq(m, -1.0*v0)
    k0 = np.array(caget(trim), 'd')
    caput(trim, k0+dk)

def createLocalBump(bpm, trim, ref, **kwargs):
    """
    create a local bump at certain BPM, while keep all other orbit untouched
    
    - *bpm* a list of BPM name
    - *trim* corrector (group/family/list)
    - *ref* target orbit, (len(bpm),2), if the ref[i][j] == None, use the current hardware result.
    """
    plane = kwargs.get('plane', 'HV')

    bpmlst = getElements(bpm, alwayslist=True)
    if len(bpm) != len(bpmlst):
        raise ValueError("bpm must be a list of qualified BPM names")
    for i,b in enumerate(bpmlst):
        if b.name != bpm[i]:
            raise ValueError("bpm must be a list of qualified BPM names")

    bpmfulllst = getElements('BPM')
    bpmpv, bpmref = [], []
    pvx, pvy = [], []
    for b in bpmfulllst:
        xpv = b.pv(tags=[machines.HLA_TAG_X, machines.HLA_TAG_EGET])
        ypv = b.pv(tags=[machines.HLA_TAG_Y, machines.HLA_TAG_EGET])
        if xpv: pvx.append(xpv)
        if ypv: pvy.append(ypv)
        bpmpv.append(xpv)
        bpmpv.append(ypv)
        x0, y0 = b.value
        if b in bpmlst:
            idx = bpmlst.index(b)
            if ref[idx][0] == None:
                bpmref.append(x0)
            else:
                bpmref.append(ref[idx][0])

            if ref[idx][1] == None:
                bpmref.append(y0)
            else:
                bpmref.append(ref[idx][1])
        else:
            bpmref.append(caget(xpv))
            bpmref.append(caget(ypv))

    # did not check duplicate PV
    # pv for trim
    trimlst = machines._lat.getElements(trim)

    trimpv, pvxsp, pvysp = [], [], []
    for e in trimlst:
        pv = e.pv(tags=[machines.HLA_TAG_X, machines.HLA_TAG_EPUT])
        if pv: pvxsp.append(pv)
        if isinstance(pv, (str, unicode)): trimpv.append(pv)
        elif pv: trimpv.extend(pv)
        
        pv = e.pv(tags=[machines.HLA_TAG_Y, machines.HLA_TAG_EPUT])
        if pv: pvysp.append(pv)
        if isinstance(pv, (str, unicode)): trimpv.append(pv)
        elif pv: trimpv.extend(pv)

    if 'H' in plane and len(pvx) > 0 and len(pvxsp) == 0:
        print("WARNING: no HCOR for horizontal orbit correction", file=sys.stderr)
    if 'V' in plane and len(pvy) > 0 and len(pvysp) == 0:
        print("WARNING: no VCOR for vertical orbit correction", file=sys.stderr)

    if not machines._lat.orm:
        print("ERROR: this lattice setting has no ORM data", file=sys.stderr)
    else:
        correctOrbitPv(bpmpv, trimpv, machines._lat.orm, np.array(bpmref))

    
    
def correctOrbit(bpm, trim, **kwargs):
    """
    correct the orbit with given BPMs and Trims

    Example::

      >>> correctOrbit(['BPM1', 'BPM2'], ['T1', 'T2', 'T3'])

    The orbit not in BPM list may change.

    .. seealso:: :func:`hla.getSubOrm`
    """

    plane = kwargs.get('plane', 'HV')

    # an orbit based these bpm
    bpmlst = machines._lat.getElements(bpm)
    pvx = [e.pv(tags=[machines.HLA_TAG_X, machines.HLA_TAG_EGET])
           for e in bpmlst]
    pvy = [e.pv(tags=[machines.HLA_TAG_Y, machines.HLA_TAG_EGET])
           for e in bpmlst]

    if plane == 'H': bpmpv = set(pvx)
    elif plane == 'V': bpmpv = set(pvy)
    else: bpmpv = set(pvx + pvy)

    # pv for trim
    trimlst = machines._lat.getElements(trim)

    trimpv, pvxsp, pvysp = [], [], []
    for e in trimlst:
        pv = e.pv(tags=[machines.HLA_TAG_X, machines.HLA_TAG_EPUT])
        print(e.name, pv)
        if pv: pvxsp.append(pv)
        if isinstance(pv, (str, unicode)): trimpv.append(pv)
        elif pv: trimpv.extend(pv)
        
        pv = e.pv(tags=[machines.HLA_TAG_Y, machines.HLA_TAG_EPUT])
        print(str(e.name), pv)
        if pv: pvysp.append(pv)
        if isinstance(pv, (str, unicode)): trimpv.append(pv)
        elif pv: trimpv.extend(pv)

    if 'H' in plane and len(pvx) > 0 and len(pvxsp) == 0:
        print("WARNING: no HCOR for horizontal orbit correction", file=sys.stderr)
    if 'V' in plane and len(pvy) > 0 and len(pvysp) == 0:
        print("WARNING: no VCOR for vertical orbit correction", file=sys.stderr)

    if not machines._lat.orm:
        print("ERROR: this lattice setting has no ORM data", file=sys.stderr)
    else:
        correctOrbitPv(list(set(bpmpv)), list(set(trimpv)), machines._lat.orm)


    
def alignQuadrupole(quad, **kwargs):
    """
    align quadrupole with nearby BPM using beam based alignment

    Example::

      >>> alignQuadrupole('Q1')
      >>> alignQuadrupole(['Q1', 'Q2'])
    """
    trim = kwargs.get('trim', None)
    bpm = kwargs.get('bpm', None)
    plane = kwargs.get('plane', 'H')
    dqk1 = kwargs.get('dqk1', 0.05)
    dkick = kwargs.get('dkick', np.linspace(-1e-6, 1e-6, 5).tolist())
    export_figures = kwargs.get('export_figures', True)

    if isinstance(quad, (str, unicode)):
        quadlst = [quad]
    else:
        quadlst = [q for q in quad]
        
    if plane == 'H': trim_type = 'HCOR'
    elif plane == 'V': trim_type = 'VCOR'
    else:
        raise ValueError('Unknnow plane type: "%s"' % plane)

    if trim == None:
        trimlst = []
        for q in quadlst:
            ch = getNeighbors(q, trim_type, 1)
            trimlst.append(ch[0].name)
    else:
        trimlst = [t for t in trim]

    if bpm == None:
        bpmlst = []
        for q in quadlst:
            bpmlst.append(getClosest(q, 'BPM').name)
    else:
        bpmlst = [b for b in bpm]

    # now we get a list of Quad,BPM,Trim names.
    bb = BBA(plane=plane)
    for i in range(len(quadlst)):
        bb.setQuadBpmTrim(quadlst[i], bpmlst[i], trimlst[i], dqk1=dqk1, dkick=dkick)
        
    for i in range(len(quadlst)):
        cva0, cva1 = bb.checkAlignment(i)

        #print "Initial quad value: ", quad.name, quad.value
        bb.alignQuad(i)
        cvb0, cvb1 = bb.checkAlignment(i)

        if export_figures:
            # plot 
            plt.clf()
            plt.plot(cva0[:,-1], (cva1-cva0)[:,0], '-o', label="before BBA")
            plt.plot(cvb0[:,-1], (cvb1-cvb0)[:,0], '-v', label="after BBA")    
            plt.title("Orbit change due to quad")
            plt.savefig("bba-%s-check.png" % quadlst[i])

            bb.exportFigures(i, 'png')
            bb.exportFigures(i, 'pdf')
            #print "final quad value: ", quad.name, quad.value
    return bb.getQuadCenter()

