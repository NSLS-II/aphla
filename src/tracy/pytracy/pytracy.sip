%Module pytracy 0

%ModuleHeaderCode
#define ORDER 1
#include <../tracy-3.5/tracy/inc/tracy_lib.h>
%End

int ss_dim;

struct globvalrec {
    double        dPcommon;       // dp for numerical differentiation 
    double        dPparticle;     // energy deviation 
    double        delta_RF;       // RF acceptance 
    SIP_PYOBJECT  TotalTune;      // Vector2, transverse tunes 
%GetCode
sipPy = PyList_New(2);
for (int index = 0; index < 2; index++)
    PyList_SetItem(sipPy, index, PyFloat_FromDouble((double)sipCpp->TotalTune[index]));
%End
%SetCode
for (int index = 0; index < 2; index++)
  sipCpp->TotalTune[index] = (double) PyFloat_AsDouble((PyObject*) PyList_GetItem(sipPy,index));
%End
    double        Omega;
    double        U0;             // energy lost per turn in keV 
    double        Alphac;         // alphap 
    SIP_PYOBJECT  Chrom;          // Vector2, chromaticities 
%GetCode
sipPy = PyList_New(2);
for (int index = 0; index < 2; index++)
    PyList_SetItem(sipPy, index, PyFloat_FromDouble((double)sipCpp->Chrom[index]));
%End
%SetCode
for (int index = 0; index < 2; index++)
  sipCpp->Chrom[index] = (double) PyFloat_AsDouble((PyObject*) PyList_GetItem(sipPy,index));
%End
    double        Energy;         // ring energy 
    long          Cell_nLoc;      // number of elements 
    long          Elem_nFam;      // number of families 
    long          CODimax;        /* maximum number of cod search before failing */
    double        CODeps;         // precision for closed orbit finder
//    Vector        CODvect;        // closed orbit
    SIP_PYOBJECT  CODvect;        // Vector, closed orbit
%GetCode
sipPy = PyList_New(ss_dim);
for (int index=0;index<ss_dim;index++)
  PyList_SetItem(sipPy, index, PyFloat_FromDouble((double) sipCpp->CODvect[index]));
%End
%SetCode
for (int index = 0; index < ss_dim; index++)
  sipCpp->CODvect[index] = (double) PyFloat_AsDouble((PyObject*) PyList_GetItem(sipPy,index));
%End
    int           bpm;            // bpm number 
    int           hcorr;          // horizontal corrector number 
    int           vcorr;          // vertical corrector number 
    int           qt;             // vertical corrector number 
    int           gs;             // girder start marker 
    int           ge;             // girder end marker 
    SIP_PYOBJECT  OneTurnMat;     // Matrix, oneturn matrix 
%GetCode
sipPy=PyList_New(ss_dim);
for (int i=0; i<ss_dim; ++i)
{
    PyObject * row = PyList_New(ss_dim);
    for (int j=0; j<ss_dim; ++j)
      PyList_SetItem(row, j, PyFloat_FromDouble(sipCpp->OneTurnMat[i][j]));
    PyList_SetItem(sipPy,i,row);
}
%End
%SetCode
for (int i=0; i<ss_dim; ++i)
{
  PyObject * pyRow = (PyObject *) PyList_GetItem(sipPy,i);
  for (int j=0; j<ss_dim; ++j)
    sipCpp->OneTurnMat[i][j] = (double) PyFloat_AsDouble((PyObject*) PyList_GetItem(pyRow,j));
}
%End
//  SIP_PYOBJECT  Ascr;           //Matrix
//  SIP_PYOBJECT  Ascrinv;        //Matrix
//  SIP_PYOBJECT  Vr;             //Matrix, real part of the eigenvectors 
//  SIP_PYOBJECT  Vi;             //Matrix, imaginal par of the eigenvectors 

    bool          MatMeth;        // matrix method 
    bool          Cavity_on;      // if true, cavity turned on 
    bool          radiation;      // if true, radiation turned on 
    bool          emittance;
    bool          quad_fringe;    /* dipole- and quadrupole hard-edge fringe fields. */
    bool          H_exact;        // "small ring" Hamiltonian. 
    bool          pathlength;     // absolute path length
    bool          stable;
    bool          Aperture_on;
    bool          EPU;
    bool          wake_on;

    double        dE;             // energy loss
    SIP_PYOBJECT  alpha_rad; // double[DOF] damping coeffs.
%GetCode
sipPy = PyList_New(DOF);
for (int index = 0; index < DOF; index++)
    PyList_SetItem(sipPy, index, PyFloat_FromDouble((double)sipCpp->alpha_rad[index]));
%End
%SetCode
for (int index = 0; index < DOF; index++)
  sipCpp->alpha_rad[index] = (double) PyFloat_AsDouble((PyObject*) PyList_GetItem(sipPy,index));
%End    
    SIP_PYOBJECT  D_rad;           // double[DOF] diffusion coeffs (Floquet space)
%GetCode
sipPy = PyList_New(DOF);
for (int index = 0; index < DOF; index++)
    PyList_SetItem(sipPy, index, PyFloat_FromDouble((double)sipCpp->D_rad[index]));
%End
%SetCode
for (int index = 0; index < DOF; index++)
  sipCpp->D_rad[index] = (double) PyFloat_AsDouble((PyObject*) PyList_GetItem(sipPy,index));
%End        
    SIP_PYOBJECT  J;         // partition numbers
%GetCode
sipPy = PyList_New(DOF);
for (int index = 0; index < DOF; index++)
    PyList_SetItem(sipPy, index, PyFloat_FromDouble((double)sipCpp->J[index]));
%End
%SetCode
for (int index = 0; index < DOF; index++)
  sipCpp->J[index] = (double) PyFloat_AsDouble((PyObject*) PyList_GetItem(sipPy,index));
%End
    SIP_PYOBJECT       tau;       // double[DOF] damping times
%GetCode
sipPy = PyList_New(DOF);
for (int index = 0; index < DOF; index++)
    PyList_SetItem(sipPy, index, PyFloat_FromDouble((double)sipCpp->tau[index]));
%End
%SetCode
for (int index = 0; index < DOF; index++)
  sipCpp->tau[index] = (double) PyFloat_AsDouble((PyObject*) PyList_GetItem(sipPy,index));
%End
    bool          IBS;            // intrabeam scattering
    double        Qb;             // bunch charge
    SIP_PYOBJECT  D_IBS;     // double[DOF] diffusion matrix (Floquet space)
%GetCode
sipPy = PyList_New(DOF);
for (int index = 0; index < DOF; index++)
    PyList_SetItem(sipPy, index, PyFloat_FromDouble((double)sipCpp->D_IBS[index]));
%End
%SetCode
for (int index = 0; index < DOF; index++)
  sipCpp->D_IBS[index] = (double) PyFloat_AsDouble((PyObject*) PyList_GetItem(sipPy,index));
%End
    SIP_PYOBJECT wr;         //Vector
%GetCode
sipPy = PyList_New(ss_dim);
for (int index=0;index<ss_dim;index++)
  PyList_SetItem(sipPy, index, PyFloat_FromDouble((double) sipCpp->wr[index]));
%End
%SetCode
for (int index = 0; index < ss_dim; index++)
  sipCpp->wr[index] = (double) PyFloat_AsDouble((PyObject*) PyList_GetItem(sipPy,index));
%End
    SIP_PYOBJECT  wi;         // Vector real and imaginary part of eigenvalues
%GetCode
sipPy = PyList_New(ss_dim);
for (int index=0;index<ss_dim;index++)
  PyList_SetItem(sipPy, index, PyFloat_FromDouble((double) sipCpp->wi[index]));
%End
%SetCode
for (int index = 0; index < ss_dim; index++)
  sipCpp->wi[index] = (double) PyFloat_AsDouble((PyObject*) PyList_GetItem(sipPy,index));
%End
    SIP_PYOBJECT eps;            //Vector3 3 motion invariants
%GetCode
sipPy = PyList_New(3);
for (int index = 0; index < 3; index++)
    PyList_SetItem(sipPy, index, PyFloat_FromDouble((double)sipCpp->eps[index]));
%End
%SetCode
for (int index = 0; index < 3; index++)
  sipCpp->eps[index] = (double) PyFloat_AsDouble((PyObject*) PyList_GetItem(sipPy,index));
%End
    SIP_PYOBJECT epsp;           //Vector3 transverse and longitudinal projected emittances
%GetCode
sipPy = PyList_New(3);
for (int index = 0; index < 3; index++)
    PyList_SetItem(sipPy, index, PyFloat_FromDouble((double)sipCpp->epsp[index]));
%End
%SetCode
for (int index = 0; index < 3; index++)
  sipCpp->epsp[index] = (double) PyFloat_AsDouble((PyObject*) PyList_GetItem(sipPy,index));
%End
    int           RingType;       // 1 if a ring (0 if transfer line)
};


globvalrec globval;

void Read_Lattice(char * infile);

void Ring_GetTwiss(bool, double);

SIP_PYLIST getS();
%MethodCode

        PyObject * s;
        double pl=0;

        if (s = PyList_New(globval.Cell_nLoc))
        {
          Py_BEGIN_ALLOW_THREADS
          for (int i=0 ; i<globval.Cell_nLoc ;i++)
          {
            pl += Cell[i].Elem.PL;
            PyList_SetItem(s,i,PyFloat_FromDouble(pl));
          }
          Py_END_ALLOW_THREADS
          return s;
        }
        else
        {
            // PyList_New() will have raised the exception.
            sipIsErr = 1;
            return NULL;
        }
%End

SIP_PYLIST getBetaX();
%MethodCode
 
        PyObject * bx;
      
        if (bx = PyList_New(globval.Cell_nLoc))
        {
          Py_BEGIN_ALLOW_THREADS
          for (int i=0 ; i<globval.Cell_nLoc ;i++)
          {
            PyList_SetItem(bx,i,PyFloat_FromDouble(Cell[i].Beta[0]));
          }
          Py_END_ALLOW_THREADS
          return bx;
        }
        else
        {
            // PyList_New() will have raised the exception.
            sipIsErr = 1;
            return NULL;
        }
%End

SIP_PYLIST getBetaY();
%MethodCode
        // The C++ API takes a 2 element array of integers but passing a
        // two element tuple is more Pythonic.


        PyObject * by;

        if (by = PyList_New(globval.Cell_nLoc))
        {
          Py_BEGIN_ALLOW_THREADS
          for (int i=0 ; i<globval.Cell_nLoc ;i++)
          {
            PyList_SetItem(by,i,PyFloat_FromDouble(Cell[i].Beta[1]));
          }
          Py_END_ALLOW_THREADS
          return by;
        }
        else
        {
            // PyList_New() will have raised the exception.
            sipIsErr = 1;
            return NULL;
        }
%End

SIP_PYLIST getAlphaX();
%MethodCode

        PyObject * ax;

        if (ax = PyList_New(globval.Cell_nLoc))
        {
          Py_BEGIN_ALLOW_THREADS
          for (int i=0 ; i<globval.Cell_nLoc ;i++)
          {
            PyList_SetItem(ax,i,PyFloat_FromDouble(Cell[i].Alpha[0]));
          }
          Py_END_ALLOW_THREADS
          return ax;
        }
        else
        {
            // PyList_New() will have raised the exception.
            sipIsErr = 1;
            return NULL;
        }
%End

SIP_PYLIST getAlphaY();
%MethodCode

        PyObject * ay;

        if (ay = PyList_New(globval.Cell_nLoc))
        {
          Py_BEGIN_ALLOW_THREADS
          for (int i=0 ; i<globval.Cell_nLoc ;i++)
          {
            PyList_SetItem(ay,i,PyFloat_FromDouble(Cell[i].Alpha[1]));
          }
          Py_END_ALLOW_THREADS
          return ay;
        }
        else
        {
            // PyList_New() will have raised the exception.
            sipIsErr = 1;
            return NULL;
        }
%End

SIP_PYLIST getEtaX();
%MethodCode

        PyObject * ex;

        if (ex = PyList_New(globval.Cell_nLoc))
        {
          Py_BEGIN_ALLOW_THREADS
          for (int i=0 ; i<globval.Cell_nLoc ;i++)
          {
            PyList_SetItem(ex,i,PyFloat_FromDouble(Cell[i].Eta[0]));
          }
          Py_END_ALLOW_THREADS
          return ex;
        }
        else
        {
            // PyList_New() will have raised the exception.
            sipIsErr = 1;
            return NULL;
        }
%End

SIP_PYLIST getEtaY();
%MethodCode

        PyObject * ex;

        if (ex = PyList_New(globval.Cell_nLoc))
        {
          Py_BEGIN_ALLOW_THREADS
          for (int i=0 ; i<globval.Cell_nLoc ;i++)
          {
            PyList_SetItem(ex,i,PyFloat_FromDouble(Cell[i].Eta[1]));
          }
          Py_END_ALLOW_THREADS
          return ex;
        }
        else
        {
            // PyList_New() will have raised the exception.
            sipIsErr = 1;
            return NULL;
        }
%End

SIP_PYLIST getEtaXp();
%MethodCode

        PyObject * exp;

        if (exp = PyList_New(globval.Cell_nLoc))
        {
          Py_BEGIN_ALLOW_THREADS
          for (int i=0 ; i<globval.Cell_nLoc ;i++)
          {
            PyList_SetItem(exp,i,PyFloat_FromDouble(Cell[i].Etap[0]));
          }
          Py_END_ALLOW_THREADS
          return exp;
        }
        else
        {
            // PyList_New() will have raised the exception.
            sipIsErr = 1;
            return NULL;
        }
%End

SIP_PYLIST getEtaYp();
%MethodCode
        // The C++ API takes a 2 element array of integers but passing a
        // two element tuple is more Pythonic.


        PyObject * eyp;

        if (eyp = PyList_New(globval.Cell_nLoc))
        {
          Py_BEGIN_ALLOW_THREADS
          for (int i=0 ; i<globval.Cell_nLoc ;i++)
          {
            PyList_SetItem(eyp,i,PyFloat_FromDouble(Cell[i].Etap[1]));
          }
          Py_END_ALLOW_THREADS
          return eyp;
        }
        else
        {
            // PyList_New() will have raised the exception.
            sipIsErr = 1;
            return NULL;
        }
%End

SIP_PYLIST getPhiX();
%MethodCode

        PyObject * px;

        if (px = PyList_New(globval.Cell_nLoc))
        {
          Py_BEGIN_ALLOW_THREADS
          for (int i=0 ; i<globval.Cell_nLoc ;i++)
          {
            PyList_SetItem(px,i,PyFloat_FromDouble(Cell[i].Nu[0]));
          }
          Py_END_ALLOW_THREADS
          return px;
        }
        else
        {
            // PyList_New() will have raised the exception.
            sipIsErr = 1;
            return NULL;
        }
%End

SIP_PYLIST getPhiY();
%MethodCode

        PyObject * py;

        if (py = PyList_New(globval.Cell_nLoc))
        {
          Py_BEGIN_ALLOW_THREADS
          for (int i=0 ; i<globval.Cell_nLoc ;i++)
          {
            PyList_SetItem(py,i,PyFloat_FromDouble(Cell[i].Nu[1]));
          }
          Py_END_ALLOW_THREADS
          return py;
        }
        else
        {
            // PyList_New() will have raised the exception.
            sipIsErr = 1;
            return NULL;
        }
%End

SIP_PYOBJECT getX();
%MethodCode

        PyObject * X;

        if (X = PyList_New(globval.Cell_nLoc))
        {
          Py_BEGIN_ALLOW_THREADS
          for (int i=0 ; i<globval.Cell_nLoc ;i++)
          {
            PyList_SetItem(X,i,PyFloat_FromDouble(Cell[i].BeamPos[0]));
          }
          Py_END_ALLOW_THREADS
          return X;
        }
        else
        {
            // PyList_New() will have raised the exception.
            sipIsErr = 1;
            return NULL;
        }
%End

SIP_PYOBJECT getXp();
%MethodCode
        
        PyObject * xp;

        if (xp = PyList_New(globval.Cell_nLoc))
        {
          Py_BEGIN_ALLOW_THREADS
          for (int i=0 ; i<globval.Cell_nLoc ;i++)
          {
            PyList_SetItem(xp,i,PyFloat_FromDouble(Cell[i].BeamPos[1]));
          }
          Py_END_ALLOW_THREADS
          return xp;
        }
        else
        {
            // PyList_New() will have raised the exception.
            sipIsErr = 1;
            return NULL;
        }
%End

SIP_PYOBJECT getY();
%MethodCode
        
        PyObject * Y;

        if (Y = PyList_New(globval.Cell_nLoc))
        {
          Py_BEGIN_ALLOW_THREADS
          for (int i=0 ; i<globval.Cell_nLoc ;i++)
          {
            PyList_SetItem(Y,i,PyFloat_FromDouble(Cell[i].BeamPos[2]));
          }
          Py_END_ALLOW_THREADS
          return Y;
        }
        else
        {
            // PyList_New() will have raised the exception.
            sipIsErr = 1;
            return NULL;
        }
%End

SIP_PYOBJECT getYp();
%MethodCode
        
        PyObject * yp;

        if (yp = PyList_New(globval.Cell_nLoc))
        {
          Py_BEGIN_ALLOW_THREADS
          for (int i=0 ; i<globval.Cell_nLoc ;i++)
          {
            PyList_SetItem(yp,i,PyFloat_FromDouble(Cell[i].BeamPos[3]));
          }
          Py_END_ALLOW_THREADS
          return yp;
        }
        else
        {
            // PyList_New() will have raised the exception.
            sipIsErr = 1;
            return NULL;
        }
%End

SIP_PYOBJECT getDp();
%MethodCode
        
        PyObject * dp;

        if (dp = PyList_New(globval.Cell_nLoc))
        {
          Py_BEGIN_ALLOW_THREADS
          for (int i=0 ; i<globval.Cell_nLoc ;i++)
          {
            PyList_SetItem(dp,i,PyFloat_FromDouble(Cell[i].BeamPos[4]));
          }
          Py_END_ALLOW_THREADS
          return dp;
        }
        else
        {
            // PyList_New() will have raised the exception.
            sipIsErr = 1;
            return NULL;
        }
%End

SIP_PYOBJECT getDt();
%MethodCode
        
        PyObject * dt;

        if (dt = PyList_New(globval.Cell_nLoc))
        {
          Py_BEGIN_ALLOW_THREADS
          for (int i=0 ; i<globval.Cell_nLoc ;i++)
          {
            PyList_SetItem(dt,i,PyFloat_FromDouble(Cell[i].BeamPos[5]));
          }
          Py_END_ALLOW_THREADS
          return dt;
        }
        else
        {
            // PyList_New() will have raised the exception.
            sipIsErr = 1;
            return NULL;
        }
%End

void GetNu(SIP_PYLIST, SIP_PYLIST  ); 
%MethodCode
            Vector2 nu;
            Matrix   M;
            GetNu(nu,M);

            for (int index=0; index<2; index++)
                 PyList_SetItem(a0, index, PyFloat_FromDouble((double) nu[index]));
            for (int i=0; i<ss_dim; ++i)
            {
              PyObject * row = PyList_GetItem(a1, i);
              for (int j=0; j<ss_dim; ++j)
                PyList_SetItem(row, j, PyFloat_FromDouble((double) M[i][j]));
            }
%End
