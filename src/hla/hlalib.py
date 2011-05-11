#!/usr/bin/env python

"""
HLA Libraries
~~~~~~~~~~~~~~

:author: Lingyun Yang
:license:

Defines the procedural interface of HLA to the users.
"""

import numpy as np
from . import _cfa, _lat, TAG_DEFAULT_GET, TAG_DEFAULT_PUT

from catools import caget, caput

def parseElementName(name):
    """
    searching G*C*A type of string. e.g. 'CFXH1G1C30A' will be parsed as
    girder='G1', cell='C30', symmetry='A'

    Example::
    
      >>> parseElementName('CFXH1G1C30A')
      'C30', 'G1', 'A'
    """
    # for NSLS-2 convention of element name
    a = re.match(r'.+(G\d{1,2})(C\d{1,2})(.)', name)
    if a:
        girder   = a.groups()[0]
        cell     = a.groups()[1]
        symmetry = a.groups()[2]
    elif name == "CAVITY":
        # fix a broken name
        girder   = "CAVITY"
        cell     = "CAVITY"
        symmetry = "CAVITY"
    else:
        girder   = 'G0'
        cell     = 'C00'
        symmetry = '0'
    return cell, girder, symmetry


def getRbChannels(elemlist, tags = []):
    """
    get the pv names for a list of elements
    
    .. warning::

      elements like BPM will return both H/V channels. In case we want
      unique, use channelfinder class.

    .. seealso::

      :meth:`~hla.chanfinder.ChannelFinderAgent.getElementChannels`
    """
    t = [TAG_DEFAULT_GET]
    t.extend(tags)
    return _cfa.getElementChannels(elemlist, None, tags = set(t))

def getSpChannels(elemlist, tags = []):
    """get the pv names for a list of elements"""
    t = [TAG_DEFAULT_PUT]
    t.extend(tags)
    return _cfa.getElementChannels(elemlist, None, tags = set(t))

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
        elemlst = _lat._getElementsCgs(element)
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
    # use the first one of default put, ignore the rest
    pvl = [pv[0] for pv in pvls]
    
    caput(pvl, value)

def reset_trims():
    """
    reset all trims in group "TRIMX" and "TRIMY"
    """
    trimx = _lat.getGroupMembers(['*', 'TRIMX'], op='intersection')
    trimy = _lat.getGroupMembers(['*', 'TRIMY'], op='intersection')
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


def getElements(group, **kwargs):
    """
    return list of elements.

    - *cell* a list of cell name
    - *girder* a list of girder name
    - *symmetry* a list of symmetry: 'A' or 'B'
    """
    return _lat._getElementsCgs(group, **kwargs)

def getLocations(group, s='e'):
    """
    Get the location of a group, either returned as a dictionary in which the
    key is element physics name, value is the location.
    """
    if isinstance(group, list):
        return _lat.getLocations(group, s)
    elif isinstance(group, str):
        elem, loc = _lat.getElements(group, 'e')
        return loc
    else:
        raise ValueError("parameter *group* must be a list of string")


def addGroup(group):
    """
    add a new group, *group* should be plain string, characters in
    \[a-zA-Z0-9\_\]
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
    return _lat.getGroups(element)

def getGroupMembers(groups, op = 'intersection'):
    """
    Get all elements in a group. If group is a list, consider which op:

    - op = "union", consider elements in the union of the groups
    - op = "intersection", consider elements in the intersect of the groups
    """
    return _lat.getGroupMembers(groups, op)

def getNeighbors(element, group, n = 3):
    """
    Get a list of n elements belongs to group. The list is sorted along s
    (the beam direction).

    .. seealso::
        
        :class:`~hla.lattice.Lattice`
        :meth:`~hla.lattice.Lattice.getNeighbors` For getting list of
        neighbors. :py:func:`hla.lattice.Lattice.getNeighbors`
    """
    return _lat.getNeighbors(element, group, n)


def getStepSize(element):
    """Return default stepsize of a given element"""
    raise NotImplementedError()
    return None

#
#
#
def getPhase(group, loc = 'e'):
    """
    get the phase from stored data
    """
 
    if isinstance(group, list):
        return _lat.getPhase(group)
    elif isinstance(group, str):
        elem = getElements(group)
        return _lat.getPhase(elemlst = elem)
    else:
        return None

#
#
def getBeta(group, loc = 'e'):
    """
    get the beta function from stored data
    """
    return _lat.getBeta(group, loc)

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

    if isinstance(group, list):
        return _lat.getEta(group)
    elif isinstance(group, str):
        elem = getElements(group)
        return _lat.getEta(elem)
    else:
        return None

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
    get tunes
    """
    if source == 'machine':
        pv = _cfa.getElementChannel(['TUNEX', 'TUNEY'])
        nux = caget(pv[0])
        nuy = caget(pv[1])
        return nux[0], nuy[0]
    elif source == 'model':
        raise NotImplementedError()
    elif source == 'database':
        return _lat.getTunes()

def getTune(plane = 'hv'):
    """
    get tune
    """
    nux, nuy = getTunes()
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

def getFullOrbit(group = '*', sequence = None):
    """Return orbit"""
    x = caget("SR:C00-Glb:G00{ORBIT:00}RB-X")
    y = caget("SR:C00-Glb:G00{ORBIT:00}RB-Y")
    s = caget("SR:C00-Glb:G00{POS:00}RB-S")
    ret = []
    for i in range(len(s)):
        ret.append([s[i], x[i], y[i]])
    return ret

def getOrbit(group = '*', spos=False):
    """Return orbit"""
    if isinstance(group, str):
        #print __file__, "group = ", group
        elemx = _lat.getGroupMembers([group, 'BPMX'], op = 'intersection')
        elemy = _lat.getGroupMembers([group, 'BPMY'], op = 'intersection')
    elif isinstance(group, list):
        elemx = group[:]
        elemy = group[:]

    orbx, pvx = eget(elemx, full=True, tags=['X'])
    orby, pvy = eget(elemy, full=True, tags=['Y'])
    #print __file__, len(elemx), len(elemy), len(orbx), len(orby)
    #print __file__, orbx[0], elemx[0], pvx[0], caget(pvx[0][0])
    #print __file__, orbx, orby

    if spos:
        ret = np.zeros((len(orbx), 3), 'd')
        ret[:, 0] = _lat.getLocations(elemx, 'e')
        ret[:, 1] = orbx
        ret[:, 2] = orby
    else:
        ret = np.zeros((len(orbx), 2), 'd')
        ret[:, 0] = orbx
        ret[:, 1] = orby

    return ret



