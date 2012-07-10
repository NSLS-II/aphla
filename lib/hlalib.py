#!/usr/bin/env python

"""
Core APHLA Libraries
~~~~~~~~~~~~~~~~~~~~~

:author: Lingyun Yang

Defines the fundamental routines.
"""

import logging
import numpy as np
import time
from fnmatch import fnmatch
from catools import caget, caput
import machines
import element

logger = logging.getLogger(__name__)

__all__ = [
    'addGroup', 'addGroupMembers', 'eget', 'getBeamlineProfile', 'getBeta', 
    'getBpms', 'getChromaticityRm', 'getChromaticity', 'getClosest', 
    'getCurrent', 'getCurrentMode', 'getDispersion', 'getDistance', 
    'getElements', 'getEta', 'getFastOrbit', 'getFftTune', 
    'getGroupMembers', 'getGroups', 'getLocations', 'getModes', 
    'getNeighbors', 'getOrbit', 'getPhase', 'getPvList', 'getRfFrequency', 
    'getRfVoltage', 'getStepSize', 'getTbtOrbit', 'getTuneRm', 
    'getTune', 'getTunes', 
    'removeGroup', 'removeGroupMembers', 'setRfFrequency',
    'stepRfFrequency', 
    'waitStableOrbit', 
]

# current
def getCurrent():
    """
    Get the current from the first 'DCCT' element
    """
    _current = getElements('DCCT')
    if len(_current) == 1:
        return _current[0].value
    elif len(_current) > 1:
        return [c.value for c in _current]
    else:
        return None

# rf
def getRfFrequency():
    """Get the frequency from the first 'RFCAVITY' element"""
    _rf, = getElements('RFCAVITY')
    return _rf.f

def putRfFrequency(f):
    raise DeprecationWarning("use `setRfFrequency` instead")

def setRfFrequency(f):
    """set the rf frequency for the first 'RFCAVITY' element"""
    _rf, = getElements('RFCAVITY')
    _rf.f = f

def getRfVoltage():
    """Get the voltage of the first 'RFCAVITY' element"""
    _rf, = getElements('RFCAVITY')
    return _rf.v

def stepRfFrequency(df = 0.010):
    """
    change one step of the 'RFCAVITY' element

    .. seealso:: 

       :func:`~aphla.hlalib.getRfFrequency`, 
       :func:`~aphla.hlalib.putRfFrequency`
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
def eget(element, full = False, tags = None):
    """
    easier get with element name(s)

    This relies on channel finder service, and searching for :attr:`~aphla.machines.HLA_TAG_EGET`
    tag of the element.

    Example::

      >>> eget('QM1G4C01B')
      >>> eget(['CXM1G4C01B', 'CYM1G4C01B'])
      >>> eget('PL1G2C05A', tags='aphla.x')

    - single element name, it returns one value or a list of values depending on matched PVs.
    - list of element name, it returns a list, each could also be a list, a value or None.

    The value is None if element is not found or no PV is found.
    """

    # some tags + the "default"
    chtags = [machines.HLA_TAG_EGET]
    if tags is not None: chtags.extend(tags)
    #print __file__, tags, chtags
    if isinstance(element, (unicode, str)):
        ret = []
        # if given string, assume it is exact name of element
        elem = machines._lat._find_exact_element(element)
        pvl = elem.pv(tags=chtags)
        #print element, chtags, pvl
        if len(pvl) == 1: ret = caget(pvl[0])
        else: ret = caget(pvl)
        if full:
            return pvl, ret
        else: return ret
    elif isinstance(element, (tuple, set, list)):
        ret = []
        elemlst = machines._lat.getElementList(element)
        for elem in elemlst:
            if not elem:
                ret.append(None)
                continue
            pvl = elem.pv(tags=chtags)
            if pvl: ret.append(caget(pvl))
            else: ret.append(None)
        return ret
    else:
        raise ValueError("element can only be a list or group name")


def _reset_trims(verbose=False):
    """
    reset all trims in group "HCOR" and "VCOR"
    """
    trimx = machines._lat.getGroupMembers(['*', 'HCOR'], op='intersection')
    trimy = machines._lat.getGroupMembers(['*', 'VCOR'], op='intersection')
    pv = []
    for e in trimx:
        pv.extend(e.pv(field='x', handle='SETPOINT'))
    for e in trimy:
        pv.extend(e.pv(field='y', handle='SETPOINT'))
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

    :param group: a list of element name or a name pattern.
    :type group: list or string
    :param include_virtual: include virtual element or not.
    :type include_virtual: bool
    
    :return: returns a list of matched element objects.
    
    :Example:

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

    this calls :func:`~aphla.lattice.Lattice.getElementList` of the current
    lattice.

    The default does not include virtual element.

    return None if no element is found and return_list=False
    """

    elems = machines._lat.getElementList(group)
    if not include_virtual:
        elems = [e for e in elems if e.virtual == 0]

    return elems

def getPvList(elem, field, handle, **kwargs):
    """
    return a pv list for given element list

    :param elem: element pattern, name list
    :param field: e.g. 'x', 'y', 'k1'
    :param handle: 'READBACK' or 'SETPOINT'

    Keyword arguments:

      - *first_only* (False) use only the first PV for each element. 
      - *compress_empty* (False) remove element with no PV.

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

    Example::

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
    add a new group, *group* should be plain string, characters in
    \[a-zA-Z0-9\_\]

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
    Get a list of n elements belongs to group. The list is sorted along s
    (the beam direction).

    it calls :meth:`~aphla.lattice.Lattice.getNeighbors` of the current
    lattice to get neighbors.

    ::

      >>> getNeighbors('PM1G4C27B', 'BPM', 2)
      >>> getNeighbors('PM1G4C27B', 'QUAD', 1)
      >>> el = hla.getNeighbors('PH2G6C25B', 'P*C10*', 2)
      >>> [e.name for e in el]
      ['PL2G6C10B', 'PL1G6C10B', 'PH2G6C25B', 'PH1G2C10A', 'PH2G2C10A']
      >>> [e.sb for e in el]
      [284.233, 286.797, 678.903, 268.921, 271.446]
    """

    return machines._lat.getNeighbors(element, group, n)

def getClosest(element, group):
    """
    Get the closest element in *group*

    ::

      >>> getClosest('PM1G4C27B', 'BPM')

    It calls :meth:`~aphla.lattice.Lattice.getClosest`
    """

    return machines._lat.getClosest(element, group)

def getBeamlineProfile(s1 = 0, s2 = 1e10):
    """
    return the beamline profile from s1 to s2

    it calls :meth:`~aphla.lattice.Lattice.getBeamlineProfile` of the
    current lattice.
    """
    return machines._lat.getBeamlineProfile(s1, s2)

def getStepSize(element):
    """
    Return default stepsize of a given element

    .. warning::

      Not implemented
    """
    raise NotImplementedError()
    return None

def getDistance(elem1, elem2, absolute=True):
    """
    return distance between two element name

    :param str elem1: name of one element
    :param str elem2: name of the other element
    :param bool absolute: return s2 - s1 or the absolute value.

    raise RuntimeError if None or more than one elements are found
    """
    e1 = getElements(elem1)
    e2 = getElements(elem2)

    if len(e1) != 1 or len(e2) != 1:
        raise RuntimeError("elements are not uniq: %d and %d" % (len(e1), len(e2)))

    ds = e2[0].sb - e1[0].sb
    C = machines._lat.circumference
    if machines._lat.loop and C > 0:
        while ds < -C: ds = ds + C
        while ds > C: ds = ds - C
    if absolute: return abs(ds)
    else: return ds

#
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

    ::

      >>> getBeta('Q*', spos = True)

    this calls :func:`~aphla.twiss.Twiss.getTwiss` of the current twiss data.
    """
    if not machines._twiss:
        print "ERROR: No twiss data loaeded"
        return None
    elem = getElements(group)

    col = ('beta',)
    if kwargs.get('spos', False): col = ('beta', 's')
    
    return machines._twiss.getTwiss([e.name for e in elem], col=col, **kwargs)

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
    """

    if not machines._twiss: return None
    elem = getElements(group)
    col = ('eta',)
    if kwargs.get('spos', False): col = ('eta', 's')
    
    return machines._twiss.getTwiss([e.name for e in elem], col=col, **kwargs)

def getChromaticity(source='machine'):
    """
    get chromaticity

    .. warning::

      Not implemented yet.
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
        nu, = getElements('TUNE')
        return nu.value
    elif source == 'database':
        return machines._lat.getTunes()
    elif source == 'model':
        raise NotImplementedError()

def getTune(source='machine', plane = 'h'):
    """
    get tune

    :Example:

        >>> getTune(plane='v')
    """
    nux, nuy = getTunes(source)
    if plane == 'h': return nux
    elif plane == 'v': return nuy
    else:
        raise ValueError("plane must be either h or v")

def getFftTune(plane = 'hv', mode = ''):
    """
    get tune from FFT

    .. warning::

      Not Implemented Yet
    """
    raise NotImplementedError()
    return None

def savePhase(mode, phase, info):
    """
    Not implemented yet
    """
    raise NotImplementedError()
    return None

def saveBeta(mode, phase, info):
    """
    Not implemented yet
    """
    raise NotImplementedError()
    return None

def saveDispersion(mode, phase, info):
    """
    Not implemented yet
    """
    raise NotImplementedError()
    return None

def saveTune(mode, phase, info):
    """
    Not implemented yet
    """
    raise NotImplementedError()
    return None

def saveTuneRm(mode, phase, info):
    """
    Not implemented yet
    """
    raise NotImplementedError()
    return None

def saveChromaticity(mode, phase, info):
    """
    Not implemented yet
    """
    raise NotImplementedError()
    return None

def saveChromaticityRm(mode, phase, info):
    """
    Not implemented yet
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
    print "DONE"

def _reset_quad():
    qtag = {'H2': (1.47765, 30), 
            'H3': (-1.70755, 30),
            'H1': (-0.633004, 30),
            'M1': (-0.803148, 60),
            'M2': (1.2223, 60),
            'L2': (1.81307, 30),
            'L3': (-1.48928, 30),
            'L1': (-1.56216, 30)}
    
    for tag, v in qtag.items():
        qlst = getElements('Q%s*' % tag)
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


