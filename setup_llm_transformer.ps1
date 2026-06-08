Write-Host "Creating .venv_transformers virtual environment..." -ForegroundColor Green
py -3.14 -m venv .venv_llm_transformers

Write-Host "Activating virtual environment..." -ForegroundColor Green
& .\.venv_llm_transformers\Scripts\Activate.ps1

Write-Host "Upgrading pip, setuptools, and wheel..." -ForegroundColor Green
python -m pip install --upgrade pip setuptools wheel

Write-Host "Installing transformers and core dependencies..." -ForegroundColor Green
pip install transformers torch torchvision torchaudio


Write-Host "Installing requirements_llm_transformers.txt..." -ForegroundColor Green
pip install -r .\env_dependencies\requirements_llm_transformers.txt
