"""
In ``aphla`` one machine includes several accelerator structure, e.g. "nsls2v2" is a machine with several submachine or lattice V1LTD, V1LTB, V2SR.

Submachines are also called lattice in ``aphla``. Each lattice has a list of elements, magnet or instrument. The submachines/lattices can share elements. 
"""

from ..unitconv import *
from ..element import *
from ..apdata import *
from ..lattice import Lattice
from ..chanfinder import ChannelFinderAgent
from ..resource import getResource

import os
import glob
from pkg_resources import resource_string, resource_exists, resource_filename
#from pvlist import vsr_pvlist
import cPickle as pickle

import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
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
# unless %HOME% is set on Windows, which is not the case by default.

_lattice_dict = {}

# the current lattice
_lat = None

def init(machine, submachines = "*", **kwargs):
    load(machine, submachines = submachines, **kwargs)

def load(machine, submachines = "*", **kwargs):
    """
    load submachine lattices in machine

    :param machine: the exact name of machine
    :param submachine: pattern of sub machines
    :param use_cache: optional bool, default False, use cache
    :param save_cache: optional bool, default False, save cache
    """
    
    use_cache = kwargs.get('use_cache',False)
    save_cache = kwargs.get('save_cache',False)
    
    if use_cache:
        try:
            loadCache(machine)
        except:
            print('Lattice initialization using cache failed. ' +
                  'Will attempt initialization with other method(s).')
            save_cache = True
        else:
            # Loading from cache was successful.
            return
        
    #importlib.import_module(machine, 'machines')
    logger.debug("importing '%s'" % machine)
    m = __import__(machine, globals(), locals(), [], -1)
    lats, lat = m.init_submachines(machine, submachines, **kwargs)

    global _lat, _lattice_dict
    _lattice_dict.update(lats)
    _lat = lat

    if save_cache:
        selected_lattice_name = [k for (k,v) in _lattice_dict.iteritems()
                                 if _lat == v][0]
        saveCache(machine, _lattice_dict, selected_lattice_name)
        

def loadCache(machine_name):
    
    global _lat, _lattice_dict
    
    cache_folderpath = os.path.join(HOME,'.hla')
    cache_filepath = os.path.join(cache_folderpath,
                                  machine_name+'_lattices.cpkl')
    with open(cache_filepath,'rb') as f:
        selected_lattice_name = pickle.load(f)
        _lattice_dict = pickle.load(f)
    _lat = _lattice_dict[selected_lattice_name]
        

def saveCache(machine_name, lattice_dict, selected_lattice_name):
    
    cache_folderpath = os.path.join(HOME,'.hla')
    if not os.path.exists(cache_folderpath):
        os.mkdir(cache_folderpath)
    cache_filepath = os.path.join(cache_folderpath,
                                  machine_name+'_lattices.cpkl')
    with open(cache_filepath,'wb') as f:
        pickle.dump(selected_lattice_name,f,2)
        pickle.dump(lattice_dict,f,2)

def findCfaConfig(srcname, machine, submachines):
    """
    find the appropriate config for ChannelFinderAgent

    initialize the virtual accelerator 'V2SR', 'V1LTD1', 'V1LTD2', 'V1LTB' from

    - `${HOME}/.hla/us_nsls2v2.sqlite`
    - channel finder in ${HLA_CFS_URL}
    - `us_nsls2v2.sqlite` with aphla package.

    """
    cfa = ChannelFinderAgent()

    # if source is an explicit file name
    if os.path.exists(srcname):
        msg = "Creating lattice from explicit source '%s'" % srcname
        if srcname.endswith('.csv'):
            cfa.importCsv(srcname)
        elif srcname.endswith(".sqlite"):
            cfa.importSqliteDb(srcname)
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
        cfa.downloadCfs(HLA_CFS_URL, tagName='aphla.sys.*')
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
                elem = CaElement(**prpt)
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


def machines():
    """all available machines"""
    from pkg_resources import resource_filename, resource_listdir, resource_isdir
    return [d for d in resource_listdir(__name__, ".") if resource_isdir(__name__, d)]

