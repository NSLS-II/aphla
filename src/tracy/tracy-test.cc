
#define ORDER 1

#include "tracy_lib.h"
#include "t2elem.h"

#include <string>
#include <iostream>

using namespace std;

int no_tps = 1;

int main(int argc, char* argv[])
{
    char *infile="CD3-June20-tracy";
    
    globvalrec globv;

    Read_Lattice(infile);

    globval.H_exact     = false;
    globval.quad_fringe = false;
    globval.radiation   = false; 
    //globval.diffusion   = false;
    globval.pathlength  = true;  
    globval.bpm         = 0;
    globval.Cavity_on   = true;  
    globval.emittance   = false;
  
    // store global state
    //putglobv_(&globval);

    //Cell_SetdP(dP);


    double dP = 0.0;
    Ring_GetTwiss(true, dP);

    printglob();

    CellType Cell;
    getelem(0, &Cell);
    cout << dP << Cell.BeamPos[0] << endl;
}
