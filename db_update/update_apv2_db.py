import json
import pickle
import gzip
from pathlib import Path
import re

import numpy as np
from cothread.catools import caget

import aphla as ap
ap.machines.load('nsls2', 'SR')

SR_CIRCUMF = ap.machines.getMachine('SR').se # [m]

#V2DB_FOLDER = Path(__file__).joinpath('../../v2tests').resolve()
V2DB_FOLDER = Path('/epics/aphla/apconf/nsls2')

ELEM_PV_MV_PGZ_FILEPATHS = dict(
    LN=V2DB_FOLDER.joinpath('nsls2_sr_elems_pvs_mvs.pgz'),
    LTD1=V2DB_FOLDER.joinpath('nsls2_ltd1_elems_pvs_mvs.pgz'),
    LTD2=V2DB_FOLDER.joinpath('nsls2_ltd2_elems_pvs_mvs.pgz'),
    LTB=V2DB_FOLDER.joinpath('nsls2_ltb_elems_pvs_mvs.pgz'),
    BR=V2DB_FOLDER.joinpath('nsls2_br_elems_pvs_mvs.pgz'),
    BTD=V2DB_FOLDER.joinpath('nsls2_btd_elems_pvs_mvs.pgz'),
    BTS=V2DB_FOLDER.joinpath('nsls2_bts_elems_pvs_mvs.pgz'),
    SR=V2DB_FOLDER.joinpath('nsls2_sr_elems_pvs_mvs.pgz'),
)

BPM_PV_SUFFIX = {
    'get': {
        'xbba': 'BBA:X-I', 'ybba': 'BBA:Y-I',
        'x0': 'Pos:X-I', 'y0': 'Pos:Y-I',
        'x': 'Pos:XwUsrOff-Calc', 'y': 'Pos:YwUsrOff-Calc',
        'ampl': 'Ampl:SSA-Calc',
        'xtbt': 'TBT-X', 'ytbt': 'TBT-Y', 'Itbt': 'TBT-S',
        'xfa': 'FA-X', 'yfa': 'FA-Y', 'Ifa': 'FA-S',
            },
    'put': {
        'xbba': 'BbaXOff-SP', 'ybba': 'BbaYOff-SP',
        'xref1': 'Pos:Href-SP', 'yref1': 'Pos:Vref-SP',
        'xref2': 'Pos:UsrXoffset-SP', 'yref2': 'Pos:UsrYoffset-SP',
    }
}

def jsonify(o):

    if isinstance(o, (np.int64, np.int32)):
        return int(o)

def save_pgz_db_contents_to_json(machine_list=None):

    for machine, pgz_filepath in ELEM_PV_MV_PGZ_FILEPATHS.items():
        if machine_list is not None:
            if machine not in machine_list:
                continue

        d = get_elem_pv_mv_pgz_database_dict(machine)

        json_filepath = pgz_filepath.name.replace('.pgz', '.json')
        with open(json_filepath, 'w') as f:
            json.dump(d, f, default=jsonify, indent=2)

def update_C23u_BNL_PSI_upgrade():
    """
    --- PV Changes ---

    For "Ch.0":
        SR:C23-ID:G1A{EPU:1}MPS:ch0:setpoint => SR:C22-MG{PS:EPU_8}U1-I-SP
        SR:C23-ID:G1A{EPU:1}MPS:ch0:readback => SR:C22-MG{PS:EPU_8}U1-I-I
        SR:C23-ID:G1A{EPU:1}MPS:ch0:current => SR:C22-MG{PS:EPU_8}U1-I-I

    For the other channels 1 through 5, change "ch0" to "ch1", "ch2", ..., "ch5"
    and and "U1" to "U2", "U3", ..., "U6".

    --- Field Changes ---
    cch0, cch1, ..., cch5:
        change RB/SP => -I-I & -I-SP
    cch0_on, cch1_on, ..., cch5_on:
        delete this field
    cch0rb1, cch1rb1, ..., cch5rb1:
        RB => -I-I
        SP => None
    cch[0], cch[1], ..., cch[5]:
        RB => -I-I
        SP => None
    orbff0_output, orbff1_output, ..., orbff5_output:
        RB => None
        SP => -I-SP
    """

    with gzip.GzipFile(ELEM_PV_MV_PGZ_FILEPATHS['SR'], 'rb') as f:
        d = pickle.load(f)

    idname = 'epu49g1c23u'

    for fld, v1 in d[idname]['map'].items():
        if 'get' in v1:
            pvrb = v1['get']['pv']
        else:
            pvrb = None

        if 'put' in v1:
            pvsp = v1['put']['pv']
        else:
            pvsp = None

        print(f"Field: {fld}; Get: {pvrb}; Put: {pvsp}")

    print('###################################################')

    for fld in list(d[idname]['map']):

        v1 = d[idname]['map'][fld]

        if 'get' in v1:
            pvrb = v1['get']['pv']
        else:
            pvrb = None

        if 'put' in v1:
            pvsp = v1['put']['pv']
        else:
            pvsp = None

        if ((pvrb is not None) and (':ch' in pvrb)) or (
            (pvsp is not None) and (':ch' in pvsp)):
            print(f"OLD:: Field: {fld}; Get: {pvrb}; Put: {pvsp}")

            if matches := re.findall('^cch(\d)$', fld):
                i = int(matches[0])
                v1['get']['pv'] = f'SR:C22-MG{{PS:EPU_8}}U{i+1}-I-I'
                v1['put']['pv'] = f'SR:C22-MG{{PS:EPU_8}}U{i+1}-I-SP'

            elif matches := re.findall('^cch(\d)_on$', fld):
                del d[idname]['map'][fld]

            elif matches := re.findall('^cch(\d)rb1$', fld):
                i = int(matches[0])
                v1['get']['pv'] = f'SR:C22-MG{{PS:EPU_8}}U{i+1}-I-I'
                if 'put' in v1:
                    del v1['put']

            elif matches := re.findall('^cch\[(\d)\]$', fld):
                i = int(matches[0])
                assert 'get' not in v1 # This was an error already in the db
                v1['get']= dict(pv=f'SR:C22-MG{{PS:EPU_8}}U{i+1}-I-I')
                if 'put' in v1:
                    del v1['put']

            elif matches := re.findall('^orbff(\d)_output$', fld):
                i = int(matches[0])
                if 'get' in v1:
                    del v1['get']
                v1['put']['pv'] = f'SR:C22-MG{{PS:EPU_8}}U{i+1}-I-SP'

            else:
                raise NotImplementedError

            if fld in d[idname]['map']:

                if 'get' in v1:
                    new_pvrb = v1['get']['pv']
                else:
                    new_pvrb = None

                if 'put' in v1:
                    new_pvsp = v1['put']['pv']
                else:
                    new_pvsp = None

                print((f"NEW:: Field: {fld}; Get: {new_pvrb}; Put: {new_pvsp}"))
            else:
                print(f"NEW:: Field '{fld}' deleted")

    ''' Also the unit conversion file "nsls2sr_unitconv.yaml" had to be manually
        modified as follows:

diff --git a/v2tests/nsls2sr_unitconv.yaml b/v2tests/nsls2sr_unitconv.yaml
index ebb4f34..3856168 100644
--- a/v2tests/nsls2sr_unitconv.yaml
+++ b/v2tests/nsls2sr_unitconv.yaml
@@ -442,7 +442,7 @@ SR:
     coeffs: [1e-3, 0.0]

   ID_orb_cor_channel_type1: &ID_orb_cor_channel_type1
-    elements: [dw100g1c28u, dw100g1c28d, epu49g1c23u, epu49g1c23d]
+    elements: [dw100g1c28u, dw100g1c28d, epu49g1c23d]
     fields: [
       cch0, cch1, cch2, cch3, cch4, cch5,
       orbff0_m0_I, orbff1_m0_I, orbff2_m0_I, orbff3_m0_I, orbff4_m0_I,
@@ -475,7 +475,10 @@ SR:
                ivu20g1c11c, ivu23g1c12d, ivu23g1c16c, ivu21g1c17u, ivu21g1c17d,
                ivu18g1c19u,
                dw100g1c08u, dw100g1c08d, dw100g1c18u, dw100g1c18d,
+               epu49g1c23u,
                _phaserg1c23c]
+    # *) Only ivu20g1c03c has cch6, cch7, cch8, cch9, which were introduced when
+    #    its ID correctors couldn't be used.
     fields: [
       cch0, cch1, cch2, cch3, cch4, cch5, cch6, cch7, cch8, cch9,
       orbff0_m0_I, orbff1_m0_I, orbff2_m0_I, orbff3_m0_I, orbff4_m0_I,
    '''

    with gzip.GzipFile(ELEM_PV_MV_PGZ_FILEPATHS['SR'], 'wb') as f:
        pickle.dump(d, f)


def update_C23d_BNL_PSI_upgrade():
    """
    --- PV Changes ---

    For "Ch.0":
        SR:C23-ID:G1A{EPU:2}MPS:ch0:setpoint => SR:C22-MG{PS:EPU_9}U1-I-SP
        SR:C23-ID:G1A{EPU:2}MPS:ch0:readback => SR:C22-MG{PS:EPU_9}U1-I-I
        SR:C23-ID:G1A{EPU:2}MPS:ch0:current => SR:C22-MG{PS:EPU_9}U1-I-I

    For the other channels 1 through 5, change "ch0" to "ch1", "ch2", ..., "ch5"
    and and "U1" to "U2", "U3", ..., "U6".

    --- Field Changes ---
    cch0, cch1, ..., cch5:
        change RB/SP => -I-I & -I-SP
    cch0_on, cch1_on, ..., cch5_on:
        delete this field
    cch0rb1, cch1rb1, ..., cch5rb1:
        RB => -I-I
        SP => None
    cch[0], cch[1], ..., cch[5]:
        RB => -I-I
        SP => None
    orbff0_output, orbff1_output, ..., orbff5_output:
        RB => None
        SP => -I-SP
    """

    with gzip.GzipFile(ELEM_PV_MV_PGZ_FILEPATHS['SR'], 'rb') as f:
        d = pickle.load(f)

    idname = 'epu49g1c23d'

    for fld, v1 in d[idname]['map'].items():
        if 'get' in v1:
            pvrb = v1['get']['pv']
        else:
            pvrb = None

        if 'put' in v1:
            pvsp = v1['put']['pv']
        else:
            pvsp = None

        print(f"Field: {fld}; Get: {pvrb}; Put: {pvsp}")

    print('###################################################')

    for fld in list(d[idname]['map']):

        v1 = d[idname]['map'][fld]

        if 'get' in v1:
            pvrb = v1['get']['pv']
        else:
            pvrb = None

        if 'put' in v1:
            pvsp = v1['put']['pv']
        else:
            pvsp = None

        if ((pvrb is not None) and (':ch' in pvrb)) or (
            (pvsp is not None) and (':ch' in pvsp)):
            print(f"OLD:: Field: {fld}; Get: {pvrb}; Put: {pvsp}")

            if matches := re.findall('^cch(\d)$', fld):
                i = int(matches[0])
                v1['get']['pv'] = f'SR:C22-MG{{PS:EPU_9}}U{i+1}-I-I'
                v1['put']['pv'] = f'SR:C22-MG{{PS:EPU_9}}U{i+1}-I-SP'

            elif matches := re.findall('^cch(\d)_on$', fld):
                del d[idname]['map'][fld]

            elif matches := re.findall('^cch(\d)rb1$', fld):
                i = int(matches[0])
                v1['get']['pv'] = f'SR:C22-MG{{PS:EPU_9}}U{i+1}-I-I'
                if 'put' in v1:
                    del v1['put']

            elif matches := re.findall('^cch\[(\d)\]$', fld):
                i = int(matches[0])
                assert 'get' not in v1 # This was an error already in the db
                v1['get']= dict(pv=f'SR:C22-MG{{PS:EPU_9}}U{i+1}-I-I')
                if 'put' in v1:
                    del v1['put']

            elif matches := re.findall('^orbff(\d)_output$', fld):
                i = int(matches[0])
                if 'get' in v1:
                    del v1['get']
                v1['put']['pv'] = f'SR:C22-MG{{PS:EPU_9}}U{i+1}-I-SP'

            else:
                raise NotImplementedError

            if fld in d[idname]['map']:

                if 'get' in v1:
                    new_pvrb = v1['get']['pv']
                else:
                    new_pvrb = None

                if 'put' in v1:
                    new_pvsp = v1['put']['pv']
                else:
                    new_pvsp = None

                print((f"NEW:: Field: {fld}; Get: {new_pvrb}; Put: {new_pvsp}"))
            else:
                print(f"NEW:: Field '{fld}' deleted")

    ''' Also the unit conversion file "nsls2sr_unitconv.yaml" had to be manually
        modified as follows:

diff --git a/v2tests/nsls2sr_unitconv.yaml b/v2tests/nsls2sr_unitconv.yaml
index 3856168..e7cce7e 100644
--- a/v2tests/nsls2sr_unitconv.yaml
+++ b/v2tests/nsls2sr_unitconv.yaml
@@ -442,7 +442,7 @@ SR:
     coeffs: [1e-3, 0.0]

   ID_orb_cor_channel_type1: &ID_orb_cor_channel_type1
-    elements: [dw100g1c28u, dw100g1c28d, epu49g1c23d]
+    elements: [dw100g1c28u, dw100g1c28d]
     fields: [
       cch0, cch1, cch2, cch3, cch4, cch5,
       orbff0_m0_I, orbff1_m0_I, orbff2_m0_I, orbff3_m0_I, orbff4_m0_I,
@@ -475,7 +475,7 @@ SR:
                ivu20g1c11c, ivu23g1c12d, ivu23g1c16c, ivu21g1c17u, ivu21g1c17d,
                ivu18g1c19u,
                dw100g1c08u, dw100g1c08d, dw100g1c18u, dw100g1c18d,
-               epu49g1c23u,
+               epu49g1c23u, epu49g1c23d,
                _phaserg1c23c]
     # *) Only ivu20g1c03c has cch6, cch7, cch8, cch9, which were introduced when
     #    its ID correctors couldn't be used.
    '''

    with gzip.GzipFile(ELEM_PV_MV_PGZ_FILEPATHS['SR'], 'wb') as f:
        pickle.dump(d, f)

def get_new_id(database_dict):

    d = database_dict

    all_ids = [] # Likely SQL related
    for elemName, d2 in d.items():
        all_ids.append(d2['id'])

    assert all_ids.count(None) == 1
    all_ids.remove(None)
    assert np.unique(all_ids).size == len(all_ids)

    return np.max(all_ids) + 1

def get_elem_pv_mv_pgz_database_dict(machine):

    with gzip.GzipFile(ELEM_PV_MV_PGZ_FILEPATHS[machine], 'rb') as f:
        d = pickle.load(f)

    return d

def print_elems_around_straight(cell_num, n=5):
    """"""

    sc = SR_CIRCUMF / 30 * cell_num # [m]

    all_elems_nearby_cells = (
        ap.getElements(f'*c{(cell_num-1 if cell_num >= 2 else 30):02d}*') +
        ap.getElements(f'*c{cell_num:02d}*'))
    closest = np.argmin(np.abs(np.array([e.se for e in all_elems_nearby_cells]) - sc))

    print(f'\n** Straight Center @ {sc:.4f}')
    print('[Elem.Name]  [Type]     [sb]     [se]   [index]')

    past_center = False
    for e in all_elems_nearby_cells[(closest-n):(closest+n)]:
        if (not past_center) and (e.se >= sc):
            print(f'## Straight Center @ {sc:4f} ##')
            past_center = True
        print(f'{e.name:12s}: {e.family:6s}: {e.sb:8.4f}:{e.se:8.4f}: {e.index:d}')

def update_C27_straight(exist_ok=False):
    """ C27 HEX SCW """

    d = get_elem_pv_mv_pgz_database_dict('SR')

    cell_num = 27

    print_elems_around_straight(cell_num, n=5)

    us_sext = sorted(ap.getGroupMembers(['SEXT', f'C{cell_num-1:02d}'], op='intersection'))[-1]
    ds_sext = sorted(ap.getGroupMembers(['SEXT', f'C{cell_num:02d}'], op='intersection'))[0]

    us_i = ap.getElements('*').index(us_sext)
    ds_i = ap.getElements('*').index(ds_sext)
    existing_elems = ap.getElements('*')[us_i:(ds_i+1)]

    print('Elem Name, Index,     sb,       se')
    print('\n'.join([f'{elem.name}, {elem.index}, {elem.sb:.6f}, {elem.se:.6f}'
                     for elem in existing_elems]))

    existing_elem_props = dict(sc=[], index=[])
    for e in existing_elems:
        existing_elem_props['sc'].append((e.sb+e.se)/2)
        existing_elem_props['index'].append(e.index)

    # s-pos of center of straight
    straight_sc = SR_CIRCUMF / 30 * cell_num # [m]

    bpm_info_list = [
        dict(name='pu1g1c27a',
             sc=float(f'{straight_sc - 2.3177:.6f}'),
             devname=f'C{cell_num:02d}-BPM7',
             groups=['UBPM', 'PU1']),
        dict(name='pu4g1c27a',
             sc=float(f'{straight_sc + 2.1519:.6f}'),
             devname=f'C{cell_num:02d}-BPM8',
             groups=['UBPM', 'PU4']),
    ]
    for info in bpm_info_list:
        info['sb'] = info['sc']
        info['se'] = info['sc']
        info['L'] = 0.0
        info['type'] = "UBPM_"
        info['cell'] = f"C{cell_num:02d}"
        info['girder'] = "G1"
        info['symmetry'] = "A"

    id_info_list = [dict(name='scw70g1c27d', type='SCW',
                   symmetry='D', groups=['ID', 'SCW70', 'HEX'],
                   sc=straight_sc+1.0, L=1.19)]
    for info in id_info_list:
        info['sb'] = info['sc'] - info['L']/2
        info['se'] = info['sc'] + info['L']/2
        info['cell'] = f"C{cell_num:02d}"
        info['girder'] = "G1"


    for new_elem_info in bpm_info_list + id_info_list:
        new_elem_info['index'] = int(np.round(
            np.interp(new_elem_info['sc'], existing_elem_props['sc'],
                      existing_elem_props['index'],
                      left=np.nan, right=np.nan)))
        print(new_elem_info['name'], new_elem_info['index'])


    for info in bpm_info_list + id_info_list:

        elem_name = info['name']
        upper_elem_name = elem_name.upper()

        if (not exist_ok) and (elem_name in d):
            print(f'Specified element "{elem_name}" aready exists. Aborting.')
            return

        new = {}
        new['id'] = get_new_id(d)
        for k in ['archive', 'size', 'virtual']:
            new[k] = 0
        new['elemType'] = info['type']
        new['cell'] = info['cell']
        new['girder'] = info['girder']
        new['symmetry'] = info['symmetry']
        new["elemLength"] = info['L']
        new["elemPosition"] = info['se']
        new["elemIndex"] = info['index']
        new["elemGroups"] = ';'.join(info['groups'])
        new["tags"] = ["aphla.sys.SR"]

        if 'UBPM' in info['groups']:

            new["devName"] = info['devname']
            bpm_num = int(info['devname'].split('-')[1][len('BPM'):])

            new["map"] = {}
            for fld in ['x0', 'y0', 'x', 'y', 'xref1', 'yref1', 'xref2', 'yref2',
                        'ampl', 'xtbt', 'ytbt', 'Itbt', 'xfa', 'yfa', 'Ifa',
                        'xbba', 'ybba']:

                fld_d = {}

                if fld in BPM_PV_SUFFIX['get']:
                    get_d = {}
                    pv_suffix = BPM_PV_SUFFIX['get'][fld]
                    get_d['pv'] = f"SR:{new['cell']}-BI{{BPM:{bpm_num}}}{pv_suffix}"
                    get_d['mv'] = {'pyelegant':
                                   dict(elem_name=upper_elem_name, property=fld)}
                    fld_d['get'] = get_d

                if fld in BPM_PV_SUFFIX['put']:
                    put_d = {}
                    pv_suffix = BPM_PV_SUFFIX['put'][fld]
                    put_d['pv'] = f"SR:{new['cell']}-BI{{BPM:{bpm_num}}}{pv_suffix}"
                    put_d['mv'] = {'pyelegant':
                                   dict(elem_name=upper_elem_name, property=fld)}
                    fld_d['put'] = put_d

                new['map'][fld] = fld_d

        elif 'ID' in info['groups']:

            new["map"] = {}

            # Field "gap" == "mainI" [A] (442 A maximum according to T. Tanabe)
            #
            mainI_pvsp = 'SR:C26-MG{PS:HEX-Main}I:Sp1-SP' # main current SP with Y. Tian's sequencer
            mainI_raw_pvsp = 'SR:C26-MG{PS:HEX-Main}I:Sp1-SPHW' # main current SP (underlying PV for Y. Tian's sequencer)
            mainI_pvrb1 = 'SR:C26-MG{PS:HEX-Main}I:Ps1DCCT1-I' # main current actual RB (DCCT1)
            mainI_pvrb2 = 'SR:C26-MG{PS:HEX-Main}I:Ps1DCCT2-I' # main current actual RB (DCCT2)
            # Main current loopback (The current value the regulartor wants,
            # but this value and the actual DCCT values may start diverge a lot,
            # if the main current is below 25 A and ramping down. In this case,
            # reducing the ramp rate to 0.1 A/s should keep the divergence minimal.)
            mainI_pvloopback = 'SR:C26-MG{PS:HEX-Main}I:Ps1DAC-I'
            #
            # "mainI_speed" [A/s] (max 1 A/s, but recommended to use 0.5 A/s
            # up to 400 A, and then 0.25 A/s above 400 A. According to T. Tanabe,
            # 1 A/s would be probably fine up to 300 A without quenching, but above
            # that current, the speed should be slowed down.)
            mainI_speed_pvsp = 'SR:C26-MG{PS:HEX-Main}Rate:Rmp1-SP' # main current ramp rate SP
            #
            # "mainI_ramping": 0 means "not ramping"; 1 means "ramping".
            mainI_ramping_pvrb = 'SR:C26-MG{PS:HEX-Main}RpStart1-Cmd'

            # Sequencer state control PV
            # [0 := Sequencer is On ("mainI_raw_pvsp" & "mainI_speed_pvsp"
            #       will be controlled by Y. Tian's sequencer)
            #  1 := Sequener is Off (can control "mainI_raw_pvsp" &
            #       "mainI_speed_pvsp" independently)]
            mainI_seq_sel_pvsp = 'SR:C26-MG{PS:HEX-Main}SequencerSel'

            # Quench detection status [0: good, 1: bad]
            qd_status_pvrb = 'SR:C26-MG{PS:QD}QDOut-Sts'

            # Main Coil PS On/Off [0: Off, 1: On]
            mainI_on_pvsp = 'SR:C26-MG{PS:HEX-Main}PsOnOff-Sel'

            # Main Coil PS Progress [0: 'DONE', 1: 'Go! Pls wait...']
            mainI_ps_status_pvrb = 'SR:C26-MG{PS:HEX-Main}PsOnOff-Sts'

            # CryoInt [0 (Good): 'CryoInt Low', 1 (Bad): 'CryoInt High']
            cryo_status_pvrb = 'SR:C26-MG{PS:QD}CryoInt-Sts'

            for fld in ['mainI', 'By']:
                fld_d = {}
                get_d = dict(pv=mainI_pvrb1) # Use DCCT1 for main readback
                fld_d['get'] = get_d
                put_d = dict(pv=mainI_pvsp)
                fld_d['put'] = put_d
                new['map'][fld] = fld_d

            for fld in ['mainI_expert', 'By_expert']:
                fld_d = {}
                get_d = dict(pv=mainI_pvrb1) # Use DCCT1 for main readback
                fld_d['get'] = get_d
                put_d = dict(pv=mainI_raw_pvsp)
                fld_d['put'] = put_d
                new['map'][fld] = fld_d

            for fld, pvrb in {'dcct1': mainI_pvrb1,
                            'dcct2': mainI_pvrb2,
                            'loopback': mainI_pvloopback,
                            'qd_status': qd_status_pvrb,
                            'mainI_ps_status': mainI_ps_status_pvrb,
                            'cryo_status': cryo_status_pvrb,
                            'mainI_ramping': mainI_ramping_pvrb,
                            }.items():
                fld_d = {}
                get_d = dict(pv=pvrb)
                fld_d['get'] = get_d
                new['map'][fld] = fld_d

            for fld, pvsp in {'mainI_speed': mainI_speed_pvsp,
                              'mainI_on': mainI_on_pvsp,
                              'mainI_seq_sel': mainI_seq_sel_pvsp
                              }.items():
                fld_d = {}
                put_d = dict(pv=pvsp)
                fld_d['put'] = put_d
                new['map'][fld] = fld_d



            idcor_pv_prefix = 'SR:C26-MG{PS:HEX-IDMPS}'

            cch_eps = 0.05

            for iCh in range(6): # +/-10 Amp
                fld = f'cch{iCh}'
                fld_d = {}
                get_d = dict(pv=f'{idcor_pv_prefix}U{iCh+1}-I-I', epsilon=cch_eps)
                fld_d['get'] = get_d
                put_d = dict(pv=f'{idcor_pv_prefix}U{iCh+1}-I-SP', epsilon=cch_eps)
                fld_d['put'] = put_d
                new['map'][fld] = fld_d

                fld = f'cch[{iCh}]'
                fld_d = {}
                get_d = dict(pv=f'{idcor_pv_prefix}U{iCh+1}-I-I', epsilon=cch_eps)
                fld_d['get'] = get_d
                new['map'][fld] = fld_d

            # ### For readback fields: "cch6", "cch7", "cch8", "cch9" ###
            # These readbacks are for the sum PVs, not just for the 2nd setpoint
            # channels, so the setpoint and readback will always differ significantly.
            for iCh, pvsp, pvrb in [
                # Upstream reg. H slow cor. 2nd channel
                (6, 'SR:C26-MG{PS:CL1B}I:Sp1_2-SP', 'SR:C26-MG{PS:CL1B}I:Ps1DCCT1-I'),
                # Upstream reg. V slow cor. 2nd channel
                (7, 'SR:C26-MG{PS:CL1B}I:Sp2_2-SP', 'SR:C26-MG{PS:CL1B}I:Ps2DCCT1-I'),
                # Downstream reg. H slow cor. 2nd channel
                (8, 'SR:C27-MG{PS:CL1A}I:Sp1_2-SP', 'SR:C27-MG{PS:CL1A}I:Ps1DCCT1-I'),
                # Downstream reg. V slow cor. 2nd channel
                (9, 'SR:C27-MG{PS:CL1A}I:Sp2_2-SP', 'SR:C27-MG{PS:CL1A}I:Ps2DCCT1-I'),
                ]:

                fld = f'cch{iCh}'
                fld_d = {}
                get_d = dict(pv=pvrb)
                fld_d['get'] = get_d
                put_d = dict(pv=pvsp)
                fld_d['put'] = put_d
                new['map'][fld] = fld_d

                fld = f'cch[{iCh}]'
                fld_d = {}
                get_d = dict(pv=pvrb)
                fld_d['get'] = get_d
                new['map'][fld] = fld_d

            # Orbit feedforwad PVs
            output_cor_pvsps = [f'SR:C26-MG{{PS:HEX-IDMPS}}U{i}-I-SP'
                                for i in range(1, 6+1)] + [
                                'SR:C26-MG{PS:CL1B}I:Sp1_2-SP',
                                'SR:C26-MG{PS:CL1B}I:Sp2_2-SP',
                                'SR:C27-MG{PS:CL1A}I:Sp1_2-SP',
                                'SR:C27-MG{PS:CL1A}I:Sp2_2-SP'
                                ]
            for i in range(10):
                pv_prefix = f'SR:C26-MG{{HEX:Orbit-FF:{i}}}'

                fld_d = {}
                put_d = dict(pv=f'{pv_prefix}Ena-Sel')
                fld_d['put'] = put_d
                new['map'][f'orbff{i}_on'] = fld_d

                fld_d = {}
                put_d = dict(pv=f'{pv_prefix}L2-Calc_.C')
                fld_d['put'] = put_d
                new['map'][f'orbff{i}_m0_mainI'] = fld_d

                fld_d = {}
                put_d = dict(pv=f'{pv_prefix}L2-Calc_.D')
                fld_d['put'] = put_d
                new['map'][f'orbff{i}_m0_I'] = fld_d

                fld_d = {}
                put_d = dict(pv=output_cor_pvsps[i])
                fld_d['put'] = put_d
                new['map'][f'orbff{i}_output'] = fld_d

            # Second PV channels of nearby quads that are used to correct linear optics
            # ### For readback fields: "qch0" thru "qch5" ###
            # These readbacks are for the sum PVs, not just for the 2nd setpoint
            # channels, so the setpoint and readback will always differ significantly.
            quad_pvsps = ['SR:C26-MG{PS:QL1B}I:Sp1_2-SP',
                          'SR:C26-MG{PS:QL2B}I:Sp1_2-SP',
                          'SR:C26-MG{PS:QL3B}I:Sp1_2-SP',
                          'SR:C27-MG{PS:QL1A}I:Sp1_2-SP',
                          'SR:C27-MG{PS:QL2A}I:Sp1_2-SP',
                          'SR:C27-MG{PS:QL3A}I:Sp1_2-SP']
            quad_pvrbs = ['SR:C26-MG{PS:QL1B}I:Ps1DCCT1-I',
                          'SR:C26-MG{PS:QL2B}I:Ps1DCCT1-I',
                          'SR:C26-MG{PS:QL3B}I:Ps1DCCT1-I',
                          'SR:C27-MG{PS:QL1A}I:Ps1DCCT1-I',
                          'SR:C27-MG{PS:QL2A}I:Ps1DCCT1-I',
                          'SR:C27-MG{PS:QL3A}I:Ps1DCCT1-I']
            for iCh, (pvsp, pvrb) in enumerate(zip(quad_pvsps, quad_pvrbs)):
                fld = f'qch{iCh}'
                fld_d = {}
                get_d = dict(pv=pvrb)
                fld_d['get'] = get_d
                put_d = dict(pv=pvsp)
                fld_d['put'] = put_d
                new['map'][fld] = fld_d

                fld = f'qch[{iCh}]'
                fld_d = {}
                get_d = dict(pv=pvrb)
                fld_d['get'] = get_d
                new['map'][fld] = fld_d

            # Linear-Optics feedforwad PVs
            output_quad_pvsps = quad_pvsps
            for i in range(6):
                pv_prefix = f'SR:C26-MG{{HEX:Tune-FF:{i}}}'
                fld_d = {}
                put_d = dict(pv=f'{pv_prefix}Ena-Sel')
                fld_d['put'] = put_d
                new['map'][f'linoptff{i}_on'] = fld_d

                fld_d = {}
                put_d = dict(pv=f'{pv_prefix}L2-Calc_.C')
                fld_d['put'] = put_d
                new['map'][f'linoptff{i}_m0_mainI'] = fld_d

                fld_d = {}
                put_d = dict(pv=f'{pv_prefix}L2-Calc_.D')
                fld_d['put'] = put_d
                new['map'][f'linoptff{i}_m0_I'] = fld_d
                # Even though strictly speaking, this table should contain
                # "delta_K" to account for nonlinear relation between the quad
                # PS current and integrated field strength "K". But the expected
                # PS current change is small enough that "K" and PS "I" should
                # be roughly linear. So, we are using "I" for the table.

                fld_d = {}
                put_d = dict(pv=output_quad_pvsps[i])
                fld_d['put'] = put_d
                new['map'][f'linoptff{i}_output'] = fld_d

        else:
            raise NotImplementedError

        d[elem_name] = new

    with gzip.GzipFile(ELEM_PV_MV_PGZ_FILEPATHS['SR'], 'wb') as f:
        pickle.dump(d, f)

def add_C27_HEX_unitconv_table_for_mainI_vs_By_Tesla():

    unitconv_pkl_filepath = '../v2tests/nsls2sr_unitconv_tables.pkl'

    with open(unitconv_pkl_filepath, 'rb') as f:
        d = pickle.load(f)

    d['SR']['scw70g1c27d_mainI_vs_By_Tesla'] = np.flipud(
        np.fliplr(
        [
         [4.3+(500-434)/(434-390)*(4.3-4.0), 500.0], # linear interpolation
         [4.34, 440.0],
         [4.3, 434.0],
         [4.0, 390.0],
         [3.5, 320.0],
         [3.0, 250.0],
         [2.5, 186.0],
         [2.0, 127.0],
         [1.5, 74.0],
         [1.0, 34.0],
         [0.5, 17.0],
         [0.0, 0.0],
         ]
    ))

    with open(unitconv_pkl_filepath, 'wb') as f:
        pickle.dump(d, f)


def add_2nd_channels_to_C27_HEX_FF_quads(exist_ok=False):

    d = get_elem_pv_mv_pgz_database_dict('SR')

    scw = ap.getElements('scw*c27*')[0]
    sel_quads = ap.getNeighbors(scw, 'ql*', n=3, elemself=False)

    for e in sel_quads:
        if (not exist_ok) and ('b1_2nd' in d[e.name]['map']):
            print(f'Field "b1_2nd" already defined for "{e.name}". Not changing.')
            continue
        primary_pvsp = d[e.name]['map']['b1']['put']['pv']
        put_d = dict(pv=primary_pvsp.replace('I:Sp1-', 'I:Sp1_2-'))
        fld_d = {}
        fld_d['put'] = put_d
        d[e.name]['map']['b1_2nd'] = fld_d

    with gzip.GzipFile(ELEM_PV_MV_PGZ_FILEPATHS['SR'], 'wb') as f:
        pickle.dump(d, f)

def add_2nd_channels_to_C27_HEX_cch6thru9(exist_ok=False):

    d = get_elem_pv_mv_pgz_database_dict('SR')

    scw = ap.getElements('scw*c27*')[0]
    sel_scors = ap.getNeighbors(scw, 'cl*', n=1, elemself=False)

    for plane in ['x', 'y']:
        for e in sel_scors:
            if (not exist_ok) and (f'{plane}_2nd' in d[e.name]['map']):
                print(f'Field "{plane}_2nd" already defined for "{e.name}". Not changing.')
                continue
            primary_pvsp = d[e.name]['map'][plane]['put']['pv']
            if plane == 'x':
                put_d = dict(pv=primary_pvsp.replace('I:Sp1-', 'I:Sp1_2-'))
            elif plane == 'y':
                put_d = dict(pv=primary_pvsp.replace('I:Sp2-', 'I:Sp2_2-'))
            else:
                raise ValueError
            put_d['epsilon'] = 0.01
            mv_copy = json.loads(json.dumps(d[e.name]['map'][plane]['put']['mv']))
            mv_copy['pyelegant']['property'][1] = 1
            mv_copy['pyelegant']['property'] = tuple(mv_copy['pyelegant']['property'])
            put_d['mv'] = mv_copy
            fld_d = {}
            fld_d['put'] = put_d
            d[e.name]['map'][f'{plane}_2nd'] = fld_d

    with gzip.GzipFile(ELEM_PV_MV_PGZ_FILEPATHS['SR'], 'wb') as f:
        pickle.dump(d, f)

if __name__ == '__main__':

    if False: # Run on 01/14/2022

        if False: # Run on 01/14/2022
            # This WILL modify the database file. Be careful.
            update_C23u_BNL_PSI_upgrade()

        # Also manually confirmed that these new setpoint PVs have
        # .DRVL and .DRVH, which are needed for the orbit feedforward script to
        # work correctly. Just run the following section.
        if True: # Run on 01/14/2022
            id_list = ap.getElements('epu49g1c23u')
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
        # DRVL & DRVH had to be adjusted from +/-10 to +/-8.0001
        if False: # Run on 05/16/2022
            from cothread.catools import caput

            id_list = ap.getElements('epu49g1c23u')
            for idobj in id_list:
                print(idobj.name)
                for iCh in range(6):
                    try:
                        pv = idobj.pv(field='cch{0:d}'.format(iCh), handle='setpoint')[0]
                        caput(f'{pv}.DRVL', -8.0001)
                        caput(f'{pv}.DRVH', +8.0001)
                        print(caget([pv+'.DRVL', pv+'.DRVH']))
                    except IndexError:
                        break
                    except:
                        raise

    elif False: # Run on 05/16/2022

        if False: # Run on 05/16/2022
            # This WILL modify the database file. Be careful.
            update_C23d_BNL_PSI_upgrade()

        # Also manually confirmed that these new setpoint PVs have
        # .DRVL and .DRVH, which are needed for the orbit feedforward script to
        # work correctly. Just run the following section.
        if True: # Run on 05/16/2022
            id_list = ap.getElements('epu49g1c23d')
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
        # DRVL & DRVH had to be adjusted from +/-10 to +/-8.0001
        if False: # Run on 05/16/2022
            from cothread.catools import caput

            id_list = ap.getElements('epu49g1c23d')
            for idobj in id_list:
                print(idobj.name)
                for iCh in range(6):
                    try:
                        pv = idobj.pv(field='cch{0:d}'.format(iCh), handle='setpoint')[0]
                        caput(f'{pv}.DRVL', -8.0001)
                        caput(f'{pv}.DRVH', +8.0001)
                        print(caget([pv+'.DRVL', pv+'.DRVH']))
                    except IndexError:
                        break
                    except:
                        raise

    elif False: # Run on 11/03/2022
        add_2nd_channels_to_C27_HEX_FF_quads(exist_ok=False)

    elif False: # Run on 11/11/2022
        update_C27_straight(exist_ok=False)

    elif False: # Run on 11/08/2022
        add_C27_HEX_unitconv_table_for_mainI_vs_By_Tesla()

    elif False: # Run on 11/23/2022
        add_2nd_channels_to_C27_HEX_cch6thru9(exist_ok=False)

    elif True: # Last run on 11/23/2022
        save_pgz_db_contents_to_json(machine_list=['SR'])

    print('Finished')