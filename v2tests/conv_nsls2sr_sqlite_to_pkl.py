'''
Convert the contents of /epics/aphla/apconf/nsls2/nsls2_sr.sqlite as of
12/09/2020 into a dict in a gzipped pickled file for aphla v2.
'''

import pickle
import gzip
from pprint import pprint
import shutil

from cothread.catools import caget
import pyelegant as pe

LTE = pe.ltemanager.Lattice(
    LTE_filepath='/home/yhidaka/git_repos/aphla/utils/20190125_VS_nsls2sr17idsmt_SQLC16.lte',
    used_beamline_name='RING')
flat_used_elem_names = LTE.get_used_beamline_element_defs()['flat_used_elem_names']

# While running "ap.machines.load('nsls2', 'SR')" interactively, within load()
# in aphla/machines/__init__.py, right after "cfa.loadSqlite(accsqlite)" was
# exectuted, the contents of the list "cfa.rows" was manually saved into the
# following pgz file:
#
# with gzip.GzipFile(nsls2_sr_sqlite_rows_pgz_file, 'wb') as f:
#     pickle.dump(cfa.rows, f)
nsls2_sr_sqlite_rows_pgz_file = 'nsls2_sr_sqlite_rows.pgz'
with gzip.GzipFile(nsls2_sr_sqlite_rows_pgz_file, 'rb') as f:
    cfa_rows = pickle.load(f)

root = {}
submachine = root['SR'] = {}
tags_list = []
for pv, elem_def, tags in cfa_rows:
    tags_list.append(tuple(tags))

    elemName = elem_def.pop('elemName')

    if pv.strip():
        field = elem_def.pop('elemField')

        # Must exclude the "list" field names (e.g.,
        #   cch := [cch[0], cch[1], ..., cch[5]])
        if field in ('cch', 'cscch'):
            continue

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
                    if (elemName == 'pu4g1c19a') and (k == 'devName'):
                        assert v == 'C19-BPM8'
                        elem[k] = 'C19-BPM10'
                    else: # If there is no mistake in the original SQLite file
                        elem[k] = v

        # Remove unidentified/unwanted elements
        if elem_def['elemType'] == 'UCOR_':
            # It looks like these are canting magnet elements, but the associated
            # PVs are disconnected. So, these elements are being removed here.
            del submachine[elemName]
            continue

        if field not in elem['map']:
            elem['map'][field] = {}
        if handle not in elem['map'][field]:
            elem['map'][field][handle] = {}

            elem['map'][field][handle]['mv'] = {}

        # Prevent invalid PV definitions from overwriting
        if (elemName == 'ivu20g1c03c') and (handle == 'put'):
            if field in ('orbff0_output', 'orbff4_output'):
                if pv.endswith('I:Sp1_2-SP'):
                    continue
            elif field in ('orbff1_output', 'orbff5_output'):
                if pv.endswith('I:Sp2_2-SP'):
                    continue

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

        # Reject invalid PV definitions
        if pv in ('_RF_V:I', '_RF_V:SP'):
            continue
        elif (elemName == 'rfcavity') and (field == 'v'):
            continue # PV 'SR-RF{CFC:D}E:Fb-SP' does not seem to be a voltage.
                     # Also, it would be dangerous to allow RF voltage change
                     # from a script. So, this PV is being removed.
        elif (elemName == 'rfcavity') and (field == 'phi'):
            continue # PV 'SR-RF{CFC:D}Phs:Fb-SP' is being removed here, as it
                     # would be probably dangerous to allow RF phase change
                     # from a script.
        #
        elif (elemName == 'pu4g1c19a') and ('BPM:8' in pv): # Must be 'BPM:10'
            continue
        #
        elif (elemName in ('dw100g1c08d',)) and \
             (field in ('orbff0_output','orbff1_output','orbff2_output',
                        'orbff3_output','orbff4_output','orbff5_output')) and \
             (handle == 'put') and 'PS:DW2_ID08' in pv:
            continue
        elif (elemName in ('dw100g1c18d',)) and \
             (field in ('orbff0_output','orbff1_output','orbff2_output',
                        'orbff3_output','orbff4_output','orbff5_output')) and \
             (handle == 'put') and 'PS:DW2_ID18' in pv:
            continue
        #
        elif (elemName in ('epu57g1c02c', 'ivu20g1c03c', 'ivu23g1c04u',
                           'ivu21g1c05d', 'ivu23g1c16c', 'ivu21g1c17u',
                           'ivu21g1c17d', 'epu57g1c21u', 'epu105g1c21d')) and \
             (field in ('cch0','cch1','cch2','cch3','cch4','cch5')) and \
             (handle == 'get') and pv.endswith('Loop-I'):
            continue
        elif (elemName in ('ovu42g1c07u', 'epu60g1c07d', 'ivu22g1c10c')) and \
             (field in ('cch0','cch1','cch2','cch3')) and \
             (handle == 'get') and pv.endswith('Loop-I'):
            continue
        elif (elemName in ('ivu18g1c19u',)) and \
             (field in ('cch0','cch1','cch2','cch3','cch4')) and \
             (handle == 'get') and pv.endswith('Loop-I'):
            continue
        elif (elemName in ('ivu20g1c03c', 'ivu23g1c04u',
                           'ivu21g1c05d', 'ivu23g1c16c', 'ivu21g1c17u',
                           'ivu21g1c17d', )) and \
             (field in ('cch[0]','cch[1]','cch[2]','cch[3]','cch[4]','cch[5]')) and \
             (handle == 'get') and pv.endswith('Loop-I'):
            continue
        elif (elemName in ('ivu22g1c10c')) and \
             (field in ('cch[0]','cch[1]','cch[2]','cch[3]')) and \
             (handle == 'get') and pv.endswith('Loop-I'):
            continue
        #
        elif (elemName == 'fh2g1c30a') and (field in ('x', 'y')) and \
             (handle in ('put', 'get')) and pv.startswith('SR:C02-MG'):
            continue
        elif (elemName == 'fm1g4c30a') and (field in ('x', 'y')) and \
             (handle in ('put', 'get')) and pv.startswith('SR:C01-MG'):
            continue
        elif (elemName == 'fl1g1c01a') and (field in ('x', 'y')) and \
             (handle in ('put', 'get')) and pv.startswith('SR:C02-MG'):
            continue
        elif (elemName == 'fm1g4c01a') and (field in ('x', 'y')) and \
             (handle in ('put', 'get')) and pv.startswith('SR:C02-MG'):
            continue
        elif (elemName == 'fh2g1c02a') and (field in ('x', 'y')) and \
             (handle in ('put', 'get')) and pv.startswith('SR:C04-MG'):
            continue
        elif (elemName == 'fm1g4c02a') and (field in ('x', 'y')) and \
             (handle in ('put', 'get')) and pv.startswith('SR:C03-MG'):
            continue
        elif (elemName == 'fl1g1c03a') and (field in ('x', 'y')) and \
             (handle in ('put', 'get')) and pv.startswith('SR:C04-MG'):
            continue
        elif (elemName == 'fm1g4c03a') and (field in ('x', 'y')) and \
             (handle in ('put', 'get')) and pv.startswith('SR:C04-MG'):
            continue
        elif (elemName == 'fh2g1c04a') and (field in ('x', 'y')) and \
             (handle in ('put', 'get')) and pv.startswith('SR:C06-MG'):
            continue
        elif (elemName == 'fm1g4c04a') and (field in ('x', 'y')) and \
             (handle in ('put', 'get')) and pv.startswith('SR:C05-MG'):
            continue
        elif (elemName == 'fl1g1c05a') and (field in ('x', 'y')) and \
             (handle in ('put', 'get')) and pv.startswith('SR:C06-MG'):
            continue
        elif (elemName == 'fm1g4c05a') and (field in ('x', 'y')) and \
             (handle in ('put', 'get')) and pv.startswith('SR:C06-MG'):
            continue
        elif (elemName == 'fh2g1c06a') and (field in ('x', 'y')) and \
             (handle in ('put', 'get')) and pv.startswith('SR:C08-MG'):
            continue
        elif (elemName == 'fm1g4c06a') and (field in ('x', 'y')) and \
             (handle in ('put', 'get')) and pv.startswith('SR:C07-MG'):
            continue
        elif (elemName == 'fl1g1c07a') and (field in ('x', 'y')) and \
             (handle in ('put', 'get')) and pv.startswith('SR:C08-MG'):
            continue
        elif (elemName == 'fm1g4c07a') and (field in ('x', 'y')) and \
             (handle in ('put', 'get')) and pv.startswith('SR:C08-MG'):
            continue
        elif (elemName == 'fh2g1c08a') and (field in ('x', 'y')) and \
             (handle in ('put', 'get')) and pv.startswith('SR:C10-MG'):
            continue
        elif (elemName == 'fm1g4c08a') and (field in ('x', 'y')) and \
             (handle in ('put', 'get')) and pv.startswith('SR:C09-MG'):
            continue
        elif (elemName == 'fl1g1c09a') and (field in ('x', 'y')) and \
             (handle in ('put', 'get')) and pv.startswith('SR:C10-MG'):
            continue
        elif (elemName == 'fm1g4c09a') and (field in ('x', 'y')) and \
             (handle in ('put', 'get')) and pv.startswith('SR:C10-MG'):
            continue
        elif (elemName == 'fh2g1c10a') and (field in ('x', 'y')) and \
             (handle in ('put', 'get')) and pv.startswith('SR:C12-MG'):
            continue
        elif (elemName == 'fm1g4c10a') and (field in ('x', 'y')) and \
             (handle in ('put', 'get')) and pv.startswith('SR:C11-MG'):
            continue
        elif (elemName == 'fl1g1c11a') and (field in ('x', 'y')) and \
             (handle in ('put', 'get')) and pv.startswith('SR:C12-MG'):
            continue
        elif (elemName == 'fm1g4c11a') and (field in ('x', 'y')) and \
             (handle in ('put', 'get')) and pv.startswith('SR:C12-MG'):
            continue
        elif (elemName == 'fh2g1c12a') and (field in ('x', 'y')) and \
             (handle in ('put', 'get')) and pv.startswith('SR:C14-MG'):
            continue
        elif (elemName == 'fm1g4c12a') and (field in ('x', 'y')) and \
             (handle in ('put', 'get')) and pv.startswith('SR:C13-MG'):
            continue
        elif (elemName == 'fl1g1c13a') and (field in ('x', 'y')) and \
             (handle in ('put', 'get')) and pv.startswith('SR:C14-MG'):
            continue
        elif (elemName == 'fm1g4c13a') and (field in ('x', 'y')) and \
             (handle in ('put', 'get')) and pv.startswith('SR:C14-MG'):
            continue
        elif (elemName == 'fh2g1c14a') and (field in ('x', 'y')) and \
             (handle in ('put', 'get')) and pv.startswith('SR:C16-MG'):
            continue
        elif (elemName == 'fm1g4c14a') and (field in ('x', 'y')) and \
             (handle in ('put', 'get')) and pv.startswith('SR:C15-MG'):
            continue
        elif (elemName == 'fl1g1c15a') and (field in ('x', 'y')) and \
             (handle in ('put', 'get')) and pv.startswith('SR:C16-MG'):
            continue
        elif (elemName == 'fm1g4c15a') and (field in ('x', 'y')) and \
             (handle in ('put', 'get')) and pv.startswith('SR:C16-MG'):
            continue
        elif (elemName == 'fh2g1c16a') and (field in ('x', 'y')) and \
             (handle in ('put', 'get')) and pv.startswith('SR:C18-MG'):
            continue
        elif (elemName == 'fm1g4c16a') and (field in ('x', 'y')) and \
             (handle in ('put', 'get')) and pv.startswith('SR:C17-MG'):
            continue
        elif (elemName == 'fl1g1c17a') and (field in ('x', 'y')) and \
             (handle in ('put', 'get')) and pv.startswith('SR:C18-MG'):
            continue
        elif (elemName == 'fm1g4c17a') and (field in ('x', 'y')) and \
             (handle in ('put', 'get')) and pv.startswith('SR:C18-MG'):
            continue
        elif (elemName == 'fh2g1c18a') and (field in ('x', 'y')) and \
             (handle in ('put', 'get')) and pv.startswith('SR:C20-MG'):
            continue
        elif (elemName == 'fm1g4c18a') and (field in ('x', 'y')) and \
             (handle in ('put', 'get')) and pv.startswith('SR:C19-MG'):
            continue
        elif (elemName == 'fl1g1c19a') and (field in ('x', 'y')) and \
             (handle in ('put', 'get')) and pv.startswith('SR:C20-MG'):
            continue
        elif (elemName == 'fm1g4c19a') and (field in ('x', 'y')) and \
             (handle in ('put', 'get')) and pv.startswith('SR:C20-MG'):
            continue
        elif (elemName == 'fh2g1c20a') and (field in ('x', 'y')) and \
             (handle in ('put', 'get')) and pv.startswith('SR:C22-MG'):
            continue
        elif (elemName == 'fm1g4c20a') and (field in ('x', 'y')) and \
             (handle in ('put', 'get')) and pv.startswith('SR:C21-MG'):
            continue
        elif (elemName == 'fl1g1c21a') and (field in ('x', 'y')) and \
             (handle in ('put', 'get')) and pv.startswith('SR:C22-MG'):
            continue
        elif (elemName == 'fm1g4c21a') and (field in ('x', 'y')) and \
             (handle in ('put', 'get')) and pv.startswith('SR:C22-MG'):
            continue
        elif (elemName == 'fh2g1c22a') and (field in ('x', 'y')) and \
             (handle in ('put', 'get')) and pv.startswith('SR:C24-MG'):
            continue
        elif (elemName == 'fm1g4c22a') and (field in ('x', 'y')) and \
             (handle in ('put', 'get')) and pv.startswith('SR:C23-MG'):
            continue
        elif (elemName == 'fl1g1c23a') and (field in ('x', 'y')) and \
             (handle in ('put', 'get')) and pv.startswith('SR:C24-MG'):
            continue
        elif (elemName == 'fm1g4c23a') and (field in ('x', 'y')) and \
             (handle in ('put', 'get')) and pv.startswith('SR:C24-MG'):
            continue
        elif (elemName == 'fh2g1c24a') and (field in ('x', 'y')) and \
             (handle in ('put', 'get')) and pv.startswith('SR:C26-MG'):
            continue
        elif (elemName == 'fm1g4c24a') and (field in ('x', 'y')) and \
             (handle in ('put', 'get')) and pv.startswith('SR:C25-MG'):
            continue
        elif (elemName == 'fl1g1c25a') and (field in ('x', 'y')) and \
             (handle in ('put', 'get')) and pv.startswith('SR:C26-MG'):
            continue
        elif (elemName == 'fm1g4c25a') and (field in ('x', 'y')) and \
             (handle in ('put', 'get')) and pv.startswith('SR:C26-MG'):
            continue
        elif (elemName == 'fh2g1c26a') and (field in ('x', 'y')) and \
             (handle in ('put', 'get')) and pv.startswith('SR:C28-MG'):
            continue
        elif (elemName == 'fm1g4c26a') and (field in ('x', 'y')) and \
             (handle in ('put', 'get')) and pv.startswith('SR:C27-MG'):
            continue
        elif (elemName == 'fl1g1c27a') and (field in ('x', 'y')) and \
             (handle in ('put', 'get')) and pv.startswith('SR:C28-MG'):
            continue
        elif (elemName == 'fm1g4c27a') and (field in ('x', 'y')) and \
             (handle in ('put', 'get')) and pv.startswith('SR:C28-MG'):
            continue
        elif (elemName == 'fh2g1c28a') and (field in ('x', 'y')) and \
             (handle in ('put', 'get')) and pv.startswith('SR:C30-MG'):
            continue
        elif (elemName == 'fm1g4c28a') and (field in ('x', 'y')) and \
             (handle in ('put', 'get')) and pv.startswith('SR:C29-MG'):
            continue
        elif (elemName == 'fl1g1c29a') and (field in ('x', 'y')) and \
             (handle in ('put', 'get')) and pv.startswith('SR:C30-MG'):
            continue
        elif (elemName == 'fm1g4c29a') and (field in ('x', 'y')) and \
             (handle in ('put', 'get')) and pv.startswith('SR:C30-MG'):
            continue
        #
        # Reject disconnected PV definitions
        elif (elem['elemType'] == 'COR') and (
            field in ('mcblx', 'mckx', 'mcbly', 'mcky')):
            # PVs offline as of 02/01/2021
            #   'mcblx' like 'SR:C30-MG{PS:CH1A}BL:Ps1DCCT1-I'
            #   'mckx' like 'SR:C30-MG{PS:CH1A}K:Ps1DCCT1-I'
            #   'mcbly' like 'SR:C30-MG{PS:CH1A}BL:Ps2DCCT1-I'
            #   'mcky' like 'SR:C30-MG{PS:CH1A}K:Ps2DCCT1-I'
            continue

        # Fix wrong/obsolete PVs to correct/updated PVs
        if elem['elemType'] == 'TUNE':
            if pv == 'SR:C16-BI{TuneNA}Freq:Vx-I':
                pv = 'SR:OPS-BI{IGPF}FBX:Tune-I'
            elif pv == 'SR:C16-BI{TuneNA}Freq:Vy-I':
                pv = 'SR:OPS-BI{IGPF}FBY:Tune-I'
            else:
                raise ValueError

        elem['map'][field][handle]['pv'] = pv
        if epsilon:
            elem['map'][field][handle]['epsilon'] = epsilon

        # Add model variable (MV) information
        mv_d = dict(elem_name=elemName.upper())
        if elem['elemType'] in ('BPM', 'UBPM_', '_BPM'):
            mv_d['property'] = field
        elif elem['elemType'] in ('XBPM_', 'CAMERA'):
            pass # No corresponding elements in the model.
        elif elem['elemType'] == 'BEND':
            pass # For now, not allowed to change in the model
        elif elem['elemType'] == 'QUAD':
            mv_d['property'] = 'K1'
        elif elem['elemType'] == 'SKQUAD':
            mv_d['elem_name'] = mv_d['elem_name'].replace('HG', 'G')
            mv_d['property'] = 'K1'
        elif elem['elemType'] == 'SEXT':
            mv_d['property'] = 'K2'
        elif elem['elemType'] == 'COR':
            if field == 'x':
                mv_d['property'] = ('HKICK', 0) # [rad]
                mv_d['elem_name'] = mv_d['elem_name'].replace('G', 'YG')
            elif field == 'x_2nd':
                mv_d['property'] = ('HKICK', 1) # [rad]
                mv_d['elem_name'] = mv_d['elem_name'].replace('G', 'YG')
            elif field == 'y':
                mv_d['property'] = ('VKICK', 0) # [rad]
                mv_d['elem_name'] = mv_d['elem_name'].replace('G', 'YG')
            elif field == 'y_2nd':
                mv_d['property'] = ('VKICK', 1) # [rad]
                mv_d['elem_name'] = mv_d['elem_name'].replace('G', 'YG')
            elif field in ('mcblx', 'mckx', 'mcbly', 'mcky'):
                raise ValueError # Corresponding PVs are disconnected, and this
                                 # should not be reachable.
            elif field in ('ramping[0]', 'ramping[1]'):
                mv_d['property'] = None # indicates "do nothing" to the model
                if field.endswith('[0]'):
                    mv_d['elem_name'] = mv_d['elem_name'].replace('G', 'YG')
                elif field.endswith('[1]'):
                    mv_d['elem_name'] = mv_d['elem_name'].replace('G', 'YG')
                else:
                    raise ValueError
            else:
                raise ValueError
        elif elem['elemType'] == 'FCOR':
            if field == 'x':
                mv_d['property'] = 'HKICK' # [rad]
            elif field == 'y':
                mv_d['property'] = 'VKICK' # [rad]
            elif field in ('mode', 'x2', 'y2', 'xjump', 'yjump'):
                mv_d['property'] = None # indicates "do nothing" to the model
            else:
                raise ValueError
        elif elem['elemType'] == 'RFCAVITY':
            if field in ('f_hz', 'f'):
                mv_d['property'] = 'FREQ' # [Hz]
            elif field in ('v', 'phi'):
                raise ValueError # Corresponding PVs should have been removed
                                 # above and so this line should not be reachable.
            else:
                raise ValueError
            mv_d['elem_name'] = 'RFC'
        #
        elif elem['elemType'] in ('DW', 'EPU', 'IVU', 'OVU'):
            mv_d['property'] = None # indicates "do nothing" to the model
            if elemName in ('epu57g1c02c',
                            'ivu20g1c03c',
                            'ivu23g1c04u',
                            'ivu21g1c05d',
                            'ovu42g1c07u',
                            'epu60g1c07d',
                            'ivu22g1c10c',
                            'ivu20g1c11c',
                            'ivu23g1c12d',
                            'ivu23g1c16c',
                            'ivu21g1c17u',
                            'ivu21g1c17d',
                            'ivu18g1c19u',
                            'epu57g1c21u',
                            'epu105g1c21d',
                            'epu49g1c23u',
                            'epu49g1c23d',
                            ):
                mv_d['elem_name'] = f'{elemName.upper()}M'
            elif elemName in (
                'dw100g1c08u',
                'dw100g1c08d',
                'dw100g1c18u',
                'dw100g1c18d',
                'dw100g1c28u',
                'dw100g1c28d',
                ):
                mv_d['elem_name'] = elemName.upper()
            else:
                raise ValueError
        #
        elif elem['elemType'] == 'TUNE':
            if field == 'x':
                mv_d['property'] = 'NUX'
            elif field == 'y':
                mv_d['property'] = 'NUY'
            else:
                raise ValueError
            mv_d['elem_name'] = '!TUNE'
        elif elem['elemType'] == 'DCCT':
            if field == 'tau':
                mv_d['property'] = 'TAU' # [hr]
            elif field in ('Iavg', 'I'):
                mv_d['property'] = 'I' # [mA]
            else:
                raise ValueError
            mv_d['elem_name'] = '!DCCT'
        else:
            #raise NotImplementedError
            print(elemName, elem['elemType'], field, handle, pv)
        #
        if len(mv_d) != 1:
            if not mv_d['elem_name'].startswith('!'):
                assert mv_d['elem_name'] in flat_used_elem_names
            elem['map'][field][handle]['mv']['pyelegant'] = mv_d

    else:
        assert 'elemField' not in elem_def
        assert 'elemHandle' not in elem_def

        assert elemName not in submachine

        elem = submachine[elemName] = {k: v for k, v in elem_def.items()}

print(set(tags_list))


nsls2_elems_pvs_mvs_pgz_file = 'nsls2_sr_elems_pvs_mvs.pgz'
with gzip.GzipFile(nsls2_elems_pvs_mvs_pgz_file, 'wb') as f:
    pickle.dump(root['SR'], f)
shutil.copy(nsls2_elems_pvs_mvs_pgz_file,
            '/epics/aphla/apconf/nsls2/nsls2_sr_elems_pvs_mvs.pgz')

#with gzip.GzipFile(nsls2_elems_pvs_mvs_pgz_file, 'rb') as f:
    #loaded_SR = pickle.load(f)

print('Finished')