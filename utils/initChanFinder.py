#!/usr/bin/env python

"""
This script initialized some PVs in channel finder. The PVs are only those
used by HLA.

:author: Lingyun Yang
:date: 2011-05-11 16:22
"""

import os, sys
import re, time, csv

from channelfinder.ChannelFinderClient import ChannelFinderClient
from channelfinder.CFDataTypes import Channel, Property, Tag

from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()
from sqlalchemy import Column, Integer, String, Float
class ChannelRecord(Base):
    __tablename__ = 'channelfinder'

    pv       = Column(String, primary_key=True)
    elemname = Column(String)
    elemtype = Column(String)
    devname  = Column(String)
    cell     = Column(String)
    girder   = Column(String)
    symmetry = Column(String)
    handle   = Column(String)
    length   = Column(Float)
    hostname = Column(String)
    iocname  = Column(String)
    ordinal  = Column(Integer)
    send     = Column(Float)
    system   = Column(String)
    tags     = Column(String) # deliminator: ','

    tracy_el_idx_va = Column(Integer)
    tracy_machine   = Column(String)
    tracy_el_name_va = Column(String)
    tracy_el_field_va = Column(String)
    tracy_el_type_va = Column(String)

    def __init__(self, pv, elemName):
        self.pv = pv
        self.elemname = elemName

    def __repr__(self):
        return "<Channel('%s', '%s', ...)>" % (self.pv, self.elemname)




def _process_tracy_va_pvrecord(data, apsys = 'aphla.sys.V1SR'):
    """
    convert pv record "dict" and return 
    - pv string
    - properties dict
    - tags list of string
    """

    pv = data["#pv_name"]
    prpts, tags = {}, [apsys]
    elem_type = {'Beam Position Monitor': 'BPM',
                 'Sextupole': 'SEXT', 'Quadrupole': 'QUAD',
                 'Horizontal Corrector': 'HCOR',
                 'Vertical Corrector': 'VCOR',
                 'Bending': 'DIPOLE',
                 'Cavity': 'CAVITY'}

    # required
    prpts.setdefault('system', data['machine'])
    prpts.setdefault('ordinal', data.get('el_idx_va', -1))

    prpts.setdefault('cell', data.get('cell', None))
    prpts.setdefault('girder', data.get('girder', None))

    name = data.get('el_name_va', None)
    if name == None:
        if pv.find('{TUNE}X') > 0: prpts.setdefault('elemName', 'tune')
        elif pv.find('{TUNE}Y') > 0: prpts.setdefault('elemName', 'tune')
        elif pv.find('{ALPHA}X') > 0: prpts.setdefault('elemName', 'alpha')
        elif pv.find('{ALPHA}Y') > 0: prpts.setdefault('elemName', 'alpha')
        elif pv.find('{BETA}X') > 0: prpts.setdefault('elemName', 'beta')
        elif pv.find('{BETA}Y') > 0: prpts.setdefault('elemName', 'beta')
        elif pv.find('{ETA}X') > 0: prpts.setdefault('elemName', 'eta')
        elif pv.find('{ETA}Y') > 0: prpts.setdefault('elemName', 'eta')
        elif pv.find('{PHI}X') > 0: prpts.setdefault('elemName', 'phi')
        elif pv.find('{PHI}Y') > 0: prpts.setdefault('elemName', 'phi')
        elif pv.find('{ORBIT}X') > 0: prpts.setdefault('elemName', 'orbit')
        elif pv.find('{ORBIT}Y') > 0: prpts.setdefault('elemName', 'orbit')
        elif pv.find('{POS}-I') > 0: prpts.setdefault('elemName', 'pos')
        elif pv.find('{ALPHA}Y') > 0: prpts.setdefault('elemName', 'alpha')
        elif pv.find('{DCCT}CUR-') > 0: prpts.setdefault('elemName', 'dcct')
        else:
            raise RuntimeError("pv '%s' has no element name" % pv)
    elif name == 'BPM':
        prpts.setdefault('elemName', 'p_bpm_%03d' % int(prpts['ordinal']))
    elif name == 'CH':
        prpts.setdefault('elemName', 'ch_%03d' % int(prpts['ordinal']))
    elif name == 'CV':
        prpts.setdefault('elemName', 'cv_%03d' % int(prpts['ordinal']))
    elif name == 'CHIDSim':
        prpts.setdefault('elemName', 'chidsim_%03d' % int(prpts['ordinal']))
    elif name == 'CVIDSim':
        prpts.setdefault('elemName', 'cvidsim_%03d' % int(prpts['ordinal']))
    elif name == 'CAV':
        prpts.setdefault('elemName', 'RFCAVITY0')
    else:
        prpts.setdefault('elemName', name.lower())

    if data.get('el_type_va', None) is None:
        if prpts['elemName'] in ['dcct']:
            prpts.setdefault('elemType', 'DCCT')
        elif prpts['elemName'] not in [
            'tune', 'alpha', 'beta', 'eta', 'phi', 'orbit', 'pos']: 
            raise RuntimeError("pv '%s' has no element type" % pv)
    else:
        prpts.setdefault('elemType', elem_type[data['el_type_va']])

    prpts.setdefault('handle', data['handle'])
    # elemfield tag
    if prpts.get('elemType', None) == 'QUAD':
        if data.get('el_field_va', None) == 'K': tags.append('aphla.elemfield.k1')
    elif prpts.get('elemType', None) == 'SEXT':
        if data.get('el_field_va', None) == 'K': tags.append('aphla.elemfield.k2')
    elif prpts.get('elemType', None) == 'HCOR':
        #if data.get('el_field_va', None) == 'CH': tags.append('aphla.elemfield.x')
        tags.append('aphla.elemfield.x')
    elif prpts.get('elemType', None) == 'VCOR':
        #if data.get('el_field_va', None) == 'CV': tags.append('aphla.elemfield.y')
        tags.append('aphla.elemfield.y')
    
    return pv, prpts, tags

def convert_tracy_va_table(dbfname = 'us_nsls2.sqlite'):
    pass

def update_pvr(pvr, col, r1):
    if col == "elemname":
        if pvr.pv.find('{TUNE}X') > 0 or pvr.pv.find('{TUNE}Y') > 0: 
            pvr.elemname = 'tune'
        elif pvr.pv.find('{ALPHA}X') > 0 or pvr.pv.find('{ALPHA}Y') > 0: 
            pvr.elemname = 'alpha'
        elif pvr.pv.find('{BETA}X') > 0 or pvr.pv.find('{BETA}Y') > 0: 
            pvr.elemname = 'beta'
        elif pvr.pv.find('{ETA}X') > 0 or pvr.pv.find('{ETA}Y') > 0: 
            pvr.elemname = 'eta'
        elif pvr.pv.find('{PHI}X') > 0 or pvr.pv.find('{PHI}Y') > 0: 
            pvr.elemname = 'phi'
        elif pvr.pv.find('{ORBIT}X') > 0 or pvr.pv.find('{ORBIT}Y') > 0: 
            pvr.elemname = 'orbit'
        elif pvr.pv.find('{POS}-I') > 0: 
            pvr.elemname = 'pos'
        elif pvr.pv.find('{DCCT}CUR-') > 0: 
            pvr.elemname = 'dcct'
        elif pvr.tracy_el_name_va == 'BPM':
            pvr.elemname = "p_bpm_%03d" % int(pvr.ordinal)
        elif pvr.tracy_el_name_va == 'CH':
            pvr.elemname = "hcor_%03d" % int(pvr.ordinal)
        elif pvr.tracy_el_name_va == 'CV':
            pvr.elemname = "vcor_%03d" % int(pvr.ordinal)
        elif pvr.tracy_el_type_va == 'Sextupole':
            pvr.elemname = pvr.elemname[:3] + pvr.girder + pvr.cell + pvr.symmetry
    elif col == 'elemtype': 
        if pvr.tracy_el_type_va == 'Sextupole':
            pvr.elemtype = "SEXT"
        elif pvr.tracy_el_type_va == 'Quadrupole':
            pvr.elemtype = "QUAD"
        elif pvr.tracy_el_type_va == "Beam Position Monitor":
            pvr.elemtype = "BPM"
        elif pvr.tracy_el_type_va == "Horizontal Corrector":
            pvr.elemtype = "HCOR"
        elif pvr.tracy_el_type_va == "Vertical Corrector":
            pvr.elemtype = "VCOR"
        elif pvr.tracy_el_type_va == "Bending":
            pvr.elemtype = "DIPOLE"
    elif col == "handle":
        if pvr.pv.find("{BPM:") > 0: 
            pvr.handle = 'readback'
    elif col == "tags":
        tags = ["aphla.sys.V1SR"]
        if pvr.elemtype == "QUAD":
            if pvr.tracy_el_field_va == "K":
                tags.append("aphla.elemfield.k1")
        elif pvr.elemtype == "SEXT":
            if pvr.tracy_el_field_va == "K":
                tags.append("aphla.elemfield.k2")
        elif pvr.elemtype == "BPM":
            if pvr.pv[-4:] == "SA:X": tags.append("aphla.elemfield.x")
            elif pvr.pv[-4:] == "SA:Y": tags.append("aphla.elemfield.y")
        elif pvr.elemtype == "HCOR":
            if pvr.pv.find("Fld:") > 0: tags.append("aphla.elemfield.x")
        elif pvr.elemtype == "VCOR":
            if pvr.pv.find("Fld:") > 0: tags.append("aphla.elemfield.y")
        pvr.tags = ",".join(tags)

def import_tracy_va_table(fname, dbfname = 'us_nsls2.sqlite'):
    """
    initialize Channel finder from Tracy Virtual Accelerator data::

      #pv_name, el_idx_va, machine, cell, girder, handle, el_name_va, el_field_va, el_type_va
      V:1-SR:C30-MG:G2{SH1:7}Fld:SP,7,V:1-SR,C30,G2,setpoint,SH1G2C30A,K,Sextupole
      V:1-SR:C30-MG:G2{SH1:7}Fld:I,7,V:1-SR,C30,G2,readback,SH1G2C30A,K,Sextupole
      V:1-SR:C30-BI:G2{BPM:9}SA:X,9,V:1-SR,C30,G2,X,BPM,,Beam Position Monitor
      V:1-SR:C30-BI:G2{BPM:9}SA:Y,9,V:1-SR,C30,G2,Y,BPM,,Beam Position Monitor
      V:1-SR:C30-MG:G2{QH1:11}Fld:SP,11,V:1-SR,C30,G2,setpoint,QH1G2C30A,K,Quadrupole
      V:1-SR:C30-MG:G2{QH1:11}Fld:I,11,V:1-SR,C30,G2,readback,QH1G2C30A,K,Quadrupole

    Assumes the PV is already in.
    """

    from sqlalchemy import create_engine
    engine = create_engine('sqlite:///' + dbfname, echo = False)
    Base.metadata.create_all(engine) 

    from sqlalchemy.orm import sessionmaker
    Session = sessionmaker(bind=engine)
    session = Session()


    with open(fname, 'r') as f:
        dialect = csv.excel
        dialect.skipinitialspace = True
        rd = csv.DictReader(f, dialect=dialect)
        for rec in rd:
            r1 = dict([(k,rec[k]) for k in rec.keys() if rec[k].strip()])
            #pv, prpts, tags = _process_tracy_va_pvrecord(r1)
            pvr = session.query(ChannelRecord).\
                filter(ChannelRecord.pv == r1['#pv_name']).first()
            if not pvr:
                pvr = ChannelRecord(r1['#pv_name'], r1.get("el_name_va", ""))

            pvr.ordinal = r1.get('el_idx_va', -1)
            pvr.cell   = r1.get('cell', '')
            pvr.girder = r1.get('girder', '')
            pvr.handle = r1['handle']
            pvr.system = r1.get('machine', '')
            pvr.symmetry = r1.get('symmetry', '')
            #
            pvr.tracy_el_idx_va = r1.get('el_idx_va', -1)
            pvr.tracy_machine   = r1.get('machine', "")
            pvr.tracy_el_name_va  = r1.get('el_name_va', "")
            pvr.tracy_el_type_va  = r1.get('el_type_va', "")
            pvr.tracy_el_field_va = r1.get('el_field_va', '')
            # cell
            # girder
            # handle
            update_pvr(pvr, "elemname", r1)
            update_pvr(pvr, "elemtype", r1)
            update_pvr(pvr, "handle", r1)
            update_pvr(pvr, "tags", r1)

            session.add(pvr)
            #session.flush()

        session.commit()
            

def import_cfa_table(fname, dbfname = 'us_nsls2.sqlite'):
    """
    """

    from sqlalchemy import create_engine
    engine = create_engine('sqlite:///' + dbfname, echo = False)
    Base.metadata.create_all(engine) 

    from sqlalchemy.orm import sessionmaker
    Session = sessionmaker(bind=engine)
    session = Session()


    with open(fname, 'r') as f:
        dialect = csv.excel
        dialect.skipinitialspace = True
        rd = csv.DictReader(f, dialect=dialect, restkey='tags')
        for rec in rd:
            #print rec
            r1 = dict([(k,rec[k]) for k in rec.keys() if k != 'tags' and rec[k].strip()])
            #pv, prpts, tags = _process_tracy_va_pvrecord(r1)
            #print r1
            #continue

            pvr = session.query(ChannelRecord).\
                filter(ChannelRecord.pv == r1['PV']).first()
            if not pvr:
                pvr = ChannelRecord(r1['PV'], r1.get("elemName", ""))

            pvr.ordinal = r1.get('ordinal', -1)
            pvr.cell   = r1.get('cell', '')
            pvr.girder = r1.get('girder', '')
            pvr.handle = r1['handle'].lower()
            pvr.system = r1.get('system', '')
            pvr.devname = r1.get('devName', '')
            pvr.elemtype = r1.get('elemType', '')
            pvr.symmetry = r1.get('symmetry', None)
            pvr.send = r1.get('sEnd', None)
            pvr.length = r1.get('length', None)
            pvr.hostname = r1.get('hostname', None)
            pvr.iocname = r1.get('iocname', None)

            #
            #pvr.tracy_el_idx_va = r1.get('el_idx_va', -1)
            #pvr.tracy_machine   = r1.get('machine', "")
            #pvr.tracy_el_name_va  = r1.get('el_name_va', "")
            #pvr.tracy_el_type_va  = r1.get('el_type_va', "")
            #pvr.tracy_el_field_va = r1.get('el_field_va', '')
            # cell
            # girder
            # handle
            #update_pvr(pvr, "elemname", r1)
            #update_pvr(pvr, "elemtype", r1)
            #update_pvr(pvr, "handle", r1)
            #update_pvr(pvr, "tags", r1)
            pvr.tags = ','.join(rec.get('tags', []))

            session.add(pvr)
            #session.flush()

        session.commit()

def dump_hla_cfa(out):
    hla._cfa.exportTextRecord(out)

def clean_small_cases_ones():
    pass

def initialize_cfs(out):
    all_keys, all_tags = [], []
    cfsurl = 'http://channelfinder.nsls2.bnl.gov:8080/ChannelFinder'
    cf = ChannelFinderClient(BaseURL = cfsurl, username='boss', password='1234')

    # clean up
    props = cf.getAllProperties()
    #cf.set(properties = [Property('ORDINAL', '85')])
    cfchannels = []
    for line in open(out, 'r').readlines():
        if line.strip()[0] == '#': continue
        # three parts, "pv; properties; tags"
        rec = line.split(';')
        pv, pstr, tagstr = rec
        chs = cf.find(name=pv.strip())
        if not chs:
            print "Did not find", pv
            continue
        if len(chs) > 1:
            print "PV is not unique:", pv
            continue
        
        prop, tags = {}, []
        for r in pstr.split(','):
            if not r: continue
            # all in upper cases
            k,v = r.upper().split('=')
            k = k.strip()
            v = v.strip()
            prop[k] = v
            if not k in all_keys: all_keys.append(k)

        for r in tagstr.split()[1:]:
            if r == 'default.eput': r = 'HLA.EPUT'
            elif r == 'default.eget': r = 'HLA.EGET'
            elif not r.startswith('HLA.'): r = 'HLA.' + r

            if not r in all_tags: all_tags.append(r)
            
            tags.append(r)
        #print pv, prop, tags
        cfprop = [Property(k, 'HLA', v) for k,v in prop.items()]
        cftags = [Tag(t, 'HLA') for t in tags]
        cfchannels.append(Channel(u'%s' % pv, 'HLA', properties=cfprop, tags=cftags))
        #cf.update(channel = Channel(pv, 'HLA'), properties=cfprop,
        #          tags = cftags)
        
    print ""
    print all_keys
    print all_tags
    cfprop = [Property(p, 'HLA', 'N.A.') for p in all_keys]
    cf.set(properties = cfprop)
    cftags = [Tag(t, 'HLA') for t in all_tags]
    cf.set(tags = cftags)    
    cf.set(channels=cfchannels)

def update_cfs(out):
    # same as initi_cfs for now
    #
    all_keys, all_tags = [], []
    cfsurl = 'http://channelfinder.nsls2.bnl.gov:8080/ChannelFinder'
    cf = ChannelFinderClient(BaseURL = cfsurl, username='boss', password='1234')

    # clean up
    props = cf.getAllProperties()
    #cf.set(properties = [Property('ORDINAL', '85')])
    cfchannels = []
    for line in open(out, 'r').readlines():
        if line.strip()[0] == '#': continue
        # three parts, "pv; properties; tags"
        pv, pstr, tagstr = [r.strip() for r in line.split(';')]
        chs = cf.find(name=pv.strip())
        if not chs:
            print "Did not find '%s'" % pv
            #cf.set(channel=Channel(pv, 'HLA'))
            #continue
        elif len(chs) > 1:
            print "PV is not unique:", pv
            continue
        
        prop, tags = {}, []
        for r in pstr.split(','):
            if not r: continue
            # all in upper cases
            k,v = r.upper().split('=')
            k = k.strip()
            v = v.strip()
            prop[k] = v
            if not k in all_keys: all_keys.append(k)

        for r in tagstr.split(','):
            tg = r.strip()
            if tg == '~tags=': continue

            if not tg in all_tags: all_tags.append(tg)
            
            tags.append(tg)
        #print pv, prop, tags
        cfprop = [Property(k, 'HLA', v) for k,v in prop.items()]
        cftags = [Tag(t, 'HLA') for t in tags]
        cfchannels.append(Channel(u'%s' % pv, 'HLA', properties=cfprop, tags=cftags))
        #cf.update(channel = Channel(pv, 'HLA'), properties=cfprop,
        #          tags = cftags)
        
    print ""
    print "keys:", all_keys
    print "tags:", all_tags
    print "channels:", len(cfchannels)
    if all_keys:
        cfprop = [Property(p, 'HLA', 'N.A.') for p in all_keys]
        #cf.set(properties = cfprop)
        #for p in cfprop:
        #    cf.update(p)
    if all_tags:
        cftags = [Tag(t, 'HLA') for t in all_tags]
        cf.set(tags = cftags)    
        #for t in cftags:
        #    cf.update(t)
    #for ch in cfchannels:
    #    cf.update(channel=ch)
    cf.set(channels = cfchannels)
    #for c in cfchannels:
    #    print c.Name, c.getProperties(), c.getTags()

def test():
    cfsurl = 'http://channelfinder.nsls2.bnl.gov:8080/ChannelFinder'
    cf = ChannelFinderClient(BaseURL = cfsurl, username='boss', password='1234')
    ch = cf.find(name='SR*')
    for c in ch:
        print c.name,
        
if __name__ == "__main__":
    #out = 'cfa.txt'
    #dump_hla_cfa(out)
    import_tracy_va_table("nsls2srid_prop.csv")
    import_cfa_table(sys.argv[1])

    if len(sys.argv) > 1 and os.path.exists(sys.argv[1]):
        #initialize_cfs(sys.argv[1])
        #update_cfs(sys.argv[1])
        pass
    #test()
    
