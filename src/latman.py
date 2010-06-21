#!/usr/bin/env python

class LatticeManager:
    def __init__(self, db):
        dat = open(db, "r").readlines()
        self.idx, self.elem, self.group, self.s = [], [], [], []
        self.pvrb, self.pvsp = [], []
        for line in dat:
            d = line.split()
            self.idx.append(int(d[0]))
            self.elem.append(d[1])
            self.pvrb.append(d[2].strip()[1:-1])
            self.pvsp.append(d[3].strip()[1:-1])
            self.group.append(d[4])
            self.s.append(float(d[5]))

    def pvindex(self, pv):
        if pv in self.pvrb:
            return self.idx[self.pvrb.index(pv)]
        elif pv in self.pvsp:
            return self.idx[self.pvsp.index(pv)]
        else:
            return -1
        
    def s_end(self, pv):
        i = self.pvindex(pv)
        if i >= 0:
            return self.s[self.idx.index(i)]
    def group_index(self, grp):
        idx = []
        for i in range(len(self.group)):
            if grp == self.group[i].strip():
                idx.append(self.idx[i])
        return idx

    
