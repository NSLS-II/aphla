#!/usr/env/python

"""
lattice
~~~~~~~

:author: Lingyun Yang
:license:

defines lattice related classes and functions.
"""

import re
from math import log10
import shelve
from . import INF
import numpy as np
from fnmatch import fnmatch

#from cothread.catools import caget, caput
from catools import caget, caput

def parseElementName(name):
    """
    searching G*C*A type of string. e.g. "CFXH1G1C30A" will be parsed as
    girder="G1", cell="C30", symmetry="A"
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


class Element:
    """Element"""
    def __init__(self, name = '', family = '', s_beg = 0.0, s_end = 0.0,
                 effective_length = 0, cell = '', girder = '', symmetry = '',
                 sequence = [0, 0]):
        self.index = -1
        self.name = name[:]
        self.family = family[:]
        self.s_beg = s_beg
        self.s_end = s_end
        self.len_eff = effective_length
        self.len_phy = 0.0
        self.cell = cell
        self.girder = girder
        self.symmetry = symmetry
        self.sequence = sequence[:]

    def profile(self, vscale=1.0):
        b, e = self.s_beg, self.s_end
        h = vscale
        if self.family == 'QUAD':
            return [b, b, e, e], [0, h, h, 0], 'k'
        elif self.family == 'DIPOLE':
            return [b, b, e, e, b, b, e, e], [0, h, h, -h, -h, h, h, 0], 'k'
        elif self.family == 'SEXT':
            return [b, b, e, e], [0, 1.25*h, 1.25*h, 0], 'k'
        elif self.family in ['TRIMX', 'TRIMY']:
            return [b, (b+e)/2.0, (b+e)/2.0, (b+e)/2.0, e], \
                [0, 0, h, 0, 0], 'r'
        elif self.family in ['BPMX', 'BPMY']:
            return [b, (b+e)/2.0, (b+e)/2.0, (b+e)/2.0, e], \
                [0, 0, h, 0, 0], 'b'        
        else:
            return [b, e], [0, 0], 'k'

class Twiss:
    """twiss"""
    def __init__(self):
        self.s     = np.zeros(3, 'd')
        self.alpha = np.zeros((3, 2), 'd')
        self.beta  = np.zeros((3, 2), 'd')
        self.gamma = np.zeros((3, 2), 'd')
        self.eta   = np.zeros((3, 2), 'd')
        self.phi   = np.zeros((3, 2), 'd')
        self.elemname = ''
        
class Lattice:
    """Lattice"""
    # ginore those "element" when construct the lattice object
    IGN = ['MCF', 'CHROM', 'TUNE', 'OMEGA', 'DCCT', 'CAVITY']

    def __init__(self):
        self.__group = {}
        # guaranteed in the order of s.
        self.element = []
        # same order of element
        self.twiss = []
        self.mode = 'undefined'
        self.tune = [ 0.0, 0.0]
        self.chromaticity = [0.0, 0.0]

    def save(self, fname, dbmode = 'c'):
        """
        call signature::
        
          save(self, fname, dbmode='c')

        save the lattice into binary data, using writing *dbmode*
        """
        f = shelve.open(fname, dbmode)
        pref = "lat.%s." % self.mode
        f[pref+'group']   = self.__group
        f[pref+'element'] = self.element
        f[pref+'twiss']   = self.twiss
        f[pref+'mode']    = self.mode
        f[pref+'tune']    = self.tune
        f[pref+'chromaticity'] = self.chromaticity
        f.close()

    def load(self, fname, mode = ''):
        """
        call signature::
        
          load(self, fname, mode='')

        load the lattice from binary data
        """
        f = shelve.open(fname, 'r')
        #modes = []
        #for k in f.keys():
        #    if re.match(r'lat\.\w+\.mode', k): print "mode:", k
        if not mode:
            pref = "lat."
        else:
            pref = 'lat.%s.' % mode
        self.__group  = f[pref+'group']
        self.element  = f[pref+'element']
        self.twiss    = f[pref+'twiss']
        self.mode     = f[pref+'mode']
        self.tune     = f[pref+'tune']
        self.chromaticity = f[pref+'chromaticity']
        f.close()

    def importChannelFinderData(self, cfa):
        """
        call signature::
        
          importChannelFinderData(self, cfa)

        .. seealso::

          :class:`~hla.chanfinder.ChannelFinderAgent`

        load info from channel finder server/data
        """
        elems = cfa.sortElements(cfa.getElements())
        cnt = {'BPMX':0, 'BPMY':0, 'TRIMD':0, 'TRIMX':0, 'TRIMY':0, 'SEXT':0, 'QUAD':0}
        # ignore MCF/TUNE/ORBIT ....
        for e in elems:
            prop = cfa.getElementProperties(e)
            if prop[cfa.ELEMTYPE] in self.IGN: continue

            #counting each family
            if cnt.has_key(prop[cfa.ELEMTYPE]):
                cnt[prop[cfa.ELEMTYPE]] += 1
            else:
                cnt[prop[cfa.ELEMTYPE]] = 0

            #
            #print prop
            self.element.append(
                Element(prop[cfa.ELEMNAME], prop[cfa.ELEMTYPE], 0.0,
                        prop[cfa.SPOSITION], prop[cfa.LENGTH], prop[cfa.CELL], 
                        prop[cfa.GIRDER], prop[cfa.ELEMSYM]))
            self.element[-1].index = prop[cfa.ELEMIDX]
            for g in [prop[cfa.ELEMTYPE], prop[cfa.CELL], prop[cfa.GIRDER],
                      prop[cfa.ELEMSYM]]:
                if self.__group.has_key(g):
                    self.__group[g].append(prop[cfa.ELEMNAME])
                else: self.__group[g] = [prop[cfa.ELEMNAME]]
            
        # adjust s_beg
        for e in self.element:
            e.s_beg = e.s_end - e.len_eff
        #print "# import elements:", len(self.element)
        #print cnt
        
        # since single element (BPM) can be both BPMX/BPMY, we need scan
        # pv record again
        for pv in cfa.getChannels():
            prop = cfa.getChannelProperties(pv)
            if not self.__group.has_key(prop[cfa.ELEMTYPE]):
                self.__group[prop[cfa.ELEMTYPE]] = [prop[cfa.ELEMNAME]]
            elif not prop[cfa.ELEMNAME] in self.__group[prop[cfa.ELEMTYPE]]:
                self.__group[prop[cfa.ELEMTYPE]].append(prop[cfa.ELEMNAME])
        

    def mergeGroups(self, parent, children):
        """
        merge child group(s) into a parent group
        
        Example::

            mergeGroups('BPM', ['BPMX', 'BPMY'])
            mergeGroups('TRIM', ['TRIMX', 'TRIMY'])
        """
        if isinstance(children, str):
            chlst = [children]
        elif isinstance(children, list):
            chlist = children[:]
        else:
            raise ValueError("children can be string or list of string")

        if not self.__group.has_key(parent):
            self.__group[parent] = []

        for child in chlist:
            if not self.__group.has_key(child): continue
            for elem in self.__group[child]:
                if elem in self.__group[parent]: continue
                self.__group[parent].append(elem)

    def importLatticeTable(self, lattable):
        """
        call signature::
        
          importLatticeTable(self, lattable)

        Import the table used for Tracy-VirtualIOC. The table has columns
        in the following order:

        =======   =============================================
        Index     Description
        =======   =============================================
        1         element index in the whole beam line
        2         channel for read back
        3         channel for set point
        4         element phys name (unique)
        5         element length (effective)
        6         s location of its exit
        7         magnet family(type)
        =======   =============================================

        Data are deliminated by spaces.
        """

        #print "Importing file:", lattable

        cnt = {'BPM':0, 'BPMX':0, 'BPMY':0, 'TRIM':0, \
                   'TRIMD':0, 'TRIMX':0, 'TRIMY':0, 'SEXT':0, 'QUAD':0}

        for k in cnt.keys(): self.__group[k] = []

        f = open(lattable, 'r').readlines()
        for s in f[1:]:
            t = s.split()
            idx  = int(t[0])     # index
            rb   = t[1].strip()  # PV readback
            sp   = t[2].strip()  # PV setpoint
            phy  = t[3].strip()  # name
            L    = float(t[4])   # length
            s2   = float(t[5])   # s_end location
            grp  = t[6].strip()  # group

            # parse cell/girder/symmetry from name
            cell, girder, symmetry = parseElementName(phy)
            self.element.append(Element(phy, grp, 0.0, s2, L,
                                        cell, girder, symmetry))
            self.element[-1].index = idx

            # count element numbers in each type
            if cnt.has_key(grp): cnt[grp] += 1

            if self.__group.has_key(grp): self.__group[grp].append(phy)
            else: self.__group[grp] = [phy]
            
            # in lat_conf_table, used only BPM as groupname, not BPMX/BPMY
            if grp == 'BPM':
                if rb[-2:] == '-X':
                    self.__group['BPMX'].append(phy)
                    cnt['BPMX'] += 1
                elif rb[-2:] == '-Y': 
                    self.__group['BPMY'].append(phy)
                    cnt['BPMY'] += 1
                else:
                    raise ValueError("pv %s pattern not recognized" % rb)
            if grp[:4] == 'TRIM':
                self.__group['TRIM'].append(phy)

        # adjust s_beg
        for e in self.element:
            e.s_beg = e.s_end - e.len_eff

        if False:
            for k,v in self.__group.items():
                print k, len(v)

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
        for e in self.element:
            i = e.index
            #print e.name, e.family, s[i]
            if i >= len(s): 
                print "Missing element in PV waveform", e.name, e.family
                continue
            self.twiss.append(Twiss())
            # the first one is marker, index > 0
            # PV gets twiss at s_end
            self.twiss[-1].s[-1]       = s[i]
            self.twiss[-1].beta[-1,0] = betax[i]
            self.twiss[-1].beta[-1,1] = betay[i]
            self.twiss[-1].alpha[-1,0]= alphax[i]
            self.twiss[-1].alpha[-1,1]= alphay[i]
            self.twiss[-1].eta[-1,0]  = etax[i]
            self.twiss[-1].eta[-1,1]  = etay[i]
            self.twiss[-1].phi[-1,0]  = phix[i]
            self.twiss[-1].phi[-1,1]  = phiy[i]

            # s_beg, assuming i > 0
            if i == 0: k = 0
            else: k = i - 1
            self.twiss[-1].s[0]       = s[k]
            self.twiss[-1].beta[0,0] = betax[k]
            self.twiss[-1].beta[0,1] = betay[k]
            self.twiss[-1].alpha[0,0]= alphax[k]
            self.twiss[-1].alpha[0,1]= alphay[k]
            self.twiss[-1].eta[0,0]  = etax[k]
            self.twiss[-1].eta[0,1]  = etay[k]
            self.twiss[-1].phi[0,0]  = phix[k]
            self.twiss[-1].phi[0,1]  = phiy[k]
            
        # set s_beg
        #print self.twiss
            
    def init_virtac_group(self):
        """
        initialize the "group" settings, add member to group of its
        *cell*, *girder* and *symmetry* parsed from its name
        """

        for elem in self.element:
            self.addGroup(elem.cell)
            self.addGroupMember(elem.cell, elem.name)
            self.addGroup(elem.girder)
            self.addGroupMember(elem.girder, elem.name)
            self.addGroup(elem.symmetry)
            self.addGroupMember(elem.symmetry, elem.name)

    def sortElements(self, elemlist):
        """
        sort the element list to the order of *s*
        """
        ret = []
        for e in self.element:
            if e.name in ret: continue
            if e.name in elemlist:
                ret.append(e.name)

        #
        if len(ret) < len(elemlist):
            raise ValueError("Some elements are missing in the results")
        elif len(ret) > len(elemlist):
            raise ValueError("something wrong on sorting element list")
 
        return ret[:]

    def getLocations(self, elems, point):
        """
        if elems is a string, do exact match. return single number.  if
        elems is a list do exact match on each of them, return a
        list. None if the element in this list is not found.
        """
        if isinstance(elems, str):
            e, s = self.getElements(elems, point)
            return s
        elif isinstance(elems, list):
            ret = [None] * len(elems)
            for elem in self.element:
                if elem.name in elems:
                    idx = elems.index(elem.name)
                    if point == 'begin': ret[idx] = elem.s_beg
                    elif point == 'end': ret[idx] = elem.s_end
                    elif point == 'middle': ret[idx] = elem.s_mid
                    else: ret[idx] = elem.s_end
                
            return ret
        
    def getElements(self, group, point = ''):
        """
        get elements and their locations.

        parameter *point* = ['begin', 'middle', 'end'] tells the s location
        returned with element name at at the begin, middle or end of the
        elements. For a nonempty string, it returns s at the 'end'.

        if *point* == "", location is not returned. 

        no duplicate element name outputed.
        """
        ret, loc = [], []
        s = point.lower()
        #print "... get elements ...", s
        for e in self.element:
            #print group, e.name, e.family,
            if e.name in ret: continue
            if fnmatch(e.name, group) or fnmatch(e.family, group) or \
                    (self.__group.has_key(group) and e.name in self.__group[group]):
                ret.append(e.name)
                if s == 'begin': loc.append(e.s_beg)
                elif s == 'end': loc.append(e.s_end)
                elif s == 'middle': loc.append(e.s_mid)
                else: loc.append(e.s_end)
            else:
                #print e.name
                pass
        if point: return ret, loc
        else: return ret

    def getElementsCgs(self, group, cell = [], girder = [],
                    sequence = []):
        """
        call signature::
        
          getElementsCgs(self, group, cell=[], girder=[], sequence=[])

        Get a list of elements from cell, girder and sequence
        """
        if group in self.__group.keys():
            return self.__group[group][:]

        elem = []
        #print group
        for e in self.element:
            # self.element is unique on each name, but just in case ....
            if e.name in elem: continue
            if group and not fnmatch(e.name, group) \
                    and not fnmatch(e.family, group):
                continue
            if cell and e.cell != cell: continue
            if girder and e.girder != girder: continue
            if sequence and (e.sequence[0] != sequence[0] \
                                 or e.sequence[1] != sequence[1]):
                continue

            elem.append(e.name)

        # may have duplicate element
        #return [v for v in set(elem)]
        return elem

    def __illegalGroupName(self, group):
        # found character not in [a-zA-Z0-9_]
        if re.search(r'[^\w]+', group):
            raise ValueError("Group name must be in [a-zA-Z0-9_]+")
            #return False
        else: return False

    def addGroup(self, group):
        """
        call signature::
        
          addGroup(self, group)
          
        *group* is a combination of alphabetic and numeric characters and
         underscores. i.e. "[a-zA-Z0-9\_]" 
        """
        if self.__illegalGroupName(group): return
        if not self.__group.has_key(group):
            self.__group[group] = []

    def removeGroup(self, group):
        """
        call signature::

          removeGroup(self, group)

        remove a group only when it is empty
        """
        if self.__illegalGroupName(group): return
        if not self.__group.has_key(group):
            raise ValueError("Group %s does not exist" % group)
        if len(self.__group[group]) > 0:
            raise ValueError("Group %s is not empty" % group)
        # remove it!
        self.__group.pop(group)

    def addGroupMember(self, group, member):
        """
        add member to group

        group must exist before.
        """
        if self.__group.has_key(group):
            self.__group[group].append(member)
        else:
            raise ValueError("Group %s does not exist" % group)

    def hasGroup(self, group):
        """
        check group exists or not.
        """
        return self.__group.has_key(group)

    def removeGroupMember(self, group, member):
        """
        remove member from group
        """
        if not self.hasGroup(group):
            raise ValueError("Group %s does not exist" % group)
        if member in self.__group[group]:
            self.__group[group].remove(member)
        else:
            raise ValueError("%s not in group %s" % (member, group))

    def getGroups(self, element):
        """
        return a list of groups this element is in
        """
        ret = []
        for k, elems in self.__group.items():
            for e in elems:
                if fnmatch(e, element):
                    ret.append(k)
                    break
        return ret

    def getGroupMembers(self, groups, op):
        """
        return members in a list of groups. 

        can take a union or intersections of members in each group
        """
        if groups == None: return None
        ret = {}
        #print __file__, groups
        for g in groups:
            ret[g] = []
            for k, elems in self.__group.items():
                if fnmatch(k, g): ret[g].extend(elems)
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
        
        return self.sortElements(r)

    def getNeighbors(self, element, group, n):
        """Assuming self.element is in s order"""
        #elem = [i for i in range(len(self.element)) \
        #            if self.element[i].name == element]
        #print element,elem

        e0, s0 = self.getElements(element, point = 'end')
        #print element,e0, s0
        #return
        if len(e0) > 1:
            raise ValueError("element %s is not unique" % element)
        elif e0 == None or len(e0) == 0:
            raise ValueError("element %s does not exist" % element)

        e, s = self.getElements(group, point = 'end')
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
        for e in self.element:
            if len(e.name) > ml_name: ml_name = len(e.name)
            if len(e.family) > ml_family: ml_family = len(e.family)

        idx = int(1.0+log10(len(self.element)))
        fmt = "%%%dd %%%ds  %%%ds  %%9.4f  %%9.4f\n" % (idx, ml_name, ml_family)
        #print fmt
        for i, e in enumerate(self.element):
            s = s + fmt % (i, e.name, e.family, e.s_beg, e.s_end)
        return s


    def getPhase(self, elem, loc = 'end'):
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
        for i,e in enumerate(self.element):
            if e.name in elemlst: idx[elemlst.index(e.name)] = i
        if loc == 'begin': 
            for i, k in enumerate(idx):
                phi[i, :] = self.twiss[k].phi[0, :]
        elif loc == 'middle': 
            raise NotImplementedError()
        else:
            # loc == 'end': 
            for i, k in enumerate(idx):
                phi[i, :] = self.twiss[k].phi[-1, :]
        return phi

    def getBeta(self, elem, loc = 'end'):
        """
        return beta function
        """
        if isinstance(elem, str):
           elemlst = self.getElements(elem)
        elif isinstance(elem, list):
           elemlst = elem[:]
        else:
           raise ValueError("elem can only be string or list")

        idx = [-1] * len(elemlst)
        beta = np.zeros((len(elemlst), 2), 'd')
        for i,e in enumerate(self.element):
            if e.name in elemlst: idx[elemlst.index(e.name)] = i
        if loc == 'begin': 
            for i, k in enumerate(idx):
                beta[i, :] = self.twiss[k].beta[0, :]
        elif loc == 'middle': 
            raise NotImplementedError()
        else:
            # loc == 'end': 
            for i, k in enumerate(idx):
                beta[i, :] = self.twiss[k].beta[-1, :]
        return beta

    def getEta(self, elem, loc = 'end'):
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
        for i,e in enumerate(self.element):
            if e.name in elemlst: idx[elemlst.index(e.name)] = i
        if loc == 'begin': 
            for i, k in enumerate(idx):
                eta[i, :] = self.twiss[k].eta[0, :]
        elif loc == 'middle': 
            raise NotImplementedError()
        else:
            # loc == 'end': 
            for i, k in enumerate(idx):
                eta[i, :] = self.twiss[k].eta[-1, :]
        return eta
    
    def getTunes(self):
        """
        return tunes
        """
        return self.tune[0], self.tune[1]

    def getBeamlineProfile(self, s1=0.0, s2=1e10):
        prof = []
        for elem in self.element:
            if elem.s_end < s1: continue
            elif elem.s_beg > s2: continue
            x1, y1, c = elem.profile()
            prof.append((x1, y1, c))
        ret = [prof[0]]
        for p in prof[1:]:
            if abs(p[0][0] - ret[-1][0][-1]) >  1e-10:
                ret.append(([ret[-1][0][-1], p[0][0]], [0, 0], 'k'))
            ret.append(p)
        return ret


