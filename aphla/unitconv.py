"""
Unit Conversion
~~~~~~~~~~~~~~~~
"""

import numpy as np
from collections import Iterable

class UnitConversion(object):
    def __init__(self, src, dst):
        self.direction = (src, dst)

    def __str__(self):
        src, dst = self.direction[0], self.direction[1]
        return "%s -> %s: identity" % (src, dst)

    def eval(self, x):
        return x

class UcPoly(UnitConversion):
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

class UcInterp1(UnitConversion):
    """linear interpolation"""
    def __init__(self, src, dst, x, y):
        super(UcInterp1, self).__init__(src, dst)
        #self.f = np.interpolate.interp1d(x, y)
        self.xp, self.fp = x, y

    def eval(self, x):
        if x < self.xp[0] or x > self.xp[-1]: return None
        return np.interp(x, self.xp, self.fp)

class UcInterpN(UnitConversion):
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


