import re

def return_goal_part(user_story_text: str, user_story_benefit: str = None) -> str:
    """Extract the goal part from a user story text."""
    PATTERN_BENEFIT_PART = r'(?:,\s*)?(?:so\s+that|so|that)\s+.+?\.?$'
    
    if not re.search(PATTERN_BENEFIT_PART, user_story_text, flags=re.IGNORECASE) and user_story_benefit is None:
        if not user_story_text.endswith('.'):
            user_story_text += '.'
        return user_story_text.strip()
    
    goal_part = re.sub(r'(?:,\s*)?(?:so\s+that|so|that)\s+.+?\.?$', '', user_story_text, flags=re.IGNORECASE).strip()
    goal_part = goal_part.strip()
    
        
    if user_story_benefit is not None and user_story_benefit.strip() in goal_part:
        goal_part = goal_part.replace(user_story_benefit, '').strip()
        if goal_part.endswith(',') or goal_part.endswith('.'):
            goal_part = goal_part[:-1].strip()
    
    if not goal_part.endswith('.'):
        goal_part += '.'  
    
    return goal_part

def remove_pid_from_text(user_story_text: str) -> str:
    """Remove PID from the user story text."""
    PATTERN_PID = r'^\s*#G\d{2,}#\s*'
    cleaned_text = re.sub(PATTERN_PID, '', user_story_text).strip()
    return cleaned_text

VOWELS = "aeiou"
def get_article(word: str) -> str:
    """
    Determine the correct article (a or an) based on the word's first letter.
    
    Args:
        word: The word to determine the article for
        
    Returns:
        str: "a" or "an"
    """
    global VOWELS
    if word and word[0].lower() in VOWELS:
        return "an"
    return "a"