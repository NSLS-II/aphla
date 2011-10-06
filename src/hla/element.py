"""
Element

:author: Lingyun Yang
:date: 2011-05-13 10:28
"""

import os

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

        HLA_DEBUG is used for enabling debug.
        """
        AbstractElement.__init__(self, **kwargs)
        self._eget = kwargs.get('eget', None)
        self._eput = kwargs.get('eput', None)
        self._field = {'value': {'eget':[], 'eput':[], 'desc':[]},
                       'status': {'eget':[], 'desc': []}}
        self._pvtags = {}
        self.virtual = 0
        self.debug = 0
        
    def eget(self):
        return self._eget

    def eput(self):
        return self._eput

    def _pv_1(self, **kwargs):
        """One input"""
        ret = None
        if kwargs.get('tag', None):
            ret = self._pv_tags([kwargs['tag']])
        elif kwargs.get('tags', None):
            ret = self._pv_tags(kwargs['tags'])
        elif kwargs.get('field', None):
            ret = self._pv_fields([kwargs['field']])

        return ret

    def _pv_tags(self, tags):
        """
        return pv based on a list of tags
        """
        tagset = set(tags)
        return [pv for pv,ts in self._pvtags.iteritems()
                   if tagset.issubset(ts)]

    def _pv_fields(self, fields):
        """
        return pvs based on a list of fields
        """
        fieldset = set(fields)
        ret = []
        for k,v in self._field.iteritems():
            print k, v
            if k in fieldset:
                ret.extend(v['eget'])
                ret.extend(v['eput'])
        return ret
            
    def pv(self, **kwargs):
        """
        search for pv

        Example::

          >>> pv() # returns all pvs.
          >>> pv(tag='aphla.X')
          >>> pv(tags=['aphla.EGET', 'aphla.Y'])
          >>> pv(field = "x")
          >>> pv(field="x", handle='readback')
        """
        if len(kwargs) == 0:
            ret = []
            for k,v in self._field.iteritems():
                #print k, v
                for k2 in ['eget', 'eput']:
                    v2 = v.get(k2, [])
                    if not v2: continue
                    if isinstance(v2, (str, unicode)): ret.append(v2)
                    else: ret.extend(v2)
            ret = [v for v in set(ret)]
        elif len(kwargs) == 1:
            ret = self._pv_1(**kwargs)
        elif len(kwargs) == 2:
            try:
                if kwargs['handle'] == 'readback':
                    return self._field[kwargs['field']]['eget']
                elif kwargs['handle'] == 'setpoint':
                    return self._field[kwargs['field']]['eput']
            except KeyError:
                return []
        else: return []

        if not ret: return None
        elif len(ret) == 1: return ret[0]
        else: return sorted(ret)

    def _insert_in_order(self, lst, v):
        if len(lst) == 0:
            lst.append(v)
            return 0

        for i,x in enumerate(lst):
            if x < v: continue
            lst.insert(i, v)
            return i

        lst.append(v)
        return len(lst) - 1

    def hasPv(self, pv):
        return self._pvtags.has_key(pv)
        
    def appendStatusPv(self, pv, desc, order=True):
        """
        append (func, pv, description) to status
        """
        if order:
            i = self._insert_in_order(self._field['status']['eget'], pv)
            self._field['status']['desc'].insert(i, desc)
        else:
            self._field['status']['eget'].append(pv)
            self._field['status']['eget'].append(desc)

    def addEGet(self, pv):
        """
        add *pv* for `eget` action
        """
        vf = self._field['value']
        if pv in vf['eget']: return
        else:
            self._insert_in_order(vf['eget'], pv)
        
    def addEPut(self, pv):
        """
        add *pv* for `eset` action
        """
        vf = self._field['value']
        if pv in vf['eput']: return
        else:
            self._insert_in_order(vf['eput'], pv)
        
    def __getattr__(self, att):
        if not self._field.has_key(att):
            raise AttributeError("element %s has no attribute(field) %s" % 
                                 (self.name, att))
        elif att == 'status':
            pv, desc = self._field[att]['eget'], self._field[att]['desc']
            ret = self.name
            if pv and desc:
               val = self._eget(pv)
               for i,v in enumerate(pv):
                   ret = ret + '\n  %s (%s) %f' % (desc[i], pv[i], val[i])
            return ret
        else:
            x = self._field[att]['eget']
            if not x:
                x = self._field[att]['eput']
            if not x:
                raise AttributeError("element %s has no read/write for field %s" %
                                     (self.name, att))
        #print "reading ", att
        ret = self._eget(x)
        if len(x) == 1: return ret[0]
        else: return ret

    def __setattr__(self, att, val):
        if not self.__dict__.has_key('_field'):
            # too early
            self.__dict__[att] = val
        elif att in self.__dict__['_field'].keys():
            act = self.__dict__['_field'][att]['eput']
            if act:
                self._eput(act, val)
            else: raise AttributeError("no writable channel associated with property '%s'" % att)
        else:
            # new property
            self.__dict__[att] = val

    def setFieldGetAction(self, field, v, desc):
        """
        set the action when reading *field*
        """
        if not self._field.has_key(field):
            self._field[field] = {'eget': [v], 'eput': None, 'desc': desc}
        else:
            self._field[field]['eget'] = [v]
            self._field[field]['desc'] = desc

    def setFieldPutAction(self, field, v, desc):
        """
        set the action for writing *field*
        """
        if not self._field.has_key(field):
            self._field[field] = {'eget': None, 'eput': [v], 'desc': desc}
        else:
            self._field[field]['eput'] = [v]
            self._field[field]['desc'] = desc

    def fields(self):
        """
        return element's fields
        """
        return self._field.keys()

    def updateCfsProperties(self, pv, prpt):
        AbstractElement.updateCfsProperties(self, prpt)
        
    def updateCfsTags(self, pv, tags):
        """
        update a list of tags
        """
        AbstractElement.updateCfsTags(self, tags)
        if not pv in self._pvtags.keys():
            self._pvtags[pv] = set([])
        self._pvtags[pv].update(tags)

    def updateCfsRecord(self, pv, prpt, tags):
        AbstractElement.updateCfsProperties(self, prpt)
        AbstractElement.updateCfsTags(self, tags)

        if not pv in self._pvtags.keys(): self._pvtags[pv] = set([])
        self._pvtags[pv].update(tags)


