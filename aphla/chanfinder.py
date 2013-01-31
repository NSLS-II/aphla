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

        :Example:

            >>> sort('pv')
            >>> sort('elemName')
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
        n = 0
        for r in self.rows:
            if oldkey not in r[1]: continue
            r[1][newkey] = r[1].pop(oldkey)
            n += 1
        #print("Renamed %s records" % n)

    
    def importCsv(self, fname):
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
            self._import_csv_1(fname)
        else:
            self._import_csv_2(fname)
        self.source = fname

    def _import_csv_1(self, fname):
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

    def _import_csv_2(self, fname):
        """
        import data from CSV (comma separated values). 

        each line of csv starts with pv name, then property list and tags. An
        example is in the following::

          PV1, elemName=Name, elemPosition=0.2, aphla.sys.SR,aphla.elemfield.f1
        """
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


    def _importSqliteDb1(self, fname, **kwargs):
        """
        import from sqlite database (v1 with two tables)
        
        :param fname: sqlite db file name
        
        - NULL/None or '' will be ignored
        - *properties*, a list of column names for properties
        - *pvcol* default 'pv', the column name for pv
        - *tagscol* default 'tags', the column name for tags
        - *tagsep* default ';'

        The default properties will have all in 'elements' and 'pvs' tables, 
        except the pv and tags columns.

        tags are separated by ';'
        """
        conn = sqlite3.connect(fname)
        c = conn.cursor()
        c.execute('''select * from pvs,elements where pvs.elem_id=elements.elem_id''')
        # head of columns
        allcols = [v[0] for v in c.description]
        # default using all columns
        proplist= kwargs.get('properties', allcols)
        pvcol = kwargs.get('pvcol', 'pv')
        tagscol = kwargs.get('tagscol', 'tags')
        tagsep = kwargs.get('tagsep', ';')

        icols = [i for i in range(len(c.description)) \
                 if c.description[i][0] in proplist]

        ipv = allcols.index(pvcol)
        itags = allcols.index(tagscol)
        for row in c:
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
                tags = [v.strip() for v in row[itags].split(tagsep)]
            self.rows.append([pv, prpts, tags])

        c.close()
        conn.close()
        self.source = fname

    def importSqlite(self, fname, **kwargs):
        """
        import from sqlite database table 'channels'
        
        :param fname: sqlite db file name
        
        - NULL/None or '' will be ignored
        - *properties*, a list of column names for properties
        - *pvcol* default 'pv', the column name for pv
        - *tagscol* default 'tags', the column name for tags
        - *tagsep* default ';'

        The default properties will have all in 'elements' and 'pvs' tables, 
        except the pv and tags columns.

        tags are separated by ';'
        """
        conn = sqlite3.connect(fname)
        c = conn.cursor()
        c.execute('''select * from channels''')
        # head of columns
        allcols = [v[0] for v in c.description]
        # default using all columns
        proplist= kwargs.get('properties', allcols)
        pvcol = kwargs.get('pvcol', 'pv')
        tagscol = kwargs.get('tagscol', 'tags')
        tagsep = kwargs.get('tagsep', ';')

        icols = [i for i in range(len(c.description)) \
                 if c.description[i][0] in proplist]

        ipv = allcols.index(pvcol)
        itags = allcols.index(tagscol)
        for row in c:
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
                tags = [v.strip() for v in row[itags].split(tagsep)]
            self.rows.append([pv, prpts, tags])

        c.close()
        conn.close()
        self.source = fname

    def exportSqlite(self, fname, tbl = "channels"):
        """
        export to sqlite table, drop if exists.
        """
        prpts, tags = set(), set()
        for r in self.rows:
            prpts.update(r[1].keys())
            tags.update(r[2])
        conn = sqlite3.connect(fname)
        prpts = sorted(prpts)
        prpts.insert(0, "pv")
        prpts.append("tags")
        c = conn.cursor()
        c.execute("drop table if exists " + tbl)
        c.execute("create table " + tbl + "(" + ','.join(prpts) + ")")
        for r in self.rows:
            pv = r[0]
            k,v0 = zip(*(r[1].items()))
            v = [r[0]] + list(v0) + [",".join(r[2])]
            query = "insert into " + tbl + "(pv," + ",".join(k) +  \
                    ", tags) values (" + ",".join(["?"] * (len(k)+2)) + ")"
            c.execute(query, v)
            
        conn.commit()

    def _export_csv_1(self, fname):
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

    def _export_csv_2(self, fname):
        """
        export the CFS in CSV2 format (explicit).
        """
        # find out all the property names
        with open(fname, 'w') as f:
            for r in self.rows:
                p = ",".join(["%s=%s" % (k,v) for k,v in r[1].items()])
                f.write(",".join([r[0], p, ",".join(r[2])]) + "\n")

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

     
