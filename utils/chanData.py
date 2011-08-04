#!/usr/bin/env python

import sys

class ChannelFinderData:
    """
    """
    def __init__(self):
        self._data = {}
        self._properties = {}
        self._tags = []

    def update(self, **kwargs):
        pv = kwargs.get('pv', None)
        prpt = kwargs.get('properties', {})
        tag = kwargs.get('tags', [])

        if not pv: return
        elif not self._data.has_key(pv):
            self._data[pv] = {'properties':{}, 'tags':[]}
        if prpt:
            self._data[pv]['properties'].update(prpt)

        for k,v in prpt.iteritems():
            if self._properties.has_key(k):
                if not v in self._properties[k]: self._properties[k].append(v)
            else: self._properties[k] = [v]
            
        for t in tag:
            if t in self._data[pv]['tags']: continue
            self._data[pv]['tags'].append(t)
            if not t in self._tags: self._tags.append(t)

    def __sub__(self, x):
        #print "Substract ..."
        ret = ChannelFinderData()
        for k in sorted(self._data.keys()):
            if not k in x._data.keys():
                # k is not in x, return it
                ret.update(pv = k, properties = self._data[k]['properties'],
                           tags = self._data[k]['tags'])
            else:
                # check properties
                dst = x._data[k]
                src = self._data[k]
                prpt = {}
                tags = []
                for p, v in src['properties'].items():
                    if not p in dst['properties'].keys() or \
                           dst['properties'][p] != v:
                        prpt[p] = v
                for t in src['tags']:
                    if not t in dst['tags']:
                        tags.append(t)
                if prpt or tags:
                    ret.update(pv = k, properties = prpt, tags = tags)
        return ret

    def read_txt(self, f):
        for i,line in enumerate(open(f, 'r').readlines()):
            s = line.strip()
            if not s or s[0] == '#' or s.find('{') < 0:
                #rec.append(s)
                continue

            rawpv, rawprpt, rawtag = line.split(';')
            #print rawpv
            pv = rawpv.strip()

            prpts = {}
            for p in rawprpt.split(','):
                if not p.strip() or p.find('=') < 0:
                    continue
                k,v = p.split('=')
                prpts[k.strip()] = v.strip()

            tags = []
            for t in rawtag.split(','):
                if not t.strip():
                    continue
                tags.append(t.strip())

            self.update(pv = pv, properties=prpts, tags = tags)

    def __str__(self):
        s = ''
        for k in sorted(self._data.keys()):
            s = s + k + '; '
            for p in sorted(self._data[k]['properties'].keys()):
                s = s + p + '=%s, ' % self._data[k]['properties'][p]
            if s[-2:] == ', ': s = s[:-2] + '; '
            for t in sorted(self._data[k]['tags']):
                s = s + t + ', '
            if s[-2:] == ', ': s = s[:-2]
            s = s + '\n'
        s = s + '\n'
        return s

    def removeProperties(self, prpts):
        for k,v in self._data.iteritems():
            if not v.has_key('properties'): continue
            for p in prpts:
                if v['properties'].has_key(p):
                    v['properties'].pop(p)
            

if __name__ == "__main__":
    d1 = ChannelFinderData()
    d1.read_txt(sys.argv[1])
    print d1._properties

    d2 = ChannelFinderData()
    d2.read_txt(sys.argv[1])

    d2.update(pv='x', properties={'x':'1'}, tags=['1', '2'])
    print d2._properties
    
    print "d1-d2", d1 - d2
    print "d2-d1", d2 - d1
    
