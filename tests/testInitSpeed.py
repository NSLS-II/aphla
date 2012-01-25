#!/usr/bin/env python

import sys

def load_cache():
    import hla
    hla.machines.loadCache()
    

def load_cf():
    import hla
    hla.initNSLS2VSR()

def load_txt():
    import hla
    hla.machines.initNSLS2VSRTxt()

if __name__ == "__main__":
    if len(sys.argv) <= 1:
        print sys.argv[0], "[--cache | --cf | --txt]"
    elif sys.argv[1] == '--cache':
        load_cache()
    elif sys.argv[1] == '--cf':
        load_cf()
    elif sys.argv[1] == '--txt':
        load_txt()
    else:
        pass


