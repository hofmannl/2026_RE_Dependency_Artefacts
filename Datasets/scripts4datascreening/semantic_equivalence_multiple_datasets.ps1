$filePairs = @(
    @(
        "<USER_PATH_TO_GROUND_TRUTH_CSV>",
        "<USER_PATH_TO_RESULTS>"
    ),
    @(
        "<USER_PATH_TO_GROUND_TRUTH_CSV>",
        "<USER_PATH_TO_RESULTS>"
    ),
    @(
        "<USER_PATH_TO_GROUND_TRUTH_CSV>",
        "<USER_PATH_TO_RESULTS>"
    )
)




# --------------------------
# Settings
# --------------------------
$pythonExe = "python"  # or full path to python.exe
$pythonScriptPath = "<USER_PATH>\evalutator_scripts\semantic_equivalence_multiple_datasets.py"

$separator  = "|"     # what your evaluator expects
$skipHeader = "yes"   # "yes" or "no"

# --------------------------
# Validate Python script exists
# --------------------------
if (-not (Test-Path -LiteralPath $pythonScriptPath)) {
    Write-Host "Error: Python script not found at $pythonScriptPath" -ForegroundColor Red
    exit 1
}

# --------------------------
# Validate all files exist
# --------------------------
$allValid = $true
foreach ($pair in $filePairs) {
    if ($pair.Count -ne 2) {
        Write-Host "Error: A pair must be exactly (ground_truth, prediction). Found: $pair" -ForegroundColor Red
        $allValid = $false
        continue
    }

    $gtPath = $pair[0]
    $predPath = $pair[1]

    if (-not (Test-Path -LiteralPath $gtPath)) {
        Write-Host "Error: Ground truth file not found at $gtPath" -ForegroundColor Red
        $allValid = $false
    }

    if (-not (Test-Path -LiteralPath $predPath)) {
        Write-Host "Error: Prediction file not found at $predPath" -ForegroundColor Red
        $allValid = $false
    }
}

if (-not $allValid) { exit 1 }

Write-Host "Found $($filePairs.Count) file pair(s)" -ForegroundColor Green
Write-Host ""

# --------------------------
# Create a temporary input file for the Python script
# --------------------------
$tempInputFile = New-TemporaryFile -Errorentity Stop
$inputContent = @()

# Add all file pairs (exactly in the order your Python script asks them)
foreach ($pair in $filePairs) {
    $gtPath = $pair[0]
    $predPath = $pair[1]

    Write-Host "Adding pair:" -ForegroundColor Cyan
    Write-Host "  Ground Truth: $(Split-Path -Leaf $gtPath)"
    Write-Host "  Prediction:   $(Split-Path -Leaf $predPath)"
    Write-Host ""

    $inputContent += $gtPath
    $inputContent += $predPath
}

# Empty line to finish pairs entry
$inputContent += ""

# Then separator prompt
$inputContent += $separator

# Then skip-header prompt
$inputContent += $skipHeader

# Write input to temporary file
$inputContent | Out-File -FilePath $tempInputFile.FullName -Encoding UTF8

Write-Host "Running generalisation containment evaluation..." -ForegroundColor Green
Write-Host ""

# Run Python script with input redirection
Get-Content -LiteralPath $tempInputFile.FullName | & $pythonExe $pythonScriptPath

# Clean up
Remove-Item -LiteralPath $tempInputFile.FullName -Force

Write-Host ""
Write-Host "Evaluation complete!" -ForegroundColor Green