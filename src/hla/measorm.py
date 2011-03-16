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
from os.path import join
from cothread.catools import caget, caput
import numpy as np
import shelve

from . import _lat
from . import _cfa
from . import getSpChannels, getRbChannels

class Orm:
    """
    Orbit Response Matrix
    """
    tsleep = 25
    def __init__(self, bpm, trim):
        #print trim, getSpChannels(trim)
        #print _cfa
        #print _cfa.getElementChannel(trim)
        #print _cfa.getElementChannel(trim, {'handle': 'set'}, ['default'])

        # points for trim setting when calc dx/dkick
        npts = 4

        if trim and bpm:
            trimsp = [v[0] for v in getSpChannels(trim)]
            trimrb = [v[0] for v in getRbChannels(trim)]
            
            #
            bpmrb  = [v[1] for v in getRbChannels(bpm)]
            #print trimsp, trimrb, bpmrb

            self.bpm  = [v for v in bpm]
            self.trim = [v for v in trim]
            self.__bpmrb  = [v for v in bpmrb]
            self.__trimsp = [v for v in trimsp]
            self.__trimrb = [v for v in trimrb]
        else:
            self.bpm = []
            self.trim = []
            self.__bpmrb = []
            self.__trimsp = []
            self.__trimrb = []

        nbpm, ntrim = len(self.bpm), len(self.trim)

        # 3d raw data
        self.__rawmatrix = np.zeros((npts+2, nbpm, ntrim), 'd')
        self.__mask = np.zeros((nbpm, ntrim), 'i')
        self.__rawkick = np.zeros((ntrim, npts+2), 'd')
        self.__m = np.zeros((nbpm, ntrim), 'd')

    def save(self, filename, format = 'HDF5'):
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

        current default format: HDF5 
        """
        if format == 'HDF5':
            import h5py
            f = h5py.File(filename, 'w')
            dst = f.create_dataset("orm", data = self.__m)
            dst = f.create_dataset("bpm", data = self.bpm)
            dst = f.create_dataset("trim", data = self.trim)
            dst = f.create_dataset("bpm_pvrb", data = self.__bpmrb)
            dst = f.create_dataset("trim_pvsp", data = self.__trimsp)
            dst = f.create_dataset("trim_pvrb", data = self.__trimrb)

            grp = f.create_group("_rawdata_")
            dst = grp.create_dataset("matrix", data = self.__rawmatrix)
            dst = grp.create_dataset("kicker_sp", data = self.__rawkick)
            dst = grp.create_dataset("mask", data = self.__mask)

            f.close()
        elif format == 'shelve':
            import shelve
            f = shelve.open(filename, 'c')
            f['orm.m'] = self.__m
            f['orm.bpm'] = self.bpm
            f['orm.trim'] = self.trim
            f['orm.bpm_pvrb']  = self.__bpmrb
            f['orm.trim_pvsp'] = self.__trimsp
            f['orm.trim_pvrb'] = self.__trimrb
            f['orm._rawdata_.matrix']    = self.__rawmatrix
            f['orm._rawdata_.kicker_sp'] = self.__rawkick
            f['orm._rawdata_.mask']      = self.__mask
        else:
            raise ValueError("not supported file format: %s" % format)

    def load(self, filename, format = 'HDF5'):
        """
        load orm data from binary file
        """
        if format == 'HDF5':
            import h5py
            f = h5py.File(filename, 'r')
            self.bpm = [ b for b in f["bpm"]]
            self.trim = [t for t in f["trim"]]
            nbpm, ntrim = len(self.bpm), len(self.trim)
            self.__m = np.zeros((nbpm, ntrim), 'd')
            self.__m[:,:] = f["orm"][:,:]
            self.__bpmrb = [b.strip() for b in f["bpm_pvrb"]]
            self.__trimsp = [b for b in f["trim_pvsp"]]
            self.__trimrb = [b for b in f["trim_pvrb"]]
            t, npts = f["_rawdata_"]["kicker_sp"].shape
            self.__rawkick = np.zeros((ntrim, npts), 'd')
            #print np.shape(self.__rawkick)
            #print f["_rawdata_"]["kicker_sp"].shape
            self.__rawkick[:,:] = f["_rawdata_"]["kicker_sp"][:,:]
            self.__rawmatrix = np.zeros((npts, nbpm, ntrim), 'd')
            self.__rawmatrix[:,:,:] = f["_rawdata_"]["matrix"][:,:,:]
            self.__mask = np.zeros((nbpm, ntrim))
            self.__mask[:,:] = f["_rawdata_"]["mask"][:,:]
        elif format == 'shelve':
            f = shelve.open(filename, 'r')
            self.bpm = f["orm.bpm"]
            self.trim = f["orm.trim"]
            self.__m = f["orm.m"]
            self.__bpmrb  = f["orm.bpm_pvrb"]
            self.__trimsp = f["orm.trim_pvsp"]
            self.__trimrb = f["orm.trim_pvrb"]
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

        #print __file__, kickerpv
        #print __file__, bpmpvlist
        if not getattr(dkick, '__iter__', False):
            # not iterable ?
            pass
        kx0 = caget(kickerpv)
        ret = np.zeros((6, len(bpmpvlist)), 'd')
        #tsleep = 20
        for j, bpm in enumerate(bpmpvlist):
            if mask[j]: ret[0,j] = 0
            else: ret[0,j] = caget(bpm)

        
        kstrength = [kx0, kx0-2*dkick, kx0-dkick, kx0+dkick, kx0+2*dkick, kx0]
        for i,kx in enumerate(kstrength[1:]):
            caput(kickerpv, kx)
            if verbose: 
                print "Setting trim: ", kickerpv, kx, caget(kickerpv)
            time.sleep(self.tsleep)
            for j,bpm in enumerate(bpmpvlist):
                if mask[j]: ret[i+1,j] = 0
                else: ret[i+1,j] = caget(bpm)
                if j < 3 or j >= len(bpmpvlist)-3:
                    print "  %4d" % j, bpm, ret[i+1,j]
                sys.stdout.flush()
            print ""
        # 4 points
        v = (-ret[4,:] + 8.0*ret[3,:] - 8*ret[2,:] + ret[1,:])/12.0/dkick
        
        # polyfit
        p, residuals, rank, singular_values, rcond = \
            np.polyfit(kstrength[1:-1], ret[1:-1,:], 1, full=True)
        print ""
        print "Shape:", np.shape(kstrength[1:-1]), np.shape(ret[1:-1,:])
        print "Shape:",np.shape(p), np.shape(residuals)

        for i in range(len(bpmpvlist)):
            if abs((v[i] - p[0, i])/v[i]) > .1:
                print kickerpv, bpmpvlist[i], v[i], p[0,i]
        
        return v, kstrength, ret

    def measure(self, coupled=False, verbose = 0):
        """
        Measure the ORM, ignore the Horizontal(kicker)-Vertical(bpm)
        coupled terms or not.
        """

        for i, trim in enumerate(self.__trimsp):
            kref = caget(self.__trimrb[i])
            #if True: print i, self.__trimsp[i], kref,
            v, kstrength, ret = self.__meas_orbit_rm4(
                trim, self.__bpmrb, mask = self.__mask[:,i], kref=kref,
                verbose=verbose)
            self.__rawkick[i, :] = kstrength[:]
            self.__rawmatrix[:,:,i] = ret[:,:]
            self.__m[:,i] = v[:]
            time.sleep(3)

    def merge(self, src):
        """
        merge two orm into one
        """

        print "Merging ..."
        nbpm, ntrim = len(self.__bpmrb), len(self.__trimsp)
        ntrim1, npts = np.shape(self.__rawkick)
        if ntrim != ntrim:
            raise ValueError("Internal data dimension does not match")
        
        # index of src bpm/trim in the new bpm/trim list
        ibpm, itrim = range(len(src.__bpmrb)), range(len(src.__trimsp))

        # new header
        bpm = [b for b in set(self.bpm).union(set(src.bpm))]
        trim = [ t for t in set(self.trim).union(set(src.trim))]
        print bpm, trim
        bpmpv  = set(self.__bpmrb).union(set(src.__bpmrb))
        trimsp = set(self.__trimsp).union(set(src.__trimsp))
        trimrb = set(self.__trimrb).union(set(src.__trimrb))

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
        print self.trim
        #print npoints, nbpm, ntrim
        res = []
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
                #if residuals[0] > 1e-11:
                #    print "x [%f %f]" % (k[0], k[-1]), residuals, p[0], \
                #        " calc:", self.__m[i, j]
                if self.__bpmrb[i].find("Pos-X") > 0 and \
                        self.__trimrb[j].find("VCM") > 0:
                    continue

                if self.__bpmrb[i].find("Pos-Y") > 0 and \
                        self.__trimrb[j].find("HCM") > 0:
                    continue

                tag = 'o'
                if abs((p[0] - self.__m[i,j])/p[0]) > dev:
                    print "%8d: bpm %3d, trim %3d" % (n, i, j), \
                        self.__bpmrb[i], self.__trimrb[j]
                    print "        ", residuals, \
                        p[0], " calc:", self.__m[i, j]
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
                        f.write("caput '%s' %e\n" % (self.__trimsp[j],  
                                                 self.__rawkick[j, ki]))
                        f.write("sleep 3\n")
                        f.write("caget '%s'\n" % self.__bpmrb[i])
                    f.close()

                if p[0] < 1e-10: continue
                res.append(residuals[0])
            # end of all bpm
            if n > 0:
                #plt.ylabel(self.__bpm[i] + "  x1e6")
                plt.title("Failed: %d/%d (%s)" % (n, len(self.__bpmrb), self.trim[j]))
                plt.xlabel(self.__trimsp[j] + "  x1e6")
                plt.savefig("orm-check-%07d.png" % (j))
        print len(res), np.average(res), np.var(res)

    def checkOrbitReproduce(self, bpm, trim, kick = None):
        print "checking ..."
        print "    bpm:", bpm
        print "    trim:", trim
        m = self.getSubMatrix(bpm, trim)
        if kick == None:
            kick = np.random.rand(len(trim)) * 1e-6
        for i,t in enumerate(trim):
            i1 = self.trim.index(t)
            caput(self.__trimsp[i1], kick[i])
        print "RB:", len(self.__bpmrb)
        time.sleep(60)
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

def measOrbitRm(bpm, trim):
    """Measure the beta function by varying quadrupole strength"""
    print "EPICS_CA_MAX_ARRAY_BYTES:", os.environ['EPICS_CA_MAX_ARRAY_BYTES']
    print "EPICS_CA_ADDR_LIST      :", os.environ['EPICS_CA_ADDR_LIST']
    print "BPM: ", len(bpm)
    print "TRIM:", len(trim)

    orm = Orm(bpm, trim)
    orm.measure(verbose=1)
    #orm.save("test.hdf5")
    return orm

# testing ...

def measChromRm():
    """
    measure chromaticity response matrix
    """
    pass

def test():
    x = []
    t0 = 1299032723.0
    for k in [.0, -2e-6, -1e-6, 1e-6, 2e-6, 0.]:
        #caput('SR:C30-MG:G01A<VCM:H2>Fld-SP', k)
        caput('SR:C01-MG:G04A<VCM:M>Fld-SP', k)
        t1 = time.time()
        x1 = caget('SR:C30-BI:G02A<BPM:H2>Pos-Y')
        for i in range(200):
            #time.sleep(4)
            #print time.time()
            x2 = caget('SR:C30-BI:G02A<BPM:H2>Pos-Y')
            #time.sleep(4)
            if abs(x2 - x1) > 1e-12:
                print k, "%4d" % i, time.time() - t1, x1
                break
            x1 = x2
            time.sleep(3)
            #t2 = caget('SR:C30-BI:G02A<BPM:H2>Pos-Y')
        #print k, t1, t2
        #x.append([k, t1, t2])
    print x

