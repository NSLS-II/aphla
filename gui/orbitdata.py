"""
Orbit Data
"""
import numpy as np

class OrbitData(object):
    """
    the orbit related data. Raw orbit reading and statistics.

    - *samples* data points kept to calculate the statistics.
    - *scale* factor for *y*
    - *x* list of s-coordinate, never updated.
    - *pvs* list of channel names
    - *mode* 'EPICS' | 'sim', default is 'EPICS'
    - *keep* mask for ignore(0) or keep(1) that data point.
    """
    def __init__(self, **kw):
        print "kw:",kw
        self.samples = kw.get('samples', 10)
        self.xscale = kw.get('xscale', 1.0)
        self.yscale = kw.get('yscale', 1.0)

        self.picker_profile = kw.get('picker_profile', None)
        self.magnet_profile = kw.get('magnet_profile', None)

        self.s = kw.get('s', None)
        if self.s is None: n = 0
        else: n = len(self.s)
        print "s loc:", self.s

        self.pvs = kw.get('pvs', None)
        self.elems = kw.get('elements', None)

        if n == 0:
            self.x, self.y = None, None
            self.xref, self.yref = None, None
            self.icur, self.icount = None, None
            # how many samples are kept for statistics
            self.xerrbar, self.yerrbar = None, None
            self.keep   = None
            #print self.x, self.y
        else:
            dim = (self.samples, n)
            self.x, self.y = np.zeros(dim, 'd'), np.zeros(dim, 'd')
            self.xref, self.yref = np.zeros(n, 'd'), np.zeros(n, 'd')
            self.icur, self.icount = -1, 0
            self.xerrbar = np.ones(n, 'd') * 1e-15
            self.yerrbar = np.ones(n, 'd') * 1e-15
            self.keep = [True] * n

        return

        if self.pvs is not None:
            n = len(pvs)
            self.x = kw.get('x', np.arange(n))
            self.y = np.zeros((self.samples, n), 'd')
            self.y[0,:] = caget(self.pvs)
        elif self.elems is not None:
            n = len(self.elems)
            self.x = kw.get('x', np.arange(n))
            self.y = np.zeros((self.samples, n), 'd')
            # only take the first sample
            for j in range(n):
                self.y[0,j] = self.elems[j].get(self.field)
        else:
            n = 0
            self.x = None

        #if self.x is not None and len(self.x) != n:
        #    raise ValueError("pv and x are not same size %d != %d" % (n, len(self.x)))
            

    def _update_pvs_data(self):
        """
        update the orbit data. It retrieve the data with channel access and
        calculate the updated standard deviation. If the current mode is
        'sim', instead of channel access it uses random data.
        """
        # y and errbar sync with plot, not changing data.
        i = self.icur + 1
        if i >= self.samples: i = 0
        self.y[i,:] = caget(self.pvs)
        self.y[i, :] *= self.yfactor
        self.errbar[:] = np.std(self.y, axis=0)
        self.icount += 1
        self.icur = i
        
    def _update_elems_data(self):
        """
        update the orbit data. It retrieve the data with channel access and
        calculate the updated standard deviation. If the current mode is
        'sim', instead of channel access it uses random data.
        """
        # y and errbar sync with plot, not changing data.
        i = self.icur + 1
        if i >= self.samples: i = 0
        self.y[i,:] = [e.get(self.field) for j,e in enumerate(self.elems)]
        self.y[i,:] *= self.scale
        self.errbar[:] = np.std(self.y, axis=0)
        self.icount += 1
        self.icur = i
        
    def update(self):
        if self.pvs is not None:
            self._update_pvs_data()
        elif self.elems is not None:
            self._update_elems_data()

    def reset(self):
        """
        clear the history data points and statistics.
        """
        self.icur, self.icount = -1, 0
        self.x.fill(0.0)
        self.y.fill(0.0)
        self.errbar.fill(0.0)
        #self.update()
        
    def xmin(self, axis='s'):
        c, i = divmod(self.icount - 1, self.samples)
        data = np.compress(self.keep, self.x, axis=1)
        return np.min(data)
    
    def ymin(self, axis='s'):
        c, i = divmod(self.icount - 1, self.samples)
        data = np.compress(self.keep, self.y, axis=1)
        return np.min(data)

    def max(self, axis='s'):
        c, i = divmod(self.icount - 1, self.samples)
        data = np.compress(self.keep, self.y, axis=1)
        return np.max(data)
        
    def average(self, axis='s'):
        """average of the whole curve"""
        c, i = divmod(self.icount - 1, self.samples)
        data = np.compress(self.keep, self.y, axis=1)
        return np.average(data)

    def std(self, axis='s'):
        """
        std of the curve
        - axis='t' std over time axis for each PV
        - axis='s' std over all PV for the latest dataset
        """
        if axis == 't': ax = 1
        elif axis == 's': ax = 0
        y = np.compress(self.keep, self.y, axis=1)
        return np.std(y, axis = ax)

    def xorbit(self, nomask=False):
        """
        return horizontal orbit: (s, x, errorbar)
        """
        i = self.icur
        ret = self.s, self.x[i,:]-self.xref[:], self.xerrbar
        if nomask:
            return ret
        else:
            return np.compress(self.keep, ret, axis=1)
        
    def yorbit(self, nomask=False):
        """
        return vertical orbit: (s, y, errorbar)
        """
        i = self.icur
        ret = self.s, self.y[i,:]-self.yref[:], self.yerrbar
        if nomask:
            return ret
        else:
            return np.compress(self.keep, ret, axis=1)
        
    

class OrbitDataVirtualBpm(OrbitData):
    def __init__(self, **kw):
        self.velem = kw.get('velement', None)
        sb, se = np.array(self.velem.sb), np.array(self.velem.se)
        s = kw.get('s', None)
        print "s", s
        if s is None: kw.update({'s': 0.5*(sb+se)})
        print "kw vbpm:", kw

        OrbitData.__init__(self, **kw)
        #self.update()

    def update(self):
        """
        update the orbit data from virtual element.
        """
        # y and errbar sync with plot, not changing data.
        i = (self.icur + 1) % self.samples

        print "x shape", np.shape(self.velem.get('x')), np.shape(self.x)
        print "y shape", np.shape(self.velem.get('y')), np.shape(self.y)
        self.x[i,:] = self.xscale * np.array(self.velem.get('x'))
        self.y[i,:] = self.yscale * np.array(self.velem.get('y'))
        self.xerrbar[:] = np.std(self.x, axis=0)
        self.yerrbar[:] = np.std(self.y, axis=0)
        self.icount += 1
        self.icur = i
