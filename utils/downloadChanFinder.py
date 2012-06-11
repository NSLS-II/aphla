#!/usr/bin/env python

"""
Download Channel Finder Data
================================

Download the Channel Finder data to local file

.. warning::

  Used by Lingyun for testing purpose.

"""

import os, sys
import shelve
from time import gmtime, strftime


if __name__ == "__main__":
    # 
    curdir = os.path.abspath(os.getcwd())
    print "# Current dir:", curdir
    sys.path.append(os.path.join(curdir, '..', 'lib'))
    #print sys.path

    import chanfinder
                    
    cfa = chanfinder.ChannelFinderAgent()
    # about 12 seconds
    #cfa.downloadCfs('http://channelfinder.nsls2.bnl.gov:8080/ChannelFinder', 
    #                property=[('hostName', 'virtac*')], tagName='aphla.sys.*')
    cfa.downloadCfs('http://channelfinder.nsls2.bnl.gov:8080/ChannelFinder', tagName='aphla.*')
    #cfa.importCsv('test1.csv')
    cfa.exportCsv('test1.csv')
    #cfa._exportJson('test1.json')
    #cfa._importJson('test1.json')
    #cfa.sort('elemName')
    print cfa.tags('aphla.sys.*')

