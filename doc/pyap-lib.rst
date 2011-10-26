Python Accelerator Physics Library (PyAP-Lib)
==============================================

.. htmlonly::
   :Date: |today|

PyAP-Lib is a Python library for high level accelerator physics control. It
uses EPICS for equipment control and channel finder for PV data management.

EPICS
--------

`EPICS (Experimental Physics and Industrial Control
System) <http://www.aps.anl.gov/epics/>`_ is a set of Open Source software
tools, libraries and applications developed collaboratively and used worldwide
to create distributed soft real-time control systems for scientific
instruments such as a particle accelerators, telescopes and other large
scientific experiments.

Channel Access
---------------

The read and write of equipment can be done by *caget* and *caput*. There is a
module in HLA *catools.py* which wrapps the original *caget* and *caput*
routines which could not support the UTF-8 encoding (the encoding from channel
finder server). There is also a *caputwait* routine to make the
waiting-after-writing more efficient and reliable.


Channel Finder
---------------

`ChannelFinder <http://channelfinder.sourceforge.net/>`_ is a directory
server, implemented as a REST style web service. Its intended use is within
control systems, namely the EPICS Control system, for which it has been
written.

This directory server assigns properties and tags to PVs. The PyAP library
will read these values and build the lattice structure for Linac, booster and
storage rings. It can also have the transfer lines and beam dumps.

The following is a record for one readback PV of BPM *PH2G6C01B*

::

  SR:C01-BI:G06B{BPM:H2}SA:X-I;
  Properties:
    cell = C01, devName = PH2G6C01B, elemField = x, elemName = PH2G6C01B,
    elemType = BPM, girder = G6, handle = READBACK, length = 0.0, ordinal = 193,
    sEnd = 45.3368, symmetry = B;
  Tags:
    aphla.eget, aphla.x, aphla.sys.SR


By querying for *elemName=PH2G6C01B*, we can construct an element with this
name, type, length etc. The tags *aphla.sys.SR* marks this element or PV is
part of storage ring system in HLA. One element can belongs to many
system. The lattice built is just a list of elements.

By convention, all tags used by HLA have a prefix *aphla*.

Element
--------

*Element* class has wrapped the channel access. The PVs, properties and tags
in channel finder server are also included.

The *elemField* is mapped into a field of element. For example, in the above
record, *SR:C01-BI:G06B{BPM:H2}SA:X-I* has an *elemField=x*. This makes the
element *PH2G6C01B* has a field *x*. Reading this field will be equivalent to
read that PV (it has a *handle=READBACK*). Similarly for setting an horizontal
orbit corrector which may have a PV record with *handle=SETPOINT* and
*elemField=x*.

::

  >>> bpm = hla.getElement("PH2G6C01B")
  >>> print bpm.x


This is implemented by providing *__getattr__* and *__setattr__* for *Element*
class.


Lattice
--------

Several lattices are built on top of channel finder service. By querying the
tags of prefix *aphla.sys.* The elements are stored in a sorted order and is
guaranteed in routines where a list of elements are returned.

There is a global current lattice *hla.machines._lat*. It is used when
searching for elements: *hla.getElements*. This can be changed by
*hla.machines.use*. The complete lattice list is given by
*hla.machines.lattices*.

See *machines.py* for details on how to construct elements and lattices from
channel finder server or plain text config file.

A virtual element can also be built for convenience. (see *machines.py*)



Data
-----

Certain data, such as orbit response matrix, cached lattice, are coupled with
certain set of lattices. This needs to be taken care of in initializing the
lattice and switching the lattice.

ORM (orbit response matrix) are in two files: *orm.py* and *ormdata.py*. The
former is a class with measurement routines and the later is only for data
manipulation purpose.


High Level Tools
-----------------

There is a module *aptools.py* for accelerator physics measurement
routines. *twiss.py* for twiss data manipulation.


Documentation
---------------

write a *rst* file in *doc*, then *make html*



