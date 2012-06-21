"""
Twiss
~~~~~~


:author: Lingyun Yang
:date: 2011-05-13 12:40
"""

import numpy as np

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
        get twiss value

        :param name: twiss item name
        :type name: str
        :return: twiss value
        :rtype: tuple, float
        :Example:

            get('alpha')
            (0.0, 0.0)
            get('betax')
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

    
class Twiss:
    """
    Twiss table

    A list of twiss items and related element names. It has tunes and
    chromaticities.

    :Example:

        tw = Twiss()
        print tw[0]
    """
    def __init__(self, name):
        self._elements = []
        self._twlist = []
        self._name = name
        self.tune = (None, None)
        self.chrom = (None, None)
        
    def _find_element(self, elemname):
        try:
            i = self._elements.index(elemname)
            return i
        except IndexError:
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
        if not self._elements or not self._twlist: return ''

        s = "# %d " % len(self._elements) + TwissItem.header() + '\n'
        for i, e in enumerate(self._elements):
            s = s + "%16s " % e + self._twlist[i].__repr__() + '\n'
        return s

    def append(self, twi):
        """
        :param twi: twiss value at one point
        :type twi: :class:`~aphla.twiss.TwissItem`
        """

        self._twlist.append(twi)

    def getTwiss(self, elem, col, **kwargs):
        """
        return a list of twiss functions when given a list of element name.
        
        - *col*, a list of columns : 's', 'beta', 'betax', 'betay',
          'alpha', 'alphax', 'alphay', 'phi', 'phix', 'phiy'.
        - *clean*, skip the unknown elements 
        
        :Example:

          getTwiss(['E1', 'E2'], col=('s', 'beta'))

        'beta', 'alpha' and 'phi' will be expanded to two columns.
        """

        if not col: return None
        clean = kwargs.get('clean', False)

        # check if element is valid
        iret = []
        for e in elem:
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

