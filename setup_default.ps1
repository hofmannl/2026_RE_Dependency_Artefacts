Write-Host "Creating .venv_fasttext virtual environment..." -ForegroundColor Green
py -3.14 -m venv .venv_default

Write-Host "Activating virtual environment..." -ForegroundColor Green
& .\.venv_default\Scripts\Activate.ps1

Write-Host "Upgrading pip..." -ForegroundColor Green
python -m pip install --upgrade pip

Write-Host "Installing required packages from requirements.txt..." -ForegroundColor Green
pip install -r .\env_dependencies\requirements_default.txt