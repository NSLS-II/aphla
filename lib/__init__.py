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

__version__ = "0.3.0b4"


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
logging.basicConfig(filename=APHLA_LOG,
    format='%(asctime)s - %(name)s [%(levelname)s]: %(message)s',
    level=logging.DEBUG)
# set null handler when logging for a library.
_hdl = NullHandler()
logging.getLogger('aphla').addHandler(_hdl)

#
from catools import *
from chanfinder import ChannelFinderAgent
from machines import initNSLS2VSR, initNSLS2VSRTwiss, initNSLS2

#from rf import *
from hlalib import *
from ormdata import OrmData

from meastwiss import *
from measorm import *
from aptools import *

import bba


# Added by Y. Hidaka
# require newer version of scipy, not available in controls terminal yet.
#import curve_fitting

