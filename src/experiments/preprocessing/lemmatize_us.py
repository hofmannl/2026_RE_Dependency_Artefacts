import json
from pathlib import Path
from utilis.keys_us_part import KeyOfUserStoryPart
from preprocessing_piplines.lemmatizing.lemmatize import lemmatize_single_word

def lemmatize_user_story_graph(user_story_records: list[dict]) -> list[dict]:
    for user_story_record in user_story_records:
        temp: list[str] = []
        local_temp: list[str] = []
        
        for persona in user_story_record.get(KeyOfUserStoryPart.persona.value, []):
            temp.append(
                " ".join(lemmatize_single_word(word) for word in persona.split()).strip()
            )
            
        user_story_record[KeyOfUserStoryPart.persona.value] = temp
        temp = []
        
        for key in [KeyOfUserStoryPart.action.value, KeyOfUserStoryPart.entity.value]:
            for part in [KeyOfUserStoryPart.goal_part.value, KeyOfUserStoryPart.benefit_part.value]:
                for item in user_story_record.get(key, []).get(part, []):
                    
                    temp.append(
                        " ".join(lemmatize_single_word(word) for word in item.split()).strip()
                    )           
                user_story_record[key][part] = temp
                temp = []
            
        for key in [KeyOfUserStoryPart.triggers.value, KeyOfUserStoryPart.targets.value, KeyOfUserStoryPart.contains.value]:
            for _ in user_story_record.get(key, []):
                local_temp = []
                for item in _:
                    local_temp.append(
                        " ".join(lemmatize_single_word(word) for word in item.split()).strip()
                    )
                temp.append(local_temp)
            user_story_record[key] = temp
            temp = []
    
    return user_story_records

current_file = Path(__file__).resolve()
data_path = current_file.parents[1] / "_data" / "improved_data"

file_name: str = input("Enter the filename (without extension) to process lemmatize annotated User Stories: ") 
file_name = file_name.strip()
file_path: str = f"{file_name}.json" if not file_name.endswith(".json") else file_name

us_data: list[dict] = []
with open(data_path / file_path, "r", encoding="utf-8") as f:
    temp: str = ""
    for line in f:
        temp += line
    us_data = json.loads(temp)
    
us_quality_issues: list[dict] = []
processed_us = lemmatize_user_story_graph(us_data)

output_file = current_file.parent / f"{file_name}_lemmatized.json"
with open(output_file, "w", encoding="utf-8") as f:
    f.write(json.dumps(processed_us, indent=4))