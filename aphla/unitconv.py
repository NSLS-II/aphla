"""
Unit Conversion
~~~~~~~~~~~~~~~~
"""

import numpy as np

class UnitConversion(object):
    def __init__(self, src, dst):
        self.direction = (src, dst)

    def __str__(self):
        src, dst = self.direction[0], self.direction[1]
        return "%s -> %s: identity" % (src, dst)

    def eval(self, x):
        return x

class UcPoly1d(UnitConversion):
    def __init__(self, src, dst, coef):
        super(UcPolynomial, self).__init__(src, dst)
        self.p = np.poly1d(coef)

    def __str__(self):
        src, dst = self.direction[0], self.direction[1]
        return "%s -> %s: %s" % (src, dst, str(self.p))

    def eval(self, x):
        return self.p(x)

class UcInterp1d(UnitConversion):
    """linear interpolation"""
    def __init__(self, src, dst, x, y):
        super(UcPolynomial, self).__init__(src, dst)
        #self.f = np.interpolate.interp1d(x, y)
        self.xp, self.fp = x, y

    def eval(self, x):
        if x < self.xp[0] or x > self.xp[-1]: return None
        return np.interp(x, self.xp, self.fp)

