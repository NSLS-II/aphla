#!/usr/env/python

import re
from math import log10
import shelve
from . import INF
import numpy as np
from fnmatch import fnmatch

from cothread.catools import caget, caput

def parseElementName(name):
    # for NSLS-2 convention of element name
    a = re.match(r'.+(G\d{1,2})(C\d{1,2})(.)', name)
    if a:
        girder   = a.groups()[0]
        cell     = a.groups()[1]
        symmetry = a.groups()[2]
    elif name == "CAVITY":
        # fix a broken name
        girder   = "CAVITY"
        cell     = "CAVITY"
        symmetry = "CAVITY"
    else:
        girder   = 'G0'
        cell     = 'C00'
        symmetry = '0'
    return cell, girder, symmetry


class Element:
    def __init__(self, name = '', family = '', s_beg = 0.0, s_end = 0.0,
                 effective_length = 0, cell = 0, girder = 0, symmetry = '',
                 sequence = [0, 0]):
        self.index = -1
        self.name = name
        self.family = family
        self.s_beg = s_beg
        self.s_end = s_end
        self.len_eff = effective_length
        self.len_phy = 0.0
        self.cell = cell
        self.girder = girder
        self.symmetry = symmetry
        self.sequence = sequence[:]

class Twiss:
    def __init__(self):
        self.s     = np.zeros(3, 'd')
        self.alpha = np.zeros((3, 2), 'd')
        self.beta  = np.zeros((3, 2), 'd')
        self.gamma = np.zeros((3, 2), 'd')
        self.eta   = np.zeros((3, 2), 'd')
        self.phi   = np.zeros((3, 2), 'd')
        self.elemname = ''
        
class Lattice:
    def __init__(self):
        self.__group = {}
        self.element = []
        self.twiss = []
        self.mode = ''
        self.tune = [ 0.0, 0.0]
        self.chromaticity = [0.0, 0.0]

    def save(self, fname, dbmode = 'c'):
        """
        call signature::
        
          save(self, fname, dbmode='c')

        save the lattice into binary data, using writing *dbmode*
        """
        f = shelve.open(fname, dbmode)
        f['lat.group']   = self.__group
        f['lat.element'] = self.element
        f['lat.twiss']   = self.twiss
        f['lat.mode']    = self.mode
        f.close()

    def load(self, fname, mode = 'default'):
        """
        call signature::
        
          load(self, fname, mode='default')

        load the lattice from binary data
        """
        f = shelve.open(fname, 'r')
        self.__group  = f['lat.group']
        self.element  = f['lat.element']
        self.twiss    = f['lat.twiss']
        self.mode     = f['lat.mode']
        f.close()

    def importLatticeTable(self, lattable):
        """
        call signature::
        
          importLatticeTable(self, lattable)

        Import the table used for Tracy-VirtualIOC. The table has columns
        in the following order:

        =======   =============================================
        Index     Description
        =======   =============================================
        1         element index in the whole beam line
        2         channel for read back
        3         channel for set point
        4         element phys name (unique)
        5         element length (effective)
        6         s location of its exit
        7         magnet family(type)
        =======   =============================================

        Data are deliminated by spaces.
        """

        print "Importing file:", lattable

        cnt = {'BPM':0, 'TRIMD':0, 'TRIMX':0, 'TRIMY':0, 'SEXT':0, 'QUAD':0}

        f = open(lattable, 'r').readlines()
        for s in f[1:]:
            t = s.split()
            idx  = int(t[0])     # index
            rb   = t[1].strip()  # PV readback
            sp   = t[2].strip()  # PV setpoint
            phy  = t[3].strip()  # name
            L    = float(t[4])   # length
            s2   = float(t[5])   # s_end location
            grp  = t[6].strip()  # group

            # parse cell/girder/symmetry from name
            cell, girder, symmetry = parseElementName(phy)
            self.element.append(Element(phy, grp, 0.0, s2, L,
                                        cell, girder, symmetry))
            self.element[-1].index = idx

            # count element numbers in each type
            if cnt.has_key(grp): cnt[grp] += 1

            if self.__group.has_key(grp): self.__group[grp].append(phy)
            else: self.__group[grp] = [phy]
        # adjust s_beg
        for e in self.element:
            e.s_beg = e.s_end - e.len_eff

    def init_virtac_twiss(self):
        """Only works from virtac.nsls2.bnl.gov"""
        # s location
        s = caget('SR:C00-Glb:G00<POS:00>RB-S')
        alphax = caget('SR:C00-Glb:G00<ALPHA:00>RB-X')
        alphay = caget('SR:C00-Glb:G00<ALPHA:00>RB-Y')
        betax  = caget('SR:C00-Glb:G00<BETA:00>RB-X')
        betay  = caget('SR:C00-Glb:G00<BETA:00>RB-Y')
        etax   = caget('SR:C00-Glb:G00<ETA:00>RB-X')
        etay   = caget('SR:C00-Glb:G00<ETA:00>RB-Y')
        orbx   = caget('SR:C00-Glb:G00<ORBIT:00>RB-X')
        orby   = caget('SR:C00-Glb:G00<ORBIT:00>RB-Y')
        phix   = caget('SR:C00-Glb:G00<PHI:00>RB-X')
        phiy   = caget('SR:C00-Glb:G00<PHI:00>RB-Y')
        nux = caget('SR:C00-Glb:G00<TUNE:00>RB-X')
        nuy = caget('SR:C00-Glb:G00<TUNE:00>RB-Y')
        print len(s), s[0], s[-1]
        print len(alphax), s[0], s[-1]
        print len(alphay), s[0], s[-1]
        print len(betax), s[0], s[-1]
        print len(betay), s[0], s[-1]
        print len(etax), s[0], s[-1]
        print len(etay), s[0], s[-1]
        print len(orbx), len(orby)
        print len(phix), len(phiy)
        #return None
        
        for e in self.element:
            i = e.index
            #print e.name, e.family, s[i]
            if i >= len(s): 
                print "Missing element in PV waveform", e.name, e.family
                continue
            self.twiss.append(Twiss())
            self.twiss[-1].s[-1]       = s[i]
            self.twiss[-1].beta[-1,0] = betax[i]
            self.twiss[-1].beta[-1,1] = betay[i]
            self.twiss[-1].alpha[-1,0]= alphax[i]
            self.twiss[-1].alpha[-1,1]= alphay[i]
            self.twiss[-1].eta[-1,0]  = etax[i]
            self.twiss[-1].eta[-1,1]  = etay[i]
            self.twiss[-1].phi[-1,0]  = phix[i]
            self.twiss[-1].phi[-1,1]  = phiy[i]
            
    def getElements(self, group, point = ''):
        ret, loc = [], []
        s = point.lower()
        for e in self.element:
            if fnmatch(group, e.name) or fnmatch(group, e.family):
                ret.append(e.name)
                if s == 'begin': loc.append(e.s_beg)
                elif s == 'end': loc.append(e.s_end)
                elif s == 'middle': loc.append(e.s_mid)
                else: loc.append(e.s_end())
        if point: return ret, loc
        else: return ret

    def __repr__(self):
        s = ''
        ml_name, ml_family = 0, 0
        for e in self.element:
            if len(e.name) > ml_name: ml_name = len(e.name)
            if len(e.family) > ml_family: ml_family = len(e.family)

        idx = int(1.0+log10(len(self.element)))
        fmt = "%%%dd %%%ds  %%%ds  %%9.4f  %%9.4f\n" % (idx, ml_name, ml_family)
        #print fmt
        for i, e in enumerate(self.element):
            s = s + fmt % (i, e.name, e.family, e.s_beg, e.s_end)
        return s


