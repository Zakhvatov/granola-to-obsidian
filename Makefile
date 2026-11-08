.PHONY: test lint check install

test:
	pytest

lint:
	ruff check .
	shellcheck install.sh

check: lint test

install:
	./install.sh
