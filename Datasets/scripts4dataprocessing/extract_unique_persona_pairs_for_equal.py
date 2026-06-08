import json
import pandas as pd
import sys
import itertools
from _lemmatize import strip_lowercase_lemmatize_word

def extract_unique_persona_pairs(json_file, output_file):
    """
    Extract all unique pairs of personas from user stories.
    Each pair is represented only once (e.g., A|B and B|A are the same pair).
    """
    
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    all_personas: set[str] = set()
    
    def collect_personas(all_personas: set[str]=all_personas, data: list[dict]=data) -> None:
        lc_persona: str = None
        for story in data:
            personas = story.get('Persona', [])
            for persona in personas:
                if persona:
                    lc_persona = persona.strip()
                    lc_persona = strip_lowercase_lemmatize_word(lc_persona)
                    all_personas.add(lc_persona)
    collect_personas()  
    
    # generates unique pairs like A|A, A|B, A|C, B|B, B|C, C|C 
    # each pair appears only once (no duplicates, no swapped versions like B|A)
    persona_pairs = list(
        itertools.combinations_with_replacement(
                all_personas,
                2
            )
        )
    
    # persona_story_count: dict[str, int] = {}
    # for story in data:
    #     personas = story.get('Persona', [])
    #     for persona in personas:
    #         if persona:
    #             lc_persona = strip_lowercase_lemmatize_word(persona.strip())
    #             persona_story_count[lc_persona] = persona_story_count.get(lc_persona, 0) + 1

    # appear_only_once: list[str] = [persona for persona, count in persona_story_count.items() if count == 1]

    # persona_pairs = [
    #     (p1, p2)
    #     for (p1, p2) in persona_pairs
    #     if not (p1 == p2 and p1 in appear_only_once)
    # ]
    
    real_appearances: set[tuple[str,str]] = set()
    for pair in persona_pairs:
        for story1 in data:
            for story2 in data:
                personas1 = story1.get('Persona', [])
                personas2 = story2.get('Persona', [])
                for persona1 in personas1:
                    for persona2 in personas2:
                        if persona1 and persona2:
                            # the lemmatization is still fast here as we cache results in _lemmatize.py
                            lemmatized1 = strip_lowercase_lemmatize_word(persona1)
                            lemmatized2 = strip_lowercase_lemmatize_word(persona2)
                            # check if this pair matches the current unique pair (in any order)
                            if (lemmatized1 == pair[0] and lemmatized2 == pair[1]) or \
                                    (lemmatized1 == pair[1] and lemmatized2 == pair[0]):
                                real_appearances.add(pair)
                                
    unique_pairs = sorted(list(real_appearances))    
    
    df: pd.DataFrame = pd.DataFrame(persona_pairs, columns=['Persona 1', 'Persona 2'])
    df.to_csv(output_file, index=False, encoding='utf-8', sep='|')
    
    print(f"CSV file created: {output_file}")
    print(f"Total unique personas: {len(all_personas)}")
    print(f"Total persona pairs: {len(persona_pairs)}")


if __name__ == "__main__":
    print("Starting persona pairs extraction...")
    # if len(sys.argv) < 2:
    #     print("Usage: python extract_persona_pairs.py <input_json_file> [output_csv_file]")
    #     sys.exit(1)

    arg_one = r"D:\_Projects\_myProjects\dependencyanalyseandsynergyofuserstories\Datasets\elaborated_ground_truth\datasets\annotated\g03_baseline.json"
    arg_two = r"D:\_Projects\_myProjects\dependencyanalyseandsynergyofuserstories\Datasets\elaborated_ground_truth\datasets\annotated\extracted_informations\g03_baseline_unique_persona_pairs.csv"

    input_file = arg_one # sys.argv[1]
    output_file = arg_two # sys.argv[2] if len(sys.argv) > 2 else input_file.replace('.json', '_persona_pairs.csv')
    
    try:
        extract_unique_persona_pairs(input_file, output_file)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

    # --- G08 Baseline Example Paths --- #

    arg_one = r"D:\_Projects\_myProjects\dependencyanalyseandsynergyofuserstories\Datasets\elaborated_ground_truth\datasets\annotated\g08_baseline.json"
    arg_two = r"D:\_Projects\_myProjects\dependencyanalyseandsynergyofuserstories\Datasets\elaborated_ground_truth\datasets\annotated\extracted_informations\g08_baseline_unique_persona_pairs.csv"

    input_file = arg_one # sys.argv[1]
    output_file = arg_two # sys.argv[2] if len(sys.argv) > 2 else input_file.replace('.json', '_split_edges.csv')
    
    try:
        extract_unique_persona_pairs(input_file, output_file)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
        
    # --- G17 Baseline Example Paths --- #

    arg_one = r"D:\_Projects\_myProjects\dependencyanalyseandsynergyofuserstories\Datasets\elaborated_ground_truth\datasets\annotated\g17_baseline.json"
    arg_two = r"D:\_Projects\_myProjects\dependencyanalyseandsynergyofuserstories\Datasets\elaborated_ground_truth\datasets\annotated\extracted_informations\g17_baseline_unique_persona_pairs.csv"

    input_file = arg_one # sys.argv[1]
    output_file = arg_two # sys.argv[2] if len(sys.argv) > 2 else input_file.replace('.json', '_split_edges.csv')
    
    try:
        extract_unique_persona_pairs(input_file, output_file)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
        
    # --- G22 Baseline Example Paths --- #

    arg_one = r"D:\_Projects\_myProjects\dependencyanalyseandsynergyofuserstories\Datasets\elaborated_ground_truth\datasets\annotated\g22_baseline.json"
    arg_two = r"D:\_Projects\_myProjects\dependencyanalyseandsynergyofuserstories\Datasets\elaborated_ground_truth\datasets\annotated\extracted_informations\g22_baseline_unique_persona_pairs.csv"

    input_file = arg_one
    output_file = arg_two #
    
    try:
        extract_unique_persona_pairs(input_file, output_file)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)