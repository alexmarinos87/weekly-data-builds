# Set SRC to the path of your source data or script
SRC=src/data/input.csv

install: ; poetry install
lint: ; ruff check etl
test: ; pytest
run: ; poetry run python -m etl.cli run $(SRC)
