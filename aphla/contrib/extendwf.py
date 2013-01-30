#!/usr/bin/env python
# -*- coding: utf-8 -*-

from numpy import *
import os
import commands

import time
import datetime
import re
import string
import sys

# python 
'''
from extendwf import *
outputwf=extendwf(Nwflength,inputwf)
Nwflength:output waveform length to be extended to,inputwf: input waveform,outputwf: return output waveform with length Nwflength)
'''

def extendwf(Nwflength,inputwf):
        '''
	extend input array length to length Nwflength by setting the  

	from extendwf import *
	outputwf=extendwf(Nwflength,inputwf)

	Nwflength:output waveform length to be extended to,inputwf: input waveform,
	outputwf: return output waveform with length Nwflength)
	'''
	outputwf=zeros(Nwflength)
	Nin=len(inputwf)
	for i in range(Nwflength):
		if i<Nin:
			outputwf[i]= inputwf[i]
		else:
			outputwf[i]= inputwf[Nin-1]

	print outputwf

	return outputwf
