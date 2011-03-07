#!/usr/bin/env python

"""
Channel Finder Agent
~~~~~~~~~~~~~~~~~~~~~

This module builds a local cache of channel finder service.
"""

import cadict
import re, shelve
from fnmatch import fnmatch
from time import gmtime, strftime
import sys

class ChannelFinderAgent:
    def __init__(self):
        self.__d = {}
        self.__cdate = strftime("%Y-%m-%dT%H:%M:%S", gmtime())
        self.__elempv = {}
        self.__elemidx = {}

    def importXml(self, fname):
        """OBSOLETE - the main.xml file does not have latest pv list
        """
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

    def __parseElementName(self, name):
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

    def importLatticeTable(self, lattable):
        """Import the table used for Tracy-VirtualIOC

        #index, read back, set point, phys name, len[m], s[m], group name(type)

        Data are deliminated by spaces
        """

        print "Importing file:", lattable

        cnt = {'BPM':0, 'TRIMD':0, 'TRIMX':0, 'TRIMY':0, 'SEXT':0, 'QUAD':0}

        f = open(lattable, 'r').readlines()
        d = []
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
            cell, girder, symmetry = self.__parseElementName(phy)

            # count element numbers in each type
            if cnt.has_key(grp): cnt[grp] += 1

            # add the readback pv
            if rb != 'NULL':
                self.addChannel(rb,
                                {'handle': 'get', 'elementname': phy,
                                 'elementtype': grp, 'cell': cell, 
                                 'girder': girder, 'symmetry': symmetry,
                                 'elemindex': idx, 's_end': s2}, None)
            if sp != 'NULL':
                self.addChannel(sp,
                                {'handle': 'get', 'elementname': phy,
                                 'elementtype': grp, 'cell': cell,
                                 'girder': girder, 'symmetry': symmetry,
                                 'elemindex': idx, 's_end': s2}, None)
            self.__elemidx[phy] = idx
        print "Summary:"
        for k,v in cnt.items():
            print " %8s %5d" % (k, v)
        print "--"
        print " %8s %5d" % ("Elements", len(self.__elemidx.keys()))
        print " %8s %5d" % ("PVs",len(self.__d.keys()))
        #return d

    def save(self, fname, mode = 'c'):
        f = shelve.open(fname, mode)
        f['cfa.d']       = self.__d
        f['cfa.cdate']   = self.__cdate
        f['cfa.elempv']  = self.__elempv
        f['cfa.elemidx'] = self.__elemidx
        f.close()

    def load(self, fname):
        f = shelve.open(fname, 'r')
        self.__d       = f['cfa.d']
        self.__cdate   = f['cfa.cdate']
        self.__elempv  = f['cfa.elempv']
        self.__elemidx = f['cfa.elemidx']
        f.close()

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

    def getElementChannel(self, element, handle='', prop = {}, tags = []):
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
        #if len(ret) == 0: print msg
        return ret
    
    def getChannels(self, handle = '', prop = {}, tags = []):
        ret = {}
        for elem in self.__elempv.keys():
            pvs = self.getElementChannel(elem, handle, prop, tags)
            if pvs: ret[elem] = pvs
        return ret

    def getElements(self, group, cell = [], girder = [],
                    sequence = []):
        """
        """
        elem = []
        for pv in self.__d.keys():
            elemname = self.__d[pv]['elementname']
            elemtype = self.__d[pv]['elementtype']
            if group and not fnmatch(elemname, group) \
                    and not fnmatch(elemtype, group):
                continue
            if cell and not self.__d[pv]['cell'] in cell: continue
            if girder and not self.__d[pv]['girder'] in girder: continue
            elem.append(elemname)

        # may have duplicate element
        return [v for v in set(elem)]

    def testChannels(self):
        import cothread
        from cothread.catools import caget

        rec = {}
        n = 0
        print "Testing %d channels" % len(self.__d.keys())
        for v in sorted(self.__d.keys()):
            #print "'%s'" % v, 
            n += 1
            try:
                x = caget(v, timeout=2)
                sys.stdout.write('-')
            except:
                #print "TIME OUT"
                rec[v] = 1
                sys.stdout.write('\nx %6d  %s' % (n,v))
                
            sys.stdout.flush()
        print ""
        for k,v in rec.items():
            print k, v
    
    def checkMissingChannels(self, pvlist):
        for i, line in enumerate(open(pvlist, 'r').readlines()):
            if self.__d.has_key(line.strip() ): continue
            print "Line: %d %s" % (i, line.strip())
        print "-- DONE --"

if __name__ == "__main__":
    import os, sys
    d = ChannelFinderAgent()
    #d.importXml('/home/lyyang/devel/nsls2-hla/machine/nsls2/main.xml')
    hlaroot = '/home/lyyang/devel/nsls2-hla/'
    d.importLatticeTable(hlaroot + 'machine/nsls2/lat_conf_table.txt')
    #d.testChannels()
    print d.getElements('P*G2C2*', cell=['C21'])
    d.checkMissingChannels(hlaroot + 'machine/nsls2/pvlist_2011_03_03.txt')
    d.save(hlaroot + 'machine/nsls2/hla.pkl')
    
    # testing ...
    #d1 = ChannelFinderAgent()
    #d1.load('')
    #c = d1.getChannel(prop = {'cell':'C01', 'girder':'G2'})
    #for k,v in c.items():
    #    print k, v
    #print d1

