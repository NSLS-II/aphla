"""
Core APHLA Libraries
---------------------

Defines the fundamental routines.
"""

# :author: Lingyun Yang

import logging
import numpy as np
import time
import os
from fnmatch import fnmatch
from datetime import datetime
from catools import caget, caput, CA_OFFLINE, savePvData
import machines
import element
import itertools

logger = logging.getLogger(__name__)

#__all__ = [
#    'addGroup', 'addGroupMembers', 'eget',  
#    'getBeamlineProfile', 'getBeta', 
#    'getBpms', 'getChromaticityRm', 'getChromaticity', 'getClosest', 
#    'getCurrent', 'getCurrentMode', 'getDispersion', 'getDistance', 
#    'getElements', 'getEta', 'getFastOrbit', 'getFftTune', 
#    'getGroupMembers', 'getGroups', 'getLocations', 'getModes', 
#    'getNeighbors', 'getOrbit', 'getPhase', 'getPvList', 'getRfFrequency', 
#    'getRfVoltage', 'getStepSize', 'getTbtOrbit', 'getTuneRm', 
#    'getTune', 'getTunes', 
#    'removeGroup', 'removeGroupMembers', 'putRfFrequency',
#    'stepRfFrequency', 
#    'waitStableOrbit', 
#]

def setEnergy(Ek):
    """set energy (MeV) for current submachine

    see also :func:`setEnergy`
    """
    machines._lat.Ek = Ek

def getEnergy():
    """get current submachine beam energy (MeV)

    see also :func:`setEnergy`
    """
    return machines._lat.Ek

def getOutputDir():
    """get the output data dir for the current lattice""" 
    return machines._lat.OUTPUT_DIR

# current
def getCurrent(name='dcct', field='I', unitsys=None):
    """Get the current from the first DCCT element

    :param str name: the name of DCCT, default 'dcct'
    :param str field: the field of DCCT, default 'value'
    :param unit: the desired unit sytem, default None, no conversion.

    returns None if no 'dcct' element found

    seealso :func:`eget`
    """
    _current = getElements(name)
    if _current: return _current[0].get(field, unitsys=unitsys)
    else: return None

# rf
def getRfFrequency(name = 'rfcavity', field = 'f', unitsys=None, handle="readback"):
    """
    Get the frequency from the first 'RFCAVITY' element.

    seealso :func:`eget`, :func:`getRfVoltage`, :func:`putRfFrequency`
    """
    _rf = getElements(name)
    if _rf: return _rf[0].get(field, unitsys=unitsys, handle=handle)
    else: return None


def setRfFrequency(f, name = 'rfcavity', field = 'f', unitsys=None):
    """set the rf frequency for the first 'RFCAVITY' element"""
    _rf = getElements(name)
    if _rf: return _rf[0].put(field, f, unitsys=unitsys)
    else: raise RuntimeError("element '%s' not found" % name)

def getRfVoltage(name = 'rfcavity', field='v', unitsys=None):
    """
    Get the voltage of the first 'RFCAVITY' element

    :param str name: cavity name
    :param str field: field name for voltage, default 'v'
    :param str unit: unit system

    return None if no element found
    """
    _rf = getElements(name)
    if _rf: return _rf[0].get(field, unitsys=unitsys)
    else: return None

def stepRfFrequency(df = 0.010):
    """
    change one step of the first 'RFCAVITY' element

    seealso :func:`getRfFrequency`, :func:`putRfFrequency`

    .. warning:: 

      Need check the unit for real machine
    """
    f0 = getRfFrequency()
    putRfFrequency(f0 + df)

def _reset_rf():
    """
    reset the RF requency, used only in Tracy-II simulator to zero the orbit
    """
    _rf, = getElements('RFCAVITY')
    _rf.f = 499.680528631


#
#

def _reset_trims(verbose=False):
    """reset all trims in group *HCOR* and *VCOR* """
    trimx = machines._lat.getGroupMembers(['*', 'HCOR'], op='intersection')
    trimy = machines._lat.getGroupMembers(['*', 'VCOR'], op='intersection')
    pv = []
    for e in trimx:
        pv.extend(e.pv(field='x', handle='setpoint'))
    for e in trimy:
        pv.extend(e.pv(field='y', handle='setpoint'))
    if not pv:
        raise ValueError("no pv for trims found")
    
    if verbose:
        for p in pv: 
            print p, caget(p),
            caput(p, 0.0, wait=True)
            print caget(p)
    else:
        caput(pv, 0.0)

    logger.info("reset all trims")
    #print "DONE"


def _levenshtein_distance(first, second):
    """Find the Levenshtein distance between two strings."""
    if len(first) > len(second):
        first, second = second, first
    if len(second) == 0:
        return len(first)
    first_length = len(first) + 1
    second_length = len(second) + 1
    distance_matrix = np.zeros((first_length, second_length), 'd')
    for i in range(first_length):
        distance_matrix[i, 0] = i
    for j in range(second_length):
        distance_matrix[0, j]=j
    for i in xrange(1, first_length):
        for j in range(1, second_length):
            deletion = distance_matrix[i-1, j] + 1
            insertion = distance_matrix[i, j-1] + 1
            substitution = distance_matrix[i-1, j-1]
            if first[i-1] != second[j-1]:
                substitution += 1
            distance_matrix[i, j] = min(insertion, deletion, substitution)
    return distance_matrix[first_length-1, second_length-1]


def getElements(group, include_virtual=False):
    """searching for elements.

    this calls :func:`~aphla.lattice.Lattice.getElementList` of the current
    lattice.

    The default does not include virtual element.

    Parameters
    -----------
    group : str, list. a list of element name or a name pattern.
    include_virtual : include virtual element or not.

    Returns
    ---------
     elemlist : a list of matched element objects.
    
    Examples
    ----------
    >>> getElements('NO_SUCH_ELEMENT')
      []
    >>> getElements('PH1G2C30A')
      [PH1G2C30A:BPM @ sb=4.935000]
    >>> getElements('BPM')
      ...
    >>> getElements('F*G1C0*')
      ...
    >>> getElements(['FH2G1C30A', 'FH2G1C28A'])
      ...

    """

    # return the input if it is a list of element object
    if isinstance(group, element.AbstractElement):
        return [group]
    elif isinstance(group, (list, tuple)):
        if all([isinstance(e, element.AbstractElement) for e in group]):
            return group

    elems = machines._lat.getElementList(group)
    ret = []
    for e in elems:
        if e is None: 
            ret.append(e)
            continue

        if not include_virtual and e.virtual: continue
        ret.append(e)

    return ret

def getExactElement(elemname):
    """find the element with exact name"""
    return machines._lat._find_exact_element(name=elemname)

def eget(elem, fields = None, **kwargs):
    raise RuntimeError("deprecated! please revise it to `fget(elem,field)`")

def fget(elem, field, **kwargs):
    """get elements field values for a family

    Parameters
    -----------
    elem : str, list. element name, name list, pattern or object list
    fields : str, list. field name or name list
    handle : str, optional, default "readback"
    unitsys : str, optional, default None, unit system, 
    Examples
    ---------
    >>> eget('DCCT', 'value')
    >>> eget('BPM', 'x')
    >>> eget('p*c30*', 'x')

    >>> bpm = getElements('p*c30*')
    >>> eget(bpm, 'x', handle="setpoint", unitsys = None)
    """

    handle = kwargs.pop('handle', "readback")
    unitsys = kwargs.pop("unitsys", None)

    elst = getElements(elem)
    if not elst: return None

    v = [e.pv(field=field, handle=handle) for e in elst]
    assert len(set([len(pvl) for pvl in v])) <= 1, \
        "Must be exact one pv for each field"
    pvl = reduce(lambda x,y: x + y, v)

    dat = caget(pvl, **kwargs)
    if unitsys is None: return dat

    ret = [e.convertUnit(field, dat[i], None, unitsys)
               for i,e in enumerate(elst)]
    return ret

        
def getPvList(elem, field, handle = 'readback', **kwargs):
    """return a pv list for given element or element list

    Parameters
    ------------
    elem : element pattern, name list or CaElement object list
    field : e.g. 'x', 'y', 'k1'
    handle : 'readback' or 'setpoint'

    Keyword arguments:

      - *first_only* (False) use only the first PV for each element. 
      - *compress_empty* (False) remove element with no PV.

    :Example:

      >>> getPvList('p*c30*', 'x')

    This can be simplified as::

      [e.pv(field) for e in getElements(elem) if field in e.fields()]

    extract the pv only if the element has that field (compress_empty=True).

      [e.pv(field) if field in e.fields() else None for e in getElements(elem)]

    put a None in the list if the field is not in that element

    *elem* accepts same input as :func:`getElements`
    """
    first_only = kwargs.get('first_only', False)
    compress_empty = kwargs.get('compress_empty', False)

    # did not check if it is a BPM 
    elemlst = getElements(elem)
    pvlst = []
    for elem in elemlst:
        if not isinstance(elem, element.CaElement):
            raise ValueError("element '%s' is not CaElement" % elem.name)
        #
        pvs = elem.pv(field=field, handle=handle)
        if len(pvs) == 0 and not compress_empty:
            raise ValueError("element '%s' has no readback pv" % elem.name)
        elif len(pvs) > 1 and not first_only:
            raise ValueError("element '%s' has more %d (>1) pv" % 
                             (elem.name, len(pvs)))

        pvlst.append(pvs[0])

    return pvlst


def getLocations(group):
    """
    Get the location of a group, i.e. a family, an element or a list of
    elements

    Examples
    ---------

    >>> s = getLocations('BPM')
    >>> s = getLocations(['PM1G4C27B', 'PH2G2C28A'])

    It has a same input as :func:`getElements` and accepts group name,
    element name, element name pattern and a list of element names.
    """
    
    elem = getElements(group)
    if isinstance(elem, (list, set, tuple)):
        return [e.sb for e in elem]
    else: return elem.sb

def addGroup(group):
    """
    add a new group to current submachine.

    *group* should be plain string, characters in \[a-zA-Z0-9\_\]

    raise *ValueError* if *group* is an illegal name.

    it calls :func:`~aphla.lattice.Lattice.addGroup` of the current lattice.
    """
    return machines._lat.addGroup(group)

def removeGroup(group):
    """
    Remove a group if it is empty. It calls
    :func:`~aphla.lattice.Lattice.removeGroup` of the current lattice.
    """
    machines._lat.removeGroup(group)

def addGroupMembers(group, member):
    """
    add new members to an existing group

    ::

      >>> addGroupMembers('HCOR', 'CX1')
      >>> addGroupMembers('HCOR', ['CX1', 'CX2']) 

    it calls :meth:`~aphla.lattice.Lattice.addGroupMember` of the current
    lattice.
    """
    if isinstance(member, str):
        machines._lat.addGroupMember(group, member)
    elif isinstance(member, list):
        for m in member:
            machines._lat.addGroupMember(group, m)
    else:
        raise ValueError("member can only be string or list")

def removeGroupMembers(group, member):
    """
    Remove a member from group

    ::

      >>> removeGroupMembers('HCOR', 'CX1')
      >>> removeGroupMembers('HCOR', ['CX1', 'CX2'])

    it calls :meth:`~aphla.lattice.Lattice.removeGroupMember` of the current
    lattice.
    """
    if isinstance(member, str):
        machines._lat.removeGroupMember(group, member)
    elif isinstance(member, list):
        for m in member: machines._lat.removeGroupMember(group, m)
    else:
        raise ValueError("member can only be string or list")


def getGroups(element = '*'):
    """
    Get all groups own these elements, '*' returns all possible groups,
    since it matches every element
    
    it calls :func:`~aphla.lattice.Lattice.getGroups` of the current lattice.
    """
    return machines._lat.getGroups(element)


def getGroupMembers(groups, op = 'intersection', **kwargs):
    """
    Get all elements in a group. If group is a list, consider which op:

    - op = "union", consider elements in the union of the groups
    - op = "intersection", consider elements in the intersect of the groups

    it calls :func:`~aphla.lattice.Lattice.getGroupMembers` of the current
    lattice.
    """
    return machines._lat.getGroupMembers(groups, op, **kwargs)


def getNeighbors(element, group, n = 3):
    """
    Get a list of n objects in *group* before and after *element* 

    it calls :meth:`~aphla.lattice.Lattice.getNeighbors` of the current
    lattice to get neighbors.

    Parameters
    -----------
    element: str, object. the central element name
    group: str, the neighbors belong to

    Returns
    --------
    elems : a list of element in given group with size 2*n+1. The list is
        sorted along s (the beam direction).


    Examples
    ----------
    >>> getNeighbors('X', 'BPM', 2) # their names are ['1','2','X', '3', '4']
    >>> getNeighbors('QC', 'QUAD', 1) # their names are ['Q1', 'QC', 'Q2']
    >>> el = hla.getNeighbors('PH2G6C25B', 'P*C10*', 2)
    >>> [e.name for e in el]
      ['PL2G6C10B', 'PL1G6C10B', 'PH2G6C25B', 'PH1G2C10A', 'PH2G2C10A']
    >>> [e.sb for e in el]
      [284.233, 286.797, 678.903, 268.921, 271.446]

    """

    if isinstance(element, (str, unicode)):
        return machines._lat.getNeighbors(element, group, n)
    else:
        return machines._lat.getNeighbors(element.name, group, n)
        

def getClosest(element, group):
    """
    Get the closest neighbor in *group* for an element

    It calls :meth:`~aphla.lattice.Lattice.getClosest`

    Parameters
    -----------
    element: str, object. the element name or object
    group: str, the closest neighbor belongs to this group

    Examples
    ----------
    >>> getClosest('pm1g4c27b', 'BPM') # find the closest BPM to 'pm1g4c27b'

    """
    if isinstance(element, (str, unicode)):
        return machines._lat.getClosest(element, group)
    else:
        return machines._lat.getClosest(element.name, group)

def getBeamlineProfile(**kwargs):
    """
    return the beamline profile from sposition sb to se

    :param float s1: s-begin
    :param float s2: s-end, None means the end of beamline.

    it calls :meth:`~aphla.lattice.Lattice.getBeamlineProfile` of the
    current lattice.
    """
    return machines._lat.getBeamlineProfile(**kwargs)


def getDistance(elem1, elem2, absolute=True):
    """
    return distance between two element name

    Parameters
    -----------
    elem1: str, object. name or object of one element
    elem2: str, object. name or object of the other element
    absolute: bool. return s2 - s1 or the absolute value.

    Raises
    -------
    it raises RuntimeError if None or more than one elements are found
    """
    e1 = getElements(elem1)
    e2 = getElements(elem2)

    if len(e1) != 1 or len(e2) != 1:
        raise RuntimeError("elements are not uniq: %d and %d" % \
                           (len(e1), len(e2)))

    ds = e2[0].sb - e1[0].sb
    C = machines._lat.circumference
    if machines._lat.loop and C > 0:
        while ds < -C: ds = ds + C
        while ds > C: ds = ds - C
    if absolute: return abs(ds)
    else: return ds

#
#
def getTwiss(names, columns, **kwargs):
    """
    get the twiss data
    - names, a list of element sames or a name pattern.
    - columns, a sublist of [s, betax(y), alphax(y), gammax(y), etax(y), phix(y)]
    - source, optional, default database (no other source yet)

    example:

    >>> getTwiss("p*", ["s", "betax", "betay"])
    >>> getTwiss(["p1", "p2"], ["s", "etax"])

    Unlike getElements, it will not accept group name "BPM", "QUAD", ...
    """

    col = [c for c in columns]
    src = kwargs.pop("source", "database")
    if src == "database":
        if not machines._lat._twiss:
            logger.error("ERROR: no twiss data loaded")
            return None
        return machines._lat._twiss.get(names, col=col)
    elif src == "VA":
        vas = getElements("VA")
        if not vas: return None
        twiss = vas[kwargs.get("iva", 0)]
        if isinstance(names, (str, unicode)):
            namelst = [i for i,s in enumerate(twiss.names) if fnmatch(s, names)]
        elif isinstance(names, (list, tuple)):
            namelst = [i for i,s in enumerate(twiss.names) if s in names]
        else:
            raise ValueError("names must be string or list of element names")
        dat = np.zeros((len(namelst), len(columns)), 'd')
        for i,c in enumerate(columns):
            d = twiss.get(c, unitsys=None)
            dat[:,i] = [d[j] for j in namelst]
        return dat
    else:
        return None


def getTwissAt(s, columns, **kwargs):
    """
    similar to getTwiss, but at specific location
    """
    col = [c for c in columns]
    src = kwargs.pop("source", "database")
    if src == "database":
        if not machines._lat._twiss:
            logger.error("ERROR: no twiss data loaded")
            return None
        return machines._lat._twiss.at(s, col=col)
    else:
        return [None] * len(columns)

    
def getPhi(group, **kwargs):
    """
    get the phase from stored data

    this calls :func:`~aphla.apdata.TwissData.get` of the current twiss data.
    """
    col = ['phix', 'phiy']
    if kwargs.pop('spos', False): col.append('s')
    return getTwiss(group, col=col, **kwargs)


def getPhase(group, **kwargs):
    """see :func:`getPhi`"""
    return getPhi(group, **kwargs)

##
def getAlpha(group, **kwargs):
    """
    get the phase from stored data

    this calls :func:`~aphla.apdata.TwissData.get` of the current twiss data.
    """
    col = ['alphax', 'alphay']
    if kwargs.pop('spos', False): col.append('s')
    return getTwiss(group, col, **kwargs)
#
#
def getBeta(group, **kwargs):
    """get the beta function of *group* from stored data.
    
    Parameters
    -----------
    src : str.
        'database' from database, 'VA' from 'virtualacc' element of virtual accelerator

    Examples
    ---------
    >>> getBeta('q*', spos = False)

    """
    col = ['betax', 'betay']
    if kwargs.pop('spos', False): col.append('s')
    return getTwiss(group, col, **kwargs)


def getDispersion(group, **kwargs):
    """
    get the dispersion

    this calls :func:`~aphla.hlalib.getEta`.
    """
    return getEta(group, **kwargs)


def getEta(group, **kwargs):
    """get the dispersion from stored data

    Parameters
    -----------
    source : str. 
        'database' from database; 'VA' from virtual accelerator where a 'twiss'
        element must exist.

    Examples
    --------
    >>> getEta('p*', spos = True, source = 'database')
    >>> getEta(['BPM1', 'BPM2'])

    """

    col = ['etax', 'etay']
    if kwargs.pop('spos', False): col.append('s')
    return getTwiss(group, col, **kwargs)


def getChromaticity(source='database'):
    """
    get chromaticity from ["database"]
    """
    if source == 'database':
        return machines._lat.getChromaticities()
    elif source == "VA":
        vas = getElements('VA')
        if not vas: return None
        twiss = vas[kwargs.get("iva", 0)]
        return twiss.chromx, twiss.chromy        
    else:
        raise ValueError("Unknown source: '%s'" % source)


def getTunes(source='machine', **kwargs):
    """
    get tunes from ['machine', 'database', "VA"]
    """
    if source == 'machine':
        # return only the first matched element
        nu = getElements('tune')
        if not nu:
            raise RuntimeError("can not find element 'tune'") 
        return nu[0].x, nu[0].y
    elif source == 'database':
        return machines._lat.getTunes()
    elif source == "VA":
        vas = getElements('VA')
        if not vas: return None
        twiss = vas[kwargs.get("iva", 0)]
        return twiss.nux, twiss.nuy
    else:
        raise ValueError("Unknow source: '%s'" % source)


def getTune(source='machine', plane = 'h'):
    """get one of the tune, 'h' or 'v'

    Examples
    ---------
    >>> getTune(plane='v')

    """
    nux, nuy = getTunes(source)
    if plane == 'h': return nux
    elif plane == 'v': return nuy
    else:
        raise ValueError("plane must be either h or v")


def _getFftTune(plane = 'hv', mode = ''):
    """get tune from FFT

    .. warning::

      Not Implemented Yet
    """
    raise NotImplementedError()
    return None


def getChromaticityRm(mode, phase, info):
    """
    Not implemented yet
    """
    raise NotImplementedError()
    return None, None


def getTuneRm(mode):
    """
    Not implemented yet, see `measTuneRm`
    """
    raise NotImplementedError()


def getBpms():
    """
    return a list of bpms object.

    this calls :func:`~aphla.lattice.Lattice.getGroupMembers` of current
    lattice and take a "union".
    """
    return machines._lat.getGroupMembers('BPM', op='union')


def getQuads():
    """
    return a list of bpms object.

    this calls :func:`~aphla.lattice.Lattice.getGroupMembers` of current
    lattice and take a "union".
    """
    return machines._lat.getGroupMembers('QUAD', op='union')


def getOrbit(pat = '', spos = False):
    """
    Return orbit

    :Example:

      >>> getOrbit()
      >>> getOrbit('*')
      >>> getOrbit('*', spos=True)
      >>> getOrbit(['PL1G6C24B', 'PH2G6C25B'])

    If *pat* is not provided, use the group read of every BPMs, this is
    faster than read BPM one by one with getOrbit('*').

    The return value is a (n,4) or (n,2) 2D array, where n is the number
    of matched BPMs. The first two columns are x/y orbit, the last two
    columns are s location for x and y BPMs. returns (n,3) 2D array if x/y
    have same *s* position.

    When the element is not found or not a BPM, return NaN in its positon.
    """
    if not pat:
        bpm = machines._lat._find_exact_element(machines.HLA_VBPM)
        n = len(bpm.sb)
        if spos:
            ret = np.zeros((n, 3), 'd')
            ret[:,2] = bpm.sb
        else:
            ret = np.zeros((n,2), 'd')
        ret[:,0] = bpm.x
        ret[:,1] = bpm.y
        return ret

    # need match the element name
    if isinstance(pat, (unicode, str)):
        elem = [e for e in getBpms() if fnmatch(e.name, pat)]
        if not elem: return None
        ret = [[e.x, e.y, e.sb] for e in elem]
    elif isinstance(pat, (list,)):
        elem = machines._lat.getElementList(pat)
        if not elem: return None
        bpm = [e.name for e in getBpms()]
        ret = []
        for e in elem:
            if not e.name in bpm: ret.append([None, None, None])
            else: ret.append([e.x, e.y, e.sb])
    if not ret: return None
    obt = np.array(ret, 'd')
    if not spos: return obt[:,:2]
    else: return obt


def getOrbitResponseMatrix():
    """
    returns m, list of (bpmname, field) and list of (corname, field). field is
    'x' or 'y'
    """
    orm = machines._lat.ormdata
    return orm.m, orm.bpm, orm.cor


def _getTbtOrbit(**kwargs):
    """
    return turn-by-turn BPM data.

    - *field* ['A', 'B', 'C', 'D', 'X', 'Y', 'S', 'Q'], each has the RMS value: 'rmsA'-'rmsQ'
    """
    field = kwargs.get('field', 'X')
    pref = 'LTB:BI{BPM:1}' + 'TBT-'
    return caget(pref + field)
    
def _getFastOrbit(**kwargs):
    """
    return fast 10kHz turn-by-turn BPM data.

    - *field* ['A', 'B', 'C', 'D', 'X', 'Y', 'S', 'Q'], each has the RMS value: 'rmsA'-'rmsQ'
    """
    field = kwargs.get('field', 'X')
    pref = 'LTB:BI{BPM:1}' + 'FA-'
    return caget(pref + field)


def _reset_bpm_offset():
    bpms = getElements('BPM')
    pvs = []
    for b in bpms:
        #print b.pv(tags=['aphla.offset', 'aphla.eput'])
        pvs.extend(b.pv(tags=['aphla.offset', 'aphla.eput']))
    if pvs: caput(pvs, 0.0)
    logger.info("Reset the bpm offset")


def _reset_quad():
    #raise RuntimeError("does not work for SR above V1SR")

    qtag = {'H2': (1.47765, 30), 
            'H3': (-1.70755, 30),
            'H1': (-0.633004, 30),
            'M1': (-0.803148, 60),
            'M2': (1.2223, 60),
            'L2': (1.81307, 30),
            'L3': (-1.48928, 30),
            'L1': (-1.56216, 30)}
    
    for tag, v in qtag.items():
        qlst = getElements('Q%s' % tag)
        qval, qnum = v
        if len(qlst) != qnum:
            raise ValueError("ring does not have exactly %d %s (%d)" % \
                                 (qnum, tag, len(qlst)))
        for q in qlst:
            q.value = qval

def waitStableOrbit(reforbit, **kwargs):
    """
    set pv to a value, waiting for timeout or the std of monipv is greater
    than diffstd

    - *diffstd* = 1e-7
    - *minwait* = 2
    - *maxwait* =30
    - *step* = 2
    - *diffstd_list* = False
    """

    diffstd = kwargs.get('diffstd', 1e-7)
    minwait = kwargs.get('minwait', 2)
    maxwait = kwargs.get('maxwait', 30)
    step    = kwargs.get('step', 2)
    diffstd_list = kwargs.get('diffstd_list', False)
    verbose = kwargs.get('verbose', 0)

    t0 = time.time()
    time.sleep(minwait)
    dv = getOrbit() - reforbit
    dvstd = [dv.std()]
    timeout = False

    while dv.std() < diffstd:
        time.sleep(step)
        dt = time.time() - t0
        if dt  > maxwait:
            timeout = True
            break
        dv = getOrbit() - reforbit
        dvstd.append(dv.std())

    if diffstd_list:
        return timeout, dvstd


def _wait_for_lock(tag, maxwait=60):
    """
    wait until the virtual accelerator is available to me.
    """
    print "# Locking the mathine for userid=%d" % tag
    if tag == 0:
        raise ValueError("you tag (=%d)  must be > 0." % tag)

    t0 = time.time()
    while caget('SVR:LOCKED') > 0:
        print "# waiting ... for user %d ..." % int(caget('SVR:LOCKED'))
        time.sleep(1)
        if time.time() - t0 > maxwait: break

    if caget('SVR:LOCKED') == 0:
        caput('SVR:LOCKED', tag)
    else:
        raise ValueError("can not get the writting permission to virtual accelerator")

def _release_lock(tag):
    if caget('SVR:LOCKED') == 0:
        raise ValueError("some one already reset the lock")
    if caget('SVR:LOCKED') != tag:
        raise ValueError("it is not locked by me, abort")

    caput('SVR:LOCKED', 0)
    print "released the lock for userid=%d" % tag



def waitChanged(elemlst, fields, v0, **kwargs):
    """
    set pvs and waiting until the setting takes effect

    :param elemlst: element list
    :type elemlist: list of Elements
    :param v0: old values
    :type v0: list
    :param diffstd: threshold value of effective change of *pvmonitors*.
    :param wait: waiting time for initial, each step and final (seconds)
    :param maxtrial: maximum trial before return.
    :param unit: unit of field
    :param full: return total trials

    :return: whether pvmonitors change significant enough.
    :rtype: bool

    It sets the pvs with new values and tests the monitor values see if the
    changes are significant enough. This significance is measured by comparing
    the std of monitor value changes due to the *pvs* changes. If it exceeds
    *diffstd* then return, otherwise wait for *wait* seconds and test
    again. The maximum trial is *maxtrial*.

    It is good for ORM measurement where setting a trim and observing a list
    of BPM.
    """

    diffstd= kwargs.get('diffstd', 1e-6)
    wait = kwargs.get('wait', (2, 1, 0))
    maxtrial= kwargs.get('maxtrial', 20)
    full = kwargs.get('full', False)
    unitsys = kwargs.get('unitsys', None)

    if CA_OFFLINE: 
        if full: return (True, 0)
        else: return True

    time.sleep(wait[0])

    ntrial = 0
    while True:
        v1 = np.ravel(eget(elemlst, fields, unitsys=unitsys))
        time.sleep(wait[1])
        ntrial = ntrial + 1
        if np.std(v1 - np.array(v0)) > diffstd: break
        if ntrial >= maxtrial: break

    time.sleep(wait[2])

    if full:
        if ntrial >= maxtrial: return (False, ntrial)
        else: return (True, ntrial)
    else: 
        if ntrial >= maxtrial: return False
        else: return True

def waitStable(elemlst, fields, maxstd, **kwargs):
    """
    set pvs and waiting until the setting takes effect

    :param elemlst: element list
    :type elemlist: list of Elements
    :param v0: old values
    :type v0: list
    :param diffstd: threshold value of effective change of *pvmonitors*.
    :param wait: waiting time for initial, each step and final (seconds)
    :param maxtrial: maximum trial before return.
    :param unit: unit of field

    :return: whether pvmonitors change significant enough.
    :rtype: bool

    It sets the pvs with new values and tests the monitor values see if the
    changes are significant enough. This significance is measured by comparing
    the std of monitor value changes due to the *pvs* changes. If it exceeds
    *diffstd* then return, otherwise wait for *wait* seconds and test
    again. The maximum trial is *maxtrial*.

    It is good for ORM measurement where setting a trim and observing a list
    of BPM.
    """

    wait = kwargs.get('wait', (2, 1, 0))
    maxtrial= kwargs.get('maxtrial', 3)
    unitsys = kwargs.get('unitsys', None)

    if CA_OFFLINE: return True

    time.sleep(wait[0])

    v = np.zeros((len(elemlst), maxtrial), 'd')
    for i in range(maxtrial):
        v[:,i] = np.ravel(eget(elemlst, fields, unitsys=unitsys))
        time.sleep(wait[1])

    time.sleep(wait[2])
    if np.average(np.std(v, axis=0)) < maxstd: return True
    else: return False
    


def saveLattice(**kwargs):
    """
    save lattice info to a HDF5 file.

    - output, output file name. If it is True, save to the default place with default filename.
    - lattice, default the current active lattice
    - subgroup, default "", used for output file name
    - elements, default "*"
    - notes, default ""

    returns the output file name.

    ::
        saveLattice(output=True, elements=["BEND", "COR", "QUAD", "SEXT"], notes="Good one")

    """
    # save the lattice
    output = kwargs.get("output", False)
    lat = kwargs.get("lattice", machines._lat)
    verbose = kwargs.get("verbose", 0)

    pvspl = []
    if kwargs.has_key("elements"):
        pvs = []
        for el in kwargs["elements"]:
            elems = lat.getElementList(el, virtual=False)
            pvs.extend(reduce(lambda a,b: a+b, [e.pv() for e in elems]))
            pvspl.extend(reduce(lambda a,b: a+b, 
                                [e.pv(handle="setpoint") for e in elems]))
    elif lat.arpvs is not None:
        pvs = [s.strip() for s in open(lat.arpvs, 'r').readlines()]
    else:
        elems = lat.getElementList("*", virtual=False)
        pvs = reduce(lambda a,b: a+b, [e.pv() for e in elems])
        pvspl = reduce(lambda a,b: a+b, 
                       [e.pv(handle="setpoint") for e in elems])

    if output is True:
        #t0 = datetime.now()
        #output = os.path.join(
        #    lat.OUTPUT_DIR, t0.strftime("%Y_%m"),
        #    t0.strftime("snapshot_%d_%H%M%S_") + "_%s.hdf5" % lat.name)
        output = outputFileName("snapshot", kwargs.get("subgroup",""))
    nlive, nead = savePvData(output, pvs, group=lat.name, pvsp = pvspl,
                             notes=kwargs.get("notes", ""))
    if verbose > 0:
        print "PV dead: %d, live: %d" % (nlive, ndead)
    return output


def putLattice(fname, **kwargs):
    """
    put saved lattice to real machine.

    - group: hdf5 group, default the current lattice name
    """
    # save the lattice
    group = kwargs.get("group", machines._lat.name)
    import h5py
    h5f = h5py.File(fname, 'r')
    grp = h5f[group]
    for k,v in grp.items():
        caput(k, v)


def outputFileName(group, subgroup, create_path = True):
    """generate the system default output data file name

    'Lattice/Year_Month/group/subgroup_Year_Month_Day_HourMinSec.hdf5'
    e.g. 'SR/2014_03/bpm/bpm_Fa_0_2014_03_04_145020.hdf5'

    if new directory is created, with permission "rwxrwxr-x"
    """
    # use the default file name
    import stat
    t0 = datetime.now()
    output_dir = ""
    for subdir in [machines.getOutputDir(), t0.strftime("%Y_%m"), group]:
        output_dir = os.path.join(output_dir, subdir)
        if not os.path.exists(output_dir):
            if create_path:
                logger.info("creating new directory: {0}".format(output_dir))
                os.mkdir(output_dir)
                os.chmod(output_dir, stat.S_ISGID | stat.S_IRWXU | stat.S_IRWXG | \
                         stat.S_IROTH | stat.S_IXOTH)
            else:
                raise RuntimeError("{0} does not exist".format(output_dir))

    fopt = subgroup + t0.strftime("%Y_%m_%d_%H%M%S.hdf5")
    return os.path.join(output_dir, fopt)


def calcTuneRm(quad, **kwargs):
    """
    calculate tune respose matrix

    quad - quadrupoles. same input as getElements.
    setpoint - default None, or a list of ("b1", raw_value, dval).

    In physics unit, dnu/dkl = beta/4pi. When asking for raw unit (in A), we
    need to have a setpoint for Quad and convert the unit dkl/dI to get
    dnu/dI.  We calculate dkl/dI by converting I0=raw_value and
    I1=raw_value+dval to kl0 and kl1, dkl/dI = (kl1-kl0)/(I1-I0).
    """
    unitsys = kwargs.get("unitsys", None)
    sp = kwargs.get("setpoint", None)

    qls = getElements(quad)
    bta = np.zeros((len(qls), 2), 'd')
    m = np.zeros((2, len(qls)), 'd')
    for i,q in enumerate(qls):
        # use beta at the center of quad
        bta[i,:] = getTwissAt((q.sb + q.se)/2.0, ["betax", "betay"])
        # need to check if focusing or defocusing
        try:
            k1l = q.get("b1", handle="golden", unitsys="phy")
        except:
            raise RuntimeError(
                "can not determin defocusing/focusing for {}".format(q.name))
        if sp is None:
            fld = "b1"
            I0 = q.convertUnit(fld, k1l, "phy", None)
            dk1l = 0.01 * k1l
            dI = q.convertUnit(fld, k1l+dk1l, "phy", None) - I0
        else:
            fld, I0, dI = sp[i]
            dk1l = q.convertUnit("b1", I0+dI, None, "phy") - \
                q.convertUnit("b1", I0, None, "phy")
        if unitsys is None:
            fac = dk1l/dI
        elif unitsys == "phy":
            fac = 1.0
        else:
            raise RuntimeError("Unknow unitsys={0}".format(unitsys))
        m[0,i] =  bta[i,0]/4.0/np.pi * fac
        m[1,i] = -bta[i,1]/4.0/np.pi * fac
    return m

