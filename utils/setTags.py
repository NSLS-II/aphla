#!/usr/bin/env python

"""
Set Channel Finder Data
================================

Set tags for Channel Finder data

.. warning::

  Used by Lingyun for testing purpose.

"""

import sys
import shelve
from time import gmtime, strftime

if __name__ == "__main__":
    sys.path.append('/home/lyyang/Downloads/python.channelfinder.api/src')
    from ChannelFinderClient import ChannelFinderClient
    from Channel import Channel, Tag, Property
    cf = ChannelFinderClient(BaseURL = 'http://channelfinder.nsls2.bnl.gov:8080/ChannelFinder')
    channels = cf.find(name='SR*')
    # a dict k=PV, v = property + tags
    d = {}
    conv_float = ['length', 's_position']
    conv_int = ['ordinal']
    for channel in channels:
        #print channel.Name, type(channel.Name)
        props = channel.getProperties()
        tags  = channel.getTags()
        if channel.Name[-7:] == '}Fld-SP':
            print channel.Name, props['elem_name']
            cf.add(channel=channel, tag = Tag('default.eput', owner='hla'))
        elif channel.Name[-6:] == '}Fld-I':
            print channel.Name, props['elem_name']
            cf.add(channel=channel, tag = Tag('default.eget', owner='hla'))

#        client.remove(channelName=(u'%s' % channel.Name))
    print len(channels)
    #f = shelve.open('chanfinder.pkl', 'c')
    #f['cfa.create_date'] = strftime("%Y-%m-%dT%H:%M:%S", gmtime())
    #f['cfa.data'] = d
    #f.close()

