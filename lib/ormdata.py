#!/usr/bin/env python

"""
Response Matrix Data
----------------------------------

:author: Lingyun Yang
:license:

:class:`~hla.orm.OrmData` is an Orbit Response Matrix (ORM) 

"""

import os
from os.path import splitext
import numpy as np
import shelve

class OrmData:
    """
    Orbit Response Matrix Data

    - *bpm* is a list of tuple (name, plane, pv)
    - *trim* is a list of tuple (name, plane, pv_readback, pv_setpoint)
    - *m* 2D matrix, len(bpm) * len(trim)
    """
    fmtdict = {'.hdf5': 'HDF5', '.pkl':'shelve'}
    def __init__(self, datafile = None):
        # points for trim setting when calc dx/dkick
        #npts = 6

        # list of tuple, (name, plane, pv)
        self.bpm = []
        self.trim = []
        
        # 3d raw data
        self._rawmatrix = None
        self._mask = None
        self._rawkick = None
        self.m = None

        if datafile is not None:
            self.load(datafile)

        
    def _io_format(self, filename, format):
        rt, ext = splitext(filename)
        if format == '' and ext in self.fmtdict.keys():
            fmt = self.fmtdict[ext]
        elif format:
            fmt = format
        else:
            fmt = 'HDF5'
        return fmt
    
    def save_hdf5(self, filename):
        """
        save data to hdf5 format

        h5py before v2.0 does not accept unicode directly.
        """
        import h5py
        h5zip = None # 'gzip' works in default install
        f = h5py.File(filename, 'w')
        str_type = h5py.new_vlen(str)
        m, n = np.shape(self.m)
        dst = f.create_dataset('m', (m,n), data=self.m, compression=h5zip)
        #
        grp = f.create_group('bpm')
        name, plane, pv = zip(*self.bpm)
        # dtype('<U9') is not recognized in earlier h5py
        if h5py.version.version_tuple < (2,1,1):
            name = [v.encode('ascii') for v in name]
        dst = grp.create_dataset('element', (m,), data = name, dtype=str_type, 
                                 compression=h5zip)
        dst = grp.create_dataset('plane', (m,), data = plane, dtype=str_type,
                                 compression=h5zip)
        pvascii = [p.encode('ascii') for p in pv]
        dst = grp.create_dataset('pvrb', (m,), data = pvascii, dtype=str_type,
                                 compression=h5zip)
        #
        name, plane, pvrb, pvsp = zip(*self.trim)
        # dtype('<U9') is not recognized in earlier h5py
        if h5py.version.version_tuple < (2,1,1):
            name = [v.encode('ascii') for v in name]
        grp = f.create_group("trim")
        dst = grp.create_dataset('element', (n,), data=name, dtype=str_type,
                                 compression=h5zip)
        dst = grp.create_dataset('plane', (n,), data=plane, dtype=str_type,
                                 compression=h5zip)
        pvascii = [p.encode('ascii') for p in pvrb]
        dst = grp.create_dataset('pvrb', (n,), data=pvascii, dtype=str_type,
                                 compression=h5zip)
        pvascii = [p.encode('ascii') for p in pvsp]
        dst = grp.create_dataset('pvsp', (n,), data=pvascii, dtype=str_type,
                                 compression=h5zip)
        #
        grp = f.create_group("_rawdata_")
        dst = grp.create_dataset("rawmatrix", data = self._rawmatrix,
                                 compression=h5zip)
        dst = grp.create_dataset("rawkick", data = self._rawkick,
                                 compression=h5zip)
        dst = grp.create_dataset("mask", data = self._mask, dtype='i',
                                 compression=h5zip)
        
        f.close()

    def load_hdf5(self, filename, grp):
        """
        load data group *grp* from hdf5 file *filename*
        """
        import h5py
        f = h5py.File(filename, 'r')
        g = f[grp]['bpm']
        self.bpm = zip(g["element"], g["plane"], g["pvrb"])
        g = f[grp]['trim']
        self.trim = zip(g["element"], g["plane"], g["pvrb"], g["pvsp"])
        nbpm, ntrim = len(self.bpm), len(self.trim)
        self.m = np.zeros((nbpm, ntrim), 'd')
        self.m[:,:] = f[grp]['m'][:,:]
        t, npts = f[grp]["_rawdata_"]["rawkick"].shape
        self._rawkick = np.zeros((ntrim, npts), 'd')
        self._rawkick[:,:] = f[grp]["_rawdata_"]["rawkick"][:,:]
        self._rawmatrix = np.zeros((npts, nbpm, ntrim), 'd')
        self._rawmatrix[:,:,:] = f[grp]["_rawdata_"]["rawmatrix"][:,:,:]
        self._mask = np.zeros((nbpm, ntrim), dtype='i')
        self._mask[:,:] = f[grp]["_rawdata_"]["mask"][:,:]

        f.close()


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
            self.save_hdf5(filename)
        elif fmt == 'shelve':
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
            self.load_hdf5(filename, '/')
        elif fmt == 'shelve':
            f = shelve.open(filename, 'r')
            self.bpm = f["orm.bpm"]
            self.trim = f["orm.trim"]
            self.m = f["orm.m"]
            self._rawmatrix = f["orm._rawdata_.rawmatrix"]
            self._rawkick   = f["orm._rawdata_.rawkick"]
            self._mask      = f["orm._rawdata_.mask"]
        else:
            raise ValueError("format %s is not supported" % format)

        #print self.trim

    def getBpmNames(self):
        """
        The same order as appeared in orm rows. It may have duplicate bpm
        names in the return list.
        """
        return [v[0] for v in self.bpm]
    
    def hasBpm(self, bpm):
        """
        check if the bpm is used in this ORM measurement
        """

        for b in self.bpm:
            if b[0] == bpm: return True
        return False

    def getTrimNames(self):
        """
        The same order as appeared in orm columns. It may have duplicate trim
        names in the return list.
        """
        return [v[0] for v in self.trim]
    
    def hasTrim(self, trim):
        """
        check if the trim is used in this ORM measurement
        """
        for tr in self.trim:
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
        
    def update(self, src):
        """
        update the data using a new OrmData object *src*
        
        - masked, whether update when the value is masked to ignore

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
        #print "(%d,%d) -> (%d,%d)" % (nbpm0, ntrim0, nbpm, ntrim)
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
                # skip if any masked
                if src._mask[i,j]: continue
                ii = ibpm[i]
                if self._mask[ii,jj]: continue

                rawmatrix[:,ii,jj] = src._rawmatrix[:,i,j]
                mask[ii,jj] = src._mask[i,j]
                m[ii,jj] = src.m[i,j]
        self._rawmatrix = rawmatrix
        self._mask = mask
        self._rawkick = rawkick
        self.m = m

        self.bpmrb, self.trimsp = bpmrb, trimsp
        
    def getSubMatrix(self, bpm, trim, flags=('XY', 'XY'), **kwargs):
        """
        if only bpm name given, the return matrix will not equal to
        len(bpm),len(trim), since one bpm can have two lines (x,y) data.

        - *bpm* a list of bpm names
        - *trim* a list of trim names
        - *flags* is a tuple of (bpm plans, trim plans: ('X','X'), ('XY', 'Y') 

        optional:

        - *ignore_unmeasured* The unmeasured bpm/trim pairs will be
          ignored. Otherwise raise ValueError.
        """
        if not bpm or not trim: return None
        #if flags not in ['XX', 'XY', 'YY', 'YX', '**']: return None
        
        bpm_st  = set([v[0] for v in self.bpm])
        trim_st = set([v[0] for v in self.trim])

        ignore_unmeasured = kwargs.get('ignore_unmeasured', True)

        # only consider the bpm/trim in this ORM
        bsub = bpm_st.intersection(set(bpm))
        tsub = trim_st.intersection(set(trim))

        if not ignore_unmeasured:
            if len(bsub) < len(bpm):
                raise ValueError("Some BPMs are absent in orm measurement")
            if len(tsub) < len(trim):
                raise ValueError("Some Trims are absent in orm measurement")
        
        mat = np.zeros((len(bpm), len(trim)), 'd')
        for i,b in enumerate(self.bpm):
            if b[0] not in bpm: continue
            if b[1] not in flags[0]: continue
            ii = bpm.index(b[0])
            for j,t in enumerate(self.trim):
                if t[0] not in trim or t[1] not in flags[1]: continue
                jj = trim.index(t[0])
                mat[ii,jj] = self.m[i,j]

        return mat

    def getSubMatrixPv(self, bpm, trim):
        """
        return the submatrix according the given PVs for bpm and trim.

        the PV is readback for bpm, setpoint for trim
        """

        ib = [-1] * len(bpm)
        it = [-1] * len(trim)

        # index 2 is readback PV for BPM
        for i in range(len(self.bpm)):
            if not self.bpm[i][2] in bpm: continue
            ib[bpm.index(self.bpm[i][2])] = i

        # index 3 is setpoint PV for Trim
        for i in range(len(self.trim)):
            if not self.trim[i][3] in trim: continue
            it[trim.index(self.trim[i][3])] = i

        for i in range(len(ib)):
            if ib[i] == -1: 
                raise ValueError("BPM PV %s is not found in ORM data" % bpm[i])

        for i in range(len(it)):
            if it[i] == -1: 
                raise ValueError("Trim PV %s is not found in ORM data" % trim[i])

        m = np.zeros((len(bpm), len(trim)), 'd')
        for i in range(len(bpm)):
            for j in range(len(trim)):
                m[i,j] = self.m[ib[i], it[j]]
        return m

