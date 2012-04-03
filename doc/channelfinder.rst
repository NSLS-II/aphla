Channel Finder Data
====================

``aphla`` uses Channel Finder Service to initialize elements and their
controls. For EPICS based systems, the related PVs are the key and each PV has
its associated properties and tags. The properties and tags should follow
certain convensions.

If the CFS is not available, a spreadsheet CSV file can also provide same
information, but it is limited to ``aphla`` package only.


Properties
------------

Each record in CFS has a PV and associated properties. Each property is a
*(key, value)* pair. Properties used by ``aphla`` in NSLS-II simulator are

- *cell*, the cell number this pv or its owner-element belongs to. e.g. 'C02'
- *devName*, the device name.
- *elemField*, obsolete
- *elemName*, the element name. used in accelerator lattice.
- *elemType*, 'QUAD', 'SEXT', 'BPM', 'HCOR', 'VCOR', ...
- *girder*, 'G2'.
- *handle*, the PV is a 'READBACK' or 'SETPOINT'.
- *length*, length of *elemName*.
- *ordinal*, ordinal number since injection. The exact number is not important but the order matters. It is used to sort the element.
- *sEnd*, s-coordinate at the exit of *elemName*.
- *symmetry*, symmetry 'A' or 'B' in NSLS-II lattice. used only in storage ring for specifying certain group.
- *system*, not used yet.

Some other properties exist but not used by ``aphla``, e.g. *hostName*, *iocName*

The lattice initialization is in one routine, e.g. ``initNSLS2VSR`` for
NSLS-II Virtual Accelerator. Not recommended but in principle those keys of
properties can be mapped to other ones for other facilities.

When initializing an element, ``aphla`` searches for possible *elemName*
values. element is constructed based on its unique name.

Tags
------

:class:`~aphla.chanfinder.ChannelFinderAgent` can read CSV or download CFS data
then output all possible tags:

- *aphla.current*, beam current
- *aphla.sys.LTD2*, linac-to-dump2
- *aphla.sys.LTD1*, linac-to-dump1
- *aphla.sys.LTB*, Linac-to-booster system
- *aphla.sys.SR*, Storage ring system
- *aphla.elemfield.y*, this PV can be accessed using ``elem.y``, e.g. bpm
- *aphla.elemfield.v*, ``elem.v``, e.g. RF voltage
- *aphla.elemfield.x*, ``elem.x``, e.g. horizontal corrector, bpm
- *aphla.elemfield.k1*, ``elem.k1``, e.g. quadrupole
- *aphla.elemfield.f*, ``elem.f``, e.g. RF cavity
- *aphla.elemfield.value*, ``elem.value``
- *aphla.y*, general vertical direction
- *aphla.x*, general horizontal direction
- *aphla.offset*, not used yet
- *aphla.image*, an image waveform.
- *aphla.eget*, 
- *aphla.eput*,

The *aphla.sys.* tags tell how many systems(lattices). *aphla.elemfield.*
tells this PV can be accessed using ``element.field`` pattern.


