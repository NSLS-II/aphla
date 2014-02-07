import os
import sys
import numpy as np
import aphla as ap
import matplotlib.pylab as plt

ap.machines.load("nsls2")

fout = open("magnet_I.txt", "w")
for fam, ql, qk1 in [("QH1", 0.268, -0.641957),
                     ("QH2", 0.46,   1.43673),
                     ("QH3", 0.268, -1.75355),
                     ("QL1", 0.268, -1.61785),
                     ("QL2", 0.46,   1.76477),
                     ("QL3", 0.268, -1.51868),
                     ("QM1", 0.247, -0.812235),
                     ("QM2", 0.282, 1.22615)]:
    fname = os.path.join("magnet", fam + ".txt")
    dat = np.loadtxt(fname, skiprows=5)
    qlst = ap.getElements(fam)
    #print f, fname, np.shape(dat), len(qlst)
    rdiff = np.zeros((len(dat), 2), 'd')
    for i in range(len(dat)):
        #print i, dat[i,0],
        sys.stdout.flush()
        qb1 = [q.convertUnit("b1", dat[i,0], None, 'phy') for q in qlst]
        k1l = [qb1[j]/(dat[i,1]*dat[i,2]) - 1.0 for j in range(len(qlst)) 
                if qb1[j] is not None]
        #print min(k1l), max(k1l), len(qb1) - len(k1l) 
        rdiff[i,:] = (min(k1l), max(k1l))
    I0 = np.interp(np.abs(qk1), np.abs(dat[:,2]), np.abs(dat[:,0]))

    I = [q.convertUnit("b1", qk1*ql, 'phy', None)/I0 - 1.0 for q in qlst]
    print "Summary:", fam, min(rdiff[2:,0]), max(rdiff[2:,1]),
    print "K1L=%.3f" % (qk1*ql,), I0, min(I), max(I)
    if np.abs(min(I)) > 0.005 or np.abs(max(I)) > 0.005:
        plt.clf()
        plt.plot(I)
        plt.xticks(range(len(qlst)), [q.name for q in qlst], rotation=90)
        plt.savefig("tmp_warn_%s.png" % fam)
    for q in qlst:
        fout.write("%s %.5f % 9.5f %10.5f\n" % (
            q.name, ql, qk1, q.convertUnit("b1", qk1*ql, 'phy', None)))


for fam, ql, qk1 in [("SH1", 0.2, 19.8329),
                     ("SH3", 0.2, -5.85511),
                     ("SH4", 0.2, -15.8209),
                     ("sm1*a", 0.2, -23.6806),
                     ("SM2",  0.25, 28.6432),
                     ("sm1*b", 0.2, -25.946),
                     ("SL3", 0.2,-29.4609),
                     ("SL2", 0.2, 35.6779),
                     ("SL1", 0.2, -13.2716)]:
    fname = os.path.join("magnet", fam[:3].upper() + ".txt")
    dat = np.loadtxt(fname, skiprows=5)
    qlst = ap.getElements(fam)
    if len(qlst) == 0:
        raise RuntimeError("not found elements '{0}'".format(fam))

    #print f, fname, np.shape(dat), len(qlst)
    rdiff = np.zeros((len(dat), 2), 'd')
    for i in range(len(dat)):
        #print i, dat[i,0],
        sys.stdout.flush()
        qb1 = [q.convertUnit("b2", dat[i,0], None, 'phy') for q in qlst]
        k1l = [qb1[j]/(dat[i,1]*dat[i,2]) - 1.0 for j in range(len(qlst)) 
                if qb1[j] is not None]
        #print "I= %.3f" % dat[i,0], qb1
        #print "I= %.3f" % dat[i,0], k1l
        #print min(k1l), max(k1l), len(qb1) - len(k1l) 
        if len(k1l) == 0: continue
        rdiff[i,:] = (min(k1l), max(k1l))
    I0 = np.interp(np.abs(qk1), np.abs(dat[:,2]), np.abs(dat[:,0]))

    I = [q.convertUnit("b2", qk1*ql, 'phy', None)/I0 - 1.0 for q in qlst]
    print "Summary:", fam, min(rdiff[2:,0]), max(rdiff[2:,1]),
    print "K1L=%.3f" % (qk1*ql,), I0, min(I), max(I)
    if np.abs(min(I)) > 0.005 or np.abs(max(I)) > 0.005:
        plt.clf()
        plt.plot(I)
        plt.xticks(range(len(qlst)), [q.name for q in qlst], rotation=90)
        plt.savefig("tmp_warn_%s.png" % fam)
    for q in qlst:
        fout.write("%s %.5f % 9.5f %10.5f\n" % (
            q.name, ql, qk1, q.convertUnit("b2", qk1*ql, 'phy', None)))

fout.close()

