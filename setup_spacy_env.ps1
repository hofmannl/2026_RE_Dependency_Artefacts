Write-Host "Creating .venv_spacy virtual environment..." -ForegroundColor Green
py -3.9 -m venv .venv_spacy

Write-Host "Activating virtual environment..." -ForegroundColor Green
& .\.venv_spacy\Scripts\Activate.ps1

Write-Host "Upgrading pip..." -ForegroundColor Green
python -m pip install --upgrade pip

Write-Host "Installing spaCy with pre-built wheels..." -ForegroundColor Green
pip install --only-binary :all: spacy

Write-Host "Installing en_core_web_trf from spaCy..." -ForegroundColor Green
python -m spacy download en_core_web_trf   

Write-Host "Installing requirements_spacy.txt..." -ForegroundColor Green
pip install -r .\env_dependencies\requirements_spacy.txt

Write-Host "`nSetup complete! Virtual environment activated at .venv_spacy" -ForegroundColor Cyan
Write-Host "To deactivate later, run: deactivate" -ForegroundColor Cyan

# Verify installation
Write-Host "`nVerifying spaCy installation..." -ForegroundColor Yellow
python -c "import spacy; print(f'spaCy version: {spacy.__version__}')"
python -c "import numpy; print(f'NumPy version: {numpy.__version__}')"
