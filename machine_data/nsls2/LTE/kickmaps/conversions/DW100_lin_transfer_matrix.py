import sys, os
import numpy as np
import matplotlib.pylab as plt

import pytracy as pt
import pytracyutils.search as pts
import pytbt

sys.path.insert(0, '/home/yhidaka/hg_repos/hlsqlite')
import hlsqlite

sys.path.insert(0, '/home/yhidaka/hg_repos/numpyutil')
import numpyutil as npu

orig_filename = 'W100_DF_asbuilt_3o4m_urad.txt'

gap_mm_list = [15, 20, 30, 40, 50]
kickmap_filename_list = [orig_filename] + [
    'W100_DF_asbuilt_g{0:d}_3o4m_urad.txt'.format(gap) for gap in gap_mm_list[1:]]

#X_15mm = np.genfromtxt(
    #orig_filename, comments='#', delimiter=None,
    #skip_header=10, skip_footer=88)[:,1:]
#Y_15mm = np.genfromtxt(
    #orig_filename, comments='#', delimiter=None,
    #skip_header=54, skip_footer=43)[:,1:]
#for kickmap_filename in kickmap_filename_list[1:]:
    #X = np.genfromtxt(
        #kickmap_filename, comments='#', delimiter=None,
        #skip_header=10, skip_footer=88)[:,1:]
    #Y = np.genfromtxt(
        #kickmap_filename, comments='#', delimiter=None,
        #skip_header=54, skip_footer=43)[:,1:]

a = 3.694  # [T]
b = -5.068 # [no unit]
c = 1.52   # [no unit]
lambda0 = 0.1 # period of DW [m]
beta_avg = 4.582 # [m]
Lw = 7.0 # ID length [m]
Brho = 10.0

gaps = np.sort(gap_mm_list)[::-1]/1e3 # [m]

B_peak = a*np.exp(b*gaps/lambda0 + c*((gaps/lambda0)**2)) # Halback expression for the peak DW field [T]
dnuy = 1.0/8.0/np.pi*beta_avg*Lw*((B_peak/Brho)**2)

pt.rdmfile('../ID_integ/09_WG_20140801/CD3-Aug01-14_NoHf_1DW_C28.flat')
cell_list = pt.getCell()
dw_elem_inds = \
    pts.getElemIndexesFromName('IDC28H1') + \
    pts.getElemIndexesFromName('IDC28H2')
for ei in dw_elem_inds:
    pt.set_ID_scl(cell_list[ei].Fnum, cell_list[ei].Knum, 0.0)
pt.Ring_GetTwiss(True, 0.0)
nux0, nuy0 = pt.globval.TotalTune
for i, (g, bp) in enumerate(zip(gaps, B_peak)):

    print '### Gap {0:d} of {1:d} ({2:.0f}mm)'.format(i+1, len(B_peak), g*1e3)

    kick_frac = (bp/B_peak[-1])**2

    for ei in dw_elem_inds:
        pt.set_ID_scl(cell_list[ei].Fnum, cell_list[ei].Knum, kick_frac)
    pt.Ring_GetTwiss(True, 0.0)

    x0_6d_list = [0.0]*6
    elem_index1 = elem_index2 = pts.getElemIndexesFromName('IDC28H1')[0]
    M = pytbt.get_M_12(elem_index1, elem_index2, x0_6d_list)

    if False:
        hlsqlite.SQLiteDatabase.pprinttable(
            M, column_name_list=['x','px','y','py','dp','ct'])

    #npu.pprint2darray(M.T, str_format=':.6g', separator='|')
    npu.pprint2darray(M.T, str_format=':.6f', separator='|')


with open('../ID_integ/09_WG_20140801/CD3-Aug01-14_NoHf_1DW_C28.flat', 'r') as f:
    all_text = f.read()

for gap, kickmap_filename in zip(gap_mm_list, kickmap_filename_list):
    with open('temp.flat', 'w') as f:
        mod_text = all_text.replace(orig_filename, kickmap_filename)
        f.write(mod_text)

    pt.rdmfile('temp.flat')

    x0_6d_list = [0.0]*6
    elem_index1 = elem_index2 = pts.getElemIndexesFromName('IDC28H1')[0]
    M = pytbt.get_M_12(elem_index1, elem_index2, x0_6d_list)

    if False:
        hlsqlite.SQLiteDatabase.pprinttable(
            M, column_name_list=['x','px','y','py','dp','ct'])

    print ' '
    print 'Gap [mm] =', gap
    #npu.pprint2darray(M.T, str_format=':.6g', separator='|')
    npu.pprint2darray(M.T, str_format=':.6f', separator='|')

os.remove('temp.flat')