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
network, visualization, statistics and [EPICS]_ channel access. This
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







