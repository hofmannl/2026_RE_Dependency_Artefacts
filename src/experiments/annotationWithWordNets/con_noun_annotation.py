# Multi-source Noun Part-of Containment Module
# ---------------------------------------------
# Determines whether noun A contains noun B in the PART-OF sense.
#
# Sources used:
#   1. WordNet meronym hierarchy (part_meronyms, transitive)
#   2. ConceptNet PartOf / HasA relations (in correct directions)
#   3. Wikidata (P361 part of, P527 has part)
#
# Containment criteria:
#      A contains B  ⇔  B is a part of A
#
# No IS-A, no hypernyms, no synonyms, no sub-events.
# Pure whole → part relationships.

import time
import requests
from nltk.corpus import wordnet as wn


# ----------------------------------------------------
# Helpers
# ----------------------------------------------------

def normalize(s: str) -> str:
    return s.strip().lower()

def head_noun(text: str) -> str:
    return normalize(text).split()[-1]

def get_synsets(n: str):
    return wn.synsets(n, pos=wn.NOUN)

def lemma_set(synsets):
    s = set()
    for syn in synsets:
        for l in syn.lemmas():
            s.add(l.name().replace("_", " ").lower())
    return s


# ----------------------------------------------------
# SIGNAL 1 — WordNet PART-MERONYM (direct + transitive)
# ----------------------------------------------------

def wn_partof(a1: str, a2: str) -> bool:
    """
    True if noun a1 contains noun a2 via WordNet meronym hierarchy.
    A contains B  ⇔  B is a part_meronym of A (possibly transitively)
    """
    a1 = head_noun(a1)
    a2 = head_noun(a2)

    syn1 = get_synsets(a1)
    syn2 = get_synsets(a2)

    if not syn1 or not syn2:
        return False

    # Target: lemmas of a2 (the potential part)
    target = lemma_set(syn2)
    visited = set()

    def dfs(s):
        """Traverse part_meronyms of s to find if target exists."""
        if s in visited:
            return False
        visited.add(s)

        # Check direct part meronyms (parts of this synset)
        for mero in s.part_meronyms():
            if lemma_set([mero]) & target:
                return True
            if dfs(mero):
                return True

        return False

    # Start from a1 synsets and search for a2 as a part
    return any(dfs(s) for s in syn1)


# ----------------------------------------------------
# SIGNAL 2 — ConceptNet PartOf / HasA
# ----------------------------------------------------

def conceptnet_partof(a1: str, a2: str) -> bool:
    """
    True if ConceptNet says 'A has part B' OR 'B PartOf A'.

    We check:
      - A HasA B
      - B PartOf A
    """

    v1 = normalize(a1).replace(" ", "_")
    v2 = normalize(a2).replace(" ", "_")

    time.sleep(0.15)

    # 1) A HasA B
    url_has = (
        "https://api.conceptnet.io/query?"
        f"node=/c/en/{v1}&rel=/r/HasA&other=/c/en/{v2}"
    )
    # 2) B PartOf A
    url_partof = (
        "https://api.conceptnet.io/query?"
        f"node=/c/en/{v2}&rel=/r/PartOf&other=/c/en/{v1}"
    )

    for url in (url_has, url_partof):
        try:
            resp = requests.get(url, timeout=4)
            if resp.status_code != 200:
                continue
            if resp.json().get("edges"):
                return True
        except Exception:
            continue

    return False


# ----------------------------------------------------
# SIGNAL 3 — Wikidata "has part" / "part of" (P527, P361)
# ----------------------------------------------------

def wikidata_partof(a1: str, a2: str) -> bool:
    """
    True if Wikidata says:
        A has part B (P527)  OR
        B is part of A (P361)
    """
    a1_label = a1.strip()
    a2_label = a2.strip()

    # Escape quotes in labels
    a1_esc = a1_label.replace('"', '\\"')
    a2_esc = a2_label.replace('"', '\\"')

    query = """
    PREFIX wdt: <http://www.wikidata.org/prop/direct/>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

    SELECT ?a ?b WHERE {{
      ?a rdfs:label "{a1}"@en .
      ?b rdfs:label "{a2}"@en .

      {{ ?a wdt:P527 ?b }} UNION {{ ?b wdt:P361 ?a }}
    }}
    LIMIT 1
    """.format(a1=a1_esc, a2=a2_esc)

    url = "https://query.wikidata.org/sparql"

    try:
        resp = requests.get(url, params={"query": query, "format": "json"}, timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            return bool(data.get("results", {}).get("bindings"))
        
        time.sleep(0.1)
    except requests.RequestException:
        pass

    return False


# ----------------------------------------------------
# FINAL DECISION LOGIC
# ----------------------------------------------------

def noun_contains(a1: str, a2: str) -> bool:
    """
    Returns True if A contains B (part-of only).

    Decision rule:
      - If WordNet OR Wikidata say True → return True (strong signals)
      - Else, if ConceptNet says True → return True (fallback)
      - Else → False
    """

    a1 = head_noun(a1)
    a2 = head_noun(a2)

    if a1 == a2:
        return False

    wn_res = wn_partof(a1, a2)
    wd_res = wikidata_partof(a1, a2)

    # Strong sources: WordNet + Wikidata
    if wn_res or wd_res:
        return True

    # cn_res = conceptnet_partof(a1, a2)
    # # Fallback: ConceptNet alone
    # if cn_res:
    #     return True

    return False


# ----------------------------------------------------
# Example tests
# ----------------------------------------------------

if __name__ == "__main__":
    _path: str = r"<USER_PATH>\annotationWithWordNets\_input.txt"
    data: list[tuple[str, str]] = []
    with open(_path, "r") as f:
        for line in f:
            parts = line.strip().split("|")
            if len(parts) >= 2:
                data.append((parts[0], parts[1]))
    
    print("start contains analysis")
    output: list[str] = []
    for a1, a2 in data:
        output.append(f"{a1}|{a2}|{noun_contains(a1, a2)}")

    print("finished contains analysis, writing output")

    with open(_path.replace("_input.txt", "_output.txt"), "w") as f:
        f.truncate(0)
        f.write("\n".join(output))

    # tests = [
    #     ("car", "engine"),         # expected: True
    #     ("car", "wheel"),          # expected: True
    #     ("tree", "branch"),        # expected: True
    #     ("dog", "tail"),           # expected: True
    #     ("house", "roof"),         # expected: True
    #     ("computer", "keyboard"),  # expected: True
    #     ("car", "flower"),         # expected: False
    #     ("animal", "dog"),         # expected: False (IS-A, not part)
    #     ("engine", "car"),         # expected: False (reverse)
    # ]

    # for a1, a2 in tests:
    #     print(f"{a1} contains {a2}? {noun_contains(a1, a2)}")
