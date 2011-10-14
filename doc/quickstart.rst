Quick Start
============

.. htmlonly::
   :Date: |today|


- Remote login the server: *ssh -Y youraccount@lsasd2.ls.bnl.gov*
- Enter IPython and using HLA

.. code-block:: python

    $ ipython -pylab
    
    In [1]: import hla

- Initialize the VSR (virtual accelerator lattice structure)

.. code-block:: python

    In [2]: hla.initNSLS2VSR()

- Initialize the Twiss data

.. code-block:: python

    In [3]: hla.initNSLS2VSRTwiss()

- Get the orbit

.. code-block:: python

    In [4]: hla.getOrbit()

- Get a list of correctors, print the name and strength of one corrector.

.. code-block:: python

    In [5]: cx = hla.getElements('CX*C19*')
    In [6]: print cx[0].name, cx[0].x
    CXL1G2C19A 6.32815600708e-08

- Set the corrector

.. code-block:: python

     In [7]: cx[0].x = 5e-8
     In [8]: print cx[0].name, cx[0].x
     CXL1G2C19A 4.99974399176e-08


 
