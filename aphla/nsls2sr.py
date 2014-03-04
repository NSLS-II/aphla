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
from catools import caget, caput
from hlalib import getElements

import matplotlib.pylab as plt


def resetSrBpms(wfmsel = 1, name = "BPM", verbose=0):
    """
    reset the BPMs to external trigger and Tbt waveform. Offset is 0 for all
    Adc, Tbt and Fa waveforms. The Wfm size is set to 1,000,000 for ADC,
    100,000 for Tbt and 9,000 for Fa.
    """
    elems = [e for e in getElements(name) if e.pv(field="x")]
    pvprefs = [bpm.pv(field="x")[0].replace("Pos:X-I", "") for bpm in elems]

    if verbose:
        print "resetting {0} BPMS: {1}".format(len(elems), elems)

    for i,pvx in enumerate(pvprefs):
        pvs = [ pvx + "Trig:TrigSrc-SP" for pvx in pvprefs]
        caput(pvs, 1, wait=True)
        # 0 - Adc, 1 - Tbt, 2 - Fa
        pvs = [ pvx + "DDR:WfmSel-SP" for pvx in pvprefs]
        caput(pvs, wfmsel, wait=True)

        # enable all three waveforms
        #pvs = [ pvx + "ddrAdcWfEnable" for pvx in pvprefs]
        #caput(pvs, 1, wait=True)
        #pvs = [ pvx + "ddrTbtWfEnable" for pvx in pvprefs]
        #caput(pvs, 1, wait=True)
        #pvs = [  pvx + "ddrFaWfEnable" for pvx in pvprefs]
        #caput(pvs, 1, wait=True)
        #
        pvs = [ pvx + "ddrAdcOffset" for pvx in pvprefs]
        caput(pvs, 0, wait=True)
        pvs = [ pvx + "ddrTbtOffset" for pvx in pvprefs]
        caput(pvs, 0, wait=True)
        pvs = [  pvx + "ddrFaOffset" for pvx in pvprefs]
        caput(pvs, 0, wait=True)
        #
        pvs = [ pvx + "Burst:AdcEnableLen-SP" for pvx in pvprefs]
        caput(pvs, [1000000] * len(pvs), wait=True)
        pvs = [ pvx + "Burst:TbtEnableLen-SP" for pvx in pvprefs]
        caput(pvs,  [100000] * len(pvs), wait=True)
        pvs = [ pvx + "Burst:FaEnableLen-SP" for pvx in pvprefs]
        caput(pvs,    [9000] * len(pvs), wait=True)
        #
        pvs = [ pvx + "ERec:AdcEnableLen-SP" for pvx in pvprefs]
        if verbose: print pvs
        caput(pvs, [100000] * len(pvs), wait=True)
        pvs = [ pvx + "ERec:TbtEnableLen-SP" for pvx in pvprefs]
        if verbose: print pvs
        caput(pvs, [100000] * len(pvs), wait=True)
        pvs = [ pvx + "ERec:FaEnableLen-SP" for pvx in pvprefs]
        if verbose: print pvs
        caput(pvs,   [9000] * len(pvs), wait=True)
    
    
def _srBpmTrigData(pvprefs, waveform, **kwargs):
    """
    """
    offset = kwargs.pop("offset", 0)
    sleep  = kwargs.pop("sleep", 0.5)
    count  = kwargs.pop("count", 0)
    tc = kwargs.get("timeout", 6)
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
    ddrts0 = caget(pv_ddrts)
    ddroffset = caget(pv_ddroffset, timeout=tc)
    data = (caget(pv_x, count=count), caget(pv_y, count=count),
            caget(pv_S, count=count))
    #
    data = np.array(data, 'd')

    # set 0 - internal trig, 1 - external trig
    #caput(pv_trig, 1, wait=True)

    return data[0], data[1], data[2], ddrts0, ddroffset


def _saveSrBpmData(fname, waveform, data, **kwargs):
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
        grp["wfm_type"] = caget(pvs)
        pvs = [ p + "ddrAdcWfEnable" for p in pvpref]
        grp["wfm_Adc_enabled"] = caget(pvs)
        pvs = [ p + "ddrTbtWfEnable" for p in pvpref]
        grp["wfm_Tbt_enabled"] = caget(pvs)
        pvs = [ p + "ddrFaWfEnable" for p in pvpref]
        grp["wfm_Fa_enabled"] = caget(pvs)

    h5f.close()


def getSrBpmData(**kwargs):
    """
    timeout - 6sec
    sleep - 4sec
    output - True, use default file name, str - user specified filename

    returns name, x, y, Isum, timestamp, offset

    There will be warning if timestamp differs more than 1 second
    """
    trig_src = kwargs.get("trig", 0)
    verbose  = kwargs.get("verbose", 0)
    waveform = kwargs.pop("waveform", "Tbt")
    name     = kwargs.pop("name", "BPM")
    count    = kwargs.get("count", 0)
    #timeout  = kwargs.get("timeout", 6)

    lat = machines.getLattice()
    if lat.name != "SR":
        raise RuntimeError("the current lattice is not 'BR': %s" % lat.name)

    t0 = datetime.now()

    #pv_dcct = "BR-BI{DCCT:1}I-Wf"
    #dcct1 = caget(pv_dcct, count=1000)

    elems = [e for e in getElements(name) if e.pv(field="x")]
    pvpref = [bpm.pv(field="x")[0].replace("Pos:X-I", "") for bpm in elems]
    names = [bpm.name for bpm in elems]

    if trig_src == 0 and waveform in ["Tbt", "Fa"]:
        ret = _srBpmTrigData(pvpref, waveform, **kwargs)
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
        x  = np.array(caget(pv_x, count=count), 'd')
        y  = np.array(caget(pv_y, count=count), 'd') 
        Is = np.array(caget(pv_S, count=count), 'd')
        ts = caget(pv_ts)
        offset = caget(pv_offset)

    # get dcct
    #dcct2 = caget(pv_dcct, count=1000)
    #t1 = datetime.now()

    data = (names, x, y, Is, ts, offset)

    if kwargs.get("output", None):
        # default output dir and file
        output_file = kwargs["output"]
        if output_file is True:
            # use the default file name
            output_dir = os.path.join(machines.getOutputDir(),
                                      t0.strftime("%Y_%m"),
                                      "bpm")
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            fopt = "bpm_%s_%d_" % (waveform, trig_src) + \
                t0.strftime("%Y_%m_%d_%H%M%S.hdf5")
            output_file = os.path.join(output_dir, fopt)

        # save the data
        _saveBrBpmData(output_file, waveform, data,
                       h5group=kwargs.get("h5group", "/"),
                       #dcct_data = (dcct1, dcct2),
                       ts = (t0, t1),
                       pvpref = pvpref)
        return data, output_file
    else:
        return data

def plotChromaticity(f, nu, chrom):
    """
    see measChromaticity
    """
    df = f - np.mean(f)
    p, resi, rank, sing, rcond = np.polyfit(df, nu, deg=2, full=True)
    t = np.linspace(1.1*df[0], 1.1*df[-1], 100)
    plt.clf()
    plt.plot(f - f0, nu[:,0] - nu0[0], '-rx')
    plt.plot(f - f0, nu[:,1] - nu0[1], '-go')
    plt.plot(t, t*t*p[-3,0]+t*p[-2,0] + p[-1,0], '--r',
             label="H: %.1fx^2%+.2fx%+.1f" % (p[-3,0], p[-2,0], p[-1,0]))
    plt.plot(t, t*t*p[-3,1]+t*p[-2,1] + p[-1,1], '--g',
             label="V: %.1fx^2%+.2fx%+.1f" % (p[-3,1], p[-2,1], p[-1,1]))
    plt.text(min(df), min(dnu[:,0]),
             r"$\eta=%.3e,\quad C_x=%.2f,\quad C_y=%.2f$" %\
             (eta, chrom[0], chrom[1]))
    
    plt.legend(loc='upper right')
    plt.xlabel("$f-f_0$ [MHz]")
    plt.ylabel(r"$\nu-\nu_0$")
    plt.savefig('measchrom.png')
