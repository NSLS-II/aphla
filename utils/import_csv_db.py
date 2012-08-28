from sqlalchemy import Column, Integer, String, Float, ForeignKey, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref

import sys

Base = declarative_base()
class Element(Base):
    __tablename__ = "elements"
    id = Column(Integer, primary_key=True)
    name     = Column('elemName', String)
    elemtype = Column('elemType', String)
    machine  = Column('system', String)
    cell     = Column(String)
    girder   = Column(String)
    symmetry = Column(String)
    s_end    = Column('sEnd', Float)
    length   = Column(Float)
    virtual  = Column(Integer)

    tracy_el_idx_va = Column('ordinal', Integer)
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
    elem_id  = Column(Integer, ForeignKey('elements.id'))
    devname  = Column('devName', String)
    handle   = Column(String, nullable=False)
    hostname = Column('hostName', String)
    iocname  = Column('iocName', String)
    tags     = Column(String) # deliminator: ','

    tracy_el_field_va = Column(String)

    element = relationship("Element", backref=backref("pvs", order_by=pv))

    def __init__(self, pv, elemName, handle = 'readback'):
        self.pv = pv
        self.elemname = elemName
        self.handle = handle

    def __repr__(self):
        return "<Channel('%s', '%s', ...)>" % (self.pv, self.elemname)


def update_sqlite_db(inpt, dbfname = "us_nsls2.sqlite3"):
    engine = create_engine('sqlite:///' + dbfname, echo = False)
    Base.metadata.create_all(engine)

    from sqlalchemy.orm import sessionmaker
    Session = sessionmaker(bind=engine)
    session = Session()

    with open(inpt, 'r') as f:
        head = [v.strip() for v in f.readline().split(',')]
        ipv = head.index('PV')
        iname = head.index('elemName')
        itype = head.index('elemType')
        isys = head.index('system')
        isend = head.index('sEnd')
        ilength = head.index('length')
        icell = head.index('cell')
        igirder = head.index('girder')
        idx = head.index('ordinal')
        ihandle = head.index('handle')
        ifield = head.index('elemField')
        itags = len(head)
        #print head,
        #print ipv, iname
        for rec in f.readlines():
            grp = rec.split(',')
            #print len(grp), grp
            elem = session.query(Element).\
                filter(Element.name == grp[iname].lower()).first()
            if not elem:
                elem = Element(grp[iname].lower(), grp[itype], grp[isys])
            elem.s_end = grp[isend]
            elem.length = grp[ilength]
            if grp[icell]: elem.cell = grp[icell]
            if grp[igirder]: elem.girder = grp[igirder]
            if grp[idx]: elem.tracy_el_idx_va = grp[idx]
            else: elem.tracy_el_idx_va = -1
            elem.tracy_machine = grp[isys]

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
            pvr.tags = ','.join(grp[itags:])
            session.add(pvr)
            #session.add(elem)

        session.commit()


if __name__ == "__main__":
    update_sqlite_db(sys.argv[1], "us_nsls2v1.db")
