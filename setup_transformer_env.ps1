Write-Host "Creating .venv_transformers virtual environment..." -ForegroundColor Green
py -3.14 -m venv .venv_transformers

Write-Host "Activating virtual environment..." -ForegroundColor Green
& .\.venv_transformers\Scripts\Activate.ps1

Write-Host "Upgrading pip, setuptools, and wheel..." -ForegroundColor Green
python -m pip install --upgrade pip setuptools wheel

Write-Host "Installing transformers and core dependencies..." -ForegroundColor Green
pip install transformers torch torchvision torchaudio

Write-Host "Installing additional NLP dependencies for BART-large-MNLI..." -ForegroundColor Green
pip install accelerate scipy sentencepiece protobuf

Write-Host "Installing huggingface-hub for model management..." -ForegroundColor Green
pip install huggingface-hub

pip install dotenv
pip install parameterized

pip install -r .\env_dependencies\requirements_transformers.txt

Write-Host "`nSetup complete! Virtual environment activated at .venv_transformers" -ForegroundColor Cyan
Write-Host "To deactivate later, run: deactivate" -ForegroundColor Cyan

# Verify installation
Write-Host "`nVerifying transformers installation..." -ForegroundColor Yellow
python -c "import transformers; print(f'Transformers version: {transformers.__version__}')"
python -c "import torch; print(f'PyTorch version: {torch.__version__}')"
