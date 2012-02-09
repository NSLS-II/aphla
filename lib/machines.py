#!/usr/bin/env python

"""
Machines
~~~~~~~~

The initialization of machines
"""

from __future__ import print_function, unicode_literals

import os, re
import numpy as np

from catools import caget, caput
from lattice import Lattice
from element import CaElement, merge
from twiss import Twiss, TwissItem
from fnmatch import fnmatch
from ormdata import OrmData
from orm import Orm
from chanfinder import ChannelFinderAgent

from . import conf

from pkg_resources import resource_string, resource_exists, resource_filename

import logging
logger = logging.getLogger(__name__)

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
HLA_VBPM   = 'HLA:BPM'
HLA_VBPMX  = 'HLA:BPMX'
HLA_VBPMY  = 'HLA:BPMY'

HLA_DATA_DIRS = os.environ.get('HLA_DATA_DIRS', None)
HLA_MACHINE   = os.environ.get('HLA_MACHINE', None)
HLA_DEBUG     = int(os.environ.get('HLA_DEBUG', 0))

# map CaElement init parameters to CF properties
HLA_CFS_KEYMAP = {'name': u'elemName',
                  'field': u'elemField',
                  'devname': u'devName',
                  'family': u'elemType',
                  'girder': u'girder',
                  'length': u'length',
                  'index': u'ordinal',
                  'symmetry': u'symmetry',
                  'se': u'sEnd',
                  'system': u'system',
                  'cell': u'cell',
                  'phylen': None,
                  'sequence': None}


def createLattice(pvrec, systag):
    """
    create a lattice from channel finder agent data
    """

    # a new lattice
    lat = Lattice('channelfinder')
    for rec in pvrec:
        # skip if there's no properties.
        if rec[1] is None: continue
        if systag not in rec[2]: continue
        if 'name' not in rec[1]: continue
        pv = rec[0]
        prpt = rec[1]
        prpt['sb'] = float(prpt.get('se', 0)) - float(prpt.get('length', 0))
        name = prpt.get('name', None)

        #if name == 'CXHG2C30A': print(pv, prpt, rec[2])

        # find if the element exists.
        elem = lat._find_element(name=name)
        if elem is None:
            elem = CaElement(**prpt)
            #lat.appendElement(elem)
            lat.insertElement(elem)

        elem.updatePvRecord(pv, prpt, rec[2])

    # group info is a redundant info, needs rebuild based on each element
    lat.buildGroups()
    # !IMPORTANT! since Channel finder has no order, but lat class has
    lat.sortElements()
    lat.circumference = lat[-1].se if lat.size() > 0 else 0.0
    
    if HLA_DEBUG > 0:
        print("# mode: %s" % lat.mode)
        print("# elements: %d" % lat.size())
    if HLA_DEBUG > 1:
        for g in sorted(lat._group.keys()):
            print("# %10s: %d" % (g, len(lat._group[g])))
            
    return lat


def initNSLS2VSR():
    """
    initialize the virtual accelerator from channel finder
    """
    ORBIT_WAIT=8
    NETWORK_DOWN=False

    cfa = ChannelFinderAgent()
    src_home_csv = os.path.join(os.environ['HOME'], '.hla', 'nsls2.csv')
    HLA_CFS_URL = os.environ.get('HLA_CFS_URL', None)

    if os.path.exists(src_home_csv):
        logger.info("using home csv %s" % src_home_csv)
        cfa.importCsv(src_home_csv)
    elif conf.has('nsls2.csv'):
        #print("Using %s" % conf.filename('nsls2.csv'))
        src_pkg_csv = conf.filename('nsls2.csv')
        logger.info("using system csv %s" % src_pkg_csv)
        cfa.importCsv(src_pkg_csv)
    elif os.environ.get('HLA_CFS_URL', None):
        logger.info("using cfs %s" % HLA_CFS_URL)
        cfa.downloadCfs(HLA_CFS_URL, tagName='aphla.sys.*')
    else:
        raise RuntimeError("Failed at loading cache file")

    for k in [('name', u'elemName'), 
              ('field', u'elemField'), 
              ('devname', u'devName'),
              ('family', u'elemType'), 
              ('index', u'ordinal'), 
              ('se', u'sEnd'),
              ('system', u'system')]:
        cfa.renameProperty(k[1], k[0])
    #lat = createLattice(cfa.rows, 'aphla.sys.SR')

    tags = cfa.tags('aphla.sys.*')
    #print("Known Systems:", tags)
    #print(cfa.rows)

    global _lat, _lattice_dict

    for latname in ['SR', 'LTB', 'LTD1', 'LTD2']:
        #print("\nsys=", latname)
        _lattice_dict[latname] = createLattice(cfa.rows, 'aphla.sys.' + latname)

    print("Using ORM:", conf.filename('orm.hdf5'))
    _lattice_dict['SR'].ormdata = OrmData(conf.filename('orm.hdf5'))

    # a virtual bpm. its field is a "merge" of all bpms.
    bpms = _lattice_dict['SR'].getElements('BPM')
    allbpm = merge(bpms, **{'virtual': 1, 'name': HLA_VBPM})
    _lattice_dict['SR'].insertElement(allbpm)

    #
    # LTB 
    _lattice_dict['LTB'].loop = False
    #_lat = _lattice_dict['LTB']

    #
    # SR
    _lattice_dict['SR'].loop = True
    _lat = _lattice_dict['SR']


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

    print(__file__, "Reading twiss items:", len(s), len(betax))

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

def saveCache():
    """
    save current lattice to cache file
    """
    output = open(os.path.join(HLA_DATA_DIRS, HLA_MACHINE,'hla_cache.pkl'), 'w')
    import pickle
    #import cPickle as pickle
    pickle.dump(_lattice_dict, output)
    pickle.dump(_lat, output)
    pickle.dump(_orm, output)
    output.close()

def loadCache():
    inp_file = os.path.join(HLA_DATA_DIRS, HLA_MACHINE,'hla_cache.pkl')
    if not os.path.exists(inp_file):
        return False
    inp = open(inp_file, 'r')
    global _lat, _lattice_dict, _orm
    import pickle
    #import cPickle as pickle
    _lattice_dict = pickle.load(inp)
    _lat = pickle.load(inp)
    _orm = pickle.load(inp)
    inp.close()
    return True

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
