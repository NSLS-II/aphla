#!/usr/bin/env python

"""
This script initialized some PVs in channel finder. The PVs are only those
used by HLA.

To use this script, create a file 'conf.py' similar to the following::

  username = 'your username'
  password = 'your password'


:author: Lingyun Yang
:date: 2011-05-11 16:22
"""

import os, sys
import re, time

import channelfinder

from channelfinder import ChannelFinderClient
from channelfinder import Channel, Property, Tag

import conf

cfsurl = 'https://channelfinder.nsls2.bnl.gov:8181/ChannelFinder'
cfinput = {
    'BaseURL': cfsurl,
    'username': conf.username,
    'password': conf.password}

def simple_test():
    cf = ChannelFinderClient(**cfinput)
    cf.set(property=Property('test-prop1', 'cf-asd', 'v1'))
    cf.set(property=Property('test-prop2', 'cf-asd', 'v2'))
    cf.set(property=Property('test-prop3', 'lyyang'))
    cf.set(property=Property('test-prop4', 'lyyang'))
    cf.delete(propertyName='test-prop1')
    cf.delete(propertyName='test-prop3')

    pvname='SR:C00-BI:G00{DCCT:00}CUR-RB'
    cf.update(property=Property('test-prop2', 'cf-asd', 'v1'),
              channelName=pvname)
    cf.delete(propertyName='test-prop2', channelName=pvname)

def update_cfs_from_txt(txt, subline = 'LTB'):
    """
    skip the line if not found the 'subline'

    This is not for importing huge amount of channels. It updates channels
    one by one.

    The properties are updated as 'cf-asd' account, and tags in 'cf-aphla'
    """
    print "Updating CFS from text file:", txt
    
    cf = ChannelFinderClient(**cfinput)

    #for p in props: print p.Name, p.Owner, p.Value

    pvs = []
    
    for i,line in enumerate(open(txt, 'r').readlines()):
        if not line.strip(): continue
        if line.strip().find('#') == 0: continue
        # skip this line if I did not find 'subline'
        if line.find(subline) < 0: continue

        # skip non TRIM lines
        #if line.find('COR') < 0: continue
        
        # call every time, updated from server. Slow but reliable.
        allprops = [p.Name for p in cf.getAllProperties()]
        alltags  = [t.Name for t in cf.getAllTags()]


        pv, prptlst, taglst = [s.strip() for s in line.split(';')]
        prpt = {}
        for pair in prptlst.split(','):
            if not pair.strip(): continue
            if pair.find('=') < 0:
                print "skipping", pair
                continue
            k, v = pair.split('=')
            prpt[k.strip()] = v.strip()
        prpts = [Property(k, 'cf-asd', v) for k,v in prpt.iteritems()]
        tags = [Tag(t.strip(), 'cf-aphla') for t in taglst.split(',') \
                    if t.strip()]
        print i, pv, 
        print [p.Name for p in prpts], [p.Value for p in prpts], [t.Name for t in tags]

        # updating
        for t in tags:
            if not t.Name in alltags:
                print "Adding new tag:", t.Name
                cf.set(tag=t)
            try:
                cf.update(channelName=pv, tag = t)
            except:
                print "ERROR: ", pv, t.Name

        for p in prpts:
            if not p.Name in allprops:
                print "Adding new property:", p.Name
                cf.set(property=p)
            try:
                cf.update(channelName=pv, property=p)
            except:
                print "ERROR: ", pv, p.Name, p.Value

        print '/'.join([p.Name for p in prpts]), \
            '+'.join([t.Name for t in tags])


def renamePvTags():
    pass

def renameTags():
    cf = ChannelFinderClient(**cfinput)
    #cf.update(tag=Tag('aphla.sys.LTB', 'cf-aphla'),
    #          originalTagName='aphla.sys.ltb')
    #cf.update(tag=Tag('aphla.sys.LTD1', 'cf-aphla'),
    #          originalTagName='aphla.sys.ltd1')
    #cf.update(tag=Tag('aphla.sys.LTD2', 'cf-aphla'),
    #          originalTagName='aphla.sys.ltd2')

def updateTags():
    pvs = []
    for i,s in enumerate(open(sys.argv[1], 'r').readlines()):
        if s.find('aphla.sys.SR') < 0: continue
        pv = s.split(';')[0].strip()
        pvs.append(pv)
    cf = ChannelFinderClient(**cfinput)
    cf.update(tag=Tag('aphla.sys.SR', 'cf-aphla'), channelNames=pvs)

    
def addNewTags():
    tagname = 'aphla.sys.SR'
    cf = ChannelFinderClient(**cfinput)
    cf.set(tag=Tag(tagname, 'cf-aphla'))

def addPvTags(pv, tag):
    cf = ChannelFinderClient(**cfinput)
    cf.update(channelName=pv, tag=Tag(tag, 'cf-aphla'))


def removeTagsFromPv():
    cf = ChannelFinderClient(**cfinput)
    pv = 'LTB:MG{Quad:6}Fld-SP'
    cf.delete(tag=Tag('aphla.eget', 'cf-aphla'), channelName=pv)

    pv = 'LTB:MG{Bend:1}Fld-SP'
    cf.delete(tag=Tag('aphla.eget', 'cf-aphla'), channelName=pv)

def updatePvProperties(pv, p, v):
    cf = ChannelFinderClient(**cfinput)
    cf.update(channelName=pv, property=Property(p, 'cf-asd', v))

def removeProperties(p):
    cf = ChannelFinderClient(**cfinput)
    cf.delete(propertyName=p)

def removeTags():
    cf = ChannelFinderClient(**cfinput)
    #cf.delete(tagName='aphla.offset aphla.eput aphla.x')
    #cf.delete(tagName="aphla.offset aphla.eput aphla.y")
    cf.delete(tagName="aphla.eget aphla.x")
    cf.delete(tagName="aphla.eget aphla.y")
    cf.delete(tagName="aphla.eput aphla.x")
    cf.delete(tagName="aphla.eput aphla.y")
    cf.delete(tagName="testtag2")

if __name__ == "__main__":
    print channelfinder.__file__,
    print time.ctime(os.path.getmtime(channelfinder.__file__))

    #addPvTags('LTB:MG{HCor:2BD1}Fld-SP', 'aphla.sys.LTD1')
    #addPvTags('LTB:MG{VCor:2BD1}Fld-SP', 'aphla.sys.LTD1')
    #updatePvProperties('LTB-BI:BD1{VF1}Size:X-I', 'elemField', 'x')
    #updatePvProperties('LTB-BI:BD1{VF1}Size:Y-I', 'elemField', 'y')
    #updatePvProperties('LTB-BI:BD1{VF1}Img1:ArrayData', 'elemField', 'image')

    #removeTagsFromPv()
    #updateTags()
    #addNewTags()
    #renameTags()
    #removeTags()
    removeProperties('test-prop2')
    sys.exit(0)

    if len(sys.argv) > 1 and os.path.exists(sys.argv[1]):
        update_cfs_from_txt(sys.argv[1], subline='LTB')
        pass
    elif len(sys.argv) > 1 and sys.argv[1] == '--test':
        simple_test()
    else:
        print "Usage: %s txtfile" % (sys.argv[0],)
        
