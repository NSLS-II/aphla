/* Tracy-2

   J. Bengtsson, CBP, LBL      1990 - 1994   Pascal version
                 SLS, PSI      1995 - 1997
   M. Boege      SLS, PSI      1998          C translation
   L. Nadolski   SOLEIL        2002          Link to NAFF, Radia field maps
   J. Bengtsson  NSLS-II, BNL  2004 -        

*/


bool    first_h = true, first_v = true;
int     m, n[2];
double  *w_lsoc[2], **A_lsoc[2], **U_lsoc[2], **V_lsoc[2];


void prt_gcmat(int bpm, int corr, int plane)
{
  int     i, j;
  FILE    *outf = NULL;

  printf("bpm = %d, corr = %d, plane = %d\n", bpm, corr, plane);

  if (plane == 1)
    outf = file_write("svdh.out");
  else if (plane == 2)
    outf = file_write("svdv.out");
  else {
    printf("prt_gcmat: undefined plane %d\n", plane);
    exit_(1);
  }

  fprintf(outf,"# total monitors: %d\n", m);

  if (plane == 1)
    fprintf(outf,"# total horizontal correctors: %d\n", n[plane-1]);
  else
    fprintf(outf,"# total vertical correctors: %d\n", n[plane-1]);

  fprintf(outf, "#A [%d][%d]= \n", m, n[plane-1]);
  for (i = 1; i <= m; i++) {
    for (j = 1; j <= n[plane-1]; j++)
      fprintf(outf, "% .3e ", A_lsoc[plane-1][i][j]);
    fprintf(outf, "\n");
  }

  fprintf(outf, "#U [%d][%d]= \n", m, n[plane-1]);
  for (i = 1; i <= m; i++) {
    for (j = 1; j <= n[plane-1]; j++)
      fprintf(outf, "% .3e ", U_lsoc[plane-1][i][j]);
    fprintf(outf, "\n");
  }

  fprintf(outf, "#w [%d]= \n", n[plane-1]);
  for (j = 1; j <= n[plane-1]; j++)
    fprintf(outf, "% .3e ", w_lsoc[plane-1][j]);
  fprintf(outf, "\n#V [%d][%d]= \n", m, n[plane-1]);

  for (i = 1; i <= n[plane-1]; i++) {
    for (j = 1; j <= n[plane-1]; j++)
      fprintf(outf, "% .3e ", V_lsoc[plane-1][i][j]);
    fprintf(outf, "\n");
  }

  fclose(outf);
}


void gcmat(int bpm, int corr, int plane)
{
  /* Get correlation matrix

                -----------
              \/beta  beta
                    i     j
        A   = ------------- cos(nu pi - 2 pi|nu  - nu |)
         ij   2 sin(pi nu)                     i     j

  */

  bool      first;
  int       i, j;
  long int  loc;
  double    nu, betai, betaj, nui, nuj, spiq;

  const double  eps = 1e-10;

  m = GetnKid(bpm); n[plane-1] = GetnKid(corr);

  if (m > mnp) {
    printf("gcmat: max no of BPM exceeded %d (%d)\n", m, mnp);
    exit_(1);
  }

  if (n[plane-1] > mnp) {
    printf("gcmat: max no of correctors exceeded %d (%d)\n", n[plane-1], mnp);
    exit_(1);
  }

  first = (plane == 1)? first_h : first_v;
  if (first) {
    if (plane == 1)
      first_h = false;
    else
      first_v = false;
    A_lsoc[plane-1] = dmatrix(1, m, 1, n[plane-1]);
    U_lsoc[plane-1] = dmatrix(1, m, 1, n[plane-1]);
    w_lsoc[plane-1] = dvector(1, n[plane-1]);
    V_lsoc[plane-1] = dmatrix(1, n[plane-1], 1, n[plane-1]);
  }

  nu = globval.TotalTune[plane-1]; spiq = sin(M_PI*nu);

  for (i = 1; i <= m; i++) {
    loc = Elem_GetPos(bpm, i);
    betai = Cell[loc].Beta[plane-1]; nui = Cell[loc].Nu[plane-1];
    for (j = 1; j <= n[plane-1]; j++) {
      loc = Elem_GetPos(corr, j);
      betaj = Cell[loc].Beta[plane-1]; nuj = Cell[loc].Nu[plane-1];
      A_lsoc[plane-1][i][j] =
	sqrt(betai*betaj)/(2.0*spiq)*cos(nu*M_PI-fabs(2.0*M_PI*(nui-nuj)));
    }
  }

  for (i = 1; i <= m; i++)
    for (j = 1; j <= n[plane-1]; j++)
      U_lsoc[plane-1][i][j] = A_lsoc[plane-1][i][j];

  dsvdcmp(U_lsoc[plane-1], m, n[plane-1], w_lsoc[plane-1], V_lsoc[plane-1]);

  for (j = 1; j <= n[plane-1]; j++)
    if (w_lsoc[plane-1][j] < eps) {
      printf("gcmat: singular beam response matrix"
	     " %12.3e, plane = %d, j = %d\n",
	     w_lsoc[plane-1][j], plane, j);
      prt_gcmat(bpm, corr, plane);
      exit_(1);
    }
}

void lsoc(int niter, int bpm, int corr, int plane)
{
  int       i, j;
  long int  k;
  svdarray  b, x;

  for (i = 1; i <= niter; i++) {
    for (j = 1; j <= m; j++) {
      k = Elem_GetPos(bpm, j);
      b[j] = -Cell[k].BeamPos[(plane-1)*2] + Cell[k].dS[plane-1];
    }
      
    dsvbksb(U_lsoc[plane-1], w_lsoc[plane-1], V_lsoc[plane-1],
	    m, n[plane-1], b, x);

    for (j = 1; j <= n[plane-1]; j++)
      if (plane == 1)
        SetdKpar(corr, j, Dip, -x[j]);
      else
        SetdKpar(corr, j, -Dip, x[j]);
  }
}

