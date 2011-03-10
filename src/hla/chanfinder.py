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
    def __init__(self):
        self.__d = {}
        self.__cdate = strftime("%Y-%m-%dT%H:%M:%S", gmtime())
        self.__elempv = {}
        self.__elemidx = {}
        self.__elemname = []
        self.__elemtype = []
        self.__elemlen = []
        self.__elemloc = []

    def importXml(self, fname):

        raise NotImplementedError()

        #OBSOLETE - the main.xml file does not have latest pv list
        #"""
        ca = cadict.CADict(fname)
        for elem in ca.elements:
            #print elem
            self.__elempv[elem.name] = []
            if len(elem.ca) == 0: continue
            for i, pv in enumerate(elem.ca):
                # for each pv and handle
                #print "'%s'" % pv, 
                if len(pv.strip()) == 0: continue
                self.addChannel(pv, {'handle':elem.handle[i], 
                                     'elementname':elem.name,
                                     'elementtype':elem.type,
                                     'cell': elem.cell,
                                     'girder': elem.girder,
                                     'symmetry': elem.symmetry}, None)
                self.__elempv[elem.name].append(pv)

            #print elem.sequence
        self.__cdate = strftime("%Y-%m-%dT%H:%M:%S", gmtime())

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

        cnt = {'BPM':0, 'TRIMD':0, 'TRIMX':0, 'TRIMY':0, 'SEXT':0, 'QUAD':0}

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

            self.__elemname.append(phy)
            self.__elemtype.append(grp)
            self.__elemlen.append(L)
            self.__elemloc.append(s2)

            if not self.__elempv.has_key(phy):
                self.__elempv[phy] = []
            if rb != 'NULL': self.__elempv[phy].append(rb)
            if sp != 'NULL': self.__elempv[phy].append(sp)

            # parse cell/girder/symmetry from name
            cell, girder, symmetry = parseElementName(phy)

            # count element numbers in each type
            if cnt.has_key(grp): cnt[grp] += 1

            # add the readback pv
            if rb != 'NULL':
                self.addChannel(rb,
                                {'handle': 'get', 'elementname': phy,
                                 'elementtype': grp, 'cell': cell, 
                                 'girder': girder, 'symmetry': symmetry,
                                 'elemindex': idx, 's_end': s2}, ['default'])
            if sp != 'NULL':
                self.addChannel(sp,
                                {'handle': 'set', 'elementname': phy,
                                 'elementtype': grp, 'cell': cell,
                                 'girder': girder, 'symmetry': symmetry,
                                 'elemindex': idx, 's_end': s2}, ['default'])
            self.__elemidx[phy] = idx

        if False:
            print "Summary:"
            for k,v in cnt.items():
                print " %8s %5d" % (k, v)
            print "--"
            print " %8s %5d" % ("Elements", len(self.__elemidx.keys()))
            print " %8s %5d" % ("PVs",len(self.__d.keys()))
        #return d

    def import_virtac_pvs(self):
        self.addChannel('SR:C00-Glb:G00<ALPHA:00>RB-X', \
                            {'handle': 'get', 'elementname': 'Glb:ALPHA-X'}, \
                            ['default'])
        self.addChannel('SR:C00-Glb:G00<ALPHA:00>RB-Y', \
                            {'handle': 'get', 'elementname': 'Glb:ALPHA-Y'}, \
                            ['default'])
        self.addChannel('SR:C00-Glb:G00<BETA:00>RB-X', \
                            {'handle': 'get', 'elementname': 'Glb:BETA-X'}, \
                            ['default'])
        self.addChannel('SR:C00-Glb:G00<BETA:00>RB-Y', \
                            {'handle': 'get', 'elementname': 'Glb:BETA-Y'}, \
                            ['default'])
        self.addChannel('SR:C00-Glb:G00<ETA:00>RB-X', \
                             {'handle': 'get', 'elementname': 'Glb:ETA-X'}, \
                            ['default'])
        self.addChannel('SR:C00-Glb:G00<ETA:00>RB-Y', \
                             {'handle': 'get', 'elementname': 'Glb:ETA-Y'}, \
                            ['default'])
        self.addChannel('SR:C00-Glb:G00<ORBIT:00>RB-X', \
                             {'handle': 'get', 'elementname': 'Glb:ORBIT-X'}, \
                            ['default'])
        self.addChannel('SR:C00-Glb:G00<ORBIT:00>RB-Y', \
                             {'handle': 'get', 'elementname': 'Glb:ORBIT-Y'}, \
                            ['default'])
        self.addChannel('SR:C00-Glb:G00<PHI:00>RB-X', \
                             {'handle': 'get', 'elementname': 'Glb:PHI-X'}, \
                            ['default'])
        self.addChannel('SR:C00-Glb:G00<PHI:00>RB-Y', \
                             {'handle': 'get', 'elementname': 'Glb:PHI-Y'}, \
                            ['default'])
        self.addChannel('SR:C00-Glb:G00<POS:00>RB-S', \
                            {'handle': 'get', 'elementname': 'Glb:POS'}, \
                            ['default'])
    def fix_bpm_xy(self):
        for k,v in self.__d.items():
            if k[-7:] == 'Freq-RB': pass
            elif k[-7:] == 'Volt-RB': pass
            elif k[-7:] == 'Freq-SP': pass
            elif k[-7:] == 'Volt-SP': pass
            elif k[-6:] == 'Fld-SP': pass
            elif k[-6:] == 'Fld-RB': pass
            elif k[-6:] == 'CUR-RB': pass
            elif k[-2:] == '-X': self.__d[k]['~tags'].append('H')
            elif k[-2:] == '-Y': self.__d[k]['~tags'].append('V')
            elif k[-2:] == '-S': self.__d[k]['~tags'].append('S')
            else:
                raise ValueError("not recognized: %s" % k)

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
        f['cfa.d']       = self.__d
        f['cfa.cdate']   = self.__cdate
        f['cfa.elempv']  = self.__elempv
        f['cfa.elemidx'] = self.__elemidx
        f['cfa.elemname'] = self.__elemname
        f['cfa.elemtype'] = self.__elemtype
        f['cfa.elemlen']  = self.__elemlen
        f['cfa.elemloc']  = self.__elemloc
        f.close()

    def load(self, fname):
        f = shelve.open(fname, 'r')
        self.__d       = f['cfa.d']
        self.__cdate   = f['cfa.cdate']
        self.__elempv  = f['cfa.elempv']
        self.__elemidx = f['cfa.elemidx']
        self.__elemname = f['cfa.elemname']
        self.__elemtype = f['cfa.elemtype']
        self.__elemlen  = f['cfa.elemlen']
        self.__elemloc  = f['cfa.elemloc']
        f.close()

    def __matchProperties(self, pv, prop = {}):
        if not prop: return True
        for  k, v in prop.items():
            if not self.__d[pv].has_key(k) or \
                    self.__d[pv][k] != v:
                return False

        return True

    def __matchTags(self, pv, tags = []):
        if not tags: return True
        for tag in tags:
            if not tag in self.__d[pv]['~tags']: return False
        return True
            
    def addChannel(self, pv, props, tags):
        if not self.__d.has_key(pv):
            self.__d[pv] = {'~tags':[]}
        #
        if props:
            for prop, val in props.items(): self.__d[pv][prop] = val

        if tags:
            for tag in tags: 
                if tag in self.__d[pv]['~tags']: continue
                self.__d[pv]['~tags'].append(tag)

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

    def getElementChannel(self, elemlist, prop = {}, tags = [], unique=True):
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
        for elem in self.__elempv.keys():
            #print elem,
            pvs = self.getElementChannel(elem, prop, tags)
            if pvs: ret.extend(pvs)
        return ret

    def __getElementChannels(self, elem, prop = {}, tags = []):
        """*elem* is the exact name of an element.

        Returns a list of matched PVs."""
        if not self.__elempv.has_key(elem): return []
        ret = []
        for pv in self.__elempv[elem]:
            if self.__matchProperties(pv, prop) and \
                    self.__matchTags(pv, tags):
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
        return self.__elemname.index(a) - self.__elemname.index(b)

    def sortElements(self, elemlst):
        ret = sorted(elemlst, self.__cmp_elem_loc )
        for elem in ret:
            print elem, self.__elemloc[self.__elemname.index(elem)]



