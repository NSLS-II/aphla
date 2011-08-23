History
========

v0.2.0
-------

  - add local bump
  - add beam based alignment
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
