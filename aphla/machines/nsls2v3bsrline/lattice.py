from .. import (HLA_TAG_SYS_PREFIX, HLA_VBPM, HLA_VFAMILY, 
                createLattice, findCfaConfig)
from ... import element

from pkg_resources import resource_string, resource_exists, resource_filename
from fnmatch import fnmatch
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
