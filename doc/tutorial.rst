Tutorial
=========

The HLA and Controls are divided into three layers: HLA applictions and
scripts, client APIs and server API~([Shen]_).  The users
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


Examples
=========

Example 1

.. doctest::

   >>> import hla
   >>> hla.clean_init()
   >>> bpm = hla.getElements('BPM', cell='C20')
   >>> print bpm
   ['PH1G2C20A', 'PH2G2C20A', 'PM1G4C20A', 'PM1G4C20B', 'PL2G6C20B', 'PL1G6C20B']
   >>> hla.getLocations(bpm, 'end')
   [532.90700000000004, 535.43200000000002, 541.11699999999996, 543.34900000000005, 548.21900000000005, 550.78300000000002]
   >>> hla.getGroups('P*C01*A')
   ['A', 'BPM', 'G4', 'G2', 'BPMY', 'C01', 'BPMX']


Code Repository
===================

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

