Unit Conversion
=================

``aphla`` can use polynomial or interpolation to convert units. The most
common unit system are called physics unit and raw(machine) unit. 'phy' and
None are reserved for them. The raw unit is the unit system used at a lower
level than ``aphla``, e.g. the EPICS channel access. For some instruments,
e.g., BPM, DCCT, they may be the same as 'phy' unit.

``aphla`` can have as many unit system as you can.

.. code-block:: python

  >>> bpm.get("x", unit=None)  # read bpm "x" with raw unit
  >>> bpm.get("x") # read "x" with 'phy' unit
  >>> bpm.x # equivalent to get("x")

Each unit system can have a symbol to help the plotting applications. e.g. BPM
reading can have "mm" or "um" for 'phy' or None unit system.

.. code-block:: python

  >>> bpm.getUnitSystems("x")
  [ None, 'phy']
  >>> bpm.getUnit("x") # default unitsys='phy'
  "mm"
  >>> bpm.getUnit("x", unitsys=None)
  "mm"

To explicitly convert the unit:

.. code-block:: python

  >>> bpm.convert("x", 0.1, None, 'phy') # convert from raw to 'phy'

