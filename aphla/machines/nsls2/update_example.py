import sys, os
#import h5py

import channelfinder

from channelfinder import ChannelFinderClient
from channelfinder import Channel, Property, Tag

import conf

cfsurl = os.environ.get('HLA_CFS_URL', 'https://channelfinder.nsls2.bnl.gov:8181/ChannelFinder')

cfinput = {
    'BaseURL': cfsurl,
    'username': conf.username,
    'password': conf.password
    }

OWNER = 'cf-aphla'
PRPTOWNER = 'cf-asd'

def update():
    cf = ChannelFinderClient(**cfinput)

    chs = cf.find(property=[('elemType', 'QUAD'), ('system', 'BR')])
    #print "updating {0} elemField=b0".format([ch.Name for ch in chs])
    cf.update(property=Property('elemLength', PRPTOWNER, '0.305'),
                  channelNames = [ch.Name for ch in chs])

if __name__ == "__main__":
    update()
