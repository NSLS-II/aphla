import os
import sys
import re
#from math import abs
#from ..apdata import createLatticePvDb
from apdata import createLatticePvDb
import sqlite3

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

    print "# Finite length elements:", len(elems_1)
    print "# Zero length elements:", len(elems_0)
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
    print "# New finite length elements:", len(elems)
    
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
    print "# New finite length elements:", len(elems)

    f = open(fdst, 'w')
    for i,e in enumerate(elems_0):
        if i in elemx[0]:
            g = re.match(r"(C[A-Z0-9]+)([XY])(G[0-9]C[0-9]+ID[0-9])", e[0])
            name = "%s%s" % (g.group(1), g.group(3))
            f.write("%d, %s, %s, %.4f, %.4f, %.4f\n" % (
                    e[7]*100, name.lower(), "TRIM", e[3]-e[2], e[2], e[3]))
        elif i in elemx[1]:
            continue
        else:
            f.write("%d, %s, %s, %.4f, %.4f, %.4f\n" % (
                    e[7]*100, e[0].lower(), e[1], e[3]-e[2], e[2], e[3]))
            
    for e in elems_1:
        f.write("%d, %s, %s, %.4f, %.4f, %.4f\n" % (
                e[7]*100, e[0].lower(), e[1], e[3]-e[2], e[2], e[3]))
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
           ("Cavity", "f"): ("RFCAVITY", "f"),
           ("Cavity", "v"): ("RFCAVITY", "v"),
           ("insertion", "GAP"): ("ID", "gap"),
           ("insertion", "PHASE"): ("ID", "phase"),
           ("", "TUNEX"): ("tune", "x"),
           ("", "TUNEY"): ("tune", "y"),
           ("", "ALPHAX"): ("twiss", "alphax"),
           ("", "ALPHAY"): ("twiss", "alphay"),
           ("", "BETAX"): ("twiss", "betax"),
           ("", "BETAY"): ("twiss", "betay"),
           ("", "ETAX"): ("twiss", "etax"),
           ("", "ETAY"): ("twiss", "etay"),
           ("", "PHIX"): ("twiss", "phix"),
           ("", "PHIY"): ("twiss", "phiy"),
           ("", "NAME"): ("twiss", "name"),
           ("", "ORBITX"): ("orbit", "x"),
           ("", "ORBITY"): ("orbit", "y"),
           ("", "S"): ("twiss", "s"),
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
        f.write("%s, %s, %s, %s, %s, %s\n" % (
                pvname, pvhandle, elemname.lower(), elemidx0,
                elemtype, elemfield))
    f.close()

def createSqliteDb(fdb, felem, fpv, **kwarg):
    """
    felem and fpv are comma separated text file

    name_index: postfix with the index.
    """
    createLatticePvDb(fdb, None)
    elems = [v.split(",") for v in open(felem, 'r').readlines()]
    pvs = [v.split(",") for v in open(fpv, 'r').readlines()]

    latname    = kwarg.get("latname", "SR")
    system     = kwarg.get("system", latname)
    name_index = kwarg.get("name_index", False)

    conn = sqlite3.connect(fdb)
    # save byte string instead of the default unicode
    conn.text_factory = str
    c = conn.cursor()
    c.executemany("""INSERT INTO elements (elemName, elemIndex, """
                  """elemGroups, elemType, system)"""
                  """VALUES (?,?,?,?,?)""",
                  [(v[1].strip(), v[0].strip(), "", v[2].strip(), system) for 
                   v in elems])
    conn.commit()
    conn.close()

if __name__ == "__main__":
    convNSLS2LatTable("test_elem.txt", "./nsls2v2/ring_par.txt")
    convVirtAccPvs("test_pvs.txt", "./nsls2v2/ring_pvs.csv")
    createSqliteDb("test.sqlite", "test_elem.txt", "test_pvs.txt")

