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

        if ((s = PyList_New(globval.Cell_nLoc+1)))
        {
          Py_BEGIN_ALLOW_THREADS
          for (int i=0 ; i<=globval.Cell_nLoc ;i++)
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
      
        if ((bx = PyList_New(globval.Cell_nLoc+1)))
        {
          Py_BEGIN_ALLOW_THREADS
          for (int i=0 ; i<=globval.Cell_nLoc ;i++)
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

        if ((by = PyList_New(globval.Cell_nLoc+1)))
        {
          Py_BEGIN_ALLOW_THREADS
          for (int i=0 ; i<=globval.Cell_nLoc ;i++)
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

        if ((ax = PyList_New(globval.Cell_nLoc+1)))
        {
          Py_BEGIN_ALLOW_THREADS
          for (int i=0 ; i<=globval.Cell_nLoc ;i++)
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

        if ((ay = PyList_New(globval.Cell_nLoc+1)))
        {
          Py_BEGIN_ALLOW_THREADS
          for (int i=0 ; i<=globval.Cell_nLoc ;i++)
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

        if ((ex = PyList_New(globval.Cell_nLoc+1)))
        {
          Py_BEGIN_ALLOW_THREADS
          for (int i=0 ; i<=globval.Cell_nLoc ;i++)
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

        if ((ex = PyList_New(globval.Cell_nLoc+1)))
        {
          Py_BEGIN_ALLOW_THREADS
          for (int i=0 ; i<=globval.Cell_nLoc ;i++)
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

        if ((exp = PyList_New(globval.Cell_nLoc+1)))
        {
          Py_BEGIN_ALLOW_THREADS
          for (int i=0 ; i<=globval.Cell_nLoc ;i++)
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

        if ((eyp = PyList_New(globval.Cell_nLoc+1)))
        {
          Py_BEGIN_ALLOW_THREADS
          for (int i=0 ; i<=globval.Cell_nLoc ;i++)
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

        if ((px = PyList_New(globval.Cell_nLoc+1)))
        {
          Py_BEGIN_ALLOW_THREADS
          for (int i=0 ; i<=globval.Cell_nLoc ;i++)
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

        if ((py = PyList_New(globval.Cell_nLoc+1)))
        {
          Py_BEGIN_ALLOW_THREADS
          for (int i=0 ; i<=globval.Cell_nLoc ;i++)
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

        if ((X = PyList_New(globval.Cell_nLoc+1)))
        {
          Py_BEGIN_ALLOW_THREADS
          for (int i=0 ; i<=globval.Cell_nLoc ;i++)
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

        if ((xp = PyList_New(globval.Cell_nLoc+1)))
        {
          Py_BEGIN_ALLOW_THREADS
          for (int i=0 ; i<=globval.Cell_nLoc ;i++)
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

        if ((Y = PyList_New(globval.Cell_nLoc+1)))
        {
          Py_BEGIN_ALLOW_THREADS
          for (int i=0 ; i<=globval.Cell_nLoc ;i++)
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

        if ((yp = PyList_New(globval.Cell_nLoc+1)))
        {
          Py_BEGIN_ALLOW_THREADS
          for (int i=0 ; i<=globval.Cell_nLoc ;i++)
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

        if ((dp = PyList_New(globval.Cell_nLoc+1)))
        {
          Py_BEGIN_ALLOW_THREADS
          for (int i=0 ; i<=globval.Cell_nLoc ;i++)
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

        if ((dt = PyList_New(globval.Cell_nLoc+1)))
        {
          Py_BEGIN_ALLOW_THREADS
          for (int i=0 ; i<=globval.Cell_nLoc ;i++)
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

SIP_PYLIST GetNu(SIP_PYOBJECT);
%MethodCode
            Vector2 nu;
            Matrix   M;

	    PyObject * PyNu;

	    if ((PyNu = PyList_New(2)))
	    {
              for (int i=0; i<ss_dim; ++i)
              {
                PyObject * row = PyList_GetItem(a0, i);
                for (int j=0; j<ss_dim; ++j)
        	  M[i][j] = PyFloat_AsDouble(PyList_GetItem(row,j));
              }
  
              GetNu(nu,M);

              for (int index=0; index<2; index++)
                PyList_SetItem(PyNu, index, PyFloat_FromDouble((double) nu[index]));

      	      return PyNu;
	    }
	    else
 	    {
	      sipIsErr = 1;
	      return NULL;
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
	    Cell[kidlist[i]].Elem.M->PBsys[HOMmax+order] = val;
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

SIP_PYLIST get_bn_rnd_elem(SIP_PYOBJECT, SIP_PYOBJECT, SIP_PYOBJECT);
%MethodCode
        PyObject * B;
        int Fnum, Knum, n;
        double bn,an;
	int Enum;

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
	    Enum = ElemFam[Fnum-1].KidList[Knum-1];
	    bn = Cell[Enum].Elem.M->PBrnd[HOMmax+n];
	    an = Cell[Enum].Elem.M->PBrnd[HOMmax-n];
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
        int Fnum, n;
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

        if ((Fnum=PyLong_AsLong(a0)) < 0 || (Knum=PyLong_AsLong(a1)) <0  || (Order=PyLong_AsLong(a2)) < 0)
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
	    Py_BEGIN_ALLOW_THREADS

	    Knum=PyLong_AsLong(a1);
	    Order=PyLong_AsLong(a2);

	    val = Mpole_GetPB(Fnum+1,Knum+1,Order);

	    Py_END_ALLOW_THREADS

	    return PyFloat_FromDouble((double) val);
          }
	}
%End
*/

void InitRand(SIP_PYOBJECT,SIP_PYOBJECT);
%MethodCode
        int seed;

        if((seed=PyLong_AsLong(a0))<0 || !PyNumber_Check(a1) )
        {
           sipIsErr = 1;
        }
	else
	{
	  rseed0 = seed;
	  rseed  = seed;
	  normcut_ = (double) PyFloat_AsDouble(a1);
	}
%End

//int GetnKid(const int Fnum1) { return (ElemFam[Fnum1-1].nKid); }

SIP_PYOBJECT GetnKid(SIP_PYOBJECT);
%MethodCode
	int Fnum, Knum;

        if ((Fnum=PyLong_AsLong(a0)) < 0 )
        {
           sipIsErr = 1;
           return NULL;
        }
        else
        {
          if (Fnum < 1 || Fnum > globval.Elem_nFam )
          {
            printf("The indeces are not out of range\n");
            return NULL;
          }
          else
          {
            Py_BEGIN_ALLOW_THREADS

            Knum=GetnKid(Fnum);

            Py_END_ALLOW_THREADS

            return PyLong_FromLong((long) Knum);
          }
        }
%End

//void Cell_SetdP(const double dP)
void Cell_SetdP(SIP_PYOBJECT);
%MethodCode
	double dP;

	if (!PyNumber_Check(a0))
	{
	  sipIsErr = 1;
	}
	else
	{
	    Py_BEGIN_ALLOW_THREADS

	    dP = PyFloat_AsDouble(a0);
	    Cell_SetdP(dP);

            Py_END_ALLOW_THREADS
	}
%End

//void Cell_Pass(const long i0, const long i1, ss_vect<T> &x, long &lastpos)
SIP_PYOBJECT Cell_Pass(SIP_PYOBJECT, SIP_PYOBJECT, SIP_PYOBJECT);
%MethodCode
        long i0, i1, ilast;
	Vector x;
	PyObject *lastpos ;
        int i;

        if ((i0=PyLong_AsLong(a0))<0 || (i1=PyLong_AsLong(a1))<0 || !PyList_Check(a2))
        {
          sipIsErr = 1;
	  return NULL;
        }
        else if (i1>globval.Cell_nLoc || i0>i1 || PyList_GET_SIZE(a2) != 6)
        {
	  printf("Argument not Correct\n");
	  return NULL;
	}
	else
	{
            Py_BEGIN_ALLOW_THREADS

            for (i=0; i<6; ++i)
	      x[i] = PyFloat_AsDouble(PyList_GetItem(a2,i));
            Cell_Pass(i0, i1, x, ilast);

	    lastpos = PyLong_FromLong(ilast);
            for (i=0; i<6; ++i)
	      PyList_SetItem(a2,i,PyFloat_FromDouble(x[i]));

	    return lastpos;

            Py_END_ALLOW_THREADS
        }
%End


//void Cell_Pass_M(long i0, long i1, Vector &xref, Matrix &mat, long &lastpos)
SIP_PYOBJECT Cell_Pass_M(SIP_PYOBJECT, SIP_PYOBJECT, SIP_PYOBJECT, SIP_PYOBJECT);
%MethodCode
        long i0, i1, ilast;
        Vector x;
	Matrix M;
        PyObject *lastpos ;

        if ((i0=PyLong_AsLong(a0))<0 || (i1=PyLong_AsLong(a1))<0 || !PyList_Check(a2) || !PyList_Check(a3))
        {
          sipIsErr = 1;
          return NULL;
        }
        else if (i1>globval.Cell_nLoc || i0>i1 || PyList_GET_SIZE(a2) != 6 || PyList_GET_SIZE(a3) != 6)
        {
          printf("Argument not Correct\n");
          return NULL;
        }
        else
        {
            Py_BEGIN_ALLOW_THREADS

            int i,j;
            for (i=0; i<6; ++i)
	    {
              x[i] = PyFloat_AsDouble(PyList_GetItem(a2,i));
	      PyObject * row = PyList_GetItem(a3,i);
	      for (j=0; j<6; ++j)
		M[i][j]=PyFloat_AsDouble(PyList_GetItem(row,j));
            }

            Cell_Pass_M(i0, i1, x, M, ilast);

            lastpos = PyLong_FromLong(ilast);

            for (i=0; i<6; ++i)
	    {
              PyList_SetItem(a2,i,PyFloat_FromDouble(x[i]));
	      PyObject * row = PyList_GetItem(a3,i);
	      for (j=0; j<6; ++j)
		PyList_SetItem(row,j,PyFloat_FromDouble(M[i][j]));
            }
	    lastpos = PyLong_FromLong(ilast);

            return lastpos;

            Py_END_ALLOW_THREADS
        }
%End


// void Cell_fPass(ss_vect<double> &x, long &lastpos)
SIP_PYOBJECT Cell_fPass(SIP_PYOBJECT);
%MethodCode
        long ilast;
        Vector x;
        PyObject *lastpos ;
	int i;

        if (!PyList_Check(a0))
        {
          sipIsErr = 1;
          return NULL;
        }
        else if (PyList_GET_SIZE(a0) != 6)
        {
          printf("Argument not Correct\n");
          return NULL;
        }
        else
        {
            Py_BEGIN_ALLOW_THREADS

            for (i=0; i<6; ++i)
              x[i] = PyFloat_AsDouble(PyList_GetItem(a0,i));
            Cell_fPass(x, ilast);

            lastpos = PyLong_FromLong(ilast);
            for (i=0; i<6; ++i)
              PyList_SetItem(a0,i,PyFloat_FromDouble(x[i]));

            return lastpos;

            Py_END_ALLOW_THREADS
        }
%End

// void Cell_fPass_M(ss_vect<double> &xref, Matrix &mat, long &lastpos)
SIP_PYOBJECT Cell_fPass_M(SIP_PYOBJECT, SIP_PYOBJECT);
%MethodCode
        long ilast;
        Vector x;
        Matrix M;
        PyObject *lastpos ;

        if (!PyList_Check(a0) || !PyList_Check(a1))
        {
          sipIsErr = 1;
          return NULL;
        }
        else if (PyList_GET_SIZE(a0) != 6 || PyList_GET_SIZE(a1) != 6)
        {
          printf("Argument not Correct\n");
          return NULL;
        }
        else
        {
            Py_BEGIN_ALLOW_THREADS

            int i,j;
            for (i=0; i<6; ++i)
            {
              x[i] = PyFloat_AsDouble(PyList_GetItem(a0,i));
              PyObject * row = PyList_GetItem(a1,i);
              for (j=0; j<6; ++j)
                M[i][j]=PyFloat_AsDouble(PyList_GetItem(row,j));
            }

            Cell_fPass_M(x, M, ilast);

            lastpos = PyLong_FromLong(ilast);

            for (i=0; i<6; ++i)
            {
              PyList_SetItem(a0,i,PyFloat_FromDouble(x[i]));
              PyObject * row = PyList_GetItem(a1,i);
              for (j=0; j<6; ++j)
                PyList_SetItem(row,j,PyFloat_FromDouble(M[i][j]));
            }
            lastpos = PyLong_FromLong(ilast);

            return lastpos;

            Py_END_ALLOW_THREADS
        }
%End





// void Cell_Concat(double dP)
void Cell_Concat(SIP_PYOBJECT);
%MethodCode
        double dP;

        if(!PyNumber_Check(a0))
        {
          sipIsErr = 1;
        }
        else
        {
          dP = PyFloat_AsDouble(a0);
          Cell_Concat(dP);
        }
%End

// bool GetCOD(long imax, double eps, double dP, long &lastpos)
SIP_PYOBJECT GetCOD(SIP_PYOBJECT, SIP_PYOBJECT, SIP_PYOBJECT);
%MethodCode
        long imax, ilast;
        double eps;
        bool success;
        PyObject * Out;
        double dP;

        if((imax=PyLong_AsLong(a0))<0 || !PyNumber_Check(a1) || !PyNumber_Check(a2)) 
        {
          sipIsErr = 1;
        }
        else
        {
          eps = PyFloat_AsDouble(a1);
          dP = PyFloat_AsDouble(a2);
          success=GetCOD(imax, eps, dP, ilast);
	  if (!success) ilast = -1;
          Out = PyLong_FromLong(ilast);
          return Out;
        } 
%End    



// void Ring_Fittune(Vector2 &nu, double eps, iVector2 &nq, long qf[], long qd[], double dkL, long imax)

void Ring_Fittune(SIP_PYOBJECT, SIP_PYOBJECT, SIP_PYOBJECT, SIP_PYOBJECT, SIP_PYOBJECT, SIP_PYOBJECT, SIP_PYOBJECT);
%MethodCode
	Vector2 nu;
	double eps;
	iVector2 nq;
	double dkL;
	long imax, i0;
        int i;


        if (!PyList_Check(a0) || !PyNumber_Check(a1) || !PyList_Check(a2) || !PyList_Check(a3) || !PyList_Check(a4) || !PyNumber_Check(a5) || (i0=PyLong_AsLong(a6))<0 )
        {
          sipIsErr = 1;
          return NULL;
        }
        else
        {
           Py_BEGIN_ALLOW_THREADS

	   for(i=0; i<2; i++)
	   {
	     nu[i] = PyFloat_AsDouble(PyList_GetItem(a0,i));
	     nq[i] = PyLong_AsLong(PyList_GetItem(a2,i));
	   }

	   int nqf = nq[0];
	   int nqd = nq[1];

	   eps = PyFloat_AsDouble(a1);

           long qf[nqf];
	   long qd[nqd];

	   for (i=0; i<nqf; ++i)
               qf[i] = PyLong_AsLong(PyList_GetItem(a3,i));

	   for (i=0; i<nqd; ++i)
               qd[i] = PyLong_AsLong(PyList_GetItem(a4,i));

            dkL = PyFloat_AsDouble(a5);
	    imax = PyLong_AsLong(a6);
            
            Ring_Fittune(nu, eps, nq, qf, qd, dkL, imax);

	   for(i=0; i<2; i++)
	   {
//	     PyList_SetItem(a0,i,PyFloat_FromDouble(nu[i])); No meaning at current version. I'll ask to make output the achived tunes.
//	     PyList_SetItem(a2,i,PyLong_FromLong(nq[i]));
	   }

           Py_END_ALLOW_THREADS
 	}
%End

//void FitTune(long qf, long qd, double nux, double nuy)
void FitTune(SIP_PYOBJECT, SIP_PYOBJECT, SIP_PYOBJECT, SIP_PYOBJECT);
%MethodCode
        long qf, qd;
        double nux, nuy;

        if ((qf=PyLong_AsLong(a0))<0 || (qd=PyLong_AsLong(a1))<0 || !PyNumber_Check(a2) ||  !PyNumber_Check(a3))
        {
          sipIsErr = 1;
          return NULL;
        }
        else
        {
           Py_BEGIN_ALLOW_THREADS

           nux = PyFloat_AsDouble(a2);
           nuy = PyFloat_AsDouble(a3);
           

           FitTune(qf, qd, nux, nuy);

           Py_END_ALLOW_THREADS 
        }
%End

// void Ring_Fitchrom(Vector2 &ksi, double eps, iVector2 &ns, long sf[], long sd[], double dkpL, long imax)
void Ring_Fitchrom(SIP_PYOBJECT, SIP_PYOBJECT, SIP_PYOBJECT, SIP_PYOBJECT, SIP_PYOBJECT, SIP_PYOBJECT, SIP_PYOBJECT);
%MethodCode
	Vector2 ksi;
	double eps;
	iVector2 ns;
	double dkpL;
	long imax, i0;
	int i;

        if (!PyList_Check(a0) || !PyNumber_Check(a1) || !PyList_Check(a2) || !PyList_Check(a3) || !PyList_Check(a4) || !PyNumber_Check(a5) || (i0=PyLong_AsLong(a6))<0 )
        {
          sipIsErr = 1;
          return NULL;
        }
        else
        {
            Py_BEGIN_ALLOW_THREADS

	   for(i=0; i<2; i++)
	   {
	     ksi[i] = PyFloat_AsDouble(PyList_GetItem(a0,i));
	     ns[i] = PyLong_AsLong(PyList_GetItem(a2,i));
	   }

	   int nsf = ns[0];
	   int nsd = ns[1];

	   eps = PyFloat_AsDouble(a1);

           long sf[nsf];
	   long sd[nsd];

	   for (i=0; i<nsf; ++i)
               sf[i] = PyLong_AsLong(PyList_GetItem(a3,i));

	   for (i=0; i<nsd; ++i)
               sd[i] = PyLong_AsLong(PyList_GetItem(a4,i));

            dkpL = PyFloat_AsDouble(a5);
	    imax = PyLong_AsLong(a6);
            
            Ring_Fitchrom(ksi, eps, ns, sf, sd, dkpL, imax);

	   for(i=0; i<2; i++)
	   {
//	     PyList_SetItem(a0,i,PyFloat_FromDouble(nu[i])); No meaning at current version. I'll ask to make output the achived tunes.
//	     PyList_SetItem(a2,i,PyLong_FromLong(nq[i]));
	   }
   	   Py_END_ALLOW_THREADS
	}
%End

//void FitChrom(long sf, long sd, double ksix, double ksiy)
void FitChrom(SIP_PYOBJECT, SIP_PYOBJECT, SIP_PYOBJECT, SIP_PYOBJECT);
%MethodCode
        long sf, sd;
        double ksix, ksiy;

        if ((sf=PyLong_AsLong(a0))<0 || (sd=PyLong_AsLong(a1))<0 || !PyNumber_Check(a2) ||  !PyNumber_Check(a3))
        {
          sipIsErr = 1;
          return NULL;
        }
        else
        {
           Py_BEGIN_ALLOW_THREADS

           ksix = PyFloat_AsDouble(a2);
           ksiy = PyFloat_AsDouble(a3);
           

           FitChrom(sf, sd, ksix, ksiy);

           Py_END_ALLOW_THREADS 
        }
%End


//void Ring_FitDisp(long pos, double eta, double eps, long nq, long q[], double dkL, long imax)
void Ring_FitDisp(SIP_PYOBJECT, SIP_PYOBJECT, SIP_PYOBJECT, SIP_PYOBJECT, SIP_PYOBJECT, SIP_PYOBJECT, SIP_PYOBJECT);
%MethodCode
	long pos, imax, nq;
	double eta, eps, dkL;
        int i;
        if ((pos=PyLong_AsLong(a0))<1 || !PyNumber_Check(a1) || !PyNumber_Check(a2) || (nq=PyLong_AsLong(a3))<1 
                                                  || !PyList_Check(a4) || !PyNumber_Check(a5) || (imax=PyLong_AsLong(a6))<0 )
        {
          sipIsErr = 1;
          return NULL;
        }
        else
        {
           Py_BEGIN_ALLOW_THREADS

	   long q[nq];

	   eta = PyFloat_AsDouble(a1);
	   eps = PyFloat_AsDouble(a2);	   	   

	   for (i=0; i<nq; ++i)
               q[i] = PyLong_AsLong(PyList_GetItem(a4,i));

            dkL = PyFloat_AsDouble(a5);
	    imax = PyLong_AsLong(a6);
            
            Ring_FitDisp(pos, eta, eps, nq, q, dkL, imax);

//	   for(i=0; i<2; i++)
//	   {
//	     PyList_SetItem(a0,i,PyFloat_FromDouble(nu[i])); No meaning at current version. I'll ask to make output the achived tunes.
//	     PyList_SetItem(a2,i,PyLong_FromLong(nq[i]));
//	   }
    	   Py_END_ALLOW_THREADS
	}
%End

// void FitDisp(long q, long pos, double eta)
void FitDisp(SIP_PYOBJECT, SIP_PYOBJECT, SIP_PYOBJECT);
%MethodCode
        long q, pos;
        double eta;

        if ((q=PyLong_AsLong(a0))<0 || (pos=PyLong_AsLong(a1))<0 || !PyNumber_Check(a2))
        {
          sipIsErr = 1;
          return NULL;
        }
        else
        {
           Py_BEGIN_ALLOW_THREADS

           eta = PyFloat_AsDouble(a2);

           FitDisp(q, pos, eta);

           Py_END_ALLOW_THREADS 
        }
%End


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
    printf("Fnum:%ld is not a multipole\n", Fnum1);
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


void get_alphac();
%MethodCode
  CellType  Cell;

  getelem(globval.Cell_nLoc, &Cell);
  globval.Alphac = globval.OneTurnMat[ct_][delta_]/Cell.S;
%End


SIP_PYLIST get_alphac2();
%MethodCode
  /* Note, do not extract from M[5][4], i.e. around delta
     dependent fixed point.                                */

  const int     n_points = 5;
  const double  d_delta  = 2e-2;
  PyObject * Bs;
  Bs = PyList_New(3);

  int       i, j, n;
  long int  lastpos;
  double    delta[2*n_points+1], alphac[2*n_points+1], sigma;
  Vector    x, b;
  CellType  Cell;
 
  globval.pathlength = false;
  getelem(globval.Cell_nLoc, &Cell); n = 0;
  for (i = -n_points; i <= n_points; i++) {
    n++; delta[n-1] = i*(double)d_delta/(double)n_points;
    for (j = 0; j < nv_; j++)
      x[j] = 0.0;
    x[delta_] = delta[n-1];
    Cell_Pass(0, globval.Cell_nLoc, x, lastpos);
    alphac[n-1] = x[ct_]/Cell.S;
  }
  pol_fit(n, delta, alphac, 3, b, sigma);
//  printf("\n");
//  printf("alphac = %10.3e + %10.3e*delta + %10.3e*delta^2\n",
//         b[1], b[2], b[3]);
  for (i=0; i<3; ++i)
      PyList_SetItem(Bs,i,PyFloat_FromDouble(b[i+1]));
  return Bs;
%End

//void TraceABN(long i0, long i1, const Vector2 &alpha, const Vector2 &beta, const Vector2 &eta, const Vector2 &etap, const double dP)
void TraceABN(SIP_PYOBJECT, SIP_PYOBJECT, SIP_PYOBJECT, SIP_PYOBJECT, SIP_PYOBJECT, SIP_PYOBJECT, SIP_PYOBJECT);
%MethodCode
	long i0, i1;
	double dP;
	Vector2 alpha, beta, eta, etap;

	int i;

       if ((i0=PyLong_AsLong(a0))<1 || (i1=PyLong_AsLong(a1))<1 || !PyList_Check(a2) || !PyList_Check(a3) || !PyList_Check(a4) || !PyList_Check(a5) || !PyNumber_Check(a6)) 
        {
          sipIsErr = 1;
          return NULL;
        }
        else
        {
           Py_BEGIN_ALLOW_THREADS

	   for(i=0; i<2; ++i)
	   {
	     alpha[i] = PyFloat_AsDouble(PyList_GetItem(a2,i));
	     beta[i]  = PyFloat_AsDouble(PyList_GetItem(a3,i));
	     eta[i]   = PyFloat_AsDouble(PyList_GetItem(a4,i));
	     etap[i]  = PyFloat_AsDouble(PyList_GetItem(a5,i));	   	   
	   }
            dP = PyFloat_AsDouble(a6);
            
            TraceABN(i0, i1, alpha, beta, eta, etap, dP);

	    Py_END_ALLOW_THREADS
	}
%End

// = { 0, 0 }; // /* frequency number to look for */
//****************************************************************************/
//* void Get_NAFF(int nterm, long ndata, double T[DIM][NTURN], double *fx, double *fz, int nb_freq[2])
SIP_PYLIST Get_NAFF(SIP_PYOBJECT, SIP_PYOBJECT, SIP_PYLIST);
%MethodCode
  	double  Tab[6][NTURN];
	int     nb_freq[2];
	int nterm, ndata;
	int i,j;

        if ((nterm=(int) PyLong_AsLong(a0))<1 || (ndata=(int) PyLong_AsLong(a1))<1 || !PyList_Check(a2) )
        {
          sipIsErr = 1;
          return NULL;
        }
        else
        {
           Py_BEGIN_ALLOW_THREADS

	   double  fx[nterm], fz[nterm];

	   for (i=0;i<6;++i)
	   {
		PyObject * row = PyList_GetItem(a2,i);
		for (j=0;j<ndata;++j)
		{
		    Tab[i][j] = PyFloat_AsDouble(PyList_GetItem(row,j));
		}
	    }
	    /* initializations */
	    for (i = 0; i < nterm; i++)
	    {
	        fx[i] = 0.0; fz[i] = 0.0;
	    }
	    /* end init */
	    Get_NAFF(nterm, ndata*6, Tab, fx, fz, nb_freq);

	    PyObject * pyRet = PyList_New(3);
	    PyObject * Fx = PyList_New(nb_freq[0]);
	    PyObject * Fz = PyList_New(nb_freq[1]);
	    PyObject * Nb_Freq = PyList_New(2);

	    for (i=0; i<nb_freq[0]; ++i) PyList_SetItem(Fx, i, PyFloat_FromDouble(fx[i]));
	    for (i=0; i<nb_freq[1]; ++i) PyList_SetItem(Fz, i, PyFloat_FromDouble(fz[i]));
	    for (i=0; i<2; ++i) PyList_SetItem(Nb_Freq, i, PyLong_FromLong(nb_freq[i]));

	    PyList_SetItem(pyRet, 0, Fx);
	    PyList_SetItem(pyRet, 1, Fz);
	    PyList_SetItem(pyRet, 2, Nb_Freq);

	    return pyRet;

	    Py_END_ALLOW_THREADS
	}
%End

//* void Trac_Simple(double x, double px, double y, double py, double dp, double ctau, long nmax, double Tx[][NTURN], bool *status2)
SIP_PYLIST Trac_Simple(SIP_PYOBJECT, SIP_PYOBJECT, SIP_PYOBJECT, SIP_PYOBJECT, SIP_PYOBJECT, SIP_PYOBJECT, SIP_PYOBJECT, SIP_PYOBJECT);
%MethodCode
  	bool    status = true;
	double  Tab[6][NTURN];
	double  x, px, y, py, dp, ctau;
	long    nmax;
	int i,j;

	PyObject * pyRet;
	PyObject * pyTab; 
	PyObject * pyStatus;

        if (!PyNumber_Check(a0) || !PyNumber_Check(a1) || !PyNumber_Check(a2) || !PyNumber_Check(a3) || !PyNumber_Check(a4)
                                                                              || !PyNumber_Check(a5) || (nmax= PyLong_AsLong(a6))<1)
        {
          sipIsErr = 1;
          return NULL;
        }
        else
        {
           Py_BEGIN_ALLOW_THREADS

	   x = PyFloat_AsDouble(a0);  px = PyFloat_AsDouble(a1);
	   y = PyFloat_AsDouble(a2);  py = PyFloat_AsDouble(a3);
	   dp = PyFloat_AsDouble(a4);  ctau = PyFloat_AsDouble(a5);

	   Trac_Simple(x,px, y, py, dp,ctau, nmax, Tab, &status);

	   if (status) pyStatus = Py_True;
	   else pyStatus = Py_False;

	   pyTab = PyList_New(6);

	   for (i=0;i<6;++i)
	   {
		PyObject * row = PyList_New(nmax);
		for (j=0;j<nmax;++j)
		{
		   PyList_SetItem(row,j,PyFloat_FromDouble(Tab[i][j]));
		}
		PyList_SetItem(pyTab,i,row);
	    }

	    pyRet = PyList_New(2);
	    
	    PyList_SetItem(pyRet, 0, pyStatus);
	    PyList_SetItem(pyRet, 1, pyTab);

	    return pyRet;

	    Py_END_ALLOW_THREADS
	}
%End



// void GetChromTrac(long Nb, long Nbtour, double emax, double *xix, double *xiz)
SIP_PYLIST GetChromTrac(SIP_PYOBJECT, SIP_PYOBJECT, SIP_PYOBJECT, SIP_PYOBJECT);
%MethodCode
	long    Nb, Nbtour;
        double  emax, xix, xiz;

        if ((Nb = PyLong_AsLong(a0))<1 || (Nbtour = PyLong_AsLong(a1))<1 || !PyNumber_Check(a2) )
        {
          sipIsErr = 1;
          return NULL;
        }
        else
        {
            Py_BEGIN_ALLOW_THREADS

	    emax = PyFloat_AsDouble(a2);

	   
	    GetChromTrac(Nb, Nbtour, emax, &xix, &xiz);

	    PyObject * pyRet = PyList_New(2);

	    PyList_SetItem(pyRet, 0, PyFloat_FromDouble(xix));
	    PyList_SetItem(pyRet, 1, PyFloat_FromDouble(xiz));

	    return pyRet;

	    Py_END_ALLOW_THREADS
	}
%End


// void track(const char *file_name, double ic1, double ic2, double ic3, double ic4, double dp,
//           long int nmax, long int &lastn, long int &lastpos, int floqs, double f_rf)
//{
//  /* Single particle tracking around closed orbit:
//
//          Output                floqs
//
//        Phase Space               0     [x, px, y, py, delta, ct]
//        Floquet Space             1     [x^, px^, y^, py^, delta, ct]
//        Action-Angle Variables    2     [2Jx, phx, 2Jy, phiy, delta, ct]
//
//  */
SIP_PYLIST track(SIP_PYOBJECT, SIP_PYOBJECT, SIP_PYOBJECT, SIP_PYOBJECT, SIP_PYOBJECT, SIP_PYOBJECT, SIP_PYOBJECT, SIP_PYOBJECT, SIP_PYOBJECT);
%MethodCode
	long int  lastpos, lastn;
	double    ic1, ic2, ic3, ic4, dp, f_rf;
	long nmax, floqs;

        if (!PyString_Check(a0) || !PyNumber_Check(a1)|| !PyNumber_Check(a2)|| !PyNumber_Check(a3)|| !PyNumber_Check(a4)|| !PyNumber_Check(a5) 
                                                      || (nmax = PyLong_AsLong(a6))<1 || (floqs = PyLong_AsLong(a7))<0 || !PyNumber_Check(a8) )
        {
          sipIsErr = 1;
          return NULL;
        }
        else
        {
            Py_BEGIN_ALLOW_THREADS

	    const char   *file_name = PyString_AsString(a0);

	    ic1 = PyFloat_AsDouble(a1);
	    ic2 = PyFloat_AsDouble(a2);
	    ic3 = PyFloat_AsDouble(a3);
	    ic4 = PyFloat_AsDouble(a4);

	    dp  = PyFloat_AsDouble(a5);

	    f_rf= PyFloat_AsDouble(a8);
	   
	    track(file_name, ic1, ic2, ic3, ic4, dp, nmax, lastn, lastpos, floqs, f_rf);

	    PyObject * PyRet = PyList_New(2);

	    PyList_SetItem(PyRet, 0, PyLong_FromLong(lastn));
	    PyList_SetItem(PyRet, 1, PyLong_FromLong(lastpos));

	    return PyRet;

	    Py_END_ALLOW_THREADS
	}
%End

// void getfloqs(Vector &x)
SIP_PYLIST track(SIP_PYLIST);
%MethodCode
	int       i;
	Vector x;

        if (!PyList_Check(a0) )
        {
          sipIsErr = 1;
          return NULL;
        }
        else
        {
            Py_BEGIN_ALLOW_THREADS

	   for (i=0;i<6;++i)
	   {
		x[i] = PyFloat_AsDouble(PyList_GetItem(a0,i));
	   }

	   getfloqs(x);

	   PyObject * pyRet = PyList_New(6); 

	   for (i=0;i<6;++i)
	   {
		PyList_SetItem(pyRet,i, PyFloat_FromDouble(x[i]));
	    }

	    return pyRet;

	    Py_END_ALLOW_THREADS
	}
%End


// void GetTrack(const char *file_name, long *n, double x[], double px[], double y[], double py[])
SIP_PYLIST GetTrack(SIP_PYOBJECT, SIP_PYOBJECT);
%MethodCode
	int       i;
	long 	  n;
	long nbuff;


        if (!PyString_Check(a0) || (nbuff = PyLong_AsLong(a1))<1)
        {
          sipIsErr = 1;
          return NULL;
        }
        else
        {
            Py_BEGIN_ALLOW_THREADS

	   const char   *file_name = PyString_AsString(a0);
	   const int  n_turn = nbuff;
	   double    x[n_turn], px[n_turn], y[n_turn], py[n_turn];


	   GetTrack(file_name, &n, x, px, y, py);

	   PyObject * pyRet = PyList_New(4);

	   PyObject * pyX  = PyList_New(n);
	   PyObject * pyPx = PyList_New(n);
	   PyObject * pyY  = PyList_New(n);
	   PyObject * pyPy = PyList_New(n);

	   for (i=0;i<n;++i)
	   {
		PyList_SetItem(pyX, i, PyFloat_FromDouble(x[i]));
		PyList_SetItem(pyPx,i, PyFloat_FromDouble(px[i]));
		PyList_SetItem(pyY, i, PyFloat_FromDouble(y[i]));
		PyList_SetItem(pyPy,i, PyFloat_FromDouble(py[i]));
	   }

	   PyList_SetItem(pyRet,0, pyX);
	   PyList_SetItem(pyRet,1, pyPx);
	   PyList_SetItem(pyRet,2, pyY);
	   PyList_SetItem(pyRet,3, pyPy);

	   return pyRet;

	   Py_END_ALLOW_THREADS
	}
%End

// void getdynap(double &r, double phi, double delta, double eps, int nturn, bool floqs)
SIP_PYOBJECT getdynap(SIP_PYOBJECT, SIP_PYOBJECT, SIP_PYOBJECT, SIP_PYOBJECT, SIP_PYOBJECT, SIP_PYOBJECT);
%MethodCode
	double r, phi, delta, eps;
	long nturn;
	bool floqs=false;


        if ( !PyNumber_Check(a0)|| !PyNumber_Check(a1)|| !PyNumber_Check(a2)|| !PyNumber_Check(a3)|| (nturn = PyLong_AsLong(a4))<1 || !PyBool_Check(a5) )
        {
            sipIsErr = 1;
            return NULL;
        }
        else
        {
            Py_BEGIN_ALLOW_THREADS

	    r     = PyFloat_AsDouble(a0);
	    phi   = PyFloat_AsDouble(a1);
	    delta = PyFloat_AsDouble(a2);
	    eps   = PyFloat_AsDouble(a3);
	    if (a5 == Py_True) floqs = true;
	   

	    getdynap(r, phi, delta, eps, nturn, floqs);

	    PyObject * pyRet = PyFloat_FromDouble(r);

	    return pyRet;

	    Py_END_ALLOW_THREADS
	}
%End

// void misalign_rms_elem(const int Fnum, const int Knum, const double dx_rms, const double dy_rms, const double dr_rms, const bool new_rnd)
void misalign_rms_elem(SIP_PYOBJECT, SIP_PYOBJECT, SIP_PYOBJECT, SIP_PYOBJECT, SIP_PYOBJECT, SIP_PYOBJECT);
%MethodCode
	double dx_rms, dy_rms, dr_rms;
	long Fnum, Knum;
	bool new_rnd=false;

        if ( (Fnum = PyLong_AsLong(a0))<1 || (Knum = PyLong_AsLong(a1))<1|| !PyNumber_Check(a2)|| !PyNumber_Check(a3)|| !PyNumber_Check(a4) || !PyBool_Check(a5) )
        {
            sipIsErr = 1;
        }
        else
        {
            Py_BEGIN_ALLOW_THREADS

	    dx_rms = PyFloat_AsDouble(a2);
	    dy_rms = PyFloat_AsDouble(a3);
	    dr_rms = PyFloat_AsDouble(a4);

	    if (a5 == Py_True) new_rnd = true;
	   
	    misalign_rms_elem(Fnum, Knum, dx_rms, dy_rms, dr_rms, new_rnd);

	    Py_END_ALLOW_THREADS
	}
%End

// void misalign_sys_elem(const int Fnum, const int Knum, const double dx_sys, const double dy_sys, const double dr_sys)
void misalign_sys_elem(SIP_PYOBJECT, SIP_PYOBJECT, SIP_PYOBJECT, SIP_PYOBJECT, SIP_PYOBJECT);
%MethodCode
	double dx_sys, dy_sys, dr_sys;
	long Fnum, Knum;

        if ( (Fnum = PyLong_AsLong(a0))<1 || (Knum = PyLong_AsLong(a1))<1|| !PyNumber_Check(a2)|| !PyNumber_Check(a3)|| !PyNumber_Check(a4) )
        {
            sipIsErr = 1;
        }
        else
        {
            Py_BEGIN_ALLOW_THREADS

	    dx_sys = PyFloat_AsDouble(a2);
	    dy_sys = PyFloat_AsDouble(a3);
	    dr_sys = PyFloat_AsDouble(a4);
	   
	    misalign_sys_elem(Fnum, Knum, dx_sys, dy_sys, dr_sys);

	    Py_END_ALLOW_THREADS
	}
%End

// void misalign_rms_fam(const int Fnum, const double dx_rms, const double dy_rms, const double dr_rms, const bool new_rnd)
void misalign_rms_fam(SIP_PYOBJECT, SIP_PYOBJECT, SIP_PYOBJECT, SIP_PYOBJECT, SIP_PYOBJECT);
%MethodCode
	double dx_rms, dy_rms, dr_rms;
	long Fnum;
	bool new_rnd;

        if ( (Fnum = PyLong_AsLong(a0))<1  || !PyNumber_Check(a1)|| !PyNumber_Check(a2)|| !PyNumber_Check(a3) || !PyBool_Check(a4) )
        {
            sipIsErr = 1;
        }
        else
        {
            Py_BEGIN_ALLOW_THREADS

	    dx_rms = PyFloat_AsDouble(a1);
	    dy_rms = PyFloat_AsDouble(a2);
	    dr_rms = PyFloat_AsDouble(a3);

	    if (a4 == Py_True) new_rnd = true;
	   
	    misalign_rms_fam(Fnum, dx_rms, dy_rms, dr_rms, new_rnd);

	    Py_END_ALLOW_THREADS
	}
%End

//void misalign_sys_fam(const int Fnum, const double dx_sys, const double dy_sys, const double dr_sys)
void misalign_sys_fam(SIP_PYOBJECT, SIP_PYOBJECT, SIP_PYOBJECT, SIP_PYOBJECT);
%MethodCode
	double dx_sys, dy_sys, dr_sys;
	long Fnum;

        if ( (Fnum = PyLong_AsLong(a0))<1 || !PyNumber_Check(a1)|| !PyNumber_Check(a2)|| !PyNumber_Check(a3) )
        {
            sipIsErr = 1;
        }
        else
        {
            Py_BEGIN_ALLOW_THREADS

	    dx_sys = PyFloat_AsDouble(a1);
	    dy_sys = PyFloat_AsDouble(a2);
	    dr_sys = PyFloat_AsDouble(a3);
	   
	    misalign_sys_fam(Fnum, dx_sys, dy_sys, dr_sys);

	    Py_END_ALLOW_THREADS
	}
%End

// void misalign_rms_type(const int type, const double dx_rms, const double dy_rms, const double dr_rms, const bool new_rnd)
void misalign_rms_type(SIP_PYOBJECT, SIP_PYOBJECT, SIP_PYOBJECT, SIP_PYOBJECT, SIP_PYOBJECT);
%MethodCode
	double dx_rms, dy_rms, dr_rms;
	long type;
	bool new_rnd;

        if ( (type = PyLong_AsLong(a0))<1 || !PyNumber_Check(a1)|| !PyNumber_Check(a2)|| !PyNumber_Check(a3) || !PyBool_Check(a4) )
        {
            sipIsErr = 1;
        }
        else
        {
            Py_BEGIN_ALLOW_THREADS

	    dx_rms = PyFloat_AsDouble(a1);
	    dy_rms = PyFloat_AsDouble(a2);
	    dr_rms = PyFloat_AsDouble(a3);

	    if (a4 == Py_True) new_rnd = true;
	   
	    misalign_rms_type(type, dx_rms, dy_rms, dr_rms, new_rnd);

	    Py_END_ALLOW_THREADS
	}
%End

// void misalign_sys_type(const int type, const double dx_sys, const double dy_sys, const double dr_sys)
void misalign_sys_type(SIP_PYOBJECT, SIP_PYOBJECT, SIP_PYOBJECT, SIP_PYOBJECT);
%MethodCode
	double dx_sys, dy_sys, dr_sys;
	long type;

        if ( (type = PyLong_AsLong(a0))<1 || !PyNumber_Check(a1)|| !PyNumber_Check(a2)|| !PyNumber_Check(a3) )
        {
            sipIsErr = 1;
        }
        else
        {
            Py_BEGIN_ALLOW_THREADS

	    dx_sys = PyFloat_AsDouble(a1);
	    dy_sys = PyFloat_AsDouble(a2);
	    dr_sys = PyFloat_AsDouble(a3);
	   
	    misalign_sys_type(type, dx_sys, dy_sys, dr_sys);

	    Py_END_ALLOW_THREADS
	}
%End

// ======================= Not yet documented
SIP_PYLIST getSextList();
%MethodCode

        PyObject * list;

        if ((list = PyList_New(0)))
        {
            Py_BEGIN_ALLOW_THREADS
            for (int i=0 ; i<=globval.Cell_nLoc ;i++)
            {
	      if (Cell[i].Elem.Pkind == Mpole && Cell[i].Elem.M->n_design==Sext)
                PyList_Append(list, PyLong_FromLong(i));
            }
            Py_END_ALLOW_THREADS
            return list;
        }
        else
        {
            // PyList_New() will have raised the exception.
            sipIsErr = 1;
            return NULL;
        }
%End

//SIP_PYLIST findM44(SIP_PYOBJECT);
//%MethodCode
//
//	PyObject * 435;
 //   % optimal differentiation step - Numerical Recipes
//	double d = 6.055454452393343e-006;
//	if (PyList_Check(a0))
//	{
	    


SIP_PYLIST findM44_M(SIP_PYOBJECT);
%MethodCode
// Replce them by Elem_Pass_M ? No because Cell[i].BeamPos changed but Insertion_Pass_M should be added
	Matrix mat;
	UnitMat(4, mat);
	int i, j, k;

	PyObject * ret;

	if (PyLong_Check(a0))
	{
	    long elem = PyLong_AsLong(a0);
	    if (elem < 1 || elem > globval.Cell_nLoc) return NULL;
	    else
	    {
		ret = PyList_New(4);
		for (i=0; i<3; ++i)
		{
		    PyObject * row = PyList_New(4);
		    for (j=0; j<3; ++j)
		    {
	    		if (Cell[elem].Elem.Pkind == drift)
			    PyList_SetItem(row, j, PyFloat_FromDouble(Cell[elem].Elem.D->D55[i][j]));
	    		else if (Cell[elem].Elem.Pkind == Wigl)
			    PyList_SetItem(row, j, PyFloat_FromDouble(Cell[elem].Elem.W->W55[i][j]));
	    		else if (Cell[elem].Elem.Pkind == Mpole)
			{
			    MulLMat(4,Cell[i].Elem.M->AU55, mat);
			    MulLMat(4,Cell[i].Elem.M->AD55, mat);
			    PyList_SetItem(row, j, PyFloat_FromDouble(mat[i][j]));
			}
			else
			    PyList_SetItem(row, j, PyFloat_FromDouble(mat[i][j]));
		    }
		    PyList_SetItem(ret, i, row);
		}
		return ret;
	    }
	}
	else if (PyList_Check(a0))
	{
	    long nSize = PyList_Size(a0);
	    ret = PyList_New(nSize-1);
	    
	    for (i=0; i<nSize-1; ++i)
	    {
		long i0 = PyLong_AsLong(PyList_GetItem(a0,i));
		long i1 = PyLong_AsLong(PyList_GetItem(a0,i+1));
		if (i1 > i0)
		{
		    PyObject * trmat = PyList_New(4);
		    for (j=i0; j<=i1; j++)
		    {
	    		if (Cell[i].Elem.Pkind == drift)
			    MulLMat(4,Cell[i].Elem.D->D55,mat);
	    		else if (Cell[i].Elem.Pkind == Wigl)
			    MulLMat(4,Cell[i].Elem.W->W55,mat);
	    		else if (Cell[i].Elem.Pkind == Mpole)
			{
			    MulLMat(4,Cell[i].Elem.M->AU55, mat);
			    MulLMat(4,Cell[i].Elem.M->AD55, mat);
			}
		    }
		    for (k=0; k<4; ++i)
		    {
		        PyObject * row = PyList_New(4);
		        for (j=0; j<4; ++j)
		        {
			   PyList_SetItem(row, j, PyFloat_FromDouble(mat[k][j]));
		        }
			PyList_SetItem(trmat, k, row);
		    }
		    PyList_SetItem(ret, i, trmat);
		}
		else
		{
		    PyObject * trmat = PyList_New(4);
		    for (j=i0; j<=globval.Cell_nLoc; j++)
		    {
	    		if (Cell[i].Elem.Pkind == drift)
			    MulLMat(4,Cell[i].Elem.D->D55,mat);
	    		else if (Cell[i].Elem.Pkind == Wigl)
			    MulLMat(4,Cell[i].Elem.W->W55,mat);
	    		else if (Cell[i].Elem.Pkind == Mpole)
			{
			    MulLMat(4,Cell[i].Elem.M->AU55, mat);
			    MulLMat(4,Cell[i].Elem.M->AD55, mat);
			}
		    }
		    for (j=1; j<=i1; j++)
		    {
	    		if (Cell[i].Elem.Pkind == drift)
			    MulLMat(4,Cell[i].Elem.D->D55,mat);
	    		else if (Cell[i].Elem.Pkind == Wigl)
			    MulLMat(4,Cell[i].Elem.W->W55,mat);
	    		else if (Cell[i].Elem.Pkind == Mpole)
			{
			    MulLMat(4,Cell[i].Elem.M->AU55, mat);
			    MulLMat(4,Cell[i].Elem.M->AD55, mat);
			}
		    }
		    for (k=0; k<4; ++i)
		    {
		        PyObject * row = PyList_New(4);
		        for (j=0; j<4; ++j)
		        {
			    PyList_SetItem(row, j, PyFloat_FromDouble(mat[k][j]));
		        }
			PyList_SetItem(trmat, k, row);
		    }
		    PyList_SetItem(ret, i, trmat);
		} // if i0 < i1
	    } // for i
	    return ret;
	} // if list

%End


// void Elem_Pass(const long i, ss_vect<T> &x)
SIP_PYOBJECT Elem_Pass(SIP_PYOBJECT, SIP_PYOBJECT);
%MethodCode
	int elem;
	ss_vect<double> x;
	PyObject * ret;
	int i;
	
        if ((elem=PyLong_AsLong(a0)) < 1 || !PyList_Check(a1) )
        {
            sipIsErr = 1;
        }
        else
        {
            Py_BEGIN_ALLOW_THREADS

	    for (i=0; i<6; i++)  x[i] = PyFloat_AsDouble(PyList_GetItem(a1,i));
	   
	    Elem_Pass(elem, x);

	    ret = PyList_New(6);

	    for (i=0; i<6; i++)  PyList_SetItem(ret, i, PyFloat_FromDouble(x[i]));

	    return ret;

	    Py_END_ALLOW_THREADS
	}
%End

SIP_PYLIST findM44(SIP_PYOBJECT, SIP_PYOBJECT);
%MethodCode
	ss_vect<double> x0, x11, x12, x21, x22, x31, x32, x41, x42;
	double dp  = 6.055454452393343e-006;
	PyObject * ret;
	int i,j,k;
	
        if ( !(PyList_Check(a0)) || !PyList_Check(a1) )
        {
            sipIsErr = 1;
        }
        else
        {
            Py_BEGIN_ALLOW_THREADS

	    for (i=0; i<4; i++)  
	    {
		x0[i] = PyFloat_AsDouble(PyList_GetItem(a1,i));
		x11[i] = x0[i]; x12[i] = x0[i];
		x21[i] = x0[i]; x22[i] = x0[i];
		x31[i] = x0[i]; x32[i] = x0[i];
		x41[i] = x0[i]; x42[i] = x0[i];
	    }
	    x11[4]=0; x12[4]=0; x11[5]=0; x12[5]=0;
	    x21[4]=0; x22[4]=0; x21[5]=0; x22[5]=0;
	    x31[4]=0; x32[4]=0; x31[5]=0; x32[5]=0;
	    x41[4]=0; x42[4]=0; x41[5]=0; x42[5]=0;

	    x11[0] -= dp; x12[0] += dp;
	    x21[1] -= dp; x22[1] += dp;
	    x31[2] -= dp; x32[2] += dp;
	    x41[3] -= dp; x42[3] += dp;

	    long nSize = PyList_Size(a0);
	    ret = PyList_New(nSize-1);
	    
	    for (i=0; i<nSize-1; ++i)
	    {
		long i0 = PyLong_AsLong(PyList_GetItem(a0,i));
		long i1 = PyLong_AsLong(PyList_GetItem(a0,i+1));
		PyObject * trmat = PyList_New(4);
		PyObject * rows[4];
		for (k=0; k<4; ++k) rows[k] = PyList_New(4);
		if (i1 > i0)
		{
		    for (j=i0; j<=i1; j++)
		    {
	    		Elem_Pass(j, x11);Elem_Pass(j, x12);
	    		Elem_Pass(j, x21);Elem_Pass(j, x22);
	    		Elem_Pass(j, x31);Elem_Pass(j, x32);
	    		Elem_Pass(j, x41);Elem_Pass(j, x42);
		    }

		}
		else
		{
		    for (j=i0; j<=globval.Cell_nLoc; j++)
		    {
	    		Elem_Pass(j, x11);Elem_Pass(j, x12);
	    		Elem_Pass(j, x21);Elem_Pass(j, x22);
	    		Elem_Pass(j, x31);Elem_Pass(j, x32);
	    		Elem_Pass(j, x41);Elem_Pass(j, x42);
		    }
		    for (j=1; j<=i1; j++)
		    {
	    		Elem_Pass(j, x11);Elem_Pass(j, x12);
	    		Elem_Pass(j, x21);Elem_Pass(j, x22);
	    		Elem_Pass(j, x31);Elem_Pass(j, x32);
	    		Elem_Pass(j, x41);Elem_Pass(j, x42);
		    }
		} // if i0 < i1
		for (k=0; k<4; ++k)
		{
		    PyList_SetItem(rows[k], 0, PyFloat_FromDouble((x12[k]-x11[k])/(2.0*dp)));
		    PyList_SetItem(rows[k], 1, PyFloat_FromDouble((x22[k]-x21[k])/(2.0*dp)));
		    PyList_SetItem(rows[k], 2, PyFloat_FromDouble((x32[k]-x31[k])/(2.0*dp)));
		    PyList_SetItem(rows[k], 3, PyFloat_FromDouble((x42[k]-x41[k])/(2.0*dp)));
		}

		for (k=0; k<4; ++k) PyList_SetItem(trmat, k, rows[k]);

		PyList_SetItem(ret, i, trmat);

	    } // for i
	    return ret;

	    Py_END_ALLOW_THREADS
	}
%End





