"""
4 correctors to create local orbit bump
"""

import aphla as ap
import numpy as np
import matplotlib.pylab as plt
import time


ap.initNSLS2V1()
ap.initNSLS2V1SRTwiss()

ap.hlalib._reset_trims()

hclist = ['cyh1g2c10a',
'cyh2g2c10a',
#'cxm1g4c10a',
#'cxm1g4c10b',
'cyl1g6c10b',
'cyl2g6c10b']

hcor = ap.getElements(hclist)
for h in hcor: print h
beta = ap.getBeta(hclist)
phi  = ap.getPhase(hclist)

for h in hcor: h.y = 0
time.sleep(6)
x0 = ap.getOrbit(spos=True)

#print type(beta), type(phi), type(x)
#dphi = (phi - phi[0,:])*(2*np.pi)

# the plane, x or y
ic = 1
theta = [5e-6, -5e-6, 0, 0]
b0, b1, b2, b3 = np.sqrt(beta[:,ic])
sp30 = np.sin((phi[3,ic] - phi[0,ic])*2*np.pi)
sp31 = np.sin((phi[3,ic] - phi[1,ic])*2*np.pi)
sp20 = np.sin((phi[2,ic] - phi[0,ic])*2*np.pi)
sp21 = np.sin((phi[2,ic] - phi[1,ic])*2*np.pi)
sp32 = np.sin((phi[3,ic] - phi[2,ic])*2*np.pi)

theta[2] = -(b0*theta[0]*sp30 + b1*theta[1]*sp31)/sp32/b2
theta[3] = (b0*theta[0]*sp20 + b1*theta[1]*sp21)/sp32/b3

print theta
for i,t in enumerate(theta):
    hcor[i].y = t
time.sleep(6)
for h in hcor: print h.name, h.y

x1 = ap.getOrbit(spos=True)

plt.plot(x0[:,-1], x0[:,1], '--')
plt.plot(x1[:,-1], x1[:,1], '-')
plt.savefig('tmp.png')

