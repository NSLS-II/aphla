"""
Element

:author: Lingyun Yang
:date: 2011-05-13 10:28
"""

class AbstractElement(object):
    """
    AbstractElement

    AbstractElement has no Channel Access abilities.
    
    ==========  ===================================================
    Variable    Meaning
    ==========  ===================================================
    *name*      element name
    *index*     index
    *devname*   device name
    *phylen*    physical(yoke) length
    *family*    family
    *s*         s position
    *length*    effective(magnetic) length 
    *cell*      cell name
    *girder*    girder name
    *symmetry*  symmetry type
    *sequence*  sequence tuple
    ==========  ===================================================
    """

    # format string for __str__
    STR_FORMAT = "%d %s %s %.3f %.3f %s %s %s %s %s"
    CFS = {'name': u'ELEM_NAME',
           'devname': u'DEV_NAME',
           'family': u'ELEM_TYPE',
           'girder': u'GIRDER',
           'handle': u'HANDLE',
           'length': u'LENGTH',
           'index': u'ORDINAL',
           'symmetry': u'SYMMETRY',
           's': u'S_POSITION',
           'cell': u'CELL',
           'phylen': None,
           'sequence': None}
    
    def __init__(self, **kwargs):
        """
        create an element from Channel Finder Service data or explicit
        parameters.
        """
        if kwargs.has_key('cfs'):
            #print "Using CFS data", kwargs['cfs']
            d = kwargs['cfs']
            self.name     = d.get(self.CFS['name'], None)
            self.devname  = d.get(self.CFS['devname'], None)
            self.phylen   = float(d.get(self.CFS['phylen'], 0.0))
            self.index    = int(d.get(self.CFS['index'], -1))
            self.family   = d.get(self.CFS['family'], None)
            self.s        = float(d.get(self.CFS['s'], 0.0))
            self.length   = float(d.get(self.CFS['length'], 0.0))
            self.cell     = d.get(self.CFS['cell'], None)
            self.girder   = d.get(self.CFS['girder'], None)
            self.symmetry = d.get(self.CFS['symmetry'], None)
            self.sequence = d.get(self.CFS['sequence'], (0, 0))
        else:
            self.name     = kwargs.get('name', None)
            self.devname  = kwargs.get('devname', None)
            self.phylen   = kwargs.get('phylen', 0.0)
            self.index    = kwargs.get('index', -1)
            self.family   = kwargs.get('family', None)
            self.s        = kwargs.get('s', 0.0)
            self.length   = kwargs.get('length', 0.0)
            self.cell     = kwargs.get('cell', None)
            self.girder   = kwargs.get('girder', None)
            self.symmetry = kwargs.get('symmetry', None)
            self.sequence = kwargs.get('sequence', (0, 0))

        self.group = [self.family, self.cell, self.girder, self.symmetry]
        
    def profile(self, vscale=1.0):
        """
        the profile for drawing the lattice, return as x, y, c

        - *x* x coordinate
        - *y* y coordinate
        - *c* color
        
        - 'QUAD', quadrupole
        - 'DIPOLE', dipole
        - 'SEXT', sextupole
        - ['TRIMX' | 'TRIMY'], corrector
        - ['BPMX' | 'BPMY'], beam position monitor
        """
        b, e = self.s, self.s + self.length
        h = vscale
        if self.family == 'QUAD':
            return [b, b, e, e], [0, h, h, 0], 'k'
        elif self.family == 'DIPOLE':
            return [b, b, e, e, b, b, e, e], [0, h, h, -h, -h, h, h, 0], 'k'
        elif self.family == 'SEXT':
            return [b, b, e, e], [0, 1.25*h, 1.25*h, 0], 'k'
        elif self.family in ['TRIMX', 'TRIMY']:
            return [b, (b+e)/2.0, (b+e)/2.0, (b+e)/2.0, e], \
                [0, 0, h, 0, 0], 'r'
        elif self.family in ['BPMX', 'BPMY']:
            return [b, (b+e)/2.0, (b+e)/2.0, (b+e)/2.0, e], \
                [0, 0, h, 0, 0], 'b'        
        else:
            return [b, e], [0, 0], 'k'

    def __str__(self):
        return Element.STR_FORMAT % (
            self.index, self.name, self.family, self.s, self.length,
            self.devname, self.cell, self.girder, self.symmetry, self.sequence)

    def __lt__(self, other):
        return self.s < other.s

    def __gt__(self, other):
        return self.s > other.s

    def __eq__(self, other):
        return self.s == other.s and \
               self.length == other.length and \
               self.name == other.name

    def updateCfsProperties(self, prpt):
        """
        """
        if prpt.has_key(self.CFS['family']):
            # rename the family name, append to group. The family name is kept
            # unique, but "pushed" old family name to group name
            newfam = prpt[self.CFS['family']]
            if not newfam in self.group: self.group.append(newfam)
            self.family = newfam
            
        if prpt.has_key(self.CFS['devname']):
            self.devname = prpt[self.CFS['devname']]
        if prpt.has_key(self.CFS['cell']):
            self.cell = prpt[self.CFS['cell']]
        if prpt.has_key(self.CFS['girder']):
            self.girder = prpt[self.CFS['girder']]
        if prpt.has_key(self.CFS['symmetry']):
            self.symmetry = prpt[self.CFS['symmetry']]
            
        if prpt.has_key(self.CFS['phylen']):
            self.phylen = float(prpt[self.CFS['phylen']])
        if prpt.has_key(self.CFS['length']):
            self.length = float(prpt[self.CFS['length']])
        if prpt.has_key(self.CFS['s']):
            self.s = float(prpt[self.CFS['s']])
        if prpt.has_key(self.CFS['index']):
            self.index = int(prpt[self.CFS['index']])

    def updateCfsTags(self, tags):
        pass

class Element(AbstractElement):
    """
    Element with Channel Access ability
    """

    def __init__(self, **kwargs):
        """
        - *pvs* a list of tuple: (func,pv,description) for related status
        - *eget* the default get action (func, pv)
        - *eput* the default put action (func, pv)

        An element is homogeneous means, it use same get/put function on a
        list of variables to speed up.
        """
        AbstractElement.__init__(self, **kwargs)
        self._status   = kwargs.get('pvs', [])
        self._eget_val = kwargs.get('eget', [])
        self._eput_val = kwargs.get('eput', [])
        self.homogeneous = True
        
    def hasPv(self, pv):
        for p in self._status:
            if p[1] == pv: return True
        for p in self._eget_val:
            if p[1] == pv: return True
        for p in self._eput_val:
            if p[1] == pv: return True
        else: return False
        
    def appendStatusPv(self, pvact):
        """
        append (func, pv, description) to status
        """
        self._status.append(pvact)

    def appendEget(self, eget):
        self._eget_val.append(eget)
        
    def updateEget(self, eget):
        self._eget_val = eget

    def appendEput(self, eput):
        self._eput_val.append(eput)
        
    def updateEput(self, eput):
        self._eput_val = eput
        
    @property
    def value(self):
        if not self._eget_val: return None
        if not self.homogeneous:
            ret = []
            for f, x, desc in self._eget_val:
                if f and x: ret.append(f(x))
            if len(ret) == 1: return ret[0]
            else: return ret
        else:
            #
            pvs = [x for f,x,desc in self._eget_val]
            ret = self._eget_val[0][0](pvs)
            if len(ret) == 1: return ret[0]
            else: return ret

    @value.setter
    def value(self, v):
        if not self._eput_val: return None
        if not self.homogeneous:
            ret = []
            for f, x, desc in self._eput_val:
                if f and x: ret.append(f(x, v))
            return ret
        else:
            # speed up using pv list when calling caget/caput
            pvs = [x for f,x,desc in self._eget_val]
            return self._eget_val[0][0](pvs)
        
    @property
    def status(self):
        ret = self.name + '\n'
        if self.homogeneous:
            pvs = [x for f, x, desc in self._eget_val]
            descs = [desc for f, x, desc in self._eget_val]
            for f,x,desc in self._status:
                pvs.append(x)
                descs.append(desc)
            if self._eget_val: f = self._eget_val[0][0]
            elif self._status: f = self._status[0][0]
            else: f = None
            val = f(pvs)
            for i in range(len(pvs)):
                ret += "  %s (%s): %s\n" % (descs[i], pvs[i], val[i])
        else:
            for f, x, desc in self._eget_val:
                ret += "  %s (%s): %s\n" % (desc, x, f(x))
            for f, x, desc in self._status:
                ret += "  %s (%s): %s\n" % (desc, x, f(x))
        return ret

    def updateCfsProperties(self, pv, prpt):
        AbstractElement.updateCfsProperties(self, prpt)
    
    def updateCfsTags(self, pv, tags):
        AbstractElement.updateCfsTags(self, tags)
        
