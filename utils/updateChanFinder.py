#!/usr/bin/env python

"""
This script initialized some PVs in channel finder. The PVs are only those
used by HLA.

:author: Lingyun Yang
:date: 2011-05-11 16:22
"""

import os, sys
import re, time

from channelfinder.core.ChannelFinderClient import ChannelFinderClient
from channelfinder.core.Channel import Channel, Property, Tag

import conf

cfsurl = 'http://channelfinder.nsls2.bnl.gov:8080/ChannelFinder'
cfinput = {
    'BaseURL': cfsurl,
    'username': conf.username,
    'password': conf.password}

def add_tag(pv):
    cf = ChannelFinderClient(**cfinput)
    t1=Tag('testtag2', 'lyyang')
    cf.set(tag=t1)
    chs = cf.find(name=pv)
    cf.update(tag=t1, channelName=chs[0].Name)
    cf.delete(tag=t1, channelName=chs[0].Name)


def add_test_prop(pv):
    cf = ChannelFinderClient(**cfinput)

    cf.set(property=Property('testProp1', 'cf-asd'))
    for p in cf.getAllProperties():
        print p.Name, p.Owner

    cf.update(channelName = pv, property=Property('testProp1', 'cf-asd'))
    for ch in cf.find(name=pv):
        print ch.Name
        ch.getProperties()
        print "  ", k, v


def test_update(pv):
    cf = ChannelFinderClient(**cfinput)
    #cf.set(property=Property('elemField', 'cf-asd', 'x'))
    #cf.update(property=Property('elemField', 'cf-asd', 'x'))
    #cf.set(property=Property('elemField', 'cf-asd', 'y'))
    # clean up
    cf.update(channelName=pv, property=Property('elemField', 'cf-asd', 'x'))
    for ch in cf.find(name=pv):
        print ch.Name
        for k,v in ch.Properties:
            print "  ", k, v




def update_cfs_from_txt(txt):
    cf = ChannelFinderClient(**cfinput)
    #cf.set(property=Property('elemField', 'cf-asd', 'x'))
    #cf.update(property=Property('elemField', 'cf-asd', 'x'))
    #cf.set(property=Property('elemField', 'cf-asd', 'y'))
    # clean up
    props = cf.getAllProperties()
    for p in props: print p.Name, p.Owner, p.Value

    pvs = []

    for line in open(txt, 'r').readlines():
        if line.find('LTB') < 0: continue
        pv, prptlst, tags = [s.strip() for s in line.split(';')]
        g = re.match(r'.+(elemName)\s*=\s*([a-zA-Z0-9_]+)\s*,', prptlst)
        prpt, val = g.group(1), g.group(2)
        print "'%s'" % (pv,), prpt, val
        pvs.append(pv)
        cf.update(property=Property(prpt, 'cf-asd', val), channelName=pv)

    # for line in open(txt, 'r').readlines():
    #     if line.find('BPM') < 0: continue
    #     pv, prptlst, tags = [s.strip() for s in line.split(';')]
    #     g = re.match(r'.+(elemType)\s*=\s*([a-zA-Z0-9_]+)\s*,', prptlst)
    #     prpt, val = g.group(1), g.group(2)
    #     print "'%s'" % (pv,), prpt, val
    #     pvs.append(pv)
    #     #cf.update(property=Property(prpt, 'cf-asd', val), channelName=pv)
    # cf.update(property=Property('elemType', 'cf-asd', 'BPM'), channelNames=pvs)


    #for line in open(txt, 'r').readlines():
    #    if line.find('elemField') < 0: continue
    #    pv, prptlst, tags = [s.strip() for s in line.split(';')]
    #    g = re.match(r'.+(elemField)\s*=\s*([a-zA-Z0-9_]+)\s*,', prptlst)
    #    prpt, val = g.group(1), g.group(2)
    #    print "'%s'" % (pv,), prpt, val
    #    cf.update(property=Property(prpt, 'cf-asd', val), channelName=pv)
    #    #break

if __name__ == "__main__":
    #out = 'cfa.txt'
    #dump_hla_cfa(out)
    if len(sys.argv) > 1 and os.path.exists(sys.argv[1]):
        #initialize_cfs(sys.argv[1])
        update_cfs_from_txt(sys.argv[1])
        #test_update('SR:C01-MG:G02A{HCor:L1}Fld-I')
        pass
    #add_test_prop('SR:C01-MG:G02A{HCor:L1}Fld-I')
    #add_tag('SR:C01-MG:G02A{HCor:L1}Fld-I')
    #test()
    
