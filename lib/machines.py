#!/usr/bin/env python

"""
Machines
~~~~~~~~

:author: Lingyun Yang
:date: 2012-07-09 17:37

The initialization of machines.

Each facility can have its own initialization function.
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
HLA_TAG_PREFIX = 'aphla'
HLA_TAG_EGET = HLA_TAG_PREFIX + '.eget'
HLA_TAG_EPUT = HLA_TAG_PREFIX + '.eput'
HLA_TAG_X    = HLA_TAG_PREFIX + '.x'
HLA_TAG_Y    = HLA_TAG_PREFIX + '.y'
HLA_TAG_SYS_PREFIX = HLA_TAG_PREFIX + '.sys'

#
HLA_VFAMILY = 'HLA:VFAMILY'
HLA_VBPM   = 'HLA:VBPM'

HLA_DATA_DIRS = os.environ.get('HLA_DATA_DIRS', None)
HLA_MACHINE   = os.environ.get('HLA_MACHINE', None)
HLA_DEBUG     = int(os.environ.get('HLA_DEBUG', 0))

def createLattice(name, pvrec, systag, desc = 'channelfinder'):
    """
    create a lattice from channel finder data

    :param name: lattice name, e.g. 'SR', 'LTD'
    :param pvrec: list of pv records `(pv, property dict, list of tags)`
    :param systag: process records which has this systag. e.g. `aphla.sys.SR`
    :param desc: description is this lattice
    :return: :class:`~aphla.lattice.Lattice`
    """

    logger.debug("creating '%s':%s" % (name, desc))
    logger.debug("%d pvs found in '%s'" % (len(pvrec), name))
    # a new lattice
    lat = Lattice(name, desc)
    for rec in pvrec:
        #logger.debug("{0}".format(rec))
        # skip if there's no properties.
        if rec[1] is None: continue
        if systag not in rec[2]: continue
        if 'name' not in rec[1]: continue
        pv = rec[0]
        prpt = rec[1]
        prpt['sb'] = float(prpt.get('se', 0)) - float(prpt.get('length', 0))
        name = prpt.get('name', None)

        logger.debug("{0} {1} {2}".format(rec[0], rec[1], rec[2]))

        # find if the element exists.
        elem = lat._find_exact_element(name=name)
        if elem is None:
            try:
                elem = CaElement(**prpt)
            except:
                print("Error: creating element '{0}' with '{1}'".format(name, prpt))
                raise

            #lat.appendElement(elem)
            lat.insertElement(elem)

        elem.updatePvRecord(pv, prpt, rec[2])

    # group info is a redundant info, needs rebuild based on each element
    lat.buildGroups()
    # !IMPORTANT! since Channel finder has no order, but lat class has
    lat.sortElements()
    lat.circumference = lat[-1].se if lat.size() > 0 else 0.0
    
    logger.debug("mode {0}".format(lat.mode))
    logger.debug("'%s' has %d elements" % (lat.name, lat.size()))
    for g in sorted(lat._group.keys()):
        logger.debug("lattice '%s' group %s(%d)" % (
                lat.name, g, len(lat._group[g])))
        
    return lat


def initNSLS2V1(with_twiss = False):
    """ 
    initialize the virtual accelerator 'V1SR', 'V1LTD1', 'V1LTD2', 'V1LTB' from

    - `${HOME}/.hla/us_nsls2v1_cfs.csv`
    - channel finder in ${HLA_CFS_URL}
    - `us_nsls2v1_cfs.csv` with aphla package.
    """

    cfa = ChannelFinderAgent()
    cfs_filename = 'us_nsls2v1.db'
    src_home_csv = os.path.join(os.environ['HOME'], '.hla', cfs_filename)
    HLA_CFS_URL = os.environ.get('HLA_CFS_URL', None)

    if os.path.exists(src_home_csv):
        msg = "Creating lattice from home file '%s'" % src_home_csv
        logger.info(msg)
        if src_home_csv.endswith('.csv'): cfa.importCsv(src_home_csv)
        elif src_home_csv.endswith('.db'): cfa.importSqliteDb(src_home_csv)
    elif os.environ.get('HLA_CFS_URL', None):
        msg = "Creating lattice from channel finder '%s'" % HLA_CFS_URL
        logger.info(msg)
        cfa.downloadCfs(HLA_CFS_URL, tagName='aphla.sys.*')
    elif conf.has(cfs_filename):
        src_pkg_csv = conf.filename(cfs_filename)
        msg = "Creating lattice from '%s'" % src_pkg_csv
        logger.info(msg)
        #print(msg)
        if src_pkg_csv.endswith('.csv'): cfa.importCsv(src_pkg_csv)
        elif src_pkg_csv.endswith('.db'): cfa.importSqliteDb(src_pkg_csv)
    else:
        logger.error("Channel finder data are available, no '%s', no server" % 
                     cfs_filename)
        raise RuntimeError("Failed at loading cache file")

    #print(msg)
    # the property in Element mirrored from ChannelFinder property
    for k in [('name', u'elemName'), 
              ('field', u'elemField'), 
              ('devname', u'devName'),
              ('family', u'elemType'), 
              ('handle', u'elemHandle'),
              ('index', u'elemIndex'), 
              ('se', u'elemPosition'),
              ('system', u'system')]:
        cfa.renameProperty(k[1], k[0])

    #tags = cfa.tags('aphla.sys.*')

    global _lat, _lattice_dict

    # should be 'aphla.sys.' + ['VSR', 'VLTB', 'VLTD1', 'VLTD2']
    logger.info("Initializing lattice according to the tags: %s" % HLA_TAG_SYS_PREFIX)
    for latname in ['V1SR', 'V1LTB', 'V1LTD1', 'V1LTD2']:
        lattag = HLA_TAG_SYS_PREFIX + '.' + latname
        logger.info("Initializing lattice %s (%s)" % (latname, lattag))
        _lattice_dict[latname] = createLattice(latname, cfa.rows, lattag,
                                               desc = cfa.source)
        if _lattice_dict[latname].size() == 0:
            logger.warn("lattice '%s' has no elements" % latname)

    orm_filename = 'us_nsls2_v1sr_orm.hdf5'
    if orm_filename and conf.has(orm_filename):
        #print("Using ORM:", conf.filename(orm_filename))
        _lattice_dict['V1SR'].ormdata = OrmData(conf.filename(orm_filename))
    else:
        logger.warning("No ORM '%s' found" % orm_filename)

    # a virtual bpm. its field is a "merge" of all bpms.
    bpms = _lattice_dict['V1SR'].getElementList('BPM')
    allbpm = merge(bpms, **{'virtual': 1, 'name': HLA_VBPM, 
                            'family': HLA_VFAMILY})
    _lattice_dict['V1SR'].insertElement(allbpm, groups=[HLA_VFAMILY])

    # tune element from twiss
    #twiss = _lattice_dict['V1SR'].getElementList('twiss')[0]
    #tune = CaElement(name='tune', virtual=0)
    #tune.updatePvRecord(twiss.pv(field='tunex')[-1], None, 
    #                    [HLA_TAG_PREFIX+'.elemfield.x'])
    #tune.updatePvRecord(twiss.pv(field='tuney')[-1], None,
    #                    [HLA_TAG_PREFIX+'.elemfield.y'])
    #_lattice_dict['V1SR'].insertElement(tune, 0)
    #
    # LTB 
    _lattice_dict['V1LTB'].loop = False
    #_lat = _lattice_dict['LTB']

    #
    # SR
    _lattice_dict['V1SR'].loop = True
    _lat = _lattice_dict['V1SR']
        

def initNSLS2V1SRTwiss():
    """
    initialize the twiss data from virtual accelerator
    """

    # SR Twiss
    global _lat, _twiss
    twel = _lat.getElementList('twiss')
    if len(twel) == 1:
        tune = _lat.getElementList('tune')[-1]
        tw = twel[0]
        _twiss = Twiss('virtac')

        _twiss.tune = (tune.x, tune.y)
        _twiss.chrom = (None, None)

        nps = np.array(tw.s)
        for ielem in range(_lat.size()):
            elem = _lat._elements[ielem]
            if elem.family == HLA_VFAMILY: continue
            ds = nps - elem.sb

            i = np.argmin(np.abs(nps - elem.sb))

            gammax = (1 + tw.alphax[i]**2)/tw.betax[i]
            gammay = (1 + tw.alphay[i]**2)/tw.betay[i]
            twi = TwissItem(s = tw.s[i], alpha=(tw.alphax[i], tw.alphay[i]),
                           beta=(tw.betax[i], tw.betay[i]),
                           gamma=(gammax, gammay),
                           eta=(tw.etax[i], tw.etay[i]),
                           phi=(tw.phix[i], tw.phiy[i]))

            _twiss._elements.append(elem.name)
            _twiss.append(twi)

        _lat._twiss = _twiss

    return

    # s location
    s      = [v for v in caget('SR:C00-Glb:G00{POS:00}RB-S')]
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
    chx = caget('SR:C00-Glb:G00{CHROM:00}RB-X')
    chy = caget('SR:C00-Glb:G00{CHROM:00}RB-Y')

    #global _twiss, _lat

    #print(__file__, "Reading twiss items:", len(s))
    logger.info("Elements in lattice '%s': %d" % 
                (_lat.name, len(_lat._elements)))

    # fix the Tracy convension by adding a new element at the end
    for x in [s, alphax, alphay, betax, betay, etax, etay, orbx, orby,
              phix, phiy]:
        x.append(x[-1])
    
    _twiss = Twiss('virtac')

    _twiss.tune = (nux, nuy)
    _twiss.chrom = (chx, chy)
    #print __file__, len(s), len(betax)
    
    nps = np.array(s, 'd')
    for ielem in range(_lat.size()):
        elem = _lat._elements[ielem]
        if elem.family == HLA_VFAMILY: continue
        ds = nps - elem.sb

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

    _lat._twiss = _twiss

def initNSLS2():
    """ 
    initialize the NSLS2 accelerator lattice 'SR', 'LTD1', 'LTD2', 'LTB'.

    The initialization is done in the following order:

        - user's `${HOME}/.hla/us_nsls2_cfs.csv`; if not then
        - channel finder service in `env ${HLA_CFS_URL}`; if not then
        - the `us_nsls2_cfs.csv` installed with aphla package; if not then
        - RuntimeError
    """

    cfa = ChannelFinderAgent()
    cfs_filename = 'us_nsls2_cfs.csv'
    src_home_csv = os.path.join(os.environ['HOME'], '.hla', cfs_filename)
    HLA_CFS_URL = os.environ.get('HLA_CFS_URL', None)

    if os.path.exists(src_home_csv):
        msg = "Creating lattice from home csv '%s'" % src_home_csv
        logger.info(msg)
        cfa.importCsv(src_home_csv)
    elif os.environ.get('HLA_CFS_URL', None):
        msg = "Creating lattice from channel finder '%s'" % HLA_CFS_URL
        logger.info(msg)
        cfa.downloadCfs(HLA_CFS_URL, tagName='aphla.sys.*')
    elif conf.has(cfs_filename):
        src_pkg_csv = conf.filename(cfs_filename)
        msg = "Creating lattice from '%s'" % src_pkg_csv
        logger.info(msg)
        #print(msg)
        cfa.importCsv(src_pkg_csv)
    else:
        logger.error("Channel finder data are available, no '%s', no server" % 
                     cfs_filename)
        raise RuntimeError("Failed at loading cache file")

    #print(msg)
    for k in [('name', u'elemName'), 
              ('field', u'elemField'), 
              ('devname', u'devName'),
              ('family', u'elemType'), 
              ('index', u'ordinal'), 
              ('se', u'sEnd'),
              ('system', u'system')]:
        cfa.renameProperty(k[1], k[0])

    #tags = cfa.tags('aphla.sys.*')

    global _lat, _lattice_dict

    # should be 'aphla.sys.' + ['VSR', 'VLTB', 'VLTD1', 'VLTD2']
    logger.info("Initializing lattice according to the tags: %s" % HLA_TAG_SYS_PREFIX)
    for latname in ['SR', 'LTB', 'LTD1', 'LTD2']:
        lattag = HLA_TAG_SYS_PREFIX + '.' + latname
        logger.info("Initializing lattice %s (%s)" % (latname, lattag))
        _lattice_dict[latname] = createLattice(latname, cfa.rows, lattag,
                                               desc = cfa.source)

    orm_filename = ''
    if orm_filename and conf.has(orm_filename):
        #print("Using ORM:", conf.filename(orm_filename))
        _lattice_dict['SR'].ormdata = OrmData(conf.filename(orm_filename))
    else:
        logger.warning("No ORM '%s' found" % orm_filename)

    # a virtual bpm. its field is a "merge" of all bpms.
    bpms = _lattice_dict['SR'].getElementList('BPM')
    allbpm = merge(bpms, **{'virtual': 1, 'name': HLA_VBPM, 
                            'family': HLA_VFAMILY})
    _lattice_dict['SR'].insertElement(allbpm, groups=[HLA_VFAMILY])

    #
    # LTB 
    _lattice_dict['LTB'].loop = False
    #_lat = _lattice_dict['LTB']

    #
    # SR
    _lattice_dict['SR'].loop = True
    _lat = _lattice_dict['SR']


def initTLS(config=None):
    """ 
    initialize the Taiwan Light Source accelerator lattice 'SR'.

    unless a config is provided, the initialization is done in the following
    order:

        - user's `${HOME}/.hla/tw_tls_cfs.csv`; if not then
        - channel finder service in `env ${HLA_CFS_URL}`; if not then
        - the `tw_tls_cfs.csv` installed with aphla package; if not then
        - RuntimeError

    the provided config can be a csv file or http url to channel finder
    resources.
    """

    cfa = ChannelFinderAgent()
    if config is not None:
        if config.startswith("http"): 
            logger.info("Creating lattice from web '%s'" % config)
            cfa.downloadCfs(config, tagName='aphla.sys.*')
        elif os.path.exists(config):
            logger.info("Creating lattice from file '%s'" % config)
            cfa.importCsv(config)
        elif conf.has(config):
            fname = conf.filename(config)
            logger.info("Creating lattice from system file '%s'" % fname)
            cfa.importCsv(fname)
        else:
            logger.error("'%s' is not recognized data source" % config)
            raise RuntimeError("can not initialze from '%s'" % config)
    else:
        cfs_filename = 'tw_tls_cfs.csv'
        src_home_csv = os.path.join(os.environ['HOME'], '.hla', cfs_filename)
        HLA_CFS_URL = os.environ.get('HLA_CFS_URL', None)

        if os.path.exists(src_home_csv):
            msg = "Creating lattice from home csv '%s'" % src_home_csv
            logger.info(msg)
            cfa.importCsv(src_home_csv)
        elif os.environ.get('HLA_CFS_URL', None):
            msg = "Creating lattice from channel finder '%s'" % HLA_CFS_URL
            logger.info(msg)
            cfa.downloadCfs(HLA_CFS_URL, tagName='aphla.sys.*')
        elif conf.has(cfs_filename):
            src_pkg_csv = conf.filename(cfs_filename)
            msg = "Creating lattice from '%s'" % src_pkg_csv
            logger.info(msg)
            #print(msg)
            cfa.importCsv(src_pkg_csv)
        else:
            logger.error("Channel finder data are available, no '%s', no server" % 
                         cfs_filename)
            raise RuntimeError("Failed at loading cache file")

    #print(msg)
    for k in [('name', u'elemName'), 
              ('field', u'elemField'), 
              ('devname', u'devName'),
              ('family', u'elemType'), 
              ('index', u'ordinal'), 
              ('se', u'sEnd'),
              ('system', u'system')]:
        cfa.renameProperty(k[1], k[0])

    #tags = cfa.tags('aphla.sys.*')

    global _lat, _lattice_dict

    # should be 'aphla.sys.' + ['VSR', 'VLTB', 'VLTD1', 'VLTD2']
    logger.info("Initializing lattice according to the tags: %s" % HLA_TAG_SYS_PREFIX)
    for latname in ['SR']:
        lattag = HLA_TAG_SYS_PREFIX + '.' + latname
        logger.info("Initializing lattice %s (%s)" % (latname, lattag))
        _lattice_dict[latname] = createLattice(latname, cfa.rows, lattag,
                                               desc = cfa.source)

    orm_filename = ''
    if orm_filename and conf.has(orm_filename):
        #print("Using ORM:", conf.filename(orm_filename))
        _lattice_dict['SR'].ormdata = OrmData(conf.filename(orm_filename))
    else:
        logger.warning("No ORM '%s' found" % orm_filename)

    # a virtual bpm. its field is a "merge" of all bpms.
    bpms = _lattice_dict['SR'].getElementList('BPM')
    allbpm = merge(bpms, **{'virtual': 1, 'name': HLA_VBPM, 
                            'family': HLA_VFAMILY})
    _lattice_dict['SR'].insertElement(allbpm, groups=[HLA_VFAMILY])

    #
    # LTB 
    #_lattice_dict['LTB'].loop = False
    #_lat = _lattice_dict['LTB']

    #
    # SR
    _lattice_dict['SR'].loop = True
    _lat = _lattice_dict['SR']


def saveCache():
    """
    .. deprecated:: 0.3
    """
    raise DeprecationWarning()

    output = open(os.path.join(HLA_DATA_DIRS, HLA_MACHINE,'hla_cache.pkl'), 'w')
    import pickle
    #import cPickle as pickle
    pickle.dump(_lattice_dict, output)
    pickle.dump(_lat, output)
    pickle.dump(_orm, output)
    output.close()

def loadCache():
    """
    .. deprecated:: 0.3
    """
    raise DeprecationWarning()

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

def getLattice(lat = None):
    """
    return a :class:`~aphla.lattice.Lattice` object with given name. return the
    current lattice by default.

    .. seealso:: :func:`~aphla.machines.lattices`
    """
    if lat is None:
        return _lat

    global _lattice_dict
    #for k, v in _lattice_dict.items():
    #    print k, v.mode
    return _lattice_dict.get(lat, None)

def lattices():
    """
    get a list of available lattices

    Example::

      >>> lattices()
      [ 'LTB', 'LTB-txt', 'SR', 'SR-txt'}
      >>> use('LTB-txt')

    A lattice can be used with :func:`~aphla.machines.use`
    """
    #return dict((k, v.mode) for k,v in _lattice_dict.iteritems())
    return _lattice_dict.keys()


