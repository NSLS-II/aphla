#!/usr/bin/env python

import sys, time, os
sys.path.append('../src')

import numpy as np
import matplotlib.pylab as plt
import hla
from hla import caget, caput

def compare(o1, o2):
    print o1
    print o2
    npoint, nbpm, ntrim = np.shape(o1._rawmatrix)
    print "checking bpm"
    for i in range(nbpm):
        # bpm name
        if o1.bpm[i][0] != o2.bpm[i][0] or \
                o1.bpm[i][1] != o2.bpm[i][1] or \
                o1.bpm[i][2] != o2.bpm[i][2]:
            print i, o1.bpm[i], o2.bpm[i]

    print "checking trim"
    for i in range(ntrim):
        # bpm name
        if o1.trim[i][0] != o2.trim[i][0] or \
           o1.trim[i][1] != o2.trim[i][1] or \
           o1.trim[i][2] != o2.trim[i][2]:
            print i, o1.trim[i], o2.trim[i]

    print "checking m"
    ndiff = 0
    for i in range(nbpm):
        #if ndiff > 20: break
        for j in range(ntrim):
            if o1._mask[i,j] and o2._mask[i,j]: continue
            if o1.bpm[i][1] != o1.trim[j][1]: continue
            if o1._mask[i,j] or o2._mask[i,j]:
                print "skip", i,j,o1.bpm[i][0], o1.trim[j][0]
                continue
            if abs(o1.m[i,j]) < 5e-3: continue
            if o2._mask[i,j]: continue
            if abs((o1.m[i,j] - o2.m[i,j])/o2.m[i,j]) > .05:
                print i, j, o1.bpm[i][0], o1.trim[j][0], \
                    o1.m[i,j], o2.m[i,j]
                plt.clf()
                plt.plot(o1._rawkick[j,1:-1], o1._rawmatrix[1:-1,i,j], '-o')
                plt.plot(o2._rawkick[j,1:-1], o2._rawmatrix[1:-1,i,j], '-x')
                plt.title("%s/%s (%s/%s) %.2e %.2e" % (
                        o1.bpm[i][0], o1.trim[j][0], o1.bpm[i][1],
                        o1.trim[j][1], o1.m[i,j], o2.m[i,j]))
                plt.savefig('orm-compare-t%04d-b%04d.png' % (j,i))
                ndiff = ndiff + 1
def filter_orm(f):
    orm = hla.measorm.Orm([], [])
    orm.load(f)
    orm.checkLinearity()

def merge_orm(f1, f2):
    orm1 = hla.measorm.Orm([], [])
    orm2 = hla.measorm.Orm([], [])
    orm1.load(f1)
    orm2.load(f2)
    compare(orm1, orm2)
    #orm1.update(orm2)
    #orm1.save("orm.pkl")

def mask_orm(f, sk):
    orm = hla.measorm.Orm([], [])
    orm.load(f)
    for j in sk: orm._mask[:,j] = 1
    orm.save(f)

def test_orbit(f):
    orm2 = hla.measorm.Orm([], [])
    if not os.path.exists(f): return True
    orm2.load(f)
    print orm2
    print "delay: ", orm2.TSLEEP

    npoint, nbpm, ntrim = np.shape(orm2._rawmatrix)

    for i in range(5):
        #itrim = np.random.randint(ntrim)
        itrim = 0
        while True:
            ibpm = np.random.randint(nbpm)
            if orm2.trim[itrim][1] == orm2.bpm[ibpm][1]: break
        #print hla.getOrbit()
        bpmrb = orm2.bpm[ibpm][2]
        trimsp = orm2.trim[itrim][3]
        x0 = caget(bpmrb)
        k = caget(trimsp)
        dk = 1e-4
        caput(trimsp, k + dk)
        time.sleep(orm2.TSLEEP)
        dx = orm2.m[ibpm,itrim]*dk
        x1 = caget(bpmrb)
        print trimsp, "% .2e" % k, bpmrb, \
            "% .4e % .4e % .4e % .4e" % (x0, x1, x1-x0, dx)
        caput(trimsp, k)
        time.sleep(orm2.TSLEEP)

        plt.clf()
        plt.plot(orm2._rawkick[itrim, 1:-1], orm2._rawmatrix[1:-1,ibpm,itrim],
                 '-o')
        plt.plot([k, k+dk], [x0, x1], '-x')
        plt.grid(True)
        plt.title("%s.%s/%s.%s" % (orm2.bpm[ibpm][0], orm2.bpm[ibpm][1],
                                   orm2.trim[itrim][0], orm2.trim[itrim][1]))
        plt.savefig('orm-test-%03d.png' % i)

    return True

    plt.clf()
    plt.plot(ratio, '-o')
    plt.ylabel("[(x1-x0)-dx]/x0")
    plt.savefig("orm-orbit-reproduce-1.png")

    plt.clf()
    plt.plot(x0, '--', label='orbit 0')
    plt.plot(x1, '-', label='orbit 1')
    plt.plot(x0+dx, 'x', label='ORM predict')

    plt.ylabel("orbit")
    plt.savefig("orm-orbit-reproduce-2.png")

    for i in range(len(bpm)):
        if x0[i]+dx[i] - x1[i] > 1e-4:
            print "Not agree well:", i,bpm[i], x0[i]+dx[i], x1[i]
    print "Done", time.time()

def update_orm(f):
    orm = hla.measorm.Orm([], [])
    if not os.path.exists(f): return True
    orm.load(f)

    npoint, nbpm, ntrim = np.shape(orm._rawmatrix)
    bpm = list(set([b[0] for i,b in enumerate(orm.bpm)]))
    #orm.measure_update(bpm=bpm, trim = ['CXHG2C30A', 'CXHG2C06A', 'CXHG2C10A', 'CXL1G6C12B', 'CXHG2C14A', 'CXHG2C18A', 'CXHG2C20A', 'CXHG2C22A', 'CXHG2C24A', 'CXHG2C26A', 'FYL1G1C21A'], verbose=1)
    orm.checkLinearity(verbose=1)
    #orm.save("orm-full-update.pkl")
    
def correct_orbit(f):
    orm = hla.orm.Orm([], [])
    if not os.path.exists(f): return True
    orm.load(f)
    hla.reset_trims()
    time.sleep(5)
    npoint, nbpm, ntrim = np.shape(orm._rawmatrix)
    bpm = []
    for c in range(10):
        cc = "C%02d" % c
        b = hla.getGroupMembers(['*', 'BPMX', cc], op='intersection')
        print cc,b
        bpm.extend(b)
    print len(bpm), bpm
    ntrim_used = ntrim
    m = np.zeros((len(bpm), ntrim_used), 'd')
    sel = [0] * nbpm
    bpmpv = []
    bpmfullpv = [b[2] for i,b in enumerate(orm.bpm)]
    for i,b in enumerate(orm.bpm):
        if not b[0] in bpm: continue
        sel[i] = 1
        bpmpv.append(b[2])
    v0 = np.array(hla.caget(bpmfullpv))
    v = np.array(hla.caget(bpmpv))
    plt.clf()
    plt.plot(v0, 'r-')
    plt.plot(v, 'ro')
    plt.savefig("orbit-00.png")
    m = np.compress(sel, orm.m[:,:ntrim_used], axis=0)
    print np.shape(m)
    #u,s,vh = np.linalg.svd(m)
    #print u, s, vh
    dk, resids, rank, s = np.linalg.lstsq(m, -1.0*v)
    print dk
    trimpv = [t[3] for i,t in enumerate(orm.trim)]
    print [t[0] for i,t in enumerate(orm.trim)]
    
    hla.caput(trimpv[:ntrim_used], dk)
    for i in range(1,10):
        time.sleep(2)
        plt.clf()
        v1 =  np.array(hla.caget(bpmfullpv))
        plt.plot(v1, '-o')
        plt.savefig("orbit-%02d.png" % i)
        
        

if __name__ == "__main__":
    #filter_orm('../test/dat/orm-full-0179.pkl')
    #filter_orm('../test/dat/orm-full-0181.pkl')
    #filter_orm('../test/dat/orm-full.pkl')
    #filter_orm('../test/dat/orm-sub1.pkl')
    #mask_orm('../test/dat/orm-full-0179.pkl', [52, 90, 141, 226, 317, 413])
    #merge_orm('../test/dat/orm-full-0179.pkl',
    #          '../test/dat/orm-full-0181.pkl')
    #merge_orm('../test/dat/orm-full-0181.pkl', 'orm.pkl')
    #test_orbit('../test/dat/orm-full-0181.pkl')
    #update_orm('../test/dat/orm-full-0184.pkl')
    #update_orm('orm-full-update.pkl')
    correct_orbit('orm-full-update.pkl')
