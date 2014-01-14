"""
Some NSLS2 specific routines
=============================

:Author: Lingyun Yang
:Date: 2013-12-09 11:50

br - Booster Ring
sr - Storage Ring
"""

import os
import time
from datetime import datetime
import numpy as np
import aphla as ap
import h5py

HLA_DATA_DIR="/epics/data/aphla/data/nsls2"

def _brBpmScrub(**kwargs):
    """
    waveforms - list of Tbt, Fa and Adc
    """

    lat = ap.machines.getLattice()
    if lat.name != "BR":
        raise RuntimeError("the current lattice is not 'BR': %s" % lat.name)

    waveforms = kwargs.get("waveforms", ["Tbt", "Fa", "Adc"])
    bpms = ap.getElements("BPM")
    # did not consider the 'ddrTbtWfEnable' PV
    for bpm in bpms:
        pvx = bpm.pv(field="x")[0]
        pv = pvx.replace("Pos:X-I", "Trig:TrigSrc-SP")
        # 0 - internal, 1 - external
        ap.catools.caput(pv, 0, wait=True)
        pv = pvx.replace("Pos:X-I", "DDR:WfmSel-SP")
        for fld in waveforms:
            pv = pvx.replace("Pos:X-I", "ddr%sWfEnable" % fld)
            ap.catools.caput(pv, 0, wait=True)
            # offset
            pv = pvx.replace("Pos:X-I", "ddr%sOffset" % fld)
            ap.catools.caput(pv, 0, wait=True)

    time.sleep(2)
    for bpm in bpms:
        pvx = bpm.pv(field="x")[0]
        pv = pvx.replace("Pos:X-I", "Trig:TrigSrc-SP")
        # 0 - internal, 1 - external
        ap.catools.caput(pv, 1, wait=True)
        pv = pvx.replace("Pos:X-I", "DDR:WfmSel-SP")
        for fld in waveforms:
            pv = pvx.replace("Pos:X-I", "ddr%sWfEnable" % fld)
            ap.catools.caput(pv, 1, wait=True)
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


def brBpmTbt(**kwargs):
    """
    timeout - 6sec
    sleep - 4sec
    output_dir - 
    output_file -

    returns name, x, y, Isum

    There will be warning if timestamp differs more than 1 second
    """
    tc = kwargs.get("timeout", 6)
    single_trig = kwargs.get("single_trig", True)

    t0 = datetime.now()
    lat = ap.machines.getLattice()
    if lat.name != "BR":
        raise RuntimeError("the current lattice is not 'BR': %s" % lat.name)

    pv_dcct = "BR-BI{DCCT:1}I-Wf"
    # prepare the triggers
    pv_evg = "BR-BI{BPM}Evt:Single-Cmd"
    br_trig_pvs, br_wfm_enable_pvs, br_wfmsel_pvs = [], [], []
    br_ddrts_pvs = [] # timestamp
    bpms = ap.getElements("BPM")
    # did not consider the 'ddrTbtWfEnable' PV
    for bpm in bpms:
        pvx = bpm.pv(field="x")[0]
        #print bpm.name, pvh, caget(pvh)
        br_trig_pvs.append(pvx.replace("Pos:X-I", "Trig:TrigSrc-SP"))
        br_wfmsel_pvs.append(pvx.replace("Pos:X-I", "DDR:WfmSel-SP"))
        br_ddrts_pvs.append(pvx.replace("Pos:X-I", "TS:DdrTrigDate-I"))
        br_wfm_enable_pvs.append(pvx.replace("Pos:X-I", "ddrTbtWfEnable"))
    # save initial val
    wfsel0   = ap.catools.caget(br_wfmsel_pvs)
    trigsrc0 = ap.catools.caget(br_trig_pvs)

    dcct1 = ap.catools.caget(pv_dcct, count=1000)
    if single_trig:
        # set the trigger internal, TBT waveform
        ap.catools.caput(br_wfmsel_pvs, 1, wait=True)
        ap.catools.caput(br_wfm_enable_pvs, 1, wait=True, timeout=tc)
        ap.catools.caput(br_trig_pvs, 0, wait=True)

        # set the event
        ap.catools.caput(pv_evg, 1, wait=True)
        dcct1 = ap.catools.caget(pv_dcct, count=1000)
        time.sleep(kwargs.get("sleep", 8))

    data = []
    ddrts0   = ap.catools.caget(br_ddrts_pvs)
    mdt = _maxTimeSpan(ddrts0)
    while mdt > 1.0:
        print "Timestamp does not agree, wait ..."
        time.sleep(1.0)
        ddrts0   = ap.catools.caget(br_ddrts_pvs)
        mdt = _maxTimeSpan(ddrts0)
        
    for ibpm,bpm in enumerate(bpms):
        x, y = np.array(bpm.xtbt, 'd'), np.array(bpm.ytbt, 'd')
        I = np.array(bpm.Itbt, 'd')
        ts = ap.catools.caget(br_ddrts_pvs[ibpm])
        if ts != ddrts0[ibpm] and single_trig:
            print "Timestamp changed for '%s': %s %s" % (
                bpm.name, ddrts0[ibpm], ts)
        data.append((ibpm, bpm.name, bpm.sb, x, y, I, ts))
        #
    dcct2 = ap.catools.caget(pv_dcct, count=1000)

    mdt = _maxTimeSpan([v[6] for v in data])
    if single_trig:
        if mdt > 1.0:
            print "WARNING: BPM timestamp differs > 1 sec"
        # restore the br_trig_pvs
        ap.catools.caput(pv_evg, 0, wait=True)
        ap.catools.caput(br_trig_pvs, 1, wait=True)
        ap.catools.caput(br_wfmsel_pvs, wfsel0, wait=True)
    t1 = datetime.now()

    output_dir = kwargs.get("output_dir", "")
    output_file = kwargs.get("output_file", 
                             os.path.join(output_dir, 
                                          t0.strftime("bpm_tbt_0_%Y_%m_%d_%H%M%S.hdf5")))
    if kwargs.has_key("output_dir" ) or kwargs.has_key("output_file"):
        saveBpmTbt(output_file, data, group=kwargs.get("h5group", "/"), dt=mdt,
                   dcct_data = (dcct1, dcct2))
        return data, output_file
    else:
        time.sleep(1)

    names = [v[1] for v in data]
    x = np.array([v[3] for v in data], 'd')
    y = np.array([v[4] for v in data], 'd')
    s = np.array([v[5] for v in data], 'd')
    return names, x, y, s


def brBpmFa(**kwargs):
    """
    timeout - 6
    single_trig - True (synced data)
    output_dir - 
    output_file -

    returns name, x, y, Isum.

    see also :func:`brBpmTbt`
    """
    tc = kwargs.get("timeout", 6)
    single_trig = kwargs.get("single_trig", True)

    t0 = datetime.now()
    lat = ap.machines.getLattice()
    if lat.name != "BR":
        raise RuntimeError("the current lattice is not 'BR': %s" % lat.name)

    pv_dcct = "BR-BI{DCCT:1}I-Wf"
    pv_evg = "BR-BI{BPM}Evt:Single-Cmd"
    br_trig_pvs, br_wfmsel_pvs, br_wfm_enable_pvs = [], [], []
    br_ddrts_pvs = []
    bpms = ap.getElements("BPM")
    # did not consider the 'ddrTbtWfEnable' PV
    for bpm in bpms:
        pvx = bpm.pv(field="x")[0]
        #print bpm.name, pvh, caget(pvh)
        br_trig_pvs.append(pvx.replace("Pos:X-I", "Trig:TrigSrc-SP"))
        br_wfmsel_pvs.append(pvx.replace("Pos:X-I", "DDR:WfmSel-SP"))
        br_wfm_enable_pvs.append(pvx.replace("Pos:X-I", "ddrFaWfEnable"))
        br_ddrts_pvs.append(pvx.replace("Pos:X-I", "TS:DdrTrigDate-I"))
    # save initial val
    wfsel0   = ap.catools.caget(br_wfmsel_pvs)
    trigsrc0 = ap.catools.caget(br_trig_pvs)
    wfenb0   = ap.catools.caget(br_wfm_enable_pvs)

    dcct1 = ap.catools.caget(pv_dcct, count=1000)
    if single_trig:
        # set the trigger internal, FA waveform
        ap.catools.caput(br_wfmsel_pvs, 2, wait=True, timeout=tc)
        ap.catools.caput(br_wfm_enable_pvs, 1, wait=True, timeout=tc)
        ap.catools.caput(br_trig_pvs, 0, wait=True, timeout=tc)

        # set the event
        ap.catools.caput(pv_evg, 1, wait=True, timeout=tc)
        dcct1 = ap.catools.caget(pv_dcct, count=1000)
        time.sleep(kwargs.get("sleep", 8))

    data = []
    ddrts0   = ap.catools.caget(br_ddrts_pvs)
    for ibpm,bpm in enumerate(bpms):
        x, y, I = bpm.xfa, bpm.yfa, bpm.Ifa
        #pv = bpm.pv(field="xfa", handle="readback")[0]
        #x = np.array(ap.catools.caget(pv), 'd')
        ts = ap.catools.caget(br_ddrts_pvs[ibpm])
        if ts != ddrts0[ibpm] and single_trig:
            print "Timestamp changed for '%s': %s %s" % (
                bpm.name, ddrts0[ibpm], ts)
        #if ibpm == 0:
        #    print len(x), np.average(x), np.std(x), np.average(y), np.std(y)
        data.append((ibpm, bpm.name, bpm.sb, x, y, I, ts))
        #print ibpm, ts
        #
    dcct2 = ap.catools.caget(pv_dcct)
    mdt = _maxTimeSpan([v[6] for v in data])
    if single_trig:
        if mdt > 1.0:
            print "WARNING: BPM timestamp differs > 1 sec"
        #print "Timestamp variation:", np.std(ap.catools.caget(br_ddrtrig_ts_pvs))
        #time.sleep(5)
        # restore the br_trig_pvs
        ap.catools.caput(pv_evg, 0, wait=True, timeout=tc)
        ap.catools.caput(br_trig_pvs, 1, wait=True, timeout=tc)
        ap.catools.caput(br_wfmsel_pvs, wfsel0, wait=True, timeout=tc)
        ap.catools.caput(br_wfm_enable_pvs, wfenb0, wait=True, timeout=tc)

    t1 = datetime.now()
    output_dir = kwargs.get("output_dir", "")
    output_file = kwargs.get("output_file", 
                             os.path.join(output_dir, 
                                          t0.strftime("bpm_tbt_0_%Y_%m_%d_%H%M%S.hdf5")))
    if kwargs.has_key("output_dir" ) or kwargs.has_key("output_file"):
        saveBpmFa(output_file, data, group=kwargs.get("h5group", "/"), dt=mdt,
                  dcct_data = (dcct1, dcct2))
        return data, output_file
    else:
        time.sleep(1)

    names = [v[1] for v in data]
    x, y = [v[3] for v in data], [v[4] for v in data]
    s = [v[5] for v in data]
    return names, x, y, s


def saveBpmTbt(fname, data, group="/", dt = None, dcct_data = None):
    # open with default 'a' mode: rw if exists, create otherwise
    h5f = h5py.File(fname)
    if group != "/":
        grp = h5f.create_group(group)
    grp = h5f[group]
    grp["bpm_index"] = np.array([v[0] for v in data], 'i')
    grp["bpm_name"]  = np.array([v[1] for v in data], "S")
    grp["bpm_sb"]    = [v[2] for v in data]
    grp["data_tbt_x"] = np.array([v[3] for v in data])
    grp["data_tbt_y"]   = np.array([v[4] for v in data])
    grp["data_tbt_sum"] = np.array([v[5] for v in data])
    grp["data_tbt_timestamp"] = np.array([v[6] for v in data], "S")
    if dt is not None:
        grp.attrs["timespan"] = dt
    if dcct_data:
        for i,d in enumerate(dcct_data):
            grp["dcct_%d" % i] = np.array(d, 'd')
    h5f.close()


def saveBpmFa(fname, data, group="/", dt = None, dcct_data = None):
    # open with default 'a' mode: rw if exists, create otherwise
    h5f = h5py.File(fname)
    if group != "/":
        grp = h5f.create_group(group)
    grp = h5f[group]
    grp["bpm_index"] = np.array([v[0] for v in data], 'i')
    grp["bpm_name"]  = np.array([v[1] for v in data], "S")
    grp["bpm_sb"]    = [v[2] for v in data]
    grp["data_fa_x"] = np.array([v[3] for v in data])
    grp["data_fa_y"]   = np.array([v[4] for v in data])
    grp["data_fa_sum"] = np.array([v[5] for v in data])
    grp["data_fa_timestamp"] = np.array([v[6] for v in data], "S")
    if dt is not None:
        grp.attrs["timespan"] = dt
    if dcct_data:
        for i,d in enumerate(dcct_data):
            grp["dcct_%d" % i] = np.array(d, 'd')
    h5f.close()


def pltRmCol(m, dx, raw_data, labels = []):
    """
    plot the column of response matrix, see also :func:`catools.measCaRmCol`
    """
    import matplotlib.pylab as plt
    fig = plt.figure(figsize=(10, len(m)*2), dpi=100)
    for i in range(len(m)):
        y   = np.average(raw_data[i,:,:], axis=1)
        err = np.std(raw_data[i,:,:], axis=1)

        xl = (dx[-1] - dx[0])
        t = np.linspace(dx[0] - 0.075*xl, dx[-1]+0.075*xl, 10)
        c = np.average(raw_data[i,:,:])
        yr = [t[j] * m[i] + c for j in range(len(t))]

        plt.subplot(len(m), 1, i+1)
        plt.errorbar(dx, y, yerr=err, )
        plt.plot(t, yr, '-')


def calcBrRmCol(fname, group, nbpm=36, plot=False, faslice=(10,100)):
    """
    fname - output file name
    group - group name in HDF5 file (corrector SP PV)
    nbpm - BR has 36 bpms
    plot - whether plot or not
    faslice - slice range of FA waveform data
    """
    
    h5f = h5py.File(fname, 'r')
    grps = []
    for g in h5f.keys():
        if g != group: continue
        for g1 in h5f[g].keys():
            m = re.match(r"dx([0-9]+)__pt([0-9]+)", g1)
            if not m: continue
            grps.append((int(m.group(1)), int(m.group(2))))
    if len(grps) == 0: return None
    ndx = max([i for i, j in grps]) + 1
    npt = max([j for i, j in grps]) + 1
    i0, i1 = faslice
    mxij = np.zeros((nbpm, ndx, npt), 'd')
    myij = np.zeros((nbpm, ndx, npt), 'd')
    # show data for iBPM, for turns i0:i1
    dxlst = h5f["%s/dxlst" % group]
    #print "Dx list", np.array(dxlst)
    for i in range(ndx):
        for j in range(npt):
            h5g = h5f["%s/dx%d__pt%d" % (group, i, j)]
            xfa, yfa = h5g["data_fa_x"], h5g["data_fa_y"]
            #plt.subplot(211)
            #plt.plot(xfa[ibpm, i0:i1], 'r-')
            #plt.subplot(212)
            #plt.plot(yfa[ibpm, i0:i1], 'g-')
            xobt = np.average(xfa[:,i0:i1], axis=1)
            yobt = np.average(xfa[:,i0:i1], axis=1)
            mxij[:,i,j] = xobt
            myij[:,i,j] = yobt
    if plot:
        for i in range(ndx):
            plt.title(group)
            for j in range(npt):
                plt.errorbar(range(len(xobt)), xobt, yerr=np.std(xfa[:,i0:i1], axis=1), color="r")
                plt.errorbar(range(len(yobt)), yobt, yerr=np.std(yfa[:,i0:i1], axis=1), color='g')
            plt.show()

    mcol, pol = [], []
    for i in range(nbpm):
        px = np.polyfit(dxlst, np.average(mxij[i,:,:], axis=1), 1)
        py = np.polyfit(dxlst, np.average(myij[i,:,:], axis=1), 1)
        mcol.append((px[-2], py[-2]))
        pol.append((px, py))
    if plot:
        for i in range(nbpm):
            px, py = pol[i]
            t = np.linspace(dxlst[0], dxlst[-1], 10)
            plt.title("BPM %d" % i)
            plt.plot(dxlst, np.average(mxij[i,:,:], axis=1), 'bo')
            plt.errorbar(dxlst, np.average(mxij[i,:,:], axis=1), yerr=np.std(mxij[i,:,:], axis=1), color='b')
            plt.plot(t, np.polyval(px, t), 'r-')
            plt.show()
    return mcol
