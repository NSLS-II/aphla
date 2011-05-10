#!/usr/bin/env python

"""
HLA Libraries
~~~~~~~~~~~~~~

:author: Lingyun Yang
:license:

Defines the procedural interface of HLA to the users.
"""

from . import _cfa, _lat, TAG_DEFAULT_GET, TAG_DEFAULT_PUT

from catools import caget, caput

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


