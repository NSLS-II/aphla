"""
:author: Lingyun Yang, Yoshiteru Hidaka
:license: 

``aphla`` is a set accelerator physics high level applications and scripts. 

an object-orient high level accelerator control library.

A procedural interface is provided.

"""

from __future__ import print_function

__version__ = "0.8.32"
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
_lgfmt = logging.Formatter(
    "%(asctime)s - %(name)s [%(levelname)s]: %(message)s")
# set null handler when logging for a library.
_lghdl = _NullHandler()
_lghdl.setLevel(logging.INFO)
_lghdl.setFormatter(_lgfmt)
# logging.getLogger('aphla').addHandler(_lghdl)

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

from catools import *
from chanfinder import *
import machines
from hlalib import *
from apdata import OrmData

from meastwiss import *
from aptools import *
from tbtanal import *
import snapshot

import bba

# Added by Y. Hidaka
# require newer version of scipy, not available in controls terminal yet.
#import curve_fitting

#import contrib

# it's better to import this package separately
#import gui

import nsls2
#import nsls2br
import nsls2id
