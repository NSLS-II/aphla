from __future__ import print_function, division, absolute_import

"""
NSLS2 Machine Structure Initialization
--------------------------------------
"""

# :author: Lingyun Yang <lyyang@bnl.gov>

from .. import (HLA_TAG_SYS_PREFIX, createLattice, findCfaConfig, getResource,
                setUnitConversion, createVirtualElements)
from .. import (OrmData, TwissData)

from fnmatch import fnmatch
import logging
_logger = logging.getLogger(__name__)
#_logger.setLevel(logging.DEBUG)

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
    srcname = kwargs.get('src', 'nsls2')
    cfa = findCfaConfig(srcname, machine, submachines)

    # the column name in CSV or the property name in channel finder is
    # different from the Lattice class property, need to rename.
    if cfa.source.endswith(".sqlite") or cfa.source.endswith(".csv"):
        for k,v in _db_map.items(): cfa.renameProperty(k, v)
    elif cfa.source.startswith("http"):
        for k,v in _cf_map.items(): cfa.renameProperty(k, v)

    lattice_dict = {}

    #_logger.error("HELP")
    # should be 'aphla.sys.' + ['VSR', 'VLTB', 'VLTD1', 'VLTD2']
    _logger.info("Initializing lattice according to the tags: %s" % HLA_TAG_SYS_PREFIX)

    for latname in ['SR', 'LTB', 'LTD1', 'LTD2', 'BR', 'BTD', 'BTS']:
        if not fnmatch(latname, submachines): continue

        lattag = HLA_TAG_SYS_PREFIX + '.' + latname
        _logger.info("Initializing lattice %s (%s)" % (latname, lattag))
        lattice_dict[latname] = createLattice(latname, cfa.rows, lattag,
                                               desc = cfa.source)
        lattice_dict[latname].machine = machine
        if lattice_dict[latname].size() == 0:
            _logger.warn("lattice '%s' has no elements" % latname)

    # get the file, search current dir first
    data_filename = getResource('sr.hdf5', __name__)
    if data_filename:
        lattice_dict['SR'].ormdata = OrmData(data_filename)
        lattice_dict['SR']._twiss = TwissData(data_filename)
        lattice_dict['SR']._twiss.load_hdf5(data_filename)
        _logger.info("using ORM data '%s'" % data_filename)
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
    if 'LTB' in lattice_dict: lattice_dict['LTB'].loop = False
    data_filename = getResource('ltb_unitconv.hdf5', __name__)
    setUnitConversion(lattice_dict['LTD1'], data_filename, "unitconv")
    setUnitConversion(lattice_dict['LTD2'], data_filename, "unitconv")
    setUnitConversion(lattice_dict['LTB'], data_filename, "unitconv")
    #_lat = _lattice_dict['LTB']

    data_filename = getResource('br_unitconv.hdf5', __name__)
    setUnitConversion(lattice_dict['BR'], data_filename, "unitconv")

    data_filename = getResource('bts_unitconv.hdf5', __name__)
    setUnitConversion(lattice_dict['BTS'], data_filename, "unitconv")

    data_filename = getResource('btd_unitconv.hdf5', __name__)
    setUnitConversion(lattice_dict['BTD'], data_filename, "unitconv")
    #
    # SR
    lattice_dict['SR'].loop = True
    lattice_dict['SR'].sb = 0.0
    lattice_dict['SR'].se = 791.958
    lattice_dict['SR'].Ek = 3000.0
    #uc_m2mm = UcPoly1d('m', 'mm', [1e3, 0])
    #uc_mm2m = UcPoly1d('mm', 'm', [1e-3, 0])
    #
    #for e in lattice_dict['V2SR'].getElementList('BPM'):
    #    e.addUnitConversion('x', uc_m2mm, None, "phy")
    #    e.addUnitConversion('x', uc_mm2m, "phy", None)

    # merge common magnets to virtual elements
    for k,vlat in lattice_dict.items():
        createVirtualElements(vlat)
    _logger.info("virtual elements created")

    return lattice_dict, lattice_dict['SR']
