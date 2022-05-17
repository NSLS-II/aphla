import pickle
import gzip
from pathlib import Path
import re

from cothread.catools import caget

import aphla as ap
ap.machines.load('nsls2', 'SR')

V2DB_FOLDER = Path('/home/yhidaka/git_repos/aphla/v2tests')
ELEM_PV_MV_PGZ_FILEPATHS = dict(SR=V2DB_FOLDER.joinpath('nsls2_sr_elems_pvs_mvs.pgz'))

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
        
    print('Finished')