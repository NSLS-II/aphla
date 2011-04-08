#!/usr/bin/env python

import os, sys, shelve, re

def printChannels():
    pkl = '/home/lyyang/devel/nsls2-hla/machine/nsls2/chanfinder.pkl'
    f = shelve.open(pkl, 'w', writeback=True)
    print f.keys()
    d = f['cfa.data']
    for k,v in d.items():
        print k
        for p,vp in v.items():
            print "  ", p, ": ", vp
        print ""
    f.close()

def addDefaultTags():
    pkl = '/home/lyyang/devel/nsls2-hla/machine/nsls2/chanfinder.pkl'
    f = shelve.open(pkl, 'w', writeback=True)
    print f.keys()
    d = f['cfa.data']
    for k,v in d.items():
        if len(v['~tags']) > 0: continue
        #if not k[-5:] == u'Fld-I' and not  k[-6:] == u'Fld-SP': continue
        #if k[-5:] == u'Fld-I':
        #    f['cfa.data'][k]['~tags'].append('default.eget')
        #if k[-6:] == u'Fld-SP':
        #    f['cfa.data'][k]['~tags'].append('default.eput')
        #if k[-8:-1] == u'GOLDEN:': 
        #    f['cfa.data'][k]['~tags'].append('default.eput')
        #if re.match('SA:.-I',k[-6:]):
        #    f['cfa.data'][k]['~tags'].append('default.eget')
            
        print k
        if re.match('.+BBA:.', k):
            continue
        for p,vp in v.items():
            print "  ", p, ": ", vp
        print ""
    f.close()

if __name__ == "__main__":
    printChannels()
    #addDefaultTags()
