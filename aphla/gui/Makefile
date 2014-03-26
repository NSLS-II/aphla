all: gui_resources.py

gui_resources.py: gui_resources.qrc
	pyrcc4 -o gui_resources.py gui_resources.qrc

mleapresources.py: mleapresources.qrc
	pyrcc4 -o mleapresources.py mleapresources.qrc
clean:
	rm -f *.pyc
	rm -f gui_resources.py
