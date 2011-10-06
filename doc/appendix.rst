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
