from .. import (HLA_TAG_SYS_PREFIX, HLA_VBPM, HLA_VFAMILY,
                ChannelFinderAgent, Lattice)
from ... import element

from pkg_resources import resource_string, resource_exists, resource_filename
from fnmatch import fnmatch
import os
import logging
logger = logging.getLogger(__name__)

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

def findCfaConfig(srcname, machine, submachines):
    """
    find the appropriate config for ChannelFinderAgent

    initialize the virtual accelerator 'V2SR', 'V1LTD1', 'V1LTD2', 'V1LTB' from

    - `${HOME}/.hla/nsls2v2.sqlite`
    - channel finder in ${HLA_CFS_URL}
    - `nsls2v2.sqlite` with aphla package.

    """
    cfa = ChannelFinderAgent()

    # if source is an explicit file name
    if os.path.exists(srcname):
        msg = "Creating lattice from explicit source '%s'" % srcname
        if srcname.endswith('.csv'):
            cfa.importCsv(srcname)
        elif srcname.endswith(".sqlite"):
            cfa._importSqliteDb1(srcname)
        else:
            raise RuntimeError("Unknown explicit source '%s'" % srcname)
        return cfa

    # matching HOME -> CF -> Package
    homesrc = os.path.join(os.environ['HOME'], '.hla', srcname)
    HLA_CFS_URL = os.environ.get('HLA_CFS_URL', None)

    if os.path.exists(homesrc + '.csv'):
        msg = "Creating lattice from '%s.csv'" % homesrc
        logger.info(msg)
        cfa.importCsv(homesrc + '.csv')
        #for k,v in _cf_map.iteritems(): cfa.renameProperty(k, v)
    elif os.path.exists(homesrc + '.sqlite'):
        msg = "Creating lattice from '%s.sqlite'" % homesrc
        logger.info(msg)
        cfa.importSqliteDb(homesrc + '.sqlite')
        #for k,v in _db_map.iteritems(): cfa.renameProperty(k, v)
    elif os.environ.get('HLA_CFS_URL', None):
        msg = "Creating lattice from channel finder '%s'" % HLA_CFS_URL
        logger.info(msg)
        cfa.downloadCfs(HLA_CFS_URL, property=[('hostName', '*'), ('iocName', '*')], tagName='aphla.sys.*')
        # map the cf property name to alpha property name
        #for k,v in _cf_map.iteritems(): cfa.renameProperty(k, v)
    elif resource_exists(__name__, os.path.join(machine, srcname + '.csv')):
        name = resource_filename(__name__, os.path.join(machine, 
                                                        srcname + '.csv'))
        #src_pkg_csv = conf.filename(cfs_filename)
        msg = "Creating lattice from '%s'" % name
        logger.info(msg)
        cfa.importCsv(name)
        #for k,v in _cf_map.iteritems(): cfa.renameProperty(k, v)
    elif resource_exists(__name__, os.path.join(machine, srcname + '.sqlite')):
        name = resource_filename(__name__, os.path.join(machine, 
                                                        srcname + '.sqlite'))
        msg = "Creating lattice from '%s'" % name
        logger.info(msg)
        #print(msg)
        #src_pkg_csv.endswith('.sqlite')
        msg = "Creating lattice from '%s'" % name
        logger.info(msg)
        cfa.importSqliteDb(name)
        #for k,v in _db_map.iteritems(): cfa.renameProperty(k, v)
    else:
        logger.error("Lattice data are available for machine '%s'" % machine)
        raise RuntimeError("Failed at loading data file '%s' from '%s'" % (
            machine, srcname))

    return cfa

def createLattice(name, pvrec, systag, desc = 'channelfinder', 
                  create_vbpm = True):
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
                elem = element.CaElement(**prpt)
            except:
                print("Error: creating element '{0}' with '{1}'".format(name, prpt))
                raise

            #lat.appendElement(elem)
            lat.insertElement(elem)
        
        handle = prpt.get('handle', None).lower()
        if handle == 'get': prpt['handle'] = 'readback'
        elif handle == 'put': prpt['handle'] = 'setpoint'

        handle = prpt.get('handle', None).lower()
        if handle == 'get': prpt['handle'] = 'READBACK'
        elif handle == 'put': prpt['handle'] = 'SETPOINT'
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


def init_submachines(machine, submachines, **kwargs):
    """ 
    initialize the virtual accelerator 'V3BSRLINE'

    This is a temp ring, always use database in the package
    """

    # if src provides an explicit filename/url to initialize
    srcname = resource_filename(__name__, 'us_nsls2v3bsrline.sqlite')
    cfa = findCfaConfig(srcname, machine, submachines)

    for k,v in _db_map.iteritems(): cfa.renameProperty(k, v)

    # should be 'aphla.sys.' + ['VSR', 'VLTB', 'VLTD1', 'VLTD2']
    logger.info("Initializing lattice according to the tags: %s" % HLA_TAG_SYS_PREFIX)

    lattice_dict = {}
    for latname in ['V3BSRLINE']:
        lattag = HLA_TAG_SYS_PREFIX + '.' + latname
        logger.info("Initializing lattice %s (%s)" % (latname, lattag))
        lattice_dict[latname] = createLattice(latname, cfa.rows, lattag,
                                               desc = cfa.source, create_vbpm = False)
        if lattice_dict[latname].size() == 0:
            logger.warn("lattice '%s' has no elements" % latname)

    #orm_filename = None
    #if orm_filename and conf.has(orm_filename):
    #    #print("Using ORM:", conf.filename(orm_filename))
    #    _lattice_dict['V2SR'].ormdata = OrmData(conf.filename(orm_filename))
    #    logger.info("using ORM data '%s'" % orm_filename)
    #else:
    #    logger.warning("No ORM '%s' found" % orm_filename)


    lattice_dict['V3BSRLINE'].loop = False
    _lat = lattice_dict['V3BSRLINE']

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
        
    allbpm = element.merge(bpms, **{'virtual': 1, 'name': HLA_VBPM,
                            'family': HLA_VFAMILY})
    _lat.insertElement(allbpm, groups=[HLA_VFAMILY])

    # the last thing (when virtual elem is ready)
    _lat.buildGroups()

    return lattice_dict, _lat
