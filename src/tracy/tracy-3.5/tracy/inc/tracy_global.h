#define PLANES 2
#define n_harm_max 10
#define i_max_FM   100
#define j_max_FM   100
#define k_max_FM   1000
#define FMT_Dim    3
#define nKidMax    1000

struct globvalrec {
    double        dPcommon;       // dp for numerical differentiation 
    double        dPparticle;     // energy deviation 
    double        delta_RF;       // RF acceptance 
    Vector2       TotalTune;      // transverse tunes 
    double        Omega;
    double        U0;             // energy lost per turn in keV 
    double        Alphac;         // alphap 
    Vector2       Chrom;          // chromaticities 
    double        Energy;         // ring energy 
    long          Cell_nLoc;      // number of elements 
    long          Elem_nFam;      // number of families 
    long          CODimax;        /* maximum number of cod search before failing */
    double        CODeps;         // precision for closed orbit finder
    Vector        CODvect;        // closed orbit
    int           bpm;            // bpm number 
    int           hcorr;          // horizontal corrector number 
    int           vcorr;          // vertical corrector number 
    int           qt;             // vertical corrector number 
    int           gs;             // girder start marker 
    int           ge;             // girder end marker 
    Matrix        OneTurnMat;     // oneturn matrix 
    Matrix        Ascr;
    Matrix        Ascrinv;
    Matrix        Vr;             // real part of the eigenvectors 
    Matrix        Vi;             // imaginal par of the eigenvectors 

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
    double        alpha_rad[DOF]; // damping coeffs.
    double        D_rad[DOF];     // diffusion coeffs (Floquet space)
    double        J[DOF];         // partition numbers
    double        tau[DOF];       // damping times
    bool          IBS;            // intrabeam scattering
    double        Qb;             // bunch charge
    double        D_IBS[DOF];     // diffusion matrix (Floquet space)
    Vector        wr;
    Vector        wi;         // real and imaginary part of eigenvalues
    Vector3       eps;            // 3 motion invariants
    Vector3       epsp;           /* transverse and longitudinal projected emittances */
    int           RingType;       // 1 if a ring (0 if transfer line)
};


struct DriftType {
    Matrix D55; // Linear matrix
};


struct MpoleType {
    int         Pmethod;   // Integration Method
    int         PN;        // Number of integration steps
    // Displacement Errors
    Vector2     PdSsys;    // systematic [m] 
    Vector2     PdSrms;    // rms [m]
    Vector2     PdSrnd;    // random number
    // Roll angle
    double      PdTpar;    // design [deg]
    double      PdTsys;    // systematic [deg]
    double      PdTrms;    // rms [deg]
    double      PdTrnd;    // random number
    // Multipole strengths
    mpolArray   PBpar;     // design
    mpolArray   PBsys;     // systematic
    mpolArray   PBrms;     // rms
    mpolArray   PBrnd;     // random number
    mpolArray   PB;        // total
    int         Porder;    // The highest order in PB
    int         n_design;  // multipole order (design)
    pthicktype  Pthick;
    // Bending Angles
    double      PTx1;      // horizontal entrance angle [deg]
    double      PTx2;      // horizontal exit angle [deg]
    double      Pgap;      // total magnet gap [m] 
    double      Pirho;     // 1/rho [1/m] 
    double      Pc0;
    double      Pc1;
    double      Ps1;       // corrections for roll error of bend 
    Matrix      AU55;      // Upstream 5x5 matrix 
    Matrix      AD55;      // Downstream 5x5 matrix 
};

struct WigglerType {
    int Pmethod;                // Integration Method 
    int PN;                     // number of integration steps 
    // Displacement Error 
    Vector2 PdSsys;             // systematic [m]  
    Vector2 PdSrms;             // rms [m] 
    Vector2 PdSrnd;             // random number 
    // Roll angle 
    double PdTpar;              // design [deg] 
    double PdTsys;              // systematic [deg] 
    double PdTrms;              // rms [deg] 
    double PdTrnd;              // random number 
    double lambda;              // lambda 
    int    n_harm;              // no of harmonics
    int    harm[n_harm_max];    // harmonic number
    double BoBrhoV[n_harm_max]; // B/Brho vertical
    double BoBrhoH[n_harm_max]; // B/Brho horizontal 
    double kxV[n_harm_max];     // kx 
    double kxH[n_harm_max];     // kx 
    double phi[n_harm_max];     // phi 
    mpolArray PBW;
    Matrix W55;                 // Transport matrix 
    int Porder;                 // The highest order in PB 
};

struct FieldMapType {
    int     n_step; // number of integration steps
    int     n[FMT_Dim];                                         // no of steps
    double  scl;
    double  xyz[FMT_Dim][i_max_FM][j_max_FM][k_max_FM];         // [x, y, z]
    double  B[FMT_Dim][i_max_FM][j_max_FM][k_max_FM];           // [B_x, B_y, B_z]
    double  **AxoBrho;
    double  **AxoBrho2;
    double  **AyoBrho;
    double  **AyoBrho2; // Ax(y, s), Ay(x, s)
};


/* ID Laurent */
#define IDXMAX 200
#define IDZMAX 100
#define FN_Len 100

struct InsertionType {
    int    Pmethod;         /* Integration Method */
    int    PN;              /* number of integration steps */
    char   fname1[FN_Len];  /* Filename for insertion description: first ordre */
    char   fname2[FN_Len];  /* Filename for insertion description: second ordre */
    int    nx;              /* Horizontal point number */
    int    nz;              /* Vertical point number */
    double scaling;         /* static scaling factor as in BETA ESRF*/
    bool   linear;          /* if true linear interpolation else spline */
    bool   firstorder;      /* true if first order kick map loaded */
    bool   secondorder;     /* true if second order kick map loaded */
    double tabx[IDXMAX];    /* spacing in H-plane */
    double tabz[IDZMAX];    /* spacing in V-plane */
    double thetax[IDZMAX][IDXMAX];
    double thetax1[IDZMAX][IDXMAX]; /* 1 for 1st order */
    double thetaz[IDZMAX][IDXMAX];
    double thetaz1[IDZMAX][IDXMAX];
    double **tx;
    double **tz;
    double **f2x;
    double **f2z;
    double **tx1;
    double **tz1;
    double **f2x1;
    double **f2z1; // a voir
    double *tab1;
    double *tab2; // tab of x and z meshes from Radia code
  
    /* Displacement Error */
    Vector2 PdSsys;   /* systematic [m]  */
    Vector2 PdSrms;   /* rms [m] */
    Vector2 PdSrnd;   /* random number */
    /* Roll angle */
    double PdTpar;    /* design [deg] */
    double PdTsys;    /* systematic [deg] */
    double PdTrms;    /* rms [deg] */
    double PdTrnd;    /* random number */
    //  /* Strength */
    //  double Plperiod;  /* Length Period [m] */
    //  int Pnperiod;    /* Number of periods */
    //  double PBoBrho;   /* B/Brho */
    //  double PKx;       /* kx */
    //  mpolArray PBW;
    Matrix K55;        /* Transport matrix:kick part */
    Matrix D55;        /* Transport matrix:drift part */
    Matrix KD55;       /* Transport matrix:concatenation of kicks and drifts */
    int Porder;        /* The highest order in PB */
};

struct CavityType {
    double Pvolt;   // Vrf [V]
    double Pfreq;   // Vrf [Hz]
    double phi;     // RF phase
    int    Ph;      // Harmonic number
};

#define  Spreader_max 10

struct SpreaderType {
    double    E_max[Spreader_max];      // energy levels in increasing order
    CellType  *Cell_ptrs[Spreader_max];
};

struct RecombinerType {
    double    E_min;
    double    E_max;
};

struct SolenoidType {
    int         N;         // Number of integration steps
    // Displacement Errors
    Vector2     PdSsys;    // systematic [m] 
    Vector2     PdSrms;    // rms [m]
    Vector2     PdSrnd;    // random number
    // Roll angle
    double      dTpar;     // design [deg]
    double      dTsys;     // systematic [deg]
    double      dTrms;     // rms [deg]
    double      dTrnd;     // random number
    double      BoBrho;    // normalized field strength
};

struct elemtype {
    partsName PName;   /* Element name */
    double PL;         /* Length[m]    */
    PartsKind Pkind;   /* Enumeration  for magnet types */
    //union
    //{
	DriftType      *D;   // Drift
	MpoleType      *M;   // Multipole
	WigglerType    *W;   // Wiggler
	FieldMapType   *FM;  // Field Map
	InsertionType  *ID;  // Insertion
	CavityType     *C;   // Cavity
	SpreaderType   *Spr; // Spreader
	RecombinerType *Rec; // Recombiner
	SolenoidType   *Sol; // Solenoid
    //};
};

struct ElemFamType {
    elemtype    ElemF;    /* Structure (name, type) */
    int         nKid;         /* Kid number */
    int         KidList[nKidMax];
    int         NoDBN;
    DBNameType  DBNlist[nKidMax];
};

// LEGO block structure for each element of the lattice
struct CellType {
    int              Fnum;        // Element Family #
    int              Knum;        // Element Kid #
    double           S;           // Position in the ring
    //CellType*        next_ptr;    // pointer to next cell (for tracking)
    Vector2          dS;          // Transverse displacement
    Vector2          dT;          // dT = (cos(dT), sin(dT))
    elemtype         Elem;        // Structure (name, type)
    Vector2          Nu;          // Phase advances 
    Vector2          Alpha;       // Alpha functions (redundant)
    Vector2          Beta;        // beta fonctions (redundant)
    Vector2          Eta;
    Vector2          Etap;        // dispersion and its derivative (redundant)
    Vector           BeamPos;     // Last position of the beam this cell
    Matrix           A;           // Floquet space to phase space transformation
    Matrix           sigma;       // sigma matrix (redundant)
    Vector2          maxampl[PLANES]; // Horizontal and vertical physical apertures:
				      //   maxampl[X_][0] < x < maxampl[X_][1]
				      //   maxampl[Y_][0] < y < maxampl[Y_][1]
};
