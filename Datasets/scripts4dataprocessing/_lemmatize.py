import spacy
import sys

nlp: spacy.Language = None

try:
    nlp = spacy.load("en_core_web_trf")
except OSError:
    print("spaCy model not found. Installing en_core_web_trf...")
    import subprocess
    subprocess.run([sys.executable, "-m", "spacy", "download", "en_core_web_trf"], check=True)
    nlp = spacy.load("en_core_web_trf")

lemma_cache = {}

def strip_lowercase_lemmatize_word(text: str) -> str:
    """Lemmatize and lowercase text using spaCy with caching, Lookups, and transformer fallback."""
    global nlp, lemma_cache
    
    if not text:
        return text
    
    text_striped_lower: str = text.strip()
    text_striped_lower = text_striped_lower.lower()
    
    if text_striped_lower in lemma_cache:
        return lemma_cache[text_striped_lower]
    
    doc = nlp(text_striped_lower)
    lemmatized_tokens: list[str] = []
    
    for token in doc:
        lemma: str = token.lemma_        
        lemmatized_tokens.append(lemma)
    
    lemmatized = ' '.join(lemmatized_tokens)
    lemma_cache[text_striped_lower] = lemmatized
    
    return lemmatized

# print(strip_lowercase_lemmatize_word("mice")) #--> mouse
# print(strip_lowercase_lemmatize_word("running")) #--> run
# print(strip_lowercase_lemmatize_word("better")) #--> good
# print(strip_lowercase_lemmatize_word("geese")) #--> goose