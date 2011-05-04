Physics
=====================


The Hamiltonian
---------------



The Hamiltonian describing the motion of a charged particlearound a reference trajectory in an external magnetic field isgiven by

.. math::

   H_1\equiv-p_s=-(1+h_{ref}x)[\frac{q}{p_0}A_s+sqrt{1-\frac{2}{\beta}p_t+p_t^2-(p_x-\frac{q}{p_0}Ax)^2-(p_y-\frac{q}{A_y})^2}]-\frac{1}{\beta}p_t

where

.. math::

   p_t\equiv-\frac{E-E_0}{p_0c},\ h_{ref}=\frac{1}{\rho_{ref}}

and

.. math::

   {\bf B}=\nabla\times{\bf A}


:math:`\beta` is the relativistic factor and we are using the phase space coordinates :math:`(x,p_x,y,p_y,ct,p_t)`.
These are deviations from a particle following the refernce trajectory with the local curvature :math:`h_{ref}` and energy :math:`E_0`.
In this curvilinear system[Bengtsson]

.. math::

   \begin{array}{lll}
   B_x&=&\frac{1}{1+h_{ref}x}\frac{\partial A_y}{\partial s}-\frac{\partial A_s}{\partial y} \\
   B_y&=&\frac{h_{ref}}{1+h_{ref}x}A_s+\frac{\partial A_s}{\partial x}-\frac{1}{1+h_{ref}x}\frac{\partial A_x}{\partial s}\\
   B_s&=&\frac{\partial A_x}{\partial y}-\frac{\partial A_y}{\partial x}
   \end{array}


Introducing the canonical transformation


.. math::

   \begin{array}{lll} 
   F_2&=&\frac{1}{\beta}[1-\sqrt{1+\beta^2(2\delta+\delta^2)}](ct+\frac{s}{\beta})+\delta s,\\
   H_2&=&H_1+\frac{\partial F_2}{\partial s},\\
   -cT&=&\frac{\partial F_2}{\partial\delta}=-\frac{\beta(1+\delta)}{\sqrt{1+\beta^2(2\delta+\delta^2)}}(ct+\frac{s}{\beta})+s\\
   p_t&=&\frac{\partial F_2}{\partial(ct)}=\frac{1}{\beta}[1-\sqrt{1+\beta^2(2\delta+\delta^2)}]
   \end{array}

and

.. math::

   \delta\equiv\frac{p-p_0}{p_0}

where :math:`p_0` is the momentum of the reference particle. We obtain

.. math::

   H_2=-(1+h_{ref}x))[\frac{q}{p_0}A_s+\sqrt{(1+\delta)^2-(p_x-\frac{q}{p_0}Ax)^2-(p_y-\frac{q}{A_y})^2}]+\delta

using the phase space coordinates :math:`(x,p_x,y,p_y,-cT,\delta)`. Note that :math:`T` is not the time of flight :math:`t` which is given by

.. math::

   ct=\frac{1}{\beta}\left[\frac{\sqrt{1+\beta^2(2\delta+\delta^2)}}{1+\delta}(cT+s)-s\right]

We will only consider the ultra-relativistic limit for which

.. math::

   p_t\rightarrow-\delta,\ ct\rightarrow cT\qquad{\rm when}\quad beta\rightarrow1

It is straightforward to generalize if this approximation is not valid.

In the case of a sectorbend we have

.. math::

   \frac{q}{p_0}A_s=-\frac{1}{2}(1+h_Bx)

We linearize the equations of motion by expanding the Hamiltonians to second order

.. math::

   H_3=\frac{p_x^2+p_y^2}{2(1+\delta}-\frac{q}{p_0}A_s+\frac{1}{2}(h_Bx)^2-h_Bx\delta+O(3)

with :math:`h_{ref}` has been chosen equal to :math:`h_B` and by assuming the curvature :math:`h_{ref}` to be small (*large ring*).
Using the multipole expansion

.. math::

   B_y+iB_x=B\rho_{ref}\sum^N_{n=1}(ia_n+b_n)(x+iy)^{n-1}

neglecting end-fields. It is clear that

.. math::

   \frac{q}{p}=-\frac{1}{B\rho_B}

which is known as the *magnetic rigidity*. It follows that

.. math::

   h_B=b_1

With a suitable choice of gauge we find the corresponding vector potential to be

.. math::

   \begin{array}{lll} 
   \frac{q}{p_0}A_x&=&0, \\
   \frac{q}{p_0}A_y&=&0, \\
   \frac{q}{p_0}A_s&=&-Re\sum_{n=1}^N\frac{1}{n}(ia_n+b_n)(x+iy)^n
   \end{array}

where :math:`a_n` and :math:`b_n` are the skew and normal multipole coefficients.

Hamilton's equations are

.. math::

   \begin{array}{lllll}x'&=&\frac{\partial H}{\partial p_x}&=&\frac{p_x}{1+\delta}+O(2),\\
                     p_x'&=&-\frac{\partial H}{\partial x} &=&\frac{q}{p_0}B_y+h_B\delta-h_B^2+O(2),\\
                       y'&=&\frac{\partial H}{\partial p_y}&=&\frac{p_y}{1+\delta}+O(2),\\
                     p_y'&=&-\frac{\partial H}{\partial y} &=&-\frac{q}{p_0}B_x+O(2),\\
                     -cT'&=&\frac{\partial H}{\partial \delta}&=&h_Bx+O(2)\end{array}


:math:`4\times5` Matrix Formalism
-----------------------------------

Matrix style codes computes the solutions of Hamilton's equations as Taylor expansion around a refernce curve :math:`x_{ref}`

.. math::

   x_j^f=\sum_kM_{jk}x_k^i+\sum_{kl}x_k^ix_l^i


where :math:`{\bf x}=(x,p_x,y,p_y,\delta)` and :math:`M_{jk}` is the Jacobian

.. math::

   M=\frac{\partial(x^f,p_x^f,y^f,p_y^f,\delta)}{\partial(x^i,p_x^i,y^i,p_y^i,\delta)}|_{{\bf x}_i={\bf x}_{ref}}

In other words, :math:`M` is the :math:`4\times5` linear transport matrix acting on the phase space vector :math:`\bar x=(x,p_x,y,p_y,\delta)`.
It is customary to choose the closed orbit as the reference curve for circular accelerators. Note that, :math:`x_k^i` is a contravariant vector, 
:math:`x_k^ix_l^i` a contravariant second rank tensor etc.

If only linear terms are kept

.. math::

   {\bf x}^f=M{\bf x}^i+O({\bf x}^2)

The motion is symplectic since the equationof motions are derived from a Hamiltonian. It follows that

.. math::

   \det M=1

Since the higher order terms violates the symplectic condition, thin kicks are used for the higher order multipoles. 
The magnet model used for :math:`4\times5` matrix style calculations is shown in Fig. 1. Each magnet is broken up into two halves, represented by a linear matrix,
and a thin kick at the center, containing the higher order multipoles.


Extended :math:`4\times5` Matrix Formalism Including Thin Dipole Kicks
----------------------------------------------------------------------

The :math:`4\times5` matrix formalism

.. math::

   {\bf x}^f=M{\bf x}^i

can be extended to include dipole kicks

.. math::

   {\bf x}^f=\left(\begin{array}{c}0\\-b_1L\\0\\a_1L\\0\end{array}\right)+M{\bf x}^i

by superposition. The column vector describing the dipole kick can therefore be implemented by adding this as a 6th column and a 6th row with :math:`(0,0,0,0,0,1)`
to the matrix
The normal rule for matrix multiplication is then applied and it is possible to concatenate all linear elements, including dipole kicks and mis-alignments.

The Combined Function Sector Bend
---------------------------------

In the focusing plane

.. math::

   \left(\begin{array}{ccc}\cos\phi&\frac{1}{\sqrt{|K|}}\sin\phi&\frac{h_B}{|K|}(1-\cos\phi)\\
                          -\sqrt{|K|}\sin\phi&\cos\phi&\frac{h_B}{|K|}\sin\phi\\0&0&1\end{array}\right)


and the defocusing plane

.. math::

   \left(\begin{array}{ccc}\cosh\phi&\frac{1}{\sqrt{|K|}}\sinh\phi&\frac{h_B}{|K|}(\cosh\phi-1)\\
                          -\sqrt{|K|}\sinh\phi&\cosh\phi&\frac{h_B}{|K|}\sinh\phi\\0&0&1\end{array}\right)

where

.. math::

   \phi\equiv L\sqrt{|K|},\;K\equiv\left\{\begin{array}{ll}b_2+h_B^2\,;&\rm horizontal plane\\b_2,&\rm vertical plane\end{array}\right. 


Edge Focusing
-------------

Leading order edge focusing is described by

.. math::

   \left(\begin{array}{ccccc}     1&         0&         0&             0&     0 \\
                              h_B\tan(\psi)& 1&         0&             0&     0 \\
                                  0&         0& -h_B\tan(\psi-\psi_c)&  0&     0 \\
                                  0&         0&         0&             1&     0 \\
                                  0&         0&         0&             0&     1 \end{array}\right)

where :math:`\psi` is the edge angle and :math:`\psi_c` the leading order correction for a finite magnet gap, given by

.. math::

   \psi_c=K_1h_Bg\frac{1+\sin^2\psi}{\cos\psi}(1-K_1K_2h_Bg\tan\psi)

where g is the total magnet gap, :math:`K_1=0.5` and :math:`K_2=0`. Note that this implementation does not give the correct momentum dependence.

The Undulator
--------------


The Thin Lens Approximation
----------------------------

Non-linear multipoles are modelled by thin kicks taking the limit

.. math::

   L\rightarrow0,\;KL=\rm const

where :math:`KL` is the integrated strength. 
The kick is obtained by integrating Hamilton's equations using delta functions for the multipoles and replacing the strength by integrated strength.
We find

.. math::

   \begin{array}{lll}
   p_x^f&=&p_x^i-L(\frac{q}{p_0}B_y-h_B\delta+h_B^2x^i),\\
   p_y^f&=&p_y^i+\frac{qL}{p_0}B_x,\\
   cT^f&=&cT^i+h_BLx^i
   \end{array}

assuming :math:`h_B` to be small, where L is the length of the element.
It is clear that this model is symplectic. The corresponding linear matrix is given by

.. math::

   \left.\left(\begin{array}{ccccc}     1&                                                0&                 0&            0&              0\\
                       -\frac{qL}{p_0}\frac{\partial B_y}{\partial x}-Lh_B^2&             1&     -\frac{qL}{p_0}\frac{\partial B_y}{\partial y}& 0& Lh_B\\
                                        0&                                                0&              1&                  0&           0\\
                       \frac{qL}{p_0}\frac{\partial B_x}{\partial x}&     0&       \frac{qL}{p_0}\frac{\partial B_x}{\partial y}&    1&    0\\
                                        0&                                0&              0&                  0&           1\end{array}\right)\right|_{{\bf x}={\bf x}_{ref}}

where the field derivatives are computed from the multipole expansion.

The Cavity Model
----------------

If we neglect radial fields in the cavity, it can be represented by a thin longitudinal kick

.. math::

   \delta^f=\delta^i-\frac{q\hat V_RF}{E_0}\sin(\frac{2\pi f_{RF}}{c}cT)

where :math:`E_0` is the beam energy, :math:`\hat V_{RF}` the cavity voltage and :math:`f_{RF}` the RF frequency. 
Note that :math:`cT` is the deviation of pathlength relative to a reference particle.
To obtain absolute pathlength, the length of each magnet is added to the relative pathlength :math:`cT` for each element and, at the cavity, we subtract

.. math::

   cT^f=cT^i-\frac{hc}{f_{RF}}

where :math:`h` is the harmonic number, to avoid numerical overflow for :math:`cT`.

The Symplectic Integrator
--------------------------

It is possible to extend the :math:`4\times5` matrix formalism to the :math:`6\times6` case, as well as include higher order effects,
by using a (non-symplectic), e.g. second order matrix formalism [Brown].
However, this leads to a rather cumbersome formulation.
The elegant way, which also has advantage of being exact in the transverse coordinates, is to use a sympectic integrator [].
The importance of symplectic tracking for the study long term stability is obvious.

The Hamiltonian is separated into twoo exact solvable parts

.. math::

   H_1=H_4+H_5

where, neglecting fringe fields,

.. math::

   H_4=-(1+h_{ref}x)\sqrt{(1+\delta)^2-p_x^2-p_y^2}+\delta,\;H_5=-(1+h_{ref}x)\frac{q}{p_0}A_s

For efficiency, we will use the expanded Hamiltonian

.. math::

   H_4=\frac{p_x^2+p_y^2}{2(1+\delta)}+O(3),\;H_5=-\frac{q}{p_0}A_s+\frac{1}{2}(h_Bx)^2-h_Bx\delta+O(3)

The map generated by :math:`H1` is approximated by a symplectic integrator. A second order integrator is given by [Ruth, Forest]

.. math::

   \exp(:-LH_1:)=\exp(:-\frac{L}{2}H_4:)\exp(:-LH_5:)exp(:-\frac{L}{2}H_4:)+O(L^3)

Since :math:`H_4` is the Hamiltonian for a drift and :math:`H_5` corresponds to a thin kick, see Fig. 2.

Given a symmetric integrator of order :math:`2n`, :math:`S_{2n}(L)`, a :math:`(2n+2)` th order integrator is obtained by [Yoshida]

.. math::

   S_{2n+2}(L)=S_{2n}(z_1L)s_{2n}(z_0L)s_{2n}(z_1L)+O(L^{2n+3})

where

.. math::

   z_0=-\frac{2^{1/(2n+1)}}{2-2^{1/(2n+1)}},\;z_1=\frac{1}{2-2^{1/(2n+1)}}

In particular, a 4th order integrator is therefore given by

.. math::

   \begin{array}{ll}
   \exp(:-LH_1:)=\exp(:-c1LH_4:)&\exp(:-d_1LH_5:)\exp(:-c_2LH_4:)\exp(:-d_2LH_5:)\\
             &+\exp(:c_2LH_4:)\exp(:-d_1LH_5:)\exp(:-c_1LH_4:)+O(L^5)
   \end{array}

where

.. math::

   \begin{array}{lll}
   c_1=\frac{1}{2(2-2^{1/3})},\;
   &c_2=\frac{1-2^{1/3}}{2(2-2^{1/3})}\\
   d_1=\frac{1}{2(2-2^{1/3})},\;
   &d_2=-\frac{2^{1/3}}{2-2^{1/3}}
   \end{array}

see Fig. 3

Magnet Errors
--------------

Implementation of torsions....

Mis-alignments are implemented by applying a Euclidian transformation at the entrance and exit of each magnet [Forest].
We first transform to the magnet's local coordinate system

.. math::

   {\rm prot}(\frac{\phi}{2})\circ R(\theta_{des})

where :math:`R(\theta)` is a rotation in 2 dimensions

.. math::

   \begin{array}{lllll}
   x&  \leftarrow  & x\cos(\theta)&+&y\sin(\theta), \\
   p_x&\leftarrow  & p_x\cos(\theta)&+&p_y\sin(\theta),\\
   y  &\leftarrow  & -x\sin(\theta)&+&y\cos(\theta), \\
   p_y&\leftarrow  & -p_x\sin(\theta)&+&p_y\cos(\theta)
   \end{array}

with the design roll :math:`\theta_des` (e.g. a vertical bend is obtained by rotating a horizontal bend by :math:`90^\circ` ) and prot defined by

.. math::

   \begin{array}{llllll}
   p_s&\leftarrow&\sqrt{(1+\delta)^2-p_x^2-p_y^2}, &&& \\
   x  &\leftarrow&\frac{xp_s}{p_s\cos(\phi/2)-p_x\sin(\phi/2)},\;&p_x&\leftarrow& p_s\sin(\frac{\phi}{2})+p_x\cos(\frac{\phi}{2}), \\
   y  &\leftarrow& y+\frac{xp_y\sin(\phi/2)}{p_s\cos(\phi/2)-p_x\sin(\phi/2)},\;&p_y&\leftarrow& p_y, \\
   t  &\leftarrow& t+\frac{x(1/\beta +\delta)\sin(\phi/2)}{p_s\cos(\phi/2)-p_x\sin(\phi/2)},\;&p_t&\leftarrow& p_t 
   \end{array}

where :math:`\phi` is the bend angle. If we expand and only keep linear terms in the transverse coordinates as well as :math:`\phi`, we find

.. math::

   \begin{array}{lll}
   x&\leftarrow x+O(2),\;&p_x\leftarrow p_x+\sin(\frac{\phi}{2}+O(2),\nonumber \\
   y&\leftarrow y+O(2),\;&p_y\leftarrow p_y, \nonumber \\
   t&\leftarrow t+O(2),\;&p_t\leftarrow p_t
   \end{array}

The Euclidian transformation consists of translation :math:`T`

.. math::

   {\bf x}\leftarrow T({\bf x})={\bf x}-\Delta{\bf x}

followed by a rotation :math:`R` with the total roll angle :math:`\theta`. The total misalignment has the following contributions

.. math::

   \Delta{\bf x}=\Delta{\bf x}_{sys}+\Delta{\bf x}_{rms} r

where :math:`r` is a random number and similarly, the total roll angle

.. math::

   \theta=\theta_{des}+\Delta\theta_{sys}+\Delta\theta_{rms}r

where :math:`\theta` is a design tilt. Since we are now in the magnet's reference system we only have to apply prot:math:`(-\phi/2)` to transform back.

The multipole components have the following contributions

.. math::

   \begin{array}{lll}
   a_n&=&a_{n\,des}+a_{n\,sys}+a_{n\,rms}r \nonumber \\
   b_n&=&b_{n\,des}+b_{n\,sys}+b_{n\,rms}r
   \end{array}

where :math:`a_{n\,des}` and :math:`b_{n\,des}` are the design multipole strengths.


The Euclidian Transormation
-----------------------------

At the entrance of a given magnet we apply Euclidian transformation

.. math::

   {\rm prot}^{-1}\circ R(\theta)\circ T(\Delta{\bf x})\circ R^{-1}(\theta_{des})\circ {\rm prot}(\frac{\phi}{2})\circ R(\theta_{des})

The transformation

.. math::

   R^{-1}(\theta_{des})\circ{\rm prot}(\frac{\phi}{2})\circ R(\theta_{des})

is given by

.. math::

   \begin{array}{llllll}
   x&\leftarrow& x+O(2),\;&p_x&\leftarrow& p_x+\sin(\frac{\phi}{2})\cos(\theta_{des})+O(2), \\
   y&\leftarrow& y+O(2),\;&p_y&\leftarrow& p_y+\sin(\frac{\phi}{2})\sin(\theta_{des})+O(2), \\
   t&\leftarrow& t+O(2),\;&p_t&\leftarrow& p_t \end{array}

We then translate

.. math::

   \begin{array}{lll}
   x&\leftarrow&x-\delta x,\\
   y&\leftarrow&y-\delta y\end{array}

rotate

.. math::

   \begin{array}{lllll}
   x&\leftarrow&x\cos(\theta)&+&y\sin(\theta),\\
   p_x&\leftarrow&p_x\cos(\theta)&+&p_y\sin(\theta),\\
   y&\leftarrow&-x\sin(\theta)&+&y\cos(\theta),\\
   p_x&\leftarrow&-p_x\sin(\theta)&+&p_y\cos(\theta)
   \end{array}

and finally apply

.. math::

   {\rm prot}^{-1}(\frac{\phi}{2})\circ R(\theta)

or

.. math::

   \begin{array}{llllll}
   x&\leftarrow& x+O(2),\;&p_x&\leftarrow& p_x-\sin(\frac{\phi}{2})+O(2), \\
   y&\leftarrow& y+O(2),\;&p_y&\leftarrow& p_y+O(2), \\
   t&\leftarrow& t+O(2),\;&p_t&\leftarrow& p_t
   \end{array}

We now integrate through the magnet.
Similarly, at the exit, we apply

.. math::

   R^{-1}(\theta_{des})/,{\rm prot}(\frac{\phi}{2})/,R(\theta_{des})/,T^{-1}(\Delta{\bf x})/,R^{-1}(\theta)/,{\rm port}^{-1}(\frac{\phi}{2})

The corresponding matrix is

.. math::

   \left(\begin{array}{ccccc}\cos(\theta)& 0& \sin(\theta)& 0& 0\\
                             0& \cos(\theta)& 0& \sin(\theta)& 0\\
                             -\sin(\theta)& 0& \cos(\theta)& 0& 0\\
                             0& -\sin(\theta)& 0& \cos(\theta)& 0\\
                             0& 0& 0& 0& 1
   \end{array}\right)

since only the rotation contributes.

Note that although the :math:`4\times5` matrix formalism can be applied in the case of magnet errors this treatment is inconsistent,
since the matrices are obtained by expanding around the refernce trajectory.
In other words, only feed-down due to linear terms are included for elements represented by matrices.
This model should, therfore, at most, be applied for linear lattice design with no magnet errors.
The use of a symplectic integrator and automatic differentiation (AD) allows for the implementation of a consistent model,
since AD allows us to compute non-linear maps around any reference curve and in particular, linear maps around the perturbed closed orbit.

The Closed Orbit Finder
------------------------

For the :math:`4\times5` matrix formalism the linear on-turn map is computed by concatenating the linear transfer matrices.

In the case of the symplectic integrator, all the calculations are performed using a package for truncated power series algebra to find the
Taylor series expansion of the non-linear map :math:`M` to arbitrary order.
Given the purpose of this code as well as for efficiency, we have linked to routines for linear power series computing the linear map :math:`M`.
It is straightforward (more compact, efficient etc.) to write an independent code that computes and analysis higher order maps by reading a machine file describing the lattice
generated by this code.

The linear map :math:`M` is calculated for a given reference trajectory.
In the circular case the closed orbit is normally used.
The closed orbit is different from the design orbit when misalignment and tilt errors are added for the magnets.
In this case the closed orbit has to be found numerically.

For the one-turn map, we have

.. math::

   {\bf x}_f=M{\bf x}_i

The closed orbit at the starting point of the lattice is given by the fixed point

.. math::

   M{\bf x}_{cod}={\bf x}_{cod}

or

.. math::

   (M-I){\bf x}_{cod}=0

The fixed point is found numerically with Newton-Raphson's method[]

.. math::

   f'({\bf x}_k)({\bf x}_{k+1}-{\bf x}_k)+f({\bf x}_k)=0

where :math:`f'({\bf x}_k)` the Jacobian. It follows

.. math::

   f({\bf x}_i^k)=(M-I){\bf x}_i^k={\bf x}_f^k-{\bf x}_i^k,\;f'({\bf x}_i^k)=M-I

so that

.. math::

   {\bf x}_i^{k+1}={\bf x}_i^k-(M-1)^{-1}({\bf x}_f^k-{\bf x}_i^k)

Note that the linear one-turn map :math:`M` has to be calculated for each iteration.
The closed orbit at other points in the lattice are computed by tracking.

Linear Lattice Calculations
-----------------------------

The linear equations of motion are obtained by expanding the Hamiltonian to the second order and assuming mid-plane symmetry

.. math::

   H_3=\frac{p_x^2+p_y^2}{2(1+\delta)}+\frac{1}{2}[b_2(s)+h_B^2(s)]x^2-\frac{1}{2}b_2(s)y^2-h_B{s}x\delta+O(3)

with the solution

.. math::

   \begin{array}{lll}
   x&=&\sqrt{2J_x\beta_x(s)}\cos(\mu_x(s)+\varphi_x), \\
   p_x&=&-\sqrt{\frac{2J_x}{\beta_x(s)}}[\sin(\mu_x(s)+\varphi_x)+\alpha_x(s)\cos(\mu_x(s)+\varphi_x)]
   \end{array}

where

.. math::

   \alpha_x\equiv-\frac{1}{2}\beta'_x(s)

The linear one-turn map :math:`M` can in the :math:`2\times2` case be written

.. math::

   M=\left(\begin{array}{cc}\cos\mu+\alpha\sin\mu&\beta\sin\mu\\-\gamma\sin\mu&\cos\mu-\alpha\sin\mu\end{array}\right)

where the phase advance :math:`\mu(s)` is given by

.. math::

   \mu(s)\equiv\int_{s_0}^s\frac{d\tau}{\beta(\tau)}

and

.. math::

   \gamma\equiv\frac{1}{\beta}(1+\alpha^2)

We apply the following canonical transformation :math:`A` so that

.. math::

   A^{-1}MA=R(\mu)=\left(\begin{array}{cc}\cos\mu&\sin\mu\\-\sin\mu&\cos\mu\end{array}\right)

where :math:`R(\mu)` is the 2-dimensional rotation matrix. We find

.. math::

   A=\left(\begin{array}{cc}\frac{1}{\sqrt{\gamma}}&-\frac{\alpha}{\sqrt{\gamma}}\\0&\sqrt{\gamma}\end{array}\right)

If one imposes the normal definition of phase advance, the corresponding :math:`A_{C\&S}` is obtained from :math:`A` by rotating with and angle of :math:`\arctan(\alpha)`

.. math::

   A_{C\&S}=\left(\begin{array}{cc}\frac{1}{\sqrt{\gamma}}&-\frac{\alpha}{\sqrt{\gamma}}\\0&\sqrt{\gamma}\end{array}\right)
           \left(\begin{array}{cc}\frac{1}{\sqrt{1+\alpha^2}}&\frac{\alpha}{\sqrt{1+\alpha^2}}\\-\frac{\alpha}{\sqrt{1+\alpha^2}}&\frac{1}{\sqrt{1+\alpha^2}}\end{array}\right)
          =\left(\begin{array}{cc}\sqrt{\beta}&0\\-\frac{\alpha}{\sqrt{\beta}}&\frac{1}{\sqrt{\beta}}\end{array}\right)

The one-turn matrix has the form

.. math::

   M=\left(\begin{array}{cccccc}&&&&0&n_{16}\\&N&&&0&n_{26}\\&&&&0&n_{36}\\&&&&0&n_{46}\\n_{51}&n_{52}&n_{53}&n_{54}&1&n_{56}\\0&0&0&0&0&1\end{array}\right)





It follows that the :math:`\delta`-dependent fixed point is given by

.. math::

   \Delta{\bf x}_{cod}={\bf \eta}\delta=N{\bf \eta}\delta+{\bf n}\delta

so that

.. math::

   {\bf \eta}=(I-N)^{-1}{\bf n}

where :math:`{\bf \eta}=(\eta_x,\eta'_x,\eta_y,\eta'_y)` is the linear dispersion and :math:`{\bf n}=(n_{16},n_{26},n_{36},n_{46})`.
The translation to this point in phase space can be done by the translation operator

.. math::

   T=e^{:{\bf\Delta x}\cdot{\bf x}:}

where

.. math::

   :{\bf\Delta x}\cdot{\bf x}:=\sum_{ij}\Delta x_iJ_{ij}x_j

and :math:`J_{ij}` is the symplectic form

.. math::

   {\bf J}=\left(\begin{array}{cc}0&{\bf 1}\\{\bf -1}&0\end{array}\right)

Applying the corresponding canonical transformation :math:`B`

.. math::

   B=\left(\begin{array}{cccccc}1&0&0&0&0&\eta_x\\0&1&0&0&0&\eta'_x\\0&0&1&0&0&\eta_y\\0&0&0&1&0&\eta'_y\\-\eta'_x&\eta_x&-\eta'_y&\eta_y&1&0\\0&0&0&0&0&1\end{array}\right)

and :math:`A` as before we find

.. math::

   A^{-1}B^{-1}MBA=\left(\begin{array}{cccccc}\cos\mu_x&\sin\mu_x& 0& 0& 0& 0\\ -\sin\mu_x&\cos\mu_x& 0& 0& 0 &0\\
                                              0& 0& \cos\mu_y&\sin\mu_y& 0& 0\\ 0& 0& -\sin\mu_x&\cos\mu_x& 0 &0\\
                                              0& 0& 0& 0& 1& C\alpha_c\\ 0& 0& 0& 0& 0& 1 \end{array}\right)

where :math:`\alpha_c` is the momentum compaction

.. math::

   \alpha_c\equiv\frac{1}{C}\frac{d(cT)}{d\delta}

and :math:`C` the circumference. The longitudinal chromaticity :math:`\eta_\delta` is defined by

.. math::

   \eta_\delta\equiv\frac{1}{\omega}\frac{d\omega}{d\delta}=\frac{1}{\gamma^2_t}-\alpha_c=\frac{E_0^2-\alpha_cE^2}{E^2}

and we have for the linearized equation of motion

.. math::

   \delta^f=\delta^i+\frac{q\hat V}{E_0}\sin(\frac{\omega_{RF}}{c}[cT_0+cT+T_i+C\alpha_c\delta+{\bf n}^T\cdot{\bf x}])

For reference purposes we present the corresponding equation of motion using angle variables

.. math::

   \ddot\phi+\frac{\Omega^2}{\cos\phi_s}(\sin\phi-\sin\phi_s)=0

where

.. math::

   \Omega=\sqrt{\frac{\omega_{RF}\alpha_c\cos\phi_s}{T_0}\frac{q\hat V_{RF}}{E_0}}\;\;{\rm and}\;\;\phi=\frac{\omega_{RF}}{C}{cT},\:\dot\phi=\omega_{RF}\alpha_c\delta

Calculation of Tune for a General :math:`4\times4` Symplectic Matrix
---------------------------------------------------------------------

THe characteristic polynomial :math:`P(\lambda)` of an arbitrary symplectic matrix is given by [Forest]

.. math::

   P(\lambda)=\det(M-\lambda I)=(\lambda-\lambda_0)(\lambda-\frac{1}{\lambda_0})(\lambda-\lambda_1)(\lambda-\frac{1}{\lambda_1})

It follows that

.. math::

   P(1)=(2-x)(2-y),\;P(-1)=(2+x)(2+y)

where

.. math::

   x=\lambda_0+\frac{1}{\lambda_0}=2\cos(2\pi\nu_x)

and similarly for y. Eliminating y,

.. math::

  x^2+4bx+4c=0

where

.. math::

   b=\frac{P(1)-P(-1)}{16},\;c=\frac{P(1)+P(-1)}{8}-1

Solving for x

.. math::

   x=-2(b\pm\sqrt{b^2-c}),

so that

.. math::

   \nu_{x,y}=\frac{1}{2\pi}\cos^{-1}(\frac{x}{2})

The right quadrant :math:`(0\rightarrow2\pi)` is determined from inspection of the map :math:`M`.

Chromatic effects using the matrix formalism are calculated by numerical differentiaion.
In particular, the closed orbit is calculated for the on - as well as the off - momentum together with the one-turn map.

Synchrtron Radiation
---------------------

The classical radiation from an relativistic electron is given by [Sands p.98]

.. math::

   \frac{dE}{d(ct)}=\frac{q^2c^2C_\gamma}{2\pi}E^2({\bf B}_\bot)^2

where

.. math::

   C_\gamma=\frac{4\pi}{3}\frac{r_e}{(m_ec^2)^3}=8.846269\times10^{-5}\,{\rm m}\,{\rm GeV}^{-3}

Since

.. math::

   \frac{dE}{d(ct)}=-p_0\frac{dp_t}{dt}

It follows

.. math::

   \frac{dp_t}{d(ct)}=-\frac{cC_\gamma}{2\pi}p_0E_0^2(1-\frac{p_0c}{E_0}pt)^2\big(\frac{{\bf B}_\bot}{B\rho}\big)^2

If we take the ultra-relativistic limit

.. math::

   p_t\rightarrow-\delta,\;p_0c\rightarrow E_0\qquad{\rm when}\qquad\beta\rightarrow1

we find

.. math::

   \frac{d\delta}{d(ct)}=-\frac{C_\gamma E_0^3}{2\pi}(1+\delta)^2\big(\frac{{\bf B}_\bot}{B\rho}\big)^2,\quad\rightarrow1

The transverse field is computed from

.. math::

   {\bf B}_\bot={\bf B}\times{\bf\hat e}_s

.. math::

   r'\equiv\frac{dr}{ds}=\sqrt{(1+h_B)^2+x'^2+y'^2}

.. math::

   \hat e_x=\frac{x'}{|r'|},\;\hat e_y=\frac{y'}{|r'|},\;\hat e_s=\frac{r'}{|r'|}

Since :math:`x'` and :math:`y'` are conserved [Sands p.104], it follows from Hamilton's equations

.. math::

   \begin{array}{lllll}x'&=&\frac{\partial H}{\partial p_x}&=&\frac{p_x}{1+\delta}+O(2),\\
                       y'&=&\frac{\partial H}{\partial p_y}&=&\frac{p_y}{1+\delta}+O(2)\end{array}

that

.. math::

   \begin{array}{lll}
   p_x^f&=&\frac{1+\delta^f}{1+\delta^i}p_x^i,\\
   p_y^f&=&\frac{1+\delta^f}{1+\delta^i}p_y^i
   \end{array}

Quantum Fluctuation
-------------------




Closed Orbit Correction
-----------------------

The Local Bump Method
^^^^^^^^^^^^^^^^^^^^^^

Closed orbit correction with local bump method
Local bump implies

..
   fig

.. math::

   \begin{array}{lll}
   \theta_{x1}&=&{\rm free parameter},\\
   \theta_{x2}&=&-\sqrt{\frac{\beta_{x1}}{\beta_{x2}}}\frac{ \sin(\mu_{x3}-\mu_{x1}) }{ \sin(\mu_{x3}-\mu_{x2}) }\theta_{x1},\\
   \theta_{x3}&=&-\sqrt{\frac{\beta_{x1}}{\beta_{x3}}}\frac{\sin(\mu_{x2}-\mu_{x1})}{\sin(\mu_{x3}-\mu_{x2})}\theta_{x1}
   \end{array}

Least-square minimization of the rms orbit

.. math::

   x_{rms}^2=\sum_i\theta{x1}[x_i+\sqrt{\beta_{x1}\beta_{xi}(s)}\sin(\mu_{xi}-\mu_{x1})]^2

gives

.. math::

   \theta_{x1}=-\frac{ \sum_ix_i\sqrt{\beta_{x1}\beta_{xi}(s)}\sin(\mu_{xi}-\mu_{x1})}{\sum_i[\sqrt{\beta_{x1}\beta_{xi}(s)}\sin(\mu_{xi}-\mu_{x1})]^2}

In the linear approximation the new orbit is given by

.. math::

   x(s)=\left\{\begin{array}{ll}-\sqrt{\beta_{x1}\beta_x(s)}\sin(\mu_x-\mu_{x1})\theta_{x1},&s_1\leq s\leq s_2\\
   -\sqrt{\beta_{x1}\beta_x(s)}\sin(\mu_x-\mu_{x1})\theta_{x1}+\sqrt{\beta_{x2}\beta_x(s)}\sin(\mu_x-\mu_{x2})\theta_{x2},\:&s_2\leq s\leq s_3\end{array}\right.

Limited corrector strength is implemented by successively scaling :math:`\theta_1`, :math:`\theta_2` and :math:`\theta_3` until reaching values that are within limits.

Singular Value Decomposition
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The correlation matrix is given by

.. math::

   C_{ij}=\frac{\sqrt{\beta_i\beta_j}}{2\sin(\pi\nu)}\cos(\pi\nu-|\mu_i-\mu_j|)+\eta_i\eta_j\delta

where the last term only contributes in the case of a cavity. We attempt to solve the following equation

.. math::

   C{\bf \theta}_x+{\bf x}=0



References
------------

\E. Forest

\H. Nishimura

\M. Sands



