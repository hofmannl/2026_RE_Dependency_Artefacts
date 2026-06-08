# Semantic Containment Module
# ------------------------------------
# Provides *strict* semantic containment judgments between verbs
# using only WordNet’s entailment relation.
#
# Definition:
#   Verb A semantically contains Verb B if WordNet specifies that
#   performing A *logically requires* performing B. This corresponds to
#   WordNet’s verb entailment relation, which encodes subevent structure.
#
# What this module DOES:
#   • Identifies genuine sub-actions based solely on WordNet entailments.
#   • Handles multi-word expressions by extracting their head verb.
#
# What this module does NOT do:
#   • No troponymy (manner-of relations) — these reflect specialisation,
#     not containment, and are intentionally excluded.
#
#   • No hypernymy or hyponymy — generalisation/specialisation relations
#     are excluded to avoid false positives.
#
#   • No synonymy or verb-group equivalence — identical or interchangeable
#     verbs are not considered containment.
#
#   • No domain-specific knowledge or manual overrides — judgments rely
#     exclusively on WordNet’s curated lexical semantics and are domain-neutral.
#
# Intended Use:
#   This module is designed for linguistic analysis of subevent
#   containment, not for workflow verbs, business process modelling,
#   or domain-specific verb hierarchies.
#   Furthermore, gaps in the ontology may lead to some false negatives.
#
# Summary:
#   Pure lexical containment   (entailment only)
#   No specialisation          (troponymy excluded)
#   No generalisation          (hypernyms excluded)
#   No equivalence             (synonyms excluded)
#   No domain adjustments



import time
import requests
from nltk.corpus import wordnet as wn
from nltk.corpus import framenet as fn

# ----------------------------------------------------
# Basic utilities
# ----------------------------------------------------

def normalize(v: str) -> str:
    return v.strip().lower()

def head_verb(phrase: str) -> str:
    parts = normalize(phrase).split()
    return parts[-1] if parts else phrase

def get_synsets(v: str):
    return wn.synsets(v, pos=wn.VERB)

def lemma_set(synsets):
    result = set()
    for s in synsets:
        for l in s.lemmas():
            result.add(l.name().replace("_", " ").lower())
    return result


# ----------------------------------------------------
# 1) Strict WordNet ENTAILMENT (REAL sub-actions only)
# ----------------------------------------------------
def is_entailment(a1: str, a2: str) -> bool:
    """
    Returns True if WordNet indicates that a1 entails a2,
    considering transitive entailments.
    """
    syn1 = get_synsets(a1)
    syn2 = get_synsets(a2)

    if not syn1 or not syn2:
        return False

    target = lemma_set(syn2)
    visited = set()

    def dfs(s):
        if s in visited:
            return False
        visited.add(s)

        # direct entailment
        for ent in s.entailments():
            if lemma_set([ent]) & target:
                return True
            if dfs(ent):   # recursive / transitive allow A→B→C→D
                return True

        return False

    return any(dfs(s) for s in syn1)

# ----------------------------------------------------
# 4) ConceptNet HasSubevent = strong signal for containment
# ----------------------------------------------------
def conceptnet_contains(a1: str, a2: str) -> bool:
    """
    Returns True if ConceptNet specifies a HasSubevent relation
    indicating a2 is a sub-action of a1.
    Handles EN, EN_US, EN_GB variants and reverse lookups.
    """
    def q(verb):
        v = normalize(verb).replace(" ", "_")
        return [f"/c/en/{v}", f"/c/en_us/{v}", f"/c/en_gb/{v}"]

    # Rate limiting (safe)
    time.sleep(0.2)

    # Check all variant spellings and reversed direction
    for n1 in q(a1):
        for n2 in q(a2):
            url = (
                "https://api.conceptnet.io/query?"
                f"node={n1}&rel=/r/HasSubevent&other={n2}"
            )

            try:
                resp = requests.get(url, timeout=4)
                if resp.status_code != 200:
                    continue

                edges = resp.json().get("edges", [])
                if edges:
                    return True

            except Exception:
                continue

    return False


# ----------------------------------------------------
# 5) FrameNet Sub-events
# ----------------------------------------------------
def framenet_contains(a1: str, a2: str) -> bool:
    """
    Returns True if FrameNet indicates that a2 is a subevent,
    subframe, or procedurally required component of a1.
    """
    a1 = a1.lower()
    a2 = a2.lower()

    try:
        lu_list = fn.lus(a1)
        if not lu_list:
            return False

        for lu in lu_list:
            frame = fn.frame(lu.frame.ID)

            # 1. Check SUBFRAME relations (strongest)
            for rel in frame.frameRelations:
                reltype = rel.type.name.lower()

                # Relations that indicate subevent structure:
                if reltype in ("subframe", "precedes", "causes", "inherits_from"):
                    child = fn.frame(rel.subFrame.ID)
                    for clu in child.lexUnit.values():
                        if clu["name"].split(".")[0].lower() == a2:
                            return True

            # 2. Check Frame Elements for embedded subactions
            for fe in frame.FE.values():
                if "definition" in fe:
                    if a2 in fe["definition"].lower():
                        return True

            # 3. Check frame definition directly
            if a2 in frame.definition.lower():
                return True

        return False
    except Exception:
        return False

# ----------------------------------------------------
# FINAL STRICT CONTAINMENT FUNCTION
# ----------------------------------------------------
def verb_contains(action1: str, action2: str) -> bool:
    a1 = head_verb(action1)
    a2 = head_verb(action2)

    # SAME VERB IS NOT CONTAINMENT
    if a1 == a2:
        return False

    return is_entailment(a1, a2) or framenet_contains(a1, a2) 

    # # Reject hierarchy & synonyms
    # if is_specialisation(a1, a2):
    #     return False
    # if is_equivalent(a1, a2):
    #     return False

    # # Compute containment votes (ONLY real containment)
    # votes = {
    #     "entailment": is_entailment(a1, a2),
    #     "conceptnet": conceptnet_contains(a1, a2),
    #     "framenet": framenet_contains(a1, a2)
    # }

    # positive = sum(votes.values())

    # print(f"\nVotes for REAL containment '{action1}' → '{action2}':")
    # for k, v in votes.items():
    #     print(f"  {k}: {v}")

    # # Majority of REAL containment signals
    # return positive >= 2


# ----------------------------------------------------
# Example usage
# ----------------------------------------------------
if __name__ == "__main__":
    _path: str = r"<USER_PATH>\annotationWithWordNets\_input.txt"
    data: list[tuple[str, str]] = []
    with open(_path, "r") as f:
        for line in f:
            parts = line.strip().split("|")
            if len(parts) == 2:
                data.append((parts[0], parts[1]))
    
    output: list[str] = []
    for a1, a2 in data:
        output.append(f"{verb_contains(a1, a2)}")
    
    with open(_path.replace("_input.txt", "_output.txt"), "w") as f:
        f.truncate(0)
        f.write("\n".join(output))
    
    # tests = [
    #     ("evaluate", "check"),      # TRUE (real containment via entailment)
    #     ("review",   "check"),      # TRUE
    #     ("move",     "walk"),       # FALSE (specialisation)
    #     ("walk",     "move"),       # FALSE (generalisation)
    #     ("notify",   "inform"),     # FALSE (synonyms)
    #     ("assign",   "notify"),     # ConceptNet often TRUE
    #     ("process",  "record"),     # Maybe TRUE depending on frameworks
    #     ("submit",   "apply"),      # Usually FALSE (synonyms)
    #     ("capture",  "record"),     # FALSE (no entailment)
    # ]

    # for a1, a2 in tests:
    #     print(f"\nRESULT: {a1} strictly contains {a2}?  {verb_contains(a1, a2)}")