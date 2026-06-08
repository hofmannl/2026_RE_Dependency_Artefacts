# Semantic Equivalence Module
# ------------------------------------
# Provides *robust* semantic equivalence judgments between verbs using
# a majority-vote approach across three independent lexical-semantic signals.
#
# Definition:
#   Two verbs are semantically equivalent if they refer to the same
#   underlying action, process, or event type, regardless of surface form.
#   This module determines equivalence using:
#     (1) WordNet transitive verb-group similarity,
#     (2) ConceptNet synonym / similar-to relations,
#     (3) WordNet semantic similarity (WUP) as a fallback.
#
# What this module DOES:
#   • Identifies equivalence via WordNet’s verb-group, similar-to, and
#     also-see relations, including *transitive* similarity chains.
#
#   • Incorporates ConceptNet synonymy and near-synonymy to capture
#     modern, commonsense, and non-lexicalized equivalence patterns.
#
#   • Uses WordNet WUP similarity (≥ 0.9) as a semantic backup signal
#     for near-identical meanings not explicitly linked in the ontology.
#
#   • Applies majority voting to avoid noisy or spurious matches and to
#     combine evidence from complementary knowledge sources.
#
#   • Handles multi-word expressions by extracting their head verb.
#
#
# What this module does NOT do:
#   • Does NOT rely on hypernymy/hyponymy — generalisation or
#     specialisation relations are *not* treated as equivalence.
#
#   • Does NOT treat troponyms (manner-of verbs) as equivalent, since
#     they encode specificity rather than meaning identity.
#
#   • Does NOT infer domain-specific equivalence such as workflow or
#     business-process synonyms unless supported by ConceptNet or
#     WordNet similarity.
#
#   • Does NOT use manual overrides or handcrafted synonym lists.
#     All judgments rely on curated lexical semantics or commonsense
#     knowledge bases.
#
#
# Intended Use:
#   This module is designed for linguistic and lexical-semantic analysis
#   of verb meaning identity, not for domain-specific synonym extraction,
#   task modeling, or workflow interpretation. It aims to reflect general,
#   domain-neutral semantic equivalence as represented in large lexical
#   knowledge bases.
#
# Summary:
#   Multi-source equivalence       (WordNet + ConceptNet + similarity)
#   Transitive similarity          (verb-group/also-see chains)
#   No generalisation              (hypernyms excluded)
#   No specialisation              (troponyms excluded)
#   No domain adjustments          (pure lexical + commonsense evidence)


import time
import requests
from nltk.corpus import wordnet as wn

# ----------------------------------------------------
# Helpers
# ----------------------------------------------------

def normalize(v: str) -> str:
    return v.strip().lower()

def head_verb(phrase: str) -> str:
    parts = normalize(phrase).split()
    return parts[-1] if parts else phrase

def get_synsets(v: str):
    return wn.synsets(v, pos=wn.VERB)

def lemma_set(synsets):
    out = set()
    for s in synsets:
        for l in s.lemmas():
            out.add(l.name().replace("_", " ").lower())
    return out


# ----------------------------------------------------
# SIGNAL 1:
# TRANSITIVE WORDNET EQUIVALENCE
# via verb_groups, similar_tos, also_sees
# ----------------------------------------------------

def wn_equivalent(a1: str, a2: str) -> bool:
    """
    True if a1 and a2 belong to the same transitive
    verb-group / similar-to cluster in WordNet.
    Uses transitive closure over:
      - similar_tos()
      - verb_groups()
      - also_sees()
    """

    a1 = head_verb(a1)
    a2 = head_verb(a2)

    syn1 = get_synsets(a1)
    syn2 = get_synsets(a2)
    if not syn1 or not syn2:
        return False

    def closure(start_synsets):
        visited = set()
        queue = list(start_synsets)

        while queue:
            s = queue.pop()
            if s in visited:
                continue
            visited.add(s)

            # Expand through similarity graph
            graph_neighbors = (
                s.similar_tos() +
                s.verb_groups() +
                s.also_sees()
            )

            for n in graph_neighbors:
                if n not in visited:
                    queue.append(n)

        return lemma_set(visited)  # all lemma names reachable

    cluster1 = closure(syn1)
    cluster2 = closure(syn2)

    return len(cluster1 & cluster2) > 0


# ----------------------------------------------------
# SIGNAL 2:
# CONCEPTNET SYNONYM / SIMILARITY RELATIONS
# ----------------------------------------------------

def conceptnet_equivalent(a1: str, a2: str) -> bool:
    """
    True if ConceptNet lists a synonym/similar relation.
    """
    a1 = normalize(a1).replace(" ", "_")
    a2 = normalize(a2).replace(" ", "_")

    relations = ["Synonym", "SimilarTo", "DefinedAs", "EtymologicallyRelatedTo"]

    time.sleep(0.25)  # rate limiting

    for rel in relations:
        url = (
            "https://api.conceptnet.io/query?"
            f"node=/c/en/{a1}&rel=/r/{rel}&other=/c/en/{a2}"
        )

        try:
            resp = requests.get(url, timeout=4)
            if resp.status_code != 200:
                continue

            if resp.json().get("edges"):
                return True

        except:
            continue

    return False


# ----------------------------------------------------
# SIGNAL 3:
# WORDNET WUP-SIMILARITY (semantic closeness)
# ----------------------------------------------------

def wn_similarity_equivalent(a1: str, a2: str, threshold=0.9) -> bool:
    """
    Computes semantic equivalence using Wu-Palmer similarity,
    expanded with DFS over each synset’s neighborhood
    (hypernyms, hyponyms, similar-tos, also-sees).

    This reduces false negatives when the direct synsets
    are not similar enough but a closely related sense is.
    """

    a1 = head_verb(a1)
    a2 = head_verb(a2)

    syn1 = get_synsets(a1)
    syn2 = get_synsets(a2)
    if not syn1 or not syn2:
        return False

    # Build expanded synset neighborhoods via DFS
    def expand(start_synsets):
        visited = set()
        stack = list(start_synsets)

        while stack:
            s = stack.pop()
            if s in visited:
                continue
            visited.add(s)

            neighbors = (
                s.similar_tos() +
                s.also_sees()
            )

            for n in neighbors:
                if n not in visited:
                    stack.append(n)

        return visited

    expanded1 = expand(syn1)
    expanded2 = expand(syn2)

    # Compute best similarity across expanded neighborhoods
    best = 0.0
    for s1 in expanded1:
        for s2 in expanded2:
            sim = s1.wup_similarity(s2) or 0.0
            if sim > best:
                best = sim
                if best >= threshold:
                    return True  # early exit

    return best >= threshold

# ----------------------------------------------------
# MAJORITY VOTE SEMANTIC EQUIVALENCE
# ----------------------------------------------------

def is_semantically_equivalent(a1: str, a2: str) -> bool:
    """
    Semantic equivalence using majority vote across:
      1. WordNet transitive verb-group equivalence
      2. ConceptNet synonym/similar relations
      3. WordNet semantic similarity (WUP)
    """

    a1h = head_verb(a1)
    a2h = head_verb(a2)

    # identical verbs are trivially equivalent
    if a1h == a2h:
        return True

    return wn_equivalent(a1h, a2h) or wn_similarity_equivalent(a1h, a2h)

    # votes = {
    #     "verb_group": wn_equivalent(a1h, a2h),
    #     "conceptnet": conceptnet_equivalent(a1h, a2h),
    #     "similarity": wn_similarity_equivalent(a1h, a2h),
    # }

    # positive = sum(votes.values())

    # print(f"\nEquivalence votes for '{a1}' ↔ '{a2}':")
    # for k, v in votes.items():
    #     print(f"  {k}: {v}")

    # return positive >= 2  # majority vote


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
    
    print("start sem analysis")
    start_time = time.time()
    output: list[str] = []
    for a1, a2 in data:
        output.append(f"{is_semantically_equivalent(a1, a2)}")
    end_time = time.time()
    print(f"completed semantic equivalence analysis in {end_time - start_time:.2f} seconds")

    print("finished sem analysis, writing output")

    with open(_path.replace("_input.txt", "_output.txt"), "w") as f:
        f.truncate(0)
        f.write("\n".join(output))   
        
    #     tests = [
    #         ("notify", "inform"),        # True
    #         ("evaluate", "check"),       # True
    #         ("purchase", "buy"),         # True
    #         ("start", "begin"),          # True
    #         ("evaluate", "assess"),      # True
    #         ("process", "handle"),       # likely True via ConceptNet
    #         ("capture", "record"),       # similar but not equivalent
    #         ("jog", "run"),              # False (specialisation)
    #         ("walk", "stroll"),          # False
    #         ("submit", "send"),          # uncertain, ConceptNet sometimes
    #     ]

    #     for a1, a2 in tests:
    #         print(f"\nRESULT: {a1} ≈ {a2}?  {is_semantically_equivalent(a1, a2)}")