import re
import os 
import spacy

from spacy.language import Language
from utilis.keys_us_part import KeyOfUserStoryPart
from utilis.util_functions import return_goal_part, remove_pid_from_text
from dotenv import load_dotenv

SPACY_MODEL_NAME: str = "SPACY_MODEL_NAME"

nlp: Language = None 

def get_nlp() -> Language:    
    global nlp
    if nlp is None:
        load_dotenv()
        nlp = spacy.load(os.getenv(SPACY_MODEL_NAME))
    return nlp

def check_well_formed(user_story_record: dict) -> bool:
    return check_persona_and_target_edges(user_story_record)

def check_atomicity(user_story_record: dict, us_part: KeyOfUserStoryPart = KeyOfUserStoryPart.goal_part) -> bool:
    """
    Input: Plain Json dictionary representing a user story.
    
    Check if the user_story_record is atomic.
    
    Parameters:
    user_story_record (any): The user_story_record to be checked.
    
    Returns:
    bool: True if the user_story_record is atomic, False otherwise.
    """
    actions = set(user_story_record.get(KeyOfUserStoryPart.action.value, {}).get(us_part.value, []))
    entities = set(user_story_record.get(KeyOfUserStoryPart.entity.value, {}).get(us_part.value, []))
    
    targets_data = user_story_record.get(KeyOfUserStoryPart.targets.value, [])
    targets = set(tuple(t) if isinstance(t, list) else t for t in targets_data)
    
    counter = sum(1 for target in targets
                  if isinstance(target, (list, tuple)) and len(target) == 2
                  and target[0] in actions and target[1] in entities)
    return counter == 1
    
def check_minimality(user_story_record: dict, us_part: KeyOfUserStoryPart = KeyOfUserStoryPart.goal_part) -> bool:
    """
    Input: Plain Json dictionary representing a user story.
    
    Check if the user_story_record meets minimality criteria.
    
    Minimality means the Benefit extracted from the Text field matches the stored Benefit field.
    This ensures the benefit part is correctly identified and separated.
    
    Parameters:
        user_story_record (dict): The user_story_record to be checked.
    
    Returns:
        bool: True if benefit extracted from text matches stored benefit, False otherwise.
    """
    text: str = ""
    if us_part == KeyOfUserStoryPart.goal_part:
        text = user_story_record.get(KeyOfUserStoryPart.text.value, "").strip()
        text = return_goal_part(text)
        text = remove_pid_from_text(text)
        text = text.replace("want to", "").replace("want", "").replace("  ", " ").strip() 
    else:
        text = user_story_record.get(KeyOfUserStoryPart.benefit_text.value, "").strip()
        
    return not detect_multiple_clauses(text)["has_multiple_clauses"] 

def check_persona_and_target_edges(user_story_record: dict) -> bool:
    """
    Input: Plain Json dictionary representing a user story.
    
    Check if the user story JSON contains persona and target-edges from primary/secondary parts.
    
    Validates:
    1. Persona exists and is not empty
    2. Target-edges exist from the Primary Action and Primary Entity (primary part)
    3. Target-edges from Secondary Action and Secondary Entity (secondary part) are optional
    
    Parameters:
        user_story_record (dict): The user story record to check.
    
    Returns:
        bool: True if persona and primary target-edges exist, False otherwise.
    """
    personas = user_story_record.get(KeyOfUserStoryPart.persona.value, [])
    if not personas:
        return False
    
    targets = user_story_record.get(KeyOfUserStoryPart.targets.value, [])
    if not targets:
        return False

    action = user_story_record.get(KeyOfUserStoryPart.action.value, {})
    goal_actions = set(action.get(KeyOfUserStoryPart.goal_part.value, [])) if isinstance(action, dict) else set()
    
    entity = user_story_record.get(KeyOfUserStoryPart.entity.value, {})
    goal_entities = set(entity.get(KeyOfUserStoryPart.goal_part.value, [])) if isinstance(entity, dict) else set()
    
    if not goal_actions or not goal_entities:
        return False
    
    for target_edge in targets:
        if isinstance(target_edge, list) and len(target_edge) == 2 \
            and not (target_edge[0] == "" or target_edge[1] == ""):
            # Well-formedness does not depend on the benefit thus it has not to be checked here
            if target_edge[0] in goal_actions and target_edge[1] in goal_entities:
                return True
                
    return False

def detect_multiple_clauses(text: str) -> dict:
    """
    Detect main and subordinate clauses using spaCy dependency parsing.
    
    This function analyzes sentence structure to identify atomicity violations in user stories.
    It uses Universal Dependencies to classify verbs and their grammatical relationships.
    
    **Dependency Tags Used:**
    - ROOT: Main verb of the sentence (primary action)
    - acl: Adjectival clause (e.g., "the user who is logged in")
    - relcl: Relative clause (e.g., "the system that validates data")
    - advcl: Adverbial clause (e.g., "when the user clicks submit")
    - ccomp: Clausal complement (e.g., "I want [to login]")
    - xcomp: Open clausal complement (e.g., "I want [to be able to login]")
    
    **Examples:**
    
    Atomic (Good):
        "I want to login"
        → main_verbs: ["login"], subordinate_verbs: []
        → has_multiple_clauses: False ✓
    
    Non-Atomic (Bad - Conjunction):
        "I want to login and access my profile"
        → main_verbs: ["login", "access"], subordinate_verbs: []
        → has_multiple_clauses: True ✗
    
    Non-Atomic (Bad - Subordinate clause):
        "I want to login so that I can see my dashboard"
        → main_verbs: ["login"], subordinate_verbs: [("see", "advcl")]
        → has_multiple_clauses: True ✗
    
    Parameters:
        text (str): The user story text to analyze (typically the goal or benefit part).
    
    Returns:
        dict: Contains:
            - has_multiple_clauses (bool): True if multiple verbs/clauses detected
            - main_verb_count (int): Number of main verbs (ROOT dependency)
            - sub_verb_count (int): Number of subordinate verbs
            - main_verbs (list): List of main verb texts
            - subordinate_verbs (list): List of (verb_text, dependency_type) tuples
    """
    doc = get_nlp()(text)
    
    main_verbs: list[str] = []
    sub_verbs: list[tuple[str, str]] = []
    
    for token in doc:
        if token.pos_ == "VERB":
            # Main clause verb
            if token.dep_ == "ROOT":
                main_verbs.append(token.text)
            # Subordinate clause verbs
            elif token.dep_ in ("acl", "relcl", "advcl", "ccomp", "xcomp", "conj"):
                sub_verbs.append((token.text, token.dep_))
    
    return {
        "has_multiple_clauses": len(main_verbs) > 1 or len(sub_verbs) > 0,
        "main_verb_count": len(main_verbs),
        "sub_verb_count": len(sub_verbs),
        "main_verbs": main_verbs,
        "subordinate_verbs": sub_verbs
    }