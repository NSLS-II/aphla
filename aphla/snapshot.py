import numpy as np
import h5py

from catools import caget
from machines import lattices, getLattice
from hlalib import getElements, fget

class Snapshot(object):
    def __init__(self):
        self._rec = []
        self._diff = []

    def _read_h5_subgroup(self, grp, subgrp):
        if subgrp not in grp: return []
        ds = grp[subgrp]
        elems = list(ds[:, "element"])
        flds  = list(ds[:, "field"])
        vals  = list(ds[:, "value"])
        pvs   = list(ds[:, "pv"])
        rws   = list(ds[:, "rw"])
        wf    = [0] * len(pvs)
        ts    = list(ds[:, "timestamp"] )
        return zip(elems, flds, vals, pvs, rws, wf, ts)

    def addData(self, rec, diff):
        self._rec.append(rec)
        self._diff.append(diff)

    def count(self):
        return len(self._rec)

    def data(self, i):
        return self._rec[i], self._diff[i]

    def load(self, h5fname, latname):
        print "Loading", h5fname, latname
        f = h5py.File(str(h5fname), 'r')
        self._rec.extend(self._read_h5_subgroup(f[latname], "__scalars__"))
        self._rec.extend(self._read_h5_subgroup(f[latname], "__dead__"))

        # read waveforms
        for k,v in f[latname].items():
            if not k.startswith("wf_"): continue
            self._rec.append(
                (v.attrs["element"], v.attrs["field"], list(v),
                 v.attrs["pv"], v.attrs["rw"], len(v), 
                 v.attrs["timestamp"]))
        f.close()
        self._diff = [None] * len(self._rec)

    def _calc_diff(self, v1, v2, wf1, rel):
        if wf1 > 1:
            return [self._calc_diff(v1[i], v2[i], 0, rel) for i in range(wf1)]

        try:
            diff = float(v1) - float(v2)
            if float(v2) == 0.0:
                rdiff = None
            else:
                rdiff = diff/float(v2)
        except ValueError:
            return None

        if rel: return rdiff
        else: return diff
        

    def sub(self, rhs, relative = False):
        #k1 = dict([((r[0], r[1]), i) for i,r in enumerate(self._rec)])
        k2 = dict([((r[0], r[1]), i) for i,r in enumerate(rhs._rec)])
        rec = self._rec
        self._rec = []
        for i,r in enumerate(zip(rec, rhs._rec)):
            r2 = rhs._rec[i]
            #if (r[0],r[1]) != (r2[0], r2[1]):
            #    raise RuntimeError("two snapshot are not aligned")
            i2 = k2.get((r[0], r[1]), None)
            if i2 is None:
                self._diff[i] = None
                continue
            
            self._diff[i] = self._calc_diff(r[2], r2[2], r[5], relative)


#def plotLatticeOrbit(dsnames, withLive=True, figsize=(16,4)):
#
    
def plotLattice(fname, h5group = "/", pvs = [], elemflds = [],
                withLive=False, figsize=(16,4)):
    """
    pvs
    elemflds - use readback of this set of (elemobj, field)

    >>> elemflds = [(e, 'b1') for e in ap.getElements("QUAD")]
    >>> plotLattice("snapshot.hdf5", h5group="SR", elemflds=elemflds)
    """
    h5g = h5py.File(fname, 'r')[h5group]
    # assumes scalar, not waveform
    data = np.zeros((len(pvs) + len(elemflds), 2), 'd')
    for i,pv in enumerate(pvs):
        try:
            data[i,0] = h5g[pv]
        except:
            data[i,0] = np.nan
    # from (elemname, field) to "element.field" as in h5ds.attrs
    slst = ["%s.%s" % (e.name, fld) for e,fld in elemflds]
    for pv,val in h5g.items():
        if all([v not in slst for v in val.attrs.get("element.field", [])]) or \
                val.size > 1:
            continue
        i = slst.index(val.attrs["element.field"])
        #print i, pv, np.shape(val), val
        data[i+len(pvs), 0] = val.value
    import matplotlib.pylab as plt
    fig = plt.figure(figsize=figsize)
    if withLive:
        data[:len(pvs),1] = caget(pvs)
        data[len(pvs):,1] = fget(elemflds, unitsys=None)
        ax1 = plt.subplot(2,1,1)
        ax1.plot(data[:,0], '-x', label="snapshot")
        ax1.plot(data[:,1], '-o', label="Live")
        ax2 = plt.subplot(2,1,2)
        ax2.plot(data[:,1] - data[:,0], '-o', label="diff")
        ax2.set_ylabel("Live-snapshot")
    else:
        plt.plot(data[:,0], '-x', label="snapshot")
        
    plt.grid(True)
    return fig
