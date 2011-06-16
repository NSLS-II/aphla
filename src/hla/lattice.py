#!/usr/env/python

"""
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
from twiss import Twiss

class Lattice:
    """Lattice"""
    # ginore those "element" when construct the lattice object
    _IGN = ['MCF', 'CHROM', 'TUNE', 'OMEGA', 'DCCT', 'CAVITY']

    def __init__(self, mode = 'undefined'):
        # group name and its element
        self._group = {}
        # guaranteed in the order of s.
        self._elements = []
        # same order of element
        self._twiss = []
        # data set
        self.mode = mode
        self.tune = [ 0.0, 0.0]
        self.chromaticity = [0.0, 0.0]
        self.circumference = 0.0

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
        f[pref+'twiss']   = self.twiss
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
        self.twiss    = f[pref+'twiss']
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

    def init_virtac_twiss(self):
        """Only works from virtac.nsls2.bnl.gov"""
        # s location
        s      = [v for v in caget('SR:C00-Glb:G00{POS:00}RB-S', timeout=30)]
        # twiss at s_end (from Tracy)
        alphax = [v for v in caget('SR:C00-Glb:G00{ALPHA:00}RB-X')]
        alphay = [v for v in caget('SR:C00-Glb:G00{ALPHA:00}RB-Y')]
        betax  = [v for v in caget('SR:C00-Glb:G00{BETA:00}RB-X')]
        betay  = [v for v in caget('SR:C00-Glb:G00{BETA:00}RB-Y')]
        etax   = [v for v in caget('SR:C00-Glb:G00{ETA:00}RB-X')]
        etay   = [v for v in caget('SR:C00-Glb:G00{ETA:00}RB-Y')]
        orbx   = [v for v in caget('SR:C00-Glb:G00{ORBIT:00}RB-X')]
        orby   = [v for v in caget('SR:C00-Glb:G00{ORBIT:00}RB-Y')]
        phix   = [v for v in caget('SR:C00-Glb:G00{PHI:00}RB-X')]
        phiy   = [v for v in caget('SR:C00-Glb:G00{PHI:00}RB-Y')]
        nux = caget('SR:C00-Glb:G00{TUNE:00}RB-X')
        nuy = caget('SR:C00-Glb:G00{TUNE:00}RB-Y')

        self.tune[0], self.tune[1] = nux, nuy
        #print __file__, len(s), len(betax)

        # fix the Tracy bug by adding a new element at the end
        for x in [s, alphax, alphay, betax, betay, etax, etay, orbx, orby,
                  phix, phiy]:
            x.append(x[-1])

        #print __file__, len(s), len(betax)
        for e in self._elements:
            i = e.index
            #print e.name, e.family, s[i]
            if i >= len(s): 
                print "Missing element in PV waveform", e.name, e.family
                continue
            self._twiss.append(Twiss())
            # the first one is marker, index > 0
            # PV gets twiss at s_end
            self._twiss[-1]._s[-1]       = s[i]
            self._twiss[-1]._beta[-1,0] = betax[i]
            self._twiss[-1]._beta[-1,1] = betay[i]
            self._twiss[-1]._alpha[-1,0]= alphax[i]
            self._twiss[-1]._alpha[-1,1]= alphay[i]
            self._twiss[-1]._eta[-1,0]  = etax[i]
            self._twiss[-1]._eta[-1,1]  = etay[i]
            self._twiss[-1]._phi[-1,0]  = phix[i]
            self._twiss[-1]._phi[-1,1]  = phiy[i]

            # s_beg, assuming i > 0
            if i == 0: k = 0
            else: k = i - 1
            self._twiss[-1]._s[0]       = s[k]
            self._twiss[-1]._beta[0,0] = betax[k]
            self._twiss[-1]._beta[0,1] = betay[k]
            self._twiss[-1]._alpha[0,0]= alphax[k]
            self._twiss[-1]._alpha[0,1]= alphay[k]
            self._twiss[-1]._eta[0,0]  = etax[k]
            self._twiss[-1]._eta[0,1]  = etay[k]
            self._twiss[-1]._phi[0,0]  = phix[k]
            self._twiss[-1]._phi[0,1]  = phiy[k]
            
        # set s_beg
        #print self.twiss
            
    def init_virtac_group(self):
        """
        initialize the "group" settings, add member to group of its
        *cell*, *girder* and *symmetry* parsed from its name
        """

        for elem in self._elements:
            self.addGroup(elem.cell)
            self.addGroupMember(elem.cell, elem.name)
            self.addGroup(elem.girder)
            self.addGroupMember(elem.girder, elem.name)
            self.addGroup(elem.symmetry)
            self.addGroupMember(elem.symmetry, elem.name)

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

    def getElements(self, group):
        """
        get elements.
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
        clear the old groups, fill with new data
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
        call signature::
        
          addGroup(group)
          
        *group* is a combination of alphabetic and numeric characters and
         underscores. i.e. "[a-zA-Z0-9\_]" 
        """
        if self._illegalGroupName(group): return
        if not self._group.has_key(group):
            self._group[group] = []

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
                if e.s < elem.s: continue
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

    def getGroups(self, element):
        """
        return a list of groups this element belongs to

        ::

          getGroups('*')
          getGroups('Q?')

        The input string is wildcard matched against each element.
        """
        ret = []
        for k, elems in self._group.items():
            for e in elems:
                if fnmatch(e.name, element):
                    ret.append(k)
                    break
        return ret

    def getGroupMembers(self, groups, op):
        """
        return members in a list of groups. 

        can take a union or intersections of members in each group

        - group in *groups* can be exact name or pattern.
        - op = ['union' | 'intersection']
        """
        if groups == None: return None
        ret = {}
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

        e0, s0 = self.getElements(element, point = 'e')
        #print element,e0, s0
        #return
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
            s = s + fmt % (i, e.name, e.family, e.s, e.length)
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

    def _importChannelFinderData(self, cfa):
        """
        call signature::
        
          importChannelFinderData(self, cfa)

        .. seealso::

          :class:`~hla.chanfinder.ChannelFinderAgent`

        load info from channel finder server/data
        """
        elems = cfa.sortElements(cfa.getElements())
        cnt = {'BPMX':0, 'BPMY':0, 'TRIMD':0, 'TRIMX':0, 'TRIMY':0,
               'SEXT':0, 'QUAD':0}
        # ignore MCF/TUNE/ORBIT ....
        for e in elems:
            prop = cfa.getElementProperties(e)
            if prop[cfa.ELEMTYPE] in self._IGN: continue

            #counting each family
            if cnt.has_key(prop[cfa.ELEMTYPE]):
                cnt[prop[cfa.ELEMTYPE]] += 1
            else:
                cnt[prop[cfa.ELEMTYPE]] = 0

            #
            #print prop
            param = {'family':prop[cfa.ELEMTYPE],
                     'se':prop[cfa.SPOSITION],
                     'sb':prop[cfa.SPOSITION] - prop[cfa.LENGTH],
                     'efflen': prop[cfa.LENGTH],
                     'girder': prop[cfa.GIRDER],
                     'cell': prop[cfa.CELL],
                     'symmetry': prop[cfa.ELEMSYM],
                     'index': prop[cfa.ELEMIDX]}
            elemname = prop[cfa.ELEMNAME]
            self._elements.append(Element(elemname, **param))
            self.addGroupMember(prop[cfa.ELEMTYPE], elemname, True)
            self.addGroupMember(prop[cfa.CELL], elemname, True)
            self.addGroupMember(prop[cfa.GIRDER], elemname, True)
            self.addGroupMember(prop[cfa.ELEMSYM], elemname, True)
        # since single element (BPM) can be both BPMX/BPMY, we need scan
        # pv record again
        for pv in cfa.getChannels():
            prop = cfa.getChannelProperties(pv)
            self.addGroupMember(prop[cfa.ELEMTYPE], prop[cfa.ELEMNAME], True)
            #self.addGroupMember(prop[cfa.ELEMNAME], prop[cfa.ELEMNAME], True)

        self.circumference = self._elements[-1].se
        #print __file__, "Imported elements:", len(self.element)
        #print __file__, cnt

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



def createLatticeFromTxtTable(lattable):
    """
    call signature::

      createLatticeFromTxtTable(lattable)

    create lattice object from the table used for Tracy-VirtualIOC. The table
    has columns in the following order:

    =======   =============================================
    Index     Description
    =======   =============================================
    1         element index in the whole beam line
    2         channel for read back
    3         channel for set point (NULL for readonly element)
    4         element physics name (unique)
    5         element length (effective)
    6         s location of its exit
    7         magnet family(type)
    8         element device name
    =======   =============================================

    Data are deliminated by spaces.
    """

    #print "Importing file:", lattable

    cnt = {'BPM':0, 'BPMX':0, 'BPMY':0, 'TRIM':0, \
               'TRIMD':0, 'TRIMX':0, 'TRIMY':0, 'SEXT':0, 'QUAD':0}

    lat = Lattice()
    f = open(lattable, 'r').readlines()
    for s in f[1:]:
        rec = {}
        t = s.split()
        rec['index']   = int(t[0])     # index
        rb   = t[1].strip()  # PV readback
        sp   = t[2].strip()  # PV setpoint
        phy  = t[3].strip()  # name
        rec['length']  = float(t[4])   # length
        rec['sb']      = float(t[5])   # s_end location
        rec['family']  = t[6].strip()  # group
        rec['devname'] = t[7].strip()

        # parse cell/girder/symmetry from name
        rec['cell'], rec['girder'], rec['symmetry'] = parseElementName(phy)

        if not lat.hasElement(phy):
            elem = Element(phy, **rec)
            lat._elements.append(elem)
            lat._twiss.append(Twiss())
        else:
            elem = lat[phy]

        if rb != 'NULL': elem.appendStatusPv((caget, rb, 'readback'))
        if sp != 'NULL': elem.appendStatusPv((caget, sp, 'setpoint'))

    # ---- modify the default channel -----
    # most of the magnets have two PV, read/set
    # BPM has 6 so far
    for i in range(lat.size()):
        if len(lat[i]._status) == 2 and lat[i]._status[0][-1] == 'readback' \
               and lat[i]._status[1][-1] == 'setpoint':
            f, x, desc = lat[i]._status[0]
            lat[i].updateEget((f, x, desc))
            f, x, desc = lat[i]._status[1]
            lat[i].updateEput((f, x, desc))
            continue
        elif lat[i].family.startswith('BPM') and len(lat[i]._status) == 6:
            for rec in lat[i]._status:
                f, x, desc = rec
                if x.endswith('BBA:X') or x.endswith('BBA:Y'): continue
                if x.endswith('-I'):
                    lat[i].updateEget((f, x, desc))
                elif x.endswith('GOLDEN:X') or x.endswith('GOLDEN:Y'):
                    lat[i].updateEput((f, x, 'golden'))
                else:
                    print lat[i].name, len(lat[i]._status)
        elif lat[i].family.startswith('SEXT') and len(lat[i]._status) > 2:
            for rec in lat[i]._status:
                f, x, desc = rec
                if x.find('Sext_P') > 0: continue
                if x.endswith('-I'):
                    lat[i].updateEget((f, x, desc))
                elif x.endswith('-SP'):
                    lat[i].updateEput((f, x, desc))
                else:
                    print lat[i].name, len(lat[i]._status)
        elif lat[i].name in ['TUNEX', 'TUNEY', 'CHROMX', 'CHROMY', 'DCCT', 'MCF', 'OMEGA']:
            lat[i].updateEget(lat[i]._status[0])
        else:
            print lat[i].name

    # check the default
    for i in range(lat.size()):
        if not lat[i]._eget_val or not lat[i]._eput_val:
            print lat[i] #, lat[i]._eget_val, lat[i]._eput_val
            #print lat[i]._status

    print "Lattice size:", lat.size()
    return lat

class LatticeSet:
    """
    Manage a set of lattice data
    """

    def __init__(self):
        pass

    def load(self, f):
        pass

    def save(self, f):
        pass

    
    
