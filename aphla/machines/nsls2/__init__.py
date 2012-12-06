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

#from catools import caget, caput
#from lattice import Lattice
#from element import CaElement, merge
#from twiss import Twiss, TwissItem
#from fnmatch import fnmatch
#from ormdata import OrmData
#from orm import Orm
#from chanfinder import ChannelFinderAgent

#from . import conf

#from pkg_resources import resource_string, resource_exists, resource_filename

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




def initNSLS2V2SRTwiss():
    """
    initialize the twiss data from virtual accelerator
    """

    # SR Twiss
    global _lat, _twiss
    _twiss = Twiss("V2SR")
    _twiss.load(conf.filename('us_nsls2v2.sqlite'))
    _lat._twiss = _twiss




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


