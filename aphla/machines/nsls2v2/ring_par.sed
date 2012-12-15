s/SQ_TRIM/COR/
s/TRIM[DXY]/COR/
s/FTRIM/FCOR/
s/ EPU /INSERTION/
s/ IVU /INSERTION/
s/ DW /INSERTION/
s/^[ ]*CU\([0-9]*\)[XY]\([^ ]*\)[ ]*[A-Z][A-Z]* /CU\1\2  IDCOR /
s/^[ ]*CS\([0-9]*\)[XY]\([^ ]*\)[ ]*[A-Z][A-Z]* /CS\1\2  IDSIMCOR /
s/\(^[ ]*PU[A-Z0-9 ]*\)BPM /\1UBPM /
