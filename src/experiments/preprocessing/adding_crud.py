import json
from pathlib import Path
from relationship_analysers_classifier.crud_classifier.crud_actions import CrudAction
from utilis.keys_us_part import KeyOfUserStoryPart

def add_crud(
        user_story_records: list[dict], 
        mapping: tuple[str, CrudAction]
    ) -> list[dict]:
    for user_story_record in user_story_records:
        text = user_story_record.get(KeyOfUserStoryPart.text.value, "")
        for m in mapping:
            m[0] = m[0].strip().removesuffix(".")
            if text.lower().contains(m[0].lower()):
                user_story_record[KeyOfUserStoryPart.goal_action_crud.value].append(m[1].value)
        
current_file = Path(__file__).resolve()
data_path = current_file.parents[1] / "_data" / "lemmatized_crud_data"

file_name: str = input("Enter the filename (without extension) to process lemmatize annotated User Stories: ") 
file_name = file_name.strip()
file_path: str = f"{file_name}.json" if not file_name.endswith(".json") else file_name

us_data: list[dict] = []
with open(data_path / file_path, "r", encoding="utf-8") as f:
    temp: str = ""
    for line in f:
        temp += line
    us_data = json.loads(temp)
    
file_name: str = input("Enter the mapping ressources (without extension) to add to the jsons: ") 
file_name = file_name.strip()
file_path: str = f"{file_name}.txt" if not file_name.endswith(".txt") else file_name

mappings: list[tuple[str, CrudAction]] = []
with open(current_file.parents[0] / "crud_mappings" + file_path, "r") as f:
    temp: list[str] = []
    for line in f:
        temp = line.split("|")
        temp = [_.strip() for _ in temp]
        if len(temp) == 2:
            mappings.append((temp[0], CrudAction.from_string(temp[1])))
        else: 
            raise ValueError(f"Invalid mapping line: {line}")
    
us_quality_issues: list[dict] = []
processed_us = add_crud(us_data, mappings)

output_file = current_file.parent / f"{file_name}.json"
with open(output_file, "w", encoding="utf-8") as f:
    f.write(json.dumps(processed_us, indent=4))