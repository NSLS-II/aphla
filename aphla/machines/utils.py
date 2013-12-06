import os
import sys
import re
import sqlite3
from ..apdata import createLatticePvDb
from ..chanfinder import ChannelFinderAgent

from channelfinder import ChannelFinderClient
from channelfinder import Channel, Property, Tag

def _nsls2_filter_element_type_group(elemlst):
    """
    ignore drift.
    TRIMD -> COR, [HCOR, VCOR]
    """
    relst, rglst = [], []
    for i,elem in enumerate(elemlst):
        idx, name, tp, s0, L, s1 = elem
        grp, cell, girder, symm = "", "", "", ""
        g = re.match(r"([A-Z0-9]+)(G[0-9])(C[0-9][0-9])(.+)", name, re.I)
        if g: 
            grp, girder, cell, symm = [g.group(i) for i in range(1,5)]

        if tp in ['DRIF', 'MARK']:
            # ignore drift
            pass
        elif tp == "QUAD" and name.startswith("SQ"):
            relst.append([name, idx, "SKQUAD", s0, L, s1, cell, girder,
                          symm, grp])
        elif tp in ['BPM', 'QUAD', 'SEXT', 'IVU', 'DW', 'EPU']:
            relst.append([name, idx, tp, s0, L, s1, cell, girder, symm, grp])
        elif tp in ['TRIM', 'TRIMD']:
            newgrp =";".join(sorted([grp, "HCOR", "VCOR"]))
            relst.append([name, idx, "COR", s0, L, s1,
                          cell, girder, symm, newgrp])
        elif tp == 'FTRIM':
            relst.append([name, idx, "FCOR", s0, L, s1,
                            cell, girder, symm, grp])
        elif tp == 'SQ_TRIM':
            newgrp = ";".join(sorted([grp, "HCOR", "VCOR", "SQCOR"]))
            relst.append([name, idx, "COR", s0, L, s1, 
                          cell, girder, symm, newgrp])
            pass
        elif tp == 'DIPOLE':
            #warnings.warn("'{0}: {1}' is not processed".format(name, fam))
            relst.append([name, idx, "BEND", s0, L, s1, 
                            cell, girder, symm, grp])
            pass
        elif tp == "TRIMX":
            #warnings.warn("'{0}: {1}' is not processed".format(name, fam))
            newgrp = ";".join(sorted([grp, "HCOR"]))
            relst.append([name, idx, "COR", s0, L, s1, 
                          cell, girder, symm, newgrp])
            pass
        elif tp == "TRIMY":
            #warnings.warn("'{0}: {1}' is not processed".format(name, fam))
            newgrp = ";".join(sorted([grp, "VCOR"]))
            relst.append([name, idx, "COR", s0, L, s1,
                          cell, girder, symm, newgrp])
            pass
        else:
            raise RuntimeError("Unknow type '%s'" % tp)

        idx += 100

    return relst

def convNSLS2LatTable(fdst, fsrc, eps = 1e-6):
    """convert the NSLS2 lattice table

     ElementName  ElementType  L       s        K1    K2    Angle  KickMapFile
                               m       m        1/m2  1/m3  rad   
     ----------------------------------------------------------------------
     _BEG_        MARK         0       0        0     0     0
     DH05G1C30A   DRIF         4.29379 4.29379  0     0     0    
     FH2G1C30A    FTRIM        0.044   4.33779  0     0     0

     - split combine function magnet

    Output:
    index, name, type, s0, L, s1
    """

    srclines = open(fsrc, 'r').readlines()
    i = 0
    while srclines[i].find("_BEG_") < 0: i += 1
    if not srclines[i-1].strip().startswith("-----"): 
        raise RuntimeError("Invalid lattice table")

    elems_0, elems_1 = [], []
    for j,line in enumerate(srclines[i:]):
        name, tp, L, s1, k1, k2, ang = line.split()[:7]
        ds = (name, tp, float(L), float(s1), float(k1), float(k2), ang, j)
        if float(L) == 0.0: elems_0.append(ds)
        else: elems_1.append(ds)

    #print "# Finite length elements:", len(elems_1)
    #print "# Zero length elements:", len(elems_0)
    elems = []
    while True:
        ncmb, elems = 0, [list(elems_1[0])]
        for i in range(1, len(elems_1)):
            # not same name
            e0, e1 = elems[-1], elems_1[i]
            if e0[0] != e1[0]:
                elems.append(list(e1))
                continue
            if abs(e0[3] + e1[2] - e1[3]) < eps:
                # same element
                #print "Merged:", e1[0], e1[1]
                elems[-1][2] = elems[-1][2] + e1[2]
                elems[-1][3] = e1[3]
                ncmb += 1
        elems_1 = elems
        if ncmb == 0: break
    #print "# New finite length elements:", len(elems)
    
    # filter zero length element
    elems = []
    for i,e0 in enumerate(elems_0):
        if e0[1] not in ["TRIMX", "TRIMY"]: continue
        g0 = re.match(r"(C[A-Z0-9]+)([XY])(G[0-9]C[0-9]+ID[0-9])", e0[0])
        for j in range(i+1, len(elems_0)):
            e1 = elems_0[j]
            if e1[1] not in ["TRIMX", "TRIMY"]: continue
            g1 = re.match(r"(C[A-Z0-9]+)([XY])(G[0-9]C[0-9]+ID[0-9])", e1[0])
            if g0.group(1) != g1.group(1): continue
            if g0.group(3) != g1.group(3): continue
            if e0[0] == e1[0]:
                raise RuntimeError("Duplicate Name")
            gc = (g0.group(2), g1.group(2))
            if gc == ("X", "Y"): elems.append((i, j))
            elif gc == ("Y", "X"): elems.append((j, i))
    elemx = zip(*elems)
    #print "# New finite length elements:", len(elems)

    allelems = []
    for i,e in enumerate(elems_0):
        if i in elemx[0]:
            g = re.match(r"(C[A-Z0-9]+)([XY])(G[0-9]C[0-9]+ID[0-9])", e[0])
            name = "%s%s" % (g.group(1), g.group(3))
            allelems.append([e[7]*100, name, "TRIM", e[3]-e[2], e[2], e[3]])
        elif i in elemx[1]:
            continue
        else:
            allelems.append([e[7]*100, e[0], e[1], e[3]-e[2], e[2], e[3]])
    # combine with finite-length elements
    for e in elems_1:
        allelems.append([e[7]*100, e[0], e[1], e[3]-e[2], e[2], e[3]])

    elems = _nsls2_filter_element_type_group(allelems)

    gstat = {}
    for i,elem in enumerate(elems):
        gstat.setdefault(elem[2], 0)
        gstat[elem[2]] += 1
    print "Imported elements:", len(elems), fsrc
    for g,n in gstat.items():
        print "{0:>10} {1}".format(g,n)

    f = open(fdst, 'w')
    for i,elem in enumerate(elems):
        #name, idx, tp, s0, L, s1, c, g, s, grp = elem
        elem[0] = elem[0].lower()
        f.write("{0},{1},{2},{3},{4},{5},{6},{7},{8},{9}\n".format(*elem))

    f.close()


def convVirtAccTwiss(fdst, fsrc, grpname = False):
    f = open(fsrc, 'r')
    tunes = f.readline()
    chrom = f.readline()
    alphac = f.readline()
    energy = f.readline()
    for i in range(3): f.readline()
    elems = []
    for i,line in enumerate(f.readlines()):
        idx, name, s1 = [v.strip() for v in line.split()[:3]]
        elems.append([name, idx, "", 0.0, 0.0, float(s1), "", "", "", ""])
    f.close()
    if grpname:
        for e in elems: e[0] = "%s:%s" % (e[0], e[1])

    f = open(fdst, "w")
    for e in elems:
        f.write("{0},{1},{2},{3},{4},{5},{6},{7},{8},{9}\n".format(*e))
    f.close()
    

def convVirtAccPvs(fdst, fsrc, sep = ","):
    """
    Output:
    pv, handle, element_name, va_index, element_type, field
    """
    # change element type and field
    mp = { ("Horizontal Corrector", ""): ("COR", "x"),
           ("Vertical Corrector", ""): ("COR", "y"),
           ("Beam Position Monitor", "X"): ("BPM", "x"),
           ("Beam Position Monitor", "Y"): ("BPM", "y"),
           ("Bending", "T"): ("BEND", "b0"),
           ("Quadrupole", "K"): ("QUAD", "b1"),
           ("Sextupole", "K"): ("SEXT", "b2"),
           ("RFCavity", "f"): ("RFCAVITY", "f"),
           ("RFCavity", "v"): ("RFCAVITY", "v"),
           ("insertion", "GAP"): ("ID", "gap"),
           ("insertion", "PHASE"): ("ID", "phase"),
           ("TWISS", "TUNEX"): ("tune", "x"),
           ("TWISS", "TUNEY"): ("tune", "y"),
           ("TWISS", "ALPHAX"): ("twiss", "alphax"),
           ("TWISS", "ALPHAY"): ("twiss", "alphay"),
           ("TWISS", "BETAX"): ("twiss", "betax"),
           ("TWISS", "BETAY"): ("twiss", "betay"),
           ("TWISS", "ETAX"): ("twiss", "etax"),
           ("TWISS", "ETAY"): ("twiss", "etay"),
           ("TWISS", "PHIX"): ("twiss", "phix"),
           ("TWISS", "PHIY"): ("twiss", "phiy"),
           ("TWISS", "NAME"): ("twiss", "name"),
           ("TWISS", "ORBITX"): ("orbit", "x"),
           ("TWISS", "ORBITY"): ("orbit", "y"),
           ("TWISS", "S"): ("twiss", "s"),
           ("DCCT", "current"): ("DCCT", "current"),
           }

    lines = open(fsrc, 'r').readlines()
    head = [v.strip() for v in lines[0].split(sep)]
    if head[0] != "#pv_name":
        raise RuntimeError("unknown data format: {0}".format(
                lines[0]))
    ipv, ihandle, iidx, ielem, itype, ifield, icell, igirder, isys = [
        head.index(v) for v in (
            "#pv_name", "handle", "el_idx_va", "el_name_va", 
            "el_type_va", "el_field_va", "cell", "girder",
            "machine")]
    pvr = []
    f = open(fdst, 'w')
    for line in lines[1:]:
        r = [v.strip() for v in line.split(sep)]
        pvname = r[ipv]
        pvhandle = "put" if r[ihandle] == "setpoint" else "get"
        elemname = r[ielem]
        elemtype, elemfield = mp[(r[itype], r[ifield])]
        elemidx0 = r[iidx]
        pvr.append([pvname, pvhandle, elemname, elemidx0, elemtype, elemfield])
        f.write("%s,%s,%s,%s,%s,%s\n" % (pvname, pvhandle,
                elemname.lower(), elemidx0,
                elemtype, elemfield))
    f.close()

def createSqliteDb(fdb, felem, fpv, **kwarg):
    """
    felem and fpv are comma separated text file

    name_index: postfix with the index.
    """
    createLatticePvDb(fdb, None)
    #name, idx, tp, s0, L, s1, c, g, s, grp = elem
    elems = [v.strip().split(",") for v in open(felem, 'r').readlines()]
    #pv, handle, elemname, elemidx0, elemtype, elemfield
    pvs = [v.strip().split(",") for v in open(fpv, 'r').readlines()]

    latname    = kwarg.get("latname", "SR")
    name_index = kwarg.get("name_index", False)

    conn = sqlite3.connect(fdb)
    # save byte string instead of the default unicode
    conn.text_factory = str
    c = conn.cursor()
    c.executemany("""INSERT INTO elements (elemName,elemIndex,elemType,"""
                  """elemLength,elemPosition,"""
                  """cell,girder,symmetry,elemGroups)"""
                  """VALUES (?,?,?,?,?,?,?,?,?)""",
                  [(name,idx,tp,L,s1,cl,gd,sm,grp) 
                   for (name, idx, tp, s0, L, s1, cl, gd, sm, grp)
                   in elems])
    conn.commit()
    msg = "[%s] new 'elements' table" % (__name__,)
    c.execute("""insert into info(timestamp,name,value)
                 values (datetime('now'), "log", ? )""", (msg,))
    systag = "aphla.sys.%s" % latname
    c.executemany("""INSERT into pvs """
                  """(pv,elemName,elemHandle,elemField,tags) """
                  """values (?,?,?,?,?)""",
                  [(pv,ename,hdl,fld,systag) 
                   for (pv,hdl,ename,eidx,etp,fld) in pvs])
    conn.commit()
    msg = "[%s] new 'pvs' table" % (__name__,)
    c.execute("""insert into info(timestamp,name,value)
                 values (datetime('now'), "log", ? )""", (msg,))
    conn.commit()
    #
    names = [e[0] for e in elems]
    vrec = {
        "twiss": ["twiss", -100, "TWISS", 0.0, 0.0, "", "", "", ""],
        "dcct": ["dcct", -200, "DCCT", 0.0, 0.0, "", "", "", ""],
        "rfcavity": ["rfcavity", -300, "RFCAVITY", 0.0, 0.0, "", "", "", ""], }
    for k,v in vrec.items():
        if k in names: continue
        c.execute("""INSERT INTO elements (elemName,elemIndex,elemType,"""
                  """elemLength,elemPosition,"""
                  """cell,girder,symmetry,elemGroups)"""
                  """VALUES (?,?,?,?,?,?,?,?,?)""", v)
        names.append(k)
    conn.commit()

    conn.close()



def _saveSqliteDb(cfa, fname, sep=";"):
    """
    save cfa data to sqlite db file.
    
    the input groups, elemNames like "QH1;QH" has to be separated as list.
    """
    uniq, pvs, elems = set(), [], []
    for i,r in enumerate(cfa.rows):
        pv,prpt,tags = r
        if not prpt.get("elemName", None): 
            raise RuntimeError("no element name defined {0}".format(r))
        if not prpt.get("elemType", None):
            raise RuntimeError("no element type defined {0}".format(r))
            
        elemname = prpt["elemName"].lower()
        if elemname in uniq: continue
        uniq.add(elemname)
        grps = ";".join(prpt.get("elemGroups", []))
        elems.append((elemname,
                      prpt.get("elemIndex", -1),
                      prpt.get("elemType", None),
                      prpt.get("elemPosition", None),
                      prpt.get("elemLength", 0.0),
                      None,
                      prpt.get("cell", None),
                      prpt.get("girder", None),
                      prpt.get("symmetry", None),
                      grps))
    print fname, len(elems)
    for i,e in enumerate(elems):
        if i > 5: break
        print e

    ap.apdata.createLatticePvDb(fname)
    conn = sqlite3.connect(fname)
    # save byte string instead of the default unicode
    conn.text_factory = str
    c = conn.cursor()
    c.executemany("""INSERT INTO elements (elemName,elemIndex,elemType,"""
                  """elemLength,elemPosition,"""
                  """cell,girder,symmetry,elemGroups)"""
                  """VALUES (?,?,?,?,?,?,?,?,?)""",
                  [(name,idx,tp,L,s1,cl,gd,sm,grp) 
                   for (name, idx, tp, s0, L, s1, cl, gd, sm, grp)
                   in elems])
    conn.commit()
    conn.close()

def convCfsToSqlite(url, prefix = '', ignore = []):
    """
    url - channel finder server URL
    prefix - output DB file name prefix
    ignore - list of ignored lattice name 
    """
    cf = ChannelFinderClient(BaseURL=url)
    tagprefx = "aphla.sys."
    tags = [tag.Name for tag in cf.getAllTags() 
            if tag.Name.startswith(tagprefx)]
    for tag in tags:
        latname = tag[len(tagprefx):]
        if latname in ignore: continue
        cfa = ap.chanfinder.ChannelFinderAgent()
        cfa.downloadCfs(url, property=[('hostName', '*')], tagName=tag)
        cfa.splitPropertyValue('elemGroups')
        cfa.splitChainedElement('elemName')
        cfa.saveSqlite("%s%s.sqlite" % (prefix, latname))

def convCsvToSqlite(fdb, fcsv):
    cfa = ap.chanfinder.ChannelFinderAgent()
    cfa.loadCsv(fcsv)
    cfa.saveSqlite(fdb)

