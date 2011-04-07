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

from cothread.catools import caget, caput

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
        self.__d = None
        self.__cdate = strftime("%Y-%m-%dT%H:%M:%S", gmtime())
        self.__elempv = None
        self.__devpv = None

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
        s = s + " " + ', '.join(rec['~tags']) + '\n'
        return s

    def __repr__(self):
        s = ""
        for k,v in self.__d.items():
            s = s + "%s\n" % k
            for prop in v.keys():
                if prop == '~tags': continue
                s = s + " %s: %s\n" % (prop, v[prop])
            s = s + " "
            s = s + ', '.join(v['~tags'])
            s = s + '\n'
        return s

    def channel(self, pv):
        return self._repr_channel(pv)

    def getElementChannel(self, elemlist, prop=None, tags=None, unique=True):
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
            if self.__matchProperties(k, prop) and self.__matchTags(k, tags):
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

    def clear_trim_settings(self):
        i = 0
        for k, v in self.__d.items():
            if v['handle'] == 'get': continue
            if fnmatch(v['elementname'], 'C*'):
                caput(k, 0.0)
                i += 1
        print "reset %d trims", i

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

    def getChannels(self):
        return self.__d.keys()

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


