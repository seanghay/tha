build:
	rm -rf *.egg-info/ dist/ tha/__pycache__
	python setup.py sdist

upload:
	twine upload dist/*