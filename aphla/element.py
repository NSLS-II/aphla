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
import warnings
from catools import caget, caput
from unitconv import *

logger = logging.getLogger(__name__)

class AbstractElement(object):
    """The :class:`AbstractElement` contains most of the lattice properties, such
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

    
    *index* is used for sorting elements in a list if it is not
    None. Otherwise sorted according to *sb*.
    """

    # format string for __str__
    _STR_FORMAT = "%d %s %s %.3f %.3f %s %s %s %s %s"
    #__slots__ = []
    def __init__(self, **kwargs):
        """
        create an element from Channel Finder Service data or explicit
        parameters.

        :param str name: element name
        """
        #print kwargs
        self.name     = kwargs.get('name', None)
        self.devname  = kwargs.get('devname', None)
        self.phylen   = float(kwargs.get('phylen', '0.0'))
        self.index    = int(kwargs.get('index', '-1'))
        self.family   = kwargs.get('family', None)
        self.se       = float(kwargs.get('se', 'inf'))
        self.sb       = float(kwargs.get('sb', 'inf'))
        self.length   = float(kwargs.get('length', '0.0'))
        self.cell     = kwargs.get('cell', None)
        self.girder   = kwargs.get('girder', None)
        self.symmetry = kwargs.get('symmetry', None)
        self.sequence = kwargs.get('sequence', (0, 0))

        self.group = set([self.family, self.cell, self.girder, self.symmetry])
        for g in kwargs.get('group', []): self.group.add(g)
        
    def profile(self, vscale=1.0):
        """the profile for drawing the lattice.

        The return is a tuple of (x, y, color) where (*x*, *y) are coordinates
        and *color* is one of the ['k', 'r', 'b'] depending its family.
        
        It recognize the following *family*:

        - 'QUAD', quadrupole, box height *vscale*, no negative
        - 'DIPOLE', dipole. box height vscale both positive and negative.
        - 'SEXT', sextupole. box height 1.4*vscale
        - ['HCOR' | 'VCOR' | 'TRIMX' | 'TRIMY'], corrector, thin line
        - ['BPM' | 'BPMX' | 'BPMY'], beam position monitor, thin line
        - The rest unrecognized element, it returns a box with height 
          0.2*vscale and color 'k'.

        """
        b, e = self.sb, max(self.sb + self.length, self.se)
        h = vscale
        if self.family == 'QUAD':
            return [b, b, e, e], [0, h, h, 0], 'k'
        elif self.family == 'DIPOLE':
            return [b, b, e, e, b, b, e, e], [0, h, h, -h, -h, h, h, 0], 'k'
        elif self.family == 'SEXT':
            return [b, b, e, e], [0, 1.4*h, 1.4*h, 0], 'k'
        elif self.family in ['HCOR', 'VCOR', 'TRIMX', 'TRIMY']:
            return [b, (b+e)/2.0, (b+e)/2.0, (b+e)/2.0, e], \
                [0, 0, h, 0, 0], 'r'
        elif self.family in ['BPM', 'BPMX', 'BPMY']:
            return [b, (b+e)/2.0, (b+e)/2.0, (b+e)/2.0, e], \
                [0, 0, h, 0, 0], 'b'
        else:
            return [b, b, e, e], [0, 0.2*h, 0.2*h, 0], 'k'

    def __str__(self):
        return AbstractElement._STR_FORMAT % (
            self.index, self.name, self.family, self.sb, self.length,
            self.devname, self.cell, self.girder, self.symmetry, self.sequence)

    def __repr__(self):
        return "%s:%s @ sb=%f" % (self.name, self.family, self.sb)
            
    def __lt__(self, other):
        """use *index* if not None, otherwise use *sb*"""
        if self.index is None or other.index is None:
            return self.sb < other.sb
        else:
            return self.index < other.index

    def __gt__(self, other):
        """use *index* if not None, otherwise use *sb*"""
        if self.index is None or other.index is None:
            return self.sb > other.sb
        else:
            return self.index > other.index

    def __eq__(self, other):
        """compares location, length and name"""
        return self.sb == other.sb and \
               self.length == other.length and \
               self.index == other.index and \
               self.name == other.name

    def updateProperties(self, prpt):
        """
        Update the properties of this element.

        :param dict prpt: a dictionary with the following keys:

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
    manages channel access for an element field.

    it manages a list of readback and setpoint PVs. Each PV has its own
    stepsize and value range.

    If *trace* is True, every readback/setpoint will be recorded for later
    reset/revert whenever the get/put functions are called. Extra history
    point can be recorded by calling *mark*.

    None in unit conversion means the lower level unit, like the PV in EPICS.
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
        self.pvunit = '' # most of the cases, the unit is "Ampere", the current
        self.rb = []  # bufferred readback value 
        self.sp = []  # bufferred setpoint value
        self.field = ''
        self.desc = kwargs.get('desc', None)
        self.order = self.Ascending
        self.trace = kwargs.get('trace', False)
        self.trace_limit = 200
        self.unitconv = {}

    def __eq__(self, other):
        return self.pvrb == other.pvrb and \
            self.pvsp == other.pvsp and \
            self.field == other.field and \
            self.desc == other.desc
            
    def _insert_in_order(self, lst, v):
        """
        insert `v` to an ordered list `lst`
        """
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

    def _unit_conv(self, x, src, dst):
        if (src, dst) == (None, None): return x

        uc = self.unitconv.get((src, dst), None)
        if uc is None:
            raise RuntimeError("no method for unit conversion from "
                               "'%s' to '%s'" % (src, dst))
        else:
            return uc.eval(x)

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
        reset the setpoint to the ealiest known history. If the `trace_limit`
        is large enough, the setpoint will be restored to the value before
        changed in aphla for the first time.
        """
        if not self.sp: return
        caput(slef.pvsp, self.sp[0])
        self.sp = []

    def mark(self, data = 'setpoint'):
        """
        mark the current value in trace for revert

        :param str data: which data to mark:

        - `setpoint` save setpoint value (default)
        - `readback` save readback value
        - `rb2setpoint` save readback value to setpoint

        The default is mark the current setpoint and an imediate revert will
        restore this setpoint.

        When the queue is full, pop the 2nd data keep the first for `reset`
        """
        if data == 'readback':
            self.rb.append(caget(self.pvrb))
            if len(self.rb) > self.trace_limit: self.rb.pop(1)
        elif data == 'setpoint':
            self.sp.append(caget(self.pvsp))
            if len(self.sp) > self.trace_limit: self.sp.pop(1)
        elif data == 'rb2setpoint':
            self.sp.append(caget(self.pvrb))
            if len(self.sp) > self.trace_limit: self.sp.pop(1)

    def getReadback(self, unitsys = None):
        """
        return the value of readback PV or None if such pv is not defined.
        """
        if self.pvrb: 
            #print __name__
            #logger.info("testing")
            rawret = caget(self.pvrb)
            ret = self._unit_conv(rawret, None, unitsys)
            if self.trace: 
                self.rb.append(copy.deepcopy(rawret))
                if len(self.rb) > self.trace_limit: 
                    # keep the first one for `reset`
                    self.rb.pop(1)
            if len(self.pvrb) == 1: 
                return ret[0]
            else: return ret
        else: return None

    def getSetpoint(self, unitsys = None):
        """
        return the value of setpoint PV or None if such PV is not defined.
        """
        if self.pvsp:
            rawret = caget(self.pvsp)
            ret = self._unit_conv(rawret, None, unitsys)
            if len(self.pvsp) == 1: return ret[0]
            else: return ret
        else: return None

    def putSetpoint(self, val, unitsys = None):
        """
        set a new setpoint.

        :param val: the new value(s)
        :type val: float, list, tuple

        keep the old setpoint value if `trace=True`. Only upto `trace_limit`
        number of history data are kept.
        """
        if self.pvsp:
            rawval = self._unit_conv(val, unitsys, None)
            ret = caput(self.pvsp, rawval, wait=True)
            if self.trace: 
                if isinstance(val, (list, tuple)):
                    self.sp.append(rawval[:])
                elif isinstance(val, (float, int)):
                    self.sp.append(rawval)
                else:
                    raise RuntimeError("unsupported datatype '%s' "
                                       "for tracing object value." %
                                       type(val))
                if len(self.sp) > self.trace_limit: 
                    # keep the first for reset
                    self.sp.pop(1)
            return ret
        else: return None

    def setReadbackPv(self, pv, idx = None):
        """
        set/replace the PV for readback. 

        :param str pv: PV name
        :param int idx: index in the PV list

        `idx` is needed if such readback has a list
        of PVs.  if idx is None, replace the original one. if idx is an index
        integer and pv is not a list, then replace the one with this index.
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

    def setSetpointPv(self, pv, idx = None, **kwargs):
        """
        set the PV for setpoint at position idx. 

        :param str pv: PV name
        :param int idx: index in the PV list.

        if idx is None, replace the original one. if idx is an index integer
        and pv is not a list, then replace the one with this index.

        seealso :func:`setStepSize`, :func:`setBoundary`
        """
        #lim = kwargs.get("boundary", None)
        #h = kwargs.get("step_size", None)
        if idx is None:
            if isinstance(pv, (str, unicode)):
                self.pvsp = [pv]
                self.pvh = [None]
                self.pvlim = [None]
            elif isinstance(pv, (tuple, list)):
                self.pvsp = [p for p in pv]
                self.pvh = [None] * len(pv)
                self.pvlim = [None] * len(pv)
        elif not isinstance(pv, (tuple, list)):
            while idx >= len(self.pvsp): 
                self.pvsp.append(None)
                self.pvh.append(None)
                self.pvlim.append(None)
            self.pvsp[idx] = pv
            self.pvh[idx] = None
            self.pvlim[idx] = None
        else:
            raise RuntimeError("invalid setpoint pv '%s' for position '%s'" % 
                               (str(pv), str(idx)))


    def setStepSize(self, val, **kwargs):
        """
        set the step size for the setpoint PV. 

        :param float val: the step size 
        :param int index: index in the PV list.
        :param str pv: pv name

        when using *index*, the corresponding PV with that index should be set
        before.

        all PVs with same name will be updated if there are duplicates in
        setpoint pv list.

        seealso :func:`setBoundary`
        """
        idx = kwargs.get('index', None)
        pv  = kwargs.get('pv', None)
        if idx is not None:
            if idx >= len(self.pvsp):
                raise RuntimeError("no setpoint PV defined for index %d" % idx)
            self.pvh[idx] = val
        elif pv is not None:
            for i,pvi in enumerate(self.pvsp):
                if pv == pvi: self.pvh[i] = val

    def setBoundary(self, low, high, **kwargs):
        """
        set the boundary values for the setpoint PV. 

        :param float low: the lower boundary value
        :param float high: the higher boundary value
        :param int index: index in the PV list.
        :param str pv: pv name

        when using *index*, the corresponding PV with that index should be set
        before.

        all PVs with same name will be updated if there are duplicates in
        setpoint pv list.

        seealso :func:`setStepSize`
        """
        idx = kwargs.get('index', None)
        pv  = kwargs.get('pv', None)
        if idx is not None:
            if idx >= len(self.pvsp):
                raise RuntimeError("no setpoint PV defined for index %d" % idx)
            self.pvlim[idx] = (low, high)
        elif pv is not None:
            for i,pvi in enumerate(self.pvsp):
                if pv == pvi: self.pvlim[i] = (low, high)
        
    def appendReadback(self, pv):
        """append the pv as readback"""
        self.pvrb.append(pv)

    def appendSetpoint(self, pv):
        """append the pv as setpoint"""
        self.pvsp.append(pv)
        self.pvh.append(None)

    def removeReadback(self, pv):
        """remove the pv from readback"""
        self.pvrb.remove(pv)

    def removeSetpoint(self, pv):
        """remove the pv from setpoint"""
        i = self.pvsp.index(pv)
        self.pvsp.pop(i)
        self.pvh.pop(i)
        
    def stepSize(self, **kwargs):
        """
        return the stepsize of setpoint PV list
        
        :param index: PV with an index in the list
        :param pv: one particular PV
        :rtype: single value or a list of values.

        hardware unit
        """

        index = kwargs.get('index', None)
        pv = kwargs.get('pv', None)
        if index is not None:
            return self.pvh[index]
        elif pv is not None:
            return self.pvh[self.pvsp.index(pv)]
        elif len(self.pvh) == 0:
            raise RuntimeError("no stepsize set for pv '%s'" % str(self.pvsp))
        elif len(self.pvh) == 1:
            return self.pvh[0]
        else:
            return self.pvh[:]
        
    def boundary(self, **kwargs):
        """
        return the (low, high) range of the setpoint PV list
        
        :param index: PV with an index in the list
        :param pv: one particular PV
        :rtype: single value or a list of values.

        hardware unit
        """

        index = kwargs.get('index', None)
        pv = kwargs.get('pv', None)
        if index is not None:
            return self.pvlim[index]
        elif pv is not None:
            return self.pvlim[self.pvsp.index(pv)]
        elif len(self.pvlim) == 0:
            raise RuntimeError("no stepsize set for pv '%s'" % str(self.pvsp))
        elif len(self.pvlim) == 1:
            return self.pvlim[0]
        else:
            return self.pvlim[:]
        
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

    'field' -> Object Attr.
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
        # the linked element, alias
        self.__dict__['alias'] = []
        # update all element properties
        super(CaElement, self).__init__(**kwargs)
        
    def __setstate__(self, data):
        for (name, value) in data.iteritems():
            if name in ['_field', '_pvtags']:
                self.__dict__[name] = value
            else:
                super(CaElement, self).__setattr__(name, value)
            
    def _pv_1(self, **kwargs):
        """find the pv when len(kwargs)==1.
        
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

        Examples
        ----------
        >>> pv() # returns all pvs.
        >>> pv(tag='aphla.X')
        >>> pv(tags=['aphla.EGET', 'aphla.Y'])
        >>> pv(field = "x")
        >>> pv(field="x", handle='readback')

        seealso :class:`CaDecorator`
        """
        if len(kwargs) == 0:
            return self._pvtags.keys()
        elif len(kwargs) == 1:
            return self._pv_1(**kwargs)
        elif len(kwargs) == 2:
            handle = kwargs.get('handle', None)
            fd = kwargs.get('field', None)
            if fd not in self._field: return []
            if handle == 'readback':
                return self._field[kwargs['field']].pvrb
            elif handle == 'setpoint':
                return self._field[kwargs['field']].pvsp
            else:
                return []
        else: return []

    def hasPv(self, pv, inalias = False):
        """check if this element has pv.

        inalias=True will also check its alias elements. 

        If the alias (child) has its aliases (grand children), they are not
        checked. (no infinite loop)
        """
        if self._pvtags.has_key(pv): return True
        if inalias == True:
            for e in self.alias: 
                #if e.hasPv(pv): return True
                if e._pvtags.has_key(pv): return True
        return False
        
    def appendStatusPv(self, pv, desc, order=True):
        """append (func, pv, description) to status"""
        decr = self._field['status']
        if not decr: self._field['status'] = CaDecorator(trace=self.trace)
        
        self._field['status'].appendReadback(pv)

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
                raise AttributeError("field '%s' is not defined for '%s'" % (
                        att, self.name))
            if not decr.pvsp:
                raise ValueError("field '%s' in '%s' is not writable" % (
                        att, self.name))
            decr.putSetpoint(val)
        elif att in self.__dict__.keys():
            self.__dict__[att] = val
        else:
            # new attribute for superclass
            super(CaElement, self).__setattr__(att, val)
            #raise AttributeError("Error")
        for e in self.alias: e.__setattr__(att, val)

    def addUnitConversion(self, field, uc, src, dst):
        """add unit conversion for field"""
        # src, dst is unit system name
        self._field[field].unitconv[(src, dst)] = uc

    def convertUnit(self, field, x, src, dst):
        return self._field[field]._unit_conv(x, src, dst)

    def get_unit_systems(self, field):
        """get a list all unit systems for field. 

        None is the lower level unit, e.g. in EPICS channel
        """
        if not self._field[field].unitconv: return [None]
        #if not self._field[field].unitconv.keys(): return []

        src, dst = zip(*(self._field[field].unitconv.keys()))
        return list(set(src).intersection(dst))

    def getUnitSystems(self, field = None):
        """return a list of available unit systems for field. 

        If no field specified, return a dictionary for all fields and their
        unit systems.

        None means the unit used in the lower level control system, e.g. EPICS.
        """
        if field is None:
            return dict([(f, self.get_unit_systems(f)) for f \
                             in self._field.keys()])
        else:
            return self.get_unit_systems(field)

    def getUnit(self, field, unitsys='phy'):
        """get the unit name of a unit system, e.g. unitsys='phy'

        return '' if no such unit system.
        """
        if field in self._field.keys() and unitsys == None: 
            return self._field[field].pvunit

        for k,v in self._field[field].unitconv.iteritems():
            if k[0] == unitsys: return v.direction[0]
            elif k[1] == unitsys: return v.direction[1]
            
        return ''

    def setRawUnit(self, field, u):
        """set the unit symbol for raw unit system"""
        if field not in self._field.keys(): 
            raise RuntimeError("element '%s' has no '%s' field" % \
                               self.name, field)

        self._field[field].pvunit = u


    def updatePvRecord(self, pvname, properties, tags = []):
        """update the pv with property dictionary and tag list."""
        if not isinstance(pvname, (str, unicode)):
            raise TypeError("%s is not a valid type" % (type(pvname)))

        # update the properties
        if properties is not None: 
            self.updateProperties(properties)

        
        # the default handle is 'READBACK'
        if properties is not None:
            elemhandle = properties.get('handle', 'readback')
            fieldfname = properties.get('field', None)
            pvunit = properties.get('unit', '')
            if fieldfname is not None:
                g = re.match(r'([\w\d]+)(\[\d+\])?', fieldfname)
                if g is None:
                    raise ValueError("invalid field '%s'" % fieldfname)
                fieldname, idx = g.group(1), g.group(2)
                if idx is not None: idx = int(idx[1:-1])
                if elemhandle == 'readback': 
                    self.setFieldGetAction(pvname, fieldname, idx)
                elif elemhandle == 'setpoint':
                    self.setFieldPutAction(pvname, fieldname, idx)
                else:
                    raise ValueError("invalid handle value '%s' for pv '%s'" % 
                                     (elemhandle, pvname))
                if pvunit: self._field[fieldname].pvunit = pvunit
                logger.info("'%s' field '%s'[%s] = '%s'" % (
                        elemhandle, fieldname, idx, pvname))

        # check element field
        #for t in tags:
        #    g = re.match(r'aphla.elemfield.([\w\d]+)(\[\d+\])?', t)
        #    if g is None: continue
        #
        #    fieldname, idx = g.group(1), g.group(2)
        #    if idx is not None: 
        #        idx = int(idx[1:-1])
        #        logger.info("%s %s[%d]" % (pvname, fieldname, idx))
                        
        # update the (pv, tags) dictionary
        if pvname in self._pvtags.keys(): self._pvtags[pvname].update(tags)
        else: self._pvtags[pvname] = set(tags)

    def setFieldGetAction(self, v, field, idx = None, desc = ''):
        """set the action when reading *field*.

        the previous action will be replaced if it was defined.
        *v* is single PV or a list/tuple
        """
        if not self._field.has_key(field):
            self._field[field] = CaDecorator(trace=self.trace)

        self._field[field].setReadbackPv(v, idx)

    def setFieldPutAction(self, v, field, idx=None, desc = ''):
        """set the action for writing *field*.

        the previous action will be replaced if it was define.
        *v* is a single PV or a list/tuple
        """
        if not self._field.has_key(field):
            self._field[field] = CaDecorator(trace=self.trace)

        self._field[field].setSetpointPv(v, idx)
        
    def fields(self):
        """return element's fields, not sorted."""
        return self._field.keys()

    def stepSize(self, field):
        """return the stepsize of field"""
        return self._field[field].stepSize()

    def boundary(self, field):
        """return the (low, high) range of *field*"""
        return self._field[field].boundary()

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
            return AbstractElement.__repr__(self)

    def enableTrace(self, fieldname):
        if not self._field[fieldname].trace:
            self._field[fieldname].trace = True
            self._field[fieldname].sp = []

    def disableTrace(self, fieldname):
        if self._field[fieldname].trace:        
            self._field[fieldname].trace = False
            self._field[fieldname].sp = []

    def revert(self, fieldname):
        """undo the field value to its previous one"""
        self._field[fieldname].revert()
        for e in self.alias: e._field[fieldname].revert()

    def mark(self, fieldname, handle = 'setpoint'):
        self._field[fieldname].mark(handle)
        for e in self.alias: e._field[fieldname].mark(handle)

    def reset(self, fieldname):
        """see CaDecorator::reset()"""
        self._field[fieldname].reset()
        for e in self.alias: e._field[fieldname].reset()

    def _get_field(self, field, **kwargs):
        """
        read value of a single field, returns None if no such field.
        """
        handle = kwargs.get('handle', 'readback').lower()
        unitsys = kwargs.get('unitsys', None)
    
        if not self._field.has_key(field):
            v = None
        elif handle == 'readback':
            v = self._field[field].getReadback(unitsys)
        elif handle.lower() == 'setpoint':
            v = self._field[field].getSetpoint(unitsys)
        else:
            raise ValueError("unknow handle {0}" % field)
        
        # convert unit when required
        return v
        
    def get(self, fields, handle='readback', unitsys='phy'):
        """get the values for given fields. None if not exists.

        Parameters
        -------------
        fields : str, list. field
        handle : str. 'readback' or 'setpoint'.
        unitsys : the unit system. None for lower level unit.

        Example
        -----------
        >>> get('x')
        >>> get(['x', 'y'])
        >>> get(['x', 'unknown'])
          [ 0, None]

        """

        kw = {'handle': handle, 'unitsys': unitsys}
        if isinstance(fields, (str, unicode)):
            return self._get_field(fields, **kw)
        else:
            # a list of fields
            return [ self._get_field(v, **kw) for v in fields]

    def _put_field(self, field, val, unitsys, **kwargs):
        """set *val* to *field*.

        seealso :func:`pv(field=field)`
        """

        att = field
        if self.__dict__['_field'].has_key(att):
            decr = self.__dict__['_field'][att]
            if not decr:
                raise AttributeError("field '%s' is not defined for '%s'" % (
                        att, self.name))
            if not decr.pvsp:
                raise ValueError("field '%s' in '%s' is not writable" % (
                        att, self.name))
            decr.putSetpoint(val, unitsys)
        else:
            raise RuntimeError("field '%s' is not defined for '%s'" % (
                    att, self.name))
        

    def put(self, field, val, unitsys = 'phy'):
        """set *val* to *field*.

        seealso :func:`pv(field=field)`
        """
        self._put_field(field, val, unitsys)
        for e in self.alias: e._put_field(field, val, unitsys=unitsys)

    def settable(self, field):
        """check if the field has any setpoint PV"""
        if field not in self._field.keys():
            return False
        return self._field[field].settable()

    def readable(self, field):
        """
        check if the field is defined
        """
        if field in self._field.keys():
            return True
        return False


def merge(elems, **kwargs):
    """
    merge the fields for all elements in a list return it as a single
    element. 

    Parameters
    -----------
    elems : list. a list of element object
    kwargs: dict. other properties of the new element.

    Examples
    ----------
    >>> bpm = getElements('BPM') 
    >>> vpar = { 'virtual': 1, 'name': 'VBPM' }
    >>> vbpm = merge(bpm, **vpar)

    Notes
    ------
    It does not merge the unit conversion. All raw unit.
    seealso :class:`CaElement`

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

    # consider only the common fields
    for k,v in count.iteritems(): 
        if v < len(elems): 
            print("field '%s' has %d < %d" % (k, v, len(elems)))
            pvdict.pop(k)
    #print pvdict.keys()
    elem = CaElement(**kwargs)
    for k,v in pvdict.iteritems():
        if len(v[0]) > 0: elem.setFieldGetAction(v[0], k, None, '')
        if len(v[1]) > 0: elem.setFieldPutAction(v[1], k, None, '')

    # if all raw units are the same, so are the merged element
    for fld in elem.fields():
        units = sorted([e.getUnit(fld, unitsys=None) for e in elems])
        if units[0] == units[-1]:
            elem.setRawUnit(fld, units[0])

    elem.sb = [e.sb for e in elems]
    elem.se = [e.se for e in elems]
    elem._name = [e.name for e in elems]
    return elem

