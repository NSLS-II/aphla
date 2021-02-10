"""
:author: Lingyun Yang, Yoshiteru Hidaka
:license:

``aphla`` is a set accelerator physics high level applications and scripts.

an object-orient high level accelerator control library.

A procedural interface is provided.

"""

from __future__ import print_function, division, absolute_import

try:
    from .version import version as __version__
except:
    raise

import os
import tempfile
import logging
from pathlib import Path

from ruamel import yaml

# for compatibilities with Python < 2.7
class _NullHandler(logging.Handler):
    """a fix for Python2.6 where no NullHandler"""
    def emit(self, record):
        pass

#APHLA_LOG = os.path.join(tempfile.gettempdir(), "aphla.log")
#APHLA_LOG = 'aphla.log'
#logging.basicConfig(filename=APHLA_LOG,
#    format='%(asctime)s - %(name)s [%(levelname)s]: %(message)s',
#    level=logging.DEBUG)
_lgfmt = logging.Formatter(
    "%(asctime)s - %(name)s [%(levelname)s]: %(message)s")
# set null handler when logging for a library.
_lghdl = _NullHandler()
_lghdl.setLevel(logging.INFO)
_lghdl.setFormatter(_lgfmt)
logging.getLogger('aphla').addHandler(_lghdl)

def enableLog(f = "aphla.log", level=logging.INFO):
    # print(logging.getLogger())
    # print(logging.getLogger().handlers)
    from logging.handlers import RotatingFileHandler
    _lgh = RotatingFileHandler(f, maxBytes=100*1024*1024)
    _lgh.setLevel(level)
    _lgh.setFormatter(_lgfmt)
    _lg = logging.getLogger("aphla")
    _lg.setLevel(level)
    _lg.propagate = 0 # do not propagate to parent logger, too much for IPython Notebook
    _lg.addHandler(_lgh)

#

class OperationMode():

    ONLINE = 0
    SIMULATION = 1

    def __init__(self, value=0):
        """"""

        self.value = value

    @property
    def value(self):
        """"""

        return self._value

    @value.setter
    def value(self, new_value):
        """"""

        if new_value not in (self.ONLINE, self.SIMULATION):
            raise ValueError(f'Valid values are {self.ONLINE} or {self.SIMULATION}.')

        self._value = new_value

    def __repr__(self):

        if self._value == self.ONLINE:
            return 'ONLINE'
        else:
            return 'SIMULATION'

    def _get_valid_str_values(self):
        """"""

        return ['ONLINE', 'SIMULATION']


OP_MODE = OperationMode(OperationMode.ONLINE)

def get_op_mode():
    """"""

    return OP_MODE.value

def set_op_mode(new_mode_value):
    """"""

    OP_MODE.value = new_mode_value

def get_op_mode_str():
    """"""

    return OP_MODE.__repr__()

def set_op_mode_str(new_mode_str):
    """"""

    upper_new_mode_str = new_mode_str.upper()

    if hasattr(OP_MODE, upper_new_mode_str):
        OP_MODE.value = getattr(OP_MODE, upper_new_mode_str)
    else:
        valid_str = ', '.join([f'"{s}"' for s in OP_MODE._get_valid_str_values()])
        raise ValueError(
            f'Invalid string: "{upper_new_mode_str}" '
            f'(Valid str values are {valid_str})')

this_folder = os.path.dirname(os.path.abspath(__file__))
facility_d = yaml.YAML().load(Path(this_folder).joinpath('facility.yaml').read_text())
facility_name = facility_d['name']

from .catools import *
from .chanfinder import *
from . import machines
from . import engines
from . import models
from .hlalib import *
from .apdata import OrmData

from .meastwiss import *
from .aptools import *
from .tbtanal import *
from . import snapshot

from . import bba

# Added by Y. Hidaka
# require newer version of scipy, not available in controls terminal yet.
#import curve_fitting

#import contrib

# it's better to import this package separately
#import gui

if facility_name == 'nsls2':
    from . import nsls2
    #from . import nsls2br
    from . import nsls2id
