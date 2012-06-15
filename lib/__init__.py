#!/usr/bin/env python

from __future__ import print_function


"""
HLA Module
-----------

This is an object-orient high level accelerator control library.

A procedural interface is provided.

   
:author: Lingyun Yang
:license:

Modules include:

    :mod:`hla.machines`

        define machine specific settings, create lattice from channel
        finder service for different accelerator complex.

    :mod:`hla.lattice`

        define the :class:`~hla.lattice.CaElement`, :class:`~hla.lattice.Twiss`,
        :class:`~hla.lattice.Lattice` class

    :mod:`hla.orbit`

        defines orbit retrieve routines

    :mod:`hla.hlalib`

        defines procedural interface
        
"""

__version__ = "0.3.0b3"


import logging

logging.basicConfig(filename="aphla.log",
    filemode='w',
    format='%(asctime)s - %(name)s [%(levelname)s]: %(message)s',
    level=logging.DEBUG)
logger = logging.getLogger(__name__)

from catools import *
from machines import initNSLS2VSR, initNSLS2VSRTwiss

from rf import *
from hlalib import *
from ormdata import OrmData

from aptools import *

import bba
import meastwiss


# Added by Y. Hidaka
import curve_fitting
import current

