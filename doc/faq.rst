HLA FAQ (Frequently Asked Questions)
=====================================

- The element can have fields to read or set, where to find them ?

  Use the following command

  ::

    >>> CH = hla.getElements('HCOR')
    >>> CH[0].fields()
    ['status', 'x', 'value']
    >>> CH[0].x = 1e-6
    >>> print CH[0].x

  It first get a list of element objects, check the fields of the first `HCOR`
  and set its `x` to 1e-6.

- Why I can not find element ...

  - How many elements you get from `getElements('*')` ?
  - If less/more than expect, what are their names ? Are you using the proper
    lattice layout by *hla.machines.use('SR')* ?
  - If none, seems the lattice is not initialized.
  - Did you initialize the machine with, e.g. *hla.initNSLS2VSR()* or *hla.initNSLS2VSRTxt()* ?
  - Did you export the channel finder environment *HLA_CFS_URL* ?
  - Do you have a proper `us_nsls2_cfs.csv` file in your `$HOME` ?

- How many lattices are there ?

  Try `hla.machines.lattices()`. Depending on your initialization,
  e.g. `initNSLS2`, `initNSLS2V1`, the elements are put in the lattice if its
  PV has a tag like 'aphla.sys.*' in Channel Finder Service data.
