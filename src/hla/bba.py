#!/usr/bin/env python

"""
Beam-Based Alignment
~~~~~~~~~~~~~~~~~~~~~

:author: Lingyun Yang
:license: 

Remember:
1. Kicker has strength limit, check before set.
"""

from hlalib import getElements, getNeighbors, getDistance, getOrbit
from catools import caget, caput
import time
import numpy as np
import matplotlib.pylab as plt



def _filterSmallSlope(x, y, varcut=1e10):
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
    """
    beam based alignment
    """
    def __init__(self, **kwargs):
        """
        Read config from a big table, link quadrupole, bpm and correctors
        """
        # bpm,trim,quad triplet
        self.plane = kwargs.get('plane', 'H')
        self._bpm  = []
        self._quad = kwargs.get('quad', [])
        self._trim = []

        self._rawdkick = []
        self._rawdqk1  = []
        self._rawdorb  = []
        self._kicklim  = []
        self._rawdata  = []
        self._rawdata_mask = []
        self._fitdkick = []
        self._quadcenter = []

        self.orbit_diffstd = 1e-7

        if not self._quad:
            for q in self._quad:
                self._bpm.append(getClosest(q, 'BPM').name)
                self._trim.append(None)
                self._rawdqk1.append([0.0, 0.0])
                self._rawdkick.append([])
                self._fitdkick.append(0.0)
                self._quadcenter.append([0.0, 0.0])
                self._rawdata.append(None)
                self._rawdata_mask.append(None)

    def useBpm(self, bpmname, quadname):
        """
        use bpm for quad
        """
        if not quadname in self._quad:
            raise ValueError('quadrupole "%s" is not in BBA')
        i = self._quad.index(quadname)
        if getElements(bpmname): self._bpm[i] = bpmname

    def useCorrector(self, corrector, quad):
        """
        use corrector for quad
        """
        if not quad in self._quad:
            raise ValueError('quadrupole "%s" is not in BBA')
        i = self._quad.index(quad)
        if getElements(corrector): self._trim[i] = corrector

    def setQuad(self, quadname, dk1, **kwargs):
        """
        clear existing quad, use the new set

        - *dqk1*
        - *autoadd* [True|False] add the quadrupole if does not exist.

        """
        autoadd = kwargs.get('autoadd', False)
        if quadname in self._quad:
            i = self._quad.index(quadname)
            self._rawdqk1[i, 1] = dk1
        elif autoadd:
            self._quad.append(quadname)
            self._bpm.append(getClosest(quadname, 'BPM').name)
            self._trim.append(None)
            self._rawdkick.append([])
            self._rawdqk1.append([0.0, 0.0])
            self._rawdata.append(None)
            self._rawdata_mask.append(None)

    def setQuadBpmTrim(self, quad, bpm, trim, **kwargs):
        """
        set triplet.

        - *bpm* 
        - *quad* 
        - *trim* 
        - *dqk1*
        - *dkick*
        
        create a new record, if quad does not exist.
        """
        
        if quad in self._quad:
            # dqk1, dkick may exist, even it is default value
            dqk1  = kwargs.get('dqk1', False)
            dkick = kwargs.get('dkick', False)

            i = self._quad.index(quad)
            self._bpm[i] = bpm
            self._trim[i] = trim
            if dqk1 != False: self._rawdqk1[i] = [0.0, dqk1]
            if dkick != False: self._rawdkick[i] = dkick
        else:
            dqk1 = kwargs.get('dqk1', 0.0)
            dkick = kwargs.get('dkick', [])
            self._quad.append(quad)
            self._bpm.append(bpm)
            self._trim.append(trim)
            self._rawdqk1.append([0.0, dqk1])
            self._rawdkick.append(dkick)
            self._fitdkick.append(0.0)
            self._quadcenter.append([0.0, 0.0])
            self._rawdata.append(None)
            self._rawdata_mask.append(None)

            #print dqk1, dkick
            #print self._rawdqk1[-1]

    def _wait_stable_orbit(self, reforbit, **kwargs):
        """
        set pv to a value, waiting for timeout or the std of monipv is
        greater than diffstd

        - *diffstd* = 1e-7
        - *minwait* = 2
        - *maxwait* =30
        - *step* = 2
        - *diffstd_list* = False
        """

        diffstd = kwargs.get('diffstd', 1e-7)
        minwait = kwargs.get('minwait', 2)
        maxwait = kwargs.get('maxwait', 30)
        step    = kwargs.get('step', 2)
        diffstd_list = kwargs.get('diffstd_list', False)
        verbose = kwargs.get('verbose', 0)

        t0 = time.time()
        time.sleep(minwait)
        dv = self._get_orbit() - reforbit
        dvstd = [dv.std()]
        timeout = False

        while dv.std() < diffstd:
            time.sleep(step)
            dt = time.time() - t0
            if dt  > maxwait:
                timeout = True
                break
            dv = self._get_orbit() - reforbit
            dvstd.append(dv.std())

        if diffstd_list:
            return timeout, dvstd

    def _calculateKick(self, dkick, data):
        # The last column of nbpm is zero quad change
        ntrim, nquad, nbpm = np.shape(data)

        dobt = data[:,1,:] - data[:,0,:]
        p, res, rank, sigv, rcond = np.polyfit(dkick, dobt, 1, full=True)
        pavg = np.average(np.abs(p[-1,:]))
        resavg = np.average(np.abs(res))
        pick_c = np.logical_and(abs(p[-1,:])>pavg, res < resavg)
        psub = np.compress(pick_c, p, axis=1)

        return np.average(-psub[-1,:]/psub[-2,:]), pick_c

    def _get_orbit(self,**kwargs):
        if self.plane == 'H': return getOrbit()[:,0]
        elif self.plane == 'V': return getOrbit()[:,1]
        else: raise ValueError("BBA does not recognize the plane '%s'" % self.plane)

    def _bowtieAlign(self, iquad, **kwargs):
        verbose = kwargs.get('verbose', 0)

        quad = getElements(self._quad[iquad])
        bpm  = getElements(self._bpm[iquad])
        trim = getElements(self._trim[iquad])

        qk0 = quad.value
        xp0  = trim.value

        self._rawdqk1[iquad][0] = qk0
        dqk1 = self._rawdqk1[iquad][1]
        if verbose: print "qk1= ", qk0, "dqk1=", dqk1
        ##
        ## initial orbit-quad
        obt00 = self._get_orbit()
        quad.value = qk0 + dqk1
        timeout, log = self._wait_stable_orbit(obt00, diffstd_list=True, verbose=verbose, diffstd=self.orbit_diffstd)

        obt01 = self._get_orbit()
        #print "step down quad"
        timeout, log = self._wait_stable_orbit(obt01, diffstd=self.orbit_diffstd, verbose=verbose, diffstd_list=True)

        obt02 = self._get_orbit()

        # 2 quad settings
        ntrimsp, nquadsp, nbpmobt = len(self._rawdkick[iquad]), 2, len(obt00)
        #if verbose: print "trimsteps= %d, quad steps= %d, orbit points= %d" % (ntrimsp, nquadsp, nbpmobt)

        # store orbit
        data = np.zeros((ntrimsp, nquadsp, nbpmobt), 'd')
        quad.value = qk0
        timeout, log = self._wait_stable_orbit(obt02, diffstd=self.orbit_diffstd,
                                               diffstd_list=True, verbose=verbose)

        # initial qk
        for j,dxp in enumerate(self._rawdkick[iquad]):
            xp2 = xp0 + dxp
            obt = self._get_orbit()
            trim.value = xp2
            timeout, log = self._wait_stable_orbit(obt, 
                                                   diffstd=self.orbit_diffstd, 
                                                   diffstd_list=True, verbose=verbose)

            obt1 = self._get_orbit()
            #print j, np.shape(obt1), np.shape(data)
            data[j, 0, :] = obt1[:]

        # adjust qk
        obt = self._get_orbit()
        trim.value = xp0
        quad.value = qk0 + dqk1
        timeout, log = self._wait_stable_orbit(obt, diffstd=self.orbit_diffstd,
                                               diffstd_list= True, verbose=verbose)

        obt = self._get_orbit()
        for j,dxp in enumerate(self._rawdkick[iquad]):
            xp2 = xp0 + dxp
            trim.value = xp2
            timeout, log = self._wait_stable_orbit(obt, diffstd=self.orbit_diffstd, 
                                                   diffstd_list=True, verbose=verbose)

            obt = self._get_orbit()
            data[j, 1, :] = obt[:]

        if verbose > 0: print "# Calculating ..."
        # calculate the x part
        dkx, maskx = self._calculateKick(self._rawdkick[iquad], data)

        # save x part
        self._rawdata[iquad] = data[:,:,:]
        self._rawdata_mask[iquad] = maskx

        self._fitdkick[iquad] = dkx

        obt = self._get_orbit()
        trim.value = xp0 + dkx
        quad.value = qk0
        timeout, log = self._wait_stable_orbit(obt, diffstd=self.orbit_diffstd, diffstd_list=True, verbose=verbose)

        if verbose:
            print "# Set corrector dxp=", dkx

        if self.plane == 'H':
            self._quadcenter[iquad] = bpm.value[0]
            if verbose: print "# Quad center:", self.plane, bpm.value[0]
        elif self.plane == 'V':
            self._quadcenter[iquad] = bpm.value[1]
            if verbose: print "# Quad center:", self.plane, bpm.value[1]
        else: 
            raise ValueError("BBA does not recognize plane '%s'" % self.plane)
        

    def exportFigures(self, iquad, format):
        """
        export the bowtie figure.

        ::

          >>> exportFigures(0, 'png')
          >>> exportFigures(1, ['pdf', 'png'])
        """

        # orbit change due to quad
        d = self._rawdata[iquad]
        dsub = np.compress(self._rawdata_mask[iquad], self._rawdata[iquad], axis=2)

        if isinstance(format, (str, unicode)):
            out = ["bba-%s-%s.%s" % (self._quad[iquad], self.plane, format)]
        else:
            out = ["bba-%s-%s.%s" % (self._quad[iquad], self.plane, fmt) for fmt in format]

        plt.clf()
        plt.subplot(211)
        plt.title("Orbit change due to quad strength change")
        plt.plot(self._rawdkick[iquad], 1.0e6*(d[:,1,:]-d[:,0,:]), 'o-')
        plt.subplot(212)
        plt.plot(self._rawdkick[iquad], 1.0e6*(dsub[:,1,:] - dsub[:,0,:]), 'o-')
        for fmt in out: plt.savefig(fmt)

        
    def alignQuad(self, iquad, **kwargs):
        """
        align the quad
        """
        verbose = kwargs.get('verbose', 0)

        if iquad >= len(self._quad): return None
        return self._bowtieAlign(iquad, verbose=verbose)
    
    def checkAlignment(self, iquad, **kwargs):
        """
        check the orbit shift due to changing quadruple strength.

        - *dqk1*, 0.05, change of quadrupole strength.
        - *wait*, 10, wait 10 seconds to read orbit after changing the quadrupole.
        """
        dqk1 = kwargs.get('dqk1', 0.05)
        wait = kwargs.get('wait', 10)

        v0 = getOrbit(spos = True)
        quad = getElements(self._quad[iquad])
        quad.value = quad.value + dqk1
        time.sleep(wait)
        v1 = getOrbit(spos=True)
        quad.value = quad.value - dqk1
        return v0, v1

    def getQuadCenter(self):
        """
        get the results of alignment
        """
        return self._quadcenter[:]

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
    
    
def align(quad, bpmfamily='BPM', correctorfamily='HCOR'):
    q = getElements(quad)
    bpms = getNeighbors(q.name, bpmfamily, 1)
    print q.name
    for b in bpms:
        print "BPM:", b.name, b.sb - q.sb
    if getDistance(bpms[0].name, q.name) > getDistance(bpms[-1].name, q.name):
        bpm = bpms[-1]
    else:
        bpm = bpms[0]

    cors = getNeighbors(bpm.name, correctorfamily, 1)
    for c in cors:
        print "Corr:", c.name, c.sb - bpm.sb
    hcor = cors[0]

    # we have the bpm and corrector
    print "Ready:"
    print hcor.name, hcor.sb, hcor.value
    print bpm.name, bpm.sb, bpm.value
    print q.name, q.sb, q.value
    
    #hcor.x = 1e-5
    time.sleep(3)
    print bpm.name, bpm.sb, bpm.value
    print q.name, q.sb, q.value
    #hcor.x = 0
    #return None

    k0 = q.value
    k1 = k0 * 1.1

    v0 = getOrbit()
    m,n = np.shape(v0)

    #print v0
    t0 = hcor.x
    t = t0 + np.linspace(-.5e-6, .5e-6, 5)
    va = np.zeros((len(t), m, n), 'd')
    vb = np.zeros((len(t), m, n), 'd')
    for i,t1 in enumerate(t):
        hcor.x = t1
        print i, hcor.x
        time.sleep(4)
        v1 = getOrbit()
        va[i,:,:] = v1[:,:]

    for i in range(m):
        plt.plot(t, va[:,i,0]-v0[i,0], '-o')
    plt.xlabel("Horizontal Kick")
    plt.ylabel("Orbit Shift with Quad(k0)")
    plt.savefig('boutie-1.png')

    time.sleep(5)
    q.value = k1
    time.sleep(5)
    for i,t1 in enumerate(t):
        hcor.x = t1
        time.sleep(4)
        v1 = getOrbit()
        vb[i,:,:] = v1[:,:]

    for i in range(m):
        plt.plot(t, vb[:,i,0]-v0[i,0], '-o')    
    plt.xlabel("Horizontal Kick")
    plt.ylabel("Orbit Shift with Quad(k0+dk)")
    plt.savefig('boutie-2.png')


    q.value = k0
    hcor.x = t0
    
    plt.clf()
    for i in range(m):
        plt.plot(t, vb[:,i,0] - va[:,i,0], '-o')
    plt.xlabel("Horizontal Kick")
    plt.ylabel("Orbit Shift between k1,k0")
    plt.grid(True)
    plt.savefig('boutie.png')




