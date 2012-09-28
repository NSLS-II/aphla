"""
process "nsls2srid_prop.csv" from "CD3-Aug15-11-oneCell-norm-Aug19-tracy.lat".

-- 2012/08/21
"""

import sys, os
import re

from sqlalchemy import Column, Integer, String, Float, ForeignKey, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref

C = 787.793/30

ipv, idx, isys, icell, igirder, ihandle, iname0, ifield0, itype0 = range(9)
iname1, itype1, ifield1, isend, ilength,itag = 9, 10, 11, 12, 13, 14

APTAG = "aphla."

twiss = [
    ('{TUNE}X', 'tunex'),
    ('{TUNE}Y', 'tuney'),
    ('{ALPHA}X', 'alphax'),
    ('{ALPHA}Y','alphay'),
    ('{BETA}X','betax'),
    ('{BETA}Y','betay'),
    ('{ETA}X' ,'etax'),
    ('{ETA}Y', 'etay'),
    ('{PHI}X','phix'),
    ('{PHI}Y', 'phiy'),
    ('{ORBIT}X', 'orbitx'),
    ('{ORBIT}Y', 'orbity'),
    ('{POS}-I', 's')]

def twiss_element(pv):
    for r in twiss:
        if pv.find(r[0]) > 0: return r
    return None

def elem_pattern(ibpm):
    locs = [('H1', 'A'), ('H2', 'A'), ('M1', 'A'),
            ('M1', 'B'), ('L1', 'B'), ('L2', 'B'), 
            ('L1', 'A'), ('L2', 'A'), ('M1', 'A'), 
            ('M1', 'B'), ('H1', 'B'), ('H2', 'B')]
    i,k = divmod(ibpm, 12)
    return locs[k]

    
def patch_va_table_1(inpt, oupt):
    """
    patch the va table from Guobao. see "nsls2srid_prop.csv"

    #pv_name, el_idx_va, machine, cell, girder, handle, el_name_va, el_field_va, el_type_va
    V:1-SR:C30-MG:G2{SH1:7}Fld:SP,7,V:1-SR,C30,G2,set,SH1G2C30A,K,Sextupole
    V:1-SR:C30-MG:G2{SH1:7}Fld:I,7,V:1-SR,C30,G2,read,SH1G2C30A,K,Sextupole
    V:1-SR:C30-BI:G2{BPM:9}SA:X,9,V:1-SR,C30,G2,X,BPM,,Beam Position Monitor
    V:1-SR:C30-BI:G2{BPM:9}SA:Y,9,V:1-SR,C30,G2,Y,BPM,,Beam Position Monitor
    V:1-SR:C30-MG:G2{QH1:11}Fld:SP,11,V:1-SR,C30,G2,set,QH1G2C30A,K,Quadrupole
    V:1-SR:C30-MG:G2{QH1:11}Fld:I,11,V:1-SR,C30,G2,read,QH1G2C30A,K,Quadrupole
    V:1-SR:C30-MG:G2{SQHH:13}Fld:SP,13,V:1-SR,C30,G2,set,SQHHG2C30A,K,Quadrupole
    V:1-SR:C30-MG:G2{SQHH:13}Fld:I,13,V:1-SR,C30,G2,read,SQHHG2C30A,K,Quadrupole
    V:1-SR:C30-MG:G2{CH:14}Fld:SP,14,V:1-SR,C30,G2,set,CH,,Horizontal Corrector

    """
    finpt = open(inpt, 'r')
    foupt = open(oupt, 'w')
    foupt.write(finpt.readline().strip() + ",elemName,elemType,elemField\n")
    elemlst = {}
    jbpm, jhcor, jvcor = {}, {}, {}
    for s in finpt.readlines():
        #v = re.match(r"[A-Z0-9:-]+(C[0-9][0-9]).*[A-Z0-9:,-]+(C[0-9][0-9]).*", s)
        grp = [v.strip() for v in s.split(',')]
        # append one for real unique name
        if len(grp) <= iname1: grp.append(grp[iname0][:].lower())
        if len(grp) <= itype1: grp.append(grp[itype0][:])
        if len(grp) <= ifield1: grp.append(grp[ifield0][:])

        if grp[idx]: i = int(grp[idx])
        if grp[itype0] == 'Sextupole': 
            grp[itype1] = 'SEXT'
            if grp[ifield0] == 'K': grp[ifield1] = 'k2'
            if re.match(r"S[HLM][0-9]G[0-9]C[0-9][0-9][AB]", grp[iname0]):
                grp[iname1] = grp[iname0][:3] + grp[igirder] + grp[icell] + grp[iname0][-1]
            elif re.match(r"S[HLM][0-9]HG[0-9]C[0-9][0-9][AB]", grp[iname0]):
                grp[iname1] = grp[iname0][:4] + grp[igirder] + grp[icell] + grp[iname0][-1]
            else:
                raise RuntimeError("%s" % grp[iname0])
        elif grp[itype0] == 'Beam Position Monitor': 
            grp[itype1] = 'BPM'
            jbpm.setdefault(grp[idx], len(jbpm))
            loc, sym = elem_pattern(jbpm[grp[idx]])
            grp[iname1] = 'P%s%s%s%s' % (loc, grp[igirder], grp[icell], sym)
            grp[ifield1] = grp[ihandle].lower() # it was a bug in Guobao's data
            grp[ihandle] = 'read'
        elif grp[itype0] == 'Quadrupole': 
            grp[itype1] = 'QUAD'
            if grp[ifield0] == 'K': grp[ifield1] = 'k1'
            if re.match(r"Q[HLM][0-9]G[0-9]C[0-9][0-9][AB]", grp[iname0]):
                grp[iname1] = grp[iname0][:3] + grp[igirder] + grp[icell] + grp[iname0][-1]
            elif re.match(r"SQ[HLM][H0-9]*G[0-9]C[0-9][0-9][AB]", grp[iname0]):
                grp[iname1] = grp[iname0][:4] + grp[igirder] + grp[icell] + grp[iname0][-1]
                grp[itype1] = 'SQUAD'
            else:
                raise RuntimeError("%s" % grp[iname0])
        elif grp[itype0] == 'Horizontal Corrector': 
            grp[itype1] = 'HCOR'
            jhcor.setdefault(grp[idx], len(jhcor))
            if grp[iname0].startswith('CHIDSim'): pass
            elif grp[iname0].startswith('CHIDCor'): pass
            elif grp[iname0] == 'CH':
                loc, sym = elem_pattern(jhcor[grp[idx]])
                grp[iname1] = 'CX%s%s%s%s' % (loc, grp[igirder], grp[icell], sym)
            else: raise RuntimeError('%s' % grp[iname0])
            grp[ifield1] = 'x'
            #if grp[ifield0] == 'X': grp[ifield1] = 'x'
        elif grp[itype0] == 'Vertical Corrector': 
            grp[itype1] = 'VCOR'
            jvcor.setdefault(grp[idx], len(jvcor))
            if grp[iname0].startswith('CVIDSim'): pass
            elif grp[iname0].startswith('CVIDCor'): pass
            elif grp[iname0] == 'CV':
                loc, sym = elem_pattern(jvcor[grp[idx]])
                grp[iname1] = 'CY%s%s%s%s' % (loc, grp[igirder], grp[icell], sym)
            else: raise RuntimeError('%s' % grp[iname0])
            grp[ifield1] = 'y'
            #if grp[ifield0] == 'Y': grp[ifield1] = 'y'
        elif grp[itype0] == 'Bending': 
            grp[itype1] = 'DIPOLE'
            if grp[ifield0] == 'T': grp[ifield1] = ''
            if re.match(r"B[0-9]G[0-9]C[0-9][0-9][AB]", grp[iname0]):
                grp[iname1] = grp[iname0][:2] + grp[igirder] + grp[icell] + grp[iname0][-1]
            else:
                raise RuntimeError("%s" % grp[iname0])
        elif grp[itype0] == 'Cavity Frequency': 
            grp[itype1] = 'CAVITY'
            grp[ifield1] = 'f'
        elif grp[itype0] == 'Cavity Voltage': 
            grp[itype1] = 'CAVITY'
            grp[ifield1] = 'v'
        elif not grp[itype0]:
            if grp[iname0] in ['CHIDSim', 'CVIDSim', 'CHIDCor', 'CVIDCor']:
                grp[iname1] = grp[iname0] + grp[igirder] + grp[icell]
            elif grp[iname0] == 'EPUG1C16':
                grp[itype1] = 'EPU'
                if grp[ifield0] in [ 'Gap', 'Phase']:
                    grp[ifield1] = grp[ifield0].lower()
                else:
                    raise RuntimeError("Unknown field '%s' for '%s'" % (
                            grp[ifield0], grp[iname0]))
            elif grp[ipv].find('{DCCT}') > 0: 
                grp[iname1] = 'dcct'
                grp[itype1] = 'DCCT'
                grp[ifield1] = 'value'
            elif grp[ipv].find('{TUNE}X') > 0:
                grp[iname1] = 'tune'
                grp[ifield1] = 'x'
            elif grp[ipv].find('{TUNE}Y') > 0:
                grp[iname1] = 'tune'
                grp[ifield1] = 'y'
            elif twiss_element(grp[ipv]): 
                for r in twiss:
                    if grp[ipv].find(r[0]) > 0:
                        grp[iname1] = 'twiss'
                        grp[ifield1] = r[1]
                        break
            else:
                raise RuntimeError("'%s' in element '%s'" % (grp[ipv], grp[iname0]))
        else:
            raise RuntimeError("Unknown element type '%s' for '%s'" % (grp[itype0], grp[iname0]))

        # use lower case for element name
        grp[iname1] = grp[iname1].lower()

        elemlst.setdefault(grp[iname1], grp[idx])
        
        # the SQUAD and CH, CV might be combined and SQUAD is splitted into two elements
        #if elemlst[grp[iname]] != grp[idx]:
        #    raise RuntimeError("element {0}:'{1}' is placed at different locations: '{2}'".format(grp[idx], grp[iname], elemlst[grp[iname]]))
        #if grp[itype] not in ['QUAD']:
        foupt.write(','.join(grp) + '\n')
    foupt.close()

def patch_va_table_2(inpt, sinpt, oupt):
    """
    update the s location and length from channel of VA.
    """
    s = []
    if os.path.exists(sinpt):
        for v in open(sinpt, 'r').readlines():
            for d in v.split():
                try:
                    s.append(float(d))
                except:
                    pass
        if len(s) == int(s[0]) + 1: s = s[1:]
        #print "read:", len(s)
    with open(inpt, 'r') as f:
        head = f.readline()
        foupt = open(oupt, 'w')
        foupt.write(head.strip() + ',s_end,length\n')
        for line in f.readlines():
            grp = [v.strip() for v in line.split(',')]
            foupt.write(line.strip())
            if not grp[idx] or int(grp[idx]) <= 0:
                foupt.write(",0.0,0.0")
            else:
                i = int(grp[idx])
                foupt.write(",{0},{1}".format(s[i], s[i] - s[i-1]))
            if grp[ipv].find("SR") > 0: foupt.write(",aphla.sys.V1SR")
            else: foupt.write(",")
            foupt.write("\n")

Base = declarative_base()
class Element(Base):
    __tablename__ = "elements"
    elem_id  = Column(Integer, primary_key=True)
    name     = Column('elemName', String)
    elemtype = Column('elemType', String)
    machine  = Column('system', String)
    cell     = Column(String)
    girder   = Column(String)
    symmetry = Column(String)
    s_end    = Column('elemPosition', Float)
    length   = Column('elemLength', Float)
    virtual  = Column(Integer)

    tracy_el_idx_va = Column('elemIndex', Integer)
    tracy_machine   = Column(String)
    tracy_el_name_va = Column(String)
    tracy_el_type_va = Column(String)

    def __init__(self, name, elemtype, machine):
        self.name = name
        self.elemtype = elemtype
        self.machine = machine
        self.virtual = 0
        self.tracy_el_idx_va = -1

    def __repr__(self):
        return "<Element '%s':'%s' ...>" % (self.name, self.elemtype)

class ChannelRecord(Base):
    #__tablename__ = 'cfdata_v0'
    __tablename__ = 'pvs'

    pv       = Column(String, primary_key=True)
    elem_id  = Column(Integer, ForeignKey('elements.elem_id'))
    devname  = Column('devName', String)
    handle   = Column('elemHandle', String, nullable=False)
    hostname = Column('hostName', String)
    iocname  = Column('iocName', String)
    tags     = Column(String) # deliminator: ','
    elemField = Column(String)

    tracy_el_field_va = Column(String)

    element = relationship("Element", backref=backref("pvs", order_by=pv))

    def __init__(self, pv, elemName, handle = 'read'):
        self.pv = pv
        self.elemname = elemName
        self.handle = handle

    def __repr__(self):
        return "<Channel('%s', '%s', ...)>" % (self.pv, self.elemname)


def create_sqlite_db(inpt, dbfname = "us_nsls2.sqlite3"):
    engine = create_engine('sqlite:///' + dbfname, echo = False)
    Base.metadata.create_all(engine)

    from sqlalchemy.orm import sessionmaker
    Session = sessionmaker(bind=engine)
    session = Session()

    with open(inpt, 'r') as f:
        head = f.readline()
        for rec in f.readlines():
            grp = rec.split(',')
            elem = session.query(Element).\
                filter(Element.name == grp[iname1]).first()
            if not elem:
                elem = Element(grp[iname1], grp[itype1], grp[isys])
            elem.s_end = grp[isend]
            elem.length = grp[ilength]
            elem.cell = grp[icell]
            elem.girder = grp[igirder]
            if grp[idx]: elem.tracy_el_idx_va = grp[idx]
            else: elem.tracy_el_idx_va = -1
            elem.tracy_machine = grp[isys]
            elem.tracy_el_name_va = grp[iname0]
            elem.tracy_el_type_va = grp[itype0]

            if elem.cell and elem.girder:
                if elem.name.endswith('a'): elem.symmetry = 'A'
                elif elem.name.endswith('b'): elem.symmetry = 'B'
            if elem.name in ['twiss']:
                elem.virtual = 1

            pvr = session.query(ChannelRecord).\
                filter(ChannelRecord.pv == grp[ipv]).first()
            if not pvr:
                pvr = ChannelRecord(grp[ipv], elem.name, grp[ihandle])
            pvr.element = elem
            pvr.tracy_el_field_va = grp[ifield0]
            if grp[itag]: pvr.tags = grp[itag].replace(';', ',')
            if grp[ifield1]:
                pvr.elemField = grp[ifield1]
                #pvr.tags += ",{0}elemfield.{1}".format(APTAG, grp[ifield])
            session.add(pvr)
            #session.add(elem)

        session.commit()

def update_db_pvs_tags(dbfname):
    """
    update tags for PV
    """
    engine = create_engine('sqlite:///' + dbfname, echo = False)
    Base.metadata.create_all(engine)

    from sqlalchemy.orm import sessionmaker
    Session = sessionmaker(bind=engine)
    session = Session()

    #for a in session.query(ChannelRecord).all():
    #    #if a.tracy_el_field_va in ['x', 'y', 'k1', 'f', 'v', 'k2']:
    #    #if a.tracy_el_field_va and a.tags.find(APTAG+'elemfield.' + a.tracy_el_field_va) < 0:
    #    #a.tags += ',' + APTAG+'elemfield.' + a.tracy_el_field_va
    #    session.add(a)
    #        
    #session.commit()

def check_db(dbfname):
    import sqlite3
    conn = sqlite3.connect(dbfname)
    c = conn.cursor()
    c.execute('''select * from pvs,elements where pvs.elem_id=elements.elem_id''')
    print c.description
    for r in c.fetchall()[:5]:
        print r
    c.close()

def append_ltb_csv(src, out):
    f1 = open(src, 'r')
    f2 = open(out, 'a')
    head = f1.readline().strip().split(',')
    print len(head)
    
    neworder = ['PV', 'ordinal', 'system', 'cell', 'girder', 'handle', 
                None, None, None, 'elemName', 'elemType', None, 'sEnd',
                'length', None]
    for line in f1.readlines():
        grp = []
        src = line.strip().split(',')
        tags = src[len(head):]
        #print tags
        field = None
        for t in tags:
            if not t.startswith('aphla'):
                raise RuntimeError("not a tag '%s'" % t)
            if t.startswith('aphla.elemfield.'): field = t[len('aphla.elemfield/'):]
        #if field is not None: print field

        for i,v in enumerate(neworder):
            if v is not None: v2 = src[head.index(v)]
            elif i in [iname0, ifield0, itype0]: v2 = ''
            elif i == ifield1:
                if field is not None: v2 = field
                else: v2 = ''
            elif i == itag:
                #print tags,
                newtags = []
                for t in tags:
                    if t.startswith('aphla.elemfield.'): continue
                    if t in ['aphla.x', 'aphla.y', 'aphla.eget', 'aphla.eput']: continue
                    newtags.append(t)

                v2 = ';'.join(newtags)
                #print v2
            else:
                raise RuntimeError("unknown v '%s'" % v)

            if i == iname1: grp.append(v2.lower())
            elif i == ihandle:
                if v2 == 'READBACK': grp.append('read')
                elif v2 == 'SETPOINT': grp.append('set')
                else:
                    raise RuntimeError("unknonw handle: '%s'" % v2)
            else: grp.append(v2)
        f2.write(','.join(grp) + '\n')
    f1.close()
    f2.close()

if __name__ == "__main__":
    dbfname = "us_nsls2v1.db"
    patch_va_table_1(sys.argv[1], "output.txt")
    patch_va_table_2("output.txt", "s.txt", "cfd.txt")
    if len(sys.argv) == 3:
        append_ltb_csv(sys.argv[2], "cfd.txt")

    create_sqlite_db("cfd.txt", dbfname)
    #update_db_pvs_tags(dbfname)
    check_db(dbfname)
