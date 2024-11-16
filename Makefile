quality:
	ruff check src/clarin_spf examples/ tests/
	ruff format --check src/clarin_spf examples/ tests/

style:
	ruff check src/clarin_spf examples/ tests/ --fix
	ruff format src/clarin_spf examples/ tests/

test:
	pytest tests/
