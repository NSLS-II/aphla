#!/bin/bash

DB=nsls2_sr.sqlite
#sqlite3 $DB 'select pv from pvs where pv like "%SH1-P1%"'
#
#sqlite3 $DB 'select pv from pvs where pv like "%SH1-P2%"'
#sqlite3 $DB 'select distinct pv from pvs where pv like "%SH1-P3%"'
#sqlite3 $DB 'select distinct pv from pvs where pv like "%SH1-P4%"'
#sqlite3 $DB 'select distinct pv from pvs where pv like "%SH1-P5%"'

#sqlite3 $DB 'select distinct pv from pvs where pv like "%SH3-P2%"'
#sqlite3 $DB 'select distinct pv from pvs where pv like "%SH3-P3%"'
#sqlite3 $DB 'select distinct pv from pvs where pv like "%SH3-P4%"'
#sqlite3 $DB 'select distinct pv from pvs where pv like "%SH3-P5%"'
#sqlite3 $DB 'select distinct pv from pvs where pv like "%SH3-P1%"'

#sqlite3 $DB 'select distinct pv from pvs where pv like "%SH4-P2%"'
#sqlite3 $DB 'select distinct pv from pvs where pv like "%SH4-P3%"'
#sqlite3 $DB 'select distinct pv from pvs where pv like "%SH4-P4%"'
#sqlite3 $DB 'select distinct pv from pvs where pv like "%SH4-P5%"'
#sqlite3 $DB 'select distinct pv from pvs where pv like "%SH4-P1%"'
#sqlite3 $DB 'delete from pvs where pv="SR:C07-MG{PS:SH4-P2}I:Ps1DCCT1-I"'
#sqlite3 $DB 'delete from pvs where pv="SR:C07-MG{PS:SH4-P2}I:Sp1-SP"'

#sqlite3 $DB 'select distinct pv from pvs where pv like "%SM1A-P2%"'
#sqlite3 $DB 'select distinct pv from pvs where pv like "%SM1A-P3%"'
#sqlite3 $DB 'select distinct pv from pvs where pv like "%SM1A-P4%"'
#sqlite3 $DB 'select distinct pv from pvs where pv like "%SM1A-P5%"'
#sqlite3 $DB 'select distinct pv from pvs where pv like "%SM1A-P1%"'
#sqlite3 $DB 'delete from pvs where pv="SR:C07-MG{PS:SM1A-P2}I:Ps1DCCT1-I"'
#sqlite3 $DB 'delete from pvs where pv="SR:C07-MG{PS:SM1A-P2}I:Sp1-SP"'

#sqlite3 $DB 'select distinct pv from pvs where pv like "%SL3-P2%"'
#sqlite3 $DB 'select distinct pv from pvs where pv like "%SL3-P3%"'
#sqlite3 $DB 'select distinct pv from pvs where pv like "%SL3-P4%"'
#sqlite3 $DB 'select distinct pv from pvs where pv like "%SL3-P5%"'
#sqlite3 $DB 'select distinct pv from pvs where pv like "%SL3-P1%"'
#sqlite3 $DB 'delete from pvs where pv="SR:C09-MG{PS:SL3-P2}I:Ps1DCCT1-I"'
#sqlite3 $DB 'delete from pvs where pv="SR:C09-MG{PS:SL3-P2}I:Sp1-SP"'

#sqlite3 $DB 'select distinct pv from pvs where pv like "%SL2-P2%"'
#sqlite3 $DB 'select distinct pv from pvs where pv like "%SL2-P3%"'
#sqlite3 $DB 'select distinct pv from pvs where pv like "%SL2-P4%"'
#sqlite3 $DB 'select distinct pv from pvs where pv like "%SL2-P5%"'
#sqlite3 $DB 'select distinct pv from pvs where pv like "%SL2-P1%"'
#sqlite3 $DB 'delete from pvs where pv="SR:C09-MG{PS:SL2-P2}I:Ps1DCCT1-I"'
#sqlite3 $DB 'delete from pvs where pv="SR:C09-MG{PS:SL2-P2}I:Sp1-SP"'

#sqlite3 $DB 'select distinct pv from pvs where pv like "%SL1-P2%"'
#sqlite3 $DB 'select distinct pv from pvs where pv like "%SL1-P3%"'
#sqlite3 $DB 'select distinct pv from pvs where pv like "%SL1-P4%"'
#sqlite3 $DB 'select distinct pv from pvs where pv like "%SL1-P5%"'
#sqlite3 $DB 'select distinct pv from pvs where pv like "%SL1-P1%"'
#sqlite3 $DB 'delete from pvs where pv="SR:C10-MG{PS:SL1-P2}I:Ps1DCCT1-I"'
#sqlite3 $DB 'delete from pvs where pv="SR:C10-MG{PS:SL1-P2}I:Sp1-SP"'

#sqlite3 $DB 'update pvs set pv="SR:C30-MG{PS:QH1A}I:Sp1-SP" where pv="SR:C30-MG{PS:QH1A}I:SP1-SP"'

if false; then
    echo "Removing DW SH1, SH2 and SH3"
    # SH1 DW08, both sides 
    sqlite3 $DB 'delete from pvs where elemName="sh4g6c07b" and pv like "SR:C%SH4-P%"'
    sqlite3 $DB 'delete from pvs where elemName="sh3g6c07b" and pv like "SR:C%SH3-P%"'
    sqlite3 $DB 'delete from pvs where elemName="sh1g6c07b" and pv like "SR:C%SH1-P%"'
    sqlite3 $DB 'delete from pvs where elemName="sh1g2c08a" and pv like "SR:C%SH1-P%"'
    sqlite3 $DB 'delete from pvs where elemName="sh4g2c08a" and pv like "SR:C%SH4-P%"'
    sqlite3 $DB 'delete from pvs where elemName="sh3g2c08a" and pv like "SR:C%SH3-P%"'

    # SH1 DW18, both sides 
    sqlite3 $DB 'delete from pvs where elemName="sh4g6c17b" and pv like "SR:C%SH4-P%"'
    sqlite3 $DB 'delete from pvs where elemName="sh3g6c17b" and pv like "SR:C%SH3-P%"'
    sqlite3 $DB 'delete from pvs where elemName="sh1g6c17b" and pv like "SR:C%SH1-P%"'
    sqlite3 $DB 'delete from pvs where elemName="sh1g2c18a" and pv like "SR:C%SH1-P%"'
    sqlite3 $DB 'delete from pvs where elemName="sh4g2c18a" and pv like "SR:C%SH4-P%"'
    sqlite3 $DB 'delete from pvs where elemName="sh3g2c18a" and pv like "SR:C%SH3-P%"'

    # SH1 DW28, both sides 
    sqlite3 $DB 'delete from pvs where elemName="sh4g6c27b" and pv like "SR:C%SH4-P%"'
    sqlite3 $DB 'delete from pvs where elemName="sh3g6c27b" and pv like "SR:C%SH3-P%"'
    sqlite3 $DB 'delete from pvs where elemName="sh1g6c27b" and pv like "SR:C%SH1-P%"'
    sqlite3 $DB 'delete from pvs where elemName="sh1g2c28a" and pv like "SR:C%SH1-P%"'
    sqlite3 $DB 'delete from pvs where elemName="sh4g2c28a" and pv like "SR:C%SH4-P%"'
    sqlite3 $DB 'delete from pvs where elemName="sh3g2c28a" and pv like "SR:C%SH3-P%"'
fi

if false; then
    echo "Set DW08 SH1,2,3 SP"
    sqlite3 $DB 'insert into pvs(pv,elemName,elemHandle,elemField,tags) values("SR:C08-MG{PS:SH1-DW08}I:Sp1-SP","sh1g6c07b","put","b2","aphla.sys.SR")'
    sqlite3 $DB 'insert into pvs(pv,elemName,elemHandle,elemField,tags) values("SR:C08-MG{PS:SH1-DW08}I:Sp1-SP","sh1g2c08a","put","b2","aphla.sys.SR")'

    sqlite3 $DB 'insert into pvs(pv,elemName,elemHandle,elemField,tags) values("SR:C08-MG{PS:SH3-DW08}I:Sp1-SP","sh3g6c07b","put","b2","aphla.sys.SR")'
    sqlite3 $DB 'insert into pvs(pv,elemName,elemHandle,elemField,tags) values("SR:C08-MG{PS:SH3-DW08}I:Sp1-SP","sh3g2c08a","put","b2","aphla.sys.SR")'

    sqlite3 $DB 'insert into pvs(pv,elemName,elemHandle,elemField,tags) values("SR:C08-MG{PS:SH4-DW08}I:Sp1-SP","sh4g6c07b","put","b2","aphla.sys.SR")'
    sqlite3 $DB 'insert into pvs(pv,elemName,elemHandle,elemField,tags) values("SR:C08-MG{PS:SH4-DW08}I:Sp1-SP","sh4g2c08a","put","b2","aphla.sys.SR")'

    sqlite3 $DB 'insert into pvs(pv,elemName,elemHandle,elemField,tags) values("SR:C08-MG{PS:SH1-DW08}I:Ps1DCCT1-I","sh1g6c07b","get","b2","aphla.sys.SR")'
    sqlite3 $DB 'insert into pvs(pv,elemName,elemHandle,elemField,tags) values("SR:C08-MG{PS:SH1-DW08}I:Ps1DCCT1-I","sh1g2c08a","get","b2","aphla.sys.SR")'

    sqlite3 $DB 'insert into pvs(pv,elemName,elemHandle,elemField,tags) values("SR:C08-MG{PS:SH3-DW08}I:Ps1DCCT1-I","sh3g6c07b","get","b2","aphla.sys.SR")'
    sqlite3 $DB 'insert into pvs(pv,elemName,elemHandle,elemField,tags) values("SR:C08-MG{PS:SH3-DW08}I:Ps1DCCT1-I","sh3g2c08a","get","b2","aphla.sys.SR")'

    sqlite3 $DB 'insert into pvs(pv,elemName,elemHandle,elemField,tags) values("SR:C08-MG{PS:SH4-DW08}I:Ps1DCCT1-I","sh4g6c07b","get","b2","aphla.sys.SR")'
    sqlite3 $DB 'insert into pvs(pv,elemName,elemHandle,elemField,tags) values("SR:C08-MG{PS:SH4-DW08}I:Ps1DCCT1-I","sh4g2c08a","get","b2","aphla.sys.SR")'

    echo "Set DW18 SH1,2,3 SP"
    sqlite3 $DB 'insert into pvs(pv,elemName,elemHandle,elemField,tags) values("SR:C18-MG{PS:SH1-DW18}I:Sp1-SP","sh1g6c17b","put","b2","aphla.sys.SR")'
    sqlite3 $DB 'insert into pvs(pv,elemName,elemHandle,elemField,tags) values("SR:C18-MG{PS:SH1-DW18}I:Sp1-SP","sh1g2c18a","put","b2","aphla.sys.SR")'

    sqlite3 $DB 'insert into pvs(pv,elemName,elemHandle,elemField,tags) values("SR:C18-MG{PS:SH3-DW18}I:Sp1-SP","sh3g6c17b","put","b2","aphla.sys.SR")'
    sqlite3 $DB 'insert into pvs(pv,elemName,elemHandle,elemField,tags) values("SR:C18-MG{PS:SH3-DW18}I:Sp1-SP","sh3g2c18a","put","b2","aphla.sys.SR")'

    sqlite3 $DB 'insert into pvs(pv,elemName,elemHandle,elemField,tags) values("SR:C18-MG{PS:SH4-DW18}I:Sp1-SP","sh4g6c17b","put","b2","aphla.sys.SR")'
    sqlite3 $DB 'insert into pvs(pv,elemName,elemHandle,elemField,tags) values("SR:C18-MG{PS:SH4-DW18}I:Sp1-SP","sh4g2c18a","put","b2","aphla.sys.SR")'

    sqlite3 $DB 'insert into pvs(pv,elemName,elemHandle,elemField,tags) values("SR:C18-MG{PS:SH1-DW18}I:Ps1DCCT1-I","sh1g6c17b","get","b2","aphla.sys.SR")'
    sqlite3 $DB 'insert into pvs(pv,elemName,elemHandle,elemField,tags) values("SR:C18-MG{PS:SH1-DW18}I:Ps1DCCT1-I","sh1g2c18a","get","b2","aphla.sys.SR")'

    sqlite3 $DB 'insert into pvs(pv,elemName,elemHandle,elemField,tags) values("SR:C18-MG{PS:SH3-DW18}I:Ps1DCCT1-I","sh3g6c17b","get","b2","aphla.sys.SR")'
    sqlite3 $DB 'insert into pvs(pv,elemName,elemHandle,elemField,tags) values("SR:C18-MG{PS:SH3-DW18}I:Ps1DCCT1-I","sh3g2c18a","get","b2","aphla.sys.SR")'

    sqlite3 $DB 'insert into pvs(pv,elemName,elemHandle,elemField,tags) values("SR:C18-MG{PS:SH4-DW18}I:Ps1DCCT1-I","sh4g6c17b","get","b2","aphla.sys.SR")'
    sqlite3 $DB 'insert into pvs(pv,elemName,elemHandle,elemField,tags) values("SR:C18-MG{PS:SH4-DW18}I:Ps1DCCT1-I","sh4g2c18a","get","b2","aphla.sys.SR")'

    echo "Set DW28 SH1,2,3 SP"
    sqlite3 $DB 'insert into pvs(pv,elemName,elemHandle,elemField,tags) values("SR:C28-MG{PS:SH1-DW28}I:Sp1-SP","sh1g6c27b","put","b2","aphla.sys.SR")'
    sqlite3 $DB 'insert into pvs(pv,elemName,elemHandle,elemField,tags) values("SR:C28-MG{PS:SH1-DW28}I:Sp1-SP","sh1g2c28a","put","b2","aphla.sys.SR")'

    sqlite3 $DB 'insert into pvs(pv,elemName,elemHandle,elemField,tags) values("SR:C28-MG{PS:SH3-DW28}I:Sp1-SP","sh3g6c27b","put","b2","aphla.sys.SR")'
    sqlite3 $DB 'insert into pvs(pv,elemName,elemHandle,elemField,tags) values("SR:C28-MG{PS:SH3-DW28}I:Sp1-SP","sh3g2c28a","put","b2","aphla.sys.SR")'

    sqlite3 $DB 'insert into pvs(pv,elemName,elemHandle,elemField,tags) values("SR:C28-MG{PS:SH4-DW28}I:Sp1-SP","sh4g6c27b","put","b2","aphla.sys.SR")'
    sqlite3 $DB 'insert into pvs(pv,elemName,elemHandle,elemField,tags) values("SR:C28-MG{PS:SH4-DW28}I:Sp1-SP","sh4g2c28a","put","b2","aphla.sys.SR")'

    sqlite3 $DB 'insert into pvs(pv,elemName,elemHandle,elemField,tags) values("SR:C28-MG{PS:SH1-DW28}I:Ps1DCCT1-I","sh1g6c27b","get","b2","aphla.sys.SR")'
    sqlite3 $DB 'insert into pvs(pv,elemName,elemHandle,elemField,tags) values("SR:C28-MG{PS:SH1-DW28}I:Ps1DCCT1-I","sh1g2c28a","get","b2","aphla.sys.SR")'

    sqlite3 $DB 'insert into pvs(pv,elemName,elemHandle,elemField,tags) values("SR:C28-MG{PS:SH3-DW28}I:Ps1DCCT1-I","sh3g6c27b","get","b2","aphla.sys.SR")'
    sqlite3 $DB 'insert into pvs(pv,elemName,elemHandle,elemField,tags) values("SR:C28-MG{PS:SH3-DW28}I:Ps1DCCT1-I","sh3g2c28a","get","b2","aphla.sys.SR")'

    sqlite3 $DB 'insert into pvs(pv,elemName,elemHandle,elemField,tags) values("SR:C28-MG{PS:SH4-DW28}I:Ps1DCCT1-I","sh4g6c27b","get","b2","aphla.sys.SR")'
    sqlite3 $DB 'insert into pvs(pv,elemName,elemHandle,elemField,tags) values("SR:C28-MG{PS:SH4-DW28}I:Ps1DCCT1-I","sh4g2c28a","get","b2","aphla.sys.SR")'

fi

if false; then
    idx=990000
    #for name in "057" "058"
    for name in "037" "038" "057" "058" "059" "087" "088" "107" "108" "117" "118" "187" "188" "237" "238" "239" "287" "288" "307" "308" "309" "3010"
    do
        echo "Adding new BPM: C${name:0:2}-BPM:${name:2}"
        idx=$((idx+1))
	sqlite3 $DB "insert into elements(elemName,elemType,cell,elemLength) values(\"p_c${name:0:2}_bpm${name:2}\", \"_BPM\", \"C${name:0:2}\", 0.0)"
	sqlite3 $DB "insert into pvs(pv,elemName,elemHandle,elemField,tags) values(\"SR:C${name:0:2}-BI{BPM:${name:2}}Pos:X-I\", \"p_c${name:0:2}_bpm${name:2}\", \"get\", \"x\", \"aphla.sys.SR\")"
	sqlite3 $DB "insert into pvs(pv,elemName,elemHandle,elemField,tags) values(\"SR:C${name:0:2}-BI{BPM:${name:2}}Pos:Y-I\", \"p_c${name:0:2}_bpm${name:2}\", \"get\", \"y\", \"aphla.sys.SR\")"
     done
fi

if false; then
    idx=990000
    #for name in "057" "058"
    for name in "037" "038" "057" "058" "059" "087" "088" "107" "108" "117" "118" "187" "188" "237" "238" "239" "287" "288" "307" "308" "309" "3010"
    do
	idx=$((idx+1))
	sqlite3 $DB "update elements set elemIndex=${idx} where elemName=\"p_c${name:0:2}_bpm${name:2}\" "
    done
fi

if true; then
    echo "Adding dcct, rfcavity and tune"
    #sqlite3 $DB "insert into elements(elemName,elemType,cell,elemLength,elemIndex) values(\"dcct\", \"DCCT\", \"\", 0.0, -100)"
    #sqlite3 $DB "insert into elements(elemName,elemType,cell,elemLength,elemIndex) values(\"rfcavity\", \"RFCAVITY\", \"\", 0.0, -200)"
    #sqlite3 $DB "insert into elements(elemName,elemType,cell,elemLength,elemIndex) values(\"tune\", \"TUNE\", \"\", 0.0, -300)"
    #sqlite3 $DB "insert into pvs(pv,elemName,elemHandle,elemField,tags) values(\"SR:C16-BI{TuneNA}Freq:Vx-I\", \"tune\", \"get\", \"x\", \"aphla.sys.SR\")"
    #sqlite3 $DB "insert into pvs(pv,elemName,elemHandle,elemField,tags) values(\"SR:C16-BI{TuneNA}Freq:Vy-I\", \"tune\", \"get\", \"y\", \"aphla.sys.SR\")"
    #sqlite3 $DB "insert into pvs(pv,elemName,elemHandle,elemField,tags) values(\"RF{Osc:1}Freq:I\", \"rfcavity\", \"get\", \"f\", \"aphla.sys.SR\")"
    #sqlite3 $DB "insert into pvs(pv,elemName,elemHandle,elemField,tags) values(\"RF{Osc:1}Freq:SP\", \"rfcavity\", \"put\", \"f\", \"aphla.sys.SR\")"
    # place holder
    #sqlite3 $DB "insert into pvs(pv,elemName,elemHandle,elemField,tags) values(\"_RF_V:I\", \"rfcavity\", \"get\", \"v\", \"aphla.sys.SR\")"
    #sqlite3 $DB "insert into pvs(pv,elemName,elemHandle,elemField,tags) values(\"_RF_V:SP\", \"rfcavity\", \"put\", \"v\", \"aphla.sys.SR\")"
    #sqlite3 $DB "insert into pvs(pv,elemName,elemHandle,elemField,tags) values(\"SR:C03-BI{DCCT:1}Lifetime-I\", \"dcct\", \"get\", \"tau\", \"aphla.sys.SR\")"
    #sqlite3 $DB "insert into pvs(pv,elemName,elemHandle,elemField,tags) values(\"SR:C03-BI{DCCT:1}AveI-I\", \"dcct\", \"get\", \"Iavg\", \"aphla.sys.SR\")"
    #sqlite3 $DB "insert into pvs(pv,elemName,elemHandle,elemField,tags) values(\"SR:C03-BI{DCCT:1}I:Total-I\", \"dcct\", \"get\", \"I\", \"aphla.sys.SR\")"
fi

if false; then
    for i in 1 3 5 7 9 11 13 15 17 19 21 23 25 27 29
    do
	echo "C$i"
    done
fi

#SR:C18-MG{PS:SH1-DW18}I:Sp1-SP
#SR:C18-MG{PS:SH3-DW18}I:Sp1-SP
#SR:C18-MG{PS:SH4-DW18}I:Sp1-SP

#SR:C28-MG{PS:SH1-DW28}I:Sp1-SP
#SR:C28-MG{PS:SH3-DW28}I:Sp1-SP
#SR:C28-MG{PS:SH4-DW28}I:Sp1-SP
