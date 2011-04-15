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
from catools import caget, caput

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
                    raise ValueError("channel %s of trim %s in unknown plane ('X' or 'Y')"
                                     % (trimsp[i], prop[_cfa.ELEMNAME]))

                self.trim.append((prop[_cfa.ELEMNAME], plane, trimrb[i], trimsp[i]))

            #
            bpmrb  = reduce(lambda x,y: x+y, getRbChannels(bpm))
            for i in range(len(bpmrb)):
                prop = _cfa.getChannelProperties(bpmrb[i])
                tags = _cfa.getChannelTags(bpmrb[i])
                if 'X' in tags: plane = 'X'
                elif 'Y' in tags: plane = 'Y'
                else:
                    raise ValueError("channel %s of bpm %s in unknown plane ('X' or 'Y')"
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
        print "Kicker: read %f rb(write) %f" % (kref, kx0)
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
                print "Setting trim: ", kickerpv, kx, caget(kickerpv), 
                print "  waiting %d sec" % self.TSLEEP
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

        return np.array(kstrength), ret


    def measure(self, coupled=False, verbose = 0):
        """
        Measure the ORM, ignore the Horizontal(kicker)-Vertical(bpm)
        coupled terms or not.
        """

        bpmrb = [b[2] for b in self.bpm]
        for i, rec in enumerate(self.trim):
            # get the readback of one trim
            trim_pv_sp = rec[2]
            trim_pv_rb = rec[3]
            kickref = caget(trim_pv_sp)

            dkick = 2e-6
            #if True: print i, self.__trimsp[i], kref,
            kstrength, ret = self.__meas_orbit_rm4(
                trim_pv_rb, bpmrb, mask = self.__mask[:,i], kref=kickref,
                dkick = dkick, verbose=verbose)

            # 4 points
            v = (-ret[4,:] + 8.0*ret[3,:] - 8*ret[2,:] + ret[1,:])/12.0/dkick
        
            # polyfit
            p, residuals, rank, singular_values, rcond = \
                np.polyfit(kstrength[1:-1], ret[1:-1,:], 1, full=True)

            ###
            ### it is better to skip coupling, at low slop, error is large ...
            for j in range(len(self.bpm)):
                if abs((v[j] - p[0, j])/v[j]) > .1 and abs(v[j]) > .01:
                    print "WARNING", trim_pv_sp, self.bpm[j][0], v[j], p[0,j]

            self.__rawkick[i, :] = kstrength[:]
            self.__rawmatrix[:,:,i] = ret[:,:]
            self.m[:,i] = v[:]
            if verbose:
                plt.clf()
                for j in range(len(self.bpm)):
                    # skip the coupling
                    if rec[1] != self.bpm[j][1]: continue
                    plt.plot(self.__rawkick[i,:]*1e6, ret[:,j]*1e3, '-o')
                plt.savefig("orm-kick-%s.png" % rec[0])

            time.sleep(self.TSLEEP)

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

    def merge(self, src):
        """
        merge two orm into one
        """

        raise NotImplementedError()

        print "Merging ..."
        nbpm, ntrim = len(self.bpm), len(self.trim)
        ntrim1, npts = np.shape(self.__rawkick)
        if ntrim != ntrim:
            raise ValueError("Internal data dimension does not match")
        
        # index of src bpm/trim in the new bpm/trim list
        ibpm, itrim = range(len(src.__bpmrb)), range(len(src.__trimsp))

        # new header
        bpm = [b for b in set(self.bpm).union(set(src.bpm))]
        trim = [ t for t in set(self.trim).union(set(src.trim))]
        print bpm, trim

        # merge the matrix data
        dst = Orm(bpm = bpm, trim = trim)

        print len(self.__trimsp), len(src.__trimsp), len(dst.__trimsp)
        for pv in src.__trimsp:
            if list(src.__trimsp).count(pv) > 1: print pv
            #return None

        # 3d raw data, assuming src and self has same __npoints
        dst.__rawmatrix = np.zeros((npts, len(dst.__bpmrb),
                                   len(dst.__trimsp)), 'd')
        dst.__mask = np.zeros((len(dst.__bpmrb), len(dst.__trimsp)))
        dst.__rawkick = np.zeros((len(dst.__trimsp), npts), 'd')
        dst.__m = np.zeros((len(dst.__bpmrb), len(dst.__trimsp)), 'd')

        for j,pvj in enumerate(self.__trimsp):
            print j,
            sys.stdout.flush()
            jj = dst.__trimsp.index(pvj)
            for i,pvi in enumerate(self.__bpmrb):
                ii = dst.__bpmrb.index(pvi)
                for k in range(npts):
                    dst.__rawmatrix[k, ii, jj] = self.__rawmatrix[k, i, j]
                dst.__mask[ii, jj] = self.__mask[i, j]
                dst.__m[ii, jj] = self.__m[i, j]
            for k in range(npts):
                dst.__rawkick[jj, k] = self.__rawkick[j, k]
        print "Step 1"
        for j,pvj in enumerate(src.__trimsp):
            print j,
            sys.stdout.flush()
            jj = dst.__trimsp.index(pvj)
            for i,pvi in enumerate(src.__bpmrb):
                ii = dst.__bpmrb.index(pvi)
                for k in range(npts):
                    dst.__rawmatrix[k, ii, jj] = src.__rawmatrix[k, i, j]
                dst.__mask[ii, jj] = src.__mask[i, j]
                dst.__m[ii, jj] = src.__m[i, j]
            for k in range(npts):
                dst.__rawkick[jj, k] = src.__rawkick[j, k]
        print "Step 2"
        return dst

    def getSubMatrix(self, bpm, trim):
        raise NotImplementedError()

        if isinstance(bpm, str): bpmlst = [bpm]
        elif isinstance(bpm, list): bpmlst = bpm[:]
        if isinstance(trim, str): trimlst = [trim]
        elif isinstance(trim, list): trimlst = trim[:]
        
        for b in bpmlst:
            if not b in self.bpm:
                print b
                print self.bpm
                raise ValueError("bpm %s is not in ORM" % b)
        for t in trimlst:
            if not t in self.trim:
                raise ValueError("trim %s is not in ORM" % t)
            
        d = np.zeros((len(bpmlst), len(trimlst)), 'd')
        for i,b in enumerate(bpmlst):
            for j,t in enumerate(trimlst):
                i1 = self.bpm.index(b)
                j1 = self.trim.index(t)
                d[i,j] = self.__m[i1,j1]
        return d

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
                plt.title("Failed: %d/%d (%s)" % (n, len(self.bpm[i][2]), self.trim[j][2]))
                plt.xlabel(self.trim[j][0] + "  x1e6")
                plt.savefig("orm-check-%07d.png" % (j))
        print len(res), np.average(res), np.var(res)

    def checkOrbitReproduce(self, bpm, trim, kick = None):
        print "checking ..."
        print "    bpm:", bpm
        print "    trim:", trim
        if kick == None:
            kick = np.random.rand(len(trim)) * 1e-6
        for i,t in enumerate(trim):
            i1 = self.trim.index(t)
            caput(self.trim[i1][3], kick[i])
        print "RB:", len(self.bpm)
        time.sleep(self.TSLEEP)
        for i,b in enumerate(bpm):
            i1 = self.bpm.index(b)
            print b, caget(self.__bpmrb[i1]),
            s = 0.0
            for j in range(len(trim)):
                s = s + m[i,j]*kick[j]
            diff = (s-caget(self.__bpmrb[i1]))/s
            print s, diff*100.0,'%',
            if diff > .05: print " *"
            else: print ""

        for i,t in enumerate(trim):
            i1 = self.trim.index(t)
            caput(self.__trimsp[i1], 0.0)
        pass

    def __str__(self):
        nbpm, ntrim = np.shape(self.m)
        s = "Orbit Response Matrix\n" \
            " trim %d, bpm %d, matrix (%d, %d)" % \
            (len(self.trim), len(self.bpm), nbpm, ntrim)
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

