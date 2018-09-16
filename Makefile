build: clean
	pipenv run python setup.py sdist bdist_wheel

upload: build
	twine upload --sign dist/*

clean:
	rm -f dist/*
