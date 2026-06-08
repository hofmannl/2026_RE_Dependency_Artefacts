import os
from relationship_analysers_classifier.relationship_analysers.containment_analyser.gdwg_containment_approach import ContainmentAnalyserGdwg
from experiments.utils.word_pairs import extract_entities_pairs
from experiments.utils.import_word_pairs import load_word_pairs
from utilis.dataclasses_user_story import AtomicUserStoryRecord
from pathlib import Path
import json
import time
import dotenv

dotenv.load_dotenv()

def save_results_to_csv(file_path: Path, results: list[tuple], headers: str) -> None:
    """Save classification results to a CSV file."""
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(headers)
        for r in results:
            f.write(f'{r[0]}|{r[1]}|{r[2]}\n')

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
    file_path = data_path / file_path
    
    entity_pairs = load_word_pairs(file_path, sheet_name="HS4ConOfE")

# Initialize variables
total_results: list[tuple[str, str, bool]] = []
threshold: float = 0.0

### Entities
m = ContainmentAnalyserGdwg()

start_time = time.time()
total_results = m.compute_relations(entity_pairs)
end_time = time.time()

print(f"Containment Gdwg OpenAI-{os.getenv("MODEL_GDWG")} | {file_name} | Entity pairs | {end_time - start_time} seconds")
save_results_to_csv(
    current_file.parents[0] / f"{file_name}_containment_entity_model_{os.getenv("MODEL_GDWG")}.csv", 
    total_results, 
    "Entity 1 | Entity 2 | Result \n"
)
total_results = []

m = None
### End Entities