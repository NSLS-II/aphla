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

ipv, idx, isys, icell, igirder, ihandle, iname, ifield, itype = range(9)
isend, ilength = 9, 10

def bpm_pattern(ibpm):
    locs = [('H1', 'A'), ('H2', 'A'), ('M1', 'A'),
            ('M1', 'B'), ('L1', 'B'), ('L2', 'B'), 
            ('L1', 'A'), ('L2', 'A'), ('M1', 'A'), 
            ('M1', 'B'), ('H1', 'B'), ('H2', 'B')]
    i,k = divmod(ibpm, 12)
    return locs[k]

    
def patch_va_table_1(inpt, oupt):
    """
    """
    finpt = open(inpt, 'r')
    foupt = open(oupt, 'w')
    foupt.write(finpt.readline())
    elemlst = {}
    jbpm, jhcor, jvcor = {}, {}, {}
    for s in finpt.readlines():
        #v = re.match(r"[A-Z0-9:-]+(C[0-9][0-9]).*[A-Z0-9:,-]+(C[0-9][0-9]).*", s)
        grp = [v.strip() for v in s.split(',')]
        if grp[idx]: i = int(grp[idx])
        if grp[itype] == 'Sextupole': 
            grp[itype] = 'SEXT'
            if re.match(r"S[HLM][0-9]G[0-9]C[0-9][0-9][AB]", grp[iname]):
                grp[iname] = grp[iname][:3] + grp[igirder] + grp[icell] + grp[iname][-1]
            elif re.match(r"S[HLM][0-9]HG[0-9]C[0-9][0-9][AB]", grp[iname]):
                grp[iname] = grp[iname][:4] + grp[igirder] + grp[icell] + grp[iname][-1]
            else:
                raise RuntimeError("%s" % grp[iname])
        elif grp[itype] == 'Beam Position Monitor': 
            grp[itype] = 'BPM'
            jbpm.setdefault(grp[idx], len(jbpm))
            loc, sym = bpm_pattern(jbpm[grp[idx]])
            grp[iname] = 'P%s%s%s%s' % (loc, grp[igirder], grp[icell], sym)
            grp[ifield] = grp[ihandle]
            grp[ihandle] = 'readback'
        elif grp[itype] == 'Quadrupole': 
            grp[itype] = 'QUAD'
            if re.match(r"Q[HLM][0-9]G[0-9]C[0-9][0-9][AB]", grp[iname]):
                grp[iname] = grp[iname][:3] + grp[igirder] + grp[icell] + grp[iname][-1]
            elif re.match(r"SQ[HLM][H0-9]*G[0-9]C[0-9][0-9][AB]", grp[iname]):
                grp[iname] = grp[iname][:4] + grp[igirder] + grp[icell] + grp[iname][-1]
                grp[itype] = 'SQUAD'
            else:
                raise RuntimeError("%s" % grp[iname])
        elif grp[itype] == 'Horizontal Corrector': 
            grp[itype] = 'HCOR'
            jhcor.setdefault(grp[idx], len(jhcor))
            if grp[iname] == 'CHIDSim': pass
            elif grp[iname] == 'CHIDCor': pass
            elif grp[iname] == 'CH':
                loc, sym = bpm_pattern(jhcor[grp[idx]])
                grp[iname] = 'CX%s%s%s%s' % (loc, grp[igirder], grp[icell], sym)
                grp[ifield] = 'X'
            else: raise RuntimeError('%s' % grp[iname])
        elif grp[itype] == 'Vertical Corrector': 
            grp[itype] = 'VCOR'
            jvcor.setdefault(grp[idx], len(jvcor))
            if grp[iname] == 'CVIDSim': pass
            elif grp[iname] == 'CVIDCor': pass
            elif grp[iname] == 'CV':
                loc, sym = bpm_pattern(jvcor[grp[idx]])
                grp[iname] = 'CY%s%s%s%s' % (loc, grp[igirder], grp[icell], sym)
                grp[ifield] = 'Y'
            else: raise RuntimeError('%s' % grp[iname])
        elif grp[itype] == 'Bending': 
            grp[itype] = 'DIPOLE'
            if re.match(r"B[0-9]G[0-9]C[0-9][0-9][AB]", grp[iname]):
                grp[iname] = grp[iname][:2] + grp[igirder] + grp[icell] + grp[iname][-1]
            else:
                raise RuntimeError("%s" % grp[iname])
        elif grp[itype] == 'Cavity Frequency': 
            grp[itype] = 'CAVITY'
        elif grp[itype] == 'Cavity Voltage': 
            grp[itype] = 'CAVITY'
        elif not grp[itype]:
            if grp[iname] in ['CHIDSim', 'CVIDSim', 'CHIDCor', 'CVIDCor']:
                grp[iname] = grp[iname] + grp[igirder] + grp[icell]
            elif grp[ipv].find('{TUNE}X') > 0: grp[iname] = 'tune'
            elif grp[ipv].find('{TUNE}Y') > 0: grp[iname] = 'tune'
            elif grp[ipv].find('{ALPHA}X') > 0: grp[iname] = 'alpha'
            elif grp[ipv].find('{ALPHA}Y') > 0: grp[iname] = 'alpha'
            elif grp[ipv].find('{BETA}X') > 0: grp[iname] = 'beta'
            elif grp[ipv].find('{BETA}Y') > 0: grp[iname] = 'beta'
            elif grp[ipv].find('{ETA}X') > 0: grp[iname] = 'eta'
            elif grp[ipv].find('{ETA}Y') > 0: grp[iname] = 'eta'
            elif grp[ipv].find('{PHI}X') > 0: grp[iname] = 'phi'
            elif grp[ipv].find('{PHI}Y') > 0: grp[iname] = 'phi'
            elif grp[ipv].find('{ORBIT}X') > 0: grp[iname] = 'orbit'
            elif grp[ipv].find('{ORBIT}Y') > 0: grp[iname] = 'orbit'
            elif grp[ipv].find('{POS}-I') > 0: grp[iname] = 'pos'
            elif grp[ipv].find('{ALPHA}Y') > 0: grp[iname] = 'alpha'
            elif grp[ipv].find('{DCCT}CUR-') > 0: 
                grp[iname] = 'dcct'
                grp[itype] = 'DCCT'
            else:
                raise RuntimeError("'%s' in element '%s'" % (grp[ipv], grp[iname]))
        else:
            raise RuntimeError("Unknown element type '%s' for '%s'" % (grp[itype], grp[iname]))

        #if not grp[icell].lower() in grp[iname]:
        #    elif grp[iname] == 'CV':
        #    elif grp[iname] == 'CAV':
        #        grp[iname] = 'rfcavity0'
        #    elif grp[iname] == 'rfcavity0': 
        #        pass
        #    elif re.match(r"B[0-9]G[0-9]C[0-9][0-9][AB]", grp[iname]):
        #        grp[iname] = grp[iname][:2] + grp[igirder] + grp[icell] + grp[iname][-1]
        #    elif re.match(r"[SQ][HLM][0-9]G[0-9]C[0-9][0-9][AB]", grp[iname]):
        #        grp[iname] = grp[iname][:3] + grp[igirder] + grp[icell] + grp[iname][-1]
        #    elif re.match(r"SQ[HLM]HG[0-9]C[0-9][0-9][AB]", grp[iname]):
        #        grp[iname] = grp[iname][:4] + grp[igirder] + grp[icell] + grp[iname][-1]
        #    elif re.match(r"S[HLM][0-9]HG[0-9]C[0-9][0-9][AB]", grp[iname]):
        #        grp[iname] = grp[iname][:4] + grp[igirder] + grp[icell] + grp[iname][-1]
        #    else:
        #        raise RuntimeError("Invalid element name '%s' (no '%s')" % (grp[iname], grp[icell]))

        grp[iname] = grp[iname].lower()

        elemlst.setdefault(grp[iname], grp[idx])
        
        # the SQUAD and CH, CV might be combined and SQUAD is splitted into two elements
        #if elemlst[grp[iname]] != grp[idx]:
        #    raise RuntimeError("element {0}:'{1}' is placed at different locations: '{2}'".format(grp[idx], grp[iname], elemlst[grp[iname]]))
        #if grp[itype] not in ['QUAD']:
        foupt.write(','.join(grp) + '\n')
    foupt.close()

def patch_va_table_2(inpt, sinpt, oupt):
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
            if grp[idx]:
                i = int(grp[idx])
                foupt.write(",{0},{1}\n".format(s[i], s[i] - s[i-1]))
            else:
                foupt.write(",0.0,0.0\n")


Base = declarative_base()
class Element(Base):
    __tablename__ = "elements"
    id = Column(Integer, primary_key=True)
    name     = Column(String)
    elemtype = Column(String)
    machine  = Column(String)
    cell     = Column(String)
    girder   = Column(String)
    symmetry = Column(String)
    s_end    = Column(Float)
    length   = Column(Float)

    tracy_el_idx_va = Column(Integer)
    tracy_machine   = Column(String)
    tracy_el_name_va = Column(String)
    tracy_el_type_va = Column(String)

    def __init__(self, name, elemtype, machine):
        self.name = name
        self.elemtype = elemtype
        self.machine = machine

    def __repr__(self):
        return "<Element '%s':'%s' ...>" % (self.name, self.elemtype)

class ChannelRecord(Base):
    #__tablename__ = 'cfdata_v0'
    __tablename__ = 'cfdata'

    pv       = Column(String, primary_key=True)
    elem_id  = Column(Integer, ForeignKey('elements.id'))
    devname  = Column(String)
    handle   = Column(String, nullable=False)
    hostname = Column(String)
    iocname  = Column(String)
    tags     = Column(String) # deliminator: ','

    element = relationship("Element", backref=backref("pvs", order_by=pv))

    def __init__(self, pv, elemName, handle = 'readback'):
        self.pv = pv
        self.elemname = elemName
        self.handle = handle

    def __repr__(self):
        return "<Channel('%s', '%s', ...)>" % (self.pv, self.elemname)


def create_sqlite_db(inpt, dbfname = "us_nsls2.sqlite"):
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
                filter(Element.name == grp[iname]).first()
            if not elem:
                elem = Element(grp[iname], grp[itype], grp[isys])
            elem.s_end = grp[isend]
            elem.length = grp[ilength]
            elem.cell = grp[icell]
            elem.girder = grp[igirder]
            elem.tracy_el_idx_va = grp[idx]
            elem.tracy_machine = grp[isys]

            if elem.cell and elem.girder:
                if elem.name.endswith('a'): elem.symmetry = 'A'
                elif elem.name.endswith('b'): elem.symmetry = 'B'

            pvr = session.query(ChannelRecord).\
                filter(ChannelRecord.pv == grp[ipv]).first()
            if not pvr:
                pvr = ChannelRecord(grp[ipv], elem.name, grp[ihandle])
            pvr.element = elem
            session.add(pvr)
            #session.add(elem)

        session.commit()


if __name__ == "__main__":
    patch_va_table_1(sys.argv[1], "output.txt")
    patch_va_table_2("output.txt", "s.txt", "cfd.txt")
    create_sqlite_db("cfd.txt")

