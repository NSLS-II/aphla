"""
This is a demo of HLA interface to Fast Orbit FeedBack.

to run it on box32, in command line:

python fofb_hla_interface.py v2sr_orm.hdf5
"""

# :author: Lingyun Yang <lyyang@bnl.gov>


import sys
import h5py
import numpy as np
from cothread.catools import caput

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print "Usage: %s orm.hdf5" % sys.argv[0]
        sys.exit(0)

    # reading orm data from a full matrix.
    h5f = sys.argv[1]
    f = h5py.File(h5f, 'r')
    m = f['orm']['m']
    bpms = f['orm']['bpm']['element']
    plane = f['orm']['bpm']['plane']
    # the index for BPM x and y reading
    bpmxi = [i for i in range(len(plane)) if plane[i] == 'x']
    bpmyi = [i for i in range(len(plane)) if plane[i] == 'y']
    print "BPM x index:", bpmxi, " ... %d in total" % len(bpmxi)
    print "BPM y index:", bpmyi, " ... %d in total" % len(bpmyi)

    cors = f['orm']['trim']['element']
    plane = f['orm']['trim']['plane']
    corxi = [i for i in range(len(plane)) if plane[i] == 'x']
    coryi = [i for i in range(len(plane)) if plane[i] == 'y']

    # take only the x-x part
    # the measurement is only slow corrector
    # for interface demo purpose, just take the first 90
    #mxx = np.take(np.take(m, bpmxi, axis=0), corxi[:90], axis=1)
    #myy = np.take(np.take(m, bpmyi, axis=0), coryi[:90], axis=1)

    mxx = np.take(np.take(m, bpmxi, axis=0), corxi, axis=1)
    myy = np.take(np.take(m, bpmyi, axis=0), coryi, axis=1)

    print "ORM MXX (BPMx,hcor)", np.shape(mxx)
    print "ORM MYY (BPMy,vcor)", np.shape(myy)

    # mxx = u s v^h = Ux*diag(sx)*Vhx
    Ux, sx, Vhx = np.linalg.svd(mxx, full_matrices=False)
    #print "Shapes:", Ux.shape, sx.shape, Vhx.shape
    #Sx = np.diag(sx)
    #print np.allclose(mxx, np.dot(Ux, np.dot(Sx, Vhx)))
    xrefobt = [0.0] * 10 + [0.5]*30 + [0]*140
    try:
        caput('PV:xBPM_TargetOrbit', xrefobt) # the target 
        caput('PV:xUxMatrix', Ux.flatten()) # 180*90
        caput('PV:xsxVector', sx) # 90
        caput('PV:xVhxMatrix', Vhx.flatten()) # 90*90
        caput('PV:xBPMx_Flag', [1] * 180) # a vector of [1, 1, ..] all enabled.
        caput('PV:xCorx_Flag', [1] * 90)  # a vector of [1, 1, ..] all enabled.
        caput('PV:xNEigenValues', 40) # use 40 out of 90 eigen values in sx.
        caput('PV:xKp', [0]) # please ask yuke for a resonalbe number and size
        caput('PV:xKi', [0]) # please ask yuke for a resonalbe number and size
        caput('PV:xKd', [0]) # please ask yuke for a resonalbe number and size
        caput('PV:xSwitch', 1) # switch to use the new ORM and settings
    except:
        raise

    # the following is a repeat for y-plane
    # mxx = u s v^h = Ux*diag(sy)*Vhy
    Uy, sy, Vhy = np.linalg.svd(myy, full_matrices=False)
    #print "Shapes:", Uy.shape, sy.shape, Vhy.shape
    #Sy = np.diag(sy)
    #print np.allclose(myy, np.dot(Uy, np.dot(Sy, Vhy)))
    yrefobt = [0.0] * 10 + [0.5]*30 + [0]*140
    try:
        caput('PV:yBPM_TargetOrbit', yrefobt) # the target 
        caput('PV:yUyMatrix', Uy.flatten()) # 180*90
        caput('PV:ysyVector', sy) # 90
        caput('PV:yVhyMatrix', Vhy.flatten()) # 90*90
        caput('PV:yBPMy_Flag', [1] * 180) # a vector of [1, 1, ..] all enabled.
        caput('PV:yCory_Flag', [1] * 90)  # a vector of [1, 1, ..] all enabled.
        caput('PV:yNEigenValues', 40) # use 40 out of 90 eigen values in sy.
        caput('PV:yKp', [0]) # please ask yuke for a resonalbe number and size
        caput('PV:yKi', [0]) # please ask yuke for a resonalbe number and size
        caput('PV:yKd', [0]) # please ask yuke for a resonalbe number and size
        caput('PV:ySwitch', 1) # switch to use the new ORM and settings
    except:
        raise

