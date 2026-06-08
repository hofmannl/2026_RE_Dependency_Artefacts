# Set the working directory to the src folder
$projectRoot = "C:\Users\hofmann\Desktop\dependencyanalyseandsynergyofuserstories\src"
Set-Location $projectRoot

# Define the Python script paths
$pythonScripts = @(
    "experiments\transformer_classification\generalization_evaluation.py",
    "experiments\transformer_classification\containment_evaluation.py",
    "experiments\transformer_classification\equivalence_evaluation.py"
)

$scriptNames = @("Generalization", "Containment", "Equivalence")

# Define input files
$dataFiles = @(
    "C:\Users\hofmann\Desktop\dependencyanalyseandsynergyofuserstories\Datasets\elaborated_ground_truth\datasets_elaborated\sim02.xlsx"
)

# ,
#     "C:\lukas\dependencyanalyseandsynergyofuserstories\src\experiments\_data\pre_computed_pairs_data\g08.xlsx",
#     "C:\lukas\dependencyanalyseandsynergyofuserstories\src\experiments\_data\pre_computed_pairs_data\g17.xlsx",
#     "C:\lukas\dependencyanalyseandsynergyofuserstories\src\experiments\_data\pre_computed_pairs_data\g22.xlsx"

$loadprecompute = "l"
$logOutput = "yes"

# Function to invoke evaluations
function Invoke-Evaluation {
    param(
        [string]$DataFile,
        [string]$ScriptPath,
        [string]$ScriptName
    )
    
    $inputs = @"
$loadprecompute
$DataFile
$logOutput
"@
    
    Write-Host "Starting $ScriptName evaluation..." -ForegroundColor Cyan
    $inputs | python $ScriptPath
    Write-Host "$ScriptName evaluation completed!" -ForegroundColor Green
}

# Main execution loop
foreach ($dataFile in $dataFiles) {
    $fileName = Split-Path $dataFile -Leaf
    Write-Host "`n" -foregroundColor Black
    Write-Host "============================================================" -ForegroundColor Yellow
    Write-Host "Processing: $fileName" -ForegroundColor Yellow
    Write-Host "============================================================" -ForegroundColor Yellow
    
    for ($i = 0; $i -lt $pythonScripts.Count; $i++) {
        Write-Host "`n------------------------------------------------------------" -ForegroundColor Gray
        Invoke-Evaluation -DataFile $dataFile -ScriptPath $pythonScripts[$i] -ScriptName $scriptNames[$i]
    }
    
    Write-Host "`n============================================================" -ForegroundColor Yellow
    Write-Host "Finished processing: $fileName" -ForegroundColor Yellow
    Write-Host "============================================================`n" -ForegroundColor Yellow
}

Write-Host "All evaluations completed successfully!" -ForegroundColor Green