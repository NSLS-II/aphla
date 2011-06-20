#!/usr/bin/env python

"""
The initialization of machines
"""

import os, re

from catools import caget, caput
from lattice import Element, Lattice
from twiss import Twiss, TwissItem
from fnmatch import fnmatch

_lat = None
_lattice_dict = {}
_twiss = None

TAG_DEFAULT_GET = 'aphla.eget'
TAG_DEFAULT_PUT = 'aphla.eput'

HLA_DATA_DIRS=os.environ.get('HLA_DATA_DIRS', None)
HLA_MACHINE=os.environ.get('HLA_MACHINE', None)
HLA_CFS_URL= os.environ.get('HLA_CFS_URL', '')

def createLatticeFromCf(cfsurl, **kwargs):
    """
    create a lattice from channel finder
    
    - *cfsurl* the URL of channel finder service
    - *tagName*
    """
    from channelfinder.core.ChannelFinderClient import ChannelFinderClient
    from channelfinder.core.Channel import Channel, Property, Tag

    # map Element init parameters to CF properties
    ELEMENT_CFS_MAP = {'name': u'elemName',
                       'devname': u'devName',
                       'family': u'elemType',
                       'girder': u'girder',
                       'handle': u'handle',
                       'length': u'length',
                       'index': u'ordinal',
                       'symmetry': u'symmetry',
                       'se': u'sEnd',
                       'system': u'system',
                       'cell': u'cell',
                       'phylen': None,
                       'sequence': None}
    # reverse map, skip the None values
    CFS_MAP = dict((v,k) for k,v in ELEMENT_CFS_MAP.iteritems() if v)

    lat = Lattice('channelfinder')
    cf = ChannelFinderClient(BaseURL = cfsurl)
    ch = cf.find(**kwargs)
    for c in ch:
        if not c.getProperties(): continue
        pv = c.Name
        prpt = dict((CFS_MAP[k], v) \
                        for k,v in c.getProperties().iteritems() \
                        if CFS_MAP.has_key(k))
        prpt['sb'] = float(prpt.get('se', 0)) - float(prpt.get('length', 0))
        name = prpt.get('name', None)
        # skip if this pv has no element name
        if not name: continue
        #print pv, name, prpt

        elem = lat._find_element(name=name)
        if not elem:
            #print prpt
            elem = Element(**prpt)
            lat.appendElement(elem)
        else:
            #print prpt
            elem.updateCfsProperties(pv, prpt)
        # update element with new
        tags = c.getTags()
        elem.updateCfsTags(pv, tags)
        if 'aphla.eget' in tags:
            elem.appendEget((caget, pv, prpt['handle']))
        if 'aphla.eput' in tags:
            elem.appendEput((caput, pv, prpt['handle']))
        if not 'aphla.eput' in tags and not 'aphla.eget' in tags:
            elem.appendStatusPv((caget, pv, prpt['handle']))
        #print name, ""

    # group info is a redundant info, needs rebuild based on each element
    lat.buildGroups()
    lat.mergeGroups(u"BPM", [u'BPMX', u'BPMY'])
    # !IMPORTANT! since Channel finder has no order, but lat class has
    lat.sortElements()
    #print __file__, lat._group['BPMX']
    lat.circumference = lat[-1].se

    # create virtual hla elements
    bpmx = lat.getElements(u'BPMX')
    bpmy = lat.getElements(u'BPMY')
    nbpmx, nbpmy = len(bpmx), len(bpmy)
    elemxpv, elemypv = ['']*nbpmx, [''] * nbpmy
    ch = cf.find(**kwargs)
    for c in ch:
        #print c.Name, c.getTags()
        tags = c.getTags()
        prpt = c.getProperties()
        if not u'aphla.eget' in tags: continue
        if not prpt.has_key('ELEM_TYPE'): continue
        if not prpt['ELEM_TYPE'].startswith(u'BPM'): continue
        elemname = c.getProperties().get('ELEM_NAME', None)
        idx = [i for i,x in enumerate(bpmx) if x.name == elemname]
        #print __file__, elemname, idx, len(bpmx)
        if u'aphla.x' in tags:
            elemxpv[idx[0]] = c.Name
        if u'aphla.y' in tags:
            elemypv[idx[0]] = c.Name

    # create two virtual elements, HLA:BPMX/Y
    elem = Element(name='HLA:BPMX')
    for i in range(nbpmx):
        elem.appendEget((caget, elemxpv[i], bpmx[i]))
    lat.insertElement(0, elem)

    elem = Element(name='HLA:BPMY')
    for i in range(nbpmy):
        elem.appendEget((caget, elemypv[i], bpmy[i]))
    lat.insertElement(1, elem)
    return lat

def init(site, system):
    pass

def initNSLS2VSR():
    # are we using virtual ac
    VIRTAC = True
    os.environ['EPICS_CA_ADDR_LIST'] = 'virtac.nsls2.bnl.gov'
    os.environ['EPICS_cA_MAX_ARRAY_BYTES'] = '100000'

    INF = 1e30
    ORBIT_WAIT=8
    NETWORK_DOWN=False

    TAG_DEFAULT_GET='aphla.eget'
    TAG_DEFAULT_PUT='aphla.eput'

    #HLA_CFS_URL = 'http://channelfinder.nsls2.bnl.gov:8080/ChannelFinder'
    #HLA_CFS_URL = 'http://web01.nsls2.bnl.gov:8080/ChannelFinder'
    cfsurl = os.environ.get('HLA_CFS_URL', '')
    args = {'name': 'SR:*', 'tagName': 'aphla.*'}

    global _lat, _lattice_dict
    _lattice_dict['ltb'] = createLatticeFromCf(
        cfsurl, **{'name':'LTB:*', 'tagName': 'aphla.*'})
    #_lat = _lattice_dict['ltb']
    _lattice_dict['sr'] = createLatticeFromCf(
        cfsurl, **{'name':'SR:*', 'tagName': 'aphla.*'})
    _lat = _lattice_dict['sr']

    # self diagnostics
    # check dipole numbers
    bend = _lat.getElements(u'B1G3C14A')
    #print bend
    bend = _lat.getElements(u'DIPOLE')
    #print __file__, _lat._group[u'DIPOLE']
    if len(bend) != 60:
        #print bend
        raise ValueError("dipole number is not 60 (%d)" % len(bend))
    #print _lat.getElements('BPMX')

def createLatticeFromTxt(f, **kwargs):
    pvname = kwargs.get('name', '*')
    tagName = kwargs.get('tagName', '*') 
    lat = Lattice('channelfinder-txt')

    # map Element init parameters to CF properties
    ELEMENT_CFS_MAP = {'name': u'elemName',
                       'devname': u'devName',
                       'family': u'elemType',
                       'girder': u'girder',
                       'handle': u'handle',
                       'length': u'length',
                       'index': u'ordinal',
                       'symmetry': u'symmetry',
                       'se': u'sEnd',
                       'system': u'system',
                       'cell': u'cell',
                       'phylen': None,
                       'sequence': None}
    # reverse map, skip the None values
    CFS_MAP = dict((v,k) for k,v in ELEMENT_CFS_MAP.iteritems() if v)

    for cl in open(f, 'r').readlines():
        # skip the comment lines
        if cl.strip().startswith('#'): continue
        # prepare the pv,properties,tags
        rawpv, rawprpt, rawtag = [r.strip() for r in cl.split(';')]
        if not rawprpt.strip(): continue
        pv = rawpv.strip()
        prpt0 = dict([re.split(r'\s*=\s*', k) for k in 
                      re.split(r'\s*,\s*', rawprpt) if len(k.split('=')) > 1])
        prpt = dict((CFS_MAP[k], v) for k,v in prpt0.iteritems())
        prpt['sb'] = float(prpt['se']) - float(prpt['length'])
        tags = set(re.split(r'\s*,\s*', rawtag))
        
        # match against pvname and tag
        if not fnmatch(name=rawpv.strip(), pat=pvname):
            #print "No pv matches", rawpv, pvname
            continue
        mtags = [tag for tag in tags if fnmatch(name=tag, pat=tagName)]
        if not mtags:
            #print "No tags, skipping element: %s " % pv
            continue
        
        #print pv,prpt
        name = prpt.get('name', None)
        if not name: continue
        #print pv, name
        elem = lat._find_element(name=name)
        
        if not elem:
            #print pv, prpt
            elem = Element(**prpt)
            lat.appendElement(elem)
        else:
            elem.updateCfsProperties(pv, prpt)
        # update element with new
        elem.updateCfsTags(pv, tags)
        if 'aphla.eget' in tags:
            #print pv, tags
            elem.appendEget((caget, pv, prpt['handle']))
        if 'aphla.eput' in tags:
            elem.appendEput((caput, pv, prpt['handle']))
        if not 'aphla.eput' in tags and not 'hla.eget' in tags:
            elem.appendStatusPv((caget, pv, prpt['handle']))
        #print name, ""

    # group info is a redundant info, needs rebuild based on each element
    lat.buildGroups()
    lat.mergeGroups(u"BPM", [u'BPMX', u'BPMY'])
    # !IMPORTANT! since Channel finder has no order, but lat class has
    lat.sortElements()
    #print __file__, lat._group['BPMX']
    
    return lat
    
def initNSLS2VSRTxt(data = ''):
    # are we using virtual ac
    VIRTAC = True
    os.environ['EPICS_CA_ADDR_LIST'] = 'virtac.nsls2.bnl.gov'
    os.environ['EPICS_cA_MAX_ARRAY_BYTES'] = '100000'

    INF = 1e30
    ORBIT_WAIT=8
    NETWORK_DOWN=False

    TAG_DEFAULT_GET='aphla.eget'
    TAG_DEFAULT_PUT='aphla.eput'

    if data:
        cfsurl = data
    else:
        cfsurl = os.path.join(HLA_DATA_DIRS, 'machine', 
                              HLA_MACHINE, 'channel_finder_server.txt')

    global _lat, _lattice_dict
    _lattice_dict['ltb'] = createLatticeFromTxt(
        cfsurl, **{'name':'LTB:*', 'tagName': 'aphla.*'})
    _lattice_dict['sr'] = createLatticeFromTxt(
        cfsurl, **{'name':'SR:*', 'tagName': 'aphla.*'})
    _lat = _lattice_dict['sr']

    # self diagnostics
    # check dipole numbers
    bend = _lat.getElements(u'B1G3C14A')
    #print bend
    bend = _lat.getElements(u'DIPOLE')
    #print __file__, _lat._group[u'DIPOLE']
    if len(bend) != 60:
        #print bend
        raise ValueError("dipole number is not 60 (%d)" % len(bend))
    #print _lat.getElements('BPMX')
    _lat.circumference = _lat[-1].sb + _lat[-1].length

def initNSLS2VSRTwiss():
    """Only works from virtac.nsls2.bnl.gov"""
    # s location
    s      = [float(v) for v in caget('SR:C00-Glb:G00{POS:00}RB-S', timeout=30)]
    # twiss at s_end (from Tracy)
    alphax = [v for v in caget('SR:C00-Glb:G00{ALPHA:00}RB-X')]
    alphay = [v for v in caget('SR:C00-Glb:G00{ALPHA:00}RB-Y')]
    betax  = [v for v in caget('SR:C00-Glb:G00{BETA:00}RB-X')]
    betay  = [v for v in caget('SR:C00-Glb:G00{BETA:00}RB-Y')]
    etax   = [v for v in caget('SR:C00-Glb:G00{ETA:00}RB-X')]
    etay   = [v for v in caget('SR:C00-Glb:G00{ETA:00}RB-Y')]
    orbx   = [v for v in caget('SR:C00-Glb:G00{ORBIT:00}RB-X')]
    orby   = [v for v in caget('SR:C00-Glb:G00{ORBIT:00}RB-Y')]
    phix   = [v for v in caget('SR:C00-Glb:G00{PHI:00}RB-X')]
    phiy   = [v for v in caget('SR:C00-Glb:G00{PHI:00}RB-Y')]
    nux = caget('SR:C00-Glb:G00{TUNE:00}RB-X')
    nuy = caget('SR:C00-Glb:G00{TUNE:00}RB-Y')

    #print __file__, len(s), len(betax)

    # fix the Tracy bug by adding a new element at the end
    for x in [s, alphax, alphay, betax, betay, etax, etay, orbx, orby,
              phix, phiy]:
        x.append(x[-1])
    
    global _twiss, _lat
    _twiss = Twiss('virtac')

    _twiss.tune = (nux, nuy)
    #print __file__, len(s), len(betax)
    for i in range(len(s)):
        gammax = (1 + alphax[i]**2)/betax[i]
        gammay = (1 + alphay[i]**2)/betay[i]
        tw = TwissItem(s = s[i], alpha=(alphax[i], alphay[i]),
                       beta=(betax[i], betay[i]),
                       gamma=(gammax, gammay),
                       eta=(etax[i], etay[i]),
                       phi=(phix[i], phiy[i]))
        elem = _lat.getLine((s[i], s[i]), eps=1e-6)
        if not elem:
            #print "not found at: (%d) %f" % (i, s[i])
            continue
        elif isinstance(elem, list):
            #print "Overlap:\n  ",
            #for e in elem: print e.name, 
            #print ""
            _twiss._elements.append(elem[0].name)
        else:
            #print "Found ", s[i], elem.name
            _twiss._elements.append(elem.name)
        #print _twiss[-1]
        _twiss.append(tw)

def use(lattice):
    global _lat, _lattice_dict
    if _lattice_dict.get(lattice, None):
        _lat = _lattice_dict[lattice]
    else:
        raise ValueError("no lattice %s was defined" % lattice)
