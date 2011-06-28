#!/usr/bin/env python

"""
Response Matrix
----------------------------------

:author: Lingyun Yang
:license:

:class:`~hla.orm.Orm` is an Orbit Response Matrix (ORM) 


"""

import os, sys, time
from os.path import join, splitext
import numpy as np
import shelve

import machines
import matplotlib.pylab as plt

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
        npts = 6

        self.bpm = []
        self.trim = []
        
        if trim and bpm:
            # one trim may have two (x/y) pv or one only
            el = machines._lat.getElements(trim)
            ex = [(e.name, 'X',
                   e.pv(tags=[machines.HLA_TAG_X, machines.HLA_TAG_EGET]),
                   e.pv(tags=[machines.HLA_TAG_X, machines.HLA_TAG_EPUT]))
                  for e in el]
            ey = [(e.name, 'Y',
                   e.pv(tags=[machines.HLA_TAG_Y, machines.HLA_TAG_EGET]),
                   e.pv(tags=[machines.HLA_TAG_Y, machines.HLA_TAG_EPUT]))
                  for e in el]
            self.trim = [ e for e in ex + ey if e[2] and e[3] ]

            el = machines._lat.getElements(bpm)
            ex = [(e.name, 'X',
                   e.pv(tags=[machines.HLA_TAG_X, machines.HLA_TAG_EGET]))
                  for e in el]
            ey = [(e.name, 'Y',
                   e.pv(tags=[machines.HLA_TAG_Y, machines.HLA_TAG_EGET]))
                  for e in el]
            self.bpm = [ e for e in ex + ey if e[2] ]


        # count the dimension of matrix
        nbpm, ntrim  = len(set(bpm)), len(set(trim))
        nbpmpv, ntrimpv = len(self.bpm), len(self.trim)

        # 3d raw data
        self._rawmatrix = np.zeros((npts+2, nbpmpv, ntrimpv), 'd')
        self._mask = np.zeros((nbpmpv, ntrimpv), 'i')
        self._rawkick = np.zeros((ntrimpv, npts+2), 'd')
        self.m = np.zeros((nbpmpv, ntrimpv), 'd')

        #print __file__, "Done initialization"
        
    def save(self, filename, format = ''):
        """
        save the orm data into one file:
        """
        self.ormdata.save(filename, format)

    def load(self, filename, format = ''):
        self.ormdata.load(filename, format)

    def _set_wait_stable(
        self, pvs, values, monipv, diffstd = 1e-6, timeout=120):
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

    def _meas_orbit_rm4(self, kickerpv, bpmpvlist, mask,
                         kref = 0.0, dkick = 1e-4, verbose = 0, points=6):
        """
        Measure the RM by change one kicker. 
        """

        kx0 = caget(kickerpv)
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
            dt = self._set_wait_stable(kickerpv, kx, bpmpvlist)
            ret[i+1,:] = caget(bpmpvlist)
            for j,bpm in enumerate(bpmpvlist):
                if mask[j]: ret[i+1,j] = 0
            if verbose:
                print "% .2e %s % .4e dt= %f" % (kx, bpmpvlist[0], ret[i+1,0], dt)
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
            trim_pv_rb = t[2]
            trim_pv_sp = t[3]
            kickref = caget(trim_pv_sp)
            if verbose:
                print "%3d/%d %s" % (i,len(self.trim),trim_pv_sp),
            try:
                kstrength, ret = self._meas_orbit_rm4(
                    trim_pv_sp, bpmrb, mask = self._mask[:,i], kref=kickref,
                    dkick = dkick, verbose=verbose)
            except Timedout:
                save(output)
                raise Timedout

            # polyfit
            p, residuals, rank, singular_values, rcond = \
                np.polyfit(kstrength[1:-1], ret[1:-1,:], 1, full=True)

            ###
            ### it is better to skip coupling, at low slop, error is large ...
            for j in range(len(self.bpm)):
                if residuals[j] < 1e-11: continue
                print "WARNING", trim_pv_sp, self.trim[i][0], \
                    self.bpm[j][0], self.bpm[j][1], p[0,j], residuals[j]
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
                
    def measure(self, output="orm.pkl", verbose = 0, dkick = 2e-5):
        """
        Measure the ORM, ignore the Horizontal(kicker)-Vertical(bpm)
        coupled terms or not.
        """
        t_start = time.time()
        
        bpmrb = [b[2] for b in self.bpm]
        for i, rec in enumerate(self.trim):
            t0 = time.time()
            # get the readback of one trim
            trim_pv_rb = rec[2]
            trim_pv_sp = rec[3]
            kickref = caget(trim_pv_sp)

            if verbose:
                print "%3d/%d %s" % (i,len(self.trim),trim_pv_sp),
            try:
                kstrength, ret = self._meas_orbit_rm4(
                    trim_pv_sp, bpmrb, mask = self._mask[:,i], kref=kickref,
                    dkick = dkick, verbose=verbose)
                #if True:
                #    print "%3d/%d %.2f" % (i,len(self.trim), time.time()-t0), 
                #    t0 = time.time()
            except Timedout:
                save(output)
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
            if verbose:
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
                #if self._mask[i,j]:
                #    
                #    raise ValueError("One ORM element (%d,%d)=(%s,%s)=%s%s is not valid(masked)" % (i,j,self.bpm[i][0], self.trim[j][0], self.bpm[i][1], self.trim[j][1]))

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
        plt.clf()
        plt.hist(um, 50, normed=0)
        plt.savefig("orm-hist-m.png")

        res = []
        deadbpm, deadtrim = [], []
        for j in range(ntrim):
            n = 0
            for i in range(nbpm):
                if self._mask[i, j]: continue

                k = self._rawkick[j, 1:npoints-1]
                m = self._rawmatrix[1:npoints-1, i, j]
                p, residuals, rank, singular_values, rcond = \
                    np.polyfit(k, m, 1, full=True)

                if p[0] < 1e-10: continue
                relerr = abs((p[0] - self.m[i,j])/p[0])
                if verbose:
                    print "%3d,%3d" %(i,j), self.bpm[i][0], self.trim[j][0], \
                        p[0], self.m[i,j], relerr, residuals

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

