"""
create unit conversion data for NSLS-II
"""
# :author: Lingyun Yang <lyyang@bnl.gov>

import os
import sys
import numpy as np
import h5py

def init_ltb(grp):
    d = [("Magnet Type", "MG name", "Family", "Serial Number", 
          "Linear Fit Slope (A)", "Units of A", "Linear Fit Offset (B)", 
          "Units of B", ""),
         ("Dipole", "B1, B2, B3, B4", "", "3",
          "0.001765982", "T-m/A", "0.002043966", "T-m", "bl", "A"), 
         ("Normal Aperture Quad SOLID IRON POLE TIP", "Q1, Q2, Q3, Q4, Q7, Q1BD1, Q2BD1", "", "1", 
          "0.080434155", "T/m/A", "0.173508465", "T/m", "g", "A"), 
         ("Normal Aperture Quad (Correct Pole Tip)", "Q8, Q9, Q10, Q11, Q12, Q13, Q14, Q15", "", "", 
          "0.08310826", "T/m/A", "0.078274321", "T/m", "g", "A"),
         ("Wide Aperture Quad", "Q5, Q6", "", "2",
          "0.027125245", "T/m/A", "0.008008731", "T/m", "g", "A"),
         ("Corrector", "", "HCOR", "", "7.02e-4", "T-m/A", "0", "T-m", "x", "A"),
         ("Corrector", "", "VCOR", "", "7.02e-4", "T-m/A", "0", "T-m", "y", "A"),
         ("BPM", "", "BPM", "", "0.001", "mm/um", "0", "mm", "x", "um"),
         ("BPM", "", "BPM", "", "0.001", "mm/um", "0", "mm", "y", "um"),
         ]
       
    iuc = 0
    for i,rec in enumerate(d[1:]):
        a, b = [float(rec[4]), float(rec[6])]
        names = [v.strip() for v in rec[1].split(',')]
        fams  = [v.strip() for v in rec[2].split(",")]

        dsname = "uc_%05d" % iuc
        grp[dsname] = [a, b] # y = ax + b
        grp[dsname].attrs["unitsys"] = ",".join([rec[8], '', "phy"])
        grp[dsname].attrs["direction"] = (rec[9], rec[7])
        grp[dsname].attrs["_class_"] = "polynomial"
        grp[dsname].attrs["_magtype_"] = rec[0]
        if names: grp[dsname].attrs["elements"] = names
        if fams: grp[dsname].attrs["families"] = fams
        iuc += 1

        dsname = "uc_%05d" % iuc
        grp[dsname] = [1.0/a, -b/a]
        grp[dsname].attrs["unitsys"] = ",".join([rec[8], "phy", ""])
        grp[dsname].attrs["direction"] = (rec[7], rec[9])
        grp[dsname].attrs["_class_"] = "polynomial"
        grp[dsname].attrs["_magtype_"] = rec[0]
        if names: grp[dsname].attrs["elements"] = names
        if fams: grp[dsname].attrs["families"] = fams
        iuc += 1


def read(h5fname, grp):
    g = h5py.File(h5fname, 'r')[grp]
    for k, dst in g.items():
        fld, usrc, udst = dst.attrs['unitsys'].split(',')
        cls = dst.attrs.get('_class_', 'polynomial')
        elements = dst.attrs.get('elements', [])
        print fld, "'%s'->'%s'" % (usrc, udst), list(dst), cls, elements


if __name__ == "__main__":
    f = h5py.File("nsls2.hdf5", "w")
    grp = f.create_group("LTB")
    grp["unitconv"] = h5py.ExternalLink("ltb_unitconv.hdf5", "unitconv")
    f.close()

    f = h5py.File("ltb_unitconv.hdf5", "w")
    grp = f.create_group("unitconv")
    init_ltb(grp)
    f.close()
    read("ltb_unitconv.hdf5", "unitconv")

