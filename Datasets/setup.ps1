Write-Host "Creating .venv_fasttext virtual environment..." -ForegroundColor Green
py -3.14 -m venv .venv

Write-Host "Activating virtual environment..." -ForegroundColor Green
& .\.venv\Scripts\Activate.ps1

Write-Host "Upgrading pip..." -ForegroundColor Green
python -m pip install --upgrade pip

Write-Host "Installing required packages from requirements.txt..." -ForegroundColor Green
pip install -r .\requirements.txt