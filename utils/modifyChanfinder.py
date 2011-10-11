#!/usr/bin/env python

import os, sys, shelve, re
import hla

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

def changeChannel(safe = True):
    """rename channel from src to dst"""
    pkl = '/home/lyyang/devel/nsls2-hla/machine/nsls2/chanfinder.pkl'
    f = shelve.open(pkl, 'w', writeback=True)
    print f.keys()
    d = f['cfa.data']
    dst = [pv.strip() for pv in open('/home/lyyang/devel/nsls2-hla/machine/nsls2/pvlist_2011_04_08.txt')]
    src = [pv.strip() for pv in open('/home/lyyang/devel/nsls2-hla/machine/nsls2/pvlist.txt').readlines()]
    for k,v in d.items():
        if not k in src and not k in dst: 
            print "ERROR:", k
            continue
        elif k in dst:
            continue
        i = src.index(k)
        dis = hla.levenshtein_distance(src[i], dst[i])
        if dis > 4:
            print src[i], dst[i], dis
        if not safe:
            f['cfa.data'][dst[i]] = v
            del f['cfa.data'][src[i]]
    f.close()

def changeElementName(safe = True):
    """change element name in channel finder"""
    pkl = '/home/lyyang/devel/nsls2-hla/machine/nsls2/chanfinder.pkl'
    f = shelve.open(pkl, 'w', writeback=True)
    print f.keys()
    d = f['cfa.data']

    tbl = '/home/lyyang/devel/nsls2-hla/machine/nsls2/lat_conf_table.txt'
    for s in open(tbl).readlines()[1:]:
        idx = int(s.split()[0])
        pv1 = s.split()[1]
        pv2 = s.split()[2]
        phy = s.split()[3]
        L   = float(s.split()[4])
        spos = float(s.split()[5])
        grp  = s.split()[6]
        if pv1 != 'NULL' and f['cfa.data'].has_key(pv1): 
            if f['cfa.data'][pv1]['elem_name'] != phy:
                print pv1, phy, f['cfa.data'][pv1]['elem_name']
    f.close()

if __name__ == "__main__":
    #printChannels()
    #addDefaultTags()
    #changeChannel(False)
    changeElementName()
