#!/usr/bin/env python

"""
Response Matrix Data
----------------------------------

:author: Lingyun Yang
:license:

:class:`~aphla.apdata.OrmData` is an Orbit Response Matrix (ORM) 

"""

__all__ = ['OrmData', 'Twiss']

import os
from os.path import splitext
import numpy as np
import shelve

import logging
logger = logging.getLogger(__name__)

class OrmData:
    """
    Orbit Response Matrix Data

    - *bpm* is a list of tuple (name, location, field)
    - *trim* is a list of tuple (name, location, field)
    - *m* 2D matrix, len(bpm) * len(trim)
    """
    fmtdict = {'.hdf5': 'HDF5', '.pkl':'shelve'}
    def __init__(self, datafile = None):
        # points for trim setting when calc dx/dkick
        #npts = 6

        # list of tuple, (name, location, plane)
        self.bpm = []
        self.trim = []

        # optional PV info
        self._bpmpv = None
        self._trimpvrb = None
        self._trimpvsp = None

        # 3d raw data
        self._raworbit = None
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
    
    def save_hdf5(self, filename, group = "ormdata"):
        """
        save data to hdf5 format

        h5py before v2.0 does not accept unicode directly.
        """
        import h5py
        h5zip = None # 'gzip' works in default install
        f = h5py.File(filename, 'w')
        grp = f.create_group(group)

        str_type = h5py.new_vlen(str)
        m, n = np.shape(self.m)
        dst = grp.create_dataset('m', (m,n), data=self.m, compression=h5zip)
        #
        tgrp = grp.create_group('bpm')
        name, spos, plane = zip(*self.bpm)
        # dtype('<U9') is not recognized in earlier h5py
        if h5py.version.version_tuple[:3] <= (2,1,1):
            name = [v.encode('ascii') for v in name]
            #pv = [p.encode('ascii') for p in pv]
        dst = tgrp.create_dataset('element', (m,), data = name, dtype=str_type, 
                                 compression=h5zip)
        dst = tgrp.create_dataset('location', (m,), data = spos, 
                                  compression=h5zip)
        dst = tgrp.create_dataset('plane', (m,), data = plane, dtype=str_type,
                                 compression=h5zip)
        if self._bpmpv:
            dst = tgrp.create_dataset(
                '_bpmpv', (m,), data = pv, dtype=str_type,
                compression=h5zip)
        #
        name, spos, plane = zip(*self.trim)
        # dtype('<U9') is not recognized in earlier h5py
        if h5py.version.version_tuple[:3] <= (2,1,1):
            name = [v.encode('ascii') for v in name]
            #pvrb = [p.encode('ascii') for p in pvrb]
            #pvsp = [p.encode('ascii') for p in pvsp]
        tgrp = grp.create_group("trim")
        dst = tgrp.create_dataset('element', (n,), data=name, dtype=str_type,
                                 compression=h5zip)
        dst = tgrp.create_dataset('location', (n,), data = spos, 
                                 compression=h5zip)
        dst = tgrp.create_dataset('plane', (n,), data=plane, dtype=str_type,
                                 compression=h5zip)
        if self._trimpvrb:
            dst = tgrp.create_dataset(
                '_trimpvrb', (n,), data=pvrb, dtype=str_type,
                compression=h5zip)
        if self._trimpvsp:
            dst = tgrp.create_dataset(
                '_trimpvsp', (n,), data=pvsp, dtype=str_type,
                compression=h5zip)
        #
        grp = f.create_group("_rawdata_")
        if self._raworbit is not None:
            dst = grp.create_dataset("raworbit", data = self._raworbit,
                                     compression=h5zip)
        if self._rawkick is not None:
            dst = grp.create_dataset("rawkick", data = self._rawkick,
                                     compression=h5zip)
        if self._mask is not None:
            dst = grp.create_dataset("mask", data = self._mask, dtype='i',
                                     compression=h5zip)
        
        f.close()

    def load_hdf5(self, filename, grp = "orm"):
        """
        load data group *grp* from hdf5 file *filename*
        """
        import h5py
        f = h5py.File(filename, 'r')
        g = f[grp]['bpm']
        self.bpm = zip(g["element"], g["location"], g["plane"])
        g = f[grp]['trim']
        self.trim = zip(g["element"], g["location"], g["plane"])
        nbpm, ntrim = len(self.bpm), len(self.trim)
        self.m = np.zeros((nbpm, ntrim), 'd')
        self.m[:,:] = f[grp]['m'][:,:]
        if "_rawdata_" in f[grp]:
            t, npts = f[grp]["_rawdata_"]["rawkick"].shape
            self._rawkick = np.zeros((ntrim, npts), 'd')
            self._rawkick[:,:] = f[grp]["_rawdata_"]["rawkick"][:,:]
            self._raworbit = np.zeros((npts, nbpm, ntrim), 'd')
            #self._raworbit[:,:,:] = f[grp]["_rawdata_"]["raworbit"][:,:,:]
            self._mask = np.zeros((nbpm, ntrim), dtype='i')
            #self._mask[:,:] = f[grp]["_rawdata_"]["mask"][:,:]

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
            f['orm._rawdata_.raworbit'] = self._raworbit
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
            self.load_hdf5(filename)
        elif fmt == 'shelve':
            f = shelve.open(filename, 'r')
            self.bpm = f["orm.bpm"]
            self.trim = f["orm.trim"]
            self.m = f["orm.m"]
            self._raworbit = f["orm._rawdata_.raworbit"]
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
    
    def hasBpm(self, bpm, fields=['x', 'y']):
        """
        check if the bpm is used in this ORM measurement
        """

        for b in self.bpm:
            if b[0] == bpm and b[2] in fields: return True
        return False

    def getTrimNames(self):
        """
        The same order as appeared in orm columns. It may have duplicate trim
        names in the return list.
        """
        return [v[0] for v in self.trim]
    
    def hasTrim(self, trim, fields=['x', 'y']):
        """
        check if the trim is used in this ORM measurement
        """
        for tr in self.trim:
            if tr[0] == trim and tr[2] in fields: return True
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

    def _index_pv(self, pv):
        """
        return pv index of BPM, TRIM
        """
        if self._bpmpv:
            for i,b in enumerate(self._bpmpv):
                if b[-1] == pv: return i
        if self._trimpvrb:
            for j,t in enumerate(self._trimpvrb):
                if t[-2] == pv or t[-1] == pv:
                    return j
        if self._trimpvsp:
            for j,t in enumerate(self._trimpvsp):
                if t[-2] == pv or t[-1] == pv:
                    return j
            
        return None
    
    def _index_2(self, elem, fields):
        """
        return row index of BPM, or colum index for TRIM

        :param elem: element name
        """
        ret = [None] * len(fields)
        for i,b in enumerate(self.bpm):
            if b[0] != elem or b[2] not in fields: continue
            ret[fields.index(b[2])] = i
        for j,t in enumerate(self.trim):
            if t[0] != elem or t[2] not in fields: continue
            ret[fields.index(t[2])] = j
        return ret

    def index(self, *argv):
        """
        return the index of a pv or (element, fields)

        :Example:

          >>> index('PV1')
          >>> index('BPM1', ['x', 'y'])
        """
        if len(argv) == 1:
            return self._index_pv(argv[0])
        elif len(argv) == 2:
            return self._index_2(argv[0], argv[1])
        else:
            raise RuntimeError("Invalid number of parameters")

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
            if self._pv_index(b[-1]) < 0:
                bpm.append(b)
        for j,t in enumerate(src.trim):
            if self._pv_index(t[-2]) < 0:
                trim.append(t)
        npts, nbpm0, ntrim0 = np.shape(self._raworbit)
        
        nbpm, ntrim = len(bpm), len(trim)
        #print "(%d,%d) -> (%d,%d)" % (nbpm0, ntrim0, nbpm, ntrim)
        # the merged is larger
        raworbit = np.zeros((npts, nbpm, ntrim), 'd')
        mask      = np.zeros((nbpm, ntrim), 'i')
        rawkick   = np.zeros((ntrim, npts), 'd')
        m         = np.zeros((nbpm, ntrim), 'd')

        raworbit[:, :nbpm0, :ntrim0] = self._raworbit[:,:,:]
        mask[:nbpm0, :ntrim0]         = self._mask[:,:]
        m[:nbpm0, :ntrim0]            = self.m[:,:]
        # still updating rawkick, even it is masked
        rawkick[:ntrim0, : ]          = self._rawkick[:,:]

        # find the index
        bpmrb = [b[-1] for b in bpm]
        trimsp = [t[-1] for t in trim]
        ibpm  = [ bpmrb.index(b[-1]) for b in src.bpm ]
        itrim = [ trimsp.index(t[-1]) for t in src.trim ]
        
        for j, t in enumerate(src.trim):
            jj = itrim[j]
            rawkick[jj,:] = src._rawkick[j,:]
            for i, b in enumerate(src.bpm):
                # skip if any masked
                if src._mask[i,j]: continue
                ii = ibpm[i]
                if self._mask[ii,jj]: continue

                raworbit[:,ii,jj] = src._raworbit[:,i,j]
                mask[ii,jj] = src._mask[i,j]
                m[ii,jj] = src.m[i,j]
        self._raworbit = raworbit
        self._mask = mask
        self._rawkick = rawkick
        self.m = m

        self.bpmrb, self.trimsp = bpmrb, trimsp
        
    def getMatrixIndex(self, bpm, trim):
        """
        find the index for given list of bpm and tirm.

        :param bpm: bpm names
        :param trim: trim names

        seealso :func:`OrmData.getSubMatrix`
        """
        bpmidx, trimidx = [], []

        for i,b in enumerate(bpm):
            bpmidx.append(self._index_2(b, ['x', 'y']))
        for i,t in enumerate(trim):
            trimidx.append(self._index_2(t, ['x', 'y']))

        return bpmidx, trimidx

    def getSubMatrix(self, bpm, trim, **kwargs):
        """
        get submatrix for certain bpm and trim.

        :param bpm: a list of bpm (name, field) tuple
        :param trim: a list of trim (name, field) tuple
        :param ignore_unmeasured: optional (True, False).

        if *ignore_unmeasured* is True, the input bpm/trim pairs which are not
        in the OrmData will be ignored. Otherwise raise ValueError.

        if only bpm name given, the return matrix will not equal to
        len(bpm),len(trim), since one bpm can have two lines (x,y) data.

        :Example:

          >>> getSubMatrix([('bpm1', 'x'), ('bpm2', 'x')], None)
        """
        if not bpm or not trim: return None
        #if flags not in ['XX', 'XY', 'YY', 'YX', '**']: return None
        
        #ibpm  = set([v[0] for v in self.bpm])
        #itrim = set([v[0] for v in self.trim])

        ignore_unmeasured = kwargs.get('ignore_unmeasured', True)

        if bpm is None:
            ibpm = range(len(self.bpm))
        else:
            ibpm  = [i for i,v in enumerate(self.bpm) if (v[0], v[2]) in bpm]
        
        if trim is None:
            itrim = range(len(self.bpm))
        else:
            itrim = [i for i,v in enumerate(self.trim) if (v[0], v[2]) in trim]
        
        if len(ibpm) != len(set(ibpm)): 
            logger.warn("BPM list has duplicates")
        if len(itrim) != len(set(itrim)): 
            logger.warn("Trim list has duplicates")

            
        if len(ibpm) < len(bpm):
            if not ignore_unmeasured:
                raise ValueError("Some BPMs are absent in orm measurement")
            else:
                logger.warn("Some BPMs not in the measured ORM are ignored")
        if len(itrim) < len(trim):
            if not ignore_unmeasured:
                raise ValueError("Some Trims are absent in orm measurement")
            else:
                logger.warn("Some Trims not in the measured ORM are ignored")
        
        mat = np.take(np.take(self.m, ibpm, axis=0), itrim, axis=1)

        bpmlst  = [(self.bpm[i][0], self.bpm[i][2]) for i in ibpm]
        trimlst = [(self.trim[i][0], self.trim[i][2]) for i in itrim]
        return mat, bpmlst, trimlst

    def getSubMatrixPv(self, bpmpvs, trimpvs):
        """
        return the submatrix according the given PVs for bpm and trim.

        :param bpmpvs: pv list for BPMs
        :param trimpvs: pv list for Trims

        the PV is readback for bpm, setpoint for trim
        """
        if not self._bpmpv or not self._trimpvsp: return None

        ib = [self._bpmpv.index(p) for p in bpmpvs if p in self._bpmpv]
        it = [self._bpmpv.index(p) for p in trimpvs if p in self._trimpvsp]

        m = np.take(np.take(self.m, ib, axis=0), it, axis=1)

        return m

            

"""
Twiss
~~~~~~

:author: Lingyun Yang
:date: 2011-05-13 12:40

stores twiss data.
"""

class TwissItem:
    """
    The twiss parameter at one location

    ===============  =======================================================
    Twiss(Variable)  Description
    ===============  =======================================================
    *s*              location
    *alpha*          alpha
    *beta*           beta
    *gamma*          gamma
    *eta*            dispersion
    *phi*            phase
    ===============  =======================================================
    """

    def __init__(self, **kwargs):
        self.s     = kwargs.get('s', 0.0)
        self.alpha = kwargs.get('alpha', (0.0, 0.0))
        self.beta  = kwargs.get('beta', (0.0, 0.0))
        self.gamma = kwargs.get('gamma', (0.0, 0.0))
        self.eta   = kwargs.get('eta', (0.0, 0.0))
        self.phi   = kwargs.get('phi', (0.0, 0.0))

    @classmethod
    def header(cls):
        return "# s  alpha  beta  eta  phi"

    def __repr__(self):
        return "%.3f % .2f % .2f  % .2f % .2f  % .2f % .2f  % .2f % .2f" % \
            (self.s, self.alpha[0], self.alpha[1],
             self.beta[0], self.beta[1], self.eta[0], self.eta[1],
             self.phi[0], self.phi[1])

    def get(self, name):
        """
        get twiss value

        :param name: twiss item name
        :type name: str
        :return: twiss value
        :rtype: tuple, float
        :Example:

            >>> get('alpha')
            (0.0, 0.0)
            >>> get('betax')
            0.1
        """
        d = {'alphax': self.alpha[0], 'alphay': self.alpha[1],
             'betax': self.beta[0], 'betay': self.beta[1],
             'gammax': self.gamma[0], 'gammay': self.gamma[1],
             'etax': self.eta[0], 'etay': self.eta[1],
             'phix': self.phi[0], 'phiy': self.phi[1]}

        if hasattr(self, name):
            return getattr(self, name)
        elif name in d.keys():
            return d[name]
        else:
            return None

    def update(self, lst):
        """
        update with a list in the order of s, alpha, beta, gamma, eta and phi.
        'x' and 'y'.
        """
        n = len(lst)
        if n != 11:
            raise RuntimeError("the input has wrong size %d != 11" % n)

        self.s = lst[0]
        self.alpha = (lst[1], lst[2])
        self.beta  = (lst[3], lst[4])
        self.gamma = (lst[5], lst[6])
        self.eta   = (lst[7], lst[8])
        self.phi   = (lst[9], lst[10])

    
class Twiss:
    """
    Twiss table

    A list of twiss items and related element names. It has tunes and
    chromaticities.

    :Example:

        tw = Twiss()
        print tw[0]
    """
    def __init__(self, name):
        self._elements = []
        self._twlist = []
        self._name = name
        self.tune = (None, None)
        self.chrom = (None, None)
        
    def _find_element(self, elemname):
        try:
            i = self._elements.index(elemname)
            return i
        except IndexError:
            return None

        return None

    def __getitem__(self, key):
        if isinstance(key, int):
            i = key
            return self._twlist[i]
        elif isinstance(key, str) or isinstance(key, unicode):
            i = self._find_element(key)
            return self._twlist[i]
        else:
            return None

    def __repr__(self):
        if not self._elements or not self._twlist: return ''

        s = "# %d " % len(self._elements) + TwissItem.header() + '\n'
        for i, e in enumerate(self._elements):
            s = s + "%16s " % e + self._twlist[i].__repr__() + '\n'
        return s

    def append(self, twi):
        """
        :param twi: twiss value at one point
        :type twi: :class:`~aphla.twiss.TwissItem`
        """

        self._twlist.append(twi)

    def getTwiss(self, col, **kwargs):
        """
        return a list of twiss functions when given a list of element name.
        
        - *col*, a list of columns : 's', 'beta', 'betax', 'betay',
          'alpha', 'alphax', 'alphay', 'phi', 'phix', 'phiy'.
        - *clean*, skip the unknown elements 
        
        :Example:

          getTwiss(['E1', 'E2'], col=('s', 'beta'))

        'beta', 'alpha' and 'phi' will be expanded to two columns.
        """
        elem = kwargs.get('elements', None)
        spos = kwargs.get('spos', None)

        if not col: return None
        clean = kwargs.get('clean', False)

        # check if element is valid
        iret = []
        for e in elem:
            i = self._find_element(e)
            if i >= 0: iret.append(i)
            elif clean: continue
            else: iret.append(None)
            
        ncol = 0
        for c in col:
            if c in ('s', 'betax', 'betay', 'alphax', 'alphay', 
                     'etax', 'etay', 'phix', 'phiy'):
                ncol += 1
            elif c in ('beta', 'alpha', 'eta', 'phi'):
                ncol += 2
        ret = []
        for i in iret:
            if i == None:
                ret.append([None]*ncol)
                continue
            row = []
            tw = self._twlist[i]
            for c in col:
                v = tw.get(c)
                if isinstance(v, (list, tuple)):
                    row.extend(v)
                elif v is not None:
                    row.append(v)
                else:
                    row.append(None)
                    raise ValueError("column '%s' not supported in twiss" % c)
            ret.append(row)
        return np.array(ret, 'd')


    def load_hdf5(self, filename, group = "twiss"):
        """
        read data from HDF5 file
        """
        import h5py
        f = h5py.File(filename, 'r')
        self.element = f[group]['element']
        self.tune = f[group]['tune']
        self._twlist = []
        tw = f[group]['twtable']
        m, n = np.shape(tw)
        for i in range(m):
            twi = TwissItem()
            twi.update(tw[i,:])
            self._twlist.append(twi)

        f.close()
        
    def load_sqlite3(self, fname, table="twiss"):
        """
        read twiss from sqlite db file *fname*.

        It looks for table "prefix_tbl' and 'prefix_par'
        """
        import sqlite3
        conn = sqlite3.connect(fname)
        c = conn.cursor()
        # by-pass the front-end which do not allow parameterize table name
        qline = "select * from %s" % table
        c.execute(qline)
        # head of columns
        allcols = [v[0] for v in c.description]
        twissitems = ['element', 's', 'alphax', 'alphay', 'betax',
                      'betay', 'gammax', 'gammay',
                      'etax', 'etay', 'phix', 'phiy']
        ihead = []
        for i,head in enumerate(twissitems):
            if head in allcols: ihead.append([head, i, allcols.index(head)])
            else: ihead.append([head, i, None])

        for row in c:
            twi = TwissItem()
            lst = [None] * len(ihead)
            for i,v in enumerate(ihead):
                if v[-1] is not None: lst[i] = row[v[-1]]

            self._elements.append(lst[0])
            twi.update(lst[1:])
            self._twlist.append(twi)
        # by-pass the front-end which do not allow parameterize table name
        qline = "select par,idx,val from %s_par" % prefix
        c.execute(qline)
        self.tune  = [None, None]
        self.chrom = [None, None]
        
        for row in c:
            if row[0] == 'tunex': self.tune[0] = row[2]
            elif row[0] == 'tuney': self.tune[1] = row[2]
            elif row[0] == 'chromx': self.chrom[0] = row[2]
            elif row[0] == 'chromy': self.chrom[1] = row[2]
        
        c.close()
        conn.close()

