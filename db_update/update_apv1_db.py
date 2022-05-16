import os, sys
import numpy as np
import h5py
import pickle
import matplotlib.pylab as plt
from matplotlib.backends.backend_pdf import PdfPages
import pprint
import shutil

from cothread.catools import caget

try:
    import pytracy as pt
    import pytracyutils.search as pts
except:
    print('WARNING: PyTracy NOT available')

ORIG_APHLA_CONFIG_DIR = '/epics/aphla/apconf'

if False:
    TEMP_APHLA_CONFIG_DIR = os.path.abspath('./nsls2')
    os.environ['APHLA_CONFIG_DIR'] = TEMP_APHLA_CONFIG_DIR
else:
    TEMP_APHLA_CONFIG_DIR = ORIG_APHLA_CONFIG_DIR
    os.environ['APHLA_CONFIG_DIR'] = ORIG_APHLA_CONFIG_DIR

import aphla as ap

ap.machines.load('nsls2', 'SR')

# For `ap.machines.load('nsls2', 'SR')` to run, you only need
#     nsls2/aphla.ini
#     nsls2/sr_unitconv.hdf5
#     nsls2/sr.hdf5
#     nsls2/nsls2_sr.sqlite
#
# For `ap.machines.loadfast('nsls2', 'SR')` to run, you need additionally
#     nsls2/nsls2_LN.sqlite
#     nsls2/nsls2_LTD1.sqlite
#     nsls2/nsls2_LTD2.sqlite
#     nsls2/ltb_unitconv.ini
#     nsls2/nsls2_BR.sqlite
#     nsls2/br_unitconv.hdf5
#     nsls2/bts_unitconv.hdf5
#     nsls2/nsls2_bts.sqlite

DBFILE = os.path.join(TEMP_APHLA_CONFIG_DIR, 'nsls2', 'nsls2_sr.sqlite')

UNITCONV_FILE = os.path.join(TEMP_APHLA_CONFIG_DIR, 'nsls2', 'sr_unitconv.hdf5')

SR_CIRCUMF = ap.machines.getLattice('SR').se # [m]

BPM_PV_REC = [
    ("Pos:X-I", "x0", "get"),
    ("Pos:Y-I", "y0", "get"),
    ("Pos:XwUsrOff-Calc", "x", "get"),
    ("Pos:YwUsrOff-Calc", "y", "get"),
    ("Pos:UsrXoffset-SP", "xref2", "put"),
    ("Pos:UsrYoffset-SP", "yref2", "put"),
    ("Pos:Href-SP", "xref1", "put"),
    ("Pos:Vref-SP", "yref1", "put"),
    ("Ampl:SSA-Calc", "ampl", "get"),
    ("TBT-X", "xtbt", "get"),
    ("TBT-Y", "ytbt", "get"),
    ("TBT-S", "Itbt", "get"),
    ("FA-X", "xfa", "get"),
    ("FA-Y", "yfa", "get"),
    ("FA-S", "Ifa", "get"),
    ("BbaXOff-SP", "xbba", "put"),
    ("BbaYOff-SP", "ybba", "put"),
]

#----------------------------------------------------------------------
def put_h5py_attr(grp_dst, k, v):
    """
    """

    if isinstance(v, str):
        grp_dst.attrs[k] = v.encode('utf-8')
    else:
        try:
            grp_dst.attrs[k] = v
        except TypeError:
            grp_dst.attrs[k] = v.astype('S')

#----------------------------------------------------------------------
def _play_around():
    """"""

    #ap.getElements('BPM')

    #ap.fget('BPM', 'x')

    #ap.getElements('ID')

    for ubpm in ap.getGroupMembers(['UBPM', 'C12']):
        print(ubpm.name, ubpm.sb, ubpm.x, ubpm.y, ubpm.devname)

    for e in ap.getNeighbors(ap.getElements('ivu23g1c12d')[0], '*', n=5, elemself=True)[1:-3]:
        print(e.name, e.index)

    cfa = ap.ChannelFinderAgent()
    print(cfa.rows)
    cfa.loadSqlite(DBFILE)

    for pv, prpt, tags in cfa.rows:
        if pv.find('BPM:10') < 0: continue
        if prpt.get('devName', None) is None: continue
        print(pv, prpt, tags)

#----------------------------------------------------------------------
def print_elems_around_straight(cell_num, n=5):
    """"""

    sc = SR_CIRCUMF / 30 * cell_num # [m]

    all_elems_nearby_cells = \
        ap.getElements('*c{0:02d}*'.format(cell_num-1 if cell_num >= 2 else 30)) + \
        ap.getElements('*c{0:02d}*'.format(cell_num))
    closest = np.argmin(np.abs(np.array([e.se for e in all_elems_nearby_cells]) - sc))

    print('\n** Straight Center @ {0:.4f}'.format(sc))
    print('[Elem.Name]  [Type]     [sb]     [se]   [index]')

    past_center = False
    for e in all_elems_nearby_cells[(closest-n):(closest+n)]:
        if (not past_center) and (e.se >= sc):
            print('## Straight Center @ {0:4f} ##'.format(sc))
            past_center = True
        print('{0:12s}: {1:6s}: {2:8.4f}:{3:8.4f}: {4:d}'.format(
            e.name, e.family, e.sb, e.se, e.index))

#----------------------------------------------------------------------
def update_C02_straight():
    """"""

    pt.rdmfile('/home/yhidaka/.pytracy_control/20160930_bare_fnumReset.flat')

    cell_list = pt.getCell()
    sall = np.array(pt.getS())

    SIX = pts.getElemIndexesFromName('IDC02H1')[0]
    s_SIX = pt.getS()[SIX]

    sexts = pts.getElemIndexesFromRegExPattern(r'^S[HLM]\w+$')
    s_sexts = np.array(pt.getS())[sexts]
    #us_sext, ds_sext = sorted(np.array(sexts)[np.argsort(np.abs(s_sexts - s_SIX))[:2]])
    us_sext = sexts[np.where(s_sexts - s_SIX < 0.0)[0][-1]]
    ds_sext = sexts[np.where(s_sexts - s_SIX > 0.0)[0][0]]

    # Straight center position in the lattice file
    pt_sc = (sall[ds_sext-1] + sall[us_sext])/2.0
    print('\n# s-pos of straight center (PyTracy lattice file): {0:.9f}'.format(pt_sc))

    # print all element names in the lattice file in this straight
    elem_inds = list(range(us_sext, ds_sext+1))
    elem_names = pts.getFamNamesFromElemIndexes(elem_inds)
    sb_elems = sall[np.array(elem_inds)-1]
    se_elems = sall[elem_inds]
    print('\n(Elem. Names)          (sb)            (se)')
    for name, sb, se in zip(elem_names, sb_elems, se_elems):
        print('{0:15} : {1:.9f}   {2:.9f}'.format(name, sb ,se))

    cap_ubpm_names = ['PU1G1C02A', 'PU4G1C02A']

    pt_ubpms = pts.getElemIndexesFromFamNames(cap_ubpm_names)
    s_ubpms = sall[pt_ubpms]
    for ei in pt_ubpms:
        assert cell_list[ei].Elem.PL == 0.0
    print('\nUser BPM Infor:')
    print('(Elem.Name)           (s)       (ds from Straight Center)')
    for name, s in zip(cap_ubpm_names, s_ubpms):
        print('{0:15} : {1:.9f}'.format(name, s))

    ds = s_ubpms - pt_sc
    print('ds [m]:')
    pprint.pprint(ds)

    cell_num = 2

    print_elems_around_straight(cell_num, n=5)

    # s-pos of center of straight
    sc = SR_CIRCUMF / 30 * cell_num # [m]
    print('\n# s-pos of straight center (aphla): {0:.9f}'.format(sc))
    np.testing.assert_almost_equal(sc, pt_sc, decimal=9)

    bpm_info = [
        ('pu1g1c02a', sc + ds[0], 'PU1', 18300 + 75*1),
        ('pu4g1c02a', sc + ds[1], 'PU4', 18300 + 75*3),
    ]
    us_id_index = 18300 + 75*2
    ds_id_index = None

    # #### Adding elements for UBPMs to database ####
    for elemName, sEnd, ugg, idx in bpm_info:
        kw = dict(elemType   = 'UBPM_',
                  cell       = 'C{0:02d}'.format(cell_num),
                  girder     = 'G1',
                  symmetry   = 'A',
                  elemGroups = 'UBPM;'+ugg,
                  elemIndex  = idx,
                  elemLength = 0.0,
                  )
        ap.apdata.updateDbElement(DBFILE, 'SR', elemName, elemPosition=sEnd, **kw)

    ap.machines.load('nsls2', 'SR')

    pprint.pprint( ap.getGroupMembers(['UBPM', 'C{0:02d}'.format(cell_num)]) )
    pprint.pprint( ap.getElements('PU1') )
    pprint.pprint( ap.getElements('PU4') )

    elemName_prefix_devName_tups = [
        ('pu1g1c02a', 'SR:C02-BI{BPM:7}', 'C02-BPM7'),
        ('pu4g1c02a', 'SR:C02-BI{BPM:8}', 'C02-BPM8'),
    ]

    # #### Adding PVs for UBPM elements to database ####
    for elemName, prefix, devName in elemName_prefix_devName_tups:
        tags = ['aphla.sys.SR']
        # ^ required, otherwise can not be load by `machines.load("nsls2", "SR")`
        for pvpf, fld, hdl in BPM_PV_REC:
            if pvpf != 'Pos:XwUsrOff-Calc':
                ap.apdata.updateDbPv(
                    DBFILE, prefix + pvpf, elemName, fld, elemHandle=hdl, tags=tags,
                    quiet=True)
            else:
                ap.apdata.updateDbPv(
                    DBFILE, prefix + pvpf, elemName, fld, elemHandle=hdl, tags=tags,
                    quiet=True, devName=devName)

    ap.machines.load('nsls2', 'SR')

    ubpms = ap.getGroupMembers(['UBPM', 'C{0:02d}'.format(cell_num)])

    for k in ['x', 'y', 'x0', 'y0', 'xref1', 'yref1', 'xref2', 'yref2', 'ampl', 'xbba', 'ybba']:
        print('* (raw)', k)
        print(ap.fget(ubpms, k, unitsys=None))
        try:
            print('* (phy)', k)
            print(ap.fget(ubpms, k, unitsys='phy'))
        except:
            print('# physics conversion failed')

    # #### Adding an element for ID to database ####

    # Add SIX (center)
    elemLength = 3.5 # [m]
    elemName, sEnd = 'epu57g1c02c', s_SIX
    np.testing.assert_almost_equal(sEnd, sc - 0.0 + elemLength/2.0, decimal=9)
    kw = dict(elemType   = 'EPU',
              cell       = 'C{0:02d}'.format(cell_num),
              girder     = 'G1',
              symmetry   = 'C',
              elemGroups = 'EPU57;ID;NEXT',
              elemIndex  = us_id_index,
              elemLength = elemLength,
              )
    ap.apdata.updateDbElement(DBFILE, 'SR', elemName, elemPosition=sEnd, **kw)

    ap.machines.load('nsls2', 'SR')

    # #### Adding PVs for the ID element to database ####
    tags = ["aphla.sys.SR"]
    # a list of pv, field and handle
    if True:
        cch_epsilon = 0.15 # [A]
        idcor_pv_prefix = 'SR:C01-MG{PS:Dfsk1_ID02}'
        rec = [("SR:C02-ID:G1A{EPU:1-Ax:Gap}Mtr"    , "gap", "put"), # [mm]
               ("SR:C02-ID:G1A{EPU:1-Ax:Gap}Mtr.RBV", "gap", "get"), # [mm]
               ("SR:C02-ID:G1A{EPU:1}Cmd:Start-Cmd", "gap_trig", "put"),
               ("SR:C02-ID:G1A{EPU:1-Ax:Phase}Mode:Phs-Sel", "mode", "put"),
               ("SR:C02-ID:G1A{EPU:1-Ax:Phase}Mode:Phs-RB" , "mode", "get"),
               ("SR:C02-ID:G1A{EPU:1-Ax:Phase}Mtr"    , "phase", "put"), # [mm]
               ("SR:C02-ID:G1A{EPU:1-Ax:Phase}Mtr.RBV", "phase", "get"), # [mm]
               ("SR:C02-ID:G1A{EPU:1}Cmd:Start-Cmd", "phase_trig", "put"),
               (idcor_pv_prefix+'U1-I-SP' , 'cch0', 'put'),
               (idcor_pv_prefix+'U1Loop-I', 'cch0', 'get'),
               (idcor_pv_prefix+'U2-I-SP' , 'cch1', 'put'),
               (idcor_pv_prefix+'U2Loop-I', 'cch1', 'get'),
               (idcor_pv_prefix+'U3-I-SP' , 'cch2', 'put'),
               (idcor_pv_prefix+'U3Loop-I', 'cch2', 'get'),
               (idcor_pv_prefix+'U4-I-SP' , 'cch3', 'put'),
               (idcor_pv_prefix+'U4Loop-I', 'cch3', 'get'),
               (idcor_pv_prefix+'U5-I-SP' , 'cch4', 'put'),
               (idcor_pv_prefix+'U5Loop-I', 'cch4', 'get'),
               (idcor_pv_prefix+'U6-I-SP' , 'cch5', 'put'),
               (idcor_pv_prefix+'U6Loop-I', 'cch5', 'get'),
               #
               (idcor_pv_prefix+'U1Loop-I', 'cch[0]', 'get'),
               (idcor_pv_prefix+'U2Loop-I', 'cch[1]', 'get'),
               (idcor_pv_prefix+'U3Loop-I', 'cch[2]', 'get'),
               (idcor_pv_prefix+'U4Loop-I', 'cch[3]', 'get'),
               (idcor_pv_prefix+'U5Loop-I', 'cch[4]', 'get'),
               (idcor_pv_prefix+'U6Loop-I', 'cch[5]', 'get'),
               #("SR:C04-ID:G1{IVU:1-MPS}ch0:enable", "cch0_on", "put"),
               #("SR:C04-ID:G1{IVU:1-MPS}ch1:enable", "cch1_on", "put"),
               #("SR:C04-ID:G1{IVU:1-MPS}ch2:enable", "cch2_on", "put"),
               #("SR:C04-ID:G1{IVU:1-MPS}ch3:enable", "cch3_on", "put"),
               #("SR:C04-ID:G1{IVU:1-MPS}ch4:enable", "cch4_on", "put"),
               #("SR:C04-ID:G1{IVU:1-MPS}ch5:enable", "cch5_on", "put"),
               #
               #("SR:C21-ID:G1A{EPU:1-Ax:Gap}Mtr.MOVN", "gap_ramping", "get"),
               ]
        for pvpf, fld, hdl in rec:
            if fld.startswith('cch'):
                _kws = dict(epsilon=cch_epsilon)
            else:
                _kws = dict()
            ap.apdata.updateDbPv(
                DBFILE, pvpf, elemName, fld, elemHandle=hdl, tags=tags,
                quiet=True, **_kws)

    print_elems_around_straight(cell_num, n=5)

#----------------------------------------------------------------------
def update_C02_straight_unitconv():
    """"""

    kw = dict(compression='gzip')

    _temp_unitconv_file = UNITCONV_FILE + '.tmp'

    fnew = h5py.File(_temp_unitconv_file, 'w')
    fold = h5py.File(UNITCONV_FILE, 'r')

    # First copy existing unit conversion data
    gold = fold['UnitConversion']
    gnew = fnew.create_group('UnitConversion')
    for k, v in gold.items():

        if False: # This will end up with bigger file size
            d = gnew.create_dataset(k, data=v.value, **kw)
        else: # This will end up with smaller file size, so use this one!
            gnew[k] = v.value
            d = gnew[k]

        for ak, av in v.attrs.items():
            put_h5py_attr(d, ak, av)

    # Adding new unit conversions
    #
    id_elem_name = 'epu57g1c02c'
    #
    d = gnew.create_dataset('ID_'+id_elem_name+'_gap_rb', data=np.array([1.0, 0.0]), **kw)
    uc = {'_class_': 'polynomial', 'dst_unit': 'mm', 'dst_unit_sys': 'phy',
          'elements': [id_elem_name], 'field': 'gap', 'handle': ['readback'],
          'invertible': 1, 'src_unit': 'mm', 'src_unit_sys': ''}
    for k, v in uc.items(): put_h5py_attr(d, k, v)
    #
    d = gnew.create_dataset('ID_'+id_elem_name+'_gap_sp', data=np.array([1.0, 0.0]), **kw)
    uc = {'_class_': 'polynomial', 'dst_unit': 'mm', 'dst_unit_sys': 'phy',
          'elements': [id_elem_name], 'field': 'gap', 'handle': ['setpoint'],
          'invertible': 1, 'src_unit': 'mm', 'src_unit_sys': ''}
    for k, v in uc.items(): put_h5py_attr(d, k, v)
    #
    d = gnew.create_dataset('ID_'+id_elem_name+'_phase_rb', data=np.array([1.0, 0.0]), **kw)
    uc = {'_class_': 'polynomial', 'dst_unit': 'mm', 'dst_unit_sys': 'phy',
          'elements': [id_elem_name], 'field': 'phase', 'handle': ['readback'],
          'invertible': 1, 'src_unit': 'mm', 'src_unit_sys': ''}
    for k, v in uc.items(): put_h5py_attr(d, k, v)
    #
    d = gnew.create_dataset('ID_'+id_elem_name+'_phase_sp', data=np.array([1.0, 0.0]), **kw)
    uc = {'_class_': 'polynomial', 'dst_unit': 'mm', 'dst_unit_sys': 'phy',
          'elements': [id_elem_name], 'field': 'phase', 'handle': ['setpoint'],
          'invertible': 1, 'src_unit': 'mm', 'src_unit_sys': ''}
    for k, v in uc.items(): put_h5py_attr(d, k, v)

    fold.close()
    fnew.close()

    shutil.move(_temp_unitconv_file, UNITCONV_FILE)

#----------------------------------------------------------------------
def check_C02_elem_readback():
    """"""

    idobj = ap.getElements('epu57g1c02c')[0]
    print(idobj)

    flds = sorted(idobj.fields())

    pprint.pprint(flds)

    print('## Setpoint (Raw Unit) ## (`None` means PV not defined)')
    kwargs = dict(handle='setpoint', unitsys=None)
    for fld in flds:
        unitstr = idobj.getUnit(fld, **kwargs)
        result = idobj.get(fld, **kwargs)
        print('{0} [{1}] ='.format(fld, unitstr), result)

    print('## Readback (Raw Unit) ## (`None` means PV not defined)')
    kwargs = dict(handle='readback', unitsys=None)
    for fld in flds:
        unitstr = idobj.getUnit(fld, **kwargs)
        result = idobj.get(fld, **kwargs)
        print('{0} [{1}] ='.format(fld, unitstr), result)

    print('## Setpoint (Physics Unit) ## (`None` means PV not defined)')
    kwargs = dict(handle='setpoint', unitsys='phy')
    for fld in flds:
        unitstr = idobj.getUnit(fld, **kwargs)
        try:
            result = idobj.get(fld, **kwargs)
        except RuntimeError:
            result = '"No unit conversion available"'
        print('{0} [{1}] ='.format(fld, unitstr), result)

    print('## Readback (Physics Unit) ## (`None` means PV not defined)')
    kwargs = dict(handle='readback', unitsys='phy')
    for fld in flds:
        unitstr = idobj.getUnit(fld, **kwargs)
        try:
            result = idobj.get(fld, **kwargs)
        except RuntimeError:
            result = '"No unit conversion available"'
        print('{0} [{1}] ='.format(fld, unitstr), result)

#----------------------------------------------------------------------
def update_C19_straight():
    """"""

    pt.rdmfile('/home/yhidaka/.pytracy_control/20160610_bare.flat')

    cell_list = pt.getCell()
    sall = np.array(pt.getS())

    nyx = pts.getElemIndexesFromName('IDC19H1')[0]
    s_nyx = pt.getS()[nyx]

    sexts = pts.getElemIndexesFromRegExPattern(r'^S[HLM]\w+$')
    s_sexts = np.array(pt.getS())[sexts]
    us_sext, ds_sext = sorted(np.array(sexts)[np.argsort(np.abs(s_sexts - s_nyx))[:2]])

    # Straight center position in the lattice file
    pt_sc = (sall[ds_sext-1] + sall[us_sext])/2.0
    print('\n# s-pos of straight center (PyTracy lattice file): {0:.9f}'.format(pt_sc))

    # print all element names in the lattice file in this straight
    elem_inds = list(range(us_sext, ds_sext+1))
    elem_names = pts.getFamNamesFromElemIndexes(elem_inds)
    sb_elems = sall[np.array(elem_inds)-1]
    se_elems = sall[elem_inds]
    print('\n(Elem. Names)          (sb)            (se)')
    for name, sb, se in zip(elem_names, sb_elems, se_elems):
        print('{0:15} : {1:.9f}   {2:.9f}'.format(name, sb ,se))

    cap_ubpm_names = ['PU1G1C19A', 'PU2G1C19A', 'PU3G1C19A', 'PU4G1C19A']

    pt_ubpms = pts.getElemIndexesFromFamNames(cap_ubpm_names)
    s_ubpms = sall[pt_ubpms]
    for ei in pt_ubpms:
        assert cell_list[ei].Elem.PL == 0.0
    print('\nUser BPM Infor:')
    print('(Elem.Name)           (s)       (ds from Straight Center)')
    for name, s in zip(cap_ubpm_names, s_ubpms):
        print('{0:15} : {1:.9f}'.format(name, s))

    ds = s_ubpms - pt_sc
    print('ds [m]:')
    pprint.pprint(ds)

    cell_num = 19

    print_elems_around_straight(cell_num, n=5)

    # s-pos of center of straight
    sc = SR_CIRCUMF / 30 * cell_num # [m]
    print('\n# s-pos of straight center (aphla): {0:.9f}'.format(sc))
    np.testing.assert_almost_equal(sc, pt_sc, decimal=9)

    bpm_info = [
        ('pu1g1c19a', sc + ds[0], 'PU1', 184600 + 100),
        ('pu2g1c19a', sc + ds[1], 'PU2', 184600 + 300),
        ('pu3g1c19a', sc + ds[2], 'PU3', 184600 + 400),
        ('pu4g1c19a', sc + ds[3], 'PU4', 184600 + 600),
    ]
    us_id_index = 184600 + 200
    ds_id_index = None

    # #### Adding elements for UBPMs to database ####
    for elemName, sEnd, ugg, idx in bpm_info:
        kw = dict(elemType   = 'UBPM_',
                  cell       = 'C{0:02d}'.format(cell_num),
                  girder     = 'G1',
                  symmetry   = 'A',
                  elemGroups = 'UBPM;'+ugg,
                  elemIndex  = idx,
                  elemLength = 0.0,
                  )
        ap.apdata.updateDbElement(DBFILE, 'SR', elemName, elemPosition=sEnd, **kw)

    ap.machines.load('nsls2', 'SR')

    pprint.pprint( ap.getGroupMembers(['UBPM', 'C{0:02d}'.format(cell_num)]) )
    pprint.pprint( ap.getElements('PU1') )
    pprint.pprint( ap.getElements('PU2') )
    pprint.pprint( ap.getElements('PU3') )
    pprint.pprint( ap.getElements('PU4') )

    elemName_prefix_devName_tups = [
        ('pu1g1c19a', 'SR:C19-BI{BPM:7}', 'C19-BPM7'),
        ('pu2g1c19a', 'SR:C19-BI{BPM:8}', 'C19-BPM8'),
        ('pu3g1c19a', 'SR:C19-BI{BPM:9}', 'C19-BPM9'),
        ('pu4g1c19a', 'SR:C19-BI{BPM:10}', 'C19-BPM10'),
    ]

    # #### Adding PVs for UBPM elements to database ####
    for elemName, prefix, devName in elemName_prefix_devName_tups:
        tags = ['aphla.sys.SR']
        # ^ required, otherwise can not be load by `machines.load("nsls2", "SR")`
        for pvpf, fld, hdl in BPM_PV_REC:
            if pvpf != 'Pos:XwUsrOff-Calc':
                ap.apdata.updateDbPv(
                    DBFILE, prefix + pvpf, elemName, fld, elemHandle=hdl, tags=tags,
                    quiet=True)
            else:
                ap.apdata.updateDbPv(
                    DBFILE, prefix + pvpf, elemName, fld, elemHandle=hdl, tags=tags,
                    quiet=True, devName=devName)

    ap.machines.load('nsls2', 'SR')

    ubpms = ap.getGroupMembers(['UBPM', 'C{0:02d}'.format(cell_num)])

    for k in ['x', 'y', 'x0', 'y0', 'xref1', 'yref1', 'xref2', 'yref2', 'ampl', 'xbba', 'ybba']:
        print('* (raw)', k)
        print(ap.fget(ubpms, k, unitsys=None))
        try:
            print('* (phy)', k)
            print(ap.fget(ubpms, k, unitsys='phy'))
        except:
            print('# physics conversion failed')

    # #### Adding an element for ID to database ####

    # Add NYX (upstream)
    elemLength = 1.0 # [m]
    elemName, sEnd = 'ivu18g1c19u', s_nyx
    np.testing.assert_almost_equal(sEnd, sc - 0.545 + elemLength/2.0, decimal=9)
    kw = dict(elemType   = 'IVU',
              cell       = 'C{0:02d}'.format(cell_num),
              girder     = 'G1',
              symmetry   = 'U',
              elemGroups = 'IVU18;ID;Partner',
              elemIndex  = us_id_index,
              elemLength = elemLength,
              )
    ap.apdata.updateDbElement(DBFILE, 'SR', elemName, elemPosition=sEnd, **kw)

    ap.machines.load('nsls2', 'SR')

    # #### Adding PVs for the ID element to database ####
    tags = ["aphla.sys.SR"]
    # a list of pv, field and handle
    if True:
        cch_epsilon = 0.15 # [A]
        idcor_pv_prefix = 'SR:C18-MG{PS:Dfsk1_ID19}'
        rec = [("SR:C19-ID:G1A{NYX:1-Ax:Gap}-Mtr-SP" , "gap", "put"), # [um]
               ("SR:C19-ID:G1A{NYX:1-Ax:Gap}-Mtr.RBV", "gap", "get"), # [um]
               #("SR:C21-ID:G1A{EPU:1}Cmd:Start-Cmd", "gap_trig", "put"),
               (idcor_pv_prefix+'U1-I-SP' , 'cch0', 'put'),
               (idcor_pv_prefix+'U1Loop-I', 'cch0', 'get'),
               (idcor_pv_prefix+'U2-I-SP' , 'cch1', 'put'),
               (idcor_pv_prefix+'U2Loop-I', 'cch1', 'get'),
               (idcor_pv_prefix+'U3-I-SP' , 'cch2', 'put'),
               (idcor_pv_prefix+'U3Loop-I', 'cch2', 'get'),
               (idcor_pv_prefix+'U4-I-SP' , 'cch3', 'put'),
               (idcor_pv_prefix+'U4Loop-I', 'cch3', 'get'),
               (idcor_pv_prefix+'U5-I-SP' , 'cch4', 'put'),
               (idcor_pv_prefix+'U5Loop-I', 'cch4', 'get'),
               #
               (idcor_pv_prefix+'U1Loop-I', 'cch[0]', 'get'),
               (idcor_pv_prefix+'U2Loop-I', 'cch[1]', 'get'),
               (idcor_pv_prefix+'U3Loop-I', 'cch[2]', 'get'),
               (idcor_pv_prefix+'U4Loop-I', 'cch[3]', 'get'),
               (idcor_pv_prefix+'U5Loop-I', 'cch[4]', 'get'),
               ]
        for pvpf, fld, hdl in rec:
            if fld.startswith('cch'):
                _kws = dict(epsilon=cch_epsilon)
            else:
                _kws = dict()
            ap.apdata.updateDbPv(
                DBFILE, pvpf, elemName, fld, elemHandle=hdl, tags=tags,
                quiet=True, **_kws)

    print_elems_around_straight(cell_num, n=5)

#----------------------------------------------------------------------
def update_C19_straight_unitconv():
    """"""

    kw = dict(compression='gzip')

    _temp_unitconv_file = UNITCONV_FILE + '.tmp'

    fnew = h5py.File(_temp_unitconv_file, 'w')
    fold = h5py.File(UNITCONV_FILE, 'r')

    # First copy existing unit conversion data
    gold = fold['UnitConversion']
    gnew = fnew.create_group('UnitConversion')
    for k, v in gold.items():

        if False: # This will end up with bigger file size
            d = gnew.create_dataset(k, data=v.value, **kw)
        else: # This will end up with smaller file size, so use this one!
            gnew[k] = v.value
            d = gnew[k]

        for ak, av in v.attrs.items():
            put_h5py_attr(d, ak, av)

    # Adding new unit conversions
    #
    id_elem_name = 'ivu18g1c19u'
    #
    d = gnew.create_dataset('ID_'+id_elem_name+'_gap_rb', data=np.array([1e-3, 0.0]), **kw)
    uc = {'_class_': 'polynomial', 'dst_unit': 'mm', 'dst_unit_sys': 'phy',
          'elements': [id_elem_name], 'field': 'gap', 'handle': ['readback'],
          'invertible': 1, 'src_unit': 'um', 'src_unit_sys': ''}
    for k, v in uc.items(): put_h5py_attr(d, k, v)
    #
    d = gnew.create_dataset('ID_'+id_elem_name+'_gap_sp', data=np.array([1e-3, 0.0]), **kw)
    uc = {'_class_': 'polynomial', 'dst_unit': 'mm', 'dst_unit_sys': 'phy',
          'elements': [id_elem_name], 'field': 'gap', 'handle': ['setpoint'],
          'invertible': 1, 'src_unit': 'um', 'src_unit_sys': ''}
    for k, v in uc.items(): put_h5py_attr(d, k, v)

    fold.close()
    fnew.close()

    shutil.move(_temp_unitconv_file, UNITCONV_FILE)

#----------------------------------------------------------------------
def check_C19_elem_readback():
    """"""

    idobj = ap.getElements('ivu18g1c19u')[0]
    print(idobj)

    flds = sorted(idobj.fields())

    pprint.pprint(flds)

    print('## Setpoint (Raw Unit) ## (`None` means PV not defined)')
    kwargs = dict(handle='setpoint', unitsys=None)
    for fld in flds:
        unitstr = idobj.getUnit(fld, **kwargs)
        result = idobj.get(fld, **kwargs)
        print('{0} [{1}] ='.format(fld, unitstr), result)

    print('## Readback (Raw Unit) ## (`None` means PV not defined)')
    kwargs = dict(handle='readback', unitsys=None)
    for fld in flds:
        unitstr = idobj.getUnit(fld, **kwargs)
        result = idobj.get(fld, **kwargs)
        print('{0} [{1}] ='.format(fld, unitstr), result)

    print('## Setpoint (Physics Unit) ## (`None` means PV not defined)')
    kwargs = dict(handle='setpoint', unitsys='phy')
    for fld in flds:
        unitstr = idobj.getUnit(fld, **kwargs)
        try:
            result = idobj.get(fld, **kwargs)
        except RuntimeError:
            result = '"No unit conversion available"'
        print('{0} [{1}] ='.format(fld, unitstr), result)

    print('## Readback (Physics Unit) ## (`None` means PV not defined)')
    kwargs = dict(handle='readback', unitsys='phy')
    for fld in flds:
        unitstr = idobj.getUnit(fld, **kwargs)
        try:
            result = idobj.get(fld, **kwargs)
        except RuntimeError:
            result = '"No unit conversion available"'
        print('{0} [{1}] ='.format(fld, unitstr), result)

#----------------------------------------------------------------------
def update_C21_straight():
    """"""

    cell_num = 21

    print_elems_around_straight(cell_num, n=5)

    # s-pos of center of straight
    sc = SR_CIRCUMF / 30 * cell_num # [m]

    bpm_info = [
        ('pu1g1c21a', sc - 2.3168, 'PU1', 203140),
        ('pu4g1c21a', sc + 2.3376, 'PU4', 203560),
    ]
    us_id_index = 203210
    ds_id_index = 203490

    # #### Adding elements for UBPMs to database ####
    for elemName, sEnd, ugg, idx in bpm_info:
        kw = dict(elemType   = 'UBPM_',
                  cell       = 'C{0:02d}'.format(cell_num),
                  girder     = 'G1',
                  symmetry   = 'A',
                  elemGroups = 'UBPM;'+ugg,
                  elemIndex  = idx,
                  elemLength = 0.0,
                  )
        ap.apdata.updateDbElement(DBFILE, 'SR', elemName, elemPosition=sEnd, **kw)

    ap.machines.load('nsls2', 'SR')

    pprint.pprint( ap.getGroupMembers(['UBPM', 'C{0:02d}'.format(cell_num)]) )
    pprint.pprint( ap.getElements('PU1') )

    elemName_prefix_devName_tups = [
        ('pu1g1c21a', 'SR:C21-BI{BPM:7}', 'C21-BPM7'),
        ('pu4g1c21a', 'SR:C21-BI{BPM:8}', 'C21-BPM8'),
    ]

    # #### Adding PVs for UBPM elements to database ####
    for elemName, prefix, devName in elemName_prefix_devName_tups:
        tags = ['aphla.sys.SR']
        # ^ required, otherwise can not be load by `machines.load("nsls2", "SR")`
        for pvpf, fld, hdl in BPM_PV_REC:
            if pvpf != 'Pos:XwUsrOff-Calc':
                ap.apdata.updateDbPv(
                    DBFILE, prefix + pvpf, elemName, fld, elemHandle=hdl, tags=tags,
                    quiet=True)
            else:
                ap.apdata.updateDbPv(
                    DBFILE, prefix + pvpf, elemName, fld, elemHandle=hdl, tags=tags,
                    quiet=True, devName=devName)

    ap.machines.load('nsls2', 'SR')

    ubpms = ap.getGroupMembers(['UBPM', 'C{0:02d}'.format(cell_num)])

    for k in ['x', 'y', 'x0', 'y0', 'xref1', 'yref1', 'xref2', 'yref2', 'ampl', 'xbba', 'ybba']:
        print('* (raw)', k)
        print(ap.fget(ubpms, k, unitsys=None))
        try:
            print('* (phy)', k)
            print(ap.fget(ubpms, k, unitsys='phy'))
        except:
            print('# physics conversion failed')

    # #### Adding an element for ID to database ####

    # Add short ESM57 (upstream)
    elemLength = 1.4 # [m]
    elemName, sEnd = 'epu57g1c21u', sc - 1.4920 + elemLength/2.0
    kw = dict(elemType   = 'EPU',
              cell       = 'C{0:02d}'.format(cell_num),
              girder     = 'G1',
              symmetry   = 'U',
              elemGroups = 'EPU57;ID;NEXT',
              elemIndex  = us_id_index,
              elemLength = elemLength,
              )
    ap.apdata.updateDbElement(DBFILE, 'SR', elemName, elemPosition=sEnd, **kw)

    ap.machines.load('nsls2', 'SR')

    # #### Adding PVs for the ID element to database ####
    tags = ["aphla.sys.SR"]
    # a list of pv, field and handle
    if True:
        cch_epsilon = 0.15 # [A]
        rec = [("SR:C21-ID:G1A{EPU:1-Ax:Gap}Mtr"    , "gap", "put"), # [mm]
               ("SR:C21-ID:G1A{EPU:1-Ax:Gap}Mtr.RBV", "gap", "get"), # [mm]
               ("SR:C21-ID:G1A{EPU:1}Cmd:Start-Cmd", "gap_trig", "put"),
               ("SR:C21-ID:G1A{EPU:1-Ax:Phase}Mode:Phs-Sel", "mode", "put"),
               ("SR:C21-ID:G1A{EPU:1-Ax:Phase}Mode:Phs-RB" , "mode", "get"),
               ("SR:C21-ID:G1A{EPU:1-Ax:Phase}Mtr"    , "phase", "put"), # [mm]
               ("SR:C21-ID:G1A{EPU:1-Ax:Phase}Mtr.RBV", "phase", "get"), # [mm]
               ("SR:C21-ID:G1A{EPU:1}Cmd:Start-Cmd", "phase_trig", "put"),
               ("SR:C20-MG{PS:EPU_8}U1-I-SP" , "cch0", "put"),
               ("SR:C20-MG{PS:EPU_8}U1Loop-I", "cch0", "get"),
               ("SR:C20-MG{PS:EPU_8}U2-I-SP" , "cch1", "put"),
               ("SR:C20-MG{PS:EPU_8}U2Loop-I", "cch1", "get"),
               ("SR:C20-MG{PS:EPU_8}U3-I-SP" , "cch2", "put"),
               ("SR:C20-MG{PS:EPU_8}U3Loop-I", "cch2", "get"),
               ("SR:C20-MG{PS:EPU_8}U4-I-SP" , "cch3", "put"),
               ("SR:C20-MG{PS:EPU_8}U4Loop-I", "cch3", "get"),
               ("SR:C20-MG{PS:EPU_8}U5-I-SP" , "cch4", "put"),
               ("SR:C20-MG{PS:EPU_8}U5Loop-I", "cch4", "get"),
               ("SR:C20-MG{PS:EPU_8}U6-I-SP" , "cch5", "put"),
               ("SR:C20-MG{PS:EPU_8}U6Loop-I", "cch5", "get"),
               #
               ("SR:C20-MG{PS:EPU_8}U1Loop-I", "cch[0]", "get"),
               ("SR:C20-MG{PS:EPU_8}U2Loop-I", "cch[1]", "get"),
               ("SR:C20-MG{PS:EPU_8}U3Loop-I", "cch[2]", "get"),
               ("SR:C20-MG{PS:EPU_8}U4Loop-I", "cch[3]", "get"),
               ("SR:C20-MG{PS:EPU_8}U5Loop-I", "cch[4]", "get"),
               ("SR:C20-MG{PS:EPU_8}U6Loop-I", "cch[5]", "get"),
               #("SR:C04-ID:G1{IVU:1-MPS}ch0:enable", "cch0_on", "put"),
               #("SR:C04-ID:G1{IVU:1-MPS}ch1:enable", "cch1_on", "put"),
               #("SR:C04-ID:G1{IVU:1-MPS}ch2:enable", "cch2_on", "put"),
               #("SR:C04-ID:G1{IVU:1-MPS}ch3:enable", "cch3_on", "put"),
               #("SR:C04-ID:G1{IVU:1-MPS}ch4:enable", "cch4_on", "put"),
               #("SR:C04-ID:G1{IVU:1-MPS}ch5:enable", "cch5_on", "put"),
               #
               #("SR:C21-ID:G1A{EPU:1-Ax:Gap}Mtr.MOVN", "gap_ramping", "get"),
               ]
        for pvpf, fld, hdl in rec:
            if fld.startswith('cch'):
                _kws = dict(epsilon=cch_epsilon)
            else:
                _kws = dict()
            ap.apdata.updateDbPv(
                DBFILE, pvpf, elemName, fld, elemHandle=hdl, tags=tags,
                quiet=True, **_kws)

    print_elems_around_straight(cell_num, n=5)

#----------------------------------------------------------------------
def add_C21_2_ID_ESM105_elem_and_pvs():
    """"""

    cell_num = 21

    print_elems_around_straight(cell_num, n=5)

    # s-pos of center of straight
    sc = SR_CIRCUMF / 30 * cell_num # [m]

    #bpm_info = [
        #('pu1g1c21a', sc - 2.3168, 'PU1', 203140),
        #('pu4g1c21a', sc + 2.3376, 'PU4', 203560),
    #]
    #us_id_index = 203210
    ds_id_index = 203490

    # #### Adding an element for ID to database ####

    # Add long ESM105 (downstream)
    elemLength = 2.8 # [m]
    elemName, sEnd = 'epu105g1c21d', sc + 0.7900 + elemLength/2.0
    kw = dict(elemType   = 'EPU',
              cell       = 'C{0:02d}'.format(cell_num),
              girder     = 'G1',
              symmetry   = 'D',
              elemGroups = 'EPU105;ID;NEXT',
              elemIndex  = ds_id_index,
              elemLength = elemLength,
              )
    ap.apdata.updateDbElement(DBFILE, 'SR', elemName, elemPosition=sEnd, **kw)

    ap.machines.load('nsls2', 'SR')

    # #### Adding PVs for the ID element to database ####
    tags = ["aphla.sys.SR"]
    # a list of pv, field and handle
    if True:
        cch_epsilon = 0.15 # [A]
        rec = [("SR:C21-ID:G1B{EPU:2-Ax:Gap}Mtr"    , "gap", "put"), # [mm]
               ("SR:C21-ID:G1B{EPU:2-Ax:Gap}Mtr.RBV", "gap", "get"), # [mm]
               ("SR:C21-ID:G1B{EPU:2}Cmd:Start-Cmd", "gap_trig", "put"),
               ("SR:C21-ID:G1B{EPU:2-Ax:Phase}Mode:Phs-Sel", "mode", "put"),
               ("SR:C21-ID:G1B{EPU:2-Ax:Phase}Mode:Phs-RB" , "mode", "get"),
               ("SR:C21-ID:G1B{EPU:2-Ax:Phase}Mtr"    , "phase", "put"), # [mm]
               ("SR:C21-ID:G1B{EPU:2-Ax:Phase}Mtr.RBV", "phase", "get"), # [mm]
               ("SR:C21-ID:G1B{EPU:2}Cmd:Start-Cmd", "phase_trig", "put"),
               ("SR:C20-MG{PS:EPU_7}U1-I-SP" , "cch0", "put"),
               ("SR:C20-MG{PS:EPU_7}U1Loop-I", "cch0", "get"),
               ("SR:C20-MG{PS:EPU_7}U2-I-SP" , "cch1", "put"),
               ("SR:C20-MG{PS:EPU_7}U2Loop-I", "cch1", "get"),
               ("SR:C20-MG{PS:EPU_7}U3-I-SP" , "cch2", "put"),
               ("SR:C20-MG{PS:EPU_7}U3Loop-I", "cch2", "get"),
               ("SR:C20-MG{PS:EPU_7}U4-I-SP" , "cch3", "put"),
               ("SR:C20-MG{PS:EPU_7}U4Loop-I", "cch3", "get"),
               ("SR:C20-MG{PS:EPU_7}U5-I-SP" , "cch4", "put"),
               ("SR:C20-MG{PS:EPU_7}U5Loop-I", "cch4", "get"),
               ("SR:C20-MG{PS:EPU_7}U6-I-SP" , "cch5", "put"),
               ("SR:C20-MG{PS:EPU_7}U6Loop-I", "cch5", "get"),
               #
               ("SR:C20-MG{PS:EPU_7}U1Loop-I", "cch[0]", "get"),
               ("SR:C20-MG{PS:EPU_7}U2Loop-I", "cch[1]", "get"),
               ("SR:C20-MG{PS:EPU_7}U3Loop-I", "cch[2]", "get"),
               ("SR:C20-MG{PS:EPU_7}U4Loop-I", "cch[3]", "get"),
               ("SR:C20-MG{PS:EPU_7}U5Loop-I", "cch[4]", "get"),
               ("SR:C20-MG{PS:EPU_7}U6Loop-I", "cch[5]", "get"),
               #("SR:C04-ID:G1{IVU:1-MPS}ch0:enable", "cch0_on", "put"),
               #("SR:C04-ID:G1{IVU:1-MPS}ch1:enable", "cch1_on", "put"),
               #("SR:C04-ID:G1{IVU:1-MPS}ch2:enable", "cch2_on", "put"),
               #("SR:C04-ID:G1{IVU:1-MPS}ch3:enable", "cch3_on", "put"),
               #("SR:C04-ID:G1{IVU:1-MPS}ch4:enable", "cch4_on", "put"),
               #("SR:C04-ID:G1{IVU:1-MPS}ch5:enable", "cch5_on", "put"),
               #
               #("SR:C21-ID:G1A{EPU:1-Ax:Gap}Mtr.MOVN", "gap_ramping", "get"),
               ]
        for pvpf, fld, hdl in rec:
            if fld.startswith('cch'):
                _kws = dict(epsilon=cch_epsilon)
            else:
                _kws = dict()
            ap.apdata.updateDbPv(
                DBFILE, pvpf, elemName, fld, elemHandle=hdl, tags=tags,
                quiet=True, **_kws)

    print_elems_around_straight(cell_num, n=5)

#----------------------------------------------------------------------
def update_C21_straight_unitconv():
    """"""

    kw = dict(compression='gzip')

    _temp_unitconv_file = UNITCONV_FILE + '.tmp'

    fnew = h5py.File(_temp_unitconv_file, 'w')
    fold = h5py.File(UNITCONV_FILE, 'r')

    # First copy existing unit conversion data
    gold = fold['UnitConversion']
    gnew = fnew.create_group('UnitConversion')
    for k, v in gold.items():

        if False: # This will end up with bigger file size
            d = gnew.create_dataset(k, data=v.value, **kw)
        else: # This will end up with smaller file size, so use this one!
            gnew[k] = v.value
            d = gnew[k]

        for ak, av in v.attrs.items():
            put_h5py_attr(d, ak, av)

    # Adding new unit conversions
    #
    d = gnew.create_dataset('ID_epu57g1c21u_gap_rb', data=np.array([1.0, 0.0]), **kw)
    uc = {'_class_': 'polynomial', 'dst_unit': 'mm', 'dst_unit_sys': 'phy',
          'elements': ['epu57g1c21u'], 'field': 'gap', 'handle': ['readback'],
          'invertible': 1, 'src_unit': 'mm', 'src_unit_sys': ''}
    for k, v in uc.items(): put_h5py_attr(d, k, v)
    #
    d = gnew.create_dataset('ID_epu57g1c21u_gap_sp', data=np.array([1.0, 0.0]), **kw)
    uc = {'_class_': 'polynomial', 'dst_unit': 'mm', 'dst_unit_sys': 'phy',
          'elements': ['epu57g1c21u'], 'field': 'gap', 'handle': ['setpoint'],
          'invertible': 1, 'src_unit': 'mm', 'src_unit_sys': ''}
    for k, v in uc.items(): put_h5py_attr(d, k, v)
    #
    d = gnew.create_dataset('ID_epu57g1c21u_phase_rb', data=np.array([1.0, 0.0]), **kw)
    uc = {'_class_': 'polynomial', 'dst_unit': 'mm', 'dst_unit_sys': 'phy',
          'elements': ['epu57g1c21u'], 'field': 'phase', 'handle': ['readback'],
          'invertible': 1, 'src_unit': 'mm', 'src_unit_sys': ''}
    for k, v in uc.items(): put_h5py_attr(d, k, v)
    #
    d = gnew.create_dataset('ID_epu57g1c21u_phase_sp', data=np.array([1.0, 0.0]), **kw)
    uc = {'_class_': 'polynomial', 'dst_unit': 'mm', 'dst_unit_sys': 'phy',
          'elements': ['epu57g1c21u'], 'field': 'phase', 'handle': ['setpoint'],
          'invertible': 1, 'src_unit': 'mm', 'src_unit_sys': ''}
    for k, v in uc.items(): put_h5py_attr(d, k, v)

    fold.close()
    fnew.close()

    shutil.move(_temp_unitconv_file, UNITCONV_FILE)

#----------------------------------------------------------------------
def add_C21_2_ID_ESM105_unitconv():
    """"""

    kw = dict(compression='gzip')

    _temp_unitconv_file = UNITCONV_FILE + '.tmp'

    fnew = h5py.File(_temp_unitconv_file, 'w')
    fold = h5py.File(UNITCONV_FILE, 'r')

    # First copy existing unit conversion data
    gold = fold['UnitConversion']
    gnew = fnew.create_group('UnitConversion')
    for k, v in gold.items():

        if False: # This will end up with bigger file size
            d = gnew.create_dataset(k, data=v.value, **kw)
        else: # This will end up with smaller file size, so use this one!
            gnew[k] = v.value
            d = gnew[k]

        for ak, av in v.attrs.items():
            put_h5py_attr(d, ak, av)

    # Adding new unit conversions
    #
    d = gnew.create_dataset('ID_epu105g1c21d_gap_rb', data=np.array([1.0, 0.0]), **kw)
    uc = {'_class_': 'polynomial', 'dst_unit': 'mm', 'dst_unit_sys': 'phy',
          'elements': ['epu105g1c21d'], 'field': 'gap', 'handle': ['readback'],
          'invertible': 1, 'src_unit': 'mm', 'src_unit_sys': ''}
    for k, v in uc.items(): put_h5py_attr(d, k, v)
    #
    d = gnew.create_dataset('ID_epu105g1c21d_gap_sp', data=np.array([1.0, 0.0]), **kw)
    uc = {'_class_': 'polynomial', 'dst_unit': 'mm', 'dst_unit_sys': 'phy',
          'elements': ['epu105g1c21d'], 'field': 'gap', 'handle': ['setpoint'],
          'invertible': 1, 'src_unit': 'mm', 'src_unit_sys': ''}
    for k, v in uc.items(): put_h5py_attr(d, k, v)
    #
    d = gnew.create_dataset('ID_epu105g1c21d_phase_rb', data=np.array([1.0, 0.0]), **kw)
    uc = {'_class_': 'polynomial', 'dst_unit': 'mm', 'dst_unit_sys': 'phy',
          'elements': ['epu105g1c21d'], 'field': 'phase', 'handle': ['readback'],
          'invertible': 1, 'src_unit': 'mm', 'src_unit_sys': ''}
    for k, v in uc.items(): put_h5py_attr(d, k, v)
    #
    d = gnew.create_dataset('ID_epu105g1c21d_phase_sp', data=np.array([1.0, 0.0]), **kw)
    uc = {'_class_': 'polynomial', 'dst_unit': 'mm', 'dst_unit_sys': 'phy',
          'elements': ['epu105g1c21d'], 'field': 'phase', 'handle': ['setpoint'],
          'invertible': 1, 'src_unit': 'mm', 'src_unit_sys': ''}
    for k, v in uc.items(): put_h5py_attr(d, k, v)

    fold.close()
    fnew.close()

    shutil.move(_temp_unitconv_file, UNITCONV_FILE)

#----------------------------------------------------------------------
def diff_Xi_fcor_spos():
    """"""

    xi_fcor_csv = np.loadtxt('FCORmapforYoshi.csv', dtype=str, delimiter=',')
    xi_fcor_spos   = [float(d[0]) for d in xi_fcor_csv]
    xi_fcor_pvs    = [d[1] for d in xi_fcor_csv]
    xi_fcor_enames = [d[2] for d in xi_fcor_csv]

    fcors = ap.getElements('FCOR')

    if False:
        import pytracy as pt
        import pytracyutils.search as pts

        pt.rdmfile('/home/yhidaka/.pytracy_control/20160930_bare_fnumReset.flat')

        pt_fcors = pts.getElemIndexesFromRegExPattern('F[HLM]\w+')

        s_all = np.array(pt.getS())

        pt_fcors_sb = s_all[np.array(pt_fcors)-1]
        pt_fcors_se = s_all[pt_fcors]

        assert np.all(pt_fcors_se - pt_fcors_sb == 0.0)

        ap_fcors_sc = np.array([(e.sb + e.se)/2.0 for e in fcors])

        print('Max aphla-pytracy diff in FCOR spos [um] = {0:.3f}'.format(
            np.max(np.abs(ap_fcors_sc - pt_fcors_se)) * 1e6))

    lines = ['# (aphla s_start) (aphla s_end) (aphla s_center) (Xi spos)']
    for e, xi_s in zip(fcors, xi_fcor_spos):
        lines.append('{0:.6f}, {1:.6f}, {2:.6f}, {3:.6f}'.format(
            e.sb, e.se, (e.sb + e.se)/2.0, xi_s))
    with open('20170117_diff_fcor_spos_aphla_vs_Xi_data.txt', 'w') as f:
        f.write('\n'.join(lines))

    plt.show()

#----------------------------------------------------------------------
def update_fcors():
    """
Following IPython notebook cells from Lingyun's "hla_update_db.ipynb"
in git_repos/old_aphla_notebooks/hla_update_db.ipynb


# fcors
data = [s.split() for s in open("/home/lyyang/apconf/nsls2/fcor_elem_pvs.txt", 'r')
.readlines()]


pvl = [d[0].replace("Ps1DCCT1-I", "Sp2-SP") for d in data]
names = [d[1] for d in data]
tags = ["aphla.sys.SR"]
fld, hdl = "y", "put"
plt.plot(ap.caget(pvl))
for i in range(len(data)):
pv, elemName = pvl[i], names[i]
ap.apdata.updateDbPv(DBFILE, pv, elemName, fld, elemHandle=hdl, tags=tags, quie
t=True)

    # The text file "fcor_elem_pvs.txt" Lingyun is using has very messed-up
    # association of name-PV associations.
    #
    # In order to undo this, I am using the following MATLAB Middle Layer data
    #
    # At the same time, I'm also adding the second set of readback PVs with the
    # unit of counts like "DAC1Cnt-Sts" & "DAC2Cnt-Sts". Their field names
    # are defined to be "x2" and "y2". These PVs have the same accuracy, but
    # "x2" & "y2" are being archived without deadband issues.
    """

    # The following are from "/epics/data/mmlroot/machine/NSLS2/StorageRingID/nsls2init.m"
    # or equivalently "/direct/mmlroot-data/machine/NSLS2/StorageRingID/nsls2init.m"
    '''
%% Fast Correctors %
AO.FHCM.FamilyName             = 'FHCM';
AO.FHCM.MemberOf               = {'MachineConfig'; 'PlotFamily';  'FCOR'; 'FHCM'; 'Magnet'};
AO.FHCM.DeviceList =  [ 30 2; 30 3; 1 1; 1 2; 1 3; 2 1; 2 2; 2 3; 3 1; 3 2; 3 3; 4 1; 4 2; 4 3; 5 1; 5 2; 5 3; 6 1; 6 2; 6 3; 7 1; 7 2; 7 3; 8 1; 8 2; 8 3; 9 1; 9 2; 9 3; 10 1; 10 2; 10 3; 11 1; 11 2; 11 3; 12 1; 12 2; 12 3; 13 1; 13 2; 13 3; 14 1; 14 2; 14 3; 15 1; 15 2; 15 3; 16 1; 16 2; 16 3; 17 1; 17 2; 17 3; 18 1; 18 2; 18 3; 19 1; 19 2; 19 3; 20 1; 20 2; 20 3; 21 1; 21 2; 21 3; 22 1; 22 2; 22 3; 23 1; 23 2; 23 3; 24 1; 24 2; 24 3; 25 1; 25 2; 25 3; 26 1; 26 2; 26 3; 27 1; 27 2; 27 3; 28 1; 28 2; 28 3; 29 1; 29 2; 29 3; 30 1];
AO.FHCM.ElementList = (1:size(AO.FHCM.DeviceList,1))';
AO.FHCM.Status = ones(size(AO.FHCM.DeviceList,1),1);

AO.FHCM.Monitor.Mode           = OperationalMode;
AO.FHCM.Monitor.DataType       = 'Scalar';
AO.FHCM.Monitor.ChannelNames   = ['SR:C30-MG{PS:FH2A}I:Ps1DCCT1-I'; 'SR:C30-MG{PS:FM1A}I:Ps1DCCT1-I'; 'SR:C01-MG{PS:FL1A}I:Ps1DCCT1-I'; 'SR:C01-MG{PS:FL2A}I:Ps1DCCT1-I'; 'SR:C01-MG{PS:FM1A}I:Ps1DCCT1-I'; 'SR:C02-MG{PS:FH1A}I:Ps1DCCT1-I'; 'SR:C02-MG{PS:FH2A}I:Ps1DCCT1-I'; 'SR:C02-MG{PS:FM1A}I:Ps1DCCT1-I'; 'SR:C03-MG{PS:FL1A}I:Ps1DCCT1-I'; 'SR:C03-MG{PS:FL2A}I:Ps1DCCT1-I'; 'SR:C03-MG{PS:FM1A}I:Ps1DCCT1-I'; 'SR:C04-MG{PS:FH1A}I:Ps1DCCT1-I'; 'SR:C04-MG{PS:FH2A}I:Ps1DCCT1-I'; 'SR:C04-MG{PS:FM1A}I:Ps1DCCT1-I'; 'SR:C05-MG{PS:FL1A}I:Ps1DCCT1-I'; 'SR:C05-MG{PS:FL2A}I:Ps1DCCT1-I'; 'SR:C05-MG{PS:FM1A}I:Ps1DCCT1-I'; 'SR:C06-MG{PS:FH1A}I:Ps1DCCT1-I'; 'SR:C06-MG{PS:FH2A}I:Ps1DCCT1-I'; 'SR:C06-MG{PS:FM1A}I:Ps1DCCT1-I'; 'SR:C07-MG{PS:FL1A}I:Ps1DCCT1-I'; 'SR:C07-MG{PS:FL2A}I:Ps1DCCT1-I'; 'SR:C07-MG{PS:FM1A}I:Ps1DCCT1-I'; 'SR:C08-MG{PS:FH1A}I:Ps1DCCT1-I'; 'SR:C08-MG{PS:FH2A}I:Ps1DCCT1-I'; 'SR:C08-MG{PS:FM1A}I:Ps1DCCT1-I'; 'SR:C09-MG{PS:FL1A}I:Ps1DCCT1-I'; 'SR:C09-MG{PS:FL2A}I:Ps1DCCT1-I'; 'SR:C09-MG{PS:FM1A}I:Ps1DCCT1-I'; 'SR:C10-MG{PS:FH1A}I:Ps1DCCT1-I'; 'SR:C10-MG{PS:FH2A}I:Ps1DCCT1-I'; 'SR:C10-MG{PS:FM1A}I:Ps1DCCT1-I'; 'SR:C11-MG{PS:FL1A}I:Ps1DCCT1-I'; 'SR:C11-MG{PS:FL2A}I:Ps1DCCT1-I'; 'SR:C11-MG{PS:FM1A}I:Ps1DCCT1-I'; 'SR:C12-MG{PS:FH1A}I:Ps1DCCT1-I'; 'SR:C12-MG{PS:FH2A}I:Ps1DCCT1-I'; 'SR:C12-MG{PS:FM1A}I:Ps1DCCT1-I'; 'SR:C13-MG{PS:FL1A}I:Ps1DCCT1-I'; 'SR:C13-MG{PS:FL2A}I:Ps1DCCT1-I'; 'SR:C13-MG{PS:FM1A}I:Ps1DCCT1-I'; 'SR:C14-MG{PS:FH1A}I:Ps1DCCT1-I'; 'SR:C14-MG{PS:FH2A}I:Ps1DCCT1-I'; 'SR:C14-MG{PS:FM1A}I:Ps1DCCT1-I'; 'SR:C15-MG{PS:FL1A}I:Ps1DCCT1-I'; 'SR:C15-MG{PS:FL2A}I:Ps1DCCT1-I'; 'SR:C15-MG{PS:FM1A}I:Ps1DCCT1-I'; 'SR:C16-MG{PS:FH1A}I:Ps1DCCT1-I'; 'SR:C16-MG{PS:FH2A}I:Ps1DCCT1-I'; 'SR:C16-MG{PS:FM1A}I:Ps1DCCT1-I'; 'SR:C17-MG{PS:FL1A}I:Ps1DCCT1-I'; 'SR:C17-MG{PS:FL2A}I:Ps1DCCT1-I'; 'SR:C17-MG{PS:FM1A}I:Ps1DCCT1-I'; 'SR:C18-MG{PS:FH1A}I:Ps1DCCT1-I'; 'SR:C18-MG{PS:FH2A}I:Ps1DCCT1-I'; 'SR:C18-MG{PS:FM1A}I:Ps1DCCT1-I'; 'SR:C19-MG{PS:FL1A}I:Ps1DCCT1-I'; 'SR:C19-MG{PS:FL2A}I:Ps1DCCT1-I'; 'SR:C19-MG{PS:FM1A}I:Ps1DCCT1-I'; 'SR:C20-MG{PS:FH1A}I:Ps1DCCT1-I'; 'SR:C20-MG{PS:FH2A}I:Ps1DCCT1-I'; 'SR:C20-MG{PS:FM1A}I:Ps1DCCT1-I'; 'SR:C21-MG{PS:FL1A}I:Ps1DCCT1-I'; 'SR:C21-MG{PS:FL2A}I:Ps1DCCT1-I'; 'SR:C21-MG{PS:FM1A}I:Ps1DCCT1-I'; 'SR:C22-MG{PS:FH1A}I:Ps1DCCT1-I'; 'SR:C22-MG{PS:FH2A}I:Ps1DCCT1-I'; 'SR:C22-MG{PS:FM1A}I:Ps1DCCT1-I'; 'SR:C23-MG{PS:FL1A}I:Ps1DCCT1-I'; 'SR:C23-MG{PS:FL2A}I:Ps1DCCT1-I'; 'SR:C23-MG{PS:FM1A}I:Ps1DCCT1-I'; 'SR:C24-MG{PS:FH1A}I:Ps1DCCT1-I'; 'SR:C24-MG{PS:FH2A}I:Ps1DCCT1-I'; 'SR:C24-MG{PS:FM1A}I:Ps1DCCT1-I'; 'SR:C25-MG{PS:FL1A}I:Ps1DCCT1-I'; 'SR:C25-MG{PS:FL2A}I:Ps1DCCT1-I'; 'SR:C25-MG{PS:FM1A}I:Ps1DCCT1-I'; 'SR:C26-MG{PS:FH1A}I:Ps1DCCT1-I'; 'SR:C26-MG{PS:FH2A}I:Ps1DCCT1-I'; 'SR:C26-MG{PS:FM1A}I:Ps1DCCT1-I'; 'SR:C27-MG{PS:FL1A}I:Ps1DCCT1-I'; 'SR:C27-MG{PS:FL2A}I:Ps1DCCT1-I'; 'SR:C27-MG{PS:FM1A}I:Ps1DCCT1-I'; 'SR:C28-MG{PS:FH1A}I:Ps1DCCT1-I'; 'SR:C28-MG{PS:FH2A}I:Ps1DCCT1-I'; 'SR:C28-MG{PS:FM1A}I:Ps1DCCT1-I'; 'SR:C29-MG{PS:FL1A}I:Ps1DCCT1-I'; 'SR:C29-MG{PS:FL2A}I:Ps1DCCT1-I'; 'SR:C29-MG{PS:FM1A}I:Ps1DCCT1-I'; 'SR:C30-MG{PS:FH1A}I:Ps1DCCT1-I'];
AO.FHCM.Monitor.Units          = 'Hardware';
AO.FHCM.Monitor.HWUnits        = 'A';
AO.FHCM.Monitor.PhysicsUnits   = 'rad';
% AO.FHCM.Monitor.HW2PhysicsFcn  = @amp2k;
% AO.FHCM.Monitor.Physics2HWFcn  = @k2amp;
AO.FHCM.CommonNames = ['fh2g1c30a'; 'fm1g4c30a'; 'fl1g1c01a'; 'fl2g1c01a'; 'fm1g4c01a'; 'fh1g1c02a'; 'fh2g1c02a'; 'fm1g4c02a'; 'fl1g1c03a'; 'fl2g1c03a'; 'fm1g4c03a'; 'fh1g1c04a'; 'fh2g1c04a'; 'fm1g4c04a'; 'fl1g1c05a'; 'fl2g1c05a'; 'fm1g4c05a'; 'fh1g1c06a'; 'fh2g1c06a'; 'fm1g4c06a'; 'fl1g1c07a'; 'fl2g1c07a'; 'fm1g4c07a'; 'fh1g1c08a'; 'fh2g1c08a'; 'fm1g4c08a'; 'fl1g1c09a'; 'fl2g1c09a'; 'fm1g4c09a'; 'fh1g1c10a'; 'fh2g1c10a'; 'fm1g4c10a'; 'fl1g1c11a'; 'fl2g1c11a'; 'fm1g4c11a'; 'fh1g1c12a'; 'fh2g1c12a'; 'fm1g4c12a'; 'fl1g1c13a'; 'fl2g1c13a'; 'fm1g4c13a'; 'fh1g1c14a'; 'fh2g1c14a'; 'fm1g4c14a'; 'fl1g1c15a'; 'fl2g1c15a'; 'fm1g4c15a'; 'fh1g1c16a'; 'fh2g1c16a'; 'fm1g4c16a'; 'fl1g1c17a'; 'fl2g1c17a'; 'fm1g4c17a'; 'fh1g1c18a'; 'fh2g1c18a'; 'fm1g4c18a'; 'fl1g1c19a'; 'fl2g1c19a'; 'fm1g4c19a'; 'fh1g1c20a'; 'fh2g1c20a'; 'fm1g4c20a'; 'fl1g1c21a'; 'fl2g1c21a'; 'fm1g4c21a'; 'fh1g1c22a'; 'fh2g1c22a'; 'fm1g4c22a'; 'fl1g1c23a'; 'fl2g1c23a'; 'fm1g4c23a'; 'fh1g1c24a'; 'fh2g1c24a'; 'fm1g4c24a'; 'fl1g1c25a'; 'fl2g1c25a'; 'fm1g4c25a'; 'fh1g1c26a'; 'fh2g1c26a'; 'fm1g4c26a'; 'fl1g1c27a'; 'fl2g1c27a'; 'fm1g4c27a'; 'fh1g1c28a'; 'fh2g1c28a'; 'fm1g4c28a'; 'fl1g1c29a'; 'fl2g1c29a'; 'fm1g4c29a'; 'fh1g1c30a'];
AO.FHCM.Setpoint.MemberOf      = {'PlotFamily'; 'Save/Restore'; 'FCOR'; 'Horizontal'; 'FHCM'; 'Magnet'; 'Setpoint'; 'measbpmresp';};
AO.FHCM.Setpoint.Mode          = OperationalMode;
AO.FHCM.Setpoint.DataType      = 'Scalar';
AO.FHCM.Setpoint.ChannelNames  = ['SR:C30-MG{PS:FH2A}I:Sp1-SP'; 'SR:C30-MG{PS:FM1A}I:Sp1-SP'; 'SR:C01-MG{PS:FL1A}I:Sp1-SP'; 'SR:C01-MG{PS:FL2A}I:Sp1-SP'; 'SR:C01-MG{PS:FM1A}I:Sp1-SP'; 'SR:C02-MG{PS:FH1A}I:Sp1-SP'; 'SR:C02-MG{PS:FH2A}I:Sp1-SP'; 'SR:C02-MG{PS:FM1A}I:Sp1-SP'; 'SR:C03-MG{PS:FL1A}I:Sp1-SP'; 'SR:C03-MG{PS:FL2A}I:Sp1-SP'; 'SR:C03-MG{PS:FM1A}I:Sp1-SP'; 'SR:C04-MG{PS:FH1A}I:Sp1-SP'; 'SR:C04-MG{PS:FH2A}I:Sp1-SP'; 'SR:C04-MG{PS:FM1A}I:Sp1-SP'; 'SR:C05-MG{PS:FL1A}I:Sp1-SP'; 'SR:C05-MG{PS:FL2A}I:Sp1-SP'; 'SR:C05-MG{PS:FM1A}I:Sp1-SP'; 'SR:C06-MG{PS:FH1A}I:Sp1-SP'; 'SR:C06-MG{PS:FH2A}I:Sp1-SP'; 'SR:C06-MG{PS:FM1A}I:Sp1-SP'; 'SR:C07-MG{PS:FL1A}I:Sp1-SP'; 'SR:C07-MG{PS:FL2A}I:Sp1-SP'; 'SR:C07-MG{PS:FM1A}I:Sp1-SP'; 'SR:C08-MG{PS:FH1A}I:Sp1-SP'; 'SR:C08-MG{PS:FH2A}I:Sp1-SP'; 'SR:C08-MG{PS:FM1A}I:Sp1-SP'; 'SR:C09-MG{PS:FL1A}I:Sp1-SP'; 'SR:C09-MG{PS:FL2A}I:Sp1-SP'; 'SR:C09-MG{PS:FM1A}I:Sp1-SP'; 'SR:C10-MG{PS:FH1A}I:Sp1-SP'; 'SR:C10-MG{PS:FH2A}I:Sp1-SP'; 'SR:C10-MG{PS:FM1A}I:Sp1-SP'; 'SR:C11-MG{PS:FL1A}I:Sp1-SP'; 'SR:C11-MG{PS:FL2A}I:Sp1-SP'; 'SR:C11-MG{PS:FM1A}I:Sp1-SP'; 'SR:C12-MG{PS:FH1A}I:Sp1-SP'; 'SR:C12-MG{PS:FH2A}I:Sp1-SP'; 'SR:C12-MG{PS:FM1A}I:Sp1-SP'; 'SR:C13-MG{PS:FL1A}I:Sp1-SP'; 'SR:C13-MG{PS:FL2A}I:Sp1-SP'; 'SR:C13-MG{PS:FM1A}I:Sp1-SP'; 'SR:C14-MG{PS:FH1A}I:Sp1-SP'; 'SR:C14-MG{PS:FH2A}I:Sp1-SP'; 'SR:C14-MG{PS:FM1A}I:Sp1-SP'; 'SR:C15-MG{PS:FL1A}I:Sp1-SP'; 'SR:C15-MG{PS:FL2A}I:Sp1-SP'; 'SR:C15-MG{PS:FM1A}I:Sp1-SP'; 'SR:C16-MG{PS:FH1A}I:Sp1-SP'; 'SR:C16-MG{PS:FH2A}I:Sp1-SP'; 'SR:C16-MG{PS:FM1A}I:Sp1-SP'; 'SR:C17-MG{PS:FL1A}I:Sp1-SP'; 'SR:C17-MG{PS:FL2A}I:Sp1-SP'; 'SR:C17-MG{PS:FM1A}I:Sp1-SP'; 'SR:C18-MG{PS:FH1A}I:Sp1-SP'; 'SR:C18-MG{PS:FH2A}I:Sp1-SP'; 'SR:C18-MG{PS:FM1A}I:Sp1-SP'; 'SR:C19-MG{PS:FL1A}I:Sp1-SP'; 'SR:C19-MG{PS:FL2A}I:Sp1-SP'; 'SR:C19-MG{PS:FM1A}I:Sp1-SP'; 'SR:C20-MG{PS:FH1A}I:Sp1-SP'; 'SR:C20-MG{PS:FH2A}I:Sp1-SP'; 'SR:C20-MG{PS:FM1A}I:Sp1-SP'; 'SR:C21-MG{PS:FL1A}I:Sp1-SP'; 'SR:C21-MG{PS:FL2A}I:Sp1-SP'; 'SR:C21-MG{PS:FM1A}I:Sp1-SP'; 'SR:C22-MG{PS:FH1A}I:Sp1-SP'; 'SR:C22-MG{PS:FH2A}I:Sp1-SP'; 'SR:C22-MG{PS:FM1A}I:Sp1-SP'; 'SR:C23-MG{PS:FL1A}I:Sp1-SP'; 'SR:C23-MG{PS:FL2A}I:Sp1-SP'; 'SR:C23-MG{PS:FM1A}I:Sp1-SP'; 'SR:C24-MG{PS:FH1A}I:Sp1-SP'; 'SR:C24-MG{PS:FH2A}I:Sp1-SP'; 'SR:C24-MG{PS:FM1A}I:Sp1-SP'; 'SR:C25-MG{PS:FL1A}I:Sp1-SP'; 'SR:C25-MG{PS:FL2A}I:Sp1-SP'; 'SR:C25-MG{PS:FM1A}I:Sp1-SP'; 'SR:C26-MG{PS:FH1A}I:Sp1-SP'; 'SR:C26-MG{PS:FH2A}I:Sp1-SP'; 'SR:C26-MG{PS:FM1A}I:Sp1-SP'; 'SR:C27-MG{PS:FL1A}I:Sp1-SP'; 'SR:C27-MG{PS:FL2A}I:Sp1-SP'; 'SR:C27-MG{PS:FM1A}I:Sp1-SP'; 'SR:C28-MG{PS:FH1A}I:Sp1-SP'; 'SR:C28-MG{PS:FH2A}I:Sp1-SP'; 'SR:C28-MG{PS:FM1A}I:Sp1-SP'; 'SR:C29-MG{PS:FL1A}I:Sp1-SP'; 'SR:C29-MG{PS:FL2A}I:Sp1-SP'; 'SR:C29-MG{PS:FM1A}I:Sp1-SP'; 'SR:C30-MG{PS:FH1A}I:Sp1-SP'];
AO.FHCM.Setpoint.Units         = 'Hardware';
AO.FHCM.Setpoint.HWUnits       = 'A';
AO.FHCM.Setpoint.PhysicsUnits  = 'rad';
% AO.FHCM.Setpoint.HW2PhysicsFcn = @amp2k;
% AO.FHCM.Setpoint.Physics2HWFcn = @k2amp;
% FHCM kick setpoint


AO.FVCM.FamilyName             = 'FVCM';
AO.FVCM.MemberOf               = {'PlotFamily';  'FCOR'; 'FVCM'; 'Magnet'};
AO.FVCM.DeviceList =  [ 30 2; 30 3; 1 1; 1 2; 1 3; 2 1; 2 2; 2 3; 3 1; 3 2; 3 3; 4 1; 4 2; 4 3; 5 1; 5 2; 5 3; 6 1; 6 2; 6 3; 7 1; 7 2; 7 3; 8 1; 8 2; 8 3; 9 1; 9 2; 9 3; 10 1; 10 2; 10 3; 11 1; 11 2; 11 3; 12 1; 12 2; 12 3; 13 1; 13 2; 13 3; 14 1; 14 2; 14 3; 15 1; 15 2; 15 3; 16 1; 16 2; 16 3; 17 1; 17 2; 17 3; 18 1; 18 2; 18 3; 19 1; 19 2; 19 3; 20 1; 20 2; 20 3; 21 1; 21 2; 21 3; 22 1; 22 2; 22 3; 23 1; 23 2; 23 3; 24 1; 24 2; 24 3; 25 1; 25 2; 25 3; 26 1; 26 2; 26 3; 27 1; 27 2; 27 3; 28 1; 28 2; 28 3; 29 1; 29 2; 29 3; 30 1];
AO.FVCM.ElementList = (1:size(AO.FHCM.DeviceList,1))';
AO.FVCM.Status = ones(size(AO.FHCM.DeviceList,1),1);

AO.FVCM.Monitor.Mode           = OperationalMode;
AO.FVCM.Monitor.DataType       = 'Scalar';
AO.FVCM.Monitor.ChannelNames   = ['SR:C30-MG{PS:FH2A}I:Ps2DCCT1-I'; 'SR:C30-MG{PS:FM1A}I:Ps2DCCT1-I'; 'SR:C01-MG{PS:FL1A}I:Ps2DCCT1-I'; 'SR:C01-MG{PS:FL2A}I:Ps2DCCT1-I'; 'SR:C01-MG{PS:FM1A}I:Ps2DCCT1-I'; 'SR:C02-MG{PS:FH1A}I:Ps2DCCT1-I'; 'SR:C02-MG{PS:FH2A}I:Ps2DCCT1-I'; 'SR:C02-MG{PS:FM1A}I:Ps2DCCT1-I'; 'SR:C03-MG{PS:FL1A}I:Ps2DCCT1-I'; 'SR:C03-MG{PS:FL2A}I:Ps2DCCT1-I'; 'SR:C03-MG{PS:FM1A}I:Ps2DCCT1-I'; 'SR:C04-MG{PS:FH1A}I:Ps2DCCT1-I'; 'SR:C04-MG{PS:FH2A}I:Ps2DCCT1-I'; 'SR:C04-MG{PS:FM1A}I:Ps2DCCT1-I'; 'SR:C05-MG{PS:FL1A}I:Ps2DCCT1-I'; 'SR:C05-MG{PS:FL2A}I:Ps2DCCT1-I'; 'SR:C05-MG{PS:FM1A}I:Ps2DCCT1-I'; 'SR:C06-MG{PS:FH1A}I:Ps2DCCT1-I'; 'SR:C06-MG{PS:FH2A}I:Ps2DCCT1-I'; 'SR:C06-MG{PS:FM1A}I:Ps2DCCT1-I'; 'SR:C07-MG{PS:FL1A}I:Ps2DCCT1-I'; 'SR:C07-MG{PS:FL2A}I:Ps2DCCT1-I'; 'SR:C07-MG{PS:FM1A}I:Ps2DCCT1-I'; 'SR:C08-MG{PS:FH1A}I:Ps2DCCT1-I'; 'SR:C08-MG{PS:FH2A}I:Ps2DCCT1-I'; 'SR:C08-MG{PS:FM1A}I:Ps2DCCT1-I'; 'SR:C09-MG{PS:FL1A}I:Ps2DCCT1-I'; 'SR:C09-MG{PS:FL2A}I:Ps2DCCT1-I'; 'SR:C09-MG{PS:FM1A}I:Ps2DCCT1-I'; 'SR:C10-MG{PS:FH1A}I:Ps2DCCT1-I'; 'SR:C10-MG{PS:FH2A}I:Ps2DCCT1-I'; 'SR:C10-MG{PS:FM1A}I:Ps2DCCT1-I'; 'SR:C11-MG{PS:FL1A}I:Ps2DCCT1-I'; 'SR:C11-MG{PS:FL2A}I:Ps2DCCT1-I'; 'SR:C11-MG{PS:FM1A}I:Ps2DCCT1-I'; 'SR:C12-MG{PS:FH1A}I:Ps2DCCT1-I'; 'SR:C12-MG{PS:FH2A}I:Ps2DCCT1-I'; 'SR:C12-MG{PS:FM1A}I:Ps2DCCT1-I'; 'SR:C13-MG{PS:FL1A}I:Ps2DCCT1-I'; 'SR:C13-MG{PS:FL2A}I:Ps2DCCT1-I'; 'SR:C13-MG{PS:FM1A}I:Ps2DCCT1-I'; 'SR:C14-MG{PS:FH1A}I:Ps2DCCT1-I'; 'SR:C14-MG{PS:FH2A}I:Ps2DCCT1-I'; 'SR:C14-MG{PS:FM1A}I:Ps2DCCT1-I'; 'SR:C15-MG{PS:FL1A}I:Ps2DCCT1-I'; 'SR:C15-MG{PS:FL2A}I:Ps2DCCT1-I'; 'SR:C15-MG{PS:FM1A}I:Ps2DCCT1-I'; 'SR:C16-MG{PS:FH1A}I:Ps2DCCT1-I'; 'SR:C16-MG{PS:FH2A}I:Ps2DCCT1-I'; 'SR:C16-MG{PS:FM1A}I:Ps2DCCT1-I'; 'SR:C17-MG{PS:FL1A}I:Ps2DCCT1-I'; 'SR:C17-MG{PS:FL2A}I:Ps2DCCT1-I'; 'SR:C17-MG{PS:FM1A}I:Ps2DCCT1-I'; 'SR:C18-MG{PS:FH1A}I:Ps2DCCT1-I'; 'SR:C18-MG{PS:FH2A}I:Ps2DCCT1-I'; 'SR:C18-MG{PS:FM1A}I:Ps2DCCT1-I'; 'SR:C19-MG{PS:FL1A}I:Ps2DCCT1-I'; 'SR:C19-MG{PS:FL2A}I:Ps2DCCT1-I'; 'SR:C19-MG{PS:FM1A}I:Ps2DCCT1-I'; 'SR:C20-MG{PS:FH1A}I:Ps2DCCT1-I'; 'SR:C20-MG{PS:FH2A}I:Ps2DCCT1-I'; 'SR:C20-MG{PS:FM1A}I:Ps2DCCT1-I'; 'SR:C21-MG{PS:FL1A}I:Ps2DCCT1-I'; 'SR:C21-MG{PS:FL2A}I:Ps2DCCT1-I'; 'SR:C21-MG{PS:FM1A}I:Ps2DCCT1-I'; 'SR:C22-MG{PS:FH1A}I:Ps2DCCT1-I'; 'SR:C22-MG{PS:FH2A}I:Ps2DCCT1-I'; 'SR:C22-MG{PS:FM1A}I:Ps2DCCT1-I'; 'SR:C23-MG{PS:FL1A}I:Ps2DCCT1-I'; 'SR:C23-MG{PS:FL2A}I:Ps2DCCT1-I'; 'SR:C23-MG{PS:FM1A}I:Ps2DCCT1-I'; 'SR:C24-MG{PS:FH1A}I:Ps2DCCT1-I'; 'SR:C24-MG{PS:FH2A}I:Ps2DCCT1-I'; 'SR:C24-MG{PS:FM1A}I:Ps2DCCT1-I'; 'SR:C25-MG{PS:FL1A}I:Ps2DCCT1-I'; 'SR:C25-MG{PS:FL2A}I:Ps2DCCT1-I'; 'SR:C25-MG{PS:FM1A}I:Ps2DCCT1-I'; 'SR:C26-MG{PS:FH1A}I:Ps2DCCT1-I'; 'SR:C26-MG{PS:FH2A}I:Ps2DCCT1-I'; 'SR:C26-MG{PS:FM1A}I:Ps2DCCT1-I'; 'SR:C27-MG{PS:FL1A}I:Ps2DCCT1-I'; 'SR:C27-MG{PS:FL2A}I:Ps2DCCT1-I'; 'SR:C27-MG{PS:FM1A}I:Ps2DCCT1-I'; 'SR:C28-MG{PS:FH1A}I:Ps2DCCT1-I'; 'SR:C28-MG{PS:FH2A}I:Ps2DCCT1-I'; 'SR:C28-MG{PS:FM1A}I:Ps2DCCT1-I'; 'SR:C29-MG{PS:FL1A}I:Ps2DCCT1-I'; 'SR:C29-MG{PS:FL2A}I:Ps2DCCT1-I'; 'SR:C29-MG{PS:FM1A}I:Ps2DCCT1-I'; 'SR:C30-MG{PS:FH1A}I:Ps2DCCT1-I'];
AO.FVCM.Monitor.Units          = 'Hardware';
AO.FVCM.Monitor.HWUnits        = 'A';
AO.FVCM.Monitor.PhysicsUnits   = 'rad';
% AO.FVCM.Monitor.HW2PhysicsFcn  = @amp2k;
% AO.FVCM.Monitor.Physics2HWFcn  = @k2amp;
AO.FVCM.CommonNames =  ['fh2g1c30a'; 'fm1g4c30a'; 'fl1g1c01a'; 'fl2g1c01a'; 'fm1g4c01a'; 'fh1g1c02a'; 'fh2g1c02a'; 'fm1g4c02a'; 'fl1g1c03a'; 'fl2g1c03a'; 'fm1g4c03a'; 'fh1g1c04a'; 'fh2g1c04a'; 'fm1g4c04a'; 'fl1g1c05a'; 'fl2g1c05a'; 'fm1g4c05a'; 'fh1g1c06a'; 'fh2g1c06a'; 'fm1g4c06a'; 'fl1g1c07a'; 'fl2g1c07a'; 'fm1g4c07a'; 'fh1g1c08a'; 'fh2g1c08a'; 'fm1g4c08a'; 'fl1g1c09a'; 'fl2g1c09a'; 'fm1g4c09a'; 'fh1g1c10a'; 'fh2g1c10a'; 'fm1g4c10a'; 'fl1g1c11a'; 'fl2g1c11a'; 'fm1g4c11a'; 'fh1g1c12a'; 'fh2g1c12a'; 'fm1g4c12a'; 'fl1g1c13a'; 'fl2g1c13a'; 'fm1g4c13a'; 'fh1g1c14a'; 'fh2g1c14a'; 'fm1g4c14a'; 'fl1g1c15a'; 'fl2g1c15a'; 'fm1g4c15a'; 'fh1g1c16a'; 'fh2g1c16a'; 'fm1g4c16a'; 'fl1g1c17a'; 'fl2g1c17a'; 'fm1g4c17a'; 'fh1g1c18a'; 'fh2g1c18a'; 'fm1g4c18a'; 'fl1g1c19a'; 'fl2g1c19a'; 'fm1g4c19a'; 'fh1g1c20a'; 'fh2g1c20a'; 'fm1g4c20a'; 'fl1g1c21a'; 'fl2g1c21a'; 'fm1g4c21a'; 'fh1g1c22a'; 'fh2g1c22a'; 'fm1g4c22a'; 'fl1g1c23a'; 'fl2g1c23a'; 'fm1g4c23a'; 'fh1g1c24a'; 'fh2g1c24a'; 'fm1g4c24a'; 'fl1g1c25a'; 'fl2g1c25a'; 'fm1g4c25a'; 'fh1g1c26a'; 'fh2g1c26a'; 'fm1g4c26a'; 'fl1g1c27a'; 'fl2g1c27a'; 'fm1g4c27a'; 'fh1g1c28a'; 'fh2g1c28a'; 'fm1g4c28a'; 'fl1g1c29a'; 'fl2g1c29a'; 'fm1g4c29a'; 'fh1g1c30a'];
AO.FVCM.Setpoint.MemberOf      = {'PlotFamily'; 'Save/Restore'; 'FCOR'; 'Vertical'; 'FVCM'; 'Magnet'; 'Setpoint'; 'measbpmresp';};
AO.FVCM.Setpoint.Mode          = OperationalMode;
AO.FVCM.Setpoint.DataType      = 'Scalar';
AO.FVCM.Setpoint.ChannelNames  = ['SR:C30-MG{PS:FH2A}I:Sp2-SP'; 'SR:C30-MG{PS:FM1A}I:Sp2-SP'; 'SR:C01-MG{PS:FL1A}I:Sp2-SP'; 'SR:C01-MG{PS:FL2A}I:Sp2-SP'; 'SR:C01-MG{PS:FM1A}I:Sp2-SP'; 'SR:C02-MG{PS:FH1A}I:Sp2-SP'; 'SR:C02-MG{PS:FH2A}I:Sp2-SP'; 'SR:C02-MG{PS:FM1A}I:Sp2-SP'; 'SR:C03-MG{PS:FL1A}I:Sp2-SP'; 'SR:C03-MG{PS:FL2A}I:Sp2-SP'; 'SR:C03-MG{PS:FM1A}I:Sp2-SP'; 'SR:C04-MG{PS:FH1A}I:Sp2-SP'; 'SR:C04-MG{PS:FH2A}I:Sp2-SP'; 'SR:C04-MG{PS:FM1A}I:Sp2-SP'; 'SR:C05-MG{PS:FL1A}I:Sp2-SP'; 'SR:C05-MG{PS:FL2A}I:Sp2-SP'; 'SR:C05-MG{PS:FM1A}I:Sp2-SP'; 'SR:C06-MG{PS:FH1A}I:Sp2-SP'; 'SR:C06-MG{PS:FH2A}I:Sp2-SP'; 'SR:C06-MG{PS:FM1A}I:Sp2-SP'; 'SR:C07-MG{PS:FL1A}I:Sp2-SP'; 'SR:C07-MG{PS:FL2A}I:Sp2-SP'; 'SR:C07-MG{PS:FM1A}I:Sp2-SP'; 'SR:C08-MG{PS:FH1A}I:Sp2-SP'; 'SR:C08-MG{PS:FH2A}I:Sp2-SP'; 'SR:C08-MG{PS:FM1A}I:Sp2-SP'; 'SR:C09-MG{PS:FL1A}I:Sp2-SP'; 'SR:C09-MG{PS:FL2A}I:Sp2-SP'; 'SR:C09-MG{PS:FM1A}I:Sp2-SP'; 'SR:C10-MG{PS:FH1A}I:Sp2-SP'; 'SR:C10-MG{PS:FH2A}I:Sp2-SP'; 'SR:C10-MG{PS:FM1A}I:Sp2-SP'; 'SR:C11-MG{PS:FL1A}I:Sp2-SP'; 'SR:C11-MG{PS:FL2A}I:Sp2-SP'; 'SR:C11-MG{PS:FM1A}I:Sp2-SP'; 'SR:C12-MG{PS:FH1A}I:Sp2-SP'; 'SR:C12-MG{PS:FH2A}I:Sp2-SP'; 'SR:C12-MG{PS:FM1A}I:Sp2-SP'; 'SR:C13-MG{PS:FL1A}I:Sp2-SP'; 'SR:C13-MG{PS:FL2A}I:Sp2-SP'; 'SR:C13-MG{PS:FM1A}I:Sp2-SP'; 'SR:C14-MG{PS:FH1A}I:Sp2-SP'; 'SR:C14-MG{PS:FH2A}I:Sp2-SP'; 'SR:C14-MG{PS:FM1A}I:Sp2-SP'; 'SR:C15-MG{PS:FL1A}I:Sp2-SP'; 'SR:C15-MG{PS:FL2A}I:Sp2-SP'; 'SR:C15-MG{PS:FM1A}I:Sp2-SP'; 'SR:C16-MG{PS:FH1A}I:Sp2-SP'; 'SR:C16-MG{PS:FH2A}I:Sp2-SP'; 'SR:C16-MG{PS:FM1A}I:Sp2-SP'; 'SR:C17-MG{PS:FL1A}I:Sp2-SP'; 'SR:C17-MG{PS:FL2A}I:Sp2-SP'; 'SR:C17-MG{PS:FM1A}I:Sp2-SP'; 'SR:C18-MG{PS:FH1A}I:Sp2-SP'; 'SR:C18-MG{PS:FH2A}I:Sp2-SP'; 'SR:C18-MG{PS:FM1A}I:Sp2-SP'; 'SR:C19-MG{PS:FL1A}I:Sp2-SP'; 'SR:C19-MG{PS:FL2A}I:Sp2-SP'; 'SR:C19-MG{PS:FM1A}I:Sp2-SP'; 'SR:C20-MG{PS:FH1A}I:Sp2-SP'; 'SR:C20-MG{PS:FH2A}I:Sp2-SP'; 'SR:C20-MG{PS:FM1A}I:Sp2-SP'; 'SR:C21-MG{PS:FL1A}I:Sp2-SP'; 'SR:C21-MG{PS:FL2A}I:Sp2-SP'; 'SR:C21-MG{PS:FM1A}I:Sp2-SP'; 'SR:C22-MG{PS:FH1A}I:Sp2-SP'; 'SR:C22-MG{PS:FH2A}I:Sp2-SP'; 'SR:C22-MG{PS:FM1A}I:Sp2-SP'; 'SR:C23-MG{PS:FL1A}I:Sp2-SP'; 'SR:C23-MG{PS:FL2A}I:Sp2-SP'; 'SR:C23-MG{PS:FM1A}I:Sp2-SP'; 'SR:C24-MG{PS:FH1A}I:Sp2-SP'; 'SR:C24-MG{PS:FH2A}I:Sp2-SP'; 'SR:C24-MG{PS:FM1A}I:Sp2-SP'; 'SR:C25-MG{PS:FL1A}I:Sp2-SP'; 'SR:C25-MG{PS:FL2A}I:Sp2-SP'; 'SR:C25-MG{PS:FM1A}I:Sp2-SP'; 'SR:C26-MG{PS:FH1A}I:Sp2-SP'; 'SR:C26-MG{PS:FH2A}I:Sp2-SP'; 'SR:C26-MG{PS:FM1A}I:Sp2-SP'; 'SR:C27-MG{PS:FL1A}I:Sp2-SP'; 'SR:C27-MG{PS:FL2A}I:Sp2-SP'; 'SR:C27-MG{PS:FM1A}I:Sp2-SP'; 'SR:C28-MG{PS:FH1A}I:Sp2-SP'; 'SR:C28-MG{PS:FH2A}I:Sp2-SP'; 'SR:C28-MG{PS:FM1A}I:Sp2-SP'; 'SR:C29-MG{PS:FL1A}I:Sp2-SP'; 'SR:C29-MG{PS:FL2A}I:Sp2-SP'; 'SR:C29-MG{PS:FM1A}I:Sp2-SP'; 'SR:C30-MG{PS:FH1A}I:Sp2-SP'];
AO.FVCM.Setpoint.Units         = 'Hardware';
AO.FVCM.Setpoint.HWUnits       = 'A';
AO.FVCM.Setpoint.PhysicsUnits  = 'rad';
% AO.FVCM.Setpoint.HW2PhysicsFcn = @amp2k;
% AO.FVCM.Setpoint.Physics2HWFcn = @k2amp;
% FVCM kick setpoint

CMrange = 1.25;   % [A]
CMHgain  = 15.0e-06/2.5;
CMVgain  = 15.0e-06/2.5;
RMkick  = 2*0.5;  % Kick size for orbit response matrix measurement [A]
CMtol   = 0.050;  % Tolerance [A]


for i=1:30 % number of superperiods
    for j=1:3 % six correctors per cell
        k=j+3*(i-1);
        AO.FHCM.Setpoint.Range(k,:)            = [-CMrange CMrange];
        AO.FVCM.Setpoint.Range(k,:)            = [-CMrange CMrange];
        AO.FHCM.Setpoint.Tolerance(k,1)        = CMtol;
        AO.FVCM.Setpoint.Tolerance(k,1)        = CMtol;
        AO.FHCM.Setpoint.DeltaRespMat(k,1)     = RMkick;
        AO.FVCM.Setpoint.DeltaRespMat(k,1)     = RMkick;
        AO.FHCM.Monitor.HW2PhysicsParams(k,1)  = -CMHgain;
        AO.FVCM.Monitor.HW2PhysicsParams(k,1)  = -CMVgain;
        AO.FHCM.Monitor.Physics2HWParams(k,1)  = -1/CMHgain;
        AO.FVCM.Monitor.Physics2HWParams(k,1)  = -1/CMVgain;
        AO.FHCM.Setpoint.HW2PhysicsParams(k,1) = -CMHgain;
        AO.FVCM.Setpoint.HW2PhysicsParams(k,1) = -CMVgain;
        AO.FHCM.Setpoint.Physics2HWParams(k,1) = -1/CMHgain;
        AO.FVCM.Setpoint.Physics2HWParams(k,1) = -1/CMVgain;
    end
end
'''
    matlab_mml_fcor_H_pvrb_list = [
        pv.replace("'", '').strip() for pv in
        "'SR:C30-MG{PS:FH2A}I:Ps1DCCT1-I'; 'SR:C30-MG{PS:FM1A}I:Ps1DCCT1-I'; 'SR:C01-MG{PS:FL1A}I:Ps1DCCT1-I'; 'SR:C01-MG{PS:FL2A}I:Ps1DCCT1-I'; 'SR:C01-MG{PS:FM1A}I:Ps1DCCT1-I'; 'SR:C02-MG{PS:FH1A}I:Ps1DCCT1-I'; 'SR:C02-MG{PS:FH2A}I:Ps1DCCT1-I'; 'SR:C02-MG{PS:FM1A}I:Ps1DCCT1-I'; 'SR:C03-MG{PS:FL1A}I:Ps1DCCT1-I'; 'SR:C03-MG{PS:FL2A}I:Ps1DCCT1-I'; 'SR:C03-MG{PS:FM1A}I:Ps1DCCT1-I'; 'SR:C04-MG{PS:FH1A}I:Ps1DCCT1-I'; 'SR:C04-MG{PS:FH2A}I:Ps1DCCT1-I'; 'SR:C04-MG{PS:FM1A}I:Ps1DCCT1-I'; 'SR:C05-MG{PS:FL1A}I:Ps1DCCT1-I'; 'SR:C05-MG{PS:FL2A}I:Ps1DCCT1-I'; 'SR:C05-MG{PS:FM1A}I:Ps1DCCT1-I'; 'SR:C06-MG{PS:FH1A}I:Ps1DCCT1-I'; 'SR:C06-MG{PS:FH2A}I:Ps1DCCT1-I'; 'SR:C06-MG{PS:FM1A}I:Ps1DCCT1-I'; 'SR:C07-MG{PS:FL1A}I:Ps1DCCT1-I'; 'SR:C07-MG{PS:FL2A}I:Ps1DCCT1-I'; 'SR:C07-MG{PS:FM1A}I:Ps1DCCT1-I'; 'SR:C08-MG{PS:FH1A}I:Ps1DCCT1-I'; 'SR:C08-MG{PS:FH2A}I:Ps1DCCT1-I'; 'SR:C08-MG{PS:FM1A}I:Ps1DCCT1-I'; 'SR:C09-MG{PS:FL1A}I:Ps1DCCT1-I'; 'SR:C09-MG{PS:FL2A}I:Ps1DCCT1-I'; 'SR:C09-MG{PS:FM1A}I:Ps1DCCT1-I'; 'SR:C10-MG{PS:FH1A}I:Ps1DCCT1-I'; 'SR:C10-MG{PS:FH2A}I:Ps1DCCT1-I'; 'SR:C10-MG{PS:FM1A}I:Ps1DCCT1-I'; 'SR:C11-MG{PS:FL1A}I:Ps1DCCT1-I'; 'SR:C11-MG{PS:FL2A}I:Ps1DCCT1-I'; 'SR:C11-MG{PS:FM1A}I:Ps1DCCT1-I'; 'SR:C12-MG{PS:FH1A}I:Ps1DCCT1-I'; 'SR:C12-MG{PS:FH2A}I:Ps1DCCT1-I'; 'SR:C12-MG{PS:FM1A}I:Ps1DCCT1-I'; 'SR:C13-MG{PS:FL1A}I:Ps1DCCT1-I'; 'SR:C13-MG{PS:FL2A}I:Ps1DCCT1-I'; 'SR:C13-MG{PS:FM1A}I:Ps1DCCT1-I'; 'SR:C14-MG{PS:FH1A}I:Ps1DCCT1-I'; 'SR:C14-MG{PS:FH2A}I:Ps1DCCT1-I'; 'SR:C14-MG{PS:FM1A}I:Ps1DCCT1-I'; 'SR:C15-MG{PS:FL1A}I:Ps1DCCT1-I'; 'SR:C15-MG{PS:FL2A}I:Ps1DCCT1-I'; 'SR:C15-MG{PS:FM1A}I:Ps1DCCT1-I'; 'SR:C16-MG{PS:FH1A}I:Ps1DCCT1-I'; 'SR:C16-MG{PS:FH2A}I:Ps1DCCT1-I'; 'SR:C16-MG{PS:FM1A}I:Ps1DCCT1-I'; 'SR:C17-MG{PS:FL1A}I:Ps1DCCT1-I'; 'SR:C17-MG{PS:FL2A}I:Ps1DCCT1-I'; 'SR:C17-MG{PS:FM1A}I:Ps1DCCT1-I'; 'SR:C18-MG{PS:FH1A}I:Ps1DCCT1-I'; 'SR:C18-MG{PS:FH2A}I:Ps1DCCT1-I'; 'SR:C18-MG{PS:FM1A}I:Ps1DCCT1-I'; 'SR:C19-MG{PS:FL1A}I:Ps1DCCT1-I'; 'SR:C19-MG{PS:FL2A}I:Ps1DCCT1-I'; 'SR:C19-MG{PS:FM1A}I:Ps1DCCT1-I'; 'SR:C20-MG{PS:FH1A}I:Ps1DCCT1-I'; 'SR:C20-MG{PS:FH2A}I:Ps1DCCT1-I'; 'SR:C20-MG{PS:FM1A}I:Ps1DCCT1-I'; 'SR:C21-MG{PS:FL1A}I:Ps1DCCT1-I'; 'SR:C21-MG{PS:FL2A}I:Ps1DCCT1-I'; 'SR:C21-MG{PS:FM1A}I:Ps1DCCT1-I'; 'SR:C22-MG{PS:FH1A}I:Ps1DCCT1-I'; 'SR:C22-MG{PS:FH2A}I:Ps1DCCT1-I'; 'SR:C22-MG{PS:FM1A}I:Ps1DCCT1-I'; 'SR:C23-MG{PS:FL1A}I:Ps1DCCT1-I'; 'SR:C23-MG{PS:FL2A}I:Ps1DCCT1-I'; 'SR:C23-MG{PS:FM1A}I:Ps1DCCT1-I'; 'SR:C24-MG{PS:FH1A}I:Ps1DCCT1-I'; 'SR:C24-MG{PS:FH2A}I:Ps1DCCT1-I'; 'SR:C24-MG{PS:FM1A}I:Ps1DCCT1-I'; 'SR:C25-MG{PS:FL1A}I:Ps1DCCT1-I'; 'SR:C25-MG{PS:FL2A}I:Ps1DCCT1-I'; 'SR:C25-MG{PS:FM1A}I:Ps1DCCT1-I'; 'SR:C26-MG{PS:FH1A}I:Ps1DCCT1-I'; 'SR:C26-MG{PS:FH2A}I:Ps1DCCT1-I'; 'SR:C26-MG{PS:FM1A}I:Ps1DCCT1-I'; 'SR:C27-MG{PS:FL1A}I:Ps1DCCT1-I'; 'SR:C27-MG{PS:FL2A}I:Ps1DCCT1-I'; 'SR:C27-MG{PS:FM1A}I:Ps1DCCT1-I'; 'SR:C28-MG{PS:FH1A}I:Ps1DCCT1-I'; 'SR:C28-MG{PS:FH2A}I:Ps1DCCT1-I'; 'SR:C28-MG{PS:FM1A}I:Ps1DCCT1-I'; 'SR:C29-MG{PS:FL1A}I:Ps1DCCT1-I'; 'SR:C29-MG{PS:FL2A}I:Ps1DCCT1-I'; 'SR:C29-MG{PS:FM1A}I:Ps1DCCT1-I'; 'SR:C30-MG{PS:FH1A}I:Ps1DCCT1-I'".split(';')
    ]
    matlab_mml_fcor_H_names = [
        name.replace("'", '').strip() for name in
        "'fh2g1c30a'; 'fm1g4c30a'; 'fl1g1c01a'; 'fl2g1c01a'; 'fm1g4c01a'; 'fh1g1c02a'; 'fh2g1c02a'; 'fm1g4c02a'; 'fl1g1c03a'; 'fl2g1c03a'; 'fm1g4c03a'; 'fh1g1c04a'; 'fh2g1c04a'; 'fm1g4c04a'; 'fl1g1c05a'; 'fl2g1c05a'; 'fm1g4c05a'; 'fh1g1c06a'; 'fh2g1c06a'; 'fm1g4c06a'; 'fl1g1c07a'; 'fl2g1c07a'; 'fm1g4c07a'; 'fh1g1c08a'; 'fh2g1c08a'; 'fm1g4c08a'; 'fl1g1c09a'; 'fl2g1c09a'; 'fm1g4c09a'; 'fh1g1c10a'; 'fh2g1c10a'; 'fm1g4c10a'; 'fl1g1c11a'; 'fl2g1c11a'; 'fm1g4c11a'; 'fh1g1c12a'; 'fh2g1c12a'; 'fm1g4c12a'; 'fl1g1c13a'; 'fl2g1c13a'; 'fm1g4c13a'; 'fh1g1c14a'; 'fh2g1c14a'; 'fm1g4c14a'; 'fl1g1c15a'; 'fl2g1c15a'; 'fm1g4c15a'; 'fh1g1c16a'; 'fh2g1c16a'; 'fm1g4c16a'; 'fl1g1c17a'; 'fl2g1c17a'; 'fm1g4c17a'; 'fh1g1c18a'; 'fh2g1c18a'; 'fm1g4c18a'; 'fl1g1c19a'; 'fl2g1c19a'; 'fm1g4c19a'; 'fh1g1c20a'; 'fh2g1c20a'; 'fm1g4c20a'; 'fl1g1c21a'; 'fl2g1c21a'; 'fm1g4c21a'; 'fh1g1c22a'; 'fh2g1c22a'; 'fm1g4c22a'; 'fl1g1c23a'; 'fl2g1c23a'; 'fm1g4c23a'; 'fh1g1c24a'; 'fh2g1c24a'; 'fm1g4c24a'; 'fl1g1c25a'; 'fl2g1c25a'; 'fm1g4c25a'; 'fh1g1c26a'; 'fh2g1c26a'; 'fm1g4c26a'; 'fl1g1c27a'; 'fl2g1c27a'; 'fm1g4c27a'; 'fh1g1c28a'; 'fh2g1c28a'; 'fm1g4c28a'; 'fl1g1c29a'; 'fl2g1c29a'; 'fm1g4c29a'; 'fh1g1c30a'".split(';')
    ]
    matlab_mml_fcor_V_pvrb_list = [
        pv.replace("'", '').strip() for pv in
        "'SR:C30-MG{PS:FH2A}I:Ps2DCCT1-I'; 'SR:C30-MG{PS:FM1A}I:Ps2DCCT1-I'; 'SR:C01-MG{PS:FL1A}I:Ps2DCCT1-I'; 'SR:C01-MG{PS:FL2A}I:Ps2DCCT1-I'; 'SR:C01-MG{PS:FM1A}I:Ps2DCCT1-I'; 'SR:C02-MG{PS:FH1A}I:Ps2DCCT1-I'; 'SR:C02-MG{PS:FH2A}I:Ps2DCCT1-I'; 'SR:C02-MG{PS:FM1A}I:Ps2DCCT1-I'; 'SR:C03-MG{PS:FL1A}I:Ps2DCCT1-I'; 'SR:C03-MG{PS:FL2A}I:Ps2DCCT1-I'; 'SR:C03-MG{PS:FM1A}I:Ps2DCCT1-I'; 'SR:C04-MG{PS:FH1A}I:Ps2DCCT1-I'; 'SR:C04-MG{PS:FH2A}I:Ps2DCCT1-I'; 'SR:C04-MG{PS:FM1A}I:Ps2DCCT1-I'; 'SR:C05-MG{PS:FL1A}I:Ps2DCCT1-I'; 'SR:C05-MG{PS:FL2A}I:Ps2DCCT1-I'; 'SR:C05-MG{PS:FM1A}I:Ps2DCCT1-I'; 'SR:C06-MG{PS:FH1A}I:Ps2DCCT1-I'; 'SR:C06-MG{PS:FH2A}I:Ps2DCCT1-I'; 'SR:C06-MG{PS:FM1A}I:Ps2DCCT1-I'; 'SR:C07-MG{PS:FL1A}I:Ps2DCCT1-I'; 'SR:C07-MG{PS:FL2A}I:Ps2DCCT1-I'; 'SR:C07-MG{PS:FM1A}I:Ps2DCCT1-I'; 'SR:C08-MG{PS:FH1A}I:Ps2DCCT1-I'; 'SR:C08-MG{PS:FH2A}I:Ps2DCCT1-I'; 'SR:C08-MG{PS:FM1A}I:Ps2DCCT1-I'; 'SR:C09-MG{PS:FL1A}I:Ps2DCCT1-I'; 'SR:C09-MG{PS:FL2A}I:Ps2DCCT1-I'; 'SR:C09-MG{PS:FM1A}I:Ps2DCCT1-I'; 'SR:C10-MG{PS:FH1A}I:Ps2DCCT1-I'; 'SR:C10-MG{PS:FH2A}I:Ps2DCCT1-I'; 'SR:C10-MG{PS:FM1A}I:Ps2DCCT1-I'; 'SR:C11-MG{PS:FL1A}I:Ps2DCCT1-I'; 'SR:C11-MG{PS:FL2A}I:Ps2DCCT1-I'; 'SR:C11-MG{PS:FM1A}I:Ps2DCCT1-I'; 'SR:C12-MG{PS:FH1A}I:Ps2DCCT1-I'; 'SR:C12-MG{PS:FH2A}I:Ps2DCCT1-I'; 'SR:C12-MG{PS:FM1A}I:Ps2DCCT1-I'; 'SR:C13-MG{PS:FL1A}I:Ps2DCCT1-I'; 'SR:C13-MG{PS:FL2A}I:Ps2DCCT1-I'; 'SR:C13-MG{PS:FM1A}I:Ps2DCCT1-I'; 'SR:C14-MG{PS:FH1A}I:Ps2DCCT1-I'; 'SR:C14-MG{PS:FH2A}I:Ps2DCCT1-I'; 'SR:C14-MG{PS:FM1A}I:Ps2DCCT1-I'; 'SR:C15-MG{PS:FL1A}I:Ps2DCCT1-I'; 'SR:C15-MG{PS:FL2A}I:Ps2DCCT1-I'; 'SR:C15-MG{PS:FM1A}I:Ps2DCCT1-I'; 'SR:C16-MG{PS:FH1A}I:Ps2DCCT1-I'; 'SR:C16-MG{PS:FH2A}I:Ps2DCCT1-I'; 'SR:C16-MG{PS:FM1A}I:Ps2DCCT1-I'; 'SR:C17-MG{PS:FL1A}I:Ps2DCCT1-I'; 'SR:C17-MG{PS:FL2A}I:Ps2DCCT1-I'; 'SR:C17-MG{PS:FM1A}I:Ps2DCCT1-I'; 'SR:C18-MG{PS:FH1A}I:Ps2DCCT1-I'; 'SR:C18-MG{PS:FH2A}I:Ps2DCCT1-I'; 'SR:C18-MG{PS:FM1A}I:Ps2DCCT1-I'; 'SR:C19-MG{PS:FL1A}I:Ps2DCCT1-I'; 'SR:C19-MG{PS:FL2A}I:Ps2DCCT1-I'; 'SR:C19-MG{PS:FM1A}I:Ps2DCCT1-I'; 'SR:C20-MG{PS:FH1A}I:Ps2DCCT1-I'; 'SR:C20-MG{PS:FH2A}I:Ps2DCCT1-I'; 'SR:C20-MG{PS:FM1A}I:Ps2DCCT1-I'; 'SR:C21-MG{PS:FL1A}I:Ps2DCCT1-I'; 'SR:C21-MG{PS:FL2A}I:Ps2DCCT1-I'; 'SR:C21-MG{PS:FM1A}I:Ps2DCCT1-I'; 'SR:C22-MG{PS:FH1A}I:Ps2DCCT1-I'; 'SR:C22-MG{PS:FH2A}I:Ps2DCCT1-I'; 'SR:C22-MG{PS:FM1A}I:Ps2DCCT1-I'; 'SR:C23-MG{PS:FL1A}I:Ps2DCCT1-I'; 'SR:C23-MG{PS:FL2A}I:Ps2DCCT1-I'; 'SR:C23-MG{PS:FM1A}I:Ps2DCCT1-I'; 'SR:C24-MG{PS:FH1A}I:Ps2DCCT1-I'; 'SR:C24-MG{PS:FH2A}I:Ps2DCCT1-I'; 'SR:C24-MG{PS:FM1A}I:Ps2DCCT1-I'; 'SR:C25-MG{PS:FL1A}I:Ps2DCCT1-I'; 'SR:C25-MG{PS:FL2A}I:Ps2DCCT1-I'; 'SR:C25-MG{PS:FM1A}I:Ps2DCCT1-I'; 'SR:C26-MG{PS:FH1A}I:Ps2DCCT1-I'; 'SR:C26-MG{PS:FH2A}I:Ps2DCCT1-I'; 'SR:C26-MG{PS:FM1A}I:Ps2DCCT1-I'; 'SR:C27-MG{PS:FL1A}I:Ps2DCCT1-I'; 'SR:C27-MG{PS:FL2A}I:Ps2DCCT1-I'; 'SR:C27-MG{PS:FM1A}I:Ps2DCCT1-I'; 'SR:C28-MG{PS:FH1A}I:Ps2DCCT1-I'; 'SR:C28-MG{PS:FH2A}I:Ps2DCCT1-I'; 'SR:C28-MG{PS:FM1A}I:Ps2DCCT1-I'; 'SR:C29-MG{PS:FL1A}I:Ps2DCCT1-I'; 'SR:C29-MG{PS:FL2A}I:Ps2DCCT1-I'; 'SR:C29-MG{PS:FM1A}I:Ps2DCCT1-I'; 'SR:C30-MG{PS:FH1A}I:Ps2DCCT1-I'".split(';')
    ]
    matlab_mml_fcor_V_names = [
        name.replace("'", '').strip() for name in
        "'fh2g1c30a'; 'fm1g4c30a'; 'fl1g1c01a'; 'fl2g1c01a'; 'fm1g4c01a'; 'fh1g1c02a'; 'fh2g1c02a'; 'fm1g4c02a'; 'fl1g1c03a'; 'fl2g1c03a'; 'fm1g4c03a'; 'fh1g1c04a'; 'fh2g1c04a'; 'fm1g4c04a'; 'fl1g1c05a'; 'fl2g1c05a'; 'fm1g4c05a'; 'fh1g1c06a'; 'fh2g1c06a'; 'fm1g4c06a'; 'fl1g1c07a'; 'fl2g1c07a'; 'fm1g4c07a'; 'fh1g1c08a'; 'fh2g1c08a'; 'fm1g4c08a'; 'fl1g1c09a'; 'fl2g1c09a'; 'fm1g4c09a'; 'fh1g1c10a'; 'fh2g1c10a'; 'fm1g4c10a'; 'fl1g1c11a'; 'fl2g1c11a'; 'fm1g4c11a'; 'fh1g1c12a'; 'fh2g1c12a'; 'fm1g4c12a'; 'fl1g1c13a'; 'fl2g1c13a'; 'fm1g4c13a'; 'fh1g1c14a'; 'fh2g1c14a'; 'fm1g4c14a'; 'fl1g1c15a'; 'fl2g1c15a'; 'fm1g4c15a'; 'fh1g1c16a'; 'fh2g1c16a'; 'fm1g4c16a'; 'fl1g1c17a'; 'fl2g1c17a'; 'fm1g4c17a'; 'fh1g1c18a'; 'fh2g1c18a'; 'fm1g4c18a'; 'fl1g1c19a'; 'fl2g1c19a'; 'fm1g4c19a'; 'fh1g1c20a'; 'fh2g1c20a'; 'fm1g4c20a'; 'fl1g1c21a'; 'fl2g1c21a'; 'fm1g4c21a'; 'fh1g1c22a'; 'fh2g1c22a'; 'fm1g4c22a'; 'fl1g1c23a'; 'fl2g1c23a'; 'fm1g4c23a'; 'fh1g1c24a'; 'fh2g1c24a'; 'fm1g4c24a'; 'fl1g1c25a'; 'fl2g1c25a'; 'fm1g4c25a'; 'fh1g1c26a'; 'fh2g1c26a'; 'fm1g4c26a'; 'fl1g1c27a'; 'fl2g1c27a'; 'fm1g4c27a'; 'fh1g1c28a'; 'fh2g1c28a'; 'fm1g4c28a'; 'fl1g1c29a'; 'fl2g1c29a'; 'fm1g4c29a'; 'fh1g1c30a'".split(';')
    ]
    # ^ It turned out that the M-file's PV lists are also wrong. Some of them
    #   do not even exist.

    # Later Xi sent me the correct PV's sorted in the order of s-position
    xi_fcor_csv = np.loadtxt('FCORmapforYoshi.csv', dtype=str, delimiter=',')
    xi_fcor_spos   = [float(d[0]) for d in xi_fcor_csv]
    xi_fcor_pvs    = [d[1] for d in xi_fcor_csv]
    xi_fcor_enames = [d[2] for d in xi_fcor_csv]
    try: ap.caget(xi_fcor_pvs)
    except: pass

    fcors = ap.getElements('FCOR')
    existing_ap_fcor_names = [e.name for e in fcors]
    existing_ap_fcor_H_pvrbs = [e.pv(field='x', handle='readback')[0] for e in fcors]


    if False:
        assert len(matlab_mml_fcor_H_names) == len(matlab_mml_fcor_H_pvrb_list) == len(fcors)
        assert len(matlab_mml_fcor_V_names) == len(matlab_mml_fcor_V_pvrb_list) == len(fcors)
        assert matlab_mml_fcor_H_names == matlab_mml_fcor_V_names
        assert existing_ap_fcor_names == matlab_mml_fcor_H_names

        if existing_ap_fcor_H_pvrbs == matlab_mml_fcor_H_pvrb_list:
            print('\n\nPV orders for fast correctors are already correct.')
            print('So, not changing the aphla database.')
            return

        tags = ['aphla.sys.SR']

        fld, hdl = 'x', 'get'
        for elemName, pv in zip(existing_ap_fcor_names, matlab_mml_fcor_H_pvrb_list):
            ap.apdata.updateDbPv(DBFILE, pv, elemName, fld,
                                 elemHandle=hdl, tags=tags, quiet=True)

        fld, hdl = 'y', 'get'
        for elemName, pv in zip(existing_ap_fcor_names, matlab_mml_fcor_V_pvrb_list):
            ap.apdata.updateDbPv(DBFILE, pv, elemName, fld,
                                 elemHandle=hdl, tags=tags, quiet=True)

        fld, hdl = 'x', 'put'
        for elemName, pv in zip(existing_ap_fcor_names, matlab_mml_fcor_H_pvrb_list):
            ap.apdata.updateDbPv(
                DBFILE, pv.replace('Ps1DCCT1-I', 'Sp1-SP'), elemName, fld,
                elemHandle=hdl, tags=tags, quiet=True)

        fld, hdl = 'y', 'put'
        for elemName, pv in zip(existing_ap_fcor_names, matlab_mml_fcor_V_pvrb_list):
            ap.apdata.updateDbPv(
                DBFILE, pv.replace('Ps2DCCT1-I', 'Sp2-SP'), elemName, fld,
                elemHandle=hdl, tags=tags, quiet=True)

        fld, hdl = 'x2', 'get'
        for elemName, pv in zip(existing_ap_fcor_names, matlab_mml_fcor_H_pvrb_list):
            ap.apdata.updateDbPv(
                DBFILE, pv.replace('I:Ps1DCCT1-I', 'DAC1Cnt-Sts'), elemName, fld,
                elemHandle=hdl, tags=tags, quiet=True)

        fld, hdl = 'y2', 'get'
        for elemName, pv in zip(existing_ap_fcor_names, matlab_mml_fcor_V_pvrb_list):
            ap.apdata.updateDbPv(
                DBFILE, pv.replace('I:Ps2DCCT1-I', 'DAC2Cnt-Sts'), elemName, fld,
                elemHandle=hdl, tags=tags, quiet=True)
    else:
        assert existing_ap_fcor_names == xi_fcor_enames
        assert len(existing_ap_fcor_names) == len(xi_fcor_pvs)

        for e, xi_s in zip(fcors, xi_fcor_spos):
            print((e.sb + e.se)/2.0 - xi_s)

        tags = ['aphla.sys.SR']

        fld, hdl = 'x', 'put'
        for elemName, pv in zip(existing_ap_fcor_names, xi_fcor_pvs):
            ap.apdata.updateDbPv(DBFILE, pv, elemName, fld,
                                 elemHandle=hdl, tags=tags, quiet=True)

        fld, hdl = 'y', 'put'
        for elemName, pv in zip(existing_ap_fcor_names, xi_fcor_pvs):
            ap.apdata.updateDbPv(
                DBFILE, pv.replace('Sp1-SP', 'Sp2-SP'), elemName, fld,
                elemHandle=hdl, tags=tags, quiet=True)

        fld, hdl = 'x', 'get'
        for elemName, pv in zip(existing_ap_fcor_names, xi_fcor_pvs):
            ap.apdata.updateDbPv(
                DBFILE, pv.replace('Sp1-SP', 'Ps1DCCT1-I'), elemName, fld,
                elemHandle=hdl, tags=tags, quiet=True)

        fld, hdl = 'y', 'get'
        for elemName, pv in zip(existing_ap_fcor_names, xi_fcor_pvs):
            ap.apdata.updateDbPv(
                DBFILE, pv.replace('Sp1-SP', 'Ps2DCCT1-I'), elemName, fld,
                elemHandle=hdl, tags=tags, quiet=True)

        fld, hdl = 'x2', 'get'
        for elemName, pv in zip(existing_ap_fcor_names, xi_fcor_pvs):
            ap.apdata.updateDbPv(
                DBFILE, pv.replace('I:Sp1-SP', 'DAC1Cnt-Sts'), elemName, fld,
                elemHandle=hdl, tags=tags, quiet=True)

        fld, hdl = 'y2', 'get'
        for elemName, pv in zip(existing_ap_fcor_names, xi_fcor_pvs):
            ap.apdata.updateDbPv(
                DBFILE, pv.replace('I:Sp1-SP', 'DAC2Cnt-Sts'), elemName, fld,
                elemHandle=hdl, tags=tags, quiet=True)

#----------------------------------------------------------------------
def update_fcors_unitconv():
    """"""

    kw = dict(compression='gzip')

    _temp_unitconv_file = UNITCONV_FILE + '.tmp'

    fnew = h5py.File(_temp_unitconv_file, 'w')
    fold = h5py.File(UNITCONV_FILE, 'r')

    # First copy existing unit conversion data
    gold = fold['UnitConversion']
    gnew = fnew.create_group('UnitConversion')
    for k, v in gold.items():

        if False: # This will end up with bigger file size
            d = gnew.create_dataset(k, data=v.value, **kw)
        else: # This will end up with smaller file size, so use this one!
            gnew[k] = v.value
            d = gnew[k]

        for ak, av in v.attrs.items():
            put_h5py_attr(d, ak, av)

    # Adding new unit conversions
    #
    '''
    Email sent to Yuke on 11/28/2016 3:17 PM:

    From fitting, the estimated unit conversions are 14.6 urad/Amp horizontally
    and 13.4 urad/Amp vertically.

    -Yoshi

    From: Tian, Yuke
    Sent: Monday, November 28, 2016 3:02 PM
    To: Hidaka, Yoshiteru
    Subject: RE: FOFB response matrix

    Hi Yoshi,

    Good to know the matrix agree. I don't have a precise unit conversion sine
    I directly applied the Amp to mm. The rough conversion should be 1.25A for
    15urad for both planes. How much differences do you see for H and V planes?

    Thanks,

    -Yuke

    '''
    group_name = 'FCOR'
    #
    # TODO: Need to check the sign of physics unit
    # TODO: May need to switch to unit conversions estimated from measured ORM
    d = gnew.create_dataset(group_name+'_x', data=np.array([15e-6/1.25*1e3, 0.0]), **kw)
    uc = {'_class_': 'polynomial', 'dst_unit': 'mrad', 'dst_unit_sys': 'phy',
          'groups': [group_name], 'field': 'x', 'handle': ['readback','setpoint'],
          'invertible': 1, 'src_unit': 'A', 'src_unit_sys': ''}
    for k, v in uc.items(): put_h5py_attr(d, k, v)
    #
    d = gnew.create_dataset(group_name+'_y', data=np.array([15e-6/1.25*1e3, 0.0]), **kw)
    uc = {'_class_': 'polynomial', 'dst_unit': 'mrad', 'dst_unit_sys': 'phy',
          'groups': [group_name], 'field': 'y', 'handle': ['readback','setpoint'],
          'invertible': 1, 'src_unit': 'A', 'src_unit_sys': ''}
    for k, v in uc.items(): put_h5py_attr(d, k, v)
    #
    # Unit conversion from counts to Amps:
    # I [A] = (counts - 524280) / 524280 * 1.25
    d = gnew.create_dataset(group_name+'_x2_rb', data=np.array([1.25 / 524280, -1.25]), **kw)
    uc = {'_class_': 'polynomial', 'dst_unit': 'A', 'dst_unit_sys': 'eng',
          'groups': [group_name], 'field': 'x2', 'handle': ['readback'],
          'invertible': 1, 'src_unit': 'count', 'src_unit_sys': ''}
    for k, v in uc.items(): put_h5py_attr(d, k, v)
    #
    # Unit conversion from counts to Amps:
    # I [A] = (counts - 524280) / 524280 * 1.25
    d = gnew.create_dataset(group_name+'_y2_rb', data=np.array([1.25 / 524280, -1.25]), **kw)
    uc = {'_class_': 'polynomial', 'dst_unit': 'A', 'dst_unit_sys': 'eng',
          'groups': [group_name], 'field': 'y2', 'handle': ['readback'],
          'invertible': 1, 'src_unit': 'count', 'src_unit_sys': ''}
    for k, v in uc.items(): put_h5py_attr(d, k, v)


    fold.close()
    fnew.close()

    shutil.move(_temp_unitconv_file, UNITCONV_FILE)

#----------------------------------------------------------------------
def test_idlocalbump():
    """"""

    #ap.machines.load('nsls2', 'SR')
    ap.machines.loadfast('nsls2', 'SR')

    sys.path.insert(0, '/epics/iocs/srSOFB2/sofb2')
    import idlocalbump

    pvmaps = []
    for mac in idlocalbump._id_macros:
        pvls = [(k,mac[k]) for k in ("idname", "bpm1", "bpm2", "XY")]
        for k,v in idlocalbump._tmpl.items():
            pv = v.format(**mac)
            pvls.append((k, pv))
        pvdict = dict(pvls)
        #print (k, pv, caget(pv))
        bpm = ap.getElements(pvdict["bpm1"])[0]
        if mac["HV"] == "H" and pvdict["hv1"] != bpm.pv(field="xref1")[0]:
            print(bpm.name, mac["HV"], pvdict["hv1"], bpm.pv(field="xref1")[0])
        pvmaps.append(pvdict)

    plt.show()

#----------------------------------------------------------------------
def show_link_btw_wrong_vs_correct_fcor_indexes():
    """"""

    wrong = np.loadtxt('fcor_elem_pvs.txt', dtype=str)

    wrong_name_list = wrong[:,1].tolist()
    wrong_pvs = []
    for e in ap.getElements('FCOR'):
        wrong_pvs.append(wrong[wrong_name_list.index(e.name), 0])

    correct_pvs = [e.pv(field='x', handle='readback')[0]
                   for e in ap.getElements('FCOR')]

    pprint.pprint(
        list(zip(range(len(correct_pvs)),
            [wrong_pvs.index(pv) for pv in correct_pvs])))

    plt.figure()
    plt.plot(list(range(len(correct_pvs))),
             [wrong_pvs.index(pv) for pv in correct_pvs], '.-')
    plt.grid(True)

    plt.show()

#----------------------------------------------------------------------
def add_new_SQ_at_C16_for_AMX_coup_compensation():
    """"""

    # Add new skew quad installed at C16 CL1B corrector
    new_sq_name = 'SQLHG6C16B'.lower()
    elemLength = 0.2 # [m]
    elemName, sEnd = new_sq_name, 444.607 + elemLength/2.0
    kw = dict(elemType = 'SKQUAD',
              cell       = 'C16',
              girder     = 'G6',
              symmetry   = 'B',
              elemGroups = 'SQLH',
              elemIndex  = 162700,
              elemLength = elemLength,
              )
    ap.apdata.updateDbElement(DBFILE, 'SR', elemName, elemPosition=sEnd, **kw)

    # Make C16-CL1 corrector "thin", centered at middle of C16-SQL created above
    elemName, sEnd = 'CL1G6C16B'.lower(), 444.607
    kw = dict(elemLength = 0.0)
    ap.apdata.updateDbElement(DBFILE, 'SR', elemName, elemPosition=sEnd, **kw)

    ap.machines.load('nsls2', 'SR')

    # Add PVs for the newly added skew quad

    elemName = new_sq_name

    tags = ['aphla.sys.SR']

    fld, hdl = 'b1', 'put'
    pv = 'SR:C16-MG{PS:SQKL1B}I:Sp1-SP'
    ap.apdata.updateDbPv(DBFILE, pv, elemName, fld,
                         elemHandle=hdl, tags=tags, quiet=True, epsilon=0.1)

    fld, hdl = 'b1_2nd', 'put'
    pv = 'SR:C16-MG{PS:SQKL1B}I:Sp1_2-SP'
    ap.apdata.updateDbPv(DBFILE, pv, elemName, fld,
                         elemHandle=hdl, tags=tags, quiet=True, epsilon=0.1)

    fld, hdl = 'b1', 'get'
    pv = 'SR:C16-MG{PS:SQKL1B}I:Ps1DCCT1-I'
    ap.apdata.updateDbPv(DBFILE, pv, elemName, fld,
                         elemHandle=hdl, tags=tags, quiet=True, epsilon=0.1)

    fld, hdl = 'ramping', 'get'
    pv = 'SR:C16-MG{PS:SQKL1B}RpStart1-Cmd'
    ap.apdata.updateDbPv(DBFILE, pv, elemName, fld,
                         elemHandle=hdl, tags=tags, quiet=True, epsilon=0.0)


    if False: #True: # This section can only run once, as HDF5 file does not
                     # allow overwrite of existing datasets

        # Adding new unit conversions

        kw = dict(compression='gzip')

        _temp_unitconv_file = UNITCONV_FILE + '.tmp'

        fnew = h5py.File(_temp_unitconv_file, 'w')
        fold = h5py.File(UNITCONV_FILE, 'r')

        # First copy existing unit conversion data
        gold = fold['UnitConversion']
        gnew = fnew.create_group('UnitConversion')
        for k, v in gold.items():

            if False: # This will end up with bigger file size
                d = gnew.create_dataset(k, data=v.value, **kw)
            else: # This will end up with smaller file size, so use this one!
                gnew[k] = v.value
                d = gnew[k]

            for ak, av in v.attrs.items():
                put_h5py_attr(d, ak, av)

        group_name = 'SKQUAD'
        #
        d = gnew.create_dataset(group_name+'_b1_2nd', data=np.array([3.968e-4, 0.0]), **kw)
        uc = {'_class_': 'polynomial', 'dst_unit': 'm^{-1}', 'dst_unit_sys': 'phy',
              'groups': [group_name], 'field': 'b1_2nd', 'handle': ['readback','setpoint'],
              'invertible': 1, 'src_unit': 'A', 'src_unit_sys': ''}
        for k, v in uc.items(): put_h5py_attr(d, k, v)


        fold.close()
        fnew.close()

        shutil.move(_temp_unitconv_file, UNITCONV_FILE)
        # Need to do manually "$ chmod 777 sr_unitconv.hdf5" on terminal

#----------------------------------------------------------------------
def add_2nd_channels_to_all_SQH_skew_quads():
    """
    Note that SQM families do NOT have 2nd setpoint channels (as of 05/17/2017)
    """

    tags = ['aphla.sys.SR']

    fld, hdl = 'b1_2nd', 'put'
    for e in ap.getElements('sqh*'):
        elemName = e.name
        pv = e.pv(field='b1', handle='setpoint')[0].replace('I:Sp1-SP', 'I:Sp1_2-SP')
        ap.apdata.updateDbPv(DBFILE, pv, elemName, fld,
                             elemHandle=hdl, tags=tags, quiet=True, epsilon=0.1)

#----------------------------------------------------------------------
def add_2nd_channels_to_cors():
    """
    (as of 05/26/2017)
    # start_time_str = '2017-05-25 20:00:00'
    # end_time_str   = '2017-05-25 20:00:01'
    # import nsls2.util.archiver as archiver
    # >> pattern = 'SR:C[0-3]\d-MG{PS:C[HLM]\d[AB]}I:Sp\d_2-SP'
    # >> d = archiver.get_archived_data(start_time_str, end_time_str, pattern)
    # >> sorted(list(d['vals']))
    #['SR:C07-MG{PS:CH1B}I:Sp1_2-SP',
     #'SR:C07-MG{PS:CH1B}I:Sp2_2-SP',
     #'SR:C08-MG{PS:CH1A}I:Sp1_2-SP',
     #'SR:C08-MG{PS:CH1A}I:Sp2_2-SP',
     #'SR:C17-MG{PS:CH1B}I:Sp1_2-SP',
     #'SR:C17-MG{PS:CH1B}I:Sp2_2-SP',
     #'SR:C18-MG{PS:CH1A}I:Sp1_2-SP',
     #'SR:C18-MG{PS:CH1A}I:Sp2_2-SP',
     #'SR:C22-MG{PS:CL1B}I:Sp1_2-SP',
     #'SR:C22-MG{PS:CL1B}I:Sp2_2-SP',
     #'SR:C23-MG{PS:CL1A}I:Sp1_2-SP',
     #'SR:C23-MG{PS:CL1A}I:Sp2_2-SP',
     #'SR:C27-MG{PS:CH1B}I:Sp1_2-SP',
     #'SR:C27-MG{PS:CH1B}I:Sp2_2-SP',
     #'SR:C28-MG{PS:CH1A}I:Sp1_2-SP',
     #'SR:C28-MG{PS:CH1A}I:Sp2_2-SP']

    cors = ap.getElements('COR')
    cors[0].getEpsilon('x')
    >> 0.01
    cors[0].getEpsilon('y')
    >> 0.01

    """

    tags = ['aphla.sys.SR']

    cors = ap.getElements(['ch1g6c07b', 'ch1g2c08a', 'ch1g6c17b', 'ch1g2c18a',
                           'ch1g6c27b', 'ch1g2c28a', 'cl1g6c22b', 'cl1g2c23a'])

    fld, hdl = 'x_2nd', 'put'
    for e in cors:
        elemName = e.name
        pv = e.pv(field='x', handle='setpoint')[0].replace('I:Sp1-SP', 'I:Sp1_2-SP')
        ap.apdata.updateDbPv(DBFILE, pv, elemName, fld,
                             elemHandle=hdl, tags=tags, quiet=True, epsilon=0.01)

    fld, hdl = 'y_2nd', 'put'
    for e in cors:
        elemName = e.name
        pv = e.pv(field='y', handle='setpoint')[0].replace('I:Sp2-SP', 'I:Sp2_2-SP')
        ap.apdata.updateDbPv(DBFILE, pv, elemName, fld,
                             elemHandle=hdl, tags=tags, quiet=True, epsilon=0.01)

    if False: #True: # This section can only run once, as HDF5 file does not
                     # allow overwrite of existing datasets

        # Adding new unit conversions

        kw = dict(compression='gzip')

        _temp_unitconv_file = UNITCONV_FILE + '.tmp'

        fnew = h5py.File(_temp_unitconv_file, 'w')
        fold = h5py.File(UNITCONV_FILE, 'r')

        # First copy existing unit conversion data
        gold = fold['UnitConversion']
        gnew = fnew.create_group('UnitConversion')
        for k, v in gold.items():

            if False: # This will end up with bigger file size
                d = gnew.create_dataset(k, data=v.value, **kw)
            else: # This will end up with smaller file size, so use this one!
                gnew[k] = v.value
                d = gnew[k]

            for ak, av in v.attrs.items():
                put_h5py_attr(d, ak, av)

        key_list = ['SR-MG-CRR-1000_H', 'SR-MG-CRR-1001_H', 'SR-MG-CRR-1560_H',
                    'SR-MG-CRR-1000_V', 'SR-MG-CRR-1001_V', 'SR-MG-CRR-1560_V',]
        for old_key in key_list:
            d = gnew.create_dataset(old_key+'_2nd_Ch', data=gold[old_key].value, **kw)
            uc = {}
            for k, v in gold[old_key].attrs.items(): uc[k] = v
            if old_key.endswith('H'):
                uc['field'] = 'x_2nd'
            elif old_key.endswith('V'):
                uc['field'] = 'y_2nd'
            for k, v in uc.items(): put_h5py_attr(d, k, v)


        fold.close()
        fnew.close()

        shutil.move(_temp_unitconv_file, UNITCONV_FILE)

#----------------------------------------------------------------------
def correct_C04_C05_C17_straight_spos_C04_C12_group():
    """"""

    # Update s-pos of ID BPMs in C04

    ubpms = ap.getElements('pu*c04a')

    new_spos = [101.6784, 106.9044, 107.0744, 109.6414]

    assert len(ubpms) == len(new_spos)
    for e, sEnd in zip(ubpms, new_spos):
        kw = dict(elemType   = e.family,
                  cell       = e.cell,
                  girder     = e.girder,
                  symmetry   = e.symmetry,
                  elemGroups = ';'.join([
                      s for s in e.group
                      if s not in (e.cell, e.family, e.girder, e.symmetry)]),
                  elemIndex  = e.index,
                  elemLength = e.length,
                  )
        ap.apdata.updateDbElement(DBFILE, 'SR', e.name, elemPosition=sEnd, **kw)

    # Update s-pos of C04 upstream ID & add "NEXT" to group

    e = ap.getElements('ivu23g1c04u')[0]

    elemLength = e.length # [m]
    elemName, sEnd = e.name, 106.3934
    kw = dict(elemType   = e.family,
              cell       = e.cell,
              girder     = e.girder,
              symmetry   = e.symmetry,
              elemGroups = 'IVU23;ID;NEXT',
              elemIndex  = e.index,
              elemLength = e.length,
              )
    ap.apdata.updateDbElement(DBFILE, 'SR', e.name, elemPosition=sEnd, **kw)

    # Update s-pos of ID BPMs in C05

    ubpms = ap.getElements('pu*c05a')

    new_spos = [129.304, 131.912, 134.818]

    assert len(ubpms) == len(new_spos)
    for e, sEnd in zip(ubpms, new_spos):
        kw = dict(elemType   = e.family,
                  cell       = e.cell,
                  girder     = e.girder,
                  symmetry   = e.symmetry,
                  elemGroups = ';'.join([
                      s for s in e.group
                      if s not in (e.cell, e.family, e.girder, e.symmetry)]),
                  elemIndex  = e.index,
                  elemLength = e.length,
                  )
        ap.apdata.updateDbElement(DBFILE, 'SR', e.name, elemPosition=sEnd, **kw)


    # Add "NEXT" to group for C12 downstream ID

    e = ap.getElements('ivu23g1c12d')[0]

    elemLength = e.length # [m]
    elemName, sEnd = e.name, e.se
    kw = dict(elemType   = e.family,
              cell       = e.cell,
              girder     = e.girder,
              symmetry   = e.symmetry,
              elemGroups = 'IVU23;ID;NEXT',
              elemIndex  = e.index,
              elemLength = e.length,
              )
    ap.apdata.updateDbElement(DBFILE, 'SR', e.name, elemPosition=sEnd, **kw)


    ap.machines.load('nsls2', 'SR')

#----------------------------------------------------------------------
def correct_gap_readback_phy_unit_for_some_IVUs():
    """
    Correct ID04-1, ID12-2, ID16, ID17-1, and ID17-2 physics unit to "mm"
    """

    kw = dict(compression='gzip')

    _temp_unitconv_file = UNITCONV_FILE + '.tmp'

    fnew = h5py.File(_temp_unitconv_file, 'w')
    fold = h5py.File(UNITCONV_FILE, 'r')

    # First copy existing unit conversion data
    gold = fold['UnitConversion']
    gnew = fnew.create_group('UnitConversion')
    for k, v in gold.items():

        if False: # This will end up with bigger file size
            d = gnew.create_dataset(k, data=v.value, **kw)
        else: # This will end up with smaller file size, so use this one!
            gnew[k] = v.value
            d = gnew[k]

        for ak, av in v.attrs.items():
            put_h5py_attr(d, ak, av)

    # Adding new unit conversions
    #
    # ### Note that the new dataset name had to be named such that this new
    # dataset appears later than the existing "ID_IVU_gap_rb" dataset
    # in the newly created HDF5 file. Apparently, aphla will load the unit
    # conversion in the order of datasets, and hence the later ones will
    # overwrite if elements satisfy the given matching conditions. ##
    #
    d = gnew.create_dataset('ID_ivu_c04u_c12d_c16c_c17ud_gap_rb',
                            data=np.array([1.0, 0.0]), **kw)
    uc = {'_class_': 'polynomial', 'dst_unit': 'mm', 'dst_unit_sys': 'phy',
          'elements': ['ivu23g1c04u','ivu23g1c12d','ivu23g1c16c',
                       'ivu21g1c17u','ivu21g1c17d'],
          'field': 'gap', 'handle': ['readback'],
          'invertible': 1, 'src_unit': 'mm', 'src_unit_sys': ''}
    for k, v in uc.items(): put_h5py_attr(d, k, v)

    fold.close()
    fnew.close()

    shutil.move(_temp_unitconv_file, UNITCONV_FILE)

#----------------------------------------------------------------------
def add_cch0rb1_for_all_IDs():
    """"""

    ap.machines.loadfast('nsls2', 'SR')

    ids = ap.getElements('ID')

    tags = ['aphla.sys.SR']

    for e in ids:

        hdl = 'get'

        all_fields = e.fields()

        for iCch in range(6):
            fld = 'cch{0:d}'.format(iCch)
            if fld not in all_fields:
                break

            new_fld = fld + 'rb1'

            pv = e.pv(field=fld, handle='readback')[0]

            if pv.endswith('readback'):
                new_pv = pv.replace('readback', 'current')
                eps = 10.0 # [mA]
            elif pv.endswith('Loop-I'):
                new_pv = pv.replace('Loop-I', '-I-I')
                eps = 0.01 # [A]
            else:
                raise ValueError()

            ap.apdata.updateDbPv(
                DBFILE, new_pv, e.name, new_fld,
                elemHandle=hdl, tags=tags, quiet=True, epsilon=eps)

#----------------------------------------------------------------------
def add_unitconv_to_ID_cch():
    """"""

    if False: #True: # This section can only run once, as HDF5 file does not
                     # allow overwrite of existing datasets

        kw = dict(compression='gzip')

        _temp_unitconv_file = UNITCONV_FILE + '.tmp'

        fnew = h5py.File(_temp_unitconv_file, 'w')
        fold = h5py.File(UNITCONV_FILE, 'r')

        # First copy existing unit conversion data
        gold = fold['UnitConversion']
        gnew = fnew.create_group('UnitConversion')
        for k, v in gold.items():

            if False: # This will end up with bigger file size
                d = gnew.create_dataset(k, data=v.value, **kw)
            else: # This will end up with smaller file size, so use this one!
                gnew[k] = v.value
                d = gnew[k]

            for ak, av in v.attrs.items():
                put_h5py_attr(d, ak, av)

        # Adding new unit conversions

        ap.machines.loadfast('nsls2', 'SR')

        ids = ap.getElements('ID')

        for iCh in range(6):

            fld = 'cch{0:d}'.format(iCh)

            cch_v1_elemNames, cch_v2_elemNames = [], []
            for e in ids:
                if fld not in e.fields(): continue

                pv = e.pv(field=fld, handle='readback')[0]

                if pv.endswith('readback'):
                    cch_v1_elemNames.append(e.name)
                elif pv.endswith('Loop-I'):
                    cch_v2_elemNames.append(e.name)
                else:
                    raise ValueError()

            d = gnew.create_dataset(
                'ID_{0}_v1'.format(fld), data=np.array([1e-5, 0.0]), **kw)
            uc = {'_class_': 'polynomial', 'dst_unit': 'A', 'dst_unit_sys': 'phy',
                  'elements': cch_v1_elemNames, 'field': fld,
                  'handle': ['setpoint','readback'],
                  'invertible': 1, 'src_unit': '10uA', 'src_unit_sys': ''}
            for k, v in uc.items(): put_h5py_attr(d, k, v)

            d = gnew.create_dataset(
                'ID_{0}_v2'.format(fld), data=np.array([1.0, 0.0]), **kw)
            uc = {'_class_': 'polynomial', 'dst_unit': 'A', 'dst_unit_sys': 'phy',
                  'elements': cch_v2_elemNames, 'field': fld,
                  'handle': ['setpoint','readback'],
                  'invertible': 1, 'src_unit': 'A', 'src_unit_sys': ''}
            for k, v in uc.items(): put_h5py_attr(d, k, v)

            rb1_fld = fld + 'rb1'

            d = gnew.create_dataset(
                'ID_{0}_v1'.format(rb1_fld), data=np.array([1e-3, 0.0]), **kw)
            uc = {'_class_': 'polynomial', 'dst_unit': 'A', 'dst_unit_sys': 'phy',
                  'elements': cch_v1_elemNames, 'field': rb1_fld,
                  'handle': ['readback'],
                  'invertible': 1, 'src_unit': 'mA', 'src_unit_sys': ''}
            for k, v in uc.items(): put_h5py_attr(d, k, v)

            d = gnew.create_dataset(
                'ID_{0}_v2'.format(rb1_fld), data=np.array([1.0, 0.0]), **kw)
            uc = {'_class_': 'polynomial', 'dst_unit': 'A', 'dst_unit_sys': 'phy',
                  'elements': cch_v2_elemNames, 'field': rb1_fld,
                  'handle': ['readback'],
                  'invertible': 1, 'src_unit': 'A', 'src_unit_sys': ''}
            for k, v in uc.items(): put_h5py_attr(d, k, v)

        fold.close()
        fnew.close()

        shutil.move(_temp_unitconv_file, UNITCONV_FILE)

#----------------------------------------------------------------------
def add_orbit_ff_pvs():
    """
    """

    ap.machines.loadfast('nsls2', 'SR')

    tags = ['aphla.sys.SR']

    """
    import idcomm # ~/hg_repos/nsls2scripts/idcomm/idcomm.py

    id_index = 0
    e = ap.getElements('ID')[id_index]
    enable_pvs = idcomm.getFFEnablePVs(e, idcomm.ALL_RESP_CORNAME_CORFLD[e.name])

    For DWs:
    enable_pvs = idcomm.getFFEnablePVs(
        ap.getElements('dw100g1c08u')[0],
        idcomm.ALL_RESP_CORNAME_CORFLD['dw100g1c08c_reg'])
    enable_pvs = idcomm.getFFEnablePVs(
        ap.getElements('dw100g1c18u')[0],
        idcomm.ALL_RESP_CORNAME_CORFLD['dw100g1c18c_reg'])
    enable_pvs = idcomm.getFFEnablePVs(
        ap.getElements('dw100g1c28u')[0],
        idcomm.ALL_RESP_CORNAME_CORFLD['dw100g1c28c_reg'])
    """

    enable_pvs = {
        'epu57g1c02c':
        ['SR:C02-ID:G1A{EPU:1-FF:%d}Ena-Sel' % i for i in range(6)],
        'ivu20g1c03c':
        ['SR:C3-ID:G1{IVU20:1-FF:%d}Ena-Sel' % i for i in range(6)],
        'ivu23g1c04u':
        ['SR:C04-ID:G1{IVU:1-FF:%d}Ena-Sel' % i for i in range(6)],
        'ivu21g1c05d':
        ['SR:C5-ID:G1{IVU21:1-FF:%d}Ena-Sel' % i for i in range(6)],
        'dw100g1c08u':
        ['SR:C08-ID:G1{DW100:1-FF:%d}Ena-Sel' % i for i in range(6)] +
        ['SR:C08-ID:G1{DW100:2-FF:%d}Ena-Sel' % i for i in range(6)] +
        ['SR:C08-ID:G1{DW100:1-VCor:%d}Ena-Sel' % i for i in range(2)],
        'dw100g1c08d':
        ['SR:C08-ID:G1{DW100:1-FF:%d}Ena-Sel' % i for i in range(6)] +
        ['SR:C08-ID:G1{DW100:2-FF:%d}Ena-Sel' % i for i in range(6)] +
        ['SR:C08-ID:G1{DW100:1-VCor:%d}Ena-Sel' % i for i in range(2)],
        'ivu22g1c10c':
        ['SR:C10-ID:G1{IVU22:1-FF:%d}Ena-Sel' % i for i in range(4)],
        'ivu20g1c11c':
        ['SR:C11-ID:G1{IVU20:1-FF:%d}Ena-Sel' % i for i in range(6)],
        'ivu23g1c12d':
        ['SR:C12-ID:G1{IVU:1-FF:%d}Ena-Sel' % i for i in range(6)],
        'ivu23g1c16c':
        ['SR:C16-ID:G1{IVU:1-FF:%d}Ena-Sel' % i for i in range(6)],
        'ivu21g1c17u':
        ['SR:C17-ID:G1{IVU21:1-FF:%d}Ena-Sel' % i for i in range(6)],
        'ivu21g1c17d':
        ['SR:C17-ID:G1{IVU21:2-FF:%d}Ena-Sel' % i for i in range(6)],
        'dw100g1c18u':
        ['SR:C18-ID:G1{DW100:1-FF:%d}Ena-Sel' % i for i in range(6)] +
        ['SR:C18-ID:G1{DW100:2-FF:%d}Ena-Sel' % i for i in range(6)] +
        ['SR:C18-ID:G1{DW100:1-VCor:%d}Ena-Sel' % i for i in range(2)],
        'dw100g1c18d':
        ['SR:C18-ID:G1{DW100:1-FF:%d}Ena-Sel' % i for i in range(6)] +
        ['SR:C18-ID:G1{DW100:2-FF:%d}Ena-Sel' % i for i in range(6)] +
        ['SR:C18-ID:G1{DW100:1-VCor:%d}Ena-Sel' % i for i in range(2)],
        'ivu18g1c19u':
        ['SR:C19-ID:G1A{NYX:1-FF:%d}Ena-Sel' % i for i in range(5)],
        'epu57g1c21u':
        ['SR:C21-ID:G1A{EPU:1-FF:%d}Ena-Sel' % i for i in range(6)],
        'epu105g1c21d':
        ['SR:C21-ID:G1A{EPU:2-FF:%d}Ena-Sel' % i for i in range(6)],
        'epu49g1c23u':
        ['SR:C23-ID:G1A{EPU:1-FF:%d}Ena-Sel' % i for i in range(6)],
        'epu49g1c23d':
        ['SR:C23-ID:G1A{EPU:2-FF:%d}Ena-Sel' % i for i in range(6)],
        'dw100g1c28u':
        ['SR:C28-ID:G1{DW100:1-FF:%d}Ena-Sel' % i for i in range(6)] +
        ['SR:C28-ID:G1{DW100:2-FF:%d}Ena-Sel' % i for i in range(6)] +
        ['SR:C28-ID:G1{DW100:1-VCor:%d}Ena-Sel' % i for i in range(2)],
        'dw100g1c28d':
        ['SR:C28-ID:G1{DW100:1-FF:%d}Ena-Sel' % i for i in range(6)] +
        ['SR:C28-ID:G1{DW100:2-FF:%d}Ena-Sel' % i for i in range(6)] +
        ['SR:C28-ID:G1{DW100:1-VCor:%d}Ena-Sel' % i for i in range(2)]
    }

    # Add orbit feedforward "Enable" PVs into the database

    for elem_name, pv_list in enable_pvs.items():
        assert elem_name == ap.getElements(elem_name)[0].name
        for iCh, pv in enumerate(pv_list):
            ap.apdata.updateDbPv(
                DBFILE, pv, elem_name, 'orbff{0:d}_on'.format(iCh),
                elemHandle='put', tags=tags, quiet=True, epsilon=0)

    """

    for e in ap.getElements('IVU'):
        print('##', e.name)
        (_, _, ff_gap_pvs_all, ff_cur_pvs_all) = idcomm.getFFPVs(
            e, idcomm.ALL_RESP_CORNAME_CORFLD[e.name])
        print('* gap')
        pprint.pprint(ff_gap_pvs_all)
        print('* current')
        pprint.pprint(ff_cur_pvs_all)

    for e in ap.getElements('EPU'):
        print('##', e.name)
        (_, _, _, _,
         ff_para_TIBO_all, ff_para_TOBI_all, ff_anti_TIBO_all, ff_anti_TOBI_all
         ) = idcomm.getFFPVs(e, idcomm.ALL_RESP_CORNAME_CORFLD[e.name])
        m = [ff_para_TIBO_all, ff_para_TOBI_all, ff_anti_TIBO_all, ff_anti_TOBI_all]
        for i, _m in enumerate(m):
            print('*** Mode {0:d} ***'.format(i))
            print('@ Gap')
            pprint.pprint(_m['gap'])
            print('@ Phase')
            pprint.pprint(_m['phase'])
            print('@ Current')
            pprint.pprint(_m['cur'])


    for e in ap.getElements('dw100*u'):
        print('##', e.name)
        (_, _, ff_gap_pvs_all, ff_cur_pvs_all) = idcomm.getFFPVs(
            e, idcomm.ALL_RESP_CORNAME_CORFLD[e.name[:-1]+'c_reg'])
        print('* gap')
        pprint.pprint(ff_gap_pvs_all)
        print('* current')
        pprint.pprint(ff_cur_pvs_all)

    """

    ivu_gap_pvs = {
        'ivu20g1c03c':
        ['SR:C3-ID:G1{IVU20:1-FF:%d}L2-Calc_.C' % i for i in range(6)],
        'ivu23g1c04u':
        ['SR:C04-ID:G1{IVU:1-FF:%d}L2-Calc_.C' % i for i in range(6)],
        'ivu21g1c05d':
        ['SR:C5-ID:G1{IVU21:1-FF:%d}L2-Calc_.C' % i for i in range(6)],
        'ivu22g1c10c':
        ['SR:C10-ID:G1{IVU22:1-FF:%d}L2-Calc_.C' % i for i in range(4)],
        'ivu20g1c11c':
        ['SR:C11-ID:G1{IVU20:1-FF:%d}L2-Calc_.C' % i for i in range(6)],
        'ivu23g1c12d':
        ['SR:C12-ID:G1{IVU:1-FF:%d}L2-Calc_.C' % i for i in range(6)],
        'ivu23g1c16c':
        ['SR:C16-ID:G1{IVU:1-FF:%d}L2-Calc_.C' % i for i in range(6)],
        'ivu21g1c17u':
        ['SR:C17-ID:G1{IVU21:1-FF:%d}L2-Calc_.C' % i for i in range(6)],
        'ivu21g1c17d':
        ['SR:C17-ID:G1{IVU21:2-FF:%d}L2-Calc_.C' % i for i in range(6)],
        'ivu18g1c19u':
        ['SR:C19-ID:G1A{NYX:1-FF:%d}L2-Calc_.C' % i for i in range(5)],
    }
    ivu_current_pvs = {}
    for elem_name, pv_list in ivu_gap_pvs.items():
        ivu_current_pvs[elem_name] = [pv[:-1]+'D' for pv in pv_list]

    if False:
        for elem_name, pv_list in ivu_gap_pvs.items():
            print('# ', elem_name)
            pprint.pprint(caget(pv_list))
            pprint.pprint(caget(ivu_current_pvs[elem_name]))

    dw_gap_pvs = {
        'dw100g1c08u':
        ['SR:C08-ID:G1{DW100:1-FF:%d}L2-Calc_.C' % i for i in range(6)] +
        ['SR:C08-ID:G1{DW100:2-FF:%d}L2-Calc_.C' % i for i in range(6)] +
        ['SR:C08-ID:G1{DW100:1-VCor:%d}L2-Calc_.C' % i for i in range(2)],
        'dw100g1c08d':
        ['SR:C08-ID:G1{DW100:1-FF:%d}L2-Calc_.C' % i for i in range(6)] +
        ['SR:C08-ID:G1{DW100:2-FF:%d}L2-Calc_.C' % i for i in range(6)] +
        ['SR:C08-ID:G1{DW100:1-VCor:%d}L2-Calc_.C' % i for i in range(2)],
        'dw100g1c18u':
        ['SR:C18-ID:G1{DW100:1-FF:%d}L2-Calc_.C' % i for i in range(6)] +
        ['SR:C18-ID:G1{DW100:2-FF:%d}L2-Calc_.C' % i for i in range(6)] +
        ['SR:C18-ID:G1{DW100:1-VCor:%d}L2-Calc_.C' % i for i in range(2)],
        'dw100g1c18d':
        ['SR:C18-ID:G1{DW100:1-FF:%d}L2-Calc_.C' % i for i in range(6)] +
        ['SR:C18-ID:G1{DW100:2-FF:%d}L2-Calc_.C' % i for i in range(6)] +
        ['SR:C18-ID:G1{DW100:1-VCor:%d}L2-Calc_.C' % i for i in range(2)],
        'dw100g1c28u':
        ['SR:C28-ID:G1{DW100:1-FF:%d}L2-Calc_.C' % i for i in range(6)] +
        ['SR:C28-ID:G1{DW100:2-FF:%d}L2-Calc_.C' % i for i in range(6)] +
        ['SR:C28-ID:G1{DW100:1-VCor:%d}L2-Calc_.C' % i for i in range(2)],
        'dw100g1c28d':
        ['SR:C28-ID:G1{DW100:1-FF:%d}L2-Calc_.C' % i for i in range(6)] +
        ['SR:C28-ID:G1{DW100:2-FF:%d}L2-Calc_.C' % i for i in range(6)] +
        ['SR:C28-ID:G1{DW100:1-VCor:%d}L2-Calc_.C' % i for i in range(2)],
    }
    dw_current_pvs = {}
    for elem_name, pv_list in dw_gap_pvs.items():
        dw_current_pvs[elem_name] = [pv[:-1]+'D' for pv in pv_list]

    if False:
        for elem_name, pv_list in dw_gap_pvs.items():
            print('# ', elem_name)
            pprint.pprint(caget(pv_list))
            pprint.pprint(caget(dw_current_pvs[elem_name]))

    # Add orbit feedforward "Gap" PVs for IVUs & DWs into the database
    oneD_gap_pvs = {}
    oneD_gap_pvs.update(ivu_gap_pvs)
    oneD_gap_pvs.update(dw_gap_pvs)
    #
    for elem_name, pv_list in oneD_gap_pvs.items():
        for iCh, pv in enumerate(pv_list):
            ap.apdata.updateDbPv(
                DBFILE, pv, elem_name, 'orbff{0:d}_m0_gap'.format(iCh),
                elemHandle='put', tags=tags, quiet=True, epsilon=0)

    # Add orbit feedforward "Current" PVs for IVUs & DWs into the database
    oneD_current_pvs = {}
    oneD_current_pvs.update(ivu_current_pvs)
    oneD_current_pvs.update(dw_current_pvs)
    #
    for elem_name, pv_list in oneD_current_pvs.items():
        for iCh, pv in enumerate(pv_list):
            ap.apdata.updateDbPv(
                DBFILE, pv, elem_name, 'orbff{0:d}_m0_I'.format(iCh),
                elemHandle='put', tags=tags, quiet=True, epsilon=0)


    epu_gap_pvs = [None for _ in range(4)]
    epu_gap_pvs[0] = {
        'epu57g1c02c':
        ['SR:C02-ID:G1A{EPU:1-FF:%d}L2-Calc_.F' % i for i in range(6)],
        'epu57g1c21u':
        ['SR:C21-ID:G1A{EPU:1-FF:%d}L2-Calc_.F' % i for i in range(6)],
        'epu105g1c21d':
        ['SR:C21-ID:G1A{EPU:2-FF:%d}L2-Calc_.F' % i for i in range(6)],
        'epu49g1c23u':
        ['SR:C23-ID:G1A{EPU:1-FF:%d}L2-Calc_.F' % i for i in range(6)],
        'epu49g1c23d':
        ['SR:C23-ID:G1A{EPU:2-FF:%d}L2-Calc_.F' % i for i in range(6)],
    }
    for mode_index in range(len(epu_gap_pvs))[1:]:
        _d = {}
        if   mode_index == 1: suffix = 'I'
        elif mode_index == 2: suffix = 'L'
        elif mode_index == 3: suffix = 'O'
        else:
            raise ValueError()
        for elem_name, pv_list in epu_gap_pvs[0].items():
            _d[elem_name] = [pv[:-1]+suffix for pv in pv_list]
        epu_gap_pvs[mode_index] = _d

    epu_phase_pvs, epu_current_pvs = [], []
    for mode_index, _gap_pv_dict in enumerate(epu_gap_pvs):
        _d = {}
        if   mode_index == 0: suffix = 'G'
        elif mode_index == 1: suffix = 'J'
        elif mode_index == 2: suffix = 'M'
        elif mode_index == 3: suffix = 'P'
        else:
            raise ValueError()
        for elem_name, pv_list in _gap_pv_dict.items():
            _d[elem_name] = [pv[:-1]+suffix for pv in pv_list]
        epu_phase_pvs.append(_d)

        _d = {}
        if   mode_index == 0: suffix = 'H'
        elif mode_index == 1: suffix = 'K'
        elif mode_index == 2: suffix = 'N'
        elif mode_index == 3: suffix = 'Q'
        else:
            raise ValueError()
        for elem_name, pv_list in _gap_pv_dict.items():
            _d[elem_name] = [pv[:-1]+suffix for pv in pv_list]
        epu_current_pvs.append(_d)

    if False:
        for mode_index, d in enumerate(epu_gap_pvs):
            for elem_name, pv_list in d.items():
                print('# ', elem_name)
                pprint.pprint(caget(pv_list))
                pprint.pprint(caget(epu_phase_pvs[mode_index][elem_name]))
                pprint.pprint(caget(epu_current_pvs[mode_index][elem_name]))

    # Add orbit feedforward "Gap", "Phase", & "Current" PVs for EPUs into the database
    assert len(epu_gap_pvs) == len(epu_phase_pvs) == len(epu_current_pvs)
    for mode_index, (_gapD, _phaseD, _curD) in enumerate(zip(
        epu_gap_pvs, epu_phase_pvs, epu_current_pvs)):

        for elem_name, pv_list in _gapD.items():
            for iCh, pv in enumerate(pv_list):
                ap.apdata.updateDbPv(
                    DBFILE, pv, elem_name, 'orbff{0:d}_m{1:d}_gap'.format(iCh, mode_index),
                    elemHandle='put', tags=tags, quiet=True, epsilon=0)

        for elem_name, pv_list in _phaseD.items():
            for iCh, pv in enumerate(pv_list):
                ap.apdata.updateDbPv(
                    DBFILE, pv, elem_name, 'orbff{0:d}_m{1:d}_phase'.format(iCh, mode_index),
                    elemHandle='put', tags=tags, quiet=True, epsilon=0)

        for elem_name, pv_list in _curD.items():
            for iCh, pv in enumerate(pv_list):
                ap.apdata.updateDbPv(
                    DBFILE, pv, elem_name, 'orbff{0:d}_m{1:d}_I'.format(iCh, mode_index),
                    elemHandle='put', tags=tags, quiet=True, epsilon=0)

#----------------------------------------------------------------------
def add_unitconv_to_ID_orbit_ff_fields():
    """"""

    if False: #True: # This section can only run once, as HDF5 file does not
                     # allow overwrite of existing datasets

        kw = dict(compression='gzip')

        _temp_unitconv_file = UNITCONV_FILE + '.tmp'

        fnew = h5py.File(_temp_unitconv_file, 'w')
        fold = h5py.File(UNITCONV_FILE, 'r')

        # First copy existing unit conversion data
        gold = fold['UnitConversion']
        gnew = fnew.create_group('UnitConversion')
        for k, v in gold.items():

            if False: # This will end up with bigger file size
                d = gnew.create_dataset(k, data=v.value, **kw)
            else: # This will end up with smaller file size, so use this one!
                gnew[k] = v.value
                d = gnew[k]

            for ak, av in v.attrs.items():
                put_h5py_attr(d, ak, av)

        # Adding new unit conversions

        ap.machines.loadfast('nsls2', 'SR')


        ivu_unitconv_list = [
            ({'gap_src_unit': 'mm', 'I_src_unit': '10uA'},
             ['ivu20g1c03c',
              'ivu23g1c04u',
              'ivu21g1c05d',
              'ivu20g1c11c',
              'ivu23g1c12d',
              'ivu23g1c16c',
              'ivu21g1c17u',
              'ivu21g1c17d',]
             ),
            ({'gap_src_unit': 'um', 'I_src_unit': '10uA'},
             ['ivu22g1c10c',]
             ),
            ({'gap_src_unit': 'um', 'I_src_unit': 'A'},
             ['ivu18g1c19u',]
             ),
        ]

        for uc_index, (uc_d, elem_name_list) in enumerate(ivu_unitconv_list):

            for iCh in range(6):

                fld_gap = 'orbff{0:d}_m0_gap'.format(iCh)
                fld_I   = 'orbff{0:d}_m0_I'.format(iCh)

                _elem_names = []
                for e in ap.getElements(elem_name_list):
                    if fld_gap not in e.fields(): continue
                    _elem_names.append(e.name)

                if _elem_names == []: continue

                # Save "gap" unit conversion
                #
                if uc_d['gap_src_unit'] == 'um':
                    gap_uc = 1e-3
                elif uc_d['gap_src_unit'] == 'mm':
                    gap_uc = 1.0
                else:
                    raise ValueError()
                #
                d = gnew.create_dataset(
                    'ivu_{0}_type{1:d}'.format(fld_gap, uc_index),
                    data=np.array([gap_uc, 0.0]), **kw)
                uc = {'_class_': 'polynomial', 'dst_unit': 'mm', 'dst_unit_sys': 'phy',
                      'elements': _elem_names, 'field': fld_gap,
                      'handle': ['setpoint',],
                      'invertible': 1, 'src_unit': uc_d['gap_src_unit'], 'src_unit_sys': ''}
                for k, v in uc.items(): put_h5py_attr(d, k, v)


                # Save "current" unit conversion
                #
                if uc_d['I_src_unit'] == '10uA':
                    I_uc = 1e-5
                elif uc_d['I_src_unit'] == 'A':
                    I_uc = 1.0
                else:
                    raise ValueError()
                #
                d = gnew.create_dataset(
                    'ivu_{0}_type{1:d}'.format(fld_I, uc_index),
                    data=np.array([I_uc, 0.0]), **kw)
                uc = {'_class_': 'polynomial', 'dst_unit': 'A', 'dst_unit_sys': 'phy',
                      'elements': _elem_names, 'field': fld_I,
                      'handle': ['setpoint',],
                      'invertible': 1, 'src_unit': uc_d['I_src_unit'], 'src_unit_sys': ''}
                for k, v in uc.items(): put_h5py_attr(d, k, v)


        epu_unitconv_list = [
            ({'gap_src_unit': 'um', 'phase_src_unit': 'um', 'I_src_unit': '10uA'},
             ['epu49g1c23u', 'epu49g1c23d']
            ),
            ({'gap_src_unit': 'mm', 'phase_src_unit': 'mm', 'I_src_unit': 'A'},
             ['epu57g1c02c', 'epu57g1c21u', 'epu105g1c21d']
             ),
        ]


        for uc_index, (uc_d, elem_name_list) in enumerate(epu_unitconv_list):

            for iCh in range(6):
                for iMode in range(4):

                    fld_gap   = 'orbff{0:d}_m{1:d}_gap'.format(iCh, iMode)
                    fld_phase = 'orbff{0:d}_m{1:d}_phase'.format(iCh, iMode)
                    fld_I     = 'orbff{0:d}_m{1:d}_I'.format(iCh, iMode)

                    _elem_names = []
                    for e in ap.getElements(elem_name_list):
                        if fld_gap not in e.fields(): continue
                        _elem_names.append(e.name)

                    if _elem_names == []: continue

                    # Save "gap" unit conversion
                    #
                    if uc_d['gap_src_unit'] == 'um':
                        gap_uc = 1e-3
                    elif uc_d['gap_src_unit'] == 'mm':
                        gap_uc = 1.0
                    else:
                        raise ValueError()
                    #
                    d = gnew.create_dataset(
                        'epu_{0}_type{1:d}'.format(fld_gap, uc_index),
                        data=np.array([gap_uc, 0.0]), **kw)
                    uc = {'_class_': 'polynomial', 'dst_unit': 'mm', 'dst_unit_sys': 'phy',
                          'elements': _elem_names, 'field': fld_gap,
                          'handle': ['setpoint',],
                          'invertible': 1, 'src_unit': uc_d['gap_src_unit'], 'src_unit_sys': ''}
                    for k, v in uc.items(): put_h5py_attr(d, k, v)

                    # Save "phase" unit conversion
                    #
                    if uc_d['phase_src_unit'] == 'um':
                        phase_uc = 1e-3
                    elif uc_d['phase_src_unit'] == 'mm':
                        phase_uc = 1.0
                    else:
                        raise ValueError()
                    #
                    d = gnew.create_dataset(
                        'epu_{0}_type{1:d}'.format(fld_phase, uc_index),
                        data=np.array([phase_uc, 0.0]), **kw)
                    uc = {'_class_': 'polynomial', 'dst_unit': 'mm', 'dst_unit_sys': 'phy',
                          'elements': _elem_names, 'field': fld_phase,
                          'handle': ['setpoint',],
                          'invertible': 1, 'src_unit': uc_d['phase_src_unit'], 'src_unit_sys': ''}
                    for k, v in uc.items(): put_h5py_attr(d, k, v)

                    # Save "current" unit conversion
                    #
                    if uc_d['I_src_unit'] == '10uA':
                        I_uc = 1e-5
                    elif uc_d['I_src_unit'] == 'A':
                        I_uc = 1.0
                    else:
                        raise ValueError()
                    #
                    d = gnew.create_dataset(
                        'epu_{0}_type{1:d}'.format(fld_I, uc_index),
                        data=np.array([I_uc, 0.0]), **kw)
                    uc = {'_class_': 'polynomial', 'dst_unit': 'A', 'dst_unit_sys': 'phy',
                          'elements': _elem_names, 'field': fld_I,
                          'handle': ['setpoint',],
                          'invertible': 1, 'src_unit': uc_d['I_src_unit'], 'src_unit_sys': ''}
                    for k, v in uc.items(): put_h5py_attr(d, k, v)

        dw_unitconv_list = [
            ({'gap_src_unit': 'um', 'I_src_unit': '10uA'},
             ['dw100g1c08u', 'dw100g1c08d', 'dw100g1c18u', 'dw100g1c18d',
              'dw100g1c28u', 'dw100g1c28d'],
             list(range(12))
            ),
            ({'gap_src_unit': 'um', 'I_src_unit': 'A'},
             ['dw100g1c08u', 'dw100g1c08d', 'dw100g1c18u', 'dw100g1c18d',
              'dw100g1c28u', 'dw100g1c28d'],
             list(range(12, 13+1))
            ),
        ]

        for uc_index, (uc_d, elem_name_list, channel_indexes) in enumerate(
            dw_unitconv_list):

            for iCh in channel_indexes:

                fld_gap = 'orbff{0:d}_m0_gap'.format(iCh)
                fld_I   = 'orbff{0:d}_m0_I'.format(iCh)

                _elem_names = []
                for e in ap.getElements(elem_name_list):
                    if fld_gap not in e.fields(): continue
                    _elem_names.append(e.name)

                if _elem_names == []: continue

                # Save "gap" unit conversion
                #
                if uc_d['gap_src_unit'] == 'um':
                    gap_uc = 1e-3
                elif uc_d['gap_src_unit'] == 'mm':
                    gap_uc = 1.0
                else:
                    raise ValueError()
                #
                d = gnew.create_dataset(
                    'dw_{0}_type{1:d}'.format(fld_gap, uc_index),
                    data=np.array([gap_uc, 0.0]), **kw)
                uc = {'_class_': 'polynomial', 'dst_unit': 'mm', 'dst_unit_sys': 'phy',
                      'elements': _elem_names, 'field': fld_gap,
                      'handle': ['setpoint',],
                      'invertible': 1, 'src_unit': uc_d['gap_src_unit'], 'src_unit_sys': ''}
                for k, v in uc.items(): put_h5py_attr(d, k, v)


                # Save "current" unit conversion
                #
                if uc_d['I_src_unit'] == '10uA':
                    I_uc = 1e-5
                elif uc_d['I_src_unit'] == 'A':
                    I_uc = 1.0
                else:
                    raise ValueError()
                #
                d = gnew.create_dataset(
                    'dw_{0}_type{1:d}'.format(fld_I, uc_index),
                    data=np.array([I_uc, 0.0]), **kw)
                uc = {'_class_': 'polynomial', 'dst_unit': 'A', 'dst_unit_sys': 'phy',
                      'elements': _elem_names, 'field': fld_I,
                      'handle': ['setpoint',],
                      'invertible': 1, 'src_unit': uc_d['I_src_unit'], 'src_unit_sys': ''}
                for k, v in uc.items(): put_h5py_attr(d, k, v)


        fold.close()
        fnew.close()

        shutil.move(_temp_unitconv_file, UNITCONV_FILE)

    #
    # Test if the unit conversion works
    #

    ap.machines.loadfast('nsls2', 'SR')

    unitsys = 'phy' #None

    if False:
        for group in ['IVU', 'DW']:
            print('######', group, '######')
            ids = ap.getElements(group)

            for prop in ['gap', 'I']:

                print('***', prop, '***')

                for e in ids:
                    print('## {0}'.format(e.name))
                    for i in range(14):
                        fld = 'orbff{0:d}_m0_{1}'.format(i, prop)

                        if fld not in e.fields():
                            break

                        if prop == 'gap':
                            print('* Ch.' + str(i) + ':',
                                  e.get(fld, unitsys=unitsys, handle='setpoint'),
                                  )
                        else:
                            print('* Ch.' + str(i) + ':',
                                  np.max(np.abs(e.get(fld, unitsys=unitsys, handle='setpoint'))),
                                  )

    else:
        ids = ap.getElements('EPU')

        for prop in ['gap', 'phase', 'I']:

            print('***', prop, '***')

            for e in ids:
                print('## {0}'.format(e.name))
                for iMode in range(4):
                    print('-----', 'Mode', iMode, '-----')
                    for i in range(6):
                        fld = 'orbff{0:d}_m{1:d}_{2}'.format(i, iMode, prop)

                        if fld not in e.fields():
                            break

                        if prop in ('gap', 'phase'):
                            print('* Ch.' + str(i) + ':',
                                  e.get(fld, unitsys=unitsys, handle='setpoint'),
                                  )
                        else:
                            print('* Ch.' + str(i) + ':',
                                  np.max(np.abs(e.get(fld, unitsys=unitsys, handle='setpoint'))),
                                  )

#----------------------------------------------------------------------
def add_orbit_ff_pvs_for_SST_U42_and_EPU60():
    """
    """

    ap.machines.loadfast('nsls2', 'SR')

    tags = ['aphla.sys.SR']

    """
    import idcomm # ~/hg_repos/nsls2scripts/idcomm/idcomm.py

    id_index = 0
    e = ap.getElements('SST')[id_index]
    enable_pvs = idcomm.getFFEnablePVs(e, idcomm.ALL_RESP_CORNAME_CORFLD[e.name])
    """

    enable_pvs = {
        'ovu42g1c07u':
        ['SR:C07-ID:G1A{SST2:1-FF:%d}Ena-Sel' % i for i in [0, 1, 4, 5]],
        'epu60g1c07d':
        ['SR:C07-ID:G1A{SST1:1-FF:%d}Ena-Sel' % i for i in [0, 1, 4, 5]],
    }

    # Add orbit feedforward "Enable" PVs into the database


    for elem_name, pv_list in enable_pvs.items():
        assert elem_name == ap.getElements(elem_name)[0].name
        for iCh, pv in enumerate(pv_list):
            ap.apdata.updateDbPv(
                DBFILE, pv, elem_name, 'orbff{0:d}_on'.format(iCh),
                elemHandle='put', tags=tags, quiet=True, epsilon=0)


    """
    e = ap.getElements('ovu42g1c07u')[0]
    print('##', e.name)
    (_, _, ff_gap_pvs_all, ff_cur_pvs_all) = idcomm.getFFPVs(
        e, idcomm.ALL_RESP_CORNAME_CORFLD[e.name])
    print('* gap')
    pprint.pprint(ff_gap_pvs_all)
    print('* current')
    pprint.pprint(ff_cur_pvs_all)



    e = ap.getElements('epu60g1c07d')[0]
    print('##', e.name)
    (_, _, _, _,
     ff_para_TIBO_all, ff_para_TOBI_all, ff_anti_TIBO_all, ff_anti_TOBI_all
     ) = idcomm.getFFPVs(e, idcomm.ALL_RESP_CORNAME_CORFLD[e.name])
    m = [ff_para_TIBO_all, ff_para_TOBI_all, ff_anti_TIBO_all, ff_anti_TOBI_all]
    for i, _m in enumerate(m):
        print('*** Mode {0:d} ***'.format(i))
        print('@ Gap')
        pprint.pprint(_m['gap'])
        print('@ Phase')
        pprint.pprint(_m['phase'])
        print('@ Current')
        pprint.pprint(_m['cur'])

    """

    ovu_gap_pvs = {
        'ovu42g1c07u':
        ['SR:C07-ID:G1A{SST2:1-FF:%d}L2-Calc_.C' % i for i in [0,1,4,5]],
    }
    ovu_current_pvs = {}
    for elem_name, pv_list in ovu_gap_pvs.items():
        ovu_current_pvs[elem_name] = [pv[:-1]+'D' for pv in pv_list]

    if True:
        for elem_name, pv_list in ovu_gap_pvs.items():
            print('# ', elem_name)
            pprint.pprint(ap.caget(pv_list))
            pprint.pprint(ap.caget(ovu_current_pvs[elem_name]))

    # Add orbit feedforward "Gap" PVs for OVUs into the database
    oneD_gap_pvs = {}
    oneD_gap_pvs.update(ovu_gap_pvs)
    #
    for elem_name, pv_list in oneD_gap_pvs.items():
        for iCh, pv in enumerate(pv_list):
            ap.apdata.updateDbPv(
                DBFILE, pv, elem_name, 'orbff{0:d}_m0_gap'.format(iCh),
                elemHandle='put', tags=tags, quiet=True, epsilon=0)

    # Add orbit feedforward "Current" PVs for OVUs into the database
    oneD_current_pvs = {}
    oneD_current_pvs.update(ovu_current_pvs)
    #
    for elem_name, pv_list in oneD_current_pvs.items():
        for iCh, pv in enumerate(pv_list):
            ap.apdata.updateDbPv(
                DBFILE, pv, elem_name, 'orbff{0:d}_m0_I'.format(iCh),
                elemHandle='put', tags=tags, quiet=True, epsilon=0)


    epu_gap_pvs = [None for _ in range(4)]
    epu_gap_pvs[0] = {
        'epu60g1c07d':
        ['SR:C07-ID:G1A{SST1:1-FF:%d}L2-Calc_.F' % i for i in [0, 1, 4, 5]],
    }
    for mode_index in range(len(epu_gap_pvs))[1:]:
        _d = {}
        if   mode_index == 1: suffix = 'I'
        elif mode_index == 2: suffix = 'L'
        elif mode_index == 3: suffix = 'O'
        else:
            raise ValueError()
        for elem_name, pv_list in epu_gap_pvs[0].items():
            _d[elem_name] = [pv[:-1]+suffix for pv in pv_list]
        epu_gap_pvs[mode_index] = _d

    epu_phase_pvs, epu_current_pvs = [], []
    for mode_index, _gap_pv_dict in enumerate(epu_gap_pvs):
        _d = {}
        if   mode_index == 0: suffix = 'G'
        elif mode_index == 1: suffix = 'J'
        elif mode_index == 2: suffix = 'M'
        elif mode_index == 3: suffix = 'P'
        else:
            raise ValueError()
        for elem_name, pv_list in _gap_pv_dict.items():
            _d[elem_name] = [pv[:-1]+suffix for pv in pv_list]
        epu_phase_pvs.append(_d)

        _d = {}
        if   mode_index == 0: suffix = 'H'
        elif mode_index == 1: suffix = 'K'
        elif mode_index == 2: suffix = 'N'
        elif mode_index == 3: suffix = 'Q'
        else:
            raise ValueError()
        for elem_name, pv_list in _gap_pv_dict.items():
            _d[elem_name] = [pv[:-1]+suffix for pv in pv_list]
        epu_current_pvs.append(_d)

    if True:
        for mode_index, d in enumerate(epu_gap_pvs):
            for elem_name, pv_list in d.items():
                print('# ', elem_name)
                pprint.pprint(ap.caget(pv_list))
                pprint.pprint(ap.caget(epu_phase_pvs[mode_index][elem_name]))
                pprint.pprint(ap.caget(epu_current_pvs[mode_index][elem_name]))

    # Add orbit feedforward "Gap", "Phase", & "Current" PVs for EPUs into the database
    assert len(epu_gap_pvs) == len(epu_phase_pvs) == len(epu_current_pvs)
    for mode_index, (_gapD, _phaseD, _curD) in enumerate(zip(
        epu_gap_pvs, epu_phase_pvs, epu_current_pvs)):

        for elem_name, pv_list in _gapD.items():
            for iCh, pv in enumerate(pv_list):
                ap.apdata.updateDbPv(
                    DBFILE, pv, elem_name, 'orbff{0:d}_m{1:d}_gap'.format(iCh, mode_index),
                    elemHandle='put', tags=tags, quiet=True, epsilon=0)

        for elem_name, pv_list in _phaseD.items():
            for iCh, pv in enumerate(pv_list):
                ap.apdata.updateDbPv(
                    DBFILE, pv, elem_name, 'orbff{0:d}_m{1:d}_phase'.format(iCh, mode_index),
                    elemHandle='put', tags=tags, quiet=True, epsilon=0)

        for elem_name, pv_list in _curD.items():
            for iCh, pv in enumerate(pv_list):
                ap.apdata.updateDbPv(
                    DBFILE, pv, elem_name, 'orbff{0:d}_m{1:d}_I'.format(iCh, mode_index),
                    elemHandle='put', tags=tags, quiet=True, epsilon=0)

#----------------------------------------------------------------------
def add_unitconv_to_ID_orbit_ff_fields_for_SST_U42_and_EPU60():
    """"""

    if False: #True: # This section can only run once, as HDF5 file does not
                     # allow overwrite of existing datasets

        kw = dict(compression='gzip')

        _temp_unitconv_file = UNITCONV_FILE + '.tmp'

        fnew = h5py.File(_temp_unitconv_file, 'w')
        fold = h5py.File(UNITCONV_FILE, 'r')

        # First copy existing unit conversion data
        gold = fold['UnitConversion']
        gnew = fnew.create_group('UnitConversion')
        for k, v in gold.items():

            # NOT copying these datasets as they need to be modified
            if k.startswith('epu_') and (k[:-1].endswith('_gap_type') or
                                         k[:-1].endswith('_phase_type') or
                                         k[:-1].endswith('_I_type')):
                continue

            if False: # This will end up with bigger file size
                d = gnew.create_dataset(k, data=v.value, **kw)
            else: # This will end up with smaller file size, so use this one!
                gnew[k] = v.value
                d = gnew[k]

            for ak, av in v.attrs.items():
                put_h5py_attr(d, ak, av)

        # Adding new unit conversions

        ap.machines.loadfast('nsls2', 'SR')


        ovu_unitconv_list = [
            ({'gap_src_unit': 'um', 'I_src_unit': 'A'},
             ['ovu42g1c07u',]
             ),
        ]

        for uc_index, (uc_d, elem_name_list) in enumerate(ovu_unitconv_list):

            for iCh in range(6):

                fld_gap = 'orbff{0:d}_m0_gap'.format(iCh)
                fld_I   = 'orbff{0:d}_m0_I'.format(iCh)

                _elem_names = []
                for e in ap.getElements(elem_name_list):
                    if fld_gap not in e.fields(): continue
                    _elem_names.append(e.name)

                if _elem_names == []: continue

                # Save "gap" unit conversion
                #
                if uc_d['gap_src_unit'] == 'um':
                    gap_uc = 1e-3
                elif uc_d['gap_src_unit'] == 'mm':
                    gap_uc = 1.0
                else:
                    raise ValueError()
                #
                d = gnew.create_dataset(
                    'ovu_{0}_type{1:d}'.format(fld_gap, uc_index),
                    data=np.array([gap_uc, 0.0]), **kw)
                uc = {'_class_': 'polynomial', 'dst_unit': 'mm', 'dst_unit_sys': 'phy',
                      'elements': _elem_names, 'field': fld_gap,
                      'handle': ['setpoint',],
                      'invertible': 1, 'src_unit': uc_d['gap_src_unit'], 'src_unit_sys': ''}
                for k, v in uc.items(): put_h5py_attr(d, k, v)


                # Save "current" unit conversion
                #
                if uc_d['I_src_unit'] == '10uA':
                    I_uc = 1e-5
                elif uc_d['I_src_unit'] == 'A':
                    I_uc = 1.0
                else:
                    raise ValueError()
                #
                d = gnew.create_dataset(
                    'ovu_{0}_type{1:d}'.format(fld_I, uc_index),
                    data=np.array([I_uc, 0.0]), **kw)
                uc = {'_class_': 'polynomial', 'dst_unit': 'A', 'dst_unit_sys': 'phy',
                      'elements': _elem_names, 'field': fld_I,
                      'handle': ['setpoint',],
                      'invertible': 1, 'src_unit': uc_d['I_src_unit'], 'src_unit_sys': ''}
                for k, v in uc.items(): put_h5py_attr(d, k, v)


        epu_unitconv_list = [
            ({'gap_src_unit': 'um', 'phase_src_unit': 'um', 'I_src_unit': '10uA'},
             ['epu49g1c23u', 'epu49g1c23d']
            ),
            ({'gap_src_unit': 'mm', 'phase_src_unit': 'mm', 'I_src_unit': 'A'},
             ['epu57g1c02c', 'epu57g1c21u', 'epu105g1c21d']
             ),
            ({'gap_src_unit': 'um', 'phase_src_unit': 'um', 'I_src_unit': 'A'},
             ['epu60g1c07d',]
             ),
        ]


        for uc_index, (uc_d, elem_name_list) in enumerate(epu_unitconv_list):

            for iCh in range(6):
                for iMode in range(4):

                    fld_gap   = 'orbff{0:d}_m{1:d}_gap'.format(iCh, iMode)
                    fld_phase = 'orbff{0:d}_m{1:d}_phase'.format(iCh, iMode)
                    fld_I     = 'orbff{0:d}_m{1:d}_I'.format(iCh, iMode)

                    _elem_names = []
                    for e in ap.getElements(elem_name_list):
                        if fld_gap not in e.fields(): continue
                        _elem_names.append(e.name)

                    if _elem_names == []: continue

                    # Save "gap" unit conversion
                    #
                    if uc_d['gap_src_unit'] == 'um':
                        gap_uc = 1e-3
                    elif uc_d['gap_src_unit'] == 'mm':
                        gap_uc = 1.0
                    else:
                        raise ValueError()
                    #
                    d = gnew.create_dataset(
                        'epu_{0}_type{1:d}'.format(fld_gap, uc_index),
                        data=np.array([gap_uc, 0.0]), **kw)
                    uc = {'_class_': 'polynomial', 'dst_unit': 'mm', 'dst_unit_sys': 'phy',
                          'elements': _elem_names, 'field': fld_gap,
                          'handle': ['setpoint',],
                          'invertible': 1, 'src_unit': uc_d['gap_src_unit'], 'src_unit_sys': ''}
                    for k, v in uc.items(): put_h5py_attr(d, k, v)

                    # Save "phase" unit conversion
                    #
                    if uc_d['phase_src_unit'] == 'um':
                        phase_uc = 1e-3
                    elif uc_d['phase_src_unit'] == 'mm':
                        phase_uc = 1.0
                    else:
                        raise ValueError()
                    #
                    d = gnew.create_dataset(
                        'epu_{0}_type{1:d}'.format(fld_phase, uc_index),
                        data=np.array([phase_uc, 0.0]), **kw)
                    uc = {'_class_': 'polynomial', 'dst_unit': 'mm', 'dst_unit_sys': 'phy',
                          'elements': _elem_names, 'field': fld_phase,
                          'handle': ['setpoint',],
                          'invertible': 1, 'src_unit': uc_d['phase_src_unit'], 'src_unit_sys': ''}
                    for k, v in uc.items(): put_h5py_attr(d, k, v)

                    # Save "current" unit conversion
                    #
                    if uc_d['I_src_unit'] == '10uA':
                        I_uc = 1e-5
                    elif uc_d['I_src_unit'] == 'A':
                        I_uc = 1.0
                    else:
                        raise ValueError()
                    #
                    d = gnew.create_dataset(
                        'epu_{0}_type{1:d}'.format(fld_I, uc_index),
                        data=np.array([I_uc, 0.0]), **kw)
                    uc = {'_class_': 'polynomial', 'dst_unit': 'A', 'dst_unit_sys': 'phy',
                          'elements': _elem_names, 'field': fld_I,
                          'handle': ['setpoint',],
                          'invertible': 1, 'src_unit': uc_d['I_src_unit'], 'src_unit_sys': ''}
                    for k, v in uc.items(): put_h5py_attr(d, k, v)


        fold.close()
        fnew.close()

        shutil.move(_temp_unitconv_file, UNITCONV_FILE)
        os.chmod(UNITCONV_FILE, 0o755)

    #
    # Test if the unit conversion works
    #

    ap.machines.loadfast('nsls2', 'SR')

    unitsys = 'phy' #None

    if False:
        for group in ['IVU', 'DW', 'OVU']:
            print('######', group, '######')
            ids = ap.getElements(group)

            for prop in ['gap', 'I']:

                print('***', prop, '***')

                for e in ids:
                    print('## {0}'.format(e.name))
                    for i in range(14):
                        fld = 'orbff{0:d}_m0_{1}'.format(i, prop)

                        if fld not in e.fields():
                            break

                        if prop == 'gap':
                            print('* Ch.' + str(i) + ':',
                                  e.get(fld, unitsys=unitsys, handle='setpoint'),
                                  )
                        else:
                            print('* Ch.' + str(i) + ':',
                                  np.max(np.abs(e.get(fld, unitsys=unitsys, handle='setpoint'))),
                                  )

    else:
        ids = ap.getElements('EPU')

        for prop in ['gap', 'phase', 'I']:

            print('***', prop, '***')

            for e in ids:
                print('## {0}'.format(e.name))
                for iMode in range(4):
                    print('-----', 'Mode', iMode, '-----')
                    for i in range(6):
                        fld = 'orbff{0:d}_m{1:d}_{2}'.format(i, iMode, prop)

                        if fld not in e.fields():
                            break

                        if prop in ('gap', 'phase'):
                            print('* Ch.' + str(i) + ':',
                                  e.get(fld, unitsys=unitsys, handle='setpoint'),
                                  )
                        else:
                            print('* Ch.' + str(i) + ':',
                                  np.max(np.abs(e.get(fld, unitsys=unitsys, handle='setpoint'))),
                                  )

#----------------------------------------------------------------------
def add_current_strip_channels():
    """"""

    tags = ['aphla.sys.SR']

    # ESM 57 (C21-1)
    CS_pv_prefixes = [
        'SR:C20-MG{PS:EPU_1}U1-',
        'SR:C20-MG{PS:EPU_1}U2-',
        'SR:C20-MG{PS:EPU_1}U3-',
        'SR:C20-MG{PS:EPU_1}U4-',
        'SR:C20-MG{PS:EPU_1}U5-',
        'SR:C20-MG{PS:EPU_1}U6-',
        'SR:C20-MG{PS:EPU_2}U1-',
        'SR:C20-MG{PS:EPU_2}U2-',
        'SR:C20-MG{PS:EPU_2}U3-',
        'SR:C20-MG{PS:EPU_2}U4-',
        'SR:C20-MG{PS:EPU_2}U5-',
        'SR:C20-MG{PS:EPU_2}U6-',
        'SR:C20-MG{PS:EPU_3}U1-',
        'SR:C20-MG{PS:EPU_3}U2-',
        'SR:C20-MG{PS:EPU_3}U3-',
        'SR:C20-MG{PS:EPU_3}U4-',
        'SR:C20-MG{PS:EPU_3}U5-',
        'SR:C20-MG{PS:EPU_3}U6-',
    ]
    CS_pvsps  = [prefix + 'I-SP' for prefix in CS_pv_prefixes]
    CS_pvrbs  = [prefix + 'V-I' for prefix in CS_pv_prefixes]
    CS_pvrb1s = [prefix + 'I-I' for prefix in CS_pv_prefixes]
    channel_indexes = list(range(20))[1:-1]

    # Add ESM-57 current strips PVs into the database
    elem_name = 'epu57g1c21u'
    assert elem_name == ap.getElements(elem_name)[0].name
    assert len(CS_pvsps) == len(CS_pvrbs) == len(CS_pvrb1s) == len(channel_indexes)
    for iCh, pvsp, pvrb, pvrb1 in zip(channel_indexes, CS_pvsps, CS_pvrbs, CS_pvrb1s):
        ap.apdata.updateDbPv(
            DBFILE, pvsp, elem_name, 'csch{0:d}'.format(iCh),
            elemHandle='put', tags=tags, quiet=True, epsilon=0.01)
        ap.apdata.updateDbPv(
            DBFILE, pvrb, elem_name, 'csch{0:d}'.format(iCh),
            elemHandle='get', tags=tags, quiet=True, epsilon=0.01)
        ap.apdata.updateDbPv(
            DBFILE, pvrb1, elem_name, 'csch{0:d}rb1'.format(iCh),
            elemHandle='get', tags=tags, quiet=True, epsilon=0.01)

    # ESM 105 (C21-2)
    CS_pv_prefixes = [
        'SR:C20-MG{PS:EPU_4}U1-',
        'SR:C20-MG{PS:EPU_4}U2-',
        'SR:C20-MG{PS:EPU_4}U3-',
        'SR:C20-MG{PS:EPU_4}U4-',
        'SR:C20-MG{PS:EPU_4}U5-',
        'SR:C20-MG{PS:EPU_4}U6-',
        'SR:C20-MG{PS:EPU_9}U1-',
        'SR:C20-MG{PS:EPU_9}U2-',
        'SR:C20-MG{PS:EPU_9}U3-',
        'SR:C20-MG{PS:EPU_9}U4-',
        'SR:C20-MG{PS:EPU_9}U5-',
        'SR:C20-MG{PS:EPU_9}U6-',
        'SR:C20-MG{PS:EPU_5}U1-',
        'SR:C20-MG{PS:EPU_5}U2-',
        'SR:C20-MG{PS:EPU_5}U3-',
        'SR:C20-MG{PS:EPU_5}U4-',
        'SR:C20-MG{PS:EPU_5}U5-',
        'SR:C20-MG{PS:EPU_5}U6-',
    ]
    CS_pvsps  = [prefix + 'I-SP' for prefix in CS_pv_prefixes]
    CS_pvrbs  = [prefix + 'V-I' for prefix in CS_pv_prefixes]
    CS_pvrb1s = [prefix + 'I-I' for prefix in CS_pv_prefixes]
    channel_indexes = list(range(20))[1:-1]

    # Add ESM-105 current strips PVs into the database
    elem_name = 'epu105g1c21d'
    assert elem_name == ap.getElements(elem_name)[0].name
    assert len(CS_pvsps) == len(CS_pvrbs) == len(CS_pvrb1s) == len(channel_indexes)
    for iCh, pvsp, pvrb, pvrb1 in zip(channel_indexes, CS_pvsps, CS_pvrbs, CS_pvrb1s):
        ap.apdata.updateDbPv(
            DBFILE, pvsp, elem_name, 'csch{0:d}'.format(iCh),
            elemHandle='put', tags=tags, quiet=True, epsilon=0.01)
        ap.apdata.updateDbPv(
            DBFILE, pvrb, elem_name, 'csch{0:d}'.format(iCh),
            elemHandle='get', tags=tags, quiet=True, epsilon=0.01)
        ap.apdata.updateDbPv(
            DBFILE, pvrb1, elem_name, 'csch{0:d}rb1'.format(iCh),
            elemHandle='get', tags=tags, quiet=True, epsilon=0.01)



    # SIX (C02)
    channel_indexes = list(range(20))[1:-1]
    CS_pvsps, CS_pvrbs, CS_pvrb1s = [], [], []
    template_pvsp  = 'SR:C01-MG{{PS:RR{0:d}_ID02}}U{1:d}-I-SP'
    template_pvrb  = 'SR:C01-MG{{PS:RR{0:d}_ID02}}U{1:d}-V-I'
    template_pvrb1 = 'SR:C01-MG{{PS:RR{0:d}_ID02}}U{1:d}-I-I'
    for i in range(3):
        for j in range(6):
            CS_pvsps.append(template_pvsp.format(i+1, j+1))
            CS_pvrbs.append(template_pvrb.format(i+1, j+1))
            CS_pvrb1s.append(template_pvrb1.format(i+1, j+1))

    # Add SIX current strips PVs into the database
    elem_name = 'epu57g1c02c'
    assert elem_name == ap.getElements(elem_name)[0].name
    assert len(CS_pvsps) == len(CS_pvrbs) == len(CS_pvrb1s) == len(channel_indexes)
    for iCh, pvsp, pvrb, pvrb1 in zip(channel_indexes, CS_pvsps, CS_pvrbs, CS_pvrb1s):
        ap.apdata.updateDbPv(
            DBFILE, pvsp, elem_name, 'csch{0:d}'.format(iCh),
            elemHandle='put', tags=tags, quiet=True, epsilon=0.01)
        ap.apdata.updateDbPv(
            DBFILE, pvrb, elem_name, 'csch{0:d}'.format(iCh),
            elemHandle='get', tags=tags, quiet=True, epsilon=0.01)
        ap.apdata.updateDbPv(
            DBFILE, pvrb1, elem_name, 'csch{0:d}rb1'.format(iCh),
            elemHandle='get', tags=tags, quiet=True, epsilon=0.01)


    # CSX-1 (C23-1)
    CS_pv_prefixes = [
        'SR:C22-MG{PS:EPU_1}U1-',
        'SR:C22-MG{PS:EPU_1}U2-',
        'SR:C22-MG{PS:EPU_1}U3-',
        'SR:C22-MG{PS:EPU_1}U4-',
        'SR:C22-MG{PS:EPU_1}U5-',
        'SR:C22-MG{PS:EPU_1}U6-',

        'SR:C22-MG{PS:EPU_2}U1-',
        'SR:C22-MG{PS:EPU_2}U2-',
        'SR:C22-MG{PS:EPU_2}U3-',
        'SR:C22-MG{PS:EPU_2}U4-',
        'SR:C22-MG{PS:EPU_2}U5-',
        'SR:C22-MG{PS:EPU_2}U6-',

        'SR:C22-MG{PS:EPU_3}U1-',
        'SR:C22-MG{PS:EPU_3}U2-',
        'SR:C22-MG{PS:EPU_3}U3-',
        'SR:C22-MG{PS:EPU_3}U4-',
        'SR:C22-MG{PS:EPU_3}U5-',
        'SR:C22-MG{PS:EPU_3}U6-',

        'SR:C22-MG{PS:EPU_4}U1-',
        'SR:C22-MG{PS:EPU_4}U2-',
    ]
    CS_pvsps  = [prefix + 'I-SP' for prefix in CS_pv_prefixes]
    CS_pvrbs  = [prefix + 'I-I' for prefix in CS_pv_prefixes]
    # ^ "CS_pvrbs" should be normally linked to "V-I" PVs, but, since "V-I" PVs
    #   do not exist for CSX, the "I-I" PVs are being used here.
    CS_pvrb1s = [prefix + 'I-I' for prefix in CS_pv_prefixes]
    channel_indexes = list(range(20))
    #
    CS_pvons = [prefix + 'On-Cmd' for prefix in CS_pv_prefixes]

    # Add CSX-1 current strips PVs into the database
    elem_name = 'epu49g1c23u'
    assert elem_name == ap.getElements(elem_name)[0].name
    assert len(CS_pvsps) == len(CS_pvrbs) == len(CS_pvrb1s) \
           == len(channel_indexes) == len(CS_pvons)
    for iCh, pvsp, pvrb, pvrb1, pvon in zip(
        channel_indexes, CS_pvsps, CS_pvrbs, CS_pvrb1s, CS_pvons):
        ap.apdata.updateDbPv(
            DBFILE, pvsp, elem_name, 'csch{0:d}'.format(iCh),
            elemHandle='put', tags=tags, quiet=True, epsilon=0.01)
        ap.apdata.updateDbPv(
            DBFILE, pvrb, elem_name, 'csch{0:d}'.format(iCh),
            elemHandle='get', tags=tags, quiet=True, epsilon=0.01)
        ap.apdata.updateDbPv(
            DBFILE, pvrb1, elem_name, 'csch{0:d}rb1'.format(iCh),
            elemHandle='get', tags=tags, quiet=True, epsilon=0.01)

        ap.apdata.updateDbPv(
            DBFILE, pvon, elem_name, 'csch{0:d}_on'.format(iCh),
            elemHandle='put', tags=tags, quiet=True, epsilon=0)


    # CSX-2 (C23-2)
    CS_pv_prefixes = [
        'SR:C22-MG{PS:EPU_4}U3-',
        'SR:C22-MG{PS:EPU_4}U4-',
        'SR:C22-MG{PS:EPU_4}U5-',
        'SR:C22-MG{PS:EPU_4}U6-',
        'SR:C22-MG{PS:EPU_5}U1-',
        'SR:C22-MG{PS:EPU_5}U2-',

        'SR:C22-MG{PS:EPU_5}U3-',
        'SR:C22-MG{PS:EPU_5}U4-',
        'SR:C22-MG{PS:EPU_5}U5-',
        'SR:C22-MG{PS:EPU_5}U6-',
        'SR:C22-MG{PS:EPU_7}U1-',
        'SR:C22-MG{PS:EPU_7}U2-',

        'SR:C22-MG{PS:EPU_6}U1-',
        'SR:C22-MG{PS:EPU_6}U2-',
        'SR:C22-MG{PS:EPU_6}U3-',
        'SR:C22-MG{PS:EPU_6}U4-',
        'SR:C22-MG{PS:EPU_6}U5-',
        'SR:C22-MG{PS:EPU_6}U6-',

        'SR:C22-MG{PS:EPU_7}U3-',
        'SR:C22-MG{PS:EPU_7}U4-',
    ]
    CS_pvsps  = [prefix + 'I-SP' for prefix in CS_pv_prefixes]
    CS_pvrbs  = [prefix + 'I-I' for prefix in CS_pv_prefixes]
    # ^ "CS_pvrbs" should be normally linked to "V-I" PVs, but, since "V-I" PVs
    #   do not exist for CSX, the "I-I" PVs are being used here.
    CS_pvrb1s = [prefix + 'I-I' for prefix in CS_pv_prefixes]
    channel_indexes = list(range(20))
    #
    CS_pvons = [prefix + 'On-Cmd' for prefix in CS_pv_prefixes]

    # Add CSX-2 current strips PVs into the database
    elem_name = 'epu49g1c23d'
    assert elem_name == ap.getElements(elem_name)[0].name
    assert len(CS_pvsps) == len(CS_pvrbs) == len(CS_pvrb1s) \
           == len(channel_indexes) == len(CS_pvons)
    for iCh, pvsp, pvrb, pvrb1, pvon in zip(
        channel_indexes, CS_pvsps, CS_pvrbs, CS_pvrb1s, CS_pvons):
        ap.apdata.updateDbPv(
            DBFILE, pvsp, elem_name, 'csch{0:d}'.format(iCh),
            elemHandle='put', tags=tags, quiet=True, epsilon=0.01)
        ap.apdata.updateDbPv(
            DBFILE, pvrb, elem_name, 'csch{0:d}'.format(iCh),
            elemHandle='get', tags=tags, quiet=True, epsilon=0.01)
        ap.apdata.updateDbPv(
            DBFILE, pvrb1, elem_name, 'csch{0:d}rb1'.format(iCh),
            elemHandle='get', tags=tags, quiet=True, epsilon=0.01)

        ap.apdata.updateDbPv(
            DBFILE, pvon, elem_name, 'csch{0:d}_on'.format(iCh),
            elemHandle='put', tags=tags, quiet=True, epsilon=0)

    #
    # Test if the new fields have been correctly added to the database
    #

    ap.machines.loadfast('nsls2', 'SR')

    from cothread.catools import caget

    for e in ap.getElements('EPU'):
        print('## {0}'.format(e.name))

        fld_list, pv_list = [], []
        for i in range(20):
            fld = 'csch{0:d}'.format(i)
            if fld not in e.fields(): continue
            fld_list.append(fld)
            pv_list.append(e.pv(field=fld, handle='setpoint')[0])
        pprint.pprint(list(zip(fld_list, caget(pv_list))))

        fld_list, pv_list = [], []
        for i in range(20):
            fld = 'csch{0:d}'.format(i)
            if fld not in e.fields(): continue
            fld_list.append(fld)
            pv_list.append(e.pv(field=fld, handle='readback')[0])
        pprint.pprint(list(zip(fld_list, caget(pv_list))))

        fld_list, pv_list = [], []
        for i in range(20):
            fld = 'csch{0:d}rb1'.format(i)
            if fld not in e.fields(): continue
            fld_list.append(fld)
            pv_list.append(e.pv(field=fld, handle='readback')[0])
        pprint.pprint(list(zip(fld_list, caget(pv_list))))


        fld_list, pv_list = [], []
        for i in range(20):
            fld = 'csch{0:d}_on'.format(i)
            if fld not in e.fields(): continue
            fld_list.append(fld)
            pv_list.append(e.pv(field=fld, handle='setpoint')[0])
        if fld_list != []:
            pprint.pprint(list(zip(fld_list, caget(pv_list))))

#----------------------------------------------------------------------
def add_unitconv_to_current_strip_channels():
    """"""

    if False: #True: # This section can only run once, as HDF5 file does not
                     # allow overwrite of existing datasets

        kw = dict(compression='gzip')

        _temp_unitconv_file = UNITCONV_FILE + '.tmp'

        fnew = h5py.File(_temp_unitconv_file, 'w')
        fold = h5py.File(UNITCONV_FILE, 'r')

        # First copy existing unit conversion data
        gold = fold['UnitConversion']
        gnew = fnew.create_group('UnitConversion')
        for k, v in gold.items():

            if False: # This will end up with bigger file size
                d = gnew.create_dataset(k, data=v.value, **kw)
            else: # This will end up with smaller file size, so use this one!
                gnew[k] = v.value
                d = gnew[k]

            for ak, av in v.attrs.items():
                put_h5py_attr(d, ak, av)

        # Adding new unit conversions

        ap.machines.loadfast('nsls2', 'SR')

        ids = ap.getElements('EPU')

        for iCh in range(20):

            fld = 'csch{0:d}'.format(iCh)
            _elem_names = [e.name for e in ids if fld in e.fields()]

            d = gnew.create_dataset('EPU_{0}'.format(fld), data=np.array([1.0, 0.0]), **kw)
            uc = {'_class_': 'polynomial', 'dst_unit': 'A', 'dst_unit_sys': 'phy',
                  'elements': _elem_names, 'field': fld,
                  'handle': ['setpoint','readback'],
                  'invertible': 1, 'src_unit': 'A', 'src_unit_sys': ''}
            for k, v in uc.items(): put_h5py_attr(d, k, v)

            fld = 'csch{0:d}rb1'.format(iCh)
            _elem_names = [e.name for e in ids if fld in e.fields()]

            d = gnew.create_dataset('EPU_{0}'.format(fld), data=np.array([1.0, 0.0]), **kw)
            uc = {'_class_': 'polynomial', 'dst_unit': 'A', 'dst_unit_sys': 'phy',
                  'elements': _elem_names, 'field': fld,
                  'handle': ['setpoint','readback'],
                  'invertible': 1, 'src_unit': 'A', 'src_unit_sys': ''}
            for k, v in uc.items(): put_h5py_attr(d, k, v)

        fold.close()
        fnew.close()

        shutil.move(_temp_unitconv_file, UNITCONV_FILE)

    #
    # Test if the unit conversion works
    #

    ap.machines.loadfast('nsls2', 'SR')

    from cothread.catools import caget

    for e in ap.getElements('EPU'):
        print('## {0}'.format(e.name))

        fld_list = []
        for i in range(20):
            fld = 'csch{0:d}'.format(i)
            if fld not in e.fields(): continue
            fld_list.append(fld)
        pprint.pprint(list(zip(
            fld_list, [e.get(fld, unitsys='phy', handle='setpoint')
                       for fld in fld_list])))

        fld_list = []
        for i in range(20):
            fld = 'csch{0:d}'.format(i)
            if fld not in e.fields(): continue
            fld_list.append(fld)
        pprint.pprint(list(zip(
            fld_list, [e.get(fld, unitsys='phy', handle='readback')
                       for fld in fld_list])))

        fld_list = []
        for i in range(20):
            fld = 'csch{0:d}rb1'.format(i)
            if fld not in e.fields(): continue
            fld_list.append(fld)
        pprint.pprint(list(zip(
            fld_list, [e.get(fld, unitsys='phy', handle='readback')
                       for fld in fld_list])))

#----------------------------------------------------------------------
def add_current_strip_ff_pvs():
    """"""

    tags = ['aphla.sys.SR']

    enable_pvs = {
        'epu57g1c02c':
        ['SR:C02-ID:G1A{EPU:1-FFCS:%d}Ena-Sel' % i for i in range(18)],
        'epu57g1c21u':
        ['SR:C21-ID:G1A{EPU:1-FFCS:%d}Ena-Sel' % i for i in range(18)],
        'epu105g1c21d':
        ['SR:C21-ID:G1A{EPU:2-FFCS:%d}Ena-Sel' % i for i in range(18)],
        'epu49g1c23u':
        ['SR:C23-ID:G1A{EPU:1-FFCS:%d}Ena-Sel' % i for i in range(20)],
        'epu49g1c23d':
        ['SR:C23-ID:G1A{EPU:2-FFCS:%d}Ena-Sel' % i for i in range(20)],
    }

    # Add current strip feedforward "Enable" PVs into the database

    for elem_name, pv_list in enable_pvs.items():
        assert elem_name == ap.getElements(elem_name)[0].name
        for iCh, pv in enumerate(pv_list):
            ap.apdata.updateDbPv(
                DBFILE, pv, elem_name, 'csff{0:d}_on'.format(iCh),
                elemHandle='put', tags=tags, quiet=True, epsilon=0)








    epu_gap_pvs = [None for _ in range(4)]
    epu_gap_pvs[0] = {
        'epu57g1c02c':
        ['SR:C02-ID:G1A{EPU:1-FFCS:%d}L2-Calc_.F' % i for i in range(18)],
        'epu57g1c21u':
        ['SR:C21-ID:G1A{EPU:1-FFCS:%d}L2-Calc_.F' % i for i in range(18)],
        'epu105g1c21d':
        ['SR:C21-ID:G1A{EPU:2-FFCS:%d}L2-Calc_.F' % i for i in range(18)],
        'epu49g1c23u':
        ['SR:C23-ID:G1A{EPU:1-FFCS:%d}L2-Calc_.F' % i for i in range(20)],
        'epu49g1c23d':
        ['SR:C23-ID:G1A{EPU:2-FFCS:%d}L2-Calc_.F' % i for i in range(20)],
    }
    for mode_index in range(len(epu_gap_pvs))[1:]:
        _d = {}
        if   mode_index == 1: suffix = 'I'
        elif mode_index == 2: suffix = 'L'
        elif mode_index == 3: suffix = 'O'
        else:
            raise ValueError()
        for elem_name, pv_list in epu_gap_pvs[0].items():
            assert elem_name == ap.getElements(elem_name)[0].name
            _d[elem_name] = [pv[:-1]+suffix for pv in pv_list]
        epu_gap_pvs[mode_index] = _d

    epu_phase_pvs, epu_current_pvs = [], []
    for mode_index, _gap_pv_dict in enumerate(epu_gap_pvs):
        _d = {}
        if   mode_index == 0: suffix = 'G'
        elif mode_index == 1: suffix = 'J'
        elif mode_index == 2: suffix = 'M'
        elif mode_index == 3: suffix = 'P'
        else:
            raise ValueError()
        for elem_name, pv_list in _gap_pv_dict.items():
            assert elem_name == ap.getElements(elem_name)[0].name
            _d[elem_name] = [pv[:-1]+suffix for pv in pv_list]
        epu_phase_pvs.append(_d)

        _d = {}
        if   mode_index == 0: suffix = 'H'
        elif mode_index == 1: suffix = 'K'
        elif mode_index == 2: suffix = 'N'
        elif mode_index == 3: suffix = 'Q'
        else:
            raise ValueError()
        for elem_name, pv_list in _gap_pv_dict.items():
            assert elem_name == ap.getElements(elem_name)[0].name
            _d[elem_name] = [pv[:-1]+suffix for pv in pv_list]
        epu_current_pvs.append(_d)

    # Add current strip feedforward "Gap", "Phase", & "Current" PVs for EPUs
    # into the database
    assert len(epu_gap_pvs) == len(epu_phase_pvs) == len(epu_current_pvs)
    for mode_index, (_gapD, _phaseD, _curD) in enumerate(zip(
        epu_gap_pvs, epu_phase_pvs, epu_current_pvs)):

        for elem_name, pv_list in _gapD.items():
            assert elem_name == ap.getElements(elem_name)[0].name
            for iCh, pv in enumerate(pv_list):
                ap.apdata.updateDbPv(
                    DBFILE, pv, elem_name, 'csff{0:d}_m{1:d}_gap'.format(iCh, mode_index),
                    elemHandle='put', tags=tags, quiet=True, epsilon=0)

        for elem_name, pv_list in _phaseD.items():
            assert elem_name == ap.getElements(elem_name)[0].name
            for iCh, pv in enumerate(pv_list):
                ap.apdata.updateDbPv(
                    DBFILE, pv, elem_name, 'csff{0:d}_m{1:d}_phase'.format(iCh, mode_index),
                    elemHandle='put', tags=tags, quiet=True, epsilon=0)

        for elem_name, pv_list in _curD.items():
            assert elem_name == ap.getElements(elem_name)[0].name
            for iCh, pv in enumerate(pv_list):
                ap.apdata.updateDbPv(
                    DBFILE, pv, elem_name, 'csff{0:d}_m{1:d}_I'.format(iCh, mode_index),
                    elemHandle='put', tags=tags, quiet=True, epsilon=0)


    #
    # Test if the new fields have been correctly added to the database
    #

    ap.machines.loadfast('nsls2', 'SR')

    ids = ap.getElements('EPU')

    unitsys = None

    for prop in ['gap', 'phase', 'I']:

        print('***', prop, '***')

        for e in ids:
            print('## {0}'.format(e.name))
            for iMode in range(4):
                print('-----', 'Mode', iMode, '-----')
                for i in range(20):
                    fld = 'csff{0:d}_m{1:d}_{2}'.format(i, iMode, prop)

                    if fld not in e.fields():
                        break

                    if prop in ('gap', 'phase'):
                        print('* Ch.' + str(i) + ':',
                              e.get(fld, unitsys=unitsys, handle='setpoint'),
                              )
                    else:
                        print('* Ch.' + str(i) + ':',
                              np.max(np.abs(e.get(fld, unitsys=unitsys, handle='setpoint'))),
                              )

#----------------------------------------------------------------------
def add_unitconv_to_current_strip_ff_pvs():
    """"""

    if False: #True: # This section can only run once, as HDF5 file does not
                     # allow overwrite of existing datasets

        kw = dict(compression='gzip')

        _temp_unitconv_file = UNITCONV_FILE + '.tmp'

        fnew = h5py.File(_temp_unitconv_file, 'w')
        fold = h5py.File(UNITCONV_FILE, 'r')

        # First copy existing unit conversion data
        gold = fold['UnitConversion']
        gnew = fnew.create_group('UnitConversion')
        for k, v in gold.items():

            if False: # This will end up with bigger file size
                d = gnew.create_dataset(k, data=v.value, **kw)
            else: # This will end up with smaller file size, so use this one!
                gnew[k] = v.value
                d = gnew[k]

            for ak, av in v.attrs.items():
                put_h5py_attr(d, ak, av)

        # Adding new unit conversions

        ap.machines.loadfast('nsls2', 'SR')

        epu_unitconv_list = [
            ({'gap_src_unit': 'um', 'phase_src_unit': 'um', 'I_src_unit': 'A'},
             ['epu49g1c23u', 'epu49g1c23d']
            ),
            ({'gap_src_unit': 'mm', 'phase_src_unit': 'mm', 'I_src_unit': 'A'},
             ['epu57g1c02c', 'epu57g1c21u', 'epu105g1c21d']
             ),
        ]


        for uc_index, (uc_d, elem_name_list) in enumerate(epu_unitconv_list):

            for iCh in range(20):
                for iMode in range(4):

                    fld_gap   = 'csff{0:d}_m{1:d}_gap'.format(iCh, iMode)
                    fld_phase = 'csff{0:d}_m{1:d}_phase'.format(iCh, iMode)
                    fld_I     = 'csff{0:d}_m{1:d}_I'.format(iCh, iMode)

                    _elem_names = []
                    for e in ap.getElements(elem_name_list):
                        if fld_gap not in e.fields(): continue
                        _elem_names.append(e.name)

                    if _elem_names == []: continue

                    # Save "gap" unit conversion
                    #
                    if uc_d['gap_src_unit'] == 'um':
                        gap_uc = 1e-3
                    elif uc_d['gap_src_unit'] == 'mm':
                        gap_uc = 1.0
                    else:
                        raise ValueError()
                    #
                    d = gnew.create_dataset(
                        'epu_{0}_type{1:d}'.format(fld_gap, uc_index),
                        data=np.array([gap_uc, 0.0]), **kw)
                    uc = {'_class_': 'polynomial', 'dst_unit': 'mm', 'dst_unit_sys': 'phy',
                          'elements': _elem_names, 'field': fld_gap,
                          'handle': ['setpoint',],
                          'invertible': 1, 'src_unit': uc_d['gap_src_unit'], 'src_unit_sys': ''}
                    for k, v in uc.items(): put_h5py_attr(d, k, v)

                    # Save "phase" unit conversion
                    #
                    if uc_d['phase_src_unit'] == 'um':
                        phase_uc = 1e-3
                    elif uc_d['phase_src_unit'] == 'mm':
                        phase_uc = 1.0
                    else:
                        raise ValueError()
                    #
                    d = gnew.create_dataset(
                        'epu_{0}_type{1:d}'.format(fld_phase, uc_index),
                        data=np.array([phase_uc, 0.0]), **kw)
                    uc = {'_class_': 'polynomial', 'dst_unit': 'mm', 'dst_unit_sys': 'phy',
                          'elements': _elem_names, 'field': fld_phase,
                          'handle': ['setpoint',],
                          'invertible': 1, 'src_unit': uc_d['phase_src_unit'], 'src_unit_sys': ''}
                    for k, v in uc.items(): put_h5py_attr(d, k, v)

                    # Save "current" unit conversion
                    #
                    if uc_d['I_src_unit'] == '10uA':
                        I_uc = 1e-5
                    elif uc_d['I_src_unit'] == 'A':
                        I_uc = 1.0
                    else:
                        raise ValueError()
                    #
                    d = gnew.create_dataset(
                        'epu_{0}_type{1:d}'.format(fld_I, uc_index),
                        data=np.array([I_uc, 0.0]), **kw)
                    uc = {'_class_': 'polynomial', 'dst_unit': 'A', 'dst_unit_sys': 'phy',
                          'elements': _elem_names, 'field': fld_I,
                          'handle': ['setpoint',],
                          'invertible': 1, 'src_unit': uc_d['I_src_unit'], 'src_unit_sys': ''}
                    for k, v in uc.items(): put_h5py_attr(d, k, v)

        fold.close()
        fnew.close()

        shutil.move(_temp_unitconv_file, UNITCONV_FILE)

    #
    # Test if the unit conversion works
    #

    ap.machines.loadfast('nsls2', 'SR')

    ids = ap.getElements('EPU')

    unitsys = 'phy' #None

    for prop in ['gap', 'phase', 'I']:

        print('***', prop, '***')

        for e in ids:
            print('## {0}'.format(e.name))
            for iMode in range(4):
                print('-----', 'Mode', iMode, '-----')
                for i in range(20):
                    fld = 'csff{0:d}_m{1:d}_{2}'.format(i, iMode, prop)

                    if fld not in e.fields():
                        break

                    if prop in ('gap', 'phase'):
                        print('* Ch.' + str(i) + ':',
                              e.get(fld, unitsys=unitsys, handle='setpoint'),
                              )
                    else:
                        print('* Ch.' + str(i) + ':',
                              np.max(np.abs(e.get(fld, unitsys=unitsys, handle='setpoint'))),
                              )

#----------------------------------------------------------------------
def add_ff_output_pvs():
    """"""

    ap.machines.loadfast('nsls2', 'SR')

    tags = ['aphla.sys.SR']

    ff_output_pvs = {
        'epu57g1c02c':
        [ap.getElements('epu57g1c02c')[0].pv(
            field='csch{0:d}'.format(i), handle='setpoint')[0] for i in range(1,18+1)],
        'epu57g1c21u':
        [ap.getElements('epu57g1c21u')[0].pv(
            field='csch{0:d}'.format(i), handle='setpoint')[0] for i in range(1,18+1)],
        'epu105g1c21d':
        [ap.getElements('epu105g1c21d')[0].pv(
            field='csch{0:d}'.format(i), handle='setpoint')[0] for i in range(1,18+1)],
        'epu49g1c23u':
        [ap.getElements('epu49g1c23u')[0].pv(
            field='csch{0:d}'.format(i), handle='setpoint')[0] for i in range(20)],
        'epu49g1c23d':
        [ap.getElements('epu49g1c23d')[0].pv(
            field='csch{0:d}'.format(i), handle='setpoint')[0] for i in range(20)],
    }

    # Add current strip feedforward "Output" PVs into the database

    for elem_name, pv_list in ff_output_pvs.items():
        e = ap.getElements(elem_name)[0]
        assert elem_name == e.name

        csff_m0_inds = []
        for fld in e.fields():
            if fld.startswith('csff') and fld.endswith('_m0_I'):
                try:
                    csff_m0_inds.append(int(fld[4:-5]))
                except ValueError:
                    pass
        nFFCh = max(csff_m0_inds) + 1
        assert sorted(csff_m0_inds) == list(range(nFFCh))
        assert len(pv_list) == nFFCh

        for iCh, pv in enumerate(pv_list):
            ap.apdata.updateDbPv(
                DBFILE, pv, elem_name, 'csff{0:d}_output'.format(iCh),
                elemHandle='put', tags=tags, quiet=True, epsilon=0)





    dw_pvs = {}
    for cell in ['08', '18', '28']:

        us = ap.getElements('dw100g1c{cell}u'.format(cell=cell))[0]
        ds = ap.getElements('dw100g1c{cell}d'.format(cell=cell))[0]

        dw_pvs[cell] = (
            [us.pv(field='cch{0:d}'.format(i), handle='setpoint')[0] for i in range(6)] +
            [ds.pv(field='cch{0:d}'.format(i), handle='setpoint')[0] for i in range(6)] +
            [e.pv(field='y_2nd', handle='setpoint')[0] for e in
             ap.getNeighbors(us, 'COR', n=1, elemself=False)]
        )

    ff_output_pvs = {
        'dw100g1c08u': dw_pvs['08'],
        'dw100g1c08d': dw_pvs['08'],
        'dw100g1c18u': dw_pvs['18'],
        'dw100g1c18d': dw_pvs['18'],
        'dw100g1c28u': dw_pvs['28'],
        'dw100g1c28d': dw_pvs['28'],
    }
    for e in ap.getElements('IVU') + ap.getElements('EPU'):
        cch_inds = []
        for fld in e.fields():
            if fld.startswith('cch'):
                try:
                    cch_inds.append(int(fld[3:]))
                except ValueError:
                    pass
        nCch = max(cch_inds) + 1
        assert sorted(cch_inds) == list(range(nCch))

        ff_output_pvs[e.name] = [
            e.pv(field='cch{0:d}'.format(i), handle='setpoint')[0] for i in range(nCch)]

    # Add orbit feedforward "Output" PVs into the database

    for elem_name, pv_list in ff_output_pvs.items():
        e = ap.getElements(elem_name)[0]
        assert elem_name == e.name

        orbff_m0_inds = []
        for fld in e.fields():
            if fld.startswith('orbff') and fld.endswith('_m0_I'):
                try:
                    orbff_m0_inds.append(int(fld[5:-5]))
                except ValueError:
                    pass
        nFFCh = max(orbff_m0_inds) + 1
        assert sorted(orbff_m0_inds) == list(range(nFFCh))
        assert len(pv_list) == nFFCh

        for iCh, pv in enumerate(pv_list):
            ap.apdata.updateDbPv(
                DBFILE, pv, elem_name, 'orbff{0:d}_output'.format(iCh),
                elemHandle='put', tags=tags, quiet=True, epsilon=0)


    #
    # Test if the new fields have been correctly added to the database
    #

    ap.machines.loadfast('nsls2', 'SR')

    from cothread.catools import caget

    for e in ap.getElements('ID'):

        orbff_m0_inds = []
        for fld in e.fields():
            if fld.startswith('orbff') and fld.endswith('_m0_I'):
                try:
                    orbff_m0_inds.append(int(fld[5:-5]))
                except ValueError:
                    pass
        nFFCh = max(orbff_m0_inds) + 1
        assert sorted(orbff_m0_inds) == list(range(nFFCh))

        orbff_m0_inds = sorted(orbff_m0_inds)

        print('** {0} **'.format(e.name))
        pv_list = [
            e.pv(field='orbff{0:d}_output'.format(i), handle='setpoint')[0]
            for i in orbff_m0_inds]
        #
        matching_flds = []
        if e.name.startswith('dw'):
            if e.name.endswith('u'):
                us = e
                ds = ap.getElements(e.name[:-1]+'d')[0]
            else:
                us = ap.getElements(e.name[:-1]+'u')[0]
                ds = e

            for pv in pv_list:
                for fld in us.fields():
                    if fld.startswith('orbff') and fld.endswith('_output'):
                        continue
                    if pv in us.pv(field=fld):
                        matching_flds.append(fld)
                        break
                else:
                    for fld in ds.fields():
                        if fld.startswith('orbff') and fld.endswith('_output'):
                            continue
                        if pv in ds.pv(field=fld):
                            matching_flds.append(fld)
                            break
                    else:
                        _cors = ap.getNeighbors(e, 'COR', n=1, elemself=False)
                        for _c in _cors:
                            for fld in _c.fields():
                                if pv in _c.pv(field=fld):
                                    matching_flds.append((_c.name, fld))
                                    break

        else:
            for pv in pv_list:
                for fld in e.fields():
                    if fld.startswith('orbff') and fld.endswith('_output'):
                        continue
                    if pv in e.pv(field=fld):
                        matching_flds.append(fld)
                        break

        assert len(matching_flds) == len(pv_list)
        #
        for pv, fld, val in zip(pv_list, matching_flds, caget(pv_list)):
            print(pv, fld, val)



    for e in ap.getElements('EPU'):

        csff_m0_inds = []
        for fld in e.fields():
            if fld.startswith('csff') and fld.endswith('_m0_I'):
                try:
                    csff_m0_inds.append(int(fld[4:-5]))
                except ValueError:
                    pass
        nFFCh = max(csff_m0_inds) + 1
        assert sorted(csff_m0_inds) == list(range(nFFCh))

        csff_m0_inds = sorted(csff_m0_inds)

        print('** {0} **'.format(e.name))
        pv_list = [
            e.pv(field='csff{0:d}_output'.format(i), handle='setpoint')[0]
            for i in csff_m0_inds]
        #
        matching_flds = []
        for pv in pv_list:
            for fld in e.fields():
                if fld.startswith('csff') and fld.endswith('_output'):
                    continue
                if pv in e.pv(field=fld):
                    matching_flds.append(fld)
                    break
        assert len(matching_flds) == len(pv_list)
        #
        for pv, fld, val in zip(pv_list, matching_flds, caget(pv_list)):
            print(pv, fld, val)

#----------------------------------------------------------------------
def add_limit_nominal_gap_phase_fields():
    """"""

    ap.machines.loadfast('nsls2', 'SR')

    tags = ['aphla.sys.SR']

    # Open, Closed
    gap_nominal_pvs = {
        'epu57g1c02c': ['SR:C02-ID:NomOpen-Sp', 'SR:C02-ID:NomClose-Sp'],
        'ivu20g1c03c': ['SR:C03-ID:NomOpen-Sp', 'SR:C03-ID:NomClose-Sp'],
        'ivu23g1c04u': ['SR:C04-ID:NomOpen-Sp', 'SR:C04-ID:NomClose-Sp'],
        'ivu21g1c05d': ['SR:C05-ID:NomOpen-Sp', 'SR:C05-ID:NomClose-Sp'],
        'dw100g1c08u': ['SR:C08-ID:NomOpen-Sp', 'SR:C08-ID:NomClose-Sp'],
        'dw100g1c08d': ['SR:C08-ID:NomOpen-Sp', 'SR:C08-ID:NomClose-Sp'],
        'ivu22g1c10c': ['SR:C10-ID:NomOpen-Sp', 'SR:C10-ID:NomClose-Sp'],
        'ivu20g1c11c': ['SR:C11-ID:NomOpen-Sp', 'SR:C11-ID:NomClose-Sp'],
        'ivu23g1c12d': ['SR:C12-ID:NomOpen-Sp', 'SR:C12-ID:NomClose-Sp'],
        'ivu23g1c16c': ['SR:C16-ID:NomOpen-Sp', 'SR:C16-ID:NomClose-Sp'],
        'ivu21g1c17u': ['SR:C17-1-ID:NomOpen-Sp', 'SR:C17-1-ID:NomClose-Sp'],
        'ivu21g1c17d': ['SR:C17-2-ID:NomOpen-Sp', 'SR:C17-2-ID:NomClose-Sp'],
        'dw100g1c18u': ['SR:C18-ID:NomOpen-Sp', 'SR:C18-ID:NomClose-Sp'],
        'dw100g1c18d': ['SR:C18-ID:NomOpen-Sp', 'SR:C18-ID:NomClose-Sp'],
        'ivu18g1c19u': ['SR:C19-1-ID:NomOpen-Sp', 'SR:C19-1-ID:NomClose-Sp'],
        'epu57g1c21u': ['SR:C21-1-ID:NomOpen-Sp', 'SR:C21-1-ID:NomClose-Sp'],
        'epu105g1c21d': ['SR:C21-2-ID:NomOpen-Sp', 'SR:C21-2-ID:NomClose-Sp'],
        'epu49g1c23u': ['SR:C23-1-ID:NomOpen-Sp', 'SR:C23-1-ID:NomClose-Sp'],
        'epu49g1c23d': ['SR:C23-2-ID:NomOpen-Sp', 'SR:C23-2-ID:NomClose-Sp'],
        'dw100g1c28u': ['SR:C28-ID:NomOpen-Sp', 'SR:C28-ID:NomClose-Sp'],
        'dw100g1c28d': ['SR:C28-ID:NomOpen-Sp', 'SR:C28-ID:NomClose-Sp'],
    }

    # Max, Min
    gap_limit_pvs = {
        'epu57g1c02c': ['SR:C02-ID:G1A{EPU:1-Ax:Gap}Lim:Max-RB',
                        'SR:C02-ID:G1A{EPU:1-Ax:Gap}Lim:Min-RB'],
        'ivu20g1c03c': ['SR:C3-ID:G1{IVU20:1-Mtr:2}Inp:Pos.DRVH',
                        'SR:C3-ID:G1{IVU20:1-Mtr:2}Inp:Pos.DRVL'],
        'ivu23g1c04u': ['SR:C04-ID:G1{IVU:1-Mtr:2}Inp:Pos.DRVH',
                        'SR:C04-ID:G1{IVU:1-Mtr:2}Inp:Pos.DRVL'],
        'ivu21g1c05d': ['SR:C5-ID:G1{IVU21:1-Mtr:2}Inp:Pos.DRVH',
                        'SR:C5-ID:G1{IVU21:1-Mtr:2}Inp:Pos.DRVL'],
        'dw100g1c08u': ['SR:C08-ID:G1{DW100:1}Man:SP:Gap.DRVH',
                        'SR:C08-ID:G1{DW100:1}Man:SP:Gap.DRVL'],
        'dw100g1c08d': ['SR:C08-ID:G1{DW100:2}Man:SP:Gap.DRVH',
                        'SR:C08-ID:G1{DW100:2}Man:SP:Gap.DRVL'],
        'ivu22g1c10c': ['SR:C10-ID:G1{IVU22:1}Man:SP:Gap.DRVH',
                        'SR:C10-ID:G1{IVU22:1}Man:SP:Gap.DRVL'],
        'ivu20g1c11c': ['SR:C11-ID:G1{IVU20:1-Mtr:2}Inp:Pos.DRVH',
                        'SR:C11-ID:G1{IVU20:1-Mtr:2}Inp:Pos.DRVL'],
        'ivu23g1c12d': ['SR:C12-ID:G1{IVU:1-Mtr:2}Inp:Pos.DRVH',
                        'SR:C12-ID:G1{IVU:1-Mtr:2}Inp:Pos.DRVL'],
        'ivu23g1c16c': ['SR:C16-ID:G1{IVU:1-Mtr:2}Inp:Pos.DRVH',
                        'SR:C16-ID:G1{IVU:1-Mtr:2}Inp:Pos.DRVL'],
        'ivu21g1c17u': ['SR:C17-ID:G1{IVU21:1-Mtr:2}Inp:Pos.DRVH',
                        'SR:C17-ID:G1{IVU21:1-Mtr:2}Inp:Pos.DRVL'],
        'ivu21g1c17d': ['SR:C17-ID:G1{IVU21:2-Mtr:2}Inp:Pos.DRVH',
                        'SR:C17-ID:G1{IVU21:2-Mtr:2}Inp:Pos.DRVL'],
        'dw100g1c18u': ['SR:C18-ID:G1{DW100:1}Man:SP:Gap.DRVH',
                        'SR:C18-ID:G1{DW100:1}Man:SP:Gap.DRVL'],
        'dw100g1c18d': ['SR:C18-ID:G1{DW100:2}Man:SP:Gap.DRVH',
                        'SR:C18-ID:G1{DW100:2}Man:SP:Gap.DRVL'],
        'ivu18g1c19u': ['SR:C19-ID:G1A{NYX:1-Ax:Gap}-Mtr-SP.DRVH',
                        'SR:C19-ID:G1A{NYX:1-Ax:Gap}-Mtr-SP.DRVL'],
        'epu57g1c21u': ['SR:C21-ID:G1A{EPU:1-Ax:Gap}Lim:Max-RB',
                        'SR:C21-ID:G1A{EPU:1-Ax:Gap}Lim:Min-RB'],
        'epu105g1c21d': ['SR:C21-ID:G1B{EPU:2-Ax:Gap}Lim:Max-RB',
                         'SR:C21-ID:G1B{EPU:2-Ax:Gap}Lim:Min-RB'],
        'epu49g1c23u': ['SR:C23-ID:G1A{EPU:1-Ax:Gap}-Mtr-SP.DRVH',
                        'SR:C23-ID:G1A{EPU:1-Ax:Gap}-Mtr-SP.DRVL'],
        'epu49g1c23d': ['SR:C23-ID:G1A{EPU:2-Ax:Gap}-Mtr-SP.DRVH',
                        'SR:C23-ID:G1A{EPU:2-Ax:Gap}-Mtr-SP.DRVL'],
        'dw100g1c28u': ['SR:C28-ID:G1{DW100:1}Man:SP:Gap.DRVH',
                        'SR:C28-ID:G1{DW100:1}Man:SP:Gap.DRVL'],
        'dw100g1c28d': ['SR:C28-ID:G1{DW100:2}Man:SP:Gap.DRVH',
                        'SR:C28-ID:G1{DW100:2}Man:SP:Gap.DRVL'],
    }

    phase_limit_pvs = {
        'epu57g1c02c': ['SR:C02-ID:G1A{EPU:1-Ax:Phase}Lim:Max-RB',
                        'SR:C02-ID:G1A{EPU:1-Ax:Phase}Lim:Min-RB'],
        'epu57g1c21u': ['SR:C21-ID:G1A{EPU:1-Ax:Phase}Lim:Max-RB',
                        'SR:C21-ID:G1A{EPU:1-Ax:Phase}Lim:Min-RB'],
        'epu105g1c21d': ['SR:C21-ID:G1B{EPU:2-Ax:Phase}Lim:Max-RB',
                         'SR:C21-ID:G1B{EPU:2-Ax:Phase}Lim:Min-RB'],
        'epu49g1c23u': ['SR:C23-ID:G1A{EPU:1-Ax:Phase}-Mtr-SP.DRVH',
                        'SR:C23-ID:G1A{EPU:1-Ax:Phase}-Mtr-SP.DRVL'],
        'epu49g1c23d': ['SR:C23-ID:G1A{EPU:2-Ax:Phase}-Mtr-SP.DRVH',
                        'SR:C23-ID:G1A{EPU:2-Ax:Phase}-Mtr-SP.DRVL'],
    }

    # Add limit/nominal gap/phase PVs into the database

    for elem_name, pv_list in gap_nominal_pvs.items():
        e = ap.getElements(elem_name)[0]
        assert elem_name == e.name

        ap.apdata.updateDbPv(
            DBFILE, pv_list[0], elem_name, 'gap_hinominal',
            elemHandle='get', tags=tags, quiet=True, epsilon=0)
        ap.apdata.updateDbPv(
            DBFILE, pv_list[1], elem_name, 'gap_lonominal',
            elemHandle='get', tags=tags, quiet=True, epsilon=0)

    for elem_name, pv_list in gap_limit_pvs.items():
        e = ap.getElements(elem_name)[0]
        assert elem_name == e.name

        ap.apdata.updateDbPv(
            DBFILE, pv_list[0], elem_name, 'gap_hilim',
            elemHandle='get', tags=tags, quiet=True, epsilon=0)
        ap.apdata.updateDbPv(
            DBFILE, pv_list[1], elem_name, 'gap_lolim',
            elemHandle='get', tags=tags, quiet=True, epsilon=0)

    for elem_name, pv_list in phase_limit_pvs.items():
        e = ap.getElements(elem_name)[0]
        assert elem_name == e.name

        ap.apdata.updateDbPv(
            DBFILE, pv_list[0], elem_name, 'phase_hilim',
            elemHandle='get', tags=tags, quiet=True, epsilon=0)
        ap.apdata.updateDbPv(
            DBFILE, pv_list[1], elem_name, 'phase_lolim',
            elemHandle='get', tags=tags, quiet=True, epsilon=0)

    #
    # Test if the new fields have been correctly added to the database
    #

    ap.machines.loadfast('nsls2', 'SR')

    for e in ap.getElements('ID'):
        print('** {0} **'.format(e.name))
        print('Gap Nominal (Closed, Open):', e.gap_lonominal, e.gap_hinominal)
        print('Gap Limit (Min, Max):', e.gap_lolim, e.gap_hilim)
        if 'EPU' in e.group:
            print('Phase Limit (Min, Max):', e.phase_lolim, e.phase_hilim)

#----------------------------------------------------------------------
def add_unitconv_to_limit_nominal_gap_phase_fields():
    """"""

    if False: #True: # This section can only run once, as HDF5 file does not
                     # allow overwrite of existing datasets

        kw = dict(compression='gzip')

        _temp_unitconv_file = UNITCONV_FILE + '.tmp'

        fnew = h5py.File(_temp_unitconv_file, 'w')
        fold = h5py.File(UNITCONV_FILE, 'r')

        # First copy existing unit conversion data
        gold = fold['UnitConversion']
        gnew = fnew.create_group('UnitConversion')
        for k, v in gold.items():

            if False: # This will end up with bigger file size
                d = gnew.create_dataset(k, data=v.value, **kw)
            else: # This will end up with smaller file size, so use this one!
                gnew[k] = v.value
                d = gnew[k]

            for ak, av in v.attrs.items():
                put_h5py_attr(d, ak, av)

        # Adding new unit conversions

        ap.machines.loadfast('nsls2', 'SR')

        ivu_unitconv_list = [
            ({'gap_src_unit': 'mm',},
             ['ivu20g1c03c',
              'ivu23g1c04u',
              'ivu21g1c05d',
              'ivu20g1c11c',
              'ivu23g1c12d',
              'ivu23g1c16c',
              'ivu21g1c17u',
              'ivu21g1c17d',]
             ),
            ({'gap_src_unit': 'um',},
             ['ivu22g1c10c',
              'ivu18g1c19u',]
             ),
        ]

        for uc_index, (uc_d, elem_name_list) in enumerate(ivu_unitconv_list):

            for fld in ['gap_hilim', 'gap_lolim',
                        'gap_hinominal', 'gap_lonominal']:

                _elem_names = []
                for e in ap.getElements(elem_name_list):
                    if fld not in e.fields():
                        raise RuntimeError()
                    _elem_names.append(e.name)

                if _elem_names == []:
                    raise RuntimeError()

                # Save "gap_*" unit conversion
                #
                if uc_d['gap_src_unit'] == 'um':
                    gap_uc = 1e-3
                elif uc_d['gap_src_unit'] == 'mm':
                    gap_uc = 1.0
                else:
                    raise ValueError()
                #
                d = gnew.create_dataset(
                    'ivu_{0}_type{1:d}'.format(fld, uc_index),
                    data=np.array([gap_uc, 0.0]), **kw)
                uc = {'_class_': 'polynomial', 'dst_unit': 'mm', 'dst_unit_sys': 'phy',
                      'elements': _elem_names, 'field': fld,
                      'handle': ['readback',],
                      'invertible': 1, 'src_unit': uc_d['gap_src_unit'], 'src_unit_sys': ''}
                for k, v in uc.items(): put_h5py_attr(d, k, v)


        epu_unitconv_list = [
            ({'gap_src_unit': 'um', 'phase_src_unit': 'um',},
             ['epu49g1c23u', 'epu49g1c23d']
            ),
            ({'gap_src_unit': 'mm', 'phase_src_unit': 'mm',},
             ['epu57g1c02c', 'epu57g1c21u', 'epu105g1c21d']
             ),
        ]


        for uc_index, (uc_d, elem_name_list) in enumerate(epu_unitconv_list):

            for fld in ['gap_hilim', 'gap_lolim',
                        'gap_hinominal', 'gap_lonominal']:

                _elem_names = []
                for e in ap.getElements(elem_name_list):
                    if fld not in e.fields():
                        raise RuntimeError()
                    _elem_names.append(e.name)

                if _elem_names == []:
                    raise RuntimeError()

                # Save "gap_*" unit conversion
                #
                if uc_d['gap_src_unit'] == 'um':
                    gap_uc = 1e-3
                elif uc_d['gap_src_unit'] == 'mm':
                    gap_uc = 1.0
                else:
                    raise ValueError()
                #
                d = gnew.create_dataset(
                    'epu_{0}_type{1:d}'.format(fld, uc_index),
                    data=np.array([gap_uc, 0.0]), **kw)
                uc = {'_class_': 'polynomial', 'dst_unit': 'mm', 'dst_unit_sys': 'phy',
                      'elements': _elem_names, 'field': fld,
                      'handle': ['readback',],
                      'invertible': 1, 'src_unit': uc_d['gap_src_unit'], 'src_unit_sys': ''}
                for k, v in uc.items(): put_h5py_attr(d, k, v)

            for fld in ['phase_hilim', 'phase_lolim']:

                _elem_names = []
                for e in ap.getElements(elem_name_list):
                    if fld not in e.fields():
                        raise RuntimeError()
                    _elem_names.append(e.name)

                if _elem_names == []:
                    raise RuntimeError()

                # Save "phase_*" unit conversion
                #
                if uc_d['phase_src_unit'] == 'um':
                    phase_uc = 1e-3
                elif uc_d['phase_src_unit'] == 'mm':
                    phase_uc = 1.0
                else:
                    raise ValueError()
                #
                d = gnew.create_dataset(
                    'epu_{0}_type{1:d}'.format(fld, uc_index),
                    data=np.array([phase_uc, 0.0]), **kw)
                uc = {'_class_': 'polynomial', 'dst_unit': 'mm', 'dst_unit_sys': 'phy',
                      'elements': _elem_names, 'field': fld,
                      'handle': ['readback',],
                      'invertible': 1, 'src_unit': uc_d['phase_src_unit'], 'src_unit_sys': ''}
                for k, v in uc.items(): put_h5py_attr(d, k, v)



        dw_unitconv_list = [
            ({'gap_src_unit': 'um'},
             ['dw100g1c08u', 'dw100g1c08d', 'dw100g1c18u', 'dw100g1c18d',
              'dw100g1c28u', 'dw100g1c28d']
            ),
        ]

        for uc_index, (uc_d, elem_name_list) in enumerate(dw_unitconv_list):

            for fld in ['gap_hilim', 'gap_lolim',
                        'gap_hinominal', 'gap_lonominal']:

                _elem_names = []
                for e in ap.getElements(elem_name_list):
                    if fld not in e.fields():
                        raise RuntimeError()
                    _elem_names.append(e.name)

                if _elem_names == []:
                    raise RuntimeError()

                # Save "gap_*" unit conversion
                #
                if uc_d['gap_src_unit'] == 'um':
                    gap_uc = 1e-3
                elif uc_d['gap_src_unit'] == 'mm':
                    gap_uc = 1.0
                else:
                    raise ValueError()
                #
                d = gnew.create_dataset(
                    'dw_{0}_type{1:d}'.format(fld, uc_index),
                    data=np.array([gap_uc, 0.0]), **kw)
                uc = {'_class_': 'polynomial', 'dst_unit': 'mm', 'dst_unit_sys': 'phy',
                      'elements': _elem_names, 'field': fld,
                      'handle': ['readback',],
                      'invertible': 1, 'src_unit': uc_d['gap_src_unit'], 'src_unit_sys': ''}
                for k, v in uc.items(): put_h5py_attr(d, k, v)


        fold.close()
        fnew.close()

        shutil.move(_temp_unitconv_file, UNITCONV_FILE)

    #
    # Test if the unit conversion works
    #

    ap.machines.loadfast('nsls2', 'SR')

    for e in ap.getElements('ID'):
        print('** {0} **'.format(e.name))
        print('# unitsys = None #')
        print('[Raw] Gap Nominal (Closed, Open):',
              e.get('gap_lonominal', handle='readback', unitsys=None),
              e.get('gap_hinominal', handle='readback', unitsys=None),)
        print('[Raw] Gap Limit (Min, Max):',
              e.get('gap_lolim', handle='readback', unitsys=None),
              e.get('gap_hilim', handle='readback', unitsys=None),)
        if 'EPU' in e.group:
            print('[Raw] Phase Limit (Min, Max):',
                  e.get('phase_lolim', handle='readback', unitsys=None),
                  e.get('phase_hilim', handle='readback', unitsys=None),)
        print('# unitsys = phy #')
        print('[Phy] Gap Nominal (Closed, Open):',
              e.get('gap_lonominal', handle='readback', unitsys='phy'),
              e.get('gap_hinominal', handle='readback', unitsys='phy'),)
        print('[Phy] Gap Limit (Min, Max):',
              e.get('gap_lolim', handle='readback', unitsys='phy'),
              e.get('gap_hilim', handle='readback', unitsys='phy'),)
        if 'EPU' in e.group:
            print('[Phy] Phase Limit (Min, Max):',
                  e.get('phase_lolim', handle='readback', unitsys='phy'),
                  e.get('phase_hilim', handle='readback', unitsys='phy'),)

#----------------------------------------------------------------------
def add_gap_phase_speed_fields():
    """"""

    ap.machines.loadfast('nsls2', 'SR')

    tags = ['aphla.sys.SR']

    # (setpoint), (readback)
    gap_speed_pvs = {
        'epu57g1c02c': ['SR:C02-ID:G1A{EPU:1-Ax:Gap}S-SP',
                        'SR:C02-ID:G1A{EPU:1-Ax:Gap}S-I'],
        'ivu20g1c03c': ['SR:C3-ID:G1{IVU20:1-Mtr:2}S',
                        'SR:C3-ID:G1{IVU20:1-Mtr:2}S:RB'],
        'ivu23g1c04u': ['SR:C04-ID:G1{IVU:1-Mtr:1}S',
                        'SR:C04-ID:G1{IVU:1-Mtr:1}S:RB'],
        'ivu21g1c05d': ['SR:C5-ID:G1{IVU21:1-Mtr:2}S',
                        'SR:C5-ID:G1{IVU21:1-Mtr:2}S:RB'],
        'dw100g1c08u': ['', ''],
        'dw100g1c08d': ['', ''],
        'ivu22g1c10c': ['SR:C10-ID:G1{IVU22:1-Mtr:Gap}.VELO',
                        ''],
        'ivu20g1c11c': ['SR:C11-ID:G1{IVU20:1-Mtr:2}S',
                        'SR:C11-ID:G1{IVU20:1-Mtr:2}S:RB'],
        'ivu23g1c12d': ['SR:C12-ID:G1{IVU:1-Mtr:1}S',
                        'SR:C12-ID:G1{IVU:1-Mtr:1}S:RB'],
        'ivu23g1c16c': ['SR:C16-ID:G1{IVU:1-Mtr:1}S',
                        'SR:C16-ID:G1{IVU:1-Mtr:1}S:RB'],
        'ivu21g1c17u': ['SR:C17-ID:G1{IVU21:1-Mtr:2}S',
                        'SR:C17-ID:G1{IVU21:1-Mtr:2}S:RB'],
        'ivu21g1c17d': ['SR:C17-ID:G1{IVU21:2-Mtr:2}S',
                        'SR:C17-ID:G1{IVU21:2-Mtr:2}S:RB'],
        'dw100g1c18u': ['', ''],
        'dw100g1c18d': ['', ''],
        'ivu18g1c19u': ['', ''], # according to Harman, gap speed PV exists, but not actually implemented in hardware
        'epu57g1c21u': ['SR:C21-ID:G1A{EPU:1-Ax:Gap}S-SP',
                        'SR:C21-ID:G1A{EPU:1-Ax:Gap}S-I'],
        'epu105g1c21d': ['SR:C21-ID:G1B{EPU:2-Ax:Gap}S-SP',
                         'SR:C21-ID:G1B{EPU:2-Ax:Gap}S-I'],
        'epu49g1c23u': ['SR:C23-ID:G1A{EPU:1-Ax:Gap}-Mtr.VELO',
                        ''],
        'epu49g1c23d': ['SR:C23-ID:G1A{EPU:2-Ax:Gap}-Mtr.VELO',
                        ''],
        'dw100g1c28u': ['', ''],
        'dw100g1c28d': ['', ''],
    }

    # (setpoint), (readback)
    phase_speed_pvs = {
        'epu57g1c02c': ['SR:C02-ID:G1A{EPU:1-Ax:Phase}S-SP',
                        'SR:C02-ID:G1A{EPU:1-Ax:Phase}S-I'],
        'epu57g1c21u': ['SR:C21-ID:G1A{EPU:1-Ax:Phase}S-SP',
                        'SR:C21-ID:G1A{EPU:1-Ax:Phase}S-I'],
        'epu105g1c21d': ['SR:C21-ID:G1B{EPU:2-Ax:Phase}S-SP',
                         'SR:C21-ID:G1B{EPU:2-Ax:Phase}S-I'],
        'epu49g1c23u': ['SR:C23-ID:G1A{EPU:1-Ax:Phase}-Mtr.VELO',
                        ''],
        'epu49g1c23d': ['SR:C23-ID:G1A{EPU:2-Ax:Phase}-Mtr.VELO',
                        ''],

    }

    # Add gap speed PVs into the database
    for elem_name, pv_list in gap_speed_pvs.items():
        e = ap.getElements(elem_name)[0]
        assert elem_name == e.name

        pvsp, pvrb = pv_list

        if pvsp != '':
            ap.apdata.updateDbPv(
                DBFILE, pvsp, elem_name, 'gap_speed',
                elemHandle='put', tags=tags, quiet=True, epsilon=0)
        if pvrb != '':
            ap.apdata.updateDbPv(
                DBFILE, pvrb, elem_name, 'gap_speed',
                elemHandle='get', tags=tags, quiet=True, epsilon=0)

    # Add phase speed PVs into the database
    for elem_name, pv_list in phase_speed_pvs.items():
        e = ap.getElements(elem_name)[0]
        assert elem_name == e.name

        pvsp, pvrb = pv_list

        if pvsp != '':
            ap.apdata.updateDbPv(
                DBFILE, pvsp, elem_name, 'phase_speed',
                elemHandle='put', tags=tags, quiet=True, epsilon=0)
        if pvrb != '':
            ap.apdata.updateDbPv(
                DBFILE, pvrb, elem_name, 'phase_speed',
                elemHandle='get', tags=tags, quiet=True, epsilon=0)

    #
    # Test if the new fields have been correctly added to the database
    #

    ap.machines.loadfast('nsls2', 'SR')

    for e in ap.getElements('ID'):
        print('** {0} **'.format(e.name))
        if 'gap_speed' not in e.fields(): continue
        print('Gap Speed:',
              e.get('gap_speed', handle='setpoint', unitsys=None),
              e.get('gap_speed', handle='readback', unitsys=None),
              )
        if 'EPU' in e.group:
            if 'phase_speed' not in e.fields(): continue
            print('Phase Speed:',
                  e.get('phase_speed', handle='setpoint', unitsys=None),
                  e.get('phase_speed', handle='readback', unitsys=None),
                  )

#----------------------------------------------------------------------
def add_unitconv_gap_phase_speed_pvs():
    """"""

    if False: #True: # This section can only run once, as HDF5 file does not
                     # allow overwrite of existing datasets

        kw = dict(compression='gzip')

        _temp_unitconv_file = UNITCONV_FILE + '.tmp'

        fnew = h5py.File(_temp_unitconv_file, 'w')
        fold = h5py.File(UNITCONV_FILE, 'r')

        # First copy existing unit conversion data
        gold = fold['UnitConversion']
        gnew = fnew.create_group('UnitConversion')
        for k, v in gold.items():

            if False: # This will end up with bigger file size
                d = gnew.create_dataset(k, data=v.value, **kw)
            else: # This will end up with smaller file size, so use this one!
                gnew[k] = v.value
                d = gnew[k]

            for ak, av in v.attrs.items():
                put_h5py_attr(d, ak, av)

        # Adding new unit conversions

        ap.machines.loadfast('nsls2', 'SR')

        ivu_unitconv_list = [
            ({'gap_speed_src_unit': 'mm/s',},
             ['ivu20g1c03c',
              'ivu23g1c04u',
              'ivu21g1c05d',
              'ivu20g1c11c',
              'ivu23g1c12d',
              'ivu23g1c16c',
              'ivu21g1c17u',
              'ivu21g1c17d',]
             ),
            ({'gap_speed_src_unit': 'um/s',},
             ['ivu22g1c10c',
              ]
             ),
        ]

        for uc_index, (uc_d, elem_name_list) in enumerate(ivu_unitconv_list):

            fld = 'gap_speed'

            _elem_names = []
            for e in ap.getElements(elem_name_list):
                if fld not in e.fields():
                    raise RuntimeError()
                _elem_names.append(e.name)

            if _elem_names == []:
                raise RuntimeError()

            # Save "gap_speed" unit conversion
            #
            if uc_d['gap_speed_src_unit'] == 'um/s':
                gap_speed_uc = 1e-3
            elif uc_d['gap_speed_src_unit'] == 'mm/s':
                gap_speed_uc = 1.0
            else:
                raise ValueError()
            #
            d = gnew.create_dataset(
                'ivu_{0}_type{1:d}'.format(fld, uc_index),
                data=np.array([gap_speed_uc, 0.0]), **kw)
            uc = {'_class_': 'polynomial', 'dst_unit': 'mm/s', 'dst_unit_sys': 'phy',
                  'elements': _elem_names, 'field': fld,
                  'handle': ['readback','setpoint'],
                  'invertible': 1, 'src_unit': uc_d['gap_speed_src_unit'], 'src_unit_sys': ''}
            for k, v in uc.items(): put_h5py_attr(d, k, v)


        epu_unitconv_list = [
            ({'gap_speed_src_unit': 'um/s', 'phase_speed_src_unit': 'um/s',},
             ['epu49g1c23u', 'epu49g1c23d']
            ),
            ({'gap_speed_src_unit': 'mm/s', 'phase_speed_src_unit': 'mm/s',},
             ['epu57g1c02c', 'epu57g1c21u', 'epu105g1c21d']
             ),
        ]


        for uc_index, (uc_d, elem_name_list) in enumerate(epu_unitconv_list):

            fld = 'gap_speed'

            _elem_names = []
            for e in ap.getElements(elem_name_list):
                if fld not in e.fields():
                    raise RuntimeError()
                _elem_names.append(e.name)

            if _elem_names == []:
                raise RuntimeError()

            # Save "gap_speed" unit conversion
            #
            if uc_d['gap_speed_src_unit'] == 'um/s':
                gap_speed_uc = 1e-3
            elif uc_d['gap_speed_src_unit'] == 'mm/s':
                gap_speed_uc = 1.0
            else:
                raise ValueError()
            #
            d = gnew.create_dataset(
                'epu_{0}_type{1:d}'.format(fld, uc_index),
                data=np.array([gap_speed_uc, 0.0]), **kw)
            uc = {'_class_': 'polynomial', 'dst_unit': 'mm/s', 'dst_unit_sys': 'phy',
                  'elements': _elem_names, 'field': fld,
                  'handle': ['readback','setpoint'],
                  'invertible': 1, 'src_unit': uc_d['gap_speed_src_unit'], 'src_unit_sys': ''}
            for k, v in uc.items(): put_h5py_attr(d, k, v)



            fld = 'phase_speed'

            _elem_names = []
            for e in ap.getElements(elem_name_list):
                if fld not in e.fields():
                    raise RuntimeError()
                _elem_names.append(e.name)

            if _elem_names == []:
                raise RuntimeError()

            # Save "phase_speed" unit conversion
            #
            if uc_d['phase_speed_src_unit'] == 'um/s':
                phase_speed_uc = 1e-3
            elif uc_d['phase_speed_src_unit'] == 'mm/s':
                phase_speed_uc = 1.0
            else:
                raise ValueError()
            #
            d = gnew.create_dataset(
                'epu_{0}_type{1:d}'.format(fld, uc_index),
                data=np.array([phase_speed_uc, 0.0]), **kw)
            uc = {'_class_': 'polynomial', 'dst_unit': 'mm/s', 'dst_unit_sys': 'phy',
                  'elements': _elem_names, 'field': fld,
                  'handle': ['readback','setpoint'],
                  'invertible': 1, 'src_unit': uc_d['phase_speed_src_unit'], 'src_unit_sys': ''}
            for k, v in uc.items(): put_h5py_attr(d, k, v)

        fold.close()
        fnew.close()

        shutil.move(_temp_unitconv_file, UNITCONV_FILE)

    #
    # Test if the new fields have been correctly added to the database
    #

    ap.machines.loadfast('nsls2', 'SR')

    for e in ap.getElements('ID'):
        print('** {0} **'.format(e.name))
        if 'gap_speed' not in e.fields(): continue
        print('Gap Speed:',
              e.get('gap_speed', handle='setpoint', unitsys='phy'),
              e.get('gap_speed', handle='readback', unitsys='phy'),
              )
        if 'EPU' in e.group:
            if 'phase_speed' not in e.fields(): continue
            print('Phase Speed:',
                  e.get('phase_speed', handle='setpoint', unitsys='phy'),
                  e.get('phase_speed', handle='readback', unitsys='phy'),
                  )
#----------------------------------------------------------------------
def add_SST_fake_ID():
    """"""

    cell_num = 7

    print_elems_around_straight(cell_num, n=5)

    # s-pos of center of straight
    sc = SR_CIRCUMF / 30 * cell_num # [m]

    # Neighbor FCOR indexes = 66800, 67500
    id_index = 67000

    # Add fake SST ID at center of straight
    elemLength = 1.0
    elemName, sEnd = 'sst', 184.0

    kw = dict(elemType   = 'SST',
              cell       = 'C{0:02d}'.format(cell_num),
              girder     = 'G1',
              symmetry   = 'D',
              elemGroups = 'SST;ID;Partner',
              elemIndex  = id_index,
              elemLength = elemLength,
              )
    ap.apdata.updateDbElement(DBFILE, 'SR', elemName, elemPosition=sEnd, **kw)

    bpm_info = [
        ('pu1g1c07a', 182.5552, 'PU1', 66900),
        ('pu2g1c07a', 184.7152, 'PU2', 67100),
        ('pu3g1c07a', 184.865 , 'PU3', 67300),
        ('pu4g1c07a', 187.0252, 'PU4', 67400),
    ]

    # #### Adding elements for UBPMs to database ####
    for elemName, sEnd, ugg, idx in bpm_info:
        kw = dict(elemType   = 'UBPM_',
                  cell       = 'C{0:02d}'.format(cell_num),
                  girder     = 'G1',
                  symmetry   = 'A',
                  elemGroups = 'UBPM;'+ugg,
                  elemIndex  = idx,
                  elemLength = 0.0,
                  )
        ap.apdata.updateDbElement(DBFILE, 'SR', elemName, elemPosition=sEnd, **kw)

    elemName_prefix_devName_tups = [
        ('pu1g1c07a', 'SR:C07-BI{BPM:7}', 'C07-BPM7'),
        ('pu2g1c07a', 'SR:C07-BI{BPM:8}', 'C07-BPM8'),
        ('pu3g1c07a', 'SR:C07-BI{BPM:9}', 'C07-BPM9'),
        ('pu4g1c07a', 'SR:C07-BI{BPM:10}', 'C07-BPM10'),
    ]

    # #### Adding PVs for UBPM elements to database ####
    for elemName, prefix, devName in elemName_prefix_devName_tups:
        tags = ['aphla.sys.SR']
        # ^ required, otherwise can not be load by `machines.load("nsls2", "SR")`
        for pvpf, fld, hdl in BPM_PV_REC:
            if pvpf != 'Pos:XwUsrOff-Calc':
                ap.apdata.updateDbPv(
                    DBFILE, prefix + pvpf, elemName, fld, elemHandle=hdl, tags=tags,
                    quiet=True)
            else:
                ap.apdata.updateDbPv(
                    DBFILE, prefix + pvpf, elemName, fld, elemHandle=hdl, tags=tags,
                    quiet=True, devName=devName)

    ap.machines.load('nsls2', 'SR')


    plt.show()

#----------------------------------------------------------------------
def add_SST_ID_elems():
    """"""

    pt.rdmfile('/home/yhidaka/.pytracy_control/20170905_bare.flat')

    cell_list = pt.getCell()
    sall = np.array(pt.getS())

    us_id = pts.getElemIndexesFromName('IDC07H1')[0]
    s_us_id = pt.getS()[us_id]

    ds_id = pts.getElemIndexesFromName('IDC07H2')[0]
    s_ds_id = pt.getS()[ds_id]

    sexts = pts.getElemIndexesFromRegExPattern(r'^S[HLM]\w+$')
    s_sexts = np.array(pt.getS())[sexts]
    us_sext, ds_sext = sorted(np.array(sexts)[np.argsort(np.abs(s_sexts - s_us_id))[:2]])

    # Straight center position in the lattice file
    pt_sc = (sall[ds_sext-1] + sall[us_sext])/2.0
    print('\n# s-pos of straight center (PyTracy lattice file): {0:.9f}'.format(pt_sc))

    # print all element names in the lattice file in this straight
    elem_inds = list(range(us_sext, ds_sext+1))
    elem_names = pts.getFamNamesFromElemIndexes(elem_inds)
    sb_elems = sall[np.array(elem_inds)-1]
    se_elems = sall[elem_inds]
    print('\n(Elem. Names)          (sb)            (se)')
    for name, sb, se in zip(elem_names, sb_elems, se_elems):
        print('{0:15} : {1:.9f}   {2:.9f}'.format(name, sb ,se))

    cap_ubpm_names = ['PU1G1C07A', 'PU2G1C07A', 'PU3G1C07A', 'PU4G1C07A']

    pt_ubpms = pts.getElemIndexesFromFamNames(cap_ubpm_names)
    s_ubpms = sall[pt_ubpms]
    for ei in pt_ubpms:
        assert cell_list[ei].Elem.PL == 0.0
    print('\nUser BPM Infor:')
    print('(Elem.Name)           (s)       (ds from Straight Center)')
    for name, s in zip(cap_ubpm_names, s_ubpms):
        print('{0:15} : {1:.9f}'.format(name, s))

    ds = s_ubpms - pt_sc
    print('ds [m]:')
    pprint.pprint(ds)

    cell_num = 7

    print_elems_around_straight(cell_num, n=5)

    # s-pos of center of straight
    sc = SR_CIRCUMF / 30 * cell_num # [m]
    print('\n# s-pos of straight center (aphla): {0:.9f}'.format(sc))
    np.testing.assert_almost_equal(sc, pt_sc, decimal=9)

    # Look at the output of print_elems_around_straight() above and
    # manually type these indexes in, though these are just for information purpose.
    #us_fcor_aphla_index = 66800
    #ds_fcor_aphla_index = 67500

    bpm_info = [
        ('pu1g1c{0:02d}a'.format(cell_num), sc + ds[0], 'PU1', 66800 + 100),
        ('pu2g1c{0:02d}a'.format(cell_num), sc + ds[1], 'PU2', 66800 + 300),
        ('pu3g1c{0:02d}a'.format(cell_num), sc + ds[2], 'PU3', 66800 + 400),
        ('pu4g1c{0:02d}a'.format(cell_num), sc + ds[3], 'PU4', 66800 + 600),
    ]
    us_id_index = 66800 + 200
    ds_id_index = 66800 + 500 # None

    # #### Adding elements for UBPMs to database ####
    for elemName, sEnd, ugg, idx in bpm_info:
        kw = dict(elemType   = 'UBPM_',
                  cell       = 'C{0:02d}'.format(cell_num),
                  girder     = 'G1',
                  symmetry   = 'A',
                  elemGroups = 'UBPM;'+ugg,
                  elemIndex  = idx,
                  elemLength = 0.0,
                  )
        ap.apdata.updateDbElement(DBFILE, 'SR', elemName, elemPosition=sEnd, **kw)

    ap.machines.load('nsls2', 'SR')

    pprint.pprint( ap.getGroupMembers(['UBPM', 'C{0:02d}'.format(cell_num)]) )
    pprint.pprint( ap.getElements('PU1') )
    pprint.pprint( ap.getElements('PU2') )
    pprint.pprint( ap.getElements('PU3') )
    pprint.pprint( ap.getElements('PU4') )

    elemName_prefix_devName_tups = [
        ('pu1g1c07a', 'SR:C07-BI{BPM:7}', 'C07-BPM7'),
        ('pu2g1c07a', 'SR:C07-BI{BPM:8}', 'C07-BPM8'),
        ('pu3g1c07a', 'SR:C07-BI{BPM:9}', 'C07-BPM9'),
        ('pu4g1c07a', 'SR:C07-BI{BPM:10}', 'C07-BPM10'),
    ]

    # #### Adding PVs for UBPM elements to database ####
    for elemName, prefix, devName in elemName_prefix_devName_tups:
        tags = ['aphla.sys.SR']
        # ^ required, otherwise can not be load by `machines.load("nsls2", "SR")`
        for pvpf, fld, hdl in BPM_PV_REC:
            if pvpf != 'Pos:XwUsrOff-Calc':
                ap.apdata.updateDbPv(
                    DBFILE, prefix + pvpf, elemName, fld, elemHandle=hdl, tags=tags,
                    quiet=True)
            else:
                ap.apdata.updateDbPv(
                    DBFILE, prefix + pvpf, elemName, fld, elemHandle=hdl, tags=tags,
                    quiet=True, devName=devName)

    ap.machines.load('nsls2', 'SR')

    ubpms = ap.getGroupMembers(['UBPM', 'C{0:02d}'.format(cell_num)])

    for k in ['x', 'y', 'x0', 'y0', 'xref1', 'yref1', 'xref2', 'yref2', 'ampl', 'xbba', 'ybba']:
        print('* (raw)', k)
        print(ap.fget(ubpms, k, unitsys=None))
        try:
            print('* (phy)', k)
            print(ap.fget(ubpms, k, unitsys='phy'))
        except:
            print('# physics conversion failed')

    # #### Adding an element for ID to database ####

    # Add EPU60 (upstream)
    elemLength = 1.6 # [m]
    elemName, sEnd = 'epu60g1c07u', s_us_id
    np.testing.assert_almost_equal(sEnd, sc - 1.250 + elemLength/2.0, decimal=9)
    kw = dict(elemType   = 'EPU',
              cell       = 'C{0:02d}'.format(cell_num),
              girder     = 'G1',
              symmetry   = 'U',
              elemGroups = 'EPU60;ID;Partner;SST',
              # ^ ";" was ":" when this function was run, which was retroactively
              # fixed in correct_SST_EPU60_group().
              elemIndex  = us_id_index,
              elemLength = elemLength,
              )
    ap.apdata.updateDbElement(DBFILE, 'SR', elemName, elemPosition=sEnd, **kw)

    # Add U42 (downstream)
    elemLength = 0.89 # [m]
    elemName, sEnd = 'ivu42g1c07d', s_ds_id
    np.testing.assert_almost_equal(sEnd, sc + 1.250 + elemLength/2.0, decimal=9)
    kw = dict(elemType   = 'IVU',
              cell       = 'C{0:02d}'.format(cell_num),
              girder     = 'G1',
              symmetry   = 'D',
              elemGroups = 'IVU42;ID;Partner;SST',
              # ^ ";" was ":" when this function was run, which was retroactively
              # fixed in correct_U42_elem_name_and_type().
              elemIndex  = ds_id_index,
              elemLength = elemLength,
              )
    ap.apdata.updateDbElement(DBFILE, 'SR', elemName, elemPosition=sEnd, **kw)

    print_elems_around_straight(cell_num, n=5)

#----------------------------------------------------------------------
def add_SST_ID_elems_PVs():
    """"""

    # #### Adding PVs for the ID element EPU60 to database ####
    tags = ["aphla.sys.SR"]
    cch_epsilon = 0.01 # [A]
    elemName = 'epu60g1c07u'
    idcor_pv_prefix = 'SR:C06-MG{PS:EPU60}'
    # a list of pv, field and handle
    rec = [("SR:C07-ID:G1A{SST1:1-Ax:Gap}-Mtr-SP" , "gap", "put"), # [um]
           ("SR:C07-ID:G1A{SST1:1-Ax:Gap}-Mtr.RBV", "gap", "get"), # [um]
           ("SR:C07-ID:G1A{SST1:1-Ax:Phase}Phs:Mode-SP", "mode", "put"),
           ("SR:C07-ID:G1A{SST1:1-Ax:Phase}Phs:Mode-RB" , "mode", "get"),
           ("SR:C07-ID:G1A{SST1:1-Ax:Phase}-Mtr-SP" , "phase", "put"), # [um]
           ("SR:C07-ID:G1A{SST1:1-Ax:Phase}-Mtr.RBV", "phase", "get"), # [um]
           #
           # Note that only Ch.1, Ch.2, Ch.5, and Ch.6 are physically connected,
           # even though the CSS page shows there are 6 channels. In the aphla
           # database, Ch.1, Ch.2, Ch.4, and Ch.5 will be designated as
           # "cch0", "cch1", "cch2", and "cch3", respectively.
           (idcor_pv_prefix+'U1-I-SP' , 'cch0', 'put'),
           (idcor_pv_prefix+'U1Loop-I', 'cch0', 'get'),
           (idcor_pv_prefix+'U1-I-I'  , 'cch0rb1', 'get'),
           (idcor_pv_prefix+'U2-I-SP' , 'cch1', 'put'),
           (idcor_pv_prefix+'U2Loop-I', 'cch1', 'get'),
           (idcor_pv_prefix+'U2-I-I'  , 'cch1rb1', 'get'),
           (idcor_pv_prefix+'U5-I-SP' , 'cch2', 'put'),
           (idcor_pv_prefix+'U5Loop-I', 'cch2', 'get'),
           (idcor_pv_prefix+'U5-I-I'  , 'cch2rb1', 'get'),
           (idcor_pv_prefix+'U6-I-SP' , 'cch3', 'put'),
           (idcor_pv_prefix+'U6Loop-I', 'cch3', 'get'),
           (idcor_pv_prefix+'U6-I-I'  , 'cch3rb1', 'get'),
           #
           (idcor_pv_prefix+'U1Loop-I', 'cch[0]', 'get'),
           (idcor_pv_prefix+'U2Loop-I', 'cch[1]', 'get'),
           (idcor_pv_prefix+'U5Loop-I', 'cch[2]', 'get'),
           (idcor_pv_prefix+'U6Loop-I', 'cch[3]', 'get'),
           ]
    for pvpf, fld, hdl in rec:
        if fld.startswith('cch'):
            _kws = dict(epsilon=cch_epsilon)
        else:
            _kws = dict()
        ap.apdata.updateDbPv(
            DBFILE, pvpf, elemName, fld, elemHandle=hdl, tags=tags,
            quiet=True, **_kws)


    # #### Adding PVs for the ID element U42 to database ####
    tags = ["aphla.sys.SR"]
    cch_epsilon = 0.01 # [A]
    elemName = 'ivu42g1c07d'
    idcor_pv_prefix = 'SR:C06-MG{PS:U42}'
    # a list of pv, field and handle
    rec = [("SR:C07-ID:G1A{SST2:1-Ax:Gap}-Mtr-SP" , "gap", "put"), # [um]
           ("SR:C07-ID:G1A{SST2:1-Ax:Gap}-Mtr.RBV", "gap", "get"), # [um]
           #
           # Note that only Ch.1, Ch.2, Ch.5, and Ch.6 are physically connected,
           # even though the CSS page shows there are 6 channels. In the aphla
           # database, Ch.1, Ch.2, Ch.4, and Ch.5 will be designated as
           # "cch0", "cch1", "cch2", and "cch3", respectively.
           (idcor_pv_prefix+'U1-I-SP' , 'cch0', 'put'),
           (idcor_pv_prefix+'U1Loop-I', 'cch0', 'get'),
           (idcor_pv_prefix+'U1-I-I'  , 'cch0rb1', 'get'),
           (idcor_pv_prefix+'U2-I-SP' , 'cch1', 'put'),
           (idcor_pv_prefix+'U2Loop-I', 'cch1', 'get'),
           (idcor_pv_prefix+'U2-I-I'  , 'cch1rb1', 'get'),
           (idcor_pv_prefix+'U5-I-SP' , 'cch2', 'put'),
           (idcor_pv_prefix+'U5Loop-I', 'cch2', 'get'),
           (idcor_pv_prefix+'U5-I-I'  , 'cch2rb1', 'get'),
           (idcor_pv_prefix+'U6-I-SP' , 'cch3', 'put'),
           (idcor_pv_prefix+'U6Loop-I', 'cch3', 'get'),
           (idcor_pv_prefix+'U6-I-I'  , 'cch3rb1', 'get'),
           #
           (idcor_pv_prefix+'U1Loop-I', 'cch[0]', 'get'),
           (idcor_pv_prefix+'U2Loop-I', 'cch[1]', 'get'),
           (idcor_pv_prefix+'U5Loop-I', 'cch[2]', 'get'),
           (idcor_pv_prefix+'U6Loop-I', 'cch[3]', 'get'),
           ]
    for pvpf, fld, hdl in rec:
        if fld.startswith('cch'):
            _kws = dict(epsilon=cch_epsilon)
        else:
            _kws = dict()
        ap.apdata.updateDbPv(
            DBFILE, pvpf, elemName, fld, elemHandle=hdl, tags=tags,
            quiet=True, **_kws)


    ap.machines.load('nsls2', 'SR')

    for idname in ['epu60g1c07u', 'ivu42g1c07d']:

        idobj = ap.getElements(idname)[0]
        print('## {0} ##'.format(idname))

        for fld in ['gap', 'phase']:
            if (fld == 'phase') and (idobj.family != 'EPU'):
                continue

            for hdl in ['setpoint', 'readback']:
                for unitsys in [None, 'phy']:
                    val = idobj.get(fld, handle=hdl, unitsys=unitsys)
                    unit_str = idobj.getUnit(fld, handle=hdl, unitsys=unitsys)

                    if unitsys is None:
                        print('{0}:{1}:{2} = {3:.6g} [{4}]'.format(
                            fld, hdl, unitsys if unitsys is not None else 'None',
                            val, unit_str,
                        ))

                    else:
                        uc = idobj.convertUnit(fld, 1.0, None, 'phy', handle=hdl)
                        print('{0}:{1}:{2} = {3:.6g} [{4}] [unitconv *= {5:.3e}]'.format(
                            fld, hdl, unitsys if unitsys is not None else 'None',
                            val, unit_str, uc,
                        ))

#----------------------------------------------------------------------
def print_all_ID_field_unitconv(output_filepath=''):
    """"""

    ap.machines.loadfast('nsls2', 'SR')

    text = []

    for idname in [e.name for e in ap.getElements('ID')]:

        idobj = ap.getElements(idname)[0]

        text.append('## {0} ##'.format(idname))

        for fld in sorted(idobj.fields()):

            for hdl in ['setpoint', 'readback']:

                for unitsys in [None, 'phy']:

                    unit_str = idobj.getUnit(fld, handle=hdl, unitsys=unitsys)

                    text.append('{0}:{1}:{2}:{3} [{4}]'.format(
                        idname, fld, hdl, unitsys if unitsys is not None else 'None',
                        unit_str))

                try:
                    uc = idobj.convertUnit(fld, 1.0, None, 'phy', handle=hdl)
                except RuntimeError:
                    uc = np.nan

                text.append('{0}:{1}:{2} unitconv *= {3:.3e}'.format(
                    idname, fld, hdl, uc))

    print('\n'.join(text))

    if output_filepath != '':
        with open(output_filepath, 'w') as f:
            f.write('\n'.join(text))

#----------------------------------------------------------------------
def print_all_ID_gap_values():
    """"""

    ap.machines.loadfast('nsls2', 'SR')

    text = []

    for idname in [e.name for e in ap.getElements('ID')]:

        idobj = ap.getElements(idname)[0]

        text.append('## {0} ##'.format(idname))

        for fld in ['gap']:

            for hdl in ['setpoint', 'readback']:

                for unitsys in [None, 'phy']:

                    unit_str = idobj.getUnit(fld, handle=hdl, unitsys=unitsys)
                    val = idobj.get(fld, handle=hdl, unitsys=unitsys)

                    text.append('{0}:{1}:{2}:{3} = {4:.4g} [{5}]'.format(
                        idname, fld, hdl, unitsys if unitsys is not None else 'None',
                        val, unit_str))


    print('\n'.join(text))

#----------------------------------------------------------------------
def print_all_ID_phase_values():
    """"""

    ap.machines.loadfast('nsls2', 'SR')

    text = []

    for idname in [e.name for e in ap.getElements('ID')]:

        idobj = ap.getElements(idname)[0]

        if 'phase' not in idobj.fields():
            continue

        text.append('## {0} ##'.format(idname))

        for fld in ['phase']:

            for hdl in ['setpoint', 'readback']:

                for unitsys in [None, 'phy']:

                    unit_str = idobj.getUnit(fld, handle=hdl, unitsys=unitsys)
                    val = idobj.get(fld, handle=hdl, unitsys=unitsys)

                    text.append('{0}:{1}:{2}:{3} = {4:.4g} [{5}]'.format(
                        idname, fld, hdl, unitsys if unitsys is not None else 'None',
                        val, unit_str))


    print('\n'.join(text))

#----------------------------------------------------------------------
def add_SST_U42_gap_unitconv():
    """
    """

    kw = dict(compression='gzip')

    _temp_unitconv_file = UNITCONV_FILE + '.tmp'

    fnew = h5py.File(_temp_unitconv_file, 'w')
    fold = h5py.File(UNITCONV_FILE, 'r')

    # First copy existing unit conversion data
    gold = fold['UnitConversion']
    gnew = fnew.create_group('UnitConversion')
    for k, v in gold.items():

        if False: # This will end up with bigger file size
            d = gnew.create_dataset(k, data=v.value, **kw)
        else: # This will end up with smaller file size, so use this one!
            gnew[k] = v.value
            d = gnew[k]

        for ak, av in v.attrs.items():
            put_h5py_attr(d, ak, av)

    # Adding new unit conversions
    #
    # ### Note that the new dataset name had to be named such that this new
    # dataset appears later than the existing "ID_IVU_gap_rb" dataset
    # in the newly created HDF5 file. Apparently, aphla will load the unit
    # conversion in the order of datasets, and hence the later ones will
    # overwrite if elements satisfy the given matching conditions. ##
    #
    for new_dataset_name, handle_list in [
        ('ID_gap_rb_um_to_mm', ['readback']),
        ('ID_gap_sp_um_to_mm', ['setpoint']),
        ]:
        d = gnew.create_dataset(new_dataset_name,
                                data=np.array([1e-3, 0.0]), **kw)
        uc = {'_class_': 'polynomial', 'dst_unit': 'mm', 'dst_unit_sys': 'phy',
              'elements': ['ivu42g1c07d',],
              'field': 'gap', 'handle': handle_list,
              'invertible': 1, 'src_unit': 'um', 'src_unit_sys': ''}
        for k, v in uc.items(): put_h5py_attr(d, k, v)


    fold.close()
    fnew.close()

    shutil.move(_temp_unitconv_file, UNITCONV_FILE)

#----------------------------------------------------------------------
def add_SST_cch_unitconv():
    """"""

    kw = dict(compression='gzip')

    _temp_unitconv_file = UNITCONV_FILE + '.tmp'

    fnew = h5py.File(_temp_unitconv_file, 'w')
    fold = h5py.File(UNITCONV_FILE, 'r')

    # First copy existing unit conversion data, except for the following
    # datasets that need modification:
    #    'ID_cch0_v2', 'ID_cch1_v2', 'ID_cch2_v2', 'ID_cch3_v2',
    #    'ID_cch0rb1_v2', 'ID_cch1rb1_v2', 'ID_cch2rb1_v2', 'ID_cch3rb1_v2',
    gold = fold['UnitConversion']
    gnew = fnew.create_group('UnitConversion')
    excl_ds_names = [
        'ID_cch0_v2', 'ID_cch1_v2', 'ID_cch2_v2', 'ID_cch3_v2',
        'ID_cch0rb1_v2', 'ID_cch1rb1_v2', 'ID_cch2rb1_v2', 'ID_cch3rb1_v2',
    ]
    _ds_copy, _attr_copy = {}, {}
    for k, v in gold.items():

        if k in excl_ds_names:
            _ds_copy[k] = v.value
            _attr_copy[k] = {}
            for ak, av in v.attrs.items():
                _attr_copy[k][ak] = av
            continue

        if False: # This will end up with bigger file size
            d = gnew.create_dataset(k, data=v.value, **kw)
        else: # This will end up with smaller file size, so use this one!
            gnew[k] = v.value
            d = gnew[k]

        for ak, av in v.attrs.items():
            put_h5py_attr(d, ak, av)

    # Modify existing unit conversions
    for k, v in _ds_copy.items():
        gnew[k] = v
        d = gnew[k]

        for ak, av in _attr_copy[k].items():
            if ak == 'elements':
                av = np.sort(av.tolist() + ['epu60g1c07u', 'ivu42g1c07d'])
            put_h5py_attr(d, ak, av)

    fold.close()
    fnew.close()

    shutil.move(_temp_unitconv_file, UNITCONV_FILE)

#----------------------------------------------------------------------
def correct_U42_elem_name_and_type():
    """
    Turned out that SST U42 is not an IVU, but OVU (out-of-vacuum undulator).
    So, the name is being corrected from ivu42g1c07d to ovu42g1c07d.

    Also correct the family from "IVU" to "OVU" and
    the gruop name "IVU42" into "OVU42".

    Also fixing "Partner:SST" to "Partner;SST" such that "Partner" and "SST"
    are separated in the group names.
    """

    sys.path.insert(0, '/home/yhidaka/git_repos/hlsqlite')
    import hlsqlite

    db = hlsqlite.SQLiteDatabase(filepath=DBFILE)

    # Replacing all "elemName" entries of "ivu42g1c07d" with "ovu42g1c07d"
    for table_name in db.getTableNames():
        print('### {0} ###'.format(table_name))

        if 'elemName' in db.getColumnNames(table_name):
            pprint.pprint(db.getColumnDataFromTable(
                table_name, column_name_list=['elemName'],
                condition_str='elemName="ivu42g1c07d"'))

            db.changeValues(table_name, 'elemName', '"ovu42g1c07d"',
                            condition_str='elemName="ivu42g1c07d"')

    # Check that all the elem names have been corrected.
    for table_name in db.getTableNames():
        print('### {0} ###'.format(table_name))

        if 'elemName' in db.getColumnNames(table_name):
            pprint.pprint(db.getColumnDataFromTable(
                table_name, column_name_list=['elemName'],
                condition_str='elemName="ovu42g1c07d"'))

    db.close()

    ap.machines.loadfast('nsls2', 'SR')

    # Update U42 properties
    idobj = ap.getElements('ovu42g1c07d')[0]
    elemName = idobj.name
    kw = dict(elemType   = 'OVU',
              cell       = idobj.cell,
              girder     = idobj.girder,
              symmetry   = idobj.symmetry,
              elemGroups = 'OVU42;ID;Partner;SST',
              elemIndex  = idobj.index,
              elemLength = idobj.length,
              )
    ap.apdata.updateDbElement(DBFILE, 'SR', elemName, elemPosition=idobj.se, **kw)

#----------------------------------------------------------------------
def correct_SST_EPU60_group():
    """"""

    # Update EPU60 properties
    idobj = ap.getElements('epu60g1c07u')[0]
    elemName = idobj.name
    kw = dict(elemType   = idobj.family,
              cell       = idobj.cell,
              girder     = idobj.girder,
              symmetry   = idobj.symmetry,
              elemGroups = 'EPU60;ID;Partner;SST',
              elemIndex  = idobj.index,
              elemLength = idobj.length,
              )
    ap.apdata.updateDbElement(DBFILE, 'SR', elemName, elemPosition=idobj.se, **kw)

#----------------------------------------------------------------------
def correct_U42_unitcnov_due_to_elem_name_change():
    """"""

    kw = dict(compression='gzip')

    _temp_unitconv_file = UNITCONV_FILE + '.tmp'

    fnew = h5py.File(_temp_unitconv_file, 'w')
    fold = h5py.File(UNITCONV_FILE, 'r')

    # First copy existing unit conversion data, except for the following
    # datasets that need modification:
    #    'ID_gap_rb_um_to_mm', 'ID_gap_sp_um_to_mm',
    #    'ID_cch0_v2', 'ID_cch1_v2', 'ID_cch2_v2', 'ID_cch3_v2',
    #    'ID_cch0rb1_v2', 'ID_cch1rb1_v2', 'ID_cch2rb1_v2', 'ID_cch3rb1_v2',
    gold = fold['UnitConversion']
    gnew = fnew.create_group('UnitConversion')
    excl_ds_names = [
        'ID_gap_rb_um_to_mm', 'ID_gap_sp_um_to_mm',
        'ID_cch0_v2', 'ID_cch1_v2', 'ID_cch2_v2', 'ID_cch3_v2',
        'ID_cch0rb1_v2', 'ID_cch1rb1_v2', 'ID_cch2rb1_v2', 'ID_cch3rb1_v2',
    ]
    _ds_copy, _attr_copy = {}, {}
    for k, v in gold.items():

        if k in excl_ds_names:
            _ds_copy[k] = v.value
            _attr_copy[k] = {}
            for ak, av in v.attrs.items():
                _attr_copy[k][ak] = av
            continue

        if False: # This will end up with bigger file size
            d = gnew.create_dataset(k, data=v.value, **kw)
        else: # This will end up with smaller file size, so use this one!
            gnew[k] = v.value
            d = gnew[k]

        for ak, av in v.attrs.items():
            put_h5py_attr(d, ak, av)

    # Modify existing unit conversions
    for k, v in _ds_copy.items():
        gnew[k] = v
        d = gnew[k]

        for ak, av in _attr_copy[k].items():
            if ak == 'elements':
                av = av.tolist()
                av.remove('ivu42g1c07d')
                av.append('ovu42g1c07d')
                av = np.sort(av)
            put_h5py_attr(d, ak, av)

    fold.close()
    fnew.close()

    shutil.move(_temp_unitconv_file, UNITCONV_FILE)

#----------------------------------------------------------------------
def fix_U42_EPU60_US_DS_error():
    """
    SST EPU60 was assumed to be upstream, and SST U42 was assumed to be
    downstream, previously. But it turned out this was opposite. This
    function corrects this error.

    Element names have been corrected, with their ending "u" and "d" swapped.
    ID types (EPU vs. OVU) and groups have been swapped.
    Correct PVs for gap, phase, and orbit corrector (cch) have been reassigned.
    """

    sys.path.insert(0, '/home/yhidaka/git_repos/hlsqlite')
    import hlsqlite

    db = hlsqlite.SQLiteDatabase(filepath=DBFILE)

    # Replacing all "elemName" entries of "epu60g1c07u" with "ovu42g1c07u"
    wrong_name = 'epu60g1c07u'
    correct_name = 'ovu42g1c07u'
    for table_name in db.getTableNames():
        print('### {0} ###'.format(table_name))

        if 'elemName' in db.getColumnNames(table_name):
            pprint.pprint(db.getColumnDataFromTable(
                table_name, column_name_list=['elemName'],
                condition_str='elemName="{0}"'.format(wrong_name)))

            db.changeValues(table_name, 'elemName', '"{0}"'.format(correct_name),
                            condition_str='elemName="{}"'.format(wrong_name))

    # Check that all the elem names have been corrected.
    for table_name in db.getTableNames():
        print('### {0} ###'.format(table_name))

        if 'elemName' in db.getColumnNames(table_name):
            pprint.pprint(db.getColumnDataFromTable(
                table_name, column_name_list=['elemName'],
                condition_str='elemName="{0}"'.format(correct_name)))

    db.close()

    ap.machines.loadfast('nsls2', 'SR')

    # Update U42 properties
    idobj = ap.getElements(correct_name)[0]
    elemName = idobj.name
    kw = dict(elemType   = 'OVU',
              cell       = idobj.cell,
              girder     = idobj.girder,
              symmetry   = idobj.symmetry,
              elemGroups = 'OVU42;ID;Partner;SST',
              elemIndex  = idobj.index,
              elemLength = idobj.length,
              )
    ap.apdata.updateDbElement(DBFILE, 'SR', elemName, elemPosition=idobj.se, **kw)


    db = hlsqlite.SQLiteDatabase(filepath=DBFILE)

    # Replacing all "elemName" entries of "ovu42g1c07d" with "epu60g1c07d"
    wrong_name = 'ovu42g1c07d'
    correct_name = 'epu60g1c07d'
    for table_name in db.getTableNames():
        print('### {0} ###'.format(table_name))

        if 'elemName' in db.getColumnNames(table_name):
            pprint.pprint(db.getColumnDataFromTable(
                table_name, column_name_list=['elemName'],
                condition_str='elemName="{0}"'.format(wrong_name)))

            db.changeValues(table_name, 'elemName', '"{0}"'.format(correct_name),
                            condition_str='elemName="{}"'.format(wrong_name))

    # Check that all the elem names have been corrected.
    for table_name in db.getTableNames():
        print('### {0} ###'.format(table_name))

        if 'elemName' in db.getColumnNames(table_name):
            pprint.pprint(db.getColumnDataFromTable(
                table_name, column_name_list=['elemName'],
                condition_str='elemName="{0}"'.format(correct_name)))

    db.close()

    ap.machines.loadfast('nsls2', 'SR')

    # Update EPU60 properties
    idobj = ap.getElements(correct_name)[0]
    elemName = idobj.name
    kw = dict(elemType   = 'EPU',
              cell       = idobj.cell,
              girder     = idobj.girder,
              symmetry   = idobj.symmetry,
              elemGroups = 'EPU60;ID;Partner;SST',
              elemIndex  = idobj.index,
              elemLength = idobj.length,
              )
    ap.apdata.updateDbElement(DBFILE, 'SR', elemName, elemPosition=idobj.se, **kw)


    # ################################################################
    # ## Now delete all associated PVs before attaching correct PVs ##
    # ################################################################

    db = hlsqlite.SQLiteDatabase(filepath=DBFILE)

    table_name = 'pvs'
    print('### {0} ###'.format(table_name))
    for elem_name in ['epu60g1c07u', 'epu60g1c07d',
                      'ovu42g1c07u', 'ovu42g1c07d']:
        print('*** Deleting PVs associated with Element "{0}" ***'.format(elem_name))

        print('# Before erasing #')
        pprint.pprint(db.getColumnDataFromTable(
            table_name, column_name_list=['elemName'],
            condition_str='elemName="{0}"'.format(elem_name)))

        db.deleteRows(table_name, condition_str='elemName="{0}"'.format(elem_name))

        # Check that all potentially conflicting PVs are erased from the database.
        print('# After erasing #')
        pprint.pprint(db.getColumnDataFromTable(
            table_name, column_name_list=['elemName'],
            condition_str='elemName="{0}"'.format(elem_name)))

    db.close()


    # ################################
    # ## Now fix the associated PVs ##
    # ################################

    ap.machines.loadfast('nsls2', 'SR')

    # #### Adding PVs for the ID element EPU60 to database ####
    tags = ["aphla.sys.SR"]
    cch_epsilon = 0.01 # [A]
    elemName = 'epu60g1c07d'
    idcor_pv_prefix = 'SR:C06-MG{PS:EPU60}'
    # a list of pv, field and handle
    rec = [("SR:C07-ID:G1A{SST1:1-Ax:Gap}-Mtr-SP" , "gap", "put"), # [um]
           ("SR:C07-ID:G1A{SST1:1-Ax:Gap}-Mtr.RBV", "gap", "get"), # [um]
           ("SR:C07-ID:G1A{SST1:1-Ax:Phase}Phs:Mode-SP", "mode", "put"),
           ("SR:C07-ID:G1A{SST1:1-Ax:Phase}Phs:Mode-RB" , "mode", "get"),
           ("SR:C07-ID:G1A{SST1:1-Ax:Phase}-Mtr-SP" , "phase", "put"), # [um]
           ("SR:C07-ID:G1A{SST1:1-Ax:Phase}-Mtr.RBV", "phase", "get"), # [um]
           #
           # Note that only Ch.1, Ch.2, Ch.5, and Ch.6 are physically connected,
           # even though the CSS page shows there are 6 channels. In the aphla
           # database, Ch.1, Ch.2, Ch.4, and Ch.5 will be designated as
           # "cch0", "cch1", "cch2", and "cch3", respectively.
           (idcor_pv_prefix+'U1-I-SP' , 'cch0', 'put'),
           (idcor_pv_prefix+'U1Loop-I', 'cch0', 'get'),
           (idcor_pv_prefix+'U1-I-I'  , 'cch0rb1', 'get'),
           (idcor_pv_prefix+'U2-I-SP' , 'cch1', 'put'),
           (idcor_pv_prefix+'U2Loop-I', 'cch1', 'get'),
           (idcor_pv_prefix+'U2-I-I'  , 'cch1rb1', 'get'),
           (idcor_pv_prefix+'U5-I-SP' , 'cch2', 'put'),
           (idcor_pv_prefix+'U5Loop-I', 'cch2', 'get'),
           (idcor_pv_prefix+'U5-I-I'  , 'cch2rb1', 'get'),
           (idcor_pv_prefix+'U6-I-SP' , 'cch3', 'put'),
           (idcor_pv_prefix+'U6Loop-I', 'cch3', 'get'),
           (idcor_pv_prefix+'U6-I-I'  , 'cch3rb1', 'get'),
           #
           (idcor_pv_prefix+'U1Loop-I', 'cch[0]', 'get'),
           (idcor_pv_prefix+'U2Loop-I', 'cch[1]', 'get'),
           (idcor_pv_prefix+'U5Loop-I', 'cch[2]', 'get'),
           (idcor_pv_prefix+'U6Loop-I', 'cch[3]', 'get'),
           ]
    for pvpf, fld, hdl in rec:
        if fld.startswith('cch'):
            _kws = dict(epsilon=cch_epsilon)
        else:
            _kws = dict()
        ap.apdata.updateDbPv(
            DBFILE, pvpf, elemName, fld, elemHandle=hdl, tags=tags,
            quiet=True, **_kws)


    # #### Adding PVs for the ID element U42 to database ####
    tags = ["aphla.sys.SR"]
    cch_epsilon = 0.01 # [A]
    elemName = 'ovu42g1c07u'
    idcor_pv_prefix = 'SR:C06-MG{PS:U42}'
    # a list of pv, field and handle
    rec = [("SR:C07-ID:G1A{SST2:1-Ax:Gap}-Mtr-SP" , "gap", "put"), # [um]
           ("SR:C07-ID:G1A{SST2:1-Ax:Gap}-Mtr.RBV", "gap", "get"), # [um]
           #
           # Note that only Ch.1, Ch.2, Ch.5, and Ch.6 are physically connected,
           # even though the CSS page shows there are 6 channels. In the aphla
           # database, Ch.1, Ch.2, Ch.4, and Ch.5 will be designated as
           # "cch0", "cch1", "cch2", and "cch3", respectively.
           (idcor_pv_prefix+'U1-I-SP' , 'cch0', 'put'),
           (idcor_pv_prefix+'U1Loop-I', 'cch0', 'get'),
           (idcor_pv_prefix+'U1-I-I'  , 'cch0rb1', 'get'),
           (idcor_pv_prefix+'U2-I-SP' , 'cch1', 'put'),
           (idcor_pv_prefix+'U2Loop-I', 'cch1', 'get'),
           (idcor_pv_prefix+'U2-I-I'  , 'cch1rb1', 'get'),
           (idcor_pv_prefix+'U5-I-SP' , 'cch2', 'put'),
           (idcor_pv_prefix+'U5Loop-I', 'cch2', 'get'),
           (idcor_pv_prefix+'U5-I-I'  , 'cch2rb1', 'get'),
           (idcor_pv_prefix+'U6-I-SP' , 'cch3', 'put'),
           (idcor_pv_prefix+'U6Loop-I', 'cch3', 'get'),
           (idcor_pv_prefix+'U6-I-I'  , 'cch3rb1', 'get'),
           #
           (idcor_pv_prefix+'U1Loop-I', 'cch[0]', 'get'),
           (idcor_pv_prefix+'U2Loop-I', 'cch[1]', 'get'),
           (idcor_pv_prefix+'U5Loop-I', 'cch[2]', 'get'),
           (idcor_pv_prefix+'U6Loop-I', 'cch[3]', 'get'),
           ]
    for pvpf, fld, hdl in rec:
        if fld.startswith('cch'):
            _kws = dict(epsilon=cch_epsilon)
        else:
            _kws = dict()
        ap.apdata.updateDbPv(
            DBFILE, pvpf, elemName, fld, elemHandle=hdl, tags=tags,
            quiet=True, **_kws)



    # #################################
    # ## Now fix the unit conversion ##
    # #################################

    kw = dict(compression='gzip')

    _temp_unitconv_file = UNITCONV_FILE + '.tmp'

    fnew = h5py.File(_temp_unitconv_file, 'w')
    fold = h5py.File(UNITCONV_FILE, 'r')

    # First copy existing unit conversion data, except for the following
    # datasets that need modification:
    #    'ID_gap_rb_um_to_mm', 'ID_gap_sp_um_to_mm',
    #    'ID_cch0_v2', 'ID_cch1_v2', 'ID_cch2_v2', 'ID_cch3_v2',
    #    'ID_cch0rb1_v2', 'ID_cch1rb1_v2', 'ID_cch2rb1_v2', 'ID_cch3rb1_v2',
    gold = fold['UnitConversion']
    gnew = fnew.create_group('UnitConversion')
    excl_ds_names = [
        'ID_gap_rb_um_to_mm', 'ID_gap_sp_um_to_mm',
        'ID_cch0_v2', 'ID_cch1_v2', 'ID_cch2_v2', 'ID_cch3_v2',
        'ID_cch0rb1_v2', 'ID_cch1rb1_v2', 'ID_cch2rb1_v2', 'ID_cch3rb1_v2',
    ]
    _ds_copy, _attr_copy = {}, {}
    for k, v in gold.items():

        if k in excl_ds_names:
            _ds_copy[k] = v.value
            _attr_copy[k] = {}
            for ak, av in v.attrs.items():
                _attr_copy[k][ak] = av
            continue

        if False: # This will end up with bigger file size
            d = gnew.create_dataset(k, data=v.value, **kw)
        else: # This will end up with smaller file size, so use this one!
            gnew[k] = v.value
            d = gnew[k]

        for ak, av in v.attrs.items():
            put_h5py_attr(d, ak, av)

    # Modify existing unit conversions
    for k, v in _ds_copy.items():
        gnew[k] = v
        d = gnew[k]

        for ak, av in _attr_copy[k].items():
            if ak == 'elements':
                av = av.tolist()
                if 'ovu42g1c07d' in av:
                    av.remove('ovu42g1c07d')
                    av.append('ovu42g1c07u')
                if 'epu60g1c07u' in av:
                    av.remove('epu60g1c07u')
                    av.append('epu60g1c07d')
                av = np.sort(av)
            put_h5py_attr(d, ak, av)

    fold.close()
    fnew.close()

    shutil.move(_temp_unitconv_file, UNITCONV_FILE)

    from subprocess import Popen, PIPE
    p = Popen('chmod 777 {0}'.format(UNITCONV_FILE), stdout=PIPE, stderr=PIPE,
              shell=True, encoding='utf-8')
    out, err = p.communicate()
    print(out)
    if err:
        print('ERROR:')
        print(err)

    # ###################################################
    # ## Now confirm the fix is correcltly implemented ##
    # ###################################################

    ap.machines.loadfast('nsls2', 'SR')

    for idname in ['ovu42g1c07u', 'epu60g1c07d',]:

        idobj = ap.getElements(idname)[0]
        print('## {0} ##'.format(idname))

        for fld in ['gap', 'phase']:
            if (fld == 'phase') and (idobj.family != 'EPU'):
                continue

            for hdl in ['setpoint', 'readback']:
                for unitsys in [None, 'phy']:
                    val = idobj.get(fld, handle=hdl, unitsys=unitsys)
                    unit_str = idobj.getUnit(fld, handle=hdl, unitsys=unitsys)

                    if unitsys is None:
                        print('{0}:{1}:{2} = {3:.6g} [{4}]'.format(
                            fld, hdl, unitsys if unitsys is not None else 'None',
                            val, unit_str,
                        ))

                    else:
                        uc = idobj.convertUnit(fld, 1.0, None, 'phy', handle=hdl)
                        print('{0}:{1}:{2} = {3:.6g} [{4}] [unitconv *= {5:.3e}]'.format(
                            fld, hdl, unitsys if unitsys is not None else 'None',
                            val, unit_str, uc,
                        ))

#----------------------------------------------------------------------
def add_fcor_mode_xjump_yjump_fields():
    """
    Adding "mode", "xjump", "yjump" fields to all the fast correctors
    """

    fcors = ap.getElements('FCOR')

    fcor_names = [e.name for e in fcors]
    pv_prefixes = [e.pv(field='x', handle='setpoint')[0].replace('I:Sp1-SP', '')
                   for e in fcors]

    tags = ['aphla.sys.SR']

    fld = 'mode'
    for hdl in ['get', 'put']:
        for elemName, prefix in zip(fcor_names, pv_prefixes):
            pv = prefix + 'PsOpMode'
            ap.apdata.updateDbPv(DBFILE, pv, elemName, fld,
                                 elemHandle=hdl, tags=tags, quiet=True)

    fld, hdl = 'xjump', 'put'
    for elemName, prefix in zip(fcor_names, pv_prefixes):
        pv = prefix + 'I:Jump1-SP'
        ap.apdata.updateDbPv(DBFILE, pv, elemName, fld,
                             elemHandle=hdl, tags=tags, quiet=True)
    #
    fld, hdl = 'xjump', 'get'
    for e in fcors:
        pv = e.pv(field='x', handle='readback')[0]
        ap.apdata.updateDbPv(DBFILE, pv, e.name, fld,
                             elemHandle=hdl, tags=tags, quiet=True)


    fld, hdl = 'yjump', 'put'
    for elemName, prefix in zip(fcor_names, pv_prefixes):
        pv = prefix + 'I:Jump2-SP'
        ap.apdata.updateDbPv(DBFILE, pv, elemName, fld,
                             elemHandle=hdl, tags=tags, quiet=True)
    #
    fld, hdl = 'yjump', 'get'
    for e in fcors:
        pv = e.pv(field='y', handle='readback')[0]
        ap.apdata.updateDbPv(DBFILE, pv, e.name, fld,
                             elemHandle=hdl, tags=tags, quiet=True)

#----------------------------------------------------------------------
def add_fcor_xjump_yjump_unitconv():
    """"""

    kw = dict(compression='gzip')

    _temp_unitconv_file = UNITCONV_FILE + '.tmp'

    fnew = h5py.File(_temp_unitconv_file, 'w')
    fold = h5py.File(UNITCONV_FILE, 'r')

    # First copy existing unit conversion data
    gold = fold['UnitConversion']
    gnew = fnew.create_group('UnitConversion')
    for k, v in gold.items():

        if False: # This will end up with bigger file size
            d = gnew.create_dataset(k, data=v.value, **kw)
        else: # This will end up with smaller file size, so use this one!
            gnew[k] = v.value
            d = gnew[k]

        for ak, av in v.attrs.items():
            put_h5py_attr(d, ak, av)

    # Adding new unit conversions
    #
    '''
    Email sent to Yuke on 11/28/2016 3:17 PM:

    From fitting, the estimated unit conversions are 14.6 urad/Amp horizontally
    and 13.4 urad/Amp vertically.

    -Yoshi

    From: Tian, Yuke
    Sent: Monday, November 28, 2016 3:02 PM
    To: Hidaka, Yoshiteru
    Subject: RE: FOFB response matrix

    Hi Yoshi,

    Good to know the matrix agree. I don't have a precise unit conversion sine
    I directly applied the Amp to mm. The rough conversion should be 1.25A for
    15urad for both planes. How much differences do you see for H and V planes?

    Thanks,

    -Yuke

    '''
    group_name = 'FCOR'
    d = gnew.create_dataset(group_name+'_xjump', data=np.array([15e-6/1.25*1e3, 0.0]), **kw)
    uc = {'_class_': 'polynomial', 'dst_unit': 'mrad', 'dst_unit_sys': 'phy',
          'groups': [group_name], 'field': 'xjump', 'handle': ['readback','setpoint'],
          'invertible': 1, 'src_unit': 'A', 'src_unit_sys': ''}
    for k, v in uc.items(): put_h5py_attr(d, k, v)
    #
    d = gnew.create_dataset(group_name+'_yjump', data=np.array([15e-6/1.25*1e3, 0.0]), **kw)
    uc = {'_class_': 'polynomial', 'dst_unit': 'mrad', 'dst_unit_sys': 'phy',
          'groups': [group_name], 'field': 'yjump', 'handle': ['readback','setpoint'],
          'invertible': 1, 'src_unit': 'A', 'src_unit_sys': ''}
    for k, v in uc.items(): put_h5py_attr(d, k, v)


    fold.close()
    fnew.close()

    shutil.move(_temp_unitconv_file, UNITCONV_FILE)

    from subprocess import Popen, PIPE
    p = Popen('chmod 777 {0}'.format(UNITCONV_FILE), stdout=PIPE, stderr=PIPE,
              shell=True, encoding='utf-8')
    out, err = p.communicate()
    print(out)
    if err:
        print('ERROR:')
        print(err)

#----------------------------------------------------------------------
def fix_fast_corrector_cell_strings():
    """"""

    fcors = ap.getElements('FCOR')

    correct_cell_str_list = [
        'C{0:02d}'.format(i)
        for i in [30] * 3 + sum([[j] * 3 for j in range(1, 29+1)], [])]

    assert len(fcors) == len(correct_cell_str_list)
    for e, s in zip(fcors, correct_cell_str_list):
        ap.apdata.updateDbElement(DBFILE, 'SR', e.name, cell=s)

    ap.machines.load('nsls2', 'SR')

#----------------------------------------------------------------------
def add_BBA_readback_PVs():
    """"""

    tags = ['aphla.sys.SR']

    fld, hdl = 'xbba', 'get'
    for e in ap.getElements('p[uhlm]*'):
        elemName = e.name
        pv = e.pv(field='xbba', handle='setpoint')[0].replace(
            'BbaXOff-SP', 'BBA:X-I')
        ap.apdata.updateDbPv(DBFILE, pv, elemName, fld,
                             elemHandle=hdl, tags=tags, quiet=True, epsilon=0.0)

    fld, hdl = 'ybba', 'get'
    for e in ap.getElements('p[uhlm]*'):
        elemName = e.name
        pv = e.pv(field='ybba', handle='setpoint')[0].replace(
            'BbaYOff-SP', 'BBA:Y-I')
        ap.apdata.updateDbPv(DBFILE, pv, elemName, fld,
                             elemHandle=hdl, tags=tags, quiet=True, epsilon=0.0)

#----------------------------------------------------------------------
def add_unitconv_BPM_fields_0_ref1_ref2_bba_fa_tbt():
    """"""

    if False: #True: # This section can only run once, as HDF5 file does not
                     # allow overwrite of existing datasets

        kw = dict(compression='gzip')

        _temp_unitconv_file = UNITCONV_FILE + '.tmp'

        fnew = h5py.File(_temp_unitconv_file, 'w')
        fold = h5py.File(UNITCONV_FILE, 'r')

        # First copy existing unit conversion data
        gold = fold['UnitConversion']
        gnew = fnew.create_group('UnitConversion')
        for k, v in gold.items():

            if False: # This will end up with bigger file size
                d = gnew.create_dataset(k, data=v.value, **kw)
            else: # This will end up with smaller file size, so use this one!
                gnew[k] = v.value
                d = gnew[k]

            for ak, av in v.attrs.items():
                put_h5py_attr(d, ak, av)

        # Adding new unit conversions

        ap.machines.loadfast('nsls2', 'SR')

        all_bpms = ap.getElements('p[uhlm]*')

        # Add unit conversion for the scalar fields (src [mm], dst [mm])
        for hdl_list, fld_list in [
            (['readback',], ['x0', 'y0']),
            (['setpoint',], ['xref1', 'yref1', 'xref2', 'yref2']),
            (['readback','setpoint'], ['xbba', 'ybba']),
            ]:
            for fld in fld_list:
                d = gnew.create_dataset('BPM_'+fld, data=np.array([1.0, 0.0]), **kw)
                uc = {'_class_': 'polynomial', 'dst_unit': 'mm', 'dst_unit_sys': 'phy',
                      'groups': ['BPM', 'UBPM'], 'field': fld,
                      'handle': hdl_list,
                      'invertible': 1, 'src_unit': 'mm', 'src_unit_sys': ''}
                for k, v in uc.items(): put_h5py_attr(d, k, v)

        # Add unit conversion for the waveform fields (src [nm], dst [mm])
        for fld in ['xtbt', 'ytbt', 'xfa', 'yfa']:
            d = gnew.create_dataset('BPM_'+fld, data=np.array([1e-9 * 1e3, 0.0]), **kw)
            uc = {'_class_': 'polynomial', 'dst_unit': 'mm', 'dst_unit_sys': 'phy',
                  'groups': ['BPM', 'UBPM'], 'field': fld,
                  'handle': ['readback'],
                  'invertible': 1, 'src_unit': 'nm', 'src_unit_sys': ''}
            for k, v in uc.items(): put_h5py_attr(d, k, v)

        fold.close()
        fnew.close()

        # Make sure the new file has the correct permission
        os.chmod(_temp_unitconv_file, 0o755)

        shutil.move(_temp_unitconv_file, UNITCONV_FILE)

    #
    # Test if the unit conversion works
    #

    ap.machines.loadfast('nsls2', 'SR')

    from cothread.catools import caget

    all_bpms = ap.getElements('p[uhlm]*')

    print('\n# Checking scalar fields...')
    for e in all_bpms:
        print('## {0}'.format(e.name))

        for hdl_list, fld_list in [
            (['readback',], ['x0', 'y0']),
            (['setpoint',], ['xref1', 'yref1', 'xref2', 'yref2']),
            (['readback','setpoint'], ['xbba', 'ybba']),
            ]:
            for fld in fld_list:
                for hdl in hdl_list:
                    print('{0}/{1}: {2}, {3}'.format(
                        fld, hdl, e.getUnit(fld, handle=hdl, unitsys=None),
                        e.getUnit(fld, handle=hdl, unitsys='phy')))

                    raw_val = e.get(fld, handle=hdl, unitsys=None)
                    np.testing.assert_almost_equal(
                        raw_val,
                        e.convertUnit(fld, raw_val, None, 'phy', handle=hdl),
                        decimal=12
                    )

    print('\n# Checking waveform fields...')
    for e in all_bpms:
        print('## {0}'.format(e.name))

        hdl = 'readback'
        for fld in ['xtbt', 'ytbt', 'xfa', 'yfa']:
            print('{0}/{1}: {2}, {3}'.format(
                fld, hdl, e.getUnit(fld, handle=hdl, unitsys=None),
                e.getUnit(fld, handle=hdl, unitsys='phy')))

            raw_val = e.get(fld, handle=hdl, unitsys=None)
            np.testing.assert_almost_equal(
                raw_val * 1e-9 * 1e3,
                e.convertUnit(fld, raw_val, None, 'phy', handle=hdl),
                decimal=12
            )


    plt.show()

#----------------------------------------------------------------------
def switch_C04_C05_ID_orbcor_PVs_to_new_BNL_PSI_PVs():
    """"""

    tags = ['aphla.sys.SR']


    for elemName, pv_prefix in [('ivu23g1c04u', 'SR:C03-MG{PS:IVU_ID4}'),
                                ('ivu21g1c05d', 'SR:C04-MG{PS:IVU_ID5}')]:
        for iCh in range(6):

            # For setpoint fields: "cch0", "cch1", "cch2", ...
            fld, hdl = 'cch{0:d}'.format(iCh), 'put'
            pv = pv_prefix + ('U%d-I-SP' % (iCh + 1))
            ap.apdata.updateDbPv(DBFILE, pv, elemName, fld,
                                 elemHandle=hdl, tags=tags, quiet=True, epsilon=0.05)

            # For readback fields: "cch0", "cch1", "cch2", ...
            fld, hdl = 'cch{0:d}'.format(iCh), 'get'
            pv = pv_prefix + ('U%dLoop-I' % (iCh + 1))
            ap.apdata.updateDbPv(DBFILE, pv, elemName, fld,
                                 elemHandle=hdl, tags=tags, quiet=True, epsilon=0.0)

            # For actual readback fields: "cch0rb1", "cch1rb1", "cch2rb1", ...
            fld, hdl = 'cch{0:d}rb1'.format(iCh), 'get'
            pv = pv_prefix + ('U%d-I-I' % (iCh + 1))
            ap.apdata.updateDbPv(DBFILE, pv, elemName, fld,
                                 elemHandle=hdl, tags=tags, quiet=True, epsilon=0.0)

            # For the "cch" readback array PV
            fld, hdl = 'cch[{0:d}]'.format(iCh), 'get'
            pv = pv_prefix + ('U%dLoop-I' % (iCh + 1))
            ap.apdata.updateDbPv(DBFILE, pv, elemName, fld,
                                 elemHandle=hdl, tags=tags, quiet=True, epsilon=0.0)

            # For setpoint fields for Orbit Feedforward output:
            #     "orbff0_output", "orbff1_output", "orbff2_output", ...
            fld, hdl = 'orbff{0:d}_output'.format(iCh), 'put'
            pv = pv_prefix + ('U%d-I-SP' % (iCh + 1))
            ap.apdata.updateDbPv(DBFILE, pv, elemName, fld,
                                 elemHandle=hdl, tags=tags, quiet=True, epsilon=0.05)

#----------------------------------------------------------------------
def purge_old_ID_orb_cor_PVs_for_C04_and_C05_IDs():
    """"""

    sys.path.insert(0, '/home/yhidaka/git_repos/hlsqlite')
    import hlsqlite

    db = hlsqlite.SQLiteDatabase(filepath=DBFILE)



    lines = []
    for e in ap.getElements('*'):
        for fld in sorted(e.fields()):
            lines += ['{0}; {1}; setpoint; '.format(e.name, fld) + s
                      for s in e.pv(field=fld, handle='setpoint')]
            lines += ['{0}; {1}; readback; '.format(e.name, fld) + s
                      for s in e.pv(field=fld, handle='readback')]

        lines += sorted(e.pv()) # This includes unlinked (leftover) PVs as well.

    with open('before.txt', 'w') as f:
        f.write('\n'.join(lines))


    if False:
        table_name = 'pvs'
        column_name_list = ['elemName', 'elemField']
        pprint.pprint(
            db.getColumnDataFromTable(
                table_name, column_name_list=column_name_list,
                condition_str='elemName="ivu23g1c04u"'))

        db.getColumnNames('pvs')

        table_name = 'pvs'
        column_name_list = ['id', 'elemField', 'pv']
        out = db.getColumnDataFromTable(
                table_name, column_name_list=column_name_list,
                condition_str='(elemName="ivu23g1c04u") AND (pv="SR:C04-ID:G1{IVU:1-MPS}ch3:readback")')
        pprint.pprint(list(zip(*out)))


        table_name = 'pvs'
        column_name_list = ['id', 'elemField', 'pv']
        out = db.getColumnDataFromTable(
                table_name, column_name_list=column_name_list,
                condition_str='(elemName="ivu23g1c04u") AND (pv LIKE "%:readback")')
        pprint.pprint(list(zip(*out)))

        table_name = 'pvs'
        column_name_list = ['id', 'elemField', 'pv']
        out = db.getColumnDataFromTable(
                table_name, column_name_list=column_name_list,
                condition_str='(elemName="ivu23g1c04u") AND (pv LIKE "%:setpoint")')
        pprint.pprint(list(zip(*out)))

        table_name = 'pvs'
        column_name_list = ['id', 'elemField', 'pv']
        out = db.getColumnDataFromTable(
                table_name, column_name_list=column_name_list,
                condition_str='(elemName="ivu23g1c04u") AND (pv LIKE "%:current")')
        pprint.pprint(list(zip(*out)))


    # Delete the old PVs for ID-04 that are no longer linked to any of the
    # element-field pairs
    table_name = 'pvs'
    db.deleteRows(table_name, condition_str='(elemName="ivu23g1c04u") AND (pv LIKE "%:setpoint")')
    db.deleteRows(table_name, condition_str='(elemName="ivu23g1c04u") AND (pv LIKE "%:readback")')
    db.deleteRows(table_name, condition_str='(elemName="ivu23g1c04u") AND (pv LIKE "%:current")')

    # Delete the old PVs for ID-05 that are no longer linked to any of the
    # element-field pairs
    table_name = 'pvs'
    db.deleteRows(table_name, condition_str='(elemName="ivu21g1c05d") AND (pv LIKE "%:setpoint")')
    db.deleteRows(table_name, condition_str='(elemName="ivu21g1c05d") AND (pv LIKE "%:readback")')
    db.deleteRows(table_name, condition_str='(elemName="ivu21g1c05d") AND (pv LIKE "%:current")')

    db.close()

    ap.machines.load('nsls2', 'SR')

    lines = []
    for e in ap.getElements('*'):
        for fld in sorted(e.fields()):
            lines += ['{0}; {1}; setpoint; '.format(e.name, fld) + s
                      for s in e.pv(field=fld, handle='setpoint')]
            lines += ['{0}; {1}; readback; '.format(e.name, fld) + s
                      for s in e.pv(field=fld, handle='readback')]

        lines += sorted(e.pv()) # This includes unlinked (leftover) PVs as well.

    with open('after.txt', 'w') as f:
        f.write('\n'.join(lines))

    # Manually check "before.txt" and "after.txt" such that the intended
    # PVs have been removed from the database, but nothing else has been changed.

#----------------------------------------------------------------------
def switch_C04_C05_ID_orbcor_PV_unitconv():
    """"""

    if False: #True: # This section can only run once, as HDF5 file does not
                     # allow overwrite of existing datasets

        kw = dict(compression='gzip')

        _temp_unitconv_file = UNITCONV_FILE + '.tmp'

        fnew = h5py.File(_temp_unitconv_file, 'w')
        fold = h5py.File(UNITCONV_FILE, 'r')

        excl_ds_names = \
            ['ID_cch{0:d}_v1'.format(iCh) for iCh in range(6)] + \
            ['ID_cch{0:d}_v2'.format(iCh) for iCh in range(6)] + \
            ['ID_cch{0:d}rb1_v1'.format(iCh) for iCh in range(6)] + \
            ['ID_cch{0:d}rb1_v2'.format(iCh) for iCh in range(6)] + \
            ['ivu_orbff{0:d}_m0_I_type0'.format(iCh) for iCh in range(6)] + \
            ['ivu_orbff{0:d}_m0_I_type2'.format(iCh) for iCh in range(6)]

        # First copy existing unit conversion data
        gold = fold['UnitConversion']
        gnew = fnew.create_group('UnitConversion')
        for k, v in gold.items():

            if False: # This will end up with bigger file size
                d = gnew.create_dataset(k, data=v.value, **kw)
            else: # This will end up with smaller file size, so use this one!
                gnew[k] = v.value
                d = gnew[k]

            if k in excl_ds_names:
                continue
            else:
                for ak, av in v.attrs.items():
                    put_h5py_attr(d, ak, av)

        # Updating to new unit conversions
        for iCh in range(6):

            k = 'ID_cch{0:d}_v1'.format(iCh)
            #
            v = gold[k]
            d = gnew[k]
            #
            for ak, av in v.attrs.items():
                if ak == 'elements':
                    elem_names = av.tolist()
                    elem_names.remove('ivu23g1c04u')
                    elem_names.remove('ivu21g1c05d')
                    av = np.array(elem_names)
                put_h5py_attr(d, ak, av)


            k = 'ID_cch{0:d}_v2'.format(iCh)
            #
            v = gold[k]
            d = gnew[k]
            #
            for ak, av in v.attrs.items():
                if ak == 'elements':
                    elem_names = av.tolist()
                    elem_names += ['ivu23g1c04u', 'ivu21g1c05d']
                    av = np.array(elem_names)
                put_h5py_attr(d, ak, av)



            k = 'ID_cch{0:d}rb1_v1'.format(iCh)
            #
            v = gold[k]
            d = gnew[k]
            #
            for ak, av in v.attrs.items():
                if ak == 'elements':
                    elem_names = av.tolist()
                    elem_names.remove('ivu23g1c04u')
                    elem_names.remove('ivu21g1c05d')
                    av = np.array(elem_names)
                put_h5py_attr(d, ak, av)


            k = 'ID_cch{0:d}rb1_v2'.format(iCh)
            #
            v = gold[k]
            d = gnew[k]
            #
            for ak, av in v.attrs.items():
                if ak == 'elements':
                    elem_names = av.tolist()
                    elem_names += ['ivu23g1c04u', 'ivu21g1c05d']
                    av = np.array(elem_names)
                put_h5py_attr(d, ak, av)



            k = 'ivu_orbff{0:d}_m0_I_type0'.format(iCh)
            #
            v = gold[k]
            d = gnew[k]
            #
            for ak, av in v.attrs.items():
                if ak == 'elements':
                    elem_names = av.tolist()
                    elem_names.remove('ivu23g1c04u')
                    elem_names.remove('ivu21g1c05d')
                    av = np.array(elem_names)
                put_h5py_attr(d, ak, av)


            k = 'ivu_orbff{0:d}_m0_I_type2'.format(iCh)
            #
            if k != 'ivu_orbff5_m0_I_type2':
                v = gold[k]
                d = gnew[k]
                #
                for ak, av in v.attrs.items():
                    if ak == 'elements':
                        elem_names = av.tolist()
                        elem_names += ['ivu23g1c04u', 'ivu21g1c05d']
                        av = np.array(elem_names)
                    put_h5py_attr(d, ak, av)
            else:
                d = gnew.create_dataset(k, data=np.array([1.0, 0.0]), **kw)
                uc = {'_class_': 'polynomial', 'dst_unit': 'A', 'dst_unit_sys': 'phy',
                      'elements': ['ivu23g1c04u', 'ivu21g1c05d'],
                      'field': 'orbff5_m0_I', 'handle': ['setpoint',],
                      'invertible': 1, 'src_unit': 'A', 'src_unit_sys': ''}
                for uc_k, uc_v in uc.items(): put_h5py_attr(d, uc_k, uc_v)


        fold.close()
        fnew.close()

        # Make sure the new file has the correct permission
        os.chmod(_temp_unitconv_file, 0o755)

        shutil.move(_temp_unitconv_file, UNITCONV_FILE)

    #
    # Test if the unit conversion works
    #

    ap.machines.loadfast('nsls2', 'SR')

    for e in ap.getElements('ivu*c0[45]*'):
        print('## {0} ##'.format(e.name))
        for hdl_list, fld_list in [
            (['readback', 'setpoint'], ['cch{0:d}'.format(iCh) for iCh in range(6)]),
            (['readback',], ['cch{0:d}rb1'.format(iCh) for iCh in range(6)]),
            (['setpoint',], ['orbff{0:d}_m0_I'.format(iCh) for iCh in range(6)]),
            ]:

            for fld in fld_list:
                for hdl in hdl_list:
                    print('{0}/{1}: {2}, {3}'.format(
                        fld, hdl, e.getUnit(fld, handle=hdl, unitsys=None),
                        e.getUnit(fld, handle=hdl, unitsys='phy')))

                    raw_val = 1.0
                    np.testing.assert_almost_equal(
                        raw_val,
                        e.convertUnit(fld, raw_val, None, 'phy', handle=hdl),
                        decimal=12
                    )

    plt.show()

#----------------------------------------------------------------------
def remove_cch_on_fields_from_C04_and_C05_IDs():
    """"""

    sys.path.insert(0, '/home/yhidaka/git_repos/hlsqlite')
    import hlsqlite

    db = hlsqlite.SQLiteDatabase(filepath=DBFILE)



    lines = []
    for e in ap.getElements('*'):
        for fld in sorted(e.fields()):
            lines += ['{0}; {1}; setpoint; '.format(e.name, fld) + s
                      for s in e.pv(field=fld, handle='setpoint')]
            lines += ['{0}; {1}; readback; '.format(e.name, fld) + s
                      for s in e.pv(field=fld, handle='readback')]

        lines += sorted(e.pv()) # This includes unlinked (leftover) PVs as well.

    with open('before.txt', 'w') as f:
        f.write('\n'.join(lines))


    if False:
        table_name = 'pvs'
        column_name_list = ['elemName', 'elemField']
        pprint.pprint(
            db.getColumnDataFromTable(
                table_name, column_name_list=column_name_list,
                condition_str='elemName="ivu23g1c04u"'))

        table_name = 'pvs'
        column_name_list = ['id', 'elemField', 'pv']
        out = db.getColumnDataFromTable(
                table_name, column_name_list=column_name_list,
                condition_str='(elemName="ivu23g1c04u") AND (elemField LIKE "cch%_on")')
        pprint.pprint(list(zip(*out)))

        table_name = 'pvs'
        column_name_list = ['id', 'elemField', 'pv']
        out = db.getColumnDataFromTable(
                table_name, column_name_list=column_name_list,
                condition_str='(elemName="ivu21g1c05d") AND (elemField LIKE "cch%_on")')
        pprint.pprint(list(zip(*out)))

    # Delete the ID-04 PVs for the fields "cch[0-5]_on"
    table_name = 'pvs'
    db.deleteRows(table_name, condition_str='(elemName="ivu23g1c04u") AND (elemField LIKE "cch%_on")')

    # Delete the ID-05 PVs for the fields "cch[0-5]_on"
    table_name = 'pvs'
    db.deleteRows(table_name, condition_str='(elemName="ivu21g1c05d") AND (elemField LIKE "cch%_on")')

    db.close()

    ap.machines.load('nsls2', 'SR')

    lines = []
    for e in ap.getElements('*'):
        for fld in sorted(e.fields()):
            lines += ['{0}; {1}; setpoint; '.format(e.name, fld) + s
                      for s in e.pv(field=fld, handle='setpoint')]
            lines += ['{0}; {1}; readback; '.format(e.name, fld) + s
                      for s in e.pv(field=fld, handle='readback')]

        lines += sorted(e.pv()) # This includes unlinked (leftover) PVs as well.

    with open('after.txt', 'w') as f:
        f.write('\n'.join(lines))

    # Manually check "before.txt" and "after.txt" such that the intended
    # PVs have been removed from the database, but nothing else has been changed.

#----------------------------------------------------------------------
def add_xray_bpms_C03_C16_C17ud():
    """"""

    # **** C03, C16, C17-1 & C17-2 IDs ****
    idobj_list = ap.getElements('ivu*c03*') + ap.getElements('ivu*c16*') \
        + ap.getElements('ivu*c17*')

    # s-pos of an X-BPM will be assumed to be at the center of the associated ID
    sc_list = [(idobj.sb + idobj.se)/2 for idobj in idobj_list]

    bpm_info = [
        # (idobj)       (Elem.Name), (sEnd),    (GroupName), (Elem.Index)
        (idobj_list[0], 'px1g1c03a', sc_list[0],    'PX1',  (28300 + 28600)/2),
        (idobj_list[1], 'px1g1c16a', sc_list[1],    'PX1',  (154950 + 155050)/2),
        (idobj_list[2], 'px1g1c17a', sc_list[2],    'PX1',  (163920 + 164020)/2),
        (idobj_list[3], 'px2g1c17a', sc_list[3],    'PX2',  (164120 + 164320)/2),
        # ^ (Elem.Index) is picked to be the center value of the ID element
        #   index and the index of the element just downstream of the ID element.
    ]

    # #### Adding elements for X-BPMs to database ####
    for idobj, elemName, sEnd, ugg, idx in bpm_info:
        kw = dict(elemType   = 'XBPM_',
                  cell       = idobj.cell,
                  girder     = 'G1',
                  symmetry   = 'A',
                  elemGroups = 'XBPM;'+ugg,
                  elemIndex  = idx,
                  elemLength = 0.0,
                  )
        ap.apdata.updateDbElement(DBFILE, 'SR', elemName, elemPosition=sEnd, **kw)

    ap.machines.load('nsls2', 'SR')

    for idobj in idobj_list:
        pprint.pprint( ap.getGroupMembers(['XBPM', idobj.cell]) )
    pprint.pprint( ap.getElements('PX1') )
    pprint.pprint( ap.getElements('PX2') )


    # #### Adding PVs for XBPM elements to database ####
    elemName_prefix_devName_tups = [
        ('px1g1c03a', 'SR:C03-BI{XBPM:1}', 'C03-XBPM1'),
        ('px1g1c16a', 'SR:C16-BI{XBPM:1}', 'C16-XBPM1'),
        ('px1g1c17a', 'SR:C17-BI{XBPM:1}', 'C17-XBPM1'),
        ('px2g1c17a', 'SR:C17-BI{XBPM:2}', 'C17-XBPM2'),
    ]

    for elemName, prefix, devName in elemName_prefix_devName_tups:
        tags = ['aphla.sys.SR']
        # ^ required, otherwise can not be load by `machines.load("nsls2", "SR")`
        for pvpf, fld, hdl in BPM_PV_REC:
            if fld in ('x0', 'y0'): # Only PVs for "x0" & "y0" exist as of 11/08/2018
                ap.apdata.updateDbPv(
                    DBFILE, prefix + pvpf, elemName, fld, elemHandle=hdl, tags=tags,
                    quiet=True, devName=devName)

    ap.machines.load('nsls2', 'SR')

    for idobj in idobj_list:

        pprint.pprint('*** {0} ***'.format(idobj.name))

        xbpms = ap.getGroupMembers(['XBPM', idobj.cell])

        for k in ['x0', 'y0',]:
            print('* (raw)', k)
            print(ap.fget(xbpms, k, unitsys=None))
            try:
                print('* (phy)', k)
                print(ap.fget(xbpms, k, unitsys='phy'))
            except:
                print('# physics conversion failed')

#----------------------------------------------------------------------
def add_xray_bpms_C03_C16_C17ud_unitconv():
    """"""

    kw = dict(compression='gzip')

    _temp_unitconv_file = UNITCONV_FILE + '.tmp'

    fnew = h5py.File(_temp_unitconv_file, 'w')
    fold = h5py.File(UNITCONV_FILE, 'r')

    # First copy existing unit conversion data
    gold = fold['UnitConversion']
    gnew = fnew.create_group('UnitConversion')
    for k, v in gold.items():

        if False: # This will end up with bigger file size
            d = gnew.create_dataset(k, data=v.value, **kw)
        else: # This will end up with smaller file size, so use this one!
            gnew[k] = v.value
            d = gnew[k]

        for ak, av in v.attrs.items():
            put_h5py_attr(d, ak, av)

    # Adding new unit conversions
    #
    group_name = 'XBPM'
    #
    for fld in ['x0', 'y0']:
        d = gnew.create_dataset(group_name+'_'+fld, data=np.array([1e-3, 0.0]), **kw)
        uc = {'_class_': 'polynomial', 'dst_unit': 'mm', 'dst_unit_sys': 'phy',
              'groups': [group_name], 'field': fld, 'handle': ['readback'],
              'invertible': 1, 'src_unit': 'um', 'src_unit_sys': ''}
        for k, v in uc.items(): put_h5py_attr(d, k, v)

    fold.close()
    fnew.close()

    shutil.move(_temp_unitconv_file, UNITCONV_FILE)
    # The generated file initially may not be 777 (in terms of permission).
    # After you wait a while, it may automatically change to 777, which did
    # happen when this functionw as run on 11/08/2018.
    # If not, you need to do manually "$ chmod 777 sr_unitconv.hdf5" on terminal

#----------------------------------------------------------------------
def add_xray_bpms_C03_C16_C17ud_fld_x_y():
    """
    Even though there are no PVs for X-ray BPMs corresponding to "x" and "y"
    fields of the RF BPMs, for convenience (ORM measurements, etc.), the only
    existing PV fields of "x0" and "y0" will be duplicated to be "x" and "y"
    as well.
    """

    # **** C03, C16, C17-1 & C17-2 IDs ****
    idobj_list = ap.getElements('ivu*c03*') + ap.getElements('ivu*c16*') \
        + ap.getElements('ivu*c17*')

    # #### Adding PVs for XBPM elements to database ####
    elemName_prefix_devName_tups = [
        ('px1g1c03a', 'SR:C03-BI{XBPM:1}', 'C03-XBPM1'),
        ('px1g1c16a', 'SR:C16-BI{XBPM:1}', 'C16-XBPM1'),
        ('px1g1c17a', 'SR:C17-BI{XBPM:1}', 'C17-XBPM1'),
        ('px2g1c17a', 'SR:C17-BI{XBPM:2}', 'C17-XBPM2'),
    ]

    for elemName, prefix, devName in elemName_prefix_devName_tups:
        tags = ['aphla.sys.SR']
        # ^ required, otherwise can not be load by `machines.load("nsls2", "SR")`
        for pvpf, fld, hdl in BPM_PV_REC:
            if fld in ('x0', 'y0'): # Only PVs for "x0" & "y0" exist as of 11/08/2018
                duplicate_fld = fld[0]
                ap.apdata.updateDbPv(
                    DBFILE, prefix + pvpf, elemName, duplicate_fld, elemHandle=hdl, tags=tags,
                    quiet=True) #, devName=devName)

    ap.machines.load('nsls2', 'SR')

    for idobj in idobj_list:

        pprint.pprint('*** {0} ***'.format(idobj.name))

        xbpms = ap.getGroupMembers(['XBPM', idobj.cell])

        for k in ['x0', 'y0', 'x', 'y']:
            print('* (raw)', k)
            print(ap.fget(xbpms, k, unitsys=None))
            try:
                print('* (phy)', k)
                print(ap.fget(xbpms, k, unitsys='phy'))
            except:
                print('# physics conversion failed')

#----------------------------------------------------------------------
def add_xray_bpms_C03_C16_C17ud_fld_x_y_unitconv():
    """"""

    kw = dict(compression='gzip')

    _temp_unitconv_file = UNITCONV_FILE + '.tmp'

    fnew = h5py.File(_temp_unitconv_file, 'w')
    fold = h5py.File(UNITCONV_FILE, 'r')

    # First copy existing unit conversion data
    gold = fold['UnitConversion']
    gnew = fnew.create_group('UnitConversion')
    for k, v in gold.items():

        if False: # This will end up with bigger file size
            d = gnew.create_dataset(k, data=v.value, **kw)
        else: # This will end up with smaller file size, so use this one!
            gnew[k] = v.value
            d = gnew[k]

        for ak, av in v.attrs.items():
            put_h5py_attr(d, ak, av)

    # Adding new unit conversions
    #
    group_name = 'XBPM'
    #
    for fld in ['x', 'y']:
        d = gnew.create_dataset(group_name+'_'+fld, data=np.array([1e-3, 0.0]), **kw)
        uc = {'_class_': 'polynomial', 'dst_unit': 'mm', 'dst_unit_sys': 'phy',
              'groups': [group_name], 'field': fld, 'handle': ['readback'],
              'invertible': 1, 'src_unit': 'um', 'src_unit_sys': ''}
        for k, v in uc.items(): put_h5py_attr(d, k, v)

    fold.close()
    fnew.close()

    shutil.move(_temp_unitconv_file, UNITCONV_FILE)
    # The generated file initially may not be 777 (in terms of permission).
    # After you wait a while, it may automatically change to 777, which did
    # happen when this functionw as run on 11/08/2018.
    # If not, you need to do manually "$ chmod 777 sr_unitconv.hdf5" on terminal

#----------------------------------------------------------------------
def switch_C03_10_16_17s_ID_orbcor_PVs_to_new_BNL_PSI_PVs():
    """"""

    tags = ['aphla.sys.SR']

    for elemName, new_pv_prefix, ch_inds in [
        ('ivu20g1c03c', 'SR:C02-MG{PS:IVU_ID3}', range(6)),
        ('ivu22g1c10c', 'SR:C09-MG{PS:IVU_ID10}', range(4)),
        ('ivu23g1c16c', 'SR:C15-MG{PS:IVU_ID16}', range(6)),
        ('ivu21g1c17u', 'SR:C16-MG{PS:IVU_ID17AMX}', range(6)),
        ('ivu21g1c17d', 'SR:C16-MG{PS:IVU_ID17FMX}', range(6)),
        ]:
        for iCh in ch_inds:

            # For setpoint fields: "cch0", "cch1", "cch2", ...
            fld, hdl = 'cch{0:d}'.format(iCh), 'put'
            pv = new_pv_prefix + ('U%d-I-SP' % (iCh + 1))
            ap.apdata.updateDbPv(DBFILE, pv, elemName, fld,
                                 elemHandle=hdl, tags=tags, quiet=True, epsilon=0.05)

            # For readback fields: "cch0", "cch1", "cch2", ...
            fld, hdl = 'cch{0:d}'.format(iCh), 'get'
            pv = new_pv_prefix + ('U%dLoop-I' % (iCh + 1))
            ap.apdata.updateDbPv(DBFILE, pv, elemName, fld,
                                 elemHandle=hdl, tags=tags, quiet=True, epsilon=0.0)

            # For actual readback fields: "cch0rb1", "cch1rb1", "cch2rb1", ...
            fld, hdl = 'cch{0:d}rb1'.format(iCh), 'get'
            pv = new_pv_prefix + ('U%d-I-I' % (iCh + 1))
            ap.apdata.updateDbPv(DBFILE, pv, elemName, fld,
                                 elemHandle=hdl, tags=tags, quiet=True, epsilon=0.0)

            # For the "cch" readback array PV
            fld, hdl = 'cch[{0:d}]'.format(iCh), 'get'
            pv = new_pv_prefix + ('U%dLoop-I' % (iCh + 1))
            ap.apdata.updateDbPv(DBFILE, pv, elemName, fld,
                                 elemHandle=hdl, tags=tags, quiet=True, epsilon=0.0)

            # For setpoint fields for Orbit Feedforward output:
            #     "orbff0_output", "orbff1_output", "orbff2_output", ...
            fld, hdl = 'orbff{0:d}_output'.format(iCh), 'put'
            pv = new_pv_prefix + ('U%d-I-SP' % (iCh + 1))
            ap.apdata.updateDbPv(DBFILE, pv, elemName, fld,
                                 elemHandle=hdl, tags=tags, quiet=True, epsilon=0.05)

#----------------------------------------------------------------------
def purge_old_ID_orb_cor_PVs_for_C03_10_16_17_IDs():
    """"""

    sys.path.insert(0, '/home/yhidaka/git_repos/hlsqlite')
    import hlsqlite

    db = hlsqlite.SQLiteDatabase(filepath=DBFILE)

    lines = []
    for e in ap.getElements('*'):
        for fld in sorted(e.fields()):
            lines += ['{0}; {1}; setpoint; '.format(e.name, fld) + s
                      for s in e.pv(field=fld, handle='setpoint')]
            lines += ['{0}; {1}; readback; '.format(e.name, fld) + s
                      for s in e.pv(field=fld, handle='readback')]

        lines += sorted(e.pv()) # This includes unlinked (leftover) PVs as well.

    with open('before.txt', 'w') as f:
        f.write('\n'.join(lines))


    if False: # interactive testing section
        table_name = 'pvs'
        column_name_list = ['elemName', 'elemField']
        pprint.pprint(
            db.getColumnDataFromTable(
                table_name, column_name_list=column_name_list,
                condition_str='elemName="ivu21g1c17d"'))

        db.getColumnNames('pvs')

        table_name = 'pvs'
        column_name_list = ['id', 'elemField', 'pv']
        out = db.getColumnDataFromTable(
                table_name, column_name_list=column_name_list,
                condition_str='(elemName="ivu21g1c17d") AND (pv LIKE "%Loop-I")')
        pprint.pprint(list(zip(*out)))

        table_name = 'pvs'
        column_name_list = ['id', 'elemField', 'pv']
        out = db.getColumnDataFromTable(
                table_name, column_name_list=column_name_list,
                condition_str='(elemName="ivu21g1c17d") AND (pv="SR:C17-ID:G1{IVU21:2-MPS}ch2:readback")')
        pprint.pprint(list(zip(*out)))


        table_name = 'pvs'
        column_name_list = ['id', 'elemField', 'pv']
        out = db.getColumnDataFromTable(
                table_name, column_name_list=column_name_list,
                condition_str='(elemName="ivu21g1c17d") AND (pv LIKE "%:readback")')
        pprint.pprint(list(zip(*out)))

        table_name = 'pvs'
        column_name_list = ['id', 'elemField', 'pv']
        out = db.getColumnDataFromTable(
                table_name, column_name_list=column_name_list,
                condition_str='(elemName="ivu21g1c17d") AND (pv LIKE "%:setpoint")')
        pprint.pprint(list(zip(*out)))

        table_name = 'pvs'
        column_name_list = ['id', 'elemField', 'pv']
        out = db.getColumnDataFromTable(
                table_name, column_name_list=column_name_list,
                condition_str='(elemName="ivu21g1c17d") AND (pv LIKE "%:current")')
        pprint.pprint(list(zip(*out)))

        table_name = 'pvs'
        column_name_list = ['id', 'elemField', 'pv']
        out = db.getColumnDataFromTable(
                table_name, column_name_list=column_name_list,
                condition_str='(elemName="ivu21g1c17d") AND (pv LIKE "%:enable")')
        pprint.pprint(list(zip(*out)))


    # Delete the old PVs for ID-03 that are no longer linked to any of the
    # element-field pairs
    table_name = 'pvs'
    db.deleteRows(table_name, condition_str='(elemName="ivu20g1c03c") AND (pv LIKE "%:setpoint")')
    db.deleteRows(table_name, condition_str='(elemName="ivu20g1c03c") AND (pv LIKE "%:readback")')
    db.deleteRows(table_name, condition_str='(elemName="ivu20g1c03c") AND (pv LIKE "%:current")')
    db.deleteRows(table_name, condition_str='(elemName="ivu20g1c03c") AND (pv LIKE "%:enable")')

    # Delete the old PVs for ID-10 that are no longer linked to any of the
    # element-field pairs
    table_name = 'pvs'
    db.deleteRows(table_name, condition_str='(elemName="ivu22g1c10c") AND (pv LIKE "%:setpoint")')
    db.deleteRows(table_name, condition_str='(elemName="ivu22g1c10c") AND (pv LIKE "%:readback")')
    db.deleteRows(table_name, condition_str='(elemName="ivu22g1c10c") AND (pv LIKE "%:current")')

    # Delete the old PVs for ID-16 that are no longer linked to any of the
    # element-field pairs
    table_name = 'pvs'
    db.deleteRows(table_name, condition_str='(elemName="ivu23g1c16c") AND (pv LIKE "%:setpoint")')
    db.deleteRows(table_name, condition_str='(elemName="ivu23g1c16c") AND (pv LIKE "%:readback")')
    db.deleteRows(table_name, condition_str='(elemName="ivu23g1c16c") AND (pv LIKE "%:current")')
    db.deleteRows(table_name, condition_str='(elemName="ivu23g1c16c") AND (pv LIKE "%:enable")')

    # Delete the old PVs for ID-17-1 that are no longer linked to any of the
    # element-field pairs
    table_name = 'pvs'
    db.deleteRows(table_name, condition_str='(elemName="ivu21g1c17u") AND (pv LIKE "%:setpoint")')
    db.deleteRows(table_name, condition_str='(elemName="ivu21g1c17u") AND (pv LIKE "%:readback")')
    db.deleteRows(table_name, condition_str='(elemName="ivu21g1c17u") AND (pv LIKE "%:current")')
    db.deleteRows(table_name, condition_str='(elemName="ivu21g1c17u") AND (pv LIKE "%:enable")')

    # Delete the old PVs for ID-17-2 that are no longer linked to any of the
    # element-field pairs
    table_name = 'pvs'
    db.deleteRows(table_name, condition_str='(elemName="ivu21g1c17d") AND (pv LIKE "%:setpoint")')
    db.deleteRows(table_name, condition_str='(elemName="ivu21g1c17d") AND (pv LIKE "%:readback")')
    db.deleteRows(table_name, condition_str='(elemName="ivu21g1c17d") AND (pv LIKE "%:current")')
    db.deleteRows(table_name, condition_str='(elemName="ivu21g1c17d") AND (pv LIKE "%:enable")')


    db.close()

    ap.machines.load('nsls2', 'SR')

    lines = []
    for e in ap.getElements('*'):
        for fld in sorted(e.fields()):
            lines += ['{0}; {1}; setpoint; '.format(e.name, fld) + s
                      for s in e.pv(field=fld, handle='setpoint')]
            lines += ['{0}; {1}; readback; '.format(e.name, fld) + s
                      for s in e.pv(field=fld, handle='readback')]

        lines += sorted(e.pv()) # This includes unlinked (leftover) PVs as well.

    with open('after.txt', 'w') as f:
        f.write('\n'.join(lines))

    # Manually check "before.txt" and "after.txt" such that the intended
    # PVs have been removed from the database, but nothing else has been changed.

#----------------------------------------------------------------------
def switch_C03_10_16_17_ID_orbcor_PV_unitconv():
    """"""

    if False: #True: # This section can only run once, as HDF5 file does not
                     # allow overwrite of existing datasets

        kw = dict(compression='gzip')

        _temp_unitconv_file = UNITCONV_FILE + '.tmp'

        fnew = h5py.File(_temp_unitconv_file, 'w')
        fold = h5py.File(UNITCONV_FILE, 'r')

        excl_ds_names = \
            ['ID_cch{0:d}_v1'.format(iCh) for iCh in range(6)] + \
            ['ID_cch{0:d}_v2'.format(iCh) for iCh in range(6)] + \
            ['ID_cch{0:d}rb1_v1'.format(iCh) for iCh in range(6)] + \
            ['ID_cch{0:d}rb1_v2'.format(iCh) for iCh in range(6)] + \
            ['ivu_orbff{0:d}_m0_I_type0'.format(iCh) for iCh in range(6)] + \
            ['ivu_orbff{0:d}_m0_I_type1'.format(iCh) for iCh in range(4)] + \
            ['ivu_orbff{0:d}_m0_I_type2'.format(iCh) for iCh in range(6)]

        # First copy existing unit conversion data
        gold = fold['UnitConversion']
        gnew = fnew.create_group('UnitConversion')
        for k, v in gold.items():

            if False: # This will end up with bigger file size
                d = gnew.create_dataset(k, data=v.value, **kw)
            else: # This will end up with smaller file size, so use this one!
                gnew[k] = v.value
                d = gnew[k]

            if k in excl_ds_names:
                continue
            else:
                for ak, av in v.attrs.items():
                    put_h5py_attr(d, ak, av)

        # Updating to new unit conversions
        for iCh in range(6):

            k = 'ID_cch{0:d}_v1'.format(iCh)
            #
            v = gold[k]
            d = gnew[k]
            #
            for ak, av in v.attrs.items():
                if ak == 'elements':
                    elem_names = av.tolist()
                    elem_names.remove('ivu20g1c03c')
                    if iCh <= 3:
                        elem_names.remove('ivu22g1c10c')
                    elem_names.remove('ivu23g1c16c')
                    elem_names.remove('ivu21g1c17u')
                    elem_names.remove('ivu21g1c17d')
                    av = np.array(elem_names)
                put_h5py_attr(d, ak, av)


            k = 'ID_cch{0:d}_v2'.format(iCh)
            #
            v = gold[k]
            d = gnew[k]
            #
            for ak, av in v.attrs.items():
                if ak == 'elements':
                    elem_names = av.tolist()
                    elem_names += ['ivu20g1c03c',]
                    if iCh <= 3:
                        elem_names += ['ivu22g1c10c',]
                    elem_names += ['ivu23g1c16c', 'ivu21g1c17u', 'ivu21g1c17d']
                    av = np.array(elem_names)
                put_h5py_attr(d, ak, av)



            k = 'ID_cch{0:d}rb1_v1'.format(iCh)
            #
            v = gold[k]
            d = gnew[k]
            #
            for ak, av in v.attrs.items():
                if ak == 'elements':
                    elem_names = av.tolist()
                    elem_names.remove('ivu20g1c03c')
                    if iCh <= 3:
                        elem_names.remove('ivu22g1c10c')
                    elem_names.remove('ivu23g1c16c')
                    elem_names.remove('ivu21g1c17u')
                    elem_names.remove('ivu21g1c17d')
                    av = np.array(elem_names)
                put_h5py_attr(d, ak, av)


            k = 'ID_cch{0:d}rb1_v2'.format(iCh)
            #
            v = gold[k]
            d = gnew[k]
            #
            for ak, av in v.attrs.items():
                if ak == 'elements':
                    elem_names = av.tolist()
                    elem_names += ['ivu20g1c03c',]
                    if iCh <= 3:
                        elem_names += ['ivu22g1c10c',]
                    elem_names += ['ivu23g1c16c', 'ivu21g1c17u', 'ivu21g1c17d']
                    av = np.array(elem_names)
                put_h5py_attr(d, ak, av)



            k = 'ivu_orbff{0:d}_m0_I_type0'.format(iCh)
            #
            v = gold[k]
            d = gnew[k]
            #
            for ak, av in v.attrs.items():
                if ak == 'elements':
                    elem_names = av.tolist()
                    elem_names.remove('ivu20g1c03c')
                    elem_names.remove('ivu23g1c16c')
                    elem_names.remove('ivu21g1c17u')
                    elem_names.remove('ivu21g1c17d')
                    av = np.array(elem_names)
                put_h5py_attr(d, ak, av)


            k = 'ivu_orbff{0:d}_m0_I_type2'.format(iCh)
            #
            v = gold[k]
            d = gnew[k]
            #
            for ak, av in v.attrs.items():
                if ak == 'elements':
                    elem_names = av.tolist()
                    elem_names += ['ivu20g1c03c',]
                    if iCh <= 3:
                        elem_names += ['ivu22g1c10c',]
                    elem_names += ['ivu23g1c16c', 'ivu21g1c17u', 'ivu21g1c17d']
                    av = np.array(elem_names)
                put_h5py_attr(d, ak, av)

        fold.close()
        fnew.close()

        # Make sure the new file has the correct permission
        os.chmod(_temp_unitconv_file, 0o755)

        shutil.move(_temp_unitconv_file, UNITCONV_FILE)

    #
    # Test if the unit conversion works
    #

    ap.machines.loadfast('nsls2', 'SR')

    for e in sorted(
        ap.getElements('ivu*c03*') + ap.getElements('ivu*c10*') +
        ap.getElements('ivu*c16*') + ap.getElements('ivu*c17*')):
        print('## {0} ##'.format(e.name))

        if e.name == 'ivu22g1c10c':
            nCh = 4
        else:
            nCh = 6

        for hdl_list, fld_list in [
            (['readback', 'setpoint'], ['cch{0:d}'.format(iCh) for iCh in range(nCh)]),
            (['readback',], ['cch{0:d}rb1'.format(iCh) for iCh in range(nCh)]),
            (['setpoint',], ['orbff{0:d}_m0_I'.format(iCh) for iCh in range(nCh)]),
            ]:

            for fld in fld_list:
                for hdl in hdl_list:
                    print('{0}/{1}: {2}, {3}'.format(
                        fld, hdl, e.getUnit(fld, handle=hdl, unitsys=None),
                        e.getUnit(fld, handle=hdl, unitsys='phy')))

                    raw_val = 1.0
                    np.testing.assert_almost_equal(
                        raw_val,
                        e.convertUnit(fld, raw_val, None, 'phy', handle=hdl),
                        decimal=12
                    )

    plt.show()

#----------------------------------------------------------------------
def update_epsilon_for_BNL_PSI_channels():
    """"""

    tags = ["aphla.sys.SR"]
    cch_epsilon = 0.01 # [A]

    id_list = sorted(
        ap.getElements('ivu*c03*') + ap.getElements('ivu*c04*') +
        ap.getElements('ivu*c05*') + ap.getElements('ivu*c10*') +
        ap.getElements('ivu*c16*') + ap.getElements('ivu*c17*')
    )

    _kws = dict(epsilon=cch_epsilon)

    for idobj in id_list:

        elemName = idobj.name
        orbcor_fields = sorted(
            [_f for _f in idobj.fields() if _f.startswith('cch')])

        for fld in orbcor_fields:

            pv = idobj.pv(field=fld, handle='setpoint')
            if pv != []:
                ap.apdata.updateDbPv(
                    DBFILE, pv[0], elemName, fld, elemHandle='put', tags=tags,
                    quiet=True, **_kws)

            pv = idobj.pv(field=fld, handle='readback')
            if pv != []:
                ap.apdata.updateDbPv(
                    DBFILE, pv[0], elemName, fld, elemHandle='get', tags=tags,
                    quiet=True, **_kws)

#----------------------------------------------------------------------
def print_all_ID_cch_values():
    """"""

    ap.machines.loadfast('nsls2', 'SR')

    text = []

    for idname in [e.name for e in ap.getElements('ID')]:

        idobj = ap.getElements(idname)[0]

        text.append('## {0} ##'.format(idname))

        ch_inds = []
        for fld in idobj.fields():
            if fld.startswith('cch'):
                try:
                    ch_inds.append(int(fld[3:]))
                except:
                    continue
        ch_inds = np.sort(ch_inds)

        for iCh in ch_inds:

            for fld in ['cch{0:d}'.format(iCh), 'cch{0:d}rb1'.format(iCh)]:

                for hdl in ['setpoint', 'readback']:

                    if hdl == 'setpoint' and fld.endswith('rb1'):
                        continue

                    for unitsys in [None, 'phy']:

                        unit_str = idobj.getUnit(fld, handle=hdl, unitsys=unitsys)
                        val = idobj.get(fld, handle=hdl, unitsys=unitsys)

                        text.append('{0}:{1}:{2}:{3} = {4:.4g} [{5}]'.format(
                            idname, fld, hdl, unitsys if unitsys is not None else 'None',
                            val if val is not None else np.nan, unit_str))


    print('\n'.join(text))

#----------------------------------------------------------------------
def update_C04_gap_PVs():
    """
    """

    idobj = ap.getElements('ivu23g1c04u')[0]

    elemName = idobj.name

    if False:

        for fld in sorted(idobj.fields()):
            if not fld.startswith('gap'):
                continue
            for handle in ['setpoint', 'readback']:
                print('{0} ({1}): {2}'.format(fld, handle, str(idobj.pv(field=fld, handle=handle))))

        '''
        Output before DB change:

ivu23g1c04u
gap (setpoint): ['SR:C04-ID:G1{IVU:1-Mtr:2}Inp:Pos']
gap (readback): ['SR:C04-ID:G1{IVU:1-LEnc}Gap']
gap_hilim (setpoint): []
gap_hilim (readback): ['SR:C04-ID:G1{IVU:1-Mtr:2}Inp:Pos.DRVH']
gap_hinominal (setpoint): []
gap_hinominal (readback): ['SR:C04-ID:NomOpen-Sp']
gap_lolim (setpoint): []
gap_lolim (readback): ['SR:C04-ID:G1{IVU:1-Mtr:2}Inp:Pos.DRVL']
gap_lonominal (setpoint): []
gap_lonominal (readback): ['SR:C04-ID:NomClose-Sp']
gap_ramping (setpoint): []
gap_ramping (readback): ['SR:C04-ID:G1{IVU:1-Mtr:2}Pos.MOVN']
gap_speed (setpoint): ['SR:C04-ID:G1{IVU:1-Mtr:1}S']
gap_speed (readback): ['SR:C04-ID:G1{IVU:1-Mtr:1}S:RB']
gap_trig (setpoint): ['SR:C04-ID:G1{IVU:1-Mtr:2}Sw:Go']
gap_trig (readback): []
        '''

    new_pvs = {}
    new_pvs['gap'] = dict(setpoint='SR:C04-ID:G1{IVU:1-Ax:Gap}-Mtr-SP',
                          readback='SR:C04-ID:G1{IVU:1-Ax:Gap}-Mtr.RBV')
    new_pvs['gap_hilim'] = dict(readback=new_pvs['gap']['setpoint']+'.DRVH')
    new_pvs['gap_lolim'] = dict(readback=new_pvs['gap']['setpoint']+'.DRVL')
    new_pvs['gap_hinominal'] = dict(readback='SR:C04-ID:NomOpen-Sp')
    new_pvs['gap_lonominal'] = dict(readback='SR:C04-ID:NomClose-Sp')
    new_pvs['gap_ramping'] = dict(readback='SR:C04-ID:G1{IVU:1-Ax:Gap}-Mtr.MOVN')
    new_pvs['gap_speed'] = dict(setpoint='SR:C04-ID:G1{IVU:1}GapSpeed-SP',
                                readback='SR:C04-ID:G1{IVU:1}GapSpeed-RB')
    new_pvs['gap_trig'] = dict(setpoint='SR:C04-ID:G1{IVU:1-Ax:Gap}-Mtr-Go')

    tags = ["aphla.sys.SR"]

    for fld, d in new_pvs.items():
        for handle, pv in d.items():
            if handle == 'readback':
                hdl = 'get'
            elif handle == 'setpoint':
                hdl = 'put'
            else:
                raise ValueError()
            ap.apdata.updateDbPv(
                DBFILE, pv, elemName, fld, elemHandle=hdl, tags=tags, quiet=True)




    # Then purge old PV data from DB file
    sys.path.insert(0, '/home/yhidaka/git_repos/hlsqlite')
    import hlsqlite

    db = hlsqlite.SQLiteDatabase(filepath=DBFILE)

    lines = []
    for e in ap.getElements('*'):
        for fld in sorted(e.fields()):
            lines += ['{0}; {1}; setpoint; '.format(e.name, fld) + s
                      for s in e.pv(field=fld, handle='setpoint')]
            lines += ['{0}; {1}; readback; '.format(e.name, fld) + s
                      for s in e.pv(field=fld, handle='readback')]

        lines += sorted(e.pv()) # This includes unlinked (leftover) PVs as well.

    with open('before.txt', 'w') as f:
        f.write('\n'.join(lines))

    # Delete the old PVs that are no longer linked to any of the
    # element-field pairs
    table_name = 'pvs'
    db.deleteRows(table_name,
        condition_str='(elemName="ivu23g1c04u") AND (pv="SR:C04-ID:G1{IVU:1-Mtr:2}Inp:Pos")')
    db.deleteRows(table_name,
        condition_str='(elemName="ivu23g1c04u") AND (pv="SR:C04-ID:G1{IVU:1-Mtr:2}Inp:Pos.DRVL")')
    db.deleteRows(table_name,
        condition_str='(elemName="ivu23g1c04u") AND (pv="SR:C04-ID:G1{IVU:1-Mtr:2}Inp:Pos.DRVH")')
    db.deleteRows(table_name,
        condition_str='(elemName="ivu23g1c04u") AND (pv="SR:C04-ID:G1{IVU:1-LEnc}Gap")')
    db.deleteRows(table_name,
        condition_str='(elemName="ivu23g1c04u") AND (pv="SR:C04-ID:G1{IVU:1-Mtr:2}Pos.MOVN")')
    db.deleteRows(table_name,
        condition_str='(elemName="ivu23g1c04u") AND (pv="SR:C04-ID:G1{IVU:1-Mtr:1}S")')
    db.deleteRows(table_name,
        condition_str='(elemName="ivu23g1c04u") AND (pv="SR:C04-ID:G1{IVU:1-Mtr:1}S:RB")')
    db.deleteRows(table_name,
        condition_str='(elemName="ivu23g1c04u") AND (pv="SR:C04-ID:G1{IVU:1-Mtr:2}Sw:Go")')

    db.close()

    ap.machines.load('nsls2', 'SR')

    lines = []
    for e in ap.getElements('*'):
        for fld in sorted(e.fields()):
            lines += ['{0}; {1}; setpoint; '.format(e.name, fld) + s
                      for s in e.pv(field=fld, handle='setpoint')]
            lines += ['{0}; {1}; readback; '.format(e.name, fld) + s
                      for s in e.pv(field=fld, handle='readback')]

        lines += sorted(e.pv()) # This includes unlinked (leftover) PVs as well.

    with open('after.txt', 'w') as f:
        f.write('\n'.join(lines))

    # Manually check "before.txt" and "after.txt" such that the intended
    # PVs have been removed from the database, but nothing else has been changed.

#----------------------------------------------------------------------
def update_C12_gap_PVs():
    """
    """

    idobj = ap.getElements('ivu23g1c12d')[0]

    elemName = idobj.name

    if False:

        for fld in sorted(idobj.fields()):
            if not fld.startswith('gap'):
                continue
            for handle in ['setpoint', 'readback']:
                print('{0} ({1}): {2}'.format(fld, handle, str(idobj.pv(field=fld, handle=handle))))

        '''
        Output before DB change:

gap (setpoint): ['SR:C12-ID:G1{IVU:1-Mtr:2}Inp:Pos']
gap (readback): ['SR:C12-ID:G1{IVU:1-LEnc}Gap']
gap_hilim (setpoint): []
gap_hilim (readback): ['SR:C12-ID:G1{IVU:1-Mtr:2}Inp:Pos.DRVH']
gap_hinominal (setpoint): []
gap_hinominal (readback): ['SR:C12-ID:NomOpen-Sp']
gap_lolim (setpoint): []
gap_lolim (readback): ['SR:C12-ID:G1{IVU:1-Mtr:2}Inp:Pos.DRVL']
gap_lonominal (setpoint): []
gap_lonominal (readback): ['SR:C12-ID:NomClose-Sp']
gap_ramping (setpoint): []
gap_ramping (readback): ['SR:C12-ID:G1{IVU:1-Mtr:2}Pos.MOVN']
gap_speed (setpoint): ['SR:C12-ID:G1{IVU:1-Mtr:1}S']
gap_speed (readback): ['SR:C12-ID:G1{IVU:1-Mtr:1}S:RB']
gap_trig (setpoint): ['SR:C12-ID:G1{IVU:1-Mtr:2}Sw:Go']
gap_trig (readback): []
        '''

    new_pvs = {}
    new_pvs['gap'] = dict(setpoint='SR:C12-ID:G1{IVU:1-Ax:Gap}-Mtr-SP',
                          readback='SR:C12-ID:G1{IVU:1-Ax:Gap}-Mtr.RBV')
    new_pvs['gap_hilim'] = dict(readback=new_pvs['gap']['setpoint']+'.DRVH')
    new_pvs['gap_lolim'] = dict(readback=new_pvs['gap']['setpoint']+'.DRVL')
    new_pvs['gap_hinominal'] = dict(readback='SR:C12-ID:NomOpen-Sp')
    new_pvs['gap_lonominal'] = dict(readback='SR:C12-ID:NomClose-Sp')
    new_pvs['gap_ramping'] = dict(readback='SR:C12-ID:G1{IVU:1-Ax:Gap}-Mtr.MOVN')
    new_pvs['gap_speed'] = dict(setpoint='SR:C12-ID:G1{IVU:1}GapSpeed-SP',
                                readback='SR:C12-ID:G1{IVU:1}GapSpeed-RB')
    new_pvs['gap_trig'] = dict(setpoint='SR:C12-ID:G1{IVU:1-Ax:Gap}-Mtr-Go')

    tags = ["aphla.sys.SR"]

    for fld, d in new_pvs.items():
        for handle, pv in d.items():
            if handle == 'readback':
                hdl = 'get'
            elif handle == 'setpoint':
                hdl = 'put'
            else:
                raise ValueError()
            ap.apdata.updateDbPv(
                DBFILE, pv, elemName, fld, elemHandle=hdl, tags=tags, quiet=True)




    # Then purge old PV data from DB file
    sys.path.insert(0, '/home/yhidaka/git_repos/hlsqlite')
    import hlsqlite

    db = hlsqlite.SQLiteDatabase(filepath=DBFILE)

    lines = []
    for e in ap.getElements('*'):
        for fld in sorted(e.fields()):
            lines += ['{0}; {1}; setpoint; '.format(e.name, fld) + s
                      for s in e.pv(field=fld, handle='setpoint')]
            lines += ['{0}; {1}; readback; '.format(e.name, fld) + s
                      for s in e.pv(field=fld, handle='readback')]

        lines += sorted(e.pv()) # This includes unlinked (leftover) PVs as well.

    with open('before.txt', 'w') as f:
        f.write('\n'.join(lines))

    # Delete the old PVs that are no longer linked to any of the
    # element-field pairs
    table_name = 'pvs'
    db.deleteRows(table_name,
        condition_str='(elemName="ivu23g1c12d") AND (pv="SR:C12-ID:G1{IVU:1-Mtr:2}Inp:Pos")')
    db.deleteRows(table_name,
        condition_str='(elemName="ivu23g1c12d") AND (pv="SR:C12-ID:G1{IVU:1-Mtr:2}Inp:Pos.DRVL")')
    db.deleteRows(table_name,
        condition_str='(elemName="ivu23g1c12d") AND (pv="SR:C12-ID:G1{IVU:1-Mtr:2}Inp:Pos.DRVH")')
    db.deleteRows(table_name,
        condition_str='(elemName="ivu23g1c12d") AND (pv="SR:C12-ID:G1{IVU:1-LEnc}Gap")')
    db.deleteRows(table_name,
        condition_str='(elemName="ivu23g1c12d") AND (pv="SR:C12-ID:G1{IVU:1-Mtr:2}Pos.MOVN")')
    db.deleteRows(table_name,
        condition_str='(elemName="ivu23g1c12d") AND (pv="SR:C12-ID:G1{IVU:1-Mtr:1}S")')
    db.deleteRows(table_name,
        condition_str='(elemName="ivu23g1c12d") AND (pv="SR:C12-ID:G1{IVU:1-Mtr:1}S:RB")')
    db.deleteRows(table_name,
        condition_str='(elemName="ivu23g1c12d") AND (pv="SR:C12-ID:G1{IVU:1-Mtr:2}Sw:Go")')

    db.close()

    ap.machines.load('nsls2', 'SR')

    lines = []
    for e in ap.getElements('*'):
        for fld in sorted(e.fields()):
            lines += ['{0}; {1}; setpoint; '.format(e.name, fld) + s
                      for s in e.pv(field=fld, handle='setpoint')]
            lines += ['{0}; {1}; readback; '.format(e.name, fld) + s
                      for s in e.pv(field=fld, handle='readback')]

        lines += sorted(e.pv()) # This includes unlinked (leftover) PVs as well.

    with open('after.txt', 'w') as f:
        f.write('\n'.join(lines))

    # Manually check "before.txt" and "after.txt" such that the intended
    # PVs have been removed from the database, but nothing else has been changed.

#----------------------------------------------------------------------
def update_C16_gap_PVs():
    """
    """

    idobj = ap.getElements('ivu23g1c16c')[0]

    elemName = idobj.name

    if False:

        for fld in sorted(idobj.fields()):
            if not fld.startswith('gap'):
                continue
            for handle in ['setpoint', 'readback']:
                print('{0} ({1}): {2}'.format(fld, handle, str(idobj.pv(field=fld, handle=handle))))

        '''
        Output before DB change:

gap (setpoint): ['SR:C16-ID:G1{IVU:1-Mtr:2}Inp:Pos']
gap (readback): ['SR:C16-ID:G1{IVU:1-LEnc}Gap']
gap_hilim (setpoint): []
gap_hilim (readback): ['SR:C16-ID:G1{IVU:1-Mtr:2}Inp:Pos.DRVH']
gap_hinominal (setpoint): []
gap_hinominal (readback): ['SR:C16-ID:NomOpen-Sp']
gap_lolim (setpoint): []
gap_lolim (readback): ['SR:C16-ID:G1{IVU:1-Mtr:2}Inp:Pos.DRVL']
gap_lonominal (setpoint): []
gap_lonominal (readback): ['SR:C16-ID:NomClose-Sp']
gap_ramping (setpoint): []
gap_ramping (readback): ['SR:C16-ID:G1{IVU:1-Mtr:2}Pos.MOVN']
gap_speed (setpoint): ['SR:C16-ID:G1{IVU:1-Mtr:1}S']
gap_speed (readback): ['SR:C16-ID:G1{IVU:1-Mtr:1}S:RB']
gap_trig (setpoint): ['SR:C16-ID:G1{IVU:1-Mtr:2}Sw:Go']
gap_trig (readback): []
        '''

    new_pvs = {}
    new_pvs['gap'] = dict(setpoint='SR:C16-ID:G1{IVU:1-Ax:Gap}-Mtr-SP',
                          readback='SR:C16-ID:G1{IVU:1-Ax:Gap}-Mtr.RBV')
    new_pvs['gap_hilim'] = dict(readback=new_pvs['gap']['setpoint']+'.DRVH')
    new_pvs['gap_lolim'] = dict(readback=new_pvs['gap']['setpoint']+'.DRVL')
    new_pvs['gap_hinominal'] = dict(readback='SR:C16-ID:NomOpen-Sp')
    new_pvs['gap_lonominal'] = dict(readback='SR:C16-ID:NomClose-Sp')
    new_pvs['gap_ramping'] = dict(readback='SR:C16-ID:G1{IVU:1-Ax:Gap}-Mtr.MOVN')
    new_pvs['gap_speed'] = dict(setpoint='SR:C16-ID:G1{IVU:1}GapSpeed-SP',
                                readback='SR:C16-ID:G1{IVU:1}GapSpeed-RB')
    new_pvs['gap_trig'] = dict(setpoint='SR:C16-ID:G1{IVU:1-Ax:Gap}-Mtr-Go')

    tags = ["aphla.sys.SR"]

    for fld, d in new_pvs.items():
        for handle, pv in d.items():
            if handle == 'readback':
                hdl = 'get'
            elif handle == 'setpoint':
                hdl = 'put'
            else:
                raise ValueError()
            ap.apdata.updateDbPv(
                DBFILE, pv, elemName, fld, elemHandle=hdl, tags=tags, quiet=True)




    # Then purge old PV data from DB file
    sys.path.insert(0, '/home/yhidaka/git_repos/hlsqlite')
    import hlsqlite

    db = hlsqlite.SQLiteDatabase(filepath=DBFILE)

    lines = []
    for e in ap.getElements('*'):
        for fld in sorted(e.fields()):
            lines += ['{0}; {1}; setpoint; '.format(e.name, fld) + s
                      for s in e.pv(field=fld, handle='setpoint')]
            lines += ['{0}; {1}; readback; '.format(e.name, fld) + s
                      for s in e.pv(field=fld, handle='readback')]

        lines += sorted(e.pv()) # This includes unlinked (leftover) PVs as well.

    with open('before.txt', 'w') as f:
        f.write('\n'.join(lines))

    # Delete the old PVs that are no longer linked to any of the
    # element-field pairs
    table_name = 'pvs'
    db.deleteRows(table_name,
        condition_str='(elemName="ivu23g1c16c") AND (pv="SR:C16-ID:G1{IVU:1-Mtr:2}Inp:Pos")')
    db.deleteRows(table_name,
        condition_str='(elemName="ivu23g1c16c") AND (pv="SR:C16-ID:G1{IVU:1-Mtr:2}Inp:Pos.DRVL")')
    db.deleteRows(table_name,
        condition_str='(elemName="ivu23g1c16c") AND (pv="SR:C16-ID:G1{IVU:1-Mtr:2}Inp:Pos.DRVH")')
    db.deleteRows(table_name,
        condition_str='(elemName="ivu23g1c16c") AND (pv="SR:C16-ID:G1{IVU:1-LEnc}Gap")')
    db.deleteRows(table_name,
        condition_str='(elemName="ivu23g1c16c") AND (pv="SR:C16-ID:G1{IVU:1-Mtr:2}Pos.MOVN")')
    db.deleteRows(table_name,
        condition_str='(elemName="ivu23g1c16c") AND (pv="SR:C16-ID:G1{IVU:1-Mtr:1}S")')
    db.deleteRows(table_name,
        condition_str='(elemName="ivu23g1c16c") AND (pv="SR:C16-ID:G1{IVU:1-Mtr:1}S:RB")')
    db.deleteRows(table_name,
        condition_str='(elemName="ivu23g1c16c") AND (pv="SR:C16-ID:G1{IVU:1-Mtr:2}Sw:Go")')

    db.close()

    ap.machines.load('nsls2', 'SR')

    lines = []
    for e in ap.getElements('*'):
        for fld in sorted(e.fields()):
            lines += ['{0}; {1}; setpoint; '.format(e.name, fld) + s
                      for s in e.pv(field=fld, handle='setpoint')]
            lines += ['{0}; {1}; readback; '.format(e.name, fld) + s
                      for s in e.pv(field=fld, handle='readback')]

        lines += sorted(e.pv()) # This includes unlinked (leftover) PVs as well.

    with open('after.txt', 'w') as f:
        f.write('\n'.join(lines))

    # Manually check "before.txt" and "after.txt" such that the intended
    # PVs have been removed from the database, but nothing else has been changed.

#----------------------------------------------------------------------
def update_C04_12_16_gap_unitconvs():
    """
    """

    if False: # Check where C04, C12, C16 ID unit conversion data need to be updated.

        affected_id_names = ['ivu23g1c04u', 'ivu23g1c12d', 'ivu23g1c16c']

        fold = h5py.File(UNITCONV_FILE, 'r')
        gold = fold['UnitConversion']
        for k, v in gold.items():
            for ak, av in v.attrs.items():
                if ak == 'elements':
                    elem_names = av.tolist()
                    for _affec_name in affected_id_names:
                        if _affec_name in elem_names:
                            print(k)
                            break
        fold.close()

        ''' Output: (* denotes gap-related unit conversion fields)

ID_cch0_v1
ID_cch0_v2
ID_cch0rb1_v1
ID_cch0rb1_v2
ID_cch1_v1
ID_cch1_v2
ID_cch1rb1_v1
ID_cch1rb1_v2
ID_cch2_v1
ID_cch2_v2
ID_cch2rb1_v1
ID_cch2rb1_v2
ID_cch3_v1
ID_cch3_v2
ID_cch3rb1_v1
ID_cch3rb1_v2
ID_cch4_v1
ID_cch4_v2
ID_cch4rb1_v1
ID_cch4rb1_v2
ID_cch5_v1
ID_cch5_v2
ID_cch5rb1_v1
ID_cch5rb1_v2
* ID_ivu_c04u_c12d_c16c_c17ud_gap_rb
* ivu_gap_hilim_type0
* ivu_gap_hinominal_type0
* ivu_gap_lolim_type0
* ivu_gap_lonominal_type0
* ivu_gap_speed_type0
ivu_orbff0_m0_I_type0
ivu_orbff0_m0_I_type2
* ivu_orbff0_m0_gap_type0
ivu_orbff1_m0_I_type0
ivu_orbff1_m0_I_type2
* ivu_orbff1_m0_gap_type0
ivu_orbff2_m0_I_type0
ivu_orbff2_m0_I_type2
* ivu_orbff2_m0_gap_type0
ivu_orbff3_m0_I_type0
ivu_orbff3_m0_I_type2
* ivu_orbff3_m0_gap_type0
ivu_orbff4_m0_I_type0
ivu_orbff4_m0_I_type2
* ivu_orbff4_m0_gap_type0
ivu_orbff5_m0_I_type0
ivu_orbff5_m0_I_type2
* ivu_orbff5_m0_gap_type0
        '''


    if False: #True: # This section can only run once, as HDF5 file does not
                     # allow overwrite of existing datasets

        kw = dict(compression='gzip')

        _temp_unitconv_file = UNITCONV_FILE + '.tmp'

        fnew = h5py.File(_temp_unitconv_file, 'w')
        fold = h5py.File(UNITCONV_FILE, 'r')

        delete_ds_names = ['ID_ivu_c04u_c12d_c16c_c17ud_gap_rb',]

        excl_ds_names = \
            ['ID_gap_rb_um_to_mm', 'ID_gap_sp_um_to_mm',
             'ivu_gap_hilim_type0', 'ivu_gap_hilim_type1',
             'ivu_gap_lolim_type0', 'ivu_gap_lolim_type1',
             'ivu_gap_hinominal_type0', 'ivu_gap_hinominal_type1',
             'ivu_gap_lonominal_type0', 'ivu_gap_lonominal_type1',
             'ivu_gap_speed_type0', 'ivu_gap_speed_type1',
             'ivu_orbff0_m0_gap_type0', 'ivu_orbff0_m0_gap_type2',
             'ivu_orbff1_m0_gap_type0', 'ivu_orbff1_m0_gap_type2',
             'ivu_orbff2_m0_gap_type0', 'ivu_orbff2_m0_gap_type2',
             'ivu_orbff3_m0_gap_type0', 'ivu_orbff3_m0_gap_type2',
             'ivu_orbff4_m0_gap_type0', 'ivu_orbff4_m0_gap_type2',
             'ivu_orbff5_m0_gap_type0', 'ivu_orbff5_m0_gap_type2',
             ]

        # First copy existing unit conversion data
        gold = fold['UnitConversion']
        gnew = fnew.create_group('UnitConversion')
        for k, v in gold.items():

            if k in delete_ds_names:
                continue

            if False: # This will end up with bigger file size
                d = gnew.create_dataset(k, data=v.value, **kw)
            else: # This will end up with smaller file size, so use this one!
                gnew[k] = v.value
                d = gnew[k]

            if k in excl_ds_names:
                continue
            else:
                for ak, av in v.attrs.items():
                    put_h5py_attr(d, ak, av)

        # Updating to new unit conversions
        for k in ['ID_gap_rb_um_to_mm', 'ID_gap_sp_um_to_mm']:
            v = gold[k]
            d = gnew[k]
            #
            for ak, av in v.attrs.items():
                if ak == 'elements':
                    elem_names = av.tolist()
                    elem_names += ['ivu23g1c04u', 'ivu23g1c12d', 'ivu23g1c16c']
                    av = np.array(elem_names)
                put_h5py_attr(d, ak, av)
        #
        v = gold['ID_ivu_c04u_c12d_c16c_c17ud_gap_rb']
        gnew['ID_gap_rb_mm_to_mm'] = v.value
        d = gnew['ID_gap_rb_mm_to_mm']
        #
        for ak, av in v.attrs.items():
            if ak == 'elements':
                elem_names = av.tolist()
                elem_names.remove('ivu23g1c04u')
                elem_names.remove('ivu23g1c12d')
                elem_names.remove('ivu23g1c16c')
                av = np.array(elem_names)
            put_h5py_attr(d, ak, av)
        #
        for k in ['ivu_gap_hilim_type0', 'ivu_gap_lolim_type0',
                  'ivu_gap_hinominal_type0', 'ivu_gap_lonominal_type0',
                  'ivu_gap_speed_type0',
                  'ivu_orbff0_m0_gap_type0', 'ivu_orbff1_m0_gap_type0',
                  'ivu_orbff2_m0_gap_type0', 'ivu_orbff3_m0_gap_type0',
                  'ivu_orbff4_m0_gap_type0', 'ivu_orbff5_m0_gap_type0']:
            v = gold[k]
            d = gnew[k]
            #
            for ak, av in v.attrs.items():
                if ak == 'elements':
                    elem_names = av.tolist()
                    elem_names.remove('ivu23g1c04u')
                    elem_names.remove('ivu23g1c12d')
                    elem_names.remove('ivu23g1c16c')
                    av = np.array(elem_names)
                put_h5py_attr(d, ak, av)
        #
        for k in ['ivu_gap_hilim_type1', 'ivu_gap_lolim_type1',
                  'ivu_gap_hinominal_type1', 'ivu_gap_lonominal_type1',
                  'ivu_gap_speed_type1',
                  'ivu_orbff0_m0_gap_type2', 'ivu_orbff1_m0_gap_type2',
                  'ivu_orbff2_m0_gap_type2', 'ivu_orbff3_m0_gap_type2',
                  'ivu_orbff4_m0_gap_type2', ]:
            v = gold[k]
            d = gnew[k]
            #
            for ak, av in v.attrs.items():
                if ak == 'elements':
                    elem_names = av.tolist()
                    elem_names += ['ivu23g1c04u', 'ivu23g1c12d', 'ivu23g1c16c']
                    av = np.array(elem_names)
                put_h5py_attr(d, ak, av)
        #
        v = gnew['ivu_orbff4_m0_gap_type2']
        gnew['ivu_orbff5_m0_gap_type2'] = v.value
        d = gnew['ivu_orbff5_m0_gap_type2']
        #
        for ak, av in v.attrs.items():
            if ak == 'field':
                av = 'orbff5_m0_gap'
            put_h5py_attr(d, ak, av)


        fold.close()
        fnew.close()

        # Make sure the new file has the correct permission
        os.chmod(_temp_unitconv_file, 0o755)

        shutil.move(_temp_unitconv_file, UNITCONV_FILE)

    #
    # Test if the unit conversion works
    #

    ap.machines.loadfast('nsls2', 'SR')

    for e in sorted(
        ap.getElements('ivu*c04*') + ap.getElements('ivu*c12*') +
        ap.getElements('ivu*c16*')):
        print('## {0} ##'.format(e.name))

        for hdl_list, fld_list in [
            (['readback', 'setpoint'], ['gap', 'gap_speed']),
            (['readback',], ['gap_hilim', 'gap_lolim',
                             'gap_hinominal', 'gap_lonominal',]),
            (['setpoint',], ['orbff{0:d}_m0_gap'.format(iCh) for iCh in range(6)]),
            ]:

            for fld in fld_list:
                for hdl in hdl_list:
                    print('{0}/{1}: {2}, {3}'.format(
                        fld, hdl, e.getUnit(fld, handle=hdl, unitsys=None),
                        e.getUnit(fld, handle=hdl, unitsys='phy')))

                    val_1mm_in_mm = 1.0
                    val_1mm_in_um = 1e3
                    np.testing.assert_almost_equal(
                        val_1mm_in_mm,
                        e.convertUnit(fld, val_1mm_in_um, None, 'phy', handle=hdl),
                        decimal=12
                    )

    plt.show()

#----------------------------------------------------------------------
def add_gap_phase_limit_PVs_to_C07_IDs():
    """
    """

    idobj = ap.getElements('ovu42g1c07u')[0]

    elemName = idobj.name
#=0.001*'SR:C07-2-ID:NomClose-Sp'

    new_pvs = {}
    new_pvs['gap_hilim'] = dict(readback='SR:C07-ID:G1A{SST2:1-Ax:Gap}MaxGap-RB')
    new_pvs['gap_lolim'] = dict(readback='SR:C07-ID:G1A{SST2:1-Ax:Gap}MinGap-RB')
    new_pvs['gap_hinominal'] = dict(readback='SR:C07-2-ID:NomOpen-Sp')
    new_pvs['gap_lonominal'] = dict(readback='SR:C07-2-ID:NomClose-Sp')

    tags = ["aphla.sys.SR"]

    for fld, d in new_pvs.items():
        for handle, pv in d.items():
            if handle == 'readback':
                hdl = 'get'
            elif handle == 'setpoint':
                hdl = 'put'
            else:
                raise ValueError()
            ap.apdata.updateDbPv(
                DBFILE, pv, elemName, fld, elemHandle=hdl, tags=tags, quiet=True)


    idobj = ap.getElements('epu60g1c07d')[0]

    elemName = idobj.name
#=0.001*'SR:C07-1-ID:NomClose-Sp'

    new_pvs = {}
    new_pvs['gap_hilim'] = dict(readback='SR:C07-ID:G1A{SST1:1-Ax:Gap}MaxGap-RB')
    new_pvs['gap_lolim'] = dict(readback='SR:C07-ID:G1A{SST1:1-Ax:Gap}MinGap-RB')
    new_pvs['gap_hinominal'] = dict(readback='SR:C07-1-ID:NomOpen-Sp')
    new_pvs['gap_lonominal'] = dict(readback='SR:C07-1-ID:NomClose-Sp')
    new_pvs['phase_hilim'] = dict(readback='SR:C07-ID:G1A{SST1:1-Ax:Phase}-Mtr-SP.DRVH')
    new_pvs['phase_lolim'] = dict(readback='SR:C07-ID:G1A{SST1:1-Ax:Phase}-Mtr-SP.DRVL')

    tags = ["aphla.sys.SR"]

    for fld, d in new_pvs.items():
        for handle, pv in d.items():
            if handle == 'readback':
                hdl = 'get'
            elif handle == 'setpoint':
                hdl = 'put'
            else:
                raise ValueError()
            ap.apdata.updateDbPv(
                DBFILE, pv, elemName, fld, elemHandle=hdl, tags=tags, quiet=True)

#----------------------------------------------------------------------
def add_unitconvs_to_gap_phase_limit_to_C07_IDs():
    """"""

    if False: #True: # This section can only run once, as HDF5 file does not
                     # allow overwrite of existing datasets

        kw = dict(compression='gzip')

        _temp_unitconv_file = UNITCONV_FILE + '.tmp'

        fnew = h5py.File(_temp_unitconv_file, 'w')
        fold = h5py.File(UNITCONV_FILE, 'r')

        delete_ds_names = []

        excl_ds_names = \
            ['ivu_gap_hilim_type1', 'ivu_gap_lolim_type1',
             'ivu_gap_hinominal_type1', 'ivu_gap_lonominal_type1',
             'epu_gap_hilim_type0', 'epu_gap_lolim_type0',
             'epu_gap_hinominal_type0', 'epu_gap_lonominal_type0',
             'epu_phase_hilim_type0', 'epu_phase_lolim_type0',
             ]

        # First copy existing unit conversion data
        gold = fold['UnitConversion']
        gnew = fnew.create_group('UnitConversion')
        for k, v in gold.items():

            if k in delete_ds_names:
                continue

            if False: # This will end up with bigger file size
                d = gnew.create_dataset(k, data=v.value, **kw)
            else: # This will end up with smaller file size, so use this one!
                gnew[k] = v.value
                d = gnew[k]

            if k in excl_ds_names:
                continue
            else:
                for ak, av in v.attrs.items():
                    put_h5py_attr(d, ak, av)

        # Updating to new unit conversions
        for k in ['ivu_gap_hilim_type1', 'ivu_gap_lolim_type1',
                  'ivu_gap_hinominal_type1', 'ivu_gap_lonominal_type1']:
            v = gold[k]
            d = gnew[k]
            #
            for ak, av in v.attrs.items():
                if ak == 'elements':
                    elem_names = av.tolist()
                    elem_names += ['ovu42g1c07u',]
                    av = np.array(elem_names)
                put_h5py_attr(d, ak, av)
        #
        for k in ['epu_gap_hilim_type0', 'epu_gap_lolim_type0',
                  'epu_gap_hinominal_type0', 'epu_gap_lonominal_type0',
                  'epu_phase_hilim_type0', 'epu_phase_lolim_type0']:
            v = gold[k]
            d = gnew[k]
            #
            for ak, av in v.attrs.items():
                if ak == 'elements':
                    elem_names = av.tolist()
                    elem_names += ['epu60g1c07d',]
                    av = np.array(elem_names)
                put_h5py_attr(d, ak, av)



        fold.close()
        fnew.close()

        # Make sure the new file has the correct permission
        os.chmod(_temp_unitconv_file, 0o755)

        shutil.move(_temp_unitconv_file, UNITCONV_FILE)

    #
    # Test if the unit conversion works
    #

    ap.machines.loadfast('nsls2', 'SR')

    for e in sorted(
        ap.getElements('ovu*c07*') + ap.getElements('epu*c07*')):
        print('## {0} ##'.format(e.name))

        for hdl_list, fld_list in [
            (['readback', 'setpoint'], []),
            (['readback',], ['gap_hilim', 'gap_lolim',
                             'gap_hinominal', 'gap_lonominal',
                             'phase_hilim', 'phase_lolim']),
            (['setpoint',], []),
            ]:

            for fld in fld_list:
                if fld not in e.fields():
                    continue
                for hdl in hdl_list:
                    print('{0}/{1}: {2}, {3}'.format(
                        fld, hdl, e.getUnit(fld, handle=hdl, unitsys=None),
                        e.getUnit(fld, handle=hdl, unitsys='phy')))

                    val_1mm_in_mm = 1.0
                    val_1mm_in_um = 1e3
                    np.testing.assert_almost_equal(
                        val_1mm_in_mm,
                        e.convertUnit(fld, val_1mm_in_um, None, 'phy', handle=hdl),
                        decimal=12
                    )

    plt.show()

#----------------------------------------------------------------------
def replace_sum_PVSP_to_SP1_for_orbff_C03_16_17_IDs():
    """"""

    tags = ['aphla.sys.SR']

    # These IVUs have PLFB, so the PVSP ending with "SP" is the sum,
    # the PVSP ending with "SP1" is used for orbit feedforward system,
    # while the PVSP ending with "SP2" is used for PLFB system.
    # You cannot directly change the sum "SP" PV, which you can try change
    # it and momentarirly changes, but it will be immediately reverted
    # to the sum value of "SP1" and "SP2".
    #
    # Originally I set the setpoint PVs to the sum "SP" PVs, but now
    # changing them to "SP1" PVs.
    for elemName, new_pv_prefix, ch_inds in [
        ('ivu20g1c03c', 'SR:C02-MG{PS:IVU_ID3}', range(6)),
        ('ivu23g1c16c', 'SR:C15-MG{PS:IVU_ID16}', range(6)),
        ('ivu21g1c17u', 'SR:C16-MG{PS:IVU_ID17AMX}', range(6)),
        ('ivu21g1c17d', 'SR:C16-MG{PS:IVU_ID17FMX}', range(6)),
        ]:
        for iCh in ch_inds:

            # For setpoint fields: "cch0", "cch1", "cch2", ...
            fld, hdl = 'cch{0:d}'.format(iCh), 'put'
            pv = new_pv_prefix + ('U%d-I-SP1' % (iCh + 1))
            ap.apdata.updateDbPv(DBFILE, pv, elemName, fld,
                                 elemHandle=hdl, tags=tags, quiet=True, epsilon=0.05)

            # For setpoint fields for Orbit Feedforward output:
            #     "orbff0_output", "orbff1_output", "orbff2_output", ...
            fld, hdl = 'orbff{0:d}_output'.format(iCh), 'put'
            pv = new_pv_prefix + ('U%d-I-SP1' % (iCh + 1))
            ap.apdata.updateDbPv(DBFILE, pv, elemName, fld,
                                 elemHandle=hdl, tags=tags, quiet=True, epsilon=0.05)



    sys.path.insert(0, '/home/yhidaka/git_repos/hlsqlite')
    import hlsqlite

    db = hlsqlite.SQLiteDatabase(filepath=DBFILE)

    lines = []
    for e in ap.getElements('*'):
        for fld in sorted(e.fields()):
            lines += ['{0}; {1}; setpoint; '.format(e.name, fld) + s
                      for s in e.pv(field=fld, handle='setpoint')]
            lines += ['{0}; {1}; readback; '.format(e.name, fld) + s
                      for s in e.pv(field=fld, handle='readback')]

        lines += sorted(e.pv()) # This includes unlinked (leftover) PVs as well.

    with open('before.txt', 'w') as f:
        f.write('\n'.join(lines))


    if False: # interactive testing section
        table_name = 'pvs'
        column_name_list = ['elemName', 'elemField']
        pprint.pprint(
            db.getColumnDataFromTable(
                table_name, column_name_list=column_name_list,
                condition_str='elemName="ivu21g1c17d"'))

        db.getColumnNames('pvs')

        table_name = 'pvs'
        column_name_list = ['id', 'elemField', 'pv']
        out = db.getColumnDataFromTable(
                table_name, column_name_list=column_name_list,
                condition_str='(elemName="ivu21g1c17d") AND (pv LIKE "%-I-SP")')
        pprint.pprint(list(zip(*out)))

        table_name = 'pvs'
        column_name_list = ['id', 'elemField', 'pv']
        out = db.getColumnDataFromTable(
                table_name, column_name_list=column_name_list,
                condition_str='(elemName="ivu20g1c03c") AND (pv="SR:C02-MG{PS:IVU_ID3}U1-I-SP")')
        pprint.pprint(list(zip(*out)))

        table_name = 'pvs'
        column_name_list = ['id', 'elemField', 'pv']
        out = db.getColumnDataFromTable(
                table_name, column_name_list=column_name_list,
                condition_str='(elemName="ivu21g1c17d") AND (pv LIKE "%:setpoint")')
        pprint.pprint(list(zip(*out)))


    # Delete the old sum setpoint PVs that are no longer linked to any of the
    # element-field pairs
    table_name = 'pvs'
    db.deleteRows(table_name, condition_str='(elemName="ivu20g1c03c") AND (pv LIKE "%-I-SP")')
    db.deleteRows(table_name, condition_str='(elemName="ivu23g1c16c") AND (pv LIKE "%-I-SP")')
    db.deleteRows(table_name, condition_str='(elemName="ivu21g1c17u") AND (pv LIKE "%-I-SP")')
    db.deleteRows(table_name, condition_str='(elemName="ivu21g1c17d") AND (pv LIKE "%-I-SP")')


    db.close()

    ap.machines.load('nsls2', 'SR')

    lines = []
    for e in ap.getElements('*'):
        for fld in sorted(e.fields()):
            lines += ['{0}; {1}; setpoint; '.format(e.name, fld) + s
                      for s in e.pv(field=fld, handle='setpoint')]
            lines += ['{0}; {1}; readback; '.format(e.name, fld) + s
                      for s in e.pv(field=fld, handle='readback')]

        lines += sorted(e.pv()) # This includes unlinked (leftover) PVs as well.

    with open('after.txt', 'w') as f:
        f.write('\n'.join(lines))

    # Manually check "before.txt" and "after.txt" such that the intended
    # PVs have been removed from the database, but nothing else has been changed.


#----------------------------------------------------------------------
def change_cch_readback_PVs_to_cch_rb1_PVs_for_BNL_PSI_ID_cors():
    """
    The usual readback being used for the purpose of orbit feedforward
    table generation is the type of "U%Loop-I" for BNL PSIs. But for these
    BNL PSIs, the actual readback "U%-I-I" PVs, which are usually assigned
    to aphla elements' "cch[0-5]rb1" fields, seem to show better agreement
    with their setpoint values. So, I am replacing "cch[0-5]" readback PVs
    with "U%-I-I" in order to use smaller epsilon.

    Affected IDs (as of 01/26/2019):
    # epu57g1c02c
    # ivu20g1c03c
    # ivu23g1c04u
    # ivu21g1c05d
    # ovu42g1c07u
    # epu60g1c07d
    # ivu22g1c10c
    # ivu23g1c16c
    # ivu21g1c17u
    # ivu21g1c17d
    # ivu18g1c19u
    # epu57g1c21u
    # epu105g1c21d
    """

    tags = ['aphla.sys.SR']\

    for idobj in [idobj for idobj in ap.getElements('ID')
                  if idobj.getUnit('cch0', unitsys=None) == 'A']:

        print('# ' + idobj.name)
        for iCh in range(6):
            fld = 'cch{0:d}'.format(iCh)
            if fld not in idobj.fields():
                continue

            pv_rb1 = idobj.pv(field=fld+'rb1', handle='readback')[0]
            hdl = 'get'
            elemName = idobj.name
            ap.apdata.updateDbPv(
                DBFILE, pv_rb1, elemName, fld,
                elemHandle=hdl, tags=tags, quiet=True, epsilon=0.05)

    ap.machines.load('nsls2', 'SR')

    id_list = ap.getElements('ID')

    # They all have to be "U%-I-I"
    for idobj in [idobj for idobj in id_list
                  if idobj.getUnit('cch0', unitsys=None) == 'A']:
        print('# ' + idobj.name)
        for iCh in range(6):
            fld = 'cch{0:d}'.format(iCh)
            if fld not in idobj.fields():
                continue
            print(idobj.pv(field=fld, handle='readback'))

    # They all have to be "ch%:readback"
    for idobj in [idobj for idobj in id_list
                  if not idobj.getUnit('cch0', unitsys=None) == 'A']:
        print('# ' + idobj.name)
        for iCh in range(6):
            fld = 'cch{0:d}'.format(iCh)
            if fld not in idobj.fields():
                continue
            print(idobj.pv(field=fld, handle='readback'))

#----------------------------------------------------------------------
def update_epsilon_for_all_ID_cor_BNL_PSI_channels():
    """
01/26/2019:

epsilons [A] (based on max discrepancy observed at half limit current)

epu57g1c02c.cch[0-5]: 0.05

c03.cch: not measured at this time

ivu23g1c04u.cch[0-5]: 0.05

ivu21g1c05d.cch[0-1]: 0.05
ivu21g1c05d.cch[2-3]: disconnected
ivu21g1c05d.cch[4-5]: 0.05

ovu42g1c07u.cch[0-3]: 0.08

epu60g1c07d.cch[0-3]: 0.02

ivu22g1c10c.cch[0-3]: 0.02

ivu23g1c16c.cch[0-5]: 0.03

ivu21g1c17u.cch[0-5]: 0.02

ivu21g1c17d.cch[0-5]: 0.02

ivu18g1c19u.cch[0-4]: 0.02

epu57g1c21u.cch[0-5]: 0.03

epu105g1c21d.cch[0-1]: 0.08
epu105g1c21d.cch[2-3]: disconnected
epu105g1c21d.cch[4-5]: 0.08
"""

    tags = ["aphla.sys.SR"]

    idobj_ch_eps_list = [
        (ap.getElements('epu57g1c02c')[0], list(range(6)), 0.05),
        (ap.getElements('ivu23g1c04u')[0], list(range(6)), 0.05),
        (ap.getElements('ivu21g1c05d')[0], [0,1,4,5], 0.05),
        (ap.getElements('ivu21g1c05d')[0], [2,3], 0.0),
        (ap.getElements('ovu42g1c07u')[0], list(range(4)), 0.08),
        (ap.getElements('epu60g1c07d')[0], list(range(4)), 0.02),
        (ap.getElements('ivu22g1c10c')[0], list(range(4)), 0.02),
        (ap.getElements('ivu23g1c16c')[0], list(range(6)), 0.03),
        (ap.getElements('ivu21g1c17u')[0], list(range(6)), 0.02),
        (ap.getElements('ivu21g1c17d')[0], list(range(6)), 0.02),
        (ap.getElements('ivu18g1c19u')[0], list(range(5)), 0.02),
        (ap.getElements('epu57g1c21u')[0], list(range(6)), 0.03),
        (ap.getElements('epu105g1c21d')[0], [0,1,4,5], 0.08),
        (ap.getElements('epu105g1c21d')[0], [2,3], 0.0),
    ]

    for idobj, ch_inds, cch_epsilon in idobj_ch_eps_list:

        elemName = idobj.name
        orbcor_fields = ['cch{0:d}'.format(_i) for _i in ch_inds]

        for fld in orbcor_fields:

            pv = idobj.pv(field=fld, handle='setpoint')
            if pv != []:
                ap.apdata.updateDbPv(
                    DBFILE, pv[0], elemName, fld, elemHandle='put', tags=tags,
                    quiet=True, epsilon=cch_epsilon)

            pv = idobj.pv(field=fld, handle='readback')
            if pv != []:
                ap.apdata.updateDbPv(
                    DBFILE, pv[0], elemName, fld, elemHandle='get', tags=tags,
                    quiet=True, epsilon=cch_epsilon)

#----------------------------------------------------------------------
def fix_cch_list_readback_PVs_for_c03_04_05_10_16_17():
    """
    Found that idobj.cch contained only one PV for these IDs. The orbit
    feedforward script relies on the length of ".cch" array to figure out
    how many orbit corrector channels are available. So, this problem is
    fixed by this function.
    """

    id_list = ap.getElements('ivu20g1c03c') + ap.getElements('ivu23g1c04u') + \
        ap.getElements('ivu21g1c05d') + ap.getElements('ivu22g1c10c') + \
        ap.getElements('ivu23g1c16c') + ap.getElements('ivu21g1c17[ud]')

    tags = ["aphla.sys.SR"]

    for idobj in id_list:
        elemName = idobj.name
        hdl = 'get'
        for iCh in range(6):
            fld = 'cch{0:d}'.format(iCh)
            if fld not in idobj.fields():
                continue
            pv = idobj.pv(field=fld, handle='readback')[0]
            mod_fld = 'cch[{0:d}]'.format(iCh)
            ap.apdata.updateDbPv(
                DBFILE, pv, elemName, mod_fld, elemHandle=hdl, tags=tags,
                quiet=True, epsilon=idobj.getEpsilon(fld))

#----------------------------------------------------------------------
def add_2nd_channels_for_C02_CL1B_C03_CL1A_to_C03_ID_cch():
    """"""

    tags = ['aphla.sys.SR']

    elemName = 'ivu20g1c03c'

    # ### For setpoint fields: "cch6", "cch7", "cch8", "cch9" ###
    #
    fld, hdl = 'cch6', 'put'
    pv = 'SR:C02-MG{PS:CL1B}I:Sp1_2-SP'
    # ^ 2nd setpoint channel for upstream horizontal slow corrector
    ap.apdata.updateDbPv(DBFILE, pv, elemName, fld,
                         elemHandle=hdl, tags=tags, quiet=True, epsilon=0.05)
    #
    fld, hdl = 'cch7', 'put'
    pv = 'SR:C02-MG{PS:CL1B}I:Sp2_2-SP'
    # ^ 2nd setpoint channel for upstream vertical slow corrector
    ap.apdata.updateDbPv(DBFILE, pv, elemName, fld,
                         elemHandle=hdl, tags=tags, quiet=True, epsilon=0.05)
    #
    fld, hdl = 'cch8', 'put'
    pv = 'SR:C03-MG{PS:CL1A}I:Sp1_2-SP'
    # ^ 2nd setpoint channel for downstream horizontal slow corrector
    ap.apdata.updateDbPv(DBFILE, pv, elemName, fld,
                         elemHandle=hdl, tags=tags, quiet=True, epsilon=0.05)
    #
    fld, hdl = 'cch9', 'put'
    pv = 'SR:C03-MG{PS:CL1A}I:Sp2_2-SP'
    # ^ 2nd setpoint channel for downstream vertical slow corrector
    ap.apdata.updateDbPv(DBFILE, pv, elemName, fld,
                         elemHandle=hdl, tags=tags, quiet=True, epsilon=0.05)

    # ### For readback fields: "cch6", "cch7", "cch8", "cch9" ###
    # These readbacks are for the sum PVs, not just for the 2nd setpoint channels,
    # so the setpoint and readback will always differ significantly.
    #
    fld, hdl = 'cch6', 'get'
    cch_list_fld = 'cch[6]'
    pv = 'SR:C02-MG{PS:CL1B}I:Ps1DCCT1-I'
    # ^ sum readback for upstream horizontal slow corrector
    for _fld in [fld, cch_list_fld]:
        ap.apdata.updateDbPv(DBFILE, pv, elemName, _fld,
                             elemHandle=hdl, tags=tags, quiet=True, epsilon=0.05)
    #
    fld, hdl = 'cch7', 'get'
    cch_list_fld = 'cch[7]'
    pv = 'SR:C02-MG{PS:CL1B}I:Ps2DCCT1-I'
    # ^ sum readback for upstream vertical slow corrector
    for _fld in [fld, cch_list_fld]:
        ap.apdata.updateDbPv(DBFILE, pv, elemName, _fld,
                             elemHandle=hdl, tags=tags, quiet=True, epsilon=0.05)
    #
    fld, hdl = 'cch8', 'get'
    cch_list_fld = 'cch[8]'
    pv = 'SR:C03-MG{PS:CL1A}I:Ps1DCCT1-I'
    # ^ sum readback for downstream horizontal slow corrector
    for _fld in [fld, cch_list_fld]:
        ap.apdata.updateDbPv(DBFILE, pv, elemName, _fld,
                             elemHandle=hdl, tags=tags, quiet=True, epsilon=0.05)
    #
    fld, hdl = 'cch9', 'get'
    cch_list_fld = 'cch[9]'
    pv = 'SR:C03-MG{PS:CL1A}I:Ps2DCCT1-I'
    # ^ sum readback for downstream vertical slow corrector
    for _fld in [fld, cch_list_fld]:
        ap.apdata.updateDbPv(DBFILE, pv, elemName, _fld,
                             elemHandle=hdl, tags=tags, quiet=True, epsilon=0.05)



    # ### For setpoint fields for Orbit Feedforward output:
    #     Redirect "orbff0_output" to "cch6"
    #              "orbff1_output" to "cch7"
    #              "orbff4_output" to "cch8"
    #              "orbff5_output" to "cch9"
    fld, hdl = 'orbff0_output', 'put'
    pv = 'SR:C02-MG{PS:CL1B}I:Sp1_2-SP'
    ap.apdata.updateDbPv(DBFILE, pv, elemName, fld,
                         elemHandle=hdl, tags=tags, quiet=True, epsilon=0.05)
    #
    fld, hdl = 'orbff1_output', 'put'
    pv = 'SR:C02-MG{PS:CL1B}I:Sp2_2-SP'
    ap.apdata.updateDbPv(DBFILE, pv, elemName, fld,
                         elemHandle=hdl, tags=tags, quiet=True, epsilon=0.05)
    #
    fld, hdl = 'orbff4_output', 'put'
    pv = 'SR:C03-MG{PS:CL1A}I:Sp1_2-SP'
    ap.apdata.updateDbPv(DBFILE, pv, elemName, fld,
                         elemHandle=hdl, tags=tags, quiet=True, epsilon=0.05)
    #
    fld, hdl = 'orbff5_output', 'put'
    pv = 'SR:C03-MG{PS:CL1A}I:Sp2_2-SP'
    ap.apdata.updateDbPv(DBFILE, pv, elemName, fld,
                         elemHandle=hdl, tags=tags, quiet=True, epsilon=0.05)

#----------------------------------------------------------------------
def add_units_for_C03_ID_cch6thru9():
    """"""

    if False: #True: # This section can only run once, as HDF5 file does not
                     # allow overwrite of existing datasets

        kw = dict(compression='gzip')

        _temp_unitconv_file = UNITCONV_FILE + '.tmp'

        fnew = h5py.File(_temp_unitconv_file, 'w')
        fold = h5py.File(UNITCONV_FILE, 'r')

        delete_ds_names = []

        excl_ds_names = []

        # First copy existing unit conversion data
        gold = fold['UnitConversion']
        gnew = fnew.create_group('UnitConversion')
        for k, v in gold.items():

            if k in delete_ds_names:
                continue

            if False: # This will end up with bigger file size
                d = gnew.create_dataset(k, data=v.value, **kw)
            else: # This will end up with smaller file size, so use this one!
                gnew[k] = v.value
                d = gnew[k]

            if k in excl_ds_names:
                continue
            else:
                for ak, av in v.attrs.items():
                    put_h5py_attr(d, ak, av)

        for iCh in [6, 7, 8, 9]:
            k = 'ID_cch{0:d}_v2'.format(iCh)
            v = gold['ID_cch5_v2']
            gnew[k] = v.value
            d = gnew[k]
            #
            for ak, av in v.attrs.items():
                if ak == 'elements':
                    elem_names = ['ivu20g1c03c',]
                    av = np.array(elem_names)
                elif ak == 'field':
                    av = 'cch{0:d}'.format(iCh)
                put_h5py_attr(d, ak, av)

        fold.close()
        fnew.close()

        # Make sure the new file has the correct permission
        os.chmod(_temp_unitconv_file, 0o755)

        shutil.move(_temp_unitconv_file, UNITCONV_FILE)

    #
    # Test if the unit conversion works
    #

    ap.machines.loadfast('nsls2', 'SR')

    for e in sorted(ap.getElements('ivu*c03*')):
        print('## {0} ##'.format(e.name))

        for hdl_list, fld_list in [
            (['readback', 'setpoint'], ['cch6', 'cch7', 'cch8', 'cch9']),
            (['readback',], []),
            (['setpoint',], ['orbff{0:d}_m0_I'.format(iCh) for iCh in range(6)]),
            ]:

            for fld in fld_list:
                for hdl in hdl_list:
                    print('{0}/{1}: {2}, {3}'.format(
                        fld, hdl, e.getUnit(fld, handle=hdl, unitsys=None),
                        e.getUnit(fld, handle=hdl, unitsys='phy')))

                    val_1A_in_A = 1.0
                    val_1mm_in_um = 1e3
                    np.testing.assert_almost_equal(
                        val_1A_in_A,
                        e.convertUnit(fld, val_1A_in_A, None, 'phy', handle=hdl),
                        decimal=12
                    )

    plt.show()

#----------------------------------------------------------------------
def update_C03_gap_PVs():
    """
    """

    idobj = ap.getElements('ivu20g1c03c')[0]

    elemName = idobj.name

    if False:

        for fld in sorted(idobj.fields()):
            if not fld.startswith('gap'):
                continue
            for handle in ['setpoint', 'readback']:
                print('{0} ({1}): {2}'.format(fld, handle, str(idobj.pv(field=fld, handle=handle))))

        '''
        Output before DB change:

ivu20g1c03c
gap (setpoint): ['SR:C3-ID:G1{IVU20:1-Mtr:2}Inp:Pos']
gap (readback): ['SR:C3-ID:G1{IVU20:1-Mtr:2}Pos.RBV']
gap_hilim (setpoint): []
gap_hilim (readback): ['SR:C3-ID:G1{IVU20:1-Mtr:2}Inp:Pos.DRVH']
gap_hinominal (setpoint): []
gap_hinominal (readback): ['SR:C03-ID:NomOpen-Sp']
gap_lolim (setpoint): []
gap_lolim (readback): ['SR:C3-ID:G1{IVU20:1-Mtr:2}Inp:Pos.DRVL']
gap_lonominal (setpoint): []
gap_lonominal (readback): ['SR:C03-ID:NomClose-Sp']
gap_speed (setpoint): ['SR:C3-ID:G1{IVU20:1-Mtr:2}S']
gap_speed (readback): ['SR:C3-ID:G1{IVU20:1-Mtr:2}S:RB']
gap_trig (setpoint): ['SR:C3-ID:G1{IVU20:1-Mtr:2}Sw:Go']
gap_trig (readback): []
        '''

    new_pvs = {}
    new_pvs['gap'] = dict(setpoint='SR:C3-ID:G1{IVU20:1-Ax:Gap}-Mtr-SP',
                          readback='SR:C3-ID:G1{IVU20:1-Ax:Gap}-Mtr.RBV')
    new_pvs['gap_hilim'] = dict(readback=new_pvs['gap']['setpoint']+'.DRVH')
    new_pvs['gap_lolim'] = dict(readback=new_pvs['gap']['setpoint']+'.DRVL')
    new_pvs['gap_hinominal'] = dict(readback='SR:C03-ID:NomOpen-Sp')
    new_pvs['gap_lonominal'] = dict(readback='SR:C03-ID:NomClose-Sp')
    new_pvs['gap_ramping'] = dict(readback='SR:C3-ID:G1{IVU20:1-Ax:Gap}-Mtr.MOVN')
    new_pvs['gap_speed'] = dict(setpoint='SR:C3-ID:G1{IVU20:1}GapSpeed-SP',
                                readback='SR:C3-ID:G1{IVU20:1}GapSpeed-RB')
    new_pvs['gap_trig'] = dict(setpoint='SR:C3-ID:G1{IVU20:1-Ax:Gap}-Mtr-Go')

    tags = ["aphla.sys.SR"]

    for fld, d in new_pvs.items():
        for handle, pv in d.items():
            if handle == 'readback':
                hdl = 'get'
            elif handle == 'setpoint':
                hdl = 'put'
            else:
                raise ValueError()
            ap.apdata.updateDbPv(
                DBFILE, pv, elemName, fld, elemHandle=hdl, tags=tags, quiet=True)




    # Then purge old PV data from DB file
    sys.path.insert(0, '/home/yhidaka/git_repos/hlsqlite')
    import hlsqlite

    db = hlsqlite.SQLiteDatabase(filepath=DBFILE)

    lines = []
    for e in ap.getElements('*'):
        for fld in sorted(e.fields()):
            lines += ['{0}; {1}; setpoint; '.format(e.name, fld) + s
                      for s in e.pv(field=fld, handle='setpoint')]
            lines += ['{0}; {1}; readback; '.format(e.name, fld) + s
                      for s in e.pv(field=fld, handle='readback')]

        lines += sorted(e.pv()) # This includes unlinked (leftover) PVs as well.

    with open('before.txt', 'w') as f:
        f.write('\n'.join(lines))

    # Delete the old PVs that are no longer linked to any of the
    # element-field pairs
    table_name = 'pvs'
    db.deleteRows(table_name,
        condition_str='(elemName="ivu20g1c03c") AND (pv="SR:C3-ID:G1{IVU20:1-Mtr:2}Inp:Pos")')
    db.deleteRows(table_name,
        condition_str='(elemName="ivu20g1c03c") AND (pv="SR:C3-ID:G1{IVU20:1-Mtr:2}Pos.RBV")')
    db.deleteRows(table_name,
        condition_str='(elemName="ivu20g1c03c") AND (pv="SR:C3-ID:G1{IVU20:1-Mtr:2}Inp:Pos.DRVH")')
    db.deleteRows(table_name,
        condition_str='(elemName="ivu20g1c03c") AND (pv="SR:C3-ID:G1{IVU20:1-Mtr:2}Inp:Pos.DRVL")')
    db.deleteRows(table_name,
        condition_str='(elemName="ivu20g1c03c") AND (pv="SR:C3-ID:G1{IVU20:1-Mtr:2}S")')
    db.deleteRows(table_name,
        condition_str='(elemName="ivu20g1c03c") AND (pv="SR:C3-ID:G1{IVU20:1-Mtr:2}S:RB")')
    db.deleteRows(table_name,
        condition_str='(elemName="ivu20g1c03c") AND (pv="SR:C3-ID:G1{IVU20:1-Mtr:2}Sw:Go")')

    db.close()

    ap.machines.load('nsls2', 'SR')

    lines = []
    for e in ap.getElements('*'):
        for fld in sorted(e.fields()):
            lines += ['{0}; {1}; setpoint; '.format(e.name, fld) + s
                      for s in e.pv(field=fld, handle='setpoint')]
            lines += ['{0}; {1}; readback; '.format(e.name, fld) + s
                      for s in e.pv(field=fld, handle='readback')]

        lines += sorted(e.pv()) # This includes unlinked (leftover) PVs as well.

    with open('after.txt', 'w') as f:
        f.write('\n'.join(lines))

    # Manually check "before.txt" and "after.txt" such that the intended
    # PVs have been removed from the database, but nothing else has been changed.

#----------------------------------------------------------------------
def update_C05_gap_PVs():
    """
    """

    idobj = ap.getElements('ivu21g1c05d')[0]

    elemName = idobj.name

    if False:

        for fld in sorted(idobj.fields()):
            if not fld.startswith('gap'):
                continue
            for handle in ['setpoint', 'readback']:
                print('{0} ({1}): {2}'.format(fld, handle, str(idobj.pv(field=fld, handle=handle))))

        '''
        Output before DB change:

ivu21g1c05d
gap (setpoint): ['SR:C5-ID:G1{IVU21:1-Mtr:2}Inp:Pos']
gap (readback): ['SR:C5-ID:G1{IVU21:1-Mtr:2}Pos.RBV']
gap_hilim (setpoint): []
gap_hilim (readback): ['SR:C5-ID:G1{IVU21:1-Mtr:2}Inp:Pos.DRVH']
gap_hinominal (setpoint): []
gap_hinominal (readback): ['SR:C05-ID:NomOpen-Sp']
gap_lolim (setpoint): []
gap_lolim (readback): ['SR:C5-ID:G1{IVU21:1-Mtr:2}Inp:Pos.DRVL']
gap_lonominal (setpoint): []
gap_lonominal (readback): ['SR:C05-ID:NomClose-Sp']
gap_speed (setpoint): ['SR:C5-ID:G1{IVU21:1-Mtr:2}S']
gap_speed (readback): ['SR:C5-ID:G1{IVU21:1-Mtr:2}S:RB']
gap_trig (setpoint): ['SR:C5-ID:G1{IVU21:1-Mtr:2}Sw:Go']
gap_trig (readback): []
        '''

    new_pvs = {}
    new_pvs['gap'] = dict(setpoint='SR:C5-ID:G1{IVU21:1-Ax:Gap}-Mtr-SP',
                          readback='SR:C5-ID:G1{IVU21:1-Ax:Gap}-Mtr.RBV')
    new_pvs['gap_hilim'] = dict(readback=new_pvs['gap']['setpoint']+'.DRVH')
    new_pvs['gap_lolim'] = dict(readback=new_pvs['gap']['setpoint']+'.DRVL')
    new_pvs['gap_hinominal'] = dict(readback='SR:C05-ID:NomOpen-Sp')
    new_pvs['gap_lonominal'] = dict(readback='SR:C05-ID:NomClose-Sp')
    new_pvs['gap_ramping'] = dict(readback='SR:C5-ID:G1{IVU21:1-Ax:Gap}-Mtr.MOVN')
    new_pvs['gap_speed'] = dict(setpoint='SR:C5-ID:G1{IVU21:1}GapSpeed-SP',
                                readback='SR:C5-ID:G1{IVU21:1}GapSpeed-RB')
    new_pvs['gap_trig'] = dict(setpoint='SR:C5-ID:G1{IVU21:1-Ax:Gap}-Mtr-Go')

    tags = ["aphla.sys.SR"]

    for fld, d in new_pvs.items():
        for handle, pv in d.items():
            if handle == 'readback':
                hdl = 'get'
            elif handle == 'setpoint':
                hdl = 'put'
            else:
                raise ValueError()
            ap.apdata.updateDbPv(
                DBFILE, pv, elemName, fld, elemHandle=hdl, tags=tags, quiet=True)




    # Then purge old PV data from DB file
    sys.path.insert(0, '/home/yhidaka/git_repos/hlsqlite')
    import hlsqlite

    db = hlsqlite.SQLiteDatabase(filepath=DBFILE)

    lines = []
    for e in ap.getElements('*'):
        for fld in sorted(e.fields()):
            lines += ['{0}; {1}; setpoint; '.format(e.name, fld) + s
                      for s in e.pv(field=fld, handle='setpoint')]
            lines += ['{0}; {1}; readback; '.format(e.name, fld) + s
                      for s in e.pv(field=fld, handle='readback')]

        lines += sorted(e.pv()) # This includes unlinked (leftover) PVs as well.

    with open('before.txt', 'w') as f:
        f.write('\n'.join(lines))

    # Delete the old PVs that are no longer linked to any of the
    # element-field pairs
    table_name = 'pvs'
    db.deleteRows(table_name,
        condition_str='(elemName="ivu21g1c05d") AND (pv="SR:C5-ID:G1{IVU21:1-Mtr:2}Inp:Pos")')
    db.deleteRows(table_name,
        condition_str='(elemName="ivu21g1c05d") AND (pv="SR:C5-ID:G1{IVU21:1-Mtr:2}Pos.RBV")')
    db.deleteRows(table_name,
        condition_str='(elemName="ivu21g1c05d") AND (pv="SR:C5-ID:G1{IVU21:1-Mtr:2}Inp:Pos.DRVH")')
    db.deleteRows(table_name,
        condition_str='(elemName="ivu21g1c05d") AND (pv="SR:C5-ID:G1{IVU21:1-Mtr:2}Inp:Pos.DRVL")')
    db.deleteRows(table_name,
        condition_str='(elemName="ivu21g1c05d") AND (pv="SR:C5-ID:G1{IVU21:1-Mtr:2}S")')
    db.deleteRows(table_name,
        condition_str='(elemName="ivu21g1c05d") AND (pv="SR:C5-ID:G1{IVU21:1-Mtr:2}S:RB")')
    db.deleteRows(table_name,
        condition_str='(elemName="ivu21g1c05d") AND (pv="SR:C5-ID:G1{IVU21:1-Mtr:2}Sw:Go")')

    db.close()

    ap.machines.load('nsls2', 'SR')

    lines = []
    for e in ap.getElements('*'):
        for fld in sorted(e.fields()):
            lines += ['{0}; {1}; setpoint; '.format(e.name, fld) + s
                      for s in e.pv(field=fld, handle='setpoint')]
            lines += ['{0}; {1}; readback; '.format(e.name, fld) + s
                      for s in e.pv(field=fld, handle='readback')]

        lines += sorted(e.pv()) # This includes unlinked (leftover) PVs as well.

    with open('after.txt', 'w') as f:
        f.write('\n'.join(lines))

    # Manually check "before.txt" and "after.txt" such that the intended
    # PVs have been removed from the database, but nothing else has been changed.

#----------------------------------------------------------------------
def update_C11_gap_PVs():
    """
    """

    idobj = ap.getElements('ivu20g1c11c')[0]

    elemName = idobj.name

    if False:

        for fld in sorted(idobj.fields()):
            if not fld.startswith('gap'):
                continue
            for handle in ['setpoint', 'readback']:
                print('{0} ({1}): {2}'.format(fld, handle, str(idobj.pv(field=fld, handle=handle))))

        '''
        Output before DB change:

ivu20g1c11c
gap (setpoint): ['SR:C11-ID:G1{IVU20:1-Mtr:2}Inp:Pos']
gap (readback): ['SR:C11-ID:G1{IVU20:1-Mtr:2}Pos.RBV']
gap_hilim (setpoint): []
gap_hilim (readback): ['SR:C11-ID:G1{IVU20:1-Mtr:2}Inp:Pos.DRVH']
gap_hinominal (setpoint): []
gap_hinominal (readback): ['SR:C11-ID:NomOpen-Sp']
gap_lolim (setpoint): []
gap_lolim (readback): ['SR:C11-ID:G1{IVU20:1-Mtr:2}Inp:Pos.DRVL']
gap_lonominal (setpoint): []
gap_lonominal (readback): ['SR:C11-ID:NomClose-Sp']
gap_speed (setpoint): ['SR:C11-ID:G1{IVU20:1-Mtr:2}S']
gap_speed (readback): ['SR:C11-ID:G1{IVU20:1-Mtr:2}S:RB']
gap_trig (setpoint): ['SR:C11-ID:G1{IVU20:1-Mtr:2}Sw:Go']
gap_trig (readback): []
        '''

    new_pvs = {}
    new_pvs['gap'] = dict(setpoint='SR:C11-ID:G1{IVU20:1-Ax:Gap}-Mtr-SP',
                          readback='SR:C11-ID:G1{IVU20:1-Ax:Gap}-Mtr.RBV')
    new_pvs['gap_hilim'] = dict(readback=new_pvs['gap']['setpoint']+'.DRVH')
    new_pvs['gap_lolim'] = dict(readback=new_pvs['gap']['setpoint']+'.DRVL')
    new_pvs['gap_hinominal'] = dict(readback='SR:C11-ID:NomOpen-Sp')
    new_pvs['gap_lonominal'] = dict(readback='SR:C11-ID:NomClose-Sp')
    new_pvs['gap_ramping'] = dict(readback='SR:C11-ID:G1{IVU20:1-Ax:Gap}-Mtr.MOVN')
    new_pvs['gap_speed'] = dict(setpoint='SR:C11-ID:G1{IVU20:1}GapSpeed-SP',
                                readback='SR:C11-ID:G1{IVU20:1}GapSpeed-RB')
    new_pvs['gap_trig'] = dict(setpoint='SR:C11-ID:G1{IVU20:1-Ax:Gap}-Mtr-Go')

    tags = ["aphla.sys.SR"]

    for fld, d in new_pvs.items():
        for handle, pv in d.items():
            if handle == 'readback':
                hdl = 'get'
            elif handle == 'setpoint':
                hdl = 'put'
            else:
                raise ValueError()
            ap.apdata.updateDbPv(
                DBFILE, pv, elemName, fld, elemHandle=hdl, tags=tags, quiet=True)




    # Then purge old PV data from DB file
    sys.path.insert(0, '/home/yhidaka/git_repos/hlsqlite')
    import hlsqlite

    db = hlsqlite.SQLiteDatabase(filepath=DBFILE)

    lines = []
    for e in ap.getElements('*'):
        for fld in sorted(e.fields()):
            lines += ['{0}; {1}; setpoint; '.format(e.name, fld) + s
                      for s in e.pv(field=fld, handle='setpoint')]
            lines += ['{0}; {1}; readback; '.format(e.name, fld) + s
                      for s in e.pv(field=fld, handle='readback')]

        lines += sorted(e.pv()) # This includes unlinked (leftover) PVs as well.

    with open('before.txt', 'w') as f:
        f.write('\n'.join(lines))

    # Delete the old PVs that are no longer linked to any of the
    # element-field pairs
    table_name = 'pvs'
    db.deleteRows(table_name,
        condition_str='(elemName="ivu20g1c11c") AND (pv="SR:C11-ID:G1{IVU20:1-Mtr:2}Inp:Pos")')
    db.deleteRows(table_name,
        condition_str='(elemName="ivu20g1c11c") AND (pv="SR:C11-ID:G1{IVU20:1-Mtr:2}Pos.RBV")')
    db.deleteRows(table_name,
        condition_str='(elemName="ivu20g1c11c") AND (pv="SR:C11-ID:G1{IVU20:1-Mtr:2}Inp:Pos.DRVH")')
    db.deleteRows(table_name,
        condition_str='(elemName="ivu20g1c11c") AND (pv="SR:C11-ID:G1{IVU20:1-Mtr:2}Inp:Pos.DRVL")')
    db.deleteRows(table_name,
        condition_str='(elemName="ivu20g1c11c") AND (pv="SR:C11-ID:G1{IVU20:1-Mtr:2}S")')
    db.deleteRows(table_name,
        condition_str='(elemName="ivu20g1c11c") AND (pv="SR:C11-ID:G1{IVU20:1-Mtr:2}S:RB")')
    db.deleteRows(table_name,
        condition_str='(elemName="ivu20g1c11c") AND (pv="SR:C11-ID:G1{IVU20:1-Mtr:2}Sw:Go")')

    db.close()

    ap.machines.load('nsls2', 'SR')

    lines = []
    for e in ap.getElements('*'):
        for fld in sorted(e.fields()):
            lines += ['{0}; {1}; setpoint; '.format(e.name, fld) + s
                      for s in e.pv(field=fld, handle='setpoint')]
            lines += ['{0}; {1}; readback; '.format(e.name, fld) + s
                      for s in e.pv(field=fld, handle='readback')]

        lines += sorted(e.pv()) # This includes unlinked (leftover) PVs as well.

    with open('after.txt', 'w') as f:
        f.write('\n'.join(lines))

    # Manually check "before.txt" and "after.txt" such that the intended
    # PVs have been removed from the database, but nothing else has been changed.

#----------------------------------------------------------------------
def update_C17u_gap_PVs():
    """
    """

    idobj = ap.getElements('ivu21g1c17u')[0]

    elemName = idobj.name

    if False:

        for fld in sorted(idobj.fields()):
            if not fld.startswith('gap'):
                continue
            for handle in ['setpoint', 'readback']:
                print('{0} ({1}): {2}'.format(fld, handle, str(idobj.pv(field=fld, handle=handle))))

        '''
        Output before DB change:

ivu21g1c17u
gap (setpoint): ['SR:C17-ID:G1{IVU21:1-Mtr:2}Inp:Pos']
gap (readback): ['SR:C17-ID:G1{IVU21:1-LEnc}Gap']
gap_hilim (setpoint): []
gap_hilim (readback): ['SR:C17-ID:G1{IVU21:1-Mtr:2}Inp:Pos.DRVH']
gap_hinominal (setpoint): []
gap_hinominal (readback): ['SR:C17-1-ID:NomOpen-Sp']
gap_lolim (setpoint): []
gap_lolim (readback): ['SR:C17-ID:G1{IVU21:1-Mtr:2}Inp:Pos.DRVL']
gap_lonominal (setpoint): []
gap_lonominal (readback): ['SR:C17-1-ID:NomClose-Sp']
gap_ramping (setpoint): []
gap_ramping (readback): ['SR:C17-ID:G1{IVU21:1-Mtr:2}Pos.MOVN']
gap_speed (setpoint): ['SR:C17-ID:G1{IVU21:1-Mtr:2}S']
gap_speed (readback): ['SR:C17-ID:G1{IVU21:1-Mtr:2}S:RB']
gap_trig (setpoint): ['SR:C17-ID:G1{IVU21:1-Mtr:2}Sw:Go']
gap_trig (readback): []
        '''

    new_pvs = {}
    new_pvs['gap'] = dict(setpoint='SR:C17-ID:G1{IVU21:1-Ax:Gap}-Mtr-SP',
                          readback='SR:C17-ID:G1{IVU21:1-Ax:Gap}-Mtr.RBV')
    new_pvs['gap_hilim'] = dict(readback=new_pvs['gap']['setpoint']+'.DRVH')
    new_pvs['gap_lolim'] = dict(readback=new_pvs['gap']['setpoint']+'.DRVL')
    new_pvs['gap_hinominal'] = dict(readback='SR:C17-1-ID:NomOpen-Sp')
    new_pvs['gap_lonominal'] = dict(readback='SR:C17-1-ID:NomClose-Sp')
    new_pvs['gap_ramping'] = dict(readback='SR:C17-ID:G1{IVU21:1-Ax:Gap}-Mtr.MOVN')
    new_pvs['gap_speed'] = dict(setpoint='SR:C17-ID:G1{IVU21:1}GapSpeed-SP',
                                readback='SR:C17-ID:G1{IVU21:1}GapSpeed-RB')
    new_pvs['gap_trig'] = dict(setpoint='SR:C17-ID:G1{IVU21:1-Ax:Gap}-Mtr-Go')

    tags = ["aphla.sys.SR"]

    for fld, d in new_pvs.items():
        for handle, pv in d.items():
            if handle == 'readback':
                hdl = 'get'
            elif handle == 'setpoint':
                hdl = 'put'
            else:
                raise ValueError()
            ap.apdata.updateDbPv(
                DBFILE, pv, elemName, fld, elemHandle=hdl, tags=tags, quiet=True)




    # Then purge old PV data from DB file
    sys.path.insert(0, '/home/yhidaka/git_repos/hlsqlite')
    import hlsqlite

    db = hlsqlite.SQLiteDatabase(filepath=DBFILE)

    lines = []
    for e in ap.getElements('*'):
        for fld in sorted(e.fields()):
            lines += ['{0}; {1}; setpoint; '.format(e.name, fld) + s
                      for s in e.pv(field=fld, handle='setpoint')]
            lines += ['{0}; {1}; readback; '.format(e.name, fld) + s
                      for s in e.pv(field=fld, handle='readback')]

        lines += sorted(e.pv()) # This includes unlinked (leftover) PVs as well.

    with open('before.txt', 'w') as f:
        f.write('\n'.join(lines))

    # Delete the old PVs that are no longer linked to any of the
    # element-field pairs
    table_name = 'pvs'
    db.deleteRows(table_name,
        condition_str='(elemName="ivu21g1c17u") AND (pv="SR:C17-ID:G1{IVU21:1-Mtr:2}Inp:Pos")')
    db.deleteRows(table_name,
        condition_str='(elemName="ivu21g1c17u") AND (pv="SR:C17-ID:G1{IVU21:1-LEnc}Gap")')
    db.deleteRows(table_name,
        condition_str='(elemName="ivu21g1c17u") AND (pv="SR:C17-ID:G1{IVU21:1-Mtr:2}Inp:Pos.DRVH")')
    db.deleteRows(table_name,
        condition_str='(elemName="ivu21g1c17u") AND (pv="SR:C17-ID:G1{IVU21:1-Mtr:2}Inp:Pos.DRVL")')
    db.deleteRows(table_name,
        condition_str='(elemName="ivu21g1c17u") AND (pv="SR:C17-ID:G1{IVU21:1-Mtr:2}Pos.MOVN")')
    db.deleteRows(table_name,
        condition_str='(elemName="ivu21g1c17u") AND (pv="SR:C17-ID:G1{IVU21:1-Mtr:2}S")')
    db.deleteRows(table_name,
        condition_str='(elemName="ivu21g1c17u") AND (pv="SR:C17-ID:G1{IVU21:1-Mtr:2}S:RB")')
    db.deleteRows(table_name,
        condition_str='(elemName="ivu21g1c17u") AND (pv="SR:C17-ID:G1{IVU21:1-Mtr:2}Sw:Go")')

    db.close()

    ap.machines.load('nsls2', 'SR')

    lines = []
    for e in ap.getElements('*'):
        for fld in sorted(e.fields()):
            lines += ['{0}; {1}; setpoint; '.format(e.name, fld) + s
                      for s in e.pv(field=fld, handle='setpoint')]
            lines += ['{0}; {1}; readback; '.format(e.name, fld) + s
                      for s in e.pv(field=fld, handle='readback')]

        lines += sorted(e.pv()) # This includes unlinked (leftover) PVs as well.

    with open('after.txt', 'w') as f:
        f.write('\n'.join(lines))

    # Manually check "before.txt" and "after.txt" such that the intended
    # PVs have been removed from the database, but nothing else has been changed.

#----------------------------------------------------------------------
def update_C17d_gap_PVs():
    """
    """

    idobj = ap.getElements('ivu21g1c17d')[0]

    elemName = idobj.name

    if False:

        for fld in sorted(idobj.fields()):
            if not fld.startswith('gap'):
                continue
            for handle in ['setpoint', 'readback']:
                print('{0} ({1}): {2}'.format(fld, handle, str(idobj.pv(field=fld, handle=handle))))

        '''
        Output before DB change:

ivu21g1c17d
gap (setpoint): ['SR:C17-ID:G1{IVU21:2-Mtr:2}Inp:Pos']
gap (readback): ['SR:C17-ID:G1{IVU21:2-LEnc}Gap']
gap_hilim (setpoint): []
gap_hilim (readback): ['SR:C17-ID:G1{IVU21:2-Mtr:2}Inp:Pos.DRVH']
gap_hinominal (setpoint): []
gap_hinominal (readback): ['SR:C17-2-ID:NomOpen-Sp']
gap_lolim (setpoint): []
gap_lolim (readback): ['SR:C17-ID:G1{IVU21:2-Mtr:2}Inp:Pos.DRVL']
gap_lonominal (setpoint): []
gap_lonominal (readback): ['SR:C17-2-ID:NomClose-Sp']
gap_ramping (setpoint): []
gap_ramping (readback): ['SR:C17-ID:G1{IVU21:2-Mtr:2}Pos.MOVN']
gap_speed (setpoint): ['SR:C17-ID:G1{IVU21:2-Mtr:2}S']
gap_speed (readback): ['SR:C17-ID:G1{IVU21:2-Mtr:2}S:RB']
gap_trig (setpoint): ['SR:C17-ID:G1{IVU21:2-Mtr:2}Sw:Go']
gap_trig (readback): []
        '''

    new_pvs = {}
    new_pvs['gap'] = dict(setpoint='SR:C17-ID:G1{IVU21:2-Ax:Gap}-Mtr-SP',
                          readback='SR:C17-ID:G1{IVU21:2-Ax:Gap}-Mtr.RBV')
    new_pvs['gap_hilim'] = dict(readback=new_pvs['gap']['setpoint']+'.DRVH')
    new_pvs['gap_lolim'] = dict(readback=new_pvs['gap']['setpoint']+'.DRVL')
    new_pvs['gap_hinominal'] = dict(readback='SR:C17-2-ID:NomOpen-Sp')
    new_pvs['gap_lonominal'] = dict(readback='SR:C17-2-ID:NomClose-Sp')
    new_pvs['gap_ramping'] = dict(readback='SR:C17-ID:G1{IVU21:2-Ax:Gap}-Mtr.MOVN')
    new_pvs['gap_speed'] = dict(setpoint='SR:C17-ID:G1{IVU21:2}GapSpeed-SP',
                                readback='SR:C17-ID:G1{IVU21:2}GapSpeed-RB')
    new_pvs['gap_trig'] = dict(setpoint='SR:C17-ID:G1{IVU21:2-Ax:Gap}-Mtr-Go')

    tags = ["aphla.sys.SR"]

    for fld, d in new_pvs.items():
        for handle, pv in d.items():
            if handle == 'readback':
                hdl = 'get'
            elif handle == 'setpoint':
                hdl = 'put'
            else:
                raise ValueError()
            ap.apdata.updateDbPv(
                DBFILE, pv, elemName, fld, elemHandle=hdl, tags=tags, quiet=True)




    # Then purge old PV data from DB file
    sys.path.insert(0, '/home/yhidaka/git_repos/hlsqlite')
    import hlsqlite

    db = hlsqlite.SQLiteDatabase(filepath=DBFILE)

    lines = []
    for e in ap.getElements('*'):
        for fld in sorted(e.fields()):
            lines += ['{0}; {1}; setpoint; '.format(e.name, fld) + s
                      for s in e.pv(field=fld, handle='setpoint')]
            lines += ['{0}; {1}; readback; '.format(e.name, fld) + s
                      for s in e.pv(field=fld, handle='readback')]

        lines += sorted(e.pv()) # This includes unlinked (leftover) PVs as well.

    with open('before.txt', 'w') as f:
        f.write('\n'.join(lines))

    # Delete the old PVs that are no longer linked to any of the
    # element-field pairs
    table_name = 'pvs'
    db.deleteRows(table_name,
        condition_str='(elemName="ivu21g1c17d") AND (pv="SR:C17-ID:G1{IVU21:2-Mtr:2}Inp:Pos")')
    db.deleteRows(table_name,
        condition_str='(elemName="ivu21g1c17d") AND (pv="SR:C17-ID:G1{IVU21:2-LEnc}Gap")')
    db.deleteRows(table_name,
        condition_str='(elemName="ivu21g1c17d") AND (pv="SR:C17-ID:G1{IVU21:2-Mtr:2}Inp:Pos.DRVH")')
    db.deleteRows(table_name,
        condition_str='(elemName="ivu21g1c17d") AND (pv="SR:C17-ID:G1{IVU21:2-Mtr:2}Inp:Pos.DRVL")')
    db.deleteRows(table_name,
        condition_str='(elemName="ivu21g1c17d") AND (pv="SR:C17-ID:G1{IVU21:2-Mtr:2}Pos.MOVN")')
    db.deleteRows(table_name,
        condition_str='(elemName="ivu21g1c17d") AND (pv="SR:C17-ID:G1{IVU21:2-Mtr:2}S")')
    db.deleteRows(table_name,
        condition_str='(elemName="ivu21g1c17d") AND (pv="SR:C17-ID:G1{IVU21:2-Mtr:2}S:RB")')
    db.deleteRows(table_name,
        condition_str='(elemName="ivu21g1c17d") AND (pv="SR:C17-ID:G1{IVU21:2-Mtr:2}Sw:Go")')

    db.close()

    ap.machines.load('nsls2', 'SR')

    lines = []
    for e in ap.getElements('*'):
        for fld in sorted(e.fields()):
            lines += ['{0}; {1}; setpoint; '.format(e.name, fld) + s
                      for s in e.pv(field=fld, handle='setpoint')]
            lines += ['{0}; {1}; readback; '.format(e.name, fld) + s
                      for s in e.pv(field=fld, handle='readback')]

        lines += sorted(e.pv()) # This includes unlinked (leftover) PVs as well.

    with open('after.txt', 'w') as f:
        f.write('\n'.join(lines))

    # Manually check "before.txt" and "after.txt" such that the intended
    # PVs have been removed from the database, but nothing else has been changed.

#----------------------------------------------------------------------
def update_C03_05_11_17_gap_unitconvs():
    """
    """

    if False: # Check where C03, C05, C11, C17-1, C17-2 ID unit conversion data
              # need to be updated.

        affected_id_names = [
            'ivu20g1c03c', 'ivu21g1c05d', 'ivu20g1c11c', 'ivu21g1c17u', 'ivu21g1c17d']

        fold = h5py.File(UNITCONV_FILE, 'r')
        gold = fold['UnitConversion']
        for k, v in gold.items():
            for ak, av in v.attrs.items():
                if ak == 'elements':
                    elem_names = av.tolist()
                    for _affec_name in affected_id_names:
                        if _affec_name in elem_names:
                            print(k)
                            break
        fold.close()

        ''' Output: (* denotes gap-related unit conversion fields)
ID_cch0_v1
ID_cch0_v2
ID_cch0rb1_v1
ID_cch0rb1_v2
ID_cch1_v1
ID_cch1_v2
ID_cch1rb1_v1
ID_cch1rb1_v2
ID_cch2_v1
ID_cch2_v2
ID_cch2rb1_v1
ID_cch2rb1_v2
ID_cch3_v1
ID_cch3_v2
ID_cch3rb1_v1
ID_cch3rb1_v2
ID_cch4_v1
ID_cch4_v2
ID_cch4rb1_v1
ID_cch4rb1_v2
ID_cch5_v1
ID_cch5_v2
ID_cch5rb1_v1
ID_cch5rb1_v2
ID_cch6_v2
ID_cch7_v2
ID_cch8_v2
ID_cch9_v2
* ID_gap_rb_mm_to_mm
* ivu_gap_hilim_type0
* ivu_gap_hinominal_type0
* ivu_gap_lolim_type0
* ivu_gap_lonominal_type0
* ivu_gap_speed_type0
ivu_orbff0_m0_I_type0
ivu_orbff0_m0_I_type2
* ivu_orbff0_m0_gap_type0
ivu_orbff1_m0_I_type0
ivu_orbff1_m0_I_type2
* ivu_orbff1_m0_gap_type0
ivu_orbff2_m0_I_type0
ivu_orbff2_m0_I_type2
* ivu_orbff2_m0_gap_type0
ivu_orbff3_m0_I_type0
ivu_orbff3_m0_I_type2
* ivu_orbff3_m0_gap_type0
ivu_orbff4_m0_I_type0
ivu_orbff4_m0_I_type2
* ivu_orbff4_m0_gap_type0
ivu_orbff5_m0_I_type0
ivu_orbff5_m0_I_type2
* ivu_orbff5_m0_gap_type0
'''


    if False: #True: # This section can only run once, as HDF5 file does not
                     # allow overwrite of existing datasets

        kw = dict(compression='gzip')

        _temp_unitconv_file = UNITCONV_FILE + '.tmp'

        fnew = h5py.File(_temp_unitconv_file, 'w')
        fold = h5py.File(UNITCONV_FILE, 'r')

        delete_ds_names = [
            'ID_gap_rb_mm_to_mm', 'ivu_gap_hilim_type0', 'ivu_gap_lolim_type0',
            'ivu_gap_hinominal_type0', 'ivu_gap_lonominal_type0', 'ivu_gap_speed_type0',
            'ivu_orbff0_m0_gap_type0', 'ivu_orbff1_m0_gap_type0',
            'ivu_orbff2_m0_gap_type0', 'ivu_orbff3_m0_gap_type0',
            'ivu_orbff4_m0_gap_type0', 'ivu_orbff5_m0_gap_type0',
        ]

        excl_ds_names = \
            ['ID_gap_rb_um_to_mm', 'ID_gap_sp_um_to_mm',
             'ivu_gap_hilim_type1', 'ivu_gap_lolim_type1',
             'ivu_gap_hinominal_type1', 'ivu_gap_lonominal_type1',
             'ivu_gap_speed_type1',
             'ivu_orbff0_m0_gap_type2', 'ivu_orbff1_m0_gap_type2',
             'ivu_orbff2_m0_gap_type2', 'ivu_orbff3_m0_gap_type2',
             'ivu_orbff4_m0_gap_type2', 'ivu_orbff5_m0_gap_type2',
             ]

        # First copy existing unit conversion data
        gold = fold['UnitConversion']
        gnew = fnew.create_group('UnitConversion')
        for k, v in gold.items():

            if k in delete_ds_names:
                continue

            if False: # This will end up with bigger file size
                d = gnew.create_dataset(k, data=v.value, **kw)
            else: # This will end up with smaller file size, so use this one!
                gnew[k] = v.value
                d = gnew[k]

            if k in excl_ds_names:
                continue
            else:
                for ak, av in v.attrs.items():
                    put_h5py_attr(d, ak, av)

        # Updating to new unit conversions
        for k in ['ID_gap_rb_um_to_mm', 'ID_gap_sp_um_to_mm']:
            v = gold[k]
            d = gnew[k]
            #
            for ak, av in v.attrs.items():
                if ak == 'elements':
                    elem_names = av.tolist()
                    elem_names += ['ivu20g1c03c', 'ivu21g1c05d', 'ivu20g1c11c',
                                   'ivu21g1c17u', 'ivu21g1c17d']
                    av = np.array(elem_names)
                put_h5py_attr(d, ak, av)
        #
        for k in ['ivu_gap_hilim_type1', 'ivu_gap_lolim_type1',
                  'ivu_gap_hinominal_type1', 'ivu_gap_lonominal_type1',
                  'ivu_gap_speed_type1',
                  'ivu_orbff0_m0_gap_type2', 'ivu_orbff1_m0_gap_type2',
                  'ivu_orbff2_m0_gap_type2', 'ivu_orbff3_m0_gap_type2',
                  'ivu_orbff4_m0_gap_type2', 'ivu_orbff5_m0_gap_type2']:
            v = gold[k]
            d = gnew[k]
            #
            for ak, av in v.attrs.items():
                if ak == 'elements':
                    elem_names = av.tolist()
                    elem_names += ['ivu20g1c03c', 'ivu21g1c05d', 'ivu20g1c11c',
                                   'ivu21g1c17u', 'ivu21g1c17d']
                    av = np.array(elem_names)
                put_h5py_attr(d, ak, av)

        fold.close()
        fnew.close()

        # Make sure the new file has the correct permission
        os.chmod(_temp_unitconv_file, 0o755)

        shutil.move(_temp_unitconv_file, UNITCONV_FILE)

    #
    # Test if the unit conversion works
    #

    ap.machines.loadfast('nsls2', 'SR')

    for e in sorted(
        ap.getElements('ivu*c03*') + ap.getElements('ivu*c05*') +
        ap.getElements('ivu*c11*') + ap.getElements('ivu*c17*')):
        print('## {0} ##'.format(e.name))

        for hdl_list, fld_list in [
            (['readback', 'setpoint'], ['gap', 'gap_speed']),
            (['readback',], ['gap_hilim', 'gap_lolim',
                             'gap_hinominal', 'gap_lonominal',]),
            (['setpoint',], ['orbff{0:d}_m0_gap'.format(iCh) for iCh in range(6)]),
            ]:

            for fld in fld_list:
                for hdl in hdl_list:
                    print('{0}/{1}: {2}, {3}'.format(
                        fld, hdl, e.getUnit(fld, handle=hdl, unitsys=None),
                        e.getUnit(fld, handle=hdl, unitsys='phy')))

                    val_1mm_in_mm = 1.0
                    val_1mm_in_um = 1e3
                    np.testing.assert_almost_equal(
                        val_1mm_in_mm,
                        e.convertUnit(fld, val_1mm_in_um, None, 'phy', handle=hdl),
                        decimal=12
                    )

    plt.show()

#----------------------------------------------------------------------
def switch_C08_C11_C12_ID_orbcor_PVs_to_new_BNL_PSI_PVs():
    """"""

    tags = ['aphla.sys.SR']

    for elemName, new_pv_prefix, ch_inds in [
        ('dw100g1c08u', 'SR:C07-MG{PS:DW1_ID08}', list(range(6))),
        ('dw100g1c08d', 'SR:C07-MG{PS:DW2_ID08}', list(range(6))),
        ('ivu20g1c11c', 'SR:C10-MG{PS:CHX_ID11}', list(range(6))),
        ('ivu23g1c12d', 'SR:C11-MG{PS:SMI_ID12}', list(range(6))),
        ]:
        for iCh in ch_inds:

            # For setpoint fields: "cch0", "cch1", "cch2", ...
            fld, hdl = 'cch{0:d}'.format(iCh), 'put'
            pv = new_pv_prefix + ('U%d-I-SP' % (iCh + 1))
            ap.apdata.updateDbPv(DBFILE, pv, elemName, fld,
                                 elemHandle=hdl, tags=tags, quiet=True, epsilon=0.05)

            # For readback fields: "cch0", "cch1", "cch2", ...
            fld, hdl = 'cch{0:d}'.format(iCh), 'get'
            pv = new_pv_prefix + ('U%dLoop-I' % (iCh + 1))
            ap.apdata.updateDbPv(DBFILE, pv, elemName, fld,
                                 elemHandle=hdl, tags=tags, quiet=True, epsilon=0.0)

            # For actual readback fields: "cch0rb1", "cch1rb1", "cch2rb1", ...
            fld, hdl = 'cch{0:d}rb1'.format(iCh), 'get'
            pv = new_pv_prefix + ('U%d-I-I' % (iCh + 1))
            ap.apdata.updateDbPv(DBFILE, pv, elemName, fld,
                                 elemHandle=hdl, tags=tags, quiet=True, epsilon=0.0)

            # For the "cch" readback array PV
            fld, hdl = 'cch[{0:d}]'.format(iCh), 'get'
            pv = new_pv_prefix + ('U%dLoop-I' % (iCh + 1))
            ap.apdata.updateDbPv(DBFILE, pv, elemName, fld,
                                 elemHandle=hdl, tags=tags, quiet=True, epsilon=0.0)

            # For setpoint fields for Orbit Feedforward output:
            #     "orbff0_output", "orbff1_output", "orbff2_output", ...
            fld, hdl = 'orbff{0:d}_output'.format(iCh), 'put'
            pv = new_pv_prefix + ('U%d-I-SP' % (iCh + 1))
            ap.apdata.updateDbPv(DBFILE, pv, elemName, fld,
                                 elemHandle=hdl, tags=tags, quiet=True, epsilon=0.05)

#----------------------------------------------------------------------
def purge_old_ID_orb_cor_PVs_for_C08_11_12_IDs():
    """"""

    sys.path.insert(0, '/home/yhidaka/git_repos/hlsqlite')
    import hlsqlite

    db = hlsqlite.SQLiteDatabase(filepath=DBFILE)

    lines = []
    for e in ap.getElements('*'):
        for fld in sorted(e.fields()):
            lines += ['{0}; {1}; setpoint; '.format(e.name, fld) + s
                      for s in e.pv(field=fld, handle='setpoint')]
            lines += ['{0}; {1}; readback; '.format(e.name, fld) + s
                      for s in e.pv(field=fld, handle='readback')]

        lines += sorted(e.pv()) # This includes unlinked (leftover) PVs as well.

    with open('before.txt', 'w') as f:
        f.write('\n'.join(lines))


    if False: # interactive testing section
        table_name = 'pvs'
        column_name_list = ['elemName', 'elemField']
        pprint.pprint(
            db.getColumnDataFromTable(
                table_name, column_name_list=column_name_list,
                condition_str='elemName="dw100g1c08u"'))

        db.getColumnNames('pvs')

        table_name = 'pvs'
        column_name_list = ['id', 'elemField', 'pv']
        out = db.getColumnDataFromTable(
                table_name, column_name_list=column_name_list,
                condition_str='(elemName="dw100g1c08u") AND (pv LIKE "%Loop-I")')
        pprint.pprint(list(zip(*out)))

        table_name = 'pvs'
        column_name_list = ['id', 'elemField', 'pv']
        out = db.getColumnDataFromTable(
                table_name, column_name_list=column_name_list,
                condition_str='(elemName="dw100g1c08u") AND (pv="SR:C08-ID:G1{DW100:1}MPS:ch0:readback")')
        pprint.pprint(list(zip(*out)))


        table_name = 'pvs'
        column_name_list = ['id', 'elemField', 'pv']
        out = db.getColumnDataFromTable(
                table_name, column_name_list=column_name_list,
                condition_str='(elemName="dw100g1c08u") AND (pv LIKE "%:readback")')
        pprint.pprint(list(zip(*out)))

        table_name = 'pvs'
        column_name_list = ['id', 'elemField', 'pv']
        out = db.getColumnDataFromTable(
                table_name, column_name_list=column_name_list,
                condition_str='(elemName="dw100g1c08u") AND (pv LIKE "%:setpoint")')
        pprint.pprint(list(zip(*out)))

        table_name = 'pvs'
        column_name_list = ['id', 'elemField', 'pv']
        out = db.getColumnDataFromTable(
                table_name, column_name_list=column_name_list,
                condition_str='(elemName="dw100g1c08u") AND (pv LIKE "%:current")')
        pprint.pprint(list(zip(*out)))

        table_name = 'pvs'
        column_name_list = ['id', 'elemField', 'pv']
        out = db.getColumnDataFromTable(
                table_name, column_name_list=column_name_list,
                condition_str='(elemName="dw100g1c08u") AND (pv LIKE "%:enable")')
        pprint.pprint(list(zip(*out)))



    # Delete the old PVs for ID-08-1 that are no longer linked to any of the
    # element-field pairs
    table_name = 'pvs'
    db.deleteRows(table_name, condition_str='(elemName="dw100g1c08u") AND (pv LIKE "%:setpoint")')
    db.deleteRows(table_name, condition_str='(elemName="dw100g1c08u") AND (pv LIKE "%:readback")')
    db.deleteRows(table_name, condition_str='(elemName="dw100g1c08u") AND (pv LIKE "%:current")')
    db.deleteRows(table_name, condition_str='(elemName="dw100g1c08u") AND (pv LIKE "%:enable")')

    # Delete the old PVs for ID-08-2 that are no longer linked to any of the
    # element-field pairs
    table_name = 'pvs'
    db.deleteRows(table_name, condition_str='(elemName="dw100g1c08d") AND (pv LIKE "%:setpoint")')
    db.deleteRows(table_name, condition_str='(elemName="dw100g1c08d") AND (pv LIKE "%:readback")')
    db.deleteRows(table_name, condition_str='(elemName="dw100g1c08d") AND (pv LIKE "%:current")')
    db.deleteRows(table_name, condition_str='(elemName="dw100g1c08d") AND (pv LIKE "%:enable")')

    # Delete the old PVs for ID-11 that are no longer linked to any of the
    # element-field pairs
    table_name = 'pvs'
    db.deleteRows(table_name, condition_str='(elemName="ivu20g1c11c") AND (pv LIKE "%:setpoint")')
    db.deleteRows(table_name, condition_str='(elemName="ivu20g1c11c") AND (pv LIKE "%:readback")')
    db.deleteRows(table_name, condition_str='(elemName="ivu20g1c11c") AND (pv LIKE "%:current")')
    db.deleteRows(table_name, condition_str='(elemName="ivu20g1c11c") AND (pv LIKE "%:enable")')

    # Delete the old PVs for ID-12 that are no longer linked to any of the
    # element-field pairs
    table_name = 'pvs'
    db.deleteRows(table_name, condition_str='(elemName="ivu23g1c12d") AND (pv LIKE "%:setpoint")')
    db.deleteRows(table_name, condition_str='(elemName="ivu23g1c12d") AND (pv LIKE "%:readback")')
    db.deleteRows(table_name, condition_str='(elemName="ivu23g1c12d") AND (pv LIKE "%:current")')
    db.deleteRows(table_name, condition_str='(elemName="ivu23g1c12d") AND (pv LIKE "%:enable")')

    db.close()

    ap.machines.load('nsls2', 'SR')

    lines = []
    for e in ap.getElements('*'):
        for fld in sorted(e.fields()):
            lines += ['{0}; {1}; setpoint; '.format(e.name, fld) + s
                      for s in e.pv(field=fld, handle='setpoint')]
            lines += ['{0}; {1}; readback; '.format(e.name, fld) + s
                      for s in e.pv(field=fld, handle='readback')]

        lines += sorted(e.pv()) # This includes unlinked (leftover) PVs as well.

    with open('after.txt', 'w') as f:
        f.write('\n'.join(lines))

    # Manually check "before.txt" and "after.txt" such that the intended
    # PVs have been removed from the database, but nothing else has been changed.

#----------------------------------------------------------------------
def fix_DW08_orbff_output_PVs():
    """"""

    us_id, ds_id = ap.getElements('dw100*c08*')

    if False:

        for idobj in [us_id, ds_id]:
            for fld in sorted([fld for fld in idobj.fields()
                               if fld.startswith('orbff') and fld.endswith('_output')]):
                print(idobj.name, fld, idobj.pv(field=fld), idobj.getEpsilon(fld))

        # The output with the database before I modified for C08 PSI PVs is the following:
        #
        #('dw100g1c08u', 'orbff0_output', ['SR:C08-ID:G1{DW100:1}MPS:ch0:setpoint'], 0.0)
        #('dw100g1c08u', 'orbff10_output', ['SR:C08-ID:G1{DW100:2}MPS:ch4:setpoint'], 0.0)
        #('dw100g1c08u', 'orbff11_output', ['SR:C08-ID:G1{DW100:2}MPS:ch5:setpoint'], 0.0)
        #('dw100g1c08u', 'orbff12_output', ['SR:C07-MG{PS:CH1B}I:Sp2_2-SP'], 0.0)
        #('dw100g1c08u', 'orbff13_output', ['SR:C08-MG{PS:CH1A}I:Sp2_2-SP'], 0.0)
        #('dw100g1c08u', 'orbff1_output', ['SR:C08-ID:G1{DW100:1}MPS:ch1:setpoint'], 0.0)
        #('dw100g1c08u', 'orbff2_output', ['SR:C08-ID:G1{DW100:1}MPS:ch2:setpoint'], 0.0)
        #('dw100g1c08u', 'orbff3_output', ['SR:C08-ID:G1{DW100:1}MPS:ch3:setpoint'], 0.0)
        #('dw100g1c08u', 'orbff4_output', ['SR:C08-ID:G1{DW100:1}MPS:ch4:setpoint'], 0.0)
        #('dw100g1c08u', 'orbff5_output', ['SR:C08-ID:G1{DW100:1}MPS:ch5:setpoint'], 0.0)
        #('dw100g1c08u', 'orbff6_output', ['SR:C08-ID:G1{DW100:2}MPS:ch0:setpoint'], 0.0)
        #('dw100g1c08u', 'orbff7_output', ['SR:C08-ID:G1{DW100:2}MPS:ch1:setpoint'], 0.0)
        #('dw100g1c08u', 'orbff8_output', ['SR:C08-ID:G1{DW100:2}MPS:ch2:setpoint'], 0.0)
        #('dw100g1c08u', 'orbff9_output', ['SR:C08-ID:G1{DW100:2}MPS:ch3:setpoint'], 0.0)
        #('dw100g1c08d', 'orbff0_output', ['SR:C08-ID:G1{DW100:1}MPS:ch0:setpoint'], 0.0)
        #('dw100g1c08d', 'orbff10_output', ['SR:C08-ID:G1{DW100:2}MPS:ch4:setpoint'], 0.0)
        #('dw100g1c08d', 'orbff11_output', ['SR:C08-ID:G1{DW100:2}MPS:ch5:setpoint'], 0.0)
        #('dw100g1c08d', 'orbff12_output', ['SR:C07-MG{PS:CH1B}I:Sp2_2-SP'], 0.0)
        #('dw100g1c08d', 'orbff13_output', ['SR:C08-MG{PS:CH1A}I:Sp2_2-SP'], 0.0)
        #('dw100g1c08d', 'orbff1_output', ['SR:C08-ID:G1{DW100:1}MPS:ch1:setpoint'], 0.0)
        #('dw100g1c08d', 'orbff2_output', ['SR:C08-ID:G1{DW100:1}MPS:ch2:setpoint'], 0.0)
        #('dw100g1c08d', 'orbff3_output', ['SR:C08-ID:G1{DW100:1}MPS:ch3:setpoint'], 0.0)
        #('dw100g1c08d', 'orbff4_output', ['SR:C08-ID:G1{DW100:1}MPS:ch4:setpoint'], 0.0)
        #('dw100g1c08d', 'orbff5_output', ['SR:C08-ID:G1{DW100:1}MPS:ch5:setpoint'], 0.0)
        #('dw100g1c08d', 'orbff6_output', ['SR:C08-ID:G1{DW100:2}MPS:ch0:setpoint'], 0.0)
        #('dw100g1c08d', 'orbff7_output', ['SR:C08-ID:G1{DW100:2}MPS:ch1:setpoint'], 0.0)
        #('dw100g1c08d', 'orbff8_output', ['SR:C08-ID:G1{DW100:2}MPS:ch2:setpoint'], 0.0)
        #('dw100g1c08d', 'orbff9_output', ['SR:C08-ID:G1{DW100:2}MPS:ch3:setpoint'], 0.0)

    tags = ['aphla.sys.SR']

    for idobj in [us_id, ds_id]:

        # For setpoint fields for Orbit Feedforward output:
        #     "orbff0_output", "orbff1_output", "orbff2_output", ...

        elemName = idobj.name
        hdl = 'put'

        pvsp_list = [us_id.pv(field='cch{0:d}'.format(_i), handle='setpoint')[0]
                     for _i in range(6)]
        for iCh, pv in zip(range(6), pvsp_list):
            fld = 'orbff{0:d}_output'.format(iCh)
            ap.apdata.updateDbPv(
                DBFILE, pv, elemName, fld,
                elemHandle=hdl, tags=tags, quiet=True, epsilon=0.0)

        pvsp_list = [ds_id.pv(field='cch{0:d}'.format(_i), handle='setpoint')[0]
                     for _i in range(6)]
        for iCh, pv in zip(range(6, 12), pvsp_list):
            fld = 'orbff{0:d}_output'.format(iCh)
            ap.apdata.updateDbPv(
                DBFILE, pv, elemName, fld,
                elemHandle=hdl, tags=tags, quiet=True, epsilon=0.0)

        pvsp_list = ['SR:C07-MG{PS:CH1B}I:Sp2_2-SP',
                     'SR:C08-MG{PS:CH1A}I:Sp2_2-SP']
        for iCh, pv in zip(range(12, 14), pvsp_list):
            fld = 'orbff{0:d}_output'.format(iCh)
            ap.apdata.updateDbPv(
                DBFILE, pv, elemName, fld,
                elemHandle=hdl, tags=tags, quiet=True, epsilon=0.0)

#----------------------------------------------------------------------
def switch_C08_11_12_ID_orbcor_PV_unitconv():
    """"""

    if False: # This section can only run once, as HDF5 file does not
                     # allow overwrite of existing datasets

        kw = dict(compression='gzip')

        _temp_unitconv_file = UNITCONV_FILE + '.tmp'

        fnew = h5py.File(_temp_unitconv_file, 'w')
        fold = h5py.File(UNITCONV_FILE, 'r')

        excl_ds_names = \
            ['ID_cch{0:d}_v1'.format(iCh) for iCh in range(6)] + \
            ['ID_cch{0:d}_v2'.format(iCh) for iCh in range(6)] + \
            ['ID_cch{0:d}rb1_v1'.format(iCh) for iCh in range(6)] + \
            ['ID_cch{0:d}rb1_v2'.format(iCh) for iCh in range(6)] + \
            ['ivu_orbff{0:d}_m0_I_type0'.format(iCh) for iCh in range(6)] + \
            ['ivu_orbff{0:d}_m0_I_type2'.format(iCh) for iCh in range(6)] + \
            ['dw_orbff{0:d}_m0_I_type0'.format(iCh) for iCh in range(12)]

        # First copy existing unit conversion data
        gold = fold['UnitConversion']
        gnew = fnew.create_group('UnitConversion')
        for k, v in gold.items():

            if False: # This will end up with bigger file size
                d = gnew.create_dataset(k, data=v.value, **kw)
            else: # This will end up with smaller file size, so use this one!
                gnew[k] = v.value
                d = gnew[k]

            if k in excl_ds_names:
                continue
            else:
                for ak, av in v.attrs.items():
                    put_h5py_attr(d, ak, av)

        # Updating to new unit conversions
        for iCh in range(6):

            k = 'ID_cch{0:d}_v1'.format(iCh)
            #
            v = gold[k]
            d = gnew[k]
            #
            for ak, av in v.attrs.items():
                if ak == 'elements':
                    elem_names = av.tolist()
                    elem_names.remove('ivu20g1c11c')
                    elem_names.remove('ivu23g1c12d')
                    elem_names.remove('dw100g1c08u')
                    elem_names.remove('dw100g1c08d')
                    av = np.array(elem_names)
                put_h5py_attr(d, ak, av)


            k = 'ID_cch{0:d}_v2'.format(iCh)
            #
            v = gold[k]
            d = gnew[k]
            #
            for ak, av in v.attrs.items():
                if ak == 'elements':
                    elem_names = av.tolist()
                    elem_names += ['ivu20g1c11c', 'ivu23g1c12d', 'dw100g1c08u', 'dw100g1c08d']
                    av = np.array(elem_names)
                put_h5py_attr(d, ak, av)



            k = 'ID_cch{0:d}rb1_v1'.format(iCh)
            #
            v = gold[k]
            d = gnew[k]
            #
            for ak, av in v.attrs.items():
                if ak == 'elements':
                    elem_names = av.tolist()
                    elem_names.remove('ivu20g1c11c')
                    elem_names.remove('ivu23g1c12d')
                    elem_names.remove('dw100g1c08u')
                    elem_names.remove('dw100g1c08d')
                    av = np.array(elem_names)
                put_h5py_attr(d, ak, av)


            k = 'ID_cch{0:d}rb1_v2'.format(iCh)
            #
            v = gold[k]
            d = gnew[k]
            #
            for ak, av in v.attrs.items():
                if ak == 'elements':
                    elem_names = av.tolist()
                    elem_names += ['ivu20g1c11c', 'ivu23g1c12d', 'dw100g1c08u', 'dw100g1c08d']
                    av = np.array(elem_names)
                put_h5py_attr(d, ak, av)



            k = 'ivu_orbff{0:d}_m0_I_type0'.format(iCh)
            #
            v = gold[k]
            d = gnew[k]
            #
            for ak, av in v.attrs.items():
                if ak == 'elements':
                    elem_names = av.tolist()
                    elem_names.remove('ivu20g1c11c')
                    elem_names.remove('ivu23g1c12d')
                    av = np.array(elem_names)
                put_h5py_attr(d, ak, av)


            k = 'ivu_orbff{0:d}_m0_I_type2'.format(iCh)
            #
            v = gold[k]
            d = gnew[k]
            #
            for ak, av in v.attrs.items():
                if ak == 'elements':
                    elem_names = av.tolist()
                    elem_names += ['ivu20g1c11c', 'ivu23g1c12d',]
                    av = np.array(elem_names)
                put_h5py_attr(d, ak, av)


        # Updating to new unit conversions
        for iCh in range(12):

            k = 'dw_orbff{0:d}_m0_I_type0'.format(iCh)
            #
            v = gold[k]
            d = gnew[k]
            #
            for ak, av in v.attrs.items():
                if ak == 'elements':
                    elem_names = av.tolist()
                    elem_names.remove('dw100g1c08u')
                    elem_names.remove('dw100g1c08d')
                    av = np.array(elem_names)
                put_h5py_attr(d, ak, av)


            k = 'dw_orbff{0:d}_m0_I_type1'.format(iCh)
            #
            if k not in list(gold):
                d = gnew.create_dataset(k, data=np.array([1.0, 0.0]), **kw)
                uc = {'_class_': 'polynomial', 'dst_unit': 'A', 'dst_unit_sys': 'phy',
                      'elements': ['dw100g1c08u', 'dw100g1c08d'],
                      'field': 'orbff{0:d}_m0_I'.format(iCh),
                      'handle': ['setpoint'],
                      'invertible': 1, 'src_unit': 'A', 'src_unit_sys': ''}
                for k2, v2 in uc.items(): put_h5py_attr(d, k2, v2)
            else:
                v = gold[k]
                d = gnew[k]
                #
                for ak, av in v.attrs.items():
                    if ak == 'elements':
                        elem_names = av.tolist()
                        elem_names += ['dw100g1c08u', 'dw100g1c08d']
                        av = np.array(elem_names)
                    put_h5py_attr(d, ak, av)


        fold.close()
        fnew.close()

        # Make sure the new file has the correct permission
        os.chmod(_temp_unitconv_file, 0o755)

        shutil.move(_temp_unitconv_file, UNITCONV_FILE)

    #
    # Test if the unit conversion works
    #

    ap.machines.loadfast('nsls2', 'SR')

    for e in sorted(
        ap.getElements('ivu*c11*') + ap.getElements('ivu*c12*') +
        ap.getElements('dw*c08*')):
        print('## {0} ##'.format(e.name))

        nCh = 6

        for hdl_list, fld_list in [
            (['readback', 'setpoint'], ['cch{0:d}'.format(iCh) for iCh in range(nCh)]),
            (['readback',], ['cch{0:d}rb1'.format(iCh) for iCh in range(nCh)]),
            ]:

            for fld in fld_list:
                for hdl in hdl_list:
                    print('{0}/{1}: {2}, {3}'.format(
                        fld, hdl, e.getUnit(fld, handle=hdl, unitsys=None),
                        e.getUnit(fld, handle=hdl, unitsys='phy')))

                    raw_val = 1.0
                    np.testing.assert_almost_equal(
                        raw_val,
                        e.convertUnit(fld, raw_val, None, 'phy', handle=hdl),
                        decimal=12
                    )

        if e.name.startswith('dw'):
            nCh = 6 + 6 + 2
        else:
            nCh = 6

        for hdl_list, fld_list in [
            (['setpoint',], ['orbff{0:d}_m0_I'.format(iCh) for iCh in range(nCh)]),
            ]:

            for fld in fld_list:
                for hdl in hdl_list:
                    print('{0}/{1}: {2}, {3}'.format(
                        fld, hdl, e.getUnit(fld, handle=hdl, unitsys=None),
                        e.getUnit(fld, handle=hdl, unitsys='phy')))

                    raw_val = 1.0
                    np.testing.assert_almost_equal(
                        raw_val,
                        e.convertUnit(fld, raw_val, None, 'phy', handle=hdl),
                        decimal=12
                    )


    plt.show()

#----------------------------------------------------------------------
def switch_C18_ID_orbcor_PVs_to_new_BNL_PSI_PVs():
    """"""

    tags = ['aphla.sys.SR']

    for elemName, new_pv_prefix, ch_inds in [
        ('dw100g1c18u', 'SR:C17-MG{PS:DW1_ID18}', list(range(6))),
        ('dw100g1c18d', 'SR:C17-MG{PS:DW2_ID18}', list(range(6))),
        ]:
        for iCh in ch_inds:

            # For setpoint fields: "cch0", "cch1", "cch2", ...
            fld, hdl = 'cch{0:d}'.format(iCh), 'put'
            pv = new_pv_prefix + ('U%d-I-SP' % (iCh + 1))
            ap.apdata.updateDbPv(DBFILE, pv, elemName, fld,
                                 elemHandle=hdl, tags=tags, quiet=True, epsilon=0.05)

            # For readback fields: "cch0", "cch1", "cch2", ...
            fld, hdl = 'cch{0:d}'.format(iCh), 'get'
            pv = new_pv_prefix + ('U%dLoop-I' % (iCh + 1))
            ap.apdata.updateDbPv(DBFILE, pv, elemName, fld,
                                 elemHandle=hdl, tags=tags, quiet=True, epsilon=0.0)

            # For actual readback fields: "cch0rb1", "cch1rb1", "cch2rb1", ...
            fld, hdl = 'cch{0:d}rb1'.format(iCh), 'get'
            pv = new_pv_prefix + ('U%d-I-I' % (iCh + 1))
            ap.apdata.updateDbPv(DBFILE, pv, elemName, fld,
                                 elemHandle=hdl, tags=tags, quiet=True, epsilon=0.0)

            # For the "cch" readback array PV
            fld, hdl = 'cch[{0:d}]'.format(iCh), 'get'
            pv = new_pv_prefix + ('U%dLoop-I' % (iCh + 1))
            ap.apdata.updateDbPv(DBFILE, pv, elemName, fld,
                                 elemHandle=hdl, tags=tags, quiet=True, epsilon=0.0)

            # For setpoint fields for Orbit Feedforward output:
            #     "orbff0_output", "orbff1_output", "orbff2_output", ...
            fld, hdl = 'orbff{0:d}_output'.format(iCh), 'put'
            pv = new_pv_prefix + ('U%d-I-SP' % (iCh + 1))
            ap.apdata.updateDbPv(DBFILE, pv, elemName, fld,
                                 elemHandle=hdl, tags=tags, quiet=True, epsilon=0.05)

#----------------------------------------------------------------------
def fix_DW18_orbff_output_PVs():
    """"""

    us_id, ds_id = ap.getElements('dw100*c18*')

    if False:

        # NOTE: I should use the for-loop below, instead of this one, as the one
        #       below sorts the print more nicely
        for idobj in [us_id, ds_id]:
            for fld in sorted([fld for fld in idobj.fields()
                               if fld.startswith('orbff') and fld.endswith('_output')]):
                print(idobj.name, fld, idobj.pv(field=fld), idobj.getEpsilon(fld))

        # The output with the database before I modified for C18 PSI PVs is the following:
        #
        #dw100g1c18u orbff0_output ['SR:C17-MG{PS:DW1_ID18}U1-I-SP'] 0.05
        #dw100g1c18u orbff10_output ['SR:C18-ID:G1{DW100:2}MPS:ch4:setpoint'] 0.0
        #dw100g1c18u orbff11_output ['SR:C18-ID:G1{DW100:2}MPS:ch5:setpoint'] 0.0
        #dw100g1c18u orbff12_output ['SR:C17-MG{PS:CH1B}I:Sp2_2-SP'] 0.0
        #dw100g1c18u orbff13_output ['SR:C18-MG{PS:CH1A}I:Sp2_2-SP'] 0.0
        #dw100g1c18u orbff1_output ['SR:C17-MG{PS:DW1_ID18}U2-I-SP'] 0.05
        #dw100g1c18u orbff2_output ['SR:C17-MG{PS:DW1_ID18}U3-I-SP'] 0.05
        #dw100g1c18u orbff3_output ['SR:C17-MG{PS:DW1_ID18}U4-I-SP'] 0.05
        #dw100g1c18u orbff4_output ['SR:C17-MG{PS:DW1_ID18}U5-I-SP'] 0.05
        #dw100g1c18u orbff5_output ['SR:C17-MG{PS:DW1_ID18}U6-I-SP'] 0.05
        #dw100g1c18u orbff6_output ['SR:C18-ID:G1{DW100:2}MPS:ch0:setpoint'] 0.0
        #dw100g1c18u orbff7_output ['SR:C18-ID:G1{DW100:2}MPS:ch1:setpoint'] 0.0
        #dw100g1c18u orbff8_output ['SR:C18-ID:G1{DW100:2}MPS:ch2:setpoint'] 0.0
        #dw100g1c18u orbff9_output ['SR:C18-ID:G1{DW100:2}MPS:ch3:setpoint'] 0.0
        #dw100g1c18d orbff0_output ['SR:C17-MG{PS:DW2_ID18}U1-I-SP'] 0.05
        #dw100g1c18d orbff10_output ['SR:C18-ID:G1{DW100:2}MPS:ch4:setpoint'] 0.0
        #dw100g1c18d orbff11_output ['SR:C18-ID:G1{DW100:2}MPS:ch5:setpoint'] 0.0
        #dw100g1c18d orbff12_output ['SR:C17-MG{PS:CH1B}I:Sp2_2-SP'] 0.0
        #dw100g1c18d orbff13_output ['SR:C18-MG{PS:CH1A}I:Sp2_2-SP'] 0.0
        #dw100g1c18d orbff1_output ['SR:C17-MG{PS:DW2_ID18}U2-I-SP'] 0.05
        #dw100g1c18d orbff2_output ['SR:C17-MG{PS:DW2_ID18}U3-I-SP'] 0.05
        #dw100g1c18d orbff3_output ['SR:C17-MG{PS:DW2_ID18}U4-I-SP'] 0.05
        #dw100g1c18d orbff4_output ['SR:C17-MG{PS:DW2_ID18}U5-I-SP'] 0.05
        #dw100g1c18d orbff5_output ['SR:C17-MG{PS:DW2_ID18}U6-I-SP'] 0.05
        #dw100g1c18d orbff6_output ['SR:C18-ID:G1{DW100:2}MPS:ch0:setpoint'] 0.0
        #dw100g1c18d orbff7_output ['SR:C18-ID:G1{DW100:2}MPS:ch1:setpoint'] 0.0
        #dw100g1c18d orbff8_output ['SR:C18-ID:G1{DW100:2}MPS:ch2:setpoint'] 0.0
        #dw100g1c18d orbff9_output ['SR:C18-ID:G1{DW100:2}MPS:ch3:setpoint'] 0.0

        for idobj in [us_id, ds_id]:
            fld_list = [f'orbff{i:d}_output' for i in range(14)]
            assert np.all(np.sort(fld_list) == np.sort(
                [fld for fld in idobj.fields()
                 if fld.startswith('orbff') and fld.endswith('_output')]))
            for fld in fld_list:
                print(idobj.name, fld, idobj.pv(field=fld), idobj.getEpsilon(fld))
        # The output with the database after I modified for C18 PSI PVs is the following:
        #
        #dw100g1c18u orbff0_output ['SR:C17-MG{PS:DW1_ID18}U1-I-SP'] 0.0
        #dw100g1c18u orbff1_output ['SR:C17-MG{PS:DW1_ID18}U2-I-SP'] 0.0
        #dw100g1c18u orbff2_output ['SR:C17-MG{PS:DW1_ID18}U3-I-SP'] 0.0
        #dw100g1c18u orbff3_output ['SR:C17-MG{PS:DW1_ID18}U4-I-SP'] 0.0
        #dw100g1c18u orbff4_output ['SR:C17-MG{PS:DW1_ID18}U5-I-SP'] 0.0
        #dw100g1c18u orbff5_output ['SR:C17-MG{PS:DW1_ID18}U6-I-SP'] 0.0
        #dw100g1c18u orbff6_output ['SR:C17-MG{PS:DW2_ID18}U1-I-SP'] 0.0
        #dw100g1c18u orbff7_output ['SR:C17-MG{PS:DW2_ID18}U2-I-SP'] 0.0
        #dw100g1c18u orbff8_output ['SR:C17-MG{PS:DW2_ID18}U3-I-SP'] 0.0
        #dw100g1c18u orbff9_output ['SR:C17-MG{PS:DW2_ID18}U4-I-SP'] 0.0
        #dw100g1c18u orbff10_output ['SR:C17-MG{PS:DW2_ID18}U5-I-SP'] 0.0
        #dw100g1c18u orbff11_output ['SR:C17-MG{PS:DW2_ID18}U6-I-SP'] 0.0
        #dw100g1c18u orbff12_output ['SR:C17-MG{PS:CH1B}I:Sp2_2-SP'] 0.0
        #dw100g1c18u orbff13_output ['SR:C18-MG{PS:CH1A}I:Sp2_2-SP'] 0.0
        #dw100g1c18d orbff0_output ['SR:C17-MG{PS:DW1_ID18}U1-I-SP'] 0.0
        #dw100g1c18d orbff1_output ['SR:C17-MG{PS:DW1_ID18}U2-I-SP'] 0.0
        #dw100g1c18d orbff2_output ['SR:C17-MG{PS:DW1_ID18}U3-I-SP'] 0.0
        #dw100g1c18d orbff3_output ['SR:C17-MG{PS:DW1_ID18}U4-I-SP'] 0.0
        #dw100g1c18d orbff4_output ['SR:C17-MG{PS:DW1_ID18}U5-I-SP'] 0.0
        #dw100g1c18d orbff5_output ['SR:C17-MG{PS:DW1_ID18}U6-I-SP'] 0.0
        #dw100g1c18d orbff6_output ['SR:C17-MG{PS:DW2_ID18}U1-I-SP'] 0.0
        #dw100g1c18d orbff7_output ['SR:C17-MG{PS:DW2_ID18}U2-I-SP'] 0.0
        #dw100g1c18d orbff8_output ['SR:C17-MG{PS:DW2_ID18}U3-I-SP'] 0.0
        #dw100g1c18d orbff9_output ['SR:C17-MG{PS:DW2_ID18}U4-I-SP'] 0.0
        #dw100g1c18d orbff10_output ['SR:C17-MG{PS:DW2_ID18}U5-I-SP'] 0.0
        #dw100g1c18d orbff11_output ['SR:C17-MG{PS:DW2_ID18}U6-I-SP'] 0.0
        #dw100g1c18d orbff12_output ['SR:C17-MG{PS:CH1B}I:Sp2_2-SP'] 0.0
        #dw100g1c18d orbff13_output ['SR:C18-MG{PS:CH1A}I:Sp2_2-SP'] 0.0

    tags = ['aphla.sys.SR']

    for idobj in [us_id, ds_id]:

        # For setpoint fields for Orbit Feedforward output:
        #     "orbff0_output", "orbff1_output", "orbff2_output", ...

        elemName = idobj.name
        hdl = 'put'

        pvsp_list = [us_id.pv(field='cch{0:d}'.format(_i), handle='setpoint')[0]
                     for _i in range(6)]
        for iCh, pv in zip(range(6), pvsp_list):
            fld = 'orbff{0:d}_output'.format(iCh)
            ap.apdata.updateDbPv(
                DBFILE, pv, elemName, fld,
                elemHandle=hdl, tags=tags, quiet=True, epsilon=0.0)

        pvsp_list = [ds_id.pv(field='cch{0:d}'.format(_i), handle='setpoint')[0]
                     for _i in range(6)]
        for iCh, pv in zip(range(6, 12), pvsp_list):
            fld = 'orbff{0:d}_output'.format(iCh)
            ap.apdata.updateDbPv(
                DBFILE, pv, elemName, fld,
                elemHandle=hdl, tags=tags, quiet=True, epsilon=0.0)

        pvsp_list = ['SR:C17-MG{PS:CH1B}I:Sp2_2-SP',
                     'SR:C18-MG{PS:CH1A}I:Sp2_2-SP']
        for iCh, pv in zip(range(12, 14), pvsp_list):
            fld = 'orbff{0:d}_output'.format(iCh)
            ap.apdata.updateDbPv(
                DBFILE, pv, elemName, fld,
                elemHandle=hdl, tags=tags, quiet=True, epsilon=0.0)

#----------------------------------------------------------------------
def purge_old_ID_orb_cor_PVs_for_C18_IDs():
    """"""

    sys.path.insert(0, '/nfs/yhidaka/git_repos/hlsqlite')
    import hlsqlite

    db = hlsqlite.SQLiteDatabase(filepath=DBFILE)

    lines = []
    for e in ap.getElements('*'):
        for fld in sorted(e.fields()):
            lines += ['{0}; {1}; setpoint; '.format(e.name, fld) + s
                      for s in e.pv(field=fld, handle='setpoint')]
            lines += ['{0}; {1}; readback; '.format(e.name, fld) + s
                      for s in e.pv(field=fld, handle='readback')]

        lines += sorted(e.pv()) # This includes unlinked (leftover) PVs as well.

    with open('before.txt', 'w') as f:
        f.write('\n'.join(lines))

        #with open('intermediate.txt', 'w') as f:
            #f.write('\n'.join(lines))


    if False: # interactive testing section
        table_name = 'pvs'
        column_name_list = ['elemName', 'elemField']
        pprint.pprint(
            db.getColumnDataFromTable(
                table_name, column_name_list=column_name_list,
                condition_str='elemName="dw100g1c18u"'))

        db.getColumnNames('pvs')

        table_name = 'pvs'
        column_name_list = ['id', 'elemField', 'pv']
        out = db.getColumnDataFromTable(
                table_name, column_name_list=column_name_list,
                condition_str='(elemName="dw100g1c18u") AND (pv LIKE "%Loop-I")')
        pprint.pprint(list(zip(*out)))

        table_name = 'pvs'
        column_name_list = ['id', 'elemField', 'pv']
        out = db.getColumnDataFromTable(
                table_name, column_name_list=column_name_list,
                condition_str='(elemName="dw100g1c18u") AND (pv="SR:C18-ID:G1{DW100:1}MPS:ch0:readback")')
        pprint.pprint(list(zip(*out)))


        table_name = 'pvs'
        column_name_list = ['id', 'elemField', 'pv']
        out = db.getColumnDataFromTable(
                table_name, column_name_list=column_name_list,
                condition_str='(elemName="dw100g1c18u") AND (pv LIKE "%:readback")')
        pprint.pprint(list(zip(*out)))

        table_name = 'pvs'
        column_name_list = ['id', 'elemField', 'pv']
        out = db.getColumnDataFromTable(
                table_name, column_name_list=column_name_list,
                condition_str='(elemName="dw100g1c18u") AND (pv LIKE "%:setpoint")')
        pprint.pprint(list(zip(*out)))

        table_name = 'pvs'
        column_name_list = ['id', 'elemField', 'pv']
        out = db.getColumnDataFromTable(
                table_name, column_name_list=column_name_list,
                condition_str='(elemName="dw100g1c18u") AND (pv LIKE "%:current")')
        pprint.pprint(list(zip(*out)))

        table_name = 'pvs'
        column_name_list = ['id', 'elemField', 'pv']
        out = db.getColumnDataFromTable(
                table_name, column_name_list=column_name_list,
                condition_str='(elemName="dw100g1c18u") AND (pv LIKE "%:enable")')
        pprint.pprint(list(zip(*out)))



    # Delete the old PVs for ID-18-1 that are no longer linked to any of the
    # element-field pairs
    table_name = 'pvs'
    db.deleteRows(table_name, condition_str='(elemName="dw100g1c18u") AND (pv LIKE "%:setpoint")')
    db.deleteRows(table_name, condition_str='(elemName="dw100g1c18u") AND (pv LIKE "%:readback")')
    db.deleteRows(table_name, condition_str='(elemName="dw100g1c18u") AND (pv LIKE "%:current")')
    db.deleteRows(table_name, condition_str='(elemName="dw100g1c18u") AND (pv LIKE "%:enable")')

    # Delete the old PVs for ID-18-2 that are no longer linked to any of the
    # element-field pairs
    table_name = 'pvs'
    db.deleteRows(table_name, condition_str='(elemName="dw100g1c18d") AND (pv LIKE "%:setpoint")')
    db.deleteRows(table_name, condition_str='(elemName="dw100g1c18d") AND (pv LIKE "%:readback")')
    db.deleteRows(table_name, condition_str='(elemName="dw100g1c18d") AND (pv LIKE "%:current")')
    db.deleteRows(table_name, condition_str='(elemName="dw100g1c18d") AND (pv LIKE "%:enable")')

    db.close()

    ap.machines.load('nsls2', 'SR')

    lines = []
    for e in ap.getElements('*'):
        for fld in sorted(e.fields()):
            lines += ['{0}; {1}; setpoint; '.format(e.name, fld) + s
                      for s in e.pv(field=fld, handle='setpoint')]
            lines += ['{0}; {1}; readback; '.format(e.name, fld) + s
                      for s in e.pv(field=fld, handle='readback')]

        lines += sorted(e.pv()) # This includes unlinked (leftover) PVs as well.

    with open('after.txt', 'w') as f:
        f.write('\n'.join(lines))

    # Manually check "before.txt" and "after.txt" such that the intended
    # PVs have been removed from the database, but nothing else has been changed.

#----------------------------------------------------------------------
def switch_C08_ID_orbcor_PV_unitconv():
    """"""

    if False: # This section can only run once, as HDF5 file does not
              # allow overwrite of existing datasets

        kw = dict(compression='gzip')

        _temp_unitconv_file = UNITCONV_FILE + '.tmp'

        fnew = h5py.File(_temp_unitconv_file, 'w')
        fold = h5py.File(UNITCONV_FILE, 'r')

        excl_ds_names = \
            ['ID_cch{0:d}_v1'.format(iCh) for iCh in range(6)] + \
            ['ID_cch{0:d}_v2'.format(iCh) for iCh in range(6)] + \
            ['ID_cch{0:d}rb1_v1'.format(iCh) for iCh in range(6)] + \
            ['ID_cch{0:d}rb1_v2'.format(iCh) for iCh in range(6)] + \
            ['dw_orbff{0:d}_m0_I_type0'.format(iCh) for iCh in range(12)]

        # First copy existing unit conversion data
        gold = fold['UnitConversion']
        gnew = fnew.create_group('UnitConversion')
        for k, v in gold.items():

            if False: # This will end up with bigger file size
                d = gnew.create_dataset(k, data=v[()], **kw)
            else: # This will end up with smaller file size, so use this one!
                gnew[k] = v[()]
                d = gnew[k]

            if k in excl_ds_names:
                continue
            else:
                for ak, av in v.attrs.items():
                    put_h5py_attr(d, ak, av)

        # Updating to new unit conversions
        for iCh in range(6):

            k = 'ID_cch{0:d}_v1'.format(iCh)
            #
            v = gold[k]
            d = gnew[k]
            #
            for ak, av in v.attrs.items():
                if ak == 'elements':
                    elem_names = av.astype(str).tolist()
                    elem_names.remove('dw100g1c18u')
                    elem_names.remove('dw100g1c18d')
                    av = np.array(elem_names)
                put_h5py_attr(d, ak, av)


            k = 'ID_cch{0:d}_v2'.format(iCh)
            #
            v = gold[k]
            d = gnew[k]
            #
            for ak, av in v.attrs.items():
                if ak == 'elements':
                    elem_names = av.astype(str).tolist()
                    elem_names += ['dw100g1c18u', 'dw100g1c18d']
                    av = np.array(elem_names)
                put_h5py_attr(d, ak, av)



            k = 'ID_cch{0:d}rb1_v1'.format(iCh)
            #
            v = gold[k]
            d = gnew[k]
            #
            for ak, av in v.attrs.items():
                if ak == 'elements':
                    elem_names = av.astype(str).tolist()
                    elem_names.remove('dw100g1c18u')
                    elem_names.remove('dw100g1c18d')
                    av = np.array(elem_names)
                put_h5py_attr(d, ak, av)


            k = 'ID_cch{0:d}rb1_v2'.format(iCh)
            #
            v = gold[k]
            d = gnew[k]
            #
            for ak, av in v.attrs.items():
                if ak == 'elements':
                    elem_names = av.astype(str).tolist()
                    elem_names += ['dw100g1c18u', 'dw100g1c18d']
                    av = np.array(elem_names)
                put_h5py_attr(d, ak, av)


        # Updating to new unit conversions
        for iCh in range(12):

            k = 'dw_orbff{0:d}_m0_I_type0'.format(iCh)
            #
            v = gold[k]
            d = gnew[k]
            #
            for ak, av in v.attrs.items():
                if ak == 'elements':
                    elem_names = av.astype(str).tolist()
                    elem_names.remove('dw100g1c18u')
                    elem_names.remove('dw100g1c18d')
                    av = np.array(elem_names)
                put_h5py_attr(d, ak, av)


            k = 'dw_orbff{0:d}_m0_I_type1'.format(iCh)
            #
            if k not in list(gold):
                d = gnew.create_dataset(k, data=np.array([1.0, 0.0]), **kw)
                uc = {'_class_': 'polynomial', 'dst_unit': 'A', 'dst_unit_sys': 'phy',
                      'elements': ['dw100g1c18u', 'dw100g1c18d'],
                      'field': 'orbff{0:d}_m0_I'.format(iCh),
                      'handle': ['setpoint'],
                      'invertible': 1, 'src_unit': 'A', 'src_unit_sys': ''}
                for k2, v2 in uc.items(): put_h5py_attr(d, k2, v2)
            else:
                v = gold[k]
                d = gnew[k]
                #
                for ak, av in v.attrs.items():
                    if ak == 'elements':
                        elem_names = av.astype(str).tolist()
                        elem_names += ['dw100g1c18u', 'dw100g1c18d']
                        av = np.array(elem_names)
                    put_h5py_attr(d, ak, av)


        fold.close()
        fnew.close()

        # Make sure the new file has the correct permission
        os.chmod(_temp_unitconv_file, 0o755)

        shutil.move(_temp_unitconv_file, UNITCONV_FILE)

    #
    # Test if the unit conversion works
    #

    ap.machines.loadfast('nsls2', 'SR')

    for e in sorted(ap.getElements('dw*c18*')):
        print('## {0} ##'.format(e.name))

        nCh = 6

        for hdl_list, fld_list in [
            (['readback', 'setpoint'], ['cch{0:d}'.format(iCh) for iCh in range(nCh)]),
            (['readback',], ['cch{0:d}rb1'.format(iCh) for iCh in range(nCh)]),
            ]:

            for fld in fld_list:
                for hdl in hdl_list:
                    print('{0}/{1}: {2}, {3}'.format(
                        fld, hdl, e.getUnit(fld, handle=hdl, unitsys=None),
                        e.getUnit(fld, handle=hdl, unitsys='phy')))

                    raw_val = 1.0
                    np.testing.assert_almost_equal(
                        raw_val,
                        e.convertUnit(fld, raw_val, None, 'phy', handle=hdl),
                        decimal=12
                    )

        if e.name.startswith('dw'):
            nCh = 6 + 6 + 2
        else:
            nCh = 6

        for hdl_list, fld_list in [
            (['setpoint',], ['orbff{0:d}_m0_I'.format(iCh) for iCh in range(nCh)]),
            ]:

            for fld in fld_list:
                for hdl in hdl_list:
                    print('{0}/{1}: {2}, {3}'.format(
                        fld, hdl, e.getUnit(fld, handle=hdl, unitsys=None),
                        e.getUnit(fld, handle=hdl, unitsys='phy')))

                    raw_val = 1.0
                    np.testing.assert_almost_equal(
                        raw_val,
                        e.convertUnit(fld, raw_val, None, 'phy', handle=hdl),
                        decimal=12
                    )


    plt.show()

#----------------------------------------------------------------------
def update_C10_gap_PVs():
    """
    """

    idobj = ap.getElements('ivu22g1c10c')[0]

    elemName = idobj.name

    if False:

        for fld in sorted(idobj.fields()):
            if not fld.startswith('gap'):
                continue
            for handle in ['setpoint', 'readback']:
                print('{0} ({1}): {2}'.format(fld, handle, str(idobj.pv(field=fld, handle=handle))))

        '''
        Output before DB change:

ivu22g1c10c
gap (setpoint): ['SR:C10-ID:G1{IVU22:1}Man:SP:Gap']
gap (readback): ['SR:C10-ID:G1{IVU22:1}Y1:Rbv']
gap_hilim (setpoint): []
gap_hilim (readback): ['SR:C10-ID:G1{IVU22:1}Man:SP:Gap.DRVH']
gap_hinominal (setpoint): []
gap_hinominal (readback): ['SR:C10-ID:NomOpen-Sp']
gap_lolim (setpoint): []
gap_lolim (readback): ['SR:C10-ID:G1{IVU22:1}Man:SP:Gap.DRVL']
gap_lonominal (setpoint): []
gap_lonominal (readback): ['SR:C10-ID:NomClose-Sp']
gap_speed (setpoint): ['SR:C10-ID:G1{IVU22:1-Mtr:Gap}.VELO']
gap_speed (readback): []
gap_trig (setpoint): ['SR:C10-ID:G1{IVU22:1}ManG:Go_.PROC']
gap_trig (readback): []
        '''

    new_pvs = {}
    new_pvs['gap'] = dict(setpoint='SR:C10-ID:G1{IVU22:1-Ax:Gap}-Mtr-SP',
                          readback='SR:C10-ID:G1{IVU22:1-Ax:Gap}-Mtr.RBV')
    new_pvs['gap_hilim'] = dict(readback=new_pvs['gap']['setpoint']+'.DRVH')
    new_pvs['gap_lolim'] = dict(readback=new_pvs['gap']['setpoint']+'.DRVL')
    new_pvs['gap_hinominal'] = dict(readback='SR:C10-ID:NomOpen-Sp')
    new_pvs['gap_lonominal'] = dict(readback='SR:C10-ID:NomClose-Sp')
    new_pvs['gap_ramping'] = dict(readback='SR:C10-ID:G1{IVU22:1-Ax:Gap}-Mtr.MOVN')
    new_pvs['gap_speed'] = dict(setpoint='SR:C10-ID:G1{IVU22:1}GapSpeed-SP',
                                readback='SR:C10-ID:G1{IVU22:1}GapSpeed-RB')
    new_pvs['gap_trig'] = dict(setpoint='SR:C10-ID:G1{IVU22:1-Ax:Gap}-Mtr-Go')

    tags = ["aphla.sys.SR"]

    for fld, d in new_pvs.items():
        for handle, pv in d.items():
            if handle == 'readback':
                hdl = 'get'
            elif handle == 'setpoint':
                hdl = 'put'
            else:
                raise ValueError()
            ap.apdata.updateDbPv(
                DBFILE, pv, elemName, fld, elemHandle=hdl, tags=tags, quiet=True)



    # Then purge old PV data from DB file
    sys.path.insert(0, '/home/yhidaka/git_repos/hlsqlite')
    import hlsqlite

    db = hlsqlite.SQLiteDatabase(filepath=DBFILE)

    lines = []
    for e in ap.getElements('*'):
        for fld in sorted(e.fields()):
            lines += ['{0}; {1}; setpoint; '.format(e.name, fld) + s
                      for s in e.pv(field=fld, handle='setpoint')]
            lines += ['{0}; {1}; readback; '.format(e.name, fld) + s
                      for s in e.pv(field=fld, handle='readback')]

        lines += sorted(e.pv()) # This includes unlinked (leftover) PVs as well.

    with open('before.txt', 'w') as f:
        f.write('\n'.join(lines))

    # Delete the old PVs that are no longer linked to any of the
    # element-field pairs
    table_name = 'pvs'
    for old_pv in ['SR:C10-ID:G1{IVU22:1}Man:SP:Gap',
                   'SR:C10-ID:G1{IVU22:1}Y1:Rbv',
                   'SR:C10-ID:G1{IVU22:1}Man:SP:Gap.DRVH',
                   'SR:C10-ID:G1{IVU22:1}Man:SP:Gap.DRVL',
                   'SR:C10-ID:G1{IVU22:1-Mtr:Gap}.VELO',
                   'SR:C10-ID:G1{IVU22:1}ManG:Go_.PROC',
                   ]:
        db.deleteRows(table_name,
            condition_str='(elemName="{0}") AND (pv="{1}")'.format(elemName, old_pv))

    db.close()

    ap.machines.load('nsls2', 'SR')

    lines = []
    for e in ap.getElements('*'):
        for fld in sorted(e.fields()):
            lines += ['{0}; {1}; setpoint; '.format(e.name, fld) + s
                      for s in e.pv(field=fld, handle='setpoint')]
            lines += ['{0}; {1}; readback; '.format(e.name, fld) + s
                      for s in e.pv(field=fld, handle='readback')]

        lines += sorted(e.pv()) # This includes unlinked (leftover) PVs as well.

    with open('after.txt', 'w') as f:
        f.write('\n'.join(lines))

    # Manually check "before.txt" and "after.txt" such that the intended
    # PVs have been removed from the database, but nothing else has been changed.

#----------------------------------------------------------------------
def switch_C23u_ID_orbcor_PVs_to_new_BNL_PSI_PVs():
    """"""

    tags = ['aphla.sys.SR']

    for elemName, new_pv_prefix, ch_inds in [
        ('epu49g1c23u', 'SR:C22-MG{PS:EPU_8}', list(range(6))),        
        ]:
        for iCh in ch_inds:

            # For setpoint fields: "cch0", "cch1", "cch2", ...
            fld, hdl = 'cch{0:d}'.format(iCh), 'put'
            pv = new_pv_prefix + ('U%d-I-SP' % (iCh + 1))
            ap.apdata.updateDbPv(DBFILE, pv, elemName, fld,
                                 elemHandle=hdl, tags=tags, quiet=True, epsilon=0.05)

            # For readback fields: "cch0", "cch1", "cch2", ...
            fld, hdl = 'cch{0:d}'.format(iCh), 'get'
            pv = new_pv_prefix + ('U%d-I-I' % (iCh + 1))
            ap.apdata.updateDbPv(DBFILE, pv, elemName, fld,
                                 elemHandle=hdl, tags=tags, quiet=True, epsilon=0.0)

            # For actual readback fields: "cch0rb1", "cch1rb1", "cch2rb1", ...
            fld, hdl = 'cch{0:d}rb1'.format(iCh), 'get'
            pv = new_pv_prefix + ('U%d-I-I' % (iCh + 1))
            ap.apdata.updateDbPv(DBFILE, pv, elemName, fld,
                                 elemHandle=hdl, tags=tags, quiet=True, epsilon=0.0)

            # For the "cch" readback array PV
            fld, hdl = 'cch[{0:d}]'.format(iCh), 'get'
            pv = new_pv_prefix + ('U%d-I-I' % (iCh + 1))
            ap.apdata.updateDbPv(DBFILE, pv, elemName, fld,
                                 elemHandle=hdl, tags=tags, quiet=True, epsilon=0.0)

            # For setpoint fields for Orbit Feedforward output:
            #     "orbff0_output", "orbff1_output", "orbff2_output", ...
            fld, hdl = 'orbff{0:d}_output'.format(iCh), 'put'
            pv = new_pv_prefix + ('U%d-I-SP' % (iCh + 1))
            ap.apdata.updateDbPv(DBFILE, pv, elemName, fld,
                                 elemHandle=hdl, tags=tags, quiet=True, epsilon=0.05)


#----------------------------------------------------------------------
def switch_C23u_ID_orbcor_PV_unitconv():
    """
    """

    if False: # This section can only run once, as HDF5 file does not
              # allow overwrite of existing datasets

        kw = dict(compression='gzip')

        _temp_unitconv_file = UNITCONV_FILE + '.tmp'

        fnew = h5py.File(_temp_unitconv_file, 'w')
        fold = h5py.File(UNITCONV_FILE, 'r')

        excl_ds_names = \
            ['ID_cch{0:d}_v1'.format(iCh) for iCh in range(6)] + \
            ['ID_cch{0:d}_v2'.format(iCh) for iCh in range(6)] + \
            ['ID_cch{0:d}rb1_v1'.format(iCh) for iCh in range(6)] + \
            ['ID_cch{0:d}rb1_v2'.format(iCh) for iCh in range(6)]
        for mode_i in range(4):
            excl_ds_names += ['epu_orbff{0:d}_m{1:d}_I_type0'.format(iCh, mode_i)
                              for iCh in range(6)]
            excl_ds_names += ['epu_orbff{0:d}_m{1:d}_I_type1'.format(iCh, mode_i)
                              for iCh in range(6)]

        # First copy existing unit conversion data
        gold = fold['UnitConversion']
        gnew = fnew.create_group('UnitConversion')
        for k, v in gold.items():

            if False: # This will end up with bigger file size
                d = gnew.create_dataset(k, data=v[()], **kw)
            else: # This will end up with smaller file size, so use this one!
                gnew[k] = v[()]
                d = gnew[k]

            if k in excl_ds_names:
                continue
            else:
                for ak, av in v.attrs.items():
                    put_h5py_attr(d, ak, av)

        # Updating to new unit conversions
        for iCh in range(6):

            k = 'ID_cch{0:d}_v1'.format(iCh)
            #
            v = gold[k]
            d = gnew[k]
            #
            for ak, av in v.attrs.items():
                if ak == 'elements':
                    elem_names = av.astype(str).tolist()
                    elem_names.remove('epu49g1c23u')
                    av = np.array(elem_names)
                put_h5py_attr(d, ak, av)


            k = 'ID_cch{0:d}_v2'.format(iCh)
            #
            v = gold[k]
            d = gnew[k]
            #
            for ak, av in v.attrs.items():
                if ak == 'elements':
                    elem_names = av.astype(str).tolist()
                    elem_names += ['epu49g1c23u']
                    av = np.array(elem_names)
                put_h5py_attr(d, ak, av)



            k = 'ID_cch{0:d}rb1_v1'.format(iCh)
            #
            v = gold[k]
            d = gnew[k]
            #
            for ak, av in v.attrs.items():
                if ak == 'elements':
                    elem_names = av.astype(str).tolist()
                    elem_names.remove('epu49g1c23u')
                    av = np.array(elem_names)
                put_h5py_attr(d, ak, av)


            k = 'ID_cch{0:d}rb1_v2'.format(iCh)
            #
            v = gold[k]
            d = gnew[k]
            #
            for ak, av in v.attrs.items():
                if ak == 'elements':
                    elem_names = av.astype(str).tolist()
                    elem_names += ['epu49g1c23u']
                    av = np.array(elem_names)
                put_h5py_attr(d, ak, av)


        # Updating to new unit conversions
        for mode_i in range(4):
            for iCh in range(6):
                
                k = 'epu_orbff{0:d}_m{1:d}_I_type0'.format(iCh, mode_i)
                #
                v = gold[k]
                d = gnew[k]
                #
                for ak, av in v.attrs.items():
                    if ak == 'elements':
                        elem_names = av.astype(str).tolist()
                        elem_names.remove('epu49g1c23u')
                        av = np.array(elem_names)
                    put_h5py_attr(d, ak, av)
    
    
                k = 'epu_orbff{0:d}_m{1:d}_I_type1'.format(iCh, mode_i)
                #
                if k not in list(gold):
                    d = gnew.create_dataset(k, data=np.array([1.0, 0.0]), **kw)
                    uc = {'_class_': 'polynomial', 'dst_unit': 'A', 'dst_unit_sys': 'phy',
                          'elements': ['epu49g1c23u'],
                          'field': 'orbff{0:d}_m{1:d}_I'.format(iCh, mode_i),
                          'handle': ['setpoint'],
                          'invertible': 1, 'src_unit': 'A', 'src_unit_sys': ''}
                    for k2, v2 in uc.items(): put_h5py_attr(d, k2, v2)
                else:
                    v = gold[k]
                    d = gnew[k]
                    #
                    for ak, av in v.attrs.items():
                        if ak == 'elements':
                            elem_names = av.astype(str).tolist()
                            elem_names += ['epu49g1c23u']
                            av = np.array(elem_names)
                        put_h5py_attr(d, ak, av)                

        fold.close()
        fnew.close()

        # Make sure the new file has the correct permission
        os.chmod(_temp_unitconv_file, 0o755)

        shutil.move(_temp_unitconv_file, UNITCONV_FILE)

    #
    # Test if the unit conversion works
    #

    ap.machines.loadfast('nsls2', 'SR')

    for e in sorted(ap.getElements('epu49g1c23u')):
        print('## {0} ##'.format(e.name))

        nCh = 6

        for hdl_list, fld_list in [
            (['readback', 'setpoint'], ['cch{0:d}'.format(iCh) for iCh in range(nCh)]),
            (['readback',], ['cch{0:d}rb1'.format(iCh) for iCh in range(nCh)]),
            ]:

            for fld in fld_list:
                for hdl in hdl_list:
                    print('{0}/{1}: {2}, {3}'.format(
                        fld, hdl, e.getUnit(fld, handle=hdl, unitsys=None),
                        e.getUnit(fld, handle=hdl, unitsys='phy')))

                    raw_val = 1.0
                    np.testing.assert_almost_equal(
                        raw_val,
                        e.convertUnit(fld, raw_val, None, 'phy', handle=hdl),
                        decimal=12
                    )

        if e.name.startswith('dw'):
            nCh = 6 + 6 + 2
        else:
            nCh = 6

        if not e.name.endswith(('c23u', 'c23d')):
            for hdl_list, fld_list in [
                (['setpoint',], ['orbff{0:d}_m0_I'.format(iCh) for iCh in range(nCh)]),
                ]:
    
                for fld in fld_list:
                    for hdl in hdl_list:
                        print('{0}/{1}: {2}, {3}'.format(
                            fld, hdl, e.getUnit(fld, handle=hdl, unitsys=None),
                            e.getUnit(fld, handle=hdl, unitsys='phy')))
    
                        raw_val = 1.0
                        np.testing.assert_almost_equal(
                            raw_val,
                            e.convertUnit(fld, raw_val, None, 'phy', handle=hdl),
                            decimal=12
                        )
        else:
            nModes = 4
            for iMode in range(nModes):
                for hdl_list, fld_list in [
                    (['setpoint',], ['orbff{0:d}_m{1:d}_I'.format(iCh, iMode) 
                                     for iCh in range(nCh)]),
                    ]:
        
                    for fld in fld_list:
                        for hdl in hdl_list:
                            print('{0}/{1}: {2}, {3}'.format(
                                fld, hdl, e.getUnit(fld, handle=hdl, unitsys=None),
                                e.getUnit(fld, handle=hdl, unitsys='phy')))
        
                            raw_val = 1.0
                            np.testing.assert_almost_equal(
                                raw_val,
                                e.convertUnit(fld, raw_val, None, 'phy', handle=hdl),
                                decimal=12
                            )
            



    plt.show()


if __name__ == '__main__':
    
    # Duplicated from /home/yhidaka/git_repos/nsls2scripts2/aphla_database/update_aphla_db.py
    # on 01/14/2022

    if False:
        _play_around()

    elif False:
        update_C21_straight()
    elif False:
        update_C21_straight_unitconv()
    elif False:
        test_idlocalbump()

    elif False:
        update_C19_straight()
    elif False:
        update_C19_straight_unitconv()
    elif False:
        check_C19_elem_readback()

    elif False:
        update_C02_straight()
    elif False:
        update_C02_straight_unitconv()
    elif False:
        check_C02_elem_readback()

    elif False:
        update_fcors()
    elif False:
        update_fcors_unitconv()
    elif False:
        diff_Xi_fcor_spos()
    elif False:
        show_link_btw_wrong_vs_correct_fcor_indexes()

    elif False:
        add_new_SQ_at_C16_for_AMX_coup_compensation()
    elif False:
        add_2nd_channels_to_all_SQH_skew_quads()

    elif False:
        add_2nd_channels_to_cors()

    elif False:
        add_C21_2_ID_ESM105_elem_and_pvs()
    elif False:
        add_C21_2_ID_ESM105_unitconv()

    elif False:
        correct_C04_C05_C17_straight_spos_C04_C12_group()

    elif False:
        correct_gap_readback_phy_unit_for_some_IVUs()

    # 06/23/2017
    elif False:
        add_cch0rb1_for_all_IDs()
    elif False:
        add_unitconv_to_ID_cch()
    elif False:
        add_orbit_ff_pvs()
    elif False:
        add_unitconv_to_ID_orbit_ff_fields()
    elif False:
        add_current_strip_channels()
    elif False:
        add_unitconv_to_current_strip_channels()
    elif False:
        add_current_strip_ff_pvs()
    elif False:
        add_unitconv_to_current_strip_ff_pvs()
    # 06/26/2017
    elif False:
        add_ff_output_pvs()
    elif False:
        add_limit_nominal_gap_phase_fields()
    elif False:
        add_unitconv_to_limit_nominal_gap_phase_fields()
    elif False:
        add_gap_phase_speed_fields()
    elif False:
        add_unitconv_gap_phase_speed_pvs()

    elif False:
        add_SST_fake_ID()
    elif False:
        add_SST_ID_elems()
    elif False:
        # 11/13/2017
        add_SST_ID_elems_PVs()
    elif False:
        # 11/14/2017
        add_SST_U42_gap_unitconv()
    elif False:
        # 11/14/2017
        add_SST_cch_unitconv()
    elif False:
        # 11/14/2017
        correct_U42_elem_name_and_type()
        ap.machines.loadfast('nsls2', 'SR')
        correct_SST_EPU60_group()
    elif False:
        # 11/14/2017
        correct_U42_unitcnov_due_to_elem_name_change()
    elif False:
        # 11/16/2017
        fix_U42_EPU60_US_DS_error()

    elif False:
        # 11/22/2017
        add_fcor_mode_xjump_yjump_fields()
    elif False:
        # 11/22/2017
        add_fcor_xjump_yjump_unitconv()

    elif False:
        print_all_ID_field_unitconv('print_all_ID_field_unitconv_20171116.txt')
    elif False:
        print_all_ID_gap_values()
    elif False:
        print_all_ID_phase_values()

    elif False: # 01/19/2018
        add_orbit_ff_pvs_for_SST_U42_and_EPU60()
    elif False: # 01/19/2018
        add_unitconv_to_ID_orbit_ff_fields_for_SST_U42_and_EPU60()

    elif False: # 07/30/2018
        fix_fast_corrector_cell_strings()

    elif False: # 07/31/2018
        add_BBA_readback_PVs()
    elif False: # 07/31/2018
        add_unitconv_BPM_fields_0_ref1_ref2_bba_fa_tbt()

    elif False: # 09/10/2018
        switch_C04_C05_ID_orbcor_PVs_to_new_BNL_PSI_PVs()
        # Also manually confirmed that these new setpoint PVs have
        # .DRVL and .DRVH, which are needed for the orbit feedforward script to
        # work correctly.
    elif False: # 09/10/2018
        purge_old_ID_orb_cor_PVs_for_C04_and_C05_IDs()
    elif False: # 09/10/2018
        switch_C04_C05_ID_orbcor_PV_unitconv()
        # Had to change hg_repos/nsls2scripts/operation/idcomm/idff.py
        # for "FF_COR_UNITS" from "10uA" to "A".
        #
        # Also, this has nothing to do with this unit conversion change,
        # but I added entries for C04 and C05 IDs in "CCH_FF_PREFIX_TEMPLATE".
    elif False: # 09/10/2018
        remove_cch_on_fields_from_C04_and_C05_IDs()

    elif False: # 11/08/2018
        add_xray_bpms_C03_C16_C17ud()
    elif False: # 11/08/2018
        add_xray_bpms_C03_C16_C17ud_unitconv()
    elif False: # 11/08/2018
        add_xray_bpms_C03_C16_C17ud_fld_x_y()
    elif False: # 11/08/2018
        add_xray_bpms_C03_C16_C17ud_fld_x_y_unitconv()

    elif False: # 01/23/2019
        switch_C03_10_16_17s_ID_orbcor_PVs_to_new_BNL_PSI_PVs()

        # Also manually confirmed that these new setpoint PVs have
        # .DRVL and .DRVH, which are needed for the orbit feedforward script to
        # work correctly. Just the run the following section.
        if False:
            id_list = sorted(
                ap.getElements('ivu*c03*') + ap.getElements('ivu*c10*') +
                ap.getElements('ivu*c16*') + ap.getElements('ivu*c17*'))
            for idobj in id_list:
                print(idobj.name)
                for iCh in range(6):
                    try:
                        pv = idobj.pv(field='cch{0:d}'.format(iCh), handle='setpoint')[0]
                        print(caget([pv+'.DRVL', pv+'.DRVH']))
                    except IndexError:
                        break
                    except:
                        raise
    elif False: # 01/23/2019
        purge_old_ID_orb_cor_PVs_for_C03_10_16_17_IDs()
        # "cch%_on" fields have been automatically removed by removing PVs with
        # the ending pattern %:enable" from the database.
    elif False: # 01/23/2019
        switch_C03_10_16_17_ID_orbcor_PV_unitconv()
        # Had to change
        #    (OBSOLETE) hg_repos/nsls2scripts/operation/idcomm/idff.py
        #    (UPDATED) git_repos/hlatools/id-orb-fdfrwrd/idff.py
        # for "FF_COR_UNITS" from "10uA" to "A".
        #
        # Also, this has nothing to do with this unit conversion change,
        # but I added entries for C03, C10, C16 and C17 IDs in "CCH_FF_PREFIX_TEMPLATE".
    elif False: # 01/23/2019
        update_epsilon_for_BNL_PSI_channels()
    elif False: # 01/23/2019
        print_all_ID_cch_values() # final check
    elif False: # 01/23/2019
        update_C04_gap_PVs()
    elif False: # 01/23/2019
        update_C12_gap_PVs()
    elif False: # 01/23/2019
        update_C16_gap_PVs()
    elif False: # 01/23/2019
        update_C04_12_16_gap_unitconvs()
    elif False: # 01/23/2019
        print_all_ID_gap_values() # final check

    elif False: # 01/24/2019
        add_gap_phase_limit_PVs_to_C07_IDs()
    elif False: # 01/24/2019
        add_unitconvs_to_gap_phase_limit_to_C07_IDs()

    elif False: # 01/25/2019
        replace_sum_PVSP_to_SP1_for_orbff_C03_16_17_IDs()

    elif False: # 01/26/2019
        change_cch_readback_PVs_to_cch_rb1_PVs_for_BNL_PSI_ID_cors()
    elif False: # 01/26/2019
        update_epsilon_for_all_ID_cor_BNL_PSI_channels()
    elif False: # 01/26/2019
        fix_cch_list_readback_PVs_for_c03_04_05_10_16_17()

    elif False: # 02/02/2019 [For the issue of 3-ID corrector impact on DCCT]
        add_2nd_channels_for_C02_CL1B_C03_CL1A_to_C03_ID_cch()
    elif False: # 02/02/2019 [For the issue of 3-ID corrector impact on DCCT]
        add_units_for_C03_ID_cch6thru9()

    elif False: #04/11/2019
        update_C03_gap_PVs()
    elif False: #04/11/2019
        update_C05_gap_PVs()
    elif False: #04/11/2019
        update_C11_gap_PVs()
    elif False: #04/11/2019
        update_C17u_gap_PVs()
    elif False: #04/11/2019
        update_C17d_gap_PVs()
    elif False: #04/11/2019
        update_C03_05_11_17_gap_unitconvs()

    elif False: # 08/06/2019
        switch_C08_C11_C12_ID_orbcor_PVs_to_new_BNL_PSI_PVs()

        # Also manually confirmed that these new setpoint PVs have
        # .DRVL and .DRVH, which are needed for the orbit feedforward script to
        # work correctly. Just the run the following section.
        if False:
            id_list = sorted(
                ap.getElements('dw100*c08*') +
                ap.getElements('ivu*c11*') + ap.getElements('ivu*c12*'))
            for idobj in id_list:
                print(idobj.name)
                for iCh in range(6):
                    try:
                        pv = idobj.pv(field='cch{0:d}'.format(iCh), handle='setpoint')[0]
                        print(caget([pv+'.DRVL', pv+'.DRVH']))
                    except IndexError:
                        break
                    except:
                        raise
    elif False: # 08/06/2019
        fix_DW08_orbff_output_PVs()
    elif False: # 08/06/2019
        purge_old_ID_orb_cor_PVs_for_C08_11_12_IDs()
        # "cch%_on" fields have been automatically removed by removing PVs with
        # the ending pattern %:enable" from the database.
    elif False: # 08/06/2019
        switch_C08_11_12_ID_orbcor_PV_unitconv()
        # Had to change
        #    (UPDATED) git_repos/hlatools/id-orb-fdfrwrd/idff.py [This version
        #              should automatically get the correct unit from aphla
        #              database file.]
        #    (OBSOLETE) hg_repos/nsls2scripts/idcomm/idff.py
        # for "FF_COR_UNITS" from "10uA" to "A".
        #
        # Also, this has nothing to do with this unit conversion change,
        # but I added entries for C11 and C12 IDs in "CCH_FF_PREFIX_TEMPLATE".
        # [The git version relies on "id-orb-fdfrwrd/orbff_config.json".]


    elif False: # 01/10/2020 (**** From this date on, this script is run in Python 3 ****)
        switch_C18_ID_orbcor_PVs_to_new_BNL_PSI_PVs()

        # Also manually confirmed that these new setpoint PVs have
        # .DRVL and .DRVH, which are needed for the orbit feedforward script to
        # work correctly. Just the run the following section.
        if False:
            id_list = sorted(
                ap.getElements('dw100*c18*'))
            for idobj in id_list:
                print(idobj.name)
                for iCh in range(6):
                    try:
                        pv = idobj.pv(field='cch{0:d}'.format(iCh), handle='setpoint')[0]
                        print(caget([pv+'.DRVL', pv+'.DRVH']))
                    except IndexError:
                        break
                    except:
                        raise
        # DRVL & DRVH had to be adjusted down from +/-999999 to +/-9.0001
        if False:
            from cothread.catools import caput

            id_list = sorted(
                ap.getElements('dw100*c18*'))
            for idobj in id_list:
                print(idobj.name)
                for iCh in range(6):
                    try:
                        pv = idobj.pv(field='cch{0:d}'.format(iCh), handle='setpoint')[0]
                        caput(f'{pv}.DRVL', -9.0001)
                        caput(f'{pv}.DRVH', +9.0001)
                        print(caget([pv+'.DRVL', pv+'.DRVH']))
                    except IndexError:
                        break
                    except:
                        raise
    elif False: # 01/10/2020
        fix_DW18_orbff_output_PVs()
    elif False: # 01/10/2020
        purge_old_ID_orb_cor_PVs_for_C18_IDs()
    elif False: # 01/10/2020
        switch_C08_ID_orbcor_PV_unitconv()

    elif False: # 10/19/2020
        update_C10_gap_PVs()
        # No unit changes were needed for this.

    elif False: # 01/14/2022
        switch_C23u_ID_orbcor_PVs_to_new_BNL_PSI_PVs()

        # Manual confirmation of the presennce of .DRVL & .DRVH for these new 
        # setpoint PVs (needed for the feedforward script to work), as well as
        # adjustment of DRVL & DRVH values to +/-8 A, have been done in 
        # "update_apv2_db.py".
    elif True: # 01/14/2022
        switch_C23u_ID_orbcor_PV_unitconv()


    plt.show()