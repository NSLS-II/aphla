#!/usr/bin/env python


"""
APHLA Module
-----------

This is an object-orient high level accelerator control library.

A procedural interface is provided.

   
:author: Lingyun Yang
:license:

Modules include:

    :mod:`aphla.machines`

        define machine specific settings, create lattice from channel
        finder service for different accelerator complex.

    :mod:`aphla.lattice`

        define the :class:`~aphla.lattice.CaElement`, :class:`~aphla.lattice.Twiss`,
        :class:`~aphla.lattice.Lattice` class

    :mod:`aphla.orbit`

        defines orbit retrieve routines

    :mod:`aphla.hlalib`

        defines procedural interface
        
"""

from __future__ import print_function

__version__ = "0.7.0"


import os
import tempfile
import logging

# for compatibilities with Python < 2.7
class NullHandler(logging.Handler):
    """a fix for Python2.6 where no NullHandler"""
    def emit(self, record):
        pass

#APHLA_LOG = os.path.join(tempfile.gettempdir(), "aphla.log")
APHLA_LOG = 'aphla.log'
#logging.basicConfig(filename=APHLA_LOG,
#    format='%(asctime)s - %(name)s [%(levelname)s]: %(message)s',
#    level=logging.DEBUG)
_lgfmt = logging.Formatter("%(asctime)s - %(name)s [%(levelname)s]: %(message)s")
# set null handler when logging for a library.
_lghdl = NullHandler()
_lghdl.setLevel(logging.DEBUG)
_lghdl.setFormatter(_lgfmt)
logging.getLogger('aphla').addHandler(_lghdl)

#

from catools import (caget, caput, caputwait)
from chanfinder import ChannelFinderAgent
#from machines import (
#    initNSLS2V2, initNSLS2, initTLS, initNSLS2V3BSRLine
#    )

#from rf import *
import machines
from hlalib import *
from ormdata import OrmData

from meastwiss import *
from aptools import *

import bba

#import machines

# Added by Y. Hidaka
# require newer version of scipy, not available in controls terminal yet.
#import curve_fitting


