History
========

- :download:`aphla-0.3.2.tar.gz<aphla-0.3.2.tar.gz>`
- :download:`aphla-0.3.2b1-py2.7.egg<aphla-0.3.2b1-py2.7.egg>` (development snapshot)
- :download:`aphla-0.3.1-py2.7.egg<aphla-0.3.1-py2.7.egg>`
- :download:`hla-0.2.2-py2.7.egg<hla-0.2.2-py2.7.egg>`
- :download:`hla-0.2.1-py2.7.egg<hla-0.2.1-py2.7.egg>`
- :download:`hla-0.2.0-py2.7.egg<hla-0.2.0-py2.7.egg>`
- :download:`hla-0.1.0-py2.7.egg<hla-0.1.0-py2.7.egg>`

v0.3.2
------

  - see ChangeLog

v0.3.1
------

  - add set/get for field string
  - use cothread-2.8 to avoid core dump on lsasd2
  - combined test cases for nsls2v1
  - updated cfs server data, merged bug fix from python client

v0.3.0
-------

  - add pickle/shelve support for :mod:`~aphla.element.Element`
  - fixed testing case for element
  - fix bug in correctOrbitPV
  - fix bug in getLocations to ignore virtual element
  - add mark/reset/revert for :class:`~aphla.element.CaElement`
  - fix bug in doc

v0.2.2
------

  - add simple locking for multiusers
  - add dispersion measurement :func:`~aphla.meastwiss.measDispersion`
  - add beta function measurement :func:`~aphla.meastwiss.measBeta`
  - bug fix of :func:`~aphla.machines.initNSLS2VSRTwiss`


v0.2.0
-------

  - add local bump
  - add beam based alignment :mod:`~aphla.bba`
  - bring back eget


v0.1.0
-------

  - orbit.pyw works with new hla
  - fix bug in getElements, where a copy must be returned instead of pointer.
  - fix bug where "value" blocked by general "field"
  - *correctOrbit* and *correctOrbitPv* works on new lattice infrastructure.
  - separate orm data from orm measurement
  - add fields (x/y) for BPM/HCOR, change TRIMX/TRIMY to HCOR/VCOR and HFCOR/VFCOR.
  - *machines.initNSLS2SVR*, *machines.initNSLS2VSRTxt*: add virtual elements of BPMX/BPMY
  - *Element.getValues*: added, use tags to get default values.
  - *getOrbit*: support virtual BPMX/BPMY element
  - *getGroupMembers*: fix bug when calling with string instead of list, e.g. 'BPM'.
  - *getBpms*: added

- 0.1.0a2

  - remove *EPICS_CA_ADDR_LIST* dependency.

- 0.1.0a1

  - initial release of alpha-1.
