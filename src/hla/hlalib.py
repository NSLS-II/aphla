#!/usr/bin/env python

"""
HLA Libraries
~~~~~~~~~~~~~~

:author: Lingyun Yang
:license:

Defines the procedural interface of HLA to the users.
"""

import numpy as np
from fnmatch import fnmatch
from catools import caget, caput
import machines


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

    This relies on channel finder service, and searching for "default.eget"
    tag of the element.

    Example::

      >>> eget('QM1G4C01B')
      >>> eget(['CXM1G4C01B', 'CYM1G4C01B'])
    """
    # some tags + the "default"
    chtags = [TAG_DEFAULT_GET]
    if tags: chtags.extend(tags)
    #print __file__, tags, chtags
    if isinstance(element, str):
        ret = []
        elemlst = machines._lat._getElementsCgs(element)
        pvl = _cfa.getElementChannels(elemlst, None, chtags)
        for i, pvs in enumerate(pvl):
            if len(pvs) == 1:
                ret.append(caget(pvs[0]))
            elif len(pvs) > 1:
                rec = []
                for pv in pvs:
                    rec.append(caget(pv))
                ret.append(rec)
            else: ret = None
        if full:
            return ret, elemlst, pvl
        else: return ret
    elif isinstance(element, list):
        ret = []
        pvl = _cfa.getElementChannels(element, None, chtags)
        if not pvl:
            raise ValueError("no channels found for " + str(element))
        
        for i, pv in enumerate(pvl):
            if not pv:
                ret.append(None)
            elif len(pv) == 1:
                ret.append(caget(pv[0]))
            elif len(pv) > 1:
                ret.append(caget(pv))
        if full: return ret, pvl
        else: return ret
    else:
        raise ValueError("element can only be a list or group name")


def eput(element, value):
    """
    easier put

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

    pvls = _cfa.getElementChannels(element, None, [TAG_DEFAULT_PUT])

    print pvls
    # use the first one of default put, ignore the rest
    if isinstance(pvls, str):
        caput(pvls, value)
    else:
        caput(pvls, value)

def reset_trims():
    """
    reset all trims in group "TRIMX" and "TRIMY"
    """
    trimx = machines._lat.getGroupMembers(['*', 'TRIMX'], op='intersection')
    trimy = machines._lat.getGroupMembers(['*', 'TRIMY'], op='intersection')
    pvx = getSpChannels(trimx, tags=[TAG_DEFAULT_PUT, 'X'])
    pvy = getSpChannels(trimy, tags=[TAG_DEFAULT_PUT, 'Y'])
    pv = [p[0] for p in pvx]
    pv.extend([p[0] for p in pvy])
    v = [0]*len(pv)
    caput(pv, v)


def levenshtein_distance(first, second):
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


def getElements(group):
    """
    return list of elements.

    *group* is an exact name of element or group, or a pattern.

    ::

      >>> getElements('FH2G1C30A')
      >>> getElements('BPM')
      >>> getElements('F*G1C0*')
      >>> getElements(['FH2G1C30A', 'FH2G1C28A'])

    .. seealso:: :func:`~hla.lattice.Lattice.getElements`
    """

    return machines._lat.getElements(group)

def getLocations(group):
    """
    Get the location of an element or a list of elements

    *elements* is :

    - an element object
    - an element name
    - a list of element object
    - a list of element name

    Example::

      elem = getElements('BPMX')
      s = getLocations(elem)

      s = getLocations(['PM1G4C27B', 'PH2G2C28A'])
    """
    
    elem = getElements(group)
    if isinstance(elem, list):
        return [e.sb for e in elem]
    else: return elem.sb

def addGroup(group):
    """
    add a new group, *group* should be plain string, characters in
    \[a-zA-Z0-9\_\]

    raise *ValueError* if *group* is an illegal name.

    .. seealso:: :func:`~hla.lattice.Lattice.addGroup`
    """
    return _lat.addGroup(group)

def removeGroup(group):
    """
    Remove a group if it is empty
    """
    _lat.removeGroup(group)

def addGroupMembers(group, member):
    """Add a new member to a existing group"""
    if isinstance(member, str):
        _lat.addGroupMember(group, member)
    elif isinstance(member, list):
        for m in member:
            _lat.addGroupMember(group, m)
    else:
        raise ValueError("member can only be string or list")

def removeGroupMembers(group, member):
    """Remove a member from group"""
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
    """
    return machines._lat.getGroups(element)

def getGroupMembers(groups, op = 'intersection', **kwargs):
    """
    Get all elements in a group. If group is a list, consider which op:

    - op = "union", consider elements in the union of the groups
    - op = "intersection", consider elements in the intersect of the groups
    """
    return machines._lat.getGroupMembers(groups, op, **kwargs)

def getNeighbors(element, group, n = 3):
    """
    Get a list of n elements belongs to group. The list is sorted along s
    (the beam direction).

    .. seealso::
        
        :class:`~hla.lattice.Lattice`
        :meth:`~hla.lattice.Lattice.getNeighbors` For getting list of
        neighbors. 
    """

    return machines._lat.getNeighbors(element, group, n)


def getStepSize(element):
    """Return default stepsize of a given element"""
    raise NotImplementedError()
    return None

#
#
#
def getPhase(group, **kwargs):
    """
    get the phase from stored data
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
    get the beta function from stored data
    """
    if not machines._twiss: return None
    elem = getElements(group)
    col = ('beta',)
    if kwargs.get('spos', False): col = ('beta', 's')
    
    return machines._twiss.getTwiss([e.name for e in elem], col=col, **kwargs)

def getDispersion(group, **kwargs):
    """
    get the dispersion

    .. seealso:: :func:`~hla.hlalib.getEta`
    """
    return getEta(group, **kwargs)

def getEta(group, **kwargs):
    """
    get the dispersion from stored data

    .. seealso:: :func:`~hla.lattice.Lattice.getEta`
    """

    if not machines._twiss: return None
    elem = getElements(group)
    col = ('eta',)
    if kwargs.get('spos', False): col = ('eta', 's')
    
    return machines._twiss.getTwiss([e.name for e in elem], col=col, **kwargs)

def getChromaticity(source='machine'):
    """
    get chromaticity
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

def getTune(source='machine', plane = 'hv'):
    """
    get tune
    """
    nux, nuy = getTunes(source)
    if plane == 'h': return nux
    elif plane == 'v': return nuy
    else:
        raise ValueError("plane must be h/v")

def getFftTune(plane = 'hv', mode = ''):
    """
    get tune from FFT
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
    """
    return machines._lat.getGroupMembers('BPM', op='union')

def getFullOrbit(group = '*', sequence = None):
    """Return orbit"""
    x = caget("SR:C00-Glb:G00{ORBIT:00}RB-X")
    y = caget("SR:C00-Glb:G00{ORBIT:00}RB-Y")
    s = caget("SR:C00-Glb:G00{POS:00}RB-S")
    ret = []
    for i in range(len(s)):
        ret.append([s[i], x[i], y[i]])
    return ret

def getOrbit(pat = '', spos = False):
    """
    Return orbit::

      >>> getOrbit()
      >>> getOrbit('*')
      >>> getOrbit('*', spos=True)
      >>> getOrbit(['PL1G6C24B', 'PH2G6C25B'])

    If *pat* is not provided, use the group read of every BPMs, this is
    faster than read BPM one by one with getOrbit('*').

    The return value is a (n,4) or (n,2) 2D array, where n is the number
    of matched BPMs. The first two columns are x/y orbit, the last two
    columns are s location for x and y BPMs.

    When the element is not found or not a BPM, return NaN in its positon.

    .. warning::

      This depends on channel finder using 'aphla.x', 'aphla.y', 'aphla.eget' tags.

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
        ret[:,0] = bpmx.value
        ret[:,1] = bpmy.value
        return ret
    # need match the element name
    if isinstance(pat, (unicode,str)):
        elem = [e for e in getBpms() if fnmatch(e.name, pat)]
        x = [(e.getValues(tags=['aphla.eget', 'aphla.x']), e.getValues(tags=['aphla.y', 'aphla.eget']), e.sb) for e in elem]
        return np.array(x, 'd')
    elif isinstance(pat, (list,)):
        elem = machines._lat.getElements(pat)
        ret = []
        for e in elem:
            if not e or e.family != 'BPM': ret.append([None, None, None])
            else: ret.append([e.getValues(tags=['aphla.eget', 'aphla.x']), e.getValues(tags=['aphla.eget', 'aphla.y']), e.sb])
        return np.array(ret, 'd')




