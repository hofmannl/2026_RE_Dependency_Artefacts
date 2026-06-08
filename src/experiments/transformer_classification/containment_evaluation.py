from experiments.utils.import_word_pairs import load_word_pairs
from relationship_analysers_classifier.relationship_analysers.containment_analyser.transformer_containment_approach import ContainmentAnalyserTransformer
from experiments.transformer_classification.trans_utils import save_results_to_csv, get_yes_no_input, print_or_log
from experiments.utils.word_pairs import extract_entities_pairs
from utilis.dataclasses_user_story import AtomicUserStoryRecord
from pathlib import Path
import json
import time

current_file = Path(__file__).resolve()
entity_pairs: set[tuple[str, str]]

compute_or_load: str = input("Compute pairs or load pre-computed pairs? (c/l): ").strip().lower()
if compute_or_load not in ['c', 'l']:
    raise ValueError("Invalid input. Please enter 'c' to compute or 'l' to load pre-computed pairs.")
elif compute_or_load == 'c':
    data_path = current_file.parents[1] / "_data" / "lemmatized_data"

    file_name: str = input("Enter the filename (without extension) to process lemmatized, annotated User Stories: ") 
    file_name = file_name.strip()
    file_path: str = f"{file_name}.json" if not file_name.endswith(".json") else file_name

    us_data: list[dict] = []
    with open(data_path / file_path, "r", encoding="utf-8") as f:
        temp: str = ""
        for line in f:
            temp += line
        us_data = json.loads(temp)

    stories: list[AtomicUserStoryRecord] = []

    for us in us_data:
        story_record = AtomicUserStoryRecord.factory_direct_import(us)
        stories.append(story_record)

    # Data will be loaded
    load_pre_computed: str = input("Enter the filename (without extension) to process lemmatized, annotated User Stories: ") 
    entity_pairs = extract_entities_pairs(stories)
elif compute_or_load == 'l':
    data_path = current_file.parents[1] / "_data" / "pre_computed_pairs_data"
    
    file_name: str = input("Enter the filename (without extension) of the pre-computed entity pairs: ").strip()
    file_name = file_name.strip()
    file_path: str = f"{file_name}.xlsx" if not file_name.endswith(".xlsx") else file_name
    
    entity_pairs = load_word_pairs(file_path, sheet_name="HS4ConOfE")

# Logging option
input_print_or_log: bool = get_yes_no_input(
    "Do you want to log the output to a file? (yes/no)"
)

# Initialize variables
temp_result: tuple[bool, float] = (False, 0.0)
total_results: list[tuple[str, str, bool, float]] = []
threshold: float = 0.0

### Entities
m = ContainmentAnalyserTransformer()

### THRESHOLD 0.5 ###
threshold = 0.5
start_time = time.time()
for pair in entity_pairs:
    temp_result = m.compute_relations( pair[0], pair[1], threshold=threshold )
    total_results.append((pair[0], pair[1], temp_result[0], temp_result[1]))
    temp_result = (False, 0.0)
end_time = time.time()

print_or_log(
    f"Containment Analyser Transformer | {file_name} | Entity pairs | Threshold {threshold} | {end_time - start_time} seconds",
    file_name=f"{file_name}",
    file_path=current_file.parents[0],
    log=input_print_or_log
)

save_results_to_csv(
    current_file.parents[0] / f"{file_name}_containment_entity_threshold_{threshold}.csv", 
    total_results, 
    "Entity 1 | Entity 2 | Result | Score \n"
)
total_results = []

### THRESHOLD 0.7 ###
threshold = 0.7
start_time = time.time()
for pair in entity_pairs:
    temp_result = m.compute_relations( pair[0], pair[1], threshold=threshold )
    total_results.append((pair[0], pair[1], temp_result[0], temp_result[1]))
    temp_result = (False, 0.0)
end_time = time.time()

print_or_log(f"Containment Analyser Transformer | {file_name} | Entity pairs | Threshold {threshold} | {end_time - start_time} seconds", 
    file_name=f"{file_name}",
    file_path=current_file.parents[0],
    log=input_print_or_log
)
save_results_to_csv(
    current_file.parents[0] / f"{file_name}_containment_entity_threshold_{threshold}.csv", 
    total_results, 
    "Entity 1 | Entity 2 | Result | Score \n"
)
total_results = []

### THRESHOLD 0.9 ###
threshold = 0.9
start_time = time.time()
for pair in entity_pairs:
    temp_result = m.compute_relations( pair[0], pair[1], threshold=threshold )
    total_results.append((pair[0], pair[1], temp_result[0], temp_result[1]))
    temp_result = (False, 0.0)
end_time = time.time()

print_or_log(f"Containment Analyser Transformer | {file_name} | Entity pairs | Threshold {threshold} | {end_time - start_time} seconds", 
    file_name=f"{file_name}",
    file_path=current_file.parents[0],
    log=input_print_or_log
)
save_results_to_csv(
    current_file.parents[0] / f"{file_name}_containment_entity_threshold_{threshold}.csv", 
    total_results, 
    "Entity 1 | Entity 2 | Result | Score \n"
)
total_results = []

m = None
### End Entities