"""
NSLS-II insertion device commissioning/operation

copyright (C) 2014, Yongjun Li, Yoshi Hidaka, Lingyun Yang
"""

import aphla as ap
import itertools
import numpy as np
import re
import h5py
import time
from datetime import datetime
from copy import deepcopy

_params = {
    "dw100g1c08u":
        {"unitsys": "phy",
         "gap": (15.0, 150.0, 30, 0.1),
         "cch": ("cch0", "cch1", "cch2", "cch3", "cch4", "cch5"),
         "background": {"gap": 150.0},
         "Imin": 0.2, # mA
         "Tmin": 0.2, # hour
         "timeout": 150, },
    "dw100g1c08d":
        {"unitsys": "phy",
         "gap": (15.0, 150.0, 30, 0.1),
         "cch": ("cch0", "cch1", "cch2", "cch3", "cch4", "cch5"),
         "background": {"gap": 150.0},
         "Imin": 0.2, # mA
         "Tmin": 0.2, # hour
         "timeout": 150, },
    "dw100g1c18u":
        {"unitsys": "phy",
         "gap": (15.0, 150.0, 30, 0.1),
         "cch": ("cch0", "cch1", "cch2", "cch3", "cch4", "cch5"),
         "background": {"gap": 150.0},
         "Imin": 0.2, # mA
         "Tmin": 0.2, # hour
         "timeout": 150, },
    "dw100g1c18d":
        {"unitsys": "phy",
         "gap": (15.0, 150.0, 30, 0.1),
         "cch": ("cch0", "cch1", "cch2", "cch3", "cch4", "cch5"),
         "background": {"gap": 150.0},
         "Imin": 0.2, # mA
         "Tmin": 0.2, # hour
         "timeout": 150, },
    "dw100g1c28u":
        {"unitsys": "phy",
         "gap": (15.0, 150.0, 30, 0.1),
         "cch": ("cch0", "cch1", "cch2", "cch3", "cch4", "cch5"),
         "background": {"gap": 150.0},
         "Imin": 0.2, # mA
         "Tmin": 0.2, # hour
         "timeout": 180, },
    "dw100g1c28d":
        {"unitsys": "phy",
         "gap": (15.0, 150.0, 30, 0.1),
         "cch": ("cch0", "cch1", "cch2", "cch3", "cch4", "cch5"),
         "background": {"gap": 150.0},
         "Imin": 0.2, # mA
         "Tmin": 0.2, # hour
         "timeout": 180, },
    #
    "epu49g1c23u":
        {"unitsys": "phy",
         "gap": (11.5, 240.0, 30, 0.1),
         "phase": (-24.6, 24.6, 11, 0.01),
         "cch": ("cch0", "cch1", "cch2", "cch3", "cch4", "cch5"),
         "background": {"gap": 240.0, "phase": 0.0},
         "Imin": 0.2, # mA
         "Tmin": 0.2, # hour
         "timeout": 180, },
    "epu49g1c23d":
        {"unitsys": "phy",
         "gap": (11.5, 240.0, 30, 0.1),
         "phase": (-24.6, 24.6, 11, 0.01),
         "cch": ("cch0", "cch1", "cch2", "cch3", "cch4", "cch5"),
         "background": {"gap": 240.0, "phase": 0.0},
         "Imin": 0.2, # mA
         "Tmin": 0.2, # hour
         "timeout": 180, },
    # IVU
    "ivu20g1c03c":
        {"unitsys": "phy",
         "gap": (5.0, 40.0, 30, 0.1),
         "cch": ("cch0", "cch1", "cch2", "cch3", "cch4", "cch5"),
         "background": {"gap": 40.0},
         "Imin": 0.2, # mA
         "Tmin": 0.2, # hour
         "timeout": 180, },
    "ivu21g1c05d":
        {"unitsys": "phy",
         "gap": (5.0, 40.0, 30, 0.1),
         "cch": ("cch0", "cch1", "cch2", "cch3", "cch4", "cch5"),
         "background": {"gap": 40.0},
         "Imin": 0.2, # mA
         "Tmin": 0.2, # hour
         "timeout": 180, },
    "ivu22g1c10c":
        {"unitsys": "phy",
         "gap": (5.0, 40.0, 30, 0.1),
         "cch": ("cch0", "cch1", "cch2", "cch3"),
         "background": {"gap": 40.0},
         "Imin": 0.2, # mA
         "Tmin": 0.2, # hour
         "timeout": 180, },
    "ivu20g1c11c":
        {"unitsys": "phy",
         "gap": (5.0, 40.0, 30, 0.1),
         "cch": ("cch0", "cch1", "cch2", "cch3", "cch4", "cch5"),
         "background": {"gap": 40.0},
         "Imin": 0.2, # mA
         "Tmin": 0.2, # hour
         "timeout": 180, },
    }

_default_params = deepcopy(_params)

def getBrho(E_GeV):
    """
    """

    import scipy.constants as const

    m_e_GeV = const.m_e*const.c*const.c/const.e/1e9
    gamma = E_GeV / m_e_GeV

    Brho = const.m_e * const.c * gamma / const.e # magnetic rigidity [T*m]

    return Brho


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
        t0 = datetime.now()
        agree = False
        fld, target, tol = par[:3]

        p_init = ID.get(fld, unitsys=unitsys)
        if np.abs(p_init - target) < tol:
            print ('Target SP for "{0}" within specified tolerance. No "put" '
                   'will be performed.').format(fld)
            continue

        nMaxReput   = 3
        put_counter = 0

        ID.put(fld, target, timeout=timeout, unitsys=unitsys, trig=1)
        p_now = ID.get(fld, unitsys=unitsys)
        while True:
            if abs(p_now-target) < tol:
                agree = True
                break
            if (datetime.now() - t0).total_seconds() > timeout:
                break
            time.sleep(2)
            p_now = ID.get(fld, unitsys=unitsys)

            if (p_now-p_init) < tol:
                if put_counter >= nMaxReput:
                    print ('* Too many "put" failures for "{0}" change. Something '
                           'is wrong with "{0}" control. Aborting now.').format(fld)
                    break
                print ('* Apparently previous "put" did not start the '
                       '"{0}" change.').format(fld)
                print 'Requesting again for the "{0}" change.'.format(fld)
                time.sleep(3) # wait extra before re-put
                ID.put(fld, target, timeout=timeout, unitsys=unitsys, trig=1)
                put_counter += 1

        if agree:
            continue

        # error handling
        msg = 'Target SP = {0:.9g}, Current RB = {1:.9g}, Tol = {2:.9g}'.\
                format(target, p_now, tol)
        if verbose:
            print 'For "{0}" of {1}: {2}'.format(fld, ID.name, msg)
        if throw and not agree:
            raise RuntimeError('Failed to set device within tolerance: '+ msg)
        elif not agree:
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
    # Make sure that "gap" specification (if exists) comes at the end.
    # This is important since, for example, adjusting the gap first and then
    # adjusting the phase would may well result in an unintentional gap change
    # due to the associated magnetic force change.
    fields = [fld for fld, _ in parScale]
    if 'gap' in fields:
        gap_index = fields.index('gap')
        gap_scale = parScale.pop(gap_index)
        parScale.append(gap_scale)
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
        elif not isinstance(scale, (str, unicode)):
            # "scale" is a user-specified array for the parameter
            vlist.append(list(scale))
            if fld == 'gap':
                # Reset the background "gap" to be the max of use-specified gap array
                _params[ID.name]['background'][fld] = np.max(scale)
                # Reset the "gap" in _params
                temp_gap = (np.min(scale), np.max(scale),
                            _params[ID.name]['gap'][2], _params[ID.name]['gap'][3])
                _params[ID.name]['gap'] = temp_gap
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
    table = [vi for vi in valueList]
    return parList, nlist, table

def restoreDefaultParams():
    """"""

    _params = deepcopy(_default_params)


def putParHardCheck(ID, parList, timeout=30, throw=True, unitsys='phy'):
    '''
    Put (write) a set of parameters (list) on an ID while the hardware
    itself (motor control) checks whether the target state is reached or not.

    ID: aphla ID instance

    parList: 2d parameter list in the format of [name, value, tolerance]
    [['gap',15,1e-4],['phase',12,1e-4]]

    timeout: Maximum time the motor control should wait for each "put"
    in the unit of seconds.

    return: True if success, otherwise throws an exception.
    '''

    agree = True
    for par in parList:
        ID.put(par[0], par[1], timeout=timeout, unitsys=unitsys, trig=1)
        # raw unit for "gap"   = [um]
        # raw unit for "phase" = [um?]

        p0 = ID.get(par[0], unitsys=unitsys)

        if abs(p0-par[1]) <= par[2]: # TODO: readback & setpoint unit may be different! Check it!
            continue # print "Agree: ", p0, par[1], "eps=", par[2]
        # error handling
        agree = False
        print 'For "{0}" of {1}:'.format(par[0], ID.name)
        print 'Target Setpoint = {0:.9g}, Current Readback = {1:.9g}, Tolerance = {2:.9g}'.format(
            par[1], p0, par[2])
        if throw:
            raise RuntimeError('Failed to set device within tolerance.')
        else:
            break
    return agree

def putParSoftCheck(ID, parList, timeout=30, online=False):
    '''
    Put (write) a set of parameters (list) on an ID while this function
    checks whether the target state is reached or not through readbacks
    for given tolerances.

    ID: aphla ID instance

    parList: 2d parameter list in the format of [name, value, tolerance]
    [['gap',15,1e-4],['phase',12,1e-4]]

    timeout: Maximum time the motor control should wait for each "put"
    in the unit of seconds.

    return: True if success, otherwise throws an exception.
    '''

    if not online: return True # TODO: To be reomved once we are allowed to move ID motors

    for par in parList:
        t0 = datetime.now()
        converged = False

        try:
            ID.put(par[0], par[1], unitsys=None) # raw unit
        except:
            print 'Failed to set the setpoint for {0} to {1}'.format(par[0], par[1])
            raise

        # TODO: remove hardcoding
        ap.caput("SR:C28-ID:G1{DW100:2}ManG:Go_.PROC", 1, wait=False)

        while not converged:
            p0 = ID.get(par[0], unitsys=None)
            if abs(p0-par[1]) <= par[2]: # TODO: readback & setpoint unit may be different! Check it!
                # print "Agree: ", p0, par[1], "eps=", par[2]
                converged = True
                break
            t1 = datetime.now()
            if (t1-t0).total_seconds() > timeout:
                break
            time.sleep(0.5)
        if not converged:
            raise RuntimeError("timeout at setting {0}={1} (epsilon={2})".format(par[0], par[1], par[2]))

    return True

def putBackground(ID, **kwargs):
    """
    put ID to passive status,
    gap to max, phase to 0 if apply, all correction cch to zeros
    """
    gapMin, gapMax, gapStep, gapTol = kwargs.get("gap",
                                                 _params[ID.name]["gap"])
    # Reset the "gap" in _params['background']
    _params[ID.name]['background']['gap'] = gapMax
    # Reset the "gap" in _params
    _params[ID.name]['gap'] = (gapMin, gapMax, gapStep, gapTol)

    phaseMin, phaseMax, phaseStep, phaseTol = \
        kwargs.get("phase",  _params[ID.name].get("phase", (None, None, None, None)))
    zeroPhase = 0.0
    timeout     = kwargs.get("timeout", 150)
    throw       = kwargs.get("throw", True)
    unitsys     = kwargs.get("unitsys", 'phy')
    verbose     = kwargs.get("verbose", 0)
    bkg_trim_sp = kwargs.get("bkg_trim_sp", None)

    if bkg_trim_sp is None:
        bkg_trim_sp = [0.0]*len(ID.cch)
    else:
        if len(bkg_trim_sp) != len(ID.cch):
            raise ValueError('Length of "bkg_trim_sp" must be {0:d}.'.format(len(ID.cch)))

    flds = ID.fields()
    parList = []
    if 'gap' in flds:
        parList.append(['gap',gapMax,gapTol])
    if 'phase' in flds:
        parList.append(['phase',zeroPhase,phaseTol])

    if putPar(ID, parList, timeout=timeout,
              throw=throw, unitsys=unitsys, verbose=verbose):
        # put correcting coils to specified background values
        for i, v in enumerate(bkg_trim_sp):
            ID.put('cch'+str(i), v, unitsys=None)
        return True
    else:
        return False


def checkBeam(Imin=2.0, Tmin=2.0):
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


def switchFeedback(ID, fftable = "off"):
    """
    switchFeedback("on") or "off"
    """
    if fftable not in ["on", "off"]:
        raise RuntimeError("invalid feed forward table state: ('on'|'off')")
    # 0 - manual, 1 - auto
    val = 0 if fftable == "off" else 1

    if ID.name == "epu49g1c23u":
        for i in range(6):
            ap.caput("SR:C23-ID:G1A{EPU:1-FF:%d}Ena-Sel" % i, val)
    if ID.name == "epu49g1c23d":
        for i in range(6):
            ap.caput("SR:C23-ID:G1A{EPU:2-FF:%d}Ena-Sel" % i, val)
    elif ID.name == "dw100g1c28u":
        for i in range(6):
            ap.caput("SR:C28-ID:G1{DW100:1-FF:%d}Ena-Sel" % i, val)
    elif ID.name == "dw100g1c28d":
        for i in range(6):
            ap.caput("SR:C28-ID:G1{DW100:2-FF:%d}Ena-Sel" % i, val)
    elif ID.name == "ivu20g1c03c":
        for i in range(6):
            ap.caput("SR:C3-ID:G1{IVU20:1-FF:%d}Ena-Sel" % i, val)
    elif ID.name == "ivu21g1c05d":
        for i in range(6):
            ap.caput("SR:C5-ID:G1{IVU21:1-FF:%d}Ena-Sel" % i, val)
    elif ID.name == "ivu22g1c10c":
        for i in range(4):
            ap.caput("SR:C10-ID:G1{IVU22:1-FF:%d}Ena-Sel" % i, val)
    elif ID.name == "ivu20g1c11c":
        for i in range(6):
            ap.caput("SR:C11-ID:G1{IVU20:1-FF:%d}Ena-Sel" % i, val)

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
    unitsymbs = [
        ID.getUnit(f, unitsys=_params[ID.name]['unitsys'], handle='setpoint')
        for f in fieldList]
    subg = grp.require_group("parameters")
    if parTable and fieldList:
        subg["scanTable"] = parTable #
        subg["scanTable"].attrs["columns"]   = fieldList
        subg["scanTable"].attrs["unitsymbs"] = unitsymbs
    bkg = _params[ID.name]["background"]
    # like one row of scanTable, same columns
    subg["background"] = [bkg[fld] for fld in fieldList]
    subg["background"].attrs["columns"]   = fieldList
    subg["background"].attrs["unitsymbs"] = unitsymbs
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


def saveState(idobj, output, iiter,
              parnames=None, background=None, extdata={}):
    """
    parnames - list of extra fields of idobj to be saved.
    background - the group name for its last background.
    extdata - extra data dictionary.

    returns data group name
    """
    t1 = datetime.now()
    prefix = "background" if background is None else "iter"

    # create background subgroup with index
    fid = h5py.File(output)
    iterindex = max([int(g[len(prefix)+1:]) for g in fid[idobj.name].keys()
                     if g.startswith(prefix)] + [-1]) + 1
    groupName = "{0}_{1:04d}".format(prefix, iterindex)
    grp = fid[idobj.name].create_group(groupName)
    orb0 = ap.getOrbit(spos=True)
    grp["orbit"] = orb0
    tau, I = ap.getLifetimeCurrent()
    grp["lifetime"] = tau
    grp["current"] = I
    if parnames is None:
        parnames = ['gap', 'phase', 'mode']
    else:
        parnames = ['gap', 'phase', 'mode'] + list(parnames)
    parnames = np.unique(parnames).tolist()
    fields = idobj.fields()
    for par in parnames:
        if par in fields:
            grp[par] = idobj.get(par, unitsys=None)
            grp[par].attrs['unitsymb'] = idobj.getUnit(par, unitsys=None)
    for k,v in extdata.items():
        grp[k] = v
    grp.attrs["iter"] = iiter
    if background:
        grp.attrs["background"] = background
    else:
        # Save current ID trim setpoints
        elemflds = createCorrectorField(idobj)
        _, flds = zip(*elemflds)
        trim_sps = [idobj.get(ch, unitsys=None, handle='setpoint') for ch in flds]
        grp['trim_sp'] = trim_sps
        grp['trim_sp'].attrs['fields'] = flds

        # Save current BPM offsets
        try:
            bpm_offset_pvs         = saveState.bpm_offset_pvs
            bpm_offset_pv_suffixes = saveState.bpm_offset_pv_suffixes
            bpm_offset_fields      = saveState.bpm_offset_fields
            bpm_names              = saveState.bpm_names
        except AttributeError:
            bpms = ap.getElements('p[uhlm]*')
            bpm_names = [b.name for b in bpms]
            bpm_pv_prefixes = [b.pv(field='xbba')[0].replace('BbaXOff-SP', '')
                               for b in bpms]
            bpm_offset_fields = ['xbba', 'ybba', 'xref1', 'yref1', 'xref2', 'yref2']
            bpm_offset_pv_suffixes = [
                bpms[0].pv(field=f)[0].replace(bpm_pv_prefixes[0], '')
                for f in bpm_offset_fields]
            bpm_offset_pvs = []
            for suf in bpm_offset_pv_suffixes:
                bpm_offset_pvs += [prefix+suf for prefix in bpm_pv_prefixes]
            saveState.bpm_offset_pvs         = bpm_offset_pvs
            saveState.bpm_offset_pv_suffixes = bpm_offset_pv_suffixes
            saveState.bpm_offset_fields      = bpm_offset_fields
            saveState.bpm_names              = bpm_names
        bpm_offsets = np.array(
            [d.real if d.ok else np.nan
             for d in ap.caget(bpm_offset_pvs, throw=False)]).reshape(
                 (len(bpm_offset_pv_suffixes), -1)).T
        grp.create_dataset('bpm_offsets', data=bpm_offsets, compression='gzip')
        grp['bpm_offsets'].attrs['fields']      = bpm_offset_fields
        grp['bpm_offsets'].attrs['pv_suffixes'] = bpm_offset_pv_suffixes
        grp['bpm_offsets'].attrs['bpm_names']   = bpm_names

    grp.attrs["state_saved"] = t1.strftime("%Y-%m-%d %H:%M:%S.%f")
    fid.close()
    return groupName

def recordMeasCompletion(h5filepath, IDName, groupName):
    """
    Mark the HDF5 group /{IDName}/{groupName}/ as an iteration for which all
    the user-requested measurements have been successfully completed.
    """

    fid = h5py.File(h5filepath)
    grp = fid[IDName][groupName]
    t1 = datetime.now()
    grp.attrs['meas_completed'] = t1.strftime("%Y-%m-%d %H:%M:%S.%f")
    fid.close()


def virtKicks2FldInt(virtK1, virtK2, idLen, idKickOffset1, idKickOffset2, E_GeV):
    """
    Calculate the 1st and 2nd field integrals of an insertion device (ID)
    from the given upstream/downstream virtual kicks.

    Parameters
    ----------
    virtK1, virtK2 : float
       Virtual kick values [rad] at the upsteam and downstream of the ID,
       respectively.

    idLen : float
       Length of the ID [m].

    idKickOffset1, idKickOffset2 : float
       Position offset [m] of virtual kicks with respect to the undulator
       extremeties. `idKickOffset1` == 0 means that the upstream virtual kick
       is exactly located at the upstream entrance of the ID. If `idKickOffset1`
       is a positive value, then the virtual kick is inside of the ID by the
       amount `idKickOffset1`. If negative, the virtual kick is outside of the
       ID by the absolute value of `idKickOffset1`. The same is true for the
       downstream side.

    E_GeV : float
       Electron beam energy [GeV].

    Returns
    -------
    I1 : float
       First field integral [G*m].

    I2 : float
       Second field integral [G*(m^2)].
    """

    Brho = getBrho(E_GeV) # magnetic rigidity [T*m]

    common = Brho * 1e4
    I1 = common * (virtK1 + virtK2) # [G*m]
    I2 = common * ((idLen-idKickOffset1)*virtK1 + idKickOffset2*virtK2) # [G*(m^2)]

    return I1, I2

# <codecell>

def fldInt2VirtKicks(I1, I2, idLen, idKickOffset1, idKickOffset2, E_GeV):
    """
    Calculate upstream/downstream virtual kicks from the given 1st and 2nd field
    integrals of an insertion device (ID).

    Parameters
    ----------
    I1 : float
       First field integral [G*m].

    I2 : float
       Second field integral [G*(m^2)].

    idLen : float
       Length of the ID [m].

    idKickOffset1, idKickOffset2 : float
       Position offset [m] of virtual kicks with respect to the undulator
       extremeties. `idKickOffset1` == 0 means that the upstream virtual kick
       is exactly located at the upstream entrance of the ID. If `idKickOffset1`
       is a positive value, then the virtual kick is inside of the ID by the
       amount `idKickOffset1`. If negative, the virtual kick is outside of the
       ID by the absolute value of `idKickOffset1`. The same is true for the
       downstream side.

    E_GeV : float
       Electron beam energy [GeV].

    Returns
    -------
    virtK1, virtK2 : float
       Virtual kick values [rad] at the upsteam and downstream of the ID,
       respectively.
    """

    Brho = getBrho(E_GeV) # magnetic rigidity [T*m]

    common = 1e-4 / Brho / (idLen-idKickOffset1-idKickOffset2)
    virtK1 = common * (I2 - I1 * idKickOffset2)         # [rad]
    virtK2 = common * (I1 * (idLen-idKickOffset1) - I2) # [rad]

    return virtK1, virtK2

#----------------------------------------------------------------------
def getCompletedIterIndexes(ID_filepath):
    """
    """

    f = h5py.File(ID_filepath, 'r')

    ID_name = f.keys()[0]
    grp = f[ID_name]

    completed_iter_indexes = []
    for k in grp.keys():
        if k.startswith('iter_'):
            if 'meas_completed' in grp[k].attrs.keys():
                completed_iter_indexes.append(grp[k].attrs['iter'])
            elif 'completed' in grp[k].attrs.keys(): # for backward compatibility
                try:
                    completed_iter_indexes.append(grp[k].attrs['iter'])
                except: # for backward compatibility
                    completed_iter_indexes.append(grp[k].attrs['iteration'])

    f.close()

    if completed_iter_indexes != []:
        completed_iter_indexes = np.unique(completed_iter_indexes).tolist()
        #if not np.all(np.diff(completed_iter_indexes) == 1):
            #raise RuntimeError(
                #'List of completed iteration indexes has some missing indexes.')
        #if np.min(completed_iter_indexes) != 0:
            #raise RuntimeError('List of completed iteration indexes does not start from 0.')

    return completed_iter_indexes
