

tests:
	python autotest.py

install:
	pip install .

uninstall:
	pip uninstall url_strip

clean:
	rm build -rf
	rm url_strip.egg-info -rf
