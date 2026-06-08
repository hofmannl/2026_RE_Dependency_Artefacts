# Compiling the project
.\.venv_default\Scripts\activate
Write-Host "Directory of .venv activation: $(Get-Location)"
# Set-Location -Path ".\src\"
python.exe -m pip install --upgrade pip
pip install --upgrade pip
pip install --upgrade setuptools wheel
Write-Host "Directory of code and dependency installation and the root for the jupzter notebook: $(Get-Location)"
pip install -e .