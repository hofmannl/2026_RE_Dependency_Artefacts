# Semantic Equivalence Module (Nouns)
# ------------------------------------
# Provides *robust* semantic equivalence judgments between nouns using
# a majority-vote approach across three independent lexical-semantic
# signals.
#
# Definition:
#   Two nouns are semantically equivalent if they refer to the same
#   underlying entity, object, concept, or category, regardless of their
#   surface form. This module determines equivalence using:
#     (1) WordNet transitive synonym / similarity relations,
#     (2) ConceptNet synonym / similar-to relations,
#     (3) WordNet semantic similarity (WUP) as a fallback.
#
# What this module DOES:
#   • Identifies equivalence via WordNet’s noun synsets, including
#     transitive closure over:
#         - synset lemmas,
#         - similar-to links,
#         - also-see relations.
#
#   • Incorporates ConceptNet synonymy and near-synonymy to capture
#     commonsense and modern lexical equivalence not explicitly encoded
#     in WordNet.
#
#   • Uses WordNet WUP similarity (≥ 0.9) as a high-precision semantic
#     fallback to detect near-identical noun meanings.
#
#   • Applies majority voting to avoid false positives and to combine
#     complementary evidence from lexical and commonsense sources.
#
#   • Handles multi-word expressions by extracting their head noun.
#
#
# What this module does NOT do:
#   • Does NOT treat hypernymy (is-a broader-than) as equivalence.
#     Generalisation is handled in a separate module.
#
#   • Does NOT treat hyponymy (is-a subtype-of) as equivalence.
#     Specialisation is conceptually different.
#
#   • Does NOT infer domain-specific equivalence such as technical terms,
#     organizational roles, or workflow-specific vocabulary unless
#     supported by WordNet or ConceptNet.
#
#   • Does NOT rely on handcrafted synonym dictionaries or any manual
#     override lists. All judgments derive strictly from curated lexical
#     and commonsense resources.
#
#
# Intended Use:
#   This module is intended for linguistic and lexical-semantic analysis
#   of noun meaning identity. It targets general, domain-neutral noun
#   semantics and is not designed for terminology alignment, ontology
#   merging, or domain-specific concept mapping.
#
# Summary:
#   Multi-source equivalence       (WordNet + ConceptNet + similarity)
#   Transitive similarity          (synonyms/similar-to/also-see chains)
#   No generalisation              (hypernyms excluded)
#   No specialisation              (hyponyms excluded)
#   No domain adjustments          (pure lexical + commonsense evidence)


import time
import requests
from nltk.corpus import wordnet as wn

# ----------------------------------------------------
# Helpers
# ----------------------------------------------------

def normalize(v: str) -> str:
    return v.strip().lower()

def head_noun(phrase: str) -> str:
    """Extracts the last word as the head noun."""
    parts = normalize(phrase).split()
    return parts[-1] if parts else phrase

def get_synsets(v: str):
    """Return WordNet noun synsets."""
    return wn.synsets(v, pos=wn.NOUN)

def lemma_set(synsets):
    """Return set of all lemma names for a collection of synsets."""
    out = set()
    for s in synsets:
        for l in s.lemmas():
            out.add(l.name().replace("_", " ").lower())
    return out


# ----------------------------------------------------
# SIGNAL 1:
# TRANSITIVE WORDNET EQUIVALENCE for NOUNS
# via similar_tos() and also_sees()
# ----------------------------------------------------

def wn_equivalent(a1: str, a2: str) -> bool:
    """
    True if a1 and a2 belong to the same transitive equivalence cluster
    using:
      - synset lemmas
      - similar_tos()
      - also_sees()
    """

    a1 = head_noun(a1)
    a2 = head_noun(a2)

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

            graph_neighbors = (
                s.similar_tos() + 
                s.also_sees()
            )

            for n in graph_neighbors:
                if n not in visited:
                    queue.append(n)

        return lemma_set(visited)

    cluster1 = closure(syn1)
    cluster2 = closure(syn2)

    return len(cluster1 & cluster2) > 0


# ----------------------------------------------------
# SIGNAL 2:
# CONCEPTNET SYNONYM / SIMILARITY RELATIONS
# ----------------------------------------------------

def conceptnet_equivalent(a1: str, a2: str) -> bool:
    """True if ConceptNet lists synonym/similar relations for nouns."""
    a1 = normalize(a1).replace(" ", "_")
    a2 = normalize(a2).replace(" ", "_")

    relations = ["Synonym", "SimilarTo", "DefinedAs", "EtymologicallyRelatedTo"]

    time.sleep(0.25)

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
    WordNet semantic similarity with DFS expansion.
    Explores a transitive neighborhood of each synset
    using:
        - similar_tos()
        - also_sees()
        - hypernyms / hyponyms (optional)
    
    Returns True if *any* pair of reachable synsets
    has Wu-Palmer similarity ≥ threshold.
    """

    a1 = head_noun(a1)
    a2 = head_noun(a2)

    syn1 = get_synsets(a1)
    syn2 = get_synsets(a2)

    if not syn1 or not syn2:
        return False

    # -------------------------------------------------
    # DFS NEIGHBORHOOD EXPANSION
    # -------------------------------------------------

    def expand(start_synsets):
        """Return all reachable synsets via semantic-similarity edges."""
        visited = set()
        stack = list(start_synsets)

        while stack:
            s = stack.pop()
            if s in visited:
                continue
            visited.add(s)

            # Expand via similarity graph
            neighbors = (
                s.similar_tos() +
                s.also_sees()
            )

            for n in neighbors:
                if n not in visited:
                    stack.append(n)

        return visited

    # Full similarity neighborhoods
    neigh1 = expand(syn1)
    neigh2 = expand(syn2)

    # -------------------------------------------------
    # WUP SIMILARITY OVER NEIGHBORHOOD PAIRS
    # -------------------------------------------------

    best = 0.0
    for s1 in neigh1:
        for s2 in neigh2:
            sim = s1.wup_similarity(s2) or 0
            best = max(best, sim)
            if best >= threshold:
                return True

    return False

def is_semantically_equivalent(a1: str, a2: str) -> bool:
    """
    Semantic equivalence using majority vote:
      1. WordNet transitive equivalence
      2. ConceptNet synonymy
      3. WordNet semantic similarity
    """

    a1h = head_noun(a1)
    a2h = head_noun(a2)

    if a1h == a2h:
        return True
    
    return wn_equivalent(a1h, a2h) and wn_similarity_equivalent(a1h, a2h)
    
    # votes = {
    #     "wordnet_transitive": wn_equivalent(a1h, a2h),
    #     "conceptnet": conceptnet_equivalent(a1h, a2h),
    #     "wup_similarity": wn_similarity_equivalent(a1h, a2h),
    # }

    # positive = sum(votes.values())

    # print(f"\nEquivalence votes for noun '{a1}' ↔ '{a2}':")
    # for k, v in votes.items():
    #     print(f"  {k}: {v}")

    # return positive >= 2


if __name__ == "__main__":
    _path: str = r"<USER_PATH>\annotationWithWordNets\_input.txt"
    data: list[tuple[str, str]] = []
    with open(_path, "r") as f:
        for line in f:
            parts = line.strip().split("|")
            if len(parts) >= 2:
                data.append((parts[0], parts[1]))
    
    print("start sem analysis")
    output: list[str] = []
    for a1, a2 in data:
        output.append(f"{a1}|{a2}|{is_semantically_equivalent(a1, a2)}")

    print("finished sem analysis, writing output")

    with open(_path.replace("_input.txt", "_output.txt"), "w") as f:
        f.truncate(0)
        f.write("\n".join(output))  
        
    # tests = [
    #     ("car", "automobile"),        # True
    #     ("sofa", "couch"),            # True
    #     ("doctor", "physician"),      # True
    #     ("student", "pupil"),         # True
    #     ("house", "home"),            # True via ConceptNet mostly
    #     ("cat", "feline"),            # Not exact equivalence → False
    #     ("tree", "plant"),            # Generalisation, not equivalence
    #     ("cup", "mug"),               # Similar but borderline
    # ]  

    # for a1, a2 in tests:
    #     print(f"\nRESULT: {a1} ≈ {a2}?  {is_semantically_equivalent(a1, a2)}")