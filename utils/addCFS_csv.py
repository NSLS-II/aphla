#!/usr/bin/env python

import sys
import aphla as ap

conv_int = ['ordinal']
conv_float = ['sEnd', 'length']
conv_empty = ['elemField']

def import_explicit_csv(cfa, filename):
    for sline in open(filename, 'r').readlines():
        if sline.find('elemName') < 0:
            print "skipping line:", sline.strip()
            continue
        spv, sprpts, stags = sline.split(';')
        # 
        pv = spv.strip()
        prpts = {}
        for rec in sprpts.split(','):
            k, v = [v.strip() for v in rec.split('=')]
            if k in conv_int:
                v = int(v)
            elif k in conv_float:
                v = float(v)
            elif k in conv_empty:
                v = ''
            prpts[k] = v
        tags = [t.strip() for t in stags.split(',')]
        cfa.update(pv, prpts, tags)
    

        
if __name__ == "__main__":
    cfa = ap.ChannelFinderAgent()
    if len(sys.argv) > 2:
        cfa.importCsv(sys.argv[1])
        import_explicit_csv(cfa, sys.argv[2])
    else:
        import_explicit_csv(cfa, sys.argv[1])

    cfa.exportCsv('output.csv')


