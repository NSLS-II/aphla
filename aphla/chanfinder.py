"""
Channel Finder
---------------

A module providing local Channel Finder Service (CFS). It interfaces to CFS or
local comma separated file (csv) and provides configuration data for the aphla
package.

For each PV, Channel Finder Service (CFS) provide a set of properties and
tags. This can help us to identify the associated element name, type, location
for every PV. The PVs are also tagged for 'default' read/write for a element
it is linked.
"""

# :author: Lingyun Yang <lyyang@bnl.gov>

from __future__ import print_function, unicode_literals

from fnmatch import fnmatch
from time import gmtime, strftime
import sqlite3

import logging
_logger = logging.getLogger("aphla.chanfinder")

__all__ = ['ChannelFinderAgent']

class ChannelFinderAgent(object):
    """
    Channel Finder Agent

    This module builds a local cache of channel finder service. It can imports
    data from CSV format file.
    """
    
    def __init__(self, **kwargs):
        """
        initialzation.
        """
        self.__cdate = strftime("%Y-%m-%dT%H:%M:%S", gmtime())
        self.source = None
        self.use_unicode = False
        # the data is in `rows`. It has (n,3) shape, n*(pv, prpts, tags) with
        # type (str, dict, list)
        self.rows = []  

    def downloadCfs(self, cfsurl, **kwargs):
        """
        downloads data from channel finder service.
        
        :param cfsurl: the URL of channel finder service.
        :type cfsurl: str
        :param keep: if present, it only downloads specified properties.
        :type keep: list
        :param converter: convert properties from string to other format.
        :type converter: dict

        :Example:

            >>> prpt_list = ['elemName', 'sEnd']
            >>> conv_dict = {'sEnd', float}
            >>> downloadCfs(URL, keep = prpt_list, converter = conv_dict)
            >>> downloadCfs(URL, property=[('hostName', 'virtac2')])
            >>> downloadCfs(URL, property=[('hostName', 'virtac')], tagName='aphla.*')

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
        if not chs: return

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
            else:
                prpts = None
            # the empty tags could be None
            if self.use_unicode:
                self.rows.append([unicode(ch.Name), 
                                  dict([(unicode(k), unicode(v))
                                        for k,v in prpts.iteritems()]),
                                  [unicode(v) for v in ch.getTags()]])
            else:
                self.rows.append([ch.Name.encode('ascii'), 
                                  dict([(k.encode('ascii'), v.encode('ascii'))
                                        for k,v in prpts.iteritems()]),
                                  [v.encode('ascii') for v in ch.getTags()]])
            if self.rows[-1][1]:
                for k in converter:
                    self.rows[-1][1][k] = converter[k](prpts[k])
            # warn if hostName or iocName does not present
            if "hostName" not in self.rows[-1][1]:
                _logger.warn("no 'hostName' for {0}".format(self.rows[-1]))
            if "iocName" not in self.rows[-1][1]:
                _logger.warn("no 'iocName' for {0}".format(self.rows[-1]))

            del prptdict


    def sort(self, fld, dtype = None):
        """
        sort the data by 'pv' or other property name.

        :Example:

            >>> sort('pv')
            >>> sort('elemName')
        """
        from operator import itemgetter
        if fld == 'pv':
            self.rows.sort(key = itemgetter(0))
        elif dtype is None:
            self.rows.sort(key=lambda k: k[1][fld])            
        elif dtype == 'str':
            self.rows.sort(key=lambda k: str(k[1].get(fld, "")))
        elif dtype == 'float':
            self.rows.sort(key=lambda k: float(k[1].get(fld, 0.0)))
        elif dtype == 'int':
            self.rows.sort(key=lambda k: int(k[1].get(fld, 0)))

    def renameProperty(self, oldkey, newkey):
        """
        rename the property name
        """
        n = 0
        for r in self.rows:
            if oldkey not in r[1]: continue
            r[1][newkey] = r[1].pop(oldkey)
            n += 1
        #print("Renamed %s records" % n)

    
    def loadCsv(self, fname):
        """
        import data from CSV (comma separated values).

        two versions of `.csv` files are supported:

            - with header. The first line of csv file must be the "header"
              which describes the meaning of each column.  The column of PVs
              has a fixed header "pv" and the tags columns have an empty
              header. The order of columns does matter.  
            - explicit properties. No header as the first line. The first
              column is the pv name, then is the "property= value" cells. The
              last set of cells are tags where no "=" in the string.
        """
        head = open(fname, 'r').readline()
        if head.split(',')[0].strip() in ['pv', 'PV']:
            self._load_csv_1(fname)
        else:
            self._load_csv_2(fname)
        self.source = fname

    def _load_csv_1(self, fname):
        """
        It is recommended to put PV name as the first column and then all the
        property columns. The tags which have no header are in the last
        columns.

        As in channel finder service, the property names are case insensitive.
        """
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

    def _load_csv_2(self, fname):
        """
        import data from CSV (comma separated values). 

        each line of csv starts with pv name, then property list and tags. An
        example is in the following::

          PV1, elemName=Name, elemPosition=0.2, aphla.sys.SR,aphla.elemfield.f1
        """
        f = open(fname, 'r')
        for i,line in enumerate(f.readlines()):
            s = line.strip()
            if s.startswith('#'): continue
            r = [v.strip() for v in s.split(',')]

            pv = r[0]
            if not pv: continue

            prpts, tags = {}, []
            for col in r[1:]:
                try:
                    k, v = col.split('=')
                    prpts[k.strip()] = v.strip()
                except ValueError as e:
                    tags.append(col.strip())

            self.rows.append([pv, prpts, tags])


    def loadSqlite(self, fname, **kwargs):
        """
        import from sqlite database (v1 with two tables)
        
        :param fname: sqlite db file name
        
        - NULL/None or '' will be ignored
        - *properties*, a list of column names for properties
        - *pvcol* default 'pv', the column name for pv
        - *tagscol* default 'tags', the column name for tags
        - *sep* default ';'

        The default properties will have all in 'elements' and 'pvs' tables, 
        except the pv and tags columns.

        tags are separated by ';'

        pv name can be duplicate (chained element).
        """
        conn = sqlite3.connect(fname)
        # use byte string instead of the default unicode
        conn.text_factory = str
        c = conn.cursor()
        c.execute(r"select * from pvs,elements "
                  "where pvs.elemName=elements.elemName")
        # head of columns
        allcols = [v[0] for v in c.description]
        # default using all columns
        proplist= kwargs.get('properties', allcols)
        pvcol = kwargs.get('pvcol', 'pv')
        tagscol = kwargs.get('tagscol', 'tags')
        sep = kwargs.get('sep', ';')

        icols = [i for i in range(len(c.description)) \
                 if c.description[i][0] in proplist]

        ipv = allcols.index(pvcol)
        itags = allcols.index(tagscol)
        for row in c:
            #print(row)
            pv = row[ipv]
            prpts = {}
            for i in icols:
                if i in [ipv, itags]: continue
                # NULL or '' will be ignored
                if row[i] is None or row[i] == '': continue
                prpts[allcols[i]] = row[i]
            if not row[itags]:
                tags = []
            else:
                tags = [v.strip().encode('ascii') 
                        for v in row[itags].split(sep)]
            self.rows.append([pv, prpts, tags])

        #
        c.execute("select * from elements t1 left join pvs t2 on "
                  "t1.elemName = t2.elemName where t2.elemName is NULL")
        allcols = [v[0] for v in c.description]
        # default using all columns
        proplist= kwargs.get('properties', allcols)
        icols = [i for i in range(len(c.description)) \
                 if c.description[i][0] in proplist]

        ipv = allcols.index(pvcol)
        itags = allcols.index(tagscol)
        for row in c:
            pv, prpts = "", {}
            for i in icols:
                if i in [ipv, itags]: continue
                # NULL or '' will be ignored
                if row[i] is None or row[i] == '': continue
                prpts[allcols[i]] = row[i]
            if not row[itags]:
                tags = []
            else:
                tags = [v.strip().encode('ascii') 
                        for v in row[itags].split(sep)]
            self.rows.append([pv, prpts, tags])
        
        c.close()
        conn.close()
        self.source = fname
        #print("Imported:\n", self.rows)

    def saveSqlite(self, fname):
        """
        export to sqlite table, drop if exists.
        """
        import apdata
        # create a new empty DB, then update
        apdata.createLatticePvDb(fname, None)
        apdata._updateLatticePvDb(fname, self.rows)

    def _save_csv_1(self, fname):
        """
        save the CFS in CSV format.
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

    def _save_csv_2(self, fname):
        """
        export the CFS in CSV2 format (explicit).
        """
        # find out all the property names
        with open(fname, 'w') as f:
            for r in self.rows:
                p = ",".join(["%s=%s" % (k,v) for k,v in r[1].items()])
                f.write(",".join([r[0], p, ",".join(r[2])]) + "\n")

    def _loadJson(self, fname):
        self.source = fname
        import json
        f = open(fname, 'r')
        d = json.load(f)
        self.__cdate = d['__cdate']
        self.rows = d['rows']
        f.close()

    def _saveJson(self, fname):
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

    def tags(self, pat):
        """
        return a list of tags matching the unix filename pattern *pat*.
        """
        alltags = set()
        for r in self.rows: alltags.update(r[2])
        return [t for t in alltags if fnmatch(t, pat)]

    def splitPropertyValue(self, prpt, sep = ";"):
        for r in self.rows:
            if prpt not in r[1]: continue
            r[1][prpt] = r[1][prpt].split(sep)

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

    def splitChainedElement(self, prpt, sep=";"):
        old_rows = self.rows
        self.rows = []
        for i,r in enumerate(old_rows):
            prptlst = r[1][prpt].split(sep)
            if len(prptlst) == 1:
                self.rows.append(r)
                continue
            ext = []
            for v in prptlst:
                ext.append([r[0], {prpt: v}, r[2]])
            for k,v in r[1].items():
                if k == prpt: continue
                prptlst = v.split(sep)
                if len(prptlst) == 1:
                    for ei in ext: ei[1][k] = v
                else:
                    for j,ei in enumerate(ext): ei[1][k] = prptlst[j]
            self.rows.extend(ext)
        #print("New splited:\n", self.rows)

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
    cfa._importSqliteDb1('test.sqlite')
    print(cfa.rows)
    cfa.exportSqlite("test2.sqlite")
