#!/usr/bin/env python

import sys

from channelfinder import ChannelFinderClient, Channel, Property, Tag
import aphla as ap

#GET http://channelfinder.nsls2.bnl.gov:8080/ChannelFinder/resources/resources/channels?~name=SR*

cfsurl = 'http://web01.nsls2.bnl.gov:8080/ChannelFinder'
#cfinput = {
#    'BaseURL': cfsurl,
#    'username': conf.username,
#   'password': conf.password}

def download_cfs(cfsurl, **cfinput):
    cf = ChannelFinderClient(BaseURL = cfsurl)
    chs = cf.find(**cfinput)
    ret = chanData.ChannelFinderData()
    for ch in chs:
        pv = ch.Name
        prpt = dict([(p.Name, p.Value) for p in ch.Properties])
        tags = [t.Name for t in ch.Tags]

        ret.update(pv = pv, properties = prpt, tags = tags)
    return ret
    

def print_kv(k, v):
    s = ''
    if len(v[0]) == 0 and len(v[1]) == 0: return
    elif len(v[1]) == 0:
        for p,vv in v[0].iteritems():
            if vv is None: continue
            s = s + "{0}={1}, ".format(p, vv)
        if s:
            print k, s[:-2]
    elif len(v[0]) == 0:
        print k, 
        for p in v[1]:
            print "%s," % p,
        print ""
    else:
        print k,
        for p,vv in v[0].iteritems():
            print "%s=%s" % (str(p), str(vv)),
        for p in v[1]:
            print "%s," % p
        print ""

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print sys.argv[0], "us_nsls2_cfs.csv"
        sys.exit(0)

    cfa1 = ap.ChannelFinderAgent()
    cfa1.importCsv(sys.argv[1])

    cfa2 = ap.ChannelFinderAgent()
    cfa2.downloadCfs(cfsurl, tagName='aphla.*')

    print "<<<< local - CFS"
    for k, v in (cfa1 - cfa2).iteritems():
        print_kv(k, v)
    print "--------------"
    for k, v in (cfa2 - cfa1).iteritems():
        print_kv(k, v)
    print ">>>> CFS - local"

