#/Horizontal C/ c No such line any more
s/,V:2-SR,/,V2SR,/
s/,readback,/,get,/I
s/,setpoint,/,set,/I
s/,,Horizontal Corrector/,x,COR/
s/,,Vertical Corrector/,y,COR/
s/,CX\([A-Z0-9]*\),\(.*\),COR/,C\1,\2,COR/
s/,CY\([A-Z0-9]*\),\(.*\),COR/,C\1,\2,COR/
s/,FX\([A-Z0-9]*\),\(.*\),COR/,F\1,\2,FCOR/
s/,FY\([A-Z0-9]*\),\(.*\),COR/,F\1,\2,FCOR/
s/,[Xx],Beam Position Monitor/,x,BPM/
s/,[Yy],Beam Position Monitor/,y,BPM/
/,PU/ s/,BPM/,UBPM/
s/,T,Bending/,bend,DIPOLE/
s/,K,Sextupole/,k2,SEXT/
s/,K,Quadrupole/,k1,QUAD/
s/,GAP,insertion/,gap,INSERTION/
s/,PHASE,insertion/,phase,INSERTION/
s/,CU\([0-9]\)[XY]\([A-Z0-9]*\),\(.*\),COR/,CU\1\2,\3,IDCOR/
s/,CS\([0-9]\)[XY]\([A-Z0-9]*\),\(.*\),COR/,CS\1\2,\3,IDSIMCOR/

