

tests:
	python autotest.py
	python -c "from url_strip.testing import run_tests; exit(1 if run_tests() else 0)"

install:
	pip install .

uninstall:
	pip uninstall url_strip -y

clean:
	rm build -rf
	rm url_strip.egg-info -rf
