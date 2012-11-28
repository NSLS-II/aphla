#!/bin/bash

PAR="CD3-Oct3-12-30Cell-addID-par.txt"
VA="CD3-Oct3-12-30Cell-addID-par.csv"
#CF2_LTB="LTB-20120724.txt"
CF2_LTB="LTB.txt"
DBF="us_nsls2v2.sqlite"
if [ $(uname) == "Linux" ]; then
    PYTHON=`which python`
else
    PYTHON=python2.7
fi

echo "== import lattice table: ${PAR}"
${PYTHON} dbimport.py --par ${PAR} --system V2SR ${DBF}
#echo "  QUAD: `sqlite3 ${DBF} 'select count(*) from elements where elem_type=\"QUAD\"'`"

echo " update group info"
sqlite3 ${DBF} 'update elements set elem_group="QH1" where name like "qh1g%c%"'
sqlite3 ${DBF} 'update elements set elem_group="QH2" where name like "qh2g%c%"'
sqlite3 ${DBF} 'update elements set elem_group="QH3" where name like "qh3g%c%"'
sqlite3 ${DBF} 'update elements set elem_group="QL1" where name like "ql1g%c%"'
sqlite3 ${DBF} 'update elements set elem_group="QL2" where name like "ql2g%c%"'
sqlite3 ${DBF} 'update elements set elem_group="QL3" where name like "ql3g%c%"'
sqlite3 ${DBF} 'update elements set elem_group="QM1" where name like "qm1g%c%"'
sqlite3 ${DBF} 'update elements set elem_group="QM2" where name like "qm2g%c%"'

sqlite3 ${DBF} 'update elements set elem_group="SH1" where name like "sh1g%c%"'
sqlite3 ${DBF} 'update elements set elem_group="SH3" where name like "sh3g%c%"'
sqlite3 ${DBF} 'update elements set elem_group="SH4" where name like "sh4g%c%"'
sqlite3 ${DBF} 'update elements set elem_group="SL1" where name like "sl1g%c%"'
sqlite3 ${DBF} 'update elements set elem_group="SL2" where name like "sl2g%c%"'
sqlite3 ${DBF} 'update elements set elem_group="SL3" where name like "sl3g%c%"'
sqlite3 ${DBF} 'update elements set elem_group="SM1A" where name like "sm1g%c%a"'
sqlite3 ${DBF} 'update elements set elem_group="SM1B" where name like "sm1g%c%b"'
sqlite3 ${DBF} 'update elements set elem_group="SM2" where name like "sm2g%c%"'



echo " insert virtual element: tune, twiss, dcct, orbit"
sqlite3 ${DBF} 'insert into elements (name, system, lat_index, virtual, position) values ("tune", "V2SR", 0, 0, 0)'
sqlite3 ${DBF} 'insert into elements (name, system, lat_index, virtual, elem_type, position) values ("dcct", "V2SR", 0, 0, "DCCT", 0)'
sqlite3 ${DBF} 'insert into elements (name, system, virtual) values ("twiss", "V2SR", 1)'
sqlite3 ${DBF} 'insert into elements (name, system, virtual) values ("orbit", "V2SR", 1)'


echo "== import channel access data: ${VA}"
${PYTHON} dbimport.py --va ${VA} --mergehvcor --system V2SR ${DBF}

echo "== setting group for COR"
sqlite3 ${DBF} 'update elements set elem_group="HCOR;VCOR" where elem_type="COR"'

echo " setting tuning range for quadrupole PVs"
# set tuning range
## https://nsls2ap.bnl.gov/index.php/Magnets:_Design_and_Measurement
#QH1 	0.275 	0.36 	1.62 	2
#QH2 	0.448 	1.32 	1.79 	1.96
#QH3 	0.275 	1.28 	1.76 	2
#QL1	0.275 	0.68 	2.00 	2
#QL2 	0.448 	1.62 	1.83 	1.96
#QL3 	0.275 	1.1 	1.60 	2
#QM1 	0.25 	0.73 	1.09 	1.1
#QM2 	0.283 	1.2 	1.3 	1.34 

# sqlite does not support join in update table
sqlite3 ${DBF} 'update pvs set low_lim=0.36,high_lim=1.62 where pvs.elem_id in (select elem_id from elements where name like "qh1g%c%")'
sqlite3 ${DBF} 'update pvs set low_lim=1.32,high_lim=1.79 where pvs.elem_id in (select elem_id from elements where name like "qh2g%c%")'
sqlite3 ${DBF} 'update pvs set low_lim=1.28,high_lim=1.76 where pvs.elem_id in (select elem_id from elements where name like "qh3g%c%")'
sqlite3 ${DBF} 'update pvs set low_lim=0.68,high_lim=2.0 where pvs.elem_id in (select elem_id from elements where name like "ql1g%c%")'
sqlite3 ${DBF} 'update pvs set low_lim=0.62,high_lim=1.83 where pvs.elem_id in (select elem_id from elements where name like "ql2g%c%")'
sqlite3 ${DBF} 'update pvs set low_lim=1.1,high_lim=1.6 where pvs.elem_id in (select elem_id from elements where name like "ql3g%c%")'
sqlite3 ${DBF} 'update pvs set low_lim=0.73,high_lim=1.09 where pvs.elem_id in (select elem_id from elements where name like "qm1g%c%")'
sqlite3 ${DBF} 'update pvs set low_lim=1.2,high_lim=1.3 where pvs.elem_id in (select elem_id from elements where name like "qm2g%c%")'

echo "== set polar for SR magnets"
sqlite3 ${DBF} 'update elements set polar=1 where elem_type in ("QUAD", "SEXT", "SQUAD", "DIPOLE")'

echo "== update cs* to virtual element"
sqlite3 ${DBF} 'update elements set virtual=1 where elem_type="COR" and name like "cs%id%"'

echo "== importing LTB cf2 data: ${CF2_LTB}"
${PYTHON} dbimport.py --cf2 ${CF2_LTB} --system LTB ${DBF}

echo "== set aphla.sys.\* tags"

# -cf format has tags inside. va and lat table does not
#sqlite3 ${DBF} 'update pvs set tags="aphla.sys.V1LTB" where pv like "LTB%"'
sqlite3 ${DBF} 'update pvs set tags="aphla.sys.V2SR" where pv like "V:2-SR%"'

sqlite3 ${DBF} 'select * from pvs where elem_id is NULL'

