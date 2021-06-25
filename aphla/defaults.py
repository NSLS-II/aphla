# Based on https://gist.github.com/tmr232/9354077

from functools import wraps
import importlib
import inspect
from pathlib import Path

from ruamel import yaml

_DYNAMIC_DEF_FUNC_PATHS = []
_DEF_DICTS = {}
_DEF_OBJ_DICTS = {}

class Default(object):
    def __init__(self, key, value=None):
        super(Default, self).__init__()
        self.key = key
        self.value = value

    def __repr__(self):

        if isinstance(self.value, str):
            return f'"{self.value}"'
        else:
            return str(self.value)

class DefaultObjLinkedDict(dict):
    def __init__(self, parent_key, *args, **kwargs):
        super(DefaultObjLinkedDict, self).__init__(*args, **kwargs)

        self.parent = parent_key

    def __setitem__(self, item, value):
        super(DefaultObjLinkedDict, self).__setitem__(item, value)

        if item not in _DEF_OBJ_DICTS[self.parent]:
            _DEF_OBJ_DICTS[self.parent] = {item: Default(item)}

        _DEF_OBJ_DICTS[self.parent][item].value = value

def getDynamicDefault(key):
    """
    Useful when you want to change the default values specified in "**kwargs"
    that can change for different facilities.
    """

    return _DEF_DICTS[_DYNAMIC_DEF_FUNC_PATHS[-1]][key]

def set_defaults(func_path):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):

            # Backup original function defaults.
            original_defaults = f.__defaults__

            _DYNAMIC_DEF_FUNC_PATHS.append(func_path)

            # Replace every `Default("...")` argument with its current value.
            function_defaults = []
            for default_value in f.__defaults__:
                if isinstance(default_value, Default):
                    function_defaults.append(default_value.value)
                else:
                    function_defaults.append(default_value)

            # Set the new function defaults.
            f.__defaults__ = tuple(function_defaults)

            return_value = f(*args, **kwargs)

            # Restore original defaults (required to keep this trick working.)
            f.__defaults__ = original_defaults

            _DYNAMIC_DEF_FUNC_PATHS.pop()

            return return_value

        return wrapper

    return decorator

def initialize(yaml_filepath=''):
    """"""

    if yaml_filepath:
        for k, v in yaml.YAML().load(Path(yaml_filepath).read_text()).items():
            _DEF_DICTS[k] = v

    for func_path, d in _DEF_DICTS.items():

        *parent, func_name = func_path.split('.')
        mod_name = '.'.join(parent)
        m = importlib.import_module(mod_name)
        func = getattr(m, func_name)

        spec = inspect.getfullargspec(func.__wrapped__)

        nposargs = len(spec.args) - len(spec.defaults)

        if func_path not in _DEF_OBJ_DICTS:
            _DEF_OBJ_DICTS[func_path] = {}

        for k, v in d.items():
            if k in spec.args:
                i = spec.args.index(k) - nposargs
                def_obj = spec.defaults[i]
            elif k in spec.kwonlyargs:
                i = spec.kwonlyargs.index(k)
                def_obj = spec.kwonlydefaults[i]
            else:
                continue

            def_obj.value = v

            if k not in _DEF_OBJ_DICTS[func_path]:
                _DEF_OBJ_DICTS[func_path][k] = def_obj