'''
This script should be run in a v2-aphla environment.

Convert the contents of /epics/aphla/apconf/nsls2/nsls2_bts.sqlite as of
02/18/2020 into a dict in a gzipped pickled file for aphla v2.
'''

import pickle
import gzip
from pprint import pprint
import shutil

#from cothread.catools import caget
#import pyelegant as pe

#LTE = pe.ltemanager.Lattice(
    #LTE_filepath='/home/yhidaka/git_repos/aphla/utils/20190125_VS_nsls2sr17idsmt_SQLC16.lte',
    #used_beamline_name='RING')
#flat_used_elem_names = LTE.get_used_beamline_element_defs()['flat_used_elem_names']

submachine_name = 'BTS'

# While running "interactive_sqlite_rows_saving.py" interactively, which calls
# "ap.machines.load('nsls2', submachine_name)", within load() in
# aphla/machines/__init__.py, right after "cfa.loadSqlite(accsqlite)" was
# exectuted, the contents of the list "cfa.rows" was manually saved into the
# following pgz file:
nsls2_sqlite_rows_pgz_file = f'nsls2_{submachine_name.lower()}_sqlite_rows.pgz'
with gzip.GzipFile(nsls2_sqlite_rows_pgz_file, 'rb') as f:
    cfa_rows = pickle.load(f)

# v1 aphla unit conversion file: /epics/aphla/apconf/nsls2/bts_unitconv.hdf5

#>> ap.getGroups()
#['COR', 'BEND', 'MONI', 'FLAG', 'BPM', 'WATCH', 'HCOR', 'VCOR', 'QUAD',
 #'MARK', 'TWISS', 'HLA:VIRTUAL']

# >> bpms = ap.getElements('BPM')
# >> e = bpms[0]
# >> [(fld, e._field[fld].pvrb) for fld in e.fields()]
#[('x', ['BTS-BI{BPM:1}Pos:X-I']),
# ('y', ['BTS-BI{BPM:1}Pos:Y-I'])]


# >> [(fld, e._field[fld].pvsp) for fld in e.fields()]
#[('x', []), ('y', [])]

print(set([t for pv, elem_def, tags in cfa_rows for t in tags]))
# Output: {'aphla.sys.BTS'}
print([tags for pv, elem_def, tags in cfa_rows if tags != ['aphla.sys.BTS']])
# Output: [[], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], []]
print([pv for pv, elem_def, tags in cfa_rows if tags != ['aphla.sys.BTS']])
# Output: ['', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '']
print([elem_def for pv, elem_def, tags in cfa_rows if tags != ['aphla.sys.BTS']])
# Output:
#[
    #{
        #'id': 1,
        #'elemName': 'BRCX1SE',
        #'elemType': 'COR',
        #'elemLength': 0.134,
        #'elemPosition': 0.227,
        #'elemIndex': 300,
        #'virtual': 0,
    #},
    #{
        #'id': 2,
        #'elemName': 'BRBU1SE',
        #'elemType': 'BEND',
        #'elemLength': 0.166,
        #'elemPosition': 0.453,
        #'elemIndex': 500,
        #'virtual': 0,
    #},
    #{
        #'id': 3,
        #'elemName': 'BRK1SE',
        #'elemType': 'BEND',
        #'elemLength': 0.200638,
        #'elemPosition': 0.833643,
        #'elemIndex': 700,
        #'virtual': 0,
    #},
    #{
        #'id': 4,
        #'elemName': 'BRK2SE',
        #'elemType': 'BEND',
        #'elemLength': 0.200641,
        #'elemPosition': 1.20366,
        #'elemIndex': 900,
        #'virtual': 0,
    #},
    #{
        #'id': 5,
        #'elemName': 'BRK3SE',
        #'elemType': 'BEND',
        #'elemLength': 0.200644,
        #'elemPosition': 1.573682,
        #'elemIndex': 1100,
        #'virtual': 0,
    #},
    #{
        #'id': 6,
        #'elemName': 'BRK4SE',
        #'elemType': 'BEND',
        #'elemLength': 0.200648,
        #'elemPosition': 1.943711,
        #'elemIndex': 1300,
        #'virtual': 0,
    #},
    #{
        #'id': 7,
        #'elemName': 'BRP1SE',
        #'elemType': 'MONI',
        #'elemLength': 0.0,
        #'elemPosition': 2.345117,
        #'elemIndex': 1500,
        #'virtual': 0,
    #},
    #{
        #'id': 8,
        #'elemName': 'BRBU2SE',
        #'elemType': 'BEND',
        #'elemLength': 0.166,
        #'elemPosition': 2.658131,
        #'elemIndex': 1700,
        #'virtual': 0,
    #},
    #{
        #'id': 10,
        #'elemName': 'BRSP1SE',
        #'elemType': 'BEND',
        #'elemLength': 0.6,
        #'elemPosition': 4.060144,
        #'elemIndex': 2100,
        #'virtual': 0,
    #},
    #{
        #'id': 13,
        #'elemName': 'FT1',
        #'elemType': 'WATCH',
        #'elemLength': 0.0,
        #'elemPosition': 6.399974,
        #'elemIndex': 2700,
        #'virtual': 0,
    #},
    #{
        #'id': 35,
        #'elemName': 'M1',
        #'elemType': 'MARK',
        #'elemLength': 0.0,
        #'elemPosition': 22.90441,
        #'elemIndex': 7500,
        #'virtual': 0,
    #},
    #{
        #'id': 44,
        #'elemName': 'ESLIT',
        #'elemType': 'WATCH',
        #'elemLength': 0.0,
        #'elemPosition': 29.88569,
        #'elemIndex': 9200,
        #'virtual': 0,
    #},
    #{
        #'id': 49,
        #'elemName': 'FT2',
        #'elemType': 'WATCH',
        #'elemLength': 0.0,
        #'elemPosition': 36.82744,
        #'elemIndex': 10200,
        #'virtual': 0,
    #},
    #{
        #'id': 50,
        #'elemName': 'IT1',
        #'elemType': 'WATCH',
        #'elemLength': 0.0,
        #'elemPosition': 37.01984,
        #'elemIndex': 10400,
        #'virtual': 0,
    #},
    #{
        #'id': 61,
        #'elemName': 'ISP3',
        #'elemType': 'MONI',
        #'elemLength': 0.0,
        #'elemPosition': 44.61924,
        #'elemIndex': 12600,
        #'virtual': 0,
    #},
    #{
        #'id': 62,
        #'elemName': 'ISP4',
        #'elemType': 'MONI',
        #'elemLength': 0.0,
        #'elemPosition': 44.67639,
        #'elemIndex': 12800,
        #'virtual': 0,
    #},
    #{
        #'id': 63,
        #'elemName': 'ISBU3',
        #'elemType': 'BEND',
        #'elemLength': 0.65,
        #'elemPosition': 45.67389,
        #'elemIndex': 13000,
        #'virtual': 0,
    #},
    #{
        #'id': 64,
        #'elemName': 'ISP5',
        #'elemType': 'MONI',
        #'elemLength': 0.0,
        #'elemPosition': 45.98152,
        #'elemIndex': 13200,
        #'virtual': 0,
    #},
    #{
        #'id': 65,
        #'elemName': 'ISBU4',
        #'elemType': 'BEND',
        #'elemLength': 0.65,
        #'elemPosition': 47.55389,
        #'elemIndex': 13400,
        #'virtual': 0,
    #},
    #{
        #'id': 68,
        #'elemName': 'twiss',
        #'elemType': 'TWISS',
        #'elemLength': 0.0,
        #'elemPosition': 0.0,
        #'elemIndex': -100,
        #'virtual': 1,
    #},
#]

# Output when run in v1-aphla env for: [e.name for e in ap.getElements('*')]
v1aphal_elem_names = [
    'BRCX1SE', 'BRBU1SE', 'BRK1SE', 'BRK2SE', 'BRK3SE', 'BRK4SE', 'BRP1SE',
    'BRBU2SE', 'VF1', 'BRSP1SE', 'P1', 'SP2', 'FT1', 'C1', 'Q1', 'VF2', 'Q2',
    'B1', 'Q3', 'C2', 'B2', 'P2', 'Q4', 'C3', 'P3', 'VF3', 'Q5', 'VF4', 'P4',
    'Q6', 'C4', 'Q7', 'VF5', 'Q8', 'M1', 'B3', 'Q9', 'C5', 'P5', 'Q10', 'B4',
    'C6', 'Q11', 'ESLIT', 'Q12', 'P6', 'VF6', 'C7', 'FT2', 'IT1', 'P7', 'VF7',
    'Q13', 'Q14', 'C8', 'SP3', 'C9', 'P8', 'IS', 'ISVF1', 'ISP3', 'ISP4',
    'ISBU3', 'ISP5', 'ISBU4']

print([elem_def['elemName'] in v1aphal_elem_names
       for pv, elem_def, tags in cfa_rows if tags != ['aphla.sys.BTS']])
# Output: [True, True, True, True, True, True, True, True, True, True, True,
#          True, True, True, True, True, True, True, True, False]

# Confirm that there are no sys-tagged rows for the elements for which
# there are rows without tags but the corresponding elements exist in
# v1-aphla. (These v1-aphla elements has no fields and PVs associated, but
# they are still there, so I'll be keeping them in v2-aphla as well the same way.)
no_systag_elem_defs = [
    elem_def for pv, elem_def, tags in cfa_rows
    if (tags != ['aphla.sys.BTS']) and
    (elem_def['elemName'] in v1aphal_elem_names) # <- removing def for "twiss" element
]
counts = {elem_def['elemName']: 0 for elem_def in no_systag_elem_defs}
for elem_def in no_systag_elem_defs:
    elem_name = elem_def['elemName']
    for _, _elem_def, _tags in cfa_rows:
        if _elem_def['elemName'] == elem_name:
            counts[elem_name] += 1
            assert _tags == []
assert all([n == 1 for k, n in counts.items()])

# Only remove the row for the "twiss" element, which doesn't exist either in v1-aphla
cfa_rows = [[pv, elem_def, tags] for pv, elem_def, tags in cfa_rows
            if elem_def['elemName'] in v1aphal_elem_names]

assert [elem_def['elemField'] for pv, elem_def, tags in cfa_rows
        if ('elemField' in elem_def) and ('[' in elem_def['elemField'])] == []

root = {}
submachine = root[submachine_name] = {}
tags_list = []
for pv, elem_def, tags in cfa_rows:
    tags_list.append(tuple(tags))

    elemName = elem_def.pop('elemName')

    if pv.strip():
        field = elem_def.pop('elemField')

        handle = elem_def.pop('elemHandle')
        assert handle in ('get', 'put')

        epsilon = elem_def.pop('epsilon', None)

        if elemName not in submachine:
            elem = submachine[elemName] = {k: v for k, v in elem_def.items()}
            elem['map'] = {}
            elem['tags'] = tags
        else:
            elem = submachine[elemName]
            for k, v in elem_def.items():
                if k in elem:
                    assert elem[k] == v
                else:
                    # If there are mistakes in the original SQLite file, correct
                    # the data here
                    pass
                    #if (elemName == 'pu4g1c19a') and (k == 'devName'):
                        #assert v == 'C19-BPM8'
                        #elem[k] = 'C19-BPM10'
                    #else: # If there is no mistake in the original SQLite file
                        #elem[k] = v

        ## Remove unidentified/unwanted elements
        #if elem_def['elemType'] == 'UCOR_':
            ## It looks like these are canting magnet elements, but the associated
            ## PVs are disconnected. So, these elements are being removed here.
            #del submachine[elemName]
            #continue

        if field not in elem['map']:
            elem['map'][field] = {}
        if handle not in elem['map'][field]:
            elem['map'][field][handle] = {}

            elem['map'][field][handle]['mv'] = {}

        ## Prevent invalid PV definitions from overwriting
        #if (elemName == 'ivu20g1c03c') and (handle == 'put'):
            #if field in ('orbff0_output', 'orbff4_output'):
                #if pv.endswith('I:Sp1_2-SP'):
                    #continue
            #elif field in ('orbff1_output', 'orbff5_output'):
                #if pv.endswith('I:Sp2_2-SP'):
                    #continue

        # Avoid duplicate definitions
        for k in ['pv', 'epsilon']:
            try:
                assert k not in elem['map'][field][handle]
            except:
                print('-----------------------------')
                print(elemName, k, field, handle, pv)
                #pprint(elem)
                pprint(elem['map'][field])

                break

        ## Reject invalid PV definitions
        #if pv in ('_RF_V:I', '_RF_V:SP'):
            #continue
        #elif (elemName == 'rfcavity') and (field == 'v'):
            #continue # PV 'SR-RF{CFC:D}E:Fb-SP' does not seem to be a voltage.
                     ## Also, it would be dangerous to allow RF voltage change
                     ## from a script. So, this PV is being removed.
        #elif (elemName == 'rfcavity') and (field == 'phi'):
            #continue # PV 'SR-RF{CFC:D}Phs:Fb-SP' is being removed here, as it
                     ## would be probably dangerous to allow RF phase change
                     ## from a script.
        ##
        #elif (elemName == 'pu4g1c19a') and ('BPM:8' in pv): # Must be 'BPM:10'
            #continue
        ##
        #elif (elemName in ('dw100g1c08d',)) and \
             #(field in ('orbff0_output','orbff1_output','orbff2_output',
                        #'orbff3_output','orbff4_output','orbff5_output')) and \
             #(handle == 'put') and 'PS:DW2_ID08' in pv:
            #continue
        #elif (elemName in ('dw100g1c18d',)) and \
             #(field in ('orbff0_output','orbff1_output','orbff2_output',
                        #'orbff3_output','orbff4_output','orbff5_output')) and \
             #(handle == 'put') and 'PS:DW2_ID18' in pv:
            #continue
        ##
        #elif (elemName in ('epu57g1c02c', 'ivu20g1c03c', 'ivu23g1c04u',
                           #'ivu21g1c05d', 'ivu23g1c16c', 'ivu21g1c17u',
                           #'ivu21g1c17d', 'epu57g1c21u', 'epu105g1c21d')) and \
             #(field in ('cch0','cch1','cch2','cch3','cch4','cch5')) and \
             #(handle == 'get') and pv.endswith('Loop-I'):
            #continue
        #elif (elemName in ('ovu42g1c07u', 'epu60g1c07d', 'ivu22g1c10c')) and \
             #(field in ('cch0','cch1','cch2','cch3')) and \
             #(handle == 'get') and pv.endswith('Loop-I'):
            #continue
        #elif (elemName in ('ivu18g1c19u',)) and \
             #(field in ('cch0','cch1','cch2','cch3','cch4')) and \
             #(handle == 'get') and pv.endswith('Loop-I'):
            #continue
        #elif (elemName in ('ivu20g1c03c', 'ivu23g1c04u',
                           #'ivu21g1c05d', 'ivu23g1c16c', 'ivu21g1c17u',
                           #'ivu21g1c17d', )) and \
             #(field in ('cch[0]','cch[1]','cch[2]','cch[3]','cch[4]','cch[5]')) and \
             #(handle == 'get') and pv.endswith('Loop-I'):
            #continue
        #elif (elemName in ('ivu22g1c10c')) and \
             #(field in ('cch[0]','cch[1]','cch[2]','cch[3]')) and \
             #(handle == 'get') and pv.endswith('Loop-I'):
            #continue
        ##
        #elif (elemName == 'fh2g1c30a') and (field in ('x', 'y')) and \
             #(handle in ('put', 'get')) and pv.startswith('SR:C02-MG'):
            #continue
        #
        ##Reject disconnected PV definitions
        #elif (elem['elemType'] == 'COR') and (
            #field in ('mcblx', 'mckx', 'mcbly', 'mcky')):
            ## PVs offline as of 02/01/2021
            ##   'mcblx' like 'SR:C30-MG{PS:CH1A}BL:Ps1DCCT1-I'
            ##   'mckx' like 'SR:C30-MG{PS:CH1A}K:Ps1DCCT1-I'
            ##   'mcbly' like 'SR:C30-MG{PS:CH1A}BL:Ps2DCCT1-I'
            ##   'mcky' like 'SR:C30-MG{PS:CH1A}K:Ps2DCCT1-I'
            #continue

        ## Fix wrong/obsolete PVs to correct/updated PVs
        #if elem['elemType'] == 'TUNE':
            #if pv == 'SR:C16-BI{TuneNA}Freq:Vx-I':
                #pv = 'SR:OPS-BI{IGPF}FBX:Tune-I'
            #elif pv == 'SR:C16-BI{TuneNA}Freq:Vy-I':
                #pv = 'SR:OPS-BI{IGPF}FBY:Tune-I'
            #else:
                #raise ValueError

        elem['map'][field][handle]['pv'] = pv
        if epsilon:
            elem['map'][field][handle]['epsilon'] = epsilon

        # Add model variable (MV) information
        mv_d = dict(elem_name=elemName.upper())
        #if elem['elemType'] in ('BPM', 'UBPM_', '_BPM'):
            #mv_d['property'] = field
        #elif elem['elemType'] in ('XBPM_', 'CAMERA'):
            #pass # No corresponding elements in the model.
        #elif elem['elemType'] == 'BEND':
            #pass # For now, not allowed to change in the model
        #elif elem['elemType'] == 'QUAD':
            #mv_d['property'] = 'K1'
        #elif elem['elemType'] == 'SKQUAD':
            #mv_d['elem_name'] = mv_d['elem_name'].replace('HG', 'G')
            #mv_d['property'] = 'K1'
        #elif elem['elemType'] == 'SEXT':
            #mv_d['property'] = 'K2'
        #elif elem['elemType'] == 'COR':
            #if field == 'x':
                #mv_d['property'] = ('HKICK', 0) # [rad]
                #mv_d['elem_name'] = mv_d['elem_name'].replace('G', 'YG')
            #elif field == 'x_2nd':
                #mv_d['property'] = ('HKICK', 1) # [rad]
                #mv_d['elem_name'] = mv_d['elem_name'].replace('G', 'YG')
            #elif field == 'y':
                #mv_d['property'] = ('VKICK', 0) # [rad]
                #mv_d['elem_name'] = mv_d['elem_name'].replace('G', 'YG')
            #elif field == 'y_2nd':
                #mv_d['property'] = ('VKICK', 1) # [rad]
                #mv_d['elem_name'] = mv_d['elem_name'].replace('G', 'YG')
            #elif field in ('mcblx', 'mckx', 'mcbly', 'mcky'):
                #raise ValueError # Corresponding PVs are disconnected, and this
                                 ## should not be reachable.
            #elif field in ('ramping[0]', 'ramping[1]'):
                #mv_d['property'] = None # indicates "do nothing" to the model
                #if field.endswith('[0]'):
                    #mv_d['elem_name'] = mv_d['elem_name'].replace('G', 'YG')
                #elif field.endswith('[1]'):
                    #mv_d['elem_name'] = mv_d['elem_name'].replace('G', 'YG')
                #else:
                    #raise ValueError
            #else:
                #raise ValueError
        #elif elem['elemType'] == 'FCOR':
            #if field == 'x':
                #mv_d['property'] = 'HKICK' # [rad]
            #elif field == 'y':
                #mv_d['property'] = 'VKICK' # [rad]
            #elif field in ('mode', 'x2', 'y2', 'xjump', 'yjump'):
                #mv_d['property'] = None # indicates "do nothing" to the model
            #else:
                #raise ValueError
        #elif elem['elemType'] == 'RFCAVITY':
            #if field in ('f_hz', 'f'):
                #mv_d['property'] = 'FREQ' # [Hz]
            #elif field in ('v', 'phi'):
                #raise ValueError # Corresponding PVs should have been removed
                                 ## above and so this line should not be reachable.
            #else:
                #raise ValueError
            #mv_d['elem_name'] = 'RFC'
        ##
        #elif elem['elemType'] in ('DW', 'EPU', 'IVU', 'OVU'):
            #mv_d['property'] = None # indicates "do nothing" to the model
            #if elemName in ('epu57g1c02c',
                            #'ivu20g1c03c',
                            #'ivu23g1c04u',
                            #'ivu21g1c05d',
                            #'ovu42g1c07u',
                            #'epu60g1c07d',
                            #'ivu22g1c10c',
                            #'ivu20g1c11c',
                            #'ivu23g1c12d',
                            #'ivu23g1c16c',
                            #'ivu21g1c17u',
                            #'ivu21g1c17d',
                            #'ivu18g1c19u',
                            #'epu57g1c21u',
                            #'epu105g1c21d',
                            #'epu49g1c23u',
                            #'epu49g1c23d',
                            #):
                #mv_d['elem_name'] = f'{elemName.upper()}M'
            #elif elemName in (
                #'dw100g1c08u',
                #'dw100g1c08d',
                #'dw100g1c18u',
                #'dw100g1c18d',
                #'dw100g1c28u',
                #'dw100g1c28d',
                #):
                #mv_d['elem_name'] = elemName.upper()
            #else:
                #raise ValueError
        ##
        #elif elem['elemType'] == 'TUNE':
            #if field == 'x':
                #mv_d['property'] = 'NUX'
            #elif field == 'y':
                #mv_d['property'] = 'NUY'
            #else:
                #raise ValueError
            #mv_d['elem_name'] = '!TUNE'
        #elif elem['elemType'] == 'DCCT':
            #if field == 'tau':
                #mv_d['property'] = 'TAU' # [hr]
            #elif field in ('Iavg', 'I'):
                #mv_d['property'] = 'I' # [mA]
            #else:
                #raise ValueError
            #mv_d['elem_name'] = '!DCCT'
        #else:
            ##raise NotImplementedError
            #print(elemName, elem['elemType'], field, handle, pv)
        ##
        #if len(mv_d) != 1:
            #if not mv_d['elem_name'].startswith('!'):
                #assert mv_d['elem_name'] in flat_used_elem_names
            #elem['map'][field][handle]['mv']['pyelegant'] = mv_d

    else:
        assert 'elemField' not in elem_def
        assert 'elemHandle' not in elem_def

        assert elemName not in submachine

        elem = submachine[elemName] = {k: v for k, v in elem_def.items()}

print(set(tags_list))


nsls2_elems_pvs_mvs_pgz_file = f'nsls2_{submachine_name.lower()}_elems_pvs_mvs.pgz'
with gzip.GzipFile(nsls2_elems_pvs_mvs_pgz_file, 'wb') as f:
    pickle.dump(root[submachine_name], f)
shutil.copy(nsls2_elems_pvs_mvs_pgz_file,
            f'/epics/aphla/apconf/nsls2/{nsls2_elems_pvs_mvs_pgz_file}')

#with gzip.GzipFile(nsls2_elems_pvs_mvs_pgz_file, 'rb') as f:
    #loaded_submachine = pickle.load(f)

print('Finished')