.PHONY: format lint test check build clean

ZIP_NAME := common.zip

format:
	isort .
	black .

lint:
	black --check .
	isort --check .
	flake8 .

test:
	pytest

check: lint test

# Bytecode caches are excluded: pytest writes them under python/toa/, and they
# must not ship in the layer.
build: clean
	zip -r $(ZIP_NAME) python/ -x '*__pycache__/*' '*.pyc'
	@echo "Built $(ZIP_NAME)"

clean:
	rm -f $(ZIP_NAME)
