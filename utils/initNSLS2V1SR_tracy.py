#
import csv
import sys, os


def process_tracy_va_pvrecord(data, apsys = 'aphla.sys.V1SR'):
    """
    convert pv record "dict" and return 
    - pv string
    - properties dict
    - tags list of string
    """

    pv = data["#pv_name"]
    prpts, tags = {}, [apsys]
    #mapd = [('el_idx_va', 'ordinal'),
    #        ('el_name_va', 'elemName'),
    #        (, 'devName'),
    #        (, 'elemField'),
    #        (, 'elemType'),
    #        (, 'handle'),
    #        (, 'length'),
    #        (, 'sEnd'),
    #        (, 'system')]
    elem_type = {'Beam Position Monitor': 'BPM',
                 'Sextupole': 'SEXT', 'Quadrupole': 'QUAD',
                 'Horizontal Corrector': 'HCOR',
                 'Vertical Corrector': 'VCOR',
                 'Bending': 'DIPOLE'}

    # required
    prpts.setdefault('system', data['machine'])
    prpts.setdefault('ordinal', data.get('el_idx_va', -1))

    prpts.setdefault('cell', data.get('cell', None))
    prpts.setdefault('girder', data.get('girder', None))

    name = data.get('el_name_va', None)
    if name == None:
        if pv.find('{TUNE}X') > 0: prpts.setdefault('elemName', 'tune')
        elif pv.find('{TUNE}Y') > 0: prpts.setdefault('elemName', 'tune')
        elif pv.find('{ALPHA}X') > 0: prpts.setdefault('elemName', 'alpha')
        elif pv.find('{ALPHA}Y') > 0: prpts.setdefault('elemName', 'alpha')
        elif pv.find('{BETA}X') > 0: prpts.setdefault('elemName', 'beta')
        elif pv.find('{BETA}Y') > 0: prpts.setdefault('elemName', 'beta')
        elif pv.find('{ETA}X') > 0: prpts.setdefault('elemName', 'eta')
        elif pv.find('{ETA}Y') > 0: prpts.setdefault('elemName', 'eta')
        elif pv.find('{PHI}X') > 0: prpts.setdefault('elemName', 'phi')
        elif pv.find('{PHI}Y') > 0: prpts.setdefault('elemName', 'phi')
        elif pv.find('{ORBIT}X') > 0: prpts.setdefault('elemName', 'orbit')
        elif pv.find('{ORBIT}Y') > 0: prpts.setdefault('elemName', 'orbit')
        elif pv.find('{POS}-I') > 0: prpts.setdefault('elemName', 'pos')
        elif pv.find('{ALPHA}Y') > 0: prpts.setdefault('elemName', 'alpha')
        else:
            raise RuntimeError("pv '%s' has no element name" % pv)
    elif name == 'BPM':
        prpts.setdefault('elemName', 'p_bpm_%03d' % int(prpts['ordinal']))
    elif name == 'CH':
        prpts.setdefault('elemName', 'ch_%03d' % int(prpts['ordinal']))
    elif name == 'CV':
        prpts.setdefault('elemName', 'cv_%03d' % int(prpts['ordinal']))
    elif name == 'CHIDSim':
        prpts.setdefault('elemName', 'chidsim_%03d' % int(prpts['ordinal']))
    elif name == 'CVIDSim':
        prpts.setdefault('elemName', 'cvidsim_%03d' % int(prpts['ordinal']))
    else:
        prpts.setdefault('elemName', name.lower())

    if data.get('el_type_va', None) is None:
        if prpts['elemName'] not in [
            'tune', 'alpha', 'beta', 'eta', 'phi', 'orbit', 'pos']: 
            raise RuntimeError("pv '%s' has no element type" % pv)
    else:
        prpts.setdefault('elemType', elem_type[data['el_type_va']])

    prpts.setdefault('handle', data['handle'])
    # elemfield tag
    if prpts.get('elemType', None) == 'QUAD':
        if data.get('el_field_va', None) == 'K': tags.append('aphla.elemfield.k1')
    elif prpts.get('elemType', None) == 'SEXT':
        if data.get('el_field_va', None) == 'K': tags.append('aphla.elemfield.k2')
    elif prpts.get('elemType', None) == 'HCOR':
        #if data.get('el_field_va', None) == 'CH': tags.append('aphla.elemfield.x')
        tags.append('aphla.elemfield.x')
    elif prpts.get('elemType', None) == 'VCOR':
        #if data.get('el_field_va', None) == 'CV': tags.append('aphla.elemfield.y')
        tags.append('aphla.elemfield.y')

    return pv, prpts, tags


def init_tracy_va_table(fname):
    """
    initialize Channel finder from Tracy Virtual Accelerator data::

      #pv_name, el_idx_va, machine, cell, girder, handle, el_name_va, el_field_va, el_type_va
      V:1-SR:C30-MG:G2{SH1:7}Fld:SP,7,V:1-SR,C30,G2,setpoint,SH1G2C30A,K,Sextupole
      V:1-SR:C30-MG:G2{SH1:7}Fld:I,7,V:1-SR,C30,G2,readback,SH1G2C30A,K,Sextupole
      V:1-SR:C30-BI:G2{BPM:9}SA:X,9,V:1-SR,C30,G2,X,BPM,,Beam Position Monitor
      V:1-SR:C30-BI:G2{BPM:9}SA:Y,9,V:1-SR,C30,G2,Y,BPM,,Beam Position Monitor
      V:1-SR:C30-MG:G2{QH1:11}Fld:SP,11,V:1-SR,C30,G2,setpoint,QH1G2C30A,K,Quadrupole
      V:1-SR:C30-MG:G2{QH1:11}Fld:I,11,V:1-SR,C30,G2,readback,QH1G2C30A,K,Quadrupole

    Assumes the PV is already in.
    """

    with open(fname, 'r') as f:
        dialect = csv.excel
        dialect.skipinitialspace = True
        rd = csv.DictReader(f, dialect=dialect)
        for rec in rd:
            r1 = dict([(k,rec[k]) for k in rec.keys() if rec[k].strip()])
            pv, prpts, tags = process_tracy_va_pvrecord(r1)
            print pv, prpts, tags
            #break

if __name__ == "__main__":
    if len(sys.argv) > 1 and os.path.exists(sys.argv[1]):
        init_tracy_va_table(sys.argv[1])
    else:
        print "%s tablefile.csv" % (sys.argv[0],)
