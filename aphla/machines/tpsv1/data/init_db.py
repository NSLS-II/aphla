import os
import aphla as ap
from aphla.machines import utils

if __name__ == "__main__":
    fs1, fs2 = "va_twiss.txt", "va_pvs.csv"
    f1, f2, f3 = "test_elem.txt", "test_pvs.txt", "tps_v1sr.sqlite"

    utils.convVirtAccTwiss(f1, fs1, grpname=True)
    utils.convVirtAccPvs(f2, fs2)
    utils.createSqliteDb(f3, f1, f2, name_index=True)

    os.remove(f1)
    os.remove(f2)

