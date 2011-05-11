Tutorial
=========

The HLA and Controls are divided into three layers: HLA applictions and
scripts, client APIs (CAPI) and server API (SAPI)~([Shen]_).  The users
(accelerator physicists, operators and beamline scientists) will normally
access the first two forms: use applications/scripts by mouse clicks, and
the APIs in an interactive command line.


APIs are defined in [Shen]_, and are used by HLA applications. They
include data acquisition, processing and storage, and can be combined for
different purpose. The APIs are in Python language, and can be used in
both interactive environment or scripts. Necessary packages including
linear algebra, frequency analysis, statistics, data IO, database,
network, regular expression and visualization will be provided. See
`Python <http://www.python.org>`_, `SciPy <http://www.scipy.org>`_, `NumPy
<http://numpy.scipy.org/>`_, `iPython <http://ipython.scipy.org>`_,
`matplotlib <http://matplotlib.sourceforge.net>`_.


The HLA applications are those have a stable algorithm and data
flow. Each is in a standalone form.


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
environment, a set of APIs are provided to make physicists who has no
knowledge of EPICS or low level channel access be able to do many
measurements and diagnostics.

This interactive mode can also run as batch mode, which makes the
prototyping of new HLA and algorithms easier.

The plotting features are only in interactive environment and GUI
applications. Scripts and save pictures in *png*, *jpeg*,
*pdf* and *eps* format.

Since the CAPIs (client APIs) are from requirement analysis of NSLS-II
commissioning plan, we can describe those accelerator physics tasks and
the related APIs (both client and server).



A set of API should be provided to allow physicists to fetch data from
circular buffer of related sub-system, especially diagnostic
instrument, and RF. Detailed requirement can be found in [Shencbd]_.




Software
-----------

::

  $ apt-get install mercurial pyqt4-dev-tools
  $ apt-get install python-qt4 python-qt4-dev

By using BNL Debian/Ubuntu repository fron Controls group

::

  deb http://epics.nsls2.bnl.gov/debian/ lenny main contrib
  deb-src http://epics.nsls2.bnl.gov/debian/ lenny main contrib

::

  $ apt-get install python-cothread epics-catools

Set environment for channel access, append to ~/.bashrc::

  export EPICS_CA_MAX_ARRAY_BYTES=500000
  export EPICS_CA_ADDR_LIST=virtac.nsls2.bnl.gov

Try to see if virtual accelerator is accessible::

  $ caget 'SR:C00-BI:G00{DCCT:00}CUR-RB'

You should see the beam current of virtual accelerator. Then see if it changes::

  $ camonitor 'SR:C00-BI:G00{DCCT:00}CUR-RB'


Code Repository
-------------------

Our code is in a Mercurial repository, which keeps every version anyone
checked in. Version controlled repository not only keeps track of the
change of the code, but also support branch and merges of each revision.

I will skip the introduction of the version control tools and only talk
about what/how you should do to work with the HLA code in repository.

A typical work flow is the following. (All under linux)

The very first time, please take a look at ~/.hgrc:

::

  [ui]
  username = Lingyun Yang <lyyang@bnl.gov>

This marks who you are.

::

  $ hg clone http://code.nsls2.bnl.gov/hg/nsls2-hla
  $ cd nsls2-hla
  $ (working .....)
  $ hg add newfile.py (if you have created a new file)
  $ hg status  ( list the status of current working directory)
  $ hg commit -m "I have improved the code" (check in the code with a message)
  $ hg push (push you change to the server)

If it has been a long time after you checkout the code from the server, you can 

::

  $ hg pull (update the local files with server's)



Examples
--------------

First import some modules, including HLA and plotting routines

.. note::

   The text after '#' are comments for that line


.. doctest::

   >>> import hla
   >>> import numpy as np
   >>> import matplotlib.pylab as plt
   >>> import time

Then is the examples:

.. doctest::

   >>> hla.getElements('BPM', cell='C02')
   ['PH1G2C02A', 'PH2G2C02A', 'PM1G4C02A', 'PM1G4C02B', 'PL2G6C02B', 'PL1G6C02B']

Each element has a set of properties associated:

- *family* (element type). e.g. 'QUAD', 'BPMX'
- *cell*. The DBA cell it belongs. e.g. 'C02', 'C30'
- *girder*, girder name where it sits. e.g. 'G2', 'G1'
- *symmetry*, 'A' or 'B' symmetry
- *group*. One element belongs to many groups. e.g. 'BPMX', 'BPM'

A element can only belongs to one *family*, *cell*, *girder* and *symmetry*. But it can be in many groups:

   >>> hla.getGroups('PM1G4C02B')
   ['BPM', 'G4', 'BPMY', 'BPMX', 'C02', 'B']

   >>> hla.getElements('BPMX', cell='C15', girder='G4')
   ['PM1G4C15A', 'PM1G4C15B']

   >>> hla.getElements('C02', girder='G2')
   ['SH1G2C02A', 'PH1G2C02A', 'QH1G2C02A', 'SQHG2C02A', 'CXHG2C02A', 'CYHG2C02A', 'QH2G2C02A', 'SH3G2C02A', 'QH3G2C02A', 'PH2G2C02A', 'SH4G2C02A', 'CXH2G2C02A', 'CYH2G2C02A']

   >>> bpm = hla.getElements('BPM')
   >>> s = hla.getLocations(bpm, 'e')
   >>> for i in range(120,132): print "%.4f %s" % (s[i], bpm[i])
   532.9070 PH1G2C20A
   535.4320 PH2G2C20A
   541.1170 PM1G4C20A
   543.3490 PM1G4C20B
   548.2190 PL2G6C20B
   550.7830 PL1G6C20B
   557.9610 PL1G2C21A
   560.5240 PL2G2C21A
   566.2740 PM1G4C21A
   568.5060 PM1G4C21B
   573.3090 PH2G6C21B
   575.8340 PH1G6C21B

   >>> hla.getGroups('P*C01*A')
   ['BPM', 'A', 'C01', 'G4', 'G2', 'BPMY', 'BPMX']

   >>> hla.getCurrent() #doctest: +SKIP
   292.1354803937125

   >>> hla.getLifetime() #doctest: +SKIP
   7.2359460167254399

   >>> print hla.eget('PL1G2C05A') #doctest: +SKIP
   [[-0.0001042862911482232, 9.4271237903876306e-05]]
   >>> print hla.eget(['SQMG4C05A', 'QM2G4C05B', 'CXH2G6C05B', 'PM1G4C05A']) #doctest: +SKIP
   [0.0, 1.222326512542153, 0.0, [0.0002459691616303813, 5.0642830477320241e-05]]

   
Plotting the orbit

.. doctest::
   >>> sobt = hla.getOrbit(spos = True)
   >>> plt.clf()
   >>> plt.plot(sobt[:,0], sobt[:,1], '-x', label='X') #doctest: +ELLIPSIS
   [<matplotlib.lines.Line2D object at 0x...>]
   >>> plt.plot(sobt[:,0], sobt[:,2], '-o', label='Y') #doctest: +ELLIPSIS
   [<matplotlib.lines.Line2D object at 0x...>]
   >>> plt.xlabel('S [m]') #doctest: +ELLIPSIS
   <matplotlib.text.Text object at 0x...>
   >>> plt.savefig('hla_tut_orbit.png')

.. image:: hla_tut_orbit.png

Twiss parameters

.. doctest::

   >>> hla.getBeta('P*G2*C03*A')
   array([[  8.71242537,  11.67212006],
   	  [ 10.27574586,  22.11703928]])

   >>> bpm = hla.getElements('P*G2*C03*A')
   >>> hla.getBeta(bpm)
   array([[  8.71242537,  11.67212006],
   	  [ 10.27574586,  22.11703928]])

   >>> hla.getBeta('P*G2*C03*A', loc='b')
   array([[  8.71242537,  11.67212006],
   	  [ 10.27574586,  22.11703928]])

Plotting the beta function of cell 'C02' and 'C03'

.. doctest::

   >>> elem = hla.getElements('*', cell=['C01', 'C02'])
   >>> s = hla.getLocations(elem)
   >>> beta = hla.getBeta(elem)
   >>> eta = hla.getDispersion(elem)
   >>> plt.clf()
   >>> fig1 = plt.subplot(211)
   >>> fig=plt.plot(s, beta, '-o', label=r'$\beta_{x,y}$')
   >>> fig2 = plt.subplot(212)
   >>> fig=plt.plot(s, eta, '-o', label=r'$\eta_{x,y}$')
   >>> plt.savefig("hla_tut_twiss_c0203.png")


.. image:: hla_tut_twiss_c0203.png


Correct the orbit and plot the orbits before/after the correction:

.. doctest::

   >>> s = hla.getLocations('P*')
   >>> bpm = hla.getElements('P*C1[0-9]*')
   >>> trim = hla.getGroupMembers(['*', 'TRIMX'], op='intersection')
   >>> v0 = hla.getOrbit()
   >>> hla.correctOrbit(bpm, trim)
   >>> time.sleep(3)
   >>> v1 = hla.getOrbit()
   >>> plt.clf()
   >>> ax = plt.subplot(211) 
   >>> fig = plt.plot(s, v0[:,0], 'r-x', label='X') 
   >>> fig = plt.plot(s, v0[:,1], 'g-o', label='Y')
   >>> ax = plt.subplot(212)
   >>> fig = plt.plot(s, v1[:,0], 'r-x', label='X')
   >>> fig = plt.plot(s, v1[:,1], 'g-o', label='Y')
   >>> plt.savefig("hla_tut_orbit_correct.png")

.. image:: hla_tut_orbit_correct.png

.. doctest::

   >>> hla.getChromaticity() #doctest:+SKIP

.. sourcecode:: ipython

    In [69]: lines = plot([1,2,3])

.. math::

  G(s,s_0)=\dfrac{\sqrt{\beta(s)\beta(s_0)}}{2\sin\pi\nu}\cos(\pi\nu-\left|\psi(s)-\psi(s_0)\right|)

