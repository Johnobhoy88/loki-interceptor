SEMANTIC_REGRESSION=tests/semantic/run_regression.py

.PHONY: semantic-regression
semantic-regression:
	python3 $(SEMANTIC_REGRESSION)
