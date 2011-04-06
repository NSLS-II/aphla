#!/usr/bin/env python

import shelve
import hla

def renameElement():
    lat = hla.lattice.Lattice()
    pkl = '/home/lyyang/devel/nsls2-hla/machine/nsls2/hla.pkl'
    f = shelve.open(pkl, 'w', writeback=True)
    print f.keys()
    mode = 'virtac'
    for elem in f['lat.'+mode+'.element']:
        if elem.name.find('CF') == 0:
            print "%s -> %s" % (elem.name, elem.name[1:])
            elem.name = elem.name[1:]
    for g,v in f['lat.'+mode+'.group'].items():
        for i,elem in enumerate(v):
            if elem.find('X') == 0 or elem.find('Y') == 0: 
                f['lat.'+mode+'.group'][g][i] = 'F' + elem
                print g, elem, f['lat.'+mode+'.group'][g][i]
        #print ""

    f.close()

if __name__ == "__main__":
    renameElement()

