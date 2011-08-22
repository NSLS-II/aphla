'''
'''

import time, sys, os, re
import hla
import matplotlib.pylab as plt

hla.machines.initNSLS2VSRTxt()
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
    hla.machines.initNSLS2VSR()
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

if __name__ == '__main__':

    ex02()
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
