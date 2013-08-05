import numpy as np
import h5py

from machines import lattices, getLattice

def _read_epics_data(lat):
    val_scalar = []
    val_vec = []
    for e in lat.getElementList('*', virtual=False):
        for k in e.fields():
            pv = [s.encode("ascii") for s in e.pv(field=k, handle='setpoint')]
            if not pv: continue
            val0 = e.get(k, handle='setpoint', unitsys=None)
            if 'phy' in e.getUnitSystems(k):
                val1 = e.convertUnit(k, val0, None, 'phy')
            else:
                val1 = np.nan
            if len(pv) > 1 or isinstance(val0, (str, list, tuple)):
                val_vec.append((e.name, k, pv, val0, val1))
            else:
                val_scalar.append((e.name, k, pv[0], val0, val1))
    return val_scalar, val_vec

def _save_data_1(grp, vscalar, vvec):
    NLname  = max([len(v[0]) for v in vscalar]) + 1
    NLfield = max([len(v[1]) for v in vscalar]) + 1
    NLpv    = max([len(v[2]) for v in vscalar]) + 1

    dt = np.dtype([('name', str, NLname),
                   ('field', str, NLfield),
                   ('pv', str, NLpv),
                   ('raw', 'd'), ('phy', 'd')])
    data = np.ndarray((len(vscalar),),  dtype=dt)
    data['name'] = np.array([v[0] for v in vscalar])
    data['field'] = [v[1] for v in vscalar]
    data['pv'] = [v[2] for v in vscalar]
    data['raw'] = [v[3] for v in vscalar]
    data['phy'] = [v[4] for v in vscalar]

    grp.create_dataset("_PV_SCALAR_", (len(vscalar),), dtype=dt, data=data)


def _save_epics_data_2(lat, grp):
    """each element.field is one dataset"""
    for e in lat.getElementList('*', virtual=False):
        for k in e.fields():
            pv = [s.encode("ascii") for s in e.pv(field=k, handle='setpoint')]
            # skip the readback PVs
            if not pv: continue
            val0 = e.get(k, handle='setpoint', unitsys=None)

            val1 = np.nan
            if 'phy' in e.getUnitSystems(k):
                val1 = e.convertUnit(k, val0, None, 'phy')

            dim = (2, 1)
            if len(pv) > 1 or isinstance(val0, (str, list, tuple)):
                dim = (2, len(val0))

            dset = grp.create_dataset("%s.%s" % (e.name, k), dim,
                                      data=(val0, val1))
            dset.attrs['pv'] = pv
            dset.attrs['val'] = ['raw', 'phy']

def _save_data_2(grp, vscalar, vvec):
    for v in vscalar:
        dset = grp.create_dataset("%s.%s" % (v[0], v[1]), (2,), 
                                  data=(v[3], v[4]))
        dset.attrs['pv'] = v[2]
    for v in vvec:
        dset = grp.create_dataset("%s.%s" % (v[0], v[1]), (2, len(v[3])), 
                                  data=(v[3], v[4]))
        dset.attrs['pv'] = v[2]


def saveSnapshot(fname, lats):
    """save snapshot of a list of lattices

    - fname output file name
    - lats list/str lattice name

    The not-found lattice will be ignored.
    """
    
    livelats = []
    if lats is None:
        livelats.append(getLattice(lats))
    elif isinstance(lats, (str, unicode)):
        livelats.append(getLattice(lats))
    elif isinstance(lats, (list, tuple)):
        livelats.extend([getLattice(lat) for lat in lats])
    
    f = h5py.File(fname, 'w')
    for lat in livelats:
        if lat is None: continue
        vs, vv = _read_epics_data(lat)
        grp = f.create_group(lat.name)
        #_save_data_1(grp, vs, vv)
        #_save_data_2(grp, vs, vv)
        #_save_data_2(grp, [('a', '0', 'pv', 0, 0),
        #                   ('a', '1', 'pv', 0, 0),],
        #             [('a', '2', ['c', 'd'], [1,2,3], [4,5,6])])
        _save_epics_data_2(lat, grp)

    f.close()

    
