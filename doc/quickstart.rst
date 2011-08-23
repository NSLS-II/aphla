Quick Start
============

.. htmlonly::
   :Date: |today|


- Remote login the server: *ssh -Y youraccount@lsasd2.ls.bnl.gov*
- Enter IPython and using HLA

  ::

    $ ipython -pylab
    
    In [1]: import hla

- Initialize the VSR (virtual accelerator lattice structure)

  ::

    In [2]: hla.initNSLS2VSR()

- Initialize the Twiss data

  ::

    In [3]: hla.initNSLS2VSRTwiss()

- Get the orbit

  ::

    In [4]: hla.getOrbit()

- Get a list of correctors, print the name and strength of one corrector.

  ::

    In [5]: cx = hla.getElements('CX*C19*')
    In [6]: print cx[0].name, cx[0].x
    CXL1G2C19A 6.32815600708e-08

- Set the corrector

.. highlight:: python

     In [7]: cx[0].x = 5e-8
     In [8]: print cx[0].name, cx[0].x
     CXL1G2C19A 4.99974399176e-08


