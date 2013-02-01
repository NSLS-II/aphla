
Introduction
=============

This manual describes ``aphla`` the Accelerator Physics High Level
Applications for storage ring commissioning and beam studies. Particularly we
will use it for the `NSLS-II <http://www.bnl.gov/nsls2>`_ project.

``aphla`` is a package of both libraries and Graphical User Interface (GUI)
applications.  Besides the commonly used applications, like Beam based
alignment, the HLA includes a set of APIs (Application Programming Interface)
which is used for writing further scripts and interactive controls.


Quick Start
--------------

This is for the very impatient ones at NSLS-II. See :doc:`tutorial`

- Remote login the server: *ssh -Y youraccount@lsasd2.ls.bnl.gov*
- Enter IPython::
     $ ipython -pylab

- Import `aphla`

.. doctest::
    
     >>> import aphla as ap

- Initialize the "NSLS2V2" (virtual accelerator lattice structure)

.. doctest::

     >>> ap.machines.init("nsls2v2")

- Get the orbit

.. doctest::

     >>> d = ap.getOrbit()
     >>> x, y, s = ap.getOrbit(spos=True).T

- Get a list of correctors, print the name and strength of one corrector.

.. doctest::

     >>> cx = ap.getElements('ch*c19*')
     >>> print cx[0].name, cx[0].x
     ch2g6c19b 0.0

- Set the corrector and read the new setting

.. doctest::

     >>> cx[0].x = 5e-8
     >>> print "%s %.3e" % (cx[0].name, cx[0].x)
     cxl1g2c19a 5.000e-08


.. testcleanup::

     cx[0].x = 0.0


