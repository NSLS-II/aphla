from __future__ import print_function, division, absolute_import

"""
Unit Conversion
----------------
"""

# :author: Lingyun Yang <lyyang@bnl.gov>

from collections import Iterable
import logging
import re
import os
from pathlib import Path
import pickle

import numpy as np

_logger = logging.getLogger("aphla.unitconv")
#_logger.setLevel(logging.DEBUG)

class UcAbstract(object):
    """an identity conversion with unit names.

    - *direction*, i.e. (src, dst) from src unit, to dst unit.
    - *invertible*, in case of linear, has both f(x) and f^{-1}(y).

    This src, dst are unit name, e.g. Tesla, T-m. They are helpful for
    display, but not essential for unit conversion.  They are not unit system
    names. Unit system is a concept in higher level managed by element (and
    action)

    See CaElement and CaAction for unit system.
    """
    def __init__(self, src, dst):
        self.direction = (src, dst)
        self.srcunit = src
        self.dstunit = dst
        self.polarity = 1
        self.invertible = 0

    def __str__(self):
        src, dst = self.direction[0], self.direction[1]
        return "%s -> %s: identity" % (src, dst)

    def eval(self, x, inv = False):
        if isinstance(x, Iterable):
            return [self.polarity * v for v in x]
        return self.polarity*x

class UcPoly(UcAbstract):
    """
    a polynomial unit conversion. It is invertible if order=1.

    """
    def __init__(self, src, dst, coef):
        super(UcPoly, self).__init__(src, dst)
        self.p = np.poly1d(coef)
        if len(coef) == 2:
            self.invertible = 1

    def __str__(self):
        src, dst = self.direction[0], self.direction[1]
        return "%s -> %s: %s" % (src, dst, str(self.p))

    def _inv_eval(self, x):
        """evaluate the inverse"""
        if not self.invertible:
            raise RuntimeError("inverse is not permitted for (%s -> %s)" %
                               self.direction)
        if self.p.order == 1:
            # y = ax + b
            # x = 1/a * y - b/a
            a, b = self.p.coeffs
            ar, br = 1.0/a, -b*1.0/a
            if isinstance(x, Iterable):
                # keep None to None
                return [(ar*self.polarity*v + br)
                        if v is not None else None for v in x]
            else:
                return (ar*self.polarity*x + br)
        elif self.p.order == 0:
            raise RuntimeError("can not inverse a constant for (%s -> %s)" %
                               self.direction)
        else:
            raise RuntimeError("can not inverse polynomial order > 2 "
                               "for (%s -> %s)" % self.direction)

    def eval(self, x, inv = False):
        if x is None: return None

        if inv: return self._inv_eval(x)

        if isinstance(x, Iterable):
            return [self.polarity * self.p(v)
                    if v is not None else None for v in x]
        else:
            return self.polarity * self.p(x)

class UcInterp1(UcAbstract):
    """linear interpolation"""
    def __init__(self, src, dst, x, y):
        super(UcInterp1, self).__init__(src, dst)
        #self.f = np.interpolate.interp1d(x, y)
        # has to be increasing for linear interpolation
        self.xp, self.fp = x, y
        self._fp_r, self._xp_r = None, None
        if not np.all(np.diff(self.xp) > 0):
            raise RuntimeErorr("increasing data are needed for interpolation")
        if np.all(np.diff(self.fp) > 0):
            # fp increasing
            self.invertible = 1
            self._xp_r = [v for v in self.fp]
            self._fp_r = [v for v in self.xp]
        elif np.all(np.diff(self.fp) < 0):
            self.invertible = 1
            self._xp_r = [v for v in reversed(self.fp)]
            self._fp_r = [v for v in reversed(self.xp)]
        else:
            self.invertible = 0

    def _inv_eval(self, x):
        if x is None: return None
        # interp returns boundary if x is outside of fp
        return np.interp(self.polarity*x, self._xp_r, self._fp_r,
                         left=-np.inf, right=np.inf)

    def eval(self, x, inv = False):
        if inv:
            if not self.invertible: return None
            else:
                return self._inv_eval(x)
        #
        if x is None: return None
        # interp returns boundary if x is outside of xp
        return self.polarity*np.interp(x, self.xp, self.fp,
                                       left=-np.inf, right=np.inf)

class _UcInterpN(UcAbstract):
    """n-D linear interpolation"""
    def __init__(self, src, dst, x, y):
        """
        :param x: a list of x-data for interpolation
        :param y: a list of y-data for interpolation

        x[i] and y[i] are a list of measurement.
        """
        super(UcInterpN, self).__init__(src, dst)
        self.xp, self.fp = x, y

    def eval(self, x, inv = False):
        """if None, returns None"""
        if inv: raise RuntimeError("inverse not supported for (%s -> %s)" %
                                   self.direction)

        if not isinstance(x, Iterable):
            raise RuntimeError("expecting an iterable input")
        ret = []
        for i,v in enumerate(x):
            if x is None or x < self.xp[i][0] or x > self.xp[i][-1]:
                ret.append(None)
            else:
                ret.append(np.interp(x[i], self.xp[i], self.fp[i]))
        return ret


def loadUnitConversionYaml(lat, yaml_file):
    """set the unit conversion for lattice with input from yaml file and its
    associated pickle file that contains interpolation tables """

    _logger.info(f"setting unit conversion for lattice {lat.name} "
                 f"from data file '{yaml_file}'")

    from ruamel import yaml

    y = yaml.YAML(typ='safe').load(Path(yaml_file).read_text())

    if 'table_filepath' in y:

        table_filepath = Path(y['table_filepath'])
        if not table_filepath.exists():
            table_filepath = Path(yaml_file).parent.joinpath(table_filepath)
            if not table_filepath.exists():
                raise FileNotFoundError(
                    f"Unit conversion table file \"{y['table_filepath']}\"")

        with open(table_filepath, 'rb') as f:
            all_tables = pickle.load(f)
        tables = all_tables[lat.name]
    else:
        tables = None

    db = y[lat.name]

    for k, v in db.items():

        # None is the unit for lower level(epics) data
        usrcsys = v['src_unitsys']
        udstsys = v['dst_unitsys']

        usrc = v['src_unit']
        udst = v['dst_unit']

        # Calibration factor
        yfac = v.get('calib_factor', 1.0)

        if v['class'] == 'polynomial':
            a = [yfac**i for i in range(len(v['coeffs']))]
            a.reverse() # in place
            newp = [v['coeffs'][i]*c for i,c in enumerate(a)]
            uc = UcPoly(usrc, udst, newp)
        elif v['class'] == 'interpolation':
            t = tables[v['table_key']]
            uc = UcInterp1(usrc, udst, t[:,0], t[:,1] * yfac)
        elif v['class'] == 'composite':
            raise NotImplementedError
        else:
            raise RuntimeError("Unknown unit converter")

        uc.polarity = v.get('polarity', 1)
        uc.invertible = int(v.get('invertible', True))

        uhandles = v.get('handles', ['readback', 'setpoint'])

        # find the "elements" list
        elems = v.get('elements', [])

        eobjs = []
        for ename in elems:
            eobj = lat._find_exact_element(ename)
            if not eobj:
                _logger.warn(f"dataset '{k}': element {lat.name}.{ename} not found. ignored")
                continue
            eobjs.append(eobj)

        fams = v.get('groups', [])
        for fam in fams:
            egrps = lat.getElementList(fam)
            if not egrps:
                _logger.warn(f"dataset '{k}': group {lat.name}.{fam} not found. ignored")
            eobjs += egrps

        _logger.info(
            f"unitconversion data {usrcsys}[{usrc}] -> {udstsys}[{udst}] "
            f"for elems={elems}, fams={fams}")
        _logger.info(
            f"unitconversion will be updated for {[e.name for e in eobjs]}")
        _logger.info(f"used calibration factor {yfac}")

        for eobj in eobjs:
            for fld in v.get('fields', []):
                if fld not in eobj.fields():
                    realfld = v.get('rawfield', None)
                    if realfld is None:
                        _logger.warn(f"'{lat.name}.{eobj.name}' has no field '{fld}' for unit conversion")
                        continue
                    else:
                        eobj.addAliasField(fld, realfld)

                _logger.info(
                    f"adding unit conversion for {eobj.name}.{fld}, "
                    f"from {usrcsys}[{usrc}] to {udstsys}[{udst}] handles={uhandles}")
                for handle in uhandles:
                    eobj.addUnitConversion(fld, uc, usrcsys, udstsys, handle=handle)

    # For each element, create a unit conversion function for each field/handle/(src,dst)
    for e in lat.getElementList('*'):
        for fld in list(e.fields()):
            e.addUnitConversionFuncs(fld)

def identity(x):
    """"""

    return x

def recursive_eval(uc, src_dst_inv_list, x):
    """"""

    y = x
    for (src, dst), inv in src_dst_inv_list:
        y = uc[(src, dst)].eval(y, inv=inv)

    return y

def loadUnitConversionH5(lat, h5file, group):
    """set the unit conversion for lattice with input from hdf5 file"""

    _logger.info("setting unit conversion for lattice {0} "
                 "from data file '{1}': '{2}'".format(
                     lat.name, h5file, group))

    import h5py
    g = h5py.File(h5file, 'r')
    if group: g = g[group]

    for k,v in g.items():
        #if not v.attrs.get('_class_', None): continue

        # use separated three attrs first, otherwise, use 'unitsys' attr.
        fld = v.attrs.get('field', None)
        if not fld:
            continue
        else:
            fld = fld.decode()

        usrcsys = v.attrs.get('src_unit_sys', b'').decode()
        udstsys = v.attrs.get('dst_unit_sys', b'').decode()
        #if fld is None:
        #    fld, usrcsys, udstsys = v.attrs.get('unitsys', ",,").split(',')

        # instead of '', None is the unit for lower level(epics) data
        if usrcsys == '': usrcsys = None
        if udstsys == '': udstsys = None
        # the unit name, e.g., A, T/m, ...
        # check src_unit/dst_unit first, then direction as a backup
        usrc = v.attrs.get('src_unit', b'').decode()
        udst = v.attrs.get('dst_unit', b'').decode()

        # the calibration factor
        yfac = v.attrs.get('calib_factor', 1.0)
        if v.attrs['_class_'].decode() == 'polynomial':
            a = [yfac**i for i in range(len(v))]
            a.reverse() # in place
            newp = [v[i]*c for i,c in enumerate(a)]
            uc = UcPoly(usrc, udst, newp)
        elif v.attrs['_class_'].decode() == 'interpolation':
            uc = UcInterp1(usrc, udst, list(v[:,0]), list(v[:,1]*yfac))
        else:
            raise RuntimeError("unknow unit converter")

        # integer - invertible
        uc.polarity   = v.attrs.get('polarity', 1)
        uhandles = [_s.decode() for _s in v.attrs.get('handle', [b"readback", b"setpoint"])]

        # find the element list
        elems = [_s.decode() for _s in v.attrs.get('elements', [])]

        eobjs = []
        #lat._find_exact_element(ename) for ename in elems if lat.hasElement(ename)]
        for ename in elems:
            eobj = lat._find_exact_element(ename)
            if not eobj:
                _logger.warn("dataset '{0}': element {1}.{2} not found. ignored".format(
                    k, lat.name, ename))
                continue
            eobjs.append(eobj)

        fams = [fam.decode() for fam in v.attrs.get('groups', [])]
        for fam in fams:
            egrps = lat.getElementList(fam)
            if not egrps:
                _logger.warn("dataset '{0}': group {1}.{2} not found. ignored".format(
                    k, lat.name, fam))
            eobjs += egrps

        _logger.info("unitconversion data {0}[{1}] -> {2}[{3}] for elems={4}, "
                     "fams={5}".format(
                usrcsys, usrc, udstsys, udst, elems, fams))
        _logger.info("unitconversion will be updated for {0}".format(
                [e.name for e in eobjs]))
        _logger.info("used calibration factor {0}".format(yfac))

        for eobj in eobjs:
            if fld not in eobj.fields():
                realfld = v.attrs.get('rawfield', None)
                if realfld is None:
                    _logger.warn("'%s.%s' has no field '%s' for unit conversion" \
                                     % (lat.name, eobj.name, fld))
                    continue
                else:
                    eobj.addAliasField(fld, realfld.decode())

            _logger.info("adding unit conversion for {0}.{1}, "
                         "from {2}[{3}] to {4}[{5}] handles={6}".format(
                             eobj.name, fld, usrcsys, usrc, udstsys, udst,
                             uhandles))
            for handle in uhandles:
                eobj.addUnitConversion(fld, uc, usrcsys, udstsys, handle=handle)

def loadUnitConversionIni(lat, fname):
    """load the unit conversion for lattice from INI file"""
    _logger.info("loading unit conversion for lattice {0} from "
                 "file '{1}'".format(lat.name, fname))
    from six.moves import configparser
    # python 2.7 only:
    #cfg = configparser.ConfigParser(allow_no_value=False)
    cfg = configparser.ConfigParser()
    cfg.readfp(open(fname), 'r')
    for sec in cfg.sections():
        if not cfg.has_option(sec, 'field'):
            raise RuntimeError("section [%s] has no 'field'" % sec)
        d = dict(cfg.items(sec))
        # use separated three attrs first, otherwise, use 'unitsys' attr.
        fld = d.get('field', None)
        usrcsys = d.get('src_unit_sys', None)
        udstsys = d.get('dst_unit_sys', None)
        if fld is None:
            fld, usrcsys, udstsys = re.findall(r'\w+', d.get('unitsys', ",,"))
        if not fld: continue

        # instead of '', None is the unit for lower level(epics) data
        if usrcsys == '': usrcsys = None
        if udstsys == '': udstsys = None
        # the unit name, e.g., A, T/m, ...
        # check src_unit/dst_unit first, then direction as a backup
        usrc = d.get('src_unit', None)
        udst = d.get('dst_unit', None)
        if usrc is None and udst is None:
            usrc, udst = d.get('direction', (None, None))

        _logger.debug("{0}[{1}] -> {2}[{3}]".format(usrcsys, usrc, udstsys, udst))

        if 'polynomial' in d:
            p = [float(v) for v in re.findall(r'[^ ,;]+', d['polynomial'])]
            _logger.debug("field '{0}' polynomial {1}".format(fld, p))
            uc = UcPoly(usrc, udst, p)
        elif 'interpolation' in d:
            ix, iy = re.findall(r'\w+', d.get('interpolation_cols', "0 1"))
            v = np.loadtxt(d['interpolation'])
            uc = UcInterp1(usrc, udst, v[:,int(ix)], v[:,int(iy)])
        else:
            raise RuntimeError("unknow unit converter")

        # the unit symbol
        uc.srcunit = usrc
        uc.dstunit = udst

        # find the element list
        elems = re.findall(r'\w+', d.get('elements', ""))

        eobjs = []
        for ename in elems:
            eobj = lat._find_exact_element(ename)
            if not eobj:
                _logger.warn("element {0}/{1} not found. ignored".format(
                        lat.name, ename))
                continue
            eobjs.append(eobj)

        fams = re.findall(r'\w+', d.get('groups', ""))
        for fam in fams:
            egrps = lat.getElementList(fam)
            if not egrps:
                _logger.warn("group '{0}/{1}' not found. ignored".format(
                        lat.name, fam))
            eobjs += egrps

        _logger.info("unitconversion data for field= '{0}' elems={1}, "
                     "fams={2}".format(fld, elems, fams))
        _logger.info("unitconversion will be updated for {0}".format(
            [e.name for e in eobjs]))
        for eobj in eobjs:
            if fld not in eobj.fields():
                # fld is the converted value.
                realfld = d.get('rawfield', None)
                if realfld is None:
                    _logger.warn("'%s/%s' has no field '%s' for unit conversion" %
                                 (lat.name, eobj.name, fld))
                    continue
                else:
                    # the fld is not available, but it will be an alias to
                    # rawfield, i.e. it only holds the result of unit
                    # conversion from real field.
                    eobj.addAliasField(fld, realfld)

            _logger.info("adding unit conversion for {0}.{1}, "
                         "from {2} to {3}".format(
                             eobj.name, fld, usrcsys, udstsys))
            eobj.addUnitConversion(fld, uc, usrcsys, udstsys)


def addIdentityUnitConversion(elem, fld, usrcsys, udstsys):
    """set unit conversion for two unitsys which are equivalent

    This is usually the case for BPM where raw data are in physics unit.
    """
    uc = UcAbstract(usrcsys, udstsys)
    uc.dstunit = elem.getUnit(fld, usrcsys)
    uc.srcunit = uc.dstunit
    elem.addUnitConversion(fld, uc, usrcsys, udstsys)

def loadUnitConversion(lat, machdir, datafile):
    """
    datafile = ['file name'] or ['file name', 'group']
    """
    fname, grp = datafile if len(datafile) == 2 else (datafile[0], '')
    rt, ext = os.path.splitext(fname)
    if ext.upper() == ".INI":
        loadUnitConversionIni(lat, os.path.join(machdir, fname))
    elif ext.upper() in [".HDF5", ".H5"]:
        loadUnitConversionH5(lat, os.path.join(machdir, fname), grp)
    elif ext.upper() in (".YML", ".YAML"):
        loadUnitConversionYaml(lat, os.path.join(machdir, fname))
    else:
        raise RuntimeError("unknown unit conversion: {0}{1}".format(
            machdir, datafile))
