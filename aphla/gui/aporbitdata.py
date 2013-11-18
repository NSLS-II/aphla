"""
Orbit Data
==========

:author: Lingyun Yang <lyyang@bnl.gov>

The data module for aporbit.
"""

import numpy as np
from PyQt4.QtCore import QTimer, SIGNAL, QObject
import logging
logger = logging.getLogger(__name__)
from aphla import eget

class ApPlotData(object):
    """
    the orbit related data. Raw orbit reading and statistics.

    - *samples* data points kept to calculate the statistics.
    - *scale* factor for *y*
    - *s* list of s-coordinate, never updated.
    - *pvs* list of channel names
    - *mode* 'EPICS' | 'sim', default is 'EPICS'
    - *keep* mask for ignore(0) or keep(1) that data point.
    - *elements* 
    """
    def __init__(self, s, **kw):
        self.s        = s
        self.samples  = kw.pop('samples', 10)
        self.yscale   = kw.pop('scale', 1.0)
        self.yref     = kw.pop('yref', None)
        self.yunitsys = kw.pop('unitsys', None)
        self.yunit    = kw.pop('unit', '')
        self.ylabel   = kw.pop('label', "")

        self.picker_profile = kw.pop('picker_profile', None)
        self.magnet_profile = kw.pop('magnet_profile', None)

        n = len(self.s)
        dim = (self.samples, n)
        self.y    = np.zeros(dim, 'd')
        if self.yref is None: self.yref = np.zeros(n, 'd')
        self.icur, self.icount = -1, 0
        self.yerrbar = np.ones(n, 'd') * 1e-15
        self.keep = [True] * n

    def update(self):
        pass

    def reset(self):
        """
        clear the history data points and statistics.
        """
        self.icur, self.icount = -1, 0
        self.y.fill(0.0)
        self.yerrbar.fill(0.0)
        #self.update()

    def label(self):
        return self.ylabel

    def ymin(self, axis='s'):
        c, i = divmod(self.icount - 1, self.samples)
        data = np.compress(self.keep, self.y, axis=1)
        return np.min(data)

    def ymax(self, axis='s'):
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

    def data(self, nomask=False):
        """
        return horizontal orbit: (s, y, errorbar)
        """
        i = self.icur
        ret = self.s, self.y[i,:]-self.yref[:], self.yerrbar
        if nomask:
            return ret
        else:
            return np.compress(self.keep, ret, axis=1)
        
    
class ApVirtualElemData(ApPlotData):
    def __init__(self, velem, field, **kw):
        """
        updating immediately by default, unless update=False
        """
        self.machine = kw.get("machine", None)
        self.lattice = kw.get("lattice", None)
        self.plane   = kw.get("plane", None)

        self.velem = velem
        self.name    = velem.name
        sb, se = np.array(self.velem.sb), np.array(self.velem.se)
        if not kw.has_key('s'): kw.update({'s': 0.5*(sb+se)})

        ApPlotData.__init__(self, **kw)

        self.yfield = field
        # prefer 'phy' unit
        if 'phy' in self.velem.getUnitSystems(field):  self.yunitsys = 'phy'
        if kw.get('update', True): self.update()
        
        self.yunit = self.velem.getUnit(self.yfield, self.yunitsys)

    def label(self):
        return "%s [%s]" % (self.yfield, self.yunit)

    def update(self):
        """
        update the orbit data from virtual element.
        """
        # y and errbar sync with plot, not changing data.
        i = (self.icur + 1) % self.samples
        #print "Updating orbit data"
        try:
            vy = self.velem.get(self.yfield, unitsys=self.yunitsys)
            self.y[i,:] = [self.yscale * x if x else np.nan for x in vy]
        except:
            logger.error("Can not get data '%s'" % self.yfield)
            raise

        #for j in range(len(self.x[i,:])):
        #    self.x[i,j] = (self.s[j] - self.s[0])/(self.s[-1]-self.s[0])*1.0-0.5
        #    self.y[i,j] = (self.s[j] - self.s[0])/(self.s[-1]-self.s[0])*2.0-1.5

        self.yerrbar[:] = np.std(self.y, axis=0)
        self.icount += 1
        self.icur = i

    def names(self):
        return self.velem._name

    def remove(self, name):
        """remove name from velem, raise error if name is not in velem"""
        #if name not in self.velem._name: return
        i = self.velem._name.index(name)
        for fld,act in self.velem._field.iteritems():
            pv = act.pvrb[i]
            act.remove(pv)

    def disable(self, name):
        """disable name in velem, raise error if name is not in velem"""
        #if name not in self.velem._name: return
        i = self.velem._name.index(name)
        self.keep[i] = False


class ManagedPvData(ApPlotData):
    def __init__(self, pvm, s, pvs, **kw):
        """
        updating immediately by default, unless update=False
        """
        ApPlotData.__init__(self, s, **kw)
        self._pvm = pvm
        self._pvs = pvs
        self._element  = kw.get('element', [])
        self._field    = kw.get('field', [])

    def label(self):
        return "%s [%s]" % (self.ylabel, self.yunit)

    def update(self):
        """
        update the orbit data from virtual element.
        """
        # y and errbar sync with plot, not changing data.
        i = (self.icur + 1) % self.samples
        #print "Updating orbit data"
        for j,pv in enumerate(self._pvs):
            if not self.keep[j]: continue
            self.y[i,j] = self._pvm.get(pv)
            self.yerrbar[j] = np.std(self.y[:,j])
        self.icount += 1
        self.icur = i

    def names(self):
        return self._element

    def disable(self, name):
        """disable name in velem, raise error if name is not in velem"""
        #if name not in self.velem._name: return
        i = self._element.index(name)
        self.keep[i] = False

