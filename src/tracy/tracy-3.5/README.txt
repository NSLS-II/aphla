Tracy-3

Author: Johan Bengtsson

Requirements:

  1. GNU autoconf and automake environment.

  2. GNU C++ compiler: gcc

  3. Numerical Recipes in C (with support for "double").
     Assumed directory structure:

       $NUM_REC/lib		libnum_rec.a
       $NUM_REC/inc		nrutil.h, nr.h

To install:

  1. Define the environment variable:

       $NUM_REC = <path to Numerical Recipes library>

  2. tar -xvzf <tar ball name> 

  3. cd tracy-3.0

  4. ./bootstrap

  5. ./configure

  6.  cd tracy/wrk

  7. make

  8. ./main lattice/ALBA
