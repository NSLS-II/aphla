"""
Element
~~~~~~~~

:author: Lingyun Yang
:date: 2011-05-13 10:28
"""

import os
import re
import copy
import logging
from catools import caget, caput

logger = logging.getLogger(__name__)

class AbstractElement(object):
    """
    The :class:`AbstractElement` contains most of the lattice properties, such
    as element name, length, location and family. It also keeps a list of
    groups which belongs to. The default group list contains cell, girder,
    family and symmetry information if they are valid.

    AbstractElement has no Channel Access abilities. The AbstractElement can
    be created with the following optional parameters
    
    ==========  ===================================================
    Variable    Meaning
    ==========  ===================================================
    *name*      element name
    *index*     index
    *devname*   device name
    *phylen*    physical(yoke) length
    *family*    family
    *sb*        s position of the entrance
    *se*        s position of the exit
    *length*    effective(magnetic) length 
    *cell*      cell name
    *girder*    girder name
    *symmetry*  symmetry type
    *sequence*  sequence tuple
    *group*     list of groups the element belongs to
    ==========  ===================================================

    
    """

    # format string for __str__
    _STR_FORMAT = "%d %s %s %.3f %.3f %s %s %s %s %s"
    #__slots__ = []
    def __init__(self, **kwargs):
        """
        create an element from Channel Finder Service data or explicit
        parameters.

        :param name: element name
        :type name: ele name
        """
        #print kwargs
        self.name     = kwargs.get('name', None)
        self.devname  = kwargs.get('devname', None)
        self.phylen   = float(kwargs.get('phylen', '0.0'))
        self.index    = int(kwargs.get('index', '-1'))
        self.family   = kwargs.get('family', None)
        self.se       = float(kwargs.get('se', '0.0'))
        self.sb       = float(kwargs.get('sb', '0.0'))
        self.length   = float(kwargs.get('length', '0.0'))
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
        
        It recognize the following *family*:

        - 'QUAD', quadrupole
        - 'DIPOLE', dipole
        - 'SEXT', sextupole
        - ['TRIMX' | 'TRIMY'], corrector
        - ['BPMX' | 'BPMY'], beam position monitor

        For unrecognized element, it returns a straight line, i.e. `([s0, s1],
        [0, 0], 'k')`
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
        return AbstractElement._STR_FORMAT % (
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

    def updateProperties(self, prpt):
        """
        Update the properties of this element, the input *prpt* is a
        dictionary with the following keys:

        - *devname* Device name
        - *cell* Cell
        - *girder* Girder
        - *symmetry* Symmetry
        - *phylen* Physical length
        - *length* Effective/magnetic length
        - *sb* s-loc of the entrance (effective length)
        - *se* s-loc of the exit (effective length)
        - *index* index in lattice

        This update will not synchronize element properties, e.g. calculate
        length from sb and se, or se from sb and length.
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


class CaDecorator:
    """
    Decorator between channel access and element field.

    The field can be one single PV or a list of PVs. Each PV has its own
    stepsize and value range.

    If *trace* is True, every readback/setpoint will be recorded for later
    reset/revert whenever the get/put functions are called. Extra history
    point can be recorded by calling *mark*.
    """
    NoOrder    = 0
    Ascending  = 1
    Descending = 2
    Random     = 3
    def __init__(self, **kwargs):
        self.pvrb = []
        self.pvsp = []
        self.pvh  = [] # step size
        self.pvlim = [] # lower/upper limit 
        # buffer the initial value and last setting/reading
        self.rb = []  # bufferred readback value 
        self.sp = []  # bufferred setpoint value
        self.field = ''
        self.desc = kwargs.get('desc', None)
        self.order = self.Ascending
        self.trace = kwargs.get('trace', False)
        self.trace_limit = 200

    def __eq__(self, other):
        return self.pvrb == other.pvrb and \
            self.pvsp == other.pvsp and \
            self.field == other.field and \
            self.desc == other.desc
            
    def _insert_in_order(self, lst, v):
        if len(lst) == 0 or self.order == self.NoOrder:
            if isinstance(v, (tuple, list)): lst.extend(v)
            else: lst.append(v)
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
        """
        revert the setpoint to the last setting

        TODO: check if the current setpoint is same as the last record,
        i.e. changed by outsider ?
        """
        if not self.sp: return
        # v0 = caget(self.pvsp)
        self.sp.pop()
        caput(self.pvsp, self.sp[-1])
        
    def reset(self):
        """
        reset the setpoint to the initial setting
        """
        if not self.sp: return
        caput(slef.pvsp, self.sp[0])
        self.sp = []

    def mark(self, data = 'setpoint'):
        """
        mark the current value in trace for revert
        - `setpoint` save setpoint value (default)
        - `readback` save readback value
        - `rb2setpoint` save readback value to setpoint

        The default is mark the current setpoint and an imediate revert will
        restore this setpoint.
        """
        if data == 'readback':
            self.rb.append(caget(self.pvrb))
            if len(self.rb) > self.trace_limit: self.rb.pop(0)
        elif data == 'setpoint':
            self.sp.append(caget(self.pvsp))
            if len(self.sp) > self.trace_limit: self.sp.pop(0)
        elif data == 'rb2setpoint':
            self.sp.append(caget(self.pvrb))
            if len(self.sp) > self.trace_limit: self.sp.pop(0)

    def getReadback(self):
        if self.pvrb: 
            ret = caget(self.pvrb)
            if self.trace: 
                self.rb.append(copy.deepcopy(ret))
                if len(self.rb) > self.trace_limit: self.rb.pop(0)
            #print self.pvrb, ret
            if len(self.pvrb) == 1: 
                return ret[0]
            else: return ret
        else: return None

    def getSetpoint(self):
        """no history record on reading setpoint"""
        if self.pvsp:
            ret = caget(self.pvsp)
            if len(self.pvsp) == 1: return ret[0]
            else: return ret
        else: return None

    def putSetpoint(self, val):
        if self.pvsp:
            ret = caput(self.pvsp, val, wait=True)
            if self.trace: 
                if isinstance(val, (list, tuple)):
                    self.sp.append(val[:])
                elif isinstance(val, (float, int)):
                    self.sp.append(val)
                else:
                    raise RuntimeError("unsupported datatype '%s' "
                                       "for tracing object value." %
                                       type(val))
                if len(self.sp) > self.trace_limit: self.sp.pop(0)
            return ret
        else: return None

    def setReadbackPv(self, pv, idx = None):
        """
        set the PV for readback at position idx. if idx is None, replace the
        original one. if idx is an index integer and pv is not a list, then
        replace the one with this index.
        """
        if idx is None:
            if isinstance(pv, (str, unicode)):
                self.pvrb = [pv]
            elif isinstance(pv, (tuple, list)):
                self.pvrb = [p for p in pv]
        elif not isinstance(pv, (tuple, list)):
            while idx >= len(self.pvrb): self.pvrb.append(None)
            self.pvrb[idx] = pv
        else:
            raise RuntimeError("invalid readback pv '%s' for position '%s'" % 
                               (str(pv), str(idx)))

    def setSetpointPv(self, pv, idx = None):
        """
        set the PV for setpoint at position idx. if idx is None, replace the
        original one. if idx is an index integer and pv is not a list, then
        replace the one with this index.
        """
        if idx is None:
            if isinstance(pv, (str, unicode)):
                self.pvsp = [pv]
            elif isinstance(pv, (tuple, list)):
                self.pvsp = [p for p in pv]
        elif not isinstance(pv, (tuple, list)):
            while idx >= len(self.pvsp): self.pvsp.append(None)
            self.pvsp[idx] = pv
        else:
            raise RuntimeError("invalid setpoint pv '%s' for position '%s'" % 
                               (str(pv), str(idx)))
    def appendReadback(self, pv):
        self.pvrb.append(pv)

    def appendSetpoint(self, pv):
        self.pvsp.append(pv)

    def removeReadback(self, pv):
        self.pvrb.remove(pv)

    def removeSetpoint(self, pv):
        self.pvsp.remove(pv)
        
    def stepUp(self, n = 1):
        """
        step up the setpoint value.
        """
        raise NotImplementedError("waiting for data")

    def stepDown(self, n = 1):
        """
        step down the setpoint value.
        """
        raise NotImplementedError("waiting for data")

    def settable(self):
        """check if it can be set"""
        if not self.pvsp: return False
        else: return True

class CaElement(AbstractElement):
    """
    Element with Channel Access ability
    """
    __slots__ = []
    def __init__(self, **kwargs):
        """
        An element is homogeneous means, it use same get/put function on a
        list of variables to speed up.        
        """
        #AbstractElement.__init__(self, **kwargs)
        self.__dict__['_field'] = {}
        self.__dict__['_pvtags'] = {}
        self.__dict__['virtual'] = kwargs.get('virtual', 0)
        self.__dict__['trace'] = kwargs.get('trace', False)
        # update all element properties
        super(CaElement, self).__init__(**kwargs)
        
    def __setstate__(self, data):
        for (name, value) in data.iteritems():
            if name in ['_field', '_pvtags']:
                self.__dict__[name] = value
            else:
                super(CaElement, self).__setattr__(name, value)
            
    def _pv_1(self, **kwargs):
        """
        One input
        
        - tag: 
        - tags: all tags are met
        - field: return pvrb + pvsp
        """
        ret = None
        if kwargs.get('tag', None):
            return self._pv_tags([kwargs['tag']])
        elif kwargs.get('tags', None):
            return self._pv_tags(kwargs['tags'])
        elif kwargs.get('field', None):
            att = kwargs['field']
            if self._field.has_key(att):
                decr = self._field[att]
                return decr.pvrb + decr.pvsp
            else:
                return []
        return []

    def _pv_tags(self, tags):
        """
        return pv list which has all the *tags*.
        """
        tagset = set(tags)
        return [pv for pv,ts in self._pvtags.iteritems()
                   if tagset.issubset(ts)]

    def _pv_fields(self, fields):
        """
        return pv list which has all fields in the input
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
        search for pv with specified *tag*, *tags*, *field*, *handle* or a
        combinatinon of *field* and *handle*.

        Example::

          >>> pv() # returns all pvs.
          >>> pv(tag='aphla.X')
          >>> pv(tags=['aphla.EGET', 'aphla.Y'])
          >>> pv(field = "x")
          >>> pv(field="x", handle='readback')
        """
        if len(kwargs) == 0:
            return self._pvtags.keys()
        elif len(kwargs) == 1:
            return self._pv_1(**kwargs)
        elif len(kwargs) == 2:
            handle = kwargs.get('handle', None)
            fd = kwargs.get('field', None)
            if fd not in self._field: return []
            if handle.lower() == 'readback':
                return self._field[kwargs['field']].pvrb
            elif handle.lower() == 'setpoint':
                return self._field[kwargs['field']].pvsp
            else:
                return []
        else: return []

    def hasPv(self, pv):
        return self._pvtags.has_key(pv)
        
    def appendStatusPv(self, pv, desc, order=True):
        """
        append (func, pv, description) to status
        """
        decr = self._field['status']
        if not decr: self._field['status'] = CaDecorator(trace=self.trace)
        
        self._field['status'].appendReadback(pv)

    def addEGet(self, pv, field=None):
        """
        add *pv* for `eget` action
        
        If no field provided, assign only to the default "value" field
        """
        raise DeprecationWarning("This is deprecated, use updatePvRecord")

        sflists = ['value']
        if field: sflists.append(field)

        for sf in sflists:
            if not sf in self._field.keys() or not self._field[sf]:
                self._field[sf] = CaDecorator(trace=self.trace)
            # add pv
            self._field[sf].appendReadback(pv)

    def addEPut(self, pv, field=None):
        """
        add *pv* for `eset` action

        If no field provided, assign to the default "value" field.
        """
        raise DeprecationWarning("This is deprecated, use updatePvRecord")

        sflists = ['value']
        if field is not None: sflists.append(field)

        # for the given PV, create CaDecorator for each field.
        for sf in sflists:
            if sf not in self._field.keys() or not self._field[sf]:
                self._field[sf] = CaDecorator(trace=self.trace)
            # add setpoint pv
            self._field[sf].insertSetpoint(pv)
        
    def status(self):
        ret = self.name
        if not self._field.keys(): return ret

        maxlen = max([len(att) for att in self._field.keys()])
        head = '\n%%%ds: ' % (maxlen+2)
        for att in self._field.keys():
            decr = self._field[att]
            if not decr: continue
            val = decr.getReadback()
            ret = ret + head % att + str(val)
        return ret

    def __getattr__(self, att):
        # called after checking __dict__
        if not self._field.has_key(att):
            raise AttributeError("element '%s' has no field '%s'" % 
                                 (self.name, att))
        else:
            decr = self._field.get(att, None)
            if decr is None:
                raise AttributeError("field %s of %s is not defined" \
                                         % (att, self.name))
            x = decr.getReadback()
            if x is not None: return x
            x = decr.getSetpoint()
            if x is not None: return x
            raise AttributeError("error when reading field %s" % att)

    def __setattr__(self, att, val):
        # this could be called by AbstractElement.__init__ or Element.__init__
        if hasattr(super(CaElement, self), att):
            super(CaElement, self).__setattr__(att, val)
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
            super(CaElement, self).__setattr__(att, val)
            #raise AttributeError("Error")

    def updatePvRecord(self, pvname, properties, tags = []):
        """
        update the pv with property dictionary and tag list.
        """
        if not isinstance(pvname, (str, unicode)):
            raise TypeError("%s is not a valid type" % (type(pvname)))

        # update the properties
        if properties is not None: 
            self.updateProperties(properties)

        # check element field
        for t in tags:
            g = re.match(r'aphla.elemfield.([\w\d]+)(\[\d+\])?', t)
            if g is None: continue

            fieldname, idx = g.group(1), g.group(2)
            if idx is not None: 
                idx = int(idx[1:-1])
                logger.info("%s %s[%d]" % (pvname, fieldname, idx))

            # the default handle is 'READBACK'
            if properties is None or \
                    properties.get('handle', 'READBACK') == 'READBACK':
                self.setFieldGetAction(pvname, fieldname, idx)
            elif properties.get('handle') == 'SETPOINT':
                self.setFieldPutAction(pvname, fieldname, idx)
            else:
                raise ValueError("invalid 'handle' value '%s' for pv %s" % 
                                 (properties.get('handle'), pvname))
        # update the (pv, tags) dictionary
        if pvname in self._pvtags.keys(): self._pvtags[pvname].update(tags)
        else: self._pvtags[pvname] = set(tags)

    def setFieldGetAction(self, v, field, idx = None, desc = ''):
        """
        set the action when reading *field*.

        the previous action will be replaced if it was defined.
        *v* is single PV or a list/tuple
        """
        if not self._field.has_key(field):
            self._field[field] = CaDecorator(trace=self.trace)

        self._field[field].setReadbackPv(v, idx)

    def setFieldPutAction(self, v, field, idx=None, desc = ''):
        """
        set the action for writing *field*.

        the previous action will be replaced if it was define.
        *v* is a single PV or a list/tuple
        """
        if not self._field.has_key(field):
            self._field[field] = CaDecorator(trace=self.trace)

        self._field[field].setSetpointPv(v, idx)
        
    def fields(self):
        """
        return element's fields
        """
        return self._field.keys()


    def collect(self, elemlist, **kwargs):
        """
        collect properties in elemlist as its own.
        
        - *fields*, EPICS related
        - *attrs*, element attribute list
        """

        fields = kwargs.get("fields", [])
        attrs  = kwargs.get("attrs", [])
        for field in fields:
            pd = CaDecorator(trace=self.trace)
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
        return dir(CaElement) + list(self.__dict__) + self._field.keys()

    def __repr__(self):
        if self.virtual:
            return "%s [%s] (virtual)" % (self.name, self.family)
        else:
            AbstractElement.__repr__(self)

    def enableTrace(self, fieldname):
        self._field[fieldname].trace = True
        self._field[fieldname].mark()

    def disableTrace(self, fieldname):
        self._field[fieldname].trace = False
        self._field[fieldname].sp = []

    def revert(self, fieldname):
        self._field[fieldname].revert()

    def mark(self, fieldname, data = 'setpoint'):
        self._field[fieldname].mark(data)

    def reset(self, field):
        """
        see CaDecorator::reset()
        """
        self._field[field].reset()

    def get(self, fields, source='readback'):
        """
        get the values for given fields. the source can be 'readback' or
        'setpoint'.
        """
        if source.lower() == 'readback':
            if isinstance(fields, (str, unicode)):
                return self._field[fields].getReadback()
            else:
                # a list of fields
                return [self._field[v].getReadback() for v in fields]
        elif source.lower() == 'setpoint':
            if isinstance(fields, (str, unicode)):
                return self._field[fields].getSetpoint()
            else:
                return [self._field[v].getSetpoint() for v in fields]
        return None

    def settable(self, field):
        if field not in self._field.keys():
            return False
        return self._field[field].settable()

    def readable(self, field):
        if field in self._field.keys():
            return True
        return False

def merge(elems, **kwargs):
    """
    merge the fields for all elements in a list return it as a single
    element. The other properties of the new element are initialized by
    the input *kwargs*.

    .. seealso:: :func:`~aphla.element.CaElement`
    """
    count, pvdict = {}, {}
    for e in elems:
        fds = e.fields()
        for f in fds: 
            if f in count: count[f] += 1
            else: count[f] = 1
            pvrb = e.pv(field=f, handle='readback')
            pvsp = e.pv(field=f, handle='setpoint')
            if f not in pvdict: pvdict[f] = [[], []]
            #print f, pvrb, pvsp
            pvdict[f][0].extend(pvrb)
            pvdict[f][1].extend(pvsp)

    for k,v in count.iteritems(): 
        if v < len(elems): 
            pvdict.pop(k)
    #print pvdict.keys()
    elem = CaElement(**kwargs)
    for k,v in pvdict.iteritems():
        if len(v[0]) > 0: elem.setFieldGetAction(v[0], k, None, '')
        if len(v[1]) > 0: elem.setFieldPutAction(v[1], k, None, '')
        #print k, "GET", v[0]
        #print k, "PUT", v[1]
    elem.sb = [e.sb for e in elems]
    elem.se = [e.se for e in elems]
    return elem

