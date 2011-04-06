#!/usr/bin/env python

import os, sys, shelve, re
import hla
from cothread.catools import caget, caput
from cothread import Timedout

def renameHlaElement():
    lat = hla.lattice.Lattice()
    pkl = '/home/lyyang/devel/nsls2-hla/machine/nsls2/hla.pkl'
    f = shelve.open(pkl, 'w', writeback=True)
    print f.keys()
    mode = 'virtac'
    for elem in f['lat.'+mode+'.element']:
        if elem.name.find('CF') == 0:
            print "%s -> %s" % (elem.name, elem.name[1:])
            elem.name = elem.name[1:]
    for g,v in f['lat.'+mode+'.group'].items():
        for i,elem in enumerate(v):
            if elem.find('X') == 0 or elem.find('Y') == 0: 
                f['lat.'+mode+'.group'][g][i] = 'F' + elem
                print g, elem, f['lat.'+mode+'.group'][g][i]
        #print ""

    f.close()

def renameOrmElement():
    """rename CF(X|Y) F(X|Y)"""
    #orm = hla.measorm.Orm([], [])
    pkl = '/home/lyyang/devel/nsls2-hla/machine/nsls2/ormx.pkl'
    f = shelve.open(pkl, 'w', writeback=True)
    print f.keys()
    for i,elem in enumerate(f['orm.trim']):
        if elem.find('CF') == 0:
            print "%s -> %s" % (elem, elem[1:])
            f['orm.trim'][i] = elem[1:]

    f.close()

def updateOrmPv_old():
    # load channel finder
    cfa = hla.chanfinder.ChannelFinderAgent()
    cfa.load('/home/lyyang/devel/nsls2-hla/machine/nsls2/chanfinder.pkl')
    pvs = cfa.getChannels()
    print "total channels", len(pvs), pvs[0], pvs[-1]
    # orm data
    pkl = '/home/lyyang/devel/nsls2-hla/machine/nsls2/ormx.pkl'
    f = shelve.open(pkl, 'w', writeback=True)
    print os.environ['EPICS_CA_ADDR_LIST']
    print f.keys()
    pvset='orm.trim_pvsp'
    pvset='orm.bpm_pvrb'
    for i,elem in enumerate(f[pvset]):
        rb = 1e205
        try:
            rb = caget(elem.encode('ascii'), timeout=1)
        except Timedout:
            imin, vmin = -1, 2*len(pvs)
            for j,p in enumerate(pvs):
                ld = hla.levenshtein_distance(elem, p)
                if ld < vmin:
                    imin = j
                    vmin = ld
            print "change \"%s\"\n    to \"%s\"  [diff=%d]" %( elem, pvs[imin], vmin)
            f[pvset][i] = pvs[imin]
            #return True
            #print rb
    f.close()
    
def updateOrmPv(safe=True):
    # load channel finder
    cfa = hla.chanfinder.ChannelFinderAgent()
    cfa.load('/home/lyyang/devel/nsls2-hla/machine/nsls2/chanfinder.pkl')
    pvs = cfa.getChannels()
    print "total channels", len(pvs), pvs[0], pvs[-1]
    # orm data
    #pkl = '/home/lyyang/devel/nsls2-hla/machine/nsls2/ormx.pkl'
    pkl = '/home/lyyang/devel/nsls2-hla/machine/nsls2/ormy.pkl'
    f = shelve.open(pkl, 'w', writeback=True)
    print "#", os.environ['EPICS_CA_ADDR_LIST']
    print "#", f.keys()
    #pvset, pattern, repl='orm.trim_pvsp', 
    # bpm
    #pvset, pattern, repl='orm.bpm_pvrb', r'(SR.+)BBA:(.)', r'\1SA:\2-I'
    pvset, pattern, repl='orm.bpm_pvrb', r'(SR.+)<(.+)>Pos-(.)', r'\1{\2}SA:\3-I'    
    # trim
    #pvset, pattern, repl='orm.trim_pvrb', r'(SR.+)<(.+)>Fld-RB', r'\1{\2}Fld-I'    
    #pvset, pattern, repl='orm.trim_pvsp', r'(SR.+)<(.+)>Fld-SP', r'\1{\2}Fld-SP'    
    print "#", cfa.getElementChannel('FXH2G1C30A', unique=False)
    print "#", cfa.getElementChannel('PH1G2C30A', unique=False)
    print "#", f[pvset][0]
    cnt = 0
    for i,pv in enumerate(f[pvset]):
        if re.match(pattern, pv):
            pv_new = re.sub(pattern, repl, f[pvset][i])
            try:
                caget(pv_new.encode('ascii'))
                print "change \"%s\"\n    to \"%s\"" %(pv, pv_new)
                if not safe: 
                    f[pvset][i] = pv_new
                    cnt = cnt + 1
            except Timedout:
                pass
            #f[pvset][i] = pvs[imin]
            #break
    if True:
        #print testing existance
        print "# trim_pvrb"
        for i,pv in enumerate(f['orm.trim_pvrb']):
            try: caget(pv.encode('ascii'), timeout=1)
            except Timedout:
                print pv, "is not found"
        print "# trim_pvsp"
        for i,pv in enumerate(f['orm.trim_pvsp']):
            try: caget(pv.encode('ascii'), timeout=1)
            except Timedout:
                print pv, "is not found"
        print "# bpm_pvrb"
        for i,pv in enumerate(f['orm.bpm_pvrb']):
            try: caget(pv.encode('ascii'), timeout=1)
            except Timedout:
                print pv, "is not found"

    f.close()
    print "replaced: ", cnt

if __name__ == "__main__":
    if len(sys.argv) == 1: safe = True
    elif sys.argv[1] == '--real': safe = False
    #renameElement()
    #renameOrmElement()
    updateOrmPv(safe=safe)
