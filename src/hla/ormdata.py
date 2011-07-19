#!/usr/bin/env python

"""
Response Matrix Data
----------------------------------

:author: Lingyun Yang
:license:

:class:`~hla.orm.OrmData` is an Orbit Response Matrix (ORM) 


"""

import os, sys, time
from os.path import join, splitext
import numpy as np
import shelve

class OrmData:
    """
    Orbit Response Matrix Data
    """
    fmtdict = {'.hdf5': 'HDF5', '.pkl':'shelve'}
    def __init__(self, datafile):
        """
          orm = Orm(['BPM1', 'BPM2'], ['TRIM1', 'TRIM2'])
        """
        # points for trim setting when calc dx/dkick
        npts = 6

        self.bpm = []
        self.trim = []
        
        nbpmpv, ntrimpv = 0, 0

        # 3d raw data
        self._rawmatrix = None
        self._mask = None
        self._rawkick = None
        self.m = None

        self.load(datafile)

        #print __file__, "Done initialization"
        
    def _io_format(self, filename, format):
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

        =================   =====================================
        Data                Description
        =================   =====================================
        m                   matrix
        bpm                 list
        trim                list
        _rawdata_.matrix    raw orbit change
        _rawdata_.rawkick   raw trim strength change
        _rawdata_.mask      matrix for ignoring certain ORM terms
        =================   =====================================
        """

        fmt = self._io_format(filename, format)

        if fmt == 'HDF5':
            import h5py
            f = h5py.File(filename, 'w')
            dst = f.create_dataset("m", data = self.m)
            dst = f.create_dataset("bpm", data = self.bpm)
            dst = f.create_dataset("trim", data = self.trim)

            grp = f.create_group("_rawdata_")
            dst = grp.create_dataset("rawmatrix", data = self._rawmatrix)
            dst = grp.create_dataset("rawkick", data = self._rawkick)
            dst = grp.create_dataset("mask", data = self._mask)

            f.close()
        elif fmt == 'shelve':
            import shelve
            f = shelve.open(filename, 'c')
            f['orm.m'] = self.m
            f['orm.bpm'] = self.bpm
            f['orm.trim'] = self.trim
            f['orm._rawdata_.rawmatrix'] = self._rawmatrix
            f['orm._rawdata_.rawkick']   = self._rawkick
            f['orm._rawdata_.mask']      = self._mask
        else:
            raise ValueError("not supported file format: %s" % format)

    def load(self, filename, format = ''):
        self._load_v2(filename, format)

    def _load_v2(self, filename, format = ''):
        """
        load orm data from binary file
        """
        if not os.path.exists(filename):
            raise ValueError("ORM data %s does not exist" % filename)

        fmt = self._io_format(filename, format)
            
        if fmt == 'HDF5':
            import h5py
            f = h5py.File(filename, 'r')
            self.bpm = [ b for b in f["bpm"]]
            self.trim = [t for t in f["trim"]]
            nbpm, ntrim = len(self.bpm), len(self.trim)
            self.m = np.zeros((nbpm, ntrim), 'd')
            self.m[:,:] = f["orm"][:,:]
            t, npts = f["_rawdata_"]["rawkick"].shape
            self._rawkick = np.zeros((ntrim, npts), 'd')
            self._rawkick[:,:] = f["_rawdata_"]["rawkick"][:,:]
            self._rawmatrix = np.zeros((npts, nbpm, ntrim), 'd')
            self._rawmatrix[:,:,:] = f["_rawdata_"]["rawmatrix"][:,:,:]
            self._mask = np.zeros((nbpm, ntrim))
            self._mask[:,:] = f["_rawdata_"]["mask"][:,:]
        elif fmt == 'shelve':
            f = shelve.open(filename, 'r')
            self.bpm = f["orm.bpm"]
            self.trim = f["orm.trim"]
            self.m = f["orm.m"]
            self._rawmatrix = f["orm._rawdata_.rawmatrix"]
            self._rawkick   = f["orm._rawdata_.rawkick"]
            self._mask      = f["orm._rawdata_.mask"]
        else:
            raise ValueError("format %s is not supported yet" % format)

        #print self.trim

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
    
    def index(self, v):
        """
        return the index of a pv
        """
        i = self._pv_index(v)
        if i >= 0: return i
        
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
