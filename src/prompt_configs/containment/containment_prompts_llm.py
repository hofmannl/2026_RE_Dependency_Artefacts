

def build_prompt(pairs: list[tuple[str, str]]) -> str:
    """
    Build a prompt for batch entity containment analysis.

    Ensures the model ONLY analyzes the provided pairs and only those exact strings.
    """
    sorted_pairs: list[tuple[str, str]] = sorted(pairs)
    pairs_str: str = "\n".join(f"{word1}--{word2}" for word1, word2 in sorted_pairs)
    n: int = len(sorted_pairs)

    return f"""Y
You are a requirement engineering expert, tasked with classifying "containment relations" inside system specifications.

DEFINITION
A containment relation describes a potential compositional or structural relationships within a system.
For a pair (entity1 -- entity2), e.g., the statement “entity2 is contained in entity1” is TRUE when it is potentially or plausibly possible that, in a typical system or specification context, entity2 is or could realistically be a component, sub-element, or constituent part of entity1 (e.g., entity1 consists of, comprises, incorporates, or includes entity2).

TASK
Classify EACH PROVIDED pair (entity1 -- entity2) as true or false if at least one of the following holds:
-	entity1 includes entity2. 
-	entity1 contains entity2. 
-	entity1 holds at least entity2.
-	entity1 can hold at least entity2.
-	entity1 can include entity2. 
-	entity1 has entity2. 
-	entity1 consists of entity2. 
-	entity1 comprises entity2. 
-	entity1 incorporates entity2. 
-	entity1 has got entity2. 
-	entity1 comes with entity2.

STRICT SCOPE / CLOSED WORLD (VERY IMPORTANT)
-	Analyze ONLY the entity pairs listed under INPUT.
-	Do NOT add, remove, swap, reverse, or create any additional pairs.
-	Do NOT infer missing pairs.
-	Treat entity1 and entity2 as EXACT STRINGS. Thereby, do not correct spelling, translate, expand abbreviations, singularize/pluralize, split/join tokens, or reinterpret meanings.

DECISION RULES
1.	Use requirements engineering and system modeling intuition (components, subsystems, parts).
2.	A word is never reflexive to itself and therefore cannot be contained in itself.
3.	Consider direct and potential containment, but ONLY based on the given two strings.
4.  Containment is irreflexive: an entity cannot contain itself (e.g., "message" is not contained in "message").

OUTPUT FORMAT (STRICT)
-	Output EXACTLY {n} lines — one line per input pair.
-	Output ONLY a newline-separated list of results.
-	Each result must be exactly: entity1-- entity 2--true or false
-	Use lowercase true/false.
-	entity1 and entity2 in the output must match the input pair strings EXACTLY.
-	No extra text, no markdown, no explanations, no header.

EXAMPLE INPUTS
ENTITY1 (possible container) -- ENTITY2 (possible contained element)
system--module
module--system
system--payment
payment--system
module--function
function--module
system--function
function--system
page--button
button--page
page--form
form--page
form--field
field--form
feature--setting
setting--feature
feature--sky
sky--feature
order--item
item--order
order--payment
payment--order
account--transaction
transaction--account
search--filter
filter--search
dashboard--widget
widget--dashboard
notification--message
message--notification
message--message

EXAMPLE OUTPUTS
ENTIY1 (possible container) -- ENTIY2 (possible contained element) -- ANSWER (true or false)
system--module--true
module--system--false
system--payment--false
payment--system--false
module--function--true
function--module--false
system--function--true
function--system--false
page--button--true
button--page--false
page--form--true
form--page--false
form--field--true
field--form--false
feature--setting--true
setting--feature--false
feature--sky--false
sky--feature--false
order--item--true
item--order--false
order--payment--true
payment--order--false
account--transaction--false
transaction--account--false
search--filter--false
filter--search--false
dashboard--widget--true
widget--dashboard--false
notification--message--false
message--notification--false
message--message--false

NOW PROCESS THE FOLLOWING
INPUT -- Entity pairs (exactly these, and only these):
{pairs_str}

OUTPUT:
"""