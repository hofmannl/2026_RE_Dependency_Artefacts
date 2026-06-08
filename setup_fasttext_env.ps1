Write-Host "Creating .venv_fasttext virtual environment..." -ForegroundColor Green
py -3.9 -m venv .venv_fasttext

Write-Host "Activating virtual environment..." -ForegroundColor Green
& .\.venv_fasttext\Scripts\Activate.ps1

Write-Host "Upgrading pip..." -ForegroundColor Green
python -m pip install --upgrade pip

Write-Host "Installing FastText with pre-built wheels..." -ForegroundColor Green
pip install fasttext-wheel==0.9.2

Write-Host "Installing numpy..." -ForegroundColor Green
pip install numpy==1.26.4

Write-Host "Installing python-dotenv..." -ForegroundColor Green
pip install python-dotenv==1.1.1

Write-Host "`nSetup complete! Virtual environment activated at .venv_fasttext" -ForegroundColor Cyan
Write-Host "To deactivate later, run: deactivate" -ForegroundColor Cyan

Write-Host "Installing requirements_fasttext.txt..." -ForegroundColor Green
pip install -r .\env_dependencies\requirements_fasttext.txt

# Verify installation
Write-Host "`nVerifying installation..." -ForegroundColor Yellow
python -c "import fasttext; print(f'FastText installed successfully')"
python -c "import numpy; print(f'NumPy version: {numpy.__version__}')"
