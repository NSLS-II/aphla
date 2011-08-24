#!/usr/bin/env python

import sys, time

def read_txt(f):
    rec = []
    for i,line in enumerate(open(f, 'r').readlines()):
        s = line.strip()
        if not s or s[0] == '#' or s.find('{') < 0:
            rec.append(s)
            continue

        rawpv, rawprpt, rawtag = line.split(';')
        #print rawpv
        pv = rawpv.strip()
        
        prpts = {}
        for p in rawprpt.split(','):
            if not p.strip() or p.find('=') < 0:
                continue
            k,v = p.split('=')
            prpts[k.strip()] = v.strip()

        tags = []
        for t in rawtag.split(','):
            if not t.strip():
                continue
            tags.append(t.strip())

        #print pv, prpts
        rec.append((pv, prpts, tags))
        #print rec[-1]

    return rec

def update_rec(rec, pv, prpts, tags, debug = 0):
    """
    """
    for i,r in enumerate(rec):
        if isinstance(r, str): continue
        #print r[0],
        if r[0] != pv: continue

        # updating
        prptnew, tagnew = r[1], r[2]
        prptnew.update(prpts)

        for t in tags:
            if t in tagnew: continue
            tagnew.append(t)
        rec[i] = (pv, prptnew, tagnew)
        if debug: print "updating [%d] %s" % (i, pv), rec[i][2]
        return i
    print "Appending ", pv
    rec.append((pv, prpts, tags))
    return len(rec) - 1
    
def compress_rec(rec):
    """
    remove the duplicate pv record
    """
    ct = {}
    for i,r in enumerate(rec):
        if isinstance(r, str): continue
        pv, prpts, tags = r
        if ct.has_key(pv):
            print "duplicate @ line %d: %s" %(i, pv)
        
            j = ct[pv]
            prptsdst, tagsdst = rec[j][1], rec[j][2]
            prptsdst.update(prpts)
            for t in tags:
                if t in tagsdst: continue
                tagsdst.append(t)
            rec[j] = (pv, prptsdst, sorted(tagsdst))
            rec[i] = ''
        else:
            ct[pv] = i
    return rec


if __name__ == "__main__":
    print "%s dst src" % (sys.argv[0],)
    dst = compress_rec(read_txt(sys.argv[1]))
    print "Read %d records in destination" % (len(dst),)
    src = compress_rec(read_txt(sys.argv[2]))
    print "Read %d records" % (len(src), )
    for i,r in enumerate(src):
        if isinstance(r, str): continue
        pv, prpts, tags = r
        iret = update_rec(dst, pv, prpts, tags, debug=1)
        #print "new tags:", dst[iret][2]
    print "New records: ", len(dst)
    
    # writing the results
    if len(sys.argv) == 4:
        f = open(sys.argv[3], 'w')
    else:
        f = open('results.txt', 'w')

    for i,r in enumerate(dst):
        if isinstance(r, str):
            f.write("%s\n" % r)
            continue
        pv, prpts, tags = r
        s = "%s;" % pv
        for k in sorted(prpts.keys()):
            s += " %s = %s," % (k, prpts[k])
        if s[-1] == ',': s = s[:-1] + ';'
        if len(tags) >= 1:
            s += ' %s' % tags[0]
        if len(tags) > 1:
            for t in tags[1:]:
                s += ', %s' % t
        s += '\n'
        f.write(s)
    # 
    f.write("# updated: %s" % \
                time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime()))
    f.write(', %s' % sys.argv[1])
    for s in sys.argv[2:]:
        f.write(' %s' % s)
    f.write('\n')
    f.close()


