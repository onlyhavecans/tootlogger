build: clean
	pipenv run python setup.py sdist

upload: build
	pipenv run twine upload --sign dist/*

clean:
	rm -f dist/*
