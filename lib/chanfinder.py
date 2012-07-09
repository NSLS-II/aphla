#!/usr/bin/env python

"""
Channel Finder
---------------

A module providing local Channel Finder Service (CFS).

For each PV, Channel Finder Service (CFS) provide a set of properties and
tags. This can help us to identify the associated element name, type, location
for every PV. The PVs are also tagged for 'default' read/write for a element
it is linked.
"""
from __future__ import print_function, unicode_literals

from fnmatch import fnmatch
from time import gmtime, strftime


class ChannelFinderAgent(object):
    """
    Channel Finder Agent

    This module builds a local cache of channel finder service. It can imports
    data from CSV format file.
    """
    
    def __init__(self, **kwargs):
        self.__cdate = strftime("%Y-%m-%dT%H:%M:%S", gmtime())
        self.source = None
        self.rows = []  # nx3 list, n*(pv, prpts, tags), (str, dict, list)

    def downloadCfs(self, cfsurl, **kwargs):
        """
        downloads data from channel finder service.
        
        - *cfsurl* the URL of channel finder service.
        - *keep* if present, it only downloads specified properties.
        - *converter* convert properties from string to other format.

        :Example:

          prpt_list = ['elemName', 'sEnd']
          conv_dict = {'sEnd', float}
          downloadCfs(URL, keep = prpt_list, converter = conv_dict)
          downloadCfs(URL, property=[('hostName', 'virtac2')])
          downloadCfs(URL, property=[('hostName', 'virtac')], tagName='aphla.*')

        The channel finder client API provides *property* and *tagName* as
        keywords parameters. 
        """
        keep_prpts = kwargs.pop('keep', None)
        converter  = kwargs.pop('converter', {})
        self.source = cfsurl

        from channelfinder import ChannelFinderClient
        cf = ChannelFinderClient(BaseURL = cfsurl)
        if len(kwargs) == 0:
            chs = cf.find(name='*')
        else:
            #print kwargs
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
        sort the data by 'pv' or other property name.

        Example::

          sort('pv')
          sort('elemName')
        """
        from operator import itemgetter
        if key == 'pv':
            self.rows.sort(key = itemgetter(0))
        else:
            self.rows.sort(key=lambda k: k[1][key])            

    def renameProperty(self, oldkey, newkey):
        """
        rename the property name
        """
        for r in self.rows:
            if oldkey not in r[1]: continue
            r[1][newkey] = r[1].pop(oldkey)

    def importCsv(self, fname):
        head = open(fname, 'r').readline()
        if head.split(',')[0].strip() in ['pv', 'PV']:
            self._import_csv_1(fname)
        else:
            self._import_csv_2(fname)


    def _import_csv_1(self, fname):
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
        self.source = fname
        import csv
        rd = csv.reader(open(fname, 'r'))
        # header line
        header = rd.next()
        # lower case of header
        hlow = [s.lower() for s in header]
        # number of headers, pv + properties
        nheader = len(header)
        # the index of PV, properties and tags
        ipv = hlow.index('pv')
        iprpt, itags = [], []
        for i, h in enumerate(header):
            if i == ipv: continue
            # if the header is empty, it is a tag
            if len(h.strip()) == 0: 
                itags.append(i)
            else:
                iprpt.append(i)
        #print ipv, iprpt, itags
        for s in rd:
            prpts = dict([(header[i], s[i]) for i in iprpt if s[i].strip()])
            # itags could be empty if we put all tags in the end columns
            tags = [s[i].strip() for i in itags]
            for i in range(nheader, len(s)):
                tags.append(s[i].strip())
            #print s[ipv], prpts, tags
            self.rows.append([s[ipv], prpts, tags])

    def _import_csv_2(self, fname):
        """
        import data from CSV (comma separated values). 

        each line of csv starts with pv name, then property list and tags. An
        example is in the following::

          PV1, elemName=Name,sEnd=0.2, aphla.sys.SR,aphla.elemfield.f1
        """
        self.source = fname
        import csv
        rd = csv.reader(open(fname, 'r'))
        for s in rd:
            pv = s[0]
            prpts, tags = {}, []
            for cell in s[1:]:
                if cell.find('=') > 0:
                    k, v = cell.split('=')
                    prpts[k.strip()] = v.strip()
                else:
                    tags.append(cell.strip())

            if pv.startswith('#') and len(prpts) == 0: continue
            self.rows.append([pv, prpts, tags])

    def exportCsv(self, fname):
        """
        export the CFS in CSV format.
        """
        # find out all the property names
        prpts_set = set()
        for r in self.rows:
            if r[1] is None: continue
            for k in r[1]: 
                prpts_set.add(k)
        header = sorted(list(prpts_set))
        #print header
        import csv
        writer = csv.writer(open(fname, 'wb'))
        writer.writerow(["PV"] + header)
        for r in self.rows:
            prpt = []
            for k in header:
                if r[1] is None: 
                    prpt.append('')
                elif k not in r[1]: 
                    prpt.append('')
                else: 
                    prpt.append(r[1][k])
            if r[2] is None:
                writer.writerow([r[0]] + prpt)
            else:
                writer.writerow([r[0]] + prpt + list(r[2]))
        del writer

    def _importJson(self, fname):
        self.source = fname
        import json
        f = open(fname, 'r')
        d = json.load(f)
        self.__cdate = d['__cdate']
        self.rows = d['rows']
        f.close()

    def _exportJson(self, fname):
        import json
        f = open(fname, 'w')
        json.dump({'__cdate': self.__cdate, 'rows': self.rows}, f)
        f.close()

    def update(self, pv, prpts, tags):
        """
        update the properties and tags for pv

        :param pv: pv
        :param prpts: property dictionary
        :param tags: list of tags
        """
        idx = -1
        for i, rec in enumerate(self.rows):
            if rec[0] != pv: continue
            idx = i
            rec[1].update(prpts)
            for tag in tags:
                if tag in rec[2]: continue
                rec[3].append(tag)
        if idx < 0:
            self.rows.append([pv, prpts, tags])
            idx = len(self.rows) - 1
        return idx

    def updateCfs(self, cfsurl, username, password, **kwargs):
        """
        """
        #raise RuntimeError("not implemented")

        properties    = kwargs.get('properties', '*')
        tags          = kwargs.get('tags', '*')

        from channelfinder import ChannelFinderClient
        from channelfinder import Channel, Property, Tag
        cf = ChannelFinderClient(BaseURL = cfsurl, username=username, 
                                 password=password)
        all_prpts = [p.Name for p in cf.getAllProperties()]
        all_tags  = [t.Name for t in cf.getAllTags()]

        for i,r in enumerate(self.rows):
            pv, prpt, stags = r
            ch = cf.find(name=pv)
            if not ch or len(ch) > 1:
                print("channel matching error '%s'" % pv)
                continue
            prpts = []
            for p,v in prpt.iteritems():
                if p not in all_prpts: continue
                if not fnmatch(p, properties): continue
                cf.update(property=Property(p, 'cf-asd', v), channelName=pv)
            tags = []
            for t in stags:
                tags.append(Tag(t, 'cf-aphla'))
            #if len(prpts) == 0 and len(tags) == 0:
            #    continue
            #cf.update(channel=Channel(pv, ch[0].Owner, properties=prpts, tags = tags))


    def tags(self, pat):
        """
        return a list of tags matching the unix filename pattern *pat*.
        """
        alltags = set()
        for r in self.rows:
            for t in r[2]: alltags.add(t)
        return [t for t in alltags if fnmatch(t, pat)]

    def groups(self, key = 'elemName', **kwargs):
        """
        group the data according to their property *key*.

        e.g. groups(key='elemName') will return a dictionary with keyes the
        element names, values a list of indeces which share the same element
        name.

        Example::

          groups()
          {'BPM1': [0, 3], 'Q1': [1], 'COR1' : [2]}
        """
        
        ret = {}
        for i, r in enumerate(self.rows):
            # skip if no properties
            if r[1] is None: continue
            # skip if no interesting properties
            if key not in r[1]: continue

            # record the property-value and its index. Append if
            # property-value exists.
            v = ret.setdefault(r[1][key], [])
            v.append(i)
        return ret

    def __sub__(self, rhs):
        """
        the result has no info left if it was same as rhs, ignore empty properties in self
        """
        samp = dict([(rec[0],i) for i,rec in enumerate(rhs.rows)])
        ret = {}
        for pv, prpt, tags in self.rows:
            if not samp.has_key(pv):
                ret[pv] = (prpt, tags)
                continue
            rec2 = rhs.rows[samp[pv]]
            p2, t2 = rec2[1], rec2[2]
            ret[pv] = [{}, []]
            for k,v in prpt.iteritems():
                if not p2.has_key(k):
                    ret[pv][0][k] = v
                    continue
                elif p2[k] != v:
                    ret[pv][0][k] = v
            for t in tags:
                if t in t2: continue
                ret[pv][1].append(t)
        return ret

        #print(pv, prpt, tags)

if __name__ == "__main__":
    cfa = ChannelFinderAgent()
    # about 12 seconds
    #cfa.downloadCfs('http://channelfinder.nsls2.bnl.gov:8080/ChannelFinder', 
    #                property=[('hostName', 'virtac*')], tagName='aphla.sys.*')
    cfa.downloadCfs('http://channelfinder.nsls2.bnl.gov:8080/ChannelFinder', 
                    tagName='aphla.*')
    #cfa.importCsv('test1.csv')
    cfa.exportCsv('test1.csv')
    #cfa._exportJson('test1.json')
    #cfa._importJson('test1.json')
    #cfa.sort('elemName')
    print(cfa.tags('aphla.sys.*'))
