#!/usr/bin/env python

"""
:author: Lingyun Yang <lyyang@bnl.gov>
:license:

"""

__all__ = ['OrmData', 'TwissData', 'saveSnapshotH5']

import os
from os.path import splitext
import numpy as np
import shelve
import h5py
import sqlite3

import warnings

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

    The private dataset has a prefix "_" in its name."""

    def __init__(self, datafile = None, group = None):
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


    def _save_hdf5(self, filename, group = "OrbitResponseMatrix"):
        """
        save data in hdf5 format in HDF5 group (h5py.Group object).

        Note
        -----
        h5py before v2.0 does not accept unicode directly.
        """
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
        #if h5py.version.version_tuple[:3] <= (2,1,1):
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
        #if h5py.version.version_tuple[:3] <= (2,1,1):
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

    def _load_hdf5(self, filename, group = "OrbitResponseMatrix"):
        """
        load data group *grp* from hdf5 file *filename*
        """
        grp = group
        f = h5py.File(filename, 'r')
        if group not in f:
            _logger.warn("No '%s' group in '%s'. Ignore." % (group, filename))
            return

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
        fmt = kwargs.pop("format", None)
        if fmt == 'HDF5' or filename.endswith(".hdf5"):
            self._save_hdf5(filename, **kwargs)
        elif fmt == 'shelve' or filename.endswith(".pkl"):
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
        
        fmt = kwargs.get("format", None)
        if fmt == 'HDF5' or filename.endswith(".hdf5"):
            self._load_hdf5(filename, **kwargs)
        elif fmt == 'shelve' or filename.endswith(".pkl"):
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
        """export one of the XX, XY, YX, YY blocks of ORM data
        
        Examples
        ---------
        >>> ormdata.exportBlock("orm.hdf5", "x", "x")
        """
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

        It has same order as appeared in orm rows. For a full matrix with
        coupling terms, the result may have duplicate bpm names in the return
        list.
        """
        return [v[0] for v in self.bpm]
    
    def hasBpm(self, bpm, fields=['x', 'y']):
        """check if the bpm is used in this ORM measurement"""

        for b in self.bpm:
            if b[0] == bpm and b[2] in fields: return True
        return False

    def getTrimNames(self):
        """a list of corrector names.
        
        The same order as appeared in orm columns. For a full matrix with
        coupling terms, it may have duplicate trim names in the return list.
        """
        return [v[0] for v in self.trim]
    
    def hasTrim(self, trim, fields=['x', 'y']):
        """check if the trim is used in this ORM measurement"""
        for tr in self.trim:
            if tr[0] == trim and tr[2] in fields: return True
        return False

    def maskCrossTerms(self):
        """mask the H/V and V/H terms. 

        If the coupling between horizontal/vertical kick and
        vertical/horizontal BPM readings, it's reasonable to mask out
        these coupling terms.
        """

        for i,b in enumerate(self.bpm):
            for j,t in enumerate(self.trim):
                # b[1] = ['X'|'Y'], similar for t[1]
                if b[1] != t[1]: self._mask[i,j] = 1

    def index(self, elem, field):
        """return the index for given (element, fields). 

        Raise ValueError if does not exist.

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
        """update the data using a new OrmData object.
        
        The masked values in *src* are ignored. 

        rawkick is still updated regardless of masked or not. It is advised
        that both orm use same rawkick for measurement.
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
        """get the matrix element by bpm/trim name and field

        Examples
        ---------
        >>> get('bpm1', 'x', 'corr1', 'x')

        """
        irow, icol = None, None
        for i,r in enumerate(self.bpm):
            if r[0] != bpm or r[2] != bpmfld: continue
            irow = i
        for i,r in enumerate(self.trim):
            if r[0] != trim or r[2] != trimfld: continue
            icol = i
        if irow is None or icol is None: return None
        return self.m[irow, icol]


    def getMatrix(self, bpmrec, trimrec, **kwargs):
        """return the matrix for given bpms and trims.

        Parameters
        -----------
        bpmrec : a list of (bpmname, field) tuple.
            If it is None, use all bpms.
        trimrec : a list of (trimname, field) tuple, similar to *bpmrec*
        full : bool, default True
            Returns full matrix besides the columns and rows for given trims
            and bpms. The given BPMs(rows) and trims(columns) will be arranged
            at the upper left corner. If full is False, only the upper left
            corner is provided.
        ignore : a list of element names which is ignored in the result.

        Returns
        --------
        m : the matrix (MxN)
        bpmrec : a list of (bpm, field), length M
        trimrec : a list of (trim, field), length N

        Examples
        ---------
        >>> getMatrix([('bpm1', 'x'), ('bpm1', 'y')],
                      [('trim1', 'x'), ('trim1', 'y')], True)

        """

        full = kwargs.get('full', True)
        ignore = kwargs.get('ignore', [])

        _logger.info("ignore elements:{0}".format(ignore))

        # the upper left corner, BPM/COR from input.
        if bpmrec is None:
            rowidx = [self.index(v[0], v[2]) for v in self.bpm 
                      if v[0] not in ignore]
        else:
            rowidx = [self.index(b, f) for b,f in bpmrec if b not in ignore]

        if trimrec is None:
            colidx = [self.index(v[0], v[2]) for v in self.trim 
                      if v[0] not in ignore]
        else:
            colidx = [self.index(c, f) for c,f in trimrec if c not in ignore]

        # returns reordered full matrix, instead of upper left corner.
        if full:
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
            


class TwissData:
    """Twiss stores a twiss table.

    A list of twiss items and related element names. It has tunes and
    chromaticities.

    Examples
    ---------
    >>> tw = TwissData()
    >>> print tw[0]

    """
    def __init__(self, name):
        self._name = name
        self.tune   = (0.0, 0.0)
        self.chrom  = (0.0, 0.0)
        self.alphac = 0.0 #
        self.element = []
        self._twtable = []
        self._cols = ['s', 'alphax', 'alphay', 'betax', 'betay',
                      'gammax', 'gammay', 'etax', 'etay', 'phix', 'phiy']

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
            return self._twtable[i]
        elif isinstance(key, str) or isinstance(key, unicode):
            i = self._find_element(key)
            return self._twtable[i]
        else:
            return None

    def __repr__(self):
        if not self.element or not self._twtable: return ''

        s = "# %d " % len(self.element) + TwissItem.header() + '\n'
        for i, e in enumerate(self.element):
            s = s + "%16s " % e + self._twtable[i].__repr__() + '\n'
        return s

    def get(self, elemlst, col, **kwargs):
        """get a list of twiss functions when given a list of element names.
        
        Parameters
        -----------
        elemlst : list. 
            names of elements.
        col : list. 
            columns can be 's', 'betax', 'betay', 'alphax', 'alphay', 'phix',
            'phiy', 'etax', 'etay'. 

        Examples
        ---------
        >>> getTwiss(['E1', 'E2'], col=('s', 'betax', 'betay'))

        """
        if not col: return None
        clean = kwargs.get('clean', False)

        # check if element is valid
        ret = []
        for e in elemlst:
            if e not in self.element:
                raise RuntimeError("element '{0}' is not in twiss "
                                   "data: {1}".format(e, self.element))
            i = self.element.index(e)
            dat = []
            for c in col:
                if c in self._cols:
                    j = self._cols.index(c)
                    dat.append(self._twtable[i,j])
                else:
                    raise RuntimeError("column '%s' is not in twiss data" % c)
            ret.append(dat)
            
        return np.array(ret, 'd')


    def load(self, filename, **kwargs):
        """loading hdf5 file in a group default 'twiss'"""
        self._load_hdf5_v2(filename, **kwargs)

    def set(self, **kw):
        """set data, delete all previous data"""
        if "element" in kw:
            self.element = kw["element"]
        NROW = len(self.element)
        self._twtable = np.zeros((NROW, len(self._cols)), 'd')
        for i,k in enumerate(self._cols):
            self._twtable[:,i] = kw.get(k, np.nan)
        self.chrom = kw.get("chrom", None)
        self.tune = kw.get("tune", None)
        self.alphac = kw.get("alphac", None)

    def _load_hdf5_v1(self, filename, group = "Twiss"):
        """read data from HDF5 file in *group*"""
        f = h5py.File(filename, 'r')
        self.element = list(f[group]['element'])
        self.tune = tuple(f[group]['tune'])
        self._twtable = np.array(f[group]['twtable'])
        f.close()


    def _load_hdf5_v2(self, filename, group = "Twiss"):
        """read data from HDF5 file in *group*"""
        f = h5py.File(filename, 'r')
        if group not in f:
            _logger.warn("no '%s' in '%s', ignore" % (group, filename))
            return
        grp = f[group]
        self.tune = tuple(grp['tune'])
        self.element = list(grp['twtable']['element'])
        self._twtable = np.zeros((len(self.element), 11), 'd')
        for i,k in enumerate(self._cols):
            self._twtable[:,i] = grp['twtable'][:,k]
        f.close()
        _logger.info("loaded {0} elements from {1}".format(
                len(self._twtable), filename))

    def _save_hdf5_v2(self, filename, group = "Twiss"):
        # data type
        dt = np.dtype( [ 
            ('element', h5py.special_dtype(vlen=bytes)),
            ('s',      np.float64),
            ('alphax', np.float64),
            ('alphay', np.float64),
            ('betax',  np.float64),
            ('betay',  np.float64),
            ('gammax', np.float64),
            ('gammay', np.float64),
            ('etax',   np.float64),
            ('etay',   np.float64),
            ('phix',   np.float64),
            ('phiy',   np.float64),
            ] )

        data = np.ndarray((len(self.element),), dtype=dt)
        data['element'] = self.element
        for i,k in enumerate(self._cols):
            data[k] = self._twtable[:,i]

        f = h5py.File(filename)
        grp = f.create_group(group)
        grp['twtable'] = data
        grp['tune'] = np.array(self.tune)
        grp['chrom'] = np.array(self.chrom)
        grp['alphac'] = self.alphac
        f.close()

    def _load_sqlite3(self, fname, table="Twiss"):
        """read twiss from sqlite db file."""
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


def _updateLatticePvDb(dbfname, cfslist, sep=";"):
    """
    update sqlite3 DB with a list of (pv, properties, tags)

    It only updates common columns of DB table and cfslist.

    Constraints:

    - elemName is unique
    - (pv,elemName,elemField) is unique
    - elemType can not be NULL
    """
    # elemName, elemType, system is "NOT NULL"
    conn = sqlite3.connect(dbfname)
    # save byte string instead of the default unicode
    conn.text_factory = str
    c = conn.cursor()
    # elements need to insert
    elem_sets, pv_sets = [], []
    for i,rec in enumerate(cfslist):
        pv, prpts, tags = rec
        ukey = (prpts.get("elemName", ""),
                prpts.get("elemType", ""))
        # skip if already in the to-be-inserted list
        # elemName has to be unique
        if ukey[0] in [v[0] for v in elem_sets]: continue
        c.execute("""SELECT * from elements where elemName=?""", (ukey[0],))
        # no need to insert if exists
        if len(c.fetchall()) > 0: continue
        elem_sets.append(ukey)
        #new pvs
        ukey = (pv, prpts.get("elemName", ""), prpts.get("elemField", ""))
        if ukey in pv_sets: continue
        pv_sets.append(ukey)

    c.executemany("""INSERT INTO elements (elemName,elemType) VALUES (?,?)""",
                  elem_sets)
    # insert or replace pv
    c.executemany("""INSERT INTO pvs (pv,elemName,elemField) VALUES (?,?,?)""",
                  pv_sets)
    conn.commit()

    c.execute("PRAGMA table_info(elements)")
    tbl_elements_cols = [v[1] for v in c.fetchall()]
    for col in tbl_elements_cols:
        if col in ["elemName"]: continue
        vals = []
        for i,rec in enumerate(cfslist):
            pv, prpts, tags = rec
            if col not in prpts: continue
            vals.append((prpts[col], prpts["elemName"]))
        if len(vals) == 0: continue
        try:
            c.executemany("UPDATE elements set %s=? where elemName=?" % col,
                          vals)
        except:
            print "Error at updating {0} {1}".format(col, vals)
            raise

        conn.commit()

    c.execute("PRAGMA table_info(pvs)")
    tbl_pvs_cols = [v[1] for v in c.fetchall()]
    for col in tbl_pvs_cols:
        if col in ['pv', 'elemName', 'elemField', 'tags']:
            continue
        vals = []
        for i,rec in enumerate(cfslist):
            pv, prpts, tags = rec
            if col not in prpts: continue
            if not prpts.has_key("elemField") or not prpts.has_key("elemName"):
                print "Incomplete record for pv={0}: {1} {2}".format(
                    pv, prpts, tags)
                continue
            # elemGroups is a list
            vals.append((prpts[col], pv, prpts["elemName"], prpts["elemField"]))

        if len(vals) == 0: continue
        c.executemany("""UPDATE pvs set %s=? where pv=? and """
                      """elemName=? and elemField=?""" % col,
                      vals)
        conn.commit()

    # update tags
    vals = []
    for i,rec in enumerate(cfslist):
        pv, prpts, tags = rec
        if not tags: continue
        if not prpts.has_key("elemField") or not prpts.has_key("elemName"):
            print "Incomplete record for pv={0}: {1} {2}".format(
                pv, prpts, tags)
            continue
        vals.append((sep.join(sorted(tags)),
                     pv, prpts["elemName"], prpts["elemField"]))
    if len(vals) > 0: 
        c.executemany("""UPDATE pvs set tags=? where pv=? and """
                      """elemName=? and elemField=?""", vals)
        conn.commit()

    msg = "[%s] updated %d records" % (__name__, len(cfslist))
    c.execute("""insert into info(timestamp,name,value)
                 values (datetime('now'), "log", ? )""", (msg,))
    conn.commit()
    conn.close()


def createLatticePvDb(dbfname, csv2fname = None):
    """
    create a new sqlite3 DB. remove if same file exists.

    - elemName is unique
    - (pv,elemName,elemField) is unique
    - elemType can not be NULL
    """
    #if os.path.exists(dbfname): os.remove(dbfname)
    conn = sqlite3.connect(dbfname)
    c = conn.cursor()
    c.execute("""DROP TABLE IF EXISTS info""")
    c.execute("""DROP TABLE IF EXISTS elements""")
    c.execute("""DROP TABLE IF EXISTS pvs""")
    c.execute("""CREATE TABLE info
                 (id INTEGER PRIMARY KEY, timestamp TEXT NOT NULL,
                  name TEXT NOT NULL, value TEXT)""")
    msg = "[%s] tables created" % (__name__,)
    c.execute("""insert into info(timestamp,name,value)
                 values (datetime('now'), "log", ?)""", (msg,))
    c.execute("""CREATE TABLE elements
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  elemName TEXT UNIQUE,
                  elemType TEXT NOT NULL,
                  cell     TEXT,
                  girder   TEXT,
                  symmetry TEXT,
                  elemLength   REAL,
                  elemPosition REAL,
                  elemIndex    INTEGER,
                  elemGroups   TEXT,
                  k1           REAL,
                  k2           REAL,
                  angle        REAL,
                  fieldPolar   INTEGER,
                  virtual      INTEGER DEFAULT 0)""")
    conn.commit()

    c.execute("""CREATE TABLE pvs
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  pv TEXT,
                  elemName   TEXT,
                  elemHandle TEXT,
                  elemField  TEXT,
                  hostName   TEXT,
                  devName    TEXT,
                  iocName    TEXT,
                  tags       TEXT,
                  hlaHigh   REAL,
                  hlaLow    REAL,
                  hlaValRef REAL,
                  UNIQUE (pv,elemName,elemField) ON CONFLICT REPLACE,
                  FOREIGN KEY(elemName) REFERENCES elements(elemName))""")
    conn.commit()
    conn.close()
    if csv2fname is not None: updateLatticePvDb(dbfname, csv2fname)


def saveSnapshotH5(fname, dscalar, dvector):
    N1 = max([len(v[0]) for v in dscalar])
    N2 = max([len(v[1]) for v in dscalar])
    dt = np.dtype([('element', "S%d" % N1),
                   ('field', "S%d" % N2), ("value", 'd')])
    d = np.array(dscalar, dtype=dt)
    f = h5py.File(fname, 'w')
    grp = f.create_group("scalar")
    grp["data"] = d
    grp = f.create_group("waveform")
    for v in dvector:
        grp["%s.%s" % (v[0], v[1])] = v[2]
    f.close()
    pass


if __name__ == "__main__":
    createLatticePvDb('test.sqlite', '/home/lyyang/devel/nsls2-hla/aphla/machines/nsls2/BR-20130123-Diag.txt')
    updateLatticePvDb('test.sqlite', '/home/lyyang/devel/nsls2-hla/aphla/machines/nsls2/BR-20130123-Diag.txt')
