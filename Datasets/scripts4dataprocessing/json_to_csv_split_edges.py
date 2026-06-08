import json
import pandas as pd
import sys
import re
from _lemmatize import strip_lowercase_lemmatize_word

def convert_json_to_csv_split_edges(json_file, output_file):
    """
    Convert JSON user story data to CSV with one row per target-edge (Goal + Benefit combined).
    Each edge gets its own row with IDs for tracking.
    """
    
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    rows: list[dict] = []
    edge_counter_goal: int = 1
    edge_counter_benefit: int = 1
    
    for original_usid, story in enumerate(data, start=1):
        # Clean the text by removing PID prefix (#G### pattern)
        text = story.get('Text', '')
        text = re.sub(r'#G\d+#\s*', '', text).strip()
        
        
        persona = ', '.join(story.get('Persona', [])).lower()
        
        # Get Action and Entity info to classify targets
        primary_actions = story.get('Action', {}).get('Primary Action', [])
        secondary_actions = story.get('Action', {}).get('Secondary Action', [])
        primary_entities = story.get('Entity', {}).get('Primary Entity', [])
        secondary_entities = story.get('Entity', {}).get('Secondary Entity', [])
        
        targets = story.get('Targets', [])
        
        if not targets:
            row = {
                'Ref_Original_USID': original_usid,
                'USID': edge_counter_goal,
                'User Story Text': text,
                'Persona': persona,
                'Activity': '',
                'Entity': '',
            }
            rows.append(row)
        else:
            # Create a row for each target pair
            for target in targets:
                if len(target) >= 2:
                    activity = target[0]
                    entity = target[1]
        
                    activity_lemma = strip_lowercase_lemmatize_word(activity)
                    entity_lemma = strip_lowercase_lemmatize_word(entity)
                    
                    # Determine if this is Goal (Primary) or Benefit (Secondary)
                    is_primary = activity in primary_actions and entity in primary_entities
                    is_secondary = activity in secondary_actions and entity in secondary_entities
                    
                    part: str = ''
                    if is_primary:
                        part = 'Goal'
                    elif is_secondary:
                        part = 'Benefit'
                    else:
                        continue
                    
                    pattern = r"^(.*?)(,?\s*(so that.*))$"
                    match = re.match(pattern, text, flags=re.IGNORECASE)

                    lc_text: str = None
                    if part == 'Goal' and match:
                        lc_text = f"{match.group(1).strip()}."
                    elif part == 'Benefit' and match:
                        if match.group(2).startswith(','):
                            lc_text = f"{match.group(2).strip().lstrip(',')}"
                        else:
                            lc_text = f"{match.group(2).strip()}"

                    row: dict[str, str] = {
                        'Ref Original USID': original_usid,
                        'USID': f"G-{edge_counter_goal}" if part == 'Goal' else f"B-{edge_counter_benefit}",
                        'User Story Text': lc_text if lc_text else text,
                        'Persona': persona,
                        'Activity': activity_lemma,
                        'Entity': entity_lemma,
                        'Type': part,
                    }
                    
                    rows.append(row)
                    if part == 'Goal':
                        edge_counter_goal += 1
                    else:
                        edge_counter_benefit += 1

    df = pd.DataFrame(rows) 
    columns_order = ['Ref Original USID', 'USID', 'User Story Text', 'Persona', 'Activity', 'Entity', 'Type']
    df = df[columns_order]
    df.to_csv(output_file, sep='|', index=False, encoding='utf-8')
    
    print(f"CSV file created: {output_file}")
    print(f"Total rows: {len(df)}")


if __name__ == "__main__":
    # if len(sys.argv) < 2:
    #     print("Usage: python json_to_csv_split_edges.py <input_json_file> [output_csv_file]")
    #     sys.exit(1)
    
    # --- G03 Baseline Example Paths --- #
    
    arg_one = r"D:\_Projects\_myProjects\dependencyanalyseandsynergyofuserstories\Datasets\elaborated_ground_truth\datasets\annotated\g03_baseline.json"
    arg_two = r"D:\_Projects\_myProjects\dependencyanalyseandsynergyofuserstories\Datasets\elaborated_ground_truth\datasets\annotated\extracted_informations\g03_baseline_split_edges.csv"
    
    input_file = arg_one # sys.argv[1]
    output_file = arg_two # sys.argv[2] if len(sys.argv) > 2 else input_file.replace('.json', '_split_edges.csv')
    
    try:
        convert_json_to_csv_split_edges(input_file, output_file)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
        
    # --- G08 Baseline Example Paths --- #

    arg_one = r"D:\_Projects\_myProjects\dependencyanalyseandsynergyofuserstories\Datasets\elaborated_ground_truth\datasets\annotated\g08_baseline.json"
    arg_two = r"D:\_Projects\_myProjects\dependencyanalyseandsynergyofuserstories\Datasets\elaborated_ground_truth\datasets\annotated\extracted_informations\g08_baseline_split_edges.csv"

    input_file = arg_one # sys.argv[1]
    output_file = arg_two # sys.argv[2] if len(sys.argv) > 2 else input_file.replace('.json', '_split_edges.csv')
    
    try:
        convert_json_to_csv_split_edges(input_file, output_file)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
        
    # --- G17 Baseline Example Paths --- #

    arg_one = r"D:\_Projects\_myProjects\dependencyanalyseandsynergyofuserstories\Datasets\elaborated_ground_truth\datasets\annotated\g17_baseline.json"
    arg_two = r"D:\_Projects\_myProjects\dependencyanalyseandsynergyofuserstories\Datasets\elaborated_ground_truth\datasets\annotated\extracted_informations\g17_baseline_split_edges.csv"

    input_file = arg_one # sys.argv[1]
    output_file = arg_two # sys.argv[2] if len(sys.argv) > 2 else input_file.replace('.json', '_split_edges.csv')
    
    try:
        convert_json_to_csv_split_edges(input_file, output_file)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
        
    # --- G22 Baseline Example Paths --- #

    arg_one = r"D:\_Projects\_myProjects\dependencyanalyseandsynergyofuserstories\Datasets\elaborated_ground_truth\datasets\annotated\g22_baseline.json"
    arg_two = r"D:\_Projects\_myProjects\dependencyanalyseandsynergyofuserstories\Datasets\elaborated_ground_truth\datasets\annotated\extracted_informations\g22_baseline_split_edges.csv"

    input_file = arg_one
    output_file = arg_two
    
    try:
        convert_json_to_csv_split_edges(input_file, output_file)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)