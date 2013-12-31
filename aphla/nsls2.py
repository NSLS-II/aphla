"""
Some NSLS2 specific routines
=============================

:Author: Lingyun Yang
:Date: 2013-12-09 11:50

"""

import os
import time
from datetime import datetime
import numpy as np
import aphla as ap
import h5py

HLA_DATA_DIR="/epics/data/aphla/data/nsls2"

def brBpmTbt(**kwargs):
    t0 = datetime.now()
    lat = ap.machines.getLattice()
    if lat.name != "BR":
        raise RuntimeError("the current lattice is not 'BR': %s" % lat.name)

    pv_evg = "BR-BI{BPM}Evt:Single-Cmd"
    br_trig_pvs, br_wfmsel_pvs = [], []
    br_ddrts_pvs = [] # timestamp
    bpms = ap.getElements("BPM")
    # did not consider the 'ddrTbtWfEnable' PV
    for bpm in bpms:
        pvx = bpm.pv(field="x")[0]
        #print bpm.name, pvh, caget(pvh)
        br_trig_pvs.append(pvx.replace("Pos:X-I", "Trig:TrigSrc-SP"))
        br_wfmsel_pvs.append(pvx.replace("Pos:X-I", "DDR:WfmSel-SP"))
        br_ddrts_pvs.append(pvx.replace("Pos:X-I", "TS:DdrTrigDate-I"))
    # save initial val
    wfsel0   = ap.catools.caget(br_wfmsel_pvs)
    trigsrc0 = ap.catools.caget(br_trig_pvs)
    ddrts0   = ap.catools.caget(br_ddrts_pvs)

    # set the trigger internal, TBT waveform
    ap.catools.caput(br_wfmsel_pvs, 1, wait=True)
    ap.catools.caput(br_trig_pvs, 0, wait=True)

    # set the event
    ap.catools.caput(pv_evg, 1, wait=True)
    time.sleep(kwargs.get("sleep", 2))

    data = []
    for ibpm,bpm in enumerate(bpms):
        x, y, I = bpm.xtbt, bpm.ytbt, bpm.Itbt
        data.append((ibpm, bpm.name, bpm.sb, x, y, I, ddrts0[ibpm]))
        #

    # restore the br_trig_pvs
    ap.catools.caput(pv_evg, 0, wait=True)
    ap.catools.caput(br_trig_pvs, 1, wait=True)
    ap.catools.caput(br_wfmsel_pvs, wfsel0, wait=True)
    t1 = datetime.now()
    if kwargs.get("output_dir", None):
        output_dir = kwargs["output_dir"]
        fname = os.path.join(output_dir, 
                             t0.strftime("bpm_tbt_0_%Y_%m_%d_%H%M%S.hdf5"))
        saveBpmTbt(fname, kwargs.get("output_mode", "w"), data)
        return data, fname
    else:
        time.sleep(1)
    return data


def brBpmFa(**kwargs):
    t0 = datetime.now()
    lat = ap.machines.getLattice()
    if lat.name != "BR":
        raise RuntimeError("the current lattice is not 'BR': %s" % lat.name)

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
    ddrts0   = ap.catools.caget(br_ddrts_pvs)

    # set the trigger internal, TBT waveform
    ap.catools.caput(br_wfmsel_pvs, 2, wait=True)
    ap.catools.caput(br_trig_pvs, 0, wait=True)
    ap.catools.caput(br_wfm_enable_pvs, 1, wait=True)

    # set the event
    ap.catools.caput(pv_evg, 1, wait=True)
    time.sleep(kwargs.get("sleep", 8))

    data = []
    for ibpm,bpm in enumerate(bpms):
        x, y, I = bpm.xfa, bpm.yfa, bpm.Ifa
        ts = ap.catools.caget(br_ddrts_pvs[ibpm])
        if ts != ddrts0[ibpm]:
            print "Timestamp changed for '%s': %s %s" % (
                bpm.name, ddrts0[ibpm], ts)
        data.append((ibpm, bpm.name, bpm.sb, x, y, I, ts))
        #print ibpm, ts
        #

    #print "Timestamp variation:", np.std(ap.catools.caget(br_ddrtrig_ts_pvs))
    #time.sleep(5)
    # restore the br_trig_pvs
    ap.catools.caput(pv_evg, 0, wait=True)
    ap.catools.caput(br_trig_pvs, 1, wait=True)
    ap.catools.caput(br_wfmsel_pvs, wfsel0, wait=True)
    ap.catools.caput(br_wfm_enable_pvs, wfenb0, wait=True)

    t1 = datetime.now()
    if kwargs.get("output_dir", None):
        output_dir = kwargs["output_dir"]
        fname = os.path.join(output_dir, 
                             t0.strftime("bpm_fa_0_%Y_%m_%d_%H%M%S.hdf5"))
        saveBpmFa(fname, kwargs.get("output_mode", "w"), data)
        return data, fname
    else:
        time.sleep(1)
    return data

def saveBpmTbt(fname, mode, data):
    h5f = h5py.File(fname, mode)
    h5f["bpm_index"] = np.array([v[0] for v in data], 'i')
    h5f["bpm_name"]  = np.array([v[1] for v in data], "S")
    h5f["bpm_sb"]    = [v[2] for v in data]
    h5f["data_tbt_x"] = np.array([v[3] for v in data])
    h5f["data_tbt_y"]   = np.array([v[4] for v in data])
    h5f["data_tbt_sum"] = np.array([v[5] for v in data])
    h5f["data_tbt_timestamp"] = np.array([v[6] for v in data], "S")
    h5f.close()


def saveBpmFa(fname, mode, data):
    h5f = h5py.File(fname, mode)
    h5f["bpm_index"] = np.array([v[0] for v in data], 'i')
    h5f["bpm_name"]  = np.array([v[1] for v in data], "S")
    h5f["bpm_sb"]    = [v[2] for v in data]
    h5f["data_fa_x"] = np.array([v[3] for v in data])
    h5f["data_fa_y"]   = np.array([v[4] for v in data])
    h5f["data_fa_sum"] = np.array([v[5] for v in data])
    h5f["data_fa_timestamp"] = np.array([v[6] for v in data], "S")
    h5f.close()


def pltRmCol(m, dx, raw_data, labels = []):
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


