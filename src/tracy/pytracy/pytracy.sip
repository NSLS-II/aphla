%Module pytracy 0

%ModuleHeaderCode
#define ORDER 1
#include <../tracy-3.5/tracy/inc/tracy_lib.h>
void Mpole_Setmatrix(int Fnum1, int Knum1, double K);
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

SIP_PYOBJECT getElemName(SIP_PYOBJECT);
%MethodCode
        int i= (int) PyLong_AsLong(a0);
	if (i<1) 
	{ 
	  printf("Family Number must be a positive integer\n");
	  return NULL;
	}
	else
           return PyString_FromString(ElemFam[i-1].ElemF.PName);
%End

/*
void SetMpoleBsys(SIP_PYOBJECT,SIP_PYOBJECT,SIP_PYOBJECT); //, SIP_PYOBJECT);
%MethodCode
        partsName  name;
        char *ptr;
        int length;
        int i;
	int order;
	double val;
 	int fnum;
        int kidnum;
	int *kidlist;

        if (PyString_AsStringAndSize(a0, &ptr, &length) == -1 || !PyLong_Check(a1) || !PyNumber_Check(a2))
        {
           sipIsErr = 1;
        }
	else
	{ 
	  Py_BEGIN_ALLOW_THREADS
	  memcpy(name, "               " , sizeof(partsName));
	  order=PyLong_AsLong(a1);
	  val = PyFloat_AsDouble(a2);
	  for (i=0; i<length; ++i)
	  name[i]=tolower(ptr[i]);
        
          for (i=0; i<global.Elem_nFam; ++i)
	    if (!strncmp(name, ElemFam[i].ElemF.PName, sizeof(alfa_))
	    {
 	      kidnum = ElemFam[i].nKid;
	      kidlist= ElemFam[i].KidList;
	      break;
	    }
	  fnum = i;
	  for (i=0; i<kidnum; i++)
	  {
	    Cell[kidlist[i]].Elem->M->PBsys[HOMmax+order] = val;
	    Mpole_SetPB(fnum+1,i+1);
	  } 
	  Py_END_ALLOW_THREADS
	} 
%End
*/

SIP_PYOBJECT getFnumByName(SIP_PYOBJECT);
%MethodCode
        partsName  name;
        char *ptr;
        int length;
	long Fnum;
	int i;

        if (PyString_AsStringAndSize(a0, &ptr, &length) == -1)
        {
           sipIsErr = 1;
	   return NULL;
        }
	else
	{
	   Py_BEGIN_ALLOW_THREADS
	   memcpy(name, "               " , sizeof(partsName));
	   for (i=0; i<length; ++i) name[i]=tolower(ptr[i]);
           for (i=0; i<globval.Elem_nFam; ++i)
	     if (!strncmp(name, ElemFam[i].ElemF.PName, sizeof(alfa_))) break;
	   if (i==globval.Elem_nFam)
	   {
		printf("No element with the name\n");
		return NULL;
	   }
	   Fnum = i+1;
	   Py_END_ALLOW_THREADS
	   return PyLong_FromLong((long) Fnum);
	}
%End

// long Elem_GetPos(const int Fnum1, const int Knum1)

SIP_PYOBJECT Elem_GetPos(SIP_PYOBJECT, SIP_PYOBJECT);
%MethodCode
        long Fnum, Knum;
        long loc;
        if ((Fnum=PyLong_AsLong(a0))<0 || (Knum=PyLong_AsLong(a1))<0)
        {
          sipIsErr = 1;
          return NULL;
        }
        else
        {
	  if (Fnum < 1 || Knum <1 || Fnum > globval.Elem_nFam || Knum > ElemFam[Fnum-1].nKid)
	  {
	    printf("The indeces are not out of range\n");
	    return NULL;
	  }
	  else
	  {
            loc = Elem_GetPos(Fnum,Knum);
            return PyLong_FromLong(loc);
	  }
        }
%End

// double get_L(const int Fnum, const int Knum)
 
SIP_PYOBJECT get_L(SIP_PYOBJECT, SIP_PYOBJECT);
%MethodCode
	long Fnum, Knum;
	double len;
	if ((Fnum=PyLong_AsLong(a0))<0 || (Knum=PyLong_AsLong(a1))<0)
	{
	  sipIsErr = 1;
	  return NULL;
	}
	else
	{
	  if (Fnum < 1 || Knum <1 || Fnum > globval.Elem_nFam || Knum > ElemFam[Fnum-1].nKid)
	  {
	    printf("The indeces are not out of range\n");
	    return NULL;
	  }
	  else
	  {
	    len = get_L(Fnum,Knum);
	    return PyFloat_FromDouble(len);
	  }
	}
%End
	

// void set_L(const int Fnum, const int Knum, const double L)

void set_L(SIP_PYOBJECT, SIP_PYOBJECT, SIP_PYOBJECT);
%MethodCode
	long Fnum, Knum;
	double len;
       if ((Fnum=PyLong_AsLong(a0))<0 || (Knum=PyLong_AsLong(a1))<0 || !PyNumber_Check(a2))
        {
          sipIsErr = 1;
        }
        else
        {
	  if (Fnum < 1 || Knum <1 || Fnum > globval.Elem_nFam || Knum > ElemFam[Fnum-1].nKid)
	  {
	    printf("The indeces are not out of range\n");
	  }
	  else
	  {
            len = PyFloat_AsDouble(a2);
	    set_L(Fnum,Knum,len);
	  }
        }
%End

// void set_L(const int Fnum, const double L)

void set_L_all(SIP_PYOBJECT, SIP_PYOBJECT);
%MethodCode
        long Fnum;
        double len;
       if ((Fnum=PyLong_AsLong(a0))<0 || !PyNumber_Check(a1))
        {
          sipIsErr = 1;
        }
        else
        {
	  if (Fnum < 1 || Fnum > globval.Elem_nFam)
	  {
	    printf("The indeces are not out of range\n");
	  }
	  else
	  {
            len = PyFloat_AsDouble(a1);
            set_L(Fnum,len);
	  }
        }
%End


// void set_dL(const int Fnum, const int Knum, const double dL)

void set_dL(SIP_PYOBJECT, SIP_PYOBJECT, SIP_PYOBJECT);
%MethodCode
	long Fnum, Knum;
	double dl;
       if ((Fnum=PyLong_AsLong(a0))<0 || (Knum=PyLong_AsLong(a1))<0 || !PyNumber_Check(a2))
        {
          sipIsErr = 1;
        }
        else
        {
	  if (Fnum < 1 || Knum <1 || Fnum > globval.Elem_nFam || Knum > ElemFam[Fnum-1].nKid)
	  {
	    printf("The indeces are not out of range\n");
	  }
	  else
	  {
            dl = PyFloat_AsDouble(a2);
	    set_dL(Fnum,Knum,dl);
	  }
        }
%End

// void get_bn_design_elem(const int Fnum, const int Knum, const int n, double &bn, double &an)

SIP_PYLIST get_bn_design_elem(SIP_PYOBJECT, SIP_PYOBJECT, SIP_PYOBJECT);
%MethodCode
	PyObject * B;
	int Fnum, Knum, n;
	double bn,an;

        if((Fnum=(int) PyLong_AsLong(a0))<0 || (Knum=(int) PyLong_AsLong(a1))<0 || (n=(int) PyLong_AsLong(a2))<0)
        {
          sipIsErr = 1;
	  return NULL;
        }
	else
	{
	  if (Fnum < 1 || Knum <1 || Fnum > globval.Elem_nFam || Knum > ElemFam[Fnum-1].nKid)
	  {
	    printf("The indeces are not out of range\n");
	    return NULL;
	  }
	  else if (ElemFam[Fnum-1].ElemF.Pkind != Mpole)
	  {
	    printf("Fnum:%d is not a multipole\n", Fnum);
	    return NULL;
	  }
	  else
	  {
  	    get_bn_design_elem(Fnum, Knum, n, bn, an);
	    B = PyList_New(2);
	    PyList_SetItem(B, 0, PyFloat_FromDouble(bn));
	    PyList_SetItem(B, 1, PyFloat_FromDouble(an));
	    return B;
	  }
	}
%End

// void get_bnL_design_elem(const int Fnum, const int Knum, const int n, double &bnL, double &anL)

SIP_PYLIST get_bnL_design_elem(SIP_PYOBJECT, SIP_PYOBJECT, SIP_PYOBJECT);
%MethodCode
        PyObject * BL;
        int Fnum, Knum, n;
        double bnL,anL;

        if((Fnum=PyLong_AsLong(a0))<0 || (Knum=PyLong_AsLong(a1))<0 || (n=PyLong_AsLong(a2))<0)
        {
          sipIsErr = 1;
          return NULL;
        }
        else
        {
	  if (Fnum < 1 || Knum <1 || Fnum > globval.Elem_nFam || Knum > ElemFam[Fnum-1].nKid)
	  {
	    printf("The indeces are not out of range\n");
	    return NULL;
	  }
	  else if (ElemFam[Fnum-1].ElemF.Pkind != Mpole)
	  {
	    printf("Fnum:%d is not a multipole\n", Fnum);
	    return NULL;
	  }
	  else
	  {
            get_bnL_design_elem(Fnum, Knum, n, bnL, anL);
            BL = PyList_New(2);
            PyList_SetItem(BL, 0, PyFloat_FromDouble(bnL));
            PyList_SetItem(BL, 1, PyFloat_FromDouble(anL));
            return BL;
	  }
        }
%End

// void set_bn_design_elem(const int Fnum, const int Knum, const int n, const double bn, const double an)

void set_bn_design_elem(SIP_PYOBJECT, SIP_PYOBJECT, SIP_PYOBJECT, SIP_PYOBJECT, SIP_PYOBJECT);
%MethodCode
	int Fnum, Knum, n;
	double bn, an;

	if((Fnum=PyLong_AsLong(a0))<0 || (Knum=PyLong_AsLong(a1))<0 || (n=PyLong_AsLong(a2))<0 || !PyNumber_Check(a3) || !PyNumber_Check(a4))
        {
          sipIsErr = 1;
        }
        else
        {
	  if (Fnum < 1 || Knum <1 || Fnum > globval.Elem_nFam || Knum > ElemFam[Fnum-1].nKid)
	  {
	    printf("The indeces are not out of range\n");
	  }
	  else if (ElemFam[Fnum-1].ElemF.Pkind != Mpole)
	  {
	    printf("Fnum:%d is not a multipole\n", Fnum);
	  }
	  else
	  {
	    bn = PyFloat_AsDouble(a3);
	    an = PyFloat_AsDouble(a4);
            set_bn_design_elem(Fnum, Knum, n, bn, an);
	  }
	}
%End

// void set_dbn_design_elem(const int Fnum, const int Knum, const int n, const double dbn, const double dan)

void set_dbn_design_elem(SIP_PYOBJECT, SIP_PYOBJECT, SIP_PYOBJECT, SIP_PYOBJECT, SIP_PYOBJECT);
%MethodCode
        int Fnum, Knum, n;
        double dbn, dan;

        if((Fnum=PyLong_AsLong(a0))<0 || (Knum=PyLong_AsLong(a1))<0 || (n=PyLong_AsLong(a2))<0 || !PyNumber_Check(a3) || !PyNumber_Check(a4))
        {
          sipIsErr = 1;
        }
        else
        {
	  if (Fnum < 1 || Knum <1 || Fnum > globval.Elem_nFam || Knum > ElemFam[Fnum-1].nKid)
	  {
	    printf("The indeces are not out of range\n");
	  }
	  else if (ElemFam[Fnum-1].ElemF.Pkind != Mpole)
	  {
	    printf("Fnum:%d is not a multipole\n", Fnum);
	  }
	  else
	  {
            dbn = PyFloat_AsDouble(a3);
            dan = PyFloat_AsDouble(a4);
            set_dbn_design_elem(Fnum, Knum, n, dbn, dan);
	  }
        }
%End

// void set_bn_design_fam(const int Fnum, const int n, const double bn, const double an)

void set_bn_design_fam(SIP_PYOBJECT, SIP_PYOBJECT, SIP_PYOBJECT, SIP_PYOBJECT);
%MethodCode
        int Fnum, Knum, n;
        double bn, an;

        if((Fnum=PyLong_AsLong(a0))<0 || (n=PyLong_AsLong(a1))<0 || !PyNumber_Check(a2) || !PyNumber_Check(a3))
        {
          sipIsErr = 1;
        }
        else
        {
	  if (Fnum < 1 || Fnum > globval.Elem_nFam)
	  {
	    printf("The indeces are not out of range\n");
	  }
	  else if (ElemFam[Fnum-1].ElemF.Pkind != Mpole)
	  {
	    printf("Fnum:%d is not a multipole\n", Fnum);
	  }
	  else
	  {
            bn = PyFloat_AsDouble(a2);
            an = PyFloat_AsDouble(a3);
            set_bn_design_fam(Fnum, n, bn, an);
	  }
        }
%End


// void set_dbn_design_fam(const int Fnum, const int n, const double dbn, const double dan)

void set_dbn_design_fam(SIP_PYOBJECT, SIP_PYOBJECT, SIP_PYOBJECT, SIP_PYOBJECT);
%MethodCode
        int Fnum, n;
        double dbn, dan;

        if((Fnum=PyLong_AsLong(a0))<0 || (n=PyLong_AsLong(a1))<0 || !PyNumber_Check(a2) || !PyNumber_Check(a3))
        {
          sipIsErr = 1;
        }
        else
        {
	  if (Fnum < 1 || Fnum > globval.Elem_nFam)
	  {
	    printf("The indeces are not out of range\n");
	  }
	  else if (ElemFam[Fnum-1].ElemF.Pkind != Mpole)
	  {
	    printf("Fnum:%d is not a multipole\n", Fnum);
	  }
	  else
	  {
            dbn = PyFloat_AsDouble(a2);
            dan = PyFloat_AsDouble(a3);
            set_dbn_design_fam(Fnum, n, dbn, dan);
	  }
        }
%End

// void set_bnL_design_elem(const int Fnum, const int Knum, const int n, const double bnL, const double anL)

void set_bnL_design_elem(SIP_PYOBJECT, SIP_PYOBJECT, SIP_PYOBJECT, SIP_PYOBJECT, SIP_PYOBJECT);
%MethodCode
        int Fnum, Knum, n;
        double bnL, anL;

        if((Fnum=PyLong_AsLong(a0))<0 || (Knum=PyLong_AsLong(a1))<0 || (n=PyLong_AsLong(a2))<0 || !PyNumber_Check(a3) || !PyNumber_Check(a4))
        {
          sipIsErr = 1;
        }
        else
        {
	  if (Fnum < 1 || Knum <1 || Fnum > globval.Elem_nFam || Knum > ElemFam[Fnum-1].nKid)
	  {
	    printf("The indeces are not out of range\n");
	  }
	  else if (ElemFam[Fnum-1].ElemF.Pkind != Mpole)
	  {
	    printf("Fnum:%d is not a multipole\n", Fnum);
	  }
	  else
	  {
            bnL = PyFloat_AsDouble(a3);
            anL = PyFloat_AsDouble(a4);
            set_bnL_design_elem(Fnum, Knum, n, bnL, anL);
	  }
        }
%End


// void set_dbnL_design_elem(const int Fnum, const int Knum, const int n, const double dbnL, const double danL)

void set_dbnL_design_elem(SIP_PYOBJECT, SIP_PYOBJECT, SIP_PYOBJECT, SIP_PYOBJECT, SIP_PYOBJECT);
%MethodCode
        int Fnum, Knum, n;
        double dbnL, danL;
                          
        if((Fnum=PyLong_AsLong(a0))<0 || (Knum=PyLong_AsLong(a1))<0 || (n=PyLong_AsLong(a2))<0 || !PyNumber_Check(a3) || !PyNumber_Check(a4))
        {
          sipIsErr = 1;
        }
        else
        {
	  if (Fnum < 1 || Knum <1 || Fnum > globval.Elem_nFam || Knum > ElemFam[Fnum-1].nKid)
	  {
	    printf("The indeces are not out of range\n");
	  }
	  else if (ElemFam[Fnum-1].ElemF.Pkind != Mpole)
	  {
	    printf("Fnum:%d is not a multipole\n", Fnum);
	  }
	  else
	  {
            dbnL = PyFloat_AsDouble(a3);
            danL = PyFloat_AsDouble(a4);
            set_dbnL_design_elem(Fnum, Knum, n, dbnL, danL);
	  }
        }
%End

// void set_dbnL_design_fam(const int Fnum, const int n, const double dbnL, const double danL)

void set_dbnL_design_fam(SIP_PYOBJECT, SIP_PYOBJECT, SIP_PYOBJECT, SIP_PYOBJECT);
%MethodCode
        int Fnum, n;
        double dbnL, danL;

        if((Fnum=PyLong_AsLong(a0))<0 || (n=PyLong_AsLong(a1))<0 || !PyNumber_Check(a2) || !PyNumber_Check(a3))
        {
          sipIsErr = 1;
        }
        else
        {
	  if (Fnum < 1 || Fnum > globval.Elem_nFam)
	  {
	    printf("The indeces are not out of range\n");
	  }
	  else if (ElemFam[Fnum-1].ElemF.Pkind != Mpole)
	  {
	    printf("Fnum:%d is not a multipole\n", Fnum);
	  }
	  else
	  {
            dbnL = PyFloat_AsDouble(a2);
            danL = PyFloat_AsDouble(a3);
            set_dbnL_design_fam(Fnum, n, dbnL, danL);
	  }
        }
%End


// void set_bnL_design_fam(const int Fnum, const int n, const double bnL, const double anL)

void set_bnL_design_fam(SIP_PYOBJECT, SIP_PYOBJECT, SIP_PYOBJECT, SIP_PYOBJECT);
%MethodCode
        int Fnum, Knum, n;
        double bnL, anL;

        if((Fnum=PyLong_AsLong(a0))<0 || (n=PyLong_AsLong(a1))<0 || !PyNumber_Check(a2) || !PyNumber_Check(a3))
        {
          sipIsErr = 1;
        }
        else
        {
	  if (Fnum < 1 || Fnum > globval.Elem_nFam)
	  {
	    printf("The indeces are not out of range\n");
	  }
	  else if (ElemFam[Fnum-1].ElemF.Pkind != Mpole)
	  {
	    printf("Fnum:%d is not a multipole\n", Fnum);
	  }
	  else
	  {
            bnL = PyFloat_AsDouble(a2);
            anL = PyFloat_AsDouble(a3);
            set_bnL_design_fam(Fnum, n, bnL, anL);
	  }
        }
%End


// void set_bnL_design_type(const int type, const int n, const double bnL, const double anL)

void set_bnL_design_type(SIP_PYOBJECT, SIP_PYOBJECT, SIP_PYOBJECT, SIP_PYOBJECT);
%MethodCode
        int type, n;
        double bnL, anL;

        if((type=PyLong_AsLong(a0))<0 || (n=PyLong_AsLong(a1))<0 || !PyNumber_Check(a2) || !PyNumber_Check(a3))
        {
          sipIsErr = 1;
        }
        else
        {
          bnL = PyFloat_AsDouble(a2);
          anL = PyFloat_AsDouble(a3);
          set_bnL_design_type(type, n, bnL, anL);
        }
%End

// void set_bnL_sys_elem(const int Fnum, const int Knum, const int n, const double bnL, const double anL)

void set_bnL_sys_elem(SIP_PYOBJECT, SIP_PYOBJECT, SIP_PYOBJECT, SIP_PYOBJECT, SIP_PYOBJECT);
%MethodCode
        int Fnum, Knum, n;
        double bnL, anL;

        if((Fnum=PyLong_AsLong(a0))<0 || (Knum=PyLong_AsLong(a1))<0 || (n=PyLong_AsLong(a2))<0 || !PyNumber_Check(a3) || !PyNumber_Check(a4))
        {
          sipIsErr = 1;
        }
        else
        {
	  if (Fnum < 1 || Knum <1 || Fnum > globval.Elem_nFam || Knum > ElemFam[Fnum-1].nKid)
	  {
	    printf("The indeces are not out of range\n");
	  }
	  else if (ElemFam[Fnum-1].ElemF.Pkind != Mpole)
	  {
	    printf("Fnum:%d is not a multipole\n", Fnum);
	  }
	  else
	  {
            bnL = PyFloat_AsDouble(a3);
            anL = PyFloat_AsDouble(a4);
            set_bnL_sys_elem(Fnum, Knum, n, bnL, anL);
	  }
        }
%End


// void set_bnL_sys_fam(const int Fnum, const int n, const double bnL, const double anL)

void set_bnL_sys_fam(SIP_PYOBJECT, SIP_PYOBJECT, SIP_PYOBJECT, SIP_PYOBJECT);
%MethodCode
        int Fnum, n;
        double bnL, anL;

        if((Fnum=PyLong_AsLong(a0))<0 || (n=PyLong_AsLong(a1))<0 || !PyNumber_Check(a2) || !PyNumber_Check(a3))
        {
          sipIsErr = 1;
        }
        else
        {
	  if (Fnum < 1 || Fnum > globval.Elem_nFam)
	  {
	    printf("The indeces are not out of range\n");
	  }
	  else if (ElemFam[Fnum-1].ElemF.Pkind != Mpole)
	  {
	    printf("Fnum:%d is not a multipole\n", Fnum);
	  }
	  else
	  {
            bnL = PyFloat_AsDouble(a2);
            anL = PyFloat_AsDouble(a3);
            set_bnL_sys_fam(Fnum, n, bnL, anL);
	  }
        }
%End

// void set_bnL_sys_type(const int type, const int n, const double bnL, const double anL)

void set_bnL_sys_type(SIP_PYOBJECT, SIP_PYOBJECT, SIP_PYOBJECT, SIP_PYOBJECT);
%MethodCode
        int type, n;
        double bnL, anL;

        if((type=PyLong_AsLong(a0))<0 || (n=PyLong_AsLong(a1))<0 || !PyNumber_Check(a2) || !PyNumber_Check(a3))
        {
          sipIsErr = 1;
        }
        else
        {
          bnL = PyFloat_AsDouble(a2);
          anL = PyFloat_AsDouble(a3);
          set_bnL_sys_type(type, n, bnL, anL);
        }
%End

// void set_bnL_rms_elem(const int Fnum, const int Knum, const int n, const double bnL, const double anL, const bool new_rnd)

void set_bnL_rms_elem(SIP_PYOBJECT, SIP_PYOBJECT, SIP_PYOBJECT, SIP_PYOBJECT, SIP_PYOBJECT, SIP_PYOBJECT);
%MethodCode
        int Fnum, Knum, n;
        double bnL, anL;
	bool new_rnd=false;

        if((Fnum=PyLong_AsLong(a0))<0 || (Knum=PyLong_AsLong(a1))<0 || (n=PyLong_AsLong(a2))<0 || !PyNumber_Check(a3) || !PyNumber_Check(a4) || !PyBool_Check(a5))
        {
          sipIsErr = 1;
        }
        else
        {
	  if (Fnum < 1 || Knum <1 || Fnum > globval.Elem_nFam || Knum > ElemFam[Fnum-1].nKid)
	  {
	    printf("The indeces are not out of range\n");
	  }
	  else if (ElemFam[Fnum-1].ElemF.Pkind != Mpole)
	  {
	    printf("Fnum:%d is not a multipole\n", Fnum);
	  }
	  else
	  {
            bnL = PyFloat_AsDouble(a3);
            anL = PyFloat_AsDouble(a4);
	    if (a5 == Py_True) new_rnd=true;
            set_bnL_rms_elem(Fnum, Knum, n, bnL, anL, new_rnd);
	  }
        }
%End

// void set_bnL_rms_fam(const int Fnum, const int n, const double bnL, const double anL, const bool new_rnd)

void set_bnL_rms_fam(SIP_PYOBJECT, SIP_PYOBJECT, SIP_PYOBJECT, SIP_PYOBJECT, SIP_PYOBJECT);
%MethodCode
        int Fnum, n;
        double bnL, anL;
        bool new_rnd=false;

        if((Fnum=PyLong_AsLong(a0))<0 || (n=PyLong_AsLong(a1))<0 || !PyNumber_Check(a2) || !PyNumber_Check(a3) || !PyBool_Check(a4))
        {
          sipIsErr = 1;
        }
        else
        {
	  if (Fnum < 1 || Fnum > globval.Elem_nFam)
	  {
	    printf("The indeces are not out of range\n");
	  }
	  else if (ElemFam[Fnum-1].ElemF.Pkind != Mpole)
	  {
	    printf("Fnum:%d is not a multipole\n", Fnum);
	  }
	  else
	  {
            bnL = PyFloat_AsDouble(a2);
            anL = PyFloat_AsDouble(a3);
            if (a4 == Py_True) new_rnd=true;
            set_bnL_rms_fam(Fnum, n, bnL, anL, new_rnd);
	  }
        }
%End


// void set_bnL_rms_type(const int type, const int n, const double bnL, const double anL, const bool new_rnd)

void set_bnL_rms_type(SIP_PYOBJECT, SIP_PYOBJECT, SIP_PYOBJECT, SIP_PYOBJECT, SIP_PYOBJECT);
%MethodCode
        int type, n;
        double bnL, anL;
        bool new_rnd=false; 

        if((type=PyLong_AsLong(a0))<0 || (n=PyLong_AsLong(a1))<0 || !PyNumber_Check(a2) || !PyNumber_Check(a3) || !PyBool_Check(a4))
        {
          sipIsErr = 1;
        }
        else
        {
          bnL = PyFloat_AsDouble(a2);
          anL = PyFloat_AsDouble(a3);
          if (a4 == Py_True) new_rnd=true;
          set_bnL_rms_type(type, n, bnL, anL, new_rnd);
        }
%End

// void set_bnr_sys_elem(const int Fnum, const int Knum, const int n, const double bnr, const double anr)

void set_bnr_sys_elem(SIP_PYOBJECT, SIP_PYOBJECT, SIP_PYOBJECT, SIP_PYOBJECT, SIP_PYOBJECT);
%MethodCode
        int Fnum, Knum, n;
        double bnr, anr;

        if((Fnum=PyLong_AsLong(a0))<0 || (Knum=PyLong_AsLong(a1))<0 || (n=PyLong_AsLong(a2))<0 || !PyNumber_Check(a3) || !PyNumber_Check(a4))
        {
          sipIsErr = 1;
        }
        else
        {
	  if (Fnum < 1 || Knum <1 || Fnum > globval.Elem_nFam || Knum > ElemFam[Fnum-1].nKid)
	  {
	    printf("The indeces are not out of range\n");
	  }
	  else if (ElemFam[Fnum-1].ElemF.Pkind != Mpole)
	  {
	    printf("Fnum:%d is not a multipole\n", Fnum);
	  }
	  else
	  {
            bnr = PyFloat_AsDouble(a3);
            anr = PyFloat_AsDouble(a4);
            set_bnr_sys_elem(Fnum, Knum, n, bnr, anr);
	  }
        }
%End

// void set_bnr_sys_fam(const int Fnum, const int n, const double bnr, const double anr)

void set_bnr_sys_fam(SIP_PYOBJECT, SIP_PYOBJECT, SIP_PYOBJECT, SIP_PYOBJECT);
%MethodCode
        int Fnum, n;
        double bnr, anr;

        if((Fnum=PyLong_AsLong(a0))<0 || (n=PyLong_AsLong(a1))<0 || !PyNumber_Check(a2) || !PyNumber_Check(a3))
        {
          printf("PyFloat Check Failed\n");
          sipIsErr = 1;
	  return NULL;
        }
        else
        {
	  if (Fnum < 1 || Fnum > globval.Elem_nFam)
	  {
	    printf("The indeces are not out of range\n");
	  }
	  else if (ElemFam[Fnum-1].ElemF.Pkind != Mpole)
	  {
	    printf("Fnum:%d is not a multipole\n", Fnum);
	  }
	  else
	  {
            bnr = PyFloat_AsDouble(a2);
            anr = PyFloat_AsDouble(a3);
            set_bnr_sys_fam(Fnum, n, bnr, anr);
	  }
        }
%End


// void set_bnr_sys_type(const int type, const int n, const double bnr, const double anr)

void set_bnr_sys_type(SIP_PYOBJECT, SIP_PYOBJECT, SIP_PYOBJECT, SIP_PYOBJECT);
%MethodCode
        int type, n;
        double bnr, anr;

        if((type=PyLong_AsLong(a0))<0 || (n=PyLong_AsLong(a1))<0 || !PyNumber_Check(a2) || !PyNumber_Check(a3))
        {
          sipIsErr = 1;
        }
        else
        {
          bnr = PyFloat_AsDouble(a2);
          anr = PyFloat_AsDouble(a3);
          set_bnr_sys_type(type, n, bnr, anr);
        }
%End

// void set_bnr_rms_elem(const int Fnum, const int Knum, const int n, const double bnr, const double anr, const bool new_rnd)

void set_bnr_rms_elem(SIP_PYOBJECT, SIP_PYOBJECT, SIP_PYOBJECT, SIP_PYOBJECT, SIP_PYOBJECT, SIP_PYOBJECT);
%MethodCode
        int Fnum, Knum, n;
        double bnr, anr;
        bool new_rnd=false;

        if((Fnum=PyLong_AsLong(a0))<0 || (Knum=PyLong_AsLong(a1))<0 || (n=PyLong_AsLong(a2))<0 || !PyNumber_Check(a3) || !PyNumber_Check(a4) || !PyBool_Check(a5))
        {
          sipIsErr = 1;
        }
        else
        {
	  if (Fnum < 1 || Knum <1 || Fnum > globval.Elem_nFam || Knum > ElemFam[Fnum-1].nKid)
	  {
	    printf("The indeces are not out of range\n");
	  }
	  else if (ElemFam[Fnum-1].ElemF.Pkind != Mpole)
	  {
	    printf("Fnum:%d is not a multipole\n", Fnum);
	  }
	  else
	  {
            bnr = PyFloat_AsDouble(a3);
            anr = PyFloat_AsDouble(a4);
            if (a5 == Py_True) new_rnd=true;
            set_bnr_rms_elem(Fnum, Knum, n, bnr, anr, new_rnd);
	  }
        }
%End

// void set_bnr_rms_fam(const int Fnum, const int n, const double bnr, const double anr, const bool new_rnd)

void set_bnr_rms_fam(SIP_PYOBJECT, SIP_PYOBJECT, SIP_PYOBJECT, SIP_PYOBJECT, SIP_PYOBJECT);
%MethodCode
        int Fnum, n;
        double bnr, anr;
        bool new_rnd=false;

        if((Fnum=PyLong_AsLong(a0))<0 || (n=PyLong_AsLong(a1))<0 || !PyNumber_Check(a2) || !PyNumber_Check(a3) || !PyBool_Check(a4))
        {
          sipIsErr = 1;
        }
        else
        {
	  if (Fnum < 1 || Fnum > globval.Elem_nFam)
	  {
	    printf("The indeces are not out of range\n");
	  }
	  else if (ElemFam[Fnum-1].ElemF.Pkind != Mpole)
	  {
	    printf("Fnum:%d is not a multipole\n", Fnum);
	  }
	  else
	  {
            bnr = PyFloat_AsDouble(a2);
            anr = PyFloat_AsDouble(a3);
            if (a4 == Py_True) new_rnd=true;
            set_bnr_rms_fam(Fnum, n, bnr, anr, new_rnd);
	  }
        }
%End


// void set_bnr_rms_type(const int type, const int n, const double bnr, const double anr, const bool new_rnd)

void set_bnr_rms_type(SIP_PYOBJECT, SIP_PYOBJECT, SIP_PYOBJECT, SIP_PYOBJECT, SIP_PYOBJECT);
%MethodCode
        int type, n;
        double bnr, anr;
        bool new_rnd=false;

        if((type=PyLong_AsLong(a0))<0 || (n=PyLong_AsLong(a1))<0 || !PyNumber_Check(a2) || !PyNumber_Check(a3) || !PyBool_Check(a4))
        {
          sipIsErr = 1;
        }
        else
        {
          bnr = PyFloat_AsDouble(a2);
          anr = PyFloat_AsDouble(a3);
          if (a4 == Py_True) new_rnd=true;
          set_bnr_rms_type(type, n, bnr, anr, new_rnd);
        }
%End

/*
SIP_PYOBJECT Mpole_GetPB(SIP_PYOBJECT, SIP_PYOBJECT, SIP_PYOBJECT);
%MethodCode
	int Fnum, Knum, Order;
	double val;

        if (!PyLong_Check(a0) && !PyLong_Check(a1) && !PyLong_Check(a2))
        {
           sipIsErr = 1;
	   return NULL;
        }
	else
	{ 
	  Py_BEGIN_ALLOW_THREADS

	  Fnum=PyLong_AsLong(a0);
	  Knum=PyLong_AsLong(a1);
	  Order=PyLong_AsLong(a2);

	  val = Mpole_GetPB(Fnum+1,Knum+1,Order);

	  Py_END_ALLOW_THREADS

	  return PyFloat_FromDouble((double) val);
	}
%End
*/

// void Mpole_Init(int Fnum1)
void Reset_Mpole(SIP_PYOBJECT);
%MethodCode
  long Fnum1;
  double       x;
  int          i, order;
  ElemFamType  *elemfamp;
  CellType     *cellp;
  elemtype     *elemp;

  if ((Fnum1 = PyLong_AsLong(a0))<0)
  {
    sipIsErr = 1;
  }
  else if (Fnum1 < 1 || Fnum1 > globval.Elem_nFam)
  {
    printf("The indeces are not out of range\n");
  }
  else if (ElemFam[Fnum1-1].ElemF.Pkind != Mpole)
  {
    printf("Fnum:%d is not a multipole\n", Fnum1);
  }
  else
  {
    Py_BEGIN_ALLOW_THREADS
 MpoleType  *M;

    /* Pointer on element */
    elemfamp = &ElemFam[Fnum1-1];
    memcpy(elemfamp->ElemF.M->PB, elemfamp->ElemF.M->PBpar, sizeof(mpolArray));
    /* Update the right multipole order */
 M = elemfamp->ElemF.M;
  if (M->Pirho != 0.0) /* non zero curvature => bend */
    order = 1;
  else /* mutipole */
    order = 0;
  for (i = -HOMmax; i <= HOMmax; i++)
    if (M->PB[i+HOMmax] != 0.0 && abs(i) > order) order = abs(i);

    elemfamp->ElemF.M->Porder = order; //UpdatePorder(elemfamp->ElemF);
    /* Quadrupole strength */
    x = elemfamp->ElemF.M->PBpar[Quad+HOMmax];
    for (i = 1; i <= elemfamp->nKid; i++) {
      cellp = &Cell[elemfamp->KidList[i-1]];
      /* Memory allocation and set everything to zero */
  //    Mpole_Alloc(&cellp->Elem);
  //    memcpy(cellp->Elem.PName, elemfamp->ElemF.PName, sizeof(partsName));
      /* set length */
      cellp->Elem.PL = elemfamp->ElemF.PL;
      /* set element kind (Mpole) */
  //    cellp->Elem.Pkind = elemfamp->ElemF.Pkind;
      *cellp->Elem.M = *elemfamp->ElemF.M;
  
      elemp = &cellp->Elem;
      /* set entrance and exit angles */
      cellp->dT[0] = cos(dtor(elemp->M->PdTpar));
      cellp->dT[1] = sin(dtor(elemp->M->PdTpar));
  
      /* set displacement to zero */
      cellp->dS[0] = 0.0; cellp->dS[1] = 0.0;
  
      if (elemp->PL != 0.0 || elemp->M->Pirho != 0.0) {
        /* Thick element or radius non zero element */
        elemp->M->Pthick = pthicktype(thick);
        /* sin(L*irho/2) =sin(theta/2) half the angle */
        elemp->M->Pc0 = sin(elemp->PL*elemp->M->Pirho/2e0);
        /* cos roll: sin(theta/2)*cos(dT) */
        elemp->M->Pc1 = cellp->dT[0]*elemp->M->Pc0;
        /* sin roll: sin(theta/2)*cos(dT) */
        elemp->M->Ps1 = cellp->dT[1]*elemp->M->Pc0;
        Mpole_Setmatrix(Fnum1, i, x);
      } else /* element as thin lens */
        elemp->M->Pthick = pthicktype(thin);
    }
    Py_END_ALLOW_THREADS
  }
%End
