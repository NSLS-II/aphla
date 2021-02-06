import importlib

from .. import facility_d

_SEL_ENGINE = None
_SEL_ENGINE_NAME = ''

_ENGINES = {}
if 'engines' in facility_d:
    for _engine_name in facility_d['engines']['available']:
        _ENGINES[_engine_name] = None

def avail_names():
    """
    Return all available lattice engine names
    """

    return list(_ENGINES)

def names():
    """
    Return all the loaded lattice engine names
    """

    return [name for name, engine in _ENGINES.items()
            if engine is not None]

def load(engine_name=''):
    """
    Load (import) the selected engine package. If the package is already
    imported, it will NOT reload.
    """

    if engine_name == '':
        # Use the "default", if available. If not, use the first available engine.
        engine_name = facility_d['engines'].get('default', names()[0])

    if engine_name not in _ENGINES:
        raise ValueError((
            f'Specified engine "{engine_name}" is not available.\n'
            f'Use ap.engines.avail_names() to see all available engine names.'))

    try:
        _ENGINES[engine_name] = importlib.import_module(engine_name)
    except:
        print(f'WARNING: Engine "{engine_name}" could NOT be imported')

def use(engine_name):
    """
    Select the specified engine.
    """

    if _ENGINES[engine_name] is None:
        load(engine_name)

    if _ENGINES[engine_name] is None:
        raise RuntimeError(
            f'Cannot use specified engine "{engine_name}" as importing it failed.')
    else:
        global _SEL_ENGINE, _SEL_ENGINE_NAME
        _SEL_ENGINE = _ENGINES[engine_name]
        _SEL_ENGINE_NAME = engine_name

def getEngine():
    """
    Get the currently selected engine (package object).
    """

    return _SEL_ENGINE

def getEngineName():
    """
    Get the currently selected engine name (str).
    """

    return _SEL_ENGINE_NAME
