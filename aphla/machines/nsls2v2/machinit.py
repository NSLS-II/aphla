"""
NSLS2V2 Machine Structure Initialization
-----------------------------------------
"""

# :author: Lingyun Yang <lyyang@bnl.gov>

from .. import (HLA_TAG_SYS_PREFIX, HLA_VBPM, setUnitConversion,
                setGoldenLattice, createLattice, createVirtualElements,
                findCfaConfig, getResource)
from .. import (OrmData, Twiss, UcPoly)

from fnmatch import fnmatch
import logging
_logger = logging.getLogger(__name__)
#_logger.setLevel(logging.DEBUG)

_cf_map = {'elemName': 'name', 
           'elemField': 'field', 
           'devName': 'devname',
           'elemType': 'family',
           'elemGroup': 'group', 
           'elemHandle': 'handle',
           'elemIndex': 'index', 
           'elemPosition': 'se',
           'elemLength': 'length',
           'system': 'system'
}


def init_submachines(machine, submachines, **kwargs):
    """ initialize the submachines."""
    # if src provides an explicit filename/url to initialize
    srcname = kwargs.get('src', 'nsls2v2')
    cfa = findCfaConfig(srcname, machine, submachines)

    # the column name in CSV or the property name in channel finder will be
    # the same (NOT different) from the Lattice class property, need to rename.
    #
    #if cfa.source.endswith(".sqlite") or cfa.source.endswith(".csv"):
    #    for k,v in _db_map.iteritems(): cfa.renameProperty(k, v)
    #elif cfa.source.startswith("http"):
    for k,v in _cf_map.iteritems(): cfa.renameProperty(k, v)

    cfa.splitPropertyValue('group')

    lattice_dict = {}

    #_logger.error("HELP")
    # should be 'aphla.sys.' + ['VSR', 'VLTB', 'VLTD1', 'VLTD2']
    _logger.info("Initializing lattice: %s" % HLA_TAG_SYS_PREFIX)

    for latname in ['V2SR', 'V1LTB', 'V1LTD1', 'V1LTD2']:
        if not fnmatch(latname, submachines): continue

        lattag = HLA_TAG_SYS_PREFIX + '.' + latname
        _logger.info("Initializing lattice %s (%s)" % (latname, lattag))
        lattice_dict[latname] = createLattice(latname, cfa.rows, lattag,
                                               desc = cfa.source)
        lattice_dict[latname].machine = machine
        if lattice_dict[latname].size() == 0:
            _logger.warn("lattice '%s' has no elements" % latname)

    # setting unit
    for e in lattice_dict['V2SR'].getElementList('QUAD'):
        e.setRawUnit('k1', 'm^{-2}')
    for e in lattice_dict['V2SR'].getElementList('SEXT'):
        e.setRawUnit('k2', 'm^{-3}')
    for e in lattice_dict['V2SR'].getElementList('COR'):
        if 'x' in e.fields(): e.setRawUnit('x', 'rad')
        if 'y' in e.fields(): e.setRawUnit('y', 'rad')
        
    # get the file, search current dir first
    data_filename = getResource('nsls2v2.hdf5', __name__)
    if data_filename:
        lattice_dict['V2SR'].ormdata = OrmData()
        # group info is a redundant info, needs rebuild based on each element
        lattice_dict["V2SR"].buildGroups()
        #lattice_dict['V2SR'].ormdata.load_hdf5(data_filename, "V2SR/orm")
        # hack for h5py < 2.1.1
        ormfile = getResource('v2sr_orm.hdf5', __name__)
        lattice_dict['V2SR'].ormdata.load(ormfile)        
        _logger.info("using ORM data '%s'" % ormfile)

        lattice_dict['V2SR']._twiss = Twiss(data_filename)
        #lattice_dict['V2SR']._twiss.load_hdf5(data_filename, "V2SR/twiss")
        # hack for h5py < 2.1.1
        data_filename = getResource('v2sr_twiss.hdf5', __name__)
        if data_filename is not None:
            lattice_dict['V2SR']._twiss.load(data_filename)
            _logger.info("using Twiss data '%s'" % data_filename)
        else:
            _logger.warn("twiss data 'v2sr_twiss.hdf5' not found")
            
        data_filename = getResource('v2sr_unitconv.hdf5', __name__)
        if data_filename is not None:
            setUnitConversion(lattice_dict['V2SR'], data_filename, "unitconv")
            _logger.info("using unitconv data '%s'" % data_filename)
        else:
            _logger.warn("unitconv data 'v2sr_unitconv.hdf5' not found")

        data_filename = getResource('v2sr_golden.hdf5', __name__)
        if data_filename is not None:
            setGoldenLattice(lattice_dict['V2SR'], data_filename, "golden")
            _logger.info("using golden lattice data '%s'" % data_filename)
        else:
            _logger.warn("golden lattice data 'v2sr_golden.hdf5' not found")

    else:
        _logger.warning("No ORM '%s' found" % data_filename)

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
    lattice_dict['V2SR'].sb = 0.0
    lattice_dict['V2SR'].se = 791.958
    lattice_dict['V2SR'].loop = True

    for bpm in lattice_dict['V2SR'].getElementList('BPM'):
        bpm.setRawUnit('x', 'm')
        bpm.setRawUnit('y', 'm')
    _logger.info("raw unit for BPM x and y are set")

    for k,vlat in lattice_dict.items():
        createVirtualElements(vlat)
    _logger.info("virtual elements created")

    return lattice_dict, lattice_dict['V2SR']
