Introduction
============

PyTracy is the collection of interface routines of Tracy library and this manual describes the routines as well as the background physics.

The routines can be classified as following;

* Input Output Routines

* Twiss Routines

* Tracking Routines

* Element Info Routines

* Element Length Routines

* Multipole Routines

* Correction routines

* Other Routine

Tracy library has its origin in an idea initially realized by H. Nishimura, i.e. to use a standard programming language as the command language for a tracking code.  
In particular, starting from N. Wirth's Pascal-S compiler/interpreter (a strict subsetof Pascal), in collaboration with E. Forest, the standard proceduresand functions of Pascal were enhanced to include routines for beam dynamics.

However, the initial code was developed for the short terms needs in the lattice design of the Advanced LightSource (ALS) at LBL.  
It grew out from an initial effort for an on-line model for the Advanced Light Source (ALS) and has been developed absorbing the 
The basic design goals are:

* A clean and straightforward implementation of a magnet. 

  - It is defined by the coefficients in the multipole expansion. 
  - Mis-alignmentsare implemented by applying a Euclidian transformation at the entrance and exit of each element. 
  - All quantities can be accessed and modified from the input file.
  - Choice of integrator: matrix style and 2:nd or 4:th order symplectic integrator.
  - Referenced induvidually or as families.

* Non-linear optimizer (downhill simplex) and singular value decomposition.

* Text files, include files, passing of arrays and records to physics routines (on the Pascal-S stack)

* Access to all lattice parameters through the record structure of a magnet, matrix calculations,line numbers.

* Linear DA library compatible to simplify possible relinking to M. Berz general DA library.

* Compiled input files.

* Correction of a few Pascal-S bugs.

* Implementing generic routines at the Pascal-S level and high level routines as include files.

* Structured and generic compact code.

