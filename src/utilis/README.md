# Utilis

Shared data structures, enumerations, and utility functions used across the entire pipeline.

## Modules

### `dataclasses_user_story.py`

Dataclasses representing the structural elements of a parsed user story:

| Class | Description |
|---|---|
| `Persona` | The role initiating the story (e.g. `"admin"`) |
| `Action` | The verb / operation (e.g. `"delete"`) |
| `Entity` | The noun / domain object (e.g. `"user"`) |
| `Trigger` | A `Persona → Action` relationship |
| `Target` | An `Action → Entity` relationship |
| `Containment` | An `Entity → Entity` containment relationship |
| `UserStoryRecord` | Full record combining all of the above plus `CrudAction` classification |

### `annotation_graph_components.py`

Enumerations used to type graph nodes and classifier inputs:

| Enum | Values |
|---|---|
| `TypeGraphUs` | `PERSONA`, `ACTION`, `ENTITY`, `TRIGGER`, `TARGET`, `CONTAIN` |

### `keys_us_part.py`

`KeyOfUserStoryPart` enum — canonical string keys used when accessing user story fields from dicts or JSON (e.g. `"PID"`, `"Goal"`, `"Action"`, `"GoalActionCrud"`).

### `util_functions.py`

General-purpose helper functions:

| Function | Description |
|---|---|
| `return_goal_part(text, benefit)` | Strips the benefit clause (`so that ...`) and returns only the goal part |
| `remove_pid_from_text(text)` | Removes the `#G00#`-style PID prefix from a user story string |
| `get_article(word)` | Returns `"a"` or `"an"` based on the first letter of the word |