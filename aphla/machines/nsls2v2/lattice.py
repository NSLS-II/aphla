from .. import (HLA_TAG_SYS_PREFIX, HLA_VBPM, 
                createLattice, findCfaConfig, getResource)
from .. import (OrmData, Twiss, UcPoly)

from fnmatch import fnmatch
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

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
    srcname = kwargs.get('src', 'nsls2v2')
    cfa = findCfaConfig(srcname, machine, submachines)

    # the column name in CSV or the property name in channel finder is
    # different from the Lattice class property, need to rename.
    if cfa.source.endswith(".sqlite") or cfa.source.endswith(".csv"):
        for k,v in _db_map.iteritems(): cfa.renameProperty(k, v)
    elif cfa.source.startswith("http"):
        for k,v in _cf_map.iteritems(): cfa.renameProperty(k, v)

    lattice_dict = {}

    #logger.error("HELP")
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

    # get the file, search current dir first
    data_filename = getResource('v2sr.hdf5', __name__)
    if data_filename:
        lattice_dict['V2SR'].ormdata = OrmData(data_filename)
        lattice_dict['V2SR']._twiss = Twiss(data_filename)
        lattice_dict['V2SR']._twiss.load_hdf5(data_filename)
        logger.info("using ORM data '%s'" % data_filename)
    else:
        logger.warning("No ORM '%s' found" % data_filename)

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
    lattice_dict['V2SR'].loop = True
    uc_m2mm = UcPoly('m', 'mm', [1e3, 0])
    uc_mm2m = UcPoly('mm', 'm', [1e-3, 0])

    for e in lattice_dict['V2SR'].getElementList('BPM'):
        e.addUnitConversion('x', uc_m2mm, None, "phy")
        e.addUnitConversion('x', uc_mm2m, "phy", None)
        e.addUnitConversion('y', uc_m2mm, None, "phy")
        e.addUnitConversion('y', uc_mm2m, "phy", None)

    vbpm = lattice_dict['V2SR'].getElementList(HLA_VBPM, virtual=1)
    for v in vbpm:
        v.addUnitConversion('x', uc_m2mm, None, "phy")
        v.addUnitConversion('x', uc_mm2m, "phy", None)
        v.addUnitConversion('y', uc_m2mm, None, "phy")
        v.addUnitConversion('y', uc_mm2m, "phy", None)

    return lattice_dict, lattice_dict['V2SR']
