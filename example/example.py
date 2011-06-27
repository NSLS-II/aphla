'''
'''

import time
import hla
import matplotlib.pylab as plt

hla.initNSLS2VSRTxt()
hla.initNSLS2VSRTwiss()

if __name__ == '__main__':
    print hla.machines.lattices()
    bpm = hla.getElements('P*C1[09]*')
    trim = hla.getGroupMembers(['*', 'TRIMX'], op='intersection')
    
    v0 = hla.getOrbit()
    obt = hla.orbit.Orbit(bpm)
    print obt.bpmx.value
    print hla.machines._lat.orm.bpm
    print hla.machines._lat.orm.trim

    time.sleep(3)

    v1 = hla.getOrbit()

    plt.clf()
    ax = plt.subplot(211)
    fig = plt.plot(s, v0[:,0], 'r-x', label='X')
    fig = plt.plot(s, v0[:,1], 'g-o', label='Y')
    ax = plt.subplot(212)
    fig = plt.plot(s, v1[:,0], 'r-x', label='X')
    fig = plt.plot(s, v1[:,1], 'g-o', label='Y')
    plt.savefig("hla_tut_orbit_correct.png")
