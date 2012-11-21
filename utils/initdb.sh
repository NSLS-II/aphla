#!/bin/bash

PAR="CD3-Oct3-12-30Cell-addID-par.txt"
VA="CD3-Oct3-12-30Cell-addID-par.csv"
DBF="us_nsls2v2.sqlite"
PYTHON=python2.7
${PYTHON} dbimport.py --par ${PAR} --system V2SR ${DBF}
sqlite3 ${DBF} 'insert into elements (name, system, virtual) values ("tune", "V2SR", 0)'
sqlite3 ${DBF} 'insert into elements (name, system, virtual) values ("twiss", "V2SR", 0)'
sqlite3 ${DBF} 'insert into elements (name, system, virtual) values ("dcct", "V2SR", 0)'
sqlite3 ${DBF} 'insert into elements (name, system, virtual) values ("orbit", "V2SR", 0)'

${PYTHON} dbimport.py --va ${VA} --system V2SR ${DBF}
${PYTHON} dbimport.py --cf2 LTB-20120724.txt --system LTB ${DBF}

sqlite3 ${DBF} 'update pvs set tags="aphla.sys.LTB" where pv like "LTB%"'
sqlite3 ${DBF} 'update pvs set tags="aphla.sys.V2SR" where pv like "V:2-SR%"'
