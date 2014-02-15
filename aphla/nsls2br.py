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
import warnings

import machines
from catools import caget, caput
from hlalib import getElements

import matplotlib.pylab as plt

    
def _brBpmScrub(**kwargs):
    """
    waveforms - list of Tbt, Fa and Adc
    """

    lat = machines.getLattice()
    if lat.name != "BR":
        raise RuntimeError("the current lattice is not 'BR': %s" % lat.name)

    waveforms = kwargs.get("waveforms", ["Tbt", "Fa", "Adc"])
    bpms = getElements("BPM")
    # did not consider the 'ddrTbtWfEnable' PV
    for bpm in bpms:
        pvx = bpm.pv(field="x")[0]
        pv = pvx.replace("Pos:X-I", "Trig:TrigSrc-SP")
        # 0 - internal, 1 - external
        caput(pv, 0, wait=True)
        pv = pvx.replace("Pos:X-I", "DDR:WfmSel-SP")
        for fld in waveforms:
            pv = pvx.replace("Pos:X-I", "ddr%sWfEnable" % fld)
            caput(pv, 0, wait=True)
            # offset
            pv = pvx.replace("Pos:X-I", "ddr%sOffset" % fld)
            caput(pv, 0, wait=True)

    time.sleep(2)
    for bpm in bpms:
        pvx = bpm.pv(field="x")[0]
        pv = pvx.replace("Pos:X-I", "Trig:TrigSrc-SP")
        # 0 - internal, 1 - external
        caput(pv, 1, wait=True)
        pv = pvx.replace("Pos:X-I", "DDR:WfmSel-SP")
        for fld in waveforms:
            pv = pvx.replace("Pos:X-I", "ddr%sWfEnable" % fld)
            caput(pv, 1, wait=True)
    time.sleep(2)


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



def resetBrBpms(wfmsel = 1):
    """
    reset the BPMs to external trigger and Tbt waveform. Offset is 0 for all
    Adc, Tbt and Fa waveforms.
    """
    pvprefs = [bpm.pv(field="x")[0].replace("Pos:X-I", "")
               for bpm in getElements("BPM")]
    for i,pvx in enumerate(pvprefs):
        pvs = [ pvx + "Trig:TrigSrc-SP" for pvx in pvprefs]
        caput(pvs, 1, wait=True)
        # 0 - Adc, 1 - Tbt, 2 - Fa
        pvs = [ pvx + "DDR:WfmSel-SP" for pvx in pvprefs]
        caput(pvs, wfmsel, wait=True)
        # enable all three waveforms
        pvs = [ pvx + "ddrAdcWfEnable" for pvx in pvprefs]
        caput(pvs, 1, wait=True)
        pvs = [ pvx + "ddrTbtWfEnable" for pvx in pvprefs]
        caput(pvs, 1, wait=True)
        pvs = [  pvx + "ddrFaWfEnable" for pvx in pvprefs]
        caput(pvs, 1, wait=True)
        #
        pvs = [ pvx + "ddrAdcOffset" for pvx in pvprefs]
        caput(pvs, 0, wait=True)
        pvs = [ pvx + "ddrTbtOffset" for pvx in pvprefs]
        caput(pvs, 0, wait=True)
        pvs = [  pvx + "ddrFaOffset" for pvx in pvprefs]
        caput(pvs, 0, wait=True)
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
    wfsel0   = caget(pv_wfmsel, timeout=tc)
    trig0 = caget(pv_trig, timeout=tc)

    # set the trigger internal, TBT waveform
    prf = ""
    if waveform == "Adc":
        caput(pv_wfmsel, 0, wait=True)
        caput(pv_adcwfm, 1, wait=True)
        caput(pv_adcoffset, offset, wait=True)
        pv_ddroffset = pv_adcoffset
        prf = ""
    elif waveform == "Tbt":
        caput(pv_wfmsel, 1, wait=True)
        caput(pv_tbtwfm, 1, wait=True)
        caput(pv_tbtoffset, offset, wait=True)
        pv_ddroffset = pv_tbtoffset
        prf = "TBT"
    elif waveform == "Fa":
        caput(pv_wfmsel, 2, wait=True)
        caput(pv_fawfm,  1, wait=True)
        caput(pv_faoffset, offset, wait=True)
        pv_ddroffset = pv_faoffset
        prf = "FA"
    else:
        raise RuntimeError("unknow waveform '%s'" % waveform)

    time.sleep(1.5)
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

    time.sleep(sleep)

    # check timestamp
    n = 0
    while True:
        tss_r  = caget(pv_trigts, timeout=tc)
        tss = [t - min(tss_r) for t in tss_r]
        tsns = caget(pv_trigtsns, timeout=tc)
        ts = [s + 1.0e-9*tsns[i] for i,s in enumerate(tss)]
        mdt = max(ts) - min(ts)
        ddrts0 = caget(pv_ddrts)
        mdt_s  = _maxTimeSpan(caget(pv_ddrts, timeout=tc))
        n = n + 1
        if mdt < 1.0 and mdt_s < 1.0:
            #print "Max dt=", mdt, mdt_s, "tried %d times" % n
            break
        time.sleep(0.6)
        # quit if failed too many times
        if n > 20:
            caput(pv_trig, [1] * len(pv_trig), wait=True)
            raise RuntimeError("BPMs are not ready after %d trials" % n)

    if verbose > 0:
        print "Trials: %d, Trig=%.2e, DDR Trig=%.2e seconds." % (n, mdt, mdt_s)

    # redundent check
    ddrts0   = caget(pv_ddrts, timeout=tc)
    mdt = _maxTimeSpan(ddrts0)
    if mdt > 1.0:
        print "ERROR: Timestamp does not agree (max dt= %f), wait ..." % mdt

    ddroffset = caget(pv_ddroffset, timeout=tc)
    data = (caget(pv_x),
            caget(pv_y),
            caget(pv_S))
    #
    data = np.array(data, 'd')

    # set 0 - internal trig, 1 - external trig
    caput(pv_trig, 1, wait=True)

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
        grp["wfm_type"] = caget(pvs)
        pvs = [ p + "ddrAdcWfEnable" for p in pvpref]
        grp["wfm_Adc_enabled"] = caget(pvs)
        pvs = [ p + "ddrTbtWfEnable" for p in pvpref]
        grp["wfm_Tbt_enabled"] = caget(pvs)
        pvs = [ p + "ddrFaWfEnable" for p in pvpref]
        grp["wfm_Fa_enabled"] = caget(pvs)

    h5f.close()


def getBrBpmData(**kwargs):
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
    #timeout  = kwargs.get("timeout", 6)

    lat = machines.getLattice()
    if lat.name != "BR":
        raise RuntimeError("the current lattice is not 'BR': %s" % lat.name)

    t0 = datetime.now()

    pv_dcct = "BR-BI{DCCT:1}I-Wf"
    dcct1 = caget(pv_dcct, count=1000)

    pvpref = [bpm.pv(field="x")[0].replace("Pos:X-I", "")
              for bpm in getElements(name)]
    names = [bpm.name for bpm in getElements(name)]

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
        x  = np.array(caget(pv_x), 'd')
        y  = np.array(caget(pv_y), 'd') 
        Is = np.array(caget(pv_S), 'd')
        ts = caget(pv_ts)
        offset = caget(pv_offset)

    # get dcct
    dcct2 = caget(pv_dcct, count=1000)
    t1 = datetime.now()

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
                       dcct_data = (dcct1, dcct2),
                       ts = (t0, t1),
                       pvpref = pvpref)
        return data, output_file
    else:
        return data


def plotBrRmData(fname, group, **kwargs):
    output = kwargs.get("output", "images/br_orm")
    i0 = kwargs.get("i0", 5)
    i1 = kwargs.get("i1", -1)
    nbpm = kwargs.get("nbpm", 36)
    ndx = kwargs.get("ndx", 4)
    npt = kwargs.get("npoints", 4)
    wfm = kwargs.get("waveform", "Fa")

    h5f = h5py.File(fname, 'r')
    if group not in h5f: return None
    
    for ibpm in range(nbpm):
        for i in range(ndx):
            plt.clf()
            #fig = plt.figure(figsize=(10, 4), dpi=100)
            nlines = 0
            for j in range(npt):
                # skip the deleted data
                ds = "%s/%s_dx%d__pt%d" % (group, wfm, i, j)
                if ds not in h5f: continue
                h5g = h5f[ds]
                # average the readings over the slice i0:i1
                if wfm == "Fa":
                    xfa, yfa = h5g["Fa_x"], h5g["Fa_y"]
                elif wfm == "Tbt":
                    xfa, yfa = h5g["Tbt_x"], h5g["Tbt_y"]
                else:
                    raise RuntimeError("no waveform selected")
                #print np.shape(xfa), np.shape(yfa)
                plt.subplot(2,1,1)
                plt.plot(xfa[ibpm,i0:i1])
                plt.subplot(2,1,2)
                plt.plot(yfa[ibpm,i0:i1])
                nlines = nlines + 1
            if nlines > 0:
                plt.savefig("%s_bpm_%d_dx%d.png" % (output, ibpm, i))
            plt.clf()    
    h5f.close()        

def calcBrRmCol(fname, group, **kwargs):
    """
    fname - output file name
    group - group name in HDF5 file (corrector SP PV)
    nbpm - BR has 36 bpms
    plot - whether plot or not
    faslice - slice range of FA waveform data
    """
    nbpm = kwargs.get("nbpm", 36)
    plot = kwargs.get("plot", False)
    wfmslice = kwargs.get("wfmslice", (10,100))
    wfm = kwargs.get("waveform", "Fa") 
    output = kwargs.get("output", "images/br_orm")
    
    # check what data are available
    h5f = h5py.File(fname, 'r')
    if group not in h5f: return None
    grps = []
    for g in h5f.keys():
        if g != group: continue
        for g1 in h5f[g].keys():
            m = re.match(r".+_dx([0-9]+)__pt([0-9]+)", g1)
            if not m: continue
            #  number of kicks and number of reading for each kick
            grps.append((int(m.group(1)), int(m.group(2))))
    if len(grps) == 0:
        print "WARNING: did not find any valid data"
        return None
    # the maximum possible kicks and readings
    ndx = max([i for i, j in grps]) + 1
    npt = max([j for i, j in grps]) + 1
    # we care about this slice in FA data
    i0, i1 = wfmslice

    # nbpm, ndx, (average, std)
    mxij = np.zeros((nbpm, ndx, 2), 'd')
    myij = np.zeros((nbpm, ndx, 2), 'd')
    msk = np.ones(ndx, 'i')
    # BPM orbit range
    bpmr = np.zeros((nbpm, 4), 'd')
    # show data for iBPM, for turns i0:i1
    dxlst = np.array(h5f["%s/dxlst" % group], 'd')
    
    for i in range(ndx):
        # possible readings 
        mtx, mty = [], []
        for j in range(npt):
            # skip the deleted data
            ds = "%s/%s_dx%d__pt%d" % (group, wfm, i, j)
            if ds not in h5f: continue
            h5g = h5f[ds]
            # average the readings over the slice i0:i1
            xfa, yfa = h5g["%s_x" % wfm], h5g["%s_y" % wfm]
            xobt = np.average(xfa[:,i0:i1], axis=1)
            yobt = np.average(yfa[:,i0:i1], axis=1)
            mtx.append(xobt)
            mty.append(yobt)

        if len(mtx) == 0:
            # we do not have any readings at this kick point
            print "WARNING: no valid points found at dx=", dxlst[i]
            msk[i] = 0
            continue
        # average over all readings for ith kick
        mxij[:,i,0] = np.average(np.array(mtx), axis=0)
        myij[:,i,0] = np.average(np.array(mty), axis=0)
        # std of readings for ith kick
        mxij[:,i,1] = np.std(mtx, axis=0)
        myij[:,i,1] = np.std(mty, axis=0)
        if plot and len(mtx) > 0:
            fig = plt.figure(figsize=(10, 2), dpi=100)
            ax1 = plt.subplot(2,1,1)
            ax2 = plt.subplot(2,1,2)
            #print "Data size:", len(mtx), len(mty)
            for j in range(1, len(mtx)):
                ax1.plot(mtx[j] - mtx[0], '-', label="%d,%d" % (i,j))
                ax2.plot(mty[j] - mty[0], '-', label="%d,%d" % (i,j))
            ax1.text(0.05,0.95, "%s" % group, size="xx-large",
                     horizontalalignment='left', verticalalignment='top',
                     transform=ax1.transAxes)
            ax1.legend()
            ax2.legend()
            fig.savefig("%s_orbit_diff_dx%d.png" % (output, i))
            plt.close()

    # remove the missing points
    mxij = np.compress(msk, mxij, axis=1)  
    myij = np.compress(msk, myij, axis=1)
    dxlst = np.compress(msk, dxlst)
    h5f.close()
    # the number of kicks need to be updated.
    ndx = np.shape(mxij)[1]
    if plot:
        fig = plt.figure(figsize=(12, ndx*2), dpi=100)
        for i in range(ndx):
            #plt.title(group)
            ax = plt.subplot(ndx, 4, 4*i+1)
            plt.text(0.05,0.95, "X: d_kick= %.2f" % dxlst[i], size="xx-large",
                     horizontalalignment='left', verticalalignment='top',
                     transform=ax.transAxes)
            plt.errorbar(range(nbpm), mxij[:,i,0], yerr=mxij[:,i,1])
            ax = plt.subplot(ndx, 4, 4*i+2)
            plt.plot(mxij[:,i,1], '-')
            ax = plt.subplot(ndx, 4, 4*i+3)
            plt.text(0.05,0.95, "Y: d_kick= %.2f" % dxlst[i], size="xx-large",
                     horizontalalignment='left', verticalalignment='top',
                     transform=ax.transAxes)
            plt.errorbar(range(nbpm), myij[:,i,0], yerr=myij[:,i,1])
            ax = plt.subplot(ndx, 4, 4*i+4)
            plt.plot(myij[:,i,1], '-')
        fig.savefig("%s_orbit.png" % output)

    bpmr[:,0] = np.min(mxij[:,:,0], axis=1)
    bpmr[:,1] = np.max(mxij[:,:,0], axis=1)
    bpmr[:,2] = np.min(myij[:,:,0], axis=1)
    bpmr[:,3] = np.max(myij[:,:,0], axis=1)
    if plot:
        #plt.clf()
        fig = plt.figure(figsize=(10, 3), dpi=100)
        plt.subplot(211)
        plt.plot(bpmr[:,1] - bpmr[:,0], 'r-', label="X span")
        plt.legend()
        plt.subplot(212)
        plt.plot(bpmr[:,3] - bpmr[:,2], 'r-', label="Y span")
        plt.legend()
        #plt.show()
        fig.savefig("%s_orbit_span.png" % output)
        plt.close()

    mcol, pol = [], []
    for i in range(nbpm):
        # fit polynomial, 
        px = np.polyfit(dxlst, mxij[i,:,0], 1)
        py = np.polyfit(dxlst, myij[i,:,0], 1)
        # take the linear coef.
        mcol.append((px[-2], py[-2]))
        pol.append((px, py))

    if plot:
        ncol = 4
        nrow = (nbpm // ncol) + min(nbpm % ncol, 1)
        fig = plt.figure(figsize=(22, nrow*2))
        for i in range(nbpm):
            px, py = pol[i]
            dt = (dxlst[-1] - dxlst[0]) * 0.05
            t = np.linspace(dxlst[0]-dt, dxlst[-1]+dt, 10)
            #plt.title("BPM %d" % i)
            ax1 = plt.subplot(nrow, ncol, i+1)
            ax1.plot(dxlst, mxij[i,:,0], 'bo')
            ax1.errorbar(dxlst, mxij[i,:,0], yerr=mxij[i,:,1], color='b')
            ax1.plot(t, np.polyval(px, t), 'b-')
            ax1.text(0.05, 0.95, "BPM %d: x=%.2f*k+%.2f\n (%s)" % (i, px[-2], px[-1], group), 
                     size="large",  horizontalalignment='left', verticalalignment='top', transform=ax1.transAxes)
            for tl in ax1.get_yticklabels():
                tl.set_color('b')

            ax2 = ax1.twinx()
            ax2.plot(dxlst, myij[i,:,0], 'ro')
            ax2.errorbar(dxlst, myij[i,:,0], yerr=myij[i,:,1], color='r')
            ax2.plot(t, np.polyval(py, t), 'r-')
            ax2.text(0.05, 0.95, "BPM %d: y=%.2f*k+%.2f\n (%s)" % (i, py[-2], py[-1], group), 
                     size="large",  horizontalalignment='left', verticalalignment='top', transform=ax.transAxes)
            for tl in ax2.get_yticklabels():
                tl.set_color('r')
        if _run_from_ipython():
            plt.show()
        fig.tight_layout()
        fig.savefig("%s_lines.png" % output)
    return mcol


def plotBrOrbits(**kwargs):
    wfm = kwargs.pop("waveform", "Fa")
    slices = kwargs.pop("slices", [(0, 10),])
    average = kwargs.pop("average", True)
    exclude = kwargs.get("exclude", [17,])
    trig    = kwargs.get("trig", 1)
    data = getBrBpmData(trig=trig, waveform=wfm)
    name, x, y, Isum, ts, offset = data
    # exclude BPMs
    mask = np.ones(len(x))
    for i in exclude: mask[i] = 0
    idx  = np.compress(mask, range(len(name)), axis=0)
    bpm  = np.compress(mask, name, axis=0)
    x    = np.compress(mask, x, axis=0)/1000
    y    = np.compress(mask, y, axis=0)/1000
    Isum = np.compress(mask, Isum, axis=0)
    ts   = np.compress(mask, ts, axis=0)
    offset = np.compress(mask, offset, axis=0)

    fig = plt.figure(figsize=kwargs.get("figsize", (13, 4)))
    # rect is [left, bottom, width, height]
    ax1 = fig.add_axes([0.1,0.7,0.8,0.4])
    ax2 = fig.add_axes([0.1,0.2,0.8,0.4])
    lines = [[], []]
    for slc in slices:
        i0, i1 = slc
        #print i0, i1, np.shape(x)
        xi = np.average(x[:,i0:i1], axis=1)
        yi = np.average(y[:,i0:i1], axis=1)
        xistd, yistd = np.std(xi), np.std(yi)
        l1 = ax1.plot(idx, xi, '-', label="{0} {1} std={2:.2f}".format(
                wfm, slc, xistd))
        lines[0].append(l1)
        l2 = ax2.plot(idx, yi, '-', label="{0} {1} std={2:.2f}".format(
                wfm, slc, yistd))
        lines[1].append(l2)
    labels = ["%02d_%s" % (i,s) if mask[i] else "" for i,s in enumerate(name)]
    #nw = max([len(s) for s in labels])
    #fmt = "{:<%d}" % nw
    #labels = [fmt.format(s) + '/' for s in labels]
    ax1.grid(kwargs.get("grid", True))
    ax1.set_ylabel("%s: x [mm]" % wfm)
    ax1.set_xticks(range(len(name)))
    #ax1.legend(loc="upper right")
    ax1.legend(bbox_to_anchor=(1.03, 1), loc=2, borderaxespad=0.)
    ax2.grid(kwargs.get("grid", True))
    ax2.set_ylabel("%s: y [mm]" % wfm)
    ax2.legend(bbox_to_anchor=(1.03, 1), loc=2, borderaxespad=0.)
    ax2.set_xticks(range(len(name)))
    ax2.set_xticklabels(labels, rotation="vertical")
    plt.show()
    print "Time stamp:", ts[0]
    return (bpm, x, y, Isum, ts, offset)


def correctBrOrbit(kker, m, **kwarg):
    """correct the resp using kker and response matrix.

    Parameters
    ------------
    kker : PV list of the controllers, e.g. corrector
    m : response matrix where :math:`m_{ij}=\Delta orbit_i/\Delta kker_j`
    scale : scaling factor applied to the calculated kker
    ref : the targeting value of orbit
    rcond : the rcond for cutting singular values. 
    check : stop if the orbit gets worse.
    wait : waiting (seconds) before check.

    Returns
    --------
    err : converged or not checked (0), error (>0).
    msg : error message or None

    """
    scale = kwarg.get('scale', 0.68)
    ref   = kwarg.get('ref', None)
    check = kwarg.get('check', True)
    wait  = kwarg.get('wait', 6)
    rcond = kwarg.get('rcond', 1e-2)
    verb  = kwarg.get('verbose', 0)
    bc    = kwarg.get('bc', None)
    wfmslice = kwarg.get("wfmslice", (10, 100))
    wfm   = kwarg.pop("waveform", "Fa")
    exrows = kwarg.pop("exclude_rows", [])
    test = kwarg.pop("test", False)
    #u, s, v = np.linalg.svd(m)
    #plt.semilogy(s/s[0], 'x-')
    #plt.show()
    
    i0, i1 = wfmslice
    nbpm, ncor = np.shape(m)
    mask_row = np.ones(nbpm, 'i')
    for i in exrows: mask_row[i] = 0
    m = np.compress(mask_row, m, axis=0)

    print "New m shape:", np.shape(m)

    name, x0, y0, Isum0, ts, offset = getBrBpmData(waveform=wfm, trig=0)

    # save initial orbit in vx0
    vl0 = np.compress(mask_row, np.vstack((x0, y0)), axis=0)
    v0 = np.average(vl0[:,i0:i1], axis=1)
    if np.max(v0) > 10000 or np.min(v0) < -10000:
        plt.plot(v0)
        plt.show()
        raise RuntimeError("orbit is not stable, too large: %.2f, %.2f" % (
                np.min(v0), np.max(v0)))

    if ref is not None: v0 = v0 - ref
    if len(v0) != len(m):
        raise RuntimeError("inconsistent BPM and ORM size")
    
    # the initial norm
    norm0 = np.linalg.norm(v0)

    # solve for m*dk + (v0 - ref) = 0
    dk, resids, rank, s = np.linalg.lstsq(m, -1.0*v0, rcond = rcond)

    norm1 = np.linalg.norm(m.dot(dk*scale) + v0)

    # get the DC kicker
    kl0 = np.array(caget(kker), 'd')
    k0 = np.average(kl0, axis=1)
    print np.shape(kl0)
    #print k0, dk, scale
    k1 = k0 + dk*scale
    vk1 = [[k] * len(kl0[i]) for i,k in enumerate(k1)]
    plt.plot(k0, 'r-', label="initial")
    plt.plot(k1, 'b-', label="new")
    plt.legend()
    plt.show()
    if not test:
        caput(kker, vk1, wait=True)
    else:
        for i,pv in enumerate(kker):
            print i, pv, k1[i], "dk=", dk[i]

    time.sleep(wait)
    name, x1, y1, Isum1, ts, offset = getBrBpmData(waveform=wfm, trig=0)

    vl1 = np.compress(mask_row, np.vstack((x1, y1)), axis=0)
    v1 = np.average(vl1[:,i0:i1], axis=1)

    print norm0, "predicted norm= ", norm1, "realized:", np.linalg.norm(v1)

    return v0, v1, k0, k1


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

    # warning
    if max(v) > Ift:
        warning.warn("max(I) > Ift : {0} > {1}".format(max(v), IFt))
    if min(v) < IFb:
        warning.warn("min(I) < Ifb : {0} < {1}".format(min(v), IFb))

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


def measBrCaRmCol(kker, **kwargs):
    """measure the response matrix column between PVs (DC)

    kker - SP PV for corrector (waveform)
    waveform - "Fa" or "Tbt"
    timeout - 6 sec, EPICS CA timeout
    npoints - number of orbits for each kick.
    dxlst - a list of kick (raw unit), overwrite the choice of dxmax
    dxmax - range of kick [-dxmax, dxmax]
    ndx - default 4. Specify kicks in [-dxmax, dxmax].
    wait - default 1.5 second
    output - save the results
    verbose - default 0

    return the output file name. The output will be in HDF5 file format.
    """
    timeout = kwargs.pop("timeout", 6)
    wait    = kwargs.pop("wait", 1.5)
    verbose = kwargs.pop("verbose", 0)
    npt     = kwargs.pop("npoints", 4)
    wfm     = kwargs.pop("waveform", "Fa")
    
    t0 = datetime.now()
    dxlst, x0 = [], np.array(caget(kker, timeout=timeout), 'd')
    if "dxlst" in kwargs:
        dxlst = kwargs.get("dxlst")
    elif "dxmax" in kwargs:
        dxmax = np.abs(kwargs.get("dxmax"))
        nx    = kwargs.pop("ndx", 4)
        dxlst = list(np.linspace(-dxmax, dxmax, nx))
    else:
        raise RuntimeError("need input for at least of the parameters: "
                           "dxlst, xlst, dxmax")

    # use the provided filename or default datetimed filename
    output_file = kwargs.pop(
        "output",
        os.path.join(machines.getOutputDir(),
                     t0.strftime("%Y_%m"),
                     "orm",
                     t0.strftime("orm_%Y_%m_%d_%H%M%S.hdf5")))

    # save dx list
    h5f = h5py.File(output_file)
    grp = h5f.create_group(kker)
    grp.attrs["orm_t0"] = t0.strftime("%Y_%m_%d_%H:%M:%S.%f")
    grp["dxlst"] = dxlst
    h5f.close()
    
    # save the initial orbit
    getBrBpmData(waveform=wfm,
                 verbose=verbose-1,
                 output_file=output_file,
                 h5group="%s/%s0" % (kker, wfm),
                 **kwargs)
    
    n1 = len(dxlst)
    for i,dx in enumerate(dxlst):
        if verbose > 0:
            print "%d/%d: Setting %s " % (i, n1, kker), dx
            sys.stdout.flush()
        try:
            nx0 = len(x0)
            xi = [x0i + dx for x0i in x0]
        except:
            # should never happen for booster
            xi = x0 + dx
        caput(kker, xi, wait=True, timeout=timeout)
        time.sleep(wait*3)
        for j in range(npt):
            obt, fname = getBrBpmData(
                waveform=wfm, verbose=verbose-1,
                output_file=output_file,
                h5group="%s/%s_dx%d__pt%d" % (kker, wfm, i, j),
                **kwargs)    
            if verbose > 1:
                name, x, y, Is, ts, ddroffset = obt
                print "  %d/%d" % (j,npt), np.average(x[0]), np.std(x[0])
                sys.stdout.flush()
            time.sleep(wait)
        time.sleep(wait)

    caput(kker, x0, wait=True, timeout=timeout)
    
    t1 = datetime.now()

    h5f = h5py.File(output_file)
    h5f[kker].attrs["orm_t1"] = t1.strftime("%Y_%m_%d_%H:%M:%S.%f")
    h5f.close()
    return output_file

