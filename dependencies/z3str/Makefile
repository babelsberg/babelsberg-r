default: all

# Change the path to Z3 4.1.1 accordingly
# The directory indicated by this path should contain "lib" and "bin"
# e.g. "/home/z3_src_4.1.1"
Z3_path = /home/tim/Dev/babelsberg-r/dependencies/z3

#-----------------------------------------

JUNK = str
THEORY = strTheory.cpp
MAIN = testMain.cpp
SOURCE = $(THEORY) $(MAIN)
INCLUDE = $(Z3_path)/src/api
LIB = $(Z3_path)/build

fat: $(SOURCE)
	ar x $(LIB)/libz3.a
	g++ -rdynamic -c -fPIC -O3 -fopenmp -I$(INCLUDE) -L$(LIB) -lz3 -lrt $(THEORY) -o z3str.o
	g++ -shared -rdynamic -Wl,-soname,libz3str.so -O3 -fopenmp -I$(INCLUDE) -L$(LIB) -lz3 -lrt -o libz3str.so *.o
	rm *.o

shared: $(SOURCE)
	g++ -rdynamic -c -fPIC -O3 -fopenmp -I$(INCLUDE) -L$(LIB) -lz3 $(THEORY) -o z3str.o
	g++ -shared -rdynamic -Wl,-soname,libz3str.so -O3 -fopenmp -I$(INCLUDE) -L$(LIB) -lz3 -o libz3str.so z3str.o

static: $(SOURCE)
	ar x $(LIB)/libz3.a
	g++ -c -fPIC -O3 -fopenmp -I$(INCLUDE) -L$(LIB) -lrt $(THEORY) -o strtheory.o
	g++ -c -fPIC -O3 -fopenmp -I$(INCLUDE) -L$(LIB) -lrt $(MAIN) -o strmain.o
	g++ -O3 -fopenmp -I$(INCLUDE) -L$(LIB) *.o -lrt -o str_static
	rm *.o

dynamic: $(SOURCE)
	g++ -O3 -DDEBUGLOG -fopenmp -I$(INCLUDE) -L$(LIB) $(SOURCE) -lz3  -o str_dynamc 

all: $(SOURCE)
	g++ -O3 -fopenmp -static -I$(INCLUDE) -L$(LIB) $(SOURCE) -lz3 -lrt -o str -Wall

clean:
	rm -f $(JUNK)
