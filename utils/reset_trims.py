import os
import re
from cothread.catools import caget, caput

if __name__ == "__main__":
    f = open('../machine/nsls2/pvlist_2011_04_08.txt', 'r')
    for pv in f.readlines():
        if not pv.endswith('-SP\n'): continue
        if pv.find('Cor:') < 0: continue
        pv = pv.strip()
        k = caget(pv.encode('ascii'))
        if abs(k) > 0.0: 
            print pv, k
            caput(pv, 0.0)
