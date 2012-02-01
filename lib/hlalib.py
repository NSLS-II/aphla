#!/usr/bin/env python

"""
Core HLA Libraries
~~~~~~~~~~~~~~~~~~

:author: Lingyun Yang
:license:

Defines the procedural interface of HLA to the users.
"""

import numpy as np
import time
from fnmatch import fnmatch
from catools import caget, caput
import machines

__all__ = [
    'getCurrent', 'getElements', 'getLocations', 'addGroup', 'removeGroup',
    'addGroupMembers', 'removeGroupMembers', 'getGroups', 'getGroupMembers',
    'getNeighbors', 'getClosest', 'getBeamlineProfile', 
    'getPhase', 'getBeta', 'getDispersion', 'getEta',
    'getOrbit', 'getTune', 'getTunes', 'getBpms',
    'eget', 'waitStableOrbit'
]

def getCurrent():
    """
    Get the current from element with a name 'DCCT'
    """
    _current = machines._lat.getElements('DCCT')
    return _current.value

#
#
def eget(element, full = False, tags = []):
    """
    easier get with element name(s)

    This relies on channel finder service, and searching for :attr:`~hla.machines.HLA_TAG_EGET`
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
    if tags: chtags.extend(tags)
    #print __file__, tags, chtags
    if isinstance(element, (unicode, str)):
        ret = []
        elem = machines._lat.getElements(element)
        pvl = elem.pv(tags=chtags)
        #print element, chtags, pvl
        ret = caget(pvl)
        if full:
            return pvl, ret
        else: return ret
    elif isinstance(element, (tuple, set, list)):
        ret = []
        elemlst = machines._lat.getElements(element)
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


def __eput(element, value):
    """
    easier put

    .. warning::

      deprecated

    This relies on channel finder service, and searching for "default.eput"
    tag of the element.

    Example::

      >>> eput('QM1G4C01B', 1.0)
      >>> eput(['CXM1G4C01B', 'CYM1G4C01B'], [0.001, .001])

    It does not do any wildcard matching. call getElements before hand to get
    a list of element.

    - *element* a single explicit element name or a list of element names
    - *value*, match the size of *element*
    """

    raise DeprecationWarning

    pvls = _cfa.getElementChannels(element, None, [TAG_DEFAULT_PUT])

    print pvls
    # use the first one of default put, ignore the rest
    if isinstance(pvls, str):
        caput(pvls, value)
    else:
        caput(pvls, value)

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

    print "DONE"


def _levenshtein_distance(first, second):
    """Find the Levenshtein distance between two strings."""
    if len(first) > len(second):
        first, second = second, first
    if len(second) == 0:
        return len(first)
    first_length = len(first) + 1
    second_length = len(second) + 1
    distance_matrix = [[0] * second_length for x in range(first_length)]
    for i in range(first_length):
       distance_matrix[i][0] = i
    for j in range(second_length):
       distance_matrix[0][j]=j
    for i in xrange(1, first_length):
        for j in range(1, second_length):
            deletion = distance_matrix[i-1][j] + 1
            insertion = distance_matrix[i][j-1] + 1
            substitution = distance_matrix[i-1][j-1]
            if first[i-1] != second[j-1]:
                substitution += 1
            distance_matrix[i][j] = min(insertion, deletion, substitution)
    return distance_matrix[first_length-1][second_length-1]


def getElements(group, return_list=False):
    """
    return list of elements.

    *group* is an exact name of element or group, or a pattern.

    ::

      >>> getElements('FH2G1C30A')
      >>> getElements('BPM')
      >>> getElements('F*G1C0*')
      >>> getElements(['FH2G1C30A', 'FH2G1C28A'])

    this calls :func:`~hla.lattice.Lattice.getElements` of the current lattice.
    """

    return machines._lat.getElements(group, return_list=return_list)

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

    it calls :func:`~hla.lattice.Lattice.addGroup` of the current lattice.
    """
    return _lat.addGroup(group)

def removeGroup(group):
    """
    Remove a group if it is empty. It calls
    :func:`~hla.lattice.Lattice.removeGroup` of the current lattice.
    """
    _lat.removeGroup(group)

def addGroupMembers(group, member):
    """
    add new members to an existing group

    ::

      >>> addGroupMembers('HCOR', 'CX1')
      >>> addGroupMembers('HCOR', ['CX1', 'CX2']) 

    it calls :meth:`~hla.lattice.Lattice.addGroupMember` of the current
    lattice.
    """
    if isinstance(member, str):
        _lat.addGroupMember(group, member)
    elif isinstance(member, list):
        for m in member:
            _lat.addGroupMember(group, m)
    else:
        raise ValueError("member can only be string or list")

def removeGroupMembers(group, member):
    """
    Remove a member from group

    ::

      >>> removeGroupMembers('HCOR', 'CX1')
      >>> removeGroupMembers('HCOR', ['CX1', 'CX2'])

    it calls :meth:`~hla.lattice.Lattice.removeGroupMember` of the current
    lattice.
    """
    if isinstance(member, str):
        _lat.removeGroupMember(group, member)
    elif isinstance(member, list):
        for m in member: _lat.removeGroupMember(group, m)
    else:
        raise ValueError("member can only be string or list")

def getGroups(element = '*'):
    """
    Get all groups own these elements, '*' returns all possible groups,
    since it matches every element
    
    it calls :func:`~hla.lattice.Lattice.getGroups` of the current lattice.
    """
    return machines._lat.getGroups(element)

def getGroupMembers(groups, op = 'intersection', **kwargs):
    """
    Get all elements in a group. If group is a list, consider which op:

    - op = "union", consider elements in the union of the groups
    - op = "intersection", consider elements in the intersect of the groups

    it calls :func:`~hla.lattice.Lattice.getGroupMembers` of the current
    lattice.
    """
    return machines._lat.getGroupMembers(groups, op, **kwargs)

def getNeighbors(element, group, n = 3):
    """
    Get a list of n elements belongs to group. The list is sorted along s
    (the beam direction).

    it calls :meth:`~hla.lattice.Lattice.getNeighbors` of the current
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

    It calls :meth:`~hla.lattice.Lattice.getClosest`
    """

    return machines._lat.getClosest(element, group)

def getBeamlineProfile(s1 = 0, s2 = 1e10):
    """
    return the beamline profile from s1 to s2

    it calls :meth:`~hla.lattice.Lattice.getBeamlineProfile` of the
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
    e1 = getElements(elem1)
    e2 = getElements(elem2)

    ds = e2.sb - e1.sb
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

    this calls :func:`~hla.twiss.Twiss.getTwiss` of the current twiss data.
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

    this calls :func:`~hla.twiss.Twiss.getTwiss` of the current twiss data.
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

    this calls :func:`~hla.hlalib.getEta`.
    """
    return getEta(group, **kwargs)

def getEta(group, **kwargs):
    """
    get the dispersion from stored data

    similar to :func:`getBeta`, it calls :func:`~hla.twiss.Twiss.getTwiss`
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
    get tunes from ['machine']
    """
    if source == 'machine':
        nux = machines._lat.getElements('TUNEX')
        nuy = machines._lat.getElements('TUNEY')
        return nux.value, nuy.value
    elif source == 'model':
        raise NotImplementedError()
    elif source == 'database':
        raise NotImplementedError()

def getTune(source='machine', plane = 'h'):
    """
    get tune

    >>> getTune(plane='v')
    """
    nux, nuy = getTunes(source)
    if plane == 'h': return nux
    elif plane == 'v': return nuy
    else:
        raise ValueError("plane must be h or v")

def getFftTune(plane = 'hv', mode = ''):
    """
    get tune from FFT

    .. warning::

      Not Implemented Yet
    """
    raise NotImplementedError()
    return None

def savePhase(mode, phase, info):
    raise NotImplementedError()
    return None

def saveBeta(mode, phase, info):
    raise NotImplementedError()
    return None

def saveDispersion(mode, phase, info):
    raise NotImplementedError()
    return None

def saveTune(mode, phase, info):
    raise NotImplementedError()
    return None

def saveTuneRm(mode, phase, info):
    raise NotImplementedError()
    return None

def saveChromaticity(mode, phase, info):
    raise NotImplementedError()
    return None

def saveChromaticityRm(mode, phase, info):
    raise NotImplementedError()
    return None

def getChromaticityRm(mode, phase, info):
    raise NotImplementedError()
    return None, None

def getTuneRm(mode):
    raise NotImplementedError()

def getCurrentMode(self):
    raise NotImplementedError()
    return current_mode

def getModes(self):
    raise NotImplementedError()
    return None

def saveMode(self, mode, dest):
    """Save current states to a new mode"""
    raise NotImplementedError()


def _removeLatticeMode(mode):
    cfg = cfg_pkl = os.path.join(hlaroot, "machine", root["nsls2"], 'hla.pkl')
    f = shelve.open(cfg, 'c')
    modes = []
    #del f['lat.twiss']
    #for k in f.keys(): print k
    for k in f.keys():
        if re.match(r'lat\.\w+\.mode', k): print "mode:", k[4:-5]
    if not mode:
        pref = "lat."
    else:
        pref = 'lat.%s.' % mode
    f.close()

def saveMode(self, mode, dest):
    """Save current states to a new mode"""
    #current_mode
    raise NotImplementedError("Not implemented yet")
    pass

def getBpms():
    """
    return a list of bpms object.

    this calls :func:`~hla.lattice.Lattice.getGroupMembers` of current
    lattice and take a "union".
    """
    return machines._lat.getGroupMembers('BPM', op='union')


def getOrbit(pat = '', spos = False):
    """
    Return orbit

    ::

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
        bpmx = machines._lat.getElements(machines.HLA_VBPMX)
        bpmy = machines._lat.getElements(machines.HLA_VBPMY)
        n = max([len(bpmx.sb), len(bpmy.sb)])
        if spos:
            ret = np.zeros((n, 4), 'd')
            ret[:,2] = bpmx.sb
            ret[:,3] = bpmy.sb
        else:
            ret = np.zeros((n,2), 'd')
        ret[:,0] = bpmx.x
        ret[:,1] = bpmy.y
        return ret

    # need match the element name
    if isinstance(pat, (unicode, str)):
        elem = [e for e in getBpms() if fnmatch(e.name, pat)]
        if not elem: return None
        ret = [[e.x, e.y, e.sb] for e in elem]
    elif isinstance(pat, (list,)):
        elem = machines._lat.getElements(pat)
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
    caput(pvs, 0.0)
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


