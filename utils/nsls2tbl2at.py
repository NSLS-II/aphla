#!/usr/bin/env python

"""
convert Lattice Parameter Table to AT
"""

import sys
import re

def read_partable(fname):
    f = open(fname, 'r')
    head = f.readline().split()
    unit = f.readline()
    bar = f.readline()
    beg = f.readline()

    elemlst = []
    icell, celllst = -1, [[]]
    out = []
    stot = 0.0
    for line in f.readlines():
        rec = tuple(line.split())
        name, fam, L, S1, k1, k2, ang = rec
        if fam == 'BPM': 
            # it was finite length
            out.append("%s = drift('%s', %s, 'DriftPass')" %
                       (name, name, L))
        elif fam == 'DRIF':
            out.append("%s = drift('%s', %s, 'DriftPass');" %
                       (name, name, L))
        elif fam == 'TRIMD':
            out.append("%s = corrector('%s', %s, [0 0], 'CorrectorPass');" %
                       (name, name, L))
        elif fam == 'FTRIM':
            out.append("%s = corrector('%s', %s, [0 0], 'CorrectorPass');" %
                       (name, name, L))
        elif fam == 'SQ_TRIM':
            out.append("%% Trim in SQUAD\n%s = corrector('%s', %s, [0 0], 'CorrectorPass');" %
                       (name, name, L))
        elif fam == 'MARK': 
            pass
        elif fam == 'DIPOLE':
            out.append("%s = rbend('%s', %s, 6.0*pi/180, 3.0*pi/180, "
                       "3.0*pi/180, 0.0, 'BndMPoleSymplectic4Pass');" %
                       (name, name, L))
        elif fam == 'QUAD':
            out.append("%s = quadrupole('%s', %s, %s, 'StrMPoleSymplectic4Pass');" %
                       (name, name, L, k1))
        elif fam == 'SEXT':
            out.append("%s = sextupole('%s', %s, %s, 'StrMPoleSymplectic4Pass');" %
                       (name, name, L, k2))    
        else:
            raise RuntimeError("Unknow type '%s'" % fam)

        if re.match(r'.*C[0-9][0-9][AB]', name):
            kcell = int(name[-3:-1])
            if kcell != icell and icell >= 0: 
                celllst.append([])

            icell = kcell
        if fam != 'MARK': 
            stot += float(L)
            celllst[-1].append(name)

    print "Full length", stot
    #print head
    #print rec[-1]
    f.close()
    return out, celllst

if __name__ == "__main__":
    f = open('test.m', 'w')
    elems, cells = read_partable(sys.argv[1])

    f.write("% Elements\n")
    for s in elems:
        f.write(s + '\n')

    f.write("% Girders\n")
    ring = []
    for c in cells:
        icell = -1
        for e in c:
            if re.match(r'.*C[0-9][0-9][AB]', e):
                icell = int(e[-3:-1])
                break
        else:
            raise RuntimeError("did not find cell number")

        f.write("C%d = %s\n" % (icell, str(c)))
        ring.append("C%d" % icell)

    f.write("%% Ring\nRING=%s\n" % str(ring))
    f.close()
