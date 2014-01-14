import os
import aphla as ap
from aphla.machines import utils

if __name__ == "__main__":
    fs1, fs2 = "va_elements.txt", "va_pvs.csv"
    f1, f2, f3 = "test_elem.txt", "test_pvs.txt", "v2sr.sqlite"
    utils.convNSLS2LatTable(f1, fs1)
    utils.convVirtAccPvs(f2, fs2)
    utils.createSqliteDb(f3, f1, f2, latname="V2SR", system="V:2-SR")

    os.remove(f1)
    os.remove(f2)
    #convVirtAccTwiss(f1, "./tpsv1/tps-twiss.txt", grpname=True)
    #convVirtAccPvs(f2, "./tpsv1/TDMB1826_OB_Chamb_ID.csv")
    #createSqliteDb(f3, f1, f2, name_index=True)


