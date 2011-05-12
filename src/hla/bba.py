#!/usr/bin/env python

import ca
import matplotlib.pylab as plt
import numpy as np
import time
import os
import sys
import pickle

"""
Remember:
1. Kicker has strength limit, check before set.
2. Do not start plt.figure() in a loop, mem leak.
3. Bowtie may not appear
4. 
"""


def getFakeOrbit(sindex, goldenx, goldeny):
    """
    Get the orbit with respect to golden orbit.
    """
    obx = np.zeros(len(sindex), 'd')
    oby = np.zeros(len(sindex), 'd')

    x = ca.Get('SR:C00-Glb:G00<ORBIT:00>RB:X')
    y = ca.Get('SR:C00-Glb:G00<ORBIT:00>RB:Y')
    for i, si in enumerate(sindex):
        obx[i] = x[si]
        oby[i] = y[si]
        # offset w.r.t golden orbit
        obx[i] = obx[i] - goldenx[i]
        oby[i] = oby[i] - goldeny[i]
    del x,y
    return obx, oby

def getOrbit(sindex):
    x = ca.Get('SR:C00-Glb:G00<ORBIT:00>RB:X')
    y = ca.Get('SR:C00-Glb:G00<ORBIT:00>RB:Y')
    #print x, y
    obx = np.zeros(len(sindex), 'd')
    oby = np.zeros(len(sindex), 'd')
    for i, si in enumerate(sindex):
        #print x[i], y[i]
        obx[i] = x[si]
        oby[i] = y[si]
    del x,y
    return obx, oby

def randomGoldenOrbit(n, xampl, yampl):
    #goldenx = (2.0*np.random.rand(n) - 1) * xampl
    #goldeny = (2.0*np.random.rand(n) - 1) * yampl
    goldenx = np.zeros(n, 'd')
    goldeny = np.zeros(n, 'd')
    r = open('bba-random.txt').readlines()

    for i,s in enumerate(r):
        goldenx[i] = float(s)
    return goldenx, goldeny

def filtSmallSlope(x, y, varcut=1e10):
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
    def __init__(self, elementTable):
        """
        Read config from a big table, link quadrupole, bpm and correctors
        """
        self.bpmCa, self.bpmIndex, self.bpmS = [], [], []
        self.quadCa, self.quadIndex, self.quadS = [], [], []
        self.hcmCa, self.hcmIndex, self.hcmS = [], [], []
        self.vcmCa, self.vcmIndex, self.vcmS = [], [], []
        self.hcmRange, self.vcmRange = [], []

        rec = open(elementTable, 'r').readlines()
        for s in rec:
            r = s.split()
            self.bpmCa.append(r[0])
            self.bpmIndex.append(int(r[1]))
            self.bpmS.append(float(r[2]))

            self.quadCa.append(r[3])
            self.quadIndex.append(int(r[4]))
            self.quadS.append(float(r[5]))

            self.hcmCa.append(r[6])
            self.hcmIndex.append(int(r[7]))
            self.hcmS.append(float(r[8]))
            self.hcmRange.append([float(r[9]), float(r[10])])

            self.vcmCa.append(r[11])
            self.vcmIndex.append(int(r[12]))
            self.vcmS.append(float(r[13]))
            self.vcmRange.append([float(r[14]), float(r[15])])
        del rec
        self.NQUAD = self.NBPM = len(self.bpmCa)
        # the change of each quad
        self.quadK = [0.0] * self.NQUAD
        self.quadDk = [0.001] * self.NQUAD
        # the range of kicker
        #self.hcmRange = [[-0.0005, 0.0005]] * len(self.hcmCa)
        #self.vcmRange = [[-0.0005, 0.0005]] * len(self.vcmCa)
        self.goldenx, self.goldeny = randomGoldenOrbit(self.NBPM, 1.0e-3, .0e-3)
        self.newgoldenx = self.goldenx.copy()
        self.newgoldeny = self.goldeny.copy()
        #print self.newgoldenx, self.newgoldeny

        self.nkick = 5
        # orbit before/after changing Quad
        self.orbit0 = np.zeros((self.nkick, self.NBPM), 'd')
        self.orbit1 = np.zeros((self.nkick, self.NBPM), 'd')

        # the corrector strength making beam go through center of quad
        self.hcmProper = np.zeros(self.NQUAD, 'd')
        self.vcmProper = np.zeros(self.NQUAD, 'd')

        self.hcmOriginal = np.zeros(self.NQUAD, 'd')
        self.vcmOriginal = np.zeros(self.NQUAD, 'd')

        self.dt = 3 # 3 seconds delay

    def alignBpmQuad(self, iquad):
        if iquad >= self.NQUAD: return None
        #self.quadK[iquad] = ca.Get(self.quadCa[iquad] + ":RB")
        #self.hcmOriginal[iquad] = ca.Get(self.hcmCa[iquad] + ":RB")
        self.quadK[iquad] = ca.Get(self.quadCa[iquad] + ":SP")
        self.hcmOriginal[iquad] = ca.Get(self.hcmCa[iquad] + ":SP")

        truekick = np.zeros((self.nkick, 2), 'd')
        # list of orbit corrector strength
        dxp = np.linspace(self.hcmRange[iquad][0], self.hcmRange[iquad][1], 
                          self.nkick)

        # get orbit at ([kick], qk0)
        print "Kick@qk=%5.2f" % self.quadK[iquad],
        for i,k in enumerate(dxp): 
            print k,
            ca.Put(self.hcmCa[iquad] + ":SP", k)
            time.sleep(self.dt)
            #truekick[i, 0] = ca.Get(self.hcmCa[iquad] + ":RB")
            truekick[i, 0] = ca.Get(self.hcmCa[iquad] + ":SP")
            obx, oby = getFakeOrbit(self.bpmIndex, self.newgoldenx, self.newgoldeny)
            for j,x in enumerate(obx):
                self.orbit0[i,j] = obx[j]
            del obx, oby
        print ""

        # adjust Quad (qk0 -> qk0+delta)
        newquadk = self.quadK[iquad]*(1+self.quadDk[iquad])
        ca.Put(self.hcmCa[iquad] + ":SP", self.hcmOriginal[iquad])
        ca.Put(self.quadCa[iquad] + ":SP", newquadk)
        time.sleep(self.dt)
        print "Change",self.quadCa[iquad],"from",self.quadK[iquad],"to",newquadk
        print "Tune Changed X:", ca.Get('SR:C00-Glb:G00<TUNE:00>RB:X')
        print "Tune Changed Y:", ca.Get('SR:C00-Glb:G00<TUNE:00>RB:Y')
        
        # get orbit at ([kick], qk0+delta)
        print "Kick@qk1=%5.2f" % newquadk,
        for i,k in enumerate(dxp): 
            print k,
            ca.Put(self.hcmCa[iquad] + ":SP", k)
            time.sleep(self.dt)
            #truekick[i, 1] = ca.Get(self.hcmCa[iquad] + ":RB")
            truekick[i, 1] = ca.Get(self.hcmCa[iquad] + ":SP")
            obx, oby = getFakeOrbit(self.bpmIndex, self.newgoldenx, self.newgoldeny)
            for j,x in enumerate(obx):
                self.orbit1[i,j] = obx[j]
            del obx, oby
        print ""

        plt.clf()
        plt.subplot(211)
        plt.plot(truekick[:,0]*1000, 1000*(self.orbit1 - self.orbit0), 'ro-')
        plt.xlabel("kick [mrad]")
        plt.ylabel("dx orbit [mm]")
        #plt.ylabel(r"$\Delta x(K_0\to K_0+\delta K)~[mm]$")
        plt.subplot(212)
        plt.plot(truekick[:,1]*1000, 1000*(self.orbit1 - self.orbit0), 'ro-')
        plt.xlabel("kick [mrad]")
        plt.ylabel("dx orbit [mm]")
        #plt.ylabel(r"$\Delta x(K_0\to K_0+\delta K)~[mm]$")
        plt.savefig("bba-q%05d-03-bowtie.png" % iquad)
        # change the quadrupole
                
        dx = self.orbit1 - self.orbit0
        a, b, isel, iselstrict = filtSmallSlope(truekick[:,1], dx, 1e-12)

        khcm = np.zeros(len(isel), 'd')
        for i,ik in enumerate(isel):
            khcm[i] = -b[ik]/a[ik]

        #plt.figure()
        plt.clf()
        for i in isel:
            plt.plot(1000*truekick[:,1], 1000*(a[i]*truekick[:,1]+b[i]), 'r-')
            plt.plot(1000*truekick[:,1], 1000*(self.orbit1[:,i] - self.orbit0[:,i]), 'ro')
        plt.xlabel("kick [mrad]")
        plt.ylabel("dx [mm]")
        plt.title("Filted half of the lines")
        plt.savefig("bba-q%05d-04-boutie-b.png" % iquad)

        #plt.figure()
        plt.clf()
        for i in isel[:2]:
            plt.plot(1000*truekick[:,1], 1000*(a[i]*truekick[:,1]+b[i]), 'r-')
            plt.plot(1000*truekick[:,1], 1000*(self.orbit1[:,i] - self.orbit0[:,i]), 'ro')
        plt.xlabel("kick [mrad]")
        plt.ylabel("dx [mm]")
        plt.title("Filted half of the lines, sample")
        plt.savefig("bba-q%05d-04-boutie-c.png" % iquad)


        #plt.figure()
        plt.clf()
        n, bins, patches = plt.hist(khcm*1000, 10, 
                                    normed=1, facecolor='green', alpha=0.75)
        plt.xlabel("Proper Kicker strength [mrad]")
        plt.grid(True)
        plt.savefig("bba-q%05d-05-kicker-hist.png" % iquad)

        
        self.hcmProper[iquad] = np.mean(khcm)
        if self.hcmProper[iquad] < self.hcmRange[iquad][1] and self.hcmProper[iquad] > self.hcmRange[iquad][0]:
            L = self.hcmRange[iquad][1] - self.hcmRange[iquad][0]
            self.hcmRange[iquad][1] = self.hcmProper[iquad] + L/6
            self.hcmRange[iquad][0] = self.hcmProper[iquad] - L/6
            print "proper strength of hcm is",np.mean(khcm)
            print "adjust range [mrad] of hcm to",self.hcmRange[iquad][0]*1000, self.hcmRange[iquad][1]*1000
            self.quadDk[iquad] = self.quadDk[iquad]*2

        if len(iselstrict) > len(isel)/2:
            ca.Put(self.hcmCa[iquad] + ":SP", np.mean(khcm))
            time.sleep(self.dt)
            obx1, oby1 = getFakeOrbit(self.bpmIndex, self.newgoldenx, self.newgoldeny)

            ca.Put(self.quadCa[iquad] + ":SP", self.quadK[iquad])
            time.sleep(self.dt)
            obx0, oby0 = getFakeOrbit(self.bpmIndex, self.newgoldenx, self.newgoldeny)

            #plt.figure()
            plt.clf()
            plt.plot(self.bpmS, 1000*(obx1-obx0), 'ro-')
            plt.ylabel("dx [mm]")
            plt.title("Orbit shift with proper kick")
            plt.savefig("bba-q%05d-06-shift-proper-kick.png" % iquad)
            print obx0[iquad], obx1[iquad], self.goldenx[iquad], self.newgoldenx[iquad]
        
            print "Proper kick strength (k/var)", np.mean(khcm), np.var(khcm)
            print "Orbit at aligned quad:", obx0[iquad],self.goldenx[iquad]
            print "Golden orbit change [mm]:", self.newgoldenx[iquad]*1000,
            self.newgoldenx[iquad] = obx0[iquad] + self.newgoldenx[iquad]
            print self.newgoldenx[iquad]*1000

            del obx0, oby0
        #obx0, oby0 = getFakeOrbit(self.bpmIndex, self.goldenx, self.goldeny)
        #obx1, oby1 = getFakeOrbit(self.bpmIndex, self.newgoldenx, self.newgoldeny)

        #plt.figure()
        plt.clf()
        plt.plot(self.bpmS, self.goldenx*1000, 'bx-', label="initial")
        plt.plot(self.bpmS, self.newgoldenx*1000, 'ro-', linewidth=2, label="new")
        plt.legend()
        plt.ylabel("Golden Orbit [mm]")
        plt.xlabel("S [m]")
        plt.savefig("bba-q%05d-07-golden-orbit.png" % iquad)

        #del obx0, oby0, obx1, oby1

        # restore
        ca.Put(self.quadCa[iquad] + ":SP", self.quadK[iquad])
        ca.Put(self.hcmCa[iquad] + ":SP", self.hcmOriginal[iquad])
        time.sleep(self.dt)

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
    
