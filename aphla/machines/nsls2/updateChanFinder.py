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
    #cf.set(property=Property('test-prop1', 'lyyang', 'v1'))
    #cf.set(property=Property('test-prop2', 'cf-asd', 'v2'))
    #cf.set(property=Property('test-prop3', 'lyyang'))
    #cf.set(property=Property('test-prop4', 'lyyang'))
    #cf.delete(propertyName='test-prop1')
    #cf.delete(propertyName='test-prop3')

    pvname1='SR:C00-BI:G00{DCCT:00}CUR-RB'
    pvname2='SR:C00-Glb:G00{CHROM:00}RB-X'
    pvname3='SR:C00-Glb:G00{CHROM:00}RB-Y'
    cf.update(property=Property('test-prop2', 'cf-asd', 'v1'),
              channelNames=[pvname1, pvname2, pvname3])
    #chs = cf.find(property=[('test-prop2', '*')])
    #if chs is not None:
    #    for ch in chs:
    #        print ch.Name
    #        for p in ch.Properties: 
    #            print "  ", p.Name,"=",p.Value, p.Owner, ", "
    #        print "/"

    cf.delete(property=Property('test-prop2', 'cf-asd', 'v1'), 
              channelNames=[pvname2, pvname3])
    chs = cf.find(property=[('test-prop2', '*')])
    if chs is not None:
        for ch in chs:
            print ch.Name,
            for p in ch.Properties: 
                print p.Name,"=",p.Value,", ", 
            print " /"

    #cf.update(property=Property('test-prop4', 'cf-asd', 'vt1'),
    #          channelNames=[pvname1, pvname2, pvname3])
    #cf.delete(property=Property('test-prop4', 'cf-asd'), 
    #          channelNames=[pvname2, pvname3])
    #chs = cf.find(property=[('test-prop4', '*')])
    #if chs is not None:
    #    for ch in chs:
    #        print ch.Name,
    #        for p in ch.Properties: 
    #            print p.Name,"=",p.Value,", ", 
    #        print " /"

def hasTag(cf, tag):
    """check if tag exists"""
    for t in cf.getAllTags():
        if t.Name == tag: return True

    return False

def hasProperty(cf, prpt):
    """check if property name exists"""
    # a property exists if its name exists. Not its whole (p,v) pair.  if want
    # to check existance before creating a new one, we should check the name
    # first (no value). If no, set then update value with PV.
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
    """
    """
    if not hasProperty(cf, p):
        # in this set, value of property is not needed (confusing).  since set
        # is creating a new (p,v) pair. Before attach it to a PV, its value is
        # meaningless.
        cf.set(property=Property(p, owner, v))
        logging.info("create new property (%s,%s,%s)" % (p, owner, v))
    cf.update(property=Property(p, owner, v), channelNames=pvs)
    logging.info("batch add property (%s,%s,%s) for %d pvs" % (p, owner, v, len(pvs)))

def cfs_append_from_csv1(rec_list, update_only):
    cf = ChannelFinderClient(**cfinput)
    all_prpts = [p.Name for p in cf.getAllProperties()]
    all_tags  = [t.Name for t in cf.getAllTags()]
    ignore_prpts = ['hostName', 'iocName']
    import csv
    rd = csv.reader(rec_list)
    # header line
    header = rd.next()
    # lower case of header
    hlow = [s.lower() for s in header]
    # number of headers, pv + properties
    nheader = len(header)
    # the index of PV, properties and tags
    ipv = hlow.index('pv')
    # the code did not rely on it, but it is a good practice
    if ipv != 0:
        raise RuntimeError("the first column should be pv")

    iprpt, itags = [], []
    for i, h in enumerate(header):
        if i == ipv: continue
        # if the header is empty, it is a tag
        if len(h.strip()) == 0: 
            itags.append(i)
        else:
            iprpt.append(i)

    tag_owner = OWNER
    prpt_owner = PRPTOWNER
    tags = {}
    # the data body
    for s in rd:
        prpts = [Property(header[i], prpt_owner, s[i]) for i in iprpt if s[i]]
        # itags could be empty if we put all tags in the end columns
        for i in itags + range(nheader, len(s)):
            rec = tags.setdefault(s[i].strip(), [])
            rec.append(s[ipv].strip())

        #print s[ipv], prpts, tags
        ch = cf.find(name=s[ipv])
        if ch is None:
            logging.warning("pv {0} does not exist".format(s[ipv]))
        elif len(ch) > 1:
            logging.warning("pv {0} is not unique ({1})".format(s[ipv], len(ch)))
        else:
            for p in prpts:
                #continue
                if p.Name in ignore_prpts: continue
                #if p.Name != 'symmetry': continue
                logging.info("updating '{0}' with property, {1}={2}".format(
                        s[ipv], p.Name, p.Value))
                cf.update(channelName=s[ipv], property=p)

    logging.info("finished updating properties")
    for t,pvs in tags.iteritems():
        if not hasTag(cf, t): cf.set(tag=Tag(t, tag_owner))
        if 'V:1-SR-BI{BETA}X-I' in pvs: continue
        if 'V:1-SR-BI{BETA}Y-I' in pvs: continue
        try:
            cf.update(tag=Tag(t, tag_owner), channelNames=pvs)
        except:
            print t, pvs
            raise

        logging.info("update '{0}' for {1} pvs".format(t, len(pvs)))
    logging.info("finished updating tags")


def cfs_append_from_csv2(rec_list, update_only):
    cf = ChannelFinderClient(**cfinput)
    all_prpts = [p.Name for p in cf.getAllProperties()]
    all_tags  = [t.Name for t in cf.getAllTags()]
    ignore_prpts = ['hostName', 'iocName']
    import csv
    rd = csv.reader(rec_list)

    tag_owner = OWNER
    prpt_owner = PRPTOWNER
    prpt_data, tag_data = {}, {}
    # the data body
    for s in rd:
        if not s: continue
        if not s[0].strip(): continue
        if s[0].strip().startswith('#'): continue
        
        pv = s[0]
        for r in s[1:]:
            if r.find('=') > 0:
                prpt, val = [v.strip() for v in r.split('=')]
                prpt_data.set_default((prpt, val), [])
                prpt_data[(prpt, val)].append(pv)
            else:
                # it is a tag
                tag_data.set_default(r.strip(), [])
                tag_data.append(pv)

    for k,v in prpt_data.iteritems():
        addPropertyPvs(cf, k[0], prpt_owner, k[1], v)
        logging.info("add property {0} for pvs {1}".format(k, v))
    for k,v in tag_data.iteritems():
        addTagPvs(cf, k, v, tag_owner)
        logging.info("add tag {0} for pvs {1}".format(k, v))



def cfs_append_from_cmd(cmd_list, update_only = False):
    """
    update the cfs from command file:

        addtag tag pv1,pv2,pv3
        removetag tag pv1,pv2,...
        addproperty prpt=val pv1,pv2
        removeproperty prpt pv1,pv2

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
    #simple_test()
    #sys.exit(0)

    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--cmd', type=file, help="run command list")
    group.add_argument('--csv1', type=file, help="update with this csv1 file")
    group.add_argument('--csv2', type=file, help="update with this csv2 file")
    parser.add_argument('-u', '--update-only', action="store_true", 
                        help="do not create new")
    
    arg = parser.parse_args()

    print "#", channelfinder.__file__,
    print "#", time.ctime(os.path.getmtime(channelfinder.__file__))

    if arg.cmd:
        print "CMD"
        cfs_append_from_cmd(arg.cmd, update_only = arg.update_only)
    elif arg.csv1:
        cfs_append_from_csv1(arg.csv1, update_only = arg.update_only)
    elif arg.csv2:
        cfs_append_from_csv2(arg.csv2, update_only = arg.update_only)



    #addPvTags('LTB:MG{HCor:2BD1}Fld-SP', 'aphla.sys.LTD1')
    #addPvTags('LTB:MG{VCor:2BD1}Fld-SP', 'aphla.sys.LTD1')
    #updatePvProperties('LTB-BI:BD1{VF1}Size:X-I', 'elemField', 'x')
    #updatePvProperties('LTB-BI:BD1{VF1}Size:Y-I', 'elemField', 'y')
    #updatePvProperties('LTB-BI:BD1{VF1}Img1:ArrayData', 'elemField', 'image')

    #if len(sys.argv) > 2 and os.path.exists(sys.argv[1]):
    #    update_cfs_from_txt(sys.argv[1])
    #else:
    #    print "Usage: %s txtfile" % (sys.argv[0],)
        
