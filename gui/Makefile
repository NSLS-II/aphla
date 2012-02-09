all: gui_resources.py

gui_resources.py: gui_resources.qrc
	pyrcc4 -o gui_resources.py gui_resources.qrc

clean:
	rm -f *.pyc
	rm -f gui_resources.py
