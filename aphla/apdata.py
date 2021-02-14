#!/usr/bin/env python
from __future__ import print_function, division, absolute_import
from six import string_types

"""
:author: Lingyun Yang <lyyang@bnl.gov>
:license:

"""

import os
from os.path import splitext
from fnmatch import fnmatch
import numpy as np
import shelve
import h5py
import sqlite3

import warnings

import logging
_logger = logging.getLogger("aphla.apdata")
#_logger.setLevel(logging.DEBUG)

__all__ = ['OrmData', 'TwissData', 'saveSnapshotH5']

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

    The private dataset has a prefix "_" in its name."""

    def __init__(self, datafile = None, group = None):
        # list of tuple, (name, location, plane)
        self.bpm = []
        self.cor = []

        # optional PV info, EPICS only
        self.bpm_pv = None
        self.cor_pvrb = None
        self.cor_pv = None

        # 3d raw data
        self._mask = None
        self.m = None

        if datafile is not None and group is not None:
            self.load(datafile, group = group)
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
        name, plane = zip(*self.bpm)
        name = [v.encode('ascii') for v in name]
        dst.attrs["bpm_name"] = name
        dst.attrs["bpm_field"] = plane
        name, plane = zip(*self.cor)
        dst.attrs["cor_name"] = name
        dst.attrs["cor_field"] = plane
        if self.bpm_pv:
            dst.attrs["bpm_pv"] = self.bpm_pv
        if self.cor_pv:
            dst.attrs["cor_pv"] = self.cor_pv
        if self.cor_pvrb:
            dst.attrs["cor_pvrb"] = self.cor_pvrb

        f.close()

    def _load_hdf5(self, filename, group = "OrbitResponseMatrix"):
        """
        load data group *grp* from hdf5 file *filename*
        """
        f = h5py.File(filename, 'r')
        if group not in f:
            _logger.warn("No '%s' group in '%s'. Ignore." % (group, filename))
            return

        g = f[group]
        self.bpm = list(zip(g["m"].attrs["bpm_name"].astype(str),
                            g["m"].attrs["bpm_field"].astype(str)))
        self.bpm_pv = g["m"].attrs.get("bpm_pv", None)
        self.cor = list(zip(g["m"].attrs["cor_name"].astype(str),
                            g["m"].attrs["cor_field"].astype(str)))
        self.cor_pv = g["m"].attrs.get("cor_pv", None)
        self.cor_pvrb = None
        nbpm, ncor = len(self.bpm), len(self.cor)
        self.m = np.zeros((nbpm, ncor), 'd')
        self.m[:,:] = g['m'][:,:]
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
        else:
            raise ValueError("not supported file format: %s" % format)

    def load(self, filename, **kwargs):
        """
        load orm data from binary file
        """
        if not os.path.exists(filename):
            raise ValueError("ORM data %s does not exist" % filename)

        fmt = kwargs.get("format", None)
        if fmt == 'HDF5' or filename.endswith(".hdf5"):
            self._load_hdf5(filename, **kwargs)
        else:
            raise ValueError("format %s is not supported" % format)

    def getBpm(self):
        """The BPM names of ORM.

        It has same order as appeared in orm rows. For a full matrix with
        coupling terms, the result may have duplicate bpm names in the return
        list.
        """
        return [(v[0], v[1]) for v in self.bpm]

    def has(self, name, field):
        """check if the bpm is used in this ORM measurement"""

        for bpm,fld in self.bpm:
            if bpm == name and fld == field: return True
        for cor,fld in self.cor:
            if cor == name and fld == field: return True
        return False

    def getCor(self):
        """a list of corrector names.

        The same order as appeared in orm columns. For a full matrix with
        coupling terms, it may have duplicate trim names in the return list.
        """
        return [(v[0], v[1]) for v in self.cor]

    def maskCrossTerms(self):
        """mask the H/V and V/H terms.

        If the coupling between horizontal/vertical kick and
        vertical/horizontal BPM readings, it's reasonable to mask out
        these coupling terms.
        """

        for i,(bpm,bfld) in enumerate(self.bpm):
            for j,(cor,cfld) in enumerate(self.trim):
                # b[1] = ['X'|'Y'], similar for t[1]
                if bfld != cfld: self._mask[i,j] = 1

    def index(self, elem, field):
        """return the index for given (element, fields).

        Raise ValueError if does not exist.

        Examples
        ---------
        >>> index('BPM1', 'x')
        >>> index('TRIM1', 'y')

        """
        for i,b in enumerate(self.bpm):
            if b[0] == elem and b[1] == field: return i
        for i,t in enumerate(self.cor):
            if t[0] == elem and t[1] == field: return i

        raise ValueError("(%s,%s) are not in this ORM data" % (elem, field))


    def get(self, bpmr, corr):
        """get the matrix element by bpm/trim name and field

        Examples
        ---------
        >>> get(('bpm1', 'x'), ('corr1', 'x'))

        """
        i = self.index(bpmr[0], bpmr[1])
        j = self.index(corr[0], corr[1])

        if self._mask and self._mask[i,j]: return None
        return self.m[i, j]

    def update(self, bpmr, corr, val):
        i = self.index(bpmr[0], bpmr[1])
        j = self.index(corr[0], corr[1])

        self.m[i,j] = val

    def disable(self, bpmr, corr):
        i = self.index(bpmr[0], bpmr[1])
        j = self.index(corr[0], corr[1])
        self._mask[i,j] = 1

    def enable(self, bpmr, corr):
        i = self.index(bpmr[0], bpmr[1])
        j = self.index(corr[0], corr[1])
        self._mask[i,j] = 0


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
        self.tune   = None #(0.0, 0.0)
        self.chrom  = None #(0.0, 0.0)
        self.alphac = None #0.0
        self.epsx0 = None # Natural horizontal emittance [m-rad]
        self.Jx = self.Jy = self.Jdelta = None # Damping partitions
        self.taux = self.tauy = self.taudelta = None # Damping times [s]
        self.U0_MeV = None # Energy loss per turn
        self.sigma_delta = None # Energy spread
        self.element = []
        self._twtable = []
        self._cols = ['s', 'alphax', 'alphay', 'betax', 'betay',
                      'etax', 'etaxp', 'etay', 'etayp', 'phix', 'phiy']
        self._cols_units = ['m', 'unitless', 'unitless', 'm', 'm',
                            'm', 'unitless', 'm', 'unitless', 'rad', 'rad']
        # ^ Units following ELEGANT's Twiss SDDS output files

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
        elif isinstance(key, string_types):
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

    def at(self, s, col, **kwargs):
        """
        get twiss at a location `s`. Linear interpolation.
        """
        if s < self._twtable[0,0] or s > self._twtable[-1,0]:
            raise ValueError("s={} is outside of range ({}, {})".format(
                    s, self._twtable[0,0], self._twtable[-1,0]))
        dat = []
        for i in range(1, len(self._twtable)):
            if self._twtable[i,0] < s: continue
            for c in col:
                if c in self._cols:
                    j = self._cols.index(c)
                    x0, x1 = self._twtable[i-1:i+1, j]
                    fc = (s - self._twtable[i-1,0]) / \
                        (self._twtable[i,0] - self._twtable[i-1,0])
                    dat.append(x0 + (x1-x0)*fc)
                else:
                    dat.append(None)
            break
        return dat

    def get(self, names, col, **kwargs):
        """get a list of twiss functions when given a name pattern or a list of
        element names.

        Parameters
        -----------
        names : list, str
            name pattern or list of elements.
        col : list.
            columns can be 's', 'betax', 'betay', 'alphax', 'alphay', 'phix',
            'phiy', 'etax', 'etaxp', 'etay', 'etayp'.

        Examples
        ---------
        >>> getTwiss(['E1', 'E2'], col=('s', 'betax', 'betay'))

        Note: this matches the line of twiss data record for name and twiss
        data. Depend on the initial configured data, most likely the data is
        at the end of element. Use :func:`at`
        """
        elemlst = names
        if isinstance(names, str):
            ret = []
            for i,e in enumerate(self.element):
                if not fnmatch(e, names): continue
                dat = []
                for c in col:
                    if c in self._cols:
                        j = self._cols.index(c)
                        dat.append(self._twtable[i,j])
                    else:
                        raise ValueError("column '%s' is not in twiss data" % c)
                ret.append(dat)
            return np.array(ret, 'd')

        return self._get_elems(elemlst, col, **kwargs)


    def _get_elems(self, elemlst, col, **kwargs):
        """get a list of twiss functions when given a list of element names.

        Parameters
        -----------
        elemlst : list.
            names of elements.
        col : list.
            columns can be 's', 'betax', 'betay', 'alphax', 'alphay', 'phix',
            'phiy', 'etax', 'etaxp', 'etay', 'etayp'.

        Examples
        ---------
        >>> getTwiss(['E1', 'E2'], col=('s', 'betax', 'betay'))

        Note: this matches the line of twiss data record for name and twiss
        data. Depend on the initial configured data, most likely the data is
        at the end of element. Use :func:`at`
        """
        if not col: return None
        clean = kwargs.get('clean', False)

        # check if element is valid
        ret = []
        for e in elemlst:
            try:
                i = self.element.index(e)
            except:
                raise ValueError("element '{0}' is not in twiss "
                                 "data: {1}".format(e, self.element))
            dat = []
            for c in col:
                if c in self._cols:
                    j = self._cols.index(c)
                    dat.append(self._twtable[i,j])
                else:
                    raise ValueError("column '%s' is not in twiss data" % c)
            ret.append(dat)

        return np.array(ret, 'd')


    def load(self, filename, **kwargs):
        """loading hdf5 file in a group default 'Twiss'"""
        if filename.endswith(".hdf5") or filename.endswith(".h5"):
            self._load_hdf5_v2(filename, **kwargs)
        elif filename.endswith(".txt"):
            self._load_txt(filename)

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

    def _load_txt(self, filename):
        """
        load the Twiss data in txt format:

        ::

          Tune: 0.0 0.0
          Chrom: 0.0 0.0
          Alpha_c: 0.0
          element s alphax alphay betax betay etax etaxp etay etayp phix phiy
          BPM1 0.0 0.0 ....
        """

        f = open(filename, 'r')
        self.tune = tuple([float(v) for v in f.readline().split()[1:3]])
        self.chrom = tuple([float(v) for v in f.readline().split()[1:3]])
        self.alphac = float(f.readline().split()[1])

        # check columns
        cols = tuple([v.strip() for v in f.readline().split()])
        #print cols

        for i,s in enumerate(f):
            data = s.split()
            self._twtable.append([None for c in self._cols])
            #print i, s, data
            for j,c in enumerate(cols):
                #print j, c
                if c == "element":
                    self.element.append(data[j])
                elif c in self._cols:
                    k = self._cols.index(c)
                    self._twtable[-1][k] = float(data[j])
                #else:
                #    raise RuntimeError("can not find '%s'" % c)

            #print self._twtable[-1]
        #self._twtable = np.array(self._twtable, 'd')
        f.close()


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
        self.element = [s.decode() if hasattr(s, 'decode') else s
                        for s in grp['twtable']['element'][()]]
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
            ('etax',   np.float64),
            ('etaxp',  np.float64),
            ('etay',   np.float64),
            ('etayp',  np.float64),
            ('phix',   np.float64),
            ('phiy',   np.float64),
            ] )

        data = np.ndarray((len(self.element),), dtype=dt)
        data['element'] = self.element
        for i,k in enumerate(self._cols):
            data[k] = [v[i] for v in self._twtable]

        f = h5py.File(filename, 'a')
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

    def getUnit(self, col_name):
        """"""

        if col_name not in self._cols:
            print('Valid column names: {}'.format(', '.join([n for n in self._cols])))
            raise ValueError(f'Invalid name: "{col_name}"')

        i = self._cols.index(col_name)

        return self._cols_units[i]

def _updateLatticePvDb(dbfname, cfslist, **kwargs):
    """
    update(or add new) sqlite3 DB with a list of (pv, properties, tags)

    dbfname : str
    cflist : list of (pv, properties, tags)
    sep : str. ";". separate single string to a list.
    quiet : False. do not insert a log entry.

    It only updates columns which are in both DB table and cfslist. The
    existing data will be updated and new data will be added.

    Ignore the tags if it is None.

    Constraints:

    - elemName is unique
    - (pv,elemName,elemField) is unique
    - elemType can not be NULL

    if pv is false, the pv part is not updated. Same as elemName part.
    """

    sep   = kwargs.get("sep", ";")
    quiet = kwargs.get("quiet", False)

    # elemName, elemType, system is "NOT NULL"
    conn = sqlite3.connect(dbfname)
    # save byte string instead of the default unicode
    conn.text_factory = str
    c = conn.cursor()

    # new elements and pvs need to insert
    elem_sets, pv_sets = [], []
    for i,rec in enumerate(cfslist):
        pv, prpts, tags = rec
        ukey = (prpts.get("elemName", ""),
                prpts.get("elemType", ""))
        # skip if already in the to-be-inserted list
        # elemName has to be unique
        if ukey[0] and ukey[0] not in [v[0] for v in elem_sets]:
            c.execute("""SELECT * from elements where elemName=?""", (ukey[0],))
            # no need to insert if exists
            if len(c.fetchall()) == 0:
                elem_sets.append(ukey)
        # same as elemName, find the new pvs
        ukey = (pv, prpts.get("elemName", ""), prpts.get("elemField", ""))
        if pv and ukey not in pv_sets:
            c.execute("""SELECT * from pvs where """
                      """pv=? and elemName=? and elemField=?""",
                      ukey)
            if len(c.fetchall()) == 0:
                pv_sets.append(ukey)

    for elem in elem_sets:
        _logger.debug("adding new element: {0}".format(elem))
    c.executemany("""INSERT INTO elements (elemName,elemType) VALUES (?,?)""",
                  elem_sets)
    _logger.debug("added {0} elements".format(len(elem_sets)))

    for pv in pv_sets:
        _logger.debug("adding new pv: {0}".format(pv))
    c.executemany("""INSERT INTO pvs (pv,elemName,elemField) VALUES (?,?,?)""",
                  pv_sets)
    _logger.debug("added {0} pvs".format(len(pv_sets)))
    conn.commit()

    c.execute("PRAGMA table_info(elements)")
    tbl_elements_cols = [v[1] for v in c.fetchall()]
    # update the elements table if cfslist has the same column
    for col in tbl_elements_cols:
        if col in ["elemName"]: continue
        vals = []
        for i,rec in enumerate(cfslist):
            pv, prpts, tags = rec
            if col not in prpts: continue
            vals.append((prpts[col], prpts["elemName"]))
        if len(vals) == 0:
            _logger.debug("elements: no data for column '{0}'".format(col))
            continue
        try:
            c.executemany("UPDATE elements set %s=? where elemName=?" % col,
                          vals)
        except:
            print("Error at updating {0} {1}".format(col, vals))
            raise

        conn.commit()
        _logger.debug("elements: updated column '{0}' with {1} records".format(
                col, len(vals)))

    c.execute("PRAGMA table_info(pvs)")
    tbl_pvs_cols = [v[1] for v in c.fetchall()]
    for col in tbl_pvs_cols:
        if col in ['pv', 'elemName', 'elemField', 'tags']:
            continue
        vals = []
        for i,rec in enumerate(cfslist):
            pv, prpts, tags = rec
            if col not in prpts: continue
            if ("elemField" not in prpts) or ("elemName" not in prpts):
                print("Incomplete record for pv={0}: {1} {2}".format(
                    pv, prpts, tags))
                continue
            # elemGroups is a list
            vals.append((prpts[col], pv, prpts["elemName"], prpts["elemField"]))

        if len(vals) == 0:
            _logger.debug("pvs: no data for column '{0}'".format(col))
            continue
        c.executemany("""UPDATE pvs set %s=? where pv=? and """
                      """elemName=? and elemField=?""" % col,
                      vals)
        conn.commit()
        _logger.debug("pvs: updated column '{0}' with {1} records '{2}'".format(
                col, len(vals), [v[0] for v in vals]))

    # update tags
    vals = []
    for i,rec in enumerate(cfslist):
        pv, prpts, tags = rec
        if tags is None: continue
        if "elemField" not in prpts or "elemName" not in prpts:
            print("Incomplete record for pv={0}: {1} {2}. IGNORED".format(
                pv, prpts, tags))
            continue
        vals.append((sep.join(sorted(tags)),
                     pv, prpts["elemName"], prpts["elemField"]))
    if len(vals) > 0:
        c.executemany("""UPDATE pvs set tags=? where pv=? and """
                      """elemName=? and elemField=?""", vals)
        conn.commit()
        _logger.debug("pvs: updated tags for {0} rows".format(len(vals)))

    if not quiet:
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
                  speed       REAL,
                  hlaHigh     REAL,
                  hlaLow      REAL,
                  hlaStepsize REAL,
                  hlaValRef   REAL,
                  archive INT DEFAULT 0,
                  size    INT DEFAULT 0,
                  epsilon REAL DEFAULT 0.0,
                  UNIQUE (pv,elemName,elemField) ON CONFLICT REPLACE,
                  FOREIGN KEY(elemName) REFERENCES elements(elemName))""")
    conn.commit()
    conn.close()
    if csv2fname is not None: updateLatticePvDb(dbfname, csv2fname)


def updateDbElement(dbfname, submachine, element, **kwargs):
    """
    add or update element in the DB

    dbfname : str. SQLite3 database file name
    submachine : str, e.g. "SR"
    element : str, element name in lattice
    elemType : str
    cell : str
    girder : str
    symmetry : str
    elemLength : float
    elemPosition : float
    elemIndex : int
    elemGroups : str. separated by ";"
    virtual : int.
    tags : list of str.
    """
    kw = {"elemName": element}
    for k in ["elemType", "cell", "girder", "symmetry",
              "elemLength", "elemPosition", "elemIndex", "elemGroups",
              "virtual"]:
        if k not in kwargs or kwargs[k] is None: continue
        kw[k] = kwargs.pop(k)

    _updateLatticePvDb(dbfname, [("", kw, None), ], **kwargs)


def updateDbPv(dbfname, pv, element, field, **kwargs):
    """
    """
    kw = {"elemName": element, "elemField": field}
    tags = kwargs.get("tags", None)
    for k in ["elemHandle", "hostName", "devName", "iocName",
              "speed", "hlaHigh", "hlaLow", "hlaStepsize", "hlaValRef",
              "archive", "size", "epsilon"]:
        if k not in kwargs or kwargs[k] is None: continue
        kw[k] = kwargs.pop(k)

    _updateLatticePvDb(dbfname, [(pv, kw, tags), ], **kwargs)


def saveSnapshotH5(fname, dscalar, dvector):
    """
    save machine snapshot data as HDF5.

    - dscalar : (name, field, value) scalar data
    - dvector : (name, field, value) waveform data

    All scalar data is in one dataset, each waveform is in one dataset.
    """
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


#if __name__ == "__main__":
#    createLatticePvDb('test.sqlite', '/home/lyyang/devel/nsls2-hla/aphla/machines/nsls2/BR-20130123-Diag.txt')
#    updateLatticePvDb('test.sqlite', '/home/lyyang/devel/nsls2-hla/aphla/machines/nsls2/BR-20130123-Diag.txt')

if __name__ == "__main__":
    #m = OrmData("machines/nsls2v2/v2sr.hdf5", "OrbitResponseMatrix")
    #m._save_hdf5("test_orm.hdf5", "OrbitResponseMatrix")
    m = OrmData("test_orm.hdf5", "OrbitResponseMatrix")
    print(m.getBpmNames())
    print(m.has('ph2g6c21b', 'x'))

