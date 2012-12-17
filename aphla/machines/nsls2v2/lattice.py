from .. import (HLA_TAG_SYS_PREFIX, createLattice, findCfaConfig)

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
    """
    # if src provides an explicit filename/url to initialize
    srcname = kwargs.get('src', 'us_nsls2v2')
    cfa = findCfaConfig(srcname, machine, submachines)

    # the column name in CSV or the property name in channel finder is
    # different from the Lattice class property, need to rename.
    if cfa.source.endswith(".sqlite") or cfa.source.endswith(".csv"):
        for k,v in _db_map.iteritems(): cfa.renameProperty(k, v)
    elif cfa.source.startswith("http"):
        for k,v in _cf_map.iteritems(): cfa.renameProperty(k, v)

    lattice_dict = {}

    # should be 'aphla.sys.' + ['VSR', 'VLTB', 'VLTD1', 'VLTD2']
    logger.info("Initializing lattice according to the tags: %s" % HLA_TAG_SYS_PREFIX)

    for latname in ['V2SR', 'V1LTB', 'V1LTD1', 'V1LTD2']:
        if not fnmatch(latname, submachines): continue

        lattag = HLA_TAG_SYS_PREFIX + '.' + latname
        logger.info("Initializing lattice %s (%s)" % (latname, lattag))
        lattice_dict[latname] = createLattice(latname, cfa.rows, lattag,
                                               desc = cfa.source)
        if lattice_dict[latname].size() == 0:
            logger.warn("lattice '%s' has no elements" % latname)

    orm_filename = 'us_nsls2v2_sr_orm.hdf5'
    if orm_filename and conf.has(orm_filename):
        lattice_dict['V2SR'].ormdata = OrmData(orm_filename)
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
    if 'V1LTB' in lattice_dict: lattice_dict['V1LTB'].loop = False
    #_lat = _lattice_dict['LTB']

    #
    # SR
    if 'V2SR' in lattice_dict: lattice_dict['V2SR'].loop = True
    else: lattice_dict['V2SR'] = None

    return lattice_dict, lattice_dict['V2SR']
