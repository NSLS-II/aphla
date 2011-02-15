TRACY_HOME=tracy-3.5
NUMREC_HOME=../num_rec
LIB=-L${TRACY_HOME}/tracy/src -L ${NUMREC_HOME}/src \
    -L${TRACY_HOME}/TPSA/
INC=-I${TRACY_HOME}/tracy/inc

all:tracy-test
tracy-test: tracy-test.cc
	g++ -o $@ $< $(INC) $(LIB) -ltracy -lnum_rec -lTPSALib -lLieLib


clean:
	rm tracy-test
