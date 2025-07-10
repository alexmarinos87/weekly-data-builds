SRC=your_source_here

install: ; poetry install
lint: ; ruff check etl
test: ; pytest
run: ; poetry run python -m etl.cli run $(SRC)
