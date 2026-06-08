from dotenv import load_dotenv
from spacy.pipeline import Lemmatizer
from spacy.language import Language
from spacy.lookups import Lookups, load_lookups

import functools
import spacy
import os

VALID_MODES = {"lookup", "rule", "trainable"}
SPACY_LEMMATIZER_MODE = "SPACY_LEMMATIZER_MODE"
SPACY_LOOKUPS_DATA = "SPACY_LOOKUPS_DATA"
SPACY_MODEL_LEMMATIZATION = "SPACY_MODEL_LEMMATIZATION"
SPACY_LEMMATIZATION_MODEL_IS_CUSTOM = "SPACY_LEMMATIZATION_MODEL_IS_CUSTOM"
SPACY_LEMMATIZATION_MODEL_CUSTOM_MODE_PATH = "SPACY_LEMMATIZATION_MODEL_CUSTOM_MODE_PATH"
SPACY_FUNCTION_CACHE_SIZE = "SPACY_FUNCTION_CACHE_SIZE"
load_dotenv()
    
spacy_model: Language = None
spacy_function_cache_size: int = None
lemmatizer: Lemmatizer = None

try:
    spacy_function_cache_size = (
        int(s) if (s := os.getenv(SPACY_FUNCTION_CACHE_SIZE)) and s.lower() != "none"
        else None
    )
except ValueError:
    spacy_function_cache_size = None

def set_spacy_model():
    # TODO: IMPLEMENT CUSTOM MODEL LOADING
    global spacy_model, lemmatizer
    if not spacy_model:
        spacy_model = spacy.load(str(os.getenv(SPACY_MODEL_LEMMATIZATION)))
    if not lemmatizer:
        lemmatizer_mode = None
        lookups_data = None
        if not ((lookups_data := os.getenv(SPACY_LOOKUPS_DATA)) and lookups_data.lower() != "none"):
            raise ValueError(f"Lookups data is not set or is invalid: {lookups_data}")
        if not ((lemmatizer_mode := os.getenv("SPACY_LEMMATIZER_MODE")) and lemmatizer_mode.lower() in VALID_MODES):
            raise ValueError(f"Lemmatizer mode is not set or invalid: {lemmatizer_mode}")
        lookups: Lookups = load_lookups(
            lookups_data.lower().strip(), 
            tables=["lemma_rules", "lemma_exc", "lemma_index"]
        )
        lemmatizer = Lemmatizer(
            vocab=spacy_model.vocab,
            model=None, # Only needed for trainable lemmatizer
            mode=lemmatizer_mode.lower().strip()
        )
        lemmatizer.lookups = lookups
      
set_spacy_model()

@functools.lru_cache(maxsize=spacy_function_cache_size)
def lemmatize_single_word(word: str) -> str:
    word = word.strip().lower()
    doc = spacy_model(word)
    if doc and len(doc) > 0 and not doc[0].lemma_ == word:
        return doc[0].lemma_
        
    token = doc[0] if doc else spacy_model(word)[0]
    # Check if the token is already in base form
    if (lemmatizer.is_base_form(token=token)):
        return token.text
    
    local_lemma = lemmatizer.rule_lemmatize(token)[0]
    if local_lemma != word:
        return local_lemma
    
    local_lemma = lemmatizer.lookup_lemmatize(token)[0]
    return local_lemma if local_lemma != word else word
    
@functools.lru_cache(maxsize=spacy_function_cache_size)
def lemmatize_context_aware_single_words(words: str) -> dict[str, str]:
    """_summary_

    Args:
        words (str): a string of words separated by semicolon (;) .

    Returns:
        dict[str, str]: the original word as key and its lemma as value.
    """            
    words = words.lower().strip().replace(" ", "")
    original_words = words.split(";")
    doc = spacy_model(" ".join(original_words))
    
    result: dict[str, str] = {}
    token_text: str | None = None
    lemma:str | None = None
    for token in doc:
        token_text = token.text.lower()
        lemma = token.lemma_.lower()
        # If the lemma is the same as the token, we try to lemmatize it again
        # This can happen in cases like running boys where the results is "running" instead of "run"
        if token_text == lemma:
            lemma = lemmatize_single_word(doc[0].text)
        result[token_text] = lemma
    return result

@functools.lru_cache(maxsize=spacy_function_cache_size)
def lemmatize_sentence(sentences: str) -> list[dict[str, str]]:
    """
    Lemmatizes words in one or more sentences, mapping each original word to its lemma.

    Uses spaCy for context-aware lemmatization. If the lemma matches the original word,
    a fallback via `lemmatize_single_word()` is applied for improved accuracy.

    Args:
        sentences (str): One or more input sentences.

    Returns:
        list[dict[str, str]]: A list of dictionaries (one per sentence) mapping
        lowercase words to their lemmas, excluding punctuation and whitespace.
    """
    doc = spacy_model(sentences)
    result = []

    for sent in doc.sents:
        sent_dict = {}
        for token in sent:
            if token.is_punct or token.is_space:
                continue
            text = token.text.lower()
            lemma = token.lemma_.lower()
            if text == lemma:
                lemma = lemmatize_single_word(text)
            sent_dict[text] = lemma
        result.append(sent_dict)
    return result

# print("Lemmatization model and functions initialized.")
# print(lemmatize_sentence("Lemmatization model and functions initialized."))
# print(lemmatize_single_word("running"))
# print(lemmatize_context_aware_single_words("running"))