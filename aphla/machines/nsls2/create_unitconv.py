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


def init_br(grp):
    ds = "BD1_B_I"
    # y = v[0]*x^4 + v[1]*x^3 + ... + v[4]
    grp[ds] = [0.0000000000002717329,-0.000000000450853,0.0000002156812,0.001495718,0.0014639]
    grp[ds].attrs["unitsys"] = ",".join(["b0", "", "phy"])
    grp[ds].attrs["direction"] = ("", "")
    grp[ds].attrs["_class_"] = "polynomial"
    grp[ds].attrs["families"] = "BD1"

    ds = "BD1_G_I"
    grp[ds] = [0.000000000001239146,-0.000000002242334,0.000001117486,0.007377142,0.007218819]
    grp[ds].attrs["unitsys"] = ",".join(["b1", "", "phy"])
    grp[ds].attrs["realfield"] = "b0"
    grp[ds].attrs["direction"] = ("", "")
    grp[ds].attrs["_class_"] = "polynomial"
    grp[ds].attrs["families"] = "BD1"

    ds = "BD1_S_I"
    grp[ds] = [-0.00000000007736754,0.0000001078356,-0.0000427955,0.061426,0.031784]
    grp[ds].attrs["unitsys"] = ",".join(["b2", "", "phy"])
    grp[ds].attrs["realfield"] = "b0"
    grp[ds].attrs["direction"] = ("", "")
    grp[ds].attrs["_class_"] = "polynomial"
    grp[ds].attrs["families"] = "BD1"

    ds = "BD1_I_B"
    grp[ds] = [-33.289411,84.116293,-61.320653,668.452373,-0.969042]
    # physics unit ("phy") to None/raw ("")
    grp[ds].attrs["unitsys"] = ",".join(["b0", "phy", ""])
    grp[ds].attrs["direction"] = ("", "")
    grp[ds].attrs["_class_"] = "polynomial"
    grp[ds].attrs["families"] = "BD1"

    ds = "BD2_B_I"
    grp[ds] = [0.0000000000002407631,-0.0000000004006765,0.0000001924432,0.001497716,0.001682902]
    grp[ds].attrs["unitsys"] = ",".join(["b0", "", "phy"])
    grp[ds].attrs["direction"] = ("", "")
    grp[ds].attrs["_class_"] = "polynomial"
    grp[ds].attrs["families"] = "BD2"

    ds = "BD2_G_I"
    grp[ds] = [0.00000000000137413,-0.000000002357779,0.000001134637,0.00736757,0.008791449]
    grp[ds].attrs["unitsys"] = ",".join(["b1", "", "phy"])
    grp[ds].attrs["realfield"] = "b0"
    grp[ds].attrs["direction"] = ("", "")
    grp[ds].attrs["_class_"] = "polynomial"
    grp[ds].attrs["families"] = "BD2"

    ds = "BD2_S_I"
    grp[ds] = [-0.00000000006877786,0.00000009583012,-0.00003743725,0.060833,0.073836]
    grp[ds].attrs["unitsys"] = ",".join(["b2", "", "phy"])
    grp[ds].attrs["realfield"] = "b0"
    grp[ds].attrs["direction"] = ("", "")
    grp[ds].attrs["_class_"] = "polynomial"
    grp[ds].attrs["families"] = "BD2"

    ds = "BD2_I_B"
    grp[ds] = [-29.580511,74.960874,-54.87453,667.626806,-1.115913]
    grp[ds].attrs["unitsys"] = ",".join(["b0", "phy", ""])
    grp[ds].attrs["realfield"] = "b0"
    grp[ds].attrs["direction"] = ("", "")
    grp[ds].attrs["_class_"] = "polynomial"
    grp[ds].attrs["families"] = "BD2"

    ds = "BF_B_I"
    grp[ds] = [1.133858E-14,-0.00000000003226502,0.00000002837643,0.0005236598,0.0009995262]
    grp[ds].attrs["unitsys"] = ",".join(["b0", "", "phy"])
    grp[ds].attrs["direction"] = ("", "")
    grp[ds].attrs["_class_"] = "polynomial"
    grp[ds].attrs["families"] = "BF"

    ds = "BF_G_I"
    grp[ds] = [0.0000000000004116128,-0.0000000009158697,0.0000006821702,0.009293128,0.021007]
    grp[ds].attrs["unitsys"] = ",".join(["b1", "", "phy"])
    grp[ds].attrs["realfield"] = "b0"
    grp[ds].attrs["direction"] = ("", "")
    grp[ds].attrs["_class_"] = "polynomial"
    grp[ds].attrs["families"] = "BF"

    ds = "BF_S_I"
    grp[ds] = [0.00000000004297231,-0.00000006886472,0.00003374462,0.034619,0.30835]
    grp[ds].attrs["unitsys"] = ",".join(["b2", "", "phy"])
    grp[ds].attrs["realfield"] = "b0"
    grp[ds].attrs["direction"] = ("", "")
    grp[ds].attrs["_class_"] = "polynomial"
    grp[ds].attrs["families"] = "BF"

    ds = "BF_I_B"
    grp[ds] = [-294.399726,427.035922,-195.057031,1909.882,-1.906891]
    grp[ds].attrs["unitsys"] = ",".join(["b0","phy", ""])
    grp[ds].attrs["direction"] = ("", "")
    grp[ds].attrs["_class_"] = "polynomial"
    grp[ds].attrs["families"] = "BF"
    #,,,,,,G(I)=kg4*I^4+kg3*I^3+kg2*I^2+kg1*I+kg0,,,,,,,,,,I(G)=ki4*G^4+ki3*G^3+ki2*G^2+ki1*G+ki0,,,]

    ds = "QF_G_I"
    grp[ds] = [-0.000000004980045,0.000001158642,-0.00007272479,0.126664,0.038426]
    grp[ds].attrs["unitsys"] = ",".join(["b1", "", "phy"])
    grp[ds].attrs["direction"] = ("", "")
    grp[ds].attrs["_class_"] = "polynomial"
    grp[ds].attrs["families"] = "QF"

    ds = "QF_I_G"
    grp[ds] = [0.000221587,-0.006875003,0.061032,7.809981,-0.256296]
    grp[ds].attrs["unitsys"] = ",".join(["b1", "phy", ""])
    grp[ds].attrs["direction"] = ("", "")
    grp[ds].attrs["_class_"] = "polynomial"
    grp[ds].attrs["families"] = "QF"

    ds = "QD_G_I"
    grp[ds] = [-0.000000004722752,0.000001074093,-0.00006383258,0.126074,0.04242]
    grp[ds].attrs["unitsys"] = ",".join(["b1", "", "phy"])
    grp[ds].attrs["direction"] = ("", "")
    grp[ds].attrs["_class_"] = "polynomial"
    grp[ds].attrs["families"] = "QD"

    ds = "QD_I_G"
    grp[ds] = [0.0002132786,-0.006507694,0.055993,7.850111,-0.29104]
    grp[ds].attrs["unitsys"] = ",".join(["b1", "phy", ""])
    grp[ds].attrs["direction"] = ("", "")
    grp[ds].attrs["_class_"] = "polynomial"
    grp[ds].attrs["families"] = "QD"

    ds = "QG_G_I"
    grp[ds] = [-0.000000004896012,0.000001126162,-0.00006877026,0.126352,0.040868]
    grp[ds].attrs["unitsys"] = ",".join(["b1", "", "phy"])
    grp[ds].attrs["direction"] = ("", "")
    grp[ds].attrs["_class_"] = "polynomial"
    grp[ds].attrs["families"] = "QG"

    ds = "QG_I_G"
    grp[ds] = [0.0002203189,-0.006781118,0.059295,7.829313,-0.276279]
    grp[ds].attrs["unitsys"] = ",".join(["b1", "phy", ""])
    grp[ds].attrs["direction"] = ("", "")
    grp[ds].attrs["_class_"] = "polynomial"
    grp[ds].attrs["families"] = "QG"
    #,,,,,,,,,,,S(I)=ks4*I^4+ks3*I^3+ks2*I^2+ks1*I+ks0,,,,,I(S)=ki4*S^4+ki3*S^3+ki2*S^2+ki1*S+ki0,,,]

    ds = "SF_S_I"
    grp[ds] = [0.003588652,-0.053174,0.260755,77.374153,-11.641088]
    grp[ds].attrs["unitsys"] = ",".join(["b2", "", "phy"])
    grp[ds].attrs["direction"] = ("", "")
    grp[ds].attrs["_class_"] = "polynomial"
    grp[ds].attrs["families"] = "SF"

    ds = "SF_I_S"
    grp[ds] = [-0.000000000001254857,0.000000001387766,-0.0000005019888,0.012911,0.150391]
    grp[ds].attrs["unitsys"] = ",".join(["b2", "phy", ""])
    grp[ds].attrs["direction"] = ("", "")
    grp[ds].attrs["_class_"] = "polynomial"
    grp[ds].attrs["families"] = "SF"

    ds = "SD_S_I"
    grp[ds] = [0.004355193,-0.075572,0.44161,76.776102,-10.94581]
    grp[ds].attrs["unitsys"] = ",".join(["b2", "", "phy"])
    grp[ds].attrs["direction"] = ("", "")
    grp[ds].attrs["_class_"] = "polynomial"
    grp[ds].attrs["families"] = "SD"

    ds = "SD_I_S"
    grp[ds] = [-0.000000000001532404,0.000000001996622,-0.0000008688711,0.013002,0.142524]
    grp[ds].attrs["unitsys"] = ",".join(["b2", "phy", ""])
    grp[ds].attrs["direction"] = ("", "")
    grp[ds].attrs["_class_"] = "polynomial"
    grp[ds].attrs["families"] = "SD"

    ds = "CX_BL_I"
    grp[ds] = [-0.00000400923,0.00002840724,-0.00001164229,0.003035044,0.0002609]
    grp[ds].attrs["unitsys"] = ",".join(["b0", "", "phy"])
    grp[ds].attrs["direction"] = ("", "")
    grp[ds].attrs["_class_"] = "polynomial"
    grp[ds].attrs["families"] = "CX"

    
    ds = "CX_I_BL"
    grp[ds] = [12596160,-290657.3,460.207254,329.420128,-0.085972]
    grp[ds].attrs["unitsys"] = ",".join(["b0", "phy", ""])
    grp[ds].attrs["direction"] = ("", "")
    grp[ds].attrs["_class_"] = "polynomial"
    grp[ds].attrs["families"] = "CX"

    ds = "CXW_BL_I"
    grp[ds] = [-0.0000004065819,-0.0000001740966,0.00003364862,0.002029932,0.000178]
    grp[ds].attrs["unitsys"] = ",".join(["b0", "", "phy"])
    grp[ds].attrs["direction"] = ("", "")
    grp[ds].attrs["_class_"] = "polynomial"
    grp[ds].attrs["families"] = "CXW"

    ds = "CXW_I_BL"
    grp[ds] = [5422072,89327.08,-4096.401,494.086812,-0.087818]
    grp[ds].attrs["unitsys"] = ",".join(["b0", "phy", ""])
    grp[ds].attrs["direction"] = ("", "")
    grp[ds].attrs["_class_"] = "polynomial"
    grp[ds].attrs["families"] = "CXW"

    ds = "CY_I_BL"
    grp[ds] = [-0.000001273542,0.000008457713,0.00000410853,0.002084707,0.0001506]
    grp[ds].attrs["unitsys"] = ",".join(["b0", "phy", ""])
    grp[ds].attrs["direction"] = ("", "")
    grp[ds].attrs["_class_"] = "polynomial"
    grp[ds].attrs["families"] = "CY"

    ds = "CY_BL_I"
    grp[ds] = [27343890,-396997.8,-406.980945,479.889581,-0.072261]
    grp[ds].attrs["unitsys"] = ",".join(["b0", "", "phy"])
    grp[ds].attrs["direction"] = ("", "")
    grp[ds].attrs["_class_"] = "polynomial"
    grp[ds].attrs["families"] = "CY"


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
    grp = f.create_group("BR")
    grp["unitconv"] = h5py.ExternalLink("br_unitconv.hdf5", "unitconv")
    f.close()

    f = h5py.File("br_unitconv.hdf5", "w")
    grp = f.create_group("unitconv")
    init_br(grp)
    f.close()

    if False:
        f = h5py.File("ltb_unitconv.hdf5", "w")
        grp = f.create_group("unitconv")
        init_ltb(grp)
        f.close()
        read("ltb_unitconv.hdf5", "unitconv")

