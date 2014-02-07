import os
import aphla as ap
from aphla.machines import utils

if __name__ == "__main__":
    #fs1, fs2 = "va_twiss.txt", "va_pvs.csv"
    fs1, fs2 = "va_twiss.txt", "TDMB1826_OB_Chamb_ID.csv"
    f1, f2, f3 = "test_elem.txt", "test_pvs.txt", "tps_v1sr.sqlite"
    drifts = [v.strip().lower()
              for v in open('twiss_skipped_elements.txt', 'r').readlines()
              if not v.startswith("#")]
    utils.convVirtAccTwiss(f1, fs1, grpname=True,
                           index_step=100, skip_elements=drifts)
    f = open(f1, 'a')
    f.write("twiss:_1,-1,,0.0,0.0,0.0,,,,\n")
    #f.write("twiss:_1,-1,,0.0,0.0,0.0,,,,\n")
    #f.write("twiss:_1,-1,,0.0,0.0,0.0,,,,\n")
    f.close()
    utils.convVirtAccPvs(f2, fs2, grpname=True)
    utils.createSqliteDb(f3, f1, f2, name_index=True, virtual_elems=[])

    #os.remove(f1)
    #os.remove(f2)

    cfa = ap.chanfinder.ChannelFinderAgent()
    cfa.loadSqlite("tps_v1sr.sqlite")
    cfa._save_csv_2("tps_v1sr.csv")
