#!/usr/bin/env python

"""
:author: Lingyun Yang <lyyang@bnl.gov>
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

from hlalib import (getElements, getNeighbors, getDistance, getOrbit, 
    waitStableOrbit, waitRamping)

import time
import numpy as np
import logging
_logger = logging.getLogger(__name__)

class BbaBowtie:
    """beam based alignment with bowtie plot method (ALS)

    For each pair of neighboring (BPM,Quad), a corrector is scanned. The beam
    is kicked and through different offset of BPM and Quad. We assume the BPM
    reading is approximately same as the beam position in the paired nearby
    Quad. Depending on the beam offset, changing the quadrupole strength will
    bring extra kick to the beam. Unless the beam is kicked through the center
    of that quadrupole. This algorithm fits a line for a proper corrector
    strength which kicks the beam through the center of the quadrupole. When
    this strength applied, the BPM reading is the center of that quadrupole.
 
    Examples
    ---------
    >>> quadname = 'qh1g2c02a'
    >>> quad = getExactElement(quadname)
    >>> bpm = getClosest(quadname, 'BPM')
    >>> 'par = {'bpm':

    """
    def __init__(self, bpm, quad, cor, **kwargs):
        """
        Read config from a big table, link quadrupole, bpm and correctors
        """
        # bpm,trim,quad triplet
        self._b, self._bf = bpm
        self._q, self._qf = quad
        self._c, self._cf = cor

        self.quad_dkick = kwargs.get("quad_dkick", 0.0)
        self.cor_dkicks  = kwargs.get('cor_dkicks', [])
        self.cor_kick = []
        self.bpm_cob = []

        # the initial values of C/BPM/Q reading
        self._vc0, self._vb0, self._vq0 = None, None, None
        self.cor_fitted = None
        self.bpm_fitted = None

        self.orbit  = None
        self.mask   = None # mask lines that are kept. 
        self.slope  = None
        self.x_intercept = None
        # do not extend for the intersection with x-axis.
        #self.line_segment_only = False  
        self.wait = kwargs.get("wait", 2)

    def _get_orbit(self):
        if self._bf == 'x':
            return getOrbit()[:,0]
        elif self._bf == 'y':
            return getOrbit()[:,1]
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
        assert len(x) == m, "different size of x, y ({0} != {1})".format(len(x), m)
        #print "fitting x:", x
        #print "fitting y:", y
        # p[-1] is constant, p[-2] is slope
        p, res, rank, sigv, rcond = np.polyfit(x, y, 1, full=True)
        #print "slope:", p[-2]
        #print "constant:", p[-1]
        #print "xintercept:", np.average(-p[-1]/p[-2])
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
        self.cor_fitted = np.average(-psub[-1,:]/psub[-2,:])

        return self.cor_fitted

    def _measure(self, **kwargs):
        """
        - if dkick is set, kick will be renewed.
        - if dqk1 is set, qk1 will be renewed.
        - Ieps, compare readback and setpoint
        """
        #print __file__, "measuring bba"
        verbose = kwargs.get('verbose', 0)
        sample = kwargs.get('sample', 1)

        # record the initial values
        self._vb0 = self._b.get(self._bf, unitsys=None)
        self._vq0 = self._q.get(self._qf, handle="setpoint", unitsys=None)
        self._vc0 = self._c.get(self._cf, handle="setpoint", unitsys=None)
        if verbose > 0:
            print "getting q={0}  c={1}".format(self._vq0, self._vc0)

        # ignore kick list if dkick is provided.
        self.cor_kick = [self._vc0 + dk for dk in self.cor_dkicks]
        if not self.cor_kick:
            _logger.warn("no cor setpoints specified")
            return
        if verbose > 0:
            print "cor setpoints: {0}".format(self.cor_kick)
        obt00 = self._get_orbit()
        #print "obtshape:", np.shape(obt00)
        self.orbit = np.zeros((len(obt00), 1+2*len(self.cor_kick)), 'd')
        # one more for original orbit
        ##
        ## initial orbit-quad
        for i,dqk in enumerate([0.0, self.quad_dkick]):
            # change quad
            self._q.put(self._qf, self._vq0 + dqk, unitsys=None)
            #time.sleep(self.wait)
            #self._q.put(self._qf, self._vq0 + dqk, unitsys=None)
            waitRamping(self._q, wait = self.wait)
            _logger.info("{0} Quad sp= {1} rb= {2}".format(i,
                    self._q.get(self._qf, handle="setpoint", unitsys=None),
                    self._q.get(self._qf, unitsys=None)))
            if verbose > 0:
                print "setting {0}.{1} to {2} (delta={3})".format(
                self._q.name, self._qf, self._vq0 + dqk, self.quad_dkick)
                
            for j,dck in enumerate(self.cor_kick):
                self._c.put(self._cf, dck, unitsys=None)
                #time.sleep(self.wait)
                #self._c.put(self._cf, dck, unitsys=None)
                waitRamping(self._c, wait = self.wait)
                time.sleep(0.5)
                c1sp = self._c.get(self._cf, handle="setpoint", unitsys=None)
                c1rb = self._c.get(self._cf, unitsys=None)
                _logger.info("{0}.{1} sp= {2} rb= {3}".format(i, j, c1sp, c1rb))
                if verbose > 0:
                    print "setting {0}.{1} to {2} (rb= {3})".format(
                        self._c.name, self._cf, dck, c1rb)
                tobt = np.zeros(len(obt00), 'd')
                for jj in range(sample):
                    tobt[:] = tobt[:] + self._get_orbit()
                k = i * len(self.cor_kick) + j
                self.orbit[:,k] = tobt/sample
                #print np.min(tobt/sample), np.max(tobt/sample)
                self.bpm_cob.append(self._b.get(self._bf, unitsys=None))
        # reset qk
        if verbose > 0:
            print "reset quad and trim to %f %f" % (self._vq0, self._vc0)
        #caput(self.quad_pvsp, qk0)
        #caput(self.trim_pvsp, xp0)
        self._q.put(self._qf, self._vq0, unitsys=None)
        self._c.put(self._cf, self._vc0, unitsys=None)
        waitRamping([self._c, self._q], wait = self.wait)
        _logger.info("restoring {0} Quad sp= {1} rb= {2}".format(
                self._q.name, 
                self._q.get(self._qf, handle="setpoint", unitsys=None),
                self._q.get(self._qf, unitsys=None)))
        _logger.info("restoring {0} Cor sp= {1} rb= {2}".format(
                self._c.name, 
                self._c.get(self._cf, handle="setpoint", unitsys=None),
                self._c.get(self._cf, unitsys=None)))

        self.orbit[:,-1] = self._get_orbit()
        self.bpm_cob.append(self._b.get(self._bf, unitsys=None))
        _logger.info("measurement done: " \
                         "q={0}, dq={1}, b={2}, c={3}, dc={4}".format(
                self._q.name, self.quad_dkick,
                self._b.name, self._c.name, self.cor_dkicks))


    def align(self, **kwargs):
        """align"""
        # [12:43 PM] (sandbox/venv) $ caget "SR:C30-MG:G02A{Quad:H1}Fld-SP"
        # SR:C30-MG:G02A{Quad:H1}Fld-SP  -0.633004
        # <lyyang@svd>-{/home/lyyang/devel/nsls2-hla
        # [12:45 PM] (sandbox/venv) $ caget "SR:C30-MG:G02A{HCor:H2}Fld-SP"
        # SR:C30-MG:G02A{HCor:H2}Fld-SP  0
        from cothread.catools import caget, caput
        #print __file__, "BBA align", caget('V:2-SR:C30-BI:G2{PH1:11}SA:X')
        self._measure(**kwargs)
        self._analyze()
        if not self.cor_fitted:
            _logger.warn("no cor fitted. abort.")
            return
        # 
        # change cor
        if kwargs.get("noset", False):
            self._c.put(self._cf, self.cor_fitted, unitsys=None)
            waitRamping(self._c, wait = self.wait)
            self.bpm_fitted = self._b.get(self._bf, unitsys = None)
            # use new values ? or the original one
            self._c.put(self._cf, self._vc0, unitsys=None)
            waitRamping(self._c, wait = self.wait)


    def _analyze(self):
        #print "Analyzing BBA"
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
        if not self.cor_kick:
            _logger.warn("no cor setpoint to analyze")
            return
        #print self.cor_kick
        n = len(self.cor_kick)
        dobt = np.transpose(self.orbit[:,n:2*n] - self.orbit[:,:n])
        #print "dObt: min", np.min(dobt, axis=1)
        #print "dObt: max", np.max(dobt, axis=1)
        #print "dObt: var", np.var(dobt, axis=1)
 
        kick = self._filterLines(self.cor_kick, dobt)

    def plot(self, axbowtie = None, axhist = None, factor = (1.0, 1.0)):
        """
        export the bowtie figure and histogram for chosen data.
        """

        # plotting
        import matplotlib.pylab as plt
        if axbowtie is None: 
            fig = plt.figure()
            axbowtie = fig.add_subplot(111)
        else:
            axbowtie.cla()
        #print np.shape(psub)
        x = np.array(self.cor_kick) * factor[0]
        y = (self.orbit[1,1:,:] - self.orbit[0,1:,:]) * factor[1]
        axbowtie.plot(x, y, 'ko--', linewidth=0.5, markersize=3)
        axbowtie.set_xlabel("kicker (x{0})".format(factor[0]))
        axbowtie.set_ylabel("orbit change (x{0})".format(factor[1]))
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
        else:
            axhist.cla()

        d1 = np.compress(self.mask, self.x_intercept*factor[0])
        hnbin = 3
        d = (max(d1) - min(d1))/hnbin
        hn,hbins,hpatch = axhist.hist(
            d1, hnbin, normed=False, color='g', 
            facecolor='green', alpha=0.8, histtype='stepfilled', 
            label='filtered')
        hbins2 = hbins.tolist()
        #print "bins:", min(hbins2), max(hbins2)
        #print hn, hpatch, hbins
        while hbins2[0] > min(self.x_intercept): hbins2.insert(0, hbins2[0] - d)
        while hbins2[-1] < max(self.x_intercept): hbins2.append(hbins2[-1] + d)
        #print hbins2
        hn, edges, hpatch = axhist.hist(
            self.x_intercept*factor[0], hbins2, normed=False,
            histtype='step',
            linewidth=2, color='b', label='full set')
        axbowtie.set_xlim(axhist.get_xlim())
        #axhist.legend()
        axhist.set_xlabel("fitted kicker strength (x{0})".format(factor[0]))
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

    def save(self, output, group = "BeamBasedAlignment", iloop = 0):
        """
        save the result to HDF5 file
        """
        import h5py
        h5f = h5py.File(output)
        pgrp = h5f.require_group(group)
        grpname = "{0}.{1}-{2}.{3}-{4}.{5}_{6}".format(
            self._b.name, self._bf,
            self._q.name, self._qf,
            self._c.name, self._cf, iloop)
        if grpname in pgrp:
            del pgrp[grpname]
        grp = pgrp.create_group(grpname)
        grp["orbit"] = self.orbit
        grp['keep']  = self.mask
        grp['cor_fitted'] = self.cor_fitted
        grp['cor_kick']   = self.cor_kick
        grp['cor_dkicks'] = self.cor_dkicks
        grp['quad_dkick'] = self.quad_dkick
        grp['bpm_cob']    = self.bpm_cob
        grp["slope"] = self.slope
        grp["x_intercept"] = self.x_intercept
        grp.attrs["bpm"]  = self._b.name
        grp.attrs["quad"] = self._q.name
        grp.attrs["cor"]  = self._c.name
        grp.attrs["bpm_field"]  = self._bf
        grp.attrs["quad_field"] = self._qf
        grp.attrs["cor_field"]  = self._cf
        grp.attrs["iloop"] = iloop
        grp.attrs["_FORMAT_"] = 2
