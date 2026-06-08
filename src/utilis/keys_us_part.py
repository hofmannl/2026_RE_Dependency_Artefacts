from enum import Enum

class KeyOfUserStoryPart(Enum):
    pid="PID"
    goal_part="Goal"
    benefit_part="Benefit"
    action="Action"
    entity="Entity"
    persona="Persona"
    triggers="Triggers"
    targets="Targets"
    contains="Contains"
    text="Text"
    benefit_text="Benefit"
    goal_action_crud="GoalActionCrud"