.PHONY: setup run test setup-uv run-uv test-uv clean

setup:
	python src/setup.py

test:
	python src/run.py -test

run:
	python src/run.py

setup-uv:
	uv run src/setup.py

test-uv:
	uv run src/run.py -test

run-uv:
	uv run src/run.py

clean:
	python -c "import shutil, pathlib; shutil.rmtree('src/__pycache__', ignore_errors=True); [p.unlink() for p in pathlib.Path('logs').glob('*.txt')]"
