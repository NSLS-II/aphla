#!/usr/bin/env python

"""
The initialization of machines
"""

import os

from catools import caget, caput
from lattice import Element, Lattice

_lat = None
_lattice_dict = {}
TAG_DEFAULT_GET = 'HLA.EGET'
TAG_DEFAULT_PUT = 'HLA.EPUT'

HLA_DATA_DIRS=os.environ.get('HLA_DATA_DIRS', None)
HLA_MACHINE=os.environ.get('HLA_MACHINE', None)
HLA_CFS_URL= ''

def createLatticeFromCf(cfsurl, **kwargs):
    """
    create a lattice from channel finder
    
    - *cfsurl* the URL of channel finder service
    - *tagName*
    """
    from channelfinder.core.ChannelFinderClient import ChannelFinderClient
    from channelfinder.core.Channel import Channel, Property, Tag

    lat = Lattice('channelfinder')
    cf = ChannelFinderClient(BaseURL = cfsurl)
    ch = cf.find(**kwargs)
    for c in ch:
        pv = c.Name
        prpt = c.getProperties()
        if not prpt or not prpt.has_key('ELEM_NAME'):
            continue
        name = prpt['ELEM_NAME']
        elem = lat._find_element(name=name)
        if not elem:
            elem = Element(cfs=prpt)
            lat.appendElement(elem)
        else:
            elem.updateCfsProperties(pv, prpt)
        # update element with new
        tags = c.getTags()
        elem.updateCfsTags(pv, tags)
        if 'HLA.EGET' in tags:
            elem.appendEget((caget, pv, prpt['HANDLE']))
        if 'HLA.EPUT' in tags:
            elem.appendEput((caput, pv, prpt['HANDLE']))
        if not 'HLA.EPUT' in tags and not 'HLA.EGET' in tags:
            elem.appendStatusPv((caget, pv, prpt['HANDLE']))
        #print name, ""

    # group info is a redundant info, needs rebuild based on each element
    lat.buildGroups()
    lat.mergeGroups(u"BPM", [u'BPMX', u'BPMY'])
    # !IMPORTANT! since Channel finder has no order, but lat class has
    lat.sortElements()
    #print __file__, lat._group['BPMX']
    
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
        if not u'HLA.EGET' in tags: continue
        if not prpt.has_key('ELEM_TYPE'): continue
        if not prpt['ELEM_TYPE'].startswith(u'BPM'): continue
        elemname = c.getProperties().get('ELEM_NAME', None)
        idx = [i for i,x in enumerate(bpmx) if x.name == elemname]
        #print __file__, elemname, idx, len(bpmx)
        if u'HLA.X' in tags:
            elemxpv[idx[0]] = c.Name
        if u'HLA.Y' in tags:
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

    TAG_DEFAULT_GET='HLA.EGET'
    TAG_DEFAULT_PUT='HLA.EPUT'

    HLA_CFS_URL = 'http://channelfinder.nsls2.bnl.gov:8080/ChannelFinder'
    cfsurl = HLA_CFS_URL
    args = {'name': 'SR:*', 'tagName': 'HLA.*'}

    global _lat, _lattice_dict
    _lattice_dict['ltb'] = createLatticeFromCf(
        cfsurl, **{'name':'LTB:*', 'tagName': 'HLA.*'})
    _lattice_dict['sr'] = createLatticeFromCf(cfsurl, **args)
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


def use(lattice):
    global _lat, _lattice_dict
    if _lattice_dict.get(lattice, None):
        _lat = _lattice_dict[lattice]
    else:
        raise ValueError("no lattice %s was defined" % lattice)
