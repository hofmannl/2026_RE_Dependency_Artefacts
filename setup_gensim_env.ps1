Write-Host "Creating .venv_gensim virtual environment..." -ForegroundColor Green
py -3.9 -m venv .venv_gensim

Write-Host "Activating virtual environment..." -ForegroundColor Green
& .\.venv_gensim\Scripts\Activate.ps1

Write-Host "Upgrading pip..." -ForegroundColor Green
python -m pip install --upgrade pip

Write-Host "Installing requirements_gensim.txt..." -ForegroundColor Green
pip install -r .\env_dependencies\requirements_gensim.txt