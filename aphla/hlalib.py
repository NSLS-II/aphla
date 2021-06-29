from __future__ import print_function, division, absolute_import
from six import string_types
from six.moves import reduce

"""
Core APHLA Libraries
---------------------

Defines the fundamental routines.
"""

# :author: Lingyun Yang

import logging
import time
import os
import re
from fnmatch import fnmatch
from datetime import datetime
from functools import lru_cache

import numpy as np

from .catools import caget, caput, CA_OFFLINE, savePvData, caWait, caWaitStable
from . import machines
from . import models
from . import element
import itertools

from . import CONFIG
from . import ureg, Q_
from . import facility_d
from .defaults import Default, set_defaults, getDynamicDefault

_logger = logging.getLogger("aphla.hlalib")

#__all__ = [
#    'addGroup', 'addGroupMembers', 'eget',
#    'getBeamlineProfile', 'getBeta',
#    'getBpms', 'getChromaticityRm', 'getChromaticity', 'getClosest',
#    'getCurrent', 'getCurrentMode', 'getDispersion', 'getDistance',
#    'getElements', 'getEta', 'getFastOrbit', 'getFftTune',
#    'getGroupMembers', 'getGroups', 'getLocations', 'getModes',
#    'getNeighbors', 'getOrbit', 'getPhase', 'getPvList', 'getRfFrequency',
#    'getRfVoltage', 'getStepSize', 'getTbtOrbit', 'getTuneRm',
#    'getTune', 'getTunes',
#    'removeGroup', 'removeGroupMembers', 'putRfFrequency',
#    'stepRfFrequency',
#    'waitStableOrbit',
#]

def getTimestamp(t = None, us = True):
    """
    generate the timestamp string

    t - user provided datetime object or new a datetime.now()
    us - with microsecond or not.
    """
    fmt = "%Y-%m-%d_%H:%M:%S"
    if us: fmt = fmt + ".%f"
    if t is None:
        t = datetime.now()

    return t.strftime(fmt)

def setEnergy(E_MeV):
    """set energy (MeV) for current submachine

    see also :func:`setEnergy`
    """

    if not CONFIG['unitless_quantities']:
        if not isinstance(E_MeV, Q_):
            raise TypeError('Pint Quantity object is expected as the argument.')
        machines._lat.E_MeV = E_MeV.to('MeV').magnitude
    else:
        machines._lat.E_MeV = E_MeV

def getEnergy():
    """get current submachine beam energy (MeV)

    see also :func:`setEnergy`
    """

    if not CONFIG['unitless_quantities']:
        return Q_(machines._lat.E_MeV, 'MeV')
    else:
        return machines._lat.E_MeV

def getEnergyUnit():
    """"""

    if not CONFIG['unitless_quantities']:
        print('WARNING: A Pint Quantity object is being returned by getEnergy().')
        print('Hence, the unit string returned by this function getEnergyUnit()')
        print('is meaningless.')

    return 'MeV'

def getOutputDir():
    """get the output data dir for the current lattice"""
    return machines._lat.OUTPUT_DIR

# current
def getCurrent(name='dcct', field='I', unitsys=None):
    """Get the current from the first DCCT element

    :param str name: the name of DCCT, default 'dcct'
    :param str field: the field of DCCT, default 'I'
    :param unit: the desired unit sytem, default None, no conversion.

    returns None if no 'dcct' element found
    """
    _current = getElements(name)
    if _current: return _current[0].get(field, unitsys=unitsys)
    else: return None

# current lifetime
def getLifetime(name='dcct', field='tau', unitsys=None):
    """Get the lifetime from the first DCCT element

    :param str name: the name of DCCT, default 'dcct'
    :param str field: the field of DCCT, default 'tau'
    :param unit: the desired unit sytem, default None, no conversion.

    returns None if no 'dcct' element found
    """
    _current = getElements(name)
    if _current: return _current[0].get(field, unitsys=unitsys)
    else: return None

# lifetime and current
def getLifetimeCurrent(name='dcct', unitsys=None):
    """Get the beam lifetime and current from the first DCCT element

    :param str name: the name of DCCT, default 'dcct'
    :param unit: the desired unit sytem, default None, no conversion.

    returns (None, None) if no 'dcct' element found
    """
    _current = getElements(name)
    if not _current:
        return None, None
    I   = _current[0].get("I",   unitsys=unitsys)
    tau = _current[0].get("tau", unitsys=unitsys)
    return tau, I

@set_defaults('aphla.getRfFrequencyUnit')
def getRfFrequencyUnit(
    name=Default('name', 'rfcavity'),
    field=Default('field', 'f'),
    handle=Default('handle', 'readback'),
    **kwargs,
):
    """
    Return the unit strings for the output of getRfFrequency()
    """

    if not CONFIG['unitless_quantities']:
        print('WARNING: A Pint Quantity object is being returned by getRfFrequency().')
        print('Hence, the unit strings returned by this function getRfFrequencyUnit()')
        print('are meaningless.')

    unitsys = kwargs.get('unitsys', getDynamicDefault('unitsys', None))

    _rf = getElements(name)
    if _rf:
        return _rf[0].getUnit(field, unitsys=unitsys, handle=handle)
    else:
        return None


@set_defaults('aphla.getRfFrequency')
def getRfFrequency(
    name=Default('name', 'rfcavity'),
    field=Default('field', 'f'),
    handle=Default('handle', 'readback'),
    **kwargs,
):
    """
    Get the frequency from the first 'RFCAVITY' element.

    seealso :func:`eget`, :func:`getRfVoltage`, :func:`putRfFrequency`
    """

    unitsys = kwargs.get('unitsys', getDynamicDefault('unitsys', None))

    _rf = getElements(name)
    if _rf:
        return _rf[0].get(field, unitsys=unitsys, handle=handle)
    else:
        return None


@set_defaults('aphla.putRfFrequencyUnit')
def putRfFrequencyUnit(
    name=Default('name', 'rfcavity'),
    field=Default('field', 'f'),
    **kwargs,
):
    """
    Return the unit strings for the input frequency of putRfFrequency()
    """

    if not CONFIG['unitless_quantities']:
        print('WARNING: A Pint Quantity object should be passed to putRfFrequency().')
        print('Hence, the unit strings returned by this function putRfFrequencyUnit()')
        print('are meaningless.')

    unitsys = kwargs.get('unitsys', getDynamicDefault('unitsys', None))

    _rf = getElements(name)
    if _rf:
        return _rf[0].getUnit(field, unitsys=unitsys, handle='setpoint')
    else:
        raise RuntimeError(f"element '{name}' not found")


@set_defaults('aphla.putRfFrequency')
def putRfFrequency(
    f,
    name=Default('name', 'rfcavity'),
    field=Default('field', 'f'),
    **kwargs,
):
    """set the rf frequency for the first 'RFCAVITY' element"""

    unitsys = kwargs.get('unitsys', getDynamicDefault('unitsys', None))

    _rf = getElements(name)
    if _rf:
        return _rf[0].put(field, f, unitsys=unitsys)
    else:
        raise RuntimeError(f"element '{name}' not found")


def getRfVoltage(name = 'rfcavity', field='v', unitsys=None):
    """
    Get the voltage of the first 'RFCAVITY' element

    :param str name: cavity name
    :param str field: field name for voltage, default 'v'
    :param str unit: unit system

    return None if no element found
    """
    _rf = getElements(name)
    if _rf: return _rf[0].get(field, unitsys=unitsys)
    else: return None

def stepRfFrequency(df = 0.010):
    """
    change one step of the first 'RFCAVITY' element

    seealso :func:`getRfFrequency`, :func:`putRfFrequency`

    .. warning::

      Need check the unit for real machine
    """
    f0 = getRfFrequency()
    putRfFrequency(f0 + df)


@set_defaults('aphla.rampRfFrequency')
def rampRfFrequency(
    target_freq,
    name=Default('name', 'rfcavity'),
    field=Default('field', 'f'),
    get_handle=Default('get_handle', 'readback'),
    tol_freq=Default('tol_freq', Q_(1e-3, 'Hz')),
    max_step_freq=Default('max_step_freq', None),
    step_wait=Default('step_wait', Q_(1.0, 's')),
    max_wait=Default('max_wait', Q_(5.0, 'min')),
    **kwargs,
):
    """Ramp up or down the main RF frequency

    Ramp up or down the main RF frequency to `target_freq` with multiple steps
    while satisfying a facility-specific limit for one-step as well as total
    frequncy change.

    Parameters
    ----------
    target_freq : float ([Hz] in unitless & units mode) or Pint Quantity \
            object (in units mode)
        The final frequency you want to set.

    name : str, default='rfcavity' (facility dependent)
        The name of the RF cavity element.

    field : str, default='f' (facility dependent)
        The name of the "frequency" field for the RF cavity element.

    get_handle : {'readback', 'setpoint'}, default='readback' (facility dependent)
        The handle from which the current frequency "f0" will be defined.
        The frequency steps will be determined by "f0" and `target_freq`. There
        may be situations where the readback and setpoint are very far apart.
        In these cases, using "readback" should avoid unnecessarily large initial
        step, as long the readback is reliable. If the readback is not to be
        trusted, then "setpoint" can be used for "f0".

    tol_freq : float ([Hz] in unitless & units mode) or Pint Quantity object \
            (in units mode), default=1e-3 [Hz] (facility dependent)
        Tolerance for discrepancy between the setpoint and readback frequency
        values. This value is used to determine whether the frequency has started
        moving and whether the target frequency has been reached.

    max_step_freq : float ([Hz] in unitless & units mode) or Pint Quantity \
            object (in units mode), default=None (facility dependent)
        Maximum size for each frequency step change. If None, and (a) if a
        facility-specific limit exists (output of `machines.getControlLimits()`),
        that limit will be used; (b) if no such limit exists, the frequncy change
        will be done in a single step. If the value specified by this argument
        is larger than the facility-specific limit, if any, the limit overrides
        the user-specified step size.

    step_wait : float ([s] in unitless & units mode) or Pint Quantity object \
            (in units mode), default=1.0 [s] (facility dependent)
        Time to wait between each frequncy step change.

    max_wait : float ([s] in unitless & units mode) or Pint Quantity object \
            (in units mode), default=5.0 [min] (facility dependent)
        This function terminates itself if the frequency does not reach
        the target within this amount of time.

    Other Parameters
    ----------------

    freq_motion_max_num_trials : int, default=3 (facility dependent)
        This function checks whether the "put" action actually worked or not at
        each step by monitoring the frequency readback has changed more than
        `tol_freq`. This check is performed initially `freq_motion_init_check_wait`
        seconds after the first "put". If the frequency has not started moving
        yet, it will apply another "put", then wait for `freq_motion_check_wait`
        seoncds and check again, until it detects frequency motion, up to
        `freq_motion_max_num_trials` times. If it fails to detect motion after
        the maximum number of trials, it raise RuntimeError.

    freq_motion_init_check_wait : float ([s] in unitless & units mode) or Pint \
            Quantity object (in units mode), default=1.0 [s] (facility dependent)
        See explanation for `freq_motion_max_num_trials`.

    freq_motion_check_wait : float ([s] in unitless & units mode) or Pint \
            Quantity object (in units mode), default=3.0 [s] (facility dependent)
        See explanation for `freq_motion_max_num_trials`

    freq_target_check_wait : float ([s] in unitless & units mode) or Pint \
            Quantity object (in units mode), default=1.0 [s] (facility dependent)
        It will check every "freq_target_check_wait" second to see if the target
        frequency has been reached after frequency motion is confirmed.

    Notes
    -----
    In the unitless mode, for all the input arguments with units specified,
    users must provide either (a) pure numerical values exactly in the specified
    units or (b) Pint Quantity objects with the corresponding dimensions. In the
    units mode, users must provide Pint Quantity objects.
    """

    freq_motion_max_num_trials = kwargs.get(
        'freq_motion_max_num_trials', getDynamicDefault('freq_motion_max_num_trials', 3)
    )
    freq_motion_init_check_wait = kwargs.get(
        'freq_motion_init_check_wait',
        getDynamicDefault('freq_motion_init_check_wait', Q_(1.0, 's')),
    )
    freq_motion_check_wait = kwargs.get(
        'freq_motion_check_wait',
        getDynamicDefault('freq_motion_check_wait', Q_(3.0, 's')),
    )
    freq_target_check_wait = kwargs.get(
        'freq_target_check_wait',
        getDynamicDefault('freq_target_check_wait', Q_(1.0, 's')),
    )

    if not CONFIG['unitless_quantities']:
        _kwargs_put_freq = dict(name=name, field=field)
        _kwargs_get_freq = dict(name=name, field=field, handle=get_handle)
        _kwargs_get_readback_freq = dict(name=name, field=field, handle='readback')
        init_freq = getRfFrequency(**_kwargs_get_freq)
    else:
        if not isinstance(target_freq, Q_):
            target_freq = Q_(target_freq, 'Hz')
        if not isinstance(tol_freq, Q_):
            tol_freq = Q_(tol_freq, 'Hz')
        if (max_step_freq is not None) and (not isinstance(max_step_freq, Q_)):
            max_step_freq = Q_(max_step_freq, 'Hz')
        if not isinstance(step_wait, Q_):
            step_wait = Q_(step_wait, 's')
        if not isinstance(max_wait, Q_):
            max_wait = Q_(max_wait, 's')

        if not isinstance(freq_motion_init_check_wait, Q_):
            freq_motion_init_check_wait = Q_(freq_motion_init_check_wait, 's')
        if not isinstance(freq_motion_check_wait, Q_):
            freq_motion_check_wait = Q_(freq_motion_check_wait, 's')
        if not isinstance(freq_target_check_wait, Q_):
            freq_target_check_wait = Q_(freq_target_check_wait, 's')

        unitsys = kwargs.get('unitsys', getDynamicDefault('unitsys'))

        _kwargs_put_freq = dict(name=name, field=field, unitsys=unitsys)
        _kwargs_get_freq = dict(
            name=name, field=field, handle=get_handle, unitsys=unitsys
        )
        _kwargs_get_setpoint_freq = dict(
            name=name, field=field, handle='setpoint', unitsys=unitsys
        )
        _kwargs_get_readback_freq = dict(
            name=name, field=field, handle='readback', unitsys=unitsys
        )
        init_freq = getRfFrequency(**_kwargs_get_freq)

        unit_str = {}
        for k, func, _kwargs in [
            ('get', getRfFrequencyUnit, _kwargs_get_freq),
            ('get_setpoint', getRfFrequencyUnit, _kwargs_get_setpoint_freq),
            ('get_readback', getRfFrequencyUnit, _kwargs_get_readback_freq),
            ('put', putRfFrequencyUnit, _kwargs_put_freq),
        ]:
            unit_str[k] = func(**_kwargs)

        init_freq = Q_(init_freq, unit_str['get'])
    print(f'Initial RF Frequency = {init_freq.to("Hz"):,.3f~P}')

    dfreq = target_freq - init_freq

    # Check if requested freq change is too small
    if dfreq <= tol_freq:
        msg = (
            f'Requested frequency change ({dfreq.to("Hz"):,.3f~P}) smaller than '
            f'the "tol_freq" ({tol_freq.to("Hz"):,.3f~P})'
        )
        raise ValueError(msg)

    lim = machines.getControlLimits()

    # If specified, check the total frequency change is within the facility-
    # speicific limit.
    try:
        max_total_freq = lim['rf_freq']['change']['max_total'].to('Hz')
    except KeyError:
        print(
            'Facility-specific limit NOT found for max total change for RF Frequency.'
        )
        print('So, no check for this limit is performed.')
        max_total_freq = None

    if max_total_freq is not None:
        if abs(dfreq) > max_total_freq:
            msg = (
                f'Requested total frequency change ({dfreq.to("Hz"):,.3f~P}) '
                f'larger than the limit ({max_total_freq.to("Hz"):,.3f~P})'
            )
            raise ValueError(msg)
        else:
            msg = (
                f'Requested total frequency change ({dfreq.to("Hz"):,.3f~P}) '
                f'within the limit ({max_total_freq.to("Hz"):,.3f~P})'
            )
            print(msg)

    # Limit the frequency step size to the facility-speicific limit, if specified.
    try:
        max_step_freq_limit = lim['rf_freq']['change']['max_step'].to('Hz')
    except KeyError:
        max_step_freq_limit = None

    if max_step_freq is None:
        if max_step_freq_limit is None:
            print(
                'Facility-specific limit NOT found for max step change for RF frequency.'
            )
            nSteps = 1
        else:
            print(
                (
                    f'Using facility-specific limit for max step change for RF '
                    f'frequency: {max_step_freq_limit.to("Hz"):,.3f~P}.'
                )
            )
            nSteps = int(np.ceil(abs(dfreq) / max_step_freq_limit))
    else:
        if max_step_freq_limit is None:
            print(
                'Facility-specific limit NOT found for max step change for RF frequency.'
            )
            print('So, no check for this limit is performed.')
        else:
            if max_step_freq > max_step_freq_limit:
                print(
                    (
                        f'User-specified frequency step size '
                        f'({max_step_freq.to("Hz"):,.3f~P}) exceeds the facility'
                        f'-specific limit ({max_step_freq_limit.to("Hz"):,.3f~P}).'
                    )
                )
                max_step_freq = max_step_freq_limit
        print((f'Using step size for RF frequency: {max_step_freq.to("Hz"):,.3f~P}.'))
        nSteps = int(np.ceil(abs(dfreq) / max_step_freq))

    print(f'Frequency will be changed in {nSteps:d} step(s).')

    if isinstance(step_wait, Q_):
        step_wait_m = step_wait.to('s').magnitude

    print('Ramping RF frequency...')

    t0 = time.perf_counter()

    for iStep in range(nSteps):
        curr_freq = getRfFrequency(**_kwargs_get_readback_freq)
        if CONFIG['unitless_quantities']:
            curr_freq = Q_(curr_freq, unit_str['get_readback'])

        new_freq = init_freq + (iStep + 1) * dfreq / nSteps
        if CONFIG['unitless_quantities']:
            new_freq_m = new_freq.to(unit_str['put']).magnitude

        if not CONFIG['unitless_quantities']:
            putRfFrequency(new_freq, _kwargs_put_freq)
        else:
            putRfFrequency(new_freq_m, _kwargs_put_freq)

        time.sleep(freq_motion_init_check_wait.to('s').magnitude)

        if not CONFIG['unitless_quantities']:

            # Check whether the frequency readback has started moving. If not,
            # try to "put" the target frequency again.
            counter = 0
            while (
                abs(getRfFrequency(**_kwargs_get_readback_freq) - curr_freq) <= tol_freq
            ):
                if counter >= freq_motion_max_num_trials:
                    raise RuntimeError('Frequency could not be changed.')
                putRfFrequency(new_freq, _kwargs_put_freq)
                counter += 1
                time.sleep(freq_motion_check_wait.to('s').magnitude)

            # Once the frequency motion is confirmed, wait until the frequency
            # readback reaches the target within the tolerance.
            while (
                abs(getRfFrequency(**_kwargs_get_readback_freq) - new_freq) > tol_freq
            ):
                if time.perf_counter() - t0 > max_wait:
                    raise TimeoutError(
                        f'Exceeded max time allowed to ramp RF frequency'
                    )
                time.sleep(freq_target_check_wait.to('s').magnitude)

        else:
            # Check whether the frequency readback has started moving. If not,
            # try to "put" the target frequency again.
            counter = 0
            while (
                abs(
                    Q_(
                        getRfFrequency(**_kwargs_get_readback_freq),
                        unit_str['get_readback'],
                    )
                    - curr_freq
                )
                <= tol_freq
            ):
                if counter >= freq_motion_max_num_trials:
                    raise RuntimeError('Frequency could not be changed.')
                putRfFrequency(new_freq_m, _kwargs_put_freq)
                counter += 1
                time.sleep(freq_motion_check_wait.to('s').magnitude)

            # Once the frequency motion is confirmed, wait until the frequency
            # readback reaches the target within the tolerance.
            while (
                abs(
                    Q_(
                        getRfFrequency(**_kwargs_get_readback_freq),
                        unit_str['get_readback'],
                    )
                    - new_freq
                )
                > tol_freq
            ):
                if time.perf_counter() - t0 > max_wait:
                    raise TimeoutError(
                        f'Exceeded max time allowed to ramp RF frequency'
                    )
                time.sleep(freq_target_check_wait.to('s').magnitude)

        if iStep != nSteps - 1:
            time.sleep(step_wait_m)

    setpoint = getRfFrequency(**_kwargs_get_setpoint_freq)
    readback = getRfFrequency(**_kwargs_get_readback_freq)
    if CONFIG['unitless_quantities']:
        setpoint = Q_(setpoint, unit_str['get_setpoint'])
        readback = Q_(readback, unit_str['get_readback'])

    print(
        (
            f'* Final RF Frequency: setpoint = {setpoint.to("Hz"):,.3f~P}; '
            f'readback = {readback.to("Hz"):,.3f~P})'
        )
    )


def _reset_trims(verbose=False):
    """reset all trims in group *HCOR* and *VCOR* """
    trimx = machines._lat.getGroupMembers(['*', 'HCOR'], op='intersection')
    trimy = machines._lat.getGroupMembers(['*', 'VCOR'], op='intersection')
    pv = []
    for e in trimx:
        pv.extend(e.pv(field='x', handle='setpoint'))
    for e in trimy:
        pv.extend(e.pv(field='y', handle='setpoint'))
    if not pv:
        raise ValueError("no pv for trims found")

    if verbose:
        for p in pv:
            print((p, caget(p),))
            caput(p, 0.0, wait=True)
            print(caget(p))
    else:
        caput(pv, 0.0)

    _logger.info("reset all trims")
    #print "DONE"


def _levenshtein_distance(first, second):
    """Find the Levenshtein distance between two strings."""
    if len(first) > len(second):
        first, second = second, first
    if len(second) == 0:
        return len(first)
    first_length = len(first) + 1
    second_length = len(second) + 1
    distance_matrix = np.zeros((first_length, second_length), 'd')
    for i in range(first_length):
        distance_matrix[i, 0] = i
    for j in range(second_length):
        distance_matrix[0, j]=j
    for i in xrange(1, first_length):
        for j in range(1, second_length):
            deletion = distance_matrix[i-1, j] + 1
            insertion = distance_matrix[i, j-1] + 1
            substitution = distance_matrix[i-1, j-1]
            if first[i-1] != second[j-1]:
                substitution += 1
            distance_matrix[i, j] = min(insertion, deletion, substitution)
    return distance_matrix[first_length-1, second_length-1]


def getElements(group, include_virtual=False):
    """searching for elements.

    this calls :func:`~aphla.lattice.Lattice.getElementList` of the current
    lattice.

    The default does not include virtual element.

    Parameters
    -----------
    group : str, list. a list of element name or a name pattern.
    include_virtual : include virtual element or not.

    Returns
    ---------
     elemlist : a list of matched element objects.

    Examples
    ----------
    >>> getElements('NO_SUCH_ELEMENT')
      []
    >>> getElements('PH1G2C30A')
      [PH1G2C30A:BPM @ sb=4.935000]
    >>> getElements('BPM')
      ...
    >>> getElements('F*G1C0*')
      ...
    >>> getElements(['FH2G1C30A', 'FH2G1C28A'])
      ...

    """

    # return the input if it is a list of element object
    if isinstance(group, element.AbstractElement):
        return [group]
    elif isinstance(group, (list, tuple)):
        if all([isinstance(e, element.AbstractElement) for e in group]):
            return group

    elems = machines._lat.getElementList(group)
    ret = []
    for e in elems:
        if e is None:
            ret.append(e)
            continue

        if not include_virtual and e.virtual: continue
        ret.append(e)

    return ret

def getExactElement(elemname):
    """find the element with exact name"""
    return machines._lat._find_exact_element(name=elemname)

def eget(elem, fields = None, **kwargs):
    raise RuntimeError("deprecated! please revise it to `fget(elem,field)`")

def fget(*argv, **kwargs):
    """
    fast get data.

    If provided, it will take *sample* readings separated by *sleep* seconds
    each step and do an average.

    >>> fget("BPM", "x")
    >>> fget([(bpm1, 'x'), (bpm2, 'y')])
    >>> fget([bpm1, bpm2, bpm3], 'x', sample=5, sleep=0.15)
    >>> fget("HCOR", "x", handle="readback", unitsys=None)
    >>> fget("HCOR", "x", handle="setpoint")
    """
    sample = kwargs.pop("sample", 1)
    dt = kwargs.pop("sleep", 0.15)
    rawd = []
    for i in range(sample):
        if len(argv) == 1:
            elem, fld = zip(*(argv[0]))
            d = _fget_2(elem, fld, **kwargs)
        elif len(argv) == 2:
            elst = getElements(argv[0])
            if not elst: return None
            d = _fget_2(elst, [argv[1]] * len(elst), **kwargs)
        else:
            raise RuntimeError("Unknown input {0}".format(argv))
        if len(d) == 0:
            raise ValueError("No data retrieved")
        rawd.append(d)
        if i < sample - 1:
            time.sleep(dt)

    return np.average(rawd, axis=0)


def _fget_2(elst, field, **kwargs):
    """get elements field values for a family

    Parameters
    -----------
    elem : list. element name, name list, pattern or object list
    fields : list. field name or name list
    handle : str, optional, default "readback"
    unitsys : str, optional, default "phy", unit system,

    returns a flat 1D array.

    Examples
    ---------
    >>> fget('DCCT', 'value')
    >>> fget('BPM', 'x')
    >>> fget('p*c30*', 'x')

    >>> bpm = getElements('p*c30*')
    >>> fget(bpm, 'x', handle="readback", unitsys = None)

    Note
    -----

    if handle is not specified, try readback pvs first, if not exist, use
    setpoint.

    It will be confusing if the (elem,field) has other than one output value.
    """

    unitsys = kwargs.pop("unitsys", "phy")
    handle = kwargs.get('handle', "readback")

    if "handle" in kwargs:
        v = [e.pv(field=fld, handle=handle) for e,fld in zip(elst, field)]
        assert len(set([len(pvl) for pvl in v])) <= 1, \
            "Must be exact one pv for each field"
        pvl = reduce(lambda x,y: x + y, v)
    else:
        # if handle is not specified, try readback and setpoint
        pvlrb, pvlsp = [], []
        for e,fld in zip(elst, field):
            pvlrb.extend(e.pv(field=fld, handle="readback"))
            pvlsp.extend(e.pv(field=fld, handle="setpoint"))
        if pvlrb:
            pvl = pvlrb
        else:
            pvl = pvlsp

    #if len(pvl) == 0:
    #    raise ValueError("No PVs was found")
    kwargs.pop("handle", None)
    dat = caget(pvl, **kwargs)
    if unitsys is None or len(pvl) == 0: return dat

    ret = [e.convertUnit(field[i], dat[i], None, unitsys)
               for i,e in enumerate(elst)]
    return ret


def fput(elemfld_vals, **kwargs):
    """set elements field values for a family

    Parameters
    -----------
    elemfld_vals : list or tuple. A list of (element, field, value)
    wait_readback : True/False. default False. Waiting until readback agrees
    timeout : int, optional, default 5, in seconds.
    unitsys : None or str, default "phy", unit system.
    epsilon : float, list or tuple. default None.
    verbose : int, verbose

    Examples
    ---------
    >>> cors = getElements("COR")
    >>> elemfld = [(cors[0], 'x', 0.0), (cors[0], 'y', 0.0)]
    >>> fput(elemfld, wait_readback = True, epsilon=[0.1, 0.1])

    If epsilon is not provided, use system configured.
    """

    # timeout = kwargs.pop('timeout', 5)
    unitsys = kwargs.pop('unitsys', "phy")
    wait_readback = kwargs.pop('wait_readback', False)
    epsilon = kwargs.pop("epsilon", None)
    verbose = kwargs.get("verbose", 0)

    # a list of (pv, spval, elem, field)
    pvl, pvlsp = [], []

    if epsilon is None:
        epsl = [e.getEpsilon(fld) for e,fld,v in elemfld_vals]
    elif isinstance(epsilon, (list, tuple)):
        epsl = epsilon
    else:
        epsl = [epsilon] * len(elemfld_vals)

    for i,r in enumerate(elemfld_vals):
        elem, fld, val = r
        valrec = [val, val - epsl[i], val + epsl[i]]
        if unitsys is not None:
            valrec = [elem.convertUnit(fld, v, unitsys, None)
                      for v in valrec]
        pvsp = elem.pv(field=fld, handle="setpoint")
        pvrb = elem.pv(field=fld, handle="readback")
        for j,pv in enumerate(zip(pvsp, pvrb)):
            pvl.append([elem, fld, pv[0], pv[1]] + valrec)
        for j,pv in enumerate(pvsp):
            pvlsp.append([elem, fld, pv, None] + valrec)

    # pvsp and pvl could be different size
    if wait_readback:
        if len(pvlsp) != len(pvl):
            raise RuntimeError("invalid size READBACK != SETPOINT (%d != %d)" %
                               (len(pvl), len(pvlsp)))
        pvsp = [v[2] for v in pvl]
        pvrb = [v[3] for v in pvl]
        vals = [v[4] for v in pvl]
        if verbose:
            print((len(pvsp), pvsp))
            print((len(vals), vals))
        ret = caput(pvsp, vals, **kwargs)
        vallo, valhi = [v[5] for v in pvl], [v[6] for v in pvl]
        try:
            caWaitStable(pvrb, vals, vallo, valhi, **kwargs)
        except:
            _logger.error("failed setting {0}={1}".format(pvsp, vals))
            raise
    else:
        pvsp = [v[2] for v in pvlsp]
        vals = [v[4] for v in pvlsp]
        if verbose:
            print((len(pvsp), pvsp))
            print((len(vals), vals))
        ret = caput(pvsp, vals, **kwargs)


def getPvList(elems, field, handle = 'readback', **kwargs):
    """return a pv list for given element or element list

    Parameters
    ------------
    elems : element pattern, name list or CaElement object list
    field : e.g. 'x', 'y', 'k1'
    handle : 'readback' or 'setpoint'

    Keyword arguments:

      - *first_only* (False) use only the first PV for each element.
      - *compress_empty* (False) remove element with no PV.

    :Example:

      >>> getPvList('p*c30*', 'x')

    This can be simplified as::

      [e.pv(field) for e in getElements(elem) if field in e.fields()]

    extract the pv only if the element has that field (compress_empty=True).

      [e.pv(field) if field in e.fields() else None for e in getElements(elem)]

    put a None in the list if the field is not in that element

    *elem* accepts same input as :func:`getElements`
    """
    first_only = kwargs.get('first_only', False)
    compress_empty = kwargs.get('compress_empty', False)

    # did not check if it is a BPM
    elemlst = getElements(elem)
    pvlst = []
    for elem in elemlst:
        if not isinstance(elem, element.CaElement):
            raise ValueError("element '%s' is not CaElement" % elem.name)
        #
        pvs = elem.pv(field=field, handle=handle)
        if len(pvs) == 0 and not compress_empty:
            raise ValueError("element '%s' has no readback pv" % elem.name)
        elif len(pvs) > 1 and not first_only:
            raise ValueError("element '%s' has more %d (>1) pv" %
                             (elem.name, len(pvs)))

        pvlst.append(pvs[0])

    return pvlst


def getLocations(group):
    """
    Get the location of a group, i.e. a family, an element or a list of
    elements

    Examples
    ---------

    >>> s = getLocations('BPM')
    >>> s = getLocations(['PM1G4C27B', 'PH2G2C28A'])

    It has a same input as :func:`getElements` and accepts group name,
    element name, element name pattern and a list of element names.
    """

    elem = getElements(group)
    if isinstance(elem, (list, set, tuple)):
        return [e.sb for e in elem]
    else: return elem.sb

def addGroup(group):
    """
    add a new group to current submachine.

    *group* should be plain string, characters in \[a-zA-Z0-9\_\]

    raise *ValueError* if *group* is an illegal name.

    it calls :func:`~aphla.lattice.Lattice.addGroup` of the current lattice.
    """
    return machines._lat.addGroup(group)

def removeGroup(group):
    """
    Remove a group if it is empty. It calls
    :func:`~aphla.lattice.Lattice.removeGroup` of the current lattice.
    """
    machines._lat.removeGroup(group)

def addGroupMembers(group, member):
    """
    add new members to an existing group

    ::

      >>> addGroupMembers('HCOR', 'CX1')
      >>> addGroupMembers('HCOR', ['CX1', 'CX2'])

    it calls :meth:`~aphla.lattice.Lattice.addGroupMember` of the current
    lattice.
    """
    if isinstance(member, str):
        machines._lat.addGroupMember(group, member)
    elif isinstance(member, list):
        for m in member:
            machines._lat.addGroupMember(group, m)
    else:
        raise ValueError("member can only be string or list")

def removeGroupMembers(group, member):
    """
    Remove a member from group

    ::

      >>> removeGroupMembers('HCOR', 'CX1')
      >>> removeGroupMembers('HCOR', ['CX1', 'CX2'])

    it calls :meth:`~aphla.lattice.Lattice.removeGroupMember` of the current
    lattice.
    """
    if isinstance(member, str):
        machines._lat.removeGroupMember(group, member)
    elif isinstance(member, list):
        for m in member: machines._lat.removeGroupMember(group, m)
    else:
        raise ValueError("member can only be string or list")


def getGroups(element = '*'):
    """
    Get all groups own these elements, '*' returns all possible groups,
    since it matches every element

    it calls :func:`~aphla.lattice.Lattice.getGroups` of the current lattice.
    """
    return machines._lat.getGroups(element)


def getGroupMembers(groups, op = 'intersection', **kwargs):
    """
    Get all elements in a group. If group is a list, consider which op:

    - op = "union", consider elements in the union of the groups
    - op = "intersection", consider elements in the intersect of the groups

    it calls :func:`~aphla.lattice.Lattice.getGroupMembers` of the current
    lattice.
    """
    return machines._lat.getGroupMembers(groups, op, **kwargs)


def getNeighbors(element, group, n = 3, elemself = True):
    """
    Get a list of n objects in *group* before and after *element*

    it calls :meth:`~aphla.lattice.Lattice.getNeighbors` of the current
    lattice to get neighbors.

    Parameters
    -----------
    element: str, object. the central element name
    group: str or list of elem object, the neighbors belong to
    n : int, default 3, number of neighbors each side.
    elemself : default True, return the element itself.

    Returns
    --------
    elems : a list of element in given group. The list is
        sorted along s (the beam direction). There is 2*n+1 elements if
        elemself=True, else 2*n.


    Examples
    ----------
    >>> getNeighbors('X', 'BPM', 2) # their names are ['1','2','X', '3', '4']
    >>> getNeighbors('QC', 'QUAD', 1) # their names are ['Q1', 'QC', 'Q2']
    >>> el = hla.getNeighbors('PH2G6C25B', 'P*C10*', 2)
    >>> [e.name for e in el]
      ['PL2G6C10B', 'PL1G6C10B', 'PH2G6C25B', 'PH1G2C10A', 'PH2G2C10A']
    >>> [e.sb for e in el]
      [284.233, 286.797, 678.903, 268.921, 271.446]
    >>> hla.getNeighbors("X", ["BPM", "QUAD"], 2)
    >>> hla.getNeighbors("X", getElements("BPM"), 3)
    """

    if isinstance(element, string_types):
        return machines._lat.getNeighbors(element, group, n, elemself)
    else:
        return machines._lat.getNeighbors(element.name, group, n, elemself)


def getClosest(element, group):
    """
    Get the closest neighbor in *group* for an element

    It calls :meth:`~aphla.lattice.Lattice.getClosest`

    Parameters
    -----------
    element: str, object. the element name or object
    group: str, the closest neighbor belongs to this group

    Examples
    ----------
    >>> getClosest('pm1g4c27b', 'BPM') # find the closest BPM to 'pm1g4c27b'
    >>> getClosest('pm1g4c27b', ["QUAD", "BPM"])
    """
    if isinstance(element, string_types):
        return machines._lat.getClosest(element, group)
    else:
        return machines._lat.getClosest(element.name, group)

def getBeamlineProfile(**kwargs):
    """
    return the beamline profile from sposition sb to se

    :param float s1: s-begin
    :param float s2: s-end, None means the end of beamline.

    it calls :meth:`~aphla.lattice.Lattice.getBeamlineProfile` of the
    current lattice.
    """
    return machines._lat.getBeamlineProfile(**kwargs)


def getDistance(elem1, elem2, absolute=True):
    """
    return distance between two element name

    Parameters
    -----------
    elem1: str, object. name or object of one element
    elem2: str, object. name or object of the other element
    absolute: bool. return s2 - s1 or the absolute value.

    Raises
    -------
    it raises RuntimeError if None or more than one elements are found
    """
    e1 = getElements(elem1)
    e2 = getElements(elem2)

    if len(e1) != 1 or len(e2) != 1:
        raise RuntimeError("elements are not uniq: %d and %d" % \
                           (len(e1), len(e2)))

    ds = e2[0].sb - e1[0].sb
    C = machines._lat.circumference
    if machines._lat.loop and C > 0:
        while ds < -C: ds = ds + C
        while ds > C: ds = ds - C
    if absolute: return abs(ds)
    else: return ds

@lru_cache(maxsize=256)
def _getCahcedElemNames(group_name_or_pattern):
    """"""

    return [e.name for e in getElements(group_name_or_pattern)]

def getTwiss(names, columns, **kwargs):
    """
    get the twiss data
    - names: a list of element names or a name pattern or a group name (e.g.,
        "BPM", "QUAD").
    - columns: a sublist of [s, betax(y), alphax(y), gammax(y), etax(y), phix(y)]
    - source: optional, default "model" if a model is currently loaded; otherwise,
        "database".
    - search_model_elem_names: optional, default False. If False, seach for
        "names" will occur for all the elements in the currently selected
        Lattice object. In this case, use of group names will work as in
        getElements(). If True, search will be applied to the element names
        in the model data file from which the Twiss data are being retrieved.
        Since there is no group defined in those data files, a group name search
        will not work as intended.

    example:

    >>> getTwiss("p*", ["s", "betax", "betay"])
    >>> getTwiss(["p1", "p2"], ["s", "etax"])
    """

    col = [c for c in columns]

    m = models.getModel()
    default_src = "database" if m is None else "model"
    src = kwargs.pop("source", default_src)
    search_model_elem_names = kwargs.pop("search_model_elem_names", False)

    if src == "model":
        m._recalc('twiss') # Make sure that Twiss data are updated, if not yet.
        if not m._twiss:
            _logger.error("ERROR: no twiss data in the current model")
            return None
        if (not search_model_elem_names) and isinstance(names, string_types):
            _name_list = _getCahcedElemNames(names)
            return m._twiss.get(_name_list, col=col)
        else:
            return m._twiss.get(names, col=col)
    elif src == "database":
        if not machines._lat._twiss:
            _logger.error("ERROR: no twiss data loaded")
            return None
        if (not search_model_elem_names) and isinstance(names, string_types):
            _name_list = _getCahcedElemNames(names)
            return machines._lat._twiss.get(_name_list, col=col)
        else:
            return machines._lat._twiss.get(names, col=col)
    elif src == "VA":
        vas = getElements("VA")
        if not vas: return None
        twiss = vas[kwargs.get("iva", 0)]
        if isinstance(names, string_types):
            namelst = [i for i,s in enumerate(twiss.names) if fnmatch(s, names)]
        elif isinstance(names, (list, tuple)):
            namelst = [i for i,s in enumerate(twiss.names) if s in names]
        else:
            raise ValueError("names must be string or list of element names")
        dat = np.zeros((len(namelst), len(columns)), 'd')
        for i,c in enumerate(columns):
            d = twiss.get(c, unitsys=None)
            dat[:,i] = [d[j] for j in namelst]
        return dat
    else:
        return None


def getTwissAt(s, columns, **kwargs):
    """
    similar to getTwiss, but at specific location
    """
    col = [c for c in columns]
    src = kwargs.pop("source", "database")
    if src == "database":
        if not machines._lat._twiss:
            _logger.error("ERROR: no twiss data loaded")
            return None
        try:
            twl = [machines._lat._twiss.at(si, col=col)
                   for si in s]
            return np.array(twl, 'd')
        except:
            return machines._lat._twiss.at(s, col=col)
    else:
        return [None] * len(columns)


def getPhi(group, **kwargs):
    """
    get the phase [rad] from stored data

    this calls :func:`~aphla.apdata.TwissData.get` of the current twiss data.
    """
    col = ['phix', 'phiy']
    if kwargs.pop('spos', False): col.append('s')
    return getTwiss(group, col, **kwargs)


def getPhase(group, **kwargs):
    """see :func:`getPhi`"""
    return getPhi(group, **kwargs)

##
def getAlpha(group, **kwargs):
    """
    get the phase from stored data

    this calls :func:`~aphla.apdata.TwissData.get` of the current twiss data.
    """
    col = ['alphax', 'alphay']
    if kwargs.pop('spos', False): col.append('s')
    return getTwiss(group, col, **kwargs)
#
#
def getBeta(group, **kwargs):
    """get the beta function of *group* from stored data.

    Parameters
    -----------
    src : str.
        'database' from database, 'VA' from 'virtualacc' element of virtual accelerator

    Examples
    ---------
    >>> getBeta('q*', spos = False)

    """
    col = ['betax', 'betay']
    if kwargs.pop('spos', False): col.append('s')
    return getTwiss(group, col, **kwargs)


def getDispersion(group, **kwargs):
    """
    get the dispersion

    this calls :func:`~aphla.hlalib.getEta`.
    """
    return getEta(group, **kwargs)


def getEta(group, **kwargs):
    """get the dispersion from stored data

    Parameters
    -----------
    source : str.
        'database' from database; 'VA' from virtual accelerator where a 'twiss'
        element must exist.

    Examples
    --------
    >>> getEta('p*', spos = True, source = 'database')
    >>> getEta(['BPM1', 'BPM2'])

    """

    col = ['etax', 'etay']
    if kwargs.pop('spos', False): col.append('s')
    return getTwiss(group, col, **kwargs)

def getEtap(group, **kwargs):
    """get the so-called "eta prime", i.e., dispersion derivative w.r.t. s
    from stored data

    Parameters
    -----------
    source : str.
        'database' from database; 'VA' from virtual accelerator where a 'twiss'
        element must exist.

    Examples
    --------
    >>> getEta('p*', spos = True, source = 'database')
    >>> getEta(['BPM1', 'BPM2'])

    """

    col = ['etaxp', 'etayp']
    if kwargs.pop('spos', False): col.append('s')
    return getTwiss(group, col, **kwargs)

def getTwissUnit(property_name):
    """"""

    if machines._lat._twiss:
        return machines._lat._twiss.getUnit(property_name)

    m = models.getModel()
    m._recalc('twiss') # Make sure that Twiss data are updated, if not yet.
    if m._twiss:
        return m._twiss.getUnit(property_name)

    raise RuntimeError(f'Failed to retrieve unit for Twiss property "{property_name}"')

def getChromaticities(**kwargs):
    """"""

    m = models.getModel()
    default_src = "database" if m is None else "model"
    source = kwargs.pop("source", default_src)

    if source == 'model':
        if m is None:
            raise RuntimeError('No model is currently loaded.')
        else:
            return m.getChromaticities()
    elif source == 'database':
        return machines._lat.getChromaticities()
    else:
        raise ValueError("Unknown source: '%s'" % source)


def getChromaticity(plane, **kwargs):
    """
    get chromaticity from ["model", "database"]
    """

    m = models.getModel()
    default_src = "database" if m is None else "model"
    source = kwargs.pop("source", default_src)

    ksi_tuple = getChromaticities(source=source)
    if ksi_tuple is None:
        return None
    else:
        ksix, ksiy = ksi_tuple

    if plane.lower() in ('x', 'h'): return ksix
    elif plane.lower() in ('y', 'v'): return ksiy
    else:
        raise ValueError('Valid values for "plane": "x", "y", "h", "v"')

def getTunes(source='machine', **kwargs):
    """
    get tunes from ['machine', 'database', "VA"]
    """
    if source == 'machine':
        # If online mode, the data will be pulled from PVs, while if in simulated
        # mode, they will be pulled from MVs (i.e., from the currently loaded
        # model).

        # return only the first matched element
        nu = getElements('tune')
        if not nu:
            raise RuntimeError("can not find element 'tune'")
        return nu[0].x, nu[0].y
    elif source == 'model':
        m = models.getModel()
        if m is None:
            raise RuntimeError('No model is currently loaded.')
        else:
            return m.getTunes()
    elif source == 'database':
        return machines._lat.getTunes()
    elif source == "VA":
        vas = getElements('VA')
        if not vas: return None
        twiss = vas[kwargs.get("iva", 0)]
        return twiss.nux, twiss.nuy
    else:
        raise ValueError("Unknow source: '%s'" % source)


def getTune(plane, source='machine'):
    """get one of the tune, 'h' or 'v' or 'x' or 'y'.

    Examples
    ---------
    >>> getTune(plane='v')

    """
    nux, nuy = getTunes(source)
    if plane.lower() in ('x', 'h'): return nux
    elif plane.lower() in ('y', 'v'): return nuy
    else:
        raise ValueError('Valid values for "plane": "x", "y", "h", "v"')


def getMomentumCompaction(**kwargs):
    """"""

    m = models.getModel()
    default_src = "database" if m is None else "model"
    source = kwargs.pop("source", default_src)

    if source == 'model':
        if m is None:
            raise RuntimeError('No model is currently loaded.')
        else:
            return m.getMomentumCompaction()
    elif source == 'database':
        return machines._lat.getMomentumCompaction()
    else:
        raise ValueError("Unknown source: '%s'" % source)

def getAlphac(**kwargs):
    """"""

    return getMomentumCompaction(**kwargs)

def _getFftTune(plane = 'hv', mode = ''):
    """get tune from FFT

    .. warning::

      Not Implemented Yet
    """
    raise NotImplementedError()
    return None


def getChromaticityRm(mode, phase, info):
    """
    Not implemented yet
    """
    raise NotImplementedError()
    return None, None


def getTuneRm(mode):
    """
    Not implemented yet, see `measTuneRm`
    """
    raise NotImplementedError()


def getBpms():
    """
    return a list of bpms object.

    this calls :func:`~aphla.lattice.Lattice.getGroupMembers` of current
    lattice and take a "union".
    """
    return machines._lat.getGroupMembers('BPM', op='union')


def getQuads():
    """
    return a list of bpms object.

    this calls :func:`~aphla.lattice.Lattice.getGroupMembers` of current
    lattice and take a "union".
    """
    return machines._lat.getGroupMembers('QUAD', op='union')


def getOrbitUnit(pat='', spos=False, unitsys='phy'):
    """
    Return the unit strings for the output of getOrbit()
    """

    if not CONFIG['unitless_quantities']:
        print('WARNING: Pint Quantity objects are being returned by getOrbit().')
        print('Hence, the unit strings returned by this function getOrbitUnit()')
        print('are meaningless.')

    if not pat:
        bpm = machines._lat._find_exact_element(machines.HLA_VBPM)

        unit_strs = {
            fld: bpm.getUnit(fld, unitsys=unitsys) for fld in ['x', 'y']}

    else:

        if isinstance(pat, string_types):
            elems = [e for e in getBpms()
                    if fnmatch(e.name, pat) and e.isEnabled()]
            if not elems: return None
            ret = [[e.get('x', handle='readback', unitsys=unitsys),
                    e.get('y', handle='readback', unitsys=unitsys),
                    e.sb] for e in elems]
        elif isinstance(pat, (list,)):
            elems = machines._lat.getElementList(pat)
            if not elems: return None
            bpm = [e.name for e in getBpms() if e.isEnabled()]
            ret = []
            for e in elems:
                if not e.name in bpm: ret.append([None, None, None])
                else: ret.append([
                    e.get('x', handle='readback', unitsys=unitsys),
                    e.get('y', handle='readback', unitsys=unitsys),
                    e.sb])

        if not ret: return None

        unit_strs = {
            fld: elems[0].getUnit(fld, unitsys=unitsys) for fld in ['x', 'y']}

    if spos:
        unit_strs['spos'] = 'm'

    return unit_strs

def getOrbit(pat='', spos=False, unitsys='phy'):
    """
    Return orbit (for BPM element fields: "x" & "y")

    :Example:

      >>> getOrbit()
      >>> getOrbit('*')
      >>> getOrbit('*', spos=True)
      >>> getOrbit(['PL1G6C24B', 'PH2G6C25B'])

    If *pat* is not provided, use the group read of every BPMs, this is
    faster than read BPM one by one with getOrbit('*').

    The return value is a (n,4) or (n,2) 2D array, where n is the number
    of matched BPMs. The first two columns are x/y orbit, the last two
    columns are s location for x and y BPMs. returns (n,3) 2D array if x/y
    have same *s* position.

    When the element is not found or not a BPM, return NaN in its positon.
    """
    if not pat:
        bpm = machines._lat._find_exact_element(machines.HLA_VBPM)
        n = len(bpm.sb)
        if spos:
            if not CONFIG['unitless_quantities']:
                ret = Q_(np.zeros((n, 3)), ureg.meter)
                ret[:, 2] = Q_(bpm.sb, ureg.meter)
            else:
                ret = np.zeros((n, 3), 'd')
                ret[:, 2] = bpm.sb
        else:
            if not CONFIG['unitless_quantities']:
                ret = Q_(np.zeros((n, 2)), ureg.meter)
            else:
                ret = np.zeros((n, 2), 'd')

        try:
            ret[:, 0] = bpm.get('x', handle='readback', unitsys=unitsys)
        except:
            if unitsys is not None:
                print(f'Unit conversion for element "{bpm.name}", field "x" failed for {unitsys}')
                ret[:, 0] = bpm.x
            else:
                raise

        try:
            ret[:, 1] = bpm.get('y', handle='readback', unitsys=unitsys)
        except:
            if unitsys is not None:
                print(f'Unit conversion for element "{bpm.name}", field "y" failed for {unitsys}')
                ret[:, 1] = bpm.y
            else:
                raise
        return ret

    # need match the element name
    if isinstance(pat, string_types):
        elems = [e for e in getBpms()
                if fnmatch(e.name, pat) and e.isEnabled()]
        if not elems: return None
        ret = [[e.get('x', handle='readback', unitsys=unitsys),
                e.get('y', handle='readback', unitsys=unitsys),
                e.sb] for e in elems]
    elif isinstance(pat, (list,)):
        elems = machines._lat.getElementList(pat)
        if not elems: return None
        bpm = [e.name for e in getBpms() if e.isEnabled()]
        ret = []
        for e in elems:
            if not e.name in bpm: ret.append([None, None, None])
            else: ret.append([
                e.get('x', handle='readback', unitsys=unitsys),
                e.get('y', handle='readback', unitsys=unitsys),
                e.sb])

    if not ret: return None

    if not CONFIG['unitless_quantities']:
        n = len(ret)
        if spos:
            obt = Q_(np.zeros((n, 3)), ureg.meter)
        else:
            obt = Q_(np.zeros((n, 2)), ureg.meter)

        for i in range(2):
            obt[:, i] = Q_([v[i].magnitude for v in ret], ret[0][i].units)

        if spos:
            obt[:, 2] = Q_([v[2] for v in ret], ureg.meter)

        return obt
    else:
        obt = np.array(ret, 'd')
        if not spos: return obt[:,:2]
        else: return obt


def getAverageOrbit(pat = '', spos=False, nsample = 5, dt = 0.1):
    t0 = datetime.datetime.now()
    obt0 = getOrbit(pat=pat, spos=spos)
    nbpm, ncol = np.shape(obt0)
    obt = np.zeros((nbpm, ncol, nsample), 'd')
    obt[:,:,0] = obt0[:,:]
    for i in range(1, nsample):
        t1 = datetime.datetime.now()
        dts = (t1 - t0).total_seconds()
        if dts < dt * i:
            time.sleep(dt*i - dts + 0.001)
        obt[:,:,i] = getOrbit(pat=pat, spos=spos)
    return np.average(obt, axis=-1), np.std(obt, axis=-1)


def getOrbitResponseMatrix():
    """
    returns m, list of (bpmname, field) and list of (corname, field). field is
    'x' or 'y'
    """
    orm = machines._lat.ormdata
    return orm.m, orm.bpm, orm.cor


def _getTbtOrbit(**kwargs):
    """
    return turn-by-turn BPM data.

    - *field* ['A', 'B', 'C', 'D', 'X', 'Y', 'S', 'Q'], each has the RMS value: 'rmsA'-'rmsQ'
    """
    field = kwargs.get('field', 'X')
    pref = 'LTB:BI{BPM:1}' + 'TBT-'
    return caget(pref + field)

def _getFastOrbit(**kwargs):
    """
    return fast 10kHz turn-by-turn BPM data.

    - *field* ['A', 'B', 'C', 'D', 'X', 'Y', 'S', 'Q'], each has the RMS value: 'rmsA'-'rmsQ'
    """
    field = kwargs.get('field', 'X')
    pref = 'LTB:BI{BPM:1}' + 'FA-'
    return caget(pref + field)


def _reset_bpm_offset():
    bpms = getElements('BPM')
    pvs = []
    for b in bpms:
        #print b.pv(tags=['aphla.offset', 'aphla.eput'])
        pvs.extend(b.pv(tags=['aphla.offset', 'aphla.eput']))
    if pvs: caput(pvs, 0.0)
    _logger.info("Reset the bpm offset")


def _reset_quad():
    #raise RuntimeError("does not work for SR above V1SR")

    qtag = {'H2': (1.47765, 30),
            'H3': (-1.70755, 30),
            'H1': (-0.633004, 30),
            'M1': (-0.803148, 60),
            'M2': (1.2223, 60),
            'L2': (1.81307, 30),
            'L3': (-1.48928, 30),
            'L1': (-1.56216, 30)}

    for tag, v in qtag.items():
        qlst = getElements('Q%s' % tag)
        qval, qnum = v
        if len(qlst) != qnum:
            raise ValueError("ring does not have exactly %d %s (%d)" % \
                                 (qnum, tag, len(qlst)))
        for q in qlst:
            q.value = qval

def waitStableOrbit(reforbit, **kwargs):
    """
    set pv to a value, waiting for timeout or the new orbit is stable around reforbit.

    - *diffstd* = 1e-7, std(obt - reforbit) < diffstd means stable
    - *minwait* = 2, wait at least *minwait* seconds.
    - *maxwait* =30, timeout seconds.
    - *step* = 2, sleep at each step.
    - *diffstd_list* = False
    """

    diffstd = kwargs.get('diffstd', 1e-7)
    minwait = kwargs.get('minwait', 2)
    maxwait = kwargs.get('maxwait', 30)
    step    = kwargs.get('step', 2)
    diffstd_list = kwargs.get('diffstd_list', False)
    verbose = kwargs.get('verbose', 0)

    t0 = time.time()
    time.sleep(minwait)
    dv = getOrbit() - reforbit
    dvstd = [dv.std()]
    timeout = False

    while dv.std() < diffstd:
        time.sleep(step)
        dt = time.time() - t0
        if dt  > maxwait:
            timeout = True
            break
        dv = getOrbit() - reforbit
        dvstd.append(dv.std())

    if diffstd_list:
        return timeout, dvstd


def _wait_for_lock(tag, maxwait=60):
    """
    wait until the virtual accelerator is available to me.
    """
    print("# Locking the mathine for userid=%d" % tag)
    if tag == 0:
        raise ValueError("you tag (=%d)  must be > 0." % tag)

    t0 = time.time()
    while caget('SVR:LOCKED') > 0:
        print("# waiting ... for user %d ..." % int(caget('SVR:LOCKED')))
        time.sleep(1)
        if time.time() - t0 > maxwait: break

    if caget('SVR:LOCKED') == 0:
        caput('SVR:LOCKED', tag)
    else:
        raise ValueError("can not get the writting permission to virtual accelerator")

def _release_lock(tag):
    if caget('SVR:LOCKED') == 0:
        raise ValueError("some one already reset the lock")
    if caget('SVR:LOCKED') != tag:
        raise ValueError("it is not locked by me, abort")

    caput('SVR:LOCKED', 0)
    print("released the lock for userid=%d" % tag)



def _waitChanged(elemlst, fields, v0, **kwargs):
    """
    set pvs and waiting until the setting takes effect

    :param elemlst: element list
    :type elemlist: list of Elements
    :param v0: old values
    :type v0: list
    :param diffstd: threshold value of effective change of *pvmonitors*.
    :param wait: waiting time for initial, each step and final (seconds)
    :param maxtrial: maximum trial before return.
    :param unit: unit of field
    :param full: return total trials

    :return: whether pvmonitors change significant enough.
    :rtype: bool

    It sets the pvs with new values and tests the monitor values see if the
    changes are significant enough. This significance is measured by comparing
    the std of monitor value changes due to the *pvs* changes. If it exceeds
    *diffstd* then return, otherwise wait for *wait* seconds and test
    again. The maximum trial is *maxtrial*.

    It is good for ORM measurement where setting a trim and observing a list
    of BPM.
    """

    diffstd= kwargs.get('diffstd', 1e-6)
    wait = kwargs.get('wait', (2, 1, 0))
    maxtrial= kwargs.get('maxtrial', 20)
    full = kwargs.get('full', False)
    unitsys = kwargs.get('unitsys', None)

    if CA_OFFLINE:
        if full: return (True, 0)
        else: return True

    time.sleep(wait[0])

    ntrial = 0
    while True:
        v1 = np.ravel(eget(elemlst, fields, unitsys=unitsys))
        time.sleep(wait[1])
        ntrial = ntrial + 1
        if np.std(v1 - np.array(v0)) > diffstd: break
        if ntrial >= maxtrial: break

    time.sleep(wait[2])

    if full:
        if ntrial >= maxtrial: return (False, ntrial)
        else: return (True, ntrial)
    else:
        if ntrial >= maxtrial: return False
        else: return True


def _waitStable(elemlst, fields, maxstd, **kwargs):
    """
    set pvs and waiting until the setting takes effect

    :param elemlst: element list
    :type elemlist: list of Elements
    :param v0: old values
    :type v0: list
    :param diffstd: threshold value of effective change of *pvmonitors*.
    :param wait: waiting time for initial, each step and final (seconds)
    :param maxtrial: maximum trial before return.
    :param unit: unit of field

    :return: whether pvmonitors change significant enough.
    :rtype: bool

    It sets the pvs with new values and tests the monitor values see if the
    changes are significant enough. This significance is measured by comparing
    the std of monitor value changes due to the *pvs* changes. If it exceeds
    *diffstd* then return, otherwise wait for *wait* seconds and test
    again. The maximum trial is *maxtrial*.

    It is good for ORM measurement where setting a trim and observing a list
    of BPM.
    """

    wait = kwargs.get('wait', (2, 1, 0))
    maxtrial= kwargs.get('maxtrial', 3)
    unitsys = kwargs.get('unitsys', None)

    if CA_OFFLINE: return True

    time.sleep(wait[0])

    v = np.zeros((len(elemlst), maxtrial), 'd')
    for i in range(maxtrial):
        v[:,i] = np.ravel(eget(elemlst, fields, unitsys=unitsys))
        time.sleep(wait[1])

    time.sleep(wait[2])
    if np.average(np.std(v, axis=0)) < maxstd: return True
    else: return False



def saveLattice(output, lat, elemflds, notes, **kwargs):
    """
    save lattice info to a HDF5 file.

    - output, output file name. If it is True, save to the default place with default filename.
    - lattice, default the current active lattice
    - subgroup, default "", used for output file name
    - elements, default "*"
    - notes, default ""

    returns the output file name.

    ::
        >>> elemflds = [("COR", ("x", "y")), ("QUAD", ("b1",))]
        >>> saveLattice("snapshot.hdf5", lat, elemflds, "Good one")

    the duplicate PVs will save only one instance.
    """
    # save the lattice
    verbose = kwargs.get("verbose", 0)

    pvstat = {}
    pvs, pvspl = [], []
    for elfam,flds in elemflds:
        el = lat.getElementList(elfam, virtual=False)
        for fld in flds:
            fpvs = reduce(lambda a,b: a+b, [e.pv(field=fld) for e in el])
            pvs.extend(fpvs)
            sppvs = reduce(lambda a,b: a+b,
                           [e.pv(field=fld, handle="setpoint") for e in el])
            pvspl.extend(sppvs)
            pvstat[(elfam, fld)] = (len(fpvs), len(sppvs))
            if verbose:
                print("{0}.{1}: {2} pvs, {3} setpoint".format(
                    elfam, fld, len(fpvs), len(sppvs)))

    if lat.arpvs is not None:
        for s in open(lat.arpvs, 'r').readlines():
            pv = s.strip()
            if pv in pvs: continue
            pvs.append(pv)

    nlive, ndead = savePvData(output, pvs,
                              group=lat.name, notes=notes, **kwargs)

    import h5py
    h5f = h5py.File(output, 'a')
    grp = h5f[lat.name]
    # add elem field information
    grp.attrs["_query_"] = [
      "%s(%s)" % (elfam, ",".join(flds)) for elfam,flds in elemflds]
    for k,v in pvstat.items():
        grp.attrs["%s_%s_pvs" % (k[0], k[1])] = v
    #
    # save the query command for each PV (overhead)
    #for elfam,flds in elemflds:
    #    el = lat.getElementList(elfam, virtual=False)
    #    for fld in flds:
    #        for pv in e.pv(field=fld):
    #            grp[pv].attrs["_query_"] = [elfam, fld]
    #        for pv in e.pv(field=fld, handle="setpoint"):
    #            grp[pv].attrs["_query_"] = [elfam, fld]

    # add the setpoint
    for pv in kwargs.get("pvsp", []):
        grp[pv].attrs["setpoint"] = 1
    h5f.close()

    if verbose > 0:
        print("--------")
        print("PVs: live= %d, dead= %d" % (nlive, ndead))
    return nlive, ndead


def putLattice(h5fname, **kwargs):
    """
    elemflds : list of (elementfam, list_of_fields), e.g. [("COR", ("x", "y"))]
    nstep : 3, split each setpoint in steps
    tspan : 3.0, span over tspan seconds when set magnet in several steps.

    ::

    >>> putLattice("sr_snapshot.hdf5", elemflds=[("COR", ("x", "y"))])
    """
    nstep = kwargs.get("nstep", 3)
    tspan = kwargs.get("tspan", 3.0)
    elemflds = kwargs.get("elemflds", [])

    lat = machines._lat
    pvspl, pvs = [], []
    for elfam,flds in elemflds:
        el = lat.getElementList(elfam, virtual=False)
        for fld in flds:
            pvs.extend(
                reduce(lambda a,b: a+b, [e.pv(field=fld) for e in el]))
            pvspl.extend(
                reduce(lambda a,b: a+b,
                       [e.pv(field=fld, handle="setpoint") for e in el]))
    import h5py
    h5f = h5py.File(h5fname, 'r')
    grp = h5f[lat.name]
    if not pvspl:
        print("Please select element family and fields in this snapshot:")
        for famflds in grp.attrs.get("_query_", []):
            m =re.match(r"([^(]+)\((.+)\)", famflds)
            if not m:
                print(famflds)
                continue
            print((m.group(1), m.group(2).split(",")))
        #print grp.attrs.get("_query_", [])
    else:
        vals = [grp[pv].value for pv in pvspl]
        dv = [(vals[j] - v) / nstep for j,v in enumerate(caget(pvspl))]
        for i in range(nstep):
            t0 = datetime.now()
            vi = [vals[j] - (nstep - 1 - i)*dv[j] for j in range(len(vals))]
            caput(pvspl, vi, timeout=tspan)
            dt = (datetime.now() - t0).total_seconds()
            if dt < tspan * 1.0 / nstep:
                time.sleep(tspan * 1.0 / nstep - dt + 0.1)
    h5f.close()


def outputFileName(group, subgroup, create_path = True):
    """generate the system default output data file name

    'Lattice/Year_Month/group/subgroup_Year_Month_Day_HourMinSec.hdf5'
    e.g. 'SR/2014_03/bpm/bpm_Fa_0_2014_03_04_145020.hdf5'

    if new directory is created, with permission "rwxrwxr-x"
    """
    # use the default file name
    import stat
    t0 = datetime.now()
    output_dir = ""
    for subdir in [machines.getOutputDir(), t0.strftime("%Y_%m"), group]:
        output_dir = os.path.join(output_dir, subdir)
        if not os.path.exists(output_dir):
            if create_path:
                _logger.info("creating new directory: {0}".format(output_dir))
                os.mkdir(output_dir)
                os.chmod(output_dir, stat.S_ISGID | stat.S_IRWXU | stat.S_IRWXG | \
                         stat.S_IROTH | stat.S_IXOTH)
            else:
                raise RuntimeError("{0} does not exist".format(output_dir))

    fopt = subgroup + t0.strftime("%Y_%m_%d_%H%M%S.hdf5")
    return os.path.join(output_dir, fopt)


def calcTuneRm(quad, **kwargs):
    """
    calculate tune respose matrix

    quad - quadrupoles. same input as getElements.
    setpoint - default None, or a list of ("b1", raw_value, dval).
    unitsys - default None

    In physics unit, dnu/dkl = beta/4pi. When asking for raw unit (in A), we
    need to have a setpoint for Quad and convert the unit dkl/dI to get
    dnu/dI.  We calculate dkl/dI by converting I0=raw_value and
    I1=raw_value+dval to kl0 and kl1, dkl/dI = (kl1-kl0)/(I1-I0).
    """
    unitsys = kwargs.get("unitsys", None)
    sp = kwargs.get("setpoint", None)

    qls = getElements(quad)
    bta = np.zeros((len(qls), 2), 'd')
    m = np.zeros((2, len(qls)), 'd')
    for i,q in enumerate(qls):
        # use beta at the center of quad
        bta[i,:] = getTwissAt((q.sb + q.se)/2.0, ["betax", "betay"])
        # need to check if focusing or defocusing
        try:
            k1l = q.get("b1", handle="golden", unitsys="phy")
        except:
            raise RuntimeError(
                "can not determin defocusing/focusing for {}".format(q.name))
        if sp is None:
            fld = "b1"
            I0 = q.convertUnit(fld, k1l, "phy", None)
            dk1l = 0.01 * k1l
            dI = q.convertUnit(fld, k1l+dk1l, "phy", None) - I0
        else:
            fld, I0, dI = sp[i]
            dk1l = q.convertUnit("b1", I0+dI, None, "phy") - \
                q.convertUnit("b1", I0, None, "phy")
        if unitsys is None:
            fac = dk1l/dI
        elif unitsys == "phy":
            fac = 1.0
        else:
            raise RuntimeError("Unknow unitsys={0}".format(unitsys))
        m[0,i] =  bta[i,0]/4.0/np.pi * fac
        m[1,i] = -bta[i,1]/4.0/np.pi * fac
    return m


def calcBetaBeatRm(bpms, quads, **kwargs):
    """
    M_ij = d(db/b)_i/dkl_j

    db/b is measured at BPMs.

    db/b = -\sum dkl_j*\beta_j\cos(2\nu_0(\pi+phi_i-phi_j)

    where phi_i is the phase normalized within 2\pi range.

    See. S.Y. Lee Chap 2.III
    """
    NBPM, NQUAD = len(bpms), len(quads)
    m = np.zeros((NBPM * 2, NQUAD), 'd')
    tunes = getTunes(source="database")
    twcols = ['s', 'betax', 'betay', 'phix', 'phiy']
    twbpm  = getTwissAt([b.se for b in bpms], twcols)
    twquad = getTwissAt([q.se for q in quads], twcols)
    for i in range(NBPM):
        phix0, phiy0 = twbpm[i,3:5]
        for j in range(NQUAD):
            phix1, phiy1 = twquad[i,3:5]
            m[i,j] = -twquad[j,1]/2.0/np.sin(tunes[0]*2*np.pi) * \
                np.cos(2.0*np.pi*tunes[0] + 2*phix0 - 2*phix1)
            m[i+NBPM,j] = twquad[j,2]/2.0/np.sin(tunes[1]*2*np.pi) * \
                np.cos(2.0*np.pi*tunes[1] + 2*phiy0 - 2*phiy1)
    return m


def compareLattice(*argv, **kwargs):
    """
    - group, HDF5 file group, default lattice name
    - sponly, True, compare only the setpoint PVs
    - elements, None, or a list of family names ["QUAD"]
    - ignore, regular expression

    returns same and diff. Each is a list of (pv, values).

    >>> same, diff = compareLattice("file1.hdf5", elements=["QUAD"])
    >>> sm, df = compareLattice("file1.hdf5", elements=["COR", "BPM", "UBPM"])
    >>> sm, df = compareLattice("file1.hdf5", sponly=True)
    >>> sm, df = compareLattice("file1.hdf5", sponly=True, ignore=["SR:.+BPM.*Ampl.*"])
    """
    group = kwargs.get("group", machines._lat.name)
    sponly = kwargs.get("sponly", False)
    elements = kwargs.get("elements", None)
    ignore = kwargs.get("ignore", None)

    # filter the PVs
    if elements is not None:
        pvlst = []
        for fam in elements:
            for e in machines._lat.getElementList(fam):
                pvlst.extend(e.pv())
    else:
        pvlst = None

    dat = {}
    nset = len(argv)
    import h5py
    for i,fname in enumerate(argv):
        h5f = h5py.File(fname, 'r')
        g = h5f[group]
        for pv,val in g.items():
            if pvlst is not None and pv not in pvlst:
                continue
            if sponly and val.attrs.get("setpoint", 0) != 1:
                continue
            if ignore and any([re.match(p,pv) for p in ignore]):
                continue
            dat.setdefault(pv, [])
            if g[pv].dtype in ['float64']:
                dat[pv].append(float(val.value))
            elif g[pv].dtype in ['int32', 'int64']:
                dat[pv].append(int(val.value))
            else:
                print("unknown {0} data type: {1}, value: {2}".format(
                    pv, g[pv].dtype, g[pv].value))
        h5f.close()
    if len(dat) > 0 and kwargs.get("withlive", False):
        pvs = dat.keys()
        vals = caget(pvs)
        for i,pv in enumerate(pvs):
            dat[pv].insert(0, vals[i])
        nset = nset + 1

    same, diff = [], []
    i = 0
    for pv,vals in dat.items():
        i = i + 1
        if len(vals) < nset:
            diff.append([pv, vals])
        elif all([v == vals[0] for v in vals[1:]]):
            same.append([pv, vals])
            continue
        else:
            diff.append([pv, vals])
        #print i, pv, vals
    return same, diff

def waitRamping(elem, **kwargs):
    """
    waiting until elem finished ramping.

    - elem, single element object or list of objects
    - timeout, default 5 seconds.
    - wait, default 0 seconds. Minimal waiting.
    - stop, default 0, stop value. This is related to the ramping command PV.

    >>> cors = getElements("COR")
    >>> cors[0] = 0.0
    >>> waitRamping(cors[0])
    >>> correctOrbit()
    >>> waitRamping(cors)

    For EPICS, It looks at "ramping" field for the elements and wait until all
    of the values equal to *stop*.
    """
    t0 = datetime.now()
    wait = kwargs.get("wait", 0)
    stop = kwargs.get("stop", 0)
    timeout = kwargs.get("timeout", 5)
    dt = kwargs.get("dt", 0.2)

    if wait > 0:
        time.sleep(wait)

    if isinstance(elem, element.CaElement):
        elemlst = [elem]
        pvl = elem.pv(field="ramping")
    elif isinstance(elem, (list, tuple)) and \
            all([isinstance(e, element.CaElement) for e in elem]):
        pvl = reduce(lambda x,y: x + y,
                     [e.pv(field="ramping") for e in elem])


    wdt = caWait(pvl, stop = stop, timeout = timeout, dt = dt)
    if kwargs.get("verbose", 0) > 0:
        print(("waited for ", wdt, (datetime.now() - t0).total_seconds(), "seconds"))

def getBoundedElements(group, s0, s1):
    """
    get list of elements within [s0, s1] or outside.

    group - pattern, name, type, see `getElements`
    s0, s1 - the boundary
    outside - True: inside boundary [s0,s1], False: in [0, s0] or [s1, end]

    if s0 > s1, it will be treated as a ring.

    >>> inside, outside = getBoundedElements("BPM", 700, 100)

    The returned elements are sorted in s order. In the case of s0 > s1, it
    starts from [0, s0] and then [s1, end].
    """

    allelems = getElements(group)
    inside = [False] * len(allelems)
    for i,e in enumerate(allelems):
        # keep the elements fully inside [s0, s1]
        if s1 > s0 and e.sb > s0 and e.se < s1:
            inside[i] = True
        elif s1 < s0 and (e.sb > s0 or e.se < s1):
            inside[i] = True
        else:
            inside[i] = False

    return ([e for i,e in enumerate(allelems) if inside[i]],
            [e for i,e in enumerate(allelems) if not inside[i]])


def saveElement(elem, output, h5group = "/"):
    """
    save element info to HDF5 file *output* in *h5group*
    """
    import h5py
    h5f = h5py.File(output, 'a')
    grp = h5f.require_group(h5group)
    for fld in elem.fields():
        try:
            val = elem.get(fld, handle="setpoint", unitsys=None)
            grp[fld + ".sp"] = val
        except:
            pass
        try:
            val = elem.get(fld, handle="readback", unitsys=None)
            grp[fld + ".rb"] = val
        except:
            pass
    grp.attrs["name"]   = elem.name
    grp.attrs["family"] = elem.family
    grp.attrs["cell"]   = elem.cell
    grp.attrs["girder"] = elem.girder
    h5f.close()


def putElement(elem, output, h5group = "/", force = False):
    """
    put saved element data to hardware
    """
    import h5py
    h5f = h5py.File(output, 'r')
    grp = h5f[h5group]

    if elem.name != grp.attrs["name"]:
        _logger.warn("not same element name: %s != %s" % (
                elem.name, grp.attrs["name"]))
        if not force:
            h5f.close()
            return

    for fld in elem.fields():
        dsname = fld + '.sp'
        if dsname not in grp.keys():
            _logger.warn("%s not found in %s/%s" % (dsname, output, h5group))
            continue
        val = grp[dsname].value
        elem.put(fld, val, unitsys=None)
    h5f.close()


