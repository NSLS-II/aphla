#!/usr/bin/env python

from . import _cfa, _lat

from catools import caget, caput

def getRbChannels(elemlist, tags = []):
    """
    get the pv names for a list of elements
    
    .. warning::

      elements like BPM will return both H/V channels. In case we want
      unique, use channelfinder class.

    .. seealso::

      :meth:`~hla.chanfinder.ChannelFinderAgent.getElementChannel`
    """
    t = ['default.eget']
    t.extend(tags)
    return _cfa.getElementChannel(elemlist, None, tags = set(t), unique=False)

def getSpChannels(elemlist, tags = []):
    """get the pv names for a list of elements"""
    t = ['default.eput']
    t.extend(tags)
    return _cfa.getElementChannel(elemlist, None, tags = set(t), unique=False)

#
#
def eget(element, full = False, tags = [], unique = False):
    """easier get"""
    # some tags + the "default"
    chtags = ['default.eget']
    if tags: chtags.extend(tags)
    #print __file__, tags, chtags
    if isinstance(element, str):
        ret = {}
        elemlst = _lat.getElementsCgs(element)
        pvl = _cfa.getElementChannel(elemlst, None, chtags, unique = unique)
        for i, pvs in enumerate(pvl):
            if len(pvs) == 1:
                ret[elemlst[i]] = caget(pvs[0])
            elif len(pvs) > 1:
                ret[elemlst[i]] = []
                for pv in pvs:
                    ret[elemlst[i]].append(caget(pv))
            else: ret[elemlst[i]] = None
            #print __file__, elemlst[i], pvs, _cfa.getElementChannel([elemlst[i]], unique = False)
        if full:
            return ret, pvl
        else: return ret
    elif isinstance(element, list):
        ret = []
        pvl = _cfa.getElementChannel(element, None, chtags, unique = False)
        for i, pv in enumerate(pvl):
            if len(pv) == 1:
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
    """
    if isinstance(element, list) and len(element) != len(value):
        raise ValueError("element list must have same size as value list")
    elif isinstance(element, str):
        val = [value]
    else: val = value[:]

    pvl = _cfa.getElementChannel(element, None, ['default.eput'])
    
    for i, pv in enumerate(pvl):
        caput(pv, val[i])
        

def reset_trims():
    trimx = _lat.getGroupMembers(['*', 'TRIMX'], op='intersection')
    trimy = _lat.getGroupMembers(['*', 'TRIMY'], op='intersection')
    pvx = getSpChannels(trimx, tags=['default.eput', 'X'])
    pvy = getSpChannels(trimy, tags=['default.eput', 'Y'])
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


