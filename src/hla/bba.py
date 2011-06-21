#!/usr/bin/env python

import matplotlib.pylab as plt
import numpy as np
import time
import os
import sys
import pickle

from catools import caget, caput

"""
Remember:
1. Kicker has strength limit, check before set.
2. Do not start plt.figure() in a loop, mem leak.
3. Bowtie may not appear
4. 
"""


def _filtSmallSlope(x, y, varcut=1e10):
    """
    Filt half of the points with small slope
    """
    xb = np.mean(x)
    xx = np.correlate(x, x)[0]
    #print xb, xx
    m, n = np.shape(y)
    a = np.zeros(n, 'd')
    b = np.zeros(n, 'd')
    for i in range(n):
        yb = np.mean(y[:,i])
        yy = np.correlate(y[:,i], y[:,i])[0]
        xy = np.correlate(x, y[:,i])[0]
        # fit y = ax + b
        b[i] = (yb*xx - xb*xy)/(xx - m*xb*xb)
        a[i] = (xy - m*xb*yb)/(xx - m*xb*xb)
        #print a[i], b[i]
        pass
    k = np.median(abs(a))
    bh1 = []
    bh2 = []
    for i in range(n):
        vary = np.var(a[i]*x+b[i] - y[:,i])
        if abs(a[i]) < k: continue

        bh1.append(i)
        if vary < varcut : bh2.append(i)
        #print vary
    return np.array(a), np.array(b), bh1, bh2

class BBA:
    def __init__(self):
        """
        Read config from a big table, link quadrupole, bpm and correctors
        """
        # bpm,trim,quad triplet
        self._bpm  = []
        self._quad = []
        self._trim = []
        self._bcqpv   = []
        self._rawdkick = None
        self._rawdqk1  = None
        self._rawdorb  = None

    def _setBpm(self, bpmpv, bpmname):
        """
        clear existing bpm, use the new set
        """
        self._bpm = []
        N = max([len(bpmname), len(bpmpv)])
        for i in range(N):
            self._bpm.append([bpmpv[i], bpmname[i]])

    def _setTrim(self, trimpv, trimname, dkick):
        """
        clear existing trim, use the new set
        """
        self._trim = []
        N = max([len(trimname), len(trimpv), len(dkick)])
        for i in range(N):
            self._trim.append([trimpv[i], trimpv[i], dkick[i]])

    def _setQuad(self, quadpv, quadname, dqk1):
        """
        clear existing quad, use the new set
        """
        self._quad = []
        N = max([len(quadname), len(quadpv), len(dqk1)])
        for i in range(N):
            self._bpm.append([quadpv[i], quadname[i], dqk1[i]])

    def appendBpmQuadTrim(self, bpms, quads, trims):
        """
        append triplet. each are (pv, name) pair.

        - *bpms* ['bpmpv', 'bpmname']
        - *quads* ['quadpv', 'quadname', (dk1, dk1, ...)]
        - *trims* ['trimpv', 'trimname', (dkick, dkick, ...)]
        """
        self._bpm.append(bpms)
        self._quad.append(quads)
        self._trim.append(trims)
        
    def setBpmQuadTrim(self, bpms, quads, trims):
        """
        """
        self._bpm = bpms
        self._quad = quads
        self._trim = trims
    
    def _set_wait_stable(
        self, pvs, values, monipv, diffstd = 1e-6, timeout=30):
        """
        set pv to a value, waiting for timeout or the std of monipv is
        greater than diffstd
        """
        if isinstance(monipv, str) or isinstance(monipv, unicode):
            pvlst = [monipv]
        else:
            pvlst = monipv[:]

        v0 = np.array(caget(monipv))
        caput(pvs, values)
        dt = 0
        while dt < timeout:
            time.sleep(2)
            v1 = np.array(caget(monipv))
            dt = dt + 2.0
            if np.std(v1 - v0) > diffstd: break
        return dt


    def _calculateKick(self, dkick, data):
        # The last column of nbpm is zero quad change
        ntrim, nquad, nbpm = np.shape(data)
        k, pick = [], []
        for i in range(nquad - 1):
            v = data[:, i, :] - data[:, -1, :]
            p, res, rank, sigv, rcond = \
               np.polyfit(dkick, v, 1, full=True)
            pavg = np.average(np.abs(p[-1,:]))
            resavg = np.average(np.abs(res))
            pick_c = np.logical_and(abs(p[-1,:])>pavg, res < resavg)
            psub = np.compress(pick_c, p, axis=1)
            k.append(np.average(-psub[-1,:]/psub[-2,:]))
            pick.append(pick_c)
        return k, pick

    def _bowtieAlign(self, iquad):
        quadpv = self._quad[iquad][0]
        bpmpv  = self._bpm[iquad][0]
        trimpv = self._trim[iquad][0]
        
        # WARNING: reading using sp channel
        qk0 = caget(quadpv)
        xp0  = caget(trimpv)

        #print xp, qk1
        
        full_bpm_pv = [p[0] for p in self._bpm]
        dqklist = [v for v in self._quad[iquad][2]]
        dqklist.append(0.0)
        #print "bpms: ", len(full_bpm_pv)
        # check how many points in quad and trim
        ntrimsp = len(self._trim[iquad][2])
        nquadsp = len(self._quad[iquad][2]) + 1

        ##
        ## initial orbit-quad
        v00 = np.array(caget(full_bpm_pv))
        #print "step up quad"
        self._set_wait_stable(quadpv, qk1 + .05, full_bpm_pv)
        v01 = np.array(caget(full_bpm_pv))
        #print "step down quad"
        self._set_wait_stable(quadpv, qk1, full_bpm_pv, diffstd=1e-7)
        v02 = np.array(caget(full_bpm_pv))

        # the orbit data is a (ntrim, nquad+1) matrix
        data = np.zeros((ntrimsp, nquadsp, len(full_bpm_pv)), 'd')

        for i,dqk in enumerate(dqklist):
            for j,dxp in enumerate(self._trim[iquad][2]):
                qk2 = dqk + qk1
                xp2 = dxp + xp
                dt = self._set_wait_stable(
                    [quadpv, trimpv], [qk2, xp2], full_bpm_pv)
                data[j,i,:] = caget(full_bpm_pv)

        dk, pick = self._calculateKick(self._trim[iquad][2], data)

        #self._set_wait_stable(quadpv, qk1
        #print dk[0]+xp
        #print "Set new kick"
        self._set_wait_stable(trimpv, xp+dk[0], full_bpm_pv)

        ret = caget(bpmpv)
        v10 = np.array(caget(full_bpm_pv))
        #print "step up quad"
        self._set_wait_stable(quadpv, qk1 + .05, full_bpm_pv, diffstd=1e-7)
        v11 = np.array(caget(full_bpm_pv))
        #print "step down quad"
        self._set_wait_stable(quadpv, qk1, full_bpm_pv, diffstd=1e-7)
        v12 = np.array(caget(full_bpm_pv))

        # orbit change due to quad
        plt.clf()
        plt.subplot(211)
        plt.title("Orbit change due to quad strength change 0.01")
        plt.plot(1.0e6*(v01-v00), 'r-')
        plt.subplot(212)
        plt.plot(1.0e6*(v11-v10), 'g-o')
        plt.savefig("bba-q%05d-orbit-quad.png" % iquad)
        
        #self._set_wait_stable(trimpv, xp, full_bpm_pv)
        print "BPM:", caget(bpmpv), self._quad[iquad]

        plt.clf()
        plt.plot((xp+np.array(self._trim[iquad][2]))*1000,
                 1000*(data[:,0,:] - data[:,-1,:]), 'k--')
        plt.plot((xp+np.array(self._trim[iquad][2]))*1000,
                 1000*np.compress(pick[0], data[:,0,:] - data[:,-1,:], axis=1), 'ro-')
        plt.xlabel("kick [mrad]")
        plt.ylabel("dx orbit [mm]")
        #plt.ylabel(r"$\Delta x(K_0\to K_0+\delta K)~[mm]$")
        plt.savefig("bba-q%05d-03-bowtie.png" % iquad)
        # change the quadrupole
        
        return dk[0], ret
            
    def alignBpmQuad(self, iquad, bowtie=False):
        if iquad >= len(self._quad): return None
        return self._bowtieAlign(iquad)
    
    def __print__(self):
        for i in range(self.NQUAD):
            print self.goldenx[i], self.goldeny[i],self.newgoldenx[i],self.newgoldeny[i]

if __name__ == "__main__":
    bba = BBA("bba.txt")
    nbpm = len(bba.bpmS)

    # 1mm, 1mm randome golden orbit

    plt.figure(1)
    plt.clf()
    plt.plot(bba.bpmS, bba.goldenx, 'ro-')
    plt.plot(bba.bpmS, bba.goldeny, 'gx-')
    plt.savefig("bba-01-initial-fake.png")
    #plt.save("bba.png")

    # produce non-zero orbit condition
    ca.Put('SR:C28-MG:G04A<HCM:M1>Fld:SP', 0.000)
    time.sleep(3)
    #print "Set HCM", ca.Get('SR:C28-MG:G04A<HCM:M1>Fld:RB')
    print "Set HCM", ca.Get('SR:C28-MG:G04A<HCM:M1>Fld:SP')

    obx, oby = getOrbit(bba.bpmIndex)
    print "Tune X:", ca.Get('SR:C00-Glb:G00<TUNE:00>RB:X')
    print "Tune Y:", ca.Get('SR:C00-Glb:G00<TUNE:00>RB:Y')

    plt.figure(2)
    plt.clf()
    plt.plot(bba.bpmS, obx*1000, 'ro-')
    plt.ylabel("Orbit [mm]")
    plt.title("Nonzero orbit")
    plt.savefig("bba-02-initial-true-orbit.png")
    #print obx[0:5]
    print "-------"
    #
    for i in range(len(bba.quadCa)):
    #for i in [9]:
        bba.alignBpmQuad(i)
        print "Tune X @ loop", i, ca.Get('SR:C00-Glb:G00<TUNE:00>RB:X')
        print "Tune Y @ loop", i, ca.Get('SR:C00-Glb:G00<TUNE:00>RB:Y')
        print "Time: ", time.time()/60., "[min]"
        print ""
    #bba.alignBpmQuad(0)
    #bba.alignBpmQuad(0)
    #
    f = open("bba.output", "w")
    for i in range(len(bba.quadCa)):
        f.write("%s %11.4e %11.4e  %11.4e %11.4e  %11.4e %11.4e\n" %  \
                    (bba.quadCa[i], bba.newgoldenx[i], bba.newgoldeny[i],
                     bba.hcmRange[i][0], bba.hcmRange[i][1],
                     bba.vcmRange[i][0], bba.vcmRange[i][1]))

    f.close()

    plt.figure()
    plt.clf()
    plt.plot(bba.bpmS, bba.newgoldenx*1000, 'ro-')
    plt.savefig("bba-09-final-golden.png")

    ca.Put('SR:C28-MG:G04A<HCM:M1>Fld:SP', 0.00)

    time.sleep(3)
    obx, oby = getOrbit(bba.bpmIndex)
    
    plt.figure(20)
    plt.clf()
    plt.plot(bba.bpmS, obx*1000, 'ro-')
    plt.ylabel("Orbit [mm]")
    plt.savefig("bba-10-final-orbit.png")
    print "Orbit:", np.var(obx)
    #plt.show()

    print "Tune X:", ca.Get('SR:C00-Glb:G00<TUNE:00>RB:X')
    print "Tune Y:", ca.Get('SR:C00-Glb:G00<TUNE:00>RB:Y')
    
    
