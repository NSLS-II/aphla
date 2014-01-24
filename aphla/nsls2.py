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

    
