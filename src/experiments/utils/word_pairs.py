from unicodedata import name
from utilis.dataclasses_user_story import AtomicUserStoryRecord
from utilis.keys_us_part import KeyOfUserStoryPart
import itertools


def extract_persona_pairs(
    user_stories: set[AtomicUserStoryRecord],
    unique: bool = False,
    part: KeyOfUserStoryPart = KeyOfUserStoryPart.goal_part
) -> set[tuple[str, str]]:
    temp_result: set[tuple[str, str]] = None

    if unique:
        temp_result = {
            (us1.persona.named_element, us2.persona.named_element)
            for us1, us2 in itertools.combinations_with_replacement(user_stories, 2)
            if us1 != us2
        }
    else:
        temp_result = {
            (us1.persona.named_element, us2.persona.named_element)
            for us1, us2 in itertools.product(user_stories, user_stories)
            if us1 != us2
        }
        
    # for us in user_stories:
    #     persona = us.persona.named_element
    #     if persona is None or persona == "":
    #         print(f"\nUser Story with problematic persona:")
    #         print(f"  ID: {us.story}")
    #         print(f"  Persona: {us.persona.named_element}")
    #         print(f"  Action (None/Empty): {persona}")
            
    # for _ in temp_result:
    #     if _[0] is None or _[1] is None or _[0] == "" or _[1] == "":
    #         print(f"\nProblematic action pair found: {_}")

    return temp_result

def extract_action_pairs(
    user_stories: set[AtomicUserStoryRecord],
    unique: bool = False,
    part: KeyOfUserStoryPart = KeyOfUserStoryPart.goal_part
) -> set[tuple[str, str]]:
    temp_result: set[tuple[AtomicUserStoryRecord, AtomicUserStoryRecord]] = None
    if part == KeyOfUserStoryPart.goal_part:
        if unique:
            temp_result = {
                (us1.goal_target.src.named_element, us2.goal_target.src.named_element)
                for us1, us2 in itertools.combinations_with_replacement(user_stories, 2)
                if us1 != us2
            }
        else:
            temp_result = {
                (us1.goal_target.src.named_element, us2.goal_target.src.named_element)
                for us1, us2 in itertools.product(user_stories, user_stories)
                if us1 != us2
            }
    else:
        if unique:
            temp_result = {
                (us1.benefit_target.src.named_element, us2.benefit_target.src.named_element)
                for us1, us2 in itertools.combinations_with_replacement(user_stories, 2)
                if us1 != us2
            }
        else:
            temp_result = {
                (us1.benefit_target.src.named_element, us2.benefit_target.src.named_element)
                for us1, us2 in itertools.product(user_stories, user_stories)
                if us1 != us2
            }
         
    # for us in user_stories:
    #     action_value = us.goal_target.src.named_element
    #     if action_value is None or action_value == "":
    #         print(f"\nUser Story with problematic action:")
    #         print(f"  ID: {us.story}")
    #         print(f"  Persona: {us.persona.named_element}")
    #         print(f"  Action (None/Empty): {action_value}")
            
    # for _ in temp_result:
    #     if _[0] is None or _[1] is None or _[0] == "" or _[1] == "":
    #         print(f"\nProblematic action pair found: {_}")
    
    return temp_result

def extract_entities_pairs(
    user_stories: set[AtomicUserStoryRecord],
    unique: bool = False,
    part: KeyOfUserStoryPart = KeyOfUserStoryPart.goal_part
) -> set[tuple[str, str]]:
    temp_result: set[tuple[AtomicUserStoryRecord, AtomicUserStoryRecord]] = None
    if part == KeyOfUserStoryPart.goal_part:
        if unique:
            temp_result = {
                (us1.goal_target.trg.named_element, us2.goal_target.trg.named_element)
                for us1, us2 in itertools.combinations_with_replacement(user_stories, 2)
                if us1 != us2
            }
        else:
            temp_result = {
                (us1.goal_target.trg.named_element, us2.goal_target.trg.named_element)
                for us1, us2 in itertools.product(user_stories, user_stories)
                if us1 != us2
            }
    else:
        if unique:
            temp_result = {
                (us1.benefit_target.trg.named_element, us2.benefit_target.trg.named_element)
                for us1, us2 in itertools.combinations_with_replacement(user_stories, 2)
                if us1 != us2
            }
        else:
            temp_result = {
                (us1.benefit_target.trg.named_element, us2.benefit_target.trg.named_element)
                for us1, us2 in itertools.product(user_stories, user_stories)
                if us1 != us2
            }
    
    # for us in user_stories:
    #     entity_value = us.goal_target.trg.named_element
    #     if entity_value is None or entity_value == "":
    #         print(f"\nUser Story with problematic entity:")
    #         print(f"  ID: {us.story}")
    #         print(f"  Persona: {us.persona.named_element}")
    #         print(f"  Action (None/Empty): {entity_value}")
            
    # for _ in temp_result:
    #     if _[0] is None or _[1] is None or _[0] == "" or _[1] == "":
    #         print(f"\nProblematic action pair found: {_}")
    
    
    return temp_result