#!/usr/bin/env python

"""
Response Matrix
----------------------------------

:author: Lingyun Yang
:license:

:class:`~hla.respmat.OrbitRespMat` is an Orbit Response Matrix (ORM) 


"""

import sys, time
import numpy as np

#import matplotlib.pylab as plt
from hlalib import getElements, getPvList, waitChanged, getTunes, eget
from catools import caget, caput, caputwait, Timedout
from apdata import OrmData
import itertools
import logging
logger = logging.getLogger(__name__)

class RmCol:
    """
    One column of RM (Orbit/Tune Response Matrix)
    """

    def __init__(self, resplst, kicker):
        """
        Initialization

        .. highlight:: python

          ormline = RmCol(['BPM1', 'BPM2'], 'trim')
        """

        self.minwait = 4
        self.stepwait = 2
        self.bpmdiffstd = 1e-5
        self.points = 6
        self.resplst = getElements(resplst)
        self.kicker = getElements(kicker)[0]
        self.rawresp = None
        self.mask = None
        self.rawkick = None
        self.m = None
        self.header = None
        self._c = None
        self.unit = None # use lowerlevel unit
        self.maxdk = 1e-4
        self.residuals = None

    def measure(self, respfields, kfield, **kwargs):
        """
        Measure the RM by change one kicker. 

        :param respfields: response fields, a list
        
        """
        verbose = kwargs.get('verbose', 0)
        dklst = kwargs.get('dklst', None)

        kx0 = self.kicker.get(kfield, unitsys=self.unit) # get EPICS value
        wait = (self.minwait, self.stepwait, 0)
        if verbose:
            print "kicker: '%s.%s'= %e" % (self.kicker.name, kfield, kx0) 

        points = self.points
        if dklst is not None:
            points = len(dklst)
            print "Using external dklst:", dklst
        else:
            dklst = np.linspace(-self.maxdk, self.maxdk, points)

        # bpm read out
        ret = np.zeros((points+2, len(self.resplst)*len(respfields)), 'd')
        # initial bpm data
        v0, h = eget(self.resplst, respfields, unitsys=self.unit, header=True)
        #print "v=", v0
        #print "fields=", respfields, h
        ret[0,:] = np.ravel(v0)
        self.header = np.reshape(np.ravel(h), (-1, 2))

        kstrength = np.ones(points+2, 'd') * kx0
        kstrength[1:-1] = [dklst[i] + kx0 for i in range(points)]
        print "Kicker sp:", kstrength
        for i,kx in enumerate(kstrength[1:]):
            v0 = np.ravel(eget(self.resplst, respfields, unitsys=self.unit))
            self.kicker.put(kfield, kx, unitsys=self.unit)
            st = waitChanged(self.resplst, respfields, v0, 
                             wait=wait, diffstd=self.bpmdiffstd)

            v1 = np.ravel(eget(self.resplst, respfields, unitsys=self.unit))
            ret[i+1,:] = v1[:]
            
            if verbose:
                print "kx= % .2e  resp= [% .4e, % .4e], stable= %s" % (
                    kx, min(ret[i+1,:] - ret[0,:]), max(ret[i+1,:]-ret[0,:]),
                    str(st))

            sys.stdout.flush()

        # fit the lines
        p, self.residuals, rank, singular_values, rcond = np.polyfit(
            kstrength[1:-1], ret[1:-1,:], 1, full=True)

        # reset the kicker
        self.kicker.put(kfield, kx0, unitsys=self.unit)
        self.rawkick = kstrength
        self.rawresp = ret
        self.m = p[0,:] # the slope
        self._c = p[1,:] # the constant 



class OrbitRespMat:
    """
    Orbit Response Matrix
    """
    TSLEEP = 8
    fmtdict = {'.hdf5': 'HDF5', '.pkl':'shelve'}

    def __init__(self, bpm, trim):
        """
        Initialize an Orm object with a list of BPMs and Trims

        .. highlight:: python
        
          orm = OrbitRespMat(['BPM1', 'BPM2'], ['TRIM1', 'TRIM2'])
        
        """
        # points for trim setting when calc dx/dkick
        self.ormdata = None

        npts = 6
        self.minwait = 3 # minimum wait 3 seconds
        self.stepwait = 1.5
        self.bpmdiffstd = 1e-5

        self.bpm = getElements(bpm)
        self.trim = getElements(trim)

        self.bpmhdr = None # the header [(name, sb, field, pv=None), ...] 
        self.trimhdr = None # the header [(name, sb, field, pvrb, pvsp), ...] 

        logger.info("bpm rec: %s" % str(self.bpm))
        logger.info("trim rec: %s" % str(self.trim))
        
        # count the dimension of matrix
        #nbpm, ntrim  = len(set(bpm)), len(set(trim))
        nbpmpv, ntrimpv = len(self.bpm), len(self.trim)

        # 3d raw data
        self._raworbit = None #np.zeros((npts+2, nbpmpv, ntrimpv), 'd')
        self._mask = None #np.zeros((nbpmpv, ntrimpv), 'i')
        self._rawkick = None #np.zeros((ntrimpv, npts+2), 'd')
        self.m = None # np.zeros((nbpmpv, ntrimpv), 'd')
        self.unit = None # raw unit
        
    def save(self, filename, fmt = ''):
        """
        save the orm data into one file:
        """
        ormdata = OrmData()
        ormdata.trim = self.trimhdr
        ormdata.bpm = self.bpmhdr
        ormdata.m = self.m
        # protected data of OrmData
        ormdata._raworbit = self._raworbit
        ormdata._mask      = self._mask
        ormdata._rawkick   = self._rawkick
        ormdata.save(filename, format=fmt)
        del ormdata

    def load(self, filename, fmt = ''):
        self.ormdata.load(filename, fmt)


    def measure(self, **kwargs):
        """
        Measure the ORM, ignore the Horizontal(kicker)-Vertical(bpm)
        coupled terms or not.

        :param output:
        :param verbose:
        :param dkick:

        BPM must have both 'x', 'y'
        """
        output  = kwargs.get("output", "orm.hdf5")
        verbose = kwargs.get("verbose", 1)
        maxdk   = kwargs.get("maxdk", 1e-2)
        rflds = kwargs.get("bpmfields", ['x', 'y'])
        trimflds = kwargs.get("trimfields", ['x', 'y'])

        # the header of matrix, this must be same order as 
        # eget(self.bpm, ['x', 'y'])
        self.bpmhdr = [(b.name, b.sb, f) for b in self.bpm for f in rflds]
        self.trimhdr = [(b.name, b.sb, f) for b in self.trim for f in trimflds]

        t_start = time.time()
        self._rawkick = []
        rawobt, rawm, rawkick = [], [], []
        # a flat list of (trim, plane) 
        trimsets = list(itertools.product(self.trim, trimflds))
        for i,krec in enumerate(trimsets):
            kicker, kfld = krec
            if kfld not in kicker.fields(): continue

            t0 = time.time()
            ormline = RmCol(self.bpm, kicker)

            if verbose > 1:
                import matplotlib.pylab as plt
                plt.clf()
                nlines = 0

            if verbose:
                print "%d/%d '%s/%s.%s'" % (
                    i, len(trimsets), rflds, kicker.name, kfld)

            # measure one column of RM
            ormline.measure(rflds, kfld, unitsys=self.unit, **kwargs)
            rawobt.append(ormline.rawresp)
            rawm.append(ormline.m)
            rawkick.append(ormline.rawkick)
            #
            # it is better to skip coupling, at low slop, error is large ...
            nk, nrow = np.shape(ormline.rawresp)
            for j in range(len(self.bpmhdr)):
                x1 = min(ormline.rawresp[1:-1,j])
                x2 = max(ormline.rawresp[1:-1,j])

                #if x2 - x1 < 1e-6: continue
                if np.sqrt(ormline.residuals[j])/(nk-3) < (x2-x1)/10:
                    continue
                # ignore if the coupling is < 0.03
                # if abs(ormline.m[j]) < 0.03 and kfld not in rflds: continue

                bpmname, bpmfield = ormline.header[j]
                if (bpmname, bpmfield) != (self.bpmhdr[j][0], self.bpmhdr[j][2]):
                    raise RuntimeError("inconsistent bpm header %s,%s != %s,%s" \
                                       % (bpmname, bpmfield, self.bpmhdr[j][0], self.bpmhdr[j][2] ))

                # skip checking the coupling matrix elements
                if bpmfield != kfld: continue

                if verbose:
                    print "WARNING: %s.%s/%s.%s orbit=[% .3e, % .3e] slop=%f, r=%e" % (
                        bpmname, bpmfield, kicker.name, kfld, x1, x2,
                        ormline.m[j], ormline.residuals[j])

                if verbose > 1:
                    nlines += 1
                    x, y = ormline.rawkick[1:-1], ormline.rawresp[1:-1,j]
                    plt.plot(x, y, '--o')
                    tx = np.linspace(min(x), max(x), 20)
                    plt.plot(tx, tx*ormline.m[j] + ormline._c[j], '-')
                    plt.xlabel("%s.%s" % (kicker.name, kfld))
                    plt.ylabel("%s.%s" % (bpmname, rflds))

            if verbose > 1 and nlines > 0:
                plt.savefig("orm-t%03d.png" % (i,))

        self.m = np.array(rawm, 'd').T
        self._rawkick = np.array(rawkick, 'd')
        # roll shape from (nkick, npoint, nbpm) to (nbpm, nkick, npoint)
        self._raworbit = np.rollaxis(np.array(rawobt, 'd'), 2, 0)
        # save for every trim settings
        self.save(output)
        t_end = time.time()
        print "-- Time cost: %.2f min" % ((t_end - t_start)/60.0)

    def getBpms(self):
        return [v[0] for v in self.bpm]
    
    def hasBpm(self, bpm):
        """
        check if the bpm is used in this ORM measurement
        """

        for i,b in enumerate(self.bpm):
            if b[0] == bpm: return True
        return False

    def getTrims(self):
        return [v[0] for v in self.trim]
    
    def hasTrim(self, trim):
        """
        check if the trim is used in this ORM measurement
        """
        for i,tr in enumerate(self.trim):
            if tr[0] == trim: return True
        return False

    def maskCrossTerms(self):
        """
        mask the H/V and V/H terms. 

        If the coupling between horizontal/vertical kick and
        vertical/horizontal BPM readings, it's reasonable to mask out
        these coupling terms.
        """

        for i,b in enumerate(self.bpm):
            for j,t in enumerate(self.trim):
                # b[1] = ['X'|'Y'], similar for t[1]
                if b[1] != t[1]: self._mask[i,j] = 1

    def _pv_index(self, pv):
        """
        return pv index of BPM, TRIM
        """
        for i,b in enumerate(self.bpm):
            if b[2] == pv: return i
        for j,t in enumerate(self.trim):
            if t[2] == pv or t[3] == pv:
                return j
        return -1
    
    def update(self, src, masked=False):
        """
        merge two orm into one
        masked = True, update with a masked value
        masked = False, if the new value is masked, skip it.

        rawkick is still updated regardless of masked or not.

        It is advised that both orm use same rawkick for measurement.
        """
        # copy
        bpm, trim = self.bpm[:], self.trim[:]

        for i,b in enumerate(src.bpm):
            if self._pv_index(b[2]) < 0:
                bpm.append(b)
        for j,t in enumerate(src.trim):
            if self._pv_index(t[2]) < 0:
                trim.append(t)
        npts, nbpm0, ntrim0 = np.shape(self._rawmatrix)
        
        nbpm, ntrim = len(bpm), len(trim)
        print "(%d,%d) -> (%d,%d)" % (nbpm0, ntrim0, nbpm, ntrim)
        # the merged is larger
        rawmatrix = np.zeros((npts, nbpm, ntrim), 'd')
        mask      = np.zeros((nbpm, ntrim), 'i')
        rawkick   = np.zeros((ntrim, npts), 'd')
        m         = np.zeros((nbpm, ntrim), 'd')

        rawmatrix[:, :nbpm0, :ntrim0] = self._rawmatrix[:,:,:]
        mask[:nbpm0, :ntrim0]         = self._mask[:,:]
        m[:nbpm0, :ntrim0]            = self.m[:,:]
        # still updating rawkick, even it is masked
        rawkick[:ntrim0, : ]          = self._rawkick[:,:]

        # find the index
        bpmrb = [b[2] for b in bpm]
        trimsp = [t[3] for t in trim]
        ibpm  = [ bpmrb.index(b[2]) for b in src.bpm ]
        itrim = [ trimsp.index(t[3]) for t in src.trim ]
        
        for j, t in enumerate(src.trim):
            jj = itrim[j]
            rawkick[jj,:] = src._rawkick[j,:]
            for i, b in enumerate(src.bpm):
                # next, if not updating with a masked value
                if not masked and src._mask[i,j]: continue
                ii = ibpm[i]
                rawmatrix[:,ii,jj] = src._rawmatrix[:,i,j]
                mask[ii,jj] = src._mask[i,j]
                m[ii,jj] = src.m[i,j]
        self._rawmatrix = rawmatrix
        self._mask = mask
        self._rawkick = rawkick
        self.m = m

        self.bpmrb, self.trimsp = bpmrb, trimsp
        
    def getSubMatrix(self, bpm, trim, flags='XX'):
        """
        if only bpm name given, the return matrix will not equal to
        len(bpm),len(trim), since one bpm can have two lines (x,y) data.
        """
        if not bpm or not trim: return None
        if not flags in ['XX', 'XY', 'YY', 'YX']: return None
        
        bpm_st  = set([v[0] for v in self.bpm])
        trim_st = set([v[0] for v in self.trim])

        # only consider the bpm/trim in this ORM
        bsub = bpm_st.intersection(set(bpm))
        tsub = trim_st.intersection(set(trim))

        if len(bsub) < len(bpm):
            raise ValueError("Some BPMs are absent in orm measurement")
        if len(tsub) < len(trim):
            raise ValueError("Some Trims are absent in orm measurement")
            pass
        
        mat = np.zeros((len(bpm), len(trim)), 'd')
        for i,b in enumerate(self.bpm):
            if b[1] != flags[0] or not b[0] in bpm: continue
            ii = bpm.index(b[0])
            for j,t in enumerate(self.trim):
                if not t[0] in trim or t[1] != flags[1]: continue
                jj = trim.index(t[0])
                mat[ii,jj] = self.m[i,j]

        return mat

    def checkLinearity(self, verbose=0):
        """
        check the linearity of each orm term.

        This routine detects the BPMs which do not reponse to trim well. 
        """
        import matplotlib.pylab as plt
        npoints, nbpm, ntrim = np.shape(self._rawmatrix)

        # unmasked matrix
        um = []
        for i in range(nbpm):
            for j in range(ntrim):
                if self._mask[i,j]: continue
                um.append(self.m[i,j])

        if False:
            plt.clf()
            plt.hist(um, 50, normed=0)
            plt.savefig("orm-hist-m.png")

        res = []
        deadbpm, deadtrim = [], []
        for j in range(ntrim):
            #n = 0
            for i in range(nbpm):
                if self._mask[i, j]: continue

                k = self._rawkick[j, 1:npoints-1]
                m = self._rawmatrix[1:npoints-1, i, j]
                p, residuals, rank, singular_values, rcond = \
                    np.polyfit(k, m, 1, full=True)

                if p[0] < 1e-10: continue
                relerr = abs((p[0] - self.m[i,j])/p[0])
                if verbose:
                    print "%3d,%3d" % (i,j), self.bpm[i][0], self.trim[j][0], \
                        p[0], self.m[i,j], relerr, residuals, rank, \
                        singular_values, rcond

                # check if the reading is repeating.
                distavg = (max(m) - min(m))/(len(m)-1)
                deadreading = False
                for ik in range(1, len(m)):
                    if (m[ik] - m[ik-1]) < 0.05*distavg:
                        deadreading = True

                if residuals[0] > 2e-11:
                    if not i in deadbpm: deadbpm.append(i)
                    if not j in deadtrim: deadtrim.append(j)
                    print i,j, "mask=",self._mask[i,j],residuals[0]
                    plt.clf()
                    plt.plot(k, m, '--o', label="%s/%s" % (
                            self.bpm[i][0], self.trim[j][0]))
                    plt.title("k= %.4f res= %.4e" % (p[0], residuals[0]))
                    plt.savefig("orm-check-m-%04d-%04d.png" % (i,j))
                    if deadreading:
                        self._mask[i,j] = 1

                res.append(residuals[0])
            # end of all bpm
            if not verbose:
                print j,
                sys.stdout.flush()
        print len(res), np.average(res), np.var(res)
        plt.clf()
        plt.hist(np.log10(res), 50, normed=0, log=True)
        plt.savefig("orm-hist-residuals.png")
        print "Dead bpm:", deadbpm
        print "Dead trim:", 
        for i in deadtrim: print self.trim[i][0],
        print ""

    def checkOrbitReproduce(self, bpm, trim):
        print "checking ..."
        print "    bpm:", len(bpm)
        print "    trim:", trim

        # skip the masked value
        itrim, ibpm = [], []
        for i, b in enumerate(self.bpm):
            if b[0] in bpm: ibpm.append(i)
        for i, t in enumerate(self.trim):
            if t[0] in trim: itrim.append(i)
        if len(itrim) == 0:
            # No trim specified.
            return
        
        kick0 = np.zeros(len(itrim), 'd')
        for j,jt in enumerate(itrim):
            # read the setpoint
            kick0[j] = caget(self.trim[jt][3])
        dkick = np.random.rand(len(itrim))*5e-5 + 6e-5

        # get the initial orbit
        x0 = np.zeros(len(ibpm), 'd')
        for i,ib in enumerate(ibpm):
            x0[i] = caget(self.bpm[ib][2])
        
        dx = np.zeros(len(ibpm), 'd')
        for i,ib in enumerate(ibpm):
            for j,jt in enumerate(itrim):
                # skip the masked ORM elements
                if self._mask[ib, jt]: continue
                dx[i] = dx[i] + self.m[ib, jt]*dkick[j]
        for j, jt in enumerate(itrim):
            caput(self.trim[jt][3], kick0[j] + dkick[j])
        time.sleep(self.TSLEEP)

        # get the final orbit
        x1 = np.zeros(len(ibpm), 'd')
        for i,ib in enumerate(ibpm):
            x1[i] = caget(self.bpm[ib][2])
        #print x1

        # reset the trims
        for j,jt in enumerate(itrim):
            caput(self.trim[jt][3], kick0[j])
        time.sleep(self.TSLEEP)

        # return experiment and theory
        return x0, x1, dx

    def __str__(self):
        nbpm, ntrim = np.shape(self.m)
        s = "Orbit Response Matrix\n" \
            " trim %d, bpm %d, matrix (%d, %d)\n" \
            " masked %d / %d" % \
            (len(self.trim), len(self.bpm), nbpm, ntrim,
             np.sum(self._mask), len(self.trim)*len(self.bpm))
        return s


    m = [[], []]
            m[i].append(p[0])
