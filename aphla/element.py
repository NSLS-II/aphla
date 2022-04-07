from __future__ import print_function, division, absolute_import
from six import string_types

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
from .catools import caget, caput, FORMAT_CTRL, FORMAT_TIME
from collections.abc import Iterable
from functools import partial
from itertools import permutations

from . import CONFIG
from . import ureg, Q_
from . import OperationMode, OP_MODE
from .unitconv import *
from . import engines
from .models import modelget, modelput

# public symbols
__all__ = [ "CaElement", "merge",
            "ASCENDING", "DESCENDING", "UNSPECIFIED" ]

_logger = logging.getLogger("aphla.element")
#_logger.setLevel(logging.DEBUG)

# flags bit pattern
_DISABLED = 0x01
_READONLY = 0x02

UNSPECIFIED = 0
ASCENDING   = 1
DESCENDING  = 2
RANDOM      = 3

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
    _STR_FORMAT = "{0} {1} {2} {3} {4} {5} {6} {7} {8} {9}"
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
        self.flag   = 0

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
        return AbstractElement._STR_FORMAT.format(
            self.index, self.name, self.family, self.sb, self.length,
            self.devname, self.cell, self.girder, self.symmetry, self.sequence)

    def __repr__(self):
        return "%s:%s @ sb=%f" % (self.name, self.family, self.sb)

    def __lt__(self, other):
        """use *index* if not None, otherwise use *sb*"""
        if self.index is None and other.index is None:
            return True
        elif self.index is None:
            return False
        elif other.index is None:
            return True
        elif self.index > 0 and other.index > 0:
            return self.sb < other.sb
        elif self.index > 0:
            return True
        elif other.index > 0:
            return False
        else:
            # both less than 0
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

        if 'family' in prpt:
            # rename the family name, append to group. The family name is kept
            # unique, but "pushed" old family name to group name
            newfam = prpt['family']
            if not newfam in self.group: self.group.append(newfam)
            self.family = newfam

        if 'devname' in prpt:
            self.devname = prpt['devname']
        if 'cell' in prpt:
            self.cell = prpt['cell']
        if 'girder' in prpt:
            self.girder = prpt['girder']
        if 'symmetry' in prpt:
            self.symmetry = prpt['symmetry']

        if 'phylen' in prpt:
            self.phylen = float(prpt['phylen'])
        if 'length' in prpt:
            self.length = float(prpt['length'])
        if 'se' in prpt:
            self.se = float(prpt['se'])
        if 'sb' in prpt:
            self.sb = float(prpt['sb'])
        if 'index' in prpt:
            self.index = int(prpt['index'])

    def isEnabled(self):
        return not (self.flag & _DISABLED)

    def setEnabled(self, b):
        if b:
            self.flag = self.flag & ~_DISABLED
        else:
            self.flag = self.flag | _DISABLED


class CaAction:
    """
    manages channel access for an element field.

    it manages a list of readback and setpoint PVs. Each PV has its own
    stepsize and value range.

    If *trace* is True, every readback/setpoint will be recorded for later
    reset/revert whenever the get/put functions are called. Extra history
    point can be recorded by calling *mark*.

    None in unit conversion means the lower level unit, like the PV in EPICS.
    """
    ALLDATA  = 0
    READBACK = 1
    SETPOINT = 2
    GOLDEN   = 3
    def __init__(self, **kwargs):
        self.pvrb = [] # readback pv (process variable)
        self.pvsp = [] # setpoint pv (process variable)
        self.mvrb = [] # readback mv (model variable)
        self.mvsp = [] # setpoint mv (model variable)
        # self.unitconv = {}
        self.ucrb = {}  # unit conversion for readback
        self.ucsp = {}  # unit conversion for setpoint
        self.ucfrb = {} # unit conversion function for readback
        self.ucfsp = {} # unit conversion function for setpoint
        self.golden = [] # some setpoint can saved as golden value
        self.pvh  = [] # step size
        self.pvlim = [] # lower/upper limit
        # buffer the initial value and last setting/reading
        self.pvrbunit = '' # unit for readback PVs
        self.pvspunit = '' # overwrite unit in unit conversions
        self.rb = []  # bufferred readback value
        self.sp = []  # bufferred setpoint value
        self._sp1 = [] # the last bufferred sp value when sp dimension changes.
        self.field = ''
        self.desc = kwargs.get('desc', None)
        self.order = ASCENDING
        self.opflags = 0
        self.trace = kwargs.get('trace', False)
        self.trace_limit = 200
        self.timeout = 2
        self.sprb_epsilon = 0

    def __eq__(self, other):
        return self.pvrb == other.pvrb and \
            self.pvsp == other.pvsp and \
            self.field == other.field and \
            self.desc == other.desc

    def _insert_in_order(self, lst, v):
        """
        insert `v` to an ordered list `lst`
        """
        if len(lst) == 0 or self.order == UNSPECIFIED:
            if isinstance(v, (tuple, list)): lst.extend(v)
            else: lst.append(v)
            return 0

        if self.order == ASCENDING:
            for i,x in enumerate(lst):
                if x < v: continue
                lst.insert(i, v)
                return i
        elif self.order == DESCENDING:
            for i,x in enumerate(lst):
                if x > v: continue
                lst.insert(i, v)
                return i

        lst.append(v)
        return len(lst) - 1

    #def _unit_conv(self, x, src, dst, unitconv):
        #if (src, dst) == (None, None): return x

        ## try (src, dst) first
        #uc = unitconv.get((src, dst), None)
        #if uc is not None:
            #return uc.eval(x)

        ## then inverse (dst, src)
        #uc = unitconv.get((dst, src), None)
        #if uc is not None and uc.invertible:
            #return uc.eval(x, True)
        #else:
            #raise RuntimeError("no method for unit conversion from "
                               #"'%s' to '%s'" % (src, dst))
    def _unit_conv(self, x, src, dst, handle):

        unit = None

        if handle == 'readback':

            #return self.ucfrb[(src, dst)](x)

            if not CONFIG['unitless_quantities']:
                for k, v in self.ucrb.items():
                    if k[0] == dst:
                        unit = v.srcunit
                        break
                    elif k[1] == dst:
                        unit = v.dstunit
                        break
                else:
                    unit = None

            m = self.ucfrb[(src, dst)](x)

        elif handle == 'setpoint':

            #return self.ucfsp[(src, dst)](x)

            if not CONFIG['unitless_quantities']:
                for k, v in self.ucsp.items():
                    if k[0] == dst:
                        unit = v.srcunit
                        break
                    elif k[1] == dst:
                        unit = v.dstunit
                        break
                else:
                    unit = None

            m = self.ucfsp[(src, dst)](x)

        else:
            raise ValueError(f'Invalid handle: {handle}')

        if unit:
            if isinstance(m, Q_):
                return m.to(unit)
            else:
                return Q_(m, unit)
        else:
            return m

    def _all_within_range(self, v, lowhigh):
        """if lowhigh is not valid, returns true"""
        # did not check for string type
        if isinstance(v, string_types): return True
        if lowhigh is None: return True

        low, high = lowhigh
        if isinstance(v, (float, int, Q_)):
            if low is None: return v <= high
            elif high is None: return v >= low
            elif high <= low: return True
            elif v > high or v < low: return False
            else: return True
        elif isinstance(v, (list, tuple)):
            for vi in v:
                if not self._all_within_range(vi, lowhigh): return False
            return True
        else:
            raise RuntimeError("unknow data type '{0}:{1}'".format(v, type(v)))


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

    def reset(self, data = 'origin'):
        """
        reset the setpoint to the ealiest known history. If the `trace_limit`
        is large enough, the setpoint will be restored to the value before
        changed in aphla for the first time.

        Parameters
        -----------
        data : str. 'origin' or 'golden'. 'origin' data is the earliest history.

        Returns
        --------
        v : None or previous data if set a new value.
        """
        ret = None
        if data == 'origin' and self.sp:
            ret = caget(self.pvsp, timeout=self.timeout)
            caput(self.pvsp, self.sp[0], timeout=self.timeout)
            self.sp = []
        elif data == 'golden' and self.golden and self.pvsp:
            ret = caget(self.pvsp, timeout=self.timeout)
            caput(self.pvsp, self.golden, timeout=self.timeout)
            _logger.debug("setting {0} to {1}".format(
                    self.pvsp, self.golden))
            #print "setting {0} to {1}".format(self.pvsp, self.golden)
        return None

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
            self.rb.append(caget(self.pvrb, timeout=self.timeout))
            if len(self.rb) > self.trace_limit: self.rb.pop(1)
        elif data == 'setpoint':
            self.sp.append(caget(self.pvsp, timeout=self.timeout))
            if len(self.sp) > self.trace_limit: self.sp.pop(1)
        elif data == 'rb2setpoint':
            self.sp.append(caget(self.pvrb, timeout=self.timeout))
            if len(self.sp) > self.trace_limit: self.sp.pop(1)

    def getReadback(self, unitsys = None):
        """
        return the value of readback PV or None if such pv is not defined.
        """
        if self.opflags & _DISABLED: raise IOError("reading a disabled element")

        if OP_MODE.value == OperationMode.ONLINE:
            if self.pvrb:
                #print __name__
                #_logger.info("testing")
                rawret = caget(self.pvrb, timeout=self.timeout)
                if self.trace:
                    self.rb.append(copy.deepcopy(rawret))
                    if len(self.rb) > self.trace_limit:
                        # keep the first one for `reset`
                        self.rb.pop(1)
                if len(self.pvrb) == 1:
                    return self._unit_conv(rawret[0], None, unitsys, 'readback')
                else:
                    return self._unit_conv(rawret, None, unitsys, 'readback')
            else:
                return None
        elif OP_MODE.value == OperationMode.SIMULATION:
            if self.mvrb:
                rawret = modelget(self.mvrb)
                model_unitsys = engines.getEngineName()
                if unitsys == 'model':
                    unitsys = model_unitsys
                if len(self.mvrb) == 1:
                    return self._unit_conv(rawret[0], model_unitsys, unitsys, 'readback')
                else:
                    return self._unit_conv(rawret, model_unitsys, unitsys, 'readback')
            else:
                return None
        else:
            raise ValueError(f'Unexpected operation mode value : {OP_MODE.value}')

    def getGolden(self, unitsys = None):
        """return golden value in unitsys"""
        if len(self.golden) == 1:
            #return self._unit_conv(self.golden[0], None, unitsys, self.ucsp)
            return self._unit_conv(self.golden[0], None, unitsys, 'setpoint')
        else:
            return self._unit_conv(self.golden, None, unitsys, self.ucsp)

    def setGolden(self, val, unitsys = None):
        """set golden value in unitsys"""
        #ret = self._unit_conv(val, unitsys, None, self.ucsp)
        ret = self._unit_conv(val, unitsys, None, 'setpoint')
        if isinstance(ret, (list, tuple)):
            for i in range(len(self.golden)):
                self.golden[i] = ret[i]
        elif len(self.golden) == 1:
            self.golden[0] = ret
        else:
            raise ValueError("improper golden val {0} for {1}".format(
                    ret, self.pvsp))


    def getSetpoint(self, unitsys = None):
        """
        return the value of setpoint PV or None if such PV is not defined.
        """

        if OP_MODE.value == OperationMode.ONLINE:
            if self.pvsp:
                rawret = caget(self.pvsp, timeout=self.timeout, format=FORMAT_CTRL)
                # update the limits when necessary
                for i in range(len(self.pvsp)):
                    if self.pvlim[i] is None:
                        try:
                            self.pvlim[i] = (
                                self._unit_conv(rawret[i].lower_ctrl_limit,
                                                None, unitsys, 'setpoint'),
                                self._unit_conv(rawret[i].upper_ctrl_limit,
                                                None, unitsys, 'setpoint')
                            )
                        except:
                            pass
                if len(self.pvsp) == 1:
                    return self._unit_conv(rawret[0], None, unitsys, 'setpoint')
                else:
                    return self._unit_conv(rawret, None, unitsys, 'setpoint')
            else:
                #raise ValueError("no setpoint PVs")
                return None
        elif OP_MODE.value == OperationMode.SIMULATION:
            if self.mvsp:
                rawret = modelget(self.mvsp)
                model_unitsys = engines.getEngineName()
                if unitsys == 'model':
                    unitsys = model_unitsys
                if len(self.mvsp) == 1:
                    return self._unit_conv(rawret[0], model_unitsys, unitsys, 'setpoint')
                else:
                    return self._unit_conv(rawret, model_unitsys, unitsys, 'setpoint')
            else:
                return None
        else:
            raise ValueError(f'Unexpected operation mode value : {OP_MODE.value}')

    def putSetpoint(self, val, unitsys = None, bc = 'exception', wait=True, timeout = 5):
        """
        set a new setpoint.

        :param val: the new value(s)
        :type val: float, list, tuple

        keep the old setpoint value if `trace=True`. Only upto `trace_limit`
        number of history data are kept.

        bc = 'boundary' is the same as 'ignore' for this moment.
        """
        if self.opflags & _DISABLED:
            raise IOError("setting an disabled element")
        if self.opflags & _READONLY: raise IOError("setting a readonly field")

        if OP_MODE.value == OperationMode.ONLINE:
            if isinstance(val, (float, int, str, Q_)):
                #rawval = [self._unit_conv(val, unitsys, None, self.ucsp)] * \
                    #len(self.pvsp)
                rawval = [self._unit_conv(val, unitsys, None, 'setpoint')] * \
                    len(self.pvsp)
            else:
                # one more level of nest, due to pvsp=[]
                #rawval = [ [self._unit_conv(v, unitsys, None, self.ucsp) for v in val] ]
                rawval = [ [self._unit_conv(v, unitsys, None, 'setpoint') for v in val] ]

            # under and over flow check
            for i,lim in enumerate(self.pvlim):
                # update boundary if not done before
                if lim is None:
                    try:
                        self._update_sp_lim_h(i)
                    except:
                        _logger.warn("can not update limits for {0}".format(
                                self.pvsp[i]))
                lowhigh = self.pvlim[i]
                if self._all_within_range(rawval[i], lowhigh): continue

                if bc == 'exception':
                    raise OverflowError(
                        "value {0} is outside of boundary {1}".format(rawval[i], lowhigh))
                elif bc == 'boundary':
                    _logger.info("setting {0} to its boundary {1} instead of {2}".\
                                     format(self.pvsp[i], lowhigh, rawval[i]))
                    #rawval[i] = bc_val
                elif bc == 'ignore':
                    pass

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

            if not CONFIG['unitless_quantities']:
                rawval_wo_units = [v.m for v in rawval]
            else:
                rawval_wo_units = rawval

            retlst = caput(self.pvsp, rawval_wo_units,
                           wait=wait, timeout=timeout)
            for i,ret in enumerate(retlst):
                if ret.ok: continue
                raise RuntimeError("Failed at setting {0} to {1}".format(
                        self.pvsp[i], rawval[i]))

        elif OP_MODE.value == OperationMode.SIMULATION:
            model_unitsys = engines.getEngineName()
            if unitsys == 'model':
                unitsys = model_unitsys
            if isinstance(val, (float, int, str)):
                #rawval = [self._unit_conv(val, unitsys, model_unitsys, self.ucsp)] * \
                    #len(self.mvsp)
                rawval = [self._unit_conv(val, unitsys, model_unitsys, 'setpoint')] * \
                    len(self.mvsp)
            else:
                # one more level of nest, due to mvsp=[]
                #rawval = [ [self._unit_conv(v, unitsys, model_unitsys, self.ucsp)
                            #for v in val] ]
                rawval = [ [self._unit_conv(v, unitsys, model_unitsys, 'setpoint')
                            for v in val] ]

            retlst = modelput(self.mvsp, rawval)

        else:
            raise ValueError(f'Unexpected operation mode value : {OP_MODE.value}')

        return retlst

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
            if isinstance(pv, string_types):
                self.pvrb = [pv]
            elif isinstance(pv, (tuple, list)):
                self.pvrb = [p for p in pv]
            while len(self.golden) < len(self.pvrb): self.golden.append(None)
        elif not isinstance(pv, (tuple, list)):
            while idx >= len(self.pvrb): self.pvrb.append(None)
            while idx >= len(self.golden): self.golden.append(None)
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
            if isinstance(pv, string_types):
                self.pvsp = [pv]
            elif isinstance(pv, (tuple, list)):
                self.pvsp = [p for p in pv]
            #lim_h = [self._get_sp_lim_h(pvi) for pvi in self.pvsp]
            # None means not checked yet. (None, None) checked but no limit
            self.pvlim = [None for i in range(len(self.pvsp))]
            self.pvh = [None for i in range(len(self.pvsp))]
            self.golden = [None for i in self.pvsp]
        elif not isinstance(pv, (tuple, list)):
            while idx >= len(self.pvsp):
                self.pvsp.append(None)
                self.pvh.append(None)
                self.pvlim.append(None)
                self.golden.append(None)
            self.pvsp[idx] = pv
            self.pvlim[idx] = None
            self.pvh[idx] = None
            self.golden[idx] = None
        else:
            raise RuntimeError("invalid setpoint pv '%s' for position '%s'" %
                               (str(pv), str(idx)))

        # roll the buffer.
        self._sp1 = self.sp
        self.sp = []

    def _update_sp_lim_h(self, i, r = 1000):
        # get the EPICS ctrl_limit and stepsize. For floating point values,
        # the default step size is 1/1000 of the range. for integer value.
        # range (None, None) means checked, None alone means not checked yet.
        try:
            v = caget(self.pvsp[i], timeout=self.timeout, format=FORMAT_CTRL)
            if isinstance(v, str): return
            if v.ok:
                #self.pvlim[i] = (v.lower_ctrl_limit, v.upper_ctrl_limit)
                self.pvlim[i] = (
                    self._unit_conv(v.lower_ctrl_limit, None, None, 'setpoint'),
                    self._unit_conv(v.upper_ctrl_limit, None, None, 'setpoint'))
                if v.is_integer(): self.pvh[i] = 1
                else: self.pvh[i] = (self.pvlim[i][1] - self.pvlim[0])/r
        except:
            _logger.warn("error on reading PV limits {0}".format(self.pvsp[i]))

    def setReadbackMv(self, mv, idx=None):
        """ Set/replace the MV (model variable)"""

        if idx is None:
            if isinstance(mv, dict):
                self.mvrb = [mv]
            elif isinstance(mv, (tuple, list)):
                self.mvrb = [m for m in mv]
        elif not isinstance(mv, (tuple, list)):
            while idx >= len(self.mvrb):
                self.mvrb.append(None)
            self.mvrb[idx] = mv
        else:
            raise RuntimeError(f"invalid mv '{str(mv)}' for index '{idx}'")

    def setSetpointMv(self, mv, idx=None):
        """ Set/replace the MV (model variable)"""

        if idx is None:
            if isinstance(mv, dict):
                self.mvsp = [mv]
            elif isinstance(mv, (tuple, list)):
                self.mvsp = [m for m in mv]
        elif not isinstance(mv, (tuple, list)):
            while idx >= len(self.mvsp):
                self.mvsp.append(None)
            self.mvsp[idx] = mv
        else:
            raise RuntimeError(f"invalid mv '{str(mv)}' for index '{idx}'")


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

    def setBoundary(self, **kwargs):
        """
        set the boundary values for the setpoint PV.

        Parameters
        -------------
        low : int, float. the lower boundary value, default None
        high : int, float. the higher boundary value, default None
        r : float. divide the range to get the stepsize. default 1000.
        index : int. index in the PV list. default None
        pv : str. pv name. needed if pvsp is a list. default None

        Examples
        ---------
        >>> caa.setBoundary()
        >>> caa.setBoundary(low = 0)

        Notes
        ------
        when using *index*, the corresponding PV with that index should be set
        before.

        all PVs with same name will be updated if there are duplicates in
        setpoint pv list.

        The stepsize is set to (high-low)/r only when both low and high are
        provided or none is provide. When none of the low and high are
        provided and the values are int, the stepsize is set to 1. use
        :func:`setStepSize` to explicitly set the stepsize.

        seealso :func:`setStepSize`

        """
        if 'index' in kwargs: idx = [kwargs['index']]
        elif 'pv' in kwargs:
            idx = [self.pvsp.index(pv)]
        else:
            idx = range(len(self.pvsp))
        r = kwargs.get("r", 1000)
        low, hi = kwargs.get("low", None), kwargs.get("high", None)

        # update boundary if not yet
        for i in idx:
            if self.pvlim[i] is None:
                self._update_sp_lim_h(i, r)

    def appendReadback(self, pv):
        """append the pv as readback"""
        self.pvrb.append(pv)

    def appendSetpoint(self, pv):
        """append the pv as setpoint"""
        self.setSetpointPv(pv, len(self.pvsp))

    def removeReadback(self, pv):
        """remove the pv from readback"""
        self.pvrb.remove(pv)

    def removeSetpoint(self, pv):
        """remove the pv from setpoint"""
        i = self.pvsp.index(pv)
        self.pvsp.pop(i)
        self.pvlim.pop(i)
        self.pvh.pop(i)
        # the history needs to be changed....
        self._sp1 = self.sp
        self.sp = []

    def remove(self, pv):
        if pv in self.pvrb:
            self.removeReadback(pv)
        if pv in self.pvsp:
            self.removeSetpoint(pv)

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

    def _step_sp(self, n, unitsys, fact):
        if None in self.pvh:
            raise RuntimeError("stepsize is not defined for PV: {0}".format(
                    self.pvsp))

        rawval0 = caget(self.pvsp, timeout=self.timeout)
        rawval1 = [rawval0[i] + fact*h for i in enumerate(self.pvh)]
        return self.putSetpoint(rawval1, unitsys = None)

    def stepUp(self, n = 1, unitsys = None):
        """
        step up the setpoint value.
        """
        self._step_sp(n, unitsys, 1.0)

    def stepDown(self, n = 1, unitsys = None):
        """
        step down the setpoint value.
        """
        self._step_sp(n, unitsys, -1.0)

    def settable(self):
        """check if it can be set"""
        if self.opflags & _DISABLED: return False
        if self.opflags & _READONLY: return False

        if not self.pvsp: return False
        else: return True


class CaElement(AbstractElement):
    r"""Element with Channel Access ability.

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
        self.__dict__['_golden'] = {}  # the golden values for fields.
        self.__dict__['_pvtags'] = {}
        self.__dict__['_pvarchive'] = []
        self.__dict__['virtual'] = kwargs.get('virtual', 0)
        self.__dict__['trace'] = kwargs.get('trace', False)
        # the linked element, alias
        self.__dict__['alias'] = []

        # update all element properties
        super(CaElement, self).__init__(**kwargs)

    def __setstate__(self, data):
        for (name, value) in data.items():
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
            if att in self._field:
                decr = self._field[att]
                return decr.pvrb + decr.pvsp
            else:
                return []
        elif kwargs.get('handle', None):
            pvl = []
            if kwargs["handle"] == "setpoint":
                for fld,act in self._field.items():
                    pvl.extend(act.pvsp)
            elif kwargs["handle"] == "readback":
                for fld,act in self._field.items():
                    pvl.extend(act.pvrb)
            return pvl
        return []

    def _pv_tags(self, tags):
        """
        return pv list which has all the *tags*.
        """
        tagset = set(tags)
        return [pv for pv,ts in self._pvtags.items()
                   if tagset.issubset(ts) and ts]

    def _pv_fields(self, fields):
        """
        return pv list which has all fields in the input
        """
        fieldset = set(fields)
        ret = []
        for k,v in self._field.items():
            #print k, v
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

        seealso :class:`CaAction`
        """
        if len(kwargs) == 0:
            return list(self._pvtags)
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

    def mv(self, **kwargs):
        """"""
        if len(kwargs) == 0:
            return {} # TODO
        elif len(kwargs) == 1:
            return {} # TODO
        elif len(kwargs) == 2:
            handle = kwargs.get('handle', None)
            fd = kwargs.get('field', None)
            if fd not in self._field: return {}
            if handle == 'readback':
                return self._field[kwargs['field']].mvrb
            elif handle == 'setpoint':
                return self._field[kwargs['field']].mvsp
            else:
                return {}
        else: return {}


    def hasPv(self, pv, inalias = False):
        """check if this element has pv.

        inalias=True will also check its alias elements.

        If the alias (child) has its aliases (grand children), they are not
        checked. (no infinite loop)
        """
        if pv in self._pvtags: return True
        if inalias == True:
            for e in self.alias:
                #if e.hasPv(pv): return True
                if pv in e._pvtags: return True
        return False

    def appendStatusPv(self, pv, desc, order=True):
        """append (func, pv, description) to status"""
        decr = self._field['status']
        if not decr: self._field['status'] = CaAction(trace=self.trace)

        self._field['status'].appendReadback(pv)

    def addAliasField(self, newfld, fld):
        import copy
        self._field[newfld] = copy.deepcopy(self._field[fld])

    def status(self):
        """
        string representation of value, golden setpoint, range for each field.
        """
        ret = self.name
        if not list(self._field): return ret

        maxlen = max([len(att) for att in list(self._field)])
        head = '\n%%%ds: ' % (maxlen+2)
        for att in list(self._field):
            decr = self._field[att]
            if not decr: continue
            val = decr.getReadback()
            val1 = decr.getGolden()
            val2 = decr.boundary()
            ret = ret + head % att + str(val) + " (%s) " % str(val1) + " [%s]" % str(val2)
        return ret

    def __getattr__(self, att):
        # called after checking __dict__
        if att not in self._field:
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
        # Note: the quick way has wait=False
        if hasattr(super(CaElement, self), att):
            super(CaElement, self).__setattr__(att, val)
        elif att in self.__dict__['_field']:
            decr = self.__dict__['_field'][att]
            if not decr:
                raise AttributeError("field '%s' is not defined for '%s'" % (
                        att, self.name))
            if not decr.pvsp:
                raise ValueError("field '%s' in '%s' is not writable" % (
                        att, self.name))
            decr.putSetpoint(val, wait=False)
            # if _field_trig exists, trig it, do not wait
            decr_trig = self.__dict__['_field'].get(att + "_trig", None)
            if decr_trig:
                decr_trig.putSetpoint(1, wait=False)
        elif att in list(self.__dict__):
            self.__dict__[att] = val
        else:
            # new attribute for superclass
            super(CaElement, self).__setattr__(att, val)
            #raise AttributeError("Error")
        for e in self.alias: e.__setattr__(att, val)

    def _get_unitconv(self, field, handle):
        if field not in self._field: return {}
        if handle == "readback":
            return self._field[field].ucrb
        elif handle == "setpoint":
            return self._field[field].ucsp
        else:
            return {}

    def convertible(self, field, src, dst, handle = "readback"):
        """
        check the unit conversion is possible or not

        handle : ["readback"|"setpoint"|None]
            check readback, setpoint or all handle values.

        returns True or False. If no specified handle, returns False.
        """

        if field not in self._field: return False

        if src is None and dst is None: return True

        unitconv = self._get_unitconv(field, handle)

        if (src, dst) in unitconv: return True

        uc = unitconv.get((dst, src), None)
        if uc is not None and uc.invertible: return True
        return False

    def addUnitConversion(self, field, uc, src, dst, handle=None):
        """
        add unit conversion for field.

        handle : ["readback"|"setpoint"|None].
            None means for every named handles.
        """
        # src, dst is unit system name, e.g. None for raw, phy
        if handle is None or handle == "readback":
            _logger.info("add unit conv for handle={0}".format(handle))
            self._field[field].ucrb[(src, dst)] = uc
            if src is None: self._field[field].pvrbunit = uc.srcunit
            elif dst is None: self._field[field].pvrbunit = uc.dstunit
        if handle is None or handle == "setpoint":
            _logger.info("add unit conv for handle={0}".format(handle))
            self._field[field].ucsp[(src, dst)] = uc
            if src is None: self._field[field].pvspunit = uc.srcunit
            elif dst is None: self._field[field].pvspunit = uc.dstunit

    def addUnitConversionFuncs(self, field):
        """"""

        for uc, ucf in [(self._field[field].ucrb, self._field[field].ucfrb),
                        (self._field[field].ucsp, self._field[field].ucfsp)]:
            if uc == {}:
                # Add only the basic identity conversion from None to None
                ucf[(None, None)] = identity
                continue

            #uc = {(None, 'phy'): 1, ('phy', 'model'): 2, ('model', 'pyelegant'): 3}

            u_unitsys = set([s for src_dst_tup in list(uc) for s in src_dst_tup])
            for src in u_unitsys:
                for dst in u_unitsys:
                    k = (src, dst)
                    if src == dst:
                        ucf[k] = identity
                    elif (src, dst) in uc:
                        ucf[k] = uc[(src, dst)].eval
                    elif (dst, src) in uc:
                        ucf[k] = partial(uc[(dst, src)].eval, inv=True)
                    else:
                        # Search for composite unit conversions (e.g.,
                        # conversion from None to "phy", followed by
                        # conversion from "phy" to "model")
                        intermediate_sys_list = [
                            s for s in u_unitsys if s not in (src, dst)]
                        match_found = False
                        for n_comp in range(1, len(intermediate_sys_list)+1):
                            seq = []
                            for ini_src, fin_src in [(src, dst), (dst, src)]:
                                interm_src = ini_src
                                for interm_tup in permutations(
                                    intermediate_sys_list, n_comp):
                                    for interm_dst in interm_tup:
                                        if (interm_src, interm_dst) in uc:
                                            inv = False
                                            seq.append([(interm_src, interm_dst), inv])
                                        elif (interm_dst, interm_src) in uc:
                                            inv = True
                                            seq.append([(interm_dst, interm_src), inv])
                                        else:
                                            seq = []
                                            interm_src = ini_src
                                            break

                                        interm_src = interm_dst

                                    if seq != []:
                                        interm_dst = fin_src
                                        if (interm_src, interm_dst) in uc:
                                            inv = False
                                            seq.append([(interm_src, interm_dst), inv])
                                            match_found = True
                                        elif (interm_dst, interm_src) in uc:
                                            inv = True
                                            seq.append([(interm_dst, interm_src), inv])
                                            match_found = True
                                        else:
                                            seq = []
                                            interm_src = ini_src

                                    if match_found:
                                        break

                                if match_found:
                                    break

                            if match_found:
                                break

                        ucf[k] = partial(recursive_eval, uc, seq)


    def convertUnit(self, field, x, src, dst, handle = "readback"):
        """convert value x between units without setting hardware"""

        #uc = self._get_unitconv(field, handle)
        #return self._field[field]._unit_conv(x, src, dst, uc)
        return self._field[field]._unit_conv(x, src, dst, handle)


    def get_unit_systems(self, field, handle = "readback"):
        """get a list of all unit systems for field.

        None is the lower level unit, e.g. in EPICS channel. Use convertible
        to see if the conversion is possible between any two unit systems.

        """
        unitconv = self._get_unitconv(field, handle)
        if not unitconv: return [None]

        src, dst = zip(*(list(unitconv)))

        ret = set(src).union(set(dst))
        return list(ret)

    def getUnitSystems(self, field = None, handle = "readback"):
        """return a list of available unit systems for field.

        If no field specified, return a dictionary for all fields and their
        unit systems.

        None means the unit used in the lower level control system, e.g. EPICS.
        """
        if field is None:
            return dict([(f, self.get_unit_systems(f, handle)) for f \
                             in list(self._field)])
        else:
            return self.get_unit_systems(field, handle)

    def getUnit(self, field, unitsys='phy', handle = "readback"):
        """get the unit symbol of a unit system, e.g. unitsys='phy'

        The unit name, e.g. "T/m" for integrated quadrupole strength, is
        helpful for plotting routines.

        return '' if no such unit system. A tuple of all handles when *handle*
        is None
        """
        if field in list(self._field) and unitsys == None:
            if handle == "readback":
                return self._field[field].pvrbunit
            elif handle == "setpoint":
                return self._field[field].pvspunit
            else:
                return ""

        if unitsys == 'model':
            unitsys = engines.getEngineName()

        unitconv = self._get_unitconv(field, handle)
        for k,v in unitconv.items():
            if k[0] == unitsys: return v.srcunit
            elif k[1] == unitsys: return v.dstunit

        return ""

    def setUnit(self, field, u, unitsys = 'phy', handle = "readback"):
        """set the unit symbol for a unit system
        """
        if field not in list(self._field):
            raise RuntimeError("element '%s' has no '%s' field" % \
                                   self.name, field)

        if unitsys is None: self._field[field].pvunit = u

        for k,v in self._get_unitconv(field, handle).items():
            if k[0] == unitsys: v.srcunit = u
            elif k[1] == unitsys: v.dstunit = u

    def getEpsilon(self, field):
        return self._field[field].sprb_epsilon

    def setEpsilon(self, field, eps):
        self._field[field].sprb_epsilon = eps

    def updatePvRecord(self, pvname, properties, tags = []):
        """update the pv with property dictionary and tag list."""
        if not isinstance(pvname, string_types):
            raise TypeError("%s is not a valid type" % (type(pvname)))

        # update the properties
        if properties is not None:
            self.updateProperties(properties)


        # the default handle is 'readback'
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
                    self.setGetAction(pvname, fieldname, idx)
                elif elemhandle == 'setpoint':
                    self.setPutAction(pvname, fieldname, idx)
                else:
                    raise ValueError("invalid handle value '%s' for pv '%s'" %
                                     (elemhandle, pvname))
                if pvunit: self._field[fieldname].pvunit = pvunit
                _logger.debug("'%s' field '%s'[%s] = '%s'" % (
                        elemhandle, fieldname, idx, pvname))
                if "epsilon" in properties:
                    self.setEpsilon(fieldname, properties["epsilon"])

        # check element field
        #for t in tags:
        #    g = re.match(r'aphla.elemfield.([\w\d]+)(\[\d+\])?', t)
        #    if g is None: continue
        #
        #    fieldname, idx = g.group(1), g.group(2)
        #    if idx is not None:
        #        idx = int(idx[1:-1])
        #        _logger.info("%s %s[%d]" % (pvname, fieldname, idx))

        # update the (pv, tags) dictionary
        if pvname in list(self._pvtags): self._pvtags[pvname].update(tags)
        else: self._pvtags[pvname] = set(tags)

    def updateMvRecord(self, mv, properties, update_prop=False):
        """"""

        # update the properties
        if (properties is not None) and update_prop:
            self.updateProperties(properties)

        if properties is not None:
            elemhandle = properties.get('handle', 'readback')
            fieldfname = properties.get('field', None)
            if fieldfname is not None:
                g = re.match(r'([\w\d]+)(\[\d+\])?', fieldfname)
                if g is None:
                    raise ValueError("invalid field '%s'" % fieldfname)
                fieldname, idx = g.group(1), g.group(2)
                if idx is not None: idx = int(idx[1:-1])

                if fieldname not in self._field:
                    self._field[fieldname] = CaAction(trace=self.trace)

                if elemhandle == 'readback':
                    self._field[fieldname].setReadbackMv(mv, idx)
                elif elemhandle == 'setpoint':
                    self._field[fieldname].setSetpointMv(mv, idx)
                else:
                    raise ValueError(
                        f"invalid handle value '{elemhandle}' for mv '{str(mv)}'")

    def setGetAction(self, v, field, idx = None, desc = '', vtype='pv'):
        """set the action when reading *field*.

        the previous action will be replaced if it was defined.
        *v* is single PV or a list/tuple
        """
        if field not in self._field:
            self._field[field] = CaAction(trace=self.trace)

        if vtype == 'pv':
            self._field[field].setReadbackPv(v, idx)
        elif vtype == 'mv':
            self._field[field].setReadbackMv(v, idx)
        else:
            raise ValueError(f'Unexpected "vtype": {vtype}')

    def setPutAction(self, v, field, idx=None, desc = '', vtype='pv'):
        """set the action for writing *field*.

        the previous action will be replaced if it was define.
        *v* is a single PV or a list/tuple
        """
        if field not in self._field:
            self._field[field] = CaAction(trace=self.trace)

        if vtype == 'pv':
            self._field[field].setSetpointPv(v, idx)
        elif vtype == 'mv':
            self._field[field].setSetpointMv(v, idx)
        else:
            raise ValueError(f'Unexpected "vtype": {vtype}')

    def fields(self):
        """return element's fields, sorted."""
        return sorted(self._field)

    def stepSize(self, field):
        """return the stepsize of field (hardware unit)"""
        return self._field[field].stepSize()

    def updateBoundary(self, field = None, lowhi = None, r = None):
        """update the boundary for field

        - *field*
        - *lowhi*, tuple for low and high boundary. e.g. (0, 1)
        - *r*, int. Divide the range (hi-low) by r to get the stepsize.

        Examples
        ---------
        >>> updateBoundary('b1', (0, 2), 10)

        The above example sets 'b1' range to (0, 2) and stepsize 0.2

        If this field has been set once, its boundary has been updated at the
        first time putting a value to it. Since putting a value needs to know
        the boundary and check if the value is inside.
        """
        if field is None: fields = list(self._field)
        else: fields = [field]

        kw = {}
        if lowhi is not None:
            kw['low'] = lowhi[0]
            kw['high'] = lowhi[1]

        if r is not None: kw['r'] = r
        for fld in fields:
            self._field[fld].setBoundary(**kw)

    def boundary(self, field = None):
        """return the (low, high) range of *field* or all fields (raw unit)"""
        if field is not None:
            return self._field[field].boundary()
        else:
            return dict([(fld, act.boundary())
                         for fld,act in self._field.items()])

    def collect(self, elemlist, **kwargs):
        """
        collect properties in elemlist as its own.

        - *fields*, EPICS related
        - *attrs*, element attribute list
        """

        fields = kwargs.get("fields", [])
        attrs  = kwargs.get("attrs", [])
        for field in fields:
            pd = CaAction(trace=self.trace)
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
        return dir(CaElement) + list(self.__dict__) + list(self._field)

    def __repr__(self):
        if self.virtual:
            return "%s [%s] (virtual)" % (self.name, self.family)
        else:
            return AbstractElement.__repr__(self)

    def enableTrace(self, fieldname):
        if not self._field[fieldname].trace:
            self._field[fieldname].trace = True
            self._field[fieldname].sp = []
            self._field[fieldname].mark('setpoint')

    def disableTrace(self, fieldname):
        if self._field[fieldname].trace:
            self._field[fieldname].trace = False
            self._field[fieldname].sp = []

    def disableField(self, fieldname):
        self._field[fieldname].opflags |= _DISABLED

    def enableField(self, fieldname):
        self._field[fieldname].opflags &= ~_DISABLED

    def setFieldReadonly(self, fieldname):
        self._field[fieldname].opflags |= _READONLY

    def resetFieldReadonly(self, fieldname):
        self._field[fieldname].opflags &= ~_READONLY

    def revert(self, fieldname):
        """undo the field value to its previous one"""
        self._field[fieldname].revert()
        for e in self.alias: e._field[fieldname].revert()

    def mark(self, fieldname, handle = 'setpoint'):
        self._field[fieldname].mark(handle)
        for e in self.alias: e._field[fieldname].mark(handle)

    def reset(self, fieldname, data='golden'):
        """data='golden' or 'origin'. see CaAction::reset()"""
        self._field[fieldname].reset(data)
        for e in self.alias: e._field[fieldname].reset(data)

    def _get_field(self, field, **kwargs):
        """
        read value of a single field, raise RuntimeError if no such field.
        """
        handle = kwargs.get('handle', 'readback').lower()
        unitsys = kwargs.get('unitsys', None)

        if field not in self._field:
            raise RuntimeError("field {0} is not defined for {1}".format(field, self.name))
        elif handle == 'readback':
            v = self._field[field].getReadback(unitsys)
        elif handle == 'setpoint':
            v = self._field[field].getSetpoint(unitsys)
        elif handle == 'golden':
            v = self._field[field].getGolden(unitsys)
        else:
            raise ValueError("unknow handle {0}" % field)

        # convert unit when required
        return v

    def get(self, fields, handle='readback', unitsys='phy'):
        """get the values for given fields. None if not exists.

        Parameters
        -------------
        fields : str, list. field
        handle : str. 'readback', 'setpoint' or 'golden'.
        unitsys : the unit system. None for lower level unit.

        Example
        -----------
        >>> get('x')
        >>> get(['x', 'y'])
        >>> get(['x', 'unknown'])
          [ 0, None]

        """

        kw = {'handle': handle, 'unitsys': unitsys}
        if isinstance(fields, string_types):
            return self._get_field(fields, **kw)
        else:
            # a list of fields
            return [ self._get_field(v, **kw) for v in fields]

    def _put_field(self, field, val, unitsys, **kwargs):
        """set *val* to *field*. handle='golden' will set value as golden.

        seealso :func:`pv(field=field)`
        """

        att = field
        if att not in self.__dict__['_field']:
            raise RuntimeError("field '%s' is not defined for '%s'" % (
                    att, self.name))

        decr = self.__dict__['_field'][att]
        if not decr:
            raise AttributeError("field '%s' is not defined for '%s'" % (
                    att, self.name))

        if OP_MODE.value == OperationMode.ONLINE:
            _vsp = decr.pvsp
        elif OP_MODE.value == OperationMode.SIMULATION:
            _vsp = decr.mvsp
        else:
            raise ValueError(f'Unexpected operation mode value : {OP_MODE.value}')
        if not _vsp:
            raise ValueError(f"field '{att}' in '{self.name}' is not writable")

        bc = kwargs.get('bc', 'exception')
        wait = kwargs.get("wait", True)
        timeout = kwargs.get("timeout", 5)
        decr.putSetpoint(val, unitsys, bc=bc, wait=wait, timeout=timeout)


    def put(self, field, val, **kwargs):
        """set *val* to *field*.

        Parameters
        ==========
        field : str. Element field
        val : float, int. The new value
        unitsys : str. Unit system
        bc : str. Bounds checking: "exception" will raise a ValueError.
            "ignore" will abort the whole setting. "boundary" will use the
            boundary value it is crossing.
        wait : as in caput
        timeout :
        seealso :func:`pv(field=field)`
        """
        unitsys = kwargs.get("unitsys", 'phy')
        bc = kwargs.get("bc", 'exception')
        wait = kwargs.get("wait", True)
        trig = kwargs.get("trig", None)
        timeout = kwargs.get("timeout", 5)

        self._put_field(field, val, timeout=timeout, unitsys=unitsys, bc=bc, wait=wait)
        for e in self.alias:
            e._put_field(field, val, timeout=timeout, unitsys=unitsys, bc=bc, wait=wait)

        trig_fld = field + "_trig"
        if trig_fld in self.fields() and trig is not None:
            self._put_field(field + "_trig", trig,
                            unitsys=None, timeout=timeout, wait=True)

    def setGolden(self, field, val, unitsys = 'phy'):
        """set the golden value for field"""
        try:
            self._field[field].setGolden(val, unitsys)
        except:
            print("errors in setting golden for {0}.{1}".format(self.name, field))
            raise

    def settable(self, field):
        """check if the field can be changed. not disabled, nor readonly."""
        if field not in list(self._field): return False
        if self._field[field].opflags & _DISABLED: return False
        if self._field[field].opflags & _READONLY: return False

        return self._field[field].settable()

    def readable(self, field):
        """check if the field readable (not disabled)."""
        if field not in list(self._field): return False
        if self._field[field].opflags & _DISABLED: return False
        return True


def merge(elems, field = None, **kwargs):
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

    # count 'field' owners and its rb,wb PVs.
    count, pvdict, mvdict = {}, {}, {}
    for e in elems:
        fds = e.fields()
        for f in fds:
            if f in count: count[f] += 1
            else: count[f] = 1

            pvrb = e.pv(field=f, handle='readback')
            pvsp = e.pv(field=f, handle='setpoint')
            if f not in pvdict: pvdict[f] = [[], []]
            pvdict[f][0].extend(pvrb)
            pvdict[f][1].extend(pvsp)

            mvrb = e.mv(field=f, handle='readback')
            mvsp = e.mv(field=f, handle='setpoint')
            if f not in mvdict: mvdict[f] = [[], []]
            mvdict[f][0].extend(mvrb)
            mvdict[f][1].extend(mvsp)

    elem = CaElement(**kwargs)
    #print "merged:", elem
    # consider only the common fields
    if field is None:
        for k,v in count.items():
            if v < len(elems):
                _logger.warn("field '%s' has %d < %d" % (k, v, len(elems)))
                pvdict.pop(k)
                mvdict.pop(k)
        #print list(pvdict)
        for fld, pvs in pvdict.items():
            if len(pvs[0]) > 0: elem.setGetAction(pvs[0], fld, None, '')
            if len(pvs[1]) > 0: elem.setPutAction(pvs[1], fld, None, '')
        for fld, mvs in mvdict.items():
            if len(mvs[0]) > 0: elem.setGetAction(mvs[0], fld, None, '', vtype='mv')
            if len(mvs[1]) > 0: elem.setPutAction(mvs[1], fld, None, '', vtype='mv')
        elem.sb = [e.sb for e in elems]
        elem.se = [e.se for e in elems]
        elem._name = [e.name for e in elems]
    elif field in pvdict:
        pvrb, pvsp = pvdict[field][0], pvdict[field][1]
        if len(pvrb) > 0: elem.setGetAction(pvrb, field, None, '')
        if len(pvsp) > 0: elem.setPutAction(pvsp, field, None, '')
        if field in mvdict:
            mvrb, mvsp = mvdict[field][0], mvdict[field][1]
            if len(mvrb) > 0: elem.setGetAction(mvrb, field, None, '', vtype='mv')
            if len(mvsp) > 0: elem.setPutAction(mvsp, field, None, '', vtype='mv')

        # count the element who has the field
        elemgrp = [e for e in elems if field in e.fields()]
        elem.sb = [e.sb for e in elemgrp]
        elem.se = [e.se for e in elemgrp]
        elem._name = [e.name for e in elemgrp]
        #print pvsp
    else:
        _logger.warn("no pv merged for {0}".format([
                    e.name for e in elems]))
    # if all raw units are the same, so are the merged element
    for fld in elem.fields():
        unique_units = set([e.getUnit(fld, unitsys=None) for e in elems if fld in e.fields()])
        if len(unique_units) == 1:
            elem.setUnit(fld, unique_units.pop(), unitsys=None)

    return elem

