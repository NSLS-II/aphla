#!/usr/bin/env python

"""
Channel Finder Agent
~~~~~~~~~~~~~~~~~~~~~

This module builds a local cache of channel finder service.
"""

import cadict
import shelve
from time import gmtime, strftime

class ChannelFinderAgent:
    def __init__(self):
        self.__d = {}
        self.__cdate = strftime("%Y-%m-%dT%H:%M:%S", gmtime())
        self.__elempv = {}

    def importXml(self, fname):
        ca = cadict.CADict(fname)
        for elem in ca.elements:
            #print elem
            self.__elempv[elem.name] = []
            if len(elem.ca) == 0: continue
            for i, pv in enumerate(elem.ca):
                # for each pv and handle
                self.addChannel(pv, {'handle':elem.handle[i], 
                                     'elementname':elem.name,
                                     'elementtype':elem.type,
                                     'cell': elem.cell,
                                     'girder': elem.girder,
                                     'symmetry': elem.symmetry}, None)
                self.__elempv[elem.name].append(pv)

            #print elem.sequence
        self.__cdate = strftime("%Y-%m-%dT%H:%M:%S", gmtime())

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


if __name__ == "__main__":
    d = ChannelFinderAgent()
    d.importXml('/home/lyyang/devel/nsls2-hla/machine/nsls2/main.xml')

    #print d
    d.save('test.shelve')
    d1 = ChannelFinderAgent()
    d1.load('test.shelve')
    c = d1.getChannel(prop = {'cell':'C01', 'girder':'G2'})
    for k,v in c.items():
        print k, v
    #print d1

