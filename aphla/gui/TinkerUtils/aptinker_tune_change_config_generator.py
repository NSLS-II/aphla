from __future__ import print_function, division, absolute_import

import aphla as ap
import numpy as np
import matplotlib.pylab as plt

ap.machines.load('nsls2','SR')

quad_list_str_from_aptinker = '''
ql3g6c30b
ql2g6c30b
ql1g6c30b
ql1g2c01a
ql2g2c01a
ql3g2c01a
ql3g6c02b
ql2g6c02b
ql1g6c02b
ql1g2c03a
ql2g2c03a
ql3g2c03a
ql3g6c04b
ql2g6c04b
ql1g6c04b
ql1g2c05a
ql2g2c05a
ql3g2c05a
ql3g6c06b
ql2g6c06b
ql1g6c06b
ql1g2c07a
ql2g2c07a
ql3g2c07a
ql3g6c08b
ql2g6c08b
ql1g6c08b
ql1g2c09a
ql2g2c09a
ql3g2c09a
ql3g6c10b
ql2g6c10b
ql1g6c10b
ql1g2c11a
ql2g2c11a
ql3g2c11a
ql3g6c12b
ql2g6c12b
ql1g6c12b
ql1g2c13a
ql2g2c13a
ql3g2c13a
ql3g6c14b
ql2g6c14b
ql1g6c14b
ql1g2c15a
ql2g2c15a
ql3g2c15a
ql3g6c16b
ql2g6c16b
ql1g6c16b
ql1g2c17a
ql2g2c17a
ql3g2c17a
ql3g6c18b
ql2g6c18b
ql1g6c18b
ql1g2c19a
ql2g2c19a
ql3g2c19a
ql3g6c20b
ql2g6c20b
ql1g6c20b
ql1g2c21a
ql2g2c21a
ql3g2c21a
ql3g6c22b
ql2g6c22b
ql1g6c22b
ql1g2c23a
ql2g2c23a
ql3g2c23a
ql3g6c24b
ql2g6c24b
ql1g6c24b
ql1g2c25a
ql2g2c25a
ql3g2c25a
ql3g6c26b
ql2g6c26b
ql1g6c26b
ql1g2c27a
ql2g2c27a
ql3g2c27a
ql3g6c28b
ql2g6c28b
ql1g6c28b
ql1g2c29a
ql2g2c29a
ql3g2c29a
'''

quad_names_from_aptinker = quad_list_str_from_aptinker.split()
quads_from_aptinker = [ap.getElements(name)[0] for name
                       in quad_names_from_aptinker]

quads = ap.getElements('ql*')

assert quads == quads_from_aptinker

m = np.zeros((2, len(quads)))
betas = np.zeros((len(quads), 2))
ql1_inds = []
ql2_inds = []
ql3_inds = []
for i, q in enumerate(quads):
    if q.name.startswith('ql1'):
        ql1_inds.append(i)
    elif q.name.startswith('ql2'):
        ql2_inds.append(i)
    elif q.name.startswith('ql3'):
        ql3_inds.append(i)
    else:
        raise ValueError('Unexpected quad name: {0}'.format(q.name))

    betas[i,:] = ap.getTwissAt((q.sb + q.se)/2.0, ['betax', 'betay'])
    k1l = q.get('b1', handle='golden', unitsys='phy')
    m[0,i] =  betas[i,0]/4.0/np.pi
    m[1,i] = -betas[i,1]/4.0/np.pi
m_aphla = ap.calcTuneRm(quads, unitsys='phy')

print('Matrix max abs diff = ', np.max(np.abs((m_aphla - m).flatten())))

#dnux = 0.001
#dnuy = 0.0
#filepath = 'dnux_1em3_dK_vec.txt'

dnux = 0.0
dnuy = 0.001
filepath = 'dnuy_1em3_dK_vec.txt'

dKL = np.linalg.pinv(m, rcond=1e-5).dot(np.array([dnux, dnuy]).reshape((2,1)))
print('nux diff from target:', m.dot(dKL)[0] - dnux)
print('nuy diff from target:', m.dot(dKL)[1] - dnuy)

mean_QL1_dKL = np.mean(dKL[ql1_inds,0])
mean_QL2_dKL = np.mean(dKL[ql2_inds,0])
mean_QL3_dKL = np.mean(dKL[ql3_inds,0])

print('QL1 dKL/mean(dKL) max diff [%] = ',
      np.max(np.abs(np.diff(dKL[ql1_inds,0])/mean_QL1_dKL))*100.0)
print('QL2 dKL/mean(dKL) max diff [%] = ',
      np.max(np.abs(np.diff(dKL[ql2_inds,0])/mean_QL2_dKL))*100.0)
print('QL3 dKL/mean(dKL) max diff [%] = ',
      np.max(np.abs(np.diff(dKL[ql3_inds,0])/mean_QL3_dKL))*100.0)

dKL_using_means = [0.0]*dKL.size
for ind in ql1_inds:
    dKL_using_means[ind] = mean_QL1_dKL
for ind in ql2_inds:
    dKL_using_means[ind] = mean_QL2_dKL
for ind in ql3_inds:
    dKL_using_means[ind] = mean_QL3_dKL

with open(filepath, 'w') as f:
    f.write('\n'.join(['{0:.9e}'.format(d) for d in dKL_using_means]))
