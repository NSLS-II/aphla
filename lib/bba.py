#!/usr/bin/env python

"""
Beam-Based Alignment
~~~~~~~~~~~~~~~~~~~~~

:author: Lingyun Yang
:license: 

Remember:
1. Kicker has strength limit, check before set.

global:
  full orbit value

each quadrupole alignment:

1. neighbor BPM name, pvrb
2. paired corrector H/V, (name, pvrb, pvsp, [val_list]) * 2
3. quadrupole pvsp, dk1
"""

#from hlalib import getElements, getNeighbors, getDistance, getOrbit
from catools import caget, caput
import time
import numpy as np
import matplotlib.pylab as plt



def _filterSmallSlope(x, y, varcut=1e10):
    """
    Filt half of the points with small slope
    
    - x is 1D
    - y is 2D
    """
    xb = np.mean(x)
    xx = np.correlate(x, x)[0]
    #print xb, xx
    m, n = np.shape(y)
    a = np.zeros(n, 'd')      # slope
    b = np.zeros(n, 'd')      # 
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

class BbaBowtie:
    """
    beam based alignment
    """
    def __init__(self, **kwargs):
        """
        Read config from a big table, link quadrupole, bpm and correctors
        """
        # bpm,trim,quad triplet
        self.bpm, self.quad, self.trim  = None, None, None
        self.quad_pvsp, self.quad_pvrb = None, None
        self.trim_pvsp, self.trim_pvrb = None, None

        self.kick  = kwargs.get('kick', [])
        self.dkick = kwargs.get('dkick', None)
        self._qk1  = None
        self.dqk1  = kwargs.get('dqk1', None)
        self.orbit_pvrb = None
        self.orbit  = None

        self.orbit_diffstd = 1e-7

    def _get_orbit(self):
        return np.array(caget(self.orbit_pvrb))

    def _wait_stable_orbit(self, reforbit, **kwargs):
        """
        set pv to a value, waiting for timeout or the std of monipv is
        greater than diffstd

        - *diffstd* = 1e-7
        - *minwait* = 2
        - *maxwait* =30
        - *step* = 2
        - *diffstd_list* = False whether return the full history of diffstd
        """
        
        diffstd = kwargs.get('diffstd', self.orbit_diffstd)
        minwait = kwargs.get('minwait', 4)
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

    def _calculateKick(self):

        dobt = self.orbit[1,:,:] - self.orbit[0,:,:]
        p, res, rank, sigv, rcond = np.polyfit(dkick, dobt, 1, full=True)
        pavg = np.average(np.abs(p[-1,:]))
        resavg = np.average(np.abs(res))
        pick_c = np.logical_and(abs(p[-1,:])>pavg, res < resavg)
        psub = np.compress(pick_c, p, axis=1)

        return np.average(-psub[-1,:]/psub[-2,:]), pick_c

    def align(self, **kwargs):
        """
        - if dkick is set, kick will be renewed.
        - if dqk1 is set, qk1 will be renewed.
        """

        verbose = kwargs.get('verbose', 0)

        qk0 = caget(self.quad_pvrb)
        xp0 = caget(self.trim_pvrb)

        # ignore kick list if dkick is provided.
        if self.dkick is not None:
            self.kick = [xp0 + dk for dk in self.dkick]
            
        # one more for original orbit
        self.orbit = np.zeros((2, 1+len(self.kick), len(self.orbit_pvrb)), 'd')

        #if verbose: print "qk1= ", qk0, "dqk1=", dqk1
        ##
        ## initial orbit-quad
        obt00 = np.array(caget(self.orbit_pvrb))
        caput(self.quad_pvsp, qk0 + self.dqk1)
        timeout, log = self._wait_stable_orbit(
            obt00, diffstd_list=True, verbose=verbose, 
            diffstd=self.orbit_diffstd)

        obt01 = self._get_orbit()
        self.orbit[0, 0, :] = obt00
        self.orbit[1, 0, :] = obt01

        #print "step down quad"
        caput(self.quad_pvsp, qk0)
        timeout, log = self._wait_stable_orbit(
            obt01, diffstd=self.orbit_diffstd, verbose=verbose, 
            diffstd_list=True)

        obt02 = self._get_orbit()

        # initial qk
        for j,dxp in enumerate(self.kick):
            obt = self._get_orbit()     # for checking orbit changed
            caput(self.trim_pvsp, dxp)
            timeout, log = self._wait_stable_orbit(
                obt, diffstd=self.orbit_diffstd, 
                diffstd_list=True, verbose=verbose)

            obt1 = self._get_orbit()
            self.orbit[0, j+1,:] = obt1

        # adjust qk
        obt = self._get_orbit()
        caput(self.trim_pvsp, xp0)
        caput(self.quad_pvsp, qk0 + self.dqk1)
        timeout, log = self._wait_stable_orbit(
            obt, diffstd=self.orbit_diffstd,
            diffstd_list= True, verbose=verbose)

        obt = self._get_orbit()
        for j,dxp in enumerate(self.kick):
            caput(self.trim_pvsp, dxp)
            timeout, log = self._wait_stable_orbit(
                obt, diffstd=self.orbit_diffstd, 
                diffstd_list=True, verbose=verbose)

            obt = self._get_orbit()
            self.orbit[1, j+1, :] = obt

        #
        #
        import shelve
        import matplotlib.pylab as plt
        dobt = self.orbit[1,1:,:] = self.orbit[0,1:,:]
        x = np.array(self.kick)
        print "Shape:",np.shape(x), np.shape(dobt)
        plt.clf()
        plt.plot(x, dobt, 'ko-')
        plt.savefig("test.png")
        d = shelve.open('test.shelve')
        d['dobt'] = dobt
        d['kick'] = x
        d.close()

        
        if verbose > 0: print "# Calculating ..."
        # calculate the x part
        dkx, maskx = self._calculateKick()

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

    
def align():
    import json
    f = open("../script/data/nsls2_sr_bba.json")
    conf = json.load(f)
    bpmx = conf['orbit_pvx']
    bpmy = conf['orbit_pvy']
    vx, vy = np.array(caget(bpmx)), np.array(caget(bpmy))
    import matplotlib.pylab as plt
    plt.plot(vx)
    plt.plot(vy)
    #

    ac = BbaBowtie()
    for bbconf in conf['bowtie_align']:
        print "Quadrupole:", bbconf['Q'], caget(bbconf['Q'][2])
        ac.quad, s, ac.quad_pvsp, ac.dqk1 = bbconf['Q'][:4]
        for i in range(0, len(bbconf['COR_BPM']), 2):
            ac.bpm, s, ac.bpm_pvrb = bbconf['COR_BPM'][i][:3]
            ac.trim, s, ac.trim_pvsp, obtpv = bbconf['COR_BPM'][i+1][:4]
            ac.quad_pvrb = ac.quad_pvsp
            ac.trim_pvrb = ac.trim_pvsp
            ac.kick = np.linspace(-1e-6, 1e-6, 5)
            ac.orbit_pvrb = conf[obtpv]
            #ca.bpm = conf['
            ac.align()




if __name__ == "__main__":
    #print "Tune X:", caget('SR:C00-Glb:G00<TUNE:00>RB:X')
    #print "Tune Y:", caget('SR:C00-Glb:G00<TUNE:00>RB:Y')
    align()

