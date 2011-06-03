"""
Twiss


:author: Lingyun Yang
:date: 2011-05-13 12:40
"""

import numpy as np

class Twiss:
    """
    twiss

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
    *elemname*       element name
    *set*            available data. 'c'/'b'/'e' for center, begin and end.
                     They can be combined. 'cbe'
    ===============  =======================================================

    Values are stored for 'bce', i.e. begin/center/entrance, of one
    element. Depending on the value of *set*, could only partial data are
    non-zeros.

    default location is the end point.
    """

    def __init__(self):
        self._s     = np.zeros(3, 'd')
        self._alpha = np.zeros((3, 2), 'd')
        self._beta  = np.zeros((3, 2), 'd')
        self._gamma = np.zeros((3, 2), 'd')
        self._eta   = np.zeros((3, 2), 'd')
        self._phi   = np.zeros((3, 2), 'd')
        self._elemname = ''
        self._set   = ''

    def _valid_data_set(self, loc):
        ret = []
        for s in loc:
            if s == 'b': ret.append(0)
            elif s == 'c': ret.append(1)
            elif s == 'e': ret.append(2)
        return ret
    
    def s(self, loc = ''):
        if loc == '':
            return self._s[2]
        else:
            ret = self._valid_data_set(loc)
            return self._s[ret]

    def _get_data(self, data, loc):
        if loc == '':
            return data[2]
        else:
            ret = self._valid_data_set(loc)
            return data[ret]
        
    def beta(self, loc = ''):
        return self._get_data(self._beta, loc)

    def betax(self, loc = ''):
        return self._get_data(self._beta[:,0], loc)

    def betay(self, loc = ''):
        return self._get_data(self._beta[:,0], loc)

    def eta(self, loc = ''):
        return self._get_data(self._eta, loc)

    def etax(self, loc = ''):
        return self._get_data(self._eta[:,0], loc)

    def etay(self, loc = ''):
        return self._get_data(self._eta[:,0], loc)

    def gamma(self, loc = ''):
        return self._get_data(self._gamma, loc)

    def gammax(self, loc = ''):
        return self._get_data(self._gamma[:,0], loc)

    def gammay(self, loc = ''):
        return self._get_data(self._gamma[:,0], loc)

    def phi(self, loc = ''):
        return self._get_data(self._phi, loc)

    def phix(self, loc = ''):
        return self._get_data(self._phi[:,0], loc)

    def phiy(self, loc = ''):
        return self._get_data(self._phi[:,0], loc)

    def alpha(self, loc = ''):
        return self._get_data(self._alpha, loc)

    def alphax(self, loc = ''):
        return self._get_data(self._alpha[:,0], loc)

    def alphay(self, loc = ''):
        return self._get_data(self._alpha[:,0], loc)

if __name__ == "__main__":
    tw = Twiss()
    print 's', tw.s()
    print 'beta', tw.beta()
    print 'beta bce', tw.beta('bce')
    print 'beta x', tw.betax(), 'beta y', tw.betay()
    print 'betax e', tw.betax('e')
    print 'betax bec', tw.betax('bec')
    
