"""
:author: Lingyun Yang, Yoshiteru Hidaka
:license: 

``aphla`` is a set accelerator physics high level applications and scripts. 

an object-orient high level accelerator control library.

A procedural interface is provided.

"""

from __future__ import print_function

__version__ = "Unknow"
try:
    from version import version as __version__
except:
    pass

import os
import tempfile
import logging

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
_lgfmt = logging.Formatter("%(asctime)s - %(name)s [%(levelname)s]: %(message)s")
# set null handler when logging for a library.
_lghdl = _NullHandler()
_lghdl.setLevel(logging.INFO)
_lghdl.setFormatter(_lgfmt)
logging.getLogger('aphla').addHandler(_lghdl)

def enableLog(f = "aphla.log", level=logging.DEBUG):
    _lgh = logging.FileHandler(f)
    _lgh.setLevel(level)
    _lgh.setFormatter(_lgfmt)
    logging.getLogger('aphla').addHandler(_lgh)

#

from catools import *
from chanfinder import *
import machines
from hlalib import *
from apdata import OrmData

from meastwiss import *
from aptools import *

import bba

# Added by Y. Hidaka
# require newer version of scipy, not available in controls terminal yet.
#import curve_fitting

import contrib

import gui
