#!/usr/bin/env python

"""
Channel Finder Agent
~~~~~~~~~~~~~~~~~~~~~

This module builds a local cache of channel finder service.
"""

import cadict
import re, shelve
from time import gmtime, strftime
import sys

class ChannelFinderAgent:
    def __init__(self):
        self.__d = {}
        self.__cdate = strftime("%Y-%m-%dT%H:%M:%S", gmtime())
        self.__elempv = {}

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
            d.append([int(t[0]), t[1].strip(), t[2].strip(), t[3].strip()])
            d[-1].extend([float(t[i]) for i in range(4, 6)])
            d[-1].append(t[6].strip())
            #print d[-1]
            k = 6
            if cnt.has_key(d[-1][k]): cnt[d[-1][k]] += 1
            # parse cell/girder/symmetry from name
            cell, girder, symmetry = self.__parseElementName(d[-1][3])
            # add the readback pv
            self.addChannel(d[-1][1], {'handle': 'get', 
                                     'elementname': d[-1][3],
                                     'elementtype': d[-1][6],
                                     'cell': cell,
                                     'girder': girder,
                                     'symmetry': symmetry}, None)
        print "Summary:"
        for k,v in cnt.items():
            print " %8s %4d" % (k, v)
        return d

    def save(self, fname):
        f = shelve.open(fname, 'c')
        f['cfa.d'] = self.__d
        f['cfa.cdate'] = self.__cdate
        f['cfa.elempv'] = self.__elempv
        f.close()

    def load(self, fname):
        f = shelve.open(fname, 'r')
        self.__d = f['cfa.d']
        self.__cdate = f['cfa.cdate']
        self.__elempv = f['cfa.elempv']
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
    
    def getChannel(self, handle = '', prop = {}, tags = []):
        ret = {}
        for elem in self.__elempv.keys():
            pvs = self.getElementChannel(elem, handle, prop, tags)
            if pvs: ret[elem] = pvs
        return ret

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
        

if __name__ == "__main__":
    d = ChannelFinderAgent()
    #d.importXml('/home/lyyang/devel/nsls2-hla/machine/nsls2/main.xml')
    d.importLatticeTable('/home/lyyang/devel/nsls2-hla/machine/nsls2/lat_conf_table.txt')
    d.testChannels()
    #print d
    sys.exit(0)

    #print d
    d.save('test.shelve')
    d1 = ChannelFinderAgent()
    d1.load('test.shelve')
    c = d1.getChannel(prop = {'cell':'C01', 'girder':'G2'})
    for k,v in c.items():
        print k, v
    #print d1

