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
         "gap": (119.0, 147.0, 30, 0.01),
         "cch": ("cch0", "cch1", "cch2", "cch3", "cch4", "cch5"),
         "Imin": 2.0, # mA
         "Tmin": 2.0, # hour
         "timeout": 150, },
    "dw100g1c08d":
        {"unitsys": "phy",
         "gap": (119.0, 147.0, 30, 0.01),
         "cch": ("cch0", "cch1", "cch2", "cch3", "cch4", "cch5"),
         "Imin": 2.0, # mA
         "Tmin": 2.0, # hour
         "timeout": 150, },
    "dw100g1c18u":
        {"unitsys": "phy",
         "gap": (119.0, 147.0, 30, 0.01),
         "cch": ("cch0", "cch1", "cch2", "cch3", "cch4", "cch5"),
         "Imin": 2.0, # mA
         "Tmin": 2.0, # hour
         "timeout": 150, },
    "dw100g1c18d":
        {"unitsys": "phy",
         "gap": (119.0, 147.0, 30, 0.01),
         "cch": ("cch0", "cch1", "cch2", "cch3", "cch4", "cch5"),
         "Imin": 2.0, # mA
         "Tmin": 2.0, # hour
         "timeout": 150, },
    "dw100g1c28u":
        {"unitsys": "phy",
         "gap": (119.0, 147.0, 30, 0.01),
         "cch": ("cch0", "cch1", "cch2", "cch3", "cch4", "cch5"),
         "Imin": 2.0, # mA
         "Tmin": 2.0, # hour
         "timeout": 150, },
    "dw100g1c28d":
        {"unitsys": "phy",
         "gap": (119.0, 147.0, 30, 0.01),
         "cch": ("cch0", "cch1", "cch2", "cch3", "cch4", "cch5"),
         "Imin": 2.0, # mA
         "Tmin": 2.0, # hour
         "timeout": 150, },
    }

def putPar(ID, parList, timeout=30, throw=True, unitsys='phy', verbose=0):
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


def putBackground(ID, gapMax, gapTol, zeroPhase, phaseTol, timeout=150,
                  throw=True, unitsys='phy', verbose=False):
    """
    put ID to passive status,
    gap to max, phase to 0 if apply, all correction cch to zeros
    """
    flds = ID.getFields()
    parList = []
    for fld in flds:
        if fld == 'gap':
            parList.append(['gap',gapMax,gapTol])
            continue
        if fld == 'phase':
            parList.append(['phase',zeroPhase,phaseTol])
            continue
        else:
            ID.put(fld,0)
    if putPar(ID,parList,timeout=timeout,
              throw=throw, unitsys=unitsys, verbose=verbose):
        # put correcting coils to zeros
        nIDCor = len(ID.cch)
        for i in range(nIDcor):
            np.put(ID,'cch'+str(i),0)
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

    flds = ID.fields()
    if 'gap' in flds:
        for gap in np.linspace(gapMin,gapMax,gapStep):
            gapList = [['gap',gap,gapTol]]
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
    subg = fid.require_group("parameters")
    subg["scanTable"] = parTable #
    subg["scanTable"].attrs["columns"] = fieldList
    #for p in nameList:
    #    subg["scanTable"].attrs[p] = []
    subg["background"] = [] # like one row of scanTable, same columns
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
