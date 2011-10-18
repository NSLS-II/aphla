Tutorial
=========

.. htmlonly::
   :Date: |today|


The HLA and Controls are divided into three layers: HLA applictions and
scripts, client APIs (CAPI) and server API (SAPI) ([Shenhla]_).  The users
(accelerator physicists, operators and beamline scientists) will normally
access the first two forms: use applications/scripts by mouse clicks, and
the APIs in an interactive command line.


Some APIs are defined in [Shenhla]_, and are used by HLA applications. But they
are self-described as the standard Python modules. These APIs include data
acquisition, processing and storage, and can be combined for different
purpose. The APIs are in Python language, and can be used in both interactive
environment or scripts. Necessary packages including linear algebra, frequency
analysis, statistics, data IO, database, network, regular expression and
visualization will be provided. See `Python <http://www.python.org>`_, `SciPy
<http://www.scipy.org>`_, `NumPy <http://numpy.scipy.org/>`_, `iPython
<http://ipython.scipy.org>`_, `matplotlib
<http://matplotlib.sourceforge.net>`_.


The HLA applications are those have a stable algorithm and data
flow. Each is in a standalone form.

.. warning::

   Some notes:

   - channel finder, ordinal/elemName/elemType should be
     matched. i.e. once the elemName is known, its ordinal and elemType is
     know. It is one-to-one.


.. _Accelerator Physics Toolkit:

Accelerator Physics Toolkit
-----------------------------

By toolkit, we mean a short script based on CAPIs. Not like HLAs, they
have small set of functions, but easy to understand and modify. For
example we put a small script *probeBpmStability* into this category,
since it is mainly a function call of *getBpmVariance* plus checking
against certain criterial.

One interactive *Python* environment is also provided for
interactive control of the storage ring. In this interactive
environment, a set of APIs are provided to help physicists who has no
knowledge of EPICS or low level channel access be able to do many
measurements and diagnostics.

This interactive mode can also run as batch mode, which makes the
prototyping of new HLA and algorithms easier.

The plotting features are only in interactive environment and GUI
applications. Scripts and save pictures in *png*, *jpeg*,
*pdf* and *eps* format.



HLA Initialization
-------------------

Import some modules, including HLA and plotting routines

.. note::

   The text after '#' are comments for that line

Import modules:

.. doctest::

   >>> import hla
   >>> import numpy as np
   >>> import matplotlib.pylab as plt
   >>> import time

Initialize the NSLS2 Virtual Storage Ring lattice and twiss (from channel
finder server):

.. doctest::

   >>> hla.initNSLS2VSR()
   >>> hla.initNSLS2VSRTwiss()

if the network is not available and a copy of
text-version-channel-finder-server data is in local machine, we can
initialize HLA by the following command:

.. doctest::

   >>> hla.machines.initNSLS2VSRTxt()
   Creating lattice layout: 'SR-txt'
   Creating lattice layout: 'LTB-txt'
   Creating lattice layout: 'LTD2-txt'
   Creating lattice layout: 'LTD1-txt'
   >>> hla.machines.use('SR-txt') # use 'LTB-txt', 'LTD1-txt' or 'LTD2-txt' for injction.
   >>> hla.machines.lattices()    # list available lattices
   {'SR': 'aphla.sys.SR', 'LTD2': 'aphla.sys.LTD2', 'LTB': 'aphla.sys.LTB', 'LTD1': 'aphla.sys.LTD1', 'LTB-txt': 'LTB-txt', 'LTD1-txt': 'txt', 'LTD2-txt': 'txt', 'SR-txt': 'SR-text-ver'}



HLA Element Searching
---------------------

The lattice is merely a list of elements. In order to control the element,
we first get the instance from lattice by :func:`~hla.hlalib.getElements`
providing with element name, type or pattern.

Here are some examples:

.. doctest::

   >>> bpm = hla.getElements('BPM') # get a list of BPMs
   >>> len(bpm) # 180 in tital, guaranteed in increasing order of s coordinate.
   180
   >>> bpm[0].name
   u'PH1G2C30A'
   >>> bpm[0].family, bpm[0].cell, bpm[0].girder
   (u'BPM', u'C30', u'G2')

.. index:: family, cell, girder, symmetry, group
.. index::
   single: property; family
   single: property; girder
   single: property; cell
   single: property; symmetry

Each element has a set of properties associated:

- *family* (element type). e.g. 'QUAD', 'BPM'
- *cell*. The DBA cell it belongs. e.g. 'C02', 'C30'
- *girder*, girder name where it sits. e.g. 'G2', 'G1'
- *symmetry*, 'A' or 'B' symmetry
- *group*. A BPM in girder 2 cell 2 could be in group 'C02', 'G2', 'BPM'
  and more. *family*, *cell*, *girder* and *symmetry* are special named
  groups.

A element can only belongs to one *family*, *cell*, *girder* and
*symmetry*. But it can be in many groups:

.. doctest::

   >>> hla.getGroups('PM1G4C02B') # the groups one element belongs to
   [u'BPM', u'C02', u'G4', u'B']

To find the elements in certain cell or/and girder, use *getGroupMembers* and
take *union* or *intersection* of them.

.. doctest::

   >>> el = hla.getGroupMembers(['BPM', 'C15', 'G4'], op='intersection')
   >>> for e in el: print e.name, e.sb, e.length
   PM1G4C15A 407.882 0.0
   PM1G4C15B 410.115 0.0

This gets all BPMs in girder 4 of cell 15.

.. doctest::

   >>> el = hla.getGroupMembers(['BPM', 'C0[2-3]', 'G2'])
   >>> for e in el: print e.name, e.sb, e.cell, e.girder, e.symmetry
   PH1G2C02A 57.7322 C02 G2 A
   PH2G2C02A 60.2572 C02 G2 A
   PL1G2C03A 82.7858 C03 G2 A
   PL2G2C03A 85.3495 C03 G2 A

This gets all BPMs in the girder 2 of cell 2 and 3.

A pattern matching is also possible when searching for element or groups

.. doctest::

   >>> hla.getElements('P*C01*A')
   [<hla.element.Element at 0x3fafdd0>,
    <hla.element.Element at 0x40c0190>,
    <hla.element.Element at 0x40c0250>]
   >>> hla.getGroups('P*C01*A')
   [u'BPM', u'C01', u'G4', u'G2', u'A']


HLA Element Control
---------------------

   >>> print hla.eget('PL1G2C05A') #doctest: +SKIP
   [[-0.0001042862911482232, 9.4271237903876306e-05]]
   >>> el = hla.getElements(['SQMG4C05A', 'QM2G4C05B', 'CXH2G6C05B', 'PM1G4C05A'])
   >>> for e in el: print e.status #doctest: +SKIP
   SQMG4C05A
     READBACK (SR:C05-MG:G04A{SQuad:M1}Fld-I): 0.0
   QM2G4C05B
     READBACK (SR:C05-MG:G04B{Quad:M2}Fld-I): 1.22232651254
   CXH2G6C05B
     READBACK (SR:C05-MG:G06B{HCor:H2}Fld-I): 0.0
   PM1G4C05A
     READBACK (SR:C05-BI:G04A{BPM:M1}SA:X-I): 0.00024594511233
     READBACK (SR:C05-BI:G04A{BPM:M1}SA:Y-I): 5.06446641306e-05
     READBACK (SR:C05-BI:G04A{BPM:M1}BBA:X): 0.0
     READBACK (SR:C05-BI:G04A{BPM:M1}BBA:Y): 0.0

   >>> for e in el: print e.name, e.pv('eget'), e.value #doctest: +SKIP
   SQMG4C05A [u'SR:C05-MG:G04A{SQuad:M1}Fld-I'] 0.0
   QM2G4C05B [u'SR:C05-MG:G04B{Quad:M2}Fld-I'] 1.22232651254
   CXH2G6C05B [u'SR:C05-MG:G06B{HCor:H2}Fld-I'] 0.0
   PM1G4C05A [u'SR:C05-BI:G04A{BPM:M1}SA:X-I', u'SR:C05-BI:G04A{BPM:M1}SA:Y-I'] [0.00024599597546417758, 5.0644899005954578e-05]
   
It is easy to read/write the default value of an element:

.. doctest::

   >>> e = hla.getElements('CXH2G2C30A')
   >>> print e.status #doctest: +SKIP
   CXH2G2C30A
     READBACK (SR:C30-MG:G02A{HCor:H2}Fld-I): 0.0
     SETPOINT aphla.eput (SR:C30-MG:G02A{HCor:H2}Fld-SP): 1e-07
     READBACK (SR:C30-MG:G02A{HCor:H2}Fld-I): 9.9982402533e-08
     SETPOINT (SR:C30-MG:G02A{HCor:H2}Fld-SP): 1e-07

   >>> print e.value #doctest: +SKIP
   0.0
   >>> e.value = 1e-7 #doctest: +SKIP
   >>> e.value #doctest: +SKIP
   9.998240253299763e-08


More Examples
--------------


.. doctest::

   >>> hla.getCurrent() #doctest: +SKIP
   292.1354803937125

   >>> hla.getLifetime() #doctest: +SKIP
   7.2359460167254399


Plotting the orbit
 
.. doctest::
 
   >>> sobt = hla.getOrbit(spos = True)
   >>> plt.clf()
   >>> plt.plot(sobt[:,2], sobt[:,0], '-x', label='X') #doctest: +ELLIPSIS
   [<matplotlib.lines.Line2D object at 0x...>]
   >>> plt.plot(sobt[:,3], sobt[:,1], '-o', label='Y') #doctest: +ELLIPSIS
   [<matplotlib.lines.Line2D object at 0x...>]
   >>> plt.xlabel('S [m]') #doctest: +ELLIPSIS
   <matplotlib.text.Text object at 0x...>
   >>> plt.savefig('hla_tut_orbit.png')

.. image:: hla_tut_orbit.png

Twiss parameters

.. doctest::

   >>> hla.getBeta('P*G2*C03*A') #doctest: +ELLIPSIS 
   array([[  8.7...,  11.6...],
   	  [ 10.2...,  22.1...]])

   >>> bpm = hla.getElements('P*G2*C03*A')
   >>> hla.getBeta([e.name for e in bpm]) #doctest: +ELLIPSIS
   array([[  8.7...,  11.6...],
   	  [ 10.2...,  22.1...]])

   >>> hla.getBeta('P*G2*C03*A', loc='b') #doctest: +ELLIPSIS
   array([[  8.7...,  11.6...],
   	  [ 10.2...,  22.1...]])

Plotting the beta function of cell 'C02' and 'C03'

.. doctest::

   >>> elem = hla.getGroupMembers(['C01', 'C02'], op='union')
   >>> beta = hla.getBeta([e.name for e in elem], spos=True, clean=True)
   >>> eta = hla.getDispersion([e.name for e in elem], spos=True, clean=True)
   >>> plt.clf()
   >>> fig1 = plt.subplot(211)
   >>> fig=plt.plot(beta[:,-1], beta[:,:-1], '-o', label=r'$\beta_{x,y}$')
   >>> fig2 = plt.subplot(212)
   >>> fig=plt.plot(eta[:,-1], eta[:,:-1], '-o', label=r'$\eta_{x,y}$')
   >>> plt.savefig("hla_tut_twiss_c0203.png")


.. image:: hla_tut_twiss_c0203.png


Correct the orbit and plot the orbits before/after the correction:

.. doctest::

   >>> print hla.__path__ #doctest: +SKIP
   >>> bpm = hla.getElements('P*C1[0-3]*')
   >>> trim = hla.getGroupMembers(['*', '[HV]COR'], op='intersection')
   >>> print len(bpm), len(trim) #doctest: +SKIP
   >>> v0 = hla.getOrbit('P*', spos=True)
   >>> hla.correctOrbit([e.name for e in bpm], [e.name for e in trim])
   >>> time.sleep(4)
   >>> v1 = hla.getOrbit('P*', spos=True)
   >>> plt.clf()
   >>> ax = plt.subplot(211) 
   >>> fig = plt.plot(v0[:,-1], v0[:,0], 'r-x', label='X') 
   >>> fig = plt.plot(v0[:,-1], v0[:,1], 'g-o', label='Y')
   >>> ax = plt.subplot(212)
   >>> fig = plt.plot(v1[:,-1], v1[:,0], 'r-x', label='X')
   >>> fig = plt.plot(v1[:,-1], v1[:,1], 'g-o', label='Y')
   >>> plt.savefig("hla_tut_orbit_correct.png")

.. image:: hla_tut_orbit_correct.png

.. doctest::

   >>> hla.getChromaticity() #doctest:+SKIP

.. math::

  G(s,s_0)=\dfrac{\sqrt{\beta(s)\beta(s_0)}}{2\sin\pi\nu}\cos(\pi\nu-\left|\psi(s)-\psi(s_0)\right|)

