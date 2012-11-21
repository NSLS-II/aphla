"""
process "nsls2srid_prop.csv" from "CD3-Aug15-11-oneCell-norm-Aug19-tracy.lat".

-- 2012/08/21
"""

import sys, os
import re
import argparse 
import warnings

from sqlalchemy import (Column, Integer, String, Float, ForeignKey, 
                        create_engine, UniqueConstraint, and_)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref

C = 787.793/30

# mapping old tracy type of aphla type.
def conv(k, *args, **kwargs):
    d = { 'Horizontal Corrector': 'HCOR',
          'Vertical Corrector': 'VCOR',
          'Sextupole': 'SEXT',
          'Beam Position Monitor': 'BPM',
          'Quadrupole': 'QUAD',
          'Bending': 'DIPOLE',
          'insertion': 'INSERTION',
          'readback': 'get',
          'setpoint': 'set',
          'V:2-SR': 'V2SR',
          ('Horizontal Corrector', ''): 'x',
          ('Vertical Corrector', ''): 'y',
          ('Beam Position Monitor', 'X'): 'x',
          ('Beam Position Monitor', 'Y'): 'y',
          ('Quadrupole', 'K'): 'k1',
          ('Sextupole', 'K'): 'k2',
          ('Bending', 'T'): 'bend',
          ('insertion', 'GAP'): 'gap',
          ('insertion', 'PHASE'): 'phase',
          }
    if k in d.keys(): return d[k]
    elif isinstance(k, tuple):
        if not k[0]: return k[1] # special case for 'tune', 'twiss'
    elif 'quiet' not in args:
        #raise RuntimeError("unknow key '%s'" % k)
        warnings.warn("unknow key '{0}'".format(k))
    return k


Base = declarative_base()
class Element(Base):
    __tablename__ = "elements"
    elem_id    = Column(Integer, primary_key=True)
    name       = Column(String, nullable=False)
    elem_type  = Column(String)
    system     = Column(String, nullable=False)
    cell       = Column(String)
    girder     = Column(String)
    symmetry   = Column(String)
    length     = Column(Float)
    position   = Column(Float)
    lat_index  = Column(Integer)
    elem_group = Column(String)
    virtual    = Column(Integer)
    k1         = Column(Float)
    k2         = Column(Float)
    angle      = Column(Float)

    tracy_el_idx_va  = Column(Integer)
    tracy_machine    = Column(String)
    tracy_el_name_va = Column(String)
    tracy_el_type_va = Column(String)


    __table_args__ = (UniqueConstraint('name', 'system', 'cell', 'girder', name='_uniq_name'),)

    def __init__(self, name, elemtype, system = 'SR'):
        self.name = name
        self.elem_type = elemtype
        self.system = system
        self.virtual = 0
        self.tracy_el_idx_va = -1

    def __repr__(self):
        return "<Element '%s':'%s' ...>" % (self.name, self.elem_type)

class ChannelRecord(Base):
    #__tablename__ = 'cfdata_v0'
    __tablename__ = 'pvs'

    pv = Column(String, primary_key=True)
    elem_id    = Column(Integer, ForeignKey('elements.elem_id'))
    elem_field = Column(String)
    handle     = Column(String, default='get')
    high_lim   = Column(Float)
    low_lim    = Column(Float)
    dev_name   = Column(String)
    host_name  = Column(String)
    ioc_name   = Column(String)
    tags       = Column(String) # deliminator: ','

    element = relationship("Element", backref=backref("pvs", order_by=elem_id))

    tracy_el_field_va = Column(String)


    def __init__(self, pv, handle = 'get'):
        self.pv = pv
        self.handle = handle

    def __repr__(self):
        return "<Channel('%s', '%s', ...)>" % (self.pv, self.element.name)


def import_lattice_table(inpt, dbfname, system = None):
    """
    The drift is always treated as different element.
    """
    engine = create_engine('sqlite:///' + dbfname, echo = False)
    # create table if not exists
    Base.metadata.create_all(engine)

    from sqlalchemy.orm import sessionmaker
    Session = sessionmaker(bind=engine)
    session = Session()

    with open(inpt, 'r') as f:
        head = f.readline()
        f.readline()
        f.readline()
        for i,rec in enumerate(f.readlines()):
            grp = rec.split()
            name     = grp[0].lower()
            elemtype = grp[1]
            elem = session.query(Element).\
                filter(Element.name == name).first()
            if not elem:
                elem = Element(name, elemtype)

            elem.length, elem.position, elem.k1, elem.k2, elem.angle = \
                [float(v) for v in grp[2:7]]
            elem.lat_index = i
            if system is not None: elem.system = system
            # drift used in multiple places
            #if elemtype in ['DRIF']: elem.position = None

            session.add(elem)
            session.flush()

        session.commit()

def import_va_table(inpt, dbfname = "us_nsls2.sqlite3"):
    """
    Note:
    
    - The current VA has split correctors into H/V.
    """
    engine = create_engine('sqlite:///' + dbfname, echo = False)
    # create table if not exists
    Base.metadata.create_all(engine)

    from sqlalchemy.orm import sessionmaker
    Session = sessionmaker(bind=engine)
    session = Session()

    # the 
    k_pv       = 'pv_name'
    k_elemName = 'el_name_va'

    with open(inpt, 'r') as f:
        # the column number for its name
        col = {}
        for i,v in enumerate(re.findall('([^ ,#\n\r]+)', f.readline())):
            col[v] = i

        for line in f.readlines():
            r = [v.strip() for v in line.split(',')]
            # the original data and converted
            d0 = dict([(v, r[col[v]]) for v in col.keys()])
            d = dict([(k, conv(v, 'quiet')) for k,v in d0.iteritems()])

            elemname = d[k_elemName].lower()
            if not elemname: continue

            # a fix for H/V correctors
            if re.match(r'[cf][xy][hlm]\dg\dc[0-9][0-9].', elemname):
                elemname = elemname[0] + elemname[2:]
                elemtype = 'COR'

            pvr = session.query(ChannelRecord).\
                filter(ChannelRecord.pv == d[k_pv]).first()
            if not pvr:
                pvr = ChannelRecord(d[k_pv])
            
            elem = session.query(Element).\
                filter(Element.name == elemname).\
                filter(Element.system == d['machine']).first()
            if not elem:
                raise RuntimeError("Element '%s' is not found in table" % elemname)

                elem = Element(elemname, elemtype, d['machine'])
                session.add(elem)
                
            elem = session.query(Element).\
                filter(Element.name == elemname).\
                filter(Element.system == d['machine']).first()

            elem.elem_type = elemtype
            elem.girder    = d['girder']
            elem.cell      = d['cell']
            elem.handle    = d['handle']
            if d0['el_idx_va']: elem.tracy_el_idx_va  = int(d0['el_idx_va'])
            elem.tracy_machine    = d0['machine']
            if d0['el_name_va']: elem.tracy_el_name_va = d0['el_name_va']
            if d0['el_type_va']: elem.tracy_el_type_va = d0['el_type_va']

            #print elemname, d['machine'], elem.elem_id
            #elem = session.merge(elem)

            pvr.elem_id = elem.elem_id
            if d0['el_field_va']: pvr.tracy_el_field_va = d0['el_field_va']
            pvr.handle = d['handle']
            pvr.elem_field = conv((d0['el_type_va'], d0['el_field_va']))

            session.add(pvr)
            session.flush()
        session.commit()

def fix_correctors(dbfname, system):
    engine = create_engine('sqlite:///' + dbfname, echo = False)
    # create table if not exists
    Base.metadata.create_all(engine)

    from sqlalchemy.orm import sessionmaker
    Session = sessionmaker(bind=engine)
    session = Session()

    for elem in session.query(Element).\
            filter(Element.elemtype.like('%COR')).all():
        if not re.match(r'[cf][xy].+', elem.name): continue
        devname = elem.name[0] + elem.name[2:]
        cors = session.query(Element).filter(Element.name == devname).all()
        if len(cors) > 1:
            raise RuntimeError("'{0}' has more than one matching devices: {1}".format(elem.name, cors))
        elem.s_end  = cors[0].s_end
        elem.length = cors[0].length
        session.add(elem)
    session.commit()

def import_cf2(inpt, dbfname):
    engine = create_engine('sqlite:///' + dbfname, echo = False)
    # create table if not exists
    Base.metadata.create_all(engine)

    from sqlalchemy.orm import sessionmaker
    Session = sessionmaker(bind=engine)
    session = Session()

    f = open(inpt, 'r')
    for i,line in enumerate(f.readlines()):
        line = line.strip()
        if line.startswith('#'): continue
        r = [v.strip() for v in line.split(',')]

        pv = r[0]
        if not pv: continue

        prpts, tags = {}, []
        for col in r[1:]:
            try:
                k, v = col.split('=')
                prpts[k.strip()] = v.strip()
            except ValueError as e:
                tags.append(col)

        #print pv, prpts, tags
        if 'elemName' not in prpts:
            raise RuntimeError("pv '%s' has no elemName in line: %s" % (pv, line))

        pvr = session.query(ChannelRecord).\
            filter(ChannelRecord.pv == pv).first()
        if not pvr:
            pvr = ChannelRecord(pv)


        elem = session.query(Element).\
            filter(Element.name == prpts['elemName']).\
            filter(Element.system == prpts['system']).first()
        if not elem:
            elem = Element(prpts['elemName'], prpts['elemType'], 
                           prpts['system'])
        elem.elem_type = prpts['elemType']
        elem.position  = prpts['elemPosition']
        elem.length    = prpts['elemLength']
        elem.lat_index = prpts['elemIndex']
        #elem.handle   = prpts['handle']
        if 'girder' in prpts: elem.girder   = prpts['girder']
        if 'cell' in prpts:   elem.cell     = prpts['cell']

        elem = session.merge(elem)

        pvr.elem_id = elem.elem_id
        pvr.handle = prpts['elemHandle']
        pvr.dev_name = prpts['devName']
        if 'elemField' in prpts: pvr.elemField = prpts['elemField']
        session.add(pvr)
        session.flush()

    session.commit()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Import data to aphla database")
    parser.add_argument('dbfile', type=str, help="SQLite database file",
                        default='aphla.sqlite')
    parser.add_argument('--system', metavar='SR', type=str, 
                        help="system name for element")
    parser.add_argument('--par', metavar='CD3.txt', type=str, 
                        help="lattice parameters")
    parser.add_argument('--va', metavar='nsls2.csv', type=str, 
                        help="virtual acc data")
    parser.add_argument('--cf1', metavar='cf1.csv', type=str, 
                        help="channel finder v1 csv data")
    parser.add_argument('--cf2', metavar='cf2.csv', type=str, 
                        help="channel finder v2 csv data")
    parser.add_argument('--twiss', metavar='twiss.txt', type=str, 
                        help="twiss data")
    #parser.add_argument('--fixcorrectors', action="store_true", 
    #                    help="twiss data")    
    args = parser.parse_args()

    #print args
    #print args.dbfile

    #dbfname = "us_nsls2v1.sqlite"
    dbfname = args.dbfile
    if args.par: import_lattice_table(args.par, dbfname, args.system)
    if args.va: import_va_table(args.va, dbfname)
    if args.cf2: import_cf2(args.cf2, dbfname)
    #if args.fixcorrectors:
    #    fix_correctors(dbfname, args.system)
