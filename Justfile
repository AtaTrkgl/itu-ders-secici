set windows-shell := ["powershell.exe", "-NoLogo", "-NoProfile", "-Command"]


default:
    @just --list

# Install system dependencies (Cross-platform dispatcher)
system-reqs:
    @echo "Detected OS: {{os()}}"
    @just _system-reqs-{{os()}}

# Internal: Windows system requirements
_system-reqs-windows:
    @echo "Installing Windows dependencies..."
    winget install --id=astral-sh.uv -e; if ($LASTEXITCODE -ne 0) { if (Get-Command "uv" -ErrorAction SilentlyContinue) { echo "uv is already installed." } else { exit $LASTEXITCODE } }

# Internal: Linux system requirements
_system-reqs-linux:
    @echo "Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh

# Internal: MacOS system requirements
_system-reqs-macos:
    @echo "Installing MacOS dependencies..."
    brew install uv

# Install project dependencies with uv
install:
    uv sync

# Run setup wizard
setup:
    uv run src/setup.py

# Run the program with uv
run:
    uv run src/run.py

# Run in test mode with uv
test:
    uv run src/run.py --test

# Clean artifacts
clean:
    uv run "import shutil, pathlib; shutil.rmtree('src/__pycache__', ignore_errors=True); [p.unlink() for p in pathlib.Path('logs').glob('*.txt')]"

# Initialize project fully
init: install setup
