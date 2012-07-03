#!/usr/bin/env python

"""
This script initialized some PVs in channel finder. The PVs are only those
used by HLA.

To use this script, create a file 'conf.py' similar to the following::

  username = 'your username'
  password = 'your password'


The input command file::

  addproperty prpt=val pv1,pv2,pv3
  add 

:author: Lingyun Yang
:date: 2011-05-11 16:22
"""

import os, sys
import re, time
import argparse

import logging
logging.basicConfig(filename='log_channelfinder_update.txt',
    format='%(asctime)s - %(name)s [%(levelname)s]: %(message)s',
    level=logging.DEBUG)

import channelfinder

from channelfinder import ChannelFinderClient
from channelfinder import Channel, Property, Tag

import conf

cfsurl = 'https://channelfinder.nsls2.bnl.gov:8181/ChannelFinder'
cfinput = {
    'BaseURL': cfsurl,
    'username': conf.username,
    'password': conf.password
    }

OWNER = 'cf-aphla'
PRPTOWNER = 'cf-asd'

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

def hasTag(cf, tag):
    """check if tag exists"""
    for t in cf.getAllTags():
        if t.Name == tag: return True

    return False

def hasProperty(cf, prpt):
    """check if property name exists"""
    for p in cf.getAllProperties(): 
        if p.Name == prpt: return True

    return False

def pvHasTag(cf, pv, tag):
    """
    """
    r = cf.find(name=pv, tagName=tag)
    if r is None or len(r) == 0:
        return False
    return True


def addPvTag(cf, pv, tag, owner):
    """add a tag to pv"""
    if not hasTag(cf, tag):
        cf.set(tag=Tag(tag, owner))
        logging.info("created a new tag (%s,%s)" % (tag, owner))
    cf.update(channelName=pv, tag=Tag(tag, owner))
    logging.info("'%s' add tag '%s'" % (pv, tag))

def removePvTag(cf, pv, tag, owner):
    """remove the tag from pv"""
    if not pvHasTag(cf, pv, tag):
        logging.warn("'%s' has no tag '%s'" % (pv, tag))
        return False

    cf.delete(tag=Tag(tag, owner), channelName=pv)
    logging.info("'%s' deleted tag (%s,%s) deleted" %  (pv, tag, owner))

def renamePvTag(cf, pv, src, dst):
    if src == dst: return False
    cftag = cf.find(tagName=src, name=pv)
    if cftag is None:
        logging.warn("'%s' has no tag '%s'" % 
                     (pv, src))
        return False
    addPvTag(cf, pv, dst)
    removePvTag(cf, pv, src)

def addTagPvs(cf, tag, pvs, owner):
    if not hasTag(cf, tag):
        cf.set(tag=Tag(tag, owner))
        logging.info("created a new tag (%s,%s)" % (tag, owner))
    cf.update(tag=Tag(tag, owner), channelNames=pvs)
    logging.info("--batch add tag '%s' to %d pvs" % (tag, len(pvs)))
    for i, pv in enumerate(pvs):
        logging.info("add tag '%s' to '%s' (%d/%d)" % 
                     (tag, pv, i, len(pvs)))
    logging.info("--end batch tag add")

def removeTagPvs(cf, tag, pvs, owner):
    cf.delete(tag=Tag(tag, owner), channelNames=pvs)
    logging.info("--batch remove tag '%s' to %d pvs" % (tag, len(pvs)))
    for i, pv in enumerate(pvs):
        logging.info("remove tag '%s' from '%s' (%d/%d)" % 
                     (tag, pv, i, len(pvs)))
    logging.info("--end batch tag remove")


def removePvProperty(cf, pvname, prpt, prptval):
    """remove pv property"""
    cfprpt = cf.find(name=pvname, property = [(prpt, prptval)])
    if cfprpt is None:
        logging.warn("'%s' has no property {'%s': %s}"  % 
                     (pvname, prpt, str(prptval)))
        return False
    cf.delete(channelName = pvname, property = cfprpt)
    
def removePropertyPvs(cf, p, owner, pvs):
    logging.info("remove property '%s' from %d pvs '%s'" % 
                 (p, len(pvs), str(pvs)))
    cf.delete(property = Property(p, owner), channelNames = pvs)

def addPvProperty(cf, pv, p, v, owner):
    if not hasProperty(cf, p):
        cf.set(property=Property(p, owner, v))
    cf.update(channelName=pv, property=Property(p, owner, v))

def addPropertyPvs(cf, p, owner, v, pvs):
    if not hasProperty(cf, p):
        cf.set(property=Property(p, owner, v))
        logging.info("create new property (%s,%s,%s)" % (p, owner, v))
    cf.update(property=Property(p, owner, v), channelNames=pvs)
    logging.info("batch add property (%s,%s,%s) for %d pvs" % (p, owner, v, len(pvs)))


def update_cfs_from_cmd(cmd_list):
    """
    update the cfs from command file:

        PV command property=value,p2=v2,tag

    The properties are updated as 'cf-asd' account, and tags in 'cf-aphla'
    """
    print "# Updating CFS from text file"
    
    cf = ChannelFinderClient(**cfinput)

    pvs = []
    
    # read each line of the txt command file
    for i, line in enumerate(cmd_list.readlines()):
        if not line.strip(): continue
        if line.strip().find('#') == 0: continue

        rec = line.strip().split()
        if len(rec) <= 2: 
            logging.warning("skiping line %d: %s" % (i, line))
            continue

        if rec[0] == 'addtag':
            pvs = [pv.strip() for pv in rec[2].split(',')]
            addTagPvs(cf, rec[1].strip(), pvs, OWNER)
            continue
        elif rec[0] == 'removetag':
            pvs = [pv.strip() for pv in rec[2].split(',')]
            removeTagPvs(cf, rec[1].strip(), pvs, OWNER)
            continue
        elif rec[0] == 'addproperty':
            pvs = [pv.strip() for pv in rec[2].split(',')]
            prpt, val = rec[1].split('=')
            if val == "''": val = ''
            addPropertyPvs(cf, prpt, PRPTOWNER, val, pvs)
            continue
        elif rec[0] == 'removeproperty':
            pvs = [pv.strip() for pv in rec[2].split(',')]
            prpt = rec[1].strip()
            removePropertyPvs(cf, prpt, PRPTOWNER, pvs)
        pv = rec[0]
        cmd = rec[1]
        newval = ''.join(rec[2:])
        for v in [v.strip() for v in newval.split(',')]:
            if v.find('=') >= 0:
                # it is a property
                prpt, val = v.split('=')
                if cmd == 'add':
                    print "add", prpt, val
                    addPvProperty(cf, pv, prpt, val, PRPTOWNER)
            else:
                # tag:
                if cmd == 'add': addPvTag(cf, pv, v, OWNER)
                elif cmd == 'remove': removePvTag(cf, pv, v, OWNER)



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--cmd', type=file, help="run command list")
    arg = parser.parse_args()
    #print arg.cmd
    #sys.exit()

    print "#", channelfinder.__file__,
    print "#", time.ctime(os.path.getmtime(channelfinder.__file__))

    update_cfs_from_cmd(arg.cmd)

    #addPvTags('LTB:MG{HCor:2BD1}Fld-SP', 'aphla.sys.LTD1')
    #addPvTags('LTB:MG{VCor:2BD1}Fld-SP', 'aphla.sys.LTD1')
    #updatePvProperties('LTB-BI:BD1{VF1}Size:X-I', 'elemField', 'x')
    #updatePvProperties('LTB-BI:BD1{VF1}Size:Y-I', 'elemField', 'y')
    #updatePvProperties('LTB-BI:BD1{VF1}Img1:ArrayData', 'elemField', 'image')

    #if len(sys.argv) > 2 and os.path.exists(sys.argv[1]):
    #    update_cfs_from_txt(sys.argv[1])
    #else:
    #    print "Usage: %s txtfile" % (sys.argv[0],)
        
