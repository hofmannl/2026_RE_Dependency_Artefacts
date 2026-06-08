import json
import pandas as pd
import sys
import itertools

from _lemmatize import strip_lowercase_lemmatize_word

def extract_goal_entity_pairs_pairwise(json_file, output_file):
    """
    Extract all pairwise combinations of entities from the goal part (Primary Entities) of user stories.
    Generates all unique pairs of goal entities.
    Lemmatizes entities.
    """
    
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    all_primary_entities = set()
    for story in data:
        primary_entities = story.get('Entity', {}).get('Primary Entity', [])
        for entity in primary_entities:
            if entity:
                target = story.get('Targets', [])
                if isinstance(target, list) and len(target) >= 1:
                    in_targets: bool = False
                    for t in target:
                        # Check if the primary entity matches any target entity
                        if isinstance(t, list) and len(t) >= 1 and \
                                strip_lowercase_lemmatize_word(t[1]) == strip_lowercase_lemmatize_word(entity):
                            lemmatized = strip_lowercase_lemmatize_word(entity.strip())
                            all_primary_entities.add(lemmatized)
                            in_targets = True
                    if not in_targets:
                        pass
                        # raise Exception(f"Mismatch between Primary Entity '{entity}' and Target Entity '{t[1]}'")
    
    entity_pairs: list[tuple[str,str]] = list(
        itertools.product(
                all_primary_entities,
                all_primary_entities
            )
        )
    
    real_appearances: set[tuple[str,str]] = set()
    for pair in entity_pairs:
        for story1 in data:
            for story2 in data:
                primary_entity1 = story1.get('Entity', {}).get('Primary Entity', [])
                primary_entity2 = story2.get('Entity', {}).get('Primary Entity', [])
                for entity1 in primary_entity1:
                    for entity2 in primary_entity2:
                        if entity1 and entity2:
                            # the lemmatization is still fast here as we cache results in _lemmatize.py
                            lemmatized1 = strip_lowercase_lemmatize_word(entity1)
                            lemmatized2 = strip_lowercase_lemmatize_word(entity2)
                            # check if this pair matches the current unique pair (in any order)
                            if (lemmatized1 == pair[0] and lemmatized2 == pair[1]) or \
                                    (lemmatized1 == pair[1] and lemmatized2 == pair[0]):
                                real_appearances.add(pair)
                                
    entity_pairs = sorted(list(real_appearances))
    
    df = pd.DataFrame(entity_pairs)
    df.to_csv(output_file, index=False, encoding='utf-8', sep='|')
    
    print(f"CSV file created: {output_file}")
    print(f"Total unique goal entities: {len(all_primary_entities)}")
    print(f"Total entity pairs: {len(entity_pairs)}")


if __name__ == "__main__":
    # if len(sys.argv) < 2:
    #     print("Usage: python extract_goal_action_pairs.py <input_json_file> [output_csv_file]")
    #     sys.exit(1)
    
    arg_one = r"D:\_Projects\_myProjects\dependencyanalyseandsynergyofuserstories\Datasets\elaborated_ground_truth\datasets\annotated\g03_baseline.json"
    arg_two = r"D:\_Projects\_myProjects\dependencyanalyseandsynergyofuserstories\Datasets\elaborated_ground_truth\datasets\annotated\extracted_informations\g03_baseline_entity_pairs.csv"

    input_file = arg_one # sys.argv[1]
    output_file = arg_two # sys.argv[2] if len(sys.argv) > 2 else input_file.replace('.json', '_goal_action_pairs.csv')
    
    try:
        extract_goal_entity_pairs_pairwise(input_file, output_file)
    except Exception as e:
        print(f"✗ Error: {e}")
        sys.exit(1)

    # --- G08 Baseline Example Paths --- #

    arg_one = r"D:\_Projects\_myProjects\dependencyanalyseandsynergyofuserstories\Datasets\elaborated_ground_truth\datasets\annotated\g08_baseline.json"
    arg_two = r"D:\_Projects\_myProjects\dependencyanalyseandsynergyofuserstories\Datasets\elaborated_ground_truth\datasets\annotated\extracted_informations\g08_baseline_entity_pairs.csv"

    input_file = arg_one # sys.argv[1]
    output_file = arg_two # sys.argv[2] if len(sys.argv) > 2 else input_file.replace('.json', '_split_edges.csv')
    
    try:
        extract_goal_entity_pairs_pairwise(input_file, output_file)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
        
    # --- G17 Baseline Example Paths --- #

    arg_one = r"D:\_Projects\_myProjects\dependencyanalyseandsynergyofuserstories\Datasets\elaborated_ground_truth\datasets\annotated\g17_baseline.json"
    arg_two = r"D:\_Projects\_myProjects\dependencyanalyseandsynergyofuserstories\Datasets\elaborated_ground_truth\datasets\annotated\extracted_informations\g17_baseline_entity_pairs.csv"

    input_file = arg_one # sys.argv[1]
    output_file = arg_two # sys.argv[2] if len(sys.argv) > 2 else input_file.replace('.json', '_split_edges.csv')
    
    try:
        extract_goal_entity_pairs_pairwise(input_file, output_file)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
        
    # --- G22 Baseline Example Paths --- #

    arg_one = r"D:\_Projects\_myProjects\dependencyanalyseandsynergyofuserstories\Datasets\elaborated_ground_truth\datasets\annotated\g22_baseline.json"
    arg_two = r"D:\_Projects\_myProjects\dependencyanalyseandsynergyofuserstories\Datasets\elaborated_ground_truth\datasets\annotated\extracted_informations\g22_baseline_entity_pairs.csv"

    input_file = arg_one
    output_file = arg_two #
    
    try:
        extract_goal_entity_pairs_pairwise(input_file, output_file)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)