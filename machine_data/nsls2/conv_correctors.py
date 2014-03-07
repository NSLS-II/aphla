import os
import numpy as np
import h5py
import glob
import re
from fnmatch import fnmatch
from xlrd import open_workbook, XL_CELL_TEXT, XL_CELL_NUMBER, XL_CELL_DATE
import matplotlib.pylab as plt

import magmeasfmt as fmt

def read_magnet_curve(fxls, flt_subdevice):
    fstr = open(fxls, 'rb').read()
    wb = open_workbook(file_contents=fstr)
    sht = wb.sheet_by_index(0)
    subdev = set([])
    # magnet type
    for i,h in enumerate(fmt.file_header):
        if sht.cell(i,0).value != h[0]:
            raise RuntimeError("Different Header info: {0} {1}".format(
                 sht.cell(i,0), h))
    mtp = sht.cell(0,1).value

    r_ref = None
    for i in range(9):
        k = sht.cell(i,0).value
        if sht.cell(i,0).ctype == XL_CELL_TEXT: k = k.encode("ascii")
        if not sht.cell(i,1).value:
            if sht.cell(i,0).value == u'Magnet Notes': continue
            if sht.cell(i,0).value == "Conditioning Current": continue
            print "# WARNING:", sht.cell(i,0), "is empty"
            continue
        if k == 'Reference_Radius': r_ref = float(sht.cell(i,1).value) * 0.001

        #grp.attrs[k] = file_header[i][1](sht.cell(i,1).value)

    if r_ref is None:
        raise RuntimeError("No reference radius defined")

    n = len(fmt.file_header) - 1
    for j in range(sht.ncols):
         if sht.cell(n,j).value != fmt.rotcoil_col[j][0]:
              raise RuntimeError("incompatible columns '{0}' and '{1}'".format(
                   sht.cell(n,j).value, fmt.rotcoil_col[j][0]))
              #raise RuntimeError("incompativle data '{0}'/{1} vs. '{2}'/{3}\n"
              #                   "TEXT: {4}, NUMBER: {5}".format(
              #                        sht.cell(n,j).value, sht.cell(n,j).ctype,
              #                        rotcoil_header[j][0], rotcoil_header[j][2],
              #                        XL_CELL_TEXT, XL_CELL_NUMBER))

    isubdev, iud1, iud2, irun, iI1, iI2, iTF, iB = fmt.rotcoil_col_index([
        "SubDevice", "Up_Dn1", "Up_Dn2",
        "Run Number", "Current_1", "Current_2", "Int_Trans_Func", "B_ref_Int"])
    data_up, data_dn = [], []

    iud, iI = iud1, iI1
    if flt_subdevice == "Vert Field Dipole":
        iud, iI = iud2, iI2

    for row in range(len(fmt.file_header), sht.nrows):
        #print row, sht.cell(row, irun).value, sht.cell(row,iI1).value
        #print ", ".join(values)
        if not fnmatch(sht.cell(row, isubdev).value, flt_subdevice):
            continue

        curv = sht.cell(row,iud).value 
        if curv == "Up":
            data_up.append([sht.cell(row,iI).value,
                            sht.cell(row,iTF).value,
                            sht.cell(row,iB).value])
        elif curv == "Dn":
            data_dn.append([sht.cell(row,iI).value,
                            sht.cell(row,iTF).value,
                            sht.cell(row,iB).value])
        else:
            raise RuntimeError("unknow Curve: '{0}' (not Dn or Up)".format(
                curv))

        subdev.add(sht.cell(row,isubdev).value)

    # up curve and down curve
    d1, d2 = np.array(data_up), np.array(data_dn)
    if len(subdev) == 0:
        return None, mtp, r_ref, d1, d2
    elif len(subdev) > 1:
        raise RuntimeError("more than one device in this sheet")

    return mtp, subdev.pop(), r_ref, d1, d2


def process_matched(fname, pat="q*", latpar = "comm-ring-par.txt"):
    """
    """
    # read the lattice parameter table
    f = open(latpar, 'r')
    c = f.readline()
    if c.split()[4] != "K1":
        raise RuntimeError("{0} column 5 should be 'K1'".format(
            latpar))
    f.readline()
    f.readline()
    lat = {} # store (magnet, [[parameters], ...])
    for i,v in enumerate(f.readlines()):
        mag = v.split()[0].strip()
        lat.setdefault(mag, [])
        lat[mag] = v.split()
    h5f = h5py.File("sr_unitconv.hdf5" ,'w')
    g = h5f.create_group("UnitConversion")
    for i,line in enumerate(open(fname, 'r').readlines()):
        # searching over matched (element, measurement data)
        mag, c, fxls = line.split()
        if mag not in lat:
            raise RuntimeError("'{0} not in the lattice".format(mag))
        rt, base = os.path.split(fxls)
        if base in g.keys():
            raise RuntimeError("duplicate dataset: '{0}'".format(base))
        fstr = open(fxls, 'rb').read()
        wb = open_workbook(file_contents=fstr)
        sht = wb.sheet_by_index(0)
        if lat[mag][1] == "QUAD":
            subdev = "Quadrupole"
        elif lat[mag][1] == "SEXT":
            subdev = "Sextupole"
        elif lat[mag][1] == "TRIMD":
            subdev = "*Field Dipole"
        dev, mtp, r_ref, d1up, d2dn = process_sheet(sht, flt_subdevice=subdev)
        print fxls, dev, mtp, r_ref, np.shape(d1up), np.shape(d2dn)
        brho = 3.3357 * 3.0
        if dev == "Quadrupole":
            if lat[mag][1] != "QUAD":
                raise RuntimeError("{0} is not QUAD in {1}".format(
                    mag, latpar))
            L, k1 = float(lat[mag][2]), float(lat[mag][4])
            lat[mag].append(fxls)
            yfac = 1.0/r_ref/brho
            x = d1up[:,0]
            y = [b * yfac for b in d1up[:,2]]
            y_label = "B_ref_Int/r_ref/Brho=K1*L"
            # separate path from basename
            if x[0] > 0:
                d = np.zeros((len(d1up)+1, 2), 'd')
                d[1:,0] = x
                d[1:,1] = y
            else:
                d = np.zeros((len(d1up), 2), 'd')
                d[:,0] = x
                d[:,1] = y
                
            print base
            g[base] = d
            g[base].attrs["field"] = "b1"
            g[base].attrs["_class_"] = "interpolation"
            g[base].attrs["elements"] = [mag.lower()]
            g[base].attrs["src_unit_sys"] = ""
            g[base].attrs["src_unit"] = "A"
            g[base].attrs["dst_unit_sys"] = "phy"
            g[base].attrs["dst_unit"] = "1/m"
            g[base].attrs["invertible"] = 1
            if k1 < 0:
                g[base].attrs["polarity"] = -1
            else:
                g[base].attrs["polarity"] = 1

            if True:
                plt.clf()
                plt.plot(d[:,0], d[:,1], '-x')
                plt.axhline(y=np.abs(k1*L))
                plt.title("{0} ({1})".format(mag, mtp))
                plt.ylabel(y_label)
                plt.xlabel("I (up)")
                plt.savefig("q_%04d.png" % i)
        elif dev == "Sextupole" and lat[mag][1] == "SEXT":
            L, k2 = float(lat[mag][2]), float(lat[mag][5])
            lat[mag].append(fxls)
            yfac = 2.0/r_ref/r_ref/brho
            x = d1up[:,0]
            y = [b * yfac for b in d1up[:,2]]
            y_label = "B_ref_Int/(r^2/2)/Brho=K2*L"
            # separate path from basename
            rt, base = os.path.split(fxls)
            if x[0] > 0:
                d = np.zeros((len(d1up)+1, 2), 'd')
                d[1:,0] = x
                d[1:,1] = y
            else:
                d = np.zeros((len(d1up), 2), 'd')
                d[:,0] = x
                d[:,1] = y
            print base
            g[base] = d
            g[base].attrs["field"] = "b2"
            g[base].attrs["_class_"] = "interpolation"
            g[base].attrs["elements"] = [mag.lower()]
            g[base].attrs["src_unit_sys"] = ""
            g[base].attrs["src_unit"] = "A"
            g[base].attrs["dst_unit_sys"] = "phy"
            g[base].attrs["dst_unit"] = "1/m^2"
            g[base].attrs["invertible"] = 1
            
            if k2 < 0:
                g[base].attrs["polarity"] = -1
            else:
                g[base].attrs["polarity"] = 1

            if True:
                plt.clf()
                plt.plot(d[:,0], d[:,1], '-x')
                plt.axhline(y=np.abs(k2*L))
                plt.title("{0} ({1})".format(mag, mtp))
                plt.ylabel(y_label)
                plt.xlabel("I (up)")
                plt.savefig("s_%04d.png" % i)
        else:
            pass

        #if i > 10: break
    for k,v in enumerate(lat):
        if len(v) != 8 and v[1] in ["QUAD", "SEXT"]:
            print "WARNING", k, v

    h5f.close()

if __name__ == "__main__":
    dat = {
        "SR-MG-CRR-1000": [],
        "SR-MG-CRR-1001": [],
        "SR-MG-CRR-1560": [],
    }
    fname = "matched_magnets.txt"
    for i,line in enumerate(open(fname, 'r').readlines()):
        # searching over matched (element, measurement data)
        mag, c, fxls = line.split()
        if mag[:2] not in ["CL", "CH", "CM", "SQ"]: continue
        sn, subdev, r, vhup, vhdn = read_magnet_curve(
            fxls, "Hor Field Dipole")
        sn, subdev, r, vvup, vvdn = read_magnet_curve(
            fxls, "Vert Field Dipole")
        #print mag, sn, fxls
        dat[str(sn)].append((vhup[:,0], vhup[:,2]/(3.3357*3.0)/vhup[:,0],
                        vvup[:,0], vvup[:,2]/(3.3357*3.0)/vvup[:,0]))

    sk2cor = {}
    for i,line in enumerate(open("corr_skew_pair.txt", 'r').readlines()):
        sk, c = line.split()
        sk2cor[sk.strip().lower()] = c.strip().lower()
    print sk2cor
    sn2cor = {}
    for i,line in enumerate(open("corr_magnet_sn.txt", 'r').readlines()):
        sn, mag, cg = line.split()
        name = mag[:-6] + cg[-2:] + cg[:-2] + mag[-1]
        sn = "SR-MG-" + sn
        name = name.lower()
        sn2cor.setdefault(sn, [])
        if name in sk2cor:
            name = sk2cor[name]
        sn2cor[sn].append(name.lower())
    print sn2cor
    f = h5py.File("cor_unitconf.hdf5", "w")
    g = f.create_group("UnitConversion")
    for k,v in dat.items():
        dIh = np.average([r[1] for r in v])
        dIhvar1 = np.std([r[1] for r in v])
        dIv = np.average([r[3] for r in v])
        dIvvar1 = np.std([r[3] for r in v])
        g[k + "_H"] = [dIh*1000.0, 0.0]
        print "%10s H" % k, dIh, dIhvar1, len(sn2cor[k])
        ds = g[k + "_H"]
        ds.attrs["_class_"] = "polynomial"
        ds.attrs["calib_factor"] = 0.9988
        ds.attrs["dst_unit"] = "mrad"
        ds.attrs["dst_unit_sys"] = "phy"
        ds.attrs["field"] = "x"
        ds.attrs["elements"] = sn2cor[k]
        ds.attrs["invertible"] = 1
        ds.attrs["src_unit"] = "A"
        ds.attrs["src_unit_sys"] = ""
        g[k + "_V"] = [dIv*1000.0, 0.0]
        print "%10s V" % k, dIv, dIvvar1
        ds = g[k + "_V"]
        ds.attrs["_class_"] = "polynomial"
        ds.attrs["calib_factor"] = 0.9988
        ds.attrs["dst_unit"] = "mrad"
        ds.attrs["dst_unit_sys"] = "phy"
        ds.attrs["field"] = "x"
        ds.attrs["elements"] = sn2cor[k]
        ds.attrs["invertible"] = 1
        ds.attrs["src_unit"] = "A"
        ds.attrs["src_unit_sys"] = ""
    f.close()
    
