import os
import aphla as ap
from aphla.machines import utils

CFS_URL=''

def download_nsls2_cfs(url):
    pass

if __name__ == "__main__":
    download_nsls2_cfs()
    fs1, fs2 = "va_elements.txt", "va_pvs.csv"
    f1, f2, f3 = "test_elem.txt", "test_pvs.txt", "v2sr.sqlite"
    utils.convNSLS2LatTable(f1, fs1)
    utils.convVirtAccPvs(f2, fs2)
    utils.createSqliteDb(f3, f1, f2, latname="SR", system="SR")

    os.remove(f1)
    os.remove(f2)
    #convVirtAccTwiss(f1, "./tpsv1/tps-twiss.txt", grpname=True)
    #convVirtAccPvs(f2, "./tpsv1/TDMB1826_OB_Chamb_ID.csv")
    #createSqliteDb(f3, f1, f2, name_index=True)


