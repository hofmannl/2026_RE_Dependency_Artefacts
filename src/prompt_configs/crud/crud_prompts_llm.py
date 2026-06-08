from __future__ import annotations

def build_prompt(input: str, single_word: bool = True, sentence: bool = False) -> str:
    """
    Build a prompt for batch semantic equivalence analysis.

    Guarantees:
    - ONLY the provided pairs are analyzed (closed world).
    - persona1/persona2/action1/action2/entity1/entity2 are treated as EXACT STRINGS.
    - Output is strictly machine-parseable: one line per input pair.
    """
    if single_word:
        return SINGLE_WORD.format(WORD=input.strip())
    elif sentence:
        return SENTENCE.format(SENTENCE=input.strip())
    
SINGLE_WORD = """
Classify the following word into exactly one CRUD class.

CRUD classes:
- create: a new entity is created (add, create, register, insert, upload when new)
- read: data is retrieved or displayed (get, view, list, fetch, search)
- update: an existing entity or its state is modified (edit, update, modify, enable, disable, archive)
- delete: an entity is removed or deleted (delete, remove, purge, destroy)

Rules:
1) Decide only based on the common meaning of the word, without system or domain context.
2) Always return exactly one class.
3) If you are unsure about the correct mapping, you MUST still choose the most likely class AND this word MUST be added to the mapping list.
4) Output format must be exactly: WORD--CRUD
5) No explanations, no extra characters.
6) Do NOT output a header row.

Example 1
Input:
add
Output:
add--create

Example 2
Input:
fetch
Output:
fetch--read

Example 3
Input:
edit
Output:
edit--update

Example 4

Input:
remove
Output:
remove--delete

Example 5
Input:
register
Output:
register--create

Example 6
Input:
view
Output:
view--read

Example 7
Input:
tweak
Output:
tweak--update

Example 8
Input:
purge
Output:
purge--delete

Example 9
Input:
upload
Output:
upload--create

Example 10
Input:
search
Output:
search--read

Example 11
Input:
refresh
Output:
refresh--update

Example 12
Input:
archive
Output:
archive--delete

Example 13
Input:
create
Output:
create--create

Word:
<<<
{WORD}
>>>

Output:
"""

SENTENCE = """
Classify the following sentence into exactly one CRUD class
by identifying the most relevant verb.

CRUD classes:
- create: a new entity is created (add, create, register, insert, upload when new)
- read: data is retrieved or displayed (get, view, list, fetch, search)
- update: an existing entity or its state is modified (edit, update, modify, enable, disable, archive)
- delete: an entity is removed or deleted (delete, remove, purge, destroy)

Rules:
1) Identify the single most relevant verb in the sentence.
2) Decide only based on the common meaning of that verb, without system or domain context.
3) Always return exactly one class.
4) If you are unsure about the correct mapping, you MUST still choose the most likely class AND this verb MUST be added to the mapping list.
5) Output format must be exactly: VERB--CRUD
6) No explanations, no extra characters.
7) Do NOT output a header row.

Examples:

Input:
As a user, I want to add a new account.
Output:
add--create

Input:
The system should fetch the latest data.
Output:
fetch--read

Input:
Users can edit their profile details.
Output:
edit--update

Input:
Admins may remove inactive accounts.
Output:
remove--delete

Input:
A customer can register using email.
Output:
register--create

Input:
The user wants to view the dashboard.
Output:
view--read

Input:
The user may tweak notification settings.
Output:
tweak--update

Input:
The system will purge old logs.
Output:
purge--delete

Input:
Users can upload a document.
Output:
upload--create

Input:
The user can search for orders.
Output:
search--read

Input:
The system refreshes cached data.
Output:
refresh--update

Input:
The user archives a record.
Output:
archive--delete

Input:
Create a new project.
Output:
create--create

Sentence:
<<<
{SENTENCE}
>>>

Output:
"""