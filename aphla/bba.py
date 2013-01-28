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

from hlalib import getElements, getNeighbors, getDistance, getOrbit, waitStableOrbit

#from catools import caget, caput
import time
import numpy as np

#import matplotlib.pylab as plt

class BbaBowtie:
    """
    beam based alignment
    """
    def __init__(self, **kwargs):
        """
        Read config from a big table, link quadrupole, bpm and correctors
        """
        # bpm,trim,quad triplet
        self._b, self._bf = kwargs.get("bpm",  [None]*2)
        self._q, self._qf = kwargs.get("quad", [None]*2)
        self._c, self._cf = kwargs.get("cor",  [None]*2)

        self.quad_dkick = kwargs.get("quad_dkick", 0.0)
        self.cor_dkick  = kwargs.get('cor_kick', [])
        self.cor_kick = []

        self.trim_fitted = None

        self.orbit  = None
        self.mask   = None # mask lines that are kept. 
        self.slope  = None
        self.x_intercept = None
        # do not extend for the intersection with x-axis.
        #self.line_segment_only = False  
        self.orbit_diffstd = 1e-6
        self.minwait = 6


    def _get_orbit(self):
        if self._bf == 'x': return getOrbit()[:,0]
        if self._bf == 'y': return getOrbit()[:,1]
        return None

    def _filterLines(self, x, y, p_slope = 0.8, p_xintercept=0.9,
                     p_residual = 0.9):
        """
        filter out the bad data.
        - slope is too small, keep only p_slpe*100 percent.
        - x_interception is too far away from the most candidates (peak of histogram).
        - residual is too large, keep only the smaller p_residual*100 percent.
        """
        m, n = np.shape(y)
        # p[-1] is constant, p[-2] is slope
        p, res, rank, sigv, rcond = np.polyfit(x, y, 1, full=True)
        #print "slope:", p[-2]
        #print "constant:", p[-1]
        #print "xintercept:", -p[-1]/p[-2]
        # keep the larger slope center part
        i1 = int(n*(1.0-p_slope))
        kept1 = np.argsort(np.abs(p[-2,:]))[i1:]
        # keep the residual less than certain percentage
        i1 = int(n*p_residual)
        kept3 = np.argsort(np.abs(res))[:i1]
        # keep the lines with x_intercept smaller than x_intercept*sigma
        xitc = -p[-1,:]/p[-2,:]
        hist, edge = np.histogram(xitc, 10)
        while sum(hist) > n*p_xintercept:
            im = np.argmax(hist)
            if im < 5: rg = edge[0], edge[-2]
            else: rg = edge[1], edge[-1]
            #print im, hist, edge
            hist, edge = np.histogram(xitc, 10, range=rg)
        #
        #print "filter range of hist:", rg
        ikept2 = np.logical_and(xitc > rg[0], xitc < rg[1])

        # take the intersection of 3 filters.
        for i in range(n):
            if i not in kept1: ikept2[i] = False
            if i not in kept3: ikept2[i] = False
            #if self.line_segment_only and (xitc[i] < x[0] or xitc[i] > x[1]):
            #    ikept2[i] = False
        # 
        self.mask = ikept2
        self.slope, self.x_intercept = p[-2,:], xitc
        # the final subset of slope and y_intercept
        psub = np.compress(ikept2, p, axis=1)
        # the proper kicker strength to make beam through center of quad.
        self.trim_fitted = np.average(-psub[-1,:]/psub[-2,:])


    def _measure(self, **kwargs):
        """
        - if dkick is set, kick will be renewed.
        - if dqk1 is set, qk1 will be renewed.
        """

        verbose = kwargs.get('verbose', 0)

        qk0 = self._q.get(self._qf, unit=None)
        xp0 = self._c.get(self._cf, unit=None)

        # ignore kick list if dkick is provided.
        self.cor_kick = [xp0 + dk for dk in self.cor_dkick]

        obt00 = self._get_orbit()
        print "obtshape:", np.shape(obt00)
        self.orbit = np.zeros((2, 1+len(self.cor_dkick), len(obt00)), 'd')
        # one more for original orbit

        #if verbose: print "qk1= ", qk0, "dqk1=", dqk1
        ##
        ## initial orbit-quad
        obtref = getOrbit()
        # change quad
        self._q.put(self._qf, qk0 + self.quad_dkick, unit=None)

        timeout, log = waitStableOrbit(
            obtref, diffstd_list=True, verbose=verbose, 
            diffstd=self.orbit_diffstd, minwait=self.minwait)
        obt01 = self._get_orbit()
        print "   reading orbit", obt01
        # orbit before and after quad inc
        self.orbit[0, 0, :] = obt00[:]
        self.orbit[1, 0, :] = obt01[:]

        #print "step down quad"
        print "-- reset quad:", self._q.name
        obtref = getOrbit()
        self._q.put(self._qf, qk0, unit=None)
        timeout, log = waitStableOrbit(
            obtref,
            diffstd=self.orbit_diffstd, verbose=verbose, 
            diffstd_list=True, minwait=self.minwait)

        print "   reading orbit", getOrbit()
        obt02 = self._get_orbit()

        # initial qk
        for j,dxp in enumerate(self.cor_kick):
            obt = self._get_orbit()     # for checking orbit changed
            print "setting trim:", self._c.name, j, dxp
            obtref = getOrbit()
            self._c.put(self._cf, dxp, unit=None)
            timeout, log = waitStableOrbit(
                obtref,
                diffstd=self.orbit_diffstd, minwait = self.minwait,
                diffstd_list=True, verbose=verbose)
            print "   reading orbit", getOrbit()
            obt1 = self._get_orbit()
            self.orbit[0, j+1,:] = obt1

        # adjust qk
        obt = self._get_orbit()
        print "reset trim, inc quad"
        #caput(self.trim_pvsp, xp0)
        #caput(self.quad_pvsp, qk0 + self.dqk1)
        obtref = getOrbit()
        self._c.put(self._cf, xp0, unit=None)
        self._q.put(self._qf, qk0 + self.quad_dkick, unit=None)
        timeout, log = waitStableOrbit(
            obtref, diffstd=self.orbit_diffstd, minwait = self.minwait,
            diffstd_list= True, verbose=verbose)

        print "  get orbit", getOrbit()
        obt = self._get_orbit()
        for j,dxp in enumerate(self.cor_kick):
            print "setting trim:", self._c.name, j, dxp
            #caput(self.trim_pvsp, dxp)
            obtref = getOrbit()
            self._c.put(self._cf, dxp, unit=None)
            timeout, log = waitStableOrbit(
                obtref, diffstd=self.orbit_diffstd, minwait = self.minwait,
                diffstd_list=True, verbose=verbose)
            print "  reading orbit", getOrbit()
            obt = self._get_orbit()
            self.orbit[1, j+1, :] = obt
        # reset qk
        print "reset quad and trim"
        #caput(self.quad_pvsp, qk0)
        #caput(self.trim_pvsp, xp0)
        self._q.put(self._qf, qk0, unit=None)
        self._c.put(self._cf, xp0, unit=None)


    def align(self, **kwargs):
        """
        """
        # [12:43 PM] (sandbox/venv) $ caget "SR:C30-MG:G02A{Quad:H1}Fld-SP"
        # SR:C30-MG:G02A{Quad:H1}Fld-SP  -0.633004
        # <lyyang@svd>-{/home/lyyang/devel/nsls2-hla
        # [12:45 PM] (sandbox/venv) $ caget "SR:C30-MG:G02A{HCor:H2}Fld-SP"
        # SR:C30-MG:G02A{HCor:H2}Fld-SP  0

        self._measure(**kwargs)
        self._analyze()


    def _analyze(self):
        print "Analyzing BBA"
        #import shelve
        ##import matplotlib.pylab as plt
        #print "FIXME: using hard coded config file: test.shelve", __file__
        #f = shelve.open('/home/lyyang/devel/nsls2-hla/lib/test.shelve', 'r')
        #dobt = f['dobt'][:,:]*1e6
        #x = f['kick']*1e6
        #f.close()
        # nkick, nbpm = np.shape(dobt)
        #plt.plot(x, dobt, 'k-o')
        #plt.savefig('test2.png')
        #self.kick = x
        #self.orbit = np.zeros((2, nkick+1, nbpm), 'd')
        #print np.shape(dobt), np.shape(x), np.shape(self.orbit)
        #self.orbit[1,1:,:] = dobt[:, :]
        dobt = self.orbit[1,1:,:] - self.orbit[0,1:,:]
        self._filterLines(self.cor_kick, dobt)

    def plot(self, axbowtie = None, axhist = None, factor = (1.0, 1.0)):
        """
        export the bowtie figure and histogram for chosen data.
        """

        # plotting
        import matplotlib.pylab as plt
        if axbowtie is None: 
            fig = plt.figure()
            axbowtie = fig.add_subplot(111)
        #print np.shape(psub)
        x = np.array(self.cor_kick) * factor[0]
        y = (self.orbit[1,1:,:] - self.orbit[0,1:,:]) * factor[1]
        axbowtie.plot(x, y, 'ko--', linewidth=0.5, markersize=3)
        axbowtie.set_xlabel("kicker")
        axbowtie.set_ylabel("orbit change")
        axbowtie.grid()
        plt.savefig("test1.png")


        t = np.linspace(min(x)*1.2, max(x)*1.2, 10)
        #p = np.compress(self.mask, self.slope)
        #xitc = np.compress(self.mask, self.x_intercept)
        for i in range(len(self.mask)):
            if not self.mask[i]: continue
            slope2 = self.slope[i]*factor[1]/factor[0]
            yitc = -slope2 * self.x_intercept[i] * factor[0] 
            axbowtie.plot(t, slope2*t + yitc, 'r-')
        # draw the points
        for i in range(len(self.mask)):
            xitc = self.x_intercept[i]*factor[0]
            if self.mask[i]: 
                axbowtie.plot(xitc, 0.0, 'go')
            else:
                axbowtie.plot(xitc, 0.0, 'bx')
        axbowtie.set_xlim(min(t), max(t))
        ##
        if axhist is None: 
            fig = plt.figure()
            axhist = fig.add_subplot(111)
        d1 = np.compress(self.mask, self.x_intercept*factor[0])
        hnbin = 3
        d = (max(d1) - min(d1))/hnbin
        hn,hbins,hpatch = axhist.hist(
            d1, hnbin, normed=False, color='g', 
            facecolor='green', alpha=0.8, histtype='stepfilled', 
            label='filtered')
        hbins2 = hbins.tolist()
        while hbins2[0] > min(self.x_intercept): hbins2.insert(0, hbins2[0] - d)
        while hbins2[-1] < max(self.x_intercept): hbins2.append(hbins2[-1] + d)
        #print hbins2
        axhist.hist(self.x_intercept*factor[0], hbins2, normed=False,
                    histtype='step',
                    linewidth=2, color='b', label='full set')
        axhist.set_xlim(axbowtie.get_xlim())
        axhist.legend()
        axhist.set_xlabel("fitted kicker strength")
        axhist.set_ylabel("count")

        plt.savefig('test5.png')
        #print hn, hbins, hpatch
        #print n, len(kept1), sum(ikept2), len(kept3)

        
    def _check(self, **kwargs):
        """
        check the orbit shift due to changing quadruple strength.

        - *dqk1*, 0.05, change of quadrupole strength.
        """
        pass

    def getQuadCenter(self):
        """
        get the results of alignment
        """
        #return self._quadcenter[:]
        pass
    
if __name__ == "__main__":
    #print "Tune X:", caget('SR:C00-Glb:G00<TUNE:00>RB:X')
    #print "Tune Y:", caget('SR:C00-Glb:G00<TUNE:00>RB:Y')
    #align()
    pass

