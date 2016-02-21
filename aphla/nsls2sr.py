"""
NSLS2 Storage Ring Specific Routines
============================================

:Author: Lingyun Yang
:Date: 2014-01-27 09:37:41

br - Booster Ring
sr - Storage Ring
"""

import os
import sys
import time
from datetime import datetime
import numpy as np
import h5py
import re
import warnings

import machines
from catools import caget, caput, savePvData, ca_nothing
from catools import putPvData
from hlalib import getElements, outputFileName, getGroupMembers
from hlalib import saveLattice as _saveLattice
from tbtanal import calcFftTune


def _maxTimeSpan(timestamps):
    # take out the part beyond microsecond (nano second + ' EST')
    dtl = [ datetime.strptime(s[:-7], "%Y-%m-%d %H:%M:%S.%f")
            for s in timestamps ]
    if len(dtl) <= 1: return 0
    delta1 = [(t - dtl[0]).total_seconds() for t in dtl]
    # the nano second part
    delta2 = [float(s[-7:-4]) for s in timestamps]
    delta = [delta1[i] + (delta2[i] - delta2[0])*1e-9
             for i in range(len(timestamps))]
    return max(delta) - min(delta)


def getBpmStatus(bpms):
    """
    returns the BPM status.

    bpms : list of BPM object

    it saves
      - event code: `Trig:EventNo-SP`
      - trig source: `Trig:TrigSrc-SP`
      - waveform selection: `DDR:WfmSel-SP`
      - offsets: `ddrAdcOffset`, `ddrTbtOffset`, `ddrFaOffset`
      - burst length: `Burst:AdcEnableLen-SP`, `Burst:TbtEnableLen-SP`, `Burst:FaEnableLen-SP`
      - record length: `ERec:AdcEnableLen-SP`, `ERec:TbtEnableLen-SP`, `ERec:FaEnableLen-SP`

    see also `restoreBpmStatus`
    """
    pvprefs = [e.pv(field="x")[0].replace("Pos:XwUsrOff-Calc", "")
               for e in bpms]
    info = {}
    for pat in ["Trig:TrigSrc-SP", "DDR:WfmSel-SP",
                "ddrAdcOffset", "ddrTbtOffset", "ddrFaOffset",
                "Burst:AdcEnableLen-SP", "Burst:TbtEnableLen-SP", "Burst:FaEnableLen-SP",
                "ERec:AdcEnableLen-SP", "ERec:TbtEnableLen-SP", "ERec:FaEnableLen-SP",
                "Trig:EventNo-SP",]:
        pvs = [pvx + pat for pvx in pvprefs]
        info[pat] = [pvs, caget(pvs, throw=False)]

    return info

def restoreBpmStatus(bpmstats):
    """
    restore BPM status from the output of getBpmStatus

    see also `getBpmStatus`
    """
    for k,v in bpmstats.items():
        v0 = caget(v[0])
        idx = [i for i in range(len(v[1])) if v[1][i] != v0[i]]
        pvs = [v[0][i] for i in idx]
        vals = [v[1][i] for i in idx]
        try:
            caput(pvs, vals, throw = True, timeout=5)
        except:
            for i,pv in numerate(pvs):
                caput(pv, vals, timeout=5)


    
def resetSrBpms(wfmsel = None, name = "BPM", evcode = None, verbose=0, bpms=None, trigsrc = None):
    """
    reset the BPMs to external trigger and Tbt waveform. Offset is 0 for all
    Adc, Tbt and Fa waveforms. The Wfm size is set to 1,000,000 for ADC,
    100,000 for Tbt and 9,000 for Fa.

    Parameters
    -----------
    wfmsel : int, None
        Waveform selection: Adc(0), Tbt(1), Fa(2). default None, keep old values.
    name : str, list of element object
        Element name, group name or list of objects, as in ``getElements``
    bpms : list of element object
        overwrite `name` if presents.
    evcode : int
        Event code: - 15(LINAC), 32(1Hz, sync acquisition), 33(SR RF BPM
        trigger), 47(SR first turn), 66(Booster extraction), 35(pinger).
    trigsrc : int, None
        None - default, keep original values. 0 - internal, 1 - external
    """
    elems = bpms if bpms else [e for e in getElements(name) if e.pv(field="x")]
    pvprefs = [bpm.pv(field="x")[0].replace("Pos:XwUsrOff-Calc", "") for bpm in elems]

    if verbose:
        print "resetting {0} BPMS: {1}".format(len(elems), elems)

    if trigsrc is not None:
        pvs = [ pvx + "Trig:TrigSrc-SP" for pvx in pvprefs ]
        caput(pvs, [trigsrc] * len(pvs), wait=True)
    if wfmsel is not None: 
        # 0 - Adc, 1 - Tbt, 2 - Fa
        pvs = [ pvx + "DDR:WfmSel-SP" for pvx in pvprefs]
        caput(pvs, [wfmsel] * len(pvs), wait=True)

    # enable all three waveforms
    #pvs = [ pvx + "ddrAdcWfEnable" for pvx in pvprefs]
    #caput(pvs, 1, wait=True)
    #pvs = [ pvx + "ddrTbtWfEnable" for pvx in pvprefs]
    #caput(pvs, 1, wait=True)
    #pvs = [  pvx + "ddrFaWfEnable" for pvx in pvprefs]
    #caput(pvs, 1, wait=True)
    #
    pvs = [ pvx + "ddrAdcOffset" for pvx in pvprefs]
    caput(pvs, [0] * len(pvs), wait=True)
    pvs = [ pvx + "ddrTbtOffset" for pvx in pvprefs]
    caput(pvs, [0] * len(pvs), wait=True)
    pvs = [  pvx + "ddrFaOffset" for pvx in pvprefs]
    caput(pvs, [0] * len(pvs), wait=True)
    #
    pvs = [ pvx + "Burst:AdcEnableLen-SP" for pvx in pvprefs]
    caput(pvs, [1000000] * len(pvs), wait=True)
    pvs = [ pvx + "Burst:TbtEnableLen-SP" for pvx in pvprefs]
    caput(pvs,  [100000] * len(pvs), wait=True)
    pvs = [ pvx + "Burst:FaEnableLen-SP" for pvx in pvprefs]
    caput(pvs,    [9000] * len(pvs), wait=True)
    #
    pvs = [ pvx + "ERec:AdcEnableLen-SP" for pvx in pvprefs]
    #if verbose: print pvs
    caput(pvs, [100000] * len(pvs), wait=True)
    pvs = [ pvx + "ERec:TbtEnableLen-SP" for pvx in pvprefs]
    #if verbose: print pvs
    caput(pvs, [100000] * len(pvs), wait=True)
    pvs = [ pvx + "ERec:FaEnableLen-SP" for pvx in pvprefs]
    #if verbose: print pvs
    caput(pvs,   [9000] * len(pvs), wait=True)
    #
    if evcode is not None:
        pvs = [ pvx + "Trig:EventNo-SP" for pvx in pvprefs]
        caput(pvs, evcode, wait=True)


def _srBpmTrigData(pvprefs, waveform, **kwargs):
    """
    """
    offset = kwargs.pop("offset", 0)
    sleep  = kwargs.pop("sleep", 0.5)
    count  = kwargs.pop("count", 0)
    tc = kwargs.get("timeout", 15)
    verbose = kwargs.get("verbose", 0)

    t0 = datetime.now()

    # prepare the triggers
    pv_evg = "SR-BI{BPM}Evt:Single-Cmd"
    pv_trig = []
    pv_wfmsel, pv_adcwfm, pv_tbtwfm, pv_fawfm = [], [], [], []
    pv_adcoffset, pv_tbtoffset, pv_faoffset = [], [], []
    # available data points
    pv_adclen, pv_tbtlen, pv_falen = [], [], []
    # available data points in CA
    pv_adccalen, pv_tbtcalen, pv_facalen = [], [], []
    #
    pv_bbaxoff, pv_bbayoff = [], []
    pv_ddrts = [] # timestamp
    pv_ts, pv_tsns = [], [] # timestamp second and nano sec
    pv_trigts, pv_trigtsns = [], [] # trigger timestamp
    pv_ddrtx = [] # DDR transfer busy
    pv_evtcode = []
    # did not consider the 'ddrTbtWfEnable' PV
    for i,pvx in enumerate(pvprefs):
        #print bpm.name, pvh, caget(pvh)
        #
        pv_bbaxoff.append( pvx + "BbaXOff-SP")
        pv_bbayoff.append( pvx + "BbaYOff-SP")
        # 
        pv_trig.append(  pvx + "Trig:TrigSrc-SP")
        pv_wfmsel.append(pvx + "DDR:WfmSel-SP")
        pv_ddrts.append( pvx + "TS:DdrTrigDate-I")
        #pv_adcwfm.append(pvx + "ddrAdcWfEnable")
        #pv_tbtwfm.append(pvx + "ddrTbtWfEnable")
        #pv_fawfm.append( pvx + "ddrFaWfEnable")
        #
        pv_adcoffset.append(pvx + "ddrAdcOffset")
        pv_tbtoffset.append(pvx + "ddrTbtOffset")
        pv_faoffset.append( pvx + "ddrFaOffset")
        pv_trigts.append(  pvx + "Trig:TsSec-I")
        pv_trigtsns.append(pvx + "Trig:TsOff-I")
        #
        pv_adclen.append(  pvx + "Burst:AdcEnableLen-SP")
        pv_tbtlen.append(  pvx + "Burst:TbtEnableLen-SP")
        pv_falen.append(   pvx + "Burst:FaEnableLen-SP")
        #
        pv_adccalen.append(pvx + "ERec:AdcEnableLen-SP")
        pv_tbtcalen.append(pvx + "ERec:TbtEnableLen-SP")
        pv_facalen.append( pvx + "ERec:FaEnableLen-SP")

        pv_ddrtx.append(pvx + "DDR:TxStatus-I")
        pv_evtcode.append(pvx + "Trig:EventNo-I")

    # save initial val
    wfsel0   = caget(pv_wfmsel, timeout=tc)
    trig0 = caget(pv_trig, timeout=tc)

    # set the trigger internal, TBT waveform
    prf = ""
    if waveform == "Adc":
        caput(pv_wfmsel, 0, wait=True)
        #caput(pv_adcwfm, 1, wait=True)
        caput(pv_adcoffset, 0, wait=True)
        pv_ddroffset = pv_adcoffset
        prf = ""
    elif waveform == "Tbt":
        caput(pv_wfmsel, 1, wait=True)
        #caput(pv_tbtwfm, 1, wait=True)
        caput(pv_tbtoffset, 0, wait=True)
        pv_ddroffset = pv_tbtoffset
        prf = "TBT"
    elif waveform == "Fa":
        caput(pv_wfmsel, 2, wait=True)
        #caput(pv_fawfm,  1, wait=True)
        caput(pv_faoffset, 0, wait=True)
        pv_ddroffset = pv_faoffset
        prf = "FA"
    else:
        raise RuntimeError("unknow waveform '%s'" % waveform)

    pv_x, pv_y, pv_S = [], [], []
    pv_A, pv_B, pv_C, pv_D = [], [], [], []
    for i,pvx in enumerate(pvprefs):
        pv_x.append( pvx + "%s-X" % prf)
        pv_y.append( pvx + "%s-Y" % prf)
        pv_S.append( pvx + "%s-S" % prf)
        pv_A.append( pvx + "%s-A" % prf)
        pv_B.append( pvx + "%s-B" % prf)
        pv_C.append( pvx + "%s-C" % prf)
        pv_D.append( pvx + "%s-D" % prf)

    # set 0 - internal trig, 1 - external trig
    caput(pv_trig, 0, wait=True, timeout=tc)

    # set the event
    caput(pv_evg, 1, wait=True)

    time.sleep(1.2)

    # check timestamp
    n = 0
    while any(caget(pv_ddrtx, timeout=tc)) and n < 20:
        time.sleep(0.5)
        n += 1
    tss_r  = caget(pv_trigts, timeout=tc)
    tss = [t - min(tss_r) for t in tss_r]
    tsns = caget(pv_trigtsns, timeout=tc)
    ts = [s*1e9 + tsns[i] for i,s in enumerate(tss)]
    mdt = max(ts) - min(ts)
    if mdt > 8.0:
        raise RuntimeError("BPMs are not ready after {0} trials, dt={1}: "
                           "{2}\n{3}".format(n, mdt, ts, caget(pv_ddrtx)))

    if verbose > 0:
        print "Trials: %d, Trig=%.2e ns." % (n, mdt)
        print "Sec:", tss_r
        print "dSec: ", [s - min(tss) for s in tss]
        print "dNsec:", [s - min(tsns) for s in tsns]
        print "NSec", tsns

    # redundent check
    #ddrts0 = caget(pv_ddrts)
    ddrts0 = [datetime.fromtimestamp(v).strftime("%m/%d/%Y,%H:%M:%S") +
              ".%09d" % tsns[i] for i,v in enumerate(tss_r)]
    ddroffset = caget(pv_ddroffset, timeout=tc)
    data = (caget(pv_x, count=count), caget(pv_y, count=count),
            caget(pv_S, count=count))
    xbbaofst = caget(pv_bbaxoff, timeout=tc)
    ybbaofst = caget(pv_bbayoff, timeout=tc)
    #
    # set 0 - internal trig, 1 - external trig
    #caput(pv_trig, 1, wait=True)
    caput(pv_wfmsel, wfsel0, wait=True, timeout=tc)
    caput(pv_trig, trig0, wait=True, timeout=tc)
    ext_data = {
        "ddr_timestamp": ddrts0,
        "ddr_offset": ddroffset,
        "bba_xoffset": xbbaofst,
        "bba_yoffset": ybbaofst,
        "event_code": caget(pv_evtcode)}
    #return data[0], data[1], data[2], ddrts0, ddroffset, ts
    return (data[0], data[1], data[2], ext_data)
    #ddrts0, ddroffset, xbbaofst, ybbaofst, ext_data


def _saveSrBpmData(fname, waveform, names, x, y, Is, **kwargs):
    """
    kwargs:
      - bba_x_offset, bba_y_offset
      - event
    """
    group = kwargs.get("h5group", "/")
    dcct_data = kwargs.get("dcct_data", None)
    pvpref = kwargs.get("pvpref", None)

    # open with default 'a' mode: rw if exists, create otherwise
    h5f = h5py.File(fname)
    if group != "/":
        grp = h5f.create_group(group)
    grp = h5f[group]
    grp["%s_name" % waveform]   = names
    grp["%s_x" % waveform]      = x
    grp["%s_y" % waveform]      = y
    grp["%s_sum" % waveform]    = Is
    if "ddr_timestamp" in kwargs:
        grp["%s_ts" % waveform] = kwargs["ddr_timestamp"]
    if "ddr_offset" in kwargs:
        grp["%s_offset" % waveform] = kwargs["ddr_offset"]

    for k in ["bba_xoffset", "bba_yoffset", "event_code", "note"]:
        if k in kwargs:
            grp[k] = kwargs[k]
    #grp.attrs["timespan"] = _maxTimeSpan(data[4])

    if dcct_data:
        for i,d in enumerate(dcct_data):
            grp["dcct_%d" % i] = np.array(d, 'd')
    for i,t in enumerate(kwargs.get("ts", [])):
        grp.attrs["%s_t%d" % (waveform,i)] = t.strftime("%Y_%m_%d_%H%M%S.%f")

    if pvpref is not None:
        pvs = [ p + "DDR:WfmSel-SP" for p in pvpref]
        grp["wfm_type"] = np.array(caget(pvs), 'i')
        #pvs = [ p + "ddrAdcWfEnable" for p in pvpref]
        #grp["wfm_Adc_enabled"] = np.array(caget(pvs), 'i')
        #pvs = [ p + "ddrTbtWfEnable" for p in pvpref]
        #grp["wfm_Tbt_enabled"] = np.array(caget(pvs), 'i')
        #pvs = [ p + "ddrFaWfEnable" for p in pvpref]
        #grp["wfm_Fa_enabled"] = np.array(caget(pvs), 'i')

    h5f.close()


def getSrBpmData(**kwargs):
    """
    NSLS-II SR BPM data acquisition.

    Parameters
    -----------
    trig : int, optional
        Internal(0) or external(1) trigger. trig=1 will not set the trig PV.
    verbose : int
    waveform : str
        Waveform selection: ``"Tbt"``, ``"Fa"``
    bpms : list
        A list of BPM object.
    name : str
        BPM name or pattern, overwritten by parameter *bpms*
    count : int
        Waveform length. default all (0).
    output : str, True, False
        output file name, or default name (True), or no output (False).
    h5group : str
        output HDF5 group

    Returns
    --------
    name : list
        a list of BPM name
    x : array (nbpm, count)
        x orbit, shape (nbpm, waveform_length).
    y : array (nbpm, count)
        y orbit
    Isum : array (nbpm, count)
        Sum signal
    timestamp : list
    offset : list
        offset from the FPGA buffer.

    There will be warning if timestamp differs more than 1 second
    """
    trig_src = kwargs.get("trig", 0)
    verbose  = kwargs.get("verbose", 0)
    waveform = kwargs.pop("waveform", "Tbt")
    name     = kwargs.pop("bpms", kwargs.pop("name", "BPM"))
    count    = kwargs.get("count", 0)
    #timeout  = kwargs.get("timeout", 6)
    output   = kwargs.get("output", None)
    timeout  = kwargs.get("timeout", 30)

    lat = machines.getLattice()
    if lat.name != "SR":
        raise RuntimeError("the current lattice is not 'BR': %s" % lat.name)

    t0 = datetime.now()

    #pv_dcct = "BR-BI{DCCT:1}I-Wf"
    #dcct1 = caget(pv_dcct, count=1000)
    elems = [e for e in getElements(name) if e.pv(field="x")]
    pvpref = [bpm.pv(field="x")[0].replace("Pos:XwUsrOff-Calc", "")
              for bpm in elems]
    names = [bpm.name for bpm in elems]

    if trig_src == 0 and waveform in ["Tbt", "Fa"]:
        # wait while waveform is transmitting data
        while any(caget([p + "DDR:TxStatus-I" for p in pvpref])):
            if (datetime.now() - t0).total_seconds() > timeout:
                raise RuntimeError("timeout after {0} seconds".format(timeout))
            time.sleep(1)

        # internal trig
        # ret = _srBpmTrigData(pvpref, waveform, **kwargs)
        # x, y, Is, ts, offset, xbbaofst, ybbaofst, extdata = ret
        x, y, Is, extdata = _srBpmTrigData(pvpref, waveform, **kwargs)
    else:
        if waveform == "Tbt":
            pv_x = [pv + "TBT-X" for pv in pvpref]
            pv_y = [pv + "TBT-Y" for pv in pvpref]
            pv_S = [pv + "TBT-S" for pv in pvpref]
            pv_offset = [pv + "ddrTbtOffset" for pv in pvpref]
        elif waveform == "Fa":
            pv_x = [pv + "FA-X" for pv in pvpref]
            pv_y = [pv + "FA-Y" for pv in pvpref]
            pv_S = [pv + "FA-S" for pv in pvpref]
            pv_offset = [pv + "ddrFaOffset" for pv in pvpref]

        pv_ts = [pv + "TS:DdrTrigDate-I" for pv in pvpref]
        pv_bbaxoff = [ pv + "BbaXOff-SP" for pv in pvpref]
        pv_bbayoff = [ pv + "BbaYOff-SP" for pv in pvpref]
        pv_evtcode = [ pv + "Trig:EventNo-I" for pv in pvpref]

        x  = caget(pv_x, count=count, throw=False)
        y  = caget(pv_y, count=count, throw=False)
        Is = caget(pv_S, count=count, throw=False)
        # check srBpmTrigData, key must agrees
        extdata = {
            "ddr_timestamp": np.array(caget(pv_ts)),
            "ddr_offset": np.array(caget(pv_offset), 'i'),
            "bba_xoffset": np.array(caget(pv_bbaxoff)),
            "bba_yoffset": np.array(caget(pv_bbayoff)),
            "event_code": np.array(caget(pv_evtcode))}
    # in case they have difference size
    d = []
    for v in [x, y, Is]:
        nx = max([len(r) for r in v if not isinstance(r, ca_nothing)])
        rec = np.zeros((len(v), nx), 'd')
        for i in range(len(v)):
            rec[i,:len(v[i])] = v[i]
        d.append(rec)
    x, y, Is = d
    # get dcct
    #dcct2 = caget(pv_dcct, count=1000)
    #t1 = datetime.now()

    data = (names, x, y, Is, extdata["ddr_timestamp"], extdata["ddr_offset"])

    if not output: return data
    
    if output is True:
        # use the default file name
        output_dir = os.path.join(machines.getOutputDir(),
                                  t0.strftime("%Y_%m"),
                                  "bpm")
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        fopt = "bpm_%s_%d_" % (waveform, trig_src) + \
            t0.strftime("%Y_%m_%d_%H%M%S.hdf5")
        output = os.path.join(output_dir, fopt)

    t1 = datetime.now()
    # save the data
    _saveSrBpmData(output, waveform, names, x, y, Is,
                   h5group=kwargs.get("h5group", "/"),
                   ts = (t0, t1),
                   pvpref = pvpref,
                   **extdata)
    return data, output


def saveLattice(**kwargs):
    """
    save the current lattice info to a HDF5 file.

    Parameters
    -----------
    lattice : Lattice
        lattice object, default the current active lattice
    subgroup : str, default ""
        used for output file name
    note : str, default ""  (notes is deprecated)
    unitsys : str, None
        default "phy", 

    Returns
    -------
    out : str
        the output file name.

    Saved data with unitsys=None and "phy":

    - Magnet: BEND: b0, db0; QUAD: b1; SEXT: b2; COR: x, y;
    - BPM and UBPM: x, x0, xbba, xref0, xref1 (same for y)
    - RFCAVITY: f
    - DCCT: I, tau, Iavg

    Notes
    ------
    Besides all SR PVs, there are some BTS pvs saved without physics
    properties. The saved file does not known if the BTS pvs are readback or
    setpoint. This makes `putLattice` more safe when specifying put setpoint
    pvs only.

    Examples
    ---------
    >>> saveLattice(note="Good one")
    """
    # save the lattice
    output = kwargs.pop("output", 
                        outputFileName("snapshot", kwargs.get("subgroup","")))
    lat = kwargs.get("lattice", machines._lat)
    verbose = kwargs.get("verbose", 0)
    unitsys = kwargs.get("unitsys", "phy")
    notes = kwargs.pop("note", kwargs.pop("notes", ""))

    elemflds = [("BEND", ("b0", "db0")),
                ("QUAD", ("b1",)),
                ("SEXT", ("b2",)),
                ("COR", ("x", "y")),
                ("BPM", ("x", "y", "x0", "y0", "xbba", "ybba",
                         "xref0", "xref1", "yref0", "yref1", "ampl")),
                ("UBPM", ("x", "y", "x0", "y0", "xbba", "ybba",
                         "xref0", "xref1", "yref0", "yref1", "ampl")),
                ("RFCAVITY", ("f", "v", "phi")),
                ("DCCT", ("I", 'tau', "Iavg"))]
    t0 = datetime.now()
    nlive, ndead = _saveLattice(
        output, lat, elemflds, notes, **kwargs)

    h5f = h5py.File(output)
    h5g = h5f[lat.name]
    nameinfo = {}
    for elfam,flds in elemflds:
        for e in lat.getElementList(elfam, virtual=False):
            for fld in flds:
                for pv in e.pv(field=fld):
                    els = nameinfo.setdefault(pv, [])
                    els.append("%s.%s" % (e.name, fld)) 
                if not e.convertible(fld, None, unitsys): continue
                uname = e.getUnit(fld, unitsys=unitsys)
                pvsp = e.pv(field=fld, handle="setpoint")
                pvrb = e.pv(field=fld, handle="readback")
                for pv in pvsp + pvrb:
                    d0 = h5g[pv].value
                    d1 = e.convertUnit(fld, d0, None, unitsys)
                    s = "%s.%s.%s[%s]" % (e.name, fld, unitsys, uname)
                    h5g[pv].attrs[s] = d1
                for pv in pvsp:
                    h5g[pv].attrs["setpoint"] = 1

    for pv,els in nameinfo.items():
        h5g[pv].attrs["element.field"] = els

    t1 = datetime.now()
    try:
        import getpass
        h5g.attrs["_author_"] = getpass.getuser()
    except:
        pass
    h5g.attrs["t_start"] = t0.strftime("%Y-%m-%d %H:%M:%S.%f")
    h5g.attrs["t_end"] = t1.strftime("%Y-%m-%d %H:%M:%S.%f")

    h5f.close()
    
    return output


def putLattice(fname, **kwargs):
    """
    restore saved machine snapshot.

    Parameters
    -----------
    fname : str
        The data file name

    See also
    ---------
    saveLattice, compareLattice

    Examples
    ---------
    >>> output = saveLattice(note="example")
    >>> putLattice(output)
    """
    putPvData(fname, machines._lat.name, **kwargs)


def measKickedTbtData(idriver, ampl, **kwargs):
    """
    take turn-by-turn BPM data after kicking the beam.

    Parameters
    -----------
    idriver : int
        which driver used to kick the beam: injection kicker 3(3) or 4(4),
        vertical pinger(5), horizontal pinger(6), both H/V pingers(7).
    ampl : float, tuple
        kicking amplitude.
    bpms : list of element objects.
        provide the BPMs to take data from, default ["BPM" or "UBPM"]
    count : int
        number of turns.
    output : str, True, False
        output file name, or default (True), or no output (False)
    verbose : int

    it will set kicker/pinger and wait 100sec or readback-setpoint agree.

    event code 47 will be used for kicker 3 and 4, 35 used for pingers.

    Same returns as `getSrBpmData`

    Examples
    ---------
    >>> (name, x, y, Isum, ts, offset) = measKickedTbtData(7, (0.15, 0.2))
    >>> (name, x, y, Isum, ts, offset), output = measKickedTbtData(7, (0.15, 0.2), output=True)
    """

    verbose = kwargs.get("verbose", 0)
    output = kwargs.get("output", True)
    sleep = kwargs.get("sleep", 5)
    count = kwargs.get("count", 2000)
    timeout = kwargs.get("timeout", 60)

    bpms  = [ b for b in kwargs.get("bpms",
                                   getGroupMembers(["BPM", "UBPM"], op="union"))
              if b.isEnabled()]

    bpmstats = getBpmStatus(bpms)

    # AC contactor has to be on
    if caget("SR:C21-PS{Pinger:H}AcOnOff_Cmd") == 0 or \
            caget("SR:C21-PS{Pinger:V}AcOnOff_Cmd") == 0:
        raise RuntimeError("AC Contactors are off now")

    kpvsp, kpvrb = None, None
    # 0 - both off, 1 - V-on, 2-H-on, 3-both-on
    pv_pinger_mode = "SR:C21-PS{Pinger}Mode:Trig-Sel"
    if idriver in [3,4,5,6]:
        if idriver in [3, 4]:
            kpvsp = 'SR:IS-PS{Kick:%d}V-Sp' % idriver
            kpvrb = 'SR:IS-PS{Kick:%d}Hvps-V-Rb-1st' % idriver
            kpvon = 'SR:IS-PS{Kick:%d}HvpsOnOff_Cmd' % idriver
        elif idriver in [5,]:
            # vertical pinger
            kpvsp = 'SR:C21-PS{Pinger:V}V-Sp'
            kpvrb = 'SR:C21-PS{Pinger:V}Setpoint-Rb.VALA'
            kpvon = 'SR:C21-PS{Pinger:V}HvpsOnOff_Cmd'
            caput(pv_pinger_mode, 1)
        elif idriver in [6,]:
            # horizontal pinger
            kpvsp = 'SR:C21-PS{Pinger:H}V-Sp'
            kpvrb = 'SR:C21-PS{Pinger:H}Setpoint-Rb.VALA'
            kpvon = 'SR:C21-PS{Pinger:H}HvpsOnOff_Cmd'
            caput(pv_pinger_mode, 2)
        #
        caput(kpvsp, 0.0)
        for i in range(100):
            if caget(kpvrb, count=1) < 0.001: break
            time.sleep(1)
        caput(kpvon, 1)
    elif idriver in [7,]:
        # both pinger
        kpvsp = ['SR:C21-PS{Pinger:H}V-Sp', 'SR:C21-PS{Pinger:V}V-Sp']
        kpvrb = ['SR:C21-PS{Pinger:H}Setpoint-Rb.VALA', 'SR:C21-PS{Pinger:V}Setpoint-Rb.VALA']
        kpvon = ['SR:C21-PS{Pinger:H}HvpsOnOff_Cmd', 'SR:C21-PS{Pinger:V}HvpsOnOff_Cmd']
        caput(pv_pinger_mode, 3)
        caput(kpvsp, [0.0, 0.0])
        for i in range(100):
            rb = caget(kpvrb, count=1)
            if rb[0] < 0.001 and rb[1] < 0.001: break
            time.sleep(0.5)
        caput(kpvon, [1, 1])

    # set the kicker/pinger voltage
    caput(kpvsp, ampl, wait=True)
    #(name, x, y, Isum, ts, offset), output = ap.nsls2.getSrBpmData(
    #    trig=1, count=5000, output=True, h5group="k_%d" % idriver)
    h5g = "k_%d" % idriver
    Idcct0 = caget('SR:C03-BI{DCCT:1}I:Total-I')
    time.sleep(sleep)

    # request an injection:
    if idriver in [3,4,]:
        resetSrBpm(bpms=bpms, evcode=47)
        time.sleep(1)
        caput('ACC-TS{EVG-SSC}Request-Sel', 1)
    elif idriver in [5,6,7]:
        resetSrBpms(bpms=bpms, evcode=35)
        # do it twice
        caput('SR:C21-PS{Pinger}Ping-Cmd', 1)
        time.sleep(1)
        caput('SR:C21-PS{Pinger}Ping-Cmd', 1)
    time.sleep(2)
    Idcct1 = caget('SR:C03-BI{DCCT:1}I:Total-I')
    bpmdata = getSrBpmData(trig=1, bpms=bpms, count=count,
                           output=output, h5group=h5g, timeout=timeout)
    # record pinger wave, V-chan1, H-chan2
    pinger_delay, pinger_wave, pinger_mode = None, None, None
    if idriver in [5,6,7]:
        pinger_wave = caget(["SR:C21-PS{Dig:Png1}TimeScale-I",
                             "SR:C21-PS{Dig:Png1}Data:Chan2-I",
                             "SR:C21-PS{Dig:Png1}Data:Chan1-I"])
        pinger_delay = caget(["SR:C21-PS{Pinger:H}Delay-SP",
                              "SR:C21-PS{Pinger:V}Delay-SP"])
        pinger_mode = caget("SR:C21-PS{Pinger}Mode:Trig-Sts")
        
    # repeat_value=True
    caput(kpvon, 0)
    caput(kpvsp, 0.0)
    
    if output:
        (name, x, y, Isum, ts, offset), output = bpmdata
        
        f = h5py.File(output)
        g = f[h5g]
        g["I"]  = Idcct1
        g["I"].attrs["dI"] = Idcct1 - Idcct0
        g["RF_SP"] = float(caget('RF{Osc:1}Freq:SP'))
        g["RF_I"]  = float(caget('RF{Osc:1}Freq:I'))
        g.attrs["ampl"]  = ampl
        g.attrs["idriver"] = idriver
        g.attrs["pvsp"] = kpvsp
        g.attrs["pvrb"] = kpvrb
        g.attrs["pvon"] = kpvon
        if pinger_wave is not None:
            g["pinger_wave"] = np.array(pinger_wave, 'd').transpose()
        if pinger_delay is not None:
            g["pinger_delay"] = pinger_delay
        if pinger_mode is not None:
            g["pinger_mode"] = pinger_mode
        f.close()

    # restore
    restoreBpmStatus(bpmstats)

    return bpmdata

def measTbtTunes(idrive = 7, ampl = (0.15, 0.2), sleep=3, count=5000):
    names, x0, y0, Isum0, timestamp, offset = \
        measKickedTbtData(idrive, ampl, sleep=sleep, output=False, count=count)
    return calcFftTune(x0), calcFftTune(y0)


def measFaPsd(count=5000, nfft=4096, sleep=3, output=False, h5group="/", note=""):
    # trig=0 is internal, trig=1 is external
    if output:
        (names, x0, y0, Isum0, timestamp, offset), output = \
            getSrBpmData(waveform="Fa",trig=1, count=count, output=output, h5group=h5group)
    else:
        names, x0, y0, Isum0, timestamp, offset = \
            getSrBpmData(waveform="Fa",trig=1, count=count, output=False)
        output = None
    # adjust the offset, align to the original zero
    nbpm, nturns = np.shape(Isum0)
    from scipy import signal
    # 10khz, f=1e4
    Pfx = [signal.periodogram(x0[i,:] - np.average(x0[i,:]), 1e4, nfft=nfft)
          for i in range(nbpm)]
    Pfy = [signal.periodogram(y0[i,:] - np.average(y0[i,:]), 1e4, nfft=nfft)
          for i in range(nbpm)]
    Px = np.array([pf[1] for pf in Pfx], 'd')
    Py = np.array([pf[1] for pf in Pfy], 'd')
    if output:
        pvs = ['SR:C03-BI{DCCT:1}I:Total-I', 'SR:FOFB{}FOFBOn',
               'SR:C16-BI{FPM:2}BunchQ-Wf',
               "SR-FOFB{}Kp1", "SR-FOFB{}Ki1", ]
        h5f = h5py.File(output)
        h5f["DCCT"] = caget('SR:C03-BI{DCCT:1}I:Total-I')
        h5f["FOFB"] = caget('SR:FOFB{}FOFBOn')
        h5f["fillpattern"] = caget('SR:C16-BI{FPM:2}BunchQ-Wf')
        for i,vi in enumerate(caget(pvs)):
            h5f[pvs[i]] = vi
        h5f.close()

    return Pfx[0][0], Px, Py, output

