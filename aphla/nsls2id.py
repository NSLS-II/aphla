"""
NSLS-II insertion device commissioning/operation

copyright (C) 2014, Yongjun Li, Yoshi Hidaka, Lingyun Yang
"""

import aphla as ap
import itertools
import numpy as np
import re

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


def createParList(parRange):
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
    for p in parRange:
        nlist.append(p[0])
        if p[1] == 'linear':
            vlist.append(list(np.linspace(p[2],p[3],int(p[4]))))
        elif p[1] == 'log':
            if p[2]<=0 or p[3]<=0:
                raise RuntimeError('negative boundary can not be spaced Logarithmically')
            else:
                vlist.append(list(np.logspace(np.log10(p[2]),np.log10(p[3]),int(p[4]))))
        else:
            raise RuntimeError('unknown spaced pattern: %s'%p[1])
        tlist.append(p[5])
    valueList = itertools.product(*vlist)
    parList = []
    for v in valueList:
        tmp = []
        for i,n in enumerate(nlist):
            tmp.append([n,v[i],tlist[i]])
        parList.append(tmp)
    valueList = itertools.product(*vlist)
    table = np.array([vi for vi in valueList])
    return parList, nlist, vlist, table


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


def checkGapPhase(ID, gapMin, gapMax, gapStep, gapTol,
                  phaseMin=None, phaseMax=None, phaseStep=3, phaseTol=None,
                  timeout=150, throw=True, unitsys='phy', verbose=True):
    """
    check ID gap, phase
    return True if success, otherwise False
    """
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

def initFile(ID, nameList, parTable, Imin, Tmin):
    """initilize file name with path, save parameter table to hdf5"""
    fileName = ap.outputFileName("ID", ID.name+"_")
    fid = h5py.File(fileName)
    grp = fid.require_group(ID.name)
    grp.attrs["__FORMAT__"] = 1
    # setup parameters
    subg = fid.require_group("parameters")
    subg["scanTable"] = parTable #
    subg["scanTable"].attrs["columns"] = nameList
    #for p in nameList:
    #    subg["scanTable"].attrs[p] = []
    subg["background"] = [] # like one row of scanTable, same columns
    subg["background"].attrs["columns"] = parName
    # timestamp ISO "2007-03-01 13:00:00"
    subg["minCurrent"] = Imin
    subg["minCurrent"].attrs["unit"] = "mA"
    subg["minLifetime"] = Tmin
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
