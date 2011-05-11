#!/usr/bin/env python

"""
This script initialized some PVs in channel finder. The PVs are only those
used by HLA.

:author: Lingyun Yang
:date: 2011-05-11 16:22
"""

import os, sys
import re, time

from channelfinder.ChannelFinderClient import ChannelFinderClient
from channelfinder.Channel import Channel, Property, Tag

import hla

def dump_hla_cfa(out):
    hla._cfa.exportTextRecord(out)

def clean_small_cases_ones():
    pass

def initialize_cfs(out):
    all_keys, all_tags = [], []
    cfsurl = 'http://channelfinder.nsls2.bnl.gov:8080/ChannelFinder'
    cf = ChannelFinderClient(BaseURL = cfsurl, username='boss', password='1234')

    # clean up
    props = cf.getAllProperties()
    #cf.set(properties = [Property('ORDINAL', '85')])
    cfchannels = []
    for line in open(out, 'r').readlines():
        if line.strip()[0] == '#': continue
        rec = line.split(';')
        pv, pstr, tagstr = rec
        chs = cf.find(name=pv.strip())
        if not chs:
            print "Did not find", pv
            continue
        if len(chs) > 1:
            print "PV is not unique:", pv
            continue
        
        prop, tags = {}, []
        for r in pstr.split(','):
            if not r: continue
            k,v = r.upper().split('=')
            k = k.strip()
            v = v.strip()
            prop[k] = v
            if not k in all_keys: all_keys.append(k)

        for r in tagstr.split()[1:]:
            if r == 'default.eput': r = 'HLA.EPUT'
            elif r == 'default.eget': r = 'HLA.EGET'
            elif not r.startswith('HLA.'): r = 'HLA.' + r

            if not r in all_tags: all_tags.append(r)
            
            tags.append(r)
        #print pv, prop, tags
        cfprop = [Property(k, 'vioc', v) for k,v in prop.items()]
        cftags = [Tag(t, 'vioc') for t in tags]
        cfchannels.append(Channel(u'%s' % pv, 'vioc', properties=cfprop, tags=cftags))
        #cf.update(channel = Channel(pv, 'vioc'), properties=cfprop,
        #          tags = cftags)
        
    print ""
    print all_keys
    print all_tags
    cfprop = [Property(p, 'vioc', 'N.A.') for p in all_keys]
    cf.set(properties = cfprop)
    cftags = [Tag(t, 'vioc') for t in all_tags]
    cf.set(tags = cftags)    
    cf.set(channels=cfchannels)
    
def test():
    cfsurl = 'http://channelfinder.nsls2.bnl.gov:8080/ChannelFinder'
    cf = ChannelFinderClient(BaseURL = cfsurl, username='boss', password='1234')
    ch = cf.find(name='SR*')
    for c in ch:
        print c.name,
        
if __name__ == "__main__":
    out = 'cfa.txt'
    dump_hla_cfa(out)
    initialize_cfs(out)
    #test()
    
