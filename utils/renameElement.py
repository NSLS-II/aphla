#!/usr/bin/env python

import os, sys, shelve, re
import hla
from cothread.catools import caget, caput
from cothread import Timedout
import numpy as np
import matplotlib.pylab as plt

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

def combineOrm(safe=True):
    pklx = '/home/lyyang/devel/nsls2-hla/machine/nsls2/ormx.pkl'
    pkly = '/home/lyyang/devel/nsls2-hla/machine/nsls2/ormy.pkl'
    pkl  = '/home/lyyang/devel/nsls2-hla/machine/nsls2/orm.pkl'
    fx = shelve.open(pklx, 'r')
    fy = shelve.open(pkly, 'r')
    f  = shelve.open(pkl, 'c')

    rawmaskx  = fx['orm._rawdata_.mask']
    rawkickx  = fx['orm._rawdata_.kicker_sp']
    rawmatrixx = fx['orm._rawdata_.matrix']
    bpm_pvrbx = fx['orm.bpm_pvrb']
    trim_pvspx = fx['orm.trim_pvsp']
    trim_pvrbx = fx['orm.trim_pvrb']
    trimx = fx['orm.trim']
    bpmx  = fx['orm.bpm']
    mx    = fx['orm.m']
    
    rawmasky  = fy['orm._rawdata_.mask']
    rawkicky  = fy['orm._rawdata_.kicker_sp']
    rawmatrixy = fy['orm._rawdata_.matrix']
    bpm_pvrby = fy['orm.bpm_pvrb']
    trim_pvspy = fy['orm.trim_pvsp']
    trim_pvrby = fy['orm.trim_pvrb']
    trimy = fy['orm.trim']
    bpmy  = fy['orm.bpm']
    my    = fy['orm.m']
    print np.shape(rawmatrixx), np.shape(rawmatrixy)

    nx1, nx2 = len(bpm_pvrbx), len(trim_pvspx)
    ny1, ny2 = len(bpm_pvrby), len(trim_pvspy)

    rawmask = np.ones((nx1+ny1, nx2+ny2))
    rawmask[:nx1,:nx2] = rawmaskx[:,:]
    rawmask[nx1:,nx2:] = rawmasky[:,:]
    f['orm._rawdata_.mask'] = rawmask

    nkx1, npx = np.shape(rawkickx)
    nky1, npy = np.shape(rawkicky)
    rawkick = np.zeros((nkx1+nky1, npx), 'd')
    rawkick[:nkx1,:] = rawkickx[:,:]
    rawkick[nkx1:,:] = rawkicky[:,:]
    f['orm._rawdata_.kicker_sp'] = rawkick
    
    rawmatrix = np.zeros((npx, nx1+ny1, nx2+ny2), 'd')
    rawmatrix[:,:nx1,:nx2] = rawmatrixx[:,:,:]
    rawmatrix[:,nx1:,nx2:] = rawmatrixy[:,:,:]
    f['orm._rawdata_.matrix'] = rawmatrix

    m = np.zeros((nx1+ny1, nx2+ny2), 'd')
    m[:nx1, :nx2] = mx[:,:]
    m[nx1:, nx2:] = my[:,:]
    f['orm.m'] = m

    residuals = np.zeros((nx1+ny1, nx2+ny2), 'd')
    for i in range(nx1+ny1):
        for j in range(nx2+ny2):
            if rawmask[i,j]: continue
            p, resi, rank, singular_values, rcond = \
                np.polyfit(rawkick[j,1:-1], rawmatrix[1:-1,i,j], 1, full=True)
            residuals[i,j] = resi
        print i,
        sys.stdout.flush()
    f['orm._rawdata_.residuals'] = residuals

    bpm = []
    for i in range(nx1):
        bpm.append((bpmx[i], 'X', bpm_pvrbx[i]))
    for i in range(ny1):
        bpm.append((bpmy[i], 'Y', bpm_pvrby[i]))
    f['orm.bpm'] = bpm

    trim = []
    for i in range(nx2):
        trim.append((trimx[i], 'X', trim_pvrbx[i], trim_pvspx[i]))
    for i in range(ny2):
        trim.append((trimy[i], 'Y', trim_pvrby[i], trim_pvspy[i]))
    f['orm.trim'] = trim

    #print type(rawmasky)
    print "#", os.environ['EPICS_CA_ADDR_LIST']
    print "#", fx.keys()
    print "#", f.keys()
    f.close()
    fx.close()
    fy.close()

def ormhist():
    pkl  = '/home/lyyang/devel/nsls2-hla/machine/nsls2/orm.pkl'
    f  = shelve.open(pkl, 'r')
    d = f['orm._rawdata_.residuals']
    msk = f['orm._rawdata_.mask']
    r = []
    n1, n2 = np.shape(d)
    print n1, n2
    for i in range(n1):
        for j in range(n2):
            if msk[i,j]: continue
            r.append(d[i,j])
        print len(r),
        sys.stdout.flush()
    print len(r)

    plt.hist(r, 50, facecolor='green', alpha=0.75)
    plt.savefig('orm-residuals.png')

    
def ormtest():
    pkl  = '/home/lyyang/devel/nsls2-hla/machine/nsls2/orm.pkl'
    orm = hla.measorm.Orm(bpm=[], trim=[])
    orm.load(pkl)
    orm.save('test.pkl')

def rename_orm_trimpv():
    pkl = '/home/lyyang/devel/nsls2-hla/machine/nsls2/orm.pkl'
    orm = hla.measorm.Orm(bpm=[], trim=[])
    orm.load(pkl)
    for i,b in enumerate(orm.trim):
        b2, b3 = b[2], b[3]
        if b[0].find('CF') == 0: b = (b[0][1:], b[1], b[2], b[3])
        if b[2].find('CM:F') > 0:
            b2 = b[2].replace('CM:F', 'FCor:F')
            b3 = b[3].replace('CM:F', 'FCor:F')
        elif b[2].find('CM:') > 0:
            b2 = b[2].replace('CM:', 'Cor:')
            b3 = b[3].replace('CM:', 'Cor:')
        #print hla._cfa.channel(b2)
        prop2 = hla._cfa.getChannelProperties(b2)
        if prop2[hla._cfa.ELEMNAME] != b[0]: print b[0], prop2[hla._cfa.ELEMNAME]
        prop3 = hla._cfa.getChannelProperties(b3)
        if prop3[hla._cfa.ELEMNAME] != b[0]: print b[0], prop3[hla._cfa.ELEMNAME]
        
        orm.trim[i] = (b[0], b[1], b2, b3)
        #print "%4d" % i, hla._cfa.channel(b2)
        #print "    ", hla._cfa.channel(b3)

        print orm.trim[i]

    orm.save('orm0.pkl')

if __name__ == "__main__":
    if len(sys.argv) == 1: safe = True
    elif sys.argv[1] == '--real': safe = False
    #renameElement()
    #renameOrmElement()
    #updateOrmPv(safe=safe)
    #combineOrm()
    #ormhist()
    #ormtest()
    rename_orm_trimpv()

