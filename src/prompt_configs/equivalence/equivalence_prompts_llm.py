from __future__ import annotations

from utilis.annotation_graph_components import TypeGraphUs


def build_prompt(pairs: list[tuple[str, str]], typ: TypeGraphUs) -> str:
    """
    Build a prompt for batch semantic equivalence analysis.

    Guarantees:
    - ONLY the provided pairs are analyzed (closed world).
    - persona1/persona2/action1/action2/entity1/entity2 are treated as EXACT STRINGS.
    - Output is strictly machine-parseable: one line per input pair.
    """
    sorted_pairs: list[tuple[str, str]] = sorted(pairs)
    pairs_str: str = "\n".join(f"{a}--{b}" for a, b in sorted_pairs)
    n: int = len(sorted_pairs)

    if typ == TypeGraphUs.PERSONA:
        return PERSONA_EQUIVALENCE_PROMPT.format(n=n, pairs_str=pairs_str)
    if typ == TypeGraphUs.ACTION:
        return ACTION_EQUIVALENCE_PROMPT.format(n=n, pairs_str=pairs_str)
    return ENTITY_EQUIVALENCE_PROMPT.format(n=n, pairs_str=pairs_str)


# -------------------------
# Core prompt design choices
# -------------------------
# - Shorter, more “operational” rules (less narrative).
# - Strong negative guardrails (prevents “related/close” => true).
# - Explicit identity behavior: if strings identical => true.
# - Closed-world repeated in multiple sections to reduce drift.
# - Examples include tricky near-misses to calibrate conservatism.


# NOT EQUIVALENT (always false)
# - broader vs narrower role (generalization/specialization): user vs admin
# - different roles that can overlap: manager vs supervisor (unless identical meaning is certain)
# - related roles: customer vs account-holder
# - spelling corrections, expansions, translations, plural/singular normalization: NOT allowed (treat exact strings as-is)

PERSONA_EQUIVALENCE_PROMPT = """
You are a requirements engineering expert. Your job is to decide SEMANTIC EQUIVALENCE (same/similar meaning) for persona pairs.

WHAT "SEMANTICALLY EQUIVALENT" MEANS
For a pair (persona1 -- persona2), output TRUE when persona2 can potentially / reasonably be interpreted as the similar / equivalent role as persona1 or as a specialized, extended, or instantiated form of persona1 within the requirements.
This includes cases where persona2 could replace persona1 in the requirements without materially changing the intended meaning, even if it is more specific.

CLOSED WORLD / EXACT STRINGS (VERY IMPORTANT)
- Analyze ONLY the pairs listed under INPUT.
- Do NOT add, remove, swap, reverse, or invent pairs.
- Treat persona1/persona2 as EXACT STRINGS: do not correct, translate, expand abbreviations, change casing, tokenize, etc.

DECISION RULES
1) If persona1 == persona2 exactly, output true.
2) Otherwise, output true ONLY for clear synonyms naming the same role.
3) Assign the label true whenever it is potentially or reasonably plausible that persona2 refers to the similar semantic persona as persona1, even if this equivalence is not explicitly stated. If there is any ambiguity or uncertainty, default to true, as false positives are preferable to false negatives.

OUTPUT FORMAT (STRICT)
- Output EXACTLY {n} lines (one per input pair).
- Each line: persona1--persona2--true or false
- Lowercase true/false only. No extra text.

CALIBRATION EXAMPLES

CALIBRATION EXAMPLES

INPUT:
user--enduser
admin--administrator
guest--anonymoususer
employee--staff
user--admin
manager--supervisor
customer--client
user--user
client--buyer
developer--programmer
tester--qaengineer
operator--technician
student--learner
physician--doctor
accountant--auditor
customer--subscriber
admin--moderator
manager--teamlead

OUTPUT:
user--enduser--true
admin--administrator--true
guest--anonymoususer--false
employee--staff--true
user--admin--false
manager--supervisor--true
customer--client--true
user--user--true
client--buyer--false
developer--programmer--true
tester--qaengineer--true
operator--technician--false
student--learner--true
physician--doctor--true
accountant--auditor--false
customer--subscriber--false
admin--moderator--false
manager--teamlead--true

INPUT (exactly these, and only these):
{pairs_str}

OUTPUT:
"""


ACTION_EQUIVALENCE_PROMPT = """
You are a requirements engineering expert. Your job is to decide SEMANTIC EQUIVALENCE (same/similar meaning) for action pairs.

WHAT "SEMANTICALLY EQUIVALENT" MEANS
For a pair (action1 -- action2), output TRUE when it is potentially or plausibly possible that both actions describe the semantical equivalent operation, with the similar/equivalenet intended.
This includes cases where action2 could replace action1 in the requirements without materially changing the intended meaning.

NOT EQUIVALENT (always false)
- broader vs narrower: access vs login
- related steps / prerequisites: register vs login
- opposites: approve vs reject, send vs receive
- “roughly similar” or “often used together”: false
- spelling corrections, expansions, translations, spacing fixes: NOT allowed (treat exact strings as-is)

CLOSED WORLD / EXACT STRINGS (VERY IMPORTANT)
- Analyze ONLY the pairs listed under INPUT.
- Do NOT add, remove, swap, reverse, or invent pairs.
- Treat action1/action2 as EXACT STRINGS: do not correct, translate, expand abbreviations, change casing, tokenize, etc.

DECISION RULES
1) If action1 == action2 exactly, output true.
2) Otherwise, output true ONLY for clear synonyms of the same operation.
3) Assign the label true whenever it is potentially or reasonably plausible that action2 refers to the similar semantic action as action1, even if this equivalence is not explicitly stated. If there is any ambiguity or uncertainty, default to true, as false positives are preferable to false negatives.


OUTPUT FORMAT (STRICT)
- Output EXACTLY {n} lines (one per input pair).
- Each line: action1--action2--true or false
- Lowercase true/false only. No extra text.

CALIBRATION EXAMPLES

CALIBRATION EXAMPLES

INPUT:
delete--remove
update--modify
cancel--abort
create--add
access--login
send--receive
approve--authorize
login--sign in
view--view
buy--purchase
save--store
logout--sign out
register--signup
download--export
submit--send
reset--restart
pay--refund
enable--activate
search--filter

OUTPUT:
delete--remove--true
update--modify--true
cancel--abort--true
create--add--true
access--login--true
send--receive--false
approve--authorize--true
login--sign in--true
view--view--true
buy--purchase--true
save--store--true
logout--sign out--true
register--signup--true
download--export--false
submit--send--false
reset--restart--true
pay--refund--false
enable--activate--true
search--filter--false

INPUT (exactly these, and only these):
{pairs_str}

OUTPUT:
"""


ENTITY_EQUIVALENCE_PROMPT = """
You are a requirements engineering expert. Your job is to decide SEMANTIC EQUIVALENCE (same/similar meaning) for entity pairs.

WHAT "SEMANTICALLY EQUIVALENT" MEANS
For a pair (entity1--entity2), output TRUE when it is potentially or plausibly possible that both strings denote the similar semantic concept (i.e., the same referent) in the requirements, with equivalent intended meaning.
This includes cases where entity2 could replace entity1 in the requirements without materially changing the intended meaning.

NOT EQUIVALENT (always false)
- generalization/specialization: document vs invoice
- part-of / containment: order vs orderitem
- representation vs concept: file vs document (often related, not necessarily identical)
- different artifacts of same process: order vs payment
- spelling corrections, expansions, translations, plural/singular normalization: NOT allowed (treat exact strings as-is)

CLOSED WORLD / EXACT STRINGS (VERY IMPORTANT)
- Analyze ONLY the pairs listed under INPUT.
- Do NOT add, remove, swap, reverse, or invent pairs.
- Treat entity1/entity2 as EXACT STRINGS: do not correct, translate, expand abbreviations, change casing, tokenize, etc.

DECISION RULES
1) If entity1 == entity2 exactly, output true.
2) Otherwise, output true ONLY for clear synonyms denoting the same concept.
3) Assign the label true when it is potentially or reasonably plausible that entity2 refers to the semantic equivalent entity as entity1, otherwise false.

OUTPUT FORMAT (STRICT)
- Output EXACTLY {n} lines (one per input pair).
- Each line: entity1--entity2--true or false
- Lowercase true/false only. No extra text.

CALIBRATION EXAMPLES

INPUT:
email--mail
invoice--bill
notification--alert
document--invoice
document--file
message--notification
order--purchase
account--account
profile--userprofile
username--userid
image--picture
payment--transaction
receipt--invoice
dashboard--report
category--tag
address--location
folder--directory
role--permission

OUTPUT:
email--mail--true
invoice--bill--true
notification--alert--true
document--invoice--false
document--file--true
message--notification--true
order--purchase--false
account--account--true
profile--userprofile--true
username--userid--false
image--picture--true
payment--transaction--false
receipt--invoice--false
dashboard--report--false
category--tag--true
address--location--true
folder--directory--true
role--permission--false


INPUT (exactly these, and only these):
{pairs_str}

OUTPUT:
"""
