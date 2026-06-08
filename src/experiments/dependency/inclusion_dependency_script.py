import json
from pathlib import Path
from computation_of_dependencies.inclusion_dependencies import InclusionDependencies
from experiments.dependency.utils import save_results_to_csv
from utilis.dataclasses_user_story import AtomicUserStoryRecord

import time

def import_csv(path: str) -> list[tuple[str, str, str]]:
    result: list[tuple[str, str, str]] = []
    with open(path, 'r') as f:
        next(f)  # Skip header
        for line in f:
            parts = line.strip().split('|')
            result.append((parts[0], parts[1], (parts[2].lower().strip() == '1' or parts[2].lower().strip() == 'true')))
    return result



path_to_persona_generalisation_relations = r"D:\_Projects\_myProjects\dependencyanalyseandsynergyofuserstories\Datasets\elaborated_ground_truth\datasets_elaborated\ground_truth_in_csv\sy_data\Sim02_labeled_HS4GenOfP.csv"
# r"D:\_Projects\_myProjects\dependencyanalyseandsynergyofuserstories\src\experiments\_data\pre_computed_pairs_data\llm_results_gdwg\sy_results\sim02.xlsx_generalization_persona_model_openai-gpt-oss-120b.csv"
# r"D:\_Projects\_myProjects\dependencyanalyseandsynergyofuserstories\Datasets\elaborated_ground_truth\datasets_elaborated\ground_truth_in_csv\sy_data\Sim02_labeled_HS4GenOfP.csv"
persona_generalisation_relations: list[tuple[str, str, bool]] = import_csv(path_to_persona_generalisation_relations)

path_to_persona_equivalence_relations = r"D:\_Projects\_myProjects\dependencyanalyseandsynergyofuserstories\Datasets\elaborated_ground_truth\datasets_elaborated\ground_truth_in_csv\sy_data\Sim02_labeled_HS4SemOfP.csv"
# r"D:\_Projects\_myProjects\dependencyanalyseandsynergyofuserstories\src\experiments\_data\pre_computed_pairs_data\llm_results_gdwg\sy_results\sim02.xlsx_semantic_equivalence_persona_model_openai-gpt-oss-120b.csv"
# r"D:\_Projects\_myProjects\dependencyanalyseandsynergyofuserstories\Datasets\elaborated_ground_truth\datasets_elaborated\ground_truth_in_csv\sy_data\Sim02_labeled_HS4SemOfP.csv"
persona_sematical_equivalence_relations: list[tuple[str, str, bool]] = import_csv(path_to_persona_equivalence_relations)



path_to_action_generalisation_relations = r"D:\_Projects\_myProjects\dependencyanalyseandsynergyofuserstories\Datasets\elaborated_ground_truth\datasets_elaborated\ground_truth_in_csv\sy_data\Sim02_labeled_HS4GenOfA.csv"
# r"D:\_Projects\_myProjects\dependencyanalyseandsynergyofuserstories\src\experiments\_data\pre_computed_pairs_data\llm_results_gdwg\sy_results\sim02.xlsx_generalization_action_model_openai-gpt-oss-120b.csv"
# r"D:\_Projects\_myProjects\dependencyanalyseandsynergyofuserstories\Datasets\elaborated_ground_truth\datasets_elaborated\ground_truth_in_csv\sy_data\Sim02_labeled_HS4GenOfA.csv"
action_generalisation_relations: list[tuple[str, str, bool]] = import_csv(path_to_action_generalisation_relations)

path_to_action_equivalence_relations = r"D:\_Projects\_myProjects\dependencyanalyseandsynergyofuserstories\Datasets\elaborated_ground_truth\datasets_elaborated\ground_truth_in_csv\sy_data\Sim02_labeled_HS4SemOfA.csv"
# r"D:\_Projects\_myProjects\dependencyanalyseandsynergyofuserstories\src\experiments\_data\pre_computed_pairs_data\llm_results_gdwg\sy_results\sim02.xlsx_semantic_equivalence_action_model_openai-gpt-oss-120b.csv"
# r"D:\_Projects\_myProjects\dependencyanalyseandsynergyofuserstories\Datasets\elaborated_ground_truth\datasets_elaborated\ground_truth_in_csv\sy_data\Sim02_labeled_HS4SemOfA.csv"
action_sematical_equivalence_relations: list[tuple[str, str, bool]] = import_csv(path_to_action_equivalence_relations)



path_to_entity_generalisation_relations = r"D:\_Projects\_myProjects\dependencyanalyseandsynergyofuserstories\Datasets\elaborated_ground_truth\datasets_elaborated\ground_truth_in_csv\sy_data\Sim02_labeled_HS4GenOfE.csv"
# r"D:\_Projects\_myProjects\dependencyanalyseandsynergyofuserstories\src\experiments\_data\pre_computed_pairs_data\llm_results_gdwg\sy_results\sim02.xlsx_generalization_entity_model_openai-gpt-oss-120b.csv"
# r"D:\_Projects\_myProjects\dependencyanalyseandsynergyofuserstories\Datasets\elaborated_ground_truth\datasets_elaborated\ground_truth_in_csv\sy_data\Sim02_labeled_HS4GenOfE.csv"
entity_generalisation_relations: list[tuple[str, str, bool]] = import_csv(path_to_entity_generalisation_relations)

path_to_entity_equivalence_relations = r"D:\_Projects\_myProjects\dependencyanalyseandsynergyofuserstories\Datasets\elaborated_ground_truth\datasets_elaborated\ground_truth_in_csv\sy_data\Sim02_labeled_HS4SemOfE.csv"
# r"D:\_Projects\_myProjects\dependencyanalyseandsynergyofuserstories\src\experiments\_data\pre_computed_pairs_data\llm_results_gdwg\sy_results\sim02.xlsx_semantic_equivalence_entity_model_openai-gpt-oss-120b.csv"
# r"D:\_Projects\_myProjects\dependencyanalyseandsynergyofuserstories\Datasets\elaborated_ground_truth\datasets_elaborated\ground_truth_in_csv\sy_data\Sim02_labeled_HS4SemOfE.csv"
entity_sematical_equivalence_relations: list[tuple[str, str, bool]] = import_csv(path_to_entity_equivalence_relations)

path_to_user_stories = r"D:\_Projects\_myProjects\dependencyanalyseandsynergyofuserstories\src\experiments\_data\pre_computed_pairs_data\json_us\sim02_baseline_lemmatized.json"

user_stories: list[AtomicUserStoryRecord] = []
with open(path_to_user_stories, 'r') as f:
    data = json.load(f)
    for us in data:
        story_record = AtomicUserStoryRecord.factory_direct_import(us)
        user_stories.append(story_record)    

new_time = time.time()
calulator = InclusionDependencies()
dependencies = calulator.inclusion_dependencies(
    us_data=user_stories, 
    persona_equivalence_relations=persona_sematical_equivalence_relations,
    persona_specialization_relations=persona_generalisation_relations,
    
    action_equivalence_relations=action_sematical_equivalence_relations,
    action_specialization_relations=action_generalisation_relations,
    
    entity_equivalence_relations=entity_sematical_equivalence_relations,
    entity_specialization_relations=entity_generalisation_relations
)
print(f"The computation costed {(new_time - time.time()) * -1}")

results: list[tuple[str, str]] = []
for _ in dependencies:
    results.append((_[1],_[0]))

save_results_to_csv(
    Path(__file__).parent / "inclusion_dependencies.csv",
    results,
)