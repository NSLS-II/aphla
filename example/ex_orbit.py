import aphla as ap
import numpy as np
import matplotlib.pylab as plt
import time

print ap.__path__ 
ap.initNSLS2V1()
bpms = ap.getElements('BPM')
#trims = ap.getGroupMembers(['*', '[HV]COR'], op='intersection')
trims = ap.getElements('HCOR')[:30] + ap.getElements('VCOR')[-30:]
print "Bpms x Trims: (%d, %d)" % (len(bpms), len(trims) )

v0 = ap.getOrbit(spos=True)
k0 = []
for tr in trims:
    #print tr
    if u'x' in tr.fields(): k0.append([tr.sb, tr.x])
    if u'y' in tr.fields(): k0.append([tr.sb, tr.y])

n1, n2 = 10, 20
ap.correctOrbit([e.name for e in bpms[n1:n2]], [e.name for e in trims],
                scale=0.7, repeat=3) 
#ap.correctOrbit(scale=0.7, repeat=9)
#Euclidian norm: ...
time.sleep(4)
v1 = ap.getOrbit(spos=True)
time.sleep(4)
v2 = ap.getOrbit(spos=True)
k1 = []
for tr in trims:
    #print tr
    if u'x' in tr.fields(): k1.append([tr.sb, tr.x])
    if u'y' in tr.fields(): k1.append([tr.sb, tr.y])


# plotting
plt.clf()
fig = plt.figure(1, figsize=(12,9))
ax = fig.add_subplot(311)
ax.annotate("H orbit before/after correction", (0.03, 0.9),
            xycoords='axes fraction')
ax.plot(v0[:,-1], v0[:,0], 'r-')
ax.plot(v1[:,-1], v1[:,0], 'g--')
ax.plot(v2[n1:n2,-1], v2[n1:n2,0], 'g-o')
#ax.legend()
ax = fig.add_subplot(312)
ax.annotate("V orbit before/after correction", (0.03, 0.9), 
            xycoords='axes fraction')
ax.plot(v0[:,-1], v0[:,1], 'r-', label='Y')
ax.plot(v1[:,-1], v1[:,1], 'g--', label='Y')
ax.plot(v2[n1:n2,-1], v2[n1:n2,1], 'g-o')
ax = fig.add_subplot(313)
k0, k1 = np.array(k0), np.array(k1)
ax.plot(k0[:,0], k0[:,1], 'r--v')
ax.plot(k1[:,0], k1[:,1], 'g-o')
plt.savefig("hla_tut_orbit_correct.png") 
