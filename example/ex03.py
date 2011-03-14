#!/usr/bin/env python

"""
An example of local bump

:author: Lingyun Yang
:date: 2011-03-10
"""


import hla
import matplotlib.pylab as plt
from math import *
import numpy as np

if __name__ == '__main__':
    # initialize when no real machine exists
    hla.clean_init()

    trim1 = 'CYM1G4C30B'
    trim = [t[0] for t in hla.getNeighbors(trim1, 'TRIMY', 3)][3:]
    theta1 = 3e-5
    theta2 = 1e-5
    
    #trim.insert(0, trim1)
    #print trim
    beta = hla.getBeta(trim)
    phi = hla.getPhase(trim)
    #print beta, phi
    # orbit at cell 3-6 BPMs
    theta3 =-(sqrt(beta[0][1])*theta1*sin(phi[3][1] - phi[0][1]) + \
                  +sqrt(beta[1][1])*theta2*sin(phi[3][1] - phi[1][1]))/\
                  sin(phi[3][1] - phi[2][1])/sqrt(beta[2][1])
    theta4 =(sqrt(beta[0][1])*theta1*sin(phi[2][1] - phi[0][1]) + \
                  +sqrt(beta[1][1])*theta2*sin(phi[2][1] - phi[1][1]))/\
                  sin(phi[3][1] - phi[2][1])/sqrt(beta[3][1])
    
    hla.eput(trim, [theta1, theta2, theta3, theta4])

    #eta0 = hla.getDispersion('P*C0[3-6]*')

    #plt.clf()
    #plt.plot(s1, eta0, 'x-')
    #plt.savefig('test.png')
