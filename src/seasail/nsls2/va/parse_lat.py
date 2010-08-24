#!/usr/bin/env python
"""
This script parses a flat lattice configuration file,
generate a lattice deck for tracy, and an EPICS database for virtual ioc.
"""
from time import gmtime, strftime
import re
import odict

class parse_lat:
    def __init__(self, file='', *argv):
        if file != '':
            self.lattice = file
    
    def read(self):
        f = open(self.lattice, 'r')
        self.elements = f.readlines()
        f.close()
    
    def getAllElem(self):
        return self.elements

class gen_tracy:
    def __init__(self, elems = '', ring='', cell = 'C30', gird = 'G1'):
        self.elems = elems
        self.ringCur = ring
        self.cellCur = cell
        self.girdCur = gird
        
        self.ring = 'RING: '
        self.cell = odict.odict({})
        self.gird = odict.odict({})

        self.elemTypeMap = {
            'DRIF':    'Drift',
            'FTRIM':   'Corrector',
            'TRIMD':   'Corrector',
            'BPM':     'Beam Position Monitor',
            'MARK':    'Marker',
            'DIPOLE':  'Dipole',
            'QUAD':    'Quadrupole',
            'SEXT':    'Sextupole',
            'SQ_TRIM': 'Quadrupole',
            }

        self.drifSeq = {}
        self.bendSeq = {}
        self.quadSeq = {}
        self.sextSeq = {}

        self.corrSeq = {}
        self.markSeq = {}
        self.bpmSeq = {}

    def tracyHead(self):
        t = strftime("%a, %d %b %Y, %H:%M:%S %Z")
        head =  '{****************************************}\n'
        head += '{*                                      *}\n'
        head += '{*       NSLS-II Storage Ring           *}\n'
        head += '{*            Bare Lattice              *}\n'
        head += '{*                                      *}\n'
        head += '{* %s by GS *}\n'%t
        head += '{*                                      *}\n'
        head += '{****************************************}\n'

        return head

    def tracyGlobal(self, energy='3.00', dP='1.0e-10', CODeps='1.0e-12',
                    Meth = '4', Nbend = '4', Nquad = '4', Nsext = '1',
                    h_rf = '1320', C = '791.958'):
        tglob = 'define lattice; ringtype=1;\n'
        tglob += 'Meth = %s; Nbend = %s; Nquad = %s; Nsext = %s;\n'  \
                 %(Meth, Nbend, Nquad, Nsext)
        tglob += 'pi = 4.0*arctan(1.0);\n'
        tglob += 'dP = %s; CODeps = %s;\n' %(dP, CODeps)
        tglob += 'c0 = 2.99792458e8; h_rf = %s; C = %s;\n' %(h_rf, C)
        tglob += '\n{***** System parameters *****}\n'
        tglob += 'Energy = %s;   {GeV}\n' %energy

        return tglob

    def tracyTail(self, ring='RING'):
        tail = 'CELL: %s, SYMMETRY = 1;' %ring
        tail += '\nEND;'

        return tail

    def rfElem(self, freq = 'c0/C*h_rf', volt = '5.00e6', harnum = 'h_rf'):
        return 'CAV: Cavity, Frequency = %s, Voltage = %s, Harnum = %s;\n' \
               %(freq, volt, harnum)

    def buildSeq(self):
        for elem in self.elems:
            if not (elem.startswith('!') or elem.startswith('#')):
                attrs = elem.split()
                self.dispatch(attrs)

    def getElemType(self, etype):
        try:
            elemType = self.elemTypeMap[etype]
        except:
            print 'Element type [%s] does not exist in map.' % etype
            elemType = ''
        return elemType

    def addElem(self, cell, gird, elem):
        elemId = elem
        cellId = cell

        if cell == '':
            cellId = self.cellCur
        
        if self.cellCur != cellId:
            if self.cell.has_key(cellId):
                cellId += 'H'
            self.cellCur = cellId

        if gird == '':
            girdId = self.girdCur
        else:
            girdId = gird + cellId

        if self.girdCur != girdId:
            self.girdCur = girdId
        
        if self.gird.has_key(self.girdCur):
            el = self.gird[self.girdCur]
            el.append(elemId)
            self.gird.update({self.girdCur:el})
        else:
            self.gird[self.girdCur] = [elemId]
            
            if self.cell.has_key(self.cellCur):
                cl = self.cell[self.cellCur]
                cl.append(girdId)
                self.cell.update({self.cellCur:cl})
            else:
                self.cell[self.cellCur] = [girdId]

        ## if self.cell.has_key(self.cellCur):
        ##     self.cell[self.cellCur].append(girdId)
        ## else:
        ##     self.cell[self.cellCur] = [girdId]
        
    def mark(self, attrs):
        gird = attrs[0].find('G', 2)
        elemId = attrs[0][0:gird]

        if not self.markSeq.has_key(elemId):
            self.markSeq[elemId] = ('%s: Marker;' %elemId)

        girdId = attrs[0][gird:gird+2]

        cell = attrs[0].find('C', 2)
        if cell != -1:
            cellId = attrs[0][cell:cell+3]
        else:
            cellId = self.cellCur

        self.addElem(cellId, girdId, elemId)

    def drif(self, attrs):
        gird = attrs[0].find('G', 2)
        elemId = attrs[0]

        if not self.drifSeq.has_key(elemId):
            self.drifSeq[elemId] = '%s: Drift, L = %s;' %(elemId, attrs[2])

        girdId = attrs[0][gird:gird+2]

        # Drift section does not have cell information
        ## cell = attrs[0].find('C', 2)
        ## if cell != -1:
        ##     cellId = attrs[0][cell:cell+3]
        ## else:
        ##     cellId = self.cellCur
        cellId = self.cellCur

        self.addElem(cellId, girdId, elemId)
    
    def quad(self, attrs):
        gird = attrs[0].find('G', 2)
        elemId = attrs[0][0:gird]

        if not self.quadSeq.has_key(elemId):
            self.quadSeq[elemId] = \
                '%s: Quadrupole, L = %s, K = %s, N = Nquad, Method = Meth;' \
                %(elemId, attrs[2], attrs[4])

        girdId = attrs[0][gird:gird+2]

        cell = attrs[0].find('C', 2)
        if cell != -1:
            cellId = attrs[0][cell:cell+3]
        else:
            cellId = self.cellCur

        self.addElem(cellId, girdId, elemId)    

    # Skew Quadrupole include a skew quad and 2 correctors (H, V)
    def squad(self, attrs):
        self.quad(attrs)
        self.corr(attrs)
        
    def sext(self, attrs):
        gird = attrs[0].find('G', 2)
        elemId = attrs[0][0:gird]

        strength = '%.5f' %(float(attrs[5])/2.0)
        if not self.sextSeq.has_key(elemId):
            self.sextSeq[elemId] = \
                '%s: Sextupole, L = %s, K = %s, N = Nsext, Method = Meth;' \
                %(elemId, attrs[2], strength)

        girdId = attrs[0][gird:gird+2]

        cell = attrs[0].find('C', 2)
        if cell != -1:
            cellId = attrs[0][cell:cell+3]
        else:
            cellId = self.cellCur

        self.addElem(cellId, girdId, elemId)
    
    
    def bpm(self, attrs):
        gird = attrs[0].find('G', 2)
        elemId = attrs[0][0:gird]

        if not self.bpmSeq.has_key(elemId):
            self.bpmSeq[elemId] = ('%s: Beam Position Monitor;' %elemId)

        girdId = attrs[0][gird:gird+2]

        cell = attrs[0].find('C', 2)
        if cell != -1:
            cellId = attrs[0][cell:cell+3]
        else:
            cellId = self.cellCur

        self.addElem(cellId, girdId, elemId)
    
    def bend(self, attrs):
        import math
        gird = attrs[0].find('G', 2)
        elemId = attrs[0][0:gird]

        angle = float(attrs[6])*180/math.pi

        angleH = '%.2f' %(angle/2.0)
        angle  = '%.2f' %(angle)
        
        if not self.bendSeq.has_key(elemId):
            self.bendSeq[elemId] = \
                '%s: Bending, L = %s, T = %s, T1 = %s, T2 = %s, N = Nbend, Method = Meth;' \
                %(elemId, attrs[2], angle, angleH, angleH)

        girdId = attrs[0][gird:gird+2]

        cell = attrs[0].find('C', 2)
        if cell != -1:
            cellId = attrs[0][cell:cell+3]
        else:
            cellId = self.cellCur

        self.addElem(cellId, girdId, elemId)
        
    # 2 correctors (H, V)
    def corr(self, attrs):
        gird = attrs[0].find('G', 2)

        if not self.corrSeq.has_key('CH'):
            self.corrSeq['CH'] = ('CH: Corrector, Horizontal, Method= Meth;')
            self.corrSeq['CV'] = ('CV: Corrector, Vertical, Method= Meth;')

        girdId = attrs[0][gird:gird+2]

        cell = attrs[0].find('C', 2)
        if cell != -1:
            cellId = attrs[0][cell:cell+3]
        else:
            cellId = self.cellCur

        if attrs[1] == 'FTRIM':
            self.addElem(cellId, girdId, 'DFC')
            if not self.corrSeq.has_key('DFC'):
                self.drifSeq['DFC'] = ('DFC: Drift, L = %s;' %attrs[2] )

        elif attrs[1] == 'TRIMD':
            if attrs[2] == '0.2':
                self.addElem(cellId, girdId, 'DSC1')
                if not self.corrSeq.has_key('DSC1'):
                    self.drifSeq['DSC1'] = ('DSC1: Drift, L = %s;' %attrs[2])
                    
            else:
                self.addElem(cellId, girdId, 'DSC2')
                if not self.corrSeq.has_key('DSC2'):
                    self.drifSeq['DSC2'] = ('DSC2: Drift, L = %s;' %attrs[2])
            
        self.addElem(cellId, girdId, 'CH')
        self.addElem(cellId, girdId, 'CV')
        
    def dispatch(self, attrs):
        actions = (
            ('DRIF',    self.drif),
            ('FTRIM',   self.corr),
            ('TRIMD',   self.corr),
            ('BPM',     self.bpm),
            ('MARK',    self.mark),
            ('DIPOLE',  self.bend),
            ('QUAD',    self.quad),
            ('SEXT',    self.sext),
            ('SQ_TRIM', self.squad)
            )
        
        for (p, f) in actions:
            if re.match(p, attrs[1]):
                f(attrs)

    def output(self, filename=''):
        self.buildSeq()
        
        lattice = self.tracyHead()
        lattice += self.tracyGlobal()
        lattice += self.rfElem()
        
        lattice += '\n{***** Markers *****}\n'
        for k, v in self.markSeq.items():
            lattice += v +'\n'
            
        lattice += '\n{***** Corrector *****}\n'
        for k, v in self.corrSeq.items():
            lattice += v + '\n'

        lattice += '\n{***** BPM *****}\n'
        for k, v in self.bpmSeq.items():
            lattice += v + '\n'

        lattice += '\n{***** Drift space *****}\n'
        for k, v in self.drifSeq.items():
            lattice += v + '\n'

        lattice += '\n{***** Bending *****}\n'
        for k, v in self.bendSeq.items():
            lattice += v + '\n'
    
        lattice += '\n{***** Quadrupole *****}\n'
        for k, v in self.quadSeq.items():
            lattice += v + '\n'

        lattice += '\n{***** Sextupole *****}\n'
        for k, v in self.sextSeq.items():
            lattice += v + '\n'

        lattice += '\n{***** Sequence *****}\n'
        for k, v in self.gird.items():
            lattice += k + ': '
            countTop = len(k) + 2
            count = countTop
            for s in v:
                if count < 80:
                    count += len(s) + 2
                else:
                    lattice +=  '\n       '
                    count = countTop
                lattice += s + ', '
            lattice = lattice[:-2] + ';\n'

        thering = 'RING: '
        ringcount = len(thering)
        countSP = 0
        for k, v in self.cell.items():
            ## thering += k + ', '
            ## ringcount += len(k + ', ')
            ## if ringcount > 80:
            ##     thering += '\n      '
            ##     ringcount = 6
         
            ## lattice += k + ': '
            countTop = len(k) + 2
            count = countTop
            for s in v:
                if count < 50:
                    count += len(s) + 2
                else:
                    thering +=  '\n       '
                    count = countTop
                thering += s + ', '
            
            if countSP == 1:
                thering += '\n      '
                countSP = 0
            else:
                countSP += 1
            lattice = lattice[:-2] + ';\n'

        ## thering = thering[:-2] + ';\n'
        thering += 'CAV;\n'
        lattice += '\n' + thering

        lattice += '\n'
        lattice += self.tracyTail()
        if filename == '':
            print lattice
        else:
            f = open(filename, 'w')
            f.write_nsls2(lattice)
            f.close()
   

class gen_vioc_db:
    def __init__(self, elems):
        self.elems = elems
        self.index = 0
        self.prevElem = ''
        self.elemList = {}
        self.s = 0
        # RF cavity
        self.freqRB = 'SR:C00-RF:G00<RF:00>Freq-RB'
        self.freqSP = 'SR:C00-RF:G00<RF:00>Freq-SP'
        self.voltRB = 'SR:C00-RF:G00<RF:00>Volt-RB'
        self.voltSP = 'SR:C00-RF:G00<RF:00>Volt-SP'
        self.tuneX  = 'SR:C00-Glb:G00<TUNE:00>RB-X'
        self.tuneY  = 'SR:C00-Glb:G00<TUNE:00>RB-Y'
        self.alphaX = 'SR:C00-Glb:G00<ALPHA:00>RB-X'
        self.alphaY = 'SR:C00-Glb:G00<ALPHA:00>RB-Y'
        self.betaX  = 'SR:C00-Glb:G00<BETA:00>RB-X'
        self.betaY  = 'SR:C00-Glb:G00<BETA:00>RB-Y'
        self.etaX   = 'SR:C00-Glb:G00<ETA:00>RB-X'
        self.etaY   = 'SR:C00-Glb:G00<ETA:00>RB-Y'
        self.phiX   = 'SR:C00-Glb:G00<PHI:00>RB-X'
        self.phiY   = 'SR:C00-Glb:G00<PHI:00>RB-Y'
        self.orbitX = 'SR:C00-Glb:G00<ORBIT:00>RB-X'
        self.orbitY = 'SR:C00-Glb:G00<ORBIT:00>RB-Y'
        self.posS   = 'SR:C00-Glb:G00<POS:00>RB-S'
        self.cur    = 'SR:C00-BI:G00<DCCT:00>CUR-RB'
        self.curCalc = 'SR:C00-BI:G00<DCCT:00>CUR-CALC'

        self.records = []
        self.defaults = {"user": ""}
        self.initrec = []

        index = '#index   read back                       set point' + \
                '                      phys name       len[m]  s[m]' + \
                '    group name\n'
        self.latTable = [index]

    def ao(self, **kw):
        params = dict(self.defaults)
        params.update(kw)
        record = 'record(ao, "%(nameSP)s") {\n'
        record +='    field(OUT, "%(nameCalc)s")\n'
        record +='    field(FLNK, "%(nameCalc)s")\n'
        record +='    }\n'
        record +='record(calc, "%(nameCalc)s") {\n'
        record +='    field(CALC, "((RNDM*2-1)*0.0005 + 1) * A")\n'
        record +='    field(INPA, "%(nameSP)s")\n'
        record +='    field(FLNK, "%(nameSet)s")\n'
        record +='    }\n'
        record +='record(ao, "%(nameSet)s") {\n'
        record +='    field(DTYP, "Tracy")\n'
        record +='    field(OMSL, "closed_loop")\n'
        record +='    field(DOL, "%(nameCalc)s")\n'
        record +='    field(OUT,  "@%(func)s,%(index)d%(user)s")\n'
        record +='    field(FLNK, "%(nameRB)s")\n'
        record +='    }\n'
        record +='record(ai, "%(nameRB)s") {\n'
        record +='    field(INP, "%(nameSet)s")\n'
        record +='    }\n'
        self.records.append(record % params)

    def ai(self, **kw):
        params = dict(self.defaults)
        params.update(kw)
        record = 'record(ai, "%(nameGet)s") {\n'
        record +='    field(DTYP, "Tracy")\n'
        record +='    field(INP,  "@%(func)s,%(index)d%(user)s")\n'
        record +='    field(SCAN, "Event")\n'
        record +='    field(EVNT, "101")\n'
        record +='    field(FLNK, "%(nameCalc)s")\n'
        record +='    }\n'
        record +='record(calc, "%(nameCalc)s") {\n'
        record +='    field(CALC, "((RNDM*2-1)*0.0005 + 1) * A")\n'
        record +='    field(INPA, "%(nameGet)s")\n'
        record +='    field(FLNK, "%(nameRB)s")\n'
        record +='    }\n'
        record +='record(ai, "%(nameRB)s") {\n'
        record +='    field(INP, "%(nameCalc)s")\n'
        record +='    }\n'

        self.records.append(record % params)

    def pureai(self, **kw):
        params = dict(self.defaults)
        params.update(kw)
        record = 'record(ai, "%(name)s") {\n'
        record +='    field(DTYP, "Tracy")\n'
        record +='    field(INP,  "@%(func)s,%(index)d%(user)s")\n'
        record +='    field(SCAN, "Event")\n'
        record +='    field(EVNT, "101")\n'
        record +='    }\n'

        self.records.append(record % params)

    def pureao(self, **kw):
        params = dict(self.defaults)
        params.update(kw)
        record = 'record(ao, "%(name)s") {\n'
        record +='    field(DTYP, "Tracy")\n'
        record +='    field(OMSL, "closed_loop")\n'
        record +='    field(DOL,  "%(output)f")\n'
        record +='    field(OUT,  "@%(func)s,%(index)d%(user)s")\n'
        record +='    field(SCAN, "Event")\n'
        record +='    field(EVNT, "101")\n'
        record +='    }\n'

        self.records.append(record % params)

    def waveform(self, **kw):
        params = dict(self.defaults)
        params.update(kw)
        record = 'record(waveform, "%(name)s") {\n'
        record +='    field(DTYP, "Tracy")\n'
        record +='    field(INP,  "@%(func)s,%(index)d%(user)s")\n'
        record +='    field(SCAN, "Event")\n'
        record +='    field(EVNT, "101")\n'
        record +='    field(NELM, "%(nelm)d")\n'
        record +='    field(FTVL, "DOUBLE")\n'
        record +='    }\n'

        self.records.append(record % params)

    def current(self, **kw):
        params = dict(self.defaults)
        params.update(kw)

        record = 'record(ai, "%(rec)s") {\n'
        record += '    field(INP,  "%(recCalc)s")\n'
        record += '    field(SCAN, "Passive")\n'
        record += '    }\n'
        record += 'record(calc, "%(recCalc)s") {\n'
        record += '    field(SCAN, "5 second")\n'
        record += '    field(CALC, "A<120?300:A*(1-5/(8*3600.0))")\n'
        record += '    field(INPA, "%(rec)s")\n'
        record += '    field(FLNK, "%(rec)s")\n'
        record += '    }\n'

        self.records.append(record % params)

    def buildDb(self):
        for elem in self.elems:
            if not (elem.startswith('!') or elem.startswith('#')):
                self.index += 1
                attrs = elem.split()
                self.dispatch(attrs)
                self.s = attrs[3]
                self.prevElem = attrs[0]                
                ## print self.index
                if self.elemList.has_key(attrs[0]):
                    self.elemList[attrs[0]].append(self.index)
                else:
                    self.elemList[attrs[0]] = [self.index]
        self.index += 1

        self.rf()
        self.current(rec=self.cur, recCalc = self.curCalc)
        self.globRec()

    def rf(self):        
        self.pureai(name=self.freqRB, func='getRFFreq', \
                    index=self.index)
        self.pureao(name=self.freqSP, func='setRFFreq', \
                    index=self.index, output=499.68059488)
        self.pureai(name=self.voltRB, func='getRFVolt', \
                    index=self.index)
        self.pureao(name=self.voltSP, func='setRFVolt', \
                    index=self.index, output=5.00e6)

        # add records to lattice list
        self.latTable.append(str(self.index) + '\t' \
                        + self.freqRB   + '\t' \
                        + self.freqSP   + '\t' \
                        + 'RFFREQ' + '\t' \
                        + '0.0000' + '\t' \
                        + self.s + '\t' \
                        + 'CAVITY' + '\n')
        self.latTable.append(str(self.index) + '\t' \
                        + self.voltRB   + '\t' \
                        + self.voltSP   + '\t' \
                        + 'RFVOLT' + '\t' \
                        + '0.0000' + '\t' \
                        + self.s + '\t' \
                        + 'CAVITY' + '\n')
              
    def globRec(self):
        # Beam Parameters
        # Tune
        self.pureai(name=self.tuneX, func='getTuneX', index=0)
        self.pureai(name=self.tuneY, func='getTuneY', index=0)

        # Twiss
        self.waveform(name=self.alphaX, func='getAlphaX', \
                      index=0, nelm=self.index)
        self.waveform(name=self.alphaY, func='getAlphaY', \
                      index=0, nelm=self.index)
        self.waveform(name=self.betaX , func='getBetaX',  \
                      index=0, nelm=self.index)
        self.waveform(name=self.betaY , func='getBetaY',  \
                      index=0, nelm=self.index)
        self.waveform(name=self.etaX  , func='getEtaX',   \
                      index=0, nelm=self.index)
        self.waveform(name=self.etaY  , func='getEtaY',   \
                      index=0, nelm=self.index)
        self.waveform(name=self.phiX  , func='getNuX',    \
                      index=0, nelm=self.index)
        self.waveform(name=self.phiY  , func='getNuY',    \
                      index=0, nelm=self.index)

        # Orbit
        self.waveform(name=self.orbitX, func='getOrbitX', \
                      index=0, nelm=self.index)
        self.waveform(name=self.orbitY, func='getOrbitY', \
                      index=0, nelm=self.index)

        # S
        self.waveform(name=self.posS,   func='getSpos', \
                      index=0, nelm=self.index)

    def dispatch(self, attrs):
        actions = (
            ('FTRIM',   self.corr),
            ('TRIMD',   self.corr),
            ('BPM',     self.bpm),
            ('DIPOLE',  self.bend),
            ('QUAD',    self.quad),
            ('SEXT',    self.sext),
            ('SQ_TRIM', self.squad)
            )
        
        for (p, f) in actions:
            if re.match(p, attrs[1]):
                f(attrs)

    def fire(self, recType, **kw):
        actions = (
            ('ao', self.ao),
            ('ai', self.ai),
            ('wf', self.waveform)
            )
        
        for (p, f) in actions:
            if re.match(p, recType):
                f(**kw)
    
    def getGirdCell(self, elemId):
        gird = elemId.find('G', 2)
        girdId = elemId[gird:gird+2]
        girdId = girdId[0:1] + '0' + girdId[1:2]
        cell = elemId.find('C', 2)
        cellId = elemId[cell:cell+3]
        symmetry = elemId[len(elemId)-1:]

        return girdId, cellId, symmetry

    def fillLM(self, attrs, chanRB='NULL', chanSP='NULL', index=0):
        ## indexBlk = 6
        
        ## chSPBlk  = 34
        ## chRBBlk  = 34
        ## nameBlk  = 14
        ## lengBlk  = 8
        ## positBlk = 10

        spRB = '\t'
        spSP = '\t'
        if chanRB == 'NULL':
            spRB = '\t\t\t\t'

        if chanSP == 'NULL':
            spSP = '\t\t\t\t'

        self.latTable.append(str(index) + '\t' \
                        + chanRB   + spRB \
                        + chanSP   + spSP \
                        + attrs[0] + '\t' \
                        + attrs[2] + '\t' \
                        + attrs[3] + '\t' \
                        + attrs[1] + '\n')

    def doInit(self, name, value):
        self.initrec.append('dbpf "%s" %s\n' %(name, value))
    
    def doRecord(self, attrs, devType='', devId='', devInst='', \
                 tfunc='', recType=''):
        girdId, cellId, sym = self.getGirdCell(attrs[0])
        sig = ''

        if self.elemList.has_key(attrs[0]):
            devId += '_P1'

        if devType == 'MG':
            sig = 'Fld'
            chanName = 'SR:%s-%s:%s%s<%s:%s>%s' \
                       %(cellId, devType, girdId, sym, devId, devInst, sig)
            #print chanName
            # this violate the name convention
            # nameSP = chanName + ':SP'
            # correct name rule
            nameSP = chanName + '-SP'
            if attrs[1] == 'QUAD':
                self.doInit(nameSP, attrs[4])
            elif attrs[1] == 'SEXT':
                self.doInit(nameSP, '%.5f' %(float(attrs[5])/2.0))
            ## nameCalc = chanName + ':RNDM'
            ## nameSet = chanName + ':SET'
            ## nameRB = chanName + ':RB'
            nameCalc = chanName + '-RNDM'
            nameSet = chanName + '-SET'
            nameRB = chanName + '-RB'
            self.fire(recType, nameSP=nameSP, nameCalc=nameCalc, nameSet=nameSet, \
                      nameRB=nameRB, func=tfunc, index=self.index)
            self.fillLM(attrs, chanRB=nameRB, chanSP=nameSP, index=self.index)
            
        elif devType == 'BI' and devId == 'BPM':
            sig = 'Pos'
            
            chanName = 'SR:%s-%s:%s%s<%s:%s>%s' \
                       %(cellId, devType, girdId, sym, devId, devInst, sig)
            #print chanName

            #name convention violated
            ## nameGet = chanName + ':XGET'
            ## nameCalc = chanName + ':XRNDM'
            ## nameRB = chanName + ':X'

            nameGet = chanName + '-XGET'
            nameCalc = chanName + '-XRNDM'
            nameRB = chanName + '-X'

            self.fire(recType, nameGet=nameGet, nameCalc=nameCalc, \
                      nameRB=nameRB, func='getBpmX', index=self.index)
            self.fillLM(attrs, chanRB=nameRB, index=self.index)

            ## nameGet = chanName + ':YGET'
            ## nameCalc = chanName + ':YRNDM'
            ## nameRB = chanName + ':Y'
            nameGet = chanName + '-YGET'
            nameCalc = chanName + '-YRNDM'
            nameRB = chanName + '-Y'

            self.fire(recType, nameGet=nameGet, nameCalc=nameCalc, \
                      nameRB=nameRB, func='getBpmY', index=self.index)
            self.fillLM(attrs, chanRB=nameRB, index=self.index)
## print self.index, attrs[0], girdId, cellId, sym
        
    def quad(self, attrs):
        devId = 'QDP'
        devInst = attrs[0][1:3]
        if attrs[0].startswith('SQ'):
            devId = 'SQDP'
            devInst = self.prevElem[1:3]

        self.doRecord(attrs, 'MG', devId, devInst, \
                      tfunc='setQuadrupole', recType='ao')

    
    # Skew Quadrupole include a skew quad and 2 correctors (H, V)
    def squad(self, attrs):
        attrs[1] = 'SQUAD'
        self.quad(attrs)
        
        self.index += 1
        self.corr(attrs)
        
    def sext(self, attrs):
        devId = 'STP'
        devInst = attrs[0][1:3]

        self.doRecord(attrs, 'MG', devId, devInst, \
                      tfunc='setSextupole', recType='ao')
    
    def bpm(self, attrs):
        devId = 'BPM'
        devInst = attrs[0][1:3]

        self.doRecord(attrs, 'BI', devId, devInst, \
                      tfunc='getBpm', recType='ai')
    
    def bend(self, attrs):
        devId = 'DBM'
        devInst = attrs[0][1:3]

        self.doRecord(attrs, 'MG', devId, devInst, \
                      tfunc='setDipole', recType='ao')
        
    # 2 correctors (H, V)
    def corr(self, attrs):
        if attrs[1] == 'FTRIM' or attrs[1] == 'TRIMD':
            self.index += 1
        phyName = attrs[0]
        elemType = attrs[1]
        devId = 'HCM'
        if elemType == 'SQUAD':
            devInst = phyName[2:3]
            attrs[0] = 'CX' + phyName[2:]
        elif elemType == 'FTRIM': 
            devInst = phyName[1:3]
            attrs[0] = 'CFX' + phyName[1:]
        else:
            devInst = attrs[0][1:3]
            attrs[0] = 'CX' + phyName[1:]
        
        attrs[1] = 'TRIMX'

        self.doRecord(attrs, 'MG', devId, devInst, \
                      tfunc='setCorrectorX', recType='ao')
        #print self.index, 'CH', attrs[0]

        self.index += 1
        devId = 'VCM'
        if elemType == 'SQUAD':
            devInst = phyName[2:3]
            attrs[0] = 'CY' + phyName[2:]
        elif elemType == 'FTRIM': 
            devInst = phyName[1:3]
            attrs[0] = 'CFY' + phyName[1:]
        else:
            devInst = phyName[1:3]
            attrs[0] = 'CY' + phyName[1:]
#        devInst = attrs[0][1:3]

        attrs[1] = 'TRIMY'
        self.doRecord(attrs, 'MG', devId, devInst, \
                      tfunc='setCorrectorY', recType='ao')
        #print self.index, 'CV', attrs[0]

if __name__ == '__main__':
    pl = parse_lat(file='CD3-Apr07-10-30cell-par.txt')
    pl.read()
    ## pl.getAllElem()

    tracy = gen_tracy(pl.getAllElem())
    tracy.output('CD3-Apr07-10-30cell-par.lat')

    vdb = gen_vioc_db(pl.getAllElem())
    vdb.buildDb()

    f=open('nsls2.db', 'w')
    for rec in vdb.records:
        f.write_nsls2(rec)
    f.close()

    f1=open('lat_conf_table.txt', 'w')
    for lat in vdb.latTable:
        f1.write_nsls2(lat)

    tuneRec = '0   	%s	NULL                       	TUNE 	0.0000	0.0	TUNE\n' %(vdb.tuneX) 
    f1.write_nsls2(tuneRec)
    tuneRec = '0   	%s	NULL                       	TUNE	0.0000	0.0	TUNE\n' %(vdb.tuneY)
    f1.write_nsls2(tuneRec)

    dcctRec = '0   	%s	NULL                       	DCCT	0.0000	0.0	DCCT\n' %(vdb.cur)
    f1.write_nsls2(dcctRec)
    
    f1.close()

    f2=open('glob_rec.txt', 'w')
    f2.write_nsls2('#rec type         rec name               elem #\n')
    f2.write_nsls2('ai         %s      1\n'   %vdb.tuneX)
    f2.write_nsls2('ai         %s      1\n'   %vdb.tuneY)
    f2.write_nsls2('ai         %s     1\n'   %vdb.cur)
    f2.write_nsls2('waveform   %s     %d\n'   %(vdb.alphaX, vdb.index))
    f2.write_nsls2('waveform   %s     %d\n'   %(vdb.alphaY, vdb.index))
    f2.write_nsls2('waveform   %s      %d\n'  %(vdb.betaX, vdb.index))
    f2.write_nsls2('waveform   %s      %d\n'  %(vdb.betaY, vdb.index))
    f2.write_nsls2('waveform   %s       %d\n' %(vdb.etaX, vdb.index))
    f2.write_nsls2('waveform   %s       %d\n' %(vdb.etaY, vdb.index))
    f2.write_nsls2('waveform   %s       %d\n' %(vdb.phiX, vdb.index))
    f2.write_nsls2('waveform   %s       %d\n' %(vdb.phiY, vdb.index))
    f2.write_nsls2('waveform   %s     %d\n'   %(vdb.orbitX, vdb.index))
    f2.write_nsls2('waveform   %s     %d\n'   %(vdb.orbitY, vdb.index))
    f2.write_nsls2('waveform   %s       %d\n' %(vdb.posS, vdb.index))
    f2.close()

    f3=open('init.cmd', 'w')
    for rec in vdb.initrec:
        f3.write_nsls2(rec)
    f3.close()
    
