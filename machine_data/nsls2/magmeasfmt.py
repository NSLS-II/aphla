import os, glob, shelve
from xlrd import open_workbook, XL_CELL_TEXT, XL_CELL_NUMBER, XL_CELL_DATE
import matplotlib.pylab as plt

#SRCDIR="""\\nsls2fs\Accelerator\MagnetMeasurements\RotatingCoil\Latest_Data"""
#SRCDIR="""Y:\MagnetMeasurements\RotatingCoil\Latest_Data"""
SRCDIR="./MagnetMeasurements/RotatingCoil/Latest_Data"

rotcoil_header = [
    ("Magnet Type", str, XL_CELL_TEXT),
    ("Alias", str, XL_CELL_TEXT),
    ("Vendor ID", str, XL_CELL_TEXT),
    ("Serial Number", int, XL_CELL_NUMBER),
    ("Measuring_Coil_ID", int, XL_CELL_NUMBER),
    ("Reference_Radius", float, XL_CELL_NUMBER),
    ("Magnet Notes", str, XL_CELL_TEXT),
    ("LoginName", str, XL_CELL_TEXT),
    ("Conditioning Current", float, XL_CELL_NUMBER),
    ("", None, None),
    ("Measured_at_Location", str, XL_CELL_TEXT)]


file_header = [
     ("Magnet Type", str, XL_CELL_TEXT),
     ("Alias", str, XL_CELL_TEXT),
     ("Vendor ID", str, XL_CELL_TEXT),
     ("Serial Number", int, XL_CELL_NUMBER),
     ("Measuring_Coil_ID", int, XL_CELL_NUMBER),
     ("Reference_Radius", float, XL_CELL_NUMBER),
     ("Magnet Notes", str, XL_CELL_TEXT),
     ("LoginName", str, XL_CELL_TEXT),
     ("Conditioning Current", float, XL_CELL_NUMBER),
     ("", None, None),
     ("Measured_at_Location", str, XL_CELL_TEXT)]

rotcoil_col = [
     ("Measured_at_Location", str, XL_CELL_TEXT),
     ("Run Number", int, XL_CELL_NUMBER),
     ("SubDevice", str, XL_CELL_TEXT),
     ("Current_1", float, XL_CELL_NUMBER),
     ("Current_2", float, XL_CELL_NUMBER),
     ("Current_3", float, XL_CELL_NUMBER),
     ("Up_Dn1", str, XL_CELL_TEXT),
     ("Up_Dn2", str, XL_CELL_TEXT),
     ("Up_Dn3", str, XL_CELL_TEXT),
     ("AnalysisNum", int, XL_CELL_NUMBER),
     ("Int_Trans_Func", float, XL_CELL_NUMBER),
     ("OriginOffset_X", float, XL_CELL_NUMBER),
     ("OriginOffset_Y", float, XL_CELL_NUMBER),
     ("B_ref_Int", float, XL_CELL_NUMBER),
     ("Roll_Angle", float, XL_CELL_NUMBER),
     ("Meas_notes", str, XL_CELL_TEXT),
     ("Meas_Date_Time", str, XL_CELL_TEXT),
     ("Author", str, XL_CELL_TEXT),
     ("a1", float, XL_CELL_NUMBER),
     ("a2", float, XL_CELL_NUMBER),
     ("a3", float, XL_CELL_NUMBER),
     ("a4", float, XL_CELL_NUMBER),
     ("a5", float, XL_CELL_NUMBER),
     ("a6", float, XL_CELL_NUMBER),
     ("a7", float, XL_CELL_NUMBER),
     ("a8", float, XL_CELL_NUMBER),
     ("a9", float, XL_CELL_NUMBER),
     ("a10", float, XL_CELL_NUMBER),
     ("a11", float, XL_CELL_NUMBER),
     ("a12", float, XL_CELL_NUMBER),
     ("a13", float, XL_CELL_NUMBER),
     ("a14", float, XL_CELL_NUMBER),
     ("a15", float, XL_CELL_NUMBER),
     ("a16", float, XL_CELL_NUMBER),
     ("a17", float, XL_CELL_NUMBER),
     ("a18", float, XL_CELL_NUMBER),
     ("a19", float, XL_CELL_NUMBER),
     ("a20", float, XL_CELL_NUMBER),
     ("a21", float, XL_CELL_NUMBER),
     ("b1", float, XL_CELL_NUMBER),
     ("b2", float, XL_CELL_NUMBER),
     ("b3", float, XL_CELL_NUMBER),
     ("b4", float, XL_CELL_NUMBER),
     ("b5", float, XL_CELL_NUMBER),
     ("b6", float, XL_CELL_NUMBER),
     ("b7", float, XL_CELL_NUMBER),
     ("b8", float, XL_CELL_NUMBER),
     ("b9", float, XL_CELL_NUMBER),
     ("b10", float, XL_CELL_NUMBER),
     ("b11", float, XL_CELL_NUMBER),
     ("b12", float, XL_CELL_NUMBER),
     ("b13", float, XL_CELL_NUMBER),
     ("b14", float, XL_CELL_NUMBER),
     ("b15", float, XL_CELL_NUMBER),
     ("b16", float, XL_CELL_NUMBER),
     ("b17", float, XL_CELL_NUMBER),
     ("b18", float, XL_CELL_NUMBER),
     ("b19", float, XL_CELL_NUMBER),
     ("b20", float, XL_CELL_NUMBER),
     ("b21", float, XL_CELL_NUMBER),
     ("Data Issues", int, XL_CELL_NUMBER)]

devices = ['Vert Field Dipole', 'Hor Field Dipole', 
           'Skew Quad', 'Sextupole', 'Quadrupole']

def rotcoil_col_index(cols):
    idx = []
    for i,c in enumerate(cols):
        for j,h in enumerate(rotcoil_col):
            if h[0] != c: continue
            idx.append(j)
            break
        else:
            raise RuntimeError("unknow data column: {0}".format(c))

    return idx

def _rc_read_header(fname):
    """
    read the header of XLS as a dict
    """
    fstr = open(fname, 'rb').read()
    wb = open_workbook(file_contents=fstr)
    #return wb.sheet_names()
    sht = wb.sheet_by_index(0)
    ret = {}
    for i,h in enumerate(rotcoil_header):
        cname, cfc, ctype2 = h
        if sht.cell(i,0).value != cname:
            raise RuntimeError("Different Header info: {0} {1}".format(
                 sht.cell(i,0), h))
        
        if sht.cell(i,1).value and sht.cell(i,1).ctype != ctype2:
            raise RuntimeError("Different Header info: {0} {1}".format(
                 sht.cell(i,0), h))
        elif sht.cell(i,1).value:
            ret[cname] = cfc(sht.cell(i,1).value)
        #else:
        #    ret.append((cname, None))
    return ret
    # check data header
    

def scan_rotating_coil(srcdir = SRCDIR, nmax = None):
    """
    scan all files as (fname, header_dict)
    """
    recs = {}
    for root, dirs, files in os.walk(srcdir):
        #print root, 
        for f in files:
            if f.endswith(".zip"): continue
            fname = os.path.join(root, f)
            recs[fname] = _rc_read_header(fname)
            if nmax and len(recs) > nmax: break
        #print recs
        if nmax and len(recs) > nmax: break
    #for k,v in recs.items():
    #    print k, v
    d = shelve.open("headers.shelve")
    d["headers"] = recs
    d.close()
    return recs

