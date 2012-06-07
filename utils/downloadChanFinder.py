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

if __name__ == "__main__":
    #sys.path.append('/home/lyyang/Downloads/python.channelfinder.api/src')
    from channelfinder import ChannelFinderClient
    cf = ChannelFinderClient(BaseURL = 'http://channelfinder.nsls2.bnl.gov:8080/ChannelFinder')
    channels = cf.find(name='SR*')
    # a dict k=PV, v = property + tags
    d = {}
    conv_float = ['length', 's_position']
    conv_int = ['ordinal']
    for channel in channels:
        #print channel.Name, type(channel.Name)
        d[channel.Name] = {'~tags': []}
        props = channel.getProperties()
        tags  = channel.getTags()
        if props is None:
            print "Empty prop: ", channel.Name
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
            pass
        else:
            print "Empty tags:", channel.Name
#        client.remove(channelName=(u'%s' % channel.Name))
    print "Channels: ", len(channels), "in total"
    #f = shelve.open('chanfinder.pkl', 'c')
    #f['cfa.create_date'] = strftime("%Y-%m-%dT%H:%M:%S", gmtime())
    #f['cfa.data'] = d
    #f.close()

    cnt = []
    for k,v in d.items():
        print k,
        for p,val in v.items():
            if p == '~tags': continue
            print ", %s=%s" % ( p, val ),
        if v.has_key('~tags'):
            print "   TAGS:",
            for t in v['~tags']: print t,
            print ""
        #print ""
    print cnt
    # save 
