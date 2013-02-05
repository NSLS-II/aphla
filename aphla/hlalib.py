"""
Core APHLA Libraries
---------------------

Defines the fundamental routines.
"""

# :author: Lingyun Yang

import logging
import numpy as np
import time
from fnmatch import fnmatch
from catools import caget, caput, CA_OFFLINE
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

# current
def getCurrent(name='dcct', field='value', unit=None):
    """Get the current from the first DCCT element

    :param str name: the name of DCCT, default 'dcct'
    :param str field: the field of DCCT, default 'value'
    :param unit: the desired unit sytem, default None, no conversion.

    returns None if no 'dcct' element found

    seealso :func:`eget`
    """
    _current = getElements(name)
    if _current: return _current[0].get(field, unit=unit)
    else: return None

# rf
def getRfFrequency(name = 'rfcavity', field = 'f', unit=None):
    """
    Get the frequency from the first 'RFCAVITY' element.

    seealso :func:`eget`, :func:`getRfVoltage`, :func:`putRfFrequency`
    """
    _rf = getElements(name)
    if _rf: return _rf[0].get(field, unit=unit)
    else: return None


def putRfFrequency(f, name = 'rfcavity', field = 'f', unit=None):
    """set the rf frequency for the first 'RFCAVITY' element"""
    _rf = getElements(name)
    if _rf: return _rf[0].put(field, f, unit=unit)
    else: raise RuntimeError("element '%s' not found" % name)

def getRfVoltage(name = 'rfcavity', field='v', unit=None):
    """
    Get the voltage of the first 'RFCAVITY' element

    :param str name: cavity name
    :param str field: field name for voltage, default 'v'
    :param str unit: unit system

    return None if no element found
    """
    _rf = getElements(name)
    if _rf: return _rf[0].get(field, unit=unit)
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
    """
    reset all trims in group "HCOR" and "VCOR"
    """
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
    group: str, list.
        a list of element name or a name pattern.
    include_virtual: include virtual element or not.

    Returns
    ---------
     elemlist: a list of matched element objects.
    
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
    """get elements field values
    
    :param elem: element name, name list, pattern or object list
    :type elem: str, list
    :param fields: field name or name list
    :type fields: str, list
    :param header: optional (True, False), whether returns the (name, field) list. 
 
    Examples
    ---------
    >>> eget('DCCT', 'value')
    >>> eget('BPM', 'x')
    >>> val, head = eget('p*c30*', ['x', 'y'], header=True)

    >>> bpm = getElements('p*c30*')
    >>> eget(bpm, ['x', 'y'], header=True)

    The optional parameters are unit. see :func:`~aphla.element.CaElement.get`

    It calls :func:`getElements` to obtain a list of elements, then call
    :func:`~aphla.element.CaElement.get` for each field. This could be a
    slow process when the element list is large.

    The return value is a list with same size as element list. When more than
    one field is provided, the return value is a 2D list. 

    When header is True, a list of (element name, field) which has same shape
    as return value is also returned.

    """

    header = kwargs.pop('header', False)

    elst = getElements(elem)
    if not elst: return None

    v = [e.get(fields, **kwargs) for e in elst]
    if not header: return v

    h = []
    if isinstance(fields, (str, unicode)):
        h = [(e.name, fields) for e in elst]
    elif isinstance(fields, (list, tuple)):
        h = [None] * len(v)
        for i,e in enumerate(elst):
            fld = [f if f in e.fields() else None for f in fields]
            h[i] = [(e.name, f) for f in fld] 
        # h,v should have same dimension
    return v, h

        
def getPvList(elem, field, handle = 'readback', **kwargs):
    """
    return a pv list for given element or element list

    :param elem: element pattern, name list or CaElement object list
    :param field: e.g. 'x', 'y', 'k1'
    :param handle: 'READBACK' or 'SETPOINT'

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

def getBeamlineProfile(sb = 0, se = None):
    """
    return the beamline profile from sposition sb to se

    :param float sb: s-begin
    :param float se: s-end, None means the end of beamline.

    it calls :meth:`~aphla.lattice.Lattice.getBeamlineProfile` of the
    current lattice.
    """
    return machines._lat.getBeamlineProfile(s1=sb, s2=se)


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
def getPhase(group, **kwargs):
    """
    get the phase from stored data

    this calls :func:`~aphla.twiss.Twiss.getTwiss` of the current twiss data.
    """
    if not machines._twiss: return None
    elem = getElements(group)
    col = ('phi',)
    if kwargs.get('spos', False): col = ('phi', 's')
    
    return machines._twiss.getTwiss([e.name for e in elem], col=col, **kwargs)
#
#
def getBeta(group, **kwargs):
    """
    get the beta function from stored data.

    :Example:

      >>> getBeta('Q*', spos = True)

    - *src*: 'DB' from database, 'VA' virtual accelerator

    this calls :func:`~aphla.twiss.Twiss.getTwiss` of the current twiss data.
    """
    src = kwargs.pop("src", 'DB')

    elem = getElements(group)
    col = ('beta',)
    if kwargs.get('spos', False): col = ('beta', 's')

    if src == 'DB':
        if not machines._twiss:
            logger.error("ERROR: No twiss data loaeded")
            return None
        return machines._twiss.getTwiss([e.name for e in elem], 
                                        col=col, **kwargs)
    elif src == 'VA':
        twiss = getElements('twiss')[0]
        idx = [e.index for e in elem]
        s, bx, by = twiss.s, twiss.betax, twiss.betay
        if 's' in col:
            ret = np.zeros((len(elem), 3), 'd')
            for i,e in enumerate(elem):
                j = np.argmin(np.abs(s - e.se))
                ret[i,:] = (bx[j], by[j], s[j])
        else:
            ret = np.zeros((len(elem), 2), 'd')
            for i,e in enumerate(elem):
                j = np.argmin(np.abs(s - e.se))
                ret[i,:] = (bx[j], by[j])
        if kwargs.get('names', False):
            return ret, [e.name for e in elem]
        else: return ret

def getDispersion(group, **kwargs):
    """
    get the dispersion

    this calls :func:`~aphla.hlalib.getEta`.
    """
    return getEta(group, **kwargs)

def getEta(group, **kwargs):
    """
    get the dispersion from stored data

    similar to :func:`getBeta`, it calls :func:`~aphla.twiss.Twiss.getTwiss`
    of the current twiss data.

    :Example:

        >>> getEta('P*', spos = True, src = 'DB')
        >>> getEta('BPM')
        >>> getEta(['BPM1', 'BPM2'])

    - *src*: 'DB' from database, 'VA' from virtual accelerator

    seealso :func:`getElements`
    """

    src = kwargs.pop("src", 'DB')

    elem = getElements(group)
    col = ('eta',)
    if kwargs.get('spos', False): col = ('eta', 's')

    if src == 'DB':
        if not machines._twiss:
            logger.error("ERROR: No twiss data loaeded")
            return None
        return machines._twiss.getTwiss([e.name for e in elem], 
                                        col=col, **kwargs)
    elif src == 'VA':
        twiss = getElements('twiss')[0]
        idx = [e.index for e in elem]
        if 's' in col:
            ret = np.zeros((len(elem), 3), 'd')
            ret[:,-1] = np.take(twiss.s, idx)
        else:
            ret = np.zeros((len(elem), 2), 'd')
        ret[:,0] = np.take(twiss.etax, idx)
        ret[:,1] = np.take(twiss.etay, idx)
        return ret

def getChromaticity(source='machine'):
    """
    get chromaticity **Not Implemented Yet**
    """
    if source == 'machine':
        raise NotImplementedError()
    elif source == 'model':
        raise NotImplementedError()
    elif source == 'database':
        raise NotImplementedError()
    return None

def getTunes(source='machine'):
    """
    get tunes from ['machine', 'database']
    """
    if source == 'machine':
        # return only the first matched element
        nu = getElements('tune')
        return nu[0].x, nu[0].y
    elif source == 'database':
        return machines._lat.getTunes()
    elif source == 'model':
        raise NotImplementedError()

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

def getFftTune(plane = 'hv', mode = ''):
    """get tune from FFT

    .. warning::

      Not Implemented Yet
    """
    raise NotImplementedError()
    return None

#def savePhase(mode, phase, info):
#    """
#    Not implemented yet
#    """
#    raise NotImplementedError()
#    return None
#
#def saveBeta(mode, phase, info):
#    """
#    Not implemented yet
#    """
#    raise NotImplementedError()
#    return None
#
#def saveDispersion(mode, phase, info):
#    """
#    Not implemented yet
#    """
#    raise NotImplementedError()
#    return None
#
#def saveTune(mode, phase, info):
#    """
#    Not implemented yet
#    """
#    raise NotImplementedError()
#    return None
#
#def saveTuneRm(mode, phase, info):
#    """
#    Not implemented yet
#    """
#    raise NotImplementedError()
#    return None
#
#def saveChromaticity(mode, phase, info):
#    """
#    Not implemented yet
#    """
#    raise NotImplementedError()
#    return None
#
#def saveChromaticityRm(mode, phase, info):
#    """
#    Not implemented yet
#    """
#    raise NotImplementedError()
#    return None

def getChromaticityRm(mode, phase, info):
    """
    Not implemented yet
    """
    raise NotImplementedError()
    return None, None

def getTuneRm(mode):
    """
    Not implemented yet
    """
    raise NotImplementedError()

def getCurrentMode(self):
    """
    Not implemented yet
    """
    raise NotImplementedError()
    return None

def getModes(self):
    """
    Not implemented yet
    """
    raise NotImplementedError()
    return None

def saveMode(self, mode, dest):
    """
    Save current states to a new mode
    Not implemented yet
    """
    raise NotImplementedError()


def _removeLatticeMode(mode):
    raise NotImplementedError()
    #import os
    #cfg = cfg_pkl = os.path.join(hlaroot, "machine", root["nsls2"], 'hla.pkl')
    #f = shelve.open(cfg, 'c')
    #modes = []
    ##del f['lat.twiss']
    ##for k in f.keys(): print k
    #for k in f.keys():
    #    if re.match(r'lat\.\w+\.mode', k): print "mode:", k[4:-5]
    #if not mode:
    #    pref = "lat."
    #else:
    #    pref = 'lat.%s.' % mode
    #f.close()


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

def getTbtOrbit(**kwargs):
    """
    return turn-by-turn BPM data.

    - *field* ['A', 'B', 'C', 'D', 'X', 'Y', 'S', 'Q'], each has the RMS value: 'rmsA'-'rmsQ'
    """
    field = kwargs.get('field', 'X')
    pref = 'LTB:BI{BPM:1}' + 'TBT-'
    return caget(pref + field)
    
def getFastOrbit(**kwargs):
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
    unit = kwargs.get('unit', None)

    if CA_OFFLINE: 
        if full: return (True, 0)
        else: return True

    time.sleep(wait[0])

    ntrial = 0
    while True:
        v1 = np.ravel(eget(elemlst, fields, unit=unit))
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
    unit = kwargs.get('unit', None)

    if CA_OFFLINE: return True

    time.sleep(wait[0])

    v = np.zeros((len(elemlst), maxtrial), 'd')
    for i in range(maxtrial):
        v[:,i] = np.ravel(eget(elemlst, fields, unit=unit))
        time.sleep(wait[1])

    time.sleep(wait[2])
    if np.average(np.std(v, axis=0)) < maxstd: return True
    else: return False
    

