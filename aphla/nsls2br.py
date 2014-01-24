"""
NSLS2 Booster Ring Specific Routines
============================================

:Author: Lingyun Yang
:Date: 2014-01-24 10:42:08

br - Booster Ring
"""
import os
import sys
import time
from datetime import datetime
import numpy as np
import h5py
import re

from cothread.catools import caget, caput

import matplotlib.pylab as plt
from nsls2 import _maxTimeSpan

def resetBrBpms(wfmsel = 1):
    """
    reset the BPMs to external trigger and Tbt waveform. Offset is 0 for all
    Adc, Tbt and Fa waveforms.
    """
    pvprefs = [bpm.pv(field="x")[0].replace("Pos:X-I", "")
               for bpm in ap.getElements("BPM")]
    for i,pvx in enumerate(pvprefs):
        pvs = [ pvx + "Trig:TrigSrc-SP" for pvx in pvprefs]
        ap.catools.caput(pvs, 1, wait=True)
        # 0 - Adc, 1 - Tbt, 2 - Fa
        pvs = [ pvx + "DDR:WfmSel-SP" for pvx in pvprefs]
        ap.catools.caput(pvs, wfmsel, wait=True)
        # enable all three waveforms
        pvs = [ pvx + "ddrAdcWfEnable" for pvx in pvprefs]
        ap.catools.caput(pvs, 1, wait=True)
        pvs = [ pvx + "ddrTbtWfEnable" for pvx in pvprefs]
        ap.catools.caput(pvs, 1, wait=True)
        pvs = [  pvx + "ddrFaWfEnable" for pvx in pvprefs]
        ap.catools.caput(pvs, 1, wait=True)
        #
        pvs = [ pvx + "ddrAdcOffset" for pvx in pvprefs]
        ap.catools.caput(pvs, 0, wait=True)
        pvs = [ pvx + "ddrTbtOffset" for pvx in pvprefs]
        ap.catools.caput(pvs, 0, wait=True)
        pvs = [  pvx + "ddrFaOffset" for pvx in pvprefs]
        ap.catools.caput(pvs, 0, wait=True)
        #
    
def _brBpmTrigData(pvprefs, waveform, **kwargs):
    """
    """
    offset = kwargs.pop("offset", 0)
    sleep  = kwargs.pop("sleep", 0.5)
    tc = kwargs.get("timeout", 6)
    verbose = kwargs.get("verbose", 0)

    t0 = datetime.now()

    # prepare the triggers
    pv_evg = "BR-BI{BPM}Evt:Single-Cmd"
    pv_trig = []
    pv_wfmsel, pv_adcwfm, pv_tbtwfm, pv_fawfm = [], [], [], []
    pv_adcoffset, pv_tbtoffset, pv_faoffset = [], [], []
    pv_ddrts = [] # timestamp
    pv_ts, pv_tsns = [], [] # timestamp second and nano sec
    pv_trigts, pv_trigtsns = [], [] # trigger timestamp
    # did not consider the 'ddrTbtWfEnable' PV
    for i,pvx in enumerate(pvprefs):
        #print bpm.name, pvh, caget(pvh)
        pv_trig.append(  pvx + "Trig:TrigSrc-SP")
        pv_wfmsel.append(pvx + "DDR:WfmSel-SP")
        pv_ddrts.append( pvx + "TS:DdrTrigDate-I")
        pv_adcwfm.append(pvx + "ddrAdcWfEnable")
        pv_tbtwfm.append(pvx + "ddrTbtWfEnable")
        pv_fawfm.append( pvx + "ddrFaWfEnable")
        #
        pv_adcoffset.append(pvx + "ddrAdcOffset")
        pv_tbtoffset.append(pvx + "ddrTbtOffset")
        pv_faoffset.append( pvx + "ddrFaOffset")
        pv_ts.append(  pvx + "Trig:TsSec-I")
        pv_tsns.append(pvx + "Trig:TsOff-I")
        pv_trigts.append(  pvx + "Trig:TsSec-I")
        pv_trigtsns.append(pvx + "Trig:TsOff-I")
        #

    # save initial val
    wfsel0   = ap.catools.caget(pv_wfmsel, timeout=tc)
    trig0 = ap.catools.caget(pv_trig, timeout=tc)

    # set the trigger internal, TBT waveform
    prf = ""
    if waveform == "Adc":
        ap.catools.caput(pv_wfmsel, 0, wait=True)
        ap.catools.caput(pv_adcwfm, 1, wait=True)
        ap.catools.caput(pv_adcoffset, 0, wait=True)
        pv_ddroffset = pv_adcoffset
        prf = ""
    elif waveform == "Tbt":
        ap.catools.caput(pv_wfmsel, 1, wait=True)
        ap.catools.caput(pv_tbtwfm, 1, wait=True)
        ap.catools.caput(pv_tbtoffset, 0, wait=True)
        pv_ddroffset = pv_tbtoffset
        prf = "TBT"
    elif waveform == "Fa":
        ap.catools.caput(pv_wfmsel, 2, wait=True)
        ap.catools.caput(pv_fawfm,  1, wait=True)
        ap.catools.caput(pv_faoffset, 0, wait=True)
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
    ap.catools.caput(pv_trig, 0, wait=True, timeout=tc)

    # set the event
    ap.catools.caput(pv_evg, 1, wait=True)

    time.sleep(1.2)

    # check timestamp
    n = 0
    while True:
        tss_r  = ap.catools.caget(pv_trigts, timeout=tc)
        tss = [t - min(tss_r) for t in tss_r]
        tsns = ap.catools.caget(pv_trigtsns, timeout=tc)
        ts = [s + 1.0e-9*tsns[i] for i,s in enumerate(tss)]
        mdt = max(ts) - min(ts)
        ddrts0 = ap.catools.caget(pv_ddrts)
        mdt_s  = _maxTimeSpan(ap.catools.caget(pv_ddrts, timeout=tc))
        n = n + 1
        if mdt < 1.0 and mdt_s < 1.0:
            #print "Max dt=", mdt, mdt_s, "tried %d times" % n
            break
        time.sleep(0.5)
        # quit if failed too many times
        if n > 20:
            ap.catools.caput(pv_trig, [1] * len(pv_trig), wait=True)
            raise RuntimeError("BPMs are not ready after %d trials" % n)

    if verbose > 0:
        print "Trials: %d, Trig=%.2e, DDR Trig=%.2e seconds." % (n, mdt, mdt_s)

    # redundent check
    ddrts0   = ap.catools.caget(pv_ddrts, timeout=tc)
    mdt = _maxTimeSpan(ddrts0)
    if mdt > 1.0:
        print "ERROR: Timestamp does not agree (max dt= %f), wait ..." % mdt

    ddroffset = ap.catools.caget(pv_ddroffset, timeout=tc)
    data = (ap.catools.caget(pv_x),
            ap.catools.caget(pv_y),
            ap.catools.caget(pv_S))
    #
    data = np.array(data, 'd')

    # set 0 - internal trig, 1 - external trig
    ap.catools.caput(pv_trig, 1, wait=True)

    return data[0], data[1], data[2], ddrts0, ddroffset


def _saveBrBpmData(fname, waveform, data, **kwargs):
    group = kwargs.get("h5group", "/")
    dcct_data = kwargs.get("dcct_data", None)
    pvpref = kwargs.get("pvpref", None)

    # open with default 'a' mode: rw if exists, create otherwise
    h5f = h5py.File(fname)
    if group != "/":
        grp = h5f.create_group(group)
    grp = h5f[group]
    grp["%s_name" % waveform]   = data[0]
    grp["%s_x" % waveform]      = data[1]
    grp["%s_y" % waveform]      = data[2]
    grp["%s_sum" % waveform]    = data[3]
    grp["%s_ts" % waveform]     = data[4]
    grp["%s_offset" % waveform] = data[5]
    grp.attrs["timespan"] = _maxTimeSpan(data[4])

    if dcct_data:
        for i,d in enumerate(dcct_data):
            grp["dcct_%d" % i] = np.array(d, 'd')
    for i,t in enumerate(kwargs.get("ts", [])):
        grp.attrs["%s_t%d" % (waveform,i)] = t.strftime("%Y_%m_%d_%H%M%S.%f")

    if pvpref is not None:
        pvs = [ p + "DDR:WfmSel-SP" for p in pvpref]
        grp["wfm_type"] = ap.catools.caget(pvs)
        pvs = [ p + "ddrAdcWfEnable" for p in pvpref]
        grp["wfm_Adc_enabled"] = ap.catools.caget(pvs)
        pvs = [ p + "ddrTbtWfEnable" for p in pvpref]
        grp["wfm_Tbt_enabled"] = ap.catools.caget(pvs)
        pvs = [ p + "ddrFaWfEnable" for p in pvpref]
        grp["wfm_Fa_enabled"] = ap.catools.caget(pvs)

    h5f.close()


def getBrBpmData(**kwargs):
    """
    timeout - 6sec
    sleep - 4sec
    output_dir - 
    output_file -

    returns name, x, y, Isum, timestamp, offset

    There will be warning if timestamp differs more than 1 second
    """
    trig_src = kwargs.get("trig", 0)
    verbose  = kwargs.get("verbose", 0)
    waveform = kwargs.pop("waveform", "Tbt")
    name     = kwargs.pop("name", "BPM")
    #timeout  = kwargs.get("timeout", 6)

    lat = ap.machines.getLattice()
    if lat.name != "BR":
        raise RuntimeError("the current lattice is not 'BR': %s" % lat.name)

    t0 = datetime.now()

    pv_dcct = "BR-BI{DCCT:1}I-Wf"
    dcct1 = ap.catools.caget(pv_dcct, count=1000)

    pvpref = [bpm.pv(field="x")[0].replace("Pos:X-I", "")
              for bpm in ap.getElements(name)]
    names = [bpm.name for bpm in ap.getElements(name)]

    if trig_src == 0 and waveform in ["Tbt", "Fa"]:
        ret = _brBpmTrigData(pvpref, waveform, **kwargs)
        x, y, Is, ts, offset = ret
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
        x  = np.array(ap.catools.caget(pv_x), 'd')
        y  = np.array(ap.catools.caget(pv_y), 'd') 
        Is = np.array(ap.catools.caget(pv_S), 'd')
        ts = ap.catools.caget(pv_ts)
        offset = ap.catools.caget(pv_offset)

    # get dcct
    dcct2 = ap.catools.caget(pv_dcct, count=1000)
    t1 = datetime.now()

    data = (names, x, y, Is, ts, offset)

    if kwargs.has_key("output_dir" ) or kwargs.has_key("output_file"):
        # default output dir and file
        output_dir = kwargs.pop("output_dir", "")
        fopt = "bpm_%s_%d_" % (waveform, trig_src) + \
            t0.strftime("%Y_%m_%d_%H%M%S.hdf5")
        output_file = kwargs.get("output_file", os.path.join(output_dir, fopt))
        # save the data
        _saveBrBpmData(output_file, waveform, data,
                       h5group=kwargs.get("h5group", "/"),
                       dcct_data = (dcct1, dcct2),
                       ts = (t0, t1),
                       pvpref = pvpref)
        return data, output_file
    else:
        return data


def generateBrRamping(IFb, IFt, **kwargs):
    """
    IFb - Injection
    IFt - Extraction
    dIu - dI/dt up
    dId - dI/dt down
    T - T1 to T9, default: (110, 410, 3310, 3810, 4010, 4310, 6510, 6810, 10000)
    N - length of waveform, default 10150

    returns 1D numpy array
    """
    T = kwargs.get("T", (110, 410, 3310, 3810, 4010, 4310, 6510, 6810, 10000))
    N = kwargs.get("N", 10150)
    T1, T2, T3, T4, T5, T6, T7, T8, T9 = T
    dt = 0.5*(T3+T4) - 0.5*(T1+T2)
    dIdt0_m = (IFt - IFb) / dt
    dt = 0.5*(T8+T7) - 0.5*(T5+T6)
    dIdt1_m = (IFb - IFt) / dt

    dIdt0 = kwargs.get("dIu", dIdt0_m)
    dIdt1 = kwargs.get("dId", dIdt1_m)
    
    v = np.zeros(10150, 'd')
    # 1. injection flat top
    a, b, c, d = (IFb, 0.0, 0.0, 0.0)
    for i in range(T1):
        dt = i
        v[i] = a + b*dt + c*dt**3 + d * dt**4
    # 2. 
    DT2 = T2 - T1
    a, b, c, d = (IFb, 0.0, dIdt0/DT2**2, -0.5*dIdt0/DT2**3)
    for i in range(T1, T2):
        dt = i - T1
        v[i] = a + b*dt + c*dt**3 + d * dt**4

    # 3.
    DT3 = T3 - T2
    a, b, c, d = (IFb+0.5*dIdt0*DT2, dIdt0, 0.0, 0.0)
    for i in range(T2, T3):
        dt = i - T2
        v[i] = a + b*dt + c*dt**3 + d * dt**4

    # 4
    DT4 = T4 - T3
    a = IFb+dIdt0*(0.5*DT2 + DT3)
    b = dIdt0
    c = (4*(IFb-IFt)-dIdt0*(2.0*(T1+T2)-(T3+3*T4)))/(-DT4**3)
    d = (6.0*(IFb-IFt)-dIdt0*(3.0*(T1+T2)-(2*T3+4*T4)))/(2.0*DT4**4)
    for i in range(T3, T4):
        dt = i - T3
        v[i] = a + b*dt + c*dt**3 + d * dt**4

    # 5
    for i in range(T4, T5):
        v[i] = IFt

    # 6
    DT6 = T6 - T5
    a, b, c, d = IFt, 0.0, dIdt1/DT6**2, -0.5*dIdt1/DT6**3
    for i in range(T5, T6):
        dt = i - T5
        v[i] = a + b*dt + c*dt**3 + d * dt**4

    # 7
    DT7 = T7 - T6
    a, b, c, d = IFt+0.5*dIdt1*DT6, dIdt1, 0.0, 0.0
    for i in range(T6, T7):
        dt = i - T6
        v[i] = a + b*dt + c*dt**3 + d * dt**4

    # 8
    DT8 = T8 - T7
    a = IFt + 0.5*dIdt1*DT6 + dIdt1*DT7
    b = dIdt1
    c = (4.0*(IFb-IFt)+dIdt1*(2*(T5+T6) - (T7+3*T8)))/DT8**3
    d = (dIdt1*(2.0*DT8 + 1.5*DT6+3.0*DT7)+3.0*(IFt-IFb))/DT8**4
    for i in range(T7, T8):
        dt = i - T7
        v[i] = a + b*dt + c*dt**3 + d * dt**4

    # 9
    for i in range(T8, T9):
        v[i] = IFb

    for i in range(T9, N): v[i] = IFb

    return v

def generateBrRampingBump(Tc, DTc, DTft, Ic, v0 = None):
    """
    Tc - starting Time
    DTc - delta Tc
    DTft - T for flat top
    Ic - flat top current
    v0 - if not None, the main ramping

    return new copy of ramping curve.
    """
    #Ic = 1.0
    #Tc, DTc, DTft = 0, 100, 300
    T0, T1, T2 = Tc, Tc+DTc/2, Tc+DTc,
    T3, T4, T5 = Tc+DTc+DTft, Tc+3*DTc/2+DTft, Tc+2*DTc+DTft
    v = np.zeros(Tc + 2*DTc + DTft, 'd')
    # 1
    a, b, c, d = 0.0, 0.0, 8*Ic/DTc**3, -8*Ic/DTc**4
    for i in range(T0, T1):
        dt = i - T0
        v[i] = c*dt**3 + d * dt**4
    # 2
    a, b, c, d = Ic/2.0, 2*Ic/DTc, -8*Ic/DTc**3, 8*Ic/DTc**4
    for i in range(T1, T2):
        dt = i - T1
        v[i] = a + b*dt + c*dt**3 + d * dt**4

    # 3
    a, b, c, d = Ic, 0.0, 0.0, 0.0
    for i in range(T2, T3):
        dt = i - T2
        v[i] = a + b*dt + c*dt**3 + d * dt**4

    # 4
    a, b, c, d = Ic, 0.0, -8*Ic/DTc**3, 8*Ic/DTc**4
    for i in range(T3, T4):
        dt = i - T3
        v[i] = a + b*dt + c*dt**3 + d * dt**4

    # 5
    a, b, c, d = Ic/2.0, -2*Ic/DTc, 8*Ic/DTc**3, -8*Ic/DTc**4
    for i in range(T4, T5):
        dt = i - T4
        v[i] = a + b*dt + c*dt**3 + d * dt**4

    if v0 is not None:
        v1 = np.copy(v0)
        for i in range(len(v)):
            v1[i] += v[i]
        return v1
    else:
        return v
