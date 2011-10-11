#!/usr/bin/env python

"""
Download Channel Finder Data
================================

Download the Channel Finder data to local file

.. warning::

  Used by Lingyun for testing purpose.

"""

import sys
import shelve
from time import gmtime, strftime

from channelfinder import ChannelFinderClient, Channel, Tag, Property

cfsurl = 'http://channelfinder.nsls2.bnl.gov:8080/ChannelFinder'

if __name__ == "__main__":
    
    cf = ChannelFinderClient(BaseURL = cfsurl)
    channels = cf.find(tagName='aphla.sys.SR')
    # a dict k=PV, v = property + tags
    f = open('output.txt', 'w')
    for ch in channels:
        f.write("%s; " % ch.Name)
        else:
            for k, v in props.items():
                #print "    %s:" % k, v, type(v)
                if k in conv_int:
                    d[channel.Name][k] = int(v)
                elif k in conv_float:
                    d[channel.Name][k] = float(v)
                elif k == 'cell' and v[0] != 'C':
                    d[channel.Name][k] = u'C'+v
                elif k == 'girder' and v[0] != 'G':
                    d[channel.Name][k] = u'G'+v
                else:
                    d[channel.Name][k] = v
        if tags:
            print "    TAGS:",
            for t in tags:
                print t,
            print ""

#        client.remove(channelName=(u'%s' % channel.Name))
    print len(channels)
    #f = shelve.open('chanfinder.pkl', 'c')
    #f['cfa.create_date'] = strftime("%Y-%m-%dT%H:%M:%S", gmtime())
    #f['cfa.data'] = d
    #f.close()

    cnt = []
    for k,v in d.items():
        if not k[-6:] in cnt: cnt.append(k[-6:])
        continue

        print k
        for p,val in v.items():
            if p == '~tags': continue
            print "  ", p, val, type(v)
        if v.has_key('~tags'):
            print "   TAGS:",
            for t in v['~tags']: print t,
            print ""
        print ""
    print cnt
    # save 
