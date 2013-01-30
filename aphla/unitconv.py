"""
Unit Conversion
----------------
"""

# :author: Lingyun Yang <lyyang@bnl.gov>

import numpy as np
from collections import Iterable
import h5py
import logging

logger = logging.getLogger(__name__)

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
        if isinstance(x, Iterable):
            return [self.p(v) for v in x]
        else:
            return self.p(x)

class UcInterp1(UcAbstract):
    """linear interpolation"""
    def __init__(self, src, dst, x, y):
        super(UcInterp1, self).__init__(src, dst)
        #self.f = np.interpolate.interp1d(x, y)
        self.xp, self.fp = x, y

    def eval(self, x):
        if x < self.xp[0] or x > self.xp[-1]: return None
        return np.interp(x, self.xp, self.fp)

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
        if not isinstance(x, Iterable):
            raise RuntimeError("expecting an iterable input")
        ret = []
        for i,v in enumerate(x):
            if x < self.xp[i][0] or x > self.xp[i][-1]:
                ret.append(None)
            else:
                ret.append(np.interp(x[i], self.xp[i], self.fp[i]))
        return ret


def setUnitConversion(lat, h5file, group):
    """set the unit conversion for lattice with input from hdf5 file"""
    g = h5py.File(h5file, 'r')[group]
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

        elems = v.attrs.get('elements', [])

        eobjs = []
        for ename in elems:
            eobj = lat._find_exact_element(ename)
            if not eobj: continue
            eobjs.append(eobj)

        fams = v.attrs.get('families', [])
        for fam in fams: eobjs += lat.getElementList(fam)

        for eobj in eobjs:
            if fld not in eobj.fields():
                logger.warn("'%s' has no field '%s' for unit conversion" % (
                        ename, fld))
            else:
                eobj.addUnitConversion(fld, uc, usrcsys, udstsys)

