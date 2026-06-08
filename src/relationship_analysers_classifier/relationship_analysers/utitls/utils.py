from typing import Callable
from openai import OpenAI

from utilis.annotation_graph_components import TypeGraphUs


def clean_element(element: str) -> str:
    return element.strip().lower()


def extract_triple(triple: str, seperator: str = "--") -> tuple[str, str, str]:
    parts = triple.split(seperator)
    if len(parts) != 3:
        return None
    subject, predicate, object_ = parts
    return (clean_element(subject), clean_element(predicate), clean_element(object_))


def extract_triple_elements(triples: str, seperator: str = "--", line_seperator: str = "\n") -> list[tuple[str, str, str]]:
    triples_list: list[tuple[str, str, str]] = []
    temp: tuple[str, str, str] = None 
    for line in triples.split(line_seperator):
        if line.strip(): 
            temp = extract_triple(line, seperator)
            if temp:
                triples_list.append(temp)
    return triples_list

def convert_triples(triples: list[tuple[str, str, str]]) -> list[tuple[str, str, bool]]:
    """Convert third element of triples from string to boolean."""
    return [(triple[0], triple[1], triple[2].lower().strip() in ('true', 'yes', '1')) for triple in triples] 

def detect_and_reprompt_missing_elements(
    batch_results: list[tuple[str, str, bool]], 
    sent_pairs: set[tuple[str, str]], 
    client,
    model: str, 
    top_p: float,
    typ: TypeGraphUs,
    build_prompt_func: Callable,
    seperator: str = "--"
) -> list[tuple[str, str, str]]:
    """
    Detects missing pairs from LLM response and retries once.
    Returns only pairs that could not be resolved (with False value).
    
    Args:
        batch_results: Pairs returned from LLM
        sent_pairs: Pairs that were sent to LLM
        client: OpenAI client instance
        model: Model name
        top_p: Top-p parameter for LLM
        build_prompt_func: Function to build prompt from pairs
        seperator: Separator used in triple format
    
    Returns:
        List of missing pairs with False value, or empty list if none missing
    """
    # Detect missing pairs
    returned_pairs: set[tuple[str, str]] = {(pair[0], pair[1]) for pair in batch_results}
    missing_pairs: set[tuple[str, str]] = sent_pairs - returned_pairs
    
    if not missing_pairs:
        return []
    
    prompt: str = ""
    if typ is None:
        prompt = build_prompt_func(list(missing_pairs))
    else:
        prompt = build_prompt_func(list(missing_pairs), typ)
    
    # Retry missing pairs once
    retry_response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": "You are an expert in the field of requirements engineering and semantic analysis."
            },
            {
                "role": "user",
                "content":  prompt
            }
        ],
        temperature=top_p,
        top_p=top_p,
    )
    
    retry_results = extract_triple_elements(
        retry_response.choices[0].message.content,
        seperator=seperator,
        line_seperator="\n"
    )
    
    # Check what's still missing after retry
    retry_returned_pairs = {(pair[0], pair[1]) for pair in retry_results}
    still_missing = missing_pairs - retry_returned_pairs
    
    # Return newly computed pairs from retry and still missing pairs with False
    missed_elements: list[tuple[str, str, str]] = list(retry_results)
    missed_elements.extend([(pair[0], pair[1], "false") for pair in still_missing])
    
    return missed_elements