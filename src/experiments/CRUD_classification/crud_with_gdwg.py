# Just the Word (Create, Read, Update, Delete) classification

import os
from relationship_analysers_classifier.crud_classifier.openai_crud_classifier import CrudAnalyserOpenAI
from relationship_analysers_classifier.crud_classifier.crud_actions import CrudAction
from utilis.dataclasses_user_story import AtomicUserStoryRecord
from pathlib import Path
import json
import time
import dotenv

dotenv.load_dotenv()

current_file = Path(__file__).resolve()
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

m: CrudAnalyserOpenAI = CrudAnalyserOpenAI()

### With single words only
action: str = ""
results: list[tuple[str, str, CrudAction, float]] = list()
result: tuple[CrudAction, float] = (CrudAction.UNKNOWN, 0.0)
start_time = time.time() 
for story in stories:
    action = story.goal_action.named_element
    result = m.classify(action)
    results.append((story.story, action, result[0], result[1]))
end_time = time.time()
print(f"{os.getenv('MODEL_OPENAI')} | {file_name} | Mode 30 word with action | {end_time - start_time} seconds")

with open(current_file.parents[0] / f"{file_name}_crud_classification_{os.getenv("MODEL_OPENAI")}_word_results.csv", "w", encoding="utf-8") as f:
    f.write("story|action|classified_action|similarity\n")
    for r in results:
        f.write(f'{r[0]}|{r[1]}|{r[2].value}|{r[3]}\n')