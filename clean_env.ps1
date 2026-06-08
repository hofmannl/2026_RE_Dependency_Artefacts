#.\CleanPythonTemp.ps1 -Path 'D:\Projects\MyAppExample'
#.\CleanPythonTemp.ps1 -PurgePipCache
#.\CleanPythonTemp.ps1 -Path 'D:\Projects\MyAppExample' -PurgePipCache

param(
    [string]$Path       = (Get-Location),
    [switch]$PurgePipCache
)

Write-Host "Cleaning Python temp files in `"$Path`"" -ForegroundColor Cyan

function Exclude-VenvAndVsCode {
    param($Item)
    return ($Item.FullName -notlike "*\.venv\*" -and $Item.FullName -notlike "*\.vscode\*" -and $Item.FullName -notlike "*\nlp_models\*")
}

Get-ChildItem -Path $Path -Recurse -Directory -ErrorAction SilentlyContinue |
  Where-Object { 
    $_.Name -eq '__pycache__' -and (Exclude-VenvAndVsCode $_)
  } |
  ForEach-Object {
    Write-Host "Removing folder: $($_.FullName)"
    Remove-Item -LiteralPath $_.FullName -Recurse -Force -ErrorAction SilentlyContinue
  }

Get-ChildItem -Path $Path -Recurse -File -Include *.pyc,*.pyo,*.pyd -ErrorAction SilentlyContinue |
  Where-Object { Exclude-VenvAndVsCode $_ } |
  ForEach-Object {
    Write-Host "Removing file: $($_.FullName)"
    Remove-Item -LiteralPath $_.FullName -Force -ErrorAction SilentlyContinue
  }

Get-ChildItem -Path $Path -Recurse -Directory -Include *.egg-info -ErrorAction SilentlyContinue |
  Where-Object { Exclude-VenvAndVsCode $_ } |
  ForEach-Object {
    Write-Host "Removing .egg-info folder: $($_.FullName)"
    Remove-Item -LiteralPath $_.FullName -Recurse -Force -ErrorAction SilentlyContinue
  }

  if ($PurgePipCache) {
    Write-Host "Purging pip cache..." -ForegroundColor Cyan
    try {
        pip cache purge
        Write-Host "pip cache purged."
    } catch {
        Write-Warning "Could not purge pip cache: $_"
    }
}