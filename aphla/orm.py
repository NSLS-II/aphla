#!/usr/bin/env python

"""
Response Matrix
----------------------------------

:author: Lingyun Yang
:license:

:class:`~hla.orm.Orm` is an Orbit Response Matrix (ORM) 


"""

import sys, time
import numpy as np

#import matplotlib.pylab as plt
from hlalib import getElements, getPvList
from catools import caget, caput, caputwait, Timedout
from ormdata import OrmData

import logging
logger = logging.getLogger(__name__)

class Orm:
    """
    Orbit Response Matrix
    """
    TSLEEP = 8
    fmtdict = {'.hdf5': 'HDF5', '.pkl':'shelve'}
    def __init__(self, bpm, trim):
        """
        Initialize an Orm object with a list of BPMs and Trims

        .. highlight:: python
        
          orm = Orm(['BPM1', 'BPM2'], ['TRIM1', 'TRIM2'])
        
        """
        # points for trim setting when calc dx/dkick
        self.ormdata = None

        npts = 6
        self.minwait = 3 # minimum wait 3 seconds
        self.stepwait = 1.5
        self.bpmdiffstd = 1e-5

        self.trimsp, self.bpmrb = None, None

        if trim and bpm:
            logger.info("bpm: %s" % str(bpm))
            logger.info("trim: %s" % str(trim))
            # get the list of (name, 'X', pvread, pvset)
            self.trim = self._get_trim_pv_record(trim)
            self.bpm  = self._get_bpm_pv_record(bpm)
        else:
            self.bpm = []
            self.trim = []

        logger.info("bpm rec: %s" % str(self.bpm))
        logger.info("trim rec: %s" % str(self.trim))
        
        # count the dimension of matrix
        #nbpm, ntrim  = len(set(bpm)), len(set(trim))
        nbpmpv, ntrimpv = len(self.bpm), len(self.trim)

        # 3d raw data
        self._rawmatrix = np.zeros((npts+2, nbpmpv, ntrimpv), 'd')
        self._mask = np.zeros((nbpmpv, ntrimpv), 'i')
        self._rawkick = np.zeros((ntrimpv, npts+2), 'd')
        self.m = np.zeros((nbpmpv, ntrimpv), 'd')

        
    def _get_bpm_pv_record(self, bpm):
        """
        given patter of bpm, return (name, 'X', pvrb) 
        """
        ret = []
        for bpm in getElements(bpm):
            for pv in bpm.pv(field='x', handle='readback'):
                ret.append((bpm.name, bpm.sb, 'x', pv))
            for pv in bpm.pv(field='y', handle='readback'):
                ret.append((bpm.name, bpm.sb, 'y', pv))
        return ret

    def _get_trim_pv_record(self, trim):
        """
        given patter of bpm, return (name, 'X', pvrb) 
        """
        ret = []
        for trim in getElements(trim):
            pvrb = trim.pv(field='x', handle='readback')
            pvsp = trim.pv(field='x', handle='setpoint')
            for i in range(len(pvsp)):
                ret.append((trim.name, trim.sb, 'x', pvrb[i], pvsp[i]))

            pvrb = trim.pv(field='y', handle='readback')
            pvsp = trim.pv(field='y', handle='setpoint')
            for i in range(len(pvsp)):
                ret.append((trim.name, trim.sb, 'y', pvrb[i], pvsp[i]))
        return ret

    
            
    def save(self, filename, fmt = ''):
        """
        save the orm data into one file:
        """
        ormdata = OrmData()
        ormdata.trim = self.trim
        ormdata.bpm = self.bpm
        ormdata.m = self.m
        # protected data of OrmData
        ormdata._rawmatrix = self._rawmatrix
        ormdata._mask      = self._mask
        ormdata._rawkick   = self._rawkick
        ormdata.save(filename, fmt)
        del ormdata

    def load(self, filename, fmt = ''):
        self.ormdata.load(filename, fmt)


    def _meas_orbit_rm4(self, kickerpv, bpmpvlist, mask,
                         kref = 0.0, dkick = 1e-4, verbose = 0, points=6):
        """
        Measure the RM by change one kicker. 
        """

        kx0 = caget(kickerpv)
        wait = (self.minwait, self.stepwait)
        if verbose:
            print "kicker: read %f rb(write) %f" % (kref, kx0) 
        # bpm read out
        ret = np.zeros((points+2, len(bpmpvlist)), 'd')
        # initial bpm data
        ret[0,:] = caget(bpmpvlist)
        if verbose:
            print "% .2e %s % .4e" % (kx0, bpmpvlist[0], ret[0,0])
        
        kstrength = np.ones(points+2, 'd') * kx0
        kstrength[1:-1] = np.linspace(kx0-2*dkick, kx0+2*dkick, points)
        for i,kx in enumerate(kstrength[1:]):
            st = caputwait(kickerpv, kx, bpmpvlist, wait=wait, diffstd=self.bpmdiffstd)
            ret[i+1,:] = caget(bpmpvlist)
            for j,bpm in enumerate(bpmpvlist):
                if mask[j]: ret[i+1,j] = 0
            if verbose:
                print "% .2e %s % .4e stable= %s" % (kx, bpmpvlist[0], ret[i+1,0], str(st))
            sys.stdout.flush()

        return np.array(kstrength), ret


    def measure_update(self, bpm, trim, verbose=0, dkick=2e-5):
        """
        remeasure the ORM data with given bpm and trim, ignore the
        bpm/trim not defined before.
        """

        bpmrb = [b[2] for b in self.bpm]
        for i,t in enumerate(self.trim):
            if not t[0] in trim: continue
            #trim_pv_rb = t[2]
            trim_pv_sp = t[3]
            kickref = caget(trim_pv_sp)
            if verbose:
                print "%3d/%d %s" % (i,len(self.trim),trim_pv_sp),
            try:
                kstrength, ret = self._meas_orbit_rm4(
                    trim_pv_sp, bpmrb, mask = self._mask[:,i], kref=kickref,
                    dkick = dkick, verbose=verbose)
            except Timedout:
                raise Timedout

            # polyfit
            p, residuals, rank, singular_values, rcond = \
                np.polyfit(kstrength[1:-1], ret[1:-1,:], 1, full=True)

            ###
            ### it is better to skip coupling, at low slop, error is large ...
            for j in range(len(self.bpm)):
                if residuals[j] < 1e-10: continue
                if verbose:
                    print "WARNING", trim_pv_sp, self.trim[i][0], \
                        self.bpm[j][0], self.bpm[j][1], p[0,j], residuals[j]
                logger.warn("%s %s %s %s %s resi= %s" % (
                        str(trim_pv_sp), str(self.trim[i][0]), 
                        str(self.bpm[j][0]), str(self.bpm[j][1]), str(p[0,j]),
                        str(residuals[j])))
                                                   
                if False:
                    import matplotlib.pylab as plt
                    plt.clf()
                    plt.subplot(211)
                    plt.plot(1e3*kstrength[1:-1], 1e3*ret[1:-1,j], '--o')
                    tx = np.linspace(min(kstrength), max(kstrength), 20)
                    plt.plot(1e3*tx, 1e3*(tx*p[0,j] + p[1,j]), '-')
                    plt.xlabel("kick [mrad]")
                    plt.ylabel("orbit [mm]")
                    plt.subplot(212)
                    # predicted(fitted) y offset
                    y1 = kstrength[1:-1]*p[0,j] + p[1,j]
                    plt.plot(1e3*kstrength[1:-1], 1e6*(ret[1:-1,j] - y1), '--x')
                    plt.xlabel("kick [mrad]")
                    plt.ylabel("orbit diff [um]")
                    plt.savefig("orm-t%03d-b%03d.png" % (i,j))

            self._rawkick[i, :] = kstrength[:]
            for j,b in enumerate(self.bpm):
                if not b[0] in bpm: continue
                self._rawmatrix[:,j,i] = ret[:,j]
                self.m[j,i] = p[0,j]
                
    def measure(self, **kwargs):
        """
        Measure the ORM, ignore the Horizontal(kicker)-Vertical(bpm)
        coupled terms or not.

        :param output:
        :param verbose:
        :param dkick:
        """
        output  = kwargs.get("output", "orm.hdf5")
        verbose = kwargs.get("verbose", 1)
        dkick   = kwargs.get("dkick", 2e-5)
        t_start = time.time()
        
        bpmrb = [b[-1] for b in self.bpm]
        for i, rec in enumerate(self.trim):
            t0 = time.time()
            # get the readback of one trim
            trim_pv_rb = rec[-2]
            trim_pv_sp = rec[-1]
            kickref = caget(trim_pv_sp)

            if verbose:
                print "%3d/%d %s" % (i, len(self.trim), trim_pv_sp),
            try:
                kstrength, ret = self._meas_orbit_rm4(
                    trim_pv_sp, bpmrb, mask = self._mask[:,i], kref=kickref,
                    dkick = dkick, verbose=verbose)
                #if True:
                #    print "%3d/%d %.2f" % (i,len(self.trim), time.time()-t0), 
                #    t0 = time.time()
            except Timedout:
                raise Timedout
            if verbose:
                print ""
                sys.stdout.flush()
        
            # polyfit
            p, residuals, rank, singular_values, rcond = \
                np.polyfit(kstrength[1:-1], ret[1:-1,:], 1, full=True)

            ###
            ### it is better to skip coupling, at low slop, error is large ...
            for j in range(len(self.bpm)):
                if residuals[j] < 1e-11: continue
                print "WARNING", trim_pv_sp, self.trim[i][0], \
                    self.bpm[j][0], self.bpm[j][1], p[0,j], residuals[j]
                if False:
                    import matplotlib.pylab as plt
                    plt.clf()
                    plt.subplot(211)
                    plt.plot(1e3*kstrength[1:-1], 1e3*ret[1:-1,j], '--o')
                    tx = np.linspace(min(kstrength), max(kstrength), 20)
                    plt.plot(1e3*tx, 1e3*(tx*p[0,j] + p[1,j]), '-')
                    plt.xlabel("kick [mrad]")
                    plt.ylabel("Orbit [mm]")
                    plt.subplot(212)
                    # predicted(fitted) y offset
                    y1 = kstrength[1:-1]*p[0,j] + p[1,j]
                    plt.plot(1e3*kstrength[1:-1], 1e6*(ret[1:-1,j] - y1), '--x')
                    plt.xlabel("kick [mrad]")
                    plt.ylabel("Orbit diff [um]")
                    plt.savefig("orm-t%03d-b%03d.png" % (i,j))
                    
            self._rawkick[i, :] = kstrength[:]
            self._rawmatrix[:,:,i] = ret[:,:]
            #self.m[:,i] = v[:]
            self.m[:,i] = p[0,:]
            if False:
                plt.clf()
                for j in range(len(self.bpm)):
                    # skip the coupling
                    if rec[1] != self.bpm[j][1]: continue
                    plt.plot(self._rawkick[i,:]*1e6, ret[:,j]*1e3, '-o')
                plt.savefig("orm-kick-%s.png" % rec[0])

            time.sleep(self.TSLEEP)

            # save for every trim settings
            self.save(output)
            if not verbose:
                print "%3d/%d %s %.1f sec" % \
                    (i,len(self.trim),trim_pv_sp, time.time() - t0)
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

