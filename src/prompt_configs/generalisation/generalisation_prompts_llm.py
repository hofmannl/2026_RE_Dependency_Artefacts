from utilis.annotation_graph_components import TypeGraphUs

def build_prompt(pairs: list[tuple[str, str]], typ: TypeGraphUs) -> str:
    """
    Build a prompt for batch entity containment analysis.

    Ensures the model ONLY analyzes the provided pairs and only those exact strings.
    """
    sorted_pairs: list[tuple[str, str]] = sorted(pairs)
    pairs_str: str = "\n".join(f"{word1}--{word2}" for word1, word2 in sorted_pairs)
    n: int = len(sorted_pairs)
    
    if typ == TypeGraphUs.PERSONA:
      return persona_prompt.format(n=n, pairs_str=pairs_str)
    elif typ == TypeGraphUs.ACTION:
      return actions_prompt.format(n=n, pairs_str=pairs_str)
    else:
      return entities_prompt.format(n=n, pairs_str=pairs_str)

persona_prompt = (
"""
You are a requirement engineering expert, tasked with classifying "generalization relations" between actors or personas.

DEFINITION
A generalization relationship describes an “is-a” relationship in which a more specific element (the child or subclass) inherits the characteristics of a more general element (the parent or superclass). Thereby, it indicates that the specialized element is a kind of the generalized one, sharing its attributes and behaviour while possibly adding its own within a system.
For a pair (persona1 -- persona2), the statement “persona1 is a generalization of persona2” holds TRUE when persona2 represents a more specific type or specialization of persona1 and therefore satisfies an is-a relationship. Otherwise, it is FALSE. 
Thus, assign the label true only when, based on common role or persona hierarchies in requirements engineering, persona2 can plausibly be interpreted as a specialized, extended, or instantiated form of persona1.
Additionally, it must be stated that a persona is never reflexive to itself and therefore cannot be a generalization or a specialization of itself.

TASK
Classify EACH PROVIDED pair persona1--persona2 as true or false for:
-	persona2 represents a specific persona1.
-	persona2 functions as a persona1.
-	persona2 instantiates the persona1.
-	persona2 extends the persona1.
-	persona2 is a subtype of persona1.
-	persona2 specializes the persona1.
-	persona1 generalizes persona2.
-	persona1 encompasses persona2.
-	persona1 categorizes persona2.

STRICT SCOPE / CLOSED WORLD (VERY IMPORTANT)
-	Analyze ONLY the persona pairs listed under INPUT.
-	Do NOT add, remove, swap, reverse, or create any additional pairs.
-	Do NOT infer missing pairs.
-	Treat persona1 and persona2 as EXACT STRINGS. Thereby, do not correct spelling, translate, expand abbreviations, singularize/pluralize, split/join tokens, or reinterpret meanings.

DECISION RULES
1.	Interpret generalization in the context of role or persona hierarchies.
2.  Assign the label true whenever persona2 may potentially / reasonably represent a specialized, extended, or instantiated form of persona1. If there is ambiguity or uncertainty, choose true.
3.	A persona is never reflexive to itself and therefore cannot be a generalization or a specialization of itself.
4.  Generalization is irreflexive: a persona cannot generalize itself (e.g., "user" is not a generalization of "user").

OUTPUT FORMAT (STRICT)
-	Output EXACTLY {n} lines — one line per input pair.
-	Output ONLY a newline-separated list of results.
-	Each result must be exactly: persona1--persona2--true or false
-	Use lowercase true/false.
-	persona1 and persona2 in the output must match the input pair strings EXACTLY.
-	No extra text, no markdown, no explanations, no header.

EXAMPLES

INPUT - Persona pairs:
PERSONA1 (possible parent/generalization) -- PERSONA2 (possible child/concretization)
user--user
user--admin
admin--user
customer--premiumcustomer
premiumcustomer--customer
employee--manager
manager--employee
user--system
system--user
actor--user
user--actor
staff--employee
employee--staff
administrator--superadmin
superadmin--administrator
member--customer
customer--member
operator--technician
technician--operator
customer--technician
technician--customer

OUTPUT - Pairs pairs:
PERSONA1 (possible parent/generalization) -- PERSONA2 (possible child/concretization) -- ANSWER (true or false)
user--user--false
user--admin--true
admin--user—false
customer--admin--false
admin--customer--false
customer--premiumcustomer--true
premiumcustomer--customer--false
employee--manager--true
manager--employee--false
user--system--false
system--user--false
actor--user--true
user--actor--false
employee--system-- false
system--employee--false
staff--employee--true
employee--staff--false
administrator--superadmin--true
superadmin--administrator--false
member--customer--true
customer--member--false
operator--technician--true
technician--operator--false
customer--technician--false
technician--customer--false

INPUT - Word pairs (exactly these, and only these):
{pairs_str}

OUTPUT - Word pairs:
"""
)

actions_prompt = ( """
You are a requirement engineering expert, tasked with classifying "generalization relations" between actions.

DEFINITION
A generalization relationship describes an “is-a” relationship in which a more specific element (the child or subclass) inherits the characteristics of a more general element (the parent or superclass). It indicates that the specialized element is a kind of the generalized one, sharing its essential intent and observable effects while possibly adding more specific behavior within a system.
For a pair (action1 -- action2), the statement “action1 is a generalization of action2” holds TRUE when, in the context of typical requirements or action hierarchies, action2 can plausibly be interpreted as a more specific type, specialization, or constrained form of action1, thereby satisfying an is-a relationship. Otherwise, it is FALSE.
Assign the label true when there is reasonable and plausible evidence that action2 represents a specialized, extended, or instantiated form of action1. If the relationship is merely conceivable in the abstract but not plausibly grounded in common requirements modeling practices, assign false.
Additionally, an action is never reflexive to itself and therefore cannot be a generalization or a specialization of itself.

TASK
Classify EACH PROVIDED pair action1--action2 as true or false for:
-	action2 constitutes a specific action1.
-	action2 falls under the action1 category.
-	action2 executes a specific form of action1.
-	action2 specializes the action1.
-	action1 generalizes the action2.
-	action1 defines the class for action2.
-	action1 encompasses the action2.

STRICT SCOPE / CLOSED WORLD (VERY IMPORTANT)
-	Analyze ONLY the action pairs listed under INPUT.
-	Do NOT add, remove, swap, reverse, or create any additional pairs.
-	Do NOT infer missing pairs.
-	Treat action1 and action2 as EXACT STRINGS. Thereby, do not correct spelling, translate, expand abbreviations, singularize/pluralize, split/join tokens, or reinterpret meanings.

DECISION RULES
1.	Interpret generalization in the context of role or action hierarchies.
2.	A action is never reflexive to itself and therefore cannot be a generalization or a specialization of itself.
3.  Assign the label true whenever action2 may potentially / reasonably represent a specialized, extended, or instantiated form of action1. If there is ambiguity or uncertainty, choose true.
4.  Generalization is irreflexive: a action cannot generalize itself (e.g., "access" is not a generalization of "access").

OUTPUT FORMAT (STRICT)
-	Output EXACTLY {n} lines — one line per input pair.
-	Output ONLY a newline-separated list of results.
-	Each result must be exactly: action1--action2--true or false
-	Use lowercase true or false.
-	action1 and action2 in the output must match the input pair strings EXACTLY.
-	No extra text, no markdown, no explanations, no header.

EXAMPLES
INPUT - Word pairs:
ACTION1 (possible parent/generalization) -- ACTION2 (possible child/concretization)
access--access
access--login
login--access
update--modify
modify--update
pay--refund
refund--pay
send--receive
receive--send
create--add
add--create
delete--remove
remove--delete
view--read
read--view
approve--authorize
authorize--approve
start--initialize
initialize--start
submit--cancel
cancel--submit

OUTPUT - Word pairs:
ACTION1 (possible parent/generalization) -- ACTION2 (possible child/concretization) -- ANSWER (true or false)
access--access--false
access--login--true
login--access--false
update--modify--true
modify--update--false
pay--refund--true
refund--pay--false
send--receive--false
receive--send--false
create--add--true
add--create--false
delete--remove--true
remove--delete--false
view--read--true
read--view--false
approve--authorize--false
authorize--approve--false
start--initialize--true
initialize--start--false
submit--cancel--false
cancel--submit--false

INPUT - Word pairs (exactly these, and only these):
{pairs_str}

OUTPUT - Word pairs:
""")


entities_prompt = ("""
You are a requirement engineering expert, tasked with classifying "generalization relations" between entities.

DEFINITION
A generalization relationship describes an “is-a” relationship in which a more specific element (the child or subclass) inherits the characteristics of a more general element (the parent or superclass). Thereby, it indicates that the specialized element is a kind of the generalized one, sharing its attributes and behaviour while possibly adding its own within a system.
For a pair (entity1 -- entity2), the statement “entity1 is a generalization of entity2” holds TRUE when entity2 represents a more specific type or specialization of entity1 and therefore satisfies an is-a relationship. Otherwise, it is FALSE. 
Assign the label true when there is reasonable and plausible evidence that entity2 represents a specialized, extended, or instantiated form of entity1.
Additionally, it must be stated that a entity is never reflexive to itself and therefore cannot be a generalization or a specialization of itself.

TASK
Classify EACH PROVIDED pair entity1--entity2 as true or false for:
-	entity2 represents a specific form of entity1",
-	entity2 instantiates the entity1 class",
-	entity2 extends the entity1 definition",
-	entity2 specializes the entity1.
-	entity1 generalizes entity2
-	entity1 serves as the superclass for entity2
-	entity1 categorizes entity2 as a broader term.
-	entity1 abstracts entity2

STRICT SCOPE / CLOSED WORLD (VERY IMPORTANT)
-	Analyze ONLY the entity pairs listed under INPUT.
-	Do NOT add, remove, swap, reverse, or create any additional pairs.
-	Do NOT infer missing pairs.
-	Treat entity1 and entity2 as EXACT STRINGS. Thereby, do not correct spelling, translate, expand abbreviations, singularize/pluralize, split/join tokens, or reinterpret meanings.

DECISION RULES
1.	Interpret generalization in the context of role or entity hierarchies.
2.	A entity is never reflexive to itself and therefore cannot be a generalization or a specialization of itself.
3.	Assign the label true whenever entity2 may potentially / reasonably represent a specialized, extended, or instantiated form of entity1. If there is ambiguity or uncertainty, choose true.
4.  Generalization is irreflexive: an entity cannot generalize itself (e.g., "email" is not a generalization of "email").

OUTPUT FORMAT (STRICT)
1.	Output EXACTLY {n} lines — one line per input pair.
2.	Output ONLY a newline-separated list of results.
3.	Each result must be exactly: entity1--entity2--true or false
4.	Use lowercase true or false.
5.	entity1 and entity2 in the output must match the input pair strings EXACTLY.
6.	No extra text, no markdown, no explanations, no header.

EXAMPLES

INPUT - Entity pairs:
ENTITY1 (possible parent/generalization) -- ENTITY 2 (possible child/concretization) 
email--email
notification--email
email--notification
document--invoice
invoice--document
order--payment
payment--order
system--module
module--system
message--notification
notification--message
report--document
document--report
account--profile
profile--account
feature--setting
setting--feature
file--document
document--file
dashboard--page
page--dashboard

OUTPUT - Entity pairs
ENTITY1 (possible parent/generalization) -- ENTITY 2 (possible child/concretization) -- ANSWER (true or false)
email--email--false
notification--email--true
email--notification--false
document--invoice--true
invoice--document--false
order--payment--false
payment--order--false
system--module--false
module--system--false
message--notification--true
notification--message--false
report--document--false
document--report--true
account--profile--false
profile--account--false
feature--setting--false
setting--feature--false
file--document--true
document--file--false
dashboard--page--false
page--dashboard--false

INPUT - Entity pairs (exactly these, and only these):
{pairs_str}

OUTPUT - Entity pairs:
""")