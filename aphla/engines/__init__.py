import os
import json
import importlib
from enum import Enum

from .. import facility_d

_sel_engine = None

_engines = {}
if 'engines' in facility_d:
    for _engine_name in facility_d['engines']:
        _engines[_engine_name] = None

def names():
    """
    Return all available lattice engine names
    """

    return list(_engines)

def load(engine_name):
    """
    Load (import) the selected engine package. If the package is already
    imported, it will NOT reload.
    """

    if engine_name not in _engines:
        raise ValueError((
            f'Specified engine "{engine_name}" is not available.\n'
            f'Use ap.engines.names() to see all available engine names.'))

    try:
        _engines[engine_name] = importlib.import_module(engine_name)
    except:
        print(f'WARNING: Engine "{engine_name}" could NOT be imported')

def use(engine_name):
    """
    Select the specified engine.
    """

    if _engines[engine_name] is None:
        load(engine_name)

    if _engines[engine_name] is None:
        raise RuntimeError(
            f'Cannot use specified engine "{engine_name}" as importing it failed.')
    else:
        global _sel_engine
        _sel_engine = _engines[engine_name]

def getEngine():
    """
    Get the currently selected engine (package object).
    """

    return _sel_engine
