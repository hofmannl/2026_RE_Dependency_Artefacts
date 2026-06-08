$ErrorActionPreference = "Stop"

$venvActivate = ".\.venv\Scripts\Activate.ps1"

if (-Not (Test-Path $venvActivate)) {
    Write-Error "Virtual environment not found at .venv\Scripts\Activate.ps1"
    exit 1
}

Write-Host "Activating virtual environment..." -ForegroundColor Cyan
. $venvActivate

Write-Host "Running tests with coverage..." -ForegroundColor Cyan
coverage run --branch --source=src -m unittest discover -s tests -p "*_test.py"
Write-Host "Generating HTML report in ./htmlcov..." -ForegroundColor Cyan
coverage html

Write-Host "`Done! Open 'htmlcov/index.html' in your browser to view the coverage report." -ForegroundColor Green
