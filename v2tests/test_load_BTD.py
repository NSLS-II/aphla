# This script should be run both in v1 aphla and v2 aphla such that 2 different
# log files can be compared to ensure the proper database conversion has been
# completed between v1 and v2 aphla.

import sys
import time
import pickle
conda_env_name = [
    tok for tok in pickle.__file__.split('/') if tok.startswith('ap')][0]

import aphla as ap

submachine = 'BTD'

ap.machines.load('nsls2', submachine, update_cache=True)

#TEST_NAME = 'elem_pvs'
TEST_NAME = 'unitconv'
#TEST_NAME = 'unitsymb'

import logging
logging.basicConfig(
    level=logging.INFO, filename=f'test_load_{submachine}_{conda_env_name}_{TEST_NAME}.log',
    #format='%(asctime)s | %(name)s | %(levelname)s | %(message)s'
    format='%(message)s',
    filemode='w',
)

all_elems = ap.getElements('*')

assert len(all_elems) == 16
# ^ Note that there are 0 elements that have no fields/PVs associated with.

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

        if fields == []:
            logging.info(f'{e.name}')


elif TEST_NAME == 'unitconv':

    # Comments: Differences remain for BPMs' x and y fields for handle='setpoint',
    # as the unit conversion for setpoints have been removed for v2.

    load_test_sp_from_file = False
    #load_test_sp_from_file = True

    field_list = [
        'b0', 'b1', 'centroidX', 'centroidY', 'image', 'position',
        'sigmaX', 'sigmaY', 'sizeX', 'sizeY', 'v', 'x', 'y',
    ]

    if not load_test_sp_from_file:
        test_sp_values = {}

        for e in ap.getElements('*'):
            for fld in field_list:
                if fld in e.fields():
                    avail_unitsystems = e.getUnitSystems(fld)
                    # Bring "None" in front
                    if None in avail_unitsystems:
                        avail_unitsystems.remove(None)
                        avail_unitsystems = [None] + sorted(avail_unitsystems)
                    for unitsys in avail_unitsystems:
                        args = (e.name, fld, 'setpoint', unitsys)
                        print(args)
                        test_sp_values[args] = e.get(args[1], handle=args[2], unitsys=args[3])
                    time.sleep(0.2)

        with open(f'test_unitconv_sp_values_{submachine}_{conda_env_name}_{TEST_NAME}.pkl', 'wb') as f:
            pickle.dump(test_sp_values, f)
    else:
        with open(f'test_unitconv_sp_values_{submachine}_{conda_env_name}_{TEST_NAME}.pkl', 'rb') as f:
            test_sp_values = pickle.load(f)

    for i, e in enumerate(all_elems):
        print(f'{i+1:d}/{len(all_elems):d}')
        fields = e.fields()
        for fld in fields:
            for h in ['setpoint', 'readback']:
                avail_unitsystems = e.getUnitSystems(fld)
                # Bring "None" in front
                if None in avail_unitsystems:
                    avail_unitsystems.remove(None)
                    avail_unitsystems = [None] + sorted(avail_unitsystems)
                for src in avail_unitsystems:
                    for dst in avail_unitsystems:
                        convertible = e.convertible(fld, src, dst, handle=h)
                        if not convertible:
                            logging.info(f'{e.name} : {fld} : {h} : {src} : {dst} : NOT Convertible')
                        else:
                            args = (e.name, fld, 'setpoint', src)
                            x = test_sp_values.get(args, 1.0)

                            v = e.convertUnit(fld, x, src, dst, handle=h)
                            if v is None:
                                assert x is None
                                logging.info(f'{e.name} ({e.pv(field=fld, handle=h)}) : {fld} : {h} : {src} : {dst} : None : None')
                            else:
                                try:
                                    logging.info(f'{e.name} : {fld} : {h} : {src} : {dst} : {x:.16g} : {v:.16g}')
                                except TypeError:
                                    logging.info(f'{e.name} : {fld} : {h} : {src} : {dst} : {x[0]:.16g} : {v[0]:.16g}')

elif TEST_NAME == 'unitsymb':
    for i, e in enumerate(all_elems):
        fields = e.fields()
        for fld in fields:
            for h in ['setpoint', 'readback']:
                avail_unitsystems = e.getUnitSystems(fld)
                # Bring "None" in front
                if None in avail_unitsystems:
                    avail_unitsystems.remove(None)
                    avail_unitsystems = [None] + sorted(avail_unitsystems)
                for src in avail_unitsystems:
                    unit = e.getUnit(fld, handle=h, unitsys=src)
                    logging.info(f'{e.name} : {fld} : {h} : {src} : {unit}')

else:
    raise NotImplementedError
# TODO: Check "sb", "se", etc.