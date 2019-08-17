#!/usr/bin/env python
from __future__ import print_function, division, absolute_import

import sys, re

def readTwiss(f):
    head       = []
    table_data = []
    for line in open(f, 'r').readlines():
        if line.startswith('@'):
            head.append(tuple(line.split()[1:]))
        elif line.startswith('*'):
            table_head = tuple(line.split()[1:])
        elif line.startswith('$'):
            table_format = tuple(line.split()[1:])
        else:
            data = line.split()
            if len(data) != len(table_head):
                print("ERROR: data columns != table head (%d != %d)" %  \
                    (len(data), len(table_head)))
            else:
                table_data.append(data)

    return {'head': head, 'table': {
            'head': table_head, 'format': table_format,
            'data': table_data}}

def countElements(head, dat):
    i = head.index('NAME')
    ct = {}
    for d in dat:
        elem = d[i]
        v = ct.setdefault(elem, 0)
        ct[elem] += 1

    #print "# %d lines, %d elements" % (len(dat), len(ct))
    #for k,v in ct.items():
    #    if v > 1: print k, v
    return ct

def findElementProperties(name, twiss):
    i = twiss['head'].index('NAME')
    for k,d in enumerate(twiss['data']):
        if d[i].replace('"', "") == name: break
    else:
        return ""

    rec = {'ordinal': str(k), 'system': 'SR',
           'devName': None, 'elemType': None, 'handle': None, 'length': None,
           'sEnd': None}
    if 'KEYWORD' in twiss['head']:
        j = twiss['head'].index('KEYWORD')
        rec.update([('elemType', d[j].replace('"', ''))])
    if 'S' in twiss['head']:
        j = twiss['head'].index('S')
        rec.update([('sEnd', d[j])])

    s = ''
    for k, v in rec.items():
        if v is None: continue
        s += ", %s= %s" % (k, v)
    return s


def readPvName(f, twiss = None):
    newblock = True
    for line in open(f, 'r').readlines():
        if not line.strip():
            # the empty line
            newblock = True
            continue
        if newblock:
            # the comment line
            print("##", line.strip())
            newblock = False
            continue

        t = line.split(',')
        rec = {'pv': t[0].replace("'", "").strip(),
               'elemName': t[2].strip()}
        if t[1].find('setpoint') >= 0:
            rec['handle'] = 'SETPOINT'
        elif t[1].find('readback') >=0:
            rec['handle'] = 'READBACK'

        print("%(pv)s, elemName=%(elemName)s, handle=%(handle)s" % rec,)

        if twiss is not None:
            print(findElementProperties(rec['elemName'], twiss))
        else:
            print("")

if __name__ == "__main__":
    d = readTwiss(sys.argv[1])
    #print d['head']
    #print len(d['table']['data'])

    countElements(d['table']['head'], d['table']['data'])

    readPvName(sys.argv[2], d['table'])
