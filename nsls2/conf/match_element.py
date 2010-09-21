#!/usr/bin/env python

cstr = {'@BpmX': ['BPM'], '@BpmY':['BPM'], 
        '@CorrectorX': ['TRIMX', 'TRIMD'], '@CorrectorY': ['TRIMY', 'TRIMD'],
        '@Dipole': ['DIPOLE'], '@Quadrupole': ['QUAD'], '@Sextupole': ['SEXT']}

r1 = open('lattice_channels.txt', 'r').readlines()
r2 = open('mv15-c5-v2-ring-forCntr-par.txt', 'r').readlines()

ignore_lines = 3
tplst = [ x.split(',')[1].strip()  for x in r2[ignore_lines:]]
namelst = [x.split(',')[0].strip() for x in r2[ignore_lines:]]
lenlst = [x.split(',')[2].strip() for x in r2[ignore_lines:]]

iele = 0
for r in r1:
    tp = r.split()[4]
    s = r.split()[5]
    ican = [0]*len(cstr[tp])
    imin = len(r2)
    for i,k in enumerate(cstr[tp]):
        if not k in tplst[iele:]: continue
        ican[i] = iele + tplst[iele:].index(k)
        if ican[i] < imin: imin = ican[i]
    # since BPMX and BPMY are combined in Weiming's lattice, iele =i, otherwise, iele=i+1
    i, iele = imin, imin
    print r.split()[0], tp, s, namelst[i], tplst[i], lenlst[i], r2[ignore_lines+i].split(',')[3], imin

#print tplst
