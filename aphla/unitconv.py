"""
Unit Conversion
----------------
"""

# :author: Lingyun Yang <lyyang@bnl.gov>

import numpy as np
from collections import Iterable
import h5py
import logging

_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)

class UcAbstract(object):
    """
    an identity conversion with unit names.
    """
    def __init__(self, src, dst):
        self.direction = (src, dst)

    def __str__(self):
        src, dst = self.direction[0], self.direction[1]
        return "%s -> %s: identity" % (src, dst)

    def eval(self, x):
        return x

class UcPoly(UcAbstract):
    def __init__(self, src, dst, coef):
        super(UcPoly, self).__init__(src, dst)
        self.p = np.poly1d(coef)

    def __str__(self):
        src, dst = self.direction[0], self.direction[1]
        return "%s -> %s: %s" % (src, dst, str(self.p))

    def eval(self, x):
        if x is None: return None
        elif isinstance(x, Iterable):
            return [self.p(v) if v is not None else None for v in x]
        else:
            return self.p(x)

class UcInterp1(UcAbstract):
    """linear interpolation"""
    def __init__(self, src, dst, x, y):
        super(UcInterp1, self).__init__(src, dst)
        #self.f = np.interpolate.interp1d(x, y)
        self.xp, self.fp = x, y

    def eval(self, x):
        if x is None: return None
        elif x < self.xp[0] or x > self.xp[-1]: return None
        else: return np.interp(x, self.xp, self.fp)

class UcInterpN(UcAbstract):
    """n-D linear interpolation"""
    def __init__(self, src, dst, x, y):
        """
        :param x: a list of x-data for interpolation
        :param y: a list of y-data for interpolation

        x[i] and y[i] are a list of measurement.
        """
        super(UcInterpN, self).__init__(src, dst)
        self.xp, self.fp = x, y

    def eval(self, x):
        """if None, returns None"""
        if not isinstance(x, Iterable):
            raise RuntimeError("expecting an iterable input")
        ret = []
        for i,v in enumerate(x):
            if x is None or x < self.xp[i][0] or x > self.xp[i][-1]:
                ret.append(None)
            else:
                ret.append(np.interp(x[i], self.xp[i], self.fp[i]))
        return ret


def setUnitConversion(lat, h5file, group):
    """set the unit conversion for lattice with input from hdf5 file"""
    g = h5py.File(h5file, 'r')[group]
    _logger.info("setting unit conversion for {0} from data file {1}:{2}".format(
        lat.name, h5file, g.items()))
    for k,v in g.items():
        if not v.attrs.get('_class_', None): continue 
        if not v.attrs.get('unitsys', None): continue

        fld, usrcsys, udstsys = v.attrs['unitsys'].split(',')
        # instead of '', None is the unit for lower level(epics) data
        if usrcsys == '': usrcsys = None
        if udstsys == '': udstsys = None
        # the unit name, e.g., A, T/m, ...
        usrc, udst = v.attrs.get('direction', ('', ''))
        if v.attrs['_class_'] == 'polynomial':
            uc = UcPoly(usrc, udst, list(v))
        elif v.attrs['_class_'] == 'interpolation':
            uc = UcInterp1(usrc, udst, v[:,0], v[:,1])
        else:
            raise RuntimeError("unknow unit converter")

        # find the element list
        elems = v.attrs.get('elements', [])

        eobjs = []
        #lat._find_exact_element(ename) for ename in elems if lat.hasElement(ename)]
        for ename in elems:
            eobj = lat._find_exact_element(ename)
            if not eobj: 
                _logger.warn("dataset '{0}': element {1} not found. ignored".format(
                    k, ename))
                continue
            eobjs.append(eobj)

        fams = v.attrs.get('groups', [])
        for fam in fams:
            egrps = lat.getElementList(fam)
            if not egrps:
                _logger.warn("dataset '{0}': group {1} not found. ignored".format(
                    k, fam))
            eobjs += egrps

        _logger.info("unitconversion data for elems={0}, fams={1}".format(elems, fams))
        _logger.info("unitconversion will be updated for {0}".format([e.name for e in eobjs]))
        for eobj in eobjs:
            if fld not in eobj.fields():
                realfld = v.attrs.get('rawfield', None)
                if realfld is None:
                    _logger.warn("'%s' has no field '%s' for unit conversion" % (
                        ename, fld))
                    continue
                else:
                    eobj.addAliasField(fld, realfld)

            _logger.info("adding unit conversion for {0}, from {1} to {2}".format(
                fld, usrcsys, udstsys))
            eobj.addUnitConversion(fld, uc, usrcsys, udstsys)

