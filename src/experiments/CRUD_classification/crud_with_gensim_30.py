# Just the Word (Create, Read, Update, Delete) classification

from relationship_analysers_classifier.crud_classifier.gensim_word2vec_similarity import GensimWord2VecCRUDClassifier
from relationship_analysers_classifier.crud_classifier.crud_actions import CrudAction
from utilis.dataclasses_user_story import AtomicUserStoryRecord
from pathlib import Path
import json
import time

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

m: GensimWord2VecCRUDClassifier = GensimWord2VecCRUDClassifier(bag_of_words_size=30)

### Warm up
for story in stories:
    action = story.goal_action.named_element
    result = m.classify(action)

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
print(f"Gensim | {file_name} | Mode 30 words with action | {end_time - start_time} seconds")

with open(current_file.parents[0] / f"{file_name}_crud_classification_gensim_30_words_results.csv", "w", encoding="utf-8") as f:
    f.write("story|action|classified_action|similarity\n")
    for r in results:
        f.write(f'{r[0]}|{r[1]}|{r[2].value}|{r[3]}\n')

### With whole sentences
txt: str = ""
results = list()
result = (CrudAction.UNKNOWN, 0.0)
start_time = time.time()
for story in stories:
    text = story.goal
    result = m.classify(text)
    results.append((story.story, story.goal_action.named_element, result[0], result[1]))
end_time = time.time()
print(f"Gensim | {file_name} | Mode 30 words with sentences | {end_time - start_time} seconds")

with open(current_file.parents[0] / f"{file_name}_crud_classification_gensim_30_words_sentence_results.csv", "w", encoding="utf-8") as f:
    f.write("story|action|classified_action|similarity\n")
    for r in results:
        f.write(f'{r[0]}|{r[1]}|{r[2].value}|{r[3]}\n')