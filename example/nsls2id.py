"""
NSLS-II insertion device commissioning/operation

copyright (C) 2014, Yongjun Li, Yoshi Hidaka, Lingyun Yang
"""

import aphla as ap
import itertools
import numpy as np
import re
import h5py

_params = {
    "dw100g1c08u":
        {"unitsys": "phy",
         "gap": (119.0, 147.0, 30, 0.1),
         "cch": ("cch0", "cch1", "cch2", "cch3", "cch4", "cch5"),
         "background": {"gap": 147.0},
         "Imin": 2.0, # mA
         "Tmin": 2.0, # hour
         "timeout": 150, },
    "dw100g1c08d":
        {"unitsys": "phy",
         "gap": (119.0, 147.0, 30, 0.1),
         "cch": ("cch0", "cch1", "cch2", "cch3", "cch4", "cch5"),
         "background": {"gap": 147.0},
         "Imin": 2.0, # mA
         "Tmin": 2.0, # hour
         "timeout": 150, },
    "dw100g1c18u":
        {"unitsys": "phy",
         "gap": (119.0, 147.0, 30, 0.1),
         "cch": ("cch0", "cch1", "cch2", "cch3", "cch4", "cch5"),
         "background": {"gap": 147.0},
         "Imin": 2.0, # mA
         "Tmin": 2.0, # hour
         "timeout": 150, },
    "dw100g1c18d":
        {"unitsys": "phy",
         "gap": (119.0, 147.0, 30, 0.1),
         "cch": ("cch0", "cch1", "cch2", "cch3", "cch4", "cch5"),
         "background": {"gap": 147.0},
         "Imin": 2.0, # mA
         "Tmin": 2.0, # hour
         "timeout": 150, },
    "dw100g1c28u":
        {"unitsys": "phy",
         "gap": (119.0, 147.0, 30, 0.1),
         "cch": ("cch0", "cch1", "cch2", "cch3", "cch4", "cch5"),
         "background": {"gap": 147.0},
         "Imin": 2.0, # mA
         "Tmin": 2.0, # hour
         "timeout": 150, },
    "dw100g1c28d":
        {"unitsys": "phy",
         "gap": (119.0, 147.0, 30, 0.1),
         "cch": ("cch0", "cch1", "cch2", "cch3", "cch4", "cch5"),
         "background": {"gap": 147.0},
         "Imin": 2.0, # mA
         "Tmin": 2.0, # hour
         "timeout": 150, },
    }

def putPar(ID, parList, **kwargs):
    """
    Put (write) a set of parameters (list) on an ID while the hardware
    itself (motor control) checks whether the target state is reached or not.

    inputs:
     ID: aphla ID instance

     parList: 2d parameter list in the format of [name, value, tolerance]
     [['gap',15,1e-4],['phase',12,1e-4]]

     timeout: Maximum time the motor control should wait for each "put"
     in the unit of seconds.

     verbose: integer larger means more details.
     throw: raise exception if True, otherwise return False

    returns: True if success, otherwise False
    """
    timeout = kwargs.get("timeout", _params[ID.name].get("timeout", 150))
    unitsys = kwargs.get("unitsys", _params[ID.name].get("unitsys", 'phy'))
    throw = kwargs.get("throw", True)
    verbose = kwargs.get("verbose", 0)

    agree = True
    for par in parList:
        ID.put(par[0], par[1], timeout=timeout, unitsys=unitsys, trig=1)
        p0 = ID.get(par[0], unitsys=unitsys)
        if abs(p0-par[1]) <= par[2]:
            continue
        # error handling
        agree = False
        if verbose:
            print 'For "{0}" of {1}:'.format(par[0], ID.name)
            print 'Target SP = {0:.9g}, Current RB = {1:.9g}, Tol = {2:.9g}'.\
                format(par[1], p0, par[2])
        if throw:
            raise RuntimeError('Failed to set device within tolerance.')
        else:
            break
    return agree


def createCorrectorField(ID):
    return [(ID, fld) for fld in _params[ID.name].get("cch", [])]

def createParList(ID, parScale):
    """
    create parameter list based on the paraneter range, spaced type
     parRange: 2d parameter range in the format of
     [[name, spacedType, start, end, step, tolerance],...]
     example:[['gap','log',150,15,21,0.1]]
     scan table will cover 15~150 with 21 steps, tolerance is 0.1,
     spacedType: log or linear

    return parameter list for communicating with hardware, table for data
    archive
    """
    nlist,vlist,tlist = [],[],[] #name, value and tolerance list
    for fld, scale in parScale:
        if not _params[ID.name].get(fld, None): continue
        nlist.append(fld)
        vmin, vmax, vstep, vtol = _params[ID.name][fld]
        if scale == 'linear':
            vlist.append(list(np.linspace(vmin, vmax, int(vstep))))
        elif scale == 'log':
            if vmin<=0 or vmax<=0:
                raise RuntimeError('negative boundary can not be spaced Logarithmically')
            else:
                vlist.append(list(np.logspace(np.log10(vmin),np.log10(vmax),int(vstep))))
        else:
            raise RuntimeError('unknown spaced pattern: %s'%p[1])
        tlist.append(vtol)
    valueList = itertools.product(*vlist)
    parList = []
    for v in valueList:
        tmp = []
        for i,n in enumerate(nlist):
            tmp.append([n,v[i],tlist[i]])
        parList.append(tmp)
    valueList = itertools.product(*vlist)
    table = np.array([vi for vi in valueList])
    return parList, nlist, table


def putBackground(ID, **kwargs):
    """
    put ID to passive status,
    gap to max, phase to 0 if apply, all correction cch to zeros
    """
    gapMin, gapMax, gapStep, gapTol = kwargs.get("gap",
                                                 _params[ID.name]["gap"])
    phaseMin, phaseMax, phaseStep, phaseTol = \
        kwargs.get("phase",  _params[ID.name].get("phase", (None, None, None, None)))
    zeroPhase = 0.0
    timeout = kwargs.get("timeout", 150)
    throw   = kwargs.get("throw", True)
    unitsys = kwargs.get("unitsys", 'phy')
    verbose = kwargs.get("verbose", 0)

    flds = ID.fields()
    parList = []
    if 'gap' in flds:
        parList.append(['gap',gapMax,gapTol])
    if 'phase' in flds:
        parList.append(['phase',zeroPhase,phaseTol])

    if putPar(ID, parList, timeout=timeout,
              throw=throw, unitsys=unitsys, verbose=verbose):
        # put correcting coils to zeros
        for i in range(len(ID.cch)):
            ID.put('cch'+str(i), 0.0, unitsys=None)
        return True
    else:
        return False


def checkBeam(Imin=2, Tmin=2, online=False):
    """
    check beam life time and current
    if beam lifetime is less than Tmin [hr], 2hrs by default,
    or current is less then Imin [mA], 2mA by default
    return False, otherwise True
    """
    tau, Ib = ap.getLifetimeCurrent()
    if Ib < Imin:
        print 'Beam current too low ({0} < {1})'.format(Ib, Imin)
        return False
    if tau < Tmin:
        print 'Beam lifetime too short ({0} < {1})'.format(tau, Tmin)
        return False
    return True


def checkGapPhase(ID, **kwargs):
    """
    check ID gap, phase
    return True if success, otherwise False
    """
    gapMin, gapMax, gapStep, gapTol = kwargs.get("gap",
                                                 _params[ID.name]["gap"])
    phaseMin, phaseMax, phaseStep, phaseTol = \
        kwargs.get("phase",  _params[ID.name].get("phase", (None, None, None, None)))
    timeout = kwargs.get("timeout", 150)
    throw   = kwargs.get("throw", True)
    unitsys = kwargs.get("unitsys", _params[ID.name]["unitsys"])
    verbose = kwargs.get("verbose", 0)
    gapStep = kwargs.get("gapStep", gapStep)
    phaseStep = kwargs.get("phaseStep", phaseStep)

    flds = ID.fields()
    if 'gap' in flds:
        for gap in np.linspace(gapMin, gapMax, gapStep):
            gapList = [['gap',gap, gapTol]]
            gapStatus = putPar(ID,gapList,timeout=timeout,
                               throw=throw,unitsys=unitsys,verbose=verbose)
            if not gapStatus:
                return False
    if 'phase' in flds:
        for phase in np.linspace(phaseMin,phaseMax,phaseStep):
            phaseList = [['phase',phase,phaseTol]]
            phaseStatus = putPar(ID,phaseList,timeout=timeout,
                               throw=throw,unitsys=unitsys,verbose=verbose)
            if not phaseStatus:
                return False
    return True


def switchFeedback(fftable = "off"):
    """
    switchFeedback("on") or "off"
    """
    if fftable not in ["on", "off"]:
        raise RuntimeError("invalid feed forward table state: ('on'|'off')")

    for dw in ap.getGroupMembers(["DW",], op="union"):
        if "gap" not in dw.fields():
            print "WARNING: no 'gap' field in {0}".format(dw.name)
            continue
        pv = dw.pv(field="gap", handle="setpoint")[0]
        m = re.match(r"([^\{\}]+)\{(.+)\}", pv)
        if not m:
            print "WARNING: inconsistent naming '{0}'".format(pv)
        pvffwd = "{0}{{{1}}}MPS:Lookup_.INPA".format(m.group(1), m.group(2))
        pvffwd_pref = "{0}{{{1}-Mtr:Gap}}.RBV ".format(m.group(1), m.group(2))

        pvffwd_val = {"on": pvffwd_pref + "CP NM",
                      "off": pvffwd_pref + "NPP N"}
        print "set {0}='{1}'".format(pvffwd, pvffwd_val[fftable])
        ap.caput(pvffwd, pvffwd_val[fftable])

    # fast/slow co
    # all ID feed forward
    # weixing Bunch by Bunch

def initFile(ID, fieldList, parTable):
    """initilize file name with path, save parameter table to hdf5"""
    fileName = ap.outputFileName("ID", ID.name+"_")
    fid = h5py.File(fileName)
    grp = fid.require_group(ID.name)
    grp.attrs["__FORMAT__"] = 1
    # setup parameters
    subg = grp.require_group("parameters")
    subg["scanTable"] = parTable #
    subg["scanTable"].attrs["columns"] = fieldList
    #for p in nameList:
    #    subg["scanTable"].attrs[p] = []
    bkg = _params[ID.name]["background"]
    # like one row of scanTable, same columns
    subg["background"] = [bkg[fld] for fld in fieldList]
    subg["background"].attrs["columns"] = fieldList
    # timestamp ISO "2007-03-01 13:00:00"
    subg["minCurrent"] = _params[ID.name]["Imin"]
    subg["minCurrent"].attrs["unit"] = "mA"
    subg["minLifetime"] = _params[ID.name]["Tmin"]
    subg["minLifetime"].attrs["unit"] = "hr"
    fid.close()

    return fileName

def chooseBpmCor(ID, userBpm=False):
    """
    choose bpm and corrector
    """
    bpms = ap.getElements('BPM')
    if userBpm:
        bpms += ap.getElements('UBPM')
    bpmfields = []
    for bpm in bpms:
        bpmflds.append([bpm,'x'])
        bpmflds.append([bpm,'y'])

    corfields = []
    for i in range(len(ID.cch)):
        corflds.append([ID,'cch'+'%i'%i])

    return bpmFields, corFields

def saveToDB(fileName):
    print "save to file (Guobao's DB)"
    pass

def measOrbitResponse(IDflds, bpmflds, output, h5group):

    pass

def save1DFeedFowardTable(filepath, table, fmt='%.16e'):
    """
    Save a valid 1-D Stepped Feedforward table (NSLS-II format) to a text file.
    """

    np.savetxt(filepath, table, fmt=fmt, delimiter=', ', newline='\n')

def create1DFeedForwardTable(centers, half_widths, dI_array, I0_array=None):
    """
    Create a valid 1-D Stepped Feedforward table (NSLS-II format)
    """

    if I0_array is None:
        I_array = dI_array
    else:
        I_array = I0_array + dI_array

    table = np.hstack((np.array(centers).reshape((-1,1)),
                       np.array(half_widths).reshape((-1,1)),
                       I_array))

    return table

def calc1DFeedForwardColumns(
    ID_filepath, n_interp_pts=None, interp_step_size=None, step_size_unit=None,
    cor_inds_ignored=None, bpm_inds_ignored=None, nsv=None):
    """
    """

    # TODO: Make sure all the units are correct in the generated table
    # Gap & interval are in microns => [um]
    # Currents in ppm of 10 Amps => [10uA]

    compIterInds = getCompletedIterIndexes(ID_filepath)
    nCompletedIter = len(compIterInds)

    f = h5py.File(ID_filepath, 'r')

    ID_name = f.keys()[0]
    grp = f[ID_name]

    meas_state_1d_array = grp['parameters']['scanTable'].value
    state_unitsymb = grp['parameters']['scanTable'].attrs['unit'] # TODO: need unit conversion
    nIter, ndim = meas_state_1d_array.shape
    if ndim != 1:
        f.close()
        raise NotImplementedError('Only 1-D scan has been implemented.')
    if nCompletedIter != nIter:
        print '# of completed scan states:', nCompletedIter
        print '# of requested scan states:', nIter
        f.close()
        raise RuntimeError('You have not scanned all specified states.')
    meas_state_1d_array = meas_state_1d_array.flatten()
    state_min = np.min(meas_state_1d_array)
    state_max = np.max(meas_state_1d_array)

    if (n_interp_pts is not None) and (interp_step_size is not None):
        f.close()
        raise ValueError(('You can only specify either one of "n_interp_pts" '
                          'or "interp_step_size", not both.'))
    elif n_interp_pts is not None:
        interp_state_1d_array = np.linspace(state_min, state_max, n_interp_pts)
    elif interp_step_size is not None:
        interp_state_1d_array = np.arange(state_min, state_max, interp_step_size)
        if interp_state_1d_array[-1] != state_max:
            interp_state_1d_array = np.array(interp_state_1d_array.tolist()+
                                             [state_max])
    else:
        interp_state_1d_array = meas_state_1d_array

    M_list        = [None]*nIter
    diff_orb_list = [None]*nIter
    for k in grp.keys():
        if k.startswith('iter_'):

            iIter = grp[k].attrs['iteration']

            M_list[iIter] = grp[k]['orm']['m'].value

            orb = grp[k]['orbit'].value

            bkgGroup = grp[k].attrs['background']
            orb0 = grp[bkgGroup]['orbit'].value[:,:-1] # Ignore s-pos column

            diff_orb_list[iIter] = orb - orb0


    f.close()

    interp_state_1d_array = np.sort(interp_state_1d_array)

    center_list = interp_state_1d_array.tolist()

    half_width_list = (np.diff(interp_state_1d_array)/2.0).tolist()
    half_width_list.append(center_list[-1]-center_list[-2]-half_width_list[-1])

    dI_list = []
    for M, diff_orb in zip(M_list, diff_orb_list):

        TF = np.ones(diff_orb.shape)
        if bpm_inds_ignored is not None:
            for i in bpm_inds_ignored:
                TF[i,:] = 0
        TF = TF.astype(bool)

        diff_orb_trunc = diff_orb[TF].reshape((-1,2))

        # Reverse sign to get desired orbit change
        dObs = (-1.0)*diff_orb_trunc.T.flatten().reshape((-1,1))

        TF = np.ones(M.shape)
        if cor_inds_ignored is not None:
            for i in cor_inds_ignored:
                TF[:,i] = 0
        if bpm_inds_ignored is not None:
            nBPM = M.shape[0]/2
            try:
                assert nBPM*2 == M.shape[0]
            except:
                raise ValueError('Number of rows for response matrix must be 2*nBPM.')
            for i in bpm_inds_ignored:
                TF[i     ,:] = 0
                TF[i+nBPM,:] = 0
        TF = TF.astype(bool)

        M_trunc = M[TF].reshape((dObs.size,-1))

        U, sv, V = np.linalg.svd(M_trunc, full_matrices=0, compute_uv=1)

        S_inv = np.linalg.inv(np.diag(sv))
        if nsv is not None:
            S_inv[nsv:, nsv:] = 0.0

        dI = V.T.dot(S_inv.dot(U.T.dot(dObs))).flatten().tolist()

        if cor_inds_ignored is not None:
            for i in cor_inds_ignored:
                # Set 0 Amp for unused correctors
                dI.insert(i, 0.0)

        dI_list.append(dI)

    dI_array = np.array(dI_list)
    nCor = dI_array.shape[1]
    interp_dI_array = np.zeros((interp_state_1d_array.size, nCor))
    for i in range(nCor):
        interp_dI_array[:,i] = np.interp(
            interp_state_1d_array, meas_state_1d_array, dI_array[:,i])

    return {'centers': np.array(center_list),
            'half_widths': np.array(half_width_list),
            'raw_dIs': dI_array, 'interp_dIs': interp_dI_array}

#----------------------------------------------------------------------
def getCompletedIterIndexes(ID_filepath):
    """"""

    f = h5py.File(ID_filepath, 'r')

    ID_name = f.keys()[0]
    grp = f[ID_name]

    completed_iter_indexes = []
    for k in grp.keys():
        if k.startswith('iter_') and grp[k].attrs.has_key('completed'):
            completed_iter_indexes.append(grp[k].attrs['iteration'].value)

    f.close()

    if completed_iter_indexes != []:
        if not np.all(np.diff(completed_iter_indexes) == 1):
            raise RuntimeError(
                'List of completed iteration indexes has some missing indexes.')
        if np.min(completed_iter_indexes) != 0:
            raise RuntimeError('List of completed iteration indexes does not start from 0.')

    return completed_iter_indexes

if __name__ == '__main__':

    ID_filepath = '/epics/data/aphla/SR/2014_09/ID/dw100g1c08u_2014_09_24_142644.hdf5'

    d = calc1DFeedForwardColumns(ID_filepath, interp_step_size=1.0,
                                 cor_inds_ignored=[2,3],
                                 bpm_inds_ignored=None, nsv=None)
    table = create1DFeedForwardTable(d['centers'], d['half_widths'],
                                     d['interp_dIs'])
    save1DFeedFowardTable('test_ff.txt', table, fmt='%.16e')
