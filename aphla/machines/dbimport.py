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


def cgs_from_name(name):
    """parse Cell, Girder, Symmetry from elmeent name"""
    r = re.match(r'.+(G[0-9])(C[0-9][0-9])([ABC]).*', name.upper())
    if r:
        return r.groups()
    return None, None, None

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
    length     = Column(Float, default=0)
    position   = Column(Float, default=0)
    lat_index  = Column(Integer, default=0)
    elem_group = Column(String)
    virtual    = Column(Integer)
    k1         = Column(Float)
    k2         = Column(Float)
    angle      = Column(Float)
    polar      = Column(Integer, default=2)  # unipolar or bipolar

    tracy_el_idx_va  = Column(Integer)
    tracy_machine    = Column(String)
    tracy_el_name_va = Column(String)
    tracy_el_type_va = Column(String)

    __table_args__ = (UniqueConstraint('name', name='_uniq_name'),)
    #__table_args__ = (UniqueConstraint('name', 'system', 'cell', 'girder', name='_uniq_name'),)

    def __init__(self, name, elemtype, system = 'SR'):
        self.name = name
        self.elem_type = elemtype
        self.system = system
        self.virtual = 0
        self.tracy_el_idx_va = -1
        self.polar = 2

    def __repr__(self):
        return "<Element '%s':'%s' ...>" % (self.name, self.elem_type)

class ChannelRecord(Base):
    __tablename__ = 'pvs'

    pv = Column(String, primary_key=True)
    elem_id    = Column(Integer, ForeignKey('elements.elem_id'))
    elem_field = Column(String)
    handle     = Column(String, default='get')
    high_lim   = Column(Float)
    low_lim    = Column(Float)
    val0       = Column(Float)          # the initial/reference value
    dev_name   = Column(String)
    host_name  = Column(String)
    ioc_name   = Column(String)
    tags       = Column(String) # deliminator: ';'

    element = relationship("Element", backref=backref("pvs", order_by=elem_id))

    tracy_el_field_va = Column(String)


    def __init__(self, pv, handle = 'get'):
        self.pv = pv
        self.handle = handle

    def __repr__(self):
        return "<Channel('%s', '%s', ...)>" % (self.pv, self.element.name)


def import_lattice_table(inpt, dbfname, system = None, parsecgs = False):
    """
    The drift is always treated as different element.
    """
    engine = create_engine('sqlite:///' + dbfname, echo = False, 
                           convert_unicode=True)
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
            if parsecgs:
                elem.cell, elem.girder, elem.symmetry = cgs_from_name(name)

            session.add(elem)
            session.flush()

        session.commit()

def match_hvcors(reclst):
    import difflib
    paired = {}
    for i,r1 in enumerate(reclst[:-1]):
        if r1[0] in paired: continue
        names = []
        for j,r2 in enumerate(reclst[i+1:]):
            if r2[0] in paired: continue
            if r2[0] == r1[0]: continue
            if r2[0] in names: continue
            # the name can diff only one character
            if len(set(r1[0]) - set(r2[0])) > 1: continue
            # should be nearby in their index
            if abs(r2[1] - r1[1]) > 1: continue
            names.append(r2[0])
        if not names:
            print "'{0}' is not matched".format(r1[0])
            continue
        if len(names) > 1:
            raise RuntimeError("'{0}' matches more than one '{1}'".format(
                r1[0], names))

        name1, name2 = r1[0], names[0]
        name = ''
        for j in range(len(name1)):
            if name1[j] != name2[j]: continue
            name += name1[j]
 
        paired[name1] = name
        paired[name2] = name
        print "'{0}' and '{1}' are merged to '{2}'".format(name1, name2, name)
    print paired
    return paired

def import_va_table(inpt, dbfname = "us_nsls2.sqlite3", mergehvcor = False,
                    parsecgs = False):
    """
    Note:
    
    - The current VA has split correctors into H/V.
    """
    engine = create_engine('sqlite:///' + dbfname, echo = False, 
                           convert_unicode=True)
    # create table if not exists
    Base.metadata.create_all(engine)

    from sqlalchemy.orm import sessionmaker
    Session = sessionmaker(bind=engine)
    session = Session()

    k_pv       = 'pv_name'
    k_elemName = 'el_name_va'

    with open(inpt, 'r') as f:
        # the column number for its name
        col = {}
        for i,v in enumerate(re.findall('([^ ,#\n\r]+)', f.readline())):
            col[v] = i

        reclist = [v.strip() for v in f.readlines()]
        
        corlist, hvcor = [], {}
        for i,v in enumerate(reclist):
            if re.match(r'.* Corrector\s*$', v):
                r = v.split(',')
                name, idx = r[col['el_name_va']].lower(), r[col['el_idx_va']]
                corlist.append([name.strip(), int(idx)])
        # print corlist
        # check
        # hvcor = match_hvcors(corlist)

        for line in reclist:
            r = [v.strip() for v in line.split(',')]
            # the original data and converted
            d0 = dict([(v, r[col[v]]) for v in col.keys()])
            d = d0

            elemname = d[k_elemName].lower()
            if not elemname: continue

            pvr = session.query(ChannelRecord).\
                filter(ChannelRecord.pv == d[k_pv]).first()
            if not pvr:
                pvr = ChannelRecord(d[k_pv])
            
            # a fix for H/V correctors

            elems = session.query(Element).\
                filter(Element.name == elemname).\
                filter(Element.system == d['machine']).all()
            if len(elems) != 1:
                raise RuntimeError("Found %d element '%s:%s' in system '%s'" \
                                   % (len(elems), elemname, d['el_type_va'], d['machine']))
            elem = elems[0]
                
            if parsecgs:
                elem.cell, elem.girder, elem.symmetry = cgs_from_name(elemname)

            if d[k_elemName].lower() in hvcor: 
                #print "changing '{0}' type from '{1}' to '{2}'".format(elem.name, elem.elem_type, 'COR')
                elem.elem_type = 'COR'
                name0 = d[k_elemName].lower()
                hc = session.query(Element).filter(Element.name == name0).\
                     filter(Element.system == d['machine']).first()
                if hc:
                    elem.position = hc.position
                    elem.length = hc.length
                    elem.lat_index = hc.lat_index
                    elem.cell = hc.cell
                    elem.girder = hc.girder
                    elem.symmetry = hc.symmetry

            if d['girder']: elem.girder    = d['girder']
            if d['cell']: elem.cell      = d['cell']
            elem.handle    = d['handle']
            if d0['el_idx_va']: elem.tracy_el_idx_va  = int(d0['el_idx_va'])
            elem.tracy_machine    = d0['machine']
            if d0['el_name_va']: elem.tracy_el_name_va = d0['el_name_va']
            if d0['el_type_va']: elem.tracy_el_type_va = d0['el_type_va']

            #print elemname, d['machine'], elem.elem_id
            # merge to get new elem_id. Otherwise, no elem_id for pvr for new Element
            elem = session.merge(elem)

            pvr.elem_id = elem.elem_id
            if d0['el_field_va']: pvr.tracy_el_field_va = d0['el_field_va']
            pvr.handle = d['handle']
            pvr.elem_field = d0['el_field_va']

            session.add(elem)
            session.add(pvr)
            session.flush()
        session.commit()

def fix_correctors(dbfname, system):
    engine = create_engine('sqlite:///' + dbfname, echo = False,
                           convert_unicode=True)
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
    engine = create_engine('sqlite:///' + dbfname, echo = False,
                           convert_unicode=True)
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
            session.add(elem)

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
        pvr.tags = ';'.join(tags)
        pvr.elem_field = prpts.get('elemField', None)
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
    parser.add_argument('--mergehvcor', action="store_true", 
                        help="merge H/V corr in va table")  
    parser.add_argument('--parsecgs', action="store_true", 
                        help="merge H/V corr in va table")    
    args = parser.parse_args()

    #print args
    #print args.dbfile

    #dbfname = "us_nsls2v1.sqlite"
    dbfname = args.dbfile
    if args.par: 
        import_lattice_table(args.par, dbfname, args.system, args.parsecgs)
    if args.va: import_va_table(args.va, dbfname, args.mergehvcor, args.parsecgs)
    if args.cf2: import_cf2(args.cf2, dbfname)
    #if args.fixcorrectors:
    #    fix_correctors(dbfname, args.system)
