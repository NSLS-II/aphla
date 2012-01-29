#!/usr/bin/env python

"""
A module providing local Channel Finder Service (CFS).

For each PV, Channel Finder Service (CFS) provide a set of properties and
tags. This can help us to identify the associated element name, type, location
for every PV. The PVs are also tagged for 'default' read/write for a element
it is linked.
"""

import re, shelve, sys, os
from fnmatch import fnmatch
from time import gmtime, strftime


#
#class ChannelFinderRecord(object):
#    def __init__(self, pv, properties = None, tags = None):
#        self.pv = pv
#        self.properties = properties
#        self.tags = tags
#
#        if 'pv' in properties or 'tags' in properties:
#            raise ValueError('property name can not be "pv" or "tags"')
#
    
class ChannelFinderAgent(object):
    """
    Channel Finder Agent

    This module builds a local cache of channel finder service. It can imports
    data from CSV format file.
    """
    
    def __init__(self, **kwargs):
        self.__cdate = strftime("%Y-%m-%dT%H:%M:%S", gmtime())
        self.rows = []

    def downloadCfs(self, cfsurl, **kwargs):
        """
        downloads data from channel finder service.
        
        - *cfsurl* the URL of channel finder service.
        - *properties* optional list of properties to download
        - *converter* convert properties from string to other format.

        Example::

          >>> prpt_list = ['elemName', 'sEnd']
          >>> conv_dict = {'sEnd', float}
          >>> downloadCfs(URL, keep = prpt_list, converter = conv_dict)
          >>> downloadCfs(URL, property=[('hostName', 'virtac2')])
          >>> downloadCfs(URL, property=[('hostName', 'virtac')], tagName='aphla.*')
        """
        keep_prpts = kwargs.pop('keep', None)
        converter  = kwargs.pop('converter', {})
        from channelfinder import ChannelFinderClient, Channel, Property, Tag
        cf = ChannelFinderClient(BaseURL = cfsurl)
        if len(kwargs) == 0:
            chs = cf.find(name='*')
        else:
            print kwargs
            chs = cf.find(**kwargs)
        if keep_prpts is None:
            # use all possible property names
            keep_prpts = [p.Name for p in cf.getAllProperties()]
            
        #print "# include properties", properties
        for ch in chs:
            # keep only known properties
            prptdict = ch.getProperties()
            # prpts is known part from prptdict, otherwise empty dict
            if prptdict is not None:
                prpts = dict([v for v in prptdict.iteritems()])
                # convert the data type
                for k in converter:
                    prpts[k] = converter[k](prpts[k])
            else:
                prpts = None
            # the empty tags could be None
            self.rows.append([ch.Name, prpts, ch.getTags()])
            del prptdict

        
    def sort(self, key):
        """
        sort the data.

        Example::

          >>> sort('pv')
          >>> sort('elemName')
        """
        from operator import itemgetter, attrgetter
        if key == 'pv':
            self.rows.sort(key = itemgetter(0))
        else:
            self.rows.sort(key=lambda k: k[1][key])            
        pass

    def renameProperty(self, oldkey, newkey):
        """
        """
        for r in self.rows:
            if oldkey not in r[1]: continue
            r[1][newkey] = r[1].pop(oldkey)

    def importCsv(self, fname):
        """
        import data from CSV (comma separated values). The first line of csv
        file must be the "header" which describes the meaning of each column.
        The column of PVs has a fixed header "pv" and the tags columns have an
        empty header. The order of columns does matter.

        It is recommended to put PV name as the first column and then all the
        property columns. The tags which have no header are in the last
        columns.

        As in channel finder service, the property names are case insensitive.
        """
        import csv
        rd = csv.reader(open(fname, 'r'))
        #print rd.fieldnames
        header = rd.next()
        hlow = [s.lower() for s in header]
        print header, hlow
        nheader = len(header)
        ipv = hlow.index('pv')
        iprpt, itags = [], []
        for i,h in enumerate(header):
            if i == ipv: continue
            if len(h) == 0: itags.append(i)
            else: iprpt.append(i)
        print ipv, iprpt, itags
        for s in rd:
            prpts = dict([(header[i], s[i]) for i in iprpt])
            tags = [s[i] for i in itags]
            for i in range(nheader, len(s)):
                tags.append(s[i])
            #print s[ipv], prpts, tags
            self.rows.append([s[ipv], prpts, tags])
        pass

    def exportCsv(self, fname):
        prpts_set = set()
        for r in self.rows:
            if r[1] is None: continue
            #print r
            for k in r[1]: prpts_set.add(k)
        header = sorted(list(prpts_set))
        #print header
        import csv
        writer = csv.writer(open(fname, 'wb'))
        writer.writerow(["PV"] + header)
        for r in self.rows:
            prpt = []
            for k in header:
                if r[1] is None: prpt.append('')
                elif k not in r[1]: prpt.append('')
                else: prpt.append(r[1][k])
            if r[2] is None:
                writer.writerow([r[0]] + prpt)
            else:
                writer.writerow([r[0]] + prpt + list(r[2]))
        del writer

    def _importJson(self, fname):
        import json
        f = open(fname, 'r')
        d = json.load(f)
        self.__cdate = d['__cdate']
        self.rows = d['rows']
        f.close()
        pass

    def _exportJson(self, fname):
        import json
        f = open(fname, 'w')
        json.dump({'__cdate': self.__cdate, 'rows': self.rows}, f)
        f.close()

    def tags(self, pat):
        alltags = set()
        for r in self.rows:
            for t in r[2]: alltags.add(t)
        return [t for t in alltags if fnmatch(t, pat)]

    def groups(self, key = 'elemName', **kwargs):
        """
        """
        
        ret = {}
        for i,r in enumerate(self.rows):
            if r[1] is None: continue
            if key not in r[1]: continue
            name = r[1][key]
            if name not in ret: ret[name] = []
            ret[name].append(i)
        return ret


if __name__ == "__main__":
    cfa = ChannelFinderAgent()
    # about 12 seconds
    #cfa.downloadCfs('http://channelfinder.nsls2.bnl.gov:8080/ChannelFinder', 
    #                property=[('hostName', 'virtac')], tagName='aphla.sys.*')
    cfa.importCsv('test1.csv')
    #cfa.exportCsv('test1.csv'
    cfa._exportJson('test1.json')
    cfa._importJson('test1.json')
    #cfa.sort('elemName')
    print cfa.tags('aphla.sys.*')
    sys.exit(0)

    #cfa.importCsv('/home/lyyang/devel/nsls2-hla/machine/nsls2/test.csv')
    for i,r in enumerate(cfa.rows):
        if 'elemName' not in r[1]: continue
        print r[1]['elemName'], r[0]
    #cfa.renameProperty('elemName', 'elem_name')
    #print cfa.rows
    sys.exit(0)

    cfa.downloadCfs('http://channelfinder.nsls2.bnl.gov:8080/ChannelFinder',
                    keep_prpts = ['elemName', 'cell', 'girder', 'symmetry', 
                                  'system', 'sEnd'],
                    converter = {'sEnd': float},
                    tagName='aphla.sys.LTB')
    cfa.sort('elemName')
    for r in cfa.rows:
        print r[1]['elemName'], r[0]
