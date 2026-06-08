import json
from pathlib import Path
from _lemmatize import strip_lowercase_lemmatize_word

def lemmatize_list(items):
    """Lemmatize a list of strings"""
    if not isinstance(items, list):
        return items
    return [strip_lowercase_lemmatize_word(item) if isinstance(item, str) else item for item in items]

def lemmatize_pairs(pairs):
    """Lemmatize pairs of strings (2D list)"""
    if not isinstance(pairs, list):
        return pairs
    result = []
    for pair in pairs:
        if isinstance(pair, list) and len(pair) == 2:
            lemmatized_pair = [
                strip_lowercase_lemmatize_word(pair[0]) if isinstance(pair[0], str) else pair[0],
                strip_lowercase_lemmatize_word(pair[1]) if isinstance(pair[1], str) else pair[1]
            ]
            result.append(lemmatized_pair)
        else:
            result.append(pair)
    return result

def lemmatize_record(record):
    """Lemmatize all text fields in a user story record"""
    lemmatized = record.copy()
    
    # Lemmatize Persona
    if 'Persona' in lemmatized:
        lemmatized['Persona'] = lemmatize_list(lemmatized['Persona'])
    
    # Lemmatize Action (goal and benefit)
    if 'Action' in lemmatized and isinstance(lemmatized['Action'], dict):
        if 'goal' in lemmatized['Action']:
            lemmatized['Action']['goal'] = lemmatize_list(lemmatized['Action']['goal'])
        if 'benefit' in lemmatized['Action']:
            lemmatized['Action']['benefit'] = lemmatize_list(lemmatized['Action']['benefit'])
    
    # Lemmatize Entity (goal and benefit)
    if 'Entity' in lemmatized and isinstance(lemmatized['Entity'], dict):
        if 'goal' in lemmatized['Entity']:
            lemmatized['Entity']['goal'] = lemmatize_list(lemmatized['Entity']['goal'])
        if 'benefit' in lemmatized['Entity']:
            lemmatized['Entity']['benefit'] = lemmatize_list(lemmatized['Entity']['benefit'])
    
    # Lemmatize Benefit text
    if 'Benefit' in lemmatized and isinstance(lemmatized['Benefit'], str):
        lemmatized['Benefit'] = strip_lowercase_lemmatize_word(lemmatized['Benefit'])
    
    # Lemmatize Triggers (pairs)
    if 'Triggers' in lemmatized:
        lemmatized['Triggers'] = lemmatize_pairs(lemmatized['Triggers'])
    
    # Lemmatize Targets (pairs)
    if 'Targets' in lemmatized:
        lemmatized['Targets'] = lemmatize_pairs(lemmatized['Targets'])
    
    # Lemmatize Contains (pairs)
    if 'Contains' in lemmatized:
        lemmatized['Contains'] = lemmatize_pairs(lemmatized['Contains'])
    
    return lemmatized

def lemmatize_json_file(input_file, output_file=None):
    """
    Load JSON file, lemmatize all records, and save output
    
    Args:
        input_file: Path to input JSON file
        output_file: Path to output JSON file (optional)
    
    Returns:
        List of lemmatized records
    """
    
    # Load JSON
    with open(input_file, 'r', encoding='utf-8') as f:
        records = json.load(f)
    
    print(f"Loaded {len(records)} records from {input_file}")
    
    # Lemmatize each record
    lemmatized_records = []
    for idx, record in enumerate(records):
        lemmatized_record = lemmatize_record(record)
        lemmatized_records.append(lemmatized_record)
        
        if (idx + 1) % 10 == 0:
            print(f"Lemmatized {idx + 1}/{len(records)} records...")
    
    # Save output if path provided
    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(lemmatized_records, f, indent=2, ensure_ascii=False)
        print(f"Lemmatized records saved to {output_file}")
    
    return lemmatized_records

def print_sample_record(records, index=0):
    """Print a sample lemmatized record for verification"""
    if index < len(records):
        print("\n" + "="*60)
        print(f"SAMPLE RECORD (Index {index}):")
        print("="*60)
        print(json.dumps(records[index], indent=2, ensure_ascii=False))
        print("="*60)

if __name__ == "__main__":
    # Interactive mode
    input_file = input("Enter path to JSON file: ").strip()
    
    if not Path(input_file).exists():
        print(f"File not found: {input_file}")
        exit(1)
    
    save_output = input("Save lemmatized JSON? (y/n, default: y): ").strip().lower()
    output_file = None
    if save_output != 'n':
        # Create output file in same directory as input with '_lemmatized' suffix
        input_path = Path(input_file)
        output_file = input_path.parent / input_path.name.replace('.json', '_lemmatized.json')
        output_file = str(output_file)
    
    # Lemmatize
    records = lemmatize_json_file(input_file, output_file)