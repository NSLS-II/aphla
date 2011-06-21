"""
Twiss
~~~~~~


:author: Lingyun Yang
:date: 2011-05-13 12:40
"""

import numpy as np
from catools import caget, caput

class TwissItem:
    """
    twiss item

    Stores twiss parameter for one element at begin(b), center(c), exit(e) or
    all three locations.

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
        self._s     = kwargs.get('s', 0.0)
        self._alpha = kwargs.get('alpha', (0.0, 0.0))
        self._beta  = kwargs.get('beta', (0.0, 0.0))
        self._gamma = kwargs.get('gamma', (0.0, 0.0))
        self._eta   = kwargs.get('eta', (0.0, 0.0))
        self._phi   = kwargs.get('phi', (0.0, 0.0))

    def _str_head(self):
        return "# s  alpha  beta  eta  phi"

    def __repr__(self):
        return "%.3f % .2f % .2f  % .2f % .2f  % .2f % .2f  % .2f % .2f" % \
            (self._s, self._alpha[0], self._alpha[1],
             self._beta[0], self._beta[1], self._eta[0], self._eta[1],
             self._phi[0], self._phi[1])

    
class Twiss:
    """
    Twiss table

    A list of twiss items and related element names. It has tunes and
    chromaticities.
    """
    def __init__(self, name):
        self._elements = []
        self._twlist = []
        self._name = name
        self.tune = (0, 0)
        self.chrom = (0, 0)
        
    def _find_element(self, elemname):
        try:
            i = self._elements.index(elemname)
            return i
        except:
            raise

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

        s = "# %d " % len(self._elements) + self._twlist[0]._str_head() + '\n'
        for i,e in enumerate(self._elements):
            s = s + "%16s " % e + self._twlist[i].__repr__() + '\n'
        return s

    def append(self, twi):
        self._twlist.append(twi)


if __name__ == "__main__":
    tw = Twiss()
    print 's', tw.s()
    print 'beta', tw.beta()
    print 'beta bce', tw.beta('bce')
    print 'beta x', tw.betax(), 'beta y', tw.betay()
    print 'betax e', tw.betax('e')
    print 'betax bec', tw.betax('bec')
    
