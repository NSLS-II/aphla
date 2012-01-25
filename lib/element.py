"""
Element

:author: Lingyun Yang
:date: 2011-05-13 10:28
"""

import os
import copy
from catools import caget, caput


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
    #__slots__ = []
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

    def __repr__(self):
        return "%s:%s @ sb=%f" % (self.name, self.family, self.sb)
            
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

class CaDecorator:
    """
    Decorator between channel access and element.

    PVs are in ascending order
    """
    NoOrder    = 0
    Ascending  = 1
    Descending = 2
    Random     = 3
    def __init__(self):
        self.pvrb = []
        self.pvsp = []
        # buffer the initial value and last setting/reading
        self.rb = [None, None]  # bufferred readback value 
        self.sp = [None, None]  # bufferred setpoint value
        self.field = ''
        self.desc = ''
        self.order = self.Ascending

    def __eq__(self, other):
        return self.pvrb == other.pvrb and \
            self.pvsp == other.pvsp and \
            self.field == other.field and \
            self.desc == other.desc
            
    def _insert_in_order(self, lst, v):
        if len(lst) == 0 or self.order == self.NoOrder:
            lst.append(v)
            return 0

        if self.order == self.Ascending:
            for i,x in enumerate(lst):
                if x < v: continue
                lst.insert(i, v)
                return i
        elif self.order == self.Descending:
            for i,x in enumerate(lst):
                if x > v: continue
                lst.insert(i, v)
                return i

        lst.append(v)
        return len(lst) - 1

    def revert(self):
        """revert the setpoint to the last setting"""
        return caput(self.pvsp, self.sp[-1])
        
    def reset(self):
        """reset the setpoint to the initial setting"""
        return caput(slef.pvsp, self.sp[0])

    def getReadback(self):
        if self.pvrb: 
            self.rb[-1] = caget(self.pvrb)
            if self.rb[0] is None: self.rb[0] = self.rb[-1]
            return self.rb[-1]
        else: return None

    def getSetpoint(self):
        """no history record on reading setpoint"""
        if self.pvsp:
            return caget(self.pvsp)
        else: return None

    def putSetpoint(self, val):
        if self.pvsp:
            ret = caput(self.pvsp, val, wait=True)
            self.sp[-1] = copy.deepcopy(val)
            if self.sp[0] is None: self.sp[0] = self.sp[-1]
            return ret
        else: return None

    def appendReadback(self, pv):
        self.pvrb.append(pv)

    def appendSetpoint(self, pv):
        self.pvsp.append(pv)

    def insertReadback(self, pv):
        self._insert_in_order(self.pvrb, pv)

    def insertSetpoint(self, pv):
        #self.pvsp.append(pv)
        self._insert_in_order(self.pvsp, pv)

    def removeReadback(self, pv):
        self.pvrb.remove(pv)

    def removeSetpoint(self, pv):
        self.pvsp.remove(pv)
        
class Element(AbstractElement):
    """
    Element with Channel Access ability
    """
    __slots__ = []
    def __init__(self, **kwargs):
        """
        - *pvs* a list of tuple: (func,pv,description) for related status
        - *eget* the default get action (func, pv)
        - *eput* the default put action (func, pv)

        An element is homogeneous means, it use same get/put function on a
        list of variables to speed up.
        """
        #AbstractElement.__init__(self, **kwargs)
        self.__dict__['_field'] = {'value': None, 'status': None}
        self.__dict__['_pvtags'] = {}
        self.__dict__['virtual'] = kwargs.get('virtual', 0)
        super(Element, self).__init__(**kwargs)
        
    def __setstate__(self, data):
        for (name, value) in data.iteritems():
            if name in ['_field', '_pvtags']:
                self.__dict__[name] = value
            else:
                super(Element, self).__setattr__(name, value)
            
    def _pv_1(self, **kwargs):
        """One input"""
        ret = None
        if kwargs.get('tag', None):
            ret = self._pv_tags([kwargs['tag']])
        elif kwargs.get('tags', None):
            ret = self._pv_tags(kwargs['tags'])
        elif kwargs.get('field', None):
            att = kwargs['field']
            if self._field.has_key(att):
                decr = self._field[att]
                ret = [v for v in set(decr.pvsp + decr.pvrb)]
            else:
                ret = []
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
            ret = self._pvtags.keys()
            #for k,v in self._pvtags.iteritems():
            #    #print k, v
            #    #if not v: continue
            #    if isinstance(v, (str, unicode)): ret.append(v)
            #    else: ret.extend(v)
            #ret = [v for v in set(ret)]
        elif len(kwargs) == 1:
            ret = self._pv_1(**kwargs)
        elif len(kwargs) == 2:
            handle = kwargs.get('handle', None)
            try:
                if handle == 'readback':
                    return self._field[kwargs['field']].pvrb
                elif handle == 'setpoint':
                    return self._field[kwargs['field']].pvsp
                else:
                    raise ValueError("invalid handle value: %s" % handle)
            except KeyError:
                return []
        else: return []

        # sorted
        return sorted(ret)

    def hasPv(self, pv):
        return self._pvtags.has_key(pv)
        
    def appendStatusPv(self, pv, desc, order=True):
        """
        append (func, pv, description) to status
        """
        decr = self._field['status']
        if not decr: self._field['status'] = CaDecorator()
        
        self._field['status'].insertReadback(pv)

    def addEGet(self, pv, field=None):
        """
        add *pv* for `eget` action
        
        If no field provided, assign only to the default "value" field
        """
        sflists = ['value']
        if field: sflists.append(field)

        for sf in sflists:
            if not sf in self._field.keys() or not self._field[sf]:
                self._field[sf] = CaDecorator()
            # add pv
            self._field[sf].insertReadback(pv)

    def addEPut(self, pv, field=None):
        """
        add *pv* for `eset` action

        If no field provided, assign to the default "value" field
        """
        sflists = ['value']
        if field: sflists.append(field)

        for sf in sflists:
            if not sf in self._field.keys() or not self._field[sf]:
                self._field[sf] = CaDecorator()
            # add pv
            self._field[sf].insertSetpoint(pv)
        
    def status(self):
        maxlen = max([len(att) for att in self._field.keys()])
        head = '%d%%s ' % maxlen
        ret = ''
        for att in self._field.keys():
            decr = self._field[att]
            if not decr: continue
            val = decr.getReadback()
            ret = ret + head % att + ' '.join([str(v) for v in val]) + '\n'
        return ret

    def __getattr__(self, att):
        # called after checking __dict__
        if not self._field.has_key(att):
            raise AttributeError("element %s has no attribute(field) %s" % 
                                 (self.name, att))
        else:
            decr = self._field[att]
            if not decr:
                raise AttributeError("field %s of %s is not defined" \
                                         % (att, self.name))
            elif decr.getReadback():
                x = decr.rb
            elif decr.getSetpoint():
                x = decr.sp
            else:
                raise AttributeError("error reading field %s" % att)

        if len(x) == 1: return x[0]
        else: return x

    def __setattr__(self, att, val):
        # this could be called by AbstractElement.__init__ or Element.__init__
        if hasattr(super(Element, self), att):
            super(Element, self).__setattr__(att, val)
        elif self.__dict__['_field'].has_key(att):
            decr = self.__dict__['_field'][att]
            if not decr:
                raise AttributeError("field %s is not defined" % att)
            if not decr.pvsp:
                raise ValueError("field %s is not writable" % att)
            decr.putSetpoint(val)
        elif att in self.__dict__.keys():
            self.__dict__[att] = val
        else:
            # new attribute for superclass
            super(Element, self).__setattr__(att, val)
            #raise AttributeError("Error")

    def setFieldGetAction(self, field, v, desc = ''):
        """
        set the action when reading *field*.

        the previous action will be replaced if it was defined.
        """
        if not self._field.has_key(field):
            self._field[field] = CaDecorator()

        self._field[field].insertReadback(v)

    def setFieldPutAction(self, field, v, desc = ''):
        """
        set the action for writing *field*.

        the previous action will be replaced if it was define.
        """
        if not self._field.has_key(field):
            self._field[field] = CaDecorator()

        self._field[field].insertSetpoint(v)

    def fields(self):
        """
        return element's fields
        """
        return self._field.keys()

    def updateCfsProperties(self, pv, prpt):
        """
        update the element with a property dictionary
        """
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

    def collect(self, elemlist, **kwargs):
        """
        collect properties in elemlist as its own.
        
        - *fields*, EPICS related
        - *attrs*, element attribute list
        """

        fields = kwargs.get("fields", [])
        attrs  = kwargs.get("attrs", [])
        for field in fields:
            pd = CaDecorator()
            for elem in elemlist:
                pd.pvrb += elem._field[field].pvrb
                pd.pvsp += elem._field[field].pvsp
            self._field[field] = pd
            #print "Setting %s" % field
        for att in attrs:
            vl = []
            for elem in elemlist:
                vl.append(getattr(elem, att))
            setattr(self, att, vl)
        

    def __dir__(self):
        return dir(Element) + list(self.__dict__) + self._field.keys()


