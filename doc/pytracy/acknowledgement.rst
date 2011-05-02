Acknowledgement
===============

This code has its origin in an idea initially realized by H. Nishimura, i.e. to use a standard programming language as the command language for a tracking code.
In particular, startingfrom N. Wirth's Pascal-S compiler/interpreter (a strict subsetof Pascal), in collaboration with E. Forest, 
the standard procedures and functions of Pascal were enhanced to include routines for beam dynamics.

However, the initial code was developed for theshort terms needs in the lattice design of the Advanced LightSource (ALS) at LBL.
The code therefore finally reached a state where it could hardly be maintained or modified.
The currentcode is a compromize (e.g. Pascal is still used rather than e.g.C or C++) that empasizes generality and flexibility in the user interface, 
and is built from the ideas and experiences gainedfrom the earlier codes.

One working constraint has been to keep backwards compability.
However, this has been sacrificed in cases where generality or flexibility would have to be compromized.
It grew out from an initial effort for an on-line model for the Advanced Light Source (ALS) 
but finally found little use due to an overall lack of systematic approach in the commissioning process.

I would like to thank E. Forest for continued guidance concerningthe single particle dynamics and 
I am also very grateful to S.Chattopadhyay head of the Center of Beam Physics for his continued support during this work.

