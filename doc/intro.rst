Introduction
=============

This manual describes HLA (high level applications) for the NSLS-II
commissioning and accelerator physics study.

The HLA includes a set of applications and the APIs (Application
Programming Interface) those applications are based-on. The applications
is either a simple command or an application with GUI (graphical user
interface). APIs are designed for interactive control or batch
scripting. Both applications and APIs are in a high level form that are
friendly to physicists and operators.

This manual is compiled based on the requirements from the following
documents:

- 2008, NSLS-II: Model Based Control - A Use Case Approach [Bengtsson2008]_
- 2009, Assumptions on NSLS-II Accelerator Commissioning [Willeke2009]_
- 2010, The Path to Accelerator Commissioning [Willeke2010]_
- 2010, NSLS-II Storage Ring Commissioning [Krinsky2010]_

The details of each API can be found in the reference manual distributed
with the source code. A less detailed list of APIs is in
another manual by same authors [Shen]_.

Schedule for Beam Commissioning
-------------------------------

- 12/01/2011--02/29/2012, LINAC front end commissioning
- 03/30/2012--07/28/2012, LINAC commissioning
- 05/29/2012--06/28/2012, LBTL in LINAC commissioning
- 07/28/2012--08/27/2012, LBTL commissioning
- 08/27/2012--12/25/2012, Booster commissioning
- 12/15/2012--01/14/2013, BSTL in booster tunnel
- 01/14/2013--01/24/2013, BSTL
- 01/24/2013--09/21/2013, Storage Ring Commissioning Part 1
- 09/21/2013--11/20/2013, ID installation
- 11/20/2013--02/18/2014, Storage Ring Commissioning Part 2


Overview of Control Scripts and Applications
---------------------------------------------

The high level control software is developed for the beam commissioning
and accelerator physics study. It is designed for monitoring, control and
modeling the electron beam and accelerators.

A set of existing tools such as MATLAB Middle Layer (MML) will be
installed in the control room. However, more new tools need to be
developed especially for the first turn beam monitoring and manipulations.

The new developement will be based on Python language, integrated with
libraries for numerical analysis, data input/output, image processing,
network, visualization, statistics and EPICS_ channel access. This
environment will have both interactive control terminal and batch (script)
processing mode. High level applications and APIs will be developed to
make beam manipulation and hardware control friendly to physicists and
operators.

The new Python based package will have certain overlap with MML, and will
have better integration with the global database, where all related
information are stored: from magnet bentchmark data to user profile.

This work is done by both controls group and accelerator physics group.

HLA Architecture
--------------------

The system architecture is shown as the following

.. image:: _static/hla_arch.png

It adopts a client/server model, and consists of various servers for data
acquisition, analysis, management and communication. Based on this
structure, physics applications can be developed to satisfy the
requirements of both day-1 beam commissioning, future beam study, and
daily operation.  Briefly, the system consists of

- data source layer, which can be low level hardware control system, or a
  relational database;
- a service layer, which provides services to gather data from the data
  source layer, and perform data manipulations such as constructing an
  orbit using BPM data;
- a presentation layer, which present machine status to operators, and
  provides an interface for machine control.


The server part talks directly with hardware using EPICS PV. It is an area
controls group focus on. All the data on "data bus" have a meaningful
name instead of long abstract channel name. e.g. the setpoint of
horizontal orbit corrector in cell 1 girder 3 is presented to accelerator
physicists as *CH1[0]* instead of *SR:C01-MG:G03A.SP*. This makes them to
write high level control scripts easier. The client API which encapsulate
low level control details are listed in [Shen]_. They usually contains
physics logic or accelerator dependent quantities
inside. e.g. **getChannelVariance**, **measureChromaticity**.

- BBA and LOCO are HLA applications. Turn by turn beam orbit
  measurement and analysis can be a HLA script.
- Client APIs are a group of physics logics, e.g. **measOrbitRm**,
  **measChromaticity**, **getGoldenOrbit**, ...
- Server APIs are called by client APIs across the network, and will
  not be seen by HLA applications or scripts. The server APIs have two
  major functions:
  
  - manage the accelerator magnets/lattice information, e.g. logic
    group of a magnet, whether it is used by BBA or LOCO or orbit
    measurement etc. The basic information is contained in a XML file or a
    database in the following sections, (the implementation may not be a
    XML file, but a Database). lattice layout. (optional: nearby vacuum
    and temperator sensor information, power supply name and location)
  - control the magnets via a control server, this server will call
    low level APIs to do PV readings and settings.

The high level applications developed by accelerator physicists should
be able to achieve their goals by focusing on algorithms while being
released from tedious data acquisition and manipulation issues. This
is the design strategy for the software architecture. With a clean and
carefully designed interface, collaborators, who have different areas
of expertise such as GUI design, numerical analysis, accelerator
physics, data acquisition, hardware control, and so on, can work
together effectively and productively.

.. _Software Requirement:

Software Requirement
=======================

This chapter describes software requirement for NSLS-II
commissioning. This list is mainly from [Willeke2009]_.
and [Krinsky2010]_, plus some personal experiences.

The items marked with (*) will get more focus, since they usually contains
more physics or algorithm. Parameters tuning or even new algorithms may be
needed. A more detailed list specfically for accelerator physics related
functions are in `Accelerator Physics Toolkit`_.


General Operation
----------------------------

- Overall status page (warning when read/set are different too much ?)
- Status, Alarm and warning monitor
- Permit system monitor and control
- Data logger and data display
- Electronic logbook


Operations Software
------------------------------

- Accelerator parameter store/restore (*)
    - manage, editing capability for stored accelerator status.
    - smoothly ramp from one stage to another.
    - compare two stages, online and saved data, two data file.
- Injection Control
- Power supply control
- RF control
- Fast orbit feedback control
- Front-end monitoring and control
- Machine protection system display and control
- Magnet temperature interlock display and control
- Scraper and movable mask operations


Major Subsystem Control
------------------------------

- Power supply page which lists for all PS:
    - setting or waveform, read back
    - difference between DCCTs, status
    - recent history.
- RF page with all relevant settings, read back, status, parameters
- Vacuum display and control. "Water flow" or 3D plot of vacuum status
  along the ring with time line info.
- Cryogenics system display and control
- Pulsed magnet systems monitor and control



Beam Diagnostics
------------------------------

- Beam orbit page with closed orbit, turn by turn, single turn, status
  information, difference (referecne orbit display) (*)
- Beam current history and lifetime display (*)
- Bunch intensity display and history display/analysis (*)
- Beam emittance display (*)
- Injection element display and control page (*)
- Injection efficiency
- Timing system display and control 
- Synchronization system display and control
- Tune display and control (*)
- Temperature monitoring display
- Bunch length and profile if it is available (*)
- Measure BPM linearity


Safety Systems
------------------

- Personal protection system status display
- Equipment protection status display and control
- Beam containment status display and control
- Top-off status monitor


Utility Control
-----------------------------

- Tunnel air temperature and humidity monitor
- Mechanical utilities status and controls
- Electrical utilities status and controls
- Equipment enclosure monitor
- Water colling system display
- Controls network monitor


Beam Status Diagnostics
---------------------------------


A set of API should be provided to allow physicists to fetch data from
circular buffer of related sub-system, especially diagnostic
instrument, and RF. Detailed requirement can be found in [Shencbd]_.

.. _High Level Applications:

High Level Applications
==========================

The HLA and Controls are divided into three layers: HLA applictions and
scripts, client APIs and server API~([Shen]_).  The users
(accelerator physicists, operators and beamline scientists) will normally
access the first two forms: use applications/scripts by mouse clicks, and
the APIs in an interactive command line.


Applications include:

- Overall status of all subsystems: magnet, vacuum, RF, temparature
- Orbit display and correction.
- Linear optics reconstruct, i.e. LOCO
- Beam based alignment.

APIs are defined in [Shen]_, and are used by HLA
applications. They include data acquisition, processing and storage, and
can be combined for different purpose. The APIs are in Python language,
and can be used in both interactive environment or scripts. Necessary
packages including linear algebra, frequency analysis, statistics, data
IO, database, network, regular expression and visualization will be
provided. See Python_, SciPy_, NumPy_, iPython_, matplotlib_.


The HLA applications are those have a stable algorithm and data
flow. Each is in a standalone form.


Machine Status
---------------

The applications will provide overall status of the whole machine, and
give warnings when any abnormal beam behaviour is detected, for example
a readback differs from setting point larger than its threshhold. The
status includes beam information, and hardware status including magnet
and its power supply, vacuum, RF, and so on.

These part can be done in striptool, EDM or CSS (control system
studio). No heavy data manipulation or physics logics. 

- Tunes
    - horizontal/vertical tune number, at least 1Hz update
    - optional: FFT of turn by turn BPM data, choice of any live BPM.
    - optional: 2D tune footprint with resonance lines
- Magnets, tables of data. SP/RB of main magnets: quadrupoles, sextupoles,
  correctors.
- Vacuum status in plots and tables.
    - Pressure vs index.
    - optional: Pressure vs pump location.
    - optional: waterflow plot.
- RF status
    - optional: RF feedback status which detects orbit drift vs RF frequency.
- Feedback status
- Beam profile: current, size, rms, center, image.


Orbit Display and Correction
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This application displays and controls electron orbit.
  
- Static orbit display
    - Plot static orbit. (with magnet layout)
    - Show golden orbit (or reference orbit)
    - Absolute orbit offset and orbit offset with respect to golden orbit
    - Plot orbit change from now on.
    - Orbit statistics. stability, especially drift and variation
- Static orbit control
    - Correct static orbit with selected correctors and BPMs
    - Enable/disable BPMs for orbit correction and feedback.
    - Enable/disable correctors for orbit correction and feedback
    - Import/export orbit response matrix
    - Edit golden orbit offset. (e.g. offset the golden orbit to create
      local bump)
- Orbit feedback status
- Turn by turn BPM
    - reading vistualization when available/enabled
    - get/plot turn-by-turn BPM signal, including orbit and sub/diff
    - Realtime tune based on turn-by-turn BPM
    - BPM buttons readout.
    - plot single shot orbit.
    - Correct orbit based on single shot orbit
- Measure the orbit response matrix, with flexible number of BPMs
  and correctors.

Bad BPM identification should be done in other application. Data
synchronization to be done in low level server part.

Interplay with feedback system when creating local bump: update the
reference orbit to feedback ? or share same orbit difference from a
dedicated IOC ? the feedback should check golden orbit at 10-50Hz rate
if real-time orbit difference is not available to it.


Beam Based Alignment (BBA)
----------------------------

BBA use a list of correctors, BPMs and nearby quadrupoles, to steer the
beam through center of these quadrupoles. The input is a list of
corrector-BPM-quadrupole triplets.  The BPMs in corrector-BPM-quadrupole
triplet is a subset of live BPM.  This needs to get the golden orbit, set
the golden orbit, line fitting, step the quadrupole, step the corrector
(this can be a "macro step", e.g. 10 times than normal step size). Many
raw data needs to be saved in certain format: Python binary, HDF5 or
Matlab.

We would prefer to have all data saved, corrector settings/readings, BPM
readings and Quadrupole settings/readings.

The measurement and analysis can be separated conceptually, which makes
the post processing< easier, i.e. we can analyze any historical data,
and replay them.

It should work on separate set of quadrupoles, and combine data with
previous measurement.

Linear Lattice Fitting (LOCO)
-------------------------------

- analyze quadrupole gradient error.
- analyze BPM gain error.

It requires:

- Designed orbit response matrix (ROM)
- change specified correctors 
- get closed orbit change at specified BPM

This application needs mathematical package to do minimization and
singular value decomposition (SVD). It also requires simulator for
fitting.

Measure TWISS Parameters
--------------------------

- measure beta functions
- measure dispersion
- measure chromaticity
- measure coupling
- measure coupling response matrix
- Measure and adjust tune. (tune scan ?)
- Measure and correct the chromaticity (linear and nonlinear). 
- Measure beam optics including phase advance, beta functions, dispersion.
- Dispersion measurement and correction, optimal set of quads


Smooth Ramping
------------------

- list channels we are interested.
- ramp whole group at certain rate.

It requires:

- searching for channels (regular expression, wild-card)
- save state/read stage.

The control group may provide ramping for whole storage ring, here this
application can ramp specified channels between two states.

History Analyzer
-----------------

- view archive data in certain time frame.
- link to logbook to view reasons for shutdown, current drop (?)
- simple statistic for the data: average, variance, maximum, minimum.
- print, save figures.


Insertion Device Related (Matching)
-------------------------------------

- get/correct closed orbit distortion
- get/correct phase distortion
- get/correct coupling distortion

Simulator
-------------

This is required for online lattice fitting, e.g. LOCO. Tacy-v3 will be a
choice.


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

Requirement
-----------

We have compiled a set of requirements for high level control software,
and design the APIs as a common library. The high level applications will
use these APIs to fulfil comissioning, operations and physics studies. We
need more input from operation group to make these tools more
operator-friendly.

In NSLS-II storage ring commissioning plan [Willeke2009], [Krinsky2010],
we have defined the requirement of control software. Here we only
summarize the functions needed, but neglect the order of using them in the
commissioning.


Hardware/Control checking and testing
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- BPM testing stability, polarity.
- BPM current dependency, resolution.
- Check polarity of all magnets.
- Orbit corrector polarity and strength test, 
- Converting between machine unit and physics unit.
- Ramping from one magnet setting to another.
- Monitoring stability of any readings and online data: magnet
  readback, orbit, temperature, vacuum.
- Magnetic field measurement and modeling, determine calibration
- Verify named devices in control system, control proper hardware
- Complete survey of magnetic elements
- Test diagnostic equipment without beam

BTS transport line
~~~~~~~~~~~~~~~~~~~~~

Obtain good transmission through septum and good transverse phase space
match, set timing of pulsed magnets.

Insertion Device
~~~~~~~~~~~~~~~~~~~~~

- When necessary compensate the linear optics for ID
- Observe orbit and tune shift vs gap
- Measure lifetime vs gap
- Observe beam stability vs current
- Measure change in impedance due to ID chamber
- Prepare look-up tables for feed forward orbit correction coils.
- Measure effect on tune shift with amplitude, chromaticity, and emittance
  coupling.
- Measure impedance vs gap for IVUs
- Commission undulator gap control for users
- Measure flux and brightness


Misc
~~~~~~~

- Test fast orbit feedback system.
- Look for magnet errors that may have been missed in testing.
- Obtain first turn in storage ring using single kicker
- Use flag to obtain beam size information at injection point and
  after one turn.
- Beam based alignment of sextupoles.
- Develop lattice model using measured fields, linear/nonlinear optics.
- Reduce beta beat
- Correct coupling using skew quadrupoles, local and global.
- Analysis on nonlinear dynamics.
- Use pinger to measure tune shift with amplitude, dynamic aperture
  and characterize sextupole distribution
- Wakefield modeling and tracking studies, develop model for
  impedance and wakefields, caculation and measurement, estimate
  instability thresholds, simulate bunch-by-bunch feedback with
  realistic bunches and wakefields.
- Characterize ring impedance using beam.
- Commission loss control minitoring system
- Use visible synchrotron light monitor to study transverse beam
  profile and disturbance due to kickers. *getBeamProfile*
- Study lifetime versus vacuum pressure, vertical beam size, scraper,
  dynamic aperture.
- Commission transverse bunch-by-bunch feedback
- Measure variation of coherent tune with current
- Study increasing chromaticity from +2/+2 to +5/+5
- Commission undulator gap control in control room
- Calibration/Testing of Equipment Protection Interlock System
    - Center photon beam in exit slot
    - Verify gap open/close status is properly reported to interlock system
    - Measure interlock BPM offset and scale factors.
    - Adjust the hardware trip points on the local logic chassis
    - Verify beam is dumped at the specified position offsets.
    - Set the values in the interlock test file
    - Verify the proper operation of the interlock test
- Top-off Injection
    - Check position of apertures in ring and beamline
    - Test interlocks
    - Characterize injection transient on transverse orbit, contribution
      from septum and kickers.
    - Test transverse feedback with injection transient
- Concerns: accuracy of magnet calibration-two types of dipoles, magnetic
  field quality (IRMIS data).
- PBPM matching. Read both BPM and PBPM, and use BPM to benchmark the
  PBPM values.
- Get groud motion and chamber motion if there are available readings.
- Monitor beam loss. Get loss monitor readings from beam containment
  system (beam loss monitor).
- Identify MPS (magnet power sypply) ripples.


Injector
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Software routines needed for the injector commissioning and operation are
listed in this section. Some of these routines will be delivered by linac
and booster vendors, others have to be developed by ourselves.

- Linac
    - Diagnostics calibration
    - Routines for optimization of linac performance
    - Energy feedback
    - Charge feedback
    - Specification of bunch train format    
    - Beam loading compensation      
    - Energy measurement     
    - Energy spread measurement      
    - Emittance measurement (3 screens)      
    - Emittance measurement (quad scans)     
    - Matching of Twiss parameters into booster septum       
    - Beam stacking  
    - Beam transmission optimization 
    - TL quad centering      
    - Integration of safety devices/interlocks       

- Booster
    - Diagnostics calibration       
    - Orbit correction       
    - Tune measurement system
    - Energy measurement     
    - Momentum compaction measurement
    - Emittance measurements 
    - Beam stacking  
    - Extraction optimization
    - Ramp optimization      
    - LOCO-type machine characterization     
    - MIA in transport line -    - booster acceptance testing
    - Orbit feedback 
    - Synchrotron Radiation diagnostics      
    - Bunch cleaning system  
    - TL quad centering      
    - Integration of safety devices/interlocks       

- SR

  In addition to what has been already specified by Accelerator Physics:

    - Closed bump optimization: A and t
    - Simultaneous measurements of injected/stored beam orbits


Terminology for High Level Applications
------------------------------------------------

The naming convension and terminology should follow the definitions of
project nomenclature standard:

- National Synchrotron Light Source II - Nomenclature
  Standard [LT2009nomenclature]_
- National Synchrotron Light Source II - Accelerator Systems Requirements
  Document, Storage Ring Physics Nomenclature
  Standard [LT2008nomenclature]_

A set of commonly used words are explained in the following:

- **Mode** is used for separating different machine settings. As an
  example, there could be "production mode", "accelerator physics beam
  study mode", "short bunch mode", "low current mode". With this
  separation, all the other settings can be same or different for two
  modes.
- **Group** represents a set of elements when they are sharing similar
  position, symmetry, purpose, connections or user's preferences. For
  example, we can assign all sextupoles with a group name *sextupole*
  and all magnets on the second girder in each cell a group name
  *girder2*. From lattice point of view, we can have a group name
  *qh1* for all quadrupoles with this symmetry. Each element or
  magnet can belong to one or more groups.  For consistancy, the element
  belongs to the group which has only himself and the group name is same
  as its element name (the element name is guaranteed unique).

  We can have some predefined group names, and they will be commonly used
  for their type or symmetry, e.g. *quadrupole*, *sh1*. The
  pre-defined group name should be discussed carefully, and stored in a
  relational database, *IRMIS* for example. Users can also define
  their own group name which should not overwrite any system defined group
  names.

  The suggested candidates of group name are:

    - Magnet with same power supply or lattice symmetry.
    - *bpm*, *corrector*, *quadrupole*, *sextupole*,
      *skewquadrupole*, ...
    - Specific purpose: *bba*, *orbit*, *tune*,
      *chromaticity*
    - User defined: "Sam's test BPM", "Weiming's Toy", ...

- **wildcard**. When searching for a group, the name matching should
  support a subset of regular expression (need more details on "subset",
  how small/large is this set). One choice is the BASH wildcards:

    - **\***, zero or more characters
    - **?**, exactly one character
    - **[abcde]**, exactly one character listed
    - **[a-e]**, exactly one character in the given range
    - **[!abcde]**, any character that is not listed
    - **[!a-e]**, any character that is not in the given range

- **Sequence** We can also use sequence to identify one element, usually
  BPM or corrector. For the convenience purpose when looping over BPM or
  correctors one after the other along the ring, we can use number as its
  order, instead of their names. Suggested sequence could be a pair
  [*cell*, *index*], and *cell* is the cell number
  following the name convention as below, which is an integer between 1
  and 30 according to the NSLS-II
  nomenclature [LT2008nomenclature]_, [LT2009nomenclature]_. The index
  is the order (according to s-location) in that cell, and index starts
  from 0 to follow some language conversion such as Python/C/C++. A
  definition similar to *MML (Matlab Middle Layer)* can be atopted. This
  part should be discuss carefully to avoid ambiguity.  
- **Coordinate definition**, we always use *x*, *y* and
  *s* specify the horizontal, vertical and longitudinal plane. The
  $s=0$ is defined as the injection point (in Cell 30).
- **Array Data Arrangement** Whenever the value is an
  array, sort it in the beam direction, for example, in increasing order
  of $s$ location. This may be confusing for the injection cell, where
  $s=0$ does not aligned with the begin/end point of a cell, but in the
  middle.

  A policy to determine who is the first element should be
  discussed. ($s=0$ location)

- **Control System**

    - EPICS
    - Channel
    - Record
    - PV (Process Variable)
    - CA (Channel Access)



.. _Specifications for Servers and Databases:

Specifications for Servers and Databases
=========================================

**DISCLAIMER:**

**This part serve as a list of requirements for supporting system: low
level control service and database. Scientists/Engineers in charge of
these subsystem will decide the details of their implementation. If this
section has any description related to the internal implementation, it
just servers as illustration purppose, not meant to assume that the above
HLA are interfering or relying on this specific implementation**


Services and DB
-----------------

- Model service: read/save models (magnets settings, linear lattice)
  from/to IRMIS for HLA.
- Channel finder service: HLA needs a service mapping (magnet="QF",
  field="K1", handle="readback") to the EPICS channel. So the client can
  set/get arbitrary magnet/element value via basic channel access code or
  PV service.
- PV service: set/read PV values
- Unit conversion service: convert physics unit to engineering unit for a
  specific PV.
- Log scroll
- IRMIS data: Configuration of HLA and hardware infomation is saved in DB.
- Misalignment can be from other IRMIS data set


Model Service and IRMIS Database Support
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

HLA rely on Model server as an agent to IRMIS database, only model related
data. HLA sent request, all in physics unit, to model server to read/save
different models. These model provide the access to the following data:

- Model name: a unique tag
- Date when the model is modified or created. The whole history of
  modification is not required. The latest version would be enough.
- Description: a short or reasonable long description, a couple of paragraph 
- All magnets defined in Tracy lattice description file, this includes
  magnet names, fields and their values.
- Linear lattice parameter, i.e. the twiss parameters from simulators
- Potential values: orbit response matrix, tune and chromaticity
  correction matrix. (or a link/tag to the binary file which stores them)

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



.. _appendix:

Acronym and API Prefix
=========================

We recommend to use full word instead of acronym, but for the most
common ones, acronym makes life easier. The following list serves as a
guideline for API prefix but exceptions do exist.

- **meas** is for measurement routines. They may perturb the beam, and
  affect users.
- **get** is either read history or the output of online instrument.
- **set** will change the settings of an online instrument. The value will
  be gone after next injection(non-topoff)
- **save** operates on file, read machine to file/DB. (set operates on
  real machine, on a smaller scale, single element/group). The new value
  will take effect in next injection/run.
- **load** operates on files/DB and set to memory/machine.
- **calc** is for routines doing calculation and analysis. This is
  calculation only, does not perturb the beam.
- **enable/disable** makes element online/offline

There are exceptions that a few APIs have prefix not mentioned above
(see [Shen]_ for a complete list).

BPM(beam position monitor), RF(radio frequency), SOFB/FOFB(slow/fast
orbit feedback), bba(beam based alignment), chrom(chromaticity),
sp(setpoint), rb(readback) are common acronyms.



.. [Bengtsson2008] J. Bengtsson, B. Dalesio, T. Shaftan, T. Tanabe,
   *NSLS-II: Model Based Control - A Use Case Approach*, Tech-note 51, Oct
   2008
.. [Willeke2009] F. Willeke, *Assumptions on
    NSLS-II Accelerator Commissioning*, November 22, 2009
.. [Willeke2010] F. Willeke, *The Path to Accelerator
    Commissioning*, talk on ASD Project Meeting, Jan 2010
.. [Krinsky2010] S. Krinsky, *NSLS-II Storage Ring
    Commissioning*, NSLS-II ASD Retreat, May 13, 2010.
.. [Shen] G.~Shen, L.~Yang, *High level applications -
    APIs*
.. [LT2009nomenclature] *National Synchrotron Light Source II
    - Nomenclature Standard*, LT-ENG-RSI-STD-002, Jan 21, 2009, Rev 2
.. [LT2008nomenclature] *National Synchrotron Light Source II
    - Accelerator Systems Requirements Document, Storage Ring Physics
    Nomenclature Standard*, RSI Document 1.3.4-001, Feb 17, 2008, Rev 1
.. [Shencbd] G.~Shen, Y.~Hu, B. Dalesio, *Circular Buffer
    Diagnostic*
.. _EPICS: www.aps.anl.gov/epics/
.. _Python: http://www.python.org/
.. _iPython: http://ipython.scipy.org/moin/
.. _matplotlib: http://matplotlib.sourceforge.net/
.. _SciPy: http://www.scipy.org/
.. _NumPy: http://numpy.scipy.org/
