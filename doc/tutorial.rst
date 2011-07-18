Tutorial
=========

The HLA and Controls are divided into three layers: HLA applictions and
scripts, client APIs (CAPI) and server API (SAPI)~([Shen]_).  The users
(accelerator physicists, operators and beamline scientists) will normally
access the first two forms: use applications/scripts by mouse clicks, and
the APIs in an interactive command line.


Some APIs are defined in [Shen]_, and are used by HLA applications. But they
are self-described as other Python modules. These APIs include data
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


Installation
-------------

There are some packages required before using HLA. In the following, we will
take Debian/Ubuntu Linux as an example to show how to install them.

::

  $ sudo apt-get install mercurial pyqt4-dev-tools
  $ sudo apt-get install python-qt4 python-qt4-dev
  $ sudo apt-get install python-docutils

By using BNL Debian/Ubuntu repository from Controls group, we can install some
EPICS tools easily:

::

  deb http://epics.nsls2.bnl.gov/debian/ lenny main contrib
  deb-src http://epics.nsls2.bnl.gov/debian/ lenny main contrib

.. code-block:: bash

  $ sudo apt-get install python-cothread epics-catools

Set environment for channel access and HLA. Append the following to
~/.bashrc::

  export EPICS_CA_MAX_ARRAY_BYTES=500000
  export EPICS_CA_ADDR_LIST="virtac.nsls2.bnl.gov vioc01.nsls2.bnl.gov"

Try to see if virtual accelerator is accessible

.. code-block:: bash

  $ caget 'SR:C00-BI:G00{DCCT:00}CUR-RB'

You should see the beam current of virtual accelerator. Then see if it changes

.. code-block:: bash

  $ camonitor 'SR:C00-BI:G00{DCCT:00}CUR-RB'

Download the *hla-v0.1.0a1.egg* file, then install

.. code-block:: bash

  $ sudo easy_install hla-v0.1.0a1.egg


Code Repository
-------------------

**SKIP THIS PART IF YOU DO NOT NEED TO DEVELOP HLA APPLICATIONS**

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

.. code-block:: bash

  $ hg clone http://code.nsls2.bnl.gov/hg/ap/hla
  $ cd hla
  $ (working .....)
  $ hg add newfile.py (if you have created a new file)
  $ hg status  ( list the status of current working directory)
  $ hg commit -m "I have improved the code" (check in the code with a message)
  $ hg push (push you change to the server)

If it has been a long time after you checkout the code from the server, you can 

.. code-block:: bash

  $ hg pull (update the local files with server's)



Examples
--------------

Before using HLA, we need some environment variables, like EPICS, put the
following in to ~/.bashrc::

  export HLA_DATA_DIRS=/home/lyyang/devel/nsls2-hla
  export HLA_MACHINE=nsls2
  export HLA_CFS_URL=http://channelfinder.nsls2.bnl.gov:8080/ChannelFinder

I am using **HLA_DATA_DIRS** as place to store data, the machine name
working on is *nsls2* and the channel finder service URL is at
**HLA_CFS_URL**. As an example, the orbit response matrix (ORM) data for
nsls2 would be saved in directory **HLA_DATA_DIRS/HLA_MACHINE**,
i.e. **/home/lyyang/devel/nsls2-hla/nsls2**.

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

if the network is not available and a copy of text-version-channel-finder-server data is in local machine, we can initialize HLA by the following command:

.. doctest::

   >>> hla.machines.initNSLS2VSRTxt()

Then is the examples:

.. doctest::

   >>> bpm = hla.getElements('BPM')
   >>> len(bpm)
   180
   >>> bpm[0].name
   u'PH1G2C30A'
   >>> bpm[0].family, bpm[0].cell, bpm[0].girder
   (u'BPM', u'C30', u'G2')

Each element has a set of properties associated:

- *family* (element type). e.g. 'QUAD', 'BPM'
- *cell*. The DBA cell it belongs. e.g. 'C02', 'C30'
- *girder*, girder name where it sits. e.g. 'G2', 'G1'
- *symmetry*, 'A' or 'B' symmetry
- *group*. A BPM in girder 2 cell 2 could be in group 'C02', 'G2', 'BPM'
   and more

A element can only belongs to one *family*, *cell*, *girder* and
*symmetry*. But it can be in many groups:

.. doctest::

   >>> hla.getGroups('PM1G4C02B')
   [u'BPM', u'C02', u'G4', u'B']

To find the elements in certain cell or/and girder, use *getGroupMembers* and
take *union* or *intersection* of them.

.. doctest::

   >>> el = hla.getGroupMembers(['BPM', 'C15', 'G4'], op='intersection')
   >>> for e in el: print e.name, e.sb, e.length
   PM1G4C15A 407.882 0.0
   PM1G4C15B 410.115 0.0

   >>> el = hla.getGroupMembers(['BPM', 'C0[2-3]', 'G2'])
   >>> for e in el: print e.name, e.sb, e.cell, e.girder, e.symmetry
   PH1G2C02A 57.7322 C02 G2 A
   PH2G2C02A 60.2572 C02 G2 A
   PL1G2C03A 82.7858 C03 G2 A
   PL2G2C03A 85.3495 C03 G2 A

   >>> hla.getGroups('P*C01*A')
   [u'BPM', u'C01', u'G4', u'G2', u'A']

   >>> hla.getCurrent() #doctest: +SKIP
   292.1354803937125

   >>> hla.getLifetime() #doctest: +SKIP
   7.2359460167254399

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

