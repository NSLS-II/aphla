#!/usr/bin/env python

"""
:author: Lingyun Yang <lyyang@bnl.gov>
:license:

"""

__all__ = ['OrmData', 'Twiss']

import os
from os.path import splitext
import numpy as np
import shelve

import logging
_logger = logging.getLogger(__name__)

class OrmData:
    r"""Orbit Response Matrix Data

    - *bpm* is a list of tuple (name, location, field)
    - *trim* is a list of tuple (name, location, field)
    - *m* 2D matrix, len(bpm) * len(trim)

    HDF5 format (.hdf5) is the preferred output for ORM data. It also supports
    shelve (.pkl) output format for short term storage.

    All data is saved in a group (like folder in file system, with default
    name "orm"):

    - *orm/m*, the response matrix with dimension (nbpm, ntrim).
    - *orm/bpm/element*, a list of BPM names.
    - *orm/bpm/location*, the s-position of bpms.
    - *orm/bpm/plane*, {'x', 'y'}.
    - *orm/bpm/_bpmpv*, optional. EPICS PVs for bpms.
    - *orm/trim/element*, corrector names
    - *orm/trim/location*, s-positions of correctors.
    - *orm/trim/plane*, {'x', 'y'}
    - *orm/trim/_trimpvrb*, optional, the readback EPICS PVs
    - *orm/trim/_trimpvsp*, optional, the setpoint EPICS PVs
    - *orm/_rawdata_/raworbit, optional, (ntrim, nbpm, npoints) ??
    - *orm/_rawdata_/rawkick, optional, (ntrim, npoints)
    - *orm/_rawdata_/mask, optional, (nbpm, ntrim)

    The private dataset has a prefix "_" in its name.
    """
    _fmtdict = {'.hdf5': 'HDF5', '.pkl':'shelve'}
    def __init__(self, datafile = None, group = None):
        # points for trim setting when calc dx/dkick
        #npts = 6

        # list of tuple, (name, location, plane)
        self.bpm = []
        self.trim = []

        # optional PV info, EPICS only
        self._bpmpv = None
        self._trimpvrb = None
        self._trimpvsp = None

        # 3d raw data
        self._raworbit = None
        self._mask = None
        self._rawkick = None
        self.m = None

        if datafile is not None and group is not None:
            self.load(datafile, group)
        elif datafile is not None:
            self.load(datafile)


    def _io_format(self, filename, formt):
        rt, ext = splitext(filename)
        if formt:
            fmt = formt
        elif ext in self._fmtdict.keys():
            fmt = self._fmtdict[ext]
        else:
            fmt = 'HDF5'
        return fmt
    
    def _save_hdf5(self, filename, group = "orm"):
        """
        save data in hdf5 format in HDF5 group (h5py.Group object).

        Note
        -----
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

    def _load_hdf5(self, filename, group = "orm"):
        """
        load data group *grp* from hdf5 file *filename*
        """
        grp = group
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


    def save(self, filename, **kwargs):
        """
        save the orm data into file, HDF5 or shelve.


        Example
        -------
        >>> save("orm.hdf5")
        >>> save("orm.pkl")
        >>> save("orm.shelve", format="shelve")
        """

        fmt = self._io_format(filename, kwargs.pop("format", None))

        if fmt == 'HDF5':
            self._save_hdf5(filename, **kwargs)
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

    def load(self, filename, **kwargs):
        """load data from file and guess its filetype based on extension"""
        self._load_v2(filename, **kwargs)

    def _load_v2(self, filename, **kwargs):
        """
        load orm data from binary file
        """
        if not os.path.exists(filename):
            raise ValueError("ORM data %s does not exist" % filename)

        fmt = self._io_format(filename, kwargs.pop("format", None))
            
        if fmt == 'HDF5':
            self._load_hdf5(filename, **kwargs)
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

    def exportBlock(self, fname, bpmplane, trimplane):
        dt = OrmData()
        ibpm  = [i for i,v in enumerate(self.bpm) if v[2] == bpmplane]
        itrim = [i for i,v in enumerate(self.trim) if v[2] == trimplane]
        dt.bpm  = [self.bpm[i] for i in ibpm]
        dt.trim = [self.trim[i] for i in itrim]

        npt = np.shape(self._rawkick)
        dt.m = np.zeros((len(ibpm), len(itrim)), 'd')
        dt._rawkick = np.zeros((len(itrim), npt[1]), 'd')
        #dt._raworbit = np.zeros((len(ibpm), len(itrim), npt[1]), 'd')
        for j in range(len(itrim)):
            dt._rawkick[j,:] = self._rawkick[itrim[j],:]
            for i in range(len(ibpm)):
                dt.m[i,j] = self.m[ibpm[i], itrim[j]]
                #dt._raworbit[i,j,:] = self._raworbit[ibpm[i], itrim[j],:]
        dt.save(fname)

    def getBpmNames(self):
        """The BPM names of ORM. 

        It has same order as appeared in orm rows.  The result may have
        duplicate bpm names in the return list.
        """
        return [v[0] for v in self.bpm]
    
    def hasBpm(self, bpm, fields=['x', 'y']):
        """check if the bpm is used in this ORM measurement"""

        for b in self.bpm:
            if b[0] == bpm and b[2] in fields: return True
        return False

    def getTrimNames(self):
        """a list of corrector names.
        
        The same order as appeared in orm columns. It may have duplicate trim
        names in the return list.
        """
        return [v[0] for v in self.trim]
    
    def hasTrim(self, trim, fields=['x', 'y']):
        """check if the trim is used in this ORM measurement"""
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

    def index(self, elem, field):
        """
        return the index for given (element, fields). Raise ValueError if does
        not exist.

        Examples
        ---------
        >>> index('BPM1', 'x')
        >>> index('TRIM1', 'y')

        """
        for i,b in enumerate(self.bpm):
            if b[0] == elem and b[2] == field: return i
        for i,t in enumerate(self.trim):
            if t[0] == elem and t[2] == field: return i
            
        raise ValueError("(%s,%s) are not in this ORM data" % (elem, field))


    def __update(self, src):
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

    def get(self, bpm, bpmfld, trim, trimfld):
        """get the matrix element by bpm/trim name and field"""
        irow, icol = None, None
        for i,r in enumerate(self.bpm):
            if r[0] != bpm or r[2] != bpmfld: continue
            irow = i
        for i,r in enumerate(self.trim):
            if r[0] != trim or r[2] != trimfld: continue
            icol = i
        if irow is None or icol is None: return None
        return self.m[irow, icol]

    def getSubMatrix(self, bpm, trim, **kwargs):
        """
        get submatrix for certain bpm and trim.

        Parameters
        -----------
        bpm : a list of bpm (name, field) tuple
        trim : a list of trim (name, field) tuple
        ignore_unmeasured : optional, bool.
            if True, the input bpm/trim pairs which are not in the OrmData
            will be ignored. Otherwise raise ValueError.

        Returns
        --------
        m : the matrix
        bpmlst : a list of (bpmname, field)
        trimlst : a list of (trimname, field)

        Examples
        ---------
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
            _logger.warn("BPM list has duplicates")
        if len(itrim) != len(set(itrim)): 
            _logger.warn("Trim list has duplicates")

            
        if len(ibpm) < len(bpm):
            if not ignore_unmeasured:
                raise ValueError("Some BPMs are absent in orm measurement")
            else:
                _logger.warn("Some BPMs not in the measured ORM are ignored")
        if len(itrim) < len(trim):
            if not ignore_unmeasured:
                raise ValueError("Some Trims are absent in orm measurement")
            else:
                _logger.warn("Some Trims not in the measured ORM are ignored")
        
        mat = np.take(np.take(self.m, ibpm, axis=0), itrim, axis=1)

        bpmlst  = [(self.bpm[i][0], self.bpm[i][2]) for i in ibpm]
        trimlst = [(self.trim[i][0], self.trim[i][2]) for i in itrim]
        return mat, bpmlst, trimlst

    def getMatrix(self, bpmrec, trimrec, **kwargs):
        """
        return the matrix for given bpms and trims.

        Parameters
        -----------
        bpmrec : a list of (bpmname, field) tuple. e.g. [('BPM1', 'x')]
        trimrec : a list of (trimname, field) tuple, similar to *bpmrec*
        full : bool, default True
            return full matrix besides the columns and rows for given trims
            and bpms.
        ignore : a list of element names which is ignored in the result.

        Returns
        --------
        m : the matrix (MxN)
        bpmrec : a list of (bpm, field), length M
        trimrec : a list of (trim, field), length N

        Notes
        -------
        if *full* is True, the returned (M,N) will be same size as stored data
        and the upper left corner is for given bpms and trims. Otherwise only
        the upper left corner is provided.        

        if both bpmrec and trimrec are None, use the original full matrix
        (minus the ignore list when provided)

        Examples
        ---------
        >>> getMatrix([('bpm1', 'x'), ('bpm1', 'y')],
                      [('trim1', 'x'), ('trim1', 'y')], True)

        """

        full = kwargs.get('full', True)
        ignore = kwargs.get('ignore', [])

        _logger.info("ignore elements:{0}".format(ignore))
        # the upper left corner, BPM/COR from input.
        if bpmrec is None and trimrec is None:
            rowidx = [self.index(v[0], v[2]) for v in self.bpm 
                      if v[0] not in ignore]
            colidx = [self.index(v[0], v[2]) for v in self.trim 
                      if v[0] not in ignore]
        else:
            rowidx = [self.index(b, f) for b,f in bpmrec if b not in ignore]
            colidx = [self.index(c, f) for c,f in trimrec if c not in ignore]

        #print rowidx + extrarow
        #print colidx + extracol
        if full:
            # full matrix
            extrarow = [i for i in range(len(self.bpm)) 
                        if i not in rowidx and self.bpm[i][0] not in ignore]
            extracol = [i for i in range(len(self.trim)) 
                        if i not in colidx and self.trim[i][0] not in ignore]
            rowidx = rowidx + extrarow
            colidx = colidx + extracol

        m = np.take(np.take(self.m, rowidx, axis=0), colidx, axis=1)
        brec = [(self.bpm[i][0], self.bpm[i][2]) for i in rowidx]
        trec = [(self.trim[i][0], self.trim[i][2]) for i in colidx]
            
        _logger.info("get BPM {0}, COR {1}".format(len(brec), len(trec)))
        return m, brec, trec
            


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
        get twiss value in tuple or float.

        Parameters
        -----------
        name : str, twiss item name: 'alpha', 'beta', 'gamma', 'phi'.
            the item name can add postfix 'x' or 'y' if only one plane is wanted.

        Examples
        ---------
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
    Twiss stores a twiss table

    A list of twiss items and related element names. It has tunes and
    chromaticities.

    Examples
    ---------
    >>> tw = Twiss()
    >>> print tw[0]

    """
    def __init__(self, name):
        self.element = []
        self._twlist = []
        self._name = name
        self.tune = (None, None)
        self.chrom = (None, None)
        
    def _find_element(self, elemname):
        try:
            i = self.element.index(elemname)
            return i
        except:
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
        if not self.element or not self._twlist: return ''

        s = "# %d " % len(self.element) + TwissItem.header() + '\n'
        for i, e in enumerate(self.element):
            s = s + "%16s " % e + self._twlist[i].__repr__() + '\n'
        return s

    def append(self, twi):
        """
        add a twiss item :class:`TwissItem`
        """
        self._twlist.append(twi)

    def getTwiss(self, elemlst, col, **kwargs):
        """
        return a list of twiss functions when given a list of element name.
        
        Parameters
        -----------
        elemlst : list. names of elements.
        col : list. columns can be 's', 'beta', 'betax', 'betay', 'alpha',
            'alphax', 'alphay', 'phi', 'phix', 'phiy'. If without 'x' or 
            'y' postfix, 'beta', 'alpha' and 'phi' will be expanded to
            two columns.

        Examples
        ---------
        >>> getTwiss(['E1', 'E2'], col=('s', 'beta'))

        """
        spos = kwargs.get('spos', None)

        if not col: return None
        clean = kwargs.get('clean', False)

        # check if element is valid
        iret = []
        for e in elemlst:
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


    def load(self, filename, **kwargs):
        """loading hdf5 file in a group default 'twiss'"""
        self._load_hdf5(filename, **kwargs)

    def _load_hdf5(self, filename, group = "twiss"):
        """read data from HDF5 file in *group*"""
        import h5py
        f = h5py.File(filename, 'r')
        self.element = list(f[group]['element'])
        self.tune = tuple(f[group]['tune'])
        self._twlist = []
        tw = f[group]['twtable']
        m, n = np.shape(tw)
        for i in range(m):
            twi = TwissItem()
            twi.update(tw[i,:])
            self._twlist.append(twi)

        f.close()
        
    def _load_sqlite3(self, fname, table="twiss"):
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

            self.element.append(lst[0])
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

