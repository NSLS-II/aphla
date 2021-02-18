import sys
import time
import pickle
conda_env_name = [
    tok for tok in pickle.__file__.split('/') if tok.startswith('ap')][0]

import aphla as ap

ap.machines.load('nsls2', 'SR')

#TEST_NAME = 'elem_pvs'
#TEST_NAME = 'unitconv'
TEST_NAME = 'unitsymb'

import logging
logging.basicConfig(level=logging.INFO, filename=f'test_load_{conda_env_name}_{TEST_NAME}.log',
                    #format='%(asctime)s | %(name)s | %(levelname)s | %(message)s'
                    format='%(message)s',
                    filemode='w',
                    )

all_elems = ap.getElements('*')

if False:
    all_u_elem_props = []
    for i, e in enumerate(all_elems):
        #print(f'{i+1:d}/{len(all_elems):d}')
        fields = e.fields()
        all_u_elem_props.extend(fields)
        all_u_elem_props.extend(
            [prop for prop in dir(e)
             if (prop not in fields) and (not prop.startswith('__'))
             and (not callable(getattr(e, prop)))])
        # ^ here avoiding "getattr(e, prop)" for "prop" is in "fields" is critical,
        #   as getattr can actually call caget() for those in "fields", which you
        #   want to avoid.
        all_u_elem_props = list(set(all_u_elem_props))
    #with open('all_unique_elem_property_names.pkl', 'wb') as f:
        #pickle.dump(all_u_elem_props, f)

    print(len(all_u_elem_props))

if TEST_NAME == 'elem_pvs':
    for i, e in enumerate(all_elems):
        fields = e.fields()
        for fld in fields:
            for h in ['setpoint', 'readback']:
                for pv in e.pv(field=fld, handle=h):
                    logging.info(f'{e.name} : {fld} : {h} : {pv}')


elif TEST_NAME == 'unitconv':

    load_test_sp_from_file = False
    #load_test_sp_from_file = True

    if not load_test_sp_from_file:
        test_sp_values = {}

        quads = ap.getElements('QUAD')
        for e in quads:
            args = (e.name, 'b1', 'setpoint', None)
            print(args)
            test_sp_values[args] = e.get(args[1], handle=args[2], unitsys=args[3])
            args = (e.name, 'b1', 'setpoint', 'phy')
            print(args)
            test_sp_values[args] = e.get(args[1], handle=args[2], unitsys=args[3])
            time.sleep(3.0)

        sexts = ap.getElements('SEXT')
        for e in sexts:
            args = (e.name, 'b2', 'setpoint', None)
            print(args)
            test_sp_values[args] = e.get(args[1], handle=args[2], unitsys=args[3])
            args = (e.name, 'b2', 'setpoint', 'phy')
            print(args)
            test_sp_values[args] = e.get(args[1], handle=args[2], unitsys=args[3])
            time.sleep(3.0)

        with open(f'test_unitconv_sp_values_{conda_env_name}_{TEST_NAME}.pkl', 'wb') as f:
            pickle.dump(test_sp_values, f)
    else:
        with open(f'test_unitconv_sp_values_{conda_env_name}_{TEST_NAME}.pkl', 'rb') as f:
            test_sp_values = pickle.load(f)

    for i, e in enumerate(all_elems):
        print(f'{i+1:d}/{len(all_elems):d}')
        fields = e.fields()
        for fld in fields:
            for h in ['setpoint', 'readback']:
                avail_unitsystems = e.getUnitSystems(fld)
                for src in avail_unitsystems:
                    for dst in avail_unitsystems:
                        convertible = e.convertible(fld, src, dst, handle=h)
                        if not convertible:
                            logging.info(f'{e.name} : {fld} : {h} : {src} : {dst} : {convertible}')
                        else:
                            if fld in ('b1', 'b2'):
                                args = (e.name, fld, 'setpoint', src)
                                x = test_sp_values.get(args, 1.0)
                            else:
                                x = 1.0
                            v = e.convertUnit(fld, x, src, dst, handle=h)
                            logging.info(f'{e.name} : {fld} : {h} : {src} : {dst} : {v:.16g}')

elif TEST_NAME == 'unitsymb':
    for i, e in enumerate(all_elems):
        fields = e.fields()
        for fld in fields:
            for h in ['setpoint', 'readback']:
                avail_unitsystems = e.getUnitSystems(fld)
                for src in avail_unitsystems:
                    unit = e.getUnit(fld, handle=h, unitsys=src)
                    logging.info(f'{e.name} : {fld} : {h} : {src} : {unit}')

else:
    raise NotImplementedError
# TODO: Check "sb", "se", etc.