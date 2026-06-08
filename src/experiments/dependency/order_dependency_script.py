import json
from pathlib import Path
import sys
from computation_of_dependencies.order_dependencies import OrderDependencies
from experiments.dependency.utils import save_results_to_csv
from relationship_analysers_classifier.crud_classifier.crud_actions import CrudAction
from utilis.dataclasses_user_story import AtomicUserStoryRecord
import time 

calculator = OrderDependencies()

path_to_user_stories =  r"D:\_Projects\_myProjects\dependencyanalyseandsynergyofuserstories\src\experiments\_data\pre_computed_pairs_data\json_us\sim02_baseline_lemmatized.json"

path_to_equivalence_relations = r"D:\_Projects\_myProjects\dependencyanalyseandsynergyofuserstories\src\experiments\_data\pre_computed_pairs_data\llm_resuts_gpt_5_2\sy_results\sim02.xlsx_semantic_equivalence_entity_model_openai_gpt-5.2-2025-12-11.csv"

path_to_containment_relations = r"D:\_Projects\_myProjects\dependencyanalyseandsynergyofuserstories\src\experiments\_data\pre_computed_pairs_data\llm_resuts_gpt_5_2\sy_results\sim02.xlsx_containment_entity_model_openai_gpt-5.2-2025-12-11.csv"

path_to_crud = r"D:\_Projects\_myProjects\dependencyanalyseandsynergyofuserstories\src\experiments\_data\pre_computed_pairs_data\results_crud\results_gdwg\sim02_baseline.json_crud_classification_openai-gpt-oss-120b_word_results.csv"

path_to_crud = Path(path_to_crud)

def mapping_crud__to_user_story_record(
    mapping: list[tuple[str, str, str]],
    list_of_user_stories: list[AtomicUserStoryRecord]
) -> None:
    for us in list_of_user_stories:
        for m in mapping:
            if m[0] in us.story or us.goal_target.src.named_element == m[1]:
                if m[2].lower().strip() == "c" or m[2].lower().strip() == "create":
                    us.goal_action_crud = CrudAction.CREATE
                elif m[2].lower().strip() == "r" or m[2].lower().strip() == "read":
                    us.goal_action_crud = CrudAction.READ
                elif m[2].lower().strip() == "u" or m[2].lower().strip() == "update":
                    us.goal_action_crud = CrudAction.UPDATE
                elif m[2].lower().strip() == "d" or m[2].lower().strip() == "delete":
                    us.goal_action_crud = CrudAction.DELETE
                else:
                    raise ValueError(f"Invalid CRUD action '{m[1]}' in mapping. Expected one of 'c', 'r', 'u', 'd' or their full forms.")
            
user_stories: list[AtomicUserStoryRecord] = []
with open(path_to_user_stories, 'r') as f:
    data = json.load(f)
    for us in data:
        story_record = AtomicUserStoryRecord.factory_direct_import(us)
        user_stories.append(story_record)    

crud_mappings: list[tuple[str, str, str]] = []
with open(path_to_crud, 'r') as f:
    next(f)  # Skip header
    for line in f:
        parts = line.strip().split('|')
        crud_mappings.append((parts[0], parts[1], parts[2]))
        
mapping_crud__to_user_story_record(crud_mappings, user_stories)

breaking_point: int = 0

for us in user_stories:
    if us.goal_target.trg.named_element == "":
        print(f"Warning Empty named_element: '{us.story}'.")
        breaking_point += 1
        
if breaking_point > 0:
    sys.exit(f"Error: Found {breaking_point} user stories with empty named_element. Please fix the data and try again.")

equivalence_relations: list[tuple[str, str, bool]] = []
with open(path_to_equivalence_relations, 'r') as f:
    next(f)  # Skip header
    for line in f:
        parts = line.strip().split('|')
        equivalence_relations.append((parts[0], parts[1], (parts[2].lower().strip() == '1' or parts[2].lower().strip() == 'true')))
        
containment_relations: list[tuple[str, str, bool]] = []
with open(path_to_containment_relations, 'r') as f:
    next(f)  # Skip header
    for line in f:
        parts = line.strip().split('|')
        containment_relations.append((parts[0], parts[1], (parts[2].lower().strip() == '1' or parts[2].lower().strip() == 'true')))
        
new_time = time.time()
dependencies = calculator.order_dependencies(us_data=user_stories, equivalence_relations=equivalence_relations)
print(f"Order Dependency Compute time was: {-1*(new_time - time.time())}")
save_results_to_csv(Path(__file__).parent / "order_dependencies.csv", dependencies)

new_time = time.time()
hierarchical_dependencies = calculator.hierarchical_order_dependencies(us_data=user_stories, containment_relations=containment_relations)
print(f"Hierarchical Dependency Compute time was: {-1*(new_time - time.time())}")
save_results_to_csv(Path(__file__).parent / "hierarchical_order_dependencies.csv", hierarchical_dependencies)