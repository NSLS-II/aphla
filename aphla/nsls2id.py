"""
NSLS-II insertion device commissioning/operation

copyright (C) 2014, Yongjun Li, Yoshi Hidaka, Lingyun Yang
"""

import aphla as ap
import itertools
import numpy as np
import re
import h5py
from datetime import datetime

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
         "cch": ("cch0", "cch1", "cch2", "cch3", "cch4", "cch5"),
         "background": {"gap": 240.0},
         "Imin": 0.2, # mA
         "Tmin": 0.2, # hour
         "timeout": 180, },
    "epu49g1c23d":
        {"unitsys": "phy",
         "gap": (11.5, 240.0, 30, 0.1),
         "cch": ("cch0", "cch1", "cch2", "cch3", "cch4", "cch5"),
         "background": {"gap": 240.0},
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
         "cch": ("cch0", "cch1", "cch2", "cch3", "cch4", "cch5"),
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

# <codecell>

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
        ap.caput("SR:C23-ID:G1A{EPU:1-FF:0}Ena-Sel", val)
        ap.caput("SR:C23-ID:G1A{EPU:1-FF:1}Ena-Sel", val)
        ap.caput("SR:C23-ID:G1A{EPU:1-FF:2}Ena-Sel", val)
        ap.caput("SR:C23-ID:G1A{EPU:1-FF:3}Ena-Sel", val)
        ap.caput("SR:C23-ID:G1A{EPU:1-FF:4}Ena-Sel", val)
        ap.caput("SR:C23-ID:G1A{EPU:1-FF:5}Ena-Sel", val)
    elif ID.name == "dw100g1c28u":
        ap.caput("SR:C28-ID:G1{DW100:1-FF:0}Ena-Sel", val)
        ap.caput("SR:C28-ID:G1{DW100:1-FF:1}Ena-Sel", val)
        ap.caput("SR:C28-ID:G1{DW100:1-FF:2}Ena-Sel", val)
        ap.caput("SR:C28-ID:G1{DW100:1-FF:3}Ena-Sel", val)
        ap.caput("SR:C28-ID:G1{DW100:1-FF:4}Ena-Sel", val)
        ap.caput("SR:C28-ID:G1{DW100:1-FF:5}Ena-Sel", val)
    elif ID.name == "dw100g1c28d":
        ap.caput("SR:C28-ID:G1{DW100:2-FF:0}Ena-Sel", val)
        ap.caput("SR:C28-ID:G1{DW100:2-FF:1}Ena-Sel", val)
        ap.caput("SR:C28-ID:G1{DW100:2-FF:2}Ena-Sel", val)
        ap.caput("SR:C28-ID:G1{DW100:2-FF:3}Ena-Sel", val)
        ap.caput("SR:C28-ID:G1{DW100:2-FF:4}Ena-Sel", val)
        ap.caput("SR:C28-ID:G1{DW100:2-FF:5}Ena-Sel", val)

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
    if parTable and fieldList:
        subg["scanTable"] = parTable #
        subg["scanTable"].attrs["columns"] = fieldList
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


def saveState(idobj, output, iiter,
              parnames = ["gap"], background=None, extdata={}):
    """
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
    for par in parnames:
        grp[par] = idobj.get(par, unitsys=None)
    for k,v in extdata.items():
        grp[k] = v
    grp.attrs["iter"] = iiter
    if background:
        grp.attrs["background"] = background
    grp.attrs["completed"] = t1.strftime("%Y-%m-%d %H:%M:%S.%f")
    fid.close()
    return groupName


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


def save1DFeedFowardTable(filepath, table, fmt='%.16e'):
    """
    Save a valid 1-D Stepped Feedforward table (NSLS-II format) to a text file.
    """

    np.savetxt(filepath, table, fmt=fmt, delimiter=', ', newline='\n')

def get1DFeedForwardTable(centers, half_widths, dI_array, 
                          I0_array=None, fmt='%.16e'):
    """
    Get a valid 1-D Stepped Feedforward table (NSLS-II format)
    """
    
    if I0_array is None:
        I_array = dI_array
    else:
        I_array = I0_array + dI_array

    table = np.hstack((np.array(centers).reshape((-1,1)),
                       np.array(half_widths).reshape((-1,1)),
                       I_array))

    return table    
    
def getZeroed1DFeedForwardTable(parDict, nIDCor):
    """
    Get a valid 1-D Stepped Feedforward table (NSLS-II format) with
    all ID correctors being set to zero for all the entire range of
    ID property specified in "parDict".
    """

    try:
        scanVectors = parDict['vectors']
        bkgList = parDict['bkgTable'].flatten().tolist()
        
        assert len(scanVectors) == len(bkgList) == 1
    except:
        print 'len(scanVectors) = {0:d}'.format(len(scanVectors))
        print 'len(bkgList) = {0:d}'.format(len(bkgList))
        print 'This function is only for 1D feedforward table.'
        raise RuntimeError(('Lengths of "scanVectors" and "bkgList" must be 1.'))

    array = scanVectors[0] + [bkgList[0]]
    minVal, maxVal = np.min(array), np.max(array)

    centers = [(minVal + maxVal) / 2.0]
    half_widths = [(maxVal - minVal) / 2.0 * 1.01] # Extra margin of 1% added
    dI_array = np.array([0.0]*nIDCor).reshape((1,-1))
    
    return get1DFeedForwardTable(centers, half_widths, dI_array, 
                                 I0_array=None, fmt='%.16e')
        

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
    """
    """

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
