quality:
	ruff check src/clarin_spf examples/
	ruff format --check src/clarin_spf examples/

style:
	ruff check src/clarin_spf examples/ --fix
	ruff format src/clarin_spf examples/
	