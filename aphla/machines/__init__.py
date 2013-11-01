"""
Machine Structure Initialization
--------------------------------


In ``aphla`` one machine includes several accelerator structure,
e.g. "nsls2v2" is a machine with several submachine or lattice V1LTD, V1LTB,
V2SR.

Submachines are also called lattice in ``aphla``. Each lattice has a list of
elements, magnet or instrument. The submachines/lattices can share elements.
"""

# :author: Lingyun Yang <lyyang@bnl.gov>

from ..unitconv import *
from ..element import *
from ..apdata import *
from ..lattice import Lattice
from ..chanfinder import ChannelFinderAgent
from ..resource import getResource
from .. import catools

import utils

import os
import glob
import re
from pkg_resources import resource_string, resource_exists, resource_filename
import cPickle as pickle
import ConfigParser
import fnmatch
import logging
_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)
#
HLA_TAG_PREFIX = 'aphla'
HLA_TAG_EGET = HLA_TAG_PREFIX + '.eget'
HLA_TAG_EPUT = HLA_TAG_PREFIX + '.eput'
HLA_TAG_X    = HLA_TAG_PREFIX + '.x'
HLA_TAG_Y    = HLA_TAG_PREFIX + '.y'
HLA_TAG_SYS_PREFIX = HLA_TAG_PREFIX + '.sys'

#
HLA_VFAMILY = 'HLA:VIRTUAL'
HLA_VBPM   = 'HLA:VBPM'
HLA_VHCOR  = 'HLA:VHCOR'
HLA_VVCOR  = 'HLA:VVCOR'
HLA_VCOR   = 'HLA:VCOR'
HLA_VQUAD  = 'HLA:VQUAD'
HLA_VSEXT  = 'HLA:VSEXT'


# HOME = os.environ['HOME'] will NOT work on Windows,
# unless %HOME% is set on Windows, which is not the case by default.
_home_hla = os.path.join(os.path.expanduser('~'), '.hla')
HLA_CONFIG_DIR = os.environ.get('HLA_CONFIG_DIR', _home_hla)
#HLA_OUTPUT_DIR = os.environ.get('HLA_OUTPUT_DIR', None)
HLA_MACHINE    = os.environ.get('HLA_MACHINE', None)
HLA_DEBUG      = int(os.environ.get('HLA_DEBUG', 0))

# the properties used for initializing Element are different than
# ChannelFinderAgent (CFS or SQlite). This needs a re-map.
# convert from CFS property to Element property
_cf_map = {'elemName': 'name', 
           'elemField': 'field', 
           'devName': 'devname',
           'elemType': 'family',
           'elemGroups': 'groups', 
           'elemHandle': 'handle',
           'elemIndex': 'index', 
           'elemPosition': 'se',
           'elemLength': 'length',
           'system': 'system'
}


# keep all loaded lattice
_lattice_dict = {}

# the current lattice
_lat = None

def _init(machine, submachines = "*", **kwargs):
    """use load instead"""
    load_v1(machine, submachines = submachines, **kwargs)

def load_v1(machine, submachines = "*", **kwargs):
    """
    load submachine lattices in machine.

    Parameters
    -----------
    machine: str. the exact name of machine
    submachine: str. default '*'. pattern of sub machines
    use_cache: bool. default False. use cache
    save_cache: bool. default False, save cache
    """
    
    use_cache = kwargs.get('use_cache', False)
    save_cache = kwargs.get('save_cache', False)
    
    if use_cache:
        try:
            loadCache(machine)
        except:
            _logger.error('Lattice initialization using cache failed. ' +
                          'Will attempt initialization with other method(s).')
            save_cache = True
        else:
            # Loading from cache was successful.
            return
        
    #importlib.import_module(machine, 'machines')
    _logger.debug("importing '%s'" % machine)
    m = __import__(machine, globals(), locals(), [], -1)
    lats, lat = m.init_submachines(machine, submachines, **kwargs)
    # update machine name for each lattice
    
    global _lat, _lattice_dict
    _lattice_dict.update(lats)
    _lat = lat
    _logger.info("setting default lattice '%s'" % _lat.name)

    if save_cache:
        selected_lattice_name = [k for (k,v) in _lattice_dict.iteritems()
                                 if _lat == v][0]
        saveCache(machine, _lattice_dict, selected_lattice_name)
        
def _findMachinePath(machine):
    # if machine is an abs path
    if os.path.isabs(machine) and os.path.isdir(machine):
        mname = os.path.basename(os.path.realpath(machine))
        return machine, mname
    # try "machine" in HLA_CONFIG_DIR and ~/.hla/ (default)
    home_machine = os.path.join(HLA_CONFIG_DIR, machine)
    if os.path.isdir(home_machine):
        mname = os.path.basename(os.path.realpath(machine))
        return home_machine, mname
    # try the package
    pkg_machine = resource_filename(__name__, machine)
    _logger.info("trying '%s'" % pkg_machine)
    if os.path.isdir(pkg_machine):
        mname = os.path.basename(os.path.realpath(pkg_machine))
        return pkg_machine, mname

    return None, ""

def load(machine, submachines = "*", **kwargs):
    """
    load submachine lattices in machine.

    Parameters
    -----------
    machine: str. the exact name of machine
    submachine: str. default '*'. pattern of sub machines
    use_cache: bool. default False. use cache
    save_cache: bool. default False, save cache

    This machine can be a path to config dir.
    """
    
    #global _lattice_dict, _lat

    lat_dict, lat0 = {}, None

    use_cache = kwargs.get('use_cache', False)
    save_cache = kwargs.get('save_cache', False)

    if use_cache:
        try:
            loadCache(machine)
        except:
            _logger.error('Lattice initialization using cache failed. ' +
                  'Will attempt initialization with other method(s).')
            save_cache = True
        else:
            # Loading from cache was successful.
            return
        
    #importlib.import_module(machine, 'machines')
    machdir, machname = _findMachinePath(machine)
    if machdir is None:
        _logger.error("can not find machine data directory for '%s'" % machine)
        return

    _logger.debug("importing '%s' from '%s'" % (machine, machdir))

    cfg = ConfigParser.ConfigParser()
    cfg.readfp(open(os.path.join(machdir, "aphla.ini"), 'r'))
    _logger.debug("using config file: 'aphla.ini'")
    d = dict(cfg.items("COMMON"))
    # set proper output directory
    # global HLA_OUTPUT_DIR
    HLA_OUTPUT_DIR = d.get("output_dir", _home_hla)
    # the default submachine
    accdefault = d.get("default_submachine", None)

    # print(cfg.sections())
    # for all submachines specified in INI and matches the pattern
    msects = [subm for subm in re.findall(r'\w+', d.get("submachines", ""))
             if fnmatch.fnmatch(subm, submachines)]
    # print(msect)
    for msect in msects:
        d = dict(cfg.items(msect))
        accstruct = d.get("cfs_url", None)
        if accstruct is None:
            raise RuntimeError("No accelerator data source (cfs_url) available "
                               "for '%s'" % msect)
        #print cfa.rows[:3]
        acctag = d.get("cfs_tag", "aphla.sys.%s" % msect)
        cfa = ChannelFinderAgent()
        accsqlite = os.path.join(machdir, accstruct)
        if re.match(r"https?://.*", accstruct, re.I):
            _logger.debug("using CFS '%s' for '%s'" % (accstruct, msect))
            cfa.downloadCfs(accstruct, property=[('elemName', '*'), 
                                                 ('iocName', '*')],
                            tagName=acctag)
        elif os.path.isfile(accsqlite):
            _logger.debug("using SQlite '%s'" % accsqlite)
            cfa.loadSqlite(accsqlite)
        else:
            _logger.debug("NOT CFS '%s'" % accstruct)
            _logger.debug("NOT SQlite '%s'" % accsqlite)
            raise RuntimeError("Unknown accelerator data source '%s'" % accstruct)

        cfa.splitPropertyValue('elemGroups')
        cfa.splitChainedElement('elemName')
        for k,v in _cf_map.iteritems(): cfa.renameProperty(k, v)

        #print "New CFA:", cfa.rows

        lat = createLattice(msect, cfa.rows, acctag, cfa.source)
        lat.sb = d.get("s_begin", 0.0)
        lat.se = d.get("s_end", 0.0)
        lat.loop = bool(d.get("loop", True))
        lat.machine = machname

        uconvfile = d.get("unit_conversion", None)
        if uconvfile is not None: 
            _logger.debug("loading unit conversion '%s'" % uconvfile)
            loadUnitConversion(lat, os.path.join(machdir, uconvfile))

        physics_data = d.get("physics_data", None)
        if physics_data is not None:
            phy_fname = os.path.join(machdir, physics_data)
            #_logger.debug("loading ORM data '%s'" % ormfile)
            lat.ormdata = OrmData(phy_fname)
            #_logger.debug("loading Twiss data '%s'" % twissfile)
            lat._twiss = TwissData(phy_fname)
            lat._twiss.load(phy_fname)
            #_logger.debug("loaded {0} twiss data".format(len(lat._twiss.element)))
            #_logger.debug("using golden lattice data '%s'" % goldenfile)
            setGoldenLattice(lat, phy_fname, "Golden")

        vex = lambda k: re.findall(r"\w+", d.get(k, ""))
        vfams = { HLA_VBPM:  ('BPM',  vex("virtual_bpm_exclude")),
                  HLA_VHCOR: ('HCOR', vex("virtual_hcor_exclude")),
                  HLA_VVCOR: ('VCOR', vex("virtual_vcor_exclude")),
                  HLA_VCOR:  ('COR',  vex("virtual_cor_exclude")),
                  HLA_VQUAD: ('QUAD', vex("virtual_quad_exclude")),
                  HLA_VSEXT: ('SEXT', vex("virtual_sext_exclude")),
        }
        createVirtualElements(lat, vfams)
        lat_dict[msect] = lat
        
    lat0 = lat_dict.get(accdefault, None)
    if lat0 is None and len(lat_dict) > 0:
        _logger.debug("default submachine not defined, "
                      "use the first available one '%s'" % k)
        lat0 = lat_dict[sorted(lat_dict.keys())[0]]

    if lat0 is None: 
        raise RuntimeError("NO accelerator structures available")

    _lat = lat0
    _lattice_dict.update(lat_dict)
    if save_cache:
        selected_lattice_name = [k for (k,v) in _lattice_dict.iteritems()
                                 if _lat == v][0]
        saveCache(machine, _lattice_dict, selected_lattice_name)

    return lat0, lat_dict


def loadCache(machine_name):
    """load the cached machine"""
    global _lat, _lattice_dict
    raise NotImplemented("not implemented yet")

    cache_folderpath = HLA_ROOT
    cache_filepath = os.path.join(cache_folderpath,
                                  machine_name+'_lattices.cpkl')
    with open(cache_filepath,'rb') as f:
        selected_lattice_name = pickle.load(f)
        _lattice_dict = pickle.load(f)
    _lat = _lattice_dict[selected_lattice_name]
        

def saveCache(machine_name, lattice_dict, selected_lattice_name):
    """save machine as cache"""
    raise NotImplemented("not implemented yet")
    cache_folderpath = HLA_ROOT
    if not os.path.exists(cache_folderpath):
        os.mkdir(cache_folderpath)
    cache_filepath = os.path.join(cache_folderpath,
                                  machine_name+'_lattices.cpkl')
    with open(cache_filepath,'wb') as f:
        pickle.dump(selected_lattice_name,f,2)
        pickle.dump(lattice_dict,f,2)

def saveChannelFinderDb(dst, url = None):
    """save the channel finder as a local DB

    Parameters
    -----------
    url : str. channel finder URL, default use environment *HLA_CFS_URL*
    dst : str. destination db filename. 
    """
    cfa = ChannelFinderAgent()
    if url is None: url = os.environ.get('HLA_CFS_URL', None)
    if url is None: 
        raise RuntimeError("no URL defined for downloading")
    cfa.downloadCfs(url, property=[
                ('hostName', '*'), ('iocName', '*')], tagName='aphla.sys.*')
    cfa.exportSqlite(dst)


def createVirtualElements(vlat, vfams):
    """create common merged virtual element"""
    # virutal elements
    # a virtual bpm. its field is a "merge" of all bpms.
    iv = -100
    vpar = { 'virtual': 1, 'name': None, 'family': HLA_VFAMILY,
             'index': None }
    for vfam,famr in vfams.items():
        _logger.debug("creating virtual element {0} {1}".format(vfam, famr))
        # a virtual element. its field is a "merge" of all elems.
        fam, exfam = famr
        velem = [e for e in vlat.getElementList(fam) if e.name not in exfam]
        vpar.update({'name': vfam, 'index': iv})
        if velem:
            allvelem = merge(velem, **vpar)
            vlat.insertElement(allvelem, groups=[HLA_VFAMILY])
            allvelem.virtual = 1

        iv = iv - 100

def findCfaConfig(srcname, machine, submachines):
    """
    find the appropriate config for ChannelFinderAgent

    initialize the virtual accelerator 'V2SR', 'V1LTD1', 'V1LTD2', 'V1LTB' from

    - `${HLA_ROOT}/machine.csv`
    - `${HLA_ROOT}/machine.sqlite`
    - channel finder in ${HLA_CFS_URL} with tags `aphla.sys.submachine`
    - `machine.csv` with aphla package.
    - `machine.sqlite` with aphla package.

    Examples
    ---------
    >>> findCfaConfig("/data/nsls2v2.sqlite", "nsls2", "*")

    """

    cfa = ChannelFinderAgent()

    # if source is an explicit file name
    if os.path.exists(srcname):
        msg = "Creating lattice from explicit source '%s'" % srcname
        if srcname.endswith('.csv'):
            cfa.importCsv(srcname)
        elif srcname.endswith(".sqlite"):
            cfa.importSqlite(srcname)
        else:
            raise RuntimeError("Unknown explicit source '%s'" % srcname)
        return cfa

    # if only filename provided, searching known directories in order.
    # matching HLA_ROOT -> CF -> Package
    homesrc = os.path.join(HLA_ROOT, srcname)
    HLA_CFS_URL = os.environ.get('HLA_CFS_URL', None)

    if os.path.exists(homesrc + '.csv'):
        msg = "Creating lattice from '%s.csv'" % homesrc
        _logger.info(msg)
        cfa.importCsv(homesrc + '.csv')
    elif os.path.exists(homesrc + '.sqlite'):
        msg = "Creating lattice from '%s.sqlite'" % homesrc
        _logger.info(msg)
        cfa.importSqlite(homesrc + '.sqlite')
    elif os.environ.get('HLA_CFS_URL', None):
        msg = "Creating lattice from channel finder '%s'" % HLA_CFS_URL
        _logger.info(msg)
        cfa.downloadCfs(HLA_CFS_URL, property=[
                ('hostName', '*'), ('iocName', '*')], tagName='aphla.sys.*')
    elif resource_exists(__name__, os.path.join(machine, srcname + '.csv')):
        name = resource_filename(__name__, os.path.join(machine, 
                                                        srcname + '.csv'))
        #src_pkg_csv = conf.filename(cfs_filename)
        msg = "Creating lattice from '%s'" % name
        _logger.info(msg)
        cfa.importCsv(name)
    elif resource_exists(__name__, os.path.join(machine, srcname + '.sqlite')):
        name = resource_filename(__name__, os.path.join(machine, 
                                                        srcname + '.sqlite'))
        msg = "Creating lattice from '%s'" % name
        _logger.info(msg)
        cfa.importSqlite(name)
        #for k,v in _db_map.iteritems(): cfa.renameProperty(k, v)
    else:
        _logger.error("Lattice data are available for machine '%s'" % machine)
        raise RuntimeError("Failed at loading data file '%s' from '%s'" % (
            machine, srcname))

    return cfa

def createLattice(latname, pvrec, systag, desc = 'channelfinder', 
                  vbpm = True, vcor = True):
    """
    create a lattice from channel finder data

    Parameters
    -----------
    name: lattice name, e.g. 'SR', 'LTD'
    pvrec: list of pv records `(pv, property dict, list of tags)`
    systag: process records which has this systag. e.g. `aphla.sys.SR`
    desc: description is this lattice
    
    Returns
    ---------
    lat : the :class:`~aphla.lattice.Lattice` type.
    """

    _logger.debug("creating '%s':%s" % (latname, desc))
    _logger.debug("%d pvs found in '%s'" % (len(pvrec), latname))
    # a new lattice
    lat = Lattice(latname, desc)
    for rec in pvrec:
        _logger.debug("{0}".format(rec))
        # skip if there's no properties.
        if rec[1] is None: continue
        if rec[0] and systag not in rec[2]: continue
        #if rec[1].get("system", "") != latname: continue
        if 'name' not in rec[1]: continue
        #print "PASSED"
        prpt = rec[1]
        if 'se' in prpt:
            prpt['sb'] = float(prpt['se']) - float(prpt.get('length', 0))
        name = prpt.get('name', None)

        #_logger.debug("{0} {1} {2}".format(rec[0], rec[1], rec[2]))

        # find if the element exists.
        elem = lat._find_exact_element(name=name)
        if elem is None:
            _logger.debug("new element: '%s'" % name)
            try:
                elem = CaElement(**prpt)
                gl = [g.strip() for g in prpt.get('groups', [])]
                elem.group.update(gl)
            except:
                _logger.error("Error: creating element '{0}' with '{1}'".format(name, prpt))
                raise
            
            #print "inserting:", elem
            #lat.appendElement(elem)
            lat.insertElement(elem)
        # 
        if HLA_VFAMILY in prpt.get('group', []): elem.virtual = 1

        handle = prpt.get('handle', '').lower()
        if handle == 'get': prpt['handle'] = 'readback'
        elif handle == 'put': prpt['handle'] = 'setpoint'

        handle = prpt.get('handle', '').lower()
        if handle == 'get': prpt['handle'] = 'READBACK'
        elif handle == 'put': prpt['handle'] = 'SETPOINT'

        pv = rec[0]
        if pv: elem.updatePvRecord(pv, prpt, rec[2])

    # group info is a redundant info, needs rebuild based on each element
    lat.buildGroups()
    # !IMPORTANT! since Channel finder has no order, but lat class has
    lat.sortElements()
    lat.circumference = lat[-1].se if lat.size() > 0 else 0.0
    
    _logger.debug("mode {0}".format(lat.mode))
    _logger.debug("'%s' has %d elements" % (lat.name, lat.size()))
    for g in sorted(lat._group.keys()):
        _logger.debug("lattice '%s' group %s(%d)" % (
                lat.name, g, len(lat._group[g])))
    
    return lat


def setGoldenLattice(lat, h5fname, grp = "golden"):
    import h5py
    g = h5py.File(h5fname, 'r')[grp]
    unitsys = g['value'].attrs['unitsys']
    if unitsys == '': unitsys = None
    for i,elemname in enumerate(g['element']):
        elem = lat.getElementList(elemname)
        if not elem: continue
        elem[0].setGolden(g['field'][i], g['value'][i], unitsys=unitsys)
    # the waveform ... ignored now


def use(lattice):
    """
    switch to a lattice

    use :func:`~hla.machines.lattices` to get a dict of lattices and its mode
    name
    """
    global _lat, _lattice_dict
    if isinstance(lattice, Lattice):
        _lat = lattice
    elif lattice in _lattice_dict:
        _lat = _lattice_dict[lattice]
    else:
        raise ValueError("no lattice %s was defined" % lattice)

def getLattice(lat = None):
    """
    return the lattice with given name, if None returns the current lattice.

    a :class:`~aphla.lattice.Lattice` object with given name. return the
    current lattice by default.

    .. seealso:: :func:`~aphla.machines.lattices`
    """
    if lat is None:  return _lat

    global _lattice_dict
    return _lattice_dict.get(lat, None)

def lattices():
    """
    get a list of available lattices

    Examples
    --------
    >>> lattices()
      [ 'LTB', 'LTB-txt', 'SR', 'SR-txt']
    >>> use('LTB-txt')

    """
    return _lattice_dict.keys()


def machines():
    """all available machines"""
    from pkg_resources import resource_listdir, resource_isdir
    return [d for d in resource_listdir(__name__, ".") 
            if resource_isdir(__name__, d)]

def saveSnapshot(fname, lats):
    """save snapshot of a list of lattices

    - fname output file name
    - lats list/str lattice name

    The not-found lattice will be ignored.
    """
    import h5py
    livelats = []
    if lats is None:
        livelats.append(getLattice(lats))
    elif isinstance(lats, (str, unicode)):
        livelats.append(getLattice(lats))
    elif isinstance(lats, (list, tuple)):
        livelats.extend([getLattice(lat) for lat in lats])
    
    f = h5py.File(fname, 'w')
    f.close()

    for lat in livelats:
        if lat is None: continue
        catools.save_lat_epics(fname, lat, mode='a')

