Channel Finder Data
====================

``aphla`` uses Channel Finder Service to initialize elements and their
controls. For EPICS based systems, the related PVs are the key and each PV has
its associated properties and tags. The properties and tags should follow
certain convensions.

If the CFS is not available, a spreadsheet CSV file can also provide same
information, but it is limited to ``aphla`` package only and not available to
CSS or other tools.


Properties
------------

Each record in CFS has a PV and associated properties. Each property is a
*(key, value)* pair. Properties used by ``aphla`` in NSLS-II simulator are

- *cell*, the cell number this pv or its owner-element belongs to. e.g. 'C02'
- *girder*, 'G2'.
- *system*, not used yet.
- *symmetry*, symmetry 'A' or 'B' in NSLS-II lattice. used only in storage ring for specifying certain group.
- *devName*, the device name.
- *elemField*, the field name of the element. *x* and *y* for BPM and
  corrector, *k1* for quadrupole, *k2* for sextupole. *f* and *v* for RF, *image*, *image_nx* and *image_ny* for camera.
- *elemName*, the element name. used in accelerator lattice.
- *elemType*, 'QUAD', 'SEXT', 'BPM', 'HCOR', 'VCOR', ...
- *elemHandle*, the PV is a 'READBACK' or 'SETPOINT'.
- *elemLength*, length of *elemName*.
- *elemIndex*, ordinal number since injection. The exact number is not important but the order matters. It is used to sort the element.
- *elemPosition*, s-coordinate at the exit of *elemName*.

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
- *aphla.y*, general vertical direction
- *aphla.x*, general horizontal direction
- *aphla.offset*, not used yet
- *aphla.image*, an image waveform.
- *aphla.eget*, 
- *aphla.eput*,

The *aphla.sys.* tags tell how many systems(lattices). *aphla.elemfield.*
tells this PV can be accessed using ``element.field`` pattern.

