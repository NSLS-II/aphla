all: orbit_resources.py

orbit_resources.py: orbit_resources.qrc
	pyrcc4 -o orbit_resources.py orbit_resources.qrc

clean:
	rm -f hla/*.pyc
