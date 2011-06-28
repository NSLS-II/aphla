#!/usr/env/python

"""
Lattice
~~~~~~~~

defines lattice related classes and functions.

:author: Lingyun Yang
"""

import re
from math import log10
import shelve
import numpy as np
from fnmatch import fnmatch

from catools import caget, caput
from element import Element

class Lattice:
    """Lattice"""
    # ginore those "element" when construct the lattice object

    def __init__(self, mode = 'undefined'):
        # group name and its element
        self._group = {}
        # guaranteed in the order of s.
        self._elements = []
        # data set
        self.mode = mode
        self.tune = [ 0.0, 0.0]
        self.chromaticity = [0.0, 0.0]
        self.circumference = 0.0
        self.orm = None

    def __getitem__(self, key):
        if isinstance(key, int):
            return self._elements[key]
        elif isinstance(key, str) or isinstance(key, unicode):
            return self._find_element(name=key)

    def _find_element(self, name):
        """
        exact matching of element name
        """
        for e in self._elements:
            if e.name == name: return e
        return None

    def _find_element_s(self, s, eps = 1e-9, loc='left'):
        """
        given s location, find an element at this location. If this is
        drift space, find the element at 'left' or 'right' of the given
        point.
        """
        if not loc in ['left', 'right']:
            raise ValueError('loc must be in ["left", "right"]')

        # normalize s into [0, C]
        sn = s
        if s > self.circumference: sn = s - self.circumference
        if s < 0: sn = s + self.circumference

        if sn < 0 or sn > self.circumference:
            raise ValueError("s= %f out of boundary ([%f, %f])"
                             % (s, -self.circumference, self.circumference))
        ileft, eleft = -1, self.circumference
        iright, eright = -1, self.circumference
        for i,e in enumerate(self._elements):
            if e.virtual > 0: continue
            # assuming elements is in order
            if abs(e.sb-s) <= eleft:
                ileft, eleft = i, abs(e.sb-s)
            if abs(e.se-s) <= eright:
                iright, eright = i, abs(e.se-s)
        if loc == 'left': return ileft
        elif loc == 'right': return iright

    def hasElement(self, name):
        if self._find_element(name): return True
        else: return False

    def insertElement(self, i, elem):
        self._elements.insert(i, elem)
        for g in elem.group:
            if not g: continue
            self.addGroupMember(g, elem.name, newgroup=True)
            
    def appendElement(self, elem):
        """
        append a new element to lattice. callers are responsible for avoiding
        duplicate elements (call hasElement before).
        """
        self._elements.append(elem)
        for g in elem.group:
            if not g: continue
            self.addGroupMember(g, elem.name, newgroup=True)
            
    def size(self):
        """
        total number of elements, including magnets and diagnostic instruments
        """
        return len(self._elements)
    
    def save(self, fname, dbmode = 'c'):
        """
        call signature::
        
          save(self, fname, dbmode='c')

        save the lattice into binary data, using writing *dbmode*. The exact
        dataset name is defined by *mode*, default is 'undefined'.
        """
        f = shelve.open(fname, dbmode)
        pref = "lat.%s." % self.mode
        f[pref+'group']   = self._group
        f[pref+'elements'] = self._elements
        f[pref+'mode']    = self.mode
        f[pref+'tune']    = self.tune
        f[pref+'chromaticity'] = self.chromaticity
        f.close()

    def load(self, fname, mode = ''):
        """
        call signature::
        
          load(fname, mode='')

        load the lattice from binary data

        In the db file, all lattice has a key with prefix 'lat.mode.'. If the
        given mode is empty string, then use 'lat.'
        """
        f = shelve.open(fname, 'r')
        if not mode:
            pref = "lat."
        else:
            pref = 'lat.%s.' % mode
        self._group  = f[pref+'group']
        self._elements  = f[pref+'elements']
        self.mode     = f[pref+'mode']
        self.tune     = f[pref+'tune']
        self.chromaticity = f[pref+'chromaticity']
        if self._elements:
            self.circumference = self._elements[-1].se
        f.close()

    def mergeGroups(self, parent, children):
        """
        merge child group(s) into a parent group

        the new parent group is replaced by this new merge of children groups
        
        Example::

            mergeGroups('BPM', ['BPMX', 'BPMY'])
            mergeGroups('TRIM', ['TRIMX', 'TRIMY'])
        """
        if isinstance(children, str):
            chlist = [children]
        elif hasattr(children, '__iter__'):
            chlist = children[:]
        else:
            raise ValueError("children can be string or list of string")

        #if not self._group.has_key(parent):
        self._group[parent] = []

        for child in chlist:
            if not self._group.has_key(child):
                print __file__, "WARNING: no %s group found" % child
                continue
            for elem in self._group[child]:
                if elem in self._group[parent]: continue
                self._group[parent].append(elem)

            
    def sortElements(self, namelist = None):
        """
        sort the element list to the order of *s*

        use sorted() for a list of element object.
        """
        if not namelist:
            self._elements = sorted(self._elements)
            return
        
        ret = []
        for e in self._elements:
            if e.name in ret: continue
            if e.name in namelist:
                ret.append(e.name)

        #
        if len(ret) < len(namelist):
            raise ValueError("Some elements are missing in the results")
        elif len(ret) > len(namelist):
            raise ValueError("something wrong on sorting element list")
 
        return ret[:]

    def getLocations(self, elemsname):
        """
        if elems is a string(element name), do exact match and return
        single number.  if elems is a list do exact match on each of them,
        return a list. None if the element in this list is not found.

        .. warning::
        
          If there are duplicate elements in *elems*, only first
          appearance has location returned.

          >>> getLocations(['BPM1', 'BPM1', 'BPM1']) #doctest: +SKIP
          [0.1, None, None]

        """

        if isinstance(elemsname, str):
            e = self._find_element(elemsname)
            return e.sb
        elif isinstance(elemsname, list):
            ret = [None] * len(elemsname)
            for elem in self._elements:
                if elem.name in elemsname:
                    idx = elemsname.index(elem.name)
                    ret[idx] = elem.s
            return ret
        else:
            raise ValueError("not recognized type of *elems*")

    def getLine(self, srange, eps = 1e-9):
        """
        get a list of element within range=(s0, s1).

        if s0 > s1, the range is equiv to (s0, s1+C), where C is the
        circumference.

        *eps* is the resolution.

        relying on the fact that element.s is the beginning of element.
        """
        s0, s1 = srange[0], srange[1]

        i0 = self._find_element_s(s0, loc='right')
        i1 = self._find_element_s(s1, loc='left')

        if i0 == None or i1 == None: return None
        elif i0 == i1: return self._elements[i0]
        elif i0 < i1:
            ret = self._elements[i0:i1+1]
        else:
            ret = self._elements[i0:]
            ret.extend(self._elements[:i1+1])
        return ret

    def getElements(self, group):
        """
        get elements.

        ::

          >>> getElements('BPM')
          >>> getElements('PL*')
          >>> getElements('C02')
          >>> getElements(['BPM'])
          [None]

        The input *group* is an element name, a pattern or group name. It
        is treated as an exact name first, and compared with element
        nmame, then group name. If no elements matched, it will treat
        input as a pattern and match with the element name.

        When the input *group* is a list, each string in this list will be
        treated as exact string instead of pattern.
        """

        if isinstance(group, str) or isinstance(group, unicode):
            # do exact element name match first
            #print __file__, "element ..."
            elem = self._find_element(group)
            if elem:
                #print "found exact element", group, elem
                return elem

            # do exact group name match
            #print __file__, "group ...", group, self._group.keys()
            if group in self._group.keys():
                #print "found exact group", group
                #print self._group.keys()
                return self._group[group]

            # do pattern match on element name
            ret, names = [], []
            #print __file__, "matching ..."
            for e in self._elements:
                if e.name in names: continue
                if fnmatch(e.name, group):
                    ret.append(e)
                    names.append(e.name)
            return ret
        elif isinstance(group, list):
            #print __file__, "list ..", group
            # exact one-by-one match
            ret = [None] * len(group)
            for elem in self._elements:
                if elem.name in group: ret[group.index(elem.name)] = elem
            return ret

    def _matchElementCgs(self, elem, **kwargs):
        """
        check properties of an element
        
        - *cell*
        - *girder*
        - *symmetry*
        """

        cell = kwargs.get("cell", None)
        
        if isinstance(cell, str) and elem.cell != cell:
            return False
        elif hasattr(cell, "__iter__") and not elem.cell in cell:
            return False

        girder = kwargs.get("girder", None)
        
        if isinstance(girder, str) and elem.girder != girder:
            return False
        elif hasattr(girder, "__iter__") and not elem.girder in girder:
            return False

        symmetry = kwargs.get("symmetry", None)
        
        if isinstance(symmetry, str) and elem.symmetry != symmetry:
            return False
        elif hasattr(symmetry, "__iter__") and not elem.symmetry in symmetry:
            return False

        return True

        
        
    def _getElementsCgs(self, group = '*', **kwargs):
        """
        call signature::
        
          getElementsCgs(group)

        Get a list of elements from cell, girder and sequence

        - *cell*
        - *girder*
        - *symmetry*

        Example::

          getElementsCgs('BPMX', cell=['C20'], girder=['G2'])

        When given a general group name, check the following:

        - element name
        - element family
        - existing *group*: 'BPM', 'BPMX', 'BPMY', 'A', 'C02', 'G4'

            - cell
            - girder
            - symmetry
        """

        # return empty set if not specified the group
        if not group: return None
        
        elem = []
        for e in self._elements:
            # skip for duplicate
            #print e.name,
            if e.name in elem: continue

            if not self._matchElementCgs(e, **kwargs):
                continue
            
            if e.name in self._group.get(group, []):
                elem.append(e.name)
            elif fnmatch(e.name, group):
                elem.append(e.name)
            else:
                #print "skiped"
                pass
                
            #if cell and not e.cell in cell: continue
            #if girder and not e.girder in girder: continue
            #if symmetry and not e.symmetry in symmetry: continue
        
        return elem

    def _illegalGroupName(self, group):
        # found character not in [a-zA-Z0-9_]
        if not group: return True
        elif re.search(r'[^\w]+', group):
            #raise ValueError("Group name must be in [a-zA-Z0-9_]+")
            return True
        else: return False

    def buildGroups(self):
        """
        clear the old groups, fill with new data by collecting group name
        that each element belongs to.
        """
        # cleanr everything
        self._group = {}
        for e in self._elements:
            for g in e.group:
                if self._illegalGroupName(g): continue
                self.addGroupMember(g, e.name, newgroup=True)
        #print __file__, "test a group", self._group['DIPOLE']
        #print __file__, self._group.keys()
        
    def addGroup(self, group):
        """
        create a new group

        ::
        
          >>> addGroup(group)
          
        Input *group* is a combination of alphabetic and numeric
        characters and underscores. i.e. "[a-zA-Z0-9\_]"

        raise ValueError if the name is illegal or the group already exists.
        """
        if self._illegalGroupName(group):
            raise ValueError('illegal group name %s' % group)
        if not self._group.has_key(group):
            self._group[group] = []
        else:
            raise ValueError('group %s exists' % group)

    def removeGroup(self, group):
        """
        call signature::

          removeGroup(self, group)

        remove a group only when it is empty
        """
        if self._illegalGroupName(group): return
        if not self._group.has_key(group):
            raise ValueError("Group %s does not exist" % group)
        if len(self._group[group]) > 0:
            raise ValueError("Group %s is not empty" % group)
        # remove it!
        self._group.pop(group)

    def addGroupMember(self, group, member, newgroup = False):
        """
        add a member to group

        if newgroup == False, the group must exist before.
        """

        if not self.hasElement(member): 
            raise ValueError("element %s is not defined" % member)
        elem = self.getElements(member)
        if self.hasGroup(group):
            if elem in self._group[group]: return
            for i,e in enumerate(self._group[group]):
                if e.sb < elem.sb: continue
                self._group[group].insert(i, elem)
                break
            else:
                self._group[group].append(elem)
        elif newgroup:
            self._group[group] = [elem]
        else:
            raise ValueError("Group %s does not exist."
                             "use newgroup=True to add it" % group)

    def hasGroup(self, group):
        """
        check if group exists or not.
        """
        return self._group.has_key(group)

    def removeGroupMember(self, group, member):
        """
        remove a member from group
        """
        if not self.hasGroup(group):
            raise ValueError("Group %s does not exist" % group)
        if member in self._group[group]:
            self._group[group].remove(member)
        else:
            raise ValueError("%s not in group %s" % (member, group))

    def getGroups(self, element = ''):
        """
        return a list of groups this element belongs to

        ::

          >>> getGroups() # list all groups, including the empty groups
          >>> getGroups('*') # all groups, not including empty ones
          >>> getGroups('Q?')
          
        The input string is wildcard matched against each element.
        """
        if not element: return self._group.keys()

        ret = []
        for k, elems in self._group.items():
            for e in elems:
                if fnmatch(e.name, element):
                    ret.append(k)
                    break
        return ret

    def getGroupMembers(self, groups, op, **kwargs):
        """
        return members in a list of groups. 

        can take a union or intersections of members in each group

        - group in *groups* can be exact name or pattern.
        - op = ['union' | 'intersection']

        ::
        
          >>> getGroupMembers(['C02'], op = 'union')
        """
        if groups == None: return None
        ret = {}
        cell = kwargs.get('cell', '*')
        girder = kwargs.get('girder', '*')
        symmetry = kwargs.get('symmetry', '*')

        if groups in self._group.keys():
            return self._group[groups]

        #print __file__, groups
        for g in groups:
            ret[g] = []
            for k, elems in self._group.items():
                if fnmatch(k, g): ret[g].extend([e.name for e in elems])
            #print g, ret[g]

        r = set(ret[groups[0]])
        if op.lower() == 'union':
            for g, v in ret.items():
                r = r.union(set(v))
        elif op.lower() == 'intersection':
            for g, v in ret.items():
                #print __file__, g, len(v), len(r)
                r = r.intersection(set(v))
        else:
            raise ValueError("%s not defined" % op)
        
        return self.getElements(self.sortElements(r))

    def getNeighbors(self, element, group, n):
        """
        Assuming self._elements is in s order

        the element matched with input 'element' string should be unique.
        """

        e0 = self.getElements(element)
        if len(e0) > 1:
            raise ValueError("element %s is not unique" % element)
        elif e0 == None or len(e0) == 0:
            raise ValueError("element %s does not exist" % element)

        e, s = self.getElements(group, point = 'e')
        #print e, s

        i1, i2 = 0, 0
        ret = [[element[:], s0]]
        for i in range(0, len(s)):
            if s[i] > s0[0]:
                #return e[i-1], s[i-1], e[i], s[i]
                i1, i2 = i - 1, i
                break 
            #else: print "s", s0[0], s[i]
        for i in range(n):
            ret.insert(0, [e[i1-i], s[i1-i]])
            ret.append([e[i2+i], s[i2+i]])

        return ret
        
    def __repr__(self):
        s = ''
        ml_name, ml_family = 0, 0
        for e in self._elements:
            if len(e.name) > ml_name: ml_name = len(e.name)
            if e.family and len(e.family) > ml_family:
                ml_family = len(e.family)

        idx = int(1.0+log10(len(self._elements)))
        fmt = "%%%dd %%%ds  %%%ds  %%9.4f %%9.4f\n" % (idx, ml_name, ml_family)
        #print fmt
        for i, e in enumerate(self._elements):
            s = s + fmt % (i, e.name, e.family, e.sb, e.length)
        return s


    def getPhase(self, elem, loc = 'e'):
        """
        return phase
        """

        if isinstance(elem, str):
           elemlst = self.getElements(elem)
        elif isinstance(elem, list):
           elemlst = elem[:]
        else:
           raise ValueError("elem can only be string or list")

        idx = [-1] * len(elemlst)
        phi = np.zeros((len(elemlst), 2), 'd')
        for i,e in enumerate(self._elements):
            if e.name in elemlst: idx[elemlst.index(e.name)] = i
        if loc == 'b': 
            for i, k in enumerate(idx):
                phi[i, :] = self._twiss[k].phi[0, :]
        elif loc == 'c': 
            raise NotImplementedError()
        else:
            # loc == 'end': 
            for i, k in enumerate(idx):
                phi[i, :] = self._twiss[k].phi[-1, :]
        return phi

    def getBeta(self, elem, loc = 'e'):
        """
        return beta function
        """
        if isinstance(elem, str) or isinstance(elem, unicode):
           elemlst = self.getElements(elem)
        elif isinstance(elem, list):
           elemlst = elem[:]
        else:
           raise ValueError("elem can only be string or list")

        idx = [-1] * len(elemlst)
        beta = np.zeros((len(elemlst), 2), 'd')
        for i,e in enumerate(self._elements):
            if not e.name in elemlst: continue
            j = elemlst.index(e.name)
            idx[j] = i
            beta[j, :] = self._twiss[i].beta(loc)
        return beta

    def getEta(self, elem, loc = 'e'):
        """
        return dispersion
        """
        if isinstance(elem, str):
           elemlst = self.getElements(elem)
        elif isinstance(elem, list):
           elemlst = elem[:]
        else:
           raise ValueError("elem can only be string or list")


        idx = [-1] * len(elemlst)
        eta = np.zeros((len(elemlst), 2), 'd')
        for i,e in enumerate(self._elements):
            if e.name in elemlst: idx[elemlst.index(e.name)] = i
        if loc == 'b': 
            for i, k in enumerate(idx):
                eta[i, :] = self._twiss[k].eta[0, :]
        elif loc == 'c': 
            raise NotImplementedError()
        else:
            # loc == 'end': 
            for i, k in enumerate(idx):
                eta[i, :] = self._twiss[k].eta[-1, :]
        return eta
    
    def getTunes(self):
        """
        return tunes
        """
        return self.tune[0], self.tune[1]

    def getBeamlineProfile(self, s1=0.0, s2=1e10):
        prof = []
        for elem in self._elements:
            if elem.se < s1: continue
            elif elem.sb > s2: continue
            x1, y1, c = elem.profile()
            prof.append((x1, y1, c))
        ret = [prof[0]]
        for p in prof[1:]:
            if abs(p[0][0] - ret[-1][0][-1]) >  1e-10:
                ret.append(([ret[-1][0][-1], p[0][0]], [0, 0], 'k'))
            ret.append(p)
        return ret


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
    else:
        girder   = 'G0'
        cell     = 'C00'
        symmetry = '-'
    return cell, girder, symmetry


    
    
