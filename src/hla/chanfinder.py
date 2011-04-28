#!/usr/bin/env python

"""
This module mimics Channel Finder service, and makes developing HLA earlier.

It also manages configuration data of HLA.
"""

import cadict
import re, shelve, sys, os
from fnmatch import fnmatch
from time import gmtime, strftime
from lattice import parseElementName


class ChannelFinderAgent:
    """
    Channel Finder Agent

    This module builds a local cache of channel finder service.
    """
    ELEMIDX   = 'ordinal'
    ELEMNAME  = 'elem_name'
    ELEMTYPE  = 'elem_type'
    ELEMSYM   = 'symmetry'
    CELL      = 'cell'
    GIRDER    = 'girder'
    DEVNAME   = 'dev_name'
    LENGTH    = 'length'
    SPOSITION = 's_position'
    ACCSYSTEM = 'system'
    PVHANDLE  = 'handle'
    TAGSKEY   = '~tags'

    def __init__(self):
        self.__d = {}
        self.__cdate = strftime("%Y-%m-%dT%H:%M:%S", gmtime())
        self.__elempv = {}
        self.__devpv = {}

    def save(self, fname, dbmode = 'c'):
        """
        call signature::
        
          save(self, fname, dbmode = 'c')

        save the configuration into binary data

        *dbmode* has same meaning as in *shelve*/*pickle*/*anydbm* module

        ======   ==========================================
        DBMode   Meaning
        ======   ==========================================
        'r'      Open existing database for reading only(default)
        'w'      Open existing database for reading and writing
        'c'      Open database for reading and writing, creating one if it doesn't exist.
        'n'      Always create a new, empty database, open for reading and writing
        ======   ==========================================
        """
        f = shelve.open(fname, dbmode)
        f['cfa.data']        = self.__d
        f['cfa.create_date'] = self.__cdate
        f.close()

    def load(self, fname):
        f = shelve.open(fname, 'r')
        self.__d       = f['cfa.data']
        self.__cdate   = f['cfa.create_date']
        f.close()

        # rebuild the elempv and devpv dict
        self.__elempv = {}
        self.__devpv = {}
        for k, v in self.__d.items():
            # elempv
            if self.__elempv.has_key(v[self.ELEMNAME]):
                self.__elempv[v[self.ELEMNAME]].append(k)
            else:
                self.__elempv[v[self.ELEMNAME]] = [k]
            # devpv
            if self.__devpv.has_key(v[self.DEVNAME]):
                self.__devpv[v[self.DEVNAME]].append(k)
            else:
                self.__devpv[v[self.DEVNAME]] = [k]

            # fix the chrom/tune
            if v[self.ELEMNAME] == 'TUNE':
                if k.find('RB-X') > -1:
                    v[self.ELEMNAME] = v[self.ELEMNAME] + 'X'
                    if v[self.ELEMTYPE][-1] == 'X': v[self.ELEMTYPE] = v[self.ELEMTYPE][:-1]
                if k.find('RB-Y') > -1:
                    v[self.ELEMNAME] = v[self.ELEMNAME] + 'Y'
                    if v[self.ELEMTYPE][-1] == 'Y': v[self.ELEMTYPE] = v[self.ELEMTYPE][:-1]
                
            if v[self.ELEMNAME] == 'CHROM':
                if k.find('RB-X') > -1:
                    v[self.ELEMNAME] = v[self.ELEMNAME] + 'X'
                    if v[self.ELEMTYPE][-1] == 'X': v[self.ELEMTYPE] = v[self.ELEMTYPE][:-1]
                if k.find('RB-Y') > -1:
                    v[self.ELEMNAME] = v[self.ELEMNAME] + 'Y'
                    if v[self.ELEMTYPE][-1] == 'Y': v[self.ELEMTYPE] = v[self.ELEMTYPE][:-1]


    def matchProperties(self, pv, prop=None):
        """
        check if all given properties are defined for this pv.
        """
        if not self.__d.has_key(pv): return False
        if not prop: return True

        for  k, v in prop.items():
            if not self.__d[pv].has_key(k) or \
                    self.__d[pv][k] != v:
                return False

        return True

    def matchTags(self, pv, tags=None):
        """
        check if given tags are defined for this pv.

        Example::

          matchTags('SR:C30-MG:G01A{VCM:FH2}Fld-I', 'default.get')
          matchTags('SR:C30-MG:G01A{VCM:FH2}Fld-I', ['default.get', 'orm'])
          
        if the pv does not exist, return False.

        it always return True if pv exists but no tags are given.
        """
        if not self.__d.has_key(pv): return False
        if not tags: return True

        if isinstance(tags, str):
            taglst = [ tags ]
        elif isinstance(tags, list):
            taglst = [tag for tag in tags]
        else:
            raise ValueError("tags can only be string or a list")

        for tag in tags:
            if not tag in self.__d[pv][self.TAGSKEY]: return False
        return True
            
    def matchRecord(self, pv, propt=None, tags=None):
        """
        check if the given property and tags match with pv
        
        Example::
        
            matchRecord('SR:C30-MG:G01A{VCM:FH2}Fld-I', {'cell':'C30', 'girder':'G01'}, 'default.set')
            matchRecord('SR:C30-MG:G01A{VCM:FH2}Fld-I', {'cell':'C30'}, ['default.set', 'orm'])
        """
        if not self.__d.has_key(pv): return False

        parentpropt = self.__d[pv]
        if propt:
            for k,v in propt.items():
                if not parentpropt.has_key(k) or \
                        parentpropt[k] != v: return False
        if tags:
            for tag in tags:
                if not tag in parentpropt[self.TAGSKEY]:
                    return False
        return True

    def _repr_channel(self, pv):
        s = pv + '\n'
        if not self.__d.has_key(pv): return s
        rec = self.__d[pv]
        for prop in rec:
            if prop == '~tags': continue
            s = s + " %s: %s\n" % (prop, rec[prop])
        s = s + " TAGS: [ " + ', '.join(rec['~tags']) + ' ]\n'
        return s

    def __repr__(self):
        s = ""
        for k,v in self.__d.items():
            s = s + "%s\n" % k
            for prop in v.keys():
                if prop == '~tags': continue
                s = s + " %s: %s\n" % (prop, v[prop])
            s = s + " TAGS: " + ', '.join(v['~tags']) + '\n'
        return s

    def channel(self, pv):
        return self._repr_channel(pv)
    
    def updateChannel(self, pv, props={}, tags=[]):
        for k,v in props.items():
            if k == self.TAGSKEY: continue
            self.__d[pv][k] = v
        for t in tags:
            if t in self.__d[pv][self.TAGSKEY]: continue
            self.__d[pv][self.TAGSKEY].append(t)

    def getElementChannel(self, elemlist, prop=None, tags=None, unique=False):
        """
        each element in *elemlst* may have several PVs fits *prop* and *tags*.

        return 2D list
        """
        if isinstance(elemlist, str):
            elemlst = [elemlist]
            #raise ValueError("expecting a list of element")
        elif isinstance(elemlist, list):
            elemlst = elemlist[:]
        else:
            raise ValueError("expecting a list of elements or single element")

        ret = []
        for elem in elemlst:
            pvl = self.__getElementChannels(elem, prop, tags)
            if unique and len(pvl) > 1:
                for pp in pvl:
                    print pp, self.__d[pp]
                raise ValueError("Channel of %s is not unique: %s" % (elem, ', '.join(pvl)))
            elif unique:
                ret.extend(pvl)
            else:
                ret.append(pvl)
        return ret[:]
                    
    def getGroupChannel(self, element, prop = {}, tags = []):
        if not self.__elempv.has_key(element):
            return None
        if len(self.__elempv[element]) == 0: return None
        # check against properties
        ret = []
        msg = ''
        for pv in self.__elempv[element]:
            agreed = True
            for k,v in prop.items():
                if not self.__d[pv].has_key(k):
                    agreed = False
                    msg = '%s has no property "%s"' % (pv, k)
                    break
                elif self.__d[pv][k] != v:
                    agreed = False
                    msg = '%s: %s != %s' % (pv, self.__d[pv][k], v)
                    break
            for tag in tags:
                if not tag in self.__d[pv]['~tags']:
                    agreed = False
                    msg = '%s is not in tags' % tag
                    break
            if agreed: ret.append(pv)
        if len(ret) == 0: return None
        elif len(ret) == 1: return ret[0]
        else: return ret
    
    def getChannels(self, prop = {}, tags = []):
        ret = []
        for k,v in self.__d.items():
            #print elem,
            if self.matchProperties(k, prop) and self.matchTags(k, tags):
                ret.append(k)
        return ret

    def __getElementChannels(self, elem, prop = {}, tags = []):
        """*elem* is the exact name of an element.

        Returns a list of matched PVs."""
        if not self.__elempv.has_key(elem): return None
        ret = []
        for pv in self.__elempv[elem]:
            if self.matchProperties(pv, prop) and \
                    self.matchTags(pv, tags):
                ret.append(pv)
        return ret

    def checkMissingChannels(self, pvlist):
        for i, line in enumerate(open(pvlist, 'r').readlines()):
            if self.__d.has_key(line.strip() ): continue
            print "Line: %d %s" % (i, line.strip())
        #print "-- DONE --"

    def __cmp_elem_loc(self, a, b):
        # elements must exist
        i = self.__d[self.__elempv[a][0]]['ordinal']
        j = self.__d[self.__elempv[b][0]]['ordinal']
        return i-j

    def sortElements(self, elemlst):
        ret = sorted(elemlst, self.__cmp_elem_loc )
        #for elem in ret:
        #    print elem, self.__d[self.__elempv[elem][0]]['s_position']
        return ret

    def getChannelProperties(self, pv):
        if not self.__d.has_key(pv): return None
        return self.__d[pv]

    def getElements(self):
        return self.__elempv.keys()

    def getElementProperties(self, elem, prop=None):
        if not self.__elempv.has_key(elem):
            return None

        # consider only one PV, assuming records agrees on properties
        pv = self.__elempv[elem][0]

        # if it is None, return all properties of 
        if prop == None or len(prop) == 0:
            return self.__d[pv]

        #
        ret = {}
        for p in prop:
            if self.__d[pv].has_key(p): ret[p] = self.__d[pv][p]
            else: ret[p] = None
        return ret

    def checkUniversalProperty(self, prop = ['elem_type']):
        """
        for element with several PVs, its properties are duplicated in
        each record of channel finder server. This routine checkes whether
        each record agrees with each other.
        """
        pass

    def cleanup(self):
        self.__d = {}
        self.__elempv = {}
        self.__devpv = {}
        self.__cdata = ''

    def __parsePvCellGirder(self, pv):
        m = re.match(r".+:(C\d\d).+:(G\d\d)(.)", pv)
        if not m: return {}
        cell = m.group(1)
        girder = m.group(2)
        symm = m.group(3)
        if not symm in ['A', 'B', 'a', 'b']: symm = ''
        print pv, cell, girder, symm
        return {self.CELL: cell, self.GIRDER: girder, self.ELEMSYM: symm}

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
         self.__cdate = strftime("%Y-%m-%dT%H:%M:%S", gmtime())
         cnt = {'BPM':0, 'TRIMD':0, 'TRIMX':0, 'TRIMY':0, 'SEXT':0, 'QUAD':0}
 
         f = open(lattable, 'r').readlines()
         for s in f[1:]:
             if s[0] == '#': continue
             t = s.split()
             idx  = int(t[0])     # index
             rb   = t[1].strip()  # PV readback
             sp   = t[2].strip()  # PV setpoint
             phy  = t[3].strip()  # name
             L    = float(t[4])   # length
             s2   = float(t[5])   # s_end location
             grp  = t[6].strip()  # group
             dev  = t[7].strip()
             
             # append x/y for BPMX/BPMY to make eput/eget work on unique pv
             #if grp == 'BPMX': phy = phy + 'X'
             #elif grp == 'BPMY': phy = phy + 'Y'
             
             if not self.__elempv.has_key(phy): self.__elempv[phy] = []
             if not self.__devpv.has_key(dev): self.__devpv[dev] = []
             elemprop = {self.ELEMNAME: phy, self.ELEMTYPE: grp, self.DEVNAME: dev,
                         self.ELEMIDX: idx, self.SPOSITION: s2, self.LENGTH: L}
 
             if rb != 'NULL':
                 # read back
                 if not self.__d.has_key(rb):
                     self.__d[rb] = {self.TAGSKEY: []}
                 elemprop.update(self.__parsePvCellGirder(rb))
                 tags = [ 'default.eget' ]
                 if rb.find('}GOLDEN') >= 0 or rb.find('}BBA') >= 0:
                     tags.remove('default.eget')
                 # for BPM
                 if grp in ['BPMX', 'TRIMX']: tags.append('X')
                 elif grp in ['BPMY', 'TRIMY']: tags.append('Y')

                 self.updateChannel(rb, elemprop, tags)  
                 self.__elempv[phy].append(rb)
                 self.__devpv[dev].append(rb)
             if sp != 'NULL':
                 # set point
                 if not self.__d.has_key(sp):
                     self.__d[sp] = {self.TAGSKEY: []}
                 elemprop.update(self.__parsePvCellGirder(sp))
                 tags = [ 'default.eput' ]
                 if grp in ['BPMX', 'TRIMX']: tags.append('X')
                 elif grp in ['BPMY', 'TRIMY']: tags.append('Y')
                 self.updateChannel(sp, elemprop, tags)       
                 self.__elempv[phy].append(sp)
                 self.__devpv[dev].append(sp)
                 
         # need to update elempv and devpv
         # remove lost ones
         for elem,pvlst in self.__elempv.items():
             for pv in pvlst:
                 if self.__d[pv][self.ELEMNAME] != elem:
                     self.__elempv[pv].remove(elem)
         for dev,pvlst in self.__devpv.items():
             for pv in pvlst:
                 if self.__d[pv][self.DEVNAME] != dev:
                     self.__devpv[pv].remove(dev)
         # add new ones
         for pv, props in self.__d.items():
             if props.has_key(self.ELEMNAME):
                 elem = props[self.ELEMNAME]
                 if not pv in self.__elempv[elem]:
                     self.__elempv[elem].append(pv)
             if props.has_key(self.DEVNAME):
                 dev = props[self.DEVNAME]
                 if not pv in self.__devpv[dev]:
                     self.__devpv[dev].append(pv)
         # done!
                 
