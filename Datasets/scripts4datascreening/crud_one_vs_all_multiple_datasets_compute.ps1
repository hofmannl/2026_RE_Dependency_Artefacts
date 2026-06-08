# llm
# $filePairs = @(
#     @(
#         "<USER_PATH>\Datasets\elaborated_ground_truth\datasets_elaborated\ground_truth_in_csv\real_world\g08_labeled_crud.csv",
#         "<USER_PATH>\src\experiments\_data\pre_computed_pairs_data\results_crud\results_gdwg\g08_baseline_lemmatized.json_crud_classification_openai-gpt-oss-120b_word_results.csv"
#     ),
#     @(
#         "<USER_PATH>\Datasets\elaborated_ground_truth\datasets_elaborated\ground_truth_in_csv\real_world\g22_labeled_crud.csv",
#         "<USER_PATH>\src\experiments\_data\pre_computed_pairs_data\results_crud\results_gdwg\g22_baseline_lemmatized.json_crud_classification_openai-gpt-oss-120b_word_results.csv"
#     )
# )

# gensim
# $filePairs = @(
#     @(
#         "<USER_PATH>\Datasets\elaborated_ground_truth\datasets_elaborated\ground_truth_in_csv\real_world\g08_labeled_crud.csv",
#         "<USER_PATH>\src\experiments\_data\pre_computed_pairs_data\results_crud\results_gensim\g08_baseline_lemmatized.json_crud_classification_gensim_sentence_results.csv"
#     ),
#     @(
#         "<USER_PATH>\Datasets\elaborated_ground_truth\datasets_elaborated\ground_truth_in_csv\real_world\g22_labeled_crud.csv",
#         "<USER_PATH>\src\experiments\_data\pre_computed_pairs_data\results_crud\results_gensim\g22_baseline_lemmatized.json_crud_classification_gensim_sentence_results.csv"
#     )
# )

# # fasttext 
# $filePairs = @(
#     @(
#         "<USER_PATH>\Datasets\elaborated_ground_truth\datasets_elaborated\ground_truth_in_csv\g08_labeled_crud.csv",
#         "<USER_PATH>\src\experiments\_data\pre_computed_pairs_data\results_crud\results_fasttext\g08_baseline_lemmatized.json_crud_classification_fasttext_30_words_results.csv"
#     ),
#     @(
#         "<USER_PATH>\Datasets\elaborated_ground_truth\datasets_elaborated\ground_truth_in_csv\g22_labeled_crud.csv",
#         "<USER_PATH>\src\experiments\_data\pre_computed_pairs_data\results_crud\results_fasttext\g22_baseline_lemmatized.json_crud_classification_fasttext_30_words_results.csv"
#     )
#     # Add more pairs as needed
# )

$pythonScriptPath = "<USER_PATH>\evalutator_scripts\crud_one_vs_all_multiple_datasets.py"
$separator = "|"  # Update if needed

# Validate Python script exists
if (-not (Test-Path $pythonScriptPath)) {
    Write-Host "Error: Python script not found at $pythonScriptPath" -ForegroundColor Red
    exit 1
}

# Validate all files exist
$allValid = $true
foreach ($pair in $filePairs) {
    $gtPath = $pair[0]
    $predPath = $pair[1]
    
    if (-not (Test-Path $gtPath)) {
        Write-Host "Error: Ground truth file not found at $gtPath" -ForegroundColor Red
        $allValid = $false
    }
    
    if (-not (Test-Path $predPath)) {
        Write-Host "Error: Prediction file not found at $predPath" -ForegroundColor Red
        $allValid = $false
    }
}

if (-not $allValid) {
    exit 1
}

Write-Host "Found $($filePairs.Count) file pair(s)" -ForegroundColor Green
Write-Host ""

# Create a temporary input file for the Python script
$tempInputFile = New-TemporaryFile -ErrorAction Stop
$inputContent = @()

# Add all file pairs
foreach ($pair in $filePairs) {
    $gtPath = $pair[0]
    $predPath = $pair[1]
    
    Write-Host "Adding pair:" -ForegroundColor Cyan
    Write-Host "  Ground Truth: $(Split-Path -Leaf $gtPath)"
    Write-Host "  Prediction:   $(Split-Path -Leaf $predPath)"
    
    $inputContent += $gtPath
    $inputContent += $predPath
}

# Add empty line to finish pairs and separator
$inputContent += ""  # Empty line to finish pairs
$inputContent += $separator

# Write input to temporary file
$inputContent | Out-File -FilePath $tempInputFile.FullName -Encoding UTF8

Write-Host ""
Write-Host "Running CRUD evaluation..." -ForegroundColor Green
Write-Host ""

# Run Python script with input redirection
Get-Content $tempInputFile.FullName | & python $pythonScriptPath

# Clean up
Remove-Item $tempInputFile.FullName -Force

Write-Host ""
Write-Host "Evaluation complete!" -ForegroundColor Green