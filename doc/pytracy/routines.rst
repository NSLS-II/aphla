
PyTracy Routines
=================

Structures
------------

globvalrec globval

============  ==============  ==================================================
   Type          Name                                      Use            
============  ==============  ==================================================
double        dPcommon;       dp for numerical differentiation
double        dPparticle;     energy deviation
double        delta_RF;       RF acceptance
Vector2       TotalTune;      transverse tunes
double        Omega   
double        U0;             energy lost per turn in keV
double        Alphac;         alphap
Vector2       Chrom;          chromaticities
double        Energy;         ring energy
long          Cell_nLoc;      number of elements
long          Elem_nFam;      number of families
long          CODimax;        maximum number of cod search before failing 
double        CODeps;         precision for closed orbit finder
Vector        CODvect;        closed orbit
int           bpm;            bpm number
int           hcorr;          horizontal corrector number
int           vcorr;          vertical corrector number
int           qt;             vertical corrector number
int           gs;             girder start marker
int           ge;             girder end marker
Matrix        OneTurnMat;     oneturn matrix
Matrix        Ascr            \ 
Matrix        Ascrinv         \ 
Matrix        Vr;             real part of the eigenvectors
Matrix        Vi;             imaginal par of the eigenvectors
\             \               \ 
bool          MatMeth;        matrix method
bool          Cavity_on;      if true, cavity turned on
bool          radiation;      if true, radiation turned on
bool          emittance;
bool          quad_fringe;    dipole- and quadrupole hard-edge fringe fields.
bool          H_exact;        "small ring" Hamiltonian.
bool          pathlength;     absolute path length
bool          stable          \ 
bool          Aperture_on     \ 
bool          EPU             \ 
bool          wake_on         \ 
\             \               \  
double        dE              energy loss
double        alpha_rad[DOF]  damping coeffs.
double        D_rad[DOF];     diffusion coeffs (Floquet space)
double        J[DOF];         partition numbers
double        tau[DOF];       damping times
bool          IBS;            intrabeam scattering
double        Qb;             bunch charge
double        D_IBS[DOF];     diffusion matrix (Floquet space)
Vector        wr;             \ 
Vector        wi;             real and imaginary part of eigenvalues
Vector3       eps;            3 motion invariants
Vector3       epsp;           transverse and longitudinal projected emittances
int           RingType;       1 if a ring (0 if transfer line)
============  ==============  ==================================================

Input Output Routines
-----------------------


.. py:function:: Read_Lattice(filename)

   Read the lattice file

   :arg filename: lattice file name. the name should have the extension .lat but in the function the name without the extension should be input.

Twiss Routines
--------------

.. py:function:: Ring_GetTwiss(chroma, dp)

   Computes Twiss functions w/ or w/o chromaticities
   for particle of energy offset dP
   matrix or da method

.. py:function:: Ring_GetTwiss(chroma, dp)

   :arg chroma: if true compute chromaticities and dispersion 
                if false dispersion is set to zero
   :arg  dp: energy offset
   :type chroma: Boolean


.. py:function:: s = getS()

   Get the position list at all elmements. 
   Ring_GetTwiss() or other twiss calculation routines should be run before.

   :arg s: position list at all elements
              0 is the starting position and n-th position is the position is at the end of the element.
   :rtype: List

.. py:function:: betax = getBetaX()

   Get the horizontal beta value list at all elmements. 
   Ring_GetTwiss() or other twiss calculation routines should be run before.

   :arg betax: horizontal beta value list at all elements
              0 is the starting points and n-th is the value at the end of the element.
   :rtype: List

.. py:function:: betay = getBetaY()

   Get the vertical beta value list at all elmements. 
   Ring_GetTwiss() or other twiss calculation routines should be run before.

   :return betay: vertical beta value list at all element
                    0 is the starting points and n-th is the value at the end of the element.
   :rtype: List
 
.. py:function:: alphax = getAlphaX()

   Get the horizontal alpha value list at all elmements. 
   Ring_GetTwiss() or other twiss calculation routines should be run before.

   :return alphax: horizontal alpha value list at all elements
                   0-th means the starting point and n-th is the value at the end of the element.
   :rtype: List

.. py:function:: alphay = getAlphaY()

   Get the vertical alpha value list at all elmements. 
   Ring_GetTwiss() or other twiss calculation routines should be run before.

   :return alphay: vertical alpha value list at all elements
                   0-th means the starting point and n-th is the value at the end of the element.
   :rtype: List

.. py:function:: etax = getEtaX()

   Get the horizontal dispersion list at all elmements. 
   Ring_GetTwiss() or other twiss calculation routines should be run before.

   :return etax: vertical dispersion slope at all elements
          0-th means the starting point and n-th is the value at the end of the element.
   :rtype: List

.. py:function:: etay = getEtaY()

   Get the vertical dispersion list at all elmements.
   Ring_GetTwiss() or other twiss calculation routines should be run before.

   :return etay: vertical dispersion list at all elements
         0-th means the starting point and n-th is the value at the end of the element.
   :rtype: List

.. py:function:: etaxp = getEtaXp()

   Get the horizontal dispersion slope list at all elmements. 
   Ring_GetTwiss() or other twiss calculation routines should be run before.

   :return etaxp: vertical dispersion slope list at all elements
         0-th means the starting point and n-th is the value at the end of the element.
   :rtype: List

.. py:function:: etayp = getEtaYp()

   Get the vertical dispersion slope list at all elmements.
   Ring_GetTwiss() or other twiss calculation routines should be run before.

   :return etayp: vertical dispersion slope list at all elements
         0-th means the starting point and n-th is the value at the end of the element.
   :rtype: List

.. py:function:: phix = getPhiX()

   Get the horizontal phase list at all elmements. 
   Ring_GetTwiss() or other twiss calculation routines should be run before.

   :return phix: horizontal phase list at all elements
         0-th means the starting point and n-th is the value at the end of the element.
   :rtype: List

.. py:function:: phiy = getPhiY()

   Get the vertical phase list at all elmements. 
   Ring_GetTwiss() or other twiss calculation routines should be run before.

   :return phiy: vertical phase list at all elements
     position list:  0-th means the starting point and n-th is the value at the end of the element.
   :rtype: List

.. py:function:: TraceABN(i0, i1, alpha, beta, eta, etap, dP)
 
   Get alpha and beta from i0 to i1

   :arg i0: start position
   :arg i1: end position
   :arg alpha: :math: [`\alpha_x`, :math:`\alpha_y`] at i0
   :type alpha: List
   :arg beta: :math: [`\beta_x`, :math:`\beta_y`] at i0
   :type beta: List
   :arg eta: :math: [`\eta_x`, :math:`\eta_y`] at i0
   :type eta: List
   :arg etap: :math: [`\eta_{px}`,d :math:`\eta_{py}`] at i0
   :type etap: List
   :arg dP: energy deviaiont

Tracking Routines
--------------------------

.. py:function:: x = getX()

   Get the horizontal displacement list at all elmements. 
   getCOD() or other tracking routines should be run before.

   :return x: longitudinal coordinates at all elements
         0-th means the starting point and n-th is the value at the end of the element.
   :rtype: List

.. py:function:: xp = getXp()

   Get the horizontal momentum list at all elmements. 
   getCOD() or other tracking routines should be run before.

   :return xp: longitudinal coordinates at all elements
         0-th means the starting point and n-th is the value at the end of the element.
   :rtype: List

.. py:function:: y = getY()

   :return y: longitudinal coordinates at all elements
         0-th means the starting point and n-th is the value at the end of the element.
   :rtype: List

.. py:function:: yp = getYp()

   Get the vertical momentum list at all elmements. 
   getCOD() or other tracking routines should be run before.

   :return yp: longitudinal coordinates at all elements
         0-th means the starting point and n-th is the value at the end of the element.
   :rtype: List

.. py:function:: dp = getDp()

   Get the momentum deviaion list at all elmements. 
   getCOD() or other tracking routines should be run before.

   :return dp: longitudinal coordinates at all elements
         0-th means the starting point and n-th is the value at the end of the element.
   :rtype: List

.. py:function:: dt = getDt()

   Get the longitudinal displacement in time list at all elmements. 
   getCOD() or other tracking routines should be run before.

   :return dt: longitudinal coordinates at all elements
         0-th means the starting point and n-th is the value at the end of the element.
   :rtype: List

.. py:function:: [fx, fz, nb_freq] = Get_NAFF(nterm, ndata, T)

   Compute quasiperiodic approximation of a phase space trajectory
   using NAFF Algorithm ((c) Laskar, IMCCE)

   :arg nterm: number of frequencies to look for
             if not multiple of 6, truncated to lower value
   :arg ndata: size of the data to analyse
   :arg T:     6D vector to analyse

   :return fx: frequencies found in the H-plane
   :return fz: frequencies found in the V-plane
   :return nb_freq: number of frequencies found out in each plane

..


    

  	    double  Tab[6][NTURN];
	    int     nb_freq[2] = { 0, 0 };  /* frequency number to look for */

	    /* initializations */^M
	    for (i = 0; i < nterm; i++)
	    {
	        fx[i] = 0.0; fz[i] = 0.0;
	    }
	    /* end init *
	    Get_NAFF(nterm, ndata*6, Tab, fx, fz, nb_freq);

	    PyObject * PyRet = PyList_New(3);
	    PyObject * Fx = PyList_New(nb_freq[0]);
	    PyObject * Fz = PyList_New(nb_freq[1]);
	    PyObject * Nb_Freq = PyList_New(2);

	    for (i=0; i<nb_freq[0]; ++i) PyList_SetItem(Fx, i, PyFloat_FromDouble(fx[i]));
	    for (i=0; i<nb_freq[1]; ++i) PyList_SetItem(Fz, i, PyFloat_FromDouble(fz[i]));
	    for (i=0; i<2; ++i) PyList_SetItem(Nb_Freq, i, PyLong_FromLong(nb_freq[i]));

	    PyList_SetItem(PyRet, 0, Fx);
	    PyList_SetItem(PyRet, 1, Fz);
	    PyList_SetItem(PyRet, 2, Nb_Freq);

	    return PyRet;


.. py:function::  [status, Tx] = Trac_Simple(x, px, y, py, dp, nmax)

   Single particle tracking around the closed orbit for NTURN turns
   The 6D phase trajectory is saved in a array

   :arg x: 
   :arg px:
   :arg y:
   :arg py: 4 transverses coordinates
   :arg dp:           energy offset
   :arg nmax:         number of turns
   :arg pos:          starting position for tracking
   :arg aperture:     global physical aperture
   :return status:   True if beam survived otherwise False
   :return Tx:        saved 6 x nmax coordinates


.. py:function::  [xis, xiz] = GetChromTrac(Nb, Nbtour, emax)

   Computes chromaticities by tracking

   :arg Nb:      point number
   :arg Nbtour:  turn number
   :arg emax:    energy step

   :return xix: horizontal chromaticity
   :return xiz: vertical chromaticity




// 4D tracking in normal or Floquet space over nmax turns

.. py:function:: [lastn, lastpos] = track(file_name, ic1, ic2, ic3, ic4, dp, nmax, floqs, double f_rf)

   Single particle tracking around closed orbit:
   Track particle nmax turns around the closed orbti. Data is
   stored in the file tracking.dat. Ring_Gettwiss must be called first.

   :arg ic1: 
   :arg ic2:
   :arg ic3:
   :arg ic4: 4 transverses coordinates
   :arg dp:           energy offset
   :arg nmax:         number of turns
   :arg floqs:
   :arg f_rf:
   :return lastn:
   :return lastpos:

============================= ======== =======================================
         Output                floqs
============================= ======== =======================================
       Phase Space               0     [x, px, y, py, delta, ct]
       Floquet Space             1     [x^, px^, y^, py^, delta, ct]
       Action-Angle Variables    2     [2Jx, phx, 2Jy, phiy, delta, ct]
============================= ======== =======================================

example::

	Ring_gettwiss(true, delta);
	track(x0, px0, y0, py0, delta,nturn, lastn, lastpos, true);
	if lastn <> nturn then writeln('Particle lost duringturn ', nturn:1, ' , at element ', lastpos:1);


.. py:function:: xf = getfloqs(x)

   Transform to Floquet space

   :arg	x:
   :return xf:


.. py:function:: [x, px, y, py] = gettrack(filename, nbuff)

   Get tracking data from file. Track must be called first.

   :arg fname:
   :arg nbuff:
   :return : [x, px, y, py]

example::
	Ring_gettwiss(true, delta);
	last = track('track.data', x0, px0, y0, py0, delta, nturn, 1, 0.0);
	if lastn <> n then writeln('Particle lost during turn', n:1, ' , at element ', lastpos:1);
	out = gettrack('track.data', 512)n, x, px, y, py);



.. py:function:: rout = getdynap(rin, phi, delta, eps, nturn, floqs)

   Get dynamical aperture

   :arg rin:
   :arg phi:
   :arg delta:
   :arg eps:
   :arg nturn:
   :arg flos:
   :type floqs: Bool
   :return rout:
   

Alignment Routines
-------------------------------------
.. py:function:: misalign_rms_elem(Fnum, Knum, dx_rms, dy_rms, dr_rms, new_rnd)

   Assign random misalignment errors for the given element

   :arg Fnum: Family number
   :arg Knum: Kid number
   :arg dx_rms: rms for the misalignment in horizontal direction
   :arg dy_rms: rms for the misalignment in vertical direction
   :arg dr_rms: rms for the misalignment in longitudinal direction
   :arg new_rnd: If True. give the misalignment to the elements
   :type new_rnd: Bool

.. py:function:: misalign_sys_elem(Fnum, Knum, dx_sys, dy_sys, dr_sys)

   Assign systematic misalignment errors for the given element

   :arg Fnum: Family number
   :arg Knum: Kid number
   :arg dx_sys: Systematic misalignment in horizontal direction
   :arg dy_sys: Systematic misalignment in vertical direction
   :arg dr_sys: Systematic misalignment in longitudinal direction

.. py:function:: misalign_rms_fam(Fnum, dx_rms, dy_rms, dr_rms, new_rnd)

   Assign random misalignment errors for the given family

   :arg Fnum: Family number
   :arg dx_rms: rms for the misalignment in horizontal direction
   :arg dy_rms: rms for the misalignment in vertical direction
   :arg dr_rms: rms for the misalignment in longitudinal direction
   :arg new_rnd: If True. give the misalignment to the elements
   :type new_rnd: Bool

.. py:function:: misalign_sys_fam(Fnum, dx_sys, dy_sys, dr_sys)

   Assign systematic misalignment errors for the given family

   :arg Fnum: Family number
   :arg dx_sys: Systematic misalignment in horizontal direction
   :arg dy_sys: Systematic misalignment in vertical direction
   :arg dr_sys: Systematic misalignment in longitudinal direction

.. py:function:: misalign_rms_type(type, dx_rms,dy_rms, dr_rms, new_rnd)

   Assign random misalignment errors for the given type

   :arg type: Element type
   :arg dx_rms: rms for the misalignment in horizontal direction
   :arg dy_rms: rms for the misalignment in vertical direction
   :arg dr_rms: rms for the misalignment in longitudinal direction
   :arg new_rnd: If True. give the misalignment to the elements
   :type new_rnd: Bool

.. py:function:: misalign_sys_type(type, dx_sys, dy_sys, dr_sys)

   Assign systematic misalignment errors for the given type

   :arg type: Element type
   :arg dx_sys: Systematic misalignment in horizontal direction
   :arg dy_sys: Systematic misalignment in vertical direction
   :arg dr_sys: Systematic misalignment in longitudinal direction




Element Info Routines
-------------------------------

.. py:function:: Fname = getElemName(Fnum)

   Get Family Name by the Number 
 
   :arg Fname:
	 Family number
   :return Fnum:
	 Family name

.. py:function:: Fnum = getFnumByName(Fname)

   Get Family Number by the name
 
   :arg Fname: Family name
   :return Fnum: Family number

.. py:function:: Elem_GetPos(Fnum, Knum)

   Get the position in the lattice

   :arg Fnum: Family number
   :arg Knum: kid number in the family
   :return Enum: Element position in the lattice (1 - globval.cell_nLoc)

.. py:function:: nKid = GetnKid(Fnum) 

   Get number of elements (kids) in for a given family

   :arg Fnum: Family number
   :arg nKid: Number of kids in the family

Element Length Routines
--------------------------------
 
.. py:function:: L = get_L(Fnum, Knum)

   Get the length of the element

   :arg Fnum: Family number
   :arg Knum: kid number in the family
   :return L: Length of the element
 
.. py:function:: set_L(Fnum, Knum, L)

   Set the length of the element
 
   :arg Fnum: Family number
   :arg Knum: kid number in the family
   :arg L: length

.. py:function:: set_L_all(Fnum,  L)

   Set the length of all the element of the family.

   :arg Fnum: Family number
   :arg L: length

.. py:function:: set_dL(Fnum, Knum, dL)

   Change the length of the element
 
   :arg Fnum: Family number
   :arg Knum: kid number in the family
   :arg dL: variation of the length

Multipole Routines
--------------------

.. py:function:: [bn, an] = get_bn_design_elem(Fnum, Knum, Order)

   Get the design values of normal and skew components of the multipole element

   :returns bn: design
   :returns an: skew
 
   :arg Fnum: Family number 
   :arg Knum: Kid number in the family
   :arg Order: Order of multipole

   return:
     [bn, an]: design values of normal and skew compoent of the multipole

.. py:function:: [bn, an] = get_bn_rnd_elem(Fnum, Knum, Order)

   Get the normal and skew random errors of Order for the multipole element
 
   :arg Fnum: Family number
   :arg  Knum: Kid number in the family
   :arg Order: Order of multipole

   :return [bn, an]: Normal and skew Random errors for the given Order

.. py:function:: [bnL, anL] = get_bnL_design_elem(Fnum, Knum, Order)

   Get the design values of normal and skew components of the multipole element multiplied by the length
 
   :arg Fnum: Family number
   :arg Knum: Kid number in the family
   :arg Order: Order of multipole
   :return [bnL, anL]: design values of normal and skew compoent of the multipole multiplied by the length

.. py:function:: set_bn_design_elem(Fnum, Knum, Order, bn, an)

   Set the design values of normal and skew components of the multipole element
 
   :arg Fnum: Family number
   :arg Knum: Kid number in the family
   :arg Order: Order of multipole
   :arg bn: Order'th normal component for the multipole
   :arg an: Order'th skew component for the multipole

.. py:function:: set_dbn_design_elem(Fnum, Knum, Order, dbn, dan)

   Increase (Decrease) the design values of normal and skew components of the multipole element
 
   :arg Fnum: Family number
   :arg Knum: Kid number in the family
   :arg Order: Order of multipole
   :arg dbn: Change in Order'th normal component for the multipole
   :arg dan: Change in Order'th skew component for the multipole

.. py:function:: set_bn_design_fam(Fnum, Order, bn, an)
 
   Set the design values of normal and skew components of all the multipole elements for the family
 
   :arg Fnum: Family number
   :arg Knum: Kid number in the family
   :arg Order: Order of multipole
   :arg bn: Order'th normal component for the multipole
   :arg an: Order'th skew component for the multipole

.. py:function:: set_dbn_design_fam(Fnum, Order, dbn, dan)

   Increase (Decrease) the design values of normal and skew components of all the multipole elements for family
 
   :arg Fnum: Family number
   :arg Knum: Kid number in the family
   :arg Order: Order of multipole
   :arg dbn: Change in Order'th normal component for the multipole
   :arg dan: Change in Order'th skew component for the multipole

.. py:function:: set_bnL_design_elem(Fnum, Knum, Order, bnL, anL)

   Set the design values of bn*L and an*L  of the multipole element
 
   :arg Fnum: Family number
   :arg Knum: Kid number in the family
   :arg Order: Order of multipole
   :arg bnL: Order'th normal component for the multipole multiplied by the length
   :arg anL: Order'th skew component for the multipole multiplied by the length

.. py:function:: set_dbnL_design_elem(Fnum, Knum, Order, dbnL, danL)

   Increase (Decrease) the design values of normal and skew components of the multipole element
 
   :arg Fnum: Family number
   :arg Knum: Kid number in the family
   :arg Order: Order of multipole
   :arg dbnL: Change in Order'th normal component for the multipole multiplied by the length
   :arg danL: Change in Order'th skew component for the multipole multiplied by the length

.. py:function:: set_dbnL_design_fam(Fnum, Order, dbnL, danL) 

   Increase (Decrease) the design values of bn*L and an*L of all the multipole elements for the family
 
   :arg Fnum: Family number
   :arg Knum: Kid number in the family
   :arg Order: Order of multipole
   :arg dbnL: Change in Order'th normal component for the multipole
   :arg danL: Change in Order'th skew component for the multipole

.. py:function:: set_bnL_design_fam(Fnum, Order, bnL, anL)

   Set the design values of bn*L and an*L  of all the multipole elements for the family
 
   :arg Fnum: Family number
   :arg Knum: Kid number in the family
   :arg Order: Order of multipole
   :arg bnL: Order'th normal component for the multipole multiplied by the length
   :arg anL: Order'th skew component for the multipole multiplied by the length

.. py:function:: set_bnL_design_type(Type, Order, bnL, anL) 

   Set the design values of bn*L and an*L  of all the multipole elements for the given type
 
   :arg Type: Multipole type (1: dipole, 2: quadrupole, 3: sextupole, ...)
   :arg Order: Order of multipole
   :arg bnL: Order'th normal component for the multipole multiplied by the length
   :arg anL: Order'th skew component for the multipole multiplied by the length

.. py:function:: set_bnL_sys_elem(Fnum, Knum, Order, bnL, anL)

   Set the systematic errors in bn*L and an*L  for the multipole element
 
   :arg Fnum: Family number
   :arg Knum: Kid number in the family
   :arg Order: Order of multipole
   :arg bnL: Order'th normal component for the multipole multiplied by the length
   :arg anL: Order'th skew component for the multipole multiplied by the length

.. py:function:: set_bnL_sys_fam(Fnum, Order, bnL, anL)

   Set the systematic errors in bn*L and an*L  for all the multipole elements of the family
 
   :arg Fnum: Family number
   :arg Order: Order of multipole
   :arg bnL: Order'th normal component for the multipole multiplied by the length
   :arg anL: Order'th skew component for the multipole multiplied by the length

.. py:function:: set_bnL_sys_type(Type, Order, bnL, anL) 

   Set the systematic errors in bn*L and an*L  for all the multipole elements of the given type
 
   :arg Type: Multipole type (1: dipole, 2: quadrupole, 3: sextupole, ...)
   :arg Order: Order of multipole
   :arg bnL: Order'th normal component for the multipole multiplied by the length
   :arg anL: Order'th skew component for the multipole multiplied by the length

.. py:function:: set_bnL_rms_elem(Fnum, Knum, Order, bnL, anL, new_rnd)

   Set the normal width for the random errors in bn*L and an*L for the multipole element
   If new_rnd is True the random errors are refrshed.
 
   :arg Fnum: Family number
   :arg Knum: Kid number in the family
   :arg Order: Order of multipole
   :arg bnL: Order'th normal width for bn*L random errors
   :arg anL: Order'th normal width for an*L random errors
   :arg new_rnd: Boolean to refresh the random errors for the multipoles.
         :py:func:`InitRand` should be executed before to be True.

.. py:function:: set_bnL_rms_fam(Fnum, Order, bnL, anL, new_rnd)

   Set the normal width for the random errors in bn*L and an*L for all the multipole elements of the family
   If new_rnd is True the random errors are refrshed.
 
   :arg Fnum: Family number
   :arg Order: Order of multipole
   :arg bnL: Order'th normal width for bn*L random errors
   :arg anL: Order'th normal width for an*L random errors
   :arg new_rnd: Boolean to refresh the random errors for the multipoles.
         :py:func:`InitRand` should be executed before to be True.

.. py:function:: set_bnL_rms_type(Fnum, Order, bnL, anL, bool new_rnd) 

   Set the normal width for the random errors in bn*L and an*L for all the multipole elements of the given type
   If new_rnd is True the random errors are refrshed.
 
   :arg Fnum: Family number
   :arg Order: Order of multipole
   :arg bnL: Order'th normal width for bn*L random errors
   :arg anL: Order'th normal width for an*L random errors
   :arg new_rnd: Boolean to refresh the random errors for the multipoles.
         :py:func:`InitRand` should be executed before to be True.

.. py:function:: set_bnr_sys_elem(Fnum, Knum, Order, bnr, anr)

   Set the design values of normal and skew components of the multipole element by multiplying bnr anr to the design values.
 
   :arg Fnum: Family number
   :arg Knum: Kid number in the family
   :arg Order: Order of multipole
   :arg bnr: Order'th normal component ratio to the design value
   :arg anr: Order'th skew component ratio to the design value

.. py:function:: set_bnr_sys_fam(Fnum, Order, bnr, anr)

   Set the systematic errors in relative values for all the multipole elements of the family
   Order'th systematic errors will be given as bnr*(design value) and anr*(design value) for normal and skew components, respectively.
  
   :arg Fnum: Family number
   :arg Order: Order of multipole
   :arg bnr: Order'th normal systematic error component ratio to the design value
   :arg anr: Order'th skewsy stematic error component ratio to the design value

.. py:function:: set_bnr_sys_type(Type, Order, bnr, anr) 

   Set the systematic errors in relative values for all the multipole elements for the given type
   Order'th systematic errors will be given as bnr*(design value) and anr*(design value) for normal and skew components, respectively.
 
   :arg Type: Multipole type (1: dipole, 2: quadrupole, 3: sextupole, ...)
   :arg Order: Order of multipole
   :arg bnL: Order'th normal systematic error component ratio to the design value
   :arg anL: Order'th skewsy stematic error component ratio to the design value

.. py:function:: set_bnr_rms_elem(Fnum, Knum, Order, bnr, anr, bool new_rnd)

   Set the normal width of the random errors for the element by multiplying bnr and anr to the design values.
   Order'th systematic errors will be given as bnr*(design value) and anr*(design value) for normal and skew components, respectively.
   
   :arg Fnum: Family number
   :arg Knum: Kid number in the family
   :arg Order: Order of multipole
   :arg bnr: Order'th normal component ratio to the design value
   :arg anr: Order'th skew component ratio to the design value
   :arg new_rnd: Boolean to refresh the random errors for the multipoles.
         :py:func:`InitRand` should be executed before to be True.
   

.. py:function:: set_bnr_rms_fam(Fnum, Order, bnr, anr, bool new_rnd)

   Set the normal width of the random errors for all the family elements by multiplying bnr and anr to the design values.
   Order'th systematic errors will be given as bnr*(design value) and anr*(design value) for normal and skew components, respectively.
   
   :arg Fnum: Family number
   :arg Order: Order of multipole
   :arg bnr: Order'th normal component ratio to the design value
   :arg anr: Order'th skew component ratio to the design value
   :arg new_rnd: Boolean to refresh the random errors for the multipoles.
         :py:func:`InitRand` should be executed before to be True.

.. py:function:: set_bnr_rms_type(int type, Order, bnr, anr, bool new_rnd) 

   Set the normal width of the random errors for all the family elements by multiplying bnr and anr to the design values.
   Order'th systematic errors will be given as bnr*(design value) and anr*(design value) for normal and skew components, respectively.
   
   :arg Fnum: Family number
   :arg Order: Order of multipole
   :arg bnr: Order'th normal component ratio to the design value
   :arg anr: Order'th skew component ratio to the design value
   :arg new_rnd: Boolean to refresh the random errors for the multipoles.
         :py:func:`InitRand` should be executed before to be True.

.. py:function:: Reset_Mpole(int Fnum)

   Reset all the multipole strengths of all the family's elements to the values in the input lattice file.

   :arg Fnum: Family number

.. py:function:: [xout,lastpos] = Cell_Pass(i0, i1, x0)

   Track particle from i0 to i1

   :arg i0: initial position
   :arg i1: final position
   :arg x0: initial conditions (x, px, y, py, delta, ctau)
   :return xout: final conditions (x, px, y, py, delta,ctau)
   :return lastpos: last position (# i1 if particle is not lost)

.. py:function:: [matout, lastpos] = Cell_Pass_M(i0, i1, xref, mat);

   Track matrix from i0 to i1 around ref. orbit using transfer matrix

   :arg i0: initial position
   :arg i1: final position
   :arg xref; initial reference orbit 
   :arg mat: initial transfer matrix

   :return matout: final transfer matrix
   :return lastpos: last position (# i1 if particle is not lost)

.. py:function:: [xout, lastpos] = Cell_fPass(x0)

   Fast tracking of particle using concatenated lattice(:py:func:`Cell_Concat`)

   :arg x0: initial conditions (x, px, y, py, delta, ctau)
   :return xout: final conditions (x, px, y, py, delta,ctau)
   :return lastpos: last position (# i1 if particle is not lost)

.. py:function:: [matout, lastpos] = Cell_fPass_M(xref, mat, lastpos)

   Fast tracking of matrix using concatenated lattice (:py:func:`Cell_Concat`)

   :arg xref; initial reference orbit 
   :arg mat: initial transfer matrix

   :return matout: final transfer matrix 
   :return lastpos: last position (# i1 if particle is not lost)

.. py:function:: Cell_Concat(dP)

   Concatenate lattice for fast tracking with momentum deviation of dP

   :arg dP:
         Modentum deviaion

.. py:function:: getCOD(imax, eps, dP, lastpos);

   Closed orbit finder. If globval.MatMeth is true Matrix mathod is used otherwise 

   :arg imax: maximum number of iteration
   :arg eps: precision
   :arg dP: Mommendum deviation


   :return laspos:

.. py:function:: get_alphac();

   obtain the momentum compaction factor and set globval.Alphac

.. py:function:: [b1, b2, b3] = get_alphac2()

   obtain the higher orber momentum compation factor

   :return [b1, b2, b3]: :math:`\alpha_c=b1+b2\delta+b3\delta^2`


Correction routines
----------------------

.. py:function:: Ring_Fittune([nux, nuy], eps, [nqf, nqd], [qf], [qd], dkL, imax)

   Fit tunes using two family of quadrupoles with Linear method

   :arg [nux, nuy]: target tunes
   :arg eps: precision
   :arg [nqf, nqd]: number of quad of family qf and qd
   :arg qf: position of qf magnets
   :arg qd: position of qd magnets
   :arg dKL: variation on strengths
   :arg imax: maximum number of iteration

.. py:function:: FitTune(qf, qd, nux, nuy)

   call Ring_Fittune using selected families with eps= :math:`10^{-6}`, dkL= 0.01, imax = 10

   :arg qf: family number of focussing quadrupole
   :arg qd: family number of defocussing quadrupole
   :arg nux: target horizontal tune
   :arg nuy: target vertical tune

.. py:function:: Ring_Fitchrom([ksix, ksiy], eps, [nsf, nsd], [sf], [sd],  dkpL, imax)

   Fit chromaticities with two family of sextupoles using

   :arg [ksix, ksiy]: target chromaticities
   :arg eps: precision
   :arg [nqf, nqd]: number of quad of family qf and qd
   :arg sf: position of sf magnets
   :arg sd: position of sd magnets
   :arg dKpL: variation on strengths
   :arg imax: maximum number of iterationLinear method
   
.. py:function:: FitChrom(sf, sd, ksix, ksiy)

   call Ring_Fitchrom with selected families and eps  = :math:`10^{-5}`, dkpL = 0.01, imax = 10

   :arg sf: family number of focussing   sextupole
   :arg sd: family number of defocussing sextupole
   :arg ksix: target horizontal chromaticity
   :arg ksiy: target vertical chromaticity

.. py:function:: Ring_FitDisp(pos, eta, eps, nq, [q], dkL, imax)

   Fit dispersion at the given position with quadrupoles using
   Linear method

   :arg pos: target position
   :arg eta: target dispersion
   :arg eps: precision
   :arg nq: number of quadrupoles
   :arg q: quadrupoles
   :arg dKL: variation on strengths
   :arg imax: maximum number of iteration

.. py:function:: FitDisp(q, pos, eta)

   call Ring_FitDisp with selected family and eps  = :math:`10^{-10}`, dkL  = 0.001, imax = 10

   :arg q: family number of quadrupole
   :arg pos: target position
   :arg eta: target dispersion


Other Routine
-----------------------------

.. py:function:: [nux, nuy] = GetNu(mat)

   Get the horizontal and vertical tunes for given one-turn matrix

   :arg mat: one-turn matrix in nested list. should be at least 4x4 matrix
   :return [nux, nuy]: Tune


.. py:function:: Cell_SetdP(dP)

   Give the energy deviaion dP

   :arg dP: Energy deviaion


.. py:function:: InitRand(Seed, rms_cut)

   Initialize random numbers

   :arg Seed: seed number
   :arg rms_cut: maximum limit in normal width when assigning the random values


