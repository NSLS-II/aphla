
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


