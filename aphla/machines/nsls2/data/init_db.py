import os
import sys
import re
import channelfinder
from channelfinder import ChannelFinderClient
from channelfinder import Channel, Property, Tag
import aphla as ap
from aphla.machines import utils

cfsurl = os.environ.get(
    'HLA_CFS_URL', 
    'https://channelfinder.nsls2.bnl.gov:8181/ChannelFinder')

import logging
logging.basicConfig(
    filename='log_init_db.txt',
    format='%(asctime)s - %(name)s [%(levelname)s]: %(message)s',
    level=logging.DEBUG)

cfs_pat = [
    # PV pattern, npv, properties
    ("SR:C*-MG{PS:C*:Sp1-SP", 180,
     [('elemHandle', 'put'), ('system', 'SR'),
      ('elemType', 'COR'), ('elemField', 'x')]),
    #
    ("SR:C*-MG{PS:C*}I:Ps1DCCT1-I", 180,
     [('elemHandle', 'get'), ('system', 'SR'),
      ('elemType', 'COR'), ('elemField', 'x')]),
    #
    ("SR:C*-MG{PS:C*:Sp2-SP", 180,
     [('elemHandle', 'put'), ('system', 'SR'),
      ('elemType', 'COR'), ('elemField', 'y')]),
    #
    ("SR:C*-MG{PS:C*}I:Ps2DCCT1-I", 180,
     [('elemHandle', 'get'), ('system', 'SR'),
      ('elemType', 'COR'), ('elemField', 'y')]),
    #
    ("SR:C*-BI{BPM:*}Pos:X-I", -1,
     [('elemHandle', 'get'), ('system', 'SR'),
      ('elemType', 'BPM'), ('elemField', 'x')]),
    #
    ("SR:C*-BI{BPM:*}Pos:Y-I", -1,
     [('elemHandle', 'get'), ('system', 'SR'),
      ('elemType', 'BPM'), ('elemField', 'y')]),
    ("SR:C*-MG{PS:Q*:Sp1-SP", 300,
     [('elemHandle', 'put'), ('system', 'SR'),
      ('elemType', 'QUAD'), ('elemField', 'b1')]),
    ("SR:C*-MG{PS:Q*}I:Ps1DCCT1-I", 300,
     [('elemHandle', 'get'), ('system', 'SR'),
      ('elemType', 'QUAD'), ('elemField', 'b1')]),
    ("SR:C*-MG{PS:S*:Sp1-SP", -1,
     [('elemHandle', 'put'), ('system', 'SR'),
      ('elemType', 'SEXT'), ('elemField', 'b2')]),
    ("SR:C*-MG{PS:S*}I:Ps1DCCT1-I", -1,
     [('elemHandle', 'get'), ('system', 'SR'),
      ('elemType', 'SEXT'), ('elemField', 'b2')]),
]

def download_nsls2_cfs(url, fname):
    cf = ChannelFinderClient(BaseURL=url)
    pvs = []
    for pvpat, npv, prpts  in cfs_pat:
        chs = cf.find(name=pvpat, property=[("hostName", "*"), ("iocName","*")])
        if chs is None:
            raise RuntimeError("can not find any matching pvs {0}".format(
                pvpat))

        logging.info("find {0} pvs for name='{1}'".format(len(chs), pvpat))
        if npv == 0 or (npv > 0 and len(chs) != npv):
            raise RuntimeError("pat='%s', We should have %d Cors (%d)" % (
                pvpat, npv, len(chs)))
        dprpt = dict(prpts)
        for ch in chs:
            pvs.append([ch.Name, dprpt['elemHandle'], "", "",
                        dprpt["elemType"], dprpt["elemField"]])
    return pvs

def match_bpm(elems, pv):
    g = re.match(r"SR:C([0-9][0-9]?)-BI{BPM:([0-9]+)}.*", pv)
    if not g: return "", "0"
    icell, idx = int(g.group(1)), int(g.group(2))
    cell = "C%02d" % icell
    matched = []
    for e in elems:
        if e[6] == cell and e[2] == "BPM": matched.append(e)
    logging.info("found {0} BPM records for '{1}'".format(len(matched), pv))
    e = matched[idx-1]
    logging.info("pick {0}".format(e))
    return e[0], e[1]


def match_magnet(elems, pv):
    g = re.match(r"SR:(C[0-9][0-9]?)-MG{PS:([A-Z]+[0-9]+)([AB]?)}.*", pv)
    if not g: return "", "0"
    cell, fam = g.group(1), g.group(2)
    matched = []
    for e in elems:
        if e[6] != cell: continue
        if e[9].find(fam) < 0: continue
        if g.group(3) and e[8] != g.group(3): continue
        matched.append(e)
    logging.info("found {0} BPM records for '{1}', cell={2}, fam={3}".format(
        len(matched), pv, cell, fam))
    if not matched:
        logging.warn("element not found for {0}".format(pv))
        return "", "0"

    if len(matched) > 1:
        msg = "duplicate data for {0}: {1}".format(pv, matched)
        logging.error(msg)
        raise RuntimeError(msg)

    e = matched[0]
    logging.info("pick {0}".format(e))
    return e[0], e[1]

def match_magnet_chained(elems, pv):
    """given a pv, return sorted element list which are chained"""
    logging.info("matching '{0}'".format(pv))
    g = re.match(r"SR:(C[0-9]+)-MG{PS:(S[^}]+)}.*", pv)
    if not g: return [], []
    cell, gname = g.group(1), g.group(2)
    logging.info("matched {0}, {1}".format(cell, gname))
    name, idx = [], []
    if re.match(r"(S[HLM][0-9][AB])-(P[0-9])", gname):
        for e in elems:
            if e[0][:3] + e[0][-1] == gname[:4].lower():
                name.append(e[0])
                idx.append(e[1])
    elif re.match(r"(S[HLM][0-9])-(P[0-9])", gname):
        for e in elems:
            if e[0][:3] == gname[:3].lower():
                name.append(e[0])
                idx.append(e[1])
                continue
    elif re.match(r"(S[HLM][0-9])-(DW[0-9])", gname):
        pass
    elif re.match(r"SQK.+", gname):
        pass
    else:
        raise RuntimeError("Unknow pattern: {0}".format(pv))

    if name and len(name) != 30:
        raise RuntimeError("in correct number of sextupoles:"
                           "{0} (30)".format(len(name)))
    return name, idx


def match_element_name(felem, pvs):
    elems = [r.split(",") for r in open(felem, 'r').readlines()]
    # 
    sextpvs = {}
    for i,pv in enumerate(pvs):
        if pv[4] == "SEXT": 
            # chained element
            name, idx = match_magnet_chained(elems, pv[0])
            sextpvs[pv[0]] = [ [pv[0], pv[1], name[i], idx[i], pv[4], pv[5]]
                               for i in range(len(name)) ]
            continue
        elif pv[4] == "BPM":
            pv[2], pv[3] = match_bpm(elems, pv[0])
        elif pv[4] in ["COR", "QUAD"]:
            pv[2], pv[3] = match_magnet(elems, pv[0])
        else:
            print pv
            raise RuntimeError("unknown type")

    newpvs = []
    for pv in pvs:
        if pv[0] not in sextpvs: newpvs.append(pv)

    for k,v in sextpvs.items():
        newpvs.extend(v)

    return newpvs

def output_pvs(fname, pvs):
    f = open(fname, "w")
    for rec in pvs:
        try:
            i = int(rec[3])
        except:
            print rec
            raise
        f.write(",".join(rec) + "\n")
    f.close()


if __name__ == "__main__":
    fs1, fs2 = "va_elements.txt", "va_pvs.csv"
    f1, f2, f3 = "test_elem.txt", "test_pvs.txt", "sr.sqlite"
    utils.convNSLS2LatTable(f1, fs1)
    pvs = download_nsls2_cfs(cfsurl, fs2)
    pvs = match_element_name(f1, pvs)
    output_pvs(f2, pvs)
    #sys.exit(0)

    #utils.convVirtAccPvs(f2, fs2)
    utils.createSqliteDb(f3, f1, f2, latname="SR", system="SR")

    os.remove(f1)
    os.remove(f2)
    #convVirtAccTwiss(f1, "./tpsv1/tps-twiss.txt", grpname=True)
    #convVirtAccPvs(f2, "./tpsv1/TDMB1826_OB_Chamb_ID.csv")
    #createSqliteDb(f3, f1, f2, name_index=True)


