#!/usr/bin/env python

"""
Response Matrix Measurement
----------------------------------

:author: Lingyun Yang
:license:

:class:`~hla.measorm.Orm` is an Orbit Response Matrix (ORM) 


"""

import cadict

import os, sys, time
from os.path import join, splitext
#from cothread.catools import caget, caput
import numpy as np
import shelve

from . import _lat
from . import _cfa
from . import getSpChannels, getRbChannels
from catools import caget, caput, Timedout

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
        npts = 4

        self.bpm = []
        self.trim = []
        
        if trim and bpm:
            # one trim may have two (x/y) pv or one only
            trimsp = reduce(lambda x,y: x+y, getSpChannels(trim))
            trimrb = reduce(lambda x,y: x+y, getRbChannels(trim))
            for i in range(len(trimsp)):
                prop = _cfa.getChannelProperties(trimsp[i])
                tags = _cfa.getChannelTags(trimsp[i])
                if 'X' in tags: plane = 'X'
                elif 'Y' in tags: plane = 'Y'
                else:
                    raise ValueError(
                        "channel %s of trim %s in unknown plane ('X' or 'Y')"
                        % (trimsp[i], prop[_cfa.ELEMNAME]))

                self.trim.append(
                    (prop[_cfa.ELEMNAME], plane, trimrb[i], trimsp[i]))
            #
            bpmrb  = reduce(lambda x,y: x+y, getRbChannels(bpm))
            for i in range(len(bpmrb)):
                prop = _cfa.getChannelProperties(bpmrb[i])
                tags = _cfa.getChannelTags(bpmrb[i])
                if 'X' in tags: plane = 'X'
                elif 'Y' in tags: plane = 'Y'
                else:
                    raise ValueError(
                        "channel %s of bpm %s in unknown plane ('X' or 'Y')"
                        % (bpmrb[i], prop[_cfa.ELEMNAME]))
                self.bpm.append((prop[_cfa.ELEMNAME], plane, bpmrb[i]))

        # count the dimension of matrix
        nbpm  = len(set([b[0] for b in self.bpm]))
        ntrim = len(set([t[0] for t in self.trim]))
        nbpmpv, ntrimpv = len(self.bpm), len(self.trim)

        # 3d raw data
        self.__rawmatrix = np.zeros((npts+2, nbpmpv, ntrimpv), 'd')
        self.__mask = np.zeros((nbpmpv, ntrimpv), 'i')
        self.__rawkick = np.zeros((ntrimpv, npts+2), 'd')
        self.m = np.zeros((nbpmpv, ntrimpv), 'd')

        self.bpmrb = bpmrb[:]
        self.trimsp = trimsp[:]
        
        #print __file__, "Done initialization"
        
    def __io_format(self, filename, format):
        rt, ext = splitext(filename)
        if format == '' and ext in self.fmtdict.keys():
            fmt = self.fmtdict[ext]
        elif format:
            fmt = format
        else:
            fmt = 'HDF5'
        return fmt

    def save(self, filename, format = ''):
        """
        save the orm data into one file:

        =======  =====================================
        Data     Description
        =======  =====================================
        orm      matrix
        bpm      list
        trim     list
        rawm     raw orbit change
        rawkick  raw trim strength change
        mask     matrix for ignoring certain ORM terms
        =======  =====================================
        """

        fmt = self.__io_format(filename, format)

        if fmt == 'HDF5':
            import h5py
            f = h5py.File(filename, 'w')
            dst = f.create_dataset("orm", data = self.m)
            dst = f.create_dataset("bpm", data = self.bpm)
            dst = f.create_dataset("trim", data = self.trim)

            grp = f.create_group("_rawdata_")
            dst = grp.create_dataset("matrix", data = self.__rawmatrix)
            dst = grp.create_dataset("kicker_sp", data = self.__rawkick)
            dst = grp.create_dataset("mask", data = self.__mask)

            f.close()
        elif fmt == 'shelve':
            import shelve
            f = shelve.open(filename, 'c')
            f['orm.m'] = self.m
            f['orm.bpm'] = self.bpm
            f['orm.trim'] = self.trim
            f['orm._rawdata_.matrix']    = self.__rawmatrix
            f['orm._rawdata_.kicker_sp'] = self.__rawkick
            f['orm._rawdata_.mask']      = self.__mask
        else:
            raise ValueError("not supported file format: %s" % format)

    def load(self, filename, format = ''):
        self.__load_v2(filename, format)

    def __load_v2(self, filename, format = ''):
        """
        load orm data from binary file
        """
        fmt = self.__io_format(filename, format)
            
        if fmt == 'HDF5':
            import h5py
            f = h5py.File(filename, 'r')
            self.bpm = [ b for b in f["bpm"]]
            self.trim = [t for t in f["trim"]]
            nbpm, ntrim = len(self.bpm), len(self.trim)
            self.m = np.zeros((nbpm, ntrim), 'd')
            self.m[:,:] = f["orm"][:,:]
            t, npts = f["_rawdata_"]["kicker_sp"].shape
            self.__rawkick = np.zeros((ntrim, npts), 'd')
            self.__rawkick[:,:] = f["_rawdata_"]["kicker_sp"][:,:]
            self.__rawmatrix = np.zeros((npts, nbpm, ntrim), 'd')
            self.__rawmatrix[:,:,:] = f["_rawdata_"]["matrix"][:,:,:]
            self.__mask = np.zeros((nbpm, ntrim))
            self.__mask[:,:] = f["_rawdata_"]["mask"][:,:]
        elif fmt == 'shelve':
            f = shelve.open(filename, 'r')
            self.bpm = f["orm.bpm"]
            self.trim = f["orm.trim"]
            self.m = f["orm.m"]
            self.__rawmatrix = f["orm._rawdata_.matrix"]
            self.__rawkick   = f["orm._rawdata_.kicker_sp"]
            self.__mask      = f["orm._rawdata_.mask"]
        else:
            raise ValueError("format %s is not supported yet" % format)

        #print self.trim

    def __meas_orbit_rm4(self, kickerpv, bpmpvlist, mask,
                         kref = 0.0, dkick = 1e-6, verbose = 0):
        """
        Measure the RM by change one kicker. 4 points method.
        """

        kx0 = caget(kickerpv)
        print "Kicker: read %f rb(write) %f" % (kref, kx0), 
        # bpm read out
        ret = np.zeros((6, len(bpmpvlist)), 'd')
        # initial bpm data
        for j, bpm in enumerate(bpmpvlist):
            if mask[j]: ret[0,j] = 0
            else: ret[0,j] = caget(bpm)

        kstrength = [kx0, kx0-2*dkick, kx0-dkick, kx0+dkick, kx0+2*dkick, kx0]
        for i,kx in enumerate(kstrength[1:]):
            caput(kickerpv, kx)
            if verbose: 
                print "\nSetting trim: ", kickerpv, kx, caget(kickerpv), 
                print "  waiting %d sec" % self.TSLEEP
            else:
                print kx,
                sys.stdout.flush()
            time.sleep(self.TSLEEP)
            for j,bpm in enumerate(bpmpvlist):
                if mask[j]: ret[i+1,j] = 0
                else: ret[i+1,j] = caget(bpm)
                if verbose:
                    if j < 3 or j >= len(bpmpvlist)-3:
                        print "  %4d" % j, bpm, "%13.4e" % ret[i+1,j]
                    sys.stdout.flush()
            if verbose:
                print ""
        print ""

        return np.array(kstrength), ret


    def measure(self, output="orm.pkl", verbose = 0):
        """
        Measure the ORM, ignore the Horizontal(kicker)-Vertical(bpm)
        coupled terms or not.
        """
        t_start = time.time()
        t0 = t_start
        
        bpmrb = [b[2] for b in self.bpm]
        for i, rec in enumerate(self.trim):
            # get the readback of one trim
            trim_pv_sp = rec[2]
            trim_pv_rb = rec[3]
            kickref = caget(trim_pv_sp)

            dkick = 2e-5
            try:
                kstrength, ret = self.__meas_orbit_rm4(
                    trim_pv_rb, bpmrb, mask = self.__mask[:,i], kref=kickref,
                    dkick = dkick, verbose=verbose)
                if True:
                    print "%3d/%d" % (i,len(self.trim)), time.time() - t0, 
                    t0 = time.time()
            except Timedout:
                save(output)
                raise Timedout
            
            # 4 points
            v = (-ret[4,:] + 8.0*ret[3,:] - 8*ret[2,:] + ret[1,:])/12.0/dkick
        
            # polyfit
            p, residuals, rank, singular_values, rcond = \
                np.polyfit(kstrength[1:-1], ret[1:-1,:], 1, full=True)

            ###
            ### it is better to skip coupling, at low slop, error is large ...
            for j in range(len(self.bpm)):
                # do not warn if it is coupling terms
                if abs((v[j] - p[0, j])/v[j]) > .05 and abs(v[j]) > .1 and \
                       rec[1] == self.bpm[j][1]:
                    print "WARNING", trim_pv_sp, self.trim[i][0], \
                          self.bpm[j][0], self.bpm[j][1], v[j], p[0,j]
                    plt.plot(kstrength[1:-1], ret[1:-1,j], 'o')
                    tx = np.linspace(kstrength[1], kstrength[-1], 20)
                    plt.plot(tx, tx*p[0,j] + p[1,j], '-')
                    plt.savefig("orm-trim-%03d-bpm-%03d.png" % (i,j))
                    
            self.__rawkick[i, :] = kstrength[:]
            self.__rawmatrix[:,:,i] = ret[:,:]
            #self.m[:,i] = v[:]
            self.m[:,i] = p[0,:]
            if verbose:
                plt.clf()
                for j in range(len(self.bpm)):
                    # skip the coupling
                    if rec[1] != self.bpm[j][1]: continue
                    plt.plot(self.__rawkick[i,:]*1e6, ret[:,j]*1e3, '-o')
                plt.savefig("orm-kick-%s.png" % rec[0])

            time.sleep(self.TSLEEP)

            # save for every trim settings
            self.save(output)
        t_end = time.time()
        print "Time cost: ", "%.2f" % ((t_end - t_start)/60.0), " min"

    def hasBpm(self, bpm):
        """
        check if the bpm is used in this ORM measurement
        """

        for i,b in enumerate(self.bpm):
            if b[0] == bpm: return True
        return False

    def hasTrim(self, trim):
        """
        check if the trim is used in this ORM measurement
        """
        for i,tr in enumerate(self.trim):
            if tr[0] == trim: return True
        return False

    def maskCrossTerms(self):
        for i,b in enumerate(self.bpm):
            for j,t in enumerate(self.trim):
                # b[1] = ['X'|'Y'], similar for t[1]
                if b[1] != t[1]: self.__mask[i,j] = 1

    def __pv_index(self, pv):
        """
        return pv index of BPM, TRIM
        """
        for i,b in enumerate(self.bpm):
            if b[2] == pv: return i
        for j,t in enumerate(self.trim):
            if b[2] == pv or b[3] == pv:
                return j
        return -1
    
    def update(self, src):
        """
        merge two orm into one
        """
        # copy
        bpm, trim = self.bpm[:], self.trim[:]

        for i,b in enumerate(src.bpm):
            if self.__pv_index(b[2]) < 0:
                bpm.append(b)
        for j,t in enumerate(src.trim):
            if self.__pv_index(t[2]) < 0:
                trim.append(t)
        npts, nbpm0, ntrim0 = np.shape(self.__rawmatrix)
        
        nbpm, ntrim = len(bpm), len(trim)
        print "(%d,%d) -> (%d,%d)" % (nbpm0, ntrim0, nbpm, ntrim)
        # the merged is larger
        rawmatrix = np.zeros((npts, nbpm, ntrim), 'd')
        mask      = np.zeros((nbpm, ntrim), 'i')
        rawkick   = np.zeros((ntrim, npts), 'd')
        m         = np.zeros((nbpm, ntrim), 'd')

        rawmatrix[:, :nbpm0, :ntrim0] = self.__rawmatrix[:,:,:]
        mask[:nbpm0, :ntrim0]         = self.__mask[:,:]
        rawkick[:ntrim0, : ]          = self.__rawkick[:,:]
        m[:nbpm0, :ntrim0]            = self.m[:,:]

        # find the index
        bpmrb = [b[2] for b in bpm]
        trimsp = [t[3] for t in trim]
        ibpm  = [ bpmrb.index(b[2]) for b in src.bpm ]
        itrim = [ trimsp.index(t[3]) for t in src.trim ]
        
        for j, t in enumerate(src.trim):
            jj = itrim[j]
            rawkick[jj,:] = src.__rawkick[j,:]
            for i, b in enumerate(src.bpm):
                ii = ibpm[i]
                rawmatrix[:,ii,jj] = src.__rawmatrix[:,i,j]
                mask[ii,jj] = src.__mask[i,j]
                m[ii,jj] = src.m[i,j]
        self.__rawmatrix = rawmatrix
        self.__mask = mask
        self.__rawkick = rawkick
        self.m = m

        self.bpmrb, self.trimsp = bpmrb, trimsp
        
    def getSubMatrix(self, bpm, trim):
        """
        if only bpm name given, the return matrix will not equal to
        len(bpm),len(trim), since one bpm can have two lines (x,y) data.
        """
        raise NotImplementedError()

    def checkLinearity(self, dev = .1, plot=False):
        """
        check the linearity of each orm term.

        This routine detects the BPMs which do not reponse to trim well. 
        """
        import matplotlib.pylab as plt
        npoints, nbpm, ntrim = np.shape(self.__rawmatrix)
        res = []

        # unmasked matrix
        um = []
        for i in range(nbpm):
            for j in range(ntrim):
                if self.__mask[i,j]: continue
                um.append(self.m[i,j])
        plt.hist(um, 50, normed=0)
        plt.savefig("orm-hist.png")

        for j in range(ntrim):
            #print j, self.__rawkick[0, 1:npoints-1]
            plt.clf()
            n = 0
            for i in range(nbpm):
                if self.__mask[i, j]: continue

                k = self.__rawkick[j, 1:npoints-1]
                m = self.__rawmatrix[1:npoints-1, i, j]
                p, residuals, rank, singular_values, rcond = \
                    np.polyfit(k, m, 1, full=True)

                tag = 'o'
                if abs((p[0] - self.m[i,j])/p[0]) > dev:
                    print "%8d: bpm %3d, trim %3d" % (n, i, j), \
                        self.bpm[i][0], self.trim[j][0]
                    print "        ", residuals, \
                        p[0], " calc:", self.m[i, j]
                    n = n + 1
                    tag = 'e'
                if tag == 'e' or plot:
                    t = np.linspace(min(k)*1e6, max(k)*1e6, 100)
                    plt.plot(t, p[0]*t + p[1]*1e6, '-')
                    plt.plot(k*1e6, m*1e6, '-o')
                if tag == 'e':
                    f = open("test.sh", 'w')
                    f.write("#!/bin/bash\n")
                    for ki in range(npoints):
                        f.write("caput '%s' %e\n" % (self.trim[j][3],  
                                                 self.__rawkick[j, ki]))
                        f.write("sleep 3\n")
                        f.write("caget '%s'\n" % self.bpm[i][2])
                    f.close()

                if p[0] < 1e-10: continue
                res.append(residuals[0])
            # end of all bpm
            if n > 0:
                #plt.ylabel(self.__bpm[i] + "  x1e6")
                plt.title("Failed: %d/%d (%s)" % \
                          (n, len(self.bpm[i][2]), self.trim[j][2]))
                plt.xlabel(self.trim[j][0] + "  x1e6")
                plt.savefig("orm-check-%07d.png" % (j))
        print len(res), np.average(res), np.var(res)

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
                if self.__mask[ib, jt]: continue
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
             np.sum(self.__mask), len(self.trim)*len(self.bpm))
        return s

def measOrbitRm(bpm, trim):
    """Measure the beta function by varying quadrupole strength"""
    print "EPICS_CA_MAX_ARRAY_BYTES:", os.environ['EPICS_CA_MAX_ARRAY_BYTES']
    print "EPICS_CA_ADDR_LIST      :", os.environ['EPICS_CA_ADDR_LIST']
    print "BPM: ", len(bpm)
    print "TRIM:", len(trim)

    orm = Orm(bpm, trim)
    orm.measure(verbose=1)
    return orm

# testing ...

def measChromRm():
    """
    measure chromaticity response matrix
    """
    pass

