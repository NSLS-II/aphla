"""
import virtual accelerator CSV file to sqlite

Besides a running virtual acceleartor, we are provided with a CSV file which
has all the public PVs, element names, element types, indices, etc.

Some lattice is expanded from one super-period and with element name repeated
in each super peiod. The index of an element should be unique to identify an
element.

It can update the s-location information from a running accelerator.
"""

import sys
import sqlite3
import argparse
import aphla as ap

# change element type and field
mp = {("Horizontal Corrector", ""): ("COR", "x"),
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

#pv_twiss_s = None

def import_pvs(dbf, src, latname):
    sp = ","
    lines = open(src, 'r').readlines()
    head = [v.strip() for v in lines[0].split(sp)]
    if head[0] != "#pv_name":
        raise RuntimeError("unknown data format: {0}".format(
                lines[0]))
    ipv, ihandle, iidx, ifield, itype = [head.index(v) for v in (
            "#pv_name", "handle", "el_idx_va", "el_field_va",
            "el_type_va")]
    pvr = []
    for line in lines[1:]:
        r = [v.strip() for v in line.split(sp)]
        pvname = r[ipv]
        pvhandle = "put" if r[ihandle] == "setpoint" else "get"
        pvr.append([pvname, pvhandle])

    conn = sqlite3.connect(dbf)
    # save byte string instead of the default unicode
    conn.text_factory = str
    c = conn.cursor()

    c.executemany("""INSERT INTO pvs (pv, elemHandle)
                     VALUES (?, ?)""", pvr)
    conn.commit()

    # update the elem foreign key
    for line in lines[1:]:
        r = [v.strip() for v in line.split(sp)]
        pvname = r[ipv]
        pvhandle = "put" if r[ihandle] == "setpoint" else "get"
        elemidx = r[iidx]
        elemtype, elemfield = mp[(r[itype], r[ifield])]
        c.execute("""UPDATE pvs set """
                  """elemField=?,elem_id=(select id from elements """
                  """where elemIndex=?) where pv=?""", (
                elemfield,elemidx, pvname,)) 
        if latname: c.execute("""UPDATE pvs set tags=? where pv=?""",
                              ("aphla.sys." + latname, pvname))

    msg = "[%s] updated pvs with '%s'" % (__name__, src)
    c.execute("""insert into info(timestamp,name,value)
                 values (datetime('now'), "log", ? )""", (msg,))
    conn.commit()
    conn.close()
    pass

def import_elements(dbf, src, latname):
    sp = ","
    lines = open(src, 'r').readlines()
    head = [v.strip() for v in lines[0].split(sp)]
    if head[0] != "#pv_name":
        raise RuntimeError("unknown data format: {0}".format(
                lines[0]))
    ipv, iidx, ielem, itype, ifield, icell, igirder, isys = [
        head.index(v) for v in (
            "#pv_name", "el_idx_va", "el_name_va", 
            "el_type_va", "el_field_va", "cell", "girder",
            "machine")]
    elem_fam = {}
    for line in lines[1:]:
        r = [v.strip() for v in line.split(sp)]
        pvname = r[ipv]
        elemname = r[ielem]
        elemtype = r[itype]
        elemfield = r[ifield]
        elemidx0 = r[iidx]
        elem_fam.setdefault(elemname, [])
        if elemidx0 not in elem_fam[elemname]:
            elem_fam[elemname].append(elemidx0)
    elr = []
    for elem,lst in elem_fam.items():
        if len(lst) == 1:
            elr.append([elem.lower(), int(lst[0]), "", "", ""])
        elif len(lst) > 1:
            for j,k in enumerate(lst):
                newname = "%s:%s" % (elem.lower(), j)
                elr.append([newname, k, elem.upper(), "", ""])
    for e in elr: print e
    conn = sqlite3.connect(dbf)
    # save byte string instead of the default unicode
    conn.text_factory = str
    c = conn.cursor()

    c.executemany("""INSERT INTO elements (elemName, elemIndex, """
                  """elemGroups, elemType, system)"""
                  """VALUES (?,?,?,?,?)""",
                  sorted(elr, key=lambda r: int(r[1])))
    conn.commit()

    for line in lines[1:]:
        r = [v.strip() for v in line.split(sp)]
        elemidx0 = r[iidx]
        print r
        elemtype, elemfield = mp[(r[itype], r[ifield])]
        if latname: system = latname
        else: system = r[isys]
        c.execute("""update elements set """
                  """elemType=?,system=?,cell=?,girder=? """
                  """where elemIndex=?""", (
                elemtype, system, r[icell], r[igirder], elemidx0))

    msg = "[%s] updated elements with '%s'" % (__name__, src)
    c.execute("""insert into info(timestamp,name,value)
                 values (datetime('now'), "log", ? )""", (msg,))
    conn.commit()
    conn.close()


def update_spos(dbf, src):
    from cothread.catools import caget
    sp = ","
    lines = open(src, 'r').readlines()
    head = [v.strip() for v in lines[0].split(sp)]
    if head[0] != "#pv_name":
        raise RuntimeError("unknown data format: {0}".format(
                lines[0]))
    ipv, iidx, ielem, itype, ifld = [
        head.index(v) for v in (
            "#pv_name", "el_idx_va", "el_name_va", 
            "el_type_va", "el_field_va")]
    pv_name, pv_spos = None, None
    names, spos, idx = [], [], []
    for line in lines[1:]:
        r = [v.strip() for v in line.split(sp)]
        idx.append(r[iidx])
        names.append(r[ielem])
        if (r[itype], r[ifld]) == ("", "NAME"): pv_name = r[ipv]
        if (r[itype], r[ifld]) == ("", "S"): pv_spos = r[ipv]

    if pv_name is None:
        raise RuntimeError("can not find PV for names")
    if pv_spos is None: 
        raise RuntimeError("can not find PV for sposition")

    ca_names = caget(pv_name)
    ca_spos  = caget(pv_spos)

    if len(ca_names) != len(ca_spos):
        raise RuntimeError("names does not agree with spos")

    conn = sqlite3.connect(dbf)
    # save byte string instead of the default unicode
    conn.text_factory = str
    c = conn.cursor()
    print "Name Size:", len(ca_names)
    print "Spos Size:", len(ca_spos)
    for i,ix in enumerate(idx):
        j = int(ix)
        if j < 0: continue
        if j >= len(ca_spos): continue
        L = ca_spos[j] - ca_spos[j-1]
        #print ix, names[i], ca_names[j-1], L
        c.execute("""UPDATE elements set elemPosition=?,elemLength=? """
                  """where elemIndex=?""",
                  (ca_spos[j-1], L, ix))

    conn.commit()
    conn.close()

def import_twiss(fname):
    f = open(fname, "r")
    lines = f.readlines()
    kw = {}
    kw["tune"]  = [float(v) for v in lines[0].split()[1:3]]
    kw["chrom"] = [float(v) for v in lines[1].split()[1:3]]
    kw["alphac"] = float(lines[2].split()[1])
    kw["energy"] = float(lines[3].split()[1])
    # initialize the column data
    # ignore the leading "#"
    header = [v.strip() for v in lines[4].strip()[1:].split()]
    for col in header:
        icol = header.index(col)
        if col == "name":
            kw[col] = [line.split()[icol] for line in lines[7:]]
        else:
            kw[col] = [float(v) for v in [vl.split()[icol] for vl in lines[7:]]]

    kw['element'] = kw['name']
    td = ap.apdata.TwissData("VA")
    td.set(**kw)
    td._save_hdf5_v2("tpsv1.hdf5")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()
    parser.add_argument('dbf', metavar='dbfile', type=str, 
                   help='a SQLite file')
    parser.add_argument('--latname', type=str, 
                        help="lattice name")
    group.add_argument('--csv', type=str, 
                       help="update with csv file (table)")
    parser.add_argument('--latpar', type=str, 
                        help="lattice parameter")
    parser.add_argument('-s', '--update-s', action="store_true", 
                        help="update s location from EPICS")

    
    arg = parser.parse_args()

    if arg.csv and arg.dbf:
        ap.apdata.createLatticePvDb(arg.dbf, None)
        import_elements(arg.dbf, arg.csv, arg.lattice)
        import_pvs(arg.dbf, arg.csv, arg.lattice)

    if arg.update_s:
        update_spos(arg.dbf, arg.csv)


