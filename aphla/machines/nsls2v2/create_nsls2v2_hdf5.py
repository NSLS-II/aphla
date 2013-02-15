"""
Create HDF5 conf for NSLS2V2
-----------------------------
"""
# :author: Lingyun Yang <lyyang@bnl.gov>

import h5py

import os
import sys
import numpy as np
import h5py

def init_v2sr_unitconv(grp):
    names = ["HLA:VBPM"]
    families = ["BPM"]
    dsname = "uc_0"
    for dsname, fld in [("uc_0", "x"), ("uc_1", "y")]:
        grp[dsname] = [1000.0, 0.0] # y = ax + b
        grp[dsname].attrs["unitsys"] = ",".join([fld, '', "phy"])
        grp[dsname].attrs["direction"] = ("m", "mm")
        grp[dsname].attrs["_class_"] = "polynomial"
        grp[dsname].attrs["families"] = families
        grp[dsname].attrs["elements"] = names

        dsname += "_inv"
        grp[dsname] = [0.001, 0]
        grp[dsname].attrs["unitsys"] = ",".join([fld, "phy", ""])
        grp[dsname].attrs["direction"] = ("mm", "m")
        grp[dsname].attrs["_class_"] = "polynomial"
        grp[dsname].attrs["families"] = families
        grp[dsname].attrs["elements"] = names

def init_v2sr_golden_design(grp):
    lines = open('ring_par.txt', 'r').readlines()
    elem, fld, val = [], [], []
    for s in lines[3:]:
        name, fam, L, se, k1, k2, angle = [v.strip() for v in s.split()[:7]]
        if fam == 'SEXT':
            elem.append(name.lower())
            fld.append('k2')
            val.append(float(k2))
        elif fam == 'QUAD':
            elem.append(name.lower())
            fld.append('k1')
            val.append(float(k1))
        elif fam == 'BPM':
            # 
            elem.append(name.lower())
            fld.append('x')
            val.append(0.0)
            elem.append(name.lower())
            fld.append('y')
            val.append(0.0)

    for line in open('golden.txt', 'r').readlines():
        name, fl, vali = [v.strip() for v in line.split()]
        elem.append(name.lower())
        fld.append(fl)
        val.append(float(vali))
    
    grp['element'] = elem
    grp['field'] = fld
    grp['value'] = val
    grp['value'].attrs['unitsys'] = ''
    grp.create_group("waveform")

def init_v2sr_golden(grp):
    import aphla as ap
    ap.machines.init("nsls2v2")
    elemlst, fldlst, vallst = [], [], []
    skip = ['tune', 'dcct']
    for elem in ap.getElements('COR'):
        if elem.name in skip: continue
        for fld in elem.fields():
            elemlst.append(elem.name)
            fldlst.append(fld)
            vallst.append(elem.get(fld, unitsys = None))
            if len(elemlst) % 100 == 0: 
                print len(elemlst), elem.name, fld
    grp['element'] = [e.encode("ascii") for e in elemlst]
    grp['field'] = [e.encode("ascii") for e in fldlst]
    grp['value'] = vallst
    grp['value'].attrs['unitsys'] = ''
    grp.create_group("waveform")


def read(h5fname, grp):
    g = h5py.File(h5fname, 'r')[grp]
    for k, dst in g.items():
        fld, usrc, udst = dst.attrs['unitsys'].split(',')
        cls = dst.attrs.get('_class_', 'polynomial')
        elements = dst.attrs.get('elements', [])
        print fld, "'%s'->'%s'" % (usrc, udst), list(dst), cls, elements


if __name__ == "__main__":
    f = h5py.File("nsls2v2.hdf5", "w")
    grp = f.create_group("V2SR")
    grp["orm"] = h5py.ExternalLink("v2sr_orm.hdf5", "orm")
    grp["twiss"] = h5py.ExternalLink("v2sr_twiss.hdf5", "twiss")
    grp["unitconv"] = h5py.ExternalLink("v2sr_unitconv.hdf5", "unitconv")
    grp["golden"] = h5py.ExternalLink("v2sr_golden.hdf5", "golden")

    grp = f.create_group("V1LTD1")
    grp = f.create_group("V1LTD2")
    grp = f.create_group("V1LTB")

    f.close()


    # create unit conv
    f = h5py.File("v2sr_unitconv.hdf5", "w")
    grp = f.create_group("unitconv")
    init_v2sr_unitconv(grp)
    f.close()

    # create golden
    f = h5py.File("v2sr_golden.hdf5", "w")
    grp = f.create_group("golden")
    init_v2sr_golden_design(grp)
    f.close()

    
