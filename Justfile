# Run the setup script defined in readme
setup:
    python src/setup.py

# Run the run script with test flag
test:
    python src/run.py -test

# Run the run script
run:
    python src/run.py

# Run the setup script using uv
setup-uv:
    uv run src/setup.py

# Run the run script with test flag using uv
test-uv:
    uv run src/run.py -test

# Run the run script using uv
run-uv:
    uv run src/run.py

# Clean artifacts (pycache and logs)
clean:
    python -c "import shutil, pathlib; shutil.rmtree('src/__pycache__', ignore_errors=True); [p.unlink() for p in pathlib.Path('logs').glob('*.txt')]"
