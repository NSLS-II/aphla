"""
import the explicit csv file to db
"""

from sqlalchemy import Column, Integer, String, Float, ForeignKey, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref

import sys
import csv

Base = declarative_base()
class Element(Base):
    __tablename__ = "elements"
    elem_id = Column(Integer, primary_key=True)
    name     = Column('elemName', String)
    elemtype = Column('elemType', String)
    machine  = Column('system', String)
    cell     = Column(String)
    girder   = Column(String)
    symmetry = Column(String)
    s_end    = Column('elemPosition', Float)
    length   = Column('elemLength', Float)
    virtual  = Column(Integer)
    el_idx   = Column('elemIndex', Integer)

    tracy_el_idx_va = Column(Integer)
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
    elem_field = Column('elemField', String)

    tracy_el_field_va = Column(String)

    element = relationship("Element", backref=backref("pvs", order_by=pv))

    def __init__(self, pv, elemName, handle = 'readback'):
        self.pv = pv
        self.elemname = elemName
        self.handle = handle

    def __repr__(self):
        return "<Channel('%s', '%s', ...)>" % (self.pv, self.elemname)


def update_sqlite_db(inpt, dbfname = "us_nsls2.db"):
    engine = create_engine('sqlite:///' + dbfname, echo = False)
    Base.metadata.create_all(engine)

    from sqlalchemy.orm import sessionmaker
    Session = sessionmaker(bind=engine)
    session = Session()

    rd = csv.reader(open(inpt, 'r'))
    for sraw in rd:
        if len(sraw) == 0: continue
        s = [v.strip() for v in sraw]
        pv = s[0]
        if not pv or pv.strip().startswith('#'): continue
        #and len(prpts) == 0: continue

        prpts, tags = {}, []
        for cell in s[1:]:
            if cell.find('=') > 0:
                k, v = cell.split('=')
                prpts[k.strip()] = v.strip()
            else:
                tags.append(cell.strip())

        # required properties
        for k in ['elemHandle', 'elemName']:
            if k not in prpts:
                raise RuntimeError("missing '%s' for %s" % (k,s))

        elem = session.query(Element).\
            filter(Element.name == prpts['elemName'].lower()).first()
        if not elem:
            elem = Element(prpts['elemName'].lower(),
                           prpts['elemType'], prpts['system'])
        elem.s_end = prpts['elemPosition']
        elem.length = prpts['elemLength']

        if 'cell' in prpts: elem.cell = prpts['cell']
        if 'girder' in prpts: elem.girder = prpts['girder']
        if 'elemIndex' in prpts: elem.el_idx = prpts['elemIndex']
        if 'symmetry' in prpts: elem.symmetry = prpts['symmetry']

        pvr = session.query(ChannelRecord).\
            filter(ChannelRecord.pv == pv).first()
        if not pvr:
            pvr = ChannelRecord(pv, elem.name, prpts['elemHandle'])
        pvr.element = elem
        pvr.tags = ','.join(tags)
        if 'elemField' in prpts: pvr.elem_field = prpts['elemField']

        session.add(pvr)

    session.commit()


if __name__ == "__main__":
    if len(sys.argv) > 2:
        dbname = sys.argv[2]
    else:
        dbname = "us_nsls2.db"
    update_sqlite_db(sys.argv[1], dbname)
