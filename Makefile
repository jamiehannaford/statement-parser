default: test

.PHONY: test
test:
	python ./compare_output.py
