import json
import pandas as pd
import sys
import re

def convert_json_to_excel(json_file, output_file):
    """
    Convert JSON user story data to CSV with Goal-Action and Benefit-Action columns.
    Uses | as delimiter.
    """
    
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    rows = []
    
    for story in data:
        text = story.get('Text', '')
        text = re.sub(r'#G\d+#\s*', '', text).strip()
        
        row = {
            'User Story Text': text,
            'Persona': ', '.join(story.get('Persona', [])),
        }
        
        primary_actions = story.get('Action', {}).get('Primary Action', [])
        secondary_actions = story.get('Action', {}).get('Secondary Action', [])
        primary_entities = story.get('Entity', {}).get('Primary Entity', [])
        secondary_entities = story.get('Entity', {}).get('Secondary Entity', [])
        
        targets = story.get('Targets', [])
        
        goal_pairs = []
        benefit_pairs = []
        
        for target in targets:
            if len(target) >= 2:
                activity = target[0]
                entity = target[1]
                
                # Determine if this is Goal (Primary) or Benefit (Secondary)
                is_primary = activity in primary_actions and entity in primary_entities
                is_secondary = activity in secondary_actions and entity in secondary_entities
                
                if is_primary:
                    goal_pairs.append((activity, entity))
                elif is_secondary:
                    benefit_pairs.append((activity, entity))
                else:
                    # Fallback: just continue
                    continue
        
        for idx, (activity, entity) in enumerate(goal_pairs):
            if idx == 0:
                row['Goal Activity'] = activity
                row['Goal Entity'] = entity
            else:
                row[f'Goal Activity {idx + 1}'] = activity
                row[f'Goal Entity {idx + 1}'] = entity
        
        if not goal_pairs:
            row['Goal Activity'] = ''
            row['Goal Entity'] = ''
        
        for idx, (activity, entity) in enumerate(benefit_pairs):
            if idx == 0:
                row['Benefit Activity'] = activity
                row['Benefit Entity'] = entity
            else:
                row[f'Benefit Activity {idx + 1}'] = activity
                row[f'Benefit Entity {idx + 1}'] = entity
        
        if not benefit_pairs:
            row['Benefit Activity'] = ''
            row['Benefit Entity'] = ''
        
        rows.append(row)
    
    
    df = pd.DataFrame(rows)
    columns_order = ['User Story Text', 'Persona']
    
    # Add goal columns in order
    for i in range(1, 100):  # Support up to 99 goal pairs
        if f'Goal Activity {i}' in df.columns or i == 1:
            if i == 1:
                columns_order.extend(['Goal Activity', 'Goal Entity'])
            else:
                if f'Goal Activity {i}' in df.columns:
                    columns_order.extend([f'Goal Activity {i}', f'Goal Entity {i}'])
    
    # Add benefit columns in order
    for i in range(1, 100):  # Support up to 99 benefit pairs
        if f'Benefit Activity {i}' in df.columns or i == 1:
            if i == 1:
                columns_order.extend(['Benefit Activity', 'Benefit Entity'])
            else:
                if f'Benefit Activity {i}' in df.columns:
                    columns_order.extend([f'Benefit Activity {i}', f'Benefit Entity {i}'])
    

    columns_order = [col for col in columns_order if col in df.columns]
    df = df[columns_order]
    df.to_csv(output_file, sep='|', index=False, encoding='utf-8')
    
    print(f"CSV file created: {output_file}")
    print(f"Total rows: {len(df)}")


if __name__ == "__main__":
    #if len(sys.argv) < 2:
    #    print("Usage: python json_to_csv_converter.py <input_json_file> [output_csv_file]")
    #    sys.exit(1)
    
    arg_one = r"D:\_Projects\_myProjects\dependencyanalyseandsynergyofuserstories\Datasets\elaborated_ground_truth\datasets\annotated\g03_baseline.json"
    arg_two = r"D:\_Projects\_myProjects\dependencyanalyseandsynergyofuserstories\Datasets\elaborated_ground_truth\datasets\annotated\extracted_informations\g03_baseline.csv"
    
    input_file = arg_one # sys.argv[1]
    output_file = arg_two # sys.argv[2] if len(sys.argv) > 2 else input_file.replace('.json', '.csv')

    try:
        convert_json_to_excel(input_file, output_file)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
        
    # --- G08 Baseline Example Paths --- #

    arg_one = r"D:\_Projects\_myProjects\dependencyanalyseandsynergyofuserstories\Datasets\elaborated_ground_truth\datasets\annotated\g08_baseline.json"
    arg_two = r"D:\_Projects\_myProjects\dependencyanalyseandsynergyofuserstories\Datasets\elaborated_ground_truth\datasets\annotated\extracted_informations\g08_baseline.csv"

    input_file = arg_one # sys.argv[1]
    output_file = arg_two # sys.argv[2] if len(sys.argv) > 2 else input_file.replace('.json', '_split_edges.csv')
    
    try:
        convert_json_to_excel(input_file, output_file)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
        
    # --- G17 Baseline Example Paths --- #

    arg_one = r"D:\_Projects\_myProjects\dependencyanalyseandsynergyofuserstories\Datasets\elaborated_ground_truth\datasets\annotated\g17_baseline.json"
    arg_two = r"D:\_Projects\_myProjects\dependencyanalyseandsynergyofuserstories\Datasets\elaborated_ground_truth\datasets\annotated\extracted_informations\g17_baseline.csv"

    input_file = arg_one # sys.argv[1]
    output_file = arg_two # sys.argv[2] if len(sys.argv) > 2 else input_file.replace('.json', '_split_edges.csv')
    
    try:
        convert_json_to_excel(input_file, output_file)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
        
    # --- G22 Baseline Example Paths --- #

    arg_one = r"D:\_Projects\_myProjects\dependencyanalyseandsynergyofuserstories\Datasets\elaborated_ground_truth\datasets\annotated\g22_baseline.json"
    arg_two = r"D:\_Projects\_myProjects\dependencyanalyseandsynergyofuserstories\Datasets\elaborated_ground_truth\datasets\annotated\extracted_informations\g22_baseline.csv"

    input_file = arg_one
    output_file = arg_two #
    
    try:
        convert_json_to_excel(input_file, output_file)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)