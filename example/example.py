'''
'''

import time
import hla
import matplotlib.pylab as plt

hla.machines.initNSLS2VSRTxt()
hla.machines.initNSLS2VSRTwiss()


if __name__ == '__main__':
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
