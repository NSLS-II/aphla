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
import cPickle as pickle
import inspect

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

# HOME path
HOME = os.path.expanduser('~')
# HOME = os.environ['HOME'] will NOT work on Windows,
# unless %HOME% is set on Windows.

_cf_map = {'elemName': 'name', 
           'elemField': 'field', 
           'devName': 'devname',
           'elemType': 'family', 
           'elemHandle': 'handle',
           'elemIndex': 'index', 
           'elemPosition': 'se',
           'elemLength': 'length',
           'system': 'system'
}

_db_map = {'elem_type': 'family',
           'lat_index': 'index',
           'position': 'se',
           'elem_group': 'group',
           'dev_name': 'devname',
           'elem_field': 'field'
}

def funcname():
    """
    A utility function to return the string of the
    function name within which this function is invoked.
    
    For example, if you have a function like:
    
    def somefunc(x,y):
       print 'This function name is: %s' % funcname()
       
    Then
    
    >>> somefunc(1,2)
    >>> This function name is: somefunc
    
    """
    return inspect.stack()[1][3]
    

def createLattice(name, pvrec, systag, desc = 'channelfinder', create_vbpm = True):
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
        if 'se' in prpt:
            prpt['sb'] = float(prpt['se']) - float(prpt.get('length', 0))
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
        
        handle = prpt.get('handle', None).lower()
        if handle == 'get': prpt['handle'] = 'readback'
        elif handle == 'set': prpt['handle'] = 'setpoint'

        handle = prpt.get('handle', None).lower()
        if handle == 'get': prpt['handle'] = 'READBACK'
        elif handle == 'set': prpt['handle'] = 'SETPOINT'
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
        
    if create_vbpm:
        # a virtual bpm. its field is a "merge" of all bpms.
        bpms = lat.getElementList('BPM')
        allbpm = merge(bpms, **{'virtual': 1, 'name': HLA_VBPM, 
                                'family': HLA_VFAMILY, 'index': 100000})
        lat.insertElement(allbpm, groups=[HLA_VFAMILY])

    return lat


def initNSLS2V2(use_cache = True, save_cache = True):
    """ 
    initialize the virtual accelerator 'V2SR', 'V1LTD1', 'V1LTD2', 'V1LTB' from

    - `${HOME}/.hla/us_nsls2v2.sqlite`
    - channel finder in ${HLA_CFS_URL}
    - `us_nsls2v2.sqlite` with aphla package.
    """
    
    if use_cache:
        try:
            loadCache(funcname())
        except:
            print('Lattice initialization using cache failed. ' +
                  'Will attempt initialization with other method(s).')
        else:
            # Loading from cache was successful.
            return
    

    cfa = ChannelFinderAgent()
    cfs_filename = 'us_nsls2v2.sqlite'
    src_home_csv = os.path.join(HOME, '.hla', cfs_filename)
    HLA_CFS_URL = os.environ.get('HLA_CFS_URL', None)

    if os.path.exists(src_home_csv):
        msg = "Creating lattice from home file '%s'" % src_home_csv
        logger.info(msg)
        if src_home_csv.endswith('.csv'):
            cfa.importCsv(src_home_csv)
            for k,v in _cf_map.iteritems(): cfa.renameProperty(k, v)            
        elif src_home_csv.endswith('.sqlite'):
            cfa.importSqliteDb(src_home_csv)
            for k,v in _db_map.iteritems(): cfa.renameProperty(k, v)
    elif os.environ.get('HLA_CFS_URL', None):
        msg = "Creating lattice from channel finder '%s'" % HLA_CFS_URL
        logger.info(msg)
        cfa.downloadCfs(HLA_CFS_URL, tagName='aphla.sys.*')
        # map the cf property name to alpha property name
        for k,v in _cf_map.iteritems(): cfa.renameProperty(k, v)
    elif conf.has(cfs_filename):
        src_pkg_csv = conf.filename(cfs_filename)
        msg = "Creating lattice from '%s'" % src_pkg_csv
        logger.info(msg)
        #print(msg)
        if src_pkg_csv.endswith('.csv'):
            cfa.importCsv(src_pkg_csv)
            for k,v in _cf_map.iteritems(): cfa.renameProperty(k, v)
        elif src_pkg_csv.endswith('.sqlite'): 
            cfa.importSqliteDb(src_pkg_csv)
            for k,v in _db_map.iteritems(): cfa.renameProperty(k, v)
    else:
        logger.error("Channel finder data are available, no '%s', no server" % 
                     cfs_filename)
        raise RuntimeError("Failed at loading cache file")

    #tags = cfa.tags('aphla.sys.*')

    global _lat, _lattice_dict

    # should be 'aphla.sys.' + ['VSR', 'VLTB', 'VLTD1', 'VLTD2']
    logger.info("Initializing lattice according to the tags: %s" % HLA_TAG_SYS_PREFIX)
    for latname in ['V2SR', 'V1LTB', 'V1LTD1', 'V1LTD2']:
        lattag = HLA_TAG_SYS_PREFIX + '.' + latname
        logger.info("Initializing lattice %s (%s)" % (latname, lattag))
        _lattice_dict[latname] = createLattice(latname, cfa.rows, lattag,
                                               desc = cfa.source)
        if _lattice_dict[latname].size() == 0:
            logger.warn("lattice '%s' has no elements" % latname)

    orm_filename = 'us_nsls2v2_sr_orm.hdf5'
    if orm_filename and conf.has(orm_filename):
        #print("Using ORM:", conf.filename(orm_filename))
        _lattice_dict['V2SR'].ormdata = OrmData(conf.filename(orm_filename))
        logger.info("using ORM data '%s'" % orm_filename)
    else:
        logger.warning("No ORM '%s' found" % orm_filename)


    # tune element from twiss
    #twiss = _lattice_dict['V2SR'].getElementList('twiss')[0]
    #tune = CaElement(name='tune', virtual=0)
    #tune.updatePvRecord(twiss.pv(field='tunex')[-1], None, 
    #                    [HLA_TAG_PREFIX+'.elemfield.x'])
    #tune.updatePvRecord(twiss.pv(field='tuney')[-1], None,
    #                    [HLA_TAG_PREFIX+'.elemfield.y'])
    #_lattice_dict['V2SR'].insertElement(tune, 0)
    #
    # LTB 
    _lattice_dict['V1LTB'].loop = False
    #_lat = _lattice_dict['LTB']

    #
    # SR
    _lattice_dict['V2SR'].loop = True
    _lat = _lattice_dict['V2SR']
    
    if save_cache:
        saveCache(funcname(), 'V2SR')
        

def initNSLS2V3BSRLine(with_twiss = False):
    """ 
    initialize the virtual accelerator 'V3BSRLINE'

    This is a temp ring, always use database in the package
    """

    cfa = ChannelFinderAgent()
    cfs_filename = 'us_nsls2v3bsrline.sqlite'
    src_pkg_csv = conf.filename(cfs_filename)
    msg = "Creating lattice from '%s'" % src_pkg_csv
    logger.info(msg)
    #print(msg)
    cfa.importSqliteDb(src_pkg_csv)
    for k,v in _db_map.iteritems(): cfa.renameProperty(k, v)

    global _lat, _lattice_dict

    # should be 'aphla.sys.' + ['VSR', 'VLTB', 'VLTD1', 'VLTD2']
    logger.info("Initializing lattice according to the tags: %s" % HLA_TAG_SYS_PREFIX)
    for latname in ['V3BSRLINE']:
        lattag = HLA_TAG_SYS_PREFIX + '.' + latname
        logger.info("Initializing lattice %s (%s)" % (latname, lattag))
        _lattice_dict[latname] = createLattice(latname, cfa.rows, lattag,
                                               desc = cfa.source, create_vbpm = False)
        if _lattice_dict[latname].size() == 0:
            logger.warn("lattice '%s' has no elements" % latname)

    orm_filename = None
    if orm_filename and conf.has(orm_filename):
        #print("Using ORM:", conf.filename(orm_filename))
        _lattice_dict['V2SR'].ormdata = OrmData(conf.filename(orm_filename))
        logger.info("using ORM data '%s'" % orm_filename)
    else:
        logger.warning("No ORM '%s' found" % orm_filename)


    _lattice_dict['V3BSRLINE'].loop = False
    _lat = _lattice_dict['V3BSRLINE']        

    L1 = 48.21334
    for e in _lat.getElementList('*_t1'):
        if e.sb: e.sb += L1
        if e.se: e.se += L1
    L2 = 791.958
    for e in _lat.getElementList('*_t2'):
        if e.sb: e.sb += L1 + L2
        if e.se: e.se += L1 + L2
    for e in _lat.getElementList('*_t3'):
        if e.sb: e.sb += L1 + 2*L2
        if e.se: e.se += L1 + 2*L2


    for e in _lat.getElementList('*_t1'):
        logger.info("searching alias for '{0}'".format(e.name))
        for t in ['_t2', '_t3']:
            ealias = _lat.getElementList(e.name[:-3] + t)
            if not ealias: 
                logger.info("no alias for '{0}'".format(e.name))
                continue
            if len(ealias) > 1: 
                raise RuntimeError(
                    "element '{0}' alias are not unique: {1}".format(
                        e.name, ealias))
            e2 = ealias[0]
            if e2.family == 'BPM': continue
            if e2.virtual: continue
            e.alias.append(e2)
            r = _lat.remove(e2.name)
            logger.info("removed alias '{0}' for '{1}'".format(e2, e))

        if e.family != 'BPM': e.name = e.name[:-3]

    #for i,e in enumerate(_lat._elements):
    #    logger.debug("{0}: {1}".format(i, e))

    _lat.sortElements()

    #for i,e in enumerate(_lat._elements):
    #    logger.debug("{0}: {1}".format(i, e))

    # a virtual bpm. its field is a "merge" of all bpms.
    bpms = _lat.getElementList('BPM')
    #logger.debug("bpms:{0}".format(bpms))
    #for i,e in enumerate(bpms):
    #    logger.debug("{0}: {1}".format(i, e))
        
    allbpm = merge(bpms, **{'virtual': 1, 'name': HLA_VBPM,
                            'family': HLA_VFAMILY})
    _lat.insertElement(allbpm, groups=[HLA_VFAMILY])

    # the last thing (when virtual elem is ready)
    _lat.buildGroups()


def initNSLS2V2SRTwiss():
    """
    initialize the twiss data from virtual accelerator
    """

    # SR Twiss
    global _lat, _twiss
    _twiss = Twiss("V2SR")
    _twiss.load(conf.filename('us_nsls2v2.sqlite'))
    _lat._twiss = _twiss


def initNSLS2(use_cache = True, save_cache = True):
    """ 
    initialize the NSLS2 accelerator lattice 'SR', 'LTD1', 'LTD2', 'LTB'.

    The initialization is done in the following order:

        - user's `${HOME}/.hla/us_nsls2.sqlite`; if not then
        - channel finder service in `env ${HLA_CFS_URL}`; if not then
        - the `us_nsls2.sqlite` installed with aphla package; if not then
        - RuntimeError
    """

    if use_cache:
        try:
            loadCache(funcname())
        except:
            print('Lattice initialization using cache failed. ' +
                  'Will attempt initialization with other method(s).')
        else:
            # Loading from cache was successful.
            return

    cfa = ChannelFinderAgent()
    cfs_filename = 'us_nsls2.sqlite'
    src_home_csv = os.path.join(HOME, '.hla', cfs_filename)
    HLA_CFS_URL = os.environ.get('HLA_CFS_URL', None)

    if os.path.exists(src_home_csv):
        msg = "Creating lattice from home '%s'" % src_home_csv
        logger.info(msg)
        cfa.importSqliteDb(src_home_csv)
    elif os.environ.get('HLA_CFS_URL', None):
        msg = "Creating lattice from channel finder '%s'" % HLA_CFS_URL
        logger.info(msg)
        cfa.downloadCfs(HLA_CFS_URL, tagName='aphla.sys.*')
    elif conf.has(cfs_filename):
        src_pkg_csv = conf.filename(cfs_filename)
        msg = "Creating lattice from '%s'" % src_pkg_csv
        logger.info(msg)
        #cfa.importCsv(src_pkg_csv)
        cfa.importSqliteDb(src_pkg_csv)
    else:
        logger.error("Channel finder data are available, no '%s', no server" % 
                     cfs_filename)
        raise RuntimeError("Failed at loading cache file")

    #print(msg)
    for k in [('name', u'elemName'), 
              ('field', u'elemField'), 
              ('devname', u'devName'),
              ('family', u'elemType'), 
              ('handle', u'elemHandle'),
              ('index', u'elemIndex'), 
              ('se', u'elemPosition'),
              ('length', u'elemLength'),
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
    _lattice_dict['LTD1'].loop = False
    #_lat = _lattice_dict['LTB']

    #
    # SR
    _lattice_dict['SR'].loop = True
    _lat = _lattice_dict['SR']

    if save_cache:
        saveCache(funcname(), 'SR')


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
        src_home_csv = os.path.join(HOME, '.hla', cfs_filename)
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


def saveCache(calling_func_name, selected_lattice_name):
    """
    """
    
    global _lattice_dict
    
    cache_folderpath = os.path.join(HOME,'.hla',HLA_MACHINE)
    if not os.path.isdir(cache_folderpath):
        os.mkdir(cache_folderpath)
    cache_filepath = os.path.join(cache_folderpath, calling_func_name+'.cpkl')
    with open(cache_filepath,'wb') as fp:
        pickle.dump(selected_lattice_name,fp,2)
        pickle.dump(_lattice_dict,fp,2)
    

def loadCache(calling_func_name):
    """
    """
    
    global _lat, _lattice_dict
    
    cache_folderpath = os.path.join(HOME,'.hla',HLA_MACHINE)
    cache_filepath = os.path.join(cache_folderpath, calling_func_name+'.cpkl')
    with open(cache_filepath,'rb') as fp:
        selected_lattice_name = pickle.load(fp)
        _lattice_dict = pickle.load(fp)
    _lat = _lattice_dict[selected_lattice_name]
    

def use(lattice):
    """
    switch to a lattice

    use :func:`~hla.machines.lattices` to get a dict of lattices and its mode
    name

    When switching lattice, twiss data is not sychronized.
    """
    global _lat, _lattice_dict
    if isinstance(lattice, Lattice):
        _lat = lattice
    elif _lattice_dict.get(lattice, None):
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


