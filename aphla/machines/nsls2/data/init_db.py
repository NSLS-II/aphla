import os
import sys
import re
import sqlite3

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

cfs_pat = {
    "COR": [
    # PV pattern, npv, properties
    ("SR:C*-MG{PS:C*:Sp1-SP",       "put", "", "", "COR", "x"), 
    ("SR:C*-MG{PS:C*}I:Ps1DCCT1-I", "get", "", "", "COR", "x"),
    ("SR:C*-MG{PS:C*:Sp2-SP",       "put", "", "", "COR", "y"),
    ("SR:C*-MG{PS:C*}I:Ps2DCCT1-I", "get", "", "", "COR", "y")],
    "BPM": [
    ("SR:C*-BI{BPM:*}Pos:X-I",      "get", "", "", "BPM", "x"),
    ("SR:C*-BI{BPM:*}Pos:Y-I",      "get", "", "", "BPM", "y")],
    "QUAD": [
    ("SR:C*-MG{PS:Q*:Sp1-SP",       "put", "", "", "QUAD", "b1"),
    ("SR:C*-MG{PS:Q*}I:Ps1DCCT1-I", "get", "", "", "QUAD", "b1")],
    "SKQUAD": [
    ("SR:C*-MG{PS:SQ*:Sp1-SP",       "put", "", "", "SKQUAD", "b1"),
    ("SR:C*-MG{PS:SQ*}I:Ps1DCCT1-I", "get", "", "", "SKQUAD", "b1")],
    "SEXT": [
    ("SR:C*-MG{PS:S*:Sp1-SP",       "put", "", "", "SEXT", "b2"),
    ("SR:C*-MG{PS:S*}I:Ps1DCCT1-I", "get", "", "", "SEXT", "b2")]
}

pentent = {}
for i in range(30):
    pi, pj = divmod(i, 6)
    j = i + 23
    if j > 30: j = j - 30
    pentent.setdefault("P%d" % (pi+1,), []).append("C%02d" % j)
#for k in sorted(pentent.keys()):
#    print k,pentent[k]

def generate_sr_bpm_pvs(fname):
    f = open(fname, 'w')
    for xy in ["X", "Y"]:
        for icell in range(1, 31):
            for i in range(1, 7):
                f.write("SR:C%d-BI{BPM:%d}Pos:%s-I\n" % (icell, i, xy))
    f.close()

def init_bpm_txt(elems, fsrc, fname):
    # sort BPM names in lattice
    bpms = {}
    for e in elems:
        if e[2] != "BPM": continue
        # ignore User BPM
        if e[0].startswith("pu"): continue

        k = "C%d" % (int(e[6][1:]),)
        bpms.setdefault(k, []).append((e[0], e[1],))
    #for k,v in bpms.items(): print k, v
    
    f = open(fname, "w")
    bpmpvs = {}
    for pv in [r.strip() for r in open(fsrc, 'r').readlines()]:
        g = re.match(r"SR:(C[0-9][0-9]?)-BI{BPM:([0-9]+)}Pos:([XY])-I", pv)
        if not g: 
            raise RuntimeError("unknown PV: '{0}'".format(pv))
        bpmpvs.setdefault(g.group(1), []).append(pv)

    for k,pvs in bpmpvs.items():
        #print k, pvs
        names = bpms.get(k, [])
        if len(names)*2 != len(pvs):
            print "ERROR: BPM in {0} does not agree {1} != {2}".format(
                k, len(pvs), len(names))
            print pvs
            print names
            sys.exit(0)
        for pv in pvs:
            g = re.match(r"SR:(C[0-9][0-9]?)-BI{BPM:([0-9]+)}Pos:([XY])-I", pv)
            r = bpms[k][int(g.group(2)) - 1]
            f.write("%s,get,%s,%s,BPM,%s\n" % (
                pv, r[0], r[1], g.group(3).lower()))
    f.close()

    
def init_bpm(elems, url, patl, fname):
    # sort BPM names in lattice
    bpms = {}
    for e in elems:
        if e[2] != "BPM": continue
        # ignore User BPM
        if e[0].startswith("pu"): continue

        k = "C%d" % (int(e[6][1:]),)
        bpms.setdefault(k, []).append((e[0], e[1],))
    for k,v in bpms.items(): print k, v
    
    cf = ChannelFinderClient(BaseURL=url)
    f = open(fname, "w")
    for pvpat, hdl, name, idx, etp, fld in patl:
        # for each pattern, sort PV and check against with elements.
        bpmpvs = {}
        chs = cf.find(name=pvpat, property=[("hostName", "*"),
                                            ("iocName","*")])
        for ch in chs:
            g = re.match(r"SR:(C[0-9][0-9]?)-BI{BPM:([0-9]+)}.*", ch.Name)
            if not g: 
                raise RuntimeError("unknown PV: '{0}'".format(ch.Name))
            bpmpvs.setdefault(g.group(1), []).append(ch.Name)

        for k,pvs in bpmpvs.items():
            #print k, pvs
            names = bpms.get(k, [])
            if len(names) != len(pvs):
                #raise RuntimeError("BPM in {0} does not agree {1} != {2}".format(k, len(pvs), len(names)))
                print "ERROR: BPM in {0} does not agree {1} != {2}".format(k, len(pvs), len(names))
            for pv in pvs:
                g = re.match(r"SR:(C[0-9][0-9]?)-BI{BPM:([0-9]+)}.*", pv)
                r = bpms[k][int(g.group(2)) - 1]
                f.write("%s,%s,%s,%s,BPM,%s\n" % (pv, hdl, r[0], r[1], fld))
    f.close()


def init_quad(elems, url, patl, fname):
    cf = ChannelFinderClient(BaseURL=url)
    f = open(fname, "w")
    for pvpat, hdl, name, idx, etp, fld in patl:
        chs = cf.find(name=pvpat, property=[("hostName", "*"),
                                            ("iocName","*")])
        for ch in chs:
            pv = ch.Name
            g = re.match(r"SR:(C[0-9][0-9]?)-MG{PS:([A-Z]+[0-9]+)([AB]?)}.*",
                         ch.Name)
            if not g: 
                raise RuntimeError("unknown PV: '{0}'".format(ch.Name))
            cell, fam = g.group(1), g.group(2)
            matched = []
            for e in elems:
                if e[6] != cell: continue
                if e[9].find(fam) < 0: continue
                if g.group(3) and e[8] != g.group(3): continue
                matched.append(e)

            logging.info("found {0} QUAD records for '{1}', cell={2}, fam={3}".format(
                len(matched), pv, cell, fam))
            if not matched:
                logging.warn("element not found for {0}".format(pv))
                raise RuntimeError("unmatched quad PV: {0}".format(ch.Name))

            if len(matched) > 1:
                msg = "duplicate data for {0}: {1}".format(pv, matched)
                logging.error(msg)
                raise RuntimeError(msg)

            e = matched[0]
            logging.info("pick {0}".format(e))
            f.write("%s,%s,%s,%s,QUAD,%s\n" % (ch.Name, hdl, e[0], e[1], fld))
    f.close()


def init_skquad(elems, url, patl, fname):
    cf = ChannelFinderClient(BaseURL=url)
    f = open(fname, "w")
    for pvpat, hdl, name, idx, etp, fld in patl:
        chs = cf.find(name=pvpat, property=[("hostName", "*"),
                                            ("iocName","*")])
        for ch in chs:
            pv = ch.Name
            g = re.match(r"SR:(C[0-9][0-9]?)-MG{PS:SQK([A-Z][0-9])([AB]?)}.*",
                         ch.Name)
            if not g: 
                raise RuntimeError("unknown PV: '{0}'".format(ch.Name))
            cell, fam = g.group(1), g.group(2)
            matched = []
            for e in elems:
                if e[2] != "SKQUAD": continue
                # cell
                if e[6] != cell: continue
                # symmetry
                if g.group(3) and e[8] != g.group(3): continue
                matched.append(e)

            logging.info("found {0} SKQUAD records for '{1}', cell={2}, fam={3}".format(
                len(matched), pv, cell, fam))
            if not matched:
                logging.warn("element not found for {0}".format(pv))
                raise RuntimeError("unmatched quad PV: {0}".format(ch.Name))

            if len(matched) > 1:
                msg = "duplicate data for {0}: {1}".format(pv, matched)
                logging.error(msg)
                raise RuntimeError(msg)

            e = matched[0]
            logging.info("pick {0}".format(e))
            f.write("%s,%s,%s,%s,SKQUAD,%s\n" % (ch.Name, hdl, e[0], e[1], fld))
    f.close()


def init_cor(elems, url, patl, fname):
    cf = ChannelFinderClient(BaseURL=url)
    f = open(fname, "w")
    for pvpat, hdl, name, idx, etp, fld in patl:
        chs = cf.find(name=pvpat, property=[("hostName", "*"),
                                            ("iocName","*")])
        for ch in chs:
            pv = ch.Name
            g = re.match(r"SR:(C[0-9][0-9]?)-MG{PS:([A-Z]+[0-9]+)([AB]?)}.*",
                         ch.Name)
            if not g: 
                raise RuntimeError("unknown PV: '{0}'".format(ch.Name))
            cell, fam = g.group(1), g.group(2)
            matched = []
            for e in elems:
                if e[6] != cell: continue
                if e[9].find(fam) < 0: continue
                if g.group(3) and e[8] != g.group(3): continue
                matched.append(e)

            logging.info("found {0} COR records for '{1}', cell={2}, fam={3}".format(
                len(matched), pv, cell, fam))
            if not matched:
                logging.warn("element not found for {0}".format(pv))
                raise RuntimeError("unmatched quad PV: {0}".format(ch.Name))

            if len(matched) > 1:
                msg = "duplicate data for {0}: {1}".format(pv, matched)
                logging.error(msg)
                raise RuntimeError(msg)

            e = matched[0]
            logging.info("pick {0}".format(e))
            f.write("%s,%s,%s,%s,COR,%s\n" % (ch.Name, hdl, e[0], e[1], fld))
    f.close()


def match_sextupoles(elems, pv):
    sxt_p    = re.compile(r"SR:(C[0-9]+)-MG{PS:(S[HLM][0-9])-(P[1-5])}.*")
    sxt_dw   = re.compile(r"SR:(C[0-9]+)-MG{PS:(S[HLM][0-9])-(DW[0-9]+)}.*")
    sxt_ab_p = re.compile(r"SR:(C[0-9]+)-MG{PS:(S[HLM][0-9][AB])-(P[1-5])}.*")

    matched = []
    g = sxt_p.match(pv)
    if g:
        for i,e in enumerate(elems):
            # check cell in pentent
            if e[6] not in pentent[g.group(3)]: continue
            if e[0][:3] == g.group(2).lower():
                matched.append(i)
        return matched

    g = sxt_ab_p.match(pv)
    if g:
        for i,e in enumerate(elems):
            if e[6] not in pentent[g.group(3)]: continue
            if e[0][:3] + e[0][-1] == g.group(2).lower(): matched.append(i)
        return matched

    raise RuntimeError("unknown Sextupole PV: '{0}'".format(pv))


def init_sext(elems, url, patl, fname):
    cf = ChannelFinderClient(BaseURL=url)
    skquad   = re.compile(r"SR:(C[0-9]+)-MG{PS:(SQ[A-Z0-9]+)}.*")
    sxt_dw   = re.compile(r"SR:(C[0-9]+)-MG{PS:(S[HLM][0-9])-(DW[0-9]+)}.*")
    f = open(fname, "w")
    for pvpat, hdl, name, idx, etp, fld in patl:
        chs = cf.find(name=pvpat, property=[("hostName", "*"),
                                            ("iocName","*")])
        for ch in chs:
            if skquad.match(ch.Name): continue
            if sxt_dw.match(ch.Name): continue
            matched = match_sextupoles(elems, ch.Name)

            logging.info("elements found for pv '{0}': {1}".format(
                        ch.Name, [elems[i][0] for i in matched]))
            if not matched:
                raise RuntimeError("unknown Sextupole PV: '{0}'".format(pv))
            if len(matched) != 6:
                raise RuntimeError("should be 6 sextupoles, {0} found".format(
                    len(matched)))
            for e in [elems[i] for i in matched]:
                f.write("%s,%s,%s,%s,SEXT,%s\n" % (ch.Name, hdl, e[0], e[1], fld))
    f.close()


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
        for r in v: print "    ", r
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



def _update_sqlite_elements(fdb, elems, **kwarg):
    conn = sqlite3.connect(fdb)
    # save byte string instead of the default unicode
    conn.text_factory = str
    c = conn.cursor()
    # ph1g2c30a,800,BPM,4.935,0.0,4.935,C30,G2,A,PH1
    dat = [(r[0],r[1],r[2],r[4],r[5],r[6],r[7],r[8],r[9])
           for r in elems]
    c.executemany("""INSERT OR REPLACE INTO elements """
              """(elemName,elemIndex,elemType,elemLength,elemPosition,"""
              """cell,girder,symmetry,elemGroups) values """
              """(?,?,?,?,?,?,?,?,?)""", dat)
    conn.commit()
    conn.close()
    pass

def _update_sqlite_pvs(fdb, pvs, **kwarg):
    systag = "aphla.sys.%s" % (kwarg.get("latname", ""),)
    conn = sqlite3.connect(fdb)
    # save byte string instead of the default unicode
    conn.text_factory = str
    c = conn.cursor()
    # SR:C01-MG{PS:CH2B}I:Sp1-SP,put,ch2g6c01b,16100,COR,x
    dat = [(r[0],r[1],r[2],r[5],systag) for r in pvs]
    c.executemany("""INSERT OR REPLACE INTO pvs """
                  """(pv,elemHandle,elemName,elemField,tags) """
                  """values (?,?,?,?,?)""", dat)
    conn.commit()
    conn.close()
    pass


def updateSqliteDb(fdb, **kwarg):
    if kwarg.get("felem", None):
        felem = kwarg.pop("felem")
        elems = [v.strip().split(",") for v in open(felem, 'r').readlines()]
        _update_sqlite_elements(fdb, elems, **kwarg)

    if kwarg.get("fpv", None):
        fpv = kwarg.pop("fpv")
        pvs = [v.strip().split(",") for v in open(fpv, 'r').readlines()]
        _update_sqlite_pvs(fdb, pvs, **kwarg)

def checkSqliteDb(fdb):
    conn = sqlite3.connect(fdb)
    # save byte string instead of the default unicode
    conn.text_factory = str
    c = conn.cursor()

    c.execute("""select * from ("""
              """select elements.elemName,elements.elemIndex,"""
              """elements.elemType,pvs.pv """
              """from elements LEFT JOIN pvs """
              """on elements.elemName=pvs.elemName) """
              """where pv is NULL""")
    etp = {}
    for row in c.fetchall():
        etp.setdefault(row[2], []).append(row[0])

    print "Elements have no PVs:"
    for k,v in etp.items():
        print "  ", k, len(v)

    c.execute("""select * from ("""
              """select pvs.pv,pvs.elemName,elements.elemType """
              """from pvs LEFT JOIN elements """
              """on elements.elemName=pvs.elemName) """
              """where elemName is NULL""")
    pvs = [r[0] for r in c.fetchall()]
    if pvs: 
        print "Some Pvs ({0}) are alone: {1}".format(len(pvs), pvs)
    else:
        print "All PVs have owners"

    conn.close()

    pass


if __name__ == "__main__":
    dbfname = "nsls2_sr.sqlite"
    ap.apdata.createLatticePvDb(dbfname)

    f1, fs1 = "sr_elements.txt", "va_elements.txt"
    #utils.convNSLS2LatTable(f1, fs1)
    updateSqliteDb(dbfname, felem=f1)

    elems = [r.strip().split(",") for r in open(f1, 'r').readlines()]

    #init_bpm(elems, cfsurl, cfs_pat["BPM"], "sr_pvs_BPM.txt")
    #generate_sr_bpm_pvs("sr_pvs_BPM_generated_raw.txt")
    #init_bpm_txt(elems, "sr_pvs_BPM_generated_raw.txt", "sr_pvs_BPM.txt")
    updateSqliteDb(dbfname, fpv="sr_pvs_BPM.txt", latname="SR")
    #init_quad(elems, cfsurl, cfs_pat["QUAD"], "sr_pvs_QUAD.txt")
    updateSqliteDb(dbfname, fpv="sr_pvs_QUAD.txt", latname="SR")
    #init_skquad(elems, cfsurl, cfs_pat["SKQUAD"], "sr_pvs_SKQUAD.txt")
    updateSqliteDb(dbfname, fpv="sr_pvs_SKQUAD.txt", latname="SR")
    #init_cor(elems, cfsurl, cfs_pat["COR"], "sr_pvs_COR.txt")
    updateSqliteDb(dbfname, fpv="sr_pvs_COR.txt", latname="SR")
    #init_sext(elems, cfsurl, cfs_pat["SEXT"], "sr_pvs_SEXT.txt")
    updateSqliteDb(dbfname, fpv="sr_pvs_SEXT.txt", latname="SR")

    checkSqliteDb(dbfname)

