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
    
    def __init__(self, **kwargs):
        """
        create an element from Channel Finder Service data or explicit
        parameters.
        """
        #print kwargs
        self.name     = kwargs.get('name', None)
        self.devname  = kwargs.get('devname', None)
        self.phylen   = float(kwargs.get('phylen', '0.0'))
        self.index    = int(kwargs.get('index', '-1'))
        self.family   = kwargs.get('family', None)
        self.se       = float(kwargs.get('se', '0.0'))
        self.sb       = float(kwargs.get('sb', 0.0))
        self.length   = float(kwargs.get('length', 0.0))
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
        b, e = self.sb, self.sb + self.length
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
            self.index, self.name, self.family, self.sb, self.length,
            self.devname, self.cell, self.girder, self.symmetry, self.sequence)

    def __lt__(self, other):
        return self.sb < other.sb

    def __gt__(self, other):
        return self.sb > other.sb

    def __eq__(self, other):
        return self.sb == other.sb and \
               self.length == other.length and \
               self.name == other.name

    def updateCfsProperties(self, prpt):
        """
        - *devname* Device name
        - *cell* Cell
        - *girder* Girder
        - *symmetry* Symmetry
        - *phylen* Physical length
        - *length* Effective/magnetic length
        - *s*  s-loc (not specified for entrance/midpoint/exit)
        - *index* index in lattice
        """
        if prpt.has_key('family'):
            # rename the family name, append to group. The family name is kept
            # unique, but "pushed" old family name to group name
            newfam = prpt['family']
            if not newfam in self.group: self.group.append(newfam)
            self.family = newfam
            
        if prpt.has_key('devname'):
            self.devname = prpt['devname']
        if prpt.has_key('cell'):
            self.cell = prpt['cell']
        if prpt.has_key('girder'):
            self.girder = prpt['girder']
        if prpt.has_key('symmetry'):
            self.symmetry = prpt['symmetry']
            
        if prpt.has_key('phylen'):
            self.phylen = float(prpt['phylen'])
        if prpt.has_key('length'):
            self.length = float(prpt['length'])
        if prpt.has_key('se'):
            self.se = float(prpt['se'])
        if prpt.has_key('sb'):
            self.sb = float(prpt['sb'])
        if prpt.has_key('index'):
            self.index = int(prpt['index'])

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
        ret = self.name
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
                ret += "\n  %s (%s): %s" % (descs[i], pvs[i], val[i])
        else:
            for f, x, desc in self._eget_val:
                ret += "\n  %s (%s): %s" % (desc, x, f(x))
            for f, x, desc in self._status:
                ret += "\n  %s (%s): %s" % (desc, x, f(x))
        return ret

    def updateCfsProperties(self, pv, prpt):
        AbstractElement.updateCfsProperties(self, prpt)
    
    def updateCfsTags(self, pv, tags):
        AbstractElement.updateCfsTags(self, tags)
        
