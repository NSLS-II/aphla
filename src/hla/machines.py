#!/usr/bin/env python

"""
Machines
~~~~~~~~

The initialization of machines
"""

import os, re
import numpy as np

from catools import caget, caput
from lattice import Element, Lattice
from twiss import Twiss, TwissItem
from fnmatch import fnmatch
from ormdata import OrmData

_lat = None
_lattice_dict = {}
_twiss = None

_orm = {}

#
HLA_TAG_EGET = 'aphla.eget'
HLA_TAG_EPUT = 'aphla.eput'
HLA_TAG_X    = 'aphla.x'
HLA_TAG_Y    = 'aphla.y'
HLA_TAG_SYS_PREFIX = 'aphla.sys.'

#
HLA_VFAMILY = 'HLA:VFAMILY'
HLA_VBPMX  = 'HLA:BPMX'
HLA_VBPMY  = 'HLA:BPMY'

HLA_DATA_DIRS = os.environ.get('HLA_DATA_DIRS', None)
HLA_MACHINE   = os.environ.get('HLA_MACHINE', None)
HLA_CFS_URL   = os.environ.get('HLA_CFS_URL', '')
HLA_DEBUG     = int(os.environ.get('HLA_DEBUG', 0))

# map Element init parameters to CF properties
HLA_CFS_KEYMAP = {'name': u'elemName',
                  'field': u'elemField',
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


def createLatticeFromCf(cfsurl, **kwargs):
    """
    create a lattice from channel finder
    
    - *cfsurl* the URL of channel finder service
    - *tagName*
    """
    from channelfinder import ChannelFinderClient, Channel, Property, Tag

    # reverse map, skip the None values
    CFS_MAP = dict((v,k) for k,v in HLA_CFS_KEYMAP.iteritems() if v)

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
            elem = Element(eget=caget, eput=caput, **prpt)
            lat.appendElement(elem)
        else:
            #print prpt
            elem.updateCfsProperties(pv, prpt)

        # update element with new
        tags = c.getTags()
        elem.updateCfsTags(pv, tags)
        if HLA_TAG_EGET in tags: elem.addEGet(pv)
        if HLA_TAG_EPUT in tags: elem.addEPut(pv)

        elem.appendStatusPv(pv, prpt['handle'])

        #if not HLA_TAG_EPUT in tags and not HLA_TAG_EGET in tags:
        #elem.appendStatusPv((caget, pv, prpt['handle']))
        #print name, ""
        if prpt.has_key('field'):
            if not prpt.has_key('handle'):
                pass
            elif prpt['handle'].upper() == 'READBACK':
                elem.setFieldGetAction(prpt['field'], pv, prpt['handle'])
                if HLA_TAG_EPUT in tags:
                    print "'%s': %s and READBACK ? could be a bug" % (
                        pv, HLA_TAG_EPUT)
            elif prpt['handle'].upper() == 'SETPOINT':
                elem.setFieldPutAction(prpt['field'], pv, prpt['handle'])
                if HLA_TAG_EGET in tags:
                    print "'%s': %s and SETPOINT ? could be a bug" % (
                        pv, HLA_TAG_EGET)
            # debug
        # check
        if prpt.has_key('handle'):
            if prpt['handle'].upper() == 'READBACK' and HLA_TAG_EPUT in tags:
                print "'%s': %s and READBACK ? could be a bug" % (
                        pv, HLA_TAG_EPUT)
            elif prpt['handle'].upper() == 'SETPOINT' and HLA_TAG_EGET in tags:
                print "'%s': %s and SETPOINT ? could be a bug" % (
                        pv, HLA_TAG_EGET)

    # group info is a redundant info, needs rebuild based on each element
    lat.buildGroups()
    # !IMPORTANT! since Channel finder has no order, but lat class has
    lat.sortElements()
    lat.circumference = lat[-1].se

    if HLA_DEBUG > 0:
        print "# mode: %s" % lat.mode 
        print "# elements: %d" % lat.size()
    if HLA_DEBUG > 1:
        for g in sorted(lat._group.keys()):
            print "# %10s: %d" % (g, len(lat._group[g]))
            
    return lat


def initNSLS2VSR():
    """
    initialize the virtual accelerator from channel finder
    """
    # are we using virtual ac
    VIRTAC = True
    #print "= initializing NSLS2 VSR"
    INF = 1e30
    ORBIT_WAIT=8
    NETWORK_DOWN=False

    TAG_DEFAULT_GET='aphla.eget'
    TAG_DEFAULT_PUT='aphla.eput'

    from channelfinder import ChannelFinderClient, Channel, Property, Tag

    cf = ChannelFinderClient(HLA_CFS_URL)
    alltags = [t.Name for t in cf.getAllTags()]
    #print alltags

    if HLA_DEBUG > 0:
        print "# channel finder: %s" % HLA_CFS_URL

    global _lat, _lattice_dict

    for tag in alltags:
        if not tag.startswith(HLA_TAG_SYS_PREFIX): continue
        latsys = tag[len(HLA_TAG_SYS_PREFIX):]
        if latsys:
            if HLA_DEBUG > 0: print "Creating '%s'" % latsys
            _lattice_dict[latsys] = createLatticeFromCf(
                HLA_CFS_URL, **{'tagName': tag})
            _lattice_dict[latsys].mode = tag
    
    #
    # LTB 
    _lattice_dict['LTB'].loop = False
    #_lat = _lattice_dict['LTB']

    # create virtual element BPMX and BPMY
    bpmx = Element(eget=caget, eput=caput,
                   **{'name':HLA_VBPMX, 'family': HLA_VFAMILY})
    bpmx.sb = []
    bpmy = Element(eget=caget, eput=caput,
                   **{'name':HLA_VBPMY, 'family': HLA_VFAMILY})
    bpmy.sb = []
    for e in _lattice_dict['LTB'].getElements('BPM'):
        for pv,t in e._pvtags.items():
            if 'aphla.x' in t:
                bpmx.addEGet(pv)
                bpmx.sb.append(e.sb)
            if 'aphla.y' in t:
                bpmy.addEGet(pv)
                bpmy.sb.append(e.sb)
    bpmx.virtual, bpmy.virtual = 1, 1
    _lattice_dict['LTB'].appendElement(bpmx)
    _lattice_dict['LTB'].appendElement(bpmy)

    #
    # SR
    _lattice_dict['SR'].loop = True

    bpmx = Element(eget=caget, eput=caput,
                   **{'name': HLA_VBPMX, 'family': HLA_VFAMILY})
    bpmx.sb = []
    bpmy = Element(eget=caget, eput=caput,
                   **{'name': HLA_VBPMY, 'family': HLA_VFAMILY})
    bpmy.sb = []
    for e in _lattice_dict['SR'].getElements('BPM'):
        for pv,t in e._pvtags.items():
            if 'aphla.x' in t and HLA_TAG_EGET in t:
                bpmx.addEGet(pv)
                bpmx.sb.append(e.sb)
            if 'aphla.y' in t and HLA_TAG_EGET in t:
                bpmy.addEGet(pv)
                bpmy.sb.append(e.sb)
    bpmx.virtual, bpmy.virtual = 1, 1
    _lattice_dict['SR'].appendElement(bpmx)
    _lattice_dict['SR'].appendElement(bpmy)
    _lattice_dict['SR'].orm = OrmData(
        os.path.join(HLA_DATA_DIRS, HLA_MACHINE,'orm.pkl'))

    _lat = _lattice_dict['SR']

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

def createLatticesFromTxt(f, **kwargs):
    # reverse map, skip the None values
    CFS_MAP = dict((v,k) for k,v in HLA_CFS_KEYMAP.iteritems() if v)
    lat_dict = {}
    for cl in open(f, 'r').readlines():
        # skip the comment lines
        if not cl.strip() or cl.strip().startswith('#'): continue
        # prepare the pv,properties,tags
        try:
            rawpv, rawprpt, rawtag = [r.strip() for r in cl.split(';')]
        except:
            print cl
            print [r.strip() for r in cl.split(';')]
            raise

        if not rawprpt.strip(): continue
        pv = rawpv.strip()
        prpt0 = dict([re.split(r'\s*=\s*', k) for k in 
                      re.split(r'\s*,\s*', rawprpt) if len(k.split('=')) > 1])
        prpt = dict((CFS_MAP[k], v) for k,v in prpt0.iteritems())
        prpt['sb'] = float(prpt['se']) - float(prpt['length'])

        #print pv,prpt
        name = prpt.get('name', None)
        if not name: continue
        #print pv, name

        tags = set(re.split(r'\s*,\s*', rawtag.strip()))

        for tag in tags:
            if not tag.startswith(HLA_TAG_SYS_PREFIX): continue
            latname = tag[len(HLA_TAG_SYS_PREFIX):] + '-txt'
            if not latname: continue
            if not lat_dict.has_key(latname):
                print "Creating lattice layout: '%s'" % latname
                lat_dict[latname] = Lattice('txt')

            lat = lat_dict[latname]
            elem = lat._find_element(name=name)
        
            if not elem:
                #print pv, prpt
                elem = Element(eget=caget, eput=caput, **prpt)
                lat.appendElement(elem)
            else:
                elem.updateCfsProperties(pv, prpt)
            # update element with new
            elem.updateCfsTags(pv, tags)
            if HLA_TAG_EGET in tags: elem.addEGet(pv)
            if HLA_TAG_EPUT in tags: elem.addEPut(pv)

            elem.appendStatusPv(pv, prpt['handle'])

            #if not HLA_TAG_EPUT in tags and not HLA_TAG_EGET in tags:
            #elem.appendStatusPv((caget, pv, prpt['handle']))
            #print name, ""
            if prpt.has_key('field'):
                if not prpt.has_key('handle'):
                    pass
                elif prpt['handle'].upper() == 'READBACK':
                    elem.setFieldGetAction(prpt['field'], pv, prpt['handle'])
                elif prpt['handle'].upper() == 'SETPOINT':
                    elem.setFieldPutAction(prpt['field'], pv, prpt['handle'])

    for k, lat in lat_dict.items():
        # group info is a redundant info, needs rebuild based on each element
        lat.buildGroups()
        #lat.mergeGroups(u"BPM", [u'BPMX', u'BPMY'])
        # !IMPORTANT! since Channel finder has no order, but lat class has
        lat.sortElements()
        #print __file__, lat._group['BPMX']
        lat.circumference = lat[-1].se
    
    return lat_dict
    
def initNSLS2VSRTxt(data = ''):
    # are we using virtual ac
    VIRTAC = True
    #print "= initializing NSLS2 VSR Txt"

    INF = 1e30
    ORBIT_WAIT=8
    NETWORK_DOWN=False

    if data:
        cfsurl = data
    else:
        cfsurl = os.path.join(HLA_DATA_DIRS, 
                              HLA_MACHINE, 'channel_finder_server.txt')

    global _lat, _lattice_dict
    _lattice_dict.update(createLatticesFromTxt(cfsurl))

    _lattice_dict['LTB-txt'].mode = 'LTB-txt'
    _lattice_dict['LTB-txt'].loop = False

    bpmx = Element(eget=caget, eput=caput, **{'name': HLA_VBPMX, 'family': HLA_VFAMILY})
    bpmx.sb = []                                 
    bpmy = Element(eget=caget, eput=caput, **{'name': HLA_VBPMY, 'family': HLA_VFAMILY})
    bpmy.sb = []
    for e in _lattice_dict['LTB-txt'].getElements('BPM'):
        for pv,t in e._pvtags.items(): 
            if 'aphla.x' in t and HLA_TAG_EGET in t:
                bpmx.addEGet(pv)
                bpmx.sb.append(e.sb)  
            if 'aphla.y' in t and HLA_TAG_EGET in t:
                bpmy.addEGet(pv)
                bpmy.sb.append(e.sb)
    bpmx.virtual, bpmy.virtual = 1, 1
    _lattice_dict['LTB-txt'].appendElement(bpmx)
    _lattice_dict['LTB-txt'].appendElement(bpmy)


    _lattice_dict['SR-txt'].mode = 'SR-text-ver'
    _lattice_dict['SR-txt'].loop = True

    # create virtual bpms
    bpmx = Element(eget=caget, eput=caput, **{'name': HLA_VBPMX, 'family': HLA_VFAMILY})
    bpmx.sb = []                                 
    bpmy = Element(eget=caget, eput=caput, **{'name': HLA_VBPMY, 'family': HLA_VFAMILY})
    bpmy.sb = []
    for e in _lattice_dict['SR-txt'].getElements('BPM'):
        for pv,t in e._pvtags.items(): 
            if 'aphla.x' in t and HLA_TAG_EGET in t:
                bpmx.addEGet(pv)
                bpmx.sb.append(e.sb)  
            if 'aphla.y' in t and HLA_TAG_EGET in t:
                bpmy.addEGet(pv)
                bpmy.sb.append(e.sb)
    bpmx.virtual, bpmy.virtual = 1, 1
    _lattice_dict['SR-txt'].appendElement(bpmx)
    _lattice_dict['SR-txt'].appendElement(bpmy)
    _lattice_dict['SR-txt'].orm = OrmData(
        os.path.join(HLA_DATA_DIRS, HLA_MACHINE,'orm.pkl'))


    _lat = _lattice_dict['SR-txt']
    #for k,v in _lattice_dict.iteritems(): print k, v.mode

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

def initNSLS2VSRTwiss():
    """
    Only works from virtac.nsls2.bnl.gov
    """
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

    N = len(s)

    print __file__, "Reading twiss items:", len(s), len(betax)

    # fix the Tracy convension by adding a new element at the end
    for x in [s, alphax, alphay, betax, betay, etax, etay, orbx, orby,
              phix, phiy]:
        x.append(x[-1])
    
    global _twiss, _lat
    _twiss = Twiss('virtac')

    _twiss.tune = (nux, nuy)
    #print __file__, len(s), len(betax)
    
    nps = np.array(s, 'd')
    for ielem in range(_lat.size()):
        elem = _lat._elements[ielem]
        if elem.family == HLA_VFAMILY: continue

        i = np.argmin(np.abs(nps - elem.sb))

        gammax = (1 + alphax[i]**2)/betax[i]
        gammay = (1 + alphay[i]**2)/betay[i]
        tw = TwissItem(s = s[i], alpha=(alphax[i], alphay[i]),
                       beta=(betax[i], betay[i]),
                       gamma=(gammax, gammay),
                       eta=(etax[i], etay[i]),
                       phi=(phix[i], phiy[i]))

        _twiss._elements.append(elem.name)
        _twiss.append(tw)

def use(lattice):
    """
    switch to a lattice

    use :func:`~hla.machines.lattices` to get a dict of lattices and its mode
    name

    When switching lattice, twiss data is not sychronized.
    """
    global _lat, _lattice_dict
    if _lattice_dict.get(lattice, None):
        _lat = _lattice_dict[lattice]
    else:
        raise ValueError("no lattice %s was defined" % lattice)

def getLattice(lat):
    """
    return a :class:`~hla.lattice.Lattice` object with given name.

    .. seealso:: :func:`~hla.machines.lattices`
    """
    global _lattice_dict
    #for k, v in _lattice_dict.items():
    #    print k, v.mode
    return _lattice_dict.get(lat, None)

def lattices():
    """
    get a dictionary of lattice name and mode

    Example::

      >>> lattices()
      { 'LTB': 'channelfinder-LTB', 'LTB-txt': 'channelfinder-txt',
      'SR': 'channelfinder-SR', 'SR-txt': 'channelfinder-txt' }
      >>> use('LTB-txt')
    """
    return dict((k, v.mode) for k,v in _lattice_dict.iteritems())
