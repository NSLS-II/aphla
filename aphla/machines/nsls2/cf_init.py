#
import os
import sys
import re
import conf
import string

from channelfinder import ChannelFinderClient
from channelfinder import Channel, Property, Tag

import logging
logging.basicConfig(filename='cf_init.log.txt',
    format='%(asctime)s - %(name)s [%(levelname)s]: %(message)s',
    level=logging.DEBUG)

cfsurl = os.environ.get('HLA_CFS_URL', 'https://channelfinder.nsls2.bnl.gov:8181/ChannelFinder')

cfinput = {
    'BaseURL': cfsurl,
    'username': conf.username,
    'password': conf.password
    }

OWNER = 'cf-aphla'
PRPTOWNER = 'cf-asd'

def init_ring_par(fname):
    cf = ChannelFinderClient(**cfinput)
    fcsv = open("SR_cf_init.csv", "w")
    # example name: QH1G2C30A
    p = re.compile(r"(\w+)(G[0-9])(C[0-9]+)([ABC])$")
    for line in open(fname, 'r').readlines():
        r = line.split()
        if len(r) < 4: continue
        ename, et, L, se = r[:4]
        if et in ['DRIF']: continue
        elif et in ['QUAD']:
            m = p.match(ename)
            basename, girder, cell, symm = m.groups()
            prpt = "elemName= %s, elemType= QUAD, system= SR, elemLength= %s, elemPosition= %s" % (ename, L, se)
            tags = "aphla.sys.SR"

            pat = "SR:%s-MG{PS:%s%s}*" % (cell, basename, symm)
            chs = cf.find(name=pat)
            if chs is None: 
                logging.warn("None for element '%s'" % ename)
                continue
            for ch in chs:
                if re.match(r".*}I:SP1-SP", ch.Name, flags=re.I):
                    fcsv.write("%s, elemHandle= put, elemField= b1, %s, %s\n" \
                               % (ch.Name, prpt, tags))
                elif re.match(r".*}I:PS1DCCT1-I", ch.Name, flags=re.I):
                    fcsv.write("%s, elemHandle= put, elemField= b1, %s, %s\n" \
                               % (ch.Name, prpt, tags))
        else:
            logging.info("element '%s:%s' is not handled" % (ename, et))
    fcsv.close()

def test():
    cf = ChannelFinderClient(**cfinput)

    chs = cf.find(name="SR:C*-MG*SP1-SP")
    #print "updating {0} elemField=b0".format([ch.Name for ch in chs])
    print "found pvs: %d" % len(chs)


if __name__ == "__main__":
    #test()
    init_ring_par("ring_par.txt")

