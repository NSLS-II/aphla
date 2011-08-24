'''
'''

import time, sys, os, re, shelve
import numpy as np
import matplotlib.pylab as plt

import hla



hla.machines.initNSLS2VSRTxt()
hla.hlalib._wait_for_lock(11)
hla.hlalib._reset_trims()
hla.hlalib._reset_quad()
hla.machines.initNSLS2VSRTwiss()

def ex01():
    hla.machines.use('LTB-txt')
    #elem = hla.getElements('P1')
    #print elem._field
    #print hla.getOrbit()
    #print [e.name for e in hla.getNeighbors('PH2G6C25B', 'P*C10*', 2)]
    #print [e.sb for e in hla.getNeighbors('PH2G6C25B', 'P*C10*', 2)]
    print hla.getOrbit()
    print hla.getOrbit('P*')
    print hla.getOrbit('*')
    print hla.getOrbit('P*C10*')

def ex02():
    #hla.machines.initNSLS2VSR()
    hla.hlalib._reset_trims()
    time.sleep(2)
    #hla.machines.use('LTD1')
    hc = hla.getElements('HCOR')
    print hc[0].status
    print hc[0].pv(tags=[hla.machines.HLA_TAG_X, hla.machines.HLA_TAG_EGET])
    bpmlst = [b.name for b in hla.getElements('BPM')]
    bpmquad = ['PH1G2C04A', 'PH1G2C06A']
    ref = []
    for b in bpmlst:
        if b in bpmquad: ref.append([1e-6, None])
        else: ref.append([0.0, None])
    hla.createLocalBump(bpmlst, 'HCOR', ref, plane='H') 

def ex03():
    """
    measure beta
    """
    if False:
        nux, nuy = hla.getTunes()
        #k1, nu, beta = hla.meastwiss.measBeta('QH1G2C04A', num_points=5)
        k1, nu, beta = hla.meastwiss.measBeta('Q*C0[4-5]*', num_points=5, verbose=1)
    
        # save
        d = shelve.open('ex03.pkl')
        d['nux'] = nux
        d['nuy'] = nuy
        d['k1'] = k1
        d['nu'] = nu
        d['beta'] = beta
        d.close()
    if True:
        d = shelve.open('ex03.pkl', 'r')
        nux, nuy = d['nux'], d['nuy']
        k1, nu = d['k1'], d['nu']
        beta = d['beta']

    npoint, nquad = np.shape(k1)
    
    for i in range(nquad):
        plt.clf()
        plt.plot(k1[:,i], nu[:,2*i] - nux, 'o--')
        plt.plot(k1[:,i], nu[:,2*i+1] - nuy, 'x--')
        plt.savefig('twiss-%02d.png' % i)

        print beta[:,i]
    
    bta = hla.getBeta('*', spos=True)
    s = [q.sb for q in hla.getElements('Q*C0[4-5]*')]
    plt.clf()
    plt.plot(s, beta[0,:], 'o--')
    plt.plot(bta[:,-1], bta[:,0], '-')
    plt.xlim([min(s), max(s)])
    plt.savefig('twiss-beta.png')


def ex04():
    elem = 'P*C0[1-4]*'
    etax, etay = hla.meastwiss.measDispersion(elem, verbose=1)
    eta0 = hla.getEta(elem, spos = True)

    print np.shape(etax), etax
    print np.shape(etay), etay
    plt.clf()
    plt.plot(eta0[:,-1], eta0[:,0], '-', label='Simulation')
    plt.plot(eta0[:,-1], etax, 'o')
    plt.plot(eta0[:,-1], etay, 'x')
    plt.savefig('twiss-eta.png')

    hla.hlalib._release_lock(11)

if __name__ == '__main__':

    ex04()
    sys.exit(0)

    print "reset the trims:"
    trim1 = [e.pv(tags=[hla.machines.HLA_TAG_X, hla.machines.HLA_TAG_EPUT])
             for e in hla.getElements('HCOR')]
    trim2 = [e.pv(tags=[hla.machines.HLA_TAG_Y, hla.machines.HLA_TAG_EPUT])
             for e in hla.getElements('VCOR')]
    hla.catools.caput(trim1+trim2, [0.0]*(len(trim1) + len(trim2)))

    time.sleep(4)

    v0 = hla.getOrbit('P*', spos=True)

    ## part
    #bpm = hla.getElements('P*C1[12]*')
    #trimx = hla.getGroupMembers(['C1[0-9]', 'HCOR'], op='intersection')
    #trimy = hla.getGroupMembers(['C1[0-9]', 'VCOR'], op='intersection')
    #hla.correctOrbit([e.name for e in bpm], [e.name for e in trimx], plane='H')
    #time.sleep(4)
    #hla.correctOrbit([e.name for e in bpm], [e.name for e in trimy], plane='V')
    #time.sleep(4)

    bpm = hla.getElements('P*')
    trim = hla.getGroupMembers(['*', '[HV]COR'], op='intersection')
    print "BPM=", len(bpm), " Trim=", len(trim)
    hla.correctOrbit([e.name for e in bpm], [e.name for e in trim])
    time.sleep(4)
    
    v1 = hla.getOrbit('P*', spos=True)
    plt.clf()
    ax = plt.subplot(211)
    fig = plt.plot(v0[:,-1], v0[:,0], 'r-x', label='X')
    fig = plt.plot(v0[:,-1], v0[:,1], 'g-x', label='Y')
    ax = plt.subplot(212)
    fig = plt.plot(v1[:,-1], v1[:,0], 'r-x', label='X')
    fig = plt.plot(v1[:,-1], v1[:,1], 'g-x', label='Y')
    plt.savefig("hla_tut_orbit_correct.png")
